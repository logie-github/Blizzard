package com.logie.blizz.wow

import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import java.io.File
import kotlin.coroutines.coroutineContext

/**
 * Starts and stops the WoW app's realm from Blizzard's copy of its files, the way the WoW app's
 * `Server` does: MariaDB, then the databases (set up if missing, never rebuilt), the realm's world
 * database brought in line with its modules, the realm list, the auth server (3724) and the realm's
 * world server (8085 ChromieCraft, 8086 Wrath Remix), each a program of `ctl.sh`. Stopping saves the
 * characters first (`server shutdown`), then ends auth and the database cleanly.
 *
 * Everything outside (processes, time, ports) is passed in, so tests run it with a fake runner.
 * Only that fake-runner behaviour (order of steps, statuses, failures, the commands built) is
 * verified; real musl programs, MariaDB's recovery on the user's data and the world server's
 * start have never run from Blizzard's folder.
 */
internal class RealmController(
    private val layout: WowLayout,
    private val runner: ProcessRunner,
    private val scope: CoroutineScope,
    private val timeZone: () -> String = { WowCtl.posixTimeZone() },
    private val lanAddress: () -> String? = { null },
    private val portOpen: (Int) -> Boolean,
    private val sleep: suspend (Long) -> Unit = { delay(it) },
    private val clock: () -> Long = System::currentTimeMillis,
    private val io: CoroutineDispatcher = Dispatchers.IO,
    private val onFailure: (message: String, log: String?) -> Unit = { _, _ -> },
    private val pollMs: Long = 1000,
    private val _status: MutableStateFlow<WowRealm.Status> = MutableStateFlow(WowRealm.Status()),
) {
    val status: StateFlow<WowRealm.Status> = _status

    private val lock = Mutex()
    private var db: RealmProcess? = null
    private var auth: RealmProcess? = null
    private var world: RealmProcess? = null
    @Volatile private var stepProcess: RealmProcess? = null
    @Volatile private var stopping = false
    private var watcher: Job? = null
    private lateinit var loader: File

    private val TRACEABLE = setOf("configure", "modules", "races", "realmlist")

    private class StepFailed(message: String, val log: File? = null) : Exception(message)

    private fun update(change: WowRealm.Status.() -> WowRealm.Status) { _status.value = _status.value.change() }

    private fun step(step: WowRealm.Step, message: String? = null) =
        update { copy(phase = WowRealm.Phase.STARTING, step = step, message = message, error = null, log = null) }

    /** Brings the realm up. Returns when it is up or has failed. Cancelling it ends what it started. */
    suspend fun run(realm: Realm) = lock.withLock {
        withContext(io) {
            try {
                stopping = false
                _status.value = WowRealm.Status(phase = WowRealm.Phase.STARTING, step = WowRealm.Step.PREPARING, realm = realm)
                up(realm)
            } catch (e: StepFailed) {
                fail(e.message ?: "", e.log)
            } catch (e: CancellationException) {
                withContext(kotlinx.coroutines.NonCancellable) { killAll() }
                throw e
            } catch (e: Exception) {
                fail(e.message ?: e.javaClass.simpleName, null)
            }
        }
    }

    private suspend fun up(realm: Realm) {
        step(WowRealm.Step.PREPARING, "Checking the imported realm")
        if (!layout.isImported()) {
            throw StepFailed("World of Warcraft isn't imported completely (the server's programs or databases are missing). Import it again from the World of Warcraft app's export.")
        }
        val prefix = layout.root.path
        val moved = WowPathRewrite.rewrite(layout, WowPathRewrite.oldPrefixes(WowExportInfo.sourceFilesDir(layout)), prefix)
        if (moved.changed) logLine("Paths moved to $prefix: ${moved.filesRewritten.size} files, ${moved.linksRewritten.size} links")
        loader = WowCtl.prepare(layout)
        runner.endLeftovers(layout)
        // Left by a program that ended without cleaning up (the export leaves run/ out, so these are Blizzard's own).
        for (name in listOf("mysqld.pid", "mysqld.sock", "mysqld.sock.lock", "authserver.pid", "worldserver.pid")) File(layout.run, name).delete()
        if (!layout.hasServerData()) {
            throw StepFailed("The realm's data (dbc and maps) isn't in the imported files. Open World of Warcraft's Game files in the World of Warcraft app, then export again.")
        }

        step(WowRealm.Step.CONFIGURING, "Writing the realm's settings")
        runToEnd(listOf("configure"), "configure.log")
        // Configs from an older package lack settings a newer program needs (dbimport's Updates.ExceptionShutdownDelay).
        runCatching { WowConfMerge.mergeAll(layout) }
        WowSettings.apply(layout)

        step(WowRealm.Step.DATABASE, "Starting the database")
        startDatabase()

        // The auth database and ChromieCraft's come first, whichever realm starts (the accounts are
        // there). A realm whose databases are in the imported MariaDB folder is set up: dbimport is
        // not run over the user's data (the WoW app's `.imported` marker may be missing from the export).
        for (imported in listOf(Realm.CHROMIE, realm).distinct()) {
            val marker = importedMarker(imported)
            if (marker.exists()) continue
            if (File(layout.databases, imported.charactersDatabase).isDirectory && File(layout.databases, "acore_auth").isDirectory) {
                marker.writeText("${clock()}\n")
                continue
            }
            step(WowRealm.Step.IMPORT, "Setting up the ${imported.displayName} databases")
            runToEnd(listOf("dbimport", imported.key), "dbimport.log", timeoutMinutes = 60, onLine = { step(WowRealm.Step.IMPORT, it) })
            marker.writeText("${clock()}\n")
        }

        // Custom races of the WoW app's versions 1.0.44 to 1.0.48 (a Races switch it no longer has):
        // their folders still there mean the app hadn't taken them out yet (ctl.sh races, as Server.kt).
        if (File(layout.root, "races").exists() || File(layout.root, "data-races").exists()) {
            step(WowRealm.Step.MODULES, "Taking out the custom races of earlier versions")
            runToEnd(listOf("races"), "races.log", timeoutMinutes = 60)
        }

        step(WowRealm.Step.MODULES, "Matching the world to the realm's modules")
        runToEnd(listOf("modules", realm.key), "modules.log", timeoutMinutes = 60, onLine = { step(WowRealm.Step.MODULES, it) })
        runToEnd(listOf("realmlist", lanAddress() ?: "127.0.0.1"), "realmlist.log")

        step(WowRealm.Step.AUTH, "Starting the login server")
        val authLog = File(layout.logs, "auth.out")
        auth = launch(authLog, listOf("auth"))
        waitForPort(Realm.AUTH_PORT, 90, auth!!, authLog, "The login server didn't start.")

        startWorld(realm)
    }

    private suspend fun startWorld(realm: Realm) {
        step(WowRealm.Step.WORLD, "Loading ${realm.displayName}")
        val log = File(layout.logs, "world.out")
        val process = launch(log, listOf("world", realm.key), keepInput = true)
        world = process
        // Loading takes minutes on a phone. Every line of the log is looked at for the ready one.
        val deadline = clock() + 30 * 60_000L
        val ready = LineWatch(READY)
        var read = 0L
        while (true) {
            if (!process.isAlive) throw StepFailed("The world server ended (code ${process.exitValue()}) while starting.", log)
            val (text, end) = WowLogs.readFrom(log, read)
            read = end
            if (ready.feed(text)) break
            if (clock() > deadline) throw StepFailed("The world server took more than 30 minutes to start.", log)
            update { copy(message = WowLogs.tail(log, 3).lines().lastOrNull { it.isNotBlank() }?.take(160)) }
            sleep(pollMs)
        }
        update { copy(phase = WowRealm.Phase.RUNNING, step = null, message = "${realm.displayName} is running") }
        watcher = scope.launch(io) { watch(log) }
    }

    /** The programs ending while the realm should run is a failure. */
    private suspend fun watch(worldLog: File) {
        while (coroutineContext.isActive && !stopping) {
            sleep(pollMs)
            if (stopping) return
            val dead = when {
                world?.isAlive == false -> "The world server stopped (code ${world!!.exitValue()})." to worldLog
                auth?.isAlive == false -> "The login server stopped (code ${auth!!.exitValue()})." to File(layout.logs, "auth.out")
                db?.isAlive == false -> "The database stopped (code ${db!!.exitValue()})." to File(layout.logs, "mariadb.log")
                else -> null
            } ?: continue
            // (fail ends this watcher too: it finishes anyway)
            withContext(kotlinx.coroutines.NonCancellable) { lock.withLock { if (!stopping) fail(dead.first, dead.second) } }
            return
        }
    }

    private suspend fun fail(message: String, log: File?) {
        val tail = log?.let { WowLogs.tail(it, 30) }
        killAll()
        update { copy(phase = WowRealm.Phase.FAILED, step = null, message = message, error = message, log = tail) }
        onFailure(message, tail)
    }

    /** Stops the realm: world first (it saves the characters), then auth, then the database. */
    suspend fun shutDown() {
        // (the run in progress, if any, was cancelled and has let go of the lock)
        lock.withLock {
            if (db == null && auth == null && world == null && stepProcess == null) {
                if (_status.value.phase != WowRealm.Phase.FAILED) update { WowRealm.Status(realm = realm) }
                return
            }
            update { copy(phase = WowRealm.Phase.STOPPING, step = null, message = "Saving and stopping") }
            withContext(io) { killAll() }
            update { WowRealm.Status(realm = realm) }
        }
    }

    private val realm: Realm get() = _status.value.realm

    private suspend fun killAll() = withContext(io) {
        stopping = true
        watcher?.cancel()
        watcher = null
        stepProcess?.destroy()
        stepProcess = null
        world?.let { process ->
            if (process.isAlive) {
                // In a second: the command refuses 0.
                process.send("server shutdown 1")
                if (!process.waitFor(90_000)) process.destroy()
                if (!process.waitFor(15_000)) process.destroyForcibly()
            }
        }
        world = null
        auth?.let { process ->
            process.destroy()
            if (!process.waitFor(15_000)) process.destroyForcibly()
        }
        auth = null
        db?.let { process ->
            // MariaDB shuts down cleanly on SIGTERM, flushing InnoDB.
            process.destroy()
            if (!process.waitFor(60_000)) process.destroyForcibly()
        }
        db = null
    }

    /** Sends a command to the world server's console (`saveall`, without a dot). */
    fun worldCommand(command: String): Boolean = world?.send(command) == true

    private suspend fun startDatabase() {
        val log = File(layout.logs, "mariadb.log")
        val process = launch(File(layout.logs, "db.out"), listOf("db"))
        db = process
        val deadline = clock() + 120_000
        while (true) {
            if (!process.isAlive) throw StepFailed("The database didn't start.", log)
            if (runCatching { ping() }.getOrDefault(false)) return
            if (clock() > deadline) throw StepFailed("The database didn't answer in two minutes.", log)
            sleep(pollMs)
        }
    }

    private suspend fun ping(): Boolean {
        val process = runner.start(WowCtl.command(layout, loader, timeZone(), "db-ping"), File(layout.logs, "db-ping.out"), false)
        val deadline = clock() + 10_000
        while (!process.waitFor(200)) {
            if (clock() > deadline) { process.destroyForcibly(); return false }
        }
        return process.exitValue() == 0
    }

    private fun launch(log: File, args: List<String>, keepInput: Boolean = false): RealmProcess {
        log.parentFile?.mkdirs()
        return runner.start(WowCtl.command(layout, loader, timeZone(), *args.toTypedArray()), log, keepInput)
    }

    /** Runs `ctl.sh <args>` to its end; its output lines go to [onLine]. */
    private suspend fun runToEnd(args: List<String>, logName: String, timeoutMinutes: Long = 5, onLine: ((String) -> Unit)? = null) {
        val log = File(layout.logs, logName)
        log.parentFile?.mkdirs()
        log.delete()
        val process = launch(log, args)
        stepProcess = process
        val deadline = clock() + timeoutMinutes * 60_000
        var read = 0L
        fun lines() {
            val (text, end) = WowLogs.readFrom(log, read)
            read = end
            if (onLine != null) ConsoleText.plain(text).lineSequence().filter { it.isNotBlank() }.forEach { onLine(it.take(160)) }
        }
        while (!process.waitFor(pollMs)) {
            lines()
            if (!coroutineContext.isActive) { process.destroy(); throw CancellationException() }
            if (clock() > deadline) {
                process.destroy()
                if (!process.waitFor(10_000)) process.destroyForcibly()
                stepProcess = null
                throw StepFailed("Step ${args.first()} took more than $timeoutMinutes minutes.", log)
            }
        }
        lines()
        stepProcess = null
        val code = process.exitValue()
        if (code != 0) throw StepFailed(failureText(args, code, log), log)
    }

    /**
     * What a failed step says: its code, the end of its output and, since a bare exit code doesn't say which
     * command failed, the end of a run of the same step under `sh -x` (every command it ran, the last being
     * the one that failed). The steps that fail are the idempotent set-up ones, so running one again is safe.
     */
    private fun failureText(args: List<String>, code: Int, log: File): String {
        val out = WowLogs.tail(log, 12)
        val head = runCatching { log.useLines { it.filter { l -> l.isNotBlank() }.take(8).joinToString("\n") } }.getOrDefault("")
        val trace = if (args.first() in TRACEABLE) runCatching {
            val traceLog = File(layout.logs, "${log.name}.trace")
            traceLog.delete()
            val base = WowCtl.command(layout, loader, timeZone(), *args.toTypedArray())
            val process = runner.start(base.copy(argv = listOf(base.argv[0], "-x") + base.argv.drop(1)), traceLog, false)
            if (!process.waitFor(60_000)) process.destroyForcibly()
            WowLogs.tail(traceLog, 14)
        }.getOrDefault("") else ""
        val checks = runCatching { diagnostics() }.getOrDefault("")
        return buildString {
            append("Step ${args.first()} failed (code $code).")
            if (head.isNotBlank() && head != out) append("\n\nIts output began:\n").append(head)
            if (out.isNotBlank()) append("\n\nIts output ended:\n").append(out)
            if (trace.isNotBlank()) append("\n\nThe last commands it ran (sh -x):\n").append(trace)
            if (checks.isNotBlank()) append("\n\nChecks:\n").append(checks)
            append("\n\nFull logs: games/wow/files/logs/${log.name}")
        }
    }

    /**
     * What the programs a failed step ran depend on, looked at directly (the step's own output says "could
     * not populate the database" without why): the mariadb client wrapper dbimport runs for each SQL file
     * (its mode, and whether it starts), the settings dbimport reads for it, the SQL it applies, and the ends
     * of the logs the servers keep.
     */
    private fun diagnostics(): String {
        val files = layout.root.path
        val script = """
            cd "$files" || exit 0
            echo "wrapper: $(ls -l server/blizz/mariadb 2>&1)"
            echo "client:  $(server/blizz/mariadb --version 2>&1 | head -2) [exit ${'$'}?]"
            grep -hE '^(MySQLExecutable|SourceDirectory|TempDir|WorldDatabaseInfo|Updates\.)' etc/dbimport.conf 2>&1 | head -12
            echo "base sql: $(ls server/src/data/sql/base/db_world 2>&1 | head -3 | tr '
' ' ')"
            # The static client wrapper dbimport runs (libblizzmaria.so), with dbimport's own arguments and the musl preload it has set.
            echo "static client: ${'$'}{BLIZZ_MARIA:-none}"
            echo "wrapper log of the failed run: $(tail -n 12 logs/blizzmaria.log 2>&1)"
            rm -f logs/blizzmaria.log
            LD_PRELOAD="${'$'}BLIZZ_SERVER/lib/libandroidcompat.so" "${'$'}{BLIZZ_MARIA:-/nonexistent}" -h127.0.0.1 -uacore -pacore -P3310 --default-character-set=utf8mb4 --max-allowed-packet=1GB acore_world \
              < server/src/data/sql/base/db_world/achievement_category_dbc.sql > run/tmp/probe3.out 2>&1
            echo "static client with dbimport's arguments: exit ${'$'}? $(head -c 300 run/tmp/probe3.out)"
            echo "wrapper log: $(tail -n 12 logs/blizzmaria.log 2>&1)"
            # The very command dbimport runs for its first SQL file, run by hand: its error is what dbimport doesn't print.
            server/blizz/mariadb -h127.0.0.1 -P3310 -uacore -pacore -D acore_world --default-character-set=utf8mb4 \
              < server/src/data/sql/base/db_world/achievement_category_dbc.sql > run/tmp/probe.out 2>&1
            echo "apply by hand: exit ${'$'}? $(head -c 600 run/tmp/probe.out)"
            server/blizz/mariadb -h127.0.0.1 -P3310 -uacore -pacore -e 'SELECT CURRENT_USER(); SHOW GRANTS; SHOW DATABASES; SELECT COUNT(*) FROM information_schema.tables WHERE table_schema="acore_world"' > run/tmp/probe2.out 2>&1
            echo "as acore: $(head -c 900 run/tmp/probe2.out)"
            for f in logs/DBErrors.log logs/Server.log logs/mariadb.log; do
              [ -f "${'$'}f" ] && { echo "--- ${'$'}f"; tail -n 8 "${'$'}f"; }
            done
        """.trimIndent()
        val log = File(layout.logs, "diagnostics.out")
        log.delete()
        val env = WowCtl.command(layout, loader, timeZone()).env
        val process = runner.start(WowCtl.Command(listOf("/system/bin/sh", "-c", script), env + mapOf("HOME" to files), layout.run), log, false)
        if (!process.waitFor(30_000)) process.destroyForcibly()
        return WowLogs.tail(log, 40)
    }

    private suspend fun waitForPort(port: Int, seconds: Int, process: RealmProcess, log: File, message: String) {
        repeat(seconds) {
            if (!process.isAlive) throw StepFailed(message, log)
            if (portOpen(port)) return
            sleep(pollMs)
        }
        throw StepFailed(message, log)
    }

    /** The realm's databases are set up (the WoW app's markers, in the databases folder). */
    private fun importedMarker(realm: Realm) = File(layout.databases, if (realm == Realm.CHROMIE) ".imported" else ".imported-${realm.key}")

    private fun logLine(text: String) {
        runCatching { File(layout.logs, "blizzard.log").apply { parentFile?.mkdirs() }.appendText("$text\n") }
    }

    private companion object {
        /** The world server's last line of starting up. */
        val READY = Regex("\\(worldserver-daemon\\) ready")
    }
}
