// Ported from the World of Warcraft app's SafeFs (com.logie.warcraft.turtle.core), narrowed to one client's add-ons.
package com.logie.blizz.wowaddons

import java.io.File
import java.io.IOException
import java.nio.file.FileVisitResult
import java.nio.file.Files
import java.nio.file.LinkOption
import java.nio.file.Path
import java.nio.file.SimpleFileVisitor
import java.nio.file.StandardCopyOption
import java.nio.file.attribute.BasicFileAttributes

/**
 * Every delete, move and replace the add-on manager makes goes through here. It may touch only:
 *
 * - what is strictly inside one of [roots] (the client's `Interface` folder, and the folder a
 *   download waits in), or a [root] itself where it is only made ([mkdirs]);
 * - the [files] it keeps (the records) and their `.new`, `.old` and `.tmp` companions.
 *
 * A path that leaves these, by `..` or by a link in the middle, is refused ([Refused]) before
 * anything is touched, and deleting never follows a link: a link is removed as a link.
 */
class AddonGuard(roots: List<File>, files: List<File> = emptyList()) {
    class Refused(message: String) : IOException(message)

    private val roots: List<Path> = roots.map { it.toPath().toAbsolutePath().normalize() }
    private val files: List<Path> = files.flatMap { f ->
        listOf("", ".new", ".old", ".tmp").map { File(f.path + it).toPath().toAbsolutePath().normalize() }
    }

    /** [target] is allowed to be touched; returns it. Throws [Refused] if not. */
    fun check(target: File, allowRoot: Boolean = false): File {
        val path = target.toPath().toAbsolutePath().normalize()
        if (path in files) {
            val parent = path.parent ?: throw Refused("Not allowed: ${target.path}")
            val allowed = files.mapNotNull { it.parent }.any { realPath(it) == realPath(parent) }
            if (!allowed) throw Refused("Leads outside the add-on folders: ${target.path}")
            return target
        }
        val root = roots.firstOrNull { path.startsWith(it) && (allowRoot || path != it) }
            ?: throw Refused("Outside the add-on folders: ${target.path}")
        // The same as resolved: a link that leads out isn't fine.
        val realRoot = realPath(root)
        val real = realPath(path.parent ?: path).resolve(path.fileName ?: path)
        if (!real.startsWith(realRoot) || (!allowRoot && real == realRoot)) {
            throw Refused("Leads outside the add-on folders: ${target.path}")
        }
        return target
    }

    /** Deletes [target] and everything in it, without following links; nothing if it isn't there. */
    fun delete(target: File) {
        check(target)
        val path = target.toPath()
        if (!Files.exists(path, LinkOption.NOFOLLOW_LINKS)) return
        if (Files.isSymbolicLink(path) || !Files.isDirectory(path, LinkOption.NOFOLLOW_LINKS)) {
            Files.delete(path)
            return
        }
        Files.walkFileTree(path, object : SimpleFileVisitor<Path>() {
            override fun visitFile(file: Path, attrs: BasicFileAttributes): FileVisitResult {
                check(file.toFile())
                Files.delete(file)
                return FileVisitResult.CONTINUE
            }

            override fun visitFileFailed(file: Path, exc: IOException): FileVisitResult {
                check(file.toFile())
                if (Files.exists(file, LinkOption.NOFOLLOW_LINKS)) Files.delete(file)
                return FileVisitResult.CONTINUE
            }

            override fun postVisitDirectory(dir: Path, exc: IOException?): FileVisitResult {
                if (exc != null) throw exc
                check(dir.toFile())
                Files.delete(dir)
                return FileVisitResult.CONTINUE
            }
        })
    }

    /** Moves [source] to [target], both allowed ([target] must not be there). */
    fun move(source: File, target: File) {
        check(source)
        check(target)
        Files.move(source.toPath(), target.toPath(), StandardCopyOption.ATOMIC_MOVE)
    }

    /** Puts [source] in place of [target]: [target] is set aside first, so a failure leaves the old one. */
    fun replace(source: File, target: File) {
        check(source)
        check(target)
        val aside = File(target.path + ".old")
        check(aside)
        delete(aside)
        val hadTarget = Files.exists(target.toPath(), LinkOption.NOFOLLOW_LINKS)
        if (hadTarget) Files.move(target.toPath(), aside.toPath(), StandardCopyOption.ATOMIC_MOVE)
        try {
            Files.move(source.toPath(), target.toPath(), StandardCopyOption.ATOMIC_MOVE)
        } catch (e: IOException) {
            if (hadTarget) Files.move(aside.toPath(), target.toPath(), StandardCopyOption.ATOMIC_MOVE)
            throw e
        }
        delete(aside)
    }

    /** Makes [folder] (and its parents inside the roots); one that is there is left. */
    fun mkdirs(folder: File) {
        if (folder.isDirectory) return
        check(folder, allowRoot = true)
        Files.createDirectories(folder.toPath())
    }

    private fun realPath(path: Path): Path {
        var existing: Path? = path
        val rest = ArrayDeque<Path>()
        while (existing != null && !Files.exists(existing)) {
            existing.fileName?.let { rest.addFirst(it) }
            existing = existing.parent
        }
        var real = existing?.toRealPath() ?: path.root ?: path
        for (part in rest) real = real.resolve(part)
        return real.normalize()
    }
}
