package com.logie.blizz.forevernew

import java.io.File

/**
 * Forever's server programs that outlived the app, and the wait for one to be ready.
 *
 * The phone, 16 November 2026, after the hours of map building: "mariadbd did not become ready in 3 minutes", with the database's
 * own log saying *ready for connections* on port 3313; then, at the next press, "Port 3313 is already in use; mariadbd can't
 * start". Android had stopped the app's clock while it was out of sight (the wait's three minutes passed without the app looking
 * once more), and later ended the app; the database went on running by itself and held its port. Here, with the package's own
 * `mariadbd` started the app's way, it was ready in three seconds.
 */
object ForeverLeftovers {
    /** The process a program's pid file names, or null (no file, not a number). */
    fun pidOf(pidFile: File): Int? = pidFile.takeIf { it.isFile }?.let { runCatching { it.readText().trim().toInt() }.getOrNull() }?.takeIf { it > 1 }

    /** Whether process [pid] is one of this server's programs: its command line (as `/proc` gives it) names a program in [bin]. */
    fun isOurs(pid: Int, bin: File, cmdline: (Int) -> String? = ::procCmdline): Boolean = cmdline(pid)?.contains(bin.path + "/") == true

    private fun procCmdline(pid: Int): String? = runCatching { File("/proc/$pid/cmdline").readText().replace('\u0000', ' ') }.getOrNull()

    /**
     * Ends the program [pidFile] names if it is this server's ([isOurs]): SIGTERM (MariaDB flushes and ends; the servers save), up
     * to [waitSeconds] for it to go, then SIGKILL. True if there was one. [signal] is `android.os.Process.sendSignal` on a phone.
     */
    fun end(pidFile: File, bin: File, signal: (Int, Int) -> Unit, waitSeconds: Int = 60, alive: (Int) -> Boolean = { File("/proc/$it").exists() },
            cmdline: (Int) -> String? = ::procCmdline, sleep: (Long) -> Unit = { Thread.sleep(it) }): Boolean {
        val pid = pidOf(pidFile) ?: return false
        if (!alive(pid) || !isOurs(pid, bin, cmdline)) return false
        signal(pid, 15)
        repeat(waitSeconds * 2) { if (!alive(pid)) return true; sleep(500) }
        if (alive(pid)) { signal(pid, 9); sleep(500) }
        return true
    }

    enum class Wait { READY, ENDED, TIMED_OUT }

    /**
     * Waits for a started program: [ready] (its log's line and its port), else [alive] false, looked at every half second, [tries]
     * times. Counted in looks, not by the clock, and looked at once more after the last wait: a phone that stops the app for a
     * while (out of sight, its clock running on) must not find its time gone without having looked.
     */
    fun await(tries: Int, ready: () -> Boolean, alive: () -> Boolean, sleep: (Long) -> Unit = { Thread.sleep(it) }): Wait {
        repeat(tries) {
            if (ready()) return Wait.READY
            if (!alive()) return if (ready()) Wait.READY else Wait.ENDED
            sleep(500)
        }
        return if (ready()) Wait.READY else Wait.TIMED_OUT
    }
}
