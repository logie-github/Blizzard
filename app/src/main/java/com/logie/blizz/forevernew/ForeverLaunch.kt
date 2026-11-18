package com.logie.blizz.forevernew

import com.logie.blizz.game.WowClientSetup
import com.logie.blizz.importer.LibraryEntry
import java.io.File

/**
 * Everything the client needs to start against Forever's own realm inside the app's Winlator, written new from upstream's
 * Windows launch script (repack/Play-WoWForever.ps1) and setup (repack/make-certs.ps1):
 *
 *  - `_forever_/WTF/ForeverLauncher.wtf`: a copy of the player's Config.wtf with `SET portal "trinity.actual.battle.net"`
 *    (their own Config.wtf is not changed), the screen, and the language the installation has;
 *  - `tools/foreverkey` (`foreverkey.exe`, copied beside the game program): starts `Wow.exe -config ForeverLauncher.wtf` and
 *    writes the server's login public key into the client's key table for region group 8 (its settings: `foreverkey.cfg`);
 *  - the portal name resolves to this phone through the games' own runtime hosts file ([com.logie.blizz.game.Offline.hosts]),
 *    never Android's;
 *  - the realm's own root CA is added to the games' Windows root store ([WineCerts]).
 *
 * Each is checked here on a desktop with the phone's own Wine, except the real client (not available here): see
 * docs/forever/README.md.
 */
object ForeverLaunch {
    /** The library entry's `clientVersion` of this realm's client (told apart from Wrath+ "3.3.5a", OctoWoW and Legion). */
    const val VERSION = "forever"
    const val KEEPER = "foreverkey.exe"
    const val CONFIG_NAME = "ForeverLauncher.wtf"
    /** The login public key stock TrinityCore uses (the default of upstream's script), and the region group the world server announces (Network.EnterEncryptedModeRegionGroup). */
    const val PUBLIC_KEY = "02596F0D0C061A8B30745988FD72C59E29EC367FB0F341F28E0F08D037BAFC69"
    const val REGION_GROUP = 8
    const val ASSET = "foreverkey.exe"

    fun product(client: File) = File(client, "_forever_")

    /** The language the installation has: English when `.build.info` lists it (or lists none), else the first it lists. */
    fun textLocale(buildInfo: String): String {
        val have = Regex("""\b([a-z]{2}[A-Z]{2}) text\?""").findAll(buildInfo).map { it.groupValues[1] }.distinct().toList()
        return if (have.isEmpty() || "enUS" in have) "enUS" else have.first()
    }

    fun settings(width: Int, height: Int, locale: String): Map<String, String> = mapOf(
        "portal" to ForeverConfig.PORTAL, "textLocale" to locale,
        "gxWindow" to "1", "gxMaximize" to "1", "gxWindowedResolution" to "${width}x$height", "gxFullscreenResolution" to "${width}x$height",
    )

    /** The text of ForeverLauncher.wtf from the player's Config.wtf (or none yet). */
    fun launcherWtf(config: String, width: Int, height: Int, locale: String): String = WowClientSetup.updateConfig(config, settings(width, height, locale))

    fun keeperConfig(): String = "client=Wow.exe\nconfig=$CONFIG_NAME\nkey=$PUBLIC_KEY\ngroup=$REGION_GROUP\n"

    /** The client's own program by its real name in `_forever_`. */
    fun program(client: File): String = product(client).listFiles { f -> f.isFile && f.name.equals("Wow.exe", ignoreCase = true) }?.firstOrNull()?.name ?: "Wow.exe"

    /** Writes the wtf and the keeper's settings; copies the keeper in ([keeperBytes]). Returns an error text or null. */
    fun prepare(client: File, width: Int, height: Int, keeperBytes: () -> ByteArray?): String? {
        val dir = product(client)
        if (!dir.isDirectory) return "The client's _forever_ folder is missing."
        val wtfDir = File(dir, "WTF").apply { mkdirs() }
        val base = File(wtfDir, "Config.wtf").takeIf { it.isFile }?.readText().orEmpty()
        val own = File(wtfDir, CONFIG_NAME).takeIf { it.isFile }?.readText()
        val locale = textLocale(File(client, ".build.info").takeIf { it.isFile }?.readText().orEmpty())
        File(wtfDir, CONFIG_NAME).writeText(launcherWtf(own ?: base, width, height, locale))
        File(dir, "foreverkey.cfg").writeText(keeperConfig().replace("client=Wow.exe", "client=${program(client)}"))
        // folders the download made twice, in two cases of letters, are one folder to the game
        runCatching { com.logie.blizz.forevernew.tact.TactInstaller.mergeCaseFolders(dir) }
        // which product the program is (Blizzard's installer writes it; the client finds no installation without it)
        com.logie.blizz.forevernew.tact.TactInstaller.writeFlavor(client, dir.name,
            com.logie.blizz.forevernew.tact.TactInstaller.productOf(File(client, ".build.info").takeIf { it.isFile }?.readText().orEmpty()) ?: ForeverClientDownload.PRODUCT)
        val bytes = keeperBytes() ?: return "foreverkey.exe isn't in this build of the app."
        val target = File(dir, KEEPER)
        if (!target.isFile || target.length() != bytes.size.toLong() || !target.readBytes().contentEquals(bytes)) target.writeBytes(bytes)
        return null
    }

    /** The entry Winlator starts: the keeper, which starts the client. */
    fun entry(client: File, title: String = "World of Warcraft: Forever") =
        com.logie.blizz.game.WowPlay.launchEntry(product(client), KEEPER, title).copy(clientVersion = VERSION)

    /** Adds the realm's root to the games' Windows root store; false if it isn't there or was already. */
    fun trustRealm(rootPem: File, systemReg: File): Boolean =
        rootPem.isFile && WineCerts.install(systemReg, WineCerts.pemToDer(rootPem.readText()))
}
