package com.logie.blizz.reports

/**
 * Keeps a program's repeated message from burying the rest: a line's first [limit] times pass, then it is counted, and the
 * count is said at 10, 100, 1000... times (the phone's reports of 13 November 2026 were mostly one message about the .NET
 * runtime's registry key, a line about Windows' management interface three times a second, and a thread being named).
 * Lines count as the same when they differ only in numbers (a thread id, an address, a size). Not thread safe: the caller's lock.
 */
class RepeatLimiter(private val limit: Int = 3, private val maxKinds: Int = 2000) {
    private val counts = HashMap<String, Int>()
    private val first = HashMap<String, String>()

    /** What to log for [line]: itself (its first [limit] times), a line saying how many times at 10, 100, 1000..., else null. */
    fun admit(line: String): String? {
        val key = key(line)
        if (counts.size >= maxKinds && key !in counts) { counts.clear(); first.clear() }
        val n = (counts[key] ?: 0) + 1
        counts[key] = n
        if (n == 1) first[key] = line.trim().take(160)
        return when {
            n <= limit -> line
            n == 10 || n == 100 || n == 1_000 || n == 10_000 || n == 100_000 -> "(the same kind of line $n times so far: ${first[key]})"
            else -> null
        }
    }

    /** The kinds of line that went over the limit, most frequent first: "1200 x the line". For the end of a session. */
    fun totals(max: Int = 30): List<String> =
        counts.entries.filter { it.value > limit }.sortedByDescending { it.value }.take(max).map { "${it.value} x ${first[it.key]}" }

    fun clear() { counts.clear(); first.clear() }

    companion object {
        private val thread = Regex("^[0-9a-fA-F]{4}:")
        private val numbers = Regex("\\b0x[0-9a-fA-F]+\\b|\\b[0-9a-fA-F]{5,}\\b|\\d+")

        /** What makes two lines the same kind: the line without its thread and its numbers. */
        fun key(line: String): String = line.trim().replace(thread, "").replace(numbers, "#")
    }
}

/** Wine's `loaddll` lines, shortened to what they say. */
object LibLines {
    private val path = Regex("L\"(.*?)\"")

    /**
     * `00e8:trace:loaddll:build_module Loaded L"C:\\windows\\system32\\kernelbase.dll" at 000000027FBC0000: builtin` as
     * `00e8 Loaded C:\windows\system32\kernelbase.dll builtin`; a line that isn't one stays as it is.
     */
    fun compact(line: String): String {
        val thread = line.take(4).takeIf { t -> t.length == 4 && t.all { it.isLetterOrDigit() } } ?: ""
        val file = path.find(line)?.groupValues?.get(1)?.replace("\\\\", "\\") ?: return line.trim()
        val verb = if (line.contains("Unloaded")) "Unloaded" else "Loaded"
        val kind = line.substringAfterLast(": ", "").trim().takeIf { it.isNotEmpty() && it.length < 12 } ?: ""
        return listOf(thread, verb, file, kind).filter { it.isNotEmpty() }.joinToString(" ")
    }
}
