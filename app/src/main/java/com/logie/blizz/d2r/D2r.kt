package com.logie.blizz.d2r

import com.logie.blizz.importer.deleteTree

import com.logie.blizz.importer.CancelToken
import com.logie.blizz.importer.GamePaths
import com.logie.blizz.importer.ZipExtractor
import org.json.JSONObject
import java.io.File

/**
 * Diablo II: Resurrected, the second version of the Diablo II tile, played in Blizzard itself through
 * D2R Mobile's open-source (MIT) native host (github.com/jhaizhou-ops/d2r-mobile): it runs the Nintendo
 * Switch release's own ARM64 program on the phone, on Vulkan. None of it is packaged with Blizzard:
 * the **module** is downloaded first, from the project's own release (its native libraries and the
 * rest of what the release APK carries, never run as an app of its own), and kept in `modules/d2r`.
 * The game's files are the player's own Switch packages, imported by
 * [com.logie.blizz.importer.Diablo2ResurrectedImporter].
 */
object D2r {
    const val GAME_ID = "diablo2_resurrected"
    const val REPO = "jhaizhou-ops/d2r-mobile"
    const val APK = "D2RMobile-android.apk"
    const val PROJECT_URL = "https://github.com/jhaizhou-ops/d2r-mobile"

    fun moduleDir(paths: GamePaths) = File(paths.root, "modules/d2r")

    /** The release the downloaded module is from (its tag), or null when there is none. */
    fun moduleTag(paths: GamePaths): String? = runCatching {
        JSONObject(File(moduleDir(paths), "module.json").readText()).getString("tag")
    }.getOrNull()?.takeIf { libraries(paths).isNotEmpty() }

    /** The module's native libraries (the .so files in lib/arm64-v8a). */
    fun libraries(paths: GamePaths): List<File> =
        File(moduleDir(paths), "lib/arm64-v8a").listFiles { f -> f.isFile && f.name.endsWith(".so") }?.sortedBy { it.name } ?: emptyList()

    fun hasModule(paths: GamePaths) = moduleTag(paths) != null && libraries(paths).any { it.name == "libdm.so" }

    /** What of the release APK the module keeps: its native libraries, its code and its assets. */
    fun wanted(entry: String): Boolean =
        entry.startsWith("lib/arm64-v8a/") && entry.endsWith(".so") || entry.matches(Regex("classes\\d*\\.dex")) || entry.startsWith("assets/")

    /** Unpacks [apk], the release [tag]'s, into the module folder, replacing what was there. */
    fun installModule(apk: File, paths: GamePaths, tag: String, cancel: CancelToken) {
        val dir = moduleDir(paths)
        val next = File(dir.parentFile, "d2r.new")
        next.deleteTree()
        apk.inputStream().use { ZipExtractor.extract(it, next, cancel, filter = ::wanted) }
        File(next, "module.json").writeText(JSONObject().put("tag", tag).put("apk", APK).toString())
        dir.deleteTree()
        if (!next.renameTo(dir)) throw java.io.IOException("The module couldn't be put in place.")
    }
}
