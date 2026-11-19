package com.logie.blizz.wrathpp

import java.io.File
import java.io.RandomAccessFile
import java.nio.ByteBuffer
import java.nio.ByteOrder

/**
 * Which model file the game draws for each race and sex, said in the start report so a phone can't hide it (report #332: the Troll
 * man was drawn as 3.3.5's own model, not the looks'). For each race display the looks' tables name (ChrRaces' male and female
 * displays, through CreatureDisplayInfo and CreatureModelData, as [WrathppDisplayCheck] reads them) it looks for the model file in
 * the looks' patch folder (`Data/patch-Z.MPQ`, any case: Wine finds a file in any case) and reads its header (version, bones,
 * vertices; whether the bones and vertices it names lie inside the file) and holds its length to the package's ([WrathppLooks.SIZES],
 * written as the looks are put in; a patch put in before that has none).
 *
 * Shadowed or missing: the game opens `Data\patch-?.MPQ` (files and folders alike: Storm's `SFileOpenArchive` opens a folder as an
 * archive read from the disk) in descending order of name, after which the locale's patches and `patch.MPQ`, each at a higher
 * priority than the one before; the base archives are below them all (Client.cpp `OpenArchives`, PatchFiles.cpp, in the client's
 * source). A name is answered by the first archive, by priority, that has it; a folder answers when the file exists on the disk
 * (SFileArchives.cpp `FindFileInOneArchive`). So `patch-Z.MPQ` is asked before every other archive (no one-letter patch name sorts
 * after it: [readBefore] names any that would) and a model the folder lacks is read from the next archive that has it, the game's or
 * the HD look's, which is what the line then names. A model the folder has but that is cut short is not looked for elsewhere.
 *
 * [ensure] fetches the looks again (the delta: only the files whose length or CRC-32 isn't the package's) when a model of theirs is
 * missing, damaged or not the package's, or when the patch has no size list yet (then every file is held to the package once), at
 * most once per looks. Unit-tested; NOT run on a phone.
 */
object WrathppModelCheck {
    /** In Wrath++'s copy of the game: the looks (their SHA-256) that [ensure] fetched again once. */
    const val TRIED = "wrathpp-looks.checked"
    private const val BONE = 88
    private const val VERTEX = 48
    private val NONE: (String) -> String? = { null }

    /** A model file's header (M2): its version, bones, vertices and skin profiles; [whole]: the bones and vertices lie inside the file. */
    data class Header(val version: Int, val bones: Long, val vertices: Long, val views: Long, val whole: Boolean)

    fun header(start: ByteArray, length: Long): Header? {
        if (start.size < 0x48 || String(start, 0, 4, Charsets.US_ASCII) != "MD20") return null
        val b = ByteBuffer.wrap(start).order(ByteOrder.LITTLE_ENDIAN)
        fun u(at: Int) = b.getInt(at).toLong() and 0xFFFFFFFFL
        val version = b.getInt(4)
        val whole = u(0x30) + u(0x2C) * BONE <= length && u(0x40) + u(0x3C) * VERTEX <= length
        return Header(version, u(0x2C), u(0x3C), u(0x44), whole)
    }

    fun header(file: File): Header? {
        val length = file.length()
        if (length < 0x48) return null
        val start = ByteArray(0x48)
        RandomAccessFile(file, "r").use { it.readFully(start) }
        return header(start, length)
    }

    /** One model a race display names, as found in the patch. [packaged]: its length in the package, null when unknown or not the looks'. */
    class Model(val races: List<String>, val path: String, val file: File?, val length: Long, val header: Header?, val packaged: Long?, val bodyLayer: Boolean,
                val origLength: Long? = null) {
        val name: String get() = path.substringAfterLast('\\')

        /** What is wrong with it, or null. [sizesKnown]: the patch has the package's size list. */
        fun problem(sizesKnown: Boolean): String? = when {
            file == null -> if (sizesKnown && packaged == null) null else "MISSING"
            header == null -> "NOT A MODEL FILE ($length bytes)"
            !header.whole -> "CUT SHORT ($length bytes; its header names more)"
            // (a model the body options replaced keeps the looks' own beside it, `.body-orig`: that one is the package's)
            packaged != null && (origLength ?: length) != packaged -> "NOT THE PACKAGE'S (${origLength ?: length} bytes, the package's $packaged)"
            else -> null
        }

        fun facts(): String = when {
            file == null -> "$name: not in the patch"
            header == null -> "$name: $length bytes, no model header"
            else -> "$name: $length bytes, v${header.version}, ${header.bones} bones, ${header.vertices} vertices" + (if (bodyLayer) ", with the body layer" else "")
        }
    }

    class Report(val models: List<Model>, val sizesKnown: Boolean, val before: List<String>) {
        /** The looks' models (in the package, or any when its list is unknown) that aren't as packaged. */
        val bad: List<Model> get() = models.filter { it.problem(sizesKnown) != null }
        val looks: List<Model> get() = models.filter { !sizesKnown || it.packaged != null }
        val needsRepair: Boolean get() = bad.isNotEmpty() || !sizesKnown

        /** The start report's lines; [owner]: the archive the game reads a name from when the patch lacks it. */
        fun lines(owner: (String) -> String? = { null }): String {
            val head = StringBuilder("race models: ")
            val ok = looks.count { it.problem(sizesKnown) == null }
            head.append("$ok of ${looks.size} in the looks' patch" + if (sizesKnown) ", as packaged" else " (the package's sizes not known: put in before this check)")
            for (m in bad) {
                head.append("; ").append(m.problem(sizesKnown)).append(": ").append(m.path).append(" (").append(m.races.joinToString(", "))
                if (m.file == null) head.append("; the game reads ").append(owner(m.path) ?: "it from no archive: nothing drawn")
                head.append(")")
            }
            val others = models.size - looks.size
            if (others > 0) head.append("; $others the game's own")
            head.append(if (before.isEmpty()) "; nothing is read before the looks' patch" else "; read BEFORE the looks' patch: ${before.joinToString(", ")}")
            return head.append('\n').append("race models' files: ").append(models.joinToString("; ") { it.facts() }).append('\n').toString()
        }
    }

    /** The archives of [data] the game would ask before `patch-Z.MPQ`: one-letter patches whose letter sorts after Z (`patch-_.MPQ`...). */
    fun readBefore(data: File): List<String> = data.list().orEmpty().filter { n ->
        n.length == 11 && n.startsWith("patch-", ignoreCase = true) && n.endsWith(".mpq", ignoreCase = true) && n[6].let { c -> !c.isLetterOrDigit() && c > 'Z' }
    }.sorted()

    /** CreatureModelData: each row's model path (its third column), by id. */
    fun readModelNames(data: ByteArray): Map<Int, String> {
        val b = ByteBuffer.wrap(data).order(ByteOrder.LITTLE_ENDIAN)
        val count = b.getInt(4); val size = b.getInt(12)
        val text = 20 + count * size
        return (0 until count).associate { r ->
            val at = text + b.getInt(20 + r * size + 8)
            var end = at
            while (end < data.size && data[end] != 0.toByte()) end++
            b.getInt(20 + r * size) to (if (at in text until data.size) String(data, at, end - at, Charsets.UTF_8) else "")
        }
    }

    /** [path] (a game path, backslashes) under [root], in any case, or null. */
    fun find(root: File, path: String): File? {
        var at = root
        for (part in path.split('\\', '/').filter { it.isNotEmpty() }) {
            val exact = File(at, part)
            at = if (exact.exists()) exact else at.listFiles()?.firstOrNull { it.name.equals(part, ignoreCase = true) } ?: return null
        }
        return at.takeIf { it.isFile }
    }

    /** The package's size list of [patch]: lengths by path (lower case, backslashes), or null when the patch has none. */
    fun sizes(patch: File): Map<String, Long>? = File(patch, WrathppLooks.SIZES).takeIf { it.isFile }?.readLines()?.mapNotNull { line ->
        val f = line.split('\t')
        if (f.size >= 3) f[2].replace('/', '\\').lowercase() to (f[0].toLongOrNull() ?: return@mapNotNull null) else null
    }?.toMap()

    /** What the looks' patch in [client] holds of each race display's model, or null when it lacks one of the three tables. */
    fun examine(client: File): Report? {
        val patch = File(client, "Data/${WrathppLooks.PATCH}")
        val dir = File(patch, "DBFilesClient")
        val chr = File(dir, "ChrRaces.dbc"); val cdi = File(dir, "CreatureDisplayInfo.dbc"); val cmd = File(dir, "CreatureModelData.dbc")
        if (!chr.isFile || !cdi.isFile || !cmd.isFile) return null
        val displays = WrathppDisplayCheck.readDisplays(cdi.readBytes())
        val names = readModelNames(cmd.readBytes())
        val sizes = sizes(patch)
        val byPath = LinkedHashMap<String, MutableList<String>>()
        for ((race, male, female) in WrathppDisplayCheck.readRaces(chr.readBytes())) {
            for ((sex, display) in listOf("male" to male, "female" to female)) {
                val name = displays[display]?.let { names[it] }?.takeIf { it.isNotEmpty() } ?: continue
                val path = name.replace('/', '\\').replace(Regex("\\.(mdx|mdl)$", RegexOption.IGNORE_CASE), ".m2")
                byPath.getOrPut(path) { ArrayList() }.add("race $race $sex")
            }
        }
        val models = byPath.map { (path, races) ->
            val file = find(patch, path)
            val orig = file?.let { File(it.path + ".body-orig") }?.takeIf { it.isFile }
            Model(races, path, file, file?.length() ?: 0L, file?.let { runCatching { header(it) }.getOrNull() }, sizes?.get(path.lowercase()), orig != null, orig?.length())
        }
        return Report(models, sizes != null, readBefore(File(client, "Data")))
    }

    /** The archive (its name) the game reads [path] from without the looks' patch, from the game's archives in [data]. */
    private fun ownerWithout(data: File): (String) -> String? {
        var game: com.logie.blizz.wowclient.Mpq.Game? = null
        return { path ->
            runCatching {
                val g = game ?: com.logie.blizz.wowclient.Mpq.Game(data, skip = listOf(WrathppLooks.PATCH.lowercase())).also { game = it }
                g.owner(path)?.let { "Data/" + it.relativeTo(data).invariantSeparatorsPath }
            }.getOrNull()
        }
    }

    /**
     * The start report's lines for [client]; when a model of the looks is missing, damaged or not the package's, or the patch has no
     * size list, the looks fetched again first ([repair]: [WrathppLooks.ensure] in its repair mode), at most once per looks.
     */
    fun ensure(client: File, server: File, say: (String, Float?) -> Unit, repair: () -> Unit = { WrathppLooks.ensure(client, server, say, update = true, repair = true) }): String {
        val first = examine(client) ?: return "race models: not checked (the looks' patch lacks one of the three tables)\n"
        val data = File(client, "Data")
        val sha = WrathppLooks.installedSha(client, server)
        val tried = File(client, TRIED)
        if (!first.needsRepair || sha == null || tried.takeIf { it.isFile }?.readText()?.trim() == sha) {
            return first.lines(if (first.bad.any { it.file == null }) ownerWithout(data) else NONE)
        }
        val marker = File(data, "${WrathppLooks.PATCH}/${WrathppLooks.MARKER}")
        val was = marker.lastModified()
        say("Checking Wrath++'s looks against their package", null)
        val failed = runCatching { repair() }.exceptionOrNull()
        // (put in again: the patch folder is a new one, its size list written; else, offline, the next start tries again)
        val redone = failed == null && File(data, "${WrathppLooks.PATCH}/${WrathppLooks.SIZES}").isFile && marker.lastModified() != was
        if (redone) WrathppLooks.installedSha(client, server)?.let { runCatching { tried.writeText("$it\n") } }
        val after = examine(client) ?: return "race models: not checked after the looks were put in again\n"
        val note = when {
            failed != null -> "race models: fetching the looks again FAILED (${failed.message}); as they were:\n"
            !redone -> "race models: the looks couldn't be fetched again (offline?); as they were:\n"
            else -> "race models: the looks were held to their package and put in again (" +
                (if (first.sizesKnown) "${first.bad.size} not as packaged: ${first.bad.joinToString(", ") { it.name }}" else "no size list before") + ")\n"
        }
        return note + after.lines(if (after.bad.any { it.file == null }) ownerWithout(data) else NONE)
    }
}
