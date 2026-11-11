package com.logie.blizz.wrathpp

import com.logie.blizz.BuildConfig
import com.logie.blizz.wowclient.Mpq
import org.json.JSONObject
import java.io.File
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest
import java.util.zip.ZipInputStream

/**
 * Wrath++'s add-on for its copy of the 32-bit game (docs/wrathpp/CLIENT_PROBE.md): WarcraftXL's 32-bit runtime, its Lua
 * mod runtime and glue-unlock, Wrath++'s native mod (the creator's current choices and counts) and Lua mod (the
 * appearance protocol), and the creator's script, from the `wrathpp-client-addon` release (built by
 * `wrathpp-client.yml`). [install] puts them into `client-wrathpp` only:
 *  - `WarcraftXL.dll` and `Mods/` beside the game;
 *  - `WowWrathpp.exe`: the game's program ([baseExecutable]) patched to load the runtime ([WxlPatcher]);
 *  - `Data/patch-X.MPQ`: the creator's script, and the interface's table of contents with it added last.
 * Never anything of Wrath+'s game. NOT run on a phone; the pure parts are unit-tested.
 */
object WrathppAddon {
    const val RELEASE = "wrathpp-client-addon"
    private const val BASE = "https://github.com/${BuildConfig.UPDATE_REPO}/releases/download/$RELEASE"
    const val EXE = "WowWrathpp.exe"
    const val PATCH = "patch-X.MPQ"
    const val MARKER = ".wrathpp-addon"
    private const val TOC = "Interface\\GlueXML\\GlueXML.toc"

    data class Manifest(val size: Long, val sha256: String, val format: Int)

    fun parseManifest(text: String): Manifest = JSONObject(text).let { Manifest(it.getLong("size"), it.getString("sha256"), it.optInt("format", 1)) }

    fun installedSha(client: File): String? = File(client, MARKER).takeIf { it.isFile }?.readText()?.trim()?.takeIf { it.isNotEmpty() }

    /** The program the add-on's is made from: the one the realms' setup would start (the patched copy the WoW app made, else the game's). */
    fun baseExecutable(client: File): File? =
        listOf(com.logie.blizz.game.WowClientSetup.PATCHED_EXE, com.logie.blizz.game.WowClientSetup.EXE).map { File(client, it) }.firstOrNull { it.isFile }

    /** Downloads and installs the newest add-on into [client] (Wrath++'s copy) when it isn't the one in. Offline with one in: kept. */
    fun ensure(client: File, say: (String, Float?) -> Unit) {
        val published = runCatching { parseManifest(fetchText("$BASE/wrathpp-client-addon.json")) }.getOrElse { e ->
            if (installedSha(client) != null) return
            throw IOException("Wrath++'s add-on couldn't be fetched (${e.message ?: e.javaClass.simpleName}); the release $RELEASE may not exist yet.")
        }
        if (published.sha256.equals(installedSha(client), ignoreCase = true) && File(client, EXE).isFile) return
        val zip = File(client.parentFile, "wrathpp-client-addon.zip.part")
        say("Downloading Wrath++'s add-on", 0f)
        download("$BASE/wrathpp-client-addon.zip", zip) { done, total -> say("Downloading Wrath++'s add-on: ${done shr 10} / ${total shr 10} KB", if (total > 0) done.toFloat() / total else null) }
        if (!sha256(zip).equals(published.sha256, ignoreCase = true)) {
            zip.delete()
            throw IOException("Wrath++'s add-on download didn't match its checksum; try again.")
        }
        say("Installing Wrath++'s add-on", null)
        install(client, zip.readBytes(), published.sha256)
        zip.delete()
    }

    /** Installs the add-on [zip] into [client]. Throws [IOException] on anything it can't do; [client] is left working either way. */
    fun install(client: File, zip: ByteArray, sha: String) {
        val files = unzip(zip)
        val dll = files["WarcraftXL.dll"] ?: throw IOException("The add-on has no WarcraftXL.dll")
        val base = baseExecutable(client) ?: throw IOException("Wrath++'s copy of the game has no Wow.exe")
        // Its mods replace the add-on's earlier ones; nothing else in Mods/ is touched.
        for (name in files.keys.filter { it.startsWith("Mods/") }.map { it.split('/')[1] }.toSet()) File(client, "Mods/$name").deleteRecursively()
        for ((name, bytes) in files) {
            if (!name.startsWith("Mods/")) continue
            File(client, name).apply { parentFile?.mkdirs(); writeBytes(bytes) }
        }
        File(client, "WarcraftXL.dll").writeBytes(dll)
        WxlPatcher.patchFile(base, File(client, EXE))
        File(client, MARKER).writeText("$sha\n")
    }

    /** The table of contents with [added] after everything, the lines naming a file no archive has (another realm's module's) left out. */
    fun toc(original: String, added: List<String>, exists: (String) -> Boolean): String {
        val lines = original.replace("\r\n", "\n").split("\n").filter { line ->
            val name = line.trim()
            name.isEmpty() || name.startsWith("#") || name in added || exists("Interface\\GlueXML\\$name")
        }.filter { it.trim() !in added }
        return (lines.dropLastWhile { it.isBlank() } + added).joinToString("\r\n", postfix = "\r\n")
    }

    /**
     * `Data/patch-X.MPQ` in [client]: the creator's scripts ([glue], by file name) and GlueXML.toc with them added last.
     * Written by the app at every Wrath++ Play (WrathppSetup), whether the add-on is in or not.
     */
    fun writeGluePatch(client: File, glue: Map<String, ByteArray>) {
        val data = File(client, "Data")
        val patch = File(data, PATCH)
        // The game's own archives, without this patch: what the toc is and which files exist.
        val game = Mpq.Game(data, skip = listOf(PATCH.lowercase()))
        try {
            val original = game.read(TOC)?.toString(Charsets.UTF_8) ?: throw IOException("The game's GlueXML.toc couldn't be read")
            val text = toc(original, glue.keys.sorted()) { game.has(it) }
            val tmp = File(data, "$PATCH.tmp")
            val writer = Mpq.Writer(tmp)
            writer.add(TOC, text.toByteArray(Charsets.UTF_8))
            for ((name, bytes) in glue) writer.add("Interface\\GlueXML\\$name", bytes)
            if (!writer.finish()) throw IOException("Wrath++'s interface patch couldn't be written")
            patch.delete()
            if (!tmp.renameTo(patch)) throw IOException("Wrath++'s interface patch couldn't be put in place")
        } finally {
            game.close()
        }
    }

    /** The zip's files by path (`wrathpp-client-addon/` taken off), refusing any path that would leave it. */
    fun unzip(zip: ByteArray): Map<String, ByteArray> {
        val out = LinkedHashMap<String, ByteArray>()
        ZipInputStream(zip.inputStream()).use { z ->
            while (true) {
                val entry = z.nextEntry ?: break
                if (entry.isDirectory) continue
                val name = entry.name.replace('\\', '/').removePrefix("wrathpp-client-addon/")
                if (name.isEmpty() || name.startsWith("/") || name.split('/').any { it == ".." || it.isEmpty() }) throw IOException("Bad path in the add-on: ${entry.name}")
                out[name] = z.readBytes()
            }
        }
        return out
    }

    internal fun fetchText(url: String): String = connect(url).let { c -> c.inputStream.bufferedReader().use { it.readText() }.also { c.disconnect() } }

    internal fun download(url: String, dest: File, onProgress: (Long, Long) -> Unit) {
        val c = connect(url)
        val total = c.contentLengthLong
        var done = 0L
        c.inputStream.use { input -> dest.outputStream().use { out ->
            val buffer = ByteArray(1 shl 16)
            while (true) { val n = input.read(buffer); if (n < 0) break; out.write(buffer, 0, n); done += n; onProgress(done, total) }
        } }
        c.disconnect()
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

    internal fun sha256(file: File): String {
        val d = MessageDigest.getInstance("SHA-256")
        file.inputStream().use { input -> val b = ByteArray(1 shl 16); while (true) { val n = input.read(b); if (n < 0) break; d.update(b, 0, n) } }
        return d.digest().joinToString("") { "%02x".format(it) }
    }
}
