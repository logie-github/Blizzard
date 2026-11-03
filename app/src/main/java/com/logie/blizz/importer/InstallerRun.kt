package com.logie.blizz.importer

import com.logie.blizz.game.LaunchProfile
import java.io.File

/**
 * Running a game's own installer in the app's Windows, for installers that make the game's files
 * only when they run (a repack unpacks them with its own Windows programs). The installer and its
 * data files are copied into [GamePaths.installer] (drive T: there), run silently with their
 * target folder `out`, and when they've finished the import takes the game from `out`.
 */
object InstallerRun {
    /** The installer's silent switches (Inno Setup's) and its target, `T:\<game>-installer\out`. */
    fun arguments(gameId: String) = "/SILENT /SUPPRESSMSGBOXES /NORESTART /DIR=T:\\$gameId-installer\\out"

    fun out(paths: GamePaths, gameId: String) = File(paths.installer(gameId), "out")

    /** The game's folder inside what the installer made, if it has finished. */
    fun finishedRoot(paths: GamePaths, gameId: String, isRoot: (Set<String>) -> Boolean, loose: (File) -> File?): File? {
        val out = out(paths, gameId)
        if (!out.isDirectory) return null
        return Packages.findRoot(out, 6, isRoot) ?: loose(out)
    }

    /** The installer program of [source] (a folder holding it, or the program itself) and the files beside it. */
    fun find(source: SourceNode): Pair<SourceNode, List<SourceNode>>? {
        if (source.isDirectory) {
            val holder = (listOf(source) + source.children().filter { it.isDirectory }).firstOrNull { Installers.setupIn(it.children()) != null } ?: return null
            val files = holder.children().filter { !it.isDirectory }
            return Installers.setupIn(files)!! to files
        }
        val siblings = source.localFile()?.parentFile?.listFiles()?.filter { it.isFile }?.map { FileNode(it) } ?: listOf(source)
        return source to siblings
    }

    /**
     * Copies the installer and its files into the app (files already there at their size are kept,
     * so a stopped copy resumes) and returns the installer there.
     */
    fun prepare(env: ImportEnv, gameId: String, source: SourceNode): File {
        val (setup, files) = find(source)
            ?: throw ImportException(Problem.MISSING_SOURCE_DATA, "There's no installer (Setup.exe) in what was picked. Pick the folder that holds it and its data files.")
        val dir = env.paths.installer(gameId)
        dir.mkdirs()
        val total = files.sumOf { it.size }
        // The copy, then the installed game (about as big again).
        FileValidator.requireSpace(dir, total * 2)
        var done = files.filter { File(dir, it.name).let { f -> f.isFile && f.length() == it.size } }.sumOf { it.size }
        for (file in files) {
            env.cancel.check()
            val target = File(dir, file.name)
            if (target.isFile && target.length() == file.size) continue
            env.progress(Progress(Stage.EXTRACTING, "Copying ${file.name} for the installer", done, total))
            val before = done
            copyInto(file, dir, file.name, env.cancel) { n -> done += n; env.progress(Progress(Stage.EXTRACTING, "Copying ${file.name} for the installer", done, total)) }
            done = before + file.size
        }
        return File(dir, setup.name)
    }

    /** The installer as a program to start, in the games' Windows (control profile: the game's screen shape, the touch controls of a point-and-click program). */
    fun entry(gameId: String, title: String, setup: File) = LibraryEntry(
        gameId = "installer",
        title = "$title installer",
        products = emptyList(),
        clientVersion = "",
        installPath = setup.parentFile!!.path,
        executable = setup.name,
        runtime = LibraryEntry.RUNTIME_WINLATOR,
        arguments = arguments(gameId),
        stage = Stage.NOT_INSTALLED,
        saveLocation = null,
        controlProfile = LaunchProfile.of(gameId).id,
    )
}
