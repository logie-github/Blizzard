package com.logie.blizz.wrathpp

import com.logie.blizz.wowclient.Mpq
import java.io.File
import java.io.IOException
import java.nio.ByteBuffer
import java.nio.ByteOrder

/**
 * Wrath++'s model variants: the options that give a character another model of the game's (the Orc man's Upright), in the looks
 * package (`Wrathpp/parts.txt`, lines `V race sex category choice model`: the model, made by sl_parts.variant_model, is the
 * character's own with that choice). A variant is a display: [apply] puts its rows (a CreatureModelData row of the race's model with
 * the variant's file, and a CreatureDisplayInfo row of the race's own display on it) into the game's tables, in the looks' patch, and
 * the server's, at [DISPLAY_BASE] + (the category less 1500) * 16 + the choice's value (the choice's number less one): the numbering wrathpp_appearance.h's
 * VariantDisplay has, whose module gives the character the display at login.
 *
 * It runs at every start and puts in what the looks' package carries (idempotent: its rows are taken out of a table before they are
 * put in). NOT run on a phone; the table work is unit-tested.
 */
object WrathppVariants {
    const val DISPLAY_BASE = 44000
    const val MODEL_BASE = 4400
    /** What the app wrote (the stamp's first line: the looks' package and the variants it had). */
    const val STAMP = "wrathpp-variants.stamp"

    /** One variant: the race and sex, the category and the choice's number (from 1), the model's path (a .m2, as the package names it). */
    data class Variant(val race: Int, val sex: Int, val category: Int, val choice: Int, val model: String)

    const val FIRST_CATEGORY = 1500
    const val CATEGORIES = 5

    /** wrathpp_appearance.h: kVariantDisplayBase + (category - 1500) * 16 + the option's value (the choice's number less one). */
    fun displayId(variant: Variant) = DISPLAY_BASE + (variant.category - FIRST_CATEGORY) * 16 + variant.choice - 1
    fun modelId(variant: Variant) = MODEL_BASE + (variant.category - FIRST_CATEGORY) * 32 + variant.choice - 1

    /** The `V` lines of a parts table. */
    fun parse(table: String): List<Variant> = table.lineSequence().mapNotNull { line ->
        val f = line.split('\t')
        if (f.size >= 6 && f[0] == "V") runCatching { Variant(f[1].toInt(), f[2].toInt(), f[3].toInt(), f[4].toInt(), f[5]) }.getOrNull() else null
    }.toList()

    /** ChrRaces: each race's male display (its fifth column). */
    internal fun maleDisplays(table: ByteArray): Map<Int, Int> {
        if (table.size < 20 || String(table, 0, 4, Charsets.US_ASCII) != "WDBC") throw IOException("ChrRaces.dbc isn't one of the game's tables")
        val b = ByteBuffer.wrap(table).order(ByteOrder.LITTLE_ENDIAN)
        val count = b.getInt(4); val fields = b.getInt(8); val size = b.getInt(12)
        if (fields < 6 || size < 24) throw IOException("ChrRaces.dbc has too few columns")
        return (0 until count).associate { b.getInt(20 + it * size) to b.getInt(20 + it * size + 4 * 4) }
    }

    /**
     * [displays] (and [models], the game's: null for the server's) with the variants' rows: for each, its model's row (the race's
     * model's with the variant's file) and its display (the race's own, on that model). [own]: each race's display for the sex.
     */
    internal fun addRows(displays: WrathppUndead.Dbc, models: WrathppUndead.Dbc?, variants: List<Variant>, own: (Variant) -> Int?) {
        displays.rows.removeAll { (it[0] as Int) in DISPLAY_BASE until DISPLAY_BASE + CATEGORIES * 16 }
        models?.rows?.removeAll { (it[0] as Int) in MODEL_BASE until MODEL_BASE + CATEGORIES * 32 }
        val byId = displays.rows.associateBy { it[0] as Int }
        val modelById = models?.rows?.associateBy { it[0] as Int }
        for (v in variants) {
            val base = byId[own(v) ?: continue] ?: continue
            val row = base.copyOf()
            row[0] = displayId(v)
            if (models != null) {
                val baseModel = modelById?.get(base[1] as Int) ?: continue
                val mrow = baseModel.copyOf()
                mrow[0] = modelId(v)
                mrow[2] = v.model.replace('/', '\\').removeSuffix(".m2").removeSuffix(".M2") + ".mdx"
                models.rows.add(mrow)
                row[1] = mrow[0]
            }
            displays.rows.add(row)
        }
    }

    /** Puts the package's variants' rows in the game's and the server's tables; what it did, or null for none in the package. */
    fun apply(client: File, server: File, data: File): String? {
        val patch = File(client, "Data/${WrathppLooks.PATCH}")
        val parts = File(patch, "Wrathpp/parts.txt").takeIf { it.isFile } ?: return clear(patch, server)
        val variants = parse(parts.readText())
        if (variants.isEmpty()) return clear(patch, server)
        val bodyStamp = File(patch, WrathppBody.STAMP).takeIf { it.isFile }?.readLines()?.firstOrNull().orEmpty()    // (the body options' rows are in the same tables)
        val stamp = variants.joinToString(";") { "${it.race}:${it.sex}:${it.choice}:${it.model}" } + " " + WrathppLooks.installedSha(client, server) + " " + bodyStamp
        val stamps = listOf(File(patch, STAMP), File(File(server, "share/dbc"), STAMP))
        if (stamps.all { it.isFile && it.readLines().firstOrNull() == stamp }) return "as before"
        val game = Mpq.Game(File(client, "Data"), listOf(WrathppLooks.PATCH.lowercase()))
        try {
            val chr = game.read("DBFilesClient\\ChrRaces.dbc") ?: throw IOException("The game has no ChrRaces.dbc")
            val male = maleDisplays(chr)
            val female = WrathppBody.femaleDisplays(chr)
            val own = { v: Variant -> (if (v.sex == 0) male else female)[v.race] }
            // the looks' patch's tables where it has them (the body options' rows too), else the game's
            fun table(name: String, kinds: String): WrathppUndead.Dbc {
                val mine = File(patch, "DBFilesClient/$name").takeIf { it.isFile }?.readBytes()
                val bytes = mine ?: game.read("DBFilesClient\\$name") ?: throw IOException("The game has no $name")
                return WrathppUndead.Dbc.read(bytes, kinds)
            }
            val displays = table("CreatureDisplayInfo.dbc", WrathppBody.DISPLAY_KINDS)
            val models = table("CreatureModelData.dbc", WrathppBody.MODEL_KINDS)
            addRows(displays, models, variants, own)
            File(patch, "DBFilesClient").mkdirs()
            writeWhole(File(patch, "DBFilesClient/CreatureDisplayInfo.dbc"), displays.write())
            writeWhole(File(patch, "DBFilesClient/CreatureModelData.dbc"), models.write())
            val serverDbc = File(server, "share/dbc")
            val serverTable = File(serverDbc, "CreatureDisplayInfo.dbc")
            val serverBase = serverTable.takeIf { it.isFile } ?: File(data, "dbc/CreatureDisplayInfo.dbc")
            if (serverBase.isFile) {
                val t = WrathppUndead.Dbc.read(serverBase.readBytes(), WrathppBody.DISPLAY_KINDS)
                addRows(t, null, variants, own)
                writeWhole(serverTable, t.write())
            }
        } finally {
            game.close()
        }
        stamps.forEach { it.parentFile?.mkdirs(); it.writeText("$stamp\n") }
        return "${variants.size} model variants"
    }

    private fun clear(patch: File, server: File): String? = null

    private fun writeWhole(target: File, bytes: ByteArray) {
        target.parentFile?.mkdirs()
        val tmp = File(target.path + ".tmp")
        tmp.writeBytes(bytes)
        if (!tmp.renameTo(target)) { target.delete(); if (!tmp.renameTo(target)) throw IOException("${target.path} couldn't be written") }
    }
}
