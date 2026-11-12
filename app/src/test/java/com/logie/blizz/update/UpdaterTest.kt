package com.logie.blizz.update

import com.sun.net.httpserver.HttpServer
import org.junit.After
import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File
import java.io.IOException
import java.net.InetSocketAddress
import kotlin.random.Random
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class UpdaterTest {
    private val json = """[
        {"tag_name":"blizzard-build-15","name":"Blizzard 1.0.15","draft":false,"prerelease":false,"assets":[{"name":"Blizzard.apk","url":"https://api.github.com/a/15","size":200}]},
        {"tag_name":"blizzard-build-16","name":"Blizzard 1.0.16","draft":true,"prerelease":false,"assets":[{"name":"Blizzard.apk","url":"u16","size":1}]},
        {"tag_name":"blizzard-build-12","name":"Blizzard 1.0.12","draft":false,"prerelease":false,"assets":[{"name":"Blizzard.apk","url":"u12","size":1}]},
        {"tag_name":"other-build-99","name":"Other","draft":false,"prerelease":false,"assets":[{"name":"x.apk","url":"u99","size":1}]}
    ]"""

    @Test fun theNewestPublishedBuildOfThisApp() {
        val update = UpdatePicker.pick(Updater.parse(json), "blizzard-build", currentVersionCode = 12)!!
        assertEquals(15, update.versionCode)
        assertEquals("Blizzard 1.0.15", update.title)
        assertEquals("https://api.github.com/a/15", update.apk.url)
    }

    @Test fun nothingWhenUpToDate() {
        assertNull(UpdatePicker.pick(Updater.parse(json), "blizzard-build", currentVersionCode = 15))
    }

    // --- the download: carried on from where it stopped (reports #94 to #101: 260 MB started again from nothing six times) ---

    @get:Rule val tmp = TemporaryFolder()
    private val payload = Random(7).nextBytes(400_000)
    private val ranges = java.util.Collections.synchronizedList(ArrayList<String?>())
    /** What the fake file server does with each request in turn: bytes sent before the connection drops; null: all of it. */
    private val cuts = java.util.Collections.synchronizedList(ArrayList<Int?>())
    private var honourRange = true
    private var server: HttpServer? = null

    private fun serve(): String {
        val s = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
        s.createContext("/Blizzard.apk") { ex ->
            val range = ex.requestHeaders.getFirst("Range")
            ranges += range
            val from = if (honourRange) range?.removePrefix("bytes=")?.substringBefore('-')?.toInt() ?: 0 else 0
            if (from > payload.size) { ex.sendResponseHeaders(416, -1); ex.close(); return@createContext }
            val cut = if (cuts.isEmpty()) null else cuts.removeAt(0)
            if (cut == 0) { ex.close(); return@createContext }                         // dropped before an answer
            val body = payload.copyOfRange(from, payload.size)
            if (range != null && honourRange) ex.responseHeaders.add("Content-Range", "bytes $from-${payload.size - 1}/${payload.size}")
            ex.sendResponseHeaders(if (range != null && honourRange) 206 else 200, body.size.toLong())
            ex.responseBody.use { out ->
                if (cut != null) { out.write(body, 0, minOf(cut, body.size)); out.flush(); throw IOException("cut") }
                out.write(body)
            }
        }
        s.start()
        server = s
        return "http://127.0.0.1:${s.address.port}/Blizzard.apk"
    }

    @After fun stop() { server?.stop(0) }

    @Test fun aDroppedDownloadCarriesOnFromWhereItStopped() {
        val url = serve()
        cuts += listOf(150_000, 0, 100_000)                                             // drops, a dead try, drops again, then the rest
        val partial = File(tmp.root, "226-Blizzard.apk.part")
        val seen = ArrayList<Long>()
        Updater.fetch(url, partial, payload.size.toLong(), { done, _ -> seen += done }, pause = {})
        assertArrayEquals(payload, partial.readBytes())
        assertNull(ranges.first())
        val asked = ranges.drop(1).map { it!!.removePrefix("bytes=").removeSuffix("-").toInt() }
        assertTrue("each try asks for the rest: $asked", asked.size >= 2 && asked.all { it > 0 } && asked == asked.sorted())
        assertTrue("progress never goes back: $seen", seen == seen.sorted())
    }

    @Test fun whatArrivedIsKeptForTheNextTime() {
        val url = serve()
        cuts += listOf(120_000, 0, 0, 0, 0, 0, 0, 0)                                    // some of it, then nothing however often it is tried
        val partial = File(tmp.root, "226-Blizzard.apk.part")
        try { Updater.fetch(url, partial, payload.size.toLong(), { _, _ -> }, pause = {}); fail("finished") } catch (_: IOException) { }
        val kept = partial.length()
        assertTrue("kept $kept", kept in 1 until payload.size)
        cuts.clear()
        ranges.clear()
        Updater.fetch(url, partial, payload.size.toLong(), { _, _ -> }, pause = {})     // the next check
        assertArrayEquals(payload, partial.readBytes())
        assertEquals(listOf<String?>("bytes=$kept-"), ranges.toList())
    }

    @Test fun aServerThatSendsTheWholeFileAgainIsTakenFromTheStart() {
        val url = serve()
        honourRange = false
        val partial = File(tmp.root, "226-Blizzard.apk.part").apply { writeBytes(payload.copyOf(1000)) }
        Updater.fetch(url, partial, payload.size.toLong(), { _, _ -> }, pause = {})
        assertArrayEquals(payload, partial.readBytes())
    }

    @Test fun aHalfThatIsNotThisFilesIsDropped() {
        val url = serve()
        val partial = File(tmp.root, "226-Blizzard.apk.part").apply { writeBytes(ByteArray(payload.size + 10)) }   // longer than the file
        Updater.fetch(url, partial, payload.size.toLong(), { _, _ -> }, pause = {})
        assertArrayEquals(payload, partial.readBytes())
        partial.writeBytes(ByteArray(payload.size + 10))                               // and with the size not known: the server says "no such part"
        Updater.fetch(url, partial, 0, { _, _ -> }, pause = {})
        assertArrayEquals(payload, partial.readBytes())
    }

    @Test fun aFileThatIsNotThereGivesUpAtOnce() {
        val url = serve().replace("Blizzard.apk", "missing.apk")
        try { Updater.fetch(url, File(tmp.root, "x.part"), 10, { _, _ -> }, pause = { fail("tried again") }); fail("fetched") } catch (e: Updater.HttpException) { assertEquals(404, e.code) }
    }

    @Test fun onlyAHalfOfANewerBuildIsKept() {
        assertFalse(Updater.stale("226-Blizzard.apk.part", null, 212))
        assertTrue(Updater.stale("212-Blizzard.apk.part", null, 212))
        assertTrue(Updater.stale("Blizzard.apk.part", null, 212))                       // an older build's way of naming it
        assertFalse(Updater.stale("Blizzard.apk", 226, 212))
        assertTrue(Updater.stale("Blizzard.apk", 212, 212))
        assertTrue(Updater.stale("Blizzard.apk", null, 212))
        assertTrue(Updater.stale("something", null, 212))
    }
}
