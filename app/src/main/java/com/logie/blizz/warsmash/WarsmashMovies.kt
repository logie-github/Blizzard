package com.logie.blizz.warsmash

import java.io.File

/**
 * Warcraft III's movies on the phone's side (plain Kotlin, unit-tested): which file plays a movie the engine names, and
 * the captions the game shows over one (UI\Captions\<name>.txt, which the engine reads from the game's data).
 */
object WarsmashMovies {
    /** The game's movie folders: its own, then where the Windows game's switch set them aside (Wc3Movies). */
    private val FOLDERS = listOf("Movies", "Movies (off)")

    /** The file of the movie [name] ("HumanEd": Movies\HumanEd.mpq) in [gameDir], in any case; null where it has none. */
    fun find(gameDir: File, name: String): File? {
        val dirs = gameDir.listFiles().orEmpty().filter { it.isDirectory }
        for (folder in FOLDERS) {
            val dir = dirs.firstOrNull { it.name.equals(folder, ignoreCase = true) } ?: continue
            dir.listFiles().orEmpty().firstOrNull { it.isFile && it.name.equals("$name.mpq", ignoreCase = true) }?.let { return it }
        }
        return null
    }

    /** One caption: shown from [start] to [end], seconds from the movie's start. */
    data class Cue(val start: Double, val end: Double, val text: String)

    /**
     * The game's caption file: a line a caption, "HH:MM:SS:FF<tab>HH:MM:SS:FF<tab>text", FF in frames of 24 a second,
     * "<p>" a line break. Lines that don't read so are passed over.
     */
    fun cues(text: String): List<Cue> = text.lineSequence().mapNotNull { line ->
        val parts = line.trimEnd('\r').split('\t')
        if (parts.size < 3) return@mapNotNull null
        val start = time(parts[0]) ?: return@mapNotNull null
        val end = time(parts[1]) ?: return@mapNotNull null
        val words = parts.drop(2).joinToString("\t").split("<p>").joinToString("\n") { it.trim() }.trim()
        if (words.isEmpty() || end <= start) null else Cue(start, end, words)
    }.toList()

    private fun time(stamp: String): Double? {
        val p = stamp.trim().split(':').map { it.toIntOrNull() ?: return null }
        if (p.size != 4) return null
        return p[0] * 3600.0 + p[1] * 60.0 + p[2] + p[3] / 24.0
    }

    /** The caption showing [seconds] into the movie, or null. */
    fun at(cues: List<Cue>, seconds: Double): Cue? = cues.firstOrNull { seconds >= it.start && seconds < it.end }
}
