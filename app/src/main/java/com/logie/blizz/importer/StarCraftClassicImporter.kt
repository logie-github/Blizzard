package com.logie.blizz.importer

import java.io.File

/**
 * StarCraft and Brood War, the classic client (never Remastered). From Blizzard's own legacy
 * servers (blizzard-legacy-dl: the StarCraft + Brood War payload, 1.15.2, built into a disc-free
 * game folder with StarCraft.mpq and BroodWar.mpq), or the person's installation folder, with the
 * discs' archives made from their disc images or INSTALL.EXE (Blizzard's documented way to play
 * without the discs, since 1.15.2). Saved games, replays and characters are in the game folder in
 * this version: an import or repair keeps the ones there and never overwrites them.
 *
 * Blizzard serves 1.15.2; 1.16.1 is accepted when the person's installation is already patched.
 * Blizzard no longer serves the 1.16.1 patch, so the app doesn't apply it.
 */
class StarCraftClassicImporter : GameImporter {
    override val gameId = "starcraft"
    override val title = "StarCraft"

    companion object {
        const val EXE = "StarCraft.exe"
        val REQUIRED = listOf("storm.dll", "Local.dll", "Smackw32.dll", "standard.snp")
        val ARCHIVES = listOf("StarDat.mpq", "BrooDat.mpq", "patch_rt.mpq")
        const val SC_DISC = "StarCraft.mpq"
        const val BW_DISC = "BroodWar.mpq"
        /** The player's own files, kept through a repair. */
        val USER_DATA = listOf("characters", "save", "maps/replays")
        /** What the data archives must hold: StarCraft stops with "unable to open a required file" if they don't. */
        val CONTENTS = mapOf(
            "StarDat.mpq" to listOf("font\\font.gid", "font\\font.clh", "font\\font16.fnt", "rez\\glumain.bin", "arr\\units.dat"),
            "BrooDat.mpq" to listOf("arr\\units.dat"),
        )
        val SUPPORTED = listOf("1.15.2.", "1.15.3.", "1.16.0.", "1.16.1.")
        fun supported(version: String?): Boolean = version != null && SUPPORTED.any { version.startsWith(it) }
        const val SIZE = 1_300L shl 20
        const val PROMPT_INSTALL = "Select your original StarCraft/Brood War installation folder, legacy installer, or disc image."
        const val PROMPT_SC_DISC = "StarCraft data archive missing. Select StarCraft.mpq or the original StarCraft disc image (or its INSTALL.EXE)."
        const val PROMPT_BW_DISC = "Brood War data archive missing. Select BroodWar.mpq or the original Brood War disc image."
        const val MARK = ".from-blizzard"
    }

    /** The player's own characters, saved games and replays live in the game's folder: a reset keeps them. */
    override val keptInGame: List<String> = USER_DATA

    override fun detect(env: ImportEnv): Detection {
        env.progress(Progress(Stage.DETECTING, "Looking for StarCraft"))
        val found = LinkedHashMap<String, SourceNode>()
        val roots = env.searchRoots()
        roots.firstNotNullOfOrNull { findInstall(it, 4) }?.let { found["install"] = it }
        val scan = Scan(roots)
        scan.named(SC_DISC)?.let { found["scdisc"] = it }
        scan.named(BW_DISC)?.let { found["bwdisc"] = it }
        for (iso in scan.files.filter { it.name.endsWith(".iso", true) && it.localFile() != null }) {
            val label = discLabel(iso.localFile()!!) ?: continue
            if (label.contains("BROOD")) found.putIfAbsent("bwdisc", iso) else if (label.contains("STARCRAFT")) found.putIfAbsent("scdisc", iso)
        }
        return Detection(validateDir(env.paths.game(gameId)).filesOk, found)
    }

    private fun findInstall(node: SourceNode, depth: Int): SourceNode? {
        if (!node.isDirectory || depth < 0) return null
        val children = runCatching { node.children() }.getOrDefault(emptyList())
        if (children.any { it.name.equals(EXE, true) } && children.any { it.name.equals("StarDat.mpq", true) }) return node
        return children.filter { it.isDirectory }.firstNotNullOfOrNull { findInstall(it, depth - 1) }
    }

    /** A disc image's volume name (STARCRAFT, BROODWAR...), or null. */
    private fun discLabel(file: File): String? = runCatching {
        java.io.RandomAccessFile(file, "r").use { f ->
            val pvd = ByteArray(80)
            f.seek(16 * 2048L)
            f.readFully(pvd)
            if (String(pvd, 1, 5, Charsets.US_ASCII) != "CD001") null else String(pvd, 40, 32, Charsets.US_ASCII).trim().uppercase()
        }
    }.getOrNull()

    private fun installed(env: ImportEnv) = validateDir(env.paths.game(gameId)).filesOk

    override fun resolveSources(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<AutoSource> {
        if (supplied["install"] is Supplied.Picked || detection.found["install"] != null || installed(env)) return emptyList()
        if (env.legacy == null || !env.online()) return emptyList()
        return listOf(AutoSource("blizzard", "StarCraft + Brood War 1.15.2 from Blizzard's servers", SIZE))
    }

    override fun downloadAvailableFiles(env: ImportEnv, sources: List<AutoSource>) {
        if (sources.none { it.id == "blizzard" }) return
        val legacy = env.legacy ?: return
        val staging = env.paths.staging(gameId)
        FileValidator.requireSpace(env.paths.downloads, SIZE * 2)
        staging.deleteTree()
        staging.mkdirs()
        try {
            // StarCraft's install script stores a key and owner in StarDat.mpq (font\font.gid, font.clh), and the game
            // reports "File not found" when they're missing. The game runs offline, so a placeholder key does.
            val keys = LegacyDownloader.Keys(
                classic = env.keys?.classic ?: "00000000000000000000000000",
                expansion = null,
                owner = env.keys?.owner ?: "Player",
            )
            legacy.install("STAR", staging, noBase = false, keys = keys, cancel = env.cancel, onProgress = env.progress)
            File(staging, MARK).writeText("STAR\n")
        } catch (e: Throwable) {
            staging.deleteTree()
            throw e
        }
    }

    override fun getMissingInputs(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<MissingInput> {
        val staging = env.paths.staging(gameId)
        val downloaded = File(staging, MARK).exists()
        val game = env.paths.game(gameId)
        val haveInstall = downloaded || FileValidator.find(game, EXE) != null || detection.found["install"] != null || supplied["install"] is Supplied.Picked
        if (!haveInstall) return listOf(MissingInput("install", PROMPT_INSTALL, PickKind.FILE_OR_FOLDER))
        if (downloaded) return emptyList()
        val missing = ArrayList<MissingInput>()
        val install = (supplied["install"] as? Supplied.Picked)?.source ?: detection.found["install"]
        fun has(name: String) = FileValidator.find(game, name)?.let { Mpq.containsArchive(it) } == true ||
            (install?.isDirectory == true && install.child(name) != null)
        if (!has(SC_DISC) && detection.found["scdisc"] == null && supplied["scdisc"] !is Supplied.Picked) missing += MissingInput("scdisc", PROMPT_SC_DISC, PickKind.FILE)
        if (!has(BW_DISC) && detection.found["bwdisc"] == null && supplied["bwdisc"] !is Supplied.Picked) missing += MissingInput("bwdisc", PROMPT_BW_DISC, PickKind.FILE)
        return missing
    }

    override fun importFiles(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>) {
        val asm = Assembler(env.paths, gameId)
        val scratch = File(env.paths.staging, "$gameId-scratch")
        try {
            val staging = asm.staging
            val downloaded = File(staging, MARK).exists()
            if (!downloaded) {
                asm.begin()
                asm.reuse(env.paths.game(gameId).list()?.filter { n -> USER_DATA.none { n.equals(it.substringBefore('/'), true) } } ?: emptyList()) { f ->
                    !f.name.endsWith(".mpq", true) || Mpq.containsArchive(f)
                }
                val install = (supplied["install"] as? Supplied.Picked)?.source ?: detection.found["install"]
                if (install != null) {
                    FileValidator.requireSpace(staging, SIZE)
                    copyInstall(install, staging, scratch, env)
                }
                discArchive(staging, SC_DISC, (supplied["scdisc"] as? Supplied.Picked)?.source ?: detection.found["scdisc"], scratch, env)
                discArchive(staging, BW_DISC, (supplied["bwdisc"] as? Supplied.Picked)?.source ?: detection.found["bwdisc"], scratch, env)
            }
            File(staging, MARK).delete()
            keepUserData(env.paths.game(gameId), staging)
            env.progress(Progress(Stage.VALIDATING, "Checking StarCraft"))
            val check = validateDir(staging)
            if (!check.filesOk) throw ImportException(check.problem ?: Problem.MISSING_SOURCE_DATA, check.message ?: "StarCraft's files didn't check out.")
            asm.commit()
        } catch (e: Throwable) {
            asm.abandon()
            throw e
        } finally {
            scratch.deleteTree()
        }
    }

    /** The current installation's characters, saved games and replays, moved into the new one; nothing of theirs overwritten. */
    private fun keepUserData(game: File, staging: File) {
        for (path in USER_DATA) {
            val from = File(game, path)
            if (!from.isDirectory) continue
            from.walkTopDown().filter { it.isFile }.forEach { f ->
                val target = File(File(staging, path), f.relativeTo(from).path)
                if (target.exists()) target.delete()
                target.parentFile?.mkdirs()
                if (!f.renameTo(target)) f.copyTo(target, true)
            }
        }
    }

    private fun copyInstall(source: SourceNode, staging: File, scratch: File, env: ImportEnv) {
        val lower = source.name.lowercase()
        when {
            source.isDirectory -> {
                val root = findInstall(source, 4)
                if (root == null) {
                    // A folder with only a disc's files, or Blizzard's installer payload.
                    if (source.walk(2).any { it.name.startsWith("Installer Tome", true) }) {
                        throw ImportException(Problem.UNSUPPORTED_INSTALLER, "That's Blizzard's legacy installer payload, which needs Blizzard's servers to install from. Retry online to have the app download and install StarCraft, or select an installed StarCraft folder.")
                    }
                    throw ImportException(Problem.MISSING_SOURCE_DATA, "There's no StarCraft installation in that folder (no StarCraft.exe with StarDat.mpq). $PROMPT_INSTALL")
                }
                copyTree(root, staging, env)
            }
            lower.endsWith(".iso") -> {
                // A disc image alone: its archive, but no installed game to go with it.
                throw ImportException(Problem.MISSING_SOURCE_DATA, "A disc image holds StarCraft's data archive, not the installed game. Retry online to download StarCraft from Blizzard, or select an installed StarCraft folder; the disc image can then supply its archive.")
            }
            lower.endsWith(".zip") -> {
                val out = File(scratch, "zip")
                source.open().use { ZipExtractor.extract(it, out, env.cancel) }
                val exe = out.walkTopDown().firstOrNull { it.isFile && it.name.equals(EXE, true) }
                    ?: throw ImportException(Problem.MISSING_SOURCE_DATA, "That zip has no StarCraft installation in it.")
                copyTree(FileNode(exe.parentFile!!), staging, env)
            }
            else -> throw ImportException(Problem.UNSUPPORTED_INSTALLER, "${source.name} isn't something this importer reads. $PROMPT_INSTALL")
        }
    }

    private fun copyTree(root: SourceNode, staging: File, env: ImportEnv) {
        val total = root.walk(4).sumOf { it.size }
        var done = 0L
        fun walk(node: SourceNode, into: File, depth: Int) {
            for (child in node.children()) {
                env.cancel.check()
                if (child.isDirectory) {
                    if (depth < 4) walk(child, File(into, child.name), depth + 1)
                } else {
                    copyInto(child, into, child.name, env.cancel) { n ->
                        done += n
                        env.progress(Progress(Stage.EXTRACTING, "Copying StarCraft", done, total))
                    }
                }
            }
        }
        walk(root, staging, 0)
    }

    /** StarCraft.mpq or BroodWar.mpq from [source]: the archive itself, a disc's INSTALL.EXE, or its disc image. */
    private fun discArchive(staging: File, name: String, source: SourceNode?, scratch: File, env: ImportEnv) {
        if (FileValidator.find(staging, name)?.let { Mpq.containsArchive(it) } == true) return
        source ?: return
        env.progress(Progress(Stage.EXTRACTING, "Making $name from ${source.name}"))
        val target = File(staging, name)
        val lower = source.name.lowercase()
        when {
            lower.endsWith(".iso") -> {
                val iso = Iso9660(localCopy(source, File(scratch, "iso"), env.cancel))
                val entry = iso.find("INSTALL.EXE") ?: throw ImportException(Problem.UNSUPPORTED_INSTALLER, "${source.name} has no INSTALL.EXE: it isn't a StarCraft or Brood War disc.")
                iso.open(entry).use { copyStream(it, target, env.cancel) }
            }
            source.isDirectory -> {
                val exe = source.child("INSTALL.EXE") ?: source.child(name)
                    ?: throw ImportException(Problem.MISSING_SOURCE_DATA, "That folder has neither INSTALL.EXE nor $name.")
                copyInto(exe, staging, name, env.cancel)
            }
            else -> copyInto(source, staging, name, env.cancel)
        }
        if (!Mpq.containsArchive(target)) {
            target.delete()
            throw ImportException(Problem.CORRUPT_ARCHIVE, "${source.name} doesn't hold a StarCraft data archive.")
        }
    }

    override fun validate(env: ImportEnv): Validation = validateDir(env.paths.game(gameId))

    fun validateDir(dir: File): Validation {
        val (program, pe) = programChecks(dir, EXE)
        val checks = program.toMutableList()
        val versionOk = supported(pe?.version)
        checks += Check("Version 1.15.2–1.16.1 (classic)", versionOk, pe?.version ?: "unknown")
        checks += FileValidator.requireFiles(dir, REQUIRED)
        checks += FileValidator.requireArchives(dir, ARCHIVES)
        // The archives hold the files the game opens first, not just a header.
        for ((archive, names) in CONTENTS) {
            val f = FileValidator.find(dir, archive)?.takeIf { Mpq.isArchive(it) } ?: continue
            val has = MpqContents.has(f, names)
            val missing = has?.filterValues { !it }?.keys.orEmpty()
            checks += Check("$archive holds ${names.first()}…", has != null && missing.isEmpty(), when {
                has == null -> "can't be read: damaged, or cut short"
                missing.isNotEmpty() -> "doesn't hold ${missing.joinToString()}: damaged, or not StarCraft's"
                else -> "present"
            })
        }
        for (disc in listOf(SC_DISC, BW_DISC)) {
            val f = FileValidator.find(dir, disc)
            checks += Check(disc, f != null && Mpq.containsArchive(f), if (f == null) "missing" else "${f.length()} bytes")
        }
        val failed = checks.filter { !it.passed }
        val problem = when {
            !checks[0].passed -> Problem.MISSING_SOURCE_DATA
            pe != null && !versionOk -> Problem.UNSUPPORTED_VERSION
            failed.any { it.name.contains(" holds ") } -> Problem.CORRUPT_ARCHIVE
            failed.any { it.name == "BrooDat.mpq" } -> Problem.MISSING_EXPANSION
            failed.any { it.name == SC_DISC || it.name == BW_DISC } -> Problem.MISSING_SOURCE_DATA
            failed.isNotEmpty() -> Problem.MISSING_RUNTIME_DEPENDENCY
            else -> null
        }
        val message = when (problem) {
            Problem.UNSUPPORTED_VERSION -> "This StarCraft is version ${pe?.version}; the app plays the classic 1.15.2 to 1.16.1, never Remastered. Select a classic installation, or retry online to download it from Blizzard."
            Problem.CORRUPT_ARCHIVE -> failed.filter { it.name.contains(" holds ") }.joinToString("; ") { "${it.name.substringBefore(" holds ")} ${it.detail}" } + ". Reset the installation and import it again."
            Problem.MISSING_EXPANSION -> "Brood War isn't installed in that folder (no BrooDat.mpq). Select an installation with Brood War, or retry online to download it from Blizzard."
            Problem.MISSING_SOURCE_DATA -> if (failed.any { it.name == BW_DISC }) PROMPT_BW_DISC else if (failed.any { it.name == SC_DISC }) PROMPT_SC_DISC else PROMPT_INSTALL
            Problem.MISSING_RUNTIME_DEPENDENCY -> "StarCraft's files are incomplete: ${failed.joinToString { it.name }}."
            else -> null
        }
        return Validation(checks, pe?.version?.let { "StarCraft + Brood War $it" }, problem == null, problem, message)
    }

    override fun registerLaunchEntry(env: ImportEnv, validation: Validation) = LibraryEntry(
        gameId = gameId,
        title = "StarCraft + Brood War",
        products = listOf("STAR", "SEXP"),
        clientVersion = validation.clientVersion ?: "",
        installPath = env.paths.game(gameId).path,
        executable = EXE,
        runtime = LibraryEntry.RUNTIME_WINLATOR,
        arguments = "",
        stage = Stage.READY,
        saveLocation = env.paths.game(gameId).path + "/save",
        controlProfile = "starcraft",
    )
}
