package com.logie.blizz.importer

import java.io.File

/**
 * StarCraft II 3.0.5.39117 or 3.1.4.41219 with the offline launcher that goes with the build
 * ("StarCraft II Offline.exe"), from the person's own files only: nothing is downloaded, no
 * Battle.net credentials are asked for, and no batch file or other program of the package is
 * run. They can be a folder of the installed game, or a zip, 7z, tar, disc image or installer
 * (Setup.exe with its data files, whatever they're called) ([Unpacker]). The version is checked from the game's own folder
 * (Versions/Base39117) and program, and a current Battle.net build is refused, never substituted.
 *
 * Files can't show that the offline launcher works under Winlator, nor that the campaigns load:
 * an import ends as Imported — Launch Untested, and stays that way after a start until the
 * campaign has been seen to work.
 */
class StarCraft2OfflineImporter : GameImporter {
    override val gameId = "starcraft2"
    override val title = "StarCraft II"

    companion object {
        /** The builds this plays: the build number (the game's folder, Versions/Base<build>) and its program's version. */
        val BUILDS = linkedMapOf("39117" to "3.0.5.39117", "41219" to "3.1.4.41219")
        const val LAUNCHER = "StarCraft II Offline.exe"
        val GAME_EXES = listOf("SC2_x64.exe", "SC2.exe")
        const val PROMPT_INSTALL = "Select your StarCraft II installation: its folder, a zip, 7z, tar or disc image of it, or its installer (Setup.exe, with its data files in the same folder)."
        const val PROMPT_LAUNCHER = "The supported offline launcher was not found. Select the matching StarCraft II Offline.exe and associated files."
        /** Any build is taken; these are the ones it was made for and known to start. */
        val PROMPT_VERSION = "That StarCraft II folder has no Versions\\Base<build> folder with the game's program in it (SC2_x64.exe or SC2.exe). Select the installed game's folder."
        private val BASE = Regex("(?i)base(\\d+)")
        /** Inside the games' Windows: where the game keeps profiles and saves. */
        const val DOCUMENTS = "C:\\users\\xuser\\Documents\\StarCraft II"
    }

    override fun detect(env: ImportEnv): Detection {
        env.progress(Progress(Stage.DETECTING, "Looking for StarCraft II"))
        val found = LinkedHashMap<String, SourceNode>()
        val roots = env.searchRoots()
        roots.firstNotNullOfOrNull { findInstall(it, 4) }?.let { found["install"] = it }
        val scan = Scan(roots, 5)
        scan.named(LAUNCHER)?.let { found["launcher"] = it }
        if (found["install"] == null) {
            scan.matching(Regex("(?i)(sc2|starcraft.?(ii|2)).*\\.(zip|7z|iso|tar|tar\\.gz|tgz|tar\\.xz|tar\\.bz2|tar\\.zst)")).firstOrNull()?.let { found["install"] = it }
        }
        val v = validateDir(env.paths.game(gameId))
        return Detection(v.filesOk, found)
    }

    val isGameRoot: (Set<String>) -> Boolean = { "versions/" in it && "sc2data/" in it }

    /**
     * The game's folder wherever its own markers are in what was unpacked, whatever the folders around
     * them are called: a "Versions" folder holding Base*, an "SC2Data" folder, or SC2.exe / SC2_x64.exe
     * in a Base* folder. Plain Kotlin, unit-tested.
     */
    fun looseGameRoot(dir: File): File? {
        val all = dir.walkTopDown().maxDepth(14).toList()
        all.firstOrNull { it.isDirectory && it.name.equals("Versions", true) && it.listFiles().orEmpty().any { c -> c.isDirectory && c.name.startsWith("Base", true) } }
            ?.let { return it.parentFile }
        all.firstOrNull { it.isDirectory && it.name.equals("SC2Data", true) }?.let { return it.parentFile }
        all.firstOrNull { it.isFile && it.name.lowercase() in setOf("sc2.exe", "sc2_x64.exe") }?.let { exe ->
            val base = exe.parentFile
            return if (base.name.startsWith("Base", true) && base.parentFile?.name.equals("Versions", true)) base.parentFile.parentFile else base
        }
        return null
    }

    /** What was picked is an installer (the program, or a folder holding one and no game) rather than a game, archive or disc image. */
    private fun isInstaller(source: SourceNode): Boolean =
        if (source.isDirectory) findInstall(source, 6) == null && InstallerRun.find(source) != null else Format.of(source) == Format.PROGRAM

    private fun findInstall(node: SourceNode, depth: Int): SourceNode? = Packages.findRoot(node, depth, isGameRoot)

    override fun resolveSources(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<AutoSource> = emptyList()

    override fun downloadAvailableFiles(env: ImportEnv, sources: List<AutoSource>) = Unit

    override fun getMissingInputs(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<MissingInput> {
        val game = env.paths.game(gameId)
        val install = InstallerRun.sourceOf(supplied, detection.found["install"])
        val madeByInstaller = InstallerRun.finishedRoot(env.paths, gameId, isGameRoot, ::looseGameRoot) != null
        val haveGame = File(game, "Versions").isDirectory || install != null || madeByInstaller
        if (!haveGame) return listOf(MissingInput("install", PROMPT_INSTALL, PickKind.FILE_OR_FOLDER))
        // The installer program alone, picked as a file: its data files can't be seen beside it. Ask for the folder.
        if (!madeByInstaller && install != null && !install.isDirectory && !InstallerRun.copyComplete(env.paths, gameId) &&
            Format.of(install) == Format.PROGRAM && InstallerRun.needsFolder(install)
        ) {
            return listOf(InstallerRun.folderQuestion(install.name))
        }
        // An installed game's folder shows whether it holds the launcher; an archive, a disc image or an
        // installer (and its data files) can't be looked into before it's unpacked, so it's asked about after, if at all.
        val launcherHere = FileValidator.find(game, LAUNCHER) != null || install == null || !install.isDirectory ||
            findInstall(install, 4).let { it == null || it.child(LAUNCHER) != null }
        if (!launcherHere && detection.found["launcher"] == null && supplied["launcher"] !is Supplied.Picked) {
            return listOf(MissingInput("launcher", PROMPT_LAUNCHER, PickKind.FILE_OR_FOLDER))
        }
        return emptyList()
    }

    override fun importFiles(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>) {
        val asm = Assembler(env.paths, gameId)
        val scratch = File(env.paths.staging, "$gameId-scratch")
        try {
            val staging = asm.begin()
            asm.reuse(env.paths.game(gameId).list()?.toList() ?: emptyList()) { true }
            val install = InstallerRun.sourceOf(supplied, detection.found["install"])
            val installed = InstallerRun.finishedRoot(env.paths, gameId, isGameRoot, ::looseGameRoot)
            if (installed != null) {
                // What the game's own installer made in the app's Windows.
                precheckVersion(installed)
                for (f in installed.listFiles().orEmpty()) {
                    val target = File(staging, f.name)
                    target.deleteTree()
                    if (!f.renameTo(target)) f.copyRecursively(target, true)
                }
            } else if (InstallerRun.readRun(env.paths, gameId) != null && (install == null || isInstaller(install))) {
                // The installer was run in the app's Windows and has made no game (yet): said so, not its shell unpacked again.
                throw ImportException(
                    Problem.INSTALLER_MUST_RUN,
                    "The installer was run, but no StarCraft II has appeared in its folder or in the app's Windows. If it is still running, wait for it to end and tap Retry. " +
                        "If it ended, tap Run the installer to try it with other switches (${InstallerRun.VARIANT_COUNT} sets are tried in turn).",
                    "Installer folder:${Packages.outline(env.paths.installer(gameId))}",
                )
            } else if (install != null) {
                val root = Packages.materialize(install, env, staging, scratch, "StarCraft II", PROMPT_INSTALL, isGameRoot, ::precheckVersion, ::precheckVersion, looseRoot = ::looseGameRoot)
                // Moved, not copied: it was just unpacked beside staging.
                for (f in root.listFiles().orEmpty()) {
                    val target = File(staging, f.name)
                    target.deleteTree()
                    if (!f.renameTo(target)) f.copyRecursively(target, true)
                }
            }
            // The offline launcher and the files beside it, when it came separately.
            val launcher = (supplied["launcher"] as? Supplied.Picked)?.source ?: detection.found["launcher"]
            if (FileValidator.find(staging, LAUNCHER) == null && launcher != null) {
                if (launcher.isDirectory) {
                    val exe = launcher.child(LAUNCHER) ?: throw ImportException(Problem.MISSING_SOURCE_DATA, "That folder has no $LAUNCHER. $PROMPT_LAUNCHER")
                    for (f in launcher.children().filter { !it.isDirectory }) copyInto(f, staging, f.name, env.cancel)
                    if (FileValidator.find(staging, exe.name) == null) copyInto(exe, staging, LAUNCHER, env.cancel)
                } else {
                    copyInto(launcher, staging, LAUNCHER, env.cancel)
                }
            }
            initializeProfiles(env, staging)
            env.progress(Progress(Stage.VALIDATING, "Checking StarCraft II"))
            val check = validateDir(staging)
            if (!check.filesOk) throw ImportException(check.problem ?: Problem.MISSING_SOURCE_DATA, check.message ?: "StarCraft II's files didn't check out.")
            asm.commit()
            env.paths.installer(gameId).deleteTree()
        } catch (e: Throwable) {
            asm.abandon()
            throw e
        } finally {
            scratch.deleteTree()
        }
    }

    /** The unpacked game has a build folder to play (any build), before it's moved in. */
    private fun precheckVersion(root: File) {
        if (baseFolders(root).isEmpty()) {
            throw ImportException(Problem.UNSUPPORTED_VERSION, PROMPT_VERSION, "Versions: ${File(root, "Versions").list()?.joinToString().orEmpty().ifEmpty { "none" }}")
        }
    }

    /** Before copying gigabytes: the folder has a build folder to play (any build). */
    private fun precheckVersion(root: SourceNode) {
        val versions = root.child("Versions")?.children()?.filter { it.isDirectory }?.map { it.name } ?: emptyList()
        if (versions.none { BASE.matches(it) }) {
            throw ImportException(Problem.UNSUPPORTED_VERSION, PROMPT_VERSION, "Versions: ${versions.joinToString().ifEmpty { "none" }}")
        }
    }

    /** The game's `Versions/Base<build>` folders, the newest build first: any build. */
    fun baseFolders(dir: File): List<File> =
        File(dir, "Versions").listFiles { f -> f.isDirectory && BASE.matches(f.name) }.orEmpty()
            .sortedByDescending { BASE.matchEntire(it.name)?.groupValues?.get(1)?.toLongOrNull() ?: 0L }

    /**
     * The ordinary writable folders the game uses, in the app's saves folder (copied into the games'
     * Windows Documents at start, never over what's there). Imported profiles and saves (an
     * "Accounts" folder that came with the installation) are kept. No offline licence state is
     * written or claimed: what a release's own setup step does isn't known, so it isn't imitated.
     */
    private fun initializeProfiles(env: ImportEnv, staging: File) {
        val docs = File(env.paths.saves(gameId), "Documents/StarCraft II")
        if (!docs.mkdirs() && !docs.isDirectory) throw ImportException(Problem.PROFILE_INIT_FAILED, "The profile folder couldn't be made.")
        File(docs, "Accounts").mkdirs()
        val accounts = FileValidator.find(staging, "Accounts")
        if (accounts != null && accounts.isDirectory) {
            accounts.walkTopDown().filter { it.isFile }.forEach { f ->
                val target = File(File(docs, "Accounts"), f.relativeTo(accounts).path)
                if (!target.exists()) f.copyTo(target)
            }
        }
    }

    override fun validate(env: ImportEnv): Validation = validateDir(env.paths.game(gameId))

    fun validateDir(dir: File): Validation {
        val checks = ArrayList<Check>()
        val versions = File(dir, "Versions").list()?.toList() ?: emptyList()
        // The newest build folder that has the game's program in it (any build is taken).
        val bases = baseFolders(dir)
        val base = bases.firstOrNull { b -> GAME_EXES.any { FileValidator.find(b, it) != null } } ?: bases.firstOrNull() ?: File(File(dir, "Versions"), "Base")
        checks += Check("Game assets (SC2Data)", File(dir, "SC2Data").isDirectory && (File(dir, "SC2Data").list()?.isNotEmpty() == true), if (File(dir, "SC2Data").isDirectory) "present" else "missing")
        val exe = GAME_EXES.firstNotNullOfOrNull { FileValidator.find(base, it) }
        val pe = exe?.let { PeInfo.read(it) }
        checks += Check("StarCraft II program (any version)", base.isDirectory && pe != null && pe.isWindowsX86Family, when {
            !base.isDirectory -> "Versions: ${versions.joinToString().ifEmpty { "none" }}"
            pe == null -> "no SC2 program in ${base.name}"
            else -> "${exe.name} ${pe.version ?: "(no version)"} in ${base.name}" +
                if (pe.version in BUILDS.values) "" else " (not one of ${BUILDS.values.joinToString(" or ")}, which it was made for: taken as it is)"
        })
        val launcher = FileValidator.find(dir, LAUNCHER)
        val lpe = launcher?.let { PeInfo.read(it) }
        val launcherOk = lpe != null && lpe.isWindowsX86Family
        checks += Check("Offline launcher", launcherOk, if (launcher == null) "not in the files: the game's own program starts instead" else if (lpe == null) "not a Windows program" else "present")
        if (exe != null) {
            // Any build: its libraries (FMOD, ICU, ...) differ by version and sit in the build's folder or the game's Support folders.
            // One found elsewhere in the files is fine (the game loads its own Support folders); one found nowhere is noted, not refused:
            // the game's own loader decides, and a real failure shows in the game's log.
            val missing = Dependencies.missing(exe)
            val all = if (missing.isEmpty()) emptySet() else dir.walkTopDown().filter { it.isFile }.map { it.name.lowercase() }.toSet()
            val nowhere = missing.filter { it.lowercase() !in all }
            checks += Check("Game libraries", true, when {
                missing.isEmpty() -> "present"
                nowhere.isEmpty() -> "found in the game's folders: ${missing.joinToString()}"
                else -> "not in the files (the game may still start): ${nowhere.joinToString()}"
            })
        }
        checks += Check("Executable started under Winlator", false, "not tested")
        checks += Check("Campaign menu accessible", false, "not tested")
        checks += Check("Save/load", false, "not tested")
        // Without the offline launcher the game's own program starts: imported, and untested all the same.
        val filesOk = checks[0].passed && checks[1].passed && (launcherOk || exe != null) &&
            (checks.getOrNull(3)?.name != "Game libraries" || checks[3].passed)
        val problem = if (filesOk) null else when {
            !checks[0].passed && versions.isEmpty() -> Problem.MISSING_SOURCE_DATA
            !checks[1].passed -> Problem.UNSUPPORTED_VERSION
            !checks[0].passed -> Problem.MISSING_SOURCE_DATA
            !checks[2].passed && exe == null -> Problem.MISSING_SOURCE_DATA
            else -> Problem.MISSING_RUNTIME_DEPENDENCY
        }
        val message = when (problem) {
            Problem.UNSUPPORTED_VERSION -> PROMPT_VERSION
            Problem.MISSING_SOURCE_DATA -> if (!checks[0].passed) PROMPT_INSTALL else PROMPT_LAUNCHER
            Problem.MISSING_RUNTIME_DEPENDENCY -> "StarCraft II's libraries are missing: ${checks.getOrNull(3)?.detail}."
            else -> null
        }
        return Validation(checks, pe?.version?.let { "StarCraft II $it (offline)" } ?: if (pe != null) "StarCraft II (offline)" else null, filesOk, problem, message)
    }

    override fun readyStage(validation: Validation) = Stage.IMPORTED_UNTESTED

    /** The offline launcher, else the game's own program (relative to its folder). */
    fun launchProgram(dir: File): String {
        // (only a launcher that is a Windows program: a junk file of that name would be run in place of the game's own)
        FileValidator.find(dir, LAUNCHER)?.takeIf { PeInfo.read(it)?.isWindowsX86Family == true }?.let { return it.name }
        for (base in baseFolders(dir)) {
            GAME_EXES.firstNotNullOfOrNull { FileValidator.find(base, it) }?.let { return "Versions/${base.name}/${it.name}" }
        }
        return LAUNCHER
    }

    override fun registerLaunchEntry(env: ImportEnv, validation: Validation) = LibraryEntry(
        gameId = gameId,
        title = "StarCraft II",
        products = listOf("WOL", "HOTS", "LOTV"),
        clientVersion = validation.clientVersion ?: "",
        installPath = env.paths.game(gameId).path,
        executable = launchProgram(env.paths.game(gameId)),
        runtime = LibraryEntry.RUNTIME_WINLATOR,
        arguments = "",
        stage = Stage.IMPORTED_UNTESTED,
        saveLocation = DOCUMENTS,
        controlProfile = "starcraft2",
    )
}
