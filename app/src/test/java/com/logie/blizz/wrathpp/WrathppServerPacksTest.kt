package com.logie.blizz.wrathpp

import com.logie.blizz.wow.WowLayout
import org.apache.commons.compress.archivers.tar.TarArchiveEntry
import org.apache.commons.compress.archivers.tar.TarArchiveOutputStream
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.tukaani.xz.LZMA2Options
import org.tukaani.xz.XZOutputStream
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.IOException
import java.security.MessageDigest

/** Wrath++'s server install from its packs (format 2), against real tar.xz packs made here and served from a folder. */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class WrathppServerPacksTest {
    @get:Rule val tmp = TemporaryFolder()

    private fun hex(bytes: ByteArray) = MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }

    /** A tar.xz of [files] (path under server/ to bytes), the way the repack tool writes one. */
    private fun tarXz(files: Map<String, ByteArray>, dirs: List<String> = emptyList(), exec: Set<String> = emptySet()): ByteArray {
        val out = ByteArrayOutputStream()
        TarArchiveOutputStream(XZOutputStream(out, LZMA2Options(1))).use { tar ->
            tar.setLongFileMode(TarArchiveOutputStream.LONGFILE_POSIX)
            for (d in dirs) {
                tar.putArchiveEntry(TarArchiveEntry("server/$d/")); tar.closeArchiveEntry()
            }
            for ((path, data) in files) {
                val e = TarArchiveEntry("server/$path")
                e.size = data.size.toLong()
                e.mode = if (path in exec) 493 else 420
                tar.putArchiveEntry(e); tar.write(data); tar.closeArchiveEntry()
            }
        }
        return out.toByteArray()
    }

    private class Built(val manifest: WrathppServerPackage.Manifest, val served: File, val opened: MutableList<String>)

    /** The release's folder: a core pack (ctl.sh, the world server), a shareable immutable sql pack, a shareable runtime pack, an optional payload. */
    private fun release(sqlOverride: ByteArray? = null): Built {
        val served = tmp.newFolder("release")
        val core = mapOf("ctl.sh" to "#!/bin/sh\n".toByteArray(), "bin/worldserver" to "ELF-world".toByteArray())
        val sqlFiles = mapOf("src/data/sql/base/a.sql" to "INSERT 1;".toByteArray(), "src/data/sql/updates/b.sql" to "INSERT 2;".toByteArray())
        val runtimeFiles = mapOf("bin/mariadbd" to "ELF-maria".toByteArray(), "lib/libc.so" to "libc".toByteArray())
        val payload = mapOf("src/modules/mod-x/data/files/Character/big.m2" to ByteArray(5000) { it.toByte() })
        fun pack(name: String, files: Map<String, ByteArray>, dirs: List<String> = emptyList(), exec: Set<String> = emptySet(),
                 optional: Boolean = false, shareable: Boolean = false, immutable: Boolean = false, listed: Map<String, ByteArray> = files): WrathppServerPackage.Pack {
            val data = tarXz(files, dirs, exec)
            File(served, "wrathpp-server-$name.tar.xz").writeBytes(data)
            return WrathppServerPackage.Pack(
                name, "wrathpp-server-$name.tar.xz", data.size.toLong(), hex(data), files.values.sumOf { it.size.toLong() }, optional, shareable, immutable,
                if (shareable) listed.map { (p, b) -> WrathppServerPackage.PackFile(p, b.size.toLong(), hex(b), if (p in exec) 493 else 420) } else emptyList(),
                dirs,
            )
        }
        val packs = listOf(
            pack("core", core, exec = setOf("ctl.sh", "bin/worldserver")),
            pack("sql", sqlOverride?.let { sqlFiles + ("src/data/sql/base/a.sql" to it) } ?: sqlFiles, dirs = listOf("src/data/sql/custom"), shareable = true, immutable = true,
                listed = sqlFiles),
            pack("runtime", runtimeFiles, exec = setOf("bin/mariadbd"), shareable = true),
            pack("payload-mod-x", payload, optional = true),
        )
        val manifest = WrathppServerPackage.Manifest(size = 1, sha256 = "feed", unpacked = 0, format = 2, protocol = 1, packs = packs)
        // The packs are opened on parallel threads: a list they can all add to.
        return Built(manifest, served, java.util.Collections.synchronizedList(mutableListOf()))
    }

    private fun source(b: Built) = WrathppServerPackage.Source { name ->
        b.opened += name
        val f = File(b.served, name)
        if (!f.isFile) throw WrathppServerPackage.NotPublished("no $name")
        f.inputStream()
    }

    private fun layout() = WowLayout(tmp.newFolder("files"), tmp.newFolder(".export"))

    private fun sha(f: File) = hex(f.readBytes())

    @Test fun theManifestReadsItsPacksAndFormat1StillParses() {
        val b = release()
        val json = org.json.JSONObject().put("size", 5).put("sha256", "ab").put("unpacked", 9).put("format", 2).put("protocol", 1)
            .put("packs", org.json.JSONArray().put(org.json.JSONObject().put("name", "sql").put("file", "f").put("size", 3).put("sha256", "cd")
                .put("unpacked", 7).put("optional", false).put("shareable", true).put("immutable", true)
                .put("files", org.json.JSONArray().put(org.json.JSONObject().put("path", "src/a").put("size", 1).put("sha256", "ef").put("mode", 420)))
                .put("dirs", org.json.JSONArray().put("src/c"))))
        val m = WrathppServerPackage.parseManifest(json.toString())
        assertEquals(1, m.packs.size)
        assertTrue(m.packs[0].shareable && m.packs[0].immutable)
        assertEquals("src/a", m.packs[0].files[0].path)
        assertEquals(listOf("src/c"), m.packs[0].dirs)
        assertEquals(emptyList<WrathppServerPackage.Pack>(), WrathppServerPackage.parseManifest("""{"size": 1, "sha256": "x"}""").packs)
        assertEquals(listOf("core", "sql", "runtime"), WrathppServerPackage.requiredPacks(b.manifest).map { it.name })
    }

    @Test fun installsEveryRequiredPackAndNotTheOptionalOne() {
        val b = release()
        val l = layout()
        WrathppServerPackage.install(l, b.manifest, { _, _ -> }, source(b))
        assertTrue(File(l.wrathppServer, "ctl.sh").isFile)
        assertEquals("ELF-world", File(l.wrathppServer, "bin/worldserver").readText())
        assertEquals("INSERT 1;", File(l.wrathppServer, "src/data/sql/base/a.sql").readText())
        assertTrue("an empty folder of the package is kept", File(l.wrathppServer, "src/data/sql/custom").isDirectory)
        assertTrue(File(l.wrathppServer, "bin/mariadbd").canExecute())
        assertFalse("optional: the module's client files stay out", File(l.wrathppServer, "src/modules/mod-x").exists())
        assertFalse(b.opened.contains("wrathpp-server-payload-mod-x.tar.xz"))
        assertEquals("feed", WrathppServerPackage.installedSha(l))
        assertFalse("nothing left over", File(l.root, "server-wrathpp.new").exists())
    }

    @Test fun takesFilesTheWrathPlusServerHasInsteadOfDownloadingThem() {
        val b = release()
        val l = layout()
        // Wrath+'s server: the same sql files (hard linked into Wrath++'s) and a runtime that differs by a byte.
        File(l.server, "src/data/sql/base").mkdirs(); File(l.server, "src/data/sql/updates").mkdirs()
        File(l.server, "src/data/sql/base/a.sql").writeText("INSERT 1;")
        File(l.server, "src/data/sql/updates/b.sql").writeText("INSERT 2;")
        File(l.server, "bin").mkdirs(); File(l.server, "lib").mkdirs()
        File(l.server, "bin/mariadbd").writeText("ELF-MARIA")
        File(l.server, "lib/libc.so").writeText("libc")
        WrathppServerPackage.install(l, b.manifest, { _, _ -> }, source(b))
        assertFalse("sql came from Wrath+'s folder", b.opened.contains("wrathpp-server-sql.tar.xz"))
        assertTrue("the runtime differed, so it was downloaded", b.opened.contains("wrathpp-server-runtime.tar.xz"))
        assertEquals("ELF-maria", File(l.wrathppServer, "bin/mariadbd").readText())
        assertEquals("INSERT 2;", File(l.wrathppServer, "src/data/sql/updates/b.sql").readText())
        assertTrue("its empty folder too", File(l.wrathppServer, "src/data/sql/custom").isDirectory)
        // Immutable files are links: the same file on disk (the isolation test treats these as read-only inputs).
        assertEquals(
            java.nio.file.Files.getAttribute(File(l.server, "src/data/sql/base/a.sql").toPath(), "unix:ino"),
            java.nio.file.Files.getAttribute(File(l.wrathppServer, "src/data/sql/base/a.sql").toPath(), "unix:ino"),
        )
        // Wrath+'s own folder was only read.
        assertEquals("ELF-MARIA", File(l.server, "bin/mariadbd").readText())
    }

    @Test fun aRuntimePackWhoseFilesMatchIsCopiedNotLinked() {
        val b = release()
        val l = layout()
        File(l.server, "bin").mkdirs(); File(l.server, "lib").mkdirs()
        File(l.server, "bin/mariadbd").writeText("ELF-maria")
        File(l.server, "lib/libc.so").writeText("libc")
        WrathppServerPackage.install(l, b.manifest, { _, _ -> }, source(b))
        assertFalse(b.opened.contains("wrathpp-server-runtime.tar.xz"))
        assertEquals("ELF-maria", File(l.wrathppServer, "bin/mariadbd").readText())
        assertTrue(File(l.wrathppServer, "bin/mariadbd").canExecute())
        File(l.wrathppServer, "bin/mariadbd").appendText("!")   // a write on Wrath++'s side
        assertEquals("ELF-maria", File(l.server, "bin/mariadbd").readText())
    }

    @Test fun aPackThatDoesNotMatchItsChecksumFailsTheInstall() {
        val b = release()
        // Flip a byte of the core pack in the release.
        val f = File(b.served, "wrathpp-server-core.tar.xz")
        val bytes = f.readBytes(); bytes[bytes.size / 2] = (bytes[bytes.size / 2] + 1).toByte(); f.writeBytes(bytes)
        val l = layout()
        try {
            WrathppServerPackage.install(l, b.manifest, { _, _ -> }, source(b))
            fail("a damaged pack must not install")
        } catch (e: IOException) {
            // either the checksum or the archive itself said so
        }
        assertFalse("nothing was put in place", l.wrathppServer.exists())
    }

    @Test fun aSecondTryKeepsThePacksAlreadyDone() {
        val b = release()
        val l = layout()
        val flaky = WrathppServerPackage.Source { name ->
            if (name.contains("runtime")) throw IOException("the connection dropped")
            b.opened += name
            File(b.served, name).inputStream()
        }
        try {
            WrathppServerPackage.install(l, b.manifest, { _, _ -> }, flaky)
            fail("the dropped pack must fail the install")
        } catch (e: IOException) {
            assertEquals("the connection dropped", e.message)
        }
        val staging = File(l.root, "server-wrathpp.new")
        val done = File(staging, ".packs").list().orEmpty().toSet()
        assertFalse("the failed pack isn't marked", done.contains("runtime"))
        b.opened.clear()
        WrathppServerPackage.install(l, b.manifest, { _, _ -> }, source(b))
        for (name in done) assertFalse("$name was done and isn't fetched again", b.opened.contains("wrathpp-server-$name.tar.xz"))
        assertTrue(b.opened.contains("wrathpp-server-runtime.tar.xz"))
        assertTrue(File(l.wrathppServer, "bin/mariadbd").isFile)
        assertEquals("feed", WrathppServerPackage.installedSha(l))
    }

    @Test fun progressIsReportedAndCountsBytesOfTheNeededPacks() {
        val b = release()
        val l = layout()
        val lines = ArrayList<String>()
        WrathppServerPackage.install(l, b.manifest, { text, _ -> lines += text }, source(b))
        assertTrue(lines.toString(), lines.isEmpty() || lines.all { it.startsWith("Installing Wrath++'s server (step 1 of 2)") })
    }
}
