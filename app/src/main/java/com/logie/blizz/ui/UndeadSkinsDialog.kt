package com.logie.blizz.ui

import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.logie.blizz.wrathpp.WrathppUndead
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/**
 * Undead skins for Wrath++ (World of Warcraft's boxes, held): pick the file of skins ([WrathppUndead]: textures of yours,
 * never in the app), or take them out. They go into Wrath++'s game at its next Play, as new skins after each race's own,
 * under the creator's Undead switch.
 */
@OptIn(ExperimentalLayoutApi::class)
@Composable
internal fun UndeadSkinsDialog(onDismiss: () -> Unit) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val store = remember { WrathppUndead.store(context) }
    var models by remember { mutableStateOf(runCatching { if (WrathppUndead.installed(store)) WrathppUndead.models(store) else emptyList() }.getOrDefault(emptyList())) }
    var working by remember { mutableStateOf(false) }
    var confirmRemove by remember { mutableStateOf(false) }
    val pick = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri == null) return@rememberLauncherForActivityResult
        working = true
        scope.launch {
            val result = withContext(Dispatchers.IO) {
                runCatching {
                    val input = context.contentResolver.openInputStream(uri) ?: throw java.io.IOException("The file couldn't be opened.")
                    input.use { WrathppUndead.importZip(store, it) }
                }
            }
            working = false
            result.onSuccess { models = it }
            Toast.makeText(
                context,
                result.fold({ "Undead skins in: ${it.sumOf { m -> m.skins.size }} for ${it.size} races and sexes. They are in Wrath++ at its next Play." }, { it.message ?: "The file couldn't be read." }),
                Toast.LENGTH_LONG,
            ).show()
        }
    }
    Dialog(onDismissRequest = onDismiss, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Column(
            Modifier.padding(24.dp).widthIn(max = 480.dp).fillMaxWidth().background(Colors.Deep).border(1.dp, Colors.Steel).padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            FrameTitle("Undead skins (Wrath++)", style = MaterialTheme.typography.titleLarge)
            Text(
                "Undead skins for Wrath++'s living races, from a file of yours (wrathpp-undead-skins.zip). Each is a new skin " +
                    "after the race's own, with its own face: nothing of the game's is replaced. In Wrath++'s character creator they " +
                    "are under Accessories, Undead. They go into Wrath++'s game the next time you press Play on it.",
                style = MaterialTheme.typography.bodyMedium, color = Colors.Mist,
            )
            Text(
                when {
                    working -> "Reading the file…"
                    models.isEmpty() -> "None on this phone yet."
                    else -> "${models.sumOf { it.skins.size }} skins for ${models.size} races and sexes: " + models.joinToString(", ") { it.name } + "."
                },
                style = MaterialTheme.typography.bodyMedium, color = Colors.Text,
            )
            FlowRow(
                Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(10.dp, Alignment.End),
                verticalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                if (models.isNotEmpty() && !working) FrameButton("Remove", primary = false) { confirmRemove = true }
                FrameButton("Close", primary = false, onClick = onDismiss)
                if (!working) FrameButton(if (models.isEmpty()) "Pick the file" else "Pick another file") { pick.launch(arrayOf("*/*")) }
            }
        }
    }
    if (confirmRemove) ConfirmDialog(
        title = "Remove the undead skins?",
        text = "They are taken out of Wrath++'s game at its next Play. A character made with one keeps its number of skin, which the game then has no picture for: change its skin first, or pick the file again.",
        confirm = "Remove",
        onDismiss = { confirmRemove = false },
        onConfirm = {
            confirmRemove = false
            WrathppUndead.remove(store)
            models = emptyList()
        },
    )
}
