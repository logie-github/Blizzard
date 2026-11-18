package com.logie.blizz.wrathpp

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

/** Wrath++'s downloaded pieces stay on the phone ([WrathppParts]): Play doesn't fetch them again at every start. */
class WrathppPartsTest {
    @get:Rule val tmp = TemporaryFolder()

    @Test fun refreshedOncePerBuildOfTheApp() {
        val files = tmp.newFolder("files")
        assertNull(WrathppParts.refreshedFor(files))
        assertTrue(WrathppParts.due(files, 260))                 // never refreshed: the first Play does
        WrathppParts.markDone(files, 260)
        assertFalse(WrathppParts.due(files, 260))                // the same build: kept as they are
        assertTrue(WrathppParts.due(files, 261))                 // the app was updated: once more
        File(files, "wrathpp-parts-build.txt").writeText("junk")
        assertTrue(WrathppParts.due(files, 260))
    }

    @Test fun installedLooksArtAndAddOnAreNotAskedForAgainWhenNotUpdating() {
        // not update: returns before any request (these would otherwise try the network, and the looks fail without it)
        val client = tmp.newFolder("client-wrathpp")
        val server = tmp.newFolder("server-wrathpp")
        File(client, "Data/${WrathppLooks.PATCH}").mkdirs()
        File(client, "Data/${WrathppLooks.PATCH}/${WrathppLooks.MARKER}").writeText("abc\n")
        File(server, "share/dbc").mkdirs()
        File(server, "share/dbc/${WrathppLooks.MARKER}").writeText("abc\n")
        File(client, "Data/${WrathppArt.PATCH}").mkdirs()
        File(client, "Data/${WrathppArt.PATCH}/${WrathppArt.MARKER}").writeText("def\n")
        File(client, WrathppAddon.MARKER).writeText("123\n")
        File(client, WrathppAddon.EXE).writeText("exe")
        val said = ArrayList<String>()
        WrathppLooks.ensure(client, server, { m, _ -> said += m }, update = false)
        WrathppArt.ensure(client, { m, _ -> said += m }, update = false)
        WrathppAddon.ensure(client, { m, _ -> said += m }, update = false)
        assertEquals(emptyList<String>(), said)
        assertEquals("abc", WrathppLooks.installedSha(client, server))
    }
}
