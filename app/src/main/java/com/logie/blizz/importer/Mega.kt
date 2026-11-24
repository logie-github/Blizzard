package com.logie.blizz.importer

import org.json.JSONArray
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL
import java.util.Base64
import javax.crypto.Cipher
import javax.crypto.spec.IvParameterSpec
import javax.crypto.spec.SecretKeySpec

/**
 * A public MEGA file link (`https://mega.nz/file/ID#KEY`), downloaded and decrypted on the phone. The key in the link's fragment
 * never goes to MEGA: the file arrives AES-128-CTR encrypted from MEGA's storage servers and is decrypted here as it is written.
 * The download resumes: a partly written file goes on from its last whole 16-byte block (the counter is the block number).
 * Checked against a real MEGA file (the first block and a block in the middle decrypt to the bytes of the same file downloaded by megatools).
 * The file's own MAC is not checked: the archive's format (7z's CRCs) says if a part is wrong.
 */
object Mega {
    class Link(val id: String, val key: ByteArray) {
        /** The AES key: the file key's two halves XORed. */
        val aesKey: ByteArray get() = ByteArray(16) { (key[it].toInt() xor key[16 + it].toInt()).toByte() }
        /** The counter's first 8 bytes: the second half's first 8 bytes. */
        val nonce: ByteArray get() = key.copyOfRange(16, 24)
    }

    class Info(val url: String, val size: Long)

    private fun b64(s: String): ByteArray = Base64.getUrlDecoder().decode(s.trim())

    /** The link's parts; refused when it isn't a file link with a 32-byte key. */
    fun parse(link: String): Link {
        val m = Regex("""^https?://mega\.nz/file/([A-Za-z0-9_-]{8})#([A-Za-z0-9_-]{43})$""").find(link.trim())
            ?: throw ImportException(Problem.DOWNLOAD_FAILED, "That isn't a MEGA file link.", link)
        val key = runCatching { b64(m.groupValues[2]) }.getOrNull()
        if (key == null || key.size != 32) throw ImportException(Problem.DOWNLOAD_FAILED, "That MEGA link's key is the wrong length.", link)
        return Link(m.groupValues[1], key)
    }

    /** The cipher for the data from byte [offset] on ([offset] a multiple of 16). */
    fun cipher(link: Link, offset: Long): Cipher {
        require(offset % 16 == 0L) { "offset must be a whole block" }
        val counter = java.nio.ByteBuffer.allocate(8).putLong(offset / 16).array()
        return Cipher.getInstance("AES/CTR/NoPadding").also { it.init(Cipher.DECRYPT_MODE, SecretKeySpec(link.aesKey, "AES"), IvParameterSpec(link.nonce + counter)) }
    }

    /** What MEGA's API says of the file: where to fetch it from and its size. [open] is replaceable for tests. */
    fun info(link: Link, open: (URL) -> HttpURLConnection = { it.openConnection() as HttpURLConnection }): Info {
        val connection = open(URL("https://g.api.mega.co.nz/cs?id=1"))
        connection.requestMethod = "POST"
        connection.doOutput = true
        connection.connectTimeout = 20_000
        connection.readTimeout = 30_000
        val body = """[{"a":"g","p":"${link.id}","g":1,"ssl":1}]"""
        connection.outputStream.use { it.write(body.toByteArray()) }
        val text = try {
            connection.inputStream.use { it.readBytes().toString(Charsets.UTF_8) }
        } catch (e: IOException) {
            throw ImportException(Problem.DOWNLOAD_FAILED, "MEGA couldn't be reached (${e.message}).", null, e)
        }
        val first = try { JSONArray(text).get(0) } catch (e: Exception) { throw ImportException(Problem.DOWNLOAD_FAILED, "MEGA's answer couldn't be read.", text.take(300), e) }
        if (first is Int) {
            val why = when (first) {
                -9 -> "MEGA says the file isn't there any more."
                -16 -> "MEGA says the file's owner closed that account."
                -17 -> "MEGA's download limit for this connection is used up for now: try again later, or pick the server file yourself."
                -18 -> "MEGA says the file can't be served right now: try again later."
                else -> "MEGA refused the download (error $first)."
            }
            throw ImportException(Problem.DOWNLOAD_FAILED, why, "MEGA error $first")
        }
        val json = first as? org.json.JSONObject ?: throw ImportException(Problem.DOWNLOAD_FAILED, "MEGA's answer couldn't be read.", text.take(300))
        val url = json.optString("g")
        val size = json.optLong("s", 0L)
        if (url.isEmpty() || size <= 0) throw ImportException(Problem.DOWNLOAD_FAILED, "MEGA gave no download address for the file.", text.take(300))
        return Info(url, size)
    }

    /**
     * The file at [link] into [target], decrypted. Goes on from a partly written `.part` beside it. [onProgress] gets (done, total).
     * A finished [target] of the right size is left as it is.
     */
    fun download(
        link: Link, target: File, cancel: CancelToken, expectedSize: Long = 0,
        open: (URL) -> HttpURLConnection = { it.openConnection() as HttpURLConnection },
        onProgress: (Long, Long) -> Unit = { _, _ -> },
    ): File {
        if (target.isFile && expectedSize > 0 && target.length() == expectedSize) return target
        target.parentFile?.mkdirs()
        val part = File(target.parentFile, target.name + ".part")
        var attempt = 0
        while (true) {
            cancel.check()
            try {
                fetch(link, part, cancel, expectedSize, open, onProgress)
                break
            } catch (e: IOException) {
                attempt++
                if (cancel.cancelled) throw ImportException(Problem.CANCELLED, "Cancelled.", null, e)
                if (attempt >= 4) throw ImportException(Problem.DOWNLOAD_FAILED, "The download stopped (${e.message}). What's downloaded is kept: retry to go on from there.", link.id, e)
                Thread.sleep(1000L shl attempt)
            }
        }
        target.delete()
        if (!part.renameTo(target)) throw ImportException(Problem.DOWNLOAD_FAILED, "Couldn't save the download.")
        return target
    }

    private fun fetch(link: Link, part: File, cancel: CancelToken, expectedSize: Long, open: (URL) -> HttpURLConnection, onProgress: (Long, Long) -> Unit) {
        val info = info(link, open)
        val total = info.size
        if (expectedSize > 0 && total != expectedSize) throw ImportException(Problem.DOWNLOAD_FAILED, "The file on MEGA isn't the size expected ($total, not $expectedSize).")
        // Whole 16-byte blocks only: what is past the last one is written again.
        var have = if (part.isFile) part.length() / 16 * 16 else 0L
        if (part.isFile && part.length() != have) java.io.RandomAccessFile(part, "rw").use { it.setLength(have) }
        if (have >= total) return
        FileValidator.requireSpace(part.parentFile ?: part, total - have)
        val connection = open(URL("${info.url}/$have-${total - 1}"))
        connection.connectTimeout = 20_000
        connection.readTimeout = 60_000
        val code = connection.responseCode
        if (code != HttpURLConnection.HTTP_OK && code != HttpURLConnection.HTTP_PARTIAL) throw IOException("HTTP $code")
        val cipher = cipher(link, have)
        connection.inputStream.use { input ->
            FileOutputStream(part, have > 0).use { out ->
                val buffer = ByteArray(1 shl 16)
                onProgress(have, total)
                while (true) {
                    cancel.check()
                    val n = input.read(buffer)
                    if (n < 0) break
                    cipher.update(buffer, 0, n)?.let { out.write(it) }
                    have += n
                    onProgress(have, total)
                }
                cipher.doFinal()?.takeIf { it.isNotEmpty() }?.let { out.write(it) }
            }
        }
        if (part.length() < total) throw IOException("connection closed early")
    }
}
