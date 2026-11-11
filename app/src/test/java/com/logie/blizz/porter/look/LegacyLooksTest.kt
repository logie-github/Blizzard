package com.logie.blizz.porter.look

import com.logie.blizz.porter.net.HttpNet
import com.logie.blizz.porter.wago.Row
import com.logie.blizz.porter.wago.Tables
import com.logie.blizz.porter.wago.WagoTables
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import kotlin.random.Random

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class LegacyLooksTest {
    @get:Rule val temp = TemporaryFolder()

    private class ListTables(private val rows: List<Map<String, Int>>) : Tables {
        var asked = 0
        override fun rows(table: String, column: String, values: Collection<Int>): List<Row> {
            asked++
            assertEquals("ChrCustomizationConversion", table)
            return rows.filter { it[column] in values }.map { r -> Row(r.mapValues { it.value.toString() }) }
        }
    }

    private fun conv(option: Int, data: Int, choice: Int, dependsOn: Int = 0, dependentData: Int = 0, race: Int = 2, sex: Int = 0) =
        mapOf("ChrRacesID" to race, "Sex" to sex, "OptionID" to option, "Data" to data, "ChrCustomizationChoiceID" to choice,
            "DependentOptionID" to dependsOn, "DependentData" to dependentData)

    /** Made-up rows in the table's shape: three skins, faces on the skin, two hair styles and colours, facial hair of two choices each. */
    private val rows = listOf(
        conv(1, 0, 100), conv(1, 1, 101), conv(1, 2, 102),
        // Face 0 on skin 1 became two choices, one of them also face 1's on that skin: face 1 is the whole match for 211.
        conv(2, 0, 200, 1, 0), conv(2, 0, 201, 1, 1), conv(2, 0, 211, 1, 1),
        conv(2, 1, 210, 1, 0), conv(2, 1, 211, 1, 1),
        // Face 2 has a row only on skin 0, whose choice is skin 1's face 0 too (another skin's row must not count).
        conv(2, 2, 201, 1, 0),
        conv(3, 0, 300), conv(3, 1, 301),
        conv(4, 0, 400), conv(4, 1, 401),
        conv(5, 0, 500), conv(5, 0, 510), conv(5, 1, 501), conv(5, 1, 510), conv(5, 2, 501), conv(5, 2, 511),
        // Another sex and race, never to be taken.
        conv(3, 7, 301, sex = 1), conv(3, 8, 301, race = 4),
    )

    @Test fun theOldIndicesAreReadBackFromTheChoices() {
        val tables = ListTables(rows)
        val result = LegacyLooks.of(tables, 2, 0, listOf(101, 211, 301, 400, 501, 511))
        assertEquals(mapOf(LegacyLooks.SKIN to 1, LegacyLooks.FACE to 1, LegacyLooks.HAIR_STYLE to 1, LegacyLooks.HAIR_COLOR to 0, LegacyLooks.FACIAL_HAIR to 2), result.values)
        assertEquals(emptyList<Int>(), result.unmatched)
        assertEquals("one look-up for the race", 1, tables.asked)
    }

    @Test fun aChoiceMadeSinceHasNoOldIndex() {
        // 999: a hair style of today's creator; 201 is face 0's on skin 1 (and face 2's on skin 0 only).
        val result = LegacyLooks.of(ListTables(rows), 2, 0, listOf(101, 201, 999, 401, 500, 510))
        assertEquals(1, result.values[LegacyLooks.SKIN])
        assertEquals(0, result.values[LegacyLooks.FACE])
        assertEquals(1, result.values[LegacyLooks.HAIR_COLOR])
        assertEquals(0, result.values[LegacyLooks.FACIAL_HAIR])
        assertEquals(listOf(LegacyLooks.HAIR_STYLE), result.unmatched)
    }

    /**
     * The game's own table (BLIZZ_PORTER_LIVE=1): looks of the old creator, for every race that had it, made into today's
     * choices by the table and read back. Two old indices that became the very same choices can't be told apart; any
     * other difference fails.
     */
    @Test fun theGamesOwnTableReadsBack() {
        assumeTrue(System.getenv("BLIZZ_PORTER_LIVE") == "1")
        val net = HttpNet("BlizzardLauncher-test")
        val tables = WagoTables(net, WagoTables.liveBuild(net), temp.newFolder("tables"))
        val random = Random(7)
        var tried = 0
        for (race in listOf(1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 22, 27, 29)) {
            val all = tables.rows("ChrCustomizationConversion", "ChrRacesID", race)
            for (sex in 0..1) {
                val mine = all.filter { it.int("Sex") == sex }
                val byOption = mine.groupBy { it.int("OptionID") }.mapValues { (_, r) -> r.groupBy { it.int("Data") } }
                repeat(25) {
                    val pick = HashMap<Int, Int>()
                    for (option in listOf(1, 3, 4, 5)) byOption[option]?.keys?.sorted()?.let { pick[option] = it[random.nextInt(it.size)] }
                    fun fits(r: Row) = r.int("DependentOptionID") == 0 || r.int("DependentData") == pick[r.int("DependentOptionID")]
                    byOption[2]?.filter { (_, r) -> r.any(::fits) }?.keys?.sorted()?.takeIf { it.isNotEmpty() }?.let { pick[2] = it[random.nextInt(it.size)] }
                    fun choices(option: Int, data: Int?) = byOption[option]?.get(data).orEmpty().filter { option != 2 || fits(it) }.map { it.int("ChrCustomizationChoiceID") }.toSet()
                    val chosen = pick.flatMap { (o, d) -> choices(o, d) }
                    val got = LegacyLooks.of(tables, race, sex, chosen).values
                    for ((option, data) in pick) {
                        if (got[option] != data) assertEquals("race $race sex $sex option $option: $data became ${got[option]}", choices(option, data), choices(option, got[option]))
                    }
                    tried++
                }
            }
        }
        assertTrue(tried > 500)
    }
}
