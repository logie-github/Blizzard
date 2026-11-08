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
 * How the launcher shows the games: the classic shelf, or tiles the person arranges (order, each
 * tile vertical or horizontal, how many across, their own pictures). Kept in the app's preferences
 * and files; changing any of it changes [state].
 */
object TileSettings {
    enum class Mode { SHELF, TILES }

    data class State(
        val mode: Mode = Mode.SHELF,
        val order: List<String> = emptyList(),
        /** Games whose tile is horizontal. */
        val wide: Set<String> = emptySet(),
        /** Tiles across; 0 picks as many as fit. */
        val columns: Int = 0,
        /** Changes when a picture does, so screens load it again. */
        val artVersion: Int = 0,
    )

    private const val PREFS = "tiles"
    private val _state = MutableStateFlow(State())
    val state: StateFlow<State> = _state

    private fun prefs(context: Context) = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)

    private fun csv(text: String?) = text?.split(',')?.filter { it.isNotEmpty() } ?: emptyList()

    fun load(context: Context) {
        val p = prefs(context)
        _state.value = State(
            mode = Mode.entries.firstOrNull { it.name == p.getString("mode", null) } ?: Mode.SHELF,
            order = csv(p.getString("order", null)),
            wide = csv(p.getString("wide", null)).toSet(),
            columns = p.getInt("columns", 0).coerceIn(0, TileLayout.MAX_COLUMNS),
            artVersion = _state.value.artVersion,
        )
    }

    fun setMode(context: Context, mode: Mode) {
        prefs(context).edit().putString("mode", mode.name).apply()
        _state.value = _state.value.copy(mode = mode)
    }

    fun setOrder(context: Context, order: List<String>) {
        prefs(context).edit().putString("order", order.joinToString(",")).apply()
        _state.value = _state.value.copy(order = order)
    }

    fun setWide(context: Context, id: String, wide: Boolean) {
        val set = if (wide) _state.value.wide + id else _state.value.wide - id
        prefs(context).edit().putString("wide", set.joinToString(",")).apply()
        _state.value = _state.value.copy(wide = set)
    }

    fun setColumns(context: Context, columns: Int) {
        val n = columns.coerceIn(0, TileLayout.MAX_COLUMNS)
        prefs(context).edit().putInt("columns", n).apply()
        _state.value = _state.value.copy(columns = n)
    }

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

    /** The tile layout as it came: order, orientations, size and pictures. The mode stays. */
    fun reset(context: Context) {
        prefs(context).edit().remove("order").remove("wide").remove("columns").apply()
        dir(context).deleteTree()
        _state.value = _state.value.copy(order = emptyList(), wide = emptySet(), columns = 0, artVersion = _state.value.artVersion + 1)
    }
}
