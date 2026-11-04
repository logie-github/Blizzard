package com.logie.blizz.d2r

import com.logie.blizz.Games
import com.logie.blizz.importer.SwitchPackages
import com.logie.blizz.music.MusicCatalog
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class D2rTest {
    @Test fun resurrectedIsASecondVersionOfDiabloII() {
        val d2 = Games.all.single { it.id == "diablo2" }
        assertEquals(listOf(D2r.GAME_ID), d2.variants.map { it.id })
        assertEquals("Diablo II: Resurrected", d2.variants.single().fullTitle)
        assertEquals("diablo2", MusicCatalog.keyFor(D2r.GAME_ID))
    }

    @Test fun theModuleKeepsLibrariesCodeAndAssetsOfTheApk() {
        assertTrue(D2r.wanted("lib/arm64-v8a/libdm.so"))
        assertTrue(D2r.wanted("classes.dex"))
        assertTrue(D2r.wanted("classes2.dex"))
        assertTrue(D2r.wanted("assets/x/y.png"))
        assertFalse(D2r.wanted("lib/x86_64/libdm.so"))
        assertFalse(D2r.wanted("AndroidManifest.xml"))
    }

    private fun ticket(sigType: Int, base: Int, kind: Int): ByteArray {
        val t = ByteArray(base + 0x200)
        for (i in 0 until 4) t[i] = ((sigType shr (8 * i)) and 0xff).toByte()
        t[base + 0x141] = kind.toByte()
        for (i in 0 until 16) { t[base + 0x40 + i] = (0x10 + i).toByte(); t[base + 0x160 + i] = (0xa0 + i).toByte() }
        return t
    }

    @Test fun aCommonTicketGivesItsTitleKeyAndAPersonalizedOneDoesNot() {
        val common = ticket(0x00010001, 0x140, 0)
        val key = SwitchPackages.titleKey(common)!!
        assertEquals("a0a1a2a3a4a5a6a7a8a9aaabacadaeaf", key.rightsId)
        assertEquals("101112131415161718191a1b1c1d1e1f", key.key)
        assertEquals("a0a1a2a3a4a5a6a7a8a9aaabacadaeaf = 101112131415161718191a1b1c1d1e1f", SwitchPackages.titleKeysLine(key))
        val personalized = ticket(0x00010003, 0x240, 1)
        assertNull(SwitchPackages.titleKey(personalized))
        assertEquals(SwitchPackages.TicketKind.PERSONALIZED, SwitchPackages.ticketKind(personalized))
        assertEquals(SwitchPackages.TicketKind.UNKNOWN, SwitchPackages.ticketKind(ByteArray(8)))
        assertNotNull(SwitchPackages.titleKey(ticket(0x00010002, 0x80, 0)))
    }

    @Test fun baseAndUpdateAreToldApartByWhatHactoolSays() {
        val base = "Content Type:                       Program\nTitle ID:                           0100726014352000\nSection 1:\n    Type: RomFS\n"
        val update = base + "    Patch: BKTR\n"
        assertEquals(SwitchPackages.Content.BASE, SwitchPackages.classify(base))
        assertEquals(SwitchPackages.Content.UPDATE, SwitchPackages.classify(update))
        assertEquals(SwitchPackages.Content.OTHER, SwitchPackages.classify(base.replace("Program", "Meta")))
        assertEquals(SwitchPackages.Content.OTHER, SwitchPackages.classify(base.replace("0100726014352000", "0100000000000000")))
    }

    @Test fun onlyWhatTheGameReadsIsKept() {
        assertTrue(SwitchPackages.keep("00-00000001.data"))
        assertTrue(SwitchPackages.keep("17-00000002.data.holes"))
        assertTrue(SwitchPackages.keep(".build.config"))
        assertTrue(SwitchPackages.keep("build_manifest.psv"))
        assertFalse(SwitchPackages.keep("06-00000001.data"))
        assertEquals(18, SwitchPackages.ARCHIVES.size)
    }
}
