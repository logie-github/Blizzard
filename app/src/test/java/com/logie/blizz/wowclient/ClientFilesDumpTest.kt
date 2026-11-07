package com.logie.blizz.wowclient

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

class ClientFilesDumpTest {
    @get:Rule val tmp = TemporaryFolder()

    private fun archive(path: File, vararg files: Pair<String, String>) {
        path.parentFile!!.mkdirs()
        val w = Mpq.Writer(path)
        for ((name, text) in files) w.add(name, text.toByteArray())
        w.finish()
    }

    @Test fun theCreationScreensFilesAreReadFromTheHighestArchiveThatHasThemAndSaid() {
        val data = tmp.newFolder("Data")
        File(data, "enUS").mkdirs()
        archive(File(data, "enUS/locale-enUS.MPQ"),
            "Interface\\GlueXML\\GlueXML.toc" to "## Interface: 30300\nGlueParent.lua\nCharacterCreate.xml\nCharacterSelect.xml\nOther.lua\n",
            "Interface\\GlueXML\\CharacterCreate.lua" to "-- old",
            "Interface\\GlueXML\\CharacterCreate.xml" to "<Ui/>",
            "Interface\\GlueXML\\GlueParent.lua" to "-- glue",
            "Interface\\GlueXML\\CharacterSelect.xml" to "<Ui/>",
            "Interface\\GlueXML\\Other.lua" to "-- other")
        archive(File(data, "patch-3.MPQ"), "Interface\\GlueXML\\CharacterCreate.xml" to "<Ui>patched</Ui>")
        val pieces = ClientFilesDump.collect(data).associate { it.name to it.text }
        assertEquals("<Ui>patched</Ui>", pieces["CharacterCreate.xml"])
        assertTrue(pieces.containsKey("GlueXML.toc") && pieces.containsKey("GlueParent.lua") && pieces.containsKey("CharacterSelect.xml"))
        // Only what the toc names that has to do with the screens; not the other files.
        assertTrue(!pieces.containsKey("Other.lua"))
        val overview = pieces.getValue("overview")
        assertTrue(overview, overview.contains("locale: enUS") && overview.contains("CharacterCreate.xml: patch-3.MPQ") && overview.contains("locale-enUS.MPQ"))
    }
}
