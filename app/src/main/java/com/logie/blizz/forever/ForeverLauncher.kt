package com.logie.blizz.forever

import java.io.File

/**
 * The Forever Launcher (the user's `WoWForeverLauncher.exe`): a WinForms program that points the game client
 * at a local realm and writes the realm's game-server key into the running client, which is what gets the
 * client past its "server identity check" when it enters the world. It needs the .NET runtime ([WineMono]).
 *
 * The launcher keeps small files in a `config` folder **beside itself** (`<client folder>\config`: read off the desktop
 * rigs, 12 November 2026; an earlier version of this seeded `C:\windows\config`, which the launcher never reads, so
 * the phone showed its Welcome question). With [seedConfig]'s files it opens straight on **This PC (own server)**,
 * shows this app's realm as *Online* and its PLAY NOW starts the game without a question first.
 *
 * Seen on the desktop rigs with launcher 0.1.35 and client 1.60.1.70888, on the realm's own arm64 build under qemu:
 * *Online / READY*, PLAY NOW starts `Wow.exe -config ForeverLauncher.wtf`. **Open:** on that rig the game started this
 * way ended itself some 50 seconds later, each of three times, with its own crash report (`_forever_/Errors`,
 * `0xC00000E5`); the same client started without the launcher ran on. Not run on a phone.
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

    /** The launcher's config folder: beside the launcher, in the client folder. */
    fun configDir(clientDir: File) = File(clientDir, "config")

    /** Where an earlier version of this app seeded the config (the launcher never read it there). */
    private fun oldConfigDir(driveC: File) = File(driveC, "windows/config")

    /** The realm this app runs, as the launcher's `server.json` names its "This PC (own server)" entry. */
    const val HOST = "127.0.0.1"
    const val PORTAL = "trinity.actual.battle.net"
    const val LOGIN_PORT = 1119
    /** The Forever realm's world port (`ctl.sh`: WORLD_PORT). The launcher's own default is 8085, where it found nothing. */
    const val WORLD_PORT = 8105
    const val REGION_GROUP = 8
    /** The realm's public identity key as the launcher's own default entry has it (the stock key of the realm's source). */
    const val PUBLIC_KEY = "02596F0D0C061A8B30745988FD72C59E29EC367FB0F341F28E0F08D037BAFC69"

    /** The game folder as the launcher wants it: the one with `Wow.exe` (F: is this app's `files/forever`). */
    const val GAME_FOLDER = "F:\\client\\_forever_"

    /** `server.json`: the launcher's own-server entry with this realm's world port (without it: "World: no answer", "Starting" for ever). */
    fun serverJson(): String =
        "{\"name\":\"This PC (own server)\",\"host\":\"$HOST\",\"portal\":\"$PORTAL\",\"publicKey\":\"$PUBLIC_KEY\"," +
            "\"regionGroup\":$REGION_GROUP,\"loginPort\":$LOGIN_PORT,\"worldPort\":$WORLD_PORT}\n"

    /**
     * The files this app owns in the launcher's config folder, written at every start:
     * - `launcher-mode.txt` = `own`: no "How do you want to play?" screen.
     * - `client.txt`: the game folder ([GAME_FOLDER]; with `F:\client` the launcher asks for the folder at PLAY NOW).
     * - `server.json`: this realm, with its world port.
     */
    val FILES: Map<String, String> = linkedMapOf(
        "launcher-mode.txt" to "own",
        "client.txt" to GAME_FOLDER,
        "server.json" to serverJson(),
    )

    /** The launcher's own settings file, made only when there is none (the launcher writes it itself afterwards). */
    const val SETTINGS = "launcher-settings.txt"

    /** The line the launcher itself adds to Windows' hosts file after asking ("Windows must be told that ... is 127.0.0.1"). */
    const val HOSTS_LINE = "$HOST $PORTAL # wow-forever-join"

    /**
     * Seeds the launcher: [FILES] into `<client>/config` (always: they are this app's, and a wrong one stops the start),
     * its settings when there are none, and the realm's name in the container's Windows hosts file ([driveC] is
     * `<container>/.wine/drive_c`), so its first PLAY NOW does not stop at a question. The config an earlier version
     * left in `C:\windows\config` is removed.
     */
    fun seedConfig(clientDir: File, driveC: File) {
        val dir = configDir(clientDir).apply { mkdirs() }
        for ((name, content) in FILES) {
            val file = File(dir, name)
            if (!file.isFile || file.readText() != content) runCatching { file.writeText(content) }
        }
        File(dir, SETTINGS).let { if (!it.isFile) runCatching { it.writeText("lang=en\n") } }
        runCatching { seedHosts(driveC) }
        oldConfigDir(driveC).deleteRecursively()
    }

    /** Adds [HOSTS_LINE] to the container's Windows hosts file unless the realm's name is already in it. */
    internal fun seedHosts(driveC: File) {
        val hosts = File(driveC, "windows/system32/drivers/etc/hosts")
        val text = if (hosts.isFile) hosts.readText() else ""
        val has = text.lineSequence().any { line ->
            val words = line.substringBefore('#').trim().split(Regex("\\s+"))
            words.size >= 2 && words.drop(1).any { it.equals(PORTAL, ignoreCase = true) }
        }
        if (has) return
        hosts.parentFile?.mkdirs()
        hosts.writeText(text + (if (text.isEmpty() || text.endsWith("\n")) "" else "\r\n") + HOSTS_LINE + "\r\n")
    }

    /** Removes the launcher's config (this app's files and the launcher's own) so the next Play writes it afresh (a repair). */
    fun clearConfig(clientDir: File, driveC: File?) {
        configDir(clientDir).deleteRecursively()
        if (driveC != null) oldConfigDir(driveC).deleteRecursively()
    }

    /** Deletes every placed launcher from a client folder (a repair re-asks the person to pick it). */
    fun removePlaced(clientDir: File) {
        NAMES.forEach { File(clientDir, it).delete() }
    }
}
