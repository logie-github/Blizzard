package com.logie.blizz.wrathpp

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
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

/** Wrath++'s looks package put into its copy of the game and its server ([WrathppLooks.install]). */
class WrathppLooksTest {
    @get:Rule val tmp = TemporaryFolder()

    private fun zip(entries: Map<String, String>): File = tmp.newFile().also { f ->
        ZipOutputStream(f.outputStream()).use { z -> for ((n, t) in entries) { z.putNextEntry(ZipEntry(n)); z.write(t.toByteArray()); z.closeEntry() } }
    }

    // The game's own CharSections (4 rows: iisf, the DbcChangesTest's), the package's change to it, and the server's table.
    private val gameTable = DbcTable.hex("5744424304000000040000001000000009000000010000000a000000010000000000803f020000000a00000003000000000000400300000007000000050000000000404004000000070000000700000000008040006100620063006400")
    private val tables: (String) -> ByteArray? = { name -> if (name == "DBFilesClient\\CharSections.dbc") gameTable else null }
    private val good = mapOf(
        "client/Character/Human/Male/HumanMale.m2" to "model",
        "changes/CharSections.txt" to "types\tiisf\nput\t7\t1\tseven\t0.5\n",
        "dbc/CharSections.dbc" to "sections",
        "dbc/CharHairGeosets.dbc" to "hair",
        "looks.files" to "list",
    )

    private fun setup(): Pair<File, File> {
        val client = tmp.newFolder("client-wrathpp")
        File(client, "Data/patch-W.MPQ").apply { parentFile!!.mkdirs(); writeText("alternative hd") }
        val server = tmp.newFolder("server-wrathpp")
        File(server, "share/mariadb").mkdirs()
        return client to server
    }

    @Test fun installsTheGamesPatchAndTheServersTables() {
        val (client, server) = setup()
        WrathppLooks.install(client, server, zip(good), "abc", tables = tables)
        assertEquals("model", File(client, "Data/patch-Z.MPQ/Character/Human/Male/HumanMale.m2").readText())
        // the game's own table with the package's row put in (5 rows now), not the package's alone
        val made = DbcTable(File(client, "Data/patch-Z.MPQ/DBFilesClient/CharSections.dbc").readBytes())
        assertEquals(5, made.records.size)
        assertEquals(7, made.get(4, 0))
        assertEquals("sections", File(client, "Data/patch-Z.MPQ/wrathpp-server-dbc/CharSections.dbc").readText())
        assertFalse(File(client, "Data/patch-Z.MPQ/changes").exists()); assertFalse(File(client, "Data/patch-Z.MPQ.changes").exists())
        assertEquals("sections", File(server, "share/dbc/CharSections.dbc").readText())
        assertFalse(File(client, "Data/patch-Z.MPQ/looks.files").exists())
        assertEquals("abc", WrathppLooks.installedSha(client, server))
        // the rest of the game and the server as they were
        assertEquals("alternative hd", File(client, "Data/patch-W.MPQ").readText())
        assertTrue(File(server, "share/mariadb").isDirectory)
        assertFalse(File(client, "Data/patch-Z.MPQ.new").exists()); assertFalse(File(server, "share/dbc.new").exists())
    }

    @Test fun aNewerPackageReplacesTheOldOneWhole() {
        val (client, server) = setup()
        WrathppLooks.install(client, server, zip(good + ("client/Character/Old.m2" to "old")), "one", tables = tables)
        WrathppLooks.install(client, server, zip(good), "two", tables = tables)
        assertFalse(File(client, "Data/patch-Z.MPQ/Character/Old.m2").exists())
        assertEquals("two", WrathppLooks.installedSha(client, server))
    }

    @Test fun aBadPackageLeavesWhatWasThere() {
        val (client, server) = setup()
        WrathppLooks.install(client, server, zip(good), "one", tables = tables)
        for (bad in listOf(mapOf("client/../escape" to "x") + good, good - "dbc/CharSections.dbc", good + ("changes/CharSections.txt" to "types\tii\n"), good + ("changes/Nothing.txt" to "types\tii\n"))) {
            try { WrathppLooks.install(client, server, zip(bad), "two", tables = tables); fail("installed $bad") } catch (_: IOException) {}
            assertEquals("one", WrathppLooks.installedSha(client, server))
            assertTrue(File(client, "Data/patch-Z.MPQ/Character/Human/Male/HumanMale.m2").isFile)
        }
        assertFalse(File(tmp.root, "escape").exists())
    }

    @Test fun theServersTablesComeBackFromThePatchAfterANewServerPackage() {
        val (client, server) = setup()
        WrathppLooks.install(client, server, zip(good), "abc", tables = tables)
        File(server, "share").deleteRecursively()                        // a new server package
        assertNull(WrathppLooks.installedSha(client, server))
        assertFalse(WrathppLooks.restoreServer(client, server, "other"))  // a newer package published: downloaded instead
        assertTrue(WrathppLooks.restoreServer(client, server, "abc"))
        assertEquals("sections", File(server, "share/dbc/CharSections.dbc").readText())
        assertEquals("abc", WrathppLooks.installedSha(client, server))
    }
    @Test fun aPatchFromBeforeTheChangesGivesTheServerItsWholeTables() {
        val (client, server) = setup()
        val patch = File(client, "Data/patch-Z.MPQ").apply { mkdirs() }
        File(patch, "DBFilesClient").mkdirs()
        File(patch, "DBFilesClient/CharSections.dbc").writeText("old sections")
        File(patch, WrathppLooks.MARKER).writeText("old\n")
        assertNull(WrathppLooks.installedSha(client, server))
        assertTrue(WrathppLooks.restoreServer(client, server, "old"))
        assertEquals("old sections", File(server, "share/dbc/CharSections.dbc").readText())
        assertEquals("old", WrathppLooks.installedSha(client, server))
    }
}
