package com.logie.blizz.warsmash

import java.io.File

/**
 * Ordered layers: base, expansion, locale, patch, loose files, a pack of models and textures over them ([extra]: Classic+,
 * when it is on), then engine support overrides. A later layer's file wins.
 */
object WarsmashConfig {
    private val archives = listOf("war3.mpq", "war3local.mpq", "war3x.mpq", "war3xlocal.mpq", "war3patch.mpq")
    fun sources(game: File, support: File, extra: File? = null): String {
        val present = game.listFiles().orEmpty().filter { it.isFile }.associateBy { it.name.lowercase() }
        val layers = archives.mapNotNull { present[it]?.let { f -> "MPQ" to f } } +
            listOf("Folder" to game, "Folder" to File(game, "Maps")) +
            listOfNotNull(extra?.takeIf { it.isDirectory }?.let { "Folder" to it }) +
            listOf("Folder" to support)
        return buildString {
            append("[DataSources]\nCount=${layers.size}\n")
            layers.forEachIndexed { i, (type, file) ->
                val suffix = i.toString().padStart(2, '0')
                append("Type$suffix=$type\nPath$suffix=${file.absolutePath}\n")
            }
        }
    }
}
