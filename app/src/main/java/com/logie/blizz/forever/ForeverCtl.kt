package com.logie.blizz.forever

import com.logie.blizz.wow.WowCtl
import java.io.File

/**
 * How the Forever realm's `ctl.sh` is run. The programs have this app's own path baked in as their
 * ELF interpreter, so nothing is rewritten (unlike the imported WoW realms): `ctl.sh` is run as-is
 * with Android's shell, and `FILES` points it at the realm folder.
 *
 * Pure (no Android): unit-tested.
 */
object ForeverCtl {
    /** The pid files the realm's programs write, for ending leftovers after the app was killed. */
    val PID_FILES = listOf("worldserver.pid", "bnetserver.pid", "mysqld.pid")

    fun command(layout: ForeverLayout, vararg args: String): WowCtl.Command = WowCtl.Command(
        argv = listOf("/system/bin/sh", layout.ctl.path) + args,
        env = mapOf(
            "FILES" to layout.root.path,
            "TZ" to WowCtl.posixTimeZone(),
            // Android's shell takes TMPDIR only if the folder exists when it starts (see [prepare]); else it writes
            // its here-documents to /data/local, which an app can't.
            "TMPDIR" to File(layout.run, "tmp").path,
        ),
        directory = layout.run,
    )

    /** Forever's product code in a client's `.build.info`. */
    const val PRODUCT = "wowf"

    /**
     * The client's build number from its `.build.info` (a `|`-separated table whose header names the columns, e.g.
     * `Version!STRING:0` = `1.15.8.70862`): the active Forever row's, else any Forever row's, else the first row's.
     * Null when there's no readable version. The realm offers the client's own build (the client lists no other).
     */
    fun clientBuild(buildInfo: String): Int? {
        val lines = buildInfo.lineSequence().map { it.trim() }.filter { it.isNotEmpty() && !it.startsWith("#") }.toList()
        if (lines.size < 2) return null
        val header = lines[0].split('|').map { it.substringBefore('!').trim().lowercase() }
        val version = header.indexOf("version").takeIf { it >= 0 } ?: return null
        val product = header.indexOf("product")
        val active = header.indexOf("active")
        val rows = lines.drop(1).map { line -> line.split('|').map { it.trim() } }.filter { it.size > version }
        fun isForever(row: List<String>) = product < 0 || row.getOrNull(product).equals(PRODUCT, ignoreCase = true)
        val row = rows.firstOrNull { isForever(it) && (active < 0 || it.getOrNull(active) == "1") }
            ?: rows.firstOrNull(::isForever)
            ?: rows.firstOrNull()
            ?: return null
        return row[version].substringAfterLast('.').toIntOrNull()
    }

    /** What a client folder must hold: `.build.info`, its CASC `Data` (the server's map data is read from it) and `_forever_` (the game). */
    val CLIENT_PARTS = listOf(".build.info", "Data", "_forever_")

    /**
     * Which folder of a picked tree is the client: the picked folder itself when it holds [CLIENT_PARTS], else the one
     * child that does (a folder above the client was picked). [children] lists a folder's entries (lower-cased names
     * compared). Returns the path of names from the picked folder (empty = itself), or null when neither is a client.
     */
    fun <T> findClient(root: T, children: (T) -> List<Pair<String, T>>): List<T>? {
        fun isClient(node: T): Boolean {
            val names = children(node).map { it.first.lowercase() }.toSet()
            return CLIENT_PARTS.all { it.lowercase() in names }
        }
        if (isClient(root)) return emptyList()
        return children(root).firstOrNull { isClient(it.second) }?.let { listOf(it.second) }
    }

    /**
     * The client's `WTF/Config.wtf` with its login portal set to this phone (`SET portal "127.0.0.1"`): the line
     * replaced if there is one, added if not; the rest of the person's settings kept.
     */
    fun withLocalPortal(config: String?): String {
        val line = "SET portal \"127.0.0.1\""
        val lines = config.orEmpty().lines().filter { it.isNotBlank() }
        val kept = lines.filterNot { it.trim().startsWith("SET portal ", ignoreCase = true) }
        return (kept + line).joinToString("\n", postfix = "\n")
    }

    /** The folders ctl.sh needs before its shell starts: its temporary folder (TMPDIR) and the logs. */
    fun prepare(layout: ForeverLayout) {
        File(layout.run, "tmp").mkdirs()
        layout.logs.mkdirs()
    }

    /** The package has no executable bits after a plain unpack: set them on the programs, the loader and ctl.sh. */
    fun makeExecutable(layout: ForeverLayout): Int {
        var changed = 0
        val targets = buildList {
            add(layout.ctl)
            File(layout.server, "bin").listFiles()?.let(::addAll)
            File(layout.server, "lib").listFiles()?.let(::addAll)
        }
        for (file in targets) if (file.isFile && !file.canExecute() && file.setExecutable(true, false)) changed++
        return changed
    }
}
