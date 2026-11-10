package com.logie.blizz.importer

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
import java.io.ByteArrayInputStream
import java.io.File
import java.io.InputStream

/** Running a game's own installer in the app's Windows: the copy, its states, and finding what it made. */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class InstallerRunTest {
    @get:Rule val tmp = TemporaryFolder()
    private val game = "starcraft2"
    private val importer = StarCraft2OfflineImporter()
    private lateinit var paths: GamePaths
    private var wine: File? = null
    private var log = ""
    private val host = object : InstallerHost {
        override fun wineDriveC(): File? = wine
        override fun logTail(): String = log
    }

    /** A file as the document picker gives it: no path, no neighbours, and it counts how often it was opened. */
    private class Mem(override val name: String, val data: ByteArray, val kids: List<Mem> = emptyList(), override val isDirectory: Boolean = false) : SourceNode {
        var opens = 0
        override val size: Long get() = data.size.toLong()
        override val display: String get() = name
        override fun children(): List<SourceNode> = kids
        /** Called after each read with the bytes read so far. */
        var onRead: (Int) -> Unit = {}
        override fun open(): InputStream {
            opens++
            return object : ByteArrayInputStream(data) {
                override fun read(b: ByteArray, off: Int, len: Int): Int = super.read(b, off, len).also { onRead(pos) }
            }
        }
    }

    private fun shell() = Mem("Setup.exe", ByteArray(4096) { if (it < 2) "MZ"[it].code.toByte() else 0 })
    private fun data(name: String, n: Int, fill: Int) = Mem(name, ByteArray(n) { fill.toByte() })
    private fun folder(vararg files: Mem) = Mem("SC2", ByteArray(0), files.toList(), true)

    private fun env(cancel: CancelToken = CancelToken(), progress: (Progress) -> Unit = {}): ImportEnv {
        paths = if (this::paths.isInitialized) paths else GamePaths(tmp.newFolder())
        return ImportEnv(paths, { emptyList() }, { false }, DownloadManager(), GitHubReleases(), null, innoextractTool, cancel, progress)
    }

    private fun status(now: Long = System.currentTimeMillis()) =
        InstallerRun.status(paths, game, importer.isGameRoot, importer::looseGameRoot, host, now)

    private fun aged(dir: File, at: Long) { dir.walkTopDown().forEach { it.setLastModified(at) } }

    // ---- Switches ----


    /** A file as a walk of a folder the app may read gives it: no path, but it knows what was listed with it. */
    private class Found(private val self: Mem, private val beside: () -> List<SourceNode>) : SourceNode by self {
        override fun siblings(): List<SourceNode>? = beside()
    }

    @Test fun anInstallerFoundInASearchedFolderSeesTheDataFilesBesideIt() {
        // The phone's Warcraft II from GOG (4 and 8 November 2026): an 859 KB program with its data in the .bin beside it.
        val setup = Mem("setup_warcraft_ii_2.02_v5_(78104).exe", ByteArray(4096) { if (it < 2) "MZ"[it].code.toByte() else 0 })
        val bin = Mem("setup_warcraft_ii_2.02_v5_(78104)-1.bin", ByteArray(1 shl 20) { 7 })
        val note = Mem("readme.txt", ByteArray(10))
        lateinit var all: List<SourceNode>
        val found = Found(setup) { all }
        all = listOf(found, bin, note)
        val (program, files) = InstallerRun.find(found)!!
        assertEquals(setup.name, program.name)
        assertEquals(listOf(bin.name), Installers.parts(program, files).map { it.name })
        assertFalse(InstallerRun.needsFolder(found))
        // Picked by itself with the document picker it has no neighbours: the folder is asked for, as before.
        assertEquals(null, setup.siblings())
        assertTrue(InstallerRun.needsFolder(setup))
        // On the phone's own storage the folder is read.
        val dir = tmp.newFolder("gog")
        File(dir, setup.name).writeBytes(setup.data)
        File(dir, bin.name).writeBytes(bin.data)
        val local = FileNode(File(dir, setup.name))
        assertEquals(listOf(bin.name), InstallerRun.find(local)!!.let { (p, f) -> Installers.parts(p, f) }.map { it.name })
    }
    @Test fun eachRunUsesTheNextSetOfSwitchesAndTheTargetFolder() {
        val all = (0 until InstallerRun.VARIANT_COUNT).map { InstallerRun.arguments(game, it) }
        assertEquals(all.size, all.toSet().size)
        assertTrue(all[0].contains("/DIR=T:\\starcraft2-installer\\out"))
        assertTrue(all.any { it.contains("/VERYSILENT") })
        assertTrue(all.any { it.contains("/LANG=english") })
        assertTrue(all.any { it.contains("/SP-") && it.contains("/NOCANCEL") })
        assertFalse(all.last().contains("/DIR="))
        assertEquals(all[0], InstallerRun.arguments(game, InstallerRun.VARIANT_COUNT))
        assertTrue(InstallerRun.arguments("diablo2", 1).contains("T:\\diablo2-installer\\out"))
    }

    @Test fun beginRunCountsTheRuns() {
        paths = GamePaths(tmp.newFolder())
        paths.installer(game).mkdirs()
        assertNull(InstallerRun.readRun(paths, game))
        assertEquals(0, InstallerRun.beginRun(paths, game, 1000).attempt)
        assertEquals(1, InstallerRun.beginRun(paths, game, 2000).attempt)
        assertEquals(InstallerRun.RunRecord(1, 2000), InstallerRun.readRun(paths, game))
    }

    // ---- A file picked alone ----

    @Test fun anInstallerPickedAsAFileWithNothingBesideItAsksForTheFolder() {
        assertTrue(InstallerRun.needsFolder(shell()))
        // In a folder (or beside its data in a real directory) it doesn't.
        assertFalse(InstallerRun.needsFolder(folder(shell(), data("Data01.dxn", 1_300_000, 1))))
        val real = tmp.newFolder("real")
        File(real, "Setup.exe").writeBytes(shell().data)
        File(real, "Data01.dxn").writeBytes(ByteArray(1_300_000))
        assertFalse(InstallerRun.needsFolder(FileNode(File(real, "Setup.exe"))))
        val q = InstallerRun.folderQuestion("Setup.exe")
        assertEquals(PickKind.FOLDER, q.kind)
        assertEquals(InstallerRun.FOLDER_INPUT, q.id)
        assertTrue(q.prompt.contains("Data01.dxn") && q.prompt.contains("FOLDER"))
    }

    @Test fun theImportAsksForTheFolderInsteadOfUnpackingTheShell() {
        paths = GamePaths(tmp.newFolder())
        val marker = File(tmp.root, "inno-ran")
        innoMarker(marker)
        val lone = shell()
        val pipeline = ImportPipeline(ImportStateRepository(paths), Library(paths))
        val result = pipeline.run(importer, env(), mapOf("install" to Supplied.Picked("install", lone)))
        assertTrue(result.toString(), result is ImportPipeline.Result.Waiting)
        val missing = (result as ImportPipeline.Result.Waiting).missing.single()
        assertEquals(InstallerRun.FOLDER_INPUT, missing.id)
        assertEquals(PickKind.FOLDER, missing.kind)
        assertFalse("innoextract must not have run", marker.exists())
        // The folder as the answer: the import goes on (to saying the installer must run, with the folder's data files seen).
        val answer = mapOf("install" to Supplied.Picked("install", lone), InstallerRun.FOLDER_INPUT to Supplied.Picked(InstallerRun.FOLDER_INPUT, folder(shell(), data("Data01.dxn", 1_300_000, 1))))
        val next = pipeline.run(importer, env(), answer)
        assertTrue(next.toString(), next is ImportPipeline.Result.Failed)
    }

    private fun innoMarker(marker: File) {
        val script = File(tmp.root, "inno-marker.sh").apply { writeText("#!/bin/sh\ntouch '${marker.path}'\necho 'not an Inno Setup file' >&2\nexit 1\n"); setExecutable(true) }
        innoextractTool = Innoextract(script)
    }

    private var innoextractTool: Innoextract? = null

    @Test fun anInstallerWithNoDataFilesIsAClearErrorBeforeAnyWork() {
        val marker = File(tmp.root, "inno-ran2")
        innoMarker(marker)
        val scratch = tmp.newFolder("scratch")
        try {
            Unpacker(innoextractTool).unpack(shell(), emptyList(), tmp.newFolder("dest"), scratch, CancelToken()) {}
            fail("expected an error")
        } catch (e: ImportException) {
            assertEquals(Problem.UNSUPPORTED_INSTALLER, e.problem)
            assertTrue(e.message!!.contains("data files"))
        }
        assertFalse(marker.exists())
        assertFalse(File(scratch, "installer").exists())
    }

    // ---- The copy ----

    @Test fun theCopyReportsBytesAndKeepsOnlyTheInstallerAndItsData() {
        val seen = ArrayList<Progress>()
        val e = env(progress = { seen += it })
        val source = folder(shell(), data("Data02.dxn", 1_100_000, 2), data("Data01.dxn", 1_200_000, 1), data("readme.txt", 2_000_000, 3))
        val setup = InstallerRun.prepare(e, game, source)
        assertEquals(File(paths.installer(game), "Setup.exe"), setup)
        assertEquals(setOf("Setup.exe", "Data01.dxn", "Data02.dxn", "manifest.txt"), paths.installer(game).list()!!.toSet())
        assertTrue(InstallerRun.copyComplete(paths, game))
        val total = 4096L + 1_100_000 + 1_200_000
        assertTrue(seen.any { it.total == total && it.label.contains("Data01.dxn") && it.label.contains("of 3") })
        assertEquals(total, seen.last().done)
        assertEquals(total, seen.last().total)
    }

    @Test fun aStoppedCopyGoesOnFromWhereItStoppedAndNeverCopiesCompleteFilesAgain() {
        val e = env()
        val dir = paths.installer(game).also { it.mkdirs() }
        val setup = shell()
        val one = data("Data01.dxn", 1_200_000, 1)
        val two = data("Data02.dxn", 1_100_000, 2)
        // Earlier: Setup.exe and Data01 copied whole; Data02 stopped at 400 000 bytes.
        File(dir, "Setup.exe").writeBytes(setup.data)
        File(dir, "Data01.dxn").writeBytes(one.data)
        File(dir, ".Data02.dxn.part").writeBytes(two.data.copyOf(400_000))
        val seen = ArrayList<Progress>()
        val resumed = env(progress = { seen += it })
        InstallerRun.prepare(resumed, game, folder(setup, one, two))
        assertEquals("complete files are not opened again", 0, setup.opens + one.opens)
        assertEquals(1, two.opens)
        assertTrue(File(dir, "Data02.dxn").readBytes().contentEquals(two.data))
        assertFalse(File(dir, ".Data02.dxn.part").exists())
        // The first report already counts what was there.
        assertTrue(seen.first().done >= 4096 + 1_200_000 + 400_000)
        assertNotNull(e)
    }

    @Test fun aPartialCopyIsReportedAsOneAndCancelKeepsIt() {
        val cancel = CancelToken()
        val one = data("Data01.dxn", 3_000_000, 1)
        // The source stops the copy once a megabyte has been read (as tapping Cancel would).
        one.onRead = { read -> if (read > 1_000_000) cancel.cancel() }
        val e = env(cancel)
        try {
            InstallerRun.prepare(e, game, folder(shell(), one))
            fail("expected cancel")
        } catch (x: ImportException) {
            assertEquals(Problem.CANCELLED, x.problem)
        }
        val s = status()
        assertTrue(s.toString(), s is InstallerRun.Status.PartialCopy)
        s as InstallerRun.Status.PartialCopy
        assertTrue(s.done in 1..s.total)
        assertEquals(4096L + 3_000_000, s.total)
        assertTrue(InstallerRun.describe(s).first.contains("stopped part-way"))
        // Going on later finishes it.
        one.onRead = {}
        InstallerRun.prepare(env(), game, folder(shell(), one))
        assertTrue(InstallerRun.copyComplete(paths, game))
    }

    @Test fun aLoneFilePassedToTheCopyIsRefusedWithTheQuestion() {
        val e = env()
        try {
            InstallerRun.prepare(e, game, shell())
            fail("expected an error")
        } catch (x: ImportException) {
            assertTrue(x.message!!.contains("FOLDER"))
        }
        assertFalse(InstallerRun.copyComplete(paths, game))
    }

    // ---- What the installer made ----

    private fun copied(): File {
        InstallerRun.prepare(env(), game, folder(shell(), data("Data01.dxn", 1_200_000, 1)))
        return paths.installer(game)
    }

    @Test fun beforeAnyRunTheCopyIsReady() {
        copied()
        assertTrue(status() is InstallerRun.Status.Ready)
    }

    @Test fun anInstallerThatWroteNothingIsWaitingWithTheWineLog() {
        copied()
        val run = InstallerRun.beginRun(paths, game, 0)
        log = "wine: err:module:import_dll failed"
        val s = status(now = 12 * 60_000L)
        assertTrue(s.toString(), s is InstallerRun.Status.Waiting)
        s as InstallerRun.Status.Waiting
        assertEquals(run.attempt, s.attempt)
        assertEquals(12L, s.minutes)
        assertEquals(0L, s.written)
        assertTrue(s.log.contains("import_dll"))
        assertTrue(InstallerRun.describe(s).second!!.contains("may have ended without installing"))
        // The import says so rather than unpacking the shell again, naming what to do.
        val pipeline = ImportPipeline(ImportStateRepository(paths), Library(paths))
        val failed = pipeline.run(importer, env(), mapOf("install" to Supplied.Picked("install", folder(shell(), data("Data01.dxn", 1_200_000, 1))))) as ImportPipeline.Result.Failed
        assertEquals(Problem.INSTALLER_MUST_RUN, failed.error.problem)
        assertTrue(failed.error.message!!.contains("no StarCraft II has appeared"))
    }

    @Test fun aGameBeingWrittenIsInstallingAndOneThatHasStoppedChangingIsFinished() {
        val dir = copied()
        InstallerRun.beginRun(paths, game, 0)
        val out = InstallerRun.out(paths, game)
        Fixtures.starcraft2Install(File(out, "StarCraft II"))
        val written = System.currentTimeMillis()
        aged(out, written)
        val installing = status(now = written + 30_000)
        assertTrue(installing.toString(), installing is InstallerRun.Status.Installing)
        val done = status(now = written + InstallerRun.QUIET_MS + 1000)
        assertTrue(done.toString(), done is InstallerRun.Status.Finished)
        done as InstallerRun.Status.Finished
        assertEquals(File(out, "StarCraft II"), done.root)
        assertEquals(InstallerRun.Where.OUT, done.where)
        assertTrue(InstallerRun.describe(done).second!!.contains("Import what it installed"))
        assertNotNull(dir)
        // And the import takes it.
        val result = ImportPipeline(ImportStateRepository(paths), Library(paths)).run(importer, env(), emptyMap())
        assertTrue(result.toString(), result is ImportPipeline.Result.Done)
        assertFalse(paths.installer(game).exists())
    }

    @Test fun aGameTheInstallerPutInWindowsCDriveInsteadIsFoundAndTakenIn() {
        copied()
        InstallerRun.beginRun(paths, game, 0)
        val c = tmp.newFolder("drive_c")
        wine = c
        // Nothing yet: Waiting. (The saves the app seeds there are not a game.)
        File(c, "users/xuser/Documents/StarCraft II/Accounts").mkdirs()
        File(c, "windows/system32").mkdirs()
        assertTrue(status() is InstallerRun.Status.Waiting)
        val game86 = File(c, "Program Files (x86)/StarCraft II")
        Fixtures.starcraft2Install(game86)
        val old = System.currentTimeMillis() - 10 * 60_000
        aged(game86, old)
        val s = status()
        assertTrue(s.toString(), s is InstallerRun.Status.Finished)
        assertEquals(InstallerRun.Where.WINDOWS, (s as InstallerRun.Status.Finished).where)
        assertEquals(game86, s.root)
        assertTrue(InstallerRun.describe(s).second!!.contains("app's Windows"))
        // Moved into out/, where the import reads it.
        val moved = InstallerRun.collect(paths, game, importer.isGameRoot, importer::looseGameRoot, host)
        assertEquals(File(InstallerRun.out(paths, game), "StarCraft II"), moved)
        assertFalse(game86.exists())
        val result = ImportPipeline(ImportStateRepository(paths), Library(paths)).run(importer, env(), emptyMap())
        assertTrue(result.toString(), result is ImportPipeline.Result.Done)
    }

    @Test fun theBlizzardEntertainmentAndUserFoldersAreSearchedToo() {
        for (where in listOf("Program Files/Blizzard Entertainment/StarCraft II", "users/xuser/AppData/Local/Games/odd name", "Games/SC2")) {
            val c = tmp.newFolder("c-${where.hashCode()}")
            Fixtures.starcraft2Install(File(c, where))
            assertEquals(where, File(c, where), InstallerRun.findInWindows(c, importer.isGameRoot, importer::looseGameRoot))
        }
        assertNull(InstallerRun.findInWindows(tmp.newFolder("blank"), importer.isGameRoot, importer::looseGameRoot))
        // A game still being written in Windows is not collected yet.
        copied()
        val c = tmp.newFolder("busy")
        wine = c
        Fixtures.starcraft2Install(File(c, "Program Files/StarCraft II"))
        assertNull(InstallerRun.collect(paths, game, importer.isGameRoot, importer::looseGameRoot, host))
    }

    @Test fun whenOutAlreadyHoldsAGameNothingIsCollected() {
        copied()
        Fixtures.starcraft2Install(File(InstallerRun.out(paths, game), "StarCraft II"))
        val c = tmp.newFolder("c2")
        wine = c
        Fixtures.starcraft2Install(File(c, "Program Files/StarCraft II"))
        aged(c, 0)
        assertNull(InstallerRun.collect(paths, game, importer.isGameRoot, importer::looseGameRoot, host))
        assertTrue(File(c, "Program Files/StarCraft II/Versions").isDirectory)
    }

    // ---- Generic over the game ----

    @Test fun anotherGameUsesTheSameMachineryWithItsOwnRootTest() {
        val other = "diablo2"
        paths = GamePaths(tmp.newFolder())
        val isRoot: (Set<String>) -> Boolean = { "d2data.mpq" in it }
        val loose: (File) -> File? = { null }
        InstallerRun.prepare(env(), other, folder(shell(), data("Data01.bin", 1_200_000, 1)))
        InstallerRun.beginRun(paths, other, 0)
        assertEquals("T:\\diablo2-installer\\out", InstallerRun.arguments(other).substringAfter("/DIR=").substringBefore(" "))
        val c = tmp.newFolder("c3")
        wine = c
        File(c, "Program Files (x86)/Diablo II").mkdirs()
        File(c, "Program Files (x86)/Diablo II/d2data.mpq").writeText("x")
        aged(c, 0)
        val s = InstallerRun.status(paths, other, isRoot, loose, host, now = InstallerRun.QUIET_MS + 10)
        assertTrue(s.toString(), s is InstallerRun.Status.Finished)
        // A reset takes the copy with it.
        GameReset.reset(paths, other)
        assertFalse(paths.installer(other).exists())
    }

    @Test fun removingTheCopyTakesEverythingAwayAndResetDoesToo() {
        copied()
        Fixtures.starcraft2Install(File(InstallerRun.out(paths, game), "StarCraft II"))
        InstallerRun.removeCopy(paths, game)
        assertFalse(paths.installer(game).exists())
        assertEquals(InstallerRun.Status.None, status())
        copied()
        GameReset.reset(paths, game)
        assertFalse(paths.installer(game).exists())
    }
}
