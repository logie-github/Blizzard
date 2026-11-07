package com.logie.blizz.wowaddons

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class AddonRecordsTest {
    private val questie = AddonRecord("questie", "Questie", "9.9.6-335", "Oct 12, 2026", "https://x/logo.png", listOf("Questie-335"), 1L)
    private val postal = AddonRecord("postal", "Postal\twith a tab", null, "Jun 1, 2026", null, listOf("Postal", "Ace3"), 2L)
    private val bagnon = AddonRecord("bagnon", "Bagnon", "2.13", null, null, listOf("Bagnon", "Bagnon_Config", "ace3"), 3L)

    @Test
    fun roundTrip() {
        val back = AddonRecords.parse(AddonRecords.format(listOf(questie, postal)))
        assertEquals(listOf(questie, postal.copy(title = "Postal with a tab")), back)
        assertEquals(emptyList(), AddonRecords.parse(""))
        assertEquals(emptyList(), AddonRecords.parse("warperia-addons 1\nbroken line\n"))
    }

    @Test
    fun putReplacesTheOlderInstall() {
        val newer = questie.copy(version = "9.9.7-335", installedAt = 9L)
        assertEquals(listOf(postal, newer), AddonRecords.put(listOf(questie, postal), newer))
    }

    @Test
    fun outdatedWhenTheVersionOrTheDateMoved() {
        assertFalse(AddonRecords.isOutdated(questie, "9.9.6-335", "Oct 12, 2026"))
        assertTrue(AddonRecords.isOutdated(questie, "9.9.7-335", "Oct 12, 2026"))
        assertTrue(AddonRecords.isOutdated(questie, "9.9.6-335", "Oct 20, 2026"))
        // What the site doesn't say can't be compared.
        assertFalse(AddonRecords.isOutdated(questie, null, null))
        assertFalse(AddonRecords.isOutdated(postal, "1.0", "Jun 1, 2026"))
    }

    @Test
    fun sharedFoldersStay() {
        val all = listOf(questie, postal, bagnon)
        assertEquals(listOf("Postal"), AddonRecords.ownFolders(postal, all))
        assertEquals(listOf("Bagnon", "Bagnon_Config"), AddonRecords.ownFolders(bagnon, all))
        assertEquals(listOf("Questie-335"), AddonRecords.ownFolders(questie, all))
    }
}
