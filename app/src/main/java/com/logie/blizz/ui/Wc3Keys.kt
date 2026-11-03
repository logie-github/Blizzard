package com.logie.blizz.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
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
 * Warcraft III's CD keys (optional: single player and LAN never need one): the keys the person
 * has, one a line, a label before a key allowed ("Reign of Chaos: XXXX-..."). Kept on the phone in
 * `files/cdkeys.txt`, apart from the game's folder, and offered by the game's menu to be typed
 * when the game asks. The app makes, fetches and carries no keys.
 */
@Composable
fun Wc3Keys(modifier: Modifier = Modifier) {
    val filesDir = LocalContext.current.applicationContext.filesDir
    var open by remember { mutableStateOf(false) }
    var text by remember { mutableStateOf(Wc3CdKeys.text(filesDir)) }
    val count = Wc3CdKeys.findPasted(text).size
    Column(modifier) {
        val summary = if (count > 0) " ($count)" else ""
        Text(
            if (open) "CD keys (optional)$summary ▴" else "CD keys (optional)$summary ▾",
            style = MaterialTheme.typography.bodySmall.copy(color = Colors.Mist),
            modifier = Modifier.clickable { open = !open }.padding(vertical = 4.dp),
        )
        if (!open) return@Column
        Box(Modifier.fillMaxWidth().heightIn(min = 72.dp).background(Colors.Abyss).padding(10.dp)) {
            if (text.isEmpty()) {
                Text("Paste your Warcraft III keys, one a line (a label before a key is fine).", style = MaterialTheme.typography.bodyMedium, color = Colors.Steel)
            }
            BasicTextField(
                text,
                { v ->
                    text = v
                    runCatching { Wc3CdKeys.save(filesDir, v) }
                },
                textStyle = MaterialTheme.typography.bodyMedium,
                cursorBrush = SolidColor(Colors.Ice),
                modifier = Modifier.fillMaxWidth(),
            )
        }
        Text(
            if (count == 0) "Kept on this phone only, never with the game's files." else "$count key${if (count == 1) "" else "s"} kept on this phone only, never with the game's files.",
            style = MaterialTheme.typography.bodySmall.copy(color = Colors.Steel),
            modifier = Modifier.padding(top = 4.dp),
        )
    }
}
