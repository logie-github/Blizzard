package com.logie.blizz.d2r

import com.logie.blizz.Games
import com.logie.blizz.game.LaunchOptions
import com.logie.blizz.importer.GameImportManager
import com.logie.blizz.music.MusicCatalog
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class D2rTest {
    @Test fun resurrectedIsASecondVersionOfDiabloII() {
        val d2 = Games.all.single { it.id == "diablo2" }
        assertEquals(listOf(D2r.GAME_ID), d2.variants.map { it.id })
        val r = d2.variants.single()
        assertEquals("Diablo II: Resurrected", r.fullTitle)
        assertEquals(D2r.PACKAGE, r.suggestedPackage)
        assertEquals(r, Games.find(D2r.GAME_ID))
    }

    @Test fun itIsPlayedInItsOwnAppNotImportedOrOptioned() {
        assertFalse(GameImportManager.importable(D2r.GAME_ID))
        assertFalse(LaunchOptions.hasOptions(D2r.GAME_ID))
        assertTrue(D2r.APK_URL.endsWith("/releases/latest/download/D2RMobile-android.apk"))
    }

    @Test fun itSharesDiabloIIsMusic() {
        assertEquals("diablo2", MusicCatalog.keyFor(D2r.GAME_ID))
    }
}
