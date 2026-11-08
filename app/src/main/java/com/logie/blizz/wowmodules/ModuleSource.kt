package com.logie.blizz.wowmodules

import com.logie.blizz.BuildConfig
import org.json.JSONObject

/**
 * Where the realm's modules are built. The workflow (`build-realm-modules.yml`) is in this repository and
 * compiles the realm from the `realm/` folder of it (the scripts, pins, patches and the realm's own modules),
 * then attaches the package to the release [RELEASE]. Nothing of another app's repository is used.
 */
object ModuleSource {
    /** The repository the workflow, the release and the built packages are in: this app's own. */
    val REPO: String get() = BuildConfig.UPDATE_REPO

    /** The release the built realms are attached to (not an app release: the updater reads `blizzard-build-N` only). */
    const val RELEASE = "realm-modules"

    /** Which realm sources a package was built from (`realm/`), for telling a package of an older layout from this one's. */
    const val REALM_SOURCE = 1

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
