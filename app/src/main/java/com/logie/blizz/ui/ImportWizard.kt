package com.logie.blizz.ui

import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.animateContentSize
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.Icon
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
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.compose.LifecycleEventEffect
import kotlinx.coroutines.delay
import com.logie.blizz.Game
import com.logie.blizz.importer.FileValidator
import com.logie.blizz.importer.GameImportManager
import com.logie.blizz.importer.InstallerRun
import com.logie.blizz.importer.LaunchTest
import com.logie.blizz.importer.MissingInput
import com.logie.blizz.importer.Outcome
import com.logie.blizz.importer.PickKind
import com.logie.blizz.importer.Problem
import com.logie.blizz.importer.Stage

/** The five steps the wizard walks through, and which a stage belongs to. */
private val STEPS = listOf("Detect", "Acquire", "Request", "Install", "Validate")

private fun stepOf(stage: Stage): Int = when (stage) {
    Stage.NOT_INSTALLED, Stage.DETECTING -> 0
    Stage.DOWNLOADING -> 1
    Stage.WAITING_FOR_USER_FILE -> 2
    Stage.EXTRACTING, Stage.ASSEMBLING -> 3
    Stage.VALIDATING, Stage.READY, Stage.IMPORTED_UNTESTED, Stage.FAILED -> 4
}

/** What a game's import has come to, in the person's words. */
fun statusLabel(stage: Stage, outcome: Outcome?, launchTest: LaunchTest, gameId: String): String = when {
    stage == Stage.READY && launchTest == LaunchTest.FAILED -> "Launch Test Failed"
    stage == Stage.READY -> "Ready to Play"
    stage == Stage.IMPORTED_UNTESTED && launchTest == LaunchTest.WINDOW_SHOWN && (gameId == "starcraft2" || gameId == "starcraft_remastered") -> "Started under Winlator — campaign untested"
    stage == Stage.IMPORTED_UNTESTED && gameId == "wow" -> "Copied and verified — Play starts the realm and the game here"
    stage == Stage.IMPORTED_UNTESTED -> "Imported — Launch Untested"
    outcome == Outcome.MISSING_REQUIRED_FILE -> "Missing Required File"
    outcome == Outcome.UNSUPPORTED_CLIENT_VERSION -> "Unsupported Client Version"
    outcome == Outcome.LAUNCH_TEST_FAILED -> "Launch Test Failed"
    outcome == Outcome.IMPORT_INCOMPLETE || stage == Stage.FAILED -> "Import Incomplete"
    stage == Stage.WAITING_FOR_USER_FILE -> "Waiting for a file"
    else -> ""
}

/** The installation wizard over the game's page: steps, progress, the files it asks for, the result. */
@OptIn(androidx.compose.foundation.layout.ExperimentalLayoutApi::class)
@Composable
fun ImportWizard(game: Game, onDismiss: () -> Unit, onPlay: () -> Unit) {
    val context = LocalContext.current
    val states by GameImportManager.states.collectAsState()
    LaunchedEffect(game.id) { GameImportManager.refresh(context, game.id) }
    // Back from the game's screen (where the installer ran): look at what it has made.
    LifecycleEventEffect(Lifecycle.Event.ON_RESUME) { GameImportManager.refresh(context, game.id) }
    val state = states[game.id] ?: return
    // While the installer is going, look again now and then: Retry becomes "Import what it installed" when it has finished.
    val watching = state.installer is InstallerRun.Status.Waiting || state.installer is InstallerRun.Status.Installing
    LaunchedEffect(game.id, watching, state.running) {
        while (watching && !state.running) {
            delay(15_000)
            GameImportManager.refresh(context, game.id)
        }
    }
    val record = state.record
    var pickingFor by remember { mutableStateOf<String?>(null) }
    var confirmReset by remember { mutableStateOf(false) }
    var confirmRemoveCopy by remember { mutableStateOf(false) }
    var confirmDeleteExport by remember { mutableStateOf(false) }
    // The export an import read from, offered for deletion once the copy is verified and in place.
    val exportToDelete = remember(state.record.stage, state.running, confirmDeleteExport) { GameImportManager.exportSource(context, game.id) }
    val pickFile = rememberLauncherForActivityResult(OpenDocumentWithWrite()) { uri ->
        val id = pickingFor
        pickingFor = null
        if (uri != null && id != null) GameImportManager.supply(context, game.id, id, uri, tree = false)
    }
    val pickFolder = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocumentTree()) { uri ->
        val id = pickingFor
        pickingFor = null
        if (uri != null && id != null) GameImportManager.supply(context, game.id, id, uri, tree = true)
    }
    val addFolder = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocumentTree()) { uri ->
        if (uri != null) {
            GameImportManager.addSearchFolder(context, uri)
            GameImportManager.start(context, game.id)
        }
    }

    Dialog(onDismissRequest = { if (!state.running) onDismiss() }, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Column(
            Modifier
                .padding(18.dp)
                .widthIn(max = 620.dp)
                .fillMaxWidth()
                .panel()
                .padding(20.dp)
                .animateContentSize(),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                FrameTitle(game.fullTitle, Modifier.weight(1f))
                if (!state.running) CloseButton(onDismiss)
            }
            Steps(stepOf(record.stage), done = record.stage == Stage.READY || record.stage == Stage.IMPORTED_UNTESTED, failed = record.stage == Stage.FAILED)

            Column(Modifier.weight(1f, fill = false).verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                // Downloads the import makes by itself, with their sizes.
                for (source in state.autoSources) {
                    Text("↓ ${source.label} · ${FileValidator.gb(source.size)}", style = MaterialTheme.typography.bodyMedium, color = Colors.Mist)
                }
                if (state.running) {
                    val p = state.progress
                    Text(p?.label ?: "Working…", style = MaterialTheme.typography.titleMedium)
                    if (p != null && p.total > 0) {
                        val smooth by androidx.compose.animation.core.animateFloatAsState((p.done.toFloat() / p.total).coerceIn(0f, 1f), androidx.compose.animation.core.tween(400), label = "progress")
                        LinearProgressIndicator(progress = { smooth }, color = Colors.Ice, trackColor = Colors.Frost, modifier = Modifier.fillMaxWidth())
                        Text(if (p.stage == Stage.DOWNLOADING && p.label.contains("Blizzard")) "${p.done} / ${p.total} pieces" else "${FileValidator.gb(p.done)} / ${FileValidator.gb(p.total)}", style = MaterialTheme.typography.bodySmall)
                    } else {
                        LinearProgressIndicator(color = Colors.Ice, trackColor = Colors.Frost, modifier = Modifier.fillMaxWidth())
                    }
                } else if (state.missing.isNotEmpty()) {
                    for (input in state.missing) MissingInputCard(input,
                        onPick = { kind ->
                            pickingFor = input.id
                            if (kind == PickKind.FOLDER) pickFolder.launch(null) else pickFile.launch(arrayOf("*/*"))
                        },
                        onSkip = { GameImportManager.skip(context, game.id, input.id) })
                    Text(
                        "Files can also go in ${GameImportManager.importFolder(context)?.path ?: "the app's import folder"}.",
                        style = MaterialTheme.typography.bodySmall,
                    )
                } else {
                    val label = statusLabel(record.stage, record.outcome, record.launchTest, game.id)
                    if (label.isNotEmpty()) {
                        val good = record.stage == Stage.READY
                        Text(label, style = DisplayStyle.copy(fontSize = 20.sp, color = if (good) Colors.Ice else Colors.Gold, shadow = if (Look.modern) null else if (good) IceGlow else GoldShadow))
                    }
                    state.entry?.let { e ->
                        Text(e.clientVersion, style = MaterialTheme.typography.bodyMedium, color = Colors.Mist)
                    }
                    if (record.problem != null && record.problem != Problem.CANCELLED || record.message != null) {
                        record.message?.let { Text(it, style = MaterialTheme.typography.bodyLarge) }
                    }
                    Details(record.detail, state.validation?.checks?.map { Triple(it.name, it.passed, it.detail) })
                }
                // The game's own installer: where it stands, and taking its copy away.
                val installer = state.installer
                if (installer != null && !state.running) {
                    val (headline, more) = InstallerRun.describe(installer)
                    if (headline.isNotEmpty()) {
                        Column(Modifier.fillMaxWidth().then(if (Look.modern) Modifier.box() else Modifier.drawBehind { drawFrame(corner = Colors.Ice, arm = 6.dp.toPx()) }).padding(14.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                            Text(headline, style = MaterialTheme.typography.bodyLarge)
                            more?.let { Text(it, style = MaterialTheme.typography.bodyMedium, color = Colors.Mist) }
                            if (installer is InstallerRun.Status.Waiting && installer.log.isNotBlank()) Details(installer.log, null)
                            if (!confirmRemoveCopy) {
                                Text("Remove the installer's copy", style = MaterialTheme.typography.bodySmall.copy(color = Colors.Ice), modifier = Modifier.clickable { confirmRemoveCopy = true }.padding(vertical = 4.dp))
                            } else {
                                Text("Delete the installer's copied files and what it made?", style = MaterialTheme.typography.bodyMedium, color = Colors.Gold)
                                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                                    FrameButton("No", primary = false) { confirmRemoveCopy = false }
                                    FrameButton("Remove") { confirmRemoveCopy = false; GameImportManager.removeInstallerCopy(context, game.id) }
                                }
                            }
                        }
                    }
                }
                if (game.id == "diablo2" && !state.running && state.entry == null) CdKeys(game.id)
                // Warcraft III: single player needs no CD key, so none is asked for.
                if (game.id.startsWith("warcraft3") && !state.running) {
                    if (record.stage == Stage.NOT_INSTALLED && record.problem == null && state.missing.isEmpty()) {
                        // One step: both games, whole, in one place.
                        Text("Installs Reign of Chaos and The Frozen Throne together, with every campaign, from Blizzard (about 1.4 GB). Nothing to pick or enter.", style = MaterialTheme.typography.bodyLarge)
                    }
                }
            }

            // Play stands alone on top at full width; the housekeeping buttons sit below it.
            if (!state.running && !confirmReset && (record.stage == Stage.READY || record.stage == Stage.IMPORTED_UNTESTED)) {
                FrameButton("Play", Modifier.fillMaxWidth()) { onDismiss(); onPlay() }
            }
            // The buttons wrap onto a second line where they don't fit (Retry was pushed off a phone's width).
            androidx.compose.foundation.layout.FlowRow(
                Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp, Alignment.End), verticalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                // Reset, at any time but while it's working: the game's files go, its saves stay.
                val resettable = !state.running && (state.entry != null || record.stage != Stage.NOT_INSTALLED || record.problem != null || state.installer != null)
                if (resettable) {
                    if (confirmReset) {
                        Text(if (state.installer != null) "Delete the installed game and the installer's copy?" else "Delete the installed game?", style = MaterialTheme.typography.bodyMedium, color = Colors.Gold, modifier = Modifier.weight(1f))
                        FrameButton("No", primary = false) { confirmReset = false }
                        FrameButton("Reset") { confirmReset = false; GameImportManager.reset(context, game.id) }
                    } else {
                        FrameButton("Reset", primary = false) { confirmReset = true }
                    }
                }
                if (!confirmReset) when {
                    state.running -> FrameButton("Cancel", primary = false) { GameImportManager.cancel(game.id) }
                    state.missing.isNotEmpty() -> FrameButton("Search a folder", primary = false) { addFolder.launch(null) }
                    record.stage == Stage.READY || record.stage == Stage.IMPORTED_UNTESTED -> {
                        FrameButton("Repair", primary = false) { GameImportManager.start(context, game.id, repair = true) }
                        if (exportToDelete != null) {
                            if (confirmDeleteExport) {
                                FrameButton("No", primary = false) { confirmDeleteExport = false }
                                FrameButton("Delete it") {
                                    confirmDeleteExport = false
                                    // A folder of thousands of files: deleted off the main thread.
                                    val app = context.applicationContext
                                    Thread {
                                        val ok = GameImportManager.deleteExport(app, game.id)
                                        android.os.Handler(android.os.Looper.getMainLooper()).post {
                                            android.widget.Toast.makeText(app, if (ok) "The export is deleted." else "It couldn't be deleted from here: delete it in the Files app.", android.widget.Toast.LENGTH_LONG).show()
                                        }
                                    }.start()
                                }
                            } else FrameButton("Delete the export", primary = false) { confirmDeleteExport = true }
                        }
                    }
                    record.stage == Stage.NOT_INSTALLED && record.problem == null -> FrameButton(if (game.id.startsWith("warcraft3")) "Auto Install" else "Auto Import") { GameImportManager.start(context, game.id) }
                    record.problem == Problem.INSTALLER_MUST_RUN || state.installer != null -> {
                        val ended = state.installer is InstallerRun.Status.Finished
                        val partial = state.installer is InstallerRun.Status.PartialCopy
                        val again = state.installer is InstallerRun.Status.Waiting
                        FrameButton("Search a folder", primary = false) { addFolder.launch(null) }
                        FrameButton(if (ended) "Run again" else "Retry", primary = false) { if (ended) GameImportManager.runInstaller(context, game.id) else GameImportManager.start(context, game.id) }
                        if (ended) FrameButton("Import what it installed") { GameImportManager.start(context, game.id) }
                        else FrameButton(if (partial) "Go on copying" else if (again) "Run again" else "Run the installer") { GameImportManager.runInstaller(context, game.id) }
                    }
                    else -> {
                        FrameButton("Search a folder", primary = false) { addFolder.launch(null) }
                        FrameButton("Retry") { GameImportManager.start(context, game.id) }
                    }
                }
            }
        }
    }
}

@Composable
private fun Steps(current: Int, done: Boolean, failed: Boolean) {
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
        STEPS.forEachIndexed { i, name ->
            val reached = i < current || (i == current && done)
            val active = i == current && !done
            val color = when {
                failed && i == current -> Colors.Gold
                reached -> Colors.Ice
                active -> Colors.Glow
                else -> Colors.Steel
            }
            val shown by androidx.compose.animation.animateColorAsState(color, androidx.compose.animation.core.tween(350), label = "step")
            Column(Modifier.weight(1f), horizontalAlignment = Alignment.CenterHorizontally) {
                Box(Modifier.fillMaxWidth().height(3.dp).background(shown))
                Spacer(Modifier.height(4.dp))
                Text(name, style = MaterialTheme.typography.bodySmall.copy(color = shown, fontSize = 11.sp), maxLines = 1)
            }
        }
    }
}

@Composable
private fun MissingInputCard(input: MissingInput, onPick: (PickKind) -> Unit, onSkip: () -> Unit) {
    Column(
        Modifier.fillMaxWidth().then(if (Look.modern) Modifier.box() else Modifier.drawBehind { drawFrame(corner = Colors.Ice, arm = 6.dp.toPx()) }).padding(14.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        Text(input.prompt, style = MaterialTheme.typography.bodyLarge)
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            if (input.kind != PickKind.FOLDER) FrameButton("Select file") { onPick(PickKind.FILE) }
            if (input.kind != PickKind.FILE) FrameButton("Select folder", primary = input.kind == PickKind.FOLDER) { onPick(PickKind.FOLDER) }
            if (input.optional) FrameButton(input.skipLabel ?: "Skip", primary = false, onClick = onSkip)
        }
    }
}

@Composable
private fun Details(detail: String?, checks: List<Triple<String, Boolean, String>>?) {
    if (detail.isNullOrBlank() && checks.isNullOrEmpty()) return
    var open by remember { mutableStateOf(false) }
    Text(if (open) "Hide details" else "Details", style = MaterialTheme.typography.bodySmall.copy(color = Colors.Ice), modifier = Modifier.clickable { open = !open }.padding(vertical = 4.dp))
    if (!open) return
    checks?.forEach { (name, passed, info) ->
        Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(if (passed) Icons.Default.Check else Icons.Default.Close, null, tint = if (passed) Colors.Ice else Colors.Gold, modifier = Modifier.size(16.dp))
            Spacer(Modifier.width(8.dp))
            Text("$name — $info", style = MaterialTheme.typography.bodySmall)
        }
    }
    if (!detail.isNullOrBlank()) {
        Text(detail, style = MaterialTheme.typography.bodySmall.copy(fontFamily = FontFamily.Monospace, fontSize = 11.sp), modifier = Modifier.fillMaxWidth().background(Color.Black.copy(alpha = 0.4f)).padding(8.dp))
    }
}

/** Diablo II's original keys: optional, never needed to play single player, kept on the phone only. */
@Composable
private fun CdKeys(gameId: String) {
    var open by remember { mutableStateOf(false) }
    var classic by remember { mutableStateOf("") }
    var expansion by remember { mutableStateOf("") }
    Text(if (open) "CD keys (optional) ▴" else "CD keys (optional) ▾", style = MaterialTheme.typography.bodySmall.copy(color = Colors.Mist), modifier = Modifier.clickable { open = !open }.padding(vertical = 4.dp))
    if (!open) return
    @Composable
    fun field(value: String, hint: String, onChange: (String) -> Unit) {
        Box(Modifier.fillMaxWidth().background(Colors.Abyss).padding(10.dp)) {
            if (value.isEmpty()) Text(hint, style = MaterialTheme.typography.bodyMedium, color = Colors.Steel)
            BasicTextField(value, { v ->
                val clean = v.uppercase().filter { it.isLetterOrDigit() }.take(26)
                onChange(clean)
            }, singleLine = true, textStyle = MaterialTheme.typography.bodyMedium, cursorBrush = SolidColor(Colors.Ice), modifier = Modifier.fillMaxWidth())
        }
    }
    field(classic, "Diablo II key (16 or 26 characters)") { classic = it; GameImportManager.setKeys(gameId, classic.takeIf { k -> k.length == 16 || k.length == 26 }, expansion.takeIf { k -> k.length == 26 }, null) }
    field(expansion, "Lord of Destruction key (26 characters)") { expansion = it; GameImportManager.setKeys(gameId, classic.takeIf { k -> k.length == 16 || k.length == 26 }, expansion.takeIf { k -> k.length == 26 }, null) }
}

/**
 * The file picker, asking for write access too (and to keep it): the file picked for an import is deleted once the game is in
 * ([com.logie.blizz.importer.SourceCleanup]), which a document picked with read access alone can't be.
 */
class OpenDocumentWithWrite : ActivityResultContracts.OpenDocument() {
    override fun createIntent(context: android.content.Context, input: Array<String>): android.content.Intent =
        super.createIntent(context, input).addFlags(
            android.content.Intent.FLAG_GRANT_READ_URI_PERMISSION or android.content.Intent.FLAG_GRANT_WRITE_URI_PERMISSION or
                android.content.Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION,
        )
}
