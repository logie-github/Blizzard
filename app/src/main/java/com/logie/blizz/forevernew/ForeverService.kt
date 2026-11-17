package com.logie.blizz.forevernew

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
import androidx.core.content.ContextCompat
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch

/**
 * Keeps the app, and with it Forever's programs (the database, the login server, the world server, the map tools), alive while
 * Forever installs and runs, as the other realms do ([com.logie.blizz.wow.WowRealmService]); Android requires a notification
 * for that. Forever had none: its programs are the app's children, and Android freezes or ends them while the app is out of
 * sight (the phone, 16 and 17 November 2026: the world server "hangs for 60029 ms, forcing a crash!" after hours of map
 * building with the app away, and the world server of Wrath++'s realm, which had a service too, was ended from outside by
 * signal 35). Declared in the manifest like WowRealmService (no foreground service type). The service ends itself once
 * Forever is stopped, has failed or waits for the person ([keepAlive]).
 */
class ForeverService : Service() {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
    private var wakeLock: PowerManager.WakeLock? = null
    private var lastStart = 0

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(NOTIFICATION_ID, notification(ForeverPlay.status.value))
        lastStart = startId
        if (intent?.action == ACTION_STOP) ForeverPlay.stop()
        if (wakeLock == null) {
            // The programs go on with the screen off.
            wakeLock = (getSystemService(Context.POWER_SERVICE) as PowerManager)
                .newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "blizz:forever").apply { acquire() }
            scope.launch {
                ForeverPlay.status.collect { status ->
                    if (!keepAlive(status)) {
                        stopForeground(STOP_FOREGROUND_REMOVE)
                        // (not if it was started again meanwhile: that start's own call came after this one's id)
                        stopSelf(lastStart)
                    } else manager().notify(NOTIFICATION_ID, notification(status))
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
        manager().createNotificationChannel(NotificationChannel(CHANNEL, "World of Warcraft: Forever", NotificationManager.IMPORTANCE_LOW))
        return CHANNEL
    }

    private fun notification(status: ForeverPlay.Status): Notification {
        val stop = PendingIntent.getService(
            this, 1, Intent(this, ForeverService::class.java).setAction(ACTION_STOP), PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT,
        )
        val open = packageManager.getLaunchIntentForPackage(packageName)?.let {
            PendingIntent.getActivity(this, 0, it.addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP), PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)
        }
        return NotificationCompat.Builder(this, channel())
            .setSmallIcon(android.R.drawable.stat_sys_download)
            .setContentTitle("World of Warcraft: Forever")
            .setContentText(status.text.ifBlank { "Starting" }.take(120))
            .setOngoing(true).setOnlyAlertOnce(true).setContentIntent(open)
            .apply {
                if (status.progress != null) setProgress(100, (status.progress * 100).toInt().coerceIn(0, 100), false) else if (status.running) setProgress(0, 0, true)
                if (status.state != ForeverState.STOPPING) addAction(0, "Stop", stop)
            }
            .build()
    }

    companion object {
        private const val CHANNEL = "wow-forever"
        private const val NOTIFICATION_ID = 43
        const val ACTION_STOP = "com.logie.blizz.forevernew.STOP"

        /**
         * Whether Forever's programs need the app kept alive: while it works or stops, while the realm is up for the game
         * ([ForeverState.READY], [ForeverState.PLAYING]). Not once it has failed, stopped, or waits for the game's folder.
         */
        fun keepAlive(status: ForeverPlay.Status): Boolean =
            status.running || status.state.busy || status.state == ForeverState.READY || status.state == ForeverState.PLAYING

        fun start(context: Context) {
            runCatching { ContextCompat.startForegroundService(context, Intent(context, ForeverService::class.java)) }
        }
    }
}
