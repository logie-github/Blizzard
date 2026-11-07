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
        synchronized(notes) { notes.clear() }
        ProcessHelper.addDebugCallback(callback)
    }

    /** The app's own notes (what the launcher and the touch layer decided), kept apart so a flood of Wine's lines doesn't push them out. */
    private val notes = ArrayDeque<String>()

    fun note(text: String) {
        synchronized(notes) {
            if (notes.size >= 60) notes.removeFirst()
            notes.addLast("[app] " + text.take(300))
        }
    }

    fun snapshot(): String = synchronized(notes) { notes.joinToString("\n") } +
        (if (notes.isEmpty()) "" else "\n") + synchronized(lines) { lines.joinToString("\n") }
}
