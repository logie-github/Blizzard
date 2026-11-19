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
import com.logie.blizz.wrathpp.WrathppSoftBody

/** Wrath++'s soft body: how much the women's chests move with the character ([WrathppSoftBody]). Taken at the next Play. */
@OptIn(ExperimentalLayoutApi::class)
@Composable
internal fun WrathppSoftBodyCard() {
    val context = LocalContext.current
    var level by remember { mutableStateOf(WrathppSoftBody.chosen(context.filesDir)) }
    SettingCard("Soft body") {
        Text(
            "The women's chests hang, bounce and settle as the character moves (the game's bones, sprung by the app's own mod). " +
                "Off draws them as the game does. Taken at the next Play.",
            style = MaterialTheme.typography.bodySmall, color = Colors.Mist,
        )
        FlowRow(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            for (l in WrathppSoftBody.Level.entries) {
                FrameButton(l.title, primary = l == level) {
                    WrathppSoftBody.choose(context.filesDir, l)
                    level = l
                }
            }
        }
    }
}
