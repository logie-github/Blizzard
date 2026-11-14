package com.logie.blizz.reports

import android.app.ActivityManager
import android.content.ComponentCallbacks2
import android.content.Context
import android.content.res.Configuration
import android.os.BatteryManager
import android.os.Build
import android.os.Debug
import android.os.PowerManager
import android.os.Process
import android.os.SystemClock
import java.io.File
import java.util.concurrent.TimeUnit

/**
 * What the phone itself says about a run, for the logs and the reports: memory, the processes the app owns (the app, Wine's
 * programs, the realm's servers: Android lets a program see only its own), the heat, the battery, and Android's own log of
 * this app. A game that vanishes, a window that goes black, a program that ends "by itself": on this phone each of those can be
 * the system ending it for memory or heat, and none of them leaves a word in Wine's output (the phone's reports of 12 and
 * 13 November 2026). With these in the log, what the system did shows.
 */
object Diagnostics {
    /** One process of the app's, as `/proc/<pid>/status` and `cmdline` give it. */
    data class Proc(val pid: Int, val name: String, val rssKb: Long, val threads: Int)

    // The pure parts: unit-tested ---------------------------------------------------------------

    /** `VmRSS` (kB) and `Threads` of a `/proc/<pid>/status` text; 0 where it has none (a kernel thread). */
    fun parseStatus(text: String): Pair<Long, Int> {
        var rss = 0L
        var threads = 0
        for (line in text.lineSequence()) {
            when {
                line.startsWith("VmRSS:") -> rss = line.removePrefix("VmRSS:").trim().substringBefore(' ').toLongOrNull() ?: 0L
                line.startsWith("Threads:") -> threads = line.removePrefix("Threads:").trim().toIntOrNull() ?: 0
            }
        }
        return rss to threads
    }

    /**
     * A process's name for a log: the program in its command line (Wine rewrites it to the Windows program's path:
     * `F:\client\_forever_\Wow.exe -config x` is `Wow.exe`), else the kernel's short name.
     */
    fun processName(cmdline: String, comm: String): String {
        val first = cmdline.substringBefore('\u0000').trim().substringBefore(' ')
        val base = first.substringAfterLast('\\').substringAfterLast('/')
        return (base.ifEmpty { comm.trim() }).take(40)
    }

    /** `/proc/meminfo` as a map of its lines' numbers (kB). */
    fun parseMeminfo(text: String): Map<String, Long> = text.lineSequence().mapNotNull { line ->
        val key = line.substringBefore(':', "").trim()
        val value = line.substringAfter(':', "").trim().substringBefore(' ').toLongOrNull()
        if (key.isEmpty() || value == null) null else key to value
    }.toMap()

    /** Programs that only pass by (this app's own helpers): left out of the lists. */
    private val PASSING = setOf("logcat", "sh", "getprop", "ps", "cat", "grep", "toybox", "dumpsys", "mksh")

    fun passing(name: String) = name in PASSING

    /** The sample line of the run's log: memory first, the biggest processes, heat and battery. */
    fun sampleLine(
        availMb: Long, totalMb: Long, lowMemory: Boolean, thresholdMb: Long, swapFreeMb: Long?, appPssMb: Long,
        procs: List<Proc>, thermal: Int?, battery: Int?,
    ): String = buildString {
        append("mem avail $availMb/$totalMb MB")
        append(if (lowMemory) " LOW (threshold $thresholdMb)" else " ok")
        if (swapFreeMb != null) append(", swap free $swapFreeMb MB")
        append(" | app pss $appPssMb MB")
        val total = procs.sumOf { it.rssKb } / 1024
        append(" | ${procs.size} procs $total MB")
        if (procs.isNotEmpty()) {
            val top = procs.sortedByDescending { it.rssKb }
            append(": ").append(top.take(5).joinToString(", ") { "${it.name} ${it.rssKb / 1024}" })
            if (top.size > 5) append(", +${top.size - 5}")
        }
        if (thermal != null) append(" | thermal $thermal")
        if (battery != null) append(" | batt $battery%")
    }

    /** Programs that appeared (`+`) or went (`-`, with the last size seen) between two looks; the passing ones are left out. */
    fun changes(before: Map<Int, Proc>, now: List<Proc>): List<String> {
        val current = now.filter { !passing(it.name) }.associateBy { it.pid }
        val out = ArrayList<String>()
        for ((pid, p) in current) if (pid !in before) out += "+ ${p.name} (pid $pid, ${p.rssKb / 1024} MB, ${p.threads} threads)"
        for ((pid, p) in before) if (pid !in current) out += "- ${p.name} (pid $pid, last seen ${p.rssKb / 1024} MB)"
        return out
    }

    fun thermalName(status: Int) = when (status) {
        0 -> "none"; 1 -> "light"; 2 -> "moderate"; 3 -> "severe"; 4 -> "critical"; 5 -> "emergency"; 6 -> "shutdown"
        else -> "$status"
    }

    fun trimName(level: Int) = when (level) {
        ComponentCallbacks2.TRIM_MEMORY_COMPLETE -> "COMPLETE (about to be killed)"
        ComponentCallbacks2.TRIM_MEMORY_MODERATE -> "MODERATE"
        ComponentCallbacks2.TRIM_MEMORY_BACKGROUND -> "BACKGROUND"
        ComponentCallbacks2.TRIM_MEMORY_UI_HIDDEN -> "UI_HIDDEN"
        ComponentCallbacks2.TRIM_MEMORY_RUNNING_CRITICAL -> "RUNNING_CRITICAL (the system is nearly out of memory)"
        ComponentCallbacks2.TRIM_MEMORY_RUNNING_LOW -> "RUNNING_LOW"
        ComponentCallbacks2.TRIM_MEMORY_RUNNING_MODERATE -> "RUNNING_MODERATE"
        else -> "$level"
    }

    // What the phone says ---------------------------------------------------------------------------

    /** The app's own processes now (only the app's are visible to it), without the passing helpers. */
    fun readProcesses(proc: File = File("/proc"), self: Int = Process.myPid()): List<Proc> {
        val pids = proc.list { dir, name -> name.all { it.isDigit() } && File(dir, name).isDirectory } ?: return emptyList()
        val out = ArrayList<Proc>()
        for (name in pids) {
            val pid = name.toInt()
            runCatching {
                val dir = File(proc, name)
                val (rss, threads) = parseStatus(File(dir, "status").readText())
                if (rss <= 0L) return@runCatching
                val cmd = runCatching { File(dir, "cmdline").readText() }.getOrDefault("")
                val comm = runCatching { File(dir, "comm").readText() }.getOrDefault("")
                out += Proc(pid, if (pid == self) "app" else processName(cmd, comm), rss, threads)
            }
        }
        return out
    }

    private fun readFile(path: String): String? = runCatching { File(path).readText() }.getOrNull()

    private fun thermal(context: Context): Int? =
        if (Build.VERSION.SDK_INT >= 29) runCatching { context.getSystemService(PowerManager::class.java)?.currentThermalStatus }.getOrNull() else null

    private fun battery(context: Context): Int? =
        runCatching { context.getSystemService(BatteryManager::class.java)?.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY) }
            .getOrNull()?.takeIf { it in 0..100 }

    /** One look: the sample line, and the processes it was made from. */
    fun sample(context: Context): Pair<String, List<Proc>> {
        val info = ActivityManager.MemoryInfo()
        runCatching { context.getSystemService(ActivityManager::class.java)?.getMemoryInfo(info) }
        val meminfo = readFile("/proc/meminfo")?.let { parseMeminfo(it) }.orEmpty()
        val avail = (meminfo["MemAvailable"] ?: (info.availMem / 1024)) / 1024
        val total = (meminfo["MemTotal"] ?: (info.totalMem / 1024)) / 1024
        val procs = readProcesses().filter { !passing(it.name) }
        val pss = runCatching { Debug.getPss() / 1024 }.getOrDefault(0L)
        return sampleLine(avail, total, info.lowMemory, info.threshold / (1024 * 1024), meminfo["SwapFree"]?.div(1024), pss, procs, thermal(context), battery(context)) to procs
    }

    /** The phone's state in words, for the head of a report. */
    fun deviceState(context: Context): String = buildString {
        val (line, procs) = sample(context)
        appendLine(line)
        appendLine("free storage: ${File(context.filesDir.path).usableSpace / (1024 * 1024)} MB")
        val metrics = context.resources.displayMetrics
        appendLine("screen: ${metrics.widthPixels}x${metrics.heightPixels} at ${metrics.densityDpi} dpi")
        appendLine("processes:")
        procs.sortedByDescending { it.rssKb }.take(25).forEach { appendLine("  ${it.name} (pid ${it.pid}) ${it.rssKb / 1024} MB, ${it.threads} threads") }
        val sends = BugReports.history(context, 6)
        if (sends.isNotEmpty()) {
            appendLine("recent report sends:")
            sends.forEach { appendLine("  $it") }
        }
    }

    /**
     * Android's own log of this app (warnings and up): a native crash's "Fatal signal", the runtime's complaints. An app sees only
     * its own lines; the lines of an earlier run of the same app are in it while the system keeps them.
     */
    fun logcat(maxLines: Int = 600, timeoutMs: Long = 5_000): String = runCatching {
        val process = ProcessBuilder("logcat", "-d", "-v", "threadtime", "-t", "4000", "*:W").redirectErrorStream(true).start()
        var text = ""
        val reader = Thread { text = runCatching { process.inputStream.bufferedReader().readText() }.getOrDefault("") }
        reader.start()
        reader.join(timeoutMs)
        if (reader.isAlive) { process.destroy(); reader.join(500) }
        runCatching { process.waitFor(500, TimeUnit.MILLISECONDS) }
        text.lines().filter { it.isNotBlank() }.takeLast(maxLines).joinToString("\n")
    }.getOrDefault("")

    /** What a report that explains a run carries as comments: the run's log and Android's. Each is split to fit ([BugReports.chunks]). */
    fun attachments(context: Context): List<Pair<String, String>> {
        val out = ArrayList<Pair<String, String>>()
        val run = SessionLog.tail(180_000)
        if (run.isNotBlank()) out += "Log of this run (newest last; UTC)" to run
        val android = logcat()
        if (android.isNotBlank()) out += "Android's log of this app (warnings and up)" to android
        return out
    }

    // The sampler ----------------------------------------------------------------------------------

    @Volatile private var sampler: Thread? = null

    /**
     * Once, as the app starts: a look at memory and processes every few seconds while anything of the app's runs besides the app
     * (Wine, the realm) or a game is up, a heartbeat every ten minutes otherwise, into the run's log. Programs starting and ending
     * are written as they are seen; the system's calls to give memory back and heat changes are written as they come; the session
     * keeper's lines are copied in (its own file is made anew at each start). Never raises: a failure ends the sampling.
     */
    @Synchronized fun startSampler(context: Context) {
        if (sampler != null) return
        val app = context.applicationContext
        runCatching {
            app.registerComponentCallbacks(object : ComponentCallbacks2 {
                override fun onTrimMemory(level: Int) { SessionLog.event("res", "the system asks for memory back: ${trimName(level)}") }
                override fun onLowMemory() { SessionLog.event("res", "the system is low on memory (onLowMemory)") }
                override fun onConfigurationChanged(newConfig: Configuration) {}
            })
        }
        if (Build.VERSION.SDK_INT >= 29) runCatching {
            app.getSystemService(PowerManager::class.java)?.addThermalStatusListener(app.mainExecutor) { status ->
                SessionLog.event("res", "heat: ${thermalName(status)} ($status)")
            }
        }
        sampler = Thread({ loop(app) }, "blizz-sampler").apply { isDaemon = true; start() }
    }

    private fun loop(app: Context) {
        var before = emptyMap<Int, Proc>()
        var activeSince = 0L
        var wroteAt = 0L
        var keeperAt = 0L
        var keeperName: String? = null
        val self = Process.myPid()
        while (true) {
            runCatching {
                val now = SystemClock.elapsedRealtime()
                val procs = readProcesses(self = self).filter { !passing(it.name) }
                val others = procs.filter { it.pid != self }
                val active = others.isNotEmpty() || runCatching { com.logie.blizz.selftest.RunningGame.alive() }.getOrDefault(false)
                if (!active) activeSince = 0L else if (activeSince == 0L) activeSince = now
                changes(before, procs.filter { it.pid != self }).forEach { SessionLog.event("res", it) }
                before = others.associateBy { it.pid }
                val every = when {
                    !active -> HEARTBEAT_MS
                    now - activeSince < FAST_FOR_MS -> FAST_MS
                    else -> SLOW_MS
                }
                if (now - wroteAt >= every) {
                    wroteAt = now
                    SessionLog.event("res", sample(app).first)
                }
                // The keeper's file is made anew at each session: read from where it was, from the start when it is a new one.
                val keeper = com.logie.blizz.game.GameLog.keeperLog
                if (keeper != null && keeper.isFile) {
                    if (keeper.path != keeperName || keeper.length() < keeperAt) { keeperName = keeper.path; keeperAt = 0L }
                    if (keeper.length() > keeperAt) {
                        val text = java.io.RandomAccessFile(keeper, "r").use { f ->
                            f.seek(keeperAt)
                            val bytes = ByteArray((keeper.length() - keeperAt).coerceAtMost(200_000L).toInt())
                            f.readFully(bytes)
                            keeperAt += bytes.size
                            String(bytes, Charsets.ISO_8859_1)
                        }
                        text.lineSequence().filter { it.isNotBlank() }.forEach { SessionLog.event("keeper", it) }
                    }
                }
            }
            try { Thread.sleep(if (activeSince != 0L) LOOK_MS else IDLE_LOOK_MS) } catch (_: InterruptedException) { return }
        }
    }

    private const val LOOK_MS = 2_000L
    /** Nothing of the app's runs but the app: a look now and then, only to see a game or its programs start. */
    private const val IDLE_LOOK_MS = 5_000L
    private const val FAST_MS = 5_000L
    private const val FAST_FOR_MS = 180_000L
    private const val SLOW_MS = 20_000L
    private const val HEARTBEAT_MS = 600_000L
}

/**
 * Why the app's last process ended, as Android keeps it (API 30 and up): read at each start, written to the run's log, and
 * reported when the system ended it (it ran out of memory, killed it with a signal, a native crash, a hang). A process the
 * system ended leaves nothing of its own: no crash, no log line (the phone, 12 and 13 November 2026: the launcher's window went,
 * the game ended).
 */
object ExitReasons {
    fun name(reason: Int) = when (reason) {
        0 -> "UNKNOWN"; 1 -> "EXIT_SELF"; 2 -> "SIGNALED"; 3 -> "LOW_MEMORY"; 4 -> "CRASH"; 5 -> "CRASH_NATIVE"; 6 -> "ANR"
        7 -> "INITIALIZATION_FAILURE"; 8 -> "PERMISSION_CHANGE"; 9 -> "EXCESSIVE_RESOURCE_USAGE"; 10 -> "USER_REQUESTED"
        11 -> "USER_STOPPED"; 12 -> "DEPENDENCY_DIED"; 13 -> "OTHER"; 14 -> "FREEZER"; 15 -> "PACKAGE_STATE_CHANGE"; 16 -> "PACKAGE_UPDATED"
        else -> "reason $reason"
    }

    /**
     * Whether an end is a fault worth a report: the system's kills and the crashes it saw. Not the app leaving by itself, the
     * person closing it, an update (Java crashes are reported by the crash handler itself).
     */
    fun worthReporting(reason: Int) = reason in setOf(2, 3, 5, 6, 7, 9, 12, 14)

    fun importanceName(importance: Int) = when {
        importance <= 100 -> "foreground"
        importance <= 125 -> "foreground service"
        importance <= 200 -> "visible"
        importance <= 300 -> "service"
        importance <= 400 -> "cached"
        else -> "$importance"
    }

    fun describe(reason: Int, status: Int, importance: Int, pssKb: Long, rssKb: Long, at: Long, process: String, description: String?): String =
        "${java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss", java.util.Locale.US).apply { timeZone = java.util.TimeZone.getTimeZone("UTC") }.format(java.util.Date(at))} UTC " +
            "process '$process' ended: ${name(reason)} (status $status), was ${importanceName(importance)}, " +
            "pss ${pssKb / 1024} MB, rss ${rssKb / 1024} MB" + (description?.takeIf { it.isNotBlank() }?.let { ", \"$it\"" } ?: "")

    /** The ends since the last look, newest first, written to the log; those worth it become reports (at most three). */
    fun check(context: Context) {
        if (Build.VERSION.SDK_INT < 30) return
        val app = context.applicationContext
        runCatching {
            val prefs = app.getSharedPreferences("exit-reasons", Context.MODE_PRIVATE)
            val seen = prefs.getLong("seen", 0L)
            val floor = if (seen > 0L) seen else System.currentTimeMillis() - 24L * 3600 * 1000
            val infos = app.getSystemService(ActivityManager::class.java)?.getHistoricalProcessExitReasons(app.packageName, 0, 10).orEmpty()
                .filter { it.timestamp > floor }
            if (infos.isEmpty()) return@runCatching
            prefs.edit().putLong("seen", infos.maxOf { it.timestamp }).apply()
            var reported = 0
            for (i in infos) {
                val line = describe(i.reason, i.status, i.importance, i.pss, i.rss, i.timestamp, i.processName, i.description)
                SessionLog.event("exit", line)
                if (worthReporting(i.reason) && reported < 3) {
                    reported++
                    val before = SessionLog.previousTail(150_000)
                    BugReports.report(
                        app, "App process ended by the system", "${name(i.reason)}: $line",
                        listOf("Reason" to name(i.reason), "Status" to i.status.toString(), "Importance" to importanceName(i.importance), "Process" to i.processName),
                        log = before.takeLast(18_000).ifBlank { null },
                        attach = true, force = true,
                        comments = if (before.isNotBlank()) listOf("Log of the run that ended (newest last; UTC)" to before) else emptyList(),
                    )
                }
            }
        }
    }
}
