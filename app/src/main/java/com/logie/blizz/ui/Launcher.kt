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
fun Launcher() {
    val context = LocalContext.current
    // The game the home shows: the one chosen last time.
    var openId by rememberSaveable { mutableStateOf<String?>(context.getSharedPreferences("home", android.content.Context.MODE_PRIVATE).getString("game", null)) }
    LaunchedEffect(openId) { openId?.let { context.getSharedPreferences("home", android.content.Context.MODE_PRIVATE).edit().putString("game", it).apply() } }
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
    var musicFor by remember { mutableStateOf<Game?>(null) }
    var settingsOpen by remember { mutableStateOf(false) }
    remember { TileSettings.load(context) }
    LaunchedEffect(Unit) { Variants.load(context) }
    // Music: the launcher's track on the shelf, a game's from the moment its page is open (the version chosen: Warcraft III's, StarCraft's).
    val chosenVersions by Variants.selection.collectAsState()
    // The home always shows a game (the first until one is chosen): its music plays, not the launcher's.
    val shown = open ?: Games.all.first()
    val musicKey = com.logie.blizz.music.MusicCatalog.keyFor(Variants.effective(shown, chosenVersions).id)
    LaunchedEffect(Unit) { com.logie.blizz.music.MusicDownloads.startIfMissing(context) }
    // The launch test no longer runs by itself (the user: "turn off the launch test"); the settings' button starts it.
    // A test the app died in is still reported at start.
    LaunchedEffect(Unit) { com.logie.blizz.selftest.SelfTest.reportInterruptedOnly(context) }
    val musicGame = Variants.effective(shown, chosenVersions).id
    val customMusic by com.logie.blizz.music.MusicCustom.version.collectAsState()
    LaunchedEffect(musicKey, musicGame, customMusic) { com.logie.blizz.music.MusicPlayer.select(context, musicKey, musicGame) }
    // World of Warcraft: Forever: a game that fell back here says why by itself (its own crash file, sent as a report).
    LaunchedEffect(resumed) { com.logie.blizz.forever.ForeverPlay.reportClientStop(context) }
    LaunchedEffect(resumed) { withContext(Dispatchers.IO) { Games.all.flatMap { listOf(it) + it.variants }.filter { GameImportManager.importable(it.id) }.forEach { GameImportManager.refresh(context, it.id) }; GameImportManager.reinstallStale(context) } }
    fun play(shown: Game) {
        // The installation of it the page shows (StarCraft: classic or Remastered).
        val game = Variants.effective(shown)
        // World of Warcraft: Forever runs its own offline realm on the phone (its own server package and client),
        // not the WoW-app import; its Play/Install is handled apart ([com.logie.blizz.forever.ForeverPlay]).
        if (game.id == "wow_forever") { com.logie.blizz.forever.ForeverPlay.play(context); return }
        // Wrath++ (experimental): made from the Wrath+ import, so it plays from that entry ([com.logie.blizz.game.WowPlay] with wrathpp).
        if (game.id == com.logie.blizz.game.WowPlay.WRATHPP_ID) {
            val wrath = GameImportManager.library(context).get("wow")
            if (wrath != null && java.io.File(wrath.installPath, wrath.executable).isFile) com.logie.blizz.game.WowPlay.play(context, wrath, wrathpp = true)
            else android.widget.Toast.makeText(context, "Wrath++ is made from Wrath+: import World of Warcraft (Wrath+) first.", android.widget.Toast.LENGTH_LONG).show()
            return
        }
        // Diablo, Diablo II, StarCraft and StarCraft II: imported into the app and played on its Winlator.
        if (GameImportManager.importable(game.id)) {
            // An install this update left behind (its recipe changed): made again first, in the wizard, where its progress shows.
            if (GameImportManager.stale(context, game.id)) { GameImportManager.reinstall(context, game.id); wizardFor = game; return }
            val entry = GameImportManager.library(context).get(game.id)
            if (entry != null && (entry.runtime == com.logie.blizz.importer.LibraryEntry.RUNTIME_EXTERNAL || game.id in WOW_MODES) && java.io.File(entry.installPath, entry.executable).isFile) {
                // World of Warcraft: the realm and the client, from the imported files (the WoW app isn't needed).
                com.logie.blizz.game.WowPlay.play(context, entry)
            } else if (entry != null && java.io.File(entry.installPath, entry.executable).isFile) {
                // Warcraft I and II run natively (Stratagus); the rest on the app's Winlator.
                when (entry.runtime) {
                    com.logie.blizz.warsmash.WarsmashRuntime.RUNTIME -> com.logie.blizz.warsmash.WarsmashRuntime.play(context, entry)
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
            LocalOpenMusic provides { g: Game -> musicFor = Variants.effective(g) },
            LocalChooseApp provides { g: Game -> chooseApp(g) },
            LocalOpenSettings provides { settingsOpen = true },
        ) {
        // The home: the game chosen, its art behind it, the library beside it.
        ModernHome(linkKey, open ?: Games.all.first(), onSelect = { openId = it.id }, onPlay = ::play, onChooseApp = ::chooseApp)
        // (inside the providers: the menus and dialogs open one another through them)
        UpdateBanner()
        splashFor?.let { SplashDialog(it, onDismiss = { splashFor = null }) }
        holdFor?.let { HoldMenu(it, onDismiss = { holdFor = null }) }
        optionsFor?.let { GameOptionsDialog(it, onDismiss = { optionsFor = null }) }
        addonsFor?.let { WowAddonManager(it.id, onDismiss = { addonsFor = null }) }
        if (modulesOpen) WowModuleManager(onDismiss = { modulesOpen = false })
        controlsFor?.let { ControlsScreen(it, onDismiss = { controlsFor = null }) }
        musicFor?.let { MusicDialog(it, onDismiss = { musicFor = null }) }
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

/** The box art's shape: 2:3 (the SteamGridDB grid scale). */
const val COVER_RATIO = 2f / 3f

// The inner screen: one row of boxes

// The shelf

// A game's page

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

/** A line of [gameId]'s own from [com.logie.blizz.game.LoadingLines], another every few seconds while the dialog is up; none twice in one load. */
@Composable
private fun rememberLoadingLine(gameId: String?): String {
    var line by remember(gameId) { mutableStateOf(com.logie.blizz.game.LoadingLines.next(gameId)) }
    LaunchedEffect(gameId) {
        while (true) {
            delay(3500)
            line = com.logie.blizz.game.LoadingLines.next(gameId)
        }
    }
    return line
}

/** Starting an imported game: the runtime's install and Windows' first start, or what went wrong. */
@Composable
private fun RuntimeOverlay() {
    val wow by com.logie.blizz.game.WowPlay.state.collectAsState()
    val forever by com.logie.blizz.forever.ForeverPlay.state.collectAsState()
    val state by WindowsRuntime.state.collectAsState()
    val context = LocalContext.current
    // One loading screen from the realm's start to the game's own window: World of Warcraft's realm, then Windows, then the
    // game, with no blink back to the launcher between them. It stays up until the game's screen has taken over.
    val running = state as? WindowsRuntime.State.Preparing
    val foreverBusy = forever as? com.logie.blizz.forever.ForeverPlay.State.Preparing
    val loadingId = running?.gameId ?: (wow as? com.logie.blizz.game.WowPlay.State.Preparing)?.gameId ?: foreverBusy?.let { "wow_forever" }
    val busy = running != null || wow is com.logie.blizz.game.WowPlay.State.Preparing || foreverBusy != null
    var held by remember { mutableStateOf<String?>(null) }
    var holding by remember { mutableStateOf(false) }
    // A paused client download has no game window coming: its screen goes at once.
    var downloading by remember { mutableStateOf(false) }
    if (busy) { held = loadingId ?: held; holding = true; downloading = foreverBusy?.pausable == true }
    LaunchedEffect(busy) {
        if (busy) return@LaunchedEffect
        if (downloading) { downloading = false; holding = false; return@LaunchedEffect }
        // Until the launcher is out of sight (the game's screen is up), at most a few seconds.
        val until = System.currentTimeMillis() + 4_000
        while (com.logie.blizz.MainActivity.visible && System.currentTimeMillis() < until && state !is WindowsRuntime.State.Failed && wow !is com.logie.blizz.game.WowPlay.State.Failed) delay(100)
        holding = false
    }
    if (holding && state !is WindowsRuntime.State.Failed && wow !is com.logie.blizz.game.WowPlay.State.Failed && forever !is com.logie.blizz.forever.ForeverPlay.State.Failed) {
        Dialog(onDismissRequest = {}, properties = DialogProperties(usePlatformDefaultWidth = false, decorFitsSystemWindows = false)) {
            Box(Modifier.fillMaxSize()) {
                // The runtime's install is the one wait with a number to show.
                val percent = if (running?.step == WindowsRuntime.Step.RUNTIME) running.progress?.let { " ${(it * 100).toInt()}%" }.orEmpty() else ""
                val fb = forever as? com.logie.blizz.forever.ForeverPlay.State.Preparing
                if (fb != null) {
                    val fp = fb.progress?.let { " ${(it * 100).toInt()}%" }.orEmpty()
                    com.logie.blizz.game.Loading(held, fb.message + fp)
                    // The client download takes hours: it can be paused, and the next Play goes on from where it stopped.
                    if (fb.pausable) {
                        FrameButton("Pause download", Modifier.align(Alignment.BottomEnd).padding(24.dp), primary = false) {
                            com.logie.blizz.forever.ForeverPlay.pauseDownload()
                        }
                    }
                } else {
                    com.logie.blizz.game.Loading(held, rememberLoadingLine(held) + percent)
                }
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
    when (val f = forever) {
        is com.logie.blizz.forever.ForeverPlay.State.Failed -> Dialog(onDismissRequest = { com.logie.blizz.forever.ForeverPlay.dismiss() }, properties = DialogProperties(usePlatformDefaultWidth = false)) {
            val clipboard = androidx.compose.ui.platform.LocalClipboardManager.current
            Column(Modifier.padding(16.dp).panel().padding(20.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                Column(Modifier.heightIn(max = 460.dp).verticalScroll(rememberScrollState())) { Text(f.message, style = MaterialTheme.typography.bodyLarge) }
                Row(Modifier.align(Alignment.End), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    FrameButton("Copy", primary = false) { clipboard.setText(androidx.compose.ui.text.AnnotatedString(f.message)) }
                    FrameButton("OK") { com.logie.blizz.forever.ForeverPlay.dismiss() }
                }
            }
        }
        is com.logie.blizz.forever.ForeverPlay.State.NeedsClient -> Dialog(onDismissRequest = { com.logie.blizz.forever.ForeverPlay.dismiss() }, properties = DialogProperties(usePlatformDefaultWidth = false)) {
            // Android's folder picker: the app's own storage can't be reached from a file manager, so the client is copied in from wherever it was put.
            val pickClient = androidx.activity.compose.rememberLauncherForActivityResult(androidx.activity.result.contract.ActivityResultContracts.OpenDocumentTree()) { tree ->
                if (tree != null) com.logie.blizz.forever.ForeverPlay.importClient(context, tree)
            }
            val resuming = remember { com.logie.blizz.forever.ForeverPlay.downloadPaused(context) }
            Column(Modifier.padding(16.dp).widthIn(max = 560.dp).panel().padding(20.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                FrameTitle("Download the Forever client?")
                Text(
                    "World of Warcraft: Forever needs its game client once: about ${com.logie.blizz.forever.ForeverPlay.CLIENT_SIZE_GB} GB from " +
                        "Blizzard's servers (it needs a little more than that free on the phone).\n\n" +
                        "This phone is on a metered connection (mobile data). Download anyway, wait for Wi-Fi (Play downloads it " +
                        "by itself there), or choose a Forever client folder already on the phone (from a PC's Battle.net install: " +
                        "the one with .build.info, Data and _forever_).\n\n" +
                        "To connect the client to the local realm, the Forever Launcher must be in the client folder (it sets the server key).",
                    style = MaterialTheme.typography.bodyMedium,
                )
                Row(Modifier.align(Alignment.End), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    FrameButton("Cancel", primary = false) { com.logie.blizz.forever.ForeverPlay.dismiss() }
                    FrameButton("Choose client folder", primary = false) { pickClient.launch(null) }
                    FrameButton(if (resuming) "Resume download" else "Download") {
                        com.logie.blizz.forever.ForeverPlay.dismiss()
                        com.logie.blizz.forever.ForeverPlay.downloadClient(context)
                    }
                }
            }
        }
        is com.logie.blizz.forever.ForeverPlay.State.NeedsLauncher -> Dialog(onDismissRequest = { com.logie.blizz.forever.ForeverPlay.dismiss() }, properties = DialogProperties(usePlatformDefaultWidth = false)) {
            // The Forever Launcher is the person's to supply: picked here once, kept in the client folder, run at every Play.
            val pickLauncher = androidx.activity.compose.rememberLauncherForActivityResult(androidx.activity.result.contract.ActivityResultContracts.OpenDocument()) { uri ->
                if (uri != null) com.logie.blizz.forever.ForeverPlay.importLauncher(context, uri, thenPlay = true)
            }
            Column(Modifier.padding(16.dp).widthIn(max = 560.dp).panel().padding(20.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                FrameTitle("The Forever Launcher is missing")
                Text(
                    "The realm and the game are ready: the game starts and logs in to the realm on this phone.\n\n" +
                        "It can't enter the realm yet. The game checks the world server's identity against Blizzard's own key, " +
                        "and disconnects from any other server (\"You have been disconnected\", BLZ51901023). The Forever Launcher " +
                        "(ForeverLauncher.exe, from the realm's makers) is what lets the game accept this realm. This app can't " +
                        "make or download it: pick the file once and it is run at every Play. For the current Tauri/WebView2 " +
                        "launcher the app installs the WebView2 runtime it needs on the first run (a ~250 MB download); a native " +
                        "launcher works too.",
                    style = MaterialTheme.typography.bodyMedium,
                )
                Row(Modifier.align(Alignment.End), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    FrameButton("Cancel", primary = false) { com.logie.blizz.forever.ForeverPlay.dismiss() }
                    FrameButton("Start anyway", primary = false) {
                        com.logie.blizz.forever.ForeverPlay.dismiss()
                        com.logie.blizz.forever.ForeverPlay.playWithoutLauncher(context)
                    }
                    FrameButton("Choose the launcher file") { pickLauncher.launch(arrayOf("*/*")) }
                }
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
