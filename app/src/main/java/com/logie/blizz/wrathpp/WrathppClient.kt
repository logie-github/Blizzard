package com.logie.blizz.wrathpp

import java.io.File
import java.io.IOException
import java.nio.file.Files

/**
 * Wrath++'s private copy of the 3.3.5a game (`files/client-wrathpp`), made from Wrath+'s (`files/client`) the first time
 * Wrath++ is played. Wrath++'s realm and its modules write their patches into it (ctl.sh points WOW_CLIENT_DIR there),
 * and its settings, cache and add-ons are its own, so nothing Wrath++ does reaches Wrath+'s game.
 *
 * The game's own archives (`Data/` and `Data/<locale>/` `*.MPQ` files, gigabytes the game and the realm only ever read)
 * are hard links to Wrath+'s rather than copies, where the storage allows (else copied), the HD look's own patches among
 * them (`patch-A/F/W...`). Never a patch a realm module writes (`patch-M/U/V/Y/Z.MPQ`, and their markers): those are left
 * out, and Wrath++'s own realm makes its own. (Until 2026-11-11 `patch-4/F/W` were left out too, the Alternative HD Patch's
 * `patch-F` and `patch-W` with them: a copy made then gets them at the next Play, [addMissing].)
 * The same rule is `ctl.sh`'s `wrathpp_shareable`, which `ctl.sh wrathpp-check` holds the copy to.
 *
 * Plain files only, so it is unit-tested on a temporary folder. NOT run on a phone.
 */
object WrathppClient {
    /** Written last: the copy is complete. */
    const val MARKER = ".wrathpp-client"

    private val MODULE_PATCH = Regex("""patch-[muvyz]\.mpq(\..*)?""", RegexOption.IGNORE_CASE)

    /** Left out of the copy: the game's caches and logs (it makes them again), and the realm modules' patches. */
    fun skipped(relative: String): Boolean {
        val parts = relative.split('/')
        val top = parts.first().lowercase()
        if (top == "cache" || top == "logs" || top == "errors" || top == "screenshots") return true
        // (a module's patch may be a folder the game reads as an archive: everything in it goes too)
        if (top == "data" && parts.drop(1).any { MODULE_PATCH.matches(it) }) return true
        return false
    }

    /** May be a hard link to Wrath+'s file: a game archive in `Data/` or `Data/<locale>/` that no realm module writes. */
    fun shareable(relative: String): Boolean {
        val parts = relative.split('/')
        if (parts.first().lowercase() != "data" || parts.size !in 2..3) return false
        val name = parts.last()
        return name.lowercase().endsWith(".mpq") && !MODULE_PATCH.matches(name)
    }

    fun isMade(target: File): Boolean = File(target, MARKER).isFile

    /**
     * A game archive of [source]'s that a copy made before lacks (the HD look's `patch-F`/`patch-W`, left out until
     * 2026-11-11, or one added to the game since): put in, linked where the storage allows. Nothing else is touched. Returns how many.
     */
    fun addMissing(source: File, target: File): Int {
        var added = 0
        source.walkTopDown().forEach { f ->
            val rel = f.relativeTo(source).invariantSeparatorsPath
            if (!f.isFile || !shareable(rel) || Files.isSymbolicLink(f.toPath())) return@forEach
            val out = File(target, rel)
            if (out.exists()) return@forEach
            out.parentFile?.mkdirs()
            val part = File(out.path + ".part")
            part.delete()
            if (runCatching { Files.createLink(part.toPath(), f.toPath()) }.isFailure) f.copyTo(part, overwrite = true)
            if (!part.renameTo(out)) { part.delete(); throw IOException("${out.path} couldn't be put in place") }
            added++
        }
        return added
    }

    /** What [make] would copy (bytes not shared), for the space check. */
    fun bytesToCopy(source: File): Long =
        source.walkTopDown().filter { it.isFile }.sumOf { f ->
            val rel = f.relativeTo(source).invariantSeparatorsPath
            if (skipped(rel) || shareable(rel)) 0L else f.length()
        }

    /**
     * Makes [target] from [source] if it isn't complete yet. [onProgress] gets a line now and then. Throws [IOException]
     * when [target] would be inside [source] or the other way round, or when there is no room.
     */
    fun make(source: File, target: File, onProgress: (String, Float?) -> Unit = { _, _ -> }): Boolean {
        if (isMade(target)) {
            addMissing(source, target)
            return false
        }
        val src = source.canonicalFile
        val dst = target.canonicalFile
        if (dst.path == src.path || dst.path.startsWith(src.path + File.separator) || src.path.startsWith(dst.path + File.separator)) {
            throw IOException("Wrath++'s game copy can't be inside the game it copies")
        }
        if (Files.isSymbolicLink(target.toPath())) throw IOException("${target.path} is a link")
        val need = bytesToCopy(src)
        val free = (dst.parentFile ?: dst).usableSpace
        if (free in 1 until need + (512L shl 20)) {
            throw IOException("Not enough space for Wrath++'s copy of the game: it needs about ${need shr 20} MB, ${free shr 20} MB is free.")
        }
        val staging = File(dst.parentFile, dst.name + ".new")
        staging.deleteRecursively()
        staging.mkdirs()
        var done = 0L
        var linked = 0
        src.walkTopDown().forEach { f ->
            val rel = f.relativeTo(src).invariantSeparatorsPath
            if (rel.isEmpty() || skipped(rel)) return@forEach
            if (Files.isSymbolicLink(f.toPath())) return@forEach
            val out = File(staging, rel)
            when {
                f.isDirectory -> out.mkdirs()
                f.isFile -> {
                    out.parentFile?.mkdirs()
                    val link = shareable(rel) && runCatching { Files.createLink(out.toPath(), f.toPath()) }.isSuccess
                    if (link) linked++ else {
                        f.copyTo(out, overwrite = true)
                        done += f.length()
                        onProgress("Making Wrath++'s copy of the game (step 4 of 4): ${done shr 20} / ${need shr 20} MB",
                            if (need > 0) done.toFloat() / need else null)
                    }
                }
            }
        }
        File(staging, MARKER).writeText("from ${src.path}\nshared archives: $linked\n")
        dst.deleteRecursively()
        if (!staging.renameTo(dst)) throw IOException("Wrath++'s game copy couldn't be put in place")
        return true
    }
}
