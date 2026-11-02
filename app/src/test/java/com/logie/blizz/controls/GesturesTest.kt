package com.logie.blizz.controls

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

/** The gesture engine and the game's rules: what a gesture does where, for each game's defaults and for the person's own. */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class GesturesTest {
    private class Recorder : GestureOutput {
        val events = ArrayList<String>()
        override fun pointerTo(x: Float, y: Float) { events += "to ${x.toInt()},${y.toInt()}" }
        override fun click(button: Button) { events += "click $button" }
        override fun doubleClick(button: Button) { events += "double $button" }
        override fun buttonDown(button: Button) { events += "down $button" }
        override fun buttonUp(button: Button) { events += "up $button" }
        override fun wheel(up: Boolean) { events += "wheel $up" }
        override fun keyDown(key: String) { events += "+$key" }
        override fun keyUp(key: String) { events += "-$key" }
        override fun openKeyboard() { events += "keyboard" }
        override fun showMenu() { events += "app menu" }
        override fun feedback() { events += "buzz" }
    }

    private val screen = 1000f

    /** A game's engine on a 1000-pixel screen, its rules the game's defaults unless [rules] says. */
    private fun engine(game: String, out: Recorder, rules: List<Rule>? = null): Gestures {
        val controls = ControlsStore.defaults(game).let { if (rules != null) it.copy(rules = rules) else it }
        return Gestures(out, 1f, Bindings.of(game, controls), locate = { x, y -> x / screen to y / screen })
    }

    private fun Gestures.tap(x: Float, y: Float, at: Long) { down(0, x, y, at); up(0, x, y, at + 50) }

    // The defaults ---------------------------------------------------------------------------------

    @Test fun diabloTapClicksHoldCastsDragWalks() {
        val out = Recorder()
        val g = engine("diablo", out)
        g.tap(500f, 300f, 0)
        assertEquals(listOf("to 500,300", "click LEFT"), out.events)
        out.events.clear()
        g.down(0, 100f, 100f, 1000); g.tick(1000 + Gestures.HOLD_MS); g.up(0, 100f, 100f, 1600)
        assertEquals(listOf("buzz", "to 100,100", "click RIGHT"), out.events)
        out.events.clear()
        g.down(0, 100f, 100f, 5000); g.move(0, 150f, 100f, 5300); g.move(0, 220f, 130f, 5400); g.up(0, 220f, 130f, 5600)
        assertEquals(listOf("to 100,100", "down LEFT", "to 150,100", "to 220,130", "up LEFT"), out.events)
    }

    @Test fun diabloFlicksAreArrowKeysAndClickNothing() {
        val out = Recorder()
        val g = engine("diablo", out)
        g.down(0, 100f, 100f, 0); g.move(0, 100f, 160f, 60); g.up(0, 100f, 200f, 120)
        assertEquals(listOf("+Down", "-Down"), out.events)
        out.events.clear()
        g.down(0, 300f, 100f, 1000); g.move(0, 250f, 105f, 1050); g.up(0, 200f, 110f, 1100)
        assertEquals(listOf("+Left", "-Left"), out.events)
    }

    @Test fun starcraftTapRightClicksPanelsLeftClick() {
        val out = Recorder()
        val g = engine("starcraft", out)
        g.tap(500f, 400f, 0)
        assertEquals(listOf("to 500,400", "click RIGHT"), out.events)
        out.events.clear()
        g.tap(500f, 900f, 1000)
        assertEquals(listOf("to 500,900", "click LEFT"), out.events)
    }

    @Test fun starcraftSwipePansWithTheArrowKeys() {
        val out = Recorder()
        val g = engine("starcraft", out)
        g.down(0, 100f, 100f, 0); g.move(0, 200f, 100f, 600); g.up(0, 200f, 100f, 700)
        assertEquals(listOf("+Right", "-Right"), out.events)
    }

    @Test fun threeAndFourFingersAreTheSameEverywhere() {
        for (game in listOf("diablo", "diablo2", "starcraft", "starcraft2", "warcraft3_tft")) {
            val out = Recorder()
            val g = engine(game, out)
            g.down(0, 10f, 10f, 0); g.down(1, 60f, 10f, 10); g.down(2, 110f, 10f, 20); g.up(0, 10f, 10f, 100); g.up(1, 60f, 10f, 100); g.up(2, 110f, 10f, 100)
            g.down(0, 10f, 10f, 1000); g.down(1, 60f, 10f, 1010); g.down(2, 110f, 10f, 1020); g.down(3, 160f, 10f, 1030)
            for (i in 0..3) g.up(i, 10f, 10f, 1100)
            assertEquals(game, listOf("keyboard", "app menu"), out.events)
        }
    }

    // The person's own rules ------------------------------------------------------------------------

    private fun rule(t: Trigger, f: String, area: String = "anywhere") = Rule(t, area, f)

    @Test fun ifTwoFingerTapThenEscapeWhereItsGivenAKey() {
        val out = Recorder()
        val g = engine("diablo", out, listOf(rule(Trigger.TWO_FINGER_TAP, "esc")))
        g.down(0, 100f, 100f, 0); g.down(1, 160f, 100f, 20); g.up(0, 100f, 100f, 100); g.up(1, 160f, 100f, 110)
        assertEquals(listOf("+Esc", "-Esc"), out.events)
    }

    @Test fun smallestAreaWins() {
        val out = Recorder()
        val rules = listOf(rule(Trigger.TAP, "click"), rule(Trigger.TAP, "rclick", "bottom-right"), rule(Trigger.TAP, "none", "commands"))
        val g = engine("starcraft", out, rules)
        g.tap(100f, 100f, 0)
        g.tap(600f, 600f, 500)
        // The command card (a smaller area inside the bottom right) switches that spot off.
        g.tap(900f, 900f, 1000)
        assertEquals(listOf("to 100,100", "click LEFT", "to 600,600", "click RIGHT"), out.events)
    }

    @Test fun doubleTapWaitsForASecondTapOnlyWhereTheRulesUseOne() {
        val out = Recorder()
        val rules = listOf(rule(Trigger.TAP, "rclick"), rule(Trigger.DOUBLE_TAP, "dclick", "top-left"))
        val g = engine("starcraft", out, rules)
        // Outside the area: a tap acts at once.
        g.tap(800f, 800f, 0)
        assertEquals(listOf("to 800,800", "click RIGHT"), out.events)
        out.events.clear()
        // Inside: one tap waits, then acts when the second doesn't come.
        g.tap(100f, 100f, 1000)
        assertTrue(out.events.isEmpty())
        g.tick(1000 + 50 + Gestures.DOUBLE_MS + 10)
        assertEquals(listOf("to 100,100", "click RIGHT"), out.events)
        out.events.clear()
        // Two taps: the double tap, and not the taps.
        g.tap(100f, 100f, 3000); g.tap(105f, 100f, 3200)
        assertEquals(listOf("to 105,100", "double LEFT"), out.events)
    }

    @Test fun doubleTapHoldAndTwoThenOne() {
        val out = Recorder()
        val rules = listOf(rule(Trigger.TAP, "rclick"), rule(Trigger.DOUBLE_TAP_HOLD, "dclick"), rule(Trigger.TWO_FINGER_TAP, "esc"), rule(Trigger.TWO_THEN_ONE_TAP, "enter"))
        val g = engine("starcraft", out, rules)
        g.tap(300f, 300f, 0)
        g.down(0, 300f, 300f, 200); g.tick(200 + Gestures.HOLD_MS); g.up(0, 300f, 300f, 800)
        // The first tap acts at once (nothing waits for a hold that may never come); the hold on top of it is the double tap hold.
        assertEquals(listOf("to 300,300", "click RIGHT", "buzz", "to 300,300", "double LEFT"), out.events)
        out.events.clear()
        // Two fingers, then one: Enter; two alone: Escape, once the wait runs out.
        g.down(0, 100f, 100f, 2000); g.down(1, 150f, 100f, 2010); g.up(0, 100f, 100f, 2100); g.up(1, 150f, 100f, 2110)
        g.tap(400f, 400f, 2300)
        assertEquals(listOf("+Enter", "-Enter"), out.events)
        out.events.clear()
        g.down(0, 100f, 100f, 5000); g.down(1, 150f, 100f, 5010); g.up(0, 100f, 100f, 5100); g.up(1, 150f, 100f, 5110)
        g.tick(5110 + Gestures.SEQUENCE_MS + 10)
        assertEquals(listOf("+Esc", "-Esc"), out.events)
    }

    @Test fun aKeyHeldForAsLongAsTheFingerStays() {
        val out = Recorder()
        val g = engine("diablo", out, listOf(rule(Trigger.HOLD, "highlight")))
        g.down(0, 100f, 100f, 0); g.tick(Gestures.HOLD_MS)
        assertEquals(listOf("buzz", "+Alt"), out.events)
        out.events.clear()
        g.up(0, 100f, 100f, 900)
        assertEquals(listOf("-Alt"), out.events)
    }

    @Test fun recordingReportsWhatWasDoneAndWhere() {
        val seen = ArrayList<Triple<Trigger, Float, Float>>()
        val g = Gestures(Recorder(), 1f, bindings = null, locate = { x, y -> x / screen to y / screen }, onRecord = { t, x, y -> seen += Triple(t, x, y) })
        g.tap(200f, 300f, 0)
        g.tick(400)
        g.down(0, 700f, 700f, 1000); g.tick(1000 + Gestures.HOLD_MS); g.up(0, 700f, 700f, 1700)
        assertEquals(listOf(Trigger.TAP, Trigger.HOLD), seen.map { it.first })
        assertEquals(200f, seen[0].second, 0.1f)
    }

    // Keys and the catalog ------------------------------------------------------------------------

    @Test fun keyCombosParseAndPrint() {
        assertEquals("Ctrl+Shift+F2", KeyCombo.of("shift+ctrl+f2").label)
        assertEquals(KeyCombo("Up"), KeyCombo.of("up"))
        assertNull(KeyCombo.parse("Hyper+Q"))
        assertEquals("KEY_BRACKET_LEFT", xKeyName("["))
        assertEquals("KEY_PRIOR", xKeyName("PgUp"))
    }

    @Test fun everyGamesCatalogIsConsistent() {
        for (game in listOf("diablo", "diablo2", "starcraft", "starcraft2", "warcraft", "warcraft2", "warcraft3_roc", "warcraft3_tft")) {
            val c = Catalog.of(game)
            assertEquals(game, c.functions.size, c.functions.map { it.id }.toSet().size)
            for (f in c.functions) if (f.kind.usesKey) assertTrue("$game ${f.id}", f.key != null && f.key.key in KeyCombo.KEYS)
            for (r in c.rules) {
                assertTrue("$game ${r.function}", c.function(r.function) != null)
                assertTrue("$game ${r.area}", c.area(r.area) != null)
            }
        }
    }

    @Test fun diabloKeysAreDevilutionXs() {
        val keys = Catalog.DIABLO.functions.filter { it.kind.usesKey }.associate { it.id to it.key!!.label }
        assertEquals("I", keys["inventory"]); assertEquals("C", keys["character"]); assertEquals("Q", keys["quests"])
        assertEquals("B", keys["spellbook"]); assertEquals("F2", keys["save"]); assertEquals("F3", keys["load"]); assertEquals("Tab", keys["automap"])
    }

    @Test fun controlsAreSavedAndReset() {
        val dir = java.nio.file.Files.createTempDirectory("controls").toFile()
        val store = ControlsStore(dir)
        val edited = store.load("diablo").let { it.copy(keys = it.keys + ("inventory" to KeyCombo.of("Ctrl+I")), rules = it.rules + rule(Trigger.PINCH_OUT, "zoom")) }
        store.save(edited)
        val back = store.load("diablo")
        assertEquals(KeyCombo.of("Ctrl+I"), Bindings.of("diablo", back).keyOf(Catalog.DIABLO.function("inventory")!!))
        assertTrue(back.rules.contains(rule(Trigger.PINCH_OUT, "zoom")))
        store.reset("diablo")
        assertEquals(ControlsStore.defaults("diablo"), store.load("diablo"))
    }

    @Test fun theStampChangesWhenTheSavedControlsDo() {
        val dir = java.io.File(System.getProperty("java.io.tmpdir"), "controls-stamp-${System.nanoTime()}")
        val store = ControlsStore(dir)
        val none = store.stamp("diablo")
        store.save(ControlsStore.defaults("diablo").copy(keys = mapOf("x" to com.logie.blizz.controls.KeyCombo.parse("F5")!!)))
        val saved = store.stamp("diablo")
        assertTrue(saved != none)
        store.reset("diablo")
        assertEquals(none, store.stamp("diablo"))
        dir.deleteRecursively()
    }

    @Test fun aRuleAddedForAGestureAndAreaAlreadyUsedBeatsTheDefault() {
        val base = ControlsStore.defaults("diablo")
        val added = base.copy(rules = base.rules + Rule(Trigger.TAP, "anywhere", "rclick"))
        assertEquals("rclick", Bindings.of("diablo", added).resolve(Trigger.TAP, 0.5f, 0.5f)?.id)
        // And after saving and loading, as the game does.
        val dir = java.io.File(System.getProperty("java.io.tmpdir"), "controls-rule-${System.nanoTime()}")
        val store = ControlsStore(dir)
        store.save(added)
        assertEquals("rclick", Bindings.of("diablo", store.load("diablo")).resolve(Trigger.TAP, 0.5f, 0.5f)?.id)
        dir.deleteRecursively()
    }
}
