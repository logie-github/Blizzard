package com.logie.blizz.game

import android.app.Activity
import android.content.Context
import android.os.Build

/** The games' settings: vibration on a recognised hold, and the screen they're sized for. */
object GameSettings {
    private const val PREFS = "game"

    private fun prefs(context: Context) = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)

    fun vibration(context: Context): Boolean = prefs(context).getBoolean("vibration", true)

    fun setVibration(context: Context, on: Boolean) {
        prefs(context).edit().putBoolean("vibration", on).apply()
    }

    /** The screen the launcher is on (a Fold's inside or outside), in pixels. */
    fun screenSize(context: Context): Pair<Int, Int> =
        if (context is Activity && Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            val bounds = context.windowManager.maximumWindowMetrics.bounds
            bounds.width() to bounds.height()
        } else {
            val metrics = context.resources.displayMetrics
            metrics.widthPixels to metrics.heightPixels
        }

    /** The game's screen: its own size, or the phone's shape at its lines ([Screen]). */
    fun gameSize(context: Context, profile: LaunchProfile): Pair<Int, Int> {
        profile.fixedSize?.let { return it }
        val (width, height) = screenSize(context)
        return Screen.resolutionFor(width, height, profile.lines)
    }
}
