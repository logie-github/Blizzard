package com.logie.blizz.importer

import java.io.File

/**
 * Diablo and Hellfire through DevilutionX's Windows build, on Winlator (so the app's gestures are
 * over it). The engine comes from DevilutionX's own GitHub release (its published SHA-256 checked)
 * or a release zip the person has; the game's data (DIABDAT.MPQ, and Hellfire's four archives,
 * optional) from the person's files: the archives themselves, a folder, a disc image, or GOG's
 * offline installer, unpacked by innoextract without running it.
 *
 * DevilutionX is under its Sustainable Use License (non-commercial use and free distribution
 * only); the app downloads the project's own release on the phone and redistributes nothing.
 */
class Diablo1DevilutionXImporter : GameImporter {
    override val gameId = "diablo"
    override val title = "Diablo"

    companion object {
        const val REPO = "diasurgical/devilutionX"
        const val EXE = "devilutionx.exe"
        const val DATA = "diabdat.mpq"
        val HELLFIRE = listOf("hellfire.mpq", "hfmonk.mpq", "hfmusic.mpq", "hfvoice.mpq")
        val GOG_INSTALLER = Regex("setup_diablo.*\\.exe")
        val ENGINE_ZIP = Regex("devilutionx.*windows.*\\.zip|devilutionx_x(64|86)\\.zip")

        /** The release's Windows build: 64-bit first, never the XP or Windows 9x ones. */
        fun pickAsset(assets: List<ReleaseAsset>): ReleaseAsset? {
            val windows = assets.filter { a ->
                val n = a.name.lowercase()
                n.endsWith(".zip") && n.contains("windows") && !n.contains("xp") && !n.contains("9x") && !n.contains("debug")
            }
            return windows.firstOrNull { it.name.lowercase().contains("x86_64") || it.name.lowercase().contains("x64") } ?: windows.firstOrNull()
        }

        const val PROMPT_DATA = "Select your Diablo I GOG offline installer, original game-data folder, or DIABDAT.MPQ."
        const val PROMPT_HELLFIRE = "Hellfire game data was not found. Import Hellfire files, or continue with Diablo I only?"
        const val PROMPT_ENGINE = "DevilutionX couldn't be downloaded (no connection). Select a DevilutionX Windows release zip (devilutionx-windows-x86_64.zip)."

        /** Diablo as it was: every DevilutionX option that changes the game, off. */
        val VANILLA_INI = """
            [Game]
            Run in Town=0
            Theo Quest=0
            Cow Quest=0
            Test Bard=0
            Test Barbarian=0
            Experience Bar=0
            Show health values=0
            Show mana values=0
            Enemy Health Bar=0
            Floating Item Info Box=0
            Auto Gold Pickup=0
            Auto Elixir Pickup=0
            Auto Oil Pickup=0
            Auto Pickup in Town=0
            Auto Equip Weapons=0
            Auto Equip Armor=0
            Auto Equip Helms=0
            Auto Equip Shields=0
            Auto Equip Jewelry=0
            Show Monster Type=0
            Show Item Labels=0
            Auto Refill Belt=0
            Disable Crippling Shrines=0
            Quick Cast=0
            Heal Potion Pickup=0
            Full Heal Potion Pickup=0
            Mana Potion Pickup=0
            Full Mana Potion Pickup=0
            Rejuvenation Potion Pickup=0
            Full Rejuvenation Potion Pickup=0

            [Graphics]
            Fullscreen=1
            Width=640
            Height=480
        """.trimIndent() + "\n"
    }

    private var asset: ReleaseAsset? = null
    private var engineZip: File? = null

    override fun detect(env: ImportEnv): Detection {
        env.progress(Progress(Stage.DETECTING, "Looking for Diablo's files"))
        val game = env.paths.game(gameId)
        val scan = Scan(env.searchRoots())
        val found = LinkedHashMap<String, SourceNode>()
        (scan.named(DATA) ?: scan.matching(GOG_INSTALLER).firstOrNull())?.let { found["data"] = it }
        // Hellfire's four archives together: the folder they're in.
        env.searchRoots().firstNotNullOfOrNull { root ->
            findFolder(root, 6) { files -> HELLFIRE.all { n -> files.any { it.name.equals(n, true) } } }
        }?.let { found["hellfire"] = it } ?: scan.matching(GOG_INSTALLER).firstOrNull()?.let { found["hellfire"] = it }
        scan.matching(ENGINE_ZIP).firstOrNull()?.let { found["engine"] = it }
        val installed = validateDir(game).filesOk
        return Detection(installed, found)
    }

    private fun hasEngine(env: ImportEnv) = FileValidator.find(env.paths.game(gameId), EXE) != null
    private fun hasData(env: ImportEnv) = FileValidator.find(env.paths.game(gameId), DATA)?.let { Mpq.isArchive(it) } == true
    private fun hasHellfire(env: ImportEnv) = HELLFIRE.all { n -> FileValidator.find(env.paths.game(gameId), n)?.let { Mpq.isArchive(it) } == true }

    override fun resolveSources(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<AutoSource> {
        if (supplied["engine"] is Supplied.Picked || detection.found["engine"] != null) return emptyList()
        if (hasEngine(env) || !env.online()) return emptyList()
        val chosen = runCatching { pickAsset(env.releases.latest(REPO)) }.getOrNull() ?: return emptyList()
        asset = chosen
        return listOf(AutoSource("engine", "DevilutionX ${chosen.release} (${chosen.name})", chosen.size))
    }

    override fun downloadAvailableFiles(env: ImportEnv, sources: List<AutoSource>) {
        val chosen = asset ?: return
        if (sources.none { it.id == "engine" }) return
        val target = File(env.paths.downloads, "devilutionx-${chosen.release}-${chosen.name}")
        FileValidator.requireSpace(env.paths.downloads, chosen.size)
        // GitHub's published SHA-256 when it has one; the zip's integrity is checked as it's extracted.
        engineZip = env.downloads.download(chosen.url, target, env.cancel, chosen.size, chosen.sha256) { done, total ->
            env.progress(Progress(Stage.DOWNLOADING, "Downloading DevilutionX ${chosen.release}", done, total))
        }
    }

    override fun getMissingInputs(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<MissingInput> {
        val missing = ArrayList<MissingInput>()
        val engineKnown = hasEngine(env) || engineZip != null || detection.found["engine"] != null || supplied["engine"] is Supplied.Picked
        if (!engineKnown) missing += MissingInput("engine", PROMPT_ENGINE, PickKind.FILE)
        if (!hasData(env) && detection.found["data"] == null && supplied["data"] !is Supplied.Picked) {
            missing += MissingInput("data", PROMPT_DATA, PickKind.FILE_OR_FOLDER)
        }
        val hellfireKnown = hasHellfire(env) || detection.found["hellfire"] != null || supplied["hellfire"] != null ||
            (supplied["data"] as? Supplied.Picked)?.let { isInstallerOrFolder(it.source) } == true
        if (!hellfireKnown) missing += MissingInput("hellfire", PROMPT_HELLFIRE, PickKind.FILE_OR_FOLDER, optional = true, skipLabel = "Diablo I only")
        return missing
    }

    private fun isInstallerOrFolder(node: SourceNode) = node.isDirectory || GOG_INSTALLER.matches(node.name.lowercase())

    override fun importFiles(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>) {
        val asm = Assembler(env.paths, gameId)
        val scratch = File(env.paths.staging, "$gameId-scratch")
        try {
            FileValidator.requireSpace(env.paths.staging, 1_600L shl 20)
            val staging = asm.begin()
            scratch.deleteTree()
            // What's already installed and still good stays (moved, not copied).
            asm.reuse(env.paths.game(gameId).list()?.toList() ?: emptyList()) { f -> !f.name.endsWith(".mpq", true) || Mpq.isArchive(f) }

            env.progress(Progress(Stage.EXTRACTING, "Unpacking DevilutionX"))
            val zip = (supplied["engine"] as? Supplied.Picked)?.source ?: engineZip?.let { FileNode(it) } ?: detection.found["engine"]
            if (zip != null) installEngine(zip, staging, scratch, env)
            if (FileValidator.find(staging, EXE) == null) {
                throw ImportException(Problem.MISSING_RUNTIME_DEPENDENCY, "DevilutionX isn't there: connect to the internet to download it, or select its Windows release zip.")
            }

            val sources = listOfNotNull((supplied["data"] as? Supplied.Picked)?.source, detection.found["data"])
            if (FileValidator.find(staging, DATA)?.let { Mpq.isArchive(it) } != true) {
                val got = sources.firstNotNullOfOrNull { collect(it, listOf(DATA), staging, scratch, env)[DATA] }
                    ?: throw ImportException(Problem.MISSING_SOURCE_DATA, "Diablo I game data is missing. $PROMPT_DATA")
                if (!Mpq.isArchive(got)) throw ImportException(Problem.CORRUPT_ARCHIVE, "That DIABDAT.MPQ isn't a valid archive (damaged, or not Diablo's).")
            }
            if (supplied["hellfire"] !is Supplied.Skipped && !HELLFIRE.all { FileValidator.find(staging, it) != null }) {
                val hf = listOfNotNull((supplied["hellfire"] as? Supplied.Picked)?.source, detection.found["hellfire"]) + sources
                for (source in hf) {
                    collect(source, HELLFIRE, staging, scratch, env)
                    if (HELLFIRE.all { FileValidator.find(staging, it) != null }) break
                }
            }
            // Hellfire is all four archives or none.
            if (!HELLFIRE.all { FileValidator.find(staging, it) != null }) HELLFIRE.forEach { FileValidator.find(staging, it)?.delete() }

            writeSettings(env)
            env.progress(Progress(Stage.VALIDATING, "Checking Diablo"))
            val check = validateDir(staging)
            if (!check.filesOk) throw ImportException(check.problem ?: Problem.MISSING_SOURCE_DATA, check.message ?: "Diablo's files didn't check out.")
            asm.commit()
        } catch (e: Throwable) {
            asm.abandon()
            throw e
        } finally {
            scratch.deleteTree()
        }
    }

    /** The release zip's folder with devilutionx.exe, whole, into staging. */
    private fun installEngine(zip: SourceNode, staging: File, scratch: File, env: ImportEnv) {
        val out = File(scratch, "engine")
        zip.open().use { ZipExtractor.extract(it, out, env.cancel) }
        val exe = out.walkTopDown().firstOrNull { it.isFile && it.name.equals(EXE, ignoreCase = true) }
            ?: throw ImportException(Problem.UNSUPPORTED_INSTALLER, "${zip.name} isn't a DevilutionX Windows release: there's no devilutionx.exe in it.")
        val pe = PeInfo.read(exe)
        if (pe == null || !pe.isWindowsX86Family) throw ImportException(Problem.UNSUPPORTED_INSTALLER, "${zip.name}'s devilutionx.exe isn't a Windows x86 program.")
        for (file in exe.parentFile!!.listFiles()!!) {
            val target = File(staging, file.name.lowercase().takeIf { it == EXE } ?: file.name)
            if (file.isDirectory) file.copyRecursively(target, overwrite = true) else { target.delete(); file.renameTo(target) || run { file.copyTo(target, true); true } }
        }
    }

    /** [names] out of [source] (an archive, a folder, a disc image, a GOG installer, a zip) into [staging]. */
    private fun collect(source: SourceNode, names: List<String>, staging: File, scratch: File, env: ImportEnv): Map<String, File> {
        val got = HashMap<String, File>()
        val lower = source.name.lowercase()
        when {
            source.isDirectory -> {
                for (name in names) source.walk(4).firstOrNull { it.name.equals(name, true) }?.let { got[name] = copyInto(it, staging, name, env.cancel) }
                if (got.size < names.size) source.walk(2).firstOrNull { GOG_INSTALLER.matches(it.name.lowercase()) }?.let { installer ->
                    got += collect(installer, names - got.keys, staging, scratch, env)
                }
            }
            lower in names -> got[lower] = copyInto(source, staging, lower, env.cancel)
            GOG_INSTALLER.matches(lower) || lower.endsWith(".exe") -> {
                val tool = env.innoextract ?: throw ImportException(Problem.MISSING_RUNTIME_DEPENDENCY, "innoextract is missing from this build of the app.")
                if (source.localFile() == null && source is DocumentNode) {
                    // GOG's installer for Diablo is a single .exe; a picked one is copied here first.
                    env.progress(Progress(Stage.EXTRACTING, "Copying ${source.name}"))
                }
                val exe = localCopy(source, File(scratch, "installer"), env.cancel)
                env.progress(Progress(Stage.EXTRACTING, "Unpacking ${source.name} (GOG's installer)"))
                val out = File(scratch, "gog")
                tool.extract(exe, out, env.cancel)
                for (name in names) out.walkTopDown().firstOrNull { it.isFile && it.name.equals(name, true) }?.let { f ->
                    val target = File(staging, name)
                    target.delete()
                    if (!f.renameTo(target)) f.copyTo(target, true)
                    got[name] = target
                }
            }
            lower.endsWith(".zip") -> source.open().use { input ->
                val out = File(scratch, "zip")
                ZipExtractor.extract(input, out, env.cancel, filter = { entry -> entry.substringAfterLast('/').lowercase() in names })
                for (f in out.walkTopDown().filter { it.isFile }) {
                    val name = f.name.lowercase()
                    val target = File(staging, name)
                    target.delete()
                    if (!f.renameTo(target)) f.copyTo(target, true)
                    got[name] = target
                }
            }
            lower.endsWith(".iso") -> {
                val iso = Iso9660(localCopy(source, File(scratch, "iso"), env.cancel))
                for (name in names) iso.find(name)?.let { e -> iso.open(e).use { got[name] = File(staging, name).also { t -> copyStream(it, t, env.cancel) } } }
            }
        }
        return got
    }

    /** DevilutionX's settings, Diablo as it was; written once, never over the person's own. */
    private fun writeSettings(env: ImportEnv) {
        val dir = env.paths.saves(gameId)
        dir.mkdirs()
        val ini = File(dir, "diablo.ini")
        if (!ini.exists()) ini.writeAtomically(VANILLA_INI)
    }

    override fun validate(env: ImportEnv): Validation = validateDir(env.paths.game(gameId))

    fun validateDir(dir: File): Validation {
        val (engine, pe) = programChecks(dir, EXE)
        val checks = engine.toMutableList()
        val mpq = FileValidator.find(dir, "devilutionx.mpq")
        checks += Check("devilutionx.mpq (DevilutionX's own data)", mpq != null, if (mpq == null) "not in this DevilutionX build" else "present")
        checks += FileValidator.requireArchives(dir, listOf(DATA))
        val hellfire = HELLFIRE.map { FileValidator.find(dir, it) }
        val hfCount = hellfire.count { it != null && Mpq.isArchive(it) }
        checks += Check("Hellfire (optional)", hfCount == 0 || hfCount == 4, when (hfCount) { 0 -> "not imported"; 4 -> "all four archives"; else -> "$hfCount of 4 archives" })
        val engineOk = checks.first().passed && checks[1].passed && mpq != null
        val dataOk = checks.first { it.name == DATA }.passed
        val problem = when {
            !engineOk -> Problem.MISSING_RUNTIME_DEPENDENCY
            !dataOk -> Problem.MISSING_SOURCE_DATA
            hfCount in 1..3 -> Problem.MISSING_EXPANSION
            else -> null
        }
        val message = when (problem) {
            Problem.MISSING_RUNTIME_DEPENDENCY -> "DevilutionX isn't complete: ${checks.filter { !it.passed }.joinToString { "${it.name} ${it.detail}" }}."
            Problem.MISSING_SOURCE_DATA -> "Diablo I game data is missing. $PROMPT_DATA"
            Problem.MISSING_EXPANSION -> "Hellfire's archives are incomplete. Select Hellfire's files again, or continue with Diablo I only."
            else -> null
        }
        val version = "DevilutionX ${pe?.version ?: "?"}" + if (hfCount == 4) " · Diablo + Hellfire" else " · Diablo"
        return Validation(checks, version, problem == null, problem, message)
    }

    override fun registerLaunchEntry(env: ImportEnv, validation: Validation): LibraryEntry {
        val hellfire = HELLFIRE.all { FileValidator.find(env.paths.game(gameId), it) != null }
        return LibraryEntry(
            gameId = gameId,
            title = if (hellfire) "Diablo + Hellfire" else "Diablo",
            products = if (hellfire) listOf("DIABLO", "HELLFIRE") else listOf("DIABLO"),
            clientVersion = validation.clientVersion ?: "",
            installPath = env.paths.game(gameId).path,
            executable = EXE,
            runtime = LibraryEntry.RUNTIME_WINLATOR,
            // Its data from its folder, its saves and settings in the app's saves folder (S:).
            arguments = "--data-dir D:\\$gameId --save-dir S:\\$gameId --config-dir S:\\$gameId",
            stage = Stage.READY,
            saveLocation = env.paths.saves(gameId).path,
            controlProfile = "diablo",
        )
    }
}
