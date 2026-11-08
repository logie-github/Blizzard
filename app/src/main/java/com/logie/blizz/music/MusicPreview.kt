package com.logie.blizz.music

import android.content.Context
import android.media.AudioAttributes
import android.media.MediaPlayer
import android.net.Uri
import android.os.Handler
import android.os.Looper
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/**
 * The music picker's preview: one song at a time, streamed from khinsider ([Khinsider.audioUrl] finds its file), with what is playing,
 * where it is and whether it's loading in [state]. The launcher's own music waits while a preview plays ([MusicPlayer.previewing]).
 */
object MusicPreview {
    data class State(
        /** The song page being previewed (its identity), or null when nothing is. */
        val pageUrl: String? = null,
        val title: String = "",
        val album: String = "",
        val cover: String? = null,
        val loading: Boolean = false,
        val playing: Boolean = false,
        val positionMs: Int = 0,
        val durationMs: Int = 0,
        val error: String? = null,
    )

    private val _state = MutableStateFlow(State())
    val state: StateFlow<State> = _state
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)
    private val main = Handler(Looper.getMainLooper())
    private var player: MediaPlayer? = null
    private var job: Job? = null
    private var ticker: Job? = null

    /** Plays [pageUrl]'s song, or pauses/resumes it when it is the one already there. */
    fun toggle(context: Context, pageUrl: String, title: String, album: String, cover: String?) {
        val now = _state.value
        if (now.pageUrl == pageUrl && !now.loading && player != null) {
            runCatching { if (player!!.isPlaying) { player!!.pause(); _state.value = now.copy(playing = false) } else { player!!.start(); _state.value = now.copy(playing = true); tick() } }
            return
        }
        start(context, pageUrl, title, album, cover)
    }

    private fun start(context: Context, pageUrl: String, title: String, album: String, cover: String?) {
        release()
        MusicPlayer.previewing(true)
        _state.value = State(pageUrl, title, album, cover, loading = true)
        job = scope.launch {
            val url = try { withContext(Dispatchers.IO) { Khinsider.audioUrl(pageUrl) } } catch (e: Exception) {
                if (e is kotlinx.coroutines.CancellationException) throw e
                _state.value = _state.value.copy(loading = false, error = e.message ?: "Couldn't find that song.")
                return@launch
            }
            val p = MediaPlayer()
            player = p
            runCatching {
                p.setAudioAttributes(AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_MEDIA).setContentType(AudioAttributes.CONTENT_TYPE_MUSIC).build())
                p.setDataSource(context.applicationContext, Uri.parse(url), mapOf("User-Agent" to Khinsider.AGENT))
                p.setOnPreparedListener { mp ->
                    if (player !== mp) return@setOnPreparedListener
                    mp.start()
                    _state.value = _state.value.copy(loading = false, playing = true, durationMs = mp.duration.coerceAtLeast(0))
                    tick()
                }
                p.setOnCompletionListener { _state.value = _state.value.copy(playing = false, positionMs = 0) }
                p.setOnErrorListener { _, _, _ -> _state.value = _state.value.copy(loading = false, playing = false, error = "That song wouldn't play."); true }
                p.prepareAsync()
            }.onFailure { _state.value = _state.value.copy(loading = false, error = "That song wouldn't play.") }
        }
    }

    private fun tick() {
        ticker?.cancel()
        ticker = scope.launch {
            while (isActive) {
                val p = player ?: break
                val playing = runCatching { p.isPlaying }.getOrDefault(false)
                if (playing) _state.value = _state.value.copy(positionMs = runCatching { p.currentPosition }.getOrDefault(0))
                delay(500)
                if (!playing && !_state.value.playing) break
            }
        }
    }

    /** Stops the preview and lets the launcher's music go on. */
    fun stop() {
        release()
        _state.value = State()
        MusicPlayer.previewing(false)
    }

    private fun release() {
        job?.cancel(); ticker?.cancel()
        player?.let { p -> player = null; runCatching { p.stop() }; runCatching { p.release() } }
    }
}
