package com.logie.blizz.forevernew

import java.io.File
import java.io.IOException
import java.security.MessageDigest

/**
 * The world and hotfix databases of WoW Forever (about 950 MB as SQL) are not in the server's source; Karrz ships them inside the
 * Windows repack release. Only those two entries are read out of it (range requests, [RangeZip]), each checked against a
 * SHA-256 pinned in `forever-version.env` (measured 15 November 2026 against v0.1.36.1), then kept in `downloads/` until the
 * import has run. The repack's Windows programs are not downloaded, unpacked or run.
 */
object ForeverRepackData {
    data class Pin(val entry: String, val size: Long, val sha256: String, val fileName: String)

    const val BASE = "https://github.com/Karrz1/Karrz-playerbots-wow-forever/releases/download/v0.1.36.1"
    const val REPACK_URL = "$BASE/WoW-Forever-Bots-0.1.36.1.zip"
    const val ADDON_URL = "$BASE/ForeverBots-addon-0.1.36.1.zip"
    const val ADDON_SHA256 = "0c1756fc48bd7e9af2b074c16a65d8367c06b3b1c99e216855027b7d78c1769e"
    const val BUILDS_URL = "$BASE/client-builds.txt"
    const val BUILDS_SHA256 = "0b43980708438fb2644cd1c71d2c08916eb209d746809042e03e8bc35de511d3"

    val WORLD = Pin("sql/world.sql", 613_883_583L, "3ea1b8d138bb097f7003e5b41d9bf2136a9e1bcd224bbb96ec7daeb52a2ed5a2", "world.sql")
    val HOTFIXES = Pin("sql/hotfixes.sql", 339_516_733L, "492bf4e7034832012afe282eeafc3a074a7caac79f5e20b798ae745005cb8fa7", "hotfixes.sql")

    fun spaceNeeded(): Long = WORLD.size + HOTFIXES.size + (512L shl 20)

    /**
     * Extracts [pin] from [source] into [dest] (through `.part`), checking size and SHA-256. A finished, correct [dest] is left
     * alone. [onProgress] gets (bytes, total). An interrupted extraction starts that entry again (a deflate stream can't resume).
     */
    fun extract(source: RangeZip.Source, pin: Pin, dest: File, onProgress: (Long, Long) -> Unit = { _, _ -> }): File {
        if (dest.isFile && dest.length() == pin.size && ForeverDownloads.sha256(dest).equals(pin.sha256, ignoreCase = true)) return dest
        val entry = RangeZip.list(source).firstOrNull { it.name == pin.entry } ?: throw IOException("${pin.entry} is not in the repack")
        if (entry.size != pin.size) throw IOException("${pin.entry} is ${entry.size} bytes, expected ${pin.size}: the repack is not the pinned version")
        dest.parentFile?.mkdirs()
        val part = File(dest.path + ".part")
        val digest = MessageDigest.getInstance("SHA-256")
        var done = 0L
        RangeZip.open(source, entry).use { input ->
            part.outputStream().buffered(1 shl 16).use { out ->
                val buffer = ByteArray(1 shl 16)
                while (true) {
                    val n = input.read(buffer)
                    if (n < 0) break
                    out.write(buffer, 0, n); digest.update(buffer, 0, n); done += n
                    onProgress(done, pin.size)
                }
            }
        }
        val sha = digest.digest().joinToString("") { "%02x".format(it) }
        if (done != pin.size || !sha.equals(pin.sha256, ignoreCase = true)) {
            part.delete()
            throw IOException("${pin.entry} did not match its pinned checksum")
        }
        dest.delete()
        if (!part.renameTo(dest)) throw IOException("${pin.fileName} couldn't be saved")
        return dest
    }
}
