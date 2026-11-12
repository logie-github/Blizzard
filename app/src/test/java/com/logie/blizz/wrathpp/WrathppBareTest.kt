package com.logie.blizz.wrathpp

import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

/** The women's underwear taken out of Wrath++'s character table ([WrathppBare]): their rows kept, without textures; the men's as they were. */
class WrathppBareTest {
    @get:Rule val tmp = TemporaryFolder()

    private fun row(id: Int, race: Int, sex: Int, section: Int, a: String, b: String, colour: Int): Array<Any> = arrayOf(id, race, sex, section, a, b, "", 17, 0, colour)

    @Test fun theWomensRowsLoseTheirTexturesAndKeepTheirPlace() {
        val client = tmp.newFolder("client-wrathpp")
        val table = File(client, "Data/patch-Z.MPQ/DBFilesClient/CharSections.dbc").apply { parentFile!!.mkdirs() }
        table.writeBytes(WrathppUndead.Dbc(WrathppUndead.KINDS, mutableListOf(
            row(1, 1, 1, 0, "HF\\Skin00.blp", "", 0), row(2, 1, 1, 4, "HF\\Pelvis00.blp", "HF\\Torso00.blp", 0), row(3, 1, 1, 4, "", "HF\\Torso01.blp", 1),
            row(4, 1, 0, 4, "HM\\Pelvis00.blp", "", 0), row(5, 5, 1, 4, "", "", 0), row(6, 1, 1, 1, "HF\\FaceLower00.blp", "HF\\FaceUpper00.blp", 0))).write())
        assertEquals(2, WrathppBare.apply(client))
        val rows = WrathppUndead.Dbc.read(table.readBytes(), WrathppUndead.KINDS).rows
        assertEquals(6, rows.size)
        assertEquals(listOf("", ""), rows.first { it[0] == 2 }.let { listOf(it[4], it[5]) })
        assertEquals(listOf("", ""), rows.first { it[0] == 3 }.let { listOf(it[4], it[5]) })
        assertEquals("HM\\Pelvis00.blp", rows.first { it[0] == 4 }[4])                 // a man's
        assertEquals("HF\\Skin00.blp", rows.first { it[0] == 1 }[4])                   // her skin
        assertEquals("HF\\FaceUpper00.blp", rows.first { it[0] == 6 }[5])              // her face
        val written = table.lastModified()
        assertEquals(0, WrathppBare.apply(client))                                     // again: nothing to do, nothing written
        assertEquals(written, table.lastModified())
        assertEquals(0, WrathppBare.apply(tmp.newFolder("no-looks")))
    }
}
