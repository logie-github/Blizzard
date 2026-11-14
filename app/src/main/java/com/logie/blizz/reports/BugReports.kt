package com.logie.blizz.reports

import android.content.Context
import android.os.Build
import com.logie.blizz.BuildConfig
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest

/**
 * The app's failures, sent to its GitHub repository as issues, by themselves (with the token CI
 * builds in, as YeaBwoi's apps do): the app crashing, an
 * import failing, a game failing to start. Each is written to `files/reports` first, then sent at
 * once and again every minute while any wait (offline, GitHub busy), and kept until GitHub takes
 * it. The same failure goes once a day at most. Stopping an import, a full phone and a game
 * version the app doesn't play aren't bugs and aren't sent. CD keys are never in a report.
 */
object BugReports {
    /**
     * A failure to send: its title (also what makes two the same failure), its body, and what goes after it as comments on
     * the issue (a run's log, Android's log: more than an issue's 65,536 characters hold). [issue] and [done] are where a send
     * got to (the issue opened, comments posted), kept in the file so a retry goes on from there and nothing is posted twice.
     */
    data class Report(
        val title: String, val body: String, val label: String = "auto-report",
        val comments: List<String> = emptyList(), val issue: Int = 0, val done: Int = 0,
    ) {
        val key: String get() = sha(title.replace(Regex("\\d+"), "#"))

        fun toJson(): JSONObject = JSONObject().put("title", title).put("body", body).put("label", label)
            .put("comments", JSONArray(comments)).put("issue", issue).put("done", done)

        /** What GitHub's issues API is sent (the body cut to its limit, as a last guard). */
        fun issueJson(): String = JSONObject().put("title", title).put("body", body.take(MAX_ISSUE)).put("labels", JSONArray(listOf("bug", label))).toString()

        companion object {
            fun fromJson(o: JSONObject) = Report(
                o.getString("title"), o.getString("body"), o.optString("label", "auto-report"),
                o.optJSONArray("comments")?.let { a -> List(a.length()) { a.getString(it) } } ?: emptyList(),
                o.optInt("issue", 0), o.optInt("done", 0),
            )
        }
    }

    /** What became of one attempt to send a report: for the person (a toast) and for the log. */
    data class SendResult(val outcome: Outcome, val code: Int = 0, val issue: Int = 0, val detail: String = "") {
        /** In words, for the person. */
        fun say(): String = when (outcome) {
            Outcome.SENT -> if (issue > 0) "Report sent: issue #$issue" else "Report sent"
            Outcome.RETRY -> "Couldn't send the report yet ($detail). It stays on the phone and goes again every minute."
            Outcome.NOT_CONFIGURED -> "This build can't send reports ($detail). The report stays on the phone."
            Outcome.REFUSED -> "GitHub refused the report ($detail)."
        }
    }

    enum class Outcome { SENT, RETRY, NOT_CONFIGURED, REFUSED }

    /** GitHub's limit for an issue's or a comment's text is 65,536 characters; this is kept well under it. */
    const val MAX_ISSUE = 62_000
    /** One comment's share of a long text. */
    const val CHUNK = 58_000
    /** What a body refused for its size is cut to for one more try. */
    private const val SHRUNK = 20_000
    /** Between a report's comments: GitHub asks for a pause between things made one after another. */
    private const val COMMENT_GAP_MS = 1_500L
    private const val ONCE_PER_MS = 24 * 60 * 60 * 1000L
    private const val RETRY_MS = 60_000L
    /** Between two reports sent in a row: GitHub refuses issues opened in a burst. */
    private const val SEND_GAP_MS = 3_000L
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    @Volatile private var looping = false

    /** The repository the issues go to. */
    const val repo = "logie-github/Blizzard"

    /** The token the issues are opened with: CI's BLIZZ_REPORT_TOKEN secret, built in. Without one, reports wait. */
    fun token(@Suppress("UNUSED_PARAMETER") context: Context): String = BuildConfig.REPORT_TOKEN

    fun configured(context: Context): Boolean = token(context).isNotEmpty()

    /** Reports waiting to be sent. */
    fun waiting(context: Context): Int = dir(context).listFiles { f -> f.name.endsWith(".json") }?.size ?: 0

    fun dir(context: Context) = File(context.applicationContext.filesDir, "reports")

    /** Once, as the app starts: crashes from now on are reported, and waiting reports go. */
    fun start(context: Context) {
        val app = context.applicationContext
        // The run's log first (a crash from now on is in it), then why the last run ended, then the look at memory and processes.
        runCatching { SessionLog.start(app) }
        catchCrashes(app)
        // (the system's record of how the last run ended is read off the main thread: a binder call and a file or two)
        scope.launch { runCatching { ExitReasons.check(app) } }
        runCatching { Diagnostics.startSampler(app) }
        sendSoon(app)
    }

    /**
     * A failure the app met: queued, then sent. [force]: sent even if the same one went within the day (a report the person asked
     * for; its file has a name of its own). [attach]: the phone's state in the body and the run's log and Android's log as
     * comments after it, for a report that has to explain a run. [comments]: more of that kind (title and text; long ones are
     * split to fit). [onResult]: told what became of the first attempt (the toast: [reportTelling]).
     * Whether it was queued (false: the same one went within the day; always true for one that gathers the phone's state, which is
     * done off the caller's thread).
     */
    fun report(
        context: Context, what: String, message: String, details: List<Pair<String, String?>> = emptyList(), log: String? = null,
        files: String? = null, attach: Boolean = false, force: Boolean = false, comments: List<Pair<String, String>> = emptyList(),
        onResult: ((SendResult) -> Unit)? = null,
    ): Boolean {
        val app = context.applicationContext
        val now = System.currentTimeMillis()
        fun enqueue(extra: List<Pair<String, String>>, device: String?): Boolean {
            val report = Report(
                "$what: ${message.lineSequence().first().take(140)}", body(what, message, details, log, files, device),
                comments = extra.flatMap { (title, text) -> chunks(title, redact(text)) },
            )
            // (a full phone is the usual reason an import failed: the report must not be what crashes the app)
            val queued = runCatching { queue(dir(app), report, now, force) }.getOrDefault(false)
            if (queued) {
                if (onResult != null) callbacks[fileName(report, force, now)] = onResult
                SessionLog.event("report", "queued: ${report.title} (${report.body.length} chars, ${report.comments.size} comments${if (force) ", forced" else ""})")
                sendSoon(app)
            } else SessionLog.event("report", "not queued (the same went within the day): ${report.title}")
            return queued
        }
        if (!attach && comments.isEmpty()) return enqueue(emptyList(), null)
        // Reading the phone's state and Android's log can take seconds (the log is read through a program): never on the caller's
        // thread, which may be a button's or the app's start. So whether it was queued is not known here: true.
        scope.launch {
            runCatching {
                val device = if (attach) runCatching { Diagnostics.deviceState(app) }.getOrNull() else null
                val more = if (attach) runCatching { Diagnostics.attachments(app) }.getOrDefault(emptyList()) else emptyList()
                enqueue(comments + more, device)
            }
        }
        return true
    }

    /**
     * A report the person asked for (the game menu's): sent whatever went before, with the run's log, and told in words what became
     * of it, once the first attempt is known ("Report sent: issue #12", or why not) instead of "it goes out when the phone is online".
     */
    fun reportTelling(activity: android.app.Activity, what: String, message: String, details: List<Pair<String, String?>>, log: String?) {
        val app = activity.applicationContext
        fun tell(text: String) = android.os.Handler(android.os.Looper.getMainLooper()).post {
            android.widget.Toast.makeText(app, text, android.widget.Toast.LENGTH_LONG).show()
        }
        if (!configured(app)) {
            report(app, what, message, details, log, attach = true, force = true)
            tell("This build can't send reports (no token). The report, with the run's log, is kept on the phone.")
            return
        }
        tell("Sending the report…")
        val queued = report(app, what, message, details, log, attach = true, force = true, onResult = { tell(it.say()) })
        if (!queued) tell("The report could not be written on the phone.")
    }

    /** A report that is sent whatever came before (the launch test's): kept on the phone until GitHub takes it. False when this build has no token. */
    fun submit(context: Context, report: Report): Boolean {
        val app = context.applicationContext
        val d = dir(app).also { it.mkdirs() }
        runCatching { File(d, "${report.key}-${System.currentTimeMillis()}.json").writeText(report.toJson().toString()) }
        sendSoon(app)
        return configured(app)
    }

    /** The name a queued report's file has: by its failure's key, and for a [force]d one with the time too (it never replaces another). */
    fun fileName(report: Report, force: Boolean, now: Long) = if (force) "${report.key}-f$now.json" else "${report.key}.json"

    /** Writes [report] to [dir], unless the same failure went in the last day ([force]: whatever went before). Plain Kotlin, unit-tested. */
    fun queue(dir: File, report: Report, now: Long = System.currentTimeMillis(), force: Boolean = false): Boolean {
        dir.mkdirs()
        if (force) {
            File(dir, fileName(report, true, now)).writeText(report.toJson().toString())
            return true
        }
        val sent = File(dir, "sent.txt")
        val recent = runCatching { sent.readLines() }.getOrDefault(emptyList())
            .mapNotNull { line -> line.split(' ').takeIf { it.size == 2 }?.let { it[0] to it[1].toLongOrNull() } }
            .filter { (_, at) -> at != null && now - at < ONCE_PER_MS }
        if (recent.any { it.first == report.key }) return false
        if (File(dir, "${report.key}.json").exists()) return false
        File(dir, "${report.key}.json").writeText(report.toJson().toString())
        sent.writeText((recent.map { "${it.first} ${it.second}" } + "${report.key} $now").joinToString("\n") + "\n")
        return true
    }

    /**
     * [text] as comment bodies that fit GitHub's limit, split at line ends: each a heading ([title], "part k of n"), the text in a
     * code block. A long log is posted whole as several comments instead of cut to fit one issue.
     */
    fun chunks(title: String, text: String, size: Int = CHUNK): List<String> {
        if (text.isBlank()) return emptyList()
        val parts = ArrayList<String>()
        val current = StringBuilder()
        for (line in text.lineSequence()) {
            val piece = if (line.length > 4_000) line.take(4_000) + " (cut)" else line
            if (current.length + piece.length + 1 > size && current.isNotEmpty()) { parts += current.toString(); current.setLength(0) }
            current.append(piece).append('\n')
        }
        if (current.isNotEmpty()) parts += current.toString()
        val fence = "`".repeat(3)
        return parts.mapIndexed { i, part ->
            "**$title" + (if (parts.size > 1) " (part ${i + 1} of ${parts.size})" else "") + "**\n\n$fence\n" + part.replace(fence, "'''") + "$fence\n"
        }
    }

    /** The issue's text: what failed, what the app said, its details, the device, the end of the log. */
    fun body(what: String, message: String, details: List<Pair<String, String?>>, log: String?, files: String? = null, device: String? = null): String = buildString {
        append("**$what**\n\n")
        append(message.trim()).append("\n\n")
        append("| | |\n| --- | --- |\n")
        append("| App | Blizzard ${BuildConfig.VERSION_NAME} (${BuildConfig.VERSION_CODE}) |\n")
        append("| Device | ${Build.MANUFACTURER} ${Build.MODEL} |\n")
        append("| Android | ${Build.VERSION.RELEASE} (API ${Build.VERSION.SDK_INT}) |\n")
        for ((name, value) in details) if (!value.isNullOrBlank()) append("| $name | ${value.replace("|", "\\|").replace("\n", " ")} |\n")
        if (!device.isNullOrBlank()) {
            append("\n<details open><summary>The phone just now</summary>\n\n```\n")
            append(redact(device).take(6_000).replace("```", "'''"))
            append("\n```\n</details>\n")
        }
        if (!log.isNullOrBlank()) {
            append("\n<details><summary>Log</summary>\n\n```\n")
            append(redact(log).takeLast(20_000).replace("```", "'''"))
            append("\n```\n</details>\n")
        }
        if (!files.isNullOrBlank()) {
            append("\n<details><summary>Files (paths, sizes, hashes; never their content)</summary>\n\n```\n")
            append(redact(files).take(30_000).replace("```", "'''"))
            append("\n```\n</details>\n")
        }
        append("\n_Sent by the app by itself._\n")
    }

    /** Anything shaped like a CD key or a token, out. */
    fun redact(text: String): String = text
        .replace(Regex("--cdkey(-expansion)?\\s+\\S+"), "--cdkey$1 [removed]")
        .replace(Regex("\\b[A-Z0-9]{26}\\b"), "[removed]")
        .replace(Regex("\\b(ghp|github_pat)_[A-Za-z0-9_]+"), "[removed]")
        // Console keys and title keys (hex of 32 digits or more), as hactool prints them in its errors.
        .replace(Regex("\\b[0-9A-Fa-f]{32,}\\b"), "[removed]")

    /** Told what became of a report's first attempt ([report]'s `onResult`), by its file's name. */
    private val callbacks = java.util.concurrent.ConcurrentHashMap<String, (SendResult) -> Unit>()

    private fun sendSoon(context: Context) {
        if (looping || !configured(context)) return
        looping = true
        scope.launch {
            try {
                while (true) {
                    val waiting = dir(context).listFiles { f -> f.name.endsWith(".json") }?.sortedBy { it.lastModified() } ?: emptyList()
                    if (waiting.isEmpty()) break
                    var retry = false
                    for (file in waiting) {
                        val title = runCatching { JSONObject(file.readText()).optString("title") }.getOrDefault("")
                        val result = sendDetailed(file, repo, token(context))
                        record(context, title, result)
                        callbacks.remove(file.name)?.let { callback -> runCatching { callback(result) } }
                        when (result.outcome) {
                            Outcome.SENT, Outcome.REFUSED -> { file.delete(); if (waiting.size > 1) delay(SEND_GAP_MS) }
                            Outcome.RETRY -> retry = true
                            Outcome.NOT_CONFIGURED -> return@launch
                        }
                    }
                    if (!retry) break
                    delay(RETRY_MS)
                }
            } finally {
                looping = false
            }
        }
    }

    private val historyTime = java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss", java.util.Locale.US).apply { timeZone = java.util.TimeZone.getTimeZone("UTC") }

    /** What became of an attempt: one line in the history file and in the run's log (UTC). */
    private fun record(context: Context, title: String, result: SendResult) {
        val line = synchronized(historyTime) { historyTime.format(java.util.Date()) } +
            " ${result.outcome}" + (if (result.issue > 0) " #${result.issue}" else "") + (if (result.code > 0) " ${result.code}" else "") +
            " ${title.take(90)}" + (if (result.detail.isNotBlank()) " (${result.detail})" else "")
        SessionLog.event("report", line)
        runCatching {
            val file = File(dir(context), "history.log")
            val lines = (runCatching { file.readLines() }.getOrDefault(emptyList()) + line).takeLast(200)
            file.writeText(lines.joinToString("\n") + "\n")
        }
    }

    /** The last [max] lines of what became of reports (newest last): "time OUTCOME #issue code title (detail)". */
    fun history(context: Context, max: Int = 20): List<String> =
        runCatching { File(dir(context), "history.log").readLines().takeLast(max) }.getOrDefault(emptyList())

    /** One report to GitHub, as [sendDetailed] says, as its outcome. Plain Kotlin with [open] for the connection, unit-tested. */
    fun send(file: File, repo: String, token: String, api: String = "https://api.github.com", open: (URL) -> HttpURLConnection = { it.openConnection() as HttpURLConnection }): Outcome {
        val outcome = sendDetailed(file, repo, token, api, open, gapMs = 0).outcome
        // (a report GitHub refuses as it is counts as gone: it is not sent again)
        return if (outcome == Outcome.REFUSED) Outcome.SENT else outcome
    }

    private class Http(val code: Int, val body: String, val retryAfter: String?, val remaining: String?, val error: String?)

    private fun post(url: String, json: String, token: String, open: (URL) -> HttpURLConnection): Http = try {
        val c = open(URL(url))
        c.requestMethod = "POST"
        c.doOutput = true
        c.connectTimeout = 15_000
        c.readTimeout = 30_000
        c.setRequestProperty("Authorization", "Bearer $token")
        c.setRequestProperty("Accept", "application/vnd.github+json")
        c.setRequestProperty("Content-Type", "application/json")
        c.setRequestProperty("User-Agent", "Blizzard-Android/${BuildConfig.VERSION_NAME}")
        c.outputStream.use { it.write(json.toByteArray()) }
        val code = c.responseCode
        val body = runCatching { (if (code < 400) c.inputStream else c.errorStream)?.use { it.readBytes().take(200_000).toByteArray().decodeToString() } }.getOrNull().orEmpty()
        Http(code, body, c.getHeaderField("Retry-After"), c.getHeaderField("X-RateLimit-Remaining"), null)
    } catch (e: IOException) {
        Http(0, "", null, null, "${e.javaClass.simpleName}: ${e.message.orEmpty().take(80)}")
    }

    private fun classify(h: Http): SendResult {
        val code = h.code
        val said = runCatching { JSONObject(h.body).optString("message") }.getOrDefault("").take(120)
        return when {
            h.error != null -> SendResult(Outcome.RETRY, 0, 0, "no connection to GitHub: ${h.error}")
            code in 200..299 -> SendResult(Outcome.SENT, code, runCatching { JSONObject(h.body).optInt("number", 0) }.getOrDefault(0))
            // GitHub's "too many requests too fast" (a secondary rate limit: 403 or 429 with Retry-After): the report stays and goes again, it is not a token that is refused.
            code == 429 || code == 403 && h.retryAfter != null -> SendResult(Outcome.RETRY, code, 0, "GitHub says too many requests, wait ${h.retryAfter ?: "a while"}")
            // A token that may not open issues there, or a repository that's gone: nothing a retry fixes.
            code == 401 || code == 403 && h.remaining != "0" || code == 404 || code == 410 -> SendResult(Outcome.NOT_CONFIGURED, code, 0, "GitHub answered $code${if (said.isNotEmpty()) ": $said" else ""}")
            // A report GitHub refuses as it is (malformed) is dropped: sent again every minute it would hold back every later one.
            code == 400 || code == 413 || code == 422 -> SendResult(Outcome.REFUSED, code, 0, "GitHub answered $code${if (said.isNotEmpty()) ": $said" else ""}")
            else -> SendResult(Outcome.RETRY, code, 0, "GitHub answered $code")
        }
    }

    /**
     * One report to GitHub: its issue, then its comments (a long log, in order), the file kept up to date with what is done so a retry
     * goes on where it stopped. A report GitHub refuses for its size is sent once more cut short before it is given up. Plain Kotlin
     * with [open] for the connection, unit-tested.
     */
    fun sendDetailed(
        file: File, repo: String, token: String, api: String = "https://api.github.com",
        open: (URL) -> HttpURLConnection = { it.openConnection() as HttpURLConnection }, gapMs: Long = COMMENT_GAP_MS,
    ): SendResult {
        if (repo.isEmpty() || token.isEmpty()) return SendResult(Outcome.NOT_CONFIGURED, 0, 0, "this build has no report token")
        var report = runCatching { Report.fromJson(JSONObject(file.readText())) }.getOrElse {
            file.delete()
            return SendResult(Outcome.SENT, 0, 0, "unreadable report dropped")
        }
        if (report.issue == 0) {
            var result = classify(post("$api/repos/$repo/issues", report.issueJson(), token, open))
            if (result.outcome == Outcome.REFUSED && report.body.length > SHRUNK) {
                val smaller = report.copy(body = report.body.take(SHRUNK) + "\n\n_(cut: GitHub refused the full text, ${result.code})_")
                result = classify(post("$api/repos/$repo/issues", smaller.issueJson(), token, open))
            }
            if (result.outcome != Outcome.SENT) return result
            report = report.copy(issue = result.issue)
            if (report.comments.isEmpty()) return result
            // (the answer had no issue number: the comments cannot be put anywhere)
            if (report.issue == 0) return result.copy(detail = "the answer named no issue: ${report.comments.size} comments not sent")
            runCatching { file.writeText(report.toJson().toString()) }
        }
        for (i in report.done until report.comments.size) {
            if (i > report.done && gapMs > 0) Thread.sleep(gapMs)
            val result = classify(post("$api/repos/$repo/issues/${report.issue}/comments", JSONObject().put("body", report.comments[i].take(MAX_ISSUE)).toString(), token, open))
            when (result.outcome) {
                // (a comment GitHub refuses is skipped: the rest still go)
                Outcome.SENT, Outcome.REFUSED -> { report = report.copy(done = i + 1); runCatching { file.writeText(report.toJson().toString()) } }
                else -> return result.copy(issue = report.issue, detail = "issue #${report.issue} is open, comment ${i + 1} of ${report.comments.size} waits: ${result.detail}")
            }
        }
        return SendResult(Outcome.SENT, 201, report.issue)
    }

    /** A crash: written as a report before the app goes, sent next time it starts. */
    private fun catchCrashes(context: Context) {
        val previous = Thread.getDefaultUncaughtExceptionHandler()
        if (previous is CrashHandler) return
        Thread.setDefaultUncaughtExceptionHandler(CrashHandler(context, previous))
    }

    private class CrashHandler(private val context: Context, private val previous: Thread.UncaughtExceptionHandler?) : Thread.UncaughtExceptionHandler {
        override fun uncaughtException(thread: Thread, error: Throwable) {
            runCatching {
                val top = error.stackTrace.firstOrNull { it.className.startsWith("com.logie") } ?: error.stackTrace.firstOrNull()
                val where = top?.let { "${it.className.substringAfterLast('.')}.${it.methodName}" } ?: "unknown"
                SessionLog.event("app", "CRASH on thread ${thread.name}: ${error.javaClass.name}: ${error.message.orEmpty()}\n${error.stackTraceToString().lineSequence().take(25).joinToString("\n")}")
                // (the crash reports itself next start: the run's log, the end of it, goes with it as comments)
                val comments = runCatching { chunks("Log of the run that crashed (newest last; UTC)", redact(SessionLog.tail(120_000))) }.getOrDefault(emptyList())
                queue(dir(context), Report(
                    "Crash: ${error.javaClass.simpleName} in $where",
                    body("Crash", "${error.javaClass.name}: ${error.message.orEmpty()}", listOf("Thread" to thread.name), error.stackTraceToString()),
                    comments = comments,
                ))
            }
            previous?.uncaughtException(thread, error)
        }
    }

    private fun sha(text: String): String =
        MessageDigest.getInstance("SHA-256").digest(text.toByteArray()).take(8).joinToString("") { "%02x".format(it) }
}
