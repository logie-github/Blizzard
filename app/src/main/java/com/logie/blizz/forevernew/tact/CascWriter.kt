package com.logie.blizz.forevernew.tact

import java.io.File
import java.io.IOException
import java.io.RandomAccessFile
import java.nio.ByteBuffer
import java.nio.ByteOrder

/**
 * Writes Blizzard's local storage (`Data/data/data.NNN` and `NNNNNNNNNN.idx`), the format the game and CascLib read, as the
 * layout CascLib reads it (CascIndexFiles.cpp, CascReadFile.cpp). Each stored file is a 30-byte local header (the key reversed, the
 * size, a Jenkins hash and a checksum that depends on where it sits) and the BLTE bytes exactly as the CDN has them; the index
 * says in which data file, at which offset, how big, per 9-byte key prefix, in 16 buckets.
 * Resumable: [open] reads back what an earlier run wrote (the index files and the data files' lengths).
 */
class CascWriter(private val dataDir: File, private val segmentSize: Long = 1L shl 30) {
    /** What is stored, in primitive arrays (a million entries as objects and hex strings would not fit a phone's memory). */
    private var n = 0
    private var key9s = ByteArray(9 * 1024)
    private var segs = IntArray(1024)
    private var offs = LongArray(1024)
    private var lens = IntArray(1024)
    private val index = LongIntMap(1024)

    private fun find(key9: ByteArray): Int {
        val j = index[key9.prefix64()]
        if (j < 0) return -1
        for (k in 0 until 9) if (key9s[j * 9 + k] != key9[k]) return -1
        return j
    }

    private fun put(key9: ByteArray, segment: Int, offset: Long, size: Int) {
        val at = find(key9).takeIf { it >= 0 } ?: run {
            if (n == segs.size) { key9s = key9s.copyOf(key9s.size * 2); segs = segs.copyOf(n * 2); offs = offs.copyOf(n * 2); lens = lens.copyOf(n * 2) }
            System.arraycopy(key9, 0, key9s, n * 9, 9); index[key9.prefix64()] = n
            n.also { n++ }
        }
        segs[at] = segment; offs[at] = offset; lens[at] = size
    }
    private var segment = 0
    private var raf: RandomAccessFile? = null
    private var indexVersion = 1

    init { dataDir.mkdirs(); load() }

    /** Reads back the entries of the newest index files an earlier run wrote, so an interrupted install carries on. */
    private fun load() {
        val newest = dataDir.listFiles { f -> f.name.endsWith(".idx") && f.name.length == 14 }.orEmpty()
            .groupBy { it.name.substring(0, 2) }.mapValues { (_, v) -> v.maxByOrNull { it.name }!! }
        for ((_, f) in newest) {
            val d = f.readBytes()
            if (d.size < 40) continue
            val bb = ByteBuffer.wrap(d).order(ByteOrder.LITTLE_ENDIAN)
            val size = bb.getInt(32)
            if (size < 0 || 40 + size > d.size) continue
            for (i in 0 until size / ENTRY) {
                val p = 40 + i * ENTRY
                val key9 = d.copyOfRange(p, p + 9)
                var off = 0L; for (k in 0 until 5) off = (off shl 8) or (d[p + 9 + k].toLong() and 0xff)
                val len = ((d[p + 14].toInt() and 0xff) shl 24) or ((d[p + 15].toInt() and 0xff) shl 16) or ((d[p + 16].toInt() and 0xff) shl 8) or (d[p + 17].toInt() and 0xff)
                put(key9, (off shr 30).toInt(), off and ((1L shl 30) - 1), len)
                if ((off shr 30).toInt() > segment) segment = (off shr 30).toInt()
            }
        }
    }

    fun has(ekey: ByteArray) = find(ekey.copyOf(9)) >= 0
    val count get() = n

    private fun segmentFile(n: Int) = File(dataDir, "data.%03d".format(n))

    /** The data file with room for [needed] more bytes (a file never straddles two data files). */
    private fun current(needed: Long): RandomAccessFile {
        raf?.let { if (it.length() + needed <= segmentSize) return it; it.close(); segment++; raf = null }
        if (raf == null && segmentFile(segment).length() + needed > segmentSize && segmentFile(segment).length() > 0) segment++
        return RandomAccessFile(segmentFile(segment), "rw").also { it.seek(it.length()); raf = it }
    }

    /** The BLTE bytes stored for [ekey] (what [add] was given), or null. */
    @Synchronized fun read(ekey: ByteArray): ByteArray? {
        val j = find(ekey.copyOf(9)).takeIf { it >= 0 } ?: return null
        raf?.let { if (segs[j] == segment) it.fd.sync() }
        RandomAccessFile(segmentFile(segs[j]), "r").use { f ->
            f.seek(offs[j] + HEADER)
            return ByteArray(lens[j] - HEADER).also { f.readFully(it) }
        }
    }

    /** Adds one file: [blte] is the file as the CDN stores it (it starts with "BLTE"). */
    @Synchronized fun add(ekey: ByteArray, blte: ByteArray) {
        require(ekey.size == 16) { "an encoding key has 16 bytes" }
        if (has(ekey)) return
        val f = current((HEADER + blte.size).toLong())
        val offset = f.length()
        val total = HEADER + blte.size
        f.seek(offset)
        f.write(localHeader(ekey, total, offset))
        f.write(blte)
        put(ekey.copyOf(9), segment, offset, total)
    }

    /**
     * Adds a file too large to hold whole ([size] bytes of BLTE read by [read] in pieces): the header first, then the pieces.
     */
    @Synchronized fun addStreamed(ekey: ByteArray, size: Long, read: (Long, Int) -> ByteArray) {
        require(ekey.size == 16)
        if (has(ekey)) return
        val f = current(HEADER + size)
        val offset = f.length()
        val total = (HEADER + size).toInt()
        f.seek(offset)
        f.write(localHeader(ekey, total, offset))
        var done = 0L
        while (done < size) { val n = minOf(8L shl 20, size - done).toInt(); f.write(read(done, n)); done += n }
        put(ekey.copyOf(9), segment, offset, total)
    }

    /** Writes the 16 index files (a new version of each, the older ones removed) and closes the data file. */
    @Synchronized fun finish() {
        raf?.close(); raf = null
        val old = dataDir.listFiles { f -> f.name.endsWith(".idx") }.orEmpty()
        val version = (old.maxOfOrNull { it.name.substring(2, 10).toLongOrNull(16) ?: 0L } ?: 0L).toInt() + 1
        val buckets = Array(16) { ArrayList<Int>() }
        for (j in 0 until n) buckets[bucket(key9s.copyOfRange(j * 9, j * 9 + 9))].add(j)
        for (b in 0 until 16) {
            val list = buckets[b].sortedWith { x, y -> compareRange(key9s, x * 9, y * 9) }
            val tmp = File(dataDir, "%02x%08x.idx.tmp".format(b, version))
            tmp.writeBytes(indexFile(b, list))
            if (!tmp.renameTo(File(dataDir, "%02x%08x.idx".format(b, version)))) throw IOException("an index file couldn't be saved")
        }
        old.forEach { it.delete() }
        indexVersion = version
    }

    private fun compareRange(a: ByteArray, x: Int, y: Int): Int { for (k in 0 until 9) { val d = (a[x + k].toInt() and 0xff) - (a[y + k].toInt() and 0xff); if (d != 0) return d }; return 0 }

    private fun indexFile(bucket: Int, list: List<Int>): ByteArray {
        val header = ByteBuffer.allocate(16).order(ByteOrder.LITTLE_ENDIAN)
        header.putShort(7).put(bucket.toByte()).put(0).put(4).put(5).put(9).put(30).putLong(segmentSize)
        val body = ByteArray(list.size * ENTRY)
        for ((i, j) in list.withIndex()) {
            val p = i * ENTRY
            System.arraycopy(key9s, j * 9, body, p, 9)
            val off = (segs[j].toLong() shl 30) or offs[j]
            for (k in 0 until 5) body[p + 9 + k] = (off shr (8 * (4 - k))).toByte()
            for (k in 0 until 4) body[p + 14 + k] = (lens[j] shr (8 * (3 - k))).toByte()
        }
        // the entries' hash is Blizzard's: hashlittle2 over each entry in turn, the first result chained through
        var hi = 0; var lo = 0
        for (i in list.indices) { val (c, b) = Jenkins.hashlittle2(body, i * ENTRY, ENTRY, hi, lo); hi = c; lo = b }
        val out = ByteBuffer.allocate(8 + 16 + 8 + 8 + body.size).order(ByteOrder.LITTLE_ENDIAN)
        out.putInt(16).putInt(Jenkins.hashlittle(header.array(), 0, 16, 0)).put(header.array())
        out.put(ByteArray(8))
        out.putInt(body.size).putInt(hi).put(body)
        return out.array().copyOf(out.position())
    }

    companion object {
        const val HEADER = 30
        const val ENTRY = 18
        // Blizzard's table (CascLib's table_16C57A8, from Agent.exe)
        private val TABLE = longArrayOf(
            0x049396B8, 0x72A82A9B, 0xEE626CCA, 0x9917754F, 0x15DE40B1, 0xF5A8A9B6, 0x421EAC7E, 0xA9D55C9A,
            0x317FD40C, 0x04FAF80D, 0x3D6BE971, 0x52933CFD, 0x27F64B7D, 0xC6F5C11B, 0xD5757E3A, 0x6C388745,
        ).map { it.toInt() }.toIntArray()

        fun bucket(key9: ByteArray): Int { var x = 0; for (i in 0 until 9) x = x xor (key9[i].toInt() and 0xff); return (x and 0xf) xor (x shr 4) }

        fun compareUnsigned(a: ByteArray, b: ByteArray): Int {
            for (i in 0 until minOf(a.size, b.size)) { val d = (a[i].toInt() and 0xff) - (b[i].toInt() and 0xff); if (d != 0) return d }
            return a.size - b.size
        }

        /** The 30 bytes before each file in a data file: [ekey] reversed, the size (header included), flags, a hash, a position-dependent checksum. */
        fun localHeader(ekey: ByteArray, totalSize: Int, offset: Long): ByteArray {
            val h = ByteArray(HEADER)
            for (i in 0 until 16) h[i] = ekey[15 - i]
            for (k in 0 until 4) h[16 + k] = (totalSize shr (8 * k)).toByte()
            // 20, 21: flags (zero)
            val j = Jenkins.hashlittle(h, 0, 22, 0x3D6BE971)
            for (k in 0 until 4) h[22 + k] = (j shr (8 * k)).toByte()
            var enc = (offset + HEADER).toInt()
            enc = TABLE[enc and 0xf] xor enc
            val encoded = ByteArray(4) { (enc shr (8 * it)).toByte() }
            val hashed = ByteArray(4)
            for (i in 0 until 26) hashed[i and 3] = (hashed[i and 3].toInt() xor h[i].toInt()).toByte()
            for (jx in 0 until 4) { val i = 26 + jx; h[26 + jx] = (hashed[i and 3].toInt() xor encoded[i and 3].toInt()).toByte() }
            return h
        }
    }
}
