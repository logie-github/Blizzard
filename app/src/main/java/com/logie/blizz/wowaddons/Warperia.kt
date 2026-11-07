// Ported from the World of Warcraft app (com.logie.warcraft), apart from its package.

package com.logie.blizz.wowaddons

import org.jsoup.Jsoup
import org.jsoup.nodes.Document
import org.jsoup.nodes.Element
import org.jsoup.nodes.TextNode
import java.io.IOException
import java.net.URLEncoder
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.time.format.FormatStyle
import java.util.Locale

/**
 * warperia.com's add-ons (3.3.5a's, or 1.12's for OctoWoW, 7.3.5's for Legion: [Flavor]), read from its web pages the
 * way a browser shows them (its API takes a key): the list (a search, a category, an order, 20 to a page), an add-on's own page, and
 * the two steps of its free download, the waiting page and the link the site gives after the wait.
 */
object Warperia {
    const val SITE = "https://warperia.com"
    const val LIST = "$SITE/wotlk-addons/"
    const val AJAX = "$SITE/wp-admin/admin-ajax.php"

    /** The site's sections, each with its list and its add-ons' pages: 3.3.5a's, 1.12's (OctoWoW's client) and 7.3.5's (Legion's). */
    enum class Flavor(val list: String, val type: String) {
        WOTLK("$SITE/wotlk-addons/", "addon-wotlk"),
        VANILLA("$SITE/vanilla-addons/", "addon-vanilla"),
        LEGION("$SITE/legion-addons/", "addon-legion"),
    }

    /** The list's orders, as the site names them. */
    enum class Order(val param: String?) { POPULAR(null), NEW("recent"), UPDATED("updated") }

    data class Query(val search: String = "", val category: String? = null, val order: Order = Order.POPULAR)

    fun listUrl(query: Query, page: Int, flavor: Flavor = Flavor.WOTLK): String {
        val params = buildList {
            query.search.trim().takeIf { it.isNotEmpty() }?.let { add("search" to it) }
            query.category?.let { add("category" to it) }
            query.order.param?.let { add("sort" to it) }
            if (page > 1) add("paged" to page.toString())
        }
        if (params.isEmpty()) return flavor.list
        return flavor.list + "?" + params.joinToString("&") { (k, v) -> "$k=" + URLEncoder.encode(v, "UTF-8") }
    }

    fun pageUrl(slug: String, flavor: Flavor = Flavor.WOTLK) = "$SITE/${flavor.type}/$slug/"

    fun downloadPageUrl(slug: String, flavor: Flavor = Flavor.WOTLK) = "$SITE/${flavor.type}/$slug/download/"

    /** The add-on a link of the site is for: `https://warperia.com/addon-wotlk/<slug>/`. */
    fun slugOf(url: String, flavor: Flavor = Flavor.WOTLK): String? =
        Regex("""^https?://(?:www\.)?warperia\.com/${flavor.type}/([A-Za-z0-9_-]+)/?(?:[?#].*)?$""").find(url.trim())?.groupValues?.get(1)

    // The list -----------------------------------------------------------------------------------

    /** An add-on as the list shows it. */
    data class Listing(
        val slug: String,
        val id: String?,
        val title: String,
        val author: String?,
        val summary: String?,
        val logo: String?,
        /** As the site writes it: "135K". */
        val downloads: String?,
        /** The day it was last updated, as [day] writes it: "2026-10-12". */
        val updated: String?,
        val categories: List<String>,
    )

    data class Category(val slug: String, val name: String)

    data class ListPage(val items: List<Listing>, val page: Int, val pages: Int, val categories: List<Category>)

    fun parseList(html: String, flavor: Flavor = Flavor.WOTLK): ListPage {
        val doc = document(html, flavor.list)
        val grid = doc.getElementById("addons-grid") ?: doc.body()
        val items = grid.select("a[data-addon-id][href]").mapNotNull { card ->
            val slug = slugOf(card.absUrl("href"), flavor) ?: return@mapNotNull null
            val title = firstText(card, ".addon-name-header > span", ".addon-title > span", ".details span.text-white", ".details span")
                ?: card.selectFirst("img[alt]")?.attr("alt")?.removeSuffix("addon image logo")?.trim()?.ifEmpty { null }
            Listing(
                slug = slug,
                id = card.attr("data-addon-id").ifBlank { null },
                title = title ?: slug,
                author = (firstText(card, ".addon-author") ?: card.getElementsMatchingOwnText("^by\\s").firstOrNull()?.let { text(it) })
                    ?.removePrefix("by")?.trim()?.ifEmpty { null },
                summary = firstText(card, ".addon-short"),
                logo = card.selectFirst("img")?.let(::imageUrl),
                downloads = firstText(card, "[data-tooltip=Downloads] span", "[data-tooltip=Downloads]", "[title=Downloads]"),
                updated = firstText(card, "[data-tooltip=Last updated] span", "[data-tooltip=Last updated]", "[title=Last updated]")?.let(::day),
                categories = card.select(".category-tag").ifEmpty { card.select(".addon-categories span:not(.category-separator)") }
                    .mapNotNull { text(it) }.filter { it != "•" }.distinct(),
            )
        }.distinctBy { it.slug }
        val pagination = doc.selectFirst("[data-total-pages]")
        val page = pagination?.attr("data-current-page")?.toIntOrNull() ?: 1
        val pages = pagination?.attr("data-total-pages")?.toIntOrNull() ?: page
        val categories = doc.select("input[type=checkbox][id^=category-]").mapNotNull { box ->
            val slug = box.attr("value").ifBlank { return@mapNotNull null }
            val label = doc.selectFirst("label[for=${box.id()}]")
            val name = label?.selectFirst(".checkbox-text")?.let { text(it) } ?: label?.let { text(it) }
            Category(slug, name ?: slug)
        }.distinctBy { it.slug }
        return ListPage(items, page, maxOf(pages, page), categories)
    }

    // An add-on's page ---------------------------------------------------------------------------

    /** A piece of an add-on's description. */
    sealed interface Block {
        data class Heading(val text: String) : Block
        data class Paragraph(val text: String) : Block
        /** A list item: [number] for numbered lists, null for bullets. */
        data class Item(val text: String, val number: Int?) : Block
        data class Code(val text: String) : Block
        data object Rule : Block
    }

    data class Change(val version: String, val date: String?, val notes: String?)

    /** Everything an add-on's page says about it. */
    data class Details(
        val slug: String,
        val id: String?,
        val title: String,
        val summary: String?,
        val logo: String?,
        val version: String?,
        val uploaded: String?,
        val updated: String?,
        val downloads: String?,
        val categories: List<String>,
        val developers: List<String>,
        val description: List<Block>,
        val screenshots: List<String>,
        val changelog: List<Change>,
    )

    fun parseDetails(html: String, slug: String, flavor: Flavor = Flavor.WOTLK): Details {
        val doc = document(html, pageUrl(slug, flavor))
        // "Addon Version:", "Last Updated:"...: each label's value is the element after it.
        val facts = LinkedHashMap<String, String>()
        for (label in doc.getElementsMatchingOwnText("^[A-Za-z][A-Za-z ]{1,30}:$")) {
            val value = label.nextElementSibling()?.let { text(it) } ?: continue
            facts.putIfAbsent(label.ownText().trim().removeSuffix(":").lowercase(), value)
        }
        fun fact(name: String) = facts[name.lowercase()]
        /** The part of the page under a heading: "Categories", "Developers". */
        fun section(heading: String): Element? =
            doc.select("h4, h3, h5").firstOrNull { it.text().trim().equals(heading, ignoreCase = true) }?.parent()

        val h1 = doc.selectFirst("h1.addon-hero-title") ?: doc.selectFirst("h1")
        val description = doc.getElementById("descriptionTab")?.let { it.selectFirst(".addon-content") ?: it }
        val changelog = doc.getElementById("changelogTab")
        return Details(
            slug = slug,
            id = fact("Addon ID") ?: doc.selectFirst("a[data-download-trigger][data-addon-id]")?.attr("data-addon-id")?.ifBlank { null },
            title = h1?.let { text(it) } ?: slug,
            summary = doc.selectFirst(".addon-hero-summary")?.let { text(it) }
                ?: h1?.nextElementSibling()?.takeIf { it.normalName() == "p" }?.let { text(it) },
            logo = doc.selectFirst("img.page-featured-image")?.let(::imageUrl)
                ?: doc.selectFirst("a[data-fslightbox=addon-logo]")?.absUrl("href")?.ifEmpty { null }
                ?: doc.selectFirst("meta[property=og:image]")?.absUrl("content")?.ifEmpty { null },
            version = fact("Addon Version") ?: fact("Version"),
            uploaded = fact("Upload date")?.let(::day),
            updated = fact("Last Updated")?.let(::day),
            downloads = fact("Downloads"),
            categories = (section("Categories")?.select("a") ?: doc.select("a[href*=?category=]"))
                .mapNotNull { text(it) }.distinct(),
            developers = (section("Developers")?.select("[data-bs-title]")?.map { it.attr("data-bs-title").trim() }
                ?.ifEmpty { null } ?: doc.select(".creator .name").map { it.text().trim() })
                .filter { it.isNotEmpty() }.distinct(),
            description = description?.let(::blocks).orEmpty(),
            screenshots = doc.select("a[data-fslightbox=addon-lightbox], #imagesTab a[data-fslightbox]")
                .map { it.absUrl("href") }.filter { it.isNotEmpty() }.distinct(),
            changelog = changelog?.select("[id^=changelogHeading]")?.mapNotNull { heading ->
                val button = heading.selectFirst("button") ?: heading
                val version = button.selectFirst(".changelog-version")?.let { text(it) }
                    ?: button.selectFirst("span")?.let { text(it) } ?: return@mapNotNull null
                val number = heading.id().removePrefix("changelogHeading")
                val body = doc.getElementById("changelogCollapse$number")
                val notes: String? = body?.let { b: Element -> blocks(b).joinToString("\n") { plain(it) } }
                Change(
                    version = version,
                    date = button.selectFirst("small")?.let { text(it) }?.let(::day),
                    notes = notes?.takeUnless { it.isBlank() || it.trim().equals("No changelog available.", ignoreCase = true) },
                )
            }.orEmpty(),
        )
    }

    /** A block as one line of text. */
    fun plain(block: Block): String = when (block) {
        is Block.Heading -> block.text
        is Block.Paragraph -> block.text
        is Block.Item -> (block.number?.let { "$it. " } ?: "• ") + block.text
        is Block.Code -> block.text
        Block.Rule -> ""
    }

    /** The description's HTML as headings, paragraphs, list items and rules; pictures and empty lines left out. */
    private fun blocks(root: Element): List<Block> {
        val out = mutableListOf<Block>()
        fun walk(element: Element) {
            for (node in element.childNodes()) {
                if (node is TextNode) {
                    // Text straight inside a container, between its blocks.
                    node.text().replace('\u00A0', ' ').trim().takeIf { it.isNotEmpty() }?.let { out += Block.Paragraph(it) }
                    continue
                }
                val child = node as? Element ?: continue
                when (child.normalName()) {
                    "h1", "h2", "h3", "h4", "h5", "h6" -> text(child)?.let { out += Block.Heading(it) }
                    "p", "blockquote" -> {
                        val text = text(child) ?: continue
                        // A line all in bold is how the site's editors write a heading.
                        val bold = child.select("strong, b").joinToString(" ") { it.text() }.trim()
                        out += if (bold.isNotEmpty() && bold.length >= text.length) Block.Heading(text) else Block.Paragraph(text)
                    }
                    "ul", "ol" -> {
                        var number = 0
                        for (item in child.children().filter { it.normalName() == "li" }) {
                            val text = text(item) ?: continue
                            val ordered = child.normalName() == "ol" && item.attr("data-list") != "bullet"
                            if (ordered) number++
                            out += Block.Item(text, if (ordered) number else null)
                        }
                    }
                    "hr" -> if (out.isNotEmpty() && out.last() != Block.Rule) out += Block.Rule
                    "pre" -> child.wholeText().trimEnd().takeIf { it.isNotBlank() }?.let { out += Block.Code(it) }
                    "table" -> for (row in child.select("tr")) {
                        val cells = row.select("td, th").mapNotNull { text(it) }
                        if (cells.isNotEmpty()) out += Block.Paragraph(cells.joinToString(" · "))
                    }
                    "img", "iframe", "video", "script", "style", "br", "noscript" -> {}
                    else -> if (child.children().any { it.isBlock }) walk(child) else text(child)?.let { out += Block.Paragraph(it) }
                }
            }
        }
        walk(root)
        while (out.firstOrNull() == Block.Rule) out.removeAt(0)
        while (out.lastOrNull() == Block.Rule) out.removeAt(out.size - 1)
        return out
    }

    /**
     * The page, with any class the site swapped for a random name (keeping the real one in
     * `data-w-orig`) given back.
     */
    private fun document(html: String, base: String): Document {
        val doc = Jsoup.parse(html, base)
        for (element in doc.select("[data-w-orig]")) {
            for (name in element.attr("data-w-orig").split(' ').filter { it.isNotBlank() }) element.addClass(name)
        }
        return doc
    }

    /** The text of the first of [queries] that finds something with text in [element]. */
    private fun firstText(element: Element, vararg queries: String): String? {
        for (query in queries) element.selectFirst(query)?.let { text(it) }?.let { return it }
        return null
    }

    private val SITE_DAY = DateTimeFormatter.ofPattern("MMM d, yyyy", Locale.US)

    /**
     * A day as the site writes it ("Aug 7, 2026" in the list, "Aug 07, 2026" on a page) as
     * `2026-08-07`, so the two compare; text that isn't a day stays as it is.
     */
    fun day(text: String): String =
        runCatching { LocalDate.parse(text.trim(), SITE_DAY).toString() }.getOrDefault(text.trim())

    /** A day from [day], for the screen ("Aug 7, 2026" in English). */
    fun showDay(day: String, locale: Locale = Locale.getDefault()): String =
        runCatching { LocalDate.parse(day).format(DateTimeFormatter.ofLocalizedDate(FormatStyle.MEDIUM).withLocale(locale)) }
            .getOrDefault(day)

    /** An element's text, spaces tidied (non-breaking ones too), or null when there's none. */
    private fun text(element: Element): String? =
        element.text().replace(' ', ' ').replace(Regex("\\s+"), " ").trim().ifEmpty { null }

    private fun imageUrl(img: Element): String? = img.absUrl("src").ifEmpty { null }?.takeUnless { it.endsWith("/default-image.jpg") }

    // The download -------------------------------------------------------------------------------

    /** What the waiting page gives: which add-on, how long the site asks to wait, and the form's key. */
    data class Ticket(val addonId: String, val seconds: Int, val nonce: String)

    fun parseTicket(html: String): Ticket {
        val doc = document(html, SITE)
        val main = doc.selectFirst("[data-countdown-seconds]") ?: doc.selectFirst(".page-addon-download")
        val waiting = doc.getElementById("addonDownloadWaiting")
        val id = main?.attr("data-addon-id")?.ifBlank { null }
            ?: waiting?.attr("data-addon-id")?.ifBlank { null }
            ?: throw IOException("The download page has changed: no add-on")
        val seconds = main?.attr("data-countdown-seconds")?.toIntOrNull() ?: DEFAULT_WAIT
        val nonce = Regex(""""download_nonce"\s*:\s*"([^"]+)"""").find(html)?.groupValues?.get(1)
            ?: throw IOException("The download page has changed: no key")
        return Ticket(id, seconds.coerceIn(0, MAX_WAIT), nonce)
    }

    /** The form the waiting page sends when its wait is over. */
    fun downloadForm(ticket: Ticket) = listOf(
        "action" to "increment_addon_download",
        "addon_id" to ticket.addonId,
        "nonce" to ticket.nonce,
    )

    /** The file's link from the site's answer to [downloadForm]; its message when there's none. */
    fun parseDownloadAnswer(json: String): String {
        Regex(""""download_url"\s*:\s*"((?:[^"\\]|\\.)*)"""").find(json)?.let { return unescape(it.groupValues[1]) }
        val message = Regex(""""message"\s*:\s*"((?:[^"\\]|\\.)*)"""").find(json)?.let { unescape(it.groupValues[1]) }
        throw IOException(message ?: "The site didn't give a download")
    }

    private fun unescape(text: String): String {
        val out = StringBuilder()
        var i = 0
        while (i < text.length) {
            val c = text[i]
            if (c == '\\' && i + 1 < text.length) {
                when (val next = text[i + 1]) {
                    'u' -> if (i + 5 < text.length) {
                        out.append(text.substring(i + 2, i + 6).toInt(16).toChar())
                        i += 6
                        continue
                    }
                    'n' -> out.append('\n')
                    't' -> out.append('\t')
                    'r' -> out.append('\r')
                    else -> out.append(next)
                }
                i += 2
            } else {
                out.append(c)
                i++
            }
        }
        return out.toString()
    }

    const val DEFAULT_WAIT = 5
    private const val MAX_WAIT = 30
}

