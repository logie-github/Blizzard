package com.logie.blizz.wrathpp

import com.logie.blizz.wow.WowLayout
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
import java.io.IOException
import java.nio.file.Files

/** Wrath++'s copy of the game and its server package's pure parts (Robolectric for org.json). */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class WrathppClientTest {
    @get:Rule val tmp = TemporaryFolder()

    private fun game(): File = tmp.newFolder("files", "client").also { c ->
        fun put(rel: String, text: String = rel) = File(c, rel).apply { parentFile!!.mkdirs(); writeText(text) }
        put("Wow.exe", "MZ")
        put("Data/common.MPQ"); put("Data/lichking.MPQ"); put("Data/enUS/locale-enUS.MPQ"); put("Data/enUS/realmlist.wtf", "set realmlist x")
        put("Data/patch-V.MPQ"); put("Data/patch-V.MPQ.alliedraces"); put("Data/patch-M.MPQ/realm-modules.stamp"); put("Data/patch-M.MPQ/Interface/a.lua")
        put("Data/patch-H.MPQ", "hd")
        put("WTF/Config.wtf", "SET realmName \"ChromieCraft\"")
        put("Interface/AddOns/A/A.toc")
        put("Cache/WDB/enUS/x.wdb"); put("Logs/x.log")
    }

    @Test fun theRuleIsCtlShs() {
        // ctl.sh wrathpp_shareable: archives yes, module patches and their markers no, nothing outside Data/ and Data/<locale>/.
        assertTrue(WrathppClient.shareable("Data/common.MPQ"))
        assertTrue(WrathppClient.shareable("Data/enUS/patch-enUS-3.MPQ"))
        assertTrue(WrathppClient.shareable("Data/patch-H.mpq"))
        for (no in listOf("Data/patch-V.MPQ", "Data/patch-m.mpq", "Data/patch-Z.MPQ", "Data/patch-4.MPQ", "Data/patch-V.MPQ.alliedraces",
            "Data/enUS/realmlist.wtf", "Wow.exe", "Data/x/y/z.MPQ", "WTF/Config.wtf")) assertFalse(no, WrathppClient.shareable(no))
        assertTrue(WrathppClient.skipped("Data/patch-M.MPQ/Interface/a.lua"))
        assertTrue(WrathppClient.skipped("Cache/WDB/enUS/x.wdb"))
        assertFalse(WrathppClient.skipped("Data/common.MPQ"))
    }

    @Test fun theCopySharesOnlyArchivesAndLeavesTheGameAsItWas() {
        val src = game()
        val before = src.walkTopDown().filter { it.isFile }.associate { it.relativeTo(src).path to it.readText() }
        val dst = File(src.parentFile, "client-wrathpp")

        assertTrue(WrathppClient.make(src, dst))

        assertTrue(WrathppClient.isMade(dst))
        fun shared(rel: String) = Files.isSameFile(File(src, rel).toPath(), File(dst, rel).toPath())
        assertTrue(shared("Data/common.MPQ")); assertTrue(shared("Data/enUS/locale-enUS.MPQ")); assertTrue(shared("Data/patch-H.MPQ"))
        assertFalse(shared("Wow.exe")); assertFalse(shared("WTF/Config.wtf")); assertFalse(shared("Data/enUS/realmlist.wtf"))
        // The realm modules' patches aren't taken: Wrath++'s realm makes its own.
        for (gone in listOf("Data/patch-V.MPQ", "Data/patch-V.MPQ.alliedraces", "Data/patch-M.MPQ", "Cache", "Logs")) assertFalse(gone, File(dst, gone).exists())
        assertTrue(File(dst, "Interface/AddOns/A/A.toc").isFile)
        // A write to the copy's own files doesn't reach the game.
        File(dst, "WTF/Config.wtf").writeText("SET realmName \"Wrath++\"")
        val after = src.walkTopDown().filter { it.isFile }.associate { it.relativeTo(src).path to it.readText() }
        assertEquals(before, after)
        // Made once.
        assertFalse(WrathppClient.make(src, dst))
    }

    @Test fun aCopyInsideTheGameIsRefused() {
        val src = game()
        try { WrathppClient.make(src, File(src, "Data/wrathpp")); throw AssertionError("not refused") } catch (_: IOException) { }
        try { WrathppClient.make(src, src); throw AssertionError("not refused") } catch (_: IOException) { }
    }

    @Test fun thePackagesManifestAndWhenToInstall() {
        val m = WrathppServerPackage.parseManifest("""{"size": 12, "sha256": "AB", "unpacked": 99, "format": 1, "protocol": 1, "commit": "x"}""")
        assertEquals(12L, m.size); assertEquals("AB", m.sha256); assertEquals(99L, m.unpacked); assertEquals(1, m.protocol)
        val game = tmp.newFolder("g")
        val layout = WowLayout(File(game, "files"), File(game, ".export"))
        assertTrue(WrathppServerPackage.needsInstall(layout, m))   // nothing installed
        assertTrue(WrathppServerPackage.needsInstall(layout, null))
        layout.wrathppCtl.apply { parentFile!!.mkdirs(); writeText("#") }
        File(layout.wrathppServer, "bin/worldserver").apply { parentFile!!.mkdirs(); writeText("x") }
        assertTrue(WrathppServerPackage.needsInstall(layout, m))   // no marker: an unfinished install
        File(layout.wrathppServer, WrathppServerPackage.MARKER).writeText("ab\n")
        assertFalse(WrathppServerPackage.needsInstall(layout, m))  // the same (case-insensitive)
        assertFalse(WrathppServerPackage.needsInstall(layout, null)) // offline: what is installed
        assertTrue(WrathppServerPackage.needsInstall(layout, m.copy(sha256 = "cd")))
        // Tar paths never leave the folder.
        val base = tmp.newFolder("base")
        assertEquals(File(base, "server/bin/x"), WrathppServerPackage.entryTarget(base, "./server/bin/x"))
        assertNull(WrathppServerPackage.entryTarget(base, "../x"))
        assertNull(WrathppServerPackage.entryTarget(base, "/etc/passwd"))
        assertNull(WrathppServerPackage.entryTarget(base, "server/../../x"))
    }
}
