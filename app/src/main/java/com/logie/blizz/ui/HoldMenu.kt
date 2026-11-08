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
import androidx.compose.material.icons.filled.Extension
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Storage
import androidx.compose.material.icons.filled.Tune
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.staticCompositionLocalOf
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
internal val LocalOpenModules = staticCompositionLocalOf<() -> Unit> { {} }

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
                .drawBehind { drawRect(Brush.verticalGradient(listOf(Colors.Night, Colors.Deep))); drawFrame() }
                .padding(vertical = 12.dp),
        ) {
            FrameTitle(effective.fullTitle, Modifier.padding(start = 20.dp, end = 20.dp, top = 4.dp, bottom = 8.dp), style = MaterialTheme.typography.titleMedium)
            HoldItem(Icons.Default.Tune, "Loading screen") { onDismiss(); openSplash(game) }
            if (effective.id != com.logie.blizz.d2r.D2r.GAME_ID) HoldItem(Icons.Default.Settings, "Launch options") { onDismiss(); openOptions(game) }
            if (hasAddons(effective.id)) HoldItem(Icons.Default.Extension, "Add-ons") { onDismiss(); openAddons(game) }
            if (hasModules(effective.id)) HoldItem(Icons.Default.Storage, "Modules") { onDismiss(); openModules() }
        }
    }
}

@Composable
private fun HoldItem(icon: androidx.compose.ui.graphics.vector.ImageVector, label: String, onClick: () -> Unit) {
    Row(Modifier.fillMaxWidth().clickable(onClick = onClick).padding(horizontal = 20.dp, vertical = 14.dp), verticalAlignment = Alignment.CenterVertically) {
        Icon(icon, null, tint = Colors.Gold)
        Spacer(Modifier.width(16.dp))
        Text(label, style = MaterialTheme.typography.bodyLarge, color = Colors.Text)
    }
}
