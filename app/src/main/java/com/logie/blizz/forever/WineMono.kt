package com.logie.blizz.forever

import com.logie.blizz.BuildConfig
import org.apache.commons.compress.archivers.tar.TarArchiveInputStream
import org.json.JSONObject
import org.tukaani.xz.XZInputStream
import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest

/**
 * The .NET runtime (wine-mono) for the Forever Launcher. The launcher is a WinForms (.NET 4) program, and
 * Winlator's Wine ships without mono, so a .NET program finds no runtime and does not start. This puts the
 * runtime in place by copying its files into the container's Windows: `C:\windows\mono\mono-2.0`. Wine 10.10
 * finds mono there by path alone — no installer is run and no registry is written, so there is no first-run
 * race (an installer finishing while the launcher is already starting is what left the launcher's window black).
 *
 * The runtime is `wine-mono.tar.xz` on this repository's `wine-mono` release (built by
 * `.github/workflows/build-wine-mono.yml` from the official wine-mono MSI), checked against `wine-mono.json`'s
 * SHA-256 before it is unpacked. Proven on the desktop test rig: the launcher's window renders and reaches its
 * server tab from a clean Wine prefix with only this tree placed (no registry, no Microsoft.NET).
 *
 * NOT run on a phone. The pure parts ([entryTarget]) are unit-tested.
 */
object WineMono {
    private const val BASE = "https://github.com/${BuildConfig.UPDATE_REPO}/releases/download/wine-mono"
    private const val MANIFEST_URL = "$BASE/wine-mono.json"
    private const val PACKAGE_URL = "$BASE/wine-mono.tar.xz"

    /** The marker written into the mono folder once a complete tree is in place (its release SHA-256). */
    private const val MARKER = ".blizz-wine-mono"

    data class Manifest(val size: Long, val sha256: String, val unpacked: Long)

    fun manifest(): Manifest {
        val json = JSONObject(fetchText(MANIFEST_URL))
        return Manifest(json.getLong("size"), json.getString("sha256"), json.optLong("unpacked"))
    }

    /** The mono folder in a container's Windows ([driveC] is `<container>/.wine/drive_c`). */
    private fun monoDir(driveC: File) = File(driveC, "windows/mono")

    /** The release SHA-256 the mono tree in place was unpacked from, or null when none is in place. */
    private fun installedSha(driveC: File): String? =
        File(monoDir(driveC), MARKER).takeIf { it.isFile }?.readText()?.trim()?.takeIf { it.isNotEmpty() }

    /** Whether a complete mono tree is in place (the marker is written only after a full unpack). */
    fun installed(driveC: File): Boolean =
        installedSha(driveC) != null && File(monoDir(driveC), "mono-2.0").isDirectory

    /** Removes the runtime from [driveC] so the next Play provisions it afresh (a repair). */
    fun remove(driveC: File) {
        monoDir(driveC).deleteRecursively()
        File(driveC, "windows/mono.new").deleteRecursively()
        File(driveC, "windows/mono.old").deleteRecursively()
    }

    /**
     * Puts the .NET runtime in [driveC] if it is not already there: downloads `wine-mono.tar.xz` (checking its
     * SHA-256) and unpacks it into `C:\windows\mono`. Call off the main thread. [onProgress] is called with
     * (bytes so far, total) during the download. Does nothing when the current runtime is already in place.
     */
    fun ensure(driveC: File, onProgress: (Long, Long) -> Unit = { _, _ -> }) {
        val manifest = manifest()
        if (installedSha(driveC).equals(manifest.sha256, ignoreCase = true) && File(monoDir(driveC), "mono-2.0").isDirectory) return

        File(driveC, "windows").mkdirs()
        val archive = File(driveC, "wine-mono.tar.xz.part")
        download(PACKAGE_URL, archive, manifest.size, onProgress)
        val sha = sha256(archive)
        if (!sha.equals(manifest.sha256, ignoreCase = true)) {
            archive.delete()
            throw IllegalStateException("The .NET runtime download didn't match its checksum; try again.")
        }
        // The tree is replaced whole: unpack beside the old one, swap it in, so a half-unpack is never left runnable.
        val staging = File(driveC, "windows/mono.new")
        staging.deleteRecursively()
        val old = File(driveC, "windows/mono.old")
        old.deleteRecursively()
        unpackMonoInto(archive, staging)
        archive.delete()
        val target = monoDir(driveC)
        if (target.exists() && !target.renameTo(old)) target.deleteRecursively()
        if (!staging.renameTo(target)) {
            staging.copyRecursively(target, overwrite = true)
            staging.deleteRecursively()
        }
        old.deleteRecursively()
        File(target, MARKER).writeText(manifest.sha256)
    }

    /** Where a tar entry goes under [base], refusing any path that would escape it (never absolute, never `..`). */
    fun entryTarget(base: File, name: String): File? {
        val clean = name.removePrefix("./")
        if (clean.isEmpty() || clean.startsWith("/") || clean.split('/').any { it == ".." }) return null
        return File(base, clean)
    }

    /**
     * The path a tar entry takes under `windows/mono`, with the archive's top `mono/` folder stripped, or null to
     * skip it (the top folder itself, or a name that would escape). The archive's entries are `mono/mono-2.0/...`.
     */
    fun monoEntryRel(name: String): String? {
        val clean = name.removePrefix("./")
        if (clean != "mono" && !clean.startsWith("mono/")) return null
        val rel = if (clean == "mono") "" else clean.removePrefix("mono/")
        if (rel.isEmpty() || rel.startsWith("/") || rel.split('/').any { it == ".." }) return null
        return rel
    }

    /** Unpacks the archive (whose entries are `mono/...`) into [dest] (the future `windows/mono`), stripping the top `mono/`. */
    private fun unpackMonoInto(archive: File, dest: File) {
        dest.mkdirs()
        TarArchiveInputStream(XZInputStream(archive.inputStream().buffered())).use { tar ->
            val buffer = ByteArray(1 shl 16)
            while (true) {
                val entry = tar.nextEntry ?: break
                val rel = monoEntryRel(entry.name) ?: continue
                val target = entryTarget(dest, rel) ?: continue
                if (entry.isDirectory) { target.mkdirs(); continue }
                if (entry.isSymbolicLink) {
                    runCatching { java.nio.file.Files.createSymbolicLink(target.toPath(), File(entry.linkName).toPath()) }
                        .onFailure { target.parentFile?.mkdirs() }
                    continue
                }
                target.parentFile?.mkdirs()
                target.outputStream().buffered().use { out ->
                    while (true) { val n = tar.read(buffer); if (n < 0) break; out.write(buffer, 0, n) }
                }
            }
        }
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

    /** [url]'s bytes (redirects followed, as GitHub's release downloads need), at most [max]; null on any failure. */
    internal fun fetchBytes(url: String, max: Int = 40_000_000): ByteArray? = runCatching {
        val c = connect(url)
        try {
            c.inputStream.use { input ->
                val out = java.io.ByteArrayOutputStream()
                val buffer = ByteArray(1 shl 16)
                while (true) {
                    val n = input.read(buffer); if (n < 0) break
                    out.write(buffer, 0, n)
                    if (out.size() > max) return@runCatching null
                }
                out.toByteArray()
            }
        } finally { c.disconnect() }
    }.getOrNull()

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
                else -> { val code = c.responseCode; c.disconnect(); throw IllegalStateException("The .NET runtime download failed ($code)") }
            }
        }
        throw IllegalStateException("Too many redirects")
    }

    private fun sha256(file: File): String {
        val digest = MessageDigest.getInstance("SHA-256")
        file.inputStream().buffered().use { input ->
            val buffer = ByteArray(1 shl 16)
            while (true) { val n = input.read(buffer); if (n < 0) break; digest.update(buffer, 0, n) }
        }
        return digest.digest().joinToString("") { "%02x".format(it) }
    }
}
