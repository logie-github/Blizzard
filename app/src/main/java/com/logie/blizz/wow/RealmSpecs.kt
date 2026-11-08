package com.logie.blizz.wow

import java.io.File

/** The two realms [ClassicRealmController] runs: OctoWoW's, and Legion's (a plain LegionCore 7.3.5 server, nothing of its own on top). */
internal object RealmSpecs {
    /** OctoWoW (1.18.1, build 7272). Its own database on 3311, the login server on 3724, the world on 8090. */
    val OCTO = RealmSpec(
        realm = Realm.OCTO,
        name = "OctoWoW",
        folder = "games/wow_octowow/files/turtle",
        loginProgram = "realmd", worldProgram = "mangosd",
        loginLog = "realmd.out", worldLog = "mangosd.out",
        worldConf = "mangosd.conf",
        loginPorts = listOf(3724),
        allPorts = listOf(3311, 3724, 8090),
        pidFiles = listOf("mangosd.pid", "realmd.pid", "mysqld.pid"),
        ready = Regex("World server is up and running"),
        fatal = listOf(
            Regex("Correct \\*\\.map files not found|is non-compatible version|vmap file .* is missing") to
                "The world server's data is missing or from another client (maps, vmaps). Make it again in the World of Warcraft app and export again.",
            Regex("DB AutoUpdater FAILED|Migration .* failed to apply") to "A database update failed. See games/wow_octowow/files/turtle/logs/mangosd.out.",
            Regex("Cannot connect to world database|database not specified") to "The world server couldn't reach its database.",
            Regex("required \\*\\.dbc files") to "The DBC files are missing or don't fit this server.",
        ),
        worldMinutes = 45,
        imported = { it.isOctoImported() },
        noData = "OctoWoW's server data (dbc and maps) isn't in the imported files. Make it in the World of Warcraft app's OctoWoW game files, then export again.",
        realmSql = { address ->
            "tw_logon" to "UPDATE realmlist SET name = '${com.logie.blizz.game.OctoClientSetup.REALM_NAME}', address = '$address', port = 8090, realmbuilds = '7272' WHERE id = 1;"
        },
        accountSql = { name, password -> RealmAccounts.octoSql(name, password)?.let { "tw_logon" to it } },
        worldSettings = { vmaps, mmaps ->
            mapOf(
                "vmap.enableLOS" to flag(vmaps), "vmap.enableHeight" to flag(vmaps), "vmap.enableIndoorCheck" to flag(vmaps),
                "mmap.enabled" to flag(mmaps), "GameType" to "0", "PlayerLimit" to "0",
            )
        },
    )

    /**
     * Legion: LegionCore 7.3.5 (client build 26972). Its own database on 3312, the Battle.net login server on 1119 with its
     * REST login on 8081, the world on 8095 and instances on 8096. The client is patched for this realm once
     * (`ctl.sh patch-client`: the patched program and the certificate bundle it trusts).
     */
    val LEGION = RealmSpec(
        realm = Realm.LEGION,
        name = "Legion",
        folder = "games/wow_legion/files/felsong",
        loginProgram = "bnetserver", worldProgram = "worldserver",
        loginLog = "bnetserver.out", worldLog = "worldserver.out",
        worldConf = "worldserver.conf",
        loginPorts = listOf(1119, 8081),
        allPorts = listOf(3312, 1119, 8081, 8095, 8096),
        pidFiles = listOf("worldserver.pid", "bnetserver.pid", "mysqld.pid"),
        ready = Regex("\\(worldserver-daemon\\) ready\\.\\.\\.|World initialized in"),
        fatal = listOf(
            Regex("required \\*\\.db2 files|not found or not compatible|Incorrect DataDir value") to
                "The world server's data is missing or from another client (db2 files). Make it again in the World of Warcraft app and export again.",
            Regex("Map file '[^']*' is from an incompatible|map file .* does not exist|Correct \\*\\.map files not found|vmap file .* is missing") to
                "The world server's maps are missing or from another version. Make them again in the World of Warcraft app and export again.",
            Regex("Applying of file .* failed|Could not update the .* database|Could not populate the .* database") to
                "A database update failed. See games/wow_legion/files/felsong/logs/worldserver.out.",
            Regex("DatabasePool .* NOT opened|not specified in configuration file|Cannot connect to") to "The world server couldn't reach its database.",
        ),
        worldMinutes = 60,
        imported = { it.isLegionImported() },
        noData = "Legion's server data (dbc and maps) isn't in the imported files. Make it in the World of Warcraft app's Legion game files, then export again.",
        realmSql = { address ->
            "auth" to "UPDATE realmlist SET name = 'Legion', address = '$address', localAddress = '127.0.0.1', port = 8095, gamePort = 8096, " +
                "gamebuild = 26972, flag = 0 WHERE id = 1;"
        },
        accountSql = { name, password -> RealmAccounts.legionSql(name, password)?.let { "auth" to it } },
        worldSettings = { vmaps, mmaps ->
            mapOf(
                "GameType" to "0", "DungeonFinder.DebugJoin" to "1", "Warden.Enabled" to "0",
                "vmap.enableLOS" to flag(vmaps), "vmap.enableHeight" to flag(vmaps), "vmap.enableIndoorCheck" to flag(vmaps),
                "mmap.enablePathFinding" to flag(mmaps),
            )
        },
        // The Battle.net server tells the client where its REST login is.
        otherConfs = { address -> mapOf("bnetserver.conf" to mapOf("LoginREST.ExternalAddress" to address, "LoginREST.LocalAddress" to "127.0.0.1")) },
        // Legion's ctl.sh sets no PidFile for these two (ChromieCraft's and OctoWoW's do): without one an orphaned server is never found, and the next start says its ports are taken.
        pidConfs = mapOf("bnetserver.conf" to "bnetserver.pid", "worldserver.conf" to "worldserver.pid"),
        extra = listOf("Patching the game for this realm" to { layout -> patchClientArgs(layout) }),
    )

    private fun flag(on: Boolean) = if (on) "1" else "0"

    /** The client's program by its real name (the export keeps its capitals), or null. */
    fun clientFile(client: File, name: String): File? =
        client.listFiles { f -> f.isFile && f.name.equals(name, ignoreCase = true) }?.firstOrNull()

    /** Where the connection patcher leaves the certificate bundle the patched client trusts (HOME is the realm's folder). */
    fun certBundle(layout: WowLayout) =
        File(layout.root, ".wine/drive_c/users/Public/Application Data/Blizzard Entertainment/Battle.net/Cache/web_cert_bundle")

    /** `patch-client <Wow-64.exe>` when the client isn't patched for this realm yet (no patched program or no bundle), else null. */
    fun patchClientArgs(layout: WowLayout): List<String>? {
        val patched = clientFile(layout.client, "Wow-64_Patched.exe")
        if (patched != null && certBundle(layout).isFile) return null
        val exe = clientFile(layout.client, "Wow-64.exe") ?: return null
        return listOf("patch-client", exe.path)
    }
}

/** [RealmSpecs] is internal to the realm code; the game code asks for the one thing it needs of it here. */
object RealmSpecsAccess {
    fun certBundle(layout: WowLayout): File = RealmSpecs.certBundle(layout)
}
