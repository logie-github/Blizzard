package com.logie.blizz.wow

import java.io.File
import java.io.RandomAccessFile
import java.nio.file.Files

/**
 * The WoW app's realm programs have their app's folder compiled in as text (`/data/data/com.logie.warcraft/files/turtle/server/modules`,
 * the folder Tortoise's world server reads each module's database updates from; LegionCore's install prefix is the same
 * kind of string). In Blizzard that path is another app's folder, which Android keeps closed, and the world server ended
 * on it ("filesystem error: symlink_status: Permission denied", code 134).
 *
 * The program's bytes are changed in place, to a path of exactly the same length that is Blizzard's own:
 * `com.logie.warcraft/` becomes `com.logie.blizz////` (a path ignores the extra slashes), and the app's `files/<realm>`
 * (`files/turtle`, `files/felsong`) is a link to where the imported realm is, so the compiled-in path leads to it.
 * Idempotent: a second pass finds nothing. Only the programs in `server/bin` are changed, never the databases or the client.
 */
object CompiledPaths {
    private val OLD = "com.logie.warcraft/".toByteArray()
    private val NEW = "com.logie.blizz////".toByteArray()

    init { require(OLD.size == NEW.size) }

    /** Replaces the old folder's name in [file]; how many times. */
    fun patchFile(file: File): Int {
        if (!file.isFile || Files.isSymbolicLink(file.toPath()) || file.length() < OLD.size) return 0
        var count = 0
        RandomAccessFile(file, "rw").use { raf ->
            val chunk = 1 shl 20
            val buffer = ByteArray(chunk)
            var position = 0L
            val length = raf.length()
            while (position < length) {
                raf.seek(position)
                val read = raf.read(buffer, 0, chunk)
                if (read <= 0) break
                var changed = false
                var i = 0
                while (i <= read - OLD.size) {
                    if (buffer[i] == OLD[0] && matches(buffer, i)) {
                        raf.seek(position + i)
                        raf.write(NEW)
                        count++
                        changed = true
                        i += OLD.size
                    } else i++
                }
                if (read < chunk) break
                // The next chunk starts a little back, so a match across the boundary is found.
                position += read - (OLD.size - 1)
                if (changed) raf.seek(position)
            }
        }
        return count
    }

    private fun matches(buffer: ByteArray, at: Int): Boolean {
        for (k in OLD.indices) if (buffer[at + k] != OLD[k]) return false
        return true
    }

    /** Every program of the server's `bin`; how many replacements in all. */
    fun patchServer(layout: WowLayout): Int =
        File(layout.server, "bin").listFiles()?.sumOf { runCatching { patchFile(it) }.getOrDefault(0) } ?: 0

    /** `<app files>/<realm folder>` as a link to the imported realm's folder, so the compiled-in path (`/data/data/com.logie.blizz////files/turtle/...`) leads there. */
    fun link(appFiles: File, layout: WowLayout) {
        val link = File(appFiles, layout.root.name).toPath()
        val target = layout.root.toPath()
        if (Files.isSymbolicLink(link)) {
            if (Files.readSymbolicLink(link) == target) return
            Files.delete(link)
        } else if (Files.exists(link)) return
        Files.createSymbolicLink(link, target)
    }

    /** The app's files folder an imported realm's folder is in (`files/games/<game>/files/<realm>`). */
    fun appFiles(layout: WowLayout): File = layout.root.parentFile!!.parentFile!!.parentFile!!.parentFile!!

    fun fix(layout: WowLayout): Int {
        link(appFiles(layout), layout)
        return patchServer(layout)
    }
}
