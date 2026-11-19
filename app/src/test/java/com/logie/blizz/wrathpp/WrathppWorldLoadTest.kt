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
}
