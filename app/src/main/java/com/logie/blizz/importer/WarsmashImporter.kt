package com.logie.blizz.importer

import com.logie.blizz.warsmash.WarsmashRuntime
import java.io.File

/** Classic Warcraft data for the embedded Android engine; Windows installs remain separate. */
class WarsmashImporter : GameImporter {
    override val gameId = ID
    override val title = "Warcraft III: Warsmash"
    override val keptInGame = listOf("Save", "Maps", "Replay", "Replays")

    companion object {
        const val ID = "warcraft3_warsmash"
        const val PROMPT = "Select classic Warcraft III with war3.mpq and war3x.mpq (patches 1.22–1.29): an installed folder, or an archive of it. CASC-only and Reforged files are not supported in Warsmash mode."
        fun isRoot(names: Set<String>) = "war3.mpq" in names && "war3x.mpq" in names
        fun validateDir(dir: File): Validation {
            val checks = FileValidator.requireArchives(dir, listOf("war3.mpq", "war3x.mpq"))
            val version = Warcraft3Importer(Warcraft3Importer.Product.TFT).versionOf(dir)
            val minor = version?.split('.')?.getOrNull(1)?.toIntOrNull()
            val supported = minor == null || minor in 22..29
            val all = checks + Check("Classic MPQ version (1.22–1.29)", supported, version ?: "version unknown; MPQ data checked")
            val problem = when {
                !supported -> Problem.UNSUPPORTED_VERSION
                checks.any { !it.passed } -> Problem.MISSING_SOURCE_DATA
                else -> null
            }
            return Validation(all, version ?: "Classic MPQ data", problem == null, problem, if (problem != null) PROMPT else null)
        }
    }

    fun installDir(paths: GamePaths): File = listOf(ID, Warcraft3Importer.TFT_ID, Warcraft3Importer.ROC_ID)
        .map { paths.game(it) }.firstOrNull { validateDir(it).filesOk } ?: paths.game(ID)

    override fun detect(env: ImportEnv): Detection {
        val installed = validateDir(installDir(env.paths)).filesOk
        val found = if (installed) null else env.searchRoots().firstNotNullOfOrNull { Packages.findRoot(it, 4, ::isRoot) }
        return Detection(installed, found?.let { mapOf("install" to it) } ?: emptyMap())
    }

    override fun resolveSources(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<AutoSource> = emptyList()
    override fun downloadAvailableFiles(env: ImportEnv, sources: List<AutoSource>) = Unit
    override fun getMissingInputs(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<MissingInput> =
        if (detection.installed || detection.found["install"] != null || supplied["install"] is Supplied.Picked) emptyList()
        else listOf(MissingInput("install", PROMPT, PickKind.FILE_OR_FOLDER))

    override fun importFiles(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>) {
        val source = (supplied["install"] as? Supplied.Picked)?.source ?: detection.found["install"]
        if (source == null && validateDir(installDir(env.paths)).filesOk) return
        if (source == null) throw ImportException(Problem.MISSING_SOURCE_DATA, PROMPT)
        val asm = Assembler(env.paths, ID)
        val scratch = File(env.paths.staging, "$ID-scratch")
        try {
            val root = Packages.materialize(source, env, asm.staging, scratch, title, PROMPT, ::isRoot)
            val check = validateDir(root)
            if (!check.filesOk) throw ImportException(check.problem ?: Problem.MISSING_SOURCE_DATA, check.message ?: PROMPT)
            asm.begin()
            for (child in root.listFiles().orEmpty()) {
                env.cancel.check()
                val target = File(asm.staging, child.name)
                if (!child.renameTo(target)) child.copyRecursively(target, overwrite = true)
            }
            // Preserve saves and user maps during repair; never move another mode's installation.
            for (name in keptInGame) {
                FileValidator.find(asm.game, name)?.let { old ->
                    old.copyRecursively(File(asm.staging, name), overwrite = true)
                }
            }
            env.cancel.check()
            asm.commit()
        } catch (e: Throwable) {
            asm.abandon()
            throw e
        } finally {
            scratch.deleteTree()
        }
    }

    override fun validate(env: ImportEnv) = validateDir(installDir(env.paths))
    override fun readyStage(validation: Validation) = Stage.IMPORTED_UNTESTED
    override fun registerLaunchEntry(env: ImportEnv, validation: Validation): LibraryEntry {
        val dir = installDir(env.paths)
        return LibraryEntry(ID, title, listOf("WAR3", "W3XP"), validation.clientVersion.orEmpty(), dir.path,
            FileValidator.find(dir, "war3.mpq")!!.name, WarsmashRuntime.RUNTIME, "", Stage.IMPORTED_UNTESTED,
            File(dir, "Save").path, "warcraft3")
    }
}
