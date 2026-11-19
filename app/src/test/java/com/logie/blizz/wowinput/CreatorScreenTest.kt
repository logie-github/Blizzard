package com.logie.blizz.wowinput

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

/** Wrath++'s creator telling the touch it is up, and where its lists drag ([CreatorScreen]). */
class CreatorScreenTest {
    @get:Rule val tmp = TemporaryFolder()

    @Test fun upDownOrNothingSaid() {
        assertEquals(true, CreatorScreen.up("creator 1 drag\n"))
        assertEquals(true, CreatorScreen.up("creator 1 drag 680 120 975 610"))
        assertEquals(false, CreatorScreen.up("creator 0\n"))
        assertNull(CreatorScreen.up(null)); assertNull(CreatorScreen.up("")); assertNull(CreatorScreen.up("creator")); assertNull(CreatorScreen.up("open 1"))
    }

    @Test fun theListsAreWhereAFingerDrags() {
        // the option list on the right (from its bottom left, as the game counts) and an open list of choices
        val areas = CreatorScreen.dragAreas("creator 1 drag 680 120 975 610 700 300 940 590\n")
        assertEquals(2, areas.size)
        assertTrue(areas[0].contains(0.8f, 0.5f))                  // the middle of the list, from the top left
        assertFalse(areas[0].contains(0.5f, 0.5f))                 // the character: turned, not dragged
        assertFalse(areas[0].contains(0.8f, 0.95f))                // under the list: Finish
        assertTrue(CreatorScreen.dragAreas("creator 1 drag\n").isEmpty())
        assertTrue(CreatorScreen.dragAreas("creator 0 drag 680 120 975 610").isEmpty())
    }

    @Test fun onlyAWordWrittenSinceTheGameStarted() {
        val file = File(tmp.root, "wrathpp-screen.txt").apply { writeText("creator 1 drag\n"); setLastModified(10_000) }
        assertNull(CreatorScreen.read(file, since = 20_000))
        assertEquals("creator 1 drag\n", CreatorScreen.read(file, since = 9_000))
        assertNull(CreatorScreen.read(File(tmp.root, "none.txt"), since = 0))
    }
}
