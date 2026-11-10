package com.logie.blizz.rig

import com.logie.blizz.controls.Button
import com.logie.blizz.game.Wc3Screen
import org.junit.Assert.assertEquals
import org.junit.Assume.assumeTrue
import org.junit.Test
import java.io.File

/**
 * Warcraft III's touch layout played against the game itself, on the desktop rig (README, "Testing the Windows games here"):
 * the game runs on Xvfb at the phone's 960x720 in a Human custom game with nothing selected yet, and this does what the
 * phone's touch layer does for each tap: looks at the game's picture ([Wc3Screen], here from a screenshot), picks the button
 * the smart tap picks (the right one only while the player's own units are selected), clicks, and looks again; the two-finger
 * tap's key is picked the same way. Run with
 * `BLIZZ_WC3_RIG=<the X display, such as :99>`; skipped otherwise.
 */
class Wc3TouchRigTest {
    private val display = System.getenv("BLIZZ_WC3_RIG")
    private val shots = File(System.getProperty("java.io.tmpdir"), "wc3-touch-rig").apply { mkdirs() }
    private var shot = 0

    private fun sh(vararg command: String) {
        val p = ProcessBuilder(*command).apply { environment()["DISPLAY"] = display }.redirectErrorStream(true).start()
        p.inputStream.readBytes()
        p.waitFor()
    }

    /** What the game's picture is read as now (kept as a file, numbered, for looking at afterwards). */
    private fun look(): Wc3Screen.State {
        val file = File(shots, "%02d.png".format(++shot))
        sh("import", "-window", "root", file.path)
        val image = javax.imageio.ImageIO.read(file)
        val w = image.width
        val rgb = image.getRGB(0, 0, w, image.height, null, 0, w)
        return Wc3Screen.state(w, image.height) { x, y -> rgb[y * w + x] }
    }

    private fun click(x: Int, y: Int, button: Button) {
        sh("xdotool", "mousemove", "$x", "$y")
        Thread.sleep(150)
        sh("xdotool", "click", if (button == Button.LEFT) "1" else "3")
        Thread.sleep(900)
    }

    /** A tap on the battlefield as the phone makes it: the right click only while the game shows the player's own selection. */
    private fun tap(x: Int, y: Int): Button {
        val button = if (look() == Wc3Screen.State.COMMAND) Button.RIGHT else Button.LEFT
        click(x, y, button)
        return button
    }

    /**
     * A two-finger tap as the phone makes it: Escape while the picture shows something to leave (a box over the game, a scene, a
     * menu, a command waiting for its target), the game's menu key otherwise. The key that was pressed.
     */
    private fun twoFingers(): String {
        val state = look()
        val key = if (state == Wc3Screen.State.OTHER || state == Wc3Screen.State.TARGET) "Escape" else "F10"
        sh("xdotool", "key", key)
        Thread.sleep(1200)
        return key
    }

    /** The middle of the command card's button in [column], [row], in the screen's pixels. */
    private fun card(column: Int, row: Int): Pair<Int, Int> {
        val box = Wc3Screen.cell(column, row)
        return Math.round((box.left + box.right) / 2 * 960) to Math.round((box.top + box.bottom) / 2 * 720)
    }

    @Test fun selectThenMoveAttackBuildAndTheGamesMenu() {
        assumeTrue(display != null)
        // A custom game just begun: the mission's interface with nothing selected.
        assertEquals("the game is not in a mission with nothing selected", Wc3Screen.State.IDLE, look())

        // The idle worker's icon (a button of the game's own: the left click): a worker is selected.
        click(27, 493, Button.LEFT)
        assertEquals("after the idle worker's icon", Wc3Screen.State.COMMAND, look())

        // Tap to move: with the worker selected the tap is the order.
        assertEquals(Button.RIGHT, tap(300, 330))
        assertEquals(Wc3Screen.State.COMMAND, look())

        // Attack (the command card, a left click): the game waits for a target, and the next tap is the left click that gives it.
        card(3, 0).let { (x, y) -> click(x, y, Button.LEFT) }
        assertEquals("after Attack", Wc3Screen.State.TARGET, look())
        assertEquals(Button.LEFT, tap(520, 300))
        assertEquals("after the attack's target", Wc3Screen.State.COMMAND, look())

        // Build: the menu of buildings, a farm, and the place for it by a tap (the left click again; a spot that is
        // built over or wooded takes no farm, so a few are tried).
        card(0, 2).let { (x, y) -> click(x, y, Button.LEFT) }
        assertEquals("the build menu", Wc3Screen.State.COMMAND, look())
        card(0, 1).let { (x, y) -> click(x, y, Button.LEFT) }
        assertEquals("a building chosen", Wc3Screen.State.TARGET, look())
        for ((x, y) in listOf(330 to 180, 250 to 300, 620 to 400, 200 to 420, 700 to 250)) {
            assertEquals(Button.LEFT, tap(x, y))
            if (look() != Wc3Screen.State.TARGET) break
        }
        assertEquals("after the place was given", Wc3Screen.State.COMMAND, look())

        // The game's menu over it all: every tap is the left click, and Return to Game is pressed by one.
        click(155, 14, Button.LEFT)
        assertEquals("the game's menu", Wc3Screen.State.OTHER, look())
        assertEquals(Button.LEFT, tap(480, 464))
        assertEquals("back in the game", Wc3Screen.State.COMMAND, look())

        // Two fingers: the game's menu in play, and Escape to leave it.
        assertEquals("F10", twoFingers())
        assertEquals("the game's menu by two fingers", Wc3Screen.State.OTHER, look())
        assertEquals("Escape", twoFingers())
        assertEquals("back in the game by two fingers", Wc3Screen.State.COMMAND, look())
        // A command waiting for its target is called off by them, and the selection stays.
        card(3, 0).let { (x, y) -> click(x, y, Button.LEFT) }
        assertEquals("after Attack again", Wc3Screen.State.TARGET, look())
        assertEquals("Escape", twoFingers())
        assertEquals("the command called off", Wc3Screen.State.COMMAND, look())
    }
}
