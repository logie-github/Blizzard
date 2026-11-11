package com.logie.blizz.porter.armory

import com.logie.blizz.porter.Porter
import com.logie.blizz.porter.look.Worn
import com.logie.blizz.porter.net.Net
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.io.File

/**
 * Blizzard's API as the porter asks it: the token, the addresses, what is read of its answers (in the shapes its API gives,
 * as a published client's types have them), and how what each slot shows becomes what the look wears. With
 * `BLIZZ_BNET_ID`/`BLIZZ_BNET_SECRET` (a key of one's own), the API itself.
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class BattleNetTest {
    private class Api(private val answers: Map<String, Pair<Int, String>>) : Net {
        val asked = ArrayList<Pair<String, Map<String, String>>>()
        var tokens = 0
        override fun get(url: String, headers: Map<String, String>): Net.Reply {
            asked += url to headers
            val path = url.substringAfter(".api.blizzard.com").substringBefore('?')
            val (code, body) = answers[path] ?: (404 to "")
            return Net.Reply(code, body.toByteArray(), url)
        }
        override fun post(url: String, body: ByteArray, headers: Map<String, String>): Net.Reply {
            asked += url to headers
            tokens++
            return Net.Reply(200, """{"access_token":"T$tokens","token_type":"bearer","expires_in":86399}""".toByteArray(), url)
        }
        override fun save(url: String, to: File, headers: Map<String, String>, progress: (Long) -> Unit) = error("not used")
    }

    private val appearanceJson = """{
      "_links": {"self": {"href": "x"}},
      "character": {"name": "Testhero", "id": 1, "realm": {"name": "Test Realm", "id": 1, "slug": "test-realm"}},
      "playable_race": {"name": "Orc", "id": 2}, "playable_class": {"name": "Warlock", "id": 9},
      "gender": {"type": "MALE", "name": "Male"}, "faction": {"type": "HORDE", "name": "Horde"},
      "customizations": [
        {"option": {"name": "Face", "id": 20}, "choice": {"id": 385, "display_order": 1}},
        {"option": {"name": "Hair Style", "id": 21}, "choice": {"id": 403, "display_order": 3}},
        {"option": {"name": "Broken", "id": 0}, "choice": {"id": 1}}
      ],
      "items": [
        {"id": 147183, "slot": {"type": "HEAD", "name": "Head"}, "enchant": 0, "item_appearance_modifier_id": 0, "internal_slot_id": 0, "subclass": 1},
        {"id": 253285, "slot": {"type": "MAIN_HAND", "name": "Main Hand"}, "enchant": 0, "item_appearance_modifier_id": 3, "internal_slot_id": 15, "subclass": 10}
      ]
    }"""

    @Test fun aTokenThenTheProfileWithIt() {
        val api = Api(mapOf("/profile/wow/character/test-realm/t%C3%A9sthero/appearance" to (200 to appearanceJson)))
        val bnet = BattleNet(api, "id", "secret")
        val a = bnet.appearance(Region.EU, "test-realm", "Tésthero")!!
        // The token: Battle.net's, with the client's id and secret.
        assertEquals("https://oauth.battle.net/token", api.asked[0].first)
        assertEquals("Basic aWQ6c2VjcmV0", api.asked[0].second["Authorization"])
        // The profile: the region's API, the name in small letters, the profile namespace.
        assertEquals("https://eu.api.blizzard.com/profile/wow/character/test-realm/t%C3%A9sthero/appearance?namespace=profile-eu&locale=en_US", api.asked[1].first)
        assertEquals("Bearer T1", api.asked[1].second["Authorization"])
        assertEquals(mapOf(20 to 385, 21 to 403), a.choices)
        assertEquals(listOf(Appearance.Shown("HEAD", 147183, 0), Appearance.Shown("MAIN_HAND", 253285, 3)), a.shown)
        // A private or unknown character has none; the token is had once.
        assertNull(bnet.appearance(Region.EU, "test-realm", "nobody"))
        assertEquals(1, api.tokens)
    }

    @Test fun questsAchievementsAndTitles() {
        val quests = """{"character": {"name": "Testhero"}, "quests": [{"key": {"href": "x"}, "name": "Lazy Peons", "id": 37446}, {"name": "The Admiral's Orders", "id": 25190}]}"""
        assertEquals(listOf(CompletedQuest(37446, "Lazy Peons"), CompletedQuest(25190, "The Admiral's Orders")), BattleNet.parseQuests(quests))
        val achievements = """{"total_quantity": 3, "total_points": 30, "achievements": [
            {"id": 6, "achievement": {"key": {"href": "x"}, "name": "Level 10", "id": 6}, "criteria": {"id": 1, "is_completed": true}, "completed_timestamp": 1580000000000},
            {"id": 7, "achievement": {"name": "Level 20", "id": 7}, "criteria": {"id": 2, "is_completed": false}},
            {"achievement": {"name": "Level 30", "id": 8}, "completed_timestamp": 1590000000000}
        ]}"""
        assertEquals(listOf(EarnedAchievement(6, "Level 10", 1580000000000), EarnedAchievement(8, "Level 30", 1590000000000)), BattleNet.parseAchievements(achievements))
        val titles = """{"active_title": {"name": "Champion of the Frozen Wastes", "id": 132, "display_string": "{name}, Champion of the Frozen Wastes"}, "titles": [{"name": "Private", "id": 1}, {"name": "Champion of the Frozen Wastes", "id": 132}]}"""
        assertEquals(Titles(listOf(1, 132), 132), BattleNet.parseTitles(titles))
        assertEquals(Titles(emptyList(), null), BattleNet.parseTitles("{}"))
    }

    @Test fun whatEachSlotShowsIsWhatTheLookWears() {
        val c = Armory.parseCharacter(Region.US, String(javaClass.classLoader!!.getResourceAsStream("porter/armory-model.json")!!.readBytes()))
        // Without the API: the Armory's items and the looks they were given.
        val plain = Porter.worn(c, null)
        assertEquals(Worn("head", 271546, 147183, null, "HEAD"), plain.single { it.slot == "head" })
        // With it: what the slot shows, by item and variant; the Armory's inventory type kept (the weapon's hand).
        val worn = Porter.worn(c, BattleNet.parseAppearance(appearanceJson))
        assertEquals(Worn("head", 147183, inventoryType = "HEAD", modifier = 0), worn.single { it.slot == "head" })
        assertEquals(Worn("weapon", 253285, inventoryType = "TWOHWEAPON", modifier = 3), worn.single { it.slot == "weapon" })
        // A slot the API didn't name keeps the Armory's.
        assertEquals(plain.single { it.slot == "chest" }, worn.single { it.slot == "chest" })
        assertEquals(plain.size, worn.size)
        assertEquals("hand", BattleNet.armorySlot("HANDS"))
        assertNull(BattleNet.armorySlot("AMMO"))
    }

    @Test fun theLiveApi() {
        val id = System.getenv("BLIZZ_BNET_ID")
        val secret = System.getenv("BLIZZ_BNET_SECRET")
        assumeTrue(!id.isNullOrBlank() && !secret.isNullOrBlank())
        val bnet = BattleNet(com.logie.blizz.porter.net.HttpNet(com.logie.blizz.porter.net.HttpNet.BROWSER), id!!, secret!!)
        bnet.check()
        val armory = Armory(com.logie.blizz.porter.net.HttpNet(com.logie.blizz.porter.net.HttpNet.BROWSER))
        val found = armory.search(Region.US, "thrall").first.first { it.level >= 70 }
        val a = bnet.appearance(Region.US, found.realmSlug, found.slug)
        assertTrue("no appearance", a != null && a.choices.isNotEmpty() && a.shown.isNotEmpty())
        println("BattleNetTest live: ${a!!.choices.size} choices, ${a.shown.size} slots, " +
            "${bnet.completedQuests(Region.US, found.realmSlug, found.slug).size} quests, ${bnet.achievements(Region.US, found.realmSlug, found.slug).size} achievements")
    }
}
