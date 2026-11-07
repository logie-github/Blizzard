package com.logie.blizz.wowaddons

import com.logie.blizz.wowaddons.Warperia.Flavor
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull
import kotlin.test.assertTrue

/** warperia.com's 1.12 section, for Turtle WoW's add-ons: its real pages (October 2026), whole. */
class WarperiaVanillaTest {
    private fun sample(name: String) =
        javaClass.getResource("/warperia/$name")!!.readText()

    @Test
    fun itsOwnAddresses() {
        assertEquals("https://warperia.com/vanilla-addons/", Warperia.listUrl(Warperia.Query(), 1, Flavor.VANILLA))
        assertEquals("https://warperia.com/vanilla-addons/?search=pfquest&paged=2", Warperia.listUrl(Warperia.Query("pfquest"), 2, Flavor.VANILLA))
        assertEquals("https://warperia.com/addon-vanilla/bagnon/", Warperia.pageUrl("bagnon", Flavor.VANILLA))
        assertEquals("https://warperia.com/addon-vanilla/bagnon/download/", Warperia.downloadPageUrl("bagnon", Flavor.VANILLA))
        assertEquals("bagnon", Warperia.slugOf("https://warperia.com/addon-vanilla/bagnon/", Flavor.VANILLA))
        // Each section's links only: a 3.3.5a add-on isn't a 1.12 one, nor the other way round.
        assertNull(Warperia.slugOf("https://warperia.com/addon-wotlk/bagnon/", Flavor.VANILLA))
        assertNull(Warperia.slugOf("https://warperia.com/addon-vanilla/bagnon/"))
        // The 3.3.5a game's addresses as they were.
        assertEquals("https://warperia.com/addon-wotlk/postal/download/", Warperia.downloadPageUrl("postal"))
    }

    @Test
    fun readsTheList() {
        val page = Warperia.parseList(sample("vanilla-list.html"), Flavor.VANILLA)
        assertTrue(page.items.size >= 10, "${page.items.size} add-ons")
        assertTrue(page.items.any { it.slug == "bagnon" }, page.items.map { it.slug }.toString())
        assertTrue(page.items.all { it.title.isNotBlank() })
        assertTrue(page.pages > 1)
        assertTrue(page.categories.isNotEmpty())
        // The 3.3.5a reading of the same page finds none of them.
        assertTrue(Warperia.parseList(sample("vanilla-list.html")).items.isEmpty())
    }

    @Test
    fun readsAnAddonsPage() {
        val details = Warperia.parseDetails(sample("vanilla-details.html"), "bagnon", Flavor.VANILLA)
        assertTrue(details.title.contains("Bagnon", ignoreCase = true), details.title)
    }

    @Test
    fun readsItsDownloadPage() {
        val ticket = Warperia.parseTicket(sample("vanilla-download.html"))
        assertTrue(ticket.seconds in 0..60, "${ticket.seconds} s")
        assertTrue(Warperia.downloadForm(ticket).isNotEmpty())
    }
}
