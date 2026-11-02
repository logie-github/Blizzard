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
        val PROMPT_VERSION = "This StarCraft II installation is not version ${BUILDS.values.joinToString(" or ")}. Select a compatible installation."
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
                val root = materialize(install, env, staging, scratch)
                precheckVersion(root)
                // Moved, not copied: it was just unpacked beside staging.
                for (f in root.listFiles().orEmpty()) {
                    val target = File(staging, f.name)
                    target.deleteRecursively()
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
        } catch (e: Throwable) {
            asm.abandon()
            throw e
        } finally {
            scratch.deleteRecursively()
        }
    }

    /** The folder with Versions and SC2Data that [install] holds, unpacked or copied under [scratch]. */
    private fun materialize(install: SourceNode, env: ImportEnv, staging: File, scratch: File): File {
        val out = File(scratch, "game").also { it.deleteRecursively(); it.mkdirs() }
        val unpacker = Unpacker(env.innoextract)
        val found: SourceNode?
        val setup: SourceNode?
        val siblings: List<SourceNode>
        if (install.isDirectory) {
            found = findInstall(install, 4)
            if (found == null) {
                // No game in it: an installer and its data files, in it or in a folder just under it.
                val holder = (listOf(install) + install.children().filter { it.isDirectory }).firstOrNull { Installers.setupIn(it.children()) != null }
                siblings = holder?.children() ?: emptyList()
                setup = Installers.setupIn(siblings)
            } else {
                setup = null
                siblings = emptyList()
            }
        } else {
            found = null
            setup = install
            siblings = install.localFile()?.parentFile?.listFiles()?.map { FileNode(it) } ?: emptyList()
        }
        if (found != null) {
            val total = found.walk(12).sumOf { it.size }
            precheckVersion(found)
            FileValidator.requireSpace(staging, total)
            copyTree(found, out, env, total)
            return out
        }
        val source = setup ?: throw ImportException(Problem.MISSING_SOURCE_DATA, "There's no StarCraft II in that folder (no Versions and SC2Data folders, no installer). $PROMPT_INSTALL")
        FileValidator.requireSpace(scratch, (source.size + siblings.sumOf { it.size }).coerceAtLeast(1L shl 30) + (2L shl 30))
        unpacker.unpack(source, siblings, out, scratch, env.cancel, env.progress)
        // Wherever in what was unpacked the game's folders are.
        return out.walkTopDown().maxDepth(6).firstOrNull { it.isDirectory && File(it, "Versions").isDirectory && File(it, "SC2Data").isDirectory }
            ?: throw ImportException(Problem.MISSING_SOURCE_DATA, "${source.name} has no StarCraft II in it (no Versions and SC2Data folders after unpacking). $PROMPT_INSTALL")
    }

    /** The unpacked game's build is one this plays, before it's moved in. */
    private fun precheckVersion(root: File) {
        val versions = File(root, "Versions").list()?.toList() ?: emptyList()
        if (BUILDS.keys.none { build -> versions.any { it.equals("Base$build", true) } }) {
            throw ImportException(Problem.UNSUPPORTED_VERSION, PROMPT_VERSION, "Versions: ${versions.joinToString().ifEmpty { "none" }}")
        }
    }

    /** Before copying gigabytes: the folder's build is one this plays. */
    private fun precheckVersion(root: SourceNode) {
        val versions = root.child("Versions")?.children()?.filter { it.isDirectory }?.map { it.name } ?: emptyList()
        if (BUILDS.keys.none { build -> versions.any { it.equals("Base$build", true) } }) {
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
        // The build that's there (the newest this plays, if more than one).
        val build = BUILDS.keys.lastOrNull { File(File(dir, "Versions"), "Base$it").isDirectory } ?: BUILDS.keys.first()
        val VERSION = BUILDS.getValue(build)
        val base = File(File(dir, "Versions"), "Base$build")
        checks += Check("Game assets (SC2Data)", File(dir, "SC2Data").isDirectory && (File(dir, "SC2Data").list()?.isNotEmpty() == true), if (File(dir, "SC2Data").isDirectory) "present" else "missing")
        val exe = GAME_EXES.firstNotNullOfOrNull { FileValidator.find(base, it) }
        val pe = exe?.let { PeInfo.read(it) }
        checks += Check("Supported version (${BUILDS.values.joinToString(" or ")})", base.isDirectory && pe?.version == VERSION, when {
            !base.isDirectory -> "Versions: ${versions.joinToString().ifEmpty { "none" }}"
            pe == null -> "no SC2 program in Base$build"
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
