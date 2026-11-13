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

    /** The last line with text in [log] (its end only is read), shortened for a status line; null when there is none. */
    fun lastLine(log: File, limit: Int = 70): String? = runCatching {
        if (!log.isFile) return null
        java.io.RandomAccessFile(log, "r").use { file ->
            val length = file.length()
            val tail = ByteArray(minOf(length, 4096L).toInt())
            file.seek(length - tail.size)
            file.readFully(tail)
            String(tail).lines().map { it.trim() }.lastOrNull { it.isNotEmpty() }?.replace(ANSI, "")?.take(limit)
        }
    }.getOrNull()

    private val ANSI = Regex("\u001B\\[[0-9;]*[A-Za-z]")

    /** What the client left behind about a start that went wrong: a title for the report, and the text. */
    class ClientStop(val title: String, val text: String, val at: Long)

    /**
     * What the game itself wrote about stopping, since [since] (a file time): its newest crash file
     * (a `.txt` in its `Errors` folder: the exception and where), else the failures in its storage log (`Logs/Tact.log`, where an
     * installation it calls damaged is explained). Null when it left neither: a start that went well, or one that
     * said nothing. [game] is the client's `_forever_` folder.
     */
    fun clientStop(game: File, since: Long): ClientStop? {
        val crash = File(game, "Errors").listFiles()
            ?.filter { it.isFile && it.name.endsWith(".txt", ignoreCase = true) && it.lastModified() > since }
            ?.maxByOrNull { it.lastModified() }
        if (crash != null) {
            val text = runCatching { crash.readText().removePrefix("\uFEFF") }.getOrDefault("")
            val summary = text.lineSequence().map { it.trim() }
                .firstOrNull { it.startsWith("Exception:") || it.startsWith("ERROR #") || it.startsWith("Fatal") }
                ?: "The game wrote a crash file"
            return ClientStop(summary.take(160), text.take(6000), crash.lastModified())
        }
        val tact = File(File(game, "Logs"), "Tact.log").takeIf { it.isFile && it.lastModified() > since } ?: return null
        val failures = runCatching { tact.readLines() }.getOrDefault(emptyList())
            .filter { line -> listOf("failed to", "needs repair", "needsrepair", "truncated", "corrupt").any { it in line.lowercase() } }
            .distinctBy { it.substringAfter("  ") }
        if (failures.isEmpty()) return null
        return ClientStop("The game's storage log has failures", failures.takeLast(40).joinToString("\n").take(6000), tact.lastModified())
    }

    /**
     * Whether a crash file's text ([ClientStop.text]) says the game's own protection ended it (`<ExceptionType> Security
     * Crash`): seen on the desktop rig some 50 seconds after the Forever Launcher started the game, each time, and never
     * with the game started by itself. Not a damaged installation: nothing the app can repair.
     */
    fun isSecurityCrash(text: String): Boolean =
        text.lineSequence().any { it.trim().equals("<ExceptionType> Security Crash", ignoreCase = true) }

    /**
     * The crash file the game has written since [since] and finished ([settleMs] without a change, at [now]): the newest
     * `.txt` in its `Errors` folder ([errors]), else null. After writing it the game stayed up on the rig, its last frame
     * on the screen and its program hung, so the game screen asks this while the game runs and leaves when there is one.
     */
    fun settledCrash(errors: File, since: Long, now: Long, settleMs: Long = 3000): File? =
        errors.listFiles()
            ?.filter { it.isFile && it.name.endsWith(".txt", ignoreCase = true) && it.lastModified() > since }
            ?.maxByOrNull { it.lastModified() }
            ?.takeIf { now - it.lastModified() >= settleMs }

    /**
     * The client's `WTF/Config.wtf` with its login portal set to this phone (`SET portal "127.0.0.1"`): the line
     * replaced if there is one, added if not; the rest of the person's settings kept. A language is set where
     * there is none (the downloaded client is enUS): without it the game opens a Windows list box to ask, before
     * anything else, at every start until one is chosen.
     */
    fun withLocalPortal(config: String?): String {
        val line = "SET portal \"127.0.0.1\""
        val lines = config.orEmpty().lines().filter { it.isNotBlank() }
        val kept = lines.filterNot { it.trim().startsWith("SET portal ", ignoreCase = true) }
        val locale = listOf("textLocale", "audioLocale")
            .filter { name -> kept.none { it.trim().startsWith("SET $name ", ignoreCase = true) } }
            .map { "SET $it \"enUS\"" }
        return (kept + locale + line).joinToString("\n", postfix = "\n")
    }

    /**
     * [config] (the client's `WTF/Config.wtf`) set so the game opens on its login screen ready for the password: the
     * account's e-mail filled in ([account], `accountName`: what *Remember Account* keeps), and none of the first-start
     * screens in front of it (the intro movie, the Screen Narrator question, the photosensitivity notice). Seen on the
     * desktop rig with client 70888 (13 November 2026): with these the login screen is up with the e-mail in its box and
     * the cursor in the password's; without them the e-mail box is empty and has the cursor (the app types only the
     * password), the intro plays, and the narrator's question takes the Enter. The game reads them from `Config.wtf`
     * also when the Forever Launcher starts it with its own file (`-config ForeverLauncher.wtf`), which the account name
     * in that file does not do. The rest of the settings kept; the first-start ones only where none is set.
     */
    fun withLoginReady(config: String?, account: String): String {
        val forced = mapOf("accountName" to account)
        val unlessSet = linkedMapOf(
            "playIntroMovie" to "1",
            "showScreenNarrationDialog" to "0",
            "accessibilityScreenNarrationEnabled" to "0",
            "showPhotosensitivityWarning" to "0",
        )
        fun name(line: String) = Regex("^\\s*SET\\s+(\\S+)\\s", RegexOption.IGNORE_CASE).find(line)?.groupValues?.get(1)?.lowercase()
        val lines = config.orEmpty().lines().filter { it.isNotBlank() }
        val forcedNames = forced.keys.map { it.lowercase() }.toSet()
        val kept = lines.filterNot { name(it) in forcedNames }
        val present = kept.mapNotNull { name(it) }.toSet()
        val added = unlessSet.filterKeys { it.lowercase() !in present }.map { (k, v) -> "SET $k \"$v\"" }
        val accountLine = forced.map { (k, v) -> "SET $k \"${v.replace("\"", "")}\"" }
        return (kept + added + accountLine).joinToString("\n", postfix = "\n")
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
