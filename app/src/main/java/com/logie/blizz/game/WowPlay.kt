package com.logie.blizz.game

import android.content.Context
import com.logie.blizz.importer.LibraryEntry
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File

/** What [WowPlay] needs of the realm (the orchestrator implements it by delegating to `com.logie.blizz.wow.WowRealm`). */
interface RealmControl {
    enum class Phase { STOPPED, STARTING, UP, FAILED, NO_DATA }

    data class Status(val phase: Phase, val detail: String? = null, val progress: Float? = null, val error: String? = null)

    /** Starts the realm [realm] ("main" ChromieCraft, "remix" Wrath Remix) if it isn't running; returns at once. */
    fun start(context: Context, realm: String)

    val status: StateFlow<Status>

    /** Waits until the realm is up, has failed or stopped, or [timeoutMs] has passed; the status it ended on. */
    suspend fun awaitUp(timeoutMs: Long): Status

    /** The realm the person chose ("main" or "remix"). */
    fun chosenRealm(context: Context): String
}

/**
 * Play for World of Warcraft: the realm is started, the imported 3.3.5a client is pointed at it
 * ([WowClientSetup]), and once it is up the client starts on Blizzard's own Winlator
 * ([WindowsRuntime.play]) with the `wow` touch controls. The wait for the realm (minutes the first
 * time) shows as [state]; the runtime's own steps show as [WindowsRuntime.state] after it.
 */
object WowPlay {
    sealed interface State {
        data object Idle : State
        data class Preparing(val message: String, val progress: Float? = null) : State
        data class Failed(val message: String) : State
    }

    const val GAME_ID = "wow-client"
    const val PROFILE = "wow"

    /** How long the realm may take to come up (its databases load for minutes). */
    const val REALM_TIMEOUT_MS = 15 * 60_000L

    /** The realm's control, set once by the app (the orchestrator). */
    @Volatile var realm: RealmControl? = null

    private val _state = MutableStateFlow<State>(State.Idle)
    val state: StateFlow<State> = _state
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)

    fun dismiss() {
        if (_state.value is State.Failed) _state.value = State.Idle
    }

    /** [entry] is the imported World of Warcraft ([com.logie.blizz.importer.WowImporter]); its `installPath` is `games/wow`. */
    fun play(context: Context, entry: LibraryEntry) {
        if (_state.value is State.Preparing) return
        val app = context.applicationContext
        val control = realm
        if (control == null) {
            _state.value = State.Failed("The realm isn't available in this build.")
            return
        }
        // The same size as the X screen WindowsRuntime makes for the client (its gxResolution and the screen must agree).
        val (width, height) = WindowsRuntime.gameSize(context, GAME_ID, LaunchProfile.WOW)
        _state.value = State.Preparing("Starting the realm")
        scope.launch {
            try {
                val environment = Environment(
                    root = File(entry.installPath), realm = control, size = width to height, title = entry.title,
                    start = { control.start(app, it) }, chosenRealm = { control.chosenRealm(app) },
                    launch = { WindowsRuntime.play(app, it, width to height) }, report = { _state.value = it },
                )
                val failure = prepare(environment)
                _state.value = if (failure == null) State.Idle else State.Failed(failure)
            } catch (e: CancellationException) {
                _state.value = State.Idle
                throw e
            } catch (e: Exception) {
                _state.value = State.Failed(e.message ?: e.javaClass.simpleName)
            }
        }
    }

    /** Everything [prepare] works on, apart from Android (so it is tested with a fake realm). */
    class Environment(
        /** The imported game: `games/wow` (holds `files/` and `.export/`). */
        val root: File,
        val realm: RealmControl,
        val size: Pair<Int, Int>,
        val title: String = "World of Warcraft",
        val start: (String) -> Unit,
        val chosenRealm: () -> String,
        val launch: (LibraryEntry) -> Unit,
        val report: (State) -> Unit,
        val timeoutMs: Long = REALM_TIMEOUT_MS,
    )

    fun clientFolder(root: File) = File(root, "files/client")

    /**
     * Starts the realm, points the client at it, waits for the realm, then starts the client.
     * Returns null when the client was started, else what to tell the person.
     */
    suspend fun prepare(env: Environment): String? {
        val client = clientFolder(env.root)
        if (!WowClientSetup.hasClient(client)) {
            return "The game's files aren't there (files/client with Wow.exe). Export again from the World of Warcraft app and import it."
        }
        val key = env.chosenRealm()
        env.report(State.Preparing("Starting ${WowClientSetup.realmName(key)}"))
        env.start(key)

        val prefs = File(env.root, ".export/prefs")
        val account = WowClientSetup.savedAccount(runCatching { File(prefs, "login.json").readText() }.getOrNull())
        val mods = runCatching { File(prefs, "mods.json").readText() }.getOrNull()
        withContext(Dispatchers.IO) {
            WowClientSetup.apply(client, File(env.root, "files"), env.size.first, env.size.second, key, account)
        }

        val watcher = CoroutineScope(Dispatchers.Unconfined).launch {
            env.realm.status.collect { s ->
                if (s.phase == RealmControl.Phase.STARTING) {
                    env.report(State.Preparing(s.detail ?: "Starting ${WowClientSetup.realmName(key)}", s.progress))
                }
            }
        }
        val up = try {
            env.realm.awaitUp(env.timeoutMs)
        } finally {
            watcher.cancel()
        }
        when (up.phase) {
            RealmControl.Phase.UP -> Unit
            RealmControl.Phase.FAILED -> return up.error ?: "The realm didn't start."
            RealmControl.Phase.STOPPED -> return "The realm was stopped."
            RealmControl.Phase.NO_DATA -> return up.error ?: "The realm has no data (import the World of Warcraft export first)."
            RealmControl.Phase.STARTING -> return "The realm is still loading after ${env.timeoutMs / 60_000} minutes. Try again in a moment."
        }

        env.report(State.Preparing("Starting the game"))
        val exe = withContext(Dispatchers.IO) { WowClientSetup.executable(client, mods) }
        env.launch(launchEntry(client, exe, env.title))
        return null
    }

    /** The entry [WindowsRuntime.play] starts: the client as its own game ("wow-client"), with the `wow` controls. */
    fun launchEntry(client: File, executable: String = WowClientSetup.EXE, title: String = "World of Warcraft") = LibraryEntry(
        gameId = GAME_ID,
        title = title,
        products = listOf("WOW"),
        clientVersion = "3.3.5a",
        installPath = client.path,
        executable = executable,
        runtime = LibraryEntry.RUNTIME_WINLATOR,
        arguments = "",
        stage = com.logie.blizz.importer.Stage.IMPORTED_UNTESTED,
        saveLocation = null,
        controlProfile = PROFILE,
    )
}
