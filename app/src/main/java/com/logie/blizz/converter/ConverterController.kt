package com.logie.blizz.converter

import android.content.Context
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.io.File
import kotlin.concurrent.thread

/**
 * The Converter screen's engine: makes sure the runtime is in ([ConverterRuntime]), then runs the driver (`convert.py`, which runs the catabackport tool by
 * unit and keeps `progress.json`) for one expansion at a time in a process of its own, polls its progress file and tells the screen ([state]). The output is
 * `files/converter/<expansion>/release` (the tool's packs and `index.json`, 3.3.5a's format) and `work/` beside it; a run again carries on where the last
 * stopped (the tool skips what is done). One run at a time (they share the phone's memory and the source's patience). NOT run on a phone.
 */
object ConverterController {
    data class State(
        val runtimeInstalled: Boolean = false,
        val runtimeText: String? = null,
        val runtimeFraction: Float? = null,
        val running: String? = null,                         // the expansion's key while one runs
        val progress: Map<String, ConverterProgress> = emptyMap(),
        val message: String? = null,
        val outputFolder: String = "",
    )

    private val flow = MutableStateFlow(State())
    val state: StateFlow<State> = flow.asStateFlow()

    @Volatile private var process: Process? = null
    @Volatile private var stopping = false

    private fun paths(context: Context) = ConverterRuntime.paths(context.applicationContext.filesDir, com.logie.blizz.wow.WowLayout.of(context).converted)

    /** Reads what is on disk: the runtime's state and each expansion's last progress. Cheap; call when the screen opens. */
    fun refresh(context: Context) {
        val p = paths(context)
        val progress = Expansions.all.mapNotNull { e ->
            File(p.output, "${e.key}/progress.json").takeIf { it.isFile }?.readText()?.let(ConverterProgress::parse)?.let { e.key to it }
        }.toMap()
        flow.value = flow.value.copy(runtimeInstalled = ConverterRuntime.isInstalled(p), progress = progress, outputFolder = p.output.path)
    }

    /** Downloads the runtime (or a newer one) in the background. */
    fun installRuntime(context: Context, update: Boolean = false) {
        if (flow.value.runtimeText != null || flow.value.running != null) return
        val p = paths(context)
        thread(name = "converter-runtime") {
            try {
                ConverterRuntime.ensure(p, update) { text, fraction -> flow.value = flow.value.copy(runtimeText = text, runtimeFraction = fraction) }
                flow.value = flow.value.copy(runtimeText = null, runtimeFraction = null, runtimeInstalled = ConverterRuntime.isInstalled(p), message = null)
            } catch (e: Exception) {
                flow.value = flow.value.copy(runtimeText = null, runtimeFraction = null, message = e.message ?: e.javaClass.simpleName)
            }
        }
    }

    /** Converts [key]: installs the runtime first if it is not in. */
    fun convert(context: Context, key: String) {
        if (flow.value.running != null || flow.value.runtimeText != null) return
        val expansion = Expansions.byKey(key) ?: return
        val p = paths(context)
        stopping = false
        flow.value = flow.value.copy(running = key, message = null)
        thread(name = "converter-$key") {
            try {
                if (!ConverterRuntime.isInstalled(p)) {
                    ConverterRuntime.ensure(p) { text, fraction -> flow.value = flow.value.copy(runtimeText = text, runtimeFraction = fraction) }
                    flow.value = flow.value.copy(runtimeText = null, runtimeFraction = null, runtimeInstalled = true)
                }
                p.output.mkdirs()
                val log = File(p.output, "${expansion.key}-driver.log")
                val builder = ProcessBuilder(
                    p.python.path, p.driver.path, "run", expansion.key, "--root", p.output.path, "--tool", p.tool.path, "--python", p.python.path,
                ).directory(p.output).redirectErrorStream(true).redirectOutput(ProcessBuilder.Redirect.appendTo(log))
                builder.environment()["PATH"] = File(p.folder, "bin").path + ":" + (System.getenv("PATH") ?: "/system/bin")
                builder.environment()["TMPDIR"] = File(p.output, "tmp").also { it.mkdirs() }.path
                val started = builder.start()
                process = started
                val progressFile = File(p.output, "${expansion.key}/progress.json")
                while (started.isAlive) {
                    Thread.sleep(2000)
                    readProgress(progressFile, expansion.key)
                }
                readProgress(progressFile, expansion.key)
                val code = started.exitValue()
                val text = when {
                    stopping -> "Stopped. Convert again to carry on where it left off."
                    code == 0 || code == 75 -> null
                    else -> "The converter stopped with status $code: see ${log.name} in ${p.output.path}."
                }
                flow.value = flow.value.copy(running = null, message = text)
            } catch (e: Exception) {
                flow.value = flow.value.copy(running = null, runtimeText = null, runtimeFraction = null, message = e.message ?: e.javaClass.simpleName)
            } finally {
                process = null
            }
        }
    }

    fun stop() {
        stopping = true
        process?.destroy()
    }

    private fun readProgress(file: File, key: String) {
        val progress = file.takeIf { it.isFile }?.readText()?.let(ConverterProgress::parse) ?: return
        flow.value = flow.value.copy(progress = flow.value.progress + (key to progress))
    }
}
