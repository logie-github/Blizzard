package com.logie.blizz

import org.junit.Assert.assertEquals
import org.junit.Test

class GamesTest {
    @Test fun shelfIsAlphabetical() {
        assertEquals(
            listOf(
                "Diablo", "Diablo II", "StarCraft", "StarCraft II",
                "Warcraft: Orcs & Humans", "Warcraft II: Tides of Darkness",
                "Warcraft III: Reign of Chaos", "World of Warcraft: Wrath+",
            ),
            Games.all.map { it.fullTitle },
        )
    }

    @Test fun idsAreUnique() {
        assertEquals(Games.all.size, Games.all.map { it.id }.toSet().size)
    }

    @Test fun warcraftThreeIsOneTileWithThreeModes() {
        val wc3 = Games.all.single { it.id == "warcraft3_roc" }
        assertEquals(listOf("warcraft3_tft", "warcraft3_warsmash"), wc3.variants.map { it.id })
        assertEquals("Warcraft III: The Frozen Throne", Games.find("warcraft3_tft")!!.fullTitle)
    }
}
