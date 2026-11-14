package com.logie.blizz.reports

import com.logie.blizz.game.GameLog
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

/** The run's log file: lines with their time, rolled over, trimmed, the last run's end still there, and the noise kept out. */
class SessionLogTest {
    @get:Rule val tmp = TemporaryFolder()
    private var now = 1_700_000_000_000L // 2023-11-14 22:13:20 UTC
    private fun log(dir: File = tmp.root, maxBytes: Long = 2L shl 20, keep: Int = 6) = LogFile(dir, { now }, maxBytes, keep)

    @Test fun aLineHasItsTimeAndKindAndTheRunHasItsHeader() {
        val log = log()
        log.open(listOf("run started", "device: x"))
        now += 1_234
        log.write("app", "hello")
        val file = log.runFiles().single()
        assertEquals("run-20231114-221320.log", file.name)
        val lines = file.readLines()
        assertEquals("22:13:20.000 log    run started", lines[0])
        assertEquals("22:13:20.000 log    device: x", lines[1])
        assertEquals("22:13:21.234 app    hello", lines[2])
    }

    @Test fun severalLinesEachGetTheTimeAndALongLineIsCut() {
        val log = log()
        log.open(emptyList())
        log.write("wine", "one\ntwo\n")
        log.write("wine", "x".repeat(LogFile.MAX_LINE + 50))
        val lines = log.runFiles().single().readLines()
        assertEquals(listOf("one", "two"), lines.take(2).map { it.substringAfter("wine   ") })
        assertEquals(LogFile.MAX_LINE, lines[2].substringAfter("wine   ").length)
    }

    @Test fun tailGivesTheEndFromALinesStart() {
        val log = log()
        log.open(emptyList())
        for (i in 1..200) log.write("app", "line number $i")
        val tail = log.tail(500)
        assertTrue(tail.length <= 500)
        assertTrue(tail.endsWith("line number 200\n"))
        assertTrue("starts at a line's start: ${tail.take(30)}", tail.startsWith("22:13:20.000 app    line number "))
        assertTrue(log.tail(10_000_000).contains("line number 1\n"))
    }

    @Test fun aRunRollsOverKeepingTheNewestTwoPartsAndTailReadsAcrossThem() {
        val log = log(maxBytes = 2_000)
        log.open(emptyList())
        for (i in 1..400) log.write("app", "line number $i of the run")
        val files = log.runFiles()
        assertTrue("parts: ${files.map { it.name }}", files.size in 2..2)
        // (parts are numbered from the first; the oldest parts are gone, the first lines with them)
        assertTrue(files.last().name.matches(Regex("run-\\d{8}-\\d{6}\\.\\d+\\.log")))
        val all = log.tail(10_000_000)
        assertTrue(all.contains("line number 400 of the run"))
        assertFalse(all.contains("line number 1 of the run"))
        assertTrue(all.contains("earlier part kept"))
        // The second part is the first roll: nothing deleted yet beside nothing.
        val small = log(dir = tmp.newFolder("b"), maxBytes = 1_500)
        small.open(emptyList())
        for (i in 1..30) small.write("app", "line number $i of the run, a little longer so it rolls once or twice")
        assertTrue(small.runFiles().first().exists())
    }

    @Test fun onlyTheNewestRunsStayAndThePreviousRunsEndCanBeRead() {
        val dir = tmp.newFolder("logs")
        for (r in 1..8) {
            now += 1_000_000
            val run = log(dir, keep = 3)
            run.open(listOf("run $r"))
            run.write("app", "end of run $r")
            run.close()
        }
        // The eighth run is open; the two before it stay, the older ones are gone.
        val names = dir.list()!!.sorted()
        assertEquals(names.toString(), 3, names.size)
        now += 1_000_000
        val next = log(dir, keep = 3)
        next.open(listOf("run 9"))
        assertTrue(next.previousTail(1_000).contains("end of run 8"))
        assertFalse(next.previousTail(1_000).contains("run 9"))
        assertEquals(3, dir.list()!!.size)
    }

    @Test fun withNoEarlierRunThePreviousTailIsEmptyAndAnUnwritableLogNeverRaises() {
        val first = log(tmp.newFolder("c"))
        first.open(listOf("only run"))
        assertEquals("", first.previousTail(1_000))
        // A log that can't be written (the folder is a file) turns itself off and stays quiet.
        val blocked = File(tmp.root, "blocked").apply { writeText("x") }
        val broken = log(File(blocked, "sub"))
        broken.open(listOf("header"))
        broken.write("app", "never raises")
        assertEquals("", broken.tail(100))
    }

    // What is kept out of it ---------------------------------------------------------------------

    @Test fun aRepeatedLineIsSaidThreeTimesThenCounted() {
        val limiter = RepeatLimiter()
        val said = ArrayList<String>()
        for (i in 1..120) limiter.admit("0158:err:mscoree:LoadLibraryShim error reading registry key for installroot")?.let { said += it }
        // The same message from other threads, with other numbers, is the same kind.
        limiter.admit("0168:err:mscoree:LoadLibraryShim error reading registry key for installroot")
        assertEquals(3 + 2, said.size)
        assertTrue(said[3].startsWith("(the same kind of line 10 times so far: 0158:err:mscoree"))
        assertTrue(said[4].startsWith("(the same kind of line 100 times so far"))
        assertEquals("121 x 0158:err:mscoree:LoadLibraryShim error reading registry key for installroot", limiter.totals().single())
        // Different words are different kinds.
        assertNotNull(limiter.admit("0158:err:ole:start_rpcss Failed to start RpcSs service"))
        assertNotNull(limiter.admit("0158:err:ole:start_rpcss Failed to start RpcSs service"))
    }

    @Test fun linesDifferingOnlyInNumbersAreOneKind() {
        assertEquals(RepeatLimiter.key("00ec:fixme:ntdll:NtQuerySystemInformation info_class 12 at 0x7FFF0010"), RepeatLimiter.key("00f8:fixme:ntdll:NtQuerySystemInformation info_class 98 at 0x7FFE0020"))
        assertTrue(RepeatLimiter.key("err:a:x failed") != RepeatLimiter.key("err:a:y failed"))
    }

    @Test fun threadNamingAndModuleListingsAreNoise() {
        // .NET names every thread it starts (the phone's reports were mostly this) and lists a process's modules over and over.
        val naming = listOf(
            "0144:trace:seh:dispatch_exception code=406d1388 (EXCEPTION_WINE_NAME_THREAD) flags=0 addr=000000007BC18677",
            "0144:trace:seh:dispatch_exception  info[0]=0000000000001000",
            "0144:trace:seh:dispatch_exception rip=0000007ffff1132d rsp=000000010320f050 rbp=000000000b0bfb90 eflags=00000206",
            "0144:trace:seh:call_seh_handlers calling handler 0000007FFFF11338 (rec=000000010320EE30, frame=10320f050 context=000000010320E940, dispatch=000000010320E240)",
            "0144:trace:seh:RtlUnwindEx code=406d1388 flags=2 end_frame=000000010320F050 target_ip=0000007FFFF11315",
            "0144:trace:seh:RtlRestoreContext returning to 0000007FFFF11315 stack 000000010320F050",
            "0144:trace:seh:call_vectored_handlers handler at 7A137D70 returned ffffffff",
        )
        for (line in naming) assertTrue(line, GameLog.noise(line))
        assertTrue(GameLog.noise("00ec:trace:seh:EnumProcessModulesEx (FFFFFFFFFFFFFFFF, 0000000003D7C6B0, 8192, 000000000050C9DC, 0)"))
        // The same thread then really faults: all of that is kept.
        for (line in listOf(
            "0144:trace:seh:dispatch_exception code=c0000005 (EXCEPTION_ACCESS_VIOLATION) flags=0 addr=6F8E87CC",
            "0144:trace:seh:dispatch_exception  info[0]=00000000",
        )) assertFalse(line, GameLog.noise(line))
    }

    @Test fun loadedLibrariesAreShortened() {
        assertEquals(
            "00e8 Loaded C:\\windows\\mono\\mono-2.0\\bin\\libmono-2.0-x86_64.dll builtin",
            LibLines.compact("00e8:trace:loaddll:build_module Loaded L\"C:\\\\windows\\\\mono\\\\mono-2.0\\\\bin\\\\libmono-2.0-x86_64.dll\" at 000000027EE90000: builtin"),
        )
        assertEquals(
            "00d0 Unloaded C:\\windows\\system32\\uxtheme.dll builtin",
            LibLines.compact("00d0:trace:loaddll:free_modref Unloaded module L\"C:\\\\windows\\\\system32\\\\uxtheme.dll\" : builtin"),
        )
        assertEquals("not a library line", LibLines.compact("not a library line"))
    }

    @Test fun gameLogWritesToTheRunLogOnlyWhatIsNotNoise() {
        GameLog.clear()
        // (no run log is started in a unit test: nothing is written, nothing raises)
        GameLog.take("00ec:trace:seh:EnumProcessModulesEx (FFFFFFFFFFFFFFFF, 1, 8192, 2, 0)")
        for (i in 1..50) GameLog.take("0158:err:mscoree:LoadLibraryShim error reading registry key for installroot")
        GameLog.take("00ec:err:ole:start_rpcss Failed to start RpcSs service")
        GameLog.note("something the app decided")
        val snapshot = GameLog.snapshot()
        assertFalse(snapshot.contains("EnumProcessModulesEx"))
        assertEquals(3 + 1, Regex("LoadLibraryShim").findAll(snapshot).count())
        assertTrue(snapshot.contains("(the same kind of line 10 times so far"))
        assertTrue(snapshot.contains("start_rpcss"))
        assertNull(GameLog.fault)
        GameLog.clear()
    }
}
