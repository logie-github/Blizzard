package com.logie.blizz.importer

import java.io.File
import java.io.RandomAccessFile
import java.security.MessageDigest

/**
 * A description of what an import had to work with and what it made, for the report sent when an
 * install fails: every file's path, size and a hash (SHA-256 of its size and its first and last 64 KB,
 * so a big game costs seconds, not minutes), never its content. It shows which files are there, which
 * are missing, and whether the ones that are look like the ones the importer expects, without the
 * person having to send anything. Plain Kotlin, unit-tested.
 */
object InstallManifest {
    private const val CHUNK = 64 * 1024

    /** Size and head/tail hash of [file]: "123456 3f9a...". */
    fun fingerprint(file: File): String = runCatching {
        val size = file.length()
        val md = MessageDigest.getInstance("SHA-256")
        md.update(size.toString().toByteArray())
        RandomAccessFile(file, "r").use { f ->
            val buffer = ByteArray(CHUNK)
            val head = f.read(buffer)
            if (head > 0) md.update(buffer, 0, head)
            if (size > 2L * CHUNK) {
                f.seek(size - CHUNK)
                val tail = f.read(buffer)
                if (tail > 0) md.update(buffer, 0, tail)
            }
        }
        "$size ${md.digest().take(8).joinToString("") { "%02x".format(it) }}"
    }.getOrDefault("unreadable")

    /** One line per file under [root], at most [limit]; past that a count per top folder. */
    fun describe(root: File, label: String, limit: Int = 1200): String {
        if (!root.exists()) return "$label: not there\n"
        val files = root.filesNoLinks().toList()
        val total = files.sumOf { it.length() }
        return buildString {
            append("$label: ${files.size} files, ${FileValidator.gb(total)}\n")
            if (files.size <= limit) {
                files.sortedBy { it.path }.forEach { append("  ${it.relativeTo(root).path}  ${fingerprint(it)}\n") }
            } else {
                // Too many to list: the biggest and the top folders.
                files.sortedByDescending { it.length() }.take(limit / 2).forEach { append("  ${it.relativeTo(root).path}  ${fingerprint(it)}\n") }
                append("  (the ${limit / 2} largest of ${files.size}; per top folder:)\n")
                files.groupBy { it.relativeTo(root).path.substringBefore('/') }.toSortedMap()
                    .forEach { (dir, list) -> append("  $dir/  ${list.size} files, ${FileValidator.gb(list.sumOf { it.length() })}\n") }
            }
        }
    }

    /** What the person picked: names and sizes only (it can be in a place the app reads a file at a time). */
    fun describe(node: SourceNode, label: String, limit: Int = 400): String = runCatching {
        val all = if (node.isDirectory) node.walk(8).filter { !it.isDirectory }.toList() else listOf(node)
        buildString {
            append("$label: ${node.name}${if (node.isDirectory) "/" else ""}, ${all.size} files, ${FileValidator.gb(all.sumOf { it.size })}\n")
            all.take(limit).forEach { append("  ${it.name}  ${it.size}\n") }
            if (all.size > limit) append("  ... ${all.size - limit} more\n")
        }
    }.getOrElse { "$label: ${node.name} (couldn't be listed: ${it.message})\n" }
}
