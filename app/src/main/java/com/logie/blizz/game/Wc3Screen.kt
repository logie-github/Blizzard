package com.logie.blizz.game

/**
 * What Warcraft III's own picture says a tap should be. The person's layout (10 November 2026: "Tap to select then tap to
 * move. Double tap for left click. Hold tap for right click.") makes one tap do both jobs of the mouse: the left click while
 * there is nothing to command (select a unit, press a menu's button, confirm a target), the right click once units or a
 * building of the player's are selected (move, attack, gather, rally). Which it is cannot be asked of the game (it shuts its
 * process to other programs), so it is read off the screen, from three marks that are the same for all four races and in
 * both games (measured on the desktop rig at the phone's 960x720 and at 800x600, some sixty frames):
 *
 * - **the gold coin** of the resource bar, top right of centre: its colour is (106, 88, 25) on every race's interface, and
 *   nothing like it is there in a menu, a movie, a loading screen or a letterboxed scene. With it, the mission's interface is up.
 * - **the Menu button's words**, top left: white and yellow while the game takes orders, grey whenever a box of the game's is
 *   over it (its menu, the quest log, the message log, Options, End Game): bright pixels are 5 to 6 % of the button, or none.
 * - **the command card**, bottom right, a grid of four by three buttons: empty with nothing selected or with an enemy's or a
 *   neutral unit; buttons for the player's own units and buildings; and only Cancel, in the last place, while the game waits
 *   for a target or a place to build (the left click then).
 *
 * The picture may come upside down (the game's frame as OpenGL keeps it) and with red and blue the other way round: the marks
 * are looked for both ways up, and the colour tests read the same with red and blue swapped. Anything not recognised is
 * [State.OTHER], where a tap is the left click: the safe side, on which every button can be pressed. Plain Kotlin, unit-tested.
 */
object Wc3Screen {
    enum class State {
        /** No mission interface that takes orders: a menu, a movie, a loading screen, a scene, or a box of the game's over it. */
        OTHER,
        /** In a mission with nothing to command: nothing selected, or a unit that is not the player's. */
        IDLE,
        /** The game waits for a target or a place (a command was chosen): the command card shows only Cancel. */
        TARGET,
        /** Units or a building of the player's are selected: a tap on the battlefield is an order. */
        COMMAND,
    }

    /** A picture: the colour (0xAARRGGBB, or with red and blue swapped) at [x], [y], y counted from the top. */
    fun interface Pixels {
        fun argb(x: Int, y: Int): Int
    }

    /** A part of the screen in fractions of it. */
    data class Box(val left: Float, val top: Float, val right: Float, val bottom: Float)

    // Measured at 960x720 (the phone's game screen); every place is kept as a fraction, so other sizes of the same shape read alike.
    private const val W = 960f
    private const val H = 720f
    val MENU_BUTTON = Box(108 / W, 4 / H, 206 / W, 24 / H)
    val GOLD_COIN = Box(558 / W, 4 / H, 578 / W, 23 / H)
    /** The command card's buttons: four across, three down; the middle of the first, and the step to the next. */
    private const val CELL_X = 765 / W
    private const val CELL_Y = 585 / H
    private const val CELL_DX = 51.5f / W
    private const val CELL_DY = 51.3f / H
    private const val CELL_HALF_X = 19 / W
    private const val CELL_HALF_Y = 19 / H

    /** The parts of the picture [state] reads, for a reader that fetches no more than it must: the top band and the command card. */
    val TOP_BAND = Box(0.10f, 0f, 0.62f, 0.04f)
    val CARD_BAND = Box(0.76f, 0.76f, 1f, 1f)

    fun cell(column: Int, row: Int): Box {
        val cx = CELL_X + CELL_DX * column
        val cy = CELL_Y + CELL_DY * row
        return Box(cx - CELL_HALF_X, cy - CELL_HALF_Y, cx + CELL_HALF_X, cy + CELL_HALF_Y)
    }

    /** What the picture of [width] x [height] shows, looked at both ways up. */
    fun state(width: Int, height: Int, pixels: Pixels): State {
        if (width < 320 || height < 240) return State.OTHER
        val upright = read(width, height, pixels)
        if (upright != State.OTHER) return upright
        return read(width, height) { x, y -> pixels.argb(x, height - 1 - y) }
    }

    private fun read(width: Int, height: Int, pixels: Pixels): State {
        if (!coin(width, height, pixels) || !menuTakesOrders(width, height, pixels)) return State.OTHER
        var others = 0
        var cancel = false
        for (row in 0..2) for (column in 0..3) {
            if (!filled(width, height, pixels, cell(column, row))) continue
            if (row == 2 && column == 3) cancel = true else others++
        }
        return when {
            // Only Cancel (and at most the game's own cursor over an empty button): a target or a place is wanted.
            cancel && others <= 1 -> State.TARGET
            others + (if (cancel) 1 else 0) >= 2 -> State.COMMAND
            else -> State.IDLE
        }
    }

    private inline fun each(width: Int, height: Int, box: Box, visit: (Int, Int) -> Unit) {
        val x0 = Math.round(box.left * width).coerceIn(0, width - 1)
        val x1 = Math.round(box.right * width).coerceIn(x0 + 1, width)
        val y0 = Math.round(box.top * height).coerceIn(0, height - 1)
        val y1 = Math.round(box.bottom * height).coerceIn(y0 + 1, height)
        for (y in y0 until y1) for (x in x0 until x1) visit(x, y)
    }

    private fun red(c: Int) = (c shr 16) and 0xff
    private fun green(c: Int) = (c shr 8) and 0xff
    private fun blue(c: Int) = c and 0xff

    /** The resource bar's gold coin: a dull gold on average, whichever way round red and blue come. */
    internal fun coin(width: Int, height: Int, pixels: Pixels): Boolean {
        var r = 0L
        var g = 0L
        var b = 0L
        var n = 0
        each(width, height, GOLD_COIN) { x, y ->
            val c = pixels.argb(x, y)
            r += red(c); g += green(c); b += blue(c); n++
        }
        if (n == 0) return false
        val hi = (maxOf(r, b) / n).toInt()
        val lo = (minOf(r, b) / n).toInt()
        val mid = (g / n).toInt()
        return hi in 75..140 && mid in 60..115 && lo <= 55 && hi > mid && mid - lo >= 35
    }

    /**
     * The Menu button's words lit (white and yellow on a dark button), not greyed by a box over the game. The button is dark for
     * four fifths of it; with the game's own cursor resting on it (the button lights up under it) still for nearly half.
     */
    internal fun menuTakesOrders(width: Int, height: Int, pixels: Pixels): Boolean {
        var bright = 0
        var dark = 0
        var n = 0
        each(width, height, MENU_BUTTON) { x, y ->
            val c = pixels.argb(x, y)
            val top = maxOf(red(c), green(c), blue(c))
            if (top > 200 && green(c) > 170) bright++
            if (top < 90) dark++
            n++
        }
        if (n == 0) return false
        return bright >= n * 0.02f && bright <= n * 0.12f && dark >= n * 0.4f
    }

    /** A button on the command card (an icon fills its place; an empty place is black, and the game's cursor covers little of one). */
    internal fun filled(width: Int, height: Int, pixels: Pixels, box: Box): Boolean {
        var lit = 0
        var n = 0
        each(width, height, box) { x, y ->
            val c = pixels.argb(x, y)
            if (maxOf(red(c), green(c), blue(c)) > 40) lit++
            n++
        }
        return n > 0 && lit >= n * 0.30f
    }
}
