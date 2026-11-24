package com.logie.blizz.importer

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File
import java.io.RandomAccessFile

class Warcraft2DiscTest {
    @get:Rule val tmp = TemporaryFolder()

    @Test fun aBinWithABootSignatureButMissingSectorsIsRejected() {
        val dir = tmp.newFolder()
        val cue = File(dir, "disc.cue").apply {
            writeText("FILE \"track-1.bin\" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n")
        }
        RandomAccessFile(File(dir, "track-1.bin"), "rw").use { track ->
            track.setLength(32L * 2352)
            val volume = 16L * 2352 + 24
            track.seek(volume)
            track.write(byteArrayOf(1, 67, 68, 48, 48, 49))
            track.seek(volume + 80)
            track.writeInt(Integer.reverseBytes(32))
            track.writeInt(32)

            assertTrue(Warcraft2Ps1Importer.isCompleteDisc(cue))
            track.setLength(31L * 2352)
            assertFalse(Warcraft2Ps1Importer.isCompleteDisc(cue))
        }
    }
}
