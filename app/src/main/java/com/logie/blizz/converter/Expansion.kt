package com.logie.blizz.converter

import org.json.JSONObject

/**
 * An expansion the Converter takes the maps, quests and the rest of the content of, in 3.3.5a's format, one expansion at a time
 * (`realm/warcraft/converter/expansions.json` is the list the driver reads; [Expansions.all] is the same list, kept equal by a test).
 * [id] is the Map table's ExpansionID; [build] is the wago.tools build its files and tables come from.
 */
data class Expansion(val key: String, val name: String, val id: Int, val build: String)

object Expansions {
    val all = listOf(
        Expansion("cataclysm", "Cataclysm", 3, "4.4.2.60895"),
        Expansion("mop", "Mists of Pandaria", 4, "7.3.5.26972"),
        Expansion("wod", "Warlords of Draenor", 5, "7.3.5.26972"),
        Expansion("legion", "Legion", 6, "7.3.5.26972"),
    )

    fun byKey(key: String): Expansion? = all.firstOrNull { it.key == key }
}

/** What the driver's `progress.json` says (state: starting, running, done, partial, deferred, failed). */
data class ConverterProgress(
    val expansion: String,
    val state: String,
    val stage: String,
    val unit: String,
    val done: Int,
    val total: Int,
    val message: String,
    val updated: Long,
    val failedUnits: Int,
) {
    val fraction: Float? get() = if (total > 0) (done.toFloat() / total).coerceIn(0f, 1f) else null
    val finished: Boolean get() = state == "done" || state == "partial" || state == "deferred" || state == "failed"

    companion object {
        fun parse(text: String): ConverterProgress? = runCatching {
            val j = JSONObject(text)
            val units = j.optJSONObject("units")
            var failed = 0
            if (units != null) for (k in units.keys()) if (units.getJSONObject(k).optString("state") == "failed") failed++
            ConverterProgress(
                j.getString("expansion"), j.optString("state"), j.optString("stage"), j.optString("unit"), j.optInt("done"), j.optInt("total"),
                j.optString("message"), j.optLong("updated"), failed,
            )
        }.getOrNull()
    }
}
