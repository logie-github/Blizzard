package com.logie.blizz.game

import com.logie.blizz.controls.Catalog
import com.logie.blizz.controls.KeyCombo
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
class WowClientSetupTest {
    @get:Rule val tmp = TemporaryFolder()

    private fun client(): File = tmp.newFolder("files", "client").also {
        File(it, "Wow.exe").writeText("MZ")
        File(it, "Data/enUS").mkdirs()
        File(it, "Data/enUS/realmlist.wtf").writeText("set realmlist logon.example.com\r\n")
        File(it, "Data/common.MPQ").writeText("x")
    }

    @Test fun updateConfigChangesOnlyTheNamedLinesAndKeepsTheRest() {
        val old = "SET gxResolution \"800x600\"\r\nSET Sound_MusicVolume \"0.3\"\r\n-- note\r\nSET REALMLIST \"old\"\r\n"
        val out = WowClientSetup.updateConfig(old, mapOf("gxResolution" to "2400x1080", "realmList" to "127.0.0.1", "movie" to "0"))
        assertEquals(
            "SET gxResolution \"2400x1080\"\r\nSET Sound_MusicVolume \"0.3\"\r\n-- note\r\nSET REALMLIST \"127.0.0.1\"\r\nSET movie \"0\"\r\n",
            out,
        )
    }

    @Test fun aNewConfigGetsWindowsLineEndings() {
        assertEquals("SET a \"1\"\r\n", WowClientSetup.updateConfig("", mapOf("a" to "1")))
        assertEquals("SET a \"1\"\nSET b \"2\"\n", WowClientSetup.updateConfig("SET a \"0\"\n", mapOf("a" to "1", "b" to "2")))
    }

    @Test fun applyPointsTheClientAtThePhonesRealmAndKeepsEverythingElse() {
        val c = client()
        val files = c.parentFile!!
        File(c, "WTF/Account/ME/SavedVariables").mkdirs()
        File(c, "WTF/Account/ME/SavedVariables/Bagnon.lua").writeText("mine")
        File(c, "Interface/AddOns/X").mkdirs(); File(c, "Interface/AddOns/X/X.toc").writeText("toc")
        File(c, "WTF/Config.wtf").writeText("SET Sound_MusicVolume \"0.3\"\r\nSET gxResolution \"1x1\"\r\n")
        File(c, "Cache/WDB").mkdirs(); File(c, "Cache/WDB/a").writeText("1")

        val applied = WowClientSetup.apply(c, files, 2400, 1080, "remix", "ME")

        assertEquals("set realmlist 127.0.0.1\r\n", File(c, "Data/enUS/realmlist.wtf").readText())
        assertFalse(File(c, "realmlist.wtf").exists())
        val cfg = File(c, "WTF/Config.wtf").readText()
        assertTrue(cfg.contains("SET Sound_MusicVolume \"0.3\""))
        assertTrue(cfg.contains("SET gxResolution \"2400x1080\""))
        assertTrue(cfg.contains("SET realmName \"Wrath Remix\"") && cfg.contains("SET accountName \"ME\"") && cfg.contains("SET realmList \"127.0.0.1\""))
        assertEquals("mine", File(c, "WTF/Account/ME/SavedVariables/Bagnon.lua").readText())
        assertTrue(File(c, "Interface/AddOns/X/X.toc").isFile)
        assertEquals("remix\n", File(files, "client-realm").readText())
        assertTrue(applied.clearedCache)
        assertFalse(File(c, "Cache/WDB").exists())
        assertTrue(c.walkTopDown().none { it.name.endsWith(".blizz-tmp") })
    }

    @Test fun theCacheStaysWhenTheRealmIsTheSame() {
        val c = client()
        File(c.parentFile, "client-realm").writeText("main\n")
        File(c, "Cache/WDB").mkdirs(); File(c, "Cache/WDB/a").writeText("1")
        assertFalse(WowClientSetup.apply(c, c.parentFile!!, 1280, 720, "main", null).clearedCache)
        assertTrue(File(c, "Cache/WDB/a").isFile)
        assertFalse(File(c, "WTF/Config.wtf").readText().contains("accountName"))
        assertTrue(WowClientSetup.mustClearCache(null, "remix"))
        assertFalse(WowClientSetup.mustClearCache(null, "main"))
    }

    @Test fun theSavedAccountIsReadWithoutThePassword() {
        val json = """{"name":{"type":"string","value":"PLAYER"},"password":{"type":"string","value":"secret"}}"""
        assertEquals("PLAYER", WowClientSetup.savedAccount(json))
        assertNull(WowClientSetup.savedAccount("not json"))
        assertNull(WowClientSetup.savedAccount(null))
    }

    @Test fun thePatchedProgramIsUsedOnlyWhenNeededAndThere() {
        val c = client()
        assertEquals("Wow.exe", WowClientSetup.executable(c, null))
        File(c, "WowPatched.exe").writeText("MZ")
        assertEquals("Wow.exe", WowClientSetup.executable(c, null))
        assertEquals("WowPatched.exe", WowClientSetup.executable(c, """{"hd_installed":{"type":"string","value":"ALTERNATIVE"}}"""))
        assertEquals("Wow.exe", WowClientSetup.executable(c, """{"hd_installed":{"type":"string","value":"OFF"}}"""))
        File(c, "Data/patch-Z.MPQ.skyborne").writeText("")
        assertEquals("WowPatched.exe", WowClientSetup.executable(c, null))
    }

    @Test fun theWowControlsAreComplete() {
        val wow = Catalog.of("wow-client")
        assertTrue(wow === Catalog.of("wow"))
        assertEquals(wow.functions.size, wow.functions.map { it.id }.toSet().size)
        for (f in wow.functions) if (f.kind.usesKey) assertTrue(f.id, f.key != null && f.key.key in KeyCombo.KEYS)
        for (r in wow.rules) { assertTrue(r.function, wow.function(r.function) != null); assertTrue(r.area, wow.area(r.area) != null) }
        assertEquals(LaunchProfile.WOW, LaunchProfile.of(WowPlay.PROFILE))
    }
}
