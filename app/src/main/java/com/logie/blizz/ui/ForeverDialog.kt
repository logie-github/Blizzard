package com.logie.blizz.ui

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import com.logie.blizz.forevernew.ForeverPlay
import com.logie.blizz.forevernew.ForeverState

/** World of Warcraft: Forever's page action: Install & Play, with the stage it is in and what isn't built yet. NOT run on a phone. */
@Composable
fun ForeverDialog(onDismiss: () -> Unit) {
    val context = LocalContext.current
    val status by ForeverPlay.status.collectAsState()
    LaunchedEffect(Unit) { ForeverPlay.refresh(context) }
    val picker = androidx.activity.compose.rememberLauncherForActivityResult(androidx.activity.result.contract.ActivityResultContracts.OpenDocumentTree()) { uri ->
        if (uri != null) ForeverPlay.importClient(context, uri)
    }
    Dialog(onDismissRequest = onDismiss) {
        androidx.compose.material3.Surface(shape = MaterialTheme.shapes.large, color = MaterialTheme.colorScheme.surface) {
            Column(Modifier.padding(20.dp)) {
                Text("World of Warcraft: Forever", style = MaterialTheme.typography.titleLarge)
                Text("Stage: ${status.state.name.lowercase().replace('_', ' ')}", Modifier.padding(top = 8.dp))
                if (status.text.isNotBlank()) Text(status.text, Modifier.padding(top = 4.dp))
                if (status.running) {
                    val p = status.progress
                    if (p != null) LinearProgressIndicator(progress = { p.coerceIn(0f, 1f) }, Modifier.fillMaxWidth().padding(top = 8.dp))
                    else LinearProgressIndicator(Modifier.fillMaxWidth().padding(top = 8.dp))
                }
                if (status.state == ForeverState.AWAITING_CLIENT && !status.running) {
                    Text("The game is downloaded from Blizzard's own servers (about 49 GB of free space, no account). If that couldn't be done, pick a World of Warcraft folder you already have (it holds .build.info, Data and _forever_): Import & Install.", Modifier.padding(top = 8.dp), style = MaterialTheme.typography.bodySmall)
                }
                Row(Modifier.fillMaxWidth().padding(top = 12.dp)) {
                    TextButton(onClick = { ForeverPlay.start(context) }, enabled = !status.running) { Text("Install & Play") }
                    if (status.state == ForeverState.AWAITING_CLIENT) {
                        TextButton(onClick = { picker.launch(null) }, enabled = !status.running) { Text("Import & Install") }
                    }
                    TextButton(onClick = { ForeverPlay.stop() }, enabled = !status.running && status.state == ForeverState.READY) { Text("Stop") }
                    TextButton(onClick = onDismiss) { Text("Close") }
                }
            }
        }
    }
}
