package com.logie.blizz.forever.tact

import java.io.ByteArrayOutputStream
import java.io.EOFException
import java.io.InputStream
import java.util.zip.Inflater

/*
 * The formats of Blizzard's content delivery (TACT) and local storage (CASC) that the Forever client download needs,
 * after the public descriptions (wowdev.wiki TACT/CASC) and CascLib's reader. Plain JVM: the same code runs on the
 * phone and on a desktop JVM (where it is checked against Blizzard's CDN and CascLib).
 */

/** Bob Jenkins' lookup3 (`hashlittle`, `hashlittle2`), byte by byte: what CASC's index files are checksummed with. */
object Jenkins {
    private fun rot(x: Int, k: Int) = (x shl k) or (x ushr (32 - k))

    /** hashlittle2: returns (c, b) — the primary and secondary hash — for [pc] and [pb] in. */
    fun hashlittle2(data: ByteArray, offset: Int, length: Int, pc: Int, pb: Int): Pair<Int, Int> {
        var a = 0xdeadbeef.toInt() + length + pc
        var b = a
        var c = a + pb
        var k = offset
        var left = length
        fun at(i: Int) = data[k + i].toInt() and 0xFF
        while (left > 12) {
            a += at(0) or (at(1) shl 8) or (at(2) shl 16) or (at(3) shl 24)
            b += at(4) or (at(5) shl 8) or (at(6) shl 16) or (at(7) shl 24)
            c += at(8) or (at(9) shl 8) or (at(10) shl 16) or (at(11) shl 24)
            a -= c; a = a xor rot(c, 4); c += b
            b -= a; b = b xor rot(a, 6); a += c
            c -= b; c = c xor rot(b, 8); b += a
            a -= c; a = a xor rot(c, 16); c += b
            b -= a; b = b xor rot(a, 19); a += c
            c -= b; c = c xor rot(b, 4); b += a
            left -= 12
            k += 12
        }
        if (left == 0) return c to b
        if (left >= 12) c += at(11) shl 24
        if (left >= 11) c += at(10) shl 16
        if (left >= 10) c += at(9) shl 8
        if (left >= 9) c += at(8)
        if (left >= 8) b += at(7) shl 24
        if (left >= 7) b += at(6) shl 16
        if (left >= 6) b += at(5) shl 8
        if (left >= 5) b += at(4)
        if (left >= 4) a += at(3) shl 24
        if (left >= 3) a += at(2) shl 16
        if (left >= 2) a += at(1) shl 8
        a += at(0)
        c = c xor b; c -= rot(b, 14)
        a = a xor c; a -= rot(c, 11)
        b = b xor a; b -= rot(a, 25)
        c = c xor b; c -= rot(b, 16)
        a = a xor c; a -= rot(c, 4)
        b = b xor a; b -= rot(a, 14)
        c = c xor b; c -= rot(b, 24)
        return c to b
    }

    fun hashlittle(data: ByteArray, offset: Int, length: Int, initval: Int): Int = hashlittle2(data, offset, length, initval, 0).first
}

/** A content or encoding key (MD5, 16 bytes) as two longs, so a million of them fit in arrays. Ordered as unsigned bytes. */
data class Key16(val hi: Long, val lo: Long) : Comparable<Key16> {
    override fun compareTo(other: Key16): Int {
        val h = java.lang.Long.compareUnsigned(hi, other.hi)
        return if (h != 0) h else java.lang.Long.compareUnsigned(lo, other.lo)
    }

    fun bytes(): ByteArray = ByteArray(16).also { out ->
        for (i in 0 until 8) { out[i] = (hi ushr (56 - 8 * i)).toByte(); out[8 + i] = (lo ushr (56 - 8 * i)).toByte() }
    }

    fun hex(): String = bytes().joinToString("") { "%02x".format(it) }

    companion object {
        fun of(data: ByteArray, offset: Int = 0): Key16 {
            var hi = 0L
            var lo = 0L
            for (i in 0 until 8) { hi = (hi shl 8) or (data[offset + i].toLong() and 0xFF); lo = (lo shl 8) or (data[offset + 8 + i].toLong() and 0xFF) }
            return Key16(hi, lo)
        }

        fun hex(text: String): Key16 {
            require(text.length == 32) { "Not a 16-byte key: $text" }
            return of(ByteArray(16) { text.substring(2 * it, 2 * it + 2).toInt(16).toByte() })
        }
    }
}

class EncryptedContentException : Exception("This file is encrypted")

/** What came from a server isn't what its name (its hash) says: retried from another server. */
class CorruptDownloadException(message: String) : java.io.IOException(message)

/**
 * Every file on Blizzard's CDN is named by a hash of itself, so each download is checked before it is kept: a
 * config by the MD5 of its text, an archive index by the MD5 of its 28-byte footer, an encoded (BLTE) file by its
 * encoding key = the MD5 of its BLTE header (or of the whole file when it has none).
 */
object Verify {
    private fun md5(b: ByteArray, off: Int, len: Int): ByteArray = java.security.MessageDigest.getInstance("MD5").apply { update(b, off, len) }.digest()
    private fun hex(b: ByteArray) = b.joinToString("") { "%02x".format(it) }

    fun config(bytes: ByteArray, hash: String) = hex(md5(bytes, 0, bytes.size)).equals(hash, ignoreCase = true)

    fun index(bytes: ByteArray, hash: String) = bytes.size >= 28 && hex(md5(bytes, bytes.size - 28, 28)).equals(hash, ignoreCase = true)

    /** A whole BLTE file: its key (the header's MD5, or the file's without a header) and every frame's MD5. */
    fun blte(bytes: ByteArray, ekey: Key16): Boolean = BlteStream(ekey).apply { update(bytes, 0, bytes.size) }.matches()

    /** The first bytes of what came, for an error message ("<html>…" says a lot). */
    fun preview(bytes: ByteArray, n: Int = 16): String = bytes.take(n).joinToString(" ") { "%02x".format(it) }

    /**
     * [Verify.blte] for data streaming through (an entry being written to the storage): the BLTE header's MD5 is
     * the encoding key, and the header lists each frame's MD5, so every byte is checked, a frame at a time.
     */
    class BlteStream(private val ekey: Key16) {
        private val keyDigest = java.security.MessageDigest.getInstance("MD5")
        private val frameDigest = java.security.MessageDigest.getInstance("MD5")
        private val header = java.io.ByteArrayOutputStream(64)
        private var headerSize = -1 // -1: not read yet; 0: no frame table (the key covers the whole file)
        private var seen = 0L
        private var sizes = IntArray(0)
        private var hashes = emptyArray<ByteArray>()
        private var frame = 0
        private var frameLeft = 0L
        private var ok = true

        fun update(b: ByteArray, off: Int, len: Int) {
            var o = off
            var n = len
            while (n > 0) {
                if (headerSize < 0 || seen < headerSize) {
                    val want = (if (headerSize < 0) 8 - seen else headerSize - seen).toInt()
                    val take = minOf(want, n)
                    header.write(b, o, take); keyDigest.update(b, o, take)
                    seen += take; o += take; n -= take
                    if (headerSize < 0 && seen == 8L) {
                        val h = header.toByteArray()
                        if (String(h, 0, 4, Charsets.ISO_8859_1) != "BLTE") ok = false
                        headerSize = be32(h, 4)
                        if (headerSize != 0 && (headerSize < 12 || headerSize > (1 shl 24))) { ok = false; headerSize = 0 }
                    }
                    if (headerSize > 0 && seen == headerSize.toLong()) frames()
                    continue
                }
                if (headerSize == 0) { keyDigest.update(b, o, n); seen += n; return }
                if (frame >= sizes.size) { ok = false; seen += n; return } // more data than the frames say
                val take = minOf(frameLeft, n.toLong()).toInt()
                frameDigest.update(b, o, take)
                frameLeft -= take; seen += take; o += take; n -= take
                if (frameLeft == 0L) next()
            }
        }

        private fun frames() {
            val h = header.toByteArray()
            val count = ((h[9].toInt() and 0xFF) shl 16) or ((h[10].toInt() and 0xFF) shl 8) or (h[11].toInt() and 0xFF)
            if (h[8].toInt() != 0x0F || 12 + 24 * count != headerSize) { ok = false; return }
            sizes = IntArray(count) { be32(h, 12 + it * 24) }
            hashes = Array(count) { h.copyOfRange(12 + it * 24 + 8, 12 + it * 24 + 24) }
            frame = -1
            frameLeft = 0
            next()
        }

        /** Closes the current frame (its MD5 checked) and opens the next; empty frames are checked at once. */
        private fun next() {
            if (frame >= 0 && !frameDigest.digest().contentEquals(hashes[frame])) ok = false
            frame++
            while (frame < sizes.size && sizes[frame] == 0) {
                if (!frameDigest.digest().contentEquals(hashes[frame])) ok = false
                frame++
            }
            frameLeft = if (frame < sizes.size) sizes[frame].toLong() else 0L
        }

        fun matches(): Boolean = ok && seen >= 8 && keyDigest.digest().contentEquals(ekey.bytes()) && (headerSize == 0 || frame == sizes.size)

        fun preview(): String = header.toByteArray().take(8).joinToString(" ") { "%02x".format(it) }
    }
}

/** BLTE, the frame format every file on the CDN and in local storage is wrapped in. */
object Blte {
    /** Decodes a whole BLTE file held in memory (small files: manifests, configs, install files). */
    fun decode(data: ByteArray): ByteArray = BlteInputStream(data.inputStream()).use { it.readBytes() }

    internal fun decodeFrame(frame: ByteArray, length: Int, out: ByteArrayOutputStream) {
        when (frame[0].toInt().toChar()) {
            'N' -> out.write(frame, 1, length - 1)
            'Z' -> {
                val inflater = Inflater()
                try {
                    inflater.setInput(frame, 1, length - 1)
                    val buffer = ByteArray(1 shl 16)
                    while (!inflater.finished()) {
                        val n = inflater.inflate(buffer)
                        if (n == 0 && (inflater.needsInput() || inflater.needsDictionary())) throw java.util.zip.DataFormatException("Truncated zlib frame")
                        out.write(buffer, 0, n)
                    }
                } finally { inflater.end() }
            }
            'E' -> throw EncryptedContentException()
            else -> throw java.io.IOException("Unsupported BLTE frame mode '${frame[0].toInt().toChar()}'")
        }
    }
}

/** Streams the decoded content of a BLTE file, a frame at a time (the 140 MB encoding table never sits in memory whole). */
class BlteInputStream(private val source: InputStream) : InputStream() {
    private val frameSizes: IntArray
    private var nextFrame = 0
    private var current = ByteArray(0)
    private var pos = 0
    private var singleFrameRest = false

    init {
        val head = readFully(8)
        if (String(head, 0, 4, Charsets.ISO_8859_1) != "BLTE") throw java.io.IOException("Not BLTE data (it begins ${Verify.preview(head, 8)})")
        val headerSize = be32(head, 4)
        if (headerSize == 0) {
            frameSizes = IntArray(0)
            singleFrameRest = true
        } else {
            val table = readFully(headerSize - 8)
            require(table[0].toInt() == 0x0F) { "Bad BLTE frame table" }
            val count = ((table[1].toInt() and 0xFF) shl 16) or ((table[2].toInt() and 0xFF) shl 8) or (table[3].toInt() and 0xFF)
            frameSizes = IntArray(count) { be32(table, 4 + it * 24) }
        }
    }

    private fun readFully(n: Int): ByteArray {
        val out = ByteArray(n)
        var done = 0
        while (done < n) {
            val r = source.read(out, done, n - done)
            if (r < 0) throw EOFException("BLTE ended early")
            done += r
        }
        return out
    }

    private fun fill(): Boolean {
        while (pos >= current.size) {
            val frame: ByteArray = when {
                singleFrameRest -> { singleFrameRest = false; source.readBytes().also { if (it.isEmpty()) return false } }
                nextFrame < frameSizes.size -> readFully(frameSizes[nextFrame++])
                else -> return false
            }
            val out = ByteArrayOutputStream(frame.size * 2)
            Blte.decodeFrame(frame, frame.size, out)
            current = out.toByteArray()
            pos = 0
        }
        return true
    }

    override fun read(): Int = if (!fill()) -1 else current[pos++].toInt() and 0xFF

    override fun read(b: ByteArray, off: Int, len: Int): Int {
        if (len == 0) return 0
        if (!fill()) return -1
        val n = minOf(len, current.size - pos)
        System.arraycopy(current, pos, b, off, n)
        pos += n
        return n
    }

    override fun close() = source.close()
}

internal fun be32(b: ByteArray, o: Int) =
    ((b[o].toInt() and 0xFF) shl 24) or ((b[o + 1].toInt() and 0xFF) shl 16) or ((b[o + 2].toInt() and 0xFF) shl 8) or (b[o + 3].toInt() and 0xFF)

internal fun be16(b: ByteArray, o: Int) = ((b[o].toInt() and 0xFF) shl 8) or (b[o + 1].toInt() and 0xFF)

internal fun beN(b: ByteArray, o: Int, n: Int): Long {
    var v = 0L
    for (i in 0 until n) v = (v shl 8) or (b[o + i].toLong() and 0xFF)
    return v
}

internal fun le32(b: ByteArray, o: Int) =
    (b[o].toInt() and 0xFF) or ((b[o + 1].toInt() and 0xFF) shl 8) or ((b[o + 2].toInt() and 0xFF) shl 16) or ((b[o + 3].toInt() and 0xFF) shl 24)

object Tact {
    /** A `key = value value` config (build config, CDN config). */
    fun parseConfig(text: String): Map<String, List<String>> = text.lineSequence()
        .map { it.trim() }
        .filter { it.isNotEmpty() && !it.startsWith("#") && " = " in it }
        .associate { line -> line.substringBefore(" = ").trim() to line.substringAfter(" = ").trim().split(' ').filter(String::isNotEmpty) }

    /** A `Name!TYPE:size|...` table (version service, .build.info): rows as column-name maps. */
    fun parseTable(text: String): List<Map<String, String>> {
        val lines = text.lineSequence().map { it.trim() }.filter { it.isNotEmpty() && !it.startsWith("#") }.toList()
        if (lines.isEmpty()) return emptyList()
        val names = lines[0].split('|').map { it.substringBefore('!') }
        return lines.drop(1).map { row -> names.zip(row.split('|')).toMap() }
    }

    /** A CDN archive index (`<archive>.index`): calls [entry] with each key, encoded size and offset in the archive. */
    fun parseIndex(data: ByteArray, entry: (key: ByteArray, keyOffset: Int, size: Long, offset: Long) -> Unit) {
        val checksumSize = data[data.size - 13].toInt() and 0xFF
        val f = data.size - (12 + 2 * checksumSize) + checksumSize // start of the footer's fixed fields
        val blockKb = data[f + 3].toInt() and 0xFF
        val offsetBytes = data[f + 4].toInt() and 0xFF
        val sizeBytes = data[f + 5].toInt() and 0xFF
        val keyBytes = data[f + 6].toInt() and 0xFF
        val count = le32(data, f + 8).toLong() and 0xFFFFFFFFL
        val blockSize = blockKb * 1024
        val entrySize = keyBytes + sizeBytes + offsetBytes
        val perBlock = blockSize / entrySize
        var seen = 0L
        var block = 0
        while (seen < count) {
            val base = block * blockSize
            if (base + entrySize > data.size) break
            for (i in 0 until perBlock) {
                val o = base + i * entrySize
                if (seen >= count || o + entrySize > data.size) break
                if ((0 until keyBytes).all { data[o + it].toInt() == 0 }) break
                entry(data, o, beN(data, o + keyBytes, sizeBytes), if (offsetBytes == 0) 0 else beN(data, o + keyBytes + sizeBytes, offsetBytes))
                seen++
            }
            block++
        }
    }

    /** Tags of a download or install manifest: name -> (group type, bit set per entry). */
    class Tags(val byName: Map<String, Pair<Int, ByteArray>>) {
        private fun has(mask: ByteArray, i: Int) = (mask[i ushr 3].toInt() shr (7 - (i and 7))) and 1 == 1

        /** A selection, prepared once: per tag group the wanted masks, and the excluded masks. */
        inner class Selection(wanted: Set<String>, excluded: Set<String>) {
            private val excludedMasks = byName.filterKeys { it in excluded }.values.map { it.second }
            private val groupMasks: List<List<ByteArray>> = byName.entries.groupBy({ it.value.first }, { it.key })
                .values.map { names -> names.filter { it in wanted }.map { byName.getValue(it).second } }
                .filter { it.isNotEmpty() }

            /**
             * Whether entry [i] is part of the install: in every tag group that names a wanted tag (platform, architecture,
             * locale, region, content) it carries one of them, and it carries none of the excluded (optional packs).
             */
            fun selects(i: Int): Boolean {
                for (mask in excludedMasks) if (has(mask, i)) return false
                for (masks in groupMasks) if (masks.none { has(it, i) }) return false
                return true
            }
        }

        fun select(wanted: Set<String>, excluded: Set<String>) = Selection(wanted, excluded)
    }

    private fun readTags(data: ByteArray, start: Int, tagCount: Int, entryCount: Int): Pair<Tags, Int> {
        var p = start
        val bytes = (entryCount + 7) / 8
        val tags = LinkedHashMap<String, Pair<Int, ByteArray>>()
        repeat(tagCount) {
            var e = p
            while (data[e].toInt() != 0) e++
            val name = String(data, p, e - p, Charsets.UTF_8)
            p = e + 1
            val type = be16(data, p)
            p += 2
            tags[name] = type to data.copyOfRange(p, p + bytes)
            p += bytes
        }
        return Tags(tags) to p
    }

    /**
     * The download manifest: every encoded file of the build (2.2 million for Forever), with its encoding key (as two
     * long arrays: no object per entry), encoded size, priority and tags.
     */
    class DownloadManifest(val hi: LongArray, val lo: LongArray, val sizes: LongArray, val priorities: ByteArray, val tags: Tags) {
        val size get() = hi.size
        fun key(i: Int) = Key16(hi[i], lo[i])
    }

    /** Reads a download manifest from its decoded stream (the 55 MB table is never held as one array). */
    fun parseDownload(input: InputStream): DownloadManifest {
        val head = input.readNBytesCompat(11)
        require(head[0].toInt().toChar() == 'D' && head[1].toInt().toChar() == 'L') { "Not a download manifest" }
        val version = head[2].toInt()
        val keySize = head[3].toInt()
        val hasChecksum = head[4].toInt() != 0
        val count = be32(head, 5)
        val tagCount = be16(head, 9)
        var flagBytes = 0
        if (version >= 2) flagBytes = input.read() and 0xFF
        if (version >= 3) input.skipFully(4)
        val hi = LongArray(count)
        val lo = LongArray(count)
        val sizes = LongArray(count)
        val priorities = ByteArray(count)
        val entry = ByteArray(keySize + 6 + (if (hasChecksum) 4 else 0) + flagBytes)
        val buffered = java.io.BufferedInputStream(input, 1 shl 16)
        for (i in 0 until count) {
            var done = 0
            while (done < entry.size) { val r = buffered.read(entry, done, entry.size - done); if (r < 0) throw EOFException("Download manifest ended early"); done += r }
            hi[i] = beN(entry, 0, 8)
            lo[i] = beN(entry, 8, 8)
            sizes[i] = beN(entry, keySize, 5)
            priorities[i] = entry[keySize + 5]
        }
        val rest = buffered.readBytes()
        val (tags, _) = readTags(rest, 0, tagCount, count)
        return DownloadManifest(hi, lo, sizes, priorities, tags)
    }

    /** The install manifest: the files laid out as plain files beside the storage (the game's programs). */
    class InstallFile(val name: String, val contentKey: Key16, val size: Long)
    class InstallManifest(val files: List<InstallFile>, val tags: Tags)

    fun parseInstall(data: ByteArray): InstallManifest {
        require(data[0].toInt().toChar() == 'I' && data[1].toInt().toChar() == 'N') { "Not an install manifest" }
        val hashSize = data[3].toInt()
        val tagCount = be16(data, 4)
        val count = be32(data, 6)
        val (tags, start) = readTags(data, 10, tagCount, count)
        var p = start
        val files = ArrayList<InstallFile>(count)
        repeat(count) {
            var e = p
            while (data[e].toInt() != 0) e++
            val name = String(data, p, e - p, Charsets.UTF_8)
            p = e + 1
            val key = Key16.of(data, p)
            p += hashSize
            files += InstallFile(name, key, be32(data, p).toLong() and 0xFFFFFFFFL)
            p += 4
        }
        return InstallManifest(files, tags)
    }

    /**
     * Looks [wanted] content keys up in the encoding table (streamed; only the pages that can hold them are parsed):
     * content key -> encoding key.
     */
    fun encodingKeys(encoding: InputStream, wanted: Set<Key16>): Map<Key16, Key16> {
        val head = encoding.readNBytesCompat(22)
        require(head[0].toInt().toChar() == 'E' && head[1].toInt().toChar() == 'N') { "Not an encoding table" }
        val ckeySize = head[3].toInt()
        val ekeySize = head[4].toInt()
        val pageSize = be16(head, 5) * 1024
        val pageCount = be32(head, 9)
        val especSize = be32(head, 18)
        encoding.skipFully(especSize.toLong())
        val firstKeys = Array(pageCount) { Key16.of(encoding.readNBytesCompat(32), 0) }
        val sorted = wanted.sorted()
        val found = HashMap<Key16, Key16>()
        for (page in 0 until pageCount) {
            val lo = firstKeys[page]
            val hi = if (page + 1 < pageCount) firstKeys[page + 1] else null
            val needed = sorted.any { it >= lo && (hi == null || it < hi) }
            if (!needed) { encoding.skipFully(pageSize.toLong()); continue }
            val data = encoding.readNBytesCompat(pageSize)
            var p = 0
            while (p + 6 + ckeySize <= data.size) {
                val keyCount = data[p].toInt() and 0xFF
                if (keyCount == 0) break
                val ckey = Key16.of(data, p + 6)
                if (ckey in wanted) found[ckey] = Key16.of(data, p + 6 + ckeySize)
                p += 6 + ckeySize + keyCount * ekeySize
            }
        }
        return found
    }
}

internal fun InputStream.readNBytesCompat(n: Int): ByteArray {
    val out = ByteArray(n)
    var done = 0
    while (done < n) {
        val r = read(out, done, n - done)
        if (r < 0) throw EOFException("Ended early")
        done += r
    }
    return out
}

internal fun InputStream.skipFully(n: Long) {
    var left = n
    val buffer = ByteArray(1 shl 16)
    while (left > 0) {
        val r = read(buffer, 0, minOf(buffer.size.toLong(), left).toInt())
        if (r < 0) throw EOFException("Ended early")
        left -= r
    }
}
