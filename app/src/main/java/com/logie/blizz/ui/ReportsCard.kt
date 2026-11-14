package com.logie.blizz.ui

import android.widget.Toast
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.logie.blizz.reports.BugReports

/**
 * What became of the app's reports, and a way to send the app's log whenever it is wanted (not only from a game's menu): the run's
 * log, the phone's memory and processes, Android's log of this app, and how the last run ended. The list is what the phone itself
 * wrote down at each send (`reports/history.log`): sent as which issue, kept for a retry, or refused, and why.
 */
@Composable
internal fun ReportsCard() {
    val context = LocalContext.current
    var history by remember { mutableStateOf(BugReports.history(context, 5)) }
    var waiting by remember { mutableStateOf(BugReports.waiting(context)) }
    SettingCard("Reports") {
        Text(
            when {
                !BugReports.configured(context) -> "This build has no way to send reports; they stay on the phone."
                waiting > 0 -> "$waiting waiting to be sent (they go again every minute)."
                else -> "None waiting."
            },
            style = MaterialTheme.typography.bodyMedium, color = if (waiting > 0) Colors.Gold else Colors.Ice,
        )
        if (history.isNotEmpty()) {
            Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                history.asReversed().forEach { Text(it, style = MaterialTheme.typography.bodySmall, color = Colors.Mist) }
            }
        }
        FrameButton("Send the log now", primary = false, modifier = Modifier.fillMaxWidth()) {
            val app = context.applicationContext
            BugReports.report(
                app, "Log sent from Settings", "The person pressed Send the log in Settings",
                listOf("Game" to "none"), log = com.logie.blizz.game.GameLog.snapshot().ifEmpty { null },
                attach = true, force = true,
                onResult = { result ->
                    android.os.Handler(android.os.Looper.getMainLooper()).post { Toast.makeText(app, result.say(), Toast.LENGTH_LONG).show() }
                },
            )
            Toast.makeText(context, "Sending the log…", Toast.LENGTH_SHORT).show()
            history = BugReports.history(context, 5)
            waiting = BugReports.waiting(context)
        }
    }
}
