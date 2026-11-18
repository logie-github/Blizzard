package com.logie.blizz.forevernew

import android.app.ActivityManager
import android.content.Context
import android.net.Uri
import android.os.Build
import com.logie.blizz.game.LaunchProfile
import com.logie.blizz.game.WindowsRuntime
import com.logie.blizz.game.WowPlay
import com.logie.blizz.wow.WowLogin
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import java.io.File

/**
 * The Forever page's one action ("Install & Play"): runs [ForeverInstaller] on a background thread and, once the realm is up,
 * starts the game on the app's Winlator ([WindowsRuntime.play], as Legion's and Wrath++'s clients are). The client is the one
 * thing it can't fetch: the first time the user picks their own World of Warcraft folder once ([importClient]), and the
 * same action then carries on by itself. Stop ends the programs in the right order. NOT run on a phone.
 */
object ForeverPlay {
    data class Status(val state: ForeverState, val text: String, val progress: Float?, val running: Boolean)

    private val _status = MutableStateFlow(Status(ForeverState.NOT_INSTALLED, "", null, false))
    val status: StateFlow<Status> = _status

    @Volatile private var steps: ForeverSteps? = null

    fun refresh(context: Context) {
        if (_status.value.running) return
        val saved = ForeverStateStore(ForeverLayout.of(context).stateFile).load()
        _status.value = Status(saved.state, saved.detail, null, false)
    }

    private fun totalRamMb(app: Context): Int {
        val info = ActivityManager.MemoryInfo().also { (app.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager).getMemoryInfo(it) }
        return (info.totalMem shr 20).toInt()
    }

    /** Install, start the realm, and start the game. Safe to call again. */
    fun start(context: Context) {
        if (_status.value.running) return
        val app = context.applicationContext
        val layout = ForeverLayout.of(app)
        val runner = ForeverSteps(layout, Build.SUPPORTED_ABIS.toList(), totalRamMb(app), signal = { pid, sig -> android.os.Process.sendSignal(pid, sig) })
        steps = runner
        _status.value = Status(ForeverState.DOWNLOADING, "Starting", null, true)
        // Kept alive in the foreground for as long as its programs run (the realm's other versions have such a service).
        ForeverService.start(app)
        Thread({
            val logs = ForeverLogs(File(layout.logs, "forever-events.log"))
            val installer = ForeverInstaller(layout, runner, ForeverStateStore(layout.stateFile), logs)
            val result = runCatching {
                installer.run { state, text, progress -> _status.value = Status(state, text, progress, true) }
            }.getOrElse { ForeverInstaller.Result(ForeverInstaller.Outcome.FAILED, it.message ?: it.javaClass.simpleName) }
            when (result.outcome) {
                ForeverInstaller.Outcome.READY -> launchGame(app, layout, runner, logs)
                ForeverInstaller.Outcome.AWAITING_CLIENT -> _status.value = Status(ForeverState.AWAITING_CLIENT, result.message, null, false)
                ForeverInstaller.Outcome.FAILED -> {
                    _status.value = Status(ForeverState.FAILED, result.message, null, false)
                    sendFailure(app, layout, result.message)
                }
            }
        }, "forever-install").also { it.isDaemon = true; it.start() }
    }

    /**
     * A failed install or start, as a report (until now only on the person's screen): the step's message, the event log, the last of
     * each server's own log, and the phone's memory and processes (`attach`). A crash that takes the whole app with it leaves
     * nothing to send; the system's record of how the last run ended goes in the next start's report ([com.logie.blizz.reports.Diagnostics]).
     */
    private fun sendFailure(app: Context, layout: ForeverLayout, message: String) {
        runCatching {
            fun tail(name: String, bytes: Int = 3000) = ForeverLogs.tailOf(File(layout.logs, name), bytes).trim().takeIf { it.isNotEmpty() }
            val log = buildString {
                append("[events]\n").append(tail("forever-events.log", 4000) ?: "(none)")
                for (name in listOf("worldserver.log", "bnetserver.log", "mariadbd.err")) tail(name)?.let { append("\n\n[").append(name).append("]\n").append(it) }
            }
            com.logie.blizz.reports.BugReports.report(
                app, "WoW Forever", message.take(300), listOf("Build" to com.logie.blizz.BuildConfig.VERSION_CODE.toString(), "RAM MB" to totalRamMb(app).toString()),
                log = log, attach = true, force = true,
            )
        }
    }

    /**
     * What the game itself wrote the last time it ran, sent once: its newest crash or error file (the `.txt` files of `_forever_/Errors`, the
     * first lines: the error's own words) and the end of its storage and connection logs. The game ends without a word on the
     * phone's screen; these files are where it says why.
     */
    internal fun clientTrouble(product: File, lastSent: String?): Pair<String, String>? {
        val newest = File(product, "Errors").listFiles { f -> f.isFile && f.name.endsWith(".txt") }?.maxByOrNull { it.lastModified() } ?: return null
        if (newest.name == lastSent) return null
        val text = buildString {
            append("[").append(newest.name).append("]\n").append(newest.readLines().take(40).joinToString("\n") { it.take(300) })
            for (name in listOf("Tact.log", "Connection.log", "WowConnection.log")) {
                val tail = ForeverLogs.tailOf(File(File(product, "Logs"), name), 2500).lines().filterNot { "Adding server node" in it }.joinToString("\n").trim()
                if (tail.isNotEmpty()) append("\n\n[").append(name).append("]\n").append(tail)
            }
        }
        return newest.name to text
    }

    private fun sendClientTrouble(app: Context, layout: ForeverLayout, product: File, logs: ForeverLogs) {
        runCatching {
            val marker = File(layout.manifests, "client-error-sent.txt")
            val (name, text) = clientTrouble(product, marker.takeIf { it.isFile }?.readText()?.trim()) ?: return
            marker.parentFile?.mkdirs(); marker.writeText(name)
            logs.event("client: its error file $name from the last run is sent")
            com.logie.blizz.reports.BugReports.report(
                app, "WoW Forever", "The game's own error file from its last run: $name", listOf("Build" to com.logie.blizz.BuildConfig.VERSION_CODE.toString()),
                log = text, attach = true, force = true,
            )
        }
    }

    private fun launchGame(app: Context, layout: ForeverLayout, runner: ForeverSteps, logs: ForeverLogs) {
        val client = runner.client()
        if (client == null) { _status.value = Status(ForeverState.AWAITING_CLIENT, "The client isn't there.", null, false); return }
        sendClientTrouble(app, layout, ForeverLaunch.product(client.root), logs)
        val (width, height) = WindowsRuntime.gameSize(app, WowPlay.GAME_ID, LaunchProfile.WOW)
        val failure = ForeverLaunch.prepare(client.root, width, height) { runCatching { app.assets.open(ForeverLaunch.ASSET).use { it.readBytes() } }.getOrNull() }
        if (failure != null) {
            logs.event("FAILED launch: $failure")
            _status.value = Status(ForeverState.FAILED, failure, null, false); return
        }
        // A game downloaded before the index files had their update section (which the game itself requires) gets it, in place.
        runCatching { com.logie.blizz.forevernew.tact.CascWriter.repairIndexes(File(client.root, "Data/data")) }
            .onSuccess { n -> if (n > 0) logs.event("client: $n index files given the section the game requires") }
            .onFailure { e -> logs.event("client: the index files couldn't be completed: ${e.message}") }
        // The files the client reads as it opens its storage (the patch index among them) must be on the phone: its games can't
        // reach Blizzard's servers. Asked of Blizzard's servers once per build, by the app; a few kilobytes for a game downloaded before.
        val meta = File(layout.manifests, "client-play-metadata-${client.build}.done")
        if (client.root.canonicalPath == layout.client.canonicalPath && !meta.isFile) {
            _status.value = Status(ForeverState.PLAYING, "Completing the game's files", null, false)
            val failed = runCatching { ForeverClientDownload.repairIndex(client.root) { _, _ -> } }
                .onSuccess { n -> logs.event("client: $n start-up files added to the downloaded game"); meta.parentFile?.mkdirs(); meta.writeText("$n\n") }
                .exceptionOrNull()
            if (failed != null) {
                val text = "The game's files couldn't be completed (${failed.message}). This needs the internet once."
                logs.event("FAILED launch: $text")
                _status.value = Status(ForeverState.FAILED, text, null, false); return
            }
        }
        // The game's login screen is filled in with the local account made at install ([WowLogin.forVersion]).
        val account = ForeverAuth.loadOrCreate(layout)
        WowLogin.setOwn(app, WowLogin.FOREVER, account.name, account.password)
        // A Battle.net login screen shows late (like Legion's): the touch layer waits for it the same way.
        WowPlay.legion = true
        logs.event("PLAYING starting the client (build ${client.build})")
        _status.value = Status(ForeverState.PLAYING, "Starting the game", null, false)
        WindowsRuntime.play(app, ForeverLaunch.entry(client.root), width to height)
    }

    /** The one folder pick: copies the user's installation into the app, then carries on with [start]. */
    fun importClient(context: Context, tree: Uri) {
        if (_status.value.running) return
        val app = context.applicationContext
        val layout = ForeverLayout.of(app)
        _status.value = Status(ForeverState.AWAITING_CLIENT, "Copying your game", 0f, true)
        Thread({
            val error = ForeverClientImport.copy(ForeverSafTree(app.contentResolver, tree), layout.client,
                progress = { done, total, file ->
                    _status.value = Status(ForeverState.AWAITING_CLIENT, "Copying your game: ${done shr 20} / ${total shr 20} MB ($file)", if (total > 0) done.toFloat() / total else null, true)
                })
            if (error != null) { _status.value = Status(ForeverState.AWAITING_CLIENT, error, null, false); return@Thread }
            ForeverClientImport.remember(layout)
            val check = ForeverClient.inspect(layout.client, ForeverPackage.installed(layout)?.clientBuilds.orEmpty())
            if (check is ForeverClient.Result.Rejected) { _status.value = Status(ForeverState.AWAITING_CLIENT, check.reason, null, false); return@Thread }
            _status.value = Status(ForeverState.AWAITING_CLIENT, "The game was copied.", null, false)
            start(app)
        }, "forever-import").also { it.isDaemon = true; it.start() }
    }

    fun stop() {
        val runner = steps ?: return
        _status.value = _status.value.copy(state = ForeverState.STOPPING, text = "Stopping the servers")
        Thread({
            runCatching { runner.stopAll() }
            _status.value = Status(ForeverState.NOT_INSTALLED, "Stopped", null, false)
        }, "forever-stop").start()
    }
}
