package com.logie.blizz.forever

import android.content.Context
import com.logie.blizz.BuildConfig
import org.apache.commons.compress.archivers.tar.TarArchiveInputStream
import org.json.JSONObject
import org.tukaani.xz.XZInputStream
import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest

/**
 * Downloads and unpacks the Forever realm's server package (`forever-server.tar.xz`, built by
 * `realm/scripts/package-trinity-forever.sh` and attached to this repository's `forever-server`
 * release). The download is checked against `forever-server.json`'s SHA-256 before it is unpacked,
 * and unpacked beside the old server and renamed into place, so a half-download is never run.
 *
 * NOT run on a phone. The pure parts ([entryTarget]) are unit-tested.
 */
object ForeverServerPackage {
    /** The `forever-server` release's assets, on this repository. */
    private const val BASE = "https://github.com/${BuildConfig.UPDATE_REPO}/releases/download/forever-server"
    private const val MANIFEST_URL = "$BASE/forever-server.json"
    private const val PACKAGE_URL = "$BASE/forever-server.tar.xz"

    data class Manifest(val size: Long, val sha256: String, val clientBuild: Int, val unpacked: Long, val format: Int)

    /**
     * The oldest package format this app installs. 2: the seed database has the branch's updates applied (realm 70 and
     * the client builds) and sql/old is left out. Format 1 packages were broken (their updates never ran).
     */
    const val MIN_FORMAT = 2

    fun manifest(): Manifest {
        val json = JSONObject(fetchText(MANIFEST_URL))
        return Manifest(
            json.getLong("size"), json.getString("sha256"), json.optInt("client_build"), json.optLong("unpacked"),
            json.optInt("format", 1),
        )
    }

    /** Whether a package is unpacked and ready to run. */
    fun installed(context: Context) = ForeverLayout.of(context).ctl.isFile

    /** The SHA-256 of the package the server folder was unpacked from (written after a complete install). */
    private const val MARKER = "PACKAGE_SHA256"

    private fun installedSha(layout: ForeverLayout): String? =
        File(layout.server, MARKER).takeIf { it.isFile }?.readText()?.trim()?.takeIf { it.isNotEmpty() }

    /**
     * Whether a different package is published than the one installed (a fixed or newer realm). False when the
     * manifest can't be read (offline): the installed realm is used as it is.
     */
    fun outdated(context: Context): Boolean {
        val installed = installedSha(ForeverLayout.of(context))
        return runCatching { !manifest().sha256.equals(installed, ignoreCase = true) }.getOrDefault(false)
    }

    /**
     * Downloads the package (checking its SHA-256) and unpacks it to `files/forever/server`. Call
     * off the main thread. [onStage] names the current step (download, checking, unpacking) so the UI
     * doesn't look stuck at 100% while the large archive is verified and unpacked; [onProgress] is
     * called with (bytes so far, total) during the download.
     */
    fun install(context: Context, onStage: (String) -> Unit = {}, onProgress: (Long, Long) -> Unit) {
        val layout = ForeverLayout.of(context)
        layout.root.mkdirs()
        val manifest = manifest()
        if (manifest.format < MIN_FORMAT) {
            throw IllegalStateException("The realm server is being updated. Try again in a few minutes.")
        }
        // The first package (from before packages were versioned) shipped a database its updates were never applied to:
        // no realm 70, so no realm could have run from it. It goes whole, with the database made from it, which also
        // frees its ~6.5 GB before the new download. Later upgrades keep the database (it holds the characters).
        if (layout.server.isDirectory && installedSha(layout) == null) {
            onStage("Removing the previous realm server")
            layout.server.deleteRecursively()
            layout.databases.deleteRecursively()
        }
        val archive = File(layout.root, "forever-server.tar.xz.part")
        onStage("Downloading the realm server")
        download(PACKAGE_URL, archive, manifest.size, onProgress)
        onStage("Checking the download")
        val sha = sha256(archive)
        if (!sha.equals(manifest.sha256, ignoreCase = true)) {
            archive.delete()
            throw IllegalStateException("The download didn't match its checksum; try again.")
        }
        // Unpacking the xz archive expands it several times over; fail early and clearly if the phone is short on space.
        if (manifest.unpacked > 0) {
            val need = manifest.unpacked + (256L shl 20)
            val free = layout.root.usableSpace
            if (free in 1 until need) {
                archive.delete()
                throw IllegalStateException("Not enough space to set up the realm: it needs about ${need shr 20} MB free, but only ${free shr 20} MB is left. Free some space and try again.")
            }
        }
        val staging = File(layout.root, "server.new")
        staging.deleteRecursively()
        val total = manifest.unpacked.takeIf { it > 0 }
        unpack(archive, staging) { written ->
            onStage(if (total != null) "Unpacking the realm server… ${written shr 20} / ${total shr 20} MB" else "Unpacking the realm server… ${written shr 20} MB")
        }
        archive.delete()
        // The package is a single top folder "server"; put its contents at files/forever/server.
        val unpackedServer = File(staging, "server").takeIf { it.isDirectory } ?: staging
        val target = layout.server
        File(layout.root, "server.old").deleteRecursively()
        if (target.exists() && !target.renameTo(File(layout.root, "server.old"))) target.deleteRecursively()
        if (!unpackedServer.renameTo(target)) {
            unpackedServer.copyRecursively(target, overwrite = true)
            staging.deleteRecursively()
        }
        File(layout.root, "server.old").deleteRecursively()
        staging.deleteRecursively()
        ForeverCtl.makeExecutable(layout)
        File(layout.server, MARKER).writeText(manifest.sha256)
    }

    /** Where a tar entry goes under [base], refusing any path that would escape it (never absolute, never `..`). */
    fun entryTarget(base: File, name: String): File? {
        val clean = name.removePrefix("./")
        if (clean.isEmpty() || clean.startsWith("/") || clean.split('/').any { it == ".." }) return null
        return File(base, clean)
    }

    private fun unpack(archive: File, dest: File, onBytes: (Long) -> Unit = {}) {
        dest.mkdirs()
        var written = 0L
        var lastReport = 0L
        TarArchiveInputStream(XZInputStream(archive.inputStream().buffered())).use { tar ->
            val buffer = ByteArray(1 shl 16)
            while (true) {
                val entry = tar.nextEntry ?: break
                val target = entryTarget(dest, entry.name) ?: continue
                if (entry.isDirectory) { target.mkdirs(); continue }
                if (entry.isSymbolicLink) {
                    // Rebuild links (musl's libc.so.1 → ld-musl, MariaDB's): relative, inside the package.
                    runCatching { java.nio.file.Files.createSymbolicLink(target.toPath(), File(entry.linkName).toPath()) }
                        .onFailure { target.parentFile?.mkdirs() }
                    continue
                }
                target.parentFile?.mkdirs()
                target.outputStream().buffered().use { out ->
                    while (true) {
                        val n = tar.read(buffer)
                        if (n < 0) break
                        out.write(buffer, 0, n)
                        written += n
                        // Report at most every ~16 MB so the UI advances without flooding.
                        if (written - lastReport >= (16L shl 20)) { lastReport = written; onBytes(written) }
                    }
                }
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
                else -> { val code = c.responseCode; c.disconnect(); throw IllegalStateException("Download failed ($code)") }
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
