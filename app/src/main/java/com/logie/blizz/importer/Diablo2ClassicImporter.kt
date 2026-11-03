package com.logie.blizz.importer

import java.io.File

/**
 * Diablo II with Lord of Destruction, the original 1.14 client. From Blizzard's own legacy servers
 * (blizzard-legacy-dl: the base game, then the expansion over it, as Blizzard's installers do; each
 * piece checked against its hash), or an installation the person has (a folder or a zip of it).
 * No CD key is asked for: single player doesn't need one. Saved games live in the games' Windows
 * (C:\users\xuser\Saved Games\Diablo II), apart from the game folder, so a repair can't touch them.
 */
class Diablo2ClassicImporter : GameImporter {
    override val gameId = "diablo2"
    override val title = "Diablo II"

    companion object {
        const val EXE = "Game.exe"
        val BASE = listOf("d2data.mpq", "d2char.mpq", "d2sfx.mpq", "d2music.mpq", "d2speech.mpq", "d2video.mpq", "patch_d2.mpq")
        val EXPANSION = listOf("d2exp.mpq", "d2xmusic.mpq", "d2xtalk.mpq", "d2xvideo.mpq")
        /** The movie archives: the intro, the act cinematics and the expansion's. Without them the game plays no movies. */
        val MOVIES = listOf("d2video.mpq", "d2xvideo.mpq")
        /**
         * The libraries 1.14b's Game.exe imports besides Windows' own (binkw32 and smackw32 play the movies, ijl11 reads
         * the JPEGs), and the language file; 1.14 folded the older D2*.dll files into Game.exe.
         */
        val NATIVE = listOf("binkw32.dll", "smackw32.dll", "ijl11.dll", "D2.LNG")
        /** 1.14 (1.14b is what Blizzard serves, 1.14.1.68; 1.14d is 1.14.3.71). */
        fun supported(version: String?): Boolean = version != null && version.startsWith("1.14.")
        const val SIZE = 2_150L shl 20
        const val PROMPT_INSTALL = "Select your Diablo II folder (with Game.exe and d2data.mpq) or a zip of it — or connect to the internet and retry to download it from Blizzard."
        const val PROMPT_EXPANSION = "Lord of Destruction data is missing (d2exp.mpq). Select your Diablo II folder with Lord of Destruction installed, or retry online to download it from Blizzard."
        const val MARK = ".from-blizzard"
        /** Where 1.14 keeps saved games, inside the games' Windows. */
        const val SAVE_DIR = "C:\\users\\xuser\\Saved Games\\Diablo II"
    }

    override fun detect(env: ImportEnv): Detection {
        env.progress(Progress(Stage.DETECTING, "Looking for Diablo II"))
        val scan = Scan(env.searchRoots())
        val found = LinkedHashMap<String, SourceNode>()
        // A folder with Game.exe and d2data.mpq: an existing installation.
        val roots = env.searchRoots()
        val install = roots.firstNotNullOfOrNull { root -> findInstall(root, 4) }
        if (install != null) found["install"] = install
        scan.matching(Regex("diablo.?ii.*\\.zip|d2.*\\.zip")).firstOrNull()?.let { found.putIfAbsent("install", it) }
        return Detection(validateDir(env.paths.game(gameId)).filesOk, found)
    }

    private fun findInstall(node: SourceNode, depth: Int): SourceNode? {
        if (!node.isDirectory || depth < 0) return null
        val children = runCatching { node.children() }.getOrDefault(emptyList())
        if (children.any { it.name.equals(EXE, true) } && children.any { it.name.equals("d2data.mpq", true) }) return node
        return children.filter { it.isDirectory }.firstNotNullOfOrNull { findInstall(it, depth - 1) }
    }

    private fun installed(env: ImportEnv) = validateDir(env.paths.game(gameId)).filesOk

    override fun resolveSources(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<AutoSource> {
        if (supplied["install"] is Supplied.Picked || detection.found["install"] != null || installed(env)) return emptyList()
        if (env.legacy == null || !env.online()) return emptyList()
        return listOf(AutoSource("blizzard", "Diablo II + Lord of Destruction 1.14b from Blizzard's servers", SIZE))
    }

    override fun downloadAvailableFiles(env: ImportEnv, sources: List<AutoSource>) {
        if (sources.none { it.id == "blizzard" }) return
        val legacy = env.legacy ?: return
        val staging = env.paths.staging(gameId)
        // The pieces are cached apart from staging: a stopped download goes on where it was.
        FileValidator.requireSpace(env.paths.downloads, SIZE * 2)
        staging.deleteRecursively()
        staging.mkdirs()
        try {
            legacy.install("D2DV", staging, noBase = true, keys = env.keys?.copy(expansion = null), cancel = env.cancel, onProgress = env.progress)
            legacy.install("D2XP", staging, noBase = true, keys = env.keys?.copy(classic = null), cancel = env.cancel, onProgress = env.progress)
            File(staging, MARK).writeText("D2DV D2XP\n")
        } catch (e: Throwable) {
            staging.deleteRecursively()
            throw e
        }
    }

    override fun getMissingInputs(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<MissingInput> {
        val downloaded = File(env.paths.staging(gameId), MARK).exists()
        if (downloaded || installed(env) || detection.found["install"] != null || supplied["install"] is Supplied.Picked) return emptyList()
        return listOf(MissingInput("install", PROMPT_INSTALL, PickKind.FILE_OR_FOLDER))
    }

    override fun importFiles(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>) {
        val asm = Assembler(env.paths, gameId)
        val scratch = File(env.paths.staging, "$gameId-scratch")
        try {
            val staging = asm.staging
            val downloaded = File(staging, MARK).exists()
            val source = (supplied["install"] as? Supplied.Picked)?.source ?: detection.found["install"]
            if (!downloaded) {
                asm.begin()
                asm.reuse(env.paths.game(gameId).list()?.toList() ?: emptyList()) { f -> !f.name.endsWith(".mpq", true) || Mpq.isArchive(f) }
                if (source != null) {
                    FileValidator.requireSpace(staging, SIZE)
                    copyInstall(source, staging, scratch, env)
                }
            }
            File(staging, MARK).delete()
            env.progress(Progress(Stage.VALIDATING, "Checking Diablo II"))
            val check = validateDir(staging)
            if (!check.filesOk) throw ImportException(check.problem ?: Problem.MISSING_SOURCE_DATA, check.message ?: "Diablo II's files didn't check out.")
            asm.commit()
        } catch (e: Throwable) {
            asm.abandon()
            throw e
        } finally {
            scratch.deleteRecursively()
        }
    }

    /** An installation folder (or a zip of one) into staging; its old-style save folder goes to the saves. */
    private fun copyInstall(source: SourceNode, staging: File, scratch: File, env: ImportEnv) {
        env.progress(Progress(Stage.EXTRACTING, "Copying Diablo II from ${source.display}"))
        val savesImport = File(env.paths.saves(gameId), "import")
        if (source.isDirectory) {
            val root = findInstall(source, 4) ?: throw ImportException(Problem.MISSING_SOURCE_DATA, "There's no Diablo II in that folder (no Game.exe with d2data.mpq). $PROMPT_INSTALL")
            copyTree(root, staging, env, savesImport)
        } else if (source.name.endsWith(".zip", true)) {
            val out = File(scratch, "zip")
            source.open().use { ZipExtractor.extract(it, out, env.cancel) }
            val root = out.walkTopDown().firstOrNull { it.isFile && it.name.equals(EXE, true) && File(it.parentFile, "d2data.mpq").exists() }?.parentFile
                ?: throw ImportException(Problem.MISSING_SOURCE_DATA, "That zip has no Diablo II installation in it (no Game.exe with d2data.mpq).")
            copyTree(FileNode(root), staging, env, savesImport)
        } else {
            throw ImportException(Problem.UNSUPPORTED_INSTALLER, "${source.name} isn't something this importer reads. $PROMPT_INSTALL")
        }
    }

    private fun copyTree(root: SourceNode, staging: File, env: ImportEnv, savesImport: File) {
        val total = root.walk(4).sumOf { it.size }
        var done = 0L
        fun walk(node: SourceNode, into: File, depth: Int) {
            for (child in node.children()) {
                env.cancel.check()
                // Saved games (pre-1.14 kept them in the game folder): to the saves, never over one there.
                if (depth == 0 && child.isDirectory && child.name.equals("save", true)) {
                    for (save in child.children().filter { !it.isDirectory }) {
                        val target = File(savesImport, save.name)
                        if (!target.exists()) copyInto(save, savesImport, save.name, env.cancel)
                    }
                    continue
                }
                if (child.isDirectory) {
                    if (depth < 4) walk(child, File(into, child.name), depth + 1)
                } else {
                    copyInto(child, into, child.name, env.cancel) { n ->
                        done += n
                        env.progress(Progress(Stage.EXTRACTING, "Copying Diablo II", done, total))
                    }
                }
            }
        }
        walk(root, staging, 0)
    }

    override fun validate(env: ImportEnv): Validation = validateDir(env.paths.game(gameId))

    fun validateDir(dir: File): Validation {
        val (program, pe) = programChecks(dir, EXE)
        val checks = program.toMutableList()
        val versionOk = supported(pe?.version)
        checks += Check("Version 1.14", versionOk, pe?.version ?: "unknown")
        val base = FileValidator.requireArchives(dir, BASE)
        val expansion = FileValidator.requireArchives(dir, EXPANSION)
        checks += base + expansion
        val movies = (base + expansion).filter { c -> MOVIES.any { it.equals(c.name, true) } }
        val moviesOk = movies.size == MOVIES.size && movies.all { it.passed }
        checks += Check("Movies", moviesOk, if (moviesOk) "${MOVIES.joinToString(" and ")} present" else "missing or damaged: ${MOVIES.filter { m -> movies.none { it.name == m && it.passed } }.joinToString()}")
        val native = FileValidator.requireFiles(dir, NATIVE)
        checks += native
        val problem = when {
            !checks[0].passed -> Problem.MISSING_SOURCE_DATA
            pe != null && !versionOk -> Problem.UNSUPPORTED_VERSION
            checks.getOrNull(1)?.passed == false -> Problem.MISSING_RUNTIME_DEPENDENCY
            base.any { !it.passed } -> if (base.all { it.detail == "missing" }) Problem.MISSING_SOURCE_DATA else Problem.CORRUPT_ARCHIVE
            expansion.any { !it.passed } -> Problem.MISSING_EXPANSION
            native.any { !it.passed } -> Problem.MISSING_RUNTIME_DEPENDENCY
            else -> null
        }
        val message = when (problem) {
            Problem.UNSUPPORTED_VERSION -> "This Diablo II is version ${pe?.version}; the app plays 1.14 (1.14b is what Blizzard serves). Select a 1.14 installation, or retry online to download it from Blizzard."
            Problem.MISSING_EXPANSION -> PROMPT_EXPANSION
            Problem.CORRUPT_ARCHIVE -> "Some of Diablo II's archives are damaged: ${base.filter { !it.passed }.joinToString { it.name }}. Repair to download or copy them again."
            Problem.MISSING_RUNTIME_DEPENDENCY ->
                if (checks[1].passed) "Diablo II's files are missing: ${native.filter { !it.passed }.joinToString { it.name }} (the movies and the game's text need them)."
                else "Diablo II's libraries are missing: ${checks[1].detail}."
            Problem.MISSING_SOURCE_DATA -> "Diablo II game data is missing. $PROMPT_INSTALL"
            else -> null
        }
        return Validation(checks, pe?.version?.let { "Diablo II + Lord of Destruction $it" }, problem == null, problem, message)
    }

    override fun registerLaunchEntry(env: ImportEnv, validation: Validation) = LibraryEntry(
        gameId = gameId,
        title = "Diablo II + Lord of Destruction",
        products = listOf("D2DV", "D2XP"),
        clientVersion = validation.clientVersion ?: "",
        installPath = env.paths.game(gameId).path,
        executable = EXE,
        runtime = LibraryEntry.RUNTIME_WINLATOR,
        arguments = "",
        stage = Stage.READY,
        saveLocation = SAVE_DIR,
        controlProfile = "diablo2",
    )
}
