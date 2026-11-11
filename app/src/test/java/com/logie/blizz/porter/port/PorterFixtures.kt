package com.logie.blizz.porter.port

import com.logie.blizz.wow.Realm

/**
 * Retail characters as the Armory would describe them in the Midnight era, made up for the porter's tests (no real
 * player's names): gear of item ids above 200000 (retail's own, which 3.3.5a hasn't) with some transmogs and some old
 * items 3.3.5a has, professions in retail's tiers, mounts by the Armory's mount ids and names, reputations by name.
 */
object PorterFixtures {
    data class Fixture(val character: PortCharacter, val options: PortOptions, val about: String)

    private fun gear(slot: String, id: Int, name: String, type: String, itemClass: Int, subclass: Int, ilvl: Int = 690, transmog: Int? = null, quality: String = "EPIC") =
        PortEquipment(slot, id, name, quality, ilvl, type, itemClass, subclass, transmog)

    private fun tiers(vararg pairs: Pair<String, Int>) = pairs.map { PortProfessionTier(it.first, it.second, if (it.first.startsWith("Classic")) 300 else 75) }

    private val VETERAN_ACHIEVEMENTS = listOf(6, 7, 8, 9, 10, 11, 12, 13, 42, 43, 1283, 2136, 457, 19458, 40953).map { PortAchievement(it, 1700000000L + it) }

    /** A level-cap plate tank: a human Protection warrior, ported at the realm's own 80 with the best gear tier. */
    val tank = Fixture(
        PortCharacter(
            name = "Brannoc", raceId = 1, classId = 1, gender = 0, faction = PortFaction.ALLIANCE, level = 90,
            spec = PortSpec("Protection", PortRole.TANK, PortStat.STRENGTH),
            equipment = listOf(
                gear("head", 237610, "Living Luck's Faceguard", "HEAD", 4, 4, transmog = 51227),
                gear("neck", 237568, "Chrysalis of Sundered Souls", "NECK", 4, 0),
                gear("shoulder", 237608, "Living Luck's Shoulderguards", "SHOULDER", 4, 4, transmog = 51229),
                gear("back", 235499, "Reshii Wraps", "CLOAK", 4, 1),
                gear("chest", 237613, "Living Luck's Battleplate", "CHEST", 4, 4),
                gear("shirt", 4336, "Black Swashbuckler's Shirt", "BODY", 4, 0, quality = "COMMON"),
                gear("tabard", 46874, "Argent Crusader's Tabard", "TABARD", 4, 0, quality = "RARE"),
                gear("wrist", 237534, "Cosmic Crusader's Vambraces", "WRIST", 4, 4),
                gear("hand", 237611, "Living Luck's Gauntlets", "HAND", 4, 4),
                gear("waist", 237541, "Durable Information Securing Container", "WAIST", 4, 4),
                gear("leg", 237609, "Living Luck's Legplates", "LEGS", 4, 4),
                gear("foot", 237535, "Interloper's Plated Sabatons", "FEET", 4, 4),
                gear("leftFinger", 242405, "Band of the Shattered Soul", "FINGER", 4, 0),
                gear("rightFinger", 237567, "Logic Gate: Alpha", "FINGER", 4, 0),
                gear("leftTrinket", 242401, "Brand of Ceaseless Ire", "TRINKET", 4, 0),
                gear("rightTrinket", 242396, "Unyielding Netherprism", "TRINKET", 4, 0),
                gear("weapon", 237728, "Voidglass Kris", "WEAPON", 2, 7, transmog = 19019),
                gear("offhand", 237723, "Bulwark of the Last Watch", "SHIELD", 4, 6, transmog = 40400),
            ),
            professions = listOf(
                PortProfession(164, "Blacksmithing", true, tiers("Classic Blacksmithing" to 300, "Outland Blacksmithing" to 75, "Northrend Blacksmithing" to 75, "Khaz Algar Blacksmithing" to 100)),
                PortProfession(186, "Mining", true, tiers("Classic Mining" to 300, "Outland Mining" to 75, "Northrend Mining" to 60)),
                PortProfession(794, "Archaeology", false, tiers("Archaeology" to 950)),
                PortProfession(185, "Cooking", false, tiers("Classic Cooking" to 285, "Dragon Isles Cooking" to 100)),
            ),
            mounts = listOf(PortMount(363, "Invincible"), PortMount(219, "Swift Spectral Tiger"), PortMount(1792, "Algarian Stormrider"), PortMount(6, "Brown Horse")),
            reputations = listOf(
                PortReputation("Stormwind", "Exalted", 999), PortReputation("Argent Crusade", "Exalted"), PortReputation("Knights of the Ebon Blade", "Revered", 12000),
                PortReputation("The Kalu'ak", "Honored", 4000), PortReputation("Gnomeregan", "Exalted"), PortReputation("Darkmoon Faire", "Exalted"),
                PortReputation("Council of Dornogal", "Renown 25"), PortReputation("Orgrimmar", "Hated"),
            ),
            completedQuests = listOf(PortQuest(783, "A Threat Within"), PortQuest(7, "Kobold Camp Cleanup"), PortQuest(33), PortQuest(86574, "The Weight of the World"), PortQuest(86575), PortQuest(60000)),
            achievements = VETERAN_ACHIEVEMENTS + PortAchievement(614) + PortAchievement(619),
            titleIds = listOf(131, 149, 72, 448),
            activeTitleId = 131,
            appearance = PortAppearance(skin = 4, face = 7, hairStyle = 9, hairColor = 3, facialHair = 4),
        ),
        PortOptions(Realm.CHROMIE, "porter", "Brannoc", race = 1, classId = 1, gender = 0, level = 80, money = 250_000_000L, gearTier = GearTier.BEST),
        "a level-cap plate tank (human Protection warrior), at the realm's 80, Best tier",
    )

    /** A caster in cloth: a blood elf Frost mage of the Horde, ported at 70 with early raid gear. */
    val caster = Fixture(
        PortCharacter(
            name = "Sylaria", raceId = 10, classId = 8, gender = 1, faction = PortFaction.HORDE, level = 90,
            spec = PortSpec("Frost", PortRole.DAMAGE, PortStat.INTELLECT),
            equipment = listOf(
                gear("head", 237718, "Augur's Ephemeral Wide-Brim", "HEAD", 4, 1, transmog = 16921),
                gear("neck", 237568, "Chrysalis of Sundered Souls", "NECK", 4, 0),
                gear("shoulder", 237716, "Augur's Ephemeral Orbs of Power", "SHOULDER", 4, 1),
                gear("back", 235499, "Reshii Wraps", "CLOAK", 4, 1),
                gear("chest", 237721, "Augur's Ephemeral Habiliments", "ROBE", 4, 1),
                gear("wrist", 237551, "Bindings of the Soul Prism", "WRIST", 4, 1),
                gear("hand", 237719, "Augur's Ephemeral Mitts", "HAND", 4, 1),
                gear("waist", 237552, "Sash of the Fractured Star", "WAIST", 4, 1),
                gear("leg", 237717, "Augur's Ephemeral Trousers", "LEGS", 4, 1),
                gear("foot", 237553, "Slippers of Fated Steps", "FEET", 4, 1),
                gear("leftFinger", 242405, "Band of the Shattered Soul", "FINGER", 4, 0),
                gear("rightFinger", 237567, "Logic Gate: Alpha", "FINGER", 4, 0),
                gear("leftTrinket", 242392, "Diamantine Voidcore", "TRINKET", 4, 0),
                gear("rightTrinket", 242402, "Araz's Ritual Forge", "TRINKET", 4, 0),
                gear("weapon", 237730, "Voidglass Spire", "TWOHWEAPON", 2, 10, transmog = 22589),
            ),
            professions = listOf(
                PortProfession(197, "Tailoring", true, tiers("Classic Tailoring" to 300, "Outland Tailoring" to 75, "Northrend Tailoring" to 75)),
                PortProfession(333, "Enchanting", true, tiers("Classic Enchanting" to 300, "Outland Enchanting" to 75)),
            ),
            mounts = listOf(PortMount(183, "Ashes of Al'ar"), PortMount(152, "Swift Red Wind Rider"), PortMount(2234, "Ruby Ripsaw")),
            reputations = listOf(PortReputation("Silvermoon City", "Exalted"), PortReputation("The Scryers", "Revered", 3000), PortReputation("Kirin Tor", "Exalted")),
            completedQuests = listOf(PortQuest(9676, "Paladin Training"), PortQuest(10068, "Well Watcher Solanian"), PortQuest(788), PortQuest(4641)),
            achievements = VETERAN_ACHIEVEMENTS + PortAchievement(619),
            appearance = PortAppearance(skin = 2, face = 3, hairStyle = 5, hairColor = 6, facialHair = 2),
        ),
        PortOptions(Realm.CHROMIE, "porter", "Sylaria", race = 10, classId = 8, gender = 1, level = 70, money = 12_000_000L, gearTier = GearTier.RAID),
        "a caster in cloth (blood elf Frost mage), at 70, Raid tier",
    )

    /** A hunter with a gun: a dwarf Marksmanship hunter, ported at 60 with fresh dungeon gear. */
    val hunter = Fixture(
        PortCharacter(
            name = "Durgin", raceId = 3, classId = 3, gender = 0, faction = PortFaction.ALLIANCE, level = 90,
            spec = PortSpec("Marksmanship", PortRole.DAMAGE, PortStat.AGILITY),
            equipment = listOf(
                gear("head", 237646, "Midnight Herald's Cowl", "HEAD", 4, 3),
                gear("neck", 237568, "Chrysalis of Sundered Souls", "NECK", 4, 0),
                gear("shoulder", 237644, "Midnight Herald's Pauldrons", "SHOULDER", 4, 3),
                gear("back", 235499, "Reshii Wraps", "CLOAK", 4, 1),
                gear("chest", 237649, "Midnight Herald's Hauberk", "CHEST", 4, 3),
                gear("wrist", 237560, "Swiftstrider's Bracers", "WRIST", 4, 3),
                gear("hand", 237647, "Midnight Herald's Gloves", "HAND", 4, 3),
                gear("waist", 237561, "Clasp of the Hunt", "WAIST", 4, 3),
                gear("leg", 237645, "Midnight Herald's Petticoat", "LEGS", 4, 3),
                gear("foot", 237562, "Treads of the Trail", "FEET", 4, 3),
                gear("leftFinger", 242405, "Band of the Shattered Soul", "FINGER", 4, 0),
                gear("rightFinger", 237567, "Logic Gate: Alpha", "FINGER", 4, 0),
                gear("leftTrinket", 242395, "Astral Antenna", "TRINKET", 4, 0),
                gear("rightTrinket", 242403, "Perfidious Projector", "TRINKET", 4, 0),
                gear("weapon", 237735, "Voidglass Hand Cannon", "RANGEDRIGHT", 2, 3, transmog = 2099),
            ),
            professions = listOf(
                PortProfession(202, "Engineering", true, tiers("Classic Engineering" to 300, "Outland Engineering" to 50)),
                PortProfession(165, "Leatherworking", true, tiers("Classic Leatherworking" to 225)),
            ),
            mounts = listOf(PortMount(1, "Black War Ram"), PortMount(2, "Swift Brown Ram")),
            reputations = listOf(PortReputation("Ironforge", "Exalted"), PortReputation("Timbermaw Hold", "Friendly", 2000)),
            completedQuests = listOf(PortQuest(6), PortQuest(33)),
            achievements = listOf(PortAchievement(6), PortAchievement(7), PortAchievement(42)),
            appearance = PortAppearance(skin = 1, face = 2, hairStyle = 4, hairColor = 2, facialHair = 5),
        ),
        PortOptions(Realm.CHROMIE, "porter", "Durgin", race = 3, classId = 3, gender = 0, level = 60, money = 3_000_000L, gearTier = GearTier.FRESH),
        "a hunter with a gun (dwarf Marksmanship), at 60, Fresh tier",
    )

    /** A low-level character: a tauren Feral druid of retail level 20, scaled to the realm's cap. */
    val lowLevel = Fixture(
        PortCharacter(
            name = "Hooveth", raceId = 6, classId = 11, gender = 1, faction = PortFaction.HORDE, level = 20,
            spec = PortSpec("Feral", PortRole.DAMAGE, PortStat.AGILITY),
            equipment = listOf(
                gear("shoulder", 42984, "Preened Ironfeather Shoulders", "SHOULDER", 4, 2, ilvl = 1, quality = "HEIRLOOM"),
                gear("chest", 210041, "Mulgore Plainsrunner's Vest", "CHEST", 4, 2, ilvl = 15, quality = "UNCOMMON"),
                gear("leg", 210043, "Mulgore Plainsrunner's Leggings", "LEGS", 4, 2, ilvl = 15, quality = "UNCOMMON"),
                gear("foot", 210044, "Bramble-Tread Boots", "FEET", 4, 2, ilvl = 14, quality = "COMMON"),
                gear("weapon", 210050, "Gnarled Plains Staff", "TWOHWEAPON", 2, 10, ilvl = 15, quality = "UNCOMMON"),
            ),
            professions = listOf(
                PortProfession(182, "Herbalism", true, tiers("Classic Herbalism" to 40)),
                PortProfession(185, "Cooking", false, tiers("Classic Cooking" to 60)),
            ),
            reputations = listOf(PortReputation("Thunder Bluff", "Friendly", 500)),
            appearance = PortAppearance(skin = 3, face = 1, hairStyle = 2, hairColor = 1, facialHair = 1),
        ),
        PortOptions(Realm.CHROMIE, "porter", "Hooveth", race = 6, classId = 11, gender = 1, level = null, money = 2_500L),
        "a low-level character (tauren druid, retail 20), scaled to the realm's cap",
    )

    /** A retail race and class to map: a void elf Havoc demon hunter, which the realm has as a void elf and must make a rogue. */
    val mapped = Fixture(
        PortCharacter(
            name = "Xal'veth", raceId = 29, classId = 12, gender = 1, faction = PortFaction.ALLIANCE, level = 90,
            spec = PortSpec("Havoc", PortRole.DAMAGE, PortStat.AGILITY),
            equipment = listOf(
                gear("head", 237691, "Charhound's Vicious Scalp", "HEAD", 4, 2),
                gear("shoulder", 237689, "Charhound's Vicious Hornguards", "SHOULDER", 4, 2),
                gear("chest", 237694, "Charhound's Vicious Bindings", "CHEST", 4, 2),
                gear("hand", 237692, "Charhound's Vicious Felclaws", "HAND", 4, 2),
                gear("leg", 237690, "Charhound's Vicious Hidecoat", "LEGS", 4, 2),
                gear("leftFinger", 242405, "Band of the Shattered Soul", "FINGER", 4, 0),
                gear("rightFinger", 242405, "Band of the Shattered Soul", "FINGER", 4, 0),
                gear("weapon", 237737, "Voidglass Warglaive", "WEAPONMAINHAND", 2, 9, transmog = 32837),
                gear("offhand", 237738, "Voidglass Warglaive", "WEAPONOFFHAND", 2, 9, transmog = 32838),
            ),
            professions = listOf(
                PortProfession(171, "Alchemy", true, tiers("Classic Alchemy" to 120)),
                PortProfession(182, "Herbalism", true, tiers("Classic Herbalism" to 150)),
            ),
            mounts = listOf(PortMount(1440, "Swift Zhevra"), PortMount(868, "Slayer's Felbroken Shrieker")),
            reputations = listOf(PortReputation("Exodar", "Exalted"), PortReputation("Darnassus", "Revered", 5000)),
            appearance = PortAppearance(skin = 12, face = 40, hairStyle = 9, hairColor = 14, facialHair = 3),
        ),
        PortOptions(Realm.CHROMIE, "porter", "Xalveth", race = 15, classId = 4, gender = 1, level = null, money = 900_000L),
        "a race and class to map (void elf demon hunter), as a void elf rogue at the realm's cap",
    )

    /** A death knight of a realm module's race: a nightborne Blood death knight at 80 with early raid gear. */
    val deathKnight = Fixture(
        PortCharacter(
            name = "Morthenar", raceId = 27, classId = 6, gender = 0, faction = PortFaction.HORDE, level = 90,
            spec = PortSpec("Blood", PortRole.TANK, PortStat.STRENGTH),
            equipment = listOf(
                gear("head", 237628, "Hollow Sentinel's Stonemask", "HEAD", 4, 4),
                gear("shoulder", 237626, "Hollow Sentinel's Perches", "SHOULDER", 4, 4, transmog = 51125),
                gear("chest", 237631, "Hollow Sentinel's Breastplate", "CHEST", 4, 4),
                gear("hand", 237629, "Hollow Sentinel's Gauntlets", "HAND", 4, 4),
                gear("leg", 237627, "Hollow Sentinel's Chausses", "LEGS", 4, 4),
                gear("foot", 237535, "Interloper's Plated Sabatons", "FEET", 4, 4),
                gear("weapon", 237729, "Voidglass Executioner", "TWOHWEAPON", 2, 8, transmog = 50730),
                gear("tabard", 43154, "Tabard of the Argent Crusade", "TABARD", 4, 0, quality = "COMMON"),
            ),
            professions = listOf(
                PortProfession(773, "Inscription", true, tiers("Classic Inscription" to 300, "Outland Inscription" to 75, "Northrend Inscription" to 75)),
                PortProfession(356, "Fishing", false, tiers("Classic Fishing" to 300, "Northrend Fishing" to 40)),
            ),
            mounts = listOf(PortMount(221, "Acherus Deathcharger"), PortMount(236, "Winged Steed of the Ebon Blade"), PortMount(363, "Invincible")),
            reputations = listOf(PortReputation("Knights of the Ebon Blade", "Exalted"), PortReputation("Undercity", "Honored", 100)),
            completedQuests = listOf(PortQuest(12593, "In Service Of The Lich King"), PortQuest(13092)),
            achievements = VETERAN_ACHIEVEMENTS,
            titleIds = listOf(92),
            activeTitleId = 92,
        ),
        PortOptions(Realm.CHROMIE, "porter", "Morthenar", race = 16, classId = 6, gender = 0, level = 80, money = 50_000_000L, gearTier = GearTier.RAID),
        "a death knight of a module race (nightborne Blood DK), at 80, Raid tier",
    )

    val all = listOf(tank, caster, hunter, lowLevel, mapped, deathKnight)
}
