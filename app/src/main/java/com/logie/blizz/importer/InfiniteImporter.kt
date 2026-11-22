package com.logie.blizz.importer

import java.io.File

/**
 * World of Warcraft: Infinite (the ForeverNXT server and its client), from two archives the player picks by hand at install:
 * **Add client** (the client's zip, 7z or RAR) and **Add server** (the ForeverNXT server package's 7z or zip). Each is one file chosen
 * with the phone's picker: nothing is searched for on the phone, no folder is taken and nothing is downloaded.
 * The client lands in the game's `client/` folder and the server package in `server/`; the player's own files only, no file ships with the app.
 *
 * This step makes the copies and checks them; the import ends as Imported — Launch Untested (the files can't show it starts under Winlator).
 * Running the server in Winlator is the next step.
 */
class InfiniteImporter : GameImporter {
    override val gameId = "wow_infinite"
    override val title = "World of Warcraft: Infinite"

    /** The first layout (the client straight in the game's folder, no server) is made again. */
    override val recipe = 2

    companion object {
        const val EXE = "Wow.exe"
        const val DATA = "_forever_"
        const val CLIENT = "client"
        const val SERVER = "server"
        /** The server package's marker files. */
        const val SERVER_START = "START_SERVER.cmd"
        /** Client builds the ForeverNXT launcher lists; any other build is shown as read, not refused. */
        val KNOWN_BUILDS = listOf(70450, 70532, 70685, 70707)
        const val PROMPT_CLIENT = "Add your Infinite client: pick its zip, 7z or RAR file."
        const val PROMPT_SERVER = "Add the ForeverNXT server package: pick its 7z or zip file."

        /** The client's folder: its program and its `_forever_` data folder. */
        val isClientRoot: (Set<String>) -> Boolean = { "wow.exe" in it && "_forever_/" in it }

        /** The server package's folder: its start script, its database and its releases. */
        val isServerRoot: (Set<String>) -> Boolean = { "start_server.cmd" in it && "mysql/" in it && "releases/" in it }

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

    /** Nothing is looked for by itself: the player picks both files. */
    override fun detect(env: ImportEnv): Detection =
        Detection(validateDir(env.paths.game(gameId)).filesOk, emptyMap())

    override fun resolveSources(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<AutoSource> = emptyList()

    override fun downloadAvailableFiles(env: ImportEnv, sources: List<AutoSource>) = Unit

    override fun getMissingInputs(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<MissingInput> {
        val game = env.paths.game(gameId)
        val missing = ArrayList<MissingInput>()
        if (!hasClient(game) && supplied[CLIENT] !is Supplied.Picked) missing += MissingInput(CLIENT, PROMPT_CLIENT, PickKind.FILE)
        if (!hasServer(game) && supplied[SERVER] !is Supplied.Picked) missing += MissingInput(SERVER, PROMPT_SERVER, PickKind.FILE)
        return missing
    }

    private fun hasClient(game: File) = FileValidator.find(File(game, CLIENT), EXE) != null
    private fun hasServer(game: File) = File(game, "$SERVER/$SERVER_START").isFile || FileValidator.find(File(game, SERVER), SERVER_START) != null

    override fun importFiles(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>) {
        val asm = Assembler(env.paths, gameId)
        val scratch = File(env.paths.staging, "$gameId-scratch")
        try {
            val staging = asm.begin()
            // What is already installed and still wanted stays.
            asm.reuse(listOf(CLIENT, SERVER)) { true }
            place(env, staging, scratch, supplied[CLIENT], CLIENT, "the Infinite client", PROMPT_CLIENT, isClientRoot)
            place(env, staging, scratch, supplied[SERVER], SERVER, "the ForeverNXT server package", PROMPT_SERVER, isServerRoot)
            env.progress(Progress(Stage.VALIDATING, "Checking the Infinite files"))
            val check = validateDir(staging)
            if (!check.filesOk) throw ImportException(
                check.problem ?: Problem.MISSING_SOURCE_DATA, check.message ?: "The Infinite files didn't check out.",
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

    /** One picked archive, unpacked and moved into staging's [folder]; nothing picked leaves what is there. */
    private fun place(env: ImportEnv, staging: File, scratch: File, supplied: Supplied?, folder: String, what: String, prompt: String, isRoot: (Set<String>) -> Boolean) {
        val picked = (supplied as? Supplied.Picked)?.source ?: return
        if (picked.isDirectory) throw ImportException(Problem.MISSING_SOURCE_DATA, "Pick the file itself (a zip, 7z or RAR), not a folder. $prompt")
        val root = Packages.materialize(picked, env, staging, File(scratch, folder), what, prompt, isRoot)
        val target = File(staging, folder)
        target.deleteTree()
        target.mkdirs()
        for (f in root.listFiles().orEmpty()) {
            val to = File(target, f.name)
            if (!f.renameTo(to)) f.copyRecursively(to, true)
        }
    }

    override fun validate(env: ImportEnv): Validation = validateDir(env.paths.game(gameId))

    fun validateDir(dir: File): Validation {
        val checks = ArrayList<Check>()
        val client = File(dir, CLIENT)
        val exe = FileValidator.find(client, EXE)?.takeIf { it.isFile }
        val pe = exe?.let { PeInfo.read(it) }
        checks += Check(EXE, pe != null && pe.isWindowsX86Family, if (exe == null) "missing" else if (pe == null) "not a Windows program" else "present")
        val data = FileValidator.find(client, DATA)?.takeIf { it.isDirectory }
        checks += Check("Client data ($DATA)", data != null && data.walkTopDown().any { it.isFile }, if (data == null) "missing" else "present")
        val build = buildIn(client, pe)
        // A build that can't be read isn't held against the client; the listed ones are said, any other is shown as it is.
        checks += Check("Client build", true, build?.let { if (it in KNOWN_BUILDS) "$it" else "$it (not one of ${KNOWN_BUILDS.joinToString()})" } ?: "unknown")
        val server = File(dir, SERVER)
        val start = FileValidator.find(server, SERVER_START)?.takeIf { it.isFile }
        checks += Check("Server package ($SERVER_START)", start != null, if (start == null) "missing" else "present")
        val mysql = FileValidator.find(server, "mysql")?.takeIf { it.isDirectory }
        checks += Check("Server database (mysql)", mysql != null && mysql.walkTopDown().any { it.isFile }, if (mysql == null) "missing" else "present")
        checks += Check("Started under Winlator", false, "not tested")
        val core = checks.take(5).all { it.passed }
        val problem = if (core) null else Problem.MISSING_SOURCE_DATA
        return Validation(checks, build?.let { "Infinite client $it" }, core, problem, if (core) null else "$PROMPT_CLIENT $PROMPT_SERVER")
    }

    override fun readyStage(validation: Validation) = Stage.IMPORTED_UNTESTED

    override fun registerLaunchEntry(env: ImportEnv, validation: Validation) = LibraryEntry(
        gameId = gameId,
        title = title,
        products = listOf("WOW"),
        clientVersion = validation.clientVersion ?: "",
        installPath = env.paths.game(gameId).path,
        executable = FileValidator.find(File(env.paths.game(gameId), CLIENT), EXE)?.relativeTo(env.paths.game(gameId))?.path ?: "$CLIENT/$EXE",
        runtime = LibraryEntry.RUNTIME_WINLATOR,
        arguments = "",
        stage = Stage.IMPORTED_UNTESTED,
        saveLocation = "",
        controlProfile = "wow",
    )
}
