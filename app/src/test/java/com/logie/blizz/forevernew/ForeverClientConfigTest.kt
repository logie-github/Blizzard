package com.logie.blizz.forevernew

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import java.io.File

// (Robolectric: the unit tests' org.json is Android's stub otherwise)
@RunWith(RobolectricTestRunner::class)
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
        assertTrue(a.password.length in 1..16 && a.password.none { it.isWhitespace() || it in "\"'`;" })
        assertTrue(a.dbPassword.length >= 36 && a.dbPassword != a.dbRoot)
        assertEquals("logie@wow.server", a.name); assertEquals("Logie", a.password)
        assertEquals("bnetaccount create logie@wow.server Logie", ForeverAuth.createCommand(a))
        assertEquals("account set gmlevel 7#1 3 -1", ForeverAuth.gmCommand(7))
        assertTrue(ForeverAuth.idSql(a).contains("battlenet_accounts"))
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
        override fun downloadClient(say: (String, Float?) -> Unit): String? { calls += "download"; return if (client == null) "offline" else null }
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
        override fun account() = step("account")
    }

    private fun installer(layout: ForeverLayout, f: Fake) =
        ForeverInstaller(layout, f, ForeverStateStore(layout.stateFile), ForeverLogs(File(layout.logs, "e.log"))) { 100L shl 30 }
    private val ok = ForeverClient.Result.Ok(File("/c"), 70938, "1.60.1.70938", null)

    @Test fun installerRunsTheStagesInOrderAndNeverClaimsTheGame() {
        val layout = ForeverLayout(File(tmp.root, "i1")); val f = Fake(layout, ok)
        val r = installer(layout, f).run { _, _, _ -> }
        assertEquals(ForeverInstaller.Outcome.READY, r.outcome)
        assertEquals(listOf("package", "client", "extract", "database", "addon", "auth", "world", "account"), f.calls)
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
        assertEquals(listOf("package", "client", "download"), f.calls)
        for (stage in listOf("package", "extract", "database", "addon", "auth", "world", "account")) {
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
        assertTrue(c.env["LD_PRELOAD"]!!.contains("libandroidcompat.so") && c.env["LD_PRELOAD"]!!.contains("libforeverresolve.so"))
        assertEquals(listOf("db", "auth", "world"), ForeverServer.startOrder.map { it.key })
        assertEquals(listOf("world", "auth", "db"), ForeverServer.stopOrder.map { it.key })
        assertTrue(ForeverServer.dbArgs(layout).contains("--bind-address=127.0.0.1"))
        assertTrue(ForeverServer.explain("Correct *.map files not found")!!.contains("map data"))
    }

    // ---- the game's side: certificate, hosts, launch files, key helper settings ----
    @Test fun certificateConfigsMatchUpstream() {
        assertTrue(ForeverAuth.caConfig("t").contains("nameConstraints=critical,permitted;DNS:actual.battle.net"))
        assertTrue(ForeverAuth.leafExt().contains("subjectAltName=DNS:trinity.actual.battle.net"))
        val layout = ForeverLayout(File(tmp.root, "c"))
        val cmds = ForeverAuth.certificateCommands(layout)
        assertEquals(3, cmds.size)
        assertTrue(cmds[0].containsAll(listOf("-x509", "825")) && cmds[2].contains("-CAcreateserial"))
        assertEquals("L\nR\n", ForeverAuth.chain("L\n\n", "R\n"))
        assertFalse(ForeverAuth.hasCertificate(layout))
    }

    @Test fun wineRootStoreEntryIsIdempotentAndInBothViews() {
        val der = ByteArray(300) { (it * 3).toByte() }
        val reg = File(tmp.root, "system.reg").apply { writeText("WINE REGISTRY Version 2\n") }
        assertTrue(WineCerts.install(reg, der, 1700000000))
        assertFalse(WineCerts.install(reg, der, 1700000001))
        val text = reg.readText()
        val thumb = java.security.MessageDigest.getInstance("SHA-1").digest(der).joinToString("") { "%02X".format(it) }
        assertEquals(thumb, WineCerts.thumbprint(der))
        assertEquals(2, Regex(Regex.escape(thumb) + "\\]").findAll(text).count())
        assertTrue(text.contains("Software\\\\Microsoft\\\\SystemCertificates\\\\Root\\\\Certificates"))
        assertTrue(text.contains("Software\\\\Wow6432Node\\\\Microsoft\\\\SystemCertificates"))
        val blob = WineCerts.blob(der)
        assertEquals(12 + 300, blob.size)
        assertEquals(32, blob[0].toInt()); assertEquals(1, blob[4].toInt()); assertEquals(300 and 255, blob[8].toInt() and 255)
        assertTrue(text.contains("\"Blob\"=hex:20,00,00,00,01,00,00,00,2c,01,00,00,00,03,06"))
        assertFalse(WineCerts.install(File(tmp.root, "none.reg"), der))
    }

    @Test fun pemConvertsToDer() {
        val pem = "-----BEGIN CERTIFICATE-----\n" + java.util.Base64.getMimeEncoder(64, "\n".toByteArray()).encodeToString(ByteArray(100) { it.toByte() }) + "\n-----END CERTIFICATE-----\n"
        assertEquals(100, WineCerts.pemToDer(pem).size)
    }

    @Test fun launchFilesLeaveThePlayersConfigAlone() {
        val client = tmp.newFolder("wow")
        val dir = File(client, "_forever_").apply { mkdirs() }
        File(dir, "Wow.exe").writeText("x")
        File(dir, "WTF").mkdirs(); File(dir, "WTF/Config.wtf").writeText("SET portal \"us\"\nSET gxWindow \"0\"\nSET sound \"1\"\n")
        File(client, ".build.info").writeText("Branch!STRING:0|Tags!STRING:0\nus|Windows x86_64 frFR text? enUS text? enUS speech?\n")
        assertNull(ForeverLaunch.prepare(client, 2400, 1080) { byteArrayOf(1, 2, 3) })
        assertTrue(File(dir, "WTF/Config.wtf").readText().contains("SET portal \"us\""))
        val wtf = File(dir, "WTF/ForeverLauncher.wtf").readText()
        assertTrue(wtf.contains("SET portal \"trinity.actual.battle.net\"") && wtf.contains("SET sound \"1\"") && wtf.contains("SET gxWindow \"1\""))
        assertTrue(wtf.contains("SET textLocale \"enUS\"") && wtf.contains("2400x1080"))
        val cfg = File(dir, "foreverkey.cfg").readText()
        assertTrue(cfg.contains("client=Wow.exe") && cfg.contains("group=8") && cfg.contains("key=02596F0D0C06"))
        assertTrue(File(dir, "foreverkey.exe").readBytes().contentEquals(byteArrayOf(1, 2, 3)))
        assertNotNull(ForeverLaunch.prepare(client, 800, 600) { null })
        assertEquals("frFR", ForeverLaunch.textLocale("x|Windows frFR text? deDE speech?"))
        assertEquals("enUS", ForeverLaunch.textLocale(""))
        assertTrue(ForeverLaunch.PUBLIC_KEY.length == 64)
    }

    @Test fun portalIsOnlyInTheGamesHosts() {
        val hosts = com.logie.blizz.game.Offline.hosts(true, listOf(ForeverConfig.PORTAL))
        assertTrue(hosts.contains("127.0.0.1\ttrinity.actual.battle.net"))
        assertFalse(com.logie.blizz.game.Offline.hosts(true).contains("trinity.actual.battle.net"))
        assertTrue(hosts.contains("0.0.0.0\tus.actual.battle.net"))
    }

    // ---- the one folder pick ----
    private class MapTree(val files: Map<String, ByteArray>, val failOn: String? = null) : ForeverClientImport.Tree {
        override val rootId = ""
        private fun children(id: String): List<String> = files.keys.filter { k -> id.isEmpty() || k.startsWith("$id/") }
            .map { k -> k.removePrefix(if (id.isEmpty()) "" else "$id/").substringBefore('/') }.distinct()
        override fun list(id: String) = children(id).map { n ->
            val path = if (id.isEmpty()) n else "$id/$n"
            val dir = files.keys.any { it.startsWith("$path/") }
            ForeverClientImport.Entry(path, n, dir, files[path]?.size?.toLong() ?: 0L)
        }
        override fun open(id: String): java.io.InputStream {
            if (id == failOn) throw java.io.IOException("read failed")
            return java.io.ByteArrayInputStream(files.getValue(id))
        }
    }

    private val install = mapOf(
        ".build.info" to "x".toByteArray(), "Data/data/data.000" to ByteArray(5000) { 1 }, "Data/config/a" to ByteArray(10),
        "_forever_/Wow.exe" to ByteArray(2000), "_forever_/WTF/Config.wtf" to ByteArray(20),
        "_retail_/Wow.exe" to ByteArray(9000), "Launcher.db" to ByteArray(10),
    )

    @Test fun importCopiesOnlyTheRealmsPartsAndResumes() {
        val dest = File(tmp.root, "client")
        assertNull(ForeverClientImport.copy(MapTree(install), dest, { 1L shl 40 }))
        assertTrue(File(dest, "_forever_/Wow.exe").isFile && File(dest, "Data/data/data.000").length() == 5000L && File(dest, ".build.info").isFile)
        assertFalse(File(dest, "_retail_").exists()); assertFalse(File(dest, "Launcher.db").exists())
        // a second pick copies nothing new (and a changed-size file is copied again)
        File(dest, "_forever_/Wow.exe").writeBytes(ByteArray(5))
        var opened = 0
        val counting = object : ForeverClientImport.Tree by MapTree(install) { override fun open(id: String): java.io.InputStream { opened++; return MapTree(install).open(id) } }
        assertNull(ForeverClientImport.copy(counting, dest, { 1L shl 40 }))
        assertEquals(1, opened)
        assertEquals(2000L, File(dest, "_forever_/Wow.exe").length())
    }

    @Test fun importRefusesWrongFoldersAndLowSpaceAndFailures() {
        val dest = File(tmp.root, "client2")
        val foreverOnly = mapOf("Wow.exe" to ByteArray(3), "WTF/Config.wtf" to ByteArray(3))
        assertTrue(ForeverClientImport.copy(MapTree(foreverOnly), dest)!!.contains("_forever_ folder itself"))
        assertTrue(ForeverClientImport.copy(MapTree(mapOf("a" to ByteArray(1))), dest)!!.contains("complete WoW Forever installation"))
        assertTrue(ForeverClientImport.copy(MapTree(install), dest, { 1L shl 20 })!!.contains("Not enough space"))
        val bad = ForeverClientImport.copy(MapTree(install, failOn = "_forever_/Wow.exe"), dest, { 1L shl 40 })
        assertTrue(bad!!.contains("failed"))
        assertFalse(File(dest, "_forever_/Wow.exe").exists())
        assertTrue(ForeverClientImport.copy(MapTree(install), dest, { 1L shl 40 }, cancelled = { true })!!.contains("stopped"))
    }
}
