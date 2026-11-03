package com.logie.blizz.ui

/**
 * The tile layout's arithmetic: which tiles share a row, in what order, and how tall a row is.
 * Plain Kotlin, unit-tested.
 */
object TileLayout {
    /** A wide tile's picture (a header like Steam's 460x215). */
    const val WIDE_RATIO = 2.14f
    /** A vertical tile's picture (the box art, 3:4). */
    const val TALL_RATIO = 3f / 4f
    const val MIN_COLUMNS = 1
    const val MAX_COLUMNS = 8

    data class Tile(val id: String, val wide: Boolean)

    /** Columns a wide tile covers: two where there are two to cover, else one. */
    fun units(wide: Boolean, columns: Int) = if (wide && columns >= 2) 2 else 1

    /** Tiles in rows of at most [columns] units: a tile that doesn't fit starts the next row. */
    fun rows(tiles: List<Tile>, columns: Int): List<List<Tile>> {
        val out = ArrayList<MutableList<Tile>>()
        var used = 0
        for (tile in tiles) {
            val u = units(tile.wide, columns)
            if (out.isEmpty() || used + u > columns) { out.add(mutableListOf()); used = 0 }
            out.last().add(tile)
            used += u
        }
        return out
    }

    /** Units a row uses (what's left over is blank). */
    fun used(row: List<Tile>, columns: Int) = row.sumOf { units(it.wide, columns) }

    /** The saved order first (ids that still exist), then every other id in its usual place. */
    fun ordered(all: List<String>, saved: List<String>): List<String> =
        saved.filter { it in all }.distinct().let { kept -> kept + all.filter { it !in kept } }

    /** [id] moved to where [target] is; the others close up. */
    fun move(order: List<String>, id: String, target: String): List<String> {
        if (id == target || id !in order || target !in order) return order
        val without = order.filter { it != id }
        val index = without.indexOf(target)
        // Dragged forward, it lands after the one it passes; backward, before it.
        val after = order.indexOf(id) < order.indexOf(target)
        return without.toMutableList().also { it.add(if (after) index + 1 else index, id) }
    }

    /** As many across as fit at 150 dp each, between 2 and [MAX_COLUMNS]. */
    fun autoColumns(widthDp: Float): Int = ((widthDp - 36f) / 150f).toInt().coerceIn(2, MAX_COLUMNS)

    /** A row's height (dp) for a column width [cell] and a [gap]: the box art's height if it has any, else the wide art's. */
    fun rowHeight(row: List<Tile>, columns: Int, cell: Float, gap: Float): Float {
        if (row.any { !it.wide }) return cell / TALL_RATIO
        val u = row.maxOf { units(it.wide, columns) }
        return (u * cell + (u - 1) * gap) / WIDE_RATIO
    }
}
