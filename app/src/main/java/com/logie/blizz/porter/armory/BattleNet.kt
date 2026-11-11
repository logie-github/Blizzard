package com.logie.blizz.porter.armory

import android.util.Base64
import com.logie.blizz.porter.net.Net
import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException
import java.net.URLEncoder

/** What Blizzard's own API tells of a character beyond the Armory's website: their customization choices and what each slot shows. */
data class Appearance(
    /** Customization option id to choice id (the game's ChrCustomizationOption and ChrCustomizationChoice). */
    val choices: Map<Int, Int>,
    /** What each slot shows: the API's slot type (HEAD, MAIN_HAND...), the item, and its look among the item's variants. */
    val shown: List<Shown>,
) {
    data class Shown(val slotType: String, val item: Int, val modifier: Int)
}

data class CompletedQuest(val id: Int, val name: String)

data class EarnedAchievement(val id: Int, val name: String, val completedAt: Long?)

data class Titles(val ids: List<Int>, val active: Int?)

/**
 * Blizzard's own World of Warcraft API (develop.battle.net), with a client id and secret the person makes there for free: what
 * the Armory's website keeps back. A character's face, hair and skin choices and what each slot shows ([appearance]), the
 * quests they completed, their achievements with when, their titles. A token is had from Battle.net's OAuth with the client's
 * id and secret (`POST https://oauth.battle.net/token`, `grant_type=client_credentials`) and kept until it runs out; then the
 * profile API: `https://<region>.api.blizzard.com/profile/wow/character/<realm>/<name>/<what>?namespace=profile-<region>&locale=en_US`.
 *
 * The shapes read are those Blizzard's API answers with (checked against a published client's types: `customizations` of
 * `option` and `choice`, `quests`, `achievements` with `completed_timestamp`, `titles` and `active_title`); a field missing is
 * read as none. Not tried against the API itself here (it needs the person's own key): `BattleNetTest.theLiveApi` does so with
 * one in `BLIZZ_BNET_ID` and `BLIZZ_BNET_SECRET`.
 */
class BattleNet(private val net: Net, private val clientId: String, private val secret: String) {
    @Volatile private var token: String? = null
    @Volatile private var tokenUntil = 0L

    /** Whether the id and secret are good (a token is had with them). */
    fun check() {
        token(force = true)
    }

    private fun token(force: Boolean = false): String {
        val now = System.currentTimeMillis()
        token?.takeIf { !force && now < tokenUntil }?.let { return it }
        val basic = Base64.encodeToString("$clientId:$secret".toByteArray(), Base64.NO_WRAP)
        val reply = net.post(
            "https://oauth.battle.net/token",
            "grant_type=client_credentials".toByteArray(),
            mapOf("Authorization" to "Basic $basic", "Content-Type" to "application/x-www-form-urlencoded"),
        )
        if (reply.code == 401 || reply.code == 400) throw IOException("Battle.net refused the client id and secret.")
        if (!reply.ok) throw IOException("Battle.net answered ${reply.code} for a token.")
        val json = JSONObject(reply.text)
        val access = json.optString("access_token").ifEmpty { throw IOException("Battle.net gave no token.") }
        token = access
        tokenUntil = now + (json.optLong("expires_in", 3600) - 60).coerceAtLeast(60) * 1000
        return access
    }

    private fun profile(region: Region, realmSlug: String, name: String, what: String): String? {
        val character = URLEncoder.encode(name.lowercase(), "UTF-8").replace("+", "%20")
        val realm = URLEncoder.encode(realmSlug.lowercase(), "UTF-8")
        val url = "https://${region.code}.api.blizzard.com/profile/wow/character/$realm/$character/$what?namespace=profile-${region.code}&locale=en_US"
        var reply = net.get(url, mapOf("Authorization" to "Bearer ${token()}"))
        if (reply.code == 401) reply = net.get(url, mapOf("Authorization" to "Bearer ${token(force = true)}"))
        // A character whose profile is private, or not seen lately, has none: that is no fault of the key.
        if (reply.code == 404 || reply.code == 403) return null
        if (!reply.ok) throw IOException("Blizzard's API answered ${reply.code} for the character's $what.")
        return reply.text
    }

    fun appearance(region: Region, realmSlug: String, name: String): Appearance? =
        profile(region, realmSlug, name, "appearance")?.let { parseAppearance(it) }

    fun completedQuests(region: Region, realmSlug: String, name: String): List<CompletedQuest> =
        profile(region, realmSlug, name, "quests/completed")?.let { parseQuests(it) } ?: emptyList()

    fun achievements(region: Region, realmSlug: String, name: String): List<EarnedAchievement> =
        profile(region, realmSlug, name, "achievements")?.let { parseAchievements(it) } ?: emptyList()

    fun titles(region: Region, realmSlug: String, name: String): Titles =
        profile(region, realmSlug, name, "titles")?.let { parseTitles(it) } ?: Titles(emptyList(), null)

    companion object {
        private fun JSONArray?.objects(): List<JSONObject> = if (this == null) emptyList() else (0 until length()).mapNotNull { optJSONObject(it) }

        fun parseAppearance(json: String): Appearance {
            val o = JSONObject(json)
            val choices = LinkedHashMap<Int, Int>()
            for (c in o.optJSONArray("customizations").objects()) {
                val option = c.optJSONObject("option")?.optInt("id") ?: 0
                val choice = c.optJSONObject("choice")?.optInt("id") ?: 0
                if (option > 0 && choice > 0) choices[option] = choice
            }
            val shown = o.optJSONArray("items").objects().mapNotNull { i ->
                val id = i.optInt("id")
                val slot = i.optJSONObject("slot")?.optString("type").orEmpty()
                if (id > 0 && slot.isNotEmpty()) Appearance.Shown(slot, id, i.optInt("item_appearance_modifier_id")) else null
            }
            return Appearance(choices, shown)
        }

        fun parseQuests(json: String): List<CompletedQuest> =
            JSONObject(json).optJSONArray("quests").objects().filter { it.optInt("id") > 0 }.map { CompletedQuest(it.optInt("id"), it.optString("name")) }

        fun parseAchievements(json: String): List<EarnedAchievement> =
            JSONObject(json).optJSONArray("achievements").objects().mapNotNull { a ->
                val id = a.optInt("id").takeIf { it > 0 } ?: a.optJSONObject("achievement")?.optInt("id") ?: 0
                // Only those earned: an achievement under way is listed too, without its time.
                val at = if (a.has("completed_timestamp")) a.optLong("completed_timestamp") else null
                if (id <= 0 || at == null || at <= 0) null
                else EarnedAchievement(id, a.optJSONObject("achievement")?.optString("name").orEmpty(), at)
            }

        fun parseTitles(json: String): Titles {
            val o = JSONObject(json)
            return Titles(o.optJSONArray("titles").objects().map { it.optInt("id") }.filter { it > 0 }, o.optJSONObject("active_title")?.optInt("id")?.takeIf { it > 0 })
        }

        /** The Armory's slot name for the API's slot type (what is shown there). */
        fun armorySlot(slotType: String): String? = when (slotType) {
            "HEAD" -> "head"; "NECK" -> "neck"; "SHOULDER" -> "shoulder"; "BACK" -> "back"; "CHEST" -> "chest"; "SHIRT" -> "shirt"
            "TABARD" -> "tabard"; "WRIST" -> "wrist"; "HANDS" -> "hand"; "WAIST" -> "waist"; "LEGS" -> "leg"; "FEET" -> "foot"
            "FINGER_1" -> "leftFinger"; "FINGER_2" -> "rightFinger"; "TRINKET_1" -> "leftTrinket"; "TRINKET_2" -> "rightTrinket"
            "MAIN_HAND" -> "weapon"; "OFF_HAND" -> "offhand"; else -> null
        }
    }
}
