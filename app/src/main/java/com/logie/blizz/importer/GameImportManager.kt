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
        /** How far the game's own installer has got (copied, running, finished), when there is a copy of one. */
        val installer: InstallerRun.Status? = null,
    )

    /** How a game's folder is recognised in what its installer made ([InstallerRun]). */
    private class InstallerKit(val isRoot: (Set<String>) -> Boolean, val loose: (File) -> File?)

    private fun kit(gameId: String): InstallerKit? = when (gameId) {
        "starcraft2" -> StarCraft2OfflineImporter().let { InstallerKit(it.isGameRoot, it::looseGameRoot) }
        else -> null
    }

    /** The games' Windows as the installer sees it (its C: drive, Wine's last output). */
    private fun host(context: Context): InstallerHost = object : InstallerHost {
        // "Blizzard" is the container [com.logie.blizz.game.WindowsRuntime] makes.
        override fun wineDriveC(): File? = runCatching {
            com.winlator.container.ContainerManager(context).containers.firstOrNull { it.name == "Blizzard" }
                ?.rootDir?.let { File(it, ".wine/drive_c") }?.takeIf { it.isDirectory }
        }.getOrNull()

        override fun logTail(): String = runCatching {
            com.logie.blizz.game.GameLog.snapshot().lines().takeLast(40).joinToString("\n")
        }.getOrDefault("")
    }

    private fun installerStatus(context: Context, gameId: String): InstallerRun.Status? {
        val kit = kit(gameId) ?: return null
        return runCatching { InstallerRun.status(paths(context), gameId, kit.isRoot, kit.loose, host(context)) }.getOrNull()?.takeIf { it != InstallerRun.Status.None }
    }

    /** Looks at the installer's folders in the background and adds what it finds to the state the wizard shows. */
    private fun refreshInstaller(app: Context, gameId: String) {
        scope.launch {
            val status = installerStatus(app, gameId)
            if (synchronized(cancels) { cancels.containsKey(gameId) }) return@launch
            _states.value[gameId]?.let { publish(it.copy(installer = status)) }
        }
    }

    /** Takes away the installer's copy and what it made (the installed game and the saves stay). */
    fun removeInstallerCopy(context: Context, gameId: String) {
        val app = context.applicationContext
        if (synchronized(cancels) { cancels.containsKey(gameId) }) return
        scope.launch {
            InstallerRun.removeCopy(paths(app), gameId)
            repo(app).update(gameId) { if (it.problem == Problem.INSTALLER_MUST_RUN) it.copy(message = "The installer's copy was removed. Tap Run the installer to copy it again.", detail = null) else it }
            publish(WizardState(gameId, repo(app).load(gameId), entry = library(app).get(gameId)))
        }
    }

    private val importers: Map<String, () -> GameImporter> = mapOf(
        "diablo" to { Diablo1DevilutionXImporter() },
        "diablo2" to { Diablo2ClassicImporter() },
        "starcraft" to { StarCraftClassicImporter() },
        "starcraft_remastered" to { StarCraftRemasteredImporter() },
        "starcraft2" to { StarCraft2OfflineImporter() },
        // Warcraft I and II: native Stratagus from the GOG files (the conversion tools are set in [env]).
        "warcraft" to { Warcraft1Importer() },
        "warcraft2" to { Warcraft2Importer() },
        // Warcraft III, one install for both ("warcraft3_tft" uses RoC's when it's there), on the app's Winlator.
        "warcraft3_roc" to { Warcraft3Importer(Warcraft3Importer.Product.ROC) },
        "warcraft3_tft" to { Warcraft3Importer(Warcraft3Importer.Product.TFT) },
        // World of Warcraft: the WoW app's verified export, copied over (its realms still run in that app).
        "wow" to { WowImporter() },
        "wow_legion" to { WowImporter(WowImporter.WowMode.LEGION) },
        "wow_octowow" to { WowImporter(WowImporter.WowMode.OCTOWOW) },
        "wow_forever" to { WowImporter(WowImporter.WowMode.FOREVER) },
        // Diablo II: Resurrected: the player's own Switch packages (a 7z of the .nsp files, base game and update), unpacked with hactool.
        "diablo2_resurrected" to { Diablo2ResurrectedImporter() },
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
        val before = _states.value[gameId]
        publish(WizardState(gameId, record, entry = library(context).get(gameId), missing = before?.missing ?: emptyList(), installer = before?.installer))
        refreshInstaller(context.applicationContext, gameId)
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
                // A game the installer put in the app's Windows (it ignored the folder it was given) is brought to the folder the import reads.
                kit(gameId)?.let { k -> runCatching { InstallerRun.collect(env.paths, gameId, k.isRoot, k.loose, host(app)) } }
                val supplied = supplied(app, repo.load(gameId))
                val result = ImportPipeline(repo, library).run(factory(), env, supplied, repair)
                state = when (result) {
                    is ImportPipeline.Result.Waiting -> state.copy(record = result.record, missing = result.missing, autoSources = result.autoSources)
                    is ImportPipeline.Result.Done -> state.copy(record = result.record, validation = result.validation, entry = result.entry, missing = emptyList())
                    is ImportPipeline.Result.Failed -> {
                        reportFailure(app, gameId, repair, result)
                        var record = result.record
                        if (result.error.problem == Problem.INSTALLER_MUST_RUN) {
                            // The installer ran and made nothing: what Wine printed is the evidence.
                            val tail = host(app).logTail()
                            if (tail.isNotBlank() && InstallerRun.readRun(env.paths, gameId) != null) {
                                record = repo.update(gameId) { it.copy(detail = (it.detail ?: "") + "\n\nWine's last output:\n" + tail) }
                            }
                        }
                        state.copy(record = record, validation = result.validation, missing = emptyList())
                    }
                }
            } finally {
                synchronized(cancels) { cancels.remove(gameId) }
                publish(state.copy(running = false, progress = null, entry = library.get(gameId)))
                if (synchronized(cancels) { cancels.isEmpty() }) ImportService.stop(app)
                refreshInstaller(app, gameId)
            }
        }
    }

    /** Not a failure: the person stopped it. Every other failed install is sent, a full phone and an unsupported version included. */
    private val NOT_BUGS = setOf(Problem.CANCELLED)

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
            files = runCatching { installFiles(context, gameId) }.getOrNull(),
        )
    }

    /** What the failed install had to work with and left behind ([InstallManifest]): sent with the report, so the files needn't be. */
    private fun installFiles(context: Context, gameId: String): String {
        val paths = paths(context)
        val record = repo(context).load(gameId)
        return buildString {
            for ((id, supplied) in supplied(context, record)) (supplied as? Supplied.Picked)?.let { append(InstallManifest.describe(it.source, "Picked for $id")) }
            append(InstallManifest.describe(paths.game(gameId), "Installed folder games/$gameId"))
            append(InstallManifest.describe(paths.staging(gameId), "Staging staging/$gameId"))
            for (suffix in listOf("work", "scratch", "installer")) {
                val dir = File(paths.staging, "$gameId-$suffix")
                if (dir.exists()) append(InstallManifest.describe(dir, "Left in staging/$gameId-$suffix", limit = 300))
            }
        }
    }

    /**
     * Run the game's own installer in the app's Windows ([InstallerRun]): its files are copied into the
     * app, then it's started silently; when it has finished, Retry imports what it installed.
     */
    fun runInstaller(context: Context, gameId: String) {
        val app = context.applicationContext
        if (importers[gameId] == null) return
        synchronized(cancels) {
            if (cancels.containsKey(gameId)) return
            cancels[gameId] = CancelToken()
        }
        val cancel = cancels[gameId]!!
        ImportService.start(app)
        scope.launch {
            val repo = repo(app)
            var state = WizardState(gameId, repo.load(gameId), running = true, entry = library(app).get(gameId))
            var missing: List<MissingInput> = emptyList()
            publish(state)
            try {
                val env = env(app, gameId, cancel) { p ->
                    state = state.copy(progress = p, record = state.record.copy(stage = p.stage))
                    publish(state)
                    ImportService.update(app, p)
                }
                val paths = env.paths
                val setup: File
                if (InstallerRun.copyComplete(paths, gameId)) {
                    // Copied before (or just finished): nothing is copied again.
                    setup = File(paths.installer(gameId), InstallerRun.readManifest(paths, gameId)!!.setup)
                } else {
                    val source = InstallerRun.sourceOf(supplied(app, repo.load(gameId)), null)
                        ?: throw ImportException(Problem.MISSING_SOURCE_DATA, "Pick the folder that holds the installer (Setup.exe) and its data files first.")
                    if (InstallerRun.needsFolder(source)) {
                        // A lone file from the picker: its data files can't be seen. Ask for the folder; the import goes on from there.
                        val question = InstallerRun.folderQuestion(InstallerRun.find(source)?.first?.name ?: source.name)
                        repo.update(gameId) { it.copy(stage = Stage.WAITING_FOR_USER_FILE, outcome = null, problem = null, message = question.prompt, detail = null) }
                        missing = listOf(question)
                        return@launch
                    }
                    setup = InstallerRun.prepare(env, gameId, source)
                }
                val title = com.logie.blizz.Games.find(gameId)?.fullTitle ?: gameId
                val run = InstallerRun.beginRun(paths, gameId)
                repo.update(gameId) {
                    it.copy(
                        stage = Stage.FAILED, outcome = Outcome.IMPORT_INCOMPLETE, problem = Problem.INSTALLER_MUST_RUN,
                        message = "The installer is running in the app's Windows (it shows nothing on screen and takes a long while). When it has ended, come back here and tap Retry.",
                        detail = "Run ${run.attempt + 1} of ${InstallerRun.VARIANT_COUNT}: ${setup.name} ${InstallerRun.arguments(gameId, run.attempt)}",
                    )
                }
                kotlinx.coroutines.withContext(Dispatchers.Main) { com.logie.blizz.game.WindowsRuntime.play(app, InstallerRun.entry(gameId, title, setup, run.attempt)) }
            } catch (e: Throwable) {
                val problem = (e as? ImportException)?.problem
                    ?: if (e.message?.contains("ENOSPC") == true || e.message?.contains("No space", true) == true) Problem.INSUFFICIENT_STORAGE else Problem.MISSING_SOURCE_DATA
                if (problem == Problem.CANCELLED) {
                    repo.update(gameId) { it.copy(stage = Stage.FAILED, outcome = Outcome.IMPORT_INCOMPLETE, problem = Problem.INSTALLER_MUST_RUN, message = "Cancelled. What was copied is kept: tap Run the installer to go on from there, or remove the copy.", detail = null) }
                } else {
                    val message = if (problem == Problem.INSUFFICIENT_STORAGE && e !is ImportException) "The phone ran out of space while copying the installer's files. Free some and tap Run the installer: the copy goes on from where it stopped." else e.message
                    repo.update(gameId) { it.copy(stage = Stage.FAILED, outcome = Outcome.IMPORT_INCOMPLETE, problem = problem, message = message, detail = (e as? ImportException)?.detail ?: e.toString()) }
                    if (problem != Problem.INSUFFICIENT_STORAGE) com.logie.blizz.reports.BugReports.report(app, "$gameId installer copy ($problem)", e.message ?: problem.name, listOf("Game" to gameId), log = e.stackTraceToString())
                }
            } finally {
                synchronized(cancels) { cancels.remove(gameId) }
                publish(WizardState(gameId, repo.load(gameId), running = false, missing = missing, entry = library(app).get(gameId)))
                if (synchronized(cancels) { cancels.isEmpty() }) ImportService.stop(app)
                refreshInstaller(app, gameId)
            }
        }
    }

    /** Back to not installed (not while it's importing): the game's files, entry and record go; saves and downloads stay. */
    fun reset(context: Context, gameId: String) {
        val app = context.applicationContext
        val factory = importers[gameId] ?: return
        if (synchronized(cancels) { cancels.containsKey(gameId) }) return
        scope.launch {
            GameReset.reset(paths(app), gameId, factory().keptInGame)
            publish(WizardState(gameId, repo(app).load(gameId), entry = null))
        }
    }

    fun cancel(gameId: String) {
        synchronized(cancels) { cancels[gameId] }?.cancel()
    }

    /** The person picked a file ([tree] false) or a folder for [inputId]; the import goes on. */
    /** The export this game was imported from, as a document the app may delete (once the copy is verified and in place); null when there is none. */
    fun exportSource(context: Context, gameId: String): Uri? {
        val uri = runCatching { Uri.parse(File(paths(context).state, "export-source-$gameId.txt").readText().trim()) }.getOrNull() ?: return null
        // Only where the picker gave the app write access (a folder added with Search a folder is read-only).
        val writable = context.contentResolver.persistedUriPermissions.any { p ->
            p.isWritePermission && (p.uri == uri || uri.toString().startsWith(p.uri.toString()))
        }
        return uri.takeIf { writable }
    }

    /** Deletes the export the import read from; whether it went (the app needs the picker's write access for that). */
    fun deleteExport(context: Context, gameId: String): Boolean {
        val uri = exportSource(context, gameId) ?: return false
        val gone = runCatching { android.provider.DocumentsContract.deleteDocument(context.contentResolver, uri) }.getOrDefault(false)
        if (gone) File(paths(context).state, "export-source-$gameId.txt").delete()
        return gone
    }

    fun supply(context: Context, gameId: String, inputId: String, uri: Uri, tree: Boolean) {
        val app = context.applicationContext
        // Write access too, so the export can be deleted once it is copied and verified.
        runCatching { app.contentResolver.takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION) }
            .onFailure { runCatching { app.contentResolver.takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION) } }
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
        val hactool = Tools.file(context, "libhactool.so")
        ConversionTools.installed = DeviceConversionTools(context.applicationContext)
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
            hactool = if (hactool.isFile) Hactool(hactool) else null,
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
