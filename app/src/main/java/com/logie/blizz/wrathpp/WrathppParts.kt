package com.logie.blizz.wrathpp

import java.io.File

/**
 * When Wrath++'s downloaded pieces (its server, looks, creator art and add-on) are fetched again. They live on the phone
 * and Play uses them as they are (the user, 18 November 2026: "it downloads then unpacks the server every time I launch ...
 * Can't we just keep the looks etc on the phone"): CI rebuilds and republishes each of them several times a day, and Play
 * used to fetch whatever was newer, 250 MB of server and 20,500 files of looks, at every start.
 *
 * They are refreshed ([due]) at the first Play after the app itself was updated, because the creator the app writes is made
 * for the looks, art and add-on of its own build, and when the settings page's **Update** asks ([WrathppServerUpdate]).
 * A piece that isn't there yet is always fetched. [markDone] is written only after a refresh that reached the release.
 */
object WrathppParts {
    private const val FILE = "wrathpp-parts-build.txt"

    private fun file(filesDir: File) = File(filesDir, FILE)

    /** The app build the pieces were last refreshed for, or null. */
    fun refreshedFor(filesDir: File): Int? = runCatching { file(filesDir).readText().trim().toInt() }.getOrNull()

    /** Whether the pieces are refreshed at this Play: the app is another build than the one they were refreshed for. */
    fun due(filesDir: File, build: Int): Boolean = refreshedFor(filesDir) != build

    fun markDone(filesDir: File, build: Int) {
        file(filesDir).apply { parentFile?.mkdirs() }.writeText("$build\n")
    }
}
