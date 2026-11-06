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
import com.winlator.xserver.Cursor
import com.winlator.xserver.Pointer
import com.winlator.xserver.XKeycode
import com.winlator.xserver.XServer

/**
 * The games' touch controls ([Gestures]) over Winlator's game screen, in place of its touchpad:
 * Winlator's XServerDisplayActivity puts it on top (patches/winlator/0004). The game's rules (its
 * Controls, [ControlsStore]) say what each gesture does where; this turns that into the X server's
 * pointer, buttons and keys, where Wine passes them to the game. Back is the game's Escape.
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
    /** World of Warcraft's client: it takes its mouse position a frame after the pointer moves, and logs in by itself. */
    private val wow = gameId == "wow-client"
    private val loginName = activity.intent.getStringExtra(EXTRA_LOGIN_NAME)
    private val loginPassword = activity.intent.getStringExtra(EXTRA_LOGIN_PASSWORD)
    private var loginStarted = false
    private val fingerprints = HashMap<Cursor, Long>()
    private val controlsStore = ControlsStore(java.io.File(activity.filesDir, "controls"))
    /** The controls file as it was when [gestures] were made: a game kept running in the background doesn't restart when the controls change. */
    private var controlsStamp = controlsStore.stamp(gameId ?: "")
    private var gestures = makeGestures()

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

    /** Back: the game's Escape; twice in a second, the app's menu (a way in when four fingers don't open it). */
    fun backPressed() {
        val now = SystemClock.uptimeMillis()
        if (now - lastBack < 1000) { lastBack = 0; showMenu() } else { lastBack = now; escape() }
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
            listOf("Game" to gameId, "Device" to android.os.Build.MODEL, "Screen" to "${xServer.screenInfo.width}x${xServer.screenInfo.height}", "Window shown" to windowShown.toString()),
            log = GameLog.snapshot().ifEmpty { null },
        )
    }

    override fun onAttachedToWindow() {
        super.onAttachedToWindow()
        postDelayed(noWindowReport, 90_000)
    }

    /** Back in the game: Escape (cancels an order, closes a menu). */
    fun escape() = tapKey(XKeycode.KEY_ESC)

    /** The game's first window is up: on a touch screen the finger is the pointer, never drawn. */
    fun onGameWindowShown() {
        if (wow) startLogin()
        xServer.renderer.isCursorVisible = false
        windowShown = true
        removeCallbacks(noWindowReport)
        postDelayed(minuteReport, 60_000)
        // Recorded apart from the import's file checks: the program started under Winlator.
        gameId?.takeIf { it != "installer" }?.let { id ->
            val app = activity.applicationContext
            Thread { runCatching { com.logie.blizz.importer.GameImportManager.recordLaunch(app, id, com.logie.blizz.importer.LaunchTest.WINDOW_SHOWN) } }.start()
        }
    }

    // Logging in (World of Warcraft) ----------------------------------------------------------

    /**
     * The login screen is up once the game has shown its cursor a few times running; then, after a moment for its
     * boxes, the saved password is typed and Enter pressed (the account's name is in its box already, from Config.wtf);
     * with no saved password, or after [LOGIN_WAIT_MS] in any case, the keyboard's prompt asks for it.
     */
    private fun startLogin() {
        if (loginStarted) return
        loginStarted = true
        val since = SystemClock.uptimeMillis()
        fun poll(seen: Int) {
            val now = if (cursorHere() != null) seen + 1 else 0
            when {
                now >= LOGIN_CURSOR_SEEN -> postDelayed({ loginNow() }, LOGIN_SETTLE_MS)
                SystemClock.uptimeMillis() - since >= LOGIN_WAIT_MS -> postDelayed({ loginNow() }, LOGIN_SETTLE_MS)
                else -> postDelayed({ poll(now) }, LOGIN_POLL_MS)
            }
        }
        poll(0)
    }

    private fun loginNow() {
        val password = loginPassword
        if (!password.isNullOrEmpty()) type(password, enter = true) else askText(chat = false)
    }

    /** A fingerprint of the game's cursor where the pointer is, or null when there's none to see. */
    private fun cursorHere(): Long? = runCatching {
        xServer.lock(XServer.Lockable.WINDOW_MANAGER, XServer.Lockable.DRAWABLE_MANAGER, XServer.Lockable.INPUT_DEVICE).use {
            var window = xServer.inputDeviceManager.pointWindow
            var cursor: Cursor? = null
            while (window != null && cursor == null) {
                cursor = window.attributes.cursor
                window = window.parent
            }
            cursor?.let { fingerprints.getOrPut(it) { fingerprint(it) } }
        }
    }.getOrNull()

    private fun fingerprint(cursor: Cursor): Long {
        var hash = 1469598103934665603L
        fun add(value: Int) { hash = (hash xor value.toLong()) * 1099511628211L }
        add(cursor.hotSpotX)
        add(cursor.hotSpotY)
        val image = cursor.cursorImage ?: return hash
        add(image.width.toInt())
        add(image.height.toInt())
        val data = image.data?.duplicate() ?: return hash
        data.rewind()
        while (data.remaining() >= 4) add(data.int)
        return hash
    }

    // Gestures ---------------------------------------------------------------------------------

    override fun pointerTo(x: Float, y: Float) {
        val point = XForm.transformPoint(xform, x, y)
        xServer.injectPointerMove(point[0].toInt(), point[1].toInt())
    }

    // The WoW client reads where the pointer is once a frame: a click in the same instant as the move lands on the old spot.
    private val settle: Long get() = if (wow) CURSOR_SETTLE_MS else 0L

    override fun click(button: Button) {
        postDelayed({ xServer.injectPointerButtonPress(button.x) }, settle)
        postDelayed({ xServer.injectPointerButtonRelease(button.x) }, settle + CLICK_MS)
    }

    override fun doubleClick(button: Button) {
        postDelayed({ xServer.injectPointerButtonPress(button.x) }, settle)
        postDelayed({ xServer.injectPointerButtonRelease(button.x) }, settle + CLICK_MS)
        postDelayed({ xServer.injectPointerButtonPress(button.x) }, settle + CLICK_MS * 2)
        postDelayed({ xServer.injectPointerButtonRelease(button.x) }, settle + CLICK_MS * 3)
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

    override fun openKeyboard() = askText(chat = true)

    override fun showMenu() = GameMenu.show(
        activity,
        gameId,
        onKeyboard = { askText(chat = false) },
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
        gestures.cancel()
        onLeave.run()
    }

    override fun onDetachedFromWindow() {
        removeCallbacks(noWindowReport)
        removeCallbacks(minuteReport)
        removeCallbacks(typeNext)
        removeCallbacks(ticker)
        super.onDetachedFromWindow()
    }

    companion object {
        /** The game the launcher started ([com.logie.blizz.Game.id]): the loading screen's and menus' look. */
        const val EXTRA_GAME = "com.logie.blizz.GAME"
        /** Its control profile ([LaunchProfile.id]). */
        const val EXTRA_PROFILE = "com.logie.blizz.PROFILE"

        const val EXTRA_LOGIN_NAME = "com.logie.blizz.LOGIN_NAME"
        const val EXTRA_LOGIN_PASSWORD = "com.logie.blizz.LOGIN_PASSWORD"
        /** How long the WoW client takes to show its cursor for where the pointer went. */
        private const val CURSOR_SETTLE_MS = 90L
        private const val LOGIN_POLL_MS = 250L
        private const val LOGIN_CURSOR_SEEN = 3
        private const val LOGIN_WAIT_MS = 20_000L
        private const val LOGIN_SETTLE_MS = 1500L
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
