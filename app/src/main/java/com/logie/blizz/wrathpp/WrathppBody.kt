package com.logie.blizz.wrathpp

import org.json.JSONObject
import java.io.File
import java.io.IOException
import java.io.InputStream
import java.security.MessageDigest
import java.util.zip.ZipInputStream

/**
 * Body shapes on Wrath++ (the user: "give me a zip that I can import as a body mod so that it doesn't have to ship on the
 * app or hosted on GitHub"): body presets for the women's models, from a zip of yours (`wrathpp-body.zip`), never in the
 * app or the repository. One preset is worn by every woman of the races the zip has, in place of the looks' own shape
 * ([WrathppLooks], `Data/patch-Z.MPQ`): 3.3.5 draws every character of a race and sex with one model, so a choice per
 * character needs the client's own help (not built).
 *
 * The zip (made by `realm/warcraft/wrathpp/tools/body_shapes.py`) has `wrathpp-body.json` and, per model:
 *  - the skin (`HumanFemale00.skin`): the looks' own triangles with those of the chest and seat split finer (paid for by
 *    the worn gear's pieces and a little of the hair, so it stays within 3.3.5's 65535 indices);
 *  - one block of vertices per preset (48 bytes each, 3.3.5's model vertex), the looks' own vertices first and the
 *    added ones after, each preset's shape in their places.
 * [apply] puts the chosen preset's block at the end of the looks' own model (its header pointed at it) and the skin over
 * the looks' own, both kept beside them (`.body-orig`) to put back; only on the very model the zip was made from (its
 * SHA-256 in the list): a model of other looks is left as it is, and said. Applied again when the looks, the zip or the
 * choice change; As drawn, or taken out, puts the looks' own back. NOT run on a phone; unit-tested.
 */
object WrathppBody {
    const val DIR = "wrathpp-body"
    const val STAMP = "wrathpp-body.stamp"
    const val LIST = "wrathpp-body.json"
    const val AS_DRAWN = "As drawn"
    private const val CHOICE = "choice"
    private const val SOURCE = "source"
    private const val ORIG = ".body-orig"
    private const val VERTEX = 48
    val NAMES = arrayOf("wrathpp-body.zip", "body.zip")

    fun store(context: android.content.Context): File = File(context.applicationContext.filesDir, DIR)
    fun sha(store: File): String? = File(store, STAMP).takeIf { it.isFile }?.readText()?.trim()?.takeIf { it.isNotEmpty() }
    fun installed(store: File): Boolean = sha(store) != null && File(store, "files/$LIST").isFile

    /** The zip's list, or null when nothing is imported. */
    fun list(store: File): JSONObject? = File(store, "files/$LIST").takeIf { it.isFile }?.let { runCatching { JSONObject(it.readText()) }.getOrNull() }

    fun presets(store: File): List<String> {
        val a = list(store)?.optJSONArray("presets") ?: return emptyList()
        return (0 until a.length()).map { a.getString(it) }
    }

    fun races(store: File): List<String> {
        val a = list(store)?.optJSONArray("models") ?: return emptyList()
        return (0 until a.length()).map { a.getJSONObject(it).optString("race") }
    }

    /** The preset chosen ([choose]), else the zip's own default; [AS_DRAWN] when nothing is imported. */
    fun chosen(store: File): String {
        val list = presets(store)
        if (list.isEmpty()) return AS_DRAWN
        val picked = File(store, CHOICE).takeIf { it.isFile }?.readText()?.trim()
        if (picked == AS_DRAWN || (picked != null && picked in list)) return picked
        return list(store)?.optString("default")?.takeIf { it in list } ?: list.first()
    }

    fun choose(store: File, preset: String) {
        store.mkdirs()
        File(store, CHOICE).writeText("$preset\n")
    }

    /** Taken off the phone, and not looked for again ([lookFor]) until a zip is picked or used by hand. */
    fun remove(store: File) {
        store.deleteRecursively()
        off(store).apply { parentFile?.mkdirs() }.writeText("removed\n")
    }

    private fun off(store: File) = File(store.path + ".off")

    /**
     * The zip looked for by its name ([NAMES], where downloads are: [ImportFinder]) taken in by itself when nothing is
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
     * Takes the zip in ([store]/files, as the zip has it), in place of what was there, the choice kept; returns how many
     * models it has. A zip without a body shapes list, with a path leaving it, or whose blocks don't match the list is
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
            if (!listFile.isFile) throw IOException("This zip has no body shapes in it (no $LIST).")
            val list = JSONObject(listFile.readText())
            if (list.optString("kind") != "wrathpp-body") throw IOException("This zip isn't a Wrath++ body shapes zip.")
            val models = list.optJSONArray("models") ?: throw IOException("The body shapes list names no models.")
            if (models.length() == 0) throw IOException("The body shapes list names no models.")
            for (i in 0 until models.length()) {
                val m = models.getJSONObject(i)
                val skin = File(files, m.getString("skin_file"))
                if (!skin.isFile || sha256(skin.readBytes()) != m.getString("skin_sha256")) throw IOException("${m.optString("race")}: its skin is missing or damaged.")
                val blocks = m.getJSONObject("blocks")
                for (preset in blocks.keys()) {
                    val b = blocks.getJSONObject(preset)
                    val f = File(files, b.getString("file"))
                    if (!f.isFile || f.length() != b.getLong("vertices") * VERTEX || sha256(f.readBytes()) != b.getString("sha256")) {
                        throw IOException("${m.optString("race")} $preset: its shape is missing or damaged.")
                    }
                }
            }
            File(fresh, STAMP).writeText(digest.digest().joinToString("") { "%02x".format(it) } + "\n")
            File(store, CHOICE).takeIf { it.isFile }?.copyTo(File(fresh, CHOICE))
            store.deleteRecursively()
            if (!fresh.renameTo(store)) throw IOException("The body shapes couldn't be put in place.")
            off(store).delete()
            return models.length()
        } finally {
            fresh.deleteRecursively()
        }
    }

    /**
     * The chosen preset put into Wrath++'s looks in [client], or the looks' own put back (As drawn, nothing imported).
     * Returns what was done, a line for the start report.
     */
    fun apply(store: File, client: File, say: (String, Float?) -> Unit = { _, _ -> }): String {
        val patch = File(client, "Data/${WrathppLooks.PATCH}")
        if (!patch.isDirectory) return "no looks"
        val looks = File(patch, WrathppLooks.MARKER).takeIf { it.isFile }?.readText()?.trim().orEmpty()
        val zipSha = if (installed(store)) sha(store) else null
        val choice = chosen(store)
        val stamp = File(patch, STAMP)
        val want = "$zipSha $choice $looks"
        if (stamp.isFile && stamp.readLines().firstOrNull()?.trim() == want) return stamp.readLines().drop(1).joinToString("; ").ifEmpty { "as before" }
        takeOut(patch)
        stamp.delete()
        if (zipSha == null) return "none imported"
        if (choice == AS_DRAWN) { stamp.writeText("$want\nas drawn\n"); return "as drawn" }
        val list = list(store) ?: return "none imported"
        val models = list.getJSONArray("models")
        val done = ArrayList<String>()
        for (i in 0 until models.length()) {
            val m = models.getJSONObject(i)
            val race = m.optString("race")
            say("Putting in the body shapes: $race", i.toFloat() / models.length())
            val block = m.getJSONObject("blocks").optJSONObject(choice) ?: run { done.add("$race: no $choice in the zip"); null } ?: continue
            val model = File(patch, m.getString("model"))
            val skin = File(patch, m.getString("skin"))
            if (!model.isFile || !skin.isFile) { done.add("$race: not in the looks"); continue }
            val base = model.readBytes()
            if (sha256(base) != m.getString("looks_sha256")) { done.add("$race: made for other looks, left as drawn"); continue }
            val vertices = File(store, "files/${block.getString("file")}").readBytes()
            over(model, withVertices(base, vertices))
            over(skin, File(store, "files/${m.getString("skin_file")}").readBytes())
            done.add("$race: $choice")
        }
        stamp.writeText("$want\n" + done.joinToString("\n") + "\n")
        return done.joinToString("; ")
    }

    /**
     * [model] (a 3.3.5 .m2) with [vertices] (48 bytes each) as its vertices: put at its end (16-byte aligned) and named
     * in its header (count at 60, offset at 64); everything else of it as it was.
     */
    internal fun withVertices(model: ByteArray, vertices: ByteArray): ByteArray {
        require(model.size >= 68 && String(model, 0, 4, Charsets.ISO_8859_1) == "MD20") { "not a 3.3.5 model" }
        require(vertices.size % VERTEX == 0)
        val at = (model.size + 15) / 16 * 16
        val out = model.copyOf(at + vertices.size)
        System.arraycopy(vertices, 0, out, at, vertices.size)
        val b = java.nio.ByteBuffer.wrap(out).order(java.nio.ByteOrder.LITTLE_ENDIAN)
        b.putInt(60, vertices.size / VERTEX)
        b.putInt(64, at)
        return out
    }

    private fun takeOut(patch: File) {
        patch.walkTopDown().filter { it.isFile && it.name.endsWith(ORIG) }.toList().forEach { orig ->
            val target = File(orig.path.removeSuffix(ORIG))
            target.delete()
            if (!orig.renameTo(target)) throw IOException("${target.path} couldn't be put back")
        }
    }

    /** [bytes] over the looks' [target], whose own is kept beside it ([ORIG]) to put back. */
    private fun over(target: File, bytes: ByteArray) {
        val orig = File(target.path + ORIG)
        if (!orig.isFile) target.copyTo(orig)
        val tmp = File(target.path + ".tmp")
        tmp.writeBytes(bytes)
        if (!tmp.renameTo(target)) { target.delete(); if (!tmp.renameTo(target)) throw IOException("${target.path} couldn't be written") }
    }

    private fun sha256(bytes: ByteArray): String = MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }
}
