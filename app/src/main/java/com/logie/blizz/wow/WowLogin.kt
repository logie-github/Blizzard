package com.logie.blizz.wow

import android.content.Context
import org.json.JSONObject
import java.io.File

/**
 * The account the World of Warcraft app had saved to log in by itself (its `login` preferences, kept in
 * the export as `prefs/login.json`): the game types its password at the login screen. Read from the
 * imported copy; never sent anywhere.
 */
object WowLogin {
    data class Login(val name: String, val password: String)

    fun get(context: Context): Login? = read(File(WowLayout.of(context).exportDir, "prefs/login.json"))

    /** OctoWoW's saved account (`turtle_login` in its own export, `games/wow_octowow`). */
    fun octo(context: Context): Login? = read(File(WowLayout.octo(context).exportDir, "prefs/turtle_login.json"))

    /** Legion's saved e-mail and password (`felsong_login` in its own export, `games/wow_legion`). */
    fun legion(context: Context): Login? = read(File(WowLayout.legion(context).exportDir, "prefs/felsong_login.json"))

    /** The versions with a login: World of Warcraft's game ids as the shelf has them. */
    const val WRATH = "wow"
    const val OCTO = "wow_octowow"
    const val LEGION = "wow_legion"

    private fun prefs(context: Context) = context.applicationContext.getSharedPreferences("wow_login", Context.MODE_PRIVATE)

    /** The account the person gave Blizzard for [version] (its own, apart from anything exported); null when none. */
    fun own(context: Context, version: String): Login? {
        val p = prefs(context)
        val name = p.getString("${version}_name", null)?.trim().orEmpty()
        val password = p.getString("${version}_password", null).orEmpty()
        return if (name.isNotEmpty() && password.isNotEmpty()) Login(name, password) else null
    }

    fun setOwn(context: Context, version: String, name: String, password: String) {
        prefs(context).edit().putString("${version}_name", name.trim()).putString("${version}_password", password).apply()
    }

    fun clearOwn(context: Context, version: String) {
        prefs(context).edit().remove("${version}_name").remove("${version}_password").apply()
    }

    /** What the World of Warcraft app had saved for [version], from the export. */
    fun exported(context: Context, version: String): Login? = when (version) {
        OCTO -> octo(context)
        LEGION -> legion(context)
        else -> get(context)
    }

    /** The account every start of [version] logs in with: the person's own if given, else the export's. */
    fun forVersion(context: Context, version: String): Login? = own(context, version) ?: exported(context, version)

    /** The version a client's `clientVersion` is of (see [com.logie.blizz.game.WowPlay.splashIdOf]). */
    fun versionOf(clientVersion: String?): String = when (clientVersion) {
        com.logie.blizz.game.OctoClientSetup.VERSION -> OCTO
        com.logie.blizz.game.LegionClientSetup.VERSION -> LEGION
        else -> WRATH
    }

    /** The export's `{"<key>":{"type":"string","value":...}}` file: the saved name and password. */
    fun read(file: File): Login? = runCatching {
        val o = JSONObject(file.readText())
        val name = o.getJSONObject("name").getString("value")
        val password = o.getJSONObject("password").getString("value")
        if (name.isNotEmpty() && password.isNotEmpty()) Login(name, password) else null
    }.getOrNull()
}
