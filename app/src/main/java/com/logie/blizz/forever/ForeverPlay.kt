package com.logie.blizz.forever

import android.content.Context
import android.net.Uri
import com.logie.blizz.game.LaunchProfile
import com.logie.blizz.game.WindowsRuntime
import com.logie.blizz.importer.DocumentNode
import com.logie.blizz.importer.LibraryEntry
import com.logie.blizz.importer.SourceNode
import com.logie.blizz.importer.Stage
import com.logie.blizz.wow.WowLogin
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File

/**
 * Play for World of Warcraft: Forever, offline on the phone:
 *
 * 1. the server package is downloaded the first time, and again when a fixed or newer one is published ([ForeverServerPackage]);
 * 2. the current Forever client must be present ([ForeverLayout.client]): the person picks its folder and it is copied in ([importClient]);
 * 3. the server's map data is made from the client the first time ([ForeverRealm.extractData]);
 * 4. the realm is started ([ForeverRealm]) at the client's own build, with the game account made, and waited for;
 * 5. the client is started on Blizzard's own Winlator ([WindowsRuntime.play]) with the `wow` touch controls.
 *
 * The client is pointed at the local server by the **Forever Launcher** ([ForeverLayout.clientExe]), which sets the
 * server's key in the client; it is a separate program the user supplies. Nothing talks to Blizzard's servers.
 *
 * NOT run on a phone. The state machine is the only logic here; the realm, the client and the connection need a phone.
 */
object ForeverPlay {
    sealed interface State {
        data object Idle : State
        /** [pausable]: the client download, which can be paused (it resumes on the next Play). */
        data class Preparing(val message: String, val progress: Float? = null, val pausable: Boolean = false) : State
        /**
         * The Forever client isn't here and the connection is metered (mobile data): the launcher asks before
         * downloading ~47 GB, or lets the person pick a client folder already on the phone.
         */
        data object NeedsClient : State
        /**
         * The client is here but the Forever Launcher isn't. The game then starts and logs in to the realm, and is
         * disconnected as it enters it: the client checks the world server's identity against a key of Blizzard's
         * ("server identity check failed", seen on a desktop run of client 70862 against this realm on 10 November
         * 2026: BLZ51901023 on screen). The launcher, which the person supplies, is what gets a client past that.
         * The launcher asks: pick the file, or start the game as it is.
         */
        data object NeedsLauncher : State
        data class Failed(val message: String) : State
    }

    /** About how big the client download is (build 70862: Windows, x86_64, English, text and speech). */
    const val CLIENT_SIZE_GB = 47

    @Volatile private var installer: com.logie.blizz.forever.tact.ForeverClientInstaller? = null

    /** Pauses the client download; what is downloaded is kept and the next Play goes on from there. */
    fun pauseDownload() { installer?.cancel() }

    /** Whether a client download was begun and not finished. */
    fun downloadPaused(context: Context) = File(ForeverLayout.of(context).root, "$DOWNLOAD/.blizz-download").isFile

    private fun metered(context: Context): Boolean = runCatching {
        context.getSystemService(android.net.ConnectivityManager::class.java).isActiveNetworkMetered
    }.getOrDefault(true)

    /** Play, downloading the client even on a metered connection (the person said so). */
    fun downloadClient(context: Context) = play(context, allowMetered = true)

    /**
     * Resets Forever: the realm (its server, database with the characters, map data, logs and run files; the next
     * Play downloads the server again) and, with [client], the game client too (downloaded or copied, finished or
     * not). A running download is paused and the realm stopped first.
     */
    fun reset(context: Context, client: Boolean) {
        val app = context.applicationContext
        pauseDownload()
        _state.value = State.Preparing(if (client) "Resetting World of Warcraft: Forever" else "Resetting the realm")
        scope.launch {
            try {
                withContext(Dispatchers.IO) {
                    // Let a paused download finish writing its current file before its folder goes.
                    repeat(100) { if (installer == null) return@repeat; Thread.sleep(100) }
                    if (ForeverRealm.status.value.phase != ForeverRealm.Phase.STOPPED) runCatching { ForeverRealm.stop(app) }
                    val layout = ForeverLayout.of(app)
                    val realm = listOf("server", "server.new", "server.old", "mysql", "data", "data.work", "data.old", "logs", "run", "etc", "forever-server.tar.xz.part")
                    val game = if (client) listOf("client", "client.new", DOWNLOAD) else emptyList()
                    for (name in realm + game) File(layout.root, name).deleteRecursively()
                }
                _state.value = State.Idle
            } catch (e: Throwable) {
                _state.value = State.Failed("The reset didn't finish: ${e.message ?: e.javaClass.simpleName}")
            }
        }
    }

    /**
     * Repairs the installation without losing the big downloads: keeps the realm server, the database (characters)
     * and the game client, but clears everything the app set up around them so the next Play rebuilds it from the
     * current version — the .NET runtime and the launcher's config in the container ([WindowsRuntime.clearForeverRuntime]),
     * and the placed Forever Launcher (re-picked), which is how an old launcher from a previous version is replaced.
     * It also re-checks the client's index files (the update section the game insists on). A running realm is stopped first.
     */
    fun repair(context: Context) {
        val app = context.applicationContext
        pauseDownload()
        _state.value = State.Preparing("Repairing World of Warcraft: Forever")
        scope.launch {
            try {
                withContext(Dispatchers.IO) {
                    repeat(100) { if (installer == null) return@repeat; Thread.sleep(100) }
                    if (ForeverRealm.status.value.phase != ForeverRealm.Phase.STOPPED) runCatching { ForeverRealm.stop(app) }
                    val layout = ForeverLayout.of(app)
                    // The launcher a previous version left in the client folder is removed, so Play asks for the current one.
                    ForeverLauncher.removePlaced(layout.client)
                    // Its config beside it too (also when the games' Windows isn't made yet).
                    ForeverLauncher.clearConfig(layout.client, null)
                    // The container's Forever setup (the .NET runtime, the seeded config, an old browser runtime) is rebuilt on Play.
                    runCatching { WindowsRuntime.clearForeverRuntime(app) }
                    // The client's index files get the update section again, in place (nothing re-downloaded).
                    runCatching { com.logie.blizz.forever.tact.CascStorageWriter.repairIndexes(File(layout.client, "Data/data")) }
                }
                _state.value = State.Idle
            } catch (e: Throwable) {
                _state.value = State.Failed("The repair didn't finish: ${e.message ?: e.javaClass.simpleName}")
            }
        }
    }

    /**
     * Deletes **everything** for World of Warcraft: Forever and starts from zero: every file on disk (the realm server,
     * the database with the characters, the map data, the certificate, the game client — downloaded or copied — and any
     * part-download, logs and run files), and everything the app set up in the shared Winlator container (the .NET
     * runtime, the launcher's config, an old browser runtime a previous version left). The next Play is a clean install.
     * A running realm is stopped and a running download cancelled first. This is the "Reset everything" / nuke.
     */
    fun nuke(context: Context) {
        val app = context.applicationContext
        pauseDownload()
        _state.value = State.Preparing("Deleting everything for World of Warcraft: Forever")
        scope.launch {
            try {
                withContext(Dispatchers.IO) {
                    repeat(100) { if (installer == null) return@repeat; Thread.sleep(100) }
                    if (ForeverRealm.status.value.phase != ForeverRealm.Phase.STOPPED) runCatching { ForeverRealm.stop(app) }
                    // Every Forever file on disk (files/forever: server, client, data, mysql, ca, downloads, logs, run).
                    ForeverLayout.of(app).root.deleteRecursively()
                    // Everything the app set up in the shared container (the .NET runtime, the seeded config, an old browser runtime).
                    runCatching { WindowsRuntime.clearForeverRuntime(app) }
                    // The saved crash-watch marker (the account is remade on the next Play).
                    runCatching { prefs(app).edit().clear().apply() }
                }
                _state.value = State.Idle
            } catch (e: Throwable) {
                _state.value = State.Failed("Couldn't delete everything: ${e.message ?: e.javaClass.simpleName}")
            }
        }
    }

    /** The client's touch controls id (the same `wow` gestures as the other WoW clients). */
    private const val GAME_ID = "wow-client"
    private const val PROFILE = "wow"

    /** The library's id for Forever: its Auto login account is kept under it ([WowLogin]). */
    const val VERSION = "wow_forever"

    /** The account made on the realm when the person hasn't set one (it never leaves the phone: the realm listens on 127.0.0.1 only). */
    const val DEFAULT_EMAIL = "forever@forever.local"
    const val DEFAULT_PASSWORD = "forever"

    /** The account the client logs in with: the person's own (Auto login in the game's settings), else the default, saved so it shows there. */
    fun login(context: Context): WowLogin.Login = WowLogin.own(context, VERSION)
        ?: WowLogin.Login(DEFAULT_EMAIL, DEFAULT_PASSWORD).also { WowLogin.setOwn(context, VERSION, it.name, it.password) }

    private val _state = MutableStateFlow<State>(State.Idle)
    val state: StateFlow<State> = _state

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)

    fun dismiss() {
        if (_state.value is State.Failed || _state.value is State.NeedsClient || _state.value is State.NeedsLauncher) _state.value = State.Idle
    }

    /** Play without the Forever Launcher (the person said so): the game starts and logs in, and can't enter the realm. */
    fun playWithoutLauncher(context: Context) = play(context, withoutLauncher = true)

    fun play(context: Context, allowMetered: Boolean = false, withoutLauncher: Boolean = false) {
        if (_state.value is State.Preparing) return
        val app = context.applicationContext
        val (width, height) = WindowsRuntime.gameSize(context, GAME_ID, LaunchProfile.WOW)
        _state.value = State.Preparing("Preparing")
        com.logie.blizz.reports.SessionLog.event("forever", "Play pressed (${width}x$height, metered ok: $allowMetered, without launcher: $withoutLauncher)")
        scope.launch {
            try {
                val failure = run(app, width to height, allowMetered, withoutLauncher)
                com.logie.blizz.reports.SessionLog.event("forever", "Play ended: ${failure?.let { if (it.startsWith("\u0000")) it.drop(1) else it.lineSequence().first().take(200) } ?: "started"}")
                _state.value = when (failure) {
                    null, PAUSED -> State.Idle
                    NEEDS_CLIENT -> State.NeedsClient
                    NEEDS_LAUNCHER -> State.NeedsLauncher
                    else -> State.Failed(failure)
                }
            } catch (e: CancellationException) {
                _state.value = State.Idle
                throw e
            } catch (e: Throwable) {
                val step = (_state.value as? State.Preparing)?.message
                _state.value = State.Failed(e.message ?: e.javaClass.simpleName)
                report(app, e, step)
            }
        }
    }

    /** A failure goes to the app's GitHub issues (with its step and trace), as the importers' do; a full phone isn't a bug. */
    private fun report(context: Context, e: Throwable, step: String?) {
        if (e is com.logie.blizz.forever.tact.ForeverClientInstaller.NotEnoughSpaceException) return
        runCatching {
            com.logie.blizz.reports.BugReports.report(
                context, "WoW Forever", e.message ?: e.javaClass.simpleName,
                listOf("Step" to step, "Error" to e.javaClass.name, "Cause" to e.cause?.let { "${it.javaClass.name}: ${it.message}" }),
                log = e.stackTraceToString().take(7000),
                attach = true,
            )
        }
    }

    /** Whether the client is here but no Forever Launcher is (so the client can't yet connect to the realm). */
    fun needsLauncher(context: Context): Boolean = ForeverLayout.of(context).let { it.hasClient() && !it.hasLauncher() }

    /**
     * Copies the Forever Launcher the person picked (a .exe they supply) into the client folder, so the app runs it
     * in place of Wow.exe at the next Play. The file keeps a launcher name the client start looks for.
     */
    fun importLauncher(context: Context, uri: Uri, thenPlay: Boolean = false) {
        val app = context.applicationContext
        _state.value = State.Preparing("Adding the Forever Launcher")
        scope.launch {
            try {
                val failure = withContext(Dispatchers.IO) {
                    val layout = ForeverLayout.of(app)
                    if (!layout.client.isDirectory) return@withContext "Add the game client first, then the launcher."
                    val picked = app.contentResolver.query(uri, arrayOf(android.provider.OpenableColumns.DISPLAY_NAME), null, null, null)
                        ?.use { if (it.moveToFirst()) it.getString(0) else null }
                    // Keep a known launcher name the client start looks for; anything else becomes WoWForeverLauncher.exe.
                    val target = File(layout.client, ForeverLauncher.fileNameFor(picked))
                    app.contentResolver.openInputStream(uri)?.use { input -> target.outputStream().use { input.copyTo(it) } }
                        ?: return@withContext "That file couldn't be read."
                    null
                }
                _state.value = if (failure != null) State.Failed(failure) else State.Idle
                if (failure == null && thenPlay) play(app)
            } catch (e: CancellationException) { _state.value = State.Idle; throw e }
            catch (e: Throwable) { _state.value = State.Failed("The launcher couldn't be added: ${e.message ?: e.javaClass.simpleName}") }
        }
    }

    /**
     * Copies the client from a folder the person picked (Android's folder picker: Downloads, an SD card, a USB drive)
     * into the app, then goes on with Play. The picked folder may be the client itself or the folder holding it.
     */
    fun importClient(context: Context, tree: Uri) {
        if (_state.value is State.Preparing) return
        val app = context.applicationContext
        _state.value = State.Preparing("Reading the client folder")
        scope.launch {
            try {
                val failure = withContext(Dispatchers.IO) { copyClient(app, tree) }
                if (failure != null) _state.value = State.Failed(failure) else { _state.value = State.Idle; play(app) }
            } catch (e: CancellationException) {
                _state.value = State.Idle
                throw e
            } catch (e: Throwable) {
                _state.value = State.Failed("The client couldn't be copied: ${e.message ?: e.javaClass.simpleName}")
            }
        }
    }

    private const val NEEDS_CLIENT = "\u0000needs-client"
    private const val NEEDS_LAUNCHER = "\u0000needs-launcher"
    private const val PAUSED = "\u0000paused"

    /** Where the client is downloaded to; renamed to [ForeverLayout.client] once complete. */
    private const val DOWNLOAD = "client.download"

    /**
     * Downloads the client from Blizzard's CDN ([com.logie.blizz.forever.tact.ForeverClientInstaller]) with the
     * app kept alive by the import service (its notification shows the progress). Null when the client is in place;
     * [PAUSED] when paused; else what went wrong.
     */
    private suspend fun fetchClient(context: Context, layout: ForeverLayout): String? = withContext(Dispatchers.IO) {
        val target = File(layout.root, DOWNLOAD)
        var notified = 0L
        // The speed over the last few seconds, and the time left at that speed.
        var rateAt = 0L
        var rateDone = 0L
        var rate = 0.0
        val install = com.logie.blizz.forever.tact.ForeverClientInstaller(target, onProgress = { p ->
            val label = when {
                p.total <= 0 -> p.step
                p.step.startsWith("Downloading") -> {
                    val now = System.currentTimeMillis()
                    if (rateAt == 0L) { rateAt = now; rateDone = p.done } else if (now - rateAt >= 2000) {
                        val instant = (p.done - rateDone) * 1000.0 / (now - rateAt)
                        rate = if (rate == 0.0) instant else rate * 0.7 + instant * 0.3
                        rateAt = now; rateDone = p.done
                    }
                    val speed = if (rate > 0) {
                        val left = ((p.total - p.done) / rate).toLong()
                        " · %.0f MB/s · %s left".format(rate / 1e6, if (left >= 3600) "%dh %02dm".format(left / 3600, left % 3600 / 60) else "%dm %02ds".format(left / 60, left % 60))
                    } else ""
                    "%s… %.1f / %.1f GB%s".format(p.step, p.done / 1e9, p.total / 1e9, speed)
                }
                else -> "${p.step}… ${p.done} / ${p.total}"
            }
            _state.value = State.Preparing(label, if (p.total > 0) p.done.toFloat() / p.total else null, pausable = true)
            val now = System.currentTimeMillis()
            if (now - notified >= 1000) {
                notified = now
                com.logie.blizz.importer.ImportService.update(context, com.logie.blizz.importer.Progress(com.logie.blizz.importer.Stage.DOWNLOADING, label, p.done, p.total))
            }
        })
        installer = install
        com.logie.blizz.importer.ImportService.start(context)
        try {
            install.install()
        } finally {
            installer = null
            com.logie.blizz.importer.ImportService.stop(context)
        }
        if (!File(target, ".build.info").isFile) return@withContext PAUSED
        layout.client.deleteRecursively()
        if (!target.renameTo(layout.client)) return@withContext "The downloaded client couldn't be put in place."
        null
    }

    /** Folders a client makes as it runs; not copied (the game remakes them). */
    private val SKIPPED = setOf("cache", "logs", "errors")

    private fun copyClient(context: Context, tree: Uri): String? {
        val layout = ForeverLayout.of(context)
        val picked = DocumentNode.tree(context.contentResolver, tree)
        val path = ForeverCtl.findClient<SourceNode>(picked) { node ->
            if (node.isDirectory) node.children().map { it.name to it } else emptyList()
        } ?: return "That folder isn't the Forever client. Pick the folder that holds .build.info, Data and _forever_ " +
            "(or the folder right above it)."
        val client = path.lastOrNull() ?: picked

        _state.value = State.Preparing("Measuring the client")
        val total = sizeOf(client)
        val free = layout.root.apply { mkdirs() }.usableSpace
        val need = total + (512L shl 20)
        if (free in 1 until need) {
            return "Not enough space to copy the client: it needs about ${need shr 20} MB free, but only ${free shr 20} MB is left."
        }

        val staging = File(layout.root, "client.new")
        staging.deleteRecursively()
        staging.mkdirs()
        var done = 0L
        var reported = 0L
        fun progress(bytes: Long) {
            done += bytes
            if (done - reported >= (32L shl 20) || done == total) {
                reported = done
                _state.value = State.Preparing("Copying the client… ${done shr 20} / ${total shr 20} MB", if (total > 0) done.toFloat() / total else null)
            }
        }
        for (child in client.children()) copyNode(child, staging, ::progress)
        layout.client.deleteRecursively()
        if (!staging.renameTo(layout.client)) return "The copied client couldn't be put in place."
        return null
    }

    private fun sizeOf(node: SourceNode): Long = when {
        !node.isDirectory -> node.size.coerceAtLeast(0L)
        node.name.lowercase() in SKIPPED -> 0L
        else -> node.children().sumOf { sizeOf(it) }
    }

    private fun copyNode(node: SourceNode, into: File, onBytes: (Long) -> Unit) {
        val name = node.name
        if (name.isEmpty() || name == "." || name == ".." || '/' in name) return
        val target = File(into, name)
        if (node.isDirectory) {
            if (name.lowercase() in SKIPPED) return
            target.mkdirs()
            for (child in node.children()) copyNode(child, target, onBytes)
            return
        }
        node.open().use { input ->
            target.outputStream().buffered(1 shl 16).use { out ->
                val buffer = ByteArray(1 shl 16)
                while (true) {
                    val n = input.read(buffer)
                    if (n < 0) break
                    out.write(buffer, 0, n)
                    onBytes(n.toLong())
                }
            }
        }
    }

    private suspend fun run(context: Context, size: Pair<Int, Int>, allowMetered: Boolean, withoutLauncher: Boolean): String? {
        val layout = ForeverLayout.of(context)
        val running = ForeverRealm.status.value.phase.let { it == ForeverRealm.Phase.RUNNING || it == ForeverRealm.Phase.STARTING }

        // A fixed or newer server package is fetched when one is published (never while the realm runs from the old one).
        val installed = ForeverServerPackage.installed(context)
        val outdated = installed && !running && withContext(Dispatchers.IO) { ForeverServerPackage.outdated(context) }
        if (!installed || outdated) {
            val what = if (outdated) "Updating the realm server" else "Downloading the realm server"
            _state.value = State.Preparing(what, 0f)
            withContext(Dispatchers.IO) {
                ForeverServerPackage.install(
                    context,
                    onStage = { message -> _state.value = State.Preparing(if (message.startsWith("Downloading")) what else message) },
                    onProgress = { done, total -> _state.value = State.Preparing(what, if (total > 0) done.toFloat() / total else null) },
                )
            }
        }

        // The client: downloaded from Blizzard's CDN as part of Play (on mobile data only once the person agrees).
        if (!layout.hasClient()) {
            if (!allowMetered && metered(context)) return NEEDS_CLIENT
            fetchClient(context, layout)?.let { return it }
        }

        // Without the Forever Launcher the game is disconnected as it enters the realm: said before the wait, not after it.
        if (!withoutLauncher && !layout.hasLauncher()) return NEEDS_LAUNCHER

        // The index files of a client downloaded by an earlier build lacked a part the game insists on ("Your World of
        // Warcraft installation is damaged"): given it here, in place, the 47 GB untouched.
        withContext(Dispatchers.IO) { runCatching { com.logie.blizz.forever.tact.CascStorageWriter.repairIndexes(File(layout.client, "Data/data")) } }

        if (!layout.hasServerData()) {
            _state.value = State.Preparing("Preparing the game data (first time, several minutes)")
            withContext(Dispatchers.IO) {
                ForeverRealm.extractData(context, layout.client) { line -> _state.value = State.Preparing(line) }
            }
        }

        _state.value = State.Preparing("Starting the realm")
        val account = login(context)
        com.logie.blizz.reports.SessionLog.event("forever", "client ${layout.clientBuild()}, launcher ${layout.launcher()?.let { "${it.name} ${it.length()} bytes" } ?: "none"}; starting the realm (account ${account.name})")
        val realmStart = android.os.SystemClock.elapsedRealtime()
        withContext(Dispatchers.IO) { ForeverRealm.start(context, layout.clientBuild(), account.name to account.password) }
        // Each step of the start shows by its number, and under the long one (the world loading its database) the
        // server's own latest line, so the wait is seen to move.
        val following = scope.launch {
            var lastStep: Any? = null
            while (true) {
                val now = ForeverRealm.status.value
                val stepNow = now.phase to now.step
                if (stepNow != lastStep) {
                    lastStep = stepNow
                    com.logie.blizz.reports.SessionLog.event("forever", "realm ${now.phase} ${now.step ?: ""} ${now.message ?: ""} after ${(android.os.SystemClock.elapsedRealtime() - realmStart) / 1000} s".replace("  ", " "))
                }
                if (now.phase == ForeverRealm.Phase.STARTING) {
                    val step = now.step ?: ForeverRealm.Step.CONFIGURING
                    val detail = if (step == ForeverRealm.Step.WORLD) withContext(Dispatchers.IO) { ForeverCtl.lastLine(layout.log("worldserver")) } else null
                    val head = "Starting the realm (${step.ordinal + 1} of ${ForeverRealm.Step.entries.size}): ${now.message ?: step.name.lowercase()}"
                    _state.value = State.Preparing(listOfNotNull(head, detail).joinToString("\n"))
                }
                kotlinx.coroutines.delay(700)
            }
        }
        val status = try {
            ForeverRealm.status.first { it.phase == ForeverRealm.Phase.RUNNING || it.phase == ForeverRealm.Phase.FAILED || it.phase == ForeverRealm.Phase.STOPPED }
        } finally { following.cancel() }
        when (status.phase) {
            ForeverRealm.Phase.RUNNING -> {}
            ForeverRealm.Phase.FAILED -> return status.error ?: "The realm didn't start (see logs in files/forever/logs)."
            else -> return "The realm stopped before it was ready."
        }

        _state.value = State.Preparing("Starting the game")
        val exe = layout.clientExe() ?: return NEEDS_CLIENT
        // The client logs in at this phone's realm: its portal (WTF/Config.wtf) set to 127.0.0.1, and it opens on its
        // login screen with the account's e-mail in place and nothing in front of it, so the password typed lands.
        withContext(Dispatchers.IO) {
            runCatching {
                val game = File(layout.client, "_forever_").takeIf { it.isDirectory }
                    ?: layout.client.listFiles()?.firstOrNull { it.isDirectory && it.name.equals("_forever_", ignoreCase = true) }
                    ?: return@runCatching
                val wtf = game.listFiles()?.firstOrNull { it.isDirectory && it.name.equals("WTF", ignoreCase = true) } ?: File(game, "WTF").apply { mkdirs() }
                val config = wtf.listFiles()?.firstOrNull { it.name.equals("Config.wtf", ignoreCase = true) } ?: File(wtf, "Config.wtf")
                config.writeText(ForeverCtl.withLoginReady(ForeverCtl.withLocalPortal(config.takeIf { it.isFile }?.readText()), account.name))
            }
        }
        started(context)
        com.logie.blizz.reports.SessionLog.event("forever", "realm up after ${(android.os.SystemClock.elapsedRealtime() - realmStart) / 1000} s; starting ${exe.name} in the games' Windows")
        withContext(Dispatchers.Main) { WindowsRuntime.play(context, launchEntry(layout.client, exe), size) }
        return null
    }

    private fun prefs(context: Context) = context.getSharedPreferences("forever", Context.MODE_PRIVATE)

    /** The game is about to start: what it writes about stopping from now on is this start's. */
    private fun started(context: Context) = prefs(context).edit().putLong(STOP_SEEN, System.currentTimeMillis()).putBoolean(STOP_PENDING, true).apply()

    /**
     * Sends what the game itself wrote about a start that went wrong (its crash file, or its storage log's
     * failures: [ForeverCtl.clientStop]) to the app's reports, once. The launcher calls it as it comes back to the
     * front: a game that fell back to it after a black screen has then said why, without the person doing anything.
     */
    fun reportClientStop(context: Context) {
        val app = context.applicationContext
        scope.launch(Dispatchers.IO) {
            runCatching {
                // Once per start (set by [started]): a game or launcher that ran now sends what it left behind.
                if (!prefs(app).getBoolean(STOP_PENDING, false)) return@runCatching
                // Only once the game screen has opened for this Play and closed again: the launcher's screen also
                // comes back while Play is still preparing (the phone, report 122 of 13 November 2026: "stopped early"
                // with nothing of Wine's, sent before any Windows program had run). Still pending until then.
                val since0 = prefs(app).getLong(STOP_SEEN, 0L)
                if (!sessionOver(since0, com.logie.blizz.game.GameLog.startedAt, com.logie.blizz.selftest.RunningGame.alive())) return@runCatching
                prefs(app).edit().putBoolean(STOP_PENDING, false).apply()
                val layout = ForeverLayout.of(app)
                val game = File(layout.client, "_forever_").takeIf { it.isDirectory }
                val since = prefs(app).getLong(STOP_SEEN, 0L)
                val stop = game?.let { ForeverCtl.clientStop(it, since) }
                // The Forever Launcher is a .NET program: when it stops early it writes no WoW crash file, so also keep
                // the Wine/Box64 log (what it printed before it died) — that is where the reason for a launcher crash is.
                // The end holds the crash; the start is mostly thread-naming noise.
                val wine = com.logie.blizz.game.GameLog.snapshot().takeIf { it.isNotBlank() }?.takeLast(7000)
                if (stop == null && wine == null) return@runCatching
                val title = stop?.title ?: "The launcher or game stopped early"
                val body = listOfNotNull(stop?.text, wine?.let { "[wine/box64]\n$it" }).joinToString("\n\n")
                com.logie.blizz.reports.BugReports.report(
                    app, "WoW Forever", "The game stopped: $title",
                    listOf("Program" to layout.clientExe()?.name, "Client build" to layout.clientBuild()?.toString()),
                    log = body.take(7000),
                    attach = true, force = true,
                )
                // The upload above can fail on a flaky network. When the launcher stopped early (a real crash, not a
                // long play session), also show the log in the app with Copy, so it can be sent even then.
                val early = since > 0 && System.currentTimeMillis() - since < EARLY_STOP_MS
                // The game's own protection ended it: said in plain words whenever it happens (it comes about a minute
                // after the game starts, which can be long after Play: the launcher waits for its PLAY NOW).
                if (stop != null && ForeverCtl.isSecurityCrash(stop.text)) _state.value = State.Failed(securityCrashText(layout.hasLauncher(), stop.title))
                else if (early) _state.value = State.Failed(
                    "World of Warcraft: Forever stopped (${layout.clientExe()?.name ?: "launcher"}).\n\n" +
                        "Tap Copy and send me this:\n\n$body",
                )
                Unit
            }
        }
    }

    /**
     * The game's own program ended while the session went on (the Forever Launcher stays up): a report with its exit code,
     * the game's crash file if it wrote one, and Wine's lines of the moment. Sent by itself, once per program that ended.
     */
    fun reportGameEnded(context: Context, program: String, code: String) {
        val app = context.applicationContext
        val wine = com.logie.blizz.game.GameLog.snapshot().takeLast(6000)
        scope.launch(Dispatchers.IO) {
            runCatching {
                val layout = ForeverLayout.of(app)
                val game = File(layout.client, "_forever_").takeIf { it.isDirectory }
                val crash = game?.let { ForeverCtl.clientStop(it, prefs(app).getLong(STOP_SEEN, 0L)) }
                val body = listOfNotNull(crash?.text?.take(3000), "[wine/box64]\n$wine").joinToString("\n\n")
                com.logie.blizz.reports.BugReports.report(
                    app, "WoW Forever", "The game's program ended by itself: $program, code $code",
                    listOf("Program" to program, "Exit code" to code, "Launcher" to layout.clientExe()?.name, "Client build" to layout.clientBuild()?.toString()),
                    log = body.takeLast(7000),
                    attach = true, force = true,
                )
            }
        }
    }

    /**
     * Whether the session of the Play started at [since] is over: its game screen opened after that ([screenOpenedAt],
     * [com.logie.blizz.game.GameLog.startedAt]) and is no longer up ([screenAlive]). Before that the launcher's screen
     * coming back is no stop (Play is still preparing, or the game is only out of sight).
     */
    internal fun sessionOver(since: Long, screenOpenedAt: Long, screenAlive: Boolean): Boolean =
        since > 0 && screenOpenedAt >= since && !screenAlive

    /** What the person is told when the game's protection ended it ([ForeverCtl.isSecurityCrash]). */
    internal fun securityCrashText(launcher: Boolean, title: String): String =
        "World of Warcraft: Forever closed itself.\n\n" +
            "The game's own protection ended it (its crash file says \"Security Crash\"). " +
            (if (launcher) "That is what happens here about a minute after the Forever Launcher starts the game: " +
                "the game does not accept what the launcher does to it on this app's Windows layer. " else "") +
            "The installation is not damaged, and Repair or a reinstall won't change it" +
            (if (launcher) ": it takes a launcher version from its makers that the game accepts here." else ".") +
            "\n\n$title"

    private const val STOP_SEEN = "client.stop.seen"
    private const val STOP_PENDING = "client.stop.pending"
    /** Under this from the start, a stop is a crash (not a real play session): its log is shown in the app to copy. */
    private const val EARLY_STOP_MS = 120_000L

    /** The client as its own game ("wow-client"), run under Winlator with the `wow` controls. */
    private fun launchEntry(client: File, exe: File) = LibraryEntry(
        gameId = GAME_ID,
        title = "World of Warcraft: Forever",
        products = listOf("WOW"),
        clientVersion = "forever",
        installPath = client.path,
        executable = exe.relativeTo(client).path,
        runtime = LibraryEntry.RUNTIME_WINLATOR,
        arguments = "",
        stage = Stage.IMPORTED_UNTESTED,
        saveLocation = null,
        controlProfile = PROFILE,
    )
}
