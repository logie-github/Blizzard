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

    fun play(context: Context, entry: LibraryEntry) {
        if (_state.value is State.Preparing) return
        val app = context.applicationContext
        val profile = LaunchProfile.of(entry.controlProfile)
        val size = GameSettings.gameSize(context, profile)
        _state.value = State.Preparing(Step.RUNTIME)
        scope.launch {
            try {
                run(app, entry, profile, size)
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

    fun dismiss() {
        if (_state.value is State.Failed) _state.value = State.Idle
    }

    fun onLauncherShown(context: Context) {
        val intent = pending ?: return
        pending = null
        context.startActivity(intent)
    }

    private suspend fun run(context: Context, entry: LibraryEntry, profile: LaunchProfile, size: Pair<Int, Int>) {
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
        val container = container(context, width, height, entry.gameId)
        withContext(Dispatchers.IO) { seedSaves(context, container, entry) }
        withContext(Dispatchers.IO) { registerInstall(context, container, entry) }
        withContext(Dispatchers.IO) { writeDDrawConfig(container, entry.gameId) }

        _state.value = State.Preparing(Step.STARTING)
        val intent = Intent(context, XServerDisplayActivity::class.java)
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            .putExtra("container_id", container.id)
            // The program's path alone (Winlator makes it a Windows path); its arguments apart
            // (patches/winlator/0005): paths in them would otherwise break that conversion.
            .putExtra("exec_path", program.path)
            .putExtra("exec_args", entry.arguments)
            // The app's touch controls (GestureView) in place of Winlator's touchpad.
            .putExtra("gestures", true)
            .putExtra(GestureView.EXTRA_GAME, entry.gameId)
            .putExtra(GestureView.EXTRA_PROFILE, profile.id)
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
        return "D:" + paths.games.path + "S:" + paths.saves.path
    }

    /**
     * The classic 2D games (Diablo II, StarCraft, Warcraft II) draw with DirectDraw, which Wine's own
     * version runs at a few frames a second and plays no videos through; cnc-ddraw draws them with OpenGL.
     */
    private fun dxwrapperConfig(gameId: String): String =
        if (gameId in setOf("diablo2", "starcraft", "warcraft2")) "ddrawWrapper=cnc-ddraw" else ""

    /**
     * cnc-ddraw's settings for the classic games: its GDI renderer (a window of the game's own size
     * stretched to the screen, no OpenGL or Direct3D needed, which a phone's Wine may not have), the
     * game's size kept in proportion, one CPU thread for the old programs. Written every start.
     */
    private fun writeDDrawConfig(container: Container, gameId: String) {
        if (dxwrapperConfig(gameId).isEmpty()) return
        val ini = File(container.rootDir, ".wine/drive_c/ProgramData/cnc-ddraw/ddraw.ini")
        ini.parentFile?.mkdirs()
        ini.writeText(
            "[ddraw]\nrenderer=gdi\nfullscreen=true\nwindowed=false\nmaintas=true\nboxing=false\nadjmouse=true\n" +
                "vsync=false\nmaxfps=60\nsinglecpu=true\nnoactivateapp=false\nhook_peekmessage=false\n",
        )
    }

    /** The games' Windows: made the first time, its screen and drives set every time. */
    private suspend fun container(context: Context, width: Int, height: Int, gameId: String): Container {
        val manager = ContainerManager(context)
        val drives = drives(context)
        val screenSize = "${width}x$height"
        val existing = manager.containers.firstOrNull { it.name == CONTAINER_NAME }
        if (existing != null) {
            existing.setScreenSize(screenSize)
            existing.setDrives(drives)
            existing.setDXWrapperConfig(dxwrapperConfig(gameId))
            withContext(Dispatchers.IO) { existing.saveData() }
            return existing
        }
        val defaults = Container(0)
        val data = JSONObject()
            .put("name", CONTAINER_NAME)
            .put("screenSize", screenSize)
            .put("envVars", defaults.getEnvVars())
            .put("graphicsDriver", defaults.getGraphicsDriver())
            .put("dxwrapper", defaults.getDXWrapper())
            .put("dxwrapperConfig", dxwrapperConfig(gameId))
            .put("audioDriver", defaults.getAudioDriver())
            .put("wincomponents", defaults.getWinComponents())
            .put("drives", drives)
            .put("hudMode", defaults.getHUDMode().toInt())
            .put("startupSelection", defaults.getStartupSelection().toInt())
            .put("box64Preset", defaults.getBox64Preset())
            .put("desktopTheme", defaults.getDesktopTheme())
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
