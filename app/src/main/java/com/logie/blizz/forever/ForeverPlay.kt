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
        data class Preparing(val message: String, val progress: Float? = null) : State
        /** The Forever client isn't in the app yet: the launcher asks the user to pick its folder. */
        data object NeedsClient : State
        data class Failed(val message: String) : State
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
        if (_state.value is State.Failed || _state.value is State.NeedsClient) _state.value = State.Idle
    }

    fun play(context: Context) {
        if (_state.value is State.Preparing) return
        val app = context.applicationContext
        val (width, height) = WindowsRuntime.gameSize(context, GAME_ID, LaunchProfile.WOW)
        _state.value = State.Preparing("Preparing")
        scope.launch {
            try {
                val failure = run(app, width to height)
                _state.value = when (failure) {
                    null -> State.Idle
                    NEEDS_CLIENT -> State.NeedsClient
                    else -> State.Failed(failure)
                }
            } catch (e: CancellationException) {
                _state.value = State.Idle
                throw e
            } catch (e: Throwable) {
                _state.value = State.Failed(e.message ?: e.javaClass.simpleName)
            }
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

    private suspend fun run(context: Context, size: Pair<Int, Int>): String? {
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

        if (!layout.hasClient()) return NEEDS_CLIENT

        if (!layout.hasServerData()) {
            _state.value = State.Preparing("Preparing the game data (first time, several minutes)")
            withContext(Dispatchers.IO) {
                ForeverRealm.extractData(context, layout.client) { line -> _state.value = State.Preparing(line) }
            }
        }

        _state.value = State.Preparing("Starting the realm")
        val account = login(context)
        withContext(Dispatchers.IO) { ForeverRealm.start(context, layout.clientBuild(), account.name to account.password) }
        val status = ForeverRealm.status.first { it.phase == ForeverRealm.Phase.RUNNING || it.phase == ForeverRealm.Phase.FAILED || it.phase == ForeverRealm.Phase.STOPPED }
        when (status.phase) {
            ForeverRealm.Phase.RUNNING -> {}
            ForeverRealm.Phase.FAILED -> return status.error ?: "The realm didn't start (see logs in files/forever/logs)."
            else -> return "The realm stopped before it was ready."
        }

        _state.value = State.Preparing("Starting the game")
        val exe = layout.clientExe() ?: return NEEDS_CLIENT
        withContext(Dispatchers.Main) { WindowsRuntime.play(context, launchEntry(layout.client, exe), size) }
        return null
    }

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
