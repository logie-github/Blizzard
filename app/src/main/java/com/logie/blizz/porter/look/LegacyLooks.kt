package com.logie.blizz.porter.look

import com.logie.blizz.porter.wago.Tables

/**
 * A character's looks as the old character creator numbers them (Wrath's five: skin colour, face, hair style, hair colour,
 * facial hair, each an index the realm keeps in its `characters` table), from the choices of today's creator (Blizzard's
 * API's `customizations`: ChrCustomizationChoice ids).
 *
 * The game has its own table between the two: ChrCustomizationConversion, which Blizzard made when every character moved to
 * the new creator (9.0). A row says that the old creator's option ([SKIN] ... [FACIAL_HAIR]) at index `Data`, for a race and
 * sex, became a choice of the new one; a face may hang on the skin colour (`DependentOptionID` 1, `DependentData` the skin's
 * index), and one old facial hair became several new choices at once (a beard, a moustache, sideburns). Read backwards: for
 * each old option, the index whose choices are most of the character's own. A choice made since (a hair style of 9.0 or
 * later) was never an old index; that option is [Result.unmatched], and the realm's own first is used.
 */
object LegacyLooks {
    const val SKIN = 1
    const val FACE = 2
    const val HAIR_STYLE = 3
    const val HAIR_COLOR = 4
    const val FACIAL_HAIR = 5

    /** The words for each old option, as the report says them. */
    val NAMES = mapOf(SKIN to "skin colour", FACE to "face", HAIR_STYLE to "hair style", HAIR_COLOR to "hair colour", FACIAL_HAIR to "facial hair")

    /** The old creator's index of each option found ([SKIN] ... [FACIAL_HAIR]), and the options none of whose old indices are the character's. */
    data class Result(val values: Map<Int, Int>, val unmatched: List<Int>)

    private class Conversion(val option: Int, val data: Int, val choice: Int, val dependsOn: Int, val dependentData: Int)

    /**
     * [choices] (the character's ChrCustomizationChoice ids) as the old creator's indices for [race] (retail's ChrRaces id) and
     * [sex] (0 male, 1 female). One look-up of [tables] (the race's rows of ChrCustomizationConversion).
     */
    fun of(tables: Tables, race: Int, sex: Int, choices: Collection<Int>): Result {
        val rows = tables.rows("ChrCustomizationConversion", "ChrRacesID", race)
            .filter { it.int("Sex") == sex }
            .map { Conversion(it.int("OptionID"), it.int("Data"), it.int("ChrCustomizationChoiceID"), it.int("DependentOptionID"), it.int("DependentData")) }
        return of(rows, choices.toSet())
    }

    private fun of(rows: List<Conversion>, chosen: Set<Int>): Result {
        val values = LinkedHashMap<Int, Int>()
        val unmatched = ArrayList<Int>()
        // The skin first: a face may hang on it.
        for (option in listOf(SKIN, HAIR_STYLE, HAIR_COLOR, FACIAL_HAIR, FACE)) {
            val candidates = rows.filter { it.option == option }
            if (candidates.isEmpty()) continue // the race never had that option (a facial hair for some, ...)
            data class Score(val data: Int, val matched: Int, val whole: Boolean, val fits: Boolean)
            val scores = candidates.groupBy { it.data }.map { (data, group) ->
                // Where a face hangs on the skin, only its rows for the character's own skin are weighed (another skin's
                // row of the same face may share a choice with the character's and would tie).
                val fitting = group.filter { it.dependsOn == 0 || values[it.dependsOn] == null || values[it.dependsOn] == it.dependentData }
                val wanted = fitting.ifEmpty { group }.map { it.choice }.toSet()
                val matched = wanted.count { it in chosen }
                Score(data, matched, matched == wanted.size, fitting.isNotEmpty())
            }
            val best = scores.filter { it.matched > 0 }
                .sortedWith(compareByDescending<Score> { it.matched }.thenByDescending { it.fits }.thenByDescending { it.whole }.thenBy { it.data })
                .firstOrNull()
            if (best == null) unmatched.add(option) else values[option] = best.data
        }
        return Result(values, unmatched)
    }
}
