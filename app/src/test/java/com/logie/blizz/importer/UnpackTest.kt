package com.logie.blizz.importer

import org.apache.commons.compress.archivers.sevenz.SevenZArchiveEntry
import org.apache.commons.compress.archivers.sevenz.SevenZOutputFile
import org.apache.commons.compress.archivers.tar.TarArchiveEntry
import org.apache.commons.compress.archivers.tar.TarArchiveOutputStream
import org.apache.commons.compress.compressors.gzip.GzipCompressorOutputStream
import org.apache.commons.compress.compressors.xz.XZCompressorOutputStream
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

/** StarCraft II from whatever form it comes in: a folder, zip, 7z, tar.*, disc image, or installer with its data files. */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class UnpackTest {
    @get:Rule val tmp = TemporaryFolder()
    private lateinit var paths: GamePaths
    private var innoextract: Innoextract? = null

    private fun env() = ImportEnv(
        paths = paths, searchRoots = { emptyList() }, online = { false }, downloads = DownloadManager(), releases = GitHubReleases(),
        legacy = null, innoextract = innoextract, cancel = CancelToken(), progress = {},
    )

    private fun run(source: File): ImportPipeline.Result {
        paths = GamePaths(tmp.newFolder())
        val pipeline = ImportPipeline(ImportStateRepository(paths), Library(paths))
        return pipeline.run(StarCraft2OfflineImporter(), env(), mapOf("install" to Supplied.Picked("install", FileNode(source))))
    }

    /** The game's files as a map of path → bytes, for packing. */
    private fun game(build: String = "39117", version: String = "3.0.5.39117"): Map<String, ByteArray> {
        val dir = tmp.newFolder("src-$build-${System.nanoTime()}")
        Fixtures.starcraft2Install(dir, build, version)
        return dir.walkTopDown().filter { it.isFile }.associate { it.relativeTo(dir).path.replace('\\', '/') to it.readBytes() }
    }

    private fun assertImported(result: ImportPipeline.Result, version: String) {
        assertTrue(result.toString(), result is ImportPipeline.Result.Done)
        assertEquals("StarCraft II $version (offline)", (result as ImportPipeline.Result.Done).validation.clientVersion)
        assertEquals(Stage.IMPORTED_UNTESTED, result.record.stage)
    }

    @Test fun theGameFoundWhereverItsMarkersLandedAndWhateverTheFoldersAreCalled() {
        val dir = tmp.newFolder("loose")
        File(dir, "app/{commonappdata}/odd/VERSIONS/base39117").mkdirs()
        File(dir, "app/{commonappdata}/odd/VERSIONS/base39117/SC2.exe").writeText("x")
        assertEquals(File(dir, "app/{commonappdata}/odd"), StarCraft2OfflineImporter().looseGameRoot(dir))
        val data = tmp.newFolder("loose2")
        File(data, "x/y/sc2data").mkdirs()
        assertEquals(File(data, "x/y"), StarCraft2OfflineImporter().looseGameRoot(data))
        assertEquals(null, StarCraft2OfflineImporter().looseGameRoot(tmp.newFolder("empty")))
    }

    @Test fun aGameInsideAnArchiveInsideTheOneGiven() {
        val inner = Fixtures.zip(tmp.newFile("inner.zip"), game() + ("pad.bin" to ByteArray(1 shl 18).also { java.util.Random(7).nextBytes(it) }))
        assertImported(run(Fixtures.zip(tmp.newFile("outer.zip"), mapOf("Disc/readme.txt" to "hi".toByteArray(), "Disc/Data/game.zip" to inner.readBytes()))), "3.0.5.39117")
    }

    @Test fun whatTheGamesOwnInstallerMadeIsImported() {
        paths = GamePaths(tmp.newFolder())
        Fixtures.starcraft2Install(File(paths.installer("starcraft2"), "out/StarCraft II"))
        val pipeline = ImportPipeline(ImportStateRepository(paths), Library(paths))
        val result = pipeline.run(StarCraft2OfflineImporter(), env(), emptyMap())
        assertImported(result, "3.0.5.39117")
        // The installer's copy is gone once the game is in.
        assertTrue(!paths.installer("starcraft2").exists())
    }

    @Test fun anInstallerThatMakesNoFilesUntilItRunsIsSaidToNeedRunning() {
        val dir = tmp.newFolder("repack")
        File(dir, "Setup.exe").writeBytes(ByteArray(2048) { if (it < 2) "MZ"[it].code.toByte() else 0 })
        File(dir, "Data01.dxn").writeBytes(ByteArray(1 shl 21) { 7 })
        val result = run(dir)
        assertTrue(result.toString(), result is ImportPipeline.Result.Failed)
    }

    @Test fun zip() = assertImported(run(Fixtures.zip(tmp.newFile("sc2.zip"), game().mapKeys { "StarCraft II/${it.key}" })), "3.0.5.39117")

    @Test fun theNewerBuildToo() = assertImported(run(Fixtures.zip(tmp.newFile("sc2.zip"), game("41219", "3.1.4.41219"))), "3.1.4.41219")

    @Test fun sevenZ() {
        val file = tmp.newFile("sc2.7z")
        SevenZOutputFile(file).use { z ->
            for ((path, data) in game()) {
                z.putArchiveEntry(SevenZArchiveEntry().apply { name = path; size = data.size.toLong() })
                z.write(data); z.closeArchiveEntry()
            }
        }
        assertImported(run(file), "3.0.5.39117")
    }

    @Test fun tarInAnyCompression() {
        fun tar(out: java.io.OutputStream) = TarArchiveOutputStream(out).use { t ->
            for ((path, data) in game()) {
                t.putArchiveEntry(TarArchiveEntry(path).apply { size = data.size.toLong() })
                t.write(data); t.closeArchiveEntry()
            }
        }
        val plain = tmp.newFile("a.tar").also { f -> tar(f.outputStream()) }
        val gz = tmp.newFile("a.tgz").also { f -> tar(GzipCompressorOutputStream(f.outputStream())) }
        val xz = tmp.newFile("a.bin").also { f -> tar(XZCompressorOutputStream(f.outputStream())) }
        for (f in listOf(plain, gz, xz)) assertImported(run(f), "3.0.5.39117")
    }

    @Test fun discImageWithLongNames() = assertImported(run(Fixtures.iso(tmp.newFile("sc2.iso"), "SC2", game())), "3.0.5.39117")

    @Test fun theFormatComesFromTheBytesNotTheName() {
        val zip = Fixtures.zip(tmp.newFile("sc2.dat"), game())
        assertEquals(Format.ZIP, Format.of(FileNode(zip)))
        assertEquals(Format.PROGRAM, Format.of(FileNode(Fixtures.pe(tmp.newFile("Setup.exe"), "1.0.0.0"))))
        assertEquals(Format.RAR, Format.of(byteArrayOf('R'.code.toByte(), 'a'.code.toByte(), 'r'.code.toByte(), '!'.code.toByte(), 0x1A, 0x07, 0)))
    }

    @Test fun rarIsSaidPlainly() {
        val rar = tmp.newFile("sc2.rar").apply { writeBytes(byteArrayOf('R'.code.toByte(), 'a'.code.toByte(), 'r'.code.toByte(), '!'.code.toByte(), 0x1A, 0x07, 0, 0, 0, 0)) }
        val result = run(rar) as ImportPipeline.Result.Failed
        assertEquals(Problem.UNSUPPORTED_INSTALLER, result.error.problem)
        assertTrue(result.error.message!!.contains("RAR"))
    }

    /** An installer program whose data files are named anything: they reach innoextract as <installer>-1.bin, -2.bin in order. */
    @Test fun installerWithDataFilesOfAnyName() {
        val folder = tmp.newFolder("repack")
        Fixtures.pe(File(folder, "Setup.exe"), "1.0.0.0")
        File(folder, "Data02.dxn").writeBytes(ByteArray(1_100_000) { 2 })
        File(folder, "Data01.dxn").writeBytes(ByteArray(1_200_000) { 1 })
        // A stand-in for innoextract: checks the slices' names and contents, then writes the game where it's told.
        val game = tmp.newFolder("installed").also { Fixtures.starcraft2Install(it, "41219", "3.1.4.41219") }
        val log = File(tmp.root, "inno.txt")
        val script = File(tmp.root, "inno.sh").apply {
            writeText("""#!/bin/sh
                |for a; do last="${'$'}a"; done
                |dir=${'$'}(dirname "${'$'}last"); base=${'$'}(basename "${'$'}last" .exe)
                |echo "${'$'}(ls "${'$'}dir" | sort | tr '\n' ' ')" > '${log.path}'
                |echo "${'$'}(head -c1 "${'$'}dir/${'$'}base-1.bin" | od -An -tu1) ${'$'}(head -c1 "${'$'}dir/${'$'}base-2.bin" | od -An -tu1)" >> '${log.path}'
                |while [ "${'$'}1" != --output-dir ]; do shift; done; out="${'$'}2"
                |cp -r '${game.path}'/. "${'$'}out"/
                |""".trimMargin())
            setExecutable(true)
        }
        innoextract = Innoextract(script)
        assertImported(run(folder), "3.1.4.41219")
        val lines = log.readLines()
        assertEquals("Setup-1.bin Setup-2.bin Setup.exe", lines[0].trim())
        assertEquals("1 2", lines[1].trim().replace(Regex("\\s+"), " "))
    }

    @Test fun anInstallerAloneAsksForItsDataFiles() {
        val setup = Fixtures.pe(tmp.newFile("Setup.exe"), "1.0.0.0")
        val failing = File(tmp.root, "inno-fail.sh").apply { writeText("#!/bin/sh\necho 'not an Inno Setup file' >&2\nexit 1\n"); setExecutable(true) }
        innoextract = Innoextract(failing)
        // The installer picked alone: its data files can't be seen, so the folder is asked for (innoextract is never run).
        val result = run(setup) as ImportPipeline.Result.Waiting
        assertEquals(InstallerRun.FOLDER_INPUT, result.missing.single().id)
        assertEquals(PickKind.FOLDER, result.missing.single().kind)
        assertTrue(result.missing.single().prompt.contains("data files"))
        assertTrue(!File(paths.game("starcraft2"), "Versions").exists())
        // Unpacked directly, it is a clear error before any work.
        try {
            Unpacker(innoextract).unpack(FileNode(setup), emptyList(), tmp.newFolder("dest"), tmp.newFolder("scr"), CancelToken()) {}
            fail("expected an error")
        } catch (e: ImportException) {
            assertEquals(Problem.UNSUPPORTED_INSTALLER, e.problem)
            assertTrue(e.message!!.contains("data files"))
        }
    }

    @Test fun otherBuildsAreStillRefused() {
        val result = run(Fixtures.zip(tmp.newFile("new.zip"), game("75689", "4.11.4.75689"))) as ImportPipeline.Result.Failed
        assertEquals(Problem.UNSUPPORTED_VERSION, result.error.problem)
    }

    @Test fun anUnsafePathInAnArchiveIsRefused() {
        val result = run(Fixtures.zip(tmp.newFile("evil.zip"), mapOf("../../x" to ByteArray(3)))) as ImportPipeline.Result.Failed
        assertEquals(Problem.CORRUPT_ARCHIVE, result.error.problem)
    }
}
