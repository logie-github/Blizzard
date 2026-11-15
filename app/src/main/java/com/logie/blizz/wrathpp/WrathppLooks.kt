package com.logie.blizz.wrathpp

import com.logie.blizz.BuildConfig
import java.io.File
import java.io.IOException
import java.util.zip.ZipInputStream

/**
 * Wrath++'s looks: Shadowlands' models, textures and character tables for the ten races of 3.3.5
 * (docs/wrathpp/SHADOWLANDS_OPTIONS.md), from the `wrathpp-looks` release (made by `wrathpp-looks.yml` with
 * `realm/warcraft/wrathpp/tools/sl_looks.py`: Blizzard's files, never in the repository). [install] puts them:
 *  - `client/` into Wrath++'s copy of the game as `Data/patch-Z.MPQ`, a folder the game reads as an archive, read after
 *    every other patch of that copy (the HD look's patch-W among them), so its models and tables are the ones drawn;
 *  - `dbc/` into Wrath++'s server's `share/dbc`, which `ctl.sh` (module_data) gives the world server over the game's
 *    tables, so a character is checked against the same skins, faces and hair as the game offers.
 * Nothing of Wrath+'s game or server. NOT run on a phone; [install] is unit-tested.
 */
object WrathppLooks {
    const val RELEASE = "wrathpp-looks"
    private const val BASE = "https://github.com/${BuildConfig.UPDATE_REPO}/releases/download/$RELEASE"
    const val PATCH = "patch-Z.MPQ"
    /** In the patch and in the server's dbc folder: the package's SHA-256, written last. */
    const val MARKER = "wrathpp-looks.stamp"
    /** In the patch folder (a folder the game reads as an archive: it ignores this one): the server's tables, to put back after a new server package. */
    const val SERVER_COPY = "wrathpp-server-dbc"

    /** The game's patch is [sha]'s and the server's tables aren't (a server package installed since): copied from the patch. */
    fun restoreServer(client: File, server: File, sha: String): Boolean {
        val patch = File(client, "Data/$PATCH")
        if (File(patch, MARKER).takeIf { it.isFile }?.readText()?.trim() != sha) return false
        // (a patch put in before the packages carried changes has no server copy: its DBFilesClient holds the package's whole
        // tables, the server's own)
        val dir = File(patch, SERVER_COPY).takeIf { it.isDirectory } ?: File(patch, "DBFilesClient")
        val tables = dir.listFiles { f -> f.isFile && f.name.endsWith(".dbc", ignoreCase = true) } ?: return false
        if (tables.none { it.name.equals("CharSections.dbc", ignoreCase = true) }) return false
        val dbcNew = File(server, "share/dbc.new").apply { deleteRecursively(); mkdirs() }
        try {
            for (t in tables) t.copyTo(File(dbcNew, t.name), overwrite = true)
            File(dbcNew, MARKER).writeText("$sha\n")
            swap(dbcNew, File(server, "share/dbc"))
        } finally {
            dbcNew.deleteRecursively()
        }
        return true
    }

    fun installedSha(client: File, server: File): String? {
        val a = File(client, "Data/$PATCH/$MARKER").takeIf { it.isFile }?.readText()?.trim()
        val b = File(server, "share/dbc/$MARKER").takeIf { it.isFile }?.readText()?.trim()
        return a?.takeIf { it.isNotEmpty() && it == b }
    }

    /**
     * Downloads and installs the newest looks into [client] (Wrath++'s copy of the game) and [server] (its server) when
     * they aren't the ones in. Offline with some in: kept. No release yet: an [IOException] (Wrath++ plays with the
     * game's own looks).
     */
    fun ensure(client: File, server: File, say: (String, Float?) -> Unit) {
        // The game's patch is in and the server's tables aren't (a server package put in since): the server's are put back from
        // the patch first, whatever is published, so that a failed download or a package this app can't take keeps the game and
        // its server on the same looks.
        File(client, "Data/$PATCH/$MARKER").takeIf { it.isFile }?.readText()?.trim()?.takeIf { it.isNotEmpty() }?.let { sha ->
            if (installedSha(client, server) == null) runCatching { restoreServer(client, server, sha) }
        }
        val published = runCatching { WrathppAddon.parseManifest(WrathppAddon.fetchText("$BASE/wrathpp-looks.json")) }.getOrElse { e ->
            if (installedSha(client, server) != null) return
            throw IOException("Wrath++'s looks couldn't be fetched (${e.message ?: e.javaClass.simpleName}); the release $RELEASE may not exist yet.")
        }
        if (published.sha256.equals(installedSha(client, server), ignoreCase = true)) return
        // A new server package took its share/ (and the tables with it): they are the patch's own, put back from there.
        if (restoreServer(client, server, published.sha256.lowercase())) return
        val zip = File(client.parentFile, "wrathpp-looks.zip.part")
        val free = (client.parentFile ?: client).usableSpace
        if (free in 1 until published.size * 3) {
            throw IOException("Not enough space for Wrath++'s looks: about ${published.size * 3 shr 20} MB is needed, ${free shr 20} MB is free.")
        }
        say("Downloading Shadowlands' looks for Wrath++", 0f)
        WrathppAddon.download("$BASE/wrathpp-looks.zip", zip) { done, total ->
            say("Downloading Shadowlands' looks for Wrath++: ${done shr 20} / ${total shr 20} MB", if (total > 0) done.toFloat() / total else null)
        }
        try {
            if (!WrathppAddon.sha256(zip).equals(published.sha256, ignoreCase = true)) {
                throw IOException("Wrath++'s looks download didn't match its checksum; try again.")
            }
            install(client, server, zip, published.sha256.lowercase(), progress = { n -> say("Putting in Wrath++'s looks: $n files", null) })
        } finally {
            zip.delete()
        }
    }

    /** The game's own table [name] (`DBFilesClient\\X.dbc`) as the game reads it: from the last archive of [data] that has it, this patch aside. */
    private fun gameTables(data: File): Pair<(String) -> ByteArray?, () -> Unit> {
        val game = com.logie.blizz.wowclient.Mpq.Game(data, skip = listOf(PATCH.lowercase()))
        val read: (String) -> ByteArray? = { name -> game.read(name) }
        val close: () -> Unit = { game.close() }
        return Pair(read, close)
    }

    /**
     * Installs the looks package [zip] (`client/...`: models, textures, sounds; `changes/<Table>.txt`: changes to the game's tables;
     * `dbc/...`: the server's tables). Each part is written beside its place and put in whole, the server's tables first and the
     * game's patch last; a part that fails leaves what was there. Paths leaving the package are refused. The changes are applied to
     * the tables the game reads ([tables]: the client's own, the HD look's patches' included) into the patch's DBFilesClient.
     */
    fun install(client: File, server: File, zip: File, sha: String, progress: (Int) -> Unit = {}, tables: ((String) -> ByteArray?)? = null) {
        val data = File(client, "Data")
        if (!data.isDirectory) throw IOException("Wrath++'s copy of the game has no Data folder")
        val changesNew = File(data, "$PATCH.changes").apply { deleteRecursively() }
        val patchNew = File(data, "$PATCH.new").apply { deleteRecursively() }
        val dbcDir = File(server, "share/dbc")
        val dbcNew = File(server, "share/dbc.new").apply { deleteRecursively() }
        var count = 0
        try {
            ZipInputStream(zip.inputStream().buffered()).use { z ->
                while (true) {
                    val entry = z.nextEntry ?: break
                    if (entry.isDirectory) continue
                    val name = entry.name.replace('\\', '/')
                    if (name.startsWith("/") || name.split('/').any { it == ".." || it.isEmpty() }) throw IOException("Bad path in the looks: ${entry.name}")
                    val out = when {
                        name.startsWith("client/") -> File(patchNew, name.removePrefix("client/"))
                        name.startsWith("dbc/") && !name.removePrefix("dbc/").contains('/') -> File(dbcNew, name.removePrefix("dbc/"))
                        name.startsWith("changes/") && name.endsWith(".txt") && !name.removePrefix("changes/").contains('/') -> File(changesNew, name.removePrefix("changes/"))
                        else -> continue
                    }
                    out.parentFile?.mkdirs()
                    out.outputStream().use { z.copyTo(it) }
                    if (++count % 500 == 0) progress(count)
                }
            }
            val changeFiles = changesNew.listFiles { f -> f.name.endsWith(".txt") }?.sortedBy { it.name }.orEmpty()
            if (!File(dbcNew, "CharSections.dbc").isFile || changeFiles.none { it.name == "CharSections.txt" }) {
                throw IOException("The looks package has no character tables")
            }
            val own = if (tables == null) gameTables(data) else null
            try {
                val read = tables ?: own!!.first
                File(patchNew, "DBFilesClient").mkdirs()
                for (f in changeFiles) {
                    val table = f.name.removeSuffix(".txt")
                    val bytes = read("DBFilesClient\\$table.dbc") ?: throw IOException("The game has no $table table to change")
                    val t = try { DbcTable(bytes).also { it.apply(f.readText()) } } catch (e: IOException) { throw IOException("$table: ${e.message}") }
                    File(patchNew, "DBFilesClient/$table.dbc").writeBytes(t.write())
                }
            } finally {
                own?.second?.invoke()
            }
            File(dbcNew, MARKER).writeText("$sha\n")
            File(patchNew, MARKER).writeText("$sha\n")
            File(patchNew, SERVER_COPY).mkdirs()
            dbcNew.listFiles { f -> f.name.endsWith(".dbc") }?.forEach { it.copyTo(File(patchNew, "$SERVER_COPY/${it.name}")) }
            swap(dbcNew, dbcDir)
            swap(patchNew, File(data, PATCH))
        } finally {
            patchNew.deleteRecursively()
            dbcNew.deleteRecursively()
            changesNew.deleteRecursively()
        }
    }

    private fun swap(made: File, place: File) {
        val old = File(place.path + ".old")
        old.deleteRecursively()
        if (place.exists() && !place.renameTo(old)) throw IOException("${place.path} couldn't be moved aside")
        if (!made.renameTo(place)) {
            old.renameTo(place)
            throw IOException("${place.path} couldn't be put in place")
        }
        old.deleteRecursively()
    }
}
