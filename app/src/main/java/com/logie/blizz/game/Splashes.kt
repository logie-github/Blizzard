package com.logie.blizz.game

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import java.io.File

/**
 * A game's own loading screen, chosen by the person (hold a game's art): a background picture and
 * a logo over it, from any image on the phone, kept in the app's storage. Without them, the
 * game's built-in art (or its box art) is shown.
 */
object Splashes {
    enum class Kind(val file: String, val maxSide: Int) {
        BACKGROUND("background.jpg", 1920), LOGO("logo.png", 1024),
    }

    private val _version = MutableStateFlow(0)
    /** Changes whenever one is set or cleared, so screens showing them look again. */
    val version: StateFlow<Int> = _version

    private fun dir(context: Context, gameId: String) = File(File(context.filesDir, "splash"), gameId)

    fun file(context: Context, gameId: String, kind: Kind): File? = File(dir(context, gameId), kind.file).takeIf { it.isFile }

    /** The chosen image at [uri] as [kind] of [gameId]'s splash, scaled down to what a screen needs; false if it can't be read. */
    fun set(context: Context, gameId: String, kind: Kind, uri: Uri): Boolean = runCatching {
        val resolver = context.contentResolver
        val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
        // (Reading only the size returns no bitmap: the stream being there is what's checked.)
        if (resolver.openInputStream(uri)?.use { BitmapFactory.decodeStream(it, null, bounds); true } != true) return false
        if (bounds.outWidth <= 0 || bounds.outHeight <= 0) return false
        var sample = 1
        while (maxOf(bounds.outWidth, bounds.outHeight) / (sample * 2) >= kind.maxSide) sample *= 2
        val bitmap = resolver.openInputStream(uri)?.use { BitmapFactory.decodeStream(it, null, BitmapFactory.Options().apply { inSampleSize = sample }) } ?: return false
        val scaled = if (maxOf(bitmap.width, bitmap.height) > kind.maxSide) {
            val f = kind.maxSide.toFloat() / maxOf(bitmap.width, bitmap.height)
            Bitmap.createScaledBitmap(bitmap, (bitmap.width * f).toInt().coerceAtLeast(1), (bitmap.height * f).toInt().coerceAtLeast(1), true)
        } else bitmap
        val target = File(dir(context, gameId), kind.file)
        target.parentFile?.mkdirs()
        val temp = File(target.parentFile, ".${target.name}.tmp")
        temp.outputStream().use { scaled.compress(if (kind == Kind.LOGO) Bitmap.CompressFormat.PNG else Bitmap.CompressFormat.JPEG, 90, it) }
        target.delete()
        temp.renameTo(target)
        _version.value++
        true
    }.onFailure { lastError = it; android.util.Log.w("Splashes", "couldn't use the picture", it) }.getOrDefault(false)

    /** Why the last [set] failed (for the person's report and for tests). */
    @Volatile var lastError: Throwable? = null
        private set

    /** Back to the built-in picture: one [kind], or both. */
    fun clear(context: Context, gameId: String, kind: Kind? = null) {
        for (k in Kind.entries) if (kind == null || kind == k) File(dir(context, gameId), k.file).delete()
        _version.value++
    }
}
