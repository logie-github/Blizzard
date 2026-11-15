package com.logie.blizz.forevernew

import org.json.JSONObject
import java.io.File

/**
 * WoW Forever (new integration, 15 November 2026): the stages the realm goes through. Written fresh; nothing here
 * comes from earlier Forever work. NOT run on a phone: see docs/forever-new.md for what has and hasn't been verified.
 */
enum class ForeverState {
    NOT_INSTALLED, DOWNLOADING, AWAITING_CLIENT, EXTRACTING, INSTALLING_DB, BUILDING_MAPS,
    STARTING_AUTH, STARTING_WORLD, READY, PLAYING, STOPPING, FAILED, REPAIRING;

    /** A stage that is running work now (the page shows progress and a Stop). */
    val busy: Boolean get() = this in setOf(DOWNLOADING, EXTRACTING, INSTALLING_DB, BUILDING_MAPS, STARTING_AUTH, STARTING_WORLD, STOPPING, REPAIRING)
}

/** The ports of Forever's own processes. None is used by another realm of the app (3310-3312, 3724, 1119, 8081, 8085-8087, 8090, 8095, 8096). */
object ForeverPorts {
    const val DATABASE = 3313
    const val BNET = 1120
    const val REST = 8082
    const val WORLD = 8097
    const val INSTANCE = 8098
    val all = listOf(DATABASE, BNET, REST, WORLD, INSTANCE)
}

/** Where a failure happened, so the page can name the subsystem and not spin. */
data class ForeverFailure(val stage: ForeverState, val subsystem: String, val message: String)

/**
 * The persisted state: one small JSON file written atomically (temp file, then rename), so a kill in the middle of a write
 * leaves the previous state. A stage that was running when the app died is not trusted: [load] gives back FAILED with
 * "interrupted" for a busy state, and the installer resumes from its checkpoints.
 */
class ForeverStateStore(private val file: File) {
    data class Saved(val state: ForeverState, val detail: String, val failure: ForeverFailure?)

    fun save(state: ForeverState, detail: String = "", failure: ForeverFailure? = null) {
        file.parentFile?.mkdirs()
        val json = JSONObject().put("state", state.name).put("detail", detail)
        failure?.let { json.put("failure", JSONObject().put("stage", it.stage.name).put("subsystem", it.subsystem).put("message", it.message)) }
        val tmp = File(file.path + ".tmp")
        tmp.writeText(json.toString())
        if (!tmp.renameTo(file)) { file.delete(); check(tmp.renameTo(file)) { "state not saved" } }
    }

    fun load(): Saved {
        val text = runCatching { file.readText() }.getOrNull() ?: return Saved(ForeverState.NOT_INSTALLED, "", null)
        return runCatching {
            val json = JSONObject(text)
            val state = ForeverState.valueOf(json.getString("state"))
            val failure = json.optJSONObject("failure")?.let {
                ForeverFailure(ForeverState.valueOf(it.getString("stage")), it.getString("subsystem"), it.getString("message"))
            }
            if (state.busy || state == ForeverState.PLAYING) {
                Saved(ForeverState.FAILED, "The app stopped while this was running; it continues from its last checkpoint.",
                    failure ?: ForeverFailure(state, "app", "interrupted"))
            } else Saved(state, json.optString("detail"), failure)
        }.getOrElse { Saved(ForeverState.NOT_INSTALLED, "", null) }
    }
}
