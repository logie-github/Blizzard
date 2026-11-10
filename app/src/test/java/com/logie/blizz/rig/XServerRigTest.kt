package com.logie.blizz.rig

import com.winlator.xserver.XKeycode
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.File

/**
 * What a Windows program gets of the app's clicks and keys through Winlator's own X server, on a desktop ([XRig]): run with
 * `BLIZZ_XRIG=1 BLIZZ_XRIG_LIB=<folder of libwinlator.so and the rig's programs>` (tools/xrig/README.md); skipped otherwise,
 * so CI and an ordinary test run pass over it.
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class XServerRigTest {
    private val log = File(XRig.windowsDir, "inputprobe.log")

    /**
     * The server alone, kept up for BLIZZ_XRIG_HOLD seconds as display :77 (at BLIZZ_XRIG_SIZE, 800x600 unless said), to be
     * driven by hand from a shell: `DISPLAY=:77 xwininfo -root -tree`, a Wine program of one's own, and commands written to
     * /tmp/xrig-77-cmd (one a line; [XRig.command] lists them: click, key, shot, state...), answered in /tmp/xrig-77-out.txt.
     * Its window tree is written to /tmp/xrig-77-windows.txt as it changes.
     */
    @Test fun hold() {
        val seconds = System.getenv("BLIZZ_XRIG_HOLD")?.toLongOrNull()
        assumeTrue(XRig.enabled && seconds != null)
        val size = (System.getenv("BLIZZ_XRIG_SIZE") ?: "800x600").split("x").map { it.toInt() }
        val commands = File("/tmp/xrig-77-cmd")
        val answers = File("/tmp/xrig-77-out.txt")
        commands.delete()
        answers.writeText("")
        XRig(size[0], size[1]).use { rig ->
            val end = System.currentTimeMillis() + seconds!! * 1000
            var tree = ""
            while (System.currentTimeMillis() < end) {
                val now = runCatching { rig.describe() }.getOrDefault("")
                if (now != tree) { tree = now; File("/tmp/xrig-77-windows.txt").writeText(now + "\n") }
                if (commands.isFile) {
                    val lines = commands.readLines()
                    commands.delete()
                    for (line in lines.map { it.trim() }.filter { it.isNotEmpty() }) {
                        if (line == "quit") return
                        val answer = runCatching { rig.command(line) }.getOrElse { "error: $it" }
                        answers.appendText("> $line\n$answer\n")
                    }
                }
                Thread.sleep(100)
            }
        }
    }

    /** The probe by itself on the games' desktop (no helper, no keeper). */
    private fun probe(rig: XRig, vararg args: String) {
        rig.install(File(XRig.programs, "inputprobe.exe"))
        log.delete()
        rig.run("C:\\windows\\inputprobe.exe", *args)
        rig.waitFor("the probe's window") { rig.window("inputprobe") != null && log.isFile && log.readText().contains("START") }
        // Its first lock of the cursor (as its window is activated, and every quarter second after), and the renderer's look at the new window.
        Thread.sleep(1500)
    }

    /**
     * The probe started as the app starts a game: the session's keeper, winhandler.exe, the program. Its frame is gone when this
     * returns: with "fixed" among [args] (a window of a fixed size, Diablo II's) it is 400x300 at the top left, which the server
     * shows stretched over the screen; without (a window that can be sized, Warcraft III's) the keeper has given it the whole screen.
     */
    private fun game(rig: XRig, vararg args: String): Process {
        rig.install(File(XRig.programs, "inputprobe.exe"))
        log.delete()
        val process = rig.game("C:\\windows", "inputprobe.exe", *args)
        val (width, height) = if ("fixed" in args) 400 to 300 else rig.xServer.screenInfo.width.toInt() to rig.xServer.screenInfo.height.toInt()
        rig.waitFor("the probe's window without its frame (${width}x$height at the top left)") {
            log.isFile && log.readText().contains("START") &&
                rig.window("inputprobe")?.let { it.width.toInt() == width && it.height.toInt() == height && it.x.toInt() == 0 && it.y.toInt() == 0 } == true
        }
        Thread.sleep(1500)
        return process
    }

    /**
     * Clicks the point [x],[y] of the probe's client area, wherever the server shows it on the screen. [framed]: the window still
     * has Wine's frame around the client area (the probe by itself); the keeper takes it off.
     */
    private fun clickProbe(rig: XRig, x: Int, y: Int, framed: Boolean = true) {
        val frame = if (framed) Regex("frame=(\\d+),(\\d+)").find(log.readText())!!.groupValues.drop(1).map { it.toInt() } else listOf(0, 0)
        val (sx, sy) = rig.onScreen(rig.window("inputprobe")!!, frame[0] + x, frame[1] + y)
        rig.click(sx, sy)
    }

    /** Whether [text] has [what] at [x],[y], give or take the pixels the stretch to the screen rounds away. */
    private fun has(text: String, what: String, x: Int, y: Int): Boolean =
        Regex("$what (-?\\d+) (-?\\d+)").findAll(text).any { m -> Math.abs(m.groupValues[1].toInt() - x) <= 2 && Math.abs(m.groupValues[2].toInt() - y) <= 2 }

    /**
     * Warcraft III on the phone, 9 November 2026: nothing in the game could be clicked. A program that locks the cursor to its
     * window (ClipCursor) makes Wine report the mouse without a window, and Wine's server hands such input to the window
     * station's input desktop: "Default", the first one made, not the games' ("shell"), until an input with a window switches
     * it. A game that locks the cursor from its first moment never got a move or a click. The keeper (borderless.exe) switches
     * the input desktop as the session starts ([aLockedCursorInAStretchedWindowGetsItsClickWhereTouched] is that path), and it
     * gives a window that can be sized, as Warcraft III's is, the whole screen: the game draws at the screen's own size, and a
     * lock to the whole screen is no lock to Wine, which then holds no pointer grab at all. Here: the probe locks the cursor at
     * once in such a window, is told its new size, and a touch arrives as one click where it was made, not as none, not doubled.
     */
    @Test fun aSizableWindowGetsTheWholeScreenAndItsClicks() {
        assumeTrue(XRig.enabled)
        XRig().use { rig ->
            game(rig, "clip")
            assertTrue("the program was not told its new size:\n${log.readText()}", log.readText().contains("SIZE 800 600"))
            rig.click(520, 410)
            rig.waitFor("the click's release in the probe's log", 10_000) { log.readText().contains("LUP") }
            Thread.sleep(400)
            val text = log.readText()
            assertTrue("no press reached the program:\n$text\n${rig.state()}", has(text, "LDOWN", 520, 410))
            assertTrue("no release reached the program:\n$text", has(text, "LUP", 520, 410))
            assertTrue("one press became a double click:\n$text", !text.contains("LDBL"))
            assertEquals("presses:\n$text", 1, Regex("LDOWN").findAll(text).count())
        }
    }

    /**
     * The locked cursor itself, in a window of a fixed size (400x300, which the server shows stretched over the 800x600 screen):
     * Wine holds its pointer grab, the keeper has made the games' desktop the one that takes input, and a touch on the picture's
     * middle must arrive as one click at 200,150, the stretch applied to the locked pointer too (Winlator patch 0009: the
     * pointer's grab window has no stretch of its own).
     */
    @Test fun aLockedCursorInAStretchedWindowGetsItsClickWhereTouched() {
        assumeTrue(XRig.enabled)
        XRig().use { rig ->
            game(rig, "clip", "fixed")
            assertNotNull("Wine holds no pointer grab: the cursor lock this test is about did not happen.\n${rig.state()}", rig.xServer.grabManager.window)
            clickProbe(rig, 200, 150, framed = false)
            rig.waitFor("the click's release in the probe's log", 10_000) { log.readText().contains("LUP") }
            Thread.sleep(400)
            val text = log.readText()
            assertTrue("no press reached the program:\n$text", has(text, "LDOWN", 200, 150))
            assertTrue("no release reached the program:\n$text", has(text, "LUP", 200, 150))
            assertTrue("one press became a double click:\n$text", !text.contains("LDBL"))
            assertEquals("presses:\n$text", 1, Regex("LDOWN").findAll(text).count())
        }
    }

    /** The same without the keeper, as every build up to 180 started games: the locked cursor's click never arrives. Kept as the record of the fault. */
    @Test fun withoutTheKeeperALockedCursorGetsNoClick() {
        assumeTrue(XRig.enabled)
        XRig().use { rig ->
            rig.install(File(XRig.programs, "inputprobe.exe"))
            log.delete()
            rig.game("C:\\windows", "inputprobe.exe", "clip", keeper = false)
            rig.waitFor("the probe's window") { rig.window("inputprobe") != null && log.isFile && log.readText().contains("START") }
            Thread.sleep(1500)
            clickProbe(rig, 200, 150)
            Thread.sleep(2500)
            val text = log.readText()
            assertTrue("the fault this test records is gone (a click arrived without the keeper):\n$text", !text.contains("LDOWN"))
        }
    }

    /** A game that does not lock the cursor (Diablo II's window), through the keeper: one click where it was touched. */
    @Test fun aGameThatDoesNotLockTheCursorGetsItsClicks() {
        assumeTrue(XRig.enabled)
        XRig().use { rig ->
            game(rig, "noclip", "fixed")
            clickProbe(rig, 200, 150, framed = false)
            rig.waitFor("the click in the probe's log", 10_000) { log.readText().contains("LUP") }
            Thread.sleep(400)
            val text = log.readText()
            assertTrue(text, has(text, "LDOWN", 200, 150))
            assertTrue(text, has(text, "LUP", 200, 150))
            assertEquals("presses:\n$text", 1, Regex("LDOWN").findAll(text).count())
        }
    }

    /** The probe by itself, its frame on, stretched: the click lands where the picture was touched. */
    @Test fun aFramedWindowStretchedToTheScreenGetsItsClickWhereTouched() {
        assumeTrue(XRig.enabled)
        XRig().use { rig ->
            probe(rig, "noclip")
            clickProbe(rig, 200, 150)
            rig.waitFor("the click in the probe's log", 10_000) { log.readText().contains("LUP") }
            Thread.sleep(300)
            val text = log.readText()
            assertTrue(text, has(text, "LDOWN", 200, 150))
            assertTrue(text, has(text, "LUP", 200, 150))
        }
    }

    /**
     * A game quit from its own menu left a black screen (winhandler.exe stays for as long as the desktop, and the desktop for
     * as long as winhandler.exe). The keeper ends the session three seconds after the game's last program: Wine exits, which is
     * what returns the app to the launcher.
     */
    @Test fun theSessionEndsWhenTheGameDoes() {
        assumeTrue(XRig.enabled)
        XRig().use { rig ->
            val wine = game(rig, "noclip", "fixed")
            clickProbe(rig, 200, 150, framed = false)
            Thread.sleep(300)
            rig.key(XKeycode.KEY_F4, XKeycode.KEY_ALT_L)
            assertTrue("Wine was still running 20 s after the game's window was closed.\n${rig.describe()}", wine.waitFor(20, java.util.concurrent.TimeUnit.SECONDS))
        }
    }

    /** The app's keyboard (GameKeyboard): letters, Shift with a letter and with a digit, Enter, Escape and a function key, as the game reads them. */
    @Test fun theAppsKeyboardTypesWhatItsCapsShow() {
        assumeTrue(XRig.enabled)
        XRig().use { rig ->
            game(rig, "noclip", "fixed")
            clickProbe(rig, 200, 150, framed = false)
            rig.key(XKeycode.KEY_A)
            rig.key(XKeycode.KEY_A, XKeycode.KEY_SHIFT_L)
            rig.key(XKeycode.KEY_1)
            rig.key(XKeycode.KEY_1, XKeycode.KEY_SHIFT_L)
            rig.key(XKeycode.KEY_MINUS, XKeycode.KEY_SHIFT_L)
            rig.key(XKeycode.KEY_ENTER)
            rig.key(XKeycode.KEY_ESC)
            rig.key(XKeycode.KEY_F10)
            rig.waitFor("the keys in the probe's log", 10_000) { log.readText().contains("vk=79") }
            Thread.sleep(300)
            val text = log.readText()
            val chars = Regex("CHAR (\\d+)").findAll(text).map { it.groupValues[1].toInt().toChar() }.joinToString("")
            assertEquals("the characters typed:\n$text", "aA1!_\r\u001b", chars)
            assertTrue("F10:\n$text", text.contains("KEYDOWN vk=79"))
        }
    }
}
