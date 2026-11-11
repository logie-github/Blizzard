package com.logie.blizz.ui

import android.os.Build
import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.Crossfade
import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.spring
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.MoreHoriz
import androidx.compose.material.icons.filled.Extension
import androidx.compose.material.icons.filled.Image
import androidx.compose.material.icons.filled.Mouse
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Storage
import androidx.compose.material.icons.filled.Tune
import androidx.compose.material.icons.filled.Download
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
import androidx.compose.ui.BiasAlignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.blur
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawWithContent
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.TransformOrigin
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.graphics.painter.BitmapPainter
import androidx.compose.ui.graphics.painter.Painter
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.logie.blizz.Game
import com.logie.blizz.Games
import com.logie.blizz.Links
import com.logie.blizz.R
import com.logie.blizz.game.Splashes
import com.logie.blizz.importer.GameImportManager
import com.logie.blizz.importer.Stage

/**
 * The modern launcher (the default look, [Look]): the chosen game's art fills the screen behind it, its name, version, Play
 * and its settings in front, and the library beside it (a list on the open Fold, a row of boxes on the cover screen). Holding
 * the Blizzard logo goes to the classic look (the shelf and the tiles); holding a game opens its menu.
 */
@Composable
internal fun ModernHome(
    linkKey: Int,
    selected: Game,
    onSelect: (Game) -> Unit,
    onPlay: (Game) -> Unit,
    onChooseApp: (Game) -> Unit,
) {
    BoxWithConstraints(Modifier.fillMaxSize().background(Modern.Background)) {
        val wide = maxWidth >= 680.dp
        val screenWidth = maxWidth
        Backdrop(selected)
        if (wide) {
            Row(Modifier.fillMaxSize().windowInsetsPadding(WindowInsets.safeDrawing)) {
                Library(selected, onSelect, Modifier.width((screenWidth * 0.28f).coerceIn(260.dp, 340.dp)).fillMaxHeight().padding(16.dp))
                Column(Modifier.weight(1f).fillMaxHeight().padding(end = 28.dp, top = 16.dp, bottom = 28.dp)) {
                    TopBar(Modifier.fillMaxWidth(), showLogo = false)
                    Spacer(Modifier.weight(1f))
                    Hero(selected, linkKey, onPlay, onChooseApp, Modifier.fillMaxWidth())
                }
            }
        } else {
            Column(Modifier.fillMaxSize().windowInsetsPadding(WindowInsets.safeDrawing)) {
                TopBar(Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp), showLogo = true)
                Spacer(Modifier.weight(1f))
                Hero(selected, linkKey, onPlay, onChooseApp, Modifier.padding(horizontal = 20.dp))
                Spacer(Modifier.height(32.dp))
                Shelf(selected, onSelect)
                Spacer(Modifier.height(28.dp))
            }
        }
    }
}

// The art behind everything

/** The art of the version shown, filling the screen, drifting slowly, darkened toward the text. */
@Composable
private fun Backdrop(game: Game) {
    val shown = effectiveGame(game)
    val context = LocalContext.current
    val version by Splashes.version.collectAsState()
    val drift by rememberInfiniteTransition(label = "drift").animateFloat(0f, 1f, infiniteRepeatable(tween(40_000, easing = FastOutSlowInEasing), RepeatMode.Reverse), label = "d")
    Crossfade(shown, animationSpec = tween(700), label = "backdrop") { g ->
        // The home's own picture (Art, "Header"): not the loading screen's background.
        val own = remember(g.id, version) {
            Splashes.file(context, g.id, Splashes.Kind.HEADER)?.let { runCatching { android.graphics.BitmapFactory.decodeFile(it.path)?.asImageBitmap() }.getOrNull() }
        }
        val painter: Painter = own?.let { BitmapPainter(it) } ?: painterResource(g.wide ?: g.splash ?: g.cover)
        val artIsCover = own == null && g.wide == null && g.splash == null
        Image(
            painter, null, contentScale = ContentScale.Crop, alignment = if (own != null) Alignment.Center else BiasAlignment(0.3f, -0.4f),
            modifier = Modifier.fillMaxSize().graphicsLayer {
                val z = 1.06f + 0.06f * drift
                scaleX = z; scaleY = z
                transformOrigin = TransformOrigin(0.7f, 0.3f)
                alpha = if (artIsCover) 0.55f else 0.9f
            }.let { if (artIsCover && Build.VERSION.SDK_INT >= 31) it.blur(24.dp) else it },
        )
    }
    // Scrims: dark to the left and the bottom, where the words are.
    Box(Modifier.fillMaxSize().background(Brush.horizontalGradient(0f to Modern.Background.copy(alpha = 0.92f), 0.55f to Modern.Background.copy(alpha = 0.35f), 1f to Color.Transparent)))
    Box(Modifier.fillMaxSize().background(Brush.verticalGradient(0f to Modern.Background.copy(alpha = 0.55f), 0.35f to Color.Transparent, 0.65f to Modern.Background.copy(alpha = 0.55f), 1f to Modern.Background)))
    // Particles in the picture's own colours: its highs and lows and a few accents (embers for a fiery picture, snow for an icy one).
    val art = shown.wide ?: shown.splash ?: shown.cover
    val palette = rememberArtPalette(Triple(shown.id, version, art)) { c ->
        Splashes.file(c, shown.id, Splashes.Kind.HEADER)?.let { smallFile(it) } ?: smallResource(c, art)
    }
    Snow(flakes = 44, alpha = 0.7f, palette = palette)
}

// The bar at the top

@OptIn(ExperimentalFoundationApi::class)
@Composable
private fun TopBar(modifier: Modifier, showLogo: Boolean) {
    val context = LocalContext.current
    val haptic = LocalHapticFeedback.current
    val openSettings = LocalOpenSettings.current
    Row(modifier.height(52.dp), verticalAlignment = Alignment.CenterVertically) {
        if (showLogo) Logo(Modifier.height(30.dp))
        Spacer(Modifier.weight(1f))
        RoundIcon(Icons.Default.Settings, "Settings", onClick = openSettings)
    }
}

/** The Blizzard logo. */
@Composable
private fun Logo(modifier: Modifier) {
    Image(painterResource(R.drawable.blizz_logo), contentDescription = "Blizzard", contentScale = ContentScale.Fit, modifier = modifier.aspectRatio(2000f / 1041f))
}

@OptIn(ExperimentalFoundationApi::class)
@Composable
private fun RoundIcon(icon: androidx.compose.ui.graphics.vector.ImageVector, description: String, onClick: () -> Unit) {
    val interaction = remember { MutableInteractionSource() }
    val pressed by interaction.collectIsPressedAsState()
    val press by animateFloatAsState(if (pressed) 1f else 0f, label = "press")
    Box(
        Modifier.size(44.dp).graphicsLayer { val k = 1f - 0.06f * press; scaleX = k; scaleY = k }
            .clip(CircleShape).background(Color.White.copy(alpha = 0.08f + 0.06f * press)).border(1.dp, Modern.Outline, CircleShape)
            .combinedClickable(interactionSource = interaction, indication = null, onClick = onClick),
        contentAlignment = Alignment.Center,
    ) { Icon(icon, description, tint = Modern.Text, modifier = Modifier.size(22.dp)) }
}

// The library

/** The open Fold's library: the logo, then every game as a row (its box, its name, whether it's ready), the chosen one lit. */
@OptIn(ExperimentalFoundationApi::class)
@Composable
private fun Library(selected: Game, onSelect: (Game) -> Unit, modifier: Modifier) {
    val context = LocalContext.current
    val haptic = LocalHapticFeedback.current
    val openHold = LocalOpenHold.current
    Column(
        modifier.clip(RoundedCornerShape(Modern.SheetCorner)).background(Modern.Surface.copy(alpha = 0.78f))
            .border(1.dp, Modern.Outline, RoundedCornerShape(Modern.SheetCorner)),
    ) {
        Logo(Modifier.padding(start = 22.dp, top = 22.dp, bottom = 10.dp).height(34.dp))
        LazyColumn(contentPadding = PaddingValues(start = 10.dp, end = 10.dp, bottom = 12.dp), verticalArrangement = Arrangement.spacedBy(2.dp)) {
            itemsIndexed(Games.all, key = { _, g -> g.id }) { _, game ->
                val on = game.id == selected.id
                val fill by animateColorAsState(if (on) Color.White.copy(alpha = 0.09f) else Color.Transparent, label = "row")
                Row(
                    Modifier.fillMaxWidth().clip(RoundedCornerShape(14.dp)).background(fill)
                        .combinedClickable(
                            interactionSource = remember { MutableInteractionSource() }, indication = null,
                            onClick = { onSelect(game) },
                            onLongClick = { haptic.performHapticFeedback(HapticFeedbackType.LongPress); openHold(game) },
                        )
                        .padding(horizontal = 10.dp, vertical = 8.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Box(Modifier.width(3.dp).height(30.dp).clip(CircleShape).background(if (on) Modern.Accent else Color.Transparent))
                    Spacer(Modifier.width(8.dp))
                    Image(boxArt(game), null, contentScale = ContentScale.Crop, modifier = Modifier.width(38.dp).aspectRatio(COVER_RATIO).clip(RoundedCornerShape(6.dp)))
                    Spacer(Modifier.width(12.dp))
                    Column(Modifier.weight(1f)) {
                        val chosen = effectiveGame(game)
                        Text(chosen.title, style = MaterialTheme.typography.titleMedium.copy(color = if (on) Modern.Text else Modern.Text.copy(alpha = 0.86f)), maxLines = 1, overflow = TextOverflow.Ellipsis)
                        if (game.variants.isEmpty()) chosen.subtitle?.let { Text(it, style = MaterialTheme.typography.bodySmall, maxLines = 1, overflow = TextOverflow.Ellipsis) }
                    }
                    ReadyDot(game)
                }
            }
        }
    }
}

/** A green dot for a game that's in the app (or has an app to play it with). */
@Composable
private fun ReadyDot(game: Game) {
    val shown = effectiveGame(game)
    val states by GameImportManager.states.collectAsState()
    val state = states[shown.id]
    val color = when {
        state?.running == true -> Modern.AccentBright
        state?.record?.stage == Stage.FAILED -> Modern.Warn
        state?.entry != null -> Modern.Good
        else -> null
    } ?: return
    Box(Modifier.size(8.dp).clip(CircleShape).background(color))
}

/** The cover screen's library: a row of boxes under the game, the chosen one raised and outlined. */
@OptIn(ExperimentalFoundationApi::class)
@Composable
private fun Shelf(selected: Game, onSelect: (Game) -> Unit) {
    val haptic = LocalHapticFeedback.current
    val openHold = LocalOpenHold.current
    val state = rememberLazyListState()
    LaunchedEffect(selected.id) {
        val index = Games.all.indexOfFirst { it.id == selected.id }
        if (index >= 0) state.animateScrollToItem((index - 1).coerceAtLeast(0))
    }
    LazyRow(state = state, contentPadding = PaddingValues(horizontal = 20.dp), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
        itemsIndexed(Games.all, key = { _, g -> g.id }) { _, game ->
            val on = game.id == selected.id
            val lift by animateFloatAsState(if (on) 1f else 0f, spring(dampingRatio = 0.7f, stiffness = 500f), label = "lift")
            Column(Modifier.width(108.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                Image(
                    boxArt(game), effectiveGame(game).fullTitle, contentScale = ContentScale.Crop,
                    modifier = Modifier.fillMaxWidth().aspectRatio(COVER_RATIO)
                        .graphicsLayer { translationY = -6.dp.toPx() * lift; val s = 1f + 0.04f * lift; scaleX = s; scaleY = s }
                        .shadow((4 + 10 * lift).dp, RoundedCornerShape(12.dp))
                        .clip(RoundedCornerShape(12.dp))
                        .border(if (on) 2.dp else 1.dp, if (on) Modern.AccentBright else Modern.Outline, RoundedCornerShape(12.dp))
                        .combinedClickable(
                            interactionSource = remember { MutableInteractionSource() }, indication = null,
                            onClick = { onSelect(game) },
                            onLongClick = { haptic.performHapticFeedback(HapticFeedbackType.LongPress); openHold(game) },
                        ),
                )
                Spacer(Modifier.height(8.dp))
                Text(effectiveGame(game).title, style = MaterialTheme.typography.bodySmall.copy(color = if (on) Modern.Text else Modern.Muted), maxLines = 1, overflow = TextOverflow.Ellipsis)
            }
        }
    }
}

// The game

/** The chosen game: its tags, its name, its versions, Play and what can be set for it. */
@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun Hero(game: Game, linkKey: Int, onPlay: (Game) -> Unit, onChooseApp: (Game) -> Unit, modifier: Modifier) {
    val context = LocalContext.current
    val chosen = effectiveGame(game)
    val linked = remember(linkKey, chosen.id) { Links.packageFor(context, game) }
    val openHold = LocalOpenHold.current
    AnimatedContent(
        targetState = game,
        transitionSpec = { (fadeIn(tween(320)) + slideInVertically(tween(380)) { it / 14 }) togetherWith fadeOut(tween(160)) },
        label = "hero", modifier = modifier,
    ) { g ->
        val shown = effectiveGame(g)
        Column(verticalArrangement = Arrangement.spacedBy(18.dp)) {
            Column {
                GameTitle(shown)
                shown.subtitle?.takeIf { g.variants.isEmpty() }?.let { Text(it, style = MaterialTheme.typography.headlineSmall.copy(color = Modern.Muted, fontWeight = FontWeight.Normal)) }
            }
            if (g.variants.isNotEmpty()) {
                PillSegmented(
                    (listOf(g) + g.variants).map { (it.variantLabel ?: it.fullTitle) to it },
                    shown, Modifier.widthIn(max = 520.dp),
                ) { Variants.select(context, g, it) }
            }
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                PlayCta(g, Modifier.widthIn(min = 210.dp)) { onPlay(g) }
                RoundIcon(Icons.Default.MoreHoriz, "More") { openHold(g) }
            }
            ImportBar(g)
        }
    }
}

/** The big Play button: Play, Install (an importable game that isn't in yet) or the import going on. */
@OptIn(ExperimentalFoundationApi::class)
@Composable
private fun PlayCta(game: Game, modifier: Modifier, onClick: () -> Unit) {
    val shown = effectiveGame(game)
    val states by GameImportManager.states.collectAsState()
    val state = states[shown.id]
    val importable = GameImportManager.importable(shown.id)
    val (label, icon) = when {
        // World of Warcraft: Forever runs its own offline realm on the phone (its own Play flow, not an importer).
        shown.id == "wow_forever" -> "Play" to Icons.Default.PlayArrow
        !importable -> "Play" to Icons.Default.PlayArrow
        state?.running == true -> "Importing…" to Icons.Default.Download
        state?.entry != null -> "Play" to Icons.Default.PlayArrow
        else -> "Install" to Icons.Default.Download
    }
    val interaction = remember { MutableInteractionSource() }
    val pressed by interaction.collectIsPressedAsState()
    val press by animateFloatAsState(if (pressed) 1f else 0f, spring(dampingRatio = 0.6f, stiffness = 700f), label = "press")
    val haptic = LocalHapticFeedback.current
    val glow by rememberInfiniteTransition(label = "glow").animateFloat(0.25f, 0.55f, infiniteRepeatable(tween(2200, easing = FastOutSlowInEasing), RepeatMode.Reverse), label = "g")
    Row(
        modifier
            .graphicsLayer { val k = 1f - 0.035f * press; scaleX = k; scaleY = k }
            .shadow(18.dp, RoundedCornerShape(16.dp), ambientColor = Modern.Accent.copy(alpha = glow), spotColor = Modern.Accent.copy(alpha = glow))
            .clip(RoundedCornerShape(16.dp))
            .background(Modern.AccentBrush)
            .drawWithContent { drawContent(); drawRect(Color.White.copy(alpha = 0.12f * press)) }
            .combinedClickable(interactionSource = interaction, indication = null, onClick = {
                haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove); onClick()
            })
            .heightIn(min = 54.dp)
            .padding(horizontal = 28.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.Center,
    ) {
        Icon(icon, null, tint = Color.White, modifier = Modifier.size(24.dp))
        Spacer(Modifier.width(10.dp))
        Text(label, style = MaterialTheme.typography.titleLarge.copy(color = Color.White, fontSize = 17.sp))
    }
}

/** A thin bar under Play while the version is being imported; tapping it opens the import. */
@OptIn(ExperimentalFoundationApi::class)
@Composable
private fun ImportBar(game: Game) {
    val shown = effectiveGame(game)
    val states by GameImportManager.states.collectAsState()
    val state = states[shown.id] ?: return
    if (!state.running) return
    val openWizard = LocalOpenWizard.current
    val p = state.progress
    val mod = Modifier.widthIn(max = 300.dp).fillMaxWidth().height(4.dp).clip(CircleShape).combinedClickableNoRipple { openWizard(shown) }
    if (p != null && p.total > 0) {
        val f by animateFloatAsState((p.done.toFloat() / p.total).coerceIn(0f, 1f), tween(400), label = "p")
        LinearProgressIndicator(progress = { f }, color = Modern.AccentBright, trackColor = Color.White.copy(alpha = 0.1f), modifier = mod)
    } else {
        LinearProgressIndicator(color = Modern.AccentBright, trackColor = Color.White.copy(alpha = 0.1f), modifier = mod)
    }
}


@OptIn(ExperimentalFoundationApi::class)
private fun Modifier.combinedClickableNoRipple(onClick: () -> Unit): Modifier =
    this.then(Modifier.combinedClickable(interactionSource = null, indication = null, onClick = onClick))

@Suppress("unused")
private val unusedDp: Dp = 0.dp

/**
 * Where the game's name stands: its logo, the one chosen in Art (or the game's own where it has one), at a fixed height whatever its
 * shape; a game with no logo has its name in Blizzard's lettering.
 */
@Composable
private fun GameTitle(shown: Game) {
    val context = LocalContext.current
    val version by Splashes.version.collectAsState()
    val own = remember(shown.id, version) {
        Splashes.file(context, shown.id, Splashes.Kind.LOGO)?.let { runCatching { android.graphics.BitmapFactory.decodeFile(it.path)?.asImageBitmap() }.getOrNull() }
    }
    val painter: Painter? = own?.let { BitmapPainter(it) } ?: shown.splashLogo?.let { painterResource(it) }
    if (painter != null) {
        Image(painter, shown.title, contentScale = ContentScale.Fit, alignment = Alignment.CenterStart, modifier = Modifier.heightIn(max = 110.dp).widthIn(max = 440.dp))
    } else {
        Text(shown.title, style = CinzelStyle.copy(fontSize = 40.sp, lineHeight = 46.sp, color = Modern.Text, letterSpacing = 0.02.sp), maxLines = 2)
    }
}
