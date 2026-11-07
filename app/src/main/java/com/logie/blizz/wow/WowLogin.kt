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

    /** The export's `{"<key>":{"type":"string","value":...}}` file: the saved name and password. */
    fun read(file: File): Login? = runCatching {
        val o = JSONObject(file.readText())
        val name = o.getJSONObject("name").getString("value")
        val password = o.getJSONObject("password").getString("value")
        if (name.isNotEmpty() && password.isNotEmpty()) Login(name, password) else null
    }.getOrNull()
}
