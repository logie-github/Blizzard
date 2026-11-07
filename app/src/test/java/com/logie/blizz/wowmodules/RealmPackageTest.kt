package com.logie.blizz.wowmodules

import org.apache.commons.compress.archivers.tar.TarArchiveEntry
import org.apache.commons.compress.archivers.tar.TarArchiveOutputStream
import org.apache.commons.compress.archivers.tar.TarConstants
import org.apache.commons.compress.compressors.xz.XZCompressorOutputStream
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File
import java.io.IOException

class RealmPackageTest {
    @get:Rule
    val temp = TemporaryFolder()

    private fun slots(): RealmPackage.Slots {
        val root = File(temp.root, "game/files").also { it.mkdirs() }
        return RealmPackage.Slots(File(root, "server"), File(root, "server.new"), File(root, "server.old"), File(temp.root, "game/.server-stock"))
    }

    private fun realm(label: String) = mapOf(
        "server/ctl.sh" to "#!/bin/sh\n# $label\n",
        "server/bin/worldserver" to "world $label",
        "server/bin/authserver" to "auth $label",
        "server/bin/mariadbd" to "maria $label",
        "server/lib/ld-musl-aarch64.so.1" to "loader",
        "server/VERSION" to label,
    )

    private fun pack(name: String, files: Map<String, String>, more: (TarArchiveOutputStream) -> Unit = {}): File {
        val file = File(temp.root, name)
        TarArchiveOutputStream(XZCompressorOutputStream(file.outputStream())).use { tar ->
            tar.setLongFileMode(TarArchiveOutputStream.LONGFILE_POSIX)
            for ((path, text) in files) {
                val bytes = text.toByteArray()
                val entry = TarArchiveEntry(path)
                entry.size = bytes.size.toLong()
                entry.mode = 493 // 0755
                tar.putArchiveEntry(entry)
                tar.write(bytes)
                tar.closeArchiveEntry()
            }
            more(tar)
        }
        return file
    }

    /** The realm the WoW app exported: no stamp. */
    private fun ownRealm(slots: RealmPackage.Slots) {
        for ((path, text) in realm("own")) {
            val file = File(slots.server, path.removePrefix("server/"))
            file.parentFile!!.mkdirs()
            file.writeText(text)
        }
        // What Blizzard writes into it at a start.
        File(slots.server, "ctl.blizz.sh").writeText("copy")
    }

    private fun putIn(slots: RealmPackage.Slots, pack: File, stamp: String) {
        RealmPackage.unpackToStaging(pack, slots, stamp) { }
        RealmPackage.commit(slots)
    }

    @Test
    fun aPackageReplacesTheRealmAndTheRealmsOwnIsKept() {
        val slots = slots()
        ownRealm(slots)
        assertTrue(RealmPackage.isRealm(slots.server))
        assertNull(RealmPackage.stampOf(slots.server))
        val progress = ArrayList<Float>()
        val pack = pack("a.tar.xz", realm("modules"))
        RealmPackage.unpackToStaging(pack, slots, "52:modules:aaaaaaaa1111") { progress += it }
        assertTrue(progress.isNotEmpty())
        assertTrue(progress.all { it in 0f..1f })
        // Nothing has changed in the realm until the swap.
        assertEquals("world own", File(slots.server, "bin/worldserver").readText())
        RealmPackage.commit(slots)

        assertEquals("world modules", File(slots.server, "bin/worldserver").readText())
        assertEquals("52:modules:aaaaaaaa1111", RealmPackage.stampOf(slots.server))
        assertFalse(File(slots.server, "ctl.blizz.sh").exists())
        assertFalse(slots.staging.exists())
        assertFalse(slots.old.exists())
        assertTrue(RealmPackage.hasStock(slots))
        assertEquals("world own", File(slots.stock, "bin/worldserver").readText())
        assertTrue(File(slots.server, "ctl.sh").canExecute())
    }

    @Test
    fun aSecondRealmReplacesTheFirstAndTheStockStays() {
        val slots = slots()
        ownRealm(slots)
        putIn(slots, pack("a.tar.xz", realm("one")), "52:modules:aaaaaaaa1111")
        putIn(slots, pack("b.tar.xz", realm("two")), "52:modules:bbbbbbbb2222")
        assertEquals("world two", File(slots.server, "bin/worldserver").readText())
        assertEquals("52:modules:bbbbbbbb2222", RealmPackage.stampOf(slots.server))
        assertEquals("world own", File(slots.stock, "bin/worldserver").readText())
        assertFalse(slots.old.exists())
    }

    @Test
    fun theRealmsOwnComesBack() {
        val slots = slots()
        ownRealm(slots)
        putIn(slots, pack("a.tar.xz", realm("one")), "52:modules:aaaaaaaa1111")
        RealmPackage.restoreStock(slots)
        assertEquals("world own", File(slots.server, "bin/worldserver").readText())
        assertNull(RealmPackage.stampOf(slots.server))
        assertFalse(RealmPackage.hasStock(slots))
        assertFalse(slots.old.exists())
        try {
            RealmPackage.restoreStock(slots)
            fail("nothing is kept to put back")
        } catch (e: IOException) {
            assertEquals("world own", File(slots.server, "bin/worldserver").readText())
        }
    }

    @Test
    fun aPackageThatIsNotARealmChangesNothing() {
        val slots = slots()
        ownRealm(slots)
        val bad = pack("bad.tar.xz", realm("x") - "server/bin/worldserver")
        try {
            RealmPackage.unpackToStaging(bad, slots, "52:modules:aaaaaaaa1111") { }
            fail("not a realm")
        } catch (e: IOException) {
            assertTrue(e.message!!.contains("Not a realm package"))
        }
        assertFalse(slots.staging.exists())
        assertEquals("world own", File(slots.server, "bin/worldserver").readText())
        assertFalse(RealmPackage.hasStock(slots))

        val notXz = File(temp.root, "junk.tar.xz").also { it.writeText("not a package at all") }
        try {
            RealmPackage.unpackToStaging(notXz, slots, "s") { }
            fail("not xz")
        } catch (e: IOException) {
            // The realm in is untouched.
        }
        assertFalse(slots.staging.exists())
        assertTrue(RealmPackage.isRealm(slots.server))
    }

    @Test
    fun aTruncatedPackageIsRefused() {
        val slots = slots()
        ownRealm(slots)
        val good = pack("a.tar.xz", realm("one"))
        val cut = File(temp.root, "cut.tar.xz")
        cut.writeBytes(good.readBytes().copyOf(good.length().toInt() / 2))
        try {
            RealmPackage.unpackToStaging(cut, slots, "s") { }
            fail("cut short")
        } catch (e: IOException) {
            // Staging is gone, the realm stays.
        }
        assertFalse(slots.staging.exists())
        assertEquals("world own", File(slots.server, "bin/worldserver").readText())
    }

    @Test
    fun pathsOutOfTheFolderAreRefused() {
        val slots = slots()
        val up = pack("up.tar.xz", realm("x") + ("server/../../escaped.txt" to "no"))
        try {
            RealmPackage.unpackToStaging(up, slots, "s") { }
            fail("a path with ..")
        } catch (e: IOException) {
            assertTrue(e.message!!.startsWith("Bad path"))
        }
        assertFalse(File(temp.root, "game/escaped.txt").exists())
        assertFalse(File(temp.root, "escaped.txt").exists())
        assertFalse(slots.staging.exists())
    }

    @Test
    fun nothingIsWrittenThroughALinkThePackageMade() {
        val slots = slots()
        val outside = temp.newFolder("outside")
        val link = pack("link.tar.xz", realm("x")) { tar ->
            val entry = TarArchiveEntry("server/etc", TarConstants.LF_SYMLINK)
            entry.linkName = outside.path
            tar.putArchiveEntry(entry)
            tar.closeArchiveEntry()
            val bytes = "pwned".toByteArray()
            val file = TarArchiveEntry("server/etc/passwd")
            file.size = bytes.size.toLong()
            tar.putArchiveEntry(file)
            tar.write(bytes)
            tar.closeArchiveEntry()
        }
        try {
            RealmPackage.unpackToStaging(link, slots, "s") { }
            fail("a file through a link")
        } catch (e: IOException) {
            assertTrue(e.message!!.startsWith("Bad path"))
        }
        assertEquals(0, outside.list()!!.size)
        assertFalse(slots.staging.exists())
    }

    @Test
    fun linksInsideThePackageAreKept() {
        val slots = slots()
        val withLinks = pack("l.tar.xz", realm("x")) { tar ->
            val entry = TarArchiveEntry("server/lib/libfoo.so", TarConstants.LF_SYMLINK)
            entry.linkName = "ld-musl-aarch64.so.1"
            tar.putArchiveEntry(entry)
            tar.closeArchiveEntry()
        }
        RealmPackage.unpackToStaging(withLinks, slots, "s") { }
        val made = File(slots.staging, "lib/libfoo.so").toPath()
        assertTrue(java.nio.file.Files.isSymbolicLink(made))
        assertEquals("loader", File(slots.staging, "lib/libfoo.so").readText())
    }

    @Test
    fun aSwapCutShortIsMendedAtTheNextLook() {
        val slots = slots()
        ownRealm(slots)
        // The app stopped after the old realm moved aside and before the new one moved in.
        assertTrue(slots.server.renameTo(slots.old))
        slots.staging.mkdirs()
        File(slots.staging, "half").writeText("x")
        RealmPackage.recover(slots)
        assertEquals("world own", File(slots.server, "bin/worldserver").readText())
        assertFalse(slots.old.exists())
        assertFalse(slots.staging.exists())
        // A realm that is in already: what is left over goes.
        slots.old.mkdirs()
        RealmPackage.recover(slots)
        assertFalse(slots.old.exists())
        assertTrue(RealmPackage.isRealm(slots.server))
    }

    @Test
    fun checksumsTheFile() {
        val file = temp.newFile("abc.bin").also { it.writeText("abc") }
        assertEquals("ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad", RealmPackage.sha256(file))
    }
}
