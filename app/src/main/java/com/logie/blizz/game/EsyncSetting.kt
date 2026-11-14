package com.logie.blizz.game

/**
 * Wine's esync in a container's environment (`WINEESYNC=1` or `0` among Winlator's space-separated `NAME=value` pairs). Off for
 * World of Warcraft: Forever, whose esync waits failed on the phone ([WindowsRuntime]); on for every other game, as Winlator
 * sets it by default.
 */
object EsyncSetting {
    /** [envVars] with `WINEESYNC` set to 1 ([on]) or 0, added when absent; the other pairs left as they are. */
    fun apply(envVars: String, on: Boolean): String {
        val value = "WINEESYNC=${if (on) 1 else 0}"
        val pairs = envVars.split(' ').filter { it.isNotBlank() }
        val replaced = pairs.map { if (it.startsWith("WINEESYNC=")) value else it }
        return (if (pairs.any { it.startsWith("WINEESYNC=") }) replaced else replaced + value).joinToString(" ")
    }
}
