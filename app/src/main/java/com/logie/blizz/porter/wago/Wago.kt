package com.logie.blizz.porter.wago

import com.logie.blizz.porter.net.Net
import org.json.JSONObject
import java.io.File
import java.io.IOException
import java.util.concurrent.ConcurrentHashMap

/** One row of one of the game's tables, as wago.tools' CSV export gives it: its columns by name. */
class Row(private val values: Map<String, String>) {
    fun str(column: String): String = values[column].orEmpty()

    /** A whole number; a column of flags written unsigned (above 2^31) comes back with its bits, as the game reads it. */
    fun int(column: String): Int {
        val text = values[column]?.trim().orEmpty()
        if (text.isEmpty()) return 0
        return text.toLongOrNull()?.toInt() ?: text.toDoubleOrNull()?.toLong()?.toInt() ?: 0
    }

    fun float(column: String): Float = values[column]?.trim()?.toFloatOrNull() ?: 0f

    override fun toString(): String = values.toString()
}

/** The game's tables, as the porter asks them: the rows of a table whose column holds one of some values. */
interface Tables {
    fun rows(table: String, column: String, values: Collection<Int>): List<Row>

    fun rows(table: String, column: String, value: Int): List<Row> = rows(table, column, listOf(value))

    /** The row whose ID is [id], or null. */
    fun byId(table: String, id: Int): Row? = if (id == 0) null else rows(table, "ID", id).firstOrNull()
}

/** CSV as wago.tools writes it: a header line, then rows; a field in quotes may hold commas, quotes ("") and line breaks. */
object Csv {
    fun parse(text: String): List<Row> = table(text).second

    /** The header and the rows. */
    fun table(text: String): Pair<List<String>, List<Row>> {
        val records = records(text)
        if (records.isEmpty()) return emptyList<String>() to emptyList()
        val header = records.first()
        val rows = records.drop(1).filter { it.size > 1 || (it.size == 1 && it[0].isNotEmpty()) }.map { fields ->
            val map = HashMap<String, String>(header.size * 2)
            for (i in header.indices) map[header[i]] = fields.getOrElse(i) { "" }
            Row(map)
        }
        return header to rows
    }

    /** Rows written back as CSV under [header] (a field with a comma, a quote or a line break is quoted). */
    fun write(header: List<String>, rows: List<Row>): String = buildString {
        fun field(text: String) = if (text.any { it == ',' || it == '"' || it == '\n' || it == '\r' }) "\"" + text.replace("\"", "\"\"") + "\"" else text
        append(header.joinToString(",") { field(it) }).append('\n')
        for (row in rows) append(header.joinToString(",") { field(row.str(it)) }).append('\n')
    }

    private fun records(text: String): List<List<String>> {
        val out = ArrayList<List<String>>()
        var fields = ArrayList<String>()
        val field = StringBuilder()
        var quoted = false
        var i = 0
        val start = if (text.startsWith("﻿")) 1 else 0
        i = start
        while (i < text.length) {
            val c = text[i]
            if (quoted) {
                if (c == '"') {
                    if (i + 1 < text.length && text[i + 1] == '"') { field.append('"'); i++ } else quoted = false
                } else field.append(c)
            } else when (c) {
                '"' -> quoted = true
                ',' -> { fields.add(field.toString()); field.setLength(0) }
                '\r' -> {}
                '\n' -> { fields.add(field.toString()); field.setLength(0); out.add(fields); fields = ArrayList() }
                else -> field.append(c)
            }
            i++
        }
        if (field.isNotEmpty() || fields.isNotEmpty()) { fields.add(field.toString()); out.add(fields) }
        return out
    }
}

/**
 * The tables from whole CSV files in a folder (`<Table>.csv`, as `https://wago.tools/db2/<Table>/csv` gives them): the desktop's
 * and the tests' way. Each table is read once and indexed by the columns asked of it.
 */
class CsvTables(private val dir: File) : Tables {
    private val tables = ConcurrentHashMap<String, List<Row>>()
    private val indexes = ConcurrentHashMap<String, Map<Int, List<Row>>>()

    override fun rows(table: String, column: String, values: Collection<Int>): List<Row> {
        val index = indexes.getOrPut("$table/$column") {
            val all = tables.getOrPut(table) {
                val file = File(dir, "$table.csv")
                if (file.isFile) Csv.parse(file.readText()) else emptyList()
            }
            all.groupBy { it.int(column) }
        }
        return values.distinct().flatMap { index[it].orEmpty() }
    }
}

/**
 * The tables from wago.tools, a few rows at a time: `https://wago.tools/db2/<Table>/csv?filter[<Column>]=exact:<a>|<b>|...&build=<build>`
 * answers with exactly the rows asked for (all of them, no pages), so a character's look takes some twenty small requests
 * where whole tables would be some 60 MB. Every answer is kept on the phone under [cache] (per build: the game's tables
 * change between builds), one file per table, column and value, so a second look at a character asks nothing.
 */
class WagoTables(private val net: Net, val build: String, private val cache: File) : Tables {
    private val memory = ConcurrentHashMap<String, List<Row>>()

    override fun rows(table: String, column: String, values: Collection<Int>): List<Row> {
        require(NAME.matches(table) && NAME.matches(column)) { "not a table or column name: $table.$column" }
        val wanted = values.distinct()
        val missing = wanted.filter { known(table, column, it) == null }
        for (batch in missing.chunked(BATCH)) fetch(table, column, batch)
        return wanted.flatMap { known(table, column, it).orEmpty() }
    }

    private fun key(table: String, column: String, value: Int) = "$table/$column=$value"

    private fun file(table: String, column: String, value: Int) = File(cache, "$build/$table/$column=$value.csv")

    private fun known(table: String, column: String, value: Int): List<Row>? {
        val key = key(table, column, value)
        memory[key]?.let { return it }
        val file = file(table, column, value)
        if (!file.isFile) return null
        return Csv.parse(file.readText()).also { memory[key] = it }
    }

    private fun fetch(table: String, column: String, values: List<Int>) {
        val url = "$SITE/db2/$table/csv?filter%5B$column%5D=exact%3A${values.joinToString("%7C")}&build=${build}"
        var last: IOException? = null
        for (attempt in 0 until 4) {
            try {
                val reply = net.get(url)
                if (!reply.ok) throw IOException("wago.tools answered ${reply.code} for $table")
                val (header, rows) = Csv.table(reply.text)
                if (column !in header) throw IOException("wago.tools sent no table for $table")
                // What came back, kept per value (with the header, so a value with no rows is known to have none).
                val byValue = rows.groupBy { it.int(column) }
                for (value in values) {
                    val mine = byValue[value].orEmpty()
                    memory[key(table, column, value)] = mine
                    val target = file(table, column, value)
                    runCatching {
                        target.parentFile?.mkdirs()
                        val part = File(target.path + ".part")
                        part.writeText(Csv.write(header, mine))
                        part.renameTo(target)
                    }
                }
                return
            } catch (e: IOException) {
                last = e
                Thread.sleep(500L shl attempt)
            }
        }
        throw last ?: IOException("wago.tools didn't answer for $table")
    }

    companion object {
        const val SITE = "https://wago.tools"
        private const val BATCH = 60
        private val NAME = Regex("[A-Za-z0-9_]{1,64}")

        /** The game's live build as wago.tools names it (`12.1.5.70783`): the newest of its "wow" product. */
        fun liveBuild(net: Net): String {
            val reply = net.get("$SITE/api/builds")
            if (!reply.ok) throw IOException("wago.tools answered ${reply.code} for its builds")
            return parseBuilds(reply.text) ?: throw IOException("wago.tools named no build of the game")
        }

        fun parseBuilds(json: String): String? {
            val list = JSONObject(json).optJSONArray("wow") ?: return null
            for (i in 0 until list.length()) {
                val version = list.optJSONObject(i)?.optString("version").orEmpty()
                if (Regex("""\d+\.\d+\.\d+\.\d+""").matches(version)) return version
            }
            return null
        }
    }
}
