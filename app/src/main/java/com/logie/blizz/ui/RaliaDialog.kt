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
import com.logie.blizz.wrathpp.ImportFinder
import com.logie.blizz.wrathpp.WrathppRalia
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File
import java.io.InputStream

/**
 * Ralia's mod on Wrath++ (World of Warcraft's boxes, held): the zip of its textures ([WrathppRalia]: yours, never in the
 * app) is looked for by its name, `ralia.zip`, where downloads are, or picked by hand; its skins go into Wrath++'s game
 * at its next Play, in place of the game's own they are named for, and come out again with Remove.
 */
@OptIn(ExperimentalLayoutApi::class)
@Composable
internal fun RaliaDialog(onDismiss: () -> Unit) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val store = remember { WrathppRalia.store(context) }
    var count by remember { mutableStateOf(if (WrathppRalia.installed(store)) WrathppRalia.count(store) else 0) }
    var working by remember { mutableStateOf(false) }
    var confirmRemove by remember { mutableStateOf(false) }
    val found = remember { runCatching { ImportFinder.find("ralia.zip") }.getOrNull() }
    fun take(open: () -> InputStream) {
        working = true
        scope.launch {
            val result = withContext(Dispatchers.IO) { runCatching { open().use { WrathppRalia.importZip(store, it) } } }
            working = false
            result.onSuccess { count = it }
            Toast.makeText(context, result.fold({ "Ralia's mod is in: $it textures. Its skins are in Wrath++ at its next Play." }, { it.message ?: "The file couldn't be read." }), Toast.LENGTH_LONG).show()
        }
    }
    val pick = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) take { context.contentResolver.openInputStream(uri) ?: throw java.io.IOException("The file couldn't be opened.") }
    }
    Dialog(onDismissRequest = onDismiss, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Column(
            Modifier.padding(24.dp).widthIn(max = 480.dp).fillMaxWidth().background(Colors.Deep).border(1.dp, Colors.Steel).padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            FrameTitle("Ralia's mod (Wrath++)", style = MaterialTheme.typography.titleLarge)
            Text(
                "Ralia's character textures on Wrath++, from your own zip of them (ralia.zip). A skin of the game's that the " +
                    "zip has a texture for takes it (the Forsaken's too), with the set's own body options; the others " +
                    "stay the game's. The undead skins are pictures of their own and keep theirs. They go into Wrath++'s game the " +
                    "next time you press Play on it, which also looks for ralia.zip in Download by itself; Remove puts the game's " +
                    "own back and stops the looking.",
                style = MaterialTheme.typography.bodyMedium, color = Colors.Mist,
            )
            Text(
                when {
                    working -> "Reading the zip…"
                    count > 0 -> "$count textures of the set are on this phone."
                    found != null -> "Not in yet. Found ${found.name} in ${found.parentFile?.name ?: "storage"}."
                    ImportFinder.mayLook() -> "Not in yet, and no ralia.zip in Download, Documents or the top of the phone's storage: pick it."
                    else -> "Not in yet. Pick the zip (the app may not look through the phone's files by itself)."
                },
                style = MaterialTheme.typography.bodyMedium, color = Colors.Text,
            )
            FlowRow(
                Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(10.dp, Alignment.End),
                verticalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                if (count > 0 && !working) FrameButton("Remove", primary = false) { confirmRemove = true }
                FrameButton("Close", primary = false, onClick = onDismiss)
                if (!working) {
                    FrameButton("Pick the zip", primary = found == null || count > 0) { pick.launch(arrayOf("*/*")) }
                    if (found != null && count == 0) FrameButton("Use ${found.name}") { val file: File = found; take { file.inputStream() } }
                }
            }
        }
    }
    if (confirmRemove) ConfirmDialog(
        title = "Remove Ralia's mod?",
        text = "Its textures are deleted from the phone, and at Wrath++'s next Play the game's own skins and underwear are back.",
        confirm = "Remove",
        onDismiss = { confirmRemove = false },
        onConfirm = {
            confirmRemove = false
            WrathppRalia.remove(store)
            count = 0
        },
    )
}
