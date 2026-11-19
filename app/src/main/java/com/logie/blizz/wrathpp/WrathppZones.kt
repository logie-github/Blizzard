package com.logie.blizz.wrathpp

import com.logie.blizz.wow.WowLayout
import java.io.File
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL
import java.io.RandomAccessFile

/**
 * The Worgen's and Goblins' starting areas for Wrath++ (docs/wrathpp/CATA_RACES.md; the user: "convert straight into the app so I
 * don't have to import it"): Gilneas, Kezan and the Lost Isles from Cataclysm Classic, made for 3.3.5a (mod-worgen-goblin's
 * `tools/zones`, `package.py`), a 735 MB `cata-zones.tar.xz` published as a release `cata-zones-<hash>` with its `cata-zones.json`.
 * This build names one release ([TAG], [SHA256], [SIZE], [UNPACKED]) and downloads it once (carrying on from a part after a dropped
 * connection), checks its SHA-256 and unpacks it beside into `files/zones`, where `ctl.sh` finds it ([WowLayout.zones], `ZONES`): the
 * realm turns the starting areas on when it is there (`WorgenGoblin.StartingAreas`, `WOW_ZONES_DIR`) and the game's patch is made with
 * their files at its next start. Without the package, or when the download fails, Wrath++ goes on as before (the two races start with
 * the Night Elves and the Orcs). Never touches the realms' game folders or databases: only `zones`, `zones.new` and the download.
 *
 * NOT run on a phone. The pure parts ([isInstalled], [looksComplete]) are unit-tested.
 */
object WrathppZones {
    /** The release this build installs: the repository that publishes it, its tag and the package's checksum, sizes. */
    const val REPO = "logie-github/yeabwoi"
    const val TAG = "cata-zones-b2a8428dfe7e"
    const val SHA256 = "c032002c80ad467f119f44ed61e18c6206e4079675444645128dd0c05ef20abd"
    const val SIZE = 734_727_420L
    const val UNPACKED = 1_665_288_620L
    private const val URL_BASE = "https://github.com/$REPO/releases/download/$TAG"
    private const val ASSET = "cata-zones.tar.xz"

    /** Written into `zones` after a complete install: the package's SHA-256. */
    const val MARKER = ".installed"

    /** What the package must hold to be one: the tag, the client's file list and the server's maps. */
    fun looksComplete(folder: File): Boolean =
        File(folder, "TAG").isFile && File(folder, "client/files.txt").isFile && File(folder, "server/maps").isDirectory

    fun installedSha(layout: WowLayout): String? =
        File(layout.zones, MARKER).takeIf { it.isFile }?.readText()?.trim()?.takeIf { it.length == 64 }

    /** This build's package is the one in place. */
    fun isInstalled(layout: WowLayout): Boolean = installedSha(layout).equals(SHA256, ignoreCase = true) && looksComplete(layout.zones)

    /**
     * Makes sure this build's package is in `files/zones`: nothing to do when it is, else downloads, checks and unpacks it. Call off the
     * main thread; [say] gets the step's words and share done (0..1). Throws when it can't (the caller keeps going without the areas).
     */
    fun ensure(layout: WowLayout, say: (String, Float?) -> Unit) {
        if (isInstalled(layout)) return
        val root = layout.root
        val archive = File(root, "cata-zones.tar.xz.part")
        val need = (SIZE - archive.length().coerceAtMost(SIZE)) + UNPACKED + (512L shl 20)
        val free = root.usableSpace
        if (free in 1 until need) throw IOException("Not enough space for the starting areas: they need about ${need shr 20} MB free, ${free shr 20} MB is left.")
        say("Downloading the Worgen's and Goblins' starting areas", 0f)
        download(archive) { done ->
            say("Downloading the Worgen's and Goblins' starting areas: ${done shr 20} / ${SIZE shr 20} MB", done.toFloat() / SIZE)
        }
        val size = archive.length().coerceAtLeast(1)
        val sha = WrathppServerPackage.sha256(archive) { read -> say("Checking the starting areas: ${read shr 20} / ${size shr 20} MB", read.toFloat() / size) }
        if (!sha.equals(SHA256, ignoreCase = true)) {
            archive.delete()
            throw IOException("The starting areas' download didn't match its checksum; try again.")
        }
        val staging = File(root, "zones.new")
        staging.deleteRecursively()
        try {
            WrathppServerPackage.unpack(archive, staging) { written -> say("Unpacking the starting areas: ${written shr 20} / ${UNPACKED shr 20} MB", written.toFloat() / UNPACKED) }
            val folder = File(staging, "cata-zones").takeIf { it.isDirectory } ?: staging
            if (!looksComplete(folder)) throw IOException("Not the starting areas' package")
            File(folder, MARKER).writeText(SHA256)
            val old = File(root, "zones.old")
            old.deleteRecursively()
            if (layout.zones.exists() && !layout.zones.renameTo(old)) layout.zones.deleteRecursively()
            if (!folder.renameTo(layout.zones)) folder.copyRecursively(layout.zones, overwrite = true)
            old.deleteRecursively()
        } finally {
            staging.deleteRecursively()
        }
        archive.delete()
    }

    /** The package carried on from what an earlier try left (a Range request for the rest; the whole when the server won't). */
    private fun download(dest: File, onProgress: (Long) -> Unit) {
        dest.parentFile?.mkdirs()
        var have = dest.length().coerceAtMost(SIZE)
        if (have == SIZE) { onProgress(SIZE); return }
        var current = URL("$URL_BASE/$ASSET")
        repeat(6) {
            val c = (current.openConnection() as HttpURLConnection).apply {
                connectTimeout = 30_000; readTimeout = 60_000; instanceFollowRedirects = false
                setRequestProperty("User-Agent", "Blizzard-Launcher")
                if (have > 0) setRequestProperty("Range", "bytes=$have-")
            }
            when (c.responseCode) {
                in 300..399 -> { current = URL(current, c.getHeaderField("Location")); c.disconnect() }
                HttpURLConnection.HTTP_OK, HttpURLConnection.HTTP_PARTIAL -> {
                    if (c.responseCode == HttpURLConnection.HTTP_OK) have = 0              // the server gave the whole: start again
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
                    if (have < SIZE) throw IOException("The starting areas' download came short ($have of $SIZE)")
                    return
                }
                else -> { val code = c.responseCode; c.disconnect(); throw IOException("The starting areas' download failed ($code)") }
            }
        }
        throw IOException("Too many redirects")
    }
}
