package com.logie.blizz.forever

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import java.nio.file.Files

class WineMonoTest {
    @Test
    fun `entryTarget refuses escaping names and keeps safe ones`() {
        val base = Files.createTempDirectory("mono").toFile()
        assertEquals(File(base, "mono-2.0/lib/mono/4.5/mscorlib.dll"), WineMono.entryTarget(base, "mono-2.0/lib/mono/4.5/mscorlib.dll"))
        assertEquals(File(base, "a"), WineMono.entryTarget(base, "./a"))
        assertNull(WineMono.entryTarget(base, "/etc/passwd"))
        assertNull(WineMono.entryTarget(base, "../escape"))
        assertNull(WineMono.entryTarget(base, "mono-2.0/../../escape"))
        assertNull(WineMono.entryTarget(base, ""))
    }

    @Test
    fun `monoEntryRel strips the top mono folder and skips the rest`() {
        assertEquals("mono-2.0/lib/mono/4.5/mscorlib.dll", WineMono.monoEntryRel("mono/mono-2.0/lib/mono/4.5/mscorlib.dll"))
        assertEquals("mono-2.0/lib/mono/4.5/mscorlib.dll", WineMono.monoEntryRel("./mono/mono-2.0/lib/mono/4.5/mscorlib.dll"))
        // The top folder entry itself produces nothing to write.
        assertNull(WineMono.monoEntryRel("mono"))
        assertNull(WineMono.monoEntryRel("mono/"))
        // Anything not under the archive's mono/ top, or escaping, is skipped.
        assertNull(WineMono.monoEntryRel("other/file"))
        assertNull(WineMono.monoEntryRel("mono/../escape"))
    }

    @Test
    fun `installed is false without the marker and true once the tree and marker are in place`() {
        val driveC = Files.createTempDirectory("drivec").toFile()
        assertFalse(WineMono.installed(driveC))
        val mono = File(driveC, "windows/mono")
        File(mono, "mono-2.0").mkdirs()
        // The tree alone is not enough: the marker is written only after a complete unpack.
        assertFalse(WineMono.installed(driveC))
        File(mono, ".blizz-wine-mono").writeText("abc123")
        assertTrue(WineMono.installed(driveC))
    }

    @Test
    fun `remove clears the tree and its staging so installed is false again`() {
        val driveC = Files.createTempDirectory("drivec").toFile()
        val mono = File(driveC, "windows/mono")
        File(mono, "mono-2.0").mkdirs(); File(mono, ".blizz-wine-mono").writeText("sha")
        File(driveC, "windows/mono.new/x").mkdirs()
        File(driveC, "windows/mono.old/x").mkdirs()
        assertTrue(WineMono.installed(driveC))
        WineMono.remove(driveC)
        assertFalse(WineMono.installed(driveC))
        assertFalse(File(driveC, "windows/mono").exists())
        assertFalse(File(driveC, "windows/mono.new").exists())
        assertFalse(File(driveC, "windows/mono.old").exists())
    }
}
