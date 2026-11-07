package com.logie.blizz.wowaddons

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.File
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class AddonsTest {
    @get:Rule val tmp = TemporaryFolder()
    private val context: Context = ApplicationProvider.getApplicationContext()

    /** A client in a temp folder, through the same guard the real games use. */
    private inner class Fake : AddonGame {
        val client = File(tmp.root, "files/client").also { File(it, "Interface").mkdirs() }
        private val guard = AddonGuard(
            listOf(File(client, "Interface"), File(tmp.root, "files/addon-downloads")),
            listOf(File(tmp.root, "files/warperia-addons.tsv")),
        )
        override val flavor = Warperia.Flavor.WOTLK
        override val interfaceVersion = "30300"
        override val ownFolders = setOf("wowtouch")
        override fun hasClient(context: Context) = true
        override fun client(context: Context) = client
        override fun recordsFile(context: Context) = File(tmp.root, "files/warperia-addons.tsv")
        override fun temp(context: Context) = File(tmp.root, "files/addon-downloads")
        override fun check(context: Context, file: File) = guard.check(file)
        override fun mkdirs(context: Context, folder: File) = guard.mkdirs(folder)
        override fun delete(context: Context, target: File): Boolean { guard.delete(target); return true }
        override fun move(context: Context, from: File, to: File): Boolean { guard.move(from, to); return true }
        override fun replace(context: Context, temp: File, file: File): Boolean { guard.replace(temp, file); return true }
        override fun noClientMessage(context: Context) = "none"
    }

    private fun zip(vararg entries: Pair<String, String>): File {
        val file = File(tmp.root, "z${System.nanoTime()}.zip")
        ZipOutputStream(file.outputStream()).use { out ->
            for ((name, text) in entries) {
                out.putNextEntry(ZipEntry(name))
                out.write(text.toByteArray())
                out.closeEntry()
            }
        }
        return file
    }

    private val toc = "## Interface: 30300\n## Title: |cff00ff00Questie|r\n## Version: 1.2\n"

    @Test
    fun installsListsTurnsOffAndDeletes() {
        val game = Fake()
        val folders = Addons.installZip(context, zip("Questie-1.2/Questie.toc" to toc, "Questie-1.2/Questie.lua" to "x"), game)
        assertEquals(listOf("Questie"), folders)
        assertTrue(File(game.client, "Interface/AddOns/Questie/Questie.lua").isFile)

        val listed = Addons.list(context, game).single()
        assertEquals("Questie", listed.title)
        assertEquals("1.2", listed.version)
        assertTrue(listed.forThisGame)
        assertTrue(listed.on)

        assertTrue(Addons.setOn(context, "Questie", false, game))
        assertFalse(File(game.client, "Interface/AddOns/Questie").exists())
        assertTrue(File(game.client, "Interface/AddOns-off/Questie/Questie.toc").isFile)
        assertFalse(Addons.list(context, game).single().on)

        // A new copy of an add-on that is off stays off, and lands whole.
        Addons.installZip(context, zip("Questie/Questie.toc" to toc, "Questie/new.lua" to "y"), game)
        assertTrue(File(game.client, "Interface/AddOns-off/Questie/new.lua").isFile)
        assertFalse(File(game.client, "Interface/AddOns-off/Questie/Questie.lua").exists())
        assertFalse(File(game.client, "Interface/AddOns/Questie").exists())

        assertTrue(Addons.exists(context, "Questie", game))
        assertTrue(Addons.delete(context, "Questie", game))
        assertFalse(Addons.exists(context, "Questie", game))
    }

    @Test
    fun aZipWithNoAddOnIsRefused() {
        val game = Fake()
        try {
            Addons.installZip(context, zip("readme.txt" to "hi"), game)
            org.junit.Assert.fail("Expected NoAddonException")
        } catch (_: Addons.NoAddonException) {
        }
    }

    @Test
    fun theAppsOwnAddOnIsNotListed() {
        val game = Fake()
        Addons.installZip(context, zip("WowTouch/WowTouch.toc" to "## Title: Touch\n", "Bagnon/Bagnon.toc" to "## Title: Bagnon\n"), game)
        assertEquals(listOf("Bagnon"), Addons.list(context, game).map { it.folder })
    }

    @Test
    fun entriesThatStepOutOfTheFolderAreDropped() {
        val game = Fake()
        Addons.installZip(context, zip("Good/Good.toc" to "## Title: Good\n", "Good/../../evil.txt" to "no"), game)
        assertFalse(File(game.client, "evil.txt").exists())
        assertFalse(File(game.client, "Interface/evil.txt").exists())
        assertTrue(File(game.client, "Interface/AddOns/Good/Good.toc").isFile)
    }

    @Test
    fun deletingAFolderNameThatLeadsOutDoesNothing() {
        val game = Fake()
        val keep = File(game.client, "Interface/keep").also { it.mkdirs() }
        assertFalse(Addons.delete(context, "../keep", game))
        assertTrue(keep.isDirectory)
    }

    @Test
    fun recordsAreKeptNextToTheClientNotInAddOns() {
        val game = Fake()
        val record = AddonRecord("questie", "Questie", "1.2", "2026-10-12", null, listOf("Questie"), 1L)
        Addons.updateRecords(context, game) { AddonRecords.put(it, record) }
        assertEquals(listOf(record), Addons.records(context, game))
        assertTrue(game.recordsFile(context).isFile)
        assertFalse(game.recordsFile(context).path.contains("Interface"))
        Addons.updateRecords(context, game) { it.filterNot { r -> r.slug == "questie" } }
        assertEquals(emptyList<AddonRecord>(), Addons.records(context, game))
    }

    @Test
    fun theThreeGamesKnowTheirSectionAndInterface() {
        assertEquals(Warperia.Flavor.WOTLK, WowAddonGames.of("wow")?.flavor)
        assertEquals("30300", WowAddonGames.of("wow")?.interfaceVersion)
        assertEquals(Warperia.Flavor.LEGION, WowAddonGames.of("wow_legion")?.flavor)
        assertEquals("70300", WowAddonGames.of("wow_legion")?.interfaceVersion)
        assertEquals(Warperia.Flavor.VANILLA, WowAddonGames.of("wow_octowow")?.flavor)
        assertEquals("11200", WowAddonGames.of("wow_octowow")?.interfaceVersion)
        assertNull(WowAddonGames.of("wow_forever"))
        assertNotNull(WowAddonStores.of("wow_octowow"))
        assertNull(WowAddonStores.of("diablo2"))
        assertTrue("wowtouch" in WowAddonGames.WRATH.ownFolders)
    }

    @Test
    fun noClientImportedMeansNoClient() {
        // Nothing was imported in this test app: no client, and the folders are under the game's own folder.
        assertFalse(WowAddonGames.WRATH.hasClient(context))
        assertFalse(WowAddonGames.LEGION.hasClient(context))
        assertFalse(WowAddonGames.OCTOWOW.hasClient(context))
        assertTrue(WowAddonGames.LEGION.client(context).path.endsWith("games/wow_legion/files/felsong/client"))
        assertTrue(WowAddonGames.OCTOWOW.client(context).path.endsWith("games/wow_octowow/files/turtle/client"))
        assertTrue(WowAddonGames.WRATH.client(context).path.endsWith("games/wow/files/client"))
    }
}
