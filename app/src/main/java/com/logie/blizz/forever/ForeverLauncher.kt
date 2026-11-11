package com.logie.blizz.forever

import java.io.File

/**
 * The Forever Launcher (the user's `WoWForeverLauncher.exe`): a WinForms program that points the game client
 * at a local realm and writes the realm's game-server key into the running client, which is what gets the
 * client past its "server identity check" when it enters the world. It needs the .NET runtime ([WineMono]).
 *
 * The launcher reads small text files from `C:\windows\config`; seeding them makes it open straight on its
 * server screen with **This PC (own server)** chosen (127.0.0.1, portal `trinity.actual.battle.net`, region
 * group 8, login port 1119 — the realm this app runs), so there is no menu to answer. Proven on the desktop
 * test rig: with these three files in place the launcher boots to that screen.
 *
 * NOT run on a phone; the pure parts are unit-tested.
 */
object ForeverLauncher {
    /** File names a placed launcher may have (the user's download is `WoWForeverLauncher.exe`). */
    val NAMES = listOf(
        "WoWForeverLauncher.exe", "ForeverLauncher.exe", "Forever Launcher.exe", "forever-launcher.exe",
    )

    /** The launcher file in a client folder, or null when none was placed. */
    fun find(clientDir: File): File? = NAMES.map { File(clientDir, it) }.firstOrNull { it.isFile }

    /** The name a picked launcher file keeps (its own if it is a known launcher name, else the canonical one). */
    fun fileNameFor(picked: String?): String =
        picked?.takeIf { p -> NAMES.any { it.equals(p, ignoreCase = true) } } ?: "WoWForeverLauncher.exe"

    /** The config folder in a container's Windows ([driveC] is `<container>/.wine/drive_c`). */
    private fun configDir(driveC: File) = File(driveC, "windows/config")

    /**
     * The config files that make the launcher open on **This PC (own server)**:
     * - `launcher-mode.txt` = `own`  — skip the "how do you want to play?" screen, go to the server screen.
     * - `client.txt` = `F:\client`   — the game folder (F: is this app's `files/forever`, the client under it).
     * - `launcher-settings.txt` = `lang=en` — a default the launcher otherwise writes itself on first run.
     *
     * The client path is the Windows path the game is reached by: the F: drive ([com.logie.blizz.game.WindowsRuntime.drives]).
     */
    val FILES: Map<String, String> = linkedMapOf(
        "launcher-mode.txt" to "own",
        "client.txt" to "F:\\client",
        "launcher-settings.txt" to "lang=en",
    )

    /** Writes any of [FILES] that is not already there (the launcher's own later writes are kept). */
    fun seedConfig(driveC: File) {
        val dir = configDir(driveC).apply { mkdirs() }
        for ((name, content) in FILES) {
            val file = File(dir, name)
            if (!file.isFile) runCatching { file.writeText(content) }
        }
    }

    /** Removes the seeded config so the next Play writes it afresh (a repair). */
    fun clearConfig(driveC: File) {
        configDir(driveC).deleteRecursively()
    }

    /** Deletes every placed launcher from a client folder (a repair re-asks the person to pick it). */
    fun removePlaced(clientDir: File) {
        NAMES.forEach { File(clientDir, it).delete() }
    }
}
