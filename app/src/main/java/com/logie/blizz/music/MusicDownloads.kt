package com.logie.blizz.music

import android.content.Context
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import java.io.File

/** Fetches the music that isn't on the phone: when the app first opens, and from the settings menu. */
object MusicDownloads {
    sealed interface State {
        data object Idle : State
        data class Running(val done: Int, val total: Int, val current: String) : State
        data class Finished(val failed: List<String>) : State
    }

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val _state = MutableStateFlow<State>(State.Idle)
    val state: StateFlow<State> = _state
    private var started = false

    fun store(context: Context) = MusicStore(File(context.applicationContext.filesDir, "music"))

    /** At app start: once per run, only what is missing. */
    fun startIfMissing(context: Context) {
        if (started) return
        started = true
        start(context)
    }

    /** Downloads every missing track, one at a time; each one that arrives can start playing at once. */
    fun start(context: Context) {
        if (_state.value is State.Running) return
        val store = store(context)
        val todo = store.missing()
        if (todo.isEmpty()) { _state.value = State.Finished(emptyList()); return }
        _state.value = State.Running(0, todo.size, todo.first().label)
        scope.launch {
            val failed = ArrayList<String>()
            todo.forEachIndexed { i, track ->
                _state.value = State.Running(i, todo.size, track.label)
                try {
                    store.download(track)
                    MusicPlayer.refresh()
                } catch (e: Exception) {
                    failed += "${track.label} (${e.message ?: e.javaClass.simpleName})"
                }
            }
            _state.value = State.Finished(failed)
        }
    }
}
