package com.logie.blizz.selftest

import android.content.Context
import android.os.Build
import com.logie.blizz.BuildConfig
import com.logie.blizz.Games
import com.logie.blizz.game.GameLog
import com.logie.blizz.game.StratagusRuntime
import com.logie.blizz.game.WindowsRuntime
import com.logie.blizz.game.WowPlay
import com.logie.blizz.importer.GameImportManager
import com.logie.blizz.importer.LaunchTest
import com.logie.blizz.importer.LibraryEntry
import com.logie.blizz.reports.BugReports
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File

/**
 * The launch test: the first time the app starts after an update (and from the settings), every game
 * on the shelf is looked at (is it installed, did its import finish, what stopped it) and each installed
 * one is started, watched until its first window is up (or it fails or times out), then closed. The
 * result is a report: saved on the phone, shown to copy, and sent to GitHub as an issue when this build
 * can ([BugReports]). If the app itself dies during a game, the next start reports what had been done
 * and which game it died on.
 */
object SelfTest {
    data class Target(val gameId: String, val title: String)

    /** What starting a game came to. */
    data class LaunchOutcome(
        val launch: Launch, val detail: String, val preparedSeconds: Int? = null, val windowSeconds: Int? = null, val log: String? = null,
    )

    /** Starts [entry] and watches it come up (or not); closes it again. */
    fun interface Probe { suspend fun launch(entry: LibraryEntry): LaunchOutcome }

    sealed interface State {
        data object Idle : State
        data class Running(val index: Int, val total: Int, val current: String, val done: List<GameResult>) : State
        data class Finished(val results: List<GameResult>, val markdown: String, val sent: Sent) : State
    }

    enum class Sent { SENT_LATER, NO_TOKEN }

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)
    private val _state = MutableStateFlow<State>(State.Idle)
    val state: StateFlow<State> = _state
    private var job: Job? = null

    private const val PREFS = "selftest"

    /** The games the test goes through: every installable game and each of its versions. */
    fun targets(): List<Target> = Games.all.flatMap { listOf(it) + it.variants }
        .filter { GameImportManager.importable(it.id) }.map { Target(it.id, it.fullTitle) }

    /** At app start: a test the app died in (while the person ran it) is reported; nothing is started. */
    fun reportInterruptedOnly(context: Context) = reportInterrupted(context.applicationContext)

    /** Runs the test now (the settings' button too); does nothing while one runs. */
    fun start(context: Context) {
        if (job?.isActive == true) return
        val app = context.applicationContext
        app.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().putInt("version", BuildConfig.VERSION_CODE).apply()
        job = scope.launch {
            val results = runAll(
                targets(),
                inspect = { t -> withContext(Dispatchers.IO) { inspect(app, t) } },
                probe = AndroidProbe(app),
                progress = { i, total, current, done ->
                    _state.value = State.Running(i, total, current, done)
                    saveProgress(app, done, current)
                },
            )
            finish(app, results)
        }
    }

    fun cancel(context: Context? = null) {
        job?.cancel()
        RunningGame.finish()
        // Stopped by the person: not a test the app died in.
        context?.let { File(dir(it), "partial.json").delete() }
        _state.value = State.Idle
    }

    fun dismiss() {
        if (_state.value is State.Finished) _state.value = State.Idle
    }

    /** Runs through [targets]: inspected first, started when installed. Plain Kotlin apart from the callbacks, unit-tested. */
    suspend fun runAll(
        targets: List<Target>,
        inspect: suspend (Target) -> Pair<Inspection, LibraryEntry?>,
        probe: Probe,
        progress: (index: Int, total: Int, current: String, done: List<GameResult>) -> Unit = { _, _, _, _ -> },
    ): List<GameResult> {
        val results = ArrayList<GameResult>()
        targets.forEachIndexed { i, t ->
            progress(i, targets.size, t.title, results.toList())
            val (inspection, entry) = inspect(t)
            results += if (inspection.install == Install.INSTALLED && entry != null) {
                val o = try {
                    probe.launch(entry)
                } catch (e: kotlinx.coroutines.CancellationException) {
                    throw e
                } catch (e: Exception) {
                    LaunchOutcome(Launch.FAILED, "The test itself failed: ${e.message ?: e.javaClass.simpleName}", log = e.stackTraceToString())
                }
                GameResult(t.gameId, t.title, inspection.install, inspection.detail, o.launch, o.detail, o.preparedSeconds, o.windowSeconds, o.log)
            } else GameResult(t.gameId, t.title, inspection.install, inspection.detail)
        }
        progress(targets.size, targets.size, "", results.toList())
        return results
    }

    private fun inspect(context: Context, t: Target): Pair<Inspection, LibraryEntry?> {
        val record = GameImportManager.repo(context).load(t.gameId)
        val entry = GameImportManager.library(context).get(t.gameId)
        val exists = entry != null && File(entry.installPath, entry.executable.ifEmpty { "extracted" }).isFile ||
            entry != null && entry.runtime == LibraryEntry.RUNTIME_EXTERNAL
        return SelfTestReport.inspect(record, entry, exists) to entry
    }

    private fun header(): List<Pair<String, String>> = listOf(
        "App" to "Blizzard ${BuildConfig.VERSION_NAME} (${BuildConfig.VERSION_CODE})",
        "Device" to "${Build.MANUFACTURER} ${Build.MODEL}",
        "Android" to "${Build.VERSION.RELEASE} (API ${Build.VERSION.SDK_INT})",
        "When" to java.time.Instant.now().toString(),
    )

    private fun dir(context: Context) = File(context.filesDir, "selftest").also { it.mkdirs() }

    private fun saveProgress(context: Context, done: List<GameResult>, current: String) {
        runCatching { File(dir(context), "partial.json").writeText(org.json.JSONObject().put("done", GameResult.listToJson(done)).put("current", current).toString()) }
    }

    private fun finish(context: Context, results: List<GameResult>) {
        File(dir(context), "partial.json").delete()
        val version = BuildConfig.VERSION_NAME
        val markdown = SelfTestReport.markdown(results, header(), redact = BugReports::redact)
        runCatching { File(dir(context), "report.md").writeText(markdown) }
        BugReports.submit(context, BugReports.Report(SelfTestReport.title(version, results), markdown, label = "launch-test"))
        _state.value = State.Finished(results, markdown, if (BugReports.configured(context)) Sent.SENT_LATER else Sent.NO_TOKEN)
    }

    /** The app died during a test: what was done goes out, naming the game it died on. */
    private fun reportInterrupted(context: Context) {
        val partial = File(dir(context), "partial.json")
        if (!partial.isFile) return
        runCatching {
            val o = org.json.JSONObject(partial.readText())
            val done = GameResult.listFromJson(o.optString("done", "[]"))
            val current = o.optString("current")
            partial.delete()
            if (current.isBlank()) return
            val markdown = SelfTestReport.markdown(done, header(), interruptedAt = current, redact = BugReports::redact)
            runCatching { File(dir(context), "report.md").writeText(markdown) }
            BugReports.submit(context, BugReports.Report("Launch test ${BuildConfig.VERSION_NAME}: the app stopped while testing $current", markdown, label = "launch-test"))
        }
    }

    /** The probes on a phone. */
    private class AndroidProbe(private val context: Context) : Probe {
        override suspend fun launch(entry: LibraryEntry): LaunchOutcome = when {
            entry.runtime == LibraryEntry.RUNTIME_D2R || entry.runtime == LibraryEntry.RUNTIME_PENDING ->
                LaunchOutcome(Launch.NOT_TESTED, "Imported; running it in the app isn't built yet.")
            entry.runtime == StratagusRuntime.RUNTIME -> stratagus(entry)
            entry.runtime == LibraryEntry.RUNTIME_EXTERNAL -> wow(entry)
            else -> windows(entry)
        }

        private fun now() = System.currentTimeMillis()

        private fun seconds(since: Long) = ((now() - since) / 1000).toInt()

        private suspend fun waitWindow(id: String, started: Long, timeoutMs: Long, failure: () -> String?, prepared: () -> Int?): LaunchOutcome {
            val repo = GameImportManager.repo(context)
            var preparedAt: Int? = null
            while (now() - started < timeoutMs) {
                if (preparedAt == null) preparedAt = prepared()
                if (repo.load(id).launchTest == LaunchTest.WINDOW_SHOWN) {
                    val window = seconds(started)
                    // Let the game run a moment: a window that vanishes at once is a crash, not a launch.
                    delay(SETTLE_MS)
                    val stayed = RunningGame.alive()
                    val log = GameLog.snapshot()
                    RunningGame.finish()
                    return if (stayed) LaunchOutcome(Launch.OK, "The game's window came up and stayed for ${SETTLE_MS / 1000} s.", preparedAt, window, log)
                    else LaunchOutcome(Launch.FAILED, "The window came up and the game closed within ${SETTLE_MS / 1000} s.", preparedAt, window, log)
                }
                failure()?.let { why ->
                    val log = GameLog.snapshot()
                    RunningGame.finish()
                    return LaunchOutcome(Launch.FAILED, why, preparedAt, null, log)
                }
                delay(500)
            }
            val log = GameLog.snapshot()
            RunningGame.finish()
            return LaunchOutcome(Launch.TIMED_OUT, "No window after ${timeoutMs / 1000} s.", preparedAt, null, log)
        }

        private suspend fun windows(entry: LibraryEntry): LaunchOutcome {
            GameImportManager.recordLaunch(context, entry.gameId, LaunchTest.NOT_RUN)
            val started = now()
            withContext(Dispatchers.Main) { WindowsRuntime.play(context, entry) }
            return waitWindow(
                entry.gameId, started, WINDOWS_TIMEOUT_MS,
                failure = { (WindowsRuntime.state.value as? WindowsRuntime.State.Failed)?.message?.also { WindowsRuntime.dismiss() } },
                prepared = { if (WindowsRuntime.state.value is WindowsRuntime.State.Idle && now() - started > 1500) seconds(started) else null },
            )
        }

        private suspend fun wow(entry: LibraryEntry): LaunchOutcome {
            GameImportManager.recordLaunch(context, WowPlay.GAME_ID, LaunchTest.NOT_RUN)
            val started = now()
            withContext(Dispatchers.Main) { WowPlay.play(context, entry) }
            val outcome = waitWindow(
                WowPlay.GAME_ID, started, WowPlay.REALM_TIMEOUT_MS + WINDOWS_TIMEOUT_MS,
                failure = {
                    (WowPlay.state.value as? WowPlay.State.Failed)?.message?.also { WowPlay.dismiss() }
                        ?: (WindowsRuntime.state.value as? WindowsRuntime.State.Failed)?.message?.also { WindowsRuntime.dismiss() }
                },
                prepared = { if (WowPlay.state.value is WowPlay.State.Idle && now() - started > 1500) seconds(started) else null },
            )
            com.logie.blizz.wow.WowRealm.stop(context)
            return outcome
        }

        /** Stratagus runs in a process of its own (`:stratagus`), which writes its pid to `running`: watched and closed through that. */
        private suspend fun stratagus(entry: LibraryEntry): LaunchOutcome {
            val dir = File(entry.installPath)
            val running = File(dir, "running")
            running.delete()
            val started = now()
            withContext(Dispatchers.Main) { StratagusRuntime.play(context, entry) }
            while (now() - started < STRATAGUS_TIMEOUT_MS && !running.isFile) delay(500)
            val pid = runCatching { running.readText().trim().toInt() }.getOrNull()
            if (pid == null) return LaunchOutcome(Launch.TIMED_OUT, "The game never wrote its running marker in ${STRATAGUS_TIMEOUT_MS / 1000} s.")
            val up = seconds(started)
            delay(SETTLE_MS)
            val stayed = File("/proc/$pid").exists()
            // Ended by the test, not by the game: the marker goes too, or the next start would report it as a stop.
            runCatching { android.os.Process.killProcess(pid) }
            delay(1000)
            running.delete()
            return if (stayed) LaunchOutcome(Launch.OK, "Stratagus started and stayed up for ${SETTLE_MS / 1000} s.", up, up)
            else LaunchOutcome(Launch.FAILED, "Stratagus started and stopped within ${SETTLE_MS / 1000} s.", up, up)
        }
    }

    private const val SETTLE_MS = 10_000L
    private const val WINDOWS_TIMEOUT_MS = 8 * 60_000L
    private const val STRATAGUS_TIMEOUT_MS = 90_000L
}
