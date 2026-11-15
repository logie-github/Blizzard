package com.logie.blizz.porter.port

import java.io.File
import java.io.IOException
import java.io.RandomAccessFile
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.channels.FileChannel

/**
 * One of the game's client data files as the world server reads it from `data/dbc` (the classic WDBC layout): a
 * 20-byte header (the letters WDBC, then the number of records, of fields, the size of a record and the size of the
 * string block), the records one after another, and the strings they point into. Every field the porter reads is four
 * bytes: a number, a fraction, or the place of a text in the string block.
 *
 * The file is mapped, not read into memory: Spell.dbc is 47 MB.
 */
class DbcFile private constructor(private val data: ByteBuffer, val name: String) {
    val recordCount: Int
    val fieldCount: Int
    val recordSize: Int
    val stringSize: Int
    private val stringStart: Int

    init {
        if (data.limit() < HEADER || data.getInt(0) != MAGIC) throw IOException("$name isn't a DBC file")
        recordCount = data.getInt(4)
        fieldCount = data.getInt(8)
        recordSize = data.getInt(12)
        stringSize = data.getInt(16)
        if (recordCount < 0 || fieldCount <= 0 || recordSize <= 0 || stringSize < 0) throw IOException("$name has a damaged header")
        stringStart = HEADER + recordCount.toLong().times(recordSize).also {
            if (it + stringSize > data.limit() - HEADER) throw IOException("$name is cut short")
        }.toInt()
    }

    /** Field [field] of record [record] as a whole number. Only for files whose fields are all four bytes. */
    fun int(record: Int, field: Int): Int = data.getInt(offset(record, field))

    fun float(record: Int, field: Int): Float = data.getFloat(offset(record, field))

    /** The text a field points at (UTF-8, up to its NUL); empty when the place is outside the string block. */
    fun string(record: Int, field: Int): String {
        val at = int(record, field)
        if (at <= 0 || at >= stringSize) return ""
        var end = stringStart + at
        val limit = stringStart + stringSize
        while (end < limit && data.get(end) != 0.toByte()) end++
        val bytes = ByteArray(end - (stringStart + at))
        for (i in bytes.indices) bytes[i] = data.get(stringStart + at + i)
        return String(bytes, Charsets.UTF_8)
    }

    private fun offset(record: Int, field: Int): Int {
        if (record < 0 || record >= recordCount) throw IndexOutOfBoundsException("$name has no record $record")
        if (field < 0 || field >= fieldCount || recordSize != fieldCount * 4) throw IndexOutOfBoundsException("$name has no four-byte field $field")
        return HEADER + record * recordSize + field * 4
    }

    companion object {
        private const val HEADER = 20
        private const val MAGIC = 0x43424457 // "WDBC", little-endian

        fun parse(bytes: ByteArray, name: String = "DBC"): DbcFile =
            DbcFile(ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN), name)

        fun open(file: File): DbcFile {
            RandomAccessFile(file, "r").use { raf ->
                val map = raf.channel.map(FileChannel.MapMode.READ_ONLY, 0, raf.length())
                return DbcFile(map.order(ByteOrder.LITTLE_ENDIAN), file.name)
            }
        }

        /** [name] in [folder] whatever the case of its letters (the data's file names differ between extractors). */
        fun find(folder: File, name: String): File? =
            File(folder, name).takeIf { it.isFile } ?: folder.listFiles()?.firstOrNull { it.isFile && it.name.equals(name, ignoreCase = true) }
    }
}

/** A row of a client data table: from the file, or from the realm's world database (the modules' own rows). */
interface DbcRow {
    val id: Int
    fun int(field: Int): Int
    fun float(field: Int): Float
    fun string(field: Int): String
}

/**
 * A client data table as the world server ends up with it: the file's rows, and over them the rows of the world
 * database's table of the same name (`spell_dbc`, `chrraces_dbc`, ...), which is where this realm's modules put their
 * races, spells and looks. As in the core (DBCDatabaseLoader), a database row takes the place of the file's row with
 * the same id, its columns are the file's fields in order, and an empty text column leaves the file's text.
 */
class DbcTable(val name: String, private val file: DbcFile?, private val idField: Int, overlay: List<Map<Int, String?>>) {
    private val fileIndex = HashMap<Int, Int>()
    private val overlayRows = HashMap<Int, Map<Int, String?>>()

    init {
        if (file != null) for (record in 0 until file.recordCount) fileIndex[file.int(record, idField)] = record
        for (row in overlay) {
            val id = row[idField]?.toLongOrNull()?.toInt() ?: continue
            overlayRows[id] = row
        }
    }

    val ids: Set<Int> by lazy { fileIndex.keys + overlayRows.keys }
    val size: Int get() = ids.size

    /** Whether the row comes from the game's own file (not only from a module's database row). */
    fun inFile(id: Int): Boolean = fileIndex.containsKey(id)

    operator fun get(id: Int): DbcRow? {
        val record = fileIndex[id]
        val over = overlayRows[id]
        if (record == null && over == null) return null
        return Row(id, record, over)
    }

    fun rows(): Sequence<DbcRow> = ids.asSequence().mapNotNull { get(it) }

    private inner class Row(override val id: Int, private val record: Int?, private val over: Map<Int, String?>?) : DbcRow {
        override fun int(field: Int): Int {
            if (over != null) return cell(field)?.let { it.toLongOrNull()?.toInt() ?: it.toDoubleOrNull()?.toInt() } ?: 0
            return file!!.int(record!!, field)
        }

        override fun float(field: Int): Float {
            if (over != null) return cell(field)?.toFloatOrNull() ?: 0f
            return file!!.float(record!!, field)
        }

        override fun string(field: Int): String {
            if (over != null) {
                val text = cell(field).orEmpty()
                return if (text.isEmpty() && record != null) file!!.string(record, field) else text
            }
            return file!!.string(record!!, field)
        }

        private fun cell(field: Int): String? {
            if (!over!!.containsKey(field)) throw IllegalStateException("$name: field $field wasn't read from the database")
            return over[field]
        }
    }
}
