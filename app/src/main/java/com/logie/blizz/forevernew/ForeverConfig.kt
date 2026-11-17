package com.logie.blizz.forevernew

/**
 * The configuration the app writes for Forever, from Karrz's own keys (worldserver.conf.dist, playerbot.conf.dist,
 * examples/karrz-realm.conf). Secrets go in the generated config files (app-private storage), never into logs or the package.
 */
object ForeverConfig {
    /** A bot profile: what the phone's memory allows, never Karrz's desktop 450 bots / ~9 GB. */
    data class BotProfile(
        val name: String, val worldBots: Boolean, val maxBots: Int, val perPlayer: Int, val city: Int, val zone: Int,
        val rssBudgetMb: Int, val auctionSeller: Boolean, val auctionBuyer: Boolean,
    )

    const val REALM_ID = 70
    /** The name the client logs in to (upstream doc/ForeverSetup.md); it must resolve to this phone inside the game's own Wine only. */
    const val PORTAL = "trinity.actual.battle.net"

    /** Karrz's estimate (INSTALL-BOTS.md): ~2.9 GB for the server and ~4 MB per awake bot. */
    const val SERVER_BASE_MB = 2900
    const val PER_BOT_MB = 4
    /** The game (Wine + Box64), the database and Android's own use: an ESTIMATE, to be replaced by measurement on a phone. */
    const val GAME_AND_DB_MB = 3500
    const val ANDROID_RESERVE_MB = 2000

    /** Memory left for bots after everything else, from the phone's total RAM. Negative when the realm itself can't fit. */
    fun botBudgetMb(totalRamMb: Int): Int = totalRamMb - ANDROID_RESERVE_MB - GAME_AND_DB_MB - SERVER_BASE_MB

    /**
     * [preset]: "auto" (from RAM), "off", "low", "medium", "high"; a chosen preset is still capped by what the RAM leaves.
     * [worldBots] and [auction] are the two switches the page shows.
     */
    fun profile(totalRamMb: Int, preset: String = "auto", worldBots: Boolean = true, auction: Boolean = true): BotProfile {
        val room = (botBudgetMb(totalRamMb) / PER_BOT_MB).coerceAtLeast(0)
        val wanted = when (preset) { "low" -> 40; "medium" -> 120; "high" -> 300; "off" -> 0; else -> if (room >= 300) 120 else if (room >= 60) 40 else 0 }
        val maxBots = minOf(wanted, room)
        val on = worldBots && preset != "off" && maxBots >= 10
        val name = when { !on -> "off"; maxBots <= 50 -> "low"; maxBots <= 150 -> "medium"; else -> "high" }
        return BotProfile(
            name = name, worldBots = on, maxBots = if (on) maxBots else 0,
            perPlayer = if (on) (maxBots * 3 / 4).coerceAtLeast(8) else 0,
            city = if (on) (maxBots / 2).coerceAtLeast(8) else 0, zone = if (on) (maxBots / 4).coerceAtLeast(5) else 0,
            // The server stops adding bots when its memory passes this (Playerbot.World.RssBudgetMb).
            rssBudgetMb = SERVER_BASE_MB + maxBots * PER_BOT_MB + 600,
            auctionSeller = auction, auctionBuyer = auction,
        )
    }

    /** The settings the app sets in worldserver.conf (the rest stay the `.conf.dist`'s own: its loggers and defaults). */
    fun worldserverValues(p: Params): Map<String, String> = LinkedHashMap<String, String>().apply {
        // Upstream (doc/ForeverSetup.md): the client only accepts realm 70; auth.realmlist must hold the same id.
        line("RealmID", REALM_ID.toString())
        line("DataDir", q(p.dataDir)); line("LogsDir", q(p.logsDir)); line("SourceDirectory", q(p.sourceDir))
        line("PidFile", q(p.pidFile))
        line("WorldServerPort", ForeverPorts.WORLD.toString()); line("BindIP", q("127.0.0.1"))
        line("LoginDatabaseInfo", q("127.0.0.1;${ForeverPorts.DATABASE};${p.dbUser};${p.dbPassword};auth"))
        line("WorldDatabaseInfo", q("127.0.0.1;${ForeverPorts.DATABASE};${p.dbUser};${p.dbPassword};world"))
        line("CharacterDatabaseInfo", q("127.0.0.1;${ForeverPorts.DATABASE};${p.dbUser};${p.dbPassword};characters"))
        line("HotfixDatabaseInfo", q("127.0.0.1;${ForeverPorts.DATABASE};${p.dbUser};${p.dbPassword};hotfixes"))
        // Base data is imported by the app; the servers only apply updates (an empty-database AutoSetup would load the dev base).
        line("Updates.EnableDatabases", "15"); line("Updates.AutoSetup", "0")
        line("MySQLExecutable", q(p.mysqlClient))
        // Required by upstream for the supported clients.
        line("Network.EnterEncryptedModeRegionGroup", "8")
        line("Network.SkipBuildAuthKeyCheck", "1")
        line("Expansion", "0")
        // The core's own freeze watch off: it ends the server ("World Thread hangs for 60029 ms, forcing a crash!", SIGSEGV) when the
        // world's loop has not turned for a minute. On a phone that minute passes without a fault: Android stops the app's programs
        // while the app is out of sight, and the bots' first set-up holds the loop for long (the phone, 16 November 2026: the world
        // loaded, its console up, then that line).
        line("MaxCoreStuckTime", "0")
        // Comma-separated; bnetserver.conf must hold the same list, and each build needs a row in auth.build_info.
        p.realmAlsoAccept.takeIf { it.isNotEmpty() }?.let { line("Realm.AlsoAcceptBuilds", q(it.joinToString(","))) }
    }

    fun bnetserverValues(p: Params): Map<String, String> = LinkedHashMap<String, String>().apply {
        line("BindIP", q("127.0.0.1")); line("BattlenetPort", ForeverPorts.BNET.toString())
        line("LoginREST.Port", ForeverPorts.REST.toString())
        // Both names are what the client is told to connect to; the certificate is only valid for the portal name.
        line("LoginREST.ExternalAddress", p.portal); line("LoginREST.LocalAddress", p.portal)
        line("Realm.CfgContentSetID", "137")
        p.realmAlsoAccept.takeIf { it.isNotEmpty() }?.let { line("Realm.AlsoAcceptBuilds", q(it.joinToString(","))) }
        line("CertificatesFile", q(p.certFile)); line("PrivateKeyFile", q(p.keyFile))
        line("LogsDir", q(p.logsDir)); line("SourceDirectory", q(p.sourceDir)); line("PidFile", q(p.bnetPidFile))
        line("LoginDatabaseInfo", q("127.0.0.1;${ForeverPorts.DATABASE};${p.dbUser};${p.dbPassword};auth"))
        line("Updates.EnableDatabases", "1"); line("Updates.AutoSetup", "0")
        line("MySQLExecutable", q(p.mysqlClient))
    }

    /** `worldserver.conf.d/zz-9-local.conf`: Karrz's realm rules (INSTALL-BOTS.md, examples/karrz-realm.conf) and the phone's bot limits. */
    fun localValues(bots: BotProfile): Map<String, String> = LinkedHashMap<String, String>().apply {
        line("Playerbot.Enable", "1")
        line("Playerbot.SharedDatabase", q("playerbot"))
        line("Playerbot.World.Enable", if (bots.worldBots) "1" else "0")
        if (bots.worldBots) {
            line("Playerbot.World.MaxBots", bots.maxBots.toString()); line("Playerbot.World.BotsPerPlayer", bots.perPlayer.toString())
            line("Playerbot.World.CityBots", bots.city.toString()); line("Playerbot.World.ZoneBots", bots.zone.toString())
            line("Playerbot.World.RssBudgetMb", bots.rssBudgetMb.toString())
        }
        line("AuctionHouseBot.Seller.Enabled", if (bots.auctionSeller) "1" else "0")
        line("AuctionHouseBot.Buyer.Enabled", if (bots.auctionBuyer) "1" else "0")
        // The vanilla realm rules of Karrz's own configuration.
        line("Expansion", "0"); line("MaxPlayerLevel", "60"); line("Load.Locales", "0")
        // the world server names it as missing from its config when it isn't there (found on the rig); upstream's realm config has it at 0
        line("Classic.Hardcore", "0")
        line("Instance.IgnoreAttunement", "1"); line("Instance.AhnQirajGatesOpen", "1")
    }

    data class Params(
        val dataDir: String, val logsDir: String, val sourceDir: String, val pidFile: String, val bnetPidFile: String,
        val dbUser: String, val dbPassword: String, val mysqlClient: String, val portal: String,
        val certFile: String, val keyFile: String, val realmAlsoAccept: List<Int> = emptyList(),
    )

    private fun q(s: String) = "\"$s\""
    private fun MutableMap<String, String>.line(key: String, value: String) { put(key, value) }

    fun worldserverConf(p: Params) = text(worldserverValues(p))
    fun bnetserverConf(p: Params) = text(bnetserverValues(p))
    fun localConf(bots: BotProfile) = text(localValues(bots))
    private fun text(v: Map<String, String>) = v.entries.joinToString("") { "${it.key} = ${it.value}\n" }

    private val ACTIVE = Regex("^\\s*([A-Za-z0-9_.]+)\\s*=")

    /**
     * [dist] (a `.conf.dist`, whose loggers and defaults the server needs: a file with only the app's settings made it stop with no
     * message, found on the rig) with each of [values] put in place of that key's active line, or added at the end.
     */
    fun edit(dist: String, values: Map<String, String>): String {
        val done = HashSet<String>()
        val lines = dist.lines().map { line ->
            val key = ACTIVE.find(line)?.groupValues?.get(1)
            if (key != null && key in values && done.add(key)) "$key = ${values.getValue(key)}" else line
        }
        val added = values.filterKeys { it !in done }.entries.joinToString("") { "${it.key} = ${it.value}\n" }
        return lines.joinToString("\n").trimEnd('\n') + "\n" + (if (added.isEmpty()) "" else "\n# Set by the app:\n$added")
    }
}
