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

    /** A [WowLayout] view of the same folder, for the shared process runner's leftover cleanup. */
    val wowLayout get() = WowLayout(root, root)

    fun log(name: String) = File(logs, "$name.log")

    companion object {
        fun of(context: Context) = ForeverLayout(File(context.applicationContext.filesDir, "forever"))
    }
}
