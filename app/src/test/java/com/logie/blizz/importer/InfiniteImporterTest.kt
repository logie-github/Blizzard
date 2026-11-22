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

    /** The real client's `.build.info` (the archive's own, 22 November 2026), with the build replaced when asked. */
    private fun buildInfo(build: String) = "Branch!STRING:0|Active!DEC:1|Build Key!HEX:16|CDN Key!HEX:16|Install Key!HEX:16|IM Size!DEC:4|CDN Path!STRING:0|CDN Hosts!STRING:0|CDN Servers!STRING:0|Tags!STRING:0|Armadillo!STRING:0|Last Activated!STRING:0|Version!STRING:0|KeyRing!HEX:16|Product!STRING:0\n" +
        "us|1|7feb61f3c994bcb168526b8db521514a|2a6e419be5b7d7d896f7bc40395256dd|||tpr/wow|level3.blizzard.com us.cdn.blizzard.com|http://level3.blizzard.com/?maxhosts=8 http://us.cdn.blizzard.com/?maxhosts=4&fallback=1|Windows x86_64 US? acct-AUS? geoip-AU? enUS speech?:Windows x86_64 US? acct-AUS? geoip-AU? enUS text?|||$build||wowf\n"

    /** The client as its archive holds it: a `World of Warcraft` folder with `.build.info`, `.battle.net/` and `Data/` (CASC archives). */
    private fun clientFiles(build: String = "1.60.1.70707", withData: Boolean = true, withProgram: Boolean = true): Map<String, ByteArray> {
        val dir = tmp.newFolder("client-${System.nanoTime()}")
        File(dir, ".build.info").writeText(buildInfo(build))
        File(dir, ".battle.net/bts").mkdirs()
        File(dir, ".battle.net/bts/0000000001.idx").writeBytes(ByteArray(16))
        if (withProgram) Fixtures.pe(File(dir, "Wow.exe"), "1.60.1.0")
        if (withData) {
            File(dir, "Data/data").mkdirs()
            File(dir, "Data/data/data.000").writeBytes(ByteArray(64))
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
        Fixtures.zip(tmp.newFile(name), files.mapKeys { "World of Warcraft/${it.key}" })

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
        assertTrue(File(paths.game("wow_infinite"), "client/Data/data/data.000").isFile)
        assertTrue(File(paths.game("wow_infinite"), "client/.build.info").isFile)
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

    @Test fun theRealBuildInfoGivesItsBuild() {
        assertEquals(70707, InfiniteImporter.buildOf(buildInfo("1.60.1.70707")))
    }

    @Test fun aClientWithoutItsProgramIsStillTakenAndSaidSo() {
        val dir = tmp.newFolder("noexe")
        clientFiles(withProgram = false).forEach { (p, b) -> File(dir, "client/$p").also { it.parentFile.mkdirs() }.writeBytes(b) }
        serverFiles().forEach { (p, b) -> File(dir, "server/$p").also { it.parentFile.mkdirs() }.writeBytes(b) }
        val check = InfiniteImporter().validateDir(dir)
        assertTrue(check.filesOk)
        assertEquals("not found", check.checks.first { it.name.startsWith("Game program") }.detail)
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
