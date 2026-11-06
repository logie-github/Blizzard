package com.logie.blizz.importer

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File
import java.nio.file.Files

class SafeFilesTest {
    @get:Rule val tmp = TemporaryFolder()

    @Test fun aLinkedFolderIsNeverEnteredOrEmptied() {
        val outside = tmp.newFolder("data")
        File(outside, "dbc").mkdirs()
        File(outside, "dbc/Spell.dbc").writeText("keep me")
        val game = tmp.newFolder("game")
        File(game, "files").mkdirs()
        File(game, "files/a.txt").writeText("x")
        Files.createSymbolicLink(File(game, "files/data-modules").toPath(), outside.toPath())
        // a link that points nowhere, as one left by another app's folder
        Files.createSymbolicLink(File(game, "files/dangling").toPath(), File(tmp.root, "gone").toPath())

        assertEquals(listOf("a.txt"), game.filesNoLinks().map { it.name }.toList())
        assertTrue(game.deleteTree())
        assertFalse(game.exists())
        assertEquals("keep me", File(outside, "dbc/Spell.dbc").readText())
    }

    @Test fun aFileOrNothingIsFine() {
        val f = tmp.newFile("x")
        assertTrue(f.deleteTree())
        assertTrue(File(tmp.root, "never").deleteTree())
    }
}
