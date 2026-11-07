package com.logie.blizz.wowmodules

import com.logie.blizz.BuildConfig
import com.logie.blizz.wow.WowLayout
import org.json.JSONObject

/**
 * Where the realm's modules are built, and what Blizzard knows of the realm it holds.
 *
 * The workflow (`build-warcraft-modules.yml`) lives in the World of Warcraft app's repository and
 * compiles the realm from one of that app's releases (`wow-build-N`, N being the app's version
 * code). Blizzard holds a copy of that app's realm, so the release it asks for is the one of the
 * app that made the export: the export's `appVersion` is `1.0.N`.
 */
object ModuleSource {
    /** The repository the workflow, the releases and the built packages are in (the WoW app's, as its build gave it). */
    const val REPO = "logie-github/YeaBwoi"

    /** The WoW app's release tags are `wow-build-N`. */
    const val RELEASE_TAG_PREFIX = "wow-build"

    /**
     * The modules the realm has always (`warcraft/server-version.env`'s MODULES): a build skips
     * them, and the screen shows them as in the realm. The workflow skips a repeat itself too.
     */
    val BASE_MODULES: Set<String> = setOf(
        "mod-playerbots", "mod-progression-system", "mod-zone-difficulty", "mod-chromie-xp",
        "mod-chromiecraft-smartstone", "mod-hoard-collector", "mod-npc-talent-template", "mod-ale", "mod-worgoblin",
    )

    val userAgent: String get() = "${BuildConfig.APPLICATION_ID}/${BuildConfig.VERSION_NAME} (realm modules)"

    fun workflowUrl() = "https://${GitHubApi.API_HOST}/repos/$REPO/actions/workflows/${ModuleBuild.WORKFLOW}"

    fun repoUrl() = "https://${GitHubApi.API_HOST}/repos/$REPO"

    fun runsUrl() = "${workflowUrl()}/runs?event=workflow_dispatch&per_page=30"

    fun runUrl(runId: Long) = "${repoUrl()}/actions/runs/$runId"

    fun releaseUrl(tag: String) = "${repoUrl()}/releases/tags/$tag"

    /** The WoW app's version code from its version name (`1.0.52` is 52), or null when it isn't one of its names. */
    fun versionCodeOf(appVersion: String?): Int? =
        Regex("^\\d+\\.\\d+\\.(\\d{1,9})$").matchEntire(appVersion?.trim().orEmpty())?.groupValues?.get(1)?.toIntOrNull()?.takeIf { it > 0 }

    /** The version code of the WoW app that made the export Blizzard's realm came from (its `export.json`). */
    fun exportedVersionCode(layout: WowLayout): Int? = runCatching {
        versionCodeOf(JSONObject(layout.manifest.readText()).optString("appVersion"))
    }.getOrNull()

    /** A file attached to a release. [sha256] is GitHub's own digest of it, when it gives one. */
    data class Asset(val name: String, val url: String, val size: Long, val sha256: String? = null)

    fun parseAssets(json: String): List<Asset> {
        val assets = JSONObject(json).optJSONArray("assets") ?: return emptyList()
        return (0 until assets.length()).mapNotNull { i ->
            val asset = assets.optJSONObject(i) ?: return@mapNotNull null
            val name = asset.optString("name").takeIf { it.isNotEmpty() } ?: return@mapNotNull null
            val url = asset.optString("url").takeIf { it.isNotEmpty() } ?: return@mapNotNull null
            val digest = asset.optString("digest").takeIf { it.startsWith("sha256:") }?.removePrefix("sha256:")?.lowercase()
                ?.takeIf { Regex("[0-9a-f]{64}").matches(it) }
            Asset(name, url, asset.optLong("size"), digest)
        }
    }

    /** The default branch out of the repository's answer. */
    fun parseDefaultBranch(json: String): String? =
        JSONObject(json).optString("default_branch").takeIf { ModuleBuild.isBranch(it) }
}
