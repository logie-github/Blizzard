package com.logie.blizz.ui

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.logie.blizz.reports.BugReports

/** The footer's "Bug reports": on (with the waiting count) or off, opening the token dialog. */
@Composable
internal fun BugReportsLink() {
    val context = LocalContext.current
    var open by remember { mutableStateOf(false) }
    var refresh by remember { mutableStateOf(0) }
    val on = remember(refresh) { BugReports.configured(context) }
    val waiting = remember(refresh) { BugReports.waiting(context) }
    Text(
        "Bug reports: " + (if (on) "on" else "off") + (if (waiting > 0) " · $waiting waiting" else ""),
        style = MaterialTheme.typography.bodySmall.copy(color = if (on) Colors.Ice else Colors.Mist),
        modifier = Modifier.clickable { open = true }.padding(8.dp),
    )
    if (open) BugReportsDialog(onDismiss = { open = false; refresh++ })
}

/**
 * The GitHub token the bug reports go with: a fine-grained token with Issues (read and write) on
 * logie-github/Blizzard, pasted once and kept on this phone only.
 */
@Composable
private fun BugReportsDialog(onDismiss: () -> Unit) {
    val context = LocalContext.current
    var token by remember { mutableStateOf(BugReports.token(context)) }
    Dialog(onDismissRequest = onDismiss, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Column(
            Modifier.padding(20.dp).widthIn(max = 520.dp).fillMaxWidth()
                .drawBehind { drawRect(Colors.Deep); drawFrame() }
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            FrameTitle("Bug reports")
            Text(
                "Crashes, failed imports and failed launches go to ${BugReports.repo} as issues. " +
                    "Paste a GitHub token that may open issues there (fine-grained: that repository, Issues read and write).",
                style = MaterialTheme.typography.bodyMedium,
            )
            Box(Modifier.fillMaxWidth().background(Colors.Abyss).padding(12.dp)) {
                if (token.isEmpty()) Text("github_pat_…", style = MaterialTheme.typography.bodyMedium, color = Colors.Steel)
                BasicTextField(
                    token, { token = it.trim() }, singleLine = true,
                    textStyle = MaterialTheme.typography.bodyMedium, cursorBrush = SolidColor(Colors.Ice),
                    visualTransformation = PasswordVisualTransformation(),
                    modifier = Modifier.fillMaxWidth(),
                )
            }
            Text(
                "Make one on GitHub",
                style = MaterialTheme.typography.bodySmall.copy(color = Colors.Ice),
                modifier = Modifier.clickable {
                    runCatching {
                        context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("https://github.com/settings/personal-access-tokens/new")).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
                    }
                },
            )
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp, Alignment.End)) {
                if (BugReports.configured(context)) FrameButton("Turn off", primary = false) { BugReports.setToken(context, ""); onDismiss() }
                FrameButton("Save") { BugReports.setToken(context, token); onDismiss() }
            }
        }
    }
}
