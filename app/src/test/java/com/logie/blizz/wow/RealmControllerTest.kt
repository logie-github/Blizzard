package com.logie.blizz.wow

import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeout
import kotlinx.coroutines.flow.first
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File
import java.util.concurrent.CopyOnWriteArrayList

/** The realm's start and stop with a fake process runner: order of the steps, statuses, failures, commands. */
class RealmControllerTest {
    @get:Rule val tmp = TemporaryFolder()

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    @After fun tearDown() { scope.coroutineContext[kotlinx.coroutines.Job]?.cancel() }

    /** A fake program: what ctl.sh <args> does. */
    class Fake(val args: List<String>, val command: WowCtl.Command, val log: File, behavior: Behavior) : RealmProcess {
        @Volatile var alive = behavior.alive(args)
        @Volatile var code = behavior.exit(args)
        val sent = CopyOnWriteArrayList<String>()
        @Volatile var destroyed = false
        override val isAlive get() = alive
        override fun exitValue() = code
        override fun waitFor(timeoutMs: Long): Boolean { if (!alive) return true; Thread.sleep(1); return false }
        override fun send(line: String): Boolean { sent += line; if (line.startsWith("server shutdown")) alive = false; return true }
        override fun destroy() { destroyed = true; alive = false }
        override fun destroyForcibly() { destroyed = true; alive = false }
    }

    open class Behavior {
        open fun alive(args: List<String>) = args.first() in setOf("db", "auth", "world")
        open fun exit(args: List<String>) = 0
        open fun logFor(args: List<String>): String? = if (args.first() == "world") "\u001B[0mWorld initialized\n(worldserver-daemon) ready...\n" else null
    }

    class FakeRunner(val behavior: Behavior = Behavior()) : ProcessRunner {
        val started = CopyOnWriteArrayList<Fake>()
        var leftoversCalls = 0
        override fun start(command: WowCtl.Command, log: File, keepInput: Boolean): RealmProcess {
            val args = command.argv.drop(2)
            log.parentFile?.mkdirs()
            log.writeText(behavior.logFor(args) ?: "")
            return Fake(args, command, log, behavior).also { started += it }
        }
        override fun endLeftovers(layout: WowLayout) { leftoversCalls++ }
        fun ran(vararg first: String) = started.map { it.args.first() }.let { names -> first.all { it in names } }
        fun order() = started.map { it.args.first() }
        fun find(name: String) = started.first { it.args.first() == name }
    }

    private fun layout(withMarkers: Boolean = true, databases: List<String> = listOf("acore_auth", "acore_characters", "acore_world"), serverData: Boolean = true): WowLayout {
        val game = tmp.newFolder("games", "wow")
        val l = WowLayout(File(game, "files").apply { mkdirs() }, File(game, ".export").apply { mkdirs() })
        l.ctl.apply { parentFile!!.mkdirs(); writeText("SERVER=\"\$FILES/server\"\nFILES=\"\${FILES:-/data/data/com.logie.warcraft/files}\"\n") }
        for (f in listOf("bin/worldserver", "bin/mariadbd", "lib/ld-musl-aarch64.so.1")) File(l.server, f).apply { parentFile!!.mkdirs(); writeText("x") }
        File(l.databases, "mysql").mkdirs()
        for (d in databases) File(l.databases, d).mkdirs()
        if (withMarkers) File(l.databases, ".imported").writeText("1\n")
        if (serverData) for (d in listOf("dbc", "maps")) File(l.data, "$d/f").apply { parentFile!!.mkdirs(); writeText("x") }
        File(l.etc, "worldserver.conf").apply { parentFile!!.mkdirs(); writeText("LogsDir = \"/data/data/com.logie.warcraft/files/logs\"\n") }
        return l
    }

    private fun controller(l: WowLayout, r: FakeRunner, failures: MutableList<Pair<String, String?>> = mutableListOf()) = RealmController(
        layout = l, runner = r, scope = scope, timeZone = { "<+0000>-00:00" }, lanAddress = { "192.168.1.5" },
        portOpen = { port -> port != Realm.AUTH_PORT || r.started.any { it.args.first() == "auth" } },
        sleep = { delay(1) }, pollMs = 1, onFailure = { m, log -> failures += m to log },
    )

    private fun awaitPhase(c: RealmController, phase: WowRealm.Phase) = runBlocking { withTimeout(10_000) { c.status.first { it.phase == phase } } }

    @Test fun chromieCraftStartsInOrderAndIsRunning() = runBlocking {
        val l = layout()
        val r = FakeRunner()
        val c = controller(l, r)

        c.run(Realm.CHROMIE)

        assertEquals(WowRealm.Phase.RUNNING, c.status.value.phase)
        assertEquals(Realm.CHROMIE, c.status.value.realm)
        // configure, the database and its ping, the modules and realm list, auth, world; no dbimport.
        val order = r.order()
        assertEquals(listOf("configure", "db"), order.take(2))
        assertTrue("db-ping" in order)
        assertEquals(listOf("modules", "realmlist", "auth", "world"), order.dropWhile { it != "modules" }.filter { it != "db-ping" })
        assertFalse("dbimport" in order)
        assertEquals(listOf("world", "main"), r.find("world").args)
        assertEquals(listOf("modules", "main"), r.find("modules").args)
        assertEquals(listOf("realmlist", "192.168.1.5"), r.find("realmlist").args)
        val world = r.find("world").command
        assertEquals(l.root.path, world.env["FILES"])
        assertEquals(File(l.server, "lib/ld-musl-aarch64.so.1").path, world.env["BLIZZ_LDSO"])
        assertEquals(listOf("/system/bin/sh", l.blizzCtl.path), world.argv.take(2))
        assertEquals(1, r.leftoversCalls)
        c.shutDown()
    }

    @Test fun remixUsesItsKeyAndTheMainDatabasesAreNotImportedOverTheUsersData() = runBlocking {
        // Remix's databases aren't in the imported folder: dbimport makes them; ChromieCraft's (and auth) are, so it doesn't.
        val l = layout(withMarkers = false)
        val r = FakeRunner()
        val c = controller(l, r)

        c.run(Realm.REMIX)

        assertEquals(WowRealm.Phase.RUNNING, c.status.value.phase)
        assertEquals(listOf(listOf("dbimport", "remix")), r.started.map { it.args }.filter { it.first() == "dbimport" })
        assertEquals(listOf("world", "remix"), r.find("world").args)
        assertTrue(File(l.databases, ".imported").isFile)
        assertTrue(File(l.databases, ".imported-remix").isFile)
        c.shutDown()
    }

    /** Wrath++'s server package as WrathppServerPackage leaves it: its own ctl.sh and programs in server-wrathpp. */
    private fun installWrathpp(l: WowLayout) {
        l.wrathppCtl.apply { parentFile!!.mkdirs(); writeText("SERVER=\"\$FILES/server\"\nexec \"\$SERVER/bin/worldserver\"\n") }
        for (f in listOf("bin/worldserver", "lib/libandroidcompat.so")) File(l.wrathppServer, f).apply { parentFile!!.mkdirs(); writeText("x") }
    }

    @Test fun wrathppRunsItsOwnStepsByItsOwnScriptAndTheSharedOnesByTheRealms() = runBlocking {
        val l = layout()
        installWrathpp(l)
        val r = FakeRunner()
        val c = controller(l, r)

        c.run(Realm.WRATHPP)

        assertEquals(WowRealm.Phase.RUNNING, c.status.value.phase)
        val wrathppScript = listOf("/system/bin/sh", l.wrathppBlizzCtl.path)
        val realmsScript = listOf("/system/bin/sh", l.blizzCtl.path)
        // Its configs, databases, modules, realm list row and world server: Wrath++'s script, realm wrathpp.
        assertEquals(listOf("configure-realm", "wrathpp"), r.find("configure-realm").args)
        assertEquals(listOf("dbimport", "wrathpp"), r.find("dbimport").args)
        assertEquals(listOf("modules", "wrathpp"), r.find("modules").args)
        assertEquals(listOf("wrathpp-register", "192.168.1.5"), r.find("wrathpp-register").args)
        assertEquals(listOf("world", "wrathpp"), r.find("world").args)
        for (name in listOf("configure-realm", "dbimport", "modules", "wrathpp-register", "world")) {
            assertEquals(name, wrathppScript, r.find(name).command.argv.take(2))
        }
        // The shared ones (MariaDB, the realms' configure and realm list, the login server): the realms' script.
        for (name in listOf("configure", "db", "realmlist", "auth")) assertEquals(name, realmsScript, r.find(name).command.argv.take(2))
        // ChromieCraft's databases are there (marker): only Wrath++'s are made.
        assertEquals(1, r.started.count { it.args.first() == "dbimport" })
        assertTrue(File(l.databases, ".imported-wrathpp").isFile)
        // Its script, written from its package's ctl.sh with the loader rewrite.
        assertTrue(l.wrathppBlizzCtl.readText().contains("\"\$BLIZZ_LDSO\" --library-path \"\$SERVER/lib\" \"\$SERVER/bin/worldserver\""))
        assertTrue(File(l.wrathppServer, "blizz/mariadb").isFile)
        // Its world server's log is its own.
        assertTrue(File(l.logs, "wrathpp/world.out").isFile)
        val order = r.order().filter { it != "db-ping" }
        assertTrue(order.indexOf("realmlist") < order.indexOf("wrathpp-register"))
        assertTrue(order.indexOf("wrathpp-register") < order.indexOf("auth"))
        assertTrue(order.indexOf("configure") < order.indexOf("configure-realm"))
        c.shutDown()
    }

    @Test fun wrathppWithoutItsServerFailsBeforeRunningAnything() = runBlocking {
        val l = layout()
        val r = FakeRunner()
        val failures = mutableListOf<Pair<String, String?>>()
        val c = controller(l, r, failures)

        c.run(Realm.WRATHPP)

        assertEquals(WowRealm.Phase.FAILED, c.status.value.phase)
        assertTrue(c.status.value.error!!.contains("Wrath++'s server isn't installed"))
        assertTrue(r.started.isEmpty())
        assertEquals(1, failures.size)
    }

    @Test fun existingDatabasesAreNeverRebuilt() = runBlocking {
        val l = layout(withMarkers = false, databases = listOf("acore_auth", "acore_characters", "acore_characters_remix"))
        val r = FakeRunner()
        val c = controller(l, r)
        c.run(Realm.REMIX)
        assertEquals(WowRealm.Phase.RUNNING, c.status.value.phase)
        assertFalse("dbimport" in r.order())
        c.shutDown()
    }

    @Test fun stoppingSavesTheCharactersThenEndsAuthThenTheDatabase() = runBlocking {
        val l = layout()
        val r = FakeRunner()
        val c = controller(l, r)
        c.run(Realm.CHROMIE)
        val world = r.find("world"); val auth = r.find("auth"); val db = r.find("db")

        c.shutDown()

        assertEquals(listOf("server shutdown 1"), world.sent.toList())
        assertFalse(world.destroyed) // it ended by itself after the command
        assertTrue(auth.destroyed)
        assertTrue(db.destroyed)
        assertEquals(WowRealm.Phase.STOPPED, c.status.value.phase)
        assertFalse(c.worldCommand("saveall"))
    }

    @Test fun worldCommandsReachTheConsole() = runBlocking {
        val r = FakeRunner()
        val c = controller(layout(), r)
        c.run(Realm.CHROMIE)
        assertTrue(c.worldCommand("saveall"))
        assertEquals(listOf("saveall"), r.find("world").sent.toList())
        c.shutDown()
    }

    @Test fun notImportedFailsAndIsReported() = runBlocking {
        val game = tmp.newFolder("games", "wow")
        val l = WowLayout(File(game, "files").apply { mkdirs() }, File(game, ".export"))
        val failures = mutableListOf<Pair<String, String?>>()
        val c = controller(l, FakeRunner(), failures)

        c.run(Realm.CHROMIE)

        assertEquals(WowRealm.Phase.FAILED, c.status.value.phase)
        assertTrue(c.status.value.error!!.contains("imported"))
        assertEquals(1, failures.size)
    }

    @Test fun missingServerDataFails() = runBlocking {
        val failures = mutableListOf<Pair<String, String?>>()
        val r = FakeRunner()
        val c = controller(layout(serverData = false), r, failures)
        c.run(Realm.CHROMIE)
        assertEquals(WowRealm.Phase.FAILED, c.status.value.phase)
        assertTrue(c.status.value.error!!.contains("dbc"))
        assertEquals(emptyList<String>(), r.order())
    }

    @Test fun aFailedStepFailsWithTheEndOfItsLog() = runBlocking {
        val failures = mutableListOf<Pair<String, String?>>()
        val r = FakeRunner(object : Behavior() {
            override fun exit(args: List<String>) = if (args.first() == "modules") 3 else 0
            override fun logFor(args: List<String>) = if (args.first() == "modules") "line one\nERROR: cannot connect to the database\n" else super.logFor(args)
        })
        val l = layout()
        val c = controller(l, r, failures)

        c.run(Realm.CHROMIE)

        assertEquals(WowRealm.Phase.FAILED, c.status.value.phase)
        // The message names the step and its code, then the end of its output (and, run again under sh -x, the commands).
        assertTrue(c.status.value.error!!.startsWith("Step modules failed (code 3)."))
        assertTrue(c.status.value.error!!.contains("cannot connect to the database"))
        assertTrue(c.status.value.error!!.contains("Full logs: games/wow/files/logs/modules.log"))
        assertTrue(c.status.value.log!!.contains("cannot connect to the database"))
        assertEquals(1, failures.size)
        assertTrue(failures[0].second!!.contains("cannot connect"))
        // The database that was started is stopped again; nothing else started.
        assertTrue(r.find("db").destroyed)
        assertFalse(r.ran("auth"))
    }

    @Test fun theWorldServerEndingWhileLoadingFails() = runBlocking {
        val failures = mutableListOf<Pair<String, String?>>()
        val r = FakeRunner(object : Behavior() {
            override fun logFor(args: List<String>) = if (args.first() == "world") "Loading maps\nCrash\n" else null
            override fun exit(args: List<String>) = if (args.first() == "world") 139 else 0
        })
        val c = controller(layout(), r, failures)
        // (the fake world process is alive when it starts; end it as the controller waits)
        val job = scope.launch { c.run(Realm.CHROMIE) }
        withTimeout(10_000) { while (!r.ran("world")) delay(1) }
        r.find("world").alive = false
        job.join()
        assertEquals(WowRealm.Phase.FAILED, c.status.value.phase)
        assertTrue(c.status.value.error!!.contains("139"))
        assertTrue(c.status.value.log!!.contains("Crash"))
        assertTrue(r.find("auth").destroyed && r.find("db").destroyed)
    }

    @Test fun aProgramEndingWhileRunningFailsTheRealm() = runBlocking {
        val failures = mutableListOf<Pair<String, String?>>()
        val r = FakeRunner()
        val c = controller(layout(), r, failures)
        c.run(Realm.CHROMIE)
        assertEquals(WowRealm.Phase.RUNNING, c.status.value.phase)

        r.find("auth").alive = false
        r.find("auth").code = 9
        awaitPhase(c, WowRealm.Phase.FAILED)

        assertTrue(c.status.value.error!!.contains("login server"))
        assertEquals(1, failures.size)
        assertTrue(r.find("db").destroyed)
    }

    @Test fun cancellingAStartStopsWhatItStarted() = runBlocking {
        // A world server that never says ready.
        val r = FakeRunner(object : Behavior() { override fun logFor(args: List<String>): String? = null })
        val c = controller(layout(), r)
        val job = scope.launch { c.run(Realm.CHROMIE) }
        withTimeout(10_000) { while (!r.ran("world")) delay(1) }
        assertEquals(WowRealm.Step.WORLD, c.status.value.step)

        job.cancelAndJoin()
        c.shutDown()

        assertTrue(r.find("world").sent.contains("server shutdown 1") || r.find("world").destroyed)
        assertTrue(r.find("auth").destroyed)
        assertTrue(r.find("db").destroyed)
        assertEquals(WowRealm.Phase.STOPPED, c.status.value.phase)
    }

    @Test fun customRacesOfEarlierVersionsAreTakenOutBeforeTheModulesStepLikeTheWowApp() = runBlocking {
        val l = layout()
        File(l.root, "data-races").mkdirs()
        val r = FakeRunner()
        val c = controller(l, r)

        c.run(Realm.CHROMIE)

        assertEquals(WowRealm.Phase.RUNNING, c.status.value.phase)
        assertEquals(listOf("races", "modules", "realmlist", "auth", "world"), r.order().dropWhile { it != "races" }.filter { it != "db-ping" })
        c.shutDown()
    }

    @Test fun settingsAreAppliedAfterConfigure() = runBlocking {
        val l = layout()
        File(l.etc, "worldserver.conf").writeText("MoveMaps.Enable = 1\nvmap.enableLOS = 1\n")
        val r = FakeRunner()
        val c = controller(l, r)

        c.run(Realm.CHROMIE)

        // (no mmaps or vmaps in the data)
        assertEquals("MoveMaps.Enable = 0\nvmap.enableLOS = 0\nvmap.enableHeight = 0\nvmap.enableIndoorCheck = 0", File(l.etc, "worldserver.conf").readText().trim())
        c.shutDown()
    }

    @Test fun staleFilesAreClearedAndPathsMovedBeforeStarting() = runBlocking {
        val l = layout()
        File(l.run, "mysqld.pid").apply { parentFile!!.mkdirs(); writeText("123") }
        l.manifest.writeText("{\"sourceFilesDir\":\"/data/user/0/com.logie.warcraft/files\"}")
        val r = FakeRunner()
        val c = controller(l, r)

        c.run(Realm.CHROMIE)

        assertFalse(File(l.run, "mysqld.pid").exists())
        // (then the settings of WowSettings: the data here has no vmaps or mmaps)
        assertTrue(File(l.etc, "worldserver.conf").readText().startsWith("LogsDir = \"${l.root.path}/logs\"\n"))
        assertEquals("${l.root.path}\n", l.rewriteMarker.readText())
        assertNotNull(l.blizzCtl.takeIf { it.isFile })
        c.shutDown()
    }
}
