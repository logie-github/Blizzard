package com.logie.blizz.forevernew

import java.io.IOException
import java.io.InputStream
import java.net.HttpURLConnection
import java.net.URL
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.zip.Inflater
import java.util.zip.InflaterInputStream

/**
 * Reads single entries out of a big zip that is on a server, with HTTP range requests, so the app takes the two database
 * files it needs (about 250 MB compressed) from Karrz's 490 MB Windows repack without downloading the rest of it. The repack
 * is never run or unpacked; its Windows programs are not read.
 *
 * Only plain (non-Zip64) zips with stored or deflated entries; anything else fails with a message. The caller checks the
 * entry's SHA-256 against a pinned value, so a server can't hand over other data.
 */
object RangeZip {
    /** Where the bytes come from: a total size and a ranged read. [InputStream] is positioned at [from]. */
    interface Source {
        val size: Long
        fun open(from: Long, length: Long): InputStream
    }

    data class Entry(val name: String, val method: Int, val compressed: Long, val size: Long, val crc: Long, val localOffset: Long)

    private fun le(b: ByteArray) = ByteBuffer.wrap(b).order(ByteOrder.LITTLE_ENDIAN)

    private fun readFully(input: InputStream, n: Int): ByteArray {
        val out = ByteArray(n); var off = 0
        while (off < n) { val r = input.read(out, off, n - off); if (r < 0) throw IOException("unexpected end of data"); off += r }
        return out
    }

    /** The central directory's entries. */
    fun list(source: Source): List<Entry> {
        val tailLen = minOf(source.size, 66_000L)
        val tail = source.open(source.size - tailLen, tailLen).use { it.readBytes() }
        var eocd = -1
        for (i in tail.size - 22 downTo 0) if (tail[i] == 0x50.toByte() && tail[i + 1] == 0x4b.toByte() && tail[i + 2] == 5.toByte() && tail[i + 3] == 6.toByte()) { eocd = i; break }
        if (eocd < 0) throw IOException("not a zip file")
        val e = le(tail.copyOfRange(eocd, tail.size))
        val count = e.getShort(10).toInt() and 0xffff
        val cdSize = e.getInt(12).toLong() and 0xffffffffL
        val cdOffset = e.getInt(16).toLong() and 0xffffffffL
        if (count == 0xffff || cdSize == 0xffffffffL || cdOffset == 0xffffffffL) throw IOException("Zip64 archives aren't supported")
        val cd = source.open(cdOffset, cdSize).use { readFully(it, cdSize.toInt()) }
        val b = le(cd)
        val entries = ArrayList<Entry>(count)
        var p = 0
        while (p + 46 <= cd.size && b.getInt(p) == 0x02014b50) {
            val method = b.getShort(p + 10).toInt() and 0xffff
            val crc = b.getInt(p + 16).toLong() and 0xffffffffL
            val comp = b.getInt(p + 20).toLong() and 0xffffffffL
            val size = b.getInt(p + 24).toLong() and 0xffffffffL
            val nameLen = b.getShort(p + 28).toInt() and 0xffff
            val extraLen = b.getShort(p + 30).toInt() and 0xffff
            val commentLen = b.getShort(p + 32).toInt() and 0xffff
            val offset = b.getInt(p + 42).toLong() and 0xffffffffL
            val name = String(cd, p + 46, nameLen, Charsets.UTF_8).replace('\\', '/')
            entries += Entry(name, method, comp, size, crc, offset)
            p += 46 + nameLen + extraLen + commentLen
        }
        return entries
    }

    /** The entry's uncompressed bytes, streamed. Close it when done. */
    fun open(source: Source, entry: Entry): InputStream {
        val header = source.open(entry.localOffset, 30).use { readFully(it, 30) }
        val h = le(header)
        if (h.getInt(0) != 0x04034b50) throw IOException("bad local header for ${entry.name}")
        val dataStart = entry.localOffset + 30 + (h.getShort(26).toInt() and 0xffff) + (h.getShort(28).toInt() and 0xffff)
        val raw = source.open(dataStart, entry.compressed)
        return when (entry.method) {
            0 -> raw
            8 -> InflaterInputStream(raw, Inflater(true), 1 shl 16)
            else -> { raw.close(); throw IOException("${entry.name} uses compression method ${entry.method}") }
        }
    }

    /** A [Source] over a URL that answers range requests (GitHub's release assets do, through their redirect). */
    class Http(private val url: String, override val size: Long, private val allowHttp: Boolean = false) : Source {
        override fun open(from: Long, length: Long): InputStream {
            var current = URL(url)
            repeat(8) {
                require(current.protocol == "https" || (allowHttp && current.protocol == "http")) { "Only HTTPS" }
                val c = (current.openConnection() as HttpURLConnection).apply {
                    connectTimeout = 30_000; readTimeout = 60_000; instanceFollowRedirects = false
                    setRequestProperty("User-Agent", "Blizzard-Launcher")
                    setRequestProperty("Range", "bytes=$from-${from + length - 1}")
                }
                when (val code = c.responseCode) {
                    in 300..399 -> { current = URL(current, c.getHeaderField("Location")); c.disconnect() }
                    HttpURLConnection.HTTP_PARTIAL -> return c.inputStream
                    else -> { c.disconnect(); throw IOException("The server did not answer a range request ($code)") }
                }
            }
            throw IOException("Too many redirects")
        }

        companion object {
            /** Asks for the first byte to learn the total size (`Content-Range: bytes 0-0/TOTAL`). */
            fun probe(url: String, allowHttp: Boolean = false): Http {
                var current = URL(url)
                repeat(8) {
                    val c = (current.openConnection() as HttpURLConnection).apply {
                        connectTimeout = 30_000; readTimeout = 60_000; instanceFollowRedirects = false
                        setRequestProperty("User-Agent", "Blizzard-Launcher"); setRequestProperty("Range", "bytes=0-0")
                    }
                    val code = c.responseCode
                    if (code in 300..399) { current = URL(current, c.getHeaderField("Location")); c.disconnect(); return@repeat }
                    val total = c.getHeaderField("Content-Range")?.substringAfter('/')?.toLongOrNull()
                    c.disconnect()
                    if (code != HttpURLConnection.HTTP_PARTIAL || total == null) throw IOException("The server doesn't support range requests")
                    return Http(current.toString(), total, allowHttp)
                }
                throw IOException("Too many redirects")
            }
        }
    }

    /** For tests and small files: a [Source] over bytes. */
    class Bytes(private val data: ByteArray) : Source {
        override val size get() = data.size.toLong()
        override fun open(from: Long, length: Long): InputStream = java.io.ByteArrayInputStream(data, from.toInt(), length.toInt())
    }

}
