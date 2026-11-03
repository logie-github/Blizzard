package com.logie.blizz.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
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
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.logie.blizz.game.GameSettings

/** The launcher's settings, opened by holding the Blizzard logo: the layout, the tile size, vibration. */
@Composable
fun SettingsDialog(onDismiss: () -> Unit) {
    val context = LocalContext.current
    val s by TileSettings.state.collectAsState()
    var vibration by remember { mutableStateOf(GameSettings.vibration(context)) }
    var confirmReset by remember { mutableStateOf(false) }
    Dialog(onDismissRequest = onDismiss, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Column(
            Modifier.padding(18.dp).widthIn(max = 520.dp).fillMaxWidth().background(Colors.Deep).border(1.dp, Colors.Steel)
                .verticalScroll(rememberScrollState()).padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            FrameTitle("Settings")

            Text("Layout", style = MaterialTheme.typography.titleMedium, color = Colors.Gold)
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                FrameButton("Classic shelf", primary = s.mode == TileSettings.Mode.SHELF) { TileSettings.setMode(context, TileSettings.Mode.SHELF) }
                FrameButton("Tiles", primary = s.mode == TileSettings.Mode.TILES) { TileSettings.setMode(context, TileSettings.Mode.TILES) }
            }
            Text(
                "Tiles: hold one for Change Art, Rearrange or Reinstall; pinch to make them bigger or smaller; each can be vertical or horizontal.",
                style = MaterialTheme.typography.bodySmall, color = Colors.Mist,
            )

            if (s.mode == TileSettings.Mode.TILES) {
                Text("Tiles across", style = MaterialTheme.typography.titleMedium, color = Colors.Gold)
                val shown = if (s.columns > 0) "${s.columns}" else "auto"
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalAlignment = Alignment.CenterVertically) {
                    FrameButton("−", primary = false) { TileSettings.setColumns(context, ((if (s.columns > 0) s.columns else TileLayout.autoColumns(360f)) + 1)) }
                    Text(shown, style = MaterialTheme.typography.titleMedium, modifier = Modifier.widthIn(min = 48.dp))
                    FrameButton("+", primary = false) { TileSettings.setColumns(context, ((if (s.columns > 0) s.columns else TileLayout.autoColumns(360f)) - 1).coerceAtLeast(1)) }
                    FrameButton("Auto", primary = s.columns == 0) { TileSettings.setColumns(context, 0) }
                }
            }

            Text("Touch", style = MaterialTheme.typography.titleMedium, color = Colors.Gold)
            FrameButton(if (vibration) "Vibration: on" else "Vibration: off", primary = false) {
                vibration = !vibration
                GameSettings.setVibration(context, vibration)
            }

            if (confirmReset) {
                Text("Put the tiles back as they were (order, shapes, size, pictures)?", style = MaterialTheme.typography.bodyMedium, color = Colors.Gold)
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    FrameButton("No", primary = false) { confirmReset = false }
                    FrameButton("Reset tiles") { TileSettings.reset(context); confirmReset = false }
                }
            } else {
                FrameButton("Reset tile layout", primary = false) { confirmReset = true }
            }

            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.End) { FrameButton("Done", onClick = onDismiss) }
        }
    }
}
