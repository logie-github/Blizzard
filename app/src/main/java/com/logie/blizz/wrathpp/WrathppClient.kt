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
 * are hard links to Wrath+'s rather than copies, where the storage allows (else copied). Never a patch a realm module
 * writes (`patch-4/F/M/U/V/W/Y/Z.MPQ`, and their markers): those are left out, and Wrath++'s own realm makes its own.
 * The same rule is `ctl.sh`'s `wrathpp_shareable`, which `ctl.sh wrathpp-check` holds the copy to.
 *
 * Plain files only, so it is unit-tested on a temporary folder. NOT run on a phone.
 */
object WrathppClient {
    /** Written last: the copy is complete. */
    const val MARKER = ".wrathpp-client"

    private val MODULE_PATCH = Regex("""patch-[4fmuvwyz]\.mpq(\..*)?""", RegexOption.IGNORE_CASE)

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
    fun make(source: File, target: File, onProgress: (String) -> Unit = {}): Boolean {
        if (isMade(target)) return false
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
                        onProgress("Copying the game for Wrath++… ${done shr 20} / ${need shr 20} MB")
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
