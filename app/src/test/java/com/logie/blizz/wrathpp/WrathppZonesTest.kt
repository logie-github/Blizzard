package com.logie.blizz.wrathpp

import com.logie.blizz.wow.WowLayout
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

class WrathppZonesTest {
    @get:Rule val tmp = TemporaryFolder()

    private fun layout() = WowLayout(tmp.newFolder("games"), tmp.newFolder("export"))

    private fun complete(folder: File) {
        File(folder, "server/maps").mkdirs()
        File(folder, "client").mkdirs()
        File(folder, "client/files.txt").writeText("x")
        File(folder, "TAG").writeText("cata-zones-x")
    }

    @Test fun thePinnedPackageIsTheOneThatIsPublished() {
        assertEquals("cata-zones-b2a8428dfe7e", WrathppZones.TAG)
        assertEquals(64, WrathppZones.SHA256.length)
        assertTrue(WrathppZones.SIZE in 1..Long.MAX_VALUE && WrathppZones.UNPACKED > WrathppZones.SIZE)
    }

    @Test fun aPackageIsOneOnlyWithItsTagFileListAndMaps() {
        val layout = layout()
        layout.zones.mkdirs()
        assertFalse(WrathppZones.looksComplete(layout.zones))
        complete(layout.zones)
        assertTrue(WrathppZones.looksComplete(layout.zones))
    }

    @Test fun itIsInstalledOnlyWhenTheMarkerNamesThisBuildsPackageAndTheFolderIsWhole() {
        val layout = layout()
        complete(layout.zones)
        assertFalse(WrathppZones.isInstalled(layout))
        File(layout.zones, WrathppZones.MARKER).writeText("b".repeat(64))
        assertFalse(WrathppZones.isInstalled(layout))
        File(layout.zones, WrathppZones.MARKER).writeText(WrathppZones.SHA256)
        assertTrue(WrathppZones.isInstalled(layout))
        File(layout.zones, "server/maps").deleteRecursively()
        assertFalse(WrathppZones.isInstalled(layout))
    }

    @Test fun ensureDoesNothingForAnInstalledPackage() {
        val layout = layout()
        complete(layout.zones)
        File(layout.zones, WrathppZones.MARKER).writeText(WrathppZones.SHA256)
        val said = ArrayList<String>()
        WrathppZones.ensure(layout) { text, _ -> said.add(text) }
        assertTrue(said.isEmpty())
    }
}
