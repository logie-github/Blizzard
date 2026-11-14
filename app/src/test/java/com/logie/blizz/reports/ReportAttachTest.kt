package com.logie.blizz.reports

import android.app.ActivityManager
import android.content.Context
import com.logie.blizz.game.GameLog
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment
import org.robolectric.Shadows.shadowOf
import org.robolectric.annotation.Config
import java.io.File

/** The real path of a report that has to explain a run: the run's log started, the phone's state read, the comments queued. */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class ReportAttachTest {
    private fun queued(app: Context) = BugReports.dir(app).listFiles { f -> f.name.endsWith(".json") }.orEmpty()
        .map { BugReports.Report.fromJson(JSONObject(it.readText())) }

    /** A report that gathers the phone's state is queued off the caller's thread: waits for [count] of them to be in the folder. */
    private fun queuedAfterWaiting(app: Context, count: Int = 1): List<BugReports.Report> {
        val end = System.currentTimeMillis() + 15_000
        while (queued(app).size < count && System.currentTimeMillis() < end) Thread.sleep(50)
        Thread.sleep(150)
        return queued(app)
    }

    @Test fun aReportThatExplainsARunCarriesThePhonesStateAndTheRunsLog() {
        val app = RuntimeEnvironment.getApplication()
        BugReports.dir(app).deleteRecursively()
        SessionLog.start(app)
        SessionLog.event("forever", "Play pressed (1828x1248)")
        GameLog.note("forever: the launcher is up; taps are clicks")
        GameLog.take("00ec:err:ole:start_rpcss Failed to start RpcSs service")
        assertTrue(BugReports.report(
            app, "WoW Forever", "The game stopped: Exception 0xC0000005", listOf("Program" to "Wow.exe"), log = "the tail",
            attach = true, force = true,
        ))
        val report = queuedAfterWaiting(app).single()
        assertEquals("WoW Forever: The game stopped: Exception 0xC0000005", report.title)
        assertTrue(report.body.contains("<summary>The phone just now</summary>"))
        assertTrue(report.body.contains("mem avail"))
        assertTrue(report.body.contains("| Program | Wow.exe |"))
        assertTrue("no comment holds the run's log: ${report.comments.map { it.take(60) }}", report.comments.any {
            it.startsWith("**Log of this run (newest last; UTC)") && it.contains("Play pressed (1828x1248)") &&
                it.contains("forever: the launcher is up") && it.contains("Failed to start RpcSs service")
        })
        // The run's log itself: its head says what ran where.
        val head = SessionLog.tail(1_000_000)
        assertTrue(head, head.contains("run started: Blizzard"))
        assertTrue(head.contains("device:"))
        assertTrue(head.contains(" app    forever: the launcher is up; taps are clicks"))
        assertTrue(head.contains(" wine   00ec:err:ole:start_rpcss"))
    }

    @Test fun aKeyInTheRunsLogDoesNotGoOut() {
        val app = RuntimeEnvironment.getApplication()
        BugReports.dir(app).deleteRecursively()
        SessionLog.start(app)
        SessionLog.event("app", "install D2DV --cdkey ABCD1234EFGH5678 token ghp_abcdef123 key 0123456789abcdef0123456789abcdef0123")
        BugReports.report(app, "Test", "with a key in the log", attach = true, force = true)
        // Not even in the file on the phone.
        val onDisk = SessionLog.tail(1_000_000)
        assertTrue(onDisk.contains("--cdkey [removed]"))
        assertFalse(onDisk.contains("ABCD1234EFGH5678"))
        assertFalse(onDisk.contains("ghp_abcdef123"))
        val text = queuedAfterWaiting(app).single().comments.joinToString("\n")
        assertTrue(text.contains("--cdkey [removed]"))
        assertFalse(text.contains("ABCD1234EFGH5678"))
        assertFalse(text.contains("ghp_abcdef123"))
        assertFalse(text.contains("0123456789abcdef0123456789abcdef0123"))
    }

    @Test fun aReportWithoutAttachIsTheOneItWasBeforeAndTheSameOneIsStillOncePerDay() {
        val app = RuntimeEnvironment.getApplication()
        BugReports.dir(app).deleteRecursively()
        assertTrue(BugReports.report(app, "Diablo import", "HTTP 503", log = "x"))
        val report = queued(app).single()
        assertEquals(emptyList<String>(), report.comments)
        assertFalse(report.body.contains("The phone just now"))
        File(BugReports.dir(app), "${report.key}.json").delete()
        assertFalse(BugReports.report(app, "Diablo import", "HTTP 502", log = "x"))
    }

    @Test fun theSystemsOwnWordOnHowTheLastRunEndedIsReadAndReportedOnce() {
        val app = RuntimeEnvironment.getApplication()
        BugReports.dir(app).deleteRecursively()
        app.getSharedPreferences("exit-reasons", Context.MODE_PRIVATE).edit().clear().apply()
        SessionLog.start(app)
        val manager = app.getSystemService(ActivityManager::class.java)
        // (Robolectric's shadow of the system's list of how this app's processes ended: one the system killed for memory, a minute ago)
        val info = org.robolectric.shadows.ShadowActivityManager.ApplicationExitInfoBuilder.newBuilder()
            .setPid(4321).setProcessName(app.packageName).setReason(3).setStatus(9).setImportance(100)
            .setPss(3_174_400).setRss(3_584_000).setDescription("kill all").setTimestamp(System.currentTimeMillis() - 60_000).build()
        shadowOf(manager).addApplicationExitInfo(info)
        ExitReasons.check(app)
        val written = SessionLog.tail(1_000_000)
        assertTrue(written, written.contains(" exit   ") && written.contains("LOW_MEMORY"))
        val reports = queuedAfterWaiting(app)
        assertEquals(reports.map { it.title }.toString(), 1, reports.size)
        assertTrue(reports[0].title.startsWith("App process ended by the system: LOW_MEMORY"))
        assertTrue(reports[0].body.contains("| Importance | foreground |"))
        assertTrue(reports[0].body.contains("The phone just now"))
        // Looked at once: the same end is not reported again at the next start.
        BugReports.dir(app).listFiles { f -> f.name.endsWith(".json") }!!.forEach { it.delete() }
        ExitReasons.check(app)
        Thread.sleep(1_500)
        assertEquals(0, queued(app).size)
    }
}
