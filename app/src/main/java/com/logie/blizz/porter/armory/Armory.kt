package com.logie.blizz.porter.armory

import com.logie.blizz.porter.net.Net
import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException
import java.net.URLEncoder

/** The Armory's four regions (its own "realm options"): each has its own realms and characters. */
enum class Region(val code: String, val label: String) {
    US("us", "Americas & Oceania"), EU("eu", "Europe"), KR("kr", "Korea"), TW("tw", "Taiwan");

    companion object {
        fun of(code: String?): Region = entries.firstOrNull { it.code.equals(code, ignoreCase = true) } ?: US
    }
}

/** One line of the Armory's search results. */
data class Found(
    val region: Region,
    val name: String,
    val realm: String,
    /** The realm and the character as the Armory's addresses spell them. */
    val realmSlug: String,
    val slug: String,
    val level: Int,
    val race: String,
    val className: String,
    val faction: String,
    val avatar: String?,
)

/** Something a character has on. */
data class ArmoryItem(
    /** The Armory's own name for the place: head, neck, shoulder, back, chest, shirt, tabard, wrist, hand, waist, leg, foot, leftFinger, rightFinger, leftTrinket, rightTrinket, weapon, offhand. */
    val slot: String,
    val id: Int,
    val name: String,
    /** POOR, COMMON, UNCOMMON, RARE, EPIC, LEGENDARY, ARTIFACT, HEIRLOOM. */
    val quality: String,
    val itemLevel: Int,
    /** The game's inventory type: HEAD, SHOULDER, CHEST, ROBE, WEAPON, TWOHWEAPON, SHIELD, HOLDABLE, ... */
    val inventoryType: String,
    val itemClass: Int,
    val itemSubclass: Int,
    /** The item whose look this one was given (transmogrification), if any. */
    val transmogItemId: Int?,
    val transmogName: String?,
    /** The item's own look among its variants (ItemModifiedAppearance), when the Armory says. */
    val modifiedAppearanceId: Int?,
    val bonusList: List<Int>,
    val icon: String?,
)

data class ProfessionTier(val name: String, val points: Int, val max: Int)

data class Profession(val id: Int, val name: String, val primary: Boolean, val tiers: List<ProfessionTier>)

/** A character as the Armory's summary gives it, without a key: who they are and what they wear. Not their face and hair, nor their quests. */
data class ArmoryCharacter(
    val region: Region,
    val name: String,
    val realm: String,
    val realmSlug: String,
    val slug: String,
    val level: Int,
    val raceId: Int,
    val race: String,
    val classId: Int,
    val className: String,
    /** 0 male, 1 female. */
    val gender: Int,
    /** ALLIANCE or HORDE. */
    val faction: String,
    val spec: String?,
    /** TANK, HEALER or DAMAGE. */
    val role: String?,
    val guild: String?,
    val averageItemLevel: Int,
    val achievementPoints: Int,
    /** The Armory's own picture of the character (a transparent render), and the small portrait. */
    val render: String?,
    val avatar: String?,
    val items: List<ArmoryItem>,
    val professions: List<Profession>,
    /** When the Armory last saw the character (milliseconds), or 0. */
    val updated: Long,
)

data class ArmoryMount(val id: Int, val name: String)

/** A faction's standing as the Armory words it ("Exalted", "Revered", "Renown 12"), under its group ("Classic", "Wrath of the Lich King"). */
data class ArmoryReputation(val group: String, val name: String, val standing: String, val value: Int?, val max: Int?)

/**
 * Blizzard's Armory, as its website gives it to any visitor (worldofwarcraft.blizzard.com): the search with its regions, a
 * character's summary (`model.json`: race, sex, class, level, everything worn with its transmogrification, professions),
 * the mounts collected and the reputations. No key is needed for any of it. What the site does not give is the character's
 * face, hair and skin choices, the quests done and the achievements one by one: those are Blizzard's API's
 * ([com.logie.blizz.porter.armory.BattleNet], with the person's own key).
 *
 * The parsing is plain functions on the pages' text ([parseSearch], [parseCharacter], [parseMounts], [parseReputations]),
 * unit-tested on pages kept in the tests (names changed).
 */
class Armory(private val net: Net) {
    /** The part of the address after the language: "worldsoul" in 2026 (the site names it for the game's current saga). */
    @Volatile private var saga: String? = null

    /** Characters whose names begin like [query] in [region], a hundred a [page] (from 1), and whether more follow. */
    fun search(region: Region, query: String, page: Int = 1): Pair<List<Found>, Boolean> {
        val q = query.trim()
        if (q.length < 2) return emptyList<Found>() to false
        val url = "${base(region)}/character?q=${encode(q)}" + if (page > 1) "&page=$page" else ""
        val reply = net.get(url)
        if (!reply.ok) throw IOException("The Armory answered ${reply.code} to the search.")
        return parseSearch(region, reply.text) to reply.text.contains("page=${page + 1}")
    }

    fun character(region: Region, realmSlug: String, slug: String): ArmoryCharacter {
        val reply = net.get("${page(region, realmSlug, slug)}/model.json")
        if (reply.code == 404) throw IOException("The Armory has no such character (it shows characters that logged in lately, above level 10).")
        if (!reply.ok) throw IOException("The Armory answered ${reply.code} for the character.")
        return parseCharacter(region, reply.text)
    }

    /** The mounts the character has, by the game's mount ids. Empty when the Armory won't say. */
    fun mounts(region: Region, realmSlug: String, slug: String): List<ArmoryMount> {
        val reply = net.get("${page(region, realmSlug, slug)}/collections/mounts.json")
        return if (reply.ok) parseMounts(reply.text) else emptyList()
    }

    fun reputations(region: Region, realmSlug: String, slug: String): List<ArmoryReputation> {
        val reply = net.get("${page(region, realmSlug, slug)}/reputation.json")
        return if (reply.ok) parseReputations(reply.text) else emptyList()
    }

    private fun page(region: Region, realmSlug: String, slug: String) = "${base(region)}/character/${encode(realmSlug)}/${encode(slug)}"

    private fun base(region: Region): String = "$SITE/en-us/${saga()}/${region.code}/armory"

    /** Asked of the site once: its old search address forwards to the current one, which names the saga. */
    private fun saga(): String {
        saga?.let { return it }
        val found = runCatching { sagaOf(net.get("$SITE/en-us/search?q=aa").url) }.getOrNull() ?: DEFAULT_SAGA
        saga = found
        return found
    }

    companion object {
        const val SITE = "https://worldofwarcraft.blizzard.com"
        const val DEFAULT_SAGA = "worldsoul"

        /** "worldsoul" from `https://worldofwarcraft.blizzard.com/en-us/worldsoul/us/armory?q=aa`, or null. */
        fun sagaOf(url: String): String? =
            Regex("""^https://worldofwarcraft\.blizzard\.com/[a-z]{2}-[a-z]{2}/([a-z0-9-]+)/[a-z]{2}/armory""").find(url)?.groupValues?.get(1)

        private fun encode(text: String) = URLEncoder.encode(text, "UTF-8").replace("+", "%20")

        /** The rows of the site's result table: one link each, with the name, then level, race, class, faction and realm in columns. */
        fun parseSearch(region: Region, html: String): List<Found> {
            val out = ArrayList<Found>()
            for (row in html.split("class=\"Link SortTable-row\"").drop(1)) {
                val href = Regex("""href="([^"]+)"""").find(row)?.groupValues?.get(1) ?: continue
                val path = Regex("""/armory/character/([^/"?]+)/([^/"?]+)""").find(href) ?: continue
                val name = Regex("""Character-name">([^<]*)<""").find(row)?.groupValues?.get(1)?.let { unescape(it).trim() } ?: continue
                val columns = Regex("""SortTable-data text-nowrap[^"]*">([^<]*)<""").findAll(row).map { unescape(it.groupValues[1]).trim() }.toList()
                if (columns.size < 5 || name.isEmpty()) continue
                val avatar = Regex("""background-image:url\((?:&quot;|")?([^)&"]+)""").find(row)?.groupValues?.get(1)
                out += Found(
                    region = region, name = name, realm = columns[4],
                    realmSlug = java.net.URLDecoder.decode(path.groupValues[1], "UTF-8"), slug = java.net.URLDecoder.decode(path.groupValues[2], "UTF-8"),
                    level = columns[0].toIntOrNull() ?: 0, race = columns[1], className = columns[2], faction = columns[3], avatar = avatar,
                )
            }
            return out
        }

        fun parseCharacter(region: Region, json: String): ArmoryCharacter {
            val c = JSONObject(json).optJSONObject("character") ?: throw IOException("The Armory's answer holds no character.")
            val realm = c.optJSONObject("realm")
            val gear = c.optJSONObject("gear")
            val items = ArrayList<ArmoryItem>()
            if (gear != null) for (slot in gear.keys()) gear.optJSONObject(slot)?.let { item(slot, it) }?.let { items += it }
            val professions = ArrayList<Profession>()
            c.optJSONObject("professions")?.let { p ->
                for ((key, primary) in listOf("primaries" to true, "secondaries" to false)) {
                    val list = p.optJSONArray(key) ?: continue
                    for (i in 0 until list.length()) {
                        val o = list.optJSONObject(i) ?: continue
                        val tiers = o.optJSONArray("tiers").objects().map { ProfessionTier(it.optString("name"), it.optInt("skillPoints"), it.optInt("maxSkillPoints")) }
                        professions += Profession(o.optInt("id"), o.optString("name"), primary, tiers)
                    }
                }
            }
            return ArmoryCharacter(
                region = Region.of(c.optString("region", region.code)),
                name = c.optString("name"),
                realm = realm?.optString("name").orEmpty(),
                realmSlug = realm?.optString("slug").orEmpty(),
                slug = c.optString("slug", c.optString("name").lowercase()),
                level = c.optInt("level"),
                raceId = c.optJSONObject("race")?.optInt("id") ?: 0,
                race = c.optJSONObject("race")?.optString("name").orEmpty(),
                classId = c.optJSONObject("class")?.optInt("id") ?: 0,
                className = c.optJSONObject("class")?.optString("name").orEmpty(),
                gender = if (c.optJSONObject("gender")?.optString("enum") == "FEMALE") 1 else 0,
                faction = c.optJSONObject("faction")?.optString("enum").orEmpty(),
                spec = c.optJSONObject("spec")?.optString("name")?.takeIf { it.isNotEmpty() },
                role = c.optJSONObject("spec")?.optJSONObject("role")?.optString("enum")?.takeIf { it.isNotEmpty() },
                guild = c.optJSONObject("guild")?.optString("name")?.takeIf { it.isNotEmpty() },
                averageItemLevel = c.optInt("averageItemLevel"),
                achievementPoints = c.optInt("achievement"),
                render = c.optJSONObject("media")?.optJSONObject("main-raw")?.optString("url")?.takeIf { it.isNotEmpty() }
                    ?: c.optJSONObject("render")?.optJSONObject("foreground")?.optString("url")?.takeIf { it.isNotEmpty() },
                avatar = c.optJSONObject("avatar")?.optString("url")?.takeIf { it.isNotEmpty() },
                items = items.sortedBy { ORDER.indexOf(it.slot).let { i -> if (i < 0) ORDER.size else i } },
                professions = professions,
                updated = c.optJSONObject("lastUpdatedTimestamp")?.optLong("epoch") ?: 0L,
            )
        }

        private fun item(slot: String, o: JSONObject): ArmoryItem? {
            val id = o.optInt("id")
            if (id <= 0) return null
            val transmog = o.optJSONObject("transmog")?.optJSONObject("item")
            val bonus = o.optJSONArray("bonus_list")
            return ArmoryItem(
                slot = slot, id = id, name = o.optString("name"),
                quality = o.optJSONObject("quality")?.optString("type").orEmpty(),
                itemLevel = o.optJSONObject("level")?.optInt("value") ?: 0,
                inventoryType = o.optJSONObject("inventory_type")?.optString("type").orEmpty(),
                itemClass = o.optJSONObject("item_class")?.optInt("id") ?: 0,
                itemSubclass = o.optJSONObject("item_subclass")?.optInt("id") ?: 0,
                transmogItemId = transmog?.optInt("id")?.takeIf { it > 0 },
                transmogName = transmog?.optString("name")?.takeIf { it.isNotEmpty() },
                modifiedAppearanceId = o.optInt("modified_appearance_id").takeIf { it > 0 },
                bonusList = if (bonus == null) emptyList() else List(bonus.length()) { bonus.optInt(it) },
                icon = o.optJSONObject("media")?.optJSONObject("content")?.optJSONArray("assets").objects()
                    .firstOrNull { it.optString("key") == "icon" }?.optString("value"),
            )
        }

        fun parseMounts(json: String): List<ArmoryMount> =
            JSONObject(json).optJSONArray("mounts").objects().filter { it.optBoolean("collected") && it.optInt("id") > 0 }
                .map { ArmoryMount(it.optInt("id"), it.optString("name")) }

        /** Every faction with a standing, whatever its depth in the site's groups (a faction can hold others: "Horde" holds its cities). */
        fun parseReputations(json: String): List<ArmoryReputation> {
            val out = ArrayList<ArmoryReputation>()
            fun walk(group: String, list: JSONArray?) {
                for (o in list.objects()) {
                    val standing = o.optString("standing")
                    if (standing.isNotEmpty()) {
                        out += ArmoryReputation(group, o.optString("name"), standing, if (o.has("value")) o.optInt("value") else null, if (o.has("maxValue")) o.optInt("maxValue") else null)
                    }
                    walk(group, o.optJSONArray("reputations"))
                }
            }
            for (group in JSONObject(json).optJSONArray("reputations").objects()) walk(group.optString("name"), group.optJSONArray("reputations"))
            return out.distinctBy { it.name }
        }

        private fun JSONArray?.objects(): List<JSONObject> = if (this == null) emptyList() else (0 until length()).mapNotNull { optJSONObject(it) }

        /** The order a character sheet lists what is worn. */
        val ORDER = listOf("head", "neck", "shoulder", "back", "chest", "shirt", "tabard", "wrist", "hand", "waist", "leg", "foot",
            "leftFinger", "rightFinger", "leftTrinket", "rightTrinket", "weapon", "offhand")

        fun unescape(text: String): String = Regex("""&(#x?[0-9a-fA-F]+|[a-z]+);""").replace(text) { m ->
            val body = m.groupValues[1]
            when {
                body.startsWith("#x") || body.startsWith("#X") -> body.drop(2).toIntOrNull(16)?.let { String(Character.toChars(it)) } ?: m.value
                body.startsWith("#") -> body.drop(1).toIntOrNull()?.let { String(Character.toChars(it)) } ?: m.value
                else -> when (body) { "amp" -> "&"; "lt" -> "<"; "gt" -> ">"; "quot" -> "\""; "apos" -> "'"; "nbsp" -> " "; else -> m.value }
            }
        }
    }
}
