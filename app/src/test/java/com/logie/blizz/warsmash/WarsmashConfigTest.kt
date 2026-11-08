package com.logie.blizz.warsmash

import org.junit.Assert.*
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

class WarsmashConfigTest {
    @get:Rule val tmp = TemporaryFolder()
    @Test fun patchOverridesBaseAndSupportOverridesArchivesRegardlessOfDirectoryOrder() {
        val game = tmp.newFolder("Warcraft III")
        listOf("War3Patch.MPQ", "war3x.mpq", "WAR3.MPQ").forEach { File(game, it).writeText("fixture") }
        val support = tmp.newFolder("support")
        val config = WarsmashConfig.sources(game, support)
        assertTrue(config.indexOf("WAR3.MPQ") < config.indexOf("war3x.mpq"))
        assertTrue(config.indexOf("war3x.mpq") < config.indexOf("War3Patch.MPQ"))
        assertTrue(config.indexOf("War3Patch.MPQ") < config.indexOf(support.path))
        assertTrue(config.contains("Count=6"))
        assertTrue(config.contains("Path05=${support.absolutePath}"))
    }
}
