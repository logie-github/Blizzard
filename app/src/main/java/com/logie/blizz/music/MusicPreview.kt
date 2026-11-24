package com.logie.blizz.music

import android.content.Context
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
    private var player: LauncherAudio? = null
    private var job: Job? = null
    private var ticker: Job? = null

    /** Plays [pageUrl]'s song, or pauses/resumes it when it is the one already there. */
    fun toggle(context: Context, pageUrl: String, title: String, album: String, cover: String?) {
        val now = _state.value
        val current = player
        if (now.pageUrl == pageUrl && !now.loading && current != null) {
            if (current.isPlaying) {
                current.pause()
                _state.value = now.copy(playing = false)
            } else {
                current.start()
                _state.value = now.copy(playing = true)
                tick()
            }
            return
        }
        start(context, pageUrl, title, album, cover)
    }

    private fun start(context: Context, pageUrl: String, title: String, album: String, cover: String?) {
        release()
        Khinsider.attach(context)
        MusicPlayer.previewing(true)
        _state.value = State(pageUrl, title, album, cover, loading = true)
        job = scope.launch {
            val url = try { Khinsider.audioUrl(pageUrl) } catch (e: Exception) {
                if (e is kotlinx.coroutines.CancellationException) throw e
                _state.value = _state.value.copy(loading = false, error = e.message ?: "Couldn't find that song.")
                MusicPlayer.previewing(false)
                return@launch
            }
            lateinit var audio: LauncherAudio
            audio = LauncherAudio(
                source = { it.setDataSource(url, mapOf("User-Agent" to Khinsider.AGENT, "Referer" to "https://downloads.khinsider.com/")) },
                prepared = {
                    main.post {
                        if (player === audio) {
                            audio.start()
                            _state.value = _state.value.copy(loading = false, playing = true, durationMs = audio.durationMs)
                            tick()
                        }
                    }
                },
                ended = {
                    main.post {
                        if (player === audio) _state.value = _state.value.copy(playing = false, positionMs = 0)
                    }
                },
                failed = {
                    main.post {
                        if (player === audio) {
                            release()
                            _state.value = _state.value.copy(loading = false, playing = false, error = "That song wouldn't play.")
                            MusicPlayer.previewing(false)
                        }
                    }
                },
            )
            audio.volume = 1f
            player = audio
            audio.prepare()
        }
    }

    private fun tick() {
        ticker?.cancel()
        ticker = scope.launch {
            while (isActive) {
                val p = player ?: break
                val playing = p.isPlaying
                if (playing) _state.value = _state.value.copy(positionMs = p.positionMs)
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
        player?.release()
        player = null
    }
}
