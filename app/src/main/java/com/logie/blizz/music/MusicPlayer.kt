package com.logie.blizz.music

import android.content.Context
import android.media.AudioAttributes
import android.media.MediaPlayer
import android.os.Handler
import android.os.HandlerThread
import android.os.Looper
import android.os.SystemClock
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
    /** A song paused while the launcher is away is kept this long, then let go. */
    private const val KEEP_PAUSED_MS = 10 * 60_000L
    /** Its own thread: the launcher's drawing and image loading never hold up a fade (they made the fades jump). */
    private val worker: Handler by lazy { Handler(HandlerThread("music").apply { start() }.looper) }

    /** One song: its player, its gain now, and the fade it is in (from [fromGain] to [toGain] over [fadeMs], started at [fadeStart]). */
    private class Voice(val player: MediaPlayer, val key: String) {
        var gain = 0f
        var fromGain = 0f
        var toGain = 0f
        var fadeStart = 0L
        var fadeMs = 1L
        /** At the end of a fade to silence: pause (kept, to go on from there) or release. */
        var pauseAtEnd = false
        var releaseAtEnd = false
        var paused = false
        var pausedAt = 0L
    }

    private var current: Voice? = null
    private val voices = mutableListOf<Voice>()
    private var ticking = false

    private var wanted: String = MusicCatalog.LAUNCHER
    private var wantedGame: String? = null
    private var foreground = false
    /** A preview in the music picker is playing: the background music waits (fades out, paused) and goes on after. */
    private var previewing = false
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
        worker.post { sync() }
    }

    fun setVolume(context: Context, volume: Float) {
        val v = volume.coerceIn(0f, 1f)
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().putFloat("volume", v).apply()
        _volume.value = v
        worker.post { voices.forEach { apply(it) } }
    }

    /** What should play now (see [MusicCatalog.keyFor]). */
    fun select(context: Context, key: String, gameId: String? = null) {
        val app = context.applicationContext
        worker.post { appContext = app; wanted = key; wantedGame = gameId; sync() }
    }

    /** The launcher is on screen (true) or not. */
    fun foreground(context: Context, on: Boolean) {
        val app = context.applicationContext
        worker.post { appContext = app; foreground = on; sync() }
    }

    /** The music picker's preview starts ([on]) or ends: the background music stands aside meanwhile. */
    fun previewing(on: Boolean) {
        worker.post { previewing = on; sync() }
    }

    /** A download finished: a track that was missing may play now. */
    fun refresh() {
        worker.post { sync() }
    }

    private fun sync() {
        val context = appContext ?: return
        // The person's own song for this version of the game, else the downloaded track.
        val custom = wantedGame?.let { MusicCustom.file(context, it) }
        val file = custom ?: File(File(context.filesDir, "music"), "$wanted.mp3")
        val id = if (custom != null) "custom:$wantedGame:${custom.lastModified()}" else wanted
        val playable = _enabled.value && (custom != null || MusicStore(file.parentFile!!).has(wanted))
        val now = current
        if (!playable) {
            current = null
            now?.let { fadeTo(it, 0f, Crossfade.MS, release = true) }
            return
        }
        if (!foreground || previewing) {
            // Away: the song fades and pauses where it is, to go on from there when the launcher is back.
            now?.let { fadeTo(it, 0f, Crossfade.MS, pause = true) }
            return
        }
        if (now != null && now.key == id) {
            if (now.paused) runCatching { now.player.start() }.onFailure { current = null; drop(now); return }
            now.paused = false
            fadeTo(now, 1f, Crossfade.MS)
            return
        }
        // Another song: the old one fades out while the new one fades in, over the same time.
        now?.let { fadeTo(it, 0f, Crossfade.MS, release = true) }
        current = null
        val voice = runCatching {
            val p = MediaPlayer()
            runCatching {
                p.setAudioAttributes(AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_GAME).setContentType(AudioAttributes.CONTENT_TYPE_MUSIC).build())
                p.setDataSource(file.path)
                p.isLooping = true
                p.setVolume(0f, 0f)
                p.prepare()
                p.start()
            }.onFailure { runCatching { p.release() } }.getOrThrow()
            Voice(p, id)
        }.getOrNull() ?: return
        voices += voice
        current = voice
        // From silence (the app opening, the launcher coming back) a little longer than a crossfade.
        fadeTo(voice, 1f, if (now == null) Crossfade.FIRST_MS else Crossfade.MS)
    }

    private fun fadeTo(v: Voice, to: Float, ms: Long, pause: Boolean = false, release: Boolean = false) {
        // Already silent and paused: nothing to fade.
        if (v.paused) { if (release) drop(v); return }
        v.fromGain = v.gain
        v.toGain = to
        v.fadeStart = SystemClock.uptimeMillis()
        v.fadeMs = maxOf(1L, ms)
        v.pauseAtEnd = pause
        v.releaseAtEnd = release
        if (!ticking) { ticking = true; worker.post(tick) }
    }

    private val tick = object : Runnable {
        override fun run() {
            val t = SystemClock.uptimeMillis()
            var busy = false
            for (v in voices.toList()) {
                if (v.paused) {
                    if (t - v.pausedAt > KEEP_PAUSED_MS) { if (v === current) current = null; drop(v) } else busy = true
                    continue
                }
                val along = ((t - v.fadeStart).toFloat() / v.fadeMs).coerceIn(0f, 1f)
                v.gain = Crossfade.ease(v.fromGain, v.toGain, along)
                apply(v)
                if (along < 1f) { busy = true; continue }
                when {
                    v.releaseAtEnd -> drop(v)
                    v.pauseAtEnd -> { runCatching { v.player.pause() }; v.paused = true; v.pausedAt = t; busy = true }
                }
            }
            if (busy) worker.postDelayed(this, if (voices.any { !it.paused && it.gain != it.toGain }) 16L else 30_000L) else ticking = false
        }
    }

    private fun apply(v: Voice) {
        val level = v.gain * _volume.value
        runCatching { v.player.setVolume(level, level) }
    }

    private fun drop(v: Voice) {
        voices -= v
        runCatching { v.player.stop() }
        runCatching { v.player.release() }
    }
}

/** The arithmetic of a fade: plain Kotlin, unit-tested. */
object Crossfade {
    const val MS = 1500L
    /** Starting from silence. */
    const val FIRST_MS = 2200L

    /**
     * The gain [along] (0 to 1) a fade from [from] to [to]. Ears hear loudness, not amplitude: an equal-power curve
     * (a quarter sine) eased at both ends, so a song coming in has no jump at its start and one going out no cliff at its end,
     * and two songs crossing keep the same loudness together.
     */
    fun ease(from: Float, to: Float, along: Float): Float {
        val a = along.coerceIn(0f, 1f)
        val smooth = a * a * (3f - 2f * a)
        return if (to >= from) from + (to - from) * kotlin.math.sin(smooth * Math.PI.toFloat() / 2f)
        else to + (from - to) * kotlin.math.cos(smooth * Math.PI.toFloat() / 2f)
    }
}
