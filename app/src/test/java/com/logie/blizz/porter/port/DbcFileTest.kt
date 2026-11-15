package com.logie.blizz.porter.port

import com.logie.blizz.porter.port.PortTestData.DbcWriter
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File
import java.io.IOException

class DbcFileTest {
    @get:Rule val temp = TemporaryFolder()

    private fun spells(): ByteArray {
        val w = DbcWriter(4)
        w.row(0 to 133, 1 to w.text("Fireball"), 2 to java.lang.Float.floatToIntBits(1.5f), 3 to -1)
        w.row(0 to 168, 1 to w.text("Frost Armor"), 2 to java.lang.Float.floatToIntBits(0f), 3 to 7)
        return w.bytes()
    }

    @Test fun readsTheHeaderTheRecordsAndTheStrings() {
        val dbc = DbcFile.parse(spells(), "Spell.dbc")
        assertEquals(2, dbc.recordCount)
        assertEquals(4, dbc.fieldCount)
        assertEquals(16, dbc.recordSize)
        assertEquals(133, dbc.int(0, 0))
        assertEquals("Fireball", dbc.string(0, 1))
        assertEquals("Frost Armor", dbc.string(1, 1))
        assertEquals(1.5f, dbc.float(0, 2))
        assertEquals(-1, dbc.int(0, 3))
    }

    @Test fun aStringOutsideTheBlockIsEmpty() {
        val w = DbcWriter(2)
        w.row(0 to 1, 1 to 9999)
        assertEquals("", DbcFile.parse(w.bytes()).string(0, 1))
    }

    @Test fun refusesWhatIsntADbcFile() {
        val bytes = spells()
        bytes[0] = 'X'.code.toByte()
        try { DbcFile.parse(bytes); fail() } catch (e: IOException) { assertTrue(e.message!!.contains("isn't a DBC")) }
        try { DbcFile.parse(spells().copyOf(30)); fail() } catch (e: IOException) { assertTrue(e.message!!.contains("cut short")) }
        try { DbcFile.parse(ByteArray(8)); fail() } catch (e: IOException) { }
    }

    @Test fun readsOutsideARecordOrFieldAreRefused() {
        val dbc = DbcFile.parse(spells())
        try { dbc.int(2, 0); fail() } catch (e: IndexOutOfBoundsException) { }
        try { dbc.int(0, 4); fail() } catch (e: IndexOutOfBoundsException) { }
    }

    @Test fun opensAFileByNameWhateverItsCase() {
        val dir = temp.newFolder("dbc")
        File(dir, "spell.DBC").writeBytes(spells())
        val found = DbcFile.find(dir, "Spell.dbc")!!
        assertEquals(2, DbcFile.open(found).recordCount)
        assertNull(DbcFile.find(dir, "Faction.dbc"))
    }

    @Test fun theDatabasesRowsGoOverTheFilesAsTheCoreLoadsThem() {
        val file = DbcFile.parse(spells())
        // A module's row in place of 168 (its empty name keeps the file's), and a new spell.
        val table = DbcTable("Spell", file, 0, listOf(mapOf(0 to "168", 1 to "", 3 to "9"), mapOf(0 to "98800", 1 to "Will to Survive", 3 to "2")))
        assertEquals(setOf(133, 168, 98800), table.ids)
        assertEquals("Frost Armor", table[168]!!.string(1))
        assertEquals(9, table[168]!!.int(3))
        assertEquals("Will to Survive", table[98800]!!.string(1))
        assertTrue(table.inFile(168))
        assertFalse(table.inFile(98800))
        assertEquals("Fireball", table[133]!!.string(1))
        assertNull(table[1])
    }
}
