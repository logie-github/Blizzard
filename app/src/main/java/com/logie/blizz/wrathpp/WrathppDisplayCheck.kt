package com.logie.blizz.wrathpp

import java.io.File

/**
 * The game's creation screen reads each race's display row and that row's model row without looking whether they are there (the
 * client's `GetModelDataRec`: a missing `CreatureDisplayInfo` row is a crash at Create Character, report #272, found with the allied
 * races' displays 33001 to 33022 after the body options' tables had replaced the looks' own). After everything has been put into the
 * looks' patch folder, this reads its `ChrRaces`, `CreatureDisplayInfo` and `CreatureModelData` and names each race display whose row
 * or model row is not in the tables the game will read there. Only what the patch folder holds is checked (its tables win over the
 * game's own, but a table it doesn't carry is the game's, not read here). Reads only; unit-tested, not run in the game.
 */
object WrathppDisplayCheck {
    private const val RACE_MALE = 4
    private const val RACE_FEMALE = 5
    private const val DISPLAY_MODEL = 1

    /** The problems for [races] (id, male display, female display), the display ids and each one's model id, and the model ids that exist. */
    fun problems(races: List<Triple<Int, Int, Int>>, displays: Map<Int, Int>, models: Set<Int>): List<String> {
        val out = ArrayList<String>()
        for ((race, male, female) in races) {
            for ((sex, display) in listOf("male" to male, "female" to female)) {
                if (display == 0) continue
                val model = displays[display]
                if (model == null) out.add("race $race $sex: display $display is not in CreatureDisplayInfo")
                else if (model != 0 && model !in models) out.add("race $race $sex: display $display names model $model, which is not in CreatureModelData")
            }
        }
        return out
    }


    /**
     * A phone that made the body options' tables the old way (from the game's own, over the looks') has no allied races' rows in its patch
     * folder's `CreatureDisplayInfo` and `CreatureModelData`, and the rows' own source (the looks' package, 1 GB) is not kept. The server's
     * copy of the tables the looks carry ([WrathppLooks.SERVER_COPY], in the same patch folder) has them; each row of it whose id the game's
     * table lacks is added to it (the same columns, the texts written again). Returns how many rows were added (0: none missing or no copy).
     */
    fun repair(client: File): Int {
        val patch = File(client, "Data/${WrathppLooks.PATCH}")
        val dir = File(patch, "DBFilesClient")
        var added = 0
        for ((name, kinds) in listOf("CreatureModelData.dbc" to WrathppBody.MODEL_KINDS, "CreatureDisplayInfo.dbc" to WrathppBody.DISPLAY_KINDS)) {
            val mine = File(dir, name).takeIf { it.isFile } ?: continue
            val copy = File(patch, "${WrathppLooks.SERVER_COPY}/$name").takeIf { it.isFile } ?: continue
            val table = WrathppUndead.Dbc.read(mine.readBytes(), kinds)
            val have = table.rows.map { it[0] as Int }.toHashSet()
            val extra = WrathppUndead.Dbc.read(copy.readBytes(), kinds).rows.filter { (it[0] as Int) !in have }
            if (extra.isEmpty()) continue
            table.rows.addAll(extra)
            val tmp = File(mine.path + ".tmp")
            tmp.writeBytes(table.write())
            if (!tmp.renameTo(mine)) { mine.delete(); if (!tmp.renameTo(mine)) throw java.io.IOException("${mine.path} couldn't be written") }
            added += extra.size
        }
        return added
    }

    /** The start report's line: what is wrong in [client]'s looks' tables, or that nothing is. */
    fun check(client: File): String {
        val dir = File(client, "Data/${WrathppLooks.PATCH}/DBFilesClient")
        val chr = File(dir, "ChrRaces.dbc")
        val cdi = File(dir, "CreatureDisplayInfo.dbc")
        val cmd = File(dir, "CreatureModelData.dbc")
        if (!chr.isFile || !cdi.isFile || !cmd.isFile) return "not checked (the looks' patch folder lacks one of the three tables)"
        val races = readRaces(chr.readBytes())
        val displays = readDisplays(cdi.readBytes())
        val models = readModels(cmd.readBytes())
        val bad = problems(races, displays, models)
        return if (bad.isEmpty()) "${races.size} races' displays are all there" else "${bad.size} MISSING: " + bad.take(8).joinToString("; ")
    }

    private fun words(data: ByteArray): Pair<Int, Int> {
        val b = java.nio.ByteBuffer.wrap(data).order(java.nio.ByteOrder.LITTLE_ENDIAN)
        return b.getInt(4) to b.getInt(12)
    }

    private fun int(data: ByteArray, record: Int, size: Int, field: Int): Int =
        java.nio.ByteBuffer.wrap(data).order(java.nio.ByteOrder.LITTLE_ENDIAN).getInt(20 + record * size + field * 4)

    fun readRaces(data: ByteArray): List<Triple<Int, Int, Int>> {
        val (count, size) = words(data)
        return (0 until count).map { Triple(int(data, it, size, 0), int(data, it, size, RACE_MALE), int(data, it, size, RACE_FEMALE)) }
    }

    fun readDisplays(data: ByteArray): Map<Int, Int> {
        val (count, size) = words(data)
        return (0 until count).associate { int(data, it, size, 0) to int(data, it, size, DISPLAY_MODEL) }
    }

    fun readModels(data: ByteArray): Set<Int> {
        val (count, size) = words(data)
        return (0 until count).map { int(data, it, size, 0) }.toSet()
    }
}
