package com.logie.blizz.forevernew

import com.logie.blizz.BuildConfig
import org.apache.commons.compress.archivers.tar.TarArchiveInputStream
import org.json.JSONObject
import org.tukaani.xz.XZInputStream
import java.io.File
import java.io.IOException
import java.nio.file.Files

/**
 * Forever's server package: `forever-android-arm64.tar.xz` and its manifest `forever-android-arm64.json` on this repository's
 * `forever-android-server` release, made by `.github/workflows/build-forever-native.yml`. THAT RELEASE DOES NOT EXIST UNTIL
 * THE WORKFLOW HAS RUN ON `main`; until then [manifest] fails with a message saying so, and nothing is advertised.
 *
 * Download (resumed, checked), bounded extraction beside the install, a swap in two renames, the previous version kept as
 * `server.old` and put back if the new one fails [verify]. Only `server`, `server.new`, `server.old` and `downloads` are
 * written: never the databases, characters, client or keys.
 */
object ForeverPackage {
    const val RELEASE = "forever-android-server"
    const val BASE = "https://github.com/${BuildConfig.UPDATE_REPO}/releases/download/$RELEASE"
    const val MANIFEST_URL = "$BASE/forever-android-arm64.json"
    const val PACKAGE_FORMAT = 1
    /** The app's own version of the manifest's `schema` and `min_app_version` it understands. */
    const val SCHEMA = 1
    const val APP_LEVEL = 1

    data class Manifest(
        val arch: String, val libc: String, val format: Int, val schema: Int, val minApp: Int,
        val sourceCommit: String, val upstream: String, val size: Long, val sha256: String, val unpacked: Long,
        val url: String, val clientBuilds: List<Int>, val components: Map<String, String>,
    )

    fun parseManifest(text: String): Manifest {
        val j = JSONObject(text)
        val builds = j.optJSONArray("client_builds")?.let { a -> (0 until a.length()).map { a.getInt(it) } }.orEmpty()
        val comps = j.optJSONObject("components")?.let { o -> o.keys().asSequence().associateWith { o.getString(it) } }.orEmpty()
        return Manifest(
            arch = j.getString("arch"), libc = j.getString("libc"), format = j.getInt("format"), schema = j.optInt("schema", 1),
            minApp = j.optInt("min_app_version", 1), sourceCommit = j.getString("source_commit"), upstream = j.getString("upstream_version"),
            size = j.getLong("size"), sha256 = j.getString("sha256"), unpacked = j.optLong("unpacked"), url = j.getString("url"),
            clientBuilds = builds, components = comps,
        )
    }

    /** Why this manifest can't be installed by this app and phone, or null. */
    fun incompatible(m: Manifest, deviceAbis: List<String>): String? = when {
        m.arch != "aarch64" || "arm64-v8a" !in deviceAbis -> "This server is built for 64-bit ARM phones (aarch64); this device reports ${deviceAbis.joinToString()}."
        m.libc != "musl" -> "This server needs a ${m.libc} runtime the app doesn't have."
        m.format != PACKAGE_FORMAT -> "This server's package format (${m.format}) isn't the one this app version reads ($PACKAGE_FORMAT). Update the app."
        m.schema > SCHEMA || m.minApp > APP_LEVEL -> "This server needs a newer version of the app."
        !Regex("[0-9a-f]{64}").matches(m.sha256.lowercase()) || !Regex("[0-9a-f]{40}").matches(m.sourceCommit) -> "The server's manifest is malformed."
        !m.url.startsWith("https://") -> "The server's manifest has no HTTPS address."
        else -> null
    }

    fun manifest(): Manifest = try { parseManifest(ForeverDownloads.fetchText(MANIFEST_URL)) } catch (e: IOException) {
        throw IOException("Forever's server isn't published yet or can't be reached (${e.message}). It is made by this repository's " +
            "'Build the WoW Forever realm' workflow and attached to the release $RELEASE.")
    }

    fun installed(layout: ForeverLayout): Manifest? =
        layout.installedManifest.takeIf { it.isFile }?.let { runCatching { parseManifest(it.readText()) }.getOrNull() }

    /** Nothing installed, an unfinished install, or another package than [published]. */
    fun needsInstall(layout: ForeverLayout, published: Manifest?): Boolean {
        val have = installed(layout)
        if (have == null || !layout.hasServer()) return true
        return published != null && !published.sha256.equals(have.sha256, ignoreCase = true)
    }

    /** Where a tar entry goes under [base]; null for anything that would leave it (absolute, `..`, empty). */
    fun entryTarget(base: File, name: String): File? {
        val clean = name.removePrefix("./")
        if (clean.isEmpty() || clean.startsWith("/") || clean.contains('\\') || clean.split('/').any { it == ".." }) return null
        val target = File(base, clean)
        val basePath = base.canonicalPath
        return target.takeIf { it.canonicalPath == basePath || it.canonicalPath.startsWith(basePath + File.separator) }
    }

    /** A relative link whose target stays inside [base] (resolved from the link's own folder). */
    fun linkStaysInside(base: File, linkFile: File, linkName: String): Boolean {
        if (linkName.startsWith("/") || linkName.contains('\\')) return false
        val resolved = File(linkFile.parentFile, linkName).canonicalPath
        val basePath = base.canonicalPath
        return resolved == basePath || resolved.startsWith(basePath + File.separator)
    }

    /**
     * Unpacks the archive into [dest], never more than [maxBytes] in total nor [maxEntries] entries (an archive that lies
     * about its size is stopped, not written). Returns bytes written.
     */
    fun unpack(archive: File, dest: File, maxBytes: Long, maxEntries: Int = 200_000, onBytes: (Long) -> Unit = {}): Long {
        dest.mkdirs()
        var written = 0L; var reported = 0L; var entries = 0
        TarArchiveInputStream(XZInputStream(archive.inputStream().buffered())).use { tar ->
            val buffer = ByteArray(1 shl 16)
            while (true) {
                val entry = tar.nextEntry ?: break
                if (++entries > maxEntries) throw IOException("The package has too many files")
                val target = entryTarget(dest, entry.name) ?: throw IOException("The package has an unsafe path: ${entry.name}")
                if (entry.isDirectory) { target.mkdirs(); continue }
                target.parentFile?.mkdirs()
                if (entry.isSymbolicLink) {
                    if (!linkStaysInside(dest, target, entry.linkName)) throw IOException("The package has an unsafe link: ${entry.name}")
                    Files.createSymbolicLink(target.toPath(), File(entry.linkName).toPath()); continue
                }
                if (entry.isLink) {
                    val source = entryTarget(dest, entry.linkName) ?: throw IOException("The package has an unsafe link: ${entry.name}")
                    if (source.isFile) source.copyTo(target, overwrite = true)
                    continue
                }
                target.outputStream().buffered().use { out ->
                    while (true) {
                        val n = tar.read(buffer)
                        if (n < 0) break
                        written += n
                        if (written > maxBytes) throw IOException("The package is larger than it says")
                        out.write(buffer, 0, n)
                        if (written - reported >= (4L shl 20)) { reported = written; onBytes(written) }
                    }
                }
                if (entry.mode and 0b001_000_000 != 0) target.setExecutable(true, false)
            }
        }
        onBytes(written)
        return written
    }

    /** What the unpacked package must have to be run. */
    fun verify(folder: File, m: Manifest): String? {
        if (File(folder, "lib").listFiles { f -> f.name.startsWith("ld-musl-aarch64") }.isNullOrEmpty()) return "no musl loader"
        for (p in listOf("bnetserver", "worldserver", "mariadbd", "mapextractor", "vmap4extractor", "vmap4assembler", "mmaps_generator")) {
            val f = File(folder, "bin/$p")
            if (!f.isFile) return "no $p"
            if (!f.canExecute()) return "$p is not executable"
        }
        val commit = File(folder, "SOURCE_COMMIT").takeIf { it.isFile }?.readText()?.trim()
        if (commit != m.sourceCommit) return "the source commit ${commit ?: "(none)"} is not the manifest's ${m.sourceCommit}"
        for ((path, hash) in m.components) {
            val f = File(folder, path)
            if (!f.isFile || !ForeverDownloads.sha256(f).equals(hash, ignoreCase = true)) return "$path doesn't match the manifest"
        }
        return null
    }

    /** Free space the install needs: the unpacked size, the archive, and a margin. */
    fun spaceNeeded(m: Manifest): Long = m.unpacked + m.size + (256L shl 20)

    /**
     * Installs [m]: download, check, unpack beside, verify, swap (the old kept for a rollback). The databases, the keys and
     * the client are never touched. [say] gets (words, share done 0..1 or null).
     */
    fun install(layout: ForeverLayout, m: Manifest, say: (String, Float?) -> Unit, allowHttp: Boolean = false) {
        layout.root.mkdirs()
        val free = layout.root.usableSpace
        if (free in 1 until spaceNeeded(m)) throw IOException("Not enough space for Forever's server: about ${spaceNeeded(m) shr 20} MB are needed, ${free shr 20} MB are free.")
        val archive = File(layout.downloads, "forever-android-arm64-${m.sha256.take(12)}.tar.xz")
        ForeverDownloads.fetch(m.url, archive, m.sha256, m.size, allowHttp) { done, total ->
            say("Downloading Forever's server: ${done shr 20} / ${(if (total > 0) total else m.size) shr 20} MB", if (total > 0) done.toFloat() / total else null)
        }
        val staging = File(layout.root, "server.new")
        staging.deleteRecursively()
        val limit = if (m.unpacked > 0) m.unpacked + (m.unpacked shr 4) else 8L shl 30
        unpack(archive, staging, limit) { w -> say("Unpacking Forever's server: ${w shr 20} MB", if (m.unpacked > 0) w.toFloat() / m.unpacked else null) }
        val folder = File(staging, "forever").takeIf { it.isDirectory } ?: staging
        verify(folder, m)?.let { staging.deleteRecursively(); throw IOException("Forever's server package is not usable: $it") }
        val old = File(layout.root, "server.old")
        old.deleteRecursively()
        val hadOld = layout.server.exists()
        if (hadOld && !layout.server.renameTo(old)) throw IOException("The installed server couldn't be set aside")
        if (!folder.renameTo(layout.server)) {
            if (hadOld) old.renameTo(layout.server)
            staging.deleteRecursively()
            throw IOException("The new server couldn't be put in place")
        }
        // What the realm made in the server's folder goes on with it: the map data (hours of work on a phone, from 47 GB of game)
        // lives in `server/data`, and the server set aside is deleted after the next good start.
        val oldData = File(old, "data")
        if (hadOld && oldData.isDirectory && !layout.data.exists()) oldData.renameTo(layout.data)
        staging.deleteRecursively()
        layout.manifests.mkdirs()
        layout.installedManifest.writeText(manifestJson(m))
        etcList(layout).writeText(etcFiles(layout).joinToString("\n"))
        // The previous server stays as server.old until the next successful start ([commit]); a failed start restores it.
        archive.delete()
    }

    /** The package's own settings files as unpacked (`etc/...` paths), kept so one that goes missing can be seen and put back. */
    fun etcList(layout: ForeverLayout) = File(layout.manifests, "installed-etc.txt")

    private fun etcFiles(layout: ForeverLayout): List<String> =
        layout.etc.walkTopDown().filter { it.isFile }.map { it.relativeTo(layout.server).path.replace(File.separatorChar, '/') }.sorted().toList()

    /**
     * Puts back the package's settings files that are gone from the installed server (never over one that is there), from the
     * installed package's own archive. An earlier version deleted one at each Play (`worldserver.conf.d/zz-0-playerbot-defaults.conf`:
     * a file copied onto itself); a server installed before the list above was kept has the archive fetched once to make it.
     * Returns the files put back.
     */
    fun restoreEtc(layout: ForeverLayout, say: (String, Float?) -> Unit = { _, _ -> }, allowHttp: Boolean = false): List<String> {
        val m = installed(layout) ?: return emptyList()
        val list = etcList(layout)
        if (list.isFile && list.readLines().filter { it.isNotBlank() }.all { File(layout.server, it).isFile }) return emptyList()
        val archive = File(layout.downloads, "forever-android-arm64-${m.sha256.take(12)}.tar.xz")
        ForeverDownloads.fetch(m.url, archive, m.sha256, m.size, allowHttp) { done, total ->
            say("Checking Forever's server files: ${done shr 20} / ${(if (total > 0) total else m.size) shr 20} MB", if (total > 0) done.toFloat() / total else null)
        }
        val restored = ArrayList<String>(); val all = ArrayList<String>()
        TarArchiveInputStream(XZInputStream(archive.inputStream().buffered())).use { tar ->
            while (true) {
                val entry = tar.nextEntry ?: break
                val name = entry.name.removePrefix("./").removePrefix("forever/")
                if (entry.isDirectory || entry.isSymbolicLink || entry.isLink || !name.startsWith("etc/")) continue
                val target = entryTarget(layout.server, name) ?: continue
                all += name
                if (target.isFile) continue
                if (entry.size > (16L shl 20)) throw IOException("The package's $name is larger than a settings file is")
                target.parentFile?.mkdirs()
                target.outputStream().use { tar.copyTo(it) }
                restored += name
            }
        }
        layout.manifests.mkdirs()
        list.writeText(all.sorted().joinToString("\n"))
        archive.delete()
        return restored
    }

    /** After a successful start of the new server: the old one is no longer needed. */
    fun commit(layout: ForeverLayout) { File(layout.root, "server.old").deleteRecursively() }

    /** After the new server failed to start: puts the previous one back. True if there was one. */
    fun rollback(layout: ForeverLayout): Boolean {
        val old = File(layout.root, "server.old")
        if (!old.isDirectory) return false
        val failed = File(layout.root, "server.failed")
        failed.deleteRecursively()
        if (layout.server.exists()) layout.server.renameTo(failed)
        val ok = old.renameTo(layout.server)
        failed.deleteRecursively()
        return ok
    }

    fun manifestJson(m: Manifest): String = JSONObject()
        .put("arch", m.arch).put("libc", m.libc).put("format", m.format).put("schema", m.schema).put("min_app_version", m.minApp)
        .put("source_commit", m.sourceCommit).put("upstream_version", m.upstream).put("size", m.size).put("sha256", m.sha256)
        .put("unpacked", m.unpacked).put("url", m.url).put("client_builds", org.json.JSONArray(m.clientBuilds))
        .put("components", JSONObject(m.components)).toString()
}
