package com.logie.blizz.importer

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

class LeftoversTest {
    @get:Rule val tmp = TemporaryFolder()

    private fun file(paths: GamePaths, rel: String, size: Int = 10) = File(paths.root, rel).apply { parentFile!!.mkdirs(); writeBytes(ByteArray(size)) }

    @Test fun anInstalledGamesImportLeftoversGoAndTheGameItsSavesAndStateStay() {
        val paths = GamePaths(tmp.newFolder())
        val game = file(paths, "games/sc2/SC2.exe")
        val save = file(paths, "saves/sc2/profile.dat")
        val state = file(paths, "state/library-sc2.json")
        val scratch = file(paths, "staging/sc2-scratch/big.zip", 1000)
        val work = file(paths, "staging/sc2-work/a", 500)
        val installer = file(paths, "staging/sc2-installer/out/x", 700)
        val old = file(paths, "games/.sc2.old/SC2.exe", 300)
        val other = file(paths, "staging/diablo-scratch/keep", 100)
        val freed = Leftovers.clean(paths, "sc2", othersImporting = false)
        assertEquals(1000L + 500 + 700 + 300, freed)
        for (gone in listOf(scratch, work, installer, old)) assertFalse(gone.path, gone.exists())
        for (kept in listOf(game, save, state, other)) assertTrue(kept.path, kept.exists())
    }

    @Test fun theLegacyDownloadersPiecesStayWhileAnotherImportRuns() {
        val paths = GamePaths(tmp.newFolder())
        file(paths, "downloads/legacy/piece1", 400)
        assertEquals(0L, Leftovers.clean(paths, "diablo2", othersImporting = true))
        assertTrue(File(paths.downloads, "legacy/piece1").exists())
        assertEquals(400L, Leftovers.clean(paths, "diablo2", othersImporting = false))
        assertFalse(File(paths.downloads, "legacy").exists())
    }

    @Test fun resurrectedsKeptDownloadsGoWithItsLeftovers() {
        val paths = GamePaths(tmp.newFolder())
        file(paths, "downloads/d2r-v1-module.apk", 800)
        file(paths, "downloads/something-else.bin", 50)
        assertEquals(800L, Leftovers.clean(paths, "diablo2_resurrected", othersImporting = true))
        assertTrue(File(paths.downloads, "something-else.bin").exists())
    }

    @Test fun anInstallersTemporaryFilesInTheGamesWindowsAreFound() {
        val driveC = tmp.newFolder("drive_c")
        File(driveC, "users/xuser/Temp/junk.tmp").apply { parentFile!!.mkdirs(); writeText("x") }
        File(driveC, "windows/temp/a").apply { parentFile!!.mkdirs(); writeText("y") }
        File(driveC, "users/xuser/Documents/keep.txt").apply { parentFile!!.mkdirs(); writeText("k") }
        assertEquals(setOf("junk.tmp", "a"), Leftovers.windowsTemp(driveC).map { it.name }.toSet())
    }
}
