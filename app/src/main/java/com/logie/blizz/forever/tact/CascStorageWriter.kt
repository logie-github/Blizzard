package com.logie.blizz.forever.tact

import java.io.BufferedOutputStream
import java.io.DataInputStream
import java.io.EOFException
import java.io.File
import java.io.FileOutputStream
import java.io.InputStream
import java.io.RandomAccessFile

/**
 * Writes a CASC local storage (`Data/data`), the way Blizzard's installer lays it out and CascLib reads it:
 *
 * - `data.NNN` segments (at most 1 GiB each: 30 offset bits), each file an entry of a 30-byte header (the encoding
 *   key byte-reversed, the entry's size with the header, two checksums) followed by its BLTE data as on the CDN;
 * - sixteen `XX00000001.idx` index files (bucket XX of the key's first 9 bytes), version 7: a guarded header and a
 *   guarded block of 18-byte entries (9 key bytes, segment and offset in 5 big-endian bytes, size little-endian),
 *   each guard a Jenkins hash, sorted by key.
 *
 * A journal records every entry once it is fully written, so a download that stops (the app closed, the network
 * gone) resumes with what is there: the segments are cut back to their last recorded entry.
 */
class CascStorageWriter(val dataDir: File) {
    class Placed(val segment: Int, val offset: Int, val size: Int)

    private val journal = File(dataDir, JOURNAL)
    private var nextSegment = 0
    private var journalOut: FileOutputStream? = null

    init { dataDir.mkdirs() }

    /**
     * Reads the journal of an earlier run: entry id -> where it was written. Segments are cut to the end of their
     * last recorded entry (anything after it was a write that didn't finish) and unrecorded segments removed.
     */
    @Synchronized
    fun resume(): Map<Int, Placed> {
        val placed = HashMap<Int, Placed>()
        if (journal.isFile) {
            DataInputStream(journal.inputStream().buffered(1 shl 16)).use { input ->
                while (true) {
                    val id: Int
                    try { id = input.readInt() } catch (_: EOFException) { break }
                    val record = try { Placed(input.readInt(), input.readInt(), input.readInt()) } catch (_: EOFException) { break }
                    placed[id] = record
                }
            }
            // A record cut short by a kill leaves a partial tail: rewrite the journal to whole records.
            val whole = placed.size.toLong() * RECORD
            if (journal.length() != whole) RandomAccessFile(journal, "rw").use { it.setLength(whole) }
        }
        val ends = HashMap<Int, Long>()
        for (p in placed.values) ends[p.segment] = maxOf(ends[p.segment] ?: 0L, p.offset.toLong() + p.size)
        dataDir.listFiles()?.forEach { file ->
            val index = SEGMENT_NAME.matchEntire(file.name)?.groupValues?.get(1)?.toInt() ?: return@forEach
            val end = ends[index]
            if (end == null) file.delete() else if (file.length() != end) RandomAccessFile(file, "rw").use { it.setLength(end) }
        }
        nextSegment = (ends.keys.maxOrNull() ?: -1) + 1
        return placed
    }

    /** A data segment a single worker appends to; a new one is begun when it is full. */
    inner class Segment internal constructor(val index: Int) {
        private val file = FileOutputStream(segmentFile(index), true)
        private val out = BufferedOutputStream(file, 1 shl 20)
        var size = 0L
            private set

        fun fits(length: Long) = size + HEADER + length <= SEGMENT_LIMIT

        /**
         * Appends one entry (its BLTE data read from [data], exactly [length] bytes) and records it as [id] once it
         * is written and checked against its key. Data that doesn't match its key (or ends early) is taken back
         * out of the segment and the call throws, so it can be fetched again. Returns where it went.
         */
        fun write(id: Int, ekey: Key16, data: InputStream, length: Long): Placed {
            val offset = size
            val check = Verify.BlteStream(ekey)
            try {
                out.write(header(ekey, length, offset))
                val buffer = ByteArray(1 shl 16)
                var left = length
                while (left > 0) {
                    val n = data.read(buffer, 0, minOf(buffer.size.toLong(), left).toInt())
                    if (n < 0) throw EOFException("The download of ${ekey.hex()} ended $left bytes early")
                    check.update(buffer, 0, n)
                    out.write(buffer, 0, n)
                    left -= n
                }
                if (!check.matches()) throw CorruptDownloadException("${ekey.hex()} came with the wrong content (it begins ${check.preview()})")
            } catch (e: java.io.IOException) {
                out.flush()
                file.channel.truncate(offset)
                throw e
            }
            out.flush()
            size += HEADER + length
            val placed = Placed(index, offset.toInt(), (HEADER + length).toInt())
            record(id, placed)
            return placed
        }

        fun close() = out.close()
    }

    @Synchronized
    fun newSegment(): Segment = Segment(nextSegment++)

    fun segmentFile(index: Int) = File(dataDir, "data.%03d".format(index))

    @Synchronized
    private fun record(id: Int, placed: Placed) {
        val out = journalOut ?: FileOutputStream(journal, true).also { journalOut = it }
        val r = ByteArray(RECORD)
        for ((i, v) in listOf(id, placed.segment, placed.offset, placed.size).withIndex()) {
            r[i * 4] = (v ushr 24).toByte(); r[i * 4 + 1] = (v ushr 16).toByte(); r[i * 4 + 2] = (v ushr 8).toByte(); r[i * 4 + 3] = v.toByte()
        }
        out.write(r)
    }

    /** Opens an entry's BLTE data (without its header) for reading back. */
    fun read(placed: Placed): InputStream {
        val file = RandomAccessFile(segmentFile(placed.segment), "r")
        file.seek(placed.offset.toLong() + HEADER)
        var left = (placed.size - HEADER).toLong()
        return object : InputStream() {
            override fun read(): Int = if (left <= 0) -1 else file.read().also { if (it >= 0) left-- }
            override fun read(b: ByteArray, off: Int, len: Int): Int {
                if (left <= 0) return -1
                val n = file.read(b, off, minOf(len.toLong(), left).toInt())
                if (n > 0) left -= n
                return n
            }
            override fun close() = file.close()
        }
    }

    /** Writes the sixteen index files for every entry (key, where it is). Done last, once the segments are complete. */
    fun writeIndexes(entries: List<Pair<Key16, Placed>>) {
        synchronized(this) { journalOut?.close(); journalOut = null }
        val buckets = Array(16) { ArrayList<Pair<ByteArray, Placed>>() }
        val seen = HashSet<String>()
        for ((key, placed) in entries) {
            val k9 = key.bytes().copyOf(9)
            if (!seen.add(k9.joinToString("") { "%02x".format(it) })) continue
            buckets[bucket(k9)] += k9 to placed
        }
        dataDir.listFiles()?.filter { it.name.endsWith(".idx") }?.forEach { it.delete() }
        for (b in 0 until 16) {
            val list = buckets[b].sortedWith { x, y -> compareUnsigned(x.first, y.first) }
            File(dataDir, "%02x%08x.idx".format(b, 1)).writeBytes(index(b, list))
        }
    }

    /** Removes the journal once the storage is complete. */
    fun finish() { journalOut?.close(); journalOut = null; journal.delete() }

    companion object {
        const val HEADER = 30
        const val SEGMENT_LIMIT = 1L shl 30
        const val JOURNAL = ".blizz-journal"
        private const val RECORD = 16
        private val SEGMENT_NAME = Regex("""data\.(\d{3,})""")

        /** The index bucket of a key: its first 9 bytes folded by XOR, the two nibbles XORed. */
        fun bucket(key: ByteArray): Int {
            var x = 0
            for (i in 0 until 9) x = x xor (key[i].toInt() and 0xFF)
            return (x and 0x0F) xor (x ushr 4)
        }

        private val OFFSET_TABLE = intArrayOf(
            0x049396B8, 0x72A82A9B, 0xEE626CCA.toInt(), 0x9917754F.toInt(),
            0x15DE40B1, 0xF5A8A9B6.toInt(), 0x421EAC7E, 0xA9D55C9A.toInt(),
            0x317FD40C, 0x04FAF80D, 0x3D6BE971, 0x52933CFD,
            0x27F64B7D, 0xC6F5C11B.toInt(), 0xD5757E3A.toInt(), 0x6C388745,
        )

        /**
         * An entry's 30-byte header at [offset] in its segment: the key reversed, the size with the header (little
         * endian), two zero bytes, a Jenkins hash of those and the offset-keyed checksum (as Blizzard's Agent
         * computes them; CascLib's VerifyHeaderSpan).
         */
        fun header(ekey: Key16, length: Long, offset: Long): ByteArray {
            val h = ByteArray(HEADER)
            val key = ekey.bytes()
            for (i in 0 until 16) h[i] = key[15 - i]
            putLe(h, 16, (HEADER + length).toInt())
            putLe(h, 22, Jenkins.hashlittle(h, 0, 22, 0x3D6BE971))
            val position = (offset + HEADER).toInt()
            val encoded = ByteArray(4).also { putLe(it, 0, OFFSET_TABLE[position and 0x0F] xor position) }
            val hashed = ByteArray(4)
            for (i in 0 until 26) hashed[i and 3] = (hashed[i and 3].toInt() xor h[i].toInt()).toByte()
            for (j in 0 until 4) { val i = 26 + j; h[26 + j] = (hashed[i and 3].toInt() xor encoded[i and 3].toInt()).toByte() }
            return h
        }

        /** One version-7 index file. */
        fun index(bucket: Int, entries: List<Pair<ByteArray, Placed>>): ByteArray {
            val header = ByteArray(16)
            header[0] = 7; header[1] = 0
            header[2] = bucket.toByte(); header[3] = 0
            header[4] = 4; header[5] = 5; header[6] = 9; header[7] = 30
            putLe(header, 8, 0); putLe(header, 12, 0x40) // segment size field: 0x4000000000 (little endian, 8 bytes)
            val body = ByteArray(entries.size * 18)
            var hashHigh = 0
            var hashLow = 0
            for ((n, entry) in entries.withIndex()) {
                val (key, placed) = entry
                val o = n * 18
                System.arraycopy(key, 0, body, o, 9)
                val storage = (placed.segment.toLong() shl 30) or placed.offset.toLong()
                for (i in 0 until 5) body[o + 9 + i] = (storage ushr (8 * (4 - i))).toByte()
                putLe(body, o + 14, placed.size)
                val (c, b) = Jenkins.hashlittle2(body, o, 18, hashHigh, hashLow)
                hashHigh = c
                hashLow = b
            }
            val out = java.io.ByteArrayOutputStream(48 + body.size)
            val guard = ByteArray(8)
            putLe(guard, 0, 16); putLe(guard, 4, Jenkins.hashlittle(header, 0, 16, 0))
            out.write(guard); out.write(header)
            out.write(ByteArray(8)) // padding to 0x20
            putLe(guard, 0, body.size); putLe(guard, 4, hashHigh)
            out.write(guard); out.write(body)
            return out.toByteArray()
        }

        private fun putLe(b: ByteArray, o: Int, v: Int) {
            b[o] = v.toByte(); b[o + 1] = (v ushr 8).toByte(); b[o + 2] = (v ushr 16).toByte(); b[o + 3] = (v ushr 24).toByte()
        }

        private fun compareUnsigned(a: ByteArray, b: ByteArray): Int {
            for (i in a.indices) { val d = (a[i].toInt() and 0xFF) - (b[i].toInt() and 0xFF); if (d != 0) return d }
            return 0
        }
    }
}
