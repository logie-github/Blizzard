package com.logie.blizz.wrathpp

import java.io.File
import java.nio.ByteBuffer
import java.nio.ByteOrder
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder

class WrathppDisplayCheckTest {
    @get:Rule val tmp = TemporaryFolder()

    private fun table(fields: Int, rows: List<IntArray>): ByteArray {
        val b = ByteBuffer.allocate(20 + rows.size * fields * 4 + 1).order(ByteOrder.LITTLE_ENDIAN)
        b.putInt(0x43424457); b.putInt(rows.size); b.putInt(fields); b.putInt(fields * 4); b.putInt(1)
        for (r in rows) for (i in 0 until fields) b.putInt(r.getOrElse(i) { 0 })
        return b.array()
    }

    @Test fun aRaceDisplayWithoutARowIsNamed() {
        val bad = WrathppDisplayCheck.problems(listOf(Triple(28, 33013, 33014)), mapOf(33014 to 3614), setOf(3614))
        assertEquals(listOf("race 28 male: display 33013 is not in CreatureDisplayInfo"), bad)
    }

    @Test fun aDisplayWhoseModelIsMissingIsNamed() {
        val bad = WrathppDisplayCheck.problems(listOf(Triple(26, 33009, 0)), mapOf(33009 to 3609), emptySet())
        assertTrue(bad.single().contains("model 3609"))
    }

    @Test fun theLooksTablesAreReadFromThePatchFolder() {
        val client = tmp.newFolder("client")
        val dir = File(client, "Data/${WrathppLooks.PATCH}/DBFilesClient").also { it.mkdirs() }
        File(dir, "ChrRaces.dbc").writeBytes(table(6, listOf(intArrayOf(28, 12, 3, 4147, 33013, 33014))))
        File(dir, "CreatureDisplayInfo.dbc").writeBytes(table(3, listOf(intArrayOf(33013, 3613), intArrayOf(33014, 3614))))
        File(dir, "CreatureModelData.dbc").writeBytes(table(2, listOf(intArrayOf(3613), intArrayOf(3614))))
        assertEquals("1 races' displays are all there", WrathppDisplayCheck.check(client))
        File(dir, "CreatureDisplayInfo.dbc").writeBytes(table(3, listOf(intArrayOf(33014, 3614))))
        assertTrue(WrathppDisplayCheck.check(client).startsWith("1 MISSING"))
    }
}
