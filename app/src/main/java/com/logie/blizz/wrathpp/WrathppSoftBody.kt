package com.logie.blizz.wrathpp

import java.io.File

/**
 * Wrath++'s soft body level (the women's chests move with the character: the native mod's springs on the breast bones, README "Soft body"):
 * Off, Subtle, Natural (the default) or Strong, chosen on Settings' Wrath++ page and kept between runs. The app puts it into the game's
 * interface patch as `Interface\GlueXML\WrathppSoftBody.lua` (`WrathppSoftBodyLevel = 2`: a script that only sets a number, which the
 * glue screens ignore), where the appearance add-on reads it (`wxl.storage.Read`) and tells the native mod (WrathPP_SetSoftBodyLevel).
 */
object WrathppSoftBody {
    enum class Level(val number: Int, val title: String) {
        OFF(0, "Off"), SUBTLE(1, "Subtle"), NATURAL(2, "Natural"), STRONG(3, "Strong"),
    }

    const val FILE_NAME = "WrathppSoftBody.lua"
    private const val STORE = "wrathpp-softbody"

    fun chosen(filesDir: File): Level =
        File(filesDir, STORE).takeIf { it.isFile }?.readText()?.trim()?.let { name -> Level.entries.firstOrNull { it.name == name } } ?: Level.NATURAL

    fun choose(filesDir: File, level: Level) {
        File(filesDir, STORE).writeText(level.name + "\n")
    }

    /** The patch's file for [level]. */
    fun script(level: Level): ByteArray = "WrathppSoftBodyLevel = ${level.number}\n".toByteArray(Charsets.UTF_8)
}
