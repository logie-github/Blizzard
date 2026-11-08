package com.logie.blizz.ui

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.produceState
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlin.math.abs
import kotlin.math.atan2
import kotlin.math.cos
import kotlin.math.max
import kotlin.math.min
import kotlin.math.sin

/**
 * The colours the particles over a picture are made of: read from the picture itself, so a red Diablo gets embers in the reds
 * its picture has, and an icy Lich King gets snow. [high] is the bright end of the picture's main colour, [low] its deep end,
 * [accents] a few other colours the picture has; [warm] says the colour is a fire's (reds, oranges, yellows), whose particles rise
 * as embers, where the cold ones fall as snow. A picture with hardly any colour gives the cool white of snow.
 */
class ArtPalette(val high: Color, val low: Color, val accents: List<Color>, val warm: Boolean) {
    /** The colour of the particle with this [seed] (0 to 1): mostly the highs, then the lows, then a few accents. */
    fun pick(seed: Float): Color = when {
        accents.isNotEmpty() && seed > 0.86f -> accents[((seed - 0.86f) / 0.14f * accents.size).toInt().coerceIn(0, accents.size - 1)]
        seed > 0.55f -> low
        else -> high
    }

    companion object {
        val Snow = ArtPalette(Color(0xFFE6F3FF), Color(0xFF9DB6C9), emptyList(), warm = false)

        /** [pixels] as ARGB ints (a few thousand are plenty): the palette of the picture they make. */
        fun of(pixels: IntArray): ArtPalette {
            val bins = 36
            val weight = DoubleArray(bins)
            val sinSum = DoubleArray(bins)
            val cosSum = DoubleArray(bins)
            val sats = Array(bins) { ArrayList<Float>() }
            val vals = Array(bins) { ArrayList<Float>() }
            var colourful = 0.0
            var counted = 0
            val hsv = FloatArray(3)
            for (p in pixels) {
                if ((p ushr 24) < 128) continue
                rgbToHsv((p shr 16) and 255, (p shr 8) and 255, p and 255, hsv)
                counted++
                // How much a pixel says about the picture's colour: saturated and not dark.
                val w = (hsv[1] * hsv[2]).toDouble().let { it * it }
                colourful += hsv[1] * hsv[2]
                if (w < 0.004) continue
                val bin = ((hsv[0] / 360f) * bins).toInt().coerceIn(0, bins - 1)
                weight[bin] += w
                val rad = Math.toRadians(hsv[0].toDouble())
                sinSum[bin] += sin(rad) * w
                cosSum[bin] += cos(rad) * w
                sats[bin] += hsv[1]
                vals[bin] += hsv[2]
            }
            if (counted == 0 || colourful / counted < 0.06) return Snow
            // The main colour: the heaviest bin with its neighbours (a colour straddles two bins).
            fun smoothed(i: Int) = weight[i] + 0.5 * (weight[(i + 1) % bins] + weight[(i + bins - 1) % bins])
            val main = (0 until bins).maxBy { smoothed(it) }
            val family = listOf((main + bins - 1) % bins, main, (main + 1) % bins)
            val hue = hueOf(family.sumOf { sinSum[it] }, family.sumOf { cosSum[it] })
            val familyVals = family.flatMap { vals[it] }.sorted()
            val familySats = family.flatMap { sats[it] }.sorted()
            fun pct(list: List<Float>, q: Float) = if (list.isEmpty()) 0.8f else list[((list.size - 1) * q).toInt()]
            // The highs and the lows of that colour: its bright end (paler), its deep end (never too dark to see).
            val high = hsvColor(hue, (pct(familySats, 0.3f) * 0.8f).coerceIn(0.25f, 0.9f), pct(familyVals, 0.92f).coerceIn(0.82f, 1f))
            val low = hsvColor(hue, pct(familySats, 0.7f).coerceIn(0.5f, 1f), pct(familyVals, 0.2f).coerceIn(0.4f, 0.7f))
            // Accents: other colours the picture has enough of, in their bright form.
            val mainWeight = smoothed(main)
            val accents = (0 until bins).filter { i -> i !in family && abs(angleBetween(i, main, bins)) > 2 }
                .sortedByDescending { smoothed(it) }
                .filter { smoothed(it) >= 0.12 * mainWeight }
                .fold(mutableListOf<Int>()) { chosen, i -> if (chosen.none { abs(angleBetween(it, i, bins)) <= 3 }) chosen += i; chosen }
                .take(3)
                .map { i -> hsvColor(hueOf(sinSum[i], cosSum[i]), 0.75f, 1f) }
            val warm = hue < 70f || hue >= 335f
            return ArtPalette(high, low, accents, warm)
        }

        /** The palette of [bitmap], read at a small size. */
        fun of(bitmap: Bitmap): ArtPalette {
            val w = 48
            val h = max(1, (48f * bitmap.height / bitmap.width.coerceAtLeast(1)).toInt())
            val small = Bitmap.createScaledBitmap(bitmap, w, h, true)
            val px = IntArray(w * h)
            small.getPixels(px, 0, w, 0, 0, w, h)
            if (small !== bitmap) small.recycle()
            return of(px)
        }

        private fun angleBetween(a: Int, b: Int, bins: Int): Int {
            var d = (a - b) % bins
            if (d > bins / 2) d -= bins
            if (d < -bins / 2) d += bins
            return d
        }

        private fun hueOf(sinSum: Double, cosSum: Double): Float {
            val deg = Math.toDegrees(atan2(sinSum, cosSum)).toFloat()
            return (deg + 360f) % 360f
        }

        fun rgbToHsv(r: Int, g: Int, b: Int, out: FloatArray) {
            val rf = r / 255f; val gf = g / 255f; val bf = b / 255f
            val mx = max(rf, max(gf, bf)); val mn = min(rf, min(gf, bf))
            val d = mx - mn
            val h = when {
                d == 0f -> 0f
                mx == rf -> 60f * (((gf - bf) / d) % 6f)
                mx == gf -> 60f * ((bf - rf) / d + 2f)
                else -> 60f * ((rf - gf) / d + 4f)
            }
            out[0] = (h + 360f) % 360f
            out[1] = if (mx == 0f) 0f else d / mx
            out[2] = mx
        }

        fun hsvColor(h: Float, s: Float, v: Float): Color {
            val c = v * s
            val x = c * (1f - abs((h / 60f) % 2f - 1f))
            val m = v - c
            val (r, g, b) = when {
                h < 60f -> Triple(c, x, 0f)
                h < 120f -> Triple(x, c, 0f)
                h < 180f -> Triple(0f, c, x)
                h < 240f -> Triple(0f, x, c)
                h < 300f -> Triple(x, 0f, c)
                else -> Triple(c, 0f, x)
            }
            return Color(r + m, g + m, b + m)
        }
    }
}

/**
 * The palette of a picture, worked out off the main thread when [key] changes ([ArtPalette.Snow] until then): [load] gives the
 * picture (a built-in drawable or the person's own file), at any size.
 */
@Composable
fun rememberArtPalette(key: Any, load: (android.content.Context) -> Bitmap?): ArtPalette {
    val context = LocalContext.current
    val palette by produceState(ArtPalette.Snow, key) {
        value = withContext(Dispatchers.Default) { runCatching { load(context)?.let { ArtPalette.of(it) } }.getOrNull() } ?: ArtPalette.Snow
    }
    return palette
}

/** A drawable resource as a small bitmap (at most about 256 px wide), for [rememberArtPalette]. */
fun smallResource(context: android.content.Context, id: Int): Bitmap? {
    val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
    BitmapFactory.decodeResource(context.resources, id, bounds)
    var sample = 1
    while (bounds.outWidth / (sample * 2) >= 256) sample *= 2
    return BitmapFactory.decodeResource(context.resources, id, BitmapFactory.Options().apply { inSampleSize = sample })
}

/** A picture file as a small bitmap, for [rememberArtPalette]. */
fun smallFile(file: java.io.File): Bitmap? {
    val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
    BitmapFactory.decodeFile(file.path, bounds)
    var sample = 1
    while (bounds.outWidth / (sample * 2) >= 256) sample *= 2
    return BitmapFactory.decodeFile(file.path, BitmapFactory.Options().apply { inSampleSize = sample })
}
