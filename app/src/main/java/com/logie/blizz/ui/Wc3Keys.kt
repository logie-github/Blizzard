package com.logie.blizz.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.logie.blizz.game.Wc3CdKeys

/**
 * Warcraft III's CD keys: paste them in any form (with or without spaces and dashes, one or both, a label before one); each is put with
 * its game by what it decodes to. They are written into the game's own archives when it is installed, which 1.27 looks for at start,
 * so with an install in place **Save and install again** makes the install again with them (the download again, saves kept).
 * Kept on this phone only (`files/cdkeys.txt`), never in a report. The app makes and fetches no keys.
 */
@Composable
fun Wc3Keys(installed: Boolean, onInstallAgain: () -> Unit, modifier: Modifier = Modifier) {
    val filesDir = LocalContext.current.applicationContext.filesDir
    var text by remember { mutableStateOf(Wc3CdKeys.text(filesDir)) }
    var savedText by remember { mutableStateOf(text) }
    val keys = Wc3CdKeys.wc3(text)
    fun masked(k: String?) = if (k == null) "none" else k.take(4) + "…" + k.takeLast(4)
    Column(modifier, verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text("Your CD keys", style = MaterialTheme.typography.titleMedium)
        Box(Modifier.fillMaxWidth().heightIn(min = 72.dp).background(Colors.Abyss).padding(10.dp)) {
            if (text.isEmpty()) Text("Paste your Warcraft III keys: with or without dashes and spaces, both keys at once if you like.", style = MaterialTheme.typography.bodyMedium, color = Colors.Steel)
            BasicTextField(text, { text = it }, textStyle = MaterialTheme.typography.bodyMedium.copy(color = Colors.Text), cursorBrush = SolidColor(Colors.Ice), modifier = Modifier.fillMaxWidth())
        }
        if (text.isNotBlank()) {
            Text("Reign of Chaos: ${masked(keys.reignOfChaos)}   ·   The Frozen Throne: ${masked(keys.frozenThrone)}" +
                (if (keys.unrecognised > 0) "\n${keys.unrecognised} not a Warcraft III key I recognise." else ""), style = MaterialTheme.typography.bodySmall, color = Colors.Mist)
        }
        val changed = text != savedText
        if (changed || (installed && keys.any)) {
            if (keys.any || text.isBlank()) FrameButton(if (installed) "Save and install again" else "Save", Modifier.fillMaxWidth()) {
                runCatching { Wc3CdKeys.save(filesDir, text) }
                savedText = text
                if (installed) onInstallAgain()
            }
        }
    }
}
