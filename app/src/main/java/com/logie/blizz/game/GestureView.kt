// SPDX-License-Identifier: GPL-2.0-or-later

package com.logie.blizz.game

import android.annotation.SuppressLint
import android.os.Build
import android.os.SystemClock
import android.os.VibrationEffect
import android.os.Vibrator
import android.view.HapticFeedbackConstants
import android.view.InputDevice
import android.view.KeyCharacterMap
import android.view.KeyEvent
import android.view.MotionEvent
import android.view.View
import android.view.ViewGroup
import android.view.WindowManager
import android.widget.FrameLayout
import androidx.appcompat.app.AppCompatActivity
import com.logie.blizz.controls.Bindings
import com.logie.blizz.controls.Button
import com.logie.blizz.controls.ControlsStore
import com.logie.blizz.controls.GestureOutput
import com.logie.blizz.controls.Gestures
import com.logie.blizz.controls.xKeyName
import com.winlator.core.AppUtils
import com.winlator.math.XForm
import com.winlator.renderer.ViewTransformation
import com.winlator.xserver.Pointer
import com.winlator.xserver.XKeycode
import com.winlator.xserver.XServer

/**
 * The games' touch controls ([Gestures]) over Winlator's game screen, in place of its touchpad:
 * Winlator's XServerDisplayActivity puts it on top (patches/winlator/0004). The game's rules (its
 * Controls, [ControlsStore]) say what each gesture does where; this turns that into the X server's
 * pointer, buttons and keys, where Wine passes them to the game. Back opens the app's menu (the game's Escape is in it, and
 * the app's keyboard, [GameKeyboard]); each click is noted for the reports ([GameLog]: where in the X server it went).
 */
@SuppressLint("ViewConstructor")
class GestureView(
    private val activity: AppCompatActivity,
    private val xServer: XServer,
    /** Leaves the game for the launcher. */
    private val onLeave: Runnable,
) : View(activity), GestureOutput {
    private val density = resources.displayMetrics.density
    init { GameLog.start(); com.logie.blizz.selftest.RunningGame.attach(activity) }
    private val gameId = activity.intent.getStringExtra(EXTRA_GAME)
    /**
     * World of Warcraft's client has the World of Warcraft app's own controls ([WowGestureView]: its touch gestures, cursor reading,
     * text prompt and login), over this view; this one only hands them what Winlator tells it.
     */
    private val wow = gameId == "wow-client"
    private var wowView: com.logie.blizz.wowinput.WowGestureView? = null
    private val controlsStore = ControlsStore(java.io.File(activity.filesDir, "controls"))
    /** The controls file as it was when [gestures] were made: a game kept running in the background doesn't restart when the controls change. */
    private var controlsStamp = controlsStore.stamp(gameId ?: "")
    private var gestures = makeGestures()
    /** The app's own keyboard over the game (three fingers, or the menu); its keys go to the X server. */
    private val keyboard = GameKeyboard(activity, { parent as? ViewGroup }) { key, mods -> pressKey(key, mods) }

    private fun makeGestures() = Gestures(this, density, Bindings.of(gameId ?: "", controlsStore.load(gameId ?: "")), locate = ::locate)

    /** Picks up controls changed (or reset) in the launcher since: checked as a new touch starts, when no gesture is running. */
    private fun reloadControlsIfChanged() {
        val now = controlsStore.stamp(gameId ?: "")
        if (now == controlsStamp) return
        controlsStamp = now
        gestures.cancel()
        gestures = makeGestures()
    }
    private val vibrate = GameSettings.vibration(activity)

    /** From the view's pixels to the game screen's. */
    private val xform = XForm.getInstance()
    private val ticker = object : Runnable {
        override fun run() {
            gestures.tick(SystemClock.uptimeMillis())
            if (gestures.needsTicks()) postDelayed(this, TICK_MS) else ticking = false
        }
    }
    private var ticking = false

    /** A point of the view as fractions of the game's screen, for the rules' areas. */
    private fun locate(x: Float, y: Float): Pair<Float, Float> {
        val point = XForm.transformPoint(xform, x, y)
        val w = xServer.screenInfo.width.toFloat().coerceAtLeast(1f)
        val h = xServer.screenInfo.height.toFloat().coerceAtLeast(1f)
        return (point[0] / w).coerceIn(0f, 1f) to (point[1] / h).coerceIn(0f, 1f)
    }

    private fun keepTicking() {
        if (!ticking && gestures.needsTicks()) {
            ticking = true
            postDelayed(ticker, TICK_MS)
        }
    }

    /** Key presses still to send for text from the prompt, a few milliseconds apart. */
    private val typing = ArrayDeque<() -> Unit>()
    private var typingRuns = false
    private val typeNext = object : Runnable {
        override fun run() {
            val next = typing.removeFirstOrNull()
            if (next == null) {
                typingRuns = false
                return
            }
            next()
            postDelayed(this, TYPE_STEP_MS)
        }
    }

    init {
        layoutParams = FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT)
        isClickable = true
        isFocusable = false
        // The game's screen never moves or changes size for a keyboard: text goes through a prompt.
        activity.window.setSoftInputMode(
            WindowManager.LayoutParams.SOFT_INPUT_ADJUST_NOTHING or WindowManager.LayoutParams.SOFT_INPUT_STATE_HIDDEN
        )
        // The whole screen, edge to edge, the camera's edge too.
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            activity.window.attributes = activity.window.attributes.apply {
                layoutInDisplayCutoutMode = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                    WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_ALWAYS
                } else {
                    WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES
                }
            }
        }
        // A game window smaller than the screen is scaled up to fill it (the pointer follows).
        xServer.renderer.isForceWindowsFullscreen = true
        updateXform(AppUtils.getScreenWidth(), AppUtils.getScreenHeight())
    }

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        updateXform(w, h)
    }

    /** Like Winlator's touchpad: the game screen is letterboxed in the view unless stretched to fill it. */
    private fun updateXform(width: Int, height: Int) {
        val view = ViewTransformation()
        view.update(width, height, xServer.screenInfo.width.toInt(), xServer.screenInfo.height.toInt())
        val scale = 1f / view.aspect
        if (!xServer.renderer.isFullscreen) {
            XForm.makeTranslation(xform, -view.viewOffsetX.toFloat(), -view.viewOffsetY.toFloat())
            XForm.scale(xform, scale, scale)
        } else {
            XForm.makeScale(xform, scale, scale)
        }
    }

    /** A mouse connected to the phone: its pointer is drawn again, as on a PC. */
    override fun onGenericMotionEvent(event: MotionEvent): Boolean {
        if (event.isFromSource(InputDevice.SOURCE_MOUSE)) xServer.renderer.isCursorVisible = true
        return false
    }

    @SuppressLint("ClickableViewAccessibility")
    override fun onTouchEvent(event: MotionEvent): Boolean {
        // A mouse or a trackpad goes to the game as it is (Winlator's own handling, under this view).
        if (event.isFromSource(InputDevice.SOURCE_MOUSE)) {
            xServer.renderer.isCursorVisible = true
            return false
        }
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
        keepTicking()
        return true
    }

    private var lastBack = 0L
    private var windowShown = false

    /**
     * Back: the app's menu (the game's Escape key is in it, with the keyboard), or the keyboard away when it is up. As Escape,
     * Back took the person out of Diablo II's screens when they were after the keyboard (9 November 2026). World of Warcraft
     * keeps its own: Escape, and the menu on a second press within a second.
     */
    fun backPressed() {
        if (wow) {
            val now = SystemClock.uptimeMillis()
            if (now - lastBack < 1000) { lastBack = 0; wowView?.showMenu() } else { lastBack = now; wowView?.escape() }
            return
        }
        if (keyboard.shown) keyboard.hide() else showMenu()
    }

    /** No game window after a minute and a half: the log is sent without anyone having to reach the menu. */
    private val noWindowReport = Runnable {
        if (!windowShown) sendReport("didn't start (no window in 90 s)")
    }

    /** A minute into a game: its log, once a day (the same title isn't sent twice in a day), for black screens that nothing reports. */
    private val minuteReport = Runnable { sendReport("log after 60 s") }

    private fun sendReport(what: String) {
        com.logie.blizz.reports.BugReports.report(
            activity.applicationContext, "${com.logie.blizz.Games.find(gameId)?.fullTitle ?: gameId} $what",
            "Sent by the app",
            listOf("Game" to gameId, "Version" to (activity.intent?.getStringExtra(EXTRA_SPLASH) ?: gameId), "Device" to android.os.Build.MODEL, "Screen" to "${xServer.screenInfo.width}x${xServer.screenInfo.height}", "Window shown" to windowShown.toString()),
            log = GameLog.snapshot().ifEmpty { null },
        )
    }

    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        postDelayed(noWindowReport, 90_000)
        // The World of Warcraft client's own controls go over this view.
        if (wow && wowView == null) {
            val view = com.logie.blizz.wowinput.WowGestureView(activity, xServer, onLeave)
            wowView = view
            (parent as? ViewGroup)?.addView(view)
        }
    }

    /** Back in the game: Escape (cancels an order, closes a menu). */
    fun escape() = tapKey(XKeycode.KEY_ESC)

    /** The game's first window is up: on a touch screen the finger is the pointer, never drawn. */
    fun onGameWindowShown() {
        if (wow) wowView?.onGameWindowShown()
        xServer.renderer.isCursorVisible = false
        windowShown = true
        // The strategy games' touch (the Warcraft app's): a tap is the right click, so a menu button or a unit takes a hold. Said once, as the game comes up.
        if (gameId != null && (gameId.startsWith("warcraft3") || gameId == "starcraft")) {
            activity.runOnUiThread { android.widget.Toast.makeText(activity, "Hold to select or press a button · tap to move or attack", android.widget.Toast.LENGTH_LONG).show() }
        }
        removeCallbacks(noWindowReport)
        postDelayed(minuteReport, 60_000)
        // Recorded apart from the import's file checks: the program started under Winlator.
        gameId?.takeIf { it != "installer" }?.let { id ->
            val app = activity.applicationContext
            Thread { runCatching { com.logie.blizz.importer.GameImportManager.recordLaunch(app, id, com.logie.blizz.importer.LaunchTest.WINDOW_SHOWN) } }.start()
        }
    }

    // Gestures ---------------------------------------------------------------------------------

    override fun pointerTo(x: Float, y: Float) {
        val point = XForm.transformPoint(xform, x, y)
        xServer.injectPointerMove(point[0].toInt(), point[1].toInt())
    }

    override fun click(button: Button) {
        GameLog.note(describe("$button click"))
        xServer.injectPointerButtonPress(button.x)
        postDelayed({ xServer.injectPointerButtonRelease(button.x) }, CLICK_MS)
    }

    /**
     * For the reports: where a click goes in the X server (the pointer, the window under it, a grab that takes the events, the
     * focus), so a click that does nothing in a game can be read off the phone's report instead of guessed at.
     */
    private fun describe(what: String): String = runCatching {
        val under = xServer.inputDeviceManager.pointWindow
        val grab = xServer.grabManager.window
        val focus = xServer.windowManager.focusedWindow
        buildString {
            append(what).append(" at X ").append(xServer.pointer.x.toInt()).append(',').append(xServer.pointer.y.toInt())
            append(": under ").append(window(under))
            if (grab != null) append("; grab ").append(window(grab))
            append("; focus ").append(window(focus))
        }
    }.getOrElse { "$what: ${it.javaClass.simpleName}" }

    private fun window(w: com.winlator.xserver.Window?): String {
        if (w == null) return "none"
        val type = if (w.type == com.winlator.xserver.Window.Type.DIALOG) " dialog" else ""
        val io = if (w.isInputOutput) "" else " input-only"
        val press = if (w.hasEventListenerFor(com.winlator.xserver.events.Event.BUTTON_PRESS)) " takes presses" else ""
        return "0x${Integer.toHexString(w.id)} '${w.name}' ${w.className} ${w.width}x${w.height}@${w.rootX},${w.rootY}$type$io$press"
    }

    override fun doubleClick(button: Button) {
        GameLog.note(describe("$button double click"))
        xServer.injectPointerButtonPress(button.x)
        postDelayed({ xServer.injectPointerButtonRelease(button.x) }, CLICK_MS)
        postDelayed({ xServer.injectPointerButtonPress(button.x) }, CLICK_MS * 2)
        postDelayed({ xServer.injectPointerButtonRelease(button.x) }, CLICK_MS * 3)
    }

    override fun buttonDown(button: Button) = xServer.injectPointerButtonPress(button.x)

    override fun buttonUp(button: Button) = xServer.injectPointerButtonRelease(button.x)

    override fun wheel(up: Boolean) {
        val button = if (up) Pointer.Button.BUTTON_SCROLL_UP else Pointer.Button.BUTTON_SCROLL_DOWN
        xServer.injectPointerButtonPress(button)
        xServer.injectPointerButtonRelease(button)
    }

    override fun keyDown(key: String) {
        runCatching { XKeycode.valueOf(xKeyName(key)) }.getOrNull()?.let { xServer.injectKeyPress(it) }
    }

    override fun keyUp(key: String) {
        runCatching { XKeycode.valueOf(xKeyName(key)) }.getOrNull()?.let { xServer.injectKeyRelease(it) }
    }

    /** Three fingers: the app's keyboard, up or away. */
    override fun openKeyboard() = keyboard.toggle()

    /** A key of the app's keyboard: its modifiers down, the key pressed and let go, the modifiers up. */
    private fun pressKey(key: String, mods: Set<String>) {
        val code = runCatching { XKeycode.valueOf(xKeyName(key)) }.getOrNull() ?: return
        val held = mods.mapNotNull { runCatching { XKeycode.valueOf(xKeyName(it)) }.getOrNull() }
        held.forEach { xServer.injectKeyPress(it) }
        xServer.injectKeyPress(code)
        postDelayed({
            xServer.injectKeyRelease(code)
            held.reversed().forEach { xServer.injectKeyRelease(it) }
        }, KEY_MS)
    }

    override fun showMenu() = GameMenu.show(
        activity,
        gameId,
        onKeyboard = { keyboard.show() },
        onType = { askText(chat = false) },
        onEscape = { escape() },
        onChat = { askText(chat = true) },
        onTypeKey = { key -> type(key, enter = false) },
        onLeave = { leave() },
        onReport = {
            com.logie.blizz.reports.BugReports.report(
                activity.applicationContext, "${com.logie.blizz.Games.find(gameId)?.fullTitle ?: gameId} in-game report",
                "Sent from the game menu",
                listOf("Game" to gameId, "Device" to android.os.Build.MODEL, "Screen" to "${xServer.screenInfo.width}x${xServer.screenInfo.height}"),
                log = GameLog.snapshot().ifEmpty { null },
            )
            android.widget.Toast.makeText(activity, "Report sent (it goes out when the phone is online).", android.widget.Toast.LENGTH_LONG).show()
        },
    )

    override fun feedback() {
        if (!vibrate) return
        if (!performHapticFeedback(HapticFeedbackConstants.LONG_PRESS)) {
            val vibrator = context.getSystemService(Vibrator::class.java) ?: return
            vibrator.vibrate(VibrationEffect.createOneShot(25, VibrationEffect.DEFAULT_AMPLITUDE))
        }
    }

    /** A key pressed and let go. */
    private fun tapKey(key: XKeycode) {
        xServer.injectKeyPress(key)
        postDelayed({ xServer.injectKeyRelease(key) }, KEY_MS)
    }

    /** Enter, then the prompt; its text is typed into the game with Enter (a chat line, a cheat code). */
    private fun askText(chat: Boolean) {
        if (chat) tapKey(XKeycode.KEY_ENTER)
        GamePrompt.show(
            activity,
            gameId,
            chat = chat,
            onSend = { text -> type(text, enter = chat) },
            onCancel = { if (chat) tapKey(XKeycode.KEY_ESC) },
            onBackspace = { tapKey(XKeycode.KEY_BKSP) },
        )
    }

    /** Types [text] into the game, a key at a time, then Enter if [enter]. */
    private fun type(text: String, enter: Boolean) {
        val map = KeyCharacterMap.load(KeyCharacterMap.VIRTUAL_KEYBOARD)
        for (c in text) {
            typing += {
                val events = map.getEvents(charArrayOf(c))
                if (events != null) {
                    for (event in events) xServer.keyboard.onKeyEvent(event)
                } else {
                    xServer.keyboard.onKeyEvent(KeyEvent(SystemClock.uptimeMillis(), c.toString(), KeyCharacterMap.VIRTUAL_KEYBOARD, 0))
                }
            }
        }
        if (enter) typing += { tapKey(XKeycode.KEY_ENTER) }
        if (!typingRuns) {
            typingRuns = true
            post(typeNext)
        }
    }

    private fun leave() {
        left = true
        gestures.cancel()
        keyboard.hide()
        onLeave.run()
    }

    /** The person left the game by the menu or the gesture (a game that ends by itself within a minute is reported). */
    private var left = false
    private val attachedAt = android.os.SystemClock.uptimeMillis()

    override fun onDetachedFromWindow() {
        // A game that closed by itself in its first minute (a crash back to the launcher): its log is sent, as a black screen leaves nothing else.
        val seconds = (android.os.SystemClock.uptimeMillis() - attachedAt) / 1000
        if (!left && seconds < 60 && gameId != null && gameId != "installer" && gameId != "wow-client") sendReport("closed itself after $seconds s")
        removeCallbacks(noWindowReport)
        removeCallbacks(minuteReport)
        removeCallbacks(typeNext)
        removeCallbacks(ticker)
        // (their flags too: left set, a view attached again would never type or tick)
        typingRuns = false
        ticking = false
        super.onDetachedFromWindow()
    }

    companion object {
        /** The game the launcher started ([com.logie.blizz.Game.id]): the loading screen's and menus' look. */
        const val EXTRA_GAME = "com.logie.blizz.GAME"
        /** The game whose loading screen shows ([EXTRA_GAME] when absent): the version played of World of Warcraft. */
        const val EXTRA_SPLASH = "com.logie.blizz.SPLASH"
        /** Its control profile ([LaunchProfile.id]). */
        const val EXTRA_PROFILE = "com.logie.blizz.PROFILE"

        const val EXTRA_LOGIN_NAME = "com.logie.blizz.LOGIN_NAME"
        const val EXTRA_LOGIN_PASSWORD = "com.logie.blizz.LOGIN_PASSWORD"
        private const val CLICK_MS = 40L
        private const val TICK_MS = 30L
        private const val KEY_MS = 50L
        private const val TYPE_STEP_MS = 15L

        private val Button.x: Pointer.Button
            get() = when (this) {
                Button.LEFT -> Pointer.Button.BUTTON_LEFT
                Button.RIGHT -> Pointer.Button.BUTTON_RIGHT
            }
    }
}
