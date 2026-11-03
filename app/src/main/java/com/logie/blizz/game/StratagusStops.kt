// SPDX-License-Identifier: GPL-2.0-or-later

package com.logie.blizz.game

import android.content.Context
import java.io.File
import java.io.PrintWriter
import java.io.StringWriter
import java.util.concurrent.TimeUnit

/**
 * What a Stratagus game said last when it stopped by itself (from YeaBwoi's GameStops).
 *
 * While the game plays, [StratagusActivity] keeps a file named `running` in the game's folder
 * holding its process id, deleted when the game is left from the app's menu. The engine writes its
 * output to `stdout.txt` and `stderr.txt` there, a crash's signal and stack too, and "Stratagus:
 * exit 0" when it's quit from its own menu. A `running` file whose process is gone, without that
 * line, is a game that stopped by itself: its last output and Android's log for its process make
 * the report, which goes out through [com.logie.blizz.reports.BugReports].
 */
object StratagusStops {
    private const val RUNNING = "running"
    private const val NORMAL_EXIT = "Stratagus: exit 0"

    /** A game starts in this process: the last run's output goes, this one's is watched. */
    fun started(dataDir: File) {
        File(dataDir, "stdout.txt").delete()
        File(dataDir, "stderr.txt").delete()
        File(dataDir, RUNNING).writeText(android.os.Process.myPid().toString())
    }

    /** The game was left from the app's menu. */
    fun left(dataDir: File) {
        File(dataDir, RUNNING).delete()
    }

    /** Java exceptions of the game's process are written into its folder, then go on as before. */
    fun catchJavaCrashes(dataDir: File, where: String) {
        val previous = Thread.getDefaultUncaughtExceptionHandler()
        Thread.setDefaultUncaughtExceptionHandler { thread, error ->
            runCatching {
                val trace = StringWriter().also { error.printStackTrace(PrintWriter(it)) }.toString()
                File(dataDir, "stderr.txt").appendText("\n$where, thread ${thread.name}:\n$trace")
            }
            previous?.uncaughtException(thread, error)
        }
    }

    /** Is [pid] the game's process (`:stratagus`) still running? */
    fun isGameProcess(pid: Int): Boolean =
        runCatching { File("/proc/$pid/cmdline").readText().contains(":stratagus") }.getOrDefault(false)

    /**
     * The report text of a game in [dataDir] that stopped by itself since last looked (once), or
     * null: still running, left properly, quit from its menu, or ended from outside with nothing said.
     */
    fun take(
        dataDir: File,
        name: String,
        alive: (Int) -> Boolean = ::isGameProcess,
        log: (Int) -> List<String> = ::logcat,
    ): String? {
        val running = File(dataDir, RUNNING)
        if (!running.isFile) return null
        val pid = runCatching { running.readText().trim().toInt() }.getOrNull()
        if (pid != null && alive(pid)) return null
        running.delete()
        val errors = tail(File(dataDir, "stderr.txt"), 60)
        if (errors.lastOrNull { it.isNotBlank() }?.trim() == NORMAL_EXIT) return null
        val output = tail(File(dataDir, "stdout.txt"), 25)
        val android = if (pid != null) log(pid) else emptyList()
        if (errors.isEmpty() && android.none { it.contains("Fatal signal") || it.contains("FATAL EXCEPTION") }) return null
        val text = buildString {
            appendLine("$name: stderr.txt:")
            errors.ifEmpty { listOf("(empty)") }.forEach { appendLine(it) }
            appendLine()
            appendLine("stdout.txt (last lines):")
            output.ifEmpty { listOf("(empty)") }.forEach { appendLine(it) }
            if (android.isNotEmpty()) {
                appendLine()
                appendLine("Android's log for the game's process:")
                android.forEach { appendLine(it) }
            }
        }.trimEnd()
        runCatching { File(dataDir, "last-stop.txt").writeText(text) }
        return text
    }

    /** Looks at [dataDir] and, for a game that stopped, sends the report. True if one was sent. */
    fun reportIfStopped(context: Context, dataDir: File, gameId: String, name: String): Boolean {
        val text = take(dataDir, name) ?: return false
        com.logie.blizz.reports.BugReports.report(
            context, "$name stopped", text.lineSequence().drop(1).firstOrNull { it.isNotBlank() } ?: "stopped by itself",
            listOf("Game" to gameId, "Device" to android.os.Build.MODEL),
            log = text,
        )
        return true
    }

    private fun tail(file: File, lines: Int): List<String> =
        if (file.isFile) runCatching { file.readLines().takeLast(lines) }.getOrDefault(emptyList()) else emptyList()

    /** Android's log lines of process [pid] (an app may read its own processes' log). */
    private fun logcat(pid: Int): List<String> = runCatching {
        val process = ProcessBuilder("logcat", "-d", "-v", "time", "--pid=$pid", "-t", "400")
            .redirectErrorStream(true)
            .start()
        val lines = process.inputStream.bufferedReader().readLines()
        process.waitFor(5, TimeUnit.SECONDS)
        lines.filter { it.isNotBlank() && !it.startsWith("-----") }.takeLast(80)
    }.getOrDefault(emptyList())
}
