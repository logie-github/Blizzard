package com.logie.blizz.importer

import java.io.File

/**
 * Where the imported games live in the app's own storage:
 *
 * - `games/<id>/`: the installed game, replaced only whole and only once a new one validated;
 * - `staging/<id>/`: an import being assembled, thrown away if it fails or is cancelled;
 * - `saves/<id>/`: saved games, profiles and settings, never touched by an import or a repair;
 * - `downloads/`: downloads kept between attempts (resumed, not started again);
 * - `state/`: the import state and the library entries.
 */
class GamePaths(val root: File) {
    val games = File(root, "games")
    val staging = File(root, "staging")
    val saves = File(root, "saves")
    val downloads = File(root, "downloads")
    val state = File(root, "state")

    fun game(id: String) = File(games, id)
    fun staging(id: String) = File(staging, id)
    /** A game's installer, copied here and run in the games' Windows (drive T: is [staging]); it installs into `out/`. */
    fun installer(id: String) = File(staging, "$id-installer")
    fun saves(id: String) = File(saves, id)
    /** blizzard-legacy-dl's cache of payload pieces: a stopped download resumes from it. */
    val legacyCache = File(downloads, "legacy")
}
