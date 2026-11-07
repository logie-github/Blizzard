package com.logie.blizz.importer

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

class SourceCleanupTest {
    @get:Rule val tmp = TemporaryFolder()

    private fun picked(id: String, file: File) = id to Supplied.Picked(id, FileNode(file))

    @Test fun thePickedFilesGoAfterASuccessfulImportAndNothingElseDoes() {
        val downloads = tmp.newFolder("downloads")
        val zip = File(downloads, "Diablo II.zip").apply { writeText("z") }
        val neighbour = File(downloads, "holiday.jpg").apply { writeText("j") }
        val appFiles = tmp.newFolder("files")
        val outcome = SourceCleanup.run(mapOf(picked("install", zip)), appFiles)
        assertFalse(zip.exists())
        assertTrue(neighbour.exists())
        assertEquals(listOf("Diablo II.zip"), outcome.deleted)
        assertEquals("Deleted what you picked: Diablo II.zip.", outcome.summary)
    }

    @Test fun aFolderIsNeverDeletedAndTheConsoleKeysAreKept() {
        val folder = tmp.newFolder("Downloads").also { File(it, "a.bin").writeText("a") }
        val keys = File(tmp.root, "prod.keys").apply { writeText("k") }
        val nsp = File(tmp.root, "base.nsp").apply { writeText("n") }
        val outcome = SourceCleanup.run(mapOf(picked("install", folder), picked("keys", keys), picked("base", nsp)), tmp.newFolder("files"))
        assertTrue(File(folder, "a.bin").exists() && keys.exists())
        assertFalse(nsp.exists())
        assertEquals(listOf("base.nsp"), outcome.deleted)
        assertEquals(listOf("Downloads (a folder)"), outcome.kept)
    }

    @Test fun theAppsOwnFilesAreNeverTouched() {
        val appFiles = tmp.newFolder("files")
        val inside = File(appFiles, "games/x/Game.exe").apply { parentFile!!.mkdirs(); writeText("exe") }
        val outcome = SourceCleanup.run(mapOf(picked("install", inside)), appFiles)
        assertTrue(inside.exists())
        assertTrue(outcome.deleted.isEmpty())
    }

    @Test fun nothingPickedSaysNothing() {
        assertNull(SourceCleanup.run(mapOf("keys" to Supplied.Skipped("keys")), tmp.newFolder("files")).summary)
    }
}
