package com.logie.blizz.warsmash

import android.view.Surface

/** The movie player built from movie/ (libwc3movie.so: FFmpeg's AVI, MPEG-4 and MP3 decoders; AAudio for the sound). */
internal object MovieNative {
    init {
        System.loadLibrary("wc3movie")
    }

    /** Opens a movie file; throws java.io.IOException with the reason when it can't be played. */
    @JvmStatic external fun open(path: String): Long

    /** The picture's width and height. */
    @JvmStatic external fun size(handle: Long): IntArray

    /** Plays the movie on [surface] on the calling thread: 0 when it ended, 1 when stopped, below 0 when it couldn't go on. */
    @JvmStatic external fun run(handle: Long, surface: Surface): Int

    /** Asks the movie playing to stop (a tap, Back); [run] returns soon after. */
    @JvmStatic external fun stop(handle: Long)

    @JvmStatic external fun close(handle: Long)
}
