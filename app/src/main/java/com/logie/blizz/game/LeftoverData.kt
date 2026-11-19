package com.logie.blizz.game

import java.io.File

/**
 * World of Warcraft: Forever was taken out of the app on 18 November 2026 (the user: "Delete it all. Then make it so the app
 * wipes any leftover downloaded data like the 50gb file"). What it left on the phone is removed as the app starts, once it is
 * there and whatever version left it: the game's download, the map data, the database and the servers (`files/realms/forever-v2`,
 * about 50 GB), the first Forever's folders (`files/forever`, `files/forever-arm64`, the ARM64 runtime's `files/imagefs` and
 * `files/imagefs_shared`), its programs still running, its login certificate in the games' Windows, its log there and its saved
 * login. Nothing of another game is touched: every path here was Forever's alone. Plain Kotlin but for [wipe]'s callers.
 */
object LeftoverData {
    /** Forever's folders under the app's `files` folder. */
    val FOLDERS = listOf("realms/forever-v2", "realms/forever", "forever", "forever-arm64", "imagefs", "imagefs_shared")
    /** Files it wrote into the games' Windows (`drive_c/windows`). */
    val WINDOWS_FILES = listOf("foreverkey.log", "forevergo.log", "forevergo.login", "forevergo.ca", "forevergo.exe")

    class Result(val bytes: Long, val folders: List<String>, val processes: Int, val certificates: Int)

    /** The process ids in Forever's pid files whose command line is one of its own programs (a path with [marker] in it). */
    fun leftoverPids(files: File, marker: String = "/realms/forever-v2/", cmdline: (Int) -> String? = ::cmdlineOf): List<Int> =
        File(files, "realms/forever-v2/run").listFiles { f -> f.isFile }.orEmpty()
            .mapNotNull { it.readText().trim().toIntOrNull() }
            .filter { pid -> pid > 1 && cmdline(pid)?.contains(marker) == true }

    fun cmdlineOf(pid: Int): String? = runCatching { File("/proc/$pid/cmdline").readText().replace('\u0000', ' ') }.getOrNull()

    /** The SHA-1 thumbprint (upper-case hex) of a PEM certificate, as the games' registry names it. */
    fun thumbprint(pem: String): String? = runCatching {
        val der = java.util.Base64.getMimeDecoder().decode(pem.lineSequence().filter { !it.startsWith("-----") }.joinToString(""))
        java.security.MessageDigest.getInstance("SHA-1").digest(der).joinToString("") { "%02X".format(it) }
    }.getOrNull()

    /** [registry] (Wine's system.reg) without the root-certificate keys named [thumbprint]; the count of keys taken out. */
    fun withoutCertificate(registry: String, thumbprint: String): Pair<String, Int> {
        val kept = ArrayList<String>(); var removed = 0; var skipping = false
        for (line in registry.split('\n')) {
            if (line.startsWith("[")) {
                skipping = line.contains("SystemCertificates\\\\Root\\\\Certificates\\\\$thumbprint]")
                if (skipping) removed++
            }
            if (!skipping) kept += line
        }
        if (removed == 0) return registry to 0
        val out = StringBuilder(kept.joinToString("\n"))
        if (registry.endsWith("\n") && !out.endsWith("\n")) out.append('\n')
        return out.toString() to removed
    }

    private fun sizeOf(f: File): Long = runCatching { if (f.isDirectory) f.listFiles().orEmpty().sumOf { sizeOf(it) } else f.length() }.getOrDefault(0L)

    /**
     * Removes it all. [containers] are the games' Windows folders (each holds `.wine`); [kill] ends a process. Safe to run at
     * every start: with nothing left it does nothing. Returns what it removed, or null when there was nothing.
     */
    fun wipe(files: File, containers: List<File>, kill: (Int) -> Unit): Result? {
        val there = FOLDERS.map { File(files, it) }.filter { it.exists() }
        val windows = containers.flatMap { c -> WINDOWS_FILES.map { File(c, ".wine/drive_c/windows/$it") } }.filter { it.exists() }
        if (there.isEmpty() && windows.isEmpty()) return null
        val pids = leftoverPids(files)
        pids.forEach { runCatching { kill(it) } }
        var certificates = 0
        thumbprint(File(files, "realms/forever-v2/keys/forever-root-ca.cert.pem").takeIf { it.isFile }?.readText().orEmpty())?.takeIf { it.length == 40 }?.let { print ->
            for (c in containers) runCatching {
                val reg = File(c, ".wine/system.reg")
                if (!reg.isFile) return@runCatching
                val (text, n) = withoutCertificate(reg.readText(), print)
                if (n > 0) { val tmp = File(reg.path + ".tmp"); tmp.writeText(text); if (tmp.renameTo(reg)) certificates += n else tmp.delete() }
            }
        }
        var bytes = 0L
        for (f in there) { bytes += sizeOf(f); f.deleteRecursively() }
        windows.forEach { it.delete() }
        return Result(bytes, there.filter { !it.exists() }.map { it.name }, pids.size, certificates)
    }
}
