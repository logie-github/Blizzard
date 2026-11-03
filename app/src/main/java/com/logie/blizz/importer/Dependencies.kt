package com.logie.blizz.importer

import java.io.File
import java.io.RandomAccessFile

/**
 * A Windows program's dependencies: the DLLs its import table names. Those Wine provides (Windows'
 * own) are fine; any other must be beside the program, or it won't start. Plain Kotlin, unit-tested.
 */
object Dependencies {
    /** Windows' own libraries, which Wine provides (lower-case, without ".dll"). */
    private val SYSTEM = setOf(
        "kernel32", "user32", "gdi32", "advapi32", "shell32", "ole32", "oleaut32", "ws2_32", "wsock32", "winmm", "ddraw",
        "dsound", "d3d8", "d3d9", "d3d10", "d3d10_1", "d3d11", "d3d12", "dxgi", "dinput", "dinput8", "version", "comctl32",
        "comdlg32", "shlwapi", "imm32", "setupapi", "msvcrt", "ucrtbase", "opengl32", "glu32", "rpcrt4", "crypt32",
        "iphlpapi", "dbghelp", "psapi", "uxtheme", "dwmapi", "hid", "mpr", "netapi32", "secur32", "winhttp", "wininet",
        "bcrypt", "ntdll", "normaliz", "mscoree", "msacm32", "avrt", "mmdevapi", "wintrust", "userenv", "powrprof",
        "dnsapi", "oleacc", "usp10", "gdiplus", "msimg32", "wtsapi32", "cfgmgr32", "xinput1_1", "xinput1_2", "xinput1_3",
        "xinput1_4", "xinput9_1_0", "dxva2", "mfplat", "mfreadwrite", "mf", "propsys", "shcore", "winspool", "winspool.drv",
        "d3dcompiler_43", "d3dcompiler_47", "msvfw32", "avifil32", "olepro32", "urlmon", "wldap32", "sensapi", "dciman32",
        "dsound", "dplayx", "dpnet", "msi", "riched20", "riched32", "comsupp", "vulkan-1", "x3daudio1_7", "xaudio2_7",
        "xaudio2_8", "xaudio2_9", "imagehlp", "ntdsapi", "credui", "msv1_0", "kernelbase", "sechost", "wer", "dsound",
    )

    private fun isSystem(dll: String): Boolean {
        val name = dll.lowercase().removeSuffix(".dll")
        return name in SYSTEM || name.startsWith("api-ms-win-") || name.startsWith("ext-ms-") ||
            name.startsWith("msvcp") || name.startsWith("msvcr") || name.startsWith("vcruntime") ||
            name.startsWith("d3dcompiler_") || name.startsWith("d3dx9_") || name.startsWith("d3dx10") || name.startsWith("d3dx11") || name.startsWith("xinput")
    }

    /** The DLLs [program] imports that are neither Windows' own nor in its folder. */
    fun missing(program: File): List<String> {
        val imports = imports(program) ?: return emptyList()
        val beside = program.parentFile?.list()?.map { it.lowercase() }?.toSet() ?: emptySet()
        return imports.filter { !isSystem(it) && it.lowercase() !in beside }
    }

    /** The import table's DLL names, or null when it can't be read. */
    fun imports(program: File): List<String>? = runCatching { RandomAccessFile(program, "r").use { read(it) } }.getOrNull()

    private fun read(f: RandomAccessFile): List<String> {
        f.seek(0x3c)
        val pe = le32(f).toLong()
        f.seek(pe + 4)
        f.skipBytes(2)
        val sections = le16(f)
        f.skipBytes(12)
        val optionalSize = le16(f)
        f.skipBytes(2)
        val optional = pe + 24
        f.seek(optional)
        val magic = le16(f)
        val dirs = optional + if (magic == 0x20b) 112 else 96
        f.seek(dirs + 8)
        val importRva = le32(f).toLong() and 0xffffffffL
        if (importRva == 0L) return emptyList()
        // The section table, to turn addresses into file offsets.
        val table = optional + optionalSize
        data class Section(val va: Long, val size: Long, val raw: Long)
        val list = (0 until sections).map { i ->
            f.seek(table + i * 40L + 8)
            val vsize = le32(f).toLong() and 0xffffffffL
            val va = le32(f).toLong() and 0xffffffffL
            val rawSize = le32(f).toLong() and 0xffffffffL
            val raw = le32(f).toLong() and 0xffffffffL
            Section(va, maxOf(vsize, rawSize), raw)
        }
        fun offset(rva: Long): Long? = list.firstOrNull { rva >= it.va && rva < it.va + it.size }?.let { it.raw + (rva - it.va) }
        val names = ArrayList<String>()
        var descriptor = offset(importRva) ?: return emptyList()
        while (names.size < 256) {
            f.seek(descriptor + 12)
            val nameRva = le32(f).toLong() and 0xffffffffL
            if (nameRva == 0L) break
            val at = offset(nameRva) ?: break
            f.seek(at)
            val name = StringBuilder()
            while (name.length < 260) {
                val c = f.read()
                if (c <= 0) break
                name.append(c.toChar())
            }
            names += name.toString()
            descriptor += 20
        }
        return names
    }

    private fun le16(f: RandomAccessFile): Int = f.read() or (f.read() shl 8)
    private fun le32(f: RandomAccessFile): Int = f.read() or (f.read() shl 8) or (f.read() shl 16) or (f.read() shl 24)
}

/** One pass over the person's folders: every file, by lower-case name. */
class Scan(roots: List<SourceNode>, depth: Int = 6) {
    val files: List<SourceNode> = roots.flatMap { root -> runCatching { root.walk(depth).toList() }.getOrDefault(emptyList()) }

    fun named(name: String): SourceNode? = files.firstOrNull { it.name.equals(name, ignoreCase = true) }
    fun matching(regex: Regex): List<SourceNode> = files.filter { regex.matches(it.name.lowercase()) }
}

/** Checks for a program: there, a Windows x86 program, its DLLs beside it. */
fun programChecks(dir: File, name: String): Pair<List<Check>, PeInfo?> {
    val file = FileValidator.find(dir, name)
    if (file == null) return listOf(Check(name, false, "missing")) to null
    val pe = PeInfo.read(file)
    val checks = mutableListOf(Check(name, pe != null && pe.isWindowsX86Family, if (pe == null) "not a Windows program" else "version ${pe.version ?: "unknown"}"))
    if (pe != null) {
        val missing = Dependencies.missing(file)
        checks += Check("$name's libraries", missing.isEmpty(), if (missing.isEmpty()) "all present" else "missing ${missing.joinToString()}")
    }
    return checks to pe
}

/** The first folder under [node] (to [depth] down) whose own files [accept] approves of. */
fun findFolder(node: SourceNode, depth: Int, accept: (List<SourceNode>) -> Boolean): SourceNode? {
    if (!node.isDirectory || depth < 0) return null
    val children = runCatching { node.children() }.getOrDefault(emptyList())
    if (accept(children)) return node
    return children.filter { it.isDirectory }.firstNotNullOfOrNull { findFolder(it, depth - 1, accept) }
}
