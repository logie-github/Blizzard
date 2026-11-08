package com.logie.blizz.ui

import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.logie.blizz.Game
import com.logie.blizz.music.MusicCatalog
import com.logie.blizz.music.MusicCustom

/**
 * A version's music, in the way of the art: what plays now (its own song, or the downloaded track) and what can be done with it:
 * Change (a song on the phone), Original (the downloaded track again). It plays while that version is the one the home shows.
 */
@Composable
fun MusicDialog(game: Game, onDismiss: () -> Unit) {
    val context = LocalContext.current
    val changed by MusicCustom.version.collectAsState()
    var message by remember { mutableStateOf<String?>(null) }
    val own = remember(game.id, changed) { MusicCustom.file(context, game.id) != null }
    val ownName = remember(game.id, changed) { MusicCustom.label(context, game.id) }
    val track = MusicCatalog.track(MusicCatalog.keyFor(game.id))
    var khinsider by remember { mutableStateOf(false) }
    val pick = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) message = if (MusicCustom.set(context, game.id, uri)) null else "That isn't an audio file this app can play."
    }
    if (khinsider) KhinsiderPicker(game, onMyFiles = { pick.launch(arrayOf("audio/*")) }, onDismiss = { khinsider = false })
    Dialog(onDismissRequest = onDismiss, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Sheet("${game.fullTitle} · Music", onDismiss, maxWidth = 520.dp) {
            Column(Modifier.padding(start = 20.dp, end = 20.dp, top = 8.dp, bottom = 22.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                SectionLabel(if (own) "Your song" else "Plays now")
                Column(
                    Modifier.fillMaxWidth().clip(RoundedCornerShape(12.dp)).border(1.dp, if (own) Colors.Ice else Colors.Steel, RoundedCornerShape(12.dp)).padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(4.dp),
                ) {
                    Text(
                        if (own) (ownName ?: "Your song") else (track?.label ?: "No track for this game"),
                        style = MaterialTheme.typography.titleMedium,
                    )
                    Text(if (own) "In place of the downloaded track on this page." else if (track != null) "The downloaded track." else "", style = MaterialTheme.typography.bodySmall)
                }
                Row(horizontalArrangement = Arrangement.spacedBy(18.dp)) {
                    MusicAction("Change") { khinsider = true }
                    if (own) MusicAction("Original", Colors.Mist) { MusicCustom.clear(context, game.id) }
                }
                message?.let { Text(it, style = MaterialTheme.typography.bodyMedium, color = Colors.Gold) }
            }
        }
    }
}

@Composable
private fun MusicAction(text: String, color: androidx.compose.ui.graphics.Color = Colors.Ice, onClick: () -> Unit) {
    Text(text, style = MaterialTheme.typography.labelLarge.copy(color = color, fontSize = 14.sp), modifier = Modifier.clip(RoundedCornerShape(6.dp)).clickable(onClick = onClick).padding(vertical = 4.dp))
}
