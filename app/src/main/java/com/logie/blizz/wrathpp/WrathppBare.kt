package com.logie.blizz.wrathpp

import java.io.File
import java.io.IOException

/**
 * Body option on Wrath++: the women's underwear layer is off. Each
 * woman's underwear row of the game's character table (`CharSections`, section 4, in the looks' patch folder) keeps its
 * place, which the game asks for before it offers a skin, and loses its two textures: the game lays nothing over the
 * skin for a row without a name (the client's own code: `if (*underwearRec->m_textureName[0] && ...)`, and the same for
 * the torso's). The game's table alone: the server's copy only says which rows there are. Done at every Play after the
 * looks, Ralia's set and the undead skins have had the table (each of them may put rows back); nothing is written when
 * no row has a texture left. The men's rows are not touched. NOT run in the game; unit-tested.
 */
object WrathppBare {
    private const val UNDERWEAR = 4
    private const val FEMALE = 1

    /** The women's underwear rows of [rows] without their textures; how many were changed. */
    fun strip(rows: List<Array<Any>>): Int {
        var changed = 0
        for (row in rows) {
            if (row[2] != FEMALE || row[3] != UNDERWEAR) continue
            if ((row[4] as String).isEmpty() && (row[5] as String).isEmpty()) continue
            row[4] = ""; row[5] = ""
            changed++
        }
        return changed
    }

    /** [client]'s looks' table with the women's underwear taken out; how many rows were changed (0: none had any, or no looks). */
    fun apply(client: File): Int {
        val table = File(client, "Data/${WrathppLooks.PATCH}/DBFilesClient/CharSections.dbc")
        if (!table.isFile) return 0
        val dbc = WrathppUndead.Dbc.read(table.readBytes(), WrathppUndead.KINDS)
        val changed = strip(dbc.rows)
        if (changed == 0) return 0
        val tmp = File(table.path + ".tmp")
        tmp.writeBytes(dbc.write())
        if (!tmp.renameTo(table)) { table.delete(); if (!tmp.renameTo(table)) throw IOException("${table.path} couldn't be written") }
        return changed
    }
}
