package com.logie.blizz.porter.port

import com.logie.blizz.wow.WowCtl
import java.io.File
import java.io.IOException
import java.util.concurrent.TimeUnit

/**
 * The realm's database as the porter uses it: SQL in, rows of text out. On the phone that is the realm's own
 * `ctl.sh sql <database>` (the MariaDB client in batch mode, see [ProcessRealmDb]); tests give canned rows.
 *
 * [query] only ever reads. [execute] runs a script that changes the realm: the porter calls it once per port, with one
 * transaction inside, so a script that fails part way leaves nothing behind (the client stops at the first error and
 * the server rolls the open transaction back when the connection closes).
 */
interface RealmDb {
    /** Runs one SELECT on [database]: its rows, each a list of column texts (null for SQL NULL). */
    fun query(database: String, sql: String): List<List<String?>>

    /** Runs a script of statements on [database]; the rows its SELECTs printed. Throws [RealmDbException] if any statement fails. */
    fun execute(database: String, sql: String): List<List<String?>>

    /**
     * Several SELECTs, each one's rows in the same place of the result. A handle that pays for every call (a program
     * started each time, as on the phone) answers them in one ([ProcessRealmDb]); the rows of one statement may come
     * back in any order.
     */
    fun queryAll(database: String, statements: List<String>): List<List<List<String?>>> = statements.map { query(database, it) }
}

/** The database refused a statement, or could not be reached; [message] is what the client said. */
class RealmDbException(message: String) : IOException(message)

/**
 * Text and numbers on their way into SQL. The porter builds every statement from values it has checked: numbers go in
 * as numbers (they are Int or Long before they are text), names pass [PortNames] first, and what remains is quoted here.
 */
object Sql {
    private val NAME = Regex("[A-Za-z0-9_]{1,64}")

    /** A database, table or column name in backticks; refuses anything but letters, digits and underscores. */
    fun name(identifier: String): String {
        require(NAME.matches(identifier)) { "Not a database name: $identifier" }
        return "`$identifier`"
    }

    /** A text value in single quotes, with the characters MariaDB reads specially escaped. */
    fun text(value: String): String {
        val out = StringBuilder(value.length + 2).append('\'')
        for (c in value) {
            when (c) {
                '\'' -> out.append("''")
                '\\' -> out.append("\\\\")
                '\u0000' -> out.append("\\0")
                '\n' -> out.append("\\n")
                '\r' -> out.append("\\r")
                '\u001a' -> out.append("\\Z")
                else -> out.append(c)
            }
        }
        return out.append('\'').toString()
    }

    /** A list of numbers for `IN (...)`; `NULL` when empty, which matches nothing. */
    fun list(numbers: Collection<Int>): String = if (numbers.isEmpty()) "NULL" else numbers.joinToString(",")
}

/**
 * What the MariaDB client prints in batch mode (`--batch --skip-column-names`): a row a line, columns separated by
 * tabs, with tab, newline, NUL and backslash inside a value written as `\t`, `\n`, `\0` and `\\`, and NULL as the
 * word NULL.
 */
object BatchRows {
    fun parse(output: String): List<List<String?>> {
        if (output.isEmpty()) return emptyList()
        val rows = ArrayList<List<String?>>()
        for (line in output.split('\n')) {
            if (line.isEmpty()) continue
            rows.add(line.removeSuffix("\r").split('\t').map(::unescape))
        }
        return rows
    }

    private fun unescape(cell: String): String? {
        if (cell == "NULL") return null
        if (cell.indexOf('\\') < 0) return cell
        val out = StringBuilder(cell.length)
        var i = 0
        while (i < cell.length) {
            val c = cell[i]
            if (c == '\\' && i + 1 < cell.length) {
                when (cell[i + 1]) {
                    'n' -> out.append('\n')
                    't' -> out.append('\t')
                    '0' -> out.append('\u0000')
                    '\\' -> out.append('\\')
                    else -> out.append(c).append(cell[i + 1])
                }
                i += 2
            } else {
                out.append(c)
                i++
            }
        }
        return out.toString()
    }
}

/**
 * [RealmDb] by a program that takes SQL on its input and prints batch rows: `command + database` is run for every
 * call, as the app runs `sh ctl.blizz.sh sql <database>` with the realm's environment (WowCtl.command), or as the
 * porter's rig runs the MariaDB client directly. Plain Java processes, no Android types.
 */
class ProcessRealmDb(
    private val command: List<String>,
    private val environment: Map<String, String> = emptyMap(),
    private val directory: File? = null,
    private val timeoutSeconds: Long = 300,
) : RealmDb {
    override fun query(database: String, sql: String): List<List<String?>> = run(database, sql)

    override fun execute(database: String, sql: String): List<List<String?>> = run(database, sql)

    /**
     * All of them in one run of the client: each SELECT is wrapped so that its rows begin with its place in the list,
     * which is how the rows are told apart in the client's single stream of output.
     */
    override fun queryAll(database: String, statements: List<String>): List<List<List<String?>>> {
        if (statements.isEmpty()) return emptyList()
        if (statements.size == 1) return listOf(query(database, statements[0]))
        val script = StringBuilder()
        statements.forEachIndexed { index, statement ->
            script.append("SELECT ").append(index).append(" AS porter_n, porter_t.* FROM (").append(statement.trim().trimEnd(';')).append(") porter_t;\n")
        }
        val results = List(statements.size) { ArrayList<List<String?>>() }
        for (row in run(database, script.toString())) {
            val index = row.firstOrNull()?.toIntOrNull() ?: continue
            if (index in results.indices) results[index].add(row.drop(1))
        }
        return results
    }

    companion object {
        /**
         * The realm's own `ctl.sh sql`, as the app runs it: [sql] is `WowCtl.command(layout, loader, timeZone, "sql")`
         * (the shell, `ctl.blizz.sh`, its environment and folder); each call adds the database's name.
         */
        fun of(sql: WowCtl.Command): ProcessRealmDb = ProcessRealmDb(sql.argv, sql.env, sql.directory)
    }

    private fun run(database: String, sql: String): List<List<String?>> {
        Sql.name(database)
        val builder = ProcessBuilder(command + database)
        builder.environment().putAll(environment)
        directory?.let { builder.directory(it) }
        val process = try {
            builder.start()
        } catch (e: IOException) {
            throw RealmDbException("The database client couldn't be started: ${e.message}")
        }
        // The client's two outputs are read while it runs: a large result would otherwise fill its pipe and stop it.
        var out = ""
        var err = ""
        val readOut = Thread { out = process.inputStream.bufferedReader(Charsets.UTF_8).readText() }.apply { start() }
        val readErr = Thread { err = process.errorStream.bufferedReader(Charsets.UTF_8).readText() }.apply { start() }
        try {
            process.outputStream.use { it.write(sql.toByteArray(Charsets.UTF_8)) }
        } catch (e: IOException) {
            // (the client ended before it read everything: its exit code and message say why)
        }
        if (!process.waitFor(timeoutSeconds, TimeUnit.SECONDS)) {
            process.destroyForcibly()
            throw RealmDbException("The database didn't answer in $timeoutSeconds seconds")
        }
        readOut.join()
        readErr.join()
        if (process.exitValue() != 0) {
            throw RealmDbException(err.trim().ifEmpty { "The database client ended with code ${process.exitValue()}" })
        }
        return BatchRows.parse(out)
    }
}
