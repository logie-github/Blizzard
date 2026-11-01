package com.logie.blizz.importer

import org.json.JSONArray
import org.json.JSONObject
import java.io.File

/**
 * An imported game in the library: what [com.logie.blizz.game.WindowsRuntime] starts. The shelf's
 * catalog ([com.logie.blizz.Games]) is the game's identity (title, art); this is its installation.
 */
data class LibraryEntry(
    val gameId: String,
    val title: String,
    /** The game and its expansions (e.g. D2DV, D2XP). */
    val products: List<String>,
    val clientVersion: String,
    val installPath: String,
    /** Relative to [installPath]. */
    val executable: String,
    /** "winlator": Wine and Box64 through the app's Winlator. */
    val runtime: String,
    val arguments: String,
    val stage: Stage,
    /** Where saved games are, for the person (a folder of the app's, or inside the games' Windows). */
    val saveLocation: String?,
    /** The touch control profile ([com.logie.blizz.game.LaunchProfile.id]). */
    val controlProfile: String,
) {
    fun toJson(): JSONObject = JSONObject()
        .put("gameId", gameId).put("title", title).put("products", JSONArray(products))
        .put("clientVersion", clientVersion).put("installPath", installPath).put("executable", executable)
        .put("runtime", runtime).put("arguments", arguments).put("stage", stage.name)
        .put("saveLocation", saveLocation).put("controlProfile", controlProfile)

    companion object {
        const val RUNTIME_WINLATOR = "winlator"

        fun fromJson(o: JSONObject) = LibraryEntry(
            gameId = o.getString("gameId"),
            title = o.getString("title"),
            products = o.optJSONArray("products")?.let { a -> (0 until a.length()).map { a.getString(it) } } ?: emptyList(),
            clientVersion = o.optString("clientVersion"),
            installPath = o.getString("installPath"),
            executable = o.getString("executable"),
            runtime = o.optString("runtime", RUNTIME_WINLATOR),
            arguments = o.optString("arguments"),
            stage = Stage.entries.firstOrNull { it.name == o.optString("stage") } ?: Stage.IMPORTED_UNTESTED,
            saveLocation = o.optString("saveLocation").takeIf { it.isNotEmpty() && it != "null" },
            controlProfile = o.optString("controlProfile"),
        )
    }
}

/** The library's imported games, one JSON file each under `state/`. */
class Library(private val paths: GamePaths) {
    private fun file(gameId: String) = File(paths.state, "library-$gameId.json")

    @Synchronized
    fun get(gameId: String): LibraryEntry? = runCatching { LibraryEntry.fromJson(JSONObject(file(gameId).readText())) }.getOrNull()

    @Synchronized
    fun put(entry: LibraryEntry) = file(entry.gameId).writeAtomically(entry.toJson().toString(2))

    @Synchronized
    fun remove(gameId: String) {
        file(gameId).delete()
    }
}
