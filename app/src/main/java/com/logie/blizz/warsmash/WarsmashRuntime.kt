package com.logie.blizz.warsmash

import android.content.Context
import android.content.Intent
import com.logie.blizz.importer.LibraryEntry

object WarsmashRuntime {
    const val RUNTIME = "warsmash-native"
    const val EXTRA_DATA = "com.logie.blizz.WARSMASH_DATA"
    fun play(context: Context, entry: LibraryEntry) {
        context.startActivity(Intent(context, WarsmashActivity::class.java)
            .putExtra(EXTRA_DATA, entry.installPath).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
    }
}
