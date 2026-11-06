// SPDX-License-Identifier: GPL-3.0-or-later
// Ported from the World of Warcraft app (com.logie.warcraft), unchanged apart from its package.

package com.logie.blizz.wowinput

/**
 * Whether a cutscene plays in the game, from the realm's word on it (patches/azerothcore/0008):
 * "c <time>" for a cinematic (a new character's intro, a quest's), "m <time>" for a movie, "- <time>"
 * once it's over. The game says when a cutscene ends, not always (a lost connection): one counts for
 * at most its longest run, so a hold doesn't stay Escape.
 */
object Cutscene {
    /** The longest in-game cinematic, with room. */
    const val CINEMATIC_MAX_S = 4 * 60L

    /** The longest movie (the Wrathgate), with room. */
    const val MOVIE_MAX_S = 8 * 60L

    fun isPlaying(word: String?, nowS: Long): Boolean {
        val parts = word?.trim()?.split(' ') ?: return false
        if (parts.size < 2) return false
        val since = parts[1].toLongOrNull() ?: return false
        val max = when (parts[0]) {
            "c" -> CINEMATIC_MAX_S
            "m" -> MOVIE_MAX_S
            else -> return false
        }
        return nowS - since in 0..max
    }
}
