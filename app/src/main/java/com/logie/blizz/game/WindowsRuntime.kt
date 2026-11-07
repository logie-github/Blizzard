package com.logie.blizz.game

import android.content.Context
import android.content.Intent
import com.logie.blizz.MainActivity
import com.logie.blizz.R
import com.logie.blizz.importer.GameImportManager
import com.logie.blizz.importer.LibraryEntry
import com.winlator.XServerDisplayActivity
import com.winlator.container.Container
import com.winlator.container.ContainerManager
import com.winlator.xenvironment.RootFS
import com.winlator.xenvironment.RootFSInstaller
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.File
import kotlin.coroutines.resume

/**
 * Starts an imported game ([LibraryEntry]) on Winlator, which runs Windows programs on the phone
 * (Wine, Box64 and its own X server; scripts/prepare-winlator.sh builds it into the app), as
 * YeaBwoi's Warcraft app does:
 *
 * 1. Winlator's runtime is installed, the first time and after an update that changes it;
 * 2. Blizzard's servers are put out of the games' reach ([Offline]): no Battle.net, ever;
 * 3. the games' Windows (one Winlator container) is made the first time, with the games' folder as
 *    drive D: and their saves folder as S:, its screen set to the game's ([LaunchProfile]);
 * 4. saves and profiles imported with a game go into that Windows, never over ones there;
 * 5. Winlator's game screen starts the game's program, with the app's touch controls ([GestureView]).
 */
object WindowsRuntime {
    sealed interface State {
        data object Idle : State
        data class Preparing(val step: Step, val progress: Float? = null) : State
        data class Failed(val message: String) : State
    }

    enum class Step { RUNTIME, WINDOWS, STARTING }

    private const val CONTAINER_NAME = "Blizzard"

    private val _state = MutableStateFlow<State>(State.Idle)
    val state: StateFlow<State> = _state

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)

    /** The game screen, waiting for the launcher to be on screen (Android starts no screens from the background). */
    private var pending: Intent? = null

    /** [size]: the X screen's, when the caller has worked it out already (World of Warcraft, whose Config.wtf must match it). */
    fun play(context: Context, entry: LibraryEntry, size: Pair<Int, Int>? = null) {
        if (_state.value is State.Preparing) return
        val app = context.applicationContext
        val profile = LaunchProfile.of(entry.controlProfile)
        // The person's launch options ([LaunchOptions]): the game's own screen, or a phone-shaped one at their lines.
        val options = LaunchOptionsStore(app).get(entry.gameId).resolve(entry.gameId, hardware(app))
        val size = size ?: gameSize(context, entry.gameId, profile)
        _state.value = State.Preparing(Step.RUNTIME)
        scope.launch {
            try {
                run(app, entry, profile, size, options)
                _state.value = State.Idle
            } catch (e: kotlinx.coroutines.CancellationException) {
                _state.value = State.Idle
                throw e
            } catch (e: Exception) {
                _state.value = State.Failed(app.getString(R.string.game_error, e.message ?: e.javaClass.simpleName))
                com.logie.blizz.reports.BugReports.report(
                    app, "${entry.title} launch", e.message ?: e.javaClass.simpleName,
                    listOf("Game" to entry.gameId, "Version" to entry.clientVersion, "Program" to entry.executable, "Arguments" to entry.arguments),
                    log = e.stackTraceToString(),
                )
            }
        }
    }

    /**
     * The game's screen (Winlator's X screen) for [gameId] on the screen the launcher is on: the screen's own size for the games
     * that follow its shape, else the game's own. The one place it's worked out: World of Warcraft's Config.wtf (gxResolution)
     * must be this same size, or the game's window is smaller than the screen and touches land beside it.
     */
    fun gameSize(context: Context, gameId: String, profile: LaunchProfile = LaunchProfile.of(gameId)): Pair<Int, Int> {
        val options = LaunchOptionsStore(context.applicationContext).get(gameId).resolve(gameId)
        return options.lines?.let { lines ->
            val (w, h) = GameSettings.screenSize(context)
            Screen.resolutionFor(w, h, lines)
        } ?: GameSettings.gameSize(context, profile)
    }

    /** The phone as the options see it: an Adreno GPU gets Turnip. */
    private fun hardware(context: Context): LaunchOptions.Hardware =
        LaunchOptions.Hardware(adreno = runCatching { com.winlator.core.GPUHelper.getAdrenoModelId(context) > 0 }.getOrDefault(false))

    fun dismiss() {
        if (_state.value is State.Failed) _state.value = State.Idle
    }

    fun onLauncherShown(context: Context) {
        val intent = pending ?: return
        pending = null
        context.startActivity(intent)
    }

    private suspend fun run(context: Context, entry: LibraryEntry, profile: LaunchProfile, size: Pair<Int, Int>, options: LaunchOptions.Resolved) {
        val folder = File(entry.installPath)
        val program = File(folder, entry.executable)
        if (!program.isFile) throw IllegalStateException(context.getString(R.string.game_error_missing, entry.title))

        _state.value = State.Preparing(Step.RUNTIME, 0f)
        val installed = withContext(Dispatchers.IO) {
            RootFSInstaller.installIfNeeded(context) { percent -> _state.value = State.Preparing(Step.RUNTIME, percent / 100f) }
        }
        if (!installed) throw IllegalStateException(context.getString(R.string.game_error_runtime))
        withContext(Dispatchers.IO) { keepOffline(context) }

        _state.value = State.Preparing(Step.WINDOWS)
        val (width, height) = size
        val container = container(context, width, height, options)
        withContext(Dispatchers.IO) { seedSaves(context, container, entry) }
        withContext(Dispatchers.IO) { registerInstall(context, container, entry) }
        withContext(Dispatchers.IO) { writeDDrawConfig(container, entry.gameId, options) }
        // Legion: the Battle.net certificate bundle the patched client trusts goes into the game's Windows.
        val legion = entry.gameId == WowPlay.GAME_ID && entry.clientVersion == LegionClientSetup.VERSION
        if (legion) {
            withContext(Dispatchers.IO) {
                val layout = com.logie.blizz.wow.WowLayout.legion(context)
                LegionClientSetup.installCertificateBundle(com.logie.blizz.wow.RealmSpecsAccess.certBundle(layout), File(container.rootDir, ".wine/drive_c"))
            }
        }
        // Warcraft III: its screen and install path in the games' registry ([Wc3Setup]).
        if (entry.gameId.startsWith("warcraft3")) {
            withContext(Dispatchers.IO) {
                runCatching { Wc3Setup.apply(container.rootDir, size.first, size.second, "D:\\" + File(entry.installPath).name + "\\") }
            }
        }
        // Wine's errors and the libraries it loads, kept for the game menu's report ([GameLog]).
        android.preference.PreferenceManager.getDefaultSharedPreferences(context).edit()
            .putBoolean("enable_wine_debug", true).putString("wine_debug_channels", "err,loaddll").apply()

        _state.value = State.Preparing(Step.STARTING)
        val intent = Intent(context, XServerDisplayActivity::class.java)
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            .putExtra("container_id", container.id)
            // The program's path alone (Winlator makes it a Windows path); its arguments apart
            // (patches/winlator/0005): paths in them would otherwise break that conversion.
            .putExtra("exec_path", program.path)
            .putExtra("exec_args", entry.arguments)
            // Legion's start-up protection needs the Box64 with the signal-flags fix (Winlator patch 0007).
            .apply { if (legion) putExtra("box64_version", LegionClientSetup.BOX64) }
            // The app's touch controls (GestureView) in place of Winlator's touchpad.
            .putExtra("gestures", true)
            .putExtra(GestureView.EXTRA_GAME, entry.gameId)
            .putExtra(GestureView.EXTRA_PROFILE, profile.id)
            .apply {
                // World of Warcraft: the account the other app logged in with by itself, typed at the login screen.
                if (entry.gameId == WowPlay.GAME_ID) (when (entry.clientVersion) {
                    OctoClientSetup.VERSION -> com.logie.blizz.wow.WowLogin.octo(context)
                    LegionClientSetup.VERSION -> com.logie.blizz.wow.WowLogin.legion(context)
                    else -> com.logie.blizz.wow.WowLogin.get(context)
                })?.let {
                    putExtra(GestureView.EXTRA_LOGIN_NAME, it.name).putExtra(GestureView.EXTRA_LOGIN_PASSWORD, it.password)
                }
            }
        if (MainActivity.visible) context.startActivity(intent) else pending = intent
    }

    /** The runtime's hosts file: Blizzard's names nowhere ([Offline]). */
    private fun keepOffline(context: Context) {
        val etc = File(RootFS.find(context).rootDir, "etc")
        etc.mkdirs()
        File(etc, "hosts").writeText(Offline.hosts(true))
        File(etc, "nsswitch.conf").writeText(Offline.nsswitch())
    }

    /** The drives: D: the games, S: their saves (the app's folders). */
    fun drives(context: Context): String {
        val paths = GameImportManager.paths(context)
        paths.games.mkdirs()
        paths.saves.mkdirs()
        paths.staging.mkdirs()
        // T: the importers' work folder, where a game's own installer is run ([com.logie.blizz.importer.InstallerRun]).
        return "D:" + paths.games.path + "S:" + paths.saves.path + "T:" + paths.staging.path
    }

    /**
     * cnc-ddraw's settings for the classic games (Diablo II, StarCraft, Warcraft II), which draw with
     * DirectDraw: [LaunchOptions.ddrawIni] (the renderer, frame limit, CPU pinning and the rest the
     * person chose, and why the defaults are what they are). Written at every start, so a changed
     * option takes effect on the next one; nothing when the game is not drawn through cnc-ddraw.
     */
    private fun writeDDrawConfig(container: Container, gameId: String, options: LaunchOptions.Resolved) {
        val text = LaunchOptions.ddrawIni(options, gameId) ?: return
        val ini = File(container.rootDir, ".wine/drive_c/ProgramData/cnc-ddraw/ddraw.ini")
        ini.parentFile?.mkdirs()
        ini.writeText(text)
    }

    /** The games' Windows: made the first time, its screen, drives and launch options set every time. */
    private suspend fun container(context: Context, width: Int, height: Int, options: LaunchOptions.Resolved): Container {
        val manager = ContainerManager(context)
        val drives = drives(context)
        val screenSize = "${width}x$height"
        val existing = manager.containers.firstOrNull { it.name == CONTAINER_NAME }
        if (existing != null) {
            existing.setScreenSize(screenSize)
            existing.setDrives(drives)
            // The container is shared by all the games, so every value is written at every start,
            // the defaults too, never leaving the last game's behind. Winlator re-extracts its
            // Direct3D/DirectDraw files by itself when the wrapper, its config (the DirectDraw choice)
            // or its version differ from the cached id (XServerDisplayActivity.extractDXWrapperFiles);
            // when anything it caches differs from the last start's, the cached id is dropped as well.
            existing.setDXWrapper(options.dxwrapper)
            existing.setDXWrapperConfig(options.dxwrapperConfig)
            existing.setGraphicsDriver(options.graphicsDriver)
            existing.setBox64Preset(options.box64Preset)
            val store = LaunchOptionsStore(context)
            if (store.lastApplied() != options.cacheKey) {
                existing.putExtra("dxwrapper", null)
                store.setLastApplied(options.cacheKey)
            }
            withContext(Dispatchers.IO) { existing.saveData() }
            return existing
        }
        val defaults = Container(0)
        val data = JSONObject()
            .put("name", CONTAINER_NAME)
            .put("screenSize", screenSize)
            .put("envVars", defaults.getEnvVars())
            .put("graphicsDriver", options.graphicsDriver)
            .put("dxwrapper", options.dxwrapper)
            .put("dxwrapperConfig", options.dxwrapperConfig)
            .put("audioDriver", defaults.getAudioDriver())
            .put("wincomponents", defaults.getWinComponents())
            .put("drives", drives)
            .put("hudMode", defaults.getHUDMode().toInt())
            .put("startupSelection", defaults.getStartupSelection().toInt())
            .put("box64Preset", options.box64Preset)
            .put("desktopTheme", defaults.getDesktopTheme())
        LaunchOptionsStore(context).setLastApplied(options.cacheKey)
        val created = suspendCancellableCoroutine { done ->
            manager.createContainerAsync(data) { container -> done.resume(container) }
        }
        return created ?: throw IllegalStateException(context.getString(R.string.game_error_windows))
    }

    /**
     * What the games' own installers write to the registry, which they read their data folder from:
     * StarCraft's InstallPath (and its programs), in both views of HKLM a 32-bit program can have.
     * Written every start, so a moved or reset installation is found again.
     */
    private fun registerInstall(context: Context, container: Container, entry: LibraryEntry) {
        if (entry.gameId != "starcraft") return
        val system = File(container.rootDir, ".wine/system.reg")
        if (!system.isFile) return
        val folder = File(entry.installPath)
        val dos = "D:\\${folder.name}\\"
        com.winlator.core.WineRegistryEditor(system).use { registry ->
            for (key in listOf("Software\\Blizzard Entertainment\\Starcraft", "Software\\Wow6432Node\\Blizzard Entertainment\\Starcraft")) {
                registry.setStringValue(key, "InstallPath", dos)
                registry.setStringValue(key, "Program", dos + "StarCraft.exe")
                registry.setStringValue(key, "StarEditPath", dos + "StarEdit.exe")
            }
        }
    }

    /**
     * Saves and profiles that came with an import (Diablo II's old save folder, StarCraft II's
     * Documents), copied into the games' Windows where the game reads them; never over a file there.
     */
    private fun seedSaves(context: Context, container: Container, entry: LibraryEntry) {
        val user = File(container.rootDir, ".wine/drive_c/users/xuser")
        val saves = GameImportManager.paths(context).saves(entry.gameId)
        val pairs = when (entry.gameId) {
            "diablo2" -> listOf(File(saves, "import") to File(user, "Saved Games/Diablo II"))
            "starcraft2" -> listOf(File(saves, "Documents/StarCraft II") to File(user, "Documents/StarCraft II"))
            else -> emptyList()
        }
        for ((from, to) in pairs) {
            if (!from.isDirectory) continue
            from.walkTopDown().filter { it.isFile }.forEach { f ->
                val target = File(to, f.relativeTo(from).path)
                if (!target.exists()) f.copyTo(target)
            }
        }
    }
}
