package com.logie.blizz.forever.tact

import java.io.FileNotFoundException
import java.io.IOException
import java.io.InputStream
import java.net.HttpURLConnection
import java.net.URL

/**
 * Blizzard's public content delivery for one product: the version service (which build is current, and which
 * configs describe it) and the CDN servers (`<server>/<path>/<config|data>/ab/cd/<hash>`). HTTPS only (Android
 * refuses plain HTTP to apps like this one). No account or Battle.net is involved: this is what Blizzard's own
 * installer reads.
 */
class TactCdn(val product: String = "wowf", val region: String = "us") {
    data class Version(val buildConfig: String, val cdnConfig: String, val buildId: Int, val name: String, val productConfig: String)
    data class Servers(val path: String, val hosts: String, val servers: List<String>, val configPath: String, val listed: String = "")

    class NotFoundException(url: String) : FileNotFoundException(url)

    private val service = "https://$region.version.battle.net/v2/products/$product"

    fun version(): Version {
        val rows = Tact.parseTable(String(fetch(URL("$service/versions"), null), Charsets.UTF_8))
        val row = rows.firstOrNull { it["Region"] == region } ?: rows.firstOrNull() ?: throw IOException("No version of $product is published")
        return Version(
            row.getValue("BuildConfig"), row.getValue("CDNConfig"), row["BuildId"]?.toIntOrNull() ?: 0,
            row["VersionsName"].orEmpty(), row["ProductConfig"].orEmpty(),
        )
    }

    @Volatile private var servers: Servers? = null

    /** The CDN servers for [region]: their HTTPS addresses first (a plain-HTTP-only server is reached over HTTPS). */
    fun servers(): Servers = servers ?: run {
        val rows = Tact.parseTable(String(fetch(URL("$service/cdns"), null), Charsets.UTF_8))
        val row = rows.firstOrNull { it["Name"] == region } ?: rows.first()
        val listed = row["Servers"].orEmpty().split(' ').filter { it.isNotBlank() }.map { it.substringBefore('?').trimEnd('/') }
        val https = listed.filter { it.startsWith("https://") }
        val fromHosts = row["Hosts"].orEmpty().split(' ').filter { it.isNotBlank() }.map { "https://$it" }
        Servers(row.getValue("Path"), row["Hosts"].orEmpty(), (https + fromHosts).distinct().ifEmpty { listOf("https://us.cdn.blizzard.com") }, row["ConfigPath"].orEmpty(), row["Servers"].orEmpty())
            .also { servers = it }
    }

    private fun path(kind: String, hash: String, suffix: String) = "$kind/${hash.substring(0, 2)}/${hash.substring(2, 4)}/$hash$suffix"

    /**
     * A whole CDN file: `config`, or `data` (with [suffix] `.index` for an archive's index). What fails [verify] (it
     * isn't what its hash says) is fetched again, from the next server.
     */
    fun get(kind: String, hash: String, suffix: String = "", verify: (ByteArray) -> Boolean = { true }): ByteArray = withServers { base ->
        val bytes = fetch(URL("$base/${servers().path}/${path(kind, hash, suffix)}"), null)
        if (!verify(bytes)) throw CorruptDownloadException("$base gave $kind $hash$suffix with the wrong content (${bytes.size} bytes, beginning ${Verify.preview(bytes)})")
        bytes
    }

    /** The product's own config (from the configs path, not the product's). */
    fun productConfig(hash: String): ByteArray = withServers { base -> fetch(URL("$base/${servers().configPath}/${path("", hash, "").removePrefix("/")}"), null) }

    /** Opens [length] bytes from [offset] of a data file (an archive or a loose file), for streaming; the caller closes it. */
    fun open(hash: String, offset: Long, length: Long, attempt: Int): InputStream {
        val list = servers().servers
        val base = list[attempt % list.size]
        val connection = connect(URL("$base/${servers().path}/${path("data", hash, "")}"), offset until offset + length)
        return connection.inputStream
    }

    /**
     * A data file of [size] bytes into [target], read over [connections] connections at once (a byte range each, each
     * range retried on its own from the next server). The caller checks the result.
     */
    fun download(hash: String, size: Long, target: java.io.File, connections: Int) {
        java.io.RandomAccessFile(target, "rw").use { it.setLength(size) }
        val part = maxOf(4L shl 20, (size + connections - 1) / connections)
        val ranges = (0 until ((size + part - 1) / part).toInt()).map { it * part until minOf(size, (it + 1) * part) }
        val failure = java.util.concurrent.atomic.AtomicReference<Throwable?>()
        val threads = ranges.mapIndexed { i, range ->
            Thread {
                var attempt = 0
                while (true) {
                    try {
                        java.io.RandomAccessFile(target, "rw").use { out ->
                            out.seek(range.first)
                            open(hash, range.first, range.last - range.first + 1, attempt + i).use { input ->
                                val buffer = ByteArray(1 shl 16)
                                var left = range.last - range.first + 1
                                while (left > 0) {
                                    val n = input.read(buffer, 0, minOf(buffer.size.toLong(), left).toInt())
                                    if (n < 0) throw java.io.EOFException("$hash ended early")
                                    out.write(buffer, 0, n)
                                    left -= n
                                }
                            }
                        }
                        return@Thread
                    } catch (e: IOException) {
                        if (++attempt >= RETRIES) { failure.compareAndSet(null, e); return@Thread }
                        Thread.sleep(backoff(attempt))
                    }
                }
            }.apply { start() }
        }
        threads.forEach { it.join() }
        failure.get()?.let { throw it }
    }

    private fun <T> withServers(block: (String) -> T): T {
        val list = servers().servers
        var last: IOException? = null
        for (attempt in 0 until RETRIES) {
            try {
                return block(list[attempt % list.size])
            } catch (e: NotFoundException) {
                if (attempt >= list.size - 1) throw e
                last = e
            } catch (e: IOException) {
                last = e
                Thread.sleep(backoff(attempt))
            }
        }
        throw last ?: IOException("Download failed")
    }

    private fun fetch(url: URL, range: LongRange?): ByteArray {
        val connection = connect(url, range)
        try {
            return connection.inputStream.use { it.readBytes() }
        } finally { connection.disconnect() }
    }

    private fun connect(url: URL, range: LongRange?): HttpURLConnection {
        val c = url.openConnection() as HttpURLConnection
        c.connectTimeout = 30_000
        c.readTimeout = 60_000
        c.setRequestProperty("User-Agent", "Blizzard-Launcher")
        // The bytes as stored: Android's client asks for gzip and unpacks it by itself otherwise, which a byte range can't survive.
        c.setRequestProperty("Accept-Encoding", "identity")
        if (range != null) c.setRequestProperty("Range", "bytes=${range.first}-${range.last}")
        val code = c.responseCode
        when {
            code == HttpURLConnection.HTTP_NOT_FOUND -> { c.disconnect(); throw NotFoundException(url.toString()) }
            range != null && code != HttpURLConnection.HTTP_PARTIAL -> { c.disconnect(); throw IOException("$url: expected a partial reply, got $code") }
            code !in 200..299 -> { c.disconnect(); throw IOException("$url: HTTP $code") }
        }
        return c
    }

    companion object {
        const val RETRIES = 8
        fun backoff(attempt: Int): Long = minOf(30_000L, 1_000L shl minOf(attempt, 5))
    }
}
