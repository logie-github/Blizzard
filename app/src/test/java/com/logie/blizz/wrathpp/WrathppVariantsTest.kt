package com.logie.blizz.wrathpp

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class WrathppVariantsTest {
    private val upright = WrathppVariants.Variant(2, 0, 1500, 2, "Character\\Orc\\Male\\OrcMaleV2.m2")

    @Test fun theVariantsAreReadFromThePartsTable() {
        val table = "# header\nS\t2\t0\t1\t1210\tx\nV\t2\t0\t1500\t2\tCharacter\\Orc\\Male\\OrcMaleV2.m2\nV\tbad\n"
        assertEquals(listOf(upright), WrathppVariants.parse(table))
    }

    @Test fun theNumberingIsTheRealmsOwn() {
        assertEquals(44001, WrathppVariants.displayId(upright))             // wrathpp_appearance.h: kVariantDisplayBase + (category - 1500) * 16 + the option's value
        assertEquals(44000 + 3 * 16 + 2, WrathppVariants.displayId(WrathppVariants.Variant(5, 0, 1503, 3, "x.m2")))
    }

    @Test fun theRowsAreMadeOfTheRacesOwnAndPutInAgain() {
        val displays = WrathppUndead.Dbc(WrathppBody.DISPLAY_KINDS, mutableListOf(
            arrayOf<Any>(51894, 6838, 0, 0, 1, 1, "", "", "", "", 0, 0, 0, 0, 0, 0)))
        val models = WrathppUndead.Dbc(WrathppBody.MODEL_KINDS, mutableListOf(
            (listOf<Any>(6838, 0, "Character\\Orc\\Male\\OrcMale.mdx") + List<Any>(25) { 0 }).toTypedArray()))
        repeat(2) { WrathppVariants.addRows(displays, models, listOf(upright)) { 51894 } }        // twice: the rows aren't doubled
        assertEquals(2, displays.rows.size)
        val row = displays.rows.first { it[0] == 44001 }
        assertEquals(WrathppVariants.modelId(upright), row[1])
        assertEquals(2, models.rows.size)
        assertEquals("Character\\Orc\\Male\\OrcMaleV2.mdx", models.rows.first { it[0] == WrathppVariants.modelId(upright) }[2])
        assertTrue(displays.rows.any { it[0] == 51894 })                                              // the race's own stays
        val server = WrathppUndead.Dbc(WrathppBody.DISPLAY_KINDS, mutableListOf(arrayOf<Any>(51894, 6838, 0, 0, 1, 1, "", "", "", "", 0, 0, 0, 0, 0, 0)))
        WrathppVariants.addRows(server, null, listOf(upright)) { 51894 }
        assertEquals(6838, server.rows.first { it[0] == 44001 }[1])                                   // the server's keeps the race's model id
        assertNull(WrathppVariants.parse("").firstOrNull())
    }
}
