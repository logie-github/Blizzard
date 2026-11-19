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
    private const val FACE = 1

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
     * The skins the imported set supplies a texture for itself (its file for the skin, or for its underwear: the ones [apply] puts in
     * directly, not the ones it only carries over to), by model ("1_0": race and sex) the model's name and the skins' places in the
     * looks, for [WrathppSkins]. A skin whose file name has "mannequin" in it is matched like any other, by its name. Null when
     * nothing is imported or the looks have no list of names: nothing is filtered then.
     */
    internal fun supplied(store: File, client: File): Map<String, Pair<String, List<Int>>>? {
        if (!installed(store)) return null
        val patch = File(client, "Data/${WrathppLooks.PATCH}")
        // (only once the set is in the looks: a list of the set's skins over the looks' own pictures is what build 399 showed)
        if (!File(patch, STAMP).isFile) return null
        fun has(name: String) = File(store, "files/$name").isFile
        val direct = names(patch).filter { has(it.retail) || has(it.retail.replace("skin00_", "nakedpelvisskin00_")) || has(it.retail.replace("skin00_", "nakedtorsoskin00_")) }
        if (direct.isEmpty()) return null
        val called = HashMap<String, String>()
        File(patch, NAMES).takeIf { it.isFile }?.let { f ->
            val models = JSONObject(f.readText()).optJSONObject("models")
            if (models != null) for (k in models.keys()) called[k] = models.getJSONObject(k).optString("name")
        }
        val places = HashMap<String, MutableSet<Int>>()
        for (n in direct) places.getOrPut("${n.race}_${n.sex}") { sortedSetOf() }.add(n.index)
        // the allied women's skins carried over from their donor race's bodies ([apply], WrathppSkins.DONORS): the set is their base too
        val rows = File(patch, ROWS).takeIf { it.isFile }?.let { runCatching { JSONObject(it.readText()).optJSONArray("allied") }.getOrNull() }
        if (rows != null) for (i in 0 until rows.length()) rows.getJSONArray(i).let { r -> places.getOrPut("${r.getInt(0)}_${r.getInt(1)}") { sortedSetOf() }.add(r.getInt(2)) }
        return places.toSortedMap(compareBy<String>({ it.substringBefore('_').toInt() }, { it.substringAfter('_').toInt() }))
            .mapValues { (key, set) -> (called[key] ?: WrathppSkins.RACE_NAMES[key.substringBefore('_').toInt()]?.let { it + if (key.endsWith("_1")) "Female" else "Male" } ?: key) to set.toList() }
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
        val want = "$zipSha $looks donors1 faces1"
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
        val ownPicture = names(patch).filter { it.retail.isEmpty() }
        val dbc = WrathppUndead.Dbc.read(table.readBytes(), WrathppUndead.KINDS)
        // the looks' own picture of a skin (kept beside it once a set was put over it)
        fun own(path: String): Blp.Image? {
            val f = File(patch, path.replace('\\', '/'))
            val file = File(f.path + ".orig").takeIf { it.isFile } ?: f.takeIf { it.isFile } ?: return null
            return runCatching { Blp.read(file.readBytes()).resized(512, 512) }.getOrNull()
        }
        fun ralia(retail: String): Blp.Image? = if (has(retail)) runCatching { Blp.read(File(store, "files/$retail").readBytes()) }
            .getOrNull()?.let { (if (it.width == 2 * it.height) it.leftHalf() else it).resized(512, 512) } else null
        // A few decoded pictures at a time: the set's and the looks' pictures are read when a skin is made and dropped after it. (Build
        // 399, 19 November 2026: every skin's 512 x 512 picture was held until all were planned, about 1 MB each; with the allied women's
        // donors that passed the phone's 512 MB and the whole step failed, "ralia FAILED: Failed to allocate a 1048592 byte allocation",
        // every Play, leaving the looks' own skins under a list that offered only the set's.)
        val held = object : LinkedHashMap<String, Blp.Image>(8, 0.75f, true) {
            override fun removeEldestEntry(eldest: MutableMap.MutableEntry<String, Blp.Image>?) = size > 6
        }
        fun ownHeld(path: String): Blp.Image? = held["o:$path"] ?: own(path)?.also { held["o:$path"] = it }
        fun raliaHeld(retail: String): Blp.Image? = held["r:$retail"] ?: ralia(retail)?.also { held["r:$retail"] = it }
        // every regular skin (a skin row's texture, not one of the undead skins) of a race and sex the set has a body for
        val withBody = direct.filter { has(it.retail) && runCatching { Blp.size(File(store, "files/${it.retail}").readBytes()) }.isSuccess }
        val carriedFrom = ArrayList<Pair<Named, Named>>()
        val fromDonor = ArrayList<Named>()                      // (the allied women's skins: all of them are offered, WrathppSkins)
        // a model the set has bodies for takes them for its own other colours; an allied woman takes her donor race's ([WrathppSkins.DONORS]:
        // the body she is built like), which makes the set her base (the user, 19 November 2026)
        val byModel = withBody.groupBy { it.race to it.sex }
        val plan = ArrayList<Pair<Pair<Int, Int>, Pair<Int, Int>>>()
        for (model in byModel.keys) plan.add(model to model)
        for ((race, donor) in WrathppSkins.DONORS) {
            if ((race to WrathppSkins.WOMAN) !in byModel && (donor to WrathppSkins.WOMAN) in byModel) plan.add((race to WrathppSkins.WOMAN) to (donor to WrathppSkins.WOMAN))
        }
        val carriedPaths = HashSet<String>()                    // (the High Elf's files are the Void Elf's: carried once)
        val looksMean = HashMap<String, DoubleArray?>()         // the looks' own picture of a skin: its mean colour (the picture itself is not kept)
        fun meanOf(path: String): DoubleArray? = if (path in looksMean) looksMean[path] else own(path)?.let { mean(it) }.also { looksMean[path] = it }
        for ((key, from) in plan) {
            val sources = byModel.getValue(from)
            // (skins the looks added from a picture of today's game, listed with no file name: their own picture is never replaced or carried over)
            val known = (direct + ownPicture).filter { (it.race to it.sex) == key }.map { it.index }.toSet()
            val withLooks = sources.mapNotNull { src -> meanOf(src.path)?.let { src to it } }
            if (withLooks.isEmpty()) continue
            val rows = dbc.rows.filter { it[1] == key.first && it[2] == key.second && it[3] == 0 && it[8] == 0 && (it[4] as String).isNotEmpty() &&
                !(it[4] as String).contains("Undead", ignoreCase = true) && (it[9] as Int) !in known }
            for (row in rows.distinctBy { it[4] as String }) {
                val path = row[4] as String
                if (key != from && !carriedPaths.add(path)) continue
                val target = meanOf(path) ?: continue
                val (src, _) = withLooks.minByOrNull { distance(it.second, target) } ?: continue
                val named = Named(key.first, key.second, row[9] as Int, path, src.retail)
                carriedFrom.add(named to src)
                if (key != from) fromDonor.add(named)
            }
        }
        val sourceOf = HashMap<Named, Named>()
        for ((n, src) in carriedFrom) sourceOf[n] = src
        val tonedFaces = HashSet<String>()                      // face textures matched to their skin's new body (each once: the first skin naming it)
        val named = direct + carriedFrom.map { it.first }
        val changed = JSONArray()
        val added = JSONArray()
        var done = 0
        var faces = 0
        for ((at, skin) in named.withIndex()) {
            say("Putting in Ralia's skins: ${at + 1} of ${named.size}", at.toFloat() / named.size)
            // the body: the set's left half as the 512 x 512 skin 3.3.5 composes from, over the looks' own (kept beside it)
            val target = File(patch, skin.path.replace('\\', '/'))
            // (the looks' own picture of this skin is read before the set's goes over it)
            val looksOwn = if (target.isFile) own(skin.path) else null
            val src = sourceOf[skin]
            val body = if (!target.isFile) null else if (src == null) raliaHeld(skin.retail) else {
                val set = raliaHeld(src.retail)
                val from = ownHeld(src.path)
                if (set != null && from != null && looksOwn != null) carried(set, from, looksOwn) else null
            }
            if (body != null) {
                over(target, Blp.writePalette(body))
                // The head is not in the skin: 3.3.5 lays the face row's texture over the skin's face region, and the looks' face
                // textures were made for the looks' own body. Where the set's body is another tone by the neck than the looks' own,
                // this colour's face textures take the same change (the user: "skin tones aren't lining up").
                val gain = looksOwn?.let { gain(neck(body), neck(it)) }
                // (both of a face row's textures: the lower face, which meets the neck, and the upper one, which meets the lower)
                if (gain != null && off(gain)) for (row in dbc.rows) {
                    if (row[1] != skin.race || row[2] != skin.sex || row[3] != FACE || row[9] != skin.index) continue
                    for (column in 4..5) {
                        val path = row[column] as String
                        if (path.isEmpty() || !tonedFaces.add(path.lowercase())) continue
                        val face = File(patch, path.replace('\\', '/')).takeIf { it.isFile } ?: continue
                        val picture = runCatching { Blp.read((File(face.path + ".orig").takeIf { it.isFile } ?: face).readBytes()) }.getOrNull() ?: continue
                        over(face, Blp.writePalette(toned(picture, gain), alpha = translucent(picture)))
                        faces++
                    }
                }
            }
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
        val allied = JSONArray()
        for (n in fromDonor) allied.put(JSONArray(listOf(n.race, n.sex, n.index)))
        rowsFile.writeText(JSONObject().put("skins", done).put("faces", faces).put("rows", changed).put("added", added).put("allied", allied).toString())
        write(table, dbc.write())
        stamp.writeText("$want\n")
        return done
    }

    /** How many face textures the set's skins had matched to them at the last [apply] (0: none needed it, or nothing is in). */
    fun faces(client: File): Int = File(client, "Data/${WrathppLooks.PATCH}/$ROWS").takeIf { it.isFile }
        ?.let { runCatching { JSONObject(it.readText()).optInt("faces") }.getOrNull() } ?: 0

    /**
     * A body picture's tone by the neck: the mean colour of the top rows of its right half (the upper torso's top edge in the body
     * layout every model of the looks has: the converted models' neck seams lie in its first 8 rows of 512, read off their vertices).
     */
    internal fun neck(image: Blp.Image): DoubleArray {
        val sum = DoubleArray(3)
        val rows = maxOf(1, image.height / 32)
        var n = 0
        for (y in 0 until rows) for (x in image.width / 2 until image.width) {
            val at = (y * image.width + x) * 4
            for (c in 0 until 3) sum[c] += (image.rgba[at + c].toInt() and 255).toDouble()
            n++
        }
        return DoubleArray(3) { sum[it] / maxOf(1, n) }
    }

    /** What takes the tone [from] to the tone [to], channel by channel (as [carried] does a pixel), within a half and twice. */
    internal fun gain(to: DoubleArray, from: DoubleArray) = DoubleArray(3) { ((to[it] + 8.0) / (from[it] + 8.0)).coerceIn(0.5, 2.0) }

    /** Whether a change of tone is one to make (4% in a channel; less is the palette's own noise). */
    internal fun off(gain: DoubleArray) = gain.any { Math.abs(it - 1.0) >= 0.04 }

    /** Whether a picture has any pixel not wholly opaque (a face texture's alpha is kept when it has one). */
    private fun translucent(image: Blp.Image): Boolean { for (i in 0 until image.width * image.height) if ((image.rgba[i * 4 + 3].toInt() and 255) != 255) return true; return false }

    /** [image] with each colour channel times its [gain]; the alpha as it was. */
    internal fun toned(image: Blp.Image, gain: DoubleArray): Blp.Image {
        val out = image.rgba.copyOf()
        for (i in 0 until image.width * image.height) for (c in 0 until 3) {
            val k = i * 4 + c
            out[k] = ((image.rgba[k].toInt() and 255) * gain[c] + 0.5).toInt().coerceIn(0, 255).toByte()
        }
        return Blp.Image(image.width, image.height, out)
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
