package com.logie.blizz.importer

import com.sun.net.httpserver.HttpServer
import org.junit.After
import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File
import java.net.InetSocketAddress
import kotlin.random.Random

/** 7. Interrupted downloads resume: a local server that cuts the first answer short and honours Range. */
class DownloadTest {
    @get:Rule val tmp = TemporaryFolder()
    private val payload = Random(1).nextBytes(300_000)
    private val ranges = ArrayList<String?>()
    private var cutFirst = true
    private lateinit var server: HttpServer
    private val url get() = "http://127.0.0.1:${server.address.port}/devilutionx.zip"

    @Before fun start() {
        server = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
        server.createContext("/devilutionx.zip") { ex ->
            val range = ex.requestHeaders.getFirst("Range")
            ranges += range
            val from = range?.removePrefix("bytes=")?.substringBefore('-')?.toInt() ?: 0
            val body = payload.copyOfRange(from, payload.size)
            ex.responseHeaders.add("Content-Length", body.size.toString())
            ex.sendResponseHeaders(if (range != null) 206 else 200, body.size.toLong())
            ex.responseBody.use { out ->
                if (cutFirst) {
                    cutFirst = false
                    out.write(body, 0, 100_000)
                    out.flush()
                    // The connection drops partway.
                    throw java.io.IOException("cut")
                }
                out.write(body)
            }
        }
        server.start()
    }

    @After fun stop() = server.stop(0)

    @Test fun aStoppedDownloadGoesOnFromWhereItWas() {
        val target = File(tmp.root, "devilutionx.zip")
        val sha = sha(payload)
        DownloadManager().download(url, target, CancelToken(), payload.size.toLong(), sha)
        assertArrayEquals(payload, target.readBytes())
        assertEquals(null, ranges.first())
        assertTrue("second request resumed: $ranges", ranges.drop(1).any { it != null && it.startsWith("bytes=") && it != "bytes=0-" })
        assertFalse(File(tmp.root, "devilutionx.zip.part").exists())
    }

    @Test fun aWrongChecksumIsThrownAway() {
        cutFirst = false
        val target = File(tmp.root, "x.zip")
        try {
            DownloadManager().download(url, target, CancelToken(), payload.size.toLong(), "0".repeat(64))
            fail("accepted a wrong checksum")
        } catch (e: ImportException) {
            assertEquals(Problem.CORRUPT_ARCHIVE, e.problem)
        }
        assertFalse(target.exists())
        assertFalse(File(tmp.root, "x.zip.part").exists())
    }

    @Test fun aCancelledDownloadKeepsWhatItHas() {
        cutFirst = false
        val cancel = CancelToken()
        val target = File(tmp.root, "y.zip")
        try {
            DownloadManager().download(url, target, cancel, payload.size.toLong()) { done, _ -> if (done > 50_000) cancel.cancel() }
            fail("not cancelled")
        } catch (e: ImportException) {
            assertEquals(Problem.CANCELLED, e.problem)
        }
        assertFalse(target.exists())
        assertTrue(File(tmp.root, "y.zip.part").length() > 0)
        // And the next attempt finishes it.
        DownloadManager().download(url, target, CancelToken(), payload.size.toLong())
        assertArrayEquals(payload, target.readBytes())
    }

    private fun sha(bytes: ByteArray) = java.security.MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }
}
