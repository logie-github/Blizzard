package com.logie.blizz.selftest

import com.logie.blizz.importer.ImportRecord
import com.logie.blizz.importer.LibraryEntry
import com.logie.blizz.importer.Problem
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

@org.junit.runner.RunWith(org.robolectric.RobolectricTestRunner::class)
@org.robolectric.annotation.Config(sdk = [34])
class SelfTestTest {
    private fun entry(id: String) = LibraryEntry(
        gameId = id, title = id, products = emptyList(), clientVersion = "1", installPath = "/x/$id", executable = "game.exe",
        runtime = LibraryEntry.RUNTIME_WINLATOR, arguments = "", stage = com.logie.blizz.importer.Stage.IMPORTED_UNTESTED, saveLocation = null, controlProfile = id,
    )

    @Test fun installIsToldFromTheRecordAndTheFiles() {
        val record = ImportRecord("a")
        assertEquals(Install.INSTALLED, SelfTestReport.inspect(record, entry("a"), true).install)
        assertEquals(Install.INCOMPLETE, SelfTestReport.inspect(record, entry("a"), false).install)
        assertEquals(Install.NOT_INSTALLED, SelfTestReport.inspect(record, null, false).install)
        val failed = SelfTestReport.inspect(record.copy(problem = Problem.MISSING_RUNTIME_DEPENDENCY, message = "libs missing"), null, false)
        assertEquals(Install.INCOMPLETE, failed.install)
        assertTrue("MISSING_RUNTIME_DEPENDENCY" in failed.detail && "libs missing" in failed.detail)
    }

    @Test fun onlyInstalledGamesAreStartedAndAFailingProbeIsRecorded() = runBlocking {
        val started = ArrayList<String>()
        val results = SelfTest.runAll(
            listOf(SelfTest.Target("a", "A"), SelfTest.Target("b", "B"), SelfTest.Target("c", "C"), SelfTest.Target("d", "D")),
            inspect = { t ->
                when (t.gameId) {
                    "a", "c", "d" -> Inspection(Install.INSTALLED, "ok") to entry(t.gameId)
                    else -> Inspection(Install.NOT_INSTALLED, "Never imported") to null
                }
            },
            probe = { e ->
                started += e.gameId
                when (e.gameId) {
                    "a" -> SelfTest.LaunchOutcome(Launch.OK, "up", 3, 9)
                    "c" -> throw IllegalStateException("boom")
                    else -> SelfTest.LaunchOutcome(Launch.TIMED_OUT, "no window")
                }
            },
        )
        assertEquals(listOf("a", "c", "d"), started)
        assertEquals(listOf(Launch.OK, Launch.NOT_TESTED, Launch.FAILED, Launch.TIMED_OUT), results.map { it.launch })
        assertTrue(results[2].launchDetail.contains("boom"))
        assertEquals(9, results[0].windowSeconds)
    }

    @Test fun theReportListsEveryGameAndLogsOnlyOfFailures() {
        val results = listOf(
            GameResult("a", "Diablo", Install.INSTALLED, "Files present", Launch.OK, "up", 3, 9, "ok-log"),
            GameResult("b", "StarCraft II", Install.INCOMPLETE, "The import stopped: MISSING_RUNTIME_DEPENDENCY"),
            GameResult("c", "Diablo II", Install.INSTALLED, "Files present", Launch.FAILED, "closed", null, null, "wine: err:module crash"),
        )
        val md = SelfTestReport.markdown(results, listOf("App" to "Blizzard 1"), interruptedAt = "Warcraft III")
        assertTrue("| Diablo | installed | OK | 3 s | 9 s |" in md)
        assertTrue("| StarCraft II | INCOMPLETE | not tested | - | - |" in md)
        assertTrue("| Diablo II | installed | FAILED | - | - |" in md)
        assertTrue("wine: err:module crash" in md)
        assertFalse("ok-log" in md)
        assertTrue("The app stopped while testing Warcraft III" in md)
        assertEquals("Launch test 1.0.67: 1 of 2 installed games launched (2 of 3 installed)", SelfTestReport.title("1.0.67", results))
    }

    @Test fun resultsSurviveTheJsonRoundTrip() {
        val list = listOf(GameResult("a", "A", Install.INSTALLED, "d", Launch.OK, "x", 1, null, "log"), GameResult("b", "B", Install.NOT_INSTALLED, "n"))
        assertEquals(list, GameResult.listFromJson(GameResult.listToJson(list)))
    }
}
