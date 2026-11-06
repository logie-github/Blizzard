package com.logie.blizz.wowinput

import kotlin.test.Test
import kotlin.test.assertEquals

class InterfaceNoteTest {
    @Test
    fun theSpellbooksPlaceFromTheTopLeft() {
        assertEquals(
            listOf(InterfaceNote.Area(0.25f, 0.25f, 0.5f, 0.75f)),
            InterfaceNote.dragAreas("drag 250 250 500 750\n"),
        )
    }

    @Test
    fun whereAHoldIsARightClick() {
        val note = "drag 250 250 500 750 hold 700 100 990 600 0 0 1000 90\n"
        assertEquals(listOf(InterfaceNote.Area(0.25f, 0.25f, 0.5f, 0.75f)), InterfaceNote.dragAreas(note))
        assertEquals(
            listOf(InterfaceNote.Area(0.7f, 1f - 0.6f, 0.99f, 1f - 0.1f), InterfaceNote.Area(0f, 1f - 0.09f, 1f, 1f)),
            InterfaceNote.holdAreas(note),
        )
        assertEquals(emptyList(), InterfaceNote.dragAreas("drag - hold 0 0 1000 90"))
        assertEquals(listOf(InterfaceNote.Area(0f, 1f - 0.09f, 1f, 1f)), InterfaceNote.holdAreas("drag - hold 0 0 1000 90"))
        assertEquals(emptyList(), InterfaceNote.holdAreas("drag 250 250 500 750 hold -"))
        assertEquals(emptyList(), InterfaceNote.holdAreas("drag 250 250 500 750"))
    }

    @Test
    fun whetherAWindowThePlayerIsUsingIsOpen() {
        val note = "drag - hold 0 0 1000 90 open 1\n"
        assertEquals(true, InterfaceNote.windowOpen(note))
        // (the hold areas end where "open" starts)
        assertEquals(listOf(InterfaceNote.Area(0f, 1f - 0.09f, 1f, 1f)), InterfaceNote.holdAreas(note))
        for (closed in listOf(null, "", "drag - hold - open 0", "drag - hold -", "drag - hold - open")) {
            assertEquals(false, InterfaceNote.windowOpen(closed), closed.toString())
        }
    }

    @Test
    fun nothingWhenItsClosedOrTheNoteIsOdd() {
        for (note in listOf(null, "", "-", "drag -", "drag 1000 2000", "drag 500 200 100 900", "drag 0.1 0.2 0.3 0.4", "drag a b c d", "other 1000 2000 3000 4000")) {
            assertEquals(emptyList(), InterfaceNote.dragAreas(note), note.toString())
        }
    }
}
