package com.logie.blizz.wowclient

import java.io.ByteArrayOutputStream
import java.io.IOException
import java.nio.ByteBuffer
import java.nio.ByteOrder

/**
 * World of Warcraft's textures (BLP2), as far as the launcher needs them: [read] any of the kinds the game's files come
 * in (palettized, DXT1/3/5, raw) to plain pixels, and [writePalette] the kind 3.3.5 composes a character's skin from
 * (256 colours, with its smaller copies; alpha for the pieces laid over a skin). A port of the realm tools' `blp.py`
 * (realm/warcraft/modules/mod-allied-races/tools), checked against it on real textures (BlpTest).
 */
object Blp {
    /** Pixels, a row after a row from the top: red, green, blue, alpha a pixel. */
    class Image(val width: Int, val height: Int, val rgba: ByteArray) {
        init { require(rgba.size == width * height * 4) { "pixels don't fit ${width}x$height" } }

        /** The left half (today's body texture is twice as wide as tall: the body is its left half). */
        /** Nothing of it shows (every pixel's alpha next to none). */
        fun empty(): Boolean { for (i in 0 until width * height) if ((rgba[i * 4 + 3].toInt() and 255) >= 16) return false; return true }

        fun leftHalf(): Image {
            val w = width / 2
            val out = ByteArray(w * height * 4)
            for (y in 0 until height) System.arraycopy(rgba, y * width * 4, out, y * w * 4, w * 4)
            return Image(w, height, out)
        }

        /** Made [w] x [h]: each new pixel the mean of the old ones it covers (smaller) or the nearest (larger). */
        fun resized(w: Int, h: Int): Image {
            if (w == width && h == height) return this
            val out = ByteArray(w * h * 4)
            for (y in 0 until h) {
                val y0 = y * height / h
                val y1 = maxOf(y0 + 1, (y + 1) * height / h)
                for (x in 0 until w) {
                    val x0 = x * width / w
                    val x1 = maxOf(x0 + 1, (x + 1) * width / w)
                    var r = 0; var g = 0; var b = 0; var a = 0
                    for (sy in y0 until y1) for (sx in x0 until x1) {
                        val at = (sy * width + sx) * 4
                        r += rgba[at].toInt() and 255; g += rgba[at + 1].toInt() and 255; b += rgba[at + 2].toInt() and 255; a += rgba[at + 3].toInt() and 255
                    }
                    val n = (y1 - y0) * (x1 - x0)
                    val to = (y * w + x) * 4
                    out[to] = (r / n).toByte(); out[to + 1] = (g / n).toByte(); out[to + 2] = (b / n).toByte(); out[to + 3] = (a / n).toByte()
                }
            }
            return Image(w, h, out)
        }
    }

    /** A BLP2's width and height. */
    fun size(data: ByteArray): Pair<Int, Int> {
        if (data.size < 20 || String(data, 0, 4, Charsets.US_ASCII) != "BLP2") throw IOException("Not a BLP2 texture")
        val b = ByteBuffer.wrap(data).order(ByteOrder.LITTLE_ENDIAN)
        return b.getInt(12) to b.getInt(16)
    }

    /** A BLP2's largest picture. */
    fun read(data: ByteArray): Image {
        if (data.size < 148 + 1024 || String(data, 0, 4, Charsets.US_ASCII) != "BLP2") throw IOException("Not a BLP2 texture")
        val b = ByteBuffer.wrap(data).order(ByteOrder.LITTLE_ENDIAN)
        val compression = data[8].toInt() and 255
        val alphaDepth = data[9].toInt() and 255
        val alphaEncoding = data[10].toInt() and 255
        val width = b.getInt(12)
        val height = b.getInt(16)
        val at = b.getInt(20)
        val size = b.getInt(84)
        if (width <= 0 || height <= 0 || width > 8192 || height > 8192 || at < 0 || size < 0 || at.toLong() + size > data.size) throw IOException("A damaged BLP2 texture")
        val n = width * height
        val out = ByteArray(n * 4)
        when (compression) {
            1 -> {
                if (size < n) throw IOException("A damaged BLP2 texture")
                for (i in 0 until n) {
                    val p = 148 + (data[at + i].toInt() and 255) * 4
                    out[i * 4] = data[p + 2]; out[i * 4 + 1] = data[p + 1]; out[i * 4 + 2] = data[p]; out[i * 4 + 3] = 255.toByte()
                }
                when (alphaDepth) {
                    8 -> if (size >= 2 * n) for (i in 0 until n) out[i * 4 + 3] = data[at + n + i]
                    1 -> if (size >= n + (n + 7) / 8) for (i in 0 until n) out[i * 4 + 3] = if ((data[at + n + i / 8].toInt() shr (i % 8)) and 1 != 0) 255.toByte() else 0
                    4 -> if (size >= n + (n + 1) / 2) for (i in 0 until n) out[i * 4 + 3] = ((((data[at + n + i / 2].toInt() and 255) shr (4 * (i % 2))) and 15) * 17).toByte()
                }
            }
            2 -> dxt(data, at, size, width, height, if (alphaDepth == 0 || alphaEncoding == 0) 1 else if (alphaEncoding == 1) 3 else 5, out)
            3 -> {
                if (size < n * 4) throw IOException("A damaged BLP2 texture")
                for (i in 0 until n) {
                    out[i * 4] = data[at + i * 4 + 2]; out[i * 4 + 1] = data[at + i * 4 + 1]; out[i * 4 + 2] = data[at + i * 4]; out[i * 4 + 3] = data[at + i * 4 + 3]
                }
            }
            else -> throw IOException("A BLP2 texture of a kind not known ($compression)")
        }
        return Image(width, height, out)
    }

    private fun dxt(data: ByteArray, at: Int, size: Int, width: Int, height: Int, kind: Int, out: ByteArray) {
        val bw = (width + 3) / 4
        val bh = (height + 3) / 4
        val block = if (kind == 1) 8 else 16
        if (size < bw * bh * block) throw IOException("A damaged BLP2 texture")
        val colour = IntArray(16)       // four colours: r, g, b, a
        val alpha = IntArray(8)
        for (by in 0 until bh) for (bx in 0 until bw) {
            val p = at + (by * bw + bx) * block
            val c = p + block - 8
            val c0 = (data[c].toInt() and 255) or ((data[c + 1].toInt() and 255) shl 8)
            val c1 = (data[c + 2].toInt() and 255) or ((data[c + 3].toInt() and 255) shl 8)
            val bits = (data[c + 4].toInt() and 255) or ((data[c + 5].toInt() and 255) shl 8) or ((data[c + 6].toInt() and 255) shl 16) or ((data[c + 7].toInt() and 255) shl 24)
            for ((k, v) in intArrayOf(c0, c1).withIndex()) {
                colour[k * 4] = ((v shr 11) and 31) * 255 / 31; colour[k * 4 + 1] = ((v shr 5) and 63) * 255 / 63; colour[k * 4 + 2] = (v and 31) * 255 / 31; colour[k * 4 + 3] = 255
            }
            val four = c0 > c1 || kind != 1
            for (ch in 0 until 3) {
                colour[8 + ch] = if (four) (2 * colour[ch] + colour[4 + ch]) / 3 else (colour[ch] + colour[4 + ch]) / 2
                colour[12 + ch] = if (four) (colour[ch] + 2 * colour[4 + ch]) / 3 else 0
            }
            colour[11] = 255
            colour[15] = if (four) 255 else 0
            var abits = 0L
            if (kind == 5) {
                val a0 = data[p].toInt() and 255
                val a1 = data[p + 1].toInt() and 255
                alpha[0] = a0; alpha[1] = a1
                for (i in 2 until 8) alpha[i] = if (a0 > a1) ((8 - i) * a0 + (i - 1) * a1) / 7 else if (i < 6) ((6 - i) * a0 + (i - 1) * a1) / 5 else if (i == 6) 0 else 255
                for (i in 0 until 6) abits = abits or ((data[p + 2 + i].toLong() and 255L) shl (8 * i))
            }
            for (i in 0 until 16) {
                val x = bx * 4 + i % 4
                val y = by * 4 + i / 4
                if (x >= width || y >= height) continue
                val k = (bits ushr (2 * i)) and 3
                val to = (y * width + x) * 4
                out[to] = colour[k * 4].toByte(); out[to + 1] = colour[k * 4 + 1].toByte(); out[to + 2] = colour[k * 4 + 2].toByte()
                out[to + 3] = when (kind) {
                    3 -> ((((data[p + i / 2].toInt() and 255) shr (4 * (i % 2))) and 15) * 17).toByte()
                    5 -> alpha[((abits ushr (3 * i)) and 7L).toInt()].toByte()
                    else -> colour[k * 4 + 3].toByte()
                }
            }
        }
    }

    /**
     * [image] as a palettized BLP2 (256 colours picked by median cut over the picture's own colours), with its smaller
     * copies down to one pixel when [mips]: what 3.3.5 composes a character's skin from. Without alpha, or with the
     * picture's own, a byte a pixel after each level's ([alpha]: what the pieces laid over a skin, underwear, have).
     */
    fun writePalette(image: Image, mips: Boolean = true, alpha: Boolean = false): ByteArray {
        val palette = IntArray(256)                 // 0xRRGGBB
        val lookup = quantize(image, palette)       // a colour's 15 bits -> its palette entry
        val levels = ArrayList<ByteArray>()
        var level = image
        while (true) {
            val px = level.rgba
            val n = level.width * level.height
            val idx = ByteArray(if (alpha) n * 2 else n)
            for (i in 0 until n) idx[i] = lookup[bin(px[i * 4].toInt() and 255, px[i * 4 + 1].toInt() and 255, px[i * 4 + 2].toInt() and 255)]
            if (alpha) for (i in 0 until n) idx[n + i] = px[i * 4 + 3]
            levels.add(idx)
            if (!mips || (level.width == 1 && level.height == 1) || levels.size == 16) break
            level = level.resized(maxOf(1, level.width / 2), maxOf(1, level.height / 2))
        }
        val head = ByteBuffer.allocate(148 + 1024).order(ByteOrder.LITTLE_ENDIAN)
        head.put("BLP2".toByteArray(Charsets.US_ASCII)).putInt(1).put(1).put(if (alpha) 8 else 0).put(if (alpha) 8 else 0).put(if (mips) 1 else 0).putInt(image.width).putInt(image.height)
        var at = 148 + 1024
        for (i in 0 until 16) { head.putInt(20 + i * 4, if (i < levels.size) at else 0); if (i < levels.size) at += levels[i].size }
        for (i in 0 until 16) head.putInt(84 + i * 4, if (i < levels.size) levels[i].size else 0)
        for (i in 0 until 256) {
            head.put(148 + i * 4, (palette[i] and 255).toByte()); head.put(149 + i * 4, ((palette[i] shr 8) and 255).toByte())
            head.put(150 + i * 4, ((palette[i] shr 16) and 255).toByte()); head.put(151 + i * 4, 0)
        }
        val out = ByteArrayOutputStream(at)
        out.write(head.array())
        for (l in levels) out.write(l)
        return out.toByteArray()
    }

    private fun bin(r: Int, g: Int, b: Int) = ((r shr 3) shl 10) or ((g shr 3) shl 5) or (b shr 3)

    /**
     * Median cut: the picture's colours (gathered five bits a channel) split into 256 boxes, the box with the most pixels
     * among those more than one colour wide cut at its widest channel's median; a box's colour is its pixels' mean.
     * Fills [palette] and returns each colour bin's palette entry.
     */
    private fun quantize(image: Image, palette: IntArray): ByteArray {
        val count = IntArray(32768)
        val sums = Array(3) { LongArray(32768) }
        val px = image.rgba
        for (i in 0 until image.width * image.height) {
            val r = px[i * 4].toInt() and 255; val g = px[i * 4 + 1].toInt() and 255; val b = px[i * 4 + 2].toInt() and 255
            val k = bin(r, g, b)
            count[k]++; sums[0][k] += r.toLong(); sums[1][k] += g.toLong(); sums[2][k] += b.toLong()
        }
        var used = (0 until 32768).filter { count[it] > 0 }.toIntArray()
        class Box(val bins: IntArray) {
            val pixels = bins.sumOf { count[it].toLong() }
            fun channel(k: Int, ch: Int) = (k shr (10 - 5 * ch)) and 31
            val widest: Int
            val spread: Int
            init {
                var best = 0; var bestSpread = -1
                for (ch in 0 until 3) {
                    var lo = 31; var hi = 0
                    for (k in bins) { val v = channel(k, ch); if (v < lo) lo = v; if (v > hi) hi = v }
                    if (hi - lo > bestSpread) { bestSpread = hi - lo; best = ch }
                }
                widest = best; spread = bestSpread
            }
        }
        val boxes = ArrayList<Box>().apply { add(Box(used)) }
        while (boxes.size < 256) {
            val box = boxes.filter { it.spread > 0 && it.bins.size > 1 }.maxByOrNull { it.pixels } ?: break
            val sorted = box.bins.sortedBy { box.channel(it, box.widest) }
            var half = 0L; var cut = 0
            while (cut < sorted.size - 1 && half + count[sorted[cut]] <= box.pixels / 2) { half += count[sorted[cut]]; cut++ }
            if (cut == 0) cut = 1
            boxes.remove(box)
            boxes.add(Box(sorted.subList(0, cut).toIntArray()))
            boxes.add(Box(sorted.subList(cut, sorted.size).toIntArray()))
        }
        val lookup = ByteArray(32768)
        for ((i, box) in boxes.withIndex()) {
            var r = 0L; var g = 0L; var b = 0L
            for (k in box.bins) { r += sums[0][k]; g += sums[1][k]; b += sums[2][k]; lookup[k] = i.toByte() }
            val n = maxOf(1L, box.pixels)
            palette[i] = ((r / n).toInt() shl 16) or ((g / n).toInt() shl 8) or (b / n).toInt()
        }
        // a colour no pixel had (a smaller copy's blend) takes the nearest entry
        used = IntArray(0)
        for (k in 0 until 32768) if (count[k] == 0) {
            val r = ((k shr 10) and 31) * 8 + 4; val g = ((k shr 5) and 31) * 8 + 4; val b = (k and 31) * 8 + 4
            var best = 0; var bestD = Int.MAX_VALUE
            for (i in boxes.indices) {
                val dr = r - (palette[i] shr 16); val dg = g - ((palette[i] shr 8) and 255); val db = b - (palette[i] and 255)
                val d = dr * dr + dg * dg + db * db
                if (d < bestD) { bestD = d; best = i }
            }
            lookup[k] = best.toByte()
        }
        return lookup
    }
}
