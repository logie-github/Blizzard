package com.logie.blizz.wrathpp

import com.logie.blizz.wow.WowLayout
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit

/** Wrath++ made ready in the background ([WrathppPrewarm.Core]): when Play joins it, skips the setup, or starts the realm again. */
class WrathppPrewarmTest {
    @get:Rule val tmp = TemporaryFolder()

    private class Fake {
        var setups = 0
        var realm: String? = null
        var starts = 0
        var stops = 0
        var inputs = "a"
        var outputs = "o1"
        var server = "s1"
        var stored: String? = null
        val done = object : WrathppPrewarm.Done {
            override fun read() = stored
            override fun write(value: String?) { stored = value }
        }
        var now = 1_000_000L
        var setupBody: () -> Unit = {}
        val lines = ArrayList<String>()
        fun core() = WrathppPrewarm.Core(
            setup = { say -> setups++; say("setting up", 0.5f); setupBody() },
            realms = object : WrathppPrewarm.Realms {
                override fun current() = realm
                override fun start() { starts++; realm = "wrathpp" }
                override fun stopAndWait() { stops++; realm = null }
            },
            inputs = { inputs }, outputs = { outputs }, serverFiles = { server }, done = done, clock = { now },
            log = { synchronized(lines) { lines += it } },
        )
    }

    @Test fun theBackgroundRunsTheSetupThenStartsTheRealmAndPlayDoesNeitherAgain() {
        val f = Fake(); val c = f.core()
        assertTrue(c.background())
        assertEquals(1, f.setups); assertEquals(1, f.starts)
        c.play { _, _ -> }
        assertEquals("the setup isn't run again", 1, f.setups)
        assertEquals("the realm is kept", 0, f.stops)
        assertTrue(f.lines.any { "not run again" in it })
    }

    @Test fun playRunsTheSetupWhenItsFilesChanged() {
        val f = Fake(); val c = f.core()
        c.background()
        f.inputs = "b"   // a setting changed, an import came, the app was updated
        c.play { _, _ -> }
        assertEquals(2, f.setups)
    }

    @Test fun playRunsTheSetupWhenWhatItWroteChanged() {
        val f = Fake(); val c = f.core()
        c.background()
        f.outputs = "o2"   // a table of the game's copy or the server's touched since
        c.play { _, _ -> }
        assertEquals(2, f.setups)
    }

    @Test fun whatWasDoneIsKeptAcrossTheAppsRestartsWithNoTimeLimit() {
        val f = Fake()
        f.core().play { _, _ -> }
        assertEquals(1, f.setups)
        f.now += 7L * 24 * 3600 * 1000
        f.core().play { _, _ -> }                        // a new process (the app opened again), a week later
        assertEquals("nothing changed: not run again", 1, f.setups)
    }

    @Test fun aSetupThatStopsHalfwayIsNeverTakenAsDone() {
        val f = Fake(); val c = f.core()
        c.play { _, _ -> }
        f.inputs = "b"
        f.setupBody = { throw java.io.IOException("offline") }
        try { c.play { _, _ -> } } catch (e: java.io.IOException) { }
        assertEquals(null, f.stored)
        f.setupBody = {}
        f.inputs = "a"   // back as it was: still run, since the last run didn't finish
        c.play { _, _ -> }
        assertEquals(3, f.setups)
    }

    @Test fun theRealmIsStartedAgainWhenItsServerFilesChangedAfterItStarted() {
        val f = Fake(); val c = f.core()
        c.background()
        f.server = "s2"   // the looks' tables written, a new server package, the starting areas
        c.play { _, _ -> }
        assertEquals(1, f.stops)
        assertEquals("Play starts it (its own env.start)", null, f.realm)
        // ...and what Play starts it on is remembered: the next Play keeps it.
        f.realm = "wrathpp"
        c.play { _, _ -> }
        assertEquals(1, f.stops)
    }

    @Test fun anotherRealmIsNeverTouched() {
        val f = Fake(); f.realm = "main"; val c = f.core()
        c.background()
        assertEquals("no realm started over Wrath+", 0, f.starts)
        c.play { _, _ -> }
        assertEquals(0, f.stops)
    }

    @Test fun aRealmNoOneStartedHereIsStartedAgainBeforePlay() {
        // (running, but not from this core: what it read isn't known, so it isn't trusted)
        val f = Fake(); f.realm = "wrathpp"; val c = f.core()
        c.play { _, _ -> }
        assertEquals(1, f.stops)
    }

    @Test fun playJoinsABackgroundRunUnderWay() {
        val f = Fake(); val c = f.core()
        val inSetup = CountDownLatch(1); val release = CountDownLatch(1)
        f.setupBody = { if (f.setups == 1) { inSetup.countDown(); release.await(5, TimeUnit.SECONDS) } }
        val bg = Thread { c.background() }.apply { start() }
        assertTrue(inSetup.await(5, TimeUnit.SECONDS))
        val said = ArrayList<String>()
        val player = Thread { c.play { m, _ -> synchronized(said) { said += m } } }.apply { start() }
        Thread.sleep(500)
        assertTrue("Play waits", player.isAlive)
        release.countDown()
        bg.join(5000); player.join(5000)
        assertFalse(player.isAlive)
        assertEquals("one setup for both", 1, f.setups)
        assertTrue("Play showed the background run's words", said.contains("setting up"))
        assertTrue(f.lines.any { "joined" in it })
    }

    @Test fun aFailedBackgroundRunLeavesPlayToDoItAndSayWhy() {
        val f = Fake(); val c = f.core()
        f.setupBody = { if (f.setups == 1) throw java.io.IOException("offline") }
        c.background()
        assertEquals(0, f.starts)
        f.setupBody = { throw java.io.IOException("still offline") }
        try {
            c.play { _, _ -> }
            fail("Play's own setup failure goes to Play")
        } catch (e: java.io.IOException) {
            assertEquals("still offline", e.message)
        }
    }

    @Test fun theServerFilesFingerprintSeesATableWrittenAgain() {
        val root = tmp.newFolder("files")
        val l = WowLayout(root, tmp.newFolder(".export"))
        val dbc = File(l.wrathppServer, "share/dbc").apply { mkdirs() }
        val table = File(dbc, "CharSections.dbc").apply { writeText("rows") }
        val a = WrathppPrewarm.serverFiles(l)
        assertEquals(a, WrathppPrewarm.serverFiles(l))
        table.writeText("rows")                          // the same bytes, written again
        table.setLastModified(table.lastModified() + 2000)
        assertNotEquals(a, WrathppPrewarm.serverFiles(l))
        val b = WrathppPrewarm.serverFiles(l)
        File(l.zones, "TAG").apply { parentFile!!.mkdirs(); writeText("zones 2") }
        assertNotEquals(b, WrathppPrewarm.serverFiles(l))
    }

    @Test fun theListingSkipsWhatItIsToldTo() {
        val dir = tmp.newFolder("d")
        File(dir, "keep.txt").writeText("1")
        File(dir, "server-wrathpp").mkdirs(); File(dir, "server-wrathpp/big.bin").writeText("x")
        val listing = WrathppPrewarm.listing(dir, 2) { it.name == "server-wrathpp" }
        assertTrue(listing.contains("keep.txt"))
        assertFalse(listing.contains("big.bin"))
    }
}
