package com.logie.blizz.wrathpp

import com.logie.blizz.wowclient.Blp
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

/** Ralia's mod on Wrath++ ([WrathppRalia]): the zip taken in, its skins put in place of the looks' they are named for, taken out again. */
@RunWith(RobolectricTestRunner::class)
class WrathppRaliaTest {
    @get:Rule val tmp = TemporaryFolder()

    /** A body texture as today's game has them: twice as wide as tall, the body's half one colour, the other half another. */
    private fun body(r: Int, g: Int, b: Int): ByteArray {
        val w = 64; val h = 32
        val rgba = ByteArray(w * h * 4)
        for (y in 0 until h) for (x in 0 until w) {
            val at = (y * w + x) * 4
            if (x < w / 2) { rgba[at] = r.toByte(); rgba[at + 1] = g.toByte(); rgba[at + 2] = b.toByte() }
            rgba[at + 3] = 255.toByte()
        }
        return Blp.writePalette(Blp.Image(w, h, rgba), mips = false)
    }

    /** A piece laid over a skin (underwear), with its alpha: nothing of it showing ([alpha] 0), or painted. */
    private fun piece(r: Int, g: Int, b: Int, alpha: Int, w: Int = 32, h: Int = 16): ByteArray {
        val rgba = ByteArray(w * h * 4)
        for (i in 0 until w * h) { rgba[i * 4] = r.toByte(); rgba[i * 4 + 1] = g.toByte(); rgba[i * 4 + 2] = b.toByte(); rgba[i * 4 + 3] = alpha.toByte() }
        return Blp.writePalette(Blp.Image(w, h, rgba), mips = false, alpha = true)
    }

    private fun zip(entries: Map<String, ByteArray>): File = tmp.newFile().also { f ->
        ZipOutputStream(f.outputStream()).use { z -> for ((n, t) in entries) { z.putNextEntry(ZipEntry(n)); z.write(t); z.closeEntry() } }
    }

    private val set = mapOf(
        "Ralia/Character/Human/Female/humanfemaleskin00_03_hd.blp" to body(200, 150, 120),
        "Ralia/Character/Scourge/Female/ScourgeFemaleSkin00_01_HD.blp" to body(120, 140, 130),
        "Ralia/Character/Human/Female/humanfemalenakedpelvisskin00_03_hd.blp" to piece(0, 0, 0, 0),
        "Ralia/readme.txt" to "hello".toByteArray(),
        "Ralia/Interface/icon.blp" to body(1, 2, 3),
    )

    private fun row(id: Int, race: Int, sex: Int, section: Int, a: String, b: String, colour: Int): Array<Any> = arrayOf(id, race, sex, section, a, b, "", 17, 0, colour)

    private fun game(names: Boolean = true): File {
        val client = tmp.newFolder("client-wrathpp")
        val patch = File(client, "Data/patch-Z.MPQ")
        File(patch, "DBFilesClient").mkdirs()
        val table = WrathppUndead.Dbc(WrathppUndead.KINDS, mutableListOf(
            row(1, 1, 1, 0, "Character\\Human\\Female\\HumanFemaleSkin00_00.blp", "", 0), row(2, 1, 1, 0, "Character\\Human\\Female\\HumanFemaleSkin00_01.blp", "", 1),
            row(3, 1, 1, 4, "HF\\Pelvis00.blp", "HF\\Torso00.blp", 0), row(4, 1, 1, 4, "HF\\Pelvis01.blp", "HF\\Torso01.blp", 1),
            row(5, 5, 1, 0, "Character\\Scourge\\Female\\ScourgeFemaleSkin00_00.blp", "", 0), row(6, 5, 1, 4, "SF\\Pelvis00.blp", "", 0),
            row(7, 2, 0, 4, "OM\\Pelvis00.blp", "", 0),
            row(8, 5, 0, 0, "Character\\Scourge\\Male\\ScourgeMaleSkin00_00.blp", "", 0),
            row(9, 5, 0, 4, "Character\\Scourge\\Male\\ScourgeMaleNakedPelvisSkin00_00.blp", "", 0)))
        File(patch, "DBFilesClient/CharSections.dbc").writeBytes(table.write())
        File(patch, WrathppLooks.MARKER).writeText("looks1\n")
        for (name in listOf("Human/Female/HumanFemaleSkin00_00", "Human/Female/HumanFemaleSkin00_01", "Scourge/Female/ScourgeFemaleSkin00_00", "Scourge/Male/ScourgeMaleSkin00_00")) {
            File(patch, "Character/$name.blp").apply { parentFile!!.mkdirs(); writeText("the looks' own $name") }
        }
        File(patch, "Character/Scourge/Male/ScourgeMaleNakedPelvisSkin00_00.blp").writeBytes(piece(9, 9, 9, 255, w = 16, h = 8))
        // the looks' second human skin was made from today's skin 03, the Forsaken's first from today's 01; the first human skin from one the set hasn't
        if (names) File(patch, WrathppRalia.NAMES).writeText("""{"format": 1, "models": {
            "1_1": {"name": "HumanFemale", "race": 1, "sex": 1, "skins": [
                {"index": 0, "path": "Character\\Human\\Female\\HumanFemaleSkin00_00.blp", "retail": "humanfemaleskin00_00_hd.blp"},
                {"index": 1, "path": "Character\\Human\\Female\\HumanFemaleSkin00_01.blp", "retail": "humanfemaleskin00_03_hd.blp"}]},
            "5_1": {"name": "ScourgeFemale", "race": 5, "sex": 1, "skins": [
                {"index": 0, "path": "Character\\Scourge\\Female\\ScourgeFemaleSkin00_00.blp", "retail": "scourgefemaleskin00_01_hd.blp"}]},
            "5_0": {"name": "ScourgeMale", "race": 5, "sex": 0, "skins": [
                {"index": 0, "path": "Character\\Scourge\\Male\\ScourgeMaleSkin00_00.blp", "retail": "scourgemaleskin00_00_hd.blp"}]}}}""")
        return client
    }

    private fun rows(client: File) = WrathppUndead.Dbc.read(File(client, "Data/patch-Z.MPQ/DBFilesClient/CharSections.dbc").readBytes(), WrathppUndead.KINDS).rows

    @Test fun theZipsCharacterTexturesAreKept() {
        val store = File(tmp.root, "store")
        assertEquals(3, zip(set).inputStream().use { WrathppRalia.importZip(store, it) })
        assertTrue(WrathppRalia.installed(store))
        assertEquals(setOf("humanfemaleskin00_03_hd.blp", "scourgefemaleskin00_01_hd.blp", "humanfemalenakedpelvisskin00_03_hd.blp"), File(store, "files").list()!!.toSet())
        try { zip(mapOf("notes.txt" to ByteArray(3))).inputStream().use { WrathppRalia.importZip(store, it) }; fail("taken") } catch (_: IOException) { }
        assertEquals(3, WrathppRalia.count(store))                                  // what was there is kept
    }

    @Test fun skinsTheSetHasTakeItsAndGoBack() {
        val store = File(tmp.root, "store")
        val client = game()
        val patch = File(client, "Data/patch-Z.MPQ")
        val before = File(patch, "DBFilesClient/CharSections.dbc").readBytes()
        assertEquals(0, WrathppRalia.apply(store, client))                          // nothing imported: nothing done
        zip(set).inputStream().use { WrathppRalia.importZip(store, it) }
        assertEquals(2, WrathppRalia.apply(store, client))
        // the human's second skin and the Forsaken's first are the set's body half, as a 512 x 512 palettized skin
        val human = Blp.read(File(patch, "Character/Human/Female/HumanFemaleSkin00_01.blp").readBytes())
        assertEquals(512, human.width); assertEquals(512, human.height)
        assertEquals(listOf(200, 150, 120), (0 until 3).map { human.rgba[(300 * 512 + 500) * 4 + it].toInt() and 255 })
        val forsaken = Blp.read(File(patch, "Character/Scourge/Female/ScourgeFemaleSkin00_00.blp").readBytes())
        assertEquals(listOf(120, 140, 130), (0 until 3).map { forsaken.rgba[it].toInt() and 255 })
        // the skin the set hasn't is the looks' own still
        assertEquals("the looks' own Human/Female/HumanFemaleSkin00_00", File(patch, "Character/Human/Female/HumanFemaleSkin00_00.blp").readText())
        // their underwear rows keep their place and lose their pictures; every other row as it was
        val r = rows(client)
        assertEquals(listOf("", ""), r.first { it[0] == 4 }.let { listOf(it[4], it[5]) })
        assertEquals("", r.first { it[0] == 6 }[4])
        assertEquals("HF\\Pelvis00.blp", r.first { it[0] == 3 }[4])
        assertEquals("OM\\Pelvis00.blp", r.first { it[0] == 7 }[4])
        assertEquals(9, r.size)
        // again: nothing to do
        val written = File(patch, "Character/Human/Female/HumanFemaleSkin00_01.blp").lastModified()
        assertEquals(2, WrathppRalia.apply(store, client))
        assertEquals(written, File(patch, "Character/Human/Female/HumanFemaleSkin00_01.blp").lastModified())
        // taken out: the looks' own skins and table
        WrathppRalia.remove(store)
        assertEquals(0, WrathppRalia.apply(store, client))
        assertEquals("the looks' own Human/Female/HumanFemaleSkin00_01", File(patch, "Character/Human/Female/HumanFemaleSkin00_01.blp").readText())
        assertArrayEquals(before, File(patch, "DBFilesClient/CharSections.dbc").readBytes())
        assertFalse(patch.walkTopDown().any { it.name.endsWith(".orig") || it.name == WrathppRalia.STAMP })
    }

    private fun solid(r: Int, g: Int, b: Int, w: Int = 64, h: Int = 64): ByteArray {
        val rgba = ByteArray(w * h * 4)
        for (i in 0 until w * h) { rgba[i * 4] = r.toByte(); rgba[i * 4 + 1] = g.toByte(); rgba[i * 4 + 2] = b.toByte(); rgba[i * 4 + 3] = 255.toByte() }
        return Blp.writePalette(Blp.Image(w, h, rgba), mips = false)
    }

    private fun pixel(file: File, at: Int = 0) = Blp.read(file.readBytes()).let { i -> (0 until 3).map { i.rgba[at * 4 + it].toInt() and 255 } }

    @Test fun aSkinTheSetHasNotTakesTheNearestOnesCarriedOver() {
        val store = File(tmp.root, "store")
        val client = game()
        val patch = File(client, "Data/patch-Z.MPQ")
        // the looks' own pictures: the human's second skin (the set's 03) grey, her first blue; an undead skin beside them
        val first = File(patch, "Character/Human/Female/HumanFemaleSkin00_00.blp")
        val undead = File(patch, "Character/Scourge/Female/ScourgeFemaleSkinUndead00_01.blp")
        first.writeBytes(solid(50, 100, 200))
        File(patch, "Character/Human/Female/HumanFemaleSkin00_01.blp").writeBytes(solid(100, 100, 100))
        File(patch, "Character/Scourge/Female/ScourgeFemaleSkin00_00.blp").writeBytes(solid(90, 110, 100))
        undead.writeBytes(solid(60, 70, 80))
        val table = File(patch, "DBFilesClient/CharSections.dbc")
        val dbc = WrathppUndead.Dbc.read(table.readBytes(), WrathppUndead.KINDS)
        dbc.rows.add(row(10, 5, 1, 0, "Character\\Scourge\\Female\\ScourgeFemaleSkinUndead00_01.blp", "", 1))
        table.writeBytes(dbc.write())
        val before = table.readBytes()
        val ownFirst = first.readBytes()
        val ownUndead = undead.readBytes()
        zip(set).inputStream().use { WrathppRalia.importZip(store, it) }
        assertEquals(3, WrathppRalia.apply(store, client))
        // the first skin: the set's 03 (200 150 120) times blue over grey, channel by channel ((c + 8) / (100 + 8))
        assertEquals(listOf(107, 150, 231), pixel(first, 300 * 512 + 500))
        // her underwear goes as the 03's does (the set's women: none)
        assertEquals(listOf("", ""), rows(client).first { it[0] == 3 }.let { listOf(it[4], it[5]) })
        // the undead skin stays the looks' own
        assertArrayEquals(ownUndead, undead.readBytes())
        // taken out: all back
        WrathppRalia.remove(store)
        assertEquals(0, WrathppRalia.apply(store, client))
        assertArrayEquals(ownFirst, first.readBytes())
        assertArrayEquals(before, table.readBytes())
    }

    @Test fun carriedKeepsTheSetsDetailAndTheOthersColourAndPaint() {
        fun image(vararg px: Int) = Blp.Image(2, 1, ByteArray(8) { px[it].toByte() })
        val set = image(200, 100, 50, 255, 40, 40, 40, 128)
        val from = image(100, 100, 100, 255, 100, 100, 100, 255)
        val to = image(100, 100, 100, 255, 46, 46, 46, 255)       // the other: the same, but for a dark stroke on the second pixel
        val out = WrathppRalia.carried(set, from, to)
        assertEquals(listOf(200, 100, 50, 255), (0 until 4).map { out.rgba[it].toInt() and 255 })     // alike: the set's own
        assertEquals(listOf(20, 20, 20, 128), (4 until 8).map { out.rgba[it].toInt() and 255 })      // the stroke laid on, the set's alpha kept
        val white = WrathppRalia.carried(image(200, 200, 200, 255, 0, 0, 0, 0), image(0, 0, 0, 255, 0, 0, 0, 0), image(255, 255, 255, 255, 0, 0, 0, 0))
        assertEquals(255, white.rgba[0].toInt() and 255)                                           // capped, never past white
    }

    @Test fun paintedUnderwearGoesOverTheLooksOwnAndBack() {
        // the set has no body for the Forsaken men, and their underwear painted: a pelvis the looks have a file for, a torso they don't
        val store = File(tmp.root, "store")
        val client = game()
        val patch = File(client, "Data/patch-Z.MPQ")
        val before = File(patch, "DBFilesClient/CharSections.dbc").readBytes()
        val own = File(patch, "Character/Scourge/Male/ScourgeMaleNakedPelvisSkin00_00.blp")
        val ownBytes = own.readBytes()
        zip(mapOf("Character/Scourge/male/scourgemalenakedpelvisskin00_00_hd.blp" to piece(100, 90, 80, 255),
            "Character/Scourge/male/scourgemalenakedtorsoskin00_00_hd.blp" to piece(10, 20, 30, 200))).inputStream().use { WrathppRalia.importZip(store, it) }
        assertEquals(1, WrathppRalia.apply(store, client))
        val pelvis = Blp.read(own.readBytes())
        assertEquals(16 to 8, pelvis.width to pelvis.height)                         // the size the looks' own is
        assertEquals(listOf(100, 90, 80, 255), (0 until 4).map { pelvis.rgba[it].toInt() and 255 })
        val row = rows(client).first { it[0] == 9 }
        assertEquals("Character\\Scourge\\Male\\ScourgeMaleNakedPelvisSkin00_00.blp", row[4])
        assertEquals("Character\\Scourge\\Male\\Ralia_scourgemalenakedtorsoskin00_00.blp", row[5])
        val torso = Blp.read(File(patch, "Character/Scourge/Male/Ralia_scourgemalenakedtorsoskin00_00.blp").readBytes())
        assertEquals(256 to 128, torso.width to torso.height)
        assertEquals(200, torso.rgba[3].toInt() and 255)                             // with its alpha
        assertEquals("the looks' own Scourge/Male/ScourgeMaleSkin00_00", File(patch, "Character/Scourge/Male/ScourgeMaleSkin00_00.blp").readText())   // no body in the set: the looks'
        WrathppRalia.remove(store)
        assertEquals(0, WrathppRalia.apply(store, client))
        assertArrayEquals(ownBytes, own.readBytes())
        assertArrayEquals(before, File(patch, "DBFilesClient/CharSections.dbc").readBytes())
        assertFalse(File(patch, "Character/Scourge/Male/Ralia_scourgemalenakedtorsoskin00_00.blp").exists())
    }

    @Test fun anotherSetReplacesTheFirst() {
        val store = File(tmp.root, "store")
        val client = game()
        zip(set).inputStream().use { WrathppRalia.importZip(store, it) }
        WrathppRalia.apply(store, client)
        zip(mapOf("Character/Human/Female/humanfemaleskin00_00_hd.blp" to body(10, 20, 30))).inputStream().use { WrathppRalia.importZip(store, it) }
        assertEquals(1, WrathppRalia.apply(store, client))
        val patch = File(client, "Data/patch-Z.MPQ")
        assertEquals(512, Blp.read(File(patch, "Character/Human/Female/HumanFemaleSkin00_00.blp").readBytes()).width)
        assertEquals("the looks' own Human/Female/HumanFemaleSkin00_01", File(patch, "Character/Human/Female/HumanFemaleSkin00_01.blp").readText())
        assertEquals("HF\\Pelvis01.blp", rows(client).first { it[0] == 4 }[4])
        assertEquals("", rows(client).first { it[0] == 3 }[4])
    }

    @Test fun looksWithoutTheirListOfNamesAreLeftAlone() {
        val store = File(tmp.root, "store")
        val client = game(names = false)
        zip(set).inputStream().use { WrathppRalia.importZip(store, it) }
        assertEquals(0, WrathppRalia.apply(store, client))
        assertEquals("the looks' own Human/Female/HumanFemaleSkin00_01", File(client, "Data/patch-Z.MPQ/Character/Human/Female/HumanFemaleSkin00_01.blp").readText())
    }

    @Test fun theZipFoundIsTakenInByItselfOnceAndNeverAfterRemove() {
        val store = File(tmp.root, "store")
        val found = zip(set)
        assertNull(WrathppRalia.lookFor(store, null))
        assertEquals(3, WrathppRalia.lookFor(store, found))
        assertNull(WrathppRalia.lookFor(store, found))                              // the same file: not again
        // another file under the name: taken in its place
        ZipOutputStream(found.outputStream()).use { z -> z.putNextEntry(ZipEntry("Character/Orc/Male/orcmaleskin00_00_hd.blp")); z.write(body(1, 2, 3)); z.closeEntry() }
        assertEquals(1, WrathppRalia.lookFor(store, found))
        // one picked by hand stays, whatever is in Download
        zip(set).inputStream().use { WrathppRalia.importZip(store, it) }
        assertNull(WrathppRalia.lookFor(store, found))
        assertEquals(3, WrathppRalia.count(store))
        // removed: not looked for again, until one is picked
        WrathppRalia.remove(store)
        assertNull(WrathppRalia.lookFor(store, found))
        assertFalse(WrathppRalia.installed(store))
        zip(set).inputStream().use { WrathppRalia.importZip(store, it) }
        WrathppRalia.remove(store)
        zip(set).inputStream().use { WrathppRalia.importZip(store, it) }
        assertTrue(WrathppRalia.installed(store))
    }

    @Test fun aFileIsFoundByItsName() {
        val downloads = tmp.newFolder("Download"); val documents = tmp.newFolder("Documents")
        assertNull(ImportFinder.find(listOf(downloads, documents), listOf("ralia.zip")))
        File(documents, "Ralia.ZIP").writeText("x")
        assertEquals("Ralia.ZIP", ImportFinder.find(listOf(downloads, documents, File(tmp.root, "none")), listOf("ralia.zip"))!!.name)
        File(downloads, "ralia.zip").writeText("y")
        assertEquals(downloads, ImportFinder.find(listOf(downloads, documents), listOf("ralia.zip", "other.zip"))!!.parentFile)
    }
}
