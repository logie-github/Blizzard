package com.logie.blizz.controls

import kotlin.math.abs
import kotlin.math.hypot

/** A mouse button. */
enum class Button { LEFT, RIGHT }

/** What the gestures do in the game: the game screen ([com.logie.blizz.game.GestureView]) does it. */
interface GestureOutput {
    /** The mouse pointer to this point of the screen (the view's pixels). */
    fun pointerTo(x: Float, y: Float)
    fun click(button: Button)
    fun doubleClick(button: Button)
    fun buttonDown(button: Button)
    fun buttonUp(button: Button)
    fun wheel(up: Boolean)
    /** A key by its [KeyCombo.KEYS] name, pressed or let go. */
    fun keyDown(key: String)
    fun keyUp(key: String)
    fun openKeyboard()
    fun showMenu()
    /** A short vibration: a hold was recognised. */
    fun feedback()
    /**
     * The button a smart click ([Kind.SMART_CLICK]) at this point of the screen (the view's pixels) is now: the left to select
     * or press, the right to order what is selected. The left unless the game screen knows better.
     */
    fun smartButton(x: Float, y: Float): Button = Button.LEFT
    /** A finger has landed: what [smartButton] goes by may be looked at afresh. */
    fun touched() {}
    /**
     * The game shows something to leave now (a scene, a menu page, a box over the game, a command waiting for its target): a
     * [Kind.KEY_OR_ESCAPE] function is Escape then. Not unless the game screen knows.
     */
    fun leaving(): Boolean = false
}

/**
 * The touch controls: touches become [Trigger]s (tap, double tap, hold, drag, flicks, two-, three-
 * and four-finger taps, two-then-one, pinch, a resting finger with a tap or hold), and each runs
 * the function the game's rules give for where it happened ([Bindings]). A trigger that starts a
 * longer one the rules use (a tap before a double tap, a two-finger tap before two-then-one) waits
 * to see which it is; otherwise it acts at once. In recording mode ([onRecord]) triggers are only
 * reported. Plain Kotlin (no Android types), fed touch events by the game screen and unit-tested.
 *
 * [locate] turns the view's pixels into fractions of the game's screen, for the rules' areas.
 */
class Gestures(
    private val out: GestureOutput,
    density: Float,
    private val bindings: Bindings?,
    private val locate: (Float, Float) -> Pair<Float, Float> = { x, y -> x to y },
    private val onRecord: ((Trigger, Float, Float) -> Unit)? = null,
) {
    companion object {
        const val HOLD_MS = 400L
        const val MULTI_TAP_MS = 500L
        const val REST_MS = 200L
        /** A second tap this soon after the first, on the same spot, makes a double tap. */
        const val DOUBLE_MS = 280L
        /** A one-finger tap this soon after a two-finger tap makes two-then-one. */
        const val SEQUENCE_MS = 600L
        /** A swipe lifted this soon is a flick (when the rules have flicks there); longer, a drag. */
        const val FLICK_MS = 250L
        private val ESCAPE = KeyCombo("Esc")
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
        /** Landed right after a tap there: a double tap (or double tap hold) if it ends that way. */
        var second = false
    }

    private enum class Mode { IDLE, PENDING, HELD, SWIPE, MULTI, REST, DONE }

    private val fingers = LinkedHashMap<Int, Finger>()
    private var mode = Mode.IDLE
    private var maxFingers = 0
    private var firstDownAt = 0L
    private var multiMoved = false
    private var pinching = false
    private var baseCx = 0f
    private var baseCy = 0f
    private var baseSpread = 0f
    private var wheelSteps = 0
    private var actor: Int? = null

    private class Pending(val x: Float, val y: Float, val at: Long)
    /** A tap waiting to see whether a second one follows (only where the rules have a double tap). */
    private var pendingTap: Pending? = null
    /** The last tap, acted on or not: a touch right after it, on the same spot, is a double tap hold. */
    private var lastTap: Pending? = null
    /** The last tap was a smart click that came out as the left click at once: a second tap on it is that same click, not another. */
    private var tapStandsForDouble = false
    /** What the swipe in progress is: a drag, or a drag after a hold. */
    private var swipeTrigger = Trigger.DRAG
    private var pendingTwo: Pending? = null

    /** The hold or drag in progress: what it holds down, to let go. */
    private var holding: GameFunction? = null
    private val heldKeys = linkedSetOf<String>()
    private var dragging = false
    private var swipeFlickable = false

    private fun recording() = onRecord != null

    private fun resolve(trigger: Trigger, x: Float, y: Float): GameFunction? {
        if (recording()) return RECORDED
        val (nx, ny) = locate(x, y)
        return bindings?.resolve(trigger, nx, ny)
    }

    /** Whether the game screen should call [tick] (a hold or a wait to time out). */
    fun needsTicks(): Boolean = fingers.isNotEmpty() || pendingTap != null || pendingTwo != null

    fun down(id: Int, x: Float, y: Float, now: Long) {
        val finger = Finger(x, y, now)
        if (fingers.isEmpty()) {
            out.touched()
            val tap = pendingTap ?: lastTap
            finger.second = tap != null && now - tap.at <= DOUBLE_MS && hypot(x - tap.x, y - tap.y) <= sameSpot
            if (!finger.second) { flushTap(); tapStandsForDouble = false }
            fingers[id] = finger
            mode = Mode.PENDING
            firstDownAt = now
            maxFingers = 1
            return
        }
        flushTap()
        fingers[id] = finger
        maxFingers = maxOf(maxFingers, fingers.size)
        when (mode) {
            Mode.PENDING, Mode.HELD -> {
                release()
                if (now - firstDownAt >= REST_MS && fingers.size == 2) {
                    mode = Mode.REST
                    actor = id
                } else {
                    mode = Mode.MULTI
                    multiMoved = false
                    pinching = false
                    startMulti()
                }
            }
            Mode.SWIPE -> {
                endSwipe()
                mode = Mode.DONE
            }
            Mode.REST -> if (actor == null) actor = id
            Mode.MULTI -> startMulti()
            Mode.IDLE, Mode.DONE -> {}
        }
    }

    data class Touch(val id: Int, val x: Float, val y: Float)

    fun move(id: Int, x: Float, y: Float, now: Long = Long.MAX_VALUE / 2) = move(listOf(Touch(id, x, y)), now)

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
                    if (finger.second) flushTap()
                    val held = mode == Mode.HELD
                    if (held) release()
                    mode = Mode.SWIPE
                    dragging = false
                    // A drag after the hold's buzz is its own gesture where the rules have one (a selection box where a plain drag scrolls).
                    swipeTrigger = if (held && resolve(Trigger.HOLD_DRAG, finger.startX, finger.startY) != null) Trigger.HOLD_DRAG else Trigger.DRAG
                    swipeFlickable = swipeTrigger == Trigger.DRAG && listOf(Trigger.FLICK_UP, Trigger.FLICK_DOWN, Trigger.FLICK_LEFT, Trigger.FLICK_RIGHT)
                        .any { resolve(it, finger.startX, finger.startY) != null }
                    swipe(finger, now)
                }
            }
            Mode.SWIPE -> fingers.values.firstOrNull()?.let { swipe(it, now) }
            Mode.MULTI -> moveMulti()
            Mode.REST, Mode.IDLE, Mode.DONE -> {}
        }
    }

    fun up(id: Int, x: Float, y: Float, now: Long) {
        val finger = fingers.remove(id) ?: return
        finger.x = x
        finger.y = y
        when (mode) {
            Mode.PENDING -> if (fingers.isEmpty()) tapped(finger, now)
            Mode.HELD -> if (fingers.isEmpty()) {
                val trigger = if (finger.second && resolve(Trigger.DOUBLE_TAP_HOLD, finger.startX, finger.startY) != null) Trigger.DOUBLE_TAP_HOLD else Trigger.HOLD
                if (trigger == Trigger.HOLD) flushTap() else pendingTap = null
                if (holding != null) release() else fire(trigger, finger.startX, finger.startY)
            }
            Mode.SWIPE -> if (fingers.isEmpty()) {
                if (!dragging) flick(finger) else if (recording()) onRecord!!(swipeTrigger, finger.startX, finger.startY)
                endSwipe()
            }
            Mode.REST -> if (id == actor) {
                if (!finger.moved) fire(if (finger.held) Trigger.REST_HOLD else Trigger.REST_TAP, finger.startX, finger.startY)
                actor = null
            } else {
                mode = Mode.DONE
            }
            Mode.MULTI -> if (fingers.isEmpty() && !multiMoved && !pinching && now - firstDownAt <= MULTI_TAP_MS) {
                val cx = baseCx
                val cy = baseCy
                when {
                    maxFingers >= 4 -> fire(Trigger.FOUR_FINGER_TAP, cx, cy)
                    maxFingers == 3 -> fire(Trigger.THREE_FINGER_TAP, cx, cy)
                    resolve(Trigger.TWO_THEN_ONE_TAP, cx, cy) != null -> pendingTwo = Pending(cx, cy, now)
                    else -> fire(Trigger.TWO_FINGER_TAP, cx, cy)
                }
            }
            Mode.IDLE, Mode.DONE -> {}
        }
        if (fingers.isEmpty()) {
            release()
            mode = Mode.IDLE
            actor = null
        }
    }

    /** Called every few milliseconds while [needsTicks]: holds, and waits that ran out. */
    fun tick(now: Long) {
        when (mode) {
            Mode.PENDING -> {
                val finger = fingers.values.singleOrNull() ?: return
                if (!finger.moved && now - finger.downAt >= HOLD_MS) {
                    finger.held = true
                    mode = Mode.HELD
                    val trigger = if (finger.second && resolve(Trigger.DOUBLE_TAP_HOLD, finger.startX, finger.startY) != null) Trigger.DOUBLE_TAP_HOLD else Trigger.HOLD
                    if (trigger == Trigger.HOLD && finger.second) flushTap()
                    val function = resolve(trigger, finger.startX, finger.startY)
                    if (function != null) out.feedback()
                    // A key held for as long as the finger stays.
                    if (function?.kind == Kind.KEY_HOLD && !recording()) {
                        holding = function
                        bindings?.keyOf(function)?.let { pressKeys(it) }
                    }
                }
            }
            Mode.REST -> {
                val finger = actor?.let { fingers[it] } ?: return
                if (!finger.held && !finger.moved && now - finger.downAt >= HOLD_MS) {
                    finger.held = true
                    if (resolve(Trigger.REST_HOLD, finger.startX, finger.startY) != null) out.feedback()
                }
            }
            Mode.SWIPE -> fingers.values.firstOrNull()?.let { swipe(it, now) }
            else -> {}
        }
        pendingTap?.let { if (fingers.isEmpty() && now - it.at > DOUBLE_MS) flushTap() }
        pendingTwo?.let {
            if (now - it.at > SEQUENCE_MS) {
                pendingTwo = null
                fire(Trigger.TWO_FINGER_TAP, it.x, it.y)
            }
        }
    }

    /** Lets go of everything (another window took the touch). */
    fun cancel() {
        endSwipe()
        release()
        fingers.clear()
        mode = Mode.IDLE
        actor = null
        pendingTap = null
        pendingTwo = null
        tapStandsForDouble = false
    }

    // Taps -----------------------------------------------------------------------------------

    private fun tapped(finger: Finger, now: Long) {
        val two = pendingTwo
        if (two != null) {
            pendingTwo = null
            if (now - two.at <= SEQUENCE_MS) {
                fire(Trigger.TWO_THEN_ONE_TAP, finger.startX, finger.startY)
                return
            }
            fire(Trigger.TWO_FINGER_TAP, two.x, two.y)
        }
        val here = Pending(finger.startX, finger.startY, now)
        val double = resolve(Trigger.DOUBLE_TAP, finger.startX, finger.startY) != null
        if (finger.second && double && pendingTap != null) {
            pendingTap = null
            lastTap = null
            fire(Trigger.DOUBLE_TAP, finger.startX, finger.startY)
            return
        }
        // The second tap of a double tap whose first already made the click the double tap stands for.
        if (finger.second && tapStandsForDouble) {
            tapStandsForDouble = false
            lastTap = null
            if (recording()) onRecord!!(Trigger.DOUBLE_TAP, finger.startX, finger.startY)
            return
        }
        flushTap()
        lastTap = here
        tapStandsForDouble = false
        // A tap waits only where a double tap could follow it; everywhere else it acts at once.
        if (!double) {
            fire(Trigger.TAP, finger.startX, finger.startY)
            return
        }
        // A smart click that is the left click now is what a double tap there would be: it acts at once, and a second tap adds nothing.
        val smartLeft = !recording() && resolve(Trigger.TAP, finger.startX, finger.startY)?.kind == Kind.SMART_CLICK &&
            resolve(Trigger.DOUBLE_TAP, finger.startX, finger.startY)?.kind == Kind.CLICK_LEFT &&
            out.smartButton(finger.startX, finger.startY) == Button.LEFT
        if (smartLeft) {
            tapStandsForDouble = true
            fire(Trigger.TAP, finger.startX, finger.startY)
        } else pendingTap = here
    }

    private fun flushTap() {
        val tap = pendingTap ?: return
        pendingTap = null
        fire(Trigger.TAP, tap.x, tap.y)
    }

    // Swipes ---------------------------------------------------------------------------------

    private fun swipe(finger: Finger, now: Long) {
        if (!dragging) {
            // Where flicks are used, a swipe isn't a drag until it's lasted a moment.
            if (swipeFlickable && now - finger.downAt < FLICK_MS) return
            dragging = true
            if (recording()) return
            val function = resolve(swipeTrigger, finger.startX, finger.startY) ?: return
            holding = function
            when (function.kind) {
                Kind.DRAG_LEFT -> {
                    out.pointerTo(finger.startX, finger.startY)
                    out.buttonDown(Button.LEFT)
                }
                Kind.KEY_HOLD -> bindings?.keyOf(function)?.let { pressKeys(it) }
                Kind.PAN -> {}
                else -> {
                    holding = null
                    run(function, finger.startX, finger.startY)
                }
            }
        }
        when (holding?.kind) {
            Kind.DRAG_LEFT -> out.pointerTo(finger.x, finger.y)
            Kind.PAN -> pan(finger)
            else -> {}
        }
    }

    private fun flick(finger: Finger) {
        val dx = finger.x - finger.startX
        val dy = finger.y - finger.startY
        val trigger = if (abs(dx) >= abs(dy)) (if (dx > 0) Trigger.FLICK_RIGHT else Trigger.FLICK_LEFT) else (if (dy > 0) Trigger.FLICK_DOWN else Trigger.FLICK_UP)
        fire(trigger, finger.startX, finger.startY)
    }

    private fun endSwipe() {
        if (holding?.kind == Kind.DRAG_LEFT) out.buttonUp(Button.LEFT)
        dragging = false
        release()
    }

    /** The arrow keys toward where the finger went from where it landed, beyond a small dead zone. */
    private fun pan(finger: Finger) {
        val dx = finger.x - finger.startX
        val dy = finger.y - finger.startY
        val ax = abs(dx)
        val ay = abs(dy)
        holdKeys(buildSet {
            if (ax > panDeadZone && ax > ay * 0.4f) add(if (dx > 0) "Right" else "Left")
            if (ay > panDeadZone && ay > ax * 0.4f) add(if (dy > 0) "Down" else "Up")
        })
    }

    // Two fingers or more ----------------------------------------------------------------------

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
        if (fingers.size == 2 && (pinching || (!multiMoved && abs(stretch) > slop * 2))) {
            pinching = true
            val steps = (stretch / pinchStep).toInt()
            while (wheelSteps < steps) { fire(Trigger.PINCH_OUT, cx, cy); wheelSteps++ }
            while (wheelSteps > steps) { fire(Trigger.PINCH_IN, cx, cy); wheelSteps-- }
        } else if (!pinching && hypot(cx - baseCx, cy - baseCy) > slop * 2) {
            multiMoved = true
        }
    }

    // Doing ------------------------------------------------------------------------------------

    private fun fire(trigger: Trigger, x: Float, y: Float) {
        if (recording()) {
            onRecord!!(trigger, x, y)
            return
        }
        resolve(trigger, x, y)?.let { run(it, x, y) }
    }

    private fun run(function: GameFunction, x: Float, y: Float) {
        when (function.kind) {
            Kind.CLICK_LEFT, Kind.DRAG_LEFT -> { out.pointerTo(x, y); out.click(Button.LEFT) }
            Kind.CLICK_RIGHT -> { out.pointerTo(x, y); out.click(Button.RIGHT) }
            Kind.SMART_CLICK -> { out.pointerTo(x, y); out.click(out.smartButton(x, y)) }
            Kind.DOUBLE_LEFT -> { out.pointerTo(x, y); out.doubleClick(Button.LEFT) }
            Kind.SHIFT_LEFT -> withKey("Shift") { out.pointerTo(x, y); out.click(Button.LEFT) }
            Kind.SHIFT_RIGHT -> withKey("Shift") { out.pointerTo(x, y); out.click(Button.RIGHT) }
            Kind.CTRL_LEFT -> withKey("Ctrl") { out.pointerTo(x, y); out.click(Button.LEFT) }
            Kind.WHEEL_UP -> { out.pointerTo(x, y); out.wheel(true) }
            Kind.WHEEL_DOWN -> { out.pointerTo(x, y); out.wheel(false) }
            Kind.KEY, Kind.KEY_HOLD -> bindings?.keyOf(function)?.let { tapKeys(it) }
            Kind.KEY_OR_ESCAPE -> if (out.leaving()) tapKeys(ESCAPE) else bindings?.keyOf(function)?.let { tapKeys(it) }
            Kind.PHONE_KEYBOARD -> out.openKeyboard()
            Kind.APP_MENU -> out.showMenu()
            Kind.PAN, Kind.NONE -> {}
        }
    }

    private fun withKey(key: String, action: () -> Unit) {
        out.keyDown(key)
        action()
        out.keyUp(key)
    }

    private fun modifiers(combo: KeyCombo) = listOfNotNull("Ctrl".takeIf { combo.ctrl }, "Alt".takeIf { combo.alt }, "Shift".takeIf { combo.shift })

    private fun tapKeys(combo: KeyCombo) {
        val mods = modifiers(combo)
        mods.forEach { out.keyDown(it) }
        out.keyDown(combo.key)
        out.keyUp(combo.key)
        mods.reversed().forEach { out.keyUp(it) }
    }

    private fun pressKeys(combo: KeyCombo) = holdKeys(linkedSetOf<String>().apply { addAll(modifiers(combo)); add(combo.key) })

    private fun holdKeys(keys: Set<String>) {
        for (key in heldKeys - keys) out.keyUp(key)
        for (key in keys - heldKeys) out.keyDown(key)
        heldKeys.clear()
        heldKeys += keys
    }

    /** Lets go of a held key or button. */
    private fun release() {
        holdKeys(emptySet())
        holding = null
    }
}

/** What a recording resolves every trigger to, so its waits (double tap, two-then-one) are measured. */
private val RECORDED = GameFunction("recorded", "", Kind.NONE)
