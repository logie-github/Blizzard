package com.logie.blizz.ui

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.logie.blizz.selftest.GameResult
import com.logie.blizz.selftest.Install
import com.logie.blizz.selftest.Launch
import com.logie.blizz.selftest.SelfTest

/** The launch test's progress and its report; shown while it runs and when it ends. */
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun SelfTestDialog() {
    val context = LocalContext.current
    val state by SelfTest.state.collectAsState()
    if (state is SelfTest.State.Idle) return
    Dialog(onDismissRequest = {}, properties = DialogProperties(usePlatformDefaultWidth = false, dismissOnClickOutside = false)) {
        Column(
            Modifier.padding(18.dp).widthIn(max = 520.dp).fillMaxWidth().background(Colors.Deep).border(1.dp, Colors.Steel)
                .verticalScroll(rememberScrollState()).padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            FrameTitle("Launch test")
            when (val s = state) {
                is SelfTest.State.Running -> {
                    Text("Testing ${minOf(s.index + 1, s.total)} of ${s.total}: ${s.current}", style = MaterialTheme.typography.titleMedium, color = Colors.Gold)
                    s.done.forEach { Line(it) }
                    FrameButton("Stop the test", primary = false) { SelfTest.cancel() }
                }
                is SelfTest.State.Finished -> {
                    s.results.forEach { Line(it) }
                    Text(
                        when (s.sent) {
                            SelfTest.Sent.SENT_LATER -> "The report is being sent to GitHub as an issue (kept on the phone and retried until it goes)."
                            SelfTest.Sent.NO_TOKEN -> "This build can't send reports to GitHub (no report token was built in). Copy the report and send it, or it stays on the phone."
                        },
                        style = MaterialTheme.typography.bodySmall, color = Colors.Mist,
                    )
                    FlowRow(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        FrameButton("Copy report", primary = false) {
                            (context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager).setPrimaryClip(ClipData.newPlainText("Launch test", s.markdown))
                        }
                        FrameButton("Close") { SelfTest.dismiss() }
                    }
                }
                else -> {}
            }
        }
    }
}

@Composable
private fun Line(r: GameResult) {
    val text = when {
        r.install == Install.NOT_INSTALLED -> "not installed"
        r.install == Install.INCOMPLETE -> "install incomplete"
        r.launch == Launch.OK -> "launched" + (r.windowSeconds?.let { " (window in $it s)" } ?: "")
        r.launch == Launch.TIMED_OUT -> "no window: timed out"
        r.launch == Launch.FAILED -> "failed: ${r.launchDetail.take(110)}"
        else -> "installed, not started"
    }
    Text("${r.title}: $text", style = MaterialTheme.typography.bodyMedium, color = if (r.launch == Launch.OK) Colors.Ice else Colors.Mist)
}
