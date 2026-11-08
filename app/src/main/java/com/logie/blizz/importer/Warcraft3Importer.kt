package com.logie.blizz.importer

import com.logie.blizz.game.Wc3Arguments
import java.io.File

/**
 * Warcraft III, Reign of Chaos ("warcraft3_roc") and The Frozen Throne ("warcraft3_tft"), the
 * original pre-Reforged game (1.0x to 1.30; 1.30.4 is the one Mashiro's repack carries), played on
 * Winlator offline. One class, a [Product] each.
 *
 * Source: the person's own files in any form ([Packages.materialize]: an installed folder, zip, 7z,
 * tar.*, disc image, or an installer with its data files), or, where Blizzard's legacy downloader
 * lists the product (its usage names WAR3 and W3XP), Blizzard's own servers. Nothing else is
 * downloaded; no Battle.net account is asked for. Maps and CD keys are optional (single player and
 * LAN need no key; the Wc3Keys box keeps the ones the person has).
 *
 * The two products share ONE install: Warcraft III 1.30 is one program and one CASC store, and 1.2x
 * has the base game's war3.mpq beside the expansion's war3x.mpq, so a full install plays both.
 * Whichever product the person imports first owns the folder `games/<its id>`. The other product's
 * [detect] finds that folder ([installDir]), imports nothing, and [registerLaunchEntry] points its
 * library entry at the same folder with its own start program. Nothing is copied. If the first
 * import held only the base game (a Reign of Chaos-only 1.2x install), it isn't valid for the
 * expansion, and importing The Frozen Throne asks for its files and keeps them in its own folder.
 * Resetting the owner takes the shared folder away from the other product.
 *
 * Files can't show that the game starts under Winlator: an import ends as Imported, Launch Untested.
 */
class Warcraft3Importer(private val product: Product) : GameImporter {
    enum class Product(
        val id: String,
        val title: String,
        val codes: List<String>,
        /** True for The Frozen Throne: needs its expansion data too. */
        val expansion: Boolean,
        /** The programs that start it, best first. */
        val programs: List<String>,
    ) {
        ROC("warcraft3_roc", "Warcraft III: Reign of Chaos", listOf("WAR3"), false, listOf("Warcraft III.exe", "war3.exe", "Frozen Throne.exe")),
        TFT("warcraft3_tft", "Warcraft III: The Frozen Throne", listOf("WAR3", "W3XP"), true, listOf("Frozen Throne.exe", "Warcraft III.exe", "war3.exe"));

        /** The product that shares this one's install. */
        val sibling: Product get() = if (this == ROC) TFT else ROC
    }

    override val gameId = product.id
    override val title = product.title
    /** Saved games kept beside the game (1.2x keeps them in the game folder) survive a reset. */
    override val keptInGame = listOf("Save")

    companion object {
        const val ROC_ID = "warcraft3_roc"
        const val TFT_ID = "warcraft3_tft"
        /** Programs found, in the order their version is read. */
        val PROGRAMS = listOf("Warcraft III.exe", "war3.exe", "Frozen Throne.exe")
        /**
         * Where the version is read, best first. In 1.2x, war3.exe is the game (1.27.0.52240) and "Warcraft III.exe" and
         * "Frozen Throne.exe" are small launchers with their own version resources (1.0.0.1 and 1.5.0.0 as Blizzard serves
         * them); 1.30 has only "Warcraft III.exe", which is the game.
         */
        val VERSION_ORDER = listOf("war3.exe", "Warcraft III.exe", "Frozen Throne.exe")
        /** The 1.2x game's own libraries, checked besides the launcher's: war3.exe and Game.dll import Storm, Miles (mss32), the C++ runtime and ijl15. */
        val GAME_BINARIES = listOf("war3.exe", "Game.dll")
        const val MARK = ".from-blizzard"
        /** Inside the games' Windows: where 1.28 and later keep saved games and replays. */
        const val DOCUMENTS = "C:\\users\\xuser\\Documents\\Warcraft III"
        /** Blizzard's 1.27a2 downloads, Reign of Chaos (759 MB) and The Frozen Throne (596 MB): both come with either product, so one tap gives both campaigns. */
        private const val SIZE_BOTH = 1_360L shl 20
        /** What the download fetches, in order. */
        val DOWNLOAD_CODES = listOf("WAR3", "W3XP")
        const val PROMPT_INSTALL = "Select your Warcraft III installation: its folder, a zip, 7z, tar or disc image of it, or its installer (Setup.exe, with its data files in the same folder). 1.30 and 1.2x both work."
        const val PROMPT_EXPANSION = "The Frozen Throne's data is missing (war3x.mpq, or 1.30's Data folder). Select your Warcraft III folder with The Frozen Throne installed."
        const val PROMPT_VERSION = "This is not a Warcraft III version this app plays (1.0 to 1.31, the original game; 1.30 is the one tried). Reforged (1.32 and later) is not supported. Select an older installation."

        private val VERSION = Regex("""^1\.(\d{1,2})\.""")

        /** The original game's versions: 1.00 to 1.31 (1.32 is Reforged). */
        fun supported(version: String?): Boolean {
            val minor = VERSION.find(version ?: return false)?.groupValues?.get(1)?.toIntOrNull() ?: return false
            return minor in 0..31
        }

        /** A folder with a Warcraft III program and its data (names lower-case, folders end in "/"). */
        fun isGameRoot(names: Set<String>): Boolean =
            PROGRAMS.any { it.lowercase() in names } &&
                (names.any { it == "data/" || it == ".build.info" || it == "war3.mpq" || it == "war3x.mpq" })

        /** Whether [dir] holds 1.30's CASC data (Data/data, Data/indices, Data/config and .build.info). */
        fun hasCasc(dir: File): Boolean = cascMissing(dir).isEmpty()

        /** Which parts of 1.30's data are missing, by name. */
        fun cascMissing(dir: File): List<String> {
            val data = FileValidator.find(dir, "Data")?.takeIf { it.isDirectory }
            val missing = ArrayList<String>()
            for (name in listOf("data", "indices", "config")) {
                val d = data?.let { FileValidator.find(it, name) }
                if (d == null || !d.isDirectory || d.list().isNullOrEmpty()) missing += "Data/$name"
            }
            if (FileValidator.find(dir, ".build.info")?.isFile != true) missing += ".build.info"
            return missing
        }

        /** The Reign of Chaos and Frozen Throne programs a person starts: [product]'s first one that is in [dir]. */
        fun programFor(dir: File, product: Product): File? =
            product.programs.firstNotNullOfOrNull { FileValidator.find(dir, it)?.takeIf { f -> f.isFile } }
    }

    // Where the install is ------------------------------------------------------------------------

    /**
     * The folder this product plays from: its own when that holds a valid install for it, else the
     * other product's if that does (the shared install), else its own (nothing yet).
     */
    fun installDir(paths: GamePaths, of: Product = product): File {
        val own = paths.game(of.id)
        if (validateDir(own, of).filesOk) return own
        val other = paths.game(of.sibling.id)
        if (other.isDirectory && validateDir(other, of).filesOk) return other
        return own
    }

    /** Whether the install this product plays from is the other product's folder. */
    fun isShared(paths: GamePaths): Boolean = installDir(paths) != paths.game(gameId)

    // Importer steps ------------------------------------------------------------------------------

    override fun detect(env: ImportEnv): Detection {
        env.progress(Progress(Stage.DETECTING, "Looking for Warcraft III"))
        val found = LinkedHashMap<String, SourceNode>()
        val roots = env.searchRoots()
        // A folder only counts when it is whole for this product: a half-copied 1.30 (a Data folder without config) or a base-only
        // folder for The Frozen Throne would stop the import with an error, where Blizzard's download gives a good one.
        roots.firstNotNullOfOrNull { Packages.findRoot(it, 4) { names -> isGameRoot(names) } }?.takeIf { usable(it) }?.let { found["install"] = it }
        if (found["install"] == null) {
            Scan(roots, 5).matching(Regex("(?i)(war3|warcraft.?(iii|3)|frozen.?throne|reign.?of.?chaos|w3).*\\.(zip|7z|iso|tar|tar\\.gz|tgz|tar\\.xz|tar\\.bz2|tar\\.zst)"))
                .firstOrNull()?.let { found["install"] = it }
        }
        val dir = installDir(env.paths)
        val notes = if (dir != env.paths.game(gameId)) listOf("Uses the install of ${product.sibling.title} (${dir.name}): nothing is copied.") else emptyList()
        return Detection(validateDir(dir, product).filesOk, found, notes)
    }

    /**
     * Whether a folder found on the phone can be imported as it is: whole for this product. A file (an archive, a disc image) can't be
     * looked into cheaply and is tried.
     */
    fun usable(node: SourceNode): Boolean {
        if (!node.isDirectory) return true
        val names = Packages.names(node.children())
        val mpq = "war3.mpq" in names && (!product.expansion || "war3x.mpq" in names)
        if (mpq) return true
        if (".build.info" !in names) return false
        val data = node.child("Data") ?: return false
        return listOf("data", "indices", "config").all { part -> data.child(part)?.children()?.isNotEmpty() == true }
    }

    override fun resolveSources(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<AutoSource> {
        if (supplied["install"] is Supplied.Picked || detection.found["install"] != null || detection.installed) return emptyList()
        if (programFor(env.paths.game(gameId), product) != null) return emptyList()
        if (env.legacy == null || !env.online()) return emptyList()
        return listOf(AutoSource("blizzard", "Warcraft III: Reign of Chaos and The Frozen Throne from Blizzard's servers", SIZE_BOTH))
    }

    override fun downloadAvailableFiles(env: ImportEnv, sources: List<AutoSource>) {
        if (sources.none { it.id == "blizzard" }) return
        val legacy = env.legacy ?: return
        val staging = env.paths.staging(gameId)
        FileValidator.requireSpace(env.paths.downloads, SIZE_BOTH * 2)
        staging.deleteTree()
        staging.mkdirs()
        try {
            // The base game, then the expansion over it, as Blizzard's installers do: both campaigns whichever tile was tapped.
            // No key: single player needs none, and none is passed to the tool.
            for (code in DOWNLOAD_CODES) legacy.install(code, staging, noBase = true, keys = null, cancel = env.cancel, onProgress = env.progress)
            File(staging, MARK).writeText(DOWNLOAD_CODES.joinToString(" ") + "\n")
        } catch (e: Throwable) {
            staging.deleteTree()
            throw e
        }
    }

    override fun getMissingInputs(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<MissingInput> {
        if (File(env.paths.staging(gameId), MARK).exists()) return emptyList()
        if (detection.installed || programFor(env.paths.game(gameId), product) != null) return emptyList()
        val install = (supplied["install"] as? Supplied.Picked)?.source ?: detection.found["install"]
        if (install != null) return emptyList()
        return listOf(MissingInput("install", if (product.expansion && isBaseOnly(env.paths)) PROMPT_EXPANSION else PROMPT_INSTALL, PickKind.FILE_OR_FOLDER))
    }

    /** The other product's folder holds the base game but not the expansion (so The Frozen Throne can't use it). */
    private fun isBaseOnly(paths: GamePaths): Boolean {
        val other = paths.game(product.sibling.id)
        return other.isDirectory && validateDir(other, Product.ROC).filesOk
    }

    override fun importFiles(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>) {
        val asm = Assembler(env.paths, gameId)
        val scratch = File(env.paths.staging, "$gameId-scratch")
        try {
            val picked = (supplied["install"] as? Supplied.Picked)?.source
            val downloaded = File(asm.staging, MARK).exists()
            if (!downloaded) {
                // Playing from the other product's install and no files given: nothing to do.
                if (picked == null && isShared(env.paths)) return
                val install = picked ?: detection.found["install"]
                var root: File? = null
                if (install != null) {
                    root = Packages.materialize(install, env, asm.staging, scratch, "Warcraft III", PROMPT_INSTALL, ::isGameRoot, ::precheck, ::precheckVersion, looseRoot = ::looseGameRoot)
                    // Before anything of the installed game is touched.
                    val check = validateDir(root, product)
                    if (!check.filesOk) throw ImportException(check.problem ?: Problem.MISSING_SOURCE_DATA, check.message ?: "Warcraft III's files didn't check out.", check.checks.filter { !it.passed }.joinToString { "${it.name}: ${it.detail}" })
                }
                asm.begin()
                if (root != null) {
                    // Moved, not copied: it was just unpacked beside staging.
                    for (f in root.listFiles().orEmpty()) {
                        val target = File(asm.staging, f.name)
                        target.deleteTree()
                        if (!f.renameTo(target)) f.copyRecursively(target, true)
                    }
                }
                // What was there and isn't in the new files stays. With new files given, only the player's own folders (saves, maps, replays):
                // another version's program and archives would mix two installs (1.30 over 1.27 kept the old war3.exe). A repair with none given keeps it all.
                val current = env.paths.game(gameId).list()?.toList() ?: emptyList()
                asm.reuse(if (root != null) current.filter { n -> n.lowercase() in setOf("save", "maps", "replay", "replays") } else current) { true }
            }
            File(asm.staging, MARK).delete()
            env.progress(Progress(Stage.VALIDATING, "Checking Warcraft III"))
            val check = validateDir(asm.staging, product)
            if (!check.filesOk) throw ImportException(check.problem ?: Problem.MISSING_SOURCE_DATA, check.message ?: "Warcraft III's files didn't check out.")
            asm.commit()
        } catch (e: Throwable) {
            asm.abandon()
            throw e
        } finally {
            scratch.deleteTree()
        }
    }

    /** The game's folder wherever a program and its data landed, whatever the folders around them are called. */
    fun looseGameRoot(dir: File): File? =
        dir.walkTopDown().maxDepth(14).firstOrNull { d ->
            d.isDirectory && programFor(d, Product.ROC) != null &&
                (FileValidator.find(d, "Data")?.isDirectory == true || FileValidator.find(d, "war3.mpq") != null || FileValidator.find(d, ".build.info") != null)
        }

    /** Before copying gigabytes: the folder has the data this product needs, and a version this plays. */
    private fun precheck(root: SourceNode) {
        val names = Packages.names(root.children())
        val casc = ".build.info" in names && "data/" in names
        if (product.expansion && !casc && "war3x.mpq" !in names) throw ImportException(Problem.MISSING_EXPANSION, PROMPT_EXPANSION, "Files: ${names.sorted().take(40).joinToString()}")
        val program = product.programs.firstNotNullOfOrNull { root.child(it) }
        val local = program?.localFile()
        if (local != null) precheckProgram(local)
    }

    /** After unpacking: the program's version is one this plays. */
    private fun precheckVersion(root: File) {
        programFor(root, product)?.let { precheckProgram(it) }
    }

    private fun precheckProgram(program: File) {
        val version = versionOf(program.parentFile ?: return)
        if (version != null && !supported(version)) throw ImportException(Problem.UNSUPPORTED_VERSION, "This Warcraft III is version $version. $PROMPT_VERSION", "${program.name} $version")
    }

    // Validation ----------------------------------------------------------------------------------

    override fun validate(env: ImportEnv): Validation = validateDir(installDir(env.paths), product)

    /** The program version found in [dir]: the first readable of the programs, best first. */
    fun versionOf(dir: File): String? =
        VERSION_ORDER.firstNotNullOfOrNull { name -> FileValidator.find(dir, name)?.let { PeInfo.read(it)?.version } }

    fun validateDir(dir: File, product: Product = this.product): Validation {
        val checks = ArrayList<Check>()
        val program = programFor(dir, product) ?: PROGRAMS.firstNotNullOfOrNull { FileValidator.find(dir, it) }
        val pe = program?.let { PeInfo.read(it) }
        val version = versionOf(dir)
        val programOk = program != null && pe != null && pe.isWindowsX86Family
        checks += Check("Warcraft III program", programOk, when {
            program == null -> "missing"
            pe == null -> "${program.name} is not a Windows program"
            else -> "${program.name} ${version ?: "(version unknown)"}"
        })
        val versionOk = programOk && (version == null || supported(version))
        checks += Check("Supported version (1.0 to 1.31, the original game)", versionOk, version ?: "unknown")
        val missingLibs = if (programOk) (listOf(program!!) + GAME_BINARIES.mapNotNull { FileValidator.find(dir, it) }).flatMap { Dependencies.missing(it) }.distinct() else emptyList()
        checks += Check("Program libraries", programOk && missingLibs.isEmpty(), if (!programOk) "not checked" else if (missingLibs.isEmpty()) "all present" else "missing ${missingLibs.joinToString()}")

        // The data: 1.30's CASC store (it holds both games), or 1.2x's archives.
        val casc = hasCasc(dir)
        val partialCasc = !casc && FileValidator.find(dir, "Data")?.isDirectory == true && FileValidator.find(dir, ".build.info") != null
        val base = FileValidator.requireArchives(dir, listOf("war3.mpq")).single()
        val expansion = FileValidator.requireArchives(dir, listOf("war3x.mpq")).single()
        val baseOk = casc || base.passed
        val expansionOk = casc || expansion.passed
        checks += when {
            casc -> Check("Game data (Data folder)", true, "1.30 data present")
            partialCasc -> Check("Game data (Data folder)", false, "missing ${cascMissing(dir).joinToString()}")
            else -> Check("Game data (war3.mpq)", base.passed, base.detail)
        }
        if (product.expansion) {
            checks += if (casc) Check("The Frozen Throne data", true, "in the Data folder") else Check("The Frozen Throne data (war3x.mpq)", expansion.passed, expansion.detail)
        }
        // Optional items: shown, never required.
        val maps = FileValidator.find(dir, "Maps")?.takeIf { it.isDirectory }
        checks += Check("Maps (optional)", true, if (maps != null) "present" else "none: the game's own campaigns and maps are in its data")
        val keys = dir.listFiles().orEmpty().any { it.isFile && com.logie.blizz.game.Wc3CdKeys.isKeyFile(it.name) }
        checks += Check("CD keys file (optional)", true, if (keys) "found beside the program" else "none: single player needs no key")
        checks += Check("Started under Winlator", false, "not tested")

        val problem = when {
            !programOk -> Problem.MISSING_SOURCE_DATA
            !versionOk -> Problem.UNSUPPORTED_VERSION
            missingLibs.isNotEmpty() -> Problem.MISSING_RUNTIME_DEPENDENCY
            !baseOk -> if (base.detail.startsWith("not an MPQ") || partialCasc) Problem.CORRUPT_ARCHIVE else Problem.MISSING_SOURCE_DATA
            product.expansion && !expansionOk -> if (expansion.detail.startsWith("not an MPQ")) Problem.CORRUPT_ARCHIVE else Problem.MISSING_EXPANSION
            else -> null
        }
        val message = when (problem) {
            Problem.UNSUPPORTED_VERSION -> "This Warcraft III is version ${version ?: "unknown"}. $PROMPT_VERSION"
            Problem.MISSING_EXPANSION -> PROMPT_EXPANSION
            Problem.CORRUPT_ARCHIVE -> "Some of Warcraft III's data is damaged: ${checks.filter { !it.passed && it.name.startsWith("Game data") }.joinToString { it.detail }}. Repair to copy it again."
            Problem.MISSING_RUNTIME_DEPENDENCY -> "Warcraft III's libraries are missing: ${missingLibs.joinToString()}."
            Problem.MISSING_SOURCE_DATA -> "Warcraft III's program or game data is missing. $PROMPT_INSTALL"
            else -> null
        }
        val clientVersion = if (problem == null && version != null) "${product.title} $version" else null
        return Validation(checks, clientVersion, problem == null, problem, message)
    }

    override fun readyStage(validation: Validation) = Stage.IMPORTED_UNTESTED

    /** The other product when the one install plays it too: it is in the library without a second tap. */
    override fun companions(env: ImportEnv): List<LibraryEntry> {
        val dir = installDir(env.paths, product.sibling)
        val v = validateDir(dir, product.sibling)
        if (!v.filesOk) return emptyList()
        return listOf(entryFor(product.sibling, dir, v).copy(stage = Stage.IMPORTED_UNTESTED))
    }

    override fun registerLaunchEntry(env: ImportEnv, validation: Validation): LibraryEntry = entryFor(product, installDir(env.paths), validation)

    private fun entryFor(product: Product, dir: File, validation: Validation): LibraryEntry {
        return LibraryEntry(
            gameId = product.id,
            title = product.title,
            products = product.codes,
            clientVersion = validation.clientVersion ?: "",
            installPath = dir.path,
            executable = programFor(dir, product)?.name ?: product.programs.first(),
            runtime = LibraryEntry.RUNTIME_WINLATOR,
            // Fullscreen at the screen's size, in 1.30's and 1.31's words; the registry (Wc3Setup) gives the size.
            arguments = Wc3Arguments.of("", openGl = false),
            stage = Stage.IMPORTED_UNTESTED,
            saveLocation = DOCUMENTS,
            controlProfile = "warcraft3",
        )
    }
}
