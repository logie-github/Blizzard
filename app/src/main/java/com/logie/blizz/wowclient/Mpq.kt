// SPDX-License-Identifier: GPL-3.0-or-later

package com.logie.blizz.wowclient

import org.apache.commons.compress.compressors.bzip2.BZip2CompressorInputStream
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.RandomAccessFile
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.zip.Deflater
import java.util.zip.Inflater

/**
 * The World of Warcraft 3.3.5a client's archives (MPQ), read and written: a port, line for line, of the World of Warcraft app's
 * `SkyborneFiles.cpp` (`MpqArchive`, `FolderArchive`, `Game`, `MpqWriter`), which makes the client patches of its modules.
 * Plain Kotlin, unit-tested; the tests' archives are also read by that C++ reader.
 */
object Mpq {
    /** The tables' encryption, hashing and the hash of a name, as the format defines them. */
    private val CRYPT: IntArray by lazy {
        val table = IntArray(0x500)
        var seed = 0x00100001
        for (i in 0 until 0x100) {
            var index = i
            for (j in 0 until 5) {
                seed = (seed * 125 + 3) % 0x2AAAAB
                val high = (seed and 0xFFFF) shl 16
                seed = (seed * 125 + 3) % 0x2AAAAB
                table[index] = high or (seed and 0xFFFF)
                index += 0x100
            }
        }
        table
    }

    fun hash(text: String, type: Int): Int {
        var seed1 = 0x7FED7FED
        var seed2 = 0xEEEEEEEE.toInt()
        for (c in text) {
            val ch = (if (c == '/') '\\' else c).uppercaseChar().code and 0xFF
            seed1 = CRYPT[type * 0x100 + ch] xor (seed1 + seed2)
            seed2 = ch + seed1 + seed2 + (seed2 shl 5) + 3
        }
        return seed1
    }

    /** Encrypts or decrypts [count] words of [data] in place with [key]. */
    fun crypt(data: IntArray, count: Int, key: Int, encrypt: Boolean) {
        var k = key
        var seed = 0xEEEEEEEE.toInt()
        for (i in 0 until count) {
            seed += CRYPT[0x400 + (k and 0xFF)]
            val input = data[i]
            val output = input xor (k + seed)
            k = ((k.inv() shl 0x15) + 0x11111111) or (k ushr 0x0B)
            seed = (if (encrypt) input else output) + seed + (seed shl 5) + 3
            data[i] = output
        }
    }

    private fun decryptBytes(data: ByteArray, from: Int, length: Int, key: Int) {
        val words = length / 4
        val buffer = ByteBuffer.wrap(data, from, words * 4).order(ByteOrder.LITTLE_ENDIAN)
        val w = IntArray(words) { buffer.getInt() }
        crypt(w, words, key, false)
        val out = ByteBuffer.wrap(data, from, words * 4).order(ByteOrder.LITTLE_ENDIAN)
        for (x in w) out.putInt(x)
    }

    private fun inflate(input: ByteArray, from: Int, length: Int, size: Int): ByteArray? {
        val inflater = Inflater()
        return try {
            inflater.setInput(input, from, length)
            val out = ByteArray(size)
            var got = 0
            while (got < size && !inflater.finished()) {
                val n = inflater.inflate(out, got, size - got)
                if (n == 0 && (inflater.needsInput() || inflater.needsDictionary())) break
                got += n
            }
            if (got == size) out else null
        } catch (e: java.util.zip.DataFormatException) {
            null
        } finally {
            inflater.end()
        }
    }

    /** A sector or file stored compressed: its first byte says how (2: zlib, 0x10: bzip2); anything else isn't read. */
    private fun unpack(input: ByteArray, from: Int, length: Int, size: Int): ByteArray? {
        if (length == 0) return null
        return when (input[from].toInt() and 0xFF) {
            0x02 -> inflate(input, from + 1, length - 1, size)
            0x10 -> runCatching {
                val out = ByteArray(size)
                BZip2CompressorInputStream(ByteArrayInputStream(input, from + 1, length - 1)).use { s ->
                    var got = 0
                    while (got < size) { val n = s.read(out, got, size - got); if (n < 0) break; got += n }
                    if (got == size) out else null
                }
            }.getOrNull()
            else -> null
        }
    }

    /** One of the game's archives: an MPQ file, or a folder of the game's paths. */
    interface Archive {
        val path: File
        /** The file at [name] (the game's path, either slash, any case), or null. */
        fun read(name: String): ByteArray?
        fun has(name: String): Boolean
        fun close() {}
    }

    private fun u32(b: ByteArray, at: Int): Long = ByteBuffer.wrap(b, at, 4).order(ByteOrder.LITTLE_ENDIAN).getInt().toLong() and 0xFFFFFFFFL
    private fun u16(b: ByteArray, at: Int): Int = ByteBuffer.wrap(b, at, 2).order(ByteOrder.LITTLE_ENDIAN).getShort().toInt() and 0xFFFF

    private fun gamePath(text: String) = text.replace('/', '\\').lowercase()

    /** An MPQ file, opened for reading. */
    class File_(override val path: File) : Archive {
        private val input: RandomAccessFile? = runCatching { RandomAccessFile(path, "r") }.getOrNull()
        private var base = 0L
        private var sector = 4096
        private var hashes = IntArray(0)
        private var blocks = IntArray(0)
        private var hiBlocks = ShortArray(0)

        init {
            runCatching { open() }.onFailure { hashes = IntArray(0) }
        }

        private fun readAt(at: Long, length: Int): ByteArray? {
            val file = input ?: return null
            val out = ByteArray(length)
            return runCatching { file.seek(at); file.readFully(out); out }.getOrNull()
        }

        private fun words(bytes: ByteArray): IntArray {
            val buffer = ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN)
            return IntArray(bytes.size / 4) { buffer.getInt() }
        }

        private fun open() {
            val file = input ?: return
            // The header is at the start, or 512 bytes on at a time (after data before it).
            var h = ByteArray(32)
            var at = 0L
            var found = false
            while (at < (1 shl 20)) {
                h = readAt(at, 32) ?: return
                if (h[0] == 'M'.code.toByte() && h[1] == 'P'.code.toByte() && h[2] == 'Q'.code.toByte() && h[3] == 0x1A.toByte()) { base = at; found = true; break }
                if (h[0] == 'M'.code.toByte() && h[1] == 'P'.code.toByte() && h[2] == 'Q'.code.toByte() && h[3] == 0x1B.toByte()) { at = u32(h, 8) - 0x200 }
                at += 0x200
            }
            if (!found) return
            val version = u16(h, 12)
            sector = 512 shl u16(h, 14)
            var hashPos = u32(h, 16)
            var blockPos = u32(h, 20)
            val hashCount = u32(h, 24).toInt()
            val blockCount = u32(h, 28).toInt()
            var hiBlockPos = 0L
            if (version >= 1) {
                val extra = readAt(base + 32, 12) ?: return
                hiBlockPos = u32(extra, 0) or (u32(extra, 4) shl 32)
                hashPos = hashPos or (u16(extra, 8).toLong() shl 32)
                blockPos = blockPos or (u16(extra, 10).toLong() shl 32)
            }
            val hashBytes = readAt(base + hashPos, hashCount * 16) ?: return
            val blockBytes = readAt(base + blockPos, blockCount * 16) ?: return
            hashes = words(hashBytes)
            blocks = words(blockBytes)
            crypt(hashes, hashes.size, hash("(hash table)", 3), false)
            crypt(blocks, blocks.size, hash("(block table)", 3), false)
            if (hiBlockPos != 0L) {
                val hi = readAt(base + hiBlockPos, blockCount * 2)
                if (hi != null) {
                    val buffer = ByteBuffer.wrap(hi).order(ByteOrder.LITTLE_ENDIAN)
                    hiBlocks = ShortArray(blockCount) { buffer.getShort() }
                }
            }
            if (file.length() < 0) hashes = IntArray(0)
        }

        /** The block of the file at [name], or -1. */
        private fun block(name: String): Int {
            if (hashes.isEmpty()) return -1
            val count = hashes.size / 4
            val start = Integer.remainderUnsigned(hash(name, 0), count)
            val a = hash(name, 1)
            val b = hash(name, 2)
            var block = -1
            for (i in 0 until count) {
                val e = ((start + i) % count) * 4
                if (hashes[e + 3] == -1) break
                if (hashes[e] == a && hashes[e + 1] == b && Integer.compareUnsigned(hashes[e + 3], blocks.size / 4) < 0) {
                    block = hashes[e + 3]
                    if ((hashes[e + 2] and 0xFFFF) == 0) break   // the neutral locale's, if there are several
                }
            }
            return block
        }

        override fun has(name: String): Boolean {
            val block = block(name)
            if (block < 0) return false
            val flags = blocks[block * 4 + 3]
            return (flags and 0x80000000.toInt()) != 0 && (flags and 0x02000000) == 0
        }

        override fun read(name: String): ByteArray? {
            val block = block(name)
            if (block < 0) return null
            val bl = block * 4
            val offset = (blocks[bl].toLong() and 0xFFFFFFFFL) or (if (hiBlocks.isEmpty()) 0L else (hiBlocks[block].toLong() and 0xFFFF) shl 32)
            val stored = blocks[bl + 1]
            val size = blocks[bl + 2]
            val flags = blocks[bl + 3]
            if ((flags and 0x80000000.toInt()) == 0 || (flags and 0x02000000) != 0 || (flags and 0x100) != 0) return null   // gone, deleted, or imploded (older archives)
            if (stored < 0 || size < 0) return null
            val raw = readAt(base + offset, stored) ?: return null
            var key = 0
            if ((flags and 0x10000) != 0) {
                val base = name.substringAfterLast('\\').substringAfterLast('/')
                key = hash(base, 3)
                if ((flags and 0x20000) != 0) key = (key + offset.toInt()) xor size
            }
            if ((flags and 0x01000000) != 0) {        // one unit
                if ((flags and 0x10000) != 0) decryptBytes(raw, 0, raw.size, key)
                if ((flags and 0x200) != 0 && stored < size) return unpack(raw, 0, raw.size, size)
                return if (raw.size >= size) raw.copyOf(size) else null
            }
            if ((flags and 0x200) == 0) {
                if ((flags and 0x10000) != 0) {
                    var s = 0
                    while (s.toLong() * sector < size) {
                        decryptBytes(raw, s * sector, minOf(sector, size - s * sector), key + s)
                        s++
                    }
                }
                return if (raw.size >= size) raw.copyOf(size) else null
            }
            val sectors = (size + sector - 1) / sector
            val tableSize = (sectors + 1) * 4
            if (raw.size < tableSize) return null
            if ((flags and 0x10000) != 0) decryptBytes(raw, 0, tableSize, key - 1)
            val out = ByteArrayOutputStream(size)
            for (s in 0 until sectors) {
                val from = u32(raw, s * 4).toInt()
                val to = u32(raw, s * 4 + 4).toInt()
                if (to < from || to > raw.size) return null
                val want = minOf(sector, size - s * sector)
                if ((flags and 0x10000) != 0) decryptBytes(raw, from, to - from, key + s)
                if (to - from < want) {
                    val part = unpack(raw, from, to - from, want) ?: return null
                    out.write(part)
                } else out.write(raw, from, want)
            }
            return if (out.size() == size) out.toByteArray() else null
        }

        override fun close() { runCatching { input?.close() } }
    }

    /** A folder the game reads like an archive (`Data/patch-M.MPQ` of the realm's modules is one). */
    class Folder(override val path: File) : Archive {
        private val files = HashMap<String, File>()

        init {
            path.walkTopDown().filter { it.isFile }.forEach { files[gamePath(it.relativeTo(path).path)] = it }
        }

        override fun has(name: String) = gamePath(name) in files
        override fun read(name: String): ByteArray? = files[gamePath(name)]?.let { runCatching { it.readBytes() }.getOrNull() }
    }

    fun open(path: File): Archive = if (path.isDirectory) Folder(path) else File_(path)

    /**
     * The client's archives in the order the game reads them (a later one's file wins): the game's own, its language's, and the
     * patches after them (patch-4.MPQ to patch-Z.MPQ, files or folders). [skip]: names (lower case) left out.
     */
    class Game(data: File, skip: Collection<String> = emptyList()) {
        val locale: String
        val archives: List<Archive>

        init {
            fun entries(folder: File): Map<String, File> = folder.listFiles()?.associateBy { it.name.lowercase() } ?: emptyMap()
            val top = entries(data)
            var found = ""
            for ((name, entry) in top) if (name.length == 4 && entry.isDirectory && entries(entry).containsKey("locale-$name.mpq")) { found = entry.name; break }
            locale = found
            val local = if (locale.isEmpty()) emptyMap() else entries(File(data, locale))
            val loc = locale.lowercase()
            val order = ArrayList<File>()
            fun add(from: Map<String, File>, name: String) {
                val key = name.lowercase()
                if (key in skip) return
                from[key]?.let { order += it }
            }
            for (name in listOf("common.MPQ", "common-2.MPQ", "expansion.MPQ", "lichking.MPQ")) add(top, name)
            if (loc.isNotEmpty()) for (name in listOf("locale-", "expansion-locale-", "lichking-locale-")) add(local, "$name$loc.mpq")
            val suffixes = ArrayList<String>().apply {
                addAll(listOf("", "-2", "-3"))
                for (c in '4'..'9') add("-$c")
                for (c in 'a'..'z') add("-$c")
            }
            for (s in suffixes) {
                add(top, "patch$s.mpq")
                if (loc.isNotEmpty()) add(local, "patch-$loc$s.mpq")
            }
            archives = order.map { open(it) }
        }

        fun read(name: String): ByteArray? {
            for (a in archives.asReversed()) a.read(name)?.let { return it }
            return null
        }

        fun has(name: String) = archives.any { it.has(name) }

        /** The archive the game reads [name] from (the last that has it), or null. */
        fun owner(name: String): File? = archives.lastOrNull { it.has(name) }?.path

        fun close() = archives.forEach { it.close() }
    }

    /** Writes an MPQ file of the format the 3.3.5a client reads, a file at a time: sectors of 4096 bytes, each deflated where that is smaller. */
    class Writer(private val path: File) {
        private val out = RandomAccessFile(path, "rw").also { it.setLength(0); it.write(ByteArray(32)) }
        private val blocks = ArrayList<Pair<String, IntArray>>()
        private val same = ArrayList<Pair<String, Int>>()
        private var pos = 32L
        private var ok = true

        fun add(name: String, data: ByteArray): Boolean {
            val sector = 4096
            val sectors = maxOf(1, (data.size + sector - 1) / sector)
            val stored = ByteArrayOutputStream()
            stored.write(ByteArray((sectors + 1) * 4))
            val offsets = ArrayList<Int>()
            offsets += stored.size()
            for (i in 0 until sectors) {
                val from = i * sector
                val length = minOf(sector, data.size - from)
                var done = false
                if (length > 0) {
                    val deflater = Deflater(6)
                    deflater.setInput(data, from, length)
                    deflater.finish()
                    val buffer = ByteArray(length + 64)
                    val n = deflater.deflate(buffer)
                    val finished = deflater.finished()
                    deflater.end()
                    if (finished && n + 1 < length) {
                        stored.write(0x02)
                        stored.write(buffer, 0, n)
                        done = true
                    }
                }
                if (!done) stored.write(data, from, length)
                offsets += stored.size()
            }
            val bytes = stored.toByteArray()
            val table = ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN)
            for ((i, o) in offsets.withIndex()) table.putInt(i * 4, o)
            blocks += name to intArrayOf(pos.toInt(), bytes.size, data.size, 0x80000000.toInt() or 0x200)
            out.seek(pos)
            out.write(bytes)
            pos += bytes.size
            ok = ok && pos < 0xF0000000L
            return ok
        }

        /** Another name for a file already added (its bytes stored once): false if there's none of [existing]. */
        fun addSame(name: String, existing: String): Boolean {
            val i = blocks.indexOfFirst { it.first == existing }
            if (i < 0) return false
            same += name to i
            return true
        }

        fun finish(): Boolean {
            var hashSize = 16
            while (hashSize < (blocks.size + same.size) * 2) hashSize *= 2
            val hashes = IntArray(hashSize * 4) { -1 }
            val blockWords = ArrayList<Int>()
            fun put(name: String, block: Int) {
                var index = hash(name, 0) and (hashSize - 1)
                while (hashes[index * 4 + 3] != -1) index = (index + 1) and (hashSize - 1)
                hashes[index * 4] = hash(name, 1)
                hashes[index * 4 + 1] = hash(name, 2)
                hashes[index * 4 + 2] = 0
                hashes[index * 4 + 3] = block
            }
            for ((i, b) in blocks.withIndex()) {
                put(b.first, i)
                b.second.forEach { blockWords += it }
            }
            for ((name, block) in same) put(name, block)
            val blockArray = blockWords.toIntArray()
            crypt(hashes, hashes.size, hash("(hash table)", 3), true)
            crypt(blockArray, blockArray.size, hash("(block table)", 3), true)
            fun bytes(w: IntArray): ByteArray {
                val b = ByteBuffer.allocate(w.size * 4).order(ByteOrder.LITTLE_ENDIAN)
                w.forEach { b.putInt(it) }
                return b.array()
            }
            val hashPos = pos
            out.seek(pos)
            out.write(bytes(hashes))
            val blockPos = pos + hashes.size * 4
            out.write(bytes(blockArray))
            val total = blockPos + blockArray.size * 4
            val h = ByteBuffer.allocate(32).order(ByteOrder.LITTLE_ENDIAN)
            h.put('M'.code.toByte()).put('P'.code.toByte()).put('Q'.code.toByte()).put(0x1A)
            h.putInt(32).putInt(total.toInt()).putShort(0).putShort(3)   // sectors of 4096 bytes
            h.putInt(hashPos.toInt()).putInt(blockPos.toInt()).putInt(hashSize).putInt(blocks.size)
            out.seek(0)
            out.write(h.array())
            out.close()
            return ok
        }
    }
}
