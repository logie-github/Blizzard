package com.logie.blizz.wowclient

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Test
import java.io.IOException
import java.nio.ByteBuffer
import java.nio.ByteOrder

/** World of Warcraft's textures read and written ([Blp]). */
class BlpTest {
    private fun header(compression: Int, alphaDepth: Int, alphaEncoding: Int, w: Int, h: Int, pixels: ByteArray, palette: IntArray = IntArray(256)): ByteArray {
        val b = ByteBuffer.allocate(148 + 1024 + pixels.size).order(ByteOrder.LITTLE_ENDIAN)
        b.put("BLP2".toByteArray()).putInt(1).put(compression.toByte()).put(alphaDepth.toByte()).put(alphaEncoding.toByte()).put(0).putInt(w).putInt(h)
        b.putInt(20, 148 + 1024); b.putInt(84, pixels.size)
        for (i in 0 until 256) b.putInt(148 + i * 4, palette[i])        // blue, green, red, alpha as the bytes lie
        b.position(148 + 1024); b.put(pixels)
        return b.array()
    }

    private fun px(image: Blp.Image, x: Int, y: Int) = (0 until 4).map { image.rgba[(y * image.width + x) * 4 + it].toInt() and 255 }

    @Test fun readsADxt1Block() {
        // end colours pure red (0xF800) and pure blue (0x001F), four colours; the first row red, blue, 2/3 red, 2/3 blue
        val block = byteArrayOf(0x00, 0xF8.toByte(), 0x1F, 0x00, 0b11100100.toByte(), 0, 0, 0)
        val image = Blp.read(header(2, 0, 0, 4, 4, block))
        assertEquals(listOf(255, 0, 0, 255), px(image, 0, 0))
        assertEquals(listOf(0, 0, 255, 255), px(image, 1, 0))
        assertEquals(listOf(170, 0, 85, 255), px(image, 2, 0))
        assertEquals(listOf(85, 0, 170, 255), px(image, 3, 0))
        assertEquals(listOf(255, 0, 0, 255), px(image, 0, 3))
    }

    @Test fun readsDxt3AndDxt5Alpha() {
        val colour = byteArrayOf(0xFF.toByte(), 0xFF.toByte(), 0, 0, 0, 0, 0, 0)                       // white everywhere
        val dxt3 = Blp.read(header(2, 8, 1, 4, 4, byteArrayOf(0x0F, 0, 0, 0, 0, 0, 0, 0) + colour))   // first pixel's alpha 15 of 15, second 0
        assertEquals(listOf(255, 255, 255, 255), px(dxt3, 0, 0))
        assertEquals(0, px(dxt3, 1, 0)[3])
        val dxt5 = Blp.read(header(2, 8, 7, 4, 4, byteArrayOf(200.toByte(), 100, 0b00001000, 0, 0, 0, 0, 0) + colour))   // codes 0, 1, 0...
        assertEquals(200, px(dxt5, 0, 0)[3])
        assertEquals(100, px(dxt5, 1, 0)[3])
        assertEquals(200, px(dxt5, 2, 0)[3])
    }

    @Test fun readsPalettizedAndRaw() {
        val palette = IntArray(256).also { it[7] = 0x00102030 }                                         // bytes 30 20 10 00: blue 0x30, green 0x20, red 0x10
        val pal = Blp.read(header(1, 8, 8, 2, 1, byteArrayOf(7, 7, 255.toByte(), 9), palette))
        assertEquals(listOf(0x10, 0x20, 0x30, 255), px(pal, 0, 0))
        assertEquals(9, px(pal, 1, 0)[3])
        val raw = Blp.read(header(3, 8, 8, 1, 1, byteArrayOf(1, 2, 3, 4)))
        assertEquals(listOf(3, 2, 1, 4), px(raw, 0, 0))
    }

    @Test fun aSkinWrittenReadsBackAsItWas() {
        // a 64 x 64 picture of smooth skin tones with a darker patch: more colours than a palette holds
        val w = 64; val h = 64
        val rgba = ByteArray(w * h * 4)
        for (y in 0 until h) for (x in 0 until w) {
            val dark = if (x in 20..30 && y in 20..30) 60 else 0
            val at = (y * w + x) * 4
            rgba[at] = (200 - dark + x / 2).toByte(); rgba[at + 1] = (160 - dark + y / 2).toByte(); rgba[at + 2] = (140 - dark + (x + y) / 4).toByte(); rgba[at + 3] = 255.toByte()
        }
        val bytes = Blp.writePalette(Blp.Image(w, h, rgba))
        assertEquals(1, bytes[8].toInt())                                                               // palettized, as 3.3.5 composes from
        val b = ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN)
        assertEquals(64 * 64, b.getInt(84)); assertEquals(32 * 32, b.getInt(88)); assertEquals(1, b.getInt(84 + 6 * 4)); assertEquals(0, b.getInt(84 + 7 * 4))   // its smaller copies down to one pixel
        val back = Blp.read(bytes)
        var worst = 0
        for (i in rgba.indices) if (i % 4 != 3) worst = maxOf(worst, Math.abs((back.rgba[i].toInt() and 255) - (rgba[i].toInt() and 255)))
        assertTrue("worst channel error $worst", worst <= 8)
    }

    @Test fun halvesAndResizes() {
        val wide = Blp.Image(4, 2, ByteArray(32) { (it / 4).toByte() })                                 // pixel n is all n
        val half = wide.leftHalf()
        assertEquals(2, half.width)
        assertEquals(listOf(0, 1, 4, 5), (0 until 4).map { half.rgba[it * 4].toInt() })
        val small = half.resized(1, 1)
        assertEquals((0 + 1 + 4 + 5) / 4, small.rgba[0].toInt())
        assertEquals(4, half.resized(4, 4).width)
    }

    @Test fun refusesWhatIsntOne() {
        for (bad in listOf(ByteArray(10), ByteArray(2000), header(9, 0, 0, 4, 4, ByteArray(8)), header(2, 0, 0, 64, 64, ByteArray(8)))) {
            try { Blp.read(bad); fail("read") } catch (_: IOException) { }
        }
    }

    @Test fun aPieceIsWrittenWithItsAlpha() {
        val w = 8; val h = 4
        val rgba = ByteArray(w * h * 4)
        for (i in 0 until w * h) { rgba[i * 4] = 200.toByte(); rgba[i * 4 + 1] = 100; rgba[i * 4 + 2] = 50; rgba[i * 4 + 3] = (i * 8).toByte() }
        val image = Blp.Image(w, h, rgba)
        assertFalse(image.empty())
        val back = Blp.read(Blp.writePalette(image, alpha = true))
        assertEquals(8 to 4, Blp.size(Blp.writePalette(image, alpha = true)))
        for (i in 0 until w * h) assertEquals(i * 8, back.rgba[i * 4 + 3].toInt() and 255)
        assertEquals(listOf(200, 100, 50), (0 until 3).map { back.rgba[it].toInt() and 255 })
        assertEquals(255, Blp.read(Blp.writePalette(image)).rgba[3].toInt() and 255)   // without: all of it shows
        assertTrue(Blp.Image(2, 2, ByteArray(16)).empty())
    }
}
