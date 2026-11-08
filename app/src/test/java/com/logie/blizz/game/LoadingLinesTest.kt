package com.logie.blizz.game

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import kotlin.random.Random

class LoadingLinesTest {
    @Before fun fresh() = LoadingLines.reset()

    @Test fun eachGameHasItsOwnLines() {
        assertEquals(17, LoadingLines.warcraft.size)
        assertEquals(50, LoadingLines.diablo.size)
        assertEquals(70, LoadingLines.starcraft.size)
        for (lines in listOf(LoadingLines.warcraft, LoadingLines.diablo, LoadingLines.starcraft)) {
            assertEquals(lines.size, lines.toSet().size)
            assertTrue(lines.all { it.isNotBlank() })
        }
        assertEquals(LoadingLines.diablo, LoadingLines.forGame("diablo"))
        assertEquals(LoadingLines.diablo, LoadingLines.forGame("diablo2_resurrected"))
        assertEquals(LoadingLines.starcraft, LoadingLines.forGame("starcraft"))
        assertEquals(LoadingLines.starcraft, LoadingLines.forGame("starcraft_remastered"))
        assertEquals(LoadingLines.warcraft, LoadingLines.forGame("wow_legion"))
        assertEquals(LoadingLines.warcraft, LoadingLines.forGame(null))
    }

    @Test fun noLineIsShownTwiceInOneLoad() {
        val random = Random(1)
        var now = 1_000L
        val shown = List(LoadingLines.diablo.size) { LoadingLines.next("diablo", random, now.also { now += 3_500 }) }
        assertEquals("every line once, none repeated", LoadingLines.diablo.toSet(), shown.toSet())
        assertEquals(shown.size, shown.toSet().size)
    }

    @Test fun onceEveryLineIsShownTheDeckIsDealtAgainWithoutRepeatingTheLastOne() {
        val random = Random(2)
        var now = 0L
        var last: String? = null
        repeat(5) {
            repeat(LoadingLines.warcraft.size) {
                val line = LoadingLines.next("wow", random, now.also { now += 3_500 })
                assertNotEquals(last, line)
                last = line
            }
        }
    }

    @Test fun anotherGameOrALongPauseBeginsANewLoad() {
        val random = Random(3)
        val first = LoadingLines.next("starcraft", random, 0L)
        // a pause longer than a load's gap: the used list is forgotten
        val seen = mutableSetOf(first)
        repeat(500) { seen += LoadingLines.next("starcraft", Random(it), 100_000L + it * LoadingLines.LOAD_GAP_MS * 2) }
        assertTrue(first in seen)
        // another game
        LoadingLines.next("diablo", random, 200_000_000L)
        assertTrue(LoadingLines.next("diablo", random, 200_003_500L) in LoadingLines.diablo)
    }
}
