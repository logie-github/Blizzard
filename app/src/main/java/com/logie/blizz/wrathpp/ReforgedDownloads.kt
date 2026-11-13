package com.logie.blizz.wrathpp

import android.content.Context
import com.logie.blizz.importer.ImportService
import com.logie.blizz.wow.WowLayout
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import java.io.File

/**
 * Project Reforged's downloads for Wrath++ ([Reforged.sync]) in the background: started when a switch is turned on on
 * Wrath++'s settings page and at every Wrath++ Play, kept going with the import notification ([ImportService]), never on a
 * metered connection (mobile data) unless the page's button says so once. What it does is in [state] for the page.
 * Play never waits for it: what finished goes in at the next Play.
 */
object ReforgedDownloads {
    data class State(
        val running: Boolean = false,
        val text: String = "",
        val done: Long = 0,
        val total: Long = 0,
        val lines: List<String> = emptyList(),
    )

    private val _state = MutableStateFlow(State())
    val state: StateFlow<State> = _state

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    @Volatile private var job: Job? = null
    @Volatile private var cancel = false
    @Volatile private var again = false

    private fun metered(context: Context): Boolean = runCatching {
        context.getSystemService(android.net.ConnectivityManager::class.java).isActiveNetworkMetered
    }.getOrDefault(false)

    /** Wrath++'s copy of the game's `Data`, or null while Wrath++ hasn't been played once (it is made by its first Play). */
    fun data(context: Context): File? {
        val client = WowLayout.of(context).wrathppClient
        return File(client, "Data").takeIf { WrathppClient.isMade(client) && it.isDirectory }
    }

    /** Starts (or restarts, after the choice changed) the downloads. [anyNetwork]: also on mobile data, this once. */
    @Synchronized
    fun start(context: Context, anyNetwork: Boolean = false) {
        val app = context.applicationContext
        if (job?.isActive == true) { again = true; cancel = true; return }
        val data = data(app)
        val options = Reforged.chosen(app.filesDir)
        if (data == null || options.isEmpty()) {
            _state.value = State(lines = if (data == null && options.isNotEmpty()) listOf("Play Wrath++ once first: it makes the game copy these go into.") else emptyList())
            return
        }
        if (Reforged.remaining(data, options) == 0L) {
            // all here: still asked once for a newer version, which costs a few requests
        } else if (!anyNetwork && metered(app)) {
            _state.value = State(lines = listOf("Waiting for Wi-Fi (this phone is on mobile data)."))
            return
        }
        cancel = false
        again = false
        job = scope.launch {
            ImportService.start(app)
            var notified = 0L
            try {
                _state.value = State(running = true, text = "Project Reforged: asking the project's server")
                val lines = Reforged.sync(data, options, Reforged.Http { cancel }, cancelled = { cancel }) { p ->
                    _state.value = State(true, p.text, p.done, p.total)
                    val now = System.currentTimeMillis()
                    if (now - notified >= 1000) {
                        notified = now
                        ImportService.update(app, com.logie.blizz.importer.Progress(com.logie.blizz.importer.Stage.DOWNLOADING,
                            "${p.text}: ${p.done shr 20} / ${p.total shr 20} MB", p.done, p.total))
                    }
                }
                _state.value = State(lines = lines)
            } catch (e: Reforged.Cancelled) {
                _state.value = State(lines = listOf("Stopped; it goes on from where it was."))
            } catch (e: Exception) {
                _state.value = State(lines = listOf("Stopped: ${e.message ?: e.javaClass.simpleName}. It goes on from where it was at the next Play."))
            } finally {
                ImportService.stop(app)
                job = null
                if (again) start(app, anyNetwork)
            }
        }
    }

    /** Stops the downloads; what came is kept and goes on at the next start. */
    fun stop() {
        again = false
        cancel = true
    }
}
