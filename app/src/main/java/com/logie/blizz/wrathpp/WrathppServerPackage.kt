package com.logie.blizz.wrathpp

import com.logie.blizz.BuildConfig
import com.logie.blizz.wow.WowLayout
import org.apache.commons.compress.archivers.tar.TarArchiveInputStream
import org.json.JSONObject
import org.tukaani.xz.XZInputStream
import java.io.File
import java.io.FileNotFoundException
import java.io.FilterInputStream
import java.io.IOException
import java.io.InputStream
import java.net.HttpURLConnection
import java.net.URL
import java.nio.file.Files
import java.security.DigestInputStream
import java.security.MessageDigest
import java.util.concurrent.ExecutionException
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicLong

/**
 * Wrath++'s server (docs/wrathpp): its own build of the realms' AzerothCore with the Wrath++ appearance protocol
 * (`realm/scripts/fetch-wrathpp.sh`, built for arm64 by `.github/workflows/build-wrathpp-server.yml`), attached to this
 * repository's `wrathpp-server` release as `wrathpp-server.tar.xz` with `wrathpp-server.json` (size, SHA-256, unpacked
 * size, format). Downloaded, checked against its SHA-256, unpacked beside and renamed into `files/server-wrathpp`, so a
 * half-download is never run. Only ever writes `server-wrathpp`, `server-wrathpp.new` and the download: never the realms'
 * `server`, their databases or their game.
 *
 * Format 2 (what the release publishes now; `realm/scripts/wrathpp-repack.py`) splits the package into packs, each its
 * own tar.xz: the programs of this realm alone (core), MariaDB and the libraries (runtime), AzerothCore's SQL (sql), the
 * modules' SQL and other data, and each module's client files (optional: Wrath++'s game doesn't put them in its Data).
 * The packs download and unpack at the same time, each hashed as it arrives, and a pack whose files the Wrath+ server
 * folder already holds (same size, same SHA-256) is taken from there instead of downloaded. The release keeps the whole
 * package (format 1) too, so an app that only knows that one still installs; the whole package's SHA-256 stays the
 * installed marker either way.
 *
 * NOT run on a phone. The pure parts ([entryTarget], [parseManifest], [needsInstall]) and the pack install (against a
 * folder of packs) are unit-tested.
 */
object WrathppServerPackage {
    const val RELEASE = "wrathpp-server"
    private const val BASE = "https://github.com/${BuildConfig.UPDATE_REPO}/releases/download/$RELEASE"
    private const val MANIFEST_URL = "$BASE/wrathpp-server.json"
    private const val PACKAGE_URL = "$BASE/wrathpp-server.tar.xz"

    /** The oldest package format this app runs. 1: the first (protocol 1). */
    const val MIN_FORMAT = 1

    /**
     * The oldest server protocol the app's Wrath++ client speaks. Raise it when a change to the client needs a newer
     * server: the installed server is then replaced at the next Play, as when none is installed. Any other newer package
     * waits for the next refresh ([WrathppParts]: once after the app itself updates, or the settings page's button): the
     * user, 18 November 2026: "it downloads then unpacks the server every time I launch ... Just keep it on device". The
     * server is rebuilt and published several times a day, and a Play used to fetch all 251 MB each time.
     */
    const val MIN_PROTOCOL = 1

    /** Written into `server-wrathpp` after a complete install: the package's SHA-256. */
    const val MARKER = "PACKAGE_SHA256"

    /** Written beside [MARKER]: the package's protocol (an install from before it was written is protocol 1). */
    const val PROTOCOL_MARKER = "PACKAGE_PROTOCOL"

    /** A file a shareable pack holds: where (under server/), its size and SHA-256, its mode. */
    data class PackFile(val path: String, val size: Long, val sha256: String, val mode: Int)

    /**
     * One tar.xz of the package ([file] in the release). [optional]: client files of a module that Wrath++'s game
     * doesn't use. [shareable]: its [files] may already be in the Wrath+ server folder; [immutable]: nothing ever
     * writes them, so a found file is hard linked (else copied).
     */
    data class Pack(
        val name: String, val file: String, val size: Long, val sha256: String, val unpacked: Long,
        val optional: Boolean = false, val shareable: Boolean = false, val immutable: Boolean = false,
        val files: List<PackFile> = emptyList(), val dirs: List<String> = emptyList(),
    )

    data class Manifest(
        val size: Long, val sha256: String, val unpacked: Long, val format: Int, val protocol: Int,
        val packs: List<Pack> = emptyList(),
    )

    fun parseManifest(text: String): Manifest {
        val json = JSONObject(text)
        val packs = json.optJSONArray("packs")?.let { array ->
            (0 until array.length()).map { i ->
                val p = array.getJSONObject(i)
                Pack(
                    name = p.getString("name"), file = p.getString("file"), size = p.getLong("size"),
                    sha256 = p.getString("sha256"), unpacked = p.optLong("unpacked"), optional = p.optBoolean("optional"),
                    shareable = p.optBoolean("shareable"), immutable = p.optBoolean("immutable"),
                    files = p.optJSONArray("files")?.let { f ->
                        (0 until f.length()).map { j ->
                            val e = f.getJSONObject(j)
                            PackFile(e.getString("path"), e.getLong("size"), e.getString("sha256"), e.optInt("mode", 420))
                        }
                    }.orEmpty(),
                    dirs = p.optJSONArray("dirs")?.let { d -> (0 until d.length()).map { d.getString(it) } }.orEmpty(),
                )
            }
        }.orEmpty()
        return Manifest(
            size = json.getLong("size"), sha256 = json.getString("sha256"), unpacked = json.optLong("unpacked"),
            format = json.optInt("format", 1), protocol = json.optInt("protocol", 1), packs = packs,
        )
    }

    /** Where the files come from: the release, or (in tests) a folder. */
    fun interface Source {
        @Throws(IOException::class)
        fun open(file: String): InputStream
    }

    /** A file the release doesn't have (yet): the caller may go on to the whole package. */
    class NotPublished(message: String) : FileNotFoundException(message)

    private val release = Source { file -> connect("$BASE/$file").let { c -> object : FilterInputStream(c.inputStream) {
        override fun close() { try { super.close() } finally { c.disconnect() } }
    } } }

    fun manifest(): Manifest = parseManifest(fetchText(MANIFEST_URL))

    fun installedSha(layout: WowLayout): String? =
        File(layout.wrathppServer, MARKER).takeIf { it.isFile }?.readText()?.trim()?.takeIf { it.isNotEmpty() }

    fun installedProtocol(layout: WowLayout): Int =
        File(layout.wrathppServer, PROTOCOL_MARKER).takeIf { it.isFile }?.readText()?.trim()?.toIntOrNull() ?: 1

    /**
     * Whether [published] should be downloaded over what is installed: nothing installed, an unfinished install, or a
     * server too old for this app ([MIN_PROTOCOL]) always; another package only when [update] (the settings page's button).
     * Offline ([published] null) with a server installed: what is installed.
     */
    fun needsInstall(layout: WowLayout, published: Manifest?, update: Boolean = false): Boolean {
        val installed = installedSha(layout)
        if (!layout.hasWrathppServer() || installed == null) return true
        if (published == null) return false
        if (installedProtocol(layout) < MIN_PROTOCOL && published.protocol >= MIN_PROTOCOL) return true
        return update && !published.sha256.equals(installed, ignoreCase = true)
    }

    /** The published package when it is not the installed one (for the settings page), else null; null too when offline or none installed. */
    fun newer(layout: WowLayout): Manifest? {
        val installed = installedSha(layout) ?: return null
        val published = runCatching { manifest() }.getOrNull() ?: return null
        return published.takeUnless { it.sha256.equals(installed, ignoreCase = true) }
    }

    /**
     * Makes sure a usable package is installed: the one there stays ([needsInstall]) unless there is none, or it is older
     * than [MIN_PROTOCOL], or [update] asks for the newest. Offline with a package installed: that one is used. Call off
     * the main thread; [say] gets each step's words and its share done (0..1), often (the caller thins it out).
     * Returns whether the release was reached (false: offline, the installed one used).
     */
    fun ensure(layout: WowLayout, say: (String, Float?) -> Unit, update: Boolean = false): Boolean {
        val published = runCatching { manifest() }.getOrElse { e ->
            if (layout.hasWrathppServer() && installedSha(layout) != null) return false
            throw IOException("Wrath++'s server couldn't be fetched (${e.message ?: e.javaClass.simpleName}). It is published by this app's " +
                "repository (release $RELEASE); check the connection, or that the release exists yet.")
        }
        if (!needsInstall(layout, published, update)) return true
        if (published.format < MIN_FORMAT) throw IOException("Wrath++'s server is being updated. Try again in a few minutes.")
        install(layout, published, say)
        return true
    }

    private fun mb(bytes: Long) = bytes shr 20

    /** Installs the newest package: its packs where it has them (format 2), else the whole of it. */
    internal fun install(layout: WowLayout, manifest: Manifest, say: (String, Float?) -> Unit, source: Source = release) {
        if (manifest.packs.isNotEmpty()) {
            try {
                installPacks(layout, manifest, say, source)
                return
            } catch (e: NotPublished) {
                // A pack the release doesn't have (mid-publish): the whole package, which it keeps.
            }
        }
        installWhole(layout, manifest, say)
    }

    private fun installWhole(layout: WowLayout, manifest: Manifest, say: (String, Float?) -> Unit) {
        val root = layout.root
        val archive = File(root, "wrathpp-server.tar.xz.part")
        say("Downloading Wrath++'s server (step 1 of 4)", 0f)
        download(PACKAGE_URL, archive, manifest.size) { done, total ->
            say("Downloading Wrath++'s server (step 1 of 4): ${mb(done)} / ${mb(total)} MB", if (total > 0) done.toFloat() / total else null)
        }
        val size = archive.length().coerceAtLeast(1)
        val sha = sha256(archive) { read -> say("Checking the download (step 2 of 4): ${mb(read)} / ${mb(size)} MB", read.toFloat() / size) }
        if (!sha.equals(manifest.sha256, ignoreCase = true)) {
            archive.delete()
            throw IOException("Wrath++'s server download didn't match its checksum; try again.")
        }
        if (manifest.unpacked > 0) {
            val need = manifest.unpacked + (256L shl 20)
            val free = root.usableSpace
            if (free in 1 until need) {
                archive.delete()
                throw IOException("Not enough space for Wrath++'s server: it needs about ${need shr 20} MB free, ${free shr 20} MB is left.")
            }
        }
        val staging = File(root, "server-wrathpp.new")
        staging.deleteRecursively()
        val unpacked = manifest.unpacked.takeIf { it > 0 }
        unpack(archive, staging) { written ->
            say("Unpacking Wrath++'s server (step 3 of 4): ${mb(written)}${unpacked?.let { " / ${mb(it)}" }.orEmpty()} MB",
                unpacked?.let { written.toFloat() / it })
        }
        archive.delete()
        finish(layout, staging, manifest)
    }

    /** Checks what was unpacked into [staging] and puts it in place of the installed server, marked with the package's SHA-256. */
    private fun finish(layout: WowLayout, staging: File, manifest: Manifest) {
        val root = layout.root
        val folder = File(staging, "server").takeIf { it.isDirectory } ?: staging
        if (!File(folder, "ctl.sh").isFile || !File(folder, "bin/worldserver").isFile) {
            staging.deleteRecursively()
            throw IOException("Wrath++'s server package has no ctl.sh or world server")
        }
        val target = layout.wrathppServer
        val old = File(root, "server-wrathpp.old")
        old.deleteRecursively()
        if (target.exists() && !target.renameTo(old)) target.deleteRecursively()
        if (!folder.renameTo(target)) {
            folder.copyRecursively(target, overwrite = true)
        }
        old.deleteRecursively()
        staging.deleteRecursively()
        File(target, PROTOCOL_MARKER).writeText(manifest.protocol.toString())
        File(target, MARKER).writeText(manifest.sha256)
    }


    // ---- format 2: the packs

    private const val PACK_MARK_DIR = ".packs"
    private const val STAGING_FOR = ".package-sha256"
    private const val PARALLEL_PACKS = 3

    /** Passes reads through and ignores close: the hash must still read what follows the archive's end. */
    private class NonClosing(input: InputStream) : FilterInputStream(input) {
        override fun close() {}
    }

    /** A stream that counts what passes through it. */
    private class Counting(input: InputStream, private val total: AtomicLong) : FilterInputStream(input) {
        override fun read(): Int = super.read().also { if (it >= 0) total.incrementAndGet() }
        override fun read(b: ByteArray, off: Int, len: Int): Int = super.read(b, off, len).also { if (it > 0) total.addAndGet(it.toLong()) }
    }

    /** The packs an install takes: the ones the game's own copy needs (not the optional client-file packs). */
    fun requiredPacks(manifest: Manifest): List<Pack> = manifest.packs.filter { !it.optional }

    private fun installPacks(layout: WowLayout, manifest: Manifest, say: (String, Float?) -> Unit, source: Source) {
        val root = layout.root
        val staging = File(root, "server-wrathpp.new")
        val stamp = File(staging, STAGING_FOR)
        // An earlier try's finished packs are kept (a drop in the connection costs one pack, not the lot) when it was for this package.
        if (!(stamp.isFile && stamp.readText().trim().equals(manifest.sha256, ignoreCase = true))) {
            staging.deleteRecursively()
            staging.mkdirs()
            stamp.writeText(manifest.sha256)
        }
        val marks = File(staging, PACK_MARK_DIR).apply { mkdirs() }
        val todo = requiredPacks(manifest).filter { !File(marks, it.name).isFile }

        // What the Wrath+ server folder already holds goes in first (its files checked by SHA-256): no download for those.
        val shareFrom = layout.server.takeIf { it.isDirectory }
        val reused = HashSet<String>()
        if (shareFrom != null) {
            for (pack in todo.filter { it.shareable && it.files.isNotEmpty() }) {
                say("Installing Wrath++'s server (step 1 of 2): reusing Wrath+'s ${pack.name} files", null)
                if (reuse(pack, shareFrom, staging)) { File(marks, pack.name).writeText(pack.sha256); reused += pack.name }
            }
        }
        val fetch = todo.filter { it.name !in reused }

        val need = fetch.sumOf { it.unpacked } + (256L shl 20)
        val free = root.usableSpace
        if (free in 1 until need) {
            throw IOException("Not enough space for Wrath++'s server: it needs about ${need shr 20} MB free, ${free shr 20} MB is left.")
        }

        val total = fetch.sumOf { it.size }
        val received = AtomicLong()
        if (fetch.isNotEmpty()) {
            val pool = Executors.newFixedThreadPool(PARALLEL_PACKS.coerceAtMost(fetch.size))
            try {
                val jobs = fetch.sortedByDescending { it.size }.map { pack -> pool.submit { fetchPack(pack, staging, marks, source, received) } }
                while (jobs.any { !it.isDone }) {
                    say("Installing Wrath++'s server (step 1 of 2): ${mb(received.get())} / ${mb(total)} MB",
                        if (total > 0) (received.get().toFloat() / total).coerceAtMost(1f) else null)
                    Thread.sleep(200)
                }
                try { jobs.forEach { it.get() } } catch (e: ExecutionException) { throw e.cause ?: e }
            } finally {
                pool.shutdownNow()
            }
        }
        finish(layout, staging, manifest)
    }

    /** Downloads one pack and unpacks it as it arrives, hashing the bytes that came; a pack that doesn't match its SHA-256 is an error. */
    private fun fetchPack(pack: Pack, staging: File, marks: File, source: Source, received: AtomicLong) {
        val digest = MessageDigest.getInstance("SHA-256")
        source.open(pack.file).use { raw ->
            val hashed = DigestInputStream(Counting(raw, received), digest)
            unpackStream(NonClosing(hashed).buffered(1 shl 16), staging) { }
            // What follows the archive's end (padding) is part of the file: read to the end so the hash covers all of it.
            hashed.copyTo(java.io.OutputStream.nullOutputStream())
        }
        val sha = digest.digest().joinToString("") { "%02x".format(it) }
        if (!sha.equals(pack.sha256, ignoreCase = true)) {
            throw IOException("Wrath++'s server (${pack.name}) didn't match its checksum; try again.")
        }
        File(marks, pack.name).writeText(sha)
    }

    /**
     * Takes a shareable pack's files from [from] (the Wrath+ server folder) when every one is there with the same size and
     * SHA-256: hard linked for packs nothing writes ([Pack.immutable]), else copied. All or none: false (nothing put in)
     * if any file differs, so the pack is downloaded whole.
     */
    internal fun reuse(pack: Pack, from: File, staging: File): Boolean {
        val sources = ArrayList<Pair<PackFile, File>>(pack.files.size)
        for (f in pack.files) {
            val source = entryTarget(from, f.path) ?: return false
            if (!source.isFile || source.length() != f.size) return false
            sources += f to source
        }
        for ((f, source) in sources) if (!sha256(source).equals(f.sha256, ignoreCase = true)) return false
        for (dir in pack.dirs) entryTarget(staging, "server/$dir")?.mkdirs()
        for ((f, source) in sources) {
            val target = entryTarget(staging, "server/${f.path}") ?: return false
            target.parentFile?.mkdirs()
            target.delete()
            if (pack.immutable) {
                try { Files.createLink(target.toPath(), source.toPath()) } catch (e: Exception) { source.copyTo(target, overwrite = true) }
            } else {
                source.copyTo(target, overwrite = true)
                if (f.mode and 0b001_000_000 != 0) target.setExecutable(true, false)
            }
        }
        return true
    }

    /** Where a tar entry goes under [base], refusing any path that would escape it (never absolute, never `..`). */
    fun entryTarget(base: File, name: String): File? {
        val clean = name.removePrefix("./")
        if (clean.isEmpty() || clean.startsWith("/") || clean.split('/').any { it == ".." }) return null
        return File(base, clean)
    }

    internal fun unpack(archive: File, dest: File, onBytes: (Long) -> Unit) =
        unpackStream(archive.inputStream().buffered(), dest, onBytes)

    /** Unpacks a tar.xz read from [raw] under [dest]. Does not close [raw]'s own source beyond closing the stream. */
    private fun unpackStream(raw: InputStream, dest: File, onBytes: (Long) -> Unit) {
        dest.mkdirs()
        var written = 0L
        var reported = 0L
        TarArchiveInputStream(XZInputStream(raw)).use { tar ->
            val buffer = ByteArray(1 shl 16)
            while (true) {
                val entry = tar.nextEntry ?: break
                val target = entryTarget(dest, entry.name) ?: continue
                if (entry.isDirectory) { target.mkdirs(); continue }
                target.parentFile?.mkdirs()
                if (entry.isSymbolicLink) {
                    // Relative links of the package's own (musl's libc.so → its loader, MariaDB's); never an absolute one.
                    val link = File(entry.linkName)
                    if (link.isAbsolute) continue
                    runCatching { java.nio.file.Files.createSymbolicLink(target.toPath(), link.toPath()) }
                    continue
                }
                if (entry.isLink) {
                    val source = entryTarget(dest, entry.linkName) ?: continue
                    if (source.isFile) source.copyTo(target, overwrite = true)
                    continue
                }
                target.outputStream().buffered().use { out ->
                    while (true) {
                        val n = tar.read(buffer)
                        if (n < 0) break
                        out.write(buffer, 0, n)
                        written += n
                        if (written - reported >= (4L shl 20)) { reported = written; onBytes(written) }
                    }
                }
                if (entry.mode and 0b001_000_000 != 0) target.setExecutable(true, false)
            }
        }
        onBytes(written)
    }

    private fun download(url: String, dest: File, expectedSize: Long, onProgress: (Long, Long) -> Unit) {
        dest.parentFile?.mkdirs()
        val connection = connect(url)
        val total = connection.contentLengthLong.takeIf { it > 0 } ?: expectedSize
        var done = 0L
        connection.inputStream.use { input ->
            dest.outputStream().buffered().use { out ->
                val buffer = ByteArray(1 shl 16)
                while (true) {
                    val n = input.read(buffer)
                    if (n < 0) break
                    out.write(buffer, 0, n)
                    done += n
                    onProgress(done, total)
                }
            }
        }
        connection.disconnect()
    }

    private fun fetchText(url: String): String = connect(url).let { c ->
        c.inputStream.bufferedReader().use { it.readText() }.also { c.disconnect() }
    }

    private fun connect(url: String): HttpURLConnection {
        var current = URL(url)
        repeat(6) {
            val c = (current.openConnection() as HttpURLConnection).apply {
                connectTimeout = 30_000; readTimeout = 60_000; instanceFollowRedirects = false
                setRequestProperty("User-Agent", "Blizzard-Launcher")
            }
            when (c.responseCode) {
                in 300..399 -> { current = URL(current, c.getHeaderField("Location")); c.disconnect() }
                HttpURLConnection.HTTP_OK -> return c
                HttpURLConnection.HTTP_NOT_FOUND -> { c.disconnect(); throw NotPublished("Not published: ${current.path.substringAfterLast('/')}") }
                else -> { val code = c.responseCode; c.disconnect(); throw IOException("Download failed ($code)") }
            }
        }
        throw IOException("Too many redirects")
    }

    internal fun sha256(file: File, onRead: (Long) -> Unit = {}): String {
        val digest = MessageDigest.getInstance("SHA-256")
        var read = 0L
        file.inputStream().buffered().use { input ->
            val buffer = ByteArray(1 shl 16)
            while (true) { val n = input.read(buffer); if (n < 0) break; digest.update(buffer, 0, n); read += n; onRead(read) }
        }
        return digest.digest().joinToString("") { "%02x".format(it) }
    }
}
