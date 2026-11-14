package com.logie.blizz.wrathpp

import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import java.io.File
import java.io.IOException
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.security.MessageDigest
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

/** Body shapes on Wrath++ ([WrathppBody]): the zip taken in, a preset put over the looks' model it was made for, taken out again. */
@RunWith(RobolectricTestRunner::class)
class WrathppBodyTest {
    @get:Rule val tmp = TemporaryFolder()

    private fun sha(b: ByteArray) = MessageDigest.getInstance("SHA-256").digest(b).joinToString("") { "%02x".format(it) }

    /** A small 3.3.5 model: its header (MD20, the vertices' count at 60 and offset at 64), then [n] vertices. */
    private fun model(n: Int, fill: Int): ByteArray {
        val head = 80
        val b = ByteBuffer.allocate(head + n * 48 + 5).order(ByteOrder.LITTLE_ENDIAN)
        b.put("MD20".toByteArray()); b.putInt(4, 264)
        b.putInt(60, n); b.putInt(64, head)
        for (i in 0 until n * 48) b.put(head + i, (fill + i).toByte())
        return b.array()
    }

    private fun block(n: Int, fill: Int) = ByteArray(n * 48) { (fill + it).toByte() }

    private fun zip(entries: Map<String, ByteArray>): File = tmp.newFile().also { f ->
        ZipOutputStream(f.outputStream()).use { z -> for ((n, t) in entries) { z.putNextEntry(ZipEntry(n)); z.write(t); z.closeEntry() } }
    }

    private val looksModel = model(3, 1)
    private val looksSkin = "SKIN-looks".toByteArray()
    private val skin = "SKIN-finer".toByteArray()
    private val curvy = block(5, 40)
    private val petite = block(5, 90)

    private fun list(looksSha: String = sha(looksModel)) = JSONObject()
        .put("format", 1).put("kind", "wrathpp-body").put("default", "Curvy")
        .put("presets", JSONArray(listOf("Petite", "Curvy")))
        .put("models", JSONArray().put(JSONObject()
            .put("race", "Human").put("model", "Character/Human/Female/HumanFemale.m2").put("skin", "Character/Human/Female/HumanFemale00.skin")
            .put("looks_sha256", looksSha).put("looks_vertices", 3)
            .put("skin_file", "Human/HumanFemale00.skin").put("skin_sha256", sha(skin))
            .put("blocks", JSONObject()
                .put("Petite", JSONObject().put("file", "Human/Petite.vtx").put("vertices", 5).put("sha256", sha(petite)))
                .put("Curvy", JSONObject().put("file", "Human/Curvy.vtx").put("vertices", 5).put("sha256", sha(curvy))))))

    private fun bodyZip(l: JSONObject = list(), extra: Map<String, ByteArray> = emptyMap()) = zip(mapOf(
        "wrathpp-body.json" to l.toString().toByteArray(),
        "Human/HumanFemale00.skin" to skin,
        "Human/Petite.vtx" to petite,
        "Human/Curvy.vtx" to curvy,
    ) + extra)

    private fun game(): File {
        val client = tmp.newFolder("client-wrathpp")
        val dir = File(client, "Data/patch-Z.MPQ/Character/Human/Female").apply { mkdirs() }
        File(dir, "HumanFemale.m2").writeBytes(looksModel)
        File(dir, "HumanFemale00.skin").writeBytes(looksSkin)
        File(client, "Data/patch-Z.MPQ/${WrathppLooks.MARKER}").writeText("looks1\n")
        return client
    }

    private fun m2(client: File) = File(client, "Data/patch-Z.MPQ/Character/Human/Female/HumanFemale.m2")
    private fun skinFile(client: File) = File(client, "Data/patch-Z.MPQ/Character/Human/Female/HumanFemale00.skin")

    @Test fun theModelKeepsItselfAndNamesTheNewVerticesAtItsEnd() {
        val out = WrathppBody.withVertices(looksModel, curvy)
        val b = ByteBuffer.wrap(out).order(ByteOrder.LITTLE_ENDIAN)
        val at = b.getInt(64)
        assertEquals(5, b.getInt(60))
        assertEquals(0, at % 16)
        assertTrue(at >= looksModel.size)
        assertArrayEquals(curvy, out.copyOfRange(at, at + curvy.size))
        // all else of the model as it was
        for (i in looksModel.indices) if (i !in 60 until 68) assertEquals("byte $i", looksModel[i], out[i])
    }

    @Test fun aPresetGoesOverTheLooksAndAsDrawnPutsThemBack() {
        val store = File(tmp.root, "store")
        val client = game()
        assertEquals(1, bodyZip().inputStream().use { WrathppBody.importZip(store, it) })
        assertEquals("Curvy", WrathppBody.chosen(store))            // the zip's default
        assertEquals("Human: Curvy", WrathppBody.apply(store, client))
        assertArrayEquals(WrathppBody.withVertices(looksModel, curvy), m2(client).readBytes())
        assertArrayEquals(skin, skinFile(client).readBytes())
        // the same again: nothing to do
        val before = m2(client).lastModified()
        WrathppBody.apply(store, client)
        assertEquals(before, m2(client).lastModified())
        // another preset: from the looks' own, not over the last one
        WrathppBody.choose(store, "Petite")
        assertEquals("Human: Petite", WrathppBody.apply(store, client))
        assertArrayEquals(WrathppBody.withVertices(looksModel, petite), m2(client).readBytes())
        // As drawn: the looks' own back, nothing left beside them
        WrathppBody.choose(store, WrathppBody.AS_DRAWN)
        assertEquals("as drawn", WrathppBody.apply(store, client))
        assertArrayEquals(looksModel, m2(client).readBytes())
        assertArrayEquals(looksSkin, skinFile(client).readBytes())
        assertFalse(File(m2(client).path + ".body-orig").exists())
    }

    @Test fun removedTheLooksOwnAreBackAndTheZipIsNotLookedForAgain() {
        val store = File(tmp.root, "store")
        val client = game()
        val z = bodyZip()
        assertEquals(1, WrathppBody.lookFor(store, z))
        WrathppBody.apply(store, client)
        WrathppBody.remove(store)
        assertEquals("none imported", WrathppBody.apply(store, client))
        assertArrayEquals(looksModel, m2(client).readBytes())
        assertEquals(null, WrathppBody.lookFor(store, z))
    }

    @Test fun otherLooksAreLeftAsTheyAre() {
        val store = File(tmp.root, "store")
        val client = game()
        bodyZip(list(looksSha = "0".repeat(64))).inputStream().use { WrathppBody.importZip(store, it) }
        assertEquals("Human: made for other looks, left as drawn", WrathppBody.apply(store, client))
        assertArrayEquals(looksModel, m2(client).readBytes())
        assertArrayEquals(looksSkin, skinFile(client).readBytes())
    }

    @Test fun newLooksTakeThePresetAgain() {
        val store = File(tmp.root, "store")
        val client = game()
        bodyZip().inputStream().use { WrathppBody.importZip(store, it) }
        WrathppBody.apply(store, client)
        // the looks put in again (WrathppLooks swaps the whole folder): their own model, a new stamp
        val dir = File(client, "Data/patch-Z.MPQ").apply { deleteRecursively() }
        File(dir, "Character/Human/Female").mkdirs()
        m2(client).writeBytes(looksModel); skinFile(client).writeBytes(looksSkin)
        File(dir, WrathppLooks.MARKER).writeText("looks2\n")
        assertEquals("Human: Curvy", WrathppBody.apply(store, client))
        assertArrayEquals(WrathppBody.withVertices(looksModel, curvy), m2(client).readBytes())
    }

    @Test fun damagedOrForeignZipsAreRefusedAndTheStoreKept() {
        val store = File(tmp.root, "store")
        bodyZip().inputStream().use { WrathppBody.importZip(store, it) }
        val bad = listOf(
            zip(mapOf("readme.txt" to "hi".toByteArray())),
            bodyZip(extra = mapOf("../escape.txt" to ByteArray(1))),
            zip(mapOf("wrathpp-body.json" to list().toString().toByteArray(), "Human/HumanFemale00.skin" to skin, "Human/Petite.vtx" to petite, "Human/Curvy.vtx" to block(5, 41))),
        )
        for (z in bad) {
            try { z.inputStream().use { WrathppBody.importZip(store, it) }; fail("taken: $z") } catch (e: IOException) { /* refused */ }
            assertTrue(WrathppBody.installed(store))
            assertEquals(listOf("Human"), WrathppBody.races(store))
        }
    }
}
