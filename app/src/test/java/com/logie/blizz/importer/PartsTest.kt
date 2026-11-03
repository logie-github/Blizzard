package com.logie.blizz.importer

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File
import java.net.Socket
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class PartsTest {
    @get:Rule val tmp = TemporaryFolder()

    @Test fun programVersionsAndLibraries() {
        val exe = Fixtures.pe(tmp.newFile("Game.exe"), "1.14.1.68", imports = listOf("KERNEL32.dll", "binkw32.dll"))
        val pe = PeInfo.read(exe)!!
        assertTrue(pe.isX86)
        assertEquals("1.14.1.68", pe.version)
        assertEquals(listOf("KERNEL32.dll", "binkw32.dll"), Dependencies.imports(exe))
        assertEquals(listOf("binkw32.dll"), Dependencies.missing(exe))
        File(tmp.root, "binkw32.dll").writeBytes(ByteArray(8))
        assertEquals(emptyList<String>(), Dependencies.missing(exe))
        val x64 = Fixtures.pe(tmp.newFile("SC2_x64.exe"), "3.0.5.39117", PeInfo.MACHINE_AMD64, listOf("d3d9.dll"))
        assertEquals("3.0.5.39117", PeInfo.read(x64)!!.version)
        assertTrue(PeInfo.read(x64)!!.isX64)
        assertEquals(emptyList<String>(), Dependencies.missing(x64))
        assertNull(PeInfo.read(tmp.newFile("notes.txt").apply { writeText("hello") }))
    }

    /**
     * The same readers on the real programs, when the person running the tests points BLIZZ_REAL_GAMES
     * at installations they have (Diablo II/Game.exe, StarCraft/StarCraft.exe). Skipped otherwise.
     */
    @Test fun realProgramsWhenAvailable() {
        val root = System.getenv("BLIZZ_REAL_GAMES")?.let(::File)
        assumeTrue(root != null && root.isDirectory)
        File(root, "d2/Game.exe").takeIf { it.isFile }?.let {
            assertEquals("1.14.1.68", PeInfo.read(it)!!.version)
            assertEquals(emptyList<String>(), Dependencies.missing(it))
            val v = Diablo2ClassicImporter().validateDir(it.parentFile!!)
            assertTrue(v.checks.filter { c -> !c.passed }.toString(), v.filesOk)
        }
        File(root, "sc3/StarCraft.exe").takeIf { it.isFile }?.let {
            assertEquals("1.15.2.1", PeInfo.read(it)!!.version)
            assertEquals(emptyList<String>(), Dependencies.missing(it))
            val v = StarCraftClassicImporter().validateDir(it.parentFile!!)
            assertTrue(v.checks.filter { c -> !c.passed }.toString(), v.filesOk)
            // Blizzard's own StarDat.mpq holds the file StarCraft opens first.
            assertEquals(true, MpqContents.has(File(it.parentFile, "StarDat.mpq"), listOf("font\\font.gid"))!!["font\\font.gid"])
        }
    }

    @Test fun legacyProgress() {
        val p = LegacyDownloader.parse("D2DV", "  1975/5003 pieces")!!
        assertEquals(1975L, p.done)
        assertEquals(5003L, p.total)
        assertEquals(Stage.ASSEMBLING, LegacyDownloader.parse("STAR", "installing 294 operations from 2 archive(s) -> ./sc")!!.stage)
        assertNull(LegacyDownloader.parse("STAR", "the game is in ./sc"))
    }

    @Test fun loopbackResolverAnswersNamesOnly() {
        LoopbackResolver { name -> if (name == "downloader.battle.net") listOf("23.195.81.59", "23.195.81.82") else emptyList() }.use { r ->
            fun ask(q: String) = Socket("127.0.0.1", r.port).use { s ->
                s.getOutputStream().write("$q\n".toByteArray())
                s.shutdownOutput()
                s.getInputStream().bufferedReader().readLines()
            }
            assertEquals(listOf("23.195.81.59", "23.195.81.82"), ask("downloader.battle.net"))
            assertEquals(emptyList<String>(), ask("bad name; rm -rf"))
        }
    }

    @Test fun devilutionxsWindowsAsset() {
        val json = """{"tag_name":"1.5.4","assets":[
            {"name":"devilutionx-windows-x86.zip","browser_download_url":"u1","size":1,"digest":"sha256:aa"},
            {"name":"devilutionx-windows-xp-32bit.zip","browser_download_url":"u2","size":2},
            {"name":"devilutionx-windows-x86_64.zip","browser_download_url":"u3","size":3,"digest":"sha256:bb"},
            {"name":"devilutionx-linux-x86_64.appimage","browser_download_url":"u4","size":4}]}"""
        val assets = GitHubReleases.parse(json)
        val chosen = Diablo1DevilutionXImporter.pickAsset(assets)!!
        assertEquals("devilutionx-windows-x86_64.zip", chosen.name)
        assertEquals("bb", chosen.sha256)
        assertEquals("1.5.4", chosen.release)
    }

    @Test fun discImages() {
        val data = Fixtures.installExe(tmp.newFile("INSTALL.EXE")).readBytes()
        val iso = Iso9660(Fixtures.iso(tmp.newFile("sc.iso"), "STARCRAFT", mapOf("INSTALL.EXE" to data, "README.TXT" to "hi".toByteArray())))
        assertEquals(listOf("INSTALL.EXE", "README.TXT"), iso.root().map { it.name })
        val entry = assertNotNullAndGet(iso.find("install.exe"))
        assertTrue(iso.open(entry).use { it.readBytes() }.contentEquals(data))
    }

    private fun <T> assertNotNullAndGet(value: T?): T {
        assertNotNull(value)
        return value!!
    }

    @Test fun safePaths() {
        val root = tmp.newFolder("out")
        assertEquals(File(root, "a/b.txt").canonicalPath, SafePaths.resolve(root, "a/b.txt").canonicalPath)
        for (bad in listOf("../x", "a/../../x", "/../x", "C:\\x", "a\\..\\..\\x")) {
            try {
                SafePaths.resolve(root, bad)
                throw AssertionError("accepted $bad")
            } catch (e: ImportException) {
                assertEquals(Problem.CORRUPT_ARCHIVE, e.problem)
            }
        }
    }
}
