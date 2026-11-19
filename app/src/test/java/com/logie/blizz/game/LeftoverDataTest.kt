package com.logie.blizz.game

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

class LeftoverDataTest {
    @get:Rule val tmp = TemporaryFolder()

    private val pem = "-----BEGIN CERTIFICATE-----\nAAECAwQFBgcICQ==\n-----END CERTIFICATE-----\n"

    @Test fun foreversDataGoesAndNothingElseDoes() {
        val files = tmp.newFolder("files")
        // Forever's own
        File(files, "realms/forever-v2/client/Data/data").mkdirs(); File(files, "realms/forever-v2/client/Data/data/data.000").writeBytes(ByteArray(5000))
        File(files, "realms/forever-v2/server/data/maps").mkdirs(); File(files, "realms/forever-v2/server/data/maps/a.map").writeBytes(ByteArray(3000))
        File(files, "realms/forever-v2/keys").mkdirs(); File(files, "realms/forever-v2/keys/forever-root-ca.cert.pem").writeText(pem)
        File(files, "realms/forever-v2/run").mkdirs()
        File(files, "realms/forever-v2/run/mariadbd.pid").writeText("4321\n"); File(files, "realms/forever-v2/run/old.pid").writeText("77\n")
        File(files, "forever/client").mkdirs(); File(files, "imagefs/usr").mkdirs(); File(files, "forever-arm64").mkdirs()
        // other games'
        File(files, "games/diablo").mkdirs(); File(files, "games/diablo/d.exe").writeText("d")
        File(files, "realms/wrathpp").mkdirs(); File(files, "realms/wrathpp/keep").writeText("k")
        File(files, "wow/data").mkdirs()
        val container = tmp.newFolder("container")
        File(container, ".wine/drive_c/windows").mkdirs()
        File(container, ".wine/drive_c/windows/foreverkey.log").writeText("x"); File(container, ".wine/drive_c/windows/borderless.log").writeText("y")
        val print = LeftoverData.thumbprint(pem)!!
        assertEquals(40, print.length)
        val other = "[Software\\\\Microsoft\\\\SystemCertificates\\\\Root\\\\Certificates\\\\0123456789ABCDEF0123456789ABCDEF01234567] 1\n\"Blob\"=hex:01,02\n"
        val ours = "\n[Software\\\\Microsoft\\\\SystemCertificates\\\\Root\\\\Certificates\\\\$print] 2\n\"Blob\"=hex:20,00,\\\n  01,02\n" +
            "\n[Software\\\\Wow6432Node\\\\Microsoft\\\\SystemCertificates\\\\Root\\\\Certificates\\\\$print] 2\n\"Blob\"=hex:20,00\n"
        val tail = "\n[Software\\\\Wine\\\\Fonts] 3\n\"x\"=\"y\"\n"
        File(container, ".wine/system.reg").writeText("WINE REGISTRY Version 2\n\n$other$ours$tail")

        // only a process that is Forever's own is ended (a pid file can name a number another program has since taken)
        assertEquals(listOf(4321), LeftoverData.leftoverPids(files) { pid -> if (pid == 4321) "/data/x/files/realms/forever-v2/server/bin/mariadbd --defaults" else "com.other.app" })

        val killed = ArrayList<Int>()
        val result = LeftoverData.wipe(files, listOf(container)) { killed += it }!!
        assertTrue(result.bytes >= 8000)
        assertEquals(2, result.certificates)
        for (gone in LeftoverData.FOLDERS) assertFalse(gone, File(files, gone).exists())
        assertFalse(File(container, ".wine/drive_c/windows/foreverkey.log").exists())
        assertTrue(File(files, "games/diablo/d.exe").isFile); assertTrue(File(files, "realms/wrathpp/keep").isFile); assertTrue(File(files, "wow/data").isDirectory)
        assertTrue(File(container, ".wine/drive_c/windows/borderless.log").isFile)
        assertEquals("WINE REGISTRY Version 2\n\n$other$tail", File(container, ".wine/system.reg").readText())
        // a second start: nothing to do
        assertNull(LeftoverData.wipe(files, listOf(container)) { killed += it })
    }

    @Test fun aRegistryWithoutTheCertificateIsLeftAsItIs() {
        val reg = "WINE REGISTRY Version 2\n\n[Software\\\\Wine] 1\n\"a\"=\"b\"\n"
        assertEquals(reg to 0, LeftoverData.withoutCertificate(reg, "0000000000000000000000000000000000000000"))
    }
}
