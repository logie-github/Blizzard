package com.logie.blizz.wrathpp

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

/** WarcraftXL's logs of Wrath++'s launches ([WrathppLogs]): a crash found and handed out once, the creator's lines, the creator left out after a crash with it up. */
class WrathppLogsTest {
    @get:Rule val tmp = TemporaryFolder()

    private fun launch(at: String, vararg more: String) = listOf(
        "[$at.101] [INFO ] [session] launch 2026-11-12 $at local, pid 4242",
        "[$at.744] [INFO ] [host] loaded wrathpp.native 0.3.0 (Wrath++ native) from bin/x86/wrathpp-native.dll",
        "[$at.900] [INFO ] [core] stage ready",
    ) + more
    private val crash = arrayOf(
        "[11:05:51.335] [ERROR] [crash] unhandled access violation (0xC0000005) reading 0x10 at WowWrathpp.exe+0x2134AB, thread 1234 (the main thread), 2m 29s after launch, stage ready",
        "[11:05:51.336] [ERROR] [crash] #0 WowWrathpp.exe+0x2134AB",
        "[11:05:51.336] [ERROR] [crash] #1 WowWrathpp.exe+0x1F00C2",
    )

    @Test fun aLaunchWithoutACrashHasNone() {
        assertNull(WrathppLogs.crashOf("WarcraftXL.log", launch("11:03:22", "[11:03:25.000] [INFO ] [crash] the crash report runs first, then the filter at WowWrathpp.exe+0x372760",
            "[11:20:00.000] [INFO ] [session] session end: clean exit, the client closed, after 16m 38s")))
    }

    @Test fun aCrashIsReadWithWhereTheCreatorWas() {
        val up = WrathppLogs.crashOf("WarcraftXL.log", launch("11:03:22", "[11:05:40.000] [INFO ] [wrathpp] creator: built",
            "[11:05:49.000] [INFO ] [wrathpp] creator: opened: native 0.3.0, looks' options in, undead skins not in",
            "[11:05:49.100] [INFO ] [wrathpp] creator: screen: race and class", *crash))!!
        assertEquals("unhandled access violation (0xC0000005) reading 0x10 at WowWrathpp.exe+0x2134AB, thread 1234 (the main thread), 2m 29s after launch, stage ready", up.what)
        assertTrue(up.creatorUp)
        assertTrue(up.text.contains("#1 WowWrathpp.exe+0x1F00C2") && up.text.contains("launch 2026-11-12") && up.text.contains("loaded wrathpp.native 0.3.0"))
        // built but never opened, closed again, or an older native mod that says nothing: not the creator's screen
        assertFalse(WrathppLogs.crashOf("a", launch("11:03:22", "[11:05:40.000] [INFO ] [wrathpp] creator: built", *crash))!!.creatorUp)
        assertFalse(WrathppLogs.crashOf("a", launch("11:03:22", "[11:05:40.000] [INFO ] [wrathpp] creator: opened: native 0.3.0", "[11:05:45.000] [INFO ] [wrathpp] creator: closed", *crash))!!.creatorUp)
        assertFalse(WrathppLogs.crashOf("a", launch("11:03:22", *crash))!!.creatorUp)
    }

    @Test fun eachCrashIsHandedOutOnce() {
        val logs = tmp.newFolder("Logs")
        File(logs, "WarcraftXL-2026-11-12_10-58-00.log").apply { writeText(launch("10:58:00", *crash).joinToString("\n")); setLastModified(1_000_000) }
        File(logs, "WarcraftXL-2026-11-12_11-00-00.log").apply { writeText(launch("11:00:00", "[11:00:09.000] [INFO ] [session] session end: clean exit").joinToString("\n")); setLastModified(2_000_000) }
        File(logs, "WarcraftXL.log").apply { writeText(launch("11:03:22", *crash).joinToString("\n")); setLastModified(3_000_000) }
        File(logs, "Other.log").writeText(crash.joinToString("\n"))
        val first = WrathppLogs.unreported(logs)
        assertEquals(listOf("WarcraftXL.log", "WarcraftXL-2026-11-12_10-58-00.log"), first.map { it.file })       // the newest first
        assertTrue(first[0].id != first[1].id)
        assertTrue(WrathppLogs.unreported(logs).isEmpty())
        // the running log becomes an earlier launch's at the next start: the same crash, not handed out again
        File(logs, "WarcraftXL.log").renameTo(File(logs, "WarcraftXL-2026-11-12_11-03-22.log"))
        File(logs, "WarcraftXL.log").writeText(launch("11:30:00").joinToString("\n"))
        assertTrue(WrathppLogs.unreported(logs).isEmpty())
        File(logs, "WarcraftXL.log").writeText(launch("11:30:00", *crash).joinToString("\n"))
        assertEquals(1, WrathppLogs.unreported(logs).size)
    }

    @Test fun whatTheCreatorSaid() {
        val lines = launch("11:03:22", "[11:05:40.000] [INFO ] [wrathpp] creator: built", "[11:05:49.000] [INFO ] [wrathpp] creator: customize: 1_1, 9 rows, Shadowlands' options",
            "[11:05:50.000] [INFO ] [wrathpp] creator: customize: 2_0, 7 rows, Shadowlands' options", "[11:05:52.000] [INFO ] [wrathpp] creator: closed")
        assertEquals("built; customize: #_#, # rows, Shadowlands' options; closed", WrathppLogs.creatorSaid(lines))
        val logs = tmp.newFolder("Logs")
        File(logs, "WarcraftXL-2026-11-12_11-03-22.log").apply { writeText(lines.joinToString("\n")); setLastModified(1_000_000) }
        File(logs, "WarcraftXL.log").apply { writeText(launch("11:30:00").joinToString("\n")); setLastModified(2_000_000) }
        assertEquals(4, WrathppLogs.lastCreatorLines(logs).size)                        // the running launch has none yet: the one before
        assertTrue(WrathppLogs.lastCreatorLines(tmp.newFolder("none")).isEmpty())
    }

    @Test fun theCreatorIsLeftOutForTheBuildItCrashedIn() {
        val logs = tmp.newFolder("Logs")
        assertFalse(WrathppLogs.creatorOff(logs, 227))
        WrathppLogs.creatorCrashed(logs, 227)
        assertTrue(WrathppLogs.creatorOff(logs, 227))
        assertFalse(WrathppLogs.creatorOff(logs, 228))                                  // the next build starts with it again
        assertFalse(WrathppLogs.creatorOff(logs, 227))
    }

    @Test fun theLoginScreenIsUpWhenThisLaunchsLogSaysStageReady() {
        val log = File(tmp.newFolder(), "WarcraftXL.log")
        val start = System.currentTimeMillis()
        assertFalse(WrathppLogs.ready(log, start))                              // no log yet
        log.writeText("[17:43:50.702] [INFO ] [core] stage early\n")
        assertFalse(WrathppLogs.ready(log, start - 1000))                      // still loading
        log.appendText("[17:44:05.578] [INFO ] [wrathpp] creator: built\n[17:44:06.221] [INFO ] [core] stage ready\n")
        assertTrue(WrathppLogs.ready(log, start - 1000))
        log.setLastModified(start - 60_000)                                     // the last launch's log, which said it too
        assertFalse(WrathppLogs.ready(log, start - 1000))
    }
}
