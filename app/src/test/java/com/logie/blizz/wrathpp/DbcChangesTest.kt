package com.logie.blizz.wrathpp

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Test
import java.io.IOException

/** [DbcTable] against what `realm/warcraft/wrathpp/tools/apply_client.py` makes of the same table and changes (one golden). */
class DbcChangesTest {
    private fun hex(s: String) = DbcTable.hex(s)
    private fun toHex(b: ByteArray) = b.joinToString("") { "%02x".format(it) }

    // 4 rows (iisf): put replacing a row and adding one, copyrow (once: the second names a row that is there), remapfield, or, set,
    // or of a row that isn't there, drop, appendraw twice (once), strings (one escaped), a float. Made by apply_client.py.
    private val input = "5744424304000000040000001000000009000000010000000a000000010000000000803f020000000a00000003000000000000400300000007000000050000000000404004000000070000000700000000008040006100620063006400"
    private val changes = "types\tiisf\nput\t2\t99\tnew\\\\name\t4.5\nput\t5\t5\tfive\t0.25\ncopyrow\t1\t9\ncopyrow\t1\t2\nremapfield\t1\t10\t11\nor\t3\t1\t8\nset\t5\t1\t77\nor\t55\t1\t1\ndrop\t1\t7\t0\t4\nappendraw\t0600000006000000000000000000803f\nappendraw\t0600000006000000000000000000803f\n"
    private val expected = "5744424306000000040000001000000017000000010000000b000000010000000000803f02000000630000000900000000009040030000000f0000000500000000004040050000004d000000120000000000803e090000000b000000010000000000803f0600000006000000000000000000803f0061006200630064006e65775c6e616d65006669766500"

    @Test fun theSameBytesAsTheToolMakes() {
        val t = DbcTable(hex(input))
        t.apply(changes)
        assertEquals(expected, toHex(t.write()))
    }

    // 6 rows (iiiiis: id, race, sex, skin, face, name) and Wrath++'s own map: a field from itself in the rows of one race and sex (each row
    // looked up once, the unlisted the default), no default (left as it is) and a value of 32 bits, a key of two fields, every row ("-"),
    // the id field and then a put of that id. Made by apply_client.py.
    private val mapInput = "574442430600000006000000180000000d00000001000000040000000100000002000000050000000100000002000000040000000100000003000000000000000300000003000000040000000000000002000000050000000500000004000000050000000100000009000000010000000700000005000000040000000100000028000000070000000900000006000000060000000000000003000000020000000b00000000610062006300640065006600"
    private val mapChanges = "# the creatures' looks: a rule by race and sex\nmap\t1=4,2=1\t3\t3\t0\t2=3\t3=7\nmap\t1=4,2=1\t4\t4\t-\t5=30\t0=4294967295\nmap\t1=6,2=0\t3,4\t4\t9\t3,2=17\t3,3=18\nmap\t-\t1,2\t3\t-\t5,1=8\ntypes\tiiiiis\nmap\t-\t0\t0\t-\t3=30\nput\t30\t1\t1\t1\t1\tnew\n"
    private val mapExpected = "5744424306000000060000001800000011000000010000000400000001000000030000001e0000000100000002000000040000000100000007000000ffffffff030000001e000000010000000100000001000000010000000d00000004000000050000000100000008000000010000000700000005000000040000000100000000000000070000000900000006000000060000000000000003000000110000000b000000006100620063006400650066006e657700"

    @Test fun aMapIsTheSameBytesAsTheToolMakes() {
        val t = DbcTable(hex(mapInput))
        t.apply(mapChanges)
        assertEquals(mapExpected, toHex(t.write()))
        // row by row: race 4 sex 1's skins 2 -> 3 and 3 -> 7 (not 2 -> 3 -> 7), 40 -> the default 0; another sex and race untouched by it
        assertEquals(listOf(3, 7, 1, 8, 0, 3), t.records.indices.map { t.get(it, 3) })
        assertEquals(listOf(30, -1, 1, 1, 7, 17), t.records.indices.map { t.get(it, 4) })
        assertEquals(listOf(1, 2, 30, 4, 5, 6), t.records.indices.map { t.get(it, 0) })
    }

    @Test fun aBadMapIsRefusedWithItsLine() {
        for ((text, part) in listOf("map\t-\t3\n" to "wrong size", "map\t-\t9\t3\t0\n" to "no such field", "map\t-\t3\t9\t0\n" to "no such field",
            "map\t9=1\t3\t3\t0\n" to "no such field", "map\t1\t3\t3\t0\n" to "FIELD=VALUE", "map\t-\t1,2\t3\t0\t4=1\n" to "key of the wrong size",
            "map\t-\t3\t3\tx\n" to "isn't one", "map\t-\t3\t3\t0\t2\n" to "KEY=VALUE", "map\t-\t-1\t3\t0\n" to "no such field", "\nmap\t-\t3\n" to "line 2")) {
            val t = DbcTable(hex(mapInput))
            try { t.apply(text); fail("accepted $text") } catch (e: IOException) { assertTrue("${e.message} for $part", e.message!!.contains(part)) }
        }
    }

    @Test fun aTableReadAndWrittenIsTheSame() {
        assertEquals(input, toHex(DbcTable(hex(input)).write()))
    }

    @Test fun badChangesAreRefusedWithTheirLine() {
        for ((text, part) in listOf("types\tii\n" to "isn't the one", "types\tiisf\nput\t1\t2\n" to "line 2", "frobnicate\t1\n" to "unknown", "types\tiisf\ndrop\t1\n" to "wrong size",
            "types\tiisf\nput\t1\tx\ta\t1.0\n" to "isn't one")) {
            try { DbcTable(hex(input)).apply(text); fail("accepted $text") } catch (e: IOException) { assertTrue("${e.message} for $part", e.message!!.contains(part)) }
        }
    }

    @Test fun aCutShortTableIsRefused() {
        try { DbcTable(hex(input).copyOf(30)); fail() } catch (_: IOException) {}
        try { DbcTable(ByteArray(8)); fail() } catch (_: IOException) {}
    }
}
