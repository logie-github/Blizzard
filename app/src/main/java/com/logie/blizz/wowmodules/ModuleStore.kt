package com.logie.blizz.wowmodules

import android.content.Context
import com.logie.blizz.importer.deleteTree
import com.logie.blizz.wow.Realm
import com.logie.blizz.wow.WowLayout
import com.logie.blizz.wow.WowRealm
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.delay
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.net.URLEncoder

/**
 * The module browser behind the Modules screen, for the Wrath+ realm (ChromieCraft): AzerothCore's
 * modules as GitHub lists them ([ModuleCatalog]), the ones the user picked, the realm built with
 * them on GitHub (the World of Warcraft app's workflow, started with the user's own token) and that
 * realm put in place of the one Blizzard holds, with the realm's own kept to put back.
 *
 * Kept in `files/wowmodules`: chosen.json (the picks), pending.json (the build asked for and how
 * it went), realm.json (the realm in, with the modules it was built with), and each realm put in
 * (realms/server-<request>.tar.xz, listed in realms.json), so realms can be swapped without building
 * them again. The token is only ever in this app's own preferences, and goes to GitHub's API alone.
 *
 * Which realm is in is read from the stamp inside `server` ([RealmPackage.STAMP]), not trusted
 * from realm.json: a game imported again has its own realm back.
 *
 * NOT verified on a phone: the real build on GitHub, a real package's size and unpacking time, the
 * realm starting from a swapped-in package.
 */
object ModuleStore {
    /** What the long jobs (putting a realm in or back) are doing. */
    sealed interface Work {
        data object Idle : Work
        /** [progress] null while it can't be told. */
        data class Running(val title: String, val detail: String?, val progress: Float?) : Work
        data class Done(val message: String) : Work
        data class Failed(val message: String) : Work
    }

    private val _chosen = MutableStateFlow<List<ModuleBuild.Chosen>>(emptyList())
    val chosen: StateFlow<List<ModuleBuild.Chosen>> = _chosen

    private val _pending = MutableStateFlow<ModuleBuild.Pending?>(null)
    val pending: StateFlow<ModuleBuild.Pending?> = _pending

    private val _realm = MutableStateFlow<ModuleBuild.Built?>(null)
    /** The modules realm that is in now (its stamp is in `server`), or null for the realm's own. */
    val realm: StateFlow<ModuleBuild.Built?> = _realm

    private val _saved = MutableStateFlow<List<ModuleBuild.Built>>(emptyList())
    /** The realms kept on the phone, newest first. */
    val saved: StateFlow<List<ModuleBuild.Built>> = _saved

    private val _hasToken = MutableStateFlow(false)
    val hasToken: StateFlow<Boolean> = _hasToken

    private val _work = MutableStateFlow<Work>(Work.Idle)
    val work: StateFlow<Work> = _work

    private val _stockKept = MutableStateFlow(false)
    /** The realm's own programs are kept, to put back. */
    val stockKept: StateFlow<Boolean> = _stockKept

    private var loaded = false
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    @Volatile private var job: Job? = null

    /** The realm's own modules, always in. */
    val baseModules: Set<String> get() = ModuleSource.BASE_MODULES

    private fun dir(context: Context) = File(context.applicationContext.filesDir, "wowmodules").also { it.mkdirs() }

    private fun layout(context: Context) = WowLayout.of(context)

    private fun slots(context: Context) = RealmPackage.Slots.of(layout(context))

    /** The WoW app's version the imported realm is of, which a build is made from. */
    fun versionCode(context: Context): Int? = ModuleSource.exportedVersionCode(layout(context))

    /** Why a realm can't be built or changed (null when it can): the realm isn't imported, or isn't known by version. */
    fun unavailableReason(context: Context): String? = when {
        !layout(context).isImported() -> "The Wrath+ realm isn't imported yet. Import World of Warcraft from the World of Warcraft app's export first."
        versionCode(context) == null -> "The export doesn't say which version of the World of Warcraft app made it, so the realm to build from can't be found. Export again from the World of Warcraft app."
        else -> null
    }

    /** The app's release, which a realm is built from (`wow-build-N`), or null when the export doesn't say. */
    fun release(context: Context): String? =
        versionCode(context)?.let { ModuleBuild.release(ModuleSource.RELEASE_TAG_PREFIX, it) }

    @Synchronized
    fun load(context: Context) {
        if (loaded) {
            syncRealm(context)
            return
        }
        val dir = dir(context)
        runCatching { RealmPackage.recover(slots(context)) }
        _chosen.value = runCatching {
            ModuleBuild.chosenFromJson(org.json.JSONArray(File(dir, CHOSEN).readText()))
        }.getOrDefault(emptyList())
        _pending.value = ModuleBuild.pendingFromJson(File(dir, PENDING).takeIf { it.isFile }?.readText())
        _saved.value = ModuleBuild.savedFromJson(File(dir, SAVED).takeIf { it.isFile }?.readText())
        _hasToken.value = !token(context).isNullOrBlank()
        loaded = true
        syncRealm(context)
        runCatching { tidySaved(context) }
    }

    /** Which realm is in now, from the stamp in `server`; and whether the realm's own is kept. */
    fun syncRealm(context: Context) {
        val stamp = RealmPackage.stampOf(layout(context).server)
        val recorded = ModuleBuild.builtFromJson(File(dir(context), REALM).takeIf { it.isFile }?.readText())
        _realm.value = recorded?.takeIf { stamp != null && stamp == ModuleBuild.stamp(it) }
        _stockKept.value = RealmPackage.hasStock(slots(context))
    }

    private fun write(file: File, text: String) {
        val part = File(file.path + ".part")
        part.writeText(text)
        if (!part.renameTo(file)) throw IOException("Can't save ${file.name}")
    }

    // The picks -------------------------------------------------------------------------------------

    fun isChosen(fullName: String) = _chosen.value.any { it.fullName.equals(fullName, ignoreCase = true) }

    fun add(context: Context, listing: ModuleCatalog.Listing) {
        load(context)
        if (isChosen(listing.fullName) || listing.name in baseModules) return
        if (!ModuleBuild.isBranch(listing.defaultBranch)) return
        save(context, _chosen.value + ModuleBuild.Chosen(listing.fullName, listing.defaultBranch, listing.description, listing.avatar))
    }

    fun remove(context: Context, fullName: String) {
        load(context)
        save(context, _chosen.value.filterNot { it.fullName.equals(fullName, ignoreCase = true) })
    }

    private fun save(context: Context, list: List<ModuleBuild.Chosen>) {
        write(File(dir(context), CHOSEN), ModuleBuild.chosenToJson(list).toString())
        _chosen.value = list
    }

    private fun setPending(context: Context, pending: ModuleBuild.Pending?) {
        val file = File(dir(context), PENDING)
        if (pending == null) file.delete() else write(file, ModuleBuild.pendingToJson(pending))
        _pending.value = pending
    }

    private fun setRealm(context: Context, built: ModuleBuild.Built?) {
        val file = File(dir(context), REALM)
        if (built == null) file.delete() else write(file, ModuleBuild.builtToJson(built))
        _realm.value = built
    }

    // The realms kept --------------------------------------------------------------------------------

    private fun savedDir(context: Context) = File(dir(context), "realms").also { it.mkdirs() }

    /** Where a kept realm's package is. */
    fun savedFile(context: Context, request: String) = File(savedDir(context), ModuleBuild.assetName(request))

    /** A kept realm that can be put in: for the version of the realm imported, its package there. */
    fun canPutIn(context: Context, built: ModuleBuild.Built) =
        built.versionCode == versionCode(context) && savedFile(context, built.request).isFile

    private fun setSaved(context: Context, list: List<ModuleBuild.Built>) {
        write(File(dir(context), SAVED), ModuleBuild.savedToJson(list))
        _saved.value = list
    }

    /**
     * A realm for another version of the WoW app can't be put in (the app and its realm change
     * together): its package goes, its modules stay listed, to build again. At most [MAX_SAVED].
     */
    private fun tidySaved(context: Context) {
        val version = versionCode(context)
        val list = _saved.value
        val tidy = list.map { built ->
            if (built.versionCode != version && built.size > 0) {
                savedFile(context, built.request).delete()
                built.copy(size = 0)
            } else {
                built
            }
        }.take(MAX_SAVED)
        list.drop(MAX_SAVED).forEach { savedFile(context, it.request).delete() }
        // Packages no entry lists (a download that was being kept when the app stopped).
        val listed = tidy.map { ModuleBuild.assetName(it.request) }.toSet()
        savedDir(context).listFiles().orEmpty().filter { it.name !in listed }.forEach { it.delete() }
        if (tidy != list) setSaved(context, tidy)
    }

    /** Forgets a kept realm and deletes its package. */
    fun deleteSaved(context: Context, request: String) {
        load(context)
        if (_realm.value?.request == request) return
        savedFile(context, request).delete()
        setSaved(context, _saved.value.filterNot { it.request == request })
    }

    /** [built]'s modules become the picks (to build again, or to change). */
    fun useModules(context: Context, built: ModuleBuild.Built) {
        load(context)
        save(context, built.modules.filter { it.name !in baseModules })
    }

    // The token -------------------------------------------------------------------------------------

    private fun prefs(context: Context) = context.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE)

    /** The user's GitHub token. Never logged, never shown, only sent to GitHub's API. */
    fun token(context: Context): String? = prefs(context).getString(KEY_TOKEN, null)

    /** Checks [token] can see this repository's builds, then keeps it. */
    suspend fun setToken(context: Context, token: String) = withContext(Dispatchers.IO) {
        val trimmed = token.trim()
        GitHubApi({ trimmed }, ModuleSource.userAgent).get(ModuleSource.workflowUrl())
        prefs(context).edit().putString(KEY_TOKEN, trimmed).apply()
        _hasToken.value = true
    }

    fun clearToken(context: Context) {
        prefs(context).edit().remove(KEY_TOKEN).apply()
        _hasToken.value = false
    }

    private fun api(context: Context) = GitHubApi({ token(context) }, ModuleSource.userAgent)

    // GitHub ----------------------------------------------------------------------------------------

    private fun path(text: String) = text.split('/').joinToString("/") { URLEncoder.encode(it, "UTF-8").replace("+", "%20") }

    /** A page of the topic's modules. */
    suspend fun search(context: Context, text: String, order: ModuleCatalog.Order, page: Int): ModuleCatalog.Page =
        withContext(Dispatchers.IO) { ModuleCatalog.parseSearch(api(context).get(ModuleCatalog.searchUrl(text, order, page))) }

    /** A module's README (Markdown), or null when it has none. */
    suspend fun readme(context: Context, fullName: String): String? = withContext(Dispatchers.IO) {
        try {
            api(context).get("https://${GitHubApi.API_HOST}/repos/${path(fullName)}/readme", GitHubApi.RAW)
        } catch (e: GitHubApi.HttpError) {
            if (e.code == 404) null else throw e
        }
    }

    /**
     * Asks GitHub for a realm with the chosen modules: each at its branch's newest commit, built
     * from the release of the WoW app the imported realm is of. Throws what went wrong.
     *
     * The workflow is started at the release's own tag (the file as it was for that version); if
     * GitHub doesn't know it there, at the repository's default branch.
     */
    suspend fun startBuild(context: Context) = withContext(Dispatchers.IO) {
        load(context)
        unavailableReason(context)?.let { throw IOException(it) }
        if (token(context).isNullOrBlank()) throw IOException("Add your GitHub token first.")
        val api = api(context)
        val picks = _chosen.value.filter { it.name !in baseModules }.take(ModuleBuild.MAX_MODULES)
        if (picks.isEmpty()) throw IOException("Add a module first.")
        val version = versionCode(context)!!
        val release = release(context)!!
        val pinned = picks.map { module ->
            val sha = api.get(
                "https://${GitHubApi.API_HOST}/repos/${path(module.fullName)}/commits/${path(module.branch)}",
                "application/vnd.github.sha",
            ).trim()
            if (!ModuleCatalog.isCommit(sha)) throw IOException("GitHub didn't say which commit ${module.fullName} is at.")
            module.copy(commit = sha)
        }
        val request = ModuleBuild.newRequest()
        val modules = ModuleBuild.modulesInput(pinned, baseModules)
        dispatch(api, release, request, modules)
        setPending(context, ModuleBuild.Pending(request, release, version, pinned, System.currentTimeMillis()))
    }

    private fun dispatch(api: GitHubApi, release: String, request: String, modules: String) {
        val url = "${ModuleSource.workflowUrl()}/dispatches"
        try {
            api.post(url, ModuleBuild.dispatchBody(release, release, request, modules))
        } catch (e: GitHubApi.HttpError) {
            if (e.code != 404 && e.code != 422) throw e
            // Not at the release's tag: the default branch has the workflow, if it has it at all.
            val branch = runCatching { ModuleSource.parseDefaultBranch(api.get(ModuleSource.repoUrl())) }.getOrNull()
                ?: throw IOException("GitHub wouldn't start the build at ${ModuleSource.REPO} $release (${e.reason ?: "HTTP ${e.code}"}).")
            try {
                api.post(url, ModuleBuild.dispatchBody(branch, release, request, modules))
            } catch (second: GitHubApi.HttpError) {
                throw IOException("GitHub wouldn't start the build at ${ModuleSource.REPO} (${second.reason ?: "HTTP ${second.code}"}).")
            }
        }
    }

    /** How the build is going, from GitHub. Background work. */
    suspend fun refresh(context: Context): ModuleBuild.Pending? = withContext(Dispatchers.IO) {
        load(context)
        val pending = _pending.value ?: return@withContext null
        if (pending.succeeded && pending.leftOut == null) {
            // What went in: read once the build is done.
            val leftOut = runCatching { leftOut(context, pending) }.getOrNull() ?: return@withContext pending
            if (_pending.value?.request != pending.request) return@withContext _pending.value
            return@withContext pending.copy(leftOut = leftOut).also { setPending(context, it) }
        }
        if (pending.isDone || token(context).isNullOrBlank()) return@withContext pending
        val api = api(context)
        val run = if (pending.runId == null) {
            ModuleBuild.findRun(api.get(ModuleSource.runsUrl()), pending.request)
        } else {
            ModuleBuild.parseRun(api.get(ModuleSource.runUrl(pending.runId)))
        } ?: return@withContext pending.copy(checkedAt = System.currentTimeMillis()).also { _pending.value = it }
        val step = runCatching { ModuleBuild.currentStep(api.get("${ModuleSource.runUrl(run.id)}/jobs")) }.getOrNull()
        // Asked for and seen by a newer refresh meanwhile: the newer one stays.
        if (_pending.value?.request != pending.request) return@withContext _pending.value
        ModuleBuild.seen(pending, run, step, System.currentTimeMillis()).also { setPending(context, it) }
    }

    /** Stops following the build, and stops it on GitHub if it's still going. */
    suspend fun cancelBuild(context: Context) = withContext(Dispatchers.IO) {
        val pending = _pending.value ?: return@withContext
        if (pending.runId != null && !pending.isDone) {
            runCatching { api(context).post("${ModuleSource.runUrl(pending.runId)}/cancel", "{}") }
        }
        setPending(context, null)
    }

    /** A finished build is put aside: done with. */
    fun dismissBuild(context: Context) = setPending(context, null)

    /** The files attached to [release]. Throws [IOException]. */
    private fun releaseAssets(context: Context, release: String): List<ModuleSource.Asset> =
        ModuleSource.parseAssets(api(context).get(ModuleSource.releaseUrl(release)))

    /**
     * The modules build [pending] left out, from its record next to its package (none when it has
     * no record: built before builds kept one). Throws when GitHub can't be asked.
     */
    private fun leftOut(context: Context, pending: ModuleBuild.Pending): List<ModuleBuild.LeftOut> {
        val record = releaseAssets(context, pending.release).firstOrNull { it.name == ModuleBuild.recordName(pending.request) }
            ?: return emptyList()
        return ModuleBuild.parseLeftOut(api(context).get(record.url, GitHubApi.FILE))
    }

    // Putting a realm in ----------------------------------------------------------------------------

    /** Puts the finished build's realm in (download, check, stop the realm, swap). Returns at once; follow [work]. */
    fun installBuilt(context: Context) = launchWork(context, "Putting your realm in") { progress -> installBuiltNow(context, progress) }

    /** Puts a kept realm in, in place of the one in now. */
    fun putIn(context: Context, request: String) = launchWork(context, "Changing the realm") { progress -> putInNow(context, request, progress) }

    /** The realm's own back, in place of a modules realm. */
    fun installStock(context: Context) = launchWork(context, "Putting the realm's own back") { progress -> installStockNow(context, progress) }

    /** The result of the last job is seen: the screen goes back to idle. */
    fun clearWork() {
        if (_work.value !is Work.Running) _work.value = Work.Idle
    }

    private fun launchWork(context: Context, title: String, block: suspend (progress: (Float?, String?) -> Unit) -> String) {
        val app = context.applicationContext
        synchronized(this) {
            if (_work.value is Work.Running) return
            _work.value = Work.Running(title, null, null)
        }
        job = scope.launch {
            val progress: (Float?, String?) -> Unit = { fraction, detail -> _work.value = Work.Running(title, detail, fraction) }
            try {
                load(app)
                val message = block(progress)
                _work.value = Work.Done(message)
            } catch (e: CancellationException) {
                _work.value = Work.Failed("Stopped.")
                throw e
            } catch (e: Exception) {
                _work.value = Work.Failed(e.message ?: e.javaClass.simpleName)
            } finally {
                runCatching { syncRealm(app) }
            }
        }
    }

    /** Stops what is running (a download carries on from where it got to next time). */
    fun cancelWork() {
        job?.cancel()
    }

    private suspend fun installBuiltNow(context: Context, progress: (Float?, String?) -> Unit): String {
        unavailableReason(context)?.let { throw IOException(it) }
        val pending = _pending.value
        if (pending == null || !pending.succeeded) throw IOException("There's no finished build to put in.")
        if (pending.versionCode != versionCode(context)) throw IOException("That realm was built for another version of the World of Warcraft app: build it again.")
        val name = ModuleBuild.assetName(pending.request)
        progress(null, "Finding your realm…")
        val asset = network { releaseAssets(context, pending.release) }.firstOrNull { it.name == name }
            ?: throw IOException("The release ${pending.release} has no $name any more (it keeps the last three builds): build it again.")
        val file = File(dir(context), name)
        if (!file.isFile || (asset.size > 0 && file.length() != asset.size)) download(context, asset, file, progress)
        val leftOut = pending.leftOut ?: runCatching { leftOut(context, pending) }.getOrDefault(emptyList())
        val built = ModuleBuild.Built(
            pending.versionCode, pending.request, ModuleBuild.without(pending.modules, leftOut), System.currentTimeMillis(),
            leftOut, file.length(),
        )
        swapIn(context, file, built, progress, deleteBadFile = true)
        setRealm(context, built)
        setPending(context, null)
        // Kept, to put it back in later without building it again.
        if (file.renameTo(savedFile(context, built.request))) {
            setSaved(context, listOf(built) + _saved.value.filterNot { it.request == built.request })
            runCatching { tidySaved(context) }
        } else {
            file.delete()
        }
        return "The realm is changed. It runs at its next start."
    }

    private suspend fun putInNow(context: Context, request: String, progress: (Float?, String?) -> Unit): String {
        unavailableReason(context)?.let { throw IOException(it) }
        val built = _saved.value.firstOrNull { it.request == request } ?: throw IOException("There's no finished build to put in.")
        if (built.versionCode != versionCode(context)) throw IOException("That realm was built for another version of the World of Warcraft app: build it again.")
        val file = savedFile(context, request)
        if (!file.isFile) throw IOException("That realm isn't on the phone any more: build it again.")
        swapIn(context, file, built, progress, deleteBadFile = false)
        setRealm(context, built)
        return "The realm is changed. It runs at its next start."
    }

    private suspend fun installStockNow(context: Context, progress: (Float?, String?) -> Unit): String {
        val slots = slots(context)
        if (!RealmPackage.hasStock(slots)) {
            throw IOException("The realm's own programs aren't kept on the phone: import World of Warcraft again from the World of Warcraft app's export.")
        }
        progress(null, "Stopping the realm…")
        stopRealm(context)
        progress(null, "Putting the realm's own back…")
        withContext(Dispatchers.IO) { RealmPackage.restoreStock(slots) }
        setRealm(context, null)
        return "The realm's own is back. It runs at its next start."
    }

    /**
     * [file] is checked, unpacked next to the realm, and swapped in with the realm stopped; the
     * realm in stays whole until the new one is complete. A damaged download is deleted when
     * [deleteBadFile], so the next try fetches it again.
     */
    private suspend fun swapIn(context: Context, file: File, built: ModuleBuild.Built, progress: (Float?, String?) -> Unit, deleteBadFile: Boolean) {
        val slots = slots(context)
        // The unpacked realm (about seven times the package) next to the one in now, which stays until the swap.
        requireSpace(slots.staging.parentFile ?: slots.staging, file.length() * 8)
        val unpacking = "Unpacking the realm…"
        progress(0f, unpacking)
        try {
            RealmPackage.unpackToStaging(file, slots, ModuleBuild.stamp(built)) { progress(it, unpacking) }
        } catch (e: IOException) {
            if (deleteBadFile) file.delete()
            throw IOException("Couldn't unpack the realm: ${e.message ?: ""}".trim())
        }
        try {
            currentCoroutineContext().ensureActive()
            progress(null, "Stopping the realm…")
            stopRealm(context)
            progress(null, "Putting the realm in…")
            RealmPackage.commit(slots)
        } catch (e: Exception) {
            slots.staging.deleteTree()
            throw e
        }
    }

    /** Stops the Wrath realm and waits for it (characters are saved first). Another game's realm is left running. */
    private suspend fun stopRealm(context: Context) {
        fun ours() = WowRealm.status.value.realm.let { it == Realm.CHROMIE || it == Realm.REMIX }
        fun down() = WowRealm.status.value.phase.let { it == WowRealm.Phase.STOPPED || it == WowRealm.Phase.FAILED }
        if (!ours() || down()) return
        WowRealm.stopAndWait(context)
        if (ours() && !down()) throw IOException("The realm didn't stop. Stop it from the notification and try again.")
    }

    private fun requireSpace(near: File, needed: Long) {
        var probe: File? = near
        while (probe != null && !probe.exists()) probe = probe.parentFile
        val free = probe?.usableSpace ?: return
        if (free < needed + (200L shl 20)) {
            throw IOException("Not enough free space: about ${mb(needed)} MB is needed and ${mb(free)} MB is free.")
        }
    }

    private fun mb(bytes: Long) = bytes shr 20

    private fun <T> network(block: () -> T): T =
        try {
            block()
        } catch (e: IOException) {
            throw IOException("GitHub couldn't be reached (${e.message ?: e.javaClass.simpleName}). Try again.")
        }

    /**
     * [asset] downloaded to [file], carrying on from a part already there, checked for its size and
     * (when GitHub gives one) its SHA-256 before it is used.
     */
    private suspend fun download(context: Context, asset: ModuleSource.Asset, file: File, progress: (Float?, String?) -> Unit) {
        val part = File(file.path + ".part")
        val api = api(context)
        val label = "Downloading your realm"
        var tries = 0
        while (true) {
            try {
                val total = asset.size
                if (total > 0 && part.length() > total) part.delete()
                requireSpace(file.parentFile ?: file, (if (total > 0) total - part.length() else 0L) + total * 8)
                if (total <= 0 || part.length() < total) {
                    val have = part.length()
                    val connection = api.open(asset.url, GitHubApi.FILE, readTimeoutMs = 60_000, rangeFrom = have)
                    try {
                        val resumed = have > 0 && connection.responseCode == 206
                        var done = if (resumed) have else 0L
                        FileOutputStream(part, resumed).use { output ->
                            connection.inputStream.use { input ->
                                val buffer = ByteArray(1 shl 16)
                                var reported = done
                                while (true) {
                                    currentCoroutineContext().ensureActive()
                                    val n = input.read(buffer)
                                    if (n < 0) break
                                    output.write(buffer, 0, n)
                                    done += n
                                    if (done - reported >= 1 shl 20) {
                                        reported = done
                                        progress(if (total > 0) done.toFloat() / total else null, "$label · ${mb(done)} MB" + if (total > 0) " / ${mb(total)} MB" else "")
                                    }
                                }
                            }
                        }
                    } finally {
                        connection.disconnect()
                    }
                }
                if (total > 0 && part.length() != total) throw IOException("The download ended early")
                if (asset.sha256 != null) {
                    progress(null, "Checking the download…")
                    if (RealmPackage.sha256(part) != asset.sha256) {
                        part.delete()
                        throw VerifyFailed("The download came out damaged, and was deleted. Try again.")
                    }
                }
                file.delete()
                if (!part.renameTo(file)) throw IOException("The download couldn't be saved")
                return
            } catch (e: VerifyFailed) {
                throw IOException(e.message)
            } catch (e: GitHubApi.HttpError) {
                if (e.code in 500..599 && ++tries < 6) {
                    delay(3_000L * tries)
                    continue
                }
                // GitHub said no (the token, a missing file): trying again won't change it.
                throw IOException("GitHub wouldn't send the realm (${e.reason ?: "HTTP ${e.code}"}). Does the token have read access to the repository's contents?")
            } catch (e: CancellationException) {
                throw e
            } catch (e: IOException) {
                if (e.message?.startsWith("Not enough free space") == true || ++tries >= 6) {
                    throw IOException(
                        if (e.message?.startsWith("Not enough free space") == true) e.message
                        else "The download stopped (${e.message ?: e.javaClass.simpleName}). Try again: it carries on from where it got to.",
                    )
                }
                delay(3_000L * tries)
            }
        }
    }

    private class VerifyFailed(message: String) : Exception(message)

    private const val CHOSEN = "chosen.json"
    private const val PENDING = "pending.json"
    private const val REALM = "realm.json"
    private const val SAVED = "realms.json"
    private const val MAX_SAVED = 12
    private const val PREFS = "wow_modules_github"
    private const val KEY_TOKEN = "token"

    /** For tests: the state read again from the files next time. */
    @Synchronized
    internal fun resetForTests() {
        loaded = false
        _chosen.value = emptyList()
        _pending.value = null
        _realm.value = null
        _saved.value = emptyList()
        _hasToken.value = false
        _work.value = Work.Idle
        _stockKept.value = false
    }
}

/** A one-line status for the settings card: the modules picked, the build under way, the realm in. */
fun modulesSummary(context: Context): String {
    ModuleStore.load(context)
    ModuleStore.unavailableReason(context)?.let { return "Needs the Wrath+ realm imported" }
    val build = ModuleStore.pending.value
    val current = ModuleStore.realm.value
    val picked = ModuleStore.chosen.value.size
    return when {
        build != null && !build.isDone -> "Building your realm on GitHub…"
        build != null && build.succeeded -> "Your realm is built: put it in"
        build != null -> "The realm's build failed"
        current != null -> "Realm with ${current.modules.size} module${if (current.modules.size == 1) "" else "s"} of yours"
        picked > 0 -> "$picked module${if (picked == 1) "" else "s"} picked, not built yet"
        else -> "AzerothCore modules for your realm"
    }
}
