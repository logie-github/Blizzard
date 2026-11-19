package com.logie.blizz.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.logie.blizz.converter.ConverterController
import com.logie.blizz.converter.Expansions

/**
 * Legion's settings page: the Converter. One row for each expansion from Cataclysm on (Cataclysm, Mists of Pandaria, Warlords of Draenor, Legion): its
 * maps, models, textures and tables made into 3.3.5a's format from wago.tools' files for the build (Legion's is the client this launcher plays), kept on the
 * phone for what you decide to do with them later ([ConverterController]).
 */
@Composable
internal fun ConverterCard() {
    val context = LocalContext.current
    val s by ConverterController.state.collectAsState()
    LaunchedEffect(Unit) { ConverterController.refresh(context) }
    SettingCard("Converter") {
        Text(
            "Makes the content of an expansion into 3.3.5a's format, one expansion at a time: its maps, models, textures and tables, from Cataclysm on. " +
                "The first use downloads the converter's runtime (Python and the tools). Nothing is put into a game: the results are kept on this phone for later.",
            style = MaterialTheme.typography.bodySmall, color = Colors.Mist,
        )
        s.message?.let { Text(it, style = MaterialTheme.typography.bodySmall, color = Colors.Gold) }
        s.runtimeText?.let { text ->
            Text(text, style = MaterialTheme.typography.bodySmall, color = Colors.Ice)
            s.runtimeFraction?.let { f -> LinearProgressIndicator(progress = { f.coerceIn(0f, 1f) }, modifier = Modifier.fillMaxWidth()) }
        }
        Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
            for (e in Expansions.all) {
                val p = s.progress[e.key]
                val running = s.running == e.key
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text(e.name, style = MaterialTheme.typography.bodyMedium, color = Colors.Mist)
                    val line = when {
                        running && p != null && !p.finished -> "${p.message.ifEmpty { p.state }}"
                        running -> "Starting"
                        p == null -> "Not converted yet"
                        else -> "${p.state}: ${p.message}"
                    }
                    Text(line, style = MaterialTheme.typography.bodySmall, color = Colors.Mist)
                    if (running) {
                        (p?.fraction)?.let { f -> LinearProgressIndicator(progress = { f }, modifier = Modifier.fillMaxWidth()) }
                        FrameButton("Stop", primary = false, modifier = Modifier.fillMaxWidth()) { ConverterController.stop() }
                    } else {
                        FrameButton(if (p == null) "Convert" else "Convert again", primary = false, modifier = Modifier.fillMaxWidth()) {
                            ConverterController.convert(context, e.key)
                        }
                    }
                }
            }
        }
        if (s.runtimeInstalled && s.running == null && s.runtimeText == null) {
            FrameButton("Update the converter's runtime", primary = false, modifier = Modifier.fillMaxWidth()) { ConverterController.installRuntime(context, update = true) }
        }
        if (s.outputFolder.isNotEmpty()) {
            Text("Results: ${s.outputFolder}/<expansion>/release", style = MaterialTheme.typography.bodySmall, color = Colors.Mist)
        }
    }
}
