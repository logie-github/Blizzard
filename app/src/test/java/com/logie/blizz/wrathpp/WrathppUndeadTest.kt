package com.logie.blizz.wrathpp

import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import java.io.File
import java.io.IOException
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

/**
 * The undead skins' import ([WrathppUndead]): the zip taken in, its skins added to the looks' table as new colours, taken
 * out again. (Robolectric: the manifest is read with Android's org.json, which is only a stub in a plain unit test.)
 */
@RunWith(RobolectricTestRunner::class)
class WrathppUndeadTest {
    @get:Rule val tmp = TemporaryFolder()

    private val manifest = """{"format": 1, "kind": "wrathpp-undead-skins", "models": {
        "1_1": {"race": 1, "sex": 1, "name": "HumanFemale", "underwear": "none", "skins": [
            {"name": "Grave Blue", "swatch": 7833770, "skin": "Character\\Human\\Female\\HumanFemaleSkinUndead00_00.blp", "face": "Character\\Human\\Female\\HumanFemaleFaceLowerUndead00.blp"},
            {"name": "Ash", "swatch": 10066329, "skin": "Character\\Human\\Female\\HumanFemaleSkinUndead00_01.blp", "face": "Character\\Human\\Female\\HumanFemaleFaceLowerUndead01.blp"}]},
        "2_0": {"race": 2, "sex": 0, "name": "OrcMale", "underwear": "race", "skins": [
            {"name": "Bog", "swatch": 7833702, "skin": "Character\\Orc\\Male\\OrcMaleSkinUndead00_00.blp", "face": "Character\\Orc\\Male\\OrcMaleFaceLowerUndead00.blp"}]},
        "7_0": {"race": 7, "sex": 0, "name": "GnomeMale", "underwear": "race", "skins": [
            {"name": "Dusk", "swatch": 1, "skin": "Character\\Gnome\\Male\\GnomeMaleSkinUndead00_00.blp", "face": "Character\\Gnome\\Male\\GnomeMaleFaceLowerUndead00.blp"}]}}}"""

    private val textures = listOf("Human/Female/HumanFemaleSkinUndead00_00", "Human/Female/HumanFemaleFaceLowerUndead00", "Human/Female/HumanFemaleSkinUndead00_01",
        "Human/Female/HumanFemaleFaceLowerUndead01", "Orc/Male/OrcMaleSkinUndead00_00", "Orc/Male/OrcMaleFaceLowerUndead00",
        "Gnome/Male/GnomeMaleSkinUndead00_00", "Gnome/Male/GnomeMaleFaceLowerUndead00")

    private fun zip(manifest: String?, names: List<String> = textures, extra: Map<String, String> = emptyMap()): File = tmp.newFile().also { f ->
        ZipOutputStream(f.outputStream()).use { z ->
            fun put(n: String, t: String) { z.putNextEntry(ZipEntry(n)); z.write(t.toByteArray()); z.closeEntry() }
            if (manifest != null) put("manifest.json", manifest)
            for (n in names) put("client/Character/$n.blp", "blp of $n")
            for ((n, t) in extra) put(n, t)
        }
    }

    private fun row(id: Int, race: Int, sex: Int, section: Int, a: String, b: String, flags: Int, variation: Int, colour: Int): Array<Any> =
        arrayOf(id, race, sex, section, a, b, "", flags, variation, colour)

    /** A human woman with two skins and two faces x two eye colours, an orc man with one skin, a tauren (not in the import). */
    private fun table() = WrathppUndead.Dbc(WrathppUndead.KINDS, mutableListOf(
        row(1, 1, 1, 0, "HF\\Skin00.blp", "HF\\Skin00_Extra.blp", 17, 0, 0), row(2, 1, 1, 0, "HF\\Skin01.blp", "", 17, 0, 1),
        row(3, 1, 1, 4, "HF\\Pelvis00.blp", "HF\\Torso00.blp", 17, 0, 0), row(4, 1, 1, 4, "HF\\Pelvis01.blp", "HF\\Torso01.blp", 17, 0, 1),
        row(5, 1, 1, 1, "HF\\FaceLowerA.blp", "HF\\FaceUpper00.blp", 1, 0, 0), row(6, 1, 1, 1, "HF\\FaceLowerA.blp", "HF\\FaceUpper01.blp", 1, 1, 0),
        row(7, 1, 1, 1, "HF\\FaceLowerB.blp", "HF\\FaceUpper00.blp", 1, 2, 0), row(8, 1, 1, 1, "HF\\FaceLowerB.blp", "HF\\FaceUpper01.blp", 1, 3, 0),
        row(9, 1, 1, 1, "HF\\FaceLowerA1.blp", "HF\\FaceUpper00.blp", 1, 0, 1), row(10, 1, 1, 3, "HF\\Hair00.blp", "", 17, 0, 0),
        row(11, 2, 0, 0, "OM\\Skin00.blp", "", 17, 0, 0), row(12, 2, 0, 4, "OM\\Pelvis00.blp", "", 17, 0, 0), row(13, 2, 0, 1, "OM\\FaceLower.blp", "OM\\FaceUpper00.blp", 1, 0, 0),
        row(14, 6, 0, 0, "TM\\Skin00.blp", "", 17, 0, 0), row(15, 6, 0, 1, "TM\\Face.blp", "", 1, 0, 0)))

    @Test fun aTableReadsBackAsWritten() {
        val bytes = table().write()
        assertEquals("WDBC", String(bytes, 0, 4))
        val again = WrathppUndead.Dbc.read(bytes, WrathppUndead.KINDS)
        assertEquals(15, again.rows.size)
        assertArrayEquals(table().rows[5], again.rows[5])
        assertArrayEquals(bytes, again.write())
    }

    @Test fun skinsBecomeNewColoursAfterTheRacesOwn() {
        val t = table()
        val before = t.rows.map { it.toList() }
        val first = WrathppUndead.withUndead(t, WrathppUndead.parseManifest(manifest))
        assertEquals(mapOf("1_1" to 2, "2_0" to 1), first)                         // the gnome: no skins of his in the table, left out
        // nothing of the game's own changed or went
        assertEquals(before, t.rows.take(before.size).map { it.toList() })
        val human = t.rows.filter { it[1] == 1 && it[2] == 1 }
        assertEquals(listOf(0, 1, 2, 3), human.filter { it[3] == 0 }.map { it[9] })
        assertEquals("Character\\Human\\Female\\HumanFemaleSkinUndead00_01.blp", human.first { it[3] == 0 && it[9] == 3 }[4])
        // the race's skin extra (the parts drawn on the skin's second texture, as the Forsaken's bones) kept on each new colour
        assertEquals(listOf("HF\\Skin00_Extra.blp", "HF\\Skin00_Extra.blp"), human.filter { it[3] == 0 && (it[9] as Int) >= 2 }.map { it[5] })
        // a face row for every face number, with that number's own eyes, on each new colour
        val faces = human.filter { it[3] == 1 && it[9] == 2 }
        assertEquals(listOf(0, 1, 2, 3), faces.map { it[8] })
        assertEquals(listOf("HF\\FaceUpper00.blp", "HF\\FaceUpper01.blp", "HF\\FaceUpper00.blp", "HF\\FaceUpper01.blp"), faces.map { it[5] })
        assertTrue(faces.all { it[4] == "Character\\Human\\Female\\HumanFemaleFaceLowerUndead00.blp" && it[7] == 1 })
        // underwear: a row each colour (the game won't offer a colour without one); hers with no picture, his the race's own
        assertEquals(listOf("", ""), human.filter { it[3] == 4 && (it[9] as Int) >= 2 }.map { it[4] })
        val orc = t.rows.filter { it[1] == 2 && it[3] == 4 && it[9] == 1 }
        assertEquals(listOf("OM\\Pelvis00.blp"), orc.map { it[4] })
        assertEquals(t.rows.size, t.rows.map { it[0] }.toSet().size)                // ids of their own
        assertEquals(2, t.rows.count { it[1] == 6 })                                // the tauren as he was
    }

    @Test fun appliedAgainOrTakenOutLeavesNoneTwice() {
        val t = table()
        val models = WrathppUndead.parseManifest(manifest)
        WrathppUndead.withUndead(t, models)
        val once = t.rows.size
        assertEquals(mapOf("1_1" to 2, "2_0" to 1), WrathppUndead.withUndead(t, models))
        assertEquals(once, t.rows.size)
        WrathppUndead.withUndead(t, emptyList())
        assertEquals(table().rows.map { it.toList() }, t.rows.map { it.toList() })
    }

    @Test fun theZipIsTakenIn() {
        val store = File(tmp.root, "store")
        val models = zip(manifest, extra = mapOf("readme.txt" to "hello", "client/evil.exe" to "x")).inputStream().use { WrathppUndead.importZip(store, it) }
        assertEquals(listOf("1_1", "2_0", "7_0"), models.map { it.key })
        assertTrue(WrathppUndead.installed(store))
        assertEquals(64, WrathppUndead.sha(store)!!.length)
        assertTrue(File(store, "client/Character/Orc/Male/OrcMaleSkinUndead00_00.blp").isFile)
        assertFalse(File(store, "readme.txt").exists())
        assertFalse(File(store, "client/evil.exe").exists())
    }

    @Test fun aZipThatIsntOneIsRefusedAndWhatWasThereKept() {
        val store = File(tmp.root, "store")
        zip(manifest).inputStream().use { WrathppUndead.importZip(store, it) }
        val sha = WrathppUndead.sha(store)
        for (bad in listOf(zip(null), zip("""{"format": 1, "kind": "something else", "models": {}}"""), zip(manifest, names = textures.drop(1)),
            zip(manifest, extra = mapOf("client/../../escape.blp" to "x")))) {
            try { bad.inputStream().use { WrathppUndead.importZip(store, it) }; fail("taken") } catch (_: IOException) { }
            assertEquals(sha, WrathppUndead.sha(store))
        }
    }

    private fun game(): Pair<File, File> {
        val client = tmp.newFolder("client-wrathpp")
        val server = tmp.newFolder("server-wrathpp")
        val bytes = table().write()
        File(client, "Data/patch-Z.MPQ/DBFilesClient").mkdirs()
        File(client, "Data/patch-Z.MPQ/DBFilesClient/CharSections.dbc").writeBytes(bytes)
        File(client, "Data/patch-Z.MPQ/${WrathppLooks.MARKER}").writeText("looks1\n")
        File(server, "share/dbc").mkdirs()
        File(server, "share/dbc/CharSections.dbc").writeBytes(bytes)
        return client to server
    }

    @Test fun appliedToTheLooksAndTakenOut() {
        val store = File(tmp.root, "store")
        val (client, server) = game()
        assertNull(WrathppUndead.apply(store, client, server))                     // nothing imported: nothing done
        zip(manifest).inputStream().use { WrathppUndead.importZip(store, it) }
        val lua = WrathppUndead.apply(store, client, server)!!
        assertTrue(lua.contains("""["1_1"] = { first = 2, skins = { { n = "Grave Blue", s = 7833770 }, { n = "Ash", s = 10066329 } } }"""))
        assertTrue(lua.contains("""["2_0"] = { first = 1"""))
        assertFalse(lua.contains("7_0"))
        val patch = File(client, "Data/patch-Z.MPQ")
        assertEquals("blp of Orc/Male/OrcMaleSkinUndead00_00", File(patch, "Character/Orc/Male/OrcMaleSkinUndead00_00.blp").readText())
        assertEquals(lua, File(patch, "Interface/GlueXML/WrathppUndead.lua").readText())
        val gameTable = File(patch, "DBFilesClient/CharSections.dbc").readBytes()
        assertArrayEquals(gameTable, File(server, "share/dbc/CharSections.dbc").readBytes())   // the server checks a new character by the same rows
        assertEquals(4, WrathppUndead.Dbc.read(gameTable, WrathppUndead.KINDS).rows.count { it[1] == 1 && it[3] == 0 })
        // again: nothing to do, the same answer
        val stamp = File(patch, WrathppUndead.STAMP).lastModified()
        assertEquals(lua, WrathppUndead.apply(store, client, server))
        assertEquals(stamp, File(patch, WrathppUndead.STAMP).lastModified())
        // new looks (their tables whole again, the stamp gone with the patch): put in again
        val fresh = table().write()
        File(patch, "DBFilesClient/CharSections.dbc").writeBytes(fresh)
        File(patch, WrathppLooks.MARKER).writeText("looks2\n")
        assertEquals(lua, WrathppUndead.apply(store, client, server))
        assertEquals(4, WrathppUndead.Dbc.read(File(patch, "DBFilesClient/CharSections.dbc").readBytes(), WrathppUndead.KINDS).rows.count { it[1] == 1 && it[3] == 0 })
        // removed: the tables as the looks made them
        WrathppUndead.remove(store)
        assertNull(WrathppUndead.apply(store, client, server))
        assertArrayEquals(fresh, File(patch, "DBFilesClient/CharSections.dbc").readBytes())
        assertArrayEquals(fresh, File(server, "share/dbc/CharSections.dbc").readBytes())
        assertFalse(File(patch, "Interface/GlueXML/WrathppUndead.lua").exists())
    }

    @Test fun withoutTheLooksNothingIsTouched() {
        val store = File(tmp.root, "store")
        zip(manifest).inputStream().use { WrathppUndead.importZip(store, it) }
        val client = tmp.newFolder("client-wrathpp"); val server = tmp.newFolder("server-wrathpp")
        assertNull(WrathppUndead.apply(store, client, server))
        assertFalse(File(client, "Data").exists())
    }
}
