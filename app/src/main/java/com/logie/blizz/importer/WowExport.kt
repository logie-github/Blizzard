package com.logie.blizz.importer

import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.io.InputStream
import java.security.MessageDigest

/**
 * What the World of Warcraft app's "Export everything to Blizzard" makes, and how it's read: a
 * folder `WoW-export/` holding `files/` (byte-for-byte copies of the app's data), `prefs/` (its
 * settings as JSON), `checksums.tsv` (SHA-256, size and path of every file) and, written last,
 * `export.json`. Plain Kotlin, unit-tested.
 */
object WowExport {
    const val APP = "com.logie.warcraft"
    const val MANIFEST = "export.json"
    const val CHECKSUMS = "checksums.tsv"

    data class Manifest(
        val format: Int,
        val app: String,
        val appVersion: String,
        val createdAt: String,
        val sourceFilesDir: String,
        val files: Long,
        val bytes: Long,
        val folders: List<String>,
        val excluded: List<String>,
        val prefs: List<String>,
    )

    data class Entry(val sha256: String, val size: Long, val path: String)

    fun parseManifest(json: String): Manifest {
        val o = try { JSONObject(json) } catch (e: Exception) { throw ImportException(Problem.CORRUPT_ARCHIVE, "export.json isn't readable: ${e.message}") }
        fun strings(name: String) = o.optJSONArray(name)?.let { a -> (0 until a.length()).map { a.getString(it) } } ?: emptyList()
        val m = Manifest(
            format = o.optInt("format"), app = o.optString("app"), appVersion = o.optString("appVersion"), createdAt = o.optString("createdAt"),
            sourceFilesDir = o.optString("sourceFilesDir"), files = o.optLong("files"), bytes = o.optLong("bytes"),
            folders = strings("folders"), excluded = strings("excluded"), prefs = strings("prefs"),
        )
        if (m.format != 1) throw ImportException(Problem.UNSUPPORTED_VERSION, "This export is format ${m.format}; this app reads format 1. Update both apps.")
        if (m.app != APP) throw ImportException(Problem.MISSING_SOURCE_DATA, "That export wasn't made by the World of Warcraft app (${m.app.ifEmpty { "unknown" }}).")
        return m
    }

    fun manifestJson(m: Manifest): String = JSONObject()
        .put("format", m.format).put("app", m.app).put("appVersion", m.appVersion).put("createdAt", m.createdAt)
        .put("sourceFilesDir", m.sourceFilesDir).put("files", m.files).put("bytes", m.bytes)
        .put("folders", JSONArray(m.folders)).put("excluded", JSONArray(m.excluded)).put("prefs", JSONArray(m.prefs))
        .put("checksums", CHECKSUMS).toString(2)

    /** `<sha256>\t<size>\t<path>` lines; a malformed line is an error, not skipped. */
    fun parseChecksums(text: String): List<Entry> = text.lineSequence().filter { it.isNotBlank() }.map { line ->
        val parts = line.split('\t', limit = 3)
        val ok = parts.size == 3 && parts[0].length == 64 && parts[1].toLongOrNull() != null && parts[2].isNotEmpty()
        if (!ok) throw ImportException(Problem.CORRUPT_ARCHIVE, "checksums.tsv has a line this app can't read: ${line.take(80)}")
        Entry(parts[0].lowercase(), parts[1].toLong(), parts[2])
    }.toList()

    fun checksumsText(entries: List<Entry>): String = entries.sortedBy { it.path }.joinToString("\n", postfix = "\n") { "${it.sha256}\t${it.size}\t${it.path}" }

    /** A path from the manifest that stays inside the folder it's copied to. */
    fun safePath(path: String): String {
        val parts = path.split('/')
        if (path.startsWith("/") || parts.any { it == ".." || it.isEmpty() || it == "." } || path.contains('\\')) {
            throw ImportException(Problem.CORRUPT_ARCHIVE, "The export lists a path that isn't allowed: ${path.take(80)}")
        }
        return path
    }

    /** SHA-256 of [input] while copying it to [out]; returns it (lower-case hex) and the bytes copied. */
    fun copyHashed(input: InputStream, out: java.io.OutputStream, cancel: CancelToken, onBytes: (Long) -> Unit): Pair<String, Long> {
        val digest = MessageDigest.getInstance("SHA-256")
        val buffer = ByteArray(1 shl 20)
        var total = 0L
        while (true) {
            val n = input.read(buffer)
            if (n < 0) break
            cancel.check()
            digest.update(buffer, 0, n)
            out.write(buffer, 0, n)
            total += n
            onBytes(n.toLong())
        }
        return digest.digest().joinToString("") { "%02x".format(it) } to total
    }

    fun sha256(file: File): String {
        val digest = MessageDigest.getInstance("SHA-256")
        file.inputStream().use { input ->
            val buffer = ByteArray(1 shl 20)
            while (true) { val n = input.read(buffer); if (n < 0) break; digest.update(buffer, 0, n) }
        }
        return digest.digest().joinToString("") { "%02x".format(it) }
    }
}
