package com.logie.blizz.ps1

internal object Ps1Core {
    init {
        System.loadLibrary("blizz_ps1")
    }

    external fun open(image: String, saves: String): Double
    external fun step(buttons: Int, frame: IntArray): Int
    external fun readAudio(samples: ShortArray): Int
    external fun close()
}
