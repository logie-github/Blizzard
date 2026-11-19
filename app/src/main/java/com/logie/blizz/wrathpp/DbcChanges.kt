package com.logie.blizz.wrathpp

import java.io.IOException
import java.nio.ByteBuffer
import java.nio.ByteOrder

/**
 * A game table (WDBC) and the change files the allied races module's generator writes (`put`, `putraw`, `appendraw`, `copyrow`,
 * `remapfield`, `or`, `set`) and Wrath++'s own `drop` and `map`, applied the way mod-skyborne's SkyborneFiles.cpp does as a realm starts and
 * `realm/warcraft/wrathpp/tools/apply_client.py` does at packaging (the same results: DbcChangesTest holds both to one golden).
 * `map WHERE FROM TO DEFAULT KEY=VALUE...` is a rule over whatever rows the table has (the creatures' looks, by race and sex): in
 * every row WHERE holds for (`-`: every row; else `FIELD=VALUE,...`), field TO becomes the VALUE listed for the row's values of the
 * fields FROM (`FIELD,...`), or DEFAULT for a key that isn't listed (`-`: left as it is); each row is looked up once.
 * Wrath++ applies them here, to the client's own tables (the HD look's included), as the looks are put in ([WrathppLooks]).
 */
class DbcTable(data: ByteArray) {
    val fields: Int
    val size: Int
    val records = ArrayList<ByteArray>()
    private var text: ByteArray
    private val strings = HashMap<String, Int>()

    init {
        val b = ByteBuffer.wrap(data).order(ByteOrder.LITTLE_ENDIAN)
        if (data.size < 20 || b.getInt(0) != 0x43424457) throw IOException("not a game table (WDBC)")
        val count = b.getInt(4)
        fields = b.getInt(8)
        size = b.getInt(12)
        val textSize = b.getInt(16)
        if (count < 0 || size < 0 || textSize < 0 || 20L + count.toLong() * size + textSize > data.size) throw IOException("a game table that is cut short")
        for (i in 0 until count) records.add(data.copyOfRange(20 + i * size, 20 + (i + 1) * size))
        text = data.copyOfRange(20 + count * size, 20 + count * size + textSize)
        if (text.isEmpty()) text = byteArrayOf(0)
        var at = 0
        while (at < text.size) {
            var end = at
            while (end < text.size && text[end] != 0.toByte()) end++
            strings.putIfAbsent(String(text, at, end - at, Charsets.UTF_8), at)
            at = end + 1
        }
    }

    private val extra = java.io.ByteArrayOutputStream()

    fun string(value: String): Int {
        strings[value]?.let { return it }
        val at = text.size + extra.size()
        extra.write(value.toByteArray(Charsets.UTF_8)); extra.write(0)
        strings[value] = at
        return at
    }

    fun get(row: Int, field: Int): Int = ByteBuffer.wrap(records[row]).order(ByteOrder.LITTLE_ENDIAN).getInt(field * 4)

    fun set(row: Int, field: Int, value: Int) {
        val r = records[row].copyOf()
        ByteBuffer.wrap(r).order(ByteOrder.LITTLE_ENDIAN).putInt(field * 4, value)
        records[row] = r
    }

    fun write(): ByteArray {
        val all = text + extra.toByteArray()
        val out = ByteBuffer.allocate(20 + records.size * size + all.size).order(ByteOrder.LITTLE_ENDIAN)
        out.putInt(0x43424457).putInt(records.size).putInt(fields).putInt(size).putInt(all.size)
        for (r in records) out.put(r)
        out.put(all)
        return out.array()
    }

    private fun key(r: ByteArray) = ByteBuffer.wrap(r)

    /** The [changes] (a file's text) applied; [IOException] names the line of anything it can't do, and the table is then not to be used. */
    fun apply(changes: String) {
        val hasIds = size >= 4
        val byId = HashMap<Int, Int>()
        fun reindex() { byId.clear(); if (hasIds) for (i in records.indices) byId.putIfAbsent(get(i, 0), i) }
        reindex()
        val whole = HashSet<ByteBuffer>().apply { records.forEach { add(key(it)) } }
        fun rewhole() { whole.clear(); records.forEach { whole.add(key(it)) } }
        var types = ""

        fun place(record: ByteArray) {
            if (hasIds) {
                val id = ByteBuffer.wrap(record).order(ByteOrder.LITTLE_ENDIAN).getInt(0)
                val at = byId[id]
                if (at != null) { records[at] = record; return }
                byId[id] = records.size
            }
            records.add(record)
        }

        var number = 0
        for (raw in changes.split('\n')) {
            number++
            val line = raw.trimEnd('\r')
            if (line.isEmpty() || line[0] == '#') continue
            val f = line.split('\t')
            val where = " (line $number)"
            try {
                when (f[0]) {
                    "types" -> {
                        types = f.getOrElse(1) { "" }
                        if (types.length != fields || size != fields * 4) throw IOException("the table isn't the one these changes are for: $fields fields, ${types.length} expected")
                    }
                    "put" -> {
                        if (types.isEmpty() || f.size != types.length + 1) throw IOException("a row of the wrong size$where")
                        val record = ByteArray(size)
                        val bb = ByteBuffer.wrap(record).order(ByteOrder.LITTLE_ENDIAN)
                        for (i in types.indices) {
                            val v = f[i + 1]
                            bb.putInt(i * 4, when (types[i]) {
                                's' -> string(unescape(v))
                                'f' -> java.lang.Float.floatToRawIntBits(v.toFloat())
                                else -> v.toLong().toInt()
                            })
                        }
                        place(record)
                    }
                    "putraw", "appendraw" -> {
                        val record = if (f.size == 2) hex(f[1]) else ByteArray(0)
                        if (record.size != size) throw IOException("a record of the wrong size$where")
                        if (f[0] == "putraw") place(record) else if (whole.add(key(record))) records.add(record)
                    }
                    "copyrow" -> {
                        if (!hasIds) throw IOException("a row copy the table can't take$where")
                        val from = f[1].toLong().toInt(); val to = f[2].toLong().toInt()
                        val at = byId[from]
                        if (at != null && !byId.containsKey(to)) {
                            val r = records[at].copyOf()
                            ByteBuffer.wrap(r).order(ByteOrder.LITTLE_ENDIAN).putInt(0, to)
                            place(r)
                        }
                    }
                    "remapfield" -> {
                        val field = f[1].toInt(); val from = f[2].toLong().toInt(); val to = f[3].toLong().toInt()
                        if (field >= size / 4) throw IOException("no such field$where")
                        for (row in records.indices) if (get(row, field) == from) set(row, field, to)
                        rewhole()
                        if (field == 0 && hasIds) reindex()
                    }
                    "drop" -> {
                        if (f.size < 3 || f.size % 2 == 0) throw IOException("a row drop of the wrong size$where")
                        val pairs = (1 until f.size step 2).map { f[it].toInt() to f[it + 1].toLong().toInt() }
                        if (pairs.any { it.first >= size / 4 }) throw IOException("no such field$where")
                        val kept = ArrayList<ByteArray>()
                        for (row in records.indices) if (!pairs.all { (a, b) -> get(row, a) == b }) kept.add(records[row])
                        records.clear(); records.addAll(kept)
                        rewhole(); reindex()
                    }
                    "map" -> {
                        if (f.size < 5) throw IOException("a map of the wrong size$where")
                        val count = size / 4
                        val conds = if (f[1] == "-") emptyList() else f[1].split(',').map { c ->
                            val p = c.split('=')
                            if (p.size != 2) throw IOException("a map's condition that isn't FIELD=VALUE$where")
                            p[0].toInt() to p[1].toLong().toInt()
                        }
                        val from = f[2].split(',').map { it.toInt() }
                        val to = f[3].toInt()
                        val default = if (f[4] == "-") null else f[4].toLong().toInt()
                        if ((conds.map { it.first } + from + to).any { it < 0 || it >= count }) throw IOException("no such field$where")
                        val lookup = HashMap<List<Int>, Int>()
                        for (i in 5 until f.size) {
                            val at = f[i].indexOf('=')
                            if (at < 0) throw IOException("a map's pair that isn't KEY=VALUE$where")
                            val key = f[i].substring(0, at).split(',').map { it.toLong().toInt() }
                            if (key.size != from.size) throw IOException("a map's key of the wrong size$where")
                            lookup[key] = f[i].substring(at + 1).toLong().toInt()
                        }
                        for (row in records.indices) {
                            if (!conds.all { (a, b) -> get(row, a) == b }) continue
                            val value = lookup[from.map { get(row, it) }] ?: default
                            if (value != null) set(row, to, value)
                        }
                        rewhole()
                        if (to == 0 && hasIds) reindex()
                    }
                    "or", "set" -> {
                        val id = f[1].toLong().toInt(); val field = f[2].toInt(); val value = f[3].toLong().toInt()
                        if (!hasIds || field >= size / 4) throw IOException("a field change the table can't take$where")
                        val row = byId[id]
                        if (row != null) set(row, field, if (f[0] == "or") get(row, field) or value else value)
                    }
                    else -> throw IOException("unknown change \"${f[0]}\"$where")
                }
            } catch (e: IOException) {
                throw e
            } catch (e: RuntimeException) {
                throw IOException("a value that isn't one$where")
            }
        }
    }

    companion object {
        fun unescape(s: String): String {
            val out = StringBuilder()
            var i = 0
            while (i < s.length) {
                val c = s[i]
                if (c == '\\' && i + 1 < s.length) {
                    out.append(when (val n = s[i + 1]) { 't' -> '\t'; 'n' -> '\n'; else -> n })
                    i += 2
                } else { out.append(c); i++ }
            }
            return out.toString()
        }

        fun hex(s: String): ByteArray {
            if (s.length % 2 != 0) throw IOException("a record that isn't hexadecimal")
            return ByteArray(s.length / 2) { s.substring(it * 2, it * 2 + 2).toInt(16).toByte() }
        }
    }
}
