package com.logie.blizz.forevernew

import java.io.File
import java.io.IOException
import java.io.RandomAccessFile
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest

/**
 * Downloads for Forever: HTTPS only, redirects followed (to HTTPS), resumed with a Range request from the `.part` file the
 * last try left, checked against a SHA-256 before the file gets its real name. A file that fails its check is deleted.
 */
object ForeverDownloads {
    class Failed(message: String) : IOException(message)

    /** [allowHttp]: only for tests against a local server. */
    fun fetchText(url: String, allowHttp: Boolean = false): String {
        val c = open(url, 0, allowHttp)
        return try { c.inputStream.bufferedReader().use { it.readText() } } finally { c.disconnect() }
    }

    /**
     * Downloads [url] to [dest] (via `dest.part`), resuming, and returns [dest] once its SHA-256 equals [sha256].
     * [onProgress] gets (bytes done, total or -1). If [dest] already exists with the right hash, nothing is downloaded.
     */
    fun fetch(url: String, dest: File, sha256: String, expectedSize: Long = -1, allowHttp: Boolean = false, onProgress: (Long, Long) -> Unit = { _, _ -> }): File {
        if (dest.isFile && sha256(dest).equals(sha256, ignoreCase = true)) return dest
        dest.parentFile?.mkdirs()
        val part = File(dest.path + ".part")
        repeat(2) { attempt ->
            var have = if (part.isFile) part.length() else 0L
            if (expectedSize in 1..have && have > expectedSize) { part.delete(); have = 0 }
            if (expectedSize <= 0 || have < expectedSize) {
                val c = open(url, have, allowHttp)
                try {
                    val resumed = c.responseCode == HttpURLConnection.HTTP_PARTIAL
                    if (!resumed) have = 0 // the server ignored the Range: from the start
                    val total = when {
                        resumed -> have + c.contentLengthLong
                        c.contentLengthLong > 0 -> c.contentLengthLong
                        else -> expectedSize
                    }
                    RandomAccessFile(part, "rw").use { out ->
                        out.setLength(have); out.seek(have)
                        val buffer = ByteArray(1 shl 16)
                        var done = have
                        c.inputStream.use { input ->
                            while (true) {
                                val n = input.read(buffer)
                                if (n < 0) break
                                out.write(buffer, 0, n); done += n
                                onProgress(done, total)
                            }
                        }
                    }
                } finally { c.disconnect() }
            }
            if (sha256(part).equals(sha256, ignoreCase = true)) {
                dest.delete()
                if (!part.renameTo(dest)) { part.copyTo(dest, overwrite = true); part.delete() }
                return dest
            }
            // Wrong bytes: a second try from nothing (a partial from another version of the file), then give up.
            part.delete()
            if (attempt == 1) throw Failed("${dest.name} did not match its checksum")
        }
        throw Failed("${dest.name} could not be downloaded")
    }

    private fun open(url: String, from: Long, allowHttp: Boolean): HttpURLConnection {
        var current = URL(url)
        repeat(8) {
            require(current.protocol == "https" || (allowHttp && current.protocol == "http")) { "Only HTTPS downloads are made" }
            val c = (current.openConnection() as HttpURLConnection).apply {
                connectTimeout = 30_000; readTimeout = 60_000; instanceFollowRedirects = false
                setRequestProperty("User-Agent", "Blizzard-Launcher")
                if (from > 0) setRequestProperty("Range", "bytes=$from-")
            }
            when (val code = c.responseCode) {
                in 300..399 -> { current = URL(current, c.getHeaderField("Location")); c.disconnect() }
                HttpURLConnection.HTTP_OK, HttpURLConnection.HTTP_PARTIAL -> return c
                416 -> { c.disconnect(); throw Failed("range not satisfiable") }
                else -> { c.disconnect(); throw Failed("Download failed ($code)") }
            }
        }
        throw Failed("Too many redirects")
    }

    fun sha256(file: File, onRead: (Long) -> Unit = {}): String {
        val digest = MessageDigest.getInstance("SHA-256")
        var read = 0L
        file.inputStream().buffered(1 shl 16).use { input ->
            val buffer = ByteArray(1 shl 16)
            while (true) { val n = input.read(buffer); if (n < 0) break; digest.update(buffer, 0, n); read += n; onRead(read) }
        }
        return digest.digest().joinToString("") { "%02x".format(it) }
    }
}
