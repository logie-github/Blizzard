package com.logie.blizz.wow

import java.io.File
import java.io.Writer
import java.util.concurrent.TimeUnit

/** A program the realm started ([ctl.sh db], the auth server, ...). */
interface RealmProcess {
    val isAlive: Boolean
    fun exitValue(): Int
    /** Waits up to [timeoutMs] for the program to end; true if it has. */
    fun waitFor(timeoutMs: Long): Boolean
    /** Writes a line to the program's console (the world server's commands); false if it can't. */
    fun send(line: String): Boolean
    fun destroy()
    fun destroyForcibly()
}

/** Starts the programs. An interface so tests use a fake; [SystemRunner] is the real one. */
interface ProcessRunner {
    /** Starts [command] with its output (and errors) going to [log]; [keepInput] keeps its console open for [RealmProcess.send]. */
    fun start(command: WowCtl.Command, log: File, keepInput: Boolean): RealmProcess

    /**
     * Ends server programs left from before (Android ended the app without stopping them, so they
     * hold their ports): those named in the pid files in `run/` whose command line is the server's.
     */
    fun endLeftovers(layout: WowLayout)
}

class SystemRunner : ProcessRunner {
    override fun start(command: WowCtl.Command, log: File, keepInput: Boolean): RealmProcess {
        log.parentFile?.mkdirs()
        command.directory.mkdirs()
        val builder = ProcessBuilder(command.argv).directory(command.directory)
        builder.environment().putAll(command.env)
        builder.redirectErrorStream(true).redirectOutput(log)
        if (!keepInput) builder.redirectInput(File("/dev/null"))
        val process = builder.start()
        val input: Writer? = if (keepInput) process.outputStream.bufferedWriter() else null
        return object : RealmProcess {
            override val isAlive get() = process.isAlive
            override fun exitValue() = process.exitValue()
            override fun waitFor(timeoutMs: Long) = process.waitFor(timeoutMs, TimeUnit.MILLISECONDS)
            override fun send(line: String) = input != null && runCatching { input.write(line + "\n"); input.flush() }.isSuccess
            override fun destroy() { runCatching { input?.close() }; process.destroy() }
            override fun destroyForcibly() { process.destroyForcibly() }
        }
    }

    override fun endLeftovers(layout: WowLayout) {
        val bin = File(layout.server, "bin").path
        val pids = listOf("worldserver.pid", "authserver.pid", "mysqld.pid").mapNotNull { name ->
            File(layout.run, name).takeIf { it.isFile }?.readText()?.trim()?.toIntOrNull()
        }.filter { pid -> runCatching { File("/proc/$pid/cmdline").readText().contains(bin) }.getOrDefault(false) }
        if (pids.isEmpty()) return
        for (pid in pids) android.os.Process.sendSignal(pid, 15) // SIGTERM: MariaDB flushes and ends
        repeat(60) {
            if (pids.none { File("/proc/$it").exists() }) return
            Thread.sleep(500)
        }
        for (pid in pids) if (File("/proc/$pid").exists()) android.os.Process.sendSignal(pid, 9)
    }
}
