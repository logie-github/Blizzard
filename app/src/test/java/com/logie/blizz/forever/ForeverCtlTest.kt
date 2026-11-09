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

    private val buildInfo = """
        Branch!STRING:0|Active!DEC:1|Build Key!HEX:16|CDN Key!HEX:16|Version!STRING:0|Product!STRING:0
        us|0|aa|bb|1.15.7.70790|wowf
        eu|1|cc|dd|1.15.8.70862|wowf
        us|1|ee|ff|1.15.8.99999|wow_classic_era
    """.trimIndent()

    @Test
    fun `the client build is the active Forever row's`() {
        assertEquals(70862, ForeverCtl.clientBuild(buildInfo))
    }

    @Test
    fun `without an active Forever row any Forever row is used, then the first row`() {
        val noActive = buildInfo.replace("eu|1|", "eu|0|")
        assertEquals(70790, ForeverCtl.clientBuild(noActive))
        val other = "Version!STRING:0|Product!STRING:0\n1.2.3.12345|wow"
        assertEquals(12345, ForeverCtl.clientBuild(other))
    }

    @Test
    fun `an unreadable build info gives no build`() {
        assertNull(ForeverCtl.clientBuild(""))
        assertNull(ForeverCtl.clientBuild("Branch!STRING:0|Product!STRING:0\nus|wowf"))
        assertNull(ForeverCtl.clientBuild("Version!STRING:0\nnot-a-version"))
    }

    /** A folder tree for findClient: name -> children (a leaf has none). */
    private class Node(val children: Map<String, Node> = emptyMap())
    private val listing: (Node) -> List<Pair<String, Node>> = { it.children.toList() }
    private val client = Node(mapOf(".build.info" to Node(), "Data" to Node(mapOf("data" to Node())), "_forever_" to Node(mapOf("Wow.exe" to Node()))))

    @Test
    fun `the picked folder is the client when it holds build info, Data and _forever_`() {
        assertEquals(emptyList<Node>(), ForeverCtl.findClient(client, listing))
    }

    @Test
    fun `a folder above the client finds it one level down`() {
        val above = Node(mapOf("notes.txt" to Node(), "World of Warcraft" to client))
        assertEquals(listOf(client), ForeverCtl.findClient(above, listing))
    }

    @Test
    fun `a folder that isn't the client (or only its _forever_ part) is refused`() {
        assertNull(ForeverCtl.findClient(Node(mapOf("Wow.exe" to Node())), listing))
        assertNull(ForeverCtl.findClient(client.children.getValue("_forever_"), listing))
        assertNull(ForeverCtl.findClient(Node(mapOf(".build.info" to Node(), "_forever_" to Node())), listing))
    }
}
