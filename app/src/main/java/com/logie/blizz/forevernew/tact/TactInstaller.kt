package com.logie.blizz.forevernew.tact

import java.io.File
import java.io.IOException
import java.security.MessageDigest
import java.util.concurrent.atomic.AtomicLong

/**
 * Installs a game from Blizzard's own public content servers into a local game folder the client and CascLib can read, as Blizzard's
 * Agent does: nothing of the game is in this app or this repository, every byte is fetched from Blizzard's servers by hash and checked.
 *
 *  1. the build's config and the CDN's config (which archives hold what);
 *  2. the encoding, install and download manifests (and the other metadata files, stored into the local storage as they are);
 *  3. the loose files of the install manifest (the programs), through the encoding file, written to their paths and checked by MD5;
 *  4. the download manifest's files up to [maxPriority] for the [tags] chosen, read out of the CDN's archives by ranges and appended to the
 *     local data files with their index;
 *  5. `.build.info` and `Data/config`.
 * It carries on where an interrupted run stopped (the index is written every [checkpointBytes]). NOT run on a phone.
 */
class TactInstaller(
    private val cdn: Cdn, private val root: File, private val product: String, private val region: String = "us",
    /** Where the loose program files go, under [root] (`_forever_`, beside the shared `Data`). */
    private val programFolder: String = "_forever_",
    private val tags: Set<String> = setOf("Windows", "x86_64", "enUS", "US", "speech", "text"),
    private val maxPriority: Int = Int.MAX_VALUE,
    private val checkpointBytes: Long = 512L shl 20,
) {
    class Build(val buildKey: String, val cdnKey: String, val versionName: String, val buildId: Int, val config: Map<String, List<String>>, val cdnConfig: Map<String, List<String>>, val buildText: String, val cdnText: String)

    data class Plan(val files: Int, val bytes: Long, val looseFiles: Int)

    private val data = File(root, "Data/data")

    fun build(buildKey: String, cdnKey: String, versionName: String, buildId: Int): Build {
        val bt = String(cdn.get("config", buildKey), Charsets.UTF_8)
        val ct = String(cdn.get("config", cdnKey), Charsets.UTF_8)
        return Build(buildKey, cdnKey, versionName, buildId, TactText.config(bt), TactText.config(ct), bt, ct)
    }

    private fun key(b: Build, name: String, index: Int): String = b.config[name]?.getOrNull(index) ?: throw IOException("the build has no '$name'")

    /** The download manifest: fetched whole with progress, decoded, and the encoded copy let go before the caller goes on. */
    private fun downloadManifest(ekey: String, say: (String, Float?) -> Unit): DownloadManifest {
        val decoded = Blte.decode(fetchWhole(ekey, "Downloading the list of the game's files", say))
        say("Reading the list of the game's files", null)
        return DownloadManifest.parse(decoded)
    }

    /** A whole file from the CDN with progress, in pieces (the download manifest is 48 MB: one request gave no sign of life). */
    private fun fetchWhole(ekey: String, label: String, say: (String, Float?) -> Unit): ByteArray {
        val size = cdn.size("data", ekey)
        val out = ByteArray(size.toInt())
        var done = 0
        while (done < out.size) {
            val n = minOf(4 shl 20, out.size - done)
            val part = cdn.get("data", ekey, done.toLong(), n.toLong())
            System.arraycopy(part, 0, out, done, part.size); done += part.size
            say("$label: ${done shr 20} / ${out.size shr 20} MB", done.toFloat() / out.size)
        }
        return out
    }

    /**
     * Installs. [planOnly]: stops after working out what to fetch and where it is (what a test on a small memory limit runs).
     * Memory is kept small on purpose: the download manifest has 2.2 million entries, so entries are positions in its bytes, the
     * wanted ones numbers in primitive arrays, and the writer keeps its index in arrays too.
     */
    fun run(b: Build, say: (String, Float?) -> Unit = { _, _ -> }, cancelled: () -> Boolean = { false }, planOnly: Boolean = false): Plan {
        root.mkdirs()
        val writer = CascWriter(data)
        // 2: the metadata files, by encoding key, kept in the local storage
        say("Reading the build's manifests", null)
        val encodingEKey = key(b, "encoding", 1)
        val installEKey = key(b, "install", 1); val downloadEKey = key(b, "download", 1)
        val meta = listOfNotNull(encodingEKey, installEKey, downloadEKey, b.config["size"]?.getOrNull(1), b.config["vfs-root"]?.getOrNull(1), b.config["root"]?.getOrNull(1))
        for ((i, ek) in meta.withIndex()) {
            if (writer.has(ek.unhex())) continue
            say("Storing the build's metadata (${i + 1} of ${meta.size})", i.toFloat() / meta.size)
            val rawSize = cdn.size("data", ek)
            writer.addStreamed(ek.unhex(), rawSize) { off, n ->
                say("Storing the build's metadata (${i + 1} of ${meta.size}): ${off shr 20} / ${rawSize shr 20} MB", (i + off.toFloat() / rawSize.coerceAtLeast(1)) / meta.size)
                cdn.get("data", ek, off, n.toLong())
            }
        }
        writer.finish()
        say("Reading the list of programs", null)
        val install = InstallManifest.parse(Blte.decode(cdn.get("data", installEKey)))
        // 3: the programs (loose files), through the encoding file, before the big manifest is in memory (the encoding file's frames are about 60 MB each)
        say("Reading the encoding file's index", null)
        val loosePath = ArrayList<String>(); val looseCKey = ArrayList<ByteArray>(); val looseEKey = ArrayList<ByteArray>()
        run {
            val encoding = EncodingFile(BlteRandom(cdn, encodingEKey, cdn.size("data", encodingEKey)))
            val wantedInstall = install.names.indices.filter { install.tags.wanted(it, tags) }
            say("Finding the programs in the encoding file", null)
            val found = encoding.lookupAll(wantedInstall.map { install.contentKeys[it] })
            for ((k, i) in wantedInstall.withIndex()) {
                loosePath += install.names[i]; looseCKey += install.contentKeys[i]
                looseEKey += found[k] ?: throw IOException("${install.names[i]} isn't in the encoding file")
            }
        }
        val download = downloadManifest(downloadEKey, say)

        // 4: the game's files to fetch: numbers in arrays, their keys looked up in the manifest when needed
        say("Choosing the files for this phone's game", null)
        val select = download.tags.selector(tags)
        var wantedCount = 0
        val wantedIdx = IntArray(download.count)
        var wantedBytes = 0L
        for (i in 0 until download.count) if (download.priority(i) <= maxPriority && select(i)) { wantedIdx[wantedCount++] = i; wantedBytes += download.size(i) }
        // item j: j < wantedCount is wantedIdx[j]'s file; the rest are the programs' (some of which are also among the first)
        val total = wantedCount + looseEKey.size
        val itemKey = LongIntMap(total)
        for (j in 0 until wantedCount) itemKey[download.prefix(wantedIdx[j])] = j
        val looseItem = IntArray(looseEKey.size)
        for (k in looseEKey.indices) { val pk = looseEKey[k].prefix64(); val existing = itemKey[pk]; if (existing >= 0) looseItem[k] = existing else { itemKey[pk] = wantedCount + k; looseItem[k] = wantedCount + k } }
        val plan = Plan(wantedCount, wantedBytes, loosePath.size)
        say("To fetch: $wantedCount files, ${wantedBytes shr 20} MB, and ${loosePath.size} program files", null)

        fun fullKey(j: Int): ByteArray = if (j < wantedCount) download.ekey(wantedIdx[j]) else looseEKey[j - wantedCount]
        fun isWanted(j: Int) = j < wantedCount
        // what the local storage already has needn't be fetched again; a program's blob is still needed
        val needed = BooleanArray(total)
        for (j in 0 until total) needed[j] = !writer.has(fullKey(j)) || (j >= wantedCount) || looseItem.contains(j)

        // find each file in the CDN's archives
        val archives = b.cdnConfig["archives"] ?: throw IOException("the CDN config lists no archives")
        val archiveOf = IntArray(total) { -1 }; val offsetOf = LongArray(total); val sizeOf = IntArray(total)
        var located = 0
        val toLocate = needed.count { it }
        for ((n, a) in archives.withIndex()) {
            if (cancelled()) throw IOException("stopped")
            if (located >= toLocate) break
            say("Looking up where the files are (${n + 1} of ${archives.size})", n.toFloat() / archives.size)
            val idx = ArchiveIndex.parse(a, cdn.get("data", a, suffix = ".index"))
            for (i in idx.ekeys.indices) {
                val j = itemKey[idx.ekeys[i].prefix64()]
                if (j >= 0 && needed[j] && archiveOf[j] < 0 && fullKey(j).contentEquals(idx.ekeys[i])) { archiveOf[j] = n; offsetOf[j] = idx.offsets[i]; sizeOf[j] = idx.sizes[i]; located++ }
            }
        }
        if (planOnly) return plan

        // read them out, archive by archive, adjacent ranges together
        val byArchive = HashMap<Int, ArrayList<Int>>()
        var fetchBytes = 0L
        for (j in 0 until total) if (needed[j] && archiveOf[j] >= 0) { byArchive.getOrPut(archiveOf[j]) { ArrayList() }.add(j); fetchBytes += sizeOf[j] }
        var done = 0L; var sinceCheckpoint = 0L
        val blobs = HashMap<Int, ByteArray>()
        val looseSet = looseItem.toSet()
        for ((archiveNo, items) in byArchive.toSortedMap()) {
            val archive = archives[archiveNo]
            val sorted = items.sortedBy { offsetOf[it] }
            var i = 0
            while (i < sorted.size) {
                if (cancelled()) { writer.finish(); throw IOException("stopped") }
                var k = i; val start = offsetOf[sorted[i]]
                var end = start + sizeOf[sorted[i]]
                while (k + 1 < sorted.size && offsetOf[sorted[k + 1]] - end <= 64 * 1024 && offsetOf[sorted[k + 1]] + sizeOf[sorted[k + 1]] - start <= (8L shl 20)) {
                    k++; end = offsetOf[sorted[k]] + sizeOf[sorted[k]]
                }
                val chunk = cdn.get("data", archive, start, end - start)
                for (m in i..k) {
                    val j = sorted[m]
                    val bytes = chunk.copyOfRange((offsetOf[j] - start).toInt(), (offsetOf[j] - start).toInt() + sizeOf[j])
                    if (j in looseSet) blobs[j] = bytes
                    if (isWanted(j)) { writer.add(fullKey(j), bytes); sinceCheckpoint += sizeOf[j] }
                    done += sizeOf[j]
                }
                say("Downloading the game: ${done shr 20} / ${fetchBytes shr 20} MB", if (fetchBytes > 0) done.toFloat() / fetchBytes else null)
                if (sinceCheckpoint >= checkpointBytes) { writer.finish(); sinceCheckpoint = 0 }
                i = k + 1
            }
        }
        writer.finish()
        // the wanted files that weren't in an archive are loose on the CDN
        val missing = (0 until wantedCount).filter { needed[it] && archiveOf[it] < 0 }
        for ((n, j) in missing.withIndex()) {
            say("Downloading loose files (${n + 1} of ${missing.size})", n.toFloat() / missing.size)
            val ek = fullKey(j)
            val size = cdn.size("data", ek.hex())
            writer.addStreamed(ek, size) { off, len -> cdn.get("data", ek.hex(), off, len.toLong()) }
            if (cancelled()) throw IOException("stopped")
        }
        writer.finish()

        // the programs
        for (k in looseEKey.indices) {
            say("Writing the game's programs (${k + 1} of ${looseEKey.size})", k.toFloat() / looseEKey.size)
            val blte = blobs[looseItem[k]] ?: writer.read(looseEKey[k]) ?: cdn.get("data", looseEKey[k].hex())
            val bytes = Blte.decode(blte)
            val md5 = MessageDigest.getInstance("MD5").digest(bytes)
            if (!md5.contentEquals(looseCKey[k])) throw IOException("${loosePath[k]} didn't match its checksum")
            val target = File(File(root, programFolder), loosePath[k].replace('\\', '/'))
            if (!isInside(root, target)) throw IOException("unsafe path ${loosePath[k]}")
            target.parentFile?.mkdirs(); target.writeBytes(bytes)
        }

        // what the game reads to find its data
        writeConfigs(b)
        return plan
    }

    private fun isInside(base: File, f: File) = f.canonicalPath.startsWith(base.canonicalPath + File.separator)

    private fun writeConfigs(b: Build) {
        for ((k, text) in listOf(b.buildKey to b.buildText, b.cdnKey to b.cdnText)) {
            val f = File(root, "Data/config/${k.substring(0, 2)}/${k.substring(2, 4)}/$k")
            f.parentFile?.mkdirs(); f.writeText(text)
        }
        File(root, ".build.info").writeText(buildInfo(b))
    }

    /** The file the client reads to know what is installed and where its content comes from. */
    fun buildInfo(b: Build): String {
        val header = "Branch!STRING:0|Active!DEC:1|Build Key!HEX:16|CDN Key!HEX:16|Install Key!HEX:16|IM Size!DEC:4|CDN Path!STRING:0|CDN Hosts!STRING:0|CDN Servers!STRING:0|Tags!STRING:0|Armadillo!STRING:0|Last Activated!STRING:0|Version!STRING:0|KeyRing!HEX:16|Product!STRING:0"
        val installEKey = b.config["install"]?.getOrNull(1).orEmpty()
        val imSize = b.config["install-size"]?.getOrNull(1).orEmpty()
        val tagsText = "Windows x86_64 US? enUS speech?:Windows x86_64 US? enUS text?"
        val row = listOf(region, "1", b.buildKey, b.cdnKey, installEKey, imSize, "tpr/wow", "level3.blizzard.com us.cdn.blizzard.com", "", tagsText, "", "", b.versionName, "", product).joinToString("|")
        return header + "\n" + row + "\n"
    }
}
