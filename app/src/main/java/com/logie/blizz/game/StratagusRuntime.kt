// SPDX-License-Identifier: GPL-2.0-or-later

package com.logie.blizz.game

import android.content.Context
import android.os.Handler
import android.os.Looper
import android.widget.Toast
import com.logie.blizz.importer.LibraryEntry
import java.io.File

/**
 * Starts Warcraft I or II natively ([LibraryEntry.runtime] == [RUNTIME]): Stratagus with War1gus or
 * Wargus on SDL's screen ([StratagusActivity]), playing the data the importer made from the user's
 * GOG files in [LibraryEntry.installPath] (marked by the file [LibraryEntry.executable], "extracted").
 * Nothing needs preparing, so there is no state to wait on; a game that stops by itself is reported
 * ([StratagusStops]).
 */
object StratagusRuntime {
    const val RUNTIME = "stratagus"

    fun play(context: Context, entry: LibraryEntry) {
        val app = context.applicationContext
        val dir = File(entry.installPath)
        // A game that stopped last time, not yet reported (the app was gone), goes first.
        Thread { StratagusStops.reportIfStopped(app, dir, entry.gameId, entry.title) }.start()
        if (!File(dir, entry.executable.ifEmpty { "extracted" }).isFile) {
            Toast.makeText(app, "${entry.title} isn't imported: use Repair.", Toast.LENGTH_LONG).show()
            return
        }
        context.startActivity(StratagusActivity.intent(context, entry.gameId, entry.title, dir.path))
        watch(app, dir, entry)
    }

    /** The game runs in a process of its own: when it's gone without being left properly, say so. */
    private fun watch(app: Context, dir: File, entry: LibraryEntry) {
        Thread {
            // The game's process writes `running` as it starts.
            var waited = 0
            while (!File(dir, "running").isFile && waited < 40) { Thread.sleep(500); waited++ }
            while (File(dir, "running").isFile) {
                Thread.sleep(2000)
                if (StratagusStops.reportIfStopped(app, dir, entry.gameId, entry.title)) {
                    Handler(Looper.getMainLooper()).post {
                        Toast.makeText(app, "${entry.title} stopped. A report was sent (when the phone is online).", Toast.LENGTH_LONG).show()
                    }
                    return@Thread
                }
            }
        }.apply { isDaemon = true }.start()
    }
}
