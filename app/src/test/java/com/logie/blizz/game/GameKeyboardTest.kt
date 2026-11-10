package com.logie.blizz.game

import com.logie.blizz.controls.KeyCombo
import com.logie.blizz.controls.xKeyName
import com.winlator.xserver.XKeycode
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

/** The app's keyboard: every cap is a key the X server has, letters follow Shift, the modifiers and the Hide key are there. */
class KeyboardLayoutTest {
    @Test fun everyKeyIsOneTheXServerHas() {
        for (row in KeyboardLayout.ROWS) for (key in row) {
            if (key.key == KeyboardLayout.HIDE) continue
            assertTrue("${key.key} is not a key of the Controls", key.key in KeyCombo.KEYS)
            XKeycode.valueOf(xKeyName(key.key))
        }
    }

    @Test fun lettersAndSymbolsFollowShift() {
        val q = KeyboardLayout.ROWS.flatten().first { it.key == "Q" }
        assertEquals("q", q.cap(false))
        assertEquals("Q", q.cap(true))
        val one = KeyboardLayout.ROWS.flatten().first { it.key == "1" }
        assertEquals("1", one.cap(false))
        assertEquals("!", one.cap(true))
        val esc = KeyboardLayout.ROWS.flatten().first { it.key == "Esc" }
        assertEquals("Esc", esc.cap(true))
    }

    @Test fun modifiersStayDownAndHideIsThere() {
        val all = KeyboardLayout.ROWS.flatten()
        assertEquals(setOf("Shift", "Ctrl", "Alt"), all.filter { it.modifier }.map { it.key }.toSet())
        assertEquals(1, all.count { it.key == KeyboardLayout.HIDE })
        assertFalse(all.first { it.key == KeyboardLayout.HIDE }.modifier)
        // What the games want most: Escape, the function keys, Enter, the arrows, Space.
        for (k in listOf("Esc", "F1", "F10", "F12", "Enter", "Up", "Down", "Left", "Right", "Space", "Backspace", "Tab")) assertTrue(k, all.any { it.key == k })
        assertEquals(6, KeyboardLayout.ROWS.size)
    }
}

/** The session's keeper starts every Windows game; it takes the frames off the games played in a window, never the World of Warcraft clients' or an installer's. */
class BorderlessTest {
    @Test fun framesOffForWindowedGamesOnly() {
        for (id in listOf("warcraft3_roc", "warcraft3_tft", "diablo2", "starcraft", "diablo", "starcraft2")) {
            assertTrue(id, Borderless.frames(id))
            assertEquals("C:\\windows\\borderless.exe", Borderless.command(id))
        }
        for (id in listOf("wow-client", "wow", "wow_forever", "installer", null)) {
            assertFalse(id ?: "null", Borderless.frames(id))
            assertEquals("C:\\windows\\borderless.exe /noframes", Borderless.command(id))
        }
    }
}
