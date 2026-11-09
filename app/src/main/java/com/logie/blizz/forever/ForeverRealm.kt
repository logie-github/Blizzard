package com.logie.blizz.forever

import android.content.Context
import com.logie.blizz.wow.ProcessRunner
import com.logie.blizz.wow.RealmProcess
import com.logie.blizz.wow.SystemRunner
import com.logie.blizz.wow.WowCtl
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import java.io.File

/**
 * The Forever realm on the phone (TrinityCore's "forever" branch, built by
 * `realm/scripts/compile-trinity-forever.sh`, downloaded as a package by [ForeverServerPackage]).
 * It runs entirely offline: its own MariaDB, the Battle.net login server and the world server, all
 * on 127.0.0.1, with a world database the branch built (converted from VMaNGOS), never Blizzard's.
 *
 * The package's programs have `/data/data/com.logie.blizz/files/forever/server/lib/ld-musl-aarch64.so.1`
 * baked in as their ELF interpreter (set at build time, [ForeverLayout.root]), so, unlike the
 * imported WoW realms ([WowCtl]), they run from this app's own folder with no path rewrite: `ctl.sh`
 * starts them as `"$SERVER/bin/<name>"` and the loader is where they expect it.
 *
 * NOT run on a phone. The command building ([ForeverCtl]) is unit-tested; the realm itself needs
 * the compiled package, the client's map data and a phone.
 */
object ForeverRealm {
    enum class Phase { STOPPED, STARTING, RUNNING, STOPPING, FAILED }
    enum class Step { CONFIGURING, DATABASE, LOGIN, WORLD }

    data class Status(
        val phase: Phase = Phase.STOPPED,
        val step: Step? = null,
        val message: String? = null,
        val error: String? = null,
    )

    private val _status = MutableStateFlow(Status())
    val status: StateFlow<Status> = _status

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    private val runner: ProcessRunner = SystemRunner()
    @Volatile private var db: RealmProcess? = null
    @Volatile private var login: RealmProcess? = null
    @Volatile private var world: RealmProcess? = null

    /** Whether the server package is unpacked and ready to run. */
    fun installed(context: Context) = ForeverLayout.of(context).ctl.isFile

    /** The world server has reached "ready" (printed when the realm is up). */
    private val ready = Regex("""World initialized in|\(worldserver-daemon\) ready""")

    /**
     * Brings the realm up: MariaDB, then the login server, then the world server, waiting for each. The realm is
     * offered at [clientBuild] (the client lists only realms of its own build) and the game [account] (e-mail,
     * password) is made sure of once the world server is up. Returns at once; [status] follows. Call off the main thread.
     */
    fun start(context: Context, clientBuild: Int? = null, account: Pair<String, String>? = null) {
        if (_status.value.phase == Phase.STARTING || _status.value.phase == Phase.RUNNING) return
        val layout = ForeverLayout.of(context)
        _status.value = Status(Phase.STARTING, Step.CONFIGURING, "Setting up the realm")
        scope.launch {
            try {
                runner.endLeftovers(layout.wowLayout, ForeverCtl.PID_FILES)
                ForeverCtl.makeExecutable(layout)

                run(layout, "configure")

                _status.value = Status(Phase.STARTING, Step.DATABASE, "Starting the database")
                db = startProcess(layout, "db", layout.log("mariadb-run"))
                awaitDatabase(layout)
                if (clientBuild != null) run(layout, "realm-build", clientBuild.toString())

                _status.value = Status(Phase.STARTING, Step.LOGIN, "Starting the login server")
                login = startProcess(layout, "bnetserver", layout.log("bnetserver"))

                _status.value = Status(Phase.STARTING, Step.WORLD, "Starting the world (first time: several minutes)")
                world = startProcess(layout, "worldserver", layout.log("worldserver"), keepInput = true)
                awaitWorld(layout)
                account?.let { (name, password) -> ensureAccount(name, password) }

                _status.value = Status(Phase.RUNNING, null, "Realm running")
            } catch (e: Throwable) {
                _status.value = Status(Phase.FAILED, _status.value.step, error = e.message ?: e.javaClass.simpleName)
                stop(context)
            }
        }
    }

    /**
     * Makes the server's map data from the client (dbc, maps, vmaps), off the main thread. Pathfinding (mmaps) is
     * skipped: it takes hours on a phone, and the realm runs without it (MoveMaps off in ctl.sh configure). [onStep]
     * gets a short line per step. Throws on failure.
     */
    fun extractData(context: Context, clientDir: File, onStep: (String) -> Unit) {
        val layout = ForeverLayout.of(context)
        ForeverCtl.makeExecutable(layout)
        onStep("Reading the game data (maps)")
        run(layout, "maps", clientDir.path)
        onStep("Reading the game data (collision)")
        run(layout, "vmaps", clientDir.path)
        onStep("Putting the game data in place")
        run(layout, "data-done")
    }

    /** Makes a game account (its name is an e-mail), or sets its password. Off the main thread. */
    fun account(context: Context, name: String, password: String) {
        run(ForeverLayout.of(context), "account", name, password)
    }

    fun stop(context: Context) {
        val layout = ForeverLayout.of(context)
        _status.value = Status(Phase.STOPPING, message = "Stopping")
        world?.let { it.send("saveall"); it.send("server shutdown 1"); it.waitFor(30_000); it.destroy() }
        login?.destroy()
        // MariaDB flushes on a clean shutdown; the control command asks it, then the process ends.
        runCatching { run(layout, "db-stop") }
        db?.let { it.waitFor(30_000); it.destroy() }
        world = null; login = null; db = null
        _status.value = Status(Phase.STOPPED)
    }

    private fun startProcess(layout: ForeverLayout, arg: String, log: File, keepInput: Boolean = false): RealmProcess =
        runner.start(ForeverCtl.command(layout, arg), log, keepInput)

    /**
     * Makes sure the game account exists with this password, through the running world server's console
     * (TrinityCore's `bnetaccount create`, which also makes its game account; "already exists" is harmless). The
     * console splits on spaces, so a name or password with one is left out (the game asks at its login screen).
     */
    private fun ensureAccount(name: String, password: String) {
        if (name.isBlank() || password.isBlank() || '@' !in name || (name + password).any(Char::isWhitespace)) return
        world?.send("bnetaccount create $name $password")
        world?.send("bnetaccount set password $name $password $password")
    }

    /** Runs a one-shot control command to its end; a failure carries the last line it printed (the reason). */
    private fun run(layout: ForeverLayout, vararg args: String) {
        val log = layout.log(args.first())
        val process = runner.start(ForeverCtl.command(layout, *args), log, false)
        if (!process.waitFor(20 * 60_000L)) { process.destroyForcibly(); throw IllegalStateException("'${args.first()}' timed out") }
        if (process.exitValue() != 0) {
            val reason = runCatching { log.readLines().lastOrNull { it.isNotBlank() }?.trim() }.getOrNull()
            throw IllegalStateException(reason ?: "'${args.first()}' failed (see logs/${args.first()}.log)")
        }
    }

    private fun awaitDatabase(layout: ForeverLayout) {
        repeat(120) {
            val ping = runner.start(ForeverCtl.command(layout, "db-ping"), layout.log("db-ping"), false)
            if (ping.waitFor(5_000) && ping.exitValue() == 0) return
            if (db?.isAlive != true) throw IllegalStateException("The database stopped (see logs/mariadb.log)")
            Thread.sleep(1_000)
        }
        throw IllegalStateException("The database didn't come up")
    }

    private fun awaitWorld(layout: ForeverLayout) {
        val log = layout.log("worldserver")
        val deadline = System.currentTimeMillis() + 20 * 60_000L
        while (System.currentTimeMillis() < deadline) {
            if (world?.isAlive != true) throw IllegalStateException("The world server stopped (see logs/worldserver.log)")
            if (runCatching { log.readText() }.getOrDefault("").let(ready::containsMatchIn)) return
            Thread.sleep(1_000)
        }
        throw IllegalStateException("The world server didn't reach ready")
    }
}
