package com.logie.blizz.importer

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.net.Uri
import android.os.IBinder
import android.provider.DocumentsContract
import com.logie.blizz.R
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import java.io.File

/**
 * The importers behind the app's Auto Import: one at a time per game, in the background (with
 * [ImportService] keeping the app alive through gigabytes of download), the wizard watching
 * [states].
 */
object GameImportManager {
    data class WizardState(
        val gameId: String,
        val record: ImportRecord,
        val running: Boolean = false,
        val progress: Progress? = null,
        val missing: List<MissingInput> = emptyList(),
        val autoSources: List<AutoSource> = emptyList(),
        val validation: Validation? = null,
        val entry: LibraryEntry? = null,
    )

    private val importers: Map<String, () -> GameImporter> = mapOf(
        "diablo" to { Diablo1DevilutionXImporter() },
        "diablo2" to { Diablo2ClassicImporter() },
        "starcraft" to { StarCraftClassicImporter() },
        "starcraft_remastered" to { StarCraftRemasteredImporter() },
        "starcraft2" to { StarCraft2OfflineImporter() },
    )

    fun importable(gameId: String) = gameId in importers

    private val _states = MutableStateFlow<Map<String, WizardState>>(emptyMap())
    val states: StateFlow<Map<String, WizardState>> = _states

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val cancels = HashMap<String, CancelToken>()
    /** Diablo II's optional original keys, for this session only. */
    private val keys = HashMap<String, LegacyDownloader.Keys>()

    fun paths(context: Context) = GamePaths(context.applicationContext.filesDir)
    fun repo(context: Context) = ImportStateRepository(paths(context))
    fun library(context: Context) = Library(paths(context))

    /** The game's state as stored (an import interrupted by the app closing is shown where it stopped). */
    fun refresh(context: Context, gameId: String) {
        if (cancels.containsKey(gameId)) return
        val record = repo(context).load(gameId)
        publish(WizardState(gameId, record, entry = library(context).get(gameId), missing = _states.value[gameId]?.missing ?: emptyList()))
    }

    private fun publish(state: WizardState) {
        _states.value = _states.value + (state.gameId to state)
    }

    fun setKeys(gameId: String, classic: String?, expansion: String?, owner: String?) {
        keys[gameId] = LegacyDownloader.Keys(classic?.takeIf { it.isNotBlank() }, expansion?.takeIf { it.isNotBlank() }, owner?.takeIf { it.isNotBlank() })
    }

    /** Auto Import (or Repair, [repair]): runs the importer's steps until done, or until it needs the person. */
    fun start(context: Context, gameId: String, repair: Boolean = false) {
        val app = context.applicationContext
        val factory = importers[gameId] ?: return
        synchronized(cancels) {
            if (cancels.containsKey(gameId)) return
            cancels[gameId] = CancelToken()
        }
        val cancel = cancels[gameId]!!
        ImportService.start(app)
        scope.launch {
            val repo = repo(app)
            val library = library(app)
            var state = WizardState(gameId, repo.load(gameId), running = true, entry = library.get(gameId))
            publish(state)
            try {
                val env = env(app, gameId, cancel) { p ->
                    state = state.copy(progress = p, record = state.record.copy(stage = p.stage))
                    publish(state)
                    ImportService.update(app, p)
                }
                val supplied = supplied(app, repo.load(gameId))
                val result = ImportPipeline(repo, library).run(factory(), env, supplied, repair)
                state = when (result) {
                    is ImportPipeline.Result.Waiting -> state.copy(record = result.record, missing = result.missing, autoSources = result.autoSources)
                    is ImportPipeline.Result.Done -> state.copy(record = result.record, validation = result.validation, entry = result.entry, missing = emptyList())
                    is ImportPipeline.Result.Failed -> {
                        reportFailure(app, gameId, repair, result)
                        state.copy(record = result.record, validation = result.validation, missing = emptyList())
                    }
                }
            } finally {
                synchronized(cancels) { cancels.remove(gameId) }
                publish(state.copy(running = false, progress = null, entry = library.get(gameId)))
                if (synchronized(cancels) { cancels.isEmpty() }) ImportService.stop(app)
            }
        }
    }

    /** Not bugs: the person stopped it, the phone is full, or the game is a version the app doesn't play. */
    private val NOT_BUGS = setOf(Problem.CANCELLED, Problem.INSUFFICIENT_STORAGE, Problem.UNSUPPORTED_VERSION)

    /** A failed import, sent as a GitHub issue ([com.logie.blizz.reports.BugReports]). */
    private fun reportFailure(context: Context, gameId: String, repair: Boolean, result: ImportPipeline.Result.Failed) {
        val e = result.error
        if (e.problem in NOT_BUGS) return
        val checks = result.validation?.checks?.joinToString("; ") { "${if (it.passed) "✓" else "✗"} ${it.name} (${it.detail})" }
        com.logie.blizz.reports.BugReports.report(
            context,
            "${com.logie.blizz.Games.find(gameId)?.fullTitle ?: gameId} ${if (repair) "repair" else "import"} (${e.problem})",
            e.message ?: e.problem.name,
            listOf("Game" to gameId, "Problem" to e.problem.name, "Online" to online(context).toString(), "Checks" to checks),
            log = listOfNotNull(e.detail, e.cause?.stackTraceToString()).joinToString("\n\n").ifEmpty { null },
        )
    }

    fun cancel(gameId: String) {
        synchronized(cancels) { cancels[gameId] }?.cancel()
    }

    /** The person picked a file ([tree] false) or a folder for [inputId]; the import goes on. */
    fun supply(context: Context, gameId: String, inputId: String, uri: Uri, tree: Boolean) {
        val app = context.applicationContext
        runCatching { app.contentResolver.takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION) }
        repo(app).update(gameId) { it.copy(supplied = it.supplied + (inputId to (if (tree) "tree:" else "doc:") + uri)) }
        publish((_states.value[gameId] ?: WizardState(gameId, repo(app).load(gameId))).copy(missing = emptyList()))
        start(app, gameId)
    }

    fun skip(context: Context, gameId: String, inputId: String) {
        val app = context.applicationContext
        repo(app).update(gameId) { it.copy(skipped = it.skipped + inputId) }
        publish((_states.value[gameId] ?: WizardState(gameId, repo(app).load(gameId))).copy(missing = emptyList()))
        start(app, gameId)
    }

    /** A folder the importers may search from now on (kept across restarts). */
    fun addSearchFolder(context: Context, treeUri: Uri) {
        runCatching { context.contentResolver.takePersistableUriPermission(treeUri, Intent.FLAG_GRANT_READ_URI_PERMISSION) }
    }

    /** The app's own import folder, which the person can copy files into over USB. */
    fun importFolder(context: Context): File? = context.getExternalFilesDir("import")?.also { it.mkdirs() }

    private fun supplied(context: Context, record: ImportRecord): Map<String, Supplied> {
        val out = HashMap<String, Supplied>()
        for ((id, value) in record.supplied) {
            val uri = Uri.parse(value.substringAfter(':'))
            val node = runCatching {
                if (value.startsWith("tree:")) DocumentNode.tree(context.contentResolver, uri) else DocumentNode.file(context.contentResolver, uri)
            }.getOrNull() ?: continue
            out[id] = Supplied.Picked(id, node)
        }
        for (id in record.skipped) out[id] = Supplied.Skipped(id)
        return out
    }

    private fun searchRoots(context: Context): List<SourceNode> {
        val roots = ArrayList<SourceNode>()
        importFolder(context)?.let { roots += FileNode(it) }
        for (permission in context.contentResolver.persistedUriPermissions) {
            if (!permission.isReadPermission) continue
            val uri = permission.uri
            if (runCatching { DocumentsContract.getTreeDocumentId(uri) }.isSuccess && !isDocument(uri)) {
                runCatching { DocumentNode.tree(context.contentResolver, uri) }.getOrNull()?.let { roots += it }
            }
        }
        return roots
    }

    private fun isDocument(uri: Uri) = uri.pathSegments.contains("document")

    private fun online(context: Context): Boolean {
        val cm = context.getSystemService(ConnectivityManager::class.java) ?: return false
        val caps = cm.getNetworkCapabilities(cm.activeNetwork) ?: return false
        return caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }

    private fun env(context: Context, gameId: String, cancel: CancelToken, progress: (Progress) -> Unit): ImportEnv {
        val paths = paths(context)
        val bldl = Tools.file(context, "libbldl.so")
        val inno = Tools.file(context, "libinnoextract.so")
        return ImportEnv(
            paths = paths,
            searchRoots = { searchRoots(context) },
            online = { online(context) },
            downloads = DownloadManager(),
            releases = GitHubReleases(),
            legacy = if (bldl.isFile) LegacyDownloader(bldl, paths.legacyCache) else null,
            innoextract = if (inno.isFile) Innoextract(inno) else null,
            cancel = cancel,
            progress = progress,
            keys = keys[gameId],
        )
    }

    /** The game's first window came up under Winlator: recorded apart from the file checks. */
    fun recordLaunch(context: Context, gameId: String, test: LaunchTest) {
        repo(context).update(gameId) { it.copy(launchTest = test) }
        refresh(context, gameId)
    }
}

/** Keeps the app running while an import works (downloads of gigabytes), with its progress in a notification. */
class ImportService : Service() {
    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(ID, notification(this, getString(R.string.import_running), null))
        return START_NOT_STICKY
    }

    companion object {
        private const val ID = 7
        private const val CHANNEL = "imports"

        private fun channel(context: Context) {
            val nm = context.getSystemService(NotificationManager::class.java)
            nm.createNotificationChannel(NotificationChannel(CHANNEL, context.getString(R.string.import_channel), NotificationManager.IMPORTANCE_LOW))
        }

        private fun notification(context: Context, text: String, progress: Progress?): Notification {
            channel(context)
            val b = Notification.Builder(context, CHANNEL)
                .setSmallIcon(android.R.drawable.stat_sys_download)
                .setContentTitle(context.getString(R.string.app_name))
                .setContentText(text)
                .setOngoing(true)
            if (progress != null && progress.total > 0) b.setProgress(1000, (progress.done * 1000 / progress.total).toInt(), false)
            return b.build()
        }

        fun start(context: Context) {
            runCatching { context.startForegroundService(Intent(context, ImportService::class.java)) }
        }

        fun update(context: Context, progress: Progress) {
            runCatching {
                context.getSystemService(NotificationManager::class.java).notify(ID, notification(context, progress.label, progress))
            }
        }

        fun stop(context: Context) {
            context.stopService(Intent(context, ImportService::class.java))
        }
    }
}
