package com.logie.blizz.porter.armory

import com.logie.blizz.porter.net.Net
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.File

/**
 * The Armory's pages as the porter reads them: on pages kept here (the site's own markup and JSON of November 2026, the
 * character's and realm's names changed), and, with `BLIZZ_PORTER_LIVE=1`, on the site itself.
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class ArmoryTest {
    private fun fixture(name: String) = javaClass.classLoader!!.getResourceAsStream("porter/$name")!!.readBytes()

    /** A web that answers from the fixtures, and notes what was asked. */
    private class Pages(private val pages: Map<String, ByteArray>, private val forward: Map<String, String> = emptyMap()) : Net {
        val asked = ArrayList<String>()
        override fun get(url: String, headers: Map<String, String>): Net.Reply {
            asked += url
            val at = forward[url] ?: url
            val bytes = pages[at] ?: return Net.Reply(404, ByteArray(0), at)
            return Net.Reply(200, bytes, at)
        }
        override fun post(url: String, body: ByteArray, headers: Map<String, String>) = Net.Reply(405, ByteArray(0), url)
        override fun save(url: String, to: File, headers: Map<String, String>, progress: (Long) -> Unit) = error("not used")
    }

    @Test fun theSearchListsNameLevelRaceClassFactionAndRealm() {
        val found = Armory.parseSearch(Region.EU, String(fixture("armory-search.html")))
        assertEquals(3, found.size)
        assertEquals(Found(Region.EU, "Testhero", "Test Realm", "test-realm", "testhero", 80, "Orc", "Warlock", "Horde",
            "https://render.worldofwarcraft.com/eu/character/test-realm/1/2-avatar.jpg"), found[0])
        // A name with an accent keeps it; its address is the site's own spelling of it.
        assertEquals("Tésthero", found[1].name)
        assertEquals("tésthero", found[1].slug)
        assertEquals("argent-dawn", found[1].realmSlug)
        assertNull(found[1].avatar)
        assertEquals(listOf("Void Elf", "Demon Hunter", "Alliance", "Kazzak"), found[2].let { listOf(it.race, it.className, it.faction, it.realm) })
        assertEquals(emptyList<Found>(), Armory.parseSearch(Region.US, "<html><body>No results</body></html>"))
    }

    @Test fun theCharacterIsWhoTheyAreAndWhatTheyWear() {
        val c = Armory.parseCharacter(Region.US, String(fixture("armory-model.json")))
        assertEquals(listOf("Testhero", "Test Realm", "test-realm", "testhero"), listOf(c.name, c.realm, c.realmSlug, c.slug))
        assertEquals(listOf(90, 2, 9, 0), listOf(c.level, c.raceId, c.classId, c.gender))
        assertEquals(listOf("Orc", "Warlock", "HORDE", "Destruction", "DAMAGE", "Fixture Guild"), listOf(c.race, c.className, c.faction, c.spec, c.role, c.guild))
        assertEquals("https://render.worldofwarcraft.com/us/character/test-realm/1/1-main-raw.png", c.render)
        assertEquals(15, c.items.size)
        // In the sheet's order, head first.
        assertEquals("head", c.items.first().slot)
        val head = c.items.first()
        assertEquals(listOf(271546, 295, 4, 1), listOf(head.id, head.itemLevel, head.itemClass, head.itemSubclass))
        assertEquals(listOf("Skull of the Damned Necrolyte", "EPIC", "HEAD", "Diabolic Helm"), listOf(head.name, head.quality, head.inventoryType, head.transmogName))
        assertEquals(147183, head.transmogItemId)
        assertTrue(head.icon!!.endsWith(".jpg"))
        val weapon = c.items.single { it.slot == "weapon" }
        assertEquals(listOf("TWOHWEAPON", "2", "10", "307902", "253285"),
            listOf(weapon.inventoryType, "${weapon.itemClass}", "${weapon.itemSubclass}", "${weapon.modifiedAppearanceId}", "${weapon.transmogItemId}"))
        // A ring has no look of its own (the site says 0) and none borrowed.
        val ring = c.items.single { it.slot == "leftFinger" }
        assertNull(ring.modifiedAppearanceId)
        assertNull(ring.transmogItemId)
        // Professions with each expansion's tier.
        val smith = c.professions.single { it.id == 164 }
        assertTrue(smith.primary)
        assertEquals(ProfessionTier("Classic Blacksmithing", 1, 300), smith.tiers.first())
        assertFalse(c.professions.single { it.name == "Cooking" }.primary)
    }

    @Test fun mountsAreTheCollectedOnesAndReputationsEveryFactionWithAStanding() {
        val mounts = Armory.parseMounts(String(fixture("armory-mounts.json")))
        assertEquals(setOf(6, 17, 219, 221, 363, 899, 1227), mounts.map { it.id }.toSet())
        assertEquals("Invincible", mounts.single { it.id == 363 }.name)
        val reputations = Armory.parseReputations(String(fixture("armory-reputation.json")))
        assertTrue(reputations.isNotEmpty())
        assertTrue(reputations.all { it.standing.isNotEmpty() && it.name.isNotEmpty() })
        // A group's own factions and the ones filed under another faction are both there, once each.
        assertEquals(reputations.size, reputations.map { it.name }.toSet().size)
        assertTrue(reputations.any { it.group == "Classic" })
        assertTrue(reputations.any { it.group == "Wrath of the Lich King" })
    }

    @Test fun theAddressesAreTheSitesOwn() {
        val base = "https://worldofwarcraft.blizzard.com/en-us/newsaga"
        val pages = Pages(
            mapOf(
                "$base/us/armory?q=aa" to ByteArray(0),
                "$base/eu/armory/character?q=test%20hero" to fixture("armory-search.html"),
                "$base/eu/armory/character/test-realm/t%C3%A9sthero/model.json" to fixture("armory-model.json"),
                "$base/eu/armory/character/test-realm/testhero/collections/mounts.json" to fixture("armory-mounts.json"),
            ),
            // The site's old search address forwards to wherever the Armory now lives.
            forward = mapOf("https://worldofwarcraft.blizzard.com/en-us/search?q=aa" to "$base/us/armory?q=aa"),
        )
        val armory = Armory(pages)
        val (found, more) = armory.search(Region.EU, " test hero ")
        assertEquals(3, found.size)
        assertTrue(more)
        assertEquals("Testhero", armory.character(Region.EU, "test-realm", "tésthero").name)
        assertEquals(7, armory.mounts(Region.EU, "test-realm", "testhero").size)
        // What the site doesn't have is nothing, not a failure.
        assertEquals(emptyList<ArmoryReputation>(), armory.reputations(Region.EU, "test-realm", "testhero"))
        // Asked where the Armory lives once.
        assertEquals(1, pages.asked.count { it.endsWith("/search?q=aa") })
        // One letter is no search.
        assertEquals(emptyList<Found>(), armory.search(Region.EU, "t").first)
        assertEquals("worldsoul", Armory.sagaOf("https://worldofwarcraft.blizzard.com/en-us/worldsoul/us/armory?q=aa"))
        assertNull(Armory.sagaOf("https://worldofwarcraft.blizzard.com/en-us/"))
    }

    /** The site itself: a search in each region finds characters, and the first one's summary, mounts and reputations read. */
    @Test fun theLiveSite() {
        assumeTrue(System.getenv("BLIZZ_PORTER_LIVE") == "1")
        val armory = Armory(com.logie.blizz.porter.net.HttpNet(com.logie.blizz.porter.net.HttpNet.BROWSER))
        for (region in listOf(Region.US, Region.EU)) {
            val (found, _) = armory.search(region, "thrall")
            assertTrue("${region.code}: ${found.size} found", found.size > 10)
            val pick = found.first { it.level >= 70 }
            val c = armory.character(region, pick.realmSlug, pick.slug)
            assertEquals(pick.name, c.name)
            assertTrue("${c.items.size} items", c.items.size >= 8)
            assertTrue(c.raceId > 0 && c.classId > 0)
            println("ArmoryTest live ${region.code}: ${c.level} ${c.race} ${c.className}, ${c.items.size} items, " +
                "${armory.mounts(region, pick.realmSlug, pick.slug).size} mounts, ${armory.reputations(region, pick.realmSlug, pick.slug).size} reputations")
        }
    }
}
