package com.logie.blizz.music

import android.content.Context
import android.media.AudioAttributes
import android.media.MediaPlayer
import android.os.Handler
import android.os.Looper
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import java.io.File

/**
 * Plays the music of whatever is selected, looped: the launcher's track on the shelf, a game's from
 * the moment its page is opened. It stops while the launcher is out of sight (a game running has
 * its own sound) and starts again when the launcher comes back. A track that isn't downloaded yet
 * is silence until [refresh] finds it.
 */
object MusicPlayer {
    private const val PREFS = "music"
    private val main = Handler(Looper.getMainLooper())
    private var player: MediaPlayer? = null
    private var playingKey: String? = null
    private var wanted: String = MusicCatalog.LAUNCHER
    private var foreground = false
    private var appContext: Context? = null

    private val _enabled = MutableStateFlow(true)
    val enabled: StateFlow<Boolean> = _enabled
    private val _volume = MutableStateFlow(0.6f)
    val volume: StateFlow<Float> = _volume

    fun load(context: Context) {
        appContext = context.applicationContext
        val p = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        _enabled.value = p.getBoolean("enabled", true)
        _volume.value = p.getFloat("volume", 0.6f)
    }

    fun setEnabled(context: Context, on: Boolean) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().putBoolean("enabled", on).apply()
        _enabled.value = on
        sync()
    }

    fun setVolume(context: Context, volume: Float) {
        val v = volume.coerceIn(0f, 1f)
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().putFloat("volume", v).apply()
        _volume.value = v
        player?.setVolume(v, v)
    }

    /** What should play now (see [MusicCatalog.keyFor]). */
    fun select(context: Context, key: String) {
        appContext = context.applicationContext
        wanted = key
        sync()
    }

    /** The launcher is on screen (true) or not. */
    fun foreground(context: Context, on: Boolean) {
        appContext = context.applicationContext
        foreground = on
        sync()
    }

    /** A download finished: a track that was missing may play now. */
    fun refresh() {
        main.post { sync() }
    }

    private fun sync() {
        val context = appContext ?: return
        val file = File(File(context.filesDir, "music"), "$wanted.mp3")
        if (!foreground || !_enabled.value || !MusicStore(file.parentFile!!).has(wanted)) {
            release()
            return
        }
        if (playingKey == wanted && player != null) return
        release()
        runCatching {
            val p = MediaPlayer()
            p.setAudioAttributes(AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_GAME).setContentType(AudioAttributes.CONTENT_TYPE_MUSIC).build())
            p.setDataSource(file.path)
            p.isLooping = true
            p.setVolume(0f, 0f)
            p.prepare()
            p.start()
            player = p
            playingKey = wanted
            fadeIn(p)
        }.onFailure { release() }
    }

    private fun fadeIn(p: MediaPlayer) {
        val steps = 12
        for (i in 1..steps) main.postDelayed({
            if (player === p) runCatching { val v = _volume.value * i / steps; p.setVolume(v, v) }
        }, i * 60L)
    }

    private fun release() {
        val p = player ?: return
        player = null
        playingKey = null
        runCatching { p.stop() }
        runCatching { p.release() }
    }
}
