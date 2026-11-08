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
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.clickable
import androidx.compose.foundation.combinedClickable
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
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
import androidx.compose.foundation.layout.heightIn
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
internal val LocalOpenSplash = androidx.compose.runtime.staticCompositionLocalOf<(Game) -> Unit> { {} }
/** Hold a box: its menu ([HoldMenu]). */
internal val LocalOpenHold = androidx.compose.runtime.staticCompositionLocalOf<(Game) -> Unit> { {} }

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
    var splashFor by remember { mutableStateOf<Game?>(null) }
    var holdFor by remember { mutableStateOf<Game?>(null) }
    var optionsFor by remember { mutableStateOf<Game?>(null) }
    var addonsFor by remember { mutableStateOf<Game?>(null) }
    var modulesOpen by remember { mutableStateOf(false) }
    var controlsFor by remember { mutableStateOf<Game?>(null) }
    var settingsOpen by remember { mutableStateOf(false) }
    remember { TileSettings.load(context) }
    val tiles by TileSettings.state.collectAsState()
    val tileMode = tiles.mode == TileSettings.Mode.TILES
    LaunchedEffect(Unit) { Variants.load(context) }
    // Music: the launcher's track on the shelf, a game's from the moment its page is open (the version chosen: Warcraft III's, StarCraft's).
    val chosenVersions by Variants.selection.collectAsState()
    val musicKey = com.logie.blizz.music.MusicCatalog.keyFor(open?.let { Variants.effective(it, chosenVersions).id })
    LaunchedEffect(Unit) { com.logie.blizz.music.MusicDownloads.startIfMissing(context) }
    // The launch test no longer runs by itself (the user: "turn off the launch test"); the settings' button starts it.
    // A test the app died in is still reported at start.
    LaunchedEffect(Unit) { com.logie.blizz.selftest.SelfTest.reportInterruptedOnly(context) }
    val musicGame = open?.let { Variants.effective(it, chosenVersions).id }
    val customMusic by com.logie.blizz.music.MusicCustom.version.collectAsState()
    LaunchedEffect(musicKey, musicGame, customMusic) { com.logie.blizz.music.MusicPlayer.select(context, musicKey, musicGame) }
    LaunchedEffect(resumed) { withContext(Dispatchers.IO) { Games.all.flatMap { listOf(it) + it.variants }.filter { GameImportManager.importable(it.id) }.forEach { GameImportManager.refresh(context, it.id) } } }
    fun play(shown: Game) {
        // The installation of it the page shows (StarCraft: classic or Remastered).
        val game = Variants.effective(shown)
        // Diablo, Diablo II, StarCraft and StarCraft II: imported into the app and played on its Winlator.
        if (GameImportManager.importable(game.id)) {
            val entry = GameImportManager.library(context).get(game.id)
            if (entry != null && (entry.runtime == com.logie.blizz.importer.LibraryEntry.RUNTIME_EXTERNAL || game.id in WOW_MODES) && java.io.File(entry.installPath, entry.executable).isFile) {
                // World of Warcraft: the realm and the client, from the imported files (the WoW app isn't needed).
                com.logie.blizz.game.WowPlay.play(context, entry)
            } else if (entry != null && java.io.File(entry.installPath, entry.executable).isFile) {
                // Warcraft I and II run natively (Stratagus); the rest on the app's Winlator.
                when (entry.runtime) {
                    com.logie.blizz.game.StratagusRuntime.RUNTIME -> com.logie.blizz.game.StratagusRuntime.play(context, entry)
                    // Diablo II: Resurrected: its files are imported; the native host isn't in the app yet ([com.logie.blizz.d2r.D2r]).
                    com.logie.blizz.importer.LibraryEntry.RUNTIME_D2R, com.logie.blizz.importer.LibraryEntry.RUNTIME_PENDING ->
                        android.widget.Toast.makeText(context, "${entry.title}'s files are imported. Running it in the app isn't built yet.", android.widget.Toast.LENGTH_LONG).show()
                    else -> WindowsRuntime.play(context, entry)
                }
            } else wizardFor = game
            return
        }
        if (!Links.launch(context, game)) { launchAfterPick = true; picking = game }
    }
    fun chooseApp(game: Game) { launchAfterPick = false; picking = game }

    BlizzTheme {
        androidx.compose.runtime.CompositionLocalProvider(
            LocalOpenWizard provides { g: Game -> wizardFor = g },
            LocalOpenSplash provides { g: Game -> splashFor = Variants.effective(g) },
            LocalOpenHold provides { g: Game -> holdFor = g },
            LocalOpenOptions provides { g: Game -> optionsFor = Variants.effective(g) },
            LocalOpenAddons provides { g: Game -> addonsFor = Variants.effective(g) },
            LocalOpenModules provides { modulesOpen = true },
            LocalOpenControls provides { g: Game -> controlsFor = Variants.effective(g) },
            LocalChooseApp provides { g: Game -> chooseApp(g) },
            LocalOpenSettings provides { settingsOpen = true },
        ) {
        BoxWithConstraints(Modifier.fillMaxSize().background(Color.Black)) {
            val wide = maxWidth >= 600.dp && maxWidth > maxHeight * 0.75f
            when {
                // The modern look (the default): one screen, the game chosen and the library beside it.
                Look.modern -> ModernHome(linkKey, open ?: Games.all.first(), onSelect = { openId = it.id }, onPlay = ::play, onChooseApp = ::chooseApp)
                !tileMode && fold?.tabletop == true && maxHeight >= 480.dp -> {
                    val game = open ?: Games.all.first()
                    TabletopPage(game, fold, linkKey, onSelect = { openId = it.id }, onPlay = { play(game) }, onChooseApp = { chooseApp(game) })
                }
                !tileMode && wide -> WideLauncher(open ?: Games.all.first(), linkKey, onSelect = { openId = it.id }, onPlay = ::play, onChooseApp = ::chooseApp)
                else -> {
                    if (tileMode) TileScreen(onOpen = { openId = it.id }) else Shelf(linkKey, selectedId = null, onOpen = { openId = it.id })
                    AnimatedContent(
                        targetState = open,
                        transitionSpec = { (fadeIn(tween(260)) + scaleIn(tween(260), initialScale = 0.96f)) togetherWith fadeOut(tween(200)) },
                        label = "page",
                    ) { game ->
                        if (game != null) {
                            GamePage(game, linkKey, onBack = { openId = null }, onPlay = { play(game) }, onChooseApp = { chooseApp(game) })
                        }
                    }
                    BackHandler(enabled = open != null && !Look.modern) { openId = null }
                }
            }
        }
        // (inside the providers: the menus and dialogs open one another through them)
        UpdateBanner()
        splashFor?.let { SplashDialog(it, onDismiss = { splashFor = null }) }
        holdFor?.let { HoldMenu(it, onDismiss = { holdFor = null }) }
        optionsFor?.let { GameOptionsDialog(it, onDismiss = { optionsFor = null }) }
        addonsFor?.let { WowAddonManager(it.id, onDismiss = { addonsFor = null }) }
        if (modulesOpen) WowModuleManager(onDismiss = { modulesOpen = false })
        controlsFor?.let { ControlsScreen(it, onDismiss = { controlsFor = null }) }
        if (settingsOpen) SettingsDialog(onDismiss = { settingsOpen = false })
        wizardFor?.let { game -> ImportWizard(game, onDismiss = { wizardFor = null }, onPlay = { play(game) }) }
        RuntimeOverlay()
        SelfTestDialog()
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
}

/** The classic look's logo menu: its settings, or the modern look. */
@Composable
private fun LogoMenu(onSettings: () -> Unit, onDismiss: () -> Unit) {
    val context = LocalContext.current
    Dialog(onDismissRequest = onDismiss) {
        Column(Modifier.widthIn(max = 380.dp).fillMaxWidth().panel().padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            FrameTitle("Blizzard")
            FrameButton("Modern look", Modifier.fillMaxWidth()) { onDismiss(); Look.set(context, true) }
            FrameButton("Settings", Modifier.fillMaxWidth(), primary = false, onClick = onSettings)
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
                painterResource(effectiveGame(shown).cover), contentDescription = null, contentScale = ContentScale.Crop,
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
                val chosen = effectiveGame(shown)
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Text(chosen.title, style = DisplayStyle.copy(fontSize = 30.sp, lineHeight = 36.sp, shadow = IceGlow))
                        chosen.subtitle?.let { Text(it, style = DisplayStyle.copy(fontSize = 16.sp, color = Colors.Gold, shadow = GoldShadow)) }
                        Text(chosen.year.toString(), style = MaterialTheme.typography.bodyMedium.copy(color = Colors.Mist))
                        VariantChooser(shown)
                    }
                    Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            PlayButton(shown, Modifier.widthIn(min = 220.dp)) { onPlay(shown) }
                            ControlsButton(shown)
                            LaunchOptionsButton(shown)
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
@OptIn(ExperimentalFoundationApi::class)
@Composable
internal fun Header(screenWidth: Dp, screenHeight: Dp) {
    val openSettings = LocalOpenSettings.current
    val hapticLogo = LocalHapticFeedback.current
    var logoMenu by remember { mutableStateOf(false) }
    if (logoMenu) LogoMenu(onSettings = { logoMenu = false; openSettings() }, onDismiss = { logoMenu = false })
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
                // Hold the logo: the settings, or back to the modern look.
                .combinedClickable(interactionSource = remember { MutableInteractionSource() }, indication = null, onClick = {}, onLongClick = { hapticLogo.performHapticFeedback(HapticFeedbackType.LongPress); logoMenu = true })
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
@OptIn(ExperimentalFoundationApi::class)
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
    val haptic = LocalHapticFeedback.current
    val openHold = LocalOpenHold.current

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
            .combinedClickable(
                interactionSource = interaction, indication = null, onClick = onClick,
                onLongClick = { haptic.performHapticFeedback(HapticFeedbackType.LongPress); openHold(game) },
            ),
    ) {
        Image(
            boxArt(game),
            contentDescription = effectiveGame(game).fullTitle,
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
            boxArt(game), contentDescription = null, contentScale = ContentScale.Crop,
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

@OptIn(ExperimentalFoundationApi::class)
@Composable
private fun BigCover(game: Game, modifier: Modifier) {
    val haptic = LocalHapticFeedback.current
    val openHold = LocalOpenHold.current
    val float = rememberInfiniteTransition(label = "float")
    val y by float.animateFloat(0f, 1f, infiniteRepeatable(tween(4_000, easing = FastOutSlowInEasing), RepeatMode.Reverse), label = "y")
    Image(
        boxArt(game), contentDescription = effectiveGame(game).fullTitle, contentScale = ContentScale.Crop,
        modifier = modifier
            .aspectRatio(COVER_RATIO)
            .graphicsLayer { translationY = -6.dp.toPx() * y }
            .drawBehind { drawRect(Brush.radialGradient(listOf(Colors.Ice.copy(alpha = 0.35f), Color.Transparent), radius = size.maxDimension * 0.8f)) }
            .drawWithContent { drawContent(); drawFrame(arm = 14.dp.toPx(), stroke = 1.8.dp.toPx()) }
            .combinedClickable(interactionSource = remember { MutableInteractionSource() }, indication = null, onClick = {}, onLongClick = {
                haptic.performHapticFeedback(HapticFeedbackType.LongPress); openHold(game)
            }),
    )
}

@Composable
private fun Details(game: Game, linked: String?, onPlay: () -> Unit, onChooseApp: () -> Unit, modifier: Modifier, align: Alignment.Horizontal) {
    val textAlign = if (align == Alignment.Start) TextAlign.Start else TextAlign.Center
    val chosen = effectiveGame(game)
    Column(modifier, horizontalAlignment = align, verticalArrangement = Arrangement.spacedBy(6.dp)) {
        Text(chosen.title, style = DisplayStyle.copy(fontSize = 28.sp, lineHeight = 34.sp, shadow = IceGlow), textAlign = textAlign)
        chosen.subtitle?.let { Text(it, style = DisplayStyle.copy(fontSize = 16.sp, color = Colors.Gold, shadow = GoldShadow), textAlign = textAlign) }
        Text(chosen.year.toString(), style = MaterialTheme.typography.bodyMedium.copy(color = Colors.Mist), textAlign = textAlign)
        VariantChooser(game)
        Spacer(Modifier.height(16.dp))
        Row(verticalAlignment = Alignment.CenterVertically) {
            PlayButton(game, Modifier.widthIn(min = 220.dp), onPlay)
            ControlsButton(game)
            LaunchOptionsButton(game)
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
                painterResource(effectiveGame(shown).cover), contentDescription = null, contentScale = ContentScale.Crop,
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
                val chosen = effectiveGame(game)
                Column(Modifier.widthIn(max = 360.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text(chosen.title, style = DisplayStyle.copy(fontSize = 28.sp, lineHeight = 34.sp, shadow = IceGlow))
                    chosen.subtitle?.let { Text(it, style = DisplayStyle.copy(fontSize = 16.sp, color = Colors.Gold, shadow = GoldShadow)) }
                    Text(chosen.year.toString(), style = MaterialTheme.typography.bodyMedium.copy(color = Colors.Mist))
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
                    LaunchOptionsButton(game)
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

/** The picture of [game]'s box (the version its page shows): see [boxArtOf]. */
@Composable
internal fun boxArt(game: Game): androidx.compose.ui.graphics.painter.Painter = boxArtOf(effectiveGame(game))

/** The picture of this exact [shown] version's box: the person's own for it (set in its settings, its long-press dialog or the tile layout's Change art), else the built-in cover. */
@Composable
internal fun boxArtOf(shown: Game): androidx.compose.ui.graphics.painter.Painter {
    val context = LocalContext.current
    val state by TileSettings.state.collectAsState()
    val custom = remember(shown.id, state.artVersion) {
        TileSettings.artFile(context, shown.id, false)?.let { runCatching { android.graphics.BitmapFactory.decodeFile(it.path)?.asImageBitmap() }.getOrNull() }
    }
    return custom?.let { androidx.compose.ui.graphics.painter.BitmapPainter(it) } ?: painterResource(shown.cover)
}

/** The World of Warcraft modes: each plays through [com.logie.blizz.game.WowPlay], whatever runtime an earlier import recorded (Legion's and OctoWoW's said "not ported"). */
private val WOW_MODES = setOf("wow", "wow_legion", "wow_octowow")

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
    // Shown while something is happening or has gone wrong; a finished import says nothing under Play.
    if (!state.running && state.record.stage != Stage.FAILED) return
    val text = if (state.running) state.progress?.label ?: "Importing…" else statusLabel(state.record.stage, state.record.outcome, state.record.launchTest, game.id)
    if (text.isEmpty()) return
    Row(
        Modifier.clip(CircleShape).clickable { open(game) }.padding(horizontal = 12.dp, vertical = 6.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(text, style = MaterialTheme.typography.bodySmall.copy(color = if (state.record.stage == Stage.READY) Colors.Ice else Colors.Mist))
    }
}

/** A line from [com.logie.blizz.game.LoadingLines], another every few seconds while the dialog is up. */
@Composable
private fun rememberLoadingLine(): String {
    var line by remember { mutableStateOf(com.logie.blizz.game.LoadingLines.next()) }
    LaunchedEffect(Unit) {
        while (true) {
            delay(3500)
            line = com.logie.blizz.game.LoadingLines.next(line)
        }
    }
    return line
}

/** Starting an imported game: the runtime's install and Windows' first start, or what went wrong. */
@Composable
private fun RuntimeOverlay() {
    val wow by com.logie.blizz.game.WowPlay.state.collectAsState()
    val state by WindowsRuntime.state.collectAsState()
    // One loading screen from the realm's start to the game's own window: World of Warcraft's realm, then Windows, then the
    // game, with no blink back to the launcher between them. It stays up until the game's screen has taken over.
    val running = state as? WindowsRuntime.State.Preparing
    val loadingId = running?.gameId ?: (wow as? com.logie.blizz.game.WowPlay.State.Preparing)?.gameId
    val busy = running != null || wow is com.logie.blizz.game.WowPlay.State.Preparing
    var held by remember { mutableStateOf<String?>(null) }
    var holding by remember { mutableStateOf(false) }
    if (busy) { held = loadingId ?: held; holding = true }
    LaunchedEffect(busy) {
        if (busy) return@LaunchedEffect
        // Until the launcher is out of sight (the game's screen is up), at most a few seconds.
        val until = System.currentTimeMillis() + 4_000
        while (com.logie.blizz.MainActivity.visible && System.currentTimeMillis() < until && state !is WindowsRuntime.State.Failed && wow !is com.logie.blizz.game.WowPlay.State.Failed) delay(100)
        holding = false
    }
    if (holding && state !is WindowsRuntime.State.Failed && wow !is com.logie.blizz.game.WowPlay.State.Failed) {
        Dialog(onDismissRequest = {}, properties = DialogProperties(usePlatformDefaultWidth = false, decorFitsSystemWindows = false)) {
            Box(Modifier.fillMaxSize()) {
                // The runtime's install is the one wait with a number to show.
                val percent = if (running?.step == WindowsRuntime.Step.RUNTIME) running.progress?.let { " ${(it * 100).toInt()}%" }.orEmpty() else ""
                com.logie.blizz.game.Loading(held, rememberLoadingLine() + percent)
            }
        }
    }
    when (val w = wow) {
        is com.logie.blizz.game.WowPlay.State.Failed -> Dialog(onDismissRequest = { com.logie.blizz.game.WowPlay.dismiss() }, properties = DialogProperties(usePlatformDefaultWidth = false)) {
            val clipboard = androidx.compose.ui.platform.LocalClipboardManager.current
            Column(Modifier.padding(16.dp).panel().padding(20.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                Column(Modifier.heightIn(max = 460.dp).verticalScroll(rememberScrollState())) {
                    Text(w.message, style = if (w.message.length > 160) MaterialTheme.typography.bodySmall else MaterialTheme.typography.bodyLarge)
                }
                Row(Modifier.align(Alignment.End), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    FrameButton("Copy", primary = false) { clipboard.setText(androidx.compose.ui.text.AnnotatedString(w.message)) }
                    FrameButton("OK") { com.logie.blizz.game.WowPlay.dismiss() }
                }
            }
        }
        else -> {}
    }
    when (val s = state) {
        is WindowsRuntime.State.Failed -> Dialog(onDismissRequest = { WindowsRuntime.dismiss() }) {
            Column(Modifier.panel().padding(20.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
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
                .panel()
                .padding(18.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            FrameTitle(stringResource(R.string.choose_app))
            Row(
                Modifier.fillMaxWidth().then(if (Look.modern) Modifier.box(selected = false) else Modifier.drawBehind { drawFrame(corner = Colors.Mist, arm = 6.dp.toPx()) }).padding(horizontal = 12.dp, vertical = 10.dp),
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
            .then(if (Look.modern) Modifier.box(selected = selected) else Modifier.drawBehind { if (selected) { drawRect(Colors.Ice.copy(alpha = 0.1f)); drawFrame(arm = 6.dp.toPx(), line = null) } })
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
