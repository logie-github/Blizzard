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
        for (f in frames) {
            repeat(2) { out.write(byteArrayOf((f.size ushr 24).toByte(), (f.size ushr 16).toByte(), (f.size ushr 8).toByte(), f.size.toByte())) }
            out.write(java.security.MessageDigest.getInstance("MD5").digest(f)) // each frame's MD5, as BLTE carries it
        }
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
        // After the entries: the (empty) update section, from the next 4 KiB to the end of a 64 KiB file, as the game writes it.
        assertEquals(0x10000, idx.size)
        assertTrue(idx.copyOfRange(40 + 36, idx.size).all { it.toInt() == 0 })
    }

    @Test
    fun `the update section is at least 0x7800 bytes from the next 4 KiB, the file a multiple of 64 KiB`() {
        // The game's own file: entries end at 0x5ce6, the section starts at 0x6000, the file is 0x10000.
        assertEquals(0x10000, 0x5ce6 + CascStorageWriter.tail(0x5ce6))
        // Entries ending at 0x8000 leave exactly 0x8000 of section; one byte more starts it at 0x9000, 0x7800 of it ends past 64 KiB.
        assertEquals(0x10000, 0x8000 + CascStorageWriter.tail(0x8000))
        assertEquals(0x20000, 0x8001 + CascStorageWriter.tail(0x8001))
        // A full bucket of a whole client (65,000 entries).
        val end = 40 + 65_000 * 18
        assertEquals(0x130000, end + CascStorageWriter.tail(end))
    }

    @Test
    fun `an index of the first downloads (no update section) is given one in place, its entries kept`() {
        val dir = Files.createTempDirectory("idx").toFile()
        val entries = (0 until 5000).map { n -> ByteArray(9) { (n shr (8 * (it % 3))).toByte() } to CascStorageWriter.Placed(1, n * 64, 64) }
        val whole = CascStorageWriter.index(5, entries)
        val end = CascStorageWriter.sortedEnd(whole)!!
        assertEquals(40 + 5000 * 18, end)
        assertEquals(0x20000, whole.size) // 90,040 bytes of entries: the section from 0x16000, the file 128 KiB
        val old = File(dir, "0500000001.idx").apply { writeBytes(whole.copyOf(end)) }
        File(dir, "data.000").writeBytes(ByteArray(10))
        assertEquals(1, CascStorageWriter.repairIndexes(dir))
        assertArrayEquals(whole, old.readBytes())
        assertEquals(0, CascStorageWriter.repairIndexes(dir))
        assertEquals(10, File(dir, "data.000").length())
        // An index the game has written to since (entries in its section, a longer file) is left alone.
        val games = whole.copyOf(0x30000).also { it[0x16000] = 1 }
        File(dir, "0500000002.idx").writeBytes(games)
        // Not an index file: left alone.
        File(dir, "0600000001.idx").writeBytes(ByteArray(64) { 9 })
        assertEquals(0, CascStorageWriter.repairIndexes(dir))
        assertArrayEquals(games, File(dir, "0500000002.idx").readBytes())
        assertEquals(64, File(dir, "0600000001.idx").length())
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

    private fun md5(b: ByteArray) = java.security.MessageDigest.getInstance("MD5").digest(b)

    @Test
    fun `downloads are checked against their names`() {
        val config = "# Build Configuration\nroot = 00\n".toByteArray()
        val configHash = md5(config).joinToString("") { "%02x".format(it) }
        assertTrue(Verify.config(config, configHash))
        assertTrue(!Verify.config(config + 1, configHash))

        val index = ByteArray(100) { it.toByte() }
        val indexHash = md5(index.copyOfRange(72, 100)).joinToString("") { "%02x".format(it) }
        assertTrue(Verify.index(index, indexHash))
        assertTrue(!Verify.index(index.copyOf().also { it[99] = 0 }, indexHash))

        val framed = blte(byteArrayOf('N'.code.toByte()) + "hello".toByteArray())
        val key = Key16.of(md5(framed.copyOf(be32(framed, 4))))
        assertTrue(Verify.blte(framed, key))
        assertTrue(!Verify.blte("<html>error</html>".toByteArray(), key))
        val tampered = framed.copyOf().also { it[it.size - 1] = 'X'.code.toByte() } // data changed, header (and so the key) intact
        assertTrue(!Verify.blte(tampered, key))
        val single = "BLTE".toByteArray() + ByteArray(4) + "Nraw".toByteArray()
        assertTrue(Verify.blte(single, Key16.of(md5(single))))
    }

    @Test
    fun `an entry that doesn't match its key is taken back out and nothing is recorded`() {
        val dir = Files.createTempDirectory("casc").toFile()
        val w = CascStorageWriter(dir)
        val s = w.newSegment()
        val good = blte(byteArrayOf('N'.code.toByte()) + "hello".toByteArray())
        val key = Key16.of(md5(good.copyOf(be32(good, 4))))
        val bad = good.copyOf().also { it[it.size - 1] = 'X'.code.toByte(); it[5] = 0x7F } // header changed
        var threw = false
        try { s.write(1, key, bad.inputStream(), bad.size.toLong()) } catch (_: CorruptDownloadException) { threw = true }
        assertTrue(threw)
        assertEquals(0L, File(dir, "data.000").length())
        val placed = s.write(1, key, good.inputStream(), good.size.toLong())
        s.close()
        assertEquals(0, placed.offset)
        assertEquals(30L + good.size, File(dir, "data.000").length())
        assertEquals(setOf(1), CascStorageWriter(dir).resume().keys)
    }

    @Test
    fun `a storage written, cut short and resumed keeps only whole entries`() {
        val dir = Files.createTempDirectory("casc").toFile()
        val w = CascStorageWriter(dir)
        val s = w.newSegment()
        val data = blte(byteArrayOf('N'.code.toByte()) + ByteArray(87))
        val key = Key16.of(md5(data.copyOf(be32(data, 4))))
        s.write(7, key, data.inputStream(), data.size.toLong())
        s.close()
        File(dir, "data.000").appendBytes(ByteArray(55)) // a write the app was killed in
        val placed = CascStorageWriter(dir).resume()
        assertEquals(setOf(7), placed.keys)
        assertEquals(30L + data.size, File(dir, "data.000").length())
    }
    @Test
    fun `Wine's adapter listing is fixed in the one known file only`() {
        val dll = ByteArray(0x6000) { (it * 7).toByte() }
        val hash = com.logie.blizz.forever.WineAdapterFix.sha256(dll)
        val fixed = com.logie.blizz.forever.WineAdapterFix.fixed(dll, original = hash)!!
        // mov eax, 232 (ERROR_NO_DATA); ret, at GetAdaptersAddresses; nothing else changed.
        assertArrayEquals(byteArrayOf(0xB8.toByte(), 0xE8.toByte(), 0, 0, 0, 0xC3.toByte()), fixed.copyOfRange(0x4cb0, 0x4cb6))
        assertArrayEquals(dll.copyOf(0x4cb0), fixed.copyOf(0x4cb0))
        assertArrayEquals(dll.copyOfRange(0x4cb6, dll.size), fixed.copyOfRange(0x4cb6, fixed.size))
        // Another build of the file, the fixed one again, or a short file: left as it is.
        assertEquals(null, com.logie.blizz.forever.WineAdapterFix.fixed(dll))
        assertEquals(null, com.logie.blizz.forever.WineAdapterFix.fixed(fixed, original = hash))
        assertEquals(null, com.logie.blizz.forever.WineAdapterFix.fixed(ByteArray(16), original = com.logie.blizz.forever.WineAdapterFix.sha256(ByteArray(16))))
        // Wine's real file, when the test is pointed at it (BLIZZ_WINE_IPHLPAPI): the hashes written down are its.
        System.getenv("BLIZZ_WINE_IPHLPAPI")?.let { path ->
            val real = File(path).readBytes()
            assertEquals(com.logie.blizz.forever.WineAdapterFix.ORIGINAL, com.logie.blizz.forever.WineAdapterFix.sha256(real))
            assertEquals(com.logie.blizz.forever.WineAdapterFix.FIXED, com.logie.blizz.forever.WineAdapterFix.sha256(com.logie.blizz.forever.WineAdapterFix.fixed(real)!!))
        }
    }
}
