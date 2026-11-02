package com.logie.blizz.importer

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.File

/** Warcraft I and II from GOG's files, converted for Stratagus by a fake data tool. */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class WarcraftImporterTest {
    @get:Rule val tmp = TemporaryFolder()
    private val paths by lazy { GamePaths(tmp.newFolder("files")) }
    private var innoextract: Innoextract? = null
    private val roots = ArrayList<SourceNode>()

    private fun env() = ImportEnv(
        paths = paths, searchRoots = { roots.toList() }, online = { false }, downloads = DownloadManager(), releases = GitHubReleases(),
        legacy = null, innoextract = innoextract, cancel = CancelToken(), progress = {},
    )

    private fun run(importer: GameImporter, source: File?, repair: Boolean = false) =
        ImportPipeline(ImportStateRepository(paths), Library(paths)).run(importer, env(), source?.let { mapOf("install" to Supplied.Picked("install", FileNode(it))) } ?: emptyMap(), repair)

    private fun filesOf(dir: File) = dir.walkTopDown().filter { it.isFile }.associate { it.relativeTo(dir).invariantSeparatorsPath to it.readBytes() }

    private fun assertDone(result: ImportPipeline.Result, id: String): LibraryEntry {
        assertTrue(result.toString(), result is ImportPipeline.Result.Done)
        val entry = (result as ImportPipeline.Result.Done).entry
        assertEquals(id, entry.gameId)
        assertEquals("stratagus", entry.runtime)
        assertEquals("extracted", entry.executable)
        assertEquals(id, entry.controlProfile)
        assertEquals(paths.game(id).path, entry.installPath)
        assertEquals(Stage.IMPORTED_UNTESTED, entry.stage)
        assertEquals(Stage.IMPORTED_UNTESTED, result.record.stage)
        assertTrue(File(paths.game(id), "extracted").isFile)
        assertTrue(File(paths.game(id), "scripts").isDirectory)
        assertFalse(paths.staging(id).exists())
        assertFalse(File(paths.staging, "$id-scratch").exists())
        assertNotNull(Library(paths).get(id))
        return entry
    }

    // Warcraft I -------------------------------------------------------------------------------

    @Test fun warcraft1FromAnInstalledGogFolder() {
        val tools = WarcraftFixtures.FakeTools()
        val folder = WarcraftFixtures.wc1(tmp.newFolder("GOG Games", "Warcraft Orcs and Humans"))
        assertDone(run(Warcraft1Importer(tools), tmp.root.resolve("GOG Games")), "warcraft")
        assertEquals(WargusGame.WAR1, tools.game)
        assertTrue(tools.sourceNames.toString(), "DATA/DATA.WAR" in tools.sourceNames && "WAR.EXE" in tools.sourceNames)
        assertTrue(folder.exists())
    }

    @Test fun warcraft1FromAZipWithAFolderInIt() {
        val tools = WarcraftFixtures.FakeTools()
        val src = WarcraftFixtures.wc1(tmp.newFolder("src"))
        val zip = Fixtures.zip(tmp.newFile("wc1.zip"), filesOf(src).mapKeys { "Warcraft/${it.key}" })
        assertDone(run(Warcraft1Importer(tools), zip), "warcraft")
        assertEquals(1, tools.calls)
    }

    @Test fun warcraft1FromGogsInstallerWithLowerCaseNamesFixedForTheTool() {
        val tools = WarcraftFixtures.FakeTools()
        val folder = tmp.newFolder("installer")
        Fixtures.pe(File(folder, "setup_warcraft_orcs_and_humans_1.2_(12345).exe"), "1.0.0.0")
        File(folder, "setup_warcraft_orcs_and_humans_1.2_(12345)-1.bin").writeBytes(ByteArray(1_200_000))
        val installed = WarcraftFixtures.wc1(tmp.newFolder("installed"), lower = true)
        innoextract = Innoextract(fakeInnoextract(installed, "app"))
        assertDone(run(Warcraft1Importer(tools), folder), "warcraft")
        // The tool is given the names GOG ships (innoextract writes them lower-case).
        assertTrue(tools.sourceNames.toString(), "DATA/DATA.WAR" in tools.sourceNames && "WAR.EXE" in tools.sourceNames)
    }

    @Test fun warcraft2FilesAreNotWarcraft1() {
        val folder = WarcraftFixtures.wc2(tmp.newFolder("wc2"))
        val result = run(Warcraft1Importer(WarcraftFixtures.FakeTools()), folder) as ImportPipeline.Result.Failed
        assertEquals(Problem.MISSING_SOURCE_DATA, result.error.problem)
        assertTrue(result.error.message!!, result.error.message!!.contains("Select your Warcraft: Orcs & Humans files from GOG"))
        assertFalse(paths.game("warcraft").exists())
    }

    // Warcraft II ------------------------------------------------------------------------------

    @Test fun warcraft2FromAnInstalledGogFolder() {
        val tools = WarcraftFixtures.FakeTools()
        val folder = WarcraftFixtures.wc2(tmp.newFolder("Warcraft II"))
        val entry = assertDone(run(Warcraft2Importer(tools), folder), "warcraft2")
        assertEquals(WargusGame.WAR2, tools.game)
        assertTrue(tools.sourceNames.toString(), tools.sourceNames.containsAll(listOf("Install.mpq", "War2Dat.mpq", "Support/TOMES/TOME.1", "Support/TOMES/TOME.4")))
        assertEquals("Warcraft II: Battle.net Edition", entry.title)
    }

    @Test fun warcraft2FromAZipAndFromAnInstallerWithLowerCaseNames() {
        val tools = WarcraftFixtures.FakeTools()
        val src = WarcraftFixtures.wc2(tmp.newFolder("src"), lower = true)
        // A zip of lower-case names: the tool still gets the names it opens by.
        assertDone(run(Warcraft2Importer(tools), Fixtures.zip(tmp.newFile("wc2.zip"), filesOf(src))), "warcraft2")
        assertTrue(tools.sourceNames.toString(), tools.sourceNames.containsAll(listOf("Install.mpq", "Support/TOMES/TOME.2", "Warcraft II BNE.exe")))

        val folder = tmp.newFolder("installer")
        Fixtures.pe(File(folder, "setup_warcraft_ii_battle.net_edition_2.0.exe"), "1.0.0.0")
        File(folder, "setup_warcraft_ii_battle.net_edition_2.0-1.bin").writeBytes(ByteArray(1_200_000))
        innoextract = Innoextract(fakeInnoextract(src, "app"))
        paths.game("warcraft2").deleteRecursively()
        assertDone(run(Warcraft2Importer(tools), folder), "warcraft2")
        assertEquals(2, tools.calls)
    }

    @Test fun anIncompleteWarcraft2FolderNamesWhatIsMissing() {
        val folder = WarcraftFixtures.wc2(tmp.newFolder("short"), tomes = 2)
        val result = run(Warcraft2Importer(WarcraftFixtures.FakeTools()), folder) as ImportPipeline.Result.Failed
        assertEquals(Problem.MISSING_SOURCE_DATA, result.error.problem)
        assertTrue(result.error.message!!, result.error.message!!.contains("TOME.3"))
    }

    // Both -------------------------------------------------------------------------------------

    @Test fun anEmptyFolderIsRefusedWithThePrompt() {
        val result = run(Warcraft2Importer(WarcraftFixtures.FakeTools()), tmp.newFolder("nothing")) as ImportPipeline.Result.Failed
        assertEquals(Problem.MISSING_SOURCE_DATA, result.error.problem)
        assertEquals(ImportPipeline.outcomeFor(Problem.MISSING_SOURCE_DATA), result.record.outcome)
        assertTrue(result.error.message!!.contains("Select your Warcraft II: Battle.net Edition files from GOG"))
    }

    @Test fun withoutFilesThePersonIsAsked() {
        val result = run(Warcraft1Importer(WarcraftFixtures.FakeTools()), null) as ImportPipeline.Result.Waiting
        val missing = result.missing.single()
        assertEquals("install", missing.id)
        assertEquals(PickKind.FILE_OR_FOLDER, missing.kind)
        assertTrue(missing.prompt.contains("Warcraft: Orcs & Humans"))
    }

    @Test fun anInstalledGameInASearchedFolderIsDetected() {
        WarcraftFixtures.wc1(tmp.newFolder("Games", "WC1"))
        roots += FileNode(tmp.root.resolve("Games"))
        val detection = Warcraft1Importer(WarcraftFixtures.FakeTools()).detect(env())
        assertFalse(detection.installed)
        assertEquals("WC1", detection.found["install"]!!.name)
        assertNull(Warcraft2Importer(WarcraftFixtures.FakeTools()).detect(env()).found["install"])
    }

    @Test fun aFailedConversionShowsTheToolsLastOutputAndChangesNothing() {
        val good = WarcraftFixtures.FakeTools()
        val folder = WarcraftFixtures.wc2(tmp.newFolder("wc2"))
        assertDone(run(Warcraft2Importer(good), folder), "warcraft2")
        val before = filesOf(paths.game("warcraft2"))

        val bad = WarcraftFixtures.FakeTools(code = 3, output = listOf("Reading Install.mpq", "Cannot open Support/TOMES/TOME.2"))
        val result = run(Warcraft2Importer(bad), folder, repair = true) as ImportPipeline.Result.Failed
        assertEquals(Problem.CORRUPT_ARCHIVE, result.error.problem)
        assertTrue(result.error.detail!!, result.error.detail!!.contains("Cannot open Support/TOMES/TOME.2"))
        assertTrue(result.error.message!!.contains("code 3"))
        assertEquals(before.keys, filesOf(paths.game("warcraft2")).keys)
        assertFalse(paths.staging("warcraft2").exists())
        assertFalse(File(paths.staging, "warcraft2-scratch").exists())
    }

    @Test fun aToolThatEndsWithoutTheMarkerIsAFailure() {
        val result = run(Warcraft1Importer(WarcraftFixtures.FakeTools(writeMarker = false)), WarcraftFixtures.wc1(tmp.newFolder("wc1"))) as ImportPipeline.Result.Failed
        assertEquals(Problem.CORRUPT_ARCHIVE, result.error.problem)
        assertFalse(paths.game("warcraft").exists())
    }

    @Test fun withoutTheToolsThatIsSaid() {
        ConversionTools.installed = null
        val result = run(Warcraft1Importer(), WarcraftFixtures.wc1(tmp.newFolder("wc1"))) as ImportPipeline.Result.Failed
        assertEquals(Problem.MISSING_RUNTIME_DEPENDENCY, result.error.problem)
    }

    @Test fun preferencesAndSavesInTheGameFolderSurviveAReimportAndAReset() {
        val folder = WarcraftFixtures.wc1(tmp.newFolder("wc1"))
        val importer = Warcraft1Importer(WarcraftFixtures.FakeTools())
        assertDone(run(importer, folder), "warcraft")
        File(paths.game("warcraft"), "war1gus/save").mkdirs()
        File(paths.game("warcraft"), "war1gus/save/slot1.sav").writeText("mine")
        File(paths.game("warcraft"), "war1gus/preferences.lua").writeText("prefs")

        assertDone(run(importer, folder, repair = true), "warcraft")
        assertEquals("mine", File(paths.game("warcraft"), "war1gus/save/slot1.sav").readText())

        GameReset.reset(paths, "warcraft", importer.keptInGame)
        assertEquals(listOf("war1gus"), paths.game("warcraft").list()!!.toList())
        assertEquals("prefs", File(paths.game("warcraft"), "war1gus/preferences.lua").readText())
        assertNull(Library(paths).get("warcraft"))
    }

    @Test fun validationNeedsTheMarkerAndConvertedData() {
        val importer = Warcraft2Importer(WarcraftFixtures.FakeTools())
        val dir = tmp.newFolder("converted")
        assertFalse(importer.validateDir(dir).filesOk)
        File(dir, "extracted").writeText("")
        assertFalse(importer.validateDir(dir).filesOk)
        File(dir, "graphics").mkdirs()
        File(dir, "graphics/a.png").writeText("x")
        assertTrue(importer.validateDir(dir).filesOk)
    }

    @Test fun caseFixRenamesToTheGivenCase() {
        val root = tmp.newFolder("case")
        File(root, "support/tomes").mkdirs()
        File(root, "support/tomes/tome.1").writeText("x")
        CaseFix.apply(root, "Support")
        CaseFix.apply(root, "Support/TOMES")
        CaseFix.apply(root, "Support/TOMES/TOME.1")
        assertTrue(File(root, "Support/TOMES/TOME.1").isFile)
        assertNull(CaseFix.find(root, "Support/TOMES/TOME.9"))
        assertEquals(listOf("Support"), root.list()!!.toList())
    }

    /** A stand-in for innoextract: writes [game]'s files into <output>/[sub], as GOG's installers put them in app/. */
    private fun fakeInnoextract(game: File, sub: String): File {
        val script = File(tmp.root, "inno-${System.nanoTime()}.sh")
        script.writeText(
            "#!/bin/sh\nwhile [ \"\$1\" != --output-dir ]; do shift; done; out=\"\$2\"\nmkdir -p \"\$out/$sub\"\ncp -r '${game.path}'/. \"\$out/$sub\"/\n"
        )
        script.setExecutable(true)
        return script
    }
}
