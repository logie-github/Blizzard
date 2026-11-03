package com.logie.blizz.game

import org.json.JSONObject
import java.io.File

/**
 * What World of Warcraft's 3.3.5a client needs set before it starts, in the folder that came over
 * from the World of Warcraft app (`games/wow/files/client`): where it logs in (`Data/<locale>/realmlist.wtf`),
 * and its own settings (`WTF/Config.wtf`: screen, the realm's name, the account in the login box).
 * Ported from the World of Warcraft app's Game.configureClient and ClientConfig, so the files that
 * came over are used as they are. Every other setting, the add-ons and the characters' saved variables
 * are left as they were: only the lines named here are changed, files are written whole or not at all.
 * Plain Kotlin, unit-tested.
 */
object WowClientSetup {
    /** The client's locale folders in `Data/` (enUS, deDE...). */
    val LOCALE = Regex("[a-z]{2}[A-Z]{2}")

    /** The client's program, and the copy of it the realm's modules' patch needs (the other app makes it). */
    const val EXE = "Wow.exe"
    const val PATCHED_EXE = "WowPatched.exe"

    /** The login server: the realm that Blizzard runs on this phone. */
    const val HOST = "127.0.0.1"

    /** The realm that was last played on, in `files/`: the app's record, kept when the other app made it. */
    const val REALM_RECORD = "client-realm"

    private val SET_LINE = Regex("""^\s*SET\s+(\S+)\s+"(.*)"\s*$""", RegexOption.IGNORE_CASE)

    /** The realms' names as the client's realm list shows them (the app's two realms, by key). */
    fun realmName(key: String): String = when (key) {
        "remix" -> "Wrath Remix"
        else -> "ChromieCraft"
    }

    fun realmlist(host: String = HOST) = "set realmlist $host\r\n"

    /** The client is there: its program and its data. */
    fun hasClient(client: File): Boolean = File(client, EXE).isFile && File(client, "Data").isDirectory

    /** Winlator's graphics for the client: the container's own (DXVK), as the World of Warcraft app runs it. */
    fun dxwrapperConfig(): String = ""

    /** The client's language folders in `Data/`. */
    fun locales(client: File): List<String> =
        File(client, "Data").listFiles { f -> f.isDirectory && LOCALE.matches(f.name) }?.map { it.name }?.sorted().orEmpty()

    /**
     * [text] (a Config.wtf, or "" for a new one) with each of [values] set: in place where the
     * setting is already (names are case-insensitive, like the client's), at the end where not.
     * Lines that aren't `SET name "value"` (comments, blank lines in the middle) are kept.
     */
    fun updateConfig(text: String, values: Map<String, String>): String {
        val newline = if ("\r\n" in text || text.isEmpty()) "\r\n" else "\n"
        val wanted = values.mapKeys { it.key.lowercase() }
        val seen = mutableSetOf<String>()
        val lines = text.lines().dropLastWhile { it.isBlank() }.map { line ->
            val match = SET_LINE.matchEntire(line) ?: return@map line
            val name = match.groupValues[1]
            val value = wanted[name.lowercase()] ?: return@map line
            seen += name.lowercase()
            "SET $name \"$value\""
        }
        val added = values.filterKeys { it.lowercase() !in seen }.map { (name, value) -> "SET $name \"$value\"" }
        return (lines + added).joinToString(newline, postfix = newline)
    }

    /** The settings the app owns: where to log in, the screen, and the account in the login box (if known). */
    fun configValues(width: Int, height: Int, realmKey: String, account: String?): Map<String, String> = buildMap {
        put("realmList", HOST)
        put("realmName", realmName(realmKey))
        put("accounttype", "LK")
        put("readTOS", "1")
        put("readEULA", "1")
        put("movie", "0")
        put("gxResolution", "${width}x$height")
        // Without this the first start detects the "hardware" and puts its own resolution in place of the screen's.
        put("hwDetect", "0")
        put("gxWindow", "1")
        put("gxMaximize", "1")
        // The game's own cursor shown by the system (the X server draws it), not in the picture.
        put("gxCursor", "1")
        put("stickyTargeting", "1")
        // Add-ons load whatever version of the game they say they're for.
        put("checkAddonVersion", "0")
        if (!account.isNullOrBlank()) put("accountName", account)
    }

    /** The client's cache goes when it starts on another realm than the last time (some quests and items differ). */
    fun mustClearCache(last: String?, now: String): Boolean = (last?.trim()?.ifEmpty { null } ?: "main") != now

    /** What [apply] did, for the log. */
    data class Applied(val realmlists: List<String>, val config: String, val clearedCache: Boolean)

    /**
     * Points [client] at the realm on this phone. [filesDir] is the imported `files/` folder (the
     * realm record is kept there, as the World of Warcraft app keeps it). Never deletes anything but the
     * cache of the realm played on before, which the client rebuilds.
     */
    fun apply(client: File, filesDir: File, width: Int, height: Int, realmKey: String, account: String?): Applied {
        val record = File(filesDir, REALM_RECORD)
        val last = runCatching { record.takeIf { it.isFile }?.readText() }.getOrNull()
        val clear = mustClearCache(last, realmKey)
        if (clear) File(client, "Cache/WDB").deleteRecursively()
        filesDir.mkdirs()
        writeWhole(record, realmKey + "\n")

        val written = mutableListOf<String>()
        val text = realmlist()
        for (locale in locales(client)) {
            val f = File(client, "Data/$locale/realmlist.wtf")
            writeWhole(f, text)
            written += "Data/$locale/realmlist.wtf"
        }
        File(client, "realmlist.wtf").takeIf { it.isFile }?.let { writeWhole(it, text); written += "realmlist.wtf" }

        val config = File(client, "WTF/Config.wtf")
        val old = if (config.isFile) config.readText() else ""
        writeWhole(config, updateConfig(old, configValues(width, height, realmKey, account)))
        return Applied(written, "WTF/Config.wtf", clear)
    }

    /** The account the World of Warcraft app logged in with by itself: its name in the exported `login` preferences. Never the password. */
    fun savedAccount(loginPrefsJson: String?): String? = runCatching {
        JSONObject(loginPrefsJson ?: return null).optJSONObject("name")?.optString("value")?.trim()?.takeIf { it.isNotEmpty() }
    }.getOrNull()

    /** The look the other app had put in the client (`hd_installed` in the exported `mods` preferences): null if none. */
    fun hdInstalled(modsPrefsJson: String?): String? = runCatching {
        JSONObject(modsPrefsJson ?: return null).optJSONObject("hd_installed")?.optString("value")?.takeIf { it.isNotEmpty() && it != "OFF" }
    }.getOrNull()

    /** A module's patch for the game is in its `Data` (they only load in the patched program). */
    fun hasModulePatch(client: File): Boolean {
        val data = File(client, "Data")
        return File(data, "patch-M.MPQ/realm-modules.stamp").isFile || File(data, "patch-Z.MPQ.skyborne").isFile ||
            File(data, "patch-V.MPQ.alliedraces").isFile || File(data, "patch-U.MPQ.worgengoblin").isFile
    }

    /** The program to start: the patched copy while a look or the modules' patch is in and the copy is there, else Wow.exe. */
    fun executable(client: File, modsPrefsJson: String?): String =
        if ((hdInstalled(modsPrefsJson) != null || hasModulePatch(client)) && File(client, PATCHED_EXE).isFile) PATCHED_EXE else EXE

    /** Writes [text] to [file] whole or not at all (a temporary file beside it, then moved over). */
    private fun writeWhole(file: File, text: String) {
        file.parentFile?.mkdirs()
        val tmp = File(file.parentFile, file.name + ".blizz-tmp")
        tmp.writeText(text)
        if (!tmp.renameTo(file)) {
            file.writeText(text)
            tmp.delete()
        }
    }
}
