package com.logie.blizz.importer

import java.io.File

/**
 * World of Warcraft: Infinite (the ForeverNXT server and its client). **Add client**: the client's zip, 7z or RAR, one file the player picks
 * by hand with the phone's picker (nothing is searched for on the phone, no folder is taken). **The server** is downloaded by the app from
 * the MEGA link the user gave (22 November 2026, [SERVER_LINK], see [Mega]); if MEGA refuses it (its download limit, say), the install asks
 * for **Add server** instead: the package's 7z or zip, picked by hand.
 * The client lands in the game's `client/` folder and the server package in `server/`; no file ships with the app.
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
        /** The client is Blizzard's own folder layout (seen in the real client's archive, 22 November 2026): `.build.info`, `.battle.net/`, `Data/` (CASC archives `Data/data/data.NNN`). */
        const val BUILD_INFO = ".build.info"
        const val DATA = "Data"
        const val CLIENT = "client"
        const val SERVER = "server"
        /** The server package's marker files. */
        const val SERVER_START = "START_SERVER.cmd"
        /** The ForeverNXTCore server package (build 70707), a public MEGA link given by the user; its size is MEGA's (checked on download). */
        const val SERVER_LINK = "https://mega.nz/file/pvICFA5Q#wxQV0KH6QadFZmuFR7RGpmmU5ctvL1aRDHPo6xG_q-I"
        const val SERVER_SIZE = 1_822_679_784L
        const val SERVER_FILE = "ForeverNXTCore-Y1U14-Server-v2.3.0-70707.7z"
        /** Client builds the ForeverNXT launcher lists; any other build is shown as read, not refused. */
        val KNOWN_BUILDS = listOf(70450, 70532, 70685, 70707)
        const val PROMPT_CLIENT = "Add your Infinite client: pick its zip, 7z or RAR file."
        const val PROMPT_SERVER = "Add the ForeverNXT server package: pick its 7z or zip file."

        /** The client's folder: its `.build.info` and its `Data` folder (the archive holds it inside a `World of Warcraft` folder). */
        val isClientRoot: (Set<String>) -> Boolean = { ".build.info" in it && "data/" in it }

        /**
         * The game's program: `_forever_/Wow.exe` (seen in the real client's listing, 22 November 2026: a 64-bit, Direct3D 12 program beside
         * `dxgi.dll` (ReShade) and `Data/` at the root), else any Windows program named Wow*.exe; null when none is found.
         */
        fun programIn(client: File): File? {
            val exact = File(client, "_forever_/Wow.exe").takeIf { it.isFile && PeInfo.read(it)?.isWindowsX86Family == true }
            if (exact != null) return exact
            return client.walkTopDown().maxDepth(3)
                .filter { it.isFile && it.name.endsWith(".exe", true) && it.name.startsWith("wow", true) && !it.name.contains("voice", true) && PeInfo.read(it)?.isWindowsX86Family == true }
                .sortedBy { it.relativeTo(client).path.count { c -> c == '/' } }
                .firstOrNull()
        }

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

    /** Why the server's download didn't work: then the player is asked for the file. */
    private var serverDownloadFailure: String? = null

    private fun serverDownload(env: ImportEnv) = File(File(env.paths.downloads, gameId), SERVER_FILE)

    override fun resolveSources(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<AutoSource> {
        serverDownloadFailure = null
        if (hasServer(env.paths.game(gameId)) || supplied[SERVER] is Supplied.Picked) return emptyList()
        return listOf(AutoSource(SERVER, "The ForeverNXT server package (from MEGA)", SERVER_SIZE))
    }

    override fun downloadAvailableFiles(env: ImportEnv, sources: List<AutoSource>) {
        if (sources.none { it.id == SERVER }) return
        try {
            Mega.download(Mega.parse(SERVER_LINK), serverDownload(env), env.cancel, SERVER_SIZE) { done, total ->
                env.progress(Progress(Stage.DOWNLOADING, "Downloading the ForeverNXT server package", done, total))
            }
        } catch (e: ImportException) {
            if (e.problem == Problem.CANCELLED) throw e
            // Nothing is lost: the player picks the file themselves, and what was downloaded stays for a retry.
            serverDownloadFailure = e.message ?: "The download failed."
        }
    }

    override fun getMissingInputs(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<MissingInput> {
        val game = env.paths.game(gameId)
        val missing = ArrayList<MissingInput>()
        if (!hasClient(game) && supplied[CLIENT] !is Supplied.Picked) missing += MissingInput(CLIENT, PROMPT_CLIENT, PickKind.FILE)
        // The server comes from MEGA; only when that failed is it asked for.
        if (!hasServer(game) && supplied[SERVER] !is Supplied.Picked && serverDownloadFailure != null && !serverDownload(env).isFile) {
            missing += MissingInput(SERVER, "$serverDownloadFailure $PROMPT_SERVER", PickKind.FILE)
        }
        return missing
    }

    private fun hasClient(game: File) = FileValidator.find(File(game, CLIENT), BUILD_INFO) != null
    private fun hasServer(game: File) = File(game, "$SERVER/$SERVER_START").isFile || FileValidator.find(File(game, SERVER), SERVER_START) != null

    override fun importFiles(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>) {
        val asm = Assembler(env.paths, gameId)
        val scratch = File(env.paths.staging, "$gameId-scratch")
        try {
            val staging = asm.begin()
            // What is already installed and still wanted stays.
            asm.reuse(listOf(CLIENT, SERVER)) { true }
            place(env, staging, scratch, supplied[CLIENT], CLIENT, "the Infinite client", PROMPT_CLIENT, isClientRoot)
            val downloaded = serverDownload(env).takeIf { it.isFile && it.length() == SERVER_SIZE }
            val serverSource = supplied[SERVER] ?: downloaded?.let { Supplied.Picked(SERVER, FileNode(it)) }
            place(env, staging, scratch, serverSource, SERVER, "the ForeverNXT server package", PROMPT_SERVER, isServerRoot)
            env.progress(Progress(Stage.VALIDATING, "Checking the Infinite files"))
            val check = validateDir(staging)
            if (!check.filesOk) throw ImportException(
                check.problem ?: Problem.MISSING_SOURCE_DATA, check.message ?: "The Infinite files didn't check out.",
                "Checks: ${check.checks.joinToString("; ") { "${if (it.passed) "ok" else "FAILED"} ${it.name} (${it.detail})" }}\n${Packages.outline(staging)}",
            )
            asm.commit()
            // The package is in the game's folder now: the 1.8 GB download goes.
            serverDownload(env).delete()
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
        val info = FileValidator.find(client, BUILD_INFO)?.takeIf { it.isFile }
        val build = buildIn(client, null)
        checks += Check("Client build info ($BUILD_INFO)", info != null && build != null, if (info == null) "missing" else build?.let { "build $it" } ?: "no version in it")
        val data = FileValidator.find(client, DATA)?.takeIf { it.isDirectory }
        checks += Check("Client data ($DATA)", data != null && data.walkTopDown().any { it.isFile }, if (data == null) "missing" else "present")
        // Which build it is, said; any other than the launcher's listed ones is shown as it is, not refused.
        checks += Check("Client build", true, build?.let { if (it in KNOWN_BUILDS) "$it" else "$it (not one of ${KNOWN_BUILDS.joinToString()})" } ?: "unknown")
        // The program (`_forever_/Wow.exe`) is said; a client whose program can't be found is still taken (Play says what is missing).
        val exe = programIn(client)
        checks += Check("Game program (Wow.exe)", true, exe?.relativeTo(client)?.path ?: "not found")
        val server = File(dir, SERVER)
        val start = FileValidator.find(server, SERVER_START)?.takeIf { it.isFile }
        checks += Check("Server package ($SERVER_START)", start != null, if (start == null) "missing" else "present")
        val mysql = FileValidator.find(server, "mysql")?.takeIf { it.isDirectory }
        checks += Check("Server database (mysql)", mysql != null && mysql.walkTopDown().any { it.isFile }, if (mysql == null) "missing" else "present")
        checks += Check("Started under Winlator", false, "not tested")
        val core = checks.all { it.passed || it.name == "Started under Winlator" }
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
        executable = programIn(File(env.paths.game(gameId), CLIENT))?.relativeTo(env.paths.game(gameId))?.path ?: "$CLIENT/Wow.exe",
        runtime = LibraryEntry.RUNTIME_WINLATOR,
        arguments = "",
        stage = Stage.IMPORTED_UNTESTED,
        saveLocation = "",
        controlProfile = "wow",
    )
}
