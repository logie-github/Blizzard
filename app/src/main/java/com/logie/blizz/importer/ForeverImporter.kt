package com.logie.blizz.importer

import java.io.File

/**
 * World of Warcraft: Forever (the ForeverNXT server's game), from the player's own client: the **Add client** step.
 * The client can be its folder (the one with Wow.exe and `_forever_`), or a zip, 7z, RAR, tar or disc image of it ([Unpacker]).
 * Nothing is downloaded and no client file ships with the app. The server comes in a later step; this import makes the
 * client's copy, checks it, and ends as Imported — Launch Untested (the files can't show it starts under Winlator).
 */
class ForeverImporter : GameImporter {
    override val gameId = "wow_forever"
    override val title = "World of Warcraft: Forever"

    companion object {
        const val EXE = "Wow.exe"
        const val DATA = "_forever_"
        /** Client builds the ForeverNXT launcher supports; any build is accepted and shown as read, these are the known ones. */
        val KNOWN_BUILDS = listOf(70450, 70532, 70685, 70707)
        const val PROMPT = "Add your World of Warcraft: Forever client: its folder (the one that holds Wow.exe and _forever_), or a zip, 7z, RAR or tar of it."

        /** The client's folder: its program and its `_forever_` data folder. */
        val isGameRoot: (Set<String>) -> Boolean = { "wow.exe" in it && "_forever_/" in it }

        /** The build number in a version such as 1.60.1.70707, or null. */
        fun buildOf(version: String?): Int? = Regex("""\d+\.\d+\.\d+\.(\d{4,6})""").find(version.orEmpty())?.groupValues?.get(1)?.toIntOrNull()

        /**
         * The client's build: from `.build.info` beside Wow.exe (its version column reads like 1.60.1.70707; a Windows program's own
         * version field holds 16-bit numbers and can't carry a five-digit build), else from the program's version. null when neither says.
         */
        fun buildIn(dir: File, pe: PeInfo?): Int? {
            val info = FileValidator.find(dir, ".build.info")?.takeIf { it.isFile }
            val fromInfo = info?.let { runCatching { buildOf(it.readText()) }.getOrNull() }
            return fromInfo ?: buildOf(pe?.version)
        }
    }

    override fun detect(env: ImportEnv): Detection {
        env.progress(Progress(Stage.DETECTING, "Looking for the Forever client"))
        val found = LinkedHashMap<String, SourceNode>()
        val roots = env.searchRoots()
        roots.firstNotNullOfOrNull { Packages.findRoot(it, 4, isGameRoot) }?.let { found["client"] = it }
        if (found["client"] == null) {
            Scan(roots, 5).matching(Regex("(?i)forever.*client.*\\.(zip|7z|rar|tar|tar\\.gz|tgz|tar\\.xz|tar\\.bz2|tar\\.zst)")).firstOrNull()?.let { found["client"] = it }
        }
        return Detection(validateDir(env.paths.game(gameId)).filesOk, found)
    }

    override fun resolveSources(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<AutoSource> = emptyList()

    override fun downloadAvailableFiles(env: ImportEnv, sources: List<AutoSource>) = Unit

    override fun getMissingInputs(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<MissingInput> {
        val have = FileValidator.find(env.paths.game(gameId), EXE) != null || detection.found["client"] != null || supplied["client"] is Supplied.Picked
        return if (have) emptyList() else listOf(MissingInput("client", PROMPT, PickKind.FILE_OR_FOLDER))
    }

    override fun importFiles(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>) {
        val asm = Assembler(env.paths, gameId)
        val scratch = File(env.paths.staging, "$gameId-scratch")
        try {
            val staging = asm.begin()
            asm.reuse(env.paths.game(gameId).list()?.toList() ?: emptyList()) { true }
            val client = (supplied["client"] as? Supplied.Picked)?.source ?: detection.found["client"]
            if (client != null) {
                val root = Packages.materialize(client, env, staging, scratch, "the Forever client", PROMPT, isGameRoot)
                for (f in root.listFiles().orEmpty()) {
                    val target = File(staging, f.name)
                    target.deleteTree()
                    if (!f.renameTo(target)) f.copyRecursively(target, true)
                }
            }
            env.progress(Progress(Stage.VALIDATING, "Checking the Forever client"))
            val check = validateDir(staging)
            if (!check.filesOk) throw ImportException(
                check.problem ?: Problem.MISSING_SOURCE_DATA, check.message ?: "The Forever client's files didn't check out.",
                "Checks: ${check.checks.joinToString("; ") { "${if (it.passed) "ok" else "FAILED"} ${it.name} (${it.detail})" }}\n${Packages.outline(staging)}",
            )
            asm.commit()
        } catch (e: Throwable) {
            asm.abandon()
            throw e
        } finally {
            scratch.deleteTree()
        }
    }

    override fun validate(env: ImportEnv): Validation = validateDir(env.paths.game(gameId))

    fun validateDir(dir: File): Validation {
        val checks = ArrayList<Check>()
        val exe = FileValidator.find(dir, EXE)?.takeIf { it.isFile }
        val pe = exe?.let { PeInfo.read(it) }
        checks += Check(EXE, pe != null && pe.isWindowsX86Family, if (exe == null) "missing" else if (pe == null) "not a Windows program" else "present")
        val data = FileValidator.find(dir, DATA)?.takeIf { it.isDirectory }
        checks += Check("Game data ($DATA)", data != null && data.walkTopDown().any { it.isFile }, if (data == null) "missing" else "present")
        val build = buildIn(dir, pe)
        // A build that can't be read isn't held against the client; the known ones are said, any other is shown as it is.
        checks += Check("Client build", true, build?.let { if (it in KNOWN_BUILDS) "$it" else "$it (not one of ${KNOWN_BUILDS.joinToString()})" } ?: "unknown")
        checks += Check("Executable started under Winlator", false, "not tested")
        val core = checks.take(3).all { it.passed }
        val problem = if (core) null else Problem.MISSING_SOURCE_DATA
        return Validation(checks, build?.let { "Forever client $it" }, core, problem, if (core) null else PROMPT)
    }

    override fun readyStage(validation: Validation) = Stage.IMPORTED_UNTESTED

    override fun registerLaunchEntry(env: ImportEnv, validation: Validation) = LibraryEntry(
        gameId = gameId,
        title = title,
        products = listOf("WOW"),
        clientVersion = validation.clientVersion ?: "",
        installPath = env.paths.game(gameId).path,
        executable = FileValidator.find(env.paths.game(gameId), EXE)?.relativeTo(env.paths.game(gameId))?.path ?: EXE,
        runtime = LibraryEntry.RUNTIME_WINLATOR,
        arguments = "",
        stage = Stage.IMPORTED_UNTESTED,
        saveLocation = "",
        controlProfile = "wow",
    )
}
