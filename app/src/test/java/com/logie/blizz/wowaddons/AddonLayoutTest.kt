package com.logie.blizz.wowaddons

import kotlin.test.Test
import kotlin.test.assertEquals

class AddonLayoutTest {
    @Test
    fun anAddonsFolderWithItsLibraries() {
        val plan = AddonLayout.plan(
            listOf("Questie/", "Questie/Questie.toc", "Questie/Questie.lua", "Questie/Libs/LibStub/LibStub.toc", "Questie/Libs/LibStub/LibStub.lua")
        )
        assertEquals(listOf("Questie"), plan.folders)
        assertEquals("Questie/Libs/LibStub/LibStub.toc", plan.targets["Questie/Libs/LibStub/LibStub.toc"])
        assertEquals(4, plan.targets.size)
    }

    @Test
    fun addonsSideBySide() {
        val plan = AddonLayout.plan(listOf("DBM-Core/DBM-Core.toc", "DBM-Core/a.lua", "DBM-Party/DBM-Party.toc", "DBM-Party/b.lua"))
        assertEquals(listOf("DBM-Core", "DBM-Party"), plan.folders)
        assertEquals("DBM-Party/b.lua", plan.targets["DBM-Party/b.lua"])
    }

    @Test
    fun insideInterfaceAddOns() {
        val plan = AddonLayout.plan(listOf("Interface/AddOns/Foo/Foo.toc", "Interface/AddOns/Foo/x.lua"))
        assertEquals(listOf("Foo"), plan.folders)
        assertEquals(mapOf("Interface/AddOns/Foo/Foo.toc" to "Foo/Foo.toc", "Interface/AddOns/Foo/x.lua" to "Foo/x.lua"), plan.targets)
    }

    @Test
    fun aDownloadsFolderTakesTheTocsName() {
        val plan = AddonLayout.plan(listOf("Foo-master/Foo.toc", "Foo-master/core.lua", "Foo-master/README.md"))
        assertEquals(listOf("Foo"), plan.folders)
        assertEquals("Foo/core.lua", plan.targets["Foo-master/core.lua"])
    }

    @Test
    fun filesWithNoFolder() {
        val plan = AddonLayout.plan(listOf("Foo.toc", "Foo.lua", "media/icon.blp"))
        assertEquals(listOf("Foo"), plan.folders)
        assertEquals("Foo/media/icon.blp", plan.targets["media/icon.blp"])
    }

    @Test
    fun theTocForThisVersionOfTheGame() {
        assertEquals(listOf("Bar"), AddonLayout.plan(listOf("Bar/Bar-Classic.toc", "Bar/Bar_Wrath.toc", "Bar/Bar.toc")).folders)
        assertEquals(listOf("Bar"), AddonLayout.plan(listOf("Bar-1.0/Bar-Classic.toc", "Bar-1.0/Bar.toc")).folders)
        assertEquals(listOf("Bar"), AddonLayout.plan(listOf("Bar-1.0/Bar-Wrath.toc")).folders.map { it.substringBefore('-') })
    }

    @Test
    fun unsafeAndMacFilesAreLeftOut() {
        val plan = AddonLayout.plan(listOf("Foo/Foo.toc", "Foo/../../evil.lua", "__MACOSX/Foo/._Foo.toc"))
        assertEquals(mapOf("Foo/Foo.toc" to "Foo/Foo.toc"), plan.targets)
    }

    @Test
    fun noTocNoAddon() {
        assertEquals(emptyList(), AddonLayout.plan(listOf("readme.txt", "pics/a.png")).folders)
    }

    @Test
    fun tocFieldsWithoutColours() {
        val fields = AddonLayout.tocFields("## Interface: 30300\n## Title: |cff00ff00Questie|r Helper\n## Version: 6.5\nQuestie.lua\n")
        assertEquals("30300", fields["Interface"])
        assertEquals("Questie Helper", fields["Title"])
        assertEquals("6.5", fields["Version"])
    }
}
