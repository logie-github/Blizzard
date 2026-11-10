package com.logie.blizz.game

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.File

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class Wc3SetupTest {
    @get:Rule val tmp = TemporaryFolder()

    // Wc3Arguments (ported from YeaBwoi's Warcraft app) -----------------------------------------

    @Test fun theGameStartsFullscreenIn130sWordsAnd131s() {
        assertEquals("-windowmode fullscreen -nativefullscr", Wc3Arguments.of("", openGl = false))
        // 1.0 to 1.27 know none of those: a window, which the launcher stretches.
        assertEquals("-window", Wc3Arguments.of("", openGl = false, clientVersion = "1.27.0.52240"))
        assertEquals("-window -opengl", Wc3Arguments.of("", openGl = true, clientVersion = "Warcraft III: Reign of Chaos 1.26.0.6401"))
        assertEquals("-windowmode fullscreen -nativefullscr", Wc3Arguments.of("", openGl = false, clientVersion = "1.30.4.11274"))
        assertFalse(Wc3Arguments.isBefore128("1.28.5.7680"))
        assertTrue(Wc3Arguments.isBefore128("1.27.0.52240"))
        assertFalse(Wc3Arguments.isBefore128(null))
        // An entry made before this (1.30's switches stored) gets 1.27's at the start.
        assertEquals("-window", Wc3Arguments.forVersion("-windowmode fullscreen -nativefullscr", "1.27.0.52240"))
        assertEquals("-loadfile Maps/x.w3x -window", Wc3Arguments.forVersion("-loadfile Maps/x.w3x -windowmode fullscreen -nativefullscr", "1.27.0.52240"))
        assertEquals("-windowmode fullscreen -nativefullscr", Wc3Arguments.forVersion("-windowmode fullscreen -nativefullscr", "1.30.4.11274"))
        assertEquals("-window", GameArguments.of("warcraft3_roc", "-windowmode fullscreen -nativefullscr", "", "Warcraft III: Reign of Chaos 1.27.0.52240"))
        assertEquals("-window -opengl", GameArguments.of("warcraft3_tft", "-windowmode fullscreen -nativefullscr", "-opengl", "1.27.0.52240"))
    }

    @Test fun openGlIsAddedAfterThePersonsOwnArguments() {
        assertEquals(
            "-loadfile Maps/x.w3x -windowmode fullscreen -nativefullscr -opengl -graphicsapi OpenGL",
            Wc3Arguments.of("  -loadfile Maps/x.w3x ", openGl = true),
        )
    }

    @Test fun aWindowModeTheyTypedTakesThePlaceOfFullscreen() {
        assertEquals("-window", Wc3Arguments.of("-window", openGl = false))
        assertEquals("-windowmode windowedfullscreen", Wc3Arguments.of("-windowmode windowedfullscreen", openGl = false))
        assertEquals("-FULLSCREEN", Wc3Arguments.of("-FULLSCREEN", openGl = false))
    }

    @Test fun aRendererTheyTypedIsNotDoubled() {
        assertEquals("-d3d -windowmode fullscreen -nativefullscr", Wc3Arguments.of("-d3d", openGl = true))
    }

    @Test fun aMapNamedLikeAFlagIsNotTakenForOne() {
        assertEquals(
            "-loadfile window-maps/a.w3m -windowmode fullscreen -nativefullscr",
            Wc3Arguments.of("-loadfile window-maps/a.w3m", openGl = false),
        )
    }

    // The registry ---------------------------------------------------------------------------------

    @Test fun theRegistryWritesAreTheScreenAndTheLanguage() {
        val writes = Wc3Setup.writes(2400, 1080, locale = "", installDos = null)
        assertEquals(
            listOf(
                Wc3Setup.Write(Wc3Setup.Hive.USER, Wc3Setup.VIDEO, "reswidth", 2400),
                Wc3Setup.Write(Wc3Setup.Hive.USER, Wc3Setup.VIDEO, "resheight", 1080),
                Wc3Setup.Write(Wc3Setup.Hive.USER, Wc3Setup.VIDEO, "windowmode", 2),
                Wc3Setup.Write(Wc3Setup.Hive.USER, Wc3Setup.LAUNCHER, "Locale", "enUS"),
            ),
            writes,
        )
    }

    @Test fun aLanguageAlreadyChosenIsKeptAndTheInstallFolderIsRecordedInBothViews() {
        val writes = Wc3Setup.writes(800, 600, locale = "deDE", installDos = "D:\\warcraft3_roc")
        assertTrue(writes.none { it.name == "Locale" })
        val install = writes.filter { it.hive == Wc3Setup.Hive.SYSTEM && it.name == "InstallPath" }
        assertEquals(2, install.size)
        assertTrue(install.all { it.value == "D:\\warcraft3_roc\\" })
        assertTrue(install.any { it.key.contains("Wow6432Node") })
    }

    /** A registry in memory, standing in for Winlator's editor (which needs its native library, so can't run here). */
    private class Fake : Wc3Setup.Registry {
        val values = HashMap<String, Any>()
        override fun getString(key: String, name: String) = values["$key|$name"] as? String ?: ""
        override fun setString(key: String, name: String, value: String) { values["$key|$name"] = value }
        override fun setDword(key: String, name: String, value: Int) { values["$key|$name"] = value }
        override fun close() = Unit
    }

    @Test fun theWritesAreMadeInTheGamesWindows() {
        val root = tmp.newFolder("container")
        val hives = mapOf("user.reg" to Fake(), "system.reg" to Fake())
        for (name in hives.keys) File(root, ".wine/$name").also { it.parentFile.mkdirs() }.writeText("x")
        val open = { f: File -> hives.getValue(f.name) }
        Wc3Setup.apply(root, 2400, 1080, "D:\\warcraft3_tft\\", open)
        val user = hives.getValue("user.reg").values
        assertEquals(2400, user["${Wc3Setup.VIDEO}|reswidth"])
        assertEquals(1080, user["${Wc3Setup.VIDEO}|resheight"])
        assertEquals(2, user["${Wc3Setup.VIDEO}|windowmode"])
        assertEquals("enUS", user["${Wc3Setup.LAUNCHER}|Locale"])
        assertEquals("D:\\warcraft3_tft\\", hives.getValue("system.reg").values["Software\\Blizzard Entertainment\\Warcraft III|InstallPath"])
        // Again at another size: the size follows, the language stays what it was set to.
        user["${Wc3Setup.LAUNCHER}|Locale"] = "frFR"
        Wc3Setup.apply(root, 1600, 900, null, open)
        assertEquals(1600, user["${Wc3Setup.VIDEO}|reswidth"])
        assertEquals("frFR", user["${Wc3Setup.LAUNCHER}|Locale"])
    }

    @Test fun theGamesVideoOptionsArePutAtTheirBestOnce() {
        val best = Wc3Setup.writes(2520, 1890, locale = "enUS", installDos = null, best = true)
        for ((name, value) in listOf("modeldetail" to 2, "animquality" to 2, "texquality" to 2, "particles" to 2, "lights" to 2, "spellfilter" to 2, "unitshadows" to 1, "occlusion" to 1, "colordepth" to 32, "texcolordepth" to 32)) {
            assertTrue(name, Wc3Setup.Write(Wc3Setup.Hive.USER, Wc3Setup.VIDEO, name, value) in best)
        }
        assertTrue(Wc3Setup.Write(Wc3Setup.Hive.USER, Wc3Setup.APP, Wc3Setup.BEST_VIDEO, "1") in best)
        assertTrue(Wc3Setup.writes(2520, 1890, locale = "enUS", installDos = null).none { it.name == "modeldetail" || it.key == Wc3Setup.APP })

        // In the games' Windows: written at the first start, and not again once the person has changed one in the game's Options.
        val root = tmp.newFolder("best")
        val user = Fake()
        val hives = mapOf("user.reg" to user, "system.reg" to Fake())
        for (name in hives.keys) File(root, ".wine/$name").also { it.parentFile.mkdirs() }.writeText("x")
        val open = { f: File -> hives.getValue(f.name) }
        user.values["${Wc3Setup.VIDEO}|modeldetail"] = 0
        Wc3Setup.apply(root, 2520, 1890, null, open)
        assertEquals(2, user.values["${Wc3Setup.VIDEO}|modeldetail"])
        assertEquals(32, user.values["${Wc3Setup.VIDEO}|colordepth"])
        assertEquals("1", user.values["${Wc3Setup.APP}|${Wc3Setup.BEST_VIDEO}"])
        user.values["${Wc3Setup.VIDEO}|particles"] = 0
        Wc3Setup.apply(root, 2520, 1890, null, open)
        assertEquals(0, user.values["${Wc3Setup.VIDEO}|particles"])
        assertEquals(2520, user.values["${Wc3Setup.VIDEO}|reswidth"])
    }

    @Test fun aWindowsNotMadeYetIsLeftAlone() {
        val root = tmp.newFolder("empty")
        Wc3Setup.apply(root, 800, 600, null)
        assertFalse(File(root, ".wine").exists())
    }

    // CD keys (ported) -----------------------------------------------------------------------------

    @Test fun keysAreFoundWithTheWordsBeforeThemAsTheirLabel() {
        val text = """
            Serial keys for the old installer:

            Reign of Chaos: ABCD2-EFGH3-JKLM4-NPQR5-TVWX6
            The Frozen Throne - QWER7-TYUP8-ASDF9-GHJK2-ZXCV3
        """.trimIndent()
        assertEquals(
            listOf(
                Wc3CdKeys.Found("Reign of Chaos", "ABCD2-EFGH3-JKLM4-NPQR5-TVWX6"),
                Wc3CdKeys.Found("The Frozen Throne", "QWER7-TYUP8-ASDF9-GHJK2-ZXCV3"),
            ),
            Wc3CdKeys.find(text),
        )
    }

    @Test fun a26CharacterKeyNeedsLettersAndDigitsAndWordsArentKeys() {
        val found = Wc3CdKeys.find("ROC 4ab7cd8ef9gh2jk3lm4np5qr6s\nIncomprehensibilitiesxyzab is a word")
        assertEquals(listOf(Wc3CdKeys.Found("ROC", "4AB7CD8EF9GH2JK3LM4NP5QR6S")), found)
    }

    @Test fun datesVersionsAndLinksAreLeftAloneTheSameKeyOnce() {
        val text = "v1.30.4.11274 built 2019-01-15\nhttps://ss64.com/locale.html\nKEY1-KEY2-KEY3\nagain KEY1-KEY2-KEY3"
        assertEquals(listOf(Wc3CdKeys.Found("", "KEY1-KEY2-KEY3")), Wc3CdKeys.find(text))
    }

    @Test fun keyFilesAreToldByTheirNames() {
        assertTrue(Wc3CdKeys.isKeyFile("_SERIAL_KEYS.txt"))
        assertTrue(Wc3CdKeys.isKeyFile("CD Key.txt"))
        assertTrue(Wc3CdKeys.isKeyFile("keys.txt"))
        assertFalse(Wc3CdKeys.isKeyFile("README.txt"))
        assertFalse(Wc3CdKeys.isKeyFile("CustomKeyInfo.txt.bak"))
    }

    @Test fun pastedKeysAreTakenLineByLineWithOrWithoutLabelsAndDashes() {
        val pasted = """
            RoC: ABCD-EFGH-1234-5678-WXYZ
            tft2k3j4h5g6f7d8s9a0q1w2e3

            not a key
            abcdefgh12345678
        """.trimIndent()
        assertEquals(
            listOf(
                Wc3CdKeys.Found("RoC", "ABCD-EFGH-1234-5678-WXYZ"),
                Wc3CdKeys.Found("", "TFT2K3J4H5G6F7D8S9A0Q1W2E3"),
                Wc3CdKeys.Found("", "ABCDEFGH12345678"),
            ),
            Wc3CdKeys.findPasted(pasted),
        )
    }

    @Test fun theSameKeyPastedTwiceIsOfferedOnceAndNothingPastedIsNoKey() {
        assertEquals(1, Wc3CdKeys.findPasted("ABCDEFGH12345678\nabcdefgh12345678").size)
        assertTrue(Wc3CdKeys.findPasted("").isEmpty())
        assertTrue(Wc3CdKeys.findPasted("short1234\nwords only here").isEmpty())
    }

    @Test fun theStoreKeepsWhatWasPastedApartFromTheGame() {
        val files = tmp.newFolder("files")
        assertEquals("", Wc3CdKeys.text(files))
        Wc3CdKeys.save(files, "RoC: ABCD-EFGH-1234-5678-WXYZ\n")
        assertEquals("cdkeys.txt", Wc3CdKeys.file(files).name)
        assertEquals(listOf(Wc3CdKeys.Found("RoC", "ABCD-EFGH-1234-5678-WXYZ")), Wc3CdKeys.stored(files))
        assertEquals("RoC: ABCD-EFGH-1234-5678-WXYZ", Wc3CdKeys.stored(files).single().display)
        assertFalse(File(files, "cdkeys.txt.tmp").exists())
        Wc3CdKeys.save(files, "  \n")
        assertFalse(Wc3CdKeys.file(files).exists())
        assertTrue(Wc3CdKeys.stored(files).isEmpty())
    }

    @Test fun theMenuOffersPastedKeysThenThoseTheGameCameWith() {
        val files = tmp.newFolder("files")
        val game = tmp.newFolder("game")
        File(game, "_SERIAL_KEYS.txt").writeText("TFT: QWER7-TYUP8-ASDF9-GHJK2-ZXCV3\nRoC: ABCD-EFGH-1234-5678-WXYZ")
        File(game, "readme.txt").writeText("KEY1-KEY2-KEY3")
        Wc3CdKeys.save(files, "ABCD-EFGH-1234-5678-WXYZ")
        val offered = Wc3CdKeys.offered(files, game)
        assertEquals(listOf("ABCD-EFGH-1234-5678-WXYZ", "QWER7-TYUP8-ASDF9-GHJK2-ZXCV3"), offered.map { it.key })
        assertEquals(1, Wc3CdKeys.offered(files, null).size)
        assertNull(Wc3CdKeys.inGame(tmp.newFolder("none")).firstOrNull())
    }
}

/** Warcraft III's keys, pasted in whatever form: each put with its game by what it decodes to (keys of this test were found by trying the decoder; none was ever issued). */
class Wc3KeyPasteTest {
    private val roc = "H7JNf2vrehWyRNmr9XKwCHxxrV".uppercase()
    private val tft = "KyRxmkd9vxXt8CNzyBPPG9wnTE".uppercase()

    @org.junit.Test fun theCodecKnowsTheGame() {
        org.junit.Assert.assertEquals(14, Wc3KeyCodec.product(roc))
        org.junit.Assert.assertEquals(18, Wc3KeyCodec.product(tft))
        org.junit.Assert.assertNull(Wc3KeyCodec.product("0".repeat(26)))
        org.junit.Assert.assertNull(Wc3KeyCodec.product("H7JNf2"))
    }

    @org.junit.Test fun anyGroupingWithOrWithoutDashesAndSpaces() {
        fun group(k: String, sizes: List<Int>, sep: List<String>): String {
            var i = 0; val sb = StringBuilder()
            sizes.forEachIndexed { n, sz -> sb.append(k.substring(i, i + sz)); i += sz; if (n < sizes.size - 1) sb.append(sep[n % sep.size]) }
            return sb.toString()
        }
        val shapes = listOf(
            roc,
            group(roc, listOf(6, 4, 6, 4, 6), listOf(" ", "-", "-", "-")),
            group(roc, listOf(6, 4, 6, 4, 6), listOf("-")),
            group(roc, listOf(4, 4, 4, 4, 4, 4, 2), listOf(" ")),
            "  " + roc.lowercase() + "  ",
            "Reign of Chaos: " + group(roc, listOf(6, 4, 6, 4, 6), listOf("-")),
            "ROC " + roc,
        )
        for (s in shapes) {
            val k = Wc3CdKeys.wc3(s)
            org.junit.Assert.assertEquals(s, roc, k.reignOfChaos)
            org.junit.Assert.assertNull(s, k.frozenThrone)
        }
    }

    @org.junit.Test fun bothKeysSortedByGameWhateverTheOrder() {
        val a = "$roc\n${tft.substring(0, 6)}-${tft.substring(6, 10)}-${tft.substring(10, 16)}-${tft.substring(16, 20)}-${tft.substring(20)}"
        val b = "The Frozen Throne: $tft\nReign of Chaos: $roc"
        for (s in listOf(a, b, "$roc $tft")) {
            val k = Wc3CdKeys.wc3(s)
            org.junit.Assert.assertEquals(roc, k.reignOfChaos)
            org.junit.Assert.assertEquals(tft, k.frozenThrone)
        }
        // A key broken over lines.
        val broken = Wc3CdKeys.wc3(roc.substring(0, 13) + "\n" + roc.substring(13))
        org.junit.Assert.assertEquals(roc, broken.reignOfChaos)
    }

    @org.junit.Test fun whatIsNotAWarcraftKeyIsCountedAndIgnored() {
        val k = Wc3CdKeys.wc3("hello world\n" + "0".repeat(26) + "\n12345")
        org.junit.Assert.assertFalse(k.any)
        org.junit.Assert.assertEquals(1, k.unrecognised)
        org.junit.Assert.assertFalse(Wc3CdKeys.wc3("").any)
    }
}

/** Diablo II before 1.14 is told it runs on Windows 98 (Fog's critical-section check); every Diablo II plays at 800x600. */
class Diablo2SetupTest {
    private val resolution = Wc3Setup.Write(Wc3Setup.Hive.USER, Diablo2Setup.GAME_KEY, "Resolution", Diablo2Setup.RESOLUTION_800)

    @org.junit.Test fun only113AndOlderGetWindows98() {
        org.junit.Assert.assertEquals(
            listOf(Wc3Setup.Write(Wc3Setup.Hive.USER, Diablo2Setup.APP_DEFAULTS, "Version", "win98"), resolution),
            Diablo2Setup.writes("Diablo II + Lord of Destruction 1.13c"),
        )
        org.junit.Assert.assertTrue(Diablo2Setup.isBefore114("1.0.13.60"))
        org.junit.Assert.assertTrue(Diablo2Setup.isBefore114("Diablo II + Lord of Destruction 1.13"))
        org.junit.Assert.assertTrue(Diablo2Setup.isBefore114("1.12a"))
        org.junit.Assert.assertFalse(Diablo2Setup.isBefore114("Diablo II + Lord of Destruction 1.14.1.68"))
        org.junit.Assert.assertFalse(Diablo2Setup.isBefore114("1.14.3.71"))
        org.junit.Assert.assertFalse(Diablo2Setup.isBefore114(null))
        org.junit.Assert.assertEquals(listOf(resolution), Diablo2Setup.writes("1.14.1.68"))
    }

    @org.junit.Test fun theWritesLandInUserReg() {
        val tmp = java.nio.file.Files.createTempDirectory("d2setup").toFile()
        java.io.File(tmp, ".wine").mkdirs()
        java.io.File(tmp, ".wine/user.reg").writeText("WINE REGISTRY Version 2\n")
        val values = HashMap<String, Any>()
        val fake = object : Wc3Setup.Registry {
            override fun getString(key: String, name: String) = values["$key|$name"] as? String ?: ""
            override fun setString(key: String, name: String, value: String) { values["$key|$name"] = value }
            override fun setDword(key: String, name: String, value: Int) { values["$key|$name"] = value }
            override fun close() {}
        }
        Diablo2Setup.apply(tmp, "Diablo II + Lord of Destruction 1.13c") { fake }
        org.junit.Assert.assertEquals("win98", values["${Diablo2Setup.APP_DEFAULTS}|Version"])
        org.junit.Assert.assertEquals(1, values["${Diablo2Setup.GAME_KEY}|Resolution"])
        tmp.deleteRecursively()
    }
}
