package com.logie.blizz.wow

import java.io.File
import java.io.IOException
import java.nio.file.Files

/**
 * The imported files name the WoW app's folder (`/data/data/com.logie.warcraft/files`, or the same
 * folder as `/data/user/0/...`): its configs (`LogsDir`, `DataDir`, `SourceDirectory`, ...),
 * `ctl.sh`'s default and symlinks into the server's data (`data-modules`). This puts Blizzard's
 * folder in their place, in text files and symlinks only. Idempotent: a second pass finds nothing.
 *
 * What is NOT touched, and why:
 * - Binary files (a NUL byte in the first 8 KiB): the server's programs, libraries and the
 *   databases. The programs have the old folder baked in as their ELF interpreter and rpath;
 *   [WowCtl] runs them through musl's loader so that doesn't matter.
 * - MariaDB's data folder (`mysql/`), the server's SQL (`server/src`), its libraries, the client and
 *   the server's data folders: not even opened. InnoDB keeps tablespace paths relative to the data
 *   folder, and the server is started with `--datadir` explicitly, with stale pid and socket files
 *   removed. NOT verified against a real database (it needs the user's data).
 */
object WowPathRewrite {
    /** The old app's folder, both ways Android names it. */
    val DEFAULT_OLD = listOf("/data/data/com.logie.warcraft/files", "/data/user/0/com.logie.warcraft/files")

    private const val MAX_TEXT = 2L * 1024 * 1024

    data class Result(val filesRewritten: List<String>, val linksRewritten: List<String>) {
        val changed: Boolean get() = filesRewritten.isNotEmpty() || linksRewritten.isNotEmpty()
    }

    /**
     * Rewrites every text file and symlink in `server` (its own files, `etc` and `lua_scripts`) and
     * in `etc`, `etc-remix`, `data-modules`, `data-races` and `races` that names one of
     * [oldPrefixes], to [newPrefix]. Records [newPrefix] in [WowLayout.rewriteMarker].
     */
    fun rewrite(layout: WowLayout, oldPrefixes: Collection<String>, newPrefix: String): Result {
        val new = newPrefix.trimEnd('/')
        // The longest first, so a prefix that begins another is replaced whole.
        val olds = oldPrefixes.map { it.trimEnd('/') }.filter { it.isNotEmpty() && it != new }.distinct().sortedByDescending { it.length }
        val files = ArrayList<String>()
        val links = ArrayList<String>()
        if (olds.isNotEmpty()) {
            val root = layout.root
            walk(layout.server, root, olds, new, files, links) { it.name == "etc" || it.name == "lua_scripts" }
            for (name in listOf("etc", "etc-remix", "data-modules", "data-races", "races")) {
                walk(File(root, name), root, olds, new, files, links) { true }
            }
        }
        layout.rewriteMarker.parentFile?.mkdirs()
        layout.rewriteMarker.writeText("$new\n")
        return Result(files, links)
    }

    /** Looks at [dir]'s files and symlinks, and enters the folders [enter] says. */
    private fun walk(
        dir: File, root: File, olds: List<String>, new: String,
        files: MutableList<String>, links: MutableList<String>, enter: (File) -> Boolean,
    ) {
        val children = dir.listFiles() ?: return
        for (child in children.sortedBy { it.name }) {
            val path = child.toPath()
            val relative = child.relativeTo(root).path
            if (Files.isSymbolicLink(path)) {
                val target = Files.readSymbolicLink(path).toString()
                val fixed = replace(target, olds, new)
                if (fixed != target) {
                    Files.delete(path)
                    Files.createSymbolicLink(path, File(fixed).toPath())
                    links += relative
                }
                continue
            }
            if (child.isDirectory) {
                if (enter(child)) walk(child, root, olds, new, files, links) { true }
                continue
            }
            if (!child.isFile || child.length() == 0L || child.length() > MAX_TEXT || isBinary(child)) continue
            val text = child.readText(Charsets.UTF_8)
            val fixed = replace(text, olds, new)
            if (fixed == text) continue
            val executable = child.canExecute()
            val temp = File(child.parentFile, ".${child.name}.blizz-tmp")
            temp.writeText(fixed, Charsets.UTF_8)
            if (executable) temp.setExecutable(true, false)
            if (!temp.renameTo(child)) {
                temp.delete()
                throw IOException("Couldn't rewrite ${child.path}")
            }
            files += relative
        }
    }

    internal fun replace(text: String, olds: List<String>, new: String): String {
        var out = text
        for (old in olds) if (old in out) out = out.replace(old, new)
        return out
    }

    private fun isBinary(file: File): Boolean = file.inputStream().use { input ->
        val buffer = ByteArray(8192)
        val n = input.read(buffer)
        (0 until maxOf(n, 0)).any { buffer[it] == 0.toByte() }
    }

    /** The prefix the files were last rewritten to, if they were. */
    fun recordedPrefix(layout: WowLayout): String? =
        runCatching { layout.rewriteMarker.readText().trim() }.getOrNull()?.takeIf { it.isNotEmpty() }

    /**
     * The old app's folder as the export recorded it (`sourceFilesDir`), with the standard names
     * ([DEFAULT_OLD]) and the same folder under its other spelling.
     */
    fun oldPrefixes(sourceFilesDir: String?): List<String> {
        val extra = sourceFilesDir?.trim()?.trimEnd('/')?.takeIf { it.isNotEmpty() }?.let { source ->
            listOf(source, source.replace("/data/user/0/", "/data/data/"), source.replace("/data/data/", "/data/user/0/"))
        }.orEmpty()
        return (extra + DEFAULT_OLD).distinct()
    }
}
