package com.logie.blizz.importer

import com.logie.blizz.d2r.D2r
import java.io.File

/**
 * Diablo II: Resurrected from the player's own Nintendo Switch packages: the base game's .nsp and the
 * update's (1.0.34.0, PC 3.3.94012), each as the file, in a folder, or inside a 7z, zip or tar, and
 * the player's `prod.keys`. First the **module** (D2R Mobile's native host) is downloaded from its
 * release; then the packages are unpacked with hactool, the way the project's `extract_game.sh` does:
 * the title keys come from the tickets, the base game's program content and the update's are told
 * apart, the update is extracted over the base, the three program files are checked to be the
 * 3.3.94012 ones, and only what the game reads at run time is kept (the 18 resource archives, the
 * build config, the manifest, the ExeFS), about 5.6 GB. Nothing is uploaded; the keys are copied into a
 * private folder for the unpacking and deleted with it.
 *
 * Making the game run from these files is the host's job ([D2r]); the last step of the port's own
 * tooling (the Android import pack) isn't done on the phone yet, so the game is IMPORTED_UNTESTED.
 */
class Diablo2ResurrectedImporter : GameImporter {
    override val gameId = D2r.GAME_ID
    override val title = "Diablo II: Resurrected"

    companion object {
        const val PROMPT_BASE = "Select the base game: the Diablo II: Resurrected .nsp, a folder with it, or the 7z (zip, tar) that holds it."
        const val PROMPT_UPDATE = "Select the update (1.0.34.0): its .nsp, a folder, or the 7z that holds it. It can be in the same package as the base game."
        const val PROMPT_KEYS = "Select your prod.keys, the key file dumped from your own Switch."
        private val NSP = Regex(".*\\.nsp")
        private const val SPACE = 26L shl 30
    }

    private var moduleAsset: ReleaseAsset? = null

    override fun detect(env: ImportEnv): Detection {
        env.progress(Progress(Stage.DETECTING, "Looking for the Switch files"))
        val scan = Scan(env.searchRoots())
        val found = LinkedHashMap<String, SourceNode>()
        scan.named("prod.keys")?.let { found["keys"] = it }
        return Detection(validateDir(env.paths.game(gameId)).filesOk, found)
    }

    override fun resolveSources(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<AutoSource> {
        if (D2r.hasModule(env.paths) || !env.online()) return emptyList()
        val asset = runCatching { env.releases.latest(D2r.REPO).firstOrNull { it.name == D2r.APK } }.getOrNull() ?: return emptyList()
        moduleAsset = asset
        return listOf(AutoSource("module", "D2R Mobile's module ${asset.release}", asset.size))
    }

    override fun downloadAvailableFiles(env: ImportEnv, sources: List<AutoSource>) {
        val asset = moduleAsset ?: return
        if (sources.none { it.id == "module" }) return
        val target = File(env.paths.downloads, "d2r-${asset.release}-${asset.name}")
        FileValidator.requireSpace(env.paths.downloads, asset.size * 2)
        env.downloads.download(asset.url, target, env.cancel, asset.size, asset.sha256) { done, total ->
            env.progress(Progress(Stage.DOWNLOADING, "Downloading D2R Mobile's module ${asset.release}", done, total))
        }
        env.progress(Progress(Stage.EXTRACTING, "Installing the module"))
        D2r.installModule(target, env.paths, asset.release, env.cancel)
        target.delete()
    }

    override fun getMissingInputs(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<MissingInput> {
        val missing = ArrayList<MissingInput>()
        if (!D2r.hasModule(env.paths)) {
            missing += MissingInput("module", "D2R Mobile's module couldn't be downloaded (no connection, or GitHub didn't answer). Connect to the internet and retry.", PickKind.FILE, optional = true, skipLabel = "Go on without it")
        }
        if (supplied["base"] !is Supplied.Picked) missing += MissingInput("base", PROMPT_BASE, PickKind.FILE_OR_FOLDER)
        if (supplied["update"] == null) missing += MissingInput("update", PROMPT_UPDATE, PickKind.FILE_OR_FOLDER, optional = true, skipLabel = "It's in the same package")
        if (supplied["keys"] !is Supplied.Picked && detection.found["keys"] == null) missing += MissingInput("keys", PROMPT_KEYS, PickKind.FILE)
        return missing
    }

    override fun importFiles(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>) {
        val hactool = env.hactool ?: throw ImportException(Problem.MISSING_RUNTIME_DEPENDENCY, "hactool is missing from this build of the app.")
        val keysSource = (supplied["keys"] as? Supplied.Picked)?.source ?: detection.found["keys"]
            ?: throw ImportException(Problem.MISSING_SOURCE_DATA, PROMPT_KEYS)
        val asm = Assembler(env.paths, gameId)
        val work = File(env.paths.staging, "$gameId-work")
        val home = File(env.paths.staging, "$gameId-keys")
        try {
            FileValidator.requireSpace(env.paths.staging, SPACE)
            val staging = asm.begin()
            work.deleteTree(); home.deleteTree()
            val nca = File(work, "nca").also { it.mkdirs() }
            File(home, ".switch").mkdirs()

            // The keys: a private copy where hactool looks for them, plus the title keys the tickets hold.
            val keys = File(home, ".switch/prod.keys")
            // Only the lines hactool takes (it refuses the whole file over one key of another length).
            val (cleanKeys, droppedKeys) = SwitchPackages.cleanKeys(keysSource.open().use { it.readBytes().toString(Charsets.UTF_8) })
            keys.writeText(cleanKeys)
            if (droppedKeys.isNotEmpty()) env.progress(Progress(Stage.EXTRACTING, "Left out ${droppedKeys.size} keys hactool doesn't take"))
            val titleKeys = File(home, ".switch/title.keys")
            titleKeys.writeText("")

            // The packages: the base game's and the update's, each unpacked to its contents (.nca and tickets).
            val packages = listOfNotNull(
                (supplied["base"] as? Supplied.Picked)?.source,
                (supplied["update"] as? Supplied.Picked)?.source,
            )
            var n = 0
            for (source in packages) {
                for (nsp in nspsIn(source, File(work, "src${++n}"), env)) {
                    env.progress(Progress(Stage.EXTRACTING, "Unpacking ${nsp.name}"))
                    val (code, out) = hactool.run(keys, home, listOf("-t", "pfs0", "--outdir=${nca.path}", nsp.path), work, env.cancel)
                    if (code != 0) throw ImportException(Problem.CORRUPT_ARCHIVE, "${nsp.name} couldn't be unpacked: the keys are wrong or the file is damaged.", out.lines().takeLast(3).joinToString("\n"))
                    if (nsp.toPath().startsWith(work.toPath())) nsp.delete()
                }
            }
            val tickets = nca.listFiles { f -> f.extension.equals("tik", true) }.orEmpty()
            var personalized = 0
            for (tik in tickets) {
                val bytes = tik.readBytes()
                SwitchPackages.titleKey(bytes)?.let { titleKeys.appendText(SwitchPackages.titleKeysLine(it) + "\n") }
                    ?: if (SwitchPackages.ticketKind(bytes) == SwitchPackages.TicketKind.PERSONALIZED) personalized++ else Unit
            }

            // Which contents are the base game's program and the update's.
            var base: File? = null
            var update: File? = null
            for (f in nca.listFiles { f -> f.extension.equals("nca", true) && !f.name.endsWith(".cnmt.nca", true) }.orEmpty()) {
                env.cancel.check()
                val (_, info) = hactool.run(keys, home, listOf("-t", "nca", f.path), work, env.cancel)
                when (SwitchPackages.classify(info)) {
                    SwitchPackages.Content.BASE -> base = f
                    SwitchPackages.Content.UPDATE -> update = f
                    SwitchPackages.Content.OTHER -> {}
                }
            }
            if (base == null) throw ImportException(Problem.MISSING_SOURCE_DATA, "The base game isn't in what you picked (if the base game and the update are separate packages, pick both).")
            if (update == null) throw ImportException(Problem.MISSING_SOURCE_DATA, "The update isn't in what you picked: the 1.0.34.0 update is needed as well as the base game.")

            env.progress(Progress(Stage.EXTRACTING, "Extracting the game's program and resources (several GB)"))
            val out = File(staging, "Update")
            val (code, log) = hactool.run(
                keys, home,
                listOf("-t", "nca", "--basenca=${base.path}", "--exefsdir=${File(out, "ExeFS").path}", "--romfsdir=${File(out, "RomFS").path}", update.path),
                work, env.cancel,
            ) { line -> if (line.contains("Saving") || line.contains("Extracting")) env.progress(Progress(Stage.EXTRACTING, line.take(80))) }
            if (code != 0) {
                val hint = if (personalized > 0) " The tickets are tied to the console they came from (personalized): their title keys can't be read, so add them to the keys file." else ""
                throw ImportException(Problem.CORRUPT_ARCHIVE, "The update couldn't be extracted: wrong keys, or a file that is damaged.$hint", log.lines().takeLast(3).joinToString("\n"))
            }
            nca.deleteTree()

            // Only what the game reads: the rest of RomFS/data goes.
            val data = File(out, "RomFS/data")
            data.listFiles()?.filter { it.isFile && !SwitchPackages.keep(it.name) }?.forEach { it.delete() }
            data.listFiles()?.filter { it.isDirectory }?.forEach { it.deleteTree() }

            val check = validateDir(staging)
            if (!check.filesOk) throw ImportException(check.problem ?: Problem.UNSUPPORTED_VERSION, check.message ?: "The files didn't check out.")
            asm.commit()
        } catch (e: Throwable) {
            asm.abandon()
            throw e
        } finally {
            work.deleteTree()
            home.deleteTree()
        }
    }

    /** The .nsp files [source] is or holds: the file itself, those in a folder, or those in an archive unpacked under [scratch]. */
    private fun nspsIn(source: SourceNode, scratch: File, env: ImportEnv): List<File> {
        if (source.isDirectory) return source.walk(6).filter { !it.isDirectory && NSP.matches(it.name.lowercase()) }.map { localCopy(it, scratch, env.cancel) }.toList()
        if (source.name.lowercase().endsWith(".nsp")) return listOf(localCopy(source, scratch, env.cancel))
        Unpacker(env.innoextract).unpack(source, emptyList(), scratch, File(scratch, "tmp"), env.cancel, env.progress)
        val found = scratch.walkTopDown().filter { it.isFile && NSP.matches(it.name.lowercase()) }.toList()
        File(scratch, "tmp").deleteTree()
        if (found.isEmpty()) throw ImportException(Problem.MISSING_SOURCE_DATA, "There's no .nsp in ${source.name}.")
        return found
    }

    override fun validate(env: ImportEnv): Validation = validateDir(env.paths.game(gameId))

    fun validateDir(dir: File): Validation {
        val update = File(dir, "Update")
        val checks = ArrayList<Check>()
        checks += SwitchPackages.exefsChecks(File(update, "ExeFS"))
        val data = File(update, "RomFS/data")
        val missing = SwitchPackages.ARCHIVES.filter { !File(data, it).isFile }
        checks += Check("Resource archives", missing.isEmpty(), if (missing.isEmpty()) "all ${SwitchPackages.ARCHIVES.size}" else "missing ${missing.take(3).joinToString()}${if (missing.size > 3) " and ${missing.size - 3} more" else ""}")
        checks += Check(SwitchPackages.BUILD_CONFIG, File(data, SwitchPackages.BUILD_CONFIG).isFile || File(data, "build.config").isFile, "")
        checks += Check(SwitchPackages.MANIFEST, File(data, SwitchPackages.MANIFEST).isFile, "")
        checks += Check("Not tested", false, "the game hasn't been started from these files")
        val wrongVersion = checks.take(3).any { !it.passed && it.detail == "not the 3.3.94012 version" }
        val filesOk = checks.take(SwitchPackages.EXEFS_SHA256.size + 3).all { it.passed }
        val problem = when {
            filesOk -> null
            wrongVersion -> Problem.UNSUPPORTED_VERSION
            else -> Problem.MISSING_SOURCE_DATA
        }
        val message = when (problem) {
            Problem.UNSUPPORTED_VERSION -> "These aren't the 1.0.34.0 files (PC 3.3.94012) the port is made for. $PROMPT_UPDATE"
            Problem.MISSING_SOURCE_DATA -> "The game's files are incomplete: ${checks.filter { !it.passed && it.name != "Not tested" }.joinToString { "${it.name} ${it.detail}".trim() }}."
            else -> null
        }
        return Validation(checks, "Diablo II: Resurrected 1.0.34.0 (3.3.94012)".takeIf { filesOk }, filesOk, problem, message)
    }

    override fun readyStage(validation: Validation) = Stage.IMPORTED_UNTESTED

    override fun registerLaunchEntry(env: ImportEnv, validation: Validation) = LibraryEntry(
        gameId = gameId,
        title = title,
        products = listOf("D2R", "ROTW"),
        clientVersion = validation.clientVersion ?: "",
        installPath = env.paths.game(gameId).path,
        executable = "Update/ExeFS/main",
        runtime = LibraryEntry.RUNTIME_D2R,
        arguments = "",
        stage = Stage.IMPORTED_UNTESTED,
        saveLocation = null,
        controlProfile = "diablo2",
    )
}
