package com.logie.blizz.importer

import org.json.JSONObject
import java.io.File
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest

/**
 * Downloads that survive being stopped: bytes go to `<name>.part`, a second attempt asks the
 * server for the rest (an HTTP Range request), and the file only gets its real name once it's
 * complete and its SHA-256 (when known) matches.
 */
class DownloadManager(private val open: (URL) -> HttpURLConnection = { it.openConnection() as HttpURLConnection }) {
    fun download(
        url: String,
        target: File,
        cancel: CancelToken,
        expectedSize: Long = 0,
        sha256: String? = null,
        onProgress: (done: Long, total: Long) -> Unit = { _, _ -> },
    ): File {
        if (target.isFile && (expectedSize == 0L || target.length() == expectedSize) && (sha256 == null || sha256(target) == sha256.lowercase())) {
            return target
        }
        target.parentFile?.mkdirs()
        val part = File(target.parentFile, target.name + ".part")
        var attempt = 0
        while (true) {
            cancel.check()
            try {
                fetch(url, part, cancel, expectedSize, onProgress)
                break
            } catch (e: IOException) {
                attempt++
                if (attempt >= 4) throw ImportException(Problem.DOWNLOAD_FAILED, "The download stopped (${e.message}). What's downloaded is kept: retry to go on from there.", url, e)
                Thread.sleep(1000L shl attempt)
            }
        }
        if (expectedSize > 0 && part.length() != expectedSize) {
            part.delete()
            throw ImportException(Problem.DOWNLOAD_FAILED, "The download came out the wrong size; it was thrown away. Retry.", url)
        }
        if (sha256 != null) {
            val actual = sha256(part)
            if (actual != sha256.lowercase()) {
                part.delete()
                throw ImportException(Problem.CORRUPT_ARCHIVE, "The download didn't match its published checksum; it was thrown away. Retry.", "expected $sha256, got $actual")
            }
        }
        target.delete()
        if (!part.renameTo(target)) throw ImportException(Problem.DOWNLOAD_FAILED, "Couldn't save the download.")
        return target
    }

    private fun fetch(url: String, part: File, cancel: CancelToken, expectedSize: Long, onProgress: (Long, Long) -> Unit) {
        val have = if (part.isFile) part.length() else 0L
        if (expectedSize > 0 && have == expectedSize) return
        val connection = open(URL(url))
        connection.connectTimeout = 20_000
        connection.readTimeout = 60_000
        connection.instanceFollowRedirects = true
        if (have > 0) connection.setRequestProperty("Range", "bytes=$have-")
        val code = connection.responseCode
        val append = code == HttpURLConnection.HTTP_PARTIAL && have > 0
        if (code != HttpURLConnection.HTTP_OK && code != HttpURLConnection.HTTP_PARTIAL) {
            if (code == 416 && have > 0) return
            throw IOException("HTTP $code")
        }
        val start = if (append) have else 0L
        val length = connection.contentLengthLong
        val total = when {
            expectedSize > 0 -> expectedSize
            length > 0 -> start + length
            else -> 0L
        }
        connection.inputStream.use { input ->
            java.io.FileOutputStream(part, append).buffered(1 shl 20).use { out ->
                val buffer = ByteArray(1 shl 16)
                var done = start
                onProgress(done, total)
                while (true) {
                    cancel.check()
                    val n = input.read(buffer)
                    if (n < 0) break
                    out.write(buffer, 0, n)
                    done += n
                    onProgress(done, total)
                }
            }
        }
        if (length > 0 && part.length() < start + length) throw IOException("connection closed early")
    }

    companion object {
        fun sha256(file: File): String {
            val digest = MessageDigest.getInstance("SHA-256")
            file.inputStream().use { input ->
                val buffer = ByteArray(1 shl 16)
                while (true) {
                    val n = input.read(buffer)
                    if (n < 0) break
                    digest.update(buffer, 0, n)
                }
            }
            return digest.digest().joinToString("") { "%02x".format(it) }
        }
    }
}

/** A file attached to a GitHub release, with the SHA-256 GitHub publishes for it when there is one. */
data class ReleaseAsset(val release: String, val name: String, val url: String, val size: Long, val sha256: String?)

/** Reads a project's latest GitHub release (its assets and their digests). */
open class GitHubReleases(private val open: (URL) -> HttpURLConnection = { it.openConnection() as HttpURLConnection }) {
    open fun latest(repo: String): List<ReleaseAsset> {
        val connection = open(URL("https://api.github.com/repos/$repo/releases/latest"))
        connection.setRequestProperty("Accept", "application/vnd.github+json")
        connection.connectTimeout = 15_000
        connection.readTimeout = 30_000
        val code = connection.responseCode
        if (code != 200) throw ImportException(Problem.DOWNLOAD_FAILED, "GitHub didn't answer (HTTP $code).")
        return parse(connection.inputStream.bufferedReader().use { it.readText() })
    }

    companion object {
        fun parse(json: String): List<ReleaseAsset> {
            val o = JSONObject(json)
            val tag = o.optString("tag_name")
            val assets = o.optJSONArray("assets") ?: return emptyList()
            return (0 until assets.length()).map { i ->
                val a = assets.getJSONObject(i)
                val digest = a.optString("digest").takeIf { it.startsWith("sha256:") }?.removePrefix("sha256:")
                ReleaseAsset(tag, a.getString("name"), a.getString("browser_download_url"), a.optLong("size"), digest)
            }
        }
    }
}
