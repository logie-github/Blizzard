package com.logie.blizz.wrathpp

import android.content.Context
import com.logie.blizz.importer.ImportService
import com.logie.blizz.wow.WowRealm
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

/**
 * The settings page's **Update now** ([WrathppSetup.refreshParts]): fetches the newer server, add-on, looks and creator art
 * on request. Play keeps what is on the phone ([WrathppParts]). Not while the realm runs (the server is replaced).
 */
object WrathppServerUpdate {
    data class State(val running: Boolean = false, val text: String = "", val fraction: Float? = null, val message: String? = null)

    private val _state = MutableStateFlow(State())
    val state: StateFlow<State> = _state
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    fun update(context: Context) {
        val app = context.applicationContext
        if (_state.value.running) return
        if (WowRealm.isRunning()) {
            _state.value = State(message = "Wrath++'s realm is running: close the game first, then update.")
            return
        }
        _state.value = State(running = true, text = "Asking for the newest downloads")
        scope.launch {
            ImportService.start(app)
            val message = try {
                WrathppSetup.refreshParts(app) { text, fraction -> _state.value = State(running = true, text = text, fraction = fraction?.takeIf { it.isFinite() }) }
            } catch (e: Exception) {
                "The update failed: ${e.message ?: e.javaClass.simpleName}. What was on the phone is kept."
            } finally {
                ImportService.stop(app)
            }
            _state.value = State(message = message)
        }
    }
}
