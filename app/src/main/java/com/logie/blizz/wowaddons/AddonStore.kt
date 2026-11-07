// Ported from the World of Warcraft app (com.logie.warcraft.AddonStore), for Blizzard's three clients.

package com.logie.blizz.wowaddons

import android.content.Context
import android.net.Uri
import com.logie.blizz.BuildConfig
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.sync.withPermit
import kotlinx.coroutines.withContext
import java.io.File
import java.io.IOException
import java.util.concurrent.ConcurrentHashMap

/**
 * The add-on manager behind the Add-ons screen, for one game ([AddonGame]): warperia.com's list and
 * pages (its section for that game), installs from it one at a time (each waits the site's few
 * seconds), what's installed and where it came from, and which of those the site has newer versions
 * of. Jobs carry on while the screen is closed. [WowAddonStores] keeps one for each of Blizzard's clients.
 */
class AddonStoreOf(val game: AddonGame) {
    /** Where an install from the site is. */
    sealed interface Job {
        data object Queued : Job
        data class Waiting(val secondsLeft: Int) : Job
        /** [fraction] null while the size isn't known. */
        data class Downloading(val fraction: Float?) : Job
        data object Installing : Job
        data class Failed(val message: String) : Job
    }

    /** One add-on in the client, as the screen lists it. */
    data class Installed(
        /** The site's slug, or "folder:<name>" for one from a zip. */
        val key: String,
        val title: String,
        val version: String?,
        /** The folders that go with it: on, off or delete. */
        val folders: List<String>,
        val on: Boolean,
        val forThisGame: Boolean,
        /** Set for an add-on installed from the site. */
        val record: AddonRecord?,
    )

    private val _installed = MutableStateFlow<List<Installed>>(emptyList())
    val installed: StateFlow<List<Installed>> = _installed

    private val _jobs = MutableStateFlow<Map<String, Job>>(emptyMap())
    val jobs: StateFlow<Map<String, Job>> = _jobs

    /** The site's pages of installed add-ons it has a newer version of, by slug. */
    private val _updates = MutableStateFlow<Map<String, Warperia.Details>>(emptyMap())
    val updates: StateFlow<Map<String, Warperia.Details>> = _updates

    private val _checking = MutableStateFlow(false)
    val checking: StateFlow<Boolean> = _checking

    /** What to tell the user: an install done or failed. */
    private val _messages = MutableSharedFlow<String>(extraBufferCapacity = 16)
    val messages: SharedFlow<String> = _messages

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val oneAtATime = Mutex()
    private val checkLock = Mutex()
    private val details = ConcurrentHashMap<String, Pair<Long, Warperia.Details>>()
    @Volatile private var lastCheck = 0L

    private val web by lazy { HttpWeb("Blizzard/${BuildConfig.VERSION_NAME} (com.logie.blizz)") }

    // The site -----------------------------------------------------------------------------------

    suspend fun list(query: Warperia.Query, page: Int): Warperia.ListPage = withContext(Dispatchers.IO) {
        Warperia.parseList(web.get(Warperia.listUrl(query, page, game.flavor)), game.flavor)
    }

    /** An add-on's page, from the last few minutes' copy unless [fresh]. */
    suspend fun details(slug: String, fresh: Boolean = false): Warperia.Details = withContext(Dispatchers.IO) {
        val kept = details[slug]
        if (!fresh && kept != null && System.currentTimeMillis() - kept.first < DETAILS_KEEP_MS) return@withContext kept.second
        Warperia.parseDetails(web.get(Warperia.pageUrl(slug, game.flavor)), slug, game.flavor).also { details[slug] = System.currentTimeMillis() to it }
    }

    // What's installed ---------------------------------------------------------------------------

    /** Reads what's in the client again. */
    fun refresh(context: Context) {
        val app = context.applicationContext
        scope.launch { reload(app) }
    }

    private fun reload(context: Context) {
        val folders = if (game.hasClient(context)) runCatching { Addons.list(context, game) }.getOrDefault(emptyList()) else emptyList()
        val byName = folders.associateBy { it.folder.lowercase() }
        // Records of add-ons that are no longer there (deleted by hand, or a new client) go; looked
        // up on disk again, as an install may have just finished.
        if (game.hasClient(context)) {
            runCatching { Addons.updateRecords(context, game) { records -> records.filter { r -> r.folders.any { Addons.exists(context, it, game) } } } }
        }
        val present = Addons.records(context, game).filter { r -> r.folders.any { it.lowercase() in byName } }
        val owned = mutableSetOf<String>()
        val fromSite = present.map { record ->
            val mine = record.folders.mapNotNull { byName[it.lowercase()] }
            owned += mine.map { it.folder.lowercase() }
            val main = mine.first()
            Installed(
                key = record.slug,
                title = record.title,
                version = record.version ?: main.version,
                folders = mine.map { it.folder },
                on = main.on,
                forThisGame = mine.any { it.forThisGame },
                record = record,
            )
        }
        val fromZips = folders.filter { it.folder.lowercase() !in owned }.map { addon ->
            Installed("folder:${addon.folder}", addon.title, addon.version, listOf(addon.folder), addon.on, addon.forThisGame, null)
        }
        _installed.value = (fromSite + fromZips).sortedBy { it.title.lowercase() }
        _updates.update { updates -> updates.filterKeys { slug -> present.any { it.slug == slug } } }
    }

    /** The installed copy of the site's add-on [slug], if there is one. */
    fun installedFrom(slug: String): Installed? = _installed.value.firstOrNull { it.record?.slug == slug }

    // Installing ---------------------------------------------------------------------------------

    /** Queues an install (or an update) of the site's add-on [slug]. */
    fun install(context: Context, slug: String) {
        val app = context.applicationContext
        val running = _jobs.value[slug]
        if (running != null && running !is Job.Failed) return
        setJob(slug, Job.Queued)
        scope.launch {
            oneAtATime.withLock {
                try {
                    installNow(app, slug)
                    setJob(slug, null)
                } catch (e: Exception) {
                    val message = when {
                        e is Addons.NoAddonException -> "There's no add-on in that zip (no .toc file)."
                        e is HttpException -> "warperia.com refused it (HTTP ${e.code})"
                        e is IOException && e.message != null -> e.message!!
                        else -> e.javaClass.simpleName
                    }
                    setJob(slug, Job.Failed(message))
                    _messages.tryEmit("Couldn't install it: $message")
                }
            }
        }
    }

    private suspend fun installNow(context: Context, slug: String) {
        if (!game.hasClient(context)) throw IOException(game.noClientMessage(context))
        val page = details(slug, fresh = true)
        val zip = game.check(context, File(game.temp(context).also { game.mkdirs(context, it) }, "warperia-$slug.zip"))
        try {
            withContext(Dispatchers.IO) {
                WarperiaDownload.fetch(web, slug, zip, flavor = game.flavor, onStep = { step ->
                    when (step) {
                        is WarperiaDownload.Step.Waiting -> setJob(slug, Job.Waiting(step.secondsLeft))
                        is WarperiaDownload.Step.Downloading ->
                            setJob(slug, Job.Downloading(if (step.size > 0) step.bytes.toFloat() / step.size else null))
                    }
                })
                setJob(slug, Job.Installing)
                val folders = Addons.installZip(context, zip, game)
                val record = AddonRecord(
                    slug = slug,
                    title = page.title,
                    version = page.version,
                    updated = page.updated,
                    logo = page.logo,
                    folders = folders,
                    installedAt = System.currentTimeMillis(),
                )
                Addons.updateRecords(context, game) { AddonRecords.put(it, record) }
            }
        } finally {
            game.delete(context, zip)
            game.delete(context, game.check(context, File(zip.path + ".part")))
        }
        _updates.update { it - slug }
        reload(context)
        _messages.tryEmit("Installed: ${page.title}")
    }

    private fun setJob(slug: String, job: Job?) {
        _jobs.update { jobs -> if (job == null) jobs - slug else jobs + (slug to job) }
    }

    /** Installs the add-ons in a zip the user picked. */
    suspend fun importZip(context: Context, uri: Uri): List<String> = withContext(Dispatchers.IO) {
        Addons.install(context, uri, game).also { reload(context) }
    }

    // Updates ------------------------------------------------------------------------------------

    /**
     * Looks up each add-on from the site on its page, a few at a time; not again within half an
     * hour unless [force].
     */
    fun checkUpdates(context: Context, force: Boolean) {
        val app = context.applicationContext
        if (!force && System.currentTimeMillis() - lastCheck < CHECK_EVERY_MS) return
        scope.launch {
            if (!checkLock.tryLock()) return@launch
            _checking.value = true
            try {
                reload(app)
                val records = _installed.value.mapNotNull { it.record }
                val gate = Semaphore(3)
                val found = records.map { record ->
                    async {
                        gate.withPermit {
                            val page = runCatching { details(record.slug, fresh = true) }.getOrNull() ?: return@withPermit null
                            if (AddonRecords.isOutdated(record, page.version, page.updated)) record.slug to page else null
                        }
                    }
                }.awaitAll().filterNotNull().toMap()
                _updates.value = found
                lastCheck = System.currentTimeMillis()
            } finally {
                _checking.value = false
                checkLock.unlock()
            }
        }
    }

    /** Whether the list's date for [slug] says the site has a newer one than what's installed. */
    fun isNewer(slug: String, updated: String?): Boolean {
        if (slug in _updates.value) return true
        val record = installedFrom(slug)?.record ?: return false
        return AddonRecords.isOutdated(record, null, updated)
    }

    fun updateAll(context: Context) {
        for (slug in _updates.value.keys) install(context, slug)
    }

    // On, off, gone ------------------------------------------------------------------------------

    fun setOn(context: Context, item: Installed, on: Boolean) {
        val app = context.applicationContext
        scope.launch {
            for (folder in foldersOf(app, item)) Addons.setOn(app, folder, on, game)
            reload(app)
        }
    }

    fun delete(context: Context, item: Installed) {
        val app = context.applicationContext
        scope.launch {
            for (folder in foldersOf(app, item)) Addons.delete(app, folder, game)
            if (item.record != null) {
                Addons.updateRecords(app, game) { records -> records.filterNot { it.slug == item.record.slug } }
                _updates.update { it - item.record.slug }
            }
            reload(app)
        }
    }

    /** An add-on's own folders: libraries another add-on from the site also brought stay. */
    private fun foldersOf(context: Context, item: Installed): List<String> {
        val record = item.record ?: return item.folders
        val own = AddonRecords.ownFolders(record, Addons.records(context, game)).map { it.lowercase() }.toSet()
        return item.folders.filter { it.lowercase() in own }
    }

    private companion object {
        const val DETAILS_KEEP_MS = 10 * 60_000L
        const val CHECK_EVERY_MS = 30 * 60_000L
    }
}

/** The add-on managers, one for each of Blizzard's clients (their state is kept while the app runs). */
object WowAddonStores {
    private val stores = java.util.concurrent.ConcurrentHashMap<String, AddonStoreOf>()

    /** The manager for the launcher game [gameId] ("wow", "wow_legion", "wow_octowow"), or null for another. */
    fun of(gameId: String): AddonStoreOf? {
        val game = WowAddonGames.of(gameId) ?: return null
        return stores.getOrPut(gameId) { AddonStoreOf(game) }
    }
}
