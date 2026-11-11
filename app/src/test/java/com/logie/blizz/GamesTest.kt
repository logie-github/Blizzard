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

    @Test fun warcraftThreeIsOneTileWithItsTwoGames() {
        val wc3 = Games.all.single { it.id == "warcraft3_roc" }
        // Both play in Warsmash: the separate Warsmash mode is gone (Warcraft3WarsmashImporter).
        assertEquals(listOf("warcraft3_tft"), wc3.variants.map { it.id })
        assertEquals(null, Games.find("warcraft3_warsmash"))
        assertEquals("Warcraft III: The Frozen Throne", Games.find("warcraft3_tft")!!.fullTitle)
    }
}
