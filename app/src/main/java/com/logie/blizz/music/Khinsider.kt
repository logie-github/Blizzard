package com.logie.blizz.music

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL

/**
 * khinsider (downloads.khinsider.com): the game soundtracks page by page, for the music picker. Blizzard Entertainment's albums come
 * from its publisher page; an album page lists its songs (number, name, length); a song page holds the address of its audio file
 * ([MusicStore.audioUrlFromHtml]). The pages are read the way a browser shows them; if the site answers with its browser check
 * instead, that is said. Parsing is plain Kotlin, unit-tested; the network functions are for background threads.
 */
object Khinsider {
    const val SITE = "https://downloads.khinsider.com"
    const val PUBLISHER = "$SITE/game-soundtracks/publisher/blizzard-entertainment"

    class Album(val slug: String, val title: String, val url: String, val thumb: String?)
    class Song(val number: Int, val title: String, val pageUrl: String, val length: String?, val seconds: Int?, val size: String?)
    class AlbumPage(val title: String, val cover: String?, val songs: List<Song>)

    open class KhinsiderException(message: String) : IOException(message)

    /** A plain request was turned away by the site's browser check: [fetch] then reads the page as a browser does. */
    class BrowserCheckException : KhinsiderException("khinsider asked for a browser check.")

    @Volatile private var appContext: android.content.Context? = null

    /** The app's context, for reading a page in a WebView when a plain request is turned away. */
    fun attach(context: android.content.Context) { appContext = context.applicationContext }

    /** Only the site's own addresses, over https, are fetched (pages, pictures, songs). */
    fun isSiteUrl(url: String): Boolean = runCatching {
        val u = URL(url)
        u.protocol == "https" && listOf("khinsider.com", "vgmtreasurechest.com", "vgmsite.com").any { u.host == it || u.host.endsWith(".$it") }
    }.getOrDefault(false)

    private val ANCHOR = Regex("""<a\s[^>]*?href\s*=\s*["']([^"']+)["'][^>]*>(.*?)</a>""", setOf(RegexOption.IGNORE_CASE, RegexOption.DOT_MATCHES_ALL))
    private val IMG = Regex("""<img\s[^>]*?src\s*=\s*["']([^"']+)["']""", RegexOption.IGNORE_CASE)
    private val TAG = Regex("<[^>]+>")
    private val ROW = Regex("""<tr[^>]*>(.*?)</tr>""", setOf(RegexOption.IGNORE_CASE, RegexOption.DOT_MATCHES_ALL))
    private val CELL = Regex("""<t[dh][^>]*>(.*?)</t[dh]>""", setOf(RegexOption.IGNORE_CASE, RegexOption.DOT_MATCHES_ALL))
    private val ALBUM_HREF = Regex("""^(?:https?://downloads\.khinsider\.com)?/game-soundtracks/album/([^/?#"']+)/?$""", RegexOption.IGNORE_CASE)
    private val TIME = Regex("""^\d{1,3}:\d{2}(?::\d{2})?$""")

    fun text(html: String): String = unescape(TAG.replace(html, " ")).replace(Regex("\\s+"), " ").trim()

    private fun unescape(s: String): String = s
        .replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", "\"").replace("&#039;", "'").replace("&#39;", "'")
        .replace("&nbsp;", " ").replace("&rsquo;", "'").replace("&lsquo;", "'").replace("&ndash;", "–").replace("&mdash;", "—")
        .replace(Regex("&#(\\d+);")) { m -> m.groupValues[1].toIntOrNull()?.toChar()?.toString() ?: m.value }

    private fun absolute(base: String, ref: String): String? =
        runCatching { URL(URL(base), unescape(ref.trim())).toString() }.getOrNull()

    /** The albums a publisher (or search) page lists: each album's name and thumbnail, in the page's order, once each. */
    fun parseAlbums(html: String, base: String = PUBLISHER): List<Album> {
        val titles = LinkedHashMap<String, String>()
        val thumbs = HashMap<String, String>()
        val urls = HashMap<String, String>()
        for (m in ANCHOR.findAll(html)) {
            val href = absolute(base, m.groupValues[1]) ?: continue
            val slug = ALBUM_HREF.matchEntire(href.substringBefore('#'))?.groupValues?.get(1) ?: continue
            urls.putIfAbsent(slug, href)
            val inner = m.groupValues[2]
            IMG.find(inner)?.groupValues?.get(1)?.let { src -> absolute(base, src)?.takeIf { isSiteUrl(it) }?.let { thumbs.putIfAbsent(slug, it) } }
            val label = text(inner)
            if (label.isNotEmpty() && (titles[slug] == null || label.length > titles.getValue(slug).length)) titles[slug] = label
            else if (label.isEmpty()) titles.putIfAbsent(slug, "")
        }
        return titles.entries.filter { it.value.isNotEmpty() }.map { (slug, title) -> Album(slug, title, urls.getValue(slug), thumbs[slug]) }
    }

    /** An album page: its name, its cover, and its songs with their numbers and lengths. */
    fun parseAlbum(html: String, base: String): AlbumPage {
        val title = Regex("""<h2[^>]*>(.*?)</h2>""", setOf(RegexOption.IGNORE_CASE, RegexOption.DOT_MATCHES_ALL)).find(html)?.groupValues?.get(1)?.let { text(it) }
            ?.takeIf { it.isNotEmpty() }
            ?: Regex("""<title[^>]*>(.*?)</title>""", setOf(RegexOption.IGNORE_CASE, RegexOption.DOT_MATCHES_ALL)).find(html)?.groupValues?.get(1)?.let { text(it).substringBefore(" - ").trim() }
            ?: "Album"
        val coverDiv = Regex("""<div[^>]*class\s*=\s*["'][^"']*albumImage[^"']*["'][^>]*>(.*?)</div>""", setOf(RegexOption.IGNORE_CASE, RegexOption.DOT_MATCHES_ALL)).find(html)?.groupValues?.get(1)
        val cover = coverDiv?.let { div -> IMG.find(div)?.groupValues?.get(1) ?: ANCHOR.find(div)?.groupValues?.get(1) }
            ?.let { absolute(base, it) }?.takeIf { isSiteUrl(it) }
        val table = Regex("""<table[^>]*id\s*=\s*["']songlist["'][^>]*>(.*?)</table>""", setOf(RegexOption.IGNORE_CASE, RegexOption.DOT_MATCHES_ALL)).find(html)?.groupValues?.get(1).orEmpty()
        val songs = ArrayList<Song>()
        // Which column is the number ("#"), from the header row, when the table has one (a CD column beside it is also a number).
        val numberColumn = ROW.findAll(table).firstOrNull { it.value.contains("<th", true) }
            ?.let { h -> CELL.findAll(h.groupValues[1]).map { text(it.groupValues[1]) }.toList().indexOf("#").takeIf { it >= 0 } }
        for (row in ROW.findAll(table)) {
            val cells = CELL.findAll(row.groupValues[1]).map { it.groupValues[1] }.toList()
            if (cells.isEmpty() || row.value.contains("songlist_footer", true) || row.value.contains("<th", true)) continue
            val link = ANCHOR.findAll(row.groupValues[1]).firstOrNull { l ->
                val href = unescape(l.groupValues[1])
                href.contains("/game-soundtracks/album/", true) && href.substringBefore('?').endsWith(".mp3", true) && text(l.groupValues[2]).isNotEmpty()
            } ?: continue
            val pageUrl = absolute(base, link.groupValues[1])?.takeIf { isSiteUrl(it) } ?: continue
            val plain = cells.map { text(it) }
            val length = plain.firstOrNull { TIME.matches(it) }
            val number = (numberColumn?.let { plain.getOrNull(it) }?.trimEnd('.')?.toIntOrNull())
                ?: plain.firstOrNull { Regex("""^\d{1,3}\.$""").matches(it) }?.trimEnd('.')?.toIntOrNull()
                ?: (songs.size + 1)
            val size = plain.firstOrNull { Regex("""^\d+(\.\d+)?\s*[KMG]B$""", RegexOption.IGNORE_CASE).matches(it) }
            songs += Song(number, text(link.groupValues[2]), pageUrl, length, length?.let { seconds(it) }, size)
        }
        return AlbumPage(title, cover, songs)
    }

    /** "3:36" is 216 seconds; "1:02:03" is an hour and more. */
    fun seconds(length: String): Int? {
        val parts = length.split(':').map { it.toIntOrNull() ?: return null }
        return when (parts.size) { 2 -> parts[0] * 60 + parts[1]; 3 -> parts[0] * 3600 + parts[1] * 60 + parts[2]; else -> null }
    }

    // The network (background threads) -----------------------------------------------------------

    const val AGENT = "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Mobile Safari/537.36"

    fun get(url: String): String {
        if (!isSiteUrl(url)) throw KhinsiderException("That isn't a khinsider address.")
        val c = URL(url).openConnection() as HttpURLConnection
        try {
            c.connectTimeout = 15_000; c.readTimeout = 30_000; c.instanceFollowRedirects = true
            c.setRequestProperty("User-Agent", AGENT)
            c.setRequestProperty("Accept", "text/html,application/xhtml+xml")
            val code = c.responseCode
            val body = (if (code in 200..299) c.inputStream else c.errorStream)?.use { it.readBytes().toString(Charsets.UTF_8) }.orEmpty()
            if (looksLikeBrowserCheck(body) || (code == 403 && body.contains("cloudflare", true))) throw BrowserCheckException()
            if (code !in 200..299) throw KhinsiderException("khinsider answered $code.")
            return body
        } finally { c.disconnect() }
    }

    /** Cloudflare's "Just a moment..." page, which is what the site gives a client it takes for a robot. */
    fun looksLikeBrowserCheck(html: String): Boolean = html.contains("Just a moment...") && html.contains("challenge", true)

    /** A page's HTML: a plain request first, and, where the site's browser check turns that away, the page as a browser reads it. */
    suspend fun fetch(url: String): String = try {
        withContext(Dispatchers.IO) { get(url) }
    } catch (e: BrowserCheckException) {
        val context = appContext ?: throw KhinsiderException("khinsider asked for a browser check and the app can't pass it here.")
        BrowserFetch.html(context, url)
    }

    suspend fun albums(): List<Album> = fetch(PUBLISHER).let { html -> parseAlbums(html, PUBLISHER).also { if (it.isEmpty()) throw Unreadable(PUBLISHER, html, "no albums") } }

    suspend fun album(album: Album): AlbumPage = fetch(album.url).let { html -> parseAlbum(html, album.url).also { if (it.songs.isEmpty()) throw Unreadable(album.url, html, "no songs") } }

    /** A page that came but had nothing the app could read in it: what the page said is kept for a report. */
    class Unreadable(val url: String, val html: String, what: String) : KhinsiderException("khinsider's page had $what the app could read (it said: \"${title(html)}\").")

    private fun title(html: String): String =
        Regex("""<title[^>]*>(.*?)</title>""", setOf(RegexOption.IGNORE_CASE, RegexOption.DOT_MATCHES_ALL)).find(html)?.groupValues?.get(1)?.let { text(it) }?.take(80) ?: "no title"

    /** The address of the audio file of the song page [pageUrl]. */
    suspend fun audioUrl(pageUrl: String): String {
        val html = fetch(pageUrl)
        val url = MusicStore.audioUrlFromHtml(html, pageUrl) ?: throw KhinsiderException("That song's page has no audio file.")
        if (!isSiteUrl(url)) throw KhinsiderException("That song's file isn't on khinsider's servers.")
        return url
    }
}
