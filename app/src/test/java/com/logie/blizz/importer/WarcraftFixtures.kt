package com.logie.blizz.importer

import java.io.File

/** Stand-ins shaped like GOG's Warcraft I and II files, and a fake data tool. None is a game file. */
object WarcraftFixtures {
    /** GOG's Warcraft: Orcs & Humans: WAR.EXE, DATA\*.WAR, WAR1.CUE/BIN. [lower]: as innoextract --lowercase writes them. */
    fun wc1(dir: File, lower: Boolean = false): File {
        fun n(s: String) = if (lower) s.lowercase() else s
        Fixtures.pe(File(dir, n("WAR.EXE")), "1.0.0.0")
        File(dir, n("WAR1.CUE")).writeText("FILE \"WAR1.BIN\" BINARY")
        File(dir, n("WAR1.BIN")).writeBytes(ByteArray(64))
        for (f in listOf("DATA.WAR", "CAVE1.WAR", "MUSIC.WAR")) File(dir, n("DATA/$f")).apply { parentFile!!.mkdirs() }.writeBytes(ByteArray(32) { 7 })
        return dir
    }

    /** GOG's Warcraft II: Battle.net Edition. */
    fun wc2(dir: File, lower: Boolean = false, tomes: Int = 4): File {
        fun n(s: String) = if (lower) s.lowercase() else s
        Fixtures.pe(File(dir, n("Warcraft II BNE.exe")), "2.0.0.0")
        Fixtures.mpq(File(dir, n("Install.mpq")))
        Fixtures.mpq(File(dir, n("War2Dat.mpq")))
        for (i in 1..tomes) File(dir, n("Support/TOMES/TOME.$i")).apply { parentFile!!.mkdirs() }.writeBytes(ByteArray(32) { 3 })
        return dir
    }

    /** A fake war1tool/wartool: records what it was given, then writes the scripts, converted data and the marker (unless [fail]). */
    class FakeTools(var code: Int = 0, var writeMarker: Boolean = true, val output: List<String> = listOf("Extracting data", "Done")) : ConversionTools {
        var game: WargusGame? = null
        var sourceNames: List<String> = emptyList()
        var calls = 0

        override fun convert(game: WargusGame, source: File, staging: File, cancel: CancelToken, onLine: (String) -> Unit): Tools.Result {
            calls++
            this.game = game
            this.sourceNames = source.walkTopDown().filter { it.isFile }.map { it.relativeTo(source).invariantSeparatorsPath }.sorted().toList()
            File(staging, "scripts").mkdirs()
            File(staging, "scripts/${game.key}.lua").writeText("-- scripts")
            File(staging, "graphics").mkdirs()
            File(staging, "graphics/tileset.png").writeBytes(ByteArray(16))
            output.forEach(onLine)
            if (writeMarker && code == 0) File(staging, WargusConversion.MARKER).writeText("")
            return Tools.Result(code, output.takeLast(12))
        }
    }
}
