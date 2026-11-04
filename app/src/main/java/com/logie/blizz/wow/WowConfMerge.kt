package com.logie.blizz.wow

import java.io.File

/**
 * Config files copied from an older package lack the settings a newer program reads (the imported
 * `dbimport.conf` had no `Updates.ExceptionShutdownDelay`, so dbimport stopped: "Missing property").
 * `ctl.sh configure` only copies a `.conf.dist` when the live file is missing and never adds what's new
 * in a later one, so after it the settings a file lacks are added from its `.dist`, with the dist's
 * own values and every setting already there (the person's, and the ones configure sets) left as it
 * is. Plain Kotlin, unit-tested.
 */
object WowConfMerge {
    private val KEY = Regex("^\\s*([A-Za-z0-9_.]+)\\s*=")

    /** The active (uncommented) settings of config [text], by key. */
    fun keys(text: String): Set<String> = text.lineSequence().mapNotNull { KEY.find(it)?.groupValues?.get(1) }.toSet()

    /** [conf] with the settings [dist] has and it doesn't added at the end; the lines added. */
    fun missing(conf: String, dist: String): List<String> {
        val have = keys(conf)
        val seen = HashSet<String>()
        return dist.lineSequence().filter { line ->
            val key = KEY.find(line)?.groupValues?.get(1) ?: return@filter false
            key !in have && seen.add(key)
        }.map { it.trim() }.toList()
    }

    /** Adds to [conf] what [dist] has that it lacks; the number of settings added (0 if the files aren't there). */
    fun merge(conf: File, dist: File): Int {
        if (!conf.isFile || !dist.isFile) return 0
        val text = conf.readText()
        val add = missing(text, dist.readText())
        if (add.isEmpty()) return 0
        val temp = File(conf.parentFile, ".${conf.name}.tmp")
        temp.writeText(text.trimEnd('\n') + "\n\n# Added from ${dist.name} (settings this file lacked):\n" + add.joinToString("\n", postfix = "\n"))
        if (!temp.renameTo(conf)) { conf.writeText(temp.readText()); temp.delete() }
        return add.size
    }

    /** Every realm's configs and the modules': each gets what its `.dist` in `server/etc` has that it lacks. Returns the settings added. */
    fun mergeAll(layout: WowLayout): Int {
        var added = 0
        for (etc in listOf(layout.etc, layout.etcRemix)) {
            // dbimport asks for this one by name (its .dist has it commented out), and says so on every run.
            added += ensure(File(etc, "dbimport.conf"), "Updates.ExceptionShutdownDelay", "10000")
            for (name in listOf("worldserver", "dbimport", "authserver")) {
                added += merge(File(etc, "$name.conf"), File(layout.server, "etc/$name.conf.dist"))
            }
            File(layout.server, "etc/modules").listFiles { f -> f.name.endsWith(".conf.dist") }?.forEach { dist ->
                added += merge(File(File(etc, "modules"), dist.name.removeSuffix(".dist")), dist)
            }
        }
        return added
    }

    /** [key] = [value] in [conf] when the file has no active line for it; 1 when added. */
    fun ensure(conf: File, key: String, value: String): Int {
        if (!conf.isFile) return 0
        val text = conf.readText()
        if (Regex("^\\s*" + Regex.escape(key) + "\\s*=", RegexOption.MULTILINE).containsMatchIn(text)) return 0
        conf.writeText(text.trimEnd('\n') + "\n\n$key = $value\n")
        return 1
    }
}
