package com.logie.blizz.game

import com.winlator.core.Callback
import com.winlator.core.ProcessHelper
import java.util.ArrayDeque

/**
 * The last lines Wine and Box64 printed while a game ran (Wine's errors and the libraries it loads),
 * kept so the game menu can send them with a report: a black screen leaves no crash to report.
 */
object GameLog {
    private const val MAX = 400
    private val lines = ArrayDeque<String>()
    private val callback = Callback<String> { line: String ->
        synchronized(lines) {
            if (lines.size >= MAX) lines.removeFirst()
            lines.addLast(line.take(300))
        }
    }

    /** Starts listening to the programs' output (once; after Winlator has set up its own listeners). */
    fun start() {
        synchronized(lines) { lines.clear() }
        ProcessHelper.addDebugCallback(callback)
    }

    fun snapshot(): String = synchronized(lines) { lines.joinToString("\n") }
}
