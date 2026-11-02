package com.logie.blizz.importer

import java.io.File
import java.io.InputStream
import java.io.RandomAccessFile

/** A Windows program's header: its machine and the version in its version resource. Plain Kotlin, unit-tested. */
data class PeInfo(val machine: Int, val version: String?) {
    val isX86: Boolean get() = machine == MACHINE_I386
    val isX64: Boolean get() = machine == MACHINE_AMD64
    /** A program Box64 and Wine run: 32- or 64-bit x86. */
    val isWindowsX86Family: Boolean get() = isX86 || isX64

    companion object {
        const val MACHINE_I386 = 0x14c
        const val MACHINE_AMD64 = 0x8664

        /** The header of [file], or null when it isn't a Windows program. */
        fun read(file: File): PeInfo? = runCatching { RandomAccessFile(file, "r").use { read(it) } }.getOrNull()

        private fun read(f: RandomAccessFile): PeInfo? {
            if (f.length() < 0x40) return null
            val mz = ByteArray(2).also { f.readFully(it) }
            if (mz[0] != 'M'.code.toByte() || mz[1] != 'Z'.code.toByte()) return null
            f.seek(0x3c)
            val peOffset = le32(f).toLong()
            if (peOffset <= 0 || peOffset > f.length() - 24) return null
            f.seek(peOffset)
            if (le32(f) != 0x00004550) return null
            val machine = le16(f)
            return PeInfo(machine, fixedFileVersion(f))
        }

        /**
         * The file version from the VS_FIXEDFILEINFO (signature 0xFEEF04BD) that follows the
         * "VS_VERSION_INFO" key, searched for in the file (the resource section is near its end).
         */
        private fun fixedFileVersion(f: RandomAccessFile): String? {
            val key = "VS_VERSION_INFO".toByteArray(Charsets.UTF_16LE)
            val length = f.length()
            val chunk = 1 shl 20
            val buffer = ByteArray(chunk + 256)
            var start = 0L
            while (start < length) {
                f.seek(start)
                val n = f.read(buffer, 0, minOf(buffer.size.toLong(), length - start).toInt())
                if (n <= 0) break
                var i = indexOf(buffer, n, key, 0)
                while (i >= 0) {
                    // VS_FIXEDFILEINFO is 32-bit aligned after the key and its padding.
                    var j = i + key.size
                    while (j + 52 <= n) {
                        if (le32(buffer, j) == 0xFEEF04BD.toInt()) {
                            val ms = le32(buffer, j + 8)
                            val ls = le32(buffer, j + 12)
                            return "${ms ushr 16}.${ms and 0xffff}.${ls ushr 16}.${ls and 0xffff}"
                        }
                        j += 2
                        if (j - i > 128) break
                    }
                    i = indexOf(buffer, n, key, i + 1)
                }
                start += chunk
            }
            return null
        }

        private fun indexOf(haystack: ByteArray, size: Int, needle: ByteArray, from: Int): Int {
            outer@ for (i in from..size - needle.size) {
                for (k in needle.indices) if (haystack[i + k] != needle[k]) continue@outer
                return i
            }
            return -1
        }

        private fun le16(f: RandomAccessFile): Int = f.read() or (f.read() shl 8)
        private fun le32(f: RandomAccessFile): Int = f.read() or (f.read() shl 8) or (f.read() shl 16) or (f.read() shl 24)
        private fun le32(b: ByteArray, i: Int): Int =
            (b[i].toInt() and 0xff) or ((b[i + 1].toInt() and 0xff) shl 8) or ((b[i + 2].toInt() and 0xff) shl 16) or ((b[i + 3].toInt() and 0xff) shl 24)
    }
}

/** Blizzard's archives (MPQ): checks that a file is one. */
object Mpq {
    private val MAGIC = byteArrayOf('M'.code.toByte(), 'P'.code.toByte(), 'Q'.code.toByte(), 0x1A)

    /** An MPQ archive: its header at the start (a data archive). */
    fun isArchive(file: File): Boolean = file.isFile && file.length() >= 32 && file.inputStream().use { startsWithMagic(it) }

    fun startsWithMagic(input: InputStream): Boolean {
        val head = ByteArray(4)
        var read = 0
        while (read < 4) {
            val n = input.read(head, read, 4 - read)
            if (n < 0) return false
            read += n
        }
        return head.contentEquals(MAGIC)
    }

    /**
     * An MPQ archive inside a program (a self-extracting installer like the StarCraft disc's
     * INSTALL.EXE): a header at a 512-byte boundary.
     */
    fun containsArchive(file: File, limit: Long = 64L shl 20): Boolean {
        if (!file.isFile) return false
        RandomAccessFile(file, "r").use { f ->
            val head = ByteArray(4)
            var offset = 0L
            val end = minOf(f.length() - 32, limit)
            while (offset <= end) {
                f.seek(offset)
                f.readFully(head)
                if (head.contentEquals(MAGIC)) return true
                offset += 512
            }
        }
        return false
    }
}

/** What's inside an MPQ archive, from its hash table, without unpacking anything. Plain Kotlin, unit-tested. */
object MpqContents {
    private val crypt = IntArray(0x500).also { table ->
        var seed = 0x00100001L
        for (i in 0 until 0x100) {
            var index = i
            repeat(5) {
                seed = (seed * 125 + 3) % 0x2AAAAB
                val high = (seed and 0xFFFF) shl 16
                seed = (seed * 125 + 3) % 0x2AAAAB
                table[index] = (high or (seed and 0xFFFF)).toInt()
                index += 0x100
            }
        }
    }

    /** The archive's hash of [name] for [type] (0 position, 1 and 2 the name's two checks, 3 the table's key). */
    fun hash(name: String, type: Int): Int {
        var s1 = 0x7FED7FED
        var s2 = 0xEEEEEEEE.toInt()
        for (c in name.uppercase()) {
            val ch = c.code and 0xFF
            s1 = crypt[(type shl 8) + ch] xor (s1 + s2)
            s2 = ch + s1 + s2 + (s2 shl 5) + 3
        }
        return s1
    }

    fun decrypt(data: ByteArray, firstKey: Int) {
        var key = firstKey
        var s2 = 0xEEEEEEEE.toInt()
        var i = 0
        while (i + 3 < data.size) {
            s2 += crypt[0x400 + (key and 0xFF)]
            val v = le32(data, i) xor (key + s2)
            key = ((key.inv() shl 0x15) + 0x11111111) or (key ushr 0x0B)
            s2 = v + s2 + (s2 shl 5) + 3
            put32(data, i, v)
            i += 4
        }
    }

    fun encrypt(data: ByteArray, firstKey: Int) {
        var key = firstKey
        var s2 = 0xEEEEEEEE.toInt()
        var i = 0
        while (i + 3 < data.size) {
            s2 += crypt[0x400 + (key and 0xFF)]
            val plain = le32(data, i)
            val v = plain xor (key + s2)
            key = ((key.inv() shl 0x15) + 0x11111111) or (key ushr 0x0B)
            s2 = plain + s2 + (s2 shl 5) + 3
            put32(data, i, v)
            i += 4
        }
    }

    /**
     * Which of [names] ("font\\font.gid") [file] holds, or null when its header or hash table can't
     * be read (damaged, cut short, or not an MPQ). An archive after a program (a disc's INSTALL.EXE) is found too.
     */
    fun has(file: File, names: List<String>): Map<String, Boolean>? = runCatching {
        RandomAccessFile(file, "r").use { f ->
            var base = -1L
            var offset = 0L
            val magic = ByteArray(4)
            val end = minOf(f.length() - 32, 64L shl 20)
            while (offset <= end) {
                f.seek(offset); f.readFully(magic)
                if (magic[0] == 'M'.code.toByte() && magic[1] == 'P'.code.toByte() && magic[2] == 'Q'.code.toByte() && magic[3] == 0x1A.toByte()) { base = offset; break }
                offset += 512
            }
            if (base < 0) return@use null
            val header = ByteArray(32)
            f.seek(base); f.readFully(header)
            val hashPos = le32(header, 16).toLong() and 0xffffffffL
            val hashCount = le32(header, 24)
            if (hashCount <= 0 || hashCount > (1 shl 22) || hashCount and (hashCount - 1) != 0) return@use null
            if (base + hashPos + hashCount * 16L > f.length()) return@use null
            val table = ByteArray(hashCount * 16)
            f.seek(base + hashPos); f.readFully(table)
            decrypt(table, hash("(hash table)", 3))
            names.associateWith { name ->
                val a = hash(name, 1)
                val b = hash(name, 2)
                (0 until hashCount).any { i ->
                    val block = le32(table, i * 16 + 12)
                    le32(table, i * 16) == a && le32(table, i * 16 + 4) == b && block != -1 && block != -2
                }
            }
        }
    }.getOrNull()

    private fun le32(b: ByteArray, i: Int): Int =
        (b[i].toInt() and 0xff) or ((b[i + 1].toInt() and 0xff) shl 8) or ((b[i + 2].toInt() and 0xff) shl 16) or ((b[i + 3].toInt() and 0xff) shl 24)

    private fun put32(b: ByteArray, i: Int, v: Int) {
        b[i] = v.toByte(); b[i + 1] = (v ushr 8).toByte(); b[i + 2] = (v ushr 16).toByte(); b[i + 3] = (v ushr 24).toByte()
    }
}

/** Checks of an installed game's files. */
object FileValidator {
    /** [name] in [dir], whatever its case (Windows games don't care, Android's storage does). */
    fun find(dir: File, name: String): File? {
        val exact = File(dir, name)
        if (exact.exists()) return exact
        return dir.listFiles()?.firstOrNull { it.name.equals(name, ignoreCase = true) }
    }

    fun requireFiles(dir: File, names: List<String>, label: (String) -> String = { it }): List<Check> =
        names.map { name ->
            val f = find(dir, name)
            Check(label(name), f != null && f.isFile && f.length() > 0, if (f == null) "missing" else "${f.length()} bytes")
        }

    fun requireArchives(dir: File, names: List<String>): List<Check> =
        names.map { name ->
            val f = find(dir, name)
            val ok = f != null && Mpq.isArchive(f)
            Check(name, ok, when {
                f == null -> "missing"
                !ok -> "not an MPQ archive (damaged or not the game's)"
                else -> "${f.length()} bytes"
            })
        }

    /** Free space where [dir] is, against [needed] bytes, with a margin. */
    fun requireSpace(dir: File, needed: Long) {
        var probe: File? = dir
        while (probe != null && !probe.exists()) probe = probe.parentFile
        val free = probe?.usableSpace ?: return
        if (free < needed + (200L shl 20)) {
            throw ImportException(
                Problem.INSUFFICIENT_STORAGE,
                "Not enough free space: about ${gb(needed)} is needed and ${gb(free)} is free. Free some space and retry.",
            )
        }
    }

    fun gb(bytes: Long): String = if (bytes >= (1L shl 30)) "%.1f GB".format(bytes / (1L shl 30).toDouble()) else "${bytes shr 20} MB"
}
