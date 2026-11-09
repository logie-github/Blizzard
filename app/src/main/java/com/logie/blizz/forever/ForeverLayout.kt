package com.logie.blizz.forever

import android.content.Context
import com.logie.blizz.wow.WowLayout
import java.io.File

/**
 * Where the Forever realm lives: `files/forever/` (its own folder, apart from the imported WoW
 * realms under `files/games/`). The server package unpacks to `files/forever/server`, built to run
 * from exactly that path.
 */
class ForeverLayout(val root: File) {
    val server = File(root, "server")
    val ctl = File(server, "ctl.sh")
    val data = File(root, "data")
    val databases = File(root, "mysql")
    val logs = File(root, "logs")
    val run = File(root, "run")
    /** The game's map data, made from the client (dbc and maps at least). */
    fun hasServerData() = listOf("dbc", "maps").all { File(data, it).list()?.isNotEmpty() == true }

    /** The Forever client folder (the one with .build.info and _forever_), copied or installed here. */
    val client = File(root, "client")

    /** Whether the client is present: its `.build.info`, `Data` and `_forever_`, and a program to start. */
    fun hasClient() = File(client, ".build.info").isFile && File(client, "Data").isDirectory && clientExe() != null

    /** The client's build (from its `.build.info`), or null when it can't be read. */
    fun clientBuild(): Int? = runCatching { ForeverCtl.clientBuild(File(client, ".build.info").readText()) }.getOrNull()

    /** The program to start: the Forever Launcher if the user placed one (it sets the server key), else the client exe. */
    fun clientExe(): File? {
        val names = listOf(
            "ForeverLauncher.exe", "Forever Launcher.exe", "forever-launcher.exe",
            "_forever_/Wow.exe", "_forever_/WowB.exe", "Wow.exe", "WowB.exe", "World of Warcraft Launcher.exe",
        )
        return names.map { File(client, it) }.firstOrNull { it.isFile }
    }

    /** A [WowLayout] view of the same folder, for the shared process runner's leftover cleanup. */
    val wowLayout get() = WowLayout(root, root)

    fun log(name: String) = File(logs, "$name.log")

    companion object {
        fun of(context: Context) = ForeverLayout(File(context.applicationContext.filesDir, "forever"))
    }
}
