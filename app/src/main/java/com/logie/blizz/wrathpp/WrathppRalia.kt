package com.logie.blizz.wrathpp

import com.logie.blizz.wowclient.Blp
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.io.IOException
import java.io.InputStream
import java.security.MessageDigest
import java.util.zip.ZipInputStream

/**
 * Ralia's mod on Wrath++ (the user: "Make an import for ralias mod too it will look for ralia.zip"): a set of character
 * textures named as today's game names them (`Character/Human/Female/humanfemaleskin00_03_hd.blp`), from a zip of
 * yours; never in the app or the repository. [importZip] keeps the zip's `Character` textures; [apply] puts them into
 * Wrath++'s looks ([WrathppLooks], `Data/patch-Z.MPQ`):
 *
 *  - the looks say which of today's files each of their skins was made from (`wrathpp-skins.json`, made with them by
 *    `realm/warcraft/wrathpp/tools/sl_skin_names.py`); a skin whose file the set has takes the set's: its body half
 *    (today's body texture is twice as wide as tall) made the 512 x 512 palettized skin 3.3.5 composes from ([Blp]),
 *    in place of the looks' own, which is kept beside it (`.orig`);
 *  - such a skin's underwear is the set's of the same number (`...nakedpelvisskin00_03_hd.blp`, `...nakedtorsoskin...`).
 *    The women's are empty pictures (their bodies are drawn without): the skin's row of the game's character table
 *    keeps its place and loses its textures, which are noted to put back. A painted one (the set has the Forsaken men's
 *    and no bodies for them) goes over the looks' own, at its size, with its alpha.
 *
 * Every race and sex the set has files for, the Forsaken among them, and every regular skin of theirs (the user: "regular
 * skins need the ralias patch applied. Base skins"): a skin the set has no file for (a colour today's game has and the
 * set not, a colour with war paint or a tattoo the looks made into the skin) is the set's skin nearest to it in colour,
 * carried over to it ([carried]: the set's picture times the looks' own skin over the looks' own of that nearest one,
 * pixel by pixel, which brings its colour and lays its paint on), with that skin's underwear.
 * The undead skins ([WrathppUndead]) are pictures of their own and are not changed by this (the women's were painted on
 * this set's bodies). Applied again when the looks or the zip change; taken out, the looks' own skins and underwear come
 * back. NOT run on a phone; unit-tested.
 */
object WrathppRalia {
    const val DIR = "wrathpp-ralia"
    const val STAMP = "wrathpp-ralia.stamp"
    const val NAMES = "wrathpp-skins.json"
    private const val ROWS = "wrathpp-ralia.rows.json"
    private const val UNDERWEAR = 4

    fun store(context: android.content.Context): File = File(context.applicationContext.filesDir, DIR)
    fun installed(store: File): Boolean = sha(store) != null && (File(store, "files").list()?.isNotEmpty() == true)
    fun sha(store: File): String? = File(store, STAMP).takeIf { it.isFile }?.readText()?.trim()?.takeIf { it.isNotEmpty() }
    fun count(store: File): Int = File(store, "files").list()?.size ?: 0

    /** Taken off the phone, and not looked for again ([lookFor]) until a zip is picked or used by hand. */
    fun remove(store: File) {
        store.deleteRecursively()
        off(store).apply { parentFile?.mkdirs() }.writeText("removed\n")
    }

    private fun off(store: File) = File(store.path + ".off")
    private const val SOURCE = "source"

    /**
     * The zip looked for by its name (the user: "it will look for ralia.zip"): [found] (ImportFinder's `ralia.zip` in
     * Download, Documents or the top of the phone's storage; null when there is none or the app may not look) is taken
     * in by itself when nothing is imported, and again when the file there has changed since it was taken from there.
     * Never after [remove], and never over a zip picked by hand. Returns how many textures it took in, or null when it
     * took none.
     */
    fun lookFor(store: File, found: File?): Int? {
        if (found == null || !found.isFile || off(store).exists()) return null
        val mark = "${found.length()} ${found.lastModified()}"
        val source = File(store, SOURCE)
        if (installed(store) && (!source.isFile || source.readText().trim() == mark)) return null
        val n = found.inputStream().use { importZip(store, it) }
        File(store, SOURCE).writeText("$mark\n")
        return n
    }

    /**
     * Takes the zip's character textures into [store] (each under its file name, lower case), in place of what was there;
     * returns how many. A zip with none is refused and [store] left as it was.
     */
    fun importZip(store: File, zip: InputStream): Int {
        val fresh = File(store.path + ".new").apply { deleteRecursively() }
        val files = File(fresh, "files").apply { mkdirs() }
        val digest = MessageDigest.getInstance("SHA-256")
        var n = 0
        try {
            val counted = java.security.DigestInputStream(zip, digest)
            ZipInputStream(counted).use { z ->
                while (true) {
                    val entry = z.nextEntry ?: break
                    if (entry.isDirectory) continue
                    val path = entry.name.replace('\\', '/').lowercase()
                    if (!path.endsWith(".blp") || !("/$path").contains("/character/")) continue
                    val name = path.substringAfterLast('/')
                    if (name.isEmpty() || name.contains("..")) continue
                    File(files, name).outputStream().use { z.copyTo(it) }
                    n++
                }
                val rest = ByteArray(1 shl 14)
                while (counted.read(rest) >= 0) { /* the digest is of the whole file */ }
            }
            if (n == 0) throw IOException("This zip has no character textures (a Character folder of .blp files) in it.")
            File(fresh, STAMP).writeText(digest.digest().joinToString("") { "%02x".format(it) } + "\n")
            store.deleteRecursively()
            if (!fresh.renameTo(store)) throw IOException("The textures couldn't be put in place.")
            off(store).delete()
            return n
        } finally {
            fresh.deleteRecursively()
        }
    }

    private class Named(val race: Int, val sex: Int, val index: Int, val path: String, val retail: String)

    private fun names(patch: File): List<Named> {
        val file = File(patch, NAMES).takeIf { it.isFile } ?: return emptyList()
        val models = JSONObject(file.readText()).optJSONObject("models") ?: return emptyList()
        val out = ArrayList<Named>()
        for (key in models.keys()) {
            val m = models.getJSONObject(key)
            val skins = m.getJSONArray("skins")
            for (i in 0 until skins.length()) skins.getJSONObject(i).let { out.add(Named(m.getInt("race"), m.getInt("sex"), it.getInt("index"), it.getString("path"), it.getString("retail").lowercase())) }
        }
        return out
    }

    /**
     * The imported set put into Wrath++'s looks in [client], or taken out when nothing is imported. Returns how many
     * skins are the set's now (0: none imported, no looks, or looks without their list of names). [say]: progress.
     */
    fun apply(store: File, client: File, say: (String, Float?) -> Unit = { _, _ -> }): Int {
        val patch = File(client, "Data/${WrathppLooks.PATCH}")
        val table = File(patch, "DBFilesClient/CharSections.dbc")
        if (!table.isFile) return 0
        val stamp = File(patch, STAMP)
        val rowsFile = File(patch, ROWS)
        val zipSha = if (installed(store)) sha(store) else null
        val looks = File(patch, WrathppLooks.MARKER).takeIf { it.isFile }?.readText()?.trim().orEmpty()
        val want = "$zipSha $looks"
        if (zipSha != null && stamp.isFile && stamp.readText().trim() == want) return rowsFile.takeIf { it.isFile }?.let { JSONObject(it.readText()).optInt("skins") } ?: 0
        // what an earlier set put in comes out first: the looks' own skins back, the underwear's textures back
        if (stamp.isFile || rowsFile.isFile) takeOut(patch, table, rowsFile)
        stamp.delete()
        if (zipSha == null) return 0
        fun has(name: String) = File(store, "files/$name").isFile
        fun pelvis(retail: String) = retail.replace("skin00_", "nakedpelvisskin00_")
        fun torso(retail: String) = retail.replace("skin00_", "nakedtorsoskin00_")
        val direct = names(patch).filter { has(it.retail) || has(pelvis(it.retail)) || has(torso(it.retail)) }
        if (direct.isEmpty()) return 0
        val dbc = WrathppUndead.Dbc.read(table.readBytes(), WrathppUndead.KINDS)
        // the looks' own picture of a skin (kept beside it once a set was put over it)
        fun own(path: String): Blp.Image? {
            val f = File(patch, path.replace('\\', '/'))
            val file = File(f.path + ".orig").takeIf { it.isFile } ?: f.takeIf { it.isFile } ?: return null
            return runCatching { Blp.read(file.readBytes()).resized(512, 512) }.getOrNull()
        }
        fun ralia(retail: String): Blp.Image? = if (has(retail)) runCatching { Blp.read(File(store, "files/$retail").readBytes()) }
            .getOrNull()?.let { (if (it.width == 2 * it.height) it.leftHalf() else it).resized(512, 512) } else null
        // every regular skin (a skin row's texture, not one of the undead skins) of a race and sex the set has a body for
        val bodies = HashMap<Named, Blp.Image>()
        for (skin in direct) ralia(skin.retail)?.let { bodies[skin] = it }
        val carriedFrom = ArrayList<Pair<Named, Named>>()
        for ((key, sources) in bodies.keys.groupBy { it.race to it.sex }) {
            val known = direct.filter { (it.race to it.sex) == key }.map { it.index }.toSet()
            val withLooks = sources.mapNotNull { src -> own(src.path)?.let { src to it } }
            if (withLooks.isEmpty()) continue
            val rows = dbc.rows.filter { it[1] == key.first && it[2] == key.second && it[3] == 0 && it[8] == 0 && (it[4] as String).isNotEmpty() &&
                !(it[4] as String).contains("Undead", ignoreCase = true) && (it[9] as Int) !in known }
            for (row in rows.distinctBy { it[4] as String }) {
                val path = row[4] as String
                val target = own(path) ?: continue
                val (src, srcLooks) = withLooks.minByOrNull { distance(mean(it.second), mean(target)) } ?: continue
                val named = Named(key.first, key.second, row[9] as Int, path, src.retail)
                bodies[named] = carried(bodies.getValue(src), srcLooks, target)
                carriedFrom.add(named to src)
            }
        }
        val named = direct + carriedFrom.map { it.first }
        val changed = JSONArray()
        val added = JSONArray()
        var done = 0
        for ((at, skin) in named.withIndex()) {
            say("Putting in Ralia's skins: ${at + 1} of ${named.size}", at.toFloat() / named.size)
            // the body: the set's left half as the 512 x 512 skin 3.3.5 composes from, over the looks' own (kept beside it)
            val target = File(patch, skin.path.replace('\\', '/'))
            val body = if (target.isFile) bodies[skin] else null
            if (body != null) over(target, Blp.writePalette(body))
            // its underwear (the row's two textures, pelvis and torso): the set's of the same number. An empty picture
            // (the women's: their bodies are drawn without) leaves the row without one; a painted one (the Forsaken
            // men's) goes over the looks' own, or beside the skin where the row had none. A body with neither: without.
            var touched = body != null
            for (row in dbc.rows) {
                if (row[1] != skin.race || row[2] != skin.sex || row[3] != UNDERWEAR || row[9] != skin.index) continue
                val before = listOf(row[4] as String, row[5] as String)
                for ((column, name) in listOf(4 to pelvis(skin.retail), 5 to torso(skin.retail))) {
                    val had = row[column] as String
                    val picture = if (has(name)) runCatching { Blp.read(File(store, "files/$name").readBytes()) }.getOrNull() else null
                    if (picture == null) { if (body != null) row[column] = ""; continue }
                    if (picture.empty()) { row[column] = ""; continue }
                    val own = File(patch, had.replace('\\', '/')).takeIf { had.isNotEmpty() && it.isFile }
                    if (own != null) {
                        val size = runCatching { Blp.size(own.readBytes()) }.getOrNull() ?: (256 to 128)
                        over(own, Blp.writePalette(picture.resized(size.first, size.second), alpha = true))
                    } else {
                        val path = skin.path.substringBeforeLast('\\') + "\\Ralia_" + name.removeSuffix(".blp").removeSuffix("_hd") + ".blp"
                        File(patch, path.replace('\\', '/')).apply { parentFile?.mkdirs() }.writeBytes(Blp.writePalette(picture.resized(256, 128), alpha = true))
                        added.put(path)
                        row[column] = path
                    }
                    touched = true
                }
                if (before != listOf(row[4], row[5])) changed.put(JSONArray(listOf(skin.race, skin.sex, skin.index, before[0], before[1])))
            }
            if (touched) done++
        }
        rowsFile.writeText(JSONObject().put("skins", done).put("rows", changed).put("added", added).toString())
        write(table, dbc.write())
        stamp.writeText("$want\n")
        return done
    }

    private fun mean(image: Blp.Image): DoubleArray {
        val sum = DoubleArray(3)
        val n = image.width * image.height
        for (i in 0 until n) for (c in 0 until 3) sum[c] += (image.rgba[i * 4 + c].toInt() and 255).toDouble()
        return DoubleArray(3) { sum[it] / maxOf(1, n) }
    }

    private fun distance(a: DoubleArray, b: DoubleArray) = (0 until 3).sumOf { (a[it] - b[it]) * (a[it] - b[it]) }

    /**
     * The set's picture of one skin ([set]) carried over to another: each pixel times the looks' own picture of the other
     * ([to]) over the looks' own of the one ([from]), channel by channel (all three 512 x 512). Where the looks' two
     * pictures are alike only their colour differs, and the set's shading and detail stay; where the other has paint or
     * a tattoo the one has not, it is laid on.
     */
    internal fun carried(set: Blp.Image, from: Blp.Image, to: Blp.Image): Blp.Image {
        require(set.width == from.width && set.width == to.width && set.height == from.height && set.height == to.height)
        val out = ByteArray(set.rgba.size)
        for (i in 0 until set.width * set.height) {
            for (c in 0 until 3) {
                val k = i * 4 + c
                val ratio = ((to.rgba[k].toInt() and 255) + 8.0) / ((from.rgba[k].toInt() and 255) + 8.0)
                out[k] = ((set.rgba[k].toInt() and 255) * ratio.coerceAtMost(4.0)).toInt().coerceIn(0, 255).toByte()
            }
            out[i * 4 + 3] = set.rgba[i * 4 + 3]
        }
        return Blp.Image(set.width, set.height, out)
    }

    /** [bytes] over the looks' [target], whose own is kept beside it (`.orig`) to put back. */
    private fun over(target: File, bytes: ByteArray) {
        val orig = File(target.path + ".orig")
        if (!orig.isFile) target.copyTo(orig)
        write(target, bytes)
    }

    private fun takeOut(patch: File, table: File, rowsFile: File) {
        patch.walkTopDown().filter { it.isFile && it.name.endsWith(".blp.orig") }.toList().forEach { orig ->
            val target = File(orig.path.removeSuffix(".orig"))
            target.delete()
            orig.renameTo(target)
        }
        if (rowsFile.isFile) {
            val added = JSONObject(rowsFile.readText()).optJSONArray("added") ?: JSONArray()
            for (i in 0 until added.length()) File(patch, added.getString(i).replace('\\', '/')).delete()
            val rows = JSONObject(rowsFile.readText()).optJSONArray("rows") ?: JSONArray()
            if (rows.length() > 0) {
                val dbc = WrathppUndead.Dbc.read(table.readBytes(), WrathppUndead.KINDS)
                for (i in 0 until rows.length()) {
                    val r = rows.getJSONArray(i)
                    for (row in dbc.rows) {
                        if (row[1] == r.getInt(0) && row[2] == r.getInt(1) && row[3] == UNDERWEAR && row[9] == r.getInt(2)) { row[4] = r.getString(3); row[5] = r.getString(4) }
                    }
                }
                write(table, dbc.write())
            }
            rowsFile.delete()
        }
    }

    private fun write(file: File, bytes: ByteArray) {
        val tmp = File(file.path + ".tmp")
        tmp.writeBytes(bytes)
        if (!tmp.renameTo(file)) { file.delete(); if (!tmp.renameTo(file)) throw IOException("${file.path} couldn't be written") }
    }
}
