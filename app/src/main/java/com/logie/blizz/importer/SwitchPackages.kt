package com.logie.blizz.importer

import java.io.File
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.security.MessageDigest

/**
 * Reading Nintendo Switch game packages the way D2R Mobile's own `extract_game.sh` does (the steps
 * are the same, run here on the phone with hactool): title keys out of the tickets in an eShop-style
 * .nsp, telling the base game's program content from the update's by what hactool says of each, and
 * checking the three program files are those of Diablo II: Resurrected 1.0.34.0 (PC 3.3.94012).
 * Plain Kotlin, unit-tested.
 */
object SwitchPackages {
    /** Diablo II: Resurrected's title id, as hactool prints it. */
    const val TITLE_ID = "0100726014352000"
    const val PATCH_ID = "0100726014352800"

    /** The version the port is made for: the SHA-256 of each ExeFS program file (3.3.94012). */
    val EXEFS_SHA256 = mapOf(
        "main" to "55fd909bb7230b002357e5b0d8499c11f06888f345c49e69eb4734df44a27d0e",
        "sdk" to "1c9f198a91c0bcfee5cf8f5b53fb941895e91334dfb766ce79fc68576797f017",
        "subsdk0" to "67a38fcf89cd13e040a021eb3d157072f38ebf6680a907874c35c7b231b5d4e2",
    )

    /** The 18 resource archives of RomFS/data the game reads at run time, and the files beside them it needs. */
    val ARCHIVES: List<String> = listOf(
        "00-00000001", "00-00000002", "00-00000003", "00-00000004", "00-00000005", "00-00000006",
        "01-00000001", "01-00000002", "02-00000001", "02-00000002", "03-00000001", "03-00000002",
        "04-00000001", "04-00000002", "05-00000001", "05-00000002", "17-00000001", "17-00000002",
    ).map { "$it.data" }
    const val BUILD_CONFIG = ".build.config"
    const val MANIFEST = "build_manifest.psv"

    /** Files of RomFS/data worth keeping: the archives, their `.holes`, the build config and the manifest. */
    fun keep(name: String): Boolean {
        val n = name.lowercase()
        return ARCHIVES.any { n == it || n == "$it.holes" } || n == BUILD_CONFIG || n == "build.config" || n == MANIFEST
    }

    private val KEY_LINE = Regex("^\\s*([A-Za-z0-9_]+)\\s*=\\s*([0-9A-Fa-f]+)\\s*$")

    /**
     * [text] (a prod.keys) with only the lines hactool takes: `name = <32 or 64 hex digits>`. Newer dumps hold keys of
     * other lengths, and hactool stops at the first ("Key (...) must be 32 hex digits!"). Returns the lines kept and the
     * names of the ones left out (never their values).
     */
    fun cleanKeys(text: String): Pair<String, List<String>> {
        val kept = StringBuilder()
        val dropped = ArrayList<String>()
        for (line in text.lines()) {
            val m = KEY_LINE.matchEntire(line) ?: continue
            val (name, value) = m.destructured
            if (value.length == 32 || value.length == 64) kept.append(name).append(" = ").append(value).append('\n') else dropped += name
        }
        return kept.toString() to dropped
    }

    data class TitleKey(val rightsId: String, val key: String)

    enum class TicketKind { COMMON, PERSONALIZED, UNKNOWN }

    private fun hex(b: ByteArray, from: Int, n: Int) = (from until from + n).joinToString("") { "%02x".format(b[it]) }

    /** What kind of ticket [tik] is (a personalized one is tied to the console it came from and holds no usable key). */
    fun ticketKind(tik: ByteArray): TicketKind {
        val base = dataStart(tik) ?: return TicketKind.UNKNOWN
        if (tik.size < base + 0x170) return TicketKind.UNKNOWN
        return if (tik[base + 0x141].toInt() == 0) TicketKind.COMMON else TicketKind.PERSONALIZED
    }

    private fun dataStart(tik: ByteArray): Int? {
        if (tik.size < 4) return null
        return when (ByteBuffer.wrap(tik, 0, 4).order(ByteOrder.LITTLE_ENDIAN).int) {
            0x00010000, 0x00010003 -> 0x240 // RSA-4096 signature
            0x00010001, 0x00010004 -> 0x140 // RSA-2048
            0x00010002, 0x00010005 -> 0x80 // ECDSA
            else -> null
        }
    }

    /** The title key in a common ticket: key at +0x40, rights id at +0x160 (from the start of the ticket's data). */
    fun titleKey(tik: ByteArray): TitleKey? {
        if (ticketKind(tik) != TicketKind.COMMON) return null
        val base = dataStart(tik)!!
        return TitleKey(hex(tik, base + 0x160, 16), hex(tik, base + 0x40, 16))
    }

    /** hactool's own title-keys file format. */
    fun titleKeysLine(k: TitleKey) = "${k.rightsId} = ${k.key}"

    enum class Content { BASE, UPDATE, OTHER }

    /** Whether the content file [hactool] described (`-t nca`) is this game's base program or its update's (a BKTR patch). */
    fun classify(hactoolOutput: String): Content {
        if (!Regex("Content Type:\\s*Program").containsMatchIn(hactoolOutput)) return Content.OTHER
        // The game's own id; an update's program content may name the patch's (the same with 800 at its end).
        if (!Regex("^Title ID:\\s*(?:$TITLE_ID|$PATCH_ID)", setOf(RegexOption.MULTILINE, RegexOption.IGNORE_CASE)).containsMatchIn(hactoolOutput)) return Content.OTHER
        return if (hactoolOutput.contains("BKTR") || hactoolOutput.contains("Patch RomFS", ignoreCase = true)) Content.UPDATE else Content.BASE
    }

    fun sha256(file: File): String {
        val md = MessageDigest.getInstance("SHA-256")
        file.inputStream().use { input ->
            val buffer = ByteArray(1 shl 16)
            while (true) {
                val n = input.read(buffer)
                if (n < 0) break
                md.update(buffer, 0, n)
            }
        }
        return md.digest().joinToString("") { "%02x".format(it) }
    }

    /** One check per ExeFS program file: is it the 3.3.94012 one. */
    fun exefsChecks(exefs: File): List<Check> = EXEFS_SHA256.map { (name, want) ->
        val f = File(exefs, name)
        when {
            !f.isFile -> Check("ExeFS/$name", false, "missing")
            sha256(f) == want -> Check("ExeFS/$name", true, "3.3.94012")
            else -> Check("ExeFS/$name", false, "not the 3.3.94012 version")
        }
    }
}
