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
                if (parts.isEmpty()) "${setup.name} needs its data files: select the folder that holds it and them, not the installer alone."
                else "${setup.name} isn't an installer this app can unpack (it reads Inno Setup). Unpack it on another device, or give a zip, 7z or folder of the installed game.",
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
