package com.logie.blizz.porter.port

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

class RealmDbTest {
    @get:Rule val temp = TemporaryFolder()

    @Test fun textIsQuotedWithEverythingMariaDbReadsSpeciallyEscaped() {
        assertEquals("'Brannoc'", Sql.text("Brannoc"))
        assertEquals("'O''Neil'", Sql.text("O'Neil"))
        assertEquals("'a\\\\b'", Sql.text("a\\b"))
        assertEquals("'x\\0y\\nz\\r\\Z'", Sql.text("x\u0000y\nz\r\u001a"))
    }

    @Test fun namesAreOnlyLettersDigitsAndUnderscores() {
        assertEquals("`acore_characters`", Sql.name("acore_characters"))
        for (bad in listOf("a b", "x`; DROP", "", "a-b")) {
            try { Sql.name(bad); fail(bad) } catch (e: IllegalArgumentException) { }
        }
        assertEquals("NULL", Sql.list(emptyList()))
        assertEquals("1,2,3", Sql.list(listOf(1, 2, 3)))
    }

    @Test fun batchRowsAreSplitAndUnescapedAsTheClientWritesThem() {
        val rows = BatchRows.parse("1\tBrannoc\tNULL\n2\ta\\tb\\nc\\\\d\n")
        assertEquals(listOf(listOf("1", "Brannoc", null), listOf("2", "a\tb\nc\\d")), rows)
        assertEquals(emptyList<List<String?>>(), BatchRows.parse(""))
    }

    /** A stand-in for the database client: prints [output] after reading its input, exits with [code]. */
    private fun client(output: String, code: Int = 0): List<String> {
        val script = File(temp.root, "client-${output.hashCode()}-$code.sh")
        script.writeText("#!/bin/sh\ncat > \"${temp.root}/input-\$1.sql\"\nprintf '%b' '${output.replace("'", "'\\''")}'\nexit $code\n")
        script.setExecutable(true)
        return listOf("sh", script.path)
    }

    @Test fun aProgramIsRunWithTheDatabaseAndTheSqlOnItsInput() {
        val db = ProcessRealmDb(client("7\\tBrannoc\\n"))
        assertEquals(listOf(listOf("7", "Brannoc")), db.query("acore_characters", "SELECT guid, name FROM characters"))
        assertEquals("SELECT guid, name FROM characters", File(temp.root, "input-acore_characters.sql").readText())
    }

    @Test fun manySelectsGoInOneRunAndComeBackApart() {
        val db = ProcessRealmDb(client("1\\tb\\n0\\ta\\n1\\tc\\n"))
        val results = db.queryAll("acore_world", listOf("SELECT x FROM t", "SELECT y FROM u"))
        assertEquals(listOf(listOf(listOf("a")), listOf(listOf("b"), listOf("c"))), results)
        val sent = File(temp.root, "input-acore_world.sql").readText()
        assertTrue(sent, sent.contains("SELECT 0 AS porter_n, porter_t.* FROM (SELECT x FROM t) porter_t;"))
        assertTrue(sent, sent.contains("SELECT 1 AS porter_n, porter_t.* FROM (SELECT y FROM u) porter_t;"))
    }

    @Test fun theAppsCtlCommandIsRunWithTheDatabaseAfterIt() {
        val script = File(temp.root, "ctl.sh")
        script.writeText("#!/bin/sh\ncat > /dev/null\nprintf '%s\\t%s\\t%s\\n' \"\$1\" \"\$2\" \"\$FILES\"\n")
        val db = ProcessRealmDb.of(com.logie.blizz.wow.WowCtl.Command(listOf("sh", script.path, "sql"), mapOf("FILES" to "/data/files"), temp.root))
        assertEquals(listOf(listOf("sql", "acore_world", "/data/files")), db.query("acore_world", "SELECT 1"))
    }

    @Test fun aFailureIsTheClientsOwnMessage() {
        val script = File(temp.root, "failing.sh")
        script.writeText("#!/bin/sh\ncat > /dev/null\necho 'ERROR 1644 (45000) at line 3: Porter: the name is taken' >&2\nexit 1\n")
        val db = ProcessRealmDb(listOf("sh", script.path))
        try {
            db.execute("acore_characters", "START TRANSACTION;")
            fail()
        } catch (e: RealmDbException) {
            assertTrue(e.message!!, e.message!!.contains("the name is taken"))
        }
        try { db.query("bad name", "SELECT 1"); fail() } catch (e: IllegalArgumentException) { }
    }
}
