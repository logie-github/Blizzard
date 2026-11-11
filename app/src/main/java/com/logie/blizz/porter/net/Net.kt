package com.logie.blizz.porter.net

import java.io.ByteArrayOutputStream
import java.io.File
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URI

/** What the character porter needs of the web: a page or a file, with the headers its sites want. Tests give their own. */
interface Net {
    class Reply(val code: Int, val bytes: ByteArray, val url: String) {
        val text: String get() = String(bytes, Charsets.UTF_8)
        val ok: Boolean get() = code in 200..299
    }

    /** The answer to a GET of [url], redirects followed; a refusal (404, 403) is an answer too. Throws only when nothing answered. */
    fun get(url: String, headers: Map<String, String> = emptyMap()): Reply

    /** A POST of [body] (a form, or JSON) to [url]. */
    fun post(url: String, body: ByteArray, headers: Map<String, String> = emptyMap()): Reply

    /** Saves [url] to [to] (written beside it first, so a file that is there is whole). Throws on anything but a 200 with bytes. */
    fun save(url: String, to: File, headers: Map<String, String> = emptyMap(), progress: (Long) -> Unit = {})
}

/** [Net] over HTTPS with one user agent. */
class HttpNet(private val userAgent: String) : Net {
    override fun get(url: String, headers: Map<String, String>): Net.Reply {
        val connection = open(url, headers)
        return read(connection)
    }

    override fun post(url: String, body: ByteArray, headers: Map<String, String>): Net.Reply {
        val connection = open(url, headers)
        connection.requestMethod = "POST"
        connection.doOutput = true
        connection.setFixedLengthStreamingMode(body.size)
        connection.outputStream.use { it.write(body) }
        return read(connection)
    }

    override fun save(url: String, to: File, headers: Map<String, String>, progress: (Long) -> Unit) {
        val connection = open(url, headers)
        try {
            val code = connection.responseCode
            if (code != 200) throw IOException("${URI(url).host} answered $code for ${url.substringAfterLast('/')}")
            to.parentFile?.mkdirs()
            val part = File(to.path + ".part")
            var total = 0L
            connection.inputStream.use { input ->
                part.outputStream().use { output ->
                    val buffer = ByteArray(64 * 1024)
                    while (true) {
                        val n = input.read(buffer)
                        if (n < 0) break
                        output.write(buffer, 0, n)
                        total += n
                        if (total > MAX_FILE) throw IOException("The file is too big")
                        progress(total)
                    }
                }
            }
            if (total == 0L) throw IOException("The file came empty")
            if (!part.renameTo(to)) throw IOException("Couldn't keep the download")
        } finally {
            connection.disconnect()
        }
    }

    private fun open(url: String, headers: Map<String, String>): HttpURLConnection =
        (URI(url).toURL().openConnection() as HttpURLConnection).apply {
            connectTimeout = 20_000
            readTimeout = 60_000
            instanceFollowRedirects = true
            setRequestProperty("User-Agent", userAgent)
            setRequestProperty("Accept-Language", "en-US,en;q=0.8")
            for ((name, value) in headers) setRequestProperty(name, value)
        }

    private fun read(connection: HttpURLConnection): Net.Reply =
        try {
            val code = connection.responseCode
            val stream = if (code in 200..399) connection.inputStream else connection.errorStream
            val out = ByteArrayOutputStream()
            stream?.use { input ->
                val buffer = ByteArray(32 * 1024)
                while (true) {
                    val n = input.read(buffer)
                    if (n < 0) break
                    out.write(buffer, 0, n)
                    if (out.size() > MAX_PAGE) throw IOException("The page is too big")
                }
            }
            Net.Reply(code, out.toByteArray(), connection.url.toString())
        } finally {
            connection.disconnect()
        }

    companion object {
        private const val MAX_PAGE = 16 * 1024 * 1024
        private const val MAX_FILE = 256L * 1024 * 1024
        /** A phone browser's, for the sites that serve pages to browsers (the Armory). */
        const val BROWSER = "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36"
    }
}
