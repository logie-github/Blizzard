package com.logie.blizz.wrathpp

import java.io.File
import java.io.IOException
import java.nio.ByteBuffer
import java.nio.ByteOrder

/**
 * WarcraftXL's `wxl-core-patcher` (WarcraftXL-Labs/core `src/patcher`, MIT) in Kotlin, so the app can make Wrath++'s copy
 * of the 32-bit `Wow.exe` load WarcraftXL's runtime on the phone without running a Windows program: the image made
 * large-address-aware, `WarcraftXL.dll!WarcraftXL` and `!WarcraftXLEntry` imported through a new `.wxl` section, and a
 * 19-byte entry trampoline (`.wxle`) that calls `WarcraftXLEntry` and then the original entry point. The core at the
 * pinned commit registers no byte scripts, so that is all its patcher does. The same bytes as its own: the unit test
 * checks a synthetic image against the SHA-256 the C++ patcher wrote for it.
 *
 * Only ever used on Wrath++'s own copy (`client-wrathpp/WowWrathpp.exe`), never on the realms' game.
 */
object WxlPatcher {
    const val DLL = "WarcraftXL.dll"
    private const val ANCHOR = "WarcraftXL"
    private const val ENTRY = "WarcraftXLEntry"
    private const val IMPORT_SECTION = ".wxl"
    private const val ENTRY_SECTION = ".wxle"

    private const val SECTION_HEADER = 40
    private const val IMPORT_DESCRIPTOR = 20

    class Image(var bytes: ByteArray) {
        private fun buf() = ByteBuffer.wrap(bytes).order(ByteOrder.LITTLE_ENDIAN)
        fun u16(at: Int) = buf().getShort(at).toInt() and 0xFFFF
        fun u32(at: Int) = buf().getInt(at)
        fun put16(at: Int, v: Int) { buf().putShort(at, v.toShort()) }
        fun put32(at: Int, v: Int) { buf().putInt(at, v) }

        val nt get() = u32(0x3C)
        private val fileHeader get() = nt + 4
        private val optional get() = nt + 24
        val sections get() = u16(fileHeader + 2)
        private val firstSection get() = optional + u16(fileHeader + 16)
        fun section(i: Int) = firstSection + i * SECTION_HEADER
        val imageBase get() = u32(optional + 28)
        private val sectionAlignment get() = u32(optional + 32)
        private val fileAlignment get() = u32(optional + 36)
        private val sizeOfHeaders get() = u32(optional + 60)
        private fun dataDirectory(i: Int) = optional + 96 + i * 8

        fun valid(): Boolean {
            if (bytes.size < 64 || u16(0) != 0x5A4D) return false
            val nt = u32(0x3C)
            if (nt < 0 || nt.toLong() + 248 > bytes.size) return false
            return u32(nt) == 0x00004550 && u16(nt + 24) == 0x10b
        }

        fun hasSection(name: String): Boolean = (0 until sections).any { sectionName(it) == name }

        fun sectionName(i: Int): String {
            val at = section(i)
            val raw = bytes.copyOfRange(at, at + 8)
            val end = raw.indexOf(0).let { if (it < 0) 8 else it }
            return String(raw, 0, end, Charsets.ISO_8859_1)
        }

        fun vaToOffset(va: Int): Int {
            val rva = va - imageBase
            for (i in 0 until sections) {
                val s = section(i)
                val virtualSize = u32(s + 8); val virtualAddress = u32(s + 12); val rawSize = u32(s + 16); val rawPointer = u32(s + 20)
                val span = if (Integer.compareUnsigned(virtualSize, rawSize) > 0) virtualSize else rawSize
                if (Integer.compareUnsigned(rva, virtualAddress) >= 0 && Integer.compareUnsigned(rva, virtualAddress + span) < 0) {
                    return rva - virtualAddress + rawPointer
                }
            }
            return 0
        }

        fun writeVa(va: Int, data: ByteArray): Boolean {
            val off = vaToOffset(va)
            if (off == 0 || off.toLong() + data.size > bytes.size) return false
            System.arraycopy(data, 0, bytes, off, data.size)
            return true
        }

        fun setLargeAddressAware() { put16(fileHeader + 18, u16(fileHeader + 18) or 0x0020) }

        var entryPointVa: Int
            get() = imageBase + u32(optional + 16)
            set(va) { put32(optional + 16, va - imageBase) }

        private fun alignUp(v: Int, a: Int) = (v + a - 1) and (a - 1).inv()

        /** The next section's header slot, if it fits in the headers. */
        private fun newSectionHeader(): Int? {
            val at = section(sections)
            return if (at + SECTION_HEADER > sizeOfHeaders) null else at
        }

        private fun nameBytes(name: String) = ByteArray(8).also { name.toByteArray(Charsets.ISO_8859_1).copyInto(it, 0, 0, minOf(8, name.length)) }

        /** PeImage::AddImport: the existing descriptors and one more, in a new section; the IAT slots' addresses. */
        fun addImport(dll: String, funcs: List<String>, tag: String): IntArray? {
            if (funcs.isEmpty() || hasSection(tag)) return null
            val impRva = u32(dataDirectory(1))
            val impOff = vaToOffset(impRva + imageBase)
            if (impOff == 0 || impOff + IMPORT_DESCRIPTOR > bytes.size) return null
            var origCount = 0
            while (impOff + (origCount + 1) * IMPORT_DESCRIPTOR <= bytes.size &&
                (u32(impOff + origCount * IMPORT_DESCRIPTOR + 12) != 0 || u32(impOff + origCount * IMPORT_DESCRIPTOR + 16) != 0)) origCount++

            val count = funcs.size
            val thunkBytes = (count + 1) * 4
            val descBytes = (origCount + 2) * IMPORT_DESCRIPTOR
            val offInt = descBytes
            val offIat = offInt + thunkBytes
            val offIbn = offIat + thunkBytes
            val ibnBytes = funcs.sumOf { alignUp(2 + it.length + 1, 2) }
            val offDll = offIbn + ibnBytes
            val blobSize = offDll + dll.length + 1
            val blob = ByteArray(blobSize)
            val b = ByteBuffer.wrap(blob).order(ByteOrder.LITTLE_ENDIAN)

            val last = section(sections - 1)
            val secRva = alignUp(u32(last + 12) + u32(last + 8), sectionAlignment)
            val secRaw = alignUp(bytes.size, fileAlignment)

            System.arraycopy(bytes, impOff, blob, 0, origCount * IMPORT_DESCRIPTOR)
            val d = origCount * IMPORT_DESCRIPTOR
            b.putInt(d, secRva + offInt); b.putInt(d + 4, 0); b.putInt(d + 8, 0); b.putInt(d + 12, secRva + offDll); b.putInt(d + 16, secRva + offIat)
            val iat = IntArray(count)
            var ibn = offIbn
            for (i in 0 until count) {
                b.putInt(offInt + i * 4, secRva + ibn)
                b.putInt(offIat + i * 4, secRva + ibn)
                funcs[i].toByteArray(Charsets.ISO_8859_1).copyInto(blob, ibn + 2)
                iat[i] = imageBase + secRva + offIat + i * 4
                ibn += alignUp(2 + funcs[i].length + 1, 2)
            }
            dll.toByteArray(Charsets.ISO_8859_1).copyInto(blob, offDll)

            val add = newSectionHeader() ?: return null
            java.util.Arrays.fill(bytes, add, add + SECTION_HEADER, 0)
            nameBytes(tag).copyInto(bytes, add)
            val rawSize = alignUp(blobSize, fileAlignment)
            put32(add + 8, blobSize); put32(add + 12, secRva); put32(add + 16, rawSize); put32(add + 20, secRaw)
            put32(add + 36, 0x00000040 or 0x40000000 or 0x80000000.toInt())
            put32(dataDirectory(1), secRva); put32(dataDirectory(1) + 4, descBytes)
            put32(dataDirectory(11), 0); put32(dataDirectory(11) + 4, 0)
            put32(optional + 56, alignUp(secRva + blobSize, sectionAlignment))
            put16(fileHeader + 2, sections + 1)
            grow(secRaw, blob, rawSize)
            return iat
        }

        /** PeImage::AppendCode: [code] in a new executable section; its address, or 0. */
        fun appendCode(code: ByteArray, tag: String): Int {
            val last = section(sections - 1)
            val secRva = alignUp(u32(last + 12) + u32(last + 8), sectionAlignment)
            val secRaw = alignUp(bytes.size, fileAlignment)
            val add = newSectionHeader() ?: return 0
            java.util.Arrays.fill(bytes, add, add + SECTION_HEADER, 0)
            nameBytes(tag).copyInto(bytes, add)
            val rawSize = alignUp(code.size, fileAlignment)
            put32(add + 8, code.size); put32(add + 12, secRva); put32(add + 16, rawSize); put32(add + 20, secRaw)
            put32(add + 36, 0x00000020 or 0x20000000 or 0x40000000)
            put32(optional + 56, alignUp(secRva + code.size, sectionAlignment))
            put16(fileHeader + 2, sections + 1)
            grow(secRaw, code, rawSize)
            return imageBase + secRva
        }

        /** The file padded with zeros to [at], then [data], then zeros to [rawSize] bytes of it. */
        private fun grow(at: Int, data: ByteArray, rawSize: Int) {
            val out = ByteArray(at + rawSize)
            System.arraycopy(bytes, 0, out, 0, minOf(bytes.size, at))
            System.arraycopy(data, 0, out, at, data.size)
            bytes = out
        }
    }

    /** What [patch] did. */
    enum class Result { PATCHED, ALREADY }

    /** Patches [bytes] (a 32-bit PE) as `wxl-core-patcher` does; returns the new bytes. Throws [IOException] for anything else. */
    fun patch(bytes: ByteArray): Pair<ByteArray, Result> {
        val pe = Image(bytes.copyOf())
        if (!pe.valid()) throw IOException("not a 32-bit PE")
        pe.setLargeAddressAware()
        if (pe.hasSection(IMPORT_SECTION) && pe.hasSection(ENTRY_SECTION)) return pe.bytes to Result.ALREADY
        if (pe.hasSection(IMPORT_SECTION)) throw IOException("an older WarcraftXL patch is in it (import only): not handled")
        val iat = pe.addImport(DLL, listOf(ANCHOR, ENTRY), IMPORT_SECTION) ?: throw IOException("the import couldn't be added")
        val oep = pe.entryPointVa
        val cave = byteArrayOf(0xE8.toByte(), 0, 0, 0, 0, 0x58, 0x8B.toByte(), 0x88.toByte(), 0, 0, 0, 0, 0xFF.toByte(), 0xD1.toByte(), 0xE9.toByte(), 0, 0, 0, 0)
        val caveVa = pe.appendCode(cave, ENTRY_SECTION)
        if (caveVa == 0) throw IOException("the entry trampoline couldn't be added")
        val disp = iat[1] - (caveVa + 5)
        val rel = oep - (caveVa + cave.size)
        ByteBuffer.wrap(cave).order(ByteOrder.LITTLE_ENDIAN).putInt(8, disp).putInt(15, rel)
        if (!pe.writeVa(caveVa, cave)) throw IOException("the entry trampoline couldn't be written")
        pe.entryPointVa = caveVa
        return pe.bytes to Result.PATCHED
    }

    /** [source] patched into [target] (written beside and renamed), [source] left as it is. */
    fun patchFile(source: File, target: File): Result {
        val (bytes, result) = patch(source.readBytes())
        val tmp = File(target.path + ".wxltmp")
        tmp.writeBytes(bytes)
        target.delete()
        if (!tmp.renameTo(target)) throw IOException("couldn't write ${target.path}")
        return result
    }
}
