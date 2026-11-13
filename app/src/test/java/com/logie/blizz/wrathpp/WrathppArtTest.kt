package com.logie.blizz.wrathpp

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
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

/** Shadowlands' creator art put into Wrath++'s copy of the game ([WrathppArt.install]) and given to the creator's patch. */
class WrathppArtTest {
    @get:Rule val tmp = TemporaryFolder()

    private fun zip(entries: Map<String, String>): File = tmp.newFile().also { f ->
        ZipOutputStream(f.outputStream()).use { z -> for ((n, t) in entries) { z.putNextEntry(ZipEntry(n)); z.write(t.toByteArray()); z.closeEntry() } }
    }

    private val good = mapOf(
        "client/Interface/Wrathpp/Creator/charactercreate-icon-dice.blp" to "dice",
        "client/Interface/GlueXML/WrathppAtlas.lua" to "WrathppAtlas = {}",
        "art.txt" to "list",
    )

    private fun client(): File = tmp.newFolder("client-wrathpp").also {
        File(it, "Data/patch-W.MPQ").apply { parentFile!!.mkdirs(); writeText("alternative hd") }
    }

    @Test fun installsTheArtAsAPatchOfItsOwn() {
        val client = client()
        assertNull(WrathppArt.installedSha(client)); assertNull(WrathppArt.atlas(client))
        WrathppArt.install(client, zip(good), "abc")
        assertEquals("dice", File(client, "Data/patch-S.MPQ/Interface/Wrathpp/Creator/charactercreate-icon-dice.blp").readText())
        assertEquals("abc", WrathppArt.installedSha(client))
        assertEquals("WrathppAtlas = {}", WrathppArt.atlas(client)!!.readText())
        // what is not the game's stays out; the rest of the game as it was; nothing left beside
        assertFalse(File(client, "Data/patch-S.MPQ/art.txt").exists())
        assertEquals("alternative hd", File(client, "Data/patch-W.MPQ").readText())
        assertFalse(File(client, "Data/patch-S.MPQ.new").exists()); assertFalse(File(client, "Data/patch-S.MPQ.old").exists())
    }

    @Test fun aNewerPackageReplacesTheOldOneWhole() {
        val client = client()
        WrathppArt.install(client, zip(good + ("client/Interface/Wrathpp/Creator/old.blp" to "old")), "one")
        WrathppArt.install(client, zip(good), "two")
        assertFalse(File(client, "Data/patch-S.MPQ/Interface/Wrathpp/Creator/old.blp").exists())
        assertEquals("two", WrathppArt.installedSha(client))
    }

    @Test fun aPackageWithoutItsTableOrWithAPathOutOfItLeavesWhatWasThere() {
        val client = client()
        WrathppArt.install(client, zip(good), "one")
        for (bad in listOf(good - "client/Interface/GlueXML/WrathppAtlas.lua", good + ("client/../../escape.txt" to "x"))) {
            try { WrathppArt.install(client, zip(bad), "two"); fail("installed") } catch (e: IOException) { /* refused */ }
            assertEquals("one", WrathppArt.installedSha(client))
            assertEquals("dice", File(client, "Data/patch-S.MPQ/Interface/Wrathpp/Creator/charactercreate-icon-dice.blp").readText())
            assertFalse(File(client, "Data/patch-S.MPQ.new").exists())
        }
        assertFalse(File(tmp.root, "escape.txt").exists())
    }

    @Test fun aFileOfTheGamesByThatNameIsReplacedInTheCopyOnly() {
        // a patch-S of the player's own, linked or copied into Wrath++'s copy: the art takes its place there
        val client = client()
        File(client, "Data/patch-S.MPQ").writeText("the player's own")
        WrathppArt.install(client, zip(good), "abc")
        assertTrue(File(client, "Data/patch-S.MPQ").isDirectory)
        assertEquals("abc", WrathppArt.installedSha(client))
    }

    @Test fun theCreatorsPatchTakesTheTableWhenTheArtIsIn() {
        val client = client()
        val without = WrathppSetup.glue("creator".toByteArray(), client, null)
        assertEquals(listOf("WrathppCreate.lua"), without.keys.toList())
        WrathppArt.install(client, zip(good), "abc")
        val with = WrathppSetup.glue("creator".toByteArray(), client, null)
        assertNotNull(with[WrathppArt.ATLAS])
        assertEquals("WrathppAtlas = {}", with[WrathppArt.ATLAS]!!.toString(Charsets.UTF_8))
    }
}
