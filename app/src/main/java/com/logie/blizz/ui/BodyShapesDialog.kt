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
import com.logie.blizz.wrathpp.WrathppBody
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File
import java.io.InputStream

/**
 * Body shapes on Wrath++ (World of Warcraft's boxes, held): the zip of them ([WrathppBody]: yours, never in the app) is
 * looked for as `wrathpp-body.zip` (or `body.zip`) where downloads are, or picked by hand; the preset chosen here is the
 * women's shape in Wrath++'s game from its next Play, As drawn (or Remove) puts the looks' own back.
 */
@OptIn(ExperimentalLayoutApi::class)
@Composable
internal fun BodyShapesDialog(onDismiss: () -> Unit) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val store = remember { WrathppBody.store(context) }
    var installed by remember { mutableStateOf(WrathppBody.installed(store)) }
    var choice by remember { mutableStateOf(WrathppBody.chosen(store)) }
    var working by remember { mutableStateOf(false) }
    var confirmRemove by remember { mutableStateOf(false) }
    val found = remember { runCatching { ImportFinder.find(*WrathppBody.NAMES) }.getOrNull() }
    fun take(open: () -> InputStream) {
        working = true
        scope.launch {
            val result = withContext(Dispatchers.IO) { runCatching { open().use { WrathppBody.importZip(store, it) } } }
            working = false
            installed = WrathppBody.installed(store)
            choice = WrathppBody.chosen(store)
            Toast.makeText(context, result.fold({ "The body shapes are in ($it models). They're in Wrath++ at its next Play." }, { it.message ?: "The file couldn't be read." }), Toast.LENGTH_LONG).show()
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
            FrameTitle("Body shapes (Wrath++)", style = MaterialTheme.typography.titleLarge)
            Text(
                "Body presets for the women of Wrath++, from your own zip of them (wrathpp-body.zip). The preset you choose " +
                    "is every woman's shape of the races the zip has, in the game from its next Play, which also looks for the " +
                    "zip in Download by itself. As drawn or Remove puts the game's own back.",
                style = MaterialTheme.typography.bodyMedium, color = Colors.Mist,
            )
            Text(
                when {
                    working -> "Reading the zip…"
                    installed -> "In: ${WrathppBody.races(store).joinToString(", ")}. Shape: $choice."
                    found != null -> "Not in yet. Found ${found.name} in ${found.parentFile?.name ?: "storage"}."
                    ImportFinder.mayLook() -> "Not in yet, and no wrathpp-body.zip in Download, Documents or the top of the phone's storage: pick it."
                    else -> "Not in yet. Pick the zip (the app may not look through the phone's files by itself)."
                },
                style = MaterialTheme.typography.bodyMedium, color = Colors.Text,
            )
            if (installed && !working) {
                FlowRow(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    for (preset in listOf(WrathppBody.AS_DRAWN) + WrathppBody.presets(store)) {
                        FrameButton(preset, primary = preset == choice) { WrathppBody.choose(store, preset); choice = preset }
                    }
                }
            }
            FlowRow(
                Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(10.dp, Alignment.End),
                verticalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                if (installed && !working) FrameButton("Remove", primary = false) { confirmRemove = true }
                FrameButton("Close", primary = false, onClick = onDismiss)
                if (!working) {
                    FrameButton("Pick the zip", primary = found == null || installed) { pick.launch(arrayOf("*/*")) }
                    if (found != null && !installed) FrameButton("Use ${found.name}") { val file: File = found; take { file.inputStream() } }
                }
            }
        }
    }
    if (confirmRemove) ConfirmDialog(
        title = "Remove the body shapes?",
        text = "They're deleted from the phone, and at Wrath++'s next Play the game's own shapes are back.",
        confirm = "Remove",
        onDismiss = { confirmRemove = false },
        onConfirm = {
            confirmRemove = false
            WrathppBody.remove(store)
            installed = false
            choice = WrathppBody.AS_DRAWN
        },
    )
}
