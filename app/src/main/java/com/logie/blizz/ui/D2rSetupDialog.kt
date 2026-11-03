package com.logie.blizz.ui

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
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
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.logie.blizz.d2r.D2r
import com.logie.blizz.update.Updater
import kotlinx.coroutines.launch

/** Diablo II: Resurrected's setup: the app that plays it, and what it needs from the player. */
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun D2rSetupDialog(onDismiss: () -> Unit) {
    val context = LocalContext.current
    val state by D2r.state.collectAsState()
    val scope = rememberCoroutineScope()
    val version = D2r.installedVersion(context)
    Dialog(onDismissRequest = onDismiss, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Column(
            Modifier.padding(18.dp).widthIn(max = 520.dp).fillMaxWidth().background(Colors.Deep).border(1.dp, Colors.Steel)
                .verticalScroll(rememberScrollState()).padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            FrameTitle("Diablo II: Resurrected")
            Text(
                "Played in D2R Mobile, an open-source Android port (MIT) that runs the Nintendo Switch release's own program on Vulkan. It is a separate app: Play opens it. Your game files are your own; it needs an import pack made on a computer.",
                style = MaterialTheme.typography.bodyMedium, color = Colors.Mist,
            )
            Text(
                if (version != null) "D2R Mobile $version is installed." else "D2R Mobile isn't installed.",
                style = MaterialTheme.typography.titleMedium, color = if (version != null) Colors.Ice else Colors.Gold,
            )
            D2r.STEPS.forEachIndexed { i, s -> Text("${i + 1}. $s", style = MaterialTheme.typography.bodySmall, color = Colors.Mist) }
            when (val s = state) {
                is D2r.State.Downloading -> Text(
                    "Downloading D2R Mobile" + if (s.total > 0) " ${s.done * 100 / s.total}%" else "…",
                    style = MaterialTheme.typography.bodyMedium, color = Colors.Gold,
                )
                is D2r.State.Ready -> Text("Downloaded. Tap Install to put it on the phone.", style = MaterialTheme.typography.bodyMedium, color = Colors.Ice)
                is D2r.State.Failed -> Text("Couldn't download: ${s.message}", style = MaterialTheme.typography.bodyMedium, color = Colors.Gold)
                else -> {}
            }
            FlowRow(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                val ready = state as? D2r.State.Ready
                if (ready != null) {
                    FrameButton("Install") {
                        if (Updater.canInstall(context)) context.startActivity(Updater.installIntent(context, ready.apk))
                        else context.startActivity(Intent(android.provider.Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES, Uri.parse("package:${context.packageName}")))
                    }
                } else if (state !is D2r.State.Downloading) {
                    FrameButton(if (version == null) "Download D2R Mobile" else "Update D2R Mobile", primary = version == null) { scope.launch { D2r.download(context) } }
                }
                if (version != null) FrameButton("Open D2R Mobile", primary = false) {
                    context.packageManager.getLaunchIntentForPackage(D2r.PACKAGE)?.let { context.startActivity(it.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)) }
                }
                FrameButton("Copy the computer command", primary = false) {
                    (context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager).setPrimaryClip(ClipData.newPlainText("D2R Mobile", D2r.COMPUTER_COMMAND))
                }
                FrameButton("Open its page", primary = false) {
                    context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(D2r.PROJECT_URL)).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
                }
                FrameButton("Done", primary = false) { D2r.dismissState(); onDismiss() }
            }
        }
    }
}

/** A pill on the Resurrected page: opens the setup, saying whether the app is there. */
@Composable
fun D2rStatus(shown: com.logie.blizz.Game) {
    val game = effectiveGame(shown)
    if (game.id != D2r.GAME_ID) return
    val context = LocalContext.current
    val installed = D2r.installed(context)
    androidx.compose.foundation.layout.Row(
        Modifier.padding(vertical = 4.dp).clickable { D2r.requestSetup() }.padding(horizontal = 12.dp, vertical = 6.dp),
    ) {
        Text(
            (if (installed) "D2R Mobile installed" else "Needs D2R Mobile") + "  ·  Set up",
            style = MaterialTheme.typography.bodySmall.copy(color = if (installed) Colors.Ice else Colors.Gold),
        )
    }
}
