package com.logie.blizz.wowmodules

import com.logie.blizz.importer.deleteTree
import com.logie.blizz.wow.WowLayout
import org.apache.commons.compress.archivers.tar.TarArchiveInputStream
import org.apache.commons.compress.compressors.xz.XZCompressorInputStream
import java.io.File
import java.io.FilterInputStream
import java.io.IOException
import java.io.InputStream
import java.nio.file.Files
import java.nio.file.Paths
import java.security.MessageDigest

/**
 * A built realm's package (`server-<request>.tar.xz`, the workflow's `server/` folder) put in place
 * of the realm's own programs, Assembler-style: it is unpacked into a staging folder next to
 * `server`, checked, and only then swapped in; the old folder goes aside first and comes back if the
 * swap fails, so the realm is never half-written. The databases, configs, characters and client are
 * not in `server` and stay. What is in the old `server` that isn't in a package (`ctl.blizz.sh`,
 * `blizz/`) is written again at the realm's next start ([com.logie.blizz.wow.WowCtl.prepare]), and
 * text in the new package that names the WoW app's folder is moved to Blizzard's by the start too
 * ([com.logie.blizz.wow.WowPathRewrite]).
 *
 * The realm's own `server` (what the WoW app exported) is kept as the *stock* slot the first time a
 * modules realm goes in, so "the realm's own back" is a swap, not a download.
 *
 * Plain files only (no Context), so tests use a temporary folder.
 */
object RealmPackage {
    /** Written into `server` when a package is put in: which build it is (see [ModuleBuild.stamp]). */
    const val STAMP = ".blizz-modules"

    /** Where the folders of one realm are. */
    class Slots(
        /** The realm's programs (`WowLayout.server`). */
        val server: File,
        /** The package unpacked, before the swap. */
        val staging: File,
        /** The folder replaced, while the swap is under way. */
        val old: File,
        /** The realm's own `server`, kept while a modules realm is in. */
        val stock: File,
    ) {
        companion object {
            fun of(layout: WowLayout) = Slots(
                server = layout.server,
                staging = File(layout.root, "server.new"),
                old = File(layout.root, "server.old"),
                // Next to `files`, inside the game's folder: a re-import of the game takes it along.
                stock = File(layout.root.parentFile ?: layout.root, ".server-stock"),
            )
        }
    }

    /** What a package must hold to be a realm: the same files [WowLayout.isImported] needs, and musl's loader. */
    fun isRealm(server: File): Boolean =
        File(server, "ctl.sh").isFile && File(server, "bin/worldserver").isFile && File(server, "bin/mariadbd").isFile &&
            File(server, "bin/authserver").isFile &&
            File(server, "lib").listFiles { f -> f.name.startsWith("ld-musl-") && f.name.endsWith(".so.1") }.orEmpty().isNotEmpty()

    /** The build `server` holds, or null for a realm's own. */
    fun stampOf(server: File): String? = runCatching { File(server, STAMP).readText().trim() }.getOrNull()?.takeIf { it.isNotEmpty() }

    /** The file's SHA-256, as lowercase hex. */
    fun sha256(file: File): String {
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

    /**
     * Brings back what a swap that was cut short (the app stopped in the middle) left: no `server`
     * but a `server.old` that is a realm means the old one goes back; a staging folder goes.
     */
    fun recover(slots: Slots) {
        if (!slots.server.exists() && slots.old.exists() && isRealm(slots.old)) slots.old.renameTo(slots.server)
        if (slots.server.exists()) slots.old.deleteTree()
        slots.staging.deleteTree()
    }

    /** Unpacks [file] into the staging folder and checks it is a realm. Throws [IOException] for a package that isn't one; staging is left empty then. */
    fun unpackToStaging(file: File, slots: Slots, stamp: String, onProgress: (Float) -> Unit) {
        slots.staging.deleteTree()
        slots.staging.mkdirs()
        try {
            file.inputStream().use { unpack(it, file.length(), slots.staging, onProgress) }
            if (!isRealm(slots.staging)) throw IOException("Not a realm package (the server's programs aren't in it)")
            File(slots.staging, STAMP).writeText(stamp)
        } catch (e: Exception) {
            slots.staging.deleteTree()
            throw if (e is IOException) e else IOException(e.message ?: e.javaClass.simpleName, e)
        }
    }

    /**
     * Staging becomes `server`. The folder it replaces goes to the stock slot when it is a realm's
     * own (no stamp), otherwise it is deleted. If the swap fails the old
     * folder is back where it was.
     */
    fun commit(slots: Slots) {
        if (!slots.staging.isDirectory) throw IOException("Nothing unpacked to put in")
        slots.old.deleteTree()
        if (slots.server.exists() && !slots.server.renameTo(slots.old)) throw IOException("The old realm couldn't be moved aside")
        if (!slots.staging.renameTo(slots.server)) {
            slots.old.renameTo(slots.server)
            throw IOException("The new realm couldn't be put in place")
        }
        keepOrDrop(slots)
    }

    /** The folder just replaced (server.old): a realm's own (no stamp) is kept, in place of an older one kept; everything else goes. */
    private fun keepOrDrop(slots: Slots) {
        if (!slots.old.exists()) return
        val own = stampOf(slots.old) == null
        if (own && isRealm(slots.old)) {
            slots.stock.deleteTree()
            slots.stock.parentFile?.mkdirs()
            if (slots.old.renameTo(slots.stock)) return
        }
        slots.old.deleteTree()
    }

    /** The realm's own is kept and can be put back. */
    fun hasStock(slots: Slots): Boolean = slots.stock.isDirectory && isRealm(slots.stock)

    /** The kept realm's own `server` in place of the modules realm's; the modules realm goes. */
    fun restoreStock(slots: Slots) {
        if (!hasStock(slots)) throw IOException("The realm's own programs aren't kept on the phone any more")
        slots.old.deleteTree()
        if (slots.server.exists() && !slots.server.renameTo(slots.old)) throw IOException("The modules realm couldn't be moved aside")
        if (!slots.stock.renameTo(slots.server)) {
            slots.old.renameTo(slots.server)
            throw IOException("The realm's own couldn't be put back")
        }
        slots.old.deleteTree()
    }

    // The tar ---------------------------------------------------------------------------------------

    /** Entries are `server/...`; they go to `staging/...`. XZ's own checksums are checked as it is read. */
    internal fun unpack(input: InputStream, size: Long, staging: File, onProgress: (Float) -> Unit) {
        val counting = Counting(input)
        val total = size.coerceAtLeast(1L).toFloat()
        val base = staging.canonicalFile
        var reported = -1
        TarArchiveInputStream(XZCompressorInputStream(counting.buffered(1 shl 16))).use { tar ->
            while (true) {
                val entry = tar.nextEntry ?: break
                val relative = entry.name.removePrefix("./").removePrefix("server").trimStart('/')
                if (relative.isEmpty()) continue
                if (relative.startsWith("/") || relative.split('/').any { it == ".." }) throw IOException("Bad path in the realm package: ${entry.name}")
                val file = File(base, relative)
                // Nothing is written through a link a package made (a folder that is a link to elsewhere).
                val parent = file.parentFile
                if (parent != null) {
                    parent.mkdirs()
                    val real = parent.canonicalFile.path
                    if (real != base.path && !real.startsWith(base.path + File.separator)) throw IOException("Bad path in the realm package: ${entry.name}")
                }
                when {
                    entry.isDirectory -> file.mkdirs()
                    entry.isSymbolicLink -> {
                        Files.deleteIfExists(file.toPath())
                        Files.createSymbolicLink(file.toPath(), Paths.get(entry.linkName))
                    }
                    entry.isLink -> {
                        // A hard link: the same bytes again (its target was unpacked before it).
                        val target = File(base, entry.linkName.removePrefix("./").removePrefix("server").trimStart('/'))
                        if (!target.isFile || !target.canonicalFile.path.startsWith(base.path + File.separator)) {
                            throw IOException("Bad link in the realm package: ${entry.name}")
                        }
                        target.copyTo(file, overwrite = true)
                        if (entry.mode and 0b001_000_000 != 0) file.setExecutable(true, true)
                    }
                    else -> {
                        file.outputStream().use { tar.copyTo(it, 1 shl 16) }
                        if (entry.mode and 0b001_000_000 != 0) file.setExecutable(true, true)
                    }
                }
                val percent = (counting.count / total * 100).toInt()
                if (percent != reported) {
                    reported = percent
                    onProgress((counting.count / total).coerceIn(0f, 1f))
                }
            }
        }
    }

    private class Counting(input: InputStream) : FilterInputStream(input) {
        var count = 0L
            private set

        override fun read(): Int = super.read().also { if (it >= 0) count++ }

        override fun read(b: ByteArray, off: Int, len: Int): Int = super.read(b, off, len).also { if (it > 0) count += it }

        override fun skip(n: Long): Long = super.skip(n).also { count += it }
    }
}
