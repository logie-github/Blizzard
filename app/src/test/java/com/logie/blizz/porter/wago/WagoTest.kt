package com.logie.blizz.porter.wago

import com.logie.blizz.porter.net.Net
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.File

/** wago.tools' tables and files as the porter asks for them: the addresses, the batches, what is kept, the CSV. */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class WagoTest {
    @get:Rule val tmp = TemporaryFolder()

    /** A wago.tools that answers a table's filter from rows of its own, and notes what was asked. */
    private class Site(private val header: String, private val rows: List<String>, private val column: Int) : Net {
        // Synchronized: GameFiles fetches on four threads at once (a plain list could lose one of them: CI run 220).
        val asked: MutableList<String> = java.util.Collections.synchronizedList(ArrayList())
        override fun get(url: String, headers: Map<String, String>): Net.Reply {
            asked += url
            val values = Regex("exact%3A([0-9%7C]+)").find(url)!!.groupValues[1].split("%7C").map { it.toInt() }.toSet()
            val body = (listOf(header) + rows.filter { it.split(',')[column].toInt() in values }).joinToString("\n", postfix = "\n")
            return Net.Reply(200, body.toByteArray(), url)
        }
        override fun post(url: String, body: ByteArray, headers: Map<String, String>) = Net.Reply(405, ByteArray(0), url)
        override fun save(url: String, to: File, headers: Map<String, String>, progress: (Long) -> Unit) {
            asked += url
            to.parentFile?.mkdirs()
            to.writeBytes(byteArrayOf(1, 2, 3))
            progress(3)
        }
    }

    @Test fun csvKeepsQuotedCommasQuotesAndLineBreaks() {
        val text = "ID,Name_lang,Flags\r\n1,\"Hello, \"\"world\"\"\",4294967295\n2,\"two\nlines\",-1\n"
        val (header, rows) = Csv.table(text)
        assertEquals(listOf("ID", "Name_lang", "Flags"), header)
        assertEquals(listOf("Hello, \"world\"", "two\nlines"), rows.map { it.str("Name_lang") })
        // Flags written unsigned keep their bits.
        assertEquals(listOf(-1, -1), rows.map { it.int("Flags") })
        assertEquals(rows.map { it.str("Name_lang") }, Csv.parse(Csv.write(header, rows)).map { it.str("Name_lang") })
        assertEquals(0, Row(mapOf("A" to "")).int("A"))
        assertEquals(3, Row(mapOf("A" to "3.0")).int("A"))
    }

    @Test fun rowsAreAskedInBatchesAndKeptForTheNextTime() {
        val site = Site("ID,ChrModelID,OrderIndex", (1..150).map { "$it,${it % 3},0" }, 1)
        val cache = tmp.newFolder("cache")
        val tables = WagoTables(site, "12.1.5.70783", cache)
        assertEquals(50, tables.rows("ChrCustomizationOption", "ChrModelID", 1).size)
        assertEquals("https://wago.tools/db2/ChrCustomizationOption/csv?filter%5BChrModelID%5D=exact%3A1&build=12.1.5.70783", site.asked.single())
        // Many values: in batches of sixty, each value's rows its own.
        val idSite = Site("ID,ChrModelID,OrderIndex", (1..150).map { "$it,${it % 3},0" }, 0)
        val byId = WagoTables(idSite, "12.1.5.70783", cache)
        val ids = (1..130).toList()
        assertEquals(ids, byId.rows("ChrCustomizationOption", "ID", ids).map { it.int("ID") })
        assertEquals(3, idSite.asked.size)
        // Asked again (and by a new instance, from the phone's copy): nothing is asked of the site, a value with no rows included.
        byId.rows("ChrCustomizationOption", "ID", listOf(5, 999))
        assertEquals(4, idSite.asked.size)
        val again = WagoTables(idSite, "12.1.5.70783", cache)
        assertEquals(listOf(7), again.rows("ChrCustomizationOption", "ID", listOf(7)).map { it.int("ID") })
        assertEquals(emptyList<Row>(), again.rows("ChrCustomizationOption", "ID", 999))
        assertEquals(4, idSite.asked.size)
        // Another build asks again.
        WagoTables(idSite, "12.1.7.70740", cache).rows("ChrCustomizationOption", "ID", 7)
        assertEquals(5, idSite.asked.size)
    }

    @Test fun filesAreTheBuildsAndOtherBuildsCanGo() {
        val site = Site("ID", emptyList(), 0)
        val dir = tmp.newFolder("files")
        val files = GameFiles(site, "12.1.5.70783", dir)
        var last: GameFiles.Progress? = null
        files.fetch(listOf(917116, 4690417, 917116, 0)) { last = it }
        assertEquals(setOf("https://wago.tools/api/casc/917116?download&version=12.1.5.70783", "https://wago.tools/api/casc/4690417?download&version=12.1.5.70783"), site.asked.toSet())
        assertEquals(2, last!!.total)
        assertTrue(files.has(917116))
        files.fetch(listOf(917116))
        assertEquals(2, site.asked.size)
        File(dir, "12.1.0.69933/123").apply { parentFile!!.mkdirs(); writeText("old") }
        files.forgetOtherBuilds()
        assertEquals(listOf("12.1.5.70783"), dir.list()!!.toList())
    }

    @Test fun theLiveBuildIsTheGamesNewest() {
        val json = """{"wowt":[{"version":"12.1.7.70740"}],"wow":[{"version":"12.1.5.70783","created_at":"2026-11-04"},{"version":"12.1.5.70688"}]}"""
        assertEquals("12.1.5.70783", WagoTables.parseBuilds(json))
        assertEquals(null, WagoTables.parseBuilds("""{"wow":[]}"""))
    }
}
