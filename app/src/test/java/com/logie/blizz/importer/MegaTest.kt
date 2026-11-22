package com.logie.blizz.importer

import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.InputStream
import java.io.OutputStream
import java.net.HttpURLConnection
import java.net.URL

/** A public MEGA file link: parsed, decrypted (a real vector from a real file) and downloaded with resume. */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class MegaTest {
    @get:Rule val tmp = TemporaryFolder()

    private val link = InfiniteImporter.SERVER_LINK

    private fun hex(s: String) = ByteArray(s.length / 2) { s.substring(it * 2, it * 2 + 2).toInt(16).toByte() }

    @Test fun theLinkIsParsedAndBadOnesRefused() {
        val l = Mega.parse(link)
        assertEquals("pvICFA5Q", l.id)
        assertEquals(32, l.key.size)
        for (bad in listOf("https://mega.nz/folder/pvICFA5Q#abc", "https://example.com/file/pvICFA5Q#wxQV0KH6QadFZmuFR7RGpmmU5ctvL1aRDHPo6xG_q-I", "https://mega.nz/file/pvICFA5Q#short")) {
            try { Mega.parse(bad); fail("accepted $bad") } catch (e: ImportException) { assertEquals(Problem.DOWNLOAD_FAILED, e.problem) }
        }
    }

    /** Bytes 80..111 of the server archive: its ciphertext from MEGA and its plaintext, from a file downloaded with megatools. */
    @Test fun aRealBlockDecryptsToTheFilesOwnBytes() {
        val cipher = Mega.cipher(Mega.parse(link), 80)
        val plain = cipher.doFinal(hex("6717859a4db077afa545bf316b8fa13b706bb6025f5b3ea7e3ffef89a1c28915"))
        assertArrayEquals(hex("aab3ab012d8e606c99760287d7abece9662624f16635b5779b90feee08f74979"), plain)
    }

    // ---- a fake MEGA: the API answers with an address and a size, the address serves the encrypted file by range ----

    private class Fake(url: URL, val serve: (URL, String?) -> Pair<Int, ByteArray>) : HttpURLConnection(url) {
        val sent = ByteArrayOutputStream()
        private var result: Pair<Int, ByteArray>? = null
        private fun answer(): Pair<Int, ByteArray> = result ?: serve(url, sent.toString()).also { result = it }
        override fun connect() = Unit
        override fun disconnect() = Unit
        override fun usingProxy() = false
        override fun getOutputStream(): OutputStream = sent
        override fun getResponseCode(): Int = answer().first
        override fun getInputStream(): InputStream = ByteArrayInputStream(answer().second)
    }

    private fun encrypt(l: Mega.Link, plain: ByteArray): ByteArray = Mega.cipher(l, 0).doFinal(plain)

    private fun fakeMega(l: Mega.Link, plain: ByteArray, requests: MutableList<String> = ArrayList()): (URL) -> HttpURLConnection {
        val enc = encrypt(l, plain)
        return { url ->
            Fake(url) { u, body ->
                requests += u.toString()
                if (u.host == "g.api.mega.co.nz") 200 to """[{"s":${plain.size},"g":"https://store.example/dl/x"}]""".toByteArray()
                else {
                    val range = Regex("""/(\d+)-(\d+)$""").find(u.path)!!
                    val a = range.groupValues[1].toInt(); val b = range.groupValues[2].toInt()
                    206 to enc.copyOfRange(a, b + 1)
                }
            }
        }
    }

    @Test fun aFileDownloadsDecrypted() {
        val l = Mega.parse(link)
        val plain = ByteArray(100_003) { (it * 7).toByte() }
        val target = tmp.newFile("server.7z").also { it.delete() }
        val progress = ArrayList<Long>()
        Mega.download(l, target, CancelToken(), plain.size.toLong(), fakeMega(l, plain)) { done, _ -> progress += done }
        assertArrayEquals(plain, target.readBytes())
        assertEquals(plain.size.toLong(), progress.last())
    }

    @Test fun aPartFileGoesOnFromItsLastWholeBlock() {
        val l = Mega.parse(link)
        val plain = ByteArray(50_000) { (it * 13).toByte() }
        val target = tmp.newFile("resume.7z").also { it.delete() }
        // 20,010 bytes are written: the last whole block is at 20,000, so the file goes on from there, and the bytes in between are written again.
        java.io.File(target.parentFile, "resume.7z.part").writeBytes(plain.copyOf(20_010))
        val requests = ArrayList<String>()
        Mega.download(l, target, CancelToken(), plain.size.toLong(), fakeMega(l, plain, requests))
        assertArrayEquals(plain, target.readBytes())
        assertTrue(requests.toString(), requests.any { it.endsWith("/20000-49999") })
    }

    @Test fun aFinishedFileIsNotFetchedAgain() {
        val l = Mega.parse(link)
        val target = tmp.newFile("done.7z").also { it.writeBytes(ByteArray(64)) }
        Mega.download(l, target, CancelToken(), 64, open = { fail("fetched again"); throw IllegalStateException() })
    }

    @Test fun theDownloadLimitIsSaidPlainly() {
        val l = Mega.parse(link)
        val open: (URL) -> HttpURLConnection = { url -> Fake(url) { _, _ -> 200 to "[-17]".toByteArray() } }
        try {
            Mega.download(l, tmp.newFile("limit.7z").also { it.delete() }, CancelToken(), 0, open)
            fail("downloaded")
        } catch (e: ImportException) {
            assertEquals(Problem.DOWNLOAD_FAILED, e.problem)
            assertTrue(e.message!!, e.message!!.contains("limit"))
        }
    }
}
