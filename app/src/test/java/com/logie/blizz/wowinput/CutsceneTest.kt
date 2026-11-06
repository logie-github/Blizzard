package com.logie.blizz.wowinput

import kotlin.test.Test
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class CutsceneTest {
    @Test
    fun aCinematicOrAMoviePlaysUntilItsEnd() {
        assertTrue(Cutscene.isPlaying("c 1000\n", 1030))
        assertTrue(Cutscene.isPlaying("m 1000", 1000 + 5 * 60))
        assertFalse(Cutscene.isPlaying("- 1100", 1101))
    }

    @Test
    fun notForeverWhenTheEndIsNeverSaid() {
        assertFalse(Cutscene.isPlaying("c 1000", 1000 + Cutscene.CINEMATIC_MAX_S + 1))
        assertFalse(Cutscene.isPlaying("m 1000", 1000 + Cutscene.MOVIE_MAX_S + 1))
    }

    @Test
    fun nothingKnownIsNoCutscene() {
        assertFalse(Cutscene.isPlaying(null, 1000))
        assertFalse(Cutscene.isPlaying("", 1000))
        assertFalse(Cutscene.isPlaying("c later", 1000))
        // A clock that went back doesn't count.
        assertFalse(Cutscene.isPlaying("c 2000", 1000))
    }
}
