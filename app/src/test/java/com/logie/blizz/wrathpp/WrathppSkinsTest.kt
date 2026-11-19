package com.logie.blizz.wrathpp

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import java.io.File

/** Which skins the creator offers once Ralia's mod is in ([WrathppSkins]). */
@RunWith(RobolectricTestRunner::class)
class WrathppSkinsTest {
    @get:Rule val tmp = TemporaryFolder()

    private fun row(id: Int, race: Int, sex: Int, section: Int, a: String, colour: Int): Array<Any> = arrayOf(id, race, sex, section, a, "", "", 17, 0, colour)

    private fun game(): File {
        val client = tmp.newFolder("client-wrathpp")
        val patch = File(client, "Data/patch-Z.MPQ")
        File(patch, "DBFilesClient").mkdirs()
        val table = WrathppUndead.Dbc(WrathppUndead.KINDS, mutableListOf(
            row(1, 1, 1, 0, "Character\\Human\\Female\\HumanFemaleSkin00_00.blp", 0), row(2, 1, 1, 0, "Character\\Human\\Female\\HumanFemaleSkin00_01.blp", 1),
            row(3, 1, 1, 0, "Character\\Human\\Female\\HumanFemaleSkin00_02.blp", 2), row(4, 1, 1, 4, "HF\\Pelvis00.blp", 0),
            row(5, 1, 0, 0, "Character\\Human\\Male\\HumanMaleSkin00_00.blp", 0), row(6, 1, 0, 0, "Character\\Human\\Male\\HumanMaleSkin00_01.blp", 1),
            row(7, 5, 1, 0, "Character\\Scourge\\Female\\ScourgeFemaleUndeadSkin.blp", 0)))
        File(patch, "DBFilesClient/CharSections.dbc").writeBytes(table.write())
        File(patch, WrathppRalia.STAMP).writeText("abc looks donors1 faces1\n")           // (as WrathppRalia.apply leaves it: the set is in the looks)
        File(patch, WrathppRalia.NAMES).writeText("""{"format": 1, "models": {
            "1_1": {"name": "HumanFemale", "race": 1, "sex": 1, "skins": [
                {"index": 0, "path": "Character\\Human\\Female\\HumanFemaleSkin00_00.blp", "retail": "humanfemaleskin00_00_hd.blp"},
                {"index": 1, "path": "Character\\Human\\Female\\HumanFemaleSkin00_01.blp", "retail": "humanfemaleskin00_03_hd.blp"},
                {"index": 2, "path": "Character\\Human\\Female\\HumanFemaleSkin00_02.blp", "retail": "humanfemaleskin00_07_hd.blp"}]},
            "1_0": {"name": "HumanMale", "race": 1, "sex": 0, "skins": [
                {"index": 0, "path": "Character\\Human\\Male\\HumanMaleSkin00_00.blp", "retail": "humanmaleskin00_00_hd.blp"},
                {"index": 1, "path": "Character\\Human\\Male\\HumanMaleSkin00_01.blp", "retail": "humanmalemannequinskin00_05_hd.blp"}]}}}""")
        return client
    }

    private fun store(vararg files: String): File {
        val store = File(tmp.root, "store")
        File(store, "files").mkdirs()
        for (f in files) File(store, "files/$f").writeBytes(ByteArray(4))
        File(store, WrathppRalia.STAMP).writeText("abc\n")
        return store
    }

    @Test fun onlyTheSkinsTheSetHasAFileForAreOffered() {
        val client = game()
        val offered = WrathppRalia.supplied(store("humanfemaleskin00_03_hd.blp", "humanmalemannequinskin00_05_hd.blp", "orcmaleskin00_00_hd.blp"), client)!!
        assertEquals(listOf("1_0", "1_1"), offered.keys.toList())                          // by race, then sex
        assertEquals("HumanFemale" to listOf(1), offered["1_1"])                           // the stock colours it has no file for are not offered
        assertEquals("HumanMale" to listOf(1), offered["1_0"])                             // a mannequin skin is matched by its file name
    }

    @Test fun anUnderwearFileAloneCountsAndEveryOtherModelIsNotFiltered() {
        val offered = WrathppRalia.supplied(store("humanfemalenakedpelvisskin00_07_hd.blp"), game())!!
        assertEquals(listOf("1_1"), offered.keys.toList())
        assertEquals(listOf(2), offered["1_1"]!!.second)
    }

    @Test fun withoutTheImportNothingIsFiltered() {
        val client = game()
        assertNull(WrathppRalia.supplied(File(tmp.root, "none"), client))
        assertEquals("WrathppSkins = {}\n", String(WrathppSkins.build(File(tmp.root, "none"), client).first))
        assertNull(WrathppSkins.build(File(tmp.root, "none"), client).second)
        assertNull(WrathppRalia.supplied(store("orcmaleskin00_00_hd.blp"), client))        // a set with none of the looks' skins: nothing named
    }

    @Test fun aSetThatDidNotGoIntoTheLooksFiltersNothing() {
        // build 399: "ralia FAILED: Failed to allocate..." left the looks' own skins, and the list offered only the set's
        val client = game()
        File(client, "Data/patch-Z.MPQ/${WrathppRalia.STAMP}").delete()
        val store = store("humanfemaleskin00_03_hd.blp")
        assertNull(WrathppRalia.supplied(store, client))
        assertEquals("WrathppSkins = {}\n", String(WrathppSkins.build(store, client).first))
    }

    @Test fun theFileListsPlacesPerModel() {
        val text = String(WrathppSkins.script(mapOf("1_0" to ("HumanMale" to listOf(1, 3)), "1_1" to ("HumanFemale" to listOf(0)))))
        assertEquals("WrathppSkins = {\n\t[\"1_0\"] = { 1, 3 },\n\t[\"1_1\"] = { 0 },\n}\n", text)
    }

    @Test fun theStartReportNamesTheModelsFiltered() {
        val client = game()
        assertEquals(mapOf("1_1" to 3, "1_0" to 2), WrathppSkins.totals(client))           // the undead's and underwear rows are not colours
        val (file, line) = WrathppSkins.build(store("humanfemaleskin00_03_hd.blp", "humanmalemannequinskin00_05_hd.blp"), client)
        assertEquals("Human M 1 of 2, Human F 1 of 3", line)
        assertEquals("WrathppSkins = {\n\t[\"1_0\"] = { 1 },\n\t[\"1_1\"] = { 1 },\n}\n", String(file))
    }
}
