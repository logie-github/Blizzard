package com.logie.blizz.importer

import java.io.File

/**
 * Warcraft II: Battle.net Edition from GOG (Warcraft II BNE.exe, Install.mpq, War2Dat.mpq,
 * Support\TOMES\TOME.1-4), played natively by Stratagus (Wargus) after wartool converts the files.
 * From the installed GOG folder, a zip or other archive of it, or GOG's offline installer (setup
 * .exe with its .bin parts). See [WargusImporter].
 */
class Warcraft2Importer(conversion: ConversionTools? = null) : WargusImporter(conversion) {
    override val gameId = "warcraft2"
    override val title = "Warcraft II: Battle.net Edition"
    override val game = WargusGame.WAR2
    override val what = "Warcraft II: Battle.net Edition"
    override val products = listOf("WAR2")
    override val required = (1..4).map { "Support/TOMES/TOME.$it" } + "Install.mpq"
    override val installerName = Regex("(?i)^setup.*(warcraft_?(ii|2)(?![a-z0-9])|tides|bne)")

    override val prompt = "Select your Warcraft II: Battle.net Edition files from GOG: the installed game's folder, a zip of it, or the offline installer (the setup .exe with its .bin files in the same folder)."

    override fun isRoot(names: Set<String>): Boolean = "install.mpq" in names && "support/" in names

    override fun looseRoot(dir: File): File? {
        val all = dir.walkTopDown().maxDepth(14).toList()
        all.firstOrNull { it.isFile && it.name.equals("Install.mpq", true) }?.let { return it.parentFile }
        all.firstOrNull { it.isFile && it.name.equals("TOME.1", true) && it.parentFile?.name.equals("TOMES", true) }
            ?.let { return it.parentFile?.parentFile?.parentFile }
        return all.firstOrNull { it.isFile && it.name.equals("Warcraft II BNE.exe", true) }?.parentFile
    }

    override fun fixCase(root: File) {
        for (name in listOf("Warcraft II BNE.exe", "Install.mpq", "War2Dat.mpq", "Support", "Support/TOMES")) CaseFix.apply(root, name)
        for (i in 1..4) CaseFix.apply(root, "Support/TOMES/TOME.$i")
    }
}
