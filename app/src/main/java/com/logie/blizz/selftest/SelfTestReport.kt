package com.logie.blizz.selftest

import com.logie.blizz.importer.ImportRecord
import com.logie.blizz.importer.LibraryEntry
import org.json.JSONArray
import org.json.JSONObject

enum class Install { NOT_INSTALLED, INCOMPLETE, INSTALLED }

enum class Launch { NOT_TESTED, OK, FAILED, TIMED_OUT }

/** What the launch test found for one game. */
data class GameResult(
    val gameId: String,
    val title: String,
    val install: Install,
    val installDetail: String,
    val launch: Launch = Launch.NOT_TESTED,
    val launchDetail: String = "",
    /** Seconds from Play to the runtime handing over to the game (null when not measured). */
    val preparedSeconds: Int? = null,
    /** Seconds from Play to the game's first window. */
    val windowSeconds: Int? = null,
    val log: String? = null,
) {
    fun toJson(): JSONObject = JSONObject().put("gameId", gameId).put("title", title).put("install", install.name)
        .put("installDetail", installDetail).put("launch", launch.name).put("launchDetail", launchDetail)
        .put("preparedSeconds", preparedSeconds).put("windowSeconds", windowSeconds).put("log", log)

    companion object {
        fun fromJson(o: JSONObject) = GameResult(
            o.getString("gameId"), o.getString("title"), Install.valueOf(o.getString("install")), o.optString("installDetail"),
            Launch.valueOf(o.getString("launch")), o.optString("launchDetail"),
            if (o.isNull("preparedSeconds")) null else o.getInt("preparedSeconds"),
            if (o.isNull("windowSeconds")) null else o.getInt("windowSeconds"),
            if (o.isNull("log")) null else o.getString("log"),
        )

        fun listFromJson(text: String): List<GameResult> = runCatching {
            val a = JSONArray(text)
            (0 until a.length()).map { fromJson(a.getJSONObject(it)) }
        }.getOrDefault(emptyList())

        fun listToJson(list: List<GameResult>): String = JSONArray(list.map { it.toJson() }).toString()
    }
}

/** What the game's files and import record say before anything is started. */
data class Inspection(val install: Install, val detail: String)

/** The self-test's pure parts: telling what is installed, and writing the report. */
object SelfTestReport {
    fun inspect(record: ImportRecord, entry: LibraryEntry?, programExists: Boolean): Inspection = when {
        entry != null && programExists -> Inspection(Install.INSTALLED, "Files present (${record.stage.name}); program ${entry.executable}")
        entry != null -> Inspection(Install.INCOMPLETE, "Registered, but its program is missing: ${entry.executable} in ${entry.installPath}")
        record.problem != null -> Inspection(
            Install.INCOMPLETE,
            "The import stopped: ${record.problem.name}. ${record.message.orEmpty()} ${record.detail.orEmpty()}".trim(),
        )
        record.stage.name == "NOT_INSTALLED" -> Inspection(Install.NOT_INSTALLED, "Never imported")
        else -> Inspection(Install.INCOMPLETE, "Stage ${record.stage.name}, no launch entry")
    }

    private fun mark(r: GameResult) = when {
        r.install != Install.INSTALLED -> "not tested"
        r.launch == Launch.OK -> "OK"
        r.launch == Launch.TIMED_OUT -> "TIMED OUT"
        r.launch == Launch.FAILED -> "FAILED"
        else -> "not tested"
    }

    private fun installMark(r: GameResult) = when (r.install) {
        Install.INSTALLED -> "installed"
        Install.INCOMPLETE -> "INCOMPLETE"
        Install.NOT_INSTALLED -> "not installed"
    }

    private fun cell(text: String) = text.replace("|", "\\|").replace("\n", " ")

    fun title(version: String, results: List<GameResult>): String {
        val tested = results.count { it.install == Install.INSTALLED }
        val ok = results.count { it.launch == Launch.OK }
        return "Launch test $version: $ok of $tested installed games launched ($tested of ${results.size} installed)"
    }

    /** The report as Markdown (a GitHub issue's body): a summary table, then each game that has something to say. */
    fun markdown(
        results: List<GameResult>,
        header: List<Pair<String, String>>,
        interruptedAt: String? = null,
        maxLog: Int = 3000,
        redact: (String) -> String = { it },
    ): String = buildString {
        append("## Launch test\n\n")
        append("| | |\n| --- | --- |\n")
        for ((k, v) in header) append("| ${cell(k)} | ${cell(v)} |\n")
        if (interruptedAt != null) append("\n**The app stopped while testing $interruptedAt**, so the games after it weren't tested.\n")
        append("\n| Game | Installed | Launch | Prepared | First window |\n| --- | --- | --- | --- | --- |\n")
        for (r in results) {
            append("| ${cell(r.title)} | ${installMark(r)} | ${mark(r)} | ${r.preparedSeconds?.let { "$it s" } ?: "-"} | ${r.windowSeconds?.let { "$it s" } ?: "-"} |\n")
        }
        for (r in results) {
            val notes = listOfNotNull(
                r.installDetail.takeIf { it.isNotBlank() }?.let { "Install: $it" },
                r.launchDetail.takeIf { it.isNotBlank() }?.let { "Launch: $it" },
            )
            if (notes.isEmpty() && r.log.isNullOrBlank()) continue
            append("\n### ${r.title}\n\n")
            notes.forEach { append("- ${it.replace("\n", " ")}\n") }
            if (!r.log.isNullOrBlank() && r.launch != Launch.OK) {
                append("\n<details><summary>Log</summary>\n\n```\n").append(redact(r.log).takeLast(maxLog)).append("\n```\n</details>\n")
            }
        }
        append("\n_Written by the app's launch test._\n")
    }.take(60_000)
}
