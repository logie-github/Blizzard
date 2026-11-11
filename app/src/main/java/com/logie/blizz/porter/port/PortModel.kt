package com.logie.blizz.porter.port

import com.logie.blizz.wow.Realm

/**
 * A character as Blizzard's Armory describes it today: what the porter is given to carry over. Plain facts of the
 * retail game (its race and class ids, its item ids, its mount ids); nothing here knows about a realm. Everything but
 * the first six values may be missing: the Armory hides some of it, and a look-up may only have fetched part.
 */
data class PortCharacter(
    val name: String,
    /** Retail's race id (1 Human ... 22 Worgen, 29 Void Elf, 52/70 Dracthyr, 84/85 Earthen ...). */
    val raceId: Int,
    /** Retail's class id (1 Warrior ... 10 Monk, 11 Druid, 12 Demon Hunter, 13 Evoker). */
    val classId: Int,
    /** 0 male, 1 female. */
    val gender: Int,
    val faction: PortFaction,
    /** The retail level (1 to [PortLevels.RETAIL_CAP]). */
    val level: Int,
    val spec: PortSpec? = null,
    val equipment: List<PortEquipment> = emptyList(),
    val professions: List<PortProfession> = emptyList(),
    val mounts: List<PortMount> = emptyList(),
    val reputations: List<PortReputation> = emptyList(),
    val completedQuests: List<PortQuest> = emptyList(),
    val achievements: List<PortAchievement> = emptyList(),
    val titleIds: List<Int> = emptyList(),
    /** The title it shows beside its name, one of [titleIds]. */
    val activeTitleId: Int? = null,
    val appearance: PortAppearance? = null,
)

enum class PortFaction { ALLIANCE, HORDE, NEUTRAL }

enum class PortRole { TANK, HEALER, DAMAGE }

enum class PortStat { STRENGTH, AGILITY, INTELLECT }

/** The specialization it plays: its name ("Protection"), what it does in a group, and the stat its gear is built on. */
data class PortSpec(val name: String, val role: PortRole, val primaryStat: PortStat? = null)

/** One thing it wears. */
data class PortEquipment(
    /**
     * The Armory's slot: its profile's names (head, neck, shoulder, back, chest, shirt, tabard, wrist, hand, waist, leg,
     * foot, leftFinger, rightFinger, leftTrinket, rightTrinket, weapon, offhand) or its item API's (HEAD, MAIN_HAND,
     * FINGER_1, ...); either is read ([PortSlots.realmSlot]).
     */
    val slot: String,
    val itemId: Int,
    val name: String,
    /** The Armory's quality name (POOR, COMMON, UNCOMMON, RARE, EPIC, LEGENDARY, ARTIFACT, HEIRLOOM), if it gave one. */
    val quality: String? = null,
    val itemLevel: Int = 0,
    /** The Armory's inventory type: HEAD, ROBE, TWOHWEAPON, WEAPON, WEAPONMAINHAND, WEAPONOFFHAND, SHIELD, HOLDABLE, RANGED, RANGEDRIGHT, ... */
    val inventoryType: String = "",
    /** The item's class and subclass ids (2 weapon, 4 armor; the subclass names the kind of weapon or armor). */
    val itemClass: Int = -1,
    val itemSubclass: Int = -1,
    /** The item whose look it is shown with, when the player changed the look. */
    val transmogItemId: Int? = null,
)

/** A profession: its skill line (164 Blacksmithing), whether it is a primary one, and how far each expansion's part of it is. */
data class PortProfession(val skillLineId: Int, val name: String, val primary: Boolean? = null, val tiers: List<PortProfessionTier> = emptyList())

/** One expansion's part of a profession ("Northrend Blacksmithing", 75 points of 75). */
data class PortProfessionTier(val name: String, val points: Int, val maxPoints: Int = 0)

/**
 * A mount it has: the Armory's mount id (retail's Mount table, not a spell) and its name. [spellId] is the spell that
 * summons it, when the caller knows it; otherwise the porter goes by the name.
 */
data class PortMount(val id: Int, val name: String, val spellId: Int? = null)

/**
 * A standing with a faction: its name, the standing's words ("Exalted", "Revered", "Honored", "Friendly", "Neutral",
 * "Unfriendly", "Hostile", "Hated"; newer factions' "Renown 12" and friendships have no counterpart), and how far into
 * that standing, if the Armory said.
 */
data class PortReputation(val factionName: String, val standing: String, val value: Int? = null)

/** A quest it completed; its title, when known, lets the porter make sure the realm's quest of that id is the same quest. */
data class PortQuest(val id: Int, val name: String? = null)

/** An achievement it earned, and when (seconds since 1970), if the Armory said. */
data class PortAchievement(val id: Int, val earnedAt: Long? = null)

/** The five looks the old character creator has. */
data class PortAppearance(val skin: Int = 0, val face: Int = 0, val hairStyle: Int = 0, val hairColor: Int = 0, val facialHair: Int = 0)

/** How good the gear a level-cap character is given may be. Below the caps of the game's expansions it changes only the quality allowed. */
enum class GearTier(val label: String, val about: String) {
    FRESH("Fresh", "dungeon blues: what a character has just as it reaches the cap"),
    RAID("Raid", "early raid epics"),
    BEST("Best", "the last raid tier's"),
}

/** What the person chose on the screen. */
data class PortOptions(
    val realm: Realm,
    /** The realm account that will own the character. */
    val account: String,
    /** The name, race, class and gender the character will have on the realm (the realm's own ids). */
    val name: String,
    val race: Int,
    val classId: Int,
    val gender: Int,
    /** The level on the realm; null for the retail level scaled to the realm's cap ([PortLevels.scaled]). */
    val level: Int? = null,
    /** Its money in copper; null for none. More than the realm can hold is cut to what it can. */
    val money: Long? = null,
    val gearTier: GearTier = GearTier.FRESH,
)

/** Levels on both sides. */
object PortLevels {
    /** Retail's level cap (Midnight). */
    const val RETAIL_CAP = 90

    /**
     * The retail level as a level on a realm whose cap is [cap]: the same share of the way there, at least 1, and a
     * retail level-cap character exactly on the cap.
     */
    fun scaled(retailLevel: Int, cap: Int, retailCap: Int = RETAIL_CAP): Int {
        if (cap <= 1) return 1
        if (retailLevel >= retailCap) return cap
        return Math.round(retailLevel.coerceAtLeast(1).toDouble() / retailCap * cap).toInt().coerceIn(1, cap)
    }
}
