package com.logie.blizz.importer

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.File

/** The World of Warcraft app's export, read and copied over with every file checked. */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class WowImporterTest {
    @get:Rule val tmp = TemporaryFolder()
    private lateinit var paths: GamePaths

    private fun env() = ImportEnv(
        paths = paths, searchRoots = { emptyList() }, online = { false }, downloads = DownloadManager(), releases = GitHubReleases(),
        legacy = null, innoextract = null, cancel = CancelToken(), progress = {},
    )

    /** An export as the WoW app writes it: files, checksums, prefs, and export.json last. */
    private fun export(dir: File = tmp.newFolder("WoW-export"), version: String = "1.2.3", format: Int = 1, app: String = WowExport.APP): File {
        val data = mapOf(
            "client/Data/common.MPQ" to ByteArray(5000) { (it % 251).toByte() },
            "mysql/acore_characters/characters.ibd" to ByteArray(3000) { (it % 13).toByte() },
            "addons/Questie/Questie.lua" to "print('hi')".toByteArray(),
            "turtle/WTF/Config.wtf" to "SET realmName \"Tortoise\"".toByteArray(),
        )
        val entries = data.map { (path, bytes) ->
            File(dir, "files/$path").also { it.parentFile.mkdirs() }.writeBytes(bytes)
            WowExport.Entry(java.security.MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }, bytes.size.toLong(), path)
        }
        File(dir, "prefs").mkdirs()
        File(dir, "prefs/environments.json").writeText("""{"selected":{"type":"string","value":"wrath"}}""")
        File(dir, WowExport.CHECKSUMS).writeText(WowExport.checksumsText(entries))
        File(dir, WowExport.MANIFEST).writeText(
            WowExport.manifestJson(
                WowExport.Manifest(format, app, version, "2026-11-03T00:00:00Z", "/data/data/com.logie.warcraft/files", entries.size.toLong(), entries.sumOf { it.size },
                    listOf("client", "mysql", "addons", "turtle"), listOf("rootfs", "run"), listOf("environments")),
            ),
        )
        return dir
    }

    private fun run(source: File): ImportPipeline.Result {
        paths = if (::paths.isInitialized) paths else GamePaths(tmp.newFolder())
        return ImportPipeline(ImportStateRepository(paths), Library(paths)).run(WowImporter(), env(), mapOf("install" to Supplied.Picked("install", FileNode(source))))
    }

    @Test fun anExportIsCopiedWithEveryFileCheckedAndKeptWhole() {
        val result = run(export())
        assertTrue(result.toString(), result is ImportPipeline.Result.Done)
        val game = paths.game("wow")
        assertEquals("print('hi')", File(game, "files/addons/Questie/Questie.lua").readText())
        assertEquals(3000, File(game, "files/mysql/acore_characters/characters.ibd").length())
        assertTrue(File(game, ".export/export.json").isFile)
        assertTrue(File(game, ".export/prefs/environments.json").isFile)
        assertEquals(LibraryEntry.RUNTIME_EXTERNAL, (result as ImportPipeline.Result.Done).entry.runtime)
        assertTrue(result.validation.clientVersion!!.contains("1.2.3"))
    }

    @Test fun theFolderThatHoldsTheExportWorksToo() {
        val parent = tmp.newFolder("Roms")
        export(File(parent, "WoW-export").also { it.mkdirs() })
        assertTrue(run(parent) is ImportPipeline.Result.Done)
    }

    @Test fun aFileThatDoesntMatchIsRefusedAndTheOriginalCopyStays() {
        val dir = export()
        File(dir, "files/mysql/acore_characters/characters.ibd").writeBytes(ByteArray(3000) { 9 })
        val result = run(dir)
        assertTrue(result.toString(), result is ImportPipeline.Result.Failed)
        assertEquals(Problem.CORRUPT_ARCHIVE, (result as ImportPipeline.Result.Failed).error.problem)
        assertTrue(result.error.message!!.contains("characters.ibd"))
        assertTrue(!paths.game("wow").exists())
        // What was copied and checked is kept for the next try, with its journal.
        assertTrue(File(paths.staging, "wow-work/.journal").isFile)
    }

    @Test fun anInterruptedImportCarriesOnAndFinishes() {
        val dir = export()
        val good = File(dir, "files/mysql/acore_characters/characters.ibd").readBytes()
        File(dir, "files/mysql/acore_characters/characters.ibd").writeBytes(ByteArray(3000) { 9 })
        assertTrue(run(dir) is ImportPipeline.Result.Failed)
        File(dir, "files/mysql/acore_characters/characters.ibd").writeBytes(good)
        val result = run(dir)
        assertTrue(result.toString(), result is ImportPipeline.Result.Done)
        assertTrue(!File(paths.staging, "wow-work").exists())
    }

    @Test fun anExportThatWasntFinishedIsRefused() {
        val dir = export()
        File(dir, WowExport.MANIFEST).delete()
        val result = run(dir)
        assertTrue(result is ImportPipeline.Result.Failed || result is ImportPipeline.Result.Waiting)
    }

    @Test fun aMissingFileIsNamed() {
        val dir = export()
        File(dir, "files/addons/Questie/Questie.lua").delete()
        val result = run(dir)
        assertEquals(Problem.MISSING_SOURCE_DATA, (result as ImportPipeline.Result.Failed).error.problem)
        assertTrue(result.error.message!!.contains("Questie.lua"))
    }

    @Test fun anotherAppsExportOrANewerFormatIsRefused() {
        assertEquals(Problem.MISSING_SOURCE_DATA, (run(export(app = "com.example.other")) as ImportPipeline.Result.Failed).error.problem)
        paths = GamePaths(tmp.newFolder())
        assertEquals(Problem.UNSUPPORTED_VERSION, (run(export(tmp.newFolder("WoW-export2"), format = 2)) as ImportPipeline.Result.Failed).error.problem)
    }

    @Test fun pathsThatEscapeAreNotAllowed() {
        for (bad in listOf("../x", "/etc/passwd", "a/../b", "a\\b", "a//b")) {
            try { WowExport.safePath(bad); fail(bad) } catch (e: ImportException) { assertEquals(Problem.CORRUPT_ARCHIVE, e.problem) }
        }
        assertEquals("client/Data/a.MPQ", WowExport.safePath("client/Data/a.MPQ"))
    }

    @Test fun checksumLinesRoundTrip() {
        val e = listOf(WowExport.Entry("a".repeat(64), 5, "z/b"), WowExport.Entry("b".repeat(64), 7, "a/c d"))
        assertEquals(e.sortedBy { it.path }, WowExport.parseChecksums(WowExport.checksumsText(e)))
        try { WowExport.parseChecksums("short\t1\tp"); fail() } catch (x: ImportException) { assertEquals(Problem.CORRUPT_ARCHIVE, x.problem) }
    }
}
