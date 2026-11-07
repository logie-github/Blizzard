package com.logie.blizz.importer

import java.io.File

/**
 * What an import leaves in the app's storage once the game is installed and checked, which is only taking room: the pieces of the
 * import itself (`staging/<id>`, its `-scratch`, `-work`, `-keys` and `-installer` folders: an unpacked archive, a copy of the
 * installer and what it made), the aside copy of the old installation (`games/.<id>.old`), the downloads that were kept for a
 * second try (Diablo II: Resurrected's, the legacy downloader's pieces), and the Windows temporary folders an installer filled.
 * Never the game itself, its saves, its state or its library entry. Plain Kotlin, unit-tested.
 */
object Leftovers {
    /** Downloads of one game kept in `downloads/` by their name's start. */
    private val DOWNLOAD_PREFIX = mapOf("diablo2_resurrected" to "d2r-")

    private fun sizeOf(file: File): Long = file.filesNoLinks().sumOf { it.length() }

    /** What belongs to [gameId] and is no longer needed once it is installed. */
    fun of(paths: GamePaths, gameId: String, withDownloads: Boolean = true): List<File> = buildList {
        paths.staging.listFiles { f -> f.name == gameId || f.name.startsWith("$gameId-") }?.let { addAll(it) }
        add(File(paths.games, ".$gameId.old"))
        if (withDownloads) {
            DOWNLOAD_PREFIX[gameId]?.let { prefix -> paths.downloads.listFiles { f -> f.name.startsWith(prefix) }?.let { addAll(it) } }
        }
    }.filter { it.exists() }

    /** The legacy downloader's cached pieces: the same for every game that uses it, so only with nothing downloading. */
    fun shared(paths: GamePaths): List<File> = listOf(paths.legacyCache).filter { it.exists() }

    fun size(files: List<File>): Long = files.sumOf { sizeOf(it) }

    /**
     * Deletes the leftovers of [gameId] (and the shared downloads when [othersImporting] is false); the bytes freed.
     * Never while the game's own import is running: the caller says when it has finished.
     */
    fun clean(paths: GamePaths, gameId: String, othersImporting: Boolean, extra: List<File> = emptyList()): Long {
        val files = of(paths, gameId) + extra.filter { it.exists() } + (if (othersImporting) emptyList() else shared(paths))
        val bytes = size(files)
        files.forEach { it.deleteTree() }
        return bytes
    }

    /** The folders of the games' Windows an installer fills with what it unpacks (its temporary folders): [prefixDriveC] is the container's `drive_c`. */
    fun windowsTemp(prefixDriveC: File): List<File> =
        listOf(File(prefixDriveC, "users/xuser/Temp"), File(prefixDriveC, "windows/temp")).filter { it.isDirectory }
            .flatMap { it.listFiles().orEmpty().toList() }
}
