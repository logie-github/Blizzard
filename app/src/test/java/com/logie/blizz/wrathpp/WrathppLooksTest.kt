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

    private val good = mapOf(
        "client/Character/Human/Male/HumanMale.m2" to "model",
        "client/DBFilesClient/CharSections.dbc" to "sections",
        "client/DBFilesClient/CharHairGeosets.dbc" to "hair",
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
        WrathppLooks.install(client, server, zip(good), "abc")
        assertEquals("model", File(client, "Data/patch-Z.MPQ/Character/Human/Male/HumanMale.m2").readText())
        assertEquals("sections", File(client, "Data/patch-Z.MPQ/DBFilesClient/CharSections.dbc").readText())
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
        WrathppLooks.install(client, server, zip(good + ("client/Character/Old.m2" to "old")), "one")
        WrathppLooks.install(client, server, zip(good), "two")
        assertFalse(File(client, "Data/patch-Z.MPQ/Character/Old.m2").exists())
        assertEquals("two", WrathppLooks.installedSha(client, server))
    }

    @Test fun aBadPackageLeavesWhatWasThere() {
        val (client, server) = setup()
        WrathppLooks.install(client, server, zip(good), "one")
        for (bad in listOf(mapOf("client/../escape" to "x") + good, good - "dbc/CharSections.dbc")) {
            try { WrathppLooks.install(client, server, zip(bad), "two"); fail("installed $bad") } catch (_: IOException) {}
            assertEquals("one", WrathppLooks.installedSha(client, server))
            assertTrue(File(client, "Data/patch-Z.MPQ/Character/Human/Male/HumanMale.m2").isFile)
        }
        assertFalse(File(tmp.root, "escape").exists())
    }

    @Test fun theServersTablesComeBackFromThePatchAfterANewServerPackage() {
        val (client, server) = setup()
        WrathppLooks.install(client, server, zip(good), "abc")
        File(server, "share").deleteRecursively()                        // a new server package
        assertNull(WrathppLooks.installedSha(client, server))
        assertFalse(WrathppLooks.restoreServer(client, server, "other"))  // a newer package published: downloaded instead
        assertTrue(WrathppLooks.restoreServer(client, server, "abc"))
        assertEquals("sections", File(server, "share/dbc/CharSections.dbc").readText())
        assertEquals("abc", WrathppLooks.installedSha(client, server))
    }
}
