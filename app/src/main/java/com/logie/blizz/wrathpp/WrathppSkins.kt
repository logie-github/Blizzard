package com.logie.blizz.wrathpp

import java.io.File

/**
 * Which skin colours Wrath++'s creator offers (the user, 19 November 2026: "No skins should be used except for the dark ranger skin for
 * elves and then the mannequin skins for humans. And the other ones we've added like ralias. Ralias becomes the new base."). With Ralia's
 * mod imported ([WrathppRalia]) the Skin Color row lists the skins the set supplies a texture for itself ([WrathppRalia.supplied]: matched
 * by file name, the mannequin ones among them), the Blood Elves' Dark Ranger skin (the looks mark it `keep`) and the undead skins (their
 * own switch); not Shadowlands' stock colours, nor the ones the set is only carried over to. Without the import nothing is filtered.
 *
 * The app writes `Interface\GlueXML\WrathppSkins.lua` into the glue patch, `WrathppSkins = { ["1_0"] = { 0, 1, 2 } }`: per model
 * (race_sex) the skins' places, which are the looks' colour numbers; a model it doesn't list is not filtered. The creator
 * (`WrathppCreate.lua`, skinFilter) reads it. Characters that exist keep their skin: nothing in the world path reads this.
 */
object WrathppSkins {
    const val FILE_NAME = "WrathppSkins.lua"

    /** The patch's file for [offered] (model key to its name and the skins' places); an empty table when nothing is filtered. */
    fun script(offered: Map<String, Pair<String, List<Int>>>?): ByteArray {
        val out = StringBuilder("WrathppSkins = {")
        if (!offered.isNullOrEmpty()) {
            out.append('\n')
            for ((key, entry) in offered) out.append("\t[\"$key\"] = { ${entry.second.joinToString(", ")} },\n")
        }
        out.append("}\n")
        return out.toString().toByteArray(Charsets.UTF_8)
    }

    /** "Human M 13 of 19, ..." (the models filtered; [totals]: how many regular skins a model's table has), or null when nothing is. */
    fun line(offered: Map<String, Pair<String, List<Int>>>?, totals: Map<String, Int>): String? {
        if (offered.isNullOrEmpty()) return null
        return offered.entries.joinToString(", ") { (key, entry) ->
            val n = entry.first
            val name = if (n.endsWith("Female")) n.removeSuffix("Female") + " F" else if (n.endsWith("Male")) n.removeSuffix("Male") + " M" else n
            "$name ${entry.second.size} of ${totals[key] ?: "?"}"
        }
    }

    /** How many regular skins (colours, not the undead's) each model has in the looks' character table, by model key. */
    fun totals(client: File): Map<String, Int> {
        val table = File(client, "Data/${WrathppLooks.PATCH}/DBFilesClient/CharSections.dbc")
        if (!table.isFile) return emptyMap()
        val dbc = WrathppUndead.Dbc.read(table.readBytes(), WrathppUndead.KINDS)
        return dbc.rows.filter { it[3] == 0 && it[8] == 0 && (it[4] as String).isNotEmpty() && !(it[4] as String).contains("Undead", ignoreCase = true) }
            .groupBy { "${it[1]}_${it[2]}" }.mapValues { (_, rows) -> rows.map { it[9] as Int }.distinct().size }
    }

    /** The glue file and the start report's line, from what the import supplies ([WrathppRalia.supplied]). */
    fun build(store: File, client: File): Pair<ByteArray, String?> {
        val offered = runCatching { WrathppRalia.supplied(store, client) }.getOrNull()
        return script(offered) to line(offered, if (offered.isNullOrEmpty()) emptyMap() else runCatching { totals(client) }.getOrDefault(emptyMap()))
    }
}
