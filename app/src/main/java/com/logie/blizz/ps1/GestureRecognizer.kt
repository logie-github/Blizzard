// SPDX-License-Identifier: GPL-3.0-or-later

package com.logie.blizz.ps1

import kotlin.math.abs
import kotlin.math.atan2
import kotlin.math.hypot
import kotlin.math.roundToInt

/** The PlayStation buttons the touch gestures can press. */
enum class PsButton {
    CROSS, CIRCLE, SQUARE, TRIANGLE, START, SELECT, L1, R1,
    DPAD_UP, DPAD_DOWN, DPAD_LEFT, DPAD_RIGHT
}

/** The 8 directions a swipe can hold the D-pad in, counterclockwise from right. */
enum class Direction(val degrees: Float, vararg buttons: PsButton) {
    RIGHT(0f, PsButton.DPAD_RIGHT),
    UP_RIGHT(45f, PsButton.DPAD_UP, PsButton.DPAD_RIGHT),
    UP(90f, PsButton.DPAD_UP),
    UP_LEFT(135f, PsButton.DPAD_UP, PsButton.DPAD_LEFT),
    LEFT(180f, PsButton.DPAD_LEFT),
    DOWN_LEFT(225f, PsButton.DPAD_DOWN, PsButton.DPAD_LEFT),
    DOWN(270f, PsButton.DPAD_DOWN),
    DOWN_RIGHT(315f, PsButton.DPAD_DOWN, PsButton.DPAD_RIGHT);

    val buttons: List<PsButton> = buttons.toList()
}

/** Receives the controller state produced by [GestureRecognizer]. */
interface GestureOutput {
    fun setButton(button: PsButton, pressed: Boolean)

    /** Two-finger tap, then two-finger tap and hold. */
    fun openMenu()

    /** A hold gesture (Circle, L1, R1, Select or the menu) was recognized. Used for haptic feedback. */
    fun onHoldRecognized() {}
}

fun interface Cancellable {
    fun cancel()
}

/** Runs delayed work on the same thread that feeds touch events into the recognizer. */
fun interface GestureScheduler {
    fun schedule(delayMs: Long, action: () -> Unit): Cancellable
}

data class GestureConfig(
    /** How far a finger has to move before a touch counts as a swipe. */
    val touchSlopPx: Float,
    /**
     * A swiping finger's start point is dragged along to stay at most this far behind it, so the
     * D-pad follows the finger's latest movement and turning around responds right away.
     */
    val dpadRadiusPx: Float,
    /** How far two fingers have to move together to count as a two-finger swipe. */
    val twoFingerSwipePx: Float,
    /** How long a finger has to stay still before a touch counts as a hold. */
    val holdTimeoutMs: Long = 280,
    /** Maximum time between lifting the first tap and landing the second one. */
    val doubleTapTimeoutMs: Long = 250,
    /** Same as [doubleTapTimeoutMs], for two-finger taps (fingers rarely land together). */
    val twoFingerDoubleTapTimeoutMs: Long = 350,
    /** How long a tap keeps its button pressed so the game is sure to see it. */
    val pulseMs: Long = 100,
)

/**
 * Turns raw touch points into PlayStation controller input using the Parasite Eve layout.
 * The gestures are Azure Dreams', with Triangle (Parasite Eve's menu) on the double tap:
 *
 * - Swipe anywhere: the D-pad in the swipe's direction, any of 8, for as long as the finger stays
 *   down. Moving the finger back to where the swipe started lets go.
 * - Tap: Cross
 * - Hold: Circle (held for as long as the finger stays down)
 * - While holding Circle, a tap with another finger: Triangle, as many times as the hold lasts
 * - Tap, then tap and hold: R1 on the right half of the screen, L1 on the left (held)
 * - Double tap: Triangle
 * - Two fingers swiping up: Square; right: L1; left: R1; down: Start
 * - Two-finger hold: Select (held for as long as the fingers stay down)
 * - Two-finger tap, then two-finger tap and hold: [GestureOutput.openMenu]
 *
 * Holding Circle and walking at the same time (running, in Parasite Eve): hold, then drag the same
 * finger, or hold one finger and swipe with another. While one finger walks, a second finger can
 * tap for Cross or hold for Circle; while Circle is held, its taps are Triangle instead.
 *
 * Coordinates are in pixels with y pointing down; times are in milliseconds from the same clock
 * that [GestureScheduler] uses.
 */
class GestureRecognizer(
    private val config: GestureConfig,
    private val scheduler: GestureScheduler,
    private val output: GestureOutput,
) {
    /** The width of the touch area, which tells the left half from the right half. */
    var width = 0f

    private enum class State {
        PENDING,
        /** Holding the D-pad. */
        WALK,
        HOLD,
        TWO_FINGER,
        IGNORED,
    }

    private class Touch(
        val id: Int,
        val downX: Float,
        val downY: Float,
        /** This touch landed while an earlier tap was waiting to see if it becomes a double tap. */
        val secondTap: Boolean,
        /** This touch landed while another finger was already walking or holding. */
        val secondary: Boolean,
        /** This touch landed while another finger was holding Circle. */
        val circleHeld: Boolean = false,
    ) {
        var state = State.PENDING
        var x = downX
        var y = downY
        var holdTimer: Cancellable? = null
        var heldButton: PsButton? = null
        var originX = downX
        var originY = downY

        val moved: Float
            get() = hypot(x - downX, y - downY)
    }

    private val touches = LinkedHashMap<Int, Touch>()
    private var walker: Touch? = null

    /** The direction the walking finger holds the D-pad in. */
    private var direction: Direction? = null
    /** Keeps a quick flick's D-pad press down for [GestureConfig.pulseMs] so the game sees it. */
    private var dpadPulse: Cancellable? = null
    private var dpadPulseButtons: List<PsButton> = emptyList()

    /** A finished tap waiting for the double tap window to run out before it becomes Cross. */
    private var pendingTap: Cancellable? = null

    private var twoFingerStart = 0L
    private var twoFingerSecond = false
    private var twoFingerMoved = false
    /** The two-finger touch already did its one thing (a swipe button). */
    private var twoFingerSwiped = false
    private var twoFingerTimer: Cancellable? = null
    private var lastTwoFingerTapUp: Long? = null
    private var selectHeld = false
    /** A two-finger touch moved since the last [movesFinished]. */
    private var twoFingerMovePending = false

    private val pressCount = IntArray(PsButton.entries.size)
    private val pulseTimers = HashSet<Cancellable>()

    fun pointerDown(id: Int, x: Float, y: Float, timeMs: Long) {
        touches[id]?.let { pointerUp(id, it.x, it.y, timeMs) }

        val others = touches.values.toList()

        if (others.size == 1 && others[0].state == State.PENDING && !others[0].secondary) {
            // A second finger joined a touch that hasn't turned into anything yet.
            val first = others[0]
            first.holdTimer?.cancel()
            first.holdTimer = null
            if (first.secondTap) {
                // The single tap before this one was never followed up, so it still counts.
                pulse(PsButton.CROSS)
            }
            first.state = State.TWO_FINGER
            touches[id] = Touch(id, x, y, secondTap = false, secondary = false).apply {
                state = State.TWO_FINGER
            }
            startTwoFinger(timeMs)
            return
        }

        if (others.any { it.state == State.TWO_FINGER }) {
            touches[id] = Touch(id, x, y, secondTap = false, secondary = false).apply {
                state = State.IGNORED
            }
            return
        }

        val secondary = others.any { it.state == State.WALK || it.state == State.HOLD }
        var secondTap = false
        if (!secondary && pendingTap != null) {
            pendingTap?.cancel()
            pendingTap = null
            secondTap = true
        }

        val touch = Touch(id, x, y, secondTap, secondary, circleHeld = secondary && circleHeld())
        touch.holdTimer = scheduler.schedule(config.holdTimeoutMs) { onHold(touch) }
        touches[id] = touch
    }

    fun pointerMove(id: Int, x: Float, y: Float, @Suppress("UNUSED_PARAMETER") timeMs: Long) {
        val touch = touches[id] ?: return
        touch.x = x
        touch.y = y

        when (touch.state) {
            State.PENDING -> if (touch.moved > config.touchSlopPx) {
                touch.holdTimer?.cancel()
                touch.holdTimer = null
                if (touch.secondTap) {
                    // Tap followed by a swipe: the tap still counts as Cross.
                    pulse(PsButton.CROSS)
                }
                // A second finger swiping while another holds walks; while another walks, nothing.
                startWalk(touch)
            }

            State.HOLD -> {
                if (walker == null && touch.moved > config.touchSlopPx) {
                    // Holding a button and then dragging walks too (Circle + D-pad runs).
                    walker = touch
                }
                if (walker === touch) {
                    updateWalk(touch)
                }
            }

            State.WALK -> updateWalk(touch)

            State.TWO_FINGER -> twoFingerMovePending = true

            State.IGNORED -> {}
        }
    }

    fun pointerUp(id: Int, x: Float, y: Float, timeMs: Long) {
        val touch = touches.remove(id) ?: return
        touch.x = x
        touch.y = y
        touch.holdTimer?.cancel()
        touch.holdTimer = null

        when (touch.state) {
            State.PENDING -> when {
                touch.secondary -> pulse(if (touch.circleHeld || circleHeld()) PsButton.TRIANGLE else PsButton.CROSS)
                touch.secondTap -> pulse(PsButton.TRIANGLE)
                else -> {
                    val timer = arrayOfNulls<Cancellable>(1)
                    timer[0] = scheduler.schedule(config.doubleTapTimeoutMs) {
                        if (pendingTap === timer[0]) {
                            pendingTap = null
                            pulse(PsButton.CROSS)
                        }
                    }
                    pendingTap = timer[0]
                }
            }

            State.HOLD -> {
                touch.heldButton?.let { release(it) }
                if (walker === touch) {
                    stopWalk()
                }
            }

            State.WALK -> stopWalk()

            State.TWO_FINGER -> {
                // Lifting either finger ends the chance of a hold.
                twoFingerTimer?.cancel()
                twoFingerTimer = null
                if (touches.values.none { it.state == State.TWO_FINGER }) {
                    endTwoFinger(timeMs)
                }
            }

            State.IGNORED -> {}
        }
    }

    /**
     * Call after the moves of every finger in one touch event. Two-finger gestures are judged on
     * both fingers' new positions together.
     */
    fun movesFinished() {
        if (twoFingerMovePending) {
            twoFingerMovePending = false
            updateTwoFinger()
        }
    }

    /**
     * Forgets touches whose up event never arrived. Call when the first finger of a new gesture
     * lands (no other finger can still be down then). Unlike [cancelAll], a tap waiting to become
     * a double tap is kept.
     */
    fun dropStaleTouches() {
        for (touch in touches.values) {
            touch.holdTimer?.cancel()
            if (touch.state == State.HOLD) {
                touch.heldButton?.let { release(it) }
            }
        }
        touches.clear()
        twoFingerTimer?.cancel()
        twoFingerTimer = null
        if (selectHeld) {
            selectHeld = false
            release(PsButton.SELECT)
        }
        if (walker != null) {
            stopWalk()
        }
    }

    /** Drops every touch and releases every button, e.g. when the view loses its touch stream. */
    fun cancelAll() {
        for (touch in touches.values) {
            touch.holdTimer?.cancel()
        }
        touches.clear()
        walker = null
        direction = null
        dpadPulse?.cancel()
        dpadPulse = null
        dpadPulseButtons = emptyList()

        pendingTap?.cancel()
        pendingTap = null
        twoFingerTimer?.cancel()
        twoFingerTimer = null
        lastTwoFingerTapUp = null
        selectHeld = false
        twoFingerMovePending = false

        for (timer in pulseTimers) {
            timer.cancel()
        }
        pulseTimers.clear()

        for (button in PsButton.entries) {
            if (pressCount[button.ordinal] > 0) {
                pressCount[button.ordinal] = 0
                output.setButton(button, false)
            }
        }
    }

    private fun onHold(touch: Touch) {
        touch.holdTimer = null
        if (touches[touch.id] !== touch || touch.state != State.PENDING) {
            return
        }

        touch.state = State.HOLD
        val button = when {
            !touch.secondTap -> PsButton.CIRCLE
            width > 0f && touch.downX < width / 2 -> PsButton.L1
            else -> PsButton.R1
        }
        touch.heldButton = button
        press(button)
        output.onHoldRecognized()
    }

    /** Another finger is holding Circle (the hold gesture, or holding still while one runs). */
    private fun circleHeld() = touches.values.any { it.state == State.HOLD && it.heldButton == PsButton.CIRCLE }

    private fun startWalk(touch: Touch) {
        if (walker != null) {
            touch.state = State.IGNORED
            return
        }
        touch.state = State.WALK
        walker = touch
        updateWalk(touch)
    }

    private fun stopWalk() {
        walker = null
        setDirection(null)
    }

    private fun startTwoFinger(timeMs: Long) {
        twoFingerStart = timeMs
        twoFingerMoved = false
        twoFingerSwiped = false
        twoFingerMovePending = false
        val lastTapUp = lastTwoFingerTapUp
        twoFingerSecond =
            lastTapUp != null && timeMs - lastTapUp <= config.twoFingerDoubleTapTimeoutMs
        lastTwoFingerTapUp = null

        twoFingerTimer = scheduler.schedule(config.holdTimeoutMs) {
            twoFingerTimer = null
            if (twoFingerSecond) {
                openMenu()
            } else {
                selectHeld = true
                press(PsButton.SELECT)
                output.onHoldRecognized()
            }
        }
    }

    private fun updateTwoFinger() {
        val fingers = touches.values.filter { it.state == State.TWO_FINGER }
        if (fingers.size != 2) {
            return
        }

        val farthest = fingers.maxBy { it.moved }
        val nearest = fingers.minBy { it.moved }
        if (!twoFingerMoved && farthest.moved > config.touchSlopPx * 2) {
            twoFingerMoved = true
            twoFingerTimer?.cancel()
            twoFingerTimer = null
        }
        if (twoFingerSwiped || selectHeld) {
            return
        }

        // One finger holding still while the other swipes: Circle held while walking (running).
        if (farthest.moved > config.touchSlopPx * RUN_START_SLOPS && nearest.moved < config.touchSlopPx) {
            twoFingerTimer?.cancel()
            twoFingerTimer = null
            lastTwoFingerTapUp = null
            nearest.state = State.HOLD
            nearest.heldButton = PsButton.CIRCLE
            press(PsButton.CIRCLE)
            farthest.state = State.PENDING
            startWalk(farthest)
            return
        }

        // Both fingers swiping the same way: Square (up), L1 (right), R1 (left) or Start (down).
        if (nearest.moved < config.touchSlopPx) {
            return
        }
        val dx = fingers.sumOf { (it.x - it.downX).toDouble() }.toFloat() / 2
        val dy = fingers.sumOf { (it.y - it.downY).toDouble() }.toFloat() / 2
        if (hypot(dx, dy) < config.twoFingerSwipePx) {
            return
        }
        val button = when {
            abs(dy) >= abs(dx) * SWIPE_SLOPE && fingers.all { it.y < it.downY } -> PsButton.SQUARE
            abs(dy) >= abs(dx) * SWIPE_SLOPE && fingers.all { it.y > it.downY } -> PsButton.START
            abs(dx) >= abs(dy) * SWIPE_SLOPE && fingers.all { it.x > it.downX } -> PsButton.L1
            abs(dx) >= abs(dy) * SWIPE_SLOPE && fingers.all { it.x < it.downX } -> PsButton.R1
            else -> null
        }
        twoFingerSwiped = true
        button?.let { pulse(it) }
    }

    private fun endTwoFinger(timeMs: Long) {
        twoFingerTimer?.cancel()
        twoFingerTimer = null
        if (selectHeld) {
            selectHeld = false
            release(PsButton.SELECT)
        }

        val wasTap = !twoFingerSecond && !twoFingerMoved && timeMs - twoFingerStart < config.holdTimeoutMs
        lastTwoFingerTapUp = if (wasTap) timeMs else null
    }

    private fun openMenu() {
        // Let go of everything so nothing stays pressed while the menu is open.
        val fingersStillDown = touches.keys.toList()
        cancelAll()
        for (id in fingersStillDown) {
            touches[id] = Touch(id, 0f, 0f, secondTap = false, secondary = false).apply {
                state = State.IGNORED
            }
        }
        output.onHoldRecognized()
        output.openMenu()
    }

    /** Points the D-pad where [touch] moved, dragging its start point along past the radius. */
    private fun updateWalk(touch: Touch) {
        var dx = touch.x - touch.originX
        var dy = touch.y - touch.originY
        var distance = hypot(dx, dy)
        val radius = config.dpadRadiusPx
        if (distance > radius) {
            touch.originX = touch.x - dx / distance * radius
            touch.originY = touch.y - dy / distance * radius
            dx = touch.x - touch.originX
            dy = touch.y - touch.originY
            distance = radius
        }
        setDirection(directionFor(dx, -dy, distance))
    }

    /**
     * The direction of a move of ([dx], [dyUp]), [distance] long: the closest of the 8, or none
     * when the finger is back near where it started. A held direction is kept until the finger
     * clearly turns away from it, so a wobbly finger doesn't flicker between two directions.
     */
    private fun directionFor(dx: Float, dyUp: Float, distance: Float): Direction? {
        if (distance < config.touchSlopPx / 2) {
            return null
        }
        val degrees = ((Math.toDegrees(atan2(dyUp, dx).toDouble()) + 360.0) % 360.0).toFloat()
        direction?.let { current ->
            val off = abs(((degrees - current.degrees + 540f) % 360f) - 180f)
            if (off <= 22.5f + DIRECTION_KEEP_DEGREES) {
                return current
            }
        }
        return Direction.entries[(degrees / 45f).roundToInt() % 8]
    }

    private fun setDirection(next: Direction?) {
        if (next == direction) {
            return
        }
        val held = direction?.buttons.orEmpty()
        val wanted = next?.buttons.orEmpty()
        direction = next
        for (button in held) {
            if (button !in wanted) release(button)
        }
        for (button in wanted) {
            if (button !in held) press(button)
        }
        if (wanted.isNotEmpty()) {
            // Never two directions' quick-flick presses at once.
            endDpadPulse()
            for (button in wanted) press(button)
            dpadPulseButtons = wanted
            dpadPulse = scheduler.schedule(config.pulseMs) { endDpadPulse() }
        }
    }

    private fun endDpadPulse() {
        dpadPulse?.cancel()
        dpadPulse = null
        for (button in dpadPulseButtons) release(button)
        dpadPulseButtons = emptyList()
    }

    private fun pulse(button: PsButton) {
        press(button)
        val timer = arrayOfNulls<Cancellable>(1)
        timer[0] = scheduler.schedule(config.pulseMs) {
            if (pulseTimers.remove(timer[0])) {
                release(button)
            }
        }
        pulseTimers.add(timer[0]!!)
    }

    private fun press(button: PsButton) {
        if (pressCount[button.ordinal]++ == 0) {
            output.setButton(button, true)
        }
    }

    private fun release(button: PsButton) {
        if (pressCount[button.ordinal] > 0 && --pressCount[button.ordinal] == 0) {
            output.setButton(button, false)
        }
    }

    private companion object {
        /** A held direction stays until the finger is this many degrees past its 45° slice. */
        const val DIRECTION_KEEP_DEGREES = 10f

        /** Two-finger swipes have to go mostly one way: within about 34° of it. */
        const val SWIPE_SLOPE = 1.5f

        /**
         * With two fingers down, one has to move this many touch slops (while the other stays
         * within one) to count as holding one and swiping the other. Fingers swiping together
         * both move by then.
         */
        const val RUN_START_SLOPS = 3f
    }
}
