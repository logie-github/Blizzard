package com.logie.blizz.importer

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

/** Reset an installation at any time; and the archives' contents, not just their headers, are checked. */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class ResetTest {
    @get:Rule val tmp = TemporaryFolder()
    private val paths by lazy { GamePaths(tmp.newFolder("files")) }

    private fun env() = ImportEnv(
        paths = paths, searchRoots = { emptyList() }, online = { false }, downloads = DownloadManager(), releases = GitHubReleases(),
        legacy = null, innoextract = null, cancel = CancelToken(), progress = {},
    )

    private fun run(importer: GameImporter, source: File?) =
        ImportPipeline(ImportStateRepository(paths), Library(paths)).run(importer, env(), source?.let { mapOf("install" to Supplied.Picked("install", FileNode(it))) } ?: emptyMap())

    @Test fun resetTakesAGameBackToNotInstalledKeepingTheOwnersFiles() {
        val importer = StarCraftClassicImporter()
        run(importer, Fixtures.starcraftInstall(tmp.newFolder("sc")))
        File(paths.game("starcraft"), "characters/Hero.spc").apply { parentFile!!.mkdirs(); writeText("me") }
        File(paths.game("starcraft"), "save/campaign.snx").apply { parentFile!!.mkdirs(); writeText("played") }
        File(paths.game("starcraft"), "maps/replays/last.rep").apply { parentFile!!.mkdirs(); writeText("replay") }
        File(paths.game("starcraft"), "maps/custom.scm").apply { parentFile!!.mkdirs(); writeText("map") }

        GameReset.reset(paths, "starcraft", importer.keptInGame)

        assertNull(Library(paths).get("starcraft"))
        assertEquals(Stage.NOT_INSTALLED, ImportStateRepository(paths).load("starcraft").stage)
        assertFalse(File(paths.game("starcraft"), "StarCraft.exe").exists())
        assertFalse(File(paths.game("starcraft"), "StarDat.mpq").exists())
        assertFalse(File(paths.game("starcraft"), "maps/custom.scm").exists())
        assertEquals("me", File(paths.game("starcraft"), "characters/Hero.spc").readText())
        assertEquals("played", File(paths.game("starcraft"), "save/campaign.snx").readText())
        assertEquals("replay", File(paths.game("starcraft"), "maps/replays/last.rep").readText())

        // Importing again works, and the owner's files are still there.
        val again = run(importer, Fixtures.starcraftInstall(tmp.newFolder("sc-again")))
        assertTrue(again.toString(), again is ImportPipeline.Result.Done)
        assertEquals("me", File(paths.game("starcraft"), "characters/Hero.spc").readText())
    }

    @Test fun resetLeavesSavesAndSettingsAndDownloads() {
        val importer = Diablo2ClassicImporter()
        run(importer, Fixtures.diablo2Install(tmp.newFolder("d2")))
        File(paths.saves("diablo2"), "import/Hero.d2s").apply { parentFile!!.mkdirs(); writeText("hero") }
        File(paths.downloads, "legacy/piece").apply { parentFile!!.mkdirs(); writeText("cached") }
        GameReset.reset(paths, "diablo2", importer.keptInGame)
        assertFalse(paths.game("diablo2").exists())
        assertEquals("hero", File(paths.saves("diablo2"), "import/Hero.d2s").readText())
        assertEquals("cached", File(paths.downloads, "legacy/piece").readText())
    }

    @Test fun resetClearsAHalfMadeImportToo() {
        paths.staging("diablo").apply { mkdirs(); File(this, "x").writeText("half") }
        File(paths.staging, "diablo-scratch").apply { mkdirs(); File(this, "y").writeText("scratch") }
        ImportStateRepository(paths).update("diablo") { it.copy(stage = Stage.FAILED, problem = Problem.DOWNLOAD_FAILED) }
        GameReset.reset(paths, "diablo")
        assertFalse(paths.staging("diablo").exists())
        assertFalse(File(paths.staging, "diablo-scratch").exists())
        assertEquals(Stage.NOT_INSTALLED, ImportStateRepository(paths).load("diablo").stage)
        // Resetting what was never installed is fine.
        GameReset.reset(paths, "starcraft2")
    }

    // The archives' contents ------------------------------------------------------------------------

    @Test fun anArchiveWithoutTheFilesTheGameOpensFirstIsCaught() {
        val sc = Fixtures.starcraftInstall(tmp.newFolder("sc"))
        // StarDat.mpq with a header and a hash table, but no font\font.gid: StarCraft's "unable to open a required file".
        Fixtures.mpq(File(sc, "StarDat.mpq"), listOf("arr\\units.dat"))
        val result = run(StarCraftClassicImporter(), sc) as ImportPipeline.Result.Failed
        assertEquals(Problem.CORRUPT_ARCHIVE, result.error.problem)
        assertTrue(result.error.message!!, result.error.message!!.contains("font\\font.gid"))
        assertTrue(result.error.message!!.contains("Reset the installation"))
        assertNull(Library(paths).get("starcraft"))
    }

    @Test fun anArchiveCutShortIsCaught() {
        val sc = Fixtures.starcraftInstall(tmp.newFolder("sc"))
        File(sc, "StarDat.mpq").let { f -> f.writeBytes(f.readBytes().copyOf(40)) }
        val result = run(StarCraftClassicImporter(), sc) as ImportPipeline.Result.Failed
        assertEquals(Problem.CORRUPT_ARCHIVE, result.error.problem)
        assertTrue(result.error.message!!.contains("can't be read"))
    }

    @Test fun theHashTableReaderFindsWhatsThereAndOnlyThat() {
        val file = Fixtures.mpq(tmp.newFile("a.mpq"), listOf("font\\font.gid", "arr\\units.dat", "rez\\glumain.bin"))
        val has = MpqContents.has(file, listOf("font\\font.gid", "FONT\\FONT.GID", "arr\\units.dat", "arr\\nothing.dat"))!!
        assertEquals(mapOf("font\\font.gid" to true, "FONT\\FONT.GID" to true, "arr\\units.dat" to true, "arr\\nothing.dat" to false), has)
        assertNull(MpqContents.has(tmp.newFile("not.mpq").apply { writeText("no") }, listOf("x")))
        // An archive after a program (a disc's INSTALL.EXE).
        val exe = tmp.newFile("INSTALL.EXE").apply { writeBytes(ByteArray(1024) + file.readBytes()) }
        assertEquals(true, MpqContents.has(exe, listOf("font\\font.gid"))!!["font\\font.gid"])
    }
}
