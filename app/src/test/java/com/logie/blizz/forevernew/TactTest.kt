package com.logie.blizz.forevernew

import com.logie.blizz.forevernew.tact.*
import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File
import java.io.IOException
import java.util.zip.Deflater

/** The pure parts of the installer that fetches the game from Blizzard's servers. The real fetch was run against Blizzard's CDN and read back with CascLib on a desktop (docs/forever/README.md). */
class TactTest {
    @get:Rule val tmp = TemporaryFolder()

    // (data, [seed, hashlittle, pc, pb, hashlittle2.pc, hashlittle2.pb]) from CascLib's own lookup3.c
    private val vectors = listOf(
        Triple("", intArrayOf(197372185,-361666552,2109065305,1905491376,-839449352,1550026568), 0),
        Triple("5eac99d7a9966ef372b2dfa7", intArrayOf(1219720265,-1996832995,787645371,554274574,-1914969458,-301186068), 0),
        Triple("0a094c2d8a6a2d080b4df943b415ab319dc9584b5e4baba8b3006cc82764be316e0a5ef874", intArrayOf(224799627,-111938013,487857920,154648447,865962219,752352658), 0),
        Triple("92982ccfb4917b84f7c232bf5cd74422168cedc90a733ff6", intArrayOf(1855494884,320932158,690150391,750770692,-1842299642,2033080240), 0),
        Triple("7942663f76b8fa0e05997df8f8", intArrayOf(1598032758,-1351992164,906368560,93628871,683652648,765648435), 0),
        Triple("1e76e2398a39d7039390e4", intArrayOf(1841664187,-1456760661,925891310,277652093,939829672,1924879600), 0),
        Triple("2d13e40f8610fe84dc901fcf6514f22e63d6c532243f826197", intArrayOf(575403353,-1314085685,1381817009,662157283,-1924335599,-1493240047), 0),
        Triple("46b268ccca", intArrayOf(24381238,772223071,1786597110,347498620,-1817100831,1761417612), 0)
    )

    @Test fun jenkinsMatchesTheCOriginal() {
        for ((hex, v, _) in vectors) {
            val data = ByteArray(hex.length / 2) { hex.substring(it * 2, it * 2 + 2).toInt(16).toByte() }
            assertEquals(v[1], Jenkins.hashlittle(data, 0, data.size, v[0]))
            val (c, b) = Jenkins.hashlittle2(data, 0, data.size, v[2], v[3])
            assertEquals(v[4], c); assertEquals(v[5], b)
        }
    }

    private fun zframe(data: ByteArray): ByteArray {
        val d = Deflater(); d.setInput(data); d.finish()
        val out = ByteArray(data.size + 64); val n = d.deflate(out); d.end()
        return byteArrayOf('Z'.code.toByte()) + out.copyOf(n)
    }

    private fun be(v: Int) = byteArrayOf((v shr 24).toByte(), (v shr 16).toByte(), (v shr 8).toByte(), v.toByte())

    /** A BLTE file of the given decoded pieces, each one frame (zlib or plain). */
    private fun blte(vararg parts: ByteArray, plain: Boolean = false): ByteArray {
        val frames = parts.map { if (plain) byteArrayOf('N'.code.toByte()) + it else zframe(it) }
        val head = java.io.ByteArrayOutputStream()
        head.write("BLTE".toByteArray()); head.write(be(12 + frames.size * 24)); head.write(byteArrayOf(0x0F, 0, 0, frames.size.toByte()))
        for ((i, f) in frames.withIndex()) { head.write(be(f.size)); head.write(be(parts[i].size)); head.write(ByteArray(16)) }
        return head.toByteArray() + frames.fold(ByteArray(0)) { a, f -> a + f }
    }

    @Test fun blteDecodesFramesAndRefusesTheUnknown() {
        val a = ByteArray(5000) { (it % 7).toByte() }; val b = "tail".toByteArray()
        assertArrayEquals(a + b, Blte.decode(blte(a, b)))
        assertArrayEquals(a + b, Blte.decode(blte(a, b, plain = true)))
        assertTrue(runCatching { Blte.decode("NOPE1234".toByteArray()) }.isFailure)
        val enc = blte(a); val firstFrame = 12 + 24
        enc[firstFrame] = 'E'.code.toByte()
        assertTrue(runCatching { Blte.decode(enc) }.isFailure)
    }

    @Test fun tablesAndConfigsParse() {
        val rows = TactText.table("Region!STRING:0|BuildConfig!HEX:16\n## seqn = 5\nus|abc\neu|def\n")
        assertEquals("abc", rows.first { it["Region"] == "us" }["BuildConfig"])
        val cfg = TactText.config("# Build Configuration\n\nroot = aa\nencoding = 11 22\ninstall-size = 1 2\n")
        assertEquals(listOf("11", "22"), cfg["encoding"])
    }

    @Test fun tagSelectionKeepsSharedFilesAndDropsOtherPlatformsAndLanguages() {
        val names = listOf("Windows", "OSX", "enUS", "deDE")
        val types = listOf(1, 1, 3, 3)
        // entries: 0 = every platform and language (shared); 1 = OSX only; 2 = Windows and German only; 3 = no tags
        fun mask(vararg e: Int) = ByteArray(1).also { for (i in e) it[0] = (it[0].toInt() or (0x80 shr i)).toByte() }
        // Windows: entries 0, 2, 3; OSX: 0, 1; enUS: 0, 3; deDE: 2 (entry 3 has Windows and enUS only; entry 2 Windows and German)
        val t = TagTable(names, types, listOf(mask(0, 2, 3), mask(0, 1), mask(0, 3), mask(2)))
        val sel = setOf("Windows", "enUS")
        assertTrue(t.wanted(0, sel)); assertFalse(t.wanted(1, sel)); assertFalse(t.wanted(2, sel)); assertTrue(t.wanted(3, sel))
    }

    @Test fun installAndDownloadManifestsParse() {
        // install: 'IN', version 1, hash size 16, 1 tag, 2 entries
        val tag = "Windows".toByteArray() + byteArrayOf(0, 0, 1) + byteArrayOf(0x80.toByte())
        val e1 = "Wow.exe".toByteArray() + byteArrayOf(0) + ByteArray(16) { 1 } + be(1234)
        val e2 = "Utils\\a.dll".toByteArray() + byteArrayOf(0) + ByteArray(16) { 2 } + be(99)
        val install = byteArrayOf('I'.code.toByte(), 'N'.code.toByte(), 1, 16, 0, 1) + be(2) + tag + e1 + e2
        val m = InstallManifest.parse(install)
        assertEquals(listOf("Wow.exe", "Utils\\a.dll"), m.names); assertEquals(1234L, m.sizes[0]); assertTrue(m.tags.has(0, 0)); assertFalse(m.tags.has(1, 0))
        // download: 'DL', version 2, hash 16, no checksum, 2 entries, 1 tag, flag size 0
        fun ent(k: Int, size: Int, pri: Int) = ByteArray(16) { k.toByte() } + byteArrayOf(0, 0, (size shr 16).toByte(), (size shr 8).toByte(), size.toByte(), pri.toByte())
        val dl = byteArrayOf('D'.code.toByte(), 'L'.code.toByte(), 2, 16, 0) + be(2) + byteArrayOf(0, 1, 0) + ent(5, 70000, 0) + ent(6, 9, 2) + ("x".toByteArray() + byteArrayOf(0, 0, 1, 0xC0.toByte()))
        val d = DownloadManifest.parse(dl)
        assertEquals(2, d.count); assertEquals(70000L, d.size(0)); assertEquals(2, d.priority(1)); assertTrue(d.tags.has(1, 0)); assertEquals(5, d.ekey(0)[0].toInt()); assertEquals(6, d.ekey(1)[15].toInt())
    }

    @Test fun archiveIndexReadsItsPages() {
        val per = 170; val count = 175
        val pages = ByteArray(2 * 4096)
        for (i in 0 until count) {
            val p = (i / per) * 4096 + (i % per) * 24
            pages[p] = (i / 256).toByte(); pages[p + 1] = i.toByte()
            val sz = be(100 + i); System.arraycopy(sz, 0, pages, p + 16, 4); val off = be(i * 1000); System.arraycopy(off, 0, pages, p + 20, 4)
        }
        val footer = ByteArray(36); footer[16] = 1; footer[19] = 4; footer[20] = 4; footer[21] = 4; footer[22] = 16; footer[23] = 8; footer[24] = count.toByte()
        val idx = ArchiveIndex.parse("x", pages + footer)
        assertEquals(count, idx.ekeys.size); assertEquals(100 + 171, idx.sizes[171]); assertEquals(171000L, idx.offsets[171]); assertEquals(171, idx.ekeys[171][1].toInt() and 255)
    }

    @Test fun localStorageIsWrittenAndReadBack() {
        val dir = File(tmp.root, "Data/data")
        val w = CascWriter(dir)
        val keys = (0 until 40).map { n -> ByteArray(16) { (n * 7 + it * 3).toByte() } }
        for (k in keys) w.add(k, blte(ByteArray(300) { k[0] }))
        w.add(keys[0], blte(ByteArray(10))) // a second add of the same key is ignored
        w.finish()
        assertEquals(40, w.count)
        val idx = dir.listFiles { f -> f.name.endsWith(".idx") }!!
        assertEquals(16, idx.size); assertTrue(idx.all { Regex("[0-9a-f]{10}\\.idx").matches(it.name) })
        // a new writer finds what the old one stored, and adds without repeating
        val again = CascWriter(dir)
        assertEquals(40, again.count); assertTrue(again.has(keys[17]))
        again.add(ByteArray(16) { 99 }, blte(ByteArray(5))); again.finish()
        assertEquals(41, CascWriter(dir).count)
        assertEquals(16, dir.listFiles { f -> f.name.endsWith(".idx") }!!.size)
        // the data file holds each header (the key reversed) then the BLTE bytes
        val data = File(dir, "data.000").readBytes()
        assertEquals(keys[0][15], data[0]); assertEquals('B'.code.toByte(), data[30])
        // buckets are the way Blizzard computes them
        assertTrue(keys.all { CascWriter.bucket(it.copyOf(9)) in 0..15 })
    }

    @Test fun localHeaderCarriesTheSizeAndAGuardedHash() {
        val key = ByteArray(16) { (it + 1).toByte() }
        val h = CascWriter.localHeader(key, 1030, 4096)
        assertEquals(30, h.size); assertEquals(16.toByte(), h[0]); assertEquals((1030 and 255).toByte(), h[16]); assertEquals(((1030 shr 8) and 255).toByte(), h[17])
        assertArrayEquals(h, CascWriter.localHeader(key, 1030, 4096))
        assertFalse(h.contentEquals(CascWriter.localHeader(key, 1030, 8192))) // the checksum depends on where it sits
    }

    @Test fun clientDownloadChoosesBlizzardsBuildAndChecksTheServerSupportsIt() {
        val versions = "Region!STRING:0|BuildConfig!HEX:16|CDNConfig!HEX:16|KeyRing!HEX:16|BuildId!DEC:4|VersionsName!String:0|ProductConfig!HEX:16\n## seqn = 1\nus|b1|c1||70938|1.60.1.70938|p\neu|b2|c2||70938|1.60.1.70938|p\n"
        val cdns = "Name!STRING:0|Path!STRING:0|Hosts!STRING:0|Servers!STRING:0|ConfigPath!STRING:0\n## seqn = 2\nus|tpr/wow|a.example b.example|x|tpr/configs/data\n"
        val r = ForeverClientDownload.release("us") { url -> if (url.endsWith("/versions")) versions else cdns }
        assertEquals(70938, r.buildId); assertEquals(listOf("a.example", "b.example"), r.hosts); assertEquals("tpr/wow", r.path)
        assertTrue(ForeverClientDownload.supported(r, listOf(70938, 70888))); assertFalse(ForeverClientDownload.supported(r, listOf(70888)))
        assertTrue(ForeverClientDownload.spaceNeeded(ForeverClientDownload.ALL) > 49L shl 30)
    }

    @Test fun httpsHostsComeFirstAndHttpOnlyOnesAreLast() {
        val servers = "http://level3.blizzard.com/?maxhosts=8 http://us.cdn.blizzard.com/?maxhosts=4&fallback=1 https://level3.ssl.blizzard.com/?maxhosts=4&fallback=1 https://us.cdn.blizzard.com/?maxhosts=4&fallback=1"
        assertEquals(listOf("level3.ssl.blizzard.com", "us.cdn.blizzard.com", "level3.blizzard.com"), ForeverClientDownload.httpsHosts(servers, "level3.blizzard.com us.cdn.blizzard.com"))
        assertEquals(listOf("a.example"), ForeverClientDownload.httpsHosts("", "a.example"))
    }

    @Test fun cdnTriesTheNextHostAndKeepsTheOneThatAnswered() {
        val server = com.sun.net.httpserver.HttpServer.create(java.net.InetSocketAddress("127.0.0.1", 0), 0)
        server.createContext("/p") { ex -> val body = "hello".toByteArray(); ex.sendResponseHeaders(200, body.size.toLong()); ex.responseBody.use { it.write(body) } }
        server.start()
        try {
            val cdn = HttpCdn(listOf("127.0.0.1:1", "127.0.0.1:${server.address.port}"), "p", scheme = "http")
            val hash = "aabbccddeeff00112233445566778899"
            assertEquals("hello", String(cdn.get("data", hash)))
            assertEquals("hello", String(cdn.get("data", hash))) // the second ask goes to the host that answered first
        } finally { server.stop(0) }
    }

    @Test fun longIntMapHoldsAMillionKeysAndFindsThemBack() {
        val m = LongIntMap(10)
        for (i in 0 until 200_000) m[i.toLong() * 7919L + 13] = i
        assertEquals(200_000, m.size)
        assertEquals(12345, m[12345L * 7919L + 13]); assertEquals(-1, m[5L]); m[13L] = 42; assertEquals(42, m[13L]); assertEquals(200_000, m.size)
        assertEquals(0x0102030405060708L, byteArrayOf(1, 2, 3, 4, 5, 6, 7, 8, 9).prefix64())
    }
}
