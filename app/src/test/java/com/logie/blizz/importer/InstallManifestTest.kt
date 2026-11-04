package com.logie.blizz.importer

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

class InstallManifestTest {
    @get:Rule val tmp = TemporaryFolder()

    @Test fun aFingerprintTellsFilesApartWithoutTheirContent() {
        val a = tmp.newFile("a").apply { writeBytes(ByteArray(300_000) { 1 }) }
        val b = tmp.newFile("b").apply { writeBytes(ByteArray(300_000) { 1 }) }
        val c = tmp.newFile("c").apply { writeBytes(ByteArray(300_000) { 2 }) }
        assertEquals(InstallManifest.fingerprint(a), InstallManifest.fingerprint(b))
        assertNotEquals(InstallManifest.fingerprint(a), InstallManifest.fingerprint(c))
        assertTrue(InstallManifest.fingerprint(a).startsWith("300000 "))
    }

    @Test fun aFolderIsListedWithPathsSizesAndHashes() {
        val root = tmp.newFolder("game")
        File(root, "Data").mkdirs()
        File(root, "Data/x.mpq").writeBytes(ByteArray(10))
        File(root, "game.exe").writeBytes(ByteArray(5))
        val text = InstallManifest.describe(root, "Installed")
        assertTrue(text.startsWith("Installed: 2 files"))
        assertTrue("  Data/x.mpq  10 " in text)
        assertTrue("  game.exe  5 " in text)
        assertEquals("Gone: not there\n", InstallManifest.describe(File(root, "nope"), "Gone"))
    }

    @Test fun aHugeFolderIsSummarisedPerTopFolder() {
        val root = tmp.newFolder("big")
        repeat(30) { File(root, "a").mkdirs(); File(root, "a/f$it").writeBytes(ByteArray(it + 1)) }
        repeat(5) { File(root, "b").mkdirs(); File(root, "b/g$it").writeBytes(ByteArray(2)) }
        val text = InstallManifest.describe(root, "Big", limit = 10)
        assertTrue(text, "(the 5 largest of 35; per top folder:)" in text)
        assertTrue(text, "  a/  30 files" in text && "  b/  5 files" in text)
        assertFalse("a/f0 " in text)
    }
}
