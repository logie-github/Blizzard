package com.logie.blizz.wow

import java.io.File
import java.io.RandomAccessFile

/** The servers' console output, readable: AzerothCore colours its lines with ANSI escape codes. */
object ConsoleText {
    private val ESCAPES = Regex("\u001B\\[[0-9;?]*[A-Za-z]")
    fun plain(text: String): String = ESCAPES.replace(text, "")
}

/**
 * Looks for a line in a log that's still being written, fed each piece of it as it's read: every
 * line is looked at however many come at once, including a line that arrives in two pieces
 * (the WoW app's own `LineWatch`).
 */
class LineWatch(private val pattern: Regex) {
    private var partial = ""
    var found = false
        private set

    fun feed(text: String): Boolean {
        if (found || text.isEmpty()) return found
        val all = partial + text
        val end = all.lastIndexOf('\n')
        val lines = if (end >= 0) all.substring(0, end) else ""
        partial = all.substring(end + 1).takeLast(MAX_PARTIAL)
        found = ConsoleText.plain(lines).lineSequence().any { pattern.containsMatchIn(it) } ||
            pattern.containsMatchIn(ConsoleText.plain(partial))
        return found
    }

    private companion object {
        const val MAX_PARTIAL = 4096
    }
}

/** Reading the servers' log files. */
object WowLogs {
    /** The last [lines] lines of a log without colour codes, or "" if there is none. */
    /**
     * A program's exit code in words, for a report: above 128 a shell's way of saying the program was ended by a signal
     * (128 + its number), which comes from outside it (the system, another program), with no error of its own in its
     * log. (Report #113: Wrath++'s world server, code 163, signal 35, its log ending in the bots' statistics.)
     */
    fun exitInWords(code: Int): String {
        if (code in 129..192) {
            val signal = code - 128
            val name = when (signal) {
                1 -> "SIGHUP"; 2 -> "SIGINT"; 3 -> "SIGQUIT"; 4 -> "SIGILL"; 6 -> "SIGABRT"; 7 -> "SIGBUS"; 8 -> "SIGFPE"
                9 -> "SIGKILL, the system's (often for memory)"; 11 -> "SIGSEGV, a crash"; 13 -> "SIGPIPE"; 15 -> "SIGTERM"
                35 -> "35, the one Android's debuggerd sends for a stack dump"
                else -> "$signal"
            }
            return "code $code: ended by signal $name"
        }
        return "code $code"
    }

    fun tail(file: File, lines: Int = 40): String {
        if (!file.isFile) return ""
        val start = (file.length() - 64 * 1024).coerceAtLeast(0)
        val text = file.inputStream().use { input ->
            input.skip(start)
            input.readBytes().toString(Charsets.UTF_8)
        }
        return ConsoleText.plain(text).lines().dropLastWhile { it.isBlank() }.takeLast(lines).joinToString("\n")
    }

    /** What a log that's being written has gained since byte [from], and the byte it ends at (a log started anew is read from its start). */
    fun readFrom(file: File, from: Long, max: Int = 1 shl 20): Pair<String, Long> {
        if (!file.isFile) return "" to 0L
        val length = file.length()
        val start = if (length < from) 0L else from
        if (length == start) return "" to start
        val bytes = ByteArray(minOf(max.toLong(), length - start).toInt())
        val read = RandomAccessFile(file, "r").use { input ->
            input.seek(start)
            input.read(bytes)
        }
        if (read <= 0) return "" to start
        return String(bytes, 0, read, Charsets.UTF_8) to start + read
    }
}
