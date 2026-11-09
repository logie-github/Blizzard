package com.logie.blizz.ui

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.gestures.detectTransformGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.ui.unit.Dp
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Slider
import androidx.compose.material3.SliderDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.produceState
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.clipToBounds
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.IntSize
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.compose.foundation.shape.RoundedCornerShape
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File

/** The arithmetic of a crop: which part of a picture a frame of a given shape shows. Plain Kotlin, unit-tested. */
object CropMath {
    class Rect(val x: Int, val y: Int, val w: Int, val h: Int)

    /**
     * The part of an [iw] x [ih] picture a frame of [aspect] (width over height) shows at [zoom] (1 is the most of the picture the
     * frame can hold, bigger zooms in), centred on ([cx], [cy]) in the picture's own pixels, kept inside the picture.
     */
    fun rect(iw: Int, ih: Int, aspect: Float, zoom: Float, cx: Float, cy: Float): Rect {
        val z = zoom.coerceIn(1f, MAX_ZOOM)
        val baseW: Float; val baseH: Float
        if (iw.toFloat() / ih > aspect) { baseH = ih.toFloat(); baseW = baseH * aspect } else { baseW = iw.toFloat(); baseH = baseW / aspect }
        val w = (baseW / z).coerceAtLeast(1f); val h = (baseH / z).coerceAtLeast(1f)
        val x = (cx - w / 2f).coerceIn(0f, (iw - w).coerceAtLeast(0f))
        val y = (cy - h / 2f).coerceIn(0f, (ih - h).coerceAtLeast(0f))
        return Rect(x.toInt(), y.toInt(), w.toInt().coerceIn(1, iw), h.toInt().coerceIn(1, ih))
    }

    const val MAX_ZOOM = 6f
}

/** Where the sources of cropped pictures are kept, so a crop can be adjusted again from the whole picture. */
object ArtSources {
    private fun dir(context: Context) = File(context.filesDir, "art-src")
    fun file(context: Context, gameId: String, slot: String): File? = File(dir(context), "$gameId-$slot.jpg").takeIf { it.isFile }

    /** The picture at [uri] saved as the source of [gameId]'s [slot] (scaled to at most 2400 px a side); null if it can't be read. */
    fun stage(context: Context, gameId: String, slot: String, uri: Uri): File? = runCatching {
        val resolver = context.contentResolver
        val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
        if (resolver.openInputStream(uri)?.use { BitmapFactory.decodeStream(it, null, bounds); true } != true) return null
        if (bounds.outWidth <= 0 || bounds.outHeight <= 0) return null
        var sample = 1
        while (maxOf(bounds.outWidth, bounds.outHeight) / (sample * 2) >= 2400) sample *= 2
        val bitmap = resolver.openInputStream(uri)?.use { BitmapFactory.decodeStream(it, null, BitmapFactory.Options().apply { inSampleSize = sample }) } ?: return null
        val target = File(dir(context), "$gameId-$slot.jpg")
        target.parentFile?.mkdirs()
        target.outputStream().use { bitmap.compress(Bitmap.CompressFormat.JPEG, 94, it) }
        target
    }.getOrNull()

    /** A built-in picture ([resource]) saved as the source of [gameId]'s [slot], to crop it. */
    fun stageResource(context: Context, gameId: String, slot: String, resource: Int): File? = runCatching {
        val bitmap = BitmapFactory.decodeResource(context.resources, resource) ?: return null
        val target = File(dir(context), "$gameId-$slot.jpg")
        target.parentFile?.mkdirs()
        target.outputStream().use { bitmap.compress(Bitmap.CompressFormat.JPEG, 94, it) }
        target
    }.getOrNull()

    fun clear(context: Context, gameId: String, slot: String) { File(dir(context), "$gameId-$slot.jpg").delete() }
}

/**
 * Crop a picture to a frame of [aspect]: drag to move, pinch or slide to zoom; what the frame shows is what is kept. [onSave] gets the
 * cropped bitmap.
 */
@Composable
fun CropDialog(title: String, source: File, aspect: Float, onSave: (Bitmap) -> Unit, onDismiss: () -> Unit, preloaded: Bitmap? = null) {
    // [preloaded]: the picture already in memory (the tests', which run where no JPEG can be decoded); else it is opened off the main thread.
    val bitmap by produceState<Bitmap?>(preloaded, source) { if (value == null) value = withContext(Dispatchers.IO) { runCatching { BitmapFactory.decodeFile(source.path) }.getOrNull() } }
    Dialog(onDismissRequest = onDismiss, properties = DialogProperties(usePlatformDefaultWidth = false)) {
        Sheet(title, onDismiss, maxWidth = 560.dp) {
            val bmp = bitmap
            Column(Modifier.verticalScroll(rememberScrollState()).padding(horizontal = 20.dp).padding(bottom = 18.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                if (bmp == null) {
                    Text("Opening the picture…", style = MaterialTheme.typography.bodyMedium, color = Colors.Mist)
                    return@Column
                }
                var zoom by remember { mutableFloatStateOf(1f) }
                var cx by remember { mutableFloatStateOf(bmp.width / 2f) }
                var cy by remember { mutableFloatStateOf(bmp.height / 2f) }
                // Kept inside the picture whatever the gesture does.
                val r = CropMath.rect(bmp.width, bmp.height, aspect, zoom, cx, cy)
                val image = remember(bmp) { bmp.asImageBitmap() }
                // The frame is as big as fits: never taller than 45 % of the screen, so the slider and the buttons stay in sight.
                val maxFrameHeight = androidx.compose.ui.platform.LocalConfiguration.current.screenHeightDp.dp * 0.45f
                Canvas(
                    Modifier.align(androidx.compose.ui.Alignment.CenterHorizontally).width(minOf(maxFrameHeight * aspect, 520.dp)).aspectRatio(aspect).clip(RoundedCornerShape(14.dp)).clipToBounds()
                        .pointerInput(bmp, aspect) {
                            detectTransformGestures { _, pan, z, _ ->
                                zoom = (zoom * z).coerceIn(1f, CropMath.MAX_ZOOM)
                                val now = CropMath.rect(bmp.width, bmp.height, aspect, zoom, cx, cy)
                                // a drag of the frame's width moves the view by the view's width, the other way
                                cx = (now.x + now.w / 2f) - pan.x * now.w / size.width
                                cy = (now.y + now.h / 2f) - pan.y * now.h / size.height
                            }
                        },
                ) {
                    drawImage(image, srcOffset = IntOffset(r.x, r.y), srcSize = IntSize(r.w, r.h), dstSize = IntSize(size.width.toInt(), size.height.toInt()))
                }
                Text("Drag to move, pinch or slide to zoom.", style = MaterialTheme.typography.bodySmall)
                Slider(
                    zoom, { zoom = it }, valueRange = 1f..CropMath.MAX_ZOOM,
                    colors = SliderDefaults.colors(thumbColor = Colors.Ice, activeTrackColor = Colors.Ice, inactiveTrackColor = Colors.Frost),
                )
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp, androidx.compose.ui.Alignment.End)) {
                    FrameButton("Reset", primary = false) { zoom = 1f; cx = bmp.width / 2f; cy = bmp.height / 2f }
                    FrameButton("Save") {
                        val cut = CropMath.rect(bmp.width, bmp.height, aspect, zoom, cx, cy)
                        // (never past the picture's edge, whatever rounding did)
                        val w = cut.w.coerceAtMost(bmp.width - cut.x).coerceAtLeast(1)
                        val h = cut.h.coerceAtMost(bmp.height - cut.y).coerceAtLeast(1)
                        onSave(Bitmap.createBitmap(bmp, cut.x.coerceIn(0, bmp.width - 1), cut.y.coerceIn(0, bmp.height - 1), w, h))
                    }
                }
            }
        }
    }
}
