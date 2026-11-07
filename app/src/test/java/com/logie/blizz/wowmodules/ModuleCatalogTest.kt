package com.logie.blizz.wowmodules

import java.net.URLDecoder
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class ModuleCatalogTest {
    // Trimmed from GitHub's answer to search/repositories?q=topic:azerothcore-module.
    private val answer = """
        {"total_count": 590, "incomplete_results": false, "items": [
          {"id": 1, "full_name": "azerothcore/mod-transmog", "owner": {"login": "azerothcore", "avatar_url": "https://avatars.githubusercontent.com/u/1?v=4"},
           "html_url": "https://github.com/azerothcore/mod-transmog", "description": "Transmogrification for AzerothCore",
           "pushed_at": "2026-09-30T12:01:02Z", "updated_at": "2026-10-01T00:00:00Z", "stargazers_count": 140,
           "language": "C++", "archived": false, "default_branch": "master"},
          {"id": 2, "full_name": "someone/mod-old", "owner": {"login": "someone", "avatar_url": null},
           "html_url": "https://github.com/someone/mod-old", "description": null,
           "pushed_at": null, "updated_at": "2019-01-02T03:04:05Z", "stargazers_count": 3,
           "language": null, "archived": true, "default_branch": "main"},
          {"id": 3, "full_name": "bad name/with spaces", "owner": {}}
        ]}
    """.trimIndent()

    @Test
    fun readsTheSearch() {
        val page = ModuleCatalog.parseSearch(answer)
        assertEquals(590, page.total)
        assertEquals(2, page.items.size)
        val transmog = page.items[0]
        assertEquals("azerothcore/mod-transmog", transmog.fullName)
        assertEquals("azerothcore", transmog.owner)
        assertEquals("mod-transmog", transmog.name)
        assertEquals("Transmogrification for AzerothCore", transmog.description)
        assertEquals(140, transmog.stars)
        assertEquals("2026-09-30", ModuleCatalog.day(transmog.updated))
        assertEquals("master", transmog.defaultBranch)
        assertEquals("https://avatars.githubusercontent.com/u/1?v=4", transmog.avatar)
        assertEquals("C++", transmog.language)
        assertFalse(transmog.archived)

        val old = page.items[1]
        assertNull(old.description)
        assertNull(old.avatar)
        assertNull(old.language)
        assertEquals("2019-01-02", ModuleCatalog.day(old.updated)) // updated_at when there's no push
        assertEquals("main", old.defaultBranch)
        assertTrue(old.archived)
    }

    @Test
    fun searchesTheTopic() {
        val url = ModuleCatalog.searchUrl("  auction   house ", ModuleCatalog.Order.UPDATED, 3)
        val query = URLDecoder.decode(url.substringAfter("q=").substringBefore('&'), "UTF-8")
        assertEquals("auction house topic:azerothcore-module", query)
        assertTrue(url.startsWith("https://api.github.com/search/repositories?q="))
        assertTrue("&sort=updated&order=desc&per_page=30&page=3" in url)
        val all = ModuleCatalog.searchUrl("", ModuleCatalog.Order.STARS, 1)
        assertEquals("topic:azerothcore-module", URLDecoder.decode(all.substringAfter("q=").substringBefore('&'), "UTF-8"))
        assertTrue("&sort=stars&" in all)
    }

    @Test
    fun namesAndCommitsAreChecked() {
        assertTrue(ModuleCatalog.isFullName("azerothcore/mod-ah-bot"))
        assertTrue(ModuleCatalog.isFullName("Some_One/mod.thing-2"))
        assertFalse(ModuleCatalog.isFullName("azerothcore"))
        assertFalse(ModuleCatalog.isFullName("a/b/c"))
        assertFalse(ModuleCatalog.isFullName("../mod"))
        assertFalse(ModuleCatalog.isFullName("owner/.hidden"))
        assertFalse(ModuleCatalog.isFullName("owner/mod name"))
        assertTrue(ModuleCatalog.isCommit("0123456789abcdef0123456789abcdef01234567"))
        assertFalse(ModuleCatalog.isCommit("0123456789ABCDEF0123456789abcdef01234567"))
        assertFalse(ModuleCatalog.isCommit("master"))
        assertNull(ModuleCatalog.day("2026"))
    }
}
