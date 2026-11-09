package com.logie.blizz.forever.tact

import java.io.File
import java.io.FilterInputStream
import java.io.IOException
import java.io.InputStream
import java.util.concurrent.ConcurrentLinkedQueue
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference

/**
 * Downloads the current World of Warcraft: Forever client from Blizzard's CDN and lays it out as Blizzard's installer
 * would, in [root]: `.build.info`, `Data/config`, `Data/indices` (the CDN archives' indexes), `Data/data` (the local
 * storage, [CascStorageWriter]) and the game's own files under `_forever_` (from the install manifest).
 *
 * What is installed: the files tagged for [wanted] (Windows, x86_64, enUS, US, text and speech), without the optional
 * packs in [excluded] (Alternate, HighRes, Talebound): about 47 GB for build 70862. It resumes where a stopped run left
 * off (same build), and starts over when Blizzard publishes a newer one. `.build.info` is written last: a folder
 * without it is an unfinished download.
 *
 * Plain JVM (no Android): checked on a desktop against Blizzard's CDN and CascLib.
 */
class ForeverClientInstaller(
    private val root: File,
    private val cdn: TactCdn = TactCdn(),
    private val wanted: Set<String> = DEFAULT_TAGS,
    private val excluded: Set<String> = OPTIONAL_PACKS,
    private val maxPriority: Int = Int.MAX_VALUE,
    private val workers: Int = 32,
    /** Off only in a desktop benchmark that stops long before the disk would fill. */
    private val checkSpace: Boolean = true,
    private val onProgress: (Progress) -> Unit = {},
) {
    data class Progress(val step: String, val done: Long = 0, val total: Long = 0)

    class NotEnoughSpaceException(val needed: Long, val free: Long) :
        IOException("Not enough space for the client: it needs about ${needed shr 20} MB more free, but only ${free shr 20} MB is left.")

    @Volatile private var cancelled = false

    /** Stops a running [install] at the next file; what is written is kept for the next run. */
    fun cancel() { cancelled = true }

    @Volatile private var currentStep = ""

    private fun step(text: String, done: Long = 0, total: Long = 0) { currentStep = text; onProgress(Progress(text, done, total)) }

    /** Downloads and lays out the client (see the class). A failure says the step it happened in. */
    fun install() {
        try {
            installSteps()
        } catch (e: NotEnoughSpaceException) {
            throw e
        } catch (e: Exception) {
            throw IOException("$currentStep: ${e.message ?: e.javaClass.simpleName}", e)
        }
    }

    private fun installSteps() {
        step("Asking Blizzard for the current Forever client")
        val version = cdn.version()
        val servers = cdn.servers()
        val buildText = cdn.get("config", version.buildConfig) { Verify.config(it, version.buildConfig) }
        val cdnText = cdn.get("config", version.cdnConfig) { Verify.config(it, version.cdnConfig) }
        val build = Tact.parseConfig(String(buildText, Charsets.UTF_8))
        val cdnConfig = Tact.parseConfig(String(cdnText, Charsets.UTF_8))
        val subfolder = runCatching { String(cdn.productConfig(version.productConfig), Charsets.UTF_8) }.getOrNull()
            ?.let { SUBFOLDER.find(it)?.groupValues?.get(1) } ?: "_forever_"

        // A complete client of this build is left as it is.
        val info = File(root, ".build.info")
        if (info.isFile && !File(root, STATE).isFile && info.readText().contains(version.buildConfig)) { step("The client is ready"); return }

        // The same build and selection resume; anything else starts over.
        val signature = "$FORMAT ${version.buildConfig} ${wanted.sorted()} ${excluded.sorted()} $maxPriority"
        val state = File(root, STATE)
        if (!state.isFile || state.readText() != signature) {
            root.deleteRecursively()
            root.mkdirs()
            state.writeText(signature)
        }
        val staging = File(root, STAGING).apply { mkdirs() }
        val writer = CascStorageWriter(File(root, "Data/data"))

        val plan = plan(build, staging)
        val targets = plan.targets
        val installKeys = plan.installKeys
        val installFiles = installKeys.keys
        val encodingKey = plan.encodingKey
        val encodingFile = plan.encodingFile

        locate(targets, cdnConfig, staging)
        val placed = HashMap(writer.resume())
        if (cancelled) return

        // Room: what is still to download, the game's files and a margin.
        val total = (0 until targets.count).sumOf { targets.size[it].toLong() }
        val alreadyDone = (0 until targets.count).sumOf { p -> if (placed.containsKey(targets.id[p])) targets.size[p].toLong() else 0L }
        val need = (total - alreadyDone) + targets.count.toLong() * CascStorageWriter.HEADER + installFiles.sumOf { it.size } + (512L shl 20)
        val free = root.usableSpace
        if (checkSpace && free in 1 until need) throw NotEnoughSpaceException(need, free)

        // The encoding table is already here: stored from the staged copy.
        val encodingPos = targets.find(encodingKey.hi, encodingKey.lo)
        if (encodingPos >= 0 && !placed.containsKey(targets.id[encodingPos])) {
            val segment = writer.newSegment()
            placed[targets.id[encodingPos]] = encodingFile.inputStream().buffered(1 shl 20).use { segment.write(targets.id[encodingPos], encodingKey, it, encodingFile.length()) }
            segment.close()
        }

        downloadAll(targets, placed, writer, cdnConfig.getValue("archives"), total)
        if (cancelled) return

        step("Laying out the game's files")
        val game = File(root, subfolder).apply { mkdirs() }
        for ((file, key) in installKeys) {
            val pos = targets.find(key.hi, key.lo)
            val where = placed[targets.id[pos]] ?: throw IOException("${file.name} wasn't downloaded")
            val target = placeFor(game, file.name)
            val part = File(target.path + ".part")
            step("Laying out ${file.name}")
            BlteInputStream(writer.read(where)).use { input -> part.outputStream().buffered(1 shl 20).use { input.copyTo(it) } }
            if (!part.renameTo(target)) { target.delete(); if (!part.renameTo(target)) throw IOException("Couldn't place ${file.name}") }
        }
        File(game, ".flavor.info").writeText("Product Flavor!STRING:0\n${cdn.product}\n")

        step("Finishing the client")
        for ((hash, text) in listOf(version.buildConfig to buildText, version.cdnConfig to cdnText)) {
            File(root, "Data/config/${hash.substring(0, 2)}/${hash.substring(2, 4)}/$hash").apply { parentFile?.mkdirs() }.writeBytes(text)
        }
        writer.writeIndexes((0 until targets.count).mapNotNull { p -> placed[targets.id[p]]?.let { Key16(targets.hi[p], targets.lo[p]) to it } })
        writer.finish()
        staging.deleteRecursively()
        File(root, ".build.info").writeText(buildInfo(version, servers, build))
        state.delete()
        step("The client is ready")
    }

    private class Plan(val targets: Targets, val installKeys: Map<Tact.InstallFile, Key16>, val encodingKey: Key16, val encodingFile: File)

    /**
     * What to store: the selected download-manifest entries (id = manifest index), the build's own tables (encoding,
     * root, install, download, size, vfs) and the game's install files (ids past the manifest's). The 2.2-million-entry
     * manifest lives only in here.
     */
    private fun plan(build: Map<String, List<String>>, staging: File): Plan {
        step("Reading the client's file list")
        val download = BlteInputStream(staged(staging, "download.blte", build.getValue("download")[1], build["download-size"]?.getOrNull(1)?.toLongOrNull()).inputStream().buffered(1 shl 20))
            .use { Tact.parseDownload(it) }
        val install = Tact.parseInstall(Blte.decode(staged(staging, "install.blte", build.getValue("install")[1]).readBytes()))
        val installSelection = install.tags.select(wanted, excluded)
        val installFiles = install.files.filterIndexed { i, _ -> installSelection.selects(i) }

        // The build's own tables are stored too: those named by encoding key, and root (named by content key only).
        val system = LinkedHashMap<String, Key16>()
        val systemByContent = LinkedHashMap<String, Key16>()
        for ((name, values) in build) {
            if (name !in SYSTEM_FILES && !(name.startsWith("vfs-") && !name.endsWith("-size"))) continue
            when {
                values.size >= 2 -> system[name] = Key16.hex(values[1])
                values.size == 1 && values[0].length == 32 -> systemByContent[name] = Key16.hex(values[0])
            }
        }
        val encodingKey = system.getValue("encoding")
        val encodingFile = staged(staging, "encoding.blte", encodingKey.hex(), build["encoding-size"]?.getOrNull(1)?.toLongOrNull())

        step("Reading the encoding table")
        val contentKeys = installFiles.map { it.contentKey }.toSet() + systemByContent.values
        val encoded = BlteInputStream(encodingFile.inputStream().buffered(1 shl 20)).use { Tact.encodingKeys(it, contentKeys) }
        for ((name, ckey) in systemByContent) system[name] = encoded[ckey] ?: throw IOException("The encoding table has no $name")
        val installKeys = installFiles.associateWith { encoded[it.contentKey] ?: throw IOException("The encoding table has no ${it.name}") }

        val selection = download.tags.select(wanted, excluded)
        val targets = Targets(download.size / 2 + 64)
        for (i in 0 until download.size) {
            if (download.priorities[i] <= maxPriority && selection.selects(i)) targets.add(i, download.hi[i], download.lo[i])
        }
        var extra = download.size
        for (key in system.values + installKeys.values) targets.add(extra++, key.hi, key.lo)
        targets.sortAndDedupe()
        return Plan(targets, installKeys, encodingKey, encodingFile)
    }

    /**
     * A build file fetched once into [staging] (kept for a resumed run), checked against its key; a big one ([size]
     * from the build config) over several connections at once.
     */
    private fun staged(staging: File, name: String, ekeyHex: String, size: Long? = null): File {
        val file = File(staging, name)
        val key = Key16.hex(ekeyHex)
        fun good(f: File) = f.isFile && Verify.BlteStream(key).also { v ->
            f.inputStream().use { input -> val b = ByteArray(1 shl 20); while (true) { val n = input.read(b); if (n < 0) break; v.update(b, 0, n) } }
        }.matches()
        if (good(file)) return file
        val part = File(staging, "$name.part")
        if (size != null && size > (16L shl 20)) {
            var attempt = 0
            while (true) {
                cdn.download(ekeyHex, size, part, 8)
                if (good(part)) break
                if (++attempt >= 3) throw CorruptDownloadException("$name came with the wrong content three times")
            }
        } else part.writeBytes(cdn.get("data", ekeyHex) { Verify.blte(it, key) })
        file.delete()
        part.renameTo(file)
        return file
    }

    /** Finds where every target is on the CDN: in an archive (its index) or as a loose file (the file index). */
    private fun locate(targets: Targets, cdnConfig: Map<String, List<String>>, staging: File) {
        val archives = cdnConfig.getValue("archives")
        val indices = File(root, "Data/indices").apply { mkdirs() }
        val done = AtomicLong()
        val failure = AtomicReference<Throwable?>()
        val pool = Executors.newFixedThreadPool(64)
        for ((number, hash) in archives.withIndex()) pool.execute {
            if (failure.get() != null || cancelled) return@execute
            try {
                val file = File(indices, "$hash.index")
                var bytes = if (file.isFile) file.readBytes() else null
                if (bytes == null || !Verify.index(bytes, hash)) {
                    bytes = cdn.get("data", hash, ".index") { Verify.index(it, hash) }
                    val part = File(indices, "$hash.index.part")
                    part.writeBytes(bytes)
                    file.delete()
                    part.renameTo(file)
                }
                Tact.parseIndex(bytes) { data, o, size, offset ->
                    val pos = targets.find(beN(data, o, 8), beN(data, o + 8, 8))
                    // A key in two archives: one thread takes it whole (archive, offset and size together).
                    if (pos >= 0) synchronized(targets) {
                        if (targets.archive[pos] == UNKNOWN) {
                            targets.archive[pos] = number
                            targets.offset[pos] = offset
                            targets.size[pos] = size.toInt()
                        }
                    }
                }
                step("Finding the files on Blizzard's servers", done.incrementAndGet(), archives.size.toLong())
            } catch (e: Throwable) { failure.compareAndSet(null, e) }
        }
        pool.shutdown()
        pool.awaitTermination(7, TimeUnit.DAYS)
        failure.get()?.let { throw it }

        cdnConfig["file-index"]?.firstOrNull()?.let { hash ->
            val file = File(staging, "file-index")
            if (!file.isFile || !Verify.index(file.readBytes(), hash)) file.writeBytes(cdn.get("data", hash, ".index") { Verify.index(it, hash) })
            Tact.parseIndex(file.readBytes()) { data, o, size, _ ->
                val pos = targets.find(beN(data, o, 8), beN(data, o + 8, 8))
                if (pos >= 0 && targets.archive[pos] == UNKNOWN) { targets.archive[pos] = LOOSE; targets.size[pos] = size.toInt() }
            }
        }
        val missing = (0 until targets.count).count { targets.archive[it] == UNKNOWN }
        if (missing > 0) throw IOException("$missing of the client's files aren't on Blizzard's servers (the build may have just changed): try again.")
    }

    /** One piece of work: a span of one archive (neighbouring files read in one request), or a batch of loose files. */
    private class Job(val archive: String?, val positions: List<Int>)

    /**
     * Downloads every missing file with [workers] connections at once, spread over Blizzard's servers. The work is
     * cut into spans of at most [SPAN_MAX] (files close together in an archive, read in one request), so all the
     * connections stay busy to the end. Each worker writes its own segment; its journal records are committed after
     * each job, once the job's data is on disk.
     */
    private fun downloadAll(targets: Targets, placed: MutableMap<Int, CascStorageWriter.Placed>, writer: CascStorageWriter, archives: List<String>, total: Long) {
        val done = AtomicLong((0 until targets.count).sumOf { p -> if (placed.containsKey(targets.id[p])) targets.size[p].toLong() else 0L })
        val byArchive = HashMap<Int, MutableList<Int>>()
        val loose = ArrayList<Int>()
        for (p in 0 until targets.count) {
            if (placed.containsKey(targets.id[p])) continue
            val a = targets.archive[p]
            if (a == LOOSE) loose += p else byArchive.getOrPut(a) { ArrayList() } += p
        }
        val jobs = ConcurrentLinkedQueue<Job>()
        for (a in byArchive.keys.sorted()) {
            val positions = byArchive.getValue(a).sortedBy { targets.offset[it] }
            var i = 0
            while (i < positions.size) {
                var j = i
                val start = targets.offset[positions[i]]
                var end = start + targets.size[positions[i]]
                while (j + 1 < positions.size) {
                    val next = positions[j + 1]
                    val nextStart = targets.offset[next]
                    if (nextStart - end > SPAN_GAP || nextStart + targets.size[next] - start > SPAN_MAX) break
                    end = maxOf(end, nextStart + targets.size[next])
                    j++
                }
                jobs += Job(archives[a], positions.subList(i, j + 1))
                i = j + 1
            }
        }
        for (batch in loose.chunked(16)) jobs += Job(null, batch)

        val failure = AtomicReference<Throwable?>()
        val lastReport = AtomicLong()
        fun progress(bytes: Long) {
            val now = done.addAndGet(bytes)
            val t = System.currentTimeMillis()
            val last = lastReport.get()
            if ((t - last > 300 && lastReport.compareAndSet(last, t)) || now == total) step("Downloading the client", now, total)
        }
        val threads = (0 until workers).map { worker ->
            Thread {
                var segment: CascStorageWriter.Segment? = null
                fun segmentFor(length: Long): CascStorageWriter.Segment {
                    val current = segment
                    if (current != null && current.fits(length)) return current
                    current?.close()
                    return writer.newSegment().also { segment = it }
                }
                try {
                    while (failure.get() == null && !cancelled) {
                        val job = jobs.poll() ?: break
                        if (job.archive == null) {
                            for (p in job.positions) {
                                if (cancelled) break
                                val key = Key16(targets.hi[p], targets.lo[p])
                                val length = targets.size[p].toLong()
                                retrying { attempt ->
                                    cdn.open(key.hex(), 0, length, attempt + worker).use { input ->
                                        placed.putSynced(targets.id[p], segmentFor(length).write(targets.id[p], key, input, length))
                                    }
                                }
                                progress(length)
                            }
                        } else downloadSpan(job.archive, job.positions, worker, targets, placed, ::segmentFor, ::progress)
                        segment?.commit()
                    }
                } catch (e: Throwable) {
                    failure.compareAndSet(null, e)
                } finally { runCatching { segment?.close() } }
            }.apply { start() }
        }
        threads.forEach { it.join() }
        failure.get()?.let { throw it }
    }

    /** One span of an archive in one request; if it breaks off, the rest is asked for again (from the next server). */
    private fun downloadSpan(
        archive: String, span: List<Int>, worker: Int, targets: Targets, placed: MutableMap<Int, CascStorageWriter.Placed>,
        segmentFor: (Long) -> CascStorageWriter.Segment, progress: (Long) -> Unit,
    ) {
        retrying { attempt ->
            val todo = span.filter { !placed.containsSynced(targets.id[it]) }
            if (todo.isEmpty()) return@retrying
            val from = targets.offset[todo.first()]
            val to = todo.maxOf { targets.offset[it] + targets.size[it] }
            cdn.open(archive, from, to - from, attempt + worker).use { raw ->
                val input = java.io.BufferedInputStream(raw, 1 shl 18)
                var cursor = from
                for (p in todo) {
                    if (cancelled) return@retrying
                    val at = targets.offset[p]
                    if (at < cursor) continue // overlapping duplicate: already read past it
                    input.skipFully(at - cursor)
                    val length = targets.size[p].toLong()
                    placed.putSynced(targets.id[p], segmentFor(length).write(targets.id[p], Key16(targets.hi[p], targets.lo[p]), Limited(input, length), length))
                    cursor = at + length
                    progress(length)
                }
            }
        }
    }

    private inline fun retrying(block: (attempt: Int) -> Unit) {
        var attempt = 0
        while (true) {
            try { block(attempt); return } catch (e: IOException) {
                if (++attempt >= TactCdn.RETRIES || cancelled) throw e
                Thread.sleep(TactCdn.backoff(attempt))
            }
        }
    }

    private fun MutableMap<Int, CascStorageWriter.Placed>.putSynced(id: Int, value: CascStorageWriter.Placed) = synchronized(this) { put(id, value) }
    private fun MutableMap<Int, CascStorageWriter.Placed>.containsSynced(id: Int) = synchronized(this) { containsKey(id) }

    private class Limited(input: InputStream, private var left: Long) : FilterInputStream(input) {
        override fun read(): Int = if (left <= 0) -1 else super.read().also { if (it >= 0) left-- }
        override fun read(b: ByteArray, off: Int, len: Int): Int {
            if (left <= 0) return -1
            val n = super.read(b, off, minOf(len.toLong(), left).toInt())
            if (n > 0) left -= n
            return n
        }
        override fun close() {}
    }

    private fun buildInfo(version: TactCdn.Version, servers: TactCdn.Servers, build: Map<String, List<String>>): String {
        // As Blizzard's installer writes them: "Windows x86_64 US? acct-USA? geoip-US? enUS speech?:... text?".
        val locale = wanted.firstOrNull { it.length == 4 && it[0].isLowerCase() && it[2].isUpperCase() } ?: "enUS"
        val region = wanted.firstOrNull { it.length == 2 && it.all(Char::isUpperCase) } ?: "US"
        val platform = wanted.filter { it != locale && it != region && it != "text" && it != "speech" }
        val base = "${platform.joinToString(" ")} $region? acct-${if (region == "US") "USA" else region}? geoip-$region? $locale"
        val installKey = build["install"]?.getOrNull(1).orEmpty()
        val installSize = build["install-size"]?.getOrNull(1).orEmpty()
        val now = java.text.SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", java.util.Locale.US)
            .apply { timeZone = java.util.TimeZone.getTimeZone("UTC") }.format(java.util.Date())
        val header = "Branch!STRING:0|Active!DEC:1|Build Key!HEX:16|CDN Key!HEX:16|Install Key!HEX:16|IM Size!DEC:4|CDN Path!STRING:0|" +
            "CDN Hosts!STRING:0|CDN Servers!STRING:0|Tags!STRING:0|Armadillo!STRING:0|Last Activated!STRING:0|Version!STRING:0|KeyRing!HEX:16|Product!STRING:0"
        val row = listOf(
            cdn.region, "1", version.buildConfig, version.cdnConfig, installKey, installSize, servers.path, servers.hosts,
            servers.listed, "$base speech?:$base text?", "", now, version.name, "", cdn.product,
        ).joinToString("|")
        return "$header\n$row\n"
    }

    /** The files to store, as parallel arrays (a million entries without an object each), sorted by key for lookups. */
    internal class Targets(capacity: Int) {
        var count = 0
        var id = IntArray(capacity); var hi = LongArray(capacity); var lo = LongArray(capacity)
        lateinit var archive: IntArray
        lateinit var offset: LongArray
        lateinit var size: IntArray

        fun add(entryId: Int, h: Long, l: Long) {
            if (count == id.size) { val n = id.size * 2 + 16; id = id.copyOf(n); hi = hi.copyOf(n); lo = lo.copyOf(n) }
            id[count] = entryId; hi[count] = h; lo[count] = l; count++
        }

        private fun cmp(a: Int, b: Int): Int {
            val h = java.lang.Long.compareUnsigned(hi[a], hi[b])
            return if (h != 0) h else java.lang.Long.compareUnsigned(lo[a], lo[b])
        }

        /** Sorts by key (a bottom-up merge sort of positions: no boxing) and drops repeated keys. */
        fun sortAndDedupe() {
            var order = IntArray(count) { it }
            var temp = IntArray(count)
            var width = 1
            while (width < count) {
                var lo0 = 0
                while (lo0 < count) {
                    val mid = minOf(lo0 + width, count); val hi0 = minOf(lo0 + 2 * width, count)
                    var a = lo0; var b = mid; var k = lo0
                    while (a < mid && b < hi0) temp[k++] = if (cmp(order[a], order[b]) <= 0) order[a++] else order[b++]
                    while (a < mid) temp[k++] = order[a++]
                    while (b < hi0) temp[k++] = order[b++]
                    lo0 += 2 * width
                }
                val swap = order; order = temp; temp = swap
                width *= 2
            }
            val nid = IntArray(count); val nhi = LongArray(count); val nlo = LongArray(count)
            var n = 0
            for (p in order) {
                if (n > 0 && nhi[n - 1] == hi[p] && nlo[n - 1] == lo[p]) continue
                nid[n] = id[p]; nhi[n] = hi[p]; nlo[n] = lo[p]; n++
            }
            id = nid.copyOf(n); hi = nhi.copyOf(n); lo = nlo.copyOf(n); count = n
            archive = IntArray(n) { UNKNOWN }; offset = LongArray(n); size = IntArray(n)
        }

        fun find(h: Long, l: Long): Int {
            var low = 0; var high = count - 1
            while (low <= high) {
                val mid = (low + high) ushr 1
                var c = java.lang.Long.compareUnsigned(hi[mid], h)
                if (c == 0) c = java.lang.Long.compareUnsigned(lo[mid], l)
                when { c < 0 -> low = mid + 1; c > 0 -> high = mid - 1; else -> return mid }
            }
            return -1
        }
    }

    companion object {
        val DEFAULT_TAGS = setOf("Windows", "x86_64", "enUS", "US", "text", "speech")
        val OPTIONAL_PACKS = setOf("Alternate", "HighRes", "Talebound")
        private val SYSTEM_FILES = setOf("encoding", "root", "install", "download", "size")
        private val SUBFOLDER = Regex("\"shared_container_default_subfolder\"\\s*:\\s*\"([^\"]+)\"")
        private const val STATE = ".blizz-download"
        /** The download's format: a partial download of another format starts over (2: every file checked against its key). */
        private const val FORMAT = "v2"
        private const val STAGING = ".blizz-staging"
        private const val UNKNOWN = -2
        private const val LOOSE = -1
        private const val LOOSE_JOB = ""
        private const val SPAN_GAP = 1L shl 20
        private const val SPAN_MAX = 32L shl 20

        /** Where a manifest path goes under [base]: `\` separated, directories matched without regard to case (as Windows sees them). */
        fun placeFor(base: File, name: String): File {
            val parts = name.replace('\\', '/').split('/').filter { it.isNotEmpty() && it != "." && it != ".." }
            require(parts.isNotEmpty()) { "Empty path" }
            var dir = base
            for (part in parts.dropLast(1)) {
                dir = dir.listFiles()?.firstOrNull { it.isDirectory && it.name.equals(part, ignoreCase = true) }
                    ?: File(dir, part).also { it.mkdirs() }
            }
            return File(dir, parts.last())
        }
    }
}
