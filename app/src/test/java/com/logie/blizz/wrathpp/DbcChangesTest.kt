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
