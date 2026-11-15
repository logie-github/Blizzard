
package com.logie.blizz.game

/**
 * Keeps the games off Blizzard's servers. The games' runtime (Wine on the phone) looks names up
 * with its own C library, which reads `etc/hosts` and `etc/nsswitch.conf` in the runtime's folder
 * (their paths are compiled into it); neither file comes with the runtime. With [nsswitch] the
 * hosts file comes first, and [hosts] sends Battle.net's, the patch servers' and Blizzard's other
 * names nowhere (0.0.0.0): nothing a game does can reach them, whatever its menus offer. Plain
 * Kotlin, unit-tested.
 */
object Offline {
    /** The names Blizzard's games and launcher reach (Battle.net, patches, downloads, news). */
    val BLOCKED: List<String> = listOf(
        "battle.net", "www.battle.net", "us.battle.net", "eu.battle.net", "kr.battle.net", "tw.battle.net", "cn.battle.net",
        "uswest.battle.net", "useast.battle.net", "europe.battle.net", "asia.battle.net",
        "us.actual.battle.net", "eu.actual.battle.net", "kr.actual.battle.net", "cn.actual.battle.net", "tw.actual.battle.net",
        "us.patch.battle.net", "eu.patch.battle.net", "kr.patch.battle.net", "tw.patch.battle.net", "cn.patch.battle.net",
        "us.version.battle.net", "eu.version.battle.net", "kr.version.battle.net",
        "account.battle.net", "us.account.battle.net", "eu.account.battle.net", "kr.account.battle.net",
        "launcher.battle.net", "us.launcher.battle.net", "eu.launcher.battle.net",
        "telemetry-in.battle.net", "us.telemetry.battle.net", "eu.telemetry.battle.net",
        "blizzard.com", "www.blizzard.com", "cdn.blizzard.com", "us.cdn.blizzard.com", "eu.cdn.blizzard.com",
        "kr.cdn.blizzard.com", "level3.blizzard.com", "level3.ssl.blizzard.com", "dist.blizzard.com",
        "blzddist1-a.akamaihd.net", "blzddist2-a.akamaihd.net", "blzddist3-a.akamaihd.net",
        "bnetcmsus-a.akamaihd.net", "bnetcmseu-a.akamaihd.net", "bnetproduct-a.akamaihd.net",
        "classic.battle.net", "war3.blizzard.com",
        // Diablo II and StarCraft's own Battle.net gateways and the legacy patch servers.
        "uswest.battle.net", "useast.battle.net", "asia.battle.net", "europe.battle.net",
        "ftp.blizzard.com", "us.logon.battle.net", "eu.logon.battle.net", "kr.logon.battle.net",
    ).distinct()

    /** The runtime's hosts file: this phone by its name, and with [blocked] Blizzard's names nowhere. */
    fun hosts(blocked: Boolean): String = buildString {
        append("127.0.0.1\tlocalhost\n")
        append("::1\tlocalhost\n")
        if (blocked) {
            append("# Blizzard: its servers, out of reach.\n")
            for (name in BLOCKED) append("0.0.0.0\t").append(name).append('\n')
        }
    }

    /** The hosts file first, before any name server. */
    fun nsswitch(): String = "hosts: files dns\n"
}
