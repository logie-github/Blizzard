package com.logie.blizz.forever.tact

import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.ByteArrayOutputStream
import java.io.File
import java.nio.file.Files
import java.util.zip.Deflater

/**
 * The client download's formats, offline. (The whole download was also run against Blizzard's CDN on a desktop JVM,
 * killed mid-way and resumed, and the storage it wrote opened and read back, every frame's MD5 checked, by CascLib.)
 */
class TactTest {
    private val four = "Four score and seven years ago".toByteArray()

    @Test
    fun `jenkins matches lookup3's own test values`() {
        assertEquals(0xdeadbeef.toInt(), Jenkins.hashlittle(ByteArray(0), 0, 0, 0))
        assertEquals(0xbd5b7dde.toInt(), Jenkins.hashlittle(ByteArray(0), 0, 0, 0xdeadbeef.toInt()))
        assertEquals(0x17770551, Jenkins.hashlittle(four, 0, 30, 0))
        assertEquals(0xcd628161.toInt(), Jenkins.hashlittle(four, 0, 30, 1))
        assertEquals(0x9c093ccd.toInt() to 0xbd5b7dde.toInt(), Jenkins.hashlittle2(ByteArray(0), 0, 0, 0xdeadbeef.toInt(), 0xdeadbeef.toInt()))
    }

    private fun blte(vararg frames: ByteArray): ByteArray {
        val out = ByteArrayOutputStream()
        out.write("BLTE".toByteArray())
        val header = 12 + 24 * frames.size
        out.write(byteArrayOf((header ushr 24).toByte(), (header ushr 16).toByte(), (header ushr 8).toByte(), header.toByte()))
        out.write(byteArrayOf(0x0F, 0, 0, frames.size.toByte()))
        for (f in frames) { repeat(2) { out.write(byteArrayOf((f.size ushr 24).toByte(), (f.size ushr 16).toByte(), (f.size ushr 8).toByte(), f.size.toByte())) }; out.write(ByteArray(16)) }
        frames.forEach { out.write(it) }
        return out.toByteArray()
    }

    @Test
    fun `blte decodes raw and zlib frames, also as a stream`() {
        val zipped = ByteArrayOutputStream().also { o ->
            val d = Deflater(); d.setInput("world".toByteArray()); d.finish()
            val b = ByteArray(64); while (!d.finished()) { val n = d.deflate(b); o.write(b, 0, n) }; d.end()
        }.toByteArray()
        val data = blte(byteArrayOf('N'.code.toByte()) + "hello ".toByteArray(), byteArrayOf('Z'.code.toByte()) + zipped)
        assertEquals("hello world", String(Blte.decode(data)))
        assertEquals("hello world", String(BlteInputStream(data.inputStream()).readBytes()))
    }

    @Test
    fun `configs and tables parse`() {
        val config = Tact.parseConfig("# Build Configuration\n\nroot = abc\nencoding = 11 22\n")
        assertEquals(listOf("abc"), config["root"]); assertEquals(listOf("11", "22"), config["encoding"])
        val rows = Tact.parseTable("Region!STRING:0|BuildId!DEC:4\n## seqn = 1\nus|70862\neu|70862")
        assertEquals("70862", rows.first { it["Region"] == "us" }["BuildId"])
    }

    @Test
    fun `an entry header carries the reversed key, the size with the header and both checksums`() {
        val key = Key16.hex("000102030405060708090a0b0c0d0e0f")
        val h = CascStorageWriter.header(key, 1000, 0)
        assertEquals(30, h.size)
        assertArrayEquals(ByteArray(16) { (15 - it).toByte() }, h.copyOf(16))
        assertEquals(1030, le32(h, 16))
        assertEquals(Jenkins.hashlittle(h, 0, 22, 0x3D6BE971), le32(h, 22))
        // The offset-keyed checksum changes with the offset.
        assertTrue(!CascStorageWriter.header(key, 1000, 0).contentEquals(CascStorageWriter.header(key, 1000, 4096)))
    }

    @Test
    fun `an index file is version 7 with guarded header and entries, sorted, as CascLib checks them`() {
        val k1 = ByteArray(9) { 1 }
        val k2 = ByteArray(9) { 2 }
        val idx = CascStorageWriter.index(3, listOf(k1 to CascStorageWriter.Placed(2, 0x100, 530), k2 to CascStorageWriter.Placed(0, 0, 40)))
        assertEquals(16, le32(idx, 0))
        assertEquals(Jenkins.hashlittle(idx, 8, 16, 0), le32(idx, 4))
        assertEquals(7, idx[8].toInt()); assertEquals(3, idx[10].toInt()); assertEquals(30, idx[15].toInt())
        assertEquals(36, le32(idx, 32))
        var hc = 0; var hb = 0
        for (e in 0 until 2) { val (c, b) = Jenkins.hashlittle2(idx, 40 + e * 18, 18, hc, hb); hc = c; hb = b }
        assertEquals(hc, le32(idx, 36))
        // Entry 1: key, segment 2 / offset 0x100 in 5 big-endian bytes, size little-endian.
        assertArrayEquals(k1, idx.copyOfRange(40, 49))
        assertEquals((2L shl 30) or 0x100L, beN(idx, 49, 5))
        assertEquals(530, le32(idx, 54))
    }

    @Test
    fun `the bucket folds the first nine key bytes`() {
        assertEquals(0, CascStorageWriter.bucket(ByteArray(16)))
        assertEquals(0x0F xor 0x0A, CascStorageWriter.bucket(byteArrayOf(0xAF.toByte(), 0, 0, 0, 0, 0, 0, 0, 0)))
        assertEquals(0, CascStorageWriter.bucket(byteArrayOf(5, 5, 0, 0, 0, 0, 0, 0, 0)))
    }

    @Test
    fun `install paths are laid out without regard to case, never outside`() {
        val base = Files.createTempDirectory("tact").toFile()
        val a = ForeverClientInstaller.placeFor(base, "Utils\\icudtl.dat")
        File(a.parentFile, "x").writeText("x")
        val b = ForeverClientInstaller.placeFor(base, "UTILS\\LOCALES\\EN-US.PAK")
        assertEquals(a.parentFile, b.parentFile!!.parentFile)
        assertEquals(base, ForeverClientInstaller.placeFor(base, "..\\..\\Wow.exe").parentFile)
    }

    @Test
    fun `targets sort by unsigned key, drop repeats and are found`() {
        val t = ForeverClientInstaller.Targets(2)
        t.add(1, -1L, 5); t.add(2, 0, 9); t.add(3, 0, 1); t.add(4, -1L, 5)
        t.sortAndDedupe()
        assertEquals(3, t.count)
        assertEquals(listOf(3, 2, 1), t.id.toList())
        assertEquals(2, t.find(-1L, 5)); assertEquals(0, t.find(0, 1)); assertEquals(-1, t.find(7, 7))
    }

    @Test
    fun `a storage written, cut short and resumed keeps only whole entries`() {
        val dir = Files.createTempDirectory("casc").toFile()
        val w = CascStorageWriter(dir)
        val s = w.newSegment()
        val key = Key16.hex("ffffffffffffffffffffffffffffffff")
        s.write(7, key, ByteArray(100).inputStream(), 100)
        s.close()
        File(dir, "data.000").appendBytes(ByteArray(55)) // a write the app was killed in
        val placed = CascStorageWriter(dir).resume()
        assertEquals(setOf(7), placed.keys)
        assertEquals(130L, File(dir, "data.000").length())
    }
}
