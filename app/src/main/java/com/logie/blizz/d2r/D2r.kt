package com.logie.blizz.d2r

import android.content.Context
import com.logie.blizz.importer.CancelToken
import com.logie.blizz.importer.DownloadManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.withContext
import java.io.File

/**
 * Diablo II: Resurrected, as the second version of the Diablo II tile: played in D2R Mobile
 * (github.com/jhaizhou-ops/d2r-mobile, MIT), an open-source Android port that runs the game's own
 * ARM64 program from the Nintendo Switch release, on Vulkan. It is an app of its own, not part of
 * Blizzard: Play opens it, and Blizzard installs it and says what it needs. The game's files are the
 * player's own Switch files, turned into an import pack on a computer (the port's tool needs Python,
 * the .NET SDK and the Vulkan SDK's shader tools, which a phone doesn't have) and copied to the
 * phone's `Download/S2X/D2R Mobile/`.
 */
object D2r {
    const val GAME_ID = "diablo2_resurrected"
    const val PACKAGE = "com.xiaoboluo.d2r"

    /** The newest release's APK (GitHub answers with a redirect to the current release's file). */
    const val APK_URL = "https://github.com/jhaizhou-ops/d2r-mobile/releases/latest/download/D2RMobile-android.apk"
    const val PROJECT_URL = "https://github.com/jhaizhou-ops/d2r-mobile"

    const val COMPUTER_COMMAND = "python3 dm/tools/d2rm_android.py <Update directory of your game files> <output directory>"

    /** The steps the port's own guide gives, in the order to do them. */
    val STEPS: List<String> = listOf(
        "Own the Switch release of Diablo II: Resurrected with Reign of the Warlock, updated to 1.0.34.0 (PC 3.3.94012). Dump its ExeFS and RomFS from your own console (nxdumptool).",
        "On a computer, get the port's source from the same release as the app (github.com/jhaizhou-ops/d2r-mobile) and run: $COMPUTER_COMMAND. It makes an `android` folder (about 670 MB).",
        "Copy that `android` folder, and the 18 .data archives with .build.config from RomFS/data as a folder named `data`, to Download/S2X/D2R Mobile/ on the phone (about 6 GB).",
        "Install D2R Mobile with the button here, open it, allow All files access, and let it import the pack. After that, Play on this tile opens it.",
    )

    fun installed(context: Context): Boolean = context.packageManager.getLaunchIntentForPackage(PACKAGE) != null

    fun installedVersion(context: Context): String? =
        runCatching { context.packageManager.getPackageInfo(PACKAGE, 0).versionName }.getOrNull()

    sealed interface State {
        data object Idle : State
        data class Downloading(val done: Long, val total: Long) : State
        data class Ready(val apk: File) : State
        data class Failed(val message: String) : State
    }

    private val _state = MutableStateFlow<State>(State.Idle)
    val state: StateFlow<State> = _state

    /** Asks for the setup dialog (a page's pill, or Play with the app not installed). */
    private val _setupRequested = MutableStateFlow(false)
    val setupRequested: StateFlow<Boolean> = _setupRequested

    fun requestSetup(on: Boolean = true) {
        _setupRequested.value = on
    }

    fun dismissState() {
        _state.value = State.Idle
    }

    /** Downloads the newest D2R Mobile APK and checks it is that app; [State.Ready] when it can be installed. */
    suspend fun download(context: Context) {
        if (_state.value is State.Downloading) return
        _state.value = State.Downloading(0, 0)
        val dir = File(context.cacheDir, "updates").also { it.mkdirs() }
        val target = File(dir, "D2RMobile-android.apk")
        target.delete()
        File(dir, "D2RMobile-android.apk.part").delete()
        try {
            withContext(Dispatchers.IO) {
                DownloadManager().download(APK_URL, target, CancelToken(), onProgress = { done, total -> _state.value = State.Downloading(done, total) })
            }
            val info = context.packageManager.getPackageArchiveInfo(target.path, 0)
            if (info?.packageName != PACKAGE) {
                target.delete()
                _state.value = State.Failed("What came down isn't D2R Mobile's app. Try again later.")
            } else _state.value = State.Ready(target)
        } catch (e: Exception) {
            _state.value = State.Failed(e.message ?: e.javaClass.simpleName)
        }
    }
}
