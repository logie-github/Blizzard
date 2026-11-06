package com.logie.blizz.importer

import java.io.File
import java.io.IOException
import java.nio.file.FileVisitResult
import java.nio.file.Files
import java.nio.file.LinkOption
import java.nio.file.Path
import java.nio.file.SimpleFileVisitor
import java.nio.file.attribute.BasicFileAttributes

/**
 * Deletes [this] and, if it is a folder, what is in it, without ever following a symbolic link: a link is
 * deleted as a link, and what it points to stays. Kotlin's own deleteRecursively follows links into the folders
 * they point to (the World of Warcraft realm's folders have them: `data-modules`, the server's libraries), which
 * deletes what isn't in this folder at all, and crashes when a linked folder goes while it is being walked. A file
 * that can't be deleted is left and the rest goes on. True when nothing of it is left.
 */
fun File.deleteTree(): Boolean {
    val root = toPath()
    if (!Files.exists(root, LinkOption.NOFOLLOW_LINKS)) return true
    if (Files.isSymbolicLink(root) || !Files.isDirectory(root, LinkOption.NOFOLLOW_LINKS)) return runCatching { Files.deleteIfExists(root) }.isSuccess
    runCatching {
        Files.walkFileTree(root, object : SimpleFileVisitor<Path>() {
            override fun visitFile(file: Path, attrs: BasicFileAttributes): FileVisitResult {
                runCatching { Files.deleteIfExists(file) }
                return FileVisitResult.CONTINUE
            }

            override fun visitFileFailed(file: Path, exc: IOException): FileVisitResult {
                runCatching { Files.deleteIfExists(file) }
                return FileVisitResult.CONTINUE
            }

            override fun postVisitDirectory(dir: Path, exc: IOException?): FileVisitResult {
                runCatching { Files.deleteIfExists(dir) }
                return FileVisitResult.CONTINUE
            }
        })
    }
    return !Files.exists(root, LinkOption.NOFOLLOW_LINKS)
}

/** Every regular file under [this], never following a symbolic link (a linked folder isn't entered, a link isn't listed). */
fun File.filesNoLinks(): Sequence<File> {
    val root = toPath()
    if (!Files.isDirectory(root, LinkOption.NOFOLLOW_LINKS)) return if (Files.isRegularFile(root, LinkOption.NOFOLLOW_LINKS)) sequenceOf(this) else emptySequence()
    val out = ArrayList<File>()
    runCatching {
        Files.walkFileTree(root, object : SimpleFileVisitor<Path>() {
            override fun visitFile(file: Path, attrs: BasicFileAttributes): FileVisitResult {
                if (attrs.isRegularFile) out += file.toFile()
                return FileVisitResult.CONTINUE
            }

            override fun visitFileFailed(file: Path, exc: IOException) = FileVisitResult.CONTINUE
        })
    }
    return out.asSequence()
}
