package com.logie.blizz.controls

import org.junit.Assert.assertEquals
import org.junit.Test

/** 12. The touch controls: the one gesture system, its RTS mode and its action-RPG mode. */
class GesturesTest {
    private class Recorder : GestureOutput {
        val events = ArrayList<String>()
        override fun pointerTo(x: Float, y: Float) { events += "to ${x.toInt()},${y.toInt()}" }
        override fun click(button: Button) { events += "click $button" }
        override fun buttonDown(button: Button) { events += "down $button" }
        override fun buttonUp(button: Button) { events += "up $button" }
        override fun doubleClick(button: Button) { events += "double $button" }
        override fun wheel(up: Boolean) { events += "wheel $up" }
        override fun keyDown(key: Key) { events += "key down $key" }
        override fun keyUp(key: Key) { events += "key up $key" }
        override fun gameMenu() { events += "menu" }
        override fun openKeyboard() { events += "keyboard" }
        override fun showMenu() { events += "app menu" }
        override fun feedback() { events += "buzz" }
    }

    @Test fun rtsTapRightClicksHoldLeftClicksSwipePans() {
        val out = Recorder()
        val g = Gestures(out, 1f, Profile.RTS)
        g.down(0, 100f, 100f, 0); g.up(0, 100f, 100f, 50)
        assertEquals(listOf("to 100,100", "click RIGHT"), out.events)
        out.events.clear()
        g.down(0, 100f, 100f, 1000); g.onHold(1000 + Gestures.HOLD_MS); g.up(0, 100f, 100f, 1600)
        assertEquals(listOf("buzz", "to 100,100", "click LEFT"), out.events)
        out.events.clear()
        g.down(0, 100f, 100f, 5000); g.move(0, 200f, 100f); g.up(0, 200f, 100f, 5300)
        assertEquals(listOf("key down RIGHT", "key up RIGHT"), out.events)
    }

    @Test fun arpgTapLeftClicksHoldCastsSwipeWalks() {
        val out = Recorder()
        val g = Gestures(out, 1f, Profile.ARPG)
        g.down(0, 100f, 100f, 0); g.up(0, 100f, 100f, 50)
        assertEquals(listOf("to 100,100", "click LEFT"), out.events)
        out.events.clear()
        g.down(0, 100f, 100f, 1000); g.onHold(1000 + Gestures.HOLD_MS); g.up(0, 100f, 100f, 1600)
        assertEquals(listOf("buzz", "to 100,100", "click RIGHT"), out.events)
        out.events.clear()
        g.down(0, 100f, 100f, 5000); g.move(0, 150f, 100f, 5300); g.move(0, 220f, 130f, 5400); g.up(0, 220f, 130f, 5600)
        assertEquals(listOf("to 100,100", "down LEFT", "to 150,100", "to 220,130", "up LEFT"), out.events)
    }

    @Test fun arpgFlicksAreArrowKeysAndClickNothing() {
        val out = Recorder()
        val g = Gestures(out, 1f, Profile.ARPG)
        g.down(0, 100f, 100f, 0); g.move(0, 100f, 160f, 60); g.up(0, 100f, 200f, 120)
        assertEquals(listOf("key down DOWN", "key up DOWN"), out.events)
        out.events.clear()
        g.down(0, 300f, 100f, 1000); g.move(0, 250f, 105f, 1050); g.up(0, 200f, 110f, 1100)
        assertEquals(listOf("key down LEFT", "key up LEFT"), out.events)
        out.events.clear()
        g.down(0, 100f, 300f, 2000); g.move(0, 100f, 240f, 2050); g.up(0, 100f, 200f, 2100)
        assertEquals(listOf("key down UP", "key up UP"), out.events)
    }

    @Test fun twoThreeFourFingersAreTheSameInBothProfiles() {
        for (profile in Profile.entries) {
            val out = Recorder()
            val g = Gestures(out, 1f, profile)
            g.down(0, 10f, 10f, 0); g.down(1, 60f, 10f, 20); g.up(0, 10f, 10f, 100); g.up(1, 60f, 10f, 110)
            g.down(0, 10f, 10f, 1000); g.down(1, 60f, 10f, 1010); g.down(2, 110f, 10f, 1020); g.up(0, 10f, 10f, 1100); g.up(1, 60f, 10f, 1100); g.up(2, 110f, 10f, 1100)
            assertEquals(profile.name, listOf("menu", "keyboard"), out.events)
        }
    }
}
