package com.logie.blizz.game

import com.logie.blizz.importer.deleteTree
import java.io.File

/**
 * What Legion's 7.3.5 client (build 26972) needs before it starts, in the folder that came over from the World of
 * Warcraft app (`games/wow_legion/files/felsong/client`: the folder keeps the name the export gave it). Ported from the WoW app: a 7.x
 * client has no realmlist.wtf, its `portal` in `WTF/Config.wtf` is the Battle.net server it connects to (the patched
 * program takes a plain host), and the realm list comes from that server. The screen, the intro off, the account's
 * e-mail in the login box. Every other setting stays. Plain Kotlin, unit-tested.
 */
object LegionClientSetup {
    const val VERSION = "7.3.5"
    const val EXE = "Wow-64.exe"
    const val PATCHED_EXE = "Wow-64_Patched.exe"
    const val PORTAL = "127.0.0.1"

    /** The client's graphics switch: Direct3D 9, which DXVK runs. It overrides Config.wtf's. */
    const val GRAPHICS_ARGUMENT = "-d3d"

    /** The Box64 Legion's start-up protection needs (Winlator patch 0007, scripts/build-box64.sh). */
    const val BOX64 = "0.4.4-legion"

    fun values(width: Int, height: Int, accountName: String?): Map<String, String> = buildMap {
        put("portal", PORTAL)
        // Its language, always: with none the client asks with a dialog whose OK sets the portal to the region's code.
        put("textLocale", "enUS")
        put("audioLocale", "enUS")
        put("readTOS", "1")
        put("readEULA", "1")
        put("readTerminationWithoutNotice", "1")
        put("readContest", "1")
        put("movie", "0")
        put("playIntroMovie", "7")
        put("checkAddonVersion", "0")
        put("gxWindow", "1")
        put("gxMaximize", "1")
        put("gxWindowedResolution", "${width}x$height")
        put("gxFullscreenResolution", "${width}x$height")
        // The client keeps its gxApi only with videoOptionsVersion 15, else resets it to auto at every start.
        put("gxApi", "D3D9")
        put("videoOptionsVersion", "15")
        put("seenConfigurationWarnings", "65535")
        put("maxFPS", "60")
        put("maxFPSBk", "5")
        put("gxCursor", "1")
        put("hwDetect", "0")
        if (!accountName.isNullOrBlank()) put("accountName", accountName)
    }

    /** What the game starts with the first time: Legion's "Fair" preset in the world, the lowest in raids, no anti-aliasing. */
    val FIRST_START = mapOf(
        "graphicsQuality" to "3", "RAIDgraphicsQuality" to "1", "MSAAQuality" to "0",
        "ffxAntiAliasingMode" to "0", "renderscale" to "1", "gxVSync" to "0",
    )

    /** [FIRST_START]'s settings that [config] (Config.wtf's text) has none of: what was chosen in the game stays. */
    fun firstStart(config: String): Map<String, String> =
        FIRST_START.filterKeys { key -> !Regex("(?im)^\\s*SET\\s+${Regex.escape(key)}\\s").containsMatchIn(config) }

    /** Where a Windows program finds the Battle.net certificate bundle the patched client checks its login server against. */
    val CERT_BUNDLE_IN_PREFIX = listOf(
        "ProgramData/Blizzard Entertainment/Battle.net/Cache/web_cert_bundle",
        "users/Public/Application Data/Blizzard Entertainment/Battle.net/Cache/web_cert_bundle",
    )

    fun executable(client: File, name: String): File? =
        client.listFiles { f -> f.isFile && f.name.equals(name, ignoreCase = true) }?.firstOrNull()

    /** The client is there: its program (patched or not) and its data. */
    fun hasClient(client: File): Boolean =
        (executable(client, EXE) != null || executable(client, PATCHED_EXE) != null) && File(client, "Data").isDirectory

    /** Writes the settings into [client]'s WTF/Config.wtf. */
    fun apply(client: File, width: Int, height: Int, accountName: String?) {
        val config = File(client, "WTF/Config.wtf")
        val text = if (config.isFile) config.readText() else ""
        val updated = WowClientSetup.updateConfig(text, firstStart(text) + values(width, height, accountName))
        config.parentFile?.mkdirs()
        val tmp = File(config.parentFile, config.name + ".blizz-tmp")
        tmp.writeText(updated)
        if (!tmp.renameTo(config)) { config.writeText(updated); tmp.delete() }
    }

    /**
     * The certificate bundle the connection patcher wrote ([bundle]) into the game's Windows ([driveC] is the container's
     * `.wine/drive_c`): both of the places a Windows program may look for ProgramData in a Wine prefix. Returns how many
     * copies it made (0 when there is no bundle: the client isn't patched for the realm).
     */
    fun installCertificateBundle(bundle: File, driveC: File): Int {
        if (!bundle.isFile) return 0
        var copies = 0
        for (path in CERT_BUNDLE_IN_PREFIX) {
            val target = File(driveC, path)
            target.parentFile?.mkdirs()
            bundle.copyTo(target, overwrite = true)
            copies++
        }
        return copies
    }
}
