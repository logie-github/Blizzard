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

/** World of Warcraft: Infinite: the client and the server package, each an archive the player picks by hand. */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class InfiniteImporterTest {
    @get:Rule val tmp = TemporaryFolder()
    private val paths by lazy { GamePaths(tmp.newFolder("files")) }

    private fun env(roots: List<SourceNode> = emptyList()) = ImportEnv(
        paths = paths, searchRoots = { roots }, online = { false }, downloads = DownloadManager(), releases = GitHubReleases(),
        legacy = null, innoextract = null, cancel = CancelToken(), progress = {},
    )

    private fun run(client: File? = null, server: File? = null): ImportPipeline.Result {
        val supplied = LinkedHashMap<String, Supplied>()
        client?.let { supplied["client"] = Supplied.Picked("client", FileNode(it)) }
        server?.let { supplied["server"] = Supplied.Picked("server", FileNode(it)) }
        return ImportPipeline(ImportStateRepository(paths), Library(paths)).run(InfiniteImporter(), env(), supplied)
    }

    private fun clientFiles(build: String = "1.60.1.70707", withData: Boolean = true): Map<String, ByteArray> {
        val dir = tmp.newFolder("client-${System.nanoTime()}")
        Fixtures.pe(File(dir, "Wow.exe"), "1.60.1.0")
        File(dir, ".build.info").writeText("Branch!STRING:0|Active!DEC:1|Version!STRING:0\nus|1|$build\n")
        if (withData) {
            File(dir, "_forever_/Data").mkdirs()
            File(dir, "_forever_/Data/common.MPQ").writeBytes(ByteArray(64))
        }
        return entries(dir)
    }

    private fun serverFiles(withMysql: Boolean = true): Map<String, ByteArray> {
        val dir = tmp.newFolder("server-${System.nanoTime()}")
        File(dir, "START_SERVER.cmd").writeText("@echo off")
        File(dir, "releases/20261116").mkdirs()
        File(dir, "releases/20261116/current.txt").writeText("x")
        if (withMysql) { File(dir, "mysql/bin").mkdirs(); File(dir, "mysql/bin/mysqld.exe").writeBytes(ByteArray(32)) }
        else File(dir, "mysql").mkdirs()
        return entries(dir)
    }

    private fun entries(dir: File) = dir.walkTopDown().filter { it.isFile }.associate { it.relativeTo(dir).path.replace('\\', '/') to it.readBytes() }

    private fun clientZip(name: String = "client.zip", files: Map<String, ByteArray> = clientFiles()) =
        Fixtures.zip(tmp.newFile(name), files.mapKeys { "ForeverNXT-Client/${it.key}" })

    private fun serverZip(name: String = "server.zip", files: Map<String, ByteArray> = serverFiles()) =
        Fixtures.zip(tmp.newFile(name), files.mapKeys { "ForeverNXT-Server/${it.key}" })

    @Test fun theGameIsTheInfiniteVersionOnTheWowTile() {
        assertEquals("World of Warcraft", Games.find("wow_infinite")?.title)
        assertEquals("Infinite", Games.find("wow_infinite")?.subtitle)
        assertNotNull(Games.find("wow")?.variants?.firstOrNull { it.id == "wow_infinite" })
        assertTrue(GameImportManager.importable("wow_infinite"))
    }

    @Test fun itAsksForTheClientFileAndOffersTheServerFromMega() {
        val importer = InfiniteImporter()
        val missing = importer.getMissingInputs(env(), Detection(false, emptyMap()), emptyMap())
        assertEquals(listOf("client"), missing.map { it.id })
        assertTrue(missing.all { it.kind == PickKind.FILE && !it.optional })
        val sources = importer.resolveSources(env(), Detection(false, emptyMap()), emptyMap())
        assertEquals(listOf("server"), sources.map { it.id })
        assertEquals(InfiniteImporter.SERVER_SIZE, sources.single().size)
    }

    @Test fun aServerFileThePlayerPickedIsNotDownloaded() {
        val picked = mapOf("server" to Supplied.Picked("server", FileNode(serverZip())))
        assertTrue(InfiniteImporter().resolveSources(env(), Detection(false, emptyMap()), picked).isEmpty())
    }

    @Test fun nothingIsFoundByItself() {
        // A client zip lying in a searched folder is not taken: the player picks it.
        val dir = tmp.newFolder("downloads")
        Fixtures.zip(File(dir, "ForeverNXT-Client.zip"), clientFiles())
        val detection = InfiniteImporter().detect(env(listOf(FileNode(dir))))
        assertTrue(detection.found.isEmpty())
        assertFalse(detection.installed)
    }

    @Test fun bothArchivesInstallTheGame() {
        val result = run(clientZip(), serverZip())
        assertTrue(result.toString(), result is ImportPipeline.Result.Done)
        result as ImportPipeline.Result.Done
        assertEquals(Stage.IMPORTED_UNTESTED, result.record.stage)
        assertEquals("Infinite client 70707", result.entry.clientVersion)
        assertEquals("client/Wow.exe", result.entry.executable)
        assertTrue(File(paths.game("wow_infinite"), "client/_forever_/Data/common.MPQ").isFile)
        assertTrue(File(paths.game("wow_infinite"), "server/START_SERVER.cmd").isFile)
        assertTrue(File(paths.game("wow_infinite"), "server/mysql/bin/mysqld.exe").isFile)
    }

    @Test fun aFolderIsRefusedAndTheFileIsAsked() {
        val folder = tmp.newFolder("picked-folder")
        val result = run(client = folder, server = serverZip())
        assertTrue(result.toString(), result is ImportPipeline.Result.Failed)
        assertTrue((result as ImportPipeline.Result.Failed).error.message!!.contains("file itself"))
    }

    @Test fun theServerAloneKeepsAskingForTheClient() {
        val first = run(server = serverZip())
        // Without the client the import cannot finish; the pipeline waits for it.
        assertFalse(first.toString(), first is ImportPipeline.Result.Done)
    }

    @Test fun aClientWithoutItsDataIsRefused() {
        val result = run(clientZip("nodata.zip", clientFiles(withData = false)), serverZip())
        assertFalse(result.toString(), result is ImportPipeline.Result.Done)
    }

    @Test fun anUnknownBuildIsShownAsItIs() {
        val dir = tmp.newFolder("game")
        clientFiles("1.60.1.70938").forEach { (p, b) -> File(dir, "client/$p").also { it.parentFile.mkdirs() }.writeBytes(b) }
        serverFiles().forEach { (p, b) -> File(dir, "server/$p").also { it.parentFile.mkdirs() }.writeBytes(b) }
        val check = InfiniteImporter().validateDir(dir)
        assertTrue(check.filesOk)
        assertTrue(check.checks.first { it.name == "Client build" }.detail.startsWith("70938"))
    }

    @Test fun theBuildIsReadFromTheVersion() {
        assertEquals(70707, InfiniteImporter.buildOf("1.60.1.70707"))
        assertNull(InfiniteImporter.buildOf("1.0.0"))
        assertNull(InfiniteImporter.buildOf(null))
    }

    @Test fun aDamagedRarIsSaidToBeOne() {
        val bad = tmp.newFile("client.rar").also { it.writeBytes(byteArrayOf('R'.code.toByte(), 'a'.code.toByte(), 'r'.code.toByte(), '!'.code.toByte(), 0x1A, 0x07, 0x00) + ByteArray(40)) }
        assertEquals(Format.RAR, Format.of(FileNode(bad)))
        val result = run(bad, serverZip())
        assertTrue(result.toString(), result is ImportPipeline.Result.Failed)
    }
}
