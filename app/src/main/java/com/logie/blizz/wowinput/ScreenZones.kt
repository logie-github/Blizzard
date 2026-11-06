// SPDX-License-Identifier: GPL-3.0-or-later
// Ported from the World of Warcraft app (com.logie.warcraft), unchanged apart from its package.

package com.logie.blizz.wowinput

/**
 * Where the game's action bars are, for taps: WoW's own interface puts them along the bottom (the
 * main bar and the two above it) and down the right edge (the right-hand bars). The game's
 * pointer looks the same over a button as over the ground, so the app goes by the place: a quick
 * second tap there is another press of the button, never a jump.
 */
object ScreenZones {
    /** The bottom of the screen, as a share of its height, where the bars are. */
    const val BOTTOM = 0.22f

    /** The right edge, as a share of its width. */
    const val RIGHT = 0.08f

    fun isActionBars(x: Float, y: Float, width: Float, height: Float): Boolean =
        width > 0f && height > 0f && (y >= height * (1 - BOTTOM) || x >= width * (1 - RIGHT))
}
