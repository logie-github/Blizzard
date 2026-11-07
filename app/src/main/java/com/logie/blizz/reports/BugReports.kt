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
    /** A failure to send: its title (also what makes two the same failure) and its body. */
    data class Report(val title: String, val body: String, val label: String = "auto-report") {
        val key: String get() = sha(title.replace(Regex("\\d+"), "#"))

        fun toJson(): JSONObject = JSONObject().put("title", title).put("body", body).put("label", label)

        /** What GitHub's issues API is sent. */
        fun issueJson(): String = JSONObject().put("title", title).put("body", body).put("labels", JSONArray(listOf("bug", label))).toString()

        companion object {
            fun fromJson(o: JSONObject) = Report(o.getString("title"), o.getString("body"), o.optString("label", "auto-report"))
        }
    }

    enum class Outcome { SENT, RETRY, NOT_CONFIGURED }

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
        catchCrashes(app)
        sendSoon(app)
    }

    /** A failure the app met: queued, then sent. */
    fun report(context: Context, what: String, message: String, details: List<Pair<String, String?>> = emptyList(), log: String? = null, files: String? = null) {
        val app = context.applicationContext
        val report = Report("$what: ${message.lineSequence().first().take(140)}", body(what, message, details, log, files))
        // (a full phone is the usual reason an import failed: the report must not be what crashes the app)
        if (runCatching { queue(dir(app), report) }.getOrDefault(false)) sendSoon(app)
    }

    /** A report that is sent whatever came before (the launch test's): kept on the phone until GitHub takes it. False when this build has no token. */
    fun submit(context: Context, report: Report): Boolean {
        val app = context.applicationContext
        val d = dir(app).also { it.mkdirs() }
        runCatching { File(d, "${report.key}-${System.currentTimeMillis()}.json").writeText(report.toJson().toString()) }
        sendSoon(app)
        return configured(app)
    }

    /** Writes [report] to [dir], unless the same failure went in the last day. Plain Kotlin, unit-tested. */
    fun queue(dir: File, report: Report, now: Long = System.currentTimeMillis()): Boolean {
        dir.mkdirs()
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

    /** The issue's text: what failed, what the app said, its details, the device, the end of the log. */
    fun body(what: String, message: String, details: List<Pair<String, String?>>, log: String?, files: String? = null): String = buildString {
        append("**$what**\n\n")
        append(message.trim()).append("\n\n")
        append("| | |\n| --- | --- |\n")
        append("| App | Blizzard ${BuildConfig.VERSION_NAME} (${BuildConfig.VERSION_CODE}) |\n")
        append("| Device | ${Build.MANUFACTURER} ${Build.MODEL} |\n")
        append("| Android | ${Build.VERSION.RELEASE} (API ${Build.VERSION.SDK_INT}) |\n")
        for ((name, value) in details) if (!value.isNullOrBlank()) append("| $name | ${value.replace("|", "\\|").replace("\n", " ")} |\n")
        if (!log.isNullOrBlank()) {
            append("\n<details><summary>Log</summary>\n\n```\n")
            append(redact(log).takeLast(12_000))
            append("\n```\n</details>\n")
        }
        if (!files.isNullOrBlank()) {
            append("\n<details><summary>Files (paths, sizes, hashes; never their content)</summary>\n\n```\n")
            append(redact(files).take(40_000))
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
                        when (send(file, repo, token(context))) {
                            Outcome.SENT -> { file.delete(); if (waiting.size > 1) delay(SEND_GAP_MS) }
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

    /** One report to GitHub. Plain Kotlin with [open] for the connection, unit-tested. */
    fun send(file: File, repo: String, token: String, api: String = "https://api.github.com", open: (URL) -> HttpURLConnection = { it.openConnection() as HttpURLConnection }): Outcome {
        if (repo.isEmpty() || token.isEmpty()) return Outcome.NOT_CONFIGURED
        val report = runCatching { Report.fromJson(JSONObject(file.readText())) }.getOrElse {
            file.delete()
            return Outcome.SENT
        }
        return try {
            val c = open(URL("$api/repos/$repo/issues"))
            c.requestMethod = "POST"
            c.doOutput = true
            c.connectTimeout = 15_000
            c.readTimeout = 30_000
            c.setRequestProperty("Authorization", "Bearer $token")
            c.setRequestProperty("Accept", "application/vnd.github+json")
            c.setRequestProperty("Content-Type", "application/json")
            c.setRequestProperty("User-Agent", "Blizzard-Android/${BuildConfig.VERSION_NAME}")
            c.outputStream.use { it.write(report.issueJson().toByteArray()) }
            val code = c.responseCode
            runCatching { (if (code < 400) c.inputStream else c.errorStream)?.close() }
            when {
                code in 200..299 -> Outcome.SENT
                // GitHub's "too many requests too fast" (a secondary rate limit: 403 or 429 with Retry-After): the report stays and goes again, it is not a token that is refused.
                code == 429 || code == 403 && c.getHeaderField("Retry-After") != null -> Outcome.RETRY
                // A token that may not open issues there, or a repository that's gone: nothing a retry fixes.
                code == 401 || code == 403 && c.getHeaderField("X-RateLimit-Remaining") != "0" || code == 404 || code == 410 -> Outcome.NOT_CONFIGURED
                // A report GitHub refuses as it is (too long, malformed) is dropped: sent again every minute it would hold back every later one.
                code == 400 || code == 413 || code == 422 -> Outcome.SENT
                else -> Outcome.RETRY
            }
        } catch (e: IOException) {
            Outcome.RETRY
        }
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
                queue(dir(context), Report(
                    "Crash: ${error.javaClass.simpleName} in $where",
                    body("Crash", "${error.javaClass.name}: ${error.message.orEmpty()}", listOf("Thread" to thread.name), error.stackTraceToString()),
                ))
            }
            previous?.uncaughtException(thread, error)
        }
    }

    private fun sha(text: String): String =
        MessageDigest.getInstance("SHA-256").digest(text.toByteArray()).take(8).joinToString("") { "%02x".format(it) }
}
