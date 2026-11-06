// SPDX-License-Identifier: GPL-3.0-or-later
// Ported from the World of Warcraft app (com.logie.warcraft), unchanged apart from its package.

package com.logie.blizz.wowinput

/**
 * WoW's cursor says what a click would do: the plain arrow over the ground and the interface; a
 * speech bubble over someone to talk to, a sword over an enemy, a bag over loot, a gear or a
 * flower over things to use or gather, and so on. On a PC those are right clicks. A tap looks at
 * the cursor where it lands (the game's cursor as the screen sees it, by its picture: [isSpecial]
 * takes a fingerprint of it) and, when it's one of those, clicks like a right click after the
 * left one ([confirms]).
 *
 * The arrow is learnt at the login screen, where it's the only cursor ([learnArrow]). If that
 * goes wrong (no cursor then, or another one in the world), the cursor most taps land on is the
 * plain one: taps mostly press buttons and walk the interface.
 *
 * Which special cursor means an enemy (the sword) is learnt from the realm: when a tap's click
 * selects something, the server says whether it's an enemy ([learn]; patches/azerothcore/0007).
 * A tap on an enemy only selects it; a second tap attacks. The other special cursors act at once.
 */
class CursorKinds {
    private var arrow: Long? = null
    private val recent = ArrayDeque<Long>()
    private val seen = HashSet<Long>()
    private val enemies = HashMap<Long, Boolean>()

    /** The realm's word on what a tap with [cursor] selected: an enemy or not. */
    fun learn(cursor: Long, enemy: Boolean) {
        if (enemies.size < 64 || cursor in enemies) enemies[cursor] = enemy
    }

    /** Whether [cursor] is over an enemy: true, false, or null when the realm hasn't said yet. */
    fun isEnemy(cursor: Long?): Boolean? = cursor?.let { enemies[it] }

    /**
     * The game's cursors can be told apart: more than one was seen. Until then (the game drawing
     * its own cursor into the picture, where the screen can't see it), taps can't tell an NPC
     * from the ground, and tapping one again talks to it instead.
     */
    val readable: Boolean get() = seen.size >= 2

    fun learnArrow(cursor: Long?) {
        if (cursor == null) return
        arrow = cursor
        see(cursor)
    }

    private fun see(cursor: Long) {
        if (seen.size < 64) seen += cursor
    }

    /** The cursor where a tap landed, before its click: one that offers more than a plain click. */
    fun isSpecial(cursor: Long?): Boolean {
        if (cursor == null) return false
        see(cursor)
        recent.addLast(cursor)
        if (recent.size > RECENT) recent.removeFirst()
        if (cursor == arrow) return false
        val known = arrow != null || recent.size >= LEARNING
        val usual = recent.size >= LEARNING && recent.count { it == cursor } * 10 >= recent.size * 6
        return known && !usual
    }

    /**
     * After the tap's left click: the same special cursor still there means it's someone or
     * something to use (the click only selected it). A different one means the click did something
     * else: put down an item held on the cursor, cast a spell aimed with it, picked an item up.
     */
    fun confirms(before: Long?, after: Long?): Boolean = before != null && after == before && after != arrow

    private companion object {
        const val RECENT = 12
        const val LEARNING = 6
    }
}
