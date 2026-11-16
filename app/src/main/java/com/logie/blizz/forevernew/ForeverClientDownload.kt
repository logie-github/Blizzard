package com.logie.blizz.forevernew

import com.logie.blizz.forevernew.tact.HttpCdn
import com.logie.blizz.forevernew.tact.TactInstaller
import com.logie.blizz.forevernew.tact.TactText
import java.io.File
import java.io.IOException

/**
 * The game client, fetched from Blizzard's own public content servers (the ones the Battle.net app uses; no account is involved),
 * by the app's own installer ([TactInstaller]); nothing of the game is in this app, its repository or Karrz's server package.
 * Product `wowf` is WoW Forever. Staged by Blizzard's own install priorities, each resumable:
 *  - [ESSENTIAL] (priority 0: the programs and the files to reach the login screen, about 0.6 GB for Windows in English);
 *  - [ALL] (the rest: about 47 GB; the server's map data is extracted from it, so the realm waits for it).
 */
object ForeverClientDownload {
    const val PRODUCT = "wowf"
    const val ESSENTIAL = 0
    const val ALL = 2
    /** Windows x64, English text (no voice-over: about 3 GB less to fetch; the game is silent where it would speak). */
    val TAGS = setOf("Windows", "x86_64", "enUS", "US", "text")
    const val ESSENTIAL_BYTES = 700L shl 20
    const val ALL_BYTES = 46L shl 30

    fun spaceNeeded(maxPriority: Int) = (if (maxPriority >= ALL) ALL_BYTES else ESSENTIAL_BYTES) + (512L shl 20)

    /** Blizzard's current build of [PRODUCT] for [region] and the servers to fetch it from. */
    class Release(val buildKey: String, val cdnKey: String, val version: String, val buildId: Int, val hosts: List<String>, val path: String)

    fun release(region: String = "us", fetch: (String) -> String = HttpCdn::fetch): Release {
        val v = TactText.table(fetch("${HttpCdn.VERSIONS}/$PRODUCT/versions")).firstOrNull { it["Region"] == region } ?: throw IOException("Blizzard's servers list no $PRODUCT build")
        val c = TactText.table(fetch("${HttpCdn.VERSIONS}/$PRODUCT/cdns")).firstOrNull { it["Name"] == region } ?: throw IOException("Blizzard's servers list no content servers")
        return Release(v["BuildConfig"]!!, v["CDNConfig"]!!, v["VersionsName"]!!, v["BuildId"]!!.toInt(), httpsHosts(c["Servers"].orEmpty(), c["Hosts"].orEmpty()), c["Path"]!!)
    }

    /**
     * The hosts to fetch from. The `cdns` file's plain Hosts include servers that only speak HTTP (`level3.blizzard.com`); the app only uses
     * HTTPS, so the https entries of its Servers column come first (query strings dropped), the Hosts after them. (Asking an HTTP-only host over
     * HTTPS stalled the first run on a phone, at "Storing the build's metadata".)
     */
    fun httpsHosts(servers: String, hosts: String): List<String> {
        val https = servers.split(' ').filter { it.startsWith("https://") }.map { it.removePrefix("https://").substringBefore('/').substringBefore('?') }
        return (https + hosts.split(' ').filter { it.isNotEmpty() }).filter { it.isNotEmpty() }.distinct()
    }

    /** True if [builds] (the server's supported list) has the build Blizzard currently serves. */
    fun supported(release: Release, builds: List<Int>) = builds.isEmpty() || release.buildId in builds

    /**
     * A client this app downloaded with an earlier version lacks index files the realm's tools read the game through
     * ([TactInstaller.metadataKeys]): fetches the missing ones (133 MB, once). Returns how many were fetched.
     */
    fun repairIndex(root: File, say: (String, Float?) -> Unit): Int {
        val r = release()
        return TactInstaller(HttpCdn(r.hosts, r.path), root, PRODUCT, tags = TAGS).repairMetadata(say)
    }

    /**
     * Downloads (or carries on downloading) the client into [root]. Throws with a plain message on failure. [say] gets (words, share).
     */
    fun download(root: File, maxPriority: Int, builds: List<Int>, say: (String, Float?) -> Unit, cancelled: () -> Boolean = { false }) {
        val free = root.apply { mkdirs() }.usableSpace
        if (free in 1 until spaceNeeded(maxPriority)) throw IOException("Not enough space for the game: ${spaceNeeded(maxPriority) shr 30} GB are needed, ${free shr 30} GB are free.")
        say("Asking Blizzard's servers for the current build", null)
        val r = release()
        if (!supported(r, builds)) throw IOException("Blizzard's current build ${r.buildId} isn't one this server supports (${builds.joinToString()}). The server needs an update first.")
        val installer = TactInstaller(HttpCdn(r.hosts, r.path), root, PRODUCT, tags = TAGS, maxPriority = maxPriority)
        installer.run(installer.build(r.buildKey, r.cdnKey, r.version, r.buildId), say, cancelled)
    }
}
