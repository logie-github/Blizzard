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
    fun `seedConfig writes the launcher's config beside it, in the client folder`() {
        val client = Files.createTempDirectory("client").toFile()
        val driveC = Files.createTempDirectory("drivec").toFile()
        // What an earlier version left where the launcher never looks.
        File(driveC, "windows/config").apply { mkdirs() }.resolve("launcher-mode.txt").writeText("own")
        ForeverLauncher.seedConfig(client, driveC)
        val cfg = File(client, "config")
        assertEquals("own", File(cfg, "launcher-mode.txt").readText())
        // The game folder is the one with Wow.exe: with F:\client the launcher asks for it at PLAY NOW.
        assertEquals("F:\\client\\_forever_", File(cfg, "client.txt").readText())
        assertEquals("lang=en\n", File(cfg, "launcher-settings.txt").readText())
        assertFalse(File(driveC, "windows/config").exists())
    }

    @Test
    fun `server json names this realm with its own world port`() {
        val json = ForeverLauncher.serverJson()
        assertTrue(json.contains("\"host\":\"127.0.0.1\""))
        assertTrue(json.contains("\"portal\":\"trinity.actual.battle.net\""))
        assertTrue(json.contains("\"regionGroup\":8"))
        assertTrue(json.contains("\"loginPort\":1119"))
        // ctl.sh's WORLD_PORT: the launcher's default (8085) found no world server and stayed at "Starting".
        assertTrue(json.contains("\"worldPort\":8105"))
        assertEquals(64, Regex("\"publicKey\":\"([0-9A-F]+)\"").find(json)!!.groupValues[1].length)
        val ctl = File("../realm/forever/server/ctl.sh").takeIf { it.isFile }?.readText()
        if (ctl != null) assertTrue(ctl.contains("WORLD_PORT=${ForeverLauncher.WORLD_PORT}"))
    }

    @Test
    fun `seedConfig rewrites its own files and keeps the launcher's settings`() {
        val client = Files.createTempDirectory("client").toFile()
        val driveC = Files.createTempDirectory("drivec").toFile()
        ForeverLauncher.seedConfig(client, driveC)
        val cfg = File(client, "config")
        // A wrong game folder or mode (an older seed, a stray press) is put right at the next start.
        File(cfg, "client.txt").writeText("F:\\client")
        File(cfg, "launcher-mode.txt").writeText("join")
        File(cfg, "server.json").delete()
        // The launcher's own files are its own.
        File(cfg, "launcher-settings.txt").writeText("lang=ru\ntheme=ember\n")
        File(cfg, "key-anchors.txt").writeText("1 abc\n")
        ForeverLauncher.seedConfig(client, driveC)
        assertEquals("F:\\client\\_forever_", File(cfg, "client.txt").readText())
        assertEquals("own", File(cfg, "launcher-mode.txt").readText())
        assertEquals(ForeverLauncher.serverJson(), File(cfg, "server.json").readText())
        assertEquals("lang=ru\ntheme=ember\n", File(cfg, "launcher-settings.txt").readText())
        assertEquals("1 abc\n", File(cfg, "key-anchors.txt").readText())
    }

    @Test
    fun `the realm's name goes into Windows' hosts file once`() {
        val driveC = Files.createTempDirectory("drivec").toFile()
        val hosts = File(driveC, "windows/system32/drivers/etc/hosts")
        hosts.parentFile!!.mkdirs()
        hosts.writeText("# 127.0.0.1 localhost")
        ForeverLauncher.seedHosts(driveC)
        assertEquals("# 127.0.0.1 localhost\r\n127.0.0.1 trinity.actual.battle.net # wow-forever-join\r\n", hosts.readText())
        // Already there (this app's line, or the launcher's own after its question): nothing is added.
        ForeverLauncher.seedHosts(driveC)
        assertEquals(1, hosts.readLines().count { it.contains("trinity.actual.battle.net") })
        // A commented-out line does not count, and a missing file is made.
        hosts.writeText("# 127.0.0.1 trinity.actual.battle.net\n")
        ForeverLauncher.seedHosts(driveC)
        assertEquals(2, hosts.readLines().count { it.contains("trinity.actual.battle.net") })
        hosts.delete()
        ForeverLauncher.seedHosts(driveC)
        assertEquals("127.0.0.1 trinity.actual.battle.net # wow-forever-join\r\n", hosts.readText())
    }

    @Test
    fun `clearConfig removes the config so seedConfig writes it afresh`() {
        val client = Files.createTempDirectory("client").toFile()
        val driveC = Files.createTempDirectory("drivec").toFile()
        ForeverLauncher.seedConfig(client, driveC)
        File(driveC, "windows/config").mkdirs()
        ForeverLauncher.clearConfig(client, driveC)
        assertFalse(File(client, "config").exists())
        assertFalse(File(driveC, "windows/config").exists())
        ForeverLauncher.seedConfig(client, driveC)
        assertEquals("own", File(client, "config/launcher-mode.txt").readText())
        // Without the games' Windows (not made yet) the config beside the launcher still goes.
        ForeverLauncher.clearConfig(client, null)
        assertFalse(File(client, "config").exists())
    }

    @Test
    fun `the game's window is told by its program, not by a window as big as the screen`() {
        val (sw, sh) = 1828 to 1248
        // The game, as the launcher starts it: its window is the screen's size (or a window at least half of it).
        assertTrue(ForeverLauncher.isGameWindow("wow.exe", 1828, 1248, sw, sh))
        assertTrue(ForeverLauncher.isGameWindow("Wow.exe", 1024, 768, sw, sh))
        assertTrue(ForeverLauncher.isGameWindow("wowb.exe", 1828, 1248, sw, sh))
        // Wine's desktop is as big as the screen and focused at every start: the phone's black screen (report 108).
        assertFalse(ForeverLauncher.isGameWindow("explorer.exe", 1828, 1248, sw, sh))
        // The launcher's own windows, whatever their size, and its name begins with "wow" too.
        assertFalse(ForeverLauncher.isGameWindow("wowforeverlauncher.exe", 1008, 782, sw, sh))
        assertFalse(ForeverLauncher.isGameWindow("wowforeverlauncher.exe", 1828, 1248, sw, sh))
        // The game's small first windows (a splash, an error box), the crash reporter, a window without a program.
        assertFalse(ForeverLauncher.isGameWindow("wow.exe", 400, 200, sw, sh))
        assertFalse(ForeverLauncher.isGameWindow("blizzarderror.exe", 1828, 1248, sw, sh))
        assertFalse(ForeverLauncher.isGameWindow("", 1828, 1248, sw, sh))
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
}
