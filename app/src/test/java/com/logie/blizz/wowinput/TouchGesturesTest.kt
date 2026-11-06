package com.logie.blizz.wowinput

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class TouchGesturesTest {
    /** What the gestures did, as text. */
    private class Log : GestureOutput {
        val events = mutableListOf<String>()
        /** Where a window whose icons drag is (the spellbook): none at first. */
        var dragArea: ((Float, Float) -> Boolean) = { _, _ -> false }
        override fun dragsAt(x: Float, y: Float) = dragArea(x, y)
        /** Where a hold is a right click (the bags, the action bars...): none at first. */
        var rightClickArea: ((Float, Float) -> Boolean) = { _, _ -> false }
        override fun rightClicksAt(x: Float, y: Float) = rightClickArea(x, y)
        /** The character creation screen is up. */
        var characterCreation = false
        override fun turnsModel() = characterCreation
        override fun pointerTo(x: Float, y: Float) { events += "to ${x.toInt()},${y.toInt()}" }
        override fun tapAt(x: Float, y: Float) { events += "tap at ${x.toInt()},${y.toInt()}" }
        override fun targetNearestEnemy() { events += "tab" }
        override fun doubleTapAt(x: Float, y: Float) { events += "double tap at ${x.toInt()},${y.toInt()}" }
        /** Whether the first tap is known to have found the open ground (a jump can be done at once). */
        var openGround = false
        override fun doubleTapNow(x: Float, y: Float): Boolean {
            if (!openGround) return false
            events += "jump now at ${x.toInt()},${y.toInt()}"
            return true
        }
        override fun pointerBy(dx: Float, dy: Float) { events += "by ${dx.toInt()},${dy.toInt()}" }
        override fun press(button: Button) { events += "press $button" }
        override fun release(button: Button) { events += "release $button" }
        override fun click(button: Button) { events += "click $button" }
        override fun keyDown(key: Key) { events += "down $key" }
        override fun keyUp(key: Key) { events += "up $key" }
        override fun tap(key: Key) { events += "tap $key" }
        override fun playing() { events += "playing" }
        override fun openChat() { events += "chat" }
        override fun showKeyboard() { events += "keyboard" }
        override fun showMenu() { events += "menu" }
    }

    private val log = Log()
    // Density 1: the distances below are in dp. A 1000 x 600 screen: the left half is x < 500.
    private val gestures = TouchGestures(log, density = 1f).apply { setSize(1000f, 600f) }

    @Test
    fun tapClicksWhereTheFingerIsOnEitherHalf() {
        gestures.down(0, 100f, 200f, 0)
        gestures.up(0, 102f, 201f, 80)
        gestures.down(0, 800f, 500f, 1000)
        gestures.up(0, 800f, 500f, 1080)
        assertEquals(listOf("tap at 102,201", "tap at 800,500"), log.events)
    }

    @Test
    fun doubleTapJumps() {
        gestures.down(0, 700f, 200f, 0)
        gestures.up(0, 700f, 200f, 80)
        gestures.down(0, 710f, 205f, 200)
        gestures.up(0, 710f, 205f, 260)
        assertEquals(listOf("tap at 700,200", "double tap at 710,205"), log.events)
    }

    @Test
    fun afterATapOnTheOpenGroundTheJumpComesAsTheSecondFingerLands() {
        log.openGround = true
        gestures.down(0, 700f, 200f, 0)
        gestures.up(0, 700f, 200f, 80)
        gestures.down(0, 710f, 205f, 200)
        // (before it lifts)
        assertEquals(listOf("tap at 700,200", "jump now at 710,205"), log.events)
        gestures.up(0, 710f, 205f, 260)
        // (and nothing again as it lifts; a third tap is a tap of its own)
        gestures.down(0, 710f, 205f, 400)
        gestures.up(0, 710f, 205f, 460)
        assertEquals(listOf("tap at 700,200", "jump now at 710,205", "tap at 710,205"), log.events)
    }

    @Test
    fun afterATapOnAnNpcTheSecondTapWaitsToLiftAsBefore() {
        // (the first tap's click still at work, or it talked: nothing as the second finger lands)
        gestures.down(0, 700f, 200f, 0)
        gestures.up(0, 700f, 200f, 80)
        gestures.down(0, 710f, 205f, 200)
        assertEquals(listOf("tap at 700,200"), log.events)
        gestures.up(0, 710f, 205f, 260)
        assertEquals(listOf("tap at 700,200", "double tap at 710,205"), log.events)
    }

    @Test
    fun aSecondTapThatSwipesAfterAGroundTapJumpsAndThenSteers() {
        log.openGround = true
        gestures.down(0, 300f, 400f, 0)
        gestures.up(0, 300f, 400f, 80)
        gestures.down(0, 305f, 400f, 200)
        gestures.move(0, 305f, 300f)
        gestures.up(0, 305f, 300f, 600)
        assertEquals("jump now at 305,400", log.events[1])
        assertTrue(log.events.none { it.startsWith("tap at 305") || it.startsWith("double tap") })
    }

    @Test
    fun aStillHoldRightClicksEvenAfterATap() {
        gestures.down(0, 100f, 200f, 0)
        gestures.onHold(TouchGestures.HOLD_MS)
        gestures.up(0, 100f, 200f, 900)
        gestures.down(0, 600f, 300f, 2000)
        gestures.up(0, 600f, 300f, 2080)
        gestures.down(0, 600f, 300f, 2200)
        gestures.onHold(2200 + TouchGestures.HOLD_MS)
        gestures.up(0, 600f, 300f, 2900)
        assertEquals(listOf("to 100,200", "click RIGHT", "tap at 600,300", "to 600,300", "click RIGHT"), log.events)
    }

    @Test
    fun aHoldThatDriftsStaysAHold() {
        // A finger settling after the hold, up to 30 px: right click at its held origin.
        gestures.down(0, 600f, 300f, 0)
        gestures.onHold(TouchGestures.HOLD_MS)
        gestures.move(0, 615f, 310f)
        gestures.move(0, 625f, 315f)
        gestures.up(0, 625f, 315f, 1500)
        assertEquals(listOf("to 600,300", "click RIGHT"), log.events)
    }

    @Test
    fun aHoldThenAMoveDragsWithTheLeftButtonFromWhereItWasHeld() {
        // TomTom's arrow at the top: held, then dragged down and across, as the mouse moves it.
        gestures.down(0, 600f, 100f, 0)
        gestures.onHold(TouchGestures.HOLD_MS)
        gestures.move(0, 605f, 103f) // (still within a tap's reach: nothing yet)
        gestures.move(0, 640f, 150f)
        gestures.move(0, 700f, 250f)
        gestures.up(0, 710f, 260f, 2000)
        // On the left half too (Immersion's dialog at the bottom): a drag, not the stick, and no bags.
        gestures.down(0, 300f, 500f, 3000)
        gestures.onHold(3000 + TouchGestures.HOLD_MS)
        gestures.move(0, 300f, 400f)
        gestures.up(0, 300f, 400f, 4000)
        assertEquals(
            listOf(
                "to 600,100", "press LEFT", "to 640,150", "to 700,250", "to 710,260", "release LEFT",
                "to 300,500", "press LEFT", "to 300,400", "to 300,400", "release LEFT",
            ),
            log.events,
        )
    }

    @Test
    fun leftSwipeWalksWithSidewaysSteps() {
        gestures.down(0, 200f, 400f, 0)
        gestures.move(0, 200f, 370f) // up
        gestures.move(0, 170f, 370f) // up and left
        gestures.move(0, 160f, 400f) // left
        gestures.move(0, 240f, 400f) // right
        gestures.up(0, 240f, 400f, 2000)
        assertEquals(listOf("playing", "down W", "down Q", "up W", "up Q", "down E", "up E"), log.events)
    }

    @Test
    fun theStickFollowsAThumbThatGoesFurther() {
        gestures.down(0, 200f, 500f, 0)
        gestures.move(0, 200f, 300f) // far up: the base follows to 200,370
        gestures.move(0, 200f, 330f) // back down a little: still up, past the base
        gestures.move(0, 200f, 420f) // below the base: back
        gestures.up(0, 200f, 420f, 2000)
        assertEquals(listOf("playing", "down W", "up W", "down S", "up S"), log.events)
    }

    @Test
    fun rightDragTurnsFromTheMiddleOfTheScreen() {
        gestures.down(0, 800f, 300f, 0)
        gestures.move(0, 830f, 300f)
        gestures.move(0, 850f, 290f)
        gestures.up(0, 850f, 290f, 900)
        assertEquals(listOf("playing", "to 500,240", "press RIGHT", "by 20,-10", "release RIGHT"), log.events)
    }

    @Test
    fun walkAndTurnTogetherFromThumbsThatLandTogether() {
        gestures.down(0, 200f, 400f, 0)
        gestures.down(1, 800f, 400f, 50)
        gestures.move(0, 200f, 375f) // the left thumb up
        gestures.move(1, 825f, 400f) // the right thumb right
        gestures.move(0, 200f, 360f)
        gestures.move(1, 840f, 400f)
        gestures.up(0, 200f, 360f, 2000)
        gestures.up(1, 840f, 400f, 2000)
        assertTrue("down W" in log.events, log.events.toString())
        assertTrue("press RIGHT" in log.events, log.events.toString())
        assertTrue(log.events.none { it.startsWith("click WHEEL") }, log.events.toString())
        assertEquals(listOf("up W", "release RIGHT"), log.events.takeLast(2))
    }

    @Test
    fun aTapWhileWalkingClicksAndADoubleTapJumps() {
        gestures.down(0, 200f, 400f, 0)
        gestures.move(0, 200f, 370f)
        gestures.down(1, 700f, 550f, 500)
        gestures.up(1, 700f, 550f, 560)
        gestures.down(1, 700f, 550f, 700)
        gestures.up(1, 700f, 550f, 760)
        gestures.up(0, 200f, 370f, 2000)
        assertEquals(listOf("playing", "down W", "tap at 700,550", "double tap at 700,550", "up W"), log.events)
    }

    @Test
    fun pinchZooms() {
        gestures.down(0, 400f, 300f, 0)
        gestures.down(1, 600f, 300f, 40)
        gestures.move(0, 370f, 300f)
        gestures.move(1, 630f, 300f) // 60 apart more: two notches in
        gestures.move(0, 400f, 300f)
        gestures.move(1, 600f, 300f) // back: two notches out
        gestures.up(0, 400f, 300f, 900)
        gestures.up(1, 600f, 300f, 910)
        assertEquals(
            listOf("to 500,240", "click WHEEL_UP", "click WHEEL_UP", "click WHEEL_DOWN", "click WHEEL_DOWN"),
            log.events,
        )
    }

    @Test
    fun twoFingerTapTargetsTheNearestEnemy() {
        gestures.down(0, 300f, 300f, 0)
        gestures.down(1, 400f, 300f, 30)
        gestures.up(1, 400f, 300f, 120)
        gestures.up(0, 300f, 300f, 150)
        assertEquals(listOf("tab"), log.events)
    }

    @Test
    fun twoFingersUpOpenTheChat() {
        gestures.down(0, 450f, 400f, 0)
        gestures.down(1, 550f, 400f, 30)
        for (step in 1..5) {
            gestures.move(0, 450f, 400f - step * 10)
            gestures.move(1, 550f, 400f - step * 10)
        }
        gestures.up(0, 450f, 350f, 500)
        gestures.up(1, 550f, 350f, 510)
        assertEquals(listOf("chat"), log.events)
    }

    @Test
    fun threeFingerTapShowsTheKeyboardAndFourTheMenu() {
        for (id in 0..2) gestures.down(id, 300f + 100f * id, 300f, id * 20L)
        for (id in 0..2) gestures.up(id, 300f + 100f * id, 300f, 200 + id * 20L)
        for (id in 0..3) gestures.down(id, 300f + 100f * id, 300f, 1000 + id * 20L)
        for (id in 0..3) gestures.up(id, 300f + 100f * id, 300f, 1200 + id * 20L)
        assertEquals(listOf("keyboard", "menu"), log.events)
    }

    @Test
    fun cancelLetsGoOfEverything() {
        gestures.down(0, 200f, 400f, 0)
        gestures.move(0, 230f, 370f)
        gestures.down(1, 800f, 300f, 600)
        gestures.move(1, 840f, 300f)
        gestures.cancel()
        assertEquals(
            listOf("playing", "down W", "down E", "playing", "to 500,240", "press RIGHT", "up W", "up E", "release RIGHT"),
            log.events,
        )
    }

    @Test
    fun eightDirections() {
        assertEquals(setOf(Key.E), directionKeys(1f, 0f))
        assertEquals(setOf(Key.S), directionKeys(0f, 1f))
        assertEquals(setOf(Key.Q), directionKeys(-1f, 0.1f))
        assertEquals(setOf(Key.Q), directionKeys(-1f, -0.1f))
        assertEquals(setOf(Key.W), directionKeys(0f, -1f))
        assertEquals(setOf(Key.W, Key.E), directionKeys(1f, -1f))
        assertEquals(setOf(Key.S, Key.Q), directionKeys(-1f, 1f))
    }

    @Test
    fun onTheSpellbookTheFingerDragsWithTheLeftButton() {
        log.dragArea = { x, y -> x < 300 && y < 400 }
        // A spell dragged from the spellbook down to the action bar, across the screen: the left
        // button goes down where the finger came, once it moves.
        gestures.down(0, 100f, 200f, 0)
        gestures.move(0, 105f, 203f)
        gestures.move(0, 130f, 260f)
        gestures.move(0, 600f, 560f)
        gestures.onHold(TouchGestures.HOLD_MS)
        gestures.up(0, 610f, 570f, 2000)
        // A tap on it: a click (a spell, a tab).
        gestures.down(0, 50f, 50f, 3000)
        gestures.up(0, 50f, 50f, 3080)
        // A hold on it: a right click there.
        gestures.down(0, 60f, 70f, 4000)
        gestures.onHold(4000 + TouchGestures.HOLD_MS)
        gestures.up(0, 60f, 70f, 4900)
        assertEquals(
            listOf(
                "to 100,200", "press LEFT", "to 130,260", "to 600,560", "to 610,570", "release LEFT",
                "to 50,50", "click LEFT",
                "to 60,70", "to 60,70", "click RIGHT",
            ),
            log.events,
        )
    }

    @Test
    fun aHoldOnAnItemATalentOrAnAbilityIsARightClick() {
        // The bags on the right, the action bars along the bottom.
        log.rightClickArea = { x, y -> x > 700 || y > 540 }
        gestures.down(0, 800f, 300f, 0)
        gestures.onHold(TouchGestures.HOLD_MS)
        gestures.up(0, 800f, 300f, 900)
        gestures.down(0, 300f, 570f, 2000)
        gestures.onHold(2000 + TouchGestures.HOLD_MS)
        gestures.up(0, 300f, 570f, 2900)
        // Elsewhere, the same right click.
        gestures.down(0, 400f, 200f, 4000)
        gestures.onHold(4000 + TouchGestures.HOLD_MS)
        gestures.up(0, 400f, 200f, 4900)
        assertEquals(listOf("to 800,300", "click RIGHT", "to 300,570", "click RIGHT", "to 400,200", "click RIGHT"), log.events)
    }

    @Test
    fun holdingAnItemThenDraggingNeverRightClicksIt() {
        log.rightClickArea = { _, _ -> true }
        gestures.down(0, 800f, 300f, 0)
        gestures.onHold(TouchGestures.HOLD_MS)
        assertTrue(log.events.isEmpty(), "a hold must wait to distinguish use from drag")
        gestures.move(0, 850f, 350f)
        gestures.up(0, 900f, 400f, 1000)
        assertEquals(listOf("to 800,300", "press LEFT", "to 850,350", "to 900,400", "release LEFT"), log.events)
    }

    @Test
    fun cancellingAHoldDoesNotClickOrOpenInventory() {
        gestures.down(0, 800f, 300f, 0)
        gestures.onHold(TouchGestures.HOLD_MS)
        gestures.cancel()
        assertTrue(log.events.isEmpty())
    }

    @Test
    fun offTheSpellbookTheThumbStillWalks() {
        log.dragArea = { x, y -> x < 300 && y < 400 }
        gestures.down(0, 400f, 500f, 0)
        gestures.move(0, 400f, 470f)
        gestures.up(0, 400f, 470f, 2000)
        assertEquals(listOf("playing", "down W", "up W"), log.events)
    }

    @Test
    fun aSecondFingerOnTheSpellbookWhileWalkingIsntADrag() {
        log.dragArea = { x, y -> x < 300 && y < 400 }
        gestures.down(0, 400f, 500f, 0)
        gestures.move(0, 400f, 470f)
        gestures.down(1, 100f, 200f, 1000)
        gestures.up(1, 100f, 200f, 1080)
        gestures.up(0, 400f, 470f, 2000)
        assertEquals(listOf("playing", "down W", "tap at 100,200", "up W"), log.events)
    }

    @Test
    fun onCharacterCreationASwipeTurnsTheCharacterOnEitherHalf() {
        log.characterCreation = true
        // The left half: no walking (W, S, Q, E would go into the name box).
        gestures.down(0, 200f, 400f, 0)
        gestures.move(0, 230f, 400f)
        gestures.move(0, 260f, 380f)
        gestures.up(0, 260f, 380f, 900)
        // The right half: the same, the other way.
        gestures.down(0, 800f, 300f, 2000)
        gestures.move(0, 770f, 300f)
        gestures.up(0, 770f, 300f, 2600)
        assertEquals(
            listOf(
                "to 500,270", "press LEFT", "by 30,0", "by 30,0", "release LEFT",
                "to 500,270", "press LEFT", "by -30,0", "release LEFT",
            ),
            log.events,
        )
    }

    @Test
    fun aLongTurnGoesBackToTheMiddleBeforeTheEdge() {
        log.characterCreation = true
        gestures.down(0, 100f, 300f, 0)
        gestures.move(0, 130f, 300f) // past the swipe's start: 30 so far
        gestures.move(0, 230f, 300f) // 130
        gestures.move(0, 330f, 300f) // 230: past a fifth of the width, back to the middle
        gestures.move(0, 340f, 300f)
        gestures.up(0, 340f, 300f, 900)
        assertEquals(
            listOf(
                "to 500,270", "press LEFT", "by 30,0", "by 100,0", "by 100,0",
                "release LEFT", "to 500,270", "press LEFT", "by 10,0", "release LEFT",
            ),
            log.events,
        )
    }

    @Test
    fun onCharacterCreationTapsStillClickAndHoldsPressNothing() {
        log.characterCreation = true
        gestures.down(0, 100f, 200f, 0)
        gestures.up(0, 101f, 200f, 80)
        gestures.down(0, 600f, 300f, 1000)
        gestures.onHold(1000 + TouchGestures.HOLD_MS)
        gestures.up(0, 600f, 300f, 1900)
        // Two fingers still pinch (the game zooms nothing there, but nothing else happens either).
        assertEquals(listOf("tap at 101,200"), log.events)
    }

    @Test
    fun aLostTouchLetsGoOfTheTurn() {
        log.characterCreation = true
        gestures.down(0, 600f, 300f, 0)
        gestures.move(0, 640f, 300f)
        gestures.cancel()
        assertEquals(listOf("to 500,270", "press LEFT", "by 40,0", "release LEFT"), log.events)
    }
}
