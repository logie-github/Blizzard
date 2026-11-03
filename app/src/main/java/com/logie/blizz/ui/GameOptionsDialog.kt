package com.logie.blizz.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
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
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.logie.blizz.Game
import com.logie.blizz.game.LaunchOptions
import com.logie.blizz.game.LaunchOptionsStore

/**
 * A game's launch options ([LaunchOptions]): graphics and speed settings for when a game shows a black
 * screen or runs slowly. Kept as they are chosen and used at the game's next start. Safe mode first,
 * the one choice that picks the most conservative of everything.
 */
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun GameOptionsDialog(game: Game, onDismiss: () -> Unit) {
    val context = LocalContext.current
    val store = remember { LaunchOptionsStore(context) }
    var o by remember { mutableStateOf(store.get(game.id)) }
    fun change(next: LaunchOptions) {
        o = next
        store.set(game.id, next)
    }

    Dialog(onDismissRequest = onDismiss, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Column(
            Modifier.padding(18.dp).widthIn(max = 520.dp).fillMaxWidth().background(Colors.Deep).border(1.dp, Colors.Steel)
                .verticalScroll(rememberScrollState()).padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            FrameTitle("Launch options")
            Text(game.fullTitle, style = MaterialTheme.typography.titleMedium, color = Colors.Gold)

            if (!LaunchOptions.hasOptions(game.id)) {
                Text(
                    "This game isn't played in the app's Windows, so it has no launch options.",
                    style = MaterialTheme.typography.bodyMedium, color = Colors.Mist,
                )
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.End) { FrameButton("Done", onClick = onDismiss) }
                return@Column
            }

            Text(
                "The graphics driver, Direct3D layer and resolution are chosen by the app for this phone and screen; they have no setting.",
                style = MaterialTheme.typography.bodySmall, color = Colors.Mist,
            )
            Text(
                "For a black screen, no sound, no videos or a slow game: change one thing, start the game, and come back. Used at the game's next start.",
                style = MaterialTheme.typography.bodySmall, color = Colors.Mist,
            )

            Text("Safe mode", style = MaterialTheme.typography.titleMedium, color = Colors.Gold)
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                FrameButton("Off", primary = !o.safeMode) { change(o.copy(safeMode = false)) }
                FrameButton("On", primary = o.safeMode) { change(o.copy(safeMode = true)) }
            }
            Text(
                "On: the slowest, safest of everything (software drawing, Stability, 30 frames a second) and the settings below are ignored. Try it first when the game shows nothing.",
                style = MaterialTheme.typography.bodySmall, color = Colors.Mist,
            )

            if (!o.safeMode) {
                if (LaunchOptions.isClassic(game.id)) {
                    Section("DirectDraw (how the picture is drawn)", o.ddraw.note) {
                        LaunchOptions.DDraw.entries.forEach { c -> Chip(c.label, o.ddraw == c) { change(o.copy(ddraw = c)) } }
                    }
                    Section("Frames a second", "How often the picture is drawn; the game's own speed doesn't change.") {
                        LaunchOptions.Fps.entries.forEach { c -> Chip(c.label, o.fps == c) { change(o.copy(fps = c)) } }
                    }
                    TriSection("Wait for the screen (vsync)", "Stops tearing; adds a delay to the mouse.", o.vsync) { change(o.copy(vsync = it)) }
                    TriSection(
                        "Keep redrawing", "Videos, menus or loading screens that stay black or invisible: on (default).",
                        o.redraw,
                    ) { change(o.copy(redraw = it)) }
                    TriSection(
                        "Pin to one CPU core", "Can stop crashes on some PCs; on a phone it is the slowest core. Off by default.",
                        o.singleCpu,
                    ) { change(o.copy(singleCpu = it)) }
                }

                Section("Box64 (the speed of the emulation)", "Stability and Compatible are slower and safer; Performance is the fastest.") {
                    LaunchOptions.Box64.Preset.entries.forEach { c -> Chip(c.label, o.box64 == c) { change(o.copy(box64 = c)) } }
                }
            }

            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp, androidx.compose.ui.Alignment.End)) {
                FrameButton("Reset", primary = false) { store.reset(game.id); o = store.get(game.id) }
                FrameButton("Done", onClick = onDismiss)
            }
        }
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun Section(title: String, note: String, chips: @Composable () -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
        Text(title, style = MaterialTheme.typography.titleMedium, color = Colors.Gold)
        FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) { chips() }
        Text(note, style = MaterialTheme.typography.bodySmall, color = Colors.Mist)
    }
}

@Composable
private fun TriSection(title: String, note: String, value: LaunchOptions.Tri, onChange: (LaunchOptions.Tri) -> Unit) {
    Section(title, note) {
        Chip("Default", value == LaunchOptions.Tri.DEFAULT) { onChange(LaunchOptions.Tri.DEFAULT) }
        Chip("On", value == LaunchOptions.Tri.ON) { onChange(LaunchOptions.Tri.ON) }
        Chip("Off", value == LaunchOptions.Tri.OFF) { onChange(LaunchOptions.Tri.OFF) }
    }
}

@Composable
private fun Chip(text: String, selected: Boolean, onClick: () -> Unit) = FrameButton(text, primary = selected, onClick = onClick)
