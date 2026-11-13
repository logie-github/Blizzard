package com.logie.blizz.forever

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import java.nio.file.Files

class ForeverCtlTest {
    private val layout = ForeverLayout(File("/data/data/com.logie.blizz/files/forever"))

    @Test
    fun `ctl runs the shipped script with FILES pointing at the realm folder`() {
        val command = ForeverCtl.command(layout, "worldserver")
        assertEquals(
            listOf("/system/bin/sh", "/data/data/com.logie.blizz/files/forever/server/ctl.sh", "worldserver"),
            command.argv,
        )
        assertEquals("/data/data/com.logie.blizz/files/forever", command.env["FILES"])
        assertEquals(layout.run, command.directory)
    }

    @Test
    fun `an account command passes the name and password`() {
        assertEquals(
            listOf("/system/bin/sh", "${layout.server.path}/ctl.sh", "account", "me@example.com", "secret"),
            ForeverCtl.command(layout, "account", "me@example.com", "secret").argv,
        )
    }

    @Test
    fun `makeExecutable sets the bit on the programs, the loader and ctl`() {
        val dir = Files.createTempDirectory("forever").toFile()
        val l = ForeverLayout(dir)
        File(l.server, "bin").mkdirs(); File(l.server, "lib").mkdirs()
        val files = listOf(l.ctl, File(l.server, "bin/worldserver"), File(l.server, "lib/ld-musl-aarch64.so.1"))
        files.forEach { it.writeText("x"); it.setExecutable(false, false) }
        assertEquals(3, ForeverCtl.makeExecutable(l))
        assertTrue(files.all { it.canExecute() })
        // Idempotent.
        assertEquals(0, ForeverCtl.makeExecutable(l))
    }

    @Test
    fun `a tar entry can't escape the folder`() {
        val base = File("/tmp/x")
        assertEquals(File(base, "server/bin/worldserver"), ForeverServerPackage.entryTarget(base, "./server/bin/worldserver"))
        assertNull(ForeverServerPackage.entryTarget(base, "../escape"))
        assertNull(ForeverServerPackage.entryTarget(base, "/etc/passwd"))
        assertNull(ForeverServerPackage.entryTarget(base, "server/../../x"))
    }

    private val buildInfo = """
        Branch!STRING:0|Active!DEC:1|Build Key!HEX:16|CDN Key!HEX:16|Version!STRING:0|Product!STRING:0
        us|0|aa|bb|1.15.7.70790|wowf
        eu|1|cc|dd|1.15.8.70862|wowf
        us|1|ee|ff|1.15.8.99999|wow_classic_era
    """.trimIndent()

    @Test
    fun `the client build is the active Forever row's`() {
        assertEquals(70862, ForeverCtl.clientBuild(buildInfo))
    }

    @Test
    fun `without an active Forever row any Forever row is used, then the first row`() {
        val noActive = buildInfo.replace("eu|1|", "eu|0|")
        assertEquals(70790, ForeverCtl.clientBuild(noActive))
        val other = "Version!STRING:0|Product!STRING:0\n1.2.3.12345|wow"
        assertEquals(12345, ForeverCtl.clientBuild(other))
    }

    @Test
    fun `an unreadable build info gives no build`() {
        assertNull(ForeverCtl.clientBuild(""))
        assertNull(ForeverCtl.clientBuild("Branch!STRING:0|Product!STRING:0\nus|wowf"))
        assertNull(ForeverCtl.clientBuild("Version!STRING:0\nnot-a-version"))
    }

    @Test
    fun `the client's portal points at this phone, its other settings kept`() {
        val locale = "SET textLocale \"enUS\"\nSET audioLocale \"enUS\"\n"
        assertEquals(locale + "SET portal \"127.0.0.1\"\n", ForeverCtl.withLocalPortal(null))
        val config = "SET gxWindow \"1\"\nSET portal \"us\"\nSET locale \"enUS\"\n"
        assertEquals("SET gxWindow \"1\"\nSET locale \"enUS\"\n" + locale + "SET portal \"127.0.0.1\"\n", ForeverCtl.withLocalPortal(config))
    }

    @Test
    fun `a language is set only where the client has none (no language list box at the start)`() {
        val config = "SET textLocale \"deDE\"\nSET portal \"127.0.0.1\"\n"
        assertEquals("SET textLocale \"deDE\"\nSET audioLocale \"enUS\"\nSET portal \"127.0.0.1\"\n", ForeverCtl.withLocalPortal(config))
        val both = "SET textLocale \"enUS\"\nSET audioLocale \"enUS\"\nSET portal \"127.0.0.1\"\n"
        assertEquals(both, ForeverCtl.withLocalPortal(both))
    }

    /** A folder tree for findClient: name -> children (a leaf has none). */
    private class Node(val children: Map<String, Node> = emptyMap())
    private val listing: (Node) -> List<Pair<String, Node>> = { it.children.toList() }
    private val client = Node(mapOf(".build.info" to Node(), "Data" to Node(mapOf("data" to Node())), "_forever_" to Node(mapOf("Wow.exe" to Node()))))

    @Test
    fun `the picked folder is the client when it holds build info, Data and _forever_`() {
        assertEquals(emptyList<Node>(), ForeverCtl.findClient(client, listing))
    }

    @Test
    fun `a folder above the client finds it one level down`() {
        val above = Node(mapOf("notes.txt" to Node(), "World of Warcraft" to client))
        assertEquals(listOf(client), ForeverCtl.findClient(above, listing))
    }

    @Test
    fun `a folder that isn't the client (or only its _forever_ part) is refused`() {
        assertNull(ForeverCtl.findClient(Node(mapOf("Wow.exe" to Node())), listing))
        assertNull(ForeverCtl.findClient(client.children.getValue("_forever_"), listing))
        assertNull(ForeverCtl.findClient(Node(mapOf(".build.info" to Node(), "_forever_" to Node())), listing))
    }
    @Test
    fun `the game's own crash file since the start is what a report says, its newest`() {
        val game = Files.createTempDirectory("game").toFile()
        val errors = File(game, "Errors").apply { mkdirs() }
        val old = File(errors, "2026-11-08_Crash_1.txt").apply { writeText("Exception: OLD"); setLastModified(1_000_000) }
        File(errors, "2026-11-09_Crash_2.dmp").apply { writeText("x"); setLastModified(5_000_000) }
        assertNull(ForeverCtl.clientStop(game, since = 2_000_000))
        val crash = File(errors, "2026-11-09_Crash_2.txt")
        crash.writeText("\uFEFF=====\nWorld of Warcraft: Retail Build (build 70862)\n\nException: ACCESS_VIOLATION - The instruction at \"0x1\" referenced memory at \"0x0\".\nmore\n")
        crash.setLastModified(4_000_000)
        val stop = ForeverCtl.clientStop(game, since = 2_000_000)!!
        assertTrue(stop.title.startsWith("Exception: ACCESS_VIOLATION"))
        assertTrue(stop.text.startsWith("====="))
        assertEquals(4_000_000, stop.at)
        // Reported once: nothing newer than it.
        assertNull(ForeverCtl.clientStop(game, since = stop.at))
        assertTrue(old.isFile)
    }

    @Test
    fun `the game opens on its login screen with the e-mail in place and nothing in front of it`() {
        val fresh = ForeverCtl.withLoginReady(ForeverCtl.withLocalPortal(null), "forever@forever.local")
        // What the desktop rig ran with (client 70888): no intro, no narrator question, the e-mail filled in.
        assertEquals(
            "SET textLocale \"enUS\"\nSET audioLocale \"enUS\"\nSET portal \"127.0.0.1\"\nSET playIntroMovie \"1\"\n" +
                "SET showScreenNarrationDialog \"0\"\nSET accessibilityScreenNarrationEnabled \"0\"\n" +
                "SET showPhotosensitivityWarning \"0\"\nSET accountName \"forever@forever.local\"\n",
            fresh,
        )
        // Once more: the same lines (nothing doubled; the portal's line moves to the end, as it always has).
        assertEquals(fresh.lines().sorted(), ForeverCtl.withLoginReady(ForeverCtl.withLocalPortal(fresh), "forever@forever.local").lines().sorted())
        // The game's own file after a session: its settings kept, its choices kept, the account the app's.
        val played = "SET graphicsQuality \"2\"\nSET playIntroMovie \"70888\"\nset accessibilityScreenNarrationEnabled \"1\"\n" +
            "SET accountName \"someone@else\"\nSET portal \"127.0.0.1\"\n"
        val next = ForeverCtl.withLoginReady(played, "forever@forever.local")
        assertTrue(next.contains("SET graphicsQuality \"2\""))
        assertTrue(next.contains("SET playIntroMovie \"70888\""))
        assertFalse(next.contains("SET playIntroMovie \"1\""))
        assertTrue(next.contains("set accessibilityScreenNarrationEnabled \"1\""))
        assertFalse(next.contains("someone@else"))
        assertEquals(1, next.lines().count { it.contains("accountName") })
        assertTrue(next.contains("SET accountName \"forever@forever.local\""))
    }

    @Test
    fun `a crash file that says Security Crash is the game's protection, another is not`() {
        val security = "=====\nException: 0xC00000E5 (EXCEPTION_INTERNAL_ERROR) at 00006fffffc1d127\nProcessID: 852\n\n" +
            "<Exception.IssueType> Exception\n<ExceptionType> Security Crash\n<Exception.Summary:>\n"
        assertTrue(ForeverCtl.isSecurityCrash(security))
        assertFalse(ForeverCtl.isSecurityCrash("Exception: ACCESS_VIOLATION\n<ExceptionType> Crash\n"))
        assertFalse(ForeverCtl.isSecurityCrash("the words Security Crash in a sentence are not the line"))
        val told = ForeverPlay.securityCrashText(launcher = true, title = "Exception: 0xC00000E5")
        assertTrue(told.contains("Forever Launcher") && told.contains("Security Crash") && told.endsWith("Exception: 0xC00000E5"))
        assertFalse(ForeverPlay.securityCrashText(launcher = false, title = "x").contains("Forever Launcher"))
    }

    @Test
    fun `a crash file ends the session once it is written and finished, an older one never`() {
        val errors = Files.createTempDirectory("errors").toFile()
        // No folder yet (the game makes it at its first crash), an empty one, a dump alone, a file from before this start.
        assertNull(ForeverCtl.settledCrash(File(errors, "none"), since = 0, now = 10_000))
        assertNull(ForeverCtl.settledCrash(errors, since = 0, now = 10_000))
        File(errors, "2026-11-12_Crash_1.dmp").apply { writeText("x"); setLastModified(5_000_000) }
        File(errors, "2026-11-11_Crash_0.txt").apply { writeText("old"); setLastModified(1_000_000) }
        assertNull(ForeverCtl.settledCrash(errors, since = 2_000_000, now = 9_000_000))
        val crash = File(errors, "2026-11-12_Crash_1.txt").apply { writeText("Exception"); setLastModified(5_000_000) }
        // Still being written (changed within the last three seconds): not yet.
        assertNull(ForeverCtl.settledCrash(errors, since = 2_000_000, now = 5_001_000))
        assertEquals(crash, ForeverCtl.settledCrash(errors, since = 2_000_000, now = 5_003_000))
    }

    @Test
    fun `without a crash file the storage log's failures are, each once`() {
        val game = Files.createTempDirectory("game").toFile()
        val log = File(File(game, "Logs").apply { mkdirs() }, "Tact.log")
        log.writeText(
            "11/9 23:16:56.557  Truncated updated section in KMT file detected.\n" +
                "11/9 23:16:56.557  Truncated updated section in KMT file detected.\n" +
                "11/9 23:16:56.558  Opened something fine\n" +
                "11/9 23:16:56.560  Failed to initialize dynamic container. Error(11): needs repair\n",
        )
        log.setLastModified(9_000_000)
        val stop = ForeverCtl.clientStop(game, since = 1)!!
        assertEquals(2, stop.text.lines().size)
        assertTrue("Truncated" in stop.text && "needs repair" in stop.text)
        log.writeText("11/9 23:22:44.000  Shutdown\n"); log.setLastModified(9_500_000)
        assertNull(ForeverCtl.clientStop(game, since = 1))
    }

    @Test
    fun `the last line of a log is its end's, without colour codes, shortened`() {
        val log = File(Files.createTempDirectory("log").toFile(), "worldserver.log")
        assertNull(ForeverCtl.lastLine(log))
        log.writeText("first\n" + "x".repeat(6000) + "\n\u001B[32mLoading creature templates...\u001B[0m\n\n")
        assertEquals("Loading creature templates...", ForeverCtl.lastLine(log))
        assertEquals("Loading", ForeverCtl.lastLine(log, limit = 7))
    }
}
