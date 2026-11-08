package com.logie.blizz.steamgrid

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder

/**
 * SteamGridDB (steamgriddb.com): the pictures other people make for games' boxes, heroes (wide banners) and logos, through its API
 * (v2) with the person's own key. Used by the Art screen to browse a game's pictures instead of picking a file. The key is the
 * person's, kept in the app's own preferences; it goes to steamgriddb.com's API in an `Authorization: Bearer` header and nowhere else.
 */
object SteamGrid {
    const val API = "https://www.steamgriddb.com/api/v2"

    /** What a picture is for, and which of the site's lists it comes from. */
    enum class Slot(val path: String, val dimensions: List<String>, val mimes: List<String> = emptyList()) {
        /** A game's box: the site's grids, portrait. */
        BOX("grids", listOf("600x900", "342x482", "660x930")),
        /** The home picture and the loading picture: the site's heroes, wide. */
        HERO("heroes", listOf("1920x620", "3840x1240", "1600x650")),
        /** A logo, with its transparency. */
        LOGO("logos", emptyList(), listOf("image/png", "image/webp")),
    }

    class Game(val id: Long, val name: String, val verified: Boolean)

    class Picture(val id: Long, val url: String, val thumb: String, val width: Int, val height: Int, val style: String, val author: String, val score: Int, val mime: String)

    class Page(val pictures: List<Picture>, val total: Int, val page: Int, val limit: Int) {
        val hasMore: Boolean get() = (page + 1) * limit < total
    }

    /** "600 × 900", and the style where it has one ("alternate"). */
    fun resolution(p: Picture): String =
        (if (p.width > 0 && p.height > 0) "${p.width} × ${p.height}" else "size unknown") + (if (p.style.isNotEmpty()) " · ${p.style}" else "")

    class SteamGridException(message: String, val code: Int = 0) : IOException(message)

    // The key ------------------------------------------------------------------------------------

    private const val PREFS = "steamgrid"
    private fun prefs(context: Context) = context.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE)

    fun key(context: Context): String? = prefs(context).getString("key", null)?.takeIf { it.isNotBlank() }
    fun hasKey(context: Context) = key(context) != null
    fun setKey(context: Context, key: String) { prefs(context).edit().putString("key", key.trim()).apply() }
    fun clearKey(context: Context) { prefs(context).edit().remove("key").apply() }

    // Requests (pure: the tests build and read these) --------------------------------------------

    fun searchUrl(term: String) = "$API/search/autocomplete/${URLEncoder.encode(term.trim(), "UTF-8").replace("+", "%20")}"

    /** The list of [slot]'s pictures of the game [gameId], a page of them; adult, humorous and flashing ones left out. */
    fun picturesUrl(slot: Slot, gameId: Long, page: Int = 0): String {
        val params = buildList {
            if (slot.dimensions.isNotEmpty()) add("dimensions=" + slot.dimensions.joinToString(","))
            if (slot.mimes.isNotEmpty()) add("mimes=" + slot.mimes.joinToString(","))
            add("nsfw=false"); add("humor=false"); add("epilepsy=false")
            if (slot != Slot.LOGO) add("types=static")
            if (page > 0) add("page=$page")
        }
        return "$API/${slot.path}/game/$gameId?" + params.joinToString("&")
    }

    /** Only the site's own addresses are ever fetched. */
    fun isSiteUrl(url: String): Boolean = runCatching {
        val u = URL(url)
        u.protocol == "https" && (u.host == "steamgriddb.com" || u.host.endsWith(".steamgriddb.com"))
    }.getOrDefault(false)

    fun parseGames(json: String): List<Game> {
        val root = JSONObject(json)
        if (!root.optBoolean("success", false)) throw SteamGridException(errors(root) ?: "SteamGridDB didn't answer.")
        val data = root.optJSONArray("data") ?: return emptyList()
        return (0 until data.length()).mapNotNull { i ->
            val g = data.optJSONObject(i) ?: return@mapNotNull null
            val name = g.optString("name").takeIf { it.isNotEmpty() } ?: return@mapNotNull null
            Game(g.optLong("id"), name, g.optBoolean("verified"))
        }
    }

    fun parsePictures(json: String): Page {
        val root = JSONObject(json)
        if (!root.optBoolean("success", false)) throw SteamGridException(errors(root) ?: "SteamGridDB didn't answer.")
        val data = root.optJSONArray("data") ?: JSONArray()
        val pictures = (0 until data.length()).mapNotNull { i ->
            val p = data.optJSONObject(i) ?: return@mapNotNull null
            val url = p.optString("url"); val thumb = p.optString("thumb").ifEmpty { url }
            if (!isSiteUrl(url) || !isSiteUrl(thumb)) return@mapNotNull null
            val style = when (val s = p.opt("style")) { is JSONArray -> (0 until s.length()).joinToString(", ") { s.optString(it) }; is String -> s; else -> "" }
            Picture(
                p.optLong("id"), url, thumb, p.optInt("width"), p.optInt("height"), style,
                p.optJSONObject("author")?.optString("name").orEmpty(), p.optInt("score"), p.optString("mime"),
            )
        }
        return Page(pictures, root.optInt("total", pictures.size), root.optInt("page", 0), root.optInt("limit", 50).coerceAtLeast(1))
    }

    private fun errors(root: JSONObject): String? =
        root.optJSONArray("errors")?.let { e -> (0 until e.length()).joinToString(", ") { e.optString(it) } }?.takeIf { it.isNotEmpty() }

    // The network (background threads only) ------------------------------------------------------

    private fun open(url: String, key: String?): HttpURLConnection {
        val c = URL(url).openConnection() as HttpURLConnection
        c.connectTimeout = 15_000; c.readTimeout = 30_000
        c.setRequestProperty("User-Agent", "Blizzard-launcher (steamgriddb client)")
        if (key != null) c.setRequestProperty("Authorization", "Bearer $key")
        return c
    }

    private fun get(url: String, key: String): String {
        val c = open(url, key)
        try {
            val code = c.responseCode
            if (code == 401 || code == 403) throw SteamGridException("SteamGridDB didn't accept the key. Check it in Settings.", code)
            if (code == 429) throw SteamGridException("SteamGridDB says that's too many requests: try again in a minute.", code)
            if (code !in 200..299) {
                val body = runCatching { c.errorStream?.bufferedReader()?.readText() }.getOrNull()
                throw SteamGridException(runCatching { errors(JSONObject(body ?: "")) }.getOrNull() ?: "SteamGridDB answered $code.", code)
            }
            return c.inputStream.bufferedReader().readText()
        } finally { c.disconnect() }
    }

    fun search(key: String, term: String): List<Game> = parseGames(get(searchUrl(term), key))

    fun pictures(key: String, slot: Slot, gameId: Long, page: Int = 0): Page = parsePictures(get(picturesUrl(slot, gameId, page), key))

    /** [url] (one of the site's) saved to [dest]; at most 25 MB. */
    fun download(url: String, dest: File) {
        if (!isSiteUrl(url)) throw SteamGridException("That isn't a SteamGridDB address.")
        val c = open(url, null)
        try {
            if (c.responseCode !in 200..299) throw SteamGridException("SteamGridDB answered ${c.responseCode} for the picture.", c.responseCode)
            dest.parentFile?.mkdirs()
            val part = File(dest.path + ".part")
            var total = 0L
            c.inputStream.use { input -> part.outputStream().use { out ->
                val buf = ByteArray(64 * 1024)
                while (true) {
                    val n = input.read(buf); if (n < 0) break
                    total += n
                    if (total > 25L shl 20) { part.delete(); throw SteamGridException("That picture is too big.") }
                    out.write(buf, 0, n)
                }
            } }
            dest.delete()
            if (!part.renameTo(dest)) throw SteamGridException("Couldn't save the picture.")
        } finally { c.disconnect() }
    }

    /** The name to look a game up by: its title and subtitle ("Diablo II Resurrected"); World of Warcraft's versions are all "World of Warcraft". */
    fun searchTerm(title: String, subtitle: String?): String =
        if (title == "World of Warcraft" || subtitle == null) title else "$title $subtitle"
}
