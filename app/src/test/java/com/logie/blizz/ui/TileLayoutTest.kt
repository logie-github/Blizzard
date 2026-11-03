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

    @Test fun wideArtSpreadsAcrossTheWholeRow() {
        // Alone in a row of three: all three columns.
        assertEquals(listOf(3), TileLayout.spans(listOf(t("w", true)), 3))
        // Beside a tall tile: the tall one keeps its column, the wide one takes the rest.
        assertEquals(listOf(1, 3), TileLayout.spans(listOf(t("a"), t("w", true)), 4))
        // Two wide ones share what's left.
        assertEquals(listOf(2, 2), TileLayout.spans(listOf(t("w", true), t("x", true)), 4))
        assertEquals(listOf(3, 2), TileLayout.spans(listOf(t("w", true), t("x", true)), 5))
        // Without wide art the row isn't stretched.
        assertEquals(listOf(1, 1), TileLayout.spans(listOf(t("a"), t("b")), 4))
        // One column: a wide tile is one column, which is the full width.
        assertEquals(listOf(1), TileLayout.spans(listOf(t("w", true)), 1))
    }

    @Test fun aWideRowIsAsTallAsItsArtNeedsAndTheTallTilesBesideItFollow() {
        val tall = TileLayout.rowHeight(listOf(t("a")), 3, 100f, 10f)
        assertEquals(100f / TileLayout.TALL_RATIO, tall, 0.01f)
        // Wide alone across three columns (320 wide): its art whole.
        val full = TileLayout.rowHeight(listOf(t("w", true)), 3, 100f, 10f)
        assertEquals(320f / TileLayout.WIDE_RATIO, full, 0.01f)
        // Beside a tall tile in three columns: the wide one is 210 wide, and the row is as tall as that art.
        val mixed = TileLayout.rowHeight(listOf(t("a"), t("w", true)), 3, 100f, 10f)
        assertEquals(210f / TileLayout.WIDE_RATIO, mixed, 0.01f)
    }

    @Test fun placesFillTheWidthAndAddUpToTheGridsHeight() {
        val (placed, height) = TileLayout.place(listOf(t("a"), t("b"), t("w", true), t("c")), 2, 100f, 10f)
        // Row 1: a, b (tall). Row 2: the wide one across both columns. Row 3: c.
        val byId = placed.associateBy { it.id }
        assertEquals(0f, byId.getValue("a").x, 0.01f)
        assertEquals(110f, byId.getValue("b").x, 0.01f)
        assertEquals(210f, byId.getValue("w").width, 0.01f)
        assertEquals(0f, byId.getValue("w").x, 0.01f)
        val row1 = 100f / TileLayout.TALL_RATIO
        val row2 = 210f / TileLayout.WIDE_RATIO
        assertEquals(row1 + 10f, byId.getValue("w").y, 0.01f)
        assertEquals(row1 + row2 + 20f, byId.getValue("c").y, 0.01f)
        assertEquals(row1 + row2 + 20f + row1, height, 0.01f)
        // The right edge of a full row is the grid's width (2 * 100 + 10).
        assertEquals(210f, byId.getValue("b").x + byId.getValue("b").width, 0.01f)
    }

    @Test fun autoColumnsFitScreensFromTheCoverScreenToTheInnerOne() {
        assertEquals(2, TileLayout.autoColumns(360f))
        assertEquals(3, TileLayout.autoColumns(520f))
        assertEquals(8, TileLayout.autoColumns(4000f))
    }
}
