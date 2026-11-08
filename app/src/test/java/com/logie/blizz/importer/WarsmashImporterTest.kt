package com.logie.blizz.importer

import com.logie.blizz.Games
import com.logie.blizz.warsmash.WarsmashRuntime
import org.junit.Assert.*
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.File

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class WarsmashImporterTest {
    @get:Rule val tmp = TemporaryFolder()
    private fun env(paths: GamePaths) = ImportEnv(paths, { emptyList() }, { false }, DownloadManager(), GitHubReleases(), null, null, CancelToken(), {})
    private fun data(dir: File): File {
        dir.mkdirs()
        Fixtures.mpq(File(dir, "War3.mpq")); Fixtures.mpq(File(dir, "War3x.mpq"))
        return dir
    }
    @Test fun warsmashIsTheThirdWarcraftMode() {
        val base = Games.find("warcraft3_roc")!!
        assertEquals(listOf("warcraft3_tft", WarsmashImporter.ID), base.variants.map { it.id })
        assertEquals("Warsmash", Games.find(WarsmashImporter.ID)!!.variantLabel)
    }
    @Test fun reusesExistingClassicInstallWithoutChangingWindowsEntry() {
        val paths = GamePaths(tmp.newFolder("files"))
        val dir = data(paths.game("warcraft3_tft"))
        val importer = WarsmashImporter()
        assertTrue(importer.detect(env(paths)).installed)
        val entry = importer.registerLaunchEntry(env(paths), importer.validate(env(paths)))
        assertEquals(dir.path, entry.installPath)
        assertEquals("War3.mpq", entry.executable)
        assertEquals(WarsmashRuntime.RUNTIME, entry.runtime)
        assertEquals(Stage.IMPORTED_UNTESTED, entry.stage)
        assertFalse(paths.game(WarsmashImporter.ID).exists())
    }
    @Test fun cascAndMissingExpansionAreRejected() {
        val dir = tmp.newFolder("casc")
        File(dir, "Data/data").mkdirs(); File(dir, ".build.info").writeText("fixture")
        assertFalse(WarsmashImporter.validateDir(dir).filesOk)
        Fixtures.mpq(File(dir, "war3.mpq"))
        assertFalse(WarsmashImporter.validateDir(dir).filesOk)
    }
    @Test fun separateImportPreservesExistingSaveAndDoesNotTouchOtherModes() {
        val paths = GamePaths(tmp.newFolder("files"))
        val own = data(paths.game(WarsmashImporter.ID))
        File(own, "Save").mkdirs(); File(own, "Save/player.sav").writeText("keep")
        val source = data(tmp.newFolder("source"))
        val importer = WarsmashImporter()
        importer.importFiles(env(paths), importer.detect(env(paths)), mapOf("install" to Supplied.Picked("install", FileNode(source))))
        assertEquals("keep", File(own, "Save/player.sav").readText())
        assertFalse(paths.game("warcraft3_tft").exists())
        assertTrue(WarsmashImporter.validateDir(source).filesOk)
    }
}
