package com.logie.blizz.importer

import java.io.File

/**
 * What an importer works with: the app's folders, where to look for the person's files, the
 * network (or none), the programs it runs, and how to report progress and stop.
 */
class ImportEnv(
    val paths: GamePaths,
    /** Folders the person authorized (the picker's persisted folders) and the app's own import folder. */
    val searchRoots: () -> List<SourceNode>,
    val online: () -> Boolean,
    val downloads: DownloadManager,
    val releases: GitHubReleases,
    /** null in builds or tests without it. */
    val legacy: LegacyDownloader?,
    val innoextract: Innoextract?,
    val cancel: CancelToken,
    val progress: (Progress) -> Unit,
    /** The original CD keys the person chose to enter (Diablo II only), never logged. */
    val keys: LegacyDownloader.Keys? = null,
)

/** What [GameImporter.detect] found. */
data class Detection(
    /** A complete, valid installation in the app's own storage. */
    val installed: Boolean,
    /** Usable sources found, by the input they answer ("data", "hellfire", "install"...). */
    val found: Map<String, SourceNode>,
    val notes: List<String> = emptyList(),
)

/** A source of a file the import can get by itself (a download), with its size for the wizard. */
data class AutoSource(val id: String, val label: String, val size: Long)

/**
 * One game's importer: the same steps for each, in order. [detect] looks; [resolveSources] works out
 * what can be fetched automatically; [downloadAvailableFiles] fetches it; [getMissingInputs] asks
 * only for what's still missing; [importFiles] assembles the game in staging and swaps it in;
 * [validate] checks the result; [registerLaunchEntry] puts it in the library; [repair] does it
 * again keeping every file that's still good, and never the saves.
 */
interface GameImporter {
    val gameId: String
    val title: String

    /** Folders in the game's own folder that are the player's (saved games kept beside the game): a reset leaves them. */
    val keptInGame: List<String> get() = emptyList()

    fun detect(env: ImportEnv): Detection
    fun resolveSources(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<AutoSource>
    fun downloadAvailableFiles(env: ImportEnv, sources: List<AutoSource>)
    fun getMissingInputs(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>): List<MissingInput>
    fun importFiles(env: ImportEnv, detection: Detection, supplied: Map<String, Supplied>)
    fun validate(env: ImportEnv): Validation
    fun registerLaunchEntry(env: ImportEnv, validation: Validation): LibraryEntry
    /** Readiness once the files validated: READY, or IMPORTED_UNTESTED where files can't prove it plays. */
    fun readyStage(validation: Validation): Stage = Stage.READY

    /** Revalidates and imports again, reusing every good file and never touching the saves. */
    fun repair(env: ImportEnv, supplied: Map<String, Supplied>) {
        val detection = detect(env)
        importFiles(env, detection, supplied)
    }
}

/**
 * Builds a game folder in staging and swaps it in whole: the old installation is replaced only
 * after the new one is complete, and a failed or cancelled import leaves nothing behind (and the
 * old installation as it was). Files from the current installation that are still good are moved,
 * not copied, so a repair costs little.
 */
class Assembler(private val paths: GamePaths, private val gameId: String) {
    val staging: File get() = paths.staging(gameId)
    val game: File get() = paths.game(gameId)

    fun begin(): File {
        staging.deleteRecursively()
        staging.mkdirs()
        return staging
    }

    /** Moves [names] that [good] accepts from the current installation into staging. */
    fun reuse(names: Collection<String>, good: (File) -> Boolean) {
        for (name in names) {
            val current = FileValidator.find(game, name) ?: continue
            val target = File(staging, name)
            if (target.exists() || !good(current)) continue
            target.parentFile?.mkdirs()
            if (!current.renameTo(target)) current.copyTo(target, overwrite = true)
        }
    }

    /** Staging becomes the installation; the old one goes. */
    fun commit() {
        val old = File(paths.games, ".$gameId.old")
        old.deleteRecursively()
        paths.games.mkdirs()
        if (game.exists() && !game.renameTo(old)) throw ImportException(Problem.PERMISSION_DENIED, "The old installation couldn't be moved aside.")
        if (!staging.renameTo(game)) {
            old.renameTo(game)
            throw ImportException(Problem.PERMISSION_DENIED, "The new installation couldn't be put in place.")
        }
        old.deleteRecursively()
    }

    /** A stopped or failed import: staging goes, the installation stays as it was. */
    fun abandon() {
        staging.deleteRecursively()
    }
}

/** Copies [source] (a file) into [dir] as [name], streamed. */
fun copyInto(source: SourceNode, dir: File, name: String, cancel: CancelToken, onBytes: (Long) -> Unit = {}): File {
    val target = File(dir, name)
    source.open().use { copyStream(it, target, cancel, onBytes) }
    return target
}

/** A local file for [source], copied into [scratch] when it isn't one already (programs need a path). */
fun localCopy(source: SourceNode, scratch: File, cancel: CancelToken, onBytes: (Long) -> Unit = {}): File =
    source.localFile()?.takeIf { it.isFile } ?: copyInto(source, scratch, source.name, cancel, onBytes)


/**
 * Takes a game back to not installed: its folder (but what [GameImporter.keptInGame] names), its
 * library entry, its import record and anything half-made. Saves and settings in `saves/` stay, and
 * so do downloads (they're checked piece by piece, so importing again is quick). Plain Kotlin, unit-tested.
 */
object GameReset {
    fun reset(paths: GamePaths, gameId: String, kept: List<String> = emptyList()) {
        Library(paths).remove(gameId)
        File(paths.state, "import-$gameId.json").delete()
        paths.staging(gameId).deleteRecursively()
        File(paths.staging, "$gameId-scratch").deleteRecursively()
        File(paths.games, ".$gameId.old").deleteRecursively()
        val game = paths.game(gameId)
        if (!game.exists()) return
        val keep = kept.map { it.replace('\\', '/').trim('/').lowercase() }
        fun sweep(dir: File, prefix: String) {
            for (child in dir.listFiles().orEmpty()) {
                val path = (prefix + child.name).lowercase()
                when {
                    keep.any { it == path } -> {}
                    child.isDirectory && keep.any { it.startsWith("$path/") } -> sweep(child, "${child.name}/".let { prefix + it })
                    else -> child.deleteRecursively()
                }
            }
        }
        sweep(game, "")
        // Nothing of the player's left in it: the folder goes too.
        if (game.listFiles().isNullOrEmpty()) game.delete()
    }
}
