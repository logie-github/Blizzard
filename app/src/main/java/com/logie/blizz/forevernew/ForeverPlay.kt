package com.logie.blizz.forevernew

import android.app.ActivityManager
import android.content.Context
import android.os.Build
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import java.io.File

/**
 * The Forever page's one action ("Install & Play"): runs [ForeverInstaller] on a background thread and publishes where it is.
 * Stop ends the programs in the right order. NOT run on a phone.
 */
object ForeverPlay {
    data class Status(val state: ForeverState, val text: String, val progress: Float?, val running: Boolean)

    private val _status = MutableStateFlow(Status(ForeverState.NOT_INSTALLED, "", null, false))
    val status: StateFlow<Status> = _status

    @Volatile private var steps: ForeverSteps? = null
    @Volatile private var thread: Thread? = null

    fun refresh(context: Context) {
        if (_status.value.running) return
        val saved = ForeverStateStore(ForeverLayout.of(context).stateFile).load()
        _status.value = Status(saved.state, saved.detail, null, false)
    }

    fun start(context: Context) {
        if (_status.value.running) return
        val app = context.applicationContext
        val layout = ForeverLayout.of(app)
        val info = ActivityManager.MemoryInfo().also { (app.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager).getMemoryInfo(it) }
        val runner = ForeverSteps(layout, Build.SUPPORTED_ABIS.toList(), (info.totalMem shr 20).toInt())
        steps = runner
        _status.value = Status(ForeverState.DOWNLOADING, "Starting", null, true)
        thread = Thread({
            val installer = ForeverInstaller(layout, runner, ForeverStateStore(layout.stateFile), ForeverLogs(File(layout.logs, "forever-events.log")))
            val result = runCatching {
                installer.run { state, text, progress -> _status.value = Status(state, text, progress, true) }
            }.getOrElse { ForeverInstaller.Result(ForeverInstaller.Outcome.FAILED, it.message ?: it.javaClass.simpleName) }
            val state = when (result.outcome) {
                ForeverInstaller.Outcome.READY -> ForeverState.READY
                ForeverInstaller.Outcome.AWAITING_CLIENT -> ForeverState.AWAITING_CLIENT
                ForeverInstaller.Outcome.FAILED -> ForeverState.FAILED
            }
            _status.value = Status(state, result.message, null, false)
        }, "forever-install").also { it.isDaemon = true; it.start() }
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
