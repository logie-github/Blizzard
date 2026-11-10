package com.logie.blizz.wrathpp

import com.logie.blizz.BuildConfig
import com.logie.blizz.wow.WowLayout
import org.apache.commons.compress.archivers.tar.TarArchiveInputStream
import org.json.JSONObject
import org.tukaani.xz.XZInputStream
import java.io.File
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest

/**
 * Wrath++'s server (docs/wrathpp): its own build of the realms' AzerothCore with the Wrath++ appearance protocol
 * (`realm/scripts/fetch-wrathpp.sh`, built for arm64 by `.github/workflows/build-wrathpp-server.yml`), attached to this
 * repository's `wrathpp-server` release as `wrathpp-server.tar.xz` with `wrathpp-server.json` (size, SHA-256, unpacked
 * size, format). Downloaded, checked against its SHA-256, unpacked beside and renamed into `files/server-wrathpp`, so a
 * half-download is never run. Only ever writes `server-wrathpp`, `server-wrathpp.new` and the download: never the realms'
 * `server`, their databases or their game.
 *
 * NOT run on a phone. The pure parts ([entryTarget], [parseManifest], [needsInstall]) are unit-tested.
 */
object WrathppServerPackage {
    const val RELEASE = "wrathpp-server"
    private const val BASE = "https://github.com/${BuildConfig.UPDATE_REPO}/releases/download/$RELEASE"
    private const val MANIFEST_URL = "$BASE/wrathpp-server.json"
    private const val PACKAGE_URL = "$BASE/wrathpp-server.tar.xz"

    /** The oldest package format this app runs. 1: the first (protocol 1). */
    const val MIN_FORMAT = 1

    /** Written into `server-wrathpp` after a complete install: the package's SHA-256. */
    const val MARKER = "PACKAGE_SHA256"

    data class Manifest(val size: Long, val sha256: String, val unpacked: Long, val format: Int, val protocol: Int)

    fun parseManifest(text: String): Manifest {
        val json = JSONObject(text)
        return Manifest(
            size = json.getLong("size"), sha256 = json.getString("sha256"), unpacked = json.optLong("unpacked"),
            format = json.optInt("format", 1), protocol = json.optInt("protocol", 1),
        )
    }

    fun manifest(): Manifest = parseManifest(fetchText(MANIFEST_URL))

    fun installedSha(layout: WowLayout): String? =
        File(layout.wrathppServer, MARKER).takeIf { it.isFile }?.readText()?.trim()?.takeIf { it.isNotEmpty() }

    /** Whether [published] should be downloaded over what is installed (nothing, an unfinished install, another package). */
    fun needsInstall(layout: WowLayout, published: Manifest?): Boolean {
        val installed = installedSha(layout)
        if (!layout.hasWrathppServer() || installed == null) return true
        return published != null && !published.sha256.equals(installed, ignoreCase = true)
    }

    /**
     * Makes sure the newest package is installed. Offline with a package installed: that one is used. Call off the main
     * thread; [say] gets each step's words and its share done (0..1), often (the caller thins it out).
     */
    fun ensure(layout: WowLayout, say: (String, Float?) -> Unit) {
        val published = runCatching { manifest() }.getOrElse { e ->
            if (layout.hasWrathppServer() && installedSha(layout) != null) return
            throw IOException("Wrath++'s server couldn't be fetched (${e.message ?: e.javaClass.simpleName}). It is published by this app's " +
                "repository (release $RELEASE); check the connection, or that the release exists yet.")
        }
        if (!needsInstall(layout, published)) return
        if (published.format < MIN_FORMAT) throw IOException("Wrath++'s server is being updated. Try again in a few minutes.")
        install(layout, published, say)
    }

    private fun mb(bytes: Long) = bytes shr 20

    private fun install(layout: WowLayout, manifest: Manifest, say: (String, Float?) -> Unit) {
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
        File(target, MARKER).writeText(manifest.sha256)
    }

    /** Where a tar entry goes under [base], refusing any path that would escape it (never absolute, never `..`). */
    fun entryTarget(base: File, name: String): File? {
        val clean = name.removePrefix("./")
        if (clean.isEmpty() || clean.startsWith("/") || clean.split('/').any { it == ".." }) return null
        return File(base, clean)
    }

    private fun unpack(archive: File, dest: File, onBytes: (Long) -> Unit) {
        dest.mkdirs()
        var written = 0L
        var reported = 0L
        TarArchiveInputStream(XZInputStream(archive.inputStream().buffered())).use { tar ->
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
                else -> { val code = c.responseCode; c.disconnect(); throw IOException("Download failed ($code)") }
            }
        }
        throw IOException("Too many redirects")
    }

    private fun sha256(file: File, onRead: (Long) -> Unit = {}): String {
        val digest = MessageDigest.getInstance("SHA-256")
        var read = 0L
        file.inputStream().buffered().use { input ->
            val buffer = ByteArray(1 shl 16)
            while (true) { val n = input.read(buffer); if (n < 0) break; digest.update(buffer, 0, n); read += n; onRead(read) }
        }
        return digest.digest().joinToString("") { "%02x".format(it) }
    }
}
