package com.logie.blizz.selftest

import android.app.Activity
import java.lang.ref.WeakReference

/** The game screen on top right now (Winlator's, or Stratagus's), so the launch test can close it. */
object RunningGame {
    @Volatile private var ref: WeakReference<Activity>? = null

    fun attach(activity: Activity) {
        ref = WeakReference(activity)
    }

    /** A game screen is up and not closing. */
    fun alive(): Boolean = ref?.get()?.let { !it.isFinishing && !it.isDestroyed } == true

    /** Closes the game screen (Winlator's and Stratagus's own shutdown run as it is destroyed). */
    fun finish() {
        val a = ref?.get() ?: return
        a.runOnUiThread { runCatching { a.finish() } }
    }
}
