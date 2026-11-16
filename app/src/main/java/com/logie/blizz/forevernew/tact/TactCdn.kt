package com.logie.blizz.forevernew.tact

import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL

/** Where the bytes of a content file come from, by its kind (config, data, ...) and hash; a range of it when asked. */
interface Cdn {
    fun get(kind: String, hash: String, from: Long = 0, length: Long = -1, suffix: String = ""): ByteArray
    fun size(kind: String, hash: String, suffix: String = ""): Long
}

/**
 * Blizzard's own public content servers, over HTTPS, the hosts their `cdns` file lists (tried in turn). No account is involved:
 * these are the files the Battle.net app itself downloads. Every file is named by its hash, and the caller checks it.
 */
class HttpCdn(hosts: List<String>, private val path: String, private val scheme: String = "https") : Cdn {
    /** The hosts in the order to try; the one that last answered goes first, so a host that doesn't answer isn't asked again for every piece. */
    private val order = java.util.concurrent.CopyOnWriteArrayList(hosts)

    private fun url(host: String, kind: String, hash: String, suffix: String) = "$scheme://$host/$path/$kind/${hash.substring(0, 2)}/${hash.substring(2, 4)}/$hash$suffix"

    private fun <T> eachHost(block: (String) -> T): T {
        var last: Exception? = null
        for (h in order.toList()) try {
            val r = block(h)
            if (order.first() != h) { order.remove(h); order.add(0, h) }
            return r
        } catch (e: IOException) { last = e } catch (e: java.net.SocketTimeoutException) { last = IOException(e.message, e) }
        throw IOException("No content server answered (${last?.message})")
    }

    override fun get(kind: String, hash: String, from: Long, length: Long, suffix: String): ByteArray {
        var last: IOException? = null
        repeat(3) { attempt ->
            try { return eachHost { host -> fetch(url(host, kind, hash, suffix), kind, hash, from, length) } }
            catch (e: IOException) { last = e; Thread.sleep(500L * (attempt + 1)) }
        }
        throw last!!
    }

    private fun fetch(url: String, kind: String, hash: String, from: Long, length: Long): ByteArray {
        val c = URL(url).openConnection() as HttpURLConnection
        c.connectTimeout = 12_000; c.readTimeout = 45_000; c.setRequestProperty("User-Agent", "Blizzard-Launcher")
        if (from > 0 || length >= 0) c.setRequestProperty("Range", "bytes=$from-" + if (length >= 0) (from + length - 1).toString() else "")
        try {
            val code = c.responseCode
            if (code != 200 && code != 206) throw IOException("HTTP $code for $kind/$hash")
            val bytes = c.inputStream.use { it.readBytes() }
            // the server ignored the range
            if (length >= 0 && code == 200 && bytes.size.toLong() != length) return bytes.copyOfRange(from.toInt(), (from + length).toInt())
            return bytes
        } finally { c.disconnect() }
    }

    override fun size(kind: String, hash: String, suffix: String): Long = eachHost { host ->
        val c = URL(url(host, kind, hash, suffix)).openConnection() as HttpURLConnection
        c.requestMethod = "HEAD"; c.connectTimeout = 12_000; c.readTimeout = 30_000
        try { if (c.responseCode != 200) throw IOException("HTTP ${c.responseCode}"); c.contentLengthLong } finally { c.disconnect() }
    }

    companion object {
        const val VERSIONS = "https://us.version.battle.net"

        /** `https://us.version.battle.net/<product>/versions` as rows. */
        fun fetch(url: String): String = (URL(url).openConnection() as HttpURLConnection).let { c ->
            c.connectTimeout = 30_000; c.readTimeout = 30_000
            try { if (c.responseCode != 200) throw IOException("HTTP ${c.responseCode} for $url"); c.inputStream.bufferedReader().readText() } finally { c.disconnect() }
        }
    }
}

/** A BLTE file on a CDN read by decoded position, fetching only the frames a read needs (the encoding file is hundreds of MB, a lookup needs one page of it). */
class BlteRandom(private val cdn: Cdn, private val ekey: String, private val rawSize: Long) {
    private val header: Blte.Header
    private val frameStart: LongArray   // decoded start of each frame
    private val rawStart: LongArray     // encoded start of each frame
    val size: Long
    private val cache = object : LinkedHashMap<Int, ByteArray>(16, 0.75f, true) { override fun removeEldestEntry(e: MutableMap.MutableEntry<Int, ByteArray>) = size > 8 }

    init {
        val first = cdn.get("data", ekey, 0, minOf(rawSize, 12L))
        val hs = be32(first, 4)
        val head = if (hs == 0) first else cdn.get("data", ekey, 0, hs.toLong())
        header = Blte.header(head)
        frameStart = LongArray(header.frames.size); rawStart = LongArray(header.frames.size)
        var d = 0L; var r = header.dataStart.toLong()
        for ((i, f) in header.frames.withIndex()) { frameStart[i] = d; rawStart[i] = r; d += f.decodedSize; r += f.encodedSize }
        size = d
    }

    private fun frame(i: Int): ByteArray = cache.getOrPut(i) {
        val f = header.frames[i]
        val raw = cdn.get("data", ekey, rawStart[i], f.encodedSize.toLong())
        Blte.decodeFrame(raw, 0, raw.size, f.decodedSize)
    }

    fun read(offset: Long, length: Int): ByteArray {
        val out = ByteArray(length); var done = 0
        var i = frameStart.indexOfLast { it <= offset }
        while (done < length) {
            val data = frame(i)
            val from = (offset + done - frameStart[i]).toInt()
            val n = minOf(length - done, data.size - from)
            System.arraycopy(data, from, out, done, n); done += n; i++
        }
        return out
    }
}

/** The encoding file: which encoded key holds the content of a content key. */
class EncodingFile(private val data: BlteRandom) {
    private val ckeySize: Int; private val ekeySize: Int; private val pageSize: Int; private val pageCount: Int
    private val pagesStart: Long
    private val firstKeys: Array<ByteArray>

    init {
        val h = data.read(0, 22)
        if (h[0] != 'E'.code.toByte() || h[1] != 'N'.code.toByte()) throw IOException("not an encoding file")
        ckeySize = h[3].toInt() and 0xff; ekeySize = h[4].toInt() and 0xff
        pageSize = be16(h, 5) * 1024; pageCount = be32(h, 9)
        val especBlock = be32(h, 18)
        val indexStart = 22L + especBlock
        val index = data.read(indexStart, pageCount * (ckeySize + 16))
        firstKeys = Array(pageCount) { index.copyOfRange(it * (ckeySize + 16), it * (ckeySize + 16) + ckeySize) }
        pagesStart = indexStart + pageCount.toLong() * (ckeySize + 16)
    }

    /** The first encoded key of [ckey], or null. */
    fun lookup(ckey: ByteArray): ByteArray? {
        var lo = 0; var hi = pageCount - 1; var page = -1
        while (lo <= hi) { val mid = (lo + hi) ushr 1; if (CascWriter.compareUnsigned(firstKeys[mid], ckey) <= 0) { page = mid; lo = mid + 1 } else hi = mid - 1 }
        if (page < 0) return null
        val p = data.read(pagesStart + page.toLong() * pageSize, pageSize)
        var o = 0
        while (o + 6 + ckeySize <= p.size) {
            val keys = p[o].toInt() and 0xff
            if (keys == 0) break
            val key = p.copyOfRange(o + 6, o + 6 + ckeySize)
            if (key.contentEquals(ckey)) return p.copyOfRange(o + 6 + ckeySize, o + 6 + ckeySize + ekeySize)
            o += 6 + ckeySize + keys * ekeySize
        }
        return null
    }
}
