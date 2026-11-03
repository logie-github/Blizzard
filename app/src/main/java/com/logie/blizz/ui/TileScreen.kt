package com.logie.blizz.ui

import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.Crossfade
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.slideOutVertically
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.gestures.awaitEachGesture
import androidx.compose.foundation.gestures.awaitFirstDown
import androidx.compose.foundation.gestures.calculateZoom
import androidx.compose.foundation.gestures.detectDragGesturesAfterLongPress
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.WindowInsetsSides
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.only
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Image
import androidx.compose.material.icons.filled.OpenWith
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Tune
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.key
import androidx.compose.runtime.rememberUpdatedState
import kotlinx.coroutines.delay
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateMapOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawWithContent
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Rect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.RectangleShape
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.input.pointer.PointerEventPass
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.layout.boundsInRoot
import androidx.compose.ui.layout.onGloballyPositioned
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.compose.ui.zIndex
import com.logie.blizz.Game
import com.logie.blizz.Games
import com.logie.blizz.importer.GameImportManager

/** Opens the settings (hold the Blizzard logo): set by [Launcher]. */
internal val LocalOpenSettings = androidx.compose.runtime.staticCompositionLocalOf<() -> Unit> { {} }

private val PAD = 18.dp
private val GAP = 14.dp

/**
 * The tile layout: the header, then every game as a tile in the person's order, each vertical (box
 * art) or horizontal (wide art, two across). Pinch to make the tiles bigger or smaller (the 3DS's
 * grid); hold a tile for its menu (Change Art, Rearrange, Reinstall, Loading screen); in Rearrange,
 * hold a tile and drag it where it goes.
 */
@OptIn(ExperimentalFoundationApi::class)
@Composable
fun TileScreen(onOpen: (Game) -> Unit) {
    val context = LocalContext.current
    val s by TileSettings.state.collectAsState()
    val ids = remember { Games.all.map { it.id } }
    var order by remember(s.order) { mutableStateOf(TileLayout.ordered(ids, s.order)) }
    var rearranging by remember { mutableStateOf(false) }
    var dragging by remember { mutableStateOf<String?>(null) }
    var dragAt by remember { mutableStateOf(Offset.Zero) }
    var artFor by remember { mutableStateOf<Game?>(null) }
    var optionsFor by remember { mutableStateOf<Game?>(null) }
    var reinstallFor by remember { mutableStateOf<Game?>(null) }
    val openWizard = LocalOpenWizard.current
    val openSplash = LocalOpenSplash.current

    val density = androidx.compose.ui.platform.LocalDensity.current
    // While two fingers pinch, the grid follows them a little before the columns change.
    var pinch by remember { mutableStateOf(1f) }
    val pinchShown by animateFloatAsState(pinch, spring(dampingRatio = 0.8f, stiffness = 500f), label = "pinch")

    BoxWithConstraints(Modifier.fillMaxSize().background(Colors.Abyss)) {
        val width = maxWidth
        val height = maxHeight
        val columns = if (s.columns > 0) s.columns else TileLayout.autoColumns(width.value)
        val inner = (minOf(width, 1100.dp) - PAD * 2)
        val cell = (inner - GAP * (columns - 1)) / columns
        val tiles = order.map { id -> TileLayout.Tile(id, id in s.wide) }
        val (placed, gridHeight) = remember(tiles, columns, cell) { TileLayout.place(tiles, columns, cell.value, GAP.value) }
        // Each tile's target place in pixels, in the grid's own coordinates: what a drag is measured against.
        val rects = remember(placed, density) {
            with(density) { placed.associate { it.id to Rect(it.x.dp.toPx(), it.y.dp.toPx(), (it.x + it.width).dp.toPx(), (it.y + it.height).dp.toPx()) } }
        }

        // The pointer handlers below keep running across recompositions, so what they read is read through
        // these (a plain value would stay as it was when the handler started).
        val rectsNow by rememberUpdatedState(rects)
        val stepNow by rememberUpdatedState<(Int) -> Unit> { step ->
            TileSettings.setColumns(context, ((if (s.columns > 0) s.columns else columns) + step).coerceIn(TileLayout.MIN_COLUMNS, TileLayout.MAX_COLUMNS))
        }
        Column(
            Modifier
                .fillMaxSize()
                .pinchColumns(
                    enabled = dragging == null,
                    onScale = { pinch = it.coerceIn(0.85f, 1.2f) },
                    onEnd = { pinch = 1f },
                    onStep = { step -> stepNow(step) },
                )
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Header(width, height)
            Box(
                Modifier
                    .widthIn(max = 1100.dp)
                    .fillMaxWidth()
                    .windowInsetsPadding(WindowInsets.safeDrawing.only(WindowInsetsSides.Horizontal))
                    .padding(horizontal = PAD)
                    .padding(top = 8.dp, bottom = 40.dp)
                    .height(gridHeight.dp)
                    .graphicsLayer { scaleX = pinchShown; scaleY = pinchShown },
            ) {
                placed.forEachIndexed { index, p ->
                    key(p.id) {
                        val game = Games.all.first { it.id == p.id }
                        val isDragging = dragging == p.id
                        // Tiles glide to their new places (a reorder, a new size, a new shape); the one being dragged is on the finger.
                        val spec = spring<Float>(dampingRatio = 0.82f, stiffness = 380f)
                        val x by animateFloatAsState(p.x, spec, label = "x")
                        val y by animateFloatAsState(p.y, spec, label = "y")
                        val w by animateFloatAsState(p.width, spec, label = "w")
                        val h by animateFloatAsState(p.height, spec, label = "h")
                        Tile(
                            game = game, index = index, wide = game.id in s.wide, rearranging = rearranging, isDragging = isDragging, artVersion = s.artVersion,
                            modifier = Modifier
                                .offset { androidx.compose.ui.unit.IntOffset((if (isDragging) p.x else x).dp.roundToPx(), (if (isDragging) p.y else y).dp.roundToPx()) }
                                .size((if (isDragging) p.width else w).dp, (if (isDragging) p.height else h).dp)
                                // The drag is read before the tile is moved by it: a node that follows the finger would see no motion.
                                .then(
                                    if (rearranging) Modifier.pointerInput(p.id) {
                                        detectDragGesturesAfterLongPress(
                                            onDragStart = { local -> dragging = p.id; dragAt = (rectsNow[p.id]?.topLeft ?: Offset.Zero) + local },
                                            onDrag = { change, amount ->
                                                change.consume()
                                                dragAt += amount
                                                val over = rectsNow.entries.firstOrNull { (id, r) -> id != p.id && r.contains(dragAt) }?.key
                                                if (over != null) order = TileLayout.move(order, p.id, over)
                                            },
                                            onDragEnd = { dragging = null; TileSettings.setOrder(context, order) },
                                            onDragCancel = { dragging = null; TileSettings.setOrder(context, order) },
                                        )
                                    } else Modifier,
                                )
                                .then(
                                    if (isDragging) Modifier.zIndex(5f).graphicsLayer {
                                        val c = rects[p.id]?.center ?: dragAt
                                        translationX = dragAt.x - c.x
                                        translationY = dragAt.y - c.y
                                        scaleX = 1.06f; scaleY = 1.06f
                                    } else Modifier,
                                ),
                            onClick = { if (!rearranging) onOpen(game) },
                            onChangeArt = { artFor = game },
                            onRearrange = { rearranging = true },
                            onReinstall = { reinstallFor = game },
                            onLoadingScreen = { openSplash(game) },
                            onLaunchOptions = { optionsFor = game },
                        )
                    }
                }
            }
        }

        AnimatedVisibility(
            rearranging, Modifier.align(Alignment.TopCenter),
            enter = fadeIn(tween(200)) + slideInVertically(tween(260)) { -it / 2 }, exit = fadeOut(tween(160)) + slideOutVertically(tween(200)) { -it / 2 },
        ) {
            Row(
                Modifier.windowInsetsPadding(WindowInsets.safeDrawing).padding(12.dp)
                    .background(Colors.Deep.copy(alpha = 0.96f)).border(1.dp, Colors.Steel).padding(start = 16.dp, end = 8.dp, top = 6.dp, bottom = 6.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                Text("Hold a tile, then drag it", style = MaterialTheme.typography.bodyMedium, color = Colors.Mist)
                FrameButton("Done") { rearranging = false; TileSettings.setOrder(context, order) }
            }
        }
    }

    artFor?.let { TileArtDialog(it, onDismiss = { artFor = null }) }
    optionsFor?.let { GameOptionsDialog(Variants.effective(it), onDismiss = { optionsFor = null }) }
    reinstallFor?.let { game ->
        val target = Variants.effective(game)
        ConfirmDialog(
            title = "Reinstall ${target.fullTitle}?",
            text = "Its imported files are removed and the import starts again. Saved games stay.",
            confirm = "Reinstall",
            onDismiss = { reinstallFor = null },
            onConfirm = { GameImportManager.reset(context, target.id); reinstallFor = null; openWizard(game) },
        )
    }
}

/** A tile: its art, pressed in when touched, with the hold menu; wiggling while the tiles are being rearranged. */
@OptIn(ExperimentalFoundationApi::class)
@Composable
private fun Tile(
    game: Game, index: Int, wide: Boolean, rearranging: Boolean, isDragging: Boolean, artVersion: Int, modifier: Modifier,
    onClick: () -> Unit, onChangeArt: () -> Unit, onRearrange: () -> Unit, onReinstall: () -> Unit, onLoadingScreen: () -> Unit, onLaunchOptions: () -> Unit,
) {
    val context = LocalContext.current
    val haptic = LocalHapticFeedback.current
    var menu by remember { mutableStateOf(false) }
    val shown = effectiveGame(game)
    val custom = remember(shown.id, wide, artVersion) {
        TileSettings.artFile(context, shown.id, wide)?.let { runCatching { android.graphics.BitmapFactory.decodeFile(it.path)?.asImageBitmap() }.getOrNull() }
    }
    val builtIn = if (wide) shown.wide ?: shown.splash ?: shown.cover else shown.cover
    val wiggle by rememberInfiniteTransition(label = "wiggle").animateFloat(-1.1f, 1.1f, infiniteRepeatable(tween(150 + (game.id.hashCode() and 63), easing = FastOutSlowInEasing), RepeatMode.Reverse), label = "wiggle")
    val interaction = remember { MutableInteractionSource() }
    val pressed by interaction.collectIsPressedAsState()
    val press by animateFloatAsState(if (pressed) 1f else 0f, spring(dampingRatio = 0.7f, stiffness = 600f), label = "press")
    // The tiles come in one after another the first time the screen shows.
    val appear = remember { Animatable(0f) }
    LaunchedEffect(Unit) {
        delay(120L + index * 60L)
        appear.animateTo(1f, tween(520, easing = FastOutSlowInEasing))
    }

    Box(
        modifier
            .graphicsLayer {
                alpha = appear.value
                translationY = (1f - appear.value) * 20.dp.toPx()
                val s = 1f - 0.035f * press
                scaleX = s; scaleY = s
                if (rearranging && !isDragging) rotationZ = wiggle
            }
            .combinedClickable(
                interactionSource = interaction, indication = null, enabled = !rearranging, onClick = onClick,
                onLongClick = { haptic.performHapticFeedback(HapticFeedbackType.LongPress); menu = true },
            ),
    ) {
        val frame = Modifier.fillMaxSize().drawWithContent {
            drawContent()
            drawRect(Color.White.copy(alpha = 0.07f * press))
            drawFrame(corner = if (isDragging || press > 0.5f) Colors.Ice else Colors.Gold, alpha = 0.6f + 0.3f * press, line = Colors.Steel.copy(alpha = 0.9f))
        }
        // The art cross-fades when its shape or picture changes.
        Crossfade(targetState = custom to builtIn, animationSpec = tween(260), label = "art") { (picture, resource) ->
            if (picture != null) Image(picture, game.fullTitle, frame, contentScale = ContentScale.Crop)
            else Image(painterResource(resource), game.fullTitle, frame, contentScale = ContentScale.Crop)
        }

        DropdownMenu(
            expanded = menu, onDismissRequest = { menu = false },
            shape = RectangleShape, containerColor = Colors.Deep, border = androidx.compose.foundation.BorderStroke(1.dp, Colors.Steel),
        ) {
            MenuItem(Icons.Default.Image, "Change Art") { menu = false; onChangeArt() }
            MenuItem(Icons.Default.OpenWith, "Rearrange") { menu = false; onRearrange() }
            if (GameImportManager.importable(Variants.effective(game).id)) MenuItem(Icons.Default.Refresh, "Reinstall") { menu = false; onReinstall() }
            MenuItem(Icons.Default.Tune, "Loading screen") { menu = false; onLoadingScreen() }
            MenuItem(Icons.Default.Settings, "Launch options") { menu = false; onLaunchOptions() }
        }
    }
}

@Composable
private fun MenuItem(icon: androidx.compose.ui.graphics.vector.ImageVector, label: String, onClick: () -> Unit) {
    DropdownMenuItem(
        text = { Text(label, style = MaterialTheme.typography.bodyLarge, color = Colors.Text) },
        leadingIcon = { Icon(icon, contentDescription = null, tint = Colors.Gold) },
        onClick = onClick,
    )
}

/** Change a tile's art: vertical or horizontal, and a picture of the person's own for either. */
@OptIn(androidx.compose.foundation.layout.ExperimentalLayoutApi::class)
@Composable
private fun TileArtDialog(game: Game, onDismiss: () -> Unit) {
    val context = LocalContext.current
    val s by TileSettings.state.collectAsState()
    val wide = game.id in s.wide
    val shown = effectiveGame(game)
    val pick = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) TileSettings.setArt(context, shown.id, wide, uri)
    }
    val custom = remember(shown.id, wide, s.artVersion) {
        TileSettings.artFile(context, shown.id, wide)?.let { runCatching { android.graphics.BitmapFactory.decodeFile(it.path)?.asImageBitmap() }.getOrNull() }
    }
    val builtIn = if (wide) shown.wide ?: shown.splash ?: shown.cover else shown.cover
    Dialog(onDismissRequest = onDismiss, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Column(
            Modifier.padding(18.dp).widthIn(max = 520.dp).fillMaxWidth()
                .background(Colors.Deep).border(1.dp, Colors.Steel).padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            FrameTitle("Change art")
            FlowRow(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp, Alignment.CenterHorizontally), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                FrameButton("Vertical", primary = !wide) { TileSettings.setWide(context, game.id, false) }
                FrameButton("Horizontal", primary = wide) { TileSettings.setWide(context, game.id, true) }
            }
            Box(Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
                val shape = Modifier.height(if (wide) 150.dp else 240.dp).then(if (wide) Modifier.fillMaxWidth() else Modifier.size(width = 180.dp, height = 240.dp))
                    .border(1.dp, Colors.Steel).clip(RectangleShape)
                if (custom != null) Image(custom, null, shape, contentScale = ContentScale.Crop)
                else Image(painterResource(builtIn), null, shape, contentScale = ContentScale.Crop)
            }
            FlowRow(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp, Alignment.CenterHorizontally), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                FrameButton("Choose picture") { pick.launch(arrayOf("image/*")) }
                FrameButton("Original", primary = false) { TileSettings.clearArt(context, shown.id, wide) }
                FrameButton("Done", primary = false, onClick = onDismiss)
            }
        }
    }
}

@Composable
internal fun ConfirmDialog(title: String, text: String, confirm: String, onDismiss: () -> Unit, onConfirm: () -> Unit) {
    Dialog(onDismissRequest = onDismiss, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Column(
            Modifier.padding(24.dp).widthIn(max = 460.dp).fillMaxWidth().background(Colors.Deep).border(1.dp, Colors.Steel).padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            FrameTitle(title, style = MaterialTheme.typography.titleLarge)
            Text(text, style = MaterialTheme.typography.bodyLarge, color = Colors.Mist)
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp, Alignment.End)) {
                FrameButton("No", primary = false, onClick = onDismiss)
                FrameButton(confirm, onClick = onConfirm)
            }
        }
    }
}

/**
 * Two fingers spreading make the tiles bigger (one fewer across), pinching makes them smaller (one
 * more): the grid follows the fingers a little ([onScale]) and settles when the columns change or
 * the fingers lift ([onEnd]). One finger scrolls as it always did, so nothing is taken until a
 * second one is down.
 */
private fun Modifier.pinchColumns(enabled: Boolean, onScale: (Float) -> Unit, onEnd: () -> Unit, onStep: (Int) -> Unit): Modifier = pointerInput(enabled) {
    if (!enabled) return@pointerInput
    awaitEachGesture {
        awaitFirstDown(requireUnconsumed = false)
        var scale = 1f
        var pinching = false
        do {
            val event = awaitPointerEvent(PointerEventPass.Initial)
            if (event.changes.count { it.pressed } >= 2) {
                pinching = true
                scale *= event.calculateZoom()
                onScale(scale)
                if (scale > 1.35f) { onStep(-1); scale = 1f; onScale(1f) } else if (scale < 0.74f) { onStep(1); scale = 1f; onScale(1f) }
                event.changes.forEach { it.consume() }
            }
        } while (event.changes.any { it.pressed })
        if (pinching) onEnd()
    }
}
