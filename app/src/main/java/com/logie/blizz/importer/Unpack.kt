package com.logie.blizz.importer

import org.apache.commons.compress.archivers.sevenz.SevenZFile
import org.apache.commons.compress.archivers.tar.TarArchiveInputStream
import org.apache.commons.compress.compressors.bzip2.BZip2CompressorInputStream
import org.apache.commons.compress.compressors.gzip.GzipCompressorInputStream
import org.apache.commons.compress.compressors.xz.XZCompressorInputStream
import org.apache.commons.compress.compressors.zstandard.ZstdCompressorInputStream
import java.io.File
import java.io.InputStream
import java.nio.file.Files

/** What a file the person picked is, from its first bytes (never its name). */
enum class Format(val label: String) {
    ZIP("zip"), SEVEN_Z("7z"), TAR("tar"), TAR_GZ("tar.gz"), TAR_XZ("tar.xz"), TAR_BZ2("tar.bz2"), TAR_ZST("tar.zst"),
    ISO("disc image"), RAR("RAR"), PROGRAM("Windows program"), UNKNOWN("unknown");

    companion object {
        /** The format of [node]'s first [HEAD] bytes. Plain Kotlin, unit-tested. */
        fun of(head: ByteArray): Format {
            fun at(offset: Int, vararg bytes: Int) = head.size >= offset + bytes.size && bytes.indices.all { (head[offset + it].toInt() and 0xff) == bytes[it] }
            return when {
                at(0, 'P'.code, 'K'.code, 3, 4) || at(0, 'P'.code, 'K'.code, 5, 6) -> ZIP
                at(0, 0x37, 0x7A, 0xBC, 0xAF, 0x27, 0x1C) -> SEVEN_Z
                at(0, 0x1F, 0x8B) -> TAR_GZ
                at(0, 0xFD, 0x37, 0x7A, 0x58, 0x5A, 0x00) -> TAR_XZ
                at(0, 'B'.code, 'Z'.code, 'h'.code) -> TAR_BZ2
                at(0, 0x28, 0xB5, 0x2F, 0xFD) -> TAR_ZST
                at(0, 'R'.code, 'a'.code, 'r'.code, '!'.code, 0x1A, 0x07) -> RAR
                at(257, 'u'.code, 's'.code, 't'.code, 'a'.code, 'r'.code) -> TAR
                at(32769, 'C'.code, 'D'.code, '0'.code, '0'.code, '1'.code) -> ISO
                at(0, 'M'.code, 'Z'.code) -> PROGRAM
                else -> UNKNOWN
            }
        }

        const val HEAD = 32_776

        fun of(node: SourceNode): Format {
            if (node.isDirectory) return UNKNOWN
            val head = node.open().use { input ->
                val buffer = ByteArray(HEAD)
                var n = 0
                while (n < HEAD) { val r = input.read(buffer, n, HEAD - n); if (r < 0) break; n += r }
                buffer.copyOf(n)
            }
            return of(head)
        }
    }
}

/**
 * Unpacks whatever the person gives: a zip, a 7z, a tar (plain, gz, xz, bz2 or zst), a disc image
 * (ISO), or an installer program with its data files beside it (Inno Setup, which innoextract
 * reads without running it; the data files can have any name or extension, they're matched by
 * order). The format comes from the file's first bytes. Everything lands under [dest] by
 * [SafePaths]; nothing from inside an archive is ever run.
 */
class Unpacker(private val innoextract: Innoextract?) {
    /**
     * [source] into [dest]. [siblings] are the files beside [source] (an installer's data), when
     * they can be seen; [scratch] is where a copy of [source] goes for formats that need one.
     */
    fun unpack(source: SourceNode, siblings: List<SourceNode>, dest: File, scratch: File, cancel: CancelToken, progress: (Progress) -> Unit) {
        dest.mkdirs()
        val format = Format.of(source)
        val total = source.size.coerceAtLeast(1)
        var done = 0L
        val count = { n: Long -> done += n; progress(Progress(Stage.EXTRACTING, "Unpacking ${source.name}", done.coerceAtMost(total), total)) }
        progress(Progress(Stage.EXTRACTING, "Unpacking ${source.name} (${format.label})"))
        when (format) {
            Format.ZIP -> source.open().use { ZipExtractor.extract(it, dest, cancel, onBytes = count) }
            Format.TAR -> source.open().use { tar(it, dest, cancel, count) }
            Format.TAR_GZ -> source.open().use { tar(GzipCompressorInputStream(it.buffered()), dest, cancel, count) }
            Format.TAR_XZ -> source.open().use { tar(XZCompressorInputStream(it.buffered()), dest, cancel, count) }
            Format.TAR_BZ2 -> source.open().use { tar(BZip2CompressorInputStream(it.buffered()), dest, cancel, count) }
            Format.TAR_ZST -> source.open().use { tar(ZstdCompressorInputStream(it.buffered()), dest, cancel, count) }
            Format.SEVEN_Z -> sevenZ(localCopy(source, scratch, cancel), dest, cancel, count)
            Format.ISO -> iso(localCopy(source, scratch, cancel), dest, cancel, count)
            Format.PROGRAM -> installer(source, siblings, dest, scratch, cancel, progress)
            Format.RAR -> throw ImportException(Problem.UNSUPPORTED_INSTALLER, "${source.name} is a RAR archive, which this app can't open. Pack it as a zip or 7z, or unpack it to a folder and select the folder.")
            Format.UNKNOWN -> throw ImportException(Problem.UNSUPPORTED_INSTALLER, "${source.name} isn't a zip, 7z, tar, disc image or installer this app can read.")
        }
    }

    private fun tar(input: InputStream, dest: File, cancel: CancelToken, onBytes: (Long) -> Unit) {
        val tar = try { TarArchiveInputStream(input) } catch (e: java.io.IOException) { throw ImportException(Problem.CORRUPT_ARCHIVE, "The archive is damaged.", e.message, e) }
        var any = false
        try {
            while (true) {
                val entry = tar.nextEntry ?: break
                cancel.check()
                any = true
                val target = SafePaths.resolve(dest, entry.name)
                if (entry.isDirectory) { target.mkdirs(); continue }
                if (!entry.isFile) continue
                copyStream(tar, target, cancel, onBytes)
            }
        } catch (e: java.io.IOException) {
            throw ImportException(Problem.CORRUPT_ARCHIVE, "The archive is damaged or isn't a tar archive.", e.message, e)
        }
        if (!any) throw ImportException(Problem.CORRUPT_ARCHIVE, "The archive is empty, or isn't a tar archive.")
    }

    private fun sevenZ(file: File, dest: File, cancel: CancelToken, onBytes: (Long) -> Unit) {
        try {
            SevenZFile.builder().setFile(file).get().use { z ->
                while (true) {
                    val entry = z.nextEntry ?: break
                    cancel.check()
                    val target = SafePaths.resolve(dest, entry.name)
                    if (entry.isDirectory) { target.mkdirs(); continue }
                    copyStream(object : InputStream() {
                        override fun read(): Int = z.read()
                        override fun read(b: ByteArray, off: Int, len: Int): Int = z.read(b, off, len)
                    }, target, cancel, onBytes)
                }
            }
        } catch (e: java.io.IOException) {
            throw ImportException(Problem.CORRUPT_ARCHIVE, "The 7z archive is damaged, or encrypted.", e.message, e)
        }
    }

    private fun iso(file: File, dest: File, cancel: CancelToken, onBytes: (Long) -> Unit) {
        val image = Iso9660(file)
        for ((path, entry) in image.files()) {
            cancel.check()
            image.open(entry).use { copyStream(it, SafePaths.resolve(dest, path), cancel, onBytes) }
        }
    }

    /**
     * An installer (Inno Setup) and the data files beside it, which can be named anything (Data01.dxn,
     * Data02.dxn...): they're given the names innoextract looks for (<installer>-1.bin, -2.bin...) in
     * [scratch], by symbolic link where the files are on this phone, by copy otherwise.
     */
    private fun installer(setup: SourceNode, siblings: List<SourceNode>, dest: File, scratch: File, cancel: CancelToken, progress: (Progress) -> Unit) {
        val tool = innoextract ?: throw ImportException(Problem.MISSING_RUNTIME_DEPENDENCY, "innoextract is missing from this build of the app.")
        val parts = Installers.parts(setup, siblings)
        // A shell with no data files beside it can't hold a game: said before any work is done.
        if (parts.isEmpty() && setup.size < InstallerRun.SHELL_MAX) {
            throw ImportException(
                Problem.UNSUPPORTED_INSTALLER,
                "${setup.name} needs its data files: select the folder that holds it and them (such as Data01.dxn), not the installer alone.",
                "${setup.name} is ${setup.size shr 10} KB and no data files were visible beside it (a file from the document picker has no neighbours; a folder does).",
            )
        }
        val base = setup.name.substringBeforeLast('.')
        val dir = File(scratch, "installer").also { it.deleteRecursively(); it.mkdirs() }
        val exe = File(dir, "$base.exe")
        var copied = 0L
        val needed = parts.sumOf { it.size } + setup.size
        fun place(node: SourceNode, target: File) {
            val local = node.localFile()
            val linked = local != null && runCatching { Files.createSymbolicLink(target.toPath(), local.toPath()) }.isSuccess
            if (!linked) {
                FileValidator.requireSpace(dir, needed - copied)
                node.open().use { copyStream(it, target, cancel) { n -> copied += n; progress(Progress(Stage.EXTRACTING, "Copying ${node.name}", copied, needed)) } }
            }
        }
        place(setup, exe)
        parts.forEachIndexed { i, part -> place(part, File(dir, "$base-${i + 1}.bin")) }
        progress(Progress(Stage.EXTRACTING, "Unpacking ${setup.name} (installer, ${parts.size} data files)"))
        try {
            tool.extract(exe, dest, cancel)
        } catch (e: ImportException) {
            if (e.problem != Problem.UNSUPPORTED_INSTALLER) throw e
            throw ImportException(
                Problem.UNSUPPORTED_INSTALLER,
                "${setup.name} isn't an installer this app can unpack (it reads Inno Setup). Unpack it on another device, or give a zip, 7z or folder of the installed game.",
                e.detail, e,
            )
        } finally {
            dir.deleteRecursively()
        }
    }
}

object Installers {
    /** Data files an installer program is made of: the big non-program files beside it, in natural order. */
    fun parts(setup: SourceNode, siblings: List<SourceNode>): List<SourceNode> =
        siblings.filter { s ->
            !s.isDirectory && s.name != setup.name && s.size >= (1L shl 20) &&
                s.name.substringAfterLast('.', "").lowercase() !in setOf("exe", "dll", "msi", "txt", "nfo", "url", "ini", "md5", "sfv", "sha1", "sha256", "jpg", "png", "pdf")
        }.sortedWith(compareBy({ natural(it.name) }, { it.name.lowercase() }))

    /** The number in a name ("Data02.dxn" → 2), for ordering. */
    private fun natural(name: String): Long = Regex("\\d+").findAll(name.substringBeforeLast('.')).lastOrNull()?.value?.toLongOrNull() ?: Long.MAX_VALUE

    /** The installer program in [files], if there's one: "setup*.exe" (the shallowest), else the only .exe. */
    fun setupIn(files: List<SourceNode>): SourceNode? {
        val exes = files.filter { !it.isDirectory && it.name.endsWith(".exe", true) }
        return exes.firstOrNull { it.name.startsWith("setup", true) } ?: exes.singleOrNull()
    }
}

/**
 * A game's folder out of whatever the person gave ([Unpacker]'s formats, or an installed folder):
 * the shared first half of the importers that take a package (StarCraft II, StarCraft Remastered).
 */
object Packages {
    /** A folder's own entry names, lower-case, folders ending in "/": what [isRoot] looks at. */
    fun names(children: List<SourceNode>): Set<String> = children.map { it.name.lowercase() + if (it.isDirectory) "/" else "" }.toSet()

    /** The first folder under [node] (to [depth] down) whose entries [isRoot] approves of. */
    fun findRoot(node: SourceNode, depth: Int, isRoot: (Set<String>) -> Boolean): SourceNode? {
        if (!node.isDirectory || depth < 0) return null
        val children = runCatching { node.children() }.getOrDefault(emptyList())
        if (isRoot(names(children))) return node
        return children.filter { it.isDirectory }.firstNotNullOfOrNull { findRoot(it, depth - 1, isRoot) }
    }

    /** The same on a folder on this phone. */
    fun findRoot(dir: File, depth: Int, isRoot: (Set<String>) -> Boolean): File? =
        dir.walkTopDown().maxDepth(depth).firstOrNull { it.isDirectory && isRoot(names(it)) }

    private fun names(dir: File): Set<String> = dir.listFiles().orEmpty().map { it.name.lowercase() + if (it.isDirectory) "/" else "" }.toSet()

    /**
     * The game's folder from [source]: an installed folder (copied to a folder of its own under
     * [scratch]), a zip, 7z, tar, disc image, or installer with its data files (unpacked there).
     * [checkFound] and [checkUnpacked] refuse a wrong version before the gigabytes are copied and
     * after they're unpacked. [what] names the game for the person.
     */
    fun materialize(
        source: SourceNode, env: ImportEnv, staging: File, scratch: File, what: String, prompt: String,
        isRoot: (Set<String>) -> Boolean, checkFound: (SourceNode) -> Unit = {}, checkUnpacked: (File) -> Unit = {},
        looseRoot: (File) -> File? = { null },
    ): File {
        val out = File(scratch, "game").also { it.deleteRecursively(); it.mkdirs() }
        val found: SourceNode?
        val setup: SourceNode?
        val siblings: List<SourceNode>
        if (source.isDirectory) {
            found = findRoot(source, 6, isRoot)
            if (found == null) {
                // No game in it: an installer and its data files, in it or in a folder just under it.
                val holder = (listOf(source) + source.children().filter { it.isDirectory }).firstOrNull { Installers.setupIn(it.children()) != null }
                siblings = holder?.children() ?: emptyList()
                setup = Installers.setupIn(siblings)
            } else {
                setup = null
                siblings = emptyList()
            }
        } else {
            found = null
            setup = source
            siblings = source.localFile()?.parentFile?.listFiles()?.map { FileNode(it) } ?: emptyList()
        }
        if (found != null) {
            checkFound(found)
            val total = found.walk(12).sumOf { it.size }
            FileValidator.requireSpace(staging, total)
            copyTree(found, out, env, total, what)
            return out
        }
        val package_ = setup ?: throw ImportException(Problem.MISSING_SOURCE_DATA, "There's no $what in that folder (and no installer). $prompt")
        FileValidator.requireSpace(scratch, (package_.size + siblings.sumOf { it.size }).coerceAtLeast(1L shl 30) + (2L shl 30))
        Unpacker(env.innoextract).unpack(package_, siblings, out, scratch, env.cancel, env.progress)
        // The strict shape first; then a wildcard search for the game's own markers wherever they landed
        // (any depth, any case); then archives inside what was unpacked, unpacked in turn.
        var root = findRoot(out, 6, isRoot) ?: looseRoot(out)
        if (root == null) root = unpackNested(out, env, scratch, isRoot, looseRoot)
        if (root == null) {
            // A repack's installer only runs its own unpacker over the data files: innoextract gets the
            // installer's little files, and the game stays inside a FreeArc archive (signature "ArC", 1).
            val heads = siblings.filter { !it.isDirectory && it.size >= (1L shl 20) }.take(6).map { it.name to headOf(it) }
            val arc = heads.firstOrNull { (_, h) -> h.size >= 4 && h[0] == 'A'.code.toByte() && h[1] == 'r'.code.toByte() && h[2] == 'C'.code.toByte() && h[3] == 1.toByte() }
            val headText = heads.joinToString("; ") { (n, h) -> "$n starts ${h.take(8).joinToString(" ") { "%02x".format(it) }}" }
            val repack = out.walkTopDown().maxDepth(4).any { it.isFile && it.name.lowercase() in setOf("unarc.dll", "isdone.dll", "cls-lolz_x64.exe", "xt22.exe") }
            // An installer that unpacked to no game (a repack's, which unpacks the game with Windows programs
            // when it runs): it's run in the app's Windows, which is what it's made for.
            if (repack || (arc != null) || Format.of(package_) == Format.PROGRAM) {
                throw ImportException(
                    Problem.INSTALLER_MUST_RUN,
                    "${package_.name} makes the game's files when it runs (it unpacks them with its own Windows programs). The app can run it for you in its Windows: tap Run the installer.",
                    "Data files: $headText${outline(out)}",
                )
            }
            throw ImportException(
                Problem.MISSING_SOURCE_DATA,
                "${package_.name} has no $what in it once unpacked. $prompt",
                "Data files: $headText\nUnpacked: ${outline(out)}",
            )
        }
        checkUnpacked(root)
        return root
    }

    /** Archives inside the unpacked files (a zip, 7z, tar or disc image holding the game), unpacked beside them, then looked through again. */
    private fun unpackNested(out: File, env: ImportEnv, scratch: File, isRoot: (Set<String>) -> Boolean, looseRoot: (File) -> File?): File? {
        val archives = out.walkTopDown().maxDepth(8).filter { it.isFile && it.length() >= (1L shl 16) }
            .filter { runCatching { Format.of(FileNode(it)) }.getOrDefault(Format.UNKNOWN) in NESTED }.take(6).toList()
        for ((i, archive) in archives.withIndex()) {
            val into = File(scratch, "nested-$i").also { it.deleteRecursively(); it.mkdirs() }
            runCatching { Unpacker(env.innoextract).unpack(FileNode(archive), emptyList(), into, scratch, env.cancel, env.progress) }
                .onFailure { if (it is ImportException && it.problem == Problem.CANCELLED) throw it }
            (findRoot(into, 6, isRoot) ?: looseRoot(into))?.let { return it }
        }
        return null
    }

    private fun headOf(node: SourceNode): ByteArray = runCatching {
        node.open().use { input -> ByteArray(16).let { b -> b.copyOf(input.read(b).coerceAtLeast(0)) } }
    }.getOrDefault(ByteArray(0))

    private val NESTED = setOf(Format.ZIP, Format.SEVEN_Z, Format.TAR, Format.TAR_GZ, Format.TAR_XZ, Format.TAR_BZ2, Format.TAR_ZST, Format.ISO)

    /** What an unpacked folder holds, briefly (folders with their file counts to three levels, the biggest files), for the error details. */
    fun outline(dir: File): String {
        val lines = ArrayList<String>()
        fun walk(d: File, depth: Int) {
            val kids = d.listFiles()?.sortedBy { it.name.lowercase() } ?: return
            for (k in kids.filter { it.isDirectory }.take(12)) {
                lines += "${"  ".repeat(depth)}${k.name}/ (${k.walkTopDown().count { it.isFile }} files)"
                if (depth < 2) walk(k, depth + 1)
            }
        }
        walk(dir, 0)
        val big = dir.walkTopDown().filter { it.isFile }.sortedByDescending { it.length() }.take(8).map { "${it.relativeTo(dir).path} (${it.length() shr 20} MB)" }
        return "\n" + lines.take(40).joinToString("\n") + "\nLargest: " + big.joinToString("; ")
    }

    private fun copyTree(root: SourceNode, into: File, env: ImportEnv, total: Long, what: String) {
        var done = 0L
        fun walk(node: SourceNode, to: File, depth: Int) {
            for (child in node.children()) {
                env.cancel.check()
                if (child.isDirectory) {
                    if (depth < 12) walk(child, File(to, child.name), depth + 1)
                } else {
                    copyInto(child, to, child.name, env.cancel) { n ->
                        done += n
                        env.progress(Progress(Stage.EXTRACTING, "Copying $what", done, total))
                    }
                }
            }
        }
        walk(root, into, 0)
    }
}
