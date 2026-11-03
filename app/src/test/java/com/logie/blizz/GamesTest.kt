package com.logie.blizz

import org.junit.Assert.assertEquals
import org.junit.Test

class GamesTest {
    @Test fun shelfIsAlphabetical() {
        assertEquals(
            listOf(
                "Diablo", "Diablo II", "StarCraft", "StarCraft II",
                "Warcraft: Orcs & Humans", "Warcraft II: Tides of Darkness",
                "Warcraft III: Reign of Chaos", "Warcraft III: The Frozen Throne", "World of Warcraft",
            ),
            Games.all.map { it.fullTitle },
        )
    }

    @Test fun idsAreUnique() {
        assertEquals(Games.all.size, Games.all.map { it.id }.toSet().size)
    }
}
