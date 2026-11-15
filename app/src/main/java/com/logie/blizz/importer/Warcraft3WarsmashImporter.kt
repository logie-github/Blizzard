package com.logie.blizz.importer

import com.logie.blizz.warsmash.WarsmashRuntime
import java.io.File

/**
 * Warcraft III's two games, Reign of Chaos and The Frozen Throne, played in the embedded Warsmash engine (the person chose it over
 * the Windows versions: "Replace the Windows ones"). The files come as they did ([Warcraft3Importer]: Blizzard's 1.27 download, or
 * the person's own install, one install for both games); what is checked is what Warsmash reads, the classic game's archives
 * (1.22 to 1.29: war3.mpq, and war3x.mpq for The Frozen Throne), and what goes in the library starts Warsmash in that game
 * ([WarsmashRuntime.Edition]). 1.30 and later keep their data in CASC, which Warsmash can't read: such an install is refused, and
 * Retry brings Blizzard's 1.27 in its place.
 */
class Warcraft3WarsmashImporter(private val product: Warcraft3Importer.Product) : GameImporter {
    private val windows = Warcraft3Importer(product)
    private val edition = editionOf(product)

    override val gameId = product.id
    override val title = product.title
    override val keptInGame = listOf("Save", "Replay", "Replays")
    /** The same files as the Windows importer's: its recipe, so the move to Warsmash installs nothing again. */
    override val recipe = windows.recipe

    companion object {
        /** The separate Warsmash mode's folder, from before both games moved to Warsmash: still played from when it holds the files. */
        const val LEGACY_ID = "warcraft3_warsmash"
        /** Blizzard's 1.27 downloads of both games ([Warcraft3Importer]'s). */
        private const val SIZE_BOTH = 1_360L shl 20
        const val PROMPT =
            "Select Warcraft III 1.22 to 1.29, the classic game (war3.mpq, and war3x.mpq for The Frozen Throne): its folder, a zip, 7z, " +
                "tar or disc image of it, or its installer. Warsmash can't read 1.30 and later."
        const val CASC =
            "This Warcraft III is 1.30 or later, whose data Warsmash can't read. Retry downloads 1.27 from Blizzard in its place " +
                "(about 1.4 GB; saved games stay), or pick a 1.22 to 1.29 install."

        fun editionOf(product: Warcraft3Importer.Product) =
            if (product == Warcraft3Importer.Product.ROC) WarsmashRuntime.Edition.ROC else WarsmashRuntime.Edition.TFT

        fun productOf(edition: WarsmashRuntime.Edition) =
            if (edition == WarsmashRuntime.Edition.ROC) Warcraft3Importer.Product.ROC else Warcraft3Importer.Product.TFT

        /** The archives Warsmash reads for [edition]: Reign of Chaos its own, The Frozen Throne the expansion's too. */
        fun archives(edition: WarsmashRuntime.Edition) =
            if (edition == WarsmashRuntime.Edition.ROC) listOf("war3.mpq") else listOf("war3.mpq", "war3x.mpq")

        /** A folder found on the phone (names lower-case) that holds what Warsmash reads for [edition]. */
        fun isRoot(names: Set<String>, edition: WarsmashRuntime.Edition) = archives(edition).all { it in names }

        /** What Warsmash needs of [dir] to play [edition]: its archives, of the classic game (1.22 to 1.29; an unknown version is let through). */
        fun validateDir(dir: File, edition: WarsmashRuntime.Edition): Validation {
            val product = productOf(edition)
            val archives = FileValidator.requireArchives(dir, archives(edition))
            val base = archives.first()
            val expansion = archives.getOrNull(1)
            val version = Warcraft3Importer(product).versionOf(dir)
            val minor = version?.let { Regex("""^1\.(\d{1,2})\.""").find(it)?.groupValues?.get(1)?.toIntOrNull() }
            val casc = !base.passed && Warcraft3Importer.hasCasc(dir)
            val classic = !casc && (version == null || minor in 22..29)
            val checks = ArrayList<Check>()
            checks += Check("Game data (war3.mpq)", base.passed, if (casc) "1.30's data folder instead (CASC)" else base.detail)
            if (expansion != null) checks += Check("The Frozen Throne data (war3x.mpq)", expansion.passed, expansion.detail)
            checks += Check("Classic game (1.22 to 1.29)", classic, when {
                casc -> "1.30 or later: Warsmash can't read its data"
                version != null -> version
                else -> "version unknown; the archives checked"
            })
            checks += Check("Played in Warsmash", false, "not tested")
            val problem = when {
                !classic -> Problem.UNSUPPORTED_VERSION
                !base.passed -> if (base.detail.startsWith("not an MPQ")) Problem.CORRUPT_ARCHIVE else Problem.MISSING_SOURCE_DATA
                expansion != null && !expansion.passed -> if (expansion.detail.startsWith("not an MPQ")) Problem.CORRUPT_ARCHIVE else Problem.MISSING_EXPANSION
                else -> null
            }
            val message = when (problem) {
                Problem.UNSUPPORTED_VERSION -> if (casc) CASC else "This Warcraft III is version $version. $PROMPT"
                Problem.CORRUPT_ARCHIVE -> "Some of Warcraft III's data is damaged (${archives.filter { !it.passed }.joinToString { it.name }}). Repair to copy it again."
                Problem.MISSING_EXPANSION -> "The Frozen Throne's data (war3x.mpq) is missing. $PROMPT"
                Problem.MISSING_SOURCE_DATA -> "Warcraft III's data (war3.mpq) is missing. $PROMPT"
                else -> null
            }
            val clientVersion = if (problem == null) "${product.title} ${version ?: ""}".trim() else null
            return Validation(checks, clientVersion, problem == null, problem, message)
        }

        /** The folder [edition] plays from: its own, else the other game's (one install for both), else the old Warsmash mode's; null when none holds it. */
        fun installDir(paths: GamePaths, edition: WarsmashRuntime.Edition): File? {
            val product = productOf(edition)
            return listOf(product.id, product.sibling.id, LEGACY_ID).map { paths.game(it) }
                .firstOrNull { it.isDirectory && validateDir(it, edition).filesOk }
        }

        /** The library's entry: Warsmash starts [product]'s game from [dir]. */
        fun entryFor(product: Warcraft3Importer.Product, dir: File, validation: Validation) = LibraryEntry(
            gameId = product.id,
            title = product.title,
            products = product.codes,
            clientVersion = validation.clientVersion.orEmpty(),
            installPath = dir.path,
            executable = FileValidator.find(dir, "war3.mpq")?.name ?: "war3.mpq",
            runtime = WarsmashRuntime.RUNTIME,
            arguments = "",
            stage = Stage.IMPORTED_UNTESTED,
            saveLocation = File(dir, "Save").path,
            controlProfile = "warcraft3",
        )

        /**
         * The library's Warcraft III entries made when both games played on Winlator start Warsmash now, from the same files: nothing is
         * installed again. One whose files Warsmash can't read (1.30's) leaves the library and says why, so Play opens Install & repair.
         */
        fun migrate(paths: GamePaths, library: Library, repo: ImportStateRepository) {
            for (product in Warcraft3Importer.Product.entries) {
                val entry = library.get(product.id) ?: continue
                if (entry.runtime == WarsmashRuntime.RUNTIME) continue
                val edition = editionOf(product)
                val dir = installDir(paths, edition)
                if (dir != null) {
                    library.put(entryFor(product, dir, validateDir(dir, edition)))
                } else {
                    val why = validateDir(File(entry.installPath), edition)
                    library.remove(product.id)
                    repo.update(product.id) {
                        it.copy(stage = Stage.FAILED, outcome = Outcome.UNSUPPORTED_CLIENT_VERSION, problem = why.problem ?: Problem.UNSUPPORTED_VERSION,
                            message = why.message ?: CASC, detail = null)
                    }
                }
            }
        }
    }

    // Importer steps: the files as the Windows importer gets them, checked as Warsmash reads them ------------------------------------

    override fun detect(env: ImportEnv): Detection {
        val dir = installDir(env.paths, edition)
        if (dir != null) {
            val notes = if (dir != env.paths.game(gameId)) listOf("Uses the files in ${dir.name}: nothing is copied.") else emptyList()
            return Detection(true, emptyMap(), notes)
        }
        val found = windows.detect(env).found.filterValues { node -> !node.isDirectory || readable(node) }
        return Detection(false, found)
    }

    /** A folder with the archives Warsmash reads for this game (an archive file can't be looked into cheaply: it is tried). */
    private fun readable(node: SourceNode): Boolean = isRoot(Packages.names(node.children()), edition)

    override fun resolveSources(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<AutoSource> {
        val picked = (supplied["install"] as? Supplied.Picked)?.source
        if (detection.installed || detection.found["install"] != null || (picked != null && (!picked.isDirectory || readable(picked)))) return emptyList()
        if (env.legacy == null || !env.online()) return emptyList()
        return listOf(AutoSource("blizzard", "Warcraft III: Reign of Chaos and The Frozen Throne from Blizzard's servers", SIZE_BOTH))
    }

    override fun downloadAvailableFiles(env: ImportEnv, sources: List<AutoSource>) = windows.downloadAvailableFiles(env, sources)

    override fun getMissingInputs(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<MissingInput> {
        if (File(env.paths.staging(gameId), Warcraft3Importer.MARK).exists() || detection.installed) return emptyList()
        if ((supplied["install"] as? Supplied.Picked)?.source != null || detection.found["install"] != null) return emptyList()
        return listOf(MissingInput("install", PROMPT, PickKind.FILE_OR_FOLDER))
    }

    override fun importFiles(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>) {
        // Blizzard's download (both games, 1.27) is put in place as the Windows importer always did.
        if (File(env.paths.staging(gameId), Warcraft3Importer.MARK).exists()) return windows.importFiles(env, detection, supplied)
        val given = (supplied["install"] as? Supplied.Picked)?.source ?: detection.found["install"]
        if (given == null) {
            // Playing from what is there (its own folder, the other game's or the old Warsmash mode's): nothing to copy.
            if (detection.installed) return
            throw ImportException(Problem.MISSING_SOURCE_DATA, PROMPT)
        }
        // The person's own files: what Warsmash reads is all that is checked (no Windows program or its libraries).
        val asm = Assembler(env.paths, gameId)
        val scratch = File(env.paths.staging, "$gameId-scratch")
        try {
            val root = Packages.materialize(given, env, asm.staging, scratch, "Warcraft III", PROMPT, { names -> isRoot(names, edition) })
            val check = validateDir(root, edition)
            if (!check.filesOk) throw ImportException(check.problem ?: Problem.MISSING_SOURCE_DATA, check.message ?: PROMPT)
            asm.begin()
            for (child in root.listFiles().orEmpty()) {
                env.cancel.check()
                val target = File(asm.staging, child.name)
                target.deleteTree()
                if (!child.renameTo(target)) child.copyRecursively(target, overwrite = true)
            }
            // The player's own folders of the install being replaced stay (saved games, maps, replays).
            val current = env.paths.game(gameId).list()?.toList() ?: emptyList()
            asm.reuse(current.filter { it.lowercase() in setOf("save", "maps", "replay", "replays") }) { true }
            env.cancel.check()
            asm.commit()
        } catch (e: Throwable) {
            asm.abandon()
            throw e
        } finally {
            scratch.deleteTree()
        }
    }

    override fun validate(env: ImportEnv) = validateDir(installDir(env.paths, edition) ?: env.paths.game(gameId), edition)

    override fun readyStage(validation: Validation) = Stage.IMPORTED_UNTESTED

    override fun registerLaunchEntry(env: ImportEnv, validation: Validation): LibraryEntry =
        entryFor(product, installDir(env.paths, edition) ?: env.paths.game(gameId), validation)

    /** The other game when the same files play it too (a Frozen Throne install holds Reign of Chaos's archive): in the library with it. */
    override fun companions(env: ImportEnv): List<LibraryEntry> {
        val other = product.sibling
        val dir = installDir(env.paths, editionOf(other)) ?: return emptyList()
        return listOf(entryFor(other, dir, validateDir(dir, editionOf(other))))
    }
}
