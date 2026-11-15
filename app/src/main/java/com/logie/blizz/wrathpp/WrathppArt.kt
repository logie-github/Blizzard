package com.logie.blizz.wrathpp

import com.logie.blizz.BuildConfig
import java.io.File
import java.io.IOException
import java.util.zip.ZipInputStream

/**
 * Shadowlands' character creator's own art for Wrath++'s creator (the user, 12 November 2026: "why not just use the EXACT
 * ASSETS from wago tools"): the pieces Shadowlands draws its creation screens from, each a file of its own, and the
 * table that names them (`WrathppAtlas.lua`), from the `wrathpp-creator-art` release (made by `wrathpp-looks.yml` with
 * `realm/warcraft/wrathpp/tools/sl_ui_art.py`: Blizzard's files, never in the repository; about 8 MB, apart from the
 * looks' 400 so that a change to the creator's art is a small download). [install] puts its `client/` into Wrath++'s
 * copy of the game as `Data/patch-S.MPQ`, a folder the game reads as an archive; the creator's patch takes the table
 * from there ([WrathppSetup.glue]). Without it the creator draws with 3.3.5's own pictures in the same places.
 * Nothing of Wrath+'s game. NOT run on a phone; [install] is unit-tested.
 */
object WrathppArt {
    const val RELEASE = "wrathpp-creator-art"
    private const val BASE = "https://github.com/${BuildConfig.UPDATE_REPO}/releases/download/$RELEASE"
    const val PATCH = "patch-S.MPQ"
    /** In the patch: the package's SHA-256, written last. */
    const val MARKER = "wrathpp-creator-art.stamp"
    const val ATLAS = "WrathppAtlas.lua"

    fun installedSha(client: File): String? =
        File(client, "Data/$PATCH/$MARKER").takeIf { it.isFile }?.readText()?.trim()?.takeIf { it.isNotEmpty() }

    /** The art's table as it is in [client], for the creator's patch; null without the art. */
    fun atlas(client: File): File? =
        File(client, "Data/$PATCH/Interface/GlueXML/$ATLAS").takeIf { it.isFile && installedSha(client) != null }

    /**
     * Downloads and installs the newest art into [client] (Wrath++'s copy of the game) when it isn't the one in. Offline
     * with some in: kept. No release yet: an [IOException] (the creator draws with 3.3.5's own pictures).
     */
    fun ensure(client: File, say: (String, Float?) -> Unit) {
        val published = runCatching { WrathppAddon.parseManifest(WrathppAddon.fetchText("$BASE/wrathpp-creator-art.json")) }.getOrElse { e ->
            if (installedSha(client) != null) return
            throw IOException("Wrath++'s creator art couldn't be fetched (${e.message ?: e.javaClass.simpleName}); the release $RELEASE may not exist yet.")
        }
        if (published.sha256.equals(installedSha(client), ignoreCase = true)) return
        val zip = File(client.parentFile, "wrathpp-creator-art.zip.part")
        say("Downloading Shadowlands' creator art for Wrath++", 0f)
        WrathppAddon.download("$BASE/wrathpp-creator-art.zip", zip) { done, total ->
            say("Downloading Shadowlands' creator art for Wrath++: ${done shr 20} / ${total shr 20} MB", if (total > 0) done.toFloat() / total else null)
        }
        try {
            if (!WrathppAddon.sha256(zip).equals(published.sha256, ignoreCase = true)) {
                throw IOException("Wrath++'s creator art download didn't match its checksum; try again.")
            }
            install(client, zip, published.sha256.lowercase())
        } finally {
            zip.delete()
        }
    }

    /**
     * Installs the art package [zip] (`client/...`): written beside its place and put in whole; a package that fails
     * leaves what was there. Paths leaving the package are refused; a package without the table is refused.
     */
    fun install(client: File, zip: File, sha: String) {
        val data = File(client, "Data")
        if (!data.isDirectory) throw IOException("Wrath++'s copy of the game has no Data folder")
        val patchNew = File(data, "$PATCH.new").apply { deleteRecursively() }
        try {
            ZipInputStream(zip.inputStream().buffered()).use { z ->
                while (true) {
                    val entry = z.nextEntry ?: break
                    if (entry.isDirectory) continue
                    val name = entry.name.replace('\\', '/')
                    if (name.startsWith("/") || name.split('/').any { it == ".." || it.isEmpty() }) throw IOException("Bad path in the creator art: ${entry.name}")
                    if (!name.startsWith("client/")) continue
                    val out = File(patchNew, name.removePrefix("client/"))
                    out.parentFile?.mkdirs()
                    out.outputStream().use { z.copyTo(it) }
                }
            }
            if (!File(patchNew, "Interface/GlueXML/$ATLAS").isFile) throw IOException("The creator art package has no table of its pieces")
            File(patchNew, MARKER).writeText("$sha\n")
            val place = File(data, PATCH)
            val old = File(place.path + ".old")
            old.deleteRecursively()
            if (place.exists() && !place.renameTo(old)) throw IOException("${place.path} couldn't be moved aside")
            if (!patchNew.renameTo(place)) {
                old.renameTo(place)
                throw IOException("${place.path} couldn't be put in place")
            }
            old.deleteRecursively()
        } finally {
            patchNew.deleteRecursively()
        }
    }
}
