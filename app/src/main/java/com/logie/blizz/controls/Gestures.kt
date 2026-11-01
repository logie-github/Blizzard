// SPDX-License-Identifier: GPL-2.0-or-later

package com.logie.blizz.controls

import kotlin.math.abs
import kotlin.math.hypot

/** A mouse button the gestures click. */
enum class Button { LEFT, RIGHT }

/** A key the gestures hold. */
enum class Key { LEFT, RIGHT, UP, DOWN, SHIFT }

/**
 * How a game is played by touch. Both are the same gestures (two fingers, three, four, a resting
 * finger, pinch); what a tap, a hold and a swipe do differs:
 *
 * - [RTS] (StarCraft, StarCraft II): a tap right-clicks (move, attack), a hold left-clicks
 *   (select), a swipe pans the map (the arrow keys).
 * - [ARPG] (Diablo, Diablo II): a tap left-clicks (walk, attack, pick up, talk), a hold
 *   right-clicks (the readied spell or skill), a swipe walks: the left button held down, the
 *   pointer following the finger.
 */
enum class Profile { RTS, ARPG }

/** What the gestures do, in the game: the game screen ([com.logie.blizz.game.GestureView]) does it. */
interface GestureOutput {
    /** The mouse pointer to this point of the screen (the view's pixels). */
    fun pointerTo(x: Float, y: Float)
    fun click(button: Button)
    /** A button pressed and held ([buttonUp] lets it go): [Profile.ARPG]'s walking swipe. */
    fun buttonDown(button: Button)
    fun buttonUp(button: Button)
    /** Two clicks in quick succession: the game's double click. */
    fun doubleClick(button: Button)
    /** One notch of the mouse wheel ([up]: away from you, which zooms in). */
    fun wheel(up: Boolean)
    fun keyDown(key: Key)
    fun keyUp(key: Key)
    /** The game's own menu (F10 in StarCraft and StarCraft II, Escape in Diablo and Diablo II). */
    fun gameMenu()
    /** The phone's keyboard, for a chat line or a cheat code (Enter, the text, Enter). */
    fun openKeyboard()
    /** The app's own menu over the game. */
    fun showMenu()
    /** A short vibration: a hold was recognised. */
    fun feedback()
}

/**
 * The touch controls (YeaBwoi's Warcraft app's, with [Profile.ARPG] added for the Diablo games),
 * with nothing drawn on the screen. Plain Kotlin
 * (no Android types), fed touch events by the game screen and unit-tested:
 *
 * - **Swipe** one finger: the map pans the way the finger goes (the arrow keys), for as long as the
 *   finger stays away from where it landed ([Profile.ARPG]: the hero walks after the finger; a
 *   quick flick is the arrow key its way instead, which the menus move with).
 * - **Tap**: right click there (move, attack, gather, set a rally point); on the game's panels the
 *   game screen makes it a left click ([com.logie.blizz.game.GestureView]). [Profile.ARPG]: left click.
 * - **Touch and hold** ([HOLD_MS], a buzz): left click there when the finger lifts (select a unit,
 *   press a button of the game's panel or menus). Two holds in a row on the same spot: a double
 *   click (every unit of that kind on the screen). [Profile.ARPG]: right click (cast).
 * - **A finger resting** while another taps or holds: those are Shift-clicks (queue orders, add to
 *   the selection).
 * - **Two-finger tap**: the game's menu. **Pinch**: zoom (the mouse wheel).
 * - **Three-finger tap**: the phone's keyboard. **Four-finger tap**: the app's menu.
 */
class Gestures(private val out: GestureOutput, density: Float, private val profile: Profile = Profile.RTS) {
    companion object {
        /** A finger that stays this long without moving is a hold (left click). */
        const val HOLD_MS = 400L
        /** Fingers that land and lift within this long without moving are a multi-finger tap. */
        const val MULTI_TAP_MS = 500L
        /** A finger down this long before another lands is resting (Shift), not half of a two-finger tap. */
        const val REST_MS = 200L
        /**
         * [Profile.ARPG]: a swipe whose finger lifts within this long is a flick, the arrow key its
         * way (the menus move with them); one down longer walks.
         */
        const val FLICK_MS = 250L
        /** A second hold this soon after the first one lifted, on the same spot, is a double click. */
        const val DOUBLE_HOLD_MS = 900L
    }

    private val slop = 10f * density
    private val panDeadZone = 14f * density
    private val pinchStep = 48f * density
    private val sameSpot = 40f * density

    private class Finger(val startX: Float, val startY: Float, val downAt: Long) {
        var x = startX
        var y = startY
        var held = false
        var moved = false
    }

    private enum class Mode { IDLE, PENDING, HELD, PAN, MULTI, SHIFT, DONE }

    private enum class Multi { UNDECIDED, MOVED, PINCH }

    private val fingers = LinkedHashMap<Int, Finger>()
    private var mode = Mode.IDLE
    private var maxFingers = 0
    private var firstDownAt = 0L

    private var multi = Multi.UNDECIDED
    private var baseCx = 0f
    private var baseCy = 0f
    private var baseSpread = 0f
    private var wheelSteps = 0
    private val heldKeys = mutableSetOf<Key>()

    /** In Shift mode: the finger tapping or holding (the other one rests). */
    private var actor: Int? = null

    /** The last hold's left click: where and when, for a double click. */
    private var lastHoldAt = Long.MIN_VALUE / 2
    private var lastHoldX = 0f
    private var lastHoldY = 0f

    fun down(id: Int, x: Float, y: Float, now: Long) {
        val finger = Finger(x, y, now)
        if (fingers.isEmpty()) {
            fingers[id] = finger
            mode = Mode.PENDING
            firstDownAt = now
            maxFingers = 1
            return
        }
        fingers[id] = finger
        maxFingers = maxOf(maxFingers, fingers.size)
        when (mode) {
            Mode.PENDING, Mode.HELD -> if (now - firstDownAt >= REST_MS && fingers.size == 2) {
                // The first finger rests: what the second does is Shift-clicked.
                mode = Mode.SHIFT
                actor = id
                holdKeys(setOf(Key.SHIFT))
            } else {
                mode = Mode.MULTI
                multi = Multi.UNDECIDED
                startMulti()
            }
            Mode.SHIFT -> if (actor == null) actor = id
            Mode.PAN -> {
                releaseKeys()
                stopWalking()
                mode = Mode.DONE
            }
            Mode.MULTI -> startMulti()
            Mode.IDLE, Mode.DONE -> {}
        }
    }

    /** A finger where it is now. */
    data class Touch(val id: Int, val x: Float, val y: Float)

    fun move(id: Int, x: Float, y: Float, now: Long = Long.MAX_VALUE / 2) = move(listOf(Touch(id, x, y)), now)

    /** Every finger of one touch event moved: all of them first, then what that means. */
    fun move(touches: List<Touch>, now: Long = Long.MAX_VALUE / 2) {
        for (touch in touches) {
            val finger = fingers[touch.id] ?: continue
            finger.x = touch.x
            finger.y = touch.y
            if (hypot(finger.x - finger.startX, finger.y - finger.startY) > slop) finger.moved = true
        }
        when (mode) {
            Mode.PENDING, Mode.HELD -> {
                val finger = fingers.values.firstOrNull() ?: return
                if (finger.moved) {
                    mode = Mode.PAN
                    pan(finger, now)
                }
            }
            Mode.PAN -> fingers.values.firstOrNull()?.let { pan(it, now) }
            Mode.MULTI -> moveMulti()
            Mode.SHIFT, Mode.IDLE, Mode.DONE -> {}
        }
    }

    fun up(id: Int, x: Float, y: Float, now: Long) {
        val finger = fingers.remove(id) ?: return
        finger.x = x
        finger.y = y
        when (mode) {
            Mode.SHIFT -> if (id == actor) {
                if (!finger.moved) clickFor(finger, now)
                actor = null
            } else {
                // The resting finger lifted: Shift ends.
                releaseKeys()
                mode = Mode.DONE
            }
            Mode.PENDING, Mode.HELD -> if (fingers.isEmpty()) clickFor(finger, now)
            Mode.PAN -> if (fingers.isEmpty()) {
                // [Profile.ARPG]: lifted before it walked: a flick, the arrow key its way.
                if (profile == Profile.ARPG && !walking) flick(finger)
                releaseKeys()
                stopWalking()
            }
            Mode.MULTI -> if (fingers.isNotEmpty()) {
                startMulti()
            } else if (multi == Multi.UNDECIDED && now - firstDownAt <= MULTI_TAP_MS) {
                when {
                    maxFingers >= 4 -> out.showMenu()
                    maxFingers == 3 -> out.openKeyboard()
                    else -> out.gameMenu()
                }
            }
            Mode.IDLE, Mode.DONE -> {}
        }
        if (fingers.isEmpty()) {
            releaseKeys()
            mode = Mode.IDLE
            actor = null
        }
    }

    /** [HOLD_MS] after a finger landed (the game screen calls it then, for every finger). */
    fun onHold(now: Long) {
        when (mode) {
            Mode.PENDING -> {
                val finger = fingers.values.singleOrNull() ?: return
                if (finger.moved || now - finger.downAt < HOLD_MS) return
                finger.held = true
                mode = Mode.HELD
                out.feedback()
            }
            Mode.SHIFT -> {
                val finger = actor?.let { fingers[it] } ?: return
                if (finger.held || finger.moved || now - finger.downAt < HOLD_MS) return
                finger.held = true
                out.feedback()
            }
            else -> {}
        }
    }

    /** The touch was taken away (another window, the system): lets go of everything. */
    fun cancel() {
        releaseKeys()
        stopWalking()
        fingers.clear()
        mode = Mode.IDLE
        actor = null
    }

    /** A lifted finger that didn't move: a tap right-clicks, a hold left-clicks (twice, for a second hold there). */
    private fun clickFor(finger: Finger, now: Long) {
        out.pointerTo(finger.startX, finger.startY)
        if (profile == Profile.ARPG) {
            out.click(if (finger.held) Button.RIGHT else Button.LEFT)
            return
        }
        if (!finger.held) {
            out.click(Button.RIGHT)
            return
        }
        val again = finger.downAt - lastHoldAt <= DOUBLE_HOLD_MS &&
            hypot(finger.startX - lastHoldX, finger.startY - lastHoldY) <= sameSpot
        if (again) {
            out.doubleClick(Button.LEFT)
            lastHoldAt = Long.MIN_VALUE / 2
        } else {
            out.click(Button.LEFT)
            lastHoldAt = now
            lastHoldX = finger.startX
            lastHoldY = finger.startY
        }
    }

    /** [Profile.ARPG]: the left button is held while the hero walks after the finger. */
    private var walking = false

    private fun stopWalking() {
        if (!walking) return
        walking = false
        out.buttonUp(Button.LEFT)
    }

    /** [Profile.ARPG]: a flick's arrow key, pressed and let go, the way the finger went most. */
    private fun flick(finger: Finger) {
        val dx = finger.x - finger.startX
        val dy = finger.y - finger.startY
        val key = if (abs(dx) >= abs(dy)) (if (dx > 0) Key.RIGHT else Key.LEFT) else (if (dy > 0) Key.DOWN else Key.UP)
        out.keyDown(key)
        out.keyUp(key)
    }

    /**
     * The arrow keys toward where the finger went from where it landed, beyond a small dead zone;
     * [Profile.ARPG]: once the finger's been down [FLICK_MS], the hero walks: the left button held
     * where it landed, the pointer following it. (Sooner, it may be a flick: nothing's pressed yet,
     * so a flick over a menu clicks nothing.)
     */
    private fun pan(finger: Finger, now: Long) {
        if (profile == Profile.ARPG) {
            if (!walking) {
                if (now - finger.downAt < FLICK_MS) return
                out.pointerTo(finger.startX, finger.startY)
                out.buttonDown(Button.LEFT)
                walking = true
            }
            out.pointerTo(finger.x, finger.y)
            return
        }
        val dx = finger.x - finger.startX
        val dy = finger.y - finger.startY
        val ax = abs(dx)
        val ay = abs(dy)
        holdKeys(buildSet {
            if (ax > panDeadZone && ax > ay * 0.4f) add(if (dx > 0) Key.RIGHT else Key.LEFT)
            if (ay > panDeadZone && ay > ax * 0.4f) add(if (dy > 0) Key.DOWN else Key.UP)
        })
    }

    // Two fingers or more ----------------------------------------------------------------------

    /** Where the fingers are now is where pinches count from (again, with a finger more or less). */
    private fun startMulti() {
        baseCx = fingers.values.map { it.x }.average().toFloat()
        baseCy = fingers.values.map { it.y }.average().toFloat()
        baseSpread = spread()
        wheelSteps = 0
    }

    private fun spread(): Float {
        if (fingers.size < 2) return 0f
        val (a, b) = fingers.values.take(2)
        return hypot(a.x - b.x, a.y - b.y)
    }

    private fun moveMulti() {
        val cx = fingers.values.map { it.x }.average().toFloat()
        val cy = fingers.values.map { it.y }.average().toFloat()
        val stretch = spread() - baseSpread
        if (fingers.size == 2 && (multi == Multi.PINCH || (multi == Multi.UNDECIDED && abs(stretch) > slop * 2))) {
            multi = Multi.PINCH
            val steps = (stretch / pinchStep).toInt()
            while (wheelSteps < steps) {
                out.wheel(up = true)
                wheelSteps++
            }
            while (wheelSteps > steps) {
                out.wheel(up = false)
                wheelSteps--
            }
        } else if (multi == Multi.UNDECIDED && hypot(cx - baseCx, cy - baseCy) > slop * 2) {
            multi = Multi.MOVED
        }
    }

    private fun holdKeys(keys: Set<Key>) {
        for (key in heldKeys - keys) out.keyUp(key)
        for (key in keys - heldKeys) out.keyDown(key)
        heldKeys.clear()
        heldKeys += keys
    }

    private fun releaseKeys() = holdKeys(emptySet())
}
