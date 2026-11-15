package com.logie.blizz.forevernew

import java.io.File

/**
 * Recognises a complete, user-owned WoW Forever installation and says exactly why another folder isn't one. The Windows
 * Battle.net installer is not a client file and nothing here downloads a client: Karrz doesn't ship the game and no
 * authorised Battle.net download is implemented (see docs/forever-new.md), so the app's one client step is "Import & Install".
 *
 * What is checked: `.build.info` at the installation's root (its Version and Product columns), the shared CASC `Data`
 * folder beside it, the `_forever_` product folder, and the build number against Karrz's `client-builds.txt`.
 * UNVERIFIED against a real installation: the exact Product value Battle.net writes for Forever (the documented
 * product code is `WoWF`; other known products are refused, an unknown one is accepted only with `_forever_` present),
 * and the program's file name inside `_forever_`.
 */
object ForeverClient {
    sealed class Result {
        data class Ok(val root: File, val build: Int, val version: String, val exe: File?) : Result()
        data class Rejected(val reason: String) : Result()
    }

    private val OTHER_PRODUCTS = setOf("wow", "wow_classic", "wow_classic_era", "wow_classic_ptr", "wowt", "wowb", "wow_beta", "wowz", "wowclassic", "wow_anniversary")

    /** The builds of Karrz's `client-builds.txt` text: one number per line, `#` comments, the preferred build first. */
    fun parseBuilds(text: String): List<Int> =
        text.lineSequence().map { it.trim() }.filter { it.isNotEmpty() && !it.startsWith("#") }.mapNotNull { it.toIntOrNull() }.toList()

    /** `.build.info`: pipe-separated, a header line of `Name!TYPE:len` columns, then rows. Returns the rows by column name. */
    fun parseBuildInfo(text: String): List<Map<String, String>> {
        val lines = text.lineSequence().map { it.trimEnd('\r') }.filter { it.isNotBlank() }.toList()
        if (lines.size < 2) return emptyList()
        val header = lines.first().split('|').map { it.substringBefore('!').trim() }
        return lines.drop(1).map { row -> row.split('|').let { cells -> header.indices.associate { header[it] to cells.getOrElse(it) { "" } } } }
    }

    private fun child(dir: File, name: String): File? = dir.listFiles { f -> f.name.equals(name, ignoreCase = true) }?.firstOrNull()

    /** The installation root for a selected folder: the folder itself, or its parent when `_forever_` was chosen. */
    fun findRoot(selected: File): File? {
        if (child(selected, ".build.info") != null) return selected
        if (selected.name.equals("_forever_", ignoreCase = true)) selected.parentFile?.takeIf { child(it, ".build.info") != null }?.let { return it }
        return selected.listFiles { f -> f.isDirectory }?.firstOrNull { child(it, ".build.info") != null && child(it, "_forever_") != null }
    }

    fun inspect(selected: File, supported: List<Int>): Result {
        val root = findRoot(selected) ?: return Result.Rejected(
            "No .build.info was found in ${selected.name}. Select the complete World of Warcraft installation folder (the one holding .build.info, Data and _forever_).")
        val forever = child(root, "_forever_")
        val buildInfo = child(root, ".build.info")!!
        val rows = parseBuildInfo(buildInfo.readText())
        if (rows.isEmpty()) return Result.Rejected(".build.info is empty or unreadable.")
        val forRows = rows.filter { r -> r["Product"].orEmpty().lowercase() == "wowf" }
        val row = forRows.firstOrNull() ?: rows.firstOrNull { r ->
            r["Product"].orEmpty().lowercase().let { it.isNotEmpty() && it !in OTHER_PRODUCTS } && forever != null
        } ?: return Result.Rejected("This installation is ${rows.firstOrNull()?.get("Product") ?: "another product"}, not WoW Forever. " +
            "Wrath, Classic and Legion clients can't be used as Forever's client.")
        val version = row["Version"].orEmpty()
        val build = version.substringAfterLast('.').toIntOrNull()
            ?: return Result.Rejected("The version '$version' in .build.info has no build number.")
        if (forever == null || !forever.isDirectory) return Result.Rejected("The _forever_ folder is missing; the installation is incomplete or not WoW Forever.")
        if (child(root, "Data")?.isDirectory != true) return Result.Rejected("The shared Data (CASC) folder is missing next to _forever_. Copy the complete World of Warcraft folder.")
        if (supported.isNotEmpty() && build !in supported) return Result.Rejected(
            "Client build $build isn't supported by this server. Supported builds: ${supported.joinToString()}. Update or install a listed build.")
        val exe = forever.listFiles { f -> f.isFile && f.name.lowercase().let { it.startsWith("wow") && it.endsWith(".exe") } }?.minByOrNull { it.name }
        return Result.Ok(root, build, version, exe)
    }
}
