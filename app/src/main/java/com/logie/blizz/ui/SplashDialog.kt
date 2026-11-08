package com.logie.blizz.ui

import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectTransformGestures
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.requiredSize
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Slider
import androidx.compose.material3.Text
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.input.pointer.pointerInput
import kotlinx.coroutines.delay
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clipToBounds
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.logie.blizz.Game
import com.logie.blizz.game.Loading
import com.logie.blizz.game.Splashes

/** Hold a game's art: its loading screen as it is now, with a picture and a logo to pick from the phone. */
@OptIn(androidx.compose.foundation.layout.ExperimentalLayoutApi::class)
@Composable
fun SplashDialog(game: Game, onDismiss: () -> Unit) {
    val context = LocalContext.current
    val sliderColors = androidx.compose.material3.SliderDefaults.colors(
        thumbColor = Colors.Ice, activeTrackColor = Colors.Ice, inactiveTrackColor = Colors.Frost, activeTickColor = Colors.Ice, inactiveTickColor = Colors.Steel,
    )
    @Suppress("UNUSED_VARIABLE") val version by Splashes.version.collectAsState()
    val pickBackground = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) Splashes.set(context, game.id, Splashes.Kind.BACKGROUND, uri)
    }
    val pickLogo = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) Splashes.set(context, game.id, Splashes.Kind.LOGO, uri)
    }
    val tiles by TileSettings.state.collectAsState()
    val pickBoxArt = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) TileSettings.setArt(context, game.id, false, uri)
    }
    val boxArtShown = remember(game.id, tiles.artVersion) {
        TileSettings.artFile(context, game.id, false)?.let { runCatching { android.graphics.BitmapFactory.decodeFile(it.path)?.asImageBitmap() }.getOrNull() }
    }
    var layout by remember { mutableStateOf(Splashes.layout(context, game.id)) }
    var grid by remember { mutableStateOf(true) }
    // Saved a moment after the last change.
    LaunchedEffect(layout) { delay(300); Splashes.setLayout(context, game.id, layout) }
    Dialog(onDismissRequest = onDismiss, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Column(
            Modifier.padding(18.dp).widthIn(max = 620.dp).fillMaxWidth().verticalScroll(rememberScrollState())
                .panel().padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            FrameTitle(game.fullTitle)
            // The box art of this game (each mode of World of Warcraft has its own).
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(14.dp), verticalAlignment = Alignment.CenterVertically) {
                val art = Modifier.width(72.dp).aspectRatio(3f / 4f).border(1.dp, Colors.Steel)
                if (boxArtShown != null) androidx.compose.foundation.Image(boxArtShown, null, art, contentScale = androidx.compose.ui.layout.ContentScale.Crop)
                else androidx.compose.foundation.Image(androidx.compose.ui.res.painterResource(game.cover), null, art, contentScale = androidx.compose.ui.layout.ContentScale.Crop)
                FlowRow(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    FrameButton("Box art") { pickBoxArt.launch(arrayOf("image/*")) }
                    if (boxArtShown != null) FrameButton("Original", primary = false) { TileSettings.clearArt(context, game.id, false) }
                }
            }
            // The loading screen itself, at half the size and at the game's own shape (the Fold's inside screen): what's
            // outside this frame is cut on the phone too. Pinch to zoom the picture, drag to move it.
            BoxWithConstraints(
                Modifier.fillMaxWidth().aspectRatio(com.logie.blizz.game.rememberGameAspect()).clipToBounds().border(1.dp, Colors.Steel).background(Colors.Abyss)
                    .pointerInput(Unit) {
                        detectTransformGestures { _, pan, zoom, _ ->
                            val z = (layout.zoom * zoom).coerceIn(1f, 4f)
                            val limit = (z - 1f) / 2f
                            layout = layout.copy(
                                zoom = z,
                                panX = (layout.panX + pan.x / size.width).coerceIn(-limit, limit),
                                panY = (layout.panY + pan.y / size.height).coerceIn(-limit, limit),
                            )
                        }
                    },
            ) {
                Box(Modifier.requiredSize(maxWidth * 2, maxHeight * 2).graphicsLayer { scaleX = 0.5f; scaleY = 0.5f }) {
                    Loading(game.id, "Starting…", layoutOverride = layout, grid = grid)
                }
            }
            Text("Pinch to zoom the picture, drag to move it.", style = MaterialTheme.typography.bodySmall, color = Colors.Mist)
            FlowRow(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp, Alignment.CenterHorizontally), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                FrameButton("Background") { pickBackground.launch(arrayOf("image/*")) }
                FrameButton("Logo") { pickLogo.launch(arrayOf("image/*")) }
            }
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(16.dp), verticalAlignment = Alignment.CenterVertically) {
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text("Logo place", style = MaterialTheme.typography.labelMedium, color = Colors.Mist)
                    for (row in 0..2) Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                        for (col in 0..2) {
                            val cell = row * 3 + col
                            val on = layout.logoCell == cell
                            Box(
                                Modifier.size(34.dp).border(1.dp, if (on) Colors.Ice else Colors.Steel).background(if (on) Colors.Ice.copy(alpha = 0.35f) else Colors.Abyss)
                                    .clickable { layout = layout.copy(logoCell = cell) },
                            )
                        }
                    }
                }
                Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
                    Text("Logo size", style = MaterialTheme.typography.labelMedium, color = Colors.Mist)
                    Slider(layout.logoScale, { layout = layout.copy(logoScale = it) }, valueRange = 0.3f..2.5f, colors = sliderColors)
                    Text("Picture zoom", style = MaterialTheme.typography.labelMedium, color = Colors.Mist)
                    Slider(layout.zoom, { z ->
                        val limit = (z - 1f) / 2f
                        layout = layout.copy(zoom = z, panX = layout.panX.coerceIn(-limit, limit), panY = layout.panY.coerceIn(-limit, limit))
                    }, valueRange = 1f..4f, colors = sliderColors)
                }
            }
            FlowRow(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp, Alignment.CenterHorizontally), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                FrameButton(if (grid) "Grid: on" else "Grid: off", primary = false) { grid = !grid }
                FrameButton("Centre picture", primary = false) { layout = layout.copy(zoom = layout.zoom, panX = 0f, panY = 0f) }
                FrameButton("Auto logo", primary = false) { layout = layout.copy(logoCell = -1, logoScale = 1f) }
                FrameButton("Reset", primary = false) { Splashes.clear(context, game.id); layout = Splashes.Layout() }
            }
        }
    }
}
