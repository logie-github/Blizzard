package com.logie.blizz.wrathpp

import com.logie.blizz.wowclient.Mpq
import java.io.File
import java.io.IOException
import java.io.RandomAccessFile
import java.net.HttpURLConnection
import java.net.URL

/**
 * Project Reforged (projectreforged.github.io/wotlk, "Modular Patch Library · WotLK 3.3.5"), put into Wrath++'s copy of the
 * game, for everything but the characters and character creation (the user, 13 November 2026: "Install it on everything
 * but characters and characters creation. Make it an auto import in the options"). Its patches are MPQs, downloaded by the
 * app from the project's own server (no file to pick) and chosen on Wrath++'s settings page ([Option]).
 *
 *  - **Left out**: Patch-A HD (player characters and NPCs: models, skins and the character tables) and Patch-U (upright
 *    orcs, needs A). Creatures (Patch-C) needs a Patch-A: it takes the SD one, which is 13 files of the high elf NPCs' models
 *    and nothing of the playable races.
 *  - **Letters**: Reforged's own (A, B, C...) are the HD look's, the realm modules' and Wrath++'s own in this game, so each
 *    part goes on a letter of its own ([Part.slot], F to Q, in Reforged's own order): after the game's patches and the HD
 *    look's (`patch-6`, `patch-A`, `patch-E` on the phone that reported, issue #121), before Wrath++'s creator art (S), creator
 *    (X) and looks (Z), which so win over anything of Reforged's. A shared archive of Wrath+'s on one of those letters is
 *    taken out of Wrath++'s copy only (Wrath+'s game is never touched) and comes back when the part is turned off.
 *  - **Character creation as it is**: every file Reforged has under `Interface\GlueXML` and `Interface\Glues` (the login,
 *    character select and creation screens, their textures and their 3D scenes, the login's Sindragosa among them; not the
 *    loading screens) is put back as the game's own in a patch read after Reforged's, `patch-T.MPQ` ([mask]).
 *    A file only Reforged has is then named by nothing (the game's own screens don't know it).
 *  - **Downloads** ([sync], run by [ReforgedDownloads] in the background) end as `<slot>.ready` beside the game's archives;
 *    only Play ([prepare], in Wrath++'s setup) puts them in place, so the game's archives never change under a running game
 *    or between the masking and the start. A part the project republishes (its ETag changes) is fetched again; a cut
 *    download resumes where it stopped.
 *
 * Not done: St0ny's EXE patcher, which the project calls required (client tweaks in Wow.exe: Wrath++'s exe is WarcraftXL's
 * copy; the MPQs load without it), and DXVK 3.1.1 (Winlator has its own). NOT run on a phone or in the game: unit-tested,
 * and the project's own files were read here (file lists, headers).
 */
object Reforged {
    const val BASE = "https://pub-0f05631d243e4046993fc02ca7be9542.r2.dev/Wrath%20of%20the%20Lich%20King/patches"
    const val STATE = "reforged.txt"
    const val MASK = "patch-T.MPQ"
    private const val MASK_STAMP = "reforged-mask.txt"
    /** Which files [masked] puts back; a change to it makes the mask again. v2: the login screen's own scene too (Sindragosa). */
    private const val MASK_RULES = "v2|"

    /** One MPQ of Reforged's: where it is, and the letter it takes in Wrath++'s copy (Reforged's own order kept). */
    enum class Part(val remote: String, val slot: Char, val megabytes: Int) {
        HIGH_ELVES("extras/patch-A.mpq", 'F', 5),
        BUILDINGS("patch-B.mpq", 'G', 2034),
        CREATURES("patch-C.mpq", 'H', 2495),
        DOODADS("patch-D.mpq", 'I', 3255),
        ENVIRONMENT("patch-E.mpq", 'J', 2290),
        GEAR("patch-G.mpq", 'K', 3384),
        INTERFACE("patch-I.mpq", 'L', 433),
        MAPS("patch-M.mpq", 'N', 2892),
        NIGHTS("patch-N.mpq", 'O', 3),
        SPELLS("patch-P.mpq", 'P', 85),
        SOUNDS("patch-S.mpq", 'Q', 413),
        SOUNDS_ALONE("extras/patch-S.mpq", 'Q', 414);

        val file get() = "patch-$slot.MPQ"
        val url get() = "$BASE/$remote"
    }

    /** What Wrath++'s settings page offers, each a switch. */
    enum class Option(val title: String, val detail: String) {
        WORLD("World", "Buildings, doodads and environment (Reforged's B, D and E, which go together): 7.6 GB"),
        CREATURES("Creatures", "Creature models and the high elf NPCs they need (C, and A's small SD version): 2.5 GB"),
        GEAR("Gear and weapons", "Items' models and textures (G): 3.4 GB"),
        INTERFACE("Interface", "The in-game interface (I); the login, character select and creation screens stay the game's own: 433 MB"),
        MAPS("Maps and loading screens", "World map, dungeon maps and loading screens (M): 2.9 GB"),
        NIGHTS("Darker nights", "(N): 3 MB"),
        SPELLS("Spell effects", "Spell particles (P): 85 MB"),
        SOUNDS("Sounds and music", "(S; the version made for Maps when Maps is on): 413 MB");
    }

    fun parts(options: Set<Option>): Set<Part> = buildSet {
        for (o in options) when (o) {
            Option.WORLD -> { add(Part.BUILDINGS); add(Part.DOODADS); add(Part.ENVIRONMENT) }
            Option.CREATURES -> { add(Part.HIGH_ELVES); add(Part.CREATURES) }
            Option.GEAR -> add(Part.GEAR)
            Option.INTERFACE -> add(Part.INTERFACE)
            Option.MAPS -> add(Part.MAPS)
            Option.NIGHTS -> add(Part.NIGHTS)
            Option.SPELLS -> add(Part.SPELLS)
            Option.SOUNDS -> add(if (Option.MAPS in options) Part.SOUNDS else Part.SOUNDS_ALONE)
        }
    }

    // ---- the choice (files/wrathpp-reforged.txt: one option a line) ----

    fun choiceFile(filesDir: File) = File(filesDir, "wrathpp-reforged.txt")

    fun chosen(filesDir: File): Set<Option> = runCatching {
        choiceFile(filesDir).readLines().mapNotNull { line -> Option.entries.firstOrNull { it.name == line.trim() } }.toSet()
    }.getOrDefault(emptySet())

    fun choose(filesDir: File, options: Set<Option>) {
        val f = choiceFile(filesDir)
        f.parentFile?.mkdirs()
        val tmp = File(f.path + ".tmp")
        tmp.writeText(Option.entries.filter { it in options }.joinToString("") { it.name + "\n" })
        if (!tmp.renameTo(f)) { f.delete(); tmp.renameTo(f) }
    }

    // ---- what is in the game (Data/reforged.txt: slot, remote, etag, size) ----

    data class Installed(val slot: Char, val remote: String, val etag: String, val size: Long)

    private fun parse(line: String): Installed? {
        val p = line.split('\t')
        if (p.size < 4 || p[0].length != 1) return null
        return Installed(p[0][0], p[1], p[2], p[3].toLongOrNull() ?: return null)
    }

    private fun format(i: Installed) = "${i.slot}\t${i.remote}\t${i.etag}\t${i.size}"

    fun installed(data: File): Map<Char, Installed> = runCatching {
        File(data, STATE).readLines().mapNotNull(::parse).associateBy { it.slot }
    }.getOrDefault(emptyMap())

    private fun writeInstalled(data: File, all: Collection<Installed>) {
        val f = File(data, STATE)
        if (all.isEmpty()) { f.delete(); return }
        val tmp = File(data, "$STATE.tmp")
        tmp.writeText(all.sortedBy { it.slot }.joinToString("") { format(it) + "\n" })
        if (!tmp.renameTo(f)) { f.delete(); tmp.renameTo(f) }
    }

    private fun ready(data: File, part: Part) = File(data, part.file + ".ready")
    private fun readyInfo(data: File, part: Part) = File(data, part.file + ".ready.info")
    private fun partial(data: File, part: Part) = File(data, part.file + ".part")
    private fun partialInfo(data: File, part: Part) = File(data, part.file + ".part.info")

    private fun readInfo(f: File): Installed? = runCatching { parse(f.readText().trim()) }.getOrNull()

    /** [part] is in the game as the project's file named [etag] (null: any). */
    fun isIn(data: File, part: Part, etag: String? = null): Boolean {
        val i = installed(data)[part.slot] ?: return false
        return i.remote == part.remote && (etag == null || i.etag == etag) && File(data, part.file).length() == i.size
    }

    // ---- at Play: put what is ready in place, take out what isn't chosen, mask the glue screens ----

    /**
     * Wrath++'s setup, before the creator's patch is written: [client]'s `Data` made to hold the parts of [options] that are
     * downloaded (`.ready` ones put in place), none of the others, and the mask over them. [shared]: Wrath+'s `Data`, whose
     * archive on a letter Reforged takes is taken out of Wrath++'s copy. Returns lines for the setup log.
     */
    fun prepare(client: File, shared: File?, options: Set<Option>): String {
        val data = File(client, "Data")
        if (!data.isDirectory) return "reforged: no Data\n"
        val wanted = parts(options)
        val notes = StringBuilder()
        val state = installed(data).toMutableMap()
        // out: what is in and not wanted (a slot's other version too: Sounds made for Maps or alone)
        for ((slot, i) in state.toMap()) {
            if (wanted.any { it.slot == slot && it.remote == i.remote }) continue
            File(data, "patch-$slot.MPQ").delete()
            state.remove(slot)
            notes.append("reforged: patch-$slot.MPQ (${i.remote}) taken out\n")
        }
        for (part in Part.entries) if (part !in wanted) {
            ready(data, part).delete(); readyInfo(data, part).delete(); partial(data, part).delete(); partialInfo(data, part).delete()
        }
        writeInstalled(data, state.values)
        // in: what finished downloading
        for (part in wanted) {
            val r = ready(data, part)
            val info = readInfo(readyInfo(data, part))
            if (!r.isFile || info == null || info.remote != part.remote || r.length() != info.size) continue
            val place = File(data, part.file)
            if (place.exists() && state[part.slot] == null) {
                notes.append("reforged: ${part.file} of Wrath+'s game taken out of Wrath++'s copy for Reforged's ${part.remote}" +
                    (if (shared != null && File(shared, part.file).exists()) "" else " (it wasn't Wrath+'s: deleted)") + "\n")
            }
            place.delete()
            if (!r.renameTo(place)) { notes.append("reforged: ${part.file} couldn't be put in place\n"); continue }
            readyInfo(data, part).delete()
            state[part.slot] = info.copy(slot = part.slot)
            writeInstalled(data, state.values)
            notes.append("reforged: ${part.remote} put in as ${part.file}\n")
        }
        for (part in wanted) notes.append("reforged: ${part.remote} " + (if (isIn(data, part)) "in (${part.file})" else "not downloaded yet") + "\n")
        notes.append(runCatching { mask(data) }.getOrElse { e -> "reforged: the glue screens' mask FAILED: ${e.message}\n" })
        return notes.toString()
    }

    /**
     * A game path of Reforged's that is put back as the game's own: the glue screens' code and art, the login screen's own
     * scene among them (the user, 13 November 2026: "I want the original wrath login screen with sindragosa"; Reforged's
     * draws a still picture in its place). Not the loading screens.
     */
    fun masked(path: String): Boolean {
        val p = path.replace('/', '\\').lowercase()
        if (p.startsWith("interface\\gluexml\\")) return true
        if (!p.startsWith("interface\\glues\\")) return false
        if (p.startsWith("interface\\glues\\loadingscreens\\")) return false
        return true
    }

    /**
     * `patch-T.MPQ`: the game's own version of every [masked] file the Reforged parts in [data] have, read from the game without
     * them. Made again only when the parts in changed. No Reforged part with such files: none.
     */
    fun mask(data: File): String {
        val state = installed(data)
        val ours = state.keys.map { "patch-$it.mpq".lowercase() }
        val stamp = MASK_RULES + state.values.sortedBy { it.slot }.joinToString("|") { "${it.slot}:${it.remote}:${it.etag}:${it.size}" }
        val place = File(data, MASK)
        val stampFile = File(data, MASK_STAMP)
        if (state.isEmpty()) {
            if (stampFile.isFile) { place.delete(); stampFile.delete() }
            return ""
        }
        if (runCatching { stampFile.readText() }.getOrNull() == stamp) return "reforged: mask as it was\n"
        val names = LinkedHashMap<String, String>()
        val unreadable = ArrayList<String>()
        for (slot in state.keys.sorted()) {
            val archive = Mpq.File_(File(data, "patch-$slot.MPQ"))
            try {
                val list = archive.read("(listfile)")
                if (list == null) { unreadable += "patch-$slot.MPQ"; continue }
                for (line in String(list, Charsets.ISO_8859_1).split('\n', '\r', ';')) {
                    val name = line.trim()
                    if (name.isNotEmpty() && masked(name)) names.putIfAbsent(name.lowercase(), name)
                }
            } finally { archive.close() }
        }
        // the game's own, without Reforged, the mask and what Wrath++ writes after it
        val game = Mpq.Game(data, skip = ours + listOf(MASK.lowercase(), WrathppAddon.PATCH.lowercase()))
        var count = 0
        val tmp = File(data, "$MASK.tmp")
        try {
            val writer = Mpq.Writer(tmp)
            for (name in names.values) {
                val own = game.read(name) ?: continue
                if (!writer.add(name, own)) throw IOException("$name couldn't be written")
                count++
            }
            if (count == 0) {
                writer.finish(); tmp.delete(); place.delete()
            } else {
                if (!writer.finish()) throw IOException("the mask couldn't be written")
                place.delete()
                if (!tmp.renameTo(place)) throw IOException("the mask couldn't be put in place")
            }
        } finally {
            game.close()
            tmp.delete()
        }
        stampFile.writeText(stamp)
        return "reforged: mask $MASK of ${names.size} glue files, $count of them the game's own put back" +
            (if (unreadable.isEmpty()) "" else "; no file list in ${unreadable.joinToString()}: their glue files can't be put back") + "\n"
    }

    // ---- downloading (in the background; never into the game itself) ----

    /** The project's server, behind an interface so the downloads are tested without it. */
    interface Net {
        /** The file's ETag and size, or null when it can't be reached. */
        fun head(url: String): Pair<String, Long>?
        /** Appends the file from byte [from] to [to]; [progress] gets the bytes written so far. Returns the ETag served. */
        fun get(url: String, from: Long, to: File, progress: (Long) -> Unit): String?
    }

    data class Progress(val text: String, val done: Long, val total: Long)

    class Cancelled : IOException("cancelled")

    /**
     * Downloads every part of [options] that isn't in [data] as the project now publishes it (nor ready), each to
     * `<slot>.part` (resumed), checked (its size, an MPQ's header) and renamed `<slot>.ready` for [prepare]. Offline with a
     * part in: kept. [cancelled] stops between blocks (the part kept to resume). Returns lines saying how each went.
     */
    fun sync(data: File, options: Set<Option>, net: Net, freeBytes: () -> Long = { data.usableSpace },
             cancelled: () -> Boolean = { false }, progress: (Progress) -> Unit = {}): List<String> {
        val out = ArrayList<String>()
        val wanted = parts(options).sortedBy { it.megabytes }
        for ((index, part) in wanted.withIndex()) {
            if (cancelled()) throw Cancelled()
            val remote = net.head(part.url)
            if (remote == null) {
                out += if (isIn(data, part) || ready(data, part).isFile) "${part.remote}: the project's server didn't answer; the one here is kept"
                else "${part.remote}: the project's server didn't answer"
                continue
            }
            val (etag, size) = remote
            if (isIn(data, part, etag)) { out += "${part.remote}: up to date"; continue }
            val readyInfo = readInfo(readyInfo(data, part))
            if (ready(data, part).isFile && readyInfo?.etag == etag && readyInfo.remote == part.remote) { out += "${part.remote}: downloaded, goes in at the next Play"; continue }
            val p = partial(data, part)
            val pInfo = readInfo(partialInfo(data, part))
            if (pInfo == null || pInfo.etag != etag || pInfo.remote != part.remote || pInfo.size != size || p.length() > size) {
                p.delete()
                partialInfo(data, part).writeText(format(Installed(part.slot, part.remote, etag, size)))
            }
            val need = size - p.length() + (512L shl 20)
            val free = freeBytes()
            if (free in 1 until need) {
                out += "${part.remote}: not enough space (${need shr 20} MB needed, ${free shr 20} MB free)"
                continue
            }
            val label = "Project Reforged ${index + 1} of ${wanted.size}: ${part.remote.substringAfterLast('/')}"
            val served = net.get(part.url, p.length(), p) { done -> progress(Progress(label, done, size)) }
            if (cancelled() && p.length() < size) throw Cancelled()
            if (served != null && served != etag) { out += "${part.remote}: changed while it downloaded; again next time"; p.delete(); partialInfo(data, part).delete(); continue }
            if (p.length() != size) { out += "${part.remote}: cut off at ${p.length() shr 20} of ${size shr 20} MB; it goes on next time"; continue }
            if (!isMpq(p)) { out += "${part.remote}: what came isn't an MPQ"; p.delete(); partialInfo(data, part).delete(); continue }
            ready(data, part).delete()
            if (!p.renameTo(ready(data, part))) { out += "${part.remote}: couldn't be kept"; continue }
            partialInfo(data, part).renameTo(readyInfo(data, part))
            out += "${part.remote}: downloaded, goes in at the next Play"
        }
        return out
    }

    /** What is still to download for [options], in bytes (the parts not in nor ready, at their listed size, less what's begun). */
    fun remaining(data: File, options: Set<Option>): Long = parts(options).sumOf { part ->
        if (isIn(data, part) || ready(data, part).isFile) 0L else (part.megabytes.toLong() shl 20) - partial(data, part).length()
    }.coerceAtLeast(0L)

    fun isMpq(f: File): Boolean = runCatching {
        RandomAccessFile(f, "r").use { r -> val b = ByteArray(4); r.readFully(b); b[0] == 'M'.code.toByte() && b[1] == 'P'.code.toByte() && b[2] == 'Q'.code.toByte() && b[3] == 0x1A.toByte() }
    }.getOrDefault(false)

    /** The real server: plain HTTPS with resume (the project's host serves ranges and ETags; it refuses Python's agent, not this one). */
    class Http(private val cancelled: () -> Boolean = { false }) : Net {
        private fun open(url: String, method: String, from: Long = 0): HttpURLConnection =
            (URL(url).openConnection() as HttpURLConnection).apply {
                requestMethod = method
                connectTimeout = 20_000
                readTimeout = 60_000
                setRequestProperty("User-Agent", "Blizzard-Launcher")
                setRequestProperty("Accept-Encoding", "identity")
                if (from > 0) setRequestProperty("Range", "bytes=$from-")
            }

        override fun head(url: String): Pair<String, Long>? = runCatching {
            val c = open(url, "HEAD")
            try {
                if (c.responseCode != 200) return null
                val etag = tag(c.getHeaderField("ETag")) ?: c.getHeaderField("Last-Modified") ?: return null
                etag to c.contentLengthLong.takeIf { it > 0 }!!
            } finally { c.disconnect() }
        }.getOrNull()

        override fun get(url: String, from: Long, to: File, progress: (Long) -> Unit): String? {
            val c = open(url, "GET", from)
            try {
                val code = c.responseCode
                val start = when (code) { 206 -> from; 200 -> 0L; else -> throw IOException("HTTP $code") }
                RandomAccessFile(to, "rw").use { out ->
                    out.setLength(start); out.seek(start)
                    var done = start
                    c.inputStream.use { input ->
                        val buffer = ByteArray(1 shl 16)
                        while (!cancelled()) {
                            val n = input.read(buffer); if (n < 0) break
                            out.write(buffer, 0, n); done += n; progress(done)
                        }
                    }
                }
                return tag(c.getHeaderField("ETag"))
            } finally { c.disconnect() }
        }
    }

    /** An ETag as the server says it, without its quotes or weak mark. */
    internal fun tag(raw: String?): String? = raw?.trim()?.removePrefix("W/")?.trim('"')?.takeIf { it.isNotEmpty() }
}
