package com.logie.blizz.importer

import java.io.File

/**
 * StarCraft: Remastered 1.23.10.12409, a second installation of StarCraft beside the classic one
 * (its own folder, its own saves, its own controls), from the person's own files only: nothing is
 * downloaded, no Battle.net credentials are asked for. They can be a folder of the installed game,
 * or a zip, 7z, tar, disc image or installer ([Unpacker]). The classic game is never touched.
 *
 * The files can show the game is there and which version it is; they can't show it starts under
 * Winlator, so an import ends as Imported — Launch Untested.
 */
class StarCraftRemasteredImporter : GameImporter {
    override val gameId = "starcraft_remastered"
    override val title = "StarCraft: Remastered"

    companion object {
        const val EXE = "StarCraft.exe"
        /** The version of the build this was made for; any 1.23.x is accepted, and shown as it is. */
        const val VERSION = "1.23.10.12409"
        const val FAMILY = "1.23."
        const val PROMPT_INSTALL = "Select your StarCraft: Remastered installation: its folder, a zip, 7z, tar or disc image of it (StarCraft Remastered.iso), or its installer (Setup.exe, with its data files in the same folder)."
        val PROMPT_VERSION = "This isn't StarCraft: Remastered $VERSION. Select a compatible installation."
        /** Inside the games' Windows: where the game keeps profiles and saves. */
        const val DOCUMENTS = "C:\\users\\xuser\\Documents\\StarCraft"

        /** The remastered game's folder: its program and its data folder, and none of the classic game's archives. */
        val isGameRoot: (Set<String>) -> Boolean = { "starcraft.exe" in it && "data/" in it && "stardat.mpq" !in it }
    }

    override fun detect(env: ImportEnv): Detection {
        env.progress(Progress(Stage.DETECTING, "Looking for StarCraft: Remastered"))
        val found = LinkedHashMap<String, SourceNode>()
        val roots = env.searchRoots()
        roots.firstNotNullOfOrNull { Packages.findRoot(it, 4, isGameRoot) }?.let { found["install"] = it }
        if (found["install"] == null) {
            Scan(roots, 5).matching(Regex("(?i)starcraft.?remastered.*\\.(iso|zip|7z|tar|tar\\.gz|tgz|tar\\.xz|tar\\.bz2|tar\\.zst)")).firstOrNull()?.let { found["install"] = it }
        }
        return Detection(validateDir(env.paths.game(gameId)).filesOk, found)
    }

    override fun resolveSources(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<AutoSource> = emptyList()

    override fun downloadAvailableFiles(env: ImportEnv, sources: List<AutoSource>) = Unit

    override fun getMissingInputs(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<MissingInput> {
        val have = FileValidator.find(env.paths.game(gameId), EXE) != null || detection.found["install"] != null || supplied["install"] is Supplied.Picked
        return if (have) emptyList() else listOf(MissingInput("install", PROMPT_INSTALL, PickKind.FILE_OR_FOLDER))
    }

    override fun importFiles(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>) {
        val asm = Assembler(env.paths, gameId)
        val scratch = File(env.paths.staging, "$gameId-scratch")
        try {
            val staging = asm.begin()
            asm.reuse(env.paths.game(gameId).list()?.toList() ?: emptyList()) { true }
            val install = (supplied["install"] as? Supplied.Picked)?.source ?: detection.found["install"]
            if (install != null) {
                val root = Packages.materialize(install, env, staging, scratch, "StarCraft: Remastered", PROMPT_INSTALL, isGameRoot, checkUnpacked = ::precheck)
                precheck(root)
                for (f in root.listFiles().orEmpty()) {
                    val target = File(staging, f.name)
                    target.deleteRecursively()
                    if (!f.renameTo(target)) f.copyRecursively(target, true)
                }
            }
            File(env.paths.saves(gameId), "Documents").mkdirs()
            env.progress(Progress(Stage.VALIDATING, "Checking StarCraft: Remastered"))
            val check = validateDir(staging)
            if (!check.filesOk) throw ImportException(check.problem ?: Problem.MISSING_SOURCE_DATA, check.message ?: "StarCraft: Remastered's files didn't check out.")
            asm.commit()
        } catch (e: Throwable) {
            asm.abandon()
            throw e
        } finally {
            scratch.deleteRecursively()
        }
    }

    /** The unpacked program is a remastered build, before gigabytes are moved in. */
    private fun precheck(root: File) {
        val exe = FileValidator.find(root, EXE) ?: return
        val version = PeInfo.read(exe)?.version
        if (version == null || !version.startsWith(FAMILY)) {
            throw ImportException(Problem.UNSUPPORTED_VERSION, PROMPT_VERSION, "$EXE: ${version ?: "no version"}")
        }
    }

    override fun validate(env: ImportEnv): Validation = validateDir(env.paths.game(gameId))

    fun validateDir(dir: File): Validation {
        val checks = ArrayList<Check>()
        val exe = FileValidator.find(dir, EXE)
        val pe = exe?.let { PeInfo.read(it) }
        checks += Check(EXE, pe != null && pe.isWindowsX86Family, if (exe == null) "missing" else if (pe == null) "not a Windows program" else "present")
        checks += Check("Version $VERSION (1.23.x)", pe?.version?.startsWith(FAMILY) == true, pe?.version ?: "unknown")
        val data = FileValidator.find(dir, "Data")
        checks += Check("Game data (Data)", data != null && data.isDirectory && (data.walkTopDown().take(3).count { it.isFile } > 0), if (data == null) "missing" else "present")
        if (exe != null && pe != null) {
            val missing = Dependencies.missing(exe)
            checks += Check("Game libraries", missing.isEmpty(), if (missing.isEmpty()) "present" else "missing ${missing.joinToString()}")
        }
        checks += Check("Executable started under Winlator", false, "not tested")
        checks += Check("Campaign menu accessible", false, "not tested")
        checks += Check("Save/load", false, "not tested")
        val core = checks.take(3).all { it.passed } && (checks.getOrNull(3)?.name != "Game libraries" || checks[3].passed)
        val problem = if (core) null else when {
            !checks[0].passed -> Problem.MISSING_SOURCE_DATA
            !checks[1].passed -> Problem.UNSUPPORTED_VERSION
            !checks[2].passed -> Problem.MISSING_SOURCE_DATA
            else -> Problem.MISSING_RUNTIME_DEPENDENCY
        }
        val message = when (problem) {
            Problem.UNSUPPORTED_VERSION -> PROMPT_VERSION
            Problem.MISSING_SOURCE_DATA -> PROMPT_INSTALL
            Problem.MISSING_RUNTIME_DEPENDENCY -> "StarCraft: Remastered's libraries are missing: ${checks.getOrNull(3)?.detail}."
            else -> null
        }
        return Validation(checks, pe?.version?.let { "StarCraft: Remastered $it" }, core, problem, message)
    }

    override fun readyStage(validation: Validation) = Stage.IMPORTED_UNTESTED

    override fun registerLaunchEntry(env: ImportEnv, validation: Validation) = LibraryEntry(
        gameId = gameId,
        title = "StarCraft: Remastered",
        products = listOf("SCR"),
        clientVersion = validation.clientVersion ?: "",
        installPath = env.paths.game(gameId).path,
        executable = FileValidator.find(env.paths.game(gameId), EXE)?.name ?: EXE,
        runtime = LibraryEntry.RUNTIME_WINLATOR,
        arguments = "",
        stage = Stage.IMPORTED_UNTESTED,
        saveLocation = DOCUMENTS,
        controlProfile = "starcraft_remastered",
    )
}
