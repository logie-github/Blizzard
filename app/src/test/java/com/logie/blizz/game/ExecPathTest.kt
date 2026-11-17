package com.logie.blizz.game

import com.winlator.container.Container
import com.winlator.core.FileUtils
import com.winlator.core.WineUtils
import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

/**
 * Winlator turns exec_path into a Windows path and takes the file name after its last backslash.
 * The program's path alone comes out right; with DevilutionX's arguments in it, it named "diablo"
 * as the file ("File not found."), which is why they go in exec_args (patches/winlator/0005).
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class ExecPathTest {
    private val container = Container(0).apply { setDrives("D:/data/user/0/com.logie.blizz/files/gamesS:/data/user/0/com.logie.blizz/files/saves") }

    @Test fun theProgramsPathAlone() {
        val dos = WineUtils.unixToDOSPath("/data/user/0/com.logie.blizz/files/games/diablo/devilutionx.exe", container)
        assertEquals("D:\\diablo\\devilutionx.exe", dos)
        assertEquals("devilutionx.exe", FileUtils.getName(dos))
        assertEquals("D:\\diablo", FileUtils.getDirname(dos))
    }

    /** World of Warcraft: Forever's game is in the realms' folder, which has a drive of its own ([WindowsRuntime.drivesOf]). */
    @Test fun foreversProgramHasAWindowsPath() {
        val files = "/data/user/0/com.logie.blizz/files"
        val program = "$files/realms/forever-v2/client/_forever_/foreverkey.exe"
        // without the drive (as it was): no drive letter, no folder; Winlator starts nothing and shows its file manager
        assertEquals("", FileUtils.getDirname(WineUtils.unixToDOSPath(program, container)).substringBefore('\\').filter { it == ':' })
        val withRealms = Container(0).apply { setDrives(WindowsRuntime.drivesOf("$files/games", "$files/saves", "$files/staging", "$files/realms")) }
        val dos = WineUtils.unixToDOSPath(program, withRealms)
        assertEquals("F:\\forever-v2\\client\\_forever_\\foreverkey.exe", dos)
        assertEquals("F:\\forever-v2\\client\\_forever_", FileUtils.getDirname(dos))
        // the games stay where they were
        assertEquals("D:\\diablo\\devilutionx.exe", WineUtils.unixToDOSPath("$files/games/diablo/devilutionx.exe", withRealms))
    }

    @Test fun argumentsInThePathBrokeIt() {
        val dos = WineUtils.unixToDOSPath("/data/user/0/com.logie.blizz/files/games/diablo/devilutionx.exe --save-dir S:\\diablo", container)
        assertEquals("diablo", FileUtils.getName(dos))
    }
}
