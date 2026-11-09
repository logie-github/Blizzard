package com.logie.blizz.ui

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.animateContentSize
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.graphics.Brush
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
 * the one choice that picks the most conservative of everything. In the look of the settings pages:
 * a panel of cards, each with its note, the choices in a row or a list.
 */
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
            Modifier.padding(14.dp).widthIn(max = 560.dp).fillMaxWidth().heightIn(max = 760.dp)
                .panel(),
        ) {
            Row(Modifier.fillMaxWidth().padding(start = 20.dp, end = 8.dp, top = 14.dp), verticalAlignment = Alignment.CenterVertically) {
                Column(Modifier.weight(1f)) {
                    FrameTitle("Launch options", style = MaterialTheme.typography.titleLarge)
                    Text(game.fullTitle, style = MaterialTheme.typography.bodyMedium, color = Colors.Mist, modifier = Modifier.padding(top = 2.dp))
                }
                CloseButton(onDismiss)
            }
            Column(
                Modifier.weight(1f, fill = false).verticalScroll(rememberScrollState()).padding(18.dp).animateContentSize(),
                verticalArrangement = Arrangement.spacedBy(14.dp),
            ) {
                if (!LaunchOptions.hasOptions(game.id)) {
                    SettingCard(null) {
                        Text(
                            "This game isn't played in the app's Windows, so it has no launch options.",
                            style = MaterialTheme.typography.bodyMedium, color = Colors.Mist,
                        )
                    }
                    FrameButton("Done", Modifier.fillMaxWidth(), onClick = onDismiss)
                    return@Column
                }

                SettingCard("Safe mode") {
                    Note("The most careful of everything: the slowest, for a game that shows a black screen or stops.")
                    Segmented(listOf("Off" to false, "On" to true), o.safeMode) { change(o.copy(safeMode = it)) }
                }

                if (!o.safeMode) {
                    if (LaunchOptions.isClassic(game.id)) {
                        SettingCard("DirectDraw") {
                            Note("How the picture is drawn. ${o.ddraw.note}")
                            ChoiceList(LaunchOptions.DDraw.entries.map { it.label to it }, o.ddraw) { change(o.copy(ddraw = it)) }
                        }
                        SettingCard("Frames a second") {
                            Note("How often the picture is drawn; the game's own speed doesn't change.")
                            Segmented(LaunchOptions.Fps.entries.map { it.label to it }, o.fps) { change(o.copy(fps = it)) }
                        }
                        TriCard("Wait for the screen (vsync)", "Stops tearing; adds a delay to the mouse.", o.vsync) { change(o.copy(vsync = it)) }
                        TriCard("Keep redrawing", "Videos, menus or loading screens that stay black or invisible: on (default).", o.redraw) { change(o.copy(redraw = it)) }
                        TriCard("Pin to one CPU core", "Can stop crashes on some PCs; on a phone it is the slowest core. Off by default.", o.singleCpu) { change(o.copy(singleCpu = it)) }
                    }
                    SettingCard("Box64") {
                        Note("The speed of the emulation. Stability and Compatible are slower and safer; Performance is the fastest.")
                        ChoiceList(LaunchOptions.Box64.Preset.entries.map { it.label to it }, o.box64) { change(o.copy(box64 = it)) }
                    }
                }
                SettingCard("Command line") {
                    Note("Switches of your own, added after the app's at the game's start (Diablo II: -w -ns -3dfx -ddraw -d3d; Warcraft III: -opengl -window). For trying a fix without a new build.")
                    androidx.compose.foundation.layout.Box(Modifier.fillMaxWidth().background(Colors.Abyss).padding(10.dp)) {
                        if (o.extraArgs.isEmpty()) Text("none", style = MaterialTheme.typography.bodyMedium, color = Colors.Steel)
                        androidx.compose.foundation.text.BasicTextField(
                            o.extraArgs, { v -> change(o.copy(extraArgs = v.replace("\n", " "))) },
                            singleLine = true, textStyle = MaterialTheme.typography.bodyMedium.copy(color = Colors.Text, fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace),
                            cursorBrush = androidx.compose.ui.graphics.SolidColor(Colors.Ice), modifier = Modifier.fillMaxWidth(),
                        )
                    }
                }

                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp, Alignment.End)) {
                    FrameButton("Reset", primary = false) { store.reset(game.id); o = store.get(game.id) }
                    FrameButton("Done", onClick = onDismiss)
                }
            }
        }
    }
}

@Composable
private fun Note(text: String) = Text(text, style = MaterialTheme.typography.bodySmall, color = Colors.Mist)

@Composable
private fun TriCard(title: String, note: String, value: LaunchOptions.Tri, onChange: (LaunchOptions.Tri) -> Unit) {
    SettingCard(title) {
        Note(note)
        Segmented(listOf("Default" to LaunchOptions.Tri.DEFAULT, "On" to LaunchOptions.Tri.ON, "Off" to LaunchOptions.Tri.OFF), value, onChange)
    }
}

/** A vertical list of choices, the chosen one lit with an ice bar at its side. */
@Composable
private fun <T> ChoiceList(options: List<Pair<String, T>>, selected: T, onSelect: (T) -> Unit) {
    Column(Modifier.fillMaxWidth().border(1.dp, Colors.Steel)) {
        options.forEachIndexed { index, (label, value) ->
            val on = value == selected
            val fill by animateColorAsState(if (on) Colors.Frost else Colors.Abyss.copy(alpha = 0f), label = "choice")
            Row(Modifier.fillMaxWidth().background(fill).clickable { onSelect(value) }.padding(end = 14.dp), verticalAlignment = Alignment.CenterVertically) {
                Box(Modifier.width(3.dp).heightIn(min = 46.dp).background(if (on) Colors.Ice else Colors.Abyss.copy(alpha = 0f)))
                Text(label, style = MaterialTheme.typography.bodyLarge.copy(color = if (on) Colors.Glow else Colors.Text), modifier = Modifier.padding(start = 14.dp, top = 12.dp, bottom = 12.dp).weight(1f))
            }
            if (index < options.lastIndex) Box(Modifier.fillMaxWidth().size(width = 1.dp, height = 1.dp).background(Colors.Steel.copy(alpha = 0.5f)))
        }
    }
}
