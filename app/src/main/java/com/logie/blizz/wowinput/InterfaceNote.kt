// SPDX-License-Identifier: GPL-3.0-or-later
// Ported from the World of Warcraft app (com.logie.warcraft), unchanged apart from its package.

package com.logie.blizz.wowinput

/**
 * What the app's add-on in the game ([com.logie.warcraft.client.TouchAddon]) says about the game's
 * windows, through the realm on the phone, which keeps it in `files/run/interface`
 * (patches/azerothcore/0009): where the windows whose icons drag are (the spellbook, while it's
 * open), so a drag that starts there drags an icon, as a mouse would; and where a hold is a right
 * click (the bags, the bank, the character pane, the talents and the action bars, as they're
 * shown); and whether a window the player is using is open (the loot, a talk, a vendor...), where a
 * double tap doesn't jump.
 */
object InterfaceNote {
    /** A window's place, in fractions of the game's screen, from its top left. */
    data class Area(val left: Float, val top: Float, val right: Float, val bottom: Float) {
        fun contains(x: Float, y: Float) = x in left..right && y in top..bottom
    }

    private val SECTIONS = setOf("drag", "hold", "open")

    /**
     * The windows whose icons drag, from the note's "drag" part: "<left> <bottom> <right> <top>" for
     * each (thousandths of the screen from its bottom left, as WoW counts), or "-" for none.
     */
    fun dragAreas(note: String?): List<Area> = areas(note, "drag")

    /** Where a hold is a right click, from the note's "hold" part (as its "drag" part says them). */
    fun holdAreas(note: String?): List<Area> = areas(note, "hold")

    /**
     * Whether a window the player is using is open (the loot, a talk, a quest, a vendor, a trainer,
     * the flight master's map, the mail, a trade, the game's questions): the note's "open 1".
     */
    fun windowOpen(note: String?): Boolean {
        val words = note?.trim()?.split(' ')?.filter { it.isNotEmpty() } ?: return false
        val at = words.indexOf("open")
        return at >= 0 && words.getOrNull(at + 1) == "1"
    }

    private fun areas(note: String?, section: String): List<Area> {
        val words = note?.trim()?.split(' ')?.filter { it.isNotEmpty() } ?: return emptyList()
        val start = words.indexOf(section)
        if (start < 0) return emptyList()
        val numbers = words.drop(start + 1).takeWhile { it !in SECTIONS }
            .map { (it.toIntOrNull() ?: return emptyList()) / 1_000f }
        return numbers.chunked(4).filter { it.size == 4 }.mapNotNull { (left, bottom, right, top) ->
            if (right <= left || top <= bottom) null else Area(left, 1f - top, right, 1f - bottom)
        }
    }
}
