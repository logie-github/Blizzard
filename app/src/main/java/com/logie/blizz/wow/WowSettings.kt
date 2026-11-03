package com.logie.blizz.wow

import java.io.File
import java.io.IOException

/**
 * The settings the WoW app's `Server.applySettings` writes into the realm's configs before every
 * start, which `ctl.sh configure` doesn't (it only writes paths, databases and the modules'
 * per-realm switches):
 *
 * - the first time (no `etc/.defaults`): the progression system's first brackets and the
 *   playerbots' 50 random bots, idle while nobody plays;
 * - every time, in both realms' `worldserver.conf`: line of sight, height and indoor checks with
 *   `vmaps` in the server's data, and pathfinding with `mmaps` (a config that asks for data the
 *   phone doesn't have makes the world server log errors on every move).
 *
 * Only lines of files that exist are changed (a key the file lacks is added at the end), as the
 * WoW app's `ConfFile` does.
 */
object WowSettings {
    fun apply(layout: WowLayout) {
        val firstTime = File(layout.etc, ".defaults")
        if (!firstTime.exists() && layout.etc.isDirectory) {
            edit(File(layout.etc, "modules/progression_system.conf")) {
                set("ProgressionSystem.Bracket_0", "1")
                set("ProgressionSystem.Bracket_1_19", "1")
            }
            edit(File(layout.etc, "modules/playerbots.conf")) {
                set("Playerbots.MinRandomBots", "50")
                set("Playerbots.MaxRandomBots", "50")
                set("Playerbots.DisabledWithoutRealPlayer", "1")
            }
            firstTime.writeText("1\n")
        }
        val folders = listOf("vmaps", "mmaps").filter { File(layout.data, it).list()?.isNotEmpty() == true }
        for (etc in listOf(layout.etc, layout.etcRemix)) {
            edit(File(etc, "worldserver.conf")) {
                val vmaps = if ("vmaps" in folders) "1" else "0"
                set("vmap.enableLOS", vmaps)
                set("vmap.enableHeight", vmaps)
                set("vmap.enableIndoorCheck", vmaps)
                set("MoveMaps.Enable", if ("mmaps" in folders) "1" else "0")
            }
        }
    }

    private class Conf(text: String) {
        private val lines = text.lines().toMutableList()

        fun set(key: String, value: String) {
            val pattern = Regex("^${Regex.escape(key)}\\s*=")
            val index = lines.indexOfFirst { pattern.containsMatchIn(it) }
            val line = "$key = $value"
            when {
                index >= 0 -> lines[index] = line
                lines.isNotEmpty() && lines.last().isEmpty() -> lines.add(lines.size - 1, line)
                else -> lines.add(line)
            }
        }

        override fun toString() = lines.joinToString("\n")
    }

    private fun edit(file: File, change: Conf.() -> Unit) {
        if (!file.isFile) return
        val before = file.readText()
        val after = Conf(before).apply(change).toString()
        if (after == before) return
        val temp = File(file.path + ".tmp")
        temp.writeText(after)
        if (!temp.renameTo(file)) throw IOException("Couldn't write ${file.name}")
    }
}
