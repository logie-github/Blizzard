package com.logie.blizz.forevernew

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

class ForeverLeftoversTest {
    @get:Rule val tmp = TemporaryFolder()

    @Test fun theWaitLooksOnceMoreWhenItsTimeIsUp() {
        // The phone's case: the program is ready, but only the look after the last wait sees it.
        var looks = 0
        assertEquals(ForeverLeftovers.Wait.READY, ForeverLeftovers.await(3, { ++looks > 3 }, { true }, {}))
        assertEquals(4, looks)
        assertEquals(ForeverLeftovers.Wait.TIMED_OUT, ForeverLeftovers.await(3, { false }, { true }, {}))
        assertEquals(ForeverLeftovers.Wait.READY, ForeverLeftovers.await(3, { true }, { false }, {}))
        // ended: said so, unless it was ready as it went
        assertEquals(ForeverLeftovers.Wait.ENDED, ForeverLeftovers.await(3, { false }, { false }, {}))
    }

    @Test fun theLoginServersOwnLastLinesSayItIsUp() {
        // The lines the phone showed under "bnetserver did not become ready in 3 minutes" (16 November 2026).
        val log = "Registered new handler for POST /bnetserver/login/srp/\nRegistered new handler for POST /bnetserver/launcher/remember/\n" +
            "Registered new handler for POST /bnetserver/refreshLoginTicket/\nAdded realm \"Forever\" at 127.0.0.1 (port 8097).\n"
        assertTrue(com.logie.blizz.wow.LineWatch(ForeverServer.BNET_READY).feed(log))
        // its handlers alone (their paths name "bnetserver") are not it
        assertFalse(com.logie.blizz.wow.LineWatch(ForeverServer.BNET_READY).feed("Registered new handler for POST /bnetserver/login/srp/\n"))
        assertTrue(com.logie.blizz.wow.LineWatch(ForeverServer.WORLD.ready).feed("World initialized in 2 minutes 39 seconds\n"))
        assertTrue(com.logie.blizz.wow.LineWatch(ForeverServer.DATABASE.ready).feed("2026-11-16 19:17:50 0 [Note] /x/bin/mariadbd: ready for connections.\n"))
    }

    @Test fun onlyThisServersProgramIsEnded() {
        val bin = File("/data/user/0/com.logie.blizz/files/realms/forever-v2/server/bin")
        val pidFile = tmp.newFile("mariadbd.pid").apply { writeText("4321\n") }
        val ours = "/x/lib/ld-musl-aarch64.so.1 --library-path /x/lib ${bin.path}/mariadbd --no-defaults"
        assertEquals(4321, ForeverLeftovers.pidOf(pidFile))
        assertNull(ForeverLeftovers.pidOf(File(tmp.root, "none.pid")))
        assertNull(ForeverLeftovers.pidOf(tmp.newFile("bad.pid").apply { writeText("x") }))
        assertTrue(ForeverLeftovers.isOurs(4321, bin) { ours })
        assertFalse(ForeverLeftovers.isOurs(4321, bin) { "/system/bin/app_process com.other.app" }) // the number was given to another program since
        assertFalse(ForeverLeftovers.isOurs(4321, bin) { null })
        // ours and running: SIGTERM, gone on the second look
        val sent = ArrayList<Pair<Int, Int>>(); var alive = 3
        assertTrue(ForeverLeftovers.end(pidFile, bin, { p, s -> sent += p to s }, alive = { alive-- > 0 }, cmdline = { ours }, sleep = {}))
        assertEquals(listOf(4321 to 15), sent)
        // it doesn't go: SIGKILL after the wait
        sent.clear()
        assertTrue(ForeverLeftovers.end(pidFile, bin, { p, s -> sent += p to s }, waitSeconds = 1, alive = { true }, cmdline = { ours }, sleep = {}))
        assertEquals(listOf(4321 to 15, 4321 to 9), sent)
        // another program's, or none running: nothing is sent
        sent.clear()
        assertFalse(ForeverLeftovers.end(pidFile, bin, { p, s -> sent += p to s }, alive = { true }, cmdline = { "/system/bin/sh" }, sleep = {}))
        assertFalse(ForeverLeftovers.end(pidFile, bin, { p, s -> sent += p to s }, alive = { false }, cmdline = { ours }, sleep = {}))
        assertTrue(sent.isEmpty())
    }

    /** Against a real MariaDB of the package left running (BLIZZ_LEFTOVER_PID=its pid file, BLIZZ_LEFTOVER_BIN=the package's bin). */
    @Test fun aRealDatabaseLeftRunningIsEnded() {
        val pidFile = System.getenv("BLIZZ_LEFTOVER_PID")?.let { File(it) }
        assumeTrue(pidFile != null)
        val pid = ForeverLeftovers.pidOf(pidFile!!)!!
        assertTrue(ForeverLeftovers.end(pidFile, File(System.getenv("BLIZZ_LEFTOVER_BIN")!!), { p, s -> Runtime.getRuntime().exec(arrayOf("kill", "-$s", p.toString())).waitFor() }))
        assertFalse(File("/proc/$pid").exists())
    }
}
