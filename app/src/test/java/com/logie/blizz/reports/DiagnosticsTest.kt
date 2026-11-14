package com.logie.blizz.reports

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

/** What the phone's own files say, read as the logs read them; and why a process ended. */
class DiagnosticsTest {
    @get:Rule val tmp = TemporaryFolder()

    @Test fun statusGivesTheSizeAndThreads() {
        val status = "Name:\tWow.exe\nUmask:\t0077\nVmPeak:\t 9000000 kB\nVmRSS:\t 3178496 kB\nThreads:\t42\nSigQ:\t0/1\n"
        assertEquals(3178496L to 42, Diagnostics.parseStatus(status))
        // A kernel thread has neither.
        assertEquals(0L to 0, Diagnostics.parseStatus("Name:\tkworker\nState:\tS\n"))
    }

    @Test fun aProgramIsNamedByWhatItsCommandLineSays() {
        assertEquals("Wow.exe", Diagnostics.processName("F:\\client\\_forever_\\Wow.exe\u0000-config\u0000ForeverLauncher.wtf\u0000", "box64"))
        assertEquals("Wow.exe", Diagnostics.processName("F:\\client\\_forever_\\Wow.exe -config x", "box64"))
        assertEquals("worldserver", Diagnostics.processName("/data/data/com.logie.blizz/files/forever/server/bin/worldserver\u0000-c\u0000x", "worldserver"))
        assertEquals("box64", Diagnostics.processName("", "box64\n"))
        assertEquals(40, Diagnostics.processName("a".repeat(100), "x").length)
    }

    @Test fun meminfoIsReadAsNumbers() {
        val text = "MemTotal:       11800000 kB\nMemFree:          200000 kB\nMemAvailable:    2310000 kB\nSwapFree:        1800000 kB\nnot a line\n"
        val info = Diagnostics.parseMeminfo(text)
        assertEquals(2310000L, info["MemAvailable"])
        assertEquals(1800000L, info["SwapFree"])
        assertFalse(info.containsKey("not a line"))
    }

    @Test fun theAppsOwnProcessesAreReadFromProc() {
        val proc = tmp.newFolder("proc")
        fun make(pid: Int, status: String, cmdline: String, comm: String) {
            val d = File(proc, pid.toString()).apply { mkdirs() }
            File(d, "status").writeText(status); File(d, "cmdline").writeText(cmdline); File(d, "comm").writeText(comm)
        }
        make(100, "VmRSS:\t 420000 kB\nThreads:\t60\n", "com.logie.blizz\u0000", "blizz")
        make(200, "VmRSS:\t3178496 kB\nThreads:\t42\n", "F:\\client\\_forever_\\Wow.exe\u0000-config\u0000x", "box64")
        make(300, "Name:\tkthread\n", "", "kthread")
        File(proc, "self").mkdirs()
        File(proc, "meminfo").writeText("x")
        val procs = Diagnostics.readProcesses(proc, self = 100).sortedBy { it.pid }
        assertEquals(listOf("app", "Wow.exe"), procs.map { it.name })
        assertEquals(3178496L, procs[1].rssKb)
    }

    @Test fun theKernelsOwnFilesAreReadAsTheyReallyAre() {
        // (this machine's /proc: the same formats as the phone's kernel)
        org.junit.Assume.assumeTrue(File("/proc/self/status").isFile)
        val me = Diagnostics.parseStatus(File("/proc/self/status").readText())
        assertTrue("rss ${me.first}", me.first > 1_000)
        assertTrue("threads ${me.second}", me.second >= 1)
        val info = Diagnostics.parseMeminfo(File("/proc/meminfo").readText())
        assertTrue(info["MemTotal"]!! > 100_000)
        assertTrue(info.containsKey("MemAvailable"))
        val here = ProcessHandle.current().pid().toInt()
        val procs = Diagnostics.readProcesses(self = here)
        val own = procs.single { it.pid == here }
        assertEquals("app", own.name)
        assertTrue(procs.size > 1 || procs.single().rssKb > 0)
        // And the line made of them reads as a line.
        val line = Diagnostics.sampleLine(info["MemAvailable"]!! / 1024, info["MemTotal"]!! / 1024, false, 300, null, 100, procs.take(3), null, null)
        assertTrue(line, line.startsWith("mem avail "))
    }

    @Test fun theSampleLineSaysMemoryAndTheBiggestProcesses() {
        val procs = listOf(
            Diagnostics.Proc(1, "Wow.exe", 3_178_496, 42), Diagnostics.Proc(2, "worldserver", 1_228_800, 30),
            Diagnostics.Proc(3, "mariadbd", 419_840, 20), Diagnostics.Proc(4, "explorer.exe", 40_960, 5),
            Diagnostics.Proc(5, "services.exe", 20_480, 4), Diagnostics.Proc(6, "winedevice.exe", 10_240, 3), Diagnostics.Proc(7, "svchost.exe", 5_120, 2),
        )
        assertEquals(
            "mem avail 2310/11800 MB ok, swap free 1800 MB | app pss 412 MB | 7 procs 4789 MB: Wow.exe 3104, worldserver 1200, mariadbd 410, explorer.exe 40, services.exe 20, +2 | thermal 1 | batt 74%",
            Diagnostics.sampleLine(2310, 11800, false, 380, 1800, 412, procs, 1, 74),
        )
        assertTrue(Diagnostics.sampleLine(90, 11800, true, 380, null, 400, emptyList(), null, null).startsWith("mem avail 90/11800 MB LOW (threshold 380) | app pss 400 MB | 0 procs 0 MB"))
    }

    @Test fun processesComingAndGoingAreSaidAndHelpersPassingAreNot() {
        val before = mapOf(2 to Diagnostics.Proc(2, "worldserver", 1_228_800, 30), 3 to Diagnostics.Proc(3, "mariadbd", 419_840, 20))
        val now = listOf(
            Diagnostics.Proc(3, "mariadbd", 420_000, 20), Diagnostics.Proc(9, "Wow.exe", 102_400, 12), Diagnostics.Proc(10, "logcat", 3_000, 2),
        )
        assertEquals(
            listOf("+ Wow.exe (pid 9, 100 MB, 12 threads)", "- worldserver (pid 2, last seen 1200 MB)").sorted(),
            Diagnostics.changes(before, now).sorted(),
        )
        assertEquals(emptyList<String>(), Diagnostics.changes(before, before.values.toList()))
    }

    @Test fun whyAProcessEndedIsNamedAndOnlyTheSystemsKillsAreReported() {
        assertEquals("LOW_MEMORY", ExitReasons.name(3))
        assertEquals("SIGNALED", ExitReasons.name(2))
        assertEquals("reason 99", ExitReasons.name(99))
        for (reason in listOf(2, 3, 5, 6, 7, 9, 12, 14)) assertTrue(ExitReasons.name(reason), ExitReasons.worthReporting(reason))
        // Leaving by itself, the person closing it, an update, a Java crash (the crash handler reports it itself).
        for (reason in listOf(0, 1, 4, 8, 10, 11, 13, 15, 16)) assertFalse(ExitReasons.name(reason), ExitReasons.worthReporting(reason))
        assertEquals(
            "2023-11-14 22:13:20 UTC process 'com.logie.blizz' ended: LOW_MEMORY (status 9), was foreground, pss 3100 MB, rss 3500 MB, \"kill all\"",
            ExitReasons.describe(3, 9, 100, 3_174_400, 3_584_000, 1_700_000_000_000L, "com.logie.blizz", "kill all"),
        )
        assertEquals("cached", ExitReasons.importanceName(400))
        assertEquals("visible", ExitReasons.importanceName(200))
    }
}
