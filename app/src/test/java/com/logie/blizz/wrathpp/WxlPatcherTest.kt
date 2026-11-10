package com.logie.blizz.wrathpp

import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import java.io.IOException
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.security.MessageDigest

/**
 * The Kotlin patcher against WarcraftXL's own: [synthetic] (a small 32-bit image with one import) patched by
 * WarcraftXL-Labs/core's PeImage.cpp and wxl-core-patcher's steps (built natively for the check, 2026-11-10) has the
 * SHA-256 [REFERENCE]; the Kotlin patcher must write the same bytes.
 */
class WxlPatcherTest {
    companion object {
        const val REFERENCE = "9b504c7da910e973ecb2d8644de67983bc236f0ec6ae9b56646c96d7b7cab311"
    }

    /** A 32-bit PE: headers 0x400 (room for more sections), .text with a `ret`, .idata importing KERNEL32!ExitProcess. */
    private fun synthetic(): ByteArray {
        val b = ByteBuffer.allocate(0x800).order(ByteOrder.LITTLE_ENDIAN)
        b.putShort(0, 0x5A4D); b.putInt(0x3C, 0x80)
        val nt = 0x80
        b.putInt(nt, 0x00004550)
        b.putShort(nt + 4, 0x14C); b.putShort(nt + 6, 2); b.putShort(nt + 20, 224); b.putShort(nt + 22, 0x0102)
        val o = nt + 24
        b.putShort(o, 0x10b); b.putInt(o + 16, 0x1000); b.putInt(o + 28, 0x400000); b.putInt(o + 32, 0x1000); b.putInt(o + 36, 0x200)
        b.putShort(o + 40, 5); b.putShort(o + 48, 5); b.putInt(o + 56, 0x3000); b.putInt(o + 60, 0x400); b.putShort(o + 68, 3)
        b.putInt(o + 92, 16)
        b.putInt(o + 96 + 8, 0x2000); b.putInt(o + 96 + 12, 40)       // the import directory: one descriptor and its end
        val s = o + 224
        fun section(at: Int, name: String, vsize: Int, va: Int, raw: Int, ptr: Int, ch: Int) {
            name.toByteArray().copyInto(b.array(), at)
            b.putInt(at + 8, vsize); b.putInt(at + 12, va); b.putInt(at + 16, raw); b.putInt(at + 20, ptr); b.putInt(at + 36, ch)
        }
        section(s, ".text", 0x10, 0x1000, 0x200, 0x400, 0x60000020)
        section(s + 40, ".idata", 0x80, 0x2000, 0x200, 0x600, 0xC0000040.toInt())
        b.put(0x400, 0xC3.toByte())
        // .idata at file 0x600 = rva 0x2000: descriptor (INT 0x2030, name 0x2050, IAT 0x2038), thunks, hint/name, dll name
        b.putInt(0x600, 0x2030); b.putInt(0x600 + 12, 0x2050); b.putInt(0x600 + 16, 0x2038)
        b.putInt(0x630, 0x2040); b.putInt(0x638, 0x2040)
        "ExitProcess".toByteArray().copyInto(b.array(), 0x642)
        "KERNEL32.dll".toByteArray().copyInto(b.array(), 0x650)
        return b.array()
    }

    private fun sha(bytes: ByteArray) = MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }

    @Test fun theSameBytesAsWarcraftXLsOwnPatcher() {
        System.getenv("WXL_DUMP")?.let { File(it).writeBytes(synthetic()) }
        val (out, result) = WxlPatcher.patch(synthetic())
        assertEquals(WxlPatcher.Result.PATCHED, result)
        assertEquals(REFERENCE, sha(out))
    }

    @Test fun patchingTwiceChangesNothingMore() {
        val (once, _) = WxlPatcher.patch(synthetic())
        val (twice, result) = WxlPatcher.patch(once)
        assertEquals(WxlPatcher.Result.ALREADY, result)
        assertArrayEquals(once, twice)
    }

    @Test fun theTrampolineCallsTheEntryImportThenTheOldEntryPoint() {
        val (out, _) = WxlPatcher.patch(synthetic())
        val pe = WxlPatcher.Image(out)
        assertTrue(pe.hasSection(".wxl") && pe.hasSection(".wxle"))
        assertTrue(pe.u16(pe.nt + 4 + 18) and 0x20 != 0)                  // large address aware
        val cave = pe.entryPointVa
        val at = pe.vaToOffset(cave)
        assertEquals(0xE8, out[at].toInt() and 0xFF)
        val rel = ByteBuffer.wrap(out, at + 15, 4).order(ByteOrder.LITTLE_ENDIAN).int
        assertEquals(0x401000, cave + 19 + rel)                          // then the original entry point
    }

    @Test fun anythingButA32BitPeIsRefused() {
        try { WxlPatcher.patch(ByteArray(100)); throw AssertionError("not refused") } catch (_: IOException) { }
    }
}

/** The add-on's pure parts: its zip, the creator's table of contents. */
class WrathppAddonTest {
    @Test fun theTocGetsTheCreatorLastAndLosesOtherRealmsModules() {
        val original = "GlueStrings.lua\r\n## comment\r\nCharacterCreate.xml\r\n\r\nAlliedRacesCreate.xml\r\nAlliedRacesCreate.lua\r\n"
        val toc = WrathppAddon.toc(original, listOf("WrathppCreate.lua")) { it.endsWith("GlueStrings.lua") || it.endsWith("CharacterCreate.xml") }
        assertEquals("GlueStrings.lua\r\n## comment\r\nCharacterCreate.xml\r\nWrathppCreate.lua\r\n", toc)
        // Made again from its own output: the same.
        assertEquals(toc, WrathppAddon.toc(toc, listOf("WrathppCreate.lua")) { !it.endsWith("WrathppCreate.lua") })
    }

    @Test fun theZipsPathsStayInside() {
        fun zip(vararg names: String): ByteArray {
            val out = java.io.ByteArrayOutputStream()
            java.util.zip.ZipOutputStream(out).use { z -> for (n in names) { z.putNextEntry(java.util.zip.ZipEntry(n)); z.write(n.toByteArray()); z.closeEntry() } }
            return out.toByteArray()
        }
        val files = WrathppAddon.unzip(zip("wrathpp-client-addon/WarcraftXL.dll", "wrathpp-client-addon/Mods/wxl.lua/mod.json"))
        assertEquals(setOf("WarcraftXL.dll", "Mods/wxl.lua/mod.json"), files.keys)
        for (bad in listOf("wrathpp-client-addon/../x", "/etc/x", "wrathpp-client-addon/Mods/../../x")) {
            try { WrathppAddon.unzip(zip(bad)); throw AssertionError("not refused: $bad") } catch (_: IOException) { }
        }
    }
}
