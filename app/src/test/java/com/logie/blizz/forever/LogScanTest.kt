package com.logie.blizz.forever

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import java.nio.file.Files

class LogScanTest {
    private val ready = Regex("""World initialized in|\(worldserver-daemon\) ready""")
    private fun temp() = File(Files.createTempDirectory("scan").toFile(), "worldserver.log")

    @Test
    fun `finds the pattern once it is written, reading only what was added`() {
        val log = temp()
        val scan = LogScan(log, ready, chunk = 64, overlap = 32)
        assertFalse(scan.found())
        log.writeText("loading\n".repeat(100))
        assertFalse(scan.found())
        log.appendText("World initialized in 3 minutes\n")
        assertTrue(scan.found())
    }

    @Test
    fun `a match cut between two reads is still found`() {
        val log = temp()
        val scan = LogScan(log, ready, chunk = 16, overlap = 32)
        log.writeText("x".repeat(10) + "World initialized in 1")
        assertTrue(scan.found())
        val second = temp()
        val again = LogScan(second, ready, chunk = 10, overlap = 32)
        second.writeText("aaaaaWorld ini")
        assertFalse(again.found())
        second.appendText("tialized in 5")
        assertTrue(again.found())
    }

    @Test
    fun `a log started again is read from its start`() {
        val log = temp()
        val scan = LogScan(log, ready)
        log.writeText("a long first start\n".repeat(50))
        assertFalse(scan.found())
        log.writeText("World initialized in 1\n")
        assertTrue(scan.found())
    }

    @Test
    fun `a missing log is not a match`() {
        assertFalse(LogScan(temp(), ready).found())
    }

    @Test
    fun `a big log is read in pieces, not whole`() {
        val log = temp()
        log.outputStream().use { out -> repeat(40) { out.write(ByteArray(1 shl 20) { 'a'.code.toByte() }) } }
        log.appendText("\n(worldserver-daemon) ready\n")
        assertTrue(LogScan(log, ready, chunk = 1 shl 20).found())
    }

    @Test
    fun `trim keeps the end of a log over the limit, from a line start`() {
        val log = temp()
        log.writeText((1..200).joinToString("") { "line $it\n" })
        assertTrue(LogScan.trim(log, limit = 100, keep = 50))
        val text = log.readText()
        assertTrue(text.length <= 50)
        assertTrue(text.startsWith("line "))
        assertTrue(text.endsWith("line 200\n"))
    }

    @Test
    fun `trim leaves a small or missing log alone`() {
        val log = temp()
        assertFalse(LogScan.trim(log))
        log.writeText("short\n")
        assertFalse(LogScan.trim(log))
        assertEquals("short\n", log.readText())
    }
}
