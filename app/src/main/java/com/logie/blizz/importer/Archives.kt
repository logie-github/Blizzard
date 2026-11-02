package com.logie.blizz.importer

import java.io.File
import java.io.InputStream
import java.io.RandomAccessFile
import java.util.zip.ZipEntry
import java.util.zip.ZipException
import java.util.zip.ZipInputStream

/** Paths from archives: only plain relative paths inside the destination ("zip slip" refused). Plain Kotlin, unit-tested. */
object SafePaths {
    fun resolve(root: File, entryName: String): File {
        val clean = entryName.replace('\\', '/').trimStart('/')
        if (clean.isEmpty() || clean.split('/').any { it == ".." } || clean.contains(':') || clean.contains('\u0000')) {
            throw ImportException(Problem.CORRUPT_ARCHIVE, "The archive has an unsafe path ($entryName); nothing was extracted from it.")
        }
        val target = File(root, clean)
        val rootPath = root.canonicalPath + File.separator
        if (!target.canonicalPath.startsWith(rootPath)) {
            throw ImportException(Problem.CORRUPT_ARCHIVE, "The archive has an unsafe path ($entryName); nothing was extracted from it.")
        }
        return target
    }
}

/** Copies a stream to a file, in buffered chunks, checking [cancel] between them. */
fun copyStream(input: InputStream, target: File, cancel: CancelToken, onBytes: (Long) -> Unit = {}) {
    target.parentFile?.mkdirs()
    val temp = File(target.parentFile, ".${target.name}.part")
    temp.outputStream().buffered(1 shl 20).use { out ->
        val buffer = ByteArray(1 shl 16)
        while (true) {
            cancel.check()
            val n = input.read(buffer)
            if (n < 0) break
            out.write(buffer, 0, n)
            onBytes(n.toLong())
        }
    }
    target.delete()
    if (!temp.renameTo(target)) throw java.io.IOException("Couldn't write ${target.path}")
}

/** Stops long work when the import is cancelled. */
class CancelToken {
    @Volatile var cancelled = false
        private set

    fun cancel() {
        cancelled = true
    }

    fun check() {
        if (cancelled) throw ImportException(Problem.CANCELLED, "Cancelled.")
    }
}

/** Zip archives, extracted entry by entry as streams. */
object ZipExtractor {
    /** The entries' names, without extracting. */
    fun list(input: InputStream): List<String> = ZipInputStream(input.buffered()).use { zip ->
        val names = ArrayList<String>()
        try {
            while (true) names += (zip.nextEntry ?: break).name
        } catch (e: ZipException) {
            throw ImportException(Problem.CORRUPT_ARCHIVE, "The zip archive is damaged.", e.message, e)
        }
        names
    }

    /** Every entry [filter] accepts, under [dest] (paths checked by [SafePaths]). Returns the files written. */
    fun extract(input: InputStream, dest: File, cancel: CancelToken, filter: (String) -> Boolean = { true }, onBytes: (Long) -> Unit = {}): List<File> {
        val written = ArrayList<File>()
        ZipInputStream(input.buffered(1 shl 16)).use { zip ->
            var entry: ZipEntry?
            var any = false
            try {
                while (true) {
                    entry = zip.nextEntry ?: break
                    any = true
                    cancel.check()
                    val target = SafePaths.resolve(dest, entry.name)
                    if (entry.isDirectory) {
                        target.mkdirs()
                        continue
                    }
                    if (!filter(entry.name)) continue
                    copyStream(zip, target, cancel, onBytes)
                    written += target
                }
            } catch (e: ZipException) {
                throw ImportException(Problem.CORRUPT_ARCHIVE, "The zip archive is damaged.", e.message, e)
            } catch (e: java.io.EOFException) {
                throw ImportException(Problem.CORRUPT_ARCHIVE, "The zip archive is cut short (an incomplete download?).", e.message, e)
            }
            if (!any) throw ImportException(Problem.CORRUPT_ARCHIVE, "That file isn't a zip archive, or it's empty.")
        }
        return written
    }
}

/**
 * Disc images (ISO 9660 with Joliet's long names), read without mounting: every file with its
 * path, and a file streamed out by name (the StarCraft discs' INSTALL.EXE). Plain Kotlin, unit-tested.
 */
class Iso9660(private val file: File) {
    data class Entry(val name: String, val extent: Long, val size: Long, val isDirectory: Boolean)

    private val sector = 2048L

    /** The root folder of the best table the image has (Joliet's, else the primary one). */
    private data class Table(val extent: Long, val size: Long, val joliet: Boolean)

    private fun table(f: RandomAccessFile): Table {
        var primary: Table? = null
        var joliet: Table? = null
        var at = 16L
        while (at < 64) {
            val vd = ByteArray(2048)
            f.seek(at * sector)
            if (f.read(vd) != 2048 || String(vd, 1, 5, Charsets.US_ASCII) != "CD001") break
            val type = vd[0].toInt()
            if (type == 255) break
            val record = vd.copyOfRange(156, 156 + 34)
            val t = Table(le32(record, 2).toLong() and 0xffffffffL, le32(record, 10).toLong() and 0xffffffffL, type == 2)
            if (type == 1) primary = t
            // Joliet: a supplementary descriptor whose escape sequence is %/@, %/C or %/E.
            if (type == 2 && vd[88].toInt() == '%'.code && vd[89].toInt() == '/'.code && vd[90].toInt() in listOf('@'.code, 'C'.code, 'E'.code)) joliet = t
            at++
        }
        return joliet ?: primary ?: throw ImportException(Problem.UNSUPPORTED_INSTALLER, "${file.name} isn't a disc image this app can read (ISO 9660).")
    }

    /** The root folder's entries; throws when [file] isn't an ISO 9660 image. */
    fun root(): List<Entry> = RandomAccessFile(file, "r").use { f ->
        val t = table(f)
        directory(f, t.extent, t.size, t.joliet)
    }

    /** Every file in the image, by path with "/" between folders. */
    fun files(): List<Pair<String, Entry>> = RandomAccessFile(file, "r").use { f ->
        val t = table(f)
        val out = ArrayList<Pair<String, Entry>>()
        fun walk(extent: Long, size: Long, prefix: String, depth: Int) {
            for (e in directory(f, extent, size, t.joliet)) {
                if (e.isDirectory) { if (depth < 24) walk(e.extent, e.size, "$prefix${e.name}/", depth + 1) } else out += (prefix + e.name) to e
            }
        }
        walk(t.extent, t.size, "", 0)
        out
    }

    fun find(name: String): Entry? = root().firstOrNull { it.name.equals(name, ignoreCase = true) }

    fun open(entry: Entry): InputStream {
        val f = RandomAccessFile(file, "r")
        f.seek(entry.extent * sector)
        var left = entry.size
        return object : InputStream() {
            override fun read(): Int {
                if (left <= 0) return -1
                left--
                return f.read()
            }

            override fun read(b: ByteArray, off: Int, len: Int): Int {
                if (left <= 0) return -1
                val n = f.read(b, off, minOf(len.toLong(), left).toInt())
                if (n > 0) left -= n
                return n
            }

            override fun close() = f.close()
        }
    }

    private fun directory(f: RandomAccessFile, extent: Long, size: Long, joliet: Boolean): List<Entry> {
        val data = ByteArray(size.toInt().coerceAtMost(1 shl 22))
        f.seek(extent * sector)
        f.readFully(data)
        val out = ArrayList<Entry>()
        var i = 0
        while (i < data.size) {
            val length = data[i].toInt() and 0xff
            if (length == 0) {
                // Records don't cross sectors: on to the next one.
                i = ((i / sector.toInt()) + 1) * sector.toInt()
                continue
            }
            val nameLength = data[i + 32].toInt() and 0xff
            val flags = data[i + 25].toInt()
            val dot = nameLength == 1 && (data[i + 33].toInt() == 0 || data[i + 33].toInt() == 1)
            if (!dot) {
                val raw = if (joliet) String(data, i + 33, nameLength, Charsets.UTF_16BE) else String(data, i + 33, nameLength, Charsets.ISO_8859_1)
                out += Entry(
                    name = raw.substringBefore(';').trimEnd('.'),
                    extent = le32(data, i + 2).toLong() and 0xffffffffL,
                    size = le32(data, i + 10).toLong() and 0xffffffffL,
                    isDirectory = flags and 2 != 0,
                )
            }
            i += length
        }
        return out
    }

    private fun le32(b: ByteArray, i: Int): Int =
        (b[i].toInt() and 0xff) or ((b[i + 1].toInt() and 0xff) shl 8) or ((b[i + 2].toInt() and 0xff) shl 16) or ((b[i + 3].toInt() and 0xff) shl 24)
}
