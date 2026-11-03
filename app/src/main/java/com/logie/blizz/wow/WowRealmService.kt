package com.logie.blizz.wow

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.IBinder
import android.os.PowerManager
import androidx.core.app.NotificationCompat
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch

/**
 * Keeps the app, and with it the realm's programs, alive while the Wrath realm runs: Android
 * requires a notification for that. The notification says how the realm is and has a Stop button.
 * The service ends itself once the realm is stopped or has failed ([WowRealm.start] starts it).
 * Declared in the manifest like the WoW app's ServerService (no foreground service type).
 */
class WowRealmService : Service() {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
    private var watcher: Job? = null
    private var wakeLock: PowerManager.WakeLock? = null
    private var shown = false
    private var lastStart = 0

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // In the foreground at once, whatever was asked: the app starts this service in the foreground.
        startForeground(NOTIFICATION_ID, notification(WowRealm.status.value))
        shown = true
        lastStart = startId
        if (intent?.action == ACTION_STOP) WowRealm.stop(this)
        if (wakeLock == null) {
            // The realm keeps the world going with the screen off.
            wakeLock = (getSystemService(Context.POWER_SERVICE) as PowerManager)
                .newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "blizz:wow-realm").apply { acquire() }
        }
        if (watcher == null) {
            watcher = scope.launch {
                WowRealm.status.collect { status ->
                    when (status.phase) {
                        WowRealm.Phase.STOPPED, WowRealm.Phase.FAILED -> {
                            stopForeground(STOP_FOREGROUND_REMOVE)
                            shown = false
                            if (status.phase == WowRealm.Phase.FAILED) notifyFailed(status)
                            // (not if the realm was started again meanwhile: that start's own
                            // startService call came after this one's id)
                            stopSelf(lastStart)
                        }
                        else -> if (!shown) {
                            startForeground(NOTIFICATION_ID, notification(status))
                            shown = true
                        } else {
                            manager().notify(NOTIFICATION_ID, notification(status))
                        }
                    }
                }
            }
        }
        return START_NOT_STICKY
    }

    override fun onDestroy() {
        scope.cancel()
        wakeLock?.let { if (it.isHeld) it.release() }
        wakeLock = null
        super.onDestroy()
    }

    private fun manager() = getSystemService(NotificationManager::class.java)

    private fun channel(): String {
        manager().createNotificationChannel(NotificationChannel(CHANNEL, "World of Warcraft realm", NotificationManager.IMPORTANCE_LOW))
        return CHANNEL
    }

    private fun openApp(): PendingIntent? = packageManager.getLaunchIntentForPackage(packageName)?.let {
        PendingIntent.getActivity(this, 0, it.addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP), PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)
    }

    private fun notification(status: WowRealm.Status): Notification {
        val stop = PendingIntent.getService(
            this, 1, Intent(this, WowRealmService::class.java).setAction(ACTION_STOP),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT,
        )
        return NotificationCompat.Builder(this, channel())
            .setSmallIcon(android.R.drawable.stat_sys_download)
            .setContentTitle("World of Warcraft: ${status.realm.displayName}")
            .setContentText(text(status))
            .setOngoing(true)
            .setOnlyAlertOnce(true)
            .setContentIntent(openApp())
            .apply {
                if (status.phase == WowRealm.Phase.STARTING) setProgress(0, 0, true)
                if (status.phase != WowRealm.Phase.STOPPING) addAction(0, "Stop", stop)
            }
            .build()
    }

    private fun notifyFailed(status: WowRealm.Status) {
        manager().notify(
            FAILED_ID,
            NotificationCompat.Builder(this, channel())
                .setSmallIcon(android.R.drawable.stat_sys_warning)
                .setContentTitle("The realm stopped")
                .setContentText(status.error ?: "It couldn't start.")
                .setContentIntent(openApp())
                .setAutoCancel(true)
                .build(),
        )
    }

    companion object {
        private const val CHANNEL = "wow-realm"
        private const val NOTIFICATION_ID = 41
        private const val FAILED_ID = 42
        const val ACTION_STOP = "com.logie.blizz.wow.STOP"

        /** What the realm is doing, in a line. */
        fun text(status: WowRealm.Status): String = when (status.phase) {
            WowRealm.Phase.STOPPED -> "Stopped"
            WowRealm.Phase.STOPPING -> "Saving characters and stopping"
            WowRealm.Phase.FAILED -> status.error ?: "Failed"
            WowRealm.Phase.RUNNING -> "${status.realm.displayName} is running"
            WowRealm.Phase.STARTING -> when (status.step) {
                WowRealm.Step.PREPARING -> "Getting the realm ready"
                WowRealm.Step.CONFIGURING -> "Writing settings"
                WowRealm.Step.DATABASE -> "Starting the database"
                WowRealm.Step.IMPORT -> "Setting up the databases"
                WowRealm.Step.MODULES -> "Matching the world to its modules"
                WowRealm.Step.AUTH -> "Starting the login server"
                WowRealm.Step.WORLD, null -> "Loading the world (this takes minutes)"
            }
        }
    }
}
