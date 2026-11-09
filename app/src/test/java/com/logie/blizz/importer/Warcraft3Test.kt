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

/** Warcraft III (Reign of Chaos and The Frozen Throne) from the person's files in any form, and the two sharing one install. */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class Warcraft3Test {
    @get:Rule val tmp = TemporaryFolder()
    private lateinit var paths: GamePaths
    private var innoextract: Innoextract? = null
    private var legacy: LegacyDownloader? = null
    private var online = false
    private var roots: List<SourceNode> = emptyList()

    private val roc get() = Warcraft3Importer(Warcraft3Importer.Product.ROC)
    private val tft get() = Warcraft3Importer(Warcraft3Importer.Product.TFT)

    private fun setUp() { if (!::paths.isInitialized) paths = GamePaths(tmp.newFolder("files")) }

    private var keys: LegacyDownloader.Keys? = null

    private fun env() = ImportEnv(
        paths = paths, searchRoots = { roots }, online = { online }, downloads = DownloadManager(), releases = GitHubReleases(),
        legacy = legacy, innoextract = innoextract, cancel = CancelToken(), progress = {}, keys = keys,
    )

    private fun run(importer: GameImporter, source: File? = null): ImportPipeline.Result {
        setUp()
        val supplied = if (source == null) emptyMap() else mapOf("install" to Supplied.Picked("install", FileNode(source)))
        return ImportPipeline(ImportStateRepository(paths), Library(paths)).run(importer, env(), supplied)
    }

    private fun entry(id: String) = Library(paths).get(id)

    // Fixtures: stand-ins shaped like the game's files ----------------------------------------------

    /** 1.30: one program, Data/{data,indices,config}, .build.info; it holds both games. */
    private fun casc130(dir: File, version: String = "1.30.4.11274"): File {
        Fixtures.pe(File(dir, "Warcraft III.exe"), version)
        for (d in listOf("data", "indices", "config")) File(dir, "Data/$d").mkdirs()
        File(dir, "Data/data/data.000").writeBytes(ByteArray(128))
        File(dir, "Data/indices/0000000001.idx").writeBytes(ByteArray(64))
        File(dir, "Data/config/ab").writeBytes(ByteArray(64))
        File(dir, ".build.info").writeText("Branch!STRING:0\n")
        return dir
    }

    /** 1.2x: war3.mpq (+ patch) for the base game, war3x.mpq for the expansion. */
    private fun mpq127(dir: File, expansion: Boolean = true, version: String = "1.27.0.52240"): File {
        Fixtures.pe(File(dir, "war3.exe"), version)
        Fixtures.pe(File(dir, "Warcraft III.exe"), version)
        if (expansion) Fixtures.pe(File(dir, "Frozen Throne.exe"), version)
        Fixtures.mpq(File(dir, "war3.mpq"))
        Fixtures.mpq(File(dir, "war3patch.mpq"))
        if (expansion) Fixtures.mpq(File(dir, "war3x.mpq"))
        return dir
    }

    private fun filesOf(dir: File) = dir.walkTopDown().filter { it.isFile }.associate { it.relativeTo(dir).path.replace('\\', '/') to it.readBytes() }

    private fun assertDone(result: ImportPipeline.Result): ImportPipeline.Result.Done {
        assertTrue(result.toString(), result is ImportPipeline.Result.Done)
        return result as ImportPipeline.Result.Done
    }

    // Both products, any form -----------------------------------------------------------------------

    @Test fun anInstalledFolderForReignOfChaos() {
        val done = assertDone(run(roc, casc130(tmp.newFolder("src"))))
        assertEquals("Warcraft III: Reign of Chaos 1.30.4.11274", done.validation.clientVersion)
        assertEquals(Stage.IMPORTED_UNTESTED, done.record.stage)
        assertTrue(File(paths.game("warcraft3_roc"), "Data/data/data.000").isFile)
        val e = entry("warcraft3_roc")!!
        assertEquals("Warcraft III.exe", e.executable)
        assertEquals(paths.game("warcraft3_roc").path, e.installPath)
        assertEquals(listOf("WAR3"), e.products)
        assertEquals("warcraft3", e.controlProfile)
        assertEquals("-windowmode fullscreen -nativefullscr", e.arguments)
        assertEquals(LibraryEntry.RUNTIME_WINLATOR, e.runtime)
    }

    @Test fun aZipWithItsOwnTopFolderForTheFrozenThrone() {
        setUp()
        val src = casc130(tmp.newFolder("src"))
        val zip = Fixtures.zip(tmp.newFile("wc3.zip"), filesOf(src).mapKeys { "Warcraft III 1.30 (16by9)/${it.key}" })
        val done = assertDone(run(tft, zip))
        assertEquals("Warcraft III: The Frozen Throne 1.30.4.11274", done.validation.clientVersion)
        assertEquals(listOf("WAR3", "W3XP"), entry("warcraft3_tft")!!.products)
        assertTrue(File(paths.game("warcraft3_tft"), ".build.info").isFile)
    }

    @Test fun discImageOf127AndTheExpansionProgramStartsTheFrozenThrone() {
        val src = mpq127(tmp.newFolder("src"))
        val iso = Fixtures.iso(tmp.newFile("wc3.iso"), "WAR3", filesOf(src))
        assertDone(run(tft, iso))
        assertEquals("Frozen Throne.exe", entry("warcraft3_tft")!!.executable)
        assertEquals("Warcraft III: The Frozen Throne 1.27.0.52240", entry("warcraft3_tft")!!.clientVersion)
    }

    @Test fun anInstallerAndItsDataFilesOfAnyName() {
        val folder = tmp.newFolder("repack")
        Fixtures.pe(File(folder, "Setup.exe"), "1.0.0.0")
        File(folder, "Data02.dxn").writeBytes(ByteArray(1_100_000) { 2 })
        File(folder, "Data01.dxn").writeBytes(ByteArray(1_200_000) { 1 })
        val game = casc130(tmp.newFolder("installed"))
        // A stand-in for innoextract: writes the game where it's told.
        val script = File(tmp.root, "inno.sh").apply {
            writeText("""#!/bin/sh
                |while [ "${'$'}1" != --output-dir ]; do shift; done; out="${'$'}2"
                |cp -r '${game.path}'/. "${'$'}out"/
                |""".trimMargin())
            setExecutable(true)
        }
        innoextract = Innoextract(script)
        assertDone(run(roc, folder))
        assertTrue(File(paths.game("warcraft3_roc"), "Warcraft III.exe").isFile)
    }

    @Test fun mapsAndKeysAreOptional() {
        val src = casc130(tmp.newFolder("src"))
        val done = assertDone(run(roc, src))
        assertTrue(done.validation.checks.first { it.name.startsWith("Maps") }.passed)
        assertTrue(done.validation.checks.first { it.name.startsWith("CD keys") }.detail.startsWith("none"))
        val withKeys = casc130(tmp.newFolder("src2"))
        File(withKeys, "_SERIAL_KEYS.txt").writeText("ABCD2-EFGH3-JKLM4-NPQR5-TVWX6")
        File(withKeys, "Maps/FrozenThrone/a.w3x").also { it.parentFile.mkdirs() }.writeText("map")
        val again = assertDone(ImportPipeline(ImportStateRepository(paths), Library(paths)).run(roc, env(), mapOf("install" to Supplied.Picked("install", FileNode(withKeys))), repair = true))
        assertTrue(again.validation.checks.first { it.name.startsWith("CD keys") }.detail.startsWith("found"))
        assertEquals("present", again.validation.checks.first { it.name.startsWith("Maps") }.detail)
    }

    @Test fun theLaunchIsNeverReadyOnFilesAlone() {
        val done = assertDone(run(roc, casc130(tmp.newFolder("src"))))
        assertTrue(done.validation.checks.any { it.name == "Started under Winlator" && !it.passed })
        assertEquals(Stage.IMPORTED_UNTESTED, roc.readyStage(done.validation))
    }

    // Wrong games and versions are refused ------------------------------------------------------------

    @Test fun anotherGameIsRefused() {
        val d2 = Fixtures.diablo2Install(tmp.newFolder("d2"))
        // (A folder holding only a program is taken for an installer, which needs innoextract: not here.)
        assertTrue(run(roc, d2) is ImportPipeline.Result.Failed)
        val sc2 = Fixtures.starcraft2Install(tmp.newFolder("sc2"))
        assertTrue(run(tft, sc2) is ImportPipeline.Result.Failed)
        assertFalse(paths.game("warcraft3_roc").exists())
    }

    @Test fun reforgedAndOtherVersionsAreRefusedWithTheVersionSaid() {
        val result = run(roc, casc130(tmp.newFolder("reforged"), "1.32.10.19000")) as ImportPipeline.Result.Failed
        assertEquals(Problem.UNSUPPORTED_VERSION, result.error.problem)
        assertTrue(result.error.message!!.contains("1.32.10.19000"))
        assertFalse(paths.game("warcraft3_roc").exists())
        assertTrue(Warcraft3Importer.supported("1.30.4.11274"))
        assertTrue(Warcraft3Importer.supported("1.26.0.6401"))
        assertFalse(Warcraft3Importer.supported("1.32.0.1"))
        assertFalse(Warcraft3Importer.supported("2.0.0.1"))
        assertFalse(Warcraft3Importer.supported(null))
    }

    @Test fun aProgramWithAMissingLibraryIsCaught() {
        val dir = casc130(tmp.newFolder("src"))
        Fixtures.pe(File(dir, "Warcraft III.exe"), "1.30.4.11274", imports = listOf("KERNEL32.dll", "storm.dll"))
        val result = run(roc, dir) as ImportPipeline.Result.Failed
        assertEquals(Problem.MISSING_RUNTIME_DEPENDENCY, result.error.problem)
        assertTrue(result.error.message!!.contains("storm.dll"))
    }

    @Test fun halfOf130sDataIsDamaged() {
        val dir = casc130(tmp.newFolder("src"))
        File(dir, "Data/indices/0000000001.idx").delete()
        assertEquals(Problem.CORRUPT_ARCHIVE, (run(roc, dir) as ImportPipeline.Result.Failed).error.problem)
    }

    @Test fun reignOfChaosNeedsItsData() {
        val dir = tmp.newFolder("src")
        Fixtures.pe(File(dir, "war3.exe"), "1.27.0.52240")
        Fixtures.mpq(File(dir, "war3x.mpq"))
        assertEquals(Problem.MISSING_SOURCE_DATA, (run(roc, dir) as ImportPipeline.Result.Failed).error.problem)
    }

    @Test fun theFrozenThroneNeedsItsExpansionData() {
        val result = run(tft, mpq127(tmp.newFolder("rocOnly"), expansion = false)) as ImportPipeline.Result.Failed
        assertEquals(Problem.MISSING_EXPANSION, result.error.problem)
        assertFalse(paths.staging("warcraft3_tft").exists())
        assertFalse(paths.game("warcraft3_tft").exists())
    }

    @Test fun nothingGivenAsksForTheFilesWithTheRightPrompt() {
        val result = run(roc)
        assertTrue(result.toString(), result is ImportPipeline.Result.Waiting)
        val missing = (result as ImportPipeline.Result.Waiting).missing.single()
        assertEquals("install", missing.id)
        assertTrue(missing.prompt.contains("Warcraft III"))
    }

    // One install for both ------------------------------------------------------------------------------

    @Test fun theFrozenThroneUsesReignOfChaossInstallWithoutCopying() {
        assertDone(run(roc, casc130(tmp.newFolder("src"))))
        val before = filesOf(paths.game("warcraft3_roc")).size
        // Nothing is asked for and nothing is picked: the detection finds the other product's folder.
        val detection = tft.detect(env())
        assertTrue(detection.installed)
        assertTrue(detection.notes.single().contains("Reign of Chaos"))
        val done = assertDone(run(tft))
        assertEquals(Stage.IMPORTED_UNTESTED, done.record.stage)
        assertFalse(paths.game("warcraft3_tft").exists())
        assertEquals(before, filesOf(paths.game("warcraft3_roc")).size)
        val e = entry("warcraft3_tft")!!
        assertEquals(paths.game("warcraft3_roc").path, e.installPath)
        assertEquals("Warcraft III.exe", e.executable)
        assertEquals(listOf("WAR3", "W3XP"), e.products)
        assertEquals(paths.game("warcraft3_roc").path, entry("warcraft3_roc")!!.installPath)
    }

    @Test fun reignOfChaosUsesTheFrozenThronesInstallToo() {
        assertDone(run(tft, mpq127(tmp.newFolder("full"))))
        assertDone(run(roc))
        assertFalse(paths.game("warcraft3_roc").exists())
        val e = entry("warcraft3_roc")!!
        assertEquals(paths.game("warcraft3_tft").path, e.installPath)
        // Its own program, not the expansion's.
        assertEquals("Warcraft III.exe", e.executable)
    }

    @Test fun repairingTheSharingProductChangesNothing() {
        assertDone(run(roc, casc130(tmp.newFolder("src"))))
        assertDone(run(tft))
        val before = filesOf(paths.game("warcraft3_roc"))
        setUp()
        val repaired = ImportPipeline(ImportStateRepository(paths), Library(paths)).run(tft, env(), emptyMap(), repair = true)
        assertDone(repaired)
        assertEquals(before.keys, filesOf(paths.game("warcraft3_roc")).keys)
        assertFalse(paths.game("warcraft3_tft").exists())
    }

    @Test fun aBaseOnlyInstallIsNotSharedAndTheExpansionAsksForItsFiles() {
        assertDone(run(roc, mpq127(tmp.newFolder("base"), expansion = false)))
        val waiting = run(tft)
        assertTrue(waiting.toString(), waiting is ImportPipeline.Result.Waiting)
        assertEquals(Warcraft3Importer.PROMPT_EXPANSION, (waiting as ImportPipeline.Result.Waiting).missing.single().prompt)
        // With the full game given, it keeps its own folder; Reign of Chaos' stays as it was.
        assertDone(run(tft, mpq127(tmp.newFolder("full"))))
        assertEquals(paths.game("warcraft3_tft").path, entry("warcraft3_tft")!!.installPath)
        assertEquals(paths.game("warcraft3_roc").path, entry("warcraft3_roc")!!.installPath)
        assertNull(File(paths.game("warcraft3_roc"), "war3x.mpq").takeIf { it.exists() })
    }

    @Test fun repairKeepsTheGamesOwnSaveFolder() {
        assertDone(run(roc, mpq127(tmp.newFolder("src"))))
        File(paths.game("warcraft3_roc"), "Save/Me").mkdirs()
        File(paths.game("warcraft3_roc"), "Save/Me/a.w3z").writeText("save")
        setUp()
        assertDone(ImportPipeline(ImportStateRepository(paths), Library(paths)).run(roc, env(), emptyMap(), repair = true))
        assertEquals("save", File(paths.game("warcraft3_roc"), "Save/Me/a.w3z").readText())
        GameReset.reset(paths, "warcraft3_roc", roc.keptInGame)
        assertEquals("save", File(paths.game("warcraft3_roc"), "Save/Me/a.w3z").readText())
        assertFalse(File(paths.game("warcraft3_roc"), "war3.mpq").exists())
    }

    @Test fun markersFindTheGameWhereverItLanded() {
        assertTrue(Warcraft3Importer.isGameRoot(setOf("warcraft iii.exe", "data/", ".build.info")))
        assertTrue(Warcraft3Importer.isGameRoot(setOf("war3.exe", "war3.mpq")))
        assertFalse(Warcraft3Importer.isGameRoot(setOf("warcraft iii.exe")))
        assertFalse(Warcraft3Importer.isGameRoot(setOf("game.exe", "d2data.mpq", "data/")))
        val loose = tmp.newFolder("loose")
        casc130(File(loose, "app/{app}/odd"))
        assertEquals(File(loose, "app/{app}/odd"), roc.looseGameRoot(loose))
        assertNull(roc.looseGameRoot(tmp.newFolder("empty")))
    }

    // Blizzard's servers --------------------------------------------------------------------------------

    /** A stand-in for blizzard-legacy-dl: prints progress, copies [templates]' product into --game. */
    private fun fakeTool(templates: Map<String, File>, log: File): File {
        val script = buildString {
            append("#!/bin/sh\n")
            append("echo \"$*\" >> '${log.path}'\n")
            append("product=\"$2\"; game=\"\"\n")
            append("while [ $# -gt 0 ]; do if [ \"$1\" = --game ]; then game=\"$2\"; fi; shift; done\n")
            append("echo '100/100 pieces'; echo 'installing 3 operations'\n")
            for ((product, dir) in templates) append("[ \"\$product\" = $product ] && cp -r '${dir.path}/.' \"\$game/\"\n")
            append("exit 0\n")
        }
        return File(tmp.root, "bldl.sh").apply { writeText(script); setExecutable(true) }
    }

    @Test fun theBaseGameThenTheExpansionFromBlizzardWithNoKey() {
        setUp()
        online = true
        val base = mpq127(tmp.newFolder("template-WAR3"), expansion = false)
        val exp = tmp.newFolder("template-W3XP").also { d -> Fixtures.mpq(File(d, "war3x.mpq")); Fixtures.pe(File(d, "Frozen Throne.exe"), "1.27.0.52240") }
        val log = File(tmp.root, "calls.txt")
        legacy = LegacyDownloader(fakeTool(mapOf("WAR3" to base, "W3XP" to exp), log), paths.legacyCache)
        assertDone(run(tft))
        val calls = log.readLines()
        assertEquals(2, calls.size)
        assertTrue(calls[0].startsWith("install WAR3"))
        assertTrue(calls[1].startsWith("install W3XP --no-base"))
        // The game stops at start without a key in its archives: each product's slot gets the placeholder, never a real key.
        assertTrue(calls[0].contains("--cdkey ${LegacyDownloader.PLACEHOLDER_KEY_WAR3}") && !calls[0].contains("--cdkey-expansion"))
        assertTrue(calls[1].contains("--cdkey-expansion ${LegacyDownloader.PLACEHOLDER_KEY_W3XP}"))
        assertFalse(File(paths.game("warcraft3_tft"), Warcraft3Importer.MARK).exists())
    }

    @Test fun reignOfChaosFromBlizzardBringsBothCampaignsAndBothTiles() {
        setUp()
        online = true
        val base = mpq127(tmp.newFolder("template-WAR3"), expansion = false)
        val exp = tmp.newFolder("template-W3XP").also { d -> Fixtures.mpq(File(d, "war3x.mpq")); Fixtures.pe(File(d, "Frozen Throne.exe"), "1.27.0.52240") }
        val log = File(tmp.root, "calls.txt")
        legacy = LegacyDownloader(fakeTool(mapOf("WAR3" to base, "W3XP" to exp), log), paths.legacyCache)
        val waitingLabel = roc.resolveSources(env(), roc.detect(env()), emptyMap()).single()
        assertTrue(waitingLabel.label.contains("The Frozen Throne"))
        assertDone(run(roc))
        assertEquals(2, log.readLines().size)
        assertNotNull(entry("warcraft3_roc"))
        // The Frozen Throne is in the library without a second tap, from the same folder, with its own program.
        val other = entry("warcraft3_tft")!!
        assertEquals(paths.game("warcraft3_roc").path, other.installPath)
        assertEquals("Frozen Throne.exe", other.executable)
        assertFalse(paths.game("warcraft3_tft").exists())
    }

    @Test fun aHalfCopiedFolderOnThePhoneIsIgnoredAndBlizzardsDownloadRuns() {
        setUp()
        online = true
        // 1.30's Data folder without config: what stopped the import before.
        val half = casc130(tmp.newFolder("Warcraft III"))
        File(half, "Data/config").deleteRecursively()
        roots = listOf(FileNode(half.parentFile!!))
        assertNull(roc.detect(env()).found["install"])
        val base = mpq127(tmp.newFolder("template-WAR3"), expansion = false)
        val exp = tmp.newFolder("template-W3XP").also { d -> Fixtures.mpq(File(d, "war3x.mpq")); Fixtures.pe(File(d, "Frozen Throne.exe"), "1.27.0.52240") }
        val log = File(tmp.root, "calls.txt")
        legacy = LegacyDownloader(fakeTool(mapOf("WAR3" to base, "W3XP" to exp), log), paths.legacyCache)
        assertDone(run(roc))
        assertEquals(2, log.readLines().size)
    }

    @Test fun aHalfFolderPickedEarlierDoesNotBlockTheDownloadOnRetry() {
        setUp()
        online = true
        val half = casc130(tmp.newFolder("picked"))
        File(half, "Data/config").deleteRecursively()
        val base = mpq127(tmp.newFolder("template-WAR3"), expansion = false)
        val exp = tmp.newFolder("template-W3XP").also { d -> Fixtures.mpq(File(d, "war3x.mpq")); Fixtures.pe(File(d, "Frozen Throne.exe"), "1.27.0.52240") }
        val log = File(tmp.root, "calls.txt")
        legacy = LegacyDownloader(fakeTool(mapOf("WAR3" to base, "W3XP" to exp), log), paths.legacyCache)
        // The first import's picked folder is still in the record when Retry runs.
        assertDone(run(roc, half))
        assertEquals(2, log.readLines().size)
    }

    @Test fun anArchiveThatDoesNotPlayFallsBackToBlizzardsDownload() {
        setUp()
        online = true
        // A zip of a half-copied 1.30 (no Data/config): it can't be told from a good one until it is opened.
        val half = casc130(tmp.newFolder("src"))
        File(half, "Data/config").deleteRecursively()
        val zip = Fixtures.zip(tmp.newFile("wc3.zip"), filesOf(half))
        val base = mpq127(tmp.newFolder("template-WAR3"), expansion = false)
        val exp = tmp.newFolder("template-W3XP").also { d -> Fixtures.mpq(File(d, "war3x.mpq")); Fixtures.pe(File(d, "Frozen Throne.exe"), "1.27.0.52240") }
        val log = File(tmp.root, "calls.txt")
        legacy = LegacyDownloader(fakeTool(mapOf("WAR3" to base, "W3XP" to exp), log), paths.legacyCache)
        val done = assertDone(run(roc, zip))
        assertEquals(2, log.readLines().size)
        assertTrue(done.validation.clientVersion!!.contains("1.27"))
        assertNotNull(entry("warcraft3_tft"))
    }

    @Test fun anArchiveThatDoesNotPlayStillFailsWhenOffline() {
        setUp()
        online = false
        val half = casc130(tmp.newFolder("src"))
        File(half, "Data/config").deleteRecursively()
        val zip = Fixtures.zip(tmp.newFile("wc3.zip"), filesOf(half))
        assertTrue(run(roc, zip) is ImportPipeline.Result.Failed)
    }

    @Test fun thePersonsOwnKeysAreWrittenInPlaceOfTheStandIns() {
        setUp()
        online = true
        val base = mpq127(tmp.newFolder("template-WAR3"), expansion = false)
        val exp = tmp.newFolder("template-W3XP").also { d -> Fixtures.mpq(File(d, "war3x.mpq")); Fixtures.pe(File(d, "Frozen Throne.exe"), "1.27.0.52240") }
        val log = File(tmp.root, "calls.txt")
        legacy = LegacyDownloader(fakeTool(mapOf("WAR3" to base, "W3XP" to exp), log), paths.legacyCache)
        keys = LegacyDownloader.Keys(classic = "MYROCKEY", expansion = "MYTFTKEY", owner = null)
        assertDone(run(roc))
        val calls = log.readLines()
        assertTrue(calls[0].contains("--cdkey MYROCKEY") && !calls[0].contains(LegacyDownloader.PLACEHOLDER_KEY_WAR3))
        assertTrue(calls[1].contains("--cdkey-expansion MYTFTKEY"))
    }

    @Test fun withOnlyOneKeyGivenTheOtherIsTheStandIn() {
        setUp()
        online = true
        val base = mpq127(tmp.newFolder("template-WAR3"), expansion = false)
        val exp = tmp.newFolder("template-W3XP").also { d -> Fixtures.mpq(File(d, "war3x.mpq")); Fixtures.pe(File(d, "Frozen Throne.exe"), "1.27.0.52240") }
        val log = File(tmp.root, "calls.txt")
        legacy = LegacyDownloader(fakeTool(mapOf("WAR3" to base, "W3XP" to exp), log), paths.legacyCache)
        keys = LegacyDownloader.Keys(classic = "MYROCKEY", expansion = null, owner = null)
        assertDone(run(roc))
        val calls = log.readLines()
        assertTrue(calls[0].contains("--cdkey MYROCKEY"))
        assertTrue(calls[1].contains("--cdkey-expansion ${LegacyDownloader.PLACEHOLDER_KEY_W3XP}"))
    }

    @Test fun anInstallCarriesItsRecipeAndAnOlderOneIsStale() {
        val done = assertDone(run(roc, casc130(tmp.newFolder("src"))))
        assertEquals(roc.recipe, done.record.recipe)
        assertEquals(2, done.record.recipe)
        assertFalse(Recipes.stale(done.record, roc.recipe))
        assertFalse(Recipes.stale(ImportStateRepository(paths).load("warcraft3_roc"), roc.recipe))
        // Records from before recipes existed carry 0, counted as the first recipe: only a real change installs a game again.
        assertTrue(Recipes.stale(ImportRecord("warcraft3_roc", stage = Stage.IMPORTED_UNTESTED), 2))
        assertFalse(Recipes.stale(ImportRecord("diablo", stage = Stage.READY), 1))
    }

    @Test fun aWholeFolderOnThePhoneIsFoundAndNothingIsDownloaded() {
        setUp()
        online = true
        val whole = casc130(tmp.newFolder("Warcraft III"))
        roots = listOf(FileNode(whole.parentFile!!))
        assertNotNull(roc.detect(env()).found["install"])
        assertTrue(roc.resolveSources(env(), roc.detect(env()), emptyMap()).isEmpty())
    }

    @Test fun aPickedFolderIsUsedInsteadOfDownloading() {
        setUp()
        online = true
        val log = File(tmp.root, "calls.txt")
        legacy = LegacyDownloader(fakeTool(emptyMap(), log), paths.legacyCache)
        assertDone(run(roc, casc130(tmp.newFolder("src"))))
        assertFalse(log.exists())
    }
}
