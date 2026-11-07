package com.logie.blizz.music

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class MusicPlayerFadeTest {
    @Test fun aCrossfadeTakesOneAndAHalfSecondsAndTheTwoSongsAddUpToTheVolume() {
        assertEquals(1500L, Crossfade.MS)
        assertEquals(0f, Crossfade.volume(0, 0.6f, out = false), 0.0001f)
        assertEquals(0.6f, Crossfade.volume(30, 0.6f, out = false), 0.0001f)
        assertEquals(0.6f, Crossfade.volume(0, 0.6f, out = true), 0.0001f)
        assertEquals(0f, Crossfade.volume(30, 0.6f, out = true), 0.0001f)
        for (step in 0..30) {
            val sum = Crossfade.volume(step, 0.6f, out = false) + Crossfade.volume(step, 0.6f, out = true)
            assertEquals(0.6f, sum, 0.0001f)
            assertTrue(Crossfade.volume(step, 1f, out = false) >= 0f)
        }
    }
}
