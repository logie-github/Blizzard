package com.logie.blizz.ui

import android.content.Context
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.foundation.shape.RoundedCornerShape
import com.logie.blizz.Game
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

/**
 * Which installation of a game its page is showing (StarCraft: the classic game, or Remastered
 * beside it): kept across launches. The page's Play, status, Controls and import wizard all act on it.
 */
object Variants {
    private const val PREFS = "variants"
    private val _selection = MutableStateFlow<Map<String, String>>(emptyMap())
    val selection: StateFlow<Map<String, String>> = _selection

    fun load(context: Context) {
        val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        _selection.value = prefs.all.mapNotNull { (k, v) -> (v as? String)?.let { k to it } }.toMap()
    }

    fun select(context: Context, base: Game, variant: Game) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().putString(base.id, variant.id).apply()
        _selection.value = _selection.value + (base.id to variant.id)
    }

    /** The installation of [game] chosen: the game itself, or one of its variants. */
    fun effective(game: Game, selection: Map<String, String> = _selection.value): Game =
        game.variants.firstOrNull { it.id == selection[game.id] } ?: game
}

/** The installation of [game] its page shows. */
@Composable
fun effectiveGame(game: Game): Game {
    val selection by Variants.selection.collectAsState()
    return Variants.effective(game, selection)
}

/** "Classic · Remastered": a switch between a game's installations, on pages of games that have more than one. */
@Composable
fun VariantChooser(game: Game, modifier: Modifier = Modifier) {
    if (game.variants.isEmpty()) return
    val context = LocalContext.current
    val chosen = effectiveGame(game)
    Row(modifier.padding(vertical = 4.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        for (g in listOf(game) + game.variants) {
            val on = g.id == chosen.id
            Text(
                (g.variantLabel ?: g.fullTitle).uppercase(),
                style = DisplayStyle.copy(fontSize = 12.sp, color = if (on) Colors.Gold else Colors.Mist),
                modifier = Modifier.clip(RoundedCornerShape(4.dp)).clickable { Variants.select(context, game, g) }
                    .drawBehind { if (on) drawFrame(arm = 5.dp.toPx(), line = null) }
                    .padding(horizontal = 12.dp, vertical = 8.dp),
            )
        }
    }
}
