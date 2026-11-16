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

    fun run(b: Build, say: (String, Float?) -> Unit = { _, _ -> }, cancelled: () -> Boolean = { false }): Plan {
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
        val install = InstallManifest.parse(Blte.decode(cdn.get("data", installEKey)))
        val download = DownloadManifest.parse(Blte.decode(cdn.get("data", downloadEKey)))
        val encoding = EncodingFile(BlteRandom(cdn, encodingEKey, cdn.size("data", encodingEKey)))

        // 3 and 4: what to fetch
        val loose = ArrayList<Triple<String, ByteArray, ByteArray>>() // path, ckey, ekey
        for (i in install.names.indices) {
            if (!install.tags.wanted(i, tags)) continue
            val ek = encoding.lookup(install.contentKeys[i]) ?: throw IOException("${install.names[i]} isn't in the encoding file")
            loose += Triple(install.names[i], install.contentKeys[i], ek)
        }
        val wanted = HashMap<String, Long>()   // ekey hex -> size
        for (i in download.ekeys.indices) {
            if (download.priorities[i] > maxPriority || !download.tags.wanted(i, tags)) continue
            wanted[download.ekeys[i].hex()] = download.sizes[i]
        }
        val looseEKeys = loose.map { it.third.hex() }.toSet()
        val plan = Plan(wanted.size, wanted.values.sum(), loose.size)
        say("To fetch: ${wanted.size} files, ${wanted.values.sum() shr 20} MB, and ${loose.size} program files", null)

        // find each file in the CDN's archives
        val archives = b.cdnConfig["archives"] ?: throw IOException("the CDN config lists no archives")
        val need = HashSet<String>(wanted.keys).also { it.addAll(looseEKeys) }
        need.removeAll { writer.has(it.unhex()) }
        val where = HashMap<String, Triple<String, Long, Int>>()   // ekey -> (archive, offset, size)
        for ((n, a) in archives.withIndex()) {
            if (cancelled()) throw IOException("stopped")
            if (where.size == need.size) break
            say("Looking up where the files are (${n + 1} of ${archives.size})", n.toFloat() / archives.size)
            val idx = ArchiveIndex.parse(a, cdn.get("data", a, suffix = ".index"))
            for (i in idx.ekeys.indices) { val h = idx.ekeys[i].hex(); if (h in need) where[h] = Triple(a, idx.offsets[i], idx.sizes[i]) }
        }

        // 4: read them out, archive by archive, adjacent ranges together
        val todo = need.filter { it in where }.groupBy { where.getValue(it).first }
        val total = todo.values.sumOf { l -> l.sumOf { where.getValue(it).third.toLong() } }
        val done = AtomicLong(); var sinceCheckpoint = 0L
        val blobs = HashMap<String, ByteArray>()
        for ((archive, keys) in todo) {
            val sorted = keys.sortedBy { where.getValue(it).second }
            var i = 0
            while (i < sorted.size) {
                if (cancelled()) { writer.finish(); throw IOException("stopped") }
                var j = i; val start = where.getValue(sorted[i]).second
                var end = start + where.getValue(sorted[i]).third
                while (j + 1 < sorted.size && where.getValue(sorted[j + 1]).second - end <= 64 * 1024 && where.getValue(sorted[j + 1]).second + where.getValue(sorted[j + 1]).third - start <= (8L shl 20)) {
                    j++; end = where.getValue(sorted[j]).second + where.getValue(sorted[j]).third
                }
                val chunk = cdn.get("data", archive, start, end - start)
                for (k in i..j) {
                    val (_, off, size) = where.getValue(sorted[k])
                    val bytes = chunk.copyOfRange((off - start).toInt(), (off - start).toInt() + size)
                    if (sorted[k] in looseEKeys) blobs[sorted[k]] = bytes
                    if (sorted[k] in wanted) { writer.add(sorted[k].unhex(), bytes); sinceCheckpoint += size }
                    done.addAndGet(size.toLong())
                }
                say("Downloading the game: ${done.get() shr 20} / ${total shr 20} MB", if (total > 0) done.get().toFloat() / total else null)
                if (sinceCheckpoint >= checkpointBytes) { writer.finish(); sinceCheckpoint = 0 }
                i = j + 1
            }
        }
        writer.finish()
        // the wanted files that weren't in an archive are loose on the CDN
        val missing = wanted.keys.filter { it !in where && !writer.has(it.unhex()) }
        for ((n, ek) in missing.withIndex()) {
            say("Downloading loose files (${n + 1} of ${missing.size})", n.toFloat() / missing.size)
            val size = cdn.size("data", ek)
            writer.addStreamed(ek.unhex(), size) { off, len -> cdn.get("data", ek, off, len.toLong()) }
            if (cancelled()) throw IOException("stopped")
        }
        writer.finish()

        // 3: the programs
        for ((n, f) in loose.withIndex()) {
            say("Writing the game's programs (${n + 1} of ${loose.size})", n.toFloat() / loose.size)
            val ek = f.third.hex()
            val blte = blobs[ek] ?: writer.read(f.third) ?: cdn.get("data", ek)
            val bytes = Blte.decode(blte)
            val md5 = MessageDigest.getInstance("MD5").digest(bytes)
            if (!md5.contentEquals(f.second)) throw IOException("${f.first} didn't match its checksum")
            val target = File(File(root, programFolder), f.first.replace('\\', '/'))
            if (!isInside(root, target)) throw IOException("unsafe path ${f.first}")
            target.parentFile?.mkdirs(); target.writeBytes(bytes)
        }

        // 5: what the game reads to find its data
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
