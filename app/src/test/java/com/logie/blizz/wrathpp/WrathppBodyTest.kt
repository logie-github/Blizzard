package com.logie.blizz.wrathpp

import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
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

/**
 * Body options on Wrath++ ([WrathppBody]): the package taken in; the race's own model with the layer in place of the
 * looks', a body shape's beside it with the race's animations under its name, the designs in the race's folder, and the
 * display rows in the game's and the realm's tables; taken out again.
 */
@RunWith(RobolectricTestRunner::class)
class WrathppBodyTest {
    @get:Rule val tmp = TemporaryFolder()

    private fun sha(b: ByteArray) = MessageDigest.getInstance("SHA-256").digest(b).joinToString("") { "%02x".format(it) }

    /** A 3.3.5 model as far as this goes: MD20, a header of 0x138 bytes, then [n] bytes. */
    private fun model(n: Int, fill: Int) = ByteArray(0x138 + n) { (fill + it).toByte() }.also { "MD20".toByteArray().copyInto(it) }

    /** A patch of [base]: its header with [mark] at 0x40, then [tail]. */
    private fun patchOf(base: ByteArray, mark: Int, tail: ByteArray) = base.copyOf(0x138).also { it[0x40] = mark.toByte() } + tail

    private fun dbc(kinds: String, rows: List<Array<Any>>) = WrathppUndead.Dbc(kinds, rows.toMutableList()).write()

    private fun zip(entries: Map<String, ByteArray>): File = tmp.newFile().also { f ->
        ZipOutputStream(f.outputStream()).use { z -> for ((n, t) in entries) { z.putNextEntry(ZipEntry(n)); z.write(t); z.closeEntry() } }
    }

    private val looksModel = model(37, 1)
    private val looksSkin = "SKIN-looks".toByteArray()
    private val ownPatch = patchOf(looksModel, 7, ByteArray(40) { (it + 3).toByte() })
    private val petitePatch = patchOf(looksModel, 9, ByteArray(56) { (it + 5).toByte() })
    private val ownSkin = "SKIN-with-the-layer".toByteArray()
    private val shapeSkin = "SKIN-shapes".toByteArray()
    private val styles = (1..16).map { "d$it" }

    private fun entry(file: String, bytes: ByteArray) = JSONObject().put("file", file).put("sha256", sha(bytes)).put("size", bytes.size)

    private fun designBytes(name: String, d: Int) = "BLP2 $name $d".toByteArray()

    private fun list(looksSha: String = sha(looksModel), format: Int = 2): JSONObject {
        val textures = JSONArray()
        for (name in styles + "horde1") for (d in 1..4) textures.put(entry("designs/${name}_$d.blp", designBytes(name, d)).put("design", name).put("density", d))
        textures.put(entry("designs/none.blp", designBytes("", 0)).put("design", "").put("density", 0))
        return JSONObject().put("format", format).put("kind", "wrathpp-body")
            .put("shapes", JSONArray(listOf("As drawn", "Petite", "Curvy", "Voluptuous")))
            .put("styles", JSONObject().put("alliance", JSONArray(styles)).put("horde", JSONArray(styles.dropLast(1) + "horde1")))
            .put("races", JSONArray().put(JSONObject().put("race", "Human").put("race_id", 1).put("folder", "Character/Human/Female").put("faction", "alliance")))
            .put("models", JSONArray()
                .put(JSONObject().put("race", "Human").put("shape", 0).put("model", "Character/Human/Female/HumanFemale.m2").put("skin", "Character/Human/Female/HumanFemale00.skin")
                    .put("looks_sha256", looksSha).put("made_sha256", sha(WrathppBody.withPatch(looksModel, ownPatch)))
                    .put("patch", entry("Human/0.patch", ownPatch)).put("skin_file", entry("Human/0.skin", ownSkin)))
                .put(JSONObject().put("race", "Human").put("shape", 1).put("model", "Character/Human/Female/HumanFemaleWpp1.m2").put("skin", "Character/Human/Female/HumanFemaleWpp100.skin")
                    .put("anims_of", "Character/Human/Female/HumanFemale")
                    .put("looks_sha256", looksSha).put("made_sha256", sha(WrathppBody.withPatch(looksModel, petitePatch)))
                    .put("patch", entry("Human/1.patch", petitePatch)).put("skin_file", entry("Human/shapes.skin", shapeSkin))))
            .put("textures", textures)
    }

    private fun bodyZip(l: JSONObject = list(), extra: Map<String, ByteArray> = emptyMap()): File {
        val files = HashMap<String, ByteArray>()
        files["wrathpp-body.json"] = l.toString().toByteArray()
        files["Human/0.patch"] = ownPatch; files["Human/1.patch"] = petitePatch
        files["Human/0.skin"] = ownSkin; files["Human/shapes.skin"] = shapeSkin
        for (name in styles + "horde1") for (d in 1..4) files["designs/${name}_$d.blp"] = designBytes(name, d)
        files["designs/none.blp"] = designBytes("", 0)
        return zip(files + extra)
    }

    private val displayKinds = WrathppBody.DISPLAY_KINDS
    private fun displayRow(id: Int, model: Int): Array<Any> = arrayOf(id, model, 0, 13750, 0x3f800000, 255, "", "", "", "", 1, 0, 0, 0, 0, 0)
    private fun modelRow(id: Int, name: String): Array<Any> = arrayOf<Any>(id, 0, name, *Array<Any>(25) { 0 })

    private lateinit var server: File
    private lateinit var data: File

    private fun game(): File {
        val client = tmp.newFolder("client-wrathpp")
        val dir = File(client, "Data/patch-Z.MPQ/Character/Human/Female").apply { mkdirs() }
        File(dir, "HumanFemale.m2").writeBytes(looksModel)
        File(dir, "HumanFemale00.skin").writeBytes(looksSkin)
        File(dir, "HumanFemale0060-00.anim").writeText("stand")
        File(client, "Data/patch-Z.MPQ/${WrathppLooks.MARKER}").writeText("looks1\n")
        // the game's own tables (in the realm's modules' patch, a folder the game reads like an archive)
        val tables = File(client, "Data/patch-M.MPQ/DBFilesClient").apply { mkdirs() }
        val chr = ByteBuffer.allocate(20 + 2 * 24).order(ByteOrder.LITTLE_ENDIAN)
        chr.put("WDBC".toByteArray()).putInt(2).putInt(6).putInt(24).putInt(0)
        chr.putInt(1).putInt(12).putInt(1).putInt(0).putInt(49).putInt(50)
        chr.putInt(2).putInt(12).putInt(2).putInt(0).putInt(51).putInt(52)
        File(tables, "ChrRaces.dbc").writeBytes(chr.array())
        File(tables, "CreatureDisplayInfo.dbc").writeBytes(dbc(displayKinds, listOf(displayRow(49, 3), displayRow(50, 4), displayRow(52, 6))))
        File(tables, "CreatureModelData.dbc").writeBytes(dbc(WrathppBody.MODEL_KINDS, listOf(modelRow(4, "Character\\Human\\Female\\HumanFemale.mdx"))))
        server = tmp.newFolder("server-wrathpp")
        File(server, "share/dbc").mkdirs()
        File(server, "share/dbc/CreatureDisplayInfo.dbc").writeBytes(dbc(displayKinds, listOf(displayRow(50, 4), displayRow(52, 6))))
        data = tmp.newFolder("data")
        return client
    }

    private fun female(client: File) = File(client, "Data/patch-Z.MPQ/Character/Human/Female")
    private fun table(file: File, kinds: String) = WrathppUndead.Dbc.read(file.readBytes(), kinds).rows.associateBy { it[0] as Int }

    @Test fun aPatchKeepsTheModelAndPutsWhatItAddsAtTheEnd() {
        val out = WrathppBody.withPatch(looksModel, ownPatch)
        val at = (looksModel.size + 15) / 16 * 16
        assertArrayEquals(ownPatch.copyOf(0x138), out.copyOf(0x138))
        assertArrayEquals(looksModel.copyOfRange(0x138, looksModel.size), out.copyOfRange(0x138, looksModel.size))
        assertArrayEquals(ownPatch.copyOfRange(0x138, ownPatch.size), out.copyOfRange(at, out.size))
        assertEquals(WrathppBody.DISPLAY_BASE + 9 * 260 + 2 * 65 + 1 + 15 * 4 + 2, WrathppBody.displayId(9, 2, 1 + 15 * 4 + 2))
    }

    @Test fun thePackageGoesInWithItsModelsDesignsAndDisplaysAndComesOutAgain() {
        val store = File(tmp.root, "store")
        val client = game()
        assertEquals(2, bodyZip().inputStream().use { WrathppBody.importZip(store, it) })
        val said = WrathppBody.apply(store, client, server, data)
        assertTrue(said, said.startsWith("Human (1 shapes); 1 races' displays"))
        val f = female(client)
        // the race's own model with the layer, the looks' own kept beside it
        assertArrayEquals(WrathppBody.withPatch(looksModel, ownPatch), File(f, "HumanFemale.m2").readBytes())
        assertArrayEquals(ownSkin, File(f, "HumanFemale00.skin").readBytes())
        assertArrayEquals(looksModel, File(f, "HumanFemale.m2.body-orig").readBytes())
        // the shape's model beside it, the race's animations under its name
        assertArrayEquals(WrathppBody.withPatch(looksModel, petitePatch), File(f, "HumanFemaleWpp1.m2").readBytes())
        assertArrayEquals(shapeSkin, File(f, "HumanFemaleWpp100.skin").readBytes())
        assertEquals("stand", File(f, "HumanFemaleWpp10060-00.anim").readText())
        // the designs: the sixteenth the faction's, and the empty one
        assertArrayEquals(designBytes("d3", 2), File(f, "WppLayer_3_2.blp").readBytes())
        assertArrayEquals(designBytes("d16", 4), File(f, "WppLayer_16_4.blp").readBytes())
        assertArrayEquals(designBytes("", 0), File(f, "WppLayer_0.blp").readBytes())
        // the game's tables: every shape and layer of the race, the shape's own model where it has one
        val displays = table(File(client, "Data/patch-Z.MPQ/DBFilesClient/CreatureDisplayInfo.dbc"), displayKinds)
        assertEquals(3 + 260, displays.size)
        assertEquals(WrathppBody.EMPTY, displays[50]!![6])
        assertEquals("", displays[52]!![6])
        assertEquals(4, displays[WrathppBody.displayId(0, 0, 7)]!![1])
        assertEquals("WppLayer_2_3", displays[WrathppBody.displayId(0, 0, 7)]!![6])
        assertEquals(WrathppBody.modelId(0, 1), displays[WrathppBody.displayId(0, 1, 0)]!![1])
        assertEquals(WrathppBody.EMPTY, displays[WrathppBody.displayId(0, 1, 0)]!![6])
        assertEquals(4, displays[WrathppBody.displayId(0, 2, 64)]!![1])
        assertEquals("WppLayer_16_4", displays[WrathppBody.displayId(0, 3, 64)]!![6])
        val models = table(File(client, "Data/patch-Z.MPQ/DBFilesClient/CreatureModelData.dbc"), WrathppBody.MODEL_KINDS)
        assertEquals("Character\\Human\\Female\\HumanFemaleWpp1.mdx", models[WrathppBody.modelId(0, 1)]!![2])
        // the realm's: the same displays, each with the race's model
        val realm = table(File(server, "share/dbc/CreatureDisplayInfo.dbc"), displayKinds)
        assertEquals(2 + 260, realm.size)
        assertEquals(4, realm[WrathppBody.displayId(0, 1, 0)]!![1])
        // the same again: nothing to do
        val before = File(f, "HumanFemale.m2").lastModified()
        WrathppBody.apply(store, client, server, data)
        assertEquals(before, File(f, "HumanFemale.m2").lastModified())
        // removed: the looks' own back, nothing of this left, the realm's table as it was
        WrathppBody.remove(store)
        assertEquals("none imported", WrathppBody.apply(store, client, server, data))
        assertArrayEquals(looksModel, File(f, "HumanFemale.m2").readBytes())
        assertArrayEquals(looksSkin, File(f, "HumanFemale00.skin").readBytes())
        for (name in listOf("HumanFemale.m2.body-orig", "HumanFemaleWpp1.m2", "HumanFemaleWpp100.skin", "HumanFemaleWpp10060-00.anim", "WppLayer_0.blp", "WppLayer_3_2.blp")) {
            assertFalse(name, File(f, name).exists())
        }
        assertFalse(File(client, "Data/patch-Z.MPQ/DBFilesClient/CreatureDisplayInfo.dbc").exists())
        assertEquals(setOf(50, 52), table(File(server, "share/dbc/CreatureDisplayInfo.dbc"), displayKinds).keys)
        assertEquals(null, WrathppBody.lookFor(store, bodyZip()))
    }

    @Test fun theLooksOwnDisplaysAndModelsStayWhenTheBodyRowsGoOverThem() {
        // the allied races' rows (CreatureDisplayInfo 33001, its model 3601) are in the looks' tables: the crash at Create Character
        // (issue 272) was the game's own table made over them, which took them out
        val store = File(tmp.root, "store")
        val client = game()
        val patchTables = File(client, "Data/patch-Z.MPQ/DBFilesClient").apply { mkdirs() }
        val looksDisplays = dbc(displayKinds, listOf(displayRow(49, 3), displayRow(50, 4), displayRow(52, 6), displayRow(33001, 3601)))
        val looksModels = dbc(WrathppBody.MODEL_KINDS, listOf(modelRow(4, "Character\\Human\\Female\\HumanFemale.mdx"), modelRow(3601, "Character\\VoidElf\\Male\\VoidElfMale.mdx")))
        File(patchTables, "CreatureDisplayInfo.dbc").writeBytes(looksDisplays)
        File(patchTables, "CreatureModelData.dbc").writeBytes(looksModels)
        assertEquals(2, bodyZip().inputStream().use { WrathppBody.importZip(store, it) })
        WrathppBody.apply(store, client, server, data)
        val displays = table(File(patchTables, "CreatureDisplayInfo.dbc"), displayKinds)
        assertEquals(3601, displays[33001]!![1])
        assertEquals(WrathppBody.EMPTY, displays[50]!![6])
        assertTrue(displays.containsKey(WrathppBody.displayId(0, 1, 0)))
        val models = table(File(patchTables, "CreatureModelData.dbc"), WrathppBody.MODEL_KINDS)
        assertEquals("Character\\VoidElf\\Male\\VoidElfMale.mdx", models[3601]!![2])
        // removed: the looks' own tables back, byte for byte
        WrathppBody.remove(store)
        WrathppBody.apply(store, client, server, data)
        assertArrayEquals(looksDisplays, File(patchTables, "CreatureDisplayInfo.dbc").readBytes())
        assertArrayEquals(looksModels, File(patchTables, "CreatureModelData.dbc").readBytes())
    }

    @Test fun aModelIsNamedByStructureWithoutWhereItsVerticesAre() {
        fun withVertices(x: Float): ByteArray {
            val b = ByteArray(0x138 + 2 * 48 + 16) { it.toByte() }
            "MD20".toByteArray().copyInto(b)
            ByteBuffer.wrap(b).order(ByteOrder.LITTLE_ENDIAN).putInt(60, 2).putInt(64, 0x138).putFloat(0x138, x).putFloat(0x138 + 48 + 4, x * 3)
            return b
        }
        // looks whose hair was pushed out a little differently: the same model but for where some vertices are
        assertEquals(WrathppBody.structSha256(withVertices(1f)), WrathppBody.structSha256(withVertices(2f)))
        assertFalse(sha(withVertices(1f)) == sha(withVertices(2f)))
        // anything else (a vertex's normal, the bytes after the array) is the model
        val changed = withVertices(1f).also { it[0x138 + 20] = 99 }
        assertFalse(WrathppBody.structSha256(changed) == WrathppBody.structSha256(withVertices(1f)))
        val tail = withVertices(1f).also { it[it.size - 1] = 99 }
        assertFalse(WrathppBody.structSha256(tail) == WrathppBody.structSha256(withVertices(1f)))
        // a model made by a patch keeps the looks' old array where it was: with the looks' own positions in it, which the name leaves out
        fun looksWith(x: Float) = withVertices(x)
        val patch = ByteArray(0x138 + 2 * 48 + 16) { (it * 7).toByte() }.also { "MD20".toByteArray().copyInto(it) }
        val newArrayAt = ((0x138 + 2 * 48 + 16) + 15) / 16 * 16 + 0x138
        ByteBuffer.wrap(patch).order(ByteOrder.LITTLE_ENDIAN).putInt(60, 2).putInt(64, newArrayAt)
        val made1 = WrathppBody.withPatch(looksWith(1f), patch)
        val made2 = WrathppBody.withPatch(looksWith(2f), patch)
        assertFalse(sha(made1) == sha(made2))
        assertEquals(WrathppBody.structSha256(made1, looksWith(1f)), WrathppBody.structSha256(made2, looksWith(2f)))
        // a header that names no vertex array inside the file: the model whole
        val junk = model(37, 1)
        assertEquals(sha(junk), WrathppBody.structSha256(junk))
    }

    @Test fun otherLooksAreLeftAsTheyAre() {
        val store = File(tmp.root, "store")
        val client = game()
        bodyZip(list(looksSha = "0".repeat(64))).inputStream().use { WrathppBody.importZip(store, it) }
        val said = WrathppBody.apply(store, client, server, data)
        assertTrue(said, said.contains("Human: made for other looks, left as drawn"))
        assertArrayEquals(looksModel, File(female(client), "HumanFemale.m2").readBytes())
        assertFalse(File(female(client), "HumanFemaleWpp1.m2").exists())
        assertFalse(File(female(client), "WppLayer_0.blp").exists())
        assertEquals(setOf(50, 52), table(File(server, "share/dbc/CreatureDisplayInfo.dbc"), displayKinds).keys)
    }

    @Test fun looksThePackageWasNotMadeForGetTheLayerMadeOnThePhone() {
        // (one import lasts: a looks release changed her model; the package says how her layer lies, and the layer is made
        // on the looks' own model and skin)
        val store = File(tmp.root, "store")
        val client = game()
        val looks = WrathppBodyLayerTest.model()
        val skin = WrathppBodyLayerTest.skin()
        File(female(client), "HumanFemale.m2").writeBytes(looks); File(female(client), "HumanFemale00.skin").writeBytes(skin)
        val l = list(looksSha = "0".repeat(64))
        l.getJSONArray("races").getJSONObject(0).put("layer", JSONObject().put("k", 1.0).put("fold", 1.0).put("body", JSONArray(listOf(0))).put("hair_block", JSONArray(listOf(4, 3))))
        bodyZip(l).inputStream().use { WrathppBody.importZip(store, it) }
        val said = WrathppBody.apply(store, client, server, data)
        assertTrue(said, said.contains("made here for these looks (the package was made for others): Human"))
        val made = WrathppBodyLayer.add(looks, skin, null, WrathppBodyLayer.Params(1.0, 1.0, setOf(0), intArrayOf(4, 3)), "Character\\Human\\Female")
        assertArrayEquals(made.model, File(female(client), "HumanFemale.m2").readBytes())
        assertArrayEquals(made.skin, File(female(client), "HumanFemale00.skin").readBytes())
        assertArrayEquals(designBytes("", 0), File(female(client), "WppLayer_0.blp").readBytes())
        assertFalse("her shape, made for another body, is not carried", File(female(client), "HumanFemaleWpp1.m2").exists())
        // her displays are in all the same: a style at every shape, on her own model
        val displays = table(File(client, "Data/patch-Z.MPQ/DBFilesClient/CreatureDisplayInfo.dbc"), displayKinds)
        assertEquals(4, displays[WrathppBody.displayId(0, 1, 7)]!![1])
        assertEquals("WppLayer_2_3", displays[WrathppBody.displayId(0, 1, 7)]!![6])
        // looks without room for the layer's indices: she is left as drawn, and the report says why
        WrathppBody.remove(store)
        WrathppBody.apply(store, client, server, data)
        assertArrayEquals(looks, File(female(client), "HumanFemale.m2").readBytes())
        File(female(client), "HumanFemale00.skin").writeBytes(WrathppBodyLayerTest.skin(WrathppBodyLayer.MAX_INDICES - 9 - 5))
        bodyZip(l).inputStream().use { WrathppBody.importZip(store, it) }
        val full = WrathppBody.apply(store, client, server, data)
        assertTrue(full, full.contains("Human: made for other looks, and these leave the layer no room (5 indices free, 6 needed): left as drawn"))
        assertArrayEquals(looks, File(female(client), "HumanFemale.m2").readBytes())
    }

    @Test fun aRaceDrawnWithAnothersFilesGetsItsOwnDisplaysOfThatOnesModels() {
        // (the High Elf is drawn with the Void Elf's files: here race 2 with the Human's)
        val store = File(tmp.root, "store")
        val client = game()
        val l = list()
        l.getJSONArray("races").put(JSONObject().put("race", "Other").put("race_id", 2).put("files", "Human").put("folder", "Character/Human/Female").put("faction", "horde"))
        bodyZip(l).inputStream().use { WrathppBody.importZip(store, it) }
        assertTrue(WrathppBody.apply(store, client, server, data).contains("2 races' displays"))
        val displays = table(File(client, "Data/patch-Z.MPQ/DBFilesClient/CreatureDisplayInfo.dbc"), displayKinds)
        assertEquals("her own display's model", 6, displays[WrathppBody.displayId(1, 0, 7)]!![1])
        assertEquals("WppLayer_2_3", displays[WrathppBody.displayId(1, 0, 7)]!![6])
        assertEquals(WrathppBody.EMPTY, displays[52]!![6])
        assertNotNull(table(File(server, "share/dbc/CreatureDisplayInfo.dbc"), displayKinds)[WrathppBody.displayId(1, 0, 1)])
    }

    @Test fun theDisplaysOfEveryRaceStayClearOfTheModelVariants() {
        // (the base was 42000, whose eighth slot ran into the variants' displays at 44000: WrathppVariants)
        assertEquals(23, WrathppBody.RACES.size)
        assertEquals(WrathppBody.RACES.size, WrathppBody.RACES.toSet().size)
        assertEquals(listOf(1, 2, 3, 4, 5, 6, 7, 8, 10, 11), WrathppBody.RACES.take(10))
        assertTrue(WrathppBody.displayId(0, 0, 0) > 44000 + 6 * 16)
        assertEquals(45000 + 22 * 260 + 3 * 65 + 64, WrathppBody.displayId(22, 3, 64))
    }

    @Test fun aPatchesVerticesAreFoundInThePatchItself() {
        // the model a patch makes of a base of 0x150 bytes has its vertex array after the base's end: read from the patch alone
        val base = ByteArray(0x150)
        val records = ByteArray(3 * 48) { (it % 251).toByte() }
        val head = ByteBuffer.allocate(0x138).order(ByteOrder.LITTLE_ENDIAN)
        head.put("MD20".toByteArray()); head.putInt(60, 3); head.putInt(64, 0x150 + 32)
        val patch = head.array() + ByteArray(32) + records
        assertArrayEquals(records.copyOf(96), WrathppBody.patchVertices(patch, base.size, 2))
        try { WrathppBody.patchVertices(patch, base.size, 4); fail("more vertices than the patch has") } catch (e: IOException) { }
        try { WrathppBody.patchVertices(patch, 0x1000, 2); fail("another base") } catch (e: IOException) { }
    }

    @Test fun newLooksTakeThePackageAgain() {
        val store = File(tmp.root, "store")
        val client = game()
        bodyZip().inputStream().use { WrathppBody.importZip(store, it) }
        WrathppBody.apply(store, client, server, data)
        // the looks put in again (WrathppLooks swaps the whole folder, and the realm's tables with it)
        val dir = File(client, "Data/patch-Z.MPQ").apply { deleteRecursively() }
        female(client).mkdirs()
        File(female(client), "HumanFemale.m2").writeBytes(looksModel); File(female(client), "HumanFemale00.skin").writeBytes(looksSkin)
        File(dir, WrathppLooks.MARKER).writeText("looks2\n")
        File(server, "share/dbc/CreatureDisplayInfo.dbc").writeBytes(dbc(displayKinds, listOf(displayRow(50, 4))))
        File(server, "share/dbc/${WrathppBody.STAMP}").delete()
        assertTrue(WrathppBody.apply(store, client, server, data).startsWith("Human (1 shapes)"))
        assertArrayEquals(WrathppBody.withPatch(looksModel, ownPatch), File(female(client), "HumanFemale.m2").readBytes())
        assertNotNull(table(File(server, "share/dbc/CreatureDisplayInfo.dbc"), displayKinds)[WrathppBody.displayId(0, 0, 1)])
    }

    @Test fun theGameTablesChangedTheCopyIsMadeAgainTheCreatorPatchChangedItIsNot() {
        val store = File(tmp.root, "store")
        val client = game()
        bodyZip().inputStream().use { WrathppBody.importZip(store, it) }
        WrathppBody.apply(store, client, server, data)
        val copy = File(client, "Data/patch-Z.MPQ/DBFilesClient/CreatureDisplayInfo.dbc")
        // the creator's patch written again (at every Play): nothing to do
        File(client, "Data/patch-X.MPQ").writeText("creator")
        val before = copy.lastModified()
        Thread.sleep(20)
        WrathppBody.apply(store, client, server, data)
        assertEquals(before, copy.lastModified())
        // a part that changes the game's table (a Reforged part, the realm modules' patch): made again from it
        File(client, "Data/patch-M.MPQ/DBFilesClient/CreatureDisplayInfo.dbc").writeBytes(dbc(displayKinds, listOf(displayRow(49, 3), displayRow(50, 4), displayRow(52, 6), displayRow(99, 7))))
        WrathppBody.apply(store, client, server, data)
        val displays = table(copy, displayKinds)
        assertEquals(7, displays[99]!![1])
        assertEquals(WrathppBody.EMPTY, displays[50]!![6])
        assertEquals(4 + 260, displays.size)
    }

    @Test fun anOlderPackageOnThePhoneIsTakenOutAndCountsAsNone() {
        val store = File(tmp.root, "store")
        val client = game()
        // what the held menu's body shapes left: their own store, a preset over the looks' model, the looks' own beside it
        File(store, "files").mkdirs()
        File(store, "files/wrathpp-body.json").writeText(JSONObject().put("format", 1).put("kind", "wrathpp-body").put("models", JSONArray()).toString())
        File(store, WrathppBody.STAMP).writeText("abc\n")
        val f = female(client)
        File(f, "HumanFemale.m2").copyTo(File(f, "HumanFemale.m2.body-orig"))
        File(f, "HumanFemale.m2").writeBytes(model(5, 9))
        assertFalse(WrathppBody.installed(store))
        assertTrue(WrathppBody.older(store))
        assertTrue(WrathppBody.apply(store, client, server, data).startsWith("an older package"))
        assertArrayEquals(looksModel, File(f, "HumanFemale.m2").readBytes())
        assertFalse(File(f, "HumanFemale.m2.body-orig").exists())
        // the new one found where downloads are is taken in by itself
        assertEquals(2, WrathppBody.lookFor(store, bodyZip()))
        assertTrue(WrathppBody.apply(store, client, server, data).startsWith("Human (1 shapes)"))
    }

    @Test fun theStartReportCarriesTheRealmsWrathppLines() {
        val log = tmp.newFile("Server.log")
        log.writeText((1..3000).joinToString("\n") { "line $it" } + "\nWrath++: registry version 2, 5 categories, hash be0f63ec\nother\nWrath++: account 1 client speaks protocol 1 (capabilities 0x1)\n")
        assertEquals("Wrath++: registry version 2, 5 categories, hash be0f63ec\nWrath++: account 1 client speaks protocol 1 (capabilities 0x1)", WrathppSetup.realmLines(log))
        assertEquals("no nothing.log", WrathppSetup.realmLines(File(tmp.root, "nothing.log")))
    }

    @Test fun damagedForeignOrOlderPackagesAreRefusedAndTheStoreKept() {
        val store = File(tmp.root, "store")
        bodyZip().inputStream().use { WrathppBody.importZip(store, it) }
        val bad = listOf(
            zip(mapOf("readme.txt" to "hi".toByteArray())),
            bodyZip(extra = mapOf("../escape.txt" to ByteArray(1))),
            bodyZip(extra = mapOf("Human/1.patch" to petitePatch + 1)),
            bodyZip(extra = mapOf("designs/d4_2.blp" to "other".toByteArray())),
            bodyZip(list(format = 1)),
        )
        for (z in bad) {
            try { z.inputStream().use { WrathppBody.importZip(store, it) }; fail("taken: $z") } catch (e: IOException) { /* refused */ }
            assertTrue(WrathppBody.installed(store))
            assertEquals(listOf("Human"), WrathppBody.races(store))
        }
    }
}
