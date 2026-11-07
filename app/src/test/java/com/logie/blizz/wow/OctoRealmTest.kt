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

    private fun controller(l: WowLayout, r: RealmControllerTest.FakeRunner, spec: RealmSpec = RealmSpecs.OCTO) = ClassicRealmController(
        spec = spec, layout = l, runner = r, scope = scope, timeZone = { "<+0000>-00:00" },
        // The login server's ports are open once it has been started.
        portOpen = { port -> r.started.any { it.args.first() == spec.loginProgram } && port in spec.loginPorts },
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
        assertTrue(ClassicRealmController.fatal(RealmSpecs.OCTO, "Correct *.map files not found in data dir")!!.contains("data"))
        assertTrue(ClassicRealmController.fatal(RealmSpecs.OCTO, "DB AutoUpdater FAILED")!!.contains("update"))
        assertNull(ClassicRealmController.fatal(RealmSpecs.OCTO, "World server is up and running"))
    }

    @Test fun aConfigKeyIsChangedInPlaceOrAdded() {
        val f = tmp.newFile("x.conf").apply { writeText("A = 1\nB = 2\n") }
        ClassicRealmController.setConf(f, "A", "9")
        ClassicRealmController.setConf(f, "C", "3")
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
    private fun legionLayout(patched: Boolean, clientExe: Boolean = true): WowLayout {
        val game = tmp.newFolder("games", "wow_legion")
        val l = WowLayout(File(game, "files/felsong").apply { mkdirs() }, File(game, ".export").apply { mkdirs() })
        l.ctl.apply { parentFile!!.mkdirs(); writeText("SERVER=\"\$FILES/server\"\nFILES=\"\${FILES:-/data/data/com.logie.warcraft/files/felsong}\"\n") }
        for (f in listOf("bin/worldserver", "bin/bnetserver", "bin/mariadbd", "lib/ld-musl-aarch64.so.1")) File(l.server, f).apply { parentFile!!.mkdirs(); writeText("x") }
        File(l.databases, "mysql").mkdirs()
        for (d in listOf("dbc", "maps")) File(l.data, "$d/f").apply { parentFile!!.mkdirs(); writeText("x") }
        File(l.etc, "worldserver.conf").apply { parentFile!!.mkdirs(); writeText("GameType = 1\n") }
        File(l.etc, "bnetserver.conf").writeText("LoginREST.ExternalAddress = 1.2.3.4\n")
        File(l.client, "Data").mkdirs()
        if (clientExe) File(l.client, "Wow-64.exe").writeText("x")
        if (patched) {
            File(l.client, "Wow-64_Patched.exe").writeText("x")
            RealmSpecs.certBundle(l).apply { parentFile!!.mkdirs(); writeText("c") }
        }
        return l
    }

    private class LegionBehavior : RealmControllerTest.Behavior() {
        override fun alive(args: List<String>) = args.first() in setOf("db", "bnetserver", "worldserver")
        override fun logFor(args: List<String>): String? = if (args.first() == "worldserver") "Loading\n(worldserver-daemon) ready...\n" else null
    }

    @Test fun legionComesUpWithItsBattleNetServerAndPatchesTheClientFirstWhenItIsNot() = runBlocking {
        val l = legionLayout(patched = false)
        val r = RealmControllerTest.FakeRunner(LegionBehavior())
        val c = controller(l, r, RealmSpecs.LEGION)
        c.run()
        assertEquals(c.status.value.error, WowRealm.Phase.RUNNING, c.status.value.phase)
        assertEquals(Realm.LEGION, c.status.value.realm)
        val order = r.order()
        assertEquals(listOf("configure", "patch-client", "db", "db-ping"), order.take(4))
        assertTrue(order.indexOf("bnetserver") > order.indexOf("db-ping") && order.indexOf("worldserver") > order.indexOf("bnetserver"))
        assertTrue(r.find("patch-client").command.argv.last().endsWith("Wow-64.exe"))
        val sql = r.started.first { it.args.first().contains("'sql' 'auth'") }
        assertTrue(sql.command.env.getValue("SQL").contains("gamebuild = 26972") && sql.command.env.getValue("SQL").contains("port = 8095"))
        // The REST login is told this phone's address; a normal game; no Warden; no maps parts here (no vmaps or mmaps).
        assertTrue(File(l.etc, "bnetserver.conf").readText().contains("LoginREST.ExternalAddress = 127.0.0.1"))
        val world = File(l.etc, "worldserver.conf").readText()
        assertTrue(world, world.contains("GameType = 0") && world.contains("Warden.Enabled = 0") && world.contains("mmap.enablePathFinding = 0"))
        c.shutDown()
        assertTrue(r.find("worldserver").sent.contains("server shutdown 1"))
    }

    @Test fun anAlreadyPatchedLegionClientIsNotPatchedAgain() = runBlocking {
        val r = RealmControllerTest.FakeRunner(LegionBehavior())
        controller(legionLayout(patched = true), r, RealmSpecs.LEGION).run()
        assertTrue(r.order().none { it == "patch-client" })
    }

    @Test fun theBattleNetCertificateBundleGoesIntoBothPlacesOfTheGamesWindows() {
        val bundle = tmp.newFile("web_cert_bundle").apply { writeText("certs") }
        val driveC = tmp.newFolder("drive_c")
        assertEquals(2, com.logie.blizz.game.LegionClientSetup.installCertificateBundle(bundle, driveC))
        for (path in com.logie.blizz.game.LegionClientSetup.CERT_BUNDLE_IN_PREFIX) assertEquals("certs", File(driveC, path).readText())
        assertEquals(0, com.logie.blizz.game.LegionClientSetup.installCertificateBundle(File(tmp.root, "none"), driveC))
    }

    @Test fun legionsClientIsPointedAtThePortalAndKeepsWhatWasChosenInTheGame() {
        val client = tmp.newFolder("lclient")
        File(client, "WTF").mkdirs()
        File(client, "WTF/Config.wtf").writeText("SET graphicsQuality \"7\"\r\n")
        com.logie.blizz.game.LegionClientSetup.apply(client, 1828, 1248, "anna@example.com")
        val config = File(client, "WTF/Config.wtf").readText()
        assertTrue(config, config.contains("SET portal \"127.0.0.1\"") && config.contains("SET gxWindowedResolution \"1828x1248\"") && config.contains("SET accountName \"anna@example.com\""))
        assertTrue(config, config.contains("SET graphicsQuality \"7\"") && !config.contains("graphicsQuality \"3\""))
    }
}

class CompiledPathsTest {
    @get:Rule val tmp = TemporaryFolder()

    @Test fun theOldAppsFolderInAProgramBecomesBlizzardsOfTheSameLength() {
        val old = "/data/data/com.logie.warcraft/files/turtle/server/modules"
        val filler = ByteArray(3_000_000) { 7 }
        val bytes = filler + old.toByteArray() + byteArrayOf(0) + filler.copyOf(100) + old.toByteArray() + byteArrayOf(0)
        val file = tmp.newFile("mangosd").apply { writeBytes(bytes) }
        assertEquals(2, CompiledPaths.patchFile(file))
        val after = file.readBytes()
        assertEquals(bytes.size, after.size)
        val text = String(after, Charsets.ISO_8859_1)
        assertTrue(!text.contains("com.logie.warcraft"))
        assertEquals(2, Regex(Regex.escape("/data/data/com.logie.blizz////files/turtle/server/modules")).findAll(text).count())
        assertEquals(0, CompiledPaths.patchFile(file))
    }

    @Test fun aMatchAcrossAChunkBoundaryIsFound() {
        val old = "com.logie.warcraft/".toByteArray()
        val bytes = ByteArray((1 shl 20) - 5) { 1 } + old + ByteArray(50) { 1 }
        val file = tmp.newFile("x").apply { writeBytes(bytes) }
        assertEquals(1, CompiledPaths.patchFile(file))
        assertEquals(0, CompiledPaths.patchFile(file))
    }

    @Test fun theRealmFolderIsLinkedFromTheAppsFiles() {
        val appFiles = tmp.newFolder("files")
        val root = File(appFiles, "games/wow_octowow/files/turtle").apply { mkdirs() }
        val layout = WowLayout(root, File(appFiles, "games/wow_octowow/.export"))
        assertEquals(appFiles, CompiledPaths.appFiles(layout))
        File(layout.server, "bin").mkdirs()
        File(layout.server, "bin/mangosd").writeBytes("x/data/data/com.logie.warcraft/files/turtle/server/modules\u0000".toByteArray())
        assertEquals(1, CompiledPaths.fix(layout))
        assertEquals(root.canonicalPath, File(appFiles, "turtle").canonicalPath)
        assertEquals(0, CompiledPaths.fix(layout))
    }
}
