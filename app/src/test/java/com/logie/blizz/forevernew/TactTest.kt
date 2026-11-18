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
        assertTrue(ForeverClientDownload.spaceNeeded(ForeverClientDownload.ALL) > 44L shl 30)
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

    @Test fun theVfsFilesAreMetadataAndAnEarlierDownloadGetsThemWithoutTheGameAgain() {
        // A build config as Blizzard's are: each manifest a content key and an encoding key; the VFS root, and the VFS files it names.
        fun k(n: Int) = "%02x".format(n).repeat(16) // the storage finds a file by its key's first nine bytes
        val buildKey = k(0xb1); val cdnKey = k(0xc1)
        val config = "root = ${k(1)}\ninstall = ${k(2)} ${k(3)}\ndownload = ${k(4)} ${k(5)}\nsize = ${k(6)} ${k(7)}\nencoding = ${k(8)} ${k(9)}\n" +
            "vfs-root = ${k(10)} ${k(11)}\nvfs-root-size = 5 5\nvfs-2 = ${k(14)} ${k(15)}\nvfs-2-size = 5 5\nvfs-1 = ${k(12)} ${k(13)}\nvfs-1-size = 5 5\n"
        val asked = ArrayList<String>()
        val cdn = object : Cdn {
            override fun get(kind: String, hash: String, from: Long, length: Long, suffix: String): ByteArray {
                if (kind == "config") return (if (hash == buildKey) config else "archives = \n").toByteArray()
                asked += hash
                val all = "blob-$hash".toByteArray()
                return if (length < 0) all else all.copyOfRange(from.toInt(), minOf(all.size.toLong(), from + length).toInt())
            }
            override fun size(kind: String, hash: String, suffix: String) = "blob-$hash".length.toLong()
        }
        val root = tmp.newFolder("game")
        val installer = TactInstaller(cdn, root, "wowf")
        val build = installer.build(buildKey, cdnKey, "1.60.1.70938", 70938)
        // the manifests, the VFS root, then the VFS files in their number's order
        assertEquals(listOf(k(9), k(3), k(5), k(7), k(11), k(13), k(15)), installer.metadataKeys(build))
        File(root, ".build.info").writeText(installer.buildInfo(build))
        // an earlier download: the manifests and the VFS root are there, the VFS files are not
        CascWriter(File(root, "Data/data")).apply { for (n in listOf(9, 3, 5, 7, 11)) add(k(n).unhex(), "blob-${k(n)}".toByteArray()); finish() }
        assertEquals(2, installer.repairMetadata())
        // (the encoding file is also asked for the root's key; this one has none to give)
        assertEquals(listOf(k(13), k(15)), asked.filter { it != k(9) })
        val storage = CascWriter(File(root, "Data/data"))
        for (n in listOf(9, 3, 5, 7, 11, 13, 15)) assertTrue(k(n), storage.has(k(n).unhex()))
        assertEquals("blob-${k(15)}", String(storage.read(k(15).unhex())!!))
        // nothing is fetched twice
        asked.clear()
        assertEquals(0, installer.repairMetadata())
        assertTrue(asked.none { it != k(9) })
    }

    @Test fun longIntMapHoldsAMillionKeysAndFindsThemBack() {
        val m = LongIntMap(10)
        for (i in 0 until 200_000) m[i.toLong() * 7919L + 13] = i
        assertEquals(200_000, m.size)
        assertEquals(12345, m[12345L * 7919L + 13]); assertEquals(-1, m[5L]); m[13L] = 42; assertEquals(42, m[13L]); assertEquals(200_000, m.size)
        assertEquals(0x0102030405060708L, byteArrayOf(1, 2, 3, 4, 5, 6, 7, 8, 9).prefix64())
    }

    @Test fun theIndexFilesHaveTheUpdateSectionTheGameRequiresAndAnEarlierDownloadGetsItInPlace() {
        // the game's own file: entries end at 0x5ce6, the section starts at 0x6000, the file is 0x10000
        assertEquals(0x10000, 0x5ce6 + CascWriter.tail(0x5ce6))
        assertEquals(0x10000, 0x8000 + CascWriter.tail(0x8000))
        assertEquals(0x20000, 0x8001 + CascWriter.tail(0x8001))
        val end = 40 + 65_000 * 18
        assertEquals(0x130000, end + CascWriter.tail(end))

        val dir = java.nio.file.Files.createTempDirectory("idxfix").toFile()
        val w = CascWriter(dir)
        for (n in 0 until 300) w.add(ByteArray(16) { if (it < 2) (n shr (8 * it)).toByte() else (it * 7).toByte() }, "BLTE".toByteArray() + ByteArray(20) { n.toByte() })
        w.finish()
        val files = dir.listFiles { f -> f.name.endsWith(".idx") }!!
        assertEquals(16, files.size)
        for (f in files) {
            val b = f.readBytes(); val e = CascWriter.sortedEnd(b)!!
            assertEquals(0, b.size % 0x10000); assertTrue(b.size - (e + 0xfff) / 0x1000 * 0x1000 >= 0x7800)
            assertTrue(b.copyOfRange(e, b.size).all { it.toInt() == 0 })
        }
        assertEquals(0, CascWriter.repairIndexes(dir))
        val whole = files.associate { it.name to it.readBytes() }
        // each entry: 9 key bytes, the place in 5 big-endian bytes, the size in 4 little-endian; the storage's greatest size as the game's own files name it
        val one = files.first { CascWriter.sortedEnd(it.readBytes())!! > 40 }.readBytes()
        assertEquals(30 + 24, (one[54].toInt() and 255) or ((one[55].toInt() and 255) shl 8)); assertEquals(0, one[56].toInt()); assertEquals(0, one[57].toInt())
        org.junit.Assert.assertArrayEquals(byteArrayOf(0, 0, 0, 0xC0.toByte(), 0xFF.toByte(), 0, 0, 0), one.copyOfRange(16, 24))
        assertFalse(CascWriter.legacy(one))
        // an earlier download's files (up to build 381): no section, 1 GiB named, sizes big-endian. Made right in place, the data untouched.
        val dataLength = java.io.File(dir, "data.000").length()
        for (f in files) {
            val b = f.readBytes(); val e = CascWriter.sortedEnd(b)!!
            val old = b.copyOf(e)
            for (k in 16 until 24) old[k] = 0; old[19] = 0x40
            for (p in 40 until e step 18) { val t = old.copyOfRange(p + 14, p + 18); for (k in 0 until 4) old[p + 14 + k] = t[3 - k] }
            assertTrue(CascWriter.legacy(old))
            f.writeBytes(old)
        }
        assertEquals(300, CascWriter(dir).count)
        assertEquals(16, CascWriter.repairIndexes(dir))
        val after = dir.listFiles { f -> f.name.endsWith(".idx") }!!
        assertEquals(16, after.size)
        for (f in after) org.junit.Assert.assertArrayEquals(files.first { it.name.substring(0, 2) == f.name.substring(0, 2) }.let { whole[it.name] }, f.readBytes())
        assertEquals(dataLength, java.io.File(dir, "data.000").length())
        assertEquals(0, CascWriter.repairIndexes(dir))
        val again = CascWriter(dir)
        assertEquals(300, again.count)
        org.junit.Assert.assertArrayEquals("BLTE".toByteArray() + ByteArray(20) { 7 }, again.read(ByteArray(16) { if (it < 2) (7 shr (8 * it)).toByte() else (it * 7).toByte() }))
        // what the game keeps beside its index files goes when they are written again
        java.io.File(dir, "shmem").writeText("x"); again.finish(); assertFalse(java.io.File(dir, "shmem").exists())
    }

    @Test fun aFolderNamedInTwoCasesIsOneFolderAndTheGameSaysWhichProductItIs() {
        val base = tmp.newFolder("programs")
        assertEquals(File(base, "Utils/chrome_elf.dll"), TactInstaller.placeFor(base, "Utils\\chrome_elf.dll"))
        File(base, "Utils/locales").mkdirs()
        assertEquals(File(base, "Utils/LIBCEF.DLL"), TactInstaller.placeFor(base, "UTILS\\LIBCEF.DLL"))
        assertEquals(File(base, "Utils/locales/DE.PAK"), TactInstaller.placeFor(base, "UTILS\\LOCALES\\DE.PAK"))
        assertEquals(File(base, "Wow.exe"), TactInstaller.placeFor(base, "Wow.exe"))
        // an install made before: two folders, merged into the fuller one, nothing lost, a file there already kept
        val old = tmp.newFolder("old")
        File(old, "Utils/locales").mkdirs(); File(old, "UTILS/LOCALES").mkdirs()
        File(old, "Utils/a.dll").writeText("a"); File(old, "Utils/b.dll").writeText("b"); File(old, "Utils/locales/it.pak").writeText("it")
        File(old, "UTILS/LIBCEF.DLL").writeText("cef"); File(old, "UTILS/LOCALES/DE.PAK").writeText("de"); File(old, "UTILS/A.DLL").writeText("other")
        assertEquals(1, TactInstaller.mergeCaseFolders(old))
        assertEquals(listOf("Utils"), old.list()!!.toList())
        assertEquals("cef", File(old, "Utils/LIBCEF.DLL").readText()); assertEquals("de", File(old, "Utils/locales/DE.PAK").readText())
        assertEquals("it", File(old, "Utils/locales/it.pak").readText()); assertEquals("a", File(old, "Utils/a.dll").readText())
        assertEquals(0, TactInstaller.mergeCaseFolders(old))
        // the flavor file, and the product read from the install's record
        assertTrue(TactInstaller.writeFlavor(old, "_forever_", "wowf")); assertFalse(TactInstaller.writeFlavor(old, "_forever_", "wowf"))
        assertEquals("Product Flavor!STRING:0\nwowf\n", File(old, "_forever_/.flavor.info").readText())
        assertEquals("wowf", TactInstaller.productOf("Branch!STRING:0|Active!DEC:1|Product!STRING:0\nus|1|wowf\n")); assertNull(TactInstaller.productOf(""))
    }

    @Test fun winesAdapterListingIsFixedInTheOneKnownFileOnly() {
        val fix = com.logie.blizz.game.WineAdapterFix
        val dll = ByteArray(0x6000) { (it * 7).toByte() }
        val hash = fix.sha256(dll)
        val fixed = fix.fixed(dll, original = hash)!!
        org.junit.Assert.assertArrayEquals(byteArrayOf(0xB8.toByte(), 0xE8.toByte(), 0, 0, 0, 0xC3.toByte()), fixed.copyOfRange(0x4cb0, 0x4cb6))
        org.junit.Assert.assertArrayEquals(dll.copyOf(0x4cb0), fixed.copyOf(0x4cb0))
        org.junit.Assert.assertArrayEquals(dll.copyOfRange(0x4cb6, dll.size), fixed.copyOfRange(0x4cb6, fixed.size))
        assertEquals(null, fix.fixed(dll)); assertEquals(null, fix.fixed(fixed, original = hash))
        // Wine's real file, when the test is pointed at it (BLIZZ_WINE_IPHLPAPI): the hashes written down are its
        System.getenv("BLIZZ_WINE_IPHLPAPI")?.let { path ->
            val real = java.io.File(path).readBytes()
            assertEquals(fix.ORIGINAL, fix.sha256(real)); assertEquals(fix.FIXED, fix.sha256(fix.fixed(real)!!))
        }
    }

    /** An earlier download in BLIZZ_FOREVER_REPAIR completed as Play does it (not run without it). */
    @Test fun anEarlierRealDownloadCompletedWhenAsked() {
        val root = System.getenv("BLIZZ_FOREVER_REPAIR")?.let { java.io.File(it) } ?: return
        println("index files completed: " + CascWriter.repairIndexes(java.io.File(root, "Data/data")))
        println("metadata files added: " + com.logie.blizz.forevernew.ForeverClientDownload.repairIndex(root) { text, _ -> println(text) })
        println("flavor written: " + TactInstaller.writeFlavor(root, "_forever_", TactInstaller.productOf(java.io.File(root, ".build.info").readText())!!))
        println("folders merged: " + TactInstaller.mergeCaseFolders(java.io.File(root, "_forever_")))
    }

    /**
     * The entries of a storage the game made itself (BLIZZ_FOREVER_COPY_LIST: lines `segment offset size`, of the data files in
     * BLIZZ_FOREVER_COPY_FROM) written again by this app's writer into BLIZZ_FOREVER_COPY_TO: the same content in our format, to
     * start the game on at the desk (not run without them).
     */
    @Test fun aStorageTheGameMadeWrittenAgainByOurWriterWhenAsked() {
        val list = System.getenv("BLIZZ_FOREVER_COPY_LIST")?.let { java.io.File(it) } ?: return
        val from = java.io.File(System.getenv("BLIZZ_FOREVER_COPY_FROM")!!); val to = java.io.File(System.getenv("BLIZZ_FOREVER_COPY_TO")!!)
        val w = CascWriter(to); var n = 0
        val files = HashMap<Int, java.io.RandomAccessFile>()
        for (line in list.readLines()) {
            val (seg, off, size) = line.trim().split(' ').map { it.toLong() }
            val f = files.getOrPut(seg.toInt()) { java.io.RandomAccessFile(java.io.File(from, "data.%03d".format(seg)), "r") }
            val head = ByteArray(30); f.seek(off); f.readFully(head)
            val blte = ByteArray((size - 30).toInt()); f.readFully(blte)
            if (String(blte, 0, 4, Charsets.ISO_8859_1) != "BLTE") continue
            w.add(ByteArray(16) { head[15 - it] }, blte); n++
        }
        w.finish(); println("entries written again: $n of ${list.readLines().size}")
    }

    /** A real essential download into BLIZZ_FOREVER_FRESH (not run without it): what the game is started on at the desk. */
    @Test fun aRealEssentialDownloadWhenAsked() {
        val root = System.getenv("BLIZZ_FOREVER_FRESH")?.let { java.io.File(it) } ?: return
        com.logie.blizz.forevernew.ForeverClientDownload.download(root, 0, emptyList(), { text, _ -> println(text) })
    }
}
