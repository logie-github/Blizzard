package com.logie.blizz.ui

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.gestures.detectTransformGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.requiredSize
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.PhotoSizeSelectSmall
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Slider
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.graphics.painter.BitmapPainter
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.logie.blizz.Game
import com.logie.blizz.game.Loading
import com.logie.blizz.game.Splashes
import com.logie.blizz.game.rememberGameAspect
import com.logie.blizz.steamgrid.SteamGrid
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File

/**
 * A version's art, in two parts. **Home**: its box (the library) and the picture behind it on the home screen, each cropped to its frame
 * (Crop: drag and zoom). **Loading screen**: its picture and logo, and below them the screen as it will look (drag and pinch the
 * picture, tap where the logo goes, slide for its size). Every picture: Change (SteamGridDB when the key is in Settings, else a file
 * on the phone), Crop (box, home and loading picture), Original.
 */
@Composable
fun SplashDialog(game: Game, onDismiss: () -> Unit) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val version by Splashes.version.collectAsState()
    val tiles by TileSettings.state.collectAsState()
    fun load(file: File?) = file?.let { runCatching { android.graphics.BitmapFactory.decodeFile(it.path)?.asImageBitmap() }.getOrNull() }
    val ownBox = remember(game.id, tiles.artVersion) { load(TileSettings.artFile(context, game.id, false)) }
    val ownHome = remember(game.id, version) { load(Splashes.file(context, game.id, Splashes.Kind.HEADER)) }
    val ownLoading = remember(game.id, version) { load(Splashes.file(context, game.id, Splashes.Kind.BACKGROUND)) }
    val ownLogo = remember(game.id, version) { load(Splashes.file(context, game.id, Splashes.Kind.LOGO)) }
    var layout by remember(game.id) { mutableStateOf(Splashes.layout(context, game.id)) }
    LaunchedEffect(layout) { delay(300); Splashes.setLayout(context, game.id, layout) }
    val homeAspect = rememberGameAspect()

    // A picture chosen for the box, home or loading picture goes to the crop first; the logo is set at once.
    var crop by remember { mutableStateOf<Pair<Slot, File>?>(null) }
    fun chosen(slot: Slot, uri: Uri) {
        when (slot) {
            Slot.LOGO -> Splashes.set(context, game.id, Splashes.Kind.LOGO, uri)
            Slot.BOX, Slot.HOME, Slot.LOADING -> scope.launch {
                val staged = withContext(Dispatchers.IO) { ArtSources.stage(context, game.id, slot.key, uri) }
                if (staged != null) crop = slot to staged
            }
        }
    }
    val pick = Slot.entries.associateWith { slot ->
        rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri -> if (uri != null) chosen(slot, uri) }
    }
    fun fromPhone(slot: Slot) = pick.getValue(slot).launch(arrayOf("image/*"))
    var gallery by remember { mutableStateOf<Slot?>(null) }
    fun change(slot: Slot) { if (SteamGrid.hasKey(context)) gallery = slot else fromPhone(slot) }
    fun reset(slot: Slot) {
        when (slot) {
            Slot.BOX -> TileSettings.clearArt(context, game.id, false)
            Slot.HOME -> Splashes.clear(context, game.id, Splashes.Kind.HEADER)
            Slot.LOADING -> Splashes.clear(context, game.id, Splashes.Kind.BACKGROUND)
            Slot.LOGO -> Splashes.clear(context, game.id, Splashes.Kind.LOGO)
        }
        ArtSources.clear(context, game.id, slot.key)
    }
    // Crop what is there: the whole source if it was kept, else the picture in use, else the built-in one.
    fun cropExisting(slot: Slot) {
        scope.launch {
            val source = withContext(Dispatchers.IO) {
                ArtSources.file(context, game.id, slot.key) ?: when (slot) {
                    Slot.BOX -> TileSettings.artFile(context, game.id, false)?.let { ArtSources.stage(context, game.id, slot.key, Uri.fromFile(it)) }
                        ?: ArtSources.stageResource(context, game.id, slot.key, game.cover)
                    Slot.LOADING -> Splashes.file(context, game.id, Splashes.Kind.BACKGROUND)?.let { ArtSources.stage(context, game.id, slot.key, Uri.fromFile(it)) }
                        ?: ArtSources.stageResource(context, game.id, slot.key, game.splash ?: game.wide ?: game.cover)
                    else -> Splashes.file(context, game.id, Splashes.Kind.HEADER)?.let { ArtSources.stage(context, game.id, slot.key, Uri.fromFile(it)) }
                        ?: ArtSources.stageResource(context, game.id, slot.key, game.wide ?: game.splash ?: game.cover)
                }
            }
            if (source != null) crop = slot to source
        }
    }

    gallery?.let { slot ->
        SteamGridPicker(
            game, slot.kind, slot.label,
            onPicked = { file -> chosen(slot, Uri.fromFile(file)) },
            onMyFiles = { fromPhone(slot) },
            onDismiss = { gallery = null },
        )
    }
    crop?.let { (slot, file) ->
        CropDialog(
            "Crop · ${slot.label}", file, if (slot == Slot.BOX) 2f / 3f else homeAspect,
            onSave = { bitmap ->
                when (slot) {
                    Slot.BOX -> TileSettings.setArtBitmap(context, game.id, bitmap)
                    Slot.LOADING -> Splashes.setBitmap(context, game.id, Splashes.Kind.BACKGROUND, bitmap)
                    else -> Splashes.setBitmap(context, game.id, Splashes.Kind.HEADER, bitmap)
                }
                crop = null
            },
            onDismiss = { crop = null },
        )
    }

    Dialog(onDismissRequest = onDismiss, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Sheet(game.fullTitle, onDismiss, maxWidth = 620.dp) {
            Column(Modifier.verticalScroll(rememberScrollState()).padding(start = 20.dp, end = 20.dp, top = 8.dp, bottom = 22.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                SectionLabel("Home")
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(14.dp), verticalAlignment = Alignment.Top) {
                    ArtCard(
                        Slot.BOX, Modifier.weight(1f), 2f / 3f, own = ownBox != null,
                        onChange = { change(Slot.BOX) }, onCrop = { cropExisting(Slot.BOX) }, onReset = { reset(Slot.BOX) },
                    ) {
                        if (ownBox != null) Image(ownBox, null, Modifier.fillMaxSize(), contentScale = ContentScale.Crop)
                        else Image(painterResource(game.cover), null, Modifier.fillMaxSize(), contentScale = ContentScale.Crop)
                    }
                    // as wide as makes it as tall as the box beside it
                    ArtCard(
                        Slot.HOME, Modifier.weight(2f / 3f * 3f / 2f * homeAspect), homeAspect, own = ownHome != null,
                        onChange = { change(Slot.HOME) }, onCrop = { cropExisting(Slot.HOME) }, onReset = { reset(Slot.HOME) },
                    ) {
                        val art = ownHome?.let { BitmapPainter(it) } ?: painterResource(game.wide ?: game.splash ?: game.cover)
                        Image(art, null, Modifier.fillMaxSize(), contentScale = ContentScale.Crop)
                    }
                }

                SectionLabel("Loading screen", Modifier.padding(top = 6.dp))
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(14.dp), verticalAlignment = Alignment.Top) {
                    ArtCard(
                        Slot.LOADING, Modifier.weight(1.6f), 3f / 2f, own = ownLoading != null,
                        onChange = { change(Slot.LOADING) }, onCrop = { cropExisting(Slot.LOADING) }, onReset = { reset(Slot.LOADING) },
                    ) {
                        val art = ownLoading?.let { BitmapPainter(it) } ?: painterResource(game.splash ?: game.wide ?: game.cover)
                        Image(art, null, Modifier.fillMaxSize(), contentScale = ContentScale.Crop)
                    }
                    ArtCard(
                        Slot.LOGO, Modifier.weight(1f), 3f / 2f, own = ownLogo != null,
                        onChange = { change(Slot.LOGO) }, onCrop = null, onReset = { reset(Slot.LOGO) },
                    ) {
                        val logo = ownLogo?.let { BitmapPainter(it) } ?: game.splashLogo?.let { painterResource(it) } ?: painterResource(com.logie.blizz.R.drawable.blizz_logo)
                        Box(Modifier.fillMaxSize().background(Color.Black.copy(alpha = 0.5f)).padding(10.dp), contentAlignment = Alignment.Center) {
                            Image(logo, null, Modifier.fillMaxSize(), contentScale = ContentScale.Fit)
                        }
                    }
                }

                // The loading screen itself, at the game's shape: drag and pinch the picture, tap where the logo goes.
                val corner = RoundedCornerShape(14.dp)
                BoxWithConstraints(
                    Modifier.fillMaxWidth().aspectRatio(homeAspect).clip(corner).border(1.dp, Colors.Steel, corner).background(Colors.Abyss)
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
                    Icon(Icons.Default.PhotoSizeSelectSmall, null, tint = Colors.Mist, modifier = Modifier.size(20.dp))
                    Slider(
                        layout.logoScale, { layout = layout.copy(logoScale = it) }, valueRange = 0.3f..2.5f, modifier = Modifier.weight(1f),
                        colors = androidx.compose.material3.SliderDefaults.colors(thumbColor = Colors.Ice, activeTrackColor = Colors.Ice, inactiveTrackColor = Colors.Frost),
                    )
                    Icon(Icons.Default.Refresh, "Original layout", tint = Colors.Mist, modifier = Modifier.clip(androidx.compose.foundation.shape.CircleShape).clickable { layout = Splashes.Layout() }.padding(8.dp).size(22.dp))
                }
            }
        }
    }
}

/** The four pictures of a version's art, and where SteamGridDB finds the kind of picture each is. */
private enum class Slot(val label: String, val key: String, val kind: SteamGrid.Slot) {
    BOX("Box", "box", SteamGrid.Slot.BOX),
    HOME("Home picture", "home", SteamGrid.Slot.HERO),
    LOADING("Loading picture", "loading", SteamGrid.Slot.HERO),
    LOGO("Logo", "logo", SteamGrid.Slot.LOGO),
}

/** One picture with its name under it and what can be done with it: Change, Crop (where it can be), Original (when it's your own). */
@Composable
private fun ArtCard(slot: Slot, modifier: Modifier, ratio: Float, own: Boolean, onChange: () -> Unit, onCrop: (() -> Unit)?, onReset: () -> Unit, picture: @Composable () -> Unit) {
    val shape = RoundedCornerShape(12.dp)
    Column(modifier, verticalArrangement = Arrangement.spacedBy(6.dp)) {
        Box(Modifier.fillMaxWidth().aspectRatio(ratio).clip(shape).border(1.dp, if (own) Colors.Ice else Colors.Steel, shape).clickable(onClick = onChange)) { picture() }
        Column {
            Text(slot.label, style = MaterialTheme.typography.titleMedium.copy(lineHeight = 18.sp))
            Row(horizontalArrangement = Arrangement.spacedBy(14.dp)) {
                ArtAction("Change", onChange)
                onCrop?.let { ArtAction("Crop", it) }
                if (own) ArtAction("Original", onReset, Colors.Mist)
            }
        }
    }
}

@Composable
private fun ArtAction(text: String, onClick: () -> Unit, color: Color = Colors.Ice) {
    Text(text, style = MaterialTheme.typography.labelLarge.copy(color = color, fontSize = 14.sp), modifier = Modifier.clip(RoundedCornerShape(6.dp)).clickable(onClick = onClick).padding(vertical = 4.dp))
}
