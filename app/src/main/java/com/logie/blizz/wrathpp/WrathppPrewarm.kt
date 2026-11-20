package com.logie.blizz.wrathpp

import android.content.Context
import android.os.PowerManager
import com.logie.blizz.wow.Realm
import com.logie.blizz.wow.WowLayout
import com.logie.blizz.wow.WowRealm
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import java.io.File
import java.security.MessageDigest
import java.util.concurrent.locks.ReentrantLock

/**
 * Wrath++ made ready before Play (the user, 20 November 2026: "It still takes several minutes. Find a way. Invent one even, to
 * use these resources"). Play used to do everything after the tap, one thing after another: Wrath++'s setup ([WrathppSetup.run]:
 * the server package, the looks, the imports, the creator), then the realm's cold start (the database, the login server, the
 * world server and playerbots), then the game. When the app opens, or has just been updated, and Wrath++ was the last game
 * played, the setup and then the realm start in the background, on the phone's idle cores, so Play finds them done or under way
 * and joins them instead of starting from nothing.
 *
 * Nothing is played on stale data:
 *  - Play runs the setup again unless the background run finished for the same inputs ([Core.inputs]: the app's build, the
 *    app's own files and settings, the imports and the files found to import) less than [FRESH_MS] ago;
 *  - a running Wrath++ realm is stopped (and Play starts it again) when the server files it read when it started ([Core.serverFiles]:
 *    the server package, the tables in its `share/dbc`, the starting areas' package) were changed since, by anything.
 * Another realm running (Wrath+) is never touched, and nothing starts in battery saver.
 */
object WrathppPrewarm {
    /** How long a background setup stands for Play's own. */
    const val FRESH_MS = 10 * 60 * 1000L
    private const val PLAYED = "wrathpp-played"

    /** What the background run and Play need from the realm. */
    interface Realms {
        /** The realm running or starting, or null. */
        fun current(): String?
        fun start()
        fun stopAndWait()
    }

    /**
     * The rules, apart from Android (unit-tested): [setup] is Wrath++'s setup, [inputs] and [serverFiles] fingerprints, [log]
     * what Play's start report shows of it.
     */
    class Core(
        private val setup: ((String, Float?) -> Unit) -> Unit,
        private val realms: Realms,
        private val inputs: () -> String,
        private val serverFiles: () -> String,
        private val clock: () -> Long = System::currentTimeMillis,
        private val log: (String) -> Unit = {},
    ) {
        private val running = ReentrantLock()
        @Volatile private var doneFor: String? = null
        @Volatile private var doneAt = 0L
        /** What the server files were when this core started the realm (or Play let it run). */
        @Volatile private var realmRead: String? = null
        @Volatile var progress: Pair<String, Float?>? = null
            private set

        /** The background run: the setup, then the realm when none is running. Returns false when a run was already going. */
        fun background(): Boolean {
            if (!running.tryLock()) return false
            try {
                val started = clock()
                runSetup { m, f -> progress = m to f }
                log("background: setup ${(clock() - started) / 1000.0} s")
                if (realms.current() == null) {
                    realmRead = serverFiles()
                    realms.start()
                    log("background: realm started")
                }
            } catch (e: Exception) {
                log("background: ${e.message ?: e.javaClass.simpleName}")
            } finally {
                progress = null
                running.unlock()
            }
            return true
        }

        /** Play's setup: waits for a background run under way, skips one done for the same inputs, else runs it; then the realm check. */
        fun play(say: (String, Float?) -> Unit) {
            val started = clock()
            if (running.isLocked && !running.isHeldByCurrentThread) {
                while (running.isLocked) {
                    progress?.let { (m, f) -> say(m, f) }
                    Thread.sleep(200)
                }
                log("play: joined the background setup (${(clock() - started) / 1000.0} s)")
            }
            running.lock()
            try {
                val now = inputs()
                if (doneFor == now && clock() - doneAt < FRESH_MS) {
                    log("play: setup done in the background for the same files: not run again")
                } else {
                    val t = clock()
                    runSetup(say)
                    log("play: setup ${(clock() - t) / 1000.0} s")
                }
                val files = serverFiles()
                if (realms.current() == "wrathpp") {
                    if (realmRead != files) {
                        log("play: the realm read other server files than these: stopped, started again")
                        realms.stopAndWait()
                    } else {
                        log("play: the realm already up or starting, on these server files")
                    }
                }
                realmRead = files
            } finally {
                running.unlock()
            }
        }

        private fun runSetup(say: (String, Float?) -> Unit) {
            val now = inputs()
            doneFor = null
            setup(say)
            doneFor = now
            doneAt = clock()
        }
    }

    @Volatile private var core: Core? = null
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    private fun core(app: Context): Core = core ?: synchronized(this) {
        core ?: Core(
            setup = { say -> WrathppSetup.run(app, say) },
            realms = object : Realms {
                override fun current(): String? {
                    val s = WowRealm.status.value
                    return if (s.phase == WowRealm.Phase.STARTING || s.phase == WowRealm.Phase.RUNNING) s.realm.key else null
                }
                override fun start() = WowRealm.start(app, Realm.WRATHPP)
                override fun stopAndWait() = runBlocking { WowRealm.stopAndWait(app) }
            },
            inputs = { inputs(app) },
            serverFiles = { serverFiles(WowLayout.of(app)) },
            log = { line -> playLog(app, line) },
        ).also { core = it }
    }

    /** At the app's start and after it was updated: Wrath++ made ready in the background when it was the last game played. */
    fun start(context: Context) {
        val app = context.applicationContext
        if (!File(app.filesDir, PLAYED).isFile) return
        if (runCatching { (app.getSystemService(Context.POWER_SERVICE) as PowerManager).isPowerSaveMode }.getOrDefault(false)) return
        val layout = WowLayout.of(app)
        if (!layout.hasWrathppServer() || !WrathppClient.isMade(layout.wrathppClient)) return
        val other = WowRealm.status.value.let { s ->
            (s.phase == WowRealm.Phase.STARTING || s.phase == WowRealm.Phase.RUNNING || s.phase == WowRealm.Phase.STOPPING) && s.realm != Realm.WRATHPP
        }
        if (other) return
        val c = core(app)
        scope.launch { c.background() }
    }

    /** Play's Wrath++ setup ([com.logie.blizz.game.WowPlay]'s): see [Core.play]. */
    fun setUp(context: Context, say: (String, Float?) -> Unit) {
        val app = context.applicationContext
        runCatching { File(app.filesDir, PLAYED).writeText(System.currentTimeMillis().toString()) }
        runCatching { File(playLogFile(app).path).delete() }
        core(app).play(say)
    }

    // ---- fingerprints

    private fun sha(text: String): String =
        MessageDigest.getInstance("SHA-256").digest(text.toByteArray()).joinToString("") { "%02x".format(it) }

    /** Name, size and time of each file under [dir] (to [depth] folders down), sorted. */
    internal fun listing(dir: File?, depth: Int, skip: (File) -> Boolean = { false }): String {
        if (dir == null || !dir.exists()) return "-"
        val out = StringBuilder()
        fun walk(f: File, d: Int, rel: String) {
            val children = f.listFiles()?.sortedBy { it.name } ?: return
            for (c in children) {
                if (skip(c)) continue
                out.append(rel).append(c.name).append(' ').append(if (c.isDirectory) "d" else c.length()).append(' ').append(c.lastModified()).append('\n')
                if (c.isDirectory && d > 0) walk(c, d - 1, "$rel${c.name}/")
            }
        }
        walk(dir, depth, "")
        return out.toString()
    }

    /** The big folders of the app's own (games, servers, logs): not settings, never read by Wrath++'s setup as an input of its own. */
    private val HEAVY = Regex("^(server|client|data|mysql|logs|run|zones|etc|backups|warsmash|spp|felsong|octo|turtle|legion|games|cache|tmp|wine|imagefs|rootfs|.*-wrathpp)(-.*)?$")

    /** What Wrath++'s setup is made from: the app's build, its own settings and small files, the imports, the files found to import. */
    internal fun inputs(app: Context): String = sha(buildString {
        append(com.logie.blizz.BuildConfig.VERSION_CODE).append('\n')
        append(listing(app.filesDir, 2) { it.isDirectory && HEAVY.matches(it.name) })
        append(listing(File(app.applicationInfo.dataDir, "shared_prefs"), 0))
        for (store in listOf(WrathppRalia.store(app), WrathppBody.store(app), WrathppUndead.store(app))) append(listing(store, 4))
        for (found in listOf(runCatching { ImportFinder.find("ralia.zip") }.getOrNull(), runCatching { ImportFinder.find(*WrathppBody.NAMES) }.getOrNull())) {
            append(found?.let { "${it.path} ${it.length()} ${it.lastModified()}" } ?: "-").append('\n')
        }
    })

    /** What the realm reads that Wrath++'s setup writes: the server package's marker, the tables in its share/dbc, the starting areas'. */
    internal fun serverFiles(layout: WowLayout): String = sha(buildString {
        append(listing(File(layout.wrathppServer, "share/dbc"), 0))
        append(runCatching { File(layout.wrathppServer, WrathppServerPackage.MARKER).readText() }.getOrDefault("-")).append('\n')
        append(listing(layout.zones, 0))
        append(runCatching { File(layout.zones, "TAG").readText() }.getOrDefault("-")).append('\n')
    })

    // ---- what Play's start report shows

    private fun playLogFile(app: Context): File = File(WowLayout.of(app).realmLogs(Realm.WRATHPP), "play.log")

    private fun playLog(app: Context, line: String) {
        runCatching { playLogFile(app).apply { parentFile?.mkdirs() }.appendText("$line\n") }
    }

    /** The last Play's lines, for the start report. */
    fun lastPlay(context: Context): String =
        runCatching { playLogFile(context.applicationContext).readText().trim() }.getOrNull()?.takeIf { it.isNotEmpty() } ?: "-"
}
