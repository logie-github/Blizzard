package com.logie.blizz.wow

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

class WowConfMergeTest {
    @get:Rule val tmp = TemporaryFolder()

    private val dist = """
        # a comment = not a setting
        LogsDir = ""
        Updates.ExceptionShutdownDelay = 10000
        Updates.AutoSetup = 1
        #Commented.Out = 5
        Updates.ExceptionShutdownDelay = 99
    """.trimIndent()

    @Test fun onlyTheSettingsTheConfLacksAreAddedWithTheDistsValues() {
        val conf = "LogsDir = \"/x\"\nUpdates.AutoSetup = 0\n"
        assertEquals(listOf("Updates.ExceptionShutdownDelay = 10000"), WowConfMerge.missing(conf, dist))
    }

    @Test fun mergingKeepsTheFileAndIsIdempotent() {
        val conf = File(tmp.root, "dbimport.conf").apply { writeText("LogsDir = \"/x\"\nUpdates.AutoSetup = 0\n") }
        val d = File(tmp.root, "dbimport.conf.dist").apply { writeText(dist) }
        assertEquals(1, WowConfMerge.merge(conf, d))
        val text = conf.readText()
        assertTrue(text.contains("LogsDir = \"/x\"") && text.contains("Updates.AutoSetup = 0"))
        assertTrue(text.contains("Updates.ExceptionShutdownDelay = 10000"))
        assertFalse(text.contains("Commented.Out"))
        assertEquals(0, WowConfMerge.merge(conf, d))
    }

    @Test fun missingFilesAddNothing() {
        assertEquals(0, WowConfMerge.merge(File(tmp.root, "none.conf"), File(tmp.root, "none.dist")))
    }
}
