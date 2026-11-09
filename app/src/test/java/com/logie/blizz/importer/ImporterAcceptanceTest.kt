package com.logie.blizz.importer

import com.logie.blizz.controls.Catalog
import com.logie.blizz.controls.Trigger
import com.logie.blizz.game.Offline
import com.logie.blizz.ui.statusLabel
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.File

/**
 * The importers' acceptance tests, on fixtures shaped like the games' files ([Fixtures]); none of
 * this is the games themselves, and none of it runs Wine. Each test names the requirement it covers.
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class ImporterAcceptanceTest {
    @get:Rule val tmp = TemporaryFolder()

    private lateinit var paths: GamePaths
    private val roots = ArrayList<SourceNode>()
    private var online = false
    private var releasesCalled = 0
    private var cancel = CancelToken()
    private var legacy: LegacyDownloader? = null

    private fun setUp(): GamePaths {
        paths = GamePaths(tmp.newFolder("files"))
        return paths
    }

    private fun env() = ImportEnv(
        paths = paths,
        searchRoots = { roots.toList() },
        online = { online },
        downloads = DownloadManager(),
        releases = object : GitHubReleases() {
            override fun latest(repo: String): List<ReleaseAsset> {
                releasesCalled++
                throw ImportException(Problem.DOWNLOAD_FAILED, "offline in tests")
            }
        },
        legacy = legacy,
        innoextract = null,
        cancel = cancel,
        progress = {},
    )

    private fun pipeline() = ImportPipeline(ImportStateRepository(paths), Library(paths))
    private fun run(importer: GameImporter, supplied: Map<String, Supplied> = emptyMap(), repair: Boolean = false) = pipeline().run(importer, env(), supplied, repair)
    private fun picked(id: String, file: File) = id to Supplied.Picked(id, FileNode(file))

    // 1. An existing valid installation is detected ---------------------------------------------

    @Test fun existingInstallationsAreDetected() {
        setUp()
        Fixtures.diablo2Install(paths.game("diablo2"))
        Fixtures.starcraftInstall(paths.game("starcraft"))
        Fixtures.starcraft2Install(paths.game("starcraft2"))
        File(paths.game("diablo"), "x").parentFile!!.mkdirs()
        Fixtures.zip(File(tmp.root, "dx.zip"), emptyMap())
        for (importer in listOf(Diablo2ClassicImporter(), StarCraftClassicImporter(), StarCraft2OfflineImporter())) {
            assertTrue(importer.gameId, importer.detect(env()).installed)
            val result = run(importer)
            assertTrue("${importer.gameId}: $result", result is ImportPipeline.Result.Done)
        }
    }

    @Test fun anInstallationInASearchedFolderIsFoundAndImported() {
        setUp()
        val folder = tmp.newFolder("Download")
        Fixtures.diablo2Install(File(folder, "Games/Diablo II"))
        roots += FileNode(folder)
        val result = run(Diablo2ClassicImporter())
        assertTrue(result.toString(), result is ImportPipeline.Result.Done)
        assertEquals(Stage.READY, (result as ImportPipeline.Result.Done).record.stage)
        assertTrue(File(paths.game("diablo2"), "Game.exe").isFile)
    }

    // 2 and 3. Missing data identified, with the right prompt ------------------------------------

    @Test fun missingFilesAreAskedForWithTheRightPrompts() {
        setUp()
        val d1 = run(Diablo1DevilutionXImporter()) as ImportPipeline.Result.Waiting
        assertEquals(listOf("engine", "data", "hellfire"), d1.missing.map { it.id })
        assertEquals("Select your Diablo I GOG offline installer, original game-data folder, or DIABDAT.MPQ.", d1.missing[1].prompt)
        assertEquals("Hellfire game data was not found. Import Hellfire files, or continue with Diablo I only?", d1.missing[2].prompt)
        assertTrue(d1.missing[2].optional)

        val d2 = run(Diablo2ClassicImporter()) as ImportPipeline.Result.Waiting
        assertEquals(listOf("install"), d2.missing.map { it.id })

        val sc = run(StarCraftClassicImporter()) as ImportPipeline.Result.Waiting
        assertEquals("Select your original StarCraft/Brood War installation folder, legacy installer, or disc image.", sc.missing.single().prompt)

    }

    @Test fun starcraft2TakesAnyBuild() {
        setUp()
        val sc2 = run(StarCraft2OfflineImporter(), mapOf(picked("install", Fixtures.starcraft2Install(tmp.newFolder("sc2"), build = "75689", version = "4.11.4.75689"))))
        assertTrue(sc2 is ImportPipeline.Result.Done)
    }

    @Test fun lordOfDestructionMissingIsItsOwnProblem() {
        setUp()
        val result = run(Diablo2ClassicImporter(), mapOf(picked("install", Fixtures.diablo2Install(tmp.newFolder("d2"), expansion = false)))) as ImportPipeline.Result.Failed
        assertEquals(Problem.MISSING_EXPANSION, result.error.problem)
        assertEquals(Outcome.MISSING_REQUIRED_FILE, result.record.outcome)
    }

    // 6. A cancelled import leaves no broken entry -----------------------------------------------

    @Test fun cancellingLeavesNothingBroken() {
        setUp()
        cancel = CancelToken().also { it.cancel() }
        val result = run(Diablo2ClassicImporter(), mapOf(picked("install", Fixtures.diablo2Install(tmp.newFolder("d2"))))) as ImportPipeline.Result.Failed
        assertEquals(Problem.CANCELLED, result.error.problem)
        assertNull(Library(paths).get("diablo2"))
        assertFalse(paths.staging("diablo2").exists())
        assertFalse(paths.game("diablo2").exists())
        assertEquals(Stage.NOT_INSTALLED, ImportStateRepository(paths).load("diablo2").stage)
    }

    @Test fun cancellingARepairKeepsTheInstalledGame() {
        setUp()
        val first = run(StarCraftClassicImporter(), mapOf(picked("install", Fixtures.starcraftInstall(tmp.newFolder("sc"))))) as ImportPipeline.Result.Done
        cancel = CancelToken().also { it.cancel() }
        run(StarCraftClassicImporter(), repair = true)
        assertTrue(File(paths.game("starcraft"), "StarCraft.exe").isFile)
        assertEquals(first.entry, Library(paths).get("starcraft"))
        assertEquals(Stage.READY, ImportStateRepository(paths).load("starcraft").stage)
    }

    // 7. Interrupted downloads resume (DownloadTest) ---------------------------------------------

    // 8. Reimport preserves saves -----------------------------------------------------------------

    @Test fun repairKeepsSavesAndSettings() {
        setUp()
        val engine = Fixtures.devilutionxZip(tmp.newFile("devilutionx-windows-x86_64.zip"))
        val data = Fixtures.mpq(tmp.newFile("DIABDAT.MPQ"))
        run(Diablo1DevilutionXImporter(), mapOf(picked("engine", engine), picked("data", data), "hellfire" to Supplied.Skipped("hellfire")))
        val save = File(paths.saves("diablo"), "single_0.sv").apply { writeText("hero") }
        File(paths.saves("diablo"), "diablo.ini").writeText("[Game]\nRun in Town=1\n")
        // A damaged archive, then Repair with the files again.
        File(paths.game("diablo"), "diabdat.mpq").writeBytes(ByteArray(10))
        val repaired = run(Diablo1DevilutionXImporter(), mapOf(picked("engine", engine), picked("data", data), "hellfire" to Supplied.Skipped("hellfire")), repair = true)
        assertTrue(repaired.toString(), repaired is ImportPipeline.Result.Done)
        assertEquals("hero", save.readText())
        assertEquals("[Game]\nRun in Town=1\n", File(paths.saves("diablo"), "diablo.ini").readText())
        assertTrue(Mpq.isArchive(File(paths.game("diablo"), "diabdat.mpq")))

        // StarCraft keeps its saves in the game folder: a reimport keeps them, and over the source's.
        val sc = Fixtures.starcraftInstall(tmp.newFolder("sc"))
        File(sc, "save/campaign.snx").apply { parentFile!!.mkdirs(); writeText("source") }
        run(StarCraftClassicImporter(), mapOf(picked("install", sc)))
        File(paths.game("starcraft"), "save/campaign.snx").writeText("played")
        File(paths.game("starcraft"), "characters/Hero.spc").apply { parentFile!!.mkdirs(); writeText("me") }
        run(StarCraftClassicImporter(), mapOf(picked("install", sc)), repair = true)
        assertEquals("played", File(paths.game("starcraft"), "save/campaign.snx").readText())
        assertEquals("me", File(paths.game("starcraft"), "characters/Hero.spc").readText())
    }

    @Test fun diabloIIsOldSaveFolderGoesToTheSaves() {
        setUp()
        val d2 = Fixtures.diablo2Install(tmp.newFolder("d2"))
        File(d2, "save/Hero.d2s").apply { parentFile!!.mkdirs(); writeText("hero") }
        File(paths.saves("diablo2"), "import/Hero.d2s").apply { parentFile!!.mkdirs(); writeText("newer") }
        run(Diablo2ClassicImporter(), mapOf(picked("install", d2)))
        assertEquals("newer", File(paths.saves("diablo2"), "import/Hero.d2s").readText())
        assertFalse(File(paths.game("diablo2"), "save").exists())
    }

    // 9. No licence-key prompt when no key is needed ---------------------------------------------

    @Test fun noKeyIsAskedFor() {
        setUp()
        for (importer in listOf(Diablo1DevilutionXImporter(), Diablo2ClassicImporter(), StarCraftClassicImporter(), StarCraft2OfflineImporter())) {
            val result = run(importer)
            val prompts = (result as? ImportPipeline.Result.Waiting)?.missing ?: emptyList()
            assertTrue(importer.gameId, prompts.none { it.id.contains("key", true) || it.prompt.contains("key", true) })
        }
    }

    // 10. No Battle.net process or authentication --------------------------------------------------

    @Test fun nothingReachesBattleNet() {
        setUp()
        val hosts = Offline.hosts(true)
        for (name in listOf("battle.net", "us.actual.battle.net", "uswest.battle.net", "useast.battle.net", "europe.battle.net", "asia.battle.net")) {
            assertTrue(name, hosts.contains("0.0.0.0\t$name\n"))
        }
        Fixtures.diablo2Install(paths.game("diablo2"))
        Fixtures.starcraftInstall(paths.game("starcraft"))
        Fixtures.starcraft2Install(paths.game("starcraft2"))
        for (importer in listOf(Diablo2ClassicImporter(), StarCraftClassicImporter(), StarCraft2OfflineImporter())) {
            val entry = (run(importer) as ImportPipeline.Result.Done).entry
            assertFalse(entry.executable, entry.executable.contains("Battle.net", true) || entry.executable.contains("Launcher", true))
            assertFalse(entry.arguments.contains("battle", true))
        }
    }

    // 11 and 12. The executable, runtime and control profile registered --------------------------

    @Test fun launchEntriesAreTheGamesOwnPrograms() {
        setUp()
        Fixtures.diablo2Install(paths.game("diablo2"))
        Fixtures.starcraftInstall(paths.game("starcraft"))
        Fixtures.starcraft2Install(paths.game("starcraft2"))
        val expected = mapOf(
            Diablo2ClassicImporter() to Triple("Game.exe", "diablo2", "click"),
            StarCraftClassicImporter() to Triple("StarCraft.exe", "starcraft", "click"),
            StarCraft2OfflineImporter() to Triple("StarCraft II Offline.exe", "starcraft2", "click"),
        )
        for ((importer, want) in expected) {
            val entry = (run(importer) as ImportPipeline.Result.Done).entry
            assertEquals(want.first, entry.executable)
            assertEquals(LibraryEntry.RUNTIME_WINLATOR, entry.runtime)
            assertEquals(want.second, entry.controlProfile)
            // The game's own controls (its tap does what the game's tap does).
            assertEquals(want.third, Catalog.of(entry.controlProfile).rules.first { it.trigger == Trigger.TAP }.function)
            assertEquals(entry, Library(paths).get(importer.gameId))
        }
        // Diablo: DevilutionX, its data from its folder, its saves apart (drive S:).
        val engine = Fixtures.devilutionxZip(tmp.newFile("devilutionx-windows-x86_64.zip"))
        val d1 = run(Diablo1DevilutionXImporter(), mapOf(picked("engine", engine), picked("data", Fixtures.mpq(tmp.newFile("DIABDAT.MPQ"))), "hellfire" to Supplied.Skipped("hellfire"))) as ImportPipeline.Result.Done
        assertEquals("devilutionx.exe", d1.entry.executable)
        assertEquals("--data-dir D:\\diablo --save-dir S:\\diablo --config-dir S:\\diablo", d1.entry.arguments)
        assertEquals("click", Catalog.of(d1.entry.controlProfile).rules.first { it.trigger == Trigger.TAP }.function)
        assertTrue(File(paths.saves("diablo"), "diablo.ini").readText().contains("Auto Gold Pickup=0"))
    }

    @Test fun aProgramWithAMissingLibraryIsCaught() {
        setUp()
        val d2 = Fixtures.diablo2Install(tmp.newFolder("d2"))
        File(d2, "binkw32.dll").delete()
        val result = run(Diablo2ClassicImporter(), mapOf(picked("install", d2))) as ImportPipeline.Result.Failed
        assertEquals(Problem.MISSING_RUNTIME_DEPENDENCY, result.error.problem)
    }

    // 13. Import with local files only, no network -----------------------------------------------

    @Test fun importsWorkOffline() {
        setUp()
        online = false
        val folder = tmp.newFolder("Download")
        Fixtures.devilutionxZip(File(folder, "devilutionx-windows-x86_64.zip"))
        Fixtures.mpq(File(folder, "Diablo/DIABDAT.MPQ"))
        listOf("hellfire.mpq", "hfmonk.mpq", "hfmusic.mpq", "hfvoice.mpq").forEach { Fixtures.mpq(File(folder, "Diablo/$it")) }
        roots += FileNode(folder)
        val result = run(Diablo1DevilutionXImporter())
        assertTrue(result.toString(), result is ImportPipeline.Result.Done)
        assertEquals(0, releasesCalled)
        assertEquals(Stage.READY, (result as ImportPipeline.Result.Done).record.stage)
        assertEquals("Diablo + Hellfire", result.entry.title)
    }

    // 14. StarCraft II: untested until proven ----------------------------------------------------

    @Test fun starcraft2IsNeverReadyOnFilesAlone() {
        setUp()
        val sc2 = Fixtures.starcraft2Install(tmp.newFolder("sc2"))
        File(sc2, "Accounts/123/Hots.SC2Save").apply { parentFile!!.mkdirs(); writeText("save") }
        val result = run(StarCraft2OfflineImporter(), mapOf(picked("install", sc2))) as ImportPipeline.Result.Done
        assertEquals(Stage.IMPORTED_UNTESTED, result.record.stage)
        assertEquals(Outcome.IMPORTED_LAUNCH_UNTESTED, result.record.outcome)
        assertEquals("Imported — Launch Untested", statusLabel(result.record.stage, result.record.outcome, result.record.launchTest, "starcraft2"))
        assertEquals("Started under Winlator — campaign untested", statusLabel(result.record.stage, result.record.outcome, LaunchTest.WINDOW_SHOWN, "starcraft2"))
        val untested = result.validation.checks.filter { it.name in listOf("Executable started under Winlator", "Campaign menu accessible", "Save/load") }
        assertEquals(3, untested.size)
        assertTrue(untested.none { it.passed })
        // Imported profiles kept.
        assertEquals("save", File(paths.saves("starcraft2"), "Documents/StarCraft II/Accounts/123/Hots.SC2Save").readText())
    }

    // Blizzard's legacy downloads, through a stand-in for blizzard-legacy-dl ----------------------

    @Test fun starcraftFromBlizzardsServers() {
        setUp()
        online = true
        val template = Fixtures.starcraftInstall(tmp.newFolder("template-STAR"))
        legacy = LegacyDownloader(fakeTool(mapOf("STAR" to template)), paths.legacyCache)
        val result = run(StarCraftClassicImporter())
        assertTrue(result.toString(), result is ImportPipeline.Result.Done)
        assertTrue(File(paths.game("starcraft"), "StarCraft.exe").isFile)
        assertFalse(File(paths.game("starcraft"), StarCraftClassicImporter.MARK).exists())
    }

    @Test fun diabloIIFromBlizzardsServersBaseThenExpansion() {
        setUp()
        online = true
        val base = Fixtures.diablo2Install(tmp.newFolder("template-D2DV"), expansion = false)
        val expansion = tmp.newFolder("template-D2XP").also { d -> Diablo2ClassicImporter.EXPANSION.forEach { Fixtures.mpq(File(d, it)) } }
        val log = File(tmp.root, "calls.txt")
        legacy = LegacyDownloader(fakeTool(mapOf("D2DV" to base, "D2XP" to expansion), log), paths.legacyCache)
        val result = run(Diablo2ClassicImporter())
        assertTrue(result.toString(), result is ImportPipeline.Result.Done)
        val calls = log.readLines()
        assertEquals(2, calls.size)
        assertTrue(calls[0].startsWith("install D2DV"))
        assertTrue(calls[1].startsWith("install D2XP 1.13c --no-base"))
        assertTrue(calls.none { it.contains("--cdkey") })
    }

    @Test fun aHalfInstalledDiabloIIOnThePhoneIsPassedOverForBlizzardsDownload() {
        setUp()
        online = true
        // Without Lord of Destruction's data: what would stop the import.
        roots += FileNode(Fixtures.diablo2Install(tmp.newFolder("Diablo II"), expansion = false).parentFile!!)
        assertNull(Diablo2ClassicImporter().detect(env()).found["install"])
        val base = Fixtures.diablo2Install(tmp.newFolder("template-D2DV"), expansion = false)
        val expansion = tmp.newFolder("template-D2XP").also { d -> Diablo2ClassicImporter.EXPANSION.forEach { Fixtures.mpq(File(d, it)) } }
        val log = File(tmp.root, "calls.txt")
        legacy = LegacyDownloader(fakeTool(mapOf("D2DV" to base, "D2XP" to expansion), log), paths.legacyCache)
        assertTrue(run(Diablo2ClassicImporter()) is ImportPipeline.Result.Done)
        assertEquals(2, log.readLines().size)
    }

    @Test fun diabloIIVersionsThePlayPlaysAre113And114() {
        assertTrue(Diablo2ClassicImporter.supported("1.0.13.60"))
        assertTrue(Diablo2ClassicImporter.supported("1.14.1.68"))
        assertFalse(Diablo2ClassicImporter.supported("1.0.12.0"))
        assertEquals("1.13c", Diablo2ClassicImporter.label("1.0.13.60"))
        assertEquals("1.14.1.68", Diablo2ClassicImporter.label("1.14.1.68"))
    }

    @Test fun aWholeDiabloIIOnThePhoneIsUsedAndNothingIsDownloaded() {
        setUp()
        online = true
        roots += FileNode(Fixtures.diablo2Install(tmp.newFolder("Diablo II")).parentFile!!)
        assertNotNull(Diablo2ClassicImporter().detect(env()).found["install"])
        assertTrue(Diablo2ClassicImporter().resolveSources(env(), Diablo2ClassicImporter().detect(env()), emptyMap()).isEmpty())
    }

    @Test fun aStarCraftWithoutBroodWarOnThePhoneIsPassedOverForBlizzardsDownload() {
        setUp()
        online = true
        val half = Fixtures.starcraftInstall(tmp.newFolder("StarCraft"))
        File(half, "BrooDat.mpq").delete()
        roots += FileNode(half.parentFile!!)
        assertNull(StarCraftClassicImporter().detect(env()).found["install"])
        val template = Fixtures.starcraftInstall(tmp.newFolder("template-STAR"))
        legacy = LegacyDownloader(fakeTool(mapOf("STAR" to template)), paths.legacyCache)
        assertTrue(run(StarCraftClassicImporter()) is ImportPipeline.Result.Done)
    }

    @Test fun aFailedBlizzardDownloadIsReportedAndLeavesNoStaging() {
        setUp()
        online = true
        val tool = File(tmp.root, "fail.sh").apply { writeText("#!/bin/sh\necho '10/100 pieces'\necho 'error: ConnectionTimedOut'\nexit 1\n"); setExecutable(true) }
        legacy = LegacyDownloader(tool, paths.legacyCache)
        val result = run(StarCraftClassicImporter()) as ImportPipeline.Result.Failed
        assertEquals(Problem.DOWNLOAD_FAILED, result.error.problem)
        assertTrue(result.error.detail!!.contains("ConnectionTimedOut"))
        assertFalse(paths.staging("starcraft").exists())
    }

    /** A stand-in for blizzard-legacy-dl: prints progress, copies [templates]' product into --game. */
    private fun fakeTool(templates: Map<String, File>, log: File? = null): File {
        val script = buildString {
            append("#!/bin/sh\n")
            if (log != null) append("echo \"$*\" >> '${log.path}'\n")
            append("product=\"$2\"; game=\"\"\n")
            append("while [ $# -gt 0 ]; do if [ \"$1\" = --game ]; then game=\"$2\"; fi; shift; done\n")
            append("echo '50/100 pieces'; echo '100/100 pieces'; echo 'installing 3 operations'\n")
            for ((product, dir) in templates) append("[ \"\$product\" = $product ] && cp -r '${dir.path}/.' \"\$game/\"\n")
            append("exit 0\n")
        }
        return File(tmp.root, "bldl.sh").apply { writeText(script); setExecutable(true) }
    }
}
