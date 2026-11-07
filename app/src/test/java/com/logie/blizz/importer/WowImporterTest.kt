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

    @Test fun aMissingFileTheGameCantDoWithoutIsNamed() {
        val dir = export()
        File(dir, "files/client/Data/common.MPQ").delete()
        val result = run(dir)
        assertEquals(Problem.MISSING_SOURCE_DATA, (result as ImportPipeline.Result.Failed).error.problem)
        assertTrue(result.error.message!!.contains("common.MPQ"))
    }

    @Test fun otherMissingFilesAreLeftOutWithANoteAndTheRestComesOver() {
        val dir = export()
        File(dir, "files/addons/Questie/Questie.lua").delete()
        File(dir, "files/turtle/WTF/Config.wtf").delete()
        val result = run(dir)
        assertTrue(result.toString(), result is ImportPipeline.Result.Done)
        val game = paths.game("wow")
        assertEquals(setOf("addons/Questie/Questie.lua", "turtle/WTF/Config.wtf"), File(game, ".export/missing.txt").readLines().toSet())
        assertTrue(!File(game, "files/addons/Questie/Questie.lua").exists())
        assertEquals(5000, File(game, "files/client/Data/common.MPQ").length())
        assertTrue((result as ImportPipeline.Result.Done).validation.checks.first { it.name.startsWith("Every file") }.detail.contains("left out"))
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

    @Test fun twinsKeptApartByTheExportsRenamesAreFound() {
        val dir = export()
        // The export stored the real path data/cameras/FlyByWorgen.m2 as ...~1a2b3c4d (renames in export.json).
        val bytes = "camera".toByteArray()
        File(dir, "files/data/cameras").mkdirs()
        File(dir, "files/data/cameras/FlyByWorgen.m2~1a2b3c4d").writeBytes(bytes)
        val sha = java.security.MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }
        val entries = WowExport.parseChecksums(File(dir, WowExport.CHECKSUMS).readText()) + WowExport.Entry(sha, bytes.size.toLong(), "data/cameras/FlyByWorgen.m2")
        File(dir, WowExport.CHECKSUMS).writeText(WowExport.checksumsText(entries))
        val m = WowExport.parseManifest(File(dir, WowExport.MANIFEST).readText())
        File(dir, WowExport.MANIFEST).writeText(WowExport.manifestJson(m.copy(files = m.files + 1, folders = m.folders + "data", renames = mapOf("data/cameras/FlyByWorgen.m2" to "data/cameras/FlyByWorgen.m2~1a2b3c4d"))))
        val result = run(dir)
        assertTrue(result.toString(), result is ImportPipeline.Result.Done)
        assertEquals("camera", File(paths.game("wow"), "files/data/cameras/FlyByWorgen.m2").readText())
    }

    @Test fun anOlderExportsParenthesisedCopyOfACaseTwinIsFound() {
        val dir = export()
        // Before the fix, shared storage kept the second twin as "flybyworgen (1).m2".
        val bytes = "second".toByteArray()
        File(dir, "files/data/cameras").mkdirs()
        File(dir, "files/data/cameras/flybyworgen (1).m2").writeBytes(bytes)
        val sha = java.security.MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }
        File(dir, WowExport.CHECKSUMS).writeText(WowExport.checksumsText(WowExport.parseChecksums(File(dir, WowExport.CHECKSUMS).readText()) + WowExport.Entry(sha, bytes.size.toLong(), "data/cameras/flybyworgen.m2")))
        val m = WowExport.parseManifest(File(dir, WowExport.MANIFEST).readText())
        File(dir, WowExport.MANIFEST).writeText(WowExport.manifestJson(m.copy(files = m.files + 1, folders = m.folders + "data")))
        val result = run(dir)
        assertTrue(result.toString(), result is ImportPipeline.Result.Done)
        assertEquals("second", File(paths.game("wow"), "files/data/cameras/flybyworgen.m2").readText())
    }

    @Test fun anOlderExportsCopyNamedWithTheNumberAfterTheWholeNameIsFoundByItsChecksum() {
        val dir = export()
        // Shared storage kept the second twin as "flybyworgen.m2 (1)"; the first twin, with other bytes, is there too.
        File(dir, "files/data/cameras").mkdirs()
        File(dir, "files/data/cameras/FlyByWorgen.m2").writeBytes("first".toByteArray())
        val second = "second".toByteArray()
        File(dir, "files/data/cameras/flybyworgen.m2 (1)").writeBytes(second)
        val sha = java.security.MessageDigest.getInstance("SHA-256").digest(second).joinToString("") { "%02x".format(it) }
        val first = java.security.MessageDigest.getInstance("SHA-256").digest("first".toByteArray()).joinToString("") { "%02x".format(it) }
        val entries = WowExport.parseChecksums(File(dir, WowExport.CHECKSUMS).readText()) +
            WowExport.Entry(first, 5, "data/cameras/FlyByWorgen.m2") + WowExport.Entry(sha, second.size.toLong(), "data/cameras/flybyworgen.m2")
        File(dir, WowExport.CHECKSUMS).writeText(WowExport.checksumsText(entries))
        val m = WowExport.parseManifest(File(dir, WowExport.MANIFEST).readText())
        File(dir, WowExport.MANIFEST).writeText(WowExport.manifestJson(m.copy(files = m.files + 2, folders = m.folders + "data")))
        val result = run(dir)
        assertTrue(result.toString(), result is ImportPipeline.Result.Done)
        assertEquals("first", File(paths.game("wow"), "files/data/cameras/FlyByWorgen.m2").readText())
        assertEquals("second", File(paths.game("wow"), "files/data/cameras/flybyworgen.m2").readText())
    }

    @Test fun aMissingFileIsFoundByItsContentWhateverItIsCalledAndWhereverItIs() {
        val dir = export()
        val bytes = "lost camera".toByteArray()
        val sha = java.security.MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }
        // Listed as data/cameras/flybygoblin.m2, but the only copy is somewhere else under another name.
        File(dir, "files/stray").mkdirs()
        File(dir, "files/stray/unnamed 3.bin").writeBytes(bytes)
        // A decoy of the same size with other bytes.
        File(dir, "files/stray/decoy.bin").writeBytes("LOST CAMERA".toByteArray())
        File(dir, WowExport.CHECKSUMS).writeText(WowExport.checksumsText(WowExport.parseChecksums(File(dir, WowExport.CHECKSUMS).readText()) + WowExport.Entry(sha, bytes.size.toLong(), "data/cameras/flybygoblin.m2")))
        val m = WowExport.parseManifest(File(dir, WowExport.MANIFEST).readText())
        File(dir, WowExport.MANIFEST).writeText(WowExport.manifestJson(m.copy(files = m.files + 1, folders = m.folders + "data")))
        val result = run(dir)
        assertTrue(result.toString(), result is ImportPipeline.Result.Done)
        assertEquals("lost camera", File(paths.game("wow"), "files/data/cameras/flybygoblin.m2").readText())
    }

    @Test fun whatNothingMatchesIsNamedAndSaysWhatWasSearched() {
        val dir = export()
        File(dir, WowExport.CHECKSUMS).writeText(WowExport.checksumsText(WowExport.parseChecksums(File(dir, WowExport.CHECKSUMS).readText()) + WowExport.Entry("e".repeat(64), 9, "client/Data/gone.MPQ")))
        val m = WowExport.parseManifest(File(dir, WowExport.MANIFEST).readText())
        File(dir, WowExport.MANIFEST).writeText(WowExport.manifestJson(m.copy(files = m.files + 1)))
        val result = run(dir) as ImportPipeline.Result.Failed
        assertTrue(result.error.message!!.contains("by content"))
        assertTrue(result.error.detail!!.contains("client/Data/gone.MPQ"))
    }

    /** The export as the WoW app now writes it: one zip (Zip64, stored, data descriptors), `checksums.tsv` and `export.json` last. */
    private fun zipOf(dir: File, withManifest: Boolean = true, mode: String? = null): File {
        val zipFile = File(tmp.newFolder(), "WoW-export.zip")
        org.apache.commons.compress.archivers.zip.ZipArchiveOutputStream(zipFile).use { zip ->
            zip.setUseZip64(org.apache.commons.compress.archivers.zip.Zip64Mode.Always)
            zip.setMethod(java.util.zip.ZipEntry.DEFLATED)
            zip.setLevel(java.util.zip.Deflater.NO_COMPRESSION)
            fun put(name: String, bytes: ByteArray) {
                zip.putArchiveEntry(org.apache.commons.compress.archivers.zip.ZipArchiveEntry(name))
                zip.write(bytes)
                zip.closeArchiveEntry()
            }
            if (mode != null) put(WowImporter.MODE_ENTRY, mode.toByteArray())
            File(dir, "files").walkTopDown().filter { it.isFile }.sortedBy { it.path }.forEach { put("files/" + it.relativeTo(File(dir, "files")).path, it.readBytes()) }
            File(dir, "prefs").listFiles()?.forEach { put("prefs/${it.name}", it.readBytes()) }
            put(WowExport.CHECKSUMS, File(dir, WowExport.CHECKSUMS).readBytes())
            if (withManifest) put(WowExport.MANIFEST, File(dir, WowExport.MANIFEST).readBytes())
        }
        return zipFile
    }

    @Test fun anExportZipIsReadInOnePassAndKeptWhole() {
        val result = run(zipOf(export()))
        assertTrue(result.toString(), result is ImportPipeline.Result.Done)
        val game = paths.game("wow")
        assertEquals("print('hi')", File(game, "files/addons/Questie/Questie.lua").readText())
        assertEquals(5000, File(game, "files/client/Data/common.MPQ").length())
        assertTrue(File(game, ".export/export.json").isFile && File(game, ".export/checksums.tsv").isFile)
        assertTrue(File(game, ".export/prefs/environments.json").isFile)
        assertTrue(!File(paths.staging, "wow-work").exists())
    }

    /** A file the provider hands over as a pipe: no seeking, so the streaming reader is used. */
    private class PipeNode(private val file: File) : SourceNode by FileNode(file) {
        override fun channel(): java.nio.channels.SeekableByteChannel? = null
    }

    @Test fun aZipFromASourceThatCannotSeekIsReadByStreamingToo() {
        paths = GamePaths(tmp.newFolder())
        val zip = zipOf(export())
        val result = ImportPipeline(ImportStateRepository(paths), Library(paths)).run(WowImporter(), env(), mapOf("install" to Supplied.Picked("install", PipeNode(zip))))
        assertTrue(result.toString(), result is ImportPipeline.Result.Done)
        assertEquals("print('hi')", File(paths.game("wow"), "files/addons/Questie/Questie.lua").readText())
        assertEquals(5000, File(paths.game("wow"), "files/client/Data/common.MPQ").length())
    }

    @Test fun aZipThatWasCutOffIsRefusedAndNothingIsLeftHalfMade() {
        val zip = zipOf(export())
        val bytes = zip.readBytes()
        zip.writeBytes(bytes.copyOf(bytes.size / 2))
        val result = run(zip)
        assertTrue(result.toString(), result is ImportPipeline.Result.Failed)
        assertTrue(!paths.game("wow").exists())
        assertTrue(!File(paths.staging, "wow-work").exists())
    }

    @Test fun aZipWithADamagedFileIsRefusedByItsChecksum() {
        val zip = zipOf(export())
        val bytes = zip.readBytes()
        val marker = "print('hi')".toByteArray()
        val at = (0..bytes.size - marker.size).first { i -> marker.indices.all { bytes[i + it] == marker[it] } }
        bytes[at] = 'X'.code.toByte()
        zip.writeBytes(bytes)
        val result = run(zip)
        assertEquals(Problem.CORRUPT_ARCHIVE, (result as ImportPipeline.Result.Failed).error.problem)
        assertTrue(result.error.message!!.contains("Questie.lua"))
    }

    @Test fun aZipWithoutItsManifestDidntFinish() {
        val result = run(zipOf(export(), withManifest = false))
        assertEquals(Problem.CORRUPT_ARCHIVE, (result as ImportPipeline.Result.Failed).error.problem)
        assertTrue(result.error.message!!.contains("export.json"))
    }

    private fun zipWithMode(mode: String?): File {
        val dir = export(tmp.newFolder())
        if (mode != null) {
            val manifest = File(dir, WowExport.MANIFEST)
            manifest.writeText(org.json.JSONObject(manifest.readText()).put("mode", mode).toString())
        }
        return zipOf(dir, mode = mode)
    }

    private fun runMode(zip: File, mode: WowImporter.WowMode): ImportPipeline.Result {
        paths = if (::paths.isInitialized) paths else GamePaths(tmp.newFolder())
        return ImportPipeline(ImportStateRepository(paths), Library(paths)).run(WowImporter(mode), env(), mapOf("install" to Supplied.Picked("install", FileNode(zip))))
    }

    @Test fun eachModeTakesItsOwnZipAndKeepsItsOwnFolder() {
        val legion = runMode(zipWithMode("legion"), WowImporter.WowMode.LEGION)
        assertTrue(legion.toString(), legion is ImportPipeline.Result.Done)
        assertEquals(LibraryEntry.RUNTIME_EXTERNAL, (legion as ImportPipeline.Result.Done).entry.runtime)
        assertEquals("wow_legion", legion.entry.gameId)
        assertTrue(File(paths.game("wow_legion"), "files/client/Data/common.MPQ").isFile)
        assertTrue(!paths.game("wow").exists())
        val wrath = runMode(zipWithMode("wrath-plus"), WowImporter.WowMode.WRATH_PLUS)
        assertEquals(LibraryEntry.RUNTIME_EXTERNAL, (wrath as ImportPipeline.Result.Done).entry.runtime)
    }

    @Test fun aZipOfAnotherModeIsRefusedByName() {
        val result = runMode(zipWithMode("octowow"), WowImporter.WowMode.LEGION)
        assertEquals(Problem.MISSING_SOURCE_DATA, (result as ImportPipeline.Result.Failed).error.problem)
        assertTrue(result.error.message!!.contains("OctoWoW"))
        assertTrue(!paths.game("wow_legion").exists())
    }

    @Test fun anExportMadeBeforeModesIsWrathPlusOnly() {
        assertTrue(runMode(zipWithMode(null), WowImporter.WowMode.WRATH_PLUS) is ImportPipeline.Result.Done)
        assertTrue(runMode(zipWithMode(null), WowImporter.WowMode.FOREVER) is ImportPipeline.Result.Failed)
    }

    @Test fun aFolderNodeDeletesWithWhatIsInIt() {
        val dir = export(tmp.newFolder())
        assertTrue(FileNode(dir).delete())
        assertTrue(!dir.exists())
    }
}
