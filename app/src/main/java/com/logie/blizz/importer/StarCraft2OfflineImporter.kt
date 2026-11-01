package com.logie.blizz.importer

import java.io.File

/**
 * StarCraft II 3.0.5.39117 (Wings of Liberty, Heart of the Swarm and Legacy of the Void) with the
 * offline launcher that goes with that build ("StarCraft II Offline.exe"), from the person's own
 * files only: nothing is downloaded, no Battle.net credentials are asked for, and no batch file or
 * other program of the package is run. The version is checked from the game's own folder
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
        const val BUILD = "39117"
        const val VERSION = "3.0.5.39117"
        const val LAUNCHER = "StarCraft II Offline.exe"
        val GAME_EXES = listOf("SC2_x64.exe", "SC2.exe")
        const val PROMPT_INSTALL = "Select your StarCraft II 3.0.5 installation folder or game archive."
        const val PROMPT_LAUNCHER = "The supported offline launcher was not found. Select the matching StarCraft II Offline.exe and associated files."
        const val PROMPT_VERSION = "This StarCraft II installation is not version 3.0.5.39117. Select a compatible installation."
        /** Inside the games' Windows: where the game keeps profiles and saves. */
        const val DOCUMENTS = "C:\\users\\xuser\\Documents\\StarCraft II"
    }

    override fun detect(env: ImportEnv): Detection {
        env.progress(Progress(Stage.DETECTING, "Looking for StarCraft II"))
        val found = LinkedHashMap<String, SourceNode>()
        val roots = env.searchRoots()
        roots.firstNotNullOfOrNull { findInstall(it, 4) }?.let { found["install"] = it }
        Scan(roots, 5).named(LAUNCHER)?.let { found["launcher"] = it }
        val v = validateDir(env.paths.game(gameId))
        return Detection(v.filesOk, found)
    }

    private fun findInstall(node: SourceNode, depth: Int): SourceNode? {
        if (!node.isDirectory || depth < 0) return null
        val children = runCatching { node.children() }.getOrDefault(emptyList())
        if (children.any { it.isDirectory && it.name.equals("Versions", true) } && children.any { it.isDirectory && it.name.equals("SC2Data", true) }) return node
        return children.filter { it.isDirectory }.firstNotNullOfOrNull { findInstall(it, depth - 1) }
    }

    override fun resolveSources(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<AutoSource> = emptyList()

    override fun downloadAvailableFiles(env: ImportEnv, sources: List<AutoSource>) = Unit

    override fun getMissingInputs(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<MissingInput> {
        val game = env.paths.game(gameId)
        val install = (supplied["install"] as? Supplied.Picked)?.source ?: detection.found["install"]
        val haveGame = File(game, "Versions").isDirectory || install != null
        if (!haveGame) return listOf(MissingInput("install", PROMPT_INSTALL, PickKind.FILE_OR_FOLDER))
        val launcherHere = FileValidator.find(game, LAUNCHER) != null || (install?.isDirectory == true && install.child(LAUNCHER) != null) ||
            install?.name?.endsWith(".zip", true) == true
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
            val install = (supplied["install"] as? Supplied.Picked)?.source ?: detection.found["install"]
            if (install != null) {
                val lower = install.name.lowercase()
                when {
                    install.isDirectory -> {
                        val root = findInstall(install, 4) ?: throw ImportException(Problem.MISSING_SOURCE_DATA, "There's no StarCraft II in that folder (no Versions and SC2Data folders). $PROMPT_INSTALL")
                        precheckVersion(root)
                        val total = root.walk(12).sumOf { it.size }
                        FileValidator.requireSpace(staging, total)
                        copyTree(root, staging, env, total)
                    }
                    lower.endsWith(".zip") -> {
                        FileValidator.requireSpace(staging, install.size * 2)
                        val out = File(scratch, "zip")
                        env.progress(Progress(Stage.EXTRACTING, "Unpacking ${install.name}"))
                        install.open().use { ZipExtractor.extract(it, out, env.cancel) }
                        val root = out.walkTopDown().maxDepth(5).firstOrNull { it.isDirectory && File(it, "Versions").isDirectory && File(it, "SC2Data").isDirectory }
                            ?: throw ImportException(Problem.MISSING_SOURCE_DATA, "That archive has no StarCraft II installation in it (no Versions and SC2Data folders).")
                        root.listFiles()!!.forEach { f -> val t = File(staging, f.name); t.deleteRecursively(); if (!f.renameTo(t)) f.copyRecursively(t, true) }
                    }
                    lower.endsWith(".7z") || lower.endsWith(".rar") || lower.endsWith(".iso") ->
                        throw ImportException(Problem.UNSUPPORTED_INSTALLER, "${install.name}: this importer reads folders and zip archives. Unpack it to a folder first, then select the folder.")
                    else -> throw ImportException(Problem.UNSUPPORTED_INSTALLER, "${install.name} isn't a StarCraft II folder or archive. $PROMPT_INSTALL")
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
        } catch (e: Throwable) {
            asm.abandon()
            throw e
        } finally {
            scratch.deleteRecursively()
        }
    }

    /** Before copying gigabytes: the folder's build is the supported one. */
    private fun precheckVersion(root: SourceNode) {
        val versions = root.child("Versions")?.children()?.filter { it.isDirectory }?.map { it.name } ?: emptyList()
        if (versions.none { it.equals("Base$BUILD", true) }) {
            throw ImportException(Problem.UNSUPPORTED_VERSION, PROMPT_VERSION, "Versions: ${versions.joinToString().ifEmpty { "none" }}")
        }
    }

    private fun copyTree(root: SourceNode, staging: File, env: ImportEnv, total: Long) {
        var done = 0L
        fun walk(node: SourceNode, into: File, depth: Int) {
            for (child in node.children()) {
                env.cancel.check()
                if (child.isDirectory) {
                    if (depth < 12) walk(child, File(into, child.name), depth + 1)
                } else {
                    val target = File(into, child.name)
                    if (target.isFile && target.length() == child.size) { done += child.size; continue }
                    copyInto(child, into, child.name, env.cancel) { n ->
                        done += n
                        env.progress(Progress(Stage.EXTRACTING, "Copying StarCraft II", done, total))
                    }
                }
            }
        }
        walk(root, staging, 0)
    }

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
        val base = File(File(dir, "Versions"), "Base$BUILD")
        checks += Check("Game assets (SC2Data)", File(dir, "SC2Data").isDirectory && (File(dir, "SC2Data").list()?.isNotEmpty() == true), if (File(dir, "SC2Data").isDirectory) "present" else "missing")
        val exe = GAME_EXES.firstNotNullOfOrNull { FileValidator.find(base, it) }
        val pe = exe?.let { PeInfo.read(it) }
        checks += Check("Supported version ($VERSION)", base.isDirectory && pe?.version == VERSION, when {
            !base.isDirectory -> "Versions: ${versions.joinToString().ifEmpty { "none" }}"
            pe == null -> "no SC2 program in Base$BUILD"
            else -> "${exe.name} ${pe.version}"
        })
        val launcher = FileValidator.find(dir, LAUNCHER)
        val lpe = launcher?.let { PeInfo.read(it) }
        checks += Check("Offline launcher", lpe != null && lpe.isWindowsX86Family, if (launcher == null) "missing" else if (lpe == null) "not a Windows program" else "present")
        if (exe != null) {
            val missing = Dependencies.missing(exe)
            checks += Check("Game libraries", missing.isEmpty(), if (missing.isEmpty()) "present" else "missing ${missing.joinToString()}")
        }
        checks += Check("Executable started under Winlator", false, "not tested")
        checks += Check("Campaign menu accessible", false, "not tested")
        checks += Check("Save/load", false, "not tested")
        val filesOk = checks.take(3).all { it.passed } && (checks.getOrNull(3)?.name != "Game libraries" || checks[3].passed)
        val problem = when {
            !checks[0].passed && versions.isEmpty() -> Problem.MISSING_SOURCE_DATA
            !checks[1].passed -> Problem.UNSUPPORTED_VERSION
            !checks[0].passed -> Problem.MISSING_SOURCE_DATA
            !checks[2].passed -> Problem.MISSING_SOURCE_DATA
            !filesOk -> Problem.MISSING_RUNTIME_DEPENDENCY
            else -> null
        }
        val message = when (problem) {
            Problem.UNSUPPORTED_VERSION -> PROMPT_VERSION
            Problem.MISSING_SOURCE_DATA -> if (!checks[0].passed) PROMPT_INSTALL else PROMPT_LAUNCHER
            Problem.MISSING_RUNTIME_DEPENDENCY -> "StarCraft II's libraries are missing: ${checks.getOrNull(3)?.detail}."
            else -> null
        }
        return Validation(checks, if (pe?.version == VERSION) "StarCraft II $VERSION (offline)" else null, filesOk, problem, message)
    }

    override fun readyStage(validation: Validation) = Stage.IMPORTED_UNTESTED

    override fun registerLaunchEntry(env: ImportEnv, validation: Validation) = LibraryEntry(
        gameId = gameId,
        title = "StarCraft II",
        products = listOf("WOL", "HOTS", "LOTV"),
        clientVersion = validation.clientVersion ?: "",
        installPath = env.paths.game(gameId).path,
        executable = LAUNCHER,
        runtime = LibraryEntry.RUNTIME_WINLATOR,
        arguments = "",
        stage = Stage.IMPORTED_UNTESTED,
        saveLocation = DOCUMENTS,
        controlProfile = "starcraft2",
    )
}
