package com.logie.blizz.game

import com.winlator.core.Callback
import com.winlator.core.ProcessHelper
import java.util.ArrayDeque

/**
 * The last lines Wine and Box64 printed while a game ran (Wine's errors and the libraries it loads),
 * kept so the game menu can send them with a report: a black screen leaves no crash to report.
 */
object GameLog {
    private const val MAX = 400
    private const val MAX_LOADED = 80
    private val lines = ArrayDeque<String>()
    /** The libraries loaded (the loaddll channel), apart: hundreds of them would push the errors and the exception trace out of the report. */
    private val loaded = ArrayDeque<String>()
    /**
     * Wine's own word that a program of the session died of a fault ("wine: Unhandled page fault on read access to 00000000 at
     * address 6F0E87CC (thread 0024)..."), the first one: a game that stops that way later than its first minute went back to the
     * launcher without a word, and without a report.
     */
    @Volatile var fault: String? = null
        private set

    private val callback = Callback<String> { line: String -> take(line) }

    /** What repeats, said a few times and then counted ([RepeatLimiter]). */
    private val repeats = com.logie.blizz.reports.RepeatLimiter()

    /** One line of the programs' output, into its place (and into the run's log file, [com.logie.blizz.reports.SessionLog]). */
    internal fun take(line: String) {
        if (fault == null && line.contains("Unhandled ") && line.contains("wine")) fault = line.trim().take(200)
        if (line.contains(":loaddll:")) {
            synchronized(loaded) {
                if (loaded.size >= MAX_LOADED) loaded.removeFirst()
                loaded.addLast(line.take(300))
            }
            com.logie.blizz.reports.SessionLog.event("lib", com.logie.blizz.reports.LibLines.compact(line))
        } else synchronized(lines) {
            if (!noise(line)) {
                val admitted = repeats.admit(line)
                if (admitted != null) {
                    if (lines.size >= MAX) lines.removeFirst()
                    lines.addLast(admitted.take(300))
                    com.logie.blizz.reports.SessionLog.event("wine", admitted)
                }
            }
        }
    }

    /** The threads (Wine's `00dc:` prefix) whose exception trace is, for now, a longjmp's. */
    private val unwinding = HashSet<String>()

    /**
     * Whether [line] is part of a longjmp's trace on the seh channel (`code=80000026`, STATUS_LONGJUMP, and the register lines
     * after it): Diablo II makes one a frame, eight lines each, and the phone's reports of 9 November 2026 held nothing else. A
     * real exception's trace (any other code) is kept whole. Called in the order the lines come.
     */
    internal fun noise(line: String): Boolean {
        val at = line.indexOf(":trace:seh:")
        if (at < 0) return false
        // .NET asks for a process's modules over and over (three times a second in the phone's reports): never of use.
        if (line.contains(":EnumProcessModulesEx ")) return true
        val thread = line.substring(0, at)
        // A longjmp's trace (Diablo II), and a thread being named (`code=406d1388`, every thread .NET starts): neither is a fault.
        if (line.contains(" code=")) { if (line.contains("code=80000026") || line.contains("code=406d1388")) unwinding += thread else unwinding -= thread }
        return thread in unwinding
    }

    /** Starts listening to the programs' output (once; after Winlator has set up its own listeners). */
    /** When the game screen last started its session ([start]; System.currentTimeMillis), 0 before any. */
    @Volatile var startedAt: Long = 0L
        private set

    fun start() {
        startedAt = System.currentTimeMillis()
        clear()
        com.logie.blizz.reports.SessionLog.event("game", "game screen opened: a session starts")
        ProcessHelper.addDebugCallback(callback)
    }

    /** The game screen is gone: what repeated and how often, and Wine's word of a fault, go into the run's log. */
    fun finish() {
        val totals = synchronized(lines) { repeats.totals() }
        if (totals.isNotEmpty()) com.logie.blizz.reports.SessionLog.event("wine", "repeated lines, counted instead of written:\n" + totals.joinToString("\n"))
        fault?.let { com.logie.blizz.reports.SessionLog.event("wine", "first fault Wine reported: $it") }
        com.logie.blizz.reports.SessionLog.event("game", "game screen closed")
    }

    /** A new session: nothing of the last one's. */
    internal fun clear() {
        synchronized(lines) { lines.clear(); unwinding.clear(); repeats.clear() }
        synchronized(loaded) { loaded.clear() }
        synchronized(notes) { notes.clear() }
        fault = null
    }

    /** The app's own notes (what the launcher and the touch layer decided), kept apart so a flood of Wine's lines doesn't push them out. */
    private val notes = ArrayDeque<String>()

    fun note(text: String) {
        synchronized(notes) {
            if (notes.size >= 120) notes.removeFirst()
            notes.addLast("[app] " + text.take(300))
        }
        com.logie.blizz.reports.SessionLog.event("app", text)
    }

    /**
     * The session keeper's own log of the game being played (`C:\windows\borderless.log` in the games' Windows, [Borderless]):
     * what it started, the game's windows as they appeared, a dialog box's words, why the session ended. Set at each start.
     */
    @Volatile var keeperLog: java.io.File? = null

    /** The keeper's lines (the last [max]), each cut to 300 characters; "" when there is no log. */
    fun keeperLines(file: java.io.File? = keeperLog, max: Int = 80): String {
        val f = file?.takeIf { it.isFile } ?: return ""
        val lines = runCatching { f.readLines(Charsets.ISO_8859_1) }.getOrDefault(emptyList()).filter { it.isNotBlank() }
        if (lines.isEmpty()) return ""
        return "[session keeper]\n" + lines.takeLast(max).joinToString("\n") { it.take(300) }
    }

    /**
     * Everything, the least telling first: the libraries loaded, Wine's and Box64's lines, the session keeper's log, the app's
     * own notes. A report keeps the end of it ([com.logie.blizz.reports.BugReports.body]), so what is cut for length is the
     * libraries, then the oldest of Wine's lines (the phone's reports of 9 and 10 November 2026 were four fifths library names,
     * with the app's notes cut off the top).
     */
    fun snapshot(): String = listOf(
        synchronized(loaded) { if (loaded.isEmpty()) "" else "[last ${loaded.size} libraries loaded]\n" + loaded.joinToString("\n") },
        synchronized(lines) { lines.joinToString("\n") },
        keeperLines(),
        synchronized(notes) { notes.joinToString("\n") },
    ).filter { it.isNotEmpty() }.joinToString("\n\n")
}
