package com.logie.blizz.wrathpp

import com.logie.blizz.wowclient.Mpq
import org.json.JSONObject
import java.io.File
import java.io.IOException
import java.io.InputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.security.MessageDigest
import java.util.zip.ZipInputStream

/**
 * Body options on Wrath++ (the user: "The 4 body options and all of it ... push to the game and also make them in game
 * options on the Body tab in the creation screen"): each woman's Shape, Style and Density, chosen on the creator's Body
 * tab and kept per character by the realm, from a package of yours (`wrathpp-body.zip`, made by
 * `realm/warcraft/wrathpp/tools/body_shapes/pack2.py`), never in the app or the repository.
 *
 * What the package has, per race of the looks ([WrathppLooks], `Data/patch-Z.MPQ`):
 *  - the race's own model with the body layer (a patch of the looks' model: its header and what follows it, checked by
 *    the SHA-256 of the looks' model it was made from and of the model it makes, [withPatch]) and its skin;
 *  - where the race has them, the body shapes' models (Petite, Curvy, Voluptuous), each its own model beside the race's
 *    (`HumanFemaleWpp1.m2` ...), with the race's animation files under its name;
 *  - the layer's designs, a texture each style and density (`WppLayer_<style>_<density>.blp` in each race's folder, the
 *    sixteenth style the race's faction's own) and an empty one (`WppLayer_0.blp`).
 * [apply] puts them in, and the display rows that pick them ([displayId]: a model and a design per Shape, Style and
 * Density) into the game's tables (`DBFilesClient/CreatureDisplayInfo.dbc` and `CreatureModelData.dbc` in the looks'
 * patch, made from the game's own) and the realm's (`share/dbc/CreatureDisplayInfo.dbc`), whose module gives each woman
 * her display at login (wrathpp_appearance.h's BodyDisplay: the same numbering). The race's own display gets the empty
 * design, so a woman without a style shows no layer. Without the package nothing of this is in, and the realm, finding
 * no such displays, leaves every woman as drawn.
 *
 * The layer itself is shown by the native mod (Wrath++ native 0.5.0) on a character with nothing on the legs. NOT run on
 * a phone; unit-tested.
 */
object WrathppBody {
    const val DIR = "wrathpp-body"
    const val STAMP = "wrathpp-body.stamp"
    const val LIST = "wrathpp-body.json"
    private const val SOURCE = "source"
    private const val ORIG = ".body-orig"
    private const val MADE = "wrathpp-body.files"
    private const val HEADER = 0x138
    val NAMES = arrayOf("wrathpp-body.zip", "body.zip")

    /** The realm's numbering (wrathpp_appearance.h): race slots, 4 shapes, 65 layers (none, 16 styles x 4 densities). */
    const val DISPLAY_BASE = 42000
    const val MODEL_BASE = 4200
    val RACES = intArrayOf(1, 2, 3, 4, 5, 6, 7, 8, 10, 11)
    const val SHAPES = 4
    const val STYLES = 16
    const val DENSITIES = 4
    private const val LAYERS = 1 + STYLES * DENSITIES
    const val EMPTY = "WppLayer_0"

    fun displayId(slot: Int, shape: Int, layer: Int) = DISPLAY_BASE + slot * 260 + shape * LAYERS + layer
    fun modelId(slot: Int, shape: Int) = MODEL_BASE + slot * SHAPES + shape
    fun design(style: Int, density: Int) = "WppLayer_${style}_$density"

    fun store(context: android.content.Context): File = File(context.applicationContext.filesDir, DIR)
    fun sha(store: File): String? = File(store, STAMP).takeIf { it.isFile }?.readText()?.trim()?.takeIf { it.isNotEmpty() }
    fun installed(store: File): Boolean = sha(store) != null && File(store, "files/$LIST").isFile

    /** The package's list, or null when nothing is imported. */
    fun list(store: File): JSONObject? = File(store, "files/$LIST").takeIf { it.isFile }?.let { runCatching { JSONObject(it.readText()) }.getOrNull() }

    fun races(store: File): List<String> {
        val a = list(store)?.optJSONArray("races") ?: return emptyList()
        return (0 until a.length()).map { a.getJSONObject(it).optString("race") }
    }

    /** Taken off the phone, and not looked for again ([lookFor]) until a package is picked or used by hand. */
    fun remove(store: File) {
        store.deleteRecursively()
        off(store).apply { parentFile?.mkdirs() }.writeText("removed\n")
    }

    private fun off(store: File) = File(store.path + ".off")

    /**
     * The package looked for by its name ([NAMES], where downloads are: [ImportFinder]) taken in by itself when nothing is
     * imported, and again when that file has changed since. Never after [remove]. Returns how many models it has, or null.
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
     * Takes the package in ([store]/files, as the zip has it), in place of what was there; returns how many models it has.
     * A zip without the list, of another kind or format, with a path leaving it, or whose files don't match the list is
     * refused and [store] left as it was.
     */
    fun importZip(store: File, zip: InputStream): Int {
        val fresh = File(store.path + ".new").apply { deleteRecursively() }
        val files = File(fresh, "files").apply { mkdirs() }
        val digest = MessageDigest.getInstance("SHA-256")
        try {
            val counted = java.security.DigestInputStream(zip, digest)
            ZipInputStream(counted).use { z ->
                while (true) {
                    val entry = z.nextEntry ?: break
                    if (entry.isDirectory) continue
                    val name = entry.name.replace('\\', '/')
                    if (name.startsWith("/") || name.split('/').any { it == ".." || it.isEmpty() }) throw IOException("Bad path in the zip: ${entry.name}")
                    val out = File(files, name)
                    out.parentFile?.mkdirs()
                    out.outputStream().use { z.copyTo(it) }
                }
                val rest = ByteArray(1 shl 14)
                while (counted.read(rest) >= 0) { /* the digest is of the whole file */ }
            }
            val listFile = File(files, LIST)
            if (!listFile.isFile) throw IOException("This zip has no body options in it (no $LIST).")
            val list = JSONObject(listFile.readText())
            if (list.optString("kind") != "wrathpp-body") throw IOException("This zip isn't a Wrath++ body options package.")
            if (list.optInt("format") != 2) throw IOException("This is an older body options package: make it again (pack2.py).")
            val models = list.optJSONArray("models") ?: throw IOException("The package names no models.")
            if (models.length() == 0) throw IOException("The package names no models.")
            fun check(entry: JSONObject, what: String) {
                val f = File(files, entry.getString("file"))
                if (!f.isFile || f.length() != entry.getLong("size") || sha256(f.readBytes()) != entry.getString("sha256")) throw IOException("$what is missing or damaged.")
            }
            for (i in 0 until models.length()) {
                val m = models.getJSONObject(i)
                val what = "${m.optString("race")} ${list.getJSONArray("shapes").optString(m.getInt("shape"))}"
                check(m.getJSONObject("patch"), what)
                check(m.getJSONObject("skin_file"), "$what's skin")
            }
            val textures = list.getJSONArray("textures")
            for (i in 0 until textures.length()) check(textures.getJSONObject(i), "A design")
            File(fresh, STAMP).writeText(digest.digest().joinToString("") { "%02x".format(it) } + "\n")
            store.deleteRecursively()
            if (!fresh.renameTo(store)) throw IOException("The body options couldn't be put in place.")
            off(store).delete()
            return models.length()
        } finally {
            fresh.deleteRecursively()
        }
    }

    /**
     * The package put into Wrath++'s looks in [client] and the realm's tables in [server] ([data]: the game's own tables the
     * realm reads where its package has none), or taken out again when nothing is imported. Returns what was done, a line
     * for the start report.
     */
    fun apply(store: File, client: File, server: File, data: File, say: (String, Float?) -> Unit = { _, _ -> }): String {
        val patch = File(client, "Data/${WrathppLooks.PATCH}")
        if (!patch.isDirectory) return "no looks"
        val looks = File(patch, WrathppLooks.MARKER).takeIf { it.isFile }?.readText()?.trim().orEmpty()
        val zipSha = if (installed(store)) sha(store) else null
        val serverDbc = File(server, "share/dbc")
        val stamps = listOf(File(patch, STAMP), File(serverDbc, STAMP))
        // what the game's tables are made from: a Reforged part or a realm patch put in or out changes them
        val want = "$zipSha $looks" + if (zipSha != null) " " + tableSources(File(client, "Data")) else ""
        if (stamps.all { it.isFile && it.readLines().firstOrNull()?.trim() == want }) {
            return stamps[0].readLines().drop(1).joinToString("; ").ifEmpty { "as before" }
        }
        takeOut(patch, serverDbc)
        stamps.forEach { it.delete() }
        if (zipSha == null) return "none imported"
        val list = list(store) ?: return "none imported"
        val files = File(store, "files")
        val made = ArrayList<File>()
        val done = ArrayList<String>()
        // the models: the race's own with the layer in place of the looks', the shapes' beside it
        val models = list.getJSONArray("models")
        val shapesOf = HashMap<String, MutableSet<Int>>()
        for (i in 0 until models.length()) {
            val m = models.getJSONObject(i)
            val race = m.getString("race")
            val shape = m.getInt("shape")
            say("Putting in the body options: $race", i.toFloat() / models.length())
            val looksModel = File(patch, if (shape == 0) m.getString("model") else m.getString("anims_of") + ".m2")
            if (!looksModel.isFile) { done.add("$race: not in the looks"); continue }
            if (shape != 0 && 0 !in shapesOf[race].orEmpty()) continue
            val base = if (shape == 0) looksModel.readBytes() else File(looksModel.path + ORIG).takeIf { it.isFile }?.readBytes() ?: looksModel.readBytes()
            if (sha256(base) != m.getString("looks_sha256")) { if (shape == 0) done.add("$race: made for other looks, left as drawn"); continue }
            val out = withPatch(base, File(files, m.getJSONObject("patch").getString("file")).readBytes())
            if (sha256(out) != m.getString("made_sha256")) throw IOException("$race: the package's model doesn't make what it says")
            val skin = File(files, m.getJSONObject("skin_file").getString("file")).readBytes()
            val model = File(patch, m.getString("model"))
            val skinFile = File(patch, m.getString("skin"))
            if (shape == 0) {
                over(model, out); over(skinFile, skin)
            } else {
                write(model, out, made); write(skinFile, skin, made)
                // the race's animation files under the shape's name (the game finds them by the model's name)
                val prefix = File(m.getString("anims_of")).name
                val own = File(m.getString("model")).nameWithoutExtension
                looksModel.parentFile?.listFiles()?.filter { it.name.startsWith(prefix) && it.name.endsWith(".anim") && it.name.substring(prefix.length).matches(Regex("\\d{4}-\\d{2}\\.anim")) }?.forEach { anim ->
                    link(anim, File(anim.parentFile, own + anim.name.substring(prefix.length)), made)
                }
            }
            shapesOf.getOrPut(race) { HashSet() }.add(shape)
        }
        // the designs in each race's folder: the package's own files, linked where the storage allows
        val textures = list.getJSONArray("textures")
        val byDesign = HashMap<Pair<String, Int>, File>()
        for (i in 0 until textures.length()) {
            val t = textures.getJSONObject(i)
            byDesign[t.optString("design") to t.optInt("density")] = File(files, t.getString("file"))
        }
        val raceList = list.getJSONArray("races")
        val styles = list.getJSONObject("styles")
        for (i in 0 until raceList.length()) {
            val r = raceList.getJSONObject(i)
            if (0 !in shapesOf[r.getString("race")].orEmpty()) continue
            val folder = File(patch, r.getString("folder"))
            val names = styles.getJSONArray(r.getString("faction"))
            byDesign["" to 0]?.let { link(it, File(folder, "$EMPTY.blp"), made) }
            for (s in 1..minOf(STYLES, names.length())) for (d in 1..DENSITIES) {
                byDesign[names.getString(s - 1) to d]?.let { link(it, File(folder, design(s, d) + ".blp"), made) }
            }
        }
        // the display rows: the game's tables made from its own (what the game reads without this patch), the realm's
        val game = Mpq.Game(File(client, "Data"), listOf(WrathppLooks.PATCH.lowercase()))
        val withRows = try {
            val chr = game.read("DBFilesClient\\ChrRaces.dbc") ?: throw IOException("The game has no ChrRaces.dbc")
            val displays = game.read("DBFilesClient\\CreatureDisplayInfo.dbc")?.let { WrathppUndead.Dbc.read(it, DISPLAY_KINDS) } ?: throw IOException("The game has no CreatureDisplayInfo.dbc")
            val modelData = game.read("DBFilesClient\\CreatureModelData.dbc")?.let { WrathppUndead.Dbc.read(it, MODEL_KINDS) } ?: throw IOException("The game has no CreatureModelData.dbc")
            val female = femaleDisplays(chr)
            val races = ArrayList<RaceRows>()
            for (i in 0 until raceList.length()) {
                val r = raceList.getJSONObject(i)
                val have = shapesOf[r.getString("race")].orEmpty()
                if (0 !in have) continue
                val slot = RACES.indexOf(r.getInt("race_id")).takeIf { it >= 0 } ?: continue
                val own = female[r.getInt("race_id")] ?: continue
                races += RaceRows(slot, own, r.getString("folder"), have)
            }
            addRows(displays, modelData, races, game = true)
            write(File(patch, "DBFilesClient/CreatureDisplayInfo.dbc"), displays.write(), made)
            write(File(patch, "DBFilesClient/CreatureModelData.dbc"), modelData.write(), made)
            // the realm's: its package's table, else the game's own it reads
            val serverTable = File(serverDbc, "CreatureDisplayInfo.dbc")
            val serverBase = serverTable.takeIf { it.isFile } ?: File(data, "dbc/CreatureDisplayInfo.dbc")
            if (serverBase.isFile) {
                val table = WrathppUndead.Dbc.read(serverBase.readBytes(), DISPLAY_KINDS)
                table.rows.removeAll { (it[0] as Int) in DISPLAY_BASE until DISPLAY_BASE + RACES.size * 260 }
                addRows(table, null, races, game = false)
                if (serverTable.isFile) over(serverTable, table.write()) else write(serverTable, table.write(), made)
            } else done.add("the realm's table not found: the realm leaves every woman as drawn")
            races.size
        } finally {
            game.close()
        }
        File(patch, MADE).writeText(made.joinToString("\n") { it.path } + "\n")
        val summary = shapesOf.entries.sortedBy { it.key }.joinToString(", ") { (race, s) -> if (s.size > 1) "$race (${s.size - 1} shapes)" else race }
        done.add(0, "$summary; $withRows races' displays")
        stamps.forEach { it.parentFile?.mkdirs(); it.writeText("$want\n" + done.joinToString("\n") + "\n") }
        return done.joinToString("; ")
    }

    // CreatureDisplayInfo: ID, ModelID, SoundID, ExtendedDisplayInfoID, CreatureModelScale, CreatureModelAlpha,
    // TextureVariation 1-3, PortraitTextureName, BloodLevel, BloodID, NPCSoundID, ParticleColorID, CreatureGeosetData,
    // ObjectEffectPackageID. CreatureModelData: ID, Flags, ModelName, and 25 numbers.
    internal const val DISPLAY_KINDS = "iiiiiissssiiiiii"
    internal val MODEL_KINDS = "iis" + "i".repeat(25)

    private class RaceRows(val slot: Int, val ownDisplay: Int, val folder: String, val shapes: Set<Int>)

    /**
     * [displays] (and [models], the game's) with each race's body option displays: for each shape, its model (its own
     * where the package has it, else the race's) and for each layer its design ([EMPTY] for none); the race's own display
     * with the empty design. The realm's ([game] false) need only be there, with the race's model.
     */
    private fun addRows(displays: WrathppUndead.Dbc, models: WrathppUndead.Dbc?, races: List<RaceRows>, game: Boolean) {
        val byId = displays.rows.associateBy { it[0] as Int }
        val modelById = models?.rows?.associateBy { it[0] as Int }
        for (r in races) {
            val own = byId[r.ownDisplay] ?: continue
            val ownModel = own[1] as Int
            if (game) own[6] = EMPTY
            for (shape in 0 until SHAPES) {
                var model = ownModel
                if (game && shape in r.shapes && shape > 0) {
                    val base = modelById?.get(ownModel) ?: continue
                    val row = base.copyOf()
                    row[0] = modelId(r.slot, shape)
                    row[2] = r.folder.replace('/', '\\') + "\\" + File(r.folder).parentFile!!.name + "Female" + "Wpp$shape.mdx"
                    models.rows.removeAll { it[0] == row[0] }
                    models.rows.add(row)
                    model = row[0] as Int
                }
                for (layer in 0 until LAYERS) {
                    val row = own.copyOf()
                    row[0] = displayId(r.slot, shape, layer)
                    row[1] = model
                    if (game) row[6] = if (layer == 0) EMPTY else design((layer - 1) / DENSITIES + 1, (layer - 1) % DENSITIES + 1)
                    displays.rows.removeAll { it[0] == row[0] }
                    displays.rows.add(row)
                }
            }
        }
    }

    private val TABLES = listOf("chrraces.dbc", "creaturedisplayinfo.dbc", "creaturemodeldata.dbc")

    /** The app's own patches that hold none of the game's tables and are written often: the creator's, its art, the glue mask. */
    private val NOT_TABLES = setOf("patch-x.mpq", "patch-s.mpq", "patch-t.mpq")

    /**
     * What the game's tables this changes are made from, without the looks' patch: the game's archives (each one's name,
     * size and time; a folder's, its own tables'), so that the copy is made again when one is put in, out or changed (a
     * Reforged part, the realm modules' patch). Without opening an archive: this runs at every Play.
     */
    internal fun tableSources(data: File): String {
        val out = ArrayList<String>()
        fun add(folder: File, prefix: String) {
            for (f in folder.listFiles().orEmpty().sortedBy { it.name.lowercase() }) {
                val name = f.name.lowercase()
                if (!name.endsWith(".mpq") || name == WrathppLooks.PATCH.lowercase() || name in NOT_TABLES) continue
                if (f.isDirectory) {
                    File(f, "DBFilesClient").listFiles().orEmpty().filter { it.name.lowercase() in TABLES }.sortedBy { it.name.lowercase() }
                        .forEach { out += "$prefix${f.name}/${it.name}:${it.length()}:${it.lastModified()}" }
                } else out += "$prefix${f.name}:${f.length()}:${f.lastModified()}"
            }
        }
        add(data, "")
        data.listFiles().orEmpty().filter { it.isDirectory && it.name.length == 4 && !it.name.endsWith(".MPQ", ignoreCase = true) }.forEach { add(it, it.name + "/") }
        return sha256(out.joinToString("\n").toByteArray()).take(16)
    }

    /** ChrRaces: each race's female display (its sixth column), from the table as the game has it. */
    internal fun femaleDisplays(table: ByteArray): Map<Int, Int> {
        if (table.size < 20 || String(table, 0, 4, Charsets.US_ASCII) != "WDBC") throw IOException("ChrRaces.dbc isn't one of the game's tables")
        val b = ByteBuffer.wrap(table).order(ByteOrder.LITTLE_ENDIAN)
        val count = b.getInt(4); val fields = b.getInt(8); val size = b.getInt(12)
        if (fields < 6 || size < 24) throw IOException("ChrRaces.dbc has too few columns")
        return (0 until count).associate { b.getInt(20 + it * size) to b.getInt(20 + it * size + 5 * 4) }
    }

    /**
     * The model a package's [patch] makes of the looks' [base]: the patch's header (the first 0x138 bytes) in place of the
     * base's, the rest of the base as it was, and what the patch has after its header at the base's end (16-byte aligned).
     */
    internal fun withPatch(base: ByteArray, patch: ByteArray): ByteArray {
        require(base.size >= HEADER && patch.size >= HEADER && String(base, 0, 4, Charsets.ISO_8859_1) == "MD20" && String(patch, 0, 4, Charsets.ISO_8859_1) == "MD20") { "not a 3.3.5 model" }
        val at = (base.size + 15) / 16 * 16
        val out = ByteArray(at + patch.size - HEADER)
        System.arraycopy(base, 0, out, 0, base.size)
        System.arraycopy(patch, 0, out, 0, HEADER)
        System.arraycopy(patch, HEADER, out, at, patch.size - HEADER)
        return out
    }

    /** What an earlier [apply] put in, out again: the looks' own models and skins, the realm's table without the rows. */
    private fun takeOut(patch: File, serverDbc: File) {
        patch.walkTopDown().filter { it.isFile && it.name.endsWith(ORIG) }.toList().forEach { orig ->
            val target = File(orig.path.removeSuffix(ORIG))
            target.delete()
            if (!orig.renameTo(target)) throw IOException("${target.path} couldn't be put back")
        }
        File(patch, MADE).takeIf { it.isFile }?.readLines()?.filter { it.isNotBlank() }?.forEach { File(it).delete() }
        File(patch, MADE).delete()
        val serverTable = File(serverDbc, "CreatureDisplayInfo.dbc")
        if (serverTable.isFile && File(serverDbc, STAMP).isFile) {
            val table = WrathppUndead.Dbc.read(serverTable.readBytes(), DISPLAY_KINDS)
            if (table.rows.removeAll { (it[0] as Int) in DISPLAY_BASE until DISPLAY_BASE + RACES.size * 260 }) over(serverTable, table.write(), keep = false)
        }
    }

    /** [bytes] over the looks' [target], whose own is kept beside it ([ORIG]) to put back. */
    private fun over(target: File, bytes: ByteArray, keep: Boolean = true) {
        val orig = File(target.path + ORIG)
        if (keep && !orig.isFile && target.isFile) target.copyTo(orig)
        val tmp = File(target.path + ".tmp")
        tmp.writeBytes(bytes)
        if (!tmp.renameTo(target)) { target.delete(); if (!tmp.renameTo(target)) throw IOException("${target.path} couldn't be written") }
    }

    /** A file of this one's own ([made]: taken out again by [takeOut]). */
    private fun write(target: File, bytes: ByteArray, made: MutableList<File>) {
        target.parentFile?.mkdirs()
        over(target, bytes, keep = false)
        made += target
    }

    /** [from] at [to] as a hard link where the storage has them, a copy otherwise. */
    private fun link(from: File, to: File, made: MutableList<File>) {
        to.parentFile?.mkdirs()
        to.delete()
        val linked = runCatching { java.nio.file.Files.createLink(to.toPath(), from.toPath()); true }.getOrDefault(false)
        if (!linked) from.copyTo(to, overwrite = true)
        made += to
    }

    private fun sha256(bytes: ByteArray): String = MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }
}
