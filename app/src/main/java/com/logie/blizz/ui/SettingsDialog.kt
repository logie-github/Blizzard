package com.logie.blizz.ui

import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ChevronRight
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import kotlinx.coroutines.launch
import com.logie.blizz.Game
import com.logie.blizz.Games
import com.logie.blizz.game.GameSettings
import com.logie.blizz.music.MusicCatalog
import com.logie.blizz.music.MusicCustom
import com.logie.blizz.music.MusicDownloads
import com.logie.blizz.music.MusicPlayer

/**
 * The launcher's settings, opened by holding the Blizzard logo. Two pages: **Launcher** (layout, touch, music, tests)
 * and **Games**, where every version of every game has its own settings ([GameSettingsDialog]): Warcraft III's
 * Reign of Chaos and The Frozen Throne apart, World of Warcraft's Wrath+, Legion, OctoWoW and Forever apart.
 */
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun SettingsDialog(onDismiss: () -> Unit) {
    var page by remember { mutableStateOf(0) }
    var gameOpen by remember { mutableStateOf<Game?>(null) }
    Dialog(onDismissRequest = onDismiss, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Column(
            Modifier.padding(14.dp).widthIn(max = 600.dp).fillMaxWidth().heightIn(max = 760.dp)
                .panel(),
        ) {
            Row(Modifier.fillMaxWidth().padding(start = 20.dp, end = 8.dp, top = 14.dp), verticalAlignment = Alignment.CenterVertically) {
                FrameTitle("Settings", Modifier.weight(1f))
                CloseButton(onDismiss)
            }
            Row(Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 8.dp), horizontalArrangement = Arrangement.spacedBy(22.dp)) {
                Tab("Launcher", page == 0) { page = 0 }
                Tab("Games", page == 1) { page = 1 }
            }
            Box(Modifier.fillMaxWidth().height(1.dp).background(Colors.Steel.copy(alpha = 0.6f)))
            Column(
                Modifier.weight(1f, fill = false).verticalScroll(rememberScrollState()).padding(horizontal = 18.dp, vertical = 16.dp),
                verticalArrangement = Arrangement.spacedBy(14.dp),
            ) {
                if (page == 0) LauncherPage(onDismiss) else GamesPage { gameOpen = it }
            }
        }
    }
    gameOpen?.let { GameSettingsDialog(it, onDismiss = { gameOpen = null }) }
}

@Composable
private fun Tab(text: String, on: Boolean, onClick: () -> Unit) {
    if (Look.modern) {
        val color by androidx.compose.animation.animateColorAsState(if (on) Modern.Text else Modern.Muted, label = "tab")
        Column(Modifier.clickable(onClick = onClick).padding(vertical = 6.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            Text(text, style = MaterialTheme.typography.titleMedium.copy(color = color))
            Spacer(Modifier.size(6.dp))
            Box(Modifier.size(width = 28.dp, height = 3.dp).clip(androidx.compose.foundation.shape.CircleShape).background(if (on) Modern.Accent else Color.Transparent))
        }
        return
    }
    Column(Modifier.clickable(onClick = onClick).padding(vertical = 6.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Text(text.uppercase(), style = DisplayStyle.copy(fontSize = 15.sp, color = if (on) Colors.Gold else Colors.Mist, letterSpacing = 0.16.sp))
        Spacer(Modifier.size(5.dp))
        Box(Modifier.size(width = 34.dp, height = 2.dp).background(if (on) Colors.Gold else Color.Transparent))
    }
}

/** A titled panel: a hairline-framed block, its title in gold. */
@Composable
internal fun SettingCard(title: String?, content: @Composable () -> Unit) {
    if (Look.modern) {
        Column(Modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            title?.let { SectionLabel(it, Modifier.padding(start = 4.dp)) }
            Column(
                Modifier.fillMaxWidth().clip(androidx.compose.foundation.shape.RoundedCornerShape(Modern.Corner))
                    .background(Color.White.copy(alpha = 0.04f)).border(1.dp, Modern.Outline, androidx.compose.foundation.shape.RoundedCornerShape(Modern.Corner))
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) { content() }
        }
        return
    }
    Column(
        Modifier.fillMaxWidth().background(Colors.Abyss.copy(alpha = 0.55f)).border(1.dp, Colors.Steel.copy(alpha = 0.7f)).padding(14.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        title?.let { Text(it.uppercase(), style = DisplayStyle.copy(fontSize = 13.sp, color = Colors.Gold, letterSpacing = 0.18.sp)) }
        content()
    }
}

/** One choice of a few, side by side; the chosen one lit. */
@Composable
internal fun <T> Segmented(options: List<Pair<String, T>>, selected: T, onSelect: (T) -> Unit) {
    if (Look.modern) { PillSegmented(options, selected, onSelect = onSelect); return }
    Row(Modifier.fillMaxWidth().border(1.dp, Colors.Steel)) {
        options.forEachIndexed { index, (label, value) ->
            val on = value == selected
            val fill by androidx.compose.animation.animateColorAsState(if (on) Colors.Frost else Color.Transparent, label = "segment")
            Box(
                Modifier.weight(1f).background(fill).clickable { onSelect(value) }.padding(vertical = 11.dp),
                contentAlignment = Alignment.Center,
            ) {
                Text(label, style = MaterialTheme.typography.bodyMedium.copy(color = if (on) Colors.Glow else Colors.Mist), maxLines = 1)
            }
            if (index < options.lastIndex) Box(Modifier.size(width = 1.dp, height = 40.dp).background(Colors.Steel))
        }
    }
}

@Composable
internal fun ToggleRow(label: String, checked: Boolean, onChange: (Boolean) -> Unit) {
    Row(Modifier.fillMaxWidth().clickable { onChange(!checked) }, verticalAlignment = Alignment.CenterVertically) {
        Text(label, style = MaterialTheme.typography.bodyLarge, color = Colors.Text, modifier = Modifier.weight(1f))
        Switch(
            checked, onChange,
            colors = if (Look.modern) SwitchDefaults.colors(checkedThumbColor = Color.White, checkedTrackColor = Modern.Accent, uncheckedThumbColor = Modern.Muted, uncheckedTrackColor = Modern.SurfaceTop, uncheckedBorderColor = Modern.OutlineStrong)
                else SwitchDefaults.colors(checkedThumbColor = Colors.Glow, checkedTrackColor = Colors.Ice.copy(alpha = 0.55f), uncheckedThumbColor = Colors.Mist, uncheckedTrackColor = Colors.Frost, uncheckedBorderColor = Colors.Steel),
        )
    }
}

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun LauncherPage(onDismiss: () -> Unit) {
    val context = LocalContext.current
    var vibration by remember { mutableStateOf(GameSettings.vibration(context)) }

    SettingCard("Touch") {
        ToggleRow("Vibration", vibration) { vibration = it; GameSettings.setVibration(context, it) }
    }

    SettingCard("Music") {
        val musicOn by MusicPlayer.enabled.collectAsState()
        val musicVolume by MusicPlayer.volume.collectAsState()
        val download by MusicDownloads.state.collectAsState()
        ToggleRow("Play music", musicOn) { MusicPlayer.setEnabled(context, it) }
        Segmented(listOf("Low" to 0.3f, "Medium" to 0.6f, "High" to 1f), listOf(0.3f, 0.6f, 1f).minByOrNull { kotlin.math.abs(it - musicVolume) }!!) { MusicPlayer.setVolume(context, it) }
        val store = remember(download) { MusicDownloads.store(context) }
        val have = MusicCatalog.tracks.count { store.has(it.key) }
        val total = MusicCatalog.tracks.size
        Text(
            when (val d = download) {
                is MusicDownloads.State.Running -> "Downloading ${d.done + 1} of ${d.total}: ${d.current}"
                is MusicDownloads.State.Finished ->
                    if (d.failed.isEmpty()) "$have of $total tracks on the phone"
                    else "$have of $total tracks on the phone. Not downloaded: ${d.failed.joinToString("; ")}"
                else -> "$have of $total tracks on the phone"
            },
            style = MaterialTheme.typography.bodySmall, color = Colors.Mist,
        )
        if (download !is MusicDownloads.State.Running && have < total) FrameButton("Download music", primary = false, modifier = Modifier.fillMaxWidth()) { MusicDownloads.start(context) }
    }

    SettingCard("SteamGridDB") { SteamGridKeyCard() }

    SettingCard("Imports") {
        var deleteSources by remember { mutableStateOf(GameSettings.deleteSources(context)) }
        ToggleRow("Delete the files I picked after a successful import", deleteSources) { deleteSources = it; GameSettings.setDeleteSources(context, it) }
        Text("Only files, never a folder, and never your console keys.", style = MaterialTheme.typography.bodySmall, color = Colors.Mist)
        // What imports left in the app's storage (unpacked archives, installer copies, kept downloads): cleared after each import, and here.
        var left by remember { mutableStateOf<Long?>(null) }
        var freed by remember { mutableStateOf<Long?>(null) }
        androidx.compose.runtime.LaunchedEffect(freed) { left = kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) { com.logie.blizz.importer.GameImportManager.leftoverBytes(context) } }
        val scope = androidx.compose.runtime.rememberCoroutineScope()
        val mb = (left ?: 0L) / (1024 * 1024)
        Text(
            when {
                freed != null -> "Freed ${freed!! / (1024 * 1024)} MB."
                left == null -> "Looking for leftovers…"
                left == 0L -> "No leftovers from imports."
                else -> "$mb MB of leftovers from imports."
            },
            style = MaterialTheme.typography.bodyMedium, color = if (freed != null) Colors.Ice else Colors.Text,
        )
        if ((left ?: 0L) > 0L) FrameButton("Free the space", primary = false, modifier = Modifier.fillMaxWidth()) {
            scope.launch { freed = kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) { com.logie.blizz.importer.GameImportManager.freeAllLeftovers(context) } }
        }
    }

    SettingCard("Maintenance") {
        FrameButton("Run the launch test", primary = false, modifier = Modifier.fillMaxWidth()) { com.logie.blizz.selftest.SelfTest.start(context); onDismiss() }
    }
}

@OptIn(ExperimentalLayoutApi::class)
/** The person's SteamGridDB key: with it, the Art screen browses a game's pictures on steamgriddb.com instead of asking for a file. */
@Composable
private fun SteamGridKeyCard() {
    val context = LocalContext.current
    val scope = androidx.compose.runtime.rememberCoroutineScope()
    var saved by remember { mutableStateOf(com.logie.blizz.steamgrid.SteamGrid.key(context)) }
    var text by remember { mutableStateOf("") }
    var status by remember { mutableStateOf<String?>(null) }
    var checking by remember { mutableStateOf(false) }
    Text(
        if (saved != null) "Connected: the Art screen shows SteamGridDB's pictures for each game." else "Not connected. Art asks for a file on the phone.",
        style = MaterialTheme.typography.bodyMedium, color = if (saved != null) Colors.Ice else Colors.Mist,
    )
    androidx.compose.material3.OutlinedTextField(
        value = text, onValueChange = { text = it }, singleLine = true, modifier = Modifier.fillMaxWidth(),
        label = { Text(if (saved != null) "Replace the key" else "API key", color = Colors.Mist) },
        visualTransformation = androidx.compose.ui.text.input.PasswordVisualTransformation(),
        textStyle = MaterialTheme.typography.bodyLarge,
        keyboardOptions = androidx.compose.foundation.text.KeyboardOptions(keyboardType = androidx.compose.ui.text.input.KeyboardType.Password, autoCorrectEnabled = false),
        colors = androidx.compose.material3.OutlinedTextFieldDefaults.colors(
            focusedTextColor = Colors.Text, unfocusedTextColor = Colors.Text, focusedBorderColor = Colors.Ice, unfocusedBorderColor = Colors.Steel,
            cursorColor = Colors.Ice, focusedContainerColor = Colors.Abyss.copy(alpha = 0.55f), unfocusedContainerColor = Colors.Abyss.copy(alpha = 0.55f),
        ),
    )
    status?.let { Text(it, style = MaterialTheme.typography.bodySmall, color = if (it.startsWith("Connected")) Colors.Ice else Colors.Gold) }
    FlowRow(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        FrameButton(if (checking) "Checking…" else "Save", primary = text.isNotBlank()) {
            if (text.isBlank() || checking) return@FrameButton
            val key = text.trim()
            checking = true; status = null
            scope.launch {
                // Checked with the site before it is kept.
                runCatching { kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) { com.logie.blizz.steamgrid.SteamGrid.search(key, "Diablo") } }
                    .onSuccess { com.logie.blizz.steamgrid.SteamGrid.setKey(context, key); saved = key; text = ""; status = "Connected." }
                    .onFailure { status = it.message ?: "Couldn't reach SteamGridDB." }
                checking = false
            }
        }
        if (saved != null) FrameButton("Remove", primary = false) { com.logie.blizz.steamgrid.SteamGrid.clearKey(context); saved = null; status = "Removed." }
    }
    Text(
        "To get a key: steamgriddb.com, sign in, your name at the top right → Preferences → API → Generate API Key.",
        style = MaterialTheme.typography.bodySmall, color = Colors.Mist,
    )
}

/** Every version of every game, one row each: its box art, its name and what is set for it. */
@Composable
private fun GamesPage(onOpen: (Game) -> Unit) {
    Text("Each version has its own box art, loading screen and music.", style = MaterialTheme.typography.bodySmall, color = Colors.Mist)
    for (base in Games.all) {
        val versions = listOf(base) + base.variants
        SettingCard(if (versions.size > 1) base.title else null) {
            for (version in versions) GameRow(version, label = if (versions.size > 1) (version.variantLabel ?: version.fullTitle) else null) { onOpen(version) }
        }
    }
}

@Composable
private fun GameRow(game: Game, label: String?, onClick: () -> Unit) {
    val context = LocalContext.current
    val tiles by TileSettings.state.collectAsState()
    val splashes by com.logie.blizz.game.Splashes.version.collectAsState()
    val customMusic by MusicCustom.version.collectAsState()
    val art = remember(game.id, tiles.artVersion) { TileSettings.artFile(context, game.id, false) != null }
    val loading = remember(game.id, splashes) { com.logie.blizz.game.Splashes.file(context, game.id, com.logie.blizz.game.Splashes.Kind.BACKGROUND) != null }
    val music = remember(game.id, customMusic) { MusicCustom.file(context, game.id) != null }
    val own = listOfNotNull("art".takeIf { art }, "loading screen".takeIf { loading }, "music".takeIf { music })
    Row(Modifier.fillMaxWidth().clickable(onClick = onClick), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(14.dp)) {
        Image(boxArtOf(game), null, Modifier.width(46.dp).aspectRatio(2f / 3f).border(1.dp, Colors.Steel), contentScale = ContentScale.Crop)
        Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
            Text(label ?: game.fullTitle, style = MaterialTheme.typography.titleMedium, color = Colors.Text)
            Text(if (own.isEmpty()) "Original art and music" else "Your own: ${own.joinToString(", ")}", style = MaterialTheme.typography.bodySmall, color = if (own.isEmpty()) Colors.Mist else Colors.Ice)
        }
        Icon(Icons.Default.ChevronRight, null, tint = Colors.Mist)
    }
}

/** One version's settings: its box art, its loading screen and its music, and its launch options and controls. */
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun GameSettingsDialog(game: Game, onDismiss: () -> Unit) {
    val context = LocalContext.current
    val tiles by TileSettings.state.collectAsState()
    val customMusic by MusicCustom.version.collectAsState()
    var splashOpen by remember { mutableStateOf(false) }
    var optionsOpen by remember { mutableStateOf(false) }
    var controlsOpen by remember { mutableStateOf(false) }
    var addonsOpen by remember { mutableStateOf(false) }
    var modulesOpen by remember { mutableStateOf(false) }
    var message by remember { mutableStateOf<String?>(null) }
    val pickArt = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) message = if (TileSettings.setArt(context, game.id, false, uri)) null else "That picture couldn't be read."
    }
    val pickMusic = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) message = if (MusicCustom.set(context, game.id, uri)) null else "That isn't an audio file this app can play."
    }
    val hasArt = remember(game.id, tiles.artVersion) { TileSettings.artFile(context, game.id, false) != null }
    val ownMusic = remember(game.id, customMusic) { MusicCustom.file(context, game.id) != null }
    val trackLabel = MusicCatalog.track(MusicCatalog.keyFor(game.id))?.label
    Dialog(onDismissRequest = onDismiss, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Column(
            Modifier.padding(14.dp).widthIn(max = 560.dp).fillMaxWidth().heightIn(max = 760.dp)
                .panel(),
        ) {
            Row(Modifier.fillMaxWidth().padding(start = 20.dp, end = 8.dp, top = 14.dp), verticalAlignment = Alignment.CenterVertically) {
                FrameTitle(game.fullTitle, Modifier.weight(1f), style = MaterialTheme.typography.titleLarge)
                CloseButton(onDismiss)
            }
            Column(Modifier.weight(1f, fill = false).verticalScroll(rememberScrollState()).padding(18.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                message?.let { Text(it, style = MaterialTheme.typography.bodyMedium, color = Colors.Gold) }
                SettingCard("Box art") {
                    Row(horizontalArrangement = Arrangement.spacedBy(16.dp), verticalAlignment = Alignment.CenterVertically) {
                        Image(boxArtOf(game), null, Modifier.width(96.dp).aspectRatio(2f / 3f).border(1.dp, Colors.Steel), contentScale = ContentScale.Crop)
                        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            Text(if (hasArt) "Your picture" else "The original", style = MaterialTheme.typography.bodyMedium, color = Colors.Mist)
                            FrameButton("Choose", primary = false) { pickArt.launch(arrayOf("image/*")) }
                            if (hasArt) FrameButton("Original", primary = false) { TileSettings.clearArt(context, game.id, false) }
                        }
                    }
                }
                SettingCard("Loading screen") {
                    Text("The picture and logo shown while the game starts.", style = MaterialTheme.typography.bodySmall, color = Colors.Mist)
                    FrameButton("Edit", primary = false, modifier = Modifier.fillMaxWidth()) { splashOpen = true }
                }
                SettingCard("Music") {
                    Text(if (ownMusic) "Your song plays on this page." else (trackLabel ?: "No track for this game."), style = MaterialTheme.typography.bodyMedium, color = if (ownMusic) Colors.Ice else Colors.Mist)
                    FlowRow(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        FrameButton("Choose song", primary = false) { pickMusic.launch(arrayOf("audio/*")) }
                        if (ownMusic) FrameButton("Original", primary = false) { MusicCustom.clear(context, game.id) }
                    }
                }
                // Forever's offline realm makes this account at every start (forever@forever.local / forever unless changed here).
                if (game.id == com.logie.blizz.forever.ForeverPlay.VERSION) {
                    remember(game.id) { com.logie.blizz.forever.ForeverPlay.login(context) }
                    AutoLoginCard(game.id, "E-mail")
                    // The Forever Launcher the person supplies (it lets the client connect to the local realm): pick it once, the app keeps it.
                    val forever by com.logie.blizz.forever.ForeverPlay.state.collectAsState()
                    val hasLauncher = remember(forever) { com.logie.blizz.forever.ForeverLayout.of(context).hasLauncher() }
                    val pickLauncher = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
                        if (uri != null) com.logie.blizz.forever.ForeverPlay.importLauncher(context, uri)
                    }
                    SettingCard("Forever Launcher") {
                        Text(
                            if (hasLauncher) "The Forever Launcher is in place; the client connects through it."
                            else "The client connects to the realm through the Forever Launcher, which you supply (a .exe). Pick it once and the app runs it at every Play. It must be a native build — the current Chromium-based (Tauri/WebView2) launcher can't run under Wine on the phone.",
                            style = MaterialTheme.typography.bodySmall, color = if (hasLauncher) Colors.Ice else Colors.Mist,
                        )
                        FrameButton(if (hasLauncher) "Replace launcher" else "Choose launcher (.exe)", primary = false) {
                            pickLauncher.launch(arrayOf("application/x-msdownload", "application/octet-stream", "application/vnd.microsoft.portable-executable", "*/*"))
                        }
                    }
                    // Start over: the realm alone, or the realm and the downloaded client. Each asks first.
                    var confirmReset by remember { mutableStateOf<Boolean?>(null) }
                    SettingCard("Reset") {
                        Text(
                            "Reset realm deletes the realm server, its database (your characters) and its map data; the next Play downloads " +
                                "the server again (263 MB). Reset everything also deletes the game client (${com.logie.blizz.forever.ForeverPlay.CLIENT_SIZE_GB} GB, downloaded again on Play).",
                            style = MaterialTheme.typography.bodySmall, color = Colors.Mist,
                        )
                        FlowRow(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            FrameButton("Reset realm", primary = false) { confirmReset = false }
                            FrameButton("Reset everything", primary = false) { confirmReset = true }
                        }
                    }
                    confirmReset?.let { everything ->
                        Dialog(onDismissRequest = { confirmReset = null }) {
                            Column(Modifier.panel().padding(20.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                                Text(if (everything) "Reset everything?" else "Reset the realm?", style = MaterialTheme.typography.titleMedium)
                                Text(
                                    if (everything) "Deletes the realm, your characters and the ${com.logie.blizz.forever.ForeverPlay.CLIENT_SIZE_GB} GB game client. This can't be undone."
                                    else "Deletes the realm server, its database with your characters, and its map data. The game client stays. This can't be undone.",
                                    style = MaterialTheme.typography.bodyMedium,
                                )
                                Row(Modifier.align(Alignment.End), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                                    FrameButton("Cancel", primary = false) { confirmReset = null }
                                    FrameButton("Reset") {
                                        com.logie.blizz.forever.ForeverPlay.reset(context, client = everything)
                                        confirmReset = null
                                    }
                                }
                            }
                        }
                    }
                }
                if (game.id == "wow" || game.id == "wow_legion" || game.id == "wow_octowow") {
                    AutoLoginCard(game.id, if (game.id == "wow_legion") "E-mail" else "Account name")
                    SettingCard("Add-ons") {
                        Text("Search warperia.com's add-ons for this version, install them into its client, turn them on and off, update them.", style = MaterialTheme.typography.bodySmall, color = Colors.Mist)
                        FrameButton("Search add-ons", primary = false, modifier = Modifier.fillMaxWidth()) { addonsOpen = true }
                    }
                }
                if (game.id == "wow") {
                    SettingCard("Modules") {
                        Text(com.logie.blizz.wowmodules.modulesSummary(context), style = MaterialTheme.typography.bodySmall, color = Colors.Mist)
                        FrameButton("Search modules", primary = false, modifier = Modifier.fillMaxWidth()) { modulesOpen = true }
                    }
                }
                if (game.id == "wow") {
                    val scope = androidx.compose.runtime.rememberCoroutineScope()
                    SettingCard("Modern character creation") {
                        Text(
                            "In progress. A modern creation screen has to be written for the exact files of your client. This sends the creation screen's interface files (text only, no game art) so it can be.",
                            style = MaterialTheme.typography.bodySmall, color = Colors.Mist,
                        )
                        FrameButton("Send the creation screen's files", primary = false, modifier = Modifier.fillMaxWidth()) {
                            scope.launch {
                                message = kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
                                    val entry = com.logie.blizz.importer.GameImportManager.library(context).get("wow")
                                    val client = entry?.let { com.logie.blizz.game.WowPlay.clientFolder(java.io.File(it.installPath)) }
                                    if (client == null || !client.isDirectory) "Wrath+ isn't imported yet."
                                    else runCatching { com.logie.blizz.wowclient.ClientFilesDump.sendNow(context, client) }
                                        .fold({ "Sent $it parts (they go out when the phone is online)." }, { "Couldn't read the client's files: ${it.message}" })
                                }
                            }
                        }
                    }
                }
                if (game.id != com.logie.blizz.d2r.D2r.GAME_ID) {
                    SettingCard("Play") {
                        FlowRow(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            FrameButton("Launch options", primary = false) { optionsOpen = true }
                            if (game.id != "wow" && !game.id.startsWith("wow_")) FrameButton("Controls", primary = false) { controlsOpen = true }
                        }
                    }
                }
            }
        }
    }
    if (splashOpen) SplashDialog(game, onDismiss = { splashOpen = false })
    if (optionsOpen) GameOptionsDialog(game, onDismiss = { optionsOpen = false })
    if (controlsOpen) ControlsScreen(game, onDismiss = { controlsOpen = false })
    if (addonsOpen) WowAddonManager(game.id, onDismiss = { addonsOpen = false })
    if (modulesOpen) WowModuleManager(onDismiss = { modulesOpen = false })
}
