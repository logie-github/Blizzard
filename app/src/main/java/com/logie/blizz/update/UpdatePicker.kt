
package com.logie.blizz.update

/**
 * Picks the app's newest release out of the repository's GitHub releases. The repository publishes
 * other apps too, told apart by their tag prefix: this app's are "blizzard-build-N", where N is the
 * build number, which is also the APK's version code.
 */
object UpdatePicker {
    data class Asset(val name: String, val url: String, val size: Long)

    data class Release(
        val tag: String,
        val title: String,
        val draft: Boolean,
        val prerelease: Boolean,
        val assets: List<Asset>,
    )

    data class Update(val versionCode: Int, val title: String, val apk: Asset)

    /** The build number in [tag] if it is one of this app's release tags. */
    fun versionCodeOf(tag: String, tagPrefix: String): Int? =
        Regex("^${Regex.escape(tagPrefix)}-(\\d+)$").find(tag)?.groupValues?.get(1)?.toIntOrNull()

    /** The newest release with an APK that is newer than [currentVersionCode], if any. */
    fun pick(releases: List<Release>, tagPrefix: String, currentVersionCode: Int): Update? =
        releases.asSequence()
            .filter { !it.draft && !it.prerelease }
            .mapNotNull { release ->
                val versionCode = versionCodeOf(release.tag, tagPrefix) ?: return@mapNotNull null
                val apk = release.assets.firstOrNull { it.name.endsWith(".apk", ignoreCase = true) }
                    ?: return@mapNotNull null
                Update(versionCode, release.title.ifBlank { release.tag }, apk)
            }
            .filter { it.versionCode > currentVersionCode }
            .maxByOrNull { it.versionCode }
}
