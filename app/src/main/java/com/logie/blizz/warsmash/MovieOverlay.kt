package com.logie.blizz.warsmash

import android.annotation.SuppressLint
import android.content.Context
import android.graphics.Color
import android.os.SystemClock
import android.util.Log
import android.util.TypedValue
import android.view.Gravity
import android.view.MotionEvent
import android.view.SurfaceHolder
import android.view.SurfaceView
import android.widget.FrameLayout
import android.widget.TextView
import java.io.File

/**
 * Warcraft III's movies over the engine, one after another, on black at their own shape, with the captions the game
 * shows over them where given: a tap skips the one playing, [skipAll] (Back) all of them. [onDone] runs on the main
 * thread once the last has ended. The engine waits underneath (its drawing and sound held by the activity meanwhile).
 */
@SuppressLint("ViewConstructor")
internal class MovieOverlay(context: Context, movies: List<Movie>, private val onDone: () -> Unit) : FrameLayout(context), SurfaceHolder.Callback {
    /** A movie's file and the text of its caption file, null where it is shown without. */
    data class Movie(val file: File, val captions: String?)

    private val queue = ArrayDeque(movies)
    private val surface = SurfaceView(context)
    private val caption = TextView(context)
    @Volatile private var handle = 0L
    private var thread: Thread? = null
    private var ready = false
    private var finished = false
    private var movieSize: IntArray? = null
    private var cues: List<WarsmashMovies.Cue> = emptyList()
    private var startedAt = 0L

    private val captionTick = object : Runnable {
        override fun run() {
            if (handle == 0L) return
            val now = (SystemClock.uptimeMillis() - startedAt) / 1000.0
            val text = WarsmashMovies.at(cues, now)?.text.orEmpty()
            if (caption.text.toString() != text) caption.text = text
            postDelayed(this, 100)
        }
    }

    init {
        setBackgroundColor(Color.BLACK)
        surface.setZOrderMediaOverlay(true)
        surface.holder.addCallback(this)
        addView(surface, LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT, Gravity.CENTER))
        // Over the black below the picture (the movies are far wider than the screen), white with a shadow as the game's.
        caption.setTextColor(Color.WHITE)
        caption.setShadowLayer(4f, 0f, 2f, Color.BLACK)
        caption.setTextSize(TypedValue.COMPLEX_UNIT_SP, 18f)
        caption.gravity = Gravity.CENTER_HORIZONTAL
        val pad = (16 * resources.displayMetrics.density).toInt()
        caption.setPadding(pad, 0, pad, pad * 2)
        addView(caption, LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT, Gravity.BOTTOM))
        isClickable = true
    }

    @SuppressLint("ClickableViewAccessibility")
    override fun onTouchEvent(event: MotionEvent): Boolean {
        if (event.actionMasked == MotionEvent.ACTION_UP) skipOne()
        return true
    }

    /** Stops the movie playing; the next one starts. */
    fun skipOne() {
        val h = handle
        if (h != 0L) MovieNative.stop(h)
    }

    /** Stops the movie playing and drops the rest. */
    fun skipAll() {
        queue.clear()
        skipOne()
    }

    override fun surfaceCreated(holder: SurfaceHolder) {
        ready = true
        if (thread == null) next()
    }

    override fun surfaceChanged(holder: SurfaceHolder, format: Int, width: Int, height: Int) = Unit

    /** The surface goes (the app left): the movies stop there, and the thread is waited for before the surface is let go. */
    override fun surfaceDestroyed(holder: SurfaceHolder) {
        ready = false
        skipAll()
        thread?.join(2000)
    }

    private fun next() {
        if (finished) return
        val movie = queue.removeFirstOrNull()
        if (movie == null) {
            finished = true
            caption.text = ""
            onDone()
            return
        }
        val h = try {
            MovieNative.open(movie.file.path)
        } catch (e: Exception) {
            Log.w(TAG, "${movie.file.name} didn't open: ${e.message}")
            next()
            return
        }
        handle = h
        fit(MovieNative.size(h))
        cues = movie.captions?.let(WarsmashMovies::cues).orEmpty()
        caption.text = ""
        startedAt = SystemClock.uptimeMillis()
        removeCallbacks(captionTick)
        if (cues.isNotEmpty()) post(captionTick)
        val holder = surface.holder
        thread = Thread({
            val result = runCatching { MovieNative.run(h, holder.surface) }.getOrDefault(-1)
            if (result < 0) Log.w(TAG, "${movie.file.name} stopped with $result")
            post {
                handle = 0L
                removeCallbacks(captionTick)
                MovieNative.close(h)
                thread = null
                if (ready) next() else if (!finished) {
                    finished = true
                    onDone()
                }
            }
        }, "wc3-movie").apply { start() }
    }

    /** The picture as large as the screen allows at its own shape, centred on black. */
    private fun fit(size: IntArray) {
        movieSize = size
        val w = width.takeIf { it > 0 } ?: resources.displayMetrics.widthPixels
        val h = height.takeIf { it > 0 } ?: resources.displayMetrics.heightPixels
        if (size[0] <= 0 || size[1] <= 0) return
        val scale = minOf(w.toFloat() / size[0], h.toFloat() / size[1])
        surface.layoutParams = LayoutParams((size[0] * scale).toInt(), (size[1] * scale).toInt(), Gravity.CENTER)
    }

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        movieSize?.let { fit(it) }
    }

    companion object {
        private const val TAG = "Wc3Movie"
    }
}
