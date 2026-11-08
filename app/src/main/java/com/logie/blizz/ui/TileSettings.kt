package com.logie.blizz.ui

import com.logie.blizz.importer.deleteTree

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import java.io.File

/**
 * The pictures the person chose for a game's box (the library, the menus): kept in the app's files; changing one changes [state]
 * so screens load it again. (It was the tile layout's settings too: order, shapes and size, archived in
 * `archive/classic-look/ui/TileSettings.kt`.)
 */
object TileSettings {
    data class State(
        /** Changes when a picture does, so screens load it again. */
        val artVersion: Int = 0,
    )

    private val _state = MutableStateFlow(State())
    val state: StateFlow<State> = _state

    /** Kept for the callers that load it at start; the box pictures are read from files when asked for. */
    @Suppress("UNUSED_PARAMETER")
    fun load(context: Context) {}

    private fun dir(context: Context) = File(context.filesDir, "tiles")

    /** The person's own picture for [id]'s vertical or horizontal tile, if they chose one. */
    fun artFile(context: Context, id: String, wide: Boolean): File? =
        File(dir(context), "$id-${if (wide) "wide" else "tall"}.jpg").takeIf { it.isFile }

    /** [uri]'s picture as [id]'s tile art, scaled down to what a screen needs; false if it can't be read. */
    fun setArt(context: Context, id: String, wide: Boolean, uri: Uri): Boolean = runCatching {
        val resolver = context.contentResolver
        val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
        if (resolver.openInputStream(uri)?.use { BitmapFactory.decodeStream(it, null, bounds); true } != true) return false
        if (bounds.outWidth <= 0 || bounds.outHeight <= 0) return false
        val max = 1400
        var sample = 1
        while (maxOf(bounds.outWidth, bounds.outHeight) / (sample * 2) >= max) sample *= 2
        val bitmap = resolver.openInputStream(uri)?.use { BitmapFactory.decodeStream(it, null, BitmapFactory.Options().apply { inSampleSize = sample }) } ?: return false
        val scaled = if (maxOf(bitmap.width, bitmap.height) > max) {
            val f = max.toFloat() / maxOf(bitmap.width, bitmap.height)
            Bitmap.createScaledBitmap(bitmap, (bitmap.width * f).toInt().coerceAtLeast(1), (bitmap.height * f).toInt().coerceAtLeast(1), true)
        } else bitmap
        val target = File(dir(context), "$id-${if (wide) "wide" else "tall"}.jpg")
        target.parentFile?.mkdirs()
        val temp = File(target.parentFile, ".${target.name}.tmp")
        temp.outputStream().use { scaled.compress(Bitmap.CompressFormat.JPEG, 90, it) }
        target.delete()
        temp.renameTo(target)
        _state.value = _state.value.copy(artVersion = _state.value.artVersion + 1)
        true
    }.getOrDefault(false)

    /** Back to the original picture of one orientation. */
    fun clearArt(context: Context, id: String, wide: Boolean) {
        File(dir(context), "$id-${if (wide) "wide" else "tall"}.jpg").delete()
        _state.value = _state.value.copy(artVersion = _state.value.artVersion + 1)
    }
}
