package com.logie.blizz.ui

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Apps
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.Build
import androidx.compose.material.icons.filled.DeleteForever
import androidx.compose.material.icons.filled.Extension
import androidx.compose.material.icons.filled.Face
import androidx.compose.material.icons.filled.Image
import androidx.compose.material.icons.filled.Mouse
import androidx.compose.material.icons.filled.RestartAlt
import androidx.compose.material.icons.filled.MusicNote
import androidx.compose.material.icons.filled.PersonSearch
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Storage
import androidx.compose.material.icons.filled.Tune
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import com.logie.blizz.Game

/** What a version's hold menu opens (Launcher hosts the screens): its launch options, its add-ons, the modules of its realm. */
internal val LocalOpenOptions = staticCompositionLocalOf<(Game) -> Unit> { {} }
internal val LocalOpenAddons = staticCompositionLocalOf<(Game) -> Unit> { {} }
/** Opens the Character Porter (World of Warcraft's boxes). */
internal val LocalOpenPorter = staticCompositionLocalOf<() -> Unit> { {} }
internal val LocalOpenModules = staticCompositionLocalOf<() -> Unit> { {} }
internal val LocalOpenMusic = staticCompositionLocalOf<(Game) -> Unit> { {} }
internal val LocalOpenControls = staticCompositionLocalOf<(Game) -> Unit> { {} }
internal val LocalChooseApp = staticCompositionLocalOf<(Game) -> Unit> { {} }

/** The versions of World of Warcraft that have add-ons (their client's), and the one with modules (Wrath+'s realm). */
internal fun hasAddons(gameId: String) = gameId == "wow" || gameId == "wow_legion" || gameId == "wow_octowow"
internal fun hasModules(gameId: String) = gameId == "wow"

/** The menu of a box held on the shelf or its page: its loading screen, launch options and, for World of Warcraft, add-ons and modules. */
@Composable
internal fun HoldMenu(game: Game, onDismiss: () -> Unit) {
    val effective = Variants.effective(game)
    val openSplash = LocalOpenSplash.current
    val openOptions = LocalOpenOptions.current
    val openAddons = LocalOpenAddons.current
    val openModules = LocalOpenModules.current
    Dialog(onDismissRequest = onDismiss) {
        Column(
            Modifier.widthIn(max = 360.dp).fillMaxWidth()
                .panel()
                .padding(vertical = 12.dp),
        ) {
            FrameTitle(effective.fullTitle, Modifier.padding(start = 20.dp, end = 20.dp, top = 4.dp, bottom = 8.dp), style = MaterialTheme.typography.titleMedium)
            val openControls = LocalOpenControls.current
            val chooseApp = LocalChooseApp.current
            val openWizard = LocalOpenWizard.current
            val importable = com.logie.blizz.importer.GameImportManager.importable(effective.id)
            val isWow = effective.id == "wow" || effective.id.startsWith("wow_")
            // Warcraft III plays in Warsmash: Winlator's launch options and touch controls aren't its.
            val warsmash = effective.id.startsWith("warcraft3")
            if (effective.id != com.logie.blizz.d2r.D2r.GAME_ID && !warsmash) HoldItem(Icons.Default.Settings, "Launch options") { onDismiss(); openOptions(game) }
            if (!isWow && effective.id != com.logie.blizz.d2r.D2r.GAME_ID && !warsmash) HoldItem(Icons.Default.Mouse, "Controls") { onDismiss(); openControls(game) }
            if (hasAddons(effective.id)) HoldItem(Icons.Default.Extension, "Add-ons") { onDismiss(); openAddons(game) }
            if (hasModules(effective.id)) HoldItem(Icons.Default.Storage, "Modules") { onDismiss(); openModules() }
            val openPorter = LocalOpenPorter.current
            if (isWow && effective.id != "wow_forever") HoldItem(Icons.Default.PersonSearch, "Character Porter") { onDismiss(); openPorter() }
            // Wrath++: the undead skins you import (UndeadSkinsDialog), new skins under its creator's Undead switch.
            var undeadSkins by remember { mutableStateOf(false) }
            if (isWow && effective.id != "wow_forever" && effective.id != "wow_legion" && effective.id != "wow_octowow") {
                HoldItem(Icons.Default.Face, "Undead skins (Wrath++)") { undeadSkins = true }
            }
            if (undeadSkins) UndeadSkinsDialog { undeadSkins = false; onDismiss() }
            // Wrath++: Ralia's mod from your zip of it (RaliaDialog: looked for as ralia.zip, or picked).
            var ralia by remember { mutableStateOf(false) }
            if (isWow && effective.id != "wow_forever" && effective.id != "wow_legion" && effective.id != "wow_octowow") {
                HoldItem(Icons.Default.Face, "Ralia's mod (Wrath++)") { ralia = true }
            }
            if (ralia) RaliaDialog { ralia = false; onDismiss() }
            // Warcraft III in Warsmash: Classic+, the remade models and textures (ClassicPlusDialog).
            var classicPlus by remember { mutableStateOf(false) }
            if (warsmash) HoldItem(Icons.Default.AutoAwesome, "Classic+ models") { classicPlus = true }
            if (classicPlus) ClassicPlusDialog { classicPlus = false; onDismiss() }
            HoldItem(Icons.Default.Image, "Art") { onDismiss(); openSplash(game) }
            val openMusic = LocalOpenMusic.current
            HoldItem(Icons.Default.MusicNote, "Music") { onDismiss(); openMusic(game) }
            if (importable) HoldItem(Icons.Default.Build, "Install & repair") { onDismiss(); openWizard(effective) }
            else HoldItem(Icons.Default.Apps, "App") { onDismiss(); chooseApp(game) }
            val context = LocalContext.current
            if (effective.id == "wow_forever") {
                // World of Warcraft: Forever — repair, reset the realm only, or wipe everything and start from zero.
                var confirmRepair by remember { mutableStateOf(false) }
                var confirmRealm by remember { mutableStateOf(false) }
                var confirmNuke by remember { mutableStateOf(false) }
                HoldItem(Icons.Default.Build, "Repair installation") { confirmRepair = true }
                HoldItem(Icons.Default.RestartAlt, "Reset realm") { confirmRealm = true }
                HoldItem(Icons.Default.DeleteForever, "Delete everything (start over)") { confirmNuke = true }
                if (confirmRepair) ConfirmDialog(
                    title = "Repair installation?",
                    text = "Keeps your characters, the realm and the game client, but rebuilds the .NET runtime and the launcher's settings on the next Play and removes the launcher file so you pick it again. Use it if a Play runs old files.",
                    confirm = "Repair",
                    onDismiss = { confirmRepair = false },
                    onConfirm = { confirmRepair = false; onDismiss(); com.logie.blizz.forever.ForeverPlay.repair(context) },
                )
                if (confirmRealm) ConfirmDialog(
                    title = "Reset the realm?",
                    text = "The realm (its server, characters and map data) is deleted and downloaded again on the next Play. The game client stays.",
                    confirm = "Reset",
                    onDismiss = { confirmRealm = false },
                    onConfirm = { confirmRealm = false; onDismiss(); com.logie.blizz.forever.ForeverPlay.reset(context, client = false) },
                )
                if (confirmNuke) ConfirmDialog(
                    title = "Delete everything?",
                    text = "Deletes EVERYTHING for World of Warcraft: Forever and starts from zero: the realm server, your characters, the map data, the game client (${com.logie.blizz.forever.ForeverPlay.CLIENT_SIZE_GB} GB) and everything the app set up in its Windows container (the .NET runtime, the launcher's settings, an old browser runtime a previous version left). The next Play installs it all again. This can't be undone.",
                    confirm = "Delete everything",
                    onDismiss = { confirmNuke = false },
                    onConfirm = { confirmNuke = false; onDismiss(); com.logie.blizz.forever.ForeverPlay.nuke(context) },
                )
            } else if (importable) {
                // Reset, on every other game: it is deleted and installed again from the start (saves stay).
                var confirm by remember { mutableStateOf(false) }
                HoldItem(Icons.Default.RestartAlt, "Reset") { confirm = true }
                if (confirm) ConfirmDialog(
                    title = "Reset ${effective.fullTitle}?",
                    text = "The game is deleted and installed again from the start. Your saves stay.",
                    confirm = "Reset",
                    onDismiss = { confirm = false },
                    onConfirm = {
                        confirm = false; onDismiss()
                        com.logie.blizz.importer.GameImportManager.reinstall(context, effective.id); openWizard(effective)
                    },
                )
            }
        }
    }
}

@Composable
private fun HoldItem(icon: androidx.compose.ui.graphics.vector.ImageVector, label: String, onClick: () -> Unit) {
    Row(Modifier.fillMaxWidth().clickable(onClick = onClick).padding(horizontal = 20.dp, vertical = 14.dp), verticalAlignment = Alignment.CenterVertically) {
        Icon(icon, null, tint = if (Look.modern) Modern.Muted else Colors.Gold)
        Spacer(Modifier.width(16.dp))
        Text(label, style = MaterialTheme.typography.bodyLarge, color = Colors.Text)
    }
}
