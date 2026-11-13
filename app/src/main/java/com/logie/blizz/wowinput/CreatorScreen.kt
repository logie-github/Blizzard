package com.logie.blizz.wowinput

import java.io.File

/**
 * Wrath++'s character creator's word on what is on the screen (the native mod's `WrathPP_SetScreen`, written whole to the
 * game's `Logs/wrathpp-screen.txt`): "creator 1 drag <left bottom right top>..." while the creator is up, the areas where
 * a finger drags one of its lists (thousandths of the screen from its bottom left, as [InterfaceNote] reads them),
 * "creator 0" when it is not. The touch reads it before the picture of the screen ([CharacterCreation], the 3.3.5
 * creator's banners, which Wrath++'s Shadowlands screen has not: on it a swipe walked, W A S D Q E, in build 243).
 * Only a word written since this game started counts (a crash leaves the last one behind). Plain Kotlin, unit-tested.
 */
object CreatorScreen {
    /** Up (true), not (false), or nothing said ([text] null, or not one of its words). */
    fun up(text: String?): Boolean? {
        val words = text?.trim()?.split(' ')?.filter { it.isNotEmpty() } ?: return null
        if (words.size < 2 || words[0] != "creator") return null
        return when (words[1]) { "1" -> true; "0" -> false; else -> null }
    }

    /** Where a finger drags a list, from a word that says the creator is up. */
    fun dragAreas(text: String?): List<InterfaceNote.Area> = if (up(text) == true) InterfaceNote.dragAreas(text) else emptyList()

    /** The word in [file], if it was written at [since] or later (in the file system's milliseconds). */
    fun read(file: File, since: Long): String? =
        runCatching { file.takeIf { it.isFile && it.lastModified() >= since }?.readText() }.getOrNull()
}
