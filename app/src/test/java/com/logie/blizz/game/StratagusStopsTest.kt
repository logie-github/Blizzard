package com.logie.blizz.game

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import java.nio.file.Files

class StratagusStopsTest {
    private fun dir(): File = Files.createTempDirectory("strat").toFile()

    @Test fun arguments_are_fullscreen_data_and_user_folder() {
        assertEquals(listOf("-F", "-d", "/g", "-u", "/g"), StratagusActivity.arguments("/g").toList())
    }

    @Test fun nothing_running_is_no_report() {
        assertNull(StratagusStops.take(dir(), "Warcraft", alive = { false }, log = { emptyList() }))
    }

    @Test fun a_live_process_is_no_report() {
        val d = dir()
        File(d, "running").writeText("123")
        File(d, "stderr.txt").writeText("boom")
        assertNull(StratagusStops.take(d, "Warcraft", alive = { true }, log = { emptyList() }))
        assertTrue(File(d, "running").isFile)
    }

    @Test fun a_quit_from_the_menu_is_no_report() {
        val d = dir()
        File(d, "running").writeText("123")
        File(d, "stderr.txt").writeText("x\nStratagus: exit 0\n")
        assertNull(StratagusStops.take(d, "Warcraft", alive = { false }, log = { emptyList() }))
        assertFalse(File(d, "running").exists())
    }

    @Test fun a_stop_with_errors_is_reported_once() {
        val d = dir()
        File(d, "running").writeText("123")
        File(d, "stderr.txt").writeText("Fatal signal 11")
        File(d, "stdout.txt").writeText("loading")
        val text = StratagusStops.take(d, "Warcraft II", alive = { false }, log = { listOf("F/libc: Fatal signal 11") })
        assertNotNull(text)
        assertTrue(text!!.contains("Fatal signal 11") && text.contains("loading") && text.contains("Android's log"))
        assertNull(StratagusStops.take(d, "Warcraft II", alive = { false }, log = { emptyList() }))
    }

    @Test fun silently_ended_is_no_report() {
        val d = dir()
        File(d, "running").writeText("123")
        assertNull(StratagusStops.take(d, "Warcraft", alive = { false }, log = { listOf("nothing") }))
    }
}
