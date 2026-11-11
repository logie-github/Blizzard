package com.logie.blizz.forever

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import java.nio.file.Files

class ForeverLauncherTest {
    @Test
    fun `find returns a placed launcher by any known name, else null`() {
        val client = Files.createTempDirectory("client").toFile()
        assertNull(ForeverLauncher.find(client))
        val exe = File(client, "WoWForeverLauncher.exe").apply { writeText("x") }
        assertEquals(exe, ForeverLauncher.find(client))
    }

    @Test
    fun `fileNameFor keeps a known launcher name and renames anything else`() {
        assertEquals("WoWForeverLauncher.exe", ForeverLauncher.fileNameFor("WoWForeverLauncher.exe"))
        assertEquals("ForeverLauncher.exe", ForeverLauncher.fileNameFor("ForeverLauncher.exe"))
        // Case-insensitive match keeps the known spelling of the picked file.
        assertEquals("wowforeverlauncher.exe", ForeverLauncher.fileNameFor("wowforeverlauncher.exe"))
        // An unknown name becomes the canonical one, so the client start finds it.
        assertEquals("WoWForeverLauncher.exe", ForeverLauncher.fileNameFor("something.exe"))
        assertEquals("WoWForeverLauncher.exe", ForeverLauncher.fileNameFor(null))
    }

    @Test
    fun `seedConfig writes the own-server config and does not clobber the launcher's own writes`() {
        val driveC = Files.createTempDirectory("drivec").toFile()
        ForeverLauncher.seedConfig(driveC)
        val cfg = File(driveC, "windows/config")
        assertEquals("own", File(cfg, "launcher-mode.txt").readText())
        assertEquals("F:\\client", File(cfg, "client.txt").readText())
        assertEquals("lang=en", File(cfg, "launcher-settings.txt").readText())

        // A file the launcher itself later changed is left alone on the next seed.
        File(cfg, "launcher-settings.txt").writeText("lang=ru\ntray=on")
        ForeverLauncher.seedConfig(driveC)
        assertEquals("lang=ru\ntray=on", File(cfg, "launcher-settings.txt").readText())
    }

    @Test
    fun `clearConfig removes the seeded config so seedConfig writes it afresh`() {
        val driveC = Files.createTempDirectory("drivec").toFile()
        ForeverLauncher.seedConfig(driveC)
        val cfg = File(driveC, "windows/config")
        assertTrue(File(cfg, "launcher-mode.txt").isFile)
        ForeverLauncher.clearConfig(driveC)
        assertFalse(cfg.exists())
        ForeverLauncher.seedConfig(driveC)
        assertEquals("own", File(cfg, "launcher-mode.txt").readText())
    }

    @Test
    fun `removePlaced deletes every known launcher name from the client folder`() {
        val client = Files.createTempDirectory("client").toFile()
        File(client, "WoWForeverLauncher.exe").writeText("new")
        File(client, "ForeverLauncher.exe").writeText("old")
        File(client, "Wow.exe").writeText("game")
        ForeverLauncher.removePlaced(client)
        assertNull(ForeverLauncher.find(client))
        assertFalse(File(client, "ForeverLauncher.exe").exists())
        // A non-launcher file in the folder is left alone.
        assertTrue(File(client, "Wow.exe").isFile)
    }

    @Test
    fun `the seeded server points at this app's realm`() {
        // The client path is the F: drive (this app's files/forever), where the client sits under client.
        assertEquals("F:\\client", ForeverLauncher.FILES.getValue("client.txt"))
        assertTrue("own" == ForeverLauncher.FILES.getValue("launcher-mode.txt"))
        assertFalse(ForeverLauncher.NAMES.isEmpty())
    }
}
