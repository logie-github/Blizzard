package com.logie.blizz.ui

import android.os.Build
import androidx.activity.compose.BackHandler
import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.Crossfade
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
import androidx.compose.animation.scaleIn
import androidx.compose.animation.slideInHorizontally
import androidx.compose.animation.slideOutHorizontally
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsFocusedAsState
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.WindowInsetsSides
import androidx.compose.foundation.layout.only
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
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
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Block
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.produceState
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.BiasAlignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.blur
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.clipToBounds
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.draw.drawWithContent
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.TransformOrigin
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.min
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.core.graphics.drawable.toBitmap
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.compose.LifecycleEventEffect
import com.logie.blizz.Game
import com.logie.blizz.Games
import com.logie.blizz.InstalledApp
import com.logie.blizz.Links
import com.logie.blizz.R
import com.logie.blizz.game.Spinner
import com.logie.blizz.game.WindowsRuntime
import com.logie.blizz.importer.GameImportManager
import com.logie.blizz.importer.Stage
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext

/**
 * The shelf of box art and a game's own page, laid out for the screen it's on: on a narrow screen
 * (the Fold's cover screen) the page opens over the shelf; on a wide one (the inner screen) every
 * box sits in one row under the header, the chosen one lifted, its game below; half-open like a
 * laptop, the box art stands above the hinge with Play and the other games below it.
 */
/** Opens a game's import wizard (Repair, a status line): set by [Launcher]. */
internal val LocalOpenWizard = androidx.compose.runtime.staticCompositionLocalOf<(Game) -> Unit> { {} }

@Composable
fun Launcher(fold: Fold? = rememberFold()) {
    val context = LocalContext.current
    var openId by rememberSaveable { mutableStateOf<String?>(null) }
    var picking by remember { mutableStateOf<Game?>(null) }
    var launchAfterPick by remember { mutableStateOf(false) }
    // Links change when one's chosen, and when an app's installed or removed while we're away.
    var resumed by remember { mutableIntStateOf(0) }
    LifecycleEventEffect(Lifecycle.Event.ON_RESUME) { resumed++ }
    val version by Links.version.collectAsState()
    val linkKey = version * 10_000 + resumed

    val open = Games.all.firstOrNull { it.id == openId }
    var wizardFor by remember { mutableStateOf<Game?>(null) }
    LaunchedEffect(Unit) { Variants.load(context) }
    LaunchedEffect(resumed) { Games.all.flatMap { listOf(it) + it.variants }.filter { GameImportManager.importable(it.id) }.forEach { GameImportManager.refresh(context, it.id) } }
    fun play(shown: Game) {
        // The installation of it the page shows (StarCraft: classic or Remastered).
        val game = Variants.effective(shown)
        // Diablo, Diablo II, StarCraft and StarCraft II: imported into the app and played on its Winlator.
        if (GameImportManager.importable(game.id)) {
            val entry = GameImportManager.library(context).get(game.id)
            if (entry != null && java.io.File(entry.installPath, entry.executable).isFile) WindowsRuntime.play(context, entry) else wizardFor = game
            return
        }
        if (!Links.launch(context, game)) { launchAfterPick = true; picking = game }
    }
    fun chooseApp(game: Game) { launchAfterPick = false; picking = game }

    BlizzTheme {
        androidx.compose.runtime.CompositionLocalProvider(LocalOpenWizard provides { g: Game -> wizardFor = g }) {
        BoxWithConstraints(Modifier.fillMaxSize().background(Color.Black)) {
            val wide = maxWidth >= 600.dp && maxWidth > maxHeight * 0.75f
            when {
                fold?.tabletop == true && maxHeight >= 480.dp -> {
                    val game = open ?: Games.all.first()
                    TabletopPage(game, fold, linkKey, onSelect = { openId = it.id }, onPlay = { play(game) }, onChooseApp = { chooseApp(game) })
                }
                wide -> WideLauncher(open ?: Games.all.first(), linkKey, onSelect = { openId = it.id }, onPlay = ::play, onChooseApp = ::chooseApp)
                else -> {
                    Shelf(linkKey, selectedId = null, onOpen = { openId = it.id })
                    AnimatedContent(
                        targetState = open,
                        transitionSpec = { (fadeIn(tween(260)) + scaleIn(tween(260), initialScale = 0.96f)) togetherWith fadeOut(tween(200)) },
                        label = "page",
                    ) { game ->
                        if (game != null) {
                            GamePage(game, linkKey, onBack = { openId = null }, onPlay = { play(game) }, onChooseApp = { chooseApp(game) })
                        }
                    }
                    BackHandler(enabled = open != null) { openId = null }
                }
            }
        }
        }
        UpdateBanner()
        wizardFor?.let { game -> ImportWizard(game, onDismiss = { wizardFor = null }, onPlay = { play(game) }) }
        RuntimeOverlay()
        picking?.let { game ->
            AppPicker(
                game,
                onDismiss = { picking = null },
                onPick = { app ->
                    Links.set(context, game, app?.packageName)
                    picking = null
                    if (app != null && launchAfterPick) Links.launch(context, game)
                },
            )
        }
    }
}

/** The box art's shape: 3:4. */
const val COVER_RATIO = 3f / 4f

// The inner screen: one row of boxes

@Composable
private fun WideLauncher(game: Game, linkKey: Int, onSelect: (Game) -> Unit, onPlay: (Game) -> Unit, onChooseApp: (Game) -> Unit) {
    val context = LocalContext.current
    BoxWithConstraints(Modifier.fillMaxSize().background(Colors.Abyss)) {
        val width = maxWidth
        val height = maxHeight
        // The chosen game's art, blown up and dimmed, behind everything.
        Crossfade(game, animationSpec = tween(500), label = "backdrop") { shown ->
            Image(
                painterResource(shown.cover), contentDescription = null, contentScale = ContentScale.Crop,
                modifier = Modifier.fillMaxSize().graphicsLayer { alpha = 0.4f; scaleX = 1.2f; scaleY = 1.2f }
                    .let { if (Build.VERSION.SDK_INT >= 31) it.blur(32.dp) else it },
            )
        }
        Box(Modifier.fillMaxSize().background(Brush.verticalGradient(listOf(Colors.Abyss.copy(alpha = 0.5f), Colors.Abyss.copy(alpha = 0.95f)))))
        Column(
            Modifier.fillMaxSize().verticalScroll(rememberScrollState()).windowInsetsPadding(WindowInsets.safeDrawing.only(WindowInsetsSides.Horizontal + WindowInsetsSides.Bottom)),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Header(width, height * 0.62f)
            // Every box in one row, as wide as the screen allows; the chosen one lifted and lit.
            val gap = 8.dp
            val side = 20.dp
            val n = Games.all.size
            val fit = (min(width, 1400.dp) - side * 2 - gap * (n - 1)) / n
            val coverWidth = min(fit.coerceAtLeast(72.dp), 190.dp)
            val rowState = rememberLazyListState()
            LaunchedEffect(game) {
                val index = Games.all.indexOf(game)
                if (rowState.layoutInfo.visibleItemsInfo.none { it.index == index && it.offset >= 0 }) rowState.animateScrollToItem(maxOf(index - 1, 0))
            }
            LazyRow(
                state = rowState,
                modifier = Modifier.fillMaxWidth().height(coverWidth / COVER_RATIO * 1.08f + 28.dp),
                contentPadding = PaddingValues(start = side, end = side, top = 18.dp, bottom = 6.dp),
                horizontalArrangement = Arrangement.spacedBy(gap, Alignment.CenterHorizontally),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                itemsIndexed(Games.all, key = { _, it -> it.id }) { index, item ->
                    val chosen = item.id == game.id
                    val lift by animateFloatAsState(if (chosen) 1f else 0f, spring(dampingRatio = 0.6f, stiffness = 500f), label = "lift")
                    Box(Modifier.width(coverWidth).graphicsLayer {
                        val s = 1f + 0.06f * lift
                        scaleX = s; scaleY = s
                        translationY = -12.dp.toPx() * lift
                        alpha = 0.72f + 0.28f * lift
                    }) {
                        Cover(item, linkKey, index, chosen, Modifier.fillMaxWidth()) { onSelect(item) }
                    }
                }
            }
            // The chosen game.
            AnimatedContent(
                targetState = game,
                transitionSpec = {
                    val right = Games.all.indexOf(targetState) > Games.all.indexOf(initialState)
                    (fadeIn(tween(300)) + slideInHorizontally(tween(300)) { if (right) it / 6 else -it / 6 }) togetherWith
                        (fadeOut(tween(200)) + slideOutHorizontally(tween(200)) { if (right) -it / 6 else it / 6 })
                },
                label = "chosen",
                modifier = Modifier.widthIn(max = 900.dp).fillMaxWidth().padding(horizontal = 32.dp, vertical = 24.dp),
            ) { shown ->
                val linked = remember(linkKey, shown) { Links.packageFor(context, shown) }
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Text(shown.title, style = DisplayStyle.copy(fontSize = 30.sp, lineHeight = 36.sp, shadow = IceGlow))
                        shown.subtitle?.let { Text(it, style = DisplayStyle.copy(fontSize = 16.sp, color = Colors.Gold, shadow = GoldShadow)) }
                        Text(shown.year.toString(), style = MaterialTheme.typography.bodyMedium.copy(color = Colors.Mist))
                        VariantChooser(shown)
                    }
                    Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            PlayButton(shown, Modifier.widthIn(min = 220.dp)) { onPlay(shown) }
                            ControlsButton(shown)
                        }
                        ImportStatus(shown)
                        if (linked != null) {
                            Row(
                                Modifier.clip(CircleShape).clickable { onChooseApp(shown) }.padding(horizontal = 12.dp, vertical = 6.dp),
                                verticalAlignment = Alignment.CenterVertically,
                            ) {
                                AppIcon(linked, Modifier.size(22.dp))
                                Spacer(Modifier.width(8.dp))
                                Text(remember(linked) { Links.label(context, linked) }, style = MaterialTheme.typography.bodyMedium.copy(color = Colors.Mist))
                            }
                        }
                    }
                }
            }
        }
    }
}

// The shelf

@Composable
private fun Shelf(linkKey: Int, selectedId: String?, onOpen: (Game) -> Unit) {
    BoxWithConstraints(Modifier.fillMaxSize()) {
        val width = maxWidth
        val height = maxHeight
        Box(Modifier.fillMaxSize().background(Colors.Abyss))
        Column(
            Modifier.fillMaxSize().verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Header(width, height)
            Column(
                Modifier
                    .widthIn(max = 1100.dp)
                    .fillMaxWidth()
                    .windowInsetsPadding(WindowInsets.safeDrawing.only(WindowInsetsSides.Horizontal))
                    .padding(horizontal = 18.dp),
            ) {
                // Rows of equal length: as many across as fit, of 2, 4 or 8.
                val fit = ((width - 36.dp) / 150.dp).toInt()
                val columns = listOf(8, 4, 2).firstOrNull { it <= fit && Games.all.size % it == 0 } ?: 2
                CoverGrid(Games.all, columns, linkKey, selectedId, onOpen)
            }
        }
    }
}

/** The ice field, snow over it, slowly closing in; the logo over its lower edge. */
@Composable
private fun Header(screenWidth: Dp, screenHeight: Dp) {
    val headerHeight = min((screenWidth * 0.62f).coerceIn(200.dp, 420.dp), screenHeight * 0.42f)
    val logoWidth = min(min(screenWidth * 0.52f, headerHeight * 1.05f), 340.dp)
    val logoHeight = logoWidth * (1041f / 2000f)

    val motion = rememberInfiniteTransition(label = "header")
    val drift by motion.animateFloat(0f, 1f, infiniteRepeatable(tween(30_000, easing = FastOutSlowInEasing), RepeatMode.Reverse), label = "drift")
    val breathe by motion.animateFloat(0f, 1f, infiniteRepeatable(tween(3_600, easing = FastOutSlowInEasing), RepeatMode.Reverse), label = "breathe")
    val reveal = remember { Animatable(0f) }
    LaunchedEffect(Unit) {
        delay(120)
        reveal.animateTo(1f, tween(1_400, easing = FastOutSlowInEasing))
    }

    Box(Modifier.fillMaxWidth().height(headerHeight + logoHeight * 0.6f)) {
        Box(Modifier.fillMaxWidth().height(headerHeight).clipToBounds()) {
            Image(
                painterResource(R.drawable.blizz_header),
                contentDescription = null,
                contentScale = ContentScale.Crop,
                alignment = BiasAlignment(0.2f, -0.3f),
                modifier = Modifier.fillMaxSize().graphicsLayer {
                    val zoom = 1.03f + 0.06f * drift
                    scaleX = zoom; scaleY = zoom
                    transformOrigin = TransformOrigin(0.6f, 0.2f)
                    alpha = reveal.value
                },
            )
            Snow(alpha = reveal.value)
            Box(Modifier.fillMaxSize().background(Brush.verticalGradient(0.45f to Color.Transparent, 1f to Colors.Abyss)))
        }
        Image(
            painterResource(R.drawable.blizz_logo),
            contentDescription = stringResource(R.string.app_name),
            modifier = Modifier
                .align(Alignment.TopCenter)
                .offset(y = headerHeight - logoHeight * 0.55f)
                .width(logoWidth)
                .height(logoHeight)
                .graphicsLayer {
                    val v = reveal.value
                    alpha = ((v - 0.2f) / 0.8f).coerceIn(0f, 1f)
                    val scale = (0.95f + 0.05f * v) * (1f + 0.008f * breathe)
                    scaleX = scale; scaleY = scale
                },
        )
    }
}

@Composable
private fun CoverGrid(games: List<Game>, columns: Int, linkKey: Int, selectedId: String?, onOpen: (Game) -> Unit) {
    Column(Modifier.padding(top = 8.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
        games.chunked(columns).forEachIndexed { row, chunk ->
            Row(horizontalArrangement = Arrangement.spacedBy(14.dp)) {
                chunk.forEachIndexed { col, game ->
                    Cover(game, linkKey, row * columns + col, game.id == selectedId, Modifier.weight(1f)) { onOpen(game) }
                }
                repeat(columns - chunk.size) { Spacer(Modifier.weight(1f)) }
            }
        }
    }
}

/** A box on the shelf: lit and lifted when pressed or focused, the app it plays with in its corner. */
@Composable
private fun Cover(game: Game, linkKey: Int, index: Int, selected: Boolean, modifier: Modifier, onClick: () -> Unit) {
    val context = LocalContext.current
    val interaction = remember { MutableInteractionSource() }
    val pressed by interaction.collectIsPressedAsState()
    val focused by interaction.collectIsFocusedAsState()
    val lit by animateFloatAsState(if (pressed || focused || selected) 1f else 0f, spring(dampingRatio = 0.65f, stiffness = 700f), label = "lit")
    val appear = remember { Animatable(0f) }
    LaunchedEffect(Unit) {
        delay(500L + index * 70L)
        appear.animateTo(1f, tween(600, easing = FastOutSlowInEasing))
    }
    val linked = remember(linkKey) { Links.packageFor(context, game) }

    Box(
        modifier
            .aspectRatio(COVER_RATIO)
            .graphicsLayer {
                alpha = appear.value
                translationY = (1f - appear.value) * 24.dp.toPx()
                val s = 1f + 0.05f * lit
                scaleX = s; scaleY = s
            }
            .drawBehind {
                if (lit > 0f) drawRect(Brush.radialGradient(listOf(Colors.Ice.copy(alpha = 0.45f * lit), Color.Transparent), radius = size.maxDimension * 0.75f))
            }
            .clickable(interactionSource = interaction, indication = null, onClick = onClick),
    ) {
        Image(
            painterResource(game.cover),
            contentDescription = game.fullTitle,
            contentScale = ContentScale.Crop,
            modifier = Modifier.fillMaxSize().drawWithContent {
                drawContent()
                drawRect(Color.White.copy(alpha = 0.06f * lit))
                drawFrame(corner = if (lit > 0.5f) Colors.Ice else Colors.Gold, alpha = 0.55f + 0.45f * lit, line = Colors.Steel.copy(alpha = 0.9f))
            },
        )
        if (linked != null) {
            AppIcon(linked, Modifier.align(Alignment.BottomEnd).padding(7.dp).size(26.dp))
        }
    }
}

// A game's page

@Composable
private fun GamePage(game: Game, linkKey: Int, onBack: (() -> Unit)?, onPlay: () -> Unit, onChooseApp: () -> Unit) {
    val context = LocalContext.current
    val linked = remember(linkKey, game) { Links.packageFor(context, game) }
    BoxWithConstraints(Modifier.fillMaxSize().background(Colors.Abyss).clickable(interactionSource = remember { MutableInteractionSource() }, indication = null) {}) {
        val wide = maxWidth > maxHeight
        // The box art, blown up and dimmed, behind everything.
        Image(
            painterResource(game.cover), contentDescription = null, contentScale = ContentScale.Crop,
            modifier = Modifier.fillMaxSize().graphicsLayer { alpha = 0.55f; scaleX = 1.15f; scaleY = 1.15f }
                .let { if (Build.VERSION.SDK_INT >= 31) it.blur(28.dp) else it },
        )
        Box(Modifier.fillMaxSize().background(Brush.verticalGradient(listOf(Colors.Abyss.copy(alpha = 0.55f), Colors.Abyss.copy(alpha = 0.92f)))))
        Snow(flakes = 40, alpha = 0.6f)

        val coverHeight = if (wide) maxHeight * 0.74f else min(maxHeight * 0.5f, (maxWidth * 0.66f) * 1.5f)
        val pad = Modifier.windowInsetsPadding(WindowInsets.safeDrawing)
        if (wide) {
            Row(pad.fillMaxSize().padding(horizontal = 40.dp), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(40.dp, Alignment.CenterHorizontally)) {
                BigCover(game, Modifier.height(coverHeight))
                Details(game, linked, onPlay, onChooseApp, Modifier.widthIn(max = 380.dp), Alignment.Start)
            }
        } else {
            Column(pad.fillMaxSize().verticalScroll(rememberScrollState()).padding(top = 56.dp, bottom = 24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                BigCover(game, Modifier.height(coverHeight))
                Spacer(Modifier.height(26.dp))
                Details(game, linked, onPlay, onChooseApp, Modifier.padding(horizontal = 28.dp), Alignment.CenterHorizontally)
            }
        }
        if (onBack != null) Icon(
            Icons.AutoMirrored.Filled.ArrowBack, contentDescription = null, tint = Colors.Text,
            modifier = pad.padding(8.dp).size(44.dp).clip(CircleShape).clickable(onClick = onBack).padding(10.dp),
        )
    }
}

@Composable
private fun BigCover(game: Game, modifier: Modifier) {
    val float = rememberInfiniteTransition(label = "float")
    val y by float.animateFloat(0f, 1f, infiniteRepeatable(tween(4_000, easing = FastOutSlowInEasing), RepeatMode.Reverse), label = "y")
    Image(
        painterResource(game.cover), contentDescription = game.fullTitle, contentScale = ContentScale.Crop,
        modifier = modifier
            .aspectRatio(COVER_RATIO)
            .graphicsLayer { translationY = -6.dp.toPx() * y }
            .drawBehind { drawRect(Brush.radialGradient(listOf(Colors.Ice.copy(alpha = 0.35f), Color.Transparent), radius = size.maxDimension * 0.8f)) }
            .drawWithContent { drawContent(); drawFrame(arm = 14.dp.toPx(), stroke = 1.8.dp.toPx()) },
    )
}

@Composable
private fun Details(game: Game, linked: String?, onPlay: () -> Unit, onChooseApp: () -> Unit, modifier: Modifier, align: Alignment.Horizontal) {
    val textAlign = if (align == Alignment.Start) TextAlign.Start else TextAlign.Center
    Column(modifier, horizontalAlignment = align, verticalArrangement = Arrangement.spacedBy(6.dp)) {
        Text(game.title, style = DisplayStyle.copy(fontSize = 28.sp, lineHeight = 34.sp, shadow = IceGlow), textAlign = textAlign)
        game.subtitle?.let { Text(it, style = DisplayStyle.copy(fontSize = 16.sp, color = Colors.Gold, shadow = GoldShadow), textAlign = textAlign) }
        Text(game.year.toString(), style = MaterialTheme.typography.bodyMedium.copy(color = Colors.Mist), textAlign = textAlign)
        VariantChooser(game)
        Spacer(Modifier.height(16.dp))
        Row(verticalAlignment = Alignment.CenterVertically) {
            PlayButton(game, Modifier.widthIn(min = 220.dp), onPlay)
            ControlsButton(game)
        }
        ImportStatus(game)
        if (linked != null) {
            Spacer(Modifier.height(6.dp))
            Row(
                Modifier.clip(CircleShape).clickable(onClick = onChooseApp).padding(horizontal = 12.dp, vertical = 8.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                AppIcon(linked, Modifier.size(24.dp))
                Spacer(Modifier.width(8.dp))
                val context = LocalContext.current
                Text(remember(linked) { Links.label(context, linked) }, style = MaterialTheme.typography.bodyMedium.copy(color = Colors.Mist))
            }
        }
    }
}

/** Half-open: the box art standing on the top half, Play and the shelf lying on the bottom. */
@Composable
private fun TabletopPage(game: Game, fold: Fold, linkKey: Int, onSelect: (Game) -> Unit, onPlay: () -> Unit, onChooseApp: () -> Unit) {
    val context = LocalContext.current
    val linked = remember(linkKey, game) { Links.packageFor(context, game) }
    Box(Modifier.fillMaxSize().background(Colors.Abyss)) {
        Crossfade(game, animationSpec = tween(320), label = "backdrop") { shown ->
            Image(
                painterResource(shown.cover), contentDescription = null, contentScale = ContentScale.Crop,
                modifier = Modifier.fillMaxSize().graphicsLayer { alpha = 0.5f; scaleX = 1.15f; scaleY = 1.15f }
                    .let { if (Build.VERSION.SDK_INT >= 31) it.blur(28.dp) else it },
            )
        }
        Box(Modifier.fillMaxSize().background(Colors.Abyss.copy(alpha = 0.7f)))
        Snow(flakes = 40, alpha = 0.6f)
        Column(Modifier.fillMaxSize().windowInsetsPadding(WindowInsets.safeDrawing.only(WindowInsetsSides.Horizontal))) {
            // Above the hinge.
            Row(
                Modifier.fillMaxWidth().height(fold.start).windowInsetsPadding(WindowInsets.safeDrawing.only(WindowInsetsSides.Top)).padding(vertical = 14.dp, horizontal = 28.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(28.dp, Alignment.CenterHorizontally),
            ) {
                Crossfade(game, animationSpec = tween(320), label = "cover", modifier = Modifier.fillMaxHeight()) { shown ->
                    BigCover(shown, Modifier.fillMaxHeight())
                }
                Column(Modifier.widthIn(max = 360.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text(game.title, style = DisplayStyle.copy(fontSize = 28.sp, lineHeight = 34.sp, shadow = IceGlow))
                    game.subtitle?.let { Text(it, style = DisplayStyle.copy(fontSize = 16.sp, color = Colors.Gold, shadow = GoldShadow)) }
                    Text(game.year.toString(), style = MaterialTheme.typography.bodyMedium.copy(color = Colors.Mist))
                    VariantChooser(game)
                }
            }
            Spacer(Modifier.height(fold.end - fold.start))
            // Below it: within thumb's reach.
            Column(
                Modifier.fillMaxWidth().weight(1f).windowInsetsPadding(WindowInsets.safeDrawing.only(WindowInsetsSides.Bottom)).padding(top = 14.dp, bottom = 10.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(10.dp),
            ) {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(14.dp)) {
                    PlayButton(game, Modifier.widthIn(min = 240.dp), onPlay)
                    ControlsButton(game)
                    ImportStatus(game)
                    if (linked != null) AppIcon(linked, Modifier.size(40.dp).clip(CircleShape).clickable(onClick = onChooseApp).padding(4.dp))
                }
                LazyRow(
                    Modifier.fillMaxWidth().weight(1f),
                    contentPadding = PaddingValues(horizontal = 24.dp, vertical = 8.dp),
                    horizontalArrangement = Arrangement.spacedBy(12.dp, Alignment.CenterHorizontally),
                ) {
                    itemsIndexed(Games.all, key = { _, it -> it.id }) { index, item ->
                        Cover(item, linkKey, index, item.id == game.id, Modifier.fillMaxHeight()) { onSelect(item) }
                    }
                }
            }
        }
    }
}

// Imported games

/** Play, or Auto Import for an importable game that isn't in the app yet. */
@Composable
private fun PlayButton(shown: Game, modifier: Modifier, onPlay: () -> Unit) {
    val game = effectiveGame(shown)
    val states by GameImportManager.states.collectAsState()
    val importable = GameImportManager.importable(game.id)
    val state = states[game.id]
    val label = when {
        !importable -> stringResource(R.string.play)
        state?.running == true -> "Importing…"
        state?.entry != null -> stringResource(R.string.play)
        else -> "Auto Import"
    }
    FrameButton(label, modifier, onClick = onPlay)
}

/** An imported game's status, which opens its wizard (Repair, Reimport, details). */
@Composable
private fun ImportStatus(shown: Game) {
    val game = effectiveGame(shown)
    if (!GameImportManager.importable(game.id)) return
    val states by GameImportManager.states.collectAsState()
    val state = states[game.id] ?: return
    val open = LocalOpenWizard.current
    val text = when {
        state.running -> state.progress?.label ?: "Importing…"
        else -> statusLabel(state.record.stage, state.record.outcome, state.record.launchTest, game.id)
    }
    if (text.isEmpty() && state.entry == null) return
    Row(
        Modifier.clip(CircleShape).clickable { open(game) }.padding(horizontal = 12.dp, vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(text, style = MaterialTheme.typography.bodySmall.copy(color = if (state.record.stage == Stage.READY) Colors.Ice else Colors.Mist))
        if (state.entry != null && !state.running) Text("  ·  Repair", style = MaterialTheme.typography.bodySmall.copy(color = Colors.Mist))
    }
}

/** Starting an imported game: the runtime's install and Windows' first start, or what went wrong. */
@Composable
private fun RuntimeOverlay() {
    val state by WindowsRuntime.state.collectAsState()
    when (val s = state) {
        is WindowsRuntime.State.Preparing -> Dialog(onDismissRequest = {}, properties = DialogProperties(usePlatformDefaultWidth = false)) {
            Column(Modifier.fillMaxSize().background(Colors.Abyss.copy(alpha = 0.92f)), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(18.dp, Alignment.CenterVertically)) {
                Spinner(44.dp)
                Text(
                    when (s.step) {
                        WindowsRuntime.Step.RUNTIME -> "Installing the Windows runtime" + (s.progress?.let { " ${(it * 100).toInt()}%" } ?: "")
                        WindowsRuntime.Step.WINDOWS -> "Preparing Windows"
                        WindowsRuntime.Step.STARTING -> "Starting"
                    },
                    style = MaterialTheme.typography.titleMedium, color = Colors.Mist,
                )
            }
        }
        is WindowsRuntime.State.Failed -> Dialog(onDismissRequest = { WindowsRuntime.dismiss() }) {
            Column(Modifier.drawBehind { drawRect(Colors.Deep); drawFrame() }.padding(20.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                Text(s.message, style = MaterialTheme.typography.bodyLarge)
                FrameButton("OK", Modifier.align(Alignment.End)) { WindowsRuntime.dismiss() }
            }
        }
        else -> {}
    }
}

// Choosing the app a game's played with

@Composable
private fun AppPicker(game: Game, onDismiss: () -> Unit, onPick: (InstalledApp?) -> Unit) {
    val context = LocalContext.current
    val apps by produceState<List<InstalledApp>?>(null) { value = withContext(Dispatchers.IO) { Links.installed(context) } }
    var query by remember { mutableStateOf("") }
    val linked = remember(game) { Links.packageFor(context, game) }
    Dialog(onDismissRequest = onDismiss, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Column(
            Modifier
                .padding(20.dp)
                .widthIn(max = 520.dp)
                .fillMaxWidth()
                .fillMaxHeight(0.8f)
                .drawBehind {
                    drawRect(Brush.verticalGradient(listOf(Colors.Deep, Colors.Night)))
                    drawFrame()
                }
                .padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            FrameTitle(stringResource(R.string.choose_app))
            Row(
                Modifier.fillMaxWidth().drawBehind { drawFrame(corner = Colors.Mist, arm = 6.dp.toPx()) }.padding(horizontal = 12.dp, vertical = 10.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Icon(Icons.Default.Search, contentDescription = stringResource(R.string.search), tint = Colors.Mist, modifier = Modifier.size(20.dp))
                Spacer(Modifier.width(10.dp))
                BasicTextField(
                    query, { query = it }, singleLine = true,
                    textStyle = MaterialTheme.typography.bodyLarge, cursorBrush = SolidColor(Colors.Ice),
                    modifier = Modifier.weight(1f),
                )
            }
            val shown = apps?.filter { query.isBlank() || it.label.contains(query.trim(), ignoreCase = true) }
            if (shown == null) {
                Box(Modifier.fillMaxWidth().weight(1f))
            } else {
                LazyColumn(Modifier.fillMaxWidth().weight(1f), contentPadding = PaddingValues(vertical = 4.dp)) {
                    if (linked != null && query.isBlank()) item {
                        PickerRow(null, stringResource(R.string.unlink), selected = false) { onPick(null) }
                    }
                    items(shown, key = { it.packageName }) { app ->
                        PickerRow(app.packageName, app.label, selected = app.packageName == linked) { onPick(app) }
                    }
                }
            }
        }
    }
}

@Composable
private fun PickerRow(packageName: String?, label: String, selected: Boolean, onClick: () -> Unit) {
    Row(
        Modifier
            .fillMaxWidth()
            .drawBehind { if (selected) { drawRect(Colors.Ice.copy(alpha = 0.1f)); drawFrame(arm = 6.dp.toPx(), line = null) } }
            .clickable(onClick = onClick)
            .padding(horizontal = 10.dp, vertical = 9.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        if (packageName != null) AppIcon(packageName, Modifier.size(36.dp))
        else Icon(Icons.Default.Block, contentDescription = null, tint = Colors.Mist, modifier = Modifier.size(36.dp).padding(6.dp))
        Spacer(Modifier.width(14.dp))
        Text(label, style = MaterialTheme.typography.titleMedium, color = if (selected) Colors.Glow else Colors.Text, maxLines = 1)
    }
}

@Composable
private fun AppIcon(packageName: String, modifier: Modifier) {
    val context = LocalContext.current
    val bitmap by produceState<ImageBitmap?>(null, packageName) {
        value = withContext(Dispatchers.IO) { Links.icon(context, packageName)?.toBitmap(128, 128)?.asImageBitmap() }
    }
    bitmap?.let { Image(it, contentDescription = null, modifier = modifier) } ?: Box(modifier)
}
