package com.logie.blizz

import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.drawable.Drawable
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

/** An app installed on the phone that can be opened. */
data class InstalledApp(val packageName: String, val label: String)

/** Which installed app each game opens. */
object Links {
    private const val PREFS = "links"
    private const val NONE = "-"

    private val _version = MutableStateFlow(0)
    /** Changes whenever a link does. */
    val version: StateFlow<Int> = _version

    private fun prefs(context: Context) = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)

    /** The game's app: the one chosen, else the suggested one when it's installed. */
    fun packageFor(context: Context, game: Game): String? {
        val chosen = prefs(context).getString(game.id, null)
        val name = when (chosen) {
            NONE -> null
            null -> game.suggestedPackage
            else -> chosen
        } ?: return null
        return name.takeIf { isLaunchable(context, it) }
    }

    fun set(context: Context, game: Game, packageName: String?) {
        prefs(context).edit().putString(game.id, packageName ?: NONE).apply()
        _version.value++
    }

    fun isLaunchable(context: Context, packageName: String): Boolean =
        context.packageManager.getLaunchIntentForPackage(packageName) != null

    /** Opens the game's app; false when it has none, or it's gone. */
    fun launch(context: Context, game: Game): Boolean {
        val name = packageFor(context, game) ?: return false
        val intent = context.packageManager.getLaunchIntentForPackage(name) ?: return false
        context.startActivity(intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
        return true
    }

    fun label(context: Context, packageName: String): String = runCatching {
        val pm = context.packageManager
        pm.getApplicationLabel(pm.getApplicationInfo(packageName, 0)).toString()
    }.getOrDefault(packageName)

    fun icon(context: Context, packageName: String): Drawable? =
        runCatching { context.packageManager.getApplicationIcon(packageName) }.getOrNull()

    /** Every app with a launcher entry, this one excepted, by name. */
    fun installed(context: Context): List<InstalledApp> {
        val pm = context.packageManager
        val main = Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER)
        return pm.queryIntentActivities(main, PackageManager.MATCH_ALL)
            .map { it.activityInfo.packageName }
            .distinct()
            .filter { it != context.packageName }
            .map { InstalledApp(it, label(context, it)) }
            .sortedWith(compareBy(String.CASE_INSENSITIVE_ORDER) { it.label })
    }
}
