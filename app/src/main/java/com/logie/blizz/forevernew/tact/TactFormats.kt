package com.logie.blizz.forevernew.tact

import java.io.ByteArrayOutputStream
import java.io.IOException
import java.util.zip.Inflater

/** Hex helpers for the 16-byte keys of Blizzard's content system (TACT / CASC). */
fun ByteArray.hex(): String = joinToString("") { "%02x".format(it) }
fun String.unhex(): ByteArray = ByteArray(length / 2) { substring(it * 2, it * 2 + 2).toInt(16).toByte() }

/** The text files Blizzard's version and CDN servers answer with. */
object TactText {
    /** `Name!TYPE:len|...` header, `## seqn` comments, then rows: a list of rows by column name. */
    fun table(text: String): List<Map<String, String>> {
        val lines = text.lineSequence().map { it.trim() }.filter { it.isNotEmpty() && !it.startsWith("##") }.toList()
        if (lines.isEmpty()) return emptyList()
        val header = lines.first().split('|').map { it.substringBefore('!') }
        return lines.drop(1).map { row -> row.split('|').let { c -> header.indices.associate { header[it] to c.getOrElse(it) { "" } } } }
    }

    /** `key = value value` lines of a build or CDN config. */
    fun config(text: String): Map<String, List<String>> =
        text.lineSequence().map { it.trim() }.filter { it.isNotEmpty() && !it.startsWith("#") && '=' in it }
            .associate { it.substringBefore('=').trim() to it.substringAfter('=').trim().split(' ').filter { s -> s.isNotEmpty() } }
}

/** BLTE: Blizzard's framed, compressed container. Only the plain (N) and zlib (Z) frames the manifests use; anything else is refused. */
object Blte {
    class Frame(val encodedSize: Int, val decodedSize: Int)
    class Header(val headerSize: Int, val frames: List<Frame>) {
        val dataStart get() = if (headerSize == 0) 8 else headerSize
    }

    fun header(b: ByteArray): Header {
        if (b.size < 8 || b[0] != 'B'.code.toByte() || b[1] != 'L'.code.toByte() || b[2] != 'T'.code.toByte() || b[3] != 'E'.code.toByte()) throw IOException("not a BLTE file")
        val hs = be32(b, 4)
        if (hs == 0) return Header(0, emptyList())
        if (b.size < hs) throw IOException("BLTE header is cut short")
        val n = ((b[9].toInt() and 0xff) shl 16) or ((b[10].toInt() and 0xff) shl 8) or (b[11].toInt() and 0xff)
        if (hs != 12 + n * 24) throw IOException("BLTE header size is wrong")
        return Header(hs, (0 until n).map { Frame(be32(b, 12 + it * 24), be32(b, 16 + it * 24)) })
    }

    fun decodeFrame(b: ByteArray, off: Int, len: Int, decodedSize: Int = -1): ByteArray {
        if (len < 1) throw IOException("empty BLTE frame")
        return when (val t = b[off].toInt().toChar()) {
            'N' -> b.copyOfRange(off + 1, off + len)
            'Z' -> {
                val inf = Inflater()
                inf.setInput(b, off + 1, len - 1)
                if (decodedSize > 0) {
                    // the size is known: inflate straight into an array of exactly that size (no growing buffer, no copy)
                    val out = ByteArray(decodedSize)
                    var done = 0
                    while (done < decodedSize) {
                        val n = inf.inflate(out, done, decodedSize - done)
                        if (n == 0 && (inf.finished() || inf.needsInput() || inf.needsDictionary())) break
                        done += n
                    }
                    inf.end()
                    if (done != decodedSize) throw IOException("zlib frame is shorter than it says")
                    out
                } else {
                    val out = ByteArrayOutputStream(len * 3)
                    val buf = ByteArray(1 shl 16)
                    while (!inf.finished()) {
                        val n = inf.inflate(buf)
                        if (n == 0 && (inf.needsInput() || inf.needsDictionary())) throw IOException("zlib frame is cut short")
                        out.write(buf, 0, n)
                    }
                    inf.end(); out.toByteArray()
                }
            }
            else -> throw IOException("BLTE frame type '$t' isn't supported")
        }
    }

    /** Decodes into one array of exactly the decoded size (the download manifest is 56 MB: no stream and no copies). */
    fun decode(b: ByteArray): ByteArray {
        val h = header(b)
        if (h.headerSize == 0) return decodeFrame(b, 8, b.size - 8)
        val total = h.frames.sumOf { it.decodedSize.toLong() }
        if (total > Int.MAX_VALUE) throw IOException("BLTE file is too large")
        val out = ByteArray(total.toInt())
        var p = h.dataStart; var o = 0
        for (f in h.frames) {
            val part = decodeFrame(b, p, f.encodedSize, f.decodedSize)
            if (o + part.size > out.size) throw IOException("BLTE frame is larger than it says")
            System.arraycopy(part, 0, out, o, part.size); o += part.size; p += f.encodedSize
        }
        return if (o == out.size) out else out.copyOf(o)
    }
}

fun be32(b: ByteArray, o: Int) = ((b[o].toInt() and 0xff) shl 24) or ((b[o + 1].toInt() and 0xff) shl 16) or ((b[o + 2].toInt() and 0xff) shl 8) or (b[o + 3].toInt() and 0xff)
fun be40(b: ByteArray, o: Int) = (be32(b, o).toLong() and 0xffffffffL shl 8) or (b[o + 4].toLong() and 0xff)
fun be16(b: ByteArray, o: Int) = ((b[o].toInt() and 0xff) shl 8) or (b[o + 1].toInt() and 0xff)

/** The tags of an install or download manifest and which entries have them (one bit each, most significant bit first). */
class TagTable(val names: List<String>, val types: List<Int>, private val masks: List<ByteArray>) {
    fun has(entry: Int, tag: Int) = (masks[tag][entry shr 3].toInt() shr (7 - (entry and 7))) and 1 == 1
    fun index(name: String) = names.indexOf(name)

    /**
     * Whether [entry] is wanted for [selected] tag names: for each kind of tag (platform, architecture, language, region...) the entry has
     * any tag of, it must have at least one selected tag of that kind. An entry with no tag of a kind is wanted whatever is selected.
     */
    fun wanted(entry: Int, selected: Set<String>): Boolean = selector(selected)(entry)

    /** [wanted] for one selection as a function that allocates nothing per entry (it runs over 2.2 million of them). */
    fun selector(selected: Set<String>): (Int) -> Boolean {
        val groups = types.toSet().map { t -> names.indices.filter { types[it] == t }.toIntArray() }
        val sel = BooleanArray(names.size) { names[it] in selected }
        return { entry ->
            var ok = true
            for (g in groups) {
                var any = false; var chosen = false
                for (t in g) if (has(entry, t)) { any = true; if (sel[t]) { chosen = true; break } }
                if (any && !chosen) { ok = false; break }
            }
            ok
        }
    }

    companion object {
        fun read(d: ByteArray, start: Int, tagCount: Int, entryCount: Int): Pair<TagTable, Int> {
            var p = start
            val bytes = (entryCount + 7) / 8
            val names = ArrayList<String>(); val types = ArrayList<Int>(); val masks = ArrayList<ByteArray>()
            repeat(tagCount) {
                var e = p; while (d[e] != 0.toByte()) e++
                names += String(d, p, e - p, Charsets.US_ASCII); p = e + 1
                types += be16(d, p); p += 2
                masks += d.copyOfRange(p, p + bytes); p += bytes
            }
            return TagTable(names, types, masks) to p
        }
    }
}

/** The install manifest: the loose files of the game folder (programs, libraries) by name, as content keys. */
class InstallManifest(val tags: TagTable, val names: List<String>, val contentKeys: List<ByteArray>, val sizes: List<Long>) {
    companion object {
        fun parse(d: ByteArray): InstallManifest {
            if (d.size < 10 || d[0] != 'I'.code.toByte() || d[1] != 'N'.code.toByte()) throw IOException("not an install manifest")
            val hashSize = d[3].toInt() and 0xff
            val tagCount = be16(d, 4); val count = be32(d, 6)
            val (tags, start) = TagTable.read(d, 10, tagCount, count)
            var p = start
            val names = ArrayList<String>(count); val keys = ArrayList<ByteArray>(count); val sizes = ArrayList<Long>(count)
            repeat(count) {
                var e = p; while (d[e] != 0.toByte()) e++
                names += String(d, p, e - p, Charsets.UTF_8); p = e + 1
                keys += d.copyOfRange(p, p + hashSize); p += hashSize
                sizes += be32(d, p).toLong() and 0xffffffffL; p += 4
            }
            return InstallManifest(tags, names, keys, sizes)
        }
    }
}

/**
 * The download manifest: every encoded file (by encoding key) with its size, install priority and tags. Read in place from the decoded
 * bytes (2.2 million entries: an object each would not fit a phone), so an entry is a position, not an object.
 */
class DownloadManifest(val tags: TagTable, private val d: ByteArray, private val start: Int, private val stride: Int, private val hashSize: Int,
    private val basePriority: Int, val count: Int) {
    fun ekey(i: Int): ByteArray = d.copyOfRange(start + i * stride, start + i * stride + hashSize)
    fun prefix(i: Int): Long = d.prefix64(start + i * stride)
    fun size(i: Int): Long = be40(d, start + i * stride + hashSize)
    fun priority(i: Int): Int = (d[start + i * stride + hashSize + 5].toInt() and 0xff).let { if (it > 127) it - 256 else it } - basePriority

    companion object {
        fun parse(d: ByteArray): DownloadManifest {
            if (d.size < 11 || d[0] != 'D'.code.toByte() || d[1] != 'L'.code.toByte()) throw IOException("not a download manifest")
            val version = d[2].toInt() and 0xff
            val hashSize = d[3].toInt() and 0xff
            val hasChecksum = d[4].toInt() != 0
            val count = be32(d, 5); val tagCount = be16(d, 9)
            var p = 11; var flagSize = 0; var basePriority = 0
            if (version >= 2) { flagSize = d[p].toInt() and 0xff; p++ }
            if (version >= 3) { basePriority = d[p].toInt(); p += 4 }
            val stride = hashSize + 5 + 1 + (if (hasChecksum) 4 else 0) + flagSize
            val (tags, _) = TagTable.read(d, p + count * stride, tagCount, count)
            return DownloadManifest(tags, d, p, stride, hashSize, basePriority, count)
        }
    }
}

/** One archive's index on the CDN: which of the archive's bytes hold each encoded file. */
class ArchiveIndex(val name: String, val ekeys: List<ByteArray>, val sizes: IntArray, val offsets: LongArray) {
    companion object {
        /** An index file: pages of (16-byte key, 4-byte size, 4-byte offset) records, a table of contents, and a 36-byte footer. */
        fun parse(name: String, d: ByteArray): ArchiveIndex {
            if (d.size < 36) throw IOException("archive index is cut short")
            val f = d.size - 36
            val pageBytes = (d[f + 19].toInt() and 0xff) * 1024
            val offBytes = d[f + 20].toInt() and 0xff; val sizeBytes = d[f + 21].toInt() and 0xff; val keyBytes = d[f + 22].toInt() and 0xff
            val count = (d[f + 24].toInt() and 0xff) or ((d[f + 25].toInt() and 0xff) shl 8) or ((d[f + 26].toInt() and 0xff) shl 16) or ((d[f + 27].toInt() and 0xff) shl 24)
            if (sizeBytes != 4 || offBytes != 4 || keyBytes != 16 || pageBytes == 0) throw IOException("archive index layout isn't the expected one")
            val entry = keyBytes + sizeBytes + offBytes
            val perPage = pageBytes / entry
            val keys = ArrayList<ByteArray>(count); val sizes = IntArray(count); val offs = LongArray(count)
            for (i in 0 until count) {
                val p = (i / perPage) * pageBytes + (i % perPage) * entry
                keys += d.copyOfRange(p, p + keyBytes); sizes[i] = be32(d, p + keyBytes); offs[i] = be32(d, p + keyBytes + 4).toLong() and 0xffffffffL
            }
            return ArchiveIndex(name, keys, sizes, offs)
        }
    }
}
