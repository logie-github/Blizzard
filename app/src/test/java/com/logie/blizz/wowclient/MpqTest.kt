package com.logie.blizz.wowclient

import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File
import java.util.Random

class MpqTest {
    @get:Rule val tmp = TemporaryFolder()

    private val text = ("local x = 1\n".repeat(900)).toByteArray()          // compresses: several sectors
    private val noise = ByteArray(9000).also { Random(7).nextBytes(it) }    // doesn't: stored as it is
    private val tiny = "hi".toByteArray()
    private val empty = ByteArray(0)

    private fun write(file: File = File(tmp.root, "patch-X.MPQ")): File {
        val w = Mpq.Writer(file)
        assertTrue(w.add("Interface\\GlueXML\\CharacterCreate.lua", text))
        assertTrue(w.add("Interface\\GlueXML\\noise.bin", noise))
        assertTrue(w.add("a.txt", tiny))
        assertTrue(w.add("empty.txt", empty))
        assertTrue(w.addSame("Interface\\GlueXML\\Same.lua", "Interface\\GlueXML\\CharacterCreate.lua"))
        assertFalse(w.addSame("x", "not added"))
        assertTrue(w.finish())
        return file
    }

    @Test fun anArchiveWrittenIsReadBackWholeByAnyCaseAndEitherSlash() {
        val archive = Mpq.open(write())
        assertArrayEquals(text, archive.read("interface/gluexml/CHARACTERCREATE.LUA"))
        assertArrayEquals(noise, archive.read("Interface\\GlueXML\\noise.bin"))
        assertArrayEquals(tiny, archive.read("A.TXT"))
        assertArrayEquals(empty, archive.read("empty.txt"))
        assertArrayEquals(text, archive.read("Interface\\GlueXML\\Same.lua"))
        assertNull(archive.read("missing.txt"))
        assertTrue(archive.has("a.txt"))
        assertFalse(archive.has("b.txt"))
    }

    @Test fun theNameHashMatchesTheFormatsKnownValues() {
        // The hash of "(hash table)" and "(block table)" with type 3 are the tables' keys: 0xC3AF3770 and 0xEC83B3A3 in StormLib.
        assertEquals(0xC3AF3770.toInt(), Mpq.hash("(hash table)", 3))
        assertEquals(0xEC83B3A3.toInt(), Mpq.hash("(block table)", 3))
    }

    @Test fun theGamesArchivesAreReadInTheOrderTheGameReadsThem() {
        val data = tmp.newFolder("Data")
        File(data, "enUS").mkdirs()
        fun archive(path: File, name: String, text: String) {
            path.parentFile!!.mkdirs()
            val w = Mpq.Writer(path)
            w.add(name, text.toByteArray())
            w.finish()
        }
        archive(File(data, "common.MPQ"), "Interface\\GlueXML\\GlueXML.toc", "common")
        archive(File(data, "enUS/locale-enUS.MPQ"), "Interface\\GlueXML\\GlueXML.toc", "locale")
        archive(File(data, "patch-3.MPQ"), "Interface\\GlueXML\\GlueXML.toc", "patch 3")
        archive(File(data, "enUS/patch-enUS-3.MPQ"), "Interface\\GlueXML\\GlueXML.toc", "locale patch 3")
        archive(File(data, "patch-A.MPQ"), "other", "a")
        val game = Mpq.Game(data)
        assertEquals("enUS", game.locale)
        assertEquals("locale patch 3", String(game.read("Interface\\GlueXML\\GlueXML.toc")!!))
        assertTrue(game.has("other"))
        // a folder named like a patch is an archive too
        File(data, "patch-M.MPQ/Interface/GlueXML/GlueXML.toc").apply { parentFile!!.mkdirs(); writeText("folder") }
        assertEquals("folder", String(Mpq.Game(data).read("interface\\gluexml\\gluexml.toc")!!))
        assertEquals("locale patch 3", String(Mpq.Game(data, skip = listOf("patch-m.mpq")).read("Interface\\GlueXML\\GlueXML.toc")!!))
    }

    /** With BLIZZ_MPQ_OUT set, the test's archive is also written there, for the World of Warcraft app's C++ reader to read (checked by hand). */
    @Test fun writesACopyForTheCppReader() {
        val out = System.getenv("BLIZZ_MPQ_OUT") ?: return
        write(File(out))
    }
}
