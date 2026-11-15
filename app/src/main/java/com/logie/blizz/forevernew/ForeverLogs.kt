package com.logie.blizz.forevernew

import java.io.File

/** Forever's own event log (`logs/forever-events.log`): one line per stage change or failure, bounded in size; secrets are never written. */
class ForeverLogs(private val file: File, private val maxBytes: Long = 512 * 1024, private val clock: () -> Long = System::currentTimeMillis) {
    fun event(line: String) {
        file.parentFile?.mkdirs()
        if (file.length() > maxBytes) file.writeText(file.readText().takeLast((maxBytes / 2).toInt()).substringAfter('\n'))
        file.appendText("${clock()} ${redact(line)}\n")
    }

    fun tail(lines: Int = 40): String = runCatching { file.readLines().takeLast(lines).joinToString("\n") }.getOrDefault("")

    companion object {
        private val SECRET = Regex("""(password|secret|--password)([=:\s]+)\S+""", RegexOption.IGNORE_CASE)
        fun redact(s: String) = SECRET.replace(s) { "${it.groupValues[1]}${it.groupValues[2]}***" }

        /** The last [bytes] of a program's log. */
        fun tailOf(file: File, bytes: Int = 8192): String = runCatching {
            java.io.RandomAccessFile(file, "r").use { f ->
                val n = minOf(bytes.toLong(), f.length()).toInt()
                f.seek(f.length() - n); ByteArray(n).also { f.readFully(it) }.toString(Charsets.UTF_8)
            }
        }.getOrDefault("")
    }
}
