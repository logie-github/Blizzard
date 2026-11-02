package com.logie.blizz.importer

import java.io.ByteArrayOutputStream
import java.io.File
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

/**
 * Stand-ins for the games' files, made by the tests: Windows programs with a version resource and
 * an import table, MPQ archives (their header and padding), zips and a disc image. None of them is
 * a game file: they're only shaped like ones, which is what the importers check.
 */
object Fixtures {
    /** A PE32 (or PE32+) program for [machine], file version [version], importing [imports]. */
    fun pe(file: File, version: String, machine: Int = PeInfo.MACHINE_I386, imports: List<String> = listOf("KERNEL32.dll", "USER32.dll")): File {
        val v = version.split('.').map { it.toInt() }
        val sectionRva = 0x1000
        val sectionRaw = 0x400
        val body = ByteBuffer.allocate(0x1000).order(ByteOrder.LITTLE_ENDIAN)
        // Import descriptors (20 bytes each, then a zero one), then the names.
        val namesAt = (imports.size + 1) * 20
        var nameOffset = namesAt
        imports.forEachIndexed { i, name ->
            body.position(i * 20 + 12)
            body.putInt(sectionRva + nameOffset)
            body.position(nameOffset)
            body.put(name.toByteArray(Charsets.US_ASCII)); body.put(0)
            nameOffset += name.length + 1
        }
        // The version resource's key and fixed info.
        var at = ((nameOffset + 64) / 4) * 4
        body.position(at)
        body.put("VS_VERSION_INFO".toByteArray(Charsets.UTF_16LE)); body.putShort(0)
        at = ((body.position() + 3) / 4) * 4
        body.position(at)
        body.putInt(0xFEEF04BD.toInt()); body.putInt(0x00010000)
        body.putInt((v[0] shl 16) or v[1]); body.putInt((v[2] shl 16) or v[3])

        val out = ByteBuffer.allocate(sectionRaw + body.capacity()).order(ByteOrder.LITTLE_ENDIAN)
        out.put(0, 'M'.code.toByte()); out.put(1, 'Z'.code.toByte())
        out.putInt(0x3c, 0x80)
        out.position(0x80)
        out.putInt(0x00004550)
        out.putShort(machine.toShort()); out.putShort(1) // one section
        out.putInt(0); out.putInt(0); out.putInt(0)
        val plus = machine == PeInfo.MACHINE_AMD64
        val optionalSize = if (plus) 0xF0 else 0xE0
        out.putShort(optionalSize.toShort()); out.putShort(0x0102)
        val optional = out.position()
        out.putShort((if (plus) 0x20b else 0x10b).toShort())
        val dirs = optional + if (plus) 112 else 96
        out.putInt(dirs + 8, sectionRva) // the import directory
        out.putInt(dirs + 12, namesAt)
        val table = optional + optionalSize
        out.position(table)
        out.put(".rdata\u0000\u0000".toByteArray(Charsets.US_ASCII))
        out.putInt(body.capacity()); out.putInt(sectionRva); out.putInt(body.capacity()); out.putInt(sectionRaw)
        out.position(sectionRaw)
        out.put(body.array())
        file.parentFile?.mkdirs()
        file.writeBytes(out.array())
        return file
    }

    /** An MPQ archive: its header, a hash table holding [names] (as the game's archives do), then padding. */
    fun mpq(file: File, names: List<String> = emptyList(), size: Int = 4096): File {
        val count = generateSequence(16) { it * 2 }.first { it >= names.size * 2 }
        val bytes = ByteArray(maxOf(size, 32 + count * 16 + 64))
        fun put(at: Int, v: Int) { bytes[at] = v.toByte(); bytes[at + 1] = (v ushr 8).toByte(); bytes[at + 2] = (v ushr 16).toByte(); bytes[at + 3] = (v ushr 24).toByte() }
        bytes[0] = 'M'.code.toByte(); bytes[1] = 'P'.code.toByte(); bytes[2] = 'Q'.code.toByte(); bytes[3] = 0x1A
        put(4, 32); put(8, bytes.size); bytes[12] = 0; bytes[14] = 3
        put(16, 32); put(20, 32 + count * 16); put(24, count); put(28, names.size)
        val table = ByteArray(count * 16) { 0xFF.toByte() }
        fun tput(at: Int, v: Int) { table[at] = v.toByte(); table[at + 1] = (v ushr 8).toByte(); table[at + 2] = (v ushr 16).toByte(); table[at + 3] = (v ushr 24).toByte() }
        names.forEachIndexed { block, name ->
            var i = MpqContents.hash(name, 0) and (count - 1)
            while (table[i * 16 + 12] != 0xFF.toByte() || table[i * 16 + 13] != 0xFF.toByte()) i = (i + 1) and (count - 1)
            tput(i * 16, MpqContents.hash(name, 1)); tput(i * 16 + 4, MpqContents.hash(name, 2))
            tput(i * 16 + 8, 0); tput(i * 16 + 12, block)
        }
        MpqContents.encrypt(table, MpqContents.hash("(hash table)", 3))
        table.copyInto(bytes, 32)
        file.parentFile?.mkdirs()
        file.writeBytes(bytes)
        return file
    }

    /** A program with an MPQ archive after it (a disc's INSTALL.EXE). */
    fun installExe(file: File): File {
        val stub = ByteArray(1024).also { it[0] = 'M'.code.toByte(); it[1] = 'Z'.code.toByte() }
        val archive = ByteArray(2048).also { it[0] = 'M'.code.toByte(); it[1] = 'P'.code.toByte(); it[2] = 'Q'.code.toByte(); it[3] = 0x1A }
        file.parentFile?.mkdirs()
        file.writeBytes(stub + archive)
        return file
    }

    fun zip(file: File, entries: Map<String, ByteArray>): File {
        file.parentFile?.mkdirs()
        ZipOutputStream(file.outputStream()).use { z ->
            for ((name, data) in entries) {
                z.putNextEntry(ZipEntry(name))
                z.write(data)
                z.closeEntry()
            }
        }
        return file
    }

    /** An ISO 9660 image named [volume] with [files] in it (paths with "/" make folders); long names as Joliet's second table. */
    fun iso(file: File, volume: String, files: Map<String, ByteArray>): File {
        val sector = 2048
        class Dir(val name: String, val path: String = "", val dirs: MutableMap<String, Dir> = linkedMapOf(), val files: MutableMap<String, ByteArray> = linkedMapOf()) {
            var extent = 0
            var size = sector
        }
        val root = Dir("")
        for ((path, data) in files) {
            val parts = path.split('/')
            var d = root
            for (p in parts.dropLast(1)) d = d.dirs.getOrPut(p) { Dir(p, d.path + p + "/") }
            d.files[parts.last()] = data
        }
        val all = ArrayList<Dir>()
        fun collect(d: Dir) { all += d; d.dirs.values.forEach { collect(it) } }
        collect(root)
        // Two tables (primary, Joliet) of one sector per folder each; then the data.
        var next = 20
        val primaryAt = HashMap<Dir, Int>(); val jolietAt = HashMap<Dir, Int>()
        for (d in all) { primaryAt[d] = next++; jolietAt[d] = next++ }
        val dataAt = HashMap<String, Int>()
        fun place(d: Dir, prefix: String) {
            for ((n, data) in d.files) { dataAt["$prefix$n"] = next; next += (data.size + sector - 1) / sector }
            for ((n, sub) in d.dirs) place(sub, "$prefix$n/")
        }
        place(root, "")
        val image = ByteArray(next * sector)
        fun record(buf: ByteArray, off: Int, name: ByteArray, extent: Int, size: Int, dir: Boolean): Int {
            val length = 33 + name.size + (if (name.size % 2 == 0) 1 else 0)
            buf[off] = length.toByte()
            ByteBuffer.wrap(buf, off + 2, 4).order(ByteOrder.LITTLE_ENDIAN).putInt(extent)
            ByteBuffer.wrap(buf, off + 10, 4).order(ByteOrder.LITTLE_ENDIAN).putInt(size)
            buf[off + 25] = if (dir) 2 else 0
            buf[off + 32] = name.size.toByte()
            name.copyInto(buf, off + 33)
            return length
        }
        fun descriptor(sectorNo: Int, type: Int, table: Map<Dir, Int>, joliet: Boolean) {
            val at = sectorNo * sector
            image[at] = type.toByte()
            "CD001".toByteArray().copyInto(image, at + 1)
            image[at + 6] = 1
            if (joliet) { "%/E".toByteArray().copyInto(image, at + 88) }
            volume.padEnd(32).toByteArray().copyInto(image, at + 40)
            record(image, at + 156, byteArrayOf(0), table.getValue(root), sector, true)
        }
        descriptor(16, 1, primaryAt, false)
        descriptor(17, 2, jolietAt, true)
        image[18 * sector] = 255.toByte(); "CD001".toByteArray().copyInto(image, 18 * sector + 1)
        fun name(n: String, joliet: Boolean) = if (joliet) n.toByteArray(Charsets.UTF_16BE) else (n.uppercase().take(30) + ";1").toByteArray()
        for (d in all) for (joliet in listOf(false, true)) {
            val table = if (joliet) jolietAt else primaryAt
            var at = table.getValue(d) * sector
            at += record(image, at, byteArrayOf(0), table.getValue(d), sector, true)
            at += record(image, at, byteArrayOf(1), table.getValue(d), sector, true)
            for ((n, sub) in d.dirs) at += record(image, at, if (joliet) n.toByteArray(Charsets.UTF_16BE) else n.uppercase().toByteArray(), table.getValue(sub), sector, true)
            for ((n, data) in d.files) {
                val key = d.path + n
                at += record(image, at, name(n, joliet), dataAt.getValue(key), data.size, false)
            }
        }
        for ((key, extent) in dataAt) {
            val parts = key.split('/'); var d = root
            for (p in parts.dropLast(1)) d = d.dirs.getValue(p)
            d.files.getValue(parts.last()).copyInto(image, extent * sector)
        }
        file.parentFile?.mkdirs()
        file.writeBytes(image)
        return file
    }

    // Games ------------------------------------------------------------------------------------

    fun devilutionxZip(file: File, version: String = "1.5.4.0") = zip(file, mapOf(
        "devilutionx/devilutionx.exe" to pe(File.createTempFile("devilutionx", ".exe"), version, PeInfo.MACHINE_AMD64, listOf("KERNEL32.dll", "SDL2.dll")).readBytes(),
        "devilutionx/SDL2.dll" to ByteArray(64),
        "devilutionx/devilutionx.mpq" to mpqBytes(),
    ))

    fun mpqBytes(size: Int = 4096) = ByteArray(size).also { it[0] = 'M'.code.toByte(); it[1] = 'P'.code.toByte(); it[2] = 'Q'.code.toByte(); it[3] = 0x1A }

    fun diablo2Install(dir: File, version: String = "1.14.1.68", expansion: Boolean = true): File {
        pe(File(dir, "Game.exe"), version, imports = listOf("KERNEL32.dll", "USER32.dll", "binkw32.dll", "SmackW32.dll", "ijl11.dll"))
        for (dll in listOf("binkw32.dll", "SmackW32.dll", "ijl11.dll")) File(dir, dll).writeBytes(ByteArray(64))
        Diablo2ClassicImporter.BASE.forEach { mpq(File(dir, it)) }
        if (expansion) Diablo2ClassicImporter.EXPANSION.forEach { mpq(File(dir, it)) }
        return dir
    }

    fun starcraftInstall(dir: File, version: String = "1.15.2.1", discs: Boolean = true): File {
        pe(File(dir, "StarCraft.exe"), version, imports = listOf("KERNEL32.dll", "storm.dll", "Local.dll", "Smackw32.dll"))
        StarCraftClassicImporter.REQUIRED.forEach { File(dir, it).writeBytes(ByteArray(64)) }
        StarCraftClassicImporter.ARCHIVES.forEach { mpq(File(dir, it), StarCraftClassicImporter.CONTENTS[it] ?: emptyList()) }
        if (discs) {
            installExe(File(dir, "Starcraft.mpq"))
            installExe(File(dir, "BroodWar.mpq"))
        }
        return dir
    }

    /** StarCraft: Remastered: a 64-bit StarCraft.exe at [version], its Data folder, no classic archives. */
    fun starcraftRemastered(dir: File, version: String = "1.23.10.12409"): File {
        pe(File(dir, "StarCraft.exe"), version, PeInfo.MACHINE_AMD64, listOf("KERNEL32.dll", "d3d11.dll"))
        File(dir, "Data/data").mkdirs()
        File(dir, "Data/data/data.000").writeBytes(ByteArray(128))
        File(dir, ".product.db").writeBytes(ByteArray(8))
        return dir
    }

    fun starcraft2Install(dir: File, build: String = "39117", version: String = "3.0.5.39117", launcher: Boolean = true): File {
        pe(File(dir, "Versions/Base$build/SC2_x64.exe"), version, PeInfo.MACHINE_AMD64, listOf("KERNEL32.dll", "d3d9.dll"))
        File(dir, "SC2Data/data").mkdirs()
        File(dir, "SC2Data/data/data.000").writeBytes(ByteArray(128))
        if (launcher) pe(File(dir, StarCraft2OfflineImporter.LAUNCHER), "1.0.0.0")
        return dir
    }

    fun bytes(n: Int) = ByteArrayOutputStream().apply { write(ByteArray(n)) }.toByteArray()
}
