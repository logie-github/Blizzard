package com.logie.blizz.game

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder

/** What a report's log holds: no longjmp traces, the session keeper's log, the app's notes at the end (the part a report keeps). */
class GameLogTest {
    @get:Rule val tmp = TemporaryFolder()

    @Test fun aLongjmpsTraceIsLeftOutAndARealExceptionsIsKept() {
        // Diablo II, the phone, 9 November 2026: one of these a frame.
        val longjmp = listOf(
            "00dc:trace:seh:RtlUnwindEx code=80000026 flags=2 end_frame=000000010020F3B0 target_ip=0000007FFFF12A96",
            "00dc:trace:seh:RtlUnwindEx  info[0]=000000010020e9a0",
            "00dc:trace:seh:RtlUnwindEx rip=0000007ffff75bf5 rsp=000000010020db80 rbp=000000010020e240 eflags=00000202",
            "00dc:trace:seh:RtlRestoreContext returning to 0000007FFFF12A96 stack 000000010020E930",
        )
        for (line in longjmp) assertTrue(line, GameLog.noise(line))
        // Another thread's lines meanwhile, and anything that is not the exception trace, stay.
        assertFalse(GameLog.noise("00ec:trace:seh:dispatch_exception code=6ba (RPC_S_SERVER_UNAVAILABLE) flags=0 addr=00000002800FD127"))
        assertFalse(GameLog.noise("00dc:err:ole:start_rpcss Failed to start RpcSs service"))
        // The same thread then faults for real: its whole trace is kept.
        val fault = listOf(
            "00dc:trace:seh:dispatch_exception code=c0000005 (EXCEPTION_ACCESS_VIOLATION) flags=0 addr=6F8E87CC",
            "00dc:trace:seh:dispatch_exception  info[0]=00000000",
            "00dc:trace:seh:dispatch_exception  eax=00000000 ebx=00000000 ecx=0019f8a4 edx=00000000 esi=00000000 edi=00000000",
        )
        for (line in fault) assertFalse(line, GameLog.noise(line))
        for (line in longjmp) assertTrue(line, GameLog.noise(line))
    }

    @Test fun theKeepersLogIsReadForTheReport() {
        assertEquals("", GameLog.keeperLines(null))
        assertEquals("", GameLog.keeperLines(tmp.root.resolve("none.log")))
        val log = tmp.newFile("borderless.log")
        log.writeText("0 session keeper: desktop 'shell' takes the input: yes; frames off the games' windows; screen 800x600\n" +
            "0 started 'C:\\windows\\winhandler.exe /dir D:\\\\warcraft3_roc \"Warcraft III.exe\" -window'\n" +
            "6 window of class '#32770' \"Warcraft III\": 400x150 at 200,225, style 94c800c4\n" +
            "6     Static: " + "x".repeat(500) + "\n\n")
        val text = GameLog.keeperLines(log)
        assertTrue(text.startsWith("[session keeper]\n0 session keeper"))
        assertEquals(5, text.lines().size)
        assertTrue(text.lines().all { it.length <= 300 })
        // Only the end of a long one.
        log.writeText((1..200).joinToString("\n") { "$it line" })
        assertEquals(listOf("[session keeper]", "121 line"), GameLog.keeperLines(log).lines().take(2))
    }

    @Test fun theAppsNotesAreTheEndOfTheLogWhichAReportKeeps() {
        val log = tmp.newFile("borderless.log").apply { writeText("0 the game is over: ending the session\n") }
        GameLog.keeperLog = log
        try {
            GameLog.note("left click at 400,300")
            val text = GameLog.snapshot()
            assertTrue(text.trimEnd().endsWith("[app] left click at 400,300"))
            assertTrue(text.indexOf("[session keeper]") in 0 until text.indexOf("[app] left click"))
        } finally {
            GameLog.keeperLog = null
        }
    }
}
