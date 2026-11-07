package com.logie.blizz.importer

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

/** A repair that fails leaves the installation, and the player's characters and saves, as they were. */
class AssemblerRestoreTest {
    @get:Rule val tmp = TemporaryFolder()

    private fun setup(): Pair<GamePaths, Assembler> {
        val paths = GamePaths(tmp.newFolder())
        val game = paths.game("sc")
        File(game, "Game.exe").apply { parentFile!!.mkdirs(); writeText("exe") }
        File(game, "characters/Zed.cdb").apply { parentFile!!.mkdirs(); writeText("hero") }
        File(game, "Data/big.mpq").apply { parentFile!!.mkdirs(); writeText("mpq") }
        return paths to Assembler(paths, "sc")
    }

    @Test fun whatWasMovedIntoStagingGoesBackWhenTheImportIsAbandoned() {
        val (paths, asm) = setup()
        asm.begin()
        asm.reuse(listOf("Game.exe", "Data")) { true }
        asm.move(File(paths.game("sc"), "characters/Zed.cdb"), File(asm.staging, "characters/Zed.cdb"))
        assertFalse(File(paths.game("sc"), "Game.exe").exists())
        asm.abandon()
        assertEquals("exe", File(paths.game("sc"), "Game.exe").readText())
        assertEquals("mpq", File(paths.game("sc"), "Data/big.mpq").readText())
        assertEquals("hero", File(paths.game("sc"), "characters/Zed.cdb").readText())
        assertFalse(asm.staging.exists())
    }

    @Test fun aCommittedImportIsTheNewInstallationAndNothingIsPutBack() {
        val (paths, asm) = setup()
        asm.begin()
        asm.reuse(listOf("Game.exe")) { true }
        File(asm.staging, "New.txt").writeText("new")
        asm.commit()
        assertTrue(File(paths.game("sc"), "Game.exe").isFile && File(paths.game("sc"), "New.txt").isFile)
        assertFalse(File(paths.game("sc"), "characters").exists())
        asm.abandon()
        assertTrue(File(paths.game("sc"), "Game.exe").isFile)
    }
}
