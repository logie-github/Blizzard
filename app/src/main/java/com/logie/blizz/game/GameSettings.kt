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

    /** A successful import deletes the files that were picked for it ([com.logie.blizz.importer.SourceCleanup]); on unless switched off. */
    fun deleteSources(context: Context): Boolean = prefs(context).getBoolean("delete_sources", true)

    fun setDeleteSources(context: Context, on: Boolean) {
        prefs(context).edit().putBoolean("delete_sources", on).apply()
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

    /** The Fold's inside screen when nothing has been seen yet (a Fold 8's, landscape). */
    val DEFAULT_INNER = 2520 to 2340

    /**
     * The screen the games are made for: the Fold's inside screen, always, wherever Play is pressed. The games start at its
     * shape on the cover screen too (bars at the sides there), so opening the phone needs no change. Its size is learned
     * whenever the launcher is on it (a screen no wider than 3:2), else [DEFAULT_INNER].
     */
    fun gameScreen(context: Context): Pair<Int, Int> {
        val (w, h) = screenSize(context)
        val long = maxOf(w, h)
        val short = minOf(w, h).coerceAtLeast(1)
        val p = prefs(context)
        if (long * 2 <= short * 3 && short >= 1200) {
            if (p.getInt("inner_long", 0) != long || p.getInt("inner_short", 0) != short) p.edit().putInt("inner_long", long).putInt("inner_short", short).apply()
            return long to short
        }
        val savedLong = p.getInt("inner_long", 0)
        val savedShort = p.getInt("inner_short", 0)
        return if (savedLong > 0 && savedShort > 0) savedLong to savedShort else DEFAULT_INNER
    }

    /** The game's screen: its own size, or the inside screen's shape at its lines ([Screen]). */
    fun gameSize(context: Context, profile: LaunchProfile): Pair<Int, Int> {
        profile.fixedSize?.let { return it }
        val (width, height) = gameScreen(context)
        return Screen.resolutionFor(width, height, profile.lines)
    }
}
