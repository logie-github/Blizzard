package com.logie.blizz.game

import java.io.File

/**
 * What OctoWoW's client (1.18.1, build 7272: a vanilla 1.12 client underneath) needs before it starts, in the
 * folder that came over from the World of Warcraft app (`games/wow_octowow/files/turtle/client`). Ported from
 * the WoW app: `realmlist.wtf` next to WoW.exe (a 1.12 client reads it there, unlike
 * 3.3.5a's `Data/<locale>/`), with the patch list too (the client's own files name its old servers for both), and
 * `WTF/Config.wtf` (the realm by name, the screen, the intro off, the account in the login box). Every other
 * setting stays. Plain Kotlin, unit-tested.
 */
object OctoClientSetup {
    /** The realm's name in the client's realm list. It was "Tortoise WoW" in the files that came over ([OLD_REALM_NAME]). */
    const val REALM_NAME = "OctoWoW"
    const val OLD_REALM_NAME = "Tortoise WoW"
    const val EXE = "WoW.exe"
    const val VERSION = "1.18.1"

    fun values(width: Int, height: Int, accountName: String?): Map<String, String> = buildMap {
        put("realmList", "127.0.0.1")
        put("patchList", "127.0.0.1")
        put("realmName", REALM_NAME)
        put("readTOS", "1")
        put("readEULA", "1")
        put("movie", "0")
        put("gxResolution", "${width}x$height")
        put("hwDetect", "0")
        put("gxWindow", "1")
        put("gxMaximize", "1")
        // The game's cursor shown by the system: taps read it to tell what a click would do.
        put("gxCursor", "1")
        if (!accountName.isNullOrBlank()) put("accountName", accountName)
    }

    /** The client's program by its real name (the export keeps its capitals), or null. */
    fun executable(client: File): File? =
        client.listFiles { f -> f.isFile && f.name.equals(EXE, ignoreCase = true) }?.firstOrNull()

    /** The client is there: its program and its data. */
    fun hasClient(client: File): Boolean = executable(client) != null && File(client, "Data").isDirectory

    /**
     * The client keeps each character's settings (key bindings, macros, add-on settings, layout) in `WTF/Account/<account>/<realm name>/`:
     * a folder still under the old name moves to the new one (never over one that is there), so nothing of a character's is left behind.
     * Returns how many folders moved.
     */
    fun renameRealmFolders(client: File): Int {
        var moved = 0
        File(client, "WTF/Account").listFiles { f -> f.isDirectory }?.forEach { account ->
            val old = File(account, OLD_REALM_NAME)
            val new = File(account, REALM_NAME)
            if (old.isDirectory && !new.exists() && old.renameTo(new)) moved++
        }
        return moved
    }

    /** Writes the realm list and the settings into [client]. */
    fun apply(client: File, width: Int, height: Int, accountName: String?) {
        renameRealmFolders(client)
        write(File(client, "realmlist.wtf"), "set realmlist 127.0.0.1\r\nset patchlist 127.0.0.1\r\n")
        val config = File(client, "WTF/Config.wtf")
        val old = if (config.isFile) config.readText() else ""
        write(config, WowClientSetup.updateConfig(old, values(width, height, accountName)))
    }

    private fun write(file: File, text: String) {
        file.parentFile?.mkdirs()
        val tmp = File(file.parentFile, file.name + ".blizz-tmp")
        tmp.writeText(text)
        if (!tmp.renameTo(file)) { file.writeText(text); tmp.delete() }
    }
}
