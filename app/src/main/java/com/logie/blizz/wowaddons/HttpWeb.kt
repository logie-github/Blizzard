// Ported from the World of Warcraft app (com.logie.warcraft), apart from its package.

package com.logie.blizz.wowaddons

import java.io.File
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URI
import java.net.URLEncoder
import java.util.concurrent.ConcurrentHashMap

/**
 * [Web] over HTTPS, as one visitor: the same [userAgent] on every request (the site's download
 * links are for the browser that asked for them) and the site's cookies kept between requests.
 */
class HttpWeb(private val userAgent: String) : Web {
    private val cookies = ConcurrentHashMap<String, String>()

    override fun get(url: String): String {
        val connection = open(url)
        connection.setRequestProperty("Accept", "text/html,application/xhtml+xml,*/*;q=0.8")
        return read(connection)
    }

    override fun post(url: String, form: List<Pair<String, String>>, referer: String): String {
        val body = form.joinToString("&") { (k, v) -> URLEncoder.encode(k, "UTF-8") + "=" + URLEncoder.encode(v, "UTF-8") }
            .toByteArray()
        val connection = open(url)
        connection.requestMethod = "POST"
        connection.doOutput = true
        connection.setRequestProperty("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8")
        connection.setRequestProperty("Accept", "application/json, */*;q=0.1")
        connection.setRequestProperty("X-Requested-With", "XMLHttpRequest")
        connection.setRequestProperty("Referer", referer)
        connection.setFixedLengthStreamingMode(body.size)
        connection.outputStream.use { it.write(body) }
        return read(connection)
    }

    override fun save(url: String, to: File, progress: (Long, Long) -> Unit) {
        val connection = open(url)
        try {
            check(connection)
            val size = connection.contentLengthLong
            if (size > MAX_FILE) throw IOException("The file is too big (${size / 1_048_576} MB)")
            val part = File(to.path + ".part")
            connection.inputStream.use { input ->
                part.outputStream().use { output ->
                    val buffer = ByteArray(64 * 1024)
                    var total = 0L
                    while (true) {
                        val n = input.read(buffer)
                        if (n < 0) break
                        output.write(buffer, 0, n)
                        total += n
                        if (total > MAX_FILE) throw IOException("The file is too big")
                        progress(total, size)
                    }
                }
            }
            if (!part.renameTo(to)) throw IOException("Couldn't keep the download")
        } finally {
            connection.disconnect()
        }
    }

    private fun open(url: String): HttpURLConnection =
        (URI(url).toURL().openConnection() as HttpURLConnection).apply {
            connectTimeout = 20_000
            readTimeout = 40_000
            instanceFollowRedirects = true
            setRequestProperty("User-Agent", userAgent)
            setRequestProperty("Accept-Language", "en-US,en;q=0.8")
            if (cookies.isNotEmpty() && isSite(url)) {
                setRequestProperty("Cookie", cookies.entries.joinToString("; ") { (k, v) -> "$k=$v" })
            }
        }

    private fun read(connection: HttpURLConnection): String =
        try {
            check(connection)
            val bytes = connection.inputStream.use { input ->
                val out = java.io.ByteArrayOutputStream()
                val buffer = ByteArray(32 * 1024)
                while (true) {
                    val n = input.read(buffer)
                    if (n < 0) break
                    out.write(buffer, 0, n)
                    if (out.size() > MAX_PAGE) throw IOException("The page is too big")
                }
                out.toByteArray()
            }
            String(bytes, Charsets.UTF_8)
        } finally {
            connection.disconnect()
        }

    private fun check(connection: HttpURLConnection) {
        val code = connection.responseCode
        if (isSite(connection.url.toString())) {
            for (header in connection.headerFields.filterKeys { it.equals("Set-Cookie", ignoreCase = true) }.values.flatten()) {
                val pair = header.substringBefore(';')
                val name = pair.substringBefore('=').trim()
                if (name.isNotEmpty() && '=' in pair) cookies[name] = pair.substringAfter('=').trim()
            }
        }
        if (code !in 200..299) throw HttpException(code)
    }

    private fun isSite(url: String) = Regex("""^https://(www\.)?warperia\.com(/|$)""").containsMatchIn(url)

    private companion object {
        const val MAX_PAGE = 8L * 1024 * 1024
        const val MAX_FILE = 512L * 1024 * 1024
    }
}
