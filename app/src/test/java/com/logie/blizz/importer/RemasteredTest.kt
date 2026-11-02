package com.logie.blizz.importer

import com.logie.blizz.Games
import com.logie.blizz.controls.Catalog
import com.logie.blizz.ui.Variants
import com.logie.blizz.ui.statusLabel
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.File

/** StarCraft: Remastered as a second installation beside the classic game. */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class RemasteredTest {
    @get:Rule val tmp = TemporaryFolder()
    private val paths by lazy { GamePaths(tmp.newFolder("files")) }

    private fun env() = ImportEnv(
        paths = paths, searchRoots = { emptyList() }, online = { false }, downloads = DownloadManager(), releases = GitHubReleases(),
        legacy = null, innoextract = null, cancel = CancelToken(), progress = {},
    )

    private fun run(importer: GameImporter, source: File? = null) =
        ImportPipeline(ImportStateRepository(paths), Library(paths)).run(importer, env(), source?.let { mapOf("install" to Supplied.Picked("install", FileNode(it))) } ?: emptyMap())

    private fun files(build: String = "1.23.10.12409"): Map<String, ByteArray> {
        val dir = tmp.newFolder("src-${System.nanoTime()}")
        Fixtures.starcraftRemastered(dir, build)
        return dir.walkTopDown().filter { it.isFile }.associate { it.relativeTo(dir).path.replace('\\', '/') to it.readBytes() }
    }

    @Test fun fromADiscImage() {
        val iso = Fixtures.iso(tmp.newFile("StarCraft Remastered.iso"), "SCR", files())
        val result = run(StarCraftRemasteredImporter(), iso)
        assertTrue(result.toString(), result is ImportPipeline.Result.Done)
        result as ImportPipeline.Result.Done
        assertEquals(Stage.IMPORTED_UNTESTED, result.record.stage)
        assertEquals("StarCraft: Remastered 1.23.10.12409", result.entry.clientVersion)
        assertEquals("StarCraft.exe", result.entry.executable)
        assertEquals("starcraft_remastered", result.entry.controlProfile)
        assertEquals("Imported — Launch Untested", statusLabel(result.record.stage, result.record.outcome, result.record.launchTest, "starcraft_remastered"))
        assertTrue(File(paths.game("starcraft_remastered"), "Data/data/data.000").isFile)
    }

    @Test fun besideTheClassicGameWhichIsNeverTouched() {
        val classic = Fixtures.starcraftInstall(tmp.newFolder("classic"))
        run(StarCraftClassicImporter(), classic)
        val before = Library(paths).get("starcraft")
        val classicFile = File(paths.game("starcraft"), "StarDat.mpq")
        val stamp = classicFile.lastModified()
        val result = run(StarCraftRemasteredImporter(), Fixtures.zip(tmp.newFile("scr.zip"), files()))
        assertTrue(result.toString(), result is ImportPipeline.Result.Done)
        assertEquals(before, Library(paths).get("starcraft"))
        assertEquals(stamp, classicFile.lastModified())
        assertNotNull(Library(paths).get("starcraft_remastered"))
        assertFalse(File(paths.game("starcraft_remastered"), "StarDat.mpq").exists())
        // Each has its own saves folder and the same controls as the classic game's catalog starts from.
        assertTrue(paths.saves("starcraft") != paths.saves("starcraft_remastered"))
        assertEquals(Catalog.STARCRAFT, Catalog.of("starcraft_remastered"))
    }

    @Test fun anotherGameIsRefused() {
        val result = run(StarCraftRemasteredImporter(), Fixtures.zip(tmp.newFile("scr.zip"), files("1.16.1.1"))) as ImportPipeline.Result.Failed
        assertEquals(Problem.UNSUPPORTED_VERSION, result.error.problem)
        assertEquals(Outcome.UNSUPPORTED_CLIENT_VERSION, result.record.outcome)
        assertFalse(paths.game("starcraft_remastered").exists())
    }

    @Test fun asksForTheFilesWhenThereAreNone() {
        val result = run(StarCraftRemasteredImporter()) as ImportPipeline.Result.Waiting
        assertTrue(result.missing.single().prompt.startsWith("Select your StarCraft: Remastered installation"))
    }

    @Test fun thePageSwitchesBetweenTheTwoInstallations() {
        val starcraft = Games.all.first { it.id == "starcraft" }
        assertEquals(listOf("starcraft_remastered"), starcraft.variants.map { it.id })
        assertEquals("starcraft", Variants.effective(starcraft, emptyMap()).id)
        assertEquals("starcraft_remastered", Variants.effective(starcraft, mapOf("starcraft" to "starcraft_remastered")).id)
        assertEquals("StarCraft: Remastered", Games.find("starcraft_remastered")?.fullTitle)
        // A game without a second installation is always itself.
        val diablo = Games.all.first { it.id == "diablo" }
        assertEquals("diablo", Variants.effective(diablo, mapOf("diablo" to "starcraft_remastered")).id)
    }

    @Test fun the123FolderWithItsProgramInX86IsAGameRoot() {
        val names = Packages.names(listOf("Data/", "locales/", "Maps/", "x86/", "x86_64/", "StarCraft Launcher.exe", "Launcher.db").map {
            object : SourceNode {
                override val name = it.trimEnd('/')
                override val isDirectory = it.endsWith("/")
                override val size = 1L
                override val display = it
                override fun children() = emptyList<SourceNode>()
                override fun open() = java.io.ByteArrayInputStream(ByteArray(0))
                override fun localFile(): java.io.File? = null
            }
        })
        assertTrue(StarCraftRemasteredImporter.isGameRoot(names))
        assertTrue(!StarCraftRemasteredImporter.isGameRoot(setOf("data/", "stardat.mpq", "starcraft.exe")))
    }

    @Test fun the123LayoutWithDataFilesOnlyDeepDownAndTheProgramInX86Validates() {
        val dir = java.io.File(System.getProperty("java.io.tmpdir"), "sc-r-${System.nanoTime()}")
        Fixtures.pe(java.io.File(dir, "x86/StarCraft.exe"), "1.23.10.13515")
        java.io.File(dir, "Data/config/44").mkdirs()
        java.io.File(dir, "Data/data").mkdirs()
        java.io.File(dir, "Data/data/data.000").writeText("x")
        java.io.File(dir, "Data/config/44/a").writeText("x")
        val v = StarCraftRemasteredImporter().validateDir(dir)
        assertTrue(v.checks.joinToString { "${it.name}:${it.passed}" }, v.checks.take(3).all { it.passed })
        dir.deleteRecursively()
    }
}
