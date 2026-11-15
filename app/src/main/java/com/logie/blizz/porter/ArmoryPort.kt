package com.logie.blizz.porter

import com.logie.blizz.porter.armory.ArmoryCharacter
import com.logie.blizz.porter.armory.ArmoryMount
import com.logie.blizz.porter.armory.ArmoryReputation
import com.logie.blizz.porter.armory.CompletedQuest
import com.logie.blizz.porter.armory.EarnedAchievement
import com.logie.blizz.porter.armory.Titles
import com.logie.blizz.porter.look.LegacyLooks
import com.logie.blizz.porter.port.PortAchievement
import com.logie.blizz.porter.port.PortAppearance
import com.logie.blizz.porter.port.PortCharacter
import com.logie.blizz.porter.port.PortEquipment
import com.logie.blizz.porter.port.PortFaction
import com.logie.blizz.porter.port.PortMount
import com.logie.blizz.porter.port.PortProfession
import com.logie.blizz.porter.port.PortProfessionTier
import com.logie.blizz.porter.port.PortQuest
import com.logie.blizz.porter.port.PortReputation
import com.logie.blizz.porter.port.PortRole
import com.logie.blizz.porter.port.PortSpec
import com.logie.blizz.porter.port.PortStat
import com.logie.blizz.porter.wago.Tables

/**
 * A character as the Armory (and, with the person's key, Blizzard's API) gives it, made into what the realm porter takes
 * ([PortCharacter]): who they are, what they wear, their professions, mounts, standings, and with the key their quests,
 * achievements, titles and looks. Plain Kotlin: the fetching is the screens' ([com.logie.blizz.ui.CharacterPorter]).
 */
object ArmoryPort {
    /** What the port carries beyond the Armory's summary, fetched as the person ports. */
    data class Extras(
        val mounts: List<ArmoryMount> = emptyList(),
        /** The spell each mount is summoned with (the game's Mount table), by the Armory's mount id. */
        val mountSpells: Map<Int, Int> = emptyMap(),
        val reputations: List<ArmoryReputation> = emptyList(),
        val quests: List<CompletedQuest> = emptyList(),
        val achievements: List<EarnedAchievement> = emptyList(),
        val titles: Titles? = null,
        /** Their looks as the old creator numbers them ([appearance]), when Blizzard's API gave their choices. */
        val appearance: PortAppearance? = null,
    )

    fun character(c: ArmoryCharacter, extras: Extras = Extras()): PortCharacter = PortCharacter(
        name = c.name,
        raceId = c.raceId,
        classId = c.classId,
        gender = c.gender.coerceIn(0, 1),
        faction = when (c.faction.uppercase()) {
            "ALLIANCE" -> PortFaction.ALLIANCE
            "HORDE" -> PortFaction.HORDE
            else -> PortFaction.NEUTRAL
        },
        level = c.level.coerceAtLeast(1),
        spec = spec(c.classId, c.spec, c.role),
        equipment = c.items.map {
            PortEquipment(it.slot, it.id, it.name, it.quality.ifEmpty { null }, it.itemLevel, it.inventoryType, it.itemClass, it.itemSubclass, it.transmogItemId)
        },
        professions = c.professions.map { p -> PortProfession(p.id, p.name, p.primary, p.tiers.map { PortProfessionTier(it.name, it.points, it.max) }) },
        mounts = extras.mounts.map { PortMount(it.id, it.name, extras.mountSpells[it.id]) },
        reputations = extras.reputations.map { PortReputation(it.name, it.standing, it.value) },
        completedQuests = extras.quests.map { PortQuest(it.id, it.name.ifBlank { null }) },
        // Blizzard's API gives the time in milliseconds; the realm keeps seconds.
        achievements = extras.achievements.map { PortAchievement(it.id, it.completedAt?.takeIf { at -> at > 0 }?.let { at -> at / 1000 }) },
        titleIds = extras.titles?.ids.orEmpty(),
        activeTitleId = extras.titles?.active,
        appearance = extras.appearance,
    )

    private val TANKS = setOf("Protection", "Guardian", "Blood", "Brewmaster", "Vengeance")
    private val HEALERS = setOf("Holy", "Discipline", "Restoration", "Mistweaver", "Preservation")

    /** The specialization by its name, what it does in a group (the Armory's role, else by its name) and the stat its gear is built on. */
    fun spec(classId: Int, name: String?, role: String?): PortSpec? {
        if (name.isNullOrBlank()) return null
        val r = when (role?.uppercase()) {
            "TANK" -> PortRole.TANK
            "HEALER", "HEALING" -> PortRole.HEALER
            "DAMAGE", "DPS" -> PortRole.DAMAGE
            else -> when {
                name in TANKS -> PortRole.TANK
                name in HEALERS -> PortRole.HEALER
                else -> PortRole.DAMAGE
            }
        }
        return PortSpec(name, r, primaryStat(classId, name))
    }

    /** The stat a specialization's gear is built on. */
    fun primaryStat(classId: Int, spec: String): PortStat? = when (classId) {
        1, 6 -> PortStat.STRENGTH                                                        // warrior, death knight
        2 -> if (spec == "Holy") PortStat.INTELLECT else PortStat.STRENGTH                // paladin
        3, 4, 12 -> PortStat.AGILITY                                                      // hunter, rogue, demon hunter
        5, 8, 9, 13 -> PortStat.INTELLECT                                                 // priest, mage, warlock, evoker
        7 -> if (spec == "Enhancement") PortStat.AGILITY else PortStat.INTELLECT          // shaman
        10 -> if (spec == "Mistweaver") PortStat.INTELLECT else PortStat.AGILITY          // monk
        11 -> if (spec == "Feral" || spec == "Guardian") PortStat.AGILITY else PortStat.INTELLECT // druid
        else -> null
    }

    /** The spell each of [mountIds] is summoned with (the game's Mount table: SourceSpellID), for those that have one. */
    fun mountSpells(tables: Tables, mountIds: Collection<Int>): Map<Int, Int> {
        if (mountIds.isEmpty()) return emptyMap()
        return tables.rows("Mount", "ID", mountIds.distinct()).mapNotNull { r ->
            val spell = r.int("SourceSpellID")
            if (spell > 0) r.int("ID") to spell else null
        }.toMap()
    }

    /**
     * Blizzard's API's customization [choices] (option to choice) as the old creator's looks of [race] and [sex]
     * ([LegacyLooks]), with the words for what had no old counterpart (the realm's first is used for those).
     */
    fun appearance(tables: Tables, race: Int, sex: Int, choices: Map<Int, Int>): Pair<PortAppearance, List<String>>? {
        if (choices.isEmpty()) return null
        val legacy = LegacyLooks.of(tables, race, sex, choices.values)
        if (legacy.values.isEmpty()) return null
        val v = legacy.values
        val appearance = PortAppearance(
            skin = v[LegacyLooks.SKIN] ?: 0,
            face = v[LegacyLooks.FACE] ?: 0,
            hairStyle = v[LegacyLooks.HAIR_STYLE] ?: 0,
            hairColor = v[LegacyLooks.HAIR_COLOR] ?: 0,
            facialHair = v[LegacyLooks.FACIAL_HAIR] ?: 0,
        )
        return appearance to legacy.unmatched.mapNotNull { LegacyLooks.NAMES[it] }
    }
}
