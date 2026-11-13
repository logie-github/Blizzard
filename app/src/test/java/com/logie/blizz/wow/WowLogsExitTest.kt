package com.logie.blizz.wow

import org.junit.Assert.assertEquals
import org.junit.Test

/** A program's exit code in words for the realm's reports ([WowLogs.exitInWords]). */
class WowLogsExitTest {
    @Test fun aCodeAbove128IsASignal() {
        assertEquals("code 163: ended by signal 35, the one Android's debuggerd sends for a stack dump", WowLogs.exitInWords(163))
        assertEquals("code 137: ended by signal SIGKILL, the system's (often for memory)", WowLogs.exitInWords(137))
        assertEquals("code 139: ended by signal SIGSEGV, a crash", WowLogs.exitInWords(139))
        assertEquals("code 170: ended by signal 42", WowLogs.exitInWords(170))
    }

    @Test fun otherCodesAsTheyAre() {
        assertEquals("code 0", WowLogs.exitInWords(0))
        assertEquals("code 1", WowLogs.exitInWords(1))
        assertEquals("code 255", WowLogs.exitInWords(255))
    }
}
