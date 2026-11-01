package com.logie.blizz.importer

/**
 * Runs an importer's steps in order and keeps the import's record: Detect, Acquire (downloads),
 * Request missing files (it stops there and waits), Install, Validate, then the library entry.
 * Plain Kotlin (no Android), so the whole flow is unit-tested.
 */
class ImportPipeline(private val repo: ImportStateRepository, private val library: Library) {
    sealed interface Result {
        val record: ImportRecord
        data class Waiting(override val record: ImportRecord, val missing: List<MissingInput>, val autoSources: List<AutoSource>) : Result
        data class Done(override val record: ImportRecord, val validation: Validation, val entry: LibraryEntry) : Result
        data class Failed(override val record: ImportRecord, val error: ImportException, val validation: Validation? = null) : Result
    }

    fun run(importer: GameImporter, env: ImportEnv, supplied: Map<String, Supplied>, repair: Boolean = false): Result {
        val id = importer.gameId
        fun stage(s: Stage) = repo.update(id) { it.copy(stage = s, problem = null, message = null, detail = null, outcome = null) }
        var autoSources: List<AutoSource> = emptyList()
        return try {
            stage(Stage.DETECTING)
            val detection = importer.detect(env)
            if (!detection.installed || repair) {
                autoSources = importer.resolveSources(env, detection, supplied)
                if (autoSources.isNotEmpty()) {
                    stage(Stage.DOWNLOADING)
                    importer.downloadAvailableFiles(env, autoSources)
                }
                val missing = importer.getMissingInputs(env, detection, supplied).filter { m -> supplied[m.id] == null }
                if (missing.isNotEmpty()) {
                    val record = repo.update(id) { it.copy(stage = Stage.WAITING_FOR_USER_FILE, outcome = null, message = missing.first().prompt) }
                    return Result.Waiting(record, missing, autoSources)
                }
                stage(Stage.EXTRACTING)
                if (repair) importer.repair(env, supplied) else importer.importFiles(env, detection, supplied)
            }
            stage(Stage.VALIDATING)
            val validation = importer.validate(env)
            if (!validation.filesOk) {
                val e = ImportException(validation.problem ?: Problem.MISSING_SOURCE_DATA, validation.message ?: "The game's files didn't check out.")
                return fail(id, e, validation)
            }
            val ready = importer.readyStage(validation)
            val entry = importer.registerLaunchEntry(env, validation).copy(stage = ready)
            library.put(entry)
            val record = repo.update(id) {
                it.copy(
                    stage = ready,
                    outcome = if (ready == Stage.READY) Outcome.READY_TO_PLAY else Outcome.IMPORTED_LAUNCH_UNTESTED,
                    problem = null, message = null, detail = null,
                    supplied = emptyMap(), skipped = emptySet(),
                )
            }
            Result.Done(record, validation, entry)
        } catch (e: ImportException) {
            if (e.problem == Problem.CANCELLED) {
                val installed = library.get(id)
                val record = repo.update(id) { it.copy(stage = installed?.stage ?: Stage.NOT_INSTALLED, outcome = null, problem = Problem.CANCELLED, message = "Cancelled. Downloads so far are kept.", detail = null) }
                Result.Failed(record, e)
            } else {
                fail(id, e, null)
            }
        } catch (e: java.io.IOException) {
            val problem = if (e.message?.contains("ENOSPC") == true || e.message?.contains("No space", true) == true) Problem.INSUFFICIENT_STORAGE else Problem.PERMISSION_DENIED
            fail(id, ImportException(problem, if (problem == Problem.INSUFFICIENT_STORAGE) "The phone ran out of space. Free some and retry." else "A file couldn't be read or written (${e.message}).", e.toString(), e), null)
        } catch (e: SecurityException) {
            fail(id, ImportException(Problem.PERMISSION_DENIED, "The app may no longer read that file or folder: pick it again.", e.toString(), e), null)
        }
    }

    private fun fail(id: String, e: ImportException, validation: Validation?): Result.Failed {
        val outcome = outcomeFor(e.problem)
        // A game that was installed and still is stays playable: a failed repair didn't touch it.
        val installed = library.get(id)
        val record = repo.update(id) {
            it.copy(stage = if (installed != null && e.problem != Problem.UNSUPPORTED_VERSION) installed.stage else Stage.FAILED, outcome = outcome, problem = e.problem, message = e.message, detail = e.detail)
        }
        return Result.Failed(record, e, validation)
    }

    companion object {
        fun outcomeFor(problem: Problem): Outcome = when (problem) {
            Problem.MISSING_SOURCE_DATA, Problem.MISSING_EXPANSION -> Outcome.MISSING_REQUIRED_FILE
            Problem.UNSUPPORTED_VERSION -> Outcome.UNSUPPORTED_CLIENT_VERSION
            Problem.LAUNCH_FAILED -> Outcome.LAUNCH_TEST_FAILED
            else -> Outcome.IMPORT_INCOMPLETE
        }
    }
}
