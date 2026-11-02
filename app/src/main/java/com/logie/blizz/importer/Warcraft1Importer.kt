package com.logie.blizz.importer

import java.io.File

/**
 * Warcraft: Orcs & Humans from GOG (the Windows build with its DOSBox files: WAR.EXE, DATA\*.WAR),
 * played natively by Stratagus (War1gus) after war1tool converts the files. From the installed GOG
 * folder, a zip or other archive of it, or GOG's offline installer (setup .exe with its .bin parts).
 * See [WargusImporter].
 */
class Warcraft1Importer(conversion: ConversionTools? = null) : WargusImporter(conversion) {
    override val gameId = "warcraft"
    override val title = "Warcraft: Orcs & Humans"
    override val game = WargusGame.WAR1
    override val what = "Warcraft: Orcs & Humans"
    override val products = listOf("WAR1")
    override val required = listOf("DATA/DATA.WAR")
    override val installerName = Regex("(?i)^setup.*(orcs|warcraft_?1\\b|warcraft_?i\\b)")

    override val prompt = "Select your Warcraft: Orcs & Humans files from GOG: the installed game's folder, a zip of it, or the offline installer (the setup .exe with its .bin files in the same folder)."

    override fun isRoot(names: Set<String>): Boolean =
        "data/" in names && ("war.exe" in names || "war1.cue" in names) && "install.mpq" !in names && "support/" !in names

    override fun looseRoot(dir: File): File? {
        val data = dir.walkTopDown().maxDepth(14).firstOrNull { it.isFile && it.name.equals("DATA.WAR", true) } ?: return null
        val folder = data.parentFile ?: return null
        return if (folder.name.equals("data", true)) folder.parentFile else null
    }

    override fun fixCase(root: File) {
        CaseFix.apply(root, "DATA")
        val data = File(root, "DATA")
        for (f in data.listFiles().orEmpty().filter { it.isFile }) CaseFix.apply(data, f.name.uppercase())
        for (name in listOf("WAR.EXE", "WAR1.CUE", "WAR1.BIN")) CaseFix.apply(root, name)
    }
}
