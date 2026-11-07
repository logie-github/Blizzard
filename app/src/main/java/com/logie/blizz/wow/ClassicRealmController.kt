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

/** What [WowRealm] holds of the realm it started: stopping it, and the world server's console. */
internal interface RealmRun {
    suspend fun shutDown()
    fun worldCommand(command: String): Boolean
}

/**
 * What differs between the realms this controller runs: OctoWoW's (`realmd` and `mangosd`) and
 * Legion's (LegionCore: `bnetserver` and `worldserver`). Both are the WoW app's own `ctl.sh` of a MariaDB, a login
 * server and a world server.
 */
internal class RealmSpec(
    val realm: Realm,
    val name: String,
    /** The imported folder as the person knows it, for messages (`games/wow_octowow/files/turtle`). */
    val folder: String,
    val loginProgram: String,
    val worldProgram: String,
    val loginLog: String,
    val worldLog: String,
    val worldConf: String,
    /** The ports that say the login server is up (all of them), and every port the realm holds. */
    val loginPorts: List<Int>,
    val allPorts: List<Int>,
    val pidFiles: List<String>,
    val ready: Regex,
    val fatal: List<Pair<Regex, String>>,
    val worldMinutes: Long,
    val imported: (WowLayout) -> Boolean,
    val noData: String,
    /** The login database's name for `ctl.sh sql`, and the row that tells the client where the world is. */
    val realmSql: (address: String) -> Pair<String, String>,
    /** Settings the app owns in the world server's conf (given which data parts exist). */
    val worldSettings: (vmaps: Boolean, mmaps: Boolean) -> Map<String, String>,
    /** Settings for other confs, by file name (relative to etc/), written after `configure`. */
    val otherConfs: (address: String) -> Map<String, Map<String, String>> = { emptyMap() },
    /** Programs whose own `ctl.sh` never writes a pid file: conf file (in etc/) to the pid file's name, set here so a program left running by an ended app is found and stopped. */
    val pidConfs: Map<String, String> = emptyMap(),
    /** A step to run once after configure when [needsStep] says so (Legion's client patch). */
    val extra: List<Pair<String, (WowLayout) -> List<String>?>> = emptyList(),
)

/**
 * Starts and stops one of those realms from Blizzard's copy of the files the World of Warcraft app exported,
 * the way the WoW app's servers for them do: its own MariaDB, the login server and the world
 * server, each a program of the realm's `ctl.sh`, run through musl's loader ([WowCtl]: its
 * `"$SERVER/bin/<name>"` calls are the same shape as ChromieCraft's). Stopping saves the characters first
 * (`server shutdown`).
 *
 * Everything outside (processes, time, ports) is passed in, so tests run it with a fake runner.
 * Only that fake-runner behaviour is verified; the real programs have never run from Blizzard's folder.
 */
internal class ClassicRealmController(
    private val spec: RealmSpec,
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
    private val _status: MutableStateFlow<WowRealm.Status> = MutableStateFlow(WowRealm.Status(realm = spec.realm)),
) : RealmRun {
    val status: StateFlow<WowRealm.Status> = _status

    private val lock = Mutex()
    private var db: RealmProcess? = null
    private var login: RealmProcess? = null
    private var world: RealmProcess? = null
    @Volatile private var stepProcess: RealmProcess? = null
    @Volatile private var stopping = false
    private var watcher: Job? = null
    private lateinit var loader: File

    private class StepFailed(message: String, val log: File? = null) : Exception(message)

    private fun update(change: WowRealm.Status.() -> WowRealm.Status) { _status.value = _status.value.change() }

    private fun step(step: WowRealm.Step, message: String? = null) =
        update { copy(phase = WowRealm.Phase.STARTING, step = step, message = message, error = null, log = null) }

    /** Brings the realm up. Returns when it is up or has failed. Cancelling it ends what it started. */
    suspend fun run() = lock.withLock {
        withContext(io) {
            try {
                stopping = false
                _status.value = WowRealm.Status(phase = WowRealm.Phase.STARTING, step = WowRealm.Step.PREPARING, realm = spec.realm)
                up()
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

    private suspend fun up() {
        step(WowRealm.Step.PREPARING, "Checking the imported realm")
        if (!spec.imported(layout)) {
            throw StepFailed("${spec.name} isn't imported completely (the server's programs or databases are missing). Export it again from the World of Warcraft app (${spec.name}'s zip) and import it.")
        }
        val prefix = layout.root.parentFile!!.path
        val moved = WowPathRewrite.rewrite(layout, WowPathRewrite.oldPrefixes(WowExportInfo.sourceFilesDir(layout)), prefix)
        if (moved.changed) logLine("Paths moved to $prefix: ${moved.filesRewritten.size} files, ${moved.linksRewritten.size} links")
        loader = WowCtl.prepare(layout)
        // The programs name their old app's folder inside (a modules folder the world server reads): Blizzard's own, same length.
        val patched = CompiledPaths.fix(layout)
        if (patched > 0) logLine("The programs' compiled-in folder changed to Blizzard's: $patched places")
        runner.endLeftovers(layout, spec.pidFiles)
        for (name in spec.pidFiles + listOf("mysqld.sock", "mysqld.sock.lock")) File(layout.run, name).delete()
        if (!layout.hasServerData()) {
            throw StepFailed(spec.noData)
        }
        busyPort()?.let { throw StepFailed("Port $it is taken by another program (the other realm still running?). Stop it and try again.") }

        step(WowRealm.Step.CONFIGURING, "Writing the realm's settings")
        runToEnd(listOf("configure"), "configure.log")
        applySettings()
        for ((step, args) in spec.extra) {
            val a = args(layout) ?: continue
            step(WowRealm.Step.CONFIGURING, step)
            runToEnd(a, "${a.first()}.log", timeoutMinutes = 10)
        }

        step(WowRealm.Step.DATABASE, "Starting the database")
        startDatabase()
        setRealmList()

        step(WowRealm.Step.AUTH, "Starting the login server")
        val loginLog = File(layout.logs, spec.loginLog)
        login = launch(loginLog, listOf(spec.loginProgram))
        for (port in spec.loginPorts) waitForPort(port, 90, login!!, loginLog, "The login server didn't start.")

        startWorld()
    }

    /** Settings the app owns in the live configs: what this phone's data parts allow, and a realm for one player. */
    private fun applySettings() {
        val vmaps = File(layout.data, "vmaps").list()?.isNotEmpty() == true
        val mmaps = File(layout.data, "mmaps").list()?.isNotEmpty() == true
        val world = File(layout.etc, spec.worldConf)
        for ((key, value) in spec.worldSettings(vmaps, mmaps)) setConf(world, key, value)
        val address = lanAddress() ?: "127.0.0.1"
        for ((file, settings) in spec.otherConfs(address)) for ((key, value) in settings) setConf(File(layout.etc, file), key, value)
        for ((file, pid) in spec.pidConfs) setConf(File(layout.etc, file), "PidFile", "\"${File(layout.run, pid).path}\"")
    }

    /** The realm's row in the login database: the client connects to 127.0.0.1 (or the Wi-Fi address). */
    private suspend fun setRealmList() {
        val (database, sql) = spec.realmSql(lanAddress() ?: "127.0.0.1")
        val base = WowCtl.command(layout, loader, timeZone(), "sql", database)
        val script = "printf '%s\\n' \"\$SQL\" | " + base.argv.joinToString(" ") { "'" + it.replace("'", "'\\''") + "'" }
        val log = File(layout.logs, "realmlist.log")
        log.delete()
        val process = runner.start(WowCtl.Command(listOf("/system/bin/sh", "-c", script), base.env + mapOf("SQL" to sql), base.directory), log, false)
        val deadline = clock() + 60_000
        while (!process.waitFor(200)) {
            if (clock() > deadline) { process.destroyForcibly(); throw StepFailed("Setting the realm list took more than a minute.", log) }
        }
        if (process.exitValue() != 0) throw StepFailed("Setting the realm list failed (code ${process.exitValue()}).", log)
    }

    private suspend fun startWorld() {
        step(WowRealm.Step.WORLD, "Loading ${spec.name}")
        val log = File(layout.logs, spec.worldLog)
        val process = launch(log, listOf(spec.worldProgram), keepInput = true)
        world = process
        // The first start applies the realm's database updates (minutes more on a phone).
        val deadline = clock() + spec.worldMinutes * 60_000L
        val ready = LineWatch(spec.ready)
        var read = 0L
        while (true) {
            if (!process.isAlive) throw StepFailed("The world server ended (code ${process.exitValue()}) while starting.", log)
            val (text, end) = WowLogs.readFrom(log, read)
            read = end
            ConsoleText.plain(text).lineSequence().firstNotNullOfOrNull { fatal(spec, it) }?.let { throw StepFailed(it, log) }
            if (ready.feed(text)) break
            if (clock() > deadline) throw StepFailed("The world server took more than ${spec.worldMinutes} minutes to start.", log)
            update { copy(message = WowLogs.tail(log, 3).lines().lastOrNull { it.isNotBlank() }?.take(160)) }
            sleep(pollMs)
        }
        update { copy(phase = WowRealm.Phase.RUNNING, step = null, message = "${spec.name} is running") }
        watcher = scope.launch(io) { watch(log) }
    }

    private suspend fun watch(worldLog: File) {
        while (coroutineContext.isActive && !stopping) {
            sleep(pollMs)
            if (stopping) return
            val dead = when {
                world?.isAlive == false -> "The world server stopped (code ${world!!.exitValue()})." to worldLog
                login?.isAlive == false -> "The login server stopped (code ${login!!.exitValue()})." to File(layout.logs, spec.loginLog)
                db?.isAlive == false -> "The database stopped (code ${db!!.exitValue()})." to File(layout.logs, "mariadb.log")
                else -> null
            } ?: continue
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

    /** Stops the realm: world first (it saves the characters), then the login server, then the database. */
    override suspend fun shutDown() {
        lock.withLock {
            if (db == null && login == null && world == null && stepProcess == null) {
                if (_status.value.phase != WowRealm.Phase.FAILED) update { WowRealm.Status(realm = spec.realm) }
                return
            }
            update { copy(phase = WowRealm.Phase.STOPPING, step = null, message = "Saving and stopping") }
            withContext(io) { killAll() }
            update { WowRealm.Status(realm = spec.realm) }
        }
    }

    private suspend fun killAll() = withContext(io) {
        stopping = true
        watcher?.cancel()
        watcher = null
        stepProcess?.destroy()
        stepProcess = null
        world?.let { process ->
            if (process.isAlive) {
                process.send("server shutdown 1")
                if (!process.waitFor(90_000)) process.destroy()
                if (!process.waitFor(15_000)) process.destroyForcibly()
            }
        }
        world = null
        login?.let { process ->
            process.destroy()
            if (!process.waitFor(15_000)) process.destroyForcibly()
        }
        login = null
        db?.let { process ->
            process.destroy()
            if (!process.waitFor(60_000)) process.destroyForcibly()
        }
        db = null
    }

    override fun worldCommand(command: String): Boolean = world?.send(command) == true

    private suspend fun startDatabase() {
        val log = File(layout.logs, "mariadb.log")
        val process = launch(File(layout.logs, "db.out"), listOf("db"))
        db = process
        val deadline = clock() + 180_000
        while (true) {
            if (!process.isAlive) throw StepFailed("The database didn't start.", log)
            if (runCatching { ping() }.getOrDefault(false)) return
            if (clock() > deadline) throw StepFailed("The database didn't answer in three minutes.", log)
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

    private suspend fun runToEnd(args: List<String>, logName: String, timeoutMinutes: Long = 5) {
        val log = File(layout.logs, logName)
        log.parentFile?.mkdirs()
        log.delete()
        val process = launch(log, args)
        stepProcess = process
        val deadline = clock() + timeoutMinutes * 60_000
        while (!process.waitFor(pollMs)) {
            if (!coroutineContext.isActive) { process.destroy(); throw CancellationException() }
            if (clock() > deadline) {
                process.destroy()
                if (!process.waitFor(10_000)) process.destroyForcibly()
                stepProcess = null
                throw StepFailed("Step ${args.first()} took more than $timeoutMinutes minutes.", log)
            }
        }
        stepProcess = null
        val code = process.exitValue()
        if (code != 0) throw StepFailed("Step ${args.first()} failed (code $code).\n\n${WowLogs.tail(log, 12)}\n\nFull logs: ${spec.folder}/logs/${log.name}", log)
    }

    private suspend fun waitForPort(port: Int, seconds: Int, process: RealmProcess, log: File, message: String) {
        repeat(seconds) {
            if (!process.isAlive) throw StepFailed(message, log)
            if (portOpen(port)) return
            sleep(pollMs)
        }
        throw StepFailed(message, log)
    }

    /** One of the realm's ports already taken (by another program, or the other realm). */
    private fun busyPort(): Int? = spec.allPorts.firstOrNull { portOpen(it) }

    private fun logLine(text: String) {
        runCatching { File(layout.logs, "blizzard.log").apply { parentFile?.mkdirs() }.appendText("$text\n") }
    }

    companion object {
        /** A fatal line of the world server's log, said for the person, or null. */
        fun fatal(spec: RealmSpec, line: String): String? = spec.fatal.firstOrNull { it.first.containsMatchIn(line) }?.second

        /** `Key = value` in a config file: changed in place, or added. */
        fun setConf(file: File, key: String, value: String) {
            if (!file.isFile) return
            val line = Regex("^${Regex.escape(key)}\\s*=.*$", RegexOption.MULTILINE)
            val text = file.readText()
            val updated = if (line.containsMatchIn(text)) line.replace(text) { "$key = $value" } else text.trimEnd('\n') + "\n$key = $value\n"
            if (updated != text) file.writeText(updated)
        }
    }
}
