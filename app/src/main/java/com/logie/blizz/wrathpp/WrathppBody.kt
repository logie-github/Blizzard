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
    private const val TABLES_VERSION = 3
    const val LIST = "wrathpp-body.json"
    private const val SOURCE = "source"
    private const val ORIG = ".body-orig"
    private const val MADE = "wrathpp-body.files"
    private const val HEADER = 0x138
    val NAMES = arrayOf("wrathpp-body.zip", "body.zip")

    /**
     * The realm's numbering (wrathpp_appearance.h): race slots, 4 shapes, 65 layers (none, 16 styles x 4 densities). Every
     * race's women (18 November 2026): the ten of 3.3.5 in their slots of before, then the Goblin, the Worgen and the allied
     * races by their Wrath++ ids (22, the High Elf, is drawn with the Void Elf's files: the package's `files`). The base
     * was 42000 until then, whose eighth slot (the Troll's, 43820 to 44079) ran into the model variants' displays (44000:
     * WrathppVariants); [LEGACY] is what an earlier build's rows are taken out by.
     */
    const val DISPLAY_BASE = 45000
    const val MODEL_BASE = 4200
    val RACES = intArrayOf(1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 9, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23)
    private val LEGACY = listOf(42000 until 44000, 44096 until 44600)
    private fun ours(display: Int) = display in DISPLAY_BASE until DISPLAY_BASE + RACES.size * 260 || LEGACY.any { display in it }
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
    /** A package of this format is in (an older one, the held menu's body shapes of before, counts as none: [older]). */
    fun installed(store: File): Boolean = sha(store) != null && list(store)?.optInt("format") == 2

    /** An older package (format 1: one preset for every woman) is what the phone has. */
    fun older(store: File): Boolean = sha(store) != null && list(store)?.let { it.optInt("format") != 2 } == true

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
        // (TABLES_VERSION: the way the tables are made; raised when it changed, so that phones that made them the old way make them again:
        // 2 = the looks' own CreatureDisplayInfo and CreatureModelData rows kept, which the allied races' displays need)
        val want = "$zipSha $looks" + if (zipSha != null) " " + tableSources(File(client, "Data")) + " tables$TABLES_VERSION" else ""
        if (stamps.all { it.isFile && it.readLines().firstOrNull()?.trim() == want }) {
            return stamps[0].readLines().drop(1).joinToString("; ").ifEmpty { "as before" }
        }
        takeOut(patch, serverDbc)
        stamps.forEach { it.delete() }
        if (zipSha == null) return if (older(store)) "an older package (one shape for every woman): put the new one in (Settings, Wrath++, Body options)" else "none imported"
        val list = list(store) ?: return "none imported"
        val files = File(store, "files")
        val made = ArrayList<File>()
        val done = ArrayList<String>()
        // the models: the race's own with the layer in place of the looks', the shapes' beside it
        val models = list.getJSONArray("models")
        val shapesOf = HashMap<String, MutableSet<Int>>()
        val remade = HashMap<String, MutableList<Int>>()
        for (i in 0 until models.length()) {
            val m = models.getJSONObject(i)
            val race = m.getString("race")
            val shape = m.getInt("shape")
            say("Putting in the body options: $race", i.toFloat() / models.length())
            val looksModel = File(patch, if (shape == 0) m.getString("model") else m.getString("anims_of") + ".m2")
            if (!looksModel.isFile) { done.add("$race: not in the looks"); continue }
            if (shape != 0 && 0 !in shapesOf[race].orEmpty()) continue
            val base = if (shape == 0) looksModel.readBytes() else File(looksModel.path + ORIG).takeIf { it.isFile }?.readBytes() ?: looksModel.readBytes()
            // A package that names its looks' model by structure (everything but the vertices' positions) is for any looks of that
            // model whose vertices only moved: the hair pushed out of the head differs a little with each build of the looks. An
            // older package names the bytes.
            val byStructure = m.has("looks_struct_sha256")
            val rightLooks = if (byStructure) structSha256(base) == m.getString("looks_struct_sha256") else sha256(base) == m.getString("looks_sha256")
            val out: ByteArray
            val skin: ByteArray
            if (rightLooks) {
                out = withPatch(base, File(files, m.getJSONObject("patch").getString("file")).readBytes())
                val madeRight = if (byStructure) structSha256(out, base) == m.getString("made_struct_sha256") else sha256(out) == m.getString("made_sha256")
                if (!madeRight) throw IOException("$race: the package's model doesn't make what it says")
                skin = File(files, m.getJSONObject("skin_file").getString("file")).readBytes()
            } else {
                // Looks the package was not made for (a looks release changed her model): made here on the looks' own model
                // and skin ([WrathppBodyLayer]), so one import lasts; a shape's vertices carried onto the looks' own mesh.
                val looksSkin = File(patch, if (shape == 0) m.getString("skin") else m.getString("anims_of") + "00.skin")
                    .let { f -> File(f.path + ORIG).takeIf { shape != 0 && it.isFile } ?: f }
                val made = try {
                    if (!looksSkin.isFile) throw IOException("the looks have no skin for her")
                    onTheseLooks(list, files, m, base, looksSkin.readBytes())
                } catch (e: WrathppBodyLayer.NoRoom) {
                    if (shape == 0) done.add("$race: made for other looks, and these leave the layer no room (${e.free} indices free, ${e.needed} needed): left as drawn")
                    null
                } catch (e: IOException) {
                    if (shape == 0) done.add("$race: made for other looks, left as drawn (${e.message})")
                    null
                } ?: continue
                out = made.model
                skin = made.skin
                remade.getOrPut(race) { ArrayList() }.add(shape)
            }
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
            if (0 !in shapesOf[filesOf(r)].orEmpty()) continue
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
            // the looks' patch's own tables where it has them (the allied races' displays and models are in them: Wrath++'s own rows go
            // over those, not over the game's alone, which would take the allied races' out), else the game's
            val looksTable = { name: String -> File(patch, "DBFilesClient/$name").takeIf { it.isFile } }
            val displays = (looksTable("CreatureDisplayInfo.dbc")?.readBytes() ?: game.read("DBFilesClient\\CreatureDisplayInfo.dbc"))?.let { WrathppUndead.Dbc.read(it, DISPLAY_KINDS) } ?: throw IOException("The game has no CreatureDisplayInfo.dbc")
            val modelData = (looksTable("CreatureModelData.dbc")?.readBytes() ?: game.read("DBFilesClient\\CreatureModelData.dbc"))?.let { WrathppUndead.Dbc.read(it, MODEL_KINDS) } ?: throw IOException("The game has no CreatureModelData.dbc")
            val female = femaleDisplays(chr)
            val races = ArrayList<RaceRows>()
            for (i in 0 until raceList.length()) {
                val r = raceList.getJSONObject(i)
                val have = shapesOf[filesOf(r)].orEmpty()       // (a race drawn with another's files: that one's models, its own displays)
                if (0 !in have) continue
                val slot = RACES.indexOf(r.getInt("race_id")).takeIf { it >= 0 } ?: continue
                val own = female[r.getInt("race_id")] ?: continue
                races += RaceRows(slot, own, r.getString("folder"), have)
            }
            addRows(displays, modelData, races, game = true)
            // (a table the looks' patch has is theirs, this one's rows over it and theirs kept beside to put back; else this one's own)
            for ((name, bytes) in listOf("CreatureDisplayInfo.dbc" to displays.write(), "CreatureModelData.dbc" to modelData.write())) {
                val target = File(patch, "DBFilesClient/$name")
                if (target.isFile) over(target, bytes) else write(target, bytes, made)
            }
            // the realm's: its package's table, else the game's own it reads
            val serverTable = File(serverDbc, "CreatureDisplayInfo.dbc")
            val serverBase = serverTable.takeIf { it.isFile } ?: File(data, "dbc/CreatureDisplayInfo.dbc")
            if (serverBase.isFile) {
                val table = WrathppUndead.Dbc.read(serverBase.readBytes(), DISPLAY_KINDS)
                table.rows.removeAll { ours(it[0] as Int) }
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
        if (remade.isNotEmpty()) done.add(1, "made here for these looks (the package was made for others): " + remade.entries.sortedBy { it.key }
            .joinToString(", ") { (race, s) -> if (s.any { it != 0 }) "$race (its shapes on the looks' own mesh)" else race })
        stamps.forEach { it.parentFile?.mkdirs(); it.writeText("$want\n" + done.joinToString("\n") + "\n") }
        return done.joinToString("; ")
    }

    /** The race whose models and designs a race of the package's list is drawn with (its own, but for the High Elf: `files`). */
    private fun filesOf(race: JSONObject): String = race.optString("files").ifEmpty { race.getString("race") }

    /**
     * A model of the package made here on the looks' own [base] and [looksSkin], for looks the package's patch does not
     * fit: the layer by the package's numbers for the race (`races[].layer`: [WrathppBodyLayer.add]); for a body shape, its
     * vertices first carried from the package's models onto the looks' own ([WrathppBodyLayer.carried]: the package's two
     * vertex arrays, which its `base_size` and `looks_vertices` find in the patches). Throws when the package has not what
     * this needs (an older one), the shape is not for these looks' body, or the skin has no room.
     */
    private fun onTheseLooks(list: JSONObject, files: File, m: JSONObject, base: ByteArray, looksSkin: ByteArray): WrathppBodyLayer.Made {
        val race = m.getString("race")
        val races = list.getJSONArray("races")
        val entry = (0 until races.length()).map { races.getJSONObject(it) }.firstOrNull { it.optString("race") == race && !it.has("files") }
        val l = entry?.optJSONObject("layer") ?: throw IOException("the package doesn't say how her layer lies: a newer package is needed")
        val body = l.getJSONArray("body").let { a -> (0 until a.length()).map { a.getInt(it) }.toSet() }
        val block = l.optJSONArray("hair_block")
        val params = WrathppBodyLayer.Params(l.getDouble("k"), l.getDouble("fold"), body, intArrayOf(block?.optInt(0) ?: 0, block?.optInt(1) ?: 0),
            l.optInt("texture", 6), l.optDouble("x", 0.0))
        var vertices: ByteArray? = null
        if (m.getInt("shape") != 0) {
            val models = list.getJSONArray("models")
            val zero = (0 until models.length()).map { models.getJSONObject(it) }.firstOrNull { it.optString("race") == race && it.optInt("shape") == 0 }
            if (zero == null || !zero.has("base_size") || !m.has("base_size")) throw IOException("the package's shapes can't be carried: a newer package is needed")
            val was = patchVertices(File(files, zero.getJSONObject("patch").getString("file")).readBytes(), zero.getInt("base_size"), zero.getInt("looks_vertices"))
            val shape = patchVertices(File(files, m.getJSONObject("patch").getString("file")).readBytes(), m.getInt("base_size"), m.getInt("looks_vertices"))
            vertices = WrathppBodyLayer.carried(WrathppBodyLayer.verticesOf(base), was, shape) ?: throw IOException("the shape is for another body")
        }
        return WrathppBodyLayer.add(base, looksSkin, vertices, params, entry.getString("folder").replace('/', '\\'))
    }

    /** The first [count] vertex records of the model a [patch] makes of a base of [baseSize] bytes: read out of the patch itself. */
    internal fun patchVertices(patch: ByteArray, baseSize: Int, count: Int): ByteArray {
        if (patch.size < HEADER) throw IOException("the package's patch is too short")
        val head = ByteBuffer.wrap(patch).order(ByteOrder.LITTLE_ENDIAN)
        val n = head.getInt(60)
        val at = head.getInt(64).toLong() - (baseSize + 15) / 16 * 16 + HEADER
        if (count <= 0 || count > n || at < HEADER || at + count.toLong() * 48 > patch.size) throw IOException("the package's patch doesn't hold its vertices")
        return patch.copyOfRange(at.toInt(), at.toInt() + count * 48)
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
            if (table.rows.removeAll { ours(it[0] as Int) }) over(serverTable, table.write(), keep = false)
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

    /**
     * The SHA-256 of a model without where its vertices are (the first 12 bytes of each of the 48 a vertex has: the array's count
     * and place are in the header at 60 and 64). A model whose header doesn't say a vertex array that lies inside the file is
     * taken whole. For a model a patch made of the looks' [base], the array of the base's header is left out too: the made model
     * keeps the base's old array where it was (the patch's header names the new one, after the end), and it holds the looks' own
     * positions.
     */
    internal fun structSha256(bytes: ByteArray, base: ByteArray? = null): String {
        val arrays = ArrayList<Pair<Int, Int>>()
        arrays.addAll(listOfNotNull(vertexArray(bytes, bytes)))
        if (base != null) arrays.addAll(listOfNotNull(vertexArray(base, bytes)))
        if (arrays.isEmpty()) return sha256(bytes)
        val masked = bytes.copyOf()
        for ((count, at) in arrays) for (i in 0 until count) java.util.Arrays.fill(masked, at + i * 48, at + i * 48 + 12, 0.toByte())
        return sha256(masked)
    }

    /** (count, offset) of the vertex array [header]'s model names, if it lies inside [file]. */
    private fun vertexArray(header: ByteArray, file: ByteArray): Pair<Int, Int>? {
        if (header.size < 68) return null
        val head = ByteBuffer.wrap(header).order(ByteOrder.LITTLE_ENDIAN)
        val count = head.getInt(60).toLong() and 0xFFFFFFFFL
        val at = head.getInt(64).toLong() and 0xFFFFFFFFL
        if (count == 0L || at < 68 || at + count * 48 > file.size) return null
        return count.toInt() to at.toInt()
    }

    private fun sha256(bytes: ByteArray): String = MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }
}
