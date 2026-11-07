package com.logie.blizz.wowaddons

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File
import java.nio.file.Files

class AddonGuardTest {
    @get:Rule val tmp = TemporaryFolder()

    private val files get() = File(tmp.root, "files")
    private val client get() = File(files, "client")
    private val records get() = File(files, "warperia-addons.tsv")
    private val downloads get() = File(files, "addon-downloads")
    private fun guard() = AddonGuard(listOf(File(client, "Interface"), downloads), listOf(records))

    private fun refused(block: () -> Unit) {
        try {
            block()
            fail("Expected a refusal")
        } catch (_: AddonGuard.Refused) {
        }
    }

    @Test
    fun allowsWhatIsInsideTheInterfaceFolderAndTheDownloads() {
        val g = guard()
        g.check(File(client, "Interface/AddOns/Questie/Questie.toc"))
        g.check(File(client, "Interface/AddOns"))
        g.check(File(downloads, "warperia-questie.zip.part"))
    }

    @Test
    fun refusesTheRestOfTheClientAndWhatIsOutside() {
        val g = guard()
        refused { g.check(File(client, "Data/common.MPQ")) }
        refused { g.check(File(client, "WoW.exe")) }
        refused { g.check(File(files, "server/data")) }
        refused { g.check(File(tmp.root, "elsewhere")) }
        // The roots themselves can be made, not deleted or moved.
        refused { g.check(File(client, "Interface")) }
        refused { g.delete(File(client, "Interface")) }
    }

    @Test
    fun refusesDotDotAndLinksThatLeadOut() {
        val g = guard()
        refused { g.check(File(client, "Interface/AddOns/../../Data")) }
        File(client, "Interface/AddOns").mkdirs()
        val outside = File(tmp.root, "outside").also { it.mkdirs(); File(it, "keep.txt").writeText("x") }
        val link = File(client, "Interface/AddOns/Sneaky")
        try {
            Files.createSymbolicLink(link.toPath(), outside.toPath())
        } catch (e: Exception) {
            return // no links on this machine
        }
        refused { g.check(File(link, "keep.txt")) }
        // Deleting the link removes the link, not what it points to.
        g.delete(link)
        assertFalse(Files.exists(link.toPath(), java.nio.file.LinkOption.NOFOLLOW_LINKS))
        assertTrue(File(outside, "keep.txt").isFile)
    }

    @Test
    fun theRecordsAndTheirCompanionsAreAllowedAndNothingElseBesideThem() {
        val g = guard()
        files.mkdirs()
        g.check(records)
        g.check(File(records.path + ".new"))
        g.check(File(records.path + ".old"))
        refused { g.check(File(files, "other.tsv")) }
    }

    @Test
    fun replaceKeepsTheOldOneUntilTheNewOneIsIn() {
        val g = guard()
        files.mkdirs()
        records.writeText("old")
        val fresh = File(records.path + ".new").also { it.writeText("new") }
        g.replace(fresh, records)
        assertEquals("new", records.readText())
        assertFalse(fresh.exists())
        assertFalse(File(records.path + ".old").exists())
    }

    @Test
    fun deleteAndMoveWorkInsideTheFolder() {
        val g = guard()
        val a = File(client, "Interface/AddOns/A").also { it.mkdirs(); File(it, "A.toc").writeText("## Title: A") }
        val off = File(client, "Interface/AddOns-off")
        g.mkdirs(off)
        g.move(a, File(off, "A"))
        assertTrue(File(off, "A/A.toc").isFile)
        g.delete(File(off, "A"))
        assertFalse(File(off, "A").exists())
        // Nothing there is fine.
        g.delete(File(off, "A"))
    }
}
