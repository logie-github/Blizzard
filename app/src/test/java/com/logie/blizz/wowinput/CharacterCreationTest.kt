package com.logie.blizz.wowinput

import kotlin.test.Test
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class CharacterCreationTest {
    private val dark = 0xff101820.toInt()
    private val blue = 0xff2030a8.toInt()
    private val red = 0xffb01818.toInt()
    private val icon = 0xff806040.toInt()

    /** A picture of [width] x [height], dark, with what [paint] puts on it (x and y in heights). */
    private fun picture(width: Int, height: Int, paint: (IntArray, (Float, Float, Float, Float, Int) -> Unit) -> Unit = { _, _ -> }): IntArray {
        val pixels = IntArray(width * height) { dark }
        val rect = { x0: Float, y0: Float, x1: Float, y1: Float, color: Int ->
            for (y in (y0 * height).toInt() until (y1 * height).toInt().coerceAtMost(height)) {
                for (x in (x0 * height).toInt() until (x1 * height).toInt().coerceAtMost(width)) pixels[y * width + x] = color
            }
        }
        paint(pixels, rect)
        return pixels
    }

    /**
     * The stock 3.3.5a screen's left side, as measured on a phone's screenshot: the Alliance's banner
     * from 0.069 to 0.157 heights across, the Horde's from 0.192 to 0.29, from near the top to 0.47
     * down, five race icons on each, centred.
     */
    private fun banners(width: Int, height: Int, first: Int = blue, second: Int = red) = picture(width, height) { _, rect ->
        rect(0.069f, 0.03f, 0.157f, 0.47f, first)
        rect(0.192f, 0.03f, 0.29f, 0.47f, second)
        for (i in 0 until 5) {
            val top = 0.07f + i * 0.077f
            rect(0.085f, top, 0.141f, top + 0.05f, icon)
            rect(0.213f, top, 0.27f, top + 0.05f, icon)
        }
    }

    @Test
    fun theRaceBannersAreTheScreen() {
        // A phone's 20:9 screen, a tablet's 4:3 and a Fold's inside, as Winlator's small pictures.
        for ((width, height) in listOf(569 to 256, 341 to 256, 307 to 256, 160 to 120)) {
            assertTrue(CharacterCreation.isShown(banners(width, height), width, height), "$width x $height")
        }
    }

    @Test
    fun redAndBlueTheOtherWayRoundToo() {
        // A window read as RGBA: the blue banner reads red and the red one blue.
        assertTrue(CharacterCreation.isShown(banners(569, 256, first = red, second = blue), 569, 256))
    }

    @Test
    fun otherScreensAreNot() {
        assertFalse(CharacterCreation.isShown(picture(569, 256), 569, 256))
        // One banner only.
        val alliance = picture(569, 256) { _, rect -> rect(0.069f, 0.03f, 0.157f, 0.47f, blue) }
        assertFalse(CharacterCreation.isShown(alliance, 569, 256))
        // In the world: a player frame's mana and rage bars at the top left, a few rows only.
        val frame = picture(569, 256) { _, rect ->
            rect(0.07f, 0.05f, 0.16f, 0.08f, blue)
            rect(0.19f, 0.05f, 0.29f, 0.08f, red)
        }
        assertFalse(CharacterCreation.isShown(frame, 569, 256))
        // The banners somewhere else (further right).
        val elsewhere = picture(569, 256) { _, rect ->
            rect(0.6f, 0.03f, 0.7f, 0.47f, blue)
            rect(0.8f, 0.03f, 0.9f, 0.47f, red)
        }
        assertFalse(CharacterCreation.isShown(elsewhere, 569, 256))
        // Too small, or not a picture.
        assertFalse(CharacterCreation.isShown(banners(569, 256), 569, 10))
        assertFalse(CharacterCreation.isShown(IntArray(0), 0, 0))
        assertFalse(CharacterCreation.isShown(IntArray(10), 569, 256))
    }
}
