package com.logie.blizz.forevernew

import java.io.File
import java.io.IOException
import java.util.zip.ZipInputStream

/**
 * The ForeverBots add-on (Karrz's release asset, pinned by SHA-256), installed into the client's own
 * `_forever_/Interface/AddOns/ForeverBots/`. The zip's other add-ons are not installed. A settings file the add-on keeps
 * (`SavedVariables` lives under WTF, not here) is untouched, so a repair or update only replaces the add-on's files.
 */
object ForeverBots {
    const val ADDON = "ForeverBots"

    fun targetFolder(clientRoot: File) = File(clientRoot, "_forever_/Interface/AddOns/$ADDON")

    /** Unpacks only entries of [ADDON] from [zip] into the add-on folder, replacing it; returns the number of files. */
    fun install(zip: File, clientRoot: File): Int {
        val target = targetFolder(clientRoot)
        val staging = File(target.parentFile, "$ADDON.new")
        staging.deleteRecursively(); staging.mkdirs()
        var files = 0
        try {
            ZipInputStream(zip.inputStream().buffered()).use { z ->
                while (true) {
                    val entry = z.nextEntry ?: break
                    val name = entry.name.replace('\\', '/')
                    val rel = relative(name) ?: continue
                    val dest = ForeverPackage.entryTarget(staging, rel) ?: throw IOException("The add-on has an unsafe path: $name")
                    if (entry.isDirectory) { dest.mkdirs(); continue }
                    dest.parentFile?.mkdirs()
                    dest.outputStream().use { z.copyTo(it) }
                    files++
                }
            }
            if (!File(staging, "$ADDON.toc").isFile) throw IOException("The add-on has no $ADDON.toc")
            target.deleteRecursively()
            if (!staging.renameTo(target)) throw IOException("The add-on couldn't be put in place")
        } finally { staging.deleteRecursively() }
        return files
    }

    /** The path inside the ForeverBots folder of a zip entry, or null for anything of another add-on (`ForeverBots/x.lua` or `x/ForeverBots/x.lua`). */
    fun relative(name: String): String? {
        val parts = name.split('/').filter { it.isNotEmpty() }
        val i = parts.indexOf(ADDON)
        if (i < 0 || i == parts.lastIndex && !name.endsWith("/")) return null
        return parts.drop(i + 1).joinToString("/").ifEmpty { null }
    }

    fun isInstalled(clientRoot: File) = File(targetFolder(clientRoot), "$ADDON.toc").isFile
}
