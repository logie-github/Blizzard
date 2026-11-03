package com.logie.blizz.importer

/** Where an import is. Persisted ([ImportStateRepository]) so the importer can be closed and reopened. */
enum class Stage {
    NOT_INSTALLED, DETECTING, DOWNLOADING, WAITING_FOR_USER_FILE, EXTRACTING, ASSEMBLING, VALIDATING,
    IMPORTED_UNTESTED, READY, FAILED,
}

/** What the wizard tells the person at the end. */
enum class Outcome {
    READY_TO_PLAY, IMPORTED_LAUNCH_UNTESTED, IMPORT_INCOMPLETE, MISSING_REQUIRED_FILE, UNSUPPORTED_CLIENT_VERSION, LAUNCH_TEST_FAILED,
}

/** Whether the game has been seen running under Winlator, kept apart from the file checks. */
enum class LaunchTest {
    /** Never started. */
    NOT_RUN,
    /** Its first window came up under Winlator. */
    WINDOW_SHOWN,
    /** It was started and no window came up. */
    FAILED,
}

/** Why an import stopped: each has its own message and remedy. */
enum class Problem {
    MISSING_SOURCE_DATA, CORRUPT_ARCHIVE, UNSUPPORTED_INSTALLER, UNSUPPORTED_VERSION, MISSING_EXPANSION, DOWNLOAD_FAILED,
    INSUFFICIENT_STORAGE, PERMISSION_DENIED, MISSING_RUNTIME_DEPENDENCY, LAUNCH_FAILED, PROFILE_INIT_FAILED, CANCELLED,
    /** The installer has to be run (in the app's Windows) to make the game's files. */
    INSTALLER_MUST_RUN,
}

class ImportException(val problem: Problem, message: String, val detail: String? = null, cause: Throwable? = null) : Exception(message, cause)

/** What the person can pick for a [MissingInput]. */
enum class PickKind { FILE, FOLDER, FILE_OR_FOLDER }

/**
 * Something only the person can supply: one specific file, folder or answer, with the sentence the
 * wizard asks it with. [optional] ones can be skipped ([skipLabel]).
 */
data class MissingInput(
    val id: String,
    val prompt: String,
    val kind: PickKind,
    val optional: Boolean = false,
    val skipLabel: String? = null,
)

/** An answer to a [MissingInput]: a picked file or folder, or a skip. */
sealed interface Supplied {
    val id: String
    data class Picked(override val id: String, val source: SourceNode) : Supplied
    data class Skipped(override val id: String) : Supplied
}

/** How far a long step is. [total] 0: unknown. */
data class Progress(val stage: Stage, val label: String, val done: Long = 0, val total: Long = 0)

/** One check of [com.logie.blizz.importer.GameImporter.validate]: what was checked and whether it passed. */
data class Check(val name: String, val passed: Boolean, val detail: String = "")

/** The result of validating an installed game. */
data class Validation(
    val checks: List<Check>,
    val clientVersion: String?,
    /** The checks prove what can be proven from files alone; true only when they all passed. */
    val filesOk: Boolean,
    val problem: Problem? = null,
    val message: String? = null,
)
