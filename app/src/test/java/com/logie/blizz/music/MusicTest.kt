package com.logie.blizz.music

import com.logie.blizz.Games
import com.sun.net.httpserver.HttpServer
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File
import java.io.IOException
import java.net.InetSocketAddress

class MusicTest {
    @get:Rule val tmp = TemporaryFolder()

    private fun mp3(size: Int = 30_000) = ByteArray(size).also { "ID3".toByteArray().copyInto(it) }

    private fun server(vararg routes: Pair<String, Pair<String, ByteArray>>): HttpServer {
        val s = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
        for ((path, reply) in routes) s.createContext(path) { ex ->
            ex.responseHeaders.add("Content-Type", reply.first)
            ex.sendResponseHeaders(200, reply.second.size.toLong())
            ex.responseBody.use { it.write(reply.second) }
        }
        s.start()
        return s
    }

    @Test fun everyGameAndTheLauncherHaveATrack() {
        val keys = MusicCatalog.tracks.map { it.key }
        assertEquals(keys.size, keys.toSet().size)
        assertTrue(MusicCatalog.LAUNCHER in keys)
        for (game in Games.all.flatMap { listOf(it) + it.variants }) {
            if (game.id == "starcraft_remastered") continue
            assertTrue("no track for ${game.id}", MusicCatalog.keyFor(game.id) == game.id)
        }
        assertTrue(MusicCatalog.tracks.all { it.url.startsWith("https://") && "%25" !in it.url })
    }

    @Test fun theKeyFollowsTheInstallationShown() {
        assertEquals("starcraft", MusicCatalog.keyFor("starcraft_remastered"))
        assertEquals("warcraft3_tft", MusicCatalog.keyFor("warcraft3_tft"))
        assertEquals("warcraft3_roc", MusicCatalog.keyFor("warcraft3_roc"))
        assertEquals(MusicCatalog.LAUNCHER, MusicCatalog.keyFor(null))
        assertEquals(MusicCatalog.LAUNCHER, MusicCatalog.keyFor("nothing"))
    }

    @Test fun aPagesAudioAddressIsRead() {
        val html = """<html><audio id="audio" controls preload="auto" src="https://x.example/a/01.%20Song.mp3" ></audio></html>"""
        assertEquals("https://x.example/a/01.%20Song.mp3", MusicStore.audioUrlFromHtml(html, "https://p.example/page"))
        assertEquals("https://p.example/files/s.mp3", MusicStore.audioUrlFromHtml("""<a href="/files/s.mp3">x</a>""", "https://p.example/page"))
        assertNull(MusicStore.audioUrlFromHtml("<html>nothing</html>", "https://p.example/page"))
    }

    @Test fun audioIsToldFromPages() {
        val good = tmp.newFile("a.mp3").apply { writeBytes(mp3()) }
        val frame = tmp.newFile("b.mp3").apply { writeBytes(byteArrayOf(0xff.toByte(), 0xfb.toByte(), 0x90.toByte(), 0, 1, 2)) }
        val page = tmp.newFile("c.mp3").apply { writeText("<html>") }
        assertTrue(MusicStore.looksLikeAudio(good))
        assertTrue(MusicStore.looksLikeAudio(frame))
        assertFalse(MusicStore.looksLikeAudio(page))
    }

    @Test fun aSongIsDownloadedFromItsFileAndFromItsPage() {
        val server = server("/direct.mp3" to ("audio/mpeg" to mp3()), "/song" to ("text/html" to "<audio src=\"/direct.mp3\">".toByteArray()))
        try {
            val base = "http://127.0.0.1:${server.address.port}"
            val store = MusicStore(File(tmp.root, "music"))
            val a = store.download(MusicCatalog.Track("a", "A", "$base/direct.mp3"))
            assertTrue(a.isFile && store.has("a"))
            val b = store.download(MusicCatalog.Track("b", "B", "$base/song"))
            assertTrue(b.isFile && store.has("b"))
            assertFalse(File(tmp.root, "music/b.mp3.part").exists())
            assertFalse(store.has("c"))
        } finally { server.stop(0) }
    }

    @Test fun aPageThatIsNotAudioIsRefused() {
        val server = server("/bad" to ("audio/mpeg" to ByteArray(30_000) { 'x'.code.toByte() }), "/none" to ("text/html" to "<html>".toByteArray()))
        try {
            val base = "http://127.0.0.1:${server.address.port}"
            val store = MusicStore(File(tmp.root, "music"))
            for (path in listOf("/bad", "/none")) {
                try { store.download(MusicCatalog.Track("x", "X", base + path)); org.junit.Assert.fail("expected an error") } catch (e: IOException) { assertNotNull(e.message) }
            }
            assertFalse(store.has("x"))
            assertFalse(File(tmp.root, "music/x.mp3.part").exists())
        } finally { server.stop(0) }
    }

    @Test fun missingListsWhatIsNotThere() {
        val store = MusicStore(File(tmp.root, "music"))
        assertEquals(MusicCatalog.tracks.size, store.missing().size)
        File(tmp.root, "music").mkdirs()
        file(store, "diablo")
        assertEquals(MusicCatalog.tracks.size - 1, store.missing().size)
    }

    private fun file(store: MusicStore, key: String) = store.file(key).writeBytes(mp3())
}
