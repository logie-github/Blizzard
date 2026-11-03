// SPDX-License-Identifier: GPL-2.0-or-later

package com.logie.blizz.game

import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.ViewGroup
import android.view.WindowManager
import android.widget.FrameLayout
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import com.logie.blizz.R
import org.libsdl.app.SDLActivity
import java.io.File

/**
 * Warcraft I or II, native: the Stratagus engine (libmain.so) on SDL's screen, playing War1gus or
 * Wargus from the data the importer made ([EXTRA_DATA]), with the app's gestures over it
 * ([StratagusGestureView]) in place of SDL's touch. In a process of its own (the manifest), ended
 * when the game is left: each game starts clean.
 */
class StratagusActivity : SDLActivity() {
    private val gameId: String get() = intent.getStringExtra(GestureView.EXTRA_GAME) ?: "warcraft"
    private val dataDir: String get() = intent.getStringExtra(EXTRA_DATA) ?: ""
    private var loading: GameLoading? = null
    private var gestureView: StratagusGestureView? = null

    /** SDL is linked into libmain.so. */
    override fun getLibraries(): Array<String> = arrayOf("main")

    /** Full screen (-F, over the game's own windowed preference); the game's folder is its data and user folder (-d, -u). */
    override fun getArguments(): Array<String> = arguments(dataDir)

    override fun onCreate(savedInstanceState: Bundle?) {
        StratagusStops.catchJavaCrashes(File(dataDir), "$gameId (the game's process)")
        StratagusStops.started(File(dataDir))
        super.onCreate(savedInstanceState)
        if (SDLActivity.mBrokenLibraries) return
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            window.attributes = window.attributes.apply {
                layoutInDisplayCutoutMode = WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES
            }
        }
        WindowCompat.getInsetsController(window, window.decorView).apply {
            hide(WindowInsetsCompat.Type.systemBars())
            systemBarsBehavior = WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        }
        val view = StratagusGestureView(this, gameId, onLeave = { leave() })
        gestureView = view
        addContentView(view, FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        // The loading screen while the engine starts (it has no signal for its first frame).
        runCatching {
            loading = GameLoading(this).also { it.show(R.string.blizz_game_loading) }
            Handler(Looper.getMainLooper()).postDelayed({ loading?.close() }, LOADING_MS)
        }
    }

    /** Back: the game's Escape (cancel an order, close a window); twice quickly, the app's menu. */
    @Deprecated("SDL's activity handles Back this way too")
    override fun onBackPressed() {
        gestureView?.back()
    }

    override fun onDestroy() {
        loading?.close()
        if (isFinishing) StratagusStops.left(File(dataDir))
        super.onDestroy()
    }

    private fun leave() {
        StratagusStops.left(File(dataDir))
        finish()
        // The engine keeps its state in the process: the next game starts in a new one.
        android.os.Process.killProcess(android.os.Process.myPid())
    }

    companion object {
        const val EXTRA_DATA = "com.logie.blizz.STRATAGUS_DATA"
        private const val LOADING_MS = 6000L

        fun arguments(dataDir: String): Array<String> = arrayOf("-F", "-d", dataDir, "-u", dataDir)

        fun intent(context: Context, gameId: String, title: String, dataDir: String): Intent =
            Intent(context, StratagusActivity::class.java)
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                .putExtra(EXTRA_DATA, dataDir)
                .putExtra(GestureView.EXTRA_GAME, gameId)
                .putExtra("title", title)
    }
}
