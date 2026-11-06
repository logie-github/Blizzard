package com.logie.blizz.wowinput

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class CursorKindsTest {
    private val arrow = 1L
    private val speak = 2L
    private val attack = 3L
    private val item = 4L

    @Test
    fun theArrowIsAPlainClickAndTheOthersOfferMore() {
        val kinds = CursorKinds()
        kinds.learnArrow(arrow)
        assertFalse(kinds.isSpecial(arrow))
        assertTrue(kinds.isSpecial(speak))
        assertTrue(kinds.isSpecial(attack))
        assertFalse(kinds.isSpecial(null))
    }

    @Test
    fun theRightClickOnlyWhenTheSameCursorIsStillThere() {
        val kinds = CursorKinds()
        kinds.learnArrow(arrow)
        // An NPC: the left click selects it, the speech bubble stays: talk to it.
        assertTrue(kinds.confirms(speak, speak))
        // An item held on the cursor, put down in a bag: the cursor's the arrow again.
        assertFalse(kinds.confirms(item, arrow))
        // The click picked something up: another cursor.
        assertFalse(kinds.confirms(speak, item))
        assertFalse(kinds.confirms(null, null))
        assertFalse(kinds.confirms(arrow, arrow))
    }

    @Test
    fun withoutTheLoginScreensArrowTheUsualCursorIsThePlainOne() {
        val kinds = CursorKinds()
        // Not sure yet: plain clicks while learning, whatever the cursor.
        assertFalse(kinds.isSpecial(speak))
        repeat(4) { assertFalse(kinds.isSpecial(arrow)) }
        // Learnt: the arrow is what most taps land on.
        assertTrue(kinds.isSpecial(speak))
        assertFalse(kinds.isSpecial(arrow))
    }

    @Test
    fun readableOnceTwoCursorsWereSeen() {
        val kinds = CursorKinds()
        kinds.learnArrow(arrow)
        kinds.isSpecial(arrow)
        assertFalse(kinds.readable)
        kinds.isSpecial(speak)
        assertTrue(kinds.readable)
    }

    @Test
    fun theRealmSaysWhichCursorIsAnEnemy() {
        val kinds = CursorKinds()
        assertEquals(null, kinds.isEnemy(attack))
        kinds.learn(attack, enemy = true)
        kinds.learn(speak, enemy = false)
        assertEquals(true, kinds.isEnemy(attack))
        assertEquals(false, kinds.isEnemy(speak))
        assertEquals(null, kinds.isEnemy(item))
        assertEquals(null, kinds.isEnemy(null))
        // The latest word counts.
        kinds.learn(attack, enemy = false)
        assertEquals(false, kinds.isEnemy(attack))
    }

    @Test
    fun aWrongArrowCorrectsItself() {
        val kinds = CursorKinds()
        kinds.learnArrow(99L)
        assertTrue(kinds.isSpecial(arrow))
        repeat(6) { kinds.isSpecial(arrow) }
        assertFalse(kinds.isSpecial(arrow))
        assertTrue(kinds.isSpecial(speak))
    }
}
