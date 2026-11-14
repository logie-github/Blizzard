package com.logie.blizz.reports

import android.content.Context
import android.os.Build
import com.logie.blizz.BuildConfig
import java.io.File
import java.io.FileOutputStream
import java.io.RandomAccessFile
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone

/**
 * The app's log of one run, in a file on the phone: `files/logs/run-<start>.log`, a line each with its time (UTC, to the
 * millisecond) and its kind. The in-memory log ([com.logie.blizz.game.GameLog]) is gone when the app is killed, which is
 * exactly when it is wanted (the phone, 12 and 13 November 2026: the launcher's window went, the game ended, and nothing
 * was left); this one is written line by line, straight to the file (no buffer to lose), so the next start can read the end
 * of the last run, and a report can carry as much of the run as it needs.
 *
 * Kinds: `app` (what the app decided), `forever` (Play's steps), `wine` (Wine's and Box64's lines, without the noise),
 * `lib` (libraries loaded), `keeper` (the Windows session's keeper), `res` (memory and processes, every few seconds: [Sampler]),
 * `exit` (how the last run ended: [ExitReasons]), `report` (what became of each report), `log` (this log's own words).
 *
 * A run's log is rolled over at [maxBytes] (the older part kept, the one before it dropped), and only the newest [keep] logs
 * stay. Nothing in here may crash the app: any failure to write turns the log off for that run.
 */
class LogFile(
    private val dir: File,
    private val clock: () -> Long = System::currentTimeMillis,
    private val maxBytes: Long = 2L shl 20,
    private val keep: Int = 6,
) {
    private var stamp = ""
    private var part = 1
    private var out: FileOutputStream? = null
    private var written = 0L
    private var failed = false
    private val format = SimpleDateFormat("HH:mm:ss.SSS", Locale.US).apply { timeZone = TimeZone.getTimeZone("UTC") }
    private val dayFormat = SimpleDateFormat("yyyyMMdd-HHmmss", Locale.US).apply { timeZone = TimeZone.getTimeZone("UTC") }

    /** Starts this run's log, with [header] as its first lines; the oldest logs beyond [keep] go. */
    @Synchronized fun open(header: List<String>) {
        close()
        failed = false
        dir.mkdirs()
        stamp = dayFormat.format(Date(clock()))
        part = 1
        prune()
        header.forEach { write("log", it) }
    }

    /** One line of [kind]; [text] may hold several lines, each given the time. */
    @Synchronized fun write(kind: String, text: String) {
        if (failed) return
        runCatching {
            if (out == null) startPart()
            val time = format.format(Date(clock()))
            val lines = text.trimEnd().lines().ifEmpty { listOf("") }
            val builder = StringBuilder()
            for (line in lines) builder.append(time).append(' ').append(kind.padEnd(7)).append(line.take(MAX_LINE)).append('\n')
            val bytes = builder.toString().toByteArray()
            if (written + bytes.size > maxBytes) rollOver()
            out!!.write(bytes)
            written += bytes.size
        }.onFailure { failed = true }
    }

    /** This run's files, oldest first. */
    @Synchronized fun runFiles(): List<File> = filesOf(stamp)

    /** The end of this run's log: up to [maxChars], from a line's start, the older part first when the newer one is short. */
    @Synchronized fun tail(maxChars: Int): String = tailOf(runFiles(), maxChars)

    /** The end of the newest run before this one (what a start finds of a run the system ended). Empty when there is none. */
    @Synchronized fun previousTail(maxChars: Int): String {
        val earlier = (dir.listFiles { f -> f.name.startsWith("run-") && f.name.endsWith(".log") } ?: return "")
            .map { runOf(it.name) }.filter { it != stamp }.distinct().sorted().lastOrNull() ?: return ""
        return tailOf(filesOf(earlier), maxChars)
    }

    @Synchronized fun close() {
        runCatching { out?.close() }
        out = null
    }

    private fun startPart() {
        dir.mkdirs()
        val file = File(dir, name(stamp, part))
        out = FileOutputStream(file, true)
        written = file.length()
    }

    private fun rollOver() {
        close()
        part++
        // (the part before the one just filled goes; parts are numbered from 1)
        if (part - 2 >= 1) File(dir, name(stamp, part - 2)).delete()
        startPart()
        val note = "${format.format(Date(clock()))} ${"log".padEnd(7)}(earlier part kept: ${name(stamp, part - 1)})\n"
        out!!.write(note.toByteArray())
        written += note.length
    }

    private fun prune() {
        val runs = (dir.listFiles { f -> f.name.startsWith("run-") && f.name.endsWith(".log") } ?: return)
            .map { runOf(it.name) }.distinct().sorted()
        // (this run's own files do not exist yet: `keep - 1` earlier ones stay beside it)
        for (old in runs.dropLast((keep - 1).coerceAtLeast(0))) filesOf(old).forEach { it.delete() }
    }

    private fun filesOf(run: String): List<File> =
        (dir.listFiles { f -> f.name.startsWith("run-$run") && f.name.endsWith(".log") && runOf(f.name) == run } ?: emptyArray())
            .sortedBy { partOf(it.name) }

    private fun tailOf(files: List<File>, maxChars: Int): String {
        val pieces = ArrayList<String>()
        var left = maxChars
        for (file in files.reversed()) {
            if (left <= 0) break
            val text = readEnd(file, left)
            pieces += text
            left -= text.length
        }
        return pieces.reversed().joinToString("")
    }

    /** The last [max] bytes of [file], from the start of a line (unless the file is shorter than that). */
    private fun readEnd(file: File, max: Int): String = runCatching {
        RandomAccessFile(file, "r").use { f ->
            val length = f.length()
            val start = (length - max).coerceAtLeast(0)
            f.seek(start)
            val bytes = ByteArray((length - start).toInt())
            f.readFully(bytes)
            val text = bytes.decodeToString()
            if (start > 0) text.substringAfter('\n', text) else text
        }
    }.getOrDefault("")

    companion object {
        /** A line longer than this is cut: a log line is a sentence, not a dump. */
        const val MAX_LINE = 600

        fun name(stamp: String, part: Int) = if (part <= 1) "run-$stamp.log" else "run-$stamp.$part.log"
        fun runOf(name: String) = name.removePrefix("run-").removeSuffix(".log").substringBefore('.')
        fun partOf(name: String) = name.removePrefix("run-").removeSuffix(".log").substringAfter('.', "1").toIntOrNull() ?: 1
    }
}

/** This run's log ([LogFile] in `files/logs`), started as the app starts. */
object SessionLog {
    @Volatile private var file: LogFile? = null

    fun dir(context: Context) = File(context.applicationContext.filesDir, "logs-app")

    /** Once, as the app starts (again does nothing): a new run's log with the app's and the phone's identity at its head. */
    @Synchronized fun start(context: Context) {
        if (file != null) return
        val app = context.applicationContext
        val log = LogFile(dir(app))
        log.open(listOf(
            "run started: Blizzard ${BuildConfig.VERSION_NAME} (${BuildConfig.VERSION_CODE}), times in UTC",
            "device: ${Build.MANUFACTURER} ${Build.MODEL} (${Build.DEVICE}), Android ${Build.VERSION.RELEASE} (API ${Build.VERSION.SDK_INT}), ${Build.SUPPORTED_ABIS.joinToString(",")}",
        ))
        file = log
    }

    /** One line, of [kind] (see [LogFile]). Without a started log (a test, another process) nothing is written. */
    fun event(kind: String, text: String) {
        // (a key or a token never reaches the file, even though the file never leaves the phone by itself)
        file?.write(kind, BugReports.redact(text))
    }

    /** The end of this run's log. */
    fun tail(maxChars: Int): String = file?.tail(maxChars).orEmpty()

    /** The end of the run before this one. */
    fun previousTail(maxChars: Int): String = file?.previousTail(maxChars).orEmpty()
}
