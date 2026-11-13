package com.logie.blizz.wrathpp

import com.logie.blizz.wowclient.Mpq
import com.logie.blizz.wrathpp.Reforged.Option
import com.logie.blizz.wrathpp.Reforged.Part
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

/** Project Reforged for Wrath++ ([Reforged]): what each switch brings, the downloads, Play putting them in, the glue screens kept. */
class ReforgedTest {
    @get:Rule val tmp = TemporaryFolder()

    /** An MPQ the way the project's are read: its files and a (listfile) naming them. */
    private fun mpq(file: File, files: Map<String, String>): ByteArray {
        val w = Mpq.Writer(file)
        for ((n, t) in files) w.add(n, t.toByteArray())
        w.add("(listfile)", files.keys.joinToString("\r\n").toByteArray())
        assertTrue(w.finish())
        return file.readBytes()
    }

    /** The project's server, serving [files] by URL with an ETag each; [cutAt]: a download stops there once. */
    private class FakeNet(val files: MutableMap<String, Pair<String, ByteArray>>, var cutAt: Long? = null, var online: Boolean = true) : Reforged.Net {
        val gets = ArrayList<Pair<String, Long>>()
        override fun head(url: String) = if (!online) null else files[url]?.let { it.first to it.second.size.toLong() }
        override fun get(url: String, from: Long, to: File, progress: (Long) -> Unit): String? {
            val (etag, bytes) = files.getValue(url)
            gets += url to from
            val end = cutAt?.let { minOf(it, bytes.size.toLong()) }?.also { cutAt = null } ?: bytes.size.toLong()
            java.io.RandomAccessFile(to, "rw").use { it.setLength(from); it.seek(from); it.write(bytes, from.toInt(), (end - from).toInt()) }
            progress(end)
            return etag
        }
    }

    private fun game(): Pair<File, File> {
        val client = tmp.newFolder("client-wrathpp")
        val data = File(client, "Data").apply { mkdirs() }
        mpq(File(data, "common.MPQ"), mapOf(
            "Interface\\GlueXML\\GlueXML.toc" to "CharacterCreate.xml",
            "Interface\\GlueXML\\CharacterCreate.lua" to "the game's creation screen",
            "Interface\\GlueXML\\CharacterCreate.xml" to "<Ui/>",
            "Interface\\Glues\\Models\\UI_Human\\UI_Human.m2" to "the game's human backdrop",
            "Interface\\Glues\\LoadingScreens\\LoadScreenElwynn.blp" to "the game's loading screen",
            "Creature\\Wolf\\Wolf.m2" to "the game's wolf",
        ))
        return client to data
    }

    @Test fun noCharactersAndReforgedsOwnOrderOnLettersOfTheirOwn() {
        val all = Reforged.parts(Option.entries.toSet())
        // not the HD characters (Patch-A HD) nor the upright orcs (U); the creatures' high elves are the SD A
        assertFalse(all.any { it.remote == "patch-A.mpq" || it.remote == "patch-U.mpq" })
        assertTrue(Part.HIGH_ELVES in all && Part.HIGH_ELVES.remote == "extras/patch-A.mpq")
        assertEquals(setOf(Part.BUILDINGS, Part.DOODADS, Part.ENVIRONMENT), Reforged.parts(setOf(Option.WORLD)))
        // Sounds: the version made for Maps with Maps, the one alone without
        assertTrue(Part.SOUNDS in all && Part.SOUNDS_ALONE !in all)
        assertEquals(setOf(Part.SOUNDS_ALONE), Reforged.parts(setOf(Option.SOUNDS)))
        // letters: none of the realm modules' (M U V Y Z), Wrath++'s (S X Z) or the mask's (T); after the HD look's A and E,
        // in Reforged's own order
        val ordered = Part.entries.filter { it != Part.SOUNDS_ALONE }
        for (p in Part.entries) assertTrue(p.slot !in "MUVYZSXTAE" && p.slot in 'F'..'R')
        assertEquals(ordered.map { it.slot }.sorted(), ordered.map { it.slot })
        assertEquals(ordered.size, ordered.map { it.slot }.toSet().size)
        assertTrue(Reforged.MASK.substring(6, 7)[0] in 'R'..'W')
    }

    @Test fun theChoiceIsKept() {
        val dir = tmp.newFolder()
        assertEquals(emptySet<Option>(), Reforged.chosen(dir))
        Reforged.choose(dir, setOf(Option.GEAR, Option.WORLD))
        assertEquals(setOf(Option.GEAR, Option.WORLD), Reforged.chosen(dir))
    }

    @Test fun downloadsResumeAndOnlyPlayPutsThemIn() {
        val (client, data) = game()
        val nights = mpq(tmp.newFile(), mapOf("DBFilesClient\\LightIntBand.dbc" to "darker"))
        val net = FakeNet(mutableMapOf(Part.NIGHTS.url to ("n1" to nights)), cutAt = 40)
        val first = Reforged.sync(data, setOf(Option.NIGHTS), net)
        assertTrue(first.single(), first.single().contains("cut off"))
        val second = Reforged.sync(data, setOf(Option.NIGHTS), net)
        assertTrue(second.single(), second.single().contains("next Play"))
        assertEquals(40L, net.gets.last().second)                    // went on from where it stopped
        assertFalse(File(data, "patch-O.MPQ").exists())               // not in the game before Play
        Reforged.prepare(client, null, setOf(Option.NIGHTS))
        assertTrue(Reforged.isIn(data, Part.NIGHTS, "n1"))
        assertEquals("darker", String(Mpq.Game(data).read("DBFilesClient\\LightIntBand.dbc")!!))
        // up to date: nothing fetched; republished: fetched again
        val gets = net.gets.size
        assertTrue(Reforged.sync(data, setOf(Option.NIGHTS), net).single().contains("up to date"))
        assertEquals(gets, net.gets.size)
        net.files[Part.NIGHTS.url] = "n2" to mpq(tmp.newFile(), mapOf("DBFilesClient\\LightIntBand.dbc" to "darker still"))
        Reforged.sync(data, setOf(Option.NIGHTS), net)
        Reforged.prepare(client, null, setOf(Option.NIGHTS))
        assertTrue(Reforged.isIn(data, Part.NIGHTS, "n2"))
        // offline: kept
        net.online = false
        assertTrue(Reforged.sync(data, setOf(Option.NIGHTS), net).single().contains("kept"))
        assertTrue(Reforged.isIn(data, Part.NIGHTS))
    }

    @Test fun whatIsNotAnMpqOrDoesNotFitIsRefused() {
        val (_, data) = game()
        val net = FakeNet(mutableMapOf(Part.SPELLS.url to ("p" to "<html>error page</html>".toByteArray())))
        assertTrue(Reforged.sync(data, setOf(Option.SPELLS), net).single().contains("isn't an MPQ"))
        assertFalse(File(data, "patch-P.MPQ.ready").exists())
        val big = FakeNet(mutableMapOf(Part.SPELLS.url to ("p" to ByteArray(10))))
        assertTrue(Reforged.sync(data, setOf(Option.SPELLS), big, freeBytes = { 1000L }).single().contains("not enough space"))
        assertTrue(big.gets.isEmpty())
    }

    @Test fun turnedOffItComesOutAndWrathPlusArchiveItStoodForComesBack() {
        val (client, data) = game()
        val wrathPlus = tmp.newFolder("client")
        File(wrathPlus, "Data").mkdirs()
        File(wrathPlus, "Data/patch-F.MPQ").writeText("Wrath+'s own F")
        File(data, "patch-F.MPQ").writeText("Wrath+'s own F")             // shared into Wrath++'s copy
        val elves = mpq(tmp.newFile(), mapOf("Character\\HighElf\\Male\\BloodElfMale.M2" to "high elf"))
        val creatures = mpq(tmp.newFile(), mapOf("Creature\\Wolf\\Wolf.m2" to "Reforged's wolf"))
        val net = FakeNet(mutableMapOf(Part.HIGH_ELVES.url to ("a" to elves), Part.CREATURES.url to ("c" to creatures)))
        Reforged.sync(data, setOf(Option.CREATURES), net)
        val notes = Reforged.prepare(client, File(wrathPlus, "Data"), setOf(Option.CREATURES))
        assertTrue(notes, notes.contains("taken out of Wrath++'s copy"))
        assertEquals("Reforged's wolf", String(Mpq.Game(data).read("Creature\\Wolf\\Wolf.m2")!!))
        assertEquals("Wrath+'s own F", File(wrathPlus, "Data/patch-F.MPQ").readText())   // Wrath+'s game untouched
        Reforged.prepare(client, File(wrathPlus, "Data"), emptySet())
        assertFalse(File(data, "patch-F.MPQ").exists()); assertFalse(File(data, "patch-H.MPQ").exists())
        assertTrue(Reforged.installed(data).isEmpty())
        WrathppClient.addMissing(wrathPlus, client)
        assertEquals("Wrath+'s own F", File(data, "patch-F.MPQ").readText())
        assertEquals("the game's wolf", String(Mpq.Game(data).read("Creature\\Wolf\\Wolf.m2")!!))
    }

    @Test fun theGlueScreensStayTheGamesOwn() {
        val (client, data) = game()
        val ui = mpq(tmp.newFile(), mapOf(
            "Interface\\GlueXML\\GlueXML.toc" to "Reforged's toc",
            "Interface\\GlueXML\\CharacterCreate.lua" to "Reforged's creation screen",
            "Interface\\GlueXML\\AceSerializer.lua" to "only Reforged's",
            "Interface\\Glues\\Models\\UI_Human\\UI_Human.m2" to "Reforged's backdrop",
            "Interface\\Glues\\LoadingScreens\\LoadScreenElwynn.blp" to "Reforged's loading screen",
            "Interface\\FrameXML\\ActionBar.lua" to "Reforged's action bar",
        ))
        val net = FakeNet(mutableMapOf(Part.INTERFACE.url to ("i" to ui)))
        Reforged.sync(data, setOf(Option.INTERFACE), net)
        val notes = Reforged.prepare(client, null, setOf(Option.INTERFACE))
        assertTrue(notes, File(data, Reforged.MASK).isFile)
        val game = Mpq.Game(data)
        assertEquals("CharacterCreate.xml", String(game.read("Interface\\GlueXML\\GlueXML.toc")!!))
        assertEquals("the game's creation screen", String(game.read("Interface\\GlueXML\\CharacterCreate.lua")!!))
        assertEquals("the game's human backdrop", String(game.read("Interface\\Glues\\Models\\UI_Human\\UI_Human.m2")!!))
        assertEquals("Reforged's loading screen", String(game.read("Interface\\Glues\\LoadingScreens\\LoadScreenElwynn.blp")!!))
        assertEquals("Reforged's action bar", String(game.read("Interface\\FrameXML\\ActionBar.lua")!!))
        game.close()
        // the creator's patch reads the toc as the game's own
        WrathppAddon.writeGluePatch(client, mapOf("WrathppCreate.lua" to "creator".toByteArray()))
        val withCreator = Mpq.Game(data)
        val toc = String(withCreator.read("Interface\\GlueXML\\GlueXML.toc")!!)
        assertTrue(toc, toc.startsWith("CharacterCreate.xml") && toc.contains("WrathppCreate.lua") && !toc.contains("Reforged"))
        withCreator.close()
        // the same parts again: the mask isn't made again; Interface off: the mask goes with it
        assertTrue(Reforged.prepare(client, null, setOf(Option.INTERFACE)).contains("mask as it was"))
        Reforged.prepare(client, null, emptySet())
        assertFalse(File(data, Reforged.MASK).exists())
        assertNull(Reforged.installed(data)['L'])
    }

    @Test fun whatIsMasked() {
        assertTrue(Reforged.masked("Interface\\GlueXML\\CharacterCreate.xml"))
        assertTrue(Reforged.masked("interface/glues/CHARACTERCREATE/x.blp"))
        assertTrue(Reforged.masked("Interface\\Glues\\models\\BE_B.blp"))
        assertFalse(Reforged.masked("Interface\\GLUES\\LOADINGSCREENS\\InstanceAlteracValley.blp"))
        assertFalse(Reforged.masked("Interface\\Glues\\Models\\UI_MainMenu_Northrend\\UI_MainMenu_Northrend.m2"))
        assertFalse(Reforged.masked("Interface\\FrameXML\\ActionBar.lua"))
        assertFalse(Reforged.masked("Character\\Human\\Male\\HumanMale.m2"))
    }
}
