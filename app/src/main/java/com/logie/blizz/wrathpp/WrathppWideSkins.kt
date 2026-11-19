package com.logie.blizz.wrathpp

import java.io.File

/**
 * Wrath++'s whole skins (every hair style drawn with all of its triangles; README "Whole hair"): on unless switched off on
 * Settings' Wrath++ page, kept between runs. The looks carry two skins of each character model: its own, cut to the 65535
 * triangle indices the stock game reads, and the whole one beside it (`<Model>00w.skin`), which the app's native mod makes
 * the game draw (`client-mod/wrathpp-native`, "wide skins"). The app puts the switch into the game's interface patch as
 * `Interface\GlueXML\WrathppWideSkins.lua` (`WrathppWideSkins = 1`: a script that only sets a number, which the glue
 * screens ignore), where the native mod reads it as the interface starts (`wxl.storage`); off, every model is read with
 * its cut skin, as before the whole ones were.
 */
object WrathppWideSkins {
    const val FILE_NAME = "WrathppWideSkins.lua"
    private const val STORE = "wrathpp-wideskins"

    /** On until switched off. */
    fun on(filesDir: File): Boolean = File(filesDir, STORE).takeIf { it.isFile }?.readText()?.trim() != "off"

    fun set(filesDir: File, on: Boolean) {
        File(filesDir, STORE).writeText((if (on) "on" else "off") + "\n")
    }

    /** The patch's file. */
    fun script(on: Boolean): ByteArray = "WrathppWideSkins = ${if (on) 1 else 0}\n".toByteArray(Charsets.UTF_8)

    /**
     * The whole skins the app's body options make on the phone ([WrathppBody], [WrathppBodyLayer.add]), for the native mod: as
     * the looks' own `Wrathpp/wide.txt`, a line a model ("path without extension, vertices, bytes", tabs between), read after
     * it. The mod reads `<Model>00w.skin` in place of `<Model>00.skin` only for a model file of that vertex count and size.
     */
    const val BODY_LIST = "Wrathpp/wide-body.txt"

    /** `<Model>00w.skin` for `<Model>00.skin`. */
    fun wideName(skin: String): String = skin.removeSuffix(".skin") + "w.skin"

    /** [BODY_LIST]'s line for [model] (its path in the patch) as [bytes]. */
    fun line(model: String, bytes: ByteArray): String {
        val vertices = java.nio.ByteBuffer.wrap(bytes).order(java.nio.ByteOrder.LITTLE_ENDIAN).getInt(60)
        return model.removeSuffix(".m2").replace('/', '\\') + "\t" + vertices + "\t" + bytes.size
    }

    fun list(lines: List<String>): ByteArray =
        ("# Wrath++ (the app's body options): the models made on the phone that have a whole skin: model, its vertices, its bytes\n" +
            lines.joinToString("") { it + "\n" }).toByteArray(Charsets.UTF_8)
}
