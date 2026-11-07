package com.logie.blizz.importer

import java.io.File

/**
 * After an import that finished and checked out, the files the person picked for it (the zip, the 7z, the disc image, the
 * installer, the Switch package) are deleted: the game is in the app now, and the copy they chose to import from was
 * taking the same room again. Only what was picked, and only files:
 * - **a folder is never deleted** (it can be Downloads, or hold other things; "Delete the export" in the wizard is the
 *   person's own, explicit way for World of Warcraft's);
 * - **the player's console keys** ([KEEP]) are theirs to keep for other titles;
 * - what is inside the app's own folder is never touched.
 * A file the app has no right to delete (a document picked without write access) stays; it is said which.
 * Plain Kotlin on [SourceNode], unit-tested.
 */
object SourceCleanup {
    /** Inputs that are never deleted. */
    val KEEP = setOf("keys")

    data class Outcome(val deleted: List<String>, val kept: List<String>) {
        val summary: String?
            get() = when {
                deleted.isEmpty() && kept.isEmpty() -> null
                kept.isEmpty() -> "Deleted what you picked: ${deleted.joinToString()}."
                deleted.isEmpty() -> "Kept what you picked: ${kept.joinToString()}."
                else -> "Deleted ${deleted.joinToString()}. Kept ${kept.joinToString()}."
            }
    }

    fun run(supplied: Map<String, Supplied>, appFiles: File): Outcome {
        val deleted = ArrayList<String>()
        val kept = ArrayList<String>()
        val seen = HashSet<String>()
        for ((id, input) in supplied) {
            val source = (input as? Supplied.Picked)?.source ?: continue
            if (id in KEEP) continue
            if (!seen.add(source.display)) continue
            // A folder stays, whatever it holds.
            if (source.isDirectory) { kept += "${source.name} (a folder)"; continue }
            // Never the app's own files (the installed game is in there).
            val local = source.localFile()
            if (local != null && runCatching { local.canonicalPath.startsWith(appFiles.canonicalPath + File.separator) }.getOrDefault(false)) continue
            if (runCatching { source.delete() }.getOrDefault(false)) deleted += source.name else kept += source.name
        }
        return Outcome(deleted, kept)
    }
}
