package com.logie.blizz.porter

import android.content.Context
import com.logie.blizz.porter.armory.BattleNet
import com.logie.blizz.porter.net.HttpNet

/**
 * The person's own Battle.net API client (made free at develop.battle.net), for what the Armory's website keeps back: a
 * character's face and hair, their quests and achievements. Kept in the app's own storage only; never sent anywhere but
 * Battle.net's token service.
 */
object BattleNetKey {
    private fun prefs(context: Context) = context.applicationContext.getSharedPreferences("porter_battlenet", Context.MODE_PRIVATE)

    fun get(context: Context): Pair<String, String>? {
        val p = prefs(context)
        val id = p.getString("id", null)?.takeIf { it.isNotBlank() } ?: return null
        val secret = p.getString("secret", null)?.takeIf { it.isNotBlank() } ?: return null
        return id to secret
    }

    fun set(context: Context, id: String, secret: String) {
        prefs(context).edit().putString("id", id.trim()).putString("secret", secret.trim()).apply()
        client = null
    }

    fun clear(context: Context) {
        prefs(context).edit().clear().apply()
        client = null
    }

    @Volatile private var client: BattleNet? = null

    /** A client with the kept key, or null without one. */
    fun client(context: Context): BattleNet? {
        val (id, secret) = get(context) ?: return null
        return client ?: BattleNet(HttpNet(HttpNet.BROWSER), id, secret).also { client = it }
    }

    /** A client for [id] and [secret] that has been given a token (throws when Battle.net refuses them). */
    fun tried(id: String, secret: String): BattleNet = BattleNet(HttpNet(HttpNet.BROWSER), id.trim(), secret.trim()).also { it.check() }
}
