package com.logie.blizz.reports

import com.sun.net.httpserver.HttpServer
import org.json.JSONObject
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.File
import java.net.InetSocketAddress

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class BugReportsTest {
    @get:Rule val tmp = TemporaryFolder()
    private lateinit var server: HttpServer
    private var status = 201
    private val requests = ArrayList<Triple<String, String?, String>>()

    @Before fun start() {
        server = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
        server.createContext("/") { ex ->
            requests += Triple(ex.requestURI.path, ex.requestHeaders.getFirst("Authorization"), ex.requestBody.readBytes().decodeToString())
            ex.sendResponseHeaders(status, -1)
            ex.close()
        }
        server.start()
    }

    @After fun stop() = server.stop(0)

    private val api get() = "http://127.0.0.1:${server.address.port}"

    @Test fun theSameFailureIsQueuedOnceADay() {
        val dir = tmp.newFolder("reports")
        val report = BugReports.Report("Diablo import (DOWNLOAD_FAILED): HTTP 503", "body")
        assertTrue(BugReports.queue(dir, report, now = 1_000))
        // Sent and gone: still not again the same day, even with other numbers in it.
        File(dir, "${report.key}.json").delete()
        assertFalse(BugReports.queue(dir, BugReports.Report("Diablo import (DOWNLOAD_FAILED): HTTP 502", "body"), now = 2_000))
        assertTrue(BugReports.queue(dir, report, now = 1_000 + 25 * 3600 * 1000L))
        assertTrue(BugReports.queue(dir, BugReports.Report("StarCraft launch: boom", "b"), now = 3_000))
    }

    @Test fun anIssueIsOpenedWithTheToken() {
        val dir = tmp.newFolder("reports")
        val report = BugReports.Report("Crash: IllegalStateException in Launcher.play", BugReports.body("Crash", "boom", listOf("Game" to "diablo"), "trace"))
        BugReports.queue(dir, report)
        val file = File(dir, "${report.key}.json")
        assertEquals(BugReports.Outcome.SENT, BugReports.send(file, "logie-github/Blizzard", "tok", api))
        val (path, auth, body) = requests.single()
        assertEquals("/repos/logie-github/Blizzard/issues", path)
        assertEquals("Bearer tok", auth)
        val json = JSONObject(body)
        assertEquals("Crash: IllegalStateException in Launcher.play", json.getString("title"))
        assertTrue(json.getString("body").contains("| Game | diablo |"))
        assertEquals("bug", json.getJSONArray("labels").getString(0))
    }

    @Test fun failuresToSendAreKeptOrStopped() {
        val dir = tmp.newFolder("reports")
        BugReports.queue(dir, BugReports.Report("x", "y"))
        val file = dir.listFiles { f -> f.name.endsWith(".json") }!!.single()
        status = 502
        assertEquals(BugReports.Outcome.RETRY, BugReports.send(file, "o/r", "tok", api))
        status = 401
        assertEquals(BugReports.Outcome.NOT_CONFIGURED, BugReports.send(file, "o/r", "tok", api))
        assertEquals(BugReports.Outcome.NOT_CONFIGURED, BugReports.send(file, "o/r", "", api))
        assertEquals(BugReports.Outcome.RETRY, BugReports.send(file, "o/r", "tok", "http://127.0.0.1:1"))
        assertTrue(file.exists())
    }

    @Test fun keysAndTokensNeverGoOut() {
        val log = "install D2DV --cdkey ABCD1234EFGH5678 --cdkey-expansion ABCDEFGHJKLMNPQRSTVWXYZ234 token ghp_abcdef123"
        val out = BugReports.redact(log)
        assertFalse(out.contains("ABCD1234EFGH5678"))
        assertFalse(out.contains("ABCDEFGHJKLMNPQRSTVWXYZ234"))
        assertFalse(out.contains("ghp_abcdef123"))
    }
}
