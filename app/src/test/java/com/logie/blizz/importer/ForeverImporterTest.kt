package com.logie.blizz.importer

import com.logie.blizz.Games
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

/** World of Warcraft: Forever's Add client step: the client's folder or an archive of it. */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class ForeverImporterTest {
    @get:Rule val tmp = TemporaryFolder()
    private val paths by lazy { GamePaths(tmp.newFolder("files")) }

    private fun env() = ImportEnv(
        paths = paths, searchRoots = { emptyList() }, online = { false }, downloads = DownloadManager(), releases = GitHubReleases(),
        legacy = null, innoextract = null, cancel = CancelToken(), progress = {},
    )

    private fun run(source: File) =
        ImportPipeline(ImportStateRepository(paths), Library(paths)).run(ForeverImporter(), env(), mapOf("client" to Supplied.Picked("client", FileNode(source))))

    private fun client(build: String = "1.60.1.70707", withData: Boolean = true): File {
        val dir = tmp.newFolder("client-${System.nanoTime()}")
        Fixtures.pe(File(dir, "Wow.exe"), "1.60.1.0")
        File(dir, ".build.info").writeText("Branch!STRING:0|Active!DEC:1|Version!STRING:0\nus|1|$build\n")
        if (withData) {
            File(dir, "_forever_/Data").mkdirs()
            File(dir, "_forever_/Data/common.MPQ").writeBytes(ByteArray(64))
        }
        return dir
    }

    private fun entries(dir: File) = dir.walkTopDown().filter { it.isFile }.associate { it.relativeTo(dir).path.replace('\\', '/') to it.readBytes() }

    @Test fun theGameIsOnTheWowTile() {
        assertEquals("World of Warcraft", Games.find("wow_forever")?.title)
        assertNotNull(Games.find("wow")?.variants?.firstOrNull { it.id == "wow_forever" })
        assertTrue(GameImportManager.importable("wow_forever"))
    }

    @Test fun withoutAClientItAsksForOne() {
        val missing = ForeverImporter().getMissingInputs(env(), Detection(false, emptyMap()), emptyMap())
        assertEquals(listOf("client"), missing.map { it.id })
        assertEquals(PickKind.FILE_OR_FOLDER, missing.single().kind)
    }

    @Test fun fromAFolder() {
        val result = run(client())
        assertTrue(result.toString(), result is ImportPipeline.Result.Done)
        result as ImportPipeline.Result.Done
        assertEquals(Stage.IMPORTED_UNTESTED, result.record.stage)
        assertEquals("Forever client 70707", result.entry.clientVersion)
        assertEquals("Wow.exe", result.entry.executable)
        assertTrue(File(paths.game("wow_forever"), "_forever_/Data/common.MPQ").isFile)
    }

    @Test fun fromAZipOfIt() {
        val result = run(Fixtures.zip(tmp.newFile("client.zip"), entries(client()).mapKeys { "ForeverNXT-Client/${it.key}" }))
        assertTrue(result.toString(), result is ImportPipeline.Result.Done)
        assertTrue(File(paths.game("wow_forever"), "Wow.exe").isFile)
    }

    @Test fun anUnknownBuildIsShownAsItIs() {
        val check = ForeverImporter().validateDir(client("1.60.1.70938"))
        assertTrue(check.filesOk)
        assertTrue(check.checks.first { it.name == "Client build" }.detail.startsWith("70938"))
    }

    @Test fun aFolderWithoutTheDataIsRefused() {
        val check = ForeverImporter().validateDir(client(withData = false))
        assertFalse(check.filesOk)
        assertEquals(Problem.MISSING_SOURCE_DATA, check.problem)
    }

    @Test fun theBuildIsReadFromTheVersion() {
        assertEquals(70707, ForeverImporter.buildOf("1.60.1.70707"))
        assertNull(ForeverImporter.buildOf("1.0.0"))
        assertNull(ForeverImporter.buildOf(null))
    }

    @Test fun aRarIsRecognisedAndAnEmptyOneIsRefusedWithAMessage() {
        // A RAR signature with nothing valid after it: read as a RAR, refused as damaged, not as an unknown file.
        val bad = tmp.newFile("client.rar").also { it.writeBytes(byteArrayOf('R'.code.toByte(), 'a'.code.toByte(), 'r'.code.toByte(), '!'.code.toByte(), 0x1A, 0x07, 0x00) + ByteArray(40)) }
        assertEquals(Format.RAR, Format.of(FileNode(bad)))
        val result = run(bad)
        assertTrue(result.toString(), result is ImportPipeline.Result.Failed)
    }
}
