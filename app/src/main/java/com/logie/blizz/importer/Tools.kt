package com.logie.blizz.importer

import android.content.Context
import java.io.File
import kotlin.concurrent.thread

/**
 * Runs the programs the app ships for its imports, which Android lets it run from its native
 * library folder: innoextract (libinnoextract.so, GOG's installers) and blizzard-legacy-dl
 * (libbldl.so, Blizzard's legacy downloads). Never anything from an imported archive.
 */
object Tools {
    class Result(val code: Int, val tail: List<String>)

    fun file(context: Context, name: String): File = File(context.applicationInfo.nativeLibraryDir, name)

    /** Runs [command] in [directory], its output line by line to [onLine]; stopped when [cancel] is. */
    fun run(command: List<String>, directory: File, cancel: CancelToken, environment: Map<String, String> = emptyMap(), onLine: (String) -> Unit): Result {
        directory.mkdirs()
        val process = ProcessBuilder(command)
            .directory(directory)
            .redirectErrorStream(true)
            .apply { environment().putAll(environment) }
            .start()
        val watcher = thread(isDaemon = true, name = "tool-watcher") {
            try {
                while (process.isAlive) {
                    if (cancel.cancelled) process.destroy()
                    Thread.sleep(300)
                }
            } catch (_: InterruptedException) {
            }
        }
        val tail = ArrayDeque<String>()
        process.inputStream.bufferedReader().use { reader ->
            // Progress is drawn with carriage returns: each one is a line of its own here.
            val line = StringBuilder()
            while (true) {
                val c = reader.read()
                if (c < 0 || c == '\n'.code || c == '\r'.code) {
                    if (line.isNotEmpty()) {
                        val text = line.toString()
                        tail.addLast(text)
                        if (tail.size > 20) tail.removeFirst()
                        onLine(text)
                        line.setLength(0)
                    }
                    if (c < 0) break
                } else {
                    line.append(c.toChar())
                }
            }
        }
        val code = process.waitFor()
        watcher.interrupt()
        cancel.check()
        return Result(code, tail.toList())
    }
}

/** GOG's offline installers (Inno Setup), unpacked by innoextract without running them. */
class Innoextract(private val program: File) {
    /** Unpacks [installer] (its .bin parts beside it) into [dest], lower-case names. */
    fun extract(installer: File, dest: File, cancel: CancelToken, onLine: (String) -> Unit = {}) {
        if (!program.canExecute()) throw ImportException(Problem.MISSING_RUNTIME_DEPENDENCY, "innoextract is missing from this build of the app.")
        dest.mkdirs()
        val result = Tools.run(listOf(program.path, "--extract", "--lowercase", "--silent", "--progress=1", "--output-dir", dest.path, installer.path), dest, cancel, onLine = onLine)
        if (result.code != 0) {
            throw ImportException(
                Problem.UNSUPPORTED_INSTALLER,
                "${installer.name} couldn't be unpacked: it isn't a GOG offline installer innoextract can read, or its .bin parts aren't beside it.",
                result.tail.joinToString("\n"),
            )
        }
    }
}
