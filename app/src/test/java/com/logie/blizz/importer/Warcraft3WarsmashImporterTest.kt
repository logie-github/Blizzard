package com.logie.blizz.importer

import com.logie.blizz.Games
import com.logie.blizz.warsmash.WarsmashRuntime
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.File

/** Warcraft III's two games played in Warsmash: what is checked, where they play from, the library's entries, and the move from Winlator. */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class Warcraft3WarsmashImporterTest {
    @get:Rule val tmp = TemporaryFolder()

    private val roc = Warcraft3WarsmashImporter(Warcraft3Importer.Product.ROC)
    private val tft = Warcraft3WarsmashImporter(Warcraft3Importer.Product.TFT)

    private fun env(paths: GamePaths) = ImportEnv(paths, { emptyList() }, { false }, DownloadManager(), GitHubReleases(), null, null, CancelToken(), {})

    /** 1.27 as Blizzard's download leaves it: the programs, war3.mpq and its patch, war3x.mpq for the expansion. */
    private fun classic(dir: File, expansion: Boolean = true, version: String = "1.27.0.52240"): File {
        dir.mkdirs()
        Fixtures.pe(File(dir, "war3.exe"), version)
        Fixtures.mpq(File(dir, "War3.mpq"))
        Fixtures.mpq(File(dir, "War3Patch.mpq"))
        if (expansion) Fixtures.mpq(File(dir, "War3x.mpq"))
        return dir
    }

    /** 1.30: its data in CASC (a Data folder and .build.info), no archives. */
    private fun casc(dir: File): File {
        Fixtures.pe(File(dir, "Warcraft III.exe"), "1.30.4.11274")
        for (d in listOf("data", "indices", "config")) File(dir, "Data/$d").mkdirs()
        File(dir, "Data/data/data.000").writeBytes(ByteArray(128))
        File(dir, "Data/indices/0000000001.idx").writeBytes(ByteArray(64))
        File(dir, "Data/config/ab").writeBytes(ByteArray(64))
        File(dir, ".build.info").writeText("Branch!STRING:0\n")
        return dir
    }

    @Test fun bothGamesAreOneTileAndTheWarsmashModeIsGone() {
        assertEquals(listOf("warcraft3_tft"), Games.find("warcraft3_roc")!!.variants.map { it.id })
        assertNull(Games.find(Warcraft3WarsmashImporter.LEGACY_ID))
        assertEquals(WarsmashRuntime.Edition.ROC, WarsmashRuntime.editionOf("warcraft3_roc"))
        assertEquals(WarsmashRuntime.Edition.TFT, WarsmashRuntime.editionOf("warcraft3_tft"))
        // The engine's own GameVersion: 0 Reign of Chaos, 1 The Frozen Throne.
        assertEquals(0, WarsmashRuntime.Edition.ROC.gameVersion)
        assertEquals(1, WarsmashRuntime.Edition.TFT.gameVersion)
    }

    @Test fun whatWarsmashReadsIsChecked() {
        val base = classic(tmp.newFolder("roc"), expansion = false)
        assertTrue(Warcraft3WarsmashImporter.validateDir(base, WarsmashRuntime.Edition.ROC).filesOk)
        val noExpansion = Warcraft3WarsmashImporter.validateDir(base, WarsmashRuntime.Edition.TFT)
        assertFalse(noExpansion.filesOk)
        assertEquals(Problem.MISSING_EXPANSION, noExpansion.problem)
        // The archives alone are enough: no Windows program or its libraries are needed.
        val bare = tmp.newFolder("bare")
        Fixtures.mpq(File(bare, "war3.mpq")); Fixtures.mpq(File(bare, "war3x.mpq"))
        assertTrue(Warcraft3WarsmashImporter.validateDir(bare, WarsmashRuntime.Edition.TFT).filesOk)
        assertEquals("Warcraft III: The Frozen Throne 1.27.0.52240", Warcraft3WarsmashImporter.validateDir(classic(tmp.newFolder("tft")), WarsmashRuntime.Edition.TFT).clientVersion)
    }

    @Test fun thirtyAndLaterAreRefusedWithWhatToDo() {
        val v = Warcraft3WarsmashImporter.validateDir(casc(tmp.newFolder("casc")), WarsmashRuntime.Edition.TFT)
        assertFalse(v.filesOk)
        assertEquals(Problem.UNSUPPORTED_VERSION, v.problem)
        assertTrue(v.message!!.contains("Retry downloads 1.27"))
        val reforged = Warcraft3WarsmashImporter.validateDir(classic(tmp.newFolder("131"), version = "1.31.1.12164"), WarsmashRuntime.Edition.ROC)
        assertEquals(Problem.UNSUPPORTED_VERSION, reforged.problem)
        assertTrue(reforged.message!!.contains("1.31.1.12164"))
    }

    @Test fun oneInstallPlaysBothAndTheOldWarsmashFolderIsUsed() {
        val paths = GamePaths(tmp.newFolder("files"))
        // Only the old Warsmash mode's folder holds the files: both games play from it, nothing copied.
        val legacy = classic(paths.game(Warcraft3WarsmashImporter.LEGACY_ID))
        assertTrue(roc.detect(env(paths)).installed)
        assertEquals(legacy, Warcraft3WarsmashImporter.installDir(paths, WarsmashRuntime.Edition.TFT))
        // The Frozen Throne's own folder comes first, and Reign of Chaos plays from it too.
        val own = classic(paths.game("warcraft3_tft"))
        assertEquals(own, Warcraft3WarsmashImporter.installDir(paths, WarsmashRuntime.Edition.ROC))
        val entry = roc.registerLaunchEntry(env(paths), roc.validate(env(paths)))
        assertEquals("warcraft3_roc", entry.gameId)
        assertEquals(own.path, entry.installPath)
        assertEquals("War3.mpq", entry.executable)
        assertEquals(WarsmashRuntime.RUNTIME, entry.runtime)
        assertEquals(Stage.IMPORTED_UNTESTED, entry.stage)
        assertEquals(listOf("warcraft3_tft"), roc.companions(env(paths)).map { it.gameId })
        assertTrue(roc.companions(env(paths)).all { it.runtime == WarsmashRuntime.RUNTIME })
    }

    @Test fun aFolderOfThePersonsIsImportedKeepingTheSaves() {
        val paths = GamePaths(tmp.newFolder("files"))
        val old = paths.game("warcraft3_tft").also { it.mkdirs() }
        File(old, "Save").mkdirs(); File(old, "Save/campaign.w3z").writeText("keep")
        val source = tmp.newFolder("source")
        Fixtures.mpq(File(source, "war3.mpq")); Fixtures.mpq(File(source, "war3x.mpq"))
        val supplied = mapOf("install" to Supplied.Picked("install", FileNode(source)))
        val result = ImportPipeline(ImportStateRepository(paths), Library(paths)).run(tft, env(paths), supplied)
        assertTrue(result.toString(), result is ImportPipeline.Result.Done)
        assertEquals("keep", File(old, "Save/campaign.w3z").readText())
        assertTrue(File(old, "war3x.mpq").isFile)
        assertEquals(WarsmashRuntime.RUNTIME, Library(paths).get("warcraft3_tft")!!.runtime)
        // Reign of Chaos is in the library with it.
        assertEquals(WarsmashRuntime.RUNTIME, Library(paths).get("warcraft3_roc")!!.runtime)
    }

    @Test fun nothingGivenAsksForTheClassicGame() {
        val paths = GamePaths(tmp.newFolder("files"))
        val missing = tft.getMissingInputs(env(paths), tft.detect(env(paths)), emptyMap())
        assertEquals("install", missing.single().id)
        assertTrue(missing.single().prompt.contains("1.22 to 1.29"))
    }

    @Test fun winlatorEntriesMoveToWarsmashWithTheSameFiles() {
        val paths = GamePaths(tmp.newFolder("files"))
        val library = Library(paths)
        val repo = ImportStateRepository(paths)
        val dir = classic(paths.game("warcraft3_tft"))
        val before = File(dir, "War3.mpq").readBytes()
        for (id in listOf("warcraft3_roc", "warcraft3_tft")) {
            library.put(LibraryEntry(id, id, listOf("WAR3"), "1.27", dir.path, "Frozen Throne.exe", LibraryEntry.RUNTIME_WINLATOR, "-window", Stage.IMPORTED_UNTESTED, null, "warcraft3"))
        }
        Warcraft3WarsmashImporter.migrate(paths, library, repo)
        for (id in listOf("warcraft3_roc", "warcraft3_tft")) {
            val e = library.get(id)!!
            assertEquals(WarsmashRuntime.RUNTIME, e.runtime)
            assertEquals(dir.path, e.installPath)
            assertEquals("War3.mpq", e.executable)
        }
        assertTrue(before.contentEquals(File(dir, "War3.mpq").readBytes()))
        // Again: nothing changes.
        Warcraft3WarsmashImporter.migrate(paths, library, repo)
        assertEquals(WarsmashRuntime.RUNTIME, library.get("warcraft3_roc")!!.runtime)
    }

    @Test fun aThirtyInstallLeavesTheLibraryAndSaysWhy() {
        val paths = GamePaths(tmp.newFolder("files"))
        val library = Library(paths)
        val repo = ImportStateRepository(paths)
        val dir = casc(paths.game("warcraft3_roc"))
        library.put(LibraryEntry("warcraft3_roc", "Reign of Chaos", listOf("WAR3"), "1.30", dir.path, "Warcraft III.exe", LibraryEntry.RUNTIME_WINLATOR, "", Stage.IMPORTED_UNTESTED, null, "warcraft3"))
        Warcraft3WarsmashImporter.migrate(paths, library, repo)
        assertNull(library.get("warcraft3_roc"))
        val record = repo.load("warcraft3_roc")
        assertEquals(Problem.UNSUPPORTED_VERSION, record.problem)
        assertTrue(record.message!!.contains("1.30"))
        assertTrue(dir.isDirectory)
    }
}
