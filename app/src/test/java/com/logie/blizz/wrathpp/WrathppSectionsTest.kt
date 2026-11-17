package com.logie.blizz.wrathpp

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File
import java.nio.ByteBuffer
import java.nio.ByteOrder

/** The character table put in the order the client's BuildComponentArray needs (issue 294). */
class WrathppSectionsTest {
    @get:Rule val tmp = TemporaryFolder()

    // CharSections: id, race, sex, section, three textures, flags, variation, colour
    private fun table(vararg rows: IntArray): DbcTable {
        val b = ByteBuffer.allocate(20 + rows.size * 40 + 1).order(ByteOrder.LITTLE_ENDIAN)
        b.putInt(0x43424457); b.putInt(rows.size); b.putInt(10); b.putInt(40); b.putInt(1)
        for (r in rows) for (i in 0 until 10) b.putInt(r[i])
        return DbcTable(b.array())
    }
    private fun row(id: Int, race: Int, sex: Int, section: Int, variation: Int, colour: Int) = intArrayOf(id, race, sex, section, 0, 0, 0, 0, variation, colour)

    @Test fun aGroupSplitWithAHigherVariationFirstIsTheClientsOverrun() {
        // Human woman's faces: variations 0-3, then another race, then a later run of hers with variation 0 only (a patch's row at the end)
        val t = table(row(1, 1, 1, 1, 0, 0), row(2, 1, 1, 1, 3, 0), row(3, 2, 0, 1, 0, 0), row(4, 1, 1, 1, 0, 1))
        val (over, split) = WrathppSections.overruns(t)
        assertEquals(1, split)
        assertEquals(1, over)            // the first run's variation 3 is past the 1 the last run sized
        assertTrue(WrathppSections.order(t))
        assertEquals(0 to 0, WrathppSections.overruns(t))
        assertEquals(listOf(1, 4, 2, 3), (0 until 4).map { t.get(it, 0) })   // stable: her variation 0 rows in their order, then 3, then the other race
    }

    @Test fun aTableInOrderIsLeftAsItIs() {
        val t = table(row(1, 1, 0, 0, 0, 0), row(2, 1, 0, 0, 0, 1), row(3, 1, 0, 1, 0, 0), row(4, 2, 1, 0, 0, 0))
        assertEquals(0 to 0, WrathppSections.overruns(t))
        assertFalse(WrathppSections.order(t))
    }

    @Test fun thePatchsTableIsWrittenInOrder() {
        val client = tmp.newFolder("client")
        val file = File(client, "Data/${WrathppLooks.PATCH}/DBFilesClient/CharSections.dbc").apply { parentFile!!.mkdirs() }
        file.writeBytes(table(row(1, 1, 1, 1, 0, 0), row(2, 1, 1, 1, 3, 0), row(3, 2, 0, 1, 0, 0), row(4, 1, 1, 1, 0, 1)).write())
        assertEquals("put in order: 1 overruns and 1 split groups before, 0 and 0 now", WrathppSections.apply(client))
        assertTrue(WrathppSections.apply(client).startsWith("in order (0 overruns"))
    }
}
