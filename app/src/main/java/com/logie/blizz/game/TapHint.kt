package com.logie.blizz.game

/**
 * When the strategy games' touch is said again. A tap there is the right click (move, attack), which does nothing on a menu
 * button, and the one line shown as the game's window came up is gone before the game has drawn its menu: a person who taps
 * "Single Player" sees nothing happen (the phone, 9 November 2026: "it won't let me click", where the clicks were dead as
 * well). Until the session's first left click (a touch and hold: the person then knows), a tap that made a right click says
 * the line again, at most [max] times and no more often than every [gapMs]. Plain Kotlin, unit-tested.
 */
class TapHint(private val max: Int = 4, private val gapMs: Long = 4000) {
    private var shown = 0
    private var lastAt = 0L
    private var learned = false

    /** A click was made ([right]: the right button) at [now] milliseconds; whether to say the line now. */
    fun onClick(right: Boolean, now: Long): Boolean {
        if (!right) {
            learned = true
            return false
        }
        if (learned || shown >= max || (shown > 0 && now - lastAt < gapMs)) return false
        shown++
        lastAt = now
        return true
    }

    companion object {
        const val TEXT = "Touch and hold to press a button or select · a tap is the right click (move, attack)"
    }
}

/** The strategy games' tap, where it lands. */
object StrategyTap {
    /**
     * The button a click of [asked] becomes: while a dialog box of Windows' own is up (an error message, "already running", a
     * prompt: the session's keeper says so, [Borderless.dialogUp]) the right click of a tap presses nothing, so it is the left.
     * The game's own menus are drawn inside its window and cannot be told from the battlefield: they keep the hold.
     */
    fun button(asked: com.logie.blizz.controls.Button, onDialog: Boolean): com.logie.blizz.controls.Button =
        if (asked == com.logie.blizz.controls.Button.RIGHT && onDialog) com.logie.blizz.controls.Button.LEFT else asked
}
