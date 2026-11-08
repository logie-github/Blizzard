package com.logie.blizz.forever

import android.content.Context
import com.logie.blizz.game.LaunchProfile
import com.logie.blizz.game.WindowsRuntime
import com.logie.blizz.importer.LibraryEntry
import com.logie.blizz.importer.Stage
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
 * 1. the server package is downloaded the first time ([ForeverServerPackage]);
 * 2. the current Forever client must be present ([ForeverLayout.client]); the launcher prompts for it otherwise;
 * 3. the server's map data is made from the client the first time ([ForeverRealm.extractData]);
 * 4. the realm is started ([ForeverRealm]) and waited for;
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
        /** The Forever client isn't in the app yet: the launcher asks the user to add it. */
        data object NeedsClient : State
        data class Failed(val message: String) : State
    }

    /** The client's touch controls id (the same `wow` gestures as the other WoW clients). */
    private const val GAME_ID = "wow-client"
    private const val PROFILE = "wow"

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

    private const val NEEDS_CLIENT = "\u0000needs-client"

    private suspend fun run(context: Context, size: Pair<Int, Int>): String? {
        val layout = ForeverLayout.of(context)

        if (!ForeverServerPackage.installed(context)) {
            _state.value = State.Preparing("Downloading the realm server", 0f)
            withContext(Dispatchers.IO) {
                ForeverServerPackage.install(context) { done, total ->
                    _state.value = State.Preparing("Downloading the realm server", if (total > 0) done.toFloat() / total else null)
                }
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
        withContext(Dispatchers.IO) { ForeverRealm.start(context) }
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
