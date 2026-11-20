package com.logie.blizz.wrathpp

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent

/**
 * The app was just updated (a new build installs over the old and ends its realm): Wrath++ is made ready again in the background
 * ([WrathppPrewarm]) when it was the last game played, before the app is even opened.
 */
class WrathppPrewarmReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != Intent.ACTION_MY_PACKAGE_REPLACED) return
        val app = context.applicationContext
        // (what MainActivity sets for the realm's programs, which run through the app's MariaDB wrapper)
        com.logie.blizz.wow.WowCtl.nativeWrapper = java.io.File(app.applicationInfo.nativeLibraryDir, "libblizzmaria.so")
        runCatching { WrathppPrewarm.start(app) }
    }
}
