package com.logie.blizz.warsmash

import android.content.Context
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import org.apache.commons.compress.archivers.sevenz.SevenZFile
import java.io.File
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder
import java.security.MessageDigest
import java.util.Locale

/**
 * Classic+ (Piotr Bednarczuk, kenshin.pl/classicplus): Warcraft III's units, trees and textures remade in more detail and
 * true to the original's look, played in Warsmash as a layer over the game's own files (the user, 12 November 2026:
 * "Integrate this hd model and texture pack if possible"). The author's archive is fetched on the phone (never in the app
 * or the repository) and made ready for Warsmash once ([prepare]): each DDS texture repacked as the BLP the game asks for
 * (the same DXT data under the .blp name, as Reforged finds it), and the models in Reforged's newer format (MDX 1100: the
 * pack's missiles and spell effects, a market and three units) left out, as Warsmash 1.0.4 can't read them; those keep the
 * game's own. The engine reads the layer in any case (patches/warsmash/0004).
 */
object ClassicPlus {
    const val VERSION = "1.01"
    const val PAGE = "https://kenshin.pl/classicplus/"
    private const val DRIVE_ID = "1vndUBXEFwlMNBUWhUUphSoCr3WhEPE2h"
    const val SIZE = 412_785_709L
    const val SHA256 = "d6fd0ac0c0d770b8ebf5d8f650a9d1271ddf175de10ad6d3dbbf8e3ae523521e"
    /** Raised whenever what [prepare] makes of the archive changes: the pack is made again. */
    const val RECIPE = 1
    private const val INNER = "Classic+/"

    fun root(context: Context) = File(context.filesDir, "warsmash-classicplus")
    fun folder(context: Context) = File(root(context), "Classic+")
    private fun stamp(context: Context) = File(root(context), "STAMP")
    private fun marker(context: Context) = File(root(context), "ON")
    private fun stampText() = "$SHA256 $RECIPE"

    fun installed(context: Context): Boolean =
        folder(context).isDirectory && runCatching { stamp(context).readText().trim() == stampText() }.getOrDefault(false)

    fun on(context: Context): Boolean = marker(context).isFile

    fun setOn(context: Context, on: Boolean) {
        val m = marker(context)
        if (on) { m.parentFile?.mkdirs(); m.writeText("on\n") } else m.delete()
    }

    /** The folder Warsmash layers over the game's files: null while it is off or not there. */
    fun layer(context: Context): File? = if (on(context) && installed(context)) folder(context) else null

    fun remove(context: Context) {
        root(context).deleteRecursively()
        mutable.value = State.Idle
    }

    sealed interface State {
        data object Idle : State
        data class Working(val step: String, val fraction: Float) : State
        data class Failed(val message: String) : State
        data object Done : State
    }

    private val mutable = MutableStateFlow<State>(State.Idle)
    val state: StateFlow<State> get() = mutable

    /** Fetches the archive, makes the pack ready and turns it on, on a thread of its own; [state] says how it goes. */
    @Synchronized
    fun install(context: Context) {
        if (mutable.value is State.Working) return
        val app = context.applicationContext
        mutable.value = State.Working("Starting", 0f)
        Thread({
            try {
                val archive = File(app.cacheDir, "classicplus-$VERSION.7z")
                if (!(archive.isFile && archive.length() == SIZE && sha256(archive) == SHA256)) download(archive)
                mutable.value = State.Working("Checking", 1f)
                if (sha256(archive) != SHA256) {
                    archive.delete()
                    throw IOException("The archive isn't Classic+ $VERSION as the app knows it (the author may have updated it).")
                }
                val staging = File(root(app), "staging")
                staging.deleteRecursively()
                unpack(archive, staging) { f -> mutable.value = State.Working("Unpacking", f) }
                mutable.value = State.Working("Making it ready for Warsmash", 1f)
                prepare(staging)
                val target = folder(app)
                target.deleteRecursively()
                if (!staging.renameTo(target)) throw IOException("The pack couldn't be put in place.")
                stamp(app).writeText(stampText() + "\n")
                archive.delete()
                setOn(app, true)
                mutable.value = State.Done
            } catch (e: Exception) {
                mutable.value = State.Failed(e.message ?: e.toString())
            }
        }, "classicplus").start()
    }

    // The download --------------------------------------------------------------------------------------------------

    private fun download(target: File) {
        val start = "https://drive.usercontent.google.com/download?id=$DRIVE_ID&export=download"
        var connection = open(start)
        if (connection.contentType.orEmpty().startsWith("text/html")) {
            // Google Drive's "can't scan this file for viruses" page: its form goes on to the file.
            val page = connection.inputStream.use { it.readBytes().toString(Charsets.UTF_8) }
            connection.disconnect()
            val next = confirmUrl(page) ?: throw IOException("Google Drive didn't offer the file (it may be over its download limit; try later).")
            connection = open(next)
            if (connection.contentType.orEmpty().startsWith("text/html")) {
                connection.disconnect()
                throw IOException("Google Drive didn't offer the file (it may be over its download limit; try later).")
            }
        }
        target.parentFile?.mkdirs()
        val part = File(target.path + ".part")
        connection.inputStream.use { input ->
            part.outputStream().use { out ->
                val buffer = ByteArray(1 shl 16)
                var total = 0L
                while (true) {
                    val n = input.read(buffer)
                    if (n < 0) break
                    out.write(buffer, 0, n)
                    total += n
                    mutable.value = State.Working("Downloading", (total.toFloat() / SIZE).coerceIn(0f, 1f))
                }
            }
        }
        connection.disconnect()
        if (!part.renameTo(target)) throw IOException("The download couldn't be kept.")
    }

    private fun open(url: String): HttpURLConnection = (URL(url).openConnection() as HttpURLConnection).apply {
        connectTimeout = 30_000
        readTimeout = 60_000
        instanceFollowRedirects = true
        setRequestProperty("User-Agent", "Mozilla/5.0")
        if (responseCode !in 200..299) throw IOException("The download answered $responseCode.")
    }

    /** The address Google Drive's warning page's form goes on to (its action with its hidden fields), or null. */
    internal fun confirmUrl(page: String): String? {
        val form = Regex("""<form[^>]*action="([^"]+)"[^>]*>(.*?)</form>""", RegexOption.DOT_MATCHES_ALL).find(page) ?: return null
        val action = form.groupValues[1].replace("&amp;", "&")
        val fields = Regex("""<input[^>]*type="hidden"[^>]*name="([^"]+)"[^>]*value="([^"]*)"""").findAll(form.groupValues[2])
            .map { it.groupValues[1] to it.groupValues[2].replace("&amp;", "&") }.toList()
        if (fields.isEmpty()) return null
        val query = fields.joinToString("&") { (k, v) -> "${URLEncoder.encode(k, "UTF-8")}=${URLEncoder.encode(v, "UTF-8")}" }
        return action + (if ('?' in action) "&" else "?") + query
    }

    private fun sha256(file: File): String {
        val digest = MessageDigest.getInstance("SHA-256")
        file.inputStream().use { input ->
            val buffer = ByteArray(1 shl 16)
            while (true) {
                val n = input.read(buffer)
                if (n < 0) break
                digest.update(buffer, 0, n)
            }
        }
        return digest.digest().joinToString("") { "%02x".format(it) }
    }

    // Unpacking and making it ready ---------------------------------------------------------------------------------

    /** The archive's Classic+ folder into [into] (only that: the instructions and the registry file stay out). */
    internal fun unpack(archive: File, into: File, progress: (Float) -> Unit = {}) {
        into.mkdirs()
        val base = into.canonicalFile
        SevenZFile.builder().setFile(archive).get().use { zip ->
            val entries = zip.entries.filter { !it.isDirectory }
            val total = entries.sumOf { it.size }.coerceAtLeast(1)
            var done = 0L
            val buffer = ByteArray(1 shl 16)
            while (true) {
                val entry = zip.nextEntry ?: break
                if (entry.isDirectory) continue
                val name = entry.name.replace('\\', '/')
                val at = name.indexOf(INNER)
                if (at < 0) continue
                val relative = name.substring(at + INNER.length)
                if (relative.isEmpty() || relative.split('/').any { it == ".." }) continue
                val out = File(base, relative).canonicalFile
                if (!out.path.startsWith(base.path + File.separator)) continue
                out.parentFile?.mkdirs()
                out.outputStream().use { o ->
                    while (true) {
                        val n = zip.read(buffer)
                        if (n < 0) break
                        o.write(buffer, 0, n)
                        done += n
                    }
                }
                progress((done.toFloat() / total).coerceIn(0f, 1f))
            }
        }
    }

    /**
     * Makes the unpacked pack in [dir] ready for Warsmash: models of any format but classic MDX (800) out, every DDS
     * texture written as the BLP the game names (unless the pack has that BLP), the DDS kept only where a model names it.
     */
    internal fun prepare(dir: File) {
        val files = dir.walkTopDown().filter { it.isFile }.toList()
        val named = HashSet<String>()
        for (f in files.filter { it.name.endsWith(".mdx", ignoreCase = true) }) {
            val bytes = f.readBytes()
            if (mdxVersion(bytes) != 800) {
                f.delete()
                continue
            }
            textures(bytes).filter { it.endsWith(".dds") }.forEach { named += it }
        }
        val blps = files.filter { it.name.endsWith(".blp", ignoreCase = true) }.map { key(dir, it) }.toHashSet()
        for (f in files.filter { it.name.endsWith(".dds", ignoreCase = true) }) {
            val k = key(dir, f)
            val blpKey = k.removeSuffix(".dds") + ".blp"
            if (blpKey !in blps) {
                ddsToBlp(f.readBytes())?.let { File(f.path.dropLast(4) + ".blp").writeBytes(it) }
            }
            if (k !in named) f.delete()
        }
        files.filter { it.name.endsWith(".reg", ignoreCase = true) || it.name.endsWith(".txt", ignoreCase = true) }.forEach { it.delete() }
    }

    /** The path of [f] under [dir] as the game names files: forward slashes, lower case. */
    private fun key(dir: File, f: File) = f.relativeTo(dir).path.replace('\\', '/').lowercase(Locale.US)

    /** An MDX's format version (800 classic, 900 and up Reforged's), or null for anything else. */
    internal fun mdxVersion(bytes: ByteArray): Int? {
        if (bytes.size < 16 || String(bytes, 0, 4, Charsets.ISO_8859_1) != "MDLX" || String(bytes, 4, 4, Charsets.ISO_8859_1) != "VERS") return null
        return u32(bytes, 12).toInt()
    }

    /** The texture paths an MDX names (its TEXS chunk), lower case with forward slashes. */
    internal fun textures(bytes: ByteArray): List<String> {
        val out = ArrayList<String>()
        var i = 4
        while (i + 8 <= bytes.size) {
            val tag = String(bytes, i, 4, Charsets.ISO_8859_1)
            val size = u32(bytes, i + 4).toInt()
            if (size < 0 || i + 8 + size > bytes.size) break
            if (tag == "TEXS") {
                var k = i + 8
                while (k + 268 <= i + 8 + size) {
                    var end = k + 4
                    while (end < k + 264 && bytes[end] != 0.toByte()) end++
                    val path = String(bytes, k + 4, end - (k + 4), Charsets.ISO_8859_1)
                    if (path.isNotEmpty()) out += path.replace('\\', '/').lowercase(Locale.US)
                    k += 268
                }
            }
            i += 8 + size
        }
        return out
    }

    /**
     * A DDS texture (DXT1, DXT3 or DXT5) as a BLP2 file holding the same compressed picture (its full size; Warsmash
     * draws only that), which Warsmash reads where the game asks for a .blp. Null for any other DDS.
     */
    internal fun ddsToBlp(dds: ByteArray): ByteArray? {
        if (dds.size < 128 || String(dds, 0, 4, Charsets.ISO_8859_1) != "DDS ") return null
        val height = u32(dds, 12).toInt()
        val width = u32(dds, 16).toInt()
        val flags = u32(dds, 80).toInt()
        val (block, alphaDepth, alphaEncoding) = when (String(dds, 84, 4, Charsets.ISO_8859_1)) {
            "DXT1" -> Triple(8, if (flags and 1 != 0) 1 else 0, 0)
            "DXT3" -> Triple(16, 8, 1)
            "DXT5" -> Triple(16, 8, 7)
            else -> return null
        }
        if (width <= 0 || height <= 0) return null
        val size = maxOf(1, (width + 3) / 4) * maxOf(1, (height + 3) / 4) * block
        if (128 + size > dds.size) return null
        val out = ByteArray(1172 + size)
        "BLP2".toByteArray(Charsets.ISO_8859_1).copyInto(out, 0)
        put32(out, 4, 1)
        out[8] = 2
        out[9] = alphaDepth.toByte()
        out[10] = alphaEncoding.toByte()
        out[11] = 1
        put32(out, 12, width)
        put32(out, 16, height)
        put32(out, 20, 1172)
        put32(out, 84, size)
        dds.copyInto(out, 1172, 128, 128 + size)
        return out
    }

    private fun u32(b: ByteArray, at: Int): Long =
        (b[at].toLong() and 0xFF) or ((b[at + 1].toLong() and 0xFF) shl 8) or ((b[at + 2].toLong() and 0xFF) shl 16) or ((b[at + 3].toLong() and 0xFF) shl 24)

    private fun put32(b: ByteArray, at: Int, v: Int) {
        b[at] = v.toByte(); b[at + 1] = (v shr 8).toByte(); b[at + 2] = (v shr 16).toByte(); b[at + 3] = (v shr 24).toByte()
    }
}
