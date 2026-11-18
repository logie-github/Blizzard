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
    /** Connections used at once (one connection to the CDN is far slower than the phone's line). */
    private val parallel: Int = 16,
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

    /** Runs [work] on every item with [parallel] threads; the first failure stops the rest and is thrown; [cancelled] stops it too. */
    private fun <T> inParallel(items: List<T>, cancelled: () -> Boolean, work: (T) -> Unit) {
        if (items.isEmpty()) return
        val pool = java.util.concurrent.Executors.newFixedThreadPool(parallel.coerceIn(1, 32))
        val failure = java.util.concurrent.atomic.AtomicReference<Throwable?>()
        val next = java.util.concurrent.atomic.AtomicInteger()
        try {
            val tasks = (0 until parallel.coerceIn(1, 32)).map {
                pool.submit {
                    while (failure.get() == null) {
                        if (cancelled()) { failure.compareAndSet(null, IOException("stopped")); break }
                        val i = next.getAndIncrement()
                        if (i >= items.size) break
                        try { work(items[i]) } catch (e: Throwable) { failure.compareAndSet(null, e) }
                    }
                }
            }
            tasks.forEach { it.get() }
        } finally { pool.shutdownNow() }
        failure.get()?.let { throw if (it is IOException) it else IOException(it.message ?: it.javaClass.simpleName, it) }
    }

    /**
     * The build's metadata files, by encoding key, that the local storage must hold for the client and CascLib to read it: the
     * encoding, install, download and size manifests, the roots, the patch index, and every VFS file.
     *
     * The VFS root names further VFS files (`vfs-1`, `vfs-2`, ...: 583 of them in build 70938, 133 MB together), and those hold the
     * game's file numbers. CascLib reads the game's files through them: with the VFS root alone in the storage it opened the
     * storage and then found no file by its number (the realm's map extractor on the phone, 16 November 2026: "Invalid
     * CinematicCamera.db2 file format! FILE_NOT_FOUND", 0 files extracted; the same here with CascLib on a storage this installer
     * made, and every sampled file read once they were stored).
     */
    fun metadataKeys(b: Build): List<String> {
        val vfs = b.config.keys.filter { it.matches(Regex("vfs-\\d+")) }.sortedBy { it.substringAfter('-').toInt() }.mapNotNull { b.config[it]?.getOrNull(1) }
        return (listOfNotNull(b.config["encoding"]?.getOrNull(1), b.config["install"]?.getOrNull(1), b.config["download"]?.getOrNull(1),
            b.config["size"]?.getOrNull(1), b.config["vfs-root"]?.getOrNull(1), b.config["root"]?.getOrNull(1),
            // the patch index: the client reads it as it opens its storage, and with Blizzard's servers out of reach (the phone's
            // games are kept off them) it ended there (its Tact.log: "Failed to download the patch index", then its crash file)
            b.config["patch-index"]?.getOrNull(1)) + vfs).distinct()
    }

    /** Stores those of [metadataKeys] the storage lacks; returns how many were fetched. */
    private fun storeMetadata(b: Build, writer: CascWriter, say: (String, Float?) -> Unit): Int {
        var meta = metadataKeys(b)
        // The root (the list of the game's files by number) is named by its content key alone: its encoding key is in the encoding
        // file. CascLib goes from the VFS files to it, so it is made sure of here too (a full download also has it as a game file).
        val rootKeys = b.config["root"].orEmpty()
        if (rootKeys.size == 1) {
            val encodingEKey = key(b, "encoding", 1)
            // (not found, or the encoding file unreadable: the game's own download brings the root, so the rest goes on)
            val rootEKey = runCatching { EncodingFile(BlteRandom(cdn, encodingEKey, cdn.size("data", encodingEKey))).lookup(rootKeys[0].unhex()) }.getOrNull()
            if (rootEKey != null) meta = (meta + rootEKey.hex()).distinct()
        }
        var stored = 0
        for ((i, ek) in meta.withIndex()) {
            if (writer.has(ek.unhex())) continue
            say("Storing the build's metadata (${i + 1} of ${meta.size})", i.toFloat() / meta.size)
            val rawSize = cdn.size("data", ek)
            writer.addStreamed(ek.unhex(), rawSize) { off, n -> cdn.get("data", ek, off, n.toLong()) }
            stored++
        }
        return stored
    }

    /**
     * Puts the metadata files a storage made by an earlier version lacks into it (the VFS files), for the build `.build.info` names:
     * a game already downloaded needs 133 MB more, not the game again. Returns how many files were fetched (0: nothing was missing).
     */
    fun repairMetadata(say: (String, Float?) -> Unit = { _, _ -> }): Int {
        val info = File(root, ".build.info").takeIf { it.isFile }?.readLines()?.filter { it.isNotBlank() } ?: throw IOException("the game folder has no .build.info")
        if (info.size < 2) throw IOException(".build.info is empty")
        val header = info[0].split('|').map { it.substringBefore('!').trim() }
        val row = info[1].split('|')
        fun cell(name: String) = row.getOrNull(header.indexOf(name)).orEmpty()
        val b = build(cell("Build Key"), cell("CDN Key"), cell("Version"), cell("Version").substringAfterLast('.').toIntOrNull() ?: 0)
        val writer = CascWriter(data)
        val stored = storeMetadata(b, writer, say)
        if (stored > 0) writer.finish()
        return stored
    }

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
        storeMetadata(b, writer, say)
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
        val located = java.util.concurrent.atomic.AtomicInteger()
        val toLocate = needed.count { it }
        val indexesDone = java.util.concurrent.atomic.AtomicInteger()
        inParallel(archives.indices.toList(), cancelled) { n ->
            if (located.get() >= toLocate) return@inParallel
            val idx = ArchiveIndex.parse(archives[n], cdn.get("data", archives[n], suffix = ".index"))
            synchronized(archiveOf) {
                for (i in idx.ekeys.indices) {
                    val j = itemKey[idx.ekeys[i].prefix64()]
                    if (j >= 0 && needed[j] && archiveOf[j] < 0 && fullKey(j).contentEquals(idx.ekeys[i])) { archiveOf[j] = n; offsetOf[j] = idx.offsets[i]; sizeOf[j] = idx.sizes[i]; located.incrementAndGet() }
                }
            }
            val d = indexesDone.incrementAndGet()
            say("Looking up where the files are ($d of ${archives.size})", d.toFloat() / archives.size)
        }
        if (planOnly) return plan

        // read them out: adjacent ranges of an archive together, many ranges at once
        class Job(val archive: String, val start: Long, val end: Long, val items: List<Int>)
        val jobs = ArrayList<Job>()
        var fetchBytes = 0L
        val byArchive = HashMap<Int, ArrayList<Int>>()
        for (j in 0 until total) if (needed[j] && archiveOf[j] >= 0) { byArchive.getOrPut(archiveOf[j]) { ArrayList() }.add(j); fetchBytes += sizeOf[j] }
        for ((archiveNo, items) in byArchive.toSortedMap()) {
            val sorted = items.sortedBy { offsetOf[it] }
            var i = 0
            while (i < sorted.size) {
                var k = i; val start = offsetOf[sorted[i]]
                var end = start + sizeOf[sorted[i]]
                while (k + 1 < sorted.size && offsetOf[sorted[k + 1]] - end <= 64 * 1024 && offsetOf[sorted[k + 1]] + sizeOf[sorted[k + 1]] - start <= (4L shl 20)) {
                    k++; end = offsetOf[sorted[k]] + sizeOf[sorted[k]]
                }
                jobs += Job(archives[archiveNo], start, end, sorted.subList(i, k + 1).toList())
                i = k + 1
            }
        }
        val done = java.util.concurrent.atomic.AtomicLong()
        var sinceCheckpoint = 0L
        val blobs = java.util.concurrent.ConcurrentHashMap<Int, ByteArray>()
        val looseSet = looseItem.toSet()
        val started = System.currentTimeMillis()
        inParallel(jobs, cancelled) { job ->
            val chunk = cdn.get("data", job.archive, job.start, job.end - job.start)
            for (j in job.items) {
                val bytes = chunk.copyOfRange((offsetOf[j] - job.start).toInt(), (offsetOf[j] - job.start).toInt() + sizeOf[j])
                if (j in looseSet) blobs[j] = bytes
                if (isWanted(j)) writer.add(fullKey(j), bytes)
            }
            val d = done.addAndGet(job.end - job.start)
            synchronized(writer) {
                sinceCheckpoint += job.end - job.start
                if (sinceCheckpoint >= checkpointBytes) { writer.finish(); sinceCheckpoint = 0 }
            }
            val secs = ((System.currentTimeMillis() - started) / 1000).coerceAtLeast(1)
            say("Downloading the game: ${d shr 20} / ${fetchBytes shr 20} MB (${(d shr 20) / secs} MB/s)", if (fetchBytes > 0) d.toFloat() / fetchBytes else null)
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
            val target = placeFor(File(root, programFolder), loosePath[k])
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
        writeFlavor(root, programFolder, product)
        File(root, ".build.info").writeText(buildInfo(b))
    }

    companion object {
        /**
         * Where a program file of the install list goes under [base]: its path with each folder taken as Windows takes it, whatever
         * its letters' case. The list names one folder in two ways (`UTILS\LIBCEF.DLL`, `Utils\chrome_elf.dll`): one folder on
         * Windows, two on a phone's file system, and the game then finds only the files of one of them. A folder that exists
         * under another case is used as it is.
         */
        fun placeFor(base: File, path: String): File {
            var dir = base
            val parts = path.replace('\\', '/').split('/').filter { it.isNotEmpty() }
            for (part in parts.dropLast(1)) {
                val there = if (File(dir, part).isDirectory) part else dir.list()?.firstOrNull { it.equals(part, ignoreCase = true) && File(dir, it).isDirectory }
                dir = File(dir, there ?: part)
            }
            return File(dir, parts.lastOrNull() ?: path)
        }

        /**
         * Folders under [dir] that differ only in their letters' case (an install made before [placeFor]) become one: the one with
         * the most files stays, the others' files move into it (one already there is kept), all the way down. Returns how many
         * folders were merged away.
         */
        fun mergeCaseFolders(dir: File): Int {
            var merged = 0
            val folders = dir.listFiles { f -> f.isDirectory }.orEmpty()
            for (group in folders.groupBy { it.name.lowercase() }.values) {
                if (group.size > 1) {
                    val keep = group.maxByOrNull { it.walkTopDown().count { f -> f.isFile } }!!
                    for (other in group) if (other != keep) { moveInto(other, keep); other.deleteRecursively(); merged++ }
                }
            }
            for (f in dir.listFiles { f -> f.isDirectory }.orEmpty()) merged += mergeCaseFolders(f)
            return merged
        }

        private fun moveInto(from: File, to: File) {
            for (f in from.listFiles().orEmpty()) {
                val name = to.list()?.firstOrNull { it.equals(f.name, ignoreCase = true) } ?: f.name
                val target = File(to, name)
                if (f.isDirectory) { target.mkdirs(); moveInto(f, target) }
                else if (!target.exists() && !f.renameTo(target)) { f.copyTo(target); f.delete() }
            }
        }

        /**
         * `<program folder>/.flavor.info`: which product of `.build.info` the program beside it is. Blizzard's installer writes it;
         * without it the client finds no installation ("Unable to initialize CAS from build info file. No active install info
         * entries", then it asks Blizzard's servers, which the phone's games can't reach). Returns true when it was written.
         */
        fun writeFlavor(root: File, programFolder: String, product: String): Boolean {
            val f = File(File(root, programFolder), ".flavor.info")
            val text = "Product Flavor!STRING:0\n$product\n"
            if (f.isFile && f.readText() == text) return false
            f.parentFile?.mkdirs(); f.writeText(text); return true
        }

        /** The product a `.build.info` names in its (first) row, or null. */
        fun productOf(buildInfo: String): String? {
            val lines = buildInfo.lines().filter { it.isNotBlank() }
            if (lines.size < 2) return null
            val at = lines[0].split('|').map { it.substringBefore('!').trim() }.indexOf("Product")
            return lines[1].split('|').getOrNull(at)?.trim()?.takeIf { it.isNotEmpty() }
        }
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
