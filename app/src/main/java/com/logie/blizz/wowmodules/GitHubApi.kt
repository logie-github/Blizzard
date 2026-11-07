
package com.logie.blizz.wowmodules

import org.json.JSONObject
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URI
import java.net.URL

/**
 * GitHub's API, with the user's token when there is one. Redirects are followed here: GitHub sends
 * release files from another server, and the token only ever goes to GitHub's API.
 */
class GitHubApi(private val token: () -> String?, private val userAgent: String) {
    /** GitHub said no: its status and its message. */
    class HttpError(val code: Int, val reason: String?) : IOException("HTTP $code" + (reason?.let { ": $it" } ?: ""))

    fun get(url: String, accept: String = JSON): String {
        val connection = open(url, accept)
        try {
            return connection.inputStream.bufferedReader().use { it.readText() }
        } finally {
            connection.disconnect()
        }
    }

    /** Sends [json]; the answer's status (GitHub answers some with no body). */
    fun post(url: String, json: String): Int = send(url, json).first

    /** Sends [json]; GitHub's answer (for one that makes something: what it made). */
    fun postForAnswer(url: String, json: String): String = send(url, json).second

    private fun send(url: String, json: String): Pair<Int, String> {
        val connection = (URI(url).toURL().openConnection() as HttpURLConnection).apply {
            requestMethod = "POST"
            doOutput = true
            connectTimeout = 15_000
            readTimeout = 30_000
            headers(this, URI(url).toURL(), JSON)
            setRequestProperty("Content-Type", "application/json")
        }
        try {
            connection.outputStream.use { it.write(json.toByteArray()) }
            val code = connection.responseCode
            if (code !in 200..299) throw HttpError(code, reason(connection))
            val answer = if (code == HttpURLConnection.HTTP_NO_CONTENT) "" else connection.inputStream.bufferedReader().use { it.readText() }
            return code to answer
        } finally {
            connection.disconnect()
        }
    }

    /**
     * [url] answered with 200 (or 206 when [rangeFrom] asks for the rest of a file), its redirects
     * followed. A server that ignores the range answers 200 with the whole file: the caller checks
     * `responseCode`.
     */
    fun open(url: String, accept: String, readTimeoutMs: Int = 30_000, rangeFrom: Long = 0): HttpURLConnection {
        var current = URI(url).toURL()
        repeat(MAX_REDIRECTS + 1) {
            val connection = (current.openConnection() as HttpURLConnection).apply {
                instanceFollowRedirects = false
                connectTimeout = 15_000
                readTimeout = readTimeoutMs
                headers(this, current, accept)
                if (rangeFrom > 0) setRequestProperty("Range", "bytes=$rangeFrom-")
            }
            val code = connection.responseCode
            when (code) {
                HttpURLConnection.HTTP_OK, HttpURLConnection.HTTP_PARTIAL -> return connection
                in 300..399 -> {
                    val location = connection.getHeaderField("Location")
                    connection.disconnect()
                    current = URL(current, location ?: throw HttpError(code, null))
                }
                else -> {
                    val reason = reason(connection)
                    connection.disconnect()
                    throw HttpError(code, reason)
                }
            }
        }
        throw IOException("Too many redirects")
    }

    private fun headers(connection: HttpURLConnection, url: URL, accept: String) {
        connection.setRequestProperty("Accept", accept)
        connection.setRequestProperty("User-Agent", userAgent)
        if (url.host == API_HOST) {
            connection.setRequestProperty("X-GitHub-Api-Version", "2022-11-28")
            token()?.takeIf { it.isNotBlank() }?.let { connection.setRequestProperty("Authorization", "Bearer $it") }
        }
    }

    /** GitHub's message about what went wrong, from the answer's body. */
    private fun reason(connection: HttpURLConnection): String? = runCatching {
        val body = connection.errorStream?.bufferedReader()?.use { it.readText() } ?: return null
        JSONObject(body).optString("message").takeIf { it.isNotBlank() }
    }.getOrNull()

    companion object {
        const val API_HOST = "api.github.com"
        const val JSON = "application/vnd.github+json"
        const val RAW = "application/vnd.github.raw"
        const val FILE = "application/octet-stream"
        private const val MAX_REDIRECTS = 5
    }
}
