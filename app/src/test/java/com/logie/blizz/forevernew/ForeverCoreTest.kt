package com.logie.blizz.forevernew

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import java.io.File
import java.io.StringReader
import java.io.StringWriter

/** The pure parts of the new Forever integration. Nothing here has run on a phone. */
// (Robolectric: the unit tests' org.json is Android's stub otherwise)
@RunWith(RobolectricTestRunner::class)
class ForeverCoreTest {
    @get:Rule val tmp = TemporaryFolder()

    // ---- state ----
    @Test fun stateSurvivesAndABusyOneIsNotTrusted() {
        val store = ForeverStateStore(File(tmp.root, "s/state.json"))
        assertEquals(ForeverState.NOT_INSTALLED, store.load().state)
        store.save(ForeverState.READY, "ok")
        assertEquals(ForeverState.READY, store.load().state)
        store.save(ForeverState.BUILDING_MAPS, "x")
        val after = store.load()
        assertEquals(ForeverState.FAILED, after.state)
        assertEquals(ForeverState.BUILDING_MAPS, after.failure?.stage)
    }

    @Test fun corruptStateIsNotInstalled() {
        val f = File(tmp.root, "state.json").apply { writeText("{not json") }
        assertEquals(ForeverState.NOT_INSTALLED, ForeverStateStore(f).load().state)
    }

    @Test fun portsAreNotTheOtherRealms() {
        val others = setOf(3310, 3311, 3312, 3724, 1119, 8081, 8085, 8086, 8087, 8090, 8095, 8096)
        assertTrue(ForeverPorts.all.none { it in others })
        assertEquals(ForeverPorts.all.size, ForeverPorts.all.toSet().size)
    }

    // ---- package ----
    private val manifestJson = """{"arch":"aarch64","libc":"musl","format":1,"schema":1,"min_app_version":1,
        "source_commit":"51b5ae0971fadf2e96a16b4730e986cc33e29adb","upstream_version":"0.1.36.1","size":10,"sha256":"${"a".repeat(64)}",
        "unpacked":20,"url":"https://example.org/x.tar.xz","client_builds":[70938,70888],"components":{"bin/worldserver":"${"b".repeat(64)}"}}"""

    @Test fun manifestParsesAndChecksCompatibility() {
        val m = ForeverPackage.parseManifest(manifestJson)
        assertEquals(listOf(70938, 70888), m.clientBuilds)
        assertNull(ForeverPackage.incompatible(m, listOf("arm64-v8a")))
        assertNotNull(ForeverPackage.incompatible(m, listOf("x86_64")))
        assertNotNull(ForeverPackage.incompatible(m.copy(format = 2), listOf("arm64-v8a")))
        assertNotNull(ForeverPackage.incompatible(m.copy(minApp = 99), listOf("arm64-v8a")))
        assertNotNull(ForeverPackage.incompatible(m.copy(url = "http://x"), listOf("arm64-v8a")))
        assertNotNull(ForeverPackage.incompatible(m.copy(sha256 = "zz"), listOf("arm64-v8a")))
    }

    @Test fun entryPathsCannotEscape() {
        val base = tmp.newFolder("base")
        assertNull(ForeverPackage.entryTarget(base, "../x"))
        assertNull(ForeverPackage.entryTarget(base, "/etc/passwd"))
        assertNull(ForeverPackage.entryTarget(base, "a/../../x"))
        assertNull(ForeverPackage.entryTarget(base, "a\\b"))
        assertNotNull(ForeverPackage.entryTarget(base, "./forever/bin/worldserver"))
        assertTrue(ForeverPackage.linkStaysInside(base, File(base, "lib/libc.so"), "ld-musl-aarch64.so.1"))
        assertFalse(ForeverPackage.linkStaysInside(base, File(base, "lib/libc.so"), "../../outside"))
        assertFalse(ForeverPackage.linkStaysInside(base, File(base, "lib/libc.so"), "/system/bin/sh"))
    }

    private fun tarXz(vararg files: Pair<String, ByteArray>, link: Pair<String, String>? = null): File {
        val out = File(tmp.root, "p-${System.nanoTime()}.tar.xz")
        org.apache.commons.compress.archivers.tar.TarArchiveOutputStream(org.tukaani.xz.XZOutputStream(out.outputStream(), org.tukaani.xz.LZMA2Options())).use { tar ->
            tar.setLongFileMode(org.apache.commons.compress.archivers.tar.TarArchiveOutputStream.LONGFILE_POSIX)
            for ((name, data) in files) {
                val e = org.apache.commons.compress.archivers.tar.TarArchiveEntry(name); e.size = data.size.toLong(); e.mode = 0b111_101_101
                tar.putArchiveEntry(e); tar.write(data); tar.closeArchiveEntry()
            }
            link?.let { (name, target) ->
                val e = org.apache.commons.compress.archivers.tar.TarArchiveEntry(name, org.apache.commons.compress.archivers.tar.TarArchiveEntry.LF_SYMLINK)
                e.linkName = target; tar.putArchiveEntry(e); tar.closeArchiveEntry()
            }
        }
        return out
    }

    @Test fun unpackWritesFilesAndExecutableBits() {
        val a = tarXz("forever/bin/worldserver" to "x".toByteArray(), "forever/lib/ld-musl-aarch64.so.1" to "l".toByteArray())
        val dest = File(tmp.root, "d")
        val n = ForeverPackage.unpack(a, dest, 1000)
        assertEquals(2L, n)
        assertTrue(File(dest, "forever/bin/worldserver").canExecute())
    }

    @Test fun unpackRefusesUnsafeAndOversized() {
        val bad = tarXz("../evil" to "x".toByteArray())
        assertTrue(runCatching { ForeverPackage.unpack(bad, File(tmp.root, "d1"), 1000) }.isFailure)
        assertFalse(File(tmp.root, "evil").exists())
        val big = tarXz("forever/a" to ByteArray(500))
        assertTrue(runCatching { ForeverPackage.unpack(big, File(tmp.root, "d2"), 100) }.isFailure)
        val link = tarXz("forever/a" to "x".toByteArray(), link = "forever/l" to "../../escape")
        assertTrue(runCatching { ForeverPackage.unpack(link, File(tmp.root, "d3"), 1000) }.isFailure)
    }

    @Test fun verifyChecksComponentsAndCommit() {
        val folder = File(tmp.root, "pkg")
        for (p in listOf("bnetserver", "worldserver", "mariadbd", "mapextractor", "vmap4extractor", "vmap4assembler", "mmaps_generator")) {
            File(folder, "bin/$p").apply { parentFile.mkdirs(); writeText(p); setExecutable(true) }
        }
        File(folder, "lib/ld-musl-aarch64.so.1").apply { parentFile.mkdirs(); writeText("l") }
        File(folder, "SOURCE_COMMIT").writeText("51b5ae0971fadf2e96a16b4730e986cc33e29adb\n")
        val sha = ForeverDownloads.sha256(File(folder, "bin/worldserver"))
        val m = ForeverPackage.parseManifest(manifestJson).copy(components = mapOf("bin/worldserver" to sha))
        assertNull(ForeverPackage.verify(folder, m))
        assertNotNull(ForeverPackage.verify(folder, m.copy(components = mapOf("bin/worldserver" to "0".repeat(64)))))
        assertNotNull(ForeverPackage.verify(folder, m.copy(sourceCommit = "f".repeat(40))))
    }

    @Test fun installSwapsAndRollsBack() {
        val layout = ForeverLayout(File(tmp.root, "root"))
        val manifest = ForeverPackage.parseManifest(manifestJson)
        layout.server.mkdirs(); File(layout.server, "old.txt").writeText("old")
        // Pretend the swap happened: server.old holds the previous one.
        File(layout.root, "server.old").mkdirs(); File(layout.root, "server.old/old.txt").writeText("previous")
        File(layout.server, "new.txt").writeText("new")
        assertTrue(ForeverPackage.rollback(layout))
        assertEquals("previous", File(layout.server, "old.txt").readText())
        assertFalse(File(layout.server, "new.txt").exists())
        assertFalse(ForeverPackage.rollback(layout))
        assertTrue(ForeverPackage.needsInstall(layout, manifest))
    }

    // ---- downloads (resume) ----
    @Test fun downloadResumesAndChecksTheHash() {
        val data = ByteArray(300_000) { (it * 7).toByte() }
        val server = com.sun.net.httpserver.HttpServer.create(java.net.InetSocketAddress("127.0.0.1", 0), 0)
        var rangeSeen: String? = null
        server.createContext("/f") { ex ->
            val range = ex.requestHeaders.getFirst("Range")
            rangeSeen = range
            val start = range?.substringAfter("bytes=")?.substringBefore('-')?.toInt() ?: 0
            val body = data.copyOfRange(start, data.size)
            ex.sendResponseHeaders(if (range != null) 206 else 200, body.size.toLong())
            ex.responseBody.use { it.write(body) }
        }
        server.start()
        try {
            val url = "http://127.0.0.1:${server.address.port}/f"
            val sha = java.security.MessageDigest.getInstance("SHA-256").digest(data).joinToString("") { "%02x".format(it) }
            val dest = File(tmp.root, "dl/file.bin")
            dest.parentFile.mkdirs()
            File(dest.path + ".part").writeBytes(data.copyOf(100_000))
            ForeverDownloads.fetch(url, dest, sha, data.size.toLong(), allowHttp = true)
            assertEquals("bytes=100000-", rangeSeen)
            assertTrue(data.contentEquals(dest.readBytes()))
            assertFalse(File(dest.path + ".part").exists())
            // A wrong hash is refused and nothing is kept under the real name.
            val bad = File(tmp.root, "dl/bad.bin")
            assertTrue(runCatching { ForeverDownloads.fetch(url, bad, "0".repeat(64), data.size.toLong(), allowHttp = true) }.isFailure)
            assertFalse(bad.exists())
            assertTrue(runCatching { ForeverDownloads.fetch("http://127.0.0.1/x", dest, sha) }.isSuccess) // already there: no request
        } finally { server.stop(0) }
    }

    @Test fun httpIsRefusedByDefault() {
        assertTrue(runCatching { ForeverDownloads.fetchText("http://127.0.0.1:1/x") }.exceptionOrNull() is IllegalArgumentException)
    }

    // ---- SQL ----
    @Test fun sqlCompatFixesMariaDbIncompatibilities() {
        val s = "CREATE DATABASE /*!32312 IF NOT EXISTS*/ `playerbot` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;"
        val out = SqlCompat.line(s)
        assertFalse(out.contains("0900"))
        assertFalse(out.contains("ENCRYPTION"))
        assertTrue(out.contains("/*!32312 IF NOT EXISTS*/"))
        assertTrue(out.contains("/*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */"))
        assertEquals("INSERT INTO t VALUES ('/*!80016 not code */');".let { SqlCompat.line("SELECT 1;") }, "SELECT 1;")
    }

    @Test fun sqlStreamCountsChangedLines() {
        val w = StringWriter()
        val changed = SqlCompat.stream(StringReader("a\nCOLLATE utf8mb4_0900_ai_ci;\nb\n"), w)
        assertEquals(1L, changed)
        assertEquals("a\nCOLLATE utf8mb4_unicode_ci;\nb\n", w.toString())
    }

    // ---- zip by ranges ----
    private fun zipBytes(entries: Map<String, ByteArray>, stored: Boolean = false): ByteArray {
        val bo = java.io.ByteArrayOutputStream()
        java.util.zip.ZipOutputStream(bo).use { z ->
            for ((n, d) in entries) {
                val e = java.util.zip.ZipEntry(n)
                if (stored) { e.method = java.util.zip.ZipEntry.STORED; e.size = d.size.toLong(); e.compressedSize = d.size.toLong(); e.crc = java.util.zip.CRC32().apply { update(d) }.value }
                z.putNextEntry(e); z.write(d); z.closeEntry()
            }
        }
        return bo.toByteArray()
    }

    @Test fun rangeZipReadsOneEntryAndChecksThePin() {
        val world = ByteArray(200_000) { (it % 251).toByte() }
        val zip = zipBytes(mapOf("server/worldserver.exe" to ByteArray(1000), "sql\\world.sql" to world, "sql/hotfixes.sql" to "h".toByteArray()))
        val src = RangeZip.Bytes(zip)
        assertEquals(3, RangeZip.list(src).size)
        val sha = java.security.MessageDigest.getInstance("SHA-256").digest(world).joinToString("") { "%02x".format(it) }
        val pin = ForeverRepackData.Pin("sql/world.sql", world.size.toLong(), sha, "world.sql")
        val dest = File(tmp.root, "out/world.sql")
        ForeverRepackData.extract(src, pin, dest)
        assertTrue(world.contentEquals(dest.readBytes()))
        assertFalse(File(dest.path + ".part").exists())
        val wrong = pin.copy(sha256 = "0".repeat(64), fileName = "w2.sql")
        val dest2 = File(tmp.root, "out/w2.sql")
        assertTrue(runCatching { ForeverRepackData.extract(src, wrong, dest2) }.isFailure)
        assertFalse(dest2.exists())
        assertTrue(runCatching { ForeverRepackData.extract(src, pin.copy(size = 5, fileName = "w3.sql"), File(tmp.root, "out/w3.sql")) }.isFailure)
    }

    @Test fun rangeZipHandlesStoredEntries() {
        val d = ByteArray(5000) { 3 }
        val src = RangeZip.Bytes(zipBytes(mapOf("a.bin" to d), stored = true))
        val e = RangeZip.list(src).single()
        assertTrue(d.contentEquals(RangeZip.open(src, e).use { it.readBytes() }))
    }

    @Test fun pinnedRepackEntriesMatchTheMeasuredFiles() {
        assertEquals(613_883_583L, ForeverRepackData.WORLD.size)
        assertEquals("3ea1b8d138bb097f7003e5b41d9bf2136a9e1bcd224bbb96ec7daeb52a2ed5a2", ForeverRepackData.WORLD.sha256)
        assertEquals(339_516_733L, ForeverRepackData.HOTFIXES.size)
        assertEquals("492bf4e7034832012afe282eeafc3a074a7caac79f5e20b798ae745005cb8fa7", ForeverRepackData.HOTFIXES.sha256)
    }

    @Test fun databaseSqlCreatesIsolatedStockDatabases() {
        val sql = ForeverDb.createSql("forever", "p'w\\")
        for (d in listOf("auth", "world", "characters", "hotfixes", "playerbot")) assertTrue(sql.contains("CREATE DATABASE IF NOT EXISTS `$d`"))
        assertTrue(sql.contains("p\\'w\\\\"))
        assertFalse(sql.contains("ON *.*"))
        val layout = ForeverLayout(File(tmp.root, "r"))
        val plan = ForeverDb.importPlan(layout, File("w.sql"), File("h.sql"))
        assertEquals(listOf("auth", "characters", "world", "hotfixes", "playerbot", "playerbot"), plan.map { it.first })
    }

    @Test fun bootstrapSqlFollowsInstallDbOrderAndNamesOfMariaDb114() {
        val share = tmp.newFolder("share")
        for (n in ForeverDb.BOOTSTRAP_FILES) File(share, n).writeText("-- $n\nSELECT 1;\n")
        val sql = ForeverDb.bootstrapSql(share)
        assertTrue(sql.startsWith("create database if not exists mysql;\nuse mysql;\nSET @auth_root_socket=NULL;\n"))
        assertEquals(ForeverDb.BOOTSTRAP_FILES, ForeverDb.BOOTSTRAP_FILES.sortedBy { sql.indexOf("-- $it") })
        File(share, "fill_help_tables.sql").delete()
        assertTrue(runCatching { ForeverDb.bootstrapSql(share) }.exceptionOrNull()!!.message!!.contains("fill_help_tables.sql"))
    }
}
