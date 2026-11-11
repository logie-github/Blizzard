package com.logie.blizz.warsmash

import android.content.Context
import android.content.Intent
import com.logie.blizz.importer.LibraryEntry
import com.logie.blizz.importer.Warcraft3Importer

/** Warcraft III's two games, both played in the embedded Warsmash engine ([WarsmashActivity]). */
object WarsmashRuntime {
    const val RUNTIME = "warsmash-native"
    const val EXTRA_DATA = "com.logie.blizz.WARSMASH_DATA"
    const val EXTRA_EDITION = "com.logie.blizz.WARSMASH_EDITION"

    /** Which game the engine plays: its own setting, GameVersion (0 Reign of Chaos, 1 The Frozen Throne). */
    enum class Edition(val gameVersion: Int) { ROC(0), TFT(1) }

    /** Reign of Chaos's entry plays Reign of Chaos; every other (The Frozen Throne's) The Frozen Throne. */
    fun editionOf(gameId: String) = if (gameId == Warcraft3Importer.ROC_ID) Edition.ROC else Edition.TFT

    fun play(context: Context, entry: LibraryEntry) {
        context.startActivity(Intent(context, WarsmashActivity::class.java)
            .putExtra(EXTRA_DATA, entry.installPath)
            .putExtra(EXTRA_EDITION, editionOf(entry.gameId).name)
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
    }
}
