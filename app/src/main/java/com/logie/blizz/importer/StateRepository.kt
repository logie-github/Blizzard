package com.logie.blizz.importer

import org.json.JSONObject
import java.io.File

/** One game's import, as it stands. */
data class ImportRecord(
    val gameId: String,
    val stage: Stage = Stage.NOT_INSTALLED,
    val outcome: Outcome? = null,
    val problem: Problem? = null,
    val message: String? = null,
    val detail: String? = null,
    val launchTest: LaunchTest = LaunchTest.NOT_RUN,
    /** Inputs the person already supplied (their ids), kept across a close and reopen. */
    val supplied: Map<String, String> = emptyMap(),
    val skipped: Set<String> = emptySet(),
    val updatedAt: Long = 0,
    /** The importer's install recipe ([GameImporter.recipe]) that made this install; 0 before recipes existed. */
    val recipe: Int = 0,
) {
    fun toJson(): JSONObject = JSONObject()
        .put("gameId", gameId)
        .put("stage", stage.name)
        .put("outcome", outcome?.name)
        .put("problem", problem?.name)
        .put("message", message)
        .put("detail", detail)
        .put("launchTest", launchTest.name)
        .put("supplied", JSONObject(supplied as Map<*, *>))
        .put("skipped", org.json.JSONArray(skipped.toList()))
        .put("updatedAt", updatedAt)
        .put("recipe", recipe)

    companion object {
        fun fromJson(o: JSONObject): ImportRecord {
            val supplied = o.optJSONObject("supplied")?.let { s -> s.keys().asSequence().associateWith { s.getString(it) } } ?: emptyMap()
            val skipped = o.optJSONArray("skipped")?.let { a -> (0 until a.length()).map { a.getString(it) }.toSet() } ?: emptySet()
            return ImportRecord(
                gameId = o.getString("gameId"),
                stage = enumOr(o.optString("stage"), Stage.NOT_INSTALLED),
                outcome = o.optString("outcome").takeIf { it.isNotEmpty() && it != "null" }?.let { enumOr<Outcome>(it, null) },
                problem = o.optString("problem").takeIf { it.isNotEmpty() && it != "null" }?.let { enumOr<Problem>(it, null) },
                message = o.optString("message").takeIf { it.isNotEmpty() && it != "null" },
                detail = o.optString("detail").takeIf { it.isNotEmpty() && it != "null" },
                launchTest = enumOr(o.optString("launchTest"), LaunchTest.NOT_RUN),
                supplied = supplied,
                skipped = skipped,
                updatedAt = o.optLong("updatedAt"),
                recipe = o.optInt("recipe", 0),
            )
        }

        private inline fun <reified T : Enum<T>> enumOr(name: String?, fallback: T?): T =
            (enumValues<T>().firstOrNull { it.name == name } ?: fallback) as T
    }
}

/** Writes a file whole or not at all: to a temporary file beside it, then renamed over it. */
fun File.writeAtomically(text: String) {
    parentFile?.mkdirs()
    val temp = File(parentFile, ".$name.tmp")
    temp.writeText(text)
    if (!temp.renameTo(this)) {
        delete()
        if (!temp.renameTo(this)) throw java.io.IOException("Couldn't write $path")
    }
}

/** The games' import records, one JSON file each under `state/`. */
class ImportStateRepository(private val paths: GamePaths) {
    private fun file(gameId: String) = File(paths.state, "import-$gameId.json")

    @Synchronized
    fun load(gameId: String): ImportRecord = runCatching {
        ImportRecord.fromJson(JSONObject(file(gameId).readText()))
    }.getOrElse { ImportRecord(gameId) }

    @Synchronized
    fun save(record: ImportRecord): ImportRecord {
        val stamped = record.copy(updatedAt = System.currentTimeMillis())
        file(record.gameId).writeAtomically(stamped.toJson().toString(2))
        return stamped
    }

    fun update(gameId: String, change: (ImportRecord) -> ImportRecord): ImportRecord = synchronized(this) { save(change(load(gameId))) }
}
