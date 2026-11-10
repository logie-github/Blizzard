package com.logie.blizz.importer

import com.logie.blizz.game.LaunchProfile
import java.io.File
import java.io.InputStream

/** What [InstallerRun] needs from the phone's Windows: kept apart so the rest is plain Kotlin and unit-tested. */
interface InstallerHost {
    /** The games' Windows' C: drive (`<container>/.wine/drive_c`), if the Windows has been made. */
    fun wineDriveC(): File?

    /** The last lines Wine and Box64 printed ([com.logie.blizz.game.GameLog]). */
    fun logTail(): String
}

/**
 * Running a game's own installer in the app's Windows, for installers that make the game's files
 * only when they run (a repack unpacks them with its own Windows programs: ISDone, unarc, xtool).
 * The installer and its data files are copied into [GamePaths.installer] (drive T: there), run
 * silently with their target folder `out`, and when they've finished the import takes the game from
 * `out`, or from where the installer put it in Windows' C: drive when it ignored the folder.
 *
 * Generic over the game ([gameId] and the importer's own root tests); nothing here is StarCraft's.
 */
object InstallerRun {
    /** The id of the question "which folder holds the installer and its data files" ([PickKind.FOLDER]). */
    const val FOLDER_INPUT = "installer-folder"

    /**
     * The installer's silent switches. Inno Setup repacks differ in which they honour, so each run
     * tries the next set of these (the person taps Run the installer again when one did nothing).
     * `{DIR}` is the target folder; the last has none (the installer's own default folder, which is
     * then looked for in Windows' C: drive).
     */
    private val VARIANTS = listOf(
        "/SILENT /SUPPRESSMSGBOXES /NORESTART /SP- /NOCANCEL /DIR={DIR}",
        "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP- /NOCANCEL /LANG=english /DIR={DIR}",
        "/VERYSILENT /NORESTART /DIR={DIR}",
        "/SILENT /DIR={DIR}",
        "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP- /NOCANCEL",
    )
    val VARIANT_COUNT get() = VARIANTS.size

    /** The switches for the run numbered [attempt] (0 first; wraps round after the last), with the target `T:\<game>-installer\out`. */
    fun arguments(gameId: String, attempt: Int = 0) =
        VARIANTS[Math.floorMod(attempt, VARIANTS.size)].replace("{DIR}", "T:\\$gameId-installer\\out")

    fun out(paths: GamePaths, gameId: String) = File(paths.installer(gameId), "out")

    /** The game's folder inside what the installer made in `out`, if there is one (even while it's still being written). */
    fun finishedRoot(paths: GamePaths, gameId: String, isRoot: (Set<String>) -> Boolean, loose: (File) -> File?): File? {
        val out = out(paths, gameId)
        if (!out.isDirectory) return null
        return Packages.findRoot(out, 6, isRoot) ?: loose(out)
    }

    // ---- The files to copy ----

    /** The installer program of [source] (a folder holding it, or the program itself) and the files beside it. */
    fun find(source: SourceNode): Pair<SourceNode, List<SourceNode>>? {
        if (source.isDirectory) {
            val holder = (listOf(source) + source.children().filter { it.isDirectory }).firstOrNull { Installers.setupIn(it.children()) != null } ?: return null
            val files = holder.children().filter { !it.isDirectory }
            return Installers.setupIn(files)!! to files
        }
        val siblings = source.siblings()?.filter { !it.isDirectory } ?: listOf(source)
        return source to siblings
    }

    /** Smaller than this, an installer program with nothing beside it is a shell: a game's files are not inside it. */
    const val SHELL_MAX = 64L shl 20

    /**
     * True when [source] is an installer program picked by itself whose data files can't be seen
     * (a file from the document picker has no neighbours; a folder does), so the person must pick the folder.
     */
    fun needsFolder(source: SourceNode): Boolean {
        if (source.isDirectory) return false
        val (setup, files) = find(source) ?: return false
        return Installers.parts(setup, files).isEmpty() && setup.size < SHELL_MAX
    }

    /** The question to ask when [needsFolder]: names the files the installer needs. */
    fun folderQuestion(setupName: String) = MissingInput(
        FOLDER_INPUT,
        "$setupName is only the installer's shell: it makes the game from its data files (such as Data01.dxn and Data02.dxn), which sit beside it in the same folder. " +
            "A single file can't show what is next to it, so select the FOLDER that holds $setupName and its data files.",
        PickKind.FOLDER,
    )

    /** The folder or file to install from: the folder asked for after a lone installer, else the first pick. */
    fun sourceOf(supplied: Map<String, Supplied>, found: SourceNode?): SourceNode? =
        (supplied[FOLDER_INPUT] as? Supplied.Picked)?.source ?: (supplied["install"] as? Supplied.Picked)?.source ?: found

    // ---- The copy (resumable) ----

    private fun manifest(dir: File) = File(dir, "manifest.txt")
    private fun runFile(dir: File) = File(dir, "run.txt")

    /** What the copy should hold, from its manifest: the installer's name and each file's name and size. */
    data class Copy(val setup: String, val files: List<Pair<String, Long>>) {
        val total get() = files.sumOf { it.second }
    }

    fun readManifest(paths: GamePaths, gameId: String): Copy? = runCatching {
        val lines = manifest(paths.installer(gameId)).readLines().filter { it.isNotBlank() }
        val setup = lines.first().removePrefix("setup=")
        Copy(setup, lines.drop(1).map { it.substringBeforeLast('\t') to it.substringAfterLast('\t').toLong() })
    }.getOrNull()

    /** Bytes of [copy] already in place: whole files at their size, and the start of the one being copied. */
    fun copiedBytes(dir: File, copy: Copy): Long = copy.files.sumOf { (name, size) ->
        val whole = File(dir, name)
        if (whole.isFile && whole.length() == size) size else File(dir, ".$name.part").takeIf { it.isFile }?.length()?.coerceAtMost(size) ?: 0L
    }

    fun copyComplete(paths: GamePaths, gameId: String): Boolean {
        val copy = readManifest(paths, gameId) ?: return false
        val dir = paths.installer(gameId)
        return copy.files.all { (name, size) -> File(dir, name).let { it.isFile && it.length() == size } }
    }

    /**
     * Copies the installer and its files into the app and returns the installer there. Files already
     * there at their size are kept; a stopped copy goes on from the bytes of the file it was in,
     * so nothing complete is ever copied twice.
     */
    fun prepare(env: ImportEnv, gameId: String, source: SourceNode): File {
        val (setup, files) = find(source)
            ?: throw ImportException(Problem.MISSING_SOURCE_DATA, "There's no installer (Setup.exe) in what was picked. Pick the folder that holds it and its data files.")
        if (needsFolder(source)) {
            throw ImportException(Problem.MISSING_SOURCE_DATA, folderQuestion(setup.name).prompt)
        }
        val dir = env.paths.installer(gameId)
        dir.mkdirs()
        // Only the installer and its data files are copied: other files beside it (readmes, pictures) are not needed.
        val wanted = (listOf(setup) + Installers.parts(setup, files)).distinctBy { it.name }
        val total = wanted.sumOf { it.size }
        manifest(dir).writeText("setup=${setup.name}\n" + wanted.joinToString("\n") { "${it.name}\t${it.size}" } + "\n")
        val have = copiedBytes(dir, Copy(setup.name, wanted.map { it.name to it.size }))
        // What's still to copy, then the installed game (about as big again).
        FileValidator.requireSpace(dir, (total - have) + total)
        var done = have
        var lastReport = 0L
        fun report(label: String, force: Boolean = false) {
            val now = System.currentTimeMillis()
            if (force || now - lastReport >= 250) { lastReport = now; env.progress(Progress(Stage.EXTRACTING, label, done, total)) }
        }
        wanted.forEachIndexed { i, file ->
            env.cancel.check()
            val label = "Copying ${file.name} for the installer (${i + 1} of ${wanted.size})"
            val target = File(dir, file.name)
            if (target.isFile && target.length() == file.size) return@forEachIndexed
            report(label, force = true)
            copyResumable(file, target, env.cancel) { n -> done += n; report(label) }
        }
        env.progress(Progress(Stage.EXTRACTING, "Copied the installer's files", total, total))
        return File(dir, setup.name)
    }

    /** [source] into [target] through `.<name>.part`, going on from that file's length when it's already there. */
    fun copyResumable(source: SourceNode, target: File, cancel: CancelToken, onBytes: (Long) -> Unit) {
        target.parentFile?.mkdirs()
        val part = File(target.parentFile, ".${target.name}.part")
        val size = source.size
        var offset = if (part.isFile && part.length() <= size) part.length() else 0L
        source.open().use { input ->
            if (offset > 0 && !skipFully(input, offset)) offset = 0
            // A partial file the source can no longer be skipped into is started again, never half-trusted.
            val append = offset > 0
            if (!append) part.delete()
            java.io.FileOutputStream(part, append).buffered(1 shl 20).use { out ->
                val buffer = ByteArray(1 shl 18)
                while (true) {
                    cancel.check()
                    val n = input.read(buffer)
                    if (n < 0) break
                    out.write(buffer, 0, n)
                    onBytes(n.toLong())
                }
            }
        }
        if (size > 0 && part.length() != size) {
            throw java.io.IOException("${target.name} was copied only to ${part.length()} of $size bytes")
        }
        target.delete()
        if (!part.renameTo(target)) throw java.io.IOException("Couldn't write ${target.path}")
    }

    private fun skipFully(input: InputStream, count: Long): Boolean {
        var left = count
        while (left > 0) {
            val n = input.skip(left)
            if (n <= 0) {
                if (input.read() < 0) return false
                left--
            } else {
                left -= n
            }
        }
        return true
    }

    /** The copy and everything the installer made: gone (a Reset does this too). */
    fun removeCopy(paths: GamePaths, gameId: String) {
        paths.installer(gameId).deleteTree()
    }

    // ---- Runs ----

    /** A run of the installer was started: which switch set, and when. */
    data class RunRecord(val attempt: Int, val startedAt: Long)

    fun readRun(paths: GamePaths, gameId: String): RunRecord? = runCatching {
        val p = runFile(paths.installer(gameId)).readLines().associate { it.substringBefore('=') to it.substringAfter('=') }
        RunRecord(p.getValue("attempt").toInt(), p.getValue("started").toLong())
    }.getOrNull()

    /**
     * Notes that the installer is about to be started and returns the run: each start uses the next set
     * of switches (the person only starts it again when the last one did nothing).
     */
    fun beginRun(paths: GamePaths, gameId: String, now: Long = System.currentTimeMillis()): RunRecord {
        val previous = readRun(paths, gameId)
        val attempt = if (previous == null) 0 else previous.attempt + 1
        val record = RunRecord(attempt, now)
        runFile(paths.installer(gameId)).writeText("attempt=${record.attempt}\nstarted=${record.startedAt}\n")
        return record
    }

    /** The installer as a program to start, in the games' Windows (control profile: the game's screen shape, the touch controls of a point-and-click program). */
    fun entry(gameId: String, title: String, setup: File, attempt: Int = 0) = LibraryEntry(
        gameId = "installer",
        title = "$title installer",
        products = emptyList(),
        clientVersion = "",
        installPath = setup.parentFile!!.path,
        executable = setup.name,
        runtime = LibraryEntry.RUNTIME_WINLATOR,
        arguments = arguments(gameId, attempt),
        stage = Stage.NOT_INSTALLED,
        saveLocation = null,
        controlProfile = LaunchProfile.of(gameId).id,
    )

    // ---- Where it stands ----

    enum class Where { OUT, WINDOWS }

    /** How far the installer has got, from what is on disk. */
    sealed interface Status {
        /** Nothing copied. */
        data object None : Status
        /** An earlier copy stopped part-way: [done] of [total] bytes are in place. */
        data class PartialCopy(val done: Long, val total: Long) : Status
        /** The files are copied; the installer hasn't been run. */
        data class Ready(val total: Long) : Status
        /** It was started, and no game has appeared (yet, or at all: [attempt], [minutes] ago, [written] bytes in `out`). */
        data class Waiting(val attempt: Int, val minutes: Long, val written: Long, val log: String) : Status
        /** A game is being written (files changed in the last minutes): [written] bytes so far. */
        data class Installing(val written: Long, val where: Where) : Status
        /** A game's folder is there and has stopped changing. */
        data class Finished(val root: File, val where: Where) : Status
    }

    /** A game's folder is finished when nothing in it changed for this long. */
    const val QUIET_MS = 3 * 60_000L

    fun status(
        paths: GamePaths, gameId: String, isRoot: (Set<String>) -> Boolean, loose: (File) -> File?,
        host: InstallerHost?, now: Long = System.currentTimeMillis(),
    ): Status {
        val dir = paths.installer(gameId)
        if (!dir.isDirectory) return Status.None
        val copy = readManifest(paths, gameId) ?: return if (dir.list().isNullOrEmpty()) Status.None else Status.PartialCopy(0, 0)
        if (!copyComplete(paths, gameId)) return Status.PartialCopy(copiedBytes(dir, copy), copy.total)
        val found = finishedRoot(paths, gameId, isRoot, loose)?.to(Where.OUT)
            ?: host?.wineDriveC()?.let { c -> findInWindows(c, isRoot, loose) }?.to(Where.WINDOWS)
        if (found != null) {
            val (root, where) = found
            val newest = newestWrite(root)
            return if (now - newest >= QUIET_MS) Status.Finished(root, where) else Status.Installing(sizeOf(root), where)
        }
        val run = readRun(paths, gameId) ?: return Status.Ready(copy.total)
        return Status.Waiting(run.attempt, ((now - run.startedAt) / 60_000).coerceAtLeast(0), sizeOf(out(paths, gameId)), host?.logTail().orEmpty())
    }

    private fun newestWrite(root: File): Long = root.walkTopDown().maxDepth(14).maxOf { it.lastModified() }

    private fun sizeOf(dir: File): Long = if (dir.isDirectory) dir.walkTopDown().filter { it.isFile }.sumOf { it.length() } else 0L

    /**
     * A game some installers put in Windows' own C: drive (Program Files, Program Files (x86),
     * Blizzard Entertainment, a user's folders) when they ignore the target folder.
     */
    fun findInWindows(driveC: File, isRoot: (Set<String>) -> Boolean, loose: (File) -> File?): File? {
        val tops = driveC.listFiles().orEmpty().filter { it.isDirectory && !java.nio.file.Files.isSymbolicLink(it.toPath()) && !it.name.equals("windows", true) }
        // Program Files first, then users, then anything else (C:\Games, C:\StarCraft II).
        val ordered = tops.sortedBy { when { it.name.startsWith("Program Files", true) -> 0; it.name.equals("users", true) -> 1; else -> 2 } }
        for (top in ordered) (Packages.findRoot(top, 6, isRoot) ?: loose(top))?.let { return it }
        return null
    }

    /**
     * When the installer wrote its game in Windows' C: drive and `out` holds none, moves it into `out`
     * (so the import finds it there) and returns it. Not while the game is still being written.
     */
    fun collect(
        paths: GamePaths, gameId: String, isRoot: (Set<String>) -> Boolean, loose: (File) -> File?,
        host: InstallerHost?, now: Long = System.currentTimeMillis(),
    ): File? {
        if (finishedRoot(paths, gameId, isRoot, loose) != null) return null
        val c = host?.wineDriveC() ?: return null
        val root = findInWindows(c, isRoot, loose) ?: return null
        if (now - newestWrite(root) < QUIET_MS) return null
        val target = File(out(paths, gameId), root.name.ifEmpty { "game" })
        target.parentFile?.mkdirs()
        if (!root.renameTo(target)) {
            FileValidator.requireSpace(target.parentFile!!, sizeOf(root))
            root.copyRecursively(target, true)
            root.deleteTree()
        }
        return target
    }

    /** What the person is told for each [Status]: (headline, detail). */
    fun describe(status: Status, setup: String = "the installer"): Pair<String, String?> = when (status) {
        Status.None -> "" to null
        is Status.PartialCopy -> "A copy of the installer's files was stopped part-way (${FileValidator.gb(status.done)} of ${FileValidator.gb(status.total)})." to
            "Tap Run the installer to go on copying from where it stopped; files already copied are kept. Or remove the copy."
        is Status.Ready -> "The installer's files are copied (${FileValidator.gb(status.total)})." to "Tap Run the installer."
        is Status.Waiting -> "The installer is running." to
            ("When it ends, tap Retry. Unpacking a large game takes a long while (it can be an hour) and shows nothing on screen until then. " +
                (if (status.written == 0L && status.minutes >= 5)
                    "Nothing has been written yet after ${status.minutes} minutes: it may have ended without installing. Tap Run the installer to try other switches (set ${status.attempt + 1} of $VARIANT_COUNT was used)."
                else "Written so far: ${FileValidator.gb(status.written)}."))
        is Status.Installing -> "The installer is still writing the game (${FileValidator.gb(status.written)} so far)." to "Wait until it has finished, then tap Retry."
        is Status.Finished -> "The installer has finished." to
            (if (status.where == Where.WINDOWS) "It put the game in the app's Windows (not in the folder it was given); it will be taken from there. " else "") + "Tap Import what it installed."
    }
}
