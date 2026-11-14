package com.logie.blizz.reports

import com.sun.net.httpserver.HttpServer
import org.json.JSONObject
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
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

/**
 * A report that carries a long log: the issue, then its comments in order; where it stopped is kept so a retry goes on from there;
 * what GitHub refuses for its size is cut and sent again; and the person is told in words what became of it.
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class BugReportsLongTest {
    @get:Rule val tmp = TemporaryFolder()
    private lateinit var server: HttpServer
    /** Answers by request number (1-based); the default is 201 with issue number 42. */
    private val answers = HashMap<Int, Pair<Int, String>>()
    private val requests = ArrayList<Pair<String, JSONObject>>()

    @Before fun start() {
        server = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
        server.createContext("/") { ex ->
            val body = JSONObject(ex.requestBody.readBytes().decodeToString())
            requests += ex.requestURI.path to body
            val (code, text) = answers[requests.size] ?: (201 to """{"number": 42, "html_url": "https://github.com/o/r/issues/42"}""")
            val bytes = text.toByteArray()
            ex.sendResponseHeaders(code, if (bytes.isEmpty()) -1 else bytes.size.toLong())
            if (bytes.isNotEmpty()) ex.responseBody.use { it.write(bytes) }
            ex.close()
        }
        server.start()
    }

    @After fun stop() = server.stop(0)

    private val api get() = "http://127.0.0.1:${server.address.port}"

    private fun queued(comments: List<String>, force: Boolean = false): File {
        val dir = tmp.newFolder("reports-${System.nanoTime()}")
        val report = BugReports.Report("Crash: boom", "the body", comments = comments)
        BugReports.queue(dir, report, now = 5, force = force)
        return File(dir, BugReports.fileName(report, force, 5))
    }

    @Test fun theIssueThenItsCommentsInOrderAndTheNumberIsKnown() {
        val file = queued(listOf("first", "second", "third"))
        val result = BugReports.sendDetailed(file, "o/r", "tok", api, gapMs = 0)
        assertEquals(BugReports.Outcome.SENT, result.outcome)
        assertEquals(42, result.issue)
        assertEquals("Report sent: issue #42", result.say())
        assertEquals(listOf("/repos/o/r/issues", "/repos/o/r/issues/42/comments", "/repos/o/r/issues/42/comments", "/repos/o/r/issues/42/comments"), requests.map { it.first })
        assertEquals(listOf("first", "second", "third"), requests.drop(1).map { it.second.getString("body") })
    }

    @Test fun aSendThatStopsHalfwayGoesOnWhereItStoppedAndPostsNothingTwice() {
        val file = queued(listOf("one", "two", "three", "four"))
        answers[3] = 502 to ""          // the second comment fails
        val first = BugReports.sendDetailed(file, "o/r", "tok", api, gapMs = 0)
        assertEquals(BugReports.Outcome.RETRY, first.outcome)
        assertTrue(first.detail, first.detail.contains("issue #42 is open, comment 2 of 4 waits"))
        assertEquals(42, first.issue)
        // What is done is in the file.
        val kept = BugReports.Report.fromJson(JSONObject(file.readText()))
        assertEquals(42, kept.issue)
        assertEquals(1, kept.done)
        requests.clear(); answers.clear()
        val second = BugReports.sendDetailed(file, "o/r", "tok", api, gapMs = 0)
        assertEquals(BugReports.Outcome.SENT, second.outcome)
        assertEquals(42, second.issue)
        // No second issue; the comments from the second on, each once.
        assertEquals(listOf("two", "three", "four"), requests.map { it.second.getString("body") })
        assertTrue(requests.all { it.first == "/repos/o/r/issues/42/comments" })
    }

    @Test fun aCommentGitHubRefusesIsSkippedAndTheRestGo() {
        val file = queued(listOf("one", "two", "three"))
        answers[3] = 422 to """{"message": "Validation Failed"}"""
        val result = BugReports.sendDetailed(file, "o/r", "tok", api, gapMs = 0)
        assertEquals(BugReports.Outcome.SENT, result.outcome)
        assertEquals(4, requests.size)
    }

    @Test fun anIssueRefusedForItsSizeIsSentAgainCutShort() {
        val dir = tmp.newFolder("big")
        val report = BugReports.Report("Big: one", "x".repeat(50_000))
        BugReports.queue(dir, report, now = 1)
        val file = File(dir, "${report.key}.json")
        answers[1] = 422 to """{"message": "body is too long"}"""
        val result = BugReports.sendDetailed(file, "o/r", "tok", api, gapMs = 0)
        assertEquals(BugReports.Outcome.SENT, result.outcome)
        assertEquals(2, requests.size)
        assertEquals(50_000, requests[0].second.getString("body").length)
        val second = requests[1].second.getString("body")
        assertTrue(second.length < 21_000)
        assertTrue(second.contains("cut: GitHub refused the full text, 422"))
    }

    @Test fun aSmallRefusedIssueIsGivenUpAndSaidSo() {
        val file = queued(emptyList())
        answers[1] = 422 to """{"message": "Validation Failed"}"""
        val result = BugReports.sendDetailed(file, "o/r", "tok", api, gapMs = 0)
        assertEquals(BugReports.Outcome.REFUSED, result.outcome)
        assertEquals("GitHub refused the report (GitHub answered 422: Validation Failed).", result.say())
        // (`send` keeps its old word for it: gone, not sent again)
        answers.clear(); requests.clear()
        assertEquals(BugReports.Outcome.SENT, BugReports.send(queued(emptyList()).also { answers[1] = 422 to "" }, "o/r", "tok", api))
    }

    @Test fun whatCouldNotBeSentIsSaidInWords() {
        val file = queued(emptyList())
        answers[1] = 401 to """{"message": "Bad credentials"}"""
        val refused = BugReports.sendDetailed(file, "o/r", "tok", api, gapMs = 0)
        assertEquals(BugReports.Outcome.NOT_CONFIGURED, refused.outcome)
        assertTrue(refused.say(), refused.say().startsWith("This build can't send reports (GitHub answered 401: Bad credentials)"))
        val down = BugReports.sendDetailed(file, "o/r", "tok", "http://127.0.0.1:1", gapMs = 0)
        assertEquals(BugReports.Outcome.RETRY, down.outcome)
        assertTrue(down.say(), down.say().contains("no connection to GitHub"))
        assertEquals("this build has no report token", BugReports.sendDetailed(file, "o/r", "", api).detail)
    }

    @Test fun anIssueWhoseAnswerNamesNoNumberKeepsItsCommentsNowhere() {
        val file = queued(listOf("one"))
        answers[1] = 201 to ""
        val result = BugReports.sendDetailed(file, "o/r", "tok", api, gapMs = 0)
        assertEquals(BugReports.Outcome.SENT, result.outcome)
        assertTrue(result.detail, result.detail.contains("1 comments not sent"))
        assertEquals(1, requests.size)
    }

    // What is queued ---------------------------------------------------------------------------

    @Test fun aReportThePersonAskedForIsNeverDroppedForBeingTheSameAsOneThatWent() {
        val dir = tmp.newFolder("dedupe")
        val report = BugReports.Report("World of Warcraft in-game report: Sent from the game menu", "b")
        assertTrue(BugReports.queue(dir, report, now = 1_000))
        File(dir, "${report.key}.json").delete()
        // The same one a minute later is dropped (a failure that repeats), but asked for it goes.
        assertFalse(BugReports.queue(dir, report, now = 61_000))
        assertTrue(BugReports.queue(dir, report, now = 61_000, force = true))
        assertTrue(BugReports.queue(dir, report, now = 62_000, force = true))
        assertEquals(2, dir.listFiles { f -> f.name.contains("-f") }!!.size)
    }

    @Test fun aLongTextBecomesCommentsThatFitAndAreLabelled() {
        val text = (1..5_000).joinToString("\n") { "line $it of a long log with some words in it" }
        val chunks = BugReports.chunks("Log of this run", text, size = 50_000)
        assertTrue(chunks.size in 4..6)
        assertTrue(chunks.all { it.length < 65_000 })
        assertTrue(chunks[0].startsWith("**Log of this run (part 1 of ${chunks.size})**"))
        // Every line is in exactly one, in order, and a code fence in the text cannot close the block early.
        val joined = chunks.joinToString("") { it.substringAfter("```\n").substringBeforeLast("```") }
        assertEquals(text + "\n", joined)
        assertEquals(listOf("**One**\n\n```\nshort\n```\n"), BugReports.chunks("One", "short"))
        assertEquals(emptyList<String>(), BugReports.chunks("None", "  \n"))
        assertFalse(BugReports.chunks("Fence", "a\n```\nb")[0].substringAfter("```\n").substringBeforeLast("```").contains("```"))
    }

    @Test fun theBodyHoldsThePhonesStateAndStaysUnderTheLimit() {
        val body = BugReports.body("Crash", "boom", listOf("Game" to "x"), "l".repeat(100_000), files = "f".repeat(100_000), device = "mem avail 100/11800 MB LOW")
        assertTrue(body.contains("<summary>The phone just now</summary>"))
        assertTrue(body.contains("mem avail 100/11800 MB LOW"))
        assertTrue("body is ${body.length}", body.length < BugReports.MAX_ISSUE)
        assertNull(Regex("ghp_").find(BugReports.body("Crash", "x", emptyList(), "token ghp_abc123def")))
    }

    @Test fun aReportSurvivesItsFileWithItsCommentsAndProgress() {
        val report = BugReports.Report("t", "b", comments = listOf("c1", "c2"), issue = 7, done = 1)
        assertEquals(report, BugReports.Report.fromJson(report.toJson()))
        // A file an older build wrote has none of them.
        val old = BugReports.Report.fromJson(JSONObject("""{"title":"t","body":"b","label":"auto-report"}"""))
        assertEquals(BugReports.Report("t", "b"), old)
    }
}
