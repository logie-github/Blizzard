package com.logie.blizz.music

import android.content.Context
import android.net.Uri
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import java.io.File

/**
 * A song of the person's own for one version of a game (Wrath+, Legion, OctoWoW, Warcraft III's Frozen Throne...), kept in
 * the app's own folder and played in place of the downloaded track while that version's page is open. One file per game id.
 */
object MusicCustom {
    private val _version = MutableStateFlow(0)
    /** Counts every change, so what shows the choice looks again. */
    val version: StateFlow<Int> = _version

    private fun dir(context: Context) = File(context.filesDir, "music-custom")

    /** The person's song for [gameId], or null. */
    fun file(context: Context, gameId: String): File? =
        File(dir(context), "$gameId.audio").takeIf { it.isFile && it.length() >= MusicStore.MIN_BYTES }

    /** The name of the person's song for [gameId] (the file's name), or null. */
    fun label(context: Context, gameId: String): String? =
        runCatching { File(dir(context), "$gameId.name").takeIf { it.isFile }?.readText()?.trim() }.getOrNull()?.takeIf { it.isNotEmpty() }

    /** [uri]'s song as [gameId]'s music; false (and nothing changed) when it can't be read or isn't audio. */
    fun set(context: Context, gameId: String, uri: Uri): Boolean = runCatching {
        val target = File(dir(context), "$gameId.audio")
        target.parentFile?.mkdirs()
        val part = File(target.parentFile, "$gameId.audio.part")
        context.contentResolver.openInputStream(uri)?.use { input -> part.outputStream().use { input.copyTo(it, 64 * 1024) } } ?: return false
        if (part.length() < MusicStore.MIN_BYTES || !MusicStore.looksLikeAudio(part)) { part.delete(); return false }
        target.delete()
        if (!part.renameTo(target)) { part.delete(); return false }
        val name = runCatching {
            context.contentResolver.query(uri, arrayOf(android.provider.OpenableColumns.DISPLAY_NAME), null, null, null)?.use { if (it.moveToFirst()) it.getString(0) else null }
        }.getOrNull() ?: uri.lastPathSegment?.substringAfterLast('/')
        runCatching { File(target.parentFile, "$gameId.name").writeText(name?.take(120) ?: "") }
        _version.value++
        true
    }.getOrDefault(false)

    /** Back to the downloaded track. */
    fun clear(context: Context, gameId: String) {
        File(dir(context), "$gameId.audio").delete()
        File(dir(context), "$gameId.name").delete()
        _version.value++
    }
}
