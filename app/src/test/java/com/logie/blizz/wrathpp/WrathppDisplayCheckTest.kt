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

    @Test fun rowsTheGamesTableLacksAreAddedFromTheLooksCopy() {
        val client = tmp.newFolder("client2")
        val patch = File(client, "Data/${WrathppLooks.PATCH}")
        val dir = File(patch, "DBFilesClient").also { it.mkdirs() }
        val copy = File(patch, WrathppLooks.SERVER_COPY).also { it.mkdirs() }
        fun display(vararg ids: Int) = WrathppUndead.Dbc(WrathppBody.DISPLAY_KINDS, ids.map { id -> Array<Any>(16) { i -> if (WrathppBody.DISPLAY_KINDS[i] == 's') "" else if (i == 0) id else if (i == 1) id - 29400 else 0 } }.toMutableList()).write()
        fun model(vararg ids: Int) = WrathppUndead.Dbc(WrathppBody.MODEL_KINDS, ids.map { id -> Array<Any>(WrathppBody.MODEL_KINDS.length) { i -> if (WrathppBody.MODEL_KINDS[i] == 's') "x" else if (i == 0) id else 0 } }.toMutableList()).write()
        File(dir, "CreatureDisplayInfo.dbc").writeBytes(display(1, 2))
        File(dir, "CreatureModelData.dbc").writeBytes(model(1, 2))
        File(copy, "CreatureDisplayInfo.dbc").writeBytes(display(1, 2, 33013, 33014))
        File(copy, "CreatureModelData.dbc").writeBytes(model(1, 2, 3613, 3614))
        assertEquals(4, WrathppDisplayCheck.repair(client))
        assertEquals(0, WrathppDisplayCheck.repair(client))
        assertEquals(setOf(1, 2, 33013, 33014), WrathppDisplayCheck.readDisplays(File(dir, "CreatureDisplayInfo.dbc").readBytes()).keys)
        assertEquals(setOf(1, 2, 3613, 3614), WrathppDisplayCheck.readModels(File(dir, "CreatureModelData.dbc").readBytes()))
    }
}
