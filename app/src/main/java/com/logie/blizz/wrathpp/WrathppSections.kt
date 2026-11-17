package com.logie.blizz.wrathpp

import java.io.File
import java.io.IOException

/**
 * The game's character section table (`CharSections`) put in the order its component code needs (issue 294, a heap overrun found in the
 * client's source: `CCharacterComponent::Initialize` -> `BuildComponentArray`, Common/ComponentCore/ComponentUtils.cpp). Its first pass
 * sizes each race, sex and section's list of variations from the LAST run of rows of that group it meets (and leaks the earlier one); its
 * second pass then writes each run's colours at `m_variation[variationIndex]` with no bound, so a group split over two runs whose earlier
 * run has a higher variation than the last writes 8 bytes past a heap block: a small number and a pointer, which a later allocation trips
 * on. The table the game reads is the HD look's, then the looks' changes, Ralia's skins, the undead skins and the body options: rows of a
 * group can land apart. This puts the rows in one stable order by race, sex, section and variation (the order within a group as it was),
 * so every group is one run; the game reads its rows by their columns, never by place. [overruns] is the two passes run as the client
 * runs them, for the start report. Unit-tested; NOT run in the game.
 */
object WrathppSections {
    private const val RACE = 1
    private const val SEX = 2
    private const val SECTION = 3
    private const val VARIATION = 8
    private const val COLOUR = 9
    private const val SECTIONS = 5               // (the client's component keeps sections 0 to 4)

    /** How many writes the client's passes 1 and 2 would make past their arrays in [t], and how many groups are split over several runs. */
    fun overruns(t: DbcTable): Pair<Int, Int> {
        val rows = (0 until t.records.size).map { i -> intArrayOf(t.get(i, RACE), t.get(i, SEX), t.get(i, SECTION), t.get(i, VARIATION), t.get(i, COLOUR)) }
            .filter { it[2] in 0 until SECTIONS }
        if (rows.isEmpty()) return 0 to 0
        // pass 1: a group's number of variations is the last run's highest + 1
        val variations = HashMap<Triple<Int, Int, Int>, Int>()
        val runs = HashMap<Triple<Int, Int, Int>, Int>()
        var current: Triple<Int, Int, Int>? = null
        var highest = 0
        for (r in rows) {
            val g = Triple(r[0], r[1], r[2])
            if (g != current) {
                current?.let { variations[it] = highest + 1 }
                runs[g] = (runs[g] ?: 0) + 1
                current = g; highest = 0
            }
            highest = maxOf(highest, r[3])
        }
        current?.let { variations[it] = highest + 1 }
        // pass 2: each run of (group, variation) writes at its variation
        var over = 0
        var at: List<Int>? = null
        for (r in rows) {
            val k = listOf(r[0], r[1], r[2], r[3])
            if (k != at) {
                val n = variations[Triple(r[0], r[1], r[2])] ?: 0
                if (n > 0 && r[3] >= n) over++
                at = k
            }
        }
        return over to runs.values.count { it > 1 }
    }

    /** [t]'s rows in one stable order by race, sex, section and variation; whether anything moved. */
    fun order(t: DbcTable): Boolean {
        val before = t.records.toList()
        val sorted = before.indices.sortedWith(compareBy({ t.get(it, RACE) }, { t.get(it, SEX) }, { t.get(it, SECTION) }, { t.get(it, VARIATION) }))
        if (sorted == before.indices.toList()) return false
        val moved = sorted.map { before[it] }
        t.records.clear(); t.records.addAll(moved)
        return true
    }

    /** The looks' patch's table put in order (after every step that adds rows); the start report's line. */
    fun apply(client: File): String {
        val file = File(client, "Data/${WrathppLooks.PATCH}/DBFilesClient/CharSections.dbc")
        if (!file.isFile) return "no looks' table"
        val t = DbcTable(file.readBytes())
        val (over, split) = overruns(t)
        if (!order(t)) return "in order ($over overruns, $split split groups)"
        val tmp = File(file.path + ".tmp")
        tmp.writeBytes(t.write())
        if (!tmp.renameTo(file)) { file.delete(); if (!tmp.renameTo(file)) throw IOException("${file.path} couldn't be written") }
        val (after, splitAfter) = overruns(DbcTable(file.readBytes()))
        return "put in order: $over overruns and $split split groups before, $after and $splitAfter now"
    }
}
