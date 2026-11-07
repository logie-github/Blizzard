package com.logie.blizz.wow

import com.logie.blizz.game.OctoClientSetup
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.runBlocking
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

/** OctoWoW's realm with a fake process runner: the steps' order, the statuses, the commands, and the client's settings. */
class OctoRealmTest {
    @get:Rule val tmp = TemporaryFolder()
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    @After fun tearDown() { scope.coroutineContext[kotlinx.coroutines.Job]?.cancel() }

    private class OctoBehavior : RealmControllerTest.Behavior() {
        override fun alive(args: List<String>) = args.first() in setOf("db", "realmd", "mangosd")
        override fun logFor(args: List<String>): String? = if (args.first() == "mangosd") "Loading\nWorld server is up and running.\n" else null
    }

    private fun layout(imported: Boolean = true, data: Boolean = true): WowLayout {
        val game = tmp.newFolder("games", "wow_octowow")
        val l = WowLayout(File(game, "files/turtle").apply { mkdirs() }, File(game, ".export").apply { mkdirs() })
        l.ctl.apply { parentFile!!.mkdirs(); writeText("SERVER=\"\$FILES/server\"\nFILES=\"\${FILES:-/data/data/com.logie.warcraft/files/turtle}\"\n") }
        if (imported) {
            for (f in listOf("bin/mangosd", "bin/realmd", "bin/mariadbd", "lib/ld-musl-aarch64.so.1")) File(l.server, f).apply { parentFile!!.mkdirs(); writeText("x") }
            File(l.databases, "mysql").mkdirs()
        }
        if (data) for (d in listOf("dbc", "maps")) File(l.data, "$d/f").apply { parentFile!!.mkdirs(); writeText("x") }
        File(l.etc, "mangosd.conf").apply { parentFile!!.mkdirs(); writeText("vmap.enableLOS = 1\nGameType = 1\n") }
        return l
    }

    private fun controller(l: WowLayout, r: RealmControllerTest.FakeRunner) = OctoRealmController(
        layout = l, runner = r, scope = scope, timeZone = { "<+0000>-00:00" },
        portOpen = { port -> r.started.any { it.args.first() == "realmd" } && port == OctoRealmController.AUTH_PORT },
        sleep = { }, pollMs = 1,
    )

    @Test fun theRealmComesUpInOrderAndIsStoppedWithTheCharactersSaved() = runBlocking {
        val l = layout()
        val r = RealmControllerTest.FakeRunner(OctoBehavior())
        val c = controller(l, r)
        c.run()
        assertEquals(c.status.value.error, WowRealm.Phase.RUNNING, c.status.value.phase)
        assertEquals(Realm.OCTO, c.status.value.realm)
        val order = r.order()
        assertEquals(listOf("configure", "db", "db-ping"), order.take(3))
        assertTrue(order.indexOf("realmd") > order.indexOf("db-ping") && order.indexOf("mangosd") > order.indexOf("realmd"))
        // The realm's row is set through ctl.sh's sql, with the realm's own build and ports.
        val sql = r.started.first { "tw_logon" in it.args.first() }.command.argv.last()
        assertTrue(sql, sql.contains("blizz") && sql.contains("sql") && sql.contains("tw_logon"))
        assertEquals("UPDATE realmlist SET name = 'Tortoise WoW', address = '127.0.0.1', port = 8090, realmbuilds = '7272' WHERE id = 1;", r.started.first { "tw_logon" in it.args.first() }.command.env["SQL"])
        // Leftovers are looked for by Turtle's own pid files; the programs run through the loader of the server.
        assertEquals(1, r.leftoversCalls)
        assertTrue(File(l.server, "ctl.blizz.sh").isFile)
        // The settings the data allows: no vmaps here, a normal game.
        val conf = File(l.etc, "mangosd.conf").readText()
        assertTrue(conf, conf.contains("vmap.enableLOS = 0") && conf.contains("GameType = 0") && conf.contains("mmap.enabled = 0"))

        c.shutDown()
        assertTrue(r.find("mangosd").sent.contains("server shutdown 1"))
        assertEquals(WowRealm.Phase.STOPPED, c.status.value.phase)
    }

    @Test fun anIncompleteImportFailsWithAWordForThePerson() = runBlocking {
        val r = RealmControllerTest.FakeRunner(OctoBehavior())
        val c = controller(layout(imported = false), r)
        c.run()
        assertEquals(WowRealm.Phase.FAILED, c.status.value.phase)
        assertTrue(c.status.value.error!!.contains("OctoWoW isn't imported"))
        assertTrue(r.started.isEmpty())
    }

    @Test fun missingServerDataIsSaidBeforeAnythingStarts() = runBlocking {
        val r = RealmControllerTest.FakeRunner(OctoBehavior())
        val c = controller(layout(data = false), r)
        c.run()
        assertEquals(WowRealm.Phase.FAILED, c.status.value.phase)
        assertTrue(c.status.value.error!!.contains("server data"))
        assertTrue(r.started.isEmpty())
    }

    @Test fun theWorldServersFatalLinesAreNamed() {
        assertTrue(OctoRealmController.fatal("Correct *.map files not found in data dir")!!.contains("data"))
        assertTrue(OctoRealmController.fatal("DB AutoUpdater FAILED")!!.contains("update"))
        assertNull(OctoRealmController.fatal("World server is up and running"))
    }

    @Test fun aConfigKeyIsChangedInPlaceOrAdded() {
        val f = tmp.newFile("x.conf").apply { writeText("A = 1\nB = 2\n") }
        OctoRealmController.setConf(f, "A", "9")
        OctoRealmController.setConf(f, "C", "3")
        assertEquals("A = 9\nB = 2\nC = 3\n", f.readText())
    }

    @Test fun theClientIsPointedAtTheRealm() {
        val client = tmp.newFolder("client")
        File(client, "Data").mkdirs()
        File(client, "wow.EXE").writeText("x")
        assertTrue(OctoClientSetup.hasClient(client))
        assertEquals("wow.EXE", OctoClientSetup.executable(client)!!.name)
        OctoClientSetup.apply(client, 1828, 1248, "ANNA")
        assertEquals("set realmlist 127.0.0.1\r\nset patchlist 127.0.0.1\r\n", File(client, "realmlist.wtf").readText())
        val config = File(client, "WTF/Config.wtf").readText()
        assertTrue(config, config.contains("SET gxResolution \"1828x1248\"") && config.contains("SET realmName \"Tortoise WoW\"") && config.contains("SET accountName \"ANNA\""))
    }
}
