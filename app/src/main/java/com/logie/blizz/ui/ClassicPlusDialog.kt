package com.logie.blizz.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.logie.blizz.warsmash.ClassicPlus

/** Classic+ for Warcraft III (both games, in Warsmash): fetch it, turn it on or off, remove it. Held from the box's menu. */
@Composable
internal fun ClassicPlusDialog(onDismiss: () -> Unit) {
    val context = LocalContext.current
    val state by ClassicPlus.state.collectAsState()
    var installed by remember { mutableStateOf(ClassicPlus.installed(context)) }
    var on by remember { mutableStateOf(ClassicPlus.on(context)) }
    if (state is ClassicPlus.State.Done && !installed) {
        installed = ClassicPlus.installed(context)
        on = ClassicPlus.on(context)
    }
    var confirmRemove by remember { mutableStateOf(false) }
    Dialog(onDismissRequest = onDismiss, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Column(
            Modifier.padding(24.dp).widthIn(max = 480.dp).fillMaxWidth().background(Colors.Deep).border(1.dp, Colors.Steel).padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            FrameTitle("Classic+", style = MaterialTheme.typography.titleLarge)
            Text(
                "Warcraft III's units, trees and textures remade in more detail and true to the original's look, by Piotr " +
                    "Bednarczuk (kenshin.pl/classicplus): 140 units, 200 trees, 1,200 textures, new auras and team colours. " +
                    "It plays over your game's own files in both games; the campaigns' own heroes and some missiles and spell " +
                    "effects keep the originals. A change takes effect the next time the game starts.",
                style = MaterialTheme.typography.bodyMedium, color = Colors.Mist,
            )
            when (val s = state) {
                is ClassicPlus.State.Working -> {
                    Text(s.step, style = MaterialTheme.typography.bodyMedium, color = Colors.Text)
                    LinearProgressIndicator(progress = { s.fraction }, modifier = Modifier.fillMaxWidth())
                }
                is ClassicPlus.State.Failed -> Text("Didn't finish: ${s.message}", style = MaterialTheme.typography.bodyMedium, color = Colors.Text)
                else -> Text(
                    when {
                        !installed -> "Not on this phone yet: a ${ClassicPlus.SIZE / (1L shl 20)} MB download from the author's Google Drive, about 700 MB once ready."
                        on -> "On."
                        else -> "Off (kept on the phone)."
                    },
                    style = MaterialTheme.typography.bodyMedium, color = Colors.Text,
                )
            }
            val working = state is ClassicPlus.State.Working
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp, Alignment.End)) {
                if (installed && !working) FrameButton("Remove", primary = false) { confirmRemove = true }
                FrameButton("Close", primary = false, onClick = onDismiss)
                if (!working) {
                    if (!installed) FrameButton("Download") { ClassicPlus.install(context) }
                    else FrameButton(if (on) "Turn off" else "Turn on") {
                        ClassicPlus.setOn(context, !on)
                        on = ClassicPlus.on(context)
                    }
                }
            }
        }
    }
    if (confirmRemove) ConfirmDialog(
        title = "Remove Classic+?",
        text = "Its files are deleted from the phone (about 700 MB) and the game plays with its own again. You can download it again any time.",
        confirm = "Remove",
        onDismiss = { confirmRemove = false },
        onConfirm = {
            confirmRemove = false
            ClassicPlus.remove(context)
            installed = false
            on = false
        },
    )
}
