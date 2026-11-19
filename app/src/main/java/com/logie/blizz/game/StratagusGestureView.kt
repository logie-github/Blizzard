// SPDX-License-Identifier: GPL-2.0-or-later

package com.logie.blizz.game

import android.annotation.SuppressLint
import android.app.Activity
import android.os.SystemClock
import android.os.VibrationEffect
import android.os.Vibrator
import android.view.HapticFeedbackConstants
import android.view.InputDevice
import android.view.KeyEvent
import android.view.MotionEvent
import android.view.View
import com.logie.blizz.controls.Bindings
import com.logie.blizz.controls.Button
import com.logie.blizz.controls.ControlsStore
import com.logie.blizz.controls.GestureOutput
import com.logie.blizz.controls.Gestures
import org.libsdl.app.SdlBridge

/**
 * The game's touch controls ([Gestures], the rules in [ControlsStore] for [gameId]) over the native
 * games' screen ([StratagusActivity]), turned into SDL's mouse and keys. SDL's own touch handling
 * never sees the fingers; a mouse on the phone goes to SDL as it is. Back is Escape, twice quickly
 * the app's menu.
 */
@SuppressLint("ViewConstructor")
class StratagusGestureView(
    private val activity: Activity,
    private val gameId: String,
    private val onLeave: () -> Unit,
) : View(activity), GestureOutput {
    private val density = resources.displayMetrics.density
    private val controlsStore = ControlsStore(java.io.File(activity.filesDir, "controls"))
    private var controlsStamp = controlsStore.stamp(gameId)
    private var gestures = makeGestures()
    private val vibrate = GameSettings.vibration(activity)
    private var x = 0f
    private var y = 0f
    private var lastBack = 0L
    private var ticking = false
    private val ticker = object : Runnable {
        override fun run() {
            gestures.tick(SystemClock.uptimeMillis())
            if (gestures.needsTicks()) postDelayed(this, TICK_MS) else ticking = false
        }
    }

    private fun makeGestures() = Gestures(this, density, Bindings.of(gameId, controlsStore.load(gameId)), locate = ::locate)

    /** A point of the view as fractions of the screen, for the rules' areas. */
    private fun locate(px: Float, py: Float): Pair<Float, Float> =
        (px / width.coerceAtLeast(1)).coerceIn(0f, 1f) to (py / height.coerceAtLeast(1)).coerceIn(0f, 1f)

    /** Picks up controls changed in the launcher since: checked as a new touch starts. */
    private fun reloadControlsIfChanged() {
        val now = controlsStore.stamp(gameId)
        if (now == controlsStamp) return
        controlsStamp = now
        gestures.cancel()
        gestures = makeGestures()
    }

    @SuppressLint("ClickableViewAccessibility")
    override fun onTouchEvent(event: MotionEvent): Boolean {
        if (event.isFromSource(InputDevice.SOURCE_MOUSE)) return false
        val index = event.actionIndex
        val id = event.getPointerId(index)
        val now = event.eventTime
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN, MotionEvent.ACTION_POINTER_DOWN -> {
                if (event.actionMasked == MotionEvent.ACTION_DOWN) reloadControlsIfChanged()
                gestures.down(id, event.getX(index), event.getY(index), now)
            }
            MotionEvent.ACTION_MOVE -> gestures.move(
                List(event.pointerCount) { i -> Gestures.Touch(event.getPointerId(i), event.getX(i), event.getY(i)) },
                now,
            )
            MotionEvent.ACTION_UP, MotionEvent.ACTION_POINTER_UP -> gestures.up(id, event.getX(index), event.getY(index), now)
            MotionEvent.ACTION_CANCEL -> gestures.cancel()
        }
        if (!ticking && gestures.needsTicks()) {
            ticking = true
            postDelayed(ticker, TICK_MS)
        }
        return true
    }

    /** Back: Escape; a second Back within [BACK_TWICE_MS] opens the app's menu instead. */
    fun back() {
        val now = SystemClock.uptimeMillis()
        if (now - lastBack <= BACK_TWICE_MS) {
            lastBack = 0
            showMenu()
        } else {
            lastBack = now
            tap(KeyEvent.KEYCODE_ESCAPE)
        }
    }

    // Gestures ---------------------------------------------------------------------------------

    override fun pointerTo(x: Float, y: Float) {
        this.x = x
        this.y = y
        SdlBridge.mouse(0, SdlBridge.ACTION_HOVER_MOVE, x, y)
    }

    override fun click(button: Button) {
        val (bx, by) = x to y
        SdlBridge.mouse(button.bit, SdlBridge.ACTION_DOWN, bx, by)
        postDelayed({ SdlBridge.mouse(0, SdlBridge.ACTION_UP, bx, by) }, CLICK_MS)
    }

    override fun doubleClick(button: Button) {
        click(button)
        postDelayed({ click(button) }, CLICK_MS * 2)
    }

    override fun buttonDown(button: Button) = SdlBridge.mouse(button.bit, SdlBridge.ACTION_DOWN, x, y)

    override fun buttonUp(button: Button) = SdlBridge.mouse(0, SdlBridge.ACTION_UP, x, y)

    override fun wheel(up: Boolean) = SdlBridge.mouse(0, SdlBridge.ACTION_SCROLL, 0f, if (up) 1f else -1f)

    override fun keyDown(key: String) {
        StratagusKeys.code(key)?.let { SdlBridge.keyDown(it) }
    }

    override fun keyUp(key: String) {
        StratagusKeys.code(key)?.let { code ->
            // A modifier is let go after the click it goes with: the click's mouse-up is sent 40 ms later, and the engine reads Shift and Ctrl then.
            if (key == "Shift" || key == "Ctrl" || key == "Alt") postDelayed({ SdlBridge.keyUp(code) }, CLICK_MS * 4) else SdlBridge.keyUp(code)
        }
    }

    override fun openKeyboard() = askText(chat = true)

    override fun showMenu() = GameMenu.show(
        activity,
        gameId,
        onKeyboard = { askText(chat = false) },
        onChat = { askText(chat = true) },
        onTypeKey = { key -> StratagusKeys.code(key)?.let { tap(it) } },
        onLeave = { gestures.cancel(); onLeave() },
        onReport = {
            val dir = java.io.File(activity.intent.getStringExtra(StratagusActivity.EXTRA_DATA) ?: "")
            val log = listOf("stderr.txt", "stdout.txt").joinToString("\n") { name ->
                runCatching { java.io.File(dir, name).readLines().takeLast(40).joinToString("\n", "$name:\n") }.getOrDefault("")
            }
            com.logie.blizz.reports.BugReports.reportTelling(
                activity,
                "${com.logie.blizz.Games.find(gameId)?.fullTitle ?: gameId} in-game report",
                "Sent from the game menu", listOf("Game" to gameId, "Device" to android.os.Build.MODEL), log = log.ifBlank { null },
            )
        },
    )

    override fun feedback() {
        if (!vibrate) return
        if (!performHapticFeedback(HapticFeedbackConstants.LONG_PRESS)) {
            context.getSystemService(Vibrator::class.java)
                ?.vibrate(VibrationEffect.createOneShot(25, VibrationEffect.DEFAULT_AMPLITUDE))
        }
    }

    /** Text into the game: with Enter around it for a chat line, bare for a save's name. */
    private fun askText(chat: Boolean) {
        if (chat) tap(KeyEvent.KEYCODE_ENTER)
        GamePrompt.show(
            activity,
            gameId,
            chat = chat,
            onSend = { text ->
                SdlBridge.text(text)
                if (chat) postDelayed({ tap(KeyEvent.KEYCODE_ENTER) }, KEY_MS * 2)
            },
            onCancel = { if (chat) tap(KeyEvent.KEYCODE_ESCAPE) },
            onBackspace = { tap(KeyEvent.KEYCODE_DEL) },
        )
    }

    private fun tap(code: Int) {
        SdlBridge.keyDown(code)
        postDelayed({ SdlBridge.keyUp(code) }, KEY_MS)
    }

    override fun onDetachedFromWindow() {
        removeCallbacks(ticker)
        super.onDetachedFromWindow()
    }

    companion object {
        private const val CLICK_MS = 40L
        private const val KEY_MS = 50L
        private const val TICK_MS = 30L
        const val BACK_TWICE_MS = 600L

        private val Button.bit: Int
            get() = when (this) {
                Button.LEFT -> SdlBridge.BUTTON_PRIMARY
                Button.RIGHT -> SdlBridge.BUTTON_SECONDARY
            }
    }
}

/** The controls' key names ([com.logie.blizz.controls.KeyCombo.KEYS]) as Android key codes, which SDL reads. */
object StratagusKeys {
    fun code(key: String): Int? = when (key) {
        "Esc" -> KeyEvent.KEYCODE_ESCAPE; "Enter" -> KeyEvent.KEYCODE_ENTER; "Tab" -> KeyEvent.KEYCODE_TAB
        "Space" -> KeyEvent.KEYCODE_SPACE; "Backspace" -> KeyEvent.KEYCODE_DEL
        "Up" -> KeyEvent.KEYCODE_DPAD_UP; "Down" -> KeyEvent.KEYCODE_DPAD_DOWN
        "Left" -> KeyEvent.KEYCODE_DPAD_LEFT; "Right" -> KeyEvent.KEYCODE_DPAD_RIGHT
        "Shift" -> KeyEvent.KEYCODE_SHIFT_LEFT; "Ctrl" -> KeyEvent.KEYCODE_CTRL_LEFT; "Alt" -> KeyEvent.KEYCODE_ALT_LEFT
        "Insert" -> KeyEvent.KEYCODE_INSERT; "Delete" -> KeyEvent.KEYCODE_FORWARD_DEL
        "Home" -> KeyEvent.KEYCODE_MOVE_HOME; "End" -> KeyEvent.KEYCODE_MOVE_END
        "PgUp" -> KeyEvent.KEYCODE_PAGE_UP; "PgDn" -> KeyEvent.KEYCODE_PAGE_DOWN; "PrtSc" -> KeyEvent.KEYCODE_SYSRQ
        "`" -> KeyEvent.KEYCODE_GRAVE; "-" -> KeyEvent.KEYCODE_MINUS; "=" -> KeyEvent.KEYCODE_EQUALS
        "[" -> KeyEvent.KEYCODE_LEFT_BRACKET; "]" -> KeyEvent.KEYCODE_RIGHT_BRACKET; ";" -> KeyEvent.KEYCODE_SEMICOLON
        "'" -> KeyEvent.KEYCODE_APOSTROPHE; "," -> KeyEvent.KEYCODE_COMMA; "." -> KeyEvent.KEYCODE_PERIOD
        "/" -> KeyEvent.KEYCODE_SLASH; "\\" -> KeyEvent.KEYCODE_BACKSLASH
        "NumPlus" -> KeyEvent.KEYCODE_NUMPAD_ADD; "NumMinus" -> KeyEvent.KEYCODE_NUMPAD_SUBTRACT
        "NumStar" -> KeyEvent.KEYCODE_NUMPAD_MULTIPLY; "NumSlash" -> KeyEvent.KEYCODE_NUMPAD_DIVIDE
        "NumEnter" -> KeyEvent.KEYCODE_NUMPAD_ENTER
        else -> when {
            key.length == 1 && key[0] in 'A'..'Z' -> KeyEvent.KEYCODE_A + (key[0] - 'A')
            key.length == 1 && key[0] in '0'..'9' -> KeyEvent.KEYCODE_0 + (key[0] - '0')
            key.length in 2..3 && key[0] == 'F' && key.substring(1).toIntOrNull() in 1..12 ->
                KeyEvent.KEYCODE_F1 + (key.substring(1).toInt() - 1)
            else -> null
        }
    }
}
