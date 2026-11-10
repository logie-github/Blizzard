package com.logie.blizz.importer

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

/** The phone's storage as the importers read it: Android's document ids as paths, and a search that leaves photos, music and other apps' files alone. */
class PhoneStorageTest {
    @get:Rule val tmp = TemporaryFolder()

    @Test fun aDocumentIdOfThePhonesStorageIsAPath() {
        val root = File("/storage/emulated/0")
        // The phone's own files (reports of 4 to 10 November 2026).
        assertEquals(File(root, "Roms/Warcraft/SC2/Starcraft II/Setup.exe"), PhoneStorage.pathOf("primary:Roms/Warcraft/SC2/Starcraft II/Setup.exe", root))
        assertEquals(File(root, "Roms/Warcraft/SC2/Starcraft II"), PhoneStorage.pathOf("primary:Roms/Warcraft/SC2/Starcraft II", root))
        assertEquals(root, PhoneStorage.pathOf("primary:", root))
        // A memory card.
        assertEquals(File("/storage/1A2B-3C4D/Games/x.iso"), PhoneStorage.pathOf("1A2B-3C4D:Games/x.iso", root))
        // Nothing else: another provider's id, a path that climbs out.
        assertNull(PhoneStorage.pathOf("msf:1234", root))
        assertNull(PhoneStorage.pathOf("raw", root))
        assertNull(PhoneStorage.pathOf("primary:Roms/../../data/x", root))
    }

    @Test fun theSearchLeavesPhotosMusicOtherAppsAndHiddenFoldersAlone() {
        val root = tmp.newFolder("0")
        fun file(path: String) = File(root, path).apply { parentFile!!.mkdirs(); writeText("x") }
        file("Roms/Warcraft/setup_warcraft_ii_2.02_v5_(78104).exe")
        file("Roms/Warcraft/setup_warcraft_ii_2.02_v5_(78104)-1.bin")
        file("Download/DIABDAT.MPQ")
        file("DCIM/Camera/1.jpg")
        file("Android/data/com.other/files/setup.exe")
        file("Music/a.mp3")
        file(".thumbnails/b.exe")
        file("Download/.cache/c.exe")
        // Only the top folders of those names are passed over: a game's own "Movies" folder is searched.
        file("Games/Warcraft III/Movies/HumanOp.mpq")
        val found = PhoneStorage.searchRoot(root).walk(6).map { it.localFile()!!.relativeTo(root).path }.toList().sorted()
        assertEquals(
            listOf(
                "Download/DIABDAT.MPQ",
                "Games/Warcraft III/Movies/HumanOp.mpq",
                "Roms/Warcraft/setup_warcraft_ii_2.02_v5_(78104)-1.bin",
                "Roms/Warcraft/setup_warcraft_ii_2.02_v5_(78104).exe",
            ),
            found,
        )
        // A file found there has its neighbours: the installer sees its data file.
        val setup = PhoneStorage.searchRoot(root).walk(6).first { it.name.endsWith(".exe") }
        assertTrue(setup.siblings()!!.any { it.name.endsWith("-1.bin") })
    }

    @Test fun aPickedFolderWithNothingInItGivesWayToWhatTheSearchFound() {
        val empty = FileNode(tmp.newFolder("Starcraft II"))
        val found = FileNode(tmp.newFolder("SC2").also { File(it, "Setup.exe").writeText("MZ") })
        assertEquals(found, InstallerRun.sourceOf(mapOf("install" to Supplied.Picked("install", empty)), found))
        // Nothing found: the empty folder is still what was picked (and is said to be empty).
        assertEquals(empty, InstallerRun.sourceOf(mapOf("install" to Supplied.Picked("install", empty)), null))
        // A picked folder with files in it is used, whatever the search found.
        val picked = FileNode(tmp.newFolder("mine").also { File(it, "Setup.exe").writeText("MZ") })
        assertEquals(picked, InstallerRun.sourceOf(mapOf("install" to Supplied.Picked("install", picked)), found))
    }
}
