package com.logie.blizz.wowaddons

import com.logie.blizz.wowaddons.Warperia.Block
import java.io.IOException
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertNull
import kotlin.test.assertTrue

/** Against parts of warperia.com's real pages (October 2026), cut down. */
class WarperiaTest {
    private fun sample(name: String) =
        javaClass.getResource("/warperia/$name")!!.readText()

    @Test
    fun listUrls() {
        assertEquals("https://warperia.com/wotlk-addons/", Warperia.listUrl(Warperia.Query(), 1))
        assertEquals(
            "https://warperia.com/wotlk-addons/?search=bag+bar&category=unit-frames&sort=updated&paged=3",
            Warperia.listUrl(Warperia.Query(" bag bar ", "unit-frames", Warperia.Order.UPDATED), 3),
        )
        assertEquals("https://warperia.com/wotlk-addons/?sort=recent&paged=2", Warperia.listUrl(Warperia.Query(order = Warperia.Order.NEW), 2))
    }

    @Test
    fun slugs() {
        assertEquals("questie", Warperia.slugOf("https://warperia.com/addon-wotlk/questie/"))
        assertEquals("dbm-warmane", Warperia.slugOf("https://warperia.com/addon-wotlk/dbm-warmane"))
        assertNull(Warperia.slugOf("https://warperia.com/addon-tbc/questie/"))
        assertNull(Warperia.slugOf("https://warperia.com/addon-wotlk/questie/download/"))
        assertEquals("https://warperia.com/addon-wotlk/postal/download/", Warperia.downloadPageUrl("postal"))
    }

    @Test
    fun readsTheList() {
        val page = Warperia.parseList(sample("list.html"))
        assertEquals(1, page.page)
        assertEquals(42, page.pages)
        assertEquals(listOf("questie", "details-damagemeter"), page.items.map { it.slug })
        val questie = page.items[0]
        assertEquals("3303", questie.id)
        assertEquals("Questie", questie.title)
        assertEquals("Aldori15", questie.author)
        assertEquals("A quest helper for World of Warcraft Wrath of the Lich King", questie.summary)
        assertEquals("https://warperia.com/wp-content/uploads/2024/12/addon-logo-3303-6a7604b3208e1.png", questie.logo)
        assertEquals("135K", questie.downloads)
        assertEquals("2026-10-12", questie.updated)
        assertEquals(listOf("Map & Minimap", "Quests & Leveling"), questie.categories)
        assertEquals("Details! DamageMeter", page.items[1].title)
        assertEquals(
            listOf("achievements" to "Achievements", "action-bars" to "Action Bars", "class" to "Class", "unit-frames" to "Unit Frames"),
            page.categories.map { it.slug to it.name },
        )
    }

    @Test
    fun readsTheListWithTheSitesOtherClassNames() {
        // The site doesn't always name the card's parts the same way.
        val page = Warperia.parseList(sample("list-other-names.html"))
        assertEquals(42, page.pages)
        assertEquals(listOf("Questie", "Details! DamageMeter"), page.items.map { it.title })
        assertEquals(listOf("Aldori15", "Bunny67"), page.items.map { it.author })
        assertEquals("135K", page.items[0].downloads)
    }

    @Test
    fun daysCompareHoweverTheSiteWritesThem() {
        assertEquals("2026-08-07", Warperia.day("Aug 7, 2026"))
        assertEquals("2026-08-07", Warperia.day("Aug 07, 2026"))
        assertEquals("yesterday", Warperia.day("yesterday"))
        assertEquals("Aug 7, 2026", Warperia.showDay("2026-08-07", java.util.Locale.US))
        assertEquals("soon", Warperia.showDay("soon"))
    }

    @Test
    fun readsAListWithNothing() {
        val page = Warperia.parseList(sample("list-empty.html"))
        assertTrue(page.items.isEmpty())
        assertEquals(1, page.pages)
    }

    @Test
    fun readsAnAddonsPage() {
        val details = Warperia.parseDetails(sample("details.html"), "questie")
        assertEquals("3303", details.id)
        assertEquals("Questie", details.title)
        assertEquals("A quest helper for World of Warcraft Wrath of the Lich King", details.summary)
        assertEquals("https://warperia.com/wp-content/uploads/2024/12/addon-logo-3303-6a7604b3208e1.png", details.logo)
        assertEquals("9.9.6-335", details.version)
        assertEquals("2024-12-10", details.uploaded)
        assertEquals("2026-10-12", details.updated)
        assertEquals("135K", details.downloads)
        assertEquals(listOf("Map & Minimap", "Quests & Leveling"), details.categories)
        assertEquals(listOf("Aldori15"), details.developers)
        assertEquals(3, details.screenshots.size)
        assertTrue(details.screenshots.all { it.startsWith("https://warperia.com/wp-content/uploads/") })
        assertEquals(listOf("9.9.6-335" to "2026-10-12", "9.9.6-335" to "2026-10-11"), details.changelog.map { it.version to it.date })
        assertNull(details.changelog[0].notes)
    }

    @Test
    fun descriptionAsBlocks() {
        val blocks = Warperia.parseDetails(sample("details.html"), "questie").description
        assertEquals(Block.Paragraph("A quest helper for World of Warcraft Wrath of the Lich King"), blocks[0])
        // The site's empty paragraph (&nbsp;) is left out; a line in bold is a heading.
        assertEquals(Block.Heading("Show quests on map"), blocks[1])
        assertEquals(Block.Item("Show notes for quest start points, turn in points, and objectives.", null), blocks[2])
        assertEquals(Block.Rule, blocks[3])
        assertEquals(Block.Heading("Quest Tracker"), blocks[4])
        assertEquals(
            listOf(
                "Automatically tracks quests on accepting (instead of progressing)",
                "Can show all 20 quests from the log (instead of default 5)",
                "Left click quest to open quest log (configurable)",
            ),
            blocks.subList(5, 8).map { (it as Block.Item).text },
        )
        assertTrue(blocks.last() !is Block.Rule)
        assertEquals("• Can show all 20 quests from the log (instead of default 5)", Warperia.plain(blocks[6]))
    }

    @Test
    fun readsTheWaitingPage() {
        val ticket = Warperia.parseTicket(sample("download.html"))
        assertEquals(Warperia.Ticket("1190", 5, "87d8448745"), ticket)
        assertEquals(
            listOf("action" to "increment_addon_download", "addon_id" to "1190", "nonce" to "87d8448745"),
            Warperia.downloadForm(ticket),
        )
    }

    @Test
    fun readsTheDownloadAnswer() {
        val answer = """{"success":true,"data":{"message":"Download logged successfully.","download_url":"https:\/\/warperia.com\/?wdl_token=abc-def"}}"""
        assertEquals("https://warperia.com/?wdl_token=abc-def", Warperia.parseDownloadAnswer(answer))
        val refused = assertFailsWith<IOException> {
            Warperia.parseDownloadAnswer("""{"success":false,"data":{"message":"Security check failed."}}""")
        }
        assertEquals("Security check failed.", refused.message)
        assertFailsWith<IOException> { Warperia.parseDownloadAnswer("0") }
    }
}
