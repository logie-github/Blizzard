package com.logie.blizz.wrathpp

import org.json.JSONObject
import java.io.File
import java.io.IOException
import java.io.InputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.security.MessageDigest
import java.util.zip.ZipInputStream

/**
 * Undead skins for Wrath++'s living races (the user: "These should be NEW skins added to the roster, not replacing
 * anything"): a zip you import on the phone (made by `realm/warcraft/wrathpp/tools/undead_pack.py`; textures, so never
 * in the app or the repository), holding for a race and sex a few skins, each a body texture and a face of its own:
 *
 *     manifest.json   { "format": 1, "kind": "wrathpp-undead-skins", "models": { "1_1": { "race": 1, "sex": 1,
 *                       "name": "HumanFemale", "underwear": "none" | "race",
 *                       "skins": [ { "name": "Grave Blue", "swatch": 7833770, "skin": "Character\\…\\…SkinUndead00_00.blp",
 *                                    "face": "Character\\…\\…FaceLowerUndead00.blp" } ] } } }
 *     client/…        the textures, at the game's paths the manifest names (names of their own: nothing of the game's)
 *
 * [apply] puts them into Wrath++'s looks ([WrathppLooks]: `Data/patch-Z.MPQ` and the server's `share/dbc`): each skin a
 * new skin colour after the race and sex's own in the game's character table (CharSections), with the rows the game asks
 * of a colour before it lets you pick it (WarcraftXL-Labs/client, CCharacterComponent::SetNextSkin: the skin, a face for
 * every face number, and underwear, which is the race's first skin's or none), in the game's patch and the server's
 * tables alike, so a character made with one is accepted. The creator's Undead switch (WrathppCreate.lua) reads
 * `WrathppUndead.lua`, written here: which colour is the first undead one, and their names and swatches. Every other
 * race, sex and row is left as it was; applied again whenever the looks or the import change, taken out when the import
 * is removed. NOT run on a phone; [withUndead], [importZip] and [apply] are unit-tested.
 */
object WrathppUndead {
    const val DIR = "wrathpp-undead"
    const val LUA = "WrathppUndead.lua"
    /** In the store: the zip's SHA-256. In the game's patch and the server's dbc: what was applied (it and the looks'). */
    const val STAMP = "wrathpp-undead.stamp"
    private const val KIND = "wrathpp-undead-skins"
    private const val TABLE = "CharSections.dbc"
    const val KINDS = "iiiisssiii"                 // id, race, sex, section, three textures, flags, variation, colour
    private const val SKIN = 0
    private const val FACE = 1
    private const val UNDERWEAR = 4

    class Skin(val name: String, val swatch: Int, val skin: String, val face: String)
    class Model(val key: String, val race: Int, val sex: Int, val name: String, val underwear: String, val skins: List<Skin>)

    fun parseManifest(text: String): List<Model> {
        val json = JSONObject(text)
        if (json.optString("kind") != KIND || json.optInt("format") != 1) throw IOException("This isn't a file of undead skins for Wrath++.")
        val models = json.getJSONObject("models")
        return models.keys().asSequence().sorted().map { key ->
            val m = models.getJSONObject(key)
            val skins = m.getJSONArray("skins")
            Model(key, m.getInt("race"), m.getInt("sex"), m.optString("name", key), m.optString("underwear", "race"),
                (0 until skins.length()).map { i -> skins.getJSONObject(i).let { Skin(it.getString("name"), it.optInt("swatch"), it.getString("skin"), it.getString("face")) } })
        }.filter { it.skins.isNotEmpty() }.toList()
    }

    /** Where the imported skins are kept on the phone (the app's own files). */
    fun store(context: android.content.Context): File = File(context.applicationContext.filesDir, DIR)

    fun installed(store: File): Boolean = File(store, "manifest.json").isFile
    fun sha(store: File): String? = File(store, STAMP).takeIf { it.isFile }?.readText()?.trim()?.takeIf { it.isNotEmpty() }
    fun models(store: File): List<Model> = parseManifest(File(store, "manifest.json").readText())
    fun remove(store: File) { store.deleteRecursively() }

    /**
     * Takes the zip into [store] (its manifest and `client/` textures), in place of what was there; returns its races and
     * sexes. Anything else in it is left; a zip that isn't one of these, or that names a texture it hasn't, is refused
     * and [store] left as it was.
     */
    fun importZip(store: File, zip: InputStream): List<Model> {
        val fresh = File(store.path + ".new").apply { deleteRecursively(); mkdirs() }
        val digest = MessageDigest.getInstance("SHA-256")
        try {
            val counted = java.security.DigestInputStream(zip, digest)
            ZipInputStream(counted).use { z ->
                while (true) {
                    val entry = z.nextEntry ?: break
                    if (entry.isDirectory) continue
                    val name = entry.name.replace('\\', '/').removePrefix("wrathpp-undead/")
                    if (name.startsWith("/") || name.split('/').any { it == ".." || it.isEmpty() }) throw IOException("Bad path in the file: ${entry.name}")
                    if (name != "manifest.json" && !(name.startsWith("client/") && name.endsWith(".blp", ignoreCase = true))) continue
                    File(fresh, name).apply { parentFile?.mkdirs() }.outputStream().use { z.copyTo(it) }
                }
                // (the digest is of the whole file: what is after the last entry too)
                val rest = ByteArray(1 shl 14)
                while (counted.read(rest) >= 0) { /* read on */ }
            }
            val manifest = File(fresh, "manifest.json")
            if (!manifest.isFile) throw IOException("This isn't a file of undead skins for Wrath++ (no manifest.json in it).")
            val models = parseManifest(manifest.readText())
            if (models.isEmpty()) throw IOException("The file has no skins in it.")
            for (m in models) for (s in m.skins) for (path in listOf(s.skin, s.face)) {
                if (!textureFile(fresh, path).isFile) throw IOException("The file names a texture it hasn't: $path")
            }
            File(fresh, STAMP).writeText(digest.digest().joinToString("") { "%02x".format(it) } + "\n")
            store.deleteRecursively()
            if (!fresh.renameTo(store)) throw IOException("The skins couldn't be put in place.")
            return models
        } finally {
            fresh.deleteRecursively()
        }
    }

    private fun textureFile(store: File, gamePath: String) = File(store, "client/" + gamePath.replace('\\', '/'))

    // --- the game's table (WDBC) -----------------------------------------------------------------------------------------

    /** A table of the game's: rows of numbers and texts ([kinds]: 'i' or 's' a column), as it reads and writes them. */
    class Dbc(val kinds: String, val rows: MutableList<Array<Any>>) {
        fun write(): ByteArray {
            val strings = java.io.ByteArrayOutputStream().apply { write(0) }
            val where = HashMap<String, Int>().apply { put("", 0) }
            val body = ByteBuffer.allocate(rows.size * kinds.length * 4).order(ByteOrder.LITTLE_ENDIAN)
            for (row in rows) for ((i, k) in kinds.withIndex()) {
                if (k == 's') {
                    val text = row[i] as String
                    body.putInt(where.getOrPut(text) { strings.size().also { strings.write(text.toByteArray(Charsets.UTF_8)); strings.write(0) } })
                } else body.putInt(row[i] as Int)
            }
            val head = ByteBuffer.allocate(20).order(ByteOrder.LITTLE_ENDIAN)
            head.put("WDBC".toByteArray(Charsets.US_ASCII)).putInt(rows.size).putInt(kinds.length).putInt(kinds.length * 4).putInt(strings.size())
            return head.array() + body.array() + strings.toByteArray()
        }

        companion object {
            fun read(data: ByteArray, kinds: String): Dbc {
                if (data.size < 20 || String(data, 0, 4, Charsets.US_ASCII) != "WDBC") throw IOException("Not one of the game's tables")
                val b = ByteBuffer.wrap(data).order(ByteOrder.LITTLE_ENDIAN)
                val count = b.getInt(4); val fields = b.getInt(8); val size = b.getInt(12); val textSize = b.getInt(16)
                if (fields != kinds.length || size != fields * 4 || 20L + count.toLong() * size + textSize > data.size) throw IOException("Not the table expected ($fields columns)")
                val text = 20 + count * size
                fun string(at: Int): String {
                    var end = text + at
                    while (end < data.size && data[end] != 0.toByte()) end++
                    return String(data, text + at, end - text - at, Charsets.UTF_8)
                }
                val rows = ArrayList<Array<Any>>(count)
                for (r in 0 until count) rows.add(Array(fields) { i ->
                    val v = b.getInt(20 + r * size + i * 4)
                    if (kinds[i] == 's') string(v) else v
                })
                return Dbc(kinds, rows)
            }
        }
    }

    private fun isOurs(row: Array<Any>) = (row[4] as String).contains("Undead", ignoreCase = true)

    /**
     * [table] (CharSections) with [models]' skins as new colours after each race and sex's own, and without whatever an
     * earlier call put in. Returns, a model key, the first new colour's number (from 0). A race and sex the table has no
     * skins for is left out.
     */
    fun withUndead(table: Dbc, models: List<Model>): Map<String, Int> {
        val rows = table.rows
        // what an earlier call put in: its skins (by their textures' names), and the faces and underwear of their colours
        val had = rows.filter { it[3] == SKIN && isOurs(it) }.map { (it[1] as Int) to (it[2] as Int) }.toSet()
        rows.removeAll { it[3] == SKIN && isOurs(it) }
        val living = HashMap<Pair<Int, Int>, Int>()
        for (r in rows) if (r[3] == SKIN) {
            val key = (r[1] as Int) to (r[2] as Int)
            living[key] = maxOf(living[key] ?: 0, (r[9] as Int) + 1)
        }
        rows.removeAll { row ->
            val key = (row[1] as Int) to (row[2] as Int)
            (row[3] == FACE || row[3] == UNDERWEAR) && key in had && (row[9] as Int) >= (living[key] ?: 0)
        }
        var nextId = (rows.maxOfOrNull { it[0] as Int } ?: 0) + 1
        val first = LinkedHashMap<String, Int>()
        for (m in models) {
            val n = living[m.race to m.sex] ?: continue
            val mine = rows.filter { it[1] == m.race && it[2] == m.sex }
            val firstSkin = mine.firstOrNull { it[3] == SKIN && it[9] == 0 } ?: continue
            val underwear = mine.firstOrNull { it[3] == UNDERWEAR && it[9] == 0 }
            val faces = mine.filter { it[3] == FACE && it[9] == 0 }
            first[m.key] = n
            for ((k, s) in m.skins.withIndex()) {
                val colour = n + k
                // (the second texture: the first skin's extra, where the race's skins have one: the Forsaken's bony
                // pieces are drawn from it, m2.py's skin extra; an empty one leaves them without a picture)
                rows.add(arrayOf(nextId++, m.race, m.sex, SKIN, s.skin, firstSkin[5], "", firstSkin[7], 0, colour))
                val own = m.underwear == "race" && underwear != null
                rows.add(arrayOf(nextId++, m.race, m.sex, UNDERWEAR, if (own) underwear!![4] else "", if (own) underwear!![5] else "", "", underwear?.get(7) ?: firstSkin[7], 0, colour))
                for (f in faces) rows.add(arrayOf(nextId++, m.race, m.sex, FACE, s.face, f[5], "", f[7], f[8], colour))
            }
        }
        return first
    }

    fun lua(models: List<Model>, first: Map<String, Int>): String {
        val out = StringBuilder("-- Wrath++'s undead skins (the app's import): the first undead colour of a race and sex, and the skins.\nWrathppUndead = { models = {\n")
        for (m in models) {
            val n = first[m.key] ?: continue
            out.append("\t[\"${m.key}\"] = { first = $n, skins = { ")
            out.append(m.skins.joinToString(", ") { "{ n = \"${it.name.replace("\\", "").replace("\"", "")}\", s = ${it.swatch and 0xFFFFFF} }" })
            out.append(" } },\n")
        }
        return out.append("} }\n").toString()
    }

    /**
     * The imported skins put into Wrath++'s looks in [client] and [server], or taken out when nothing is imported.
     * Returns the creator's `WrathppUndead.lua`, or null when there are none in (nothing imported, or no looks to add to).
     */
    fun apply(store: File, client: File, server: File): String? {
        val patch = File(client, "Data/${WrathppLooks.PATCH}")
        val gameTable = File(patch, "DBFilesClient/$TABLE")
        val serverTable = File(server, "share/dbc/$TABLE")
        val luaFile = File(patch, "Interface/GlueXML/$LUA")
        val stamps = listOf(File(patch, STAMP), File(serverTable.parentFile, STAMP))
        if (!gameTable.isFile || !serverTable.isFile) return null
        val zipSha = if (installed(store)) sha(store) else null
        if (zipSha == null) {
            // removed: the rows and the files this put in go
            if (stamps.any { it.isFile } || luaFile.isFile) {
                for (file in listOf(gameTable, serverTable)) {
                    val table = Dbc.read(file.readBytes(), KINDS)
                    withUndead(table, emptyList())
                    replace(file, table.write())
                }
                luaFile.delete(); stamps.forEach { it.delete() }
            }
            return null
        }
        val looks = File(patch, WrathppLooks.MARKER).takeIf { it.isFile }?.readText()?.trim().orEmpty()
        val want = "$zipSha $looks"
        if (stamps.all { it.isFile && it.readText().trim() == want } && luaFile.isFile) return luaFile.readText()
        val models = models(store)
        File(store, "client").walkTopDown().filter { it.isFile }.forEach { f ->
            val to = File(patch, f.relativeTo(File(store, "client")).path)
            to.parentFile?.mkdirs()
            f.copyTo(to, overwrite = true)
        }
        var first: Map<String, Int> = emptyMap()
        for (file in listOf(serverTable, gameTable)) {
            val table = Dbc.read(file.readBytes(), KINDS)
            first = withUndead(table, models)
            replace(file, table.write())
        }
        val text = lua(models, first)
        luaFile.parentFile?.mkdirs()
        luaFile.writeText(text)
        stamps.forEach { it.writeText("$want\n") }
        return text
    }

    private fun replace(file: File, bytes: ByteArray) {
        val tmp = File(file.path + ".tmp")
        tmp.writeBytes(bytes)
        if (!tmp.renameTo(file)) { file.delete(); if (!tmp.renameTo(file)) throw IOException("${file.path} couldn't be written") }
    }
}
