package com.logie.blizz.wrathpp

import java.io.File
import java.io.FilterInputStream
import java.io.IOException
import java.io.InputStream
import java.io.RandomAccessFile
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.zip.CRC32
import java.util.zip.Inflater
import java.util.zip.InflaterInputStream

/**
 * A new looks release without its 1 GB again (the user: "Can we cache these ... rather than loading them every time"). A release
 * is a zip; most of its files (models, textures) are the ones already installed in Wrath++'s patch folder. This reads the zip's
 * central directory (a few MB, by ranged requests), compares each entry's CRC-32 with the installed file of the same name (the
 * patch folder's `client/` files, the server copy's tables), downloads only the entries that differ or are new (ranged requests
 * of their bytes) and installs the whole from the installed files and those ([WrathppLooks.installFrom]). Any failure (a server
 * that does no ranges, a CRC that doesn't match, a package this can't read) is an exception, and [WrathppLooks.ensure] downloads
 * the whole zip as before. Unit-tested over a local file; NOT run on a phone.
 */
object WrathppLooksDelta {
    /** A file of the zip: where its local header is, and what it is. */
    class Entry(val name: String, val method: Int, val crc: Long, val compressed: Long, val size: Long, val headerAt: Long, val nameLength: Int)

    /** The zip's bytes, by ranges. */
    interface Ranges {
        val length: Long
        fun open(start: Long, endInclusive: Long): InputStream
        fun read(start: Long, count: Int): ByteArray = open(start, start + count - 1).use { it.readBytes() }
    }

    class HttpRanges(private val url: String, override val length: Long) : Ranges {
        override fun open(start: Long, endInclusive: Long): InputStream = WrathppAddon.openRange(url, start, minOf(endInclusive, length - 1))
    }

    private fun le(b: ByteArray, at: Int): ByteBuffer = ByteBuffer.wrap(b).order(ByteOrder.LITTLE_ENDIAN).position(at) as ByteBuffer
    private fun u16(b: ByteArray, at: Int) = le(b, at).short.toInt() and 0xFFFF
    private fun u32(b: ByteArray, at: Int) = le(b, at).int.toLong() and 0xFFFFFFFFL
    private fun u64(b: ByteArray, at: Int) = le(b, at).long

    /** The entries of the zip [r] (its central directory; the zip64 forms too). */
    fun entries(r: Ranges): List<Entry> {
        val tailLength = minOf(r.length, 65_557L + 22).toInt()
        val tailStart = r.length - tailLength
        val tail = r.read(tailStart, tailLength)
        var eocd = -1
        for (i in tail.size - 22 downTo 0) if (u32(tail, i) == 0x06054b50L) { eocd = i; break }
        if (eocd < 0) throw IOException("Not a zip (no end record)")
        var count = u16(tail, eocd + 10).toLong()
        var size = u32(tail, eocd + 12)
        var offset = u32(tail, eocd + 16)
        if (count == 0xFFFFL || size == 0xFFFFFFFFL || offset == 0xFFFFFFFFL) {
            val loc = eocd - 20
            if (loc < 0 || u32(tail, loc) != 0x07064b50L) throw IOException("A zip64 end record this can't find")
            val at = u64(tail, loc + 8)
            val z = r.read(at, 56)
            if (u32(z, 0) != 0x06064b50L) throw IOException("A zip64 end record this can't read")
            count = u64(z, 32); size = u64(z, 40); offset = u64(z, 48)
        }
        if (size > 64L shl 20) throw IOException("A central directory too large to read here")
        val cd = r.read(offset, size.toInt())
        val out = ArrayList<Entry>(count.toInt())
        var at = 0
        while (at + 46 <= cd.size && u32(cd, at) == 0x02014b50L) {
            val method = u16(cd, at + 10)
            var crc = u32(cd, at + 16)
            var compressed = u32(cd, at + 20)
            var length = u32(cd, at + 24)
            val nameLength = u16(cd, at + 28); val extraLength = u16(cd, at + 30); val commentLength = u16(cd, at + 32)
            var header = u32(cd, at + 42)
            val name = String(cd, at + 46, nameLength, Charsets.UTF_8)
            if (length == 0xFFFFFFFFL || compressed == 0xFFFFFFFFL || header == 0xFFFFFFFFL) {
                var x = at + 46 + nameLength
                val end = x + extraLength
                while (x + 4 <= end) {
                    val id = u16(cd, x); val n = u16(cd, x + 2)
                    if (id == 1) {
                        var p = x + 4
                        if (length == 0xFFFFFFFFL) { length = u64(cd, p); p += 8 }
                        if (compressed == 0xFFFFFFFFL) { compressed = u64(cd, p); p += 8 }
                        if (header == 0xFFFFFFFFL) { header = u64(cd, p) }
                    }
                    x += 4 + n
                }
            }
            out.add(Entry(name, method, crc, compressed, length, header, nameLength))
            at += 46 + nameLength + extraLength + commentLength
        }
        if (out.size.toLong() != count) throw IOException("The central directory lists ${out.size} files, its end record $count")
        return out
    }

    private fun crcOf(file: File): Long {
        val c = CRC32()
        file.inputStream().buffered(1 shl 16).use { input -> val b = ByteArray(1 shl 16); while (true) { val n = input.read(b); if (n < 0) break; c.update(b, 0, n) } }
        return c.value
    }

    /** What is installed that a release's entry can be taken from, or null. */
    private fun installedFile(patch: File, e: Entry): File? {
        val file = when {
            e.name.startsWith("client/") -> File(patch, e.name.removePrefix("client/"))
            e.name.startsWith("dbc/") && !e.name.removePrefix("dbc/").contains('/') -> File(patch, "${WrathppLooks.SERVER_COPY}/${e.name.removePrefix("dbc/")}")
            else -> return null
        }
        return file.takeIf { it.isFile && it.length() == e.size && crcOf(it) == e.crc }
    }

    /** The entries that have to come from the release (those with no installed copy), how many bytes that is, and the installed files to use for the rest. */
    fun plan(patch: File, all: List<Entry>): Triple<List<Entry>, Long, Map<String, File>> {
        val reuse = HashMap<String, File>()
        val need = ArrayList<Entry>()
        for (e in all) {
            if (e.name.endsWith("/")) continue
            val installed = installedFile(patch, e)
            if (installed != null) reuse[e.name] = installed else need.add(e)
        }
        return Triple(need, need.sumOf { it.compressed }, reuse)
    }

    private const val LOCAL_SLACK = 512
    private const val GAP = 128L * 1024
    private const val BATCH = 64L * 1024 * 1024

    /**
     * Installs the release [r] (its sha [sha]) over what is in [client] and [server] from the installed files and the entries it must
     * fetch; returns false when this isn't the way (nothing installed to take from, or most of the package changed), true when installed.
     * [work]: a folder for the fetched bytes.
     */
    fun update(client: File, server: File, r: Ranges, sha: String, work: File, say: (String, Float?) -> Unit, tables: ((String) -> ByteArray?)? = null): Boolean {
        val patch = File(client, "Data/${WrathppLooks.PATCH}")
        if (!patch.isDirectory) return false
        say("Looking at what changed in Wrath++'s looks", null)
        val all = entries(r)
        say("Checking Wrath++'s installed looks", null)
        val (need, bytes, reuse) = plan(patch, all)
        val total = all.sumOf { it.compressed }
        if (total > 0 && bytes * 10 > total * 7) return false     // most of it is new: the whole download is simpler (and resumes)
        work.deleteRecursively(); work.mkdirs()
        val pack = File(work, "looks-delta.pack")
        val where = HashMap<String, Long>()                       // an entry's local header, in the pack
        try {
            RandomAccessFile(pack, "rw").use { out ->
                var done = 0L
                val sorted = need.sortedBy { it.headerAt }
                var i = 0
                while (i < sorted.size) {
                    var j = i
                    var end = sorted[i].headerAt + 30 + sorted[i].nameLength + LOCAL_SLACK + sorted[i].compressed
                    while (j + 1 < sorted.size && sorted[j + 1].headerAt - end <= GAP && end - sorted[i].headerAt < BATCH) {
                        j++
                        end = maxOf(end, sorted[j].headerAt + 30 + sorted[j].nameLength + LOCAL_SLACK + sorted[j].compressed)
                    }
                    val start = sorted[i].headerAt
                    val last = minOf(end, r.length) - 1
                    val base = out.length()
                    out.seek(base)
                    r.open(start, last).use { input ->
                        val buffer = ByteArray(1 shl 16)
                        var got = 0L
                        while (true) {
                            val n = input.read(buffer); if (n < 0) break
                            out.write(buffer, 0, n); got += n; done += n
                            say("Downloading what changed in Wrath++'s looks: ${done shr 20} / ${bytes shr 20} MB", if (bytes > 0) minOf(1f, done.toFloat() / bytes) else null)
                        }
                        if (got != last - start + 1) throw IOException("A ranged download came short ($got of ${last - start + 1})")
                    }
                    for (k in i..j) where[sorted[k].name] = base + (sorted[k].headerAt - start)
                    i = j + 1
                }
            }
            RandomAccessFile(pack, "r").use { packFile ->
                val source: ((String, InputStream) -> Unit) -> Unit = { entry ->
                    for (e in all) {
                        if (e.name.endsWith("/")) continue
                        val installed = reuse[e.name]
                        if (installed != null) {
                            installed.inputStream().buffered().use { entry(e.name, NoClose(it)) }
                        } else {
                            entry(e.name, NoClose(fetched(packFile, e, where[e.name] ?: throw IOException("${e.name} was not fetched"))))
                        }
                    }
                }
                WrathppLooks.installFrom(client, server, source, sha, { n -> say("Putting in Wrath++'s looks: $n files", null) }, tables)
            }
        } finally {
            work.deleteRecursively()
        }
        return true
    }

    private class NoClose(input: InputStream) : FilterInputStream(input) { override fun close() {} }

    /** [e]'s bytes, from the pack where its local header is at [at]: inflated when it was deflated, its CRC-32 checked at the end. */
    internal fun fetched(pack: RandomAccessFile, e: Entry, at: Long): InputStream {
        val header = ByteArray(30)
        pack.seek(at); pack.readFully(header)
        if (u32(header, 0) != 0x04034b50L) throw IOException("${e.name}: no local header where it should be")
        val data = at + 30 + u16(header, 26) + u16(header, 28)
        val raw = object : InputStream() {
            var left = e.compressed
            var position = data
            override fun read(): Int { val b = ByteArray(1); return if (read(b, 0, 1) < 0) -1 else b[0].toInt() and 0xFF }
            override fun read(b: ByteArray, off: Int, len: Int): Int {
                if (left <= 0) return -1
                val n = minOf(len.toLong(), left).toInt()
                pack.seek(position)
                val got = pack.read(b, off, n)
                if (got < 0) throw IOException("${e.name}: cut short")
                position += got; left -= got
                return got
            }
        }
        val content: InputStream = when (e.method) {
            0 -> raw
            8 -> InflaterInputStream(raw, Inflater(true), 1 shl 16)
            else -> throw IOException("${e.name}: a way of packing this can't read (${e.method})")
        }
        val crc = CRC32()
        var length = 0L
        return object : FilterInputStream(content) {
            override fun read(): Int { val b = ByteArray(1); return if (read(b, 0, 1) < 0) -1 else b[0].toInt() and 0xFF }
            override fun read(b: ByteArray, off: Int, len: Int): Int {
                val n = super.read(b, off, len)
                if (n > 0) { crc.update(b, off, n); length += n }
                else if (n < 0 && (crc.value != e.crc || length != e.size)) throw IOException("${e.name}: its bytes don't match the release's checksum")
                return n
            }
        }
    }
}
