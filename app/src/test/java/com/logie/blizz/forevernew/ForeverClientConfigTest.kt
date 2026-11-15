package com.logie.blizz.forevernew

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

class ForeverClientConfigTest {
    @get:Rule val tmp = TemporaryFolder()
    private val builds = ForeverClient.parseBuilds("# comment\n70938\n70888\n\n70862\n")

    private fun install(product: String, version: String, forever: Boolean = true, data: Boolean = true): File {
        val root = tmp.newFolder("wow-${System.nanoTime()}")
        File(root, ".build.info").writeText("Branch!STRING:0|Active!DEC:1|Product!STRING:0|Version!STRING:0\r\neu|1|$product|$version\r\n")
        if (forever) File(root, "_forever_").mkdirs().also { File(root, "_forever_/Wow.exe").writeText("x") }
        if (data) File(root, "Data").mkdirs()
        return root
    }

    @Test fun buildsFileParses() { assertEquals(listOf(70938, 70888, 70862), builds) }

    @Test fun acceptsASupportedCompleteInstall() {
        val r = ForeverClient.inspect(install("wowf", "1.60.1.70938"), builds)
        r as ForeverClient.Result.Ok
        assertEquals(70938, r.build)
        assertEquals("Wow.exe", r.exe?.name)
    }

    @Test fun findsTheRootWhenForeverIsSelected() {
        val root = install("wowf", "1.60.1.70888")
        val r = ForeverClient.inspect(File(root, "_forever_"), builds)
        assertTrue(r is ForeverClient.Result.Ok && r.root == root)
    }

    @Test fun rejectsOtherProductsMissingPartsAndUnsupportedBuilds() {
        assertTrue(ForeverClient.inspect(install("wow", "3.3.5.12340"), builds) is ForeverClient.Result.Rejected)
        assertTrue(ForeverClient.inspect(install("wow_classic_era", "1.15.0.1"), builds) is ForeverClient.Result.Rejected)
        val noData = ForeverClient.inspect(install("wowf", "1.60.1.70938", data = false), builds) as ForeverClient.Result.Rejected
        assertTrue(noData.reason.contains("Data"))
        assertTrue(ForeverClient.inspect(install("wowf", "1.60.1.70938", forever = false), builds) is ForeverClient.Result.Rejected)
        val old = ForeverClient.inspect(install("wowf", "1.60.1.60000"), builds) as ForeverClient.Result.Rejected
        assertTrue(old.reason.contains("70938"))
        assertTrue(ForeverClient.inspect(tmp.newFolder("empty"), builds) is ForeverClient.Result.Rejected)
    }

    @Test fun botBudgetFollowsPhoneMemoryAndNeverTheDesktopProfile() {
        val small = ForeverConfig.profile(6_000)
        assertFalse(small.worldBots); assertEquals(0, small.maxBots)
        val mid = ForeverConfig.profile(12_000)
        assertTrue(mid.worldBots); assertTrue(mid.maxBots in 10..150)
        val big = ForeverConfig.profile(24_000, "high")
        assertTrue(big.maxBots <= 300)
        assertTrue(ForeverConfig.profile(16_000, "high").maxBots < 450)
        assertFalse(ForeverConfig.profile(24_000, "off").worldBots)
        assertFalse(ForeverConfig.profile(24_000, worldBots = false).worldBots)
        assertTrue(ForeverConfig.profile(24_000, auction = false).let { !it.auctionSeller && !it.auctionBuyer })
        assertTrue(big.rssBudgetMb < 9_000)
    }

    private val params = ForeverConfig.Params("/d", "/l", "/s", "/w.pid", "/b.pid", "u", "pw", "/mysql", ForeverConfig.PORTAL, "/c.pem", "/k.pem", listOf(70888, 70862))

    @Test fun worldConfigHasTheKeysUpstreamNeeds() {
        val c = ForeverConfig.worldserverConf(params)
        assertTrue(c.contains("Network.EnterEncryptedModeRegionGroup = 8\n"))
        assertTrue(c.contains("RealmID = 70\n"))
        assertTrue(c.contains("Updates.EnableDatabases = 15\n"))
        assertTrue(c.contains("WorldServerPort = ${ForeverPorts.WORLD}\n"))
        assertTrue(c.contains("Realm.AlsoAcceptBuilds = \"70888,70862\""))
        assertTrue(c.contains("\"127.0.0.1;${ForeverPorts.DATABASE};u;pw;world\""))
        val b = ForeverConfig.bnetserverConf(params)
        assertTrue(b.contains("BattlenetPort = ${ForeverPorts.BNET}\n"))
        assertTrue(b.contains("LoginREST.ExternalAddress = trinity.actual.battle.net\n"))
        assertTrue(b.contains("Realm.AlsoAcceptBuilds = \"70888,70862\""))
    }

    @Test fun localConfigSwitchesBotsAndAuctionSeparately() {
        val on = ForeverConfig.localConf(ForeverConfig.profile(16_000))
        assertTrue(on.contains("Playerbot.World.Enable = 1")); assertTrue(on.contains("Playerbot.World.RssBudgetMb"))
        val off = ForeverConfig.localConf(ForeverConfig.profile(16_000, worldBots = false, auction = true))
        assertTrue(off.contains("Playerbot.World.Enable = 0")); assertFalse(off.contains("Playerbot.World.MaxBots"))
        assertTrue(off.contains("AuctionHouseBot.Seller.Enabled = 1"))
        assertTrue(ForeverConfig.localConf(ForeverConfig.profile(16_000, auction = false)).contains("AuctionHouseBot.Seller.Enabled = 0"))
    }

    @Test fun mapsPlanFollowsUpstreamsOrderAndChecksSpace() {
        val layout = ForeverLayout(File(tmp.root, "r"))
        val plan = ForeverMaps.plan(layout, File("/client"), 4)
        assertEquals(listOf("mapextractor", "vmap4extractor", "vmap4assembler", "mmaps_generator"), plan.map { File(it.argv.first()).name })
        assertTrue(plan[0].argv.containsAll(listOf("-i", "/client", "-e", "15", "-f", "1")))
        assertEquals(listOf("Buildings", "vmaps"), plan[2].argv.subList(1, 3))
        assertTrue(ForeverMaps.checkSpace(5L shl 30)!!.contains("45 GB"))
        assertTrue(ForeverMaps.checkSpace(60L shl 30) == null)
    }

    @Test fun mapsStagesCheckpointOnlyWithOutput() {
        val layout = ForeverLayout(File(tmp.root, "r2"))
        assertEquals(4, ForeverMaps.remaining(layout).size)
        assertTrue(ForeverMaps.complete(layout, ForeverMaps.Stage.MAPS) != null)
        File(layout.data, "maps").mkdirs(); File(layout.data, "maps/0000.map").writeText("x"); File(layout.data, "dbc").mkdirs(); File(layout.data, "dbc/a.db2").writeText("x")
        assertTrue(ForeverMaps.complete(layout, ForeverMaps.Stage.MAPS) == null)
        assertTrue(ForeverMaps.isDone(layout, ForeverMaps.Stage.MAPS))
        assertFalse(layout.hasMaps())
        ForeverMaps.reset(layout)
        assertFalse(ForeverMaps.isDone(layout, ForeverMaps.Stage.MAPS))
    }

    @Test fun addonInstallsOnlyForeverBots() {
        val zip = File(tmp.root, "a.zip")
        java.util.zip.ZipOutputStream(zip.outputStream()).use { z ->
            for ((n, d) in mapOf("ForeverBots/ForeverBots.toc" to "## Title", "ForeverBots/ForeverBots.lua" to "x", "ForeverDots/ForeverDots.toc" to "y", "pack/ForeverBots/sub/a.lua" to "z")) {
                z.putNextEntry(java.util.zip.ZipEntry(n)); z.write(d.toByteArray()); z.closeEntry()
            }
        }
        val client = tmp.newFolder("c")
        assertEquals(3, ForeverBots.install(zip, client))
        assertTrue(ForeverBots.isInstalled(client))
        assertFalse(File(client, "_forever_/Interface/AddOns/ForeverDots").exists())
        assertTrue(File(ForeverBots.targetFolder(client), "sub/a.lua").isFile)
        // A second install replaces it.
        assertEquals(3, ForeverBots.install(zip, client))
    }

    @Test fun addonWithoutTocIsRefusedAndTheOldOneKept() {
        val client = tmp.newFolder("c2")
        File(ForeverBots.targetFolder(client), "ForeverBots.toc").apply { parentFile.mkdirs(); writeText("old") }
        val zip = File(tmp.root, "b.zip")
        java.util.zip.ZipOutputStream(zip.outputStream()).use { z -> z.putNextEntry(java.util.zip.ZipEntry("ForeverBots/x.lua")); z.write(1); z.closeEntry() }
        assertTrue(runCatching { ForeverBots.install(zip, client) }.isFailure)
        assertEquals("old", File(ForeverBots.targetFolder(client), "ForeverBots.toc").readText())
    }

    @Test fun credentialsAreGeneratedOnceAndKeptPrivate() {
        val layout = ForeverLayout(File(tmp.root, "r3"))
        val a = ForeverAuth.loadOrCreate(layout)
        val b = ForeverAuth.loadOrCreate(layout)
        assertEquals(a, b)
        assertTrue(a.password.length >= 18 && a.dbPassword.length >= 36 && a.dbPassword != a.dbRoot)
        assertTrue(ForeverAuth.consoleCommands(a).first().startsWith("bnetaccount create "))
        assertTrue(ForeverAuth.realmSql(70938).contains("70938") && ForeverAuth.realmSql(70938).contains("(70,"))
    }

    @Test fun logsRedactSecretsAndStayBounded() {
        val logs = ForeverLogs(File(tmp.root, "log/e.log"), maxBytes = 2000)
        repeat(200) { logs.event("password=hunter2 line $it") }
        val text = File(tmp.root, "log/e.log").readText()
        assertFalse(text.contains("hunter2"))
        assertTrue(text.length < 4000)
    }

    // ---- installer order ----
    private class Fake(val layout: ForeverLayout, val client: ForeverClient.Result.Ok?, val failAt: String? = null) : ForeverInstaller.Steps {
        val calls = ArrayList<String>()
        private fun step(n: String): String? { calls += n; return if (failAt == n) "boom in $n" else null }
        override fun package_(say: (String, Float?) -> Unit) = step("package")
        override fun client() = client.also { calls += "client" }
        override fun extractData(client: ForeverClient.Result.Ok, say: (String, Float?) -> Unit): String? {
            File(layout.data, "maps").mkdirs(); File(layout.data, "maps/a").writeText("x")
            File(layout.data, "vmaps").mkdirs(); File(layout.data, "vmaps/a").writeText("x")
            File(layout.data, "mmaps").mkdirs(); File(layout.data, "mmaps/a").writeText("x")
            File(layout.data, "dbc").mkdirs(); File(layout.data, "dbc/a").writeText("x")
            return step("extract")
        }
        override fun database(client: ForeverClient.Result.Ok, say: (String, Float?) -> Unit) = step("database")
        override fun addon(client: ForeverClient.Result.Ok, say: (String, Float?) -> Unit) = step("addon")
        override fun startAuth() = step("auth")
        override fun startWorld() = step("world")
    }

    private fun installer(layout: ForeverLayout, f: Fake) =
        ForeverInstaller(layout, f, ForeverStateStore(layout.stateFile), ForeverLogs(File(layout.logs, "e.log"))) { 100L shl 30 }
    private val ok = ForeverClient.Result.Ok(File("/c"), 70938, "1.60.1.70938", null)

    @Test fun installerRunsTheStagesInOrderAndNeverClaimsTheGame() {
        val layout = ForeverLayout(File(tmp.root, "i1")); val f = Fake(layout, ok)
        val r = installer(layout, f).run { _, _, _ -> }
        assertEquals(ForeverInstaller.Outcome.READY, r.outcome)
        assertEquals(listOf("package", "client", "extract", "database", "addon", "auth", "world"), f.calls)
        assertTrue(r.message.contains("not implemented"))
        assertEquals(ForeverState.READY, ForeverStateStore(layout.stateFile).load().state)
    }

    @Test fun installerRefusesMapExtractionWithoutSpace() {
        val layout = ForeverLayout(File(tmp.root, "i3")); val f = Fake(layout, ok)
        val r = ForeverInstaller(layout, f, ForeverStateStore(layout.stateFile), ForeverLogs(File(layout.logs, "e.log"))) { 3L shl 30 }.run { _, _, _ -> }
        assertEquals(ForeverInstaller.Outcome.FAILED, r.outcome)
        assertTrue(r.message.contains("45 GB"))
        assertFalse(f.calls.contains("extract"))
    }

    @Test fun installerStopsAtAMissingClientAndAtEachFailure() {
        val layout = ForeverLayout(File(tmp.root, "i2")); val f = Fake(layout, null)
        assertEquals(ForeverInstaller.Outcome.AWAITING_CLIENT, installer(layout, f).run { _, _, _ -> }.outcome)
        assertEquals(listOf("package", "client"), f.calls)
        for (stage in listOf("package", "extract", "database", "addon", "auth", "world")) {
            val l = ForeverLayout(File(tmp.root, "f-$stage")); val fk = Fake(l, ok, failAt = stage)
            val r = installer(l, fk).run { _, _, _ -> }
            assertEquals(stage, ForeverInstaller.Outcome.FAILED, r.outcome)
            assertTrue(r.message.contains("boom in $stage"))
            assertEquals(ForeverState.FAILED, ForeverStateStore(l.stateFile).load().state)
        }
    }

    @Test fun serverCommandsGoThroughTheLoaderWithoutCompiledInPaths() {
        val layout = ForeverLayout(File(tmp.root, "srv"))
        File(layout.lib, "ld-musl-aarch64.so.1").apply { parentFile.mkdirs(); writeText("l") }
        val c = ForeverServer.command(layout, ForeverServer.WORLD)
        assertEquals(File(layout.lib, "ld-musl-aarch64.so.1").path, c.argv[0])
        assertEquals("--library-path", c.argv[1]); assertEquals(File(layout.bin, "worldserver").path, c.argv[3])
        assertTrue(c.env["LD_PRELOAD"]!!.endsWith("libandroidcompat.so"))
        assertEquals(listOf("db", "auth", "world"), ForeverServer.startOrder.map { it.key })
        assertEquals(listOf("world", "auth", "db"), ForeverServer.stopOrder.map { it.key })
        assertTrue(ForeverServer.dbArgs(layout).contains("--bind-address=127.0.0.1"))
        assertTrue(ForeverServer.explain("Correct *.map files not found")!!.contains("map data"))
    }
}
