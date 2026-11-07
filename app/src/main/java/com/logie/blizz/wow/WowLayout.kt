package com.logie.blizz.wow

import android.content.Context
import java.io.File

/**
 * Where the imported World of Warcraft app's data lives in Blizzard: `files/games/wow/files/` holds
 * what the other app had in its `files/` (WowImporter), so the folder names are the WoW app's own
 * (`server`, `etc`, `etc-remix`, `mysql`, `data`, `client`, ...). `files/games/wow/.export/` holds
 * the export's `export.json` and `prefs/<name>.json`.
 *
 * Plain Kotlin on a [root] folder, so tests use a temporary one.
 */
class WowLayout(val root: File, val exportDir: File) {
    val server = File(root, "server")
    val ctl = File(server, "ctl.sh")
    /** The copy of ctl.sh Blizzard runs (see [WowCtl]); ctl.sh itself stays as imported. */
    val blizzCtl = File(server, "ctl.blizz.sh")
    /** Scripts Blizzard writes for programs the server starts by itself (see [WowCtl.mariadbWrapper]). */
    val blizzBin = File(server, "blizz")
    val etc = File(root, "etc")
    val etcRemix = File(root, "etc-remix")
    val data = File(root, "data")
    val client = File(root, "client")
    val databases = File(root, "mysql")
    val logs = File(root, "logs")
    val run = File(root, "run")
    /** Records the prefix the text files were last rewritten to ([WowPathRewrite]). */
    val rewriteMarker = File(root, ".blizz-paths")

    val manifest = File(exportDir, "export.json")
    val prefsDir = File(exportDir, "prefs")

    /** The imported realm is there to start: the server's programs, its script and the databases. */
    fun isImported(): Boolean =
        ctl.isFile && File(server, "bin/worldserver").isFile && File(server, "bin/mariadbd").isFile && File(databases, "mysql").isDirectory

    /** OctoWoW's realm is there to start: Tortoise-WoW's programs (mangosd, realmd), its script and its databases. */
    fun isOctoImported(): Boolean =
        ctl.isFile && File(server, "bin/mangosd").isFile && File(server, "bin/realmd").isFile &&
            File(server, "bin/mariadbd").isFile && File(databases, "mysql").isDirectory

    /** Legion's realm is there to start: LegionCore's programs (worldserver, bnetserver), its script and its databases. */
    fun isLegionImported(): Boolean =
        ctl.isFile && File(server, "bin/worldserver").isFile && File(server, "bin/bnetserver").isFile &&
            File(server, "bin/mariadbd").isFile && File(databases, "mysql").isDirectory

    /** The world server's data (dbc and maps at least, from the client). */
    fun hasServerData(): Boolean = listOf("dbc", "maps").all { File(data, it).list()?.isNotEmpty() == true }

    /** musl's loader in the server's lib folder (`ld-musl-aarch64.so.1`), which runs the programs. */
    fun loader(): File? =
        File(server, "lib").listFiles { f -> f.name.startsWith("ld-musl-") && f.name.endsWith(".so.1") }?.minByOrNull { it.name }

    fun realmLogs(realm: Realm) = if (realm == Realm.REMIX) File(logs, "remix") else logs

    companion object {
        /** The imported OctoWoW (`games/wow_octowow`): the export's `turtle` folder is the realm's root. */
        fun octo(context: Context): WowLayout {
            val game = File(context.applicationContext.filesDir, "games/wow_octowow")
            return WowLayout(File(game, "files/turtle"), File(game, ".export"))
        }

        /** The imported Legion (`games/wow_legion`): the export's `felsong` folder is the realm's root. */
        fun legion(context: Context): WowLayout {
            val game = File(context.applicationContext.filesDir, "games/wow_legion")
            return WowLayout(File(game, "files/felsong"), File(game, ".export"))
        }

        fun of(context: Context): WowLayout {
            val game = File(context.applicationContext.filesDir, "games/wow")
            return WowLayout(File(game, "files"), File(game, ".export"))
        }
    }
}

/** The phone's two Wrath realms: one auth server and set of accounts, one world server running at a time. */
enum class Realm(
    /** The realm's name for `ctl.sh` (its configs and databases) and as the WoW app saved it. */
    val key: String,
    val id: Int,
    val displayName: String,
    val port: Int,
    val charactersDatabase: String,
) {
    CHROMIE("main", 1, "ChromieCraft", 8085, "acore_characters"),
    REMIX("remix", 2, "Wrath Remix", 8086, "acore_characters_remix"),
    /** OctoWoW's realm (Tortoise-WoW, its own database on 3311 and world port 8090); the login port 3724 is shared, so one realm runs at a time. */
    OCTO("octo", 3, "OctoWoW", 8090, "tw_char"),
    /** Legion's realm (LegionCore 7.3.5: its own database on 3312, Battle.net on 1119, the world on 8095); no port shared with the others. */
    LEGION("legion", 4, "Legion", 8095, "characters");

    companion object {
        const val AUTH_PORT = 3724
        const val DATABASE_PORT = 3310
        fun byKey(key: String?): Realm? = entries.firstOrNull { it.key == key }
    }
}
