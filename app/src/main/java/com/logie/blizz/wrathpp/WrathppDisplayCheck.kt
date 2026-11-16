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
