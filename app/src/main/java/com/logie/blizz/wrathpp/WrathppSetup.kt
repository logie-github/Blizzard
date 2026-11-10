package com.logie.blizz.wrathpp

import android.content.Context
import com.logie.blizz.wow.WowLayout

/**
 * What Play on Wrath++'s page does before its realm starts: its server package ([WrathppServerPackage], downloaded the
 * first time and when a newer one is published) and its own copy of the game ([WrathppClient], made once from Wrath+'s).
 */
object WrathppSetup {
    fun run(context: Context, say: (String, Float?) -> Unit) {
        val layout = WowLayout.of(context)
        WrathppServerPackage.ensure(layout, onStage = { say(it, null) }) { done, total ->
            say("Downloading Wrath++'s server… ${done shr 20} / ${total shr 20} MB", if (total > 0) done.toFloat() / total else null)
        }
        if (!WrathppClient.isMade(layout.wrathppClient)) {
            say("Making Wrath++'s copy of the game (once)", null)
            WrathppClient.make(layout.client, layout.wrathppClient) { say(it, null) }
        }
    }
}
