package com.logie.blizz.warsmash

import org.apache.commons.compress.archivers.sevenz.SevenZOutputFile
import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File
import java.nio.ByteBuffer
import java.nio.ByteOrder

/** Classic+ made ready for Warsmash: textures repacked, models sorted, the archive unpacked safely, Google Drive's form. */
class ClassicPlusTest {
    @get:Rule val tmp = TemporaryFolder()

    /** A DDS header and [data]: [fourCC] compression, [flags] its pixel format's flags. */
    private fun dds(width: Int, height: Int, fourCC: String, data: ByteArray, flags: Int = 4): ByteArray {
        val b = ByteBuffer.allocate(128 + data.size).order(ByteOrder.LITTLE_ENDIAN)
        b.put("DDS ".toByteArray())
        b.putInt(4, 124)
        b.putInt(12, height)
        b.putInt(16, width)
        b.putInt(80, flags)
        fourCC.toByteArray().copyInto(b.array(), 84)
        data.copyInto(b.array(), 128)
        return b.array()
    }

    private fun u32(b: ByteArray, at: Int) = ByteBuffer.wrap(b, at, 4).order(ByteOrder.LITTLE_ENDIAN).int

    /** An MDX of [version] naming [textures] (its TEXS chunk), with nothing else in it. */
    private fun mdx(version: Int, vararg textures: String): ByteArray {
        val texs = ByteBuffer.allocate(268 * textures.size).order(ByteOrder.LITTLE_ENDIAN)
        textures.forEachIndexed { i, t -> t.toByteArray().copyInto(texs.array(), i * 268 + 4) }
        val b = ByteBuffer.allocate(4 + 12 + 8 + texs.capacity()).order(ByteOrder.LITTLE_ENDIAN)
        b.put("MDLX".toByteArray()).put("VERS".toByteArray()).putInt(4).putInt(version)
        b.put("TEXS".toByteArray()).putInt(texs.capacity()).put(texs.array())
        return b.array()
    }

    @Test
    fun aDxt5TextureBecomesABlpWithTheSameBlocks() {
        val blocks = ByteArray(32) { (it * 7).toByte() }
        val blp = ClassicPlus.ddsToBlp(dds(8, 4, "DXT5", blocks + ByteArray(16)))!!
        assertEquals("BLP2", String(blp, 0, 4))
        assertEquals(1, u32(blp, 4))
        assertEquals(2, blp[8].toInt())
        assertEquals(8, blp[9].toInt())
        assertEquals(7, blp[10].toInt())
        assertEquals(1, blp[11].toInt())
        assertEquals(8, u32(blp, 12))
        assertEquals(4, u32(blp, 16))
        assertEquals(1172, u32(blp, 20))
        assertEquals(32, u32(blp, 84))
        assertEquals(1172 + 32, blp.size)
        assertArrayEquals(blocks, blp.copyOfRange(1172, 1172 + 32))
    }

    @Test
    fun aDxt1TextureKeepsWhetherItHasAlpha() {
        val opaque = ClassicPlus.ddsToBlp(dds(4, 4, "DXT1", ByteArray(8)))!!
        assertEquals(0, opaque[9].toInt())
        assertEquals(0, opaque[10].toInt())
        val cutout = ClassicPlus.ddsToBlp(dds(4, 4, "DXT1", ByteArray(8), flags = 5))!!
        assertEquals(1, cutout[9].toInt())
        assertEquals(8, u32(cutout, 84))
    }

    @Test
    fun otherTexturesAreLeftAlone() {
        assertNull(ClassicPlus.ddsToBlp(dds(4, 4, "ATI2", ByteArray(16))))
        assertNull(ClassicPlus.ddsToBlp(dds(8, 8, "DXT5", ByteArray(16))))
        assertNull(ClassicPlus.ddsToBlp("BLP1".toByteArray() + ByteArray(200)))
    }

    @Test
    fun modelsSayTheirFormatAndTheirTextures() {
        assertEquals(800, ClassicPlus.mdxVersion(mdx(800)))
        assertEquals(1100, ClassicPlus.mdxVersion(mdx(1100)))
        assertNull(ClassicPlus.mdxVersion("MDL text".toByteArray() + ByteArray(16)))
        assertEquals(listOf("textures/a.blp", "units/b/c.dds"), ClassicPlus.textures(mdx(800, "Textures\\A.blp", "Units\\B\\C.dds")))
    }

    @Test
    fun preparingKeepsWhatWarsmashReads() {
        val dir = tmp.newFolder("pack")
        fun put(path: String, bytes: ByteArray) = File(dir, path).apply { parentFile?.mkdirs(); writeBytes(bytes) }
        put("Units/Footman/Footman.mdx", mdx(800, "Textures\\Named.dds", "Textures\\Other.blp"))
        put("abilities/weapons/Arrow/Arrow.mdx", mdx(1100, "Textures\\Arrow.blp"))
        put("textures/named.dds", dds(4, 4, "DXT5", ByteArray(16)))
        put("textures/other.dds", dds(4, 4, "DXT1", ByteArray(8)))
        val ownBlp = put("textures/kept.blp", "BLP1 the pack's own".toByteArray())
        put("textures/kept.dds", dds(4, 4, "DXT5", ByteArray(16)))
        put("Instruction.txt", "how to".toByteArray())
        ClassicPlus.prepare(dir)
        assertTrue(File(dir, "Units/Footman/Footman.mdx").isFile)
        assertFalse(File(dir, "abilities/weapons/Arrow/Arrow.mdx").exists())
        assertTrue(File(dir, "textures/named.blp").isFile)
        assertTrue("a model names it as .dds", File(dir, "textures/named.dds").isFile)
        assertTrue(File(dir, "textures/other.blp").isFile)
        assertFalse(File(dir, "textures/other.dds").exists())
        assertEquals("BLP1 the pack's own", ownBlp.readText())
        assertFalse(File(dir, "textures/kept.dds").exists())
        assertFalse(File(dir, "Instruction.txt").exists())
    }

    @Test
    fun unpackingTakesTheClassicPlusFolderOnly() {
        val archive = File(tmp.root, "pack.7z")
        SevenZOutputFile(archive).use { out ->
            fun add(name: String, text: String) {
                val entry = out.createArchiveEntry(File(tmp.root, "x"), name)
                entry.size = text.length.toLong()
                entry.setDirectory(false)
                out.putArchiveEntry(entry)
                out.write(text.toByteArray())
                out.closeArchiveEntry()
            }
            add("kenshin_lab_v1.0/Classic+/Units/Human/Footman/Footman.mdx", "model")
            add("kenshin_lab_v1.0/Classic+/../escape.txt", "outside")
            add("kenshin_lab_v1.0/Instruction.txt", "how to")
            add("kenshin_lab_v1.0/AllowLocalFiles.reg", "registry")
        }
        val into = File(tmp.root, "out")
        ClassicPlus.unpack(archive, into)
        assertEquals("model", File(into, "Units/Human/Footman/Footman.mdx").readText())
        assertEquals(listOf("Units/Human/Footman/Footman.mdx"), into.walkTopDown().filter { it.isFile }.map { it.relativeTo(into).path.replace('\\', '/') }.toList())
        assertFalse(File(tmp.root, "escape.txt").exists())
    }

    @Test
    fun googleDrivesWarningPageLeadsToTheFile() {
        val page = """<html><body><form id="download-form" action="https://drive.usercontent.google.com/download" method="get">
            <input type="submit" id="uc-download-link" class="goog-inline-block jfk-button" value="Download anyway"/>
            <input type="hidden" name="id" value="FILEID"><input type="hidden" name="export" value="download">
            <input type="hidden" name="confirm" value="t"><input type="hidden" name="uuid" value="a-b-c"></form></body></html>"""
        assertEquals("https://drive.usercontent.google.com/download?id=FILEID&export=download&confirm=t&uuid=a-b-c", ClassicPlus.confirmUrl(page))
        assertNull(ClassicPlus.confirmUrl("<html>Quota exceeded</html>"))
    }

    @Test
    fun thePackIsALayerBetweenTheGameAndTheEnginesOwnFiles() {
        val game = tmp.newFolder("Warcraft III")
        File(game, "war3.mpq").writeText("fixture")
        val support = tmp.newFolder("support")
        val pack = tmp.newFolder("Classic+")
        val config = WarsmashConfig.sources(game, support, pack)
        assertTrue(config.contains("Count=5"))
        assertTrue(config.indexOf(File(game, "Maps").path) < config.indexOf(pack.path))
        assertTrue(config.indexOf(pack.path) < config.indexOf(support.path))
        assertNotNull(Regex("Path03=.*Classic\\+").find(config))
        assertTrue(WarsmashConfig.sources(game, support, File(tmp.root, "missing")).contains("Count=4"))
    }
}
