package com.logie.blizz.ui

import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
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
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.logie.blizz.wrathpp.ImportFinder
import com.logie.blizz.wrathpp.WrathppBody
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File
import java.io.InputStream

/**
 * Wrath++'s settings page: the body options package ([WrathppBody]: yours, never in the app), looked for as
 * `wrathpp-body.zip` (or `body.zip`) where downloads are, or picked by hand. The options themselves are each woman's,
 * on the creator's Body tab; this only says whether the package is in, and takes it in or out.
 */
@OptIn(ExperimentalLayoutApi::class)
@Composable
internal fun WrathppBodyCard() {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val store = remember { WrathppBody.store(context) }
    var installed by remember { mutableStateOf(WrathppBody.installed(store)) }
    var working by remember { mutableStateOf(false) }
    var confirmRemove by remember { mutableStateOf(false) }
    val found = remember { runCatching { ImportFinder.find(*WrathppBody.NAMES) }.getOrNull() }
    fun take(open: () -> InputStream) {
        working = true
        scope.launch {
            val result = withContext(Dispatchers.IO) { runCatching { open().use { WrathppBody.importZip(store, it) } } }
            working = false
            installed = WrathppBody.installed(store)
            Toast.makeText(context, result.fold({ "The body options are in ($it models). They're in Wrath++ at its next Play." }, { it.message ?: "The file couldn't be read." }), Toast.LENGTH_LONG).show()
        }
    }
    val pick = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) take { context.contentResolver.openInputStream(uri) ?: throw java.io.IOException("The file couldn't be opened.") }
    }
    SettingCard("Body options") {
        Text(
            "The women's body options in Wrath++'s creator, on the Body tab: chosen for each character, kept by the realm and " +
                "seen in the game. They come from your own package (wrathpp-body.zip), taken in at the next Play when it is in " +
                "Download.",
            style = MaterialTheme.typography.bodySmall, color = Colors.Mist,
        )
        Text(
            when {
                working -> "Reading the package…"
                installed -> "In: ${WrathppBody.races(store).joinToString(", ")}."
                WrathppBody.older(store) -> "The package in is an older one (one shape for every woman): pick the new one. Until then every woman is as drawn."
                found != null -> "Not in yet. Found ${found.name} in ${found.parentFile?.name ?: "storage"}."
                ImportFinder.mayLook() -> "Not in yet, and no wrathpp-body.zip in Download, Documents or the top of the phone's storage: pick it."
                else -> "Not in yet. Pick the package (the app may not look through the phone's files by itself)."
            },
            style = MaterialTheme.typography.bodyMedium, color = Colors.Text,
        )
        if (!working) {
            FlowRow(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                if (found != null && !installed) FrameButton("Use ${found.name}") { val file: File = found; take { file.inputStream() } }
                FrameButton(if (installed) "Pick another" else "Pick the package", primary = found == null && !installed) { pick.launch(arrayOf("*/*")) }
                if (installed || WrathppBody.older(store)) FrameButton("Remove", primary = false) { confirmRemove = true }
            }
        }
    }
    if (confirmRemove) ConfirmDialog(
        title = "Remove the body options?",
        text = "The package is deleted from the phone, and at Wrath++'s next Play every woman is as drawn again. The choices " +
            "made in the creator stay with the characters, for a package put in again.",
        confirm = "Remove",
        onDismiss = { confirmRemove = false },
        onConfirm = {
            confirmRemove = false
            WrathppBody.remove(store)
            installed = false
        },
    )
}
