package com.logie.blizz.wrathpp

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

/** The world server's loader lines that go into Wrath++'s start report. */
class WrathppWorldLoadTest {
    @get:Rule val tmp = TemporaryFolder()

    @Test fun keepsTheLoaderLinesAndTheColoursComeOut() {
        val log = tmp.newFile("world.out")
        log.writeText(
            "2026-11-19 Some other line\n" +
                "\u001B[32m>> Loaded 12345 creature template definitions in 345 ms\u001B[0m\n" +
                "Loading quests...\n" +
                ">> Loaded 9000 quests in 80 ms\n" +
                "World initialized in 1 minutes 2 seconds\n",
        )
        val lines = WrathppSetup.worldLoadLines(log).lines()
        assertEquals(
            listOf(">> Loaded 12345 creature template definitions in 345 ms", ">> Loaded 9000 quests in 80 ms", "World initialized in 1 minutes 2 seconds"),
            lines,
        )
    }

    @Test fun saysSoWhenThereIsNothing() {
        assertEquals("no world.out", WrathppSetup.worldLoadLines(File(tmp.root, "world.out")))
        val log = tmp.newFile("empty.out").apply { writeText("nothing here\n") }
        assertTrue(WrathppSetup.worldLoadLines(log).startsWith("none"))
    }

    @Test fun onlyTheEndOfAHugeLogIsRead() {
        val log = tmp.newFile("big.out")
        log.writeText("x".repeat(6 shl 20) + "\n>> Loaded 1 things in 2 ms\n")
        assertEquals(">> Loaded 1 things in 2 ms", WrathppSetup.worldLoadLines(log))
    }

    /** The issue's body keeps the last 20,000 characters of its log: the setup's lines are the end of it, however long the rest is. */
    @Test fun theSetupsLinesAreTheEndOfTheStartReportsLog() {
        val setup = "looks: abc\nbody options package: the release's 12345678 taken in (88 models)\nbody options: Human (3 shapes); 23 races' displays\ncreator patch: WrathppCreate.lua 1\n"
        val log = WrathppSetup.startLog("WowWrathpp.exe: 1 bytes", "Data/patch-Z.MPQ: folder", List(600) { "creator: line $it ".padEnd(60, 'x') }, "Wrath++ registry 19", setup)
        assertTrue(log.length > 30_000)
        val kept = log.takeLast(20_000)
        assertTrue(kept.contains("--- the setup (setup.log) ---\nlooks: abc\n"))
        assertTrue(kept.endsWith("creator patch: WrathppCreate.lua 1"))
        assertTrue(kept.contains("body options: Human (3 shapes); 23 races' displays"))
    }
}
