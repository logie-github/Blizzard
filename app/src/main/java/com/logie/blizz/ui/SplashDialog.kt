package com.logie.blizz.ui

import android.net.Uri
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
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.PhotoSizeSelectSmall
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.graphics.painter.BitmapPainter
import androidx.compose.ui.graphics.Color
import androidx.compose.material3.Icon
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.Image
import androidx.compose.ui.draw.clip
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

/**
 * A version's art, all in one place: its box (the library and the shelf), its background (the home screen behind it and its
 * loading screen) and its logo (on the loading screen). Tap a picture to change it, the ↺ on it to put the original back. Below,
 * the loading screen as it will look: drag and pinch the background, tap where the logo goes, the slider for its size.
 */
@Composable
fun SplashDialog(game: Game, onDismiss: () -> Unit) {
    val context = LocalContext.current
    val version by Splashes.version.collectAsState()
    val tiles by TileSettings.state.collectAsState()
    val pickBackground = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) Splashes.set(context, game.id, Splashes.Kind.BACKGROUND, uri)
    }
    val pickLogo = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) Splashes.set(context, game.id, Splashes.Kind.LOGO, uri)
    }
    val pickBox = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) TileSettings.setArt(context, game.id, false, uri)
    }
    fun load(file: java.io.File?) = file?.let { runCatching { android.graphics.BitmapFactory.decodeFile(it.path)?.asImageBitmap() }.getOrNull() }
    val ownBox = remember(game.id, tiles.artVersion) { load(TileSettings.artFile(context, game.id, false)) }
    val ownBackground = remember(game.id, version) { load(Splashes.file(context, game.id, Splashes.Kind.BACKGROUND)) }
    val ownHeader = remember(game.id, version) { load(Splashes.file(context, game.id, Splashes.Kind.HEADER)) }
    val pickHeader = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) Splashes.set(context, game.id, Splashes.Kind.HEADER, uri)
    }
    val ownLogo = remember(game.id, version) { load(Splashes.file(context, game.id, Splashes.Kind.LOGO)) }
    var layout by remember(game.id) { mutableStateOf(Splashes.layout(context, game.id)) }
    LaunchedEffect(layout) { delay(300); Splashes.setLayout(context, game.id, layout) }

    // Which picture is being chosen: from SteamGridDB (when the key is in Settings), or from the phone's files.
    var gallery by remember { mutableStateOf<Slot?>(null) }
    fun fromPhone(slot: Slot) = when (slot) {
        Slot.BOX -> pickBox.launch(arrayOf("image/*"))
        Slot.HOME -> pickHeader.launch(arrayOf("image/*"))
        Slot.LOADING -> pickBackground.launch(arrayOf("image/*"))
        Slot.LOGO -> pickLogo.launch(arrayOf("image/*"))
    }
    fun choose(slot: Slot) { if (com.logie.blizz.steamgrid.SteamGrid.hasKey(context)) gallery = slot else fromPhone(slot) }
    gallery?.let { slot ->
        SteamGridPicker(
            game, slot.kind, slot.label,
            onPicked = { file ->
                val uri = Uri.fromFile(file)
                when (slot) {
                    Slot.BOX -> TileSettings.setArt(context, game.id, false, uri)
                    Slot.HOME -> Splashes.set(context, game.id, Splashes.Kind.HEADER, uri)
                    Slot.LOADING -> Splashes.set(context, game.id, Splashes.Kind.BACKGROUND, uri)
                    Slot.LOGO -> Splashes.set(context, game.id, Splashes.Kind.LOGO, uri)
                }
                file.delete()
            },
            onMyFiles = { fromPhone(slot) },
            onDismiss = { gallery = null },
        )
    }

    Dialog(onDismissRequest = onDismiss, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Sheet(game.fullTitle, onDismiss, maxWidth = 620.dp) {
            Column(Modifier.verticalScroll(rememberScrollState()).padding(start = 20.dp, end = 20.dp, top = 8.dp, bottom = 20.dp), verticalArrangement = Arrangement.spacedBy(18.dp)) {
                // The home screen: the box in the library, and the picture that fills the screen behind the game.
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp), verticalAlignment = Alignment.Bottom) {
                    ArtSlot(
                        "Box", Modifier.weight(0.75f), 3f / 4f,
                        own = ownBox != null, onReset = { TileSettings.clearArt(context, game.id, false) }, onPick = { choose(Slot.BOX) },
                    ) {
                        if (ownBox != null) Image(ownBox, null, Modifier.fillMaxSize(), contentScale = ContentScale.Crop)
                        else Image(painterResource(game.cover), null, Modifier.fillMaxSize(), contentScale = ContentScale.Crop)
                    }
                    ArtSlot(
                        "Home picture", Modifier.weight(2.25f), 2.25f,
                        own = ownHeader != null, onReset = { Splashes.clear(context, game.id, Splashes.Kind.HEADER) }, onPick = { choose(Slot.HOME) },
                    ) {
                        val art = ownHeader?.let { BitmapPainter(it) } ?: painterResource(game.wide ?: game.splash ?: game.cover)
                        Image(art, null, Modifier.fillMaxSize(), contentScale = ContentScale.Crop)
                    }
                }
                // The loading screen: its picture and its logo (below, how it will look).
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp), verticalAlignment = Alignment.Bottom) {
                    ArtSlot(
                        "Loading picture", Modifier.weight(1.5f), 3f / 2f,
                        own = ownBackground != null, onReset = { Splashes.clear(context, game.id, Splashes.Kind.BACKGROUND) }, onPick = { choose(Slot.LOADING) },
                    ) {
                        val art = ownBackground?.let { BitmapPainter(it) } ?: painterResource(game.splash ?: game.wide ?: game.cover)
                        Image(art, null, Modifier.fillMaxSize(), contentScale = ContentScale.Crop)
                    }
                    ArtSlot(
                        "Logo", Modifier.weight(0.75f), 3f / 4f,
                        own = ownLogo != null, onReset = { Splashes.clear(context, game.id, Splashes.Kind.LOGO) }, onPick = { choose(Slot.LOGO) },
                    ) {
                        val logo = ownLogo?.let { BitmapPainter(it) } ?: game.splashLogo?.let { painterResource(it) } ?: painterResource(com.logie.blizz.R.drawable.blizz_logo)
                        Box(Modifier.fillMaxSize().background(Color.Black.copy(alpha = 0.5f)).padding(8.dp), contentAlignment = Alignment.Center) {
                            Image(logo, null, Modifier.fillMaxSize(), contentScale = ContentScale.Fit)
                        }
                    }
                }

                // The loading screen itself, at the game's shape: drag and pinch the background, tap where the logo goes.
                BoxWithConstraints(
                    Modifier.fillMaxWidth().aspectRatio(com.logie.blizz.game.rememberGameAspect())
                        .clip(RoundedCornerShape(if (Look.modern) 14.dp else 0.dp)).border(1.dp, Colors.Steel, RoundedCornerShape(if (Look.modern) 14.dp else 0.dp))
                        .background(Colors.Abyss)
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
                        }
                        .pointerInput(Unit) {
                            detectTapGestures { at ->
                                val col = (at.x / size.width * 3).toInt().coerceIn(0, 2)
                                val row = (at.y / size.height * 3).toInt().coerceIn(0, 2)
                                layout = layout.copy(logoCell = row * 3 + col)
                            }
                        },
                ) {
                    Box(Modifier.requiredSize(maxWidth * 2, maxHeight * 2).graphicsLayer { scaleX = 0.5f; scaleY = 0.5f }) {
                        Loading(game.id, "", layoutOverride = layout)
                    }
                }
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    Icon(androidx.compose.material.icons.Icons.Default.PhotoSizeSelectSmall, null, tint = Colors.Mist, modifier = Modifier.size(20.dp))
                    Slider(
                        layout.logoScale, { layout = layout.copy(logoScale = it) }, valueRange = 0.3f..2.5f, modifier = Modifier.weight(1f),
                        colors = androidx.compose.material3.SliderDefaults.colors(thumbColor = Colors.Ice, activeTrackColor = Colors.Ice, inactiveTrackColor = Colors.Frost),
                    )
                    Icon(androidx.compose.material.icons.Icons.Default.Refresh, "Original layout", tint = Colors.Mist,
                        modifier = Modifier.clip(CircleShape).clickable { layout = Splashes.Layout() }.padding(8.dp).size(22.dp))
                }
            }
        }
    }
}

/** The four pictures of a version's art, and where SteamGridDB finds the kind of picture each is. */
private enum class Slot(val label: String, val kind: com.logie.blizz.steamgrid.SteamGrid.Slot) {
    BOX("Box", com.logie.blizz.steamgrid.SteamGrid.Slot.BOX),
    HOME("Home picture", com.logie.blizz.steamgrid.SteamGrid.Slot.HERO),
    LOADING("Loading picture", com.logie.blizz.steamgrid.SteamGrid.Slot.HERO),
    LOGO("Logo", com.logie.blizz.steamgrid.SteamGrid.Slot.LOGO),
}

/** One picture of a version's art: tap to choose another; the ↺ in its corner, shown when it's your own, puts the original back. */
@Composable
private fun ArtSlot(label: String, modifier: Modifier, ratio: Float, own: Boolean, onReset: () -> Unit, onPick: () -> Unit, picture: @Composable () -> Unit) {
    Column(modifier, verticalArrangement = Arrangement.spacedBy(8.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Box(
            Modifier.fillMaxWidth().aspectRatio(ratio).clip(RoundedCornerShape(12.dp))
                .border(1.dp, if (own) Colors.Ice else Colors.Steel, RoundedCornerShape(12.dp)).clickable(onClick = onPick),
        ) {
            picture()
            if (own) Icon(
                androidx.compose.material.icons.Icons.Default.Refresh, "Original", tint = Color.White,
                modifier = Modifier.align(Alignment.TopEnd).padding(6.dp).size(30.dp).clip(CircleShape).background(Color.Black.copy(alpha = 0.6f))
                    .clickable(onClick = onReset).padding(5.dp),
            )
        }
        Text(label, style = MaterialTheme.typography.bodySmall, color = Colors.Mist)
    }
}
