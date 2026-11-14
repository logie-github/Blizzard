package com.logie.blizz.forever

import java.io.File
import java.io.RandomAccessFile

/**
 * Looks for a pattern in a log that is still being written, without ever holding the log in memory. The world server's
 * log grows to about 150 MB in one start; reading it whole every second asked Android for a 268 MB allocation and ended
 * the app (report #143, 14 November 2026). Each [found] call reads only what was added since the last one, in pieces of
 * [chunk] bytes, and keeps the last [overlap] bytes so a line cut between two reads is still matched. A log that became
 * shorter (it was started again) is read from its start.
 */
class LogScan(
    private val file: File,
    private val pattern: Regex,
    private val chunk: Int = 1 shl 20,
    private val overlap: Int = 512,
) {
    private var offset = 0L
    private var carry = ""

    /** Whether the pattern occurs in what the log holds so far. */
    fun found(): Boolean = runCatching {
        if (!file.isFile) return false
        RandomAccessFile(file, "r").use { f ->
            val length = f.length()
            if (length < offset) { offset = 0; carry = "" }
            val buffer = ByteArray(chunk)
            while (offset < length) {
                val want = minOf(chunk.toLong(), length - offset).toInt()
                f.seek(offset)
                f.readFully(buffer, 0, want)
                offset += want
                // (ISO-8859-1: one char a byte, so the cut between two reads never splits a character)
                val text = carry + String(buffer, 0, want, Charsets.ISO_8859_1)
                if (pattern.containsMatchIn(text)) return true
                carry = text.takeLast(overlap)
            }
        }
        false
    }.getOrDefault(false)

    companion object {
        /**
         * Cuts [file] down to its last [keep] bytes (from a line's start) when it is larger than [limit]. Logs the realm
         * appends to (DBErrors.log, Server.log) otherwise grow with every start.
         */
        fun trim(file: File, limit: Long = 8L shl 20, keep: Long = 1L shl 20): Boolean = runCatching {
            if (!file.isFile || file.length() <= limit) return false
            val tail = RandomAccessFile(file, "r").use { f ->
                f.seek(file.length() - keep)
                ByteArray(keep.toInt()).also { f.readFully(it) }
            }
            val start = tail.indexOf('\n'.code.toByte()).let { if (it < 0) 0 else it + 1 }
            file.outputStream().use { it.write(tail, start, tail.size - start) }
            true
        }.getOrDefault(false)
    }
}
