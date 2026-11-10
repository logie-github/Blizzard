package com.logie.blizz.game

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Test
import java.io.File

/**
 * What Warcraft III's picture says a tap should be ([Wc3Screen]): on pictures drawn here with the marks' measured colours,
 * and, when `BLIZZ_WC3_FRAMES` names a folder of the game's own frames from the desktop rig (README, "Testing the Windows
 * games here"; the game's pictures are never committed), on those.
 */
class Wc3ScreenTest {
    /** A 960x720 picture, black, to draw the marks on. */
    private class Picture(val width: Int = 960, val height: Int = 720) : Wc3Screen.Pixels {
        val data = IntArray(width * height) { 0xff000000.toInt() }
        override fun argb(x: Int, y: Int) = data[y * width + x]
        fun fill(box: Wc3Screen.Box, color: Int, share: Float = 1f) {
            val x0 = Math.round(box.left * width)
            val x1 = Math.round(box.right * width)
            val y0 = Math.round(box.top * height)
            val y1 = Math.round(box.bottom * height)
            var i = 0
            for (y in y0 until y1) for (x in x0 until x1) {
                // Every [1/share]th pixel, spread evenly.
                if ((i * share).toInt() != ((i + 1) * share).toInt()) data[y * width + x] = color
                i++
            }
        }
        fun flipped() = Wc3Screen.Pixels { x, y -> argb(x, height - 1 - y) }
        fun swapped() = Wc3Screen.Pixels { x, y -> argb(x, y).let { (it and 0xff00ff00.toInt()) or ((it and 0xff) shl 16) or ((it shr 16) and 0xff) } }
    }

    private val gold = 0xff6a5819.toInt()
    private val white = 0xffffffff.toInt()
    private val grey = 0xff6e6e6e.toInt()
    private val icon = 0xff5a7890.toInt()

    /** The mission's interface: the coin, the Menu button's words lit or greyed, and buttons on the command card ([cells]: column to row). */
    private fun mission(lit: Boolean, vararg cells: Pair<Int, Int>) = Picture().apply {
        fill(Wc3Screen.GOLD_COIN, gold)
        fill(Wc3Screen.MENU_BUTTON, if (lit) white else grey, share = 0.056f)
        for ((column, row) in cells) fill(Wc3Screen.cell(column, row), icon, share = 0.6f)
    }

    private fun state(picture: Picture) = Wc3Screen.state(picture.width, picture.height, picture)

    @Test fun nothingSelectedIsALeftClickAndASelectionIsAnOrder() {
        assertEquals(Wc3Screen.State.IDLE, state(mission(lit = true)))
        // A worker: move, stop, hold, attack, patrol, gather, build.
        val worker = mission(true, 0 to 0, 1 to 0, 2 to 0, 3 to 0, 0 to 1, 0 to 2, 1 to 2)
        assertEquals(Wc3Screen.State.COMMAND, state(worker))
        // A building: train, rally.
        assertEquals(Wc3Screen.State.COMMAND, state(mission(true, 0 to 0, 3 to 1)))
        // The game's own cursor over an empty button is not a selection.
        val cursor = mission(true).apply { fill(Wc3Screen.cell(1, 0), white, share = 0.21f) }
        assertEquals(Wc3Screen.State.IDLE, state(cursor))
    }

    @Test fun onlyCancelMeansTheGameWaitsForATarget() {
        assertEquals(Wc3Screen.State.TARGET, state(mission(true, 3 to 2)))
        // With the cursor still over the button that was pressed.
        val withCursor = mission(true, 3 to 2).apply { fill(Wc3Screen.cell(3, 0), white, share = 0.35f) }
        assertEquals(Wc3Screen.State.TARGET, state(withCursor))
        // The build menu (buildings and Cancel) is a selection still.
        assertEquals(Wc3Screen.State.COMMAND, state(mission(true, 0 to 0, 1 to 0, 2 to 0, 3 to 2)))
    }

    @Test fun aBoxOverTheGameAndEverythingThatIsNotAMissionAreLeftClicks() {
        // The game's menu over a selection: the Menu button's words greyed.
        assertEquals(Wc3Screen.State.OTHER, state(mission(lit = false, 0 to 0, 1 to 0, 2 to 0, 3 to 0)))
        // No coin: a menu, a movie, a loading screen.
        assertEquals(Wc3Screen.State.OTHER, state(Picture()))
        assertEquals(Wc3Screen.State.OTHER, state(Picture().apply { fill(Wc3Screen.MENU_BUTTON, white, 0.056f); fill(Wc3Screen.cell(0, 0), icon); fill(Wc3Screen.cell(1, 0), icon) }))
        // A bright page where the coin would be (the score screen's parchment) is not the coin.
        assertEquals(Wc3Screen.State.OTHER, state(mission(true, 0 to 0, 1 to 0).apply { fill(Wc3Screen.GOLD_COIN, 0xffc8b48c.toInt()) }))
        // Too small to be the game's screen.
        assertEquals(Wc3Screen.State.OTHER, Wc3Screen.state(100, 80) { _, _ -> gold })
    }

    @Test fun upsideDownAndWithRedAndBlueSwappedItReadsTheSame() {
        val worker = mission(true, 0 to 0, 1 to 0, 2 to 0, 3 to 0)
        assertEquals(Wc3Screen.State.COMMAND, Wc3Screen.state(960, 720, worker.flipped()))
        assertEquals(Wc3Screen.State.COMMAND, Wc3Screen.state(960, 720, worker.swapped()))
        val target = mission(true, 3 to 2)
        assertEquals(Wc3Screen.State.TARGET, Wc3Screen.state(960, 720, target.flipped()))
        // At the rig's other size.
        val small = Picture(800, 600).apply {
            fill(Wc3Screen.GOLD_COIN, gold)
            fill(Wc3Screen.MENU_BUTTON, white, 0.05f)
            fill(Wc3Screen.cell(0, 0), icon, 0.6f)
            fill(Wc3Screen.cell(1, 0), icon, 0.6f)
        }
        assertEquals(Wc3Screen.State.COMMAND, state(small))
    }

    /**
     * The game's own frames (the four races with nothing, a unit, several, a building selected, the game's menu and log over
     * them, a target wanted, a place to build wanted, the menus, movies, loading and score screens), each named for what it
     * shows: `<name>=<STATE>` lines in `expected.txt` beside them. Both ways up, and with red and blue swapped.
     */
    @Test fun theGamesOwnFrames() {
        val dir = System.getenv("BLIZZ_WC3_FRAMES")?.let { File(it) }
        assumeTrue(dir != null && File(dir, "expected.txt").isFile)
        val expected = File(dir, "expected.txt").readLines().filter { '=' in it }.associate { it.substringBefore('=').trim() to Wc3Screen.State.valueOf(it.substringAfter('=').trim()) }
        assertTrue("no frames named in expected.txt", expected.isNotEmpty())
        val wrong = ArrayList<String>()
        for ((name, want) in expected) {
            val image = javax.imageio.ImageIO.read(File(dir, name)) ?: error("$name can't be read")
            val w = image.width
            val h = image.height
            val rgb = image.getRGB(0, 0, w, h, null, 0, w)
            val upright = Wc3Screen.Pixels { x, y -> rgb[y * w + x] }
            val views = mapOf(
                "upright" to upright,
                "upside down" to Wc3Screen.Pixels { x, y -> rgb[(h - 1 - y) * w + x] },
                "red and blue swapped" to Wc3Screen.Pixels { x, y -> rgb[y * w + x].let { (it and 0xff00ff00.toInt()) or ((it and 0xff) shl 16) or ((it shr 16) and 0xff) } },
            )
            for ((how, view) in views) {
                val got = Wc3Screen.state(w, h, view)
                if (got != want) wrong += "$name ($how): $got, expected $want"
            }
        }
        assertTrue("${wrong.size} of ${expected.size} frames read wrong:\n" + wrong.joinToString("\n"), wrong.isEmpty())
    }
}
