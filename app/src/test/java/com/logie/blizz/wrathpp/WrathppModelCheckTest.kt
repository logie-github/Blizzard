package com.logie.blizz.wrathpp

import java.io.File
import java.io.IOException
import java.nio.ByteBuffer
import java.nio.ByteOrder
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder

/** Each race display's model in the looks' patch, held to the package ([WrathppModelCheck]). */
class WrathppModelCheckTest {
    @get:Rule val tmp = TemporaryFolder()

    private fun table(fields: Int, rows: List<IntArray>, text: ByteArray = byteArrayOf(0)): ByteArray {
        val b = ByteBuffer.allocate(20 + rows.size * fields * 4 + text.size).order(ByteOrder.LITTLE_ENDIAN)
        b.putInt(0x43424457); b.putInt(rows.size); b.putInt(fields); b.putInt(fields * 4); b.putInt(text.size)
        for (r in rows) for (i in 0 until fields) b.putInt(r.getOrElse(i) { 0 })
        b.put(text)
        return b.array()
    }

    /** CreatureModelData: [models] (id to path), 28 columns, the path the third. */
    private fun modelTable(models: List<Pair<Int, String>>): ByteArray {
        val text = java.io.ByteArrayOutputStream().apply { write(0) }
        val rows = models.map { (id, path) -> intArrayOf(id, 0, text.size()).also { text.write(path.toByteArray()); text.write(0) } }
        return table(28, rows, text.toByteArray())
    }

    /** A model file of [bones] bones and [vertices] vertices (version 264), [cut] bytes short of what its header names. */
    private fun model(bones: Int, vertices: Int, cut: Int = 0): ByteArray {
        val bonesAt = 0x130; val verticesAt = bonesAt + bones * 88
        val b = ByteBuffer.allocate(verticesAt + vertices * 48 - cut).order(ByteOrder.LITTLE_ENDIAN)
        b.put("MD20".toByteArray()); b.putInt(4, 264)
        b.putInt(0x2C, bones); b.putInt(0x30, bonesAt); b.putInt(0x3C, vertices); b.putInt(0x40, verticesAt); b.putInt(0x44, 1)
        return b.array()
    }

    private val troll = model(231, 40)
    private val trollWoman = model(150, 30)

    /** A copy of the game whose looks' patch names the Troll man and woman (race 8: displays 1478, 1479; models 1, 2). */
    private fun client(withSizes: Boolean = true): File {
        val client = tmp.newFolder("client")
        val patch = File(client, "Data/${WrathppLooks.PATCH}")
        val dir = File(patch, "DBFilesClient").also { it.mkdirs() }
        File(dir, "ChrRaces.dbc").writeBytes(table(6, listOf(intArrayOf(8, 0, 0, 0, 1478, 1479))))
        File(dir, "CreatureDisplayInfo.dbc").writeBytes(table(3, listOf(intArrayOf(1478, 1), intArrayOf(1479, 2))))
        File(dir, "CreatureModelData.dbc").writeBytes(modelTable(listOf(1 to "Character\\Troll\\Male\\TrollMale.mdx", 2 to "Character\\Troll\\Female\\TrollFemale.mdx")))
        File(patch, "Character/Troll/Male/TrollMale.m2").apply { parentFile!!.mkdirs(); writeBytes(troll) }
        File(patch, "Character/Troll/Female/TrollFemale.m2").apply { parentFile!!.mkdirs(); writeBytes(trollWoman) }
        if (withSizes) File(patch, WrathppLooks.SIZES).writeText(
            "${troll.size}\t00000000\tCharacter/Troll/Male/TrollMale.m2\n${trollWoman.size}\t00000000\tCharacter/Troll/Female/TrollFemale.m2\n")
        File(patch, WrathppLooks.MARKER).writeText("abc\n")
        return client
    }

    private fun server(): File = tmp.newFolder("server").also { File(it, "share/dbc").mkdirs(); File(it, "share/dbc/${WrathppLooks.MARKER}").writeText("abc\n") }

    @Test fun aModelsHeaderIsRead() {
        val h = WrathppModelCheck.header(troll, troll.size.toLong())!!
        assertEquals(264, h.version); assertEquals(231L, h.bones); assertEquals(40L, h.vertices); assertEquals(1L, h.views); assertTrue(h.whole)
        val cut = model(231, 40, cut = 10)
        assertFalse(WrathppModelCheck.header(cut, cut.size.toLong())!!.whole)
        assertNull(WrathppModelCheck.header(ByteArray(0x48), 0x48))
    }

    @Test fun everyRaceModelAsPackagedIsSaidSo() {
        val lines = WrathppModelCheck.examine(client())!!.lines()
        assertTrue(lines, lines.startsWith("race models: 2 of 2 in the looks' patch, as packaged; nothing is read before the looks' patch\n"))
        assertTrue(lines, lines.contains("TrollMale.m2: ${troll.size} bytes, v264, 231 bones, 40 vertices"))
    }

    @Test fun aMissingModelIsNamedWithTheArchiveTheGameReadsInstead() {
        val client = client()
        File(client, "Data/${WrathppLooks.PATCH}/Character/Troll/Male/TrollMale.m2").delete()
        val report = WrathppModelCheck.examine(client)!!
        assertTrue(report.needsRepair)
        val lines = report.lines { path -> if (path == "Character\\Troll\\Male\\TrollMale.m2") "Data/patch-A.MPQ" else null }
        assertTrue(lines, lines.startsWith("race models: 1 of 2 in the looks' patch, as packaged; MISSING: Character\\Troll\\Male\\TrollMale.m2 (race 8 male; the game reads Data/patch-A.MPQ)"))
    }

    @Test fun aModelCutShortOrNotThePackagesIsNamed() {
        val client = client()
        val patch = File(client, "Data/${WrathppLooks.PATCH}")
        File(patch, "Character/Troll/Male/TrollMale.m2").writeBytes(model(231, 40, cut = 48))
        File(patch, "Character/Troll/Female/TrollFemale.m2").writeBytes(model(120, 30))
        val lines = WrathppModelCheck.examine(client)!!.lines()
        assertTrue(lines, lines.contains("CUT SHORT"))
        assertTrue(lines, lines.contains("NOT THE PACKAGE'S (${model(120, 30).size} bytes, the package's ${trollWoman.size})"))
    }

    @Test fun aModelWithTheBodyLayerIsHeldToTheLooksOwnKeptBesideIt() {
        val client = client()
        val woman = File(client, "Data/${WrathppLooks.PATCH}/Character/Troll/Female/TrollFemale.m2")
        woman.copyTo(File(woman.path + ".body-orig"))
        woman.writeBytes(model(150, 31))
        val report = WrathppModelCheck.examine(client)!!
        assertTrue(report.lines(), report.bad.isEmpty())
        assertTrue(report.lines().contains("with the body layer"))
    }

    @Test fun theModelIsFoundInAnyCaseAsWineFindsIt() {
        val client = client()
        val patch = File(client, "Data/${WrathppLooks.PATCH}")
        File(patch, "Character/Troll").renameTo(File(patch, "Character/TROLL"))
        assertTrue(WrathppModelCheck.examine(client)!!.bad.isEmpty())
    }

    @Test fun aPatchThatTheGameReadsBeforeTheLooksIsNamed() {
        val client = client()
        for (n in listOf("patch-A.MPQ", "patch-z.mpq.new", "patch-_.MPQ")) File(client, "Data/$n").writeText("x")
        assertEquals(listOf("patch-_.MPQ"), WrathppModelCheck.readBefore(File(client, "Data")))
    }

    @Test fun aBadModelIsFetchedAgainOncePerLooks() {
        val client = client()
        val server = server()
        val patch = File(client, "Data/${WrathppLooks.PATCH}")
        File(patch, "Character/Troll/Male/TrollMale.m2").delete()
        var fetched = 0
        // the repair puts a new patch folder in (here: the model back and a new marker)
        val repair = {
            fetched++
            File(patch, "Character/Troll/Male/TrollMale.m2").writeBytes(troll)
            File(patch, WrathppLooks.MARKER).apply { writeText("abc\n"); setLastModified(lastModified() + 5000) }
            Unit
        }
        val lines = WrathppModelCheck.ensure(client, server, { _, _ -> }, repair)
        assertEquals(1, fetched)
        assertTrue(lines, lines.startsWith("race models: the looks were held to their package and put in again (1 not as packaged: TrollMale.m2)"))
        assertTrue(lines, lines.contains("2 of 2 in the looks' patch, as packaged"))
        // the same looks bad again: not fetched a second time
        File(patch, "Character/Troll/Male/TrollMale.m2").writeBytes(model(10, 1))
        WrathppModelCheck.ensure(client, server, { _, _ -> }, repair)
        assertEquals(1, fetched)
    }

    @Test fun aPatchWithoutTheSizeListIsHeldToThePackageOnce() {
        val client = client(withSizes = false)
        val server = server()
        val patch = File(client, "Data/${WrathppLooks.PATCH}")
        assertTrue(WrathppModelCheck.examine(client)!!.needsRepair)
        var fetched = 0
        // offline: nothing put in, tried again at the next start
        val offline = { fetched++; Unit }
        assertTrue(WrathppModelCheck.ensure(client, server, { _, _ -> }, offline).startsWith("race models: the looks couldn't be fetched again"))
        val failing = { fetched++; throw IOException("no space") }
        assertTrue(WrathppModelCheck.ensure(client, server, { _, _ -> }, failing).contains("FAILED (no space)"))
        assertFalse(File(client, WrathppModelCheck.TRIED).exists())
        val repair = {
            fetched++
            File(patch, WrathppLooks.SIZES).writeText("${troll.size}\t0\tCharacter/Troll/Male/TrollMale.m2\n${trollWoman.size}\t0\tCharacter/Troll/Female/TrollFemale.m2\n")
            File(patch, WrathppLooks.MARKER).apply { writeText("abc\n"); setLastModified(lastModified() + 5000) }
            Unit
        }
        assertTrue(WrathppModelCheck.ensure(client, server, { _, _ -> }, repair).contains("(no size list before)"))
        assertEquals(3, fetched)
        WrathppModelCheck.ensure(client, server, { _, _ -> }, repair)
        assertEquals(3, fetched)
    }
}
