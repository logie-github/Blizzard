package com.logie.blizz.music

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class MusicPlayerFadeTest {
    @Test fun fadesStartAndEndWhereTheyShouldAndNeverJump() {
        assertEquals(1500L, Crossfade.MS)
        assertEquals(0f, Crossfade.ease(0f, 1f, 0f), 0.0001f)
        assertEquals(1f, Crossfade.ease(0f, 1f, 1f), 0.0001f)
        assertEquals(1f, Crossfade.ease(1f, 0f, 0f), 0.0001f)
        assertEquals(0f, Crossfade.ease(1f, 0f, 1f), 0.0001f)
        var last = 0f
        for (i in 1..100) {
            val g = Crossfade.ease(0f, 1f, i / 100f)
            assertTrue(g >= last)
            assertTrue("no jump at step $i", g - last < 0.04f)
            last = g
        }
    }

    @Test fun twoSongsCrossingKeepTheirLoudness() {
        for (i in 0..100) {
            val a = i / 100f
            val power = Crossfade.ease(0f, 1f, a).let { it * it } + Crossfade.ease(1f, 0f, a).let { it * it }
            assertEquals(1f, power, 0.001f)
        }
    }

    @Test fun aFadeCanStartPartWay() {
        assertEquals(0.4f, Crossfade.ease(0.4f, 0f, 0f), 0.0001f)
        assertEquals(1f, Crossfade.ease(0.4f, 1f, 1f), 0.0001f)
    }
}
