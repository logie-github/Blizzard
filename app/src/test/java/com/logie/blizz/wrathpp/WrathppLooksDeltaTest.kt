package com.logie.blizz.wrathpp

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File
import java.io.IOException
import java.io.InputStream
import java.io.RandomAccessFile
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

/** A new looks release taken over the installed one with only what changed ([WrathppLooksDelta]), over a local zip standing for the release. */
class WrathppLooksDeltaTest {
    @get:Rule val tmp = TemporaryFolder()

    private val gameTable = DbcTable.hex("5744424304000000040000001000000009000000010000000a000000010000000000803f020000000a00000003000000000000400300000007000000050000000000404004000000070000000700000000008040006100620063006400")
    private val tables: (String) -> ByteArray? = { name -> if (name == "DBFilesClient\\CharSections.dbc") gameTable else null }

    private fun big(seed: Int) = (0 until 200_000).joinToString("") { ((it * seed + it / 13 * seed * seed) % 10).toString() }

    private fun zip(entries: Map<String, String>, storedNames: Set<String> = emptySet()): File = tmp.newFile().also { f ->
        ZipOutputStream(f.outputStream()).use { z ->
            for ((n, t) in entries) {
                val bytes = t.toByteArray()
                val e = ZipEntry(n)
                if (n in storedNames) {
                    e.method = ZipEntry.STORED; e.size = bytes.size.toLong(); e.compressedSize = bytes.size.toLong()
                    val crc = java.util.zip.CRC32().also { it.update(bytes) }; e.crc = crc.value
                }
                z.putNextEntry(e); z.write(bytes); z.closeEntry()
            }
        }
    }

    /** The release's bytes by ranges, counting what is served. */
    private class Served(val file: File) : WrathppLooksDelta.Ranges {
        var served = 0L
        override val length = file.length()
        override fun open(start: Long, endInclusive: Long): InputStream {
            val n = (minOf(endInclusive, length - 1) - start + 1).toInt()
            val b = ByteArray(n)
            RandomAccessFile(file, "r").use { it.seek(start); it.readFully(b) }
            served += n
            return b.inputStream()
        }
    }

    private fun setup(): Pair<File, File> {
        val client = tmp.newFolder("client-wrathpp")
        File(client, "Data").mkdirs()
        val server = tmp.newFolder("server-wrathpp")
        File(server, "share/mariadb").mkdirs()
        return client to server
    }

    private val change = "types\tiisf\nput\t7\t1\tseven\t0.5\n"

    private fun release(models: Map<String, String>, sections: String = "sections") = mapOf(
        "changes/CharSections.txt" to change, "dbc/CharSections.dbc" to sections, "dbc/CharHairGeosets.dbc" to "hair",
    ) + models.mapKeys { "client/${it.key}" }

    @Test fun onlyTheChangedFilesAreFetchedAndTheRestComesFromTheInstalledOnes() {
        val (client, server) = setup()
        val a = big(1); val b = big(2); val c = big(3)
        val v1 = zip(release(mapOf("Character/A.m2" to a, "Character/B.m2" to b, "Character/C.blp" to c)), storedNames = setOf("client/Character/C.blp"))
        WrathppLooks.install(client, server, v1, "one", tables = tables)
        // the next release: B changed, D is new, A and C are as they were; the tables changed too
        val b2 = big(9); val d = big(4)
        val v2 = zip(release(mapOf("Character/A.m2" to a, "Character/B.m2" to b2, "Character/C.blp" to c, "Character/D.m2" to d), "sections two"), storedNames = setOf("client/Character/C.blp"))
        val ranges = Served(v2)
        val done = WrathppLooksDelta.update(client, server, ranges, "two", File(tmp.root, "work"), { _, _ -> }, tables)
        assertTrue(done)
        val patch = File(client, "Data/patch-Z.MPQ")
        assertEquals(a, File(patch, "Character/A.m2").readText())
        assertEquals(b2, File(patch, "Character/B.m2").readText())
        assertEquals(c, File(patch, "Character/C.blp").readText())
        assertEquals(d, File(patch, "Character/D.m2").readText())
        assertEquals("sections two", File(server, "share/dbc/CharSections.dbc").readText())
        assertEquals("sections two", File(patch, "wrathpp-server-dbc/CharSections.dbc").readText())
        assertEquals("two", WrathppLooks.installedSha(client, server))
        assertEquals(5, DbcTable(File(patch, "DBFilesClient/CharSections.dbc").readBytes()).records.size)
        // far less than the zip itself came over (B and D, deflated and a little more, and the central directory)
        assertTrue("served ${ranges.served} of ${v2.length()}", ranges.served < v2.length() / 2)
        assertFalse(File(tmp.root, "work").exists())
    }

    @Test fun aFileInstalledWithOtherBytesIsFetchedAgain() {
        val (client, server) = setup()
        val a = big(1)
        WrathppLooks.install(client, server, zip(release(mapOf("Character/A.m2" to a, "Character/Z.m2" to big(5)))), "one", tables = tables)
        File(client, "Data/patch-Z.MPQ/Character/A.m2").writeText("edited since")
        val v2 = zip(release(mapOf("Character/A.m2" to a, "Character/Z.m2" to big(5))))
        assertTrue(WrathppLooksDelta.update(client, server, Served(v2), "two", File(tmp.root, "work"), { _, _ -> }, tables))
        assertEquals(a, File(client, "Data/patch-Z.MPQ/Character/A.m2").readText())
    }

    @Test fun nothingInstalledOrMostlyNewMeansTheWholeDownload() {
        val (client, server) = setup()
        val v = zip(release(mapOf("Character/A.m2" to big(1))))
        assertFalse(WrathppLooksDelta.update(client, server, Served(v), "one", File(tmp.root, "work"), { _, _ -> }, tables))
        WrathppLooks.install(client, server, v, "one", tables = tables)
        val all = zip(release(mapOf("Character/A.m2" to big(8), "Character/B.m2" to big(7))))
        assertFalse(WrathppLooksDelta.update(client, server, Served(all), "two", File(tmp.root, "work"), { _, _ -> }, tables))
        assertEquals("one", WrathppLooks.installedSha(client, server))
    }

    @Test fun aReleaseThatCantBeReadIsAnError() {
        val (client, server) = setup()
        val v = zip(release(mapOf("Character/A.m2" to big(1))))
        WrathppLooks.install(client, server, v, "one", tables = tables)
        val garbage = tmp.newFile().also { it.writeBytes(ByteArray(5000) { 3 }) }
        try { WrathppLooksDelta.update(client, server, Served(garbage), "two", File(tmp.root, "work"), { _, _ -> }, tables); fail("read garbage") } catch (_: IOException) {}
        assertEquals("one", WrathppLooks.installedSha(client, server))
    }
}
