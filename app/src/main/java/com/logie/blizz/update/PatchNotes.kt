package com.logie.blizz.update

import android.content.Context
import com.logie.blizz.BuildConfig
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import org.json.JSONArray
import org.json.JSONObject
import java.io.File

/**
 * The launcher's patch notes: one line for each change, written with the change (the repository's `notes/`, one file a
 * change) and put by CI into its release's description as "- " lines (`scripts/release-notes.sh`). The app reads them from
 * the releases list the updater fetches anyway ([Updater.findUpdate]: no request of their own), keeps them in its files
 * for when GitHub can't be reached, and shows them on Settings' Games page (the gear button) and nowhere else.
 */
object PatchNotes {
    /** One release's notes: its build (the version code, `blizzard-build-N`) and its lines. */
    data class Release(val versionCode: Int, val lines: List<String>)

    private const val FILE = "patch-notes.json"

    private val _kept = MutableStateFlow<List<Release>?>(null)

    /** The notes kept, newest first; null until [load] read them. */
    val kept: StateFlow<List<Release>?> = _kept

    /** A release's notes: the "- " lines of its description (what follows them, how to install, isn't one). */
    fun lines(body: String): List<String> = body.lineSequence()
        .map { it.trim() }
        .filter { it.startsWith("- ") }
        .map { it.removePrefix("- ").trim() }
        .filter { it.isNotEmpty() }
        .toList()

    /** The releases of this app ([prefix]-N) that have notes, newest first, from GitHub's releases list. Drafts and pre-releases aren't. */
    fun parse(json: String, prefix: String = BuildConfig.RELEASE_TAG_PREFIX): List<Release> {
        val array = JSONArray(json)
        val out = ArrayList<Release>()
        for (i in 0 until array.length()) {
            val release = array.optJSONObject(i) ?: continue
            if (release.optBoolean("draft") || release.optBoolean("prerelease")) continue
            val tag = release.optString("tag_name")
            if (!tag.startsWith("$prefix-")) continue
            val code = tag.removePrefix("$prefix-").toIntOrNull() ?: continue
            val lines = lines(release.optString("body"))
            if (lines.isNotEmpty()) out.add(Release(code, lines))
        }
        return out.sortedByDescending { it.versionCode }
    }

    /** The kept ones with [fresh]: a release in both is [fresh]'s; one the list no longer holds (it has the latest fifty) stays. */
    fun merge(kept: List<Release>, fresh: List<Release>): List<Release> {
        val byCode = LinkedHashMap<Int, Release>()
        for (r in kept) byCode[r.versionCode] = r
        for (r in fresh) byCode[r.versionCode] = r
        return byCode.values.sortedByDescending { it.versionCode }
    }

    /** The notes in GitHub's releases list [releasesJson], kept with those kept before. Background thread. */
    @Synchronized
    fun keep(context: Context, releasesJson: String) {
        val fresh = runCatching { parse(releasesJson) }.getOrNull() ?: return
        val merged = merge(load(context), fresh)
        if (merged != _kept.value) save(context, merged)
        _kept.value = merged
    }

    /** The notes kept in the app's files (read once; [kept] has them after). Background thread. */
    @Synchronized
    fun load(context: Context): List<Release> {
        _kept.value?.let { return it }
        val read = runCatching {
            val array = JSONArray(File(context.applicationContext.filesDir, FILE).readText())
            List(array.length()) { i ->
                val o = array.getJSONObject(i)
                val lines = o.getJSONArray("lines")
                Release(o.getInt("build"), List(lines.length()) { lines.getString(it) })
            }
        }.getOrDefault(emptyList())
        _kept.value = read
        return read
    }

    /** Forgets what was kept, in memory and in the app's files (the tests start from nothing). */
    @Synchronized
    internal fun forget(context: Context) {
        File(context.applicationContext.filesDir, FILE).delete()
        _kept.value = null
    }

    private fun save(context: Context, releases: List<Release>) {
        val array = JSONArray()
        for (r in releases) array.put(JSONObject().put("build", r.versionCode).put("lines", JSONArray(r.lines)))
        val dir = context.applicationContext.filesDir
        val part = File(dir, "$FILE.part")
        runCatching {
            part.writeText(array.toString())
            if (!part.renameTo(File(dir, FILE))) part.delete()
        }
    }
}
