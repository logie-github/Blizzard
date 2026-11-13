// SPDX-License-Identifier: GPL-3.0-or-later
// Ported from the World of Warcraft app (com.logie.warcraft): its Wrath game only (the other environments stay in that app).

package com.logie.blizz.wowinput

import android.annotation.SuppressLint
import android.os.Build
import android.os.SystemClock
import android.view.InputDevice
import android.view.KeyCharacterMap
import android.view.KeyEvent
import android.view.MotionEvent
import android.view.View
import android.view.ViewGroup
import android.view.WindowManager
import android.widget.FrameLayout
import androidx.activity.ComponentDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.DefaultLifecycleObserver
import androidx.lifecycle.LifecycleOwner
import com.winlator.core.AppUtils
import com.winlator.math.XForm
import com.winlator.renderer.ViewTransformation
import com.winlator.winhandler.MouseEventFlags
import com.winlator.xserver.Cursor
import com.winlator.xserver.Drawable
import com.winlator.xserver.Pointer
import com.winlator.xserver.XKeycode
import com.winlator.xserver.Window
import com.winlator.xserver.XServer
import java.lang.ref.WeakReference

/**
 * The game's touch controls ([TouchGestures]) and keyboard over Winlator's game screen, in place
 * of its touchpad: Winlator's XServerDisplayActivity puts it on top (patches/winlator/0004). It
 * turns the gestures into the X server's pointer and keys, where Wine passes them to the game,
 * with nothing drawn over the game, and opens the app's menu ([GameMenu]) for four fingers. Taps
 * read the game's own cursor to talk, loot and gather like a PC's right click, and select enemies,
 * which a double tap attacks ([tapAt], [doubleTapAt]).
 *
 * Text goes in through a prompt ([GamePrompt]: a box at the top with the phone's keyboard), which
 * comes up by itself where the game wants text: the password when the game appears, the name at
 * character creation after the login when the account has no characters yet (the launcher says
 * so: [EXTRA_NEW_ACCOUNT]), and the chat (two fingers swiped up press Enter, which opens it).
 * What's sent is typed into the game; the game's screen itself never moves or changes size.
 */
/** The prompt's kinds: the password at the login, a chat line, a name at character creation, any other text. */
enum class PromptKind { PASSWORD, CHAT, NAME, TEXT }

@SuppressLint("ViewConstructor")
class WowGestureView(
    private val activity: AppCompatActivity,
    private val xServer: XServer,
    /** Leaves the game for the launcher. */
    private val onLeave: Runnable,
) : View(activity), GestureOutput {
    private val density = resources.displayMetrics.density
    private val gestures = TouchGestures(this, density)

    init {
        current = WeakReference(this)
    }
    /** From the view's pixels to the game screen's. */
    private val xform = XForm.getInstance()
    /** The game screen's pixels per view pixel. */
    private var scale = 1f
    private var restX = 0f
    private var restY = 0f
    private val hold = Runnable { gestures.onHold(SystemClock.uptimeMillis()) }

    private val cursors = CursorKinds()
    /** Fingerprints of the game's cursors, by cursor (the X server's, for as long as they live). */
    private val fingerprints = java.util.WeakHashMap<Cursor, Long>()
    /** Counts the pointer's moves, so a tap's delayed click can tell another gesture took over. */
    private var pointerMoves = 0
    private var lastTapAt = Long.MIN_VALUE / 2
    private var lastTap: TapResult? = null
    /** Legion (a 7.x client): its window shows well before its login screen. */
    private val legionClient = com.logie.blizz.game.WowPlay.legion
    private val runFolder: java.io.File = com.logie.blizz.wow.WowLayout.of(activity).run
    private val selectionFile = java.io.File(runFolder, "selection")
    private val cutsceneFile = java.io.File(runFolder, "cutscene")
    /**
     * Where the app's add-on last said the spellbook is (patches/azerothcore/0009); it says it again
     * as each character comes into the world.
     */
    private val interfaceFile = java.io.File(runFolder, "interface")
    /**
     * Wrath++'s creator's word on whether it is up and where its lists drag ([CreatorScreen]); only what was written since
     * this screen was made counts (a second's slack for the file system's clock).
     */
    private val creatorFile = java.io.File(com.logie.blizz.wow.WowLayout.of(activity).wrathppClient, "Logs/wrathpp-screen.txt")
    private val startedAt = System.currentTimeMillis() - 1000
    private fun creatorWord(): String? = CreatorScreen.read(creatorFile, startedAt)
    private var lastTapX = 0f
    private var lastTapY = 0f

    /**
     * The game shows its character creation screen ([CharacterCreation], looked at in a small
     * picture of its window every [SCREEN_CHECK_MS]): a finger that moves turns the character.
     */
    private var characterCreation = false
    /** When the picture asked for was asked for (0: none on its way). */
    private var screenAskedAt = 0L
    private val screenCheck = object : Runnable {
        override fun run() {
            checkScreen()
            postDelayed(this, SCREEN_CHECK_MS)
        }
    }

    /** The text prompt on screen, if one is. */
    private var prompt: ComponentDialog? = null
    private var loginShown = false
    /**
     * World of Warcraft: Forever only ([com.logie.blizz.game.GestureView.EXTRA_LAUNCHER]): the Forever Launcher (a
     * Windows GUI) is on screen before the game. While it is up a tap is a plain left click at that point (its buttons),
     * not the 3D game's cursor-reading tap, and no password is typed into it. It flips to the normal WoW gestures and
     * login as soon as the game's own full-screen window appears ([watchForGameWindow]).
     */
    private var inLauncher = activity.intent.getBooleanExtra(com.logie.blizz.game.GestureView.EXTRA_LAUNCHER, false)
    private var launcherNoted = false
    /**
     * World of Warcraft: Forever only ([com.logie.blizz.game.GestureView.EXTRA_CRASH_DIR]): the game's `Errors` folder.
     * A crash file written there since this screen opened ends the session: on the desktop rig the game, having written
     * one, stayed up with its last frame on the screen and took no input, so the phone would show a frozen picture.
     */
    private val crashDir = activity.intent.getStringExtra(com.logie.blizz.game.GestureView.EXTRA_CRASH_DIR)?.let { java.io.File(it) }

    /**
     * Wrath++ run by WarcraftXL only ([com.logie.blizz.game.GestureView.EXTRA_READY_LOG]): its log, which says when the login
     * screen's code is loaded; the password is typed then ([whenGameReady]). [readySince]: a log written before is another launch's.
     */
    private val readyLog = activity.intent.getStringExtra(com.logie.blizz.game.GestureView.EXTRA_READY_LOG)?.let { java.io.File(it) }
    private val readySince = System.currentTimeMillis() - READY_SLACK_MS
    private val openedAt = System.currentTimeMillis()
    private var crashSeen = false
    /** Forever with its launcher: the session began in the launcher's phase, and goes back to it when the game's program ends. */
    private val launcherSession = inLauncher
    /** The session keeper's lines already read for programs that ended ([gameEnded]). */
    private var keeperLinesRead = 0

    /**
     * The game's own program (Wow.exe) ended while the session goes on: the Forever Launcher started it and stays up (the
     * phone, 13 November 2026: "IN GAME", then the launcher back on its PLAY NOW, the game never seen). Read from the
     * session keeper's lines (`program ended: Wow.exe (pid N, code 0x...)`, [com.logie.blizz.forever.ForeverLauncher.gameEnded]).
     * Said in the reports with the exit code and Wine's lines of the moment, and the touch controls go back to the
     * launcher's (taps are clicks on its buttons, nothing typed), so PLAY NOW can be pressed again.
     */
    private fun gameEnded() {
        val file = com.logie.blizz.game.GameLog.keeperLog ?: return
        val lines = runCatching { file.readLines(Charsets.ISO_8859_1) }.getOrNull() ?: return
        if (lines.size < keeperLinesRead) keeperLinesRead = 0
        val fresh = lines.drop(keeperLinesRead)
        keeperLinesRead = lines.size
        val ended = fresh.mapNotNull { com.logie.blizz.forever.ForeverLauncher.gameEnded(it) }.lastOrNull() ?: return
        com.logie.blizz.game.GameLog.note("forever: the game's program ended by itself: ${ended.program}, code ${ended.code}")
        com.logie.blizz.forever.ForeverPlay.reportGameEnded(activity, ended.program, ended.code)
        if (!launcherSession || inLauncher) return
        inLauncher = true
        loginShown = false
        removeCallbacks(screenCheck)
        prompt?.dismiss()
        xServer.renderer.isCursorVisible = true
        android.widget.Toast.makeText(activity, "The game closed by itself (${ended.code}). A report was sent. PLAY NOW starts it again.", android.widget.Toast.LENGTH_LONG).show()
        watchForGameWindow()
    }

    private val crashWatch = object : Runnable {
        override fun run() {
            val dir = crashDir ?: return
            if (crashSeen) return
            runCatching { gameEnded() }
            val crash = runCatching { com.logie.blizz.forever.ForeverCtl.settledCrash(dir, openedAt, System.currentTimeMillis()) }.getOrNull()
            if (crash != null) {
                crashSeen = true
                com.logie.blizz.game.GameLog.note("forever: the game wrote a crash file (${crash.name}); leaving the game")
                onLeave.run()
                return
            }
            postDelayed(this, CRASH_WATCH_MS)
        }
    }
    private val newAccount = activity.intent.getBooleanExtra(EXTRA_NEW_ACCOUNT, false)
    /** The account in the game's login box (Config.wtf), if the launcher knows which. */
    private val account: String? get() = activity.intent.getStringExtra(EXTRA_LOGIN_NAME)
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
        // The game's screen never moves or changes size for a keyboard: changing its size while
        // the game draws blanked it and ended the game on the phone. Text goes through a prompt
        // over it instead (GamePrompt).
        activity.window.setSoftInputMode(
            WindowManager.LayoutParams.SOFT_INPUT_ADJUST_NOTHING or WindowManager.LayoutParams.SOFT_INPUT_STATE_HIDDEN
        )
        // The whole screen, edge to edge, the camera's edge too: the game is made the screen's
        // size (GameSettings), and any edge kept clear would be a black bar.
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            activity.window.attributes = activity.window.attributes.apply {
                layoutInDisplayCutoutMode = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                    WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_ALWAYS
                } else {
                    WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES
                }
            }
        }
        // And if the game's window comes up smaller than the screen anyway, it's scaled up to fill
        // it (the pointer follows the scaling).
        xServer.renderer.isForceWindowsFullscreen = true
        // No server notification over the game: it steps aside while the game is on screen.
        activity.lifecycle.addObserver(object : DefaultLifecycleObserver {
            override fun onStart(owner: LifecycleOwner) {
                // The game's window is looked at again (not while the game is out of sight).
                if (loginShown) {
                    removeCallbacks(screenCheck)
                    postDelayed(screenCheck, SCREEN_CHECK_MS)
                }
                if (crashDir != null && !crashSeen) {
                    removeCallbacks(crashWatch)
                    postDelayed(crashWatch, CRASH_WATCH_MS)
                }
            }

            override fun onStop(owner: LifecycleOwner) {
                removeCallbacks(screenCheck)
                removeCallbacks(crashWatch)
            }
        })
        updateXform(AppUtils.getScreenWidth(), AppUtils.getScreenHeight())
        gestures.setSize(AppUtils.getScreenWidth().toFloat(), AppUtils.getScreenHeight().toFloat())
    }

    override fun onSizeChanged(w: Int, h: Int, oldw: Int, oldh: Int) {
        super.onSizeChanged(w, h, oldw, oldh)
        updateXform(w, h)
        gestures.setSize(w.toFloat(), h.toFloat())
    }

    /** Like Winlator's touchpad: the game screen is letterboxed in the view unless stretched to fill it. */
    private fun updateXform(width: Int, height: Int) {
        val view = ViewTransformation()
        view.update(width, height, xServer.screenInfo.width.toInt(), xServer.screenInfo.height.toInt())
        scale = 1f / view.aspect
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
                gestures.down(id, event.getX(index), event.getY(index), now)
                postDelayed(hold, TouchGestures.HOLD_MS)
            }
            MotionEvent.ACTION_MOVE -> for (i in 0 until event.pointerCount) {
                gestures.move(event.getPointerId(i), event.getX(i), event.getY(i))
            }
            MotionEvent.ACTION_UP, MotionEvent.ACTION_POINTER_UP -> {
                gestures.up(id, event.getX(index), event.getY(index), now)
                if (event.actionMasked == MotionEvent.ACTION_UP) removeCallbacks(hold)
            }
            MotionEvent.ACTION_CANCEL -> {
                removeCallbacks(hold)
                gestures.cancel()
            }
        }
        return true
    }

    /** Back in the game: Escape (closes a window, or opens the game menu). */
    fun escape() = tap(Key.ESCAPE)

    /** The game's first window is up (the loading screen closed): the login screen wants the password. */
    fun onGameWindowShown() {
        // Forever: the first window is the Forever Launcher, not the game. Show the cursor (it is a mouse GUI, and
        // taps are plain clicks while [inLauncher]), do not type a password into it, and wait for the game's own
        // window; this runs again — cleared of [inLauncher] — when that appears, and the real login begins then.
        if (inLauncher) {
            if (!launcherNoted) {
                launcherNoted = true
                com.logie.blizz.game.GameLog.note("forever: the launcher is up; taps are clicks, nothing is typed, until the game's own window")
            }
            xServer.renderer.isCursorVisible = true
            watchForGameWindow()
            return
        }
        // The pointer is there for the game (where taps click, what the cursor offers) but never
        // drawn: on a touch screen the finger is the pointer. The game screen shows it with its
        // first window; this comes right after.
        xServer.renderer.isCursorVisible = false
        if (loginShown) return
        loginShown = true
        postDelayed(screenCheck, SCREEN_CHECK_MS)
        val saved = activity.intent.getStringExtra(EXTRA_LOGIN_PASSWORD)?.let { pw -> account?.let { com.logie.blizz.wow.WowLogin.Login(it, pw) } }
        val login = saved?.takeIf { account != null && it.name.equals(account, ignoreCase = true) }
        // A Legion client shows its window well before its login screen (it loads its data behind
        // it): its own cursor (gxCursor), not the window's first, says the login screen is up. World of Warcraft:
        // Forever's client (a modern one, [crashDir] is set for it only) does the same: on the desktop rig its login
        // screen took 35 s natively, longer than the classic wait (15 s), after which the password went nowhere.
        val legion = legionClient || crashDir != null
        val wait = if (legion) LEGION_LOGIN_WAIT_MS else LOGIN_WAIT_MS
        val shownAt = SystemClock.uptimeMillis()
        // What the login did, for the report a game sends (never the password).
        com.logie.blizz.game.GameLog.note(
            "login: password ${if (activity.intent.getStringExtra(EXTRA_LOGIN_PASSWORD) != null) "given" else "not given"}, account " +
                "${account ?: "none"}, ${if (login != null) "will type it" else "will ask"}, ${if (legion) "late login screen" else "classic"} wait ${wait / 1000} s",
        )
        if (readyLog != null && !legion) {
            // Wrath++: when its runtime says the login screen is loaded, however long that takes (with Project Reforged's
            // archives in it took 15.6 s on the phone, past the classic 15 s after which the password was typed into nothing).
            // Not ready within [READY_WAIT_MS]: asked, never typed blind.
            com.logie.blizz.game.GameLog.note("login: waiting for the runtime's \"stage ready\" (${readyLog.path})")
            whenGameReady(SystemClock.uptimeMillis(), readyLog, timedOut = {
                com.logie.blizz.game.GameLog.note("login: no \"stage ready\" after ${READY_WAIT_MS / 1000} s; asked")
                ask(PromptKind.PASSWORD)
            }) {
                com.logie.blizz.game.GameLog.note("login: game ready after ${(SystemClock.uptimeMillis() - shownAt) / 1000} s")
                if (login != null) {
                    type(login.password, enter = true)
                    if (newAccount) postDelayed({ ask(PromptKind.NAME) }, NAME_PROMPT_DELAY_MS)
                } else ask(PromptKind.PASSWORD)
            }
        } else if (login != null) {
            // (a Legion client not at its login screen when the wait ends: asked, not typed blind
            // into whatever is up, its loading screen or a dialog)
            whenLoginScreen(SystemClock.uptimeMillis(), seen = 0, legion, baseline = null, wait,
                timedOut = if (legion) ({ ask(PromptKind.PASSWORD) }) else null) {
                com.logie.blizz.game.GameLog.note("login: typed after ${(SystemClock.uptimeMillis() - shownAt) / 1000} s")
                type(login.password, enter = true)
                if (newAccount) postDelayed({ ask(PromptKind.NAME) }, NAME_PROMPT_DELAY_MS)
            }
        } else if (legion) {
            whenLoginScreen(SystemClock.uptimeMillis(), seen = 0, legion, baseline = null, wait) { ask(PromptKind.PASSWORD) }
        } else {
            // Asked once the login screen is up (its cursor seen), not while the game is still loading: what's typed before then is lost.
            whenLoginScreen(SystemClock.uptimeMillis(), seen = 0, legion, baseline = null, wait) { ask(PromptKind.PASSWORD) }
        }
        // The login screen only has the plain arrow: what the cursor looks like when it means a click.
        for (delay in ARROW_SAMPLES_MS) postDelayed({ cursors.learnArrow(cursorHere()) }, delay)
    }

    // Gestures ---------------------------------------------------------------------------------

    override fun pointerTo(x: Float, y: Float) {
        pointerMoves++
        val point = XForm.transformPoint(xform, x, y)
        xServer.injectPointerMove(point[0].toInt(), point[1].toInt())
    }

    /**
     * The pointer goes there; once the game has drawn its cursor for that spot, a left click; and
     * when the cursor offered more (talk, attack, loot, gather) and still does after the click, a
     * right click, which does it, as on a PC.
     */
    /** Forever launcher only: a plain left click at the tapped point (its buttons), no cursor-reading or interaction. */
    private fun plainClick(x: Float, y: Float) {
        pointerTo(x, y)
        val moves = pointerMoves
        postDelayed({ if (moves == pointerMoves) click(Button.LEFT) }, CURSOR_SETTLE_MS)
    }

    private val gameWatch = Runnable { watchForGameWindow() }

    /**
     * Forever launcher only: waits for the game's own window (the launcher's PLAY NOW opens it) and hands over to the
     * normal WoW controls and login. The game's window is told by its program, among all the server's windows
     * ([com.logie.blizz.forever.ForeverLauncher.isGameWindow]): never by the focused window's size, which Wine's desktop
     * has too. Polled every [GAME_WATCH_MS] while [inLauncher].
     */
    private fun watchForGameWindow() {
        if (!inLauncher) return
        if (gameProgramWindow()) {
            inLauncher = false
            com.logie.blizz.game.GameLog.note("forever: game window up; WoW controls on")
            onGameWindowShown()
        } else {
            removeCallbacks(gameWatch)
            postDelayed(gameWatch, GAME_WATCH_MS)
        }
    }

    /** Whether one of the server's shown windows is the game's own. */
    private fun gameProgramWindow(): Boolean = runCatching {
        val sw = xServer.screenInfo.width.toInt()
        val sh = xServer.screenInfo.height.toInt()
        xServer.lock(XServer.Lockable.WINDOW_MANAGER).use {
            fun visit(window: Window): Boolean {
                if (!window.isRenderable) return false
                if (com.logie.blizz.forever.ForeverLauncher.isGameWindow(window.className, window.width.toInt(), window.height.toInt(), sw, sh)) return true
                return window.children.any { visit(it) }
            }
            visit(xServer.windowManager.rootWindow)
        }
    }.getOrDefault(false)

    override fun tapAt(x: Float, y: Float) {
        if (inLauncher) return plainClick(x, y)
        val now = SystemClock.uptimeMillis()
        // The same spot tapped again, not quick enough for a double tap: see below.
        val again = now - lastTapAt in TouchGestures.DOUBLE_TAP_MS..AGAIN_MS &&
            Math.hypot((x - lastTapX).toDouble(), (y - lastTapY).toDouble()) <= AGAIN_SLOP_DP * density
        lastTapAt = now
        lastTapX = x
        lastTapY = y
        val tap = TapResult(x, y)
        lastTap = tap
        pointerTo(x, y)
        val moves = pointerMoves
        postDelayed({
            if (moves != pointerMoves) return@postDelayed tap.done(Outcome.PLAIN)
            val before = cursorHere()
            val special = cursors.isSpecial(before)
            val selected = selection()?.first
            click(Button.LEFT)
            when {
                // An enemy: the click selected it; a second tap attacks.
                special && cursors.isEnemy(before) == true -> tap.done(Outcome.ENEMY)
                special && cursors.isEnemy(before) == false -> postDelayed({ interactIfStill(before, moves, tap) }, CURSOR_SETTLE_MS)
                // Not learnt yet: the realm says what the click selected.
                special -> waitForSelection(selected, before, moves, tap, SystemClock.uptimeMillis())
                // Without a cursor to read: the first tap selects, the second talks (or attacks, loots).
                again && !cursors.readable -> postDelayed({
                    if (moves == pointerMoves) click(Button.RIGHT)
                    tap.done(Outcome.INTERACTED)
                }, CURSOR_SETTLE_MS)
                else -> tap.done(Outcome.PLAIN)
            }
        }, CURSOR_SETTLE_MS)
    }

    /**
     * After a tap's click on a special cursor: the realm writes what was selected (an enemy or
     * not) as soon as the game tells it. An enemy stays selected; anything else is used, as a right
     * click does. No word in time: something that isn't selected (a chest, a herb, a mailbox) or
     * that was already selected, which is used too.
     */
    private fun waitForSelection(before: Int?, cursor: Long?, moves: Int, tap: TapResult, since: Long) {
        val now = selection()
        if (now != null && now.first != before) {
            if (cursor != null) cursors.learn(cursor, now.second)
            if (now.second) tap.done(Outcome.ENEMY) else interactIfStill(cursor, moves, tap)
            return
        }
        if (SystemClock.uptimeMillis() - since >= SELECTION_WAIT_MS) return interactIfStill(cursor, moves, tap)
        postDelayed({ waitForSelection(before, cursor, moves, tap, since) }, SELECTION_POLL_MS)
    }

    /** The right click, when the cursor that offered it is still there after the left click. */
    private fun interactIfStill(cursor: Long?, moves: Int, tap: TapResult) {
        if (moves == pointerMoves && cursors.confirms(cursor, cursorHere())) {
            click(Button.RIGHT)
            tap.done(Outcome.INTERACTED)
        } else {
            tap.done(Outcome.PLAIN)
        }
    }

    /**
     * The second tap of a double tap: attack the enemy the first one selected; otherwise jump,
     * keeping the target. While a window the player is using is open (the loot, a talk, a vendor:
     * a jump would close it), or after a first tap that looted, talked or used something, a tap of
     * its own.
     */
    override fun doubleTapAt(x: Float, y: Float) {
        if (inLauncher) return plainClick(x, y)
        // On the action bars, quick taps are presses of the buttons, as many as there are; on the
        // game's windows (the talents, the bags, the character pane: where a hold right-clicks), two
        // clicks, as a mouse's double click (a talent's second spends its point: the app's add-on).
        if (ScreenZones.isActionBars(x, y, width.toFloat(), height.toFloat()) || rightClicksAt(x, y) || windowOpen()) return tapAt(x, y)
        val first = lastTap ?: return jump()
        val far = Math.hypot((first.x - x).toDouble(), (first.y - y).toDouble()) > AGAIN_SLOP_DP * density
        first.whenDone { outcome ->
            when {
                outcome == Outcome.ENEMY && !far -> interactAt(x, y)
                // The first tap already talked, looted or used (a window may be opening): the
                // second is the same tap again, or a tap of its own elsewhere (the loot's item).
                outcome == Outcome.INTERACTED -> { if (far) tapAt(x, y) }
                windowOpen() -> tapAt(x, y)
                else -> jump()
            }
        }
    }

    /**
     * The jump as the second finger lands, when the first tap's click is done and found the open
     * ground, with no window open; anything else (a first tap still at work on an NPC, an enemy, a
     * loot; the action bars, a window) waits for the finger to lift ([doubleTapAt]).
     */
    override fun doubleTapNow(x: Float, y: Float): Boolean {
        val first = lastTap ?: return false
        if (first.result != Outcome.PLAIN) return false
        if (ScreenZones.isActionBars(x, y, width.toFloat(), height.toFloat()) || rightClicksAt(x, y) || windowOpen()) return false
        jump()
        return true
    }

    /** Sticky targeting keeps a ground click from clearing the target; jumping sends only Space. */
    private fun jump() = tap(Key.SPACE)

    /** Whether the add-on says a window the player is using is open (the loot, a talk, a vendor...). */
    private fun windowOpen(): Boolean = InterfaceNote.windowOpen(runCatching { interfaceFile.readText() }.getOrNull())

    /** The realm's latest word on a selection: its count, and whether it was an enemy. */
    private fun selection(): Pair<Int, Boolean>? = runCatching {
        val parts = selectionFile.readText().trim().split(' ')
        parts[0].toInt() to (parts[1] == "1")
    }.getOrNull()

    private enum class Outcome { PLAIN, ENEMY, INTERACTED }

    /** What a tap did, once it's known (its clicks wait for the game and the realm). */
    private class TapResult(val x: Float, val y: Float) {
        private var outcome: Outcome? = null
        /** What it did, once known (null while its clicks wait). */
        val result: Outcome? get() = outcome
        private var waiting: ((Outcome) -> Unit)? = null

        fun done(result: Outcome) {
            outcome = result
            waiting?.invoke(result)
            waiting = null
        }

        fun whenDone(then: (Outcome) -> Unit) {
            val known = outcome
            if (known != null) then(known) else waiting = then
        }
    }

    /** Once the game knows the pointer is there (what's under it), the right click. */
    private fun interactAt(x: Float, y: Float) {
        pointerTo(x, y)
        val moves = pointerMoves
        postDelayed({ if (moves == pointerMoves) click(Button.RIGHT) }, CURSOR_SETTLE_MS)
    }

    /** A fingerprint of the game's cursor where the pointer is, or null when there's none to see. */
    private var nudged = false

    /** The pointer a pixel aside and back on the next call (within the screen): motion for Wine, no place for the game. */
    private fun nudgePointer() = runCatching {
        val x = xServer.pointer.x.toInt()
        val y = xServer.pointer.y.toInt()
        val step = if (nudged) -1 else 1
        val nx = (x + step).coerceIn(0, xServer.screenInfo.width - 1)
        nudged = !nudged
        xServer.injectPointerMove(nx, y)
    }

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
        fun add(value: Int) {
            hash = (hash xor value.toLong()) * 1099511628211L
        }
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

    /** On a window whose icons drag, by what the app's add-on last said ([InterfaceNote]). */
    override fun turnsModel() = CreatorScreen.up(creatorWord()) ?: characterCreation

    /**
     * A small picture of the game's window (Winlator draws it, at most 256 pixels high, on its
     * drawing thread), looked at for the character creation screen.
     */
    private fun checkScreen() {
        val now = SystemClock.uptimeMillis()
        if (screenAskedAt != 0L && now - screenAskedAt < SCREEN_ANSWER_MS) return
        val content = gameWindow()
        if (content == null) {
            characterCreation = false
            return
        }
        screenAskedAt = now
        xServer.renderer.takeWindowScreenshot(content) { picture ->
            val shown = runCatching {
                val pixels = IntArray(picture.width * picture.height)
                picture.getPixels(pixels, 0, picture.width, 0, 0, picture.width, picture.height)
                CharacterCreation.isShown(pixels, picture.width, picture.height)
            }.getOrDefault(false)
            picture.recycle()
            post {
                characterCreation = shown
                screenAskedAt = 0L
            }
        }
    }

    /** What the game draws into: the biggest window there is (the surface in the game's window, when it has one). */
    private fun gameWindow(): Drawable? = runCatching {
        xServer.lock(XServer.Lockable.WINDOW_MANAGER, XServer.Lockable.DRAWABLE_MANAGER).use {
            val root = xServer.windowManager.rootWindow
            var best: Window? = null
            var bestArea = 0
            fun visit(window: Window) {
                if (!window.isRenderable) return
                val area = window.width * window.height
                if (window !== root && !window.isDesktopWindow && window.content != null && area >= bestArea && area > 1) {
                    best = window
                    bestArea = area
                }
                for (child in window.children) visit(child)
            }
            visit(root)
            best?.content
        }
    }.getOrNull()

    override fun dragsAt(x: Float, y: Float): Boolean =
        inAreas(x, y) { InterfaceNote.dragAreas(it) } || inAreas(x, y, creatorWord()) { CreatorScreen.dragAreas(it) }

    /** On the bags, the bank, the character pane, the talents, the action bars or the spellbook. */
    override fun rightClicksAt(x: Float, y: Float): Boolean =
        inAreas(x, y) { InterfaceNote.holdAreas(it) + InterfaceNote.dragAreas(it) }

    /** Whether the screen's [x], [y] is in one of the areas the add-on's last note gives. */
    private fun inAreas(x: Float, y: Float, areasOf: (String?) -> List<InterfaceNote.Area>): Boolean =
        inAreas(x, y, runCatching { interfaceFile.readText() }.getOrNull(), areasOf)

    private fun inAreas(x: Float, y: Float, note: String?, areasOf: (String?) -> List<InterfaceNote.Area>): Boolean {
        val areas = areasOf(note)
        if (areas.isEmpty()) return false
        val point = XForm.transformPoint(xform, x, y)
        val width = xServer.screenInfo.width.toFloat()
        val height = xServer.screenInfo.height.toFloat()
        if (width <= 0f || height <= 0f) return false
        return areas.any { it.contains(point[0] / width, point[1] / height) }
    }

    override fun pointerBy(dx: Float, dy: Float) {
        // Whole pixels, keeping what's left over for the next move.
        restX += dx * scale * CAMERA_SPEED
        restY += dy * scale * CAMERA_SPEED
        val mx = restX.toInt()
        val my = restY.toInt()
        if (mx == 0 && my == 0) return
        restX -= mx
        restY -= my
        if (xServer.isRelativeMouseMovement) {
            xServer.winHandler.mouseEvent(MouseEventFlags.MOVE, mx, my, 0)
        } else {
            xServer.injectPointerMoveDelta(mx, my)
        }
    }

    override fun press(button: Button) {
        pointerMoves++
        restX = 0f
        restY = 0f
        xServer.injectPointerButtonPress(button.x)
    }

    override fun release(button: Button) = xServer.injectPointerButtonRelease(button.x)

    override fun click(button: Button) {
        xServer.injectPointerButtonPress(button.x)
        postDelayed({ xServer.injectPointerButtonRelease(button.x) }, CLICK_MS)
    }

    override fun keyDown(key: Key) = xServer.injectKeyPress(key.x)

    override fun keyUp(key: Key) = xServer.injectKeyRelease(key.x)

    override fun tap(key: Key) {
        // The hold that opens the bags skips a cutscene while one plays (a new character's intro).
        val pressed = if (key == Key.B && cutscenePlaying()) Key.ESCAPE else key
        xServer.injectKeyPress(pressed.x)
        postDelayed({ xServer.injectKeyRelease(pressed.x) }, KEY_MS)
    }

    /** The realm's word on cutscenes (patches/azerothcore/0008). */
    private fun cutscenePlaying(): Boolean =
        Cutscene.isPlaying(runCatching { cutsceneFile.readText() }.getOrNull(), System.currentTimeMillis() / 1000)

    override fun playing() {}

    /** Enter opens the game's chat; the prompt takes the line, and Enter sends it. */
    override fun openChat() {
        if (prompt?.isShowing == true) return
        tap(Key.ENTER)
        ask(PromptKind.CHAT)
    }

    override fun showKeyboard() = ask(PromptKind.TEXT)

    override fun targetNearestEnemy() = tap(Key.TAB)

    override fun showMenu() = com.logie.blizz.game.GameMenu.show(
        activity, "wow-client",
        onKeyboard = { ask(PromptKind.TEXT) },
        // Enter first opens the game's chat box, as the two-finger swipe does.
        onChat = { openChat() },
        onTypeKey = { key -> type(key, enter = false) },
        onLeave = { onLeave.run() },
        onReport = {
            com.logie.blizz.reports.BugReports.report(
                activity.applicationContext, "World of Warcraft in-game report", "Sent from the game menu",
                listOf("Game" to "wow-client", "Device" to Build.MODEL, "Screen" to "${xServer.screenInfo.width}x${xServer.screenInfo.height}"),
                log = com.logie.blizz.game.GameLog.snapshot().ifEmpty { null },
            )
            android.widget.Toast.makeText(activity, "Report sent (it goes out when the phone is online).", android.widget.Toast.LENGTH_LONG).show()
        },
    )

    // Text -------------------------------------------------------------------------------------

    /**
     * [then] once the login screen is up (the game has shown its cursor a few times running; for a
     * [legion] client, one other than the first it showed, the window's before the game had its
     * own: its [baseline]), then a moment more for its boxes, or after [wait] in any case ([timedOut]
     * then, if given): logging in by itself with the saved password (SavedLogin), or asking for it.
     * The account's name is in the box already (Config.wtf).
     */
    private fun whenLoginScreen(since: Long, seen: Int, legion: Boolean, baseline: Long?, wait: Long,
                                timedOut: (() -> Unit)? = null, then: () -> Unit) {
        // Wine gives the X server a program's new cursor only when the pointer moves (read on the X server rig, 13
        // November 2026: the game's cursor set every tick, the server's unchanged until a move). On a touch screen the
        // pointer stays still while the login screen loads, so the game's cursor was never seen: the pointer is moved by
        // a pixel, one way then back, at each look.
        if (legion) nudgePointer()
        val cursor = cursorHere()
        val base = if (legion && baseline == null) cursor else baseline
        val now = if (cursor != null && (!legion || cursor != base)) seen + 1 else 0
        if (now >= LOGIN_CURSOR_SEEN) {
            postDelayed(then, LOGIN_SETTLE_MS)
            return
        }
        if (SystemClock.uptimeMillis() - since >= wait) {
            postDelayed(timedOut ?: then, LOGIN_SETTLE_MS)
            return
        }
        postDelayed({ whenLoginScreen(since, now, legion, base, wait, timedOut, then) }, LOGIN_POLL_MS)
    }

    /** [then] a moment after [log] says the game's interface is up ([com.logie.blizz.wrathpp.WrathppLogs.ready]), [timedOut] after [READY_WAIT_MS]. */
    private fun whenGameReady(since: Long, log: java.io.File, timedOut: () -> Unit, then: () -> Unit) {
        Thread {
            val ready = com.logie.blizz.wrathpp.WrathppLogs.ready(log, readySince)
            post {
                when {
                    ready -> postDelayed(then, LOGIN_SETTLE_MS)
                    SystemClock.uptimeMillis() - since >= READY_WAIT_MS -> timedOut()
                    else -> postDelayed({ whenGameReady(since, log, timedOut, then) }, READY_POLL_MS)
                }
            }
        }.start()
    }

    private fun ask(kind: PromptKind) {
        if (prompt?.isShowing == true) return
        prompt = com.logie.blizz.game.GamePrompt.show(
            activity, "wow-client", chat = kind == PromptKind.CHAT, password = kind == PromptKind.PASSWORD,
            onSend = { text -> send(kind, text, enter = true) },
            // A chat opened for the prompt closes again.
            onCancel = { if (kind == PromptKind.CHAT) tap(Key.ESCAPE) },
            onBackspace = { press(KeyEvent.KEYCODE_DEL) },
        )
    }

    /**
     * Text from the prompt into the game's text box: the password, then Enter (logs in; on a new
     * account, the name prompt follows once the game is at character creation); a chat line, then
     * Enter (sends); a name, as it is; other text as it is, or then Enter ([enter]: the prompt's
     * Send, which sends a chat line or a box's text, or presses Enter alone with nothing typed).
     */
    private fun send(kind: PromptKind, text: String, enter: Boolean) {
        when (kind) {
            PromptKind.PASSWORD -> {
                type(text, enter = true)
                if (newAccount) postDelayed({ ask(PromptKind.NAME) }, NAME_PROMPT_DELAY_MS)
            }
            PromptKind.CHAT -> type(text, enter = true)
            PromptKind.NAME -> {
                // The name in its place: what's in the box (a random name) goes first.
                press(KeyEvent.KEYCODE_MOVE_END)
                repeat(NAME_CLEAR_KEYS) { press(KeyEvent.KEYCODE_DEL) }
                type(text, enter = false)
            }
            PromptKind.TEXT -> type(text, enter = enter)
        }
    }

    /**
     * The password typed in the prompt, kept on the phone to log in by itself next time, once the
     * realm says it's the account's (the one in the login box, or whichever account it opens).
     */
    private fun remember(@Suppress("UNUSED_PARAMETER") password: String) {}

    private val characters: KeyCharacterMap by lazy { KeyCharacterMap.load(KeyCharacterMap.VIRTUAL_KEYBOARD) }

    /** The key presses that make [text] (Winlator's keyboard maps any other character), a few milliseconds apart. */
    private fun type(text: String, enter: Boolean) {
        for (c in text) {
            typing.addLast {
                val events = characters.getEvents(charArrayOf(c))
                if (events != null) {
                    for (event in events) xServer.keyboard.onKeyEvent(event)
                } else {
                    xServer.keyboard.onKeyEvent(KeyEvent(SystemClock.uptimeMillis(), c.toString(), KeyCharacterMap.VIRTUAL_KEYBOARD, 0))
                }
            }
        }
        if (enter) typing.addLast { key(KeyEvent.KEYCODE_ENTER) }
        startTyping()
    }

    /** A key into the game ([KeyEvent] code), in turn with what's being typed. */
    private fun press(code: Int) {
        typing.addLast { key(code) }
        startTyping()
    }

    private fun startTyping() {
        if (!typingRuns) {
            typingRuns = true
            post(typeNext)
        }
    }

    private fun key(code: Int) {
        val time = SystemClock.uptimeMillis()
        xServer.keyboard.onKeyEvent(KeyEvent(time, time, KeyEvent.ACTION_DOWN, code, 0))
        xServer.keyboard.onKeyEvent(KeyEvent(time, time, KeyEvent.ACTION_UP, code, 0))
    }

    override fun onDetachedFromWindow() {
        if (current?.get() === this) current = null
        removeCallbacks(hold)
        removeCallbacks(typeNext)
        removeCallbacks(screenCheck)
        prompt?.dismiss()
        gestures.cancel()
        super.onDetachedFromWindow()
    }

    companion object {
        /** The game screen on show, if one is. */
        @Volatile private var current: WeakReference<WowGestureView>? = null

        /** Leaves the game for the launcher, as its own Leave does (a Wrath Remix Timerunner going home). */
        fun leaveGame(): Boolean {
            val view = current?.get() ?: return false
            view.post { view.onLeave.run() }
            return true
        }

        /** The launcher's word that the account has no characters yet: the game will go to character creation. */
        const val EXTRA_NEW_ACCOUNT = "new_account"
        const val EXTRA_LOGIN_NAME = com.logie.blizz.game.GestureView.EXTRA_LOGIN_NAME
        const val EXTRA_LOGIN_PASSWORD = com.logie.blizz.game.GestureView.EXTRA_LOGIN_PASSWORD
        /** The account the launcher put in the game's login box. */
        const val EXTRA_ACCOUNT = "account"

        private const val CLICK_MS = 30L
        private const val KEY_MS = 60L
        /** Between key presses of text from the prompt. */
        private const val TYPE_STEP_MS = 15L
        /** After the login, until the game is at character creation (a new account goes there). */
        private const val NAME_PROMPT_DELAY_MS = 7000L
        /** Logging in by itself: looking for the login screen's cursor, and how long at most. */
        private const val LOGIN_POLL_MS = 250L
        private const val LOGIN_CURSOR_SEEN = 3
        private const val LOGIN_WAIT_MS = 15000L
        /** A Legion client loads its 40 GB of data before its login screen: under Box64, minutes. */
        private const val LEGION_LOGIN_WAIT_MS = 180_000L
        private const val LOGIN_SETTLE_MS = 1500L
        /** Wrath++: how often its runtime's log is read for "stage ready", how long at most, and the clock's leeway for its date. */
        private const val READY_POLL_MS = 500L
        private const val READY_WAIT_MS = 180_000L
        private const val READY_SLACK_MS = 5_000L
        /** How long the game takes to show its cursor for where the pointer went (a frame or two at a phone's rate). */
        private const val CURSOR_SETTLE_MS = 90L
        /** Forever: how often, while the launcher is up, to look for the game's own window and hand over to WoW controls. */
        private const val GAME_WATCH_MS = 400L
        private const val CRASH_WATCH_MS = 2000L
        /** A second tap on the same spot within this talks to what the first one selected (without a cursor to read). */
        private const val AGAIN_MS = 1500L
        /** How long a tap waits for the realm to say what it selected, and how often it looks. */
        private const val SELECTION_WAIT_MS = 400L
        private const val SELECTION_POLL_MS = 25L
        private const val AGAIN_SLOP_DP = 40f
        /** When the login screen's cursor is looked at, after the game appears. */
        private val ARROW_SAMPLES_MS = longArrayOf(4000L, 8000L, 12000L)
        /** The login screen takes a moment to draw after the window appears. */
        private const val LOGIN_KEYBOARD_DELAY_MS = 1500L

        /** Backspaces that empty the name box before a name goes in (it takes up to 12 letters). */
        private const val NAME_CLEAR_KEYS = 16
        /** The camera turns a little faster than the thumb moves. */
        private const val CAMERA_SPEED = 1.5f
        /** How often the game's window is looked at for the character creation screen. */
        private const val SCREEN_CHECK_MS = 1000L
        /** A picture asked for that hasn't come by then (the drawing paused) is asked for again. */
        private const val SCREEN_ANSWER_MS = 5000L

        private val Button.x: Pointer.Button
            get() = when (this) {
                Button.LEFT -> Pointer.Button.BUTTON_LEFT
                Button.RIGHT -> Pointer.Button.BUTTON_RIGHT
                Button.WHEEL_UP -> Pointer.Button.BUTTON_SCROLL_UP
                Button.WHEEL_DOWN -> Pointer.Button.BUTTON_SCROLL_DOWN
            }

        private val Key.x: XKeycode
            get() = when (this) {
                Key.W -> XKeycode.KEY_W
                Key.S -> XKeycode.KEY_S
                Key.Q -> XKeycode.KEY_Q
                Key.E -> XKeycode.KEY_E
                Key.B -> XKeycode.KEY_B
                Key.M -> XKeycode.KEY_M
                Key.SPACE -> XKeycode.KEY_SPACE
                Key.ESCAPE -> XKeycode.KEY_ESC
                Key.ENTER -> XKeycode.KEY_ENTER
                Key.TAB -> XKeycode.KEY_TAB
            }
    }
}
