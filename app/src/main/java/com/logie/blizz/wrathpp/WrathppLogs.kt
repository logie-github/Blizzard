package com.logie.blizz.wrathpp

import java.io.File

/**
 * What WarcraftXL's runtime wrote about Wrath++'s launches (`client-wrathpp/Logs/WarcraftXL.log`; the launches before
 * it `WarcraftXL-<time>.log`, the thirty newest kept): a crash it saw (its `[crash]` lines: what faulted and where, the
 * chain of calls), and what the character creator did (`[wrathpp] creator: ...`, written by WrathppCreate.lua through
 * the native mod's `WrathPP_Log`). Read here so that a crash is reported by the app itself, from the log of the launch
 * it happened in, however long after (the user: "The game crashed for me. When clicking on create character", and
 * nothing had been sent: a report went only 90 seconds into a launch, and once a day).
 */
object WrathppLogs {
    private const val REPORTED = "wrathpp-crashes-reported.txt"
    private const val CREATOR_OFF = "wrathpp-creator-off.txt"

    /**
     * A launch's crash: [what] the runtime's first line of it says, [creatorUp] whether the creator was on the screen
     * (its last line before the crash wasn't "closed" or "off"), [text] the end of the launch's log.
     */
    class Crash(val id: String, val what: String, val file: String, val creatorUp: Boolean, val text: String)

    private fun said(line: String, tag: String): String? = line.substringAfter("[$tag]", "").trim().takeIf { line.contains("[$tag]") }

    /** The crash in a launch's log ([lines], the file [name]), or null when it has none. */
    fun crashOf(name: String, lines: List<String>): Crash? {
        val at = lines.indexOfFirst { it.contains("[crash]") && it.contains("[ERROR") }
        if (at < 0) return null
        val what = said(lines[at], "crash") ?: return null
        val creator = lines.take(at).lastOrNull { it.contains("creator: ") }?.substringAfter("creator: ")?.trim()
        val up = creator != null && !creator.startsWith("closed") && !creator.startsWith("off") && creator != "built"
        val id = "%08x".format(((lines.firstOrNull() ?: "") + "|" + lines[at]).hashCode())
        // the launch's start (what ran: the runtime, the mods), then its last lines, the crash among them
        val head = lines.take(at).filter { it.contains("[session]") || it.contains("[host] loaded") || it.contains("creator: ") }.takeLast(40)
        val tail = lines.subList(maxOf(0, at - 60), minOf(lines.size, at + 60))
        return Crash(id, what, name, up, (head + "..." + tail).joinToString("\n"))
    }

    /** The launches' logs in [logs], the newest first. */
    private fun files(logs: File): List<File> =
        logs.listFiles { f -> f.isFile && f.name.startsWith("WarcraftXL") && f.name.endsWith(".log") }?.sortedByDescending { it.lastModified() } ?: emptyList()

    /**
     * The crashes in [logs] that were not handed out before (the newest first, [max] at most: older ones are passed
     * over, and noted too); each is noted in [logs] so that it is handed out once.
     */
    @Synchronized
    fun unreported(logs: File, max: Int = 3): List<Crash> {
        val note = File(logs, REPORTED)
        val known = runCatching { note.readLines().map { it.trim() }.filter { it.isNotEmpty() } }.getOrDefault(emptyList())
        val found = files(logs).mapNotNull { f -> runCatching { crashOf(f.name, f.readLines()) }.getOrNull() }.filter { it.id !in known }
        if (found.isEmpty()) return emptyList()
        runCatching { note.writeText((known + found.map { it.id }).takeLast(200).joinToString("\n", postfix = "\n")) }
        return found.take(max)
    }

    /** What the creator said in a launch: its lines without their numbers, each once, in order (what makes two launches alike). */
    fun creatorSaid(lines: List<String>): String =
        lines.mapNotNull { l -> l.substringAfter("creator: ", "").trim().takeIf { l.contains("creator: ") } }
            .map { it.replace(Regex("\\d+"), "#") }.distinct().joinToString("; ")

    /** The creator's lines of the newest launch in [logs] that has any (the one running, or the one before). */
    fun lastCreatorLines(logs: File, max: Int = 40): List<String> =
        files(logs).asSequence().map { f -> runCatching { f.readLines().filter { it.contains("creator: ") } }.getOrDefault(emptyList()) }
            .firstOrNull { it.isNotEmpty() }?.takeLast(max) ?: emptyList()

    /**
     * The creator is left out for the rest of app build [build] once the game crashed with it on the screen in that
     * build ([creatorCrashed]): the game's own screen until the next build, which starts with the creator again.
     */
    fun creatorOff(logs: File, build: Int): Boolean {
        val f = File(logs, CREATOR_OFF)
        val noted = runCatching { f.readText().trim().toIntOrNull() }.getOrNull() ?: return false
        if (noted == build) return true
        f.delete()
        return false
    }

    fun creatorCrashed(logs: File, build: Int) {
        runCatching { logs.mkdirs(); File(logs, CREATOR_OFF).writeText("$build\n") }
    }
}
