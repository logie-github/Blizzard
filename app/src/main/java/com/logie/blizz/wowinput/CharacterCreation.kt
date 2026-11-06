// SPDX-License-Identifier: GPL-3.0-or-later
// Ported from the World of Warcraft app (com.logie.warcraft), unchanged apart from its package.

package com.logie.blizz.wowinput

import kotlin.math.max
import kotlin.math.min

/**
 * Whether the game shows its character creation screen, from a small picture of the game's
 * window: the race list's two banners down the left, the Alliance's blue one with the Horde's red
 * one to its right. The 3.3.5a client keeps that list at the screen's left edge and sizes it by
 * the screen's height, so the banners are at the same place in heights on any screen. No other
 * screen of the game has them there (character select, the login, the world).
 *
 * The picture is ARGB; one read with red and blue the other way round (RGBA) counts too.
 */
object CharacterCreation {
    /** Rows looked at, from [TOP] to [TOP] + [SPAN] of the height: down the length of the banners. */
    private const val ROWS = 20
    private const val TOP = 0.06f
    private const val SPAN = 0.38f

    /** Rows that have to show both banners: the race icons cover them in places. */
    private const val NEEDED = 14

    /** Where each banner is across, in heights from the left edge (the 3.3.5a client's layout). */
    private const val FIRST_FROM = 0.06f
    private const val FIRST_TO = 0.17f
    private const val SECOND_FROM = 0.18f
    private const val SECOND_TO = 0.30f

    /** Pixels of the banner's colour a row needs in each banner's span. */
    private const val PIXELS = 2

    private enum class Shade { BLUE, RED, OTHER }

    fun isShown(argb: IntArray, width: Int, height: Int): Boolean {
        if (width <= 0 || height < ROWS || argb.size < width * height) return false
        val firstFrom = (FIRST_FROM * height).toInt()
        val firstTo = min(width - 1, (FIRST_TO * height).toInt())
        val secondFrom = (SECOND_FROM * height).toInt()
        val secondTo = min(width - 1, (SECOND_TO * height).toInt())
        if (secondFrom >= width) return false
        var blueThenRed = 0
        var redThenBlue = 0
        for (i in 0 until ROWS) {
            val y = (height * (TOP + SPAN * i / (ROWS - 1))).toInt()
            val first = count(argb, y * width, firstFrom, firstTo)
            val second = count(argb, y * width, secondFrom, secondTo)
            if (first.blue >= PIXELS && second.red >= PIXELS) blueThenRed++
            if (first.red >= PIXELS && second.blue >= PIXELS) redThenBlue++
        }
        return max(blueThenRed, redThenBlue) >= NEEDED
    }

    private class Count(var blue: Int = 0, var red: Int = 0)

    private fun count(argb: IntArray, row: Int, from: Int, to: Int): Count {
        val count = Count()
        for (x in from..to) {
            when (shade(argb[row + x])) {
                Shade.BLUE -> count.blue++
                Shade.RED -> count.red++
                Shade.OTHER -> {}
            }
        }
        return count
    }

    /** A strong blue or a strong red, as the banners' cloth is (lit or in shadow). */
    private fun shade(color: Int): Shade {
        val r = (color shr 16) and 0xff
        val g = (color shr 8) and 0xff
        val b = color and 0xff
        return when {
            b >= 90 && b * 10 >= r * 16 && b * 10 >= g * 13 -> Shade.BLUE
            r >= 90 && r * 10 >= g * 18 && r * 10 >= b * 18 -> Shade.RED
            else -> Shade.OTHER
        }
    }
}
