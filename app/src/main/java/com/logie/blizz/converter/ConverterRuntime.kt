package com.logie.blizz.converter

import com.logie.blizz.BuildConfig
import com.logie.blizz.wrathpp.WrathppServerPackage
import org.json.JSONObject
import java.io.File
import java.io.IOException
import java.io.RandomAccessFile
import java.net.HttpURLConnection
import java.net.URL

/**
 * The Converter's runtime on the phone (`realm/scripts/package-converter-runtime.sh`, `.github/workflows/build-converter-runtime.yml`): Python 3 with numpy and
 * Pillow for arm64 musl, the catabackport tool, the launcher's driver (`realm/warcraft/converter/convert.py`) and the pinned Converter, in the release
 * `converter-runtime` of this repository. Downloaded when the Converter is first used (carrying on from a part after a dropped connection), checked against
 * its SHA-256, unpacked beside and renamed into `files/converter-runtime`, so a half-install is never run. It stays: a newer package is fetched when the
 * card's Update is tapped, never at every start. NOT run on a phone: the pure parts ([isInstalled], [paths]) are unit-tested.
 */
object ConverterRuntime {
    const val RELEASE = "converter-runtime"
    const val MARKER = ".installed"
    private const val BASE = "https://github.com/${BuildConfig.UPDATE_REPO}/releases/download/$RELEASE"

    data class Manifest(val size: Long, val sha256: String, val unpacked: Long)

    /** The runtime's folder and the files the driver is run from, under the app's `files`. */
    class Paths(val root: File, val output: File = File(root, "converter")) {
        val folder = File(root, "converter-runtime")
        val python = File(folder, "bin/python3")
        val driver = File(folder, "repo/realm/warcraft/converter/convert.py")
        val tool = File(folder, "repo/realm/warcraft/tools")
    }

    /** [filesDir]: where the runtime is kept; [output]: where the results go (the Wrath++ layout's `converter`: within its reach). */
    fun paths(filesDir: File, output: File = File(filesDir, "converter")) = Paths(filesDir, output)

    fun installedSha(p: Paths): String? = File(p.folder, MARKER).takeIf { it.isFile }?.readText()?.trim()?.takeIf { it.length == 64 }

    fun isInstalled(p: Paths): Boolean = installedSha(p) != null && p.python.isFile && p.driver.isFile

    fun manifest(): Manifest {
        val j = JSONObject(fetchText("$BASE/converter-runtime.json"))
        return Manifest(j.getLong("size"), j.getString("sha256"), j.optLong("unpacked"))
    }

    /** Makes sure a runtime is in: nothing to do when one is (unless [update]); else downloads, checks and unpacks the published one. Off the main thread. */
    fun ensure(p: Paths, update: Boolean = false, say: (String, Float?) -> Unit) {
        if (isInstalled(p) && !update) return
        val published = runCatching { manifest() }.getOrElse { e ->
            if (isInstalled(p)) return
            throw IOException("The converter's runtime couldn't be fetched (${e.message ?: e.javaClass.simpleName}). It is published by this app's repository " +
                "(release $RELEASE); check the connection, or that the release exists yet.")
        }
        if (isInstalled(p) && installedSha(p).equals(published.sha256, ignoreCase = true)) return
        val archive = File(p.root, "converter-runtime.tar.xz.part")
        val need = (published.size - archive.length().coerceAtMost(published.size)) + published.unpacked + (256L shl 20)
        val free = p.root.usableSpace
        if (free in 1 until need) throw IOException("Not enough space for the converter's runtime: about ${need shr 20} MB free is needed, ${free shr 20} MB is left.")
        say("Downloading the converter's runtime", 0f)
        download("$BASE/converter-runtime.tar.xz", archive, published.size) { done ->
            say("Downloading the converter's runtime: ${done shr 20} / ${published.size shr 20} MB", done.toFloat() / published.size)
        }
        val size = archive.length().coerceAtLeast(1)
        val sha = WrathppServerPackage.sha256(archive) { read -> say("Checking the converter's runtime: ${read shr 20} / ${size shr 20} MB", read.toFloat() / size) }
        if (!sha.equals(published.sha256, ignoreCase = true)) {
            archive.delete()
            throw IOException("The converter's runtime download didn't match its checksum; try again.")
        }
        val staging = File(p.root, "converter-runtime.new")
        staging.deleteRecursively()
        try {
            WrathppServerPackage.unpack(archive, staging) { written -> say("Unpacking the converter's runtime: ${written shr 20} MB", published.unpacked.takeIf { it > 0 }?.let { written.toFloat() / it }) }
            val folder = File(staging, "converter-runtime").takeIf { it.isDirectory } ?: staging
            if (!File(folder, "bin/python3").isFile) throw IOException("Not the converter's runtime")
            for (dir in listOf("bin", "lib", "python/bin")) File(folder, dir).walkTopDown().filter { it.isFile }.forEach { it.setExecutable(true, false) }
            File(folder, MARKER).writeText(published.sha256)
            val old = File(p.root, "converter-runtime.old")
            old.deleteRecursively()
            if (p.folder.exists() && !p.folder.renameTo(old)) p.folder.deleteRecursively()
            if (!folder.renameTo(p.folder)) folder.copyRecursively(p.folder, overwrite = true)
            old.deleteRecursively()
        } finally {
            staging.deleteRecursively()
        }
        archive.delete()
    }

    private fun fetchText(url: String): String {
        val c = open(url, 0)
        return c.inputStream.bufferedReader().use { it.readText() }.also { c.disconnect() }
    }

    private fun open(url: String, from: Long): HttpURLConnection {
        var current = URL(url)
        repeat(6) {
            val c = (current.openConnection() as HttpURLConnection).apply {
                connectTimeout = 30_000; readTimeout = 60_000; instanceFollowRedirects = false
                setRequestProperty("User-Agent", "Blizzard-Launcher")
                if (from > 0) setRequestProperty("Range", "bytes=$from-")
            }
            when (c.responseCode) {
                in 300..399 -> { current = URL(current, c.getHeaderField("Location")); c.disconnect() }
                HttpURLConnection.HTTP_OK, HttpURLConnection.HTTP_PARTIAL -> return c
                else -> { val code = c.responseCode; c.disconnect(); throw IOException("Download failed ($code)") }
            }
        }
        throw IOException("Too many redirects")
    }

    private fun download(url: String, dest: File, expected: Long, onProgress: (Long) -> Unit) {
        dest.parentFile?.mkdirs()
        var have = dest.length().coerceAtMost(expected)
        if (have == expected) { onProgress(expected); return }
        val c = open(url, have)
        if (c.responseCode == HttpURLConnection.HTTP_OK) have = 0          // the server gave the whole: start again
        RandomAccessFile(dest, "rw").use { out ->
            out.setLength(have); out.seek(have)
            c.inputStream.use { input ->
                val buffer = ByteArray(1 shl 16)
                while (true) {
                    val n = input.read(buffer); if (n < 0) break
                    out.write(buffer, 0, n); have += n
                    onProgress(have)
                }
            }
        }
        c.disconnect()
        if (have < expected) throw IOException("The converter's runtime download came short ($have of $expected)")
    }
}
