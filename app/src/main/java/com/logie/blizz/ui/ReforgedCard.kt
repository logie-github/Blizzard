package com.logie.blizz.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.logie.blizz.wrathpp.Reforged
import com.logie.blizz.wrathpp.ReforgedDownloads
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * Wrath++'s settings page: Project Reforged's parts, a switch each ([Reforged.Option]). Turning one on starts its download
 * ([ReforgedDownloads]); what is downloaded goes into Wrath++'s game at the next Play, and what is turned off comes out then.
 */
@OptIn(ExperimentalLayoutApi::class)
@Composable
internal fun ReforgedCard() {
    val context = LocalContext.current
    var chosen by remember { mutableStateOf(Reforged.chosen(context.filesDir)) }
    val downloads by ReforgedDownloads.state.collectAsState()
    var inGame by remember { mutableStateOf<Map<Char, Reforged.Installed>>(emptyMap()) }
    LaunchedEffect(chosen, downloads.running) {
        inGame = withContext(Dispatchers.IO) { ReforgedDownloads.data(context)?.let { Reforged.installed(it) } ?: emptyMap() }
    }
    SettingCard("Project Reforged") {
        Text(
            "Project Reforged's HD patches for everything but the characters: your characters and the character creator stay as " +
                "they are. Each switch downloads its part from the project by itself; it goes into Wrath++'s game at the next Play, " +
                "and a part turned off comes out then (Wrath+'s game is never changed). Downloads wait for Wi-Fi.",
            style = MaterialTheme.typography.bodySmall, color = Colors.Mist,
        )
        for (option in Reforged.Option.entries) {
            val on = option in chosen
            val parts = Reforged.parts(setOf(option) + (if (option == Reforged.Option.SOUNDS) chosen else emptySet()))
                .filter { option != Reforged.Option.SOUNDS || it == Reforged.Part.SOUNDS || it == Reforged.Part.SOUNDS_ALONE }
            val inNow = parts.all { p -> inGame[p.slot]?.remote == p.remote }
            Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                ToggleRow(option.title, on) { now ->
                    val next = if (now) chosen + option else chosen - option
                    Reforged.choose(context.filesDir, next)
                    chosen = next
                    ReforgedDownloads.start(context)
                }
                Text(option.detail + (if (on && inNow) " · in the game" else ""), style = MaterialTheme.typography.bodySmall, color = Colors.Mist)
            }
        }
        if (downloads.running) {
            Text("${downloads.text}: ${downloads.done shr 20} / ${downloads.total shr 20} MB", style = MaterialTheme.typography.bodySmall, color = Colors.Ice)
            if (downloads.total > 0) LinearProgressIndicator(progress = { downloads.done.toFloat() / downloads.total }, modifier = Modifier.fillMaxWidth())
        }
        for (line in downloads.lines) Text(line, style = MaterialTheme.typography.bodySmall, color = Colors.Mist)
        if (chosen.isNotEmpty()) FlowRow(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            if (downloads.running) FrameButton("Stop downloading", primary = false) { ReforgedDownloads.stop() }
            else {
                FrameButton("Download now", primary = false) { ReforgedDownloads.start(context) }
                FrameButton("Download on mobile data", primary = false) { ReforgedDownloads.start(context, anyNetwork = true) }
            }
        }
    }
}
