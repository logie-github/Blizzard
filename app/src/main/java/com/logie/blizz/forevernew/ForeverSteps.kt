package com.logie.blizz.forevernew

import com.logie.blizz.wow.LineWatch
import com.logie.blizz.wow.WowCtl
import com.logie.blizz.wow.WowLogs
import java.io.File
import java.io.IOException
import java.io.OutputStream
import java.net.InetSocketAddress
import java.net.Socket

/**
 * The real work of each stage, on a phone. NONE OF THIS HAS RUN ON A PHONE: what is tested is every pure part it uses
 * (package, extraction safety, client detection, config text, SQL filter, maps plan, add-on install, state and installer order).
 * What can only be learnt on hardware (the loader running the programs under the app's sandbox, MariaDB's bootstrap, the
 * updater's behaviour on these dumps, memory and time) is reported by the stage failing with the program's own log text.
 */
class ForeverSteps(
    private val layout: ForeverLayout,
    private val deviceAbis: List<String>,
    private val totalRamMb: Int,
    private val bots: () -> Pair<String, Pair<Boolean, Boolean>> = { "auto" to (true to true) },
    /** Sends a signal to a process (`android.os.Process.sendSignal` on a phone): how a program left running is ended. */
    private val signal: (Int, Int) -> Unit = { _, _ -> },
) : ForeverInstaller.Steps {
    private val processes = HashMap<String, Process>()
    private val clientPointer get() = File(layout.root, "client-path.txt")
    private fun supportedBuilds(): List<Int> =
        ForeverPackage.installed(layout)?.clientBuilds.orEmpty()

    // ---- 1: the server package -------------------------------------------------------------------------------------------
    override fun package_(say: (String, Float?) -> Unit): String? = try {
        val published = runCatching { ForeverPackage.manifest() }.getOrElse { e ->
            if (layout.hasServer() && ForeverPackage.installed(layout) != null) return null // offline with a server installed
            throw e
        }
        ForeverPackage.incompatible(published, deviceAbis)?.let { return it }
        if (ForeverPackage.needsInstall(layout, published)) ForeverPackage.install(layout, published, say)
        ForeverPackage.restoreEtc(layout, say)
        null
    } catch (e: IOException) { e.message ?: "The server package failed" }

    // ---- 2: the client ---------------------------------------------------------------------------------------------------
    override fun client(): ForeverClient.Result.Ok? {
        val path = clientPointer.takeIf { it.isFile }?.readText()?.trim()?.takeIf { it.isNotEmpty() } ?: return null
        return ForeverClient.inspect(File(path), supportedBuilds()) as? ForeverClient.Result.Ok
    }

    /** The client, from Blizzard's servers (or carried on where it stopped), into the app's own folder. */
    override fun downloadClient(say: (String, Float?) -> Unit): String? {
        val logs = ForeverLogs(File(layout.logs, "forever-events.log"))
        var lastKind = ""
        var lastAt = 0L
        val logged: (String, Float?) -> Unit = { text, p ->
            // one line per stage and at most one more every 30 seconds, so a stall shows in the log
            val kind = text.substringBefore(':').substringBefore('(').trim()
            val now = System.currentTimeMillis()
            if (kind != lastKind || now - lastAt > 30_000) { logs.event("client: $text"); lastKind = kind; lastAt = now }
            say(text, p)
        }
        return try {
            ForeverClientDownload.download(layout.client, ForeverClientDownload.ALL, supportedBuilds(), logged)
            ForeverClientImport.remember(layout)
            null
        } catch (e: IOException) {
            logs.event("client: FAILED ${e.message}")
            e.message ?: "The game couldn't be downloaded"
        }
    }

    // ---- 3: maps, vmaps, mmaps -------------------------------------------------------------------------------------------
    override fun extractData(client: ForeverClient.Result.Ok, say: (String, Float?) -> Unit): String? {
        prepareRuntime()
        // A game this app downloaded before it stored the VFS files: the tools below find no file in it without them.
        if (client.root.canonicalPath == layout.client.canonicalPath && !ForeverMaps.isDone(layout, ForeverMaps.Stage.MAPS)) {
            try {
                val n = ForeverClientDownload.repairIndex(layout.client) { text, p -> say("Completing the game's index: $text", p) }
                if (n > 0) ForeverLogs(File(layout.logs, "forever-events.log")).event("client: $n index files added to the downloaded game")
            } catch (e: IOException) {
                return "The game's index couldn't be completed (${e.message}). Check the connection and press Install & Play again."
            }
        }
        val steps = ForeverMaps.plan(layout, client.root, threads = 0)
        for ((i, step) in steps.withIndex()) {
            if (ForeverMaps.isDone(layout, step.stage)) continue
            say("${step.stage.label} (${i + 1} of ${steps.size})", i.toFloat() / steps.size)
            val log = File(layout.logs, "extract-${step.stage.key}.log")
            val code = runToEnd(ForeverServer.toolCommand(layout, step), log)
            if (code != 0) return "${step.stage.label} failed (${WowLogs.exitInWords(code)}). ${ForeverServer.explain(ForeverLogs.tailOf(log)) ?: WowLogs.tail(log, 8)}"
            ForeverMaps.complete(layout, step.stage)?.let { return it }
            if (step.stage == ForeverMaps.Stage.VMAP_ASSEMBLE) ForeverMaps.cleanup(layout)
        }
        return null
    }

    // ---- 4: database -----------------------------------------------------------------------------------------------------
    override fun database(client: ForeverClient.Result.Ok, say: (String, Float?) -> Unit): String? {
        prepareRuntime()
        val account = ForeverAuth.loadOrCreate(layout)
        try {
            if (ForeverDb.needsBootstrap(layout)) {
                say("Creating Forever's database", null)
                layout.db.mkdirs()
                val share = File(layout.server, "share/mariadb")
                val boot = ForeverServer.command(layout, "mariadbd", listOf("--no-defaults", "--bootstrap", "--skip-networking", "--datadir=${layout.db.path}",
                    "--basedir=${layout.server.path}", "--lc-messages-dir=${share.path}", "--character-sets-dir=${share.path}/charsets", "--tmpdir=${File(layout.run, "tmp").path}"))
                val code = runToEnd(boot, File(layout.logs, "db-bootstrap.log")) { it.write(ForeverDb.bootstrapSql(share).toByteArray()) }
                if (code != 0) return "The database couldn't be created (${WowLogs.exitInWords(code)}): ${WowLogs.tail(File(layout.logs, "db-bootstrap.log"), 6)}"
            }
            startProgram(ForeverServer.DATABASE)?.let { return it }
            sql("root", "", ForeverDb.createSql(account.dbUser, account.dbPassword))?.let { return it }
            val repackSource = RangeZip.Http.probe(ForeverRepackData.REPACK_URL)
            val space = layout.downloads.apply { mkdirs() }.usableSpace
            if (space in 1 until ForeverRepackData.spaceNeeded()) return "Not enough space for Forever's world database: ${ForeverRepackData.spaceNeeded() shr 20} MB are needed, ${space shr 20} MB are free."
            val world = ForeverRepackData.extract(repackSource, ForeverRepackData.WORLD, File(layout.downloads, "world.sql")) { d, t -> say("Fetching the world database: ${d shr 20} / ${t shr 20} MB", d.toFloat() / t) }
            val hotfix = ForeverRepackData.extract(repackSource, ForeverRepackData.HOTFIXES, File(layout.downloads, "hotfixes.sql")) { d, t -> say("Fetching the hotfix database: ${d shr 20} / ${t shr 20} MB", d.toFloat() / t) }
            val plan = ForeverDb.importPlan(layout, world, hotfix)
            for ((i, p) in plan.withIndex()) {
                val (db, file) = p
                val mark = ForeverDb.marker(layout, db, file)
                if (mark.isFile) continue
                if (!file.isFile) return "${file.name} is missing from the server package"
                say("Importing ${file.name} (${i + 1} of ${plan.size})", i.toFloat() / plan.size)
                importFile(account, db, file)?.let { return "Importing ${file.name} failed: $it" }
                mark.parentFile?.mkdirs(); mark.writeText("1")
            }
            // The data is in: the downloaded dumps are no longer needed.
            world.delete(); hotfix.delete()
            sql(account.dbUser, account.dbPassword, "USE auth;\n" + ForeverAuth.realmSql(client.build), "auth")?.let { return it }
            writeConfigs(account, client)
            return null
        } catch (e: IOException) { return e.message ?: "The database setup failed" }
    }

    private fun importFile(account: ForeverAuth.Account, db: String, file: File): String? {
        val cmd = ForeverServer.command(layout, "mariadb", ForeverServer.clientArgs(account.dbUser, account.dbPassword, "--max-allowed-packet=256M", db))
        val log = File(layout.logs, "import-${file.name}.log")
        val code = runToEnd(cmd, log) { out -> file.reader().buffered().use { r -> out.bufferedWriter().let { w -> SqlCompat.stream(r, w) } } }
        return if (code == 0) null else "${WowLogs.exitInWords(code)}: ${WowLogs.tail(log, 4)}"
    }

    private fun sql(user: String, password: String, statement: String, db: String? = null): String? {
        // root has no password and is only reachable through the socket in this app's private folder.
        val args = if (user == "root") listOf("--no-defaults", "-u", "root", "-S", File(layout.run, "mariadb.sock").path) + listOfNotNull(db)
        else ForeverServer.clientArgs(user, password, *listOfNotNull(db).toTypedArray())
        val log = File(layout.logs, "sql.log")
        val code = runToEnd(ForeverServer.command(layout, "mariadb", args), log) { it.write(statement.toByteArray()) }
        return if (code == 0) null else "A database command failed (${WowLogs.exitInWords(code)}): ${WowLogs.tail(log, 4)}"
    }

    // ---- 5: add-on, configs ----------------------------------------------------------------------------------------------
    override fun addon(client: ForeverClient.Result.Ok, say: (String, Float?) -> Unit): String? = try {
        val zip = ForeverDownloads.fetch(ForeverRepackData.ADDON_URL, File(layout.downloads, "ForeverBots-addon.zip"), ForeverRepackData.ADDON_SHA256)
        ForeverBots.install(zip, client.root)
        null
    } catch (e: IOException) { e.message ?: "The add-on couldn't be installed" }

    private fun writeConfigs(account: ForeverAuth.Account, client: ForeverClient.Result.Ok) {
        layout.etc.mkdirs(); layout.logs.mkdirs(); layout.run.mkdirs(); File(layout.run, "tmp").mkdirs()
        File(layout.server, "blizz").mkdirs()
        File(layout.server, "blizz/mariadb").apply { writeText(ForeverServer.clientWrapperScript(layout)); setExecutable(true, false) }
        val params = ForeverConfig.Params(
            dataDir = layout.data.path, logsDir = layout.logs.path, sourceDir = File(layout.server, "src").path,
            pidFile = File(layout.run, "worldserver.pid").path, bnetPidFile = File(layout.run, "bnetserver.pid").path,
            dbUser = account.dbUser, dbPassword = account.dbPassword, mysqlClient = ForeverServer.clientWrapperPath(layout), portal = ForeverConfig.PORTAL,
            certFile = File(layout.keys, "bnetserver.cert.pem").path, keyFile = File(layout.keys, "bnetserver.key.pem").path,
            realmAlsoAccept = supportedBuilds().filter { it != client.build },
        )
        fun dist(name: String) = File(layout.server, "etc/$name.conf.dist").takeIf { it.isFile }?.readText().orEmpty()
        File(layout.etc, "worldserver.conf").writeText(ForeverConfig.edit(dist("worldserver"), ForeverConfig.worldserverValues(params)))
        File(layout.etc, "bnetserver.conf").writeText(ForeverConfig.edit(dist("bnetserver"), ForeverConfig.bnetserverValues(params)))
        val (preset, switches) = bots()
        val profile = ForeverConfig.profile(totalRamMb, preset, switches.first, switches.second)
        // The package's own files of this folder are in place already (the settings folder is the package's `etc`). They were once
        // "copied" here from that same folder: a copy of a file onto itself, which deletes it first and then finds nothing to copy
        // (the phone, 16 November 2026: "zz-0-playerbot-defaults.conf: open failed: ENOENT", the file gone;
        // [ForeverPackage.restoreEtc] puts it back).
        File(layout.etc, "worldserver.conf.d").apply { mkdirs() }.let { d -> File(d, "zz-9-local.conf").writeText(ForeverConfig.localConf(profile)) }
        writeCertificates()
    }

    private fun writeCertificates() {
        if (ForeverAuth.hasCertificate(layout)) return
        layout.keys.mkdirs()
        val tag = java.text.SimpleDateFormat("yyyy-MM-dd", java.util.Locale.ROOT).format(java.util.Date())
        File(layout.keys, "ca.cnf").writeText(ForeverAuth.caConfig(tag))
        File(layout.keys, "server.cnf").writeText(ForeverAuth.serverConfig())
        File(layout.keys, "leaf.ext").writeText(ForeverAuth.leafExt())
        for (cmd in ForeverAuth.certificateCommands(layout)) {
            val code = runToEnd(ForeverServer.command(layout, "openssl", cmd.drop(1)), File(layout.logs, "certificate.log"))
            if (code != 0) throw IOException("The login certificate couldn't be made (${WowLogs.exitInWords(code)}): ${WowLogs.tail(File(layout.logs, "certificate.log"), 4)}")
        }
        // The chain bnetserver sends: the leaf, then the root.
        File(layout.keys, "bnetserver.cert.pem").writeText(
            ForeverAuth.chain(File(layout.keys, "bnetserver.leaf.pem").readText(), ForeverAuth.rootCertificate(layout).readText()))
        File(layout.keys, "bnetserver.key.pem").apply { setReadable(false, false); setReadable(true, true) }
        File(layout.keys, "forever-root-ca.key.pem").apply { setReadable(false, false); setReadable(true, true) }
    }

    // ---- 5b: the local account (made in the auth database; see ForeverAccount) -------------------------------------------
    override fun account(): String? {
        val account = ForeverAuth.loadOrCreate(layout)
        return sql(account.dbUser, account.dbPassword, ForeverAccount.sql(account.name, account.password), "auth")
    }

    // ---- 6: start --------------------------------------------------------------------------------------------------------
    override fun startAuth(): String? = startProgram(ForeverServer.AUTH)
    override fun startWorld(): String? = startProgram(ForeverServer.WORLD, minutes = 20)

    /** Stops everything, in the reverse of the start order; the database last, with SIGTERM so it flushes. */
    fun stopAll() {
        for (p in ForeverServer.stopOrder) {
            val proc = processes.remove(p.key) ?: continue
            if (p === ForeverServer.WORLD) runCatching { proc.outputStream.write("server shutdown 1\n".toByteArray()); proc.outputStream.flush() }
            if (!proc.waitFor(30, java.util.concurrent.TimeUnit.SECONDS)) { proc.destroy(); if (!proc.waitFor(30, java.util.concurrent.TimeUnit.SECONDS)) proc.destroyForcibly() }
        }
    }

    private fun startProgram(p: ForeverServer.Program, minutes: Long = 3): String? {
        if (processes[p.key]?.isAlive == true) return null
        prepareRuntime()
        // One of ours left running by an app Android ended (it holds the port): ended first, the way it is stopped.
        if (portOpen(p.port) && ForeverLeftovers.end(File(layout.run, p.pid), layout.bin, signal)) {
            ForeverLogs(File(layout.logs, "forever-events.log")).event("${p.binary}: one left running from before was ended")
            repeat(20) { if (portOpen(p.port)) Thread.sleep(500) }
        }
        if (portOpen(p.port)) return "Port ${p.port} is already in use; ${p.binary} can't start."
        val log = File(layout.logs, p.log)
        val cmd = ForeverServer.command(layout, p)
        val builder = ProcessBuilder(cmd.argv).directory(cmd.directory.apply { mkdirs() }).redirectErrorStream(true).redirectOutput(log)
        builder.environment().putAll(cmd.env)
        val proc = try { builder.start() } catch (e: IOException) { return "${p.binary} couldn't be started: ${e.message}" }
        processes[p.key] = proc
        val watch = LineWatch(p.ready)
        var offset = 0L
        val ready = { val (text, next) = WowLogs.readFrom(log, offset); offset = next; watch.feed(text); watch.found && portOpen(p.port) }
        return when (ForeverLeftovers.await((minutes * 120).toInt(), ready, { proc.isAlive })) {
            ForeverLeftovers.Wait.READY -> null
            ForeverLeftovers.Wait.ENDED -> "${p.binary} stopped (${WowLogs.exitInWords(proc.exitValue())}). ${ForeverServer.explain(ForeverLogs.tailOf(log)) ?: WowLogs.tail(log, 8)}"
            ForeverLeftovers.Wait.TIMED_OUT -> "${p.binary} did not become ready in $minutes minutes. Last output: ${WowLogs.tail(log, 6)}"
        }
    }

    private fun portOpen(port: Int): Boolean = runCatching { Socket().use { it.connect(InetSocketAddress("127.0.0.1", port), 300); true } }.getOrDefault(false)

    private fun prepareRuntime() {
        listOf(layout.run, File(layout.run, "tmp"), layout.logs, layout.data, layout.checkpoints).forEach { it.mkdirs() }
        layout.bin.listFiles()?.forEach { it.setExecutable(true, false) }
    }

    /** Runs a command to its end with its output in [log]; [stdin] writes what it reads. Returns the exit code. */
    private fun runToEnd(cmd: WowCtl.Command, log: File, stdin: ((OutputStream) -> Unit)? = null): Int {
        log.parentFile?.mkdirs()
        val builder = ProcessBuilder(cmd.argv).directory(cmd.directory.apply { mkdirs() }).redirectErrorStream(true).redirectOutput(log)
        builder.environment().putAll(cmd.env)
        val proc = builder.start()
        proc.outputStream.use { out -> if (stdin != null) runCatching { stdin(out) } }
        return proc.waitFor()
    }

}
