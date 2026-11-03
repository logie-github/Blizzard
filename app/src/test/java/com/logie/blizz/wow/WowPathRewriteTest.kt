package com.logie.blizz.wow

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File
import java.nio.file.Files

class WowPathRewriteTest {
    @get:Rule val tmp = TemporaryFolder()

    private val old = "/data/data/com.logie.warcraft/files"
    private val old2 = "/data/user/0/com.logie.warcraft/files"

    private fun layout(): WowLayout {
        val game = tmp.newFolder("games", "wow")
        return WowLayout(File(game, "files").apply { mkdirs() }, File(game, ".export").apply { mkdirs() })
    }

    private fun put(file: File, text: String) = file.apply { parentFile!!.mkdirs(); writeText(text) }

    @Test fun rewritesConfigsAndScriptsAndLeavesBinariesAndDatabases() {
        val l = layout()
        val ctl = put(l.ctl, "FILES=\"\${FILES:-$old}\"\n").also { it.setExecutable(true) }
        val world = put(File(l.etc, "worldserver.conf"), "LogsDir = \"$old/logs\"\nDataDir = \"$old2/data\"\n")
        val remix = put(File(l.etcRemix, "modules/mod_wrath_remix.conf"), "Path = \"$old/x\"\n")
        val dist = put(File(l.server, "etc/worldserver.conf.dist"), "LogsDir = \"\"\n")
        val bin = File(l.server, "bin/worldserver").apply { parentFile!!.mkdirs(); writeBytes(byteArrayOf(0x7f, 'E'.code.toByte(), 0, 1) + old.toByteArray()) }
        val ibd = File(l.databases, "acore_characters/characters.ibd").apply { parentFile!!.mkdirs(); writeBytes(old.toByteArray() + byteArrayOf(0)) }
        val sql = put(File(l.server, "src/modules/m/x.sql"), "-- $old")
        val myIni = put(File(l.databases, "my.cnf"), "datadir=$old/mysql")
        val binBefore = bin.readBytes()
        val ibdBefore = ibd.readBytes()

        val result = WowPathRewrite.rewrite(l, WowPathRewrite.oldPrefixes(old), l.root.path)

        val new = l.root.path
        assertEquals("FILES=\"\${FILES:-$new}\"\n", ctl.readText())
        assertTrue("script stays executable", ctl.canExecute())
        assertEquals("LogsDir = \"$new/logs\"\nDataDir = \"$new/data\"\n", world.readText())
        assertEquals("Path = \"$new/x\"\n", remix.readText())
        assertEquals("LogsDir = \"\"\n", dist.readText())
        assertTrue(bin.readBytes().contentEquals(binBefore))
        assertTrue(ibd.readBytes().contentEquals(ibdBefore))
        assertEquals("-- $old", sql.readText())
        assertEquals("datadir=$old/mysql", myIni.readText())
        assertEquals(setOf("server/ctl.sh", "etc/worldserver.conf", "etc-remix/modules/mod_wrath_remix.conf"), result.filesRewritten.toSet())
        assertEquals("$new\n", l.rewriteMarker.readText())
        assertEquals(new, WowPathRewrite.recordedPrefix(l))
    }

    @Test fun idempotent() {
        val l = layout()
        put(File(l.etc, "authserver.conf"), "PidFile = \"$old/run/authserver.pid\"\n")
        val first = WowPathRewrite.rewrite(l, listOf(old), l.root.path)
        val text = File(l.etc, "authserver.conf").readText()
        val second = WowPathRewrite.rewrite(l, listOf(old), l.root.path)
        assertTrue(first.changed)
        assertFalse(second.changed)
        assertEquals(text, File(l.etc, "authserver.conf").readText())
        assertEquals("${l.root.path}\n", l.rewriteMarker.readText())
    }

    @Test fun symlinksIntoTheOldFolderPointToTheNewOne() {
        val l = layout()
        val dir = File(l.root, "data-modules/dbc").apply { mkdirs() }
        val link = File(dir, "Spell.dbc")
        Files.createSymbolicLink(link.toPath(), File("$old/data/dbc/Spell.dbc").toPath())
        val rel = File(dir, "Other.dbc")
        Files.createSymbolicLink(rel.toPath(), File("../../data/dbc/Other.dbc").toPath())

        val result = WowPathRewrite.rewrite(l, listOf(old), l.root.path)

        assertEquals("${l.root.path}/data/dbc/Spell.dbc", Files.readSymbolicLink(link.toPath()).toString())
        assertEquals("../../data/dbc/Other.dbc", Files.readSymbolicLink(rel.toPath()).toString())
        assertEquals(listOf("data-modules/dbc/Spell.dbc"), result.linksRewritten)
    }

    @Test fun theOldPrefixesComeFromTheExportAndBothSpellings() {
        val prefixes = WowPathRewrite.oldPrefixes("/data/user/0/com.logie.warcraft/files/")
        assertTrue("/data/user/0/com.logie.warcraft/files" in prefixes)
        assertTrue("/data/data/com.logie.warcraft/files" in prefixes)
        assertEquals(prefixes.distinct(), prefixes)
        // A different old folder (a second user's app storage) is rewritten too.
        val other = "/data/user/10/com.logie.warcraft/files"
        val l = layout()
        put(File(l.etc, "worldserver.conf"), "DataDir = \"$other/data\"\n")
        WowPathRewrite.rewrite(l, WowPathRewrite.oldPrefixes(other), l.root.path)
        assertEquals("DataDir = \"${l.root.path}/data\"\n", File(l.etc, "worldserver.conf").readText())
    }

    @Test fun nothingToDoWithoutTheFolders() {
        val l = layout()
        val result = WowPathRewrite.rewrite(l, listOf(old), l.root.path)
        assertFalse(result.changed)
    }
}
