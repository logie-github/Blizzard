package com.logie.blizz.importer

import android.content.Context
import java.io.File

/** The two Stratagus game packages: the scripts zip in the APK and the data tool that converts the GOG files. */
enum class WargusGame(val key: String, val toolLibrary: String, val scriptsAsset: String) {
    /** Warcraft: Orcs & Humans, War1gus. */
    WAR1("war1gus", "libwar1tool.so", "stratagus/war1gus.zip"),

    /** Warcraft II: Battle.net Edition, Wargus. */
    WAR2("wargus", "libwartool.so", "stratagus/wargus.zip"),
}

/**
 * Runs a game's data tool. The process-running part of the conversion is behind this so the unit
 * tests can use a fake one that writes the `extracted` marker.
 */
interface ConversionTools {
    /**
     * Puts the game package's scripts into [staging] and runs the tool with [source] (the GOG game's
     * folder) and [staging], its output line by line to [onLine]. Returns the tool's exit code and
     * last lines; throws [ImportException] where the tools themselves are missing.
     */
    fun convert(game: WargusGame, source: File, staging: File, cancel: CancelToken, onLine: (String) -> Unit): Tools.Result

    companion object {
        /** Set once by the app (or the orchestrator) for importers made without tools of their own. */
        @Volatile
        var installed: ConversionTools? = null
    }
}

/**
 * The tools on the phone: war1tool and wartool ship as lib*.so in the app's native library folder
 * (which Android lets the app run), the scripts zips as assets of the APK (`stratagus/war1gus.zip`,
 * `stratagus/wargus.zip`), unpacked beside the data. The tools run with HOME set to the staging folder.
 */
class DeviceConversionTools(private val context: Context) : ConversionTools {
    override fun convert(game: WargusGame, source: File, staging: File, cancel: CancelToken, onLine: (String) -> Unit): Tools.Result {
        val tool = Tools.file(context, game.toolLibrary)
        if (!tool.canExecute()) {
            throw ImportException(Problem.MISSING_RUNTIME_DEPENDENCY, "The data tool for ${game.key} (${game.toolLibrary}) is missing from this build of the app.")
        }
        val scripts = try {
            context.assets.open(game.scriptsAsset)
        } catch (e: java.io.IOException) {
            throw ImportException(Problem.MISSING_RUNTIME_DEPENDENCY, "The game package for ${game.key} (${game.scriptsAsset}) is missing from this build of the app.", e.toString(), e)
        }
        scripts.use { ZipExtractor.extract(it, staging, cancel) }
        return Tools.run(listOf(tool.path, source.path, staging.path), staging, cancel, mapOf("HOME" to staging.path), onLine)
    }
}

/** Runs the conversion exactly as the Warcraft app does: tool on the game folder into a staging folder, which holds `extracted` when done. */
object WargusConversion {
    const val MARKER = "extracted"

    /** Converts [source] into [staging] (emptied first by the caller); a failure carries the tool's last lines as its detail. */
    fun run(tools: ConversionTools, game: WargusGame, source: File, staging: File, what: String, cancel: CancelToken, progress: (Progress) -> Unit) {
        progress(Progress(Stage.ASSEMBLING, "Converting $what for the game engine"))
        val log = File(staging.parentFile, "${staging.name}-conversion.log")
        val lines = ArrayList<String>()
        val result = try {
            tools.convert(game, source, staging, cancel) { line ->
                progress(Progress(Stage.ASSEMBLING, line.trim().ifEmpty { "Converting $what" }.take(120)))
                lines += line
                if (lines.size > 400) lines.removeAt(0)
            }
        } finally {
            runCatching { log.delete() }
        }
        if (result.code != 0 || !File(staging, MARKER).isFile) {
            val tail = (result.tail.ifEmpty { lines.takeLast(12) }).joinToString("\n")
            throw ImportException(
                Problem.CORRUPT_ARCHIVE,
                "$what couldn't be converted for the game engine (the tool ended with code ${result.code}). Check that the files are the complete GOG game, then import again.",
                tail,
            )
        }
    }
}

/** Renames files and folders to the exact case the data tools open them by (Android's storage is case-sensitive; innoextract lower-cases). */
object CaseFix {
    /** [relative] ("Support/TOMES/TOME.1") in [root], each part found whatever its case and renamed to the one given. */
    fun apply(root: File, relative: String) {
        var dir = root
        for (part in relative.split('/')) {
            val exact = File(dir, part)
            if (!exact.exists()) {
                val found = dir.listFiles()?.firstOrNull { it.name.equals(part, ignoreCase = true) } ?: return
                if (!found.renameTo(exact)) return
            }
            dir = exact
        }
    }

    /** [relative] in [root] whatever its case, or null. */
    fun find(root: File, relative: String): File? {
        var dir = root
        for (part in relative.split('/')) {
            dir = File(dir, part).takeIf { it.exists() } ?: dir.listFiles()?.firstOrNull { it.name.equals(part, ignoreCase = true) } ?: return null
        }
        return dir
    }

    fun find(root: SourceNode, relative: String): SourceNode? {
        var node = root
        for (part in relative.split('/')) node = node.child(part) ?: return null
        return node
    }
}

/**
 * What Warcraft and Warcraft II share: the person's GOG files (the installed game's folder, a zip or
 * other archive, or the offline installer with its .bin parts) are brought to a game folder
 * ([Packages.materialize]), the case of the names the tools open is made right, then the game's tool
 * converts them into the data Stratagus plays from: the game's staging folder, committed whole to
 * `games/<id>`. The library entry is the Stratagus runtime's: `executable` is the `extracted` marker.
 *
 * Stratagus keeps a game's preferences and saves in `<game folder>/<war1gus|wargus>` (it is started with
 * that folder as its user directory), so that folder is [keptInGame]: a reset leaves it, and an import
 * over an installed game carries it across. Nothing here can prove the game plays: it ends as
 * Imported, Launch Untested.
 */
abstract class WargusImporter(conversion: ConversionTools?) : GameImporter {
    private val given = conversion

    protected abstract val game: WargusGame
    protected abstract val what: String
    protected abstract val products: List<String>
    protected abstract val prompt: String
    /** Whether a folder's entries (lower-case, folders ending in "/") are this game's folder. */
    protected abstract fun isRoot(names: Set<String>): Boolean
    /** The files that must be in the GOG game's folder, relative with "/", matched whatever their case. */
    protected abstract val required: List<String>
    /** A game folder found by its files wherever they landed in what was unpacked. */
    abstract fun looseRoot(dir: File): File?
    /** Gives the files the case the tool opens them by. */
    protected abstract fun fixCase(root: File)
    /** A setup program's name that belongs to this game, to find the installer among files. */
    protected abstract val installerName: Regex

    override val keptInGame: List<String> get() = listOf(game.key)

    private fun tools(): ConversionTools = given ?: ConversionTools.installed
        ?: throw ImportException(Problem.MISSING_RUNTIME_DEPENDENCY, "The conversion tools aren't available in this build of the app.")

    override fun detect(env: ImportEnv): Detection {
        env.progress(Progress(Stage.DETECTING, "Looking for $what"))
        val found = LinkedHashMap<String, SourceNode>()
        val roots = env.searchRoots()
        roots.firstNotNullOfOrNull { Packages.findRoot(it, 4, ::isRoot) }?.let { found["install"] = it }
        if (found["install"] == null) {
            Scan(roots, 5).files.firstOrNull { it.name.endsWith(".exe", true) && installerName.containsMatchIn(it.name) }?.let { found["install"] = it }
        }
        return Detection(validateDir(env.paths.game(gameId)).filesOk, found)
    }

    override fun resolveSources(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<AutoSource> = emptyList()

    override fun downloadAvailableFiles(env: ImportEnv, sources: List<AutoSource>) = Unit

    override fun getMissingInputs(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<MissingInput> {
        // The converted data can't be made again without the GOG files, so they're asked for even when it is installed.
        val install = (supplied["install"] as? Supplied.Picked)?.source ?: detection.found["install"]
        return if (install == null) listOf(MissingInput("install", prompt, PickKind.FILE_OR_FOLDER)) else emptyList()
    }

    override fun importFiles(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>) {
        val install = (supplied["install"] as? Supplied.Picked)?.source ?: detection.found["install"]
            ?: throw ImportException(Problem.MISSING_SOURCE_DATA, prompt)
        val tools = tools()
        val asm = Assembler(env.paths, gameId)
        val scratch = File(env.paths.staging, "$gameId-scratch")
        try {
            val staging = asm.begin()
            refuseFolderWithoutGameOrInstaller(install)
            val root = Packages.materialize(
                install, env, staging, scratch, what, prompt, ::isRoot,
                checkFound = { node -> refuse(required.filter { CaseFix.find(node, it) == null }) },
                checkUnpacked = { dir -> refuse(required.filter { CaseFix.find(dir, it) == null }) },
                looseRoot = ::looseRoot,
            )
            refuse(required.filter { CaseFix.find(root, it) == null })
            fixCase(root)
            env.cancel.check()
            WargusConversion.run(tools, game, root, staging, what, env.cancel, env.progress)
            scratch.deleteRecursively()
            env.progress(Progress(Stage.VALIDATING, "Checking $what"))
            val check = validateDir(staging)
            if (!check.filesOk) throw ImportException(check.problem ?: Problem.MISSING_SOURCE_DATA, check.message ?: "$what's converted data didn't check out.")
            keepUserData(File(env.paths.game(gameId), game.key), File(staging, game.key))
            asm.commit()
        } catch (e: Throwable) {
            asm.abandon()
            throw e
        } finally {
            scratch.deleteRecursively()
        }
    }

    /** A folder with neither this game nor an installer in it: said here, not left to the installer search (which takes any lone program for one). */
    private fun refuseFolderWithoutGameOrInstaller(install: SourceNode) {
        if (!install.isDirectory || Packages.findRoot(install, 6, ::isRoot) != null) return
        val holders = listOf(install) + install.children().filter { it.isDirectory }
        val hasSetup = holders.any { h -> h.children().any { !it.isDirectory && it.name.startsWith("setup", true) && it.name.endsWith(".exe", true) } }
        if (!hasSetup) throw ImportException(Problem.MISSING_SOURCE_DATA, "There's no $what in that folder (and no installer). $prompt")
    }

    private fun refuse(missing: List<String>) {
        if (missing.isNotEmpty()) {
            throw ImportException(Problem.MISSING_SOURCE_DATA, "That doesn't hold the complete $what (missing ${missing.joinToString()}). $prompt")
        }
    }

    /** The preferences and saves of the installed game moved into the new one; nothing of the new one's overwritten. */
    private fun keepUserData(from: File, to: File) {
        if (!from.isDirectory) return
        for (f in from.walkTopDown().filter { it.isFile }) {
            val target = File(to, f.relativeTo(from).path)
            if (target.exists()) continue
            target.parentFile?.mkdirs()
            if (!f.renameTo(target)) f.copyTo(target, overwrite = false)
        }
    }

    override fun validate(env: ImportEnv): Validation = validateDir(env.paths.game(gameId))

    fun validateDir(dir: File): Validation {
        val marker = File(dir, WargusConversion.MARKER)
        val others = dir.listFiles().orEmpty().filter { it.name != WargusConversion.MARKER && !it.name.endsWith(".txt") && !it.name.endsWith(".log") }
        val checks = listOf(
            Check("Converted $what (${WargusConversion.MARKER})", marker.isFile, if (marker.isFile) "present" else "missing"),
            Check("Game scripts and data", others.any { it.isDirectory && it.walkTopDown().any { f -> f.isFile } }, if (others.isEmpty()) "missing" else "${others.size} entries"),
        )
        val ok = checks.all { it.passed }
        return Validation(
            checks, if (ok) "$what (GOG, Stratagus)" else null, ok,
            if (ok) null else Problem.MISSING_SOURCE_DATA, if (ok) null else prompt,
        )
    }

    override fun readyStage(validation: Validation) = Stage.IMPORTED_UNTESTED

    override fun registerLaunchEntry(env: ImportEnv, validation: Validation) = LibraryEntry(
        gameId = gameId,
        title = title,
        products = products,
        clientVersion = validation.clientVersion ?: "",
        installPath = env.paths.game(gameId).path,
        executable = WargusConversion.MARKER,
        runtime = "stratagus",
        arguments = "",
        stage = Stage.IMPORTED_UNTESTED,
        saveLocation = env.paths.game(gameId).path + "/" + game.key,
        controlProfile = gameId,
    )
}
