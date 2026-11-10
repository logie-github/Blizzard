package com.logie.blizz.wrathpp

import android.content.Context
import com.logie.blizz.wow.WowLayout

/**
 * What Play on Wrath++'s page does before its realm starts: its server package ([WrathppServerPackage], downloaded the
 * first time and when a newer one is published) and its own copy of the game ([WrathppClient], made once from Wrath+'s).
 * Each step reports its words and share done, thinned out ([Reports]) so the screen moves without being flooded.
 */
object WrathppSetup {
    fun run(context: Context, say: (String, Float?) -> Unit) {
        val layout = WowLayout.of(context)
        val report = Reports(say)
        WrathppServerPackage.ensure(layout, report::say)
        if (!WrathppClient.isMade(layout.wrathppClient)) {
            report.say("Making Wrath++'s copy of the game (step 4 of 4)", 0f)
            WrathppClient.make(layout.client, layout.wrathppClient, report::say)
        }
        // The add-on (WarcraftXL's runtime and the creator's boxes): Wrath++ still plays without it, as stock 3.3.5.
        runCatching { WrathppAddon.ensure(layout.wrathppClient, report::say) }.onFailure { e ->
            runCatching { java.io.File(layout.realmLogs(com.logie.blizz.wow.Realm.WRATHPP), "addon.log").apply { parentFile?.mkdirs() }.appendText("${e.message}\n") }
        }
    }

    /**
     * Passes a report on when its words' step changed, its share moved by half a percent, or a quarter second passed;
     * the rest are dropped (a download reports every 64 KiB).
     */
    class Reports(private val out: (String, Float?) -> Unit, private val clock: () -> Long = System::currentTimeMillis) {
        private var lastStep: String? = null
        private var lastFraction: Float? = null
        private var lastAt = 0L

        fun say(message: String, fraction: Float?) {
            val step = message.substringBefore(':')
            val now = clock()
            val moved = fraction != null && (lastFraction == null || fraction - lastFraction!! >= 0.005f || fraction >= 1f)
            if (step != lastStep || moved || now - lastAt >= 250) {
                lastStep = step; lastFraction = fraction; lastAt = now
                out(message, fraction)
            }
        }
    }
}
