package com.logie.blizz.importer

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.File

/**
 * The importers on the games' real files, downloaded from Blizzard's own legacy servers. Opt-in:
 * BLIZZ_REAL_GAMES names a folder holding d2 (Diablo II 1.14b + Lord of Destruction), sc (StarCraft
 * + Brood War 1.15.2, key not applied), sc3 (the same with the key applied: font\font.gid in
 * StarDat.mpq) and war3 (Warcraft III 1.27 with The Frozen Throne). Each test skips when its
 * folder isn't there. Imports copy gigabytes into a temporary folder.
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class RealFilesTest {
    @get:Rule val tmp = TemporaryFolder()

    private fun real(name: String): File {
        val root = System.getenv("BLIZZ_REAL_GAMES")?.let(::File)
        assumeTrue("BLIZZ_REAL_GAMES not set", root != null && root.isDirectory)
        val dir = File(root, name)
        assumeTrue("$name not in BLIZZ_REAL_GAMES", dir.isDirectory)
        return dir
    }

    private fun env(paths: GamePaths) = ImportEnv(
        paths = paths, searchRoots = { emptyList() }, online = { false }, downloads = DownloadManager(), releases = GitHubReleases(),
        legacy = null, innoextract = null, cancel = CancelToken(), progress = {},
    )

    private fun import(importer: GameImporter, paths: GamePaths, source: File) =
        ImportPipeline(ImportStateRepository(paths), Library(paths)).run(importer, env(paths), mapOf("install" to Supplied.Picked("install", FileNode(source))))

    private fun report(v: Validation) = v.checks.joinToString("\n") { "  [${if (it.passed) "ok" else "FAIL"}] ${it.name}: ${it.detail}" }

    private fun passed(v: Validation, name: String) = v.checks.firstOrNull { it.name == name }?.passed

    // Diablo II ---------------------------------------------------------------------------------------

    @Test fun diabloIIValidation() {
        val d2 = real("d2")
        val v = Diablo2ClassicImporter().validateDir(d2)
        println("D2 validation filesOk=${v.filesOk} client=${v.clientVersion}\n${report(v)}")
        assertTrue(report(v), v.filesOk)
        assertEquals("Diablo II + Lord of Destruction 1.14.1.68", v.clientVersion)
        // The movies, the sound, the languages and every library 1.14b's Game.exe imports.
        for (name in listOf("d2video.mpq", "d2xvideo.mpq", "d2music.mpq", "d2xmusic.mpq", "d2speech.mpq", "d2xtalk.mpq", "d2sfx.mpq", "d2char.mpq", "d2exp.mpq")) {
            assertEquals(name, true, passed(v, name))
        }
        for (name in listOf("binkw32.dll", "smackw32.dll", "ijl11.dll", "D2.LNG")) assertEquals(name, true, passed(v, name))
        assertTrue(v.checks.any { it.name == "Movies" && it.passed })
    }

    @Test fun diabloIIImportsAsAFolder() {
        val d2 = real("d2")
        val paths = GamePaths(tmp.newFolder("files"))
        val result = import(Diablo2ClassicImporter(), paths, d2)
        assertTrue(result.toString(), result is ImportPipeline.Result.Done)
        val entry = Library(paths).get("diablo2")!!
        println("D2 entry: exe=${entry.executable} args='${entry.arguments}' path=${entry.installPath} version=${entry.clientVersion} stage=${entry.stage} saves=${entry.saveLocation}")
        assertEquals("Game.exe", entry.executable)
        assertEquals(LibraryEntry.RUNTIME_WINLATOR, entry.runtime)
        assertEquals(Stage.READY, entry.stage)
        val game = paths.game("diablo2")
        // Every file of the source arrived, byte for byte in size.
        for (f in d2.listFiles()!!.filter { it.isFile }) assertEquals(f.name, f.length(), File(game, f.name).length())
        assertTrue(Diablo2ClassicImporter().validateDir(game).filesOk)
    }

    // StarCraft ---------------------------------------------------------------------------------------

    @Test fun starCraftWithTheKeyValidates() {
        val sc = real("sc3")
        val v = StarCraftClassicImporter().validateDir(sc)
        println("SC (key applied) filesOk=${v.filesOk} client=${v.clientVersion}\n${report(v)}")
        assertTrue(report(v), v.filesOk)
        assertEquals("StarCraft + Brood War 1.15.2.1", v.clientVersion)
        val names = listOf("font\\font.gid", "font\\font.clh", "font\\font16.fnt", "rez\\glumain.bin", "arr\\units.dat")
        println("sc3 StarDat.mpq: ${MpqContents.has(File(sc, "StarDat.mpq"), names)}")
        println("sc3 BrooDat.mpq: ${MpqContents.has(File(sc, "BrooDat.mpq"), names)}")
        println("sc3 patch_rt.mpq: ${MpqContents.has(File(sc, "patch_rt.mpq"), names + listOf("rez\\gluhist.tbl"))}")
    }

    @Test fun starCraftWithoutTheKeyIsRefused() {
        val sc = real("sc")
        val v = StarCraftClassicImporter().validateDir(sc)
        println("SC (no key) filesOk=${v.filesOk} problem=${v.problem}\n${report(v)}")
        // Without the key the stored font.gid/font.clh aren't in StarDat.mpq: the game says "File not found".
        assertFalse(v.filesOk)
    }

    @Test fun starCraftImportsAsAFolder() {
        val sc = real("sc3")
        val paths = GamePaths(tmp.newFolder("files"))
        val result = import(StarCraftClassicImporter(), paths, sc)
        assertTrue(result.toString(), result is ImportPipeline.Result.Done)
        val entry = Library(paths).get("starcraft")!!
        println("SC entry: exe=${entry.executable} args='${entry.arguments}' version=${entry.clientVersion} saves=${entry.saveLocation}")
        assertEquals("StarCraft.exe", entry.executable)
        assertEquals(LibraryEntry.RUNTIME_WINLATOR, entry.runtime)
        assertTrue(StarCraftClassicImporter().validateDir(paths.game("starcraft")).filesOk)
    }

    // Warcraft III ------------------------------------------------------------------------------------

    @Test fun warcraftIIIValidation() {
        val war3 = real("war3")
        for (exe in listOf("War3.exe", "Warcraft III.exe", "Frozen Throne.exe")) {
            val pe = PeInfo.read(File(war3, exe))
            println("$exe: version=${pe?.version} machine=0x${pe?.machine?.toString(16)} imports=${Dependencies.imports(File(war3, exe))} missing=${Dependencies.missing(File(war3, exe))}")
        }
        for (p in Warcraft3Importer.Product.values()) {
            val v = Warcraft3Importer(p).validateDir(war3, p)
            println("WC3 ${p.name} filesOk=${v.filesOk} problem=${v.problem} client=${v.clientVersion}\n${report(v)}")
            val failing = v.checks.filter { !it.passed && it.name != "Started under Winlator" }
            assertTrue(report(v), failing.isEmpty())
            // war3.exe is the game (1.27.0.52240); the two launchers carry versions of their own (1.0.0.1, 1.5.0.0).
            assertEquals("${p.title} 1.27.0.52240", v.clientVersion)
        }
        assertEquals("1.27.0.52240", Warcraft3Importer(Warcraft3Importer.Product.TFT).versionOf(war3))
        run {
        }
    }

    @Test fun warcraftIIISharesOneFolderForBothProducts() {
        val war3 = real("war3")
        val paths = GamePaths(tmp.newFolder("files"))
        val tft = Warcraft3Importer(Warcraft3Importer.Product.TFT)
        val roc = Warcraft3Importer(Warcraft3Importer.Product.ROC)
        val result = import(tft, paths, war3)
        assertTrue(result.toString(), result is ImportPipeline.Result.Done)
        val te = Library(paths).get("warcraft3_tft")!!
        println("WC3 TFT entry: exe=${te.executable} args='${te.arguments}' path=${te.installPath} version=${te.clientVersion}")
        assertEquals("Frozen Throne.exe", te.executable)
        // Reign of Chaos needs no import: it plays from the same folder.
        assertTrue(roc.isShared(paths))
        assertEquals(paths.game("warcraft3_tft"), roc.installDir(paths))
        val re = roc.registerLaunchEntry(env(paths), roc.validate(env(paths)))
        println("WC3 ROC entry: exe=${re.executable} path=${re.installPath} version=${re.clientVersion}")
        assertNotNull(re.executable)
        assertEquals(te.installPath, re.installPath)
    }
}
