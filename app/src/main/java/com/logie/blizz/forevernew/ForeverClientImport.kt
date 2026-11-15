package com.logie.blizz.forevernew

import java.io.File
import java.io.IOException
import java.io.InputStream

/**
 * "Import & Install": the one folder pick. The user's own complete World of Warcraft folder (the one holding `.build.info`,
 * `Data` and `_forever_`) is copied into the app's own storage (`files/realms/forever-v2/client`), because the game's Wine and
 * the map tools can only read app-owned files, not Android's picker. Only the three things the realm uses are copied
 * (other products in the same folder aren't), a file already copied with the same size is skipped (an interrupted copy resumes),
 * a partial file is written under `.part`, and nothing is ever written back to the picked folder or deleted from it.
 * The copy is of the player's own installation; nothing here downloads a client.
 */
object ForeverClientImport {
    data class Entry(val id: String, val name: String, val directory: Boolean, val size: Long)

    /** What a picked folder is: the abstraction over Android's tree so the walk is testable. */
    interface Tree {
        val rootId: String
        fun list(id: String): List<Entry>
        fun open(id: String): InputStream
    }

    /** Top-level names that are copied. */
    private val KEEP = listOf(".build.info", "Data", "_forever_")

    fun kept(name: String) = KEEP.any { it.equals(name, ignoreCase = true) }

    /** An error text if [tree]'s root isn't the installation root, else null. */
    fun checkRoot(tree: Tree): String? {
        val top = tree.list(tree.rootId).map { it.name.lowercase() }
        if (".build.info" in top && "_forever_" in top && "data" in top) return null
        if ("wow.exe" in top && "wtf" in top) return "That is the _forever_ folder itself. Pick the World of Warcraft folder that contains it (with .build.info and Data)."
        return "That folder isn't a complete WoW Forever installation: it needs .build.info, Data and _forever_ together. Pick the World of Warcraft folder."
    }

    /** All files that would be copied: (destination relative path, entry id, size). */
    fun plan(tree: Tree): List<Triple<String, String, Long>> {
        val out = ArrayList<Triple<String, String, Long>>()
        fun walk(id: String, prefix: String) {
            for (e in tree.list(id)) {
                val rel = if (prefix.isEmpty()) e.name else "$prefix/${e.name}"
                if (e.directory) walk(e.id, rel) else out += Triple(rel, e.id, e.size)
            }
        }
        for (top in tree.list(tree.rootId)) {
            if (!kept(top.name)) continue
            if (top.directory) walk(top.id, top.name) else out += Triple(top.name, top.id, top.size)
        }
        return out
    }

    /**
     * Copies the plan into [dest]. [progress] gets (bytes done, bytes total, the file). Returns an error text or null.
     * [freeBytes] is checked against what is still to copy (plus a margin) before anything is written.
     */
    fun copy(tree: Tree, dest: File, freeBytes: (File) -> Long = { it.usableSpace }, cancelled: () -> Boolean = { false },
        progress: (Long, Long, String) -> Unit = { _, _, _ -> }): String? {
        checkRoot(tree)?.let { return it }
        val files = plan(tree)
        val total = files.sumOf { it.third }
        dest.mkdirs()
        var done = 0L
        val todo = files.filter { (rel, _, size) -> val t = File(dest, rel); !(t.isFile && t.length() == size) }
        val need = todo.sumOf { it.third } + (512L shl 20)
        val free = freeBytes(dest)
        if (free in 1 until need) return "Not enough space to copy the game: ${need shr 30} GB are needed, ${free shr 30} GB are free."
        for ((rel, id, size) in files) {
            if (cancelled()) return "The copy was stopped; it continues where it left off."
            val target = ForeverPackage.entryTarget(dest, rel) ?: return "The folder has an unsafe path: $rel"
            if (target.isFile && target.length() == size) { done += size; progress(done, total, rel); continue }
            target.parentFile?.mkdirs()
            val part = File(target.path + ".part")
            try {
                tree.open(id).use { input ->
                    part.outputStream().buffered(1 shl 16).use { out ->
                        val buffer = ByteArray(1 shl 16)
                        var last = 0L
                        var fileDone = 0L
                        while (true) {
                            val n = input.read(buffer)
                            if (n < 0) break
                            out.write(buffer, 0, n); fileDone += n
                            if (fileDone - last >= (4L shl 20)) { last = fileDone; progress(done + fileDone, total, rel) }
                        }
                    }
                }
            } catch (e: IOException) { return "Copying $rel failed: ${e.message}" }
            if (size > 0 && part.length() != size) { part.delete(); return "$rel was copied incompletely (${part.length()} of $size bytes)." }
            target.delete()
            if (!part.renameTo(target)) return "$rel couldn't be saved."
            done += size; progress(done, total, rel)
        }
        return null
    }

    /** The pointer file the installer reads (`client-path.txt`): where the copied installation is. */
    fun remember(layout: ForeverLayout) { File(layout.root, "client-path.txt").apply { parentFile?.mkdirs() }.writeText(layout.client.path) }
}
