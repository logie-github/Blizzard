package com.logie.blizz.ui

import androidx.compose.ui.graphics.Color
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ArtPaletteTest {
    private fun argb(r: Int, g: Int, b: Int) = (0xFF shl 24) or (r shl 16) or (g shl 8) or b

    private fun hueOf(c: Color): Float {
        val hsv = FloatArray(3)
        ArtPalette.rgbToHsv((c.red * 255).toInt(), (c.green * 255).toInt(), (c.blue * 255).toInt(), hsv)
        return hsv[0]
    }

    private fun value(c: Color) = maxOf(c.red, c.green, c.blue)

    /** A picture that is mostly red, from dark blood red to bright, with a little gold and a little cold blue. */
    private fun diabloLike(): IntArray = IntArray(3000) { i ->
        when {
            i < 1800 -> { val t = (i % 100) / 100f; argb((90 + 160 * t).toInt(), (10 + 30 * t).toInt(), (10 + 20 * t).toInt()) }
            i < 2400 -> argb(30, 4, 4)
            i < 2700 -> argb(250, 190, 40)
            else -> argb(30, 80, 200)
        }
    }

    @Test fun aRedPictureGivesRedHighsAndLowsAndAFewAccents() {
        val p = ArtPalette.of(diabloLike())
        assertTrue("red: ${hueOf(p.high)}", hueOf(p.high).let { it < 15f || it > 345f })
        assertTrue("red: ${hueOf(p.low)}", hueOf(p.low).let { it < 15f || it > 345f })
        assertTrue("the high is brighter than the low", value(p.high) > value(p.low))
        assertTrue("the low can still be seen", value(p.low) >= 0.4f)
        assertTrue(p.warm)
        assertTrue("some accents: ${p.accents.size}", p.accents.size in 1..3)
        assertTrue("one of them is the gold", p.accents.any { hueOf(it) in 30f..60f })
    }

    @Test fun aBluePictureFallsAsSnowNotEmbers() {
        val blue = IntArray(2000) { i -> val t = (i % 50) / 50f; argb((20 + 80 * t).toInt(), (60 + 120 * t).toInt(), (150 + 100 * t).toInt()) }
        val p = ArtPalette.of(blue)
        assertFalse(p.warm)
        assertTrue(hueOf(p.high) in 190f..235f)
    }

    @Test fun aPictureHalfInFiresHuesRisesEvenWhereABlueIsTheHeaviest() {
        // Warcraft II's cover: a big blue sea and an orange and red sky of about the same weight.
        val px = IntArray(4000) { i -> if (i < 2000) argb(30, 90 + (i % 40), 200) else if (i < 3300) argb(240, 120 + (i % 30), 20) else argb(200, 30, 20) }
        val p = ArtPalette.of(px)
        assertTrue(p.warm)
        assertTrue("main colour is the fire: ${hueOf(p.high)}", hueOf(p.high).let { it < 70f || it > 335f })
        assertTrue("the blue is an accent", p.accents.any { hueOf(it) in 190f..250f })
    }

    @Test fun aPictureWithNoColourKeepsWhiteSnow() {
        val grey = IntArray(500) { i -> val v = 20 + i % 200; argb(v, v, v) }
        val p = ArtPalette.of(grey)
        assertEquals(ArtPalette.Snow.high, p.high)
        assertFalse(p.warm)
        assertTrue(p.accents.isEmpty())
    }

    @Test fun transparentPixelsDoNotCount() {
        val p = ArtPalette.of(IntArray(100) { 0x00FF0000 })
        assertEquals(ArtPalette.Snow.high, p.high)
    }

    @Test fun particlesAreMostlyTheHighsThenTheLowsThenTheAccents() {
        val p = ArtPalette(Color.White, Color.Gray, listOf(Color.Red, Color.Green), warm = true)
        val picks = (0 until 1000).map { p.pick(it / 1000f) }
        assertTrue(picks.count { it == Color.White } > picks.count { it == Color.Gray })
        assertTrue(picks.count { it == Color.Gray } > picks.count { it == Color.Red })
        assertTrue(picks.any { it == Color.Red } && picks.any { it == Color.Green })
        assertEquals(Color.White, ArtPalette(Color.White, Color.Gray, emptyList(), false).pick(0.99f).let { if (it == Color.Gray) Color.White else it })
    }
}
