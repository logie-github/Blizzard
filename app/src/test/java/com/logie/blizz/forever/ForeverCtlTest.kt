package com.logie.blizz.forever

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import java.nio.file.Files

class ForeverCtlTest {
    private val layout = ForeverLayout(File("/data/data/com.logie.blizz/files/forever"))

    @Test
    fun `ctl runs the shipped script with FILES pointing at the realm folder`() {
        val command = ForeverCtl.command(layout, "worldserver")
        assertEquals(
            listOf("/system/bin/sh", "/data/data/com.logie.blizz/files/forever/server/ctl.sh", "worldserver"),
            command.argv,
        )
        assertEquals("/data/data/com.logie.blizz/files/forever", command.env["FILES"])
        assertEquals(layout.run, command.directory)
    }

    @Test
    fun `an account command passes the name and password`() {
        assertEquals(
            listOf("/system/bin/sh", "${layout.server.path}/ctl.sh", "account", "me@example.com", "secret"),
            ForeverCtl.command(layout, "account", "me@example.com", "secret").argv,
        )
    }

    @Test
    fun `makeExecutable sets the bit on the programs, the loader and ctl`() {
        val dir = Files.createTempDirectory("forever").toFile()
        val l = ForeverLayout(dir)
        File(l.server, "bin").mkdirs(); File(l.server, "lib").mkdirs()
        val files = listOf(l.ctl, File(l.server, "bin/worldserver"), File(l.server, "lib/ld-musl-aarch64.so.1"))
        files.forEach { it.writeText("x"); it.setExecutable(false, false) }
        assertEquals(3, ForeverCtl.makeExecutable(l))
        assertTrue(files.all { it.canExecute() })
        // Idempotent.
        assertEquals(0, ForeverCtl.makeExecutable(l))
    }

    @Test
    fun `a tar entry can't escape the folder`() {
        val base = File("/tmp/x")
        assertEquals(File(base, "server/bin/worldserver"), ForeverServerPackage.entryTarget(base, "./server/bin/worldserver"))
        assertNull(ForeverServerPackage.entryTarget(base, "../escape"))
        assertNull(ForeverServerPackage.entryTarget(base, "/etc/passwd"))
        assertNull(ForeverServerPackage.entryTarget(base, "server/../../x"))
    }
}
