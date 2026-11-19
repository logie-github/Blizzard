package com.logie.blizz.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.fillMaxWidth
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
import com.logie.blizz.wrathpp.WrathppWideSkins

/** Wrath++'s whole skins: every hair style with all of its triangles, or the cut models ([WrathppWideSkins]). Taken at the next Play. */
@OptIn(ExperimentalLayoutApi::class)
@Composable
internal fun WrathppWideSkinsCard() {
    val context = LocalContext.current
    var on by remember { mutableStateOf(WrathppWideSkins.on(context.filesDir)) }
    SettingCard("Whole hair") {
        Text(
            "Every hair style is drawn with all of its triangles (the app's own mod lets the game read models larger than it can by itself). " +
                "Off draws the cut-down models: turn it off if hair or parts of a character are missing. Taken at the next Play.",
            style = MaterialTheme.typography.bodySmall, color = Colors.Mist,
        )
        FlowRow(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            for (choice in listOf(true, false)) {
                FrameButton(if (choice) "On" else "Off", primary = choice == on) {
                    WrathppWideSkins.set(context.filesDir, choice)
                    on = choice
                }
            }
        }
    }
}
