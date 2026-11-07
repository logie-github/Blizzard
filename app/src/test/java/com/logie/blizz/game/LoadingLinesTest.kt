package com.logie.blizz.game

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class LoadingLinesTest {
    @Test fun theLinesAreTheUsersSeventeenAndNeverRepeatTwiceRunning() {
        assertEquals(17, LoadingLines.all.size)
        assertTrue(LoadingLines.all.all { it.endsWith("...") })
        var line = LoadingLines.next()
        repeat(200) { val n = LoadingLines.next(line); assertNotEquals(line, n); assertTrue(n in LoadingLines.all); line = n }
    }
}
