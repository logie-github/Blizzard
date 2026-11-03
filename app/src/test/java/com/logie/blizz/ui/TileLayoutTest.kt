package com.logie.blizz.ui

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import com.logie.blizz.ui.TileLayout.Tile

class TileLayoutTest {
    private fun t(id: String, wide: Boolean = false) = Tile(id, wide)

    @Test fun tilesFillRowsAndAWideOneTakesTwoColumns() {
        val rows = TileLayout.rows(listOf(t("a"), t("b"), t("c"), t("d", true), t("e"), t("f")), 3)
        assertEquals(listOf(listOf("a", "b", "c"), listOf("d", "e"), listOf("f")), rows.map { r -> r.map { it.id } })
    }

    @Test fun aWideTileThatDoesntFitStartsTheNextRow() {
        val rows = TileLayout.rows(listOf(t("a"), t("b"), t("w", true)), 3)
        assertEquals(listOf(listOf("a", "b"), listOf("w")), rows.map { r -> r.map { it.id } })
        assertEquals(1, TileLayout.used(rows[1], 3).let { if (it == 2) 1 else 0 })
    }

    @Test fun oneColumnShowsAWideTileAsOne() {
        assertEquals(1, TileLayout.units(true, 1))
        assertEquals(2, TileLayout.units(true, 2))
        assertEquals(1, TileLayout.rows(listOf(t("a", true)), 1).size)
    }

    @Test fun theSavedOrderComesFirstAndNewGamesFollow() {
        val all = listOf("a", "b", "c", "d")
        assertEquals(listOf("c", "a", "b", "d"), TileLayout.ordered(all, listOf("c", "gone", "a")))
        assertEquals(all, TileLayout.ordered(all, emptyList()))
    }

    @Test fun movingATileClosesUpTheRest() {
        val o = listOf("a", "b", "c", "d")
        assertEquals(listOf("b", "c", "a", "d"), TileLayout.move(o, "a", "c"))
        assertEquals(listOf("d", "a", "b", "c"), TileLayout.move(o, "d", "a"))
        assertEquals(o, TileLayout.move(o, "a", "a"))
        assertEquals(o, TileLayout.move(o, "x", "a"))
    }

    @Test fun rowHeightsFollowTheArt() {
        val tall = TileLayout.rowHeight(listOf(t("a")), 3, 100f, 10f)
        assertEquals(100f / TileLayout.TALL_RATIO, tall, 0.01f)
        val wideRow = TileLayout.rowHeight(listOf(t("w", true)), 3, 100f, 10f)
        assertEquals(210f / TileLayout.WIDE_RATIO, wideRow, 0.01f)
        assertTrue(wideRow < tall)
        // A row with a tall tile among them is as tall as the box art.
        assertEquals(tall, TileLayout.rowHeight(listOf(t("w", true), t("a")), 3, 100f, 10f), 0.01f)
    }

    @Test fun autoColumnsFitScreensFromTheCoverScreenToTheInnerOne() {
        assertEquals(2, TileLayout.autoColumns(360f))
        assertEquals(3, TileLayout.autoColumns(520f))
        assertEquals(8, TileLayout.autoColumns(4000f))
    }
}
