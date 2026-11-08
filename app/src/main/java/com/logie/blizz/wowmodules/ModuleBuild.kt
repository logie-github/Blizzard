
package com.logie.blizz.wowmodules

import org.json.JSONArray
import org.json.JSONObject
import kotlin.random.Random

/**
 * A realm built with the user's modules: what's asked of the build (.github/workflows/
 * build-realm-modules.yml), how its run on GitHub goes, and what's kept of it in the app.
 */
object ModuleBuild {
    const val WORKFLOW = "build-realm-modules.yml"

    /** At most this many modules in one build (the workflow's limit too). */
    const val MAX_MODULES = 40

    /**
     * A module the user picked: its repository and branch; [commit] is the branch's newest commit
     * when the build was asked for (null until then).
     */
    data class Chosen(
        val fullName: String,
        val branch: String,
        val description: String? = null,
        val avatar: String? = null,
        val commit: String? = null,
    ) {
        val name get() = fullName.substringAfter('/')
    }

    /**
     * A module a build left out: it doesn't compile with the realm's AzerothCore (written for
     * another one). [error] is the compiler's first word on why.
     */
    data class LeftOut(val name: String, val error: String)

    /**
     * A realm built with [modules] (the ones asked for, without [leftOut]), for the app's
     * [versionCode], from build [request]. [size]: its package, kept in the app to put it back in.
     */
    data class Built(
        val versionCode: Int,
        val request: String,
        val modules: List<Chosen>,
        val builtAt: Long = 0,
        val leftOut: List<LeftOut> = emptyList(),
        val size: Long = 0,
    )

    /** What the server package's stamp is when [built] is unpacked (ServerPackage). */
    fun stamp(built: Built) = "${built.versionCode}:modules:${built.request}"

    /** A build asked for and followed on GitHub: what came of it, as last seen. */
    data class Pending(
        val request: String,
        /** The release the package is attached to ([ModuleSource.RELEASE]). */
        val release: String,
        val versionCode: Int,
        val modules: List<Chosen>,
        val startedAt: Long,
        val runId: Long? = null,
        val runUrl: String? = null,
        val status: String? = null,
        val conclusion: String? = null,
        val step: String? = null,
        val checkedAt: Long = 0,
        /** The modules the build left out, once its record (server-<request>.json) is read. */
        val leftOut: List<LeftOut>? = null,
    ) {
        val isDone get() = status == "completed"
        val succeeded get() = isDone && conclusion == "success"
        val failed get() = isDone && conclusion != "success"
    }

    /** A name for a build, so its run and its package can be found. */
    fun newRequest(random: Random = Random.Default): String =
        (1..12).map { "abcdefghijklmnopqrstuvwxyz0123456789"[random.nextInt(36)] }.joinToString("")

    fun isRequest(text: String) = Regex("[a-z0-9]{8,32}").matches(text)

    fun assetName(request: String) = "server-$request.tar.xz"

    /** What went into the build's package (the workflow's build.json). */
    fun recordName(request: String) = "server-$request.json"

    /** The modules a build's record says it left out. */
    fun parseLeftOut(json: String): List<LeftOut> = leftOutFromJson(JSONObject(json).optJSONArray("leftOut"))

    /** [modules] without those [leftOut]. */
    fun without(modules: List<Chosen>, leftOut: List<LeftOut>): List<Chosen> =
        modules.filter { module -> leftOut.none { it.name.equals(module.name, ignoreCase = true) } }

    private val MODULE_NAME = Regex("[A-Za-z0-9_.-]{1,100}")

    /** A branch name that's safe in a URL's path and as git's ref. */
    fun isBranch(text: String): Boolean =
        text.isNotEmpty() && text.length <= 200 && Regex("[A-Za-z0-9._/-]+").matches(text) &&
            ".." !in text && !text.startsWith("/") && !text.endsWith("/") && !text.endsWith(".lock")

    /** The modules the build adds: owner/name@commit a line, without the realm's own ([base]). */
    fun modulesInput(chosen: List<Chosen>, base: Set<String>): String =
        chosen.filter { it.name !in base && ModuleCatalog.isFullName(it.fullName) && it.commit != null && ModuleCatalog.isCommit(it.commit) }
            .distinctBy { it.name.lowercase() }
            .joinToString("\n") { "${it.fullName}@${it.commit}" }

    /** The workflow's inputs, as GitHub's dispatch wants them. */
    fun dispatchBody(branch: String, request: String, modules: String): String =
        JSONObject()
            .put("ref", branch)
            .put("inputs", JSONObject().put("request", request).put("modules", modules))
            .toString()

    // How the run goes ------------------------------------------------------------------------------

    data class Run(val id: Long, val status: String, val conclusion: String?, val url: String) {
        val isDone get() = status == "completed"
        val succeeded get() = isDone && conclusion == "success"
    }

    /** The run of build [request] among the workflow's runs (its title names the request). */
    fun findRun(runsJson: String, request: String): Run? {
        val runs = JSONObject(runsJson).optJSONArray("workflow_runs") ?: return null
        for (i in 0 until runs.length()) {
            val run = runs.getJSONObject(i)
            val title = run.optString("display_title")
            if (title.split(' ').getOrNull(1) == request) return run(run)
        }
        return null
    }

    fun parseRun(json: String): Run = run(JSONObject(json))

    private fun run(run: JSONObject) = Run(
        id = run.optLong("id"),
        status = run.optString("status"),
        conclusion = run.optString("conclusion").takeIf { it.isNotEmpty() && it != "null" },
        url = run.optString("html_url"),
    )

    /** What the run is on: the step under way (or the last one done) of the job under way. */
    fun currentStep(jobsJson: String): String? {
        val jobs = JSONObject(jobsJson).optJSONArray("jobs") ?: return null
        var last: String? = null
        for (i in 0 until jobs.length()) {
            val job = jobs.getJSONObject(i)
            val steps = job.optJSONArray("steps") ?: continue
            for (j in 0 until steps.length()) {
                val step = steps.getJSONObject(j)
                val name = step.optString("name")
                if (name.startsWith("Set up") || name.startsWith("Post ") || name.startsWith("Complete") || name.startsWith("Run actions/")) continue
                when (step.optString("status")) {
                    "in_progress" -> return name
                    "completed" -> {
                        // A failed step is what to tell.
                        if (step.optString("conclusion") == "failure") return name
                        last = name
                    }
                }
            }
        }
        return last
    }

    /** The run, as last seen, into [pending]. */
    fun seen(pending: Pending, run: Run, step: String?, now: Long): Pending =
        pending.copy(runId = run.id, runUrl = run.url, status = run.status, conclusion = run.conclusion, step = step ?: pending.step, checkedAt = now)

    // Kept in the app -------------------------------------------------------------------------------

    fun chosenToJson(list: List<Chosen>): JSONArray = JSONArray().apply {
        for (module in list) {
            put(
                JSONObject().put("fullName", module.fullName).put("branch", module.branch)
                    .put("description", module.description ?: JSONObject.NULL).put("avatar", module.avatar ?: JSONObject.NULL)
                    .put("commit", module.commit ?: JSONObject.NULL)
            )
        }
    }

    fun chosenFromJson(array: JSONArray?): List<Chosen> = (0 until (array?.length() ?: 0)).mapNotNull { i ->
        val o = array!!.optJSONObject(i) ?: return@mapNotNull null
        val fullName = o.optString("fullName")
        val branch = o.optString("branch")
        val commit = o.text("commit")
        if (!ModuleCatalog.isFullName(fullName) || !isBranch(branch) || (commit != null && !ModuleCatalog.isCommit(commit))) {
            return@mapNotNull null
        }
        Chosen(fullName, branch, o.text("description"), o.text("avatar"), commit)
    }

    private fun JSONObject.text(key: String): String? = if (isNull(key)) null else optString(key).takeIf { it.isNotEmpty() }

    private fun leftOutToJson(list: List<LeftOut>): JSONArray = JSONArray().apply {
        for (module in list) put(JSONObject().put("name", module.name).put("error", module.error))
    }

    private fun leftOutFromJson(array: JSONArray?): List<LeftOut> = (0 until (array?.length() ?: 0)).mapNotNull { i ->
        val o = array!!.optJSONObject(i) ?: return@mapNotNull null
        val name = o.optString("name").takeIf { MODULE_NAME.matches(it) } ?: return@mapNotNull null
        LeftOut(name, o.optString("error").take(300))
    }

    private fun builtObject(built: Built): JSONObject =
        JSONObject().put("versionCode", built.versionCode).put("request", built.request)
            .put("modules", chosenToJson(built.modules)).put("builtAt", built.builtAt)
            .put("leftOut", leftOutToJson(built.leftOut)).put("size", built.size)

    private fun builtFrom(o: JSONObject): Built? {
        val request = o.optString("request").takeIf { isRequest(it) } ?: return null
        if (!o.has("versionCode")) return null
        return Built(
            o.getInt("versionCode"), request, chosenFromJson(o.optJSONArray("modules")), o.optLong("builtAt"),
            leftOutFromJson(o.optJSONArray("leftOut")), o.optLong("size"),
        )
    }

    fun builtToJson(built: Built): String = builtObject(built).toString()

    fun builtFromJson(text: String?): Built? = runCatching { builtFrom(JSONObject(text ?: return null)) }.getOrNull()

    /** The realms kept in the app. */
    fun savedToJson(list: List<Built>): String = JSONArray().apply { list.forEach { put(builtObject(it)) } }.toString()

    fun savedFromJson(text: String?): List<Built> = runCatching {
        val array = JSONArray(text ?: return emptyList())
        (0 until array.length()).mapNotNull { i -> array.optJSONObject(i)?.let { builtFrom(it) } }.distinctBy { it.request }
    }.getOrDefault(emptyList())

    fun pendingToJson(pending: Pending): String =
        JSONObject().put("request", pending.request).put("release", pending.release).put("versionCode", pending.versionCode)
            .put("modules", chosenToJson(pending.modules)).put("startedAt", pending.startedAt)
            .put("runId", pending.runId ?: JSONObject.NULL).put("runUrl", pending.runUrl ?: JSONObject.NULL)
            .put("status", pending.status ?: JSONObject.NULL).put("conclusion", pending.conclusion ?: JSONObject.NULL)
            .put("step", pending.step ?: JSONObject.NULL).put("checkedAt", pending.checkedAt)
            .put("leftOut", pending.leftOut?.let { leftOutToJson(it) } ?: JSONObject.NULL)
            .toString()

    fun pendingFromJson(text: String?): Pending? = runCatching {
        val o = JSONObject(text ?: return null)
        val request = o.getString("request").takeIf { isRequest(it) } ?: return null
        Pending(
            request = request,
            release = o.getString("release"),
            versionCode = o.getInt("versionCode"),
            modules = chosenFromJson(o.optJSONArray("modules")),
            startedAt = o.optLong("startedAt"),
            runId = if (o.isNull("runId")) null else o.optLong("runId").takeIf { it > 0 },
            runUrl = o.text("runUrl"),
            status = o.text("status"),
            conclusion = o.text("conclusion"),
            step = o.text("step"),
            checkedAt = o.optLong("checkedAt"),
            leftOut = if (o.isNull("leftOut")) null else leftOutFromJson(o.optJSONArray("leftOut")),
        )
    }.getOrNull()
}
