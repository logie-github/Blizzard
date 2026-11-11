package com.logie.blizz.porter.port

import com.logie.blizz.wow.Realm
import java.io.File

/**
 * A realm the porter can write to: the three databases of an AzerothCore realm as the app's `ctl.sh` names them, and
 * where its configs are. Only the Wrath realms are such; OctoWoW (a 1.12 core) and Legion keep characters in other
 * tables, and [of] returns null for them.
 */
data class PortRealm(val realm: Realm, val authDb: String, val worldDb: String, val charactersDb: String, val etcFolder: String) {
    companion object {
        fun of(realm: Realm): PortRealm? = when (realm) {
            Realm.CHROMIE -> PortRealm(realm, "acore_auth", "acore_world", "acore_characters", "etc")
            Realm.REMIX -> PortRealm(realm, "acore_auth", "acore_world_remix", "acore_characters_remix", "etc-remix")
            Realm.WRATHPP -> PortRealm(realm, "acore_auth", "acore_world_wrathpp", "acore_characters_wrathpp", "etc-wrathpp")
            else -> null
        }
    }
}

/**
 * The realm's files the porter reads (never writes): its world server's config, its modules' configs, and the data
 * folder that config names. [root] is the realm's files folder (the app's `WowLayout.root`: it holds `etc`, `data`, ...).
 */
class RealmFiles(val root: File, val realm: PortRealm) {
    val etc = File(root, realm.etcFolder)
    val worldConf = File(etc, "worldserver.conf")

    private val world: Map<String, String> by lazy { ConfFile.read(worldConf) }

    fun worldSetting(key: String): String? = world[key]

    fun moduleSetting(file: String, key: String): String? = ConfFile.read(File(etc, "modules/$file"))[key]

    /**
     * The folder of client data files the world server reads: `dbc` under its DataDir. That is `data` as a rule, and
     * `data-modules` when the realm's modules bring files of their own (ctl.sh's module_data points DataDir there).
     */
    fun dbcDir(): File {
        val dataDir = worldSetting("DataDir")?.takeIf { it.isNotBlank() }?.let { File(it).let { f -> if (f.isAbsolute) f else File(root, it) } }
        return File(dataDir?.takeIf { it.isDirectory } ?: File(root, "data"), "dbc")
    }

    /** The realm's level caps, from its configs ([LevelCap]). */
    fun levelCap(): LevelCap {
        val max = worldSetting("MaxPlayerLevel")?.toIntOrNull()?.coerceIn(1, 255) ?: 80
        val stable = moduleSetting("chromie-xp.conf", "Chromie.Stable.MaxPlayerLevel")?.toIntOrNull()?.takeIf { it in 1..255 }
        val heroic = worldSetting("StartHeroicPlayerLevel")?.toIntOrNull()?.coerceIn(1, max) ?: 55
        return LevelCap(max, stable, heroic)
    }

    /** How many characters an account may have on the realm (the game's own list holds ten). */
    fun charactersPerRealm(): Int = (worldSetting("CharactersPerRealm")?.toIntOrNull() ?: 10).coerceIn(1, 10)

    fun minNameLength(): Int = (worldSetting("MinPlayerName")?.toIntOrNull() ?: 2).coerceIn(1, 12)

    /** Whether the realm keeps to names of one alphabet only (StrictPlayerNames; 0 lets any of the game's three). */
    fun strictNames(): Int = worldSetting("StrictPlayerNames")?.toIntOrNull() ?: 0

    /** Whether Wrath Remix's module runs on this realm (its own switch, which ctl.sh sets for the Remix realm alone). */
    fun wrathRemixOn(): Boolean = moduleSetting("mod_wrath_remix.conf", "WrathRemix.Enable") == "1"
}

/**
 * The realm's level caps. [max] is the world server's MaxPlayerLevel: nobody can be higher. [progression] is
 * ChromieCraft's own cap (mod-chromie-xp's Chromie.Stable.MaxPlayerLevel, 19 as the realm starts): experience stops
 * there until the realm's owner opens the next bracket, so that is where a level-cap character belongs by default.
 * A person who has opened more, or wants a character ahead of the realm, may still choose up to [max].
 */
data class LevelCap(val max: Int, val progression: Int?, val heroicStart: Int = 55) {
    /** The cap a retail level is scaled to. */
    val effective: Int get() = minOf(max, progression ?: max)
}

/** `Key = value` lines of one of the realm's config files (comments and section names left out, quotes taken off). */
object ConfFile {
    fun read(file: File): Map<String, String> {
        if (!file.isFile) return emptyMap()
        val out = HashMap<String, String>()
        for (raw in file.readLines()) {
            val line = raw.trim()
            if (line.isEmpty() || line.startsWith("#") || line.startsWith("[")) continue
            val at = line.indexOf('=')
            if (at <= 0) continue
            out[line.substring(0, at).trim()] = line.substring(at + 1).trim().removeSurrounding("\"")
        }
        return out
    }
}

/** Whether a realm can take a ported character, and if not, why, in words for the person. */
data class RealmSupport(val supported: Boolean, val reason: String? = null) {
    companion object {
        const val REMIX_REASON =
            "Wrath Remix makes its own characters: everyone there is a Timerunner who begins the realm's story at level 10 at the " +
                "Infinite Bazaar, in the gear and with the abilities the realm hands out, and is sent home to ChromieCraft when the story " +
                "ends. A ported character would arrive outside that story (the realm would pull it into its opening and its starter kit). " +
                "Port to ChromieCraft instead."
        const val NOT_WRATH_REASON = "The porter writes a Wrath (AzerothCore) realm's character tables; this realm keeps its characters differently."
    }
}

/** The name rules of the realm (ObjectMgr::CheckPlayerName and normalizePlayerName), as far as the name's own letters go. */
object PortNames {
    const val MAX_LENGTH = 12

    /** The name as the realm stores it: the first letter a capital, the rest small. */
    fun normalize(name: String): String {
        val trimmed = name.trim()
        if (trimmed.isEmpty()) return trimmed
        return trimmed.substring(0, 1).uppercase() + trimmed.substring(1).lowercase()
    }

    /**
     * What is wrong with [name] as a character's name, or null: its length, letters of one of the game's alphabets only
     * (with [strict] 0, as the realm is set: Latin with its accents, or Cyrillic, or East Asian; never mixed), no
     * letter three times in a row, and not ending in "gm" (the core keeps those for game masters).
     */
    fun problem(name: String, minLength: Int = 2, strict: Int = 0): String? {
        if (name.length < minLength) return "The name is too short (at least $minLength letters)."
        if (name.length > MAX_LENGTH) return "The name is too long (at most $MAX_LENGTH letters)."
        val latin = name.all(::isExtendedLatin)
        val basic = name.all { it in 'a'..'z' || it in 'A'..'Z' }
        val ok = when {
            strict == 0 -> latin || name.all(::isCyrillic) || name.all(::isEastAsian)
            strict and 0x1 != 0 && basic -> true
            // (a realm set to its zone's alphabet: Latin for the zones the app's realms are in)
            strict and 0x2 != 0 -> latin
            else -> false
        }
        if (!ok) return "A name is letters only, all of one alphabet."
        val lower = name.lowercase()
        for (i in 2 until lower.length) if (lower[i] == lower[i - 1] && lower[i] == lower[i - 2]) return "A name can't have the same letter three times in a row."
        if (lower.endsWith("gm")) return "Names ending in \"gm\" are kept for game masters."
        return null
    }

    private fun isExtendedLatin(c: Char): Boolean {
        val code = c.code
        return c in 'a'..'z' || c in 'A'..'Z' || code in 0x00C0..0x00D6 || code in 0x00D8..0x00DE || code == 0x00DF ||
            code in 0x00E0..0x00F6 || code in 0x00F8..0x00FE || code in 0x0100..0x012F || code == 0x1E9E
    }

    private fun isCyrillic(c: Char): Boolean = c.code in 0x0410..0x044F || c.code == 0x0401 || c.code == 0x0451

    private fun isEastAsian(c: Char): Boolean {
        val code = c.code
        return code in 0x1100..0x11F9 || code in 0x3041..0x30FF || code in 0x3131..0x318E || code in 0x31F0..0x31FF ||
            code in 0x3400..0x4DB5 || code in 0x4E00..0x9FC3 || code in 0xAC00..0xD7A3 || code in 0xFF01..0xFFEE
    }
}

/** A race and class of the realm that a character can be made as. */
data class RaceClass(val race: Int, val classId: Int)

/** What the porter proposes a retail character becomes on the realm. */
data class TargetSuggestion(
    val race: Int,
    val classId: Int,
    val gender: Int,
    /** True when the proposal changes what the character is (another class, a race that isn't its kin, the other side): the person should choose. */
    val needsChoice: Boolean,
    /** Why, in words for the person. */
    val notes: List<String>,
)

/** Retail's races and classes, and what each becomes on a Wrath realm. */
object PortTargets {
    const val WARRIOR = 1
    const val PALADIN = 2
    const val HUNTER = 3
    const val ROGUE = 4
    const val PRIEST = 5
    const val DEATH_KNIGHT = 6
    const val SHAMAN = 7
    const val MAGE = 8
    const val WARLOCK = 9
    const val MONK = 10
    const val DRUID = 11
    const val DEMON_HUNTER = 12
    const val EVOKER = 13

    /** Wrath's own classes. */
    val WRATH_CLASSES = setOf(WARRIOR, PALADIN, HUNTER, ROGUE, PRIEST, DEATH_KNIGHT, SHAMAN, MAGE, WARLOCK, DRUID)

    private val RETAIL_RACE_NAMES = mapOf(
        1 to "Human", 2 to "Orc", 3 to "Dwarf", 4 to "Night Elf", 5 to "Undead", 6 to "Tauren", 7 to "Gnome", 8 to "Troll", 9 to "Goblin",
        10 to "Blood Elf", 11 to "Draenei", 22 to "Worgen", 24 to "Pandaren", 25 to "Pandaren", 26 to "Pandaren", 27 to "Nightborne",
        28 to "Highmountain Tauren", 29 to "Void Elf", 30 to "Lightforged Draenei", 31 to "Zandalari Troll", 32 to "Kul Tiran",
        34 to "Dark Iron Dwarf", 35 to "Vulpera", 36 to "Mag'har Orc", 37 to "Mechagnome", 52 to "Dracthyr", 70 to "Dracthyr",
        84 to "Earthen", 85 to "Earthen", 86 to "Haranir", 91 to "Haranir",
    )
    private val RETAIL_CLASS_NAMES = mapOf(
        1 to "Warrior", 2 to "Paladin", 3 to "Hunter", 4 to "Rogue", 5 to "Priest", 6 to "Death Knight", 7 to "Shaman", 8 to "Mage",
        9 to "Warlock", 10 to "Monk", 11 to "Druid", 12 to "Demon Hunter", 13 to "Evoker",
    )

    fun retailRaceName(race: Int): String = RETAIL_RACE_NAMES[race] ?: "race $race"
    fun retailClassName(classId: Int): String = RETAIL_CLASS_NAMES[classId] ?: "class $classId"

    /**
     * The realm races a retail race may become, best first: the realm's own race of that name where its modules add
     * one (the allied races as 15 to 18, the Worgen 12, the Goblins 9), then its kin among Wrath's ten.
     */
    fun raceCandidates(retailRace: Int): List<Int> = when (retailRace) {
        in 1..8, 10, 11 -> listOf(retailRace)
        9 -> listOf(9, 2)                 // Goblin: the realm's, else an Orc (the Horde they joined)
        22 -> listOf(12, 1)               // Worgen: the realm's, else a Human (Gilneans)
        27 -> listOf(16, 10)              // Nightborne: the realm's, else a Blood Elf (an elf of the Horde)
        28 -> listOf(6)                   // Highmountain Tauren
        29 -> listOf(15, 4)               // Void Elf: the realm's, else a Night Elf (an elf of the Alliance)
        30 -> listOf(17, 11)              // Lightforged Draenei
        31 -> listOf(18, 8)               // Zandalari Troll
        32 -> listOf(1)                   // Kul Tiran
        34 -> listOf(3)                   // Dark Iron Dwarf
        36 -> listOf(2)                   // Mag'har Orc
        37 -> listOf(7)                   // Mechagnome
        84, 85 -> listOf(3)               // Earthen
        35 -> listOf(9)                   // Vulpera: with the Goblins, if the realm has them
        else -> emptyList()               // Pandaren, Dracthyr, Haranir and what comes after: no kin in Wrath
    }

    /** The Wrath classes a class Wrath hasn't may become, best first, by what the character does in a group. */
    private fun classStandIns(retailClass: Int, role: PortRole?): List<Int> = when (retailClass) {
        MONK -> when (role) {
            PortRole.TANK -> listOf(DRUID, WARRIOR, PALADIN)
            PortRole.HEALER -> listOf(DRUID, PRIEST, SHAMAN, PALADIN)
            else -> listOf(ROGUE, DRUID, WARRIOR)
        }
        DEMON_HUNTER -> when (role) {
            PortRole.TANK -> listOf(DRUID, WARRIOR, PALADIN)
            else -> listOf(ROGUE, WARRIOR, HUNTER)
        }
        EVOKER -> when (role) {
            PortRole.HEALER -> listOf(SHAMAN, DRUID, PRIEST, PALADIN)
            else -> listOf(SHAMAN, MAGE, WARLOCK)
        }
        DEATH_KNIGHT -> listOf(WARRIOR, PALADIN)
        else -> emptyList()
    }

    /**
     * What a retail character becomes on a realm whose race and class pairs are [combos] ([Porter.raceClassCombos]),
     * with [factionOf] telling each realm race's side and [level] the level it will have there (a death knight can't
     * be under [heroicStart]). Its own race and class when the realm has the pair; else the nearest the realm has,
     * marked for the person to confirm.
     */
    fun suggest(
        character: PortCharacter,
        combos: Collection<RaceClass>,
        factionOf: (Int) -> PortFaction,
        level: Int,
        heroicStart: Int = 55,
    ): TargetSuggestion? {
        if (combos.isEmpty()) return null
        val notes = ArrayList<String>()
        var needsChoice = false
        val has = combos.toSet()
        val realmRaces = combos.map { it.race }.toSet()
        fun usable(race: Int, classId: Int) = RaceClass(race, classId) in has && (classId != DEATH_KNIGHT || level >= heroicStart)

        // The race: its own or its kin, on its own side if there is a choice.
        val kin = raceCandidates(character.raceId).filter { it in realmRaces }
        val sameSide = realmRaces.filter { character.faction == PortFaction.NEUTRAL || factionOf(it) == character.faction }.sorted()
        val races = (kin + sameSide.filter { it <= 11 } + sameSide + realmRaces.sorted()).distinct()
        if (kin.isEmpty()) {
            notes.add("${retailRaceName(character.raceId)} has no counterpart on this realm.")
            needsChoice = true
        } else if (kin.first() != character.raceId && kin.first() <= 11) {
            notes.add("${retailRaceName(character.raceId)} isn't a race of this realm: its kin is proposed.")
        }

        // The class: its own where Wrath has it, else a stand-in by its role.
        val ownClass = character.classId.takeIf { it in WRATH_CLASSES }
        val classes = ArrayList<Int>()
        if (ownClass != null && (ownClass != DEATH_KNIGHT || level >= heroicStart)) classes.add(ownClass)
        if (ownClass == null) {
            notes.add("${retailClassName(character.classId)} isn't a class of Wrath: choose what it becomes.")
            needsChoice = true
        } else if (classes.isEmpty()) {
            notes.add("A death knight starts at level $heroicStart on this realm, and this character would be level $level: choose another class, or a higher level.")
            needsChoice = true
        }
        classes.addAll(classStandIns(character.classId, character.spec?.role))

        // Its own class on the nearest race first (the class is how the character plays); then the stand-ins.
        for (classId in classes) {
            for ((index, race) in races.withIndex()) {
                if (!usable(race, classId)) continue
                if (index > 0) {
                    if (kin.isNotEmpty()) notes.add("${retailRaceName(character.raceId)} can't be a ${retailClassName(classId).lowercase()} on this realm as its own race: another race is proposed.")
                    needsChoice = true
                }
                if (character.faction != PortFaction.NEUTRAL && factionOf(race) != character.faction) {
                    notes.add("The proposed race is on the other side.")
                    needsChoice = true
                }
                return TargetSuggestion(race, classId, character.gender.coerceIn(0, 1), needsChoice, notes)
            }
        }
        // Nothing of its own fits: anything its nearest race can be.
        for (race in races) {
            val any = combos.filter { it.race == race && usable(race, it.classId) }.minByOrNull { it.classId } ?: continue
            notes.add("None of its classes exist for that race here: choose one.")
            return TargetSuggestion(any.race, any.classId, character.gender.coerceIn(0, 1), true, notes)
        }
        return null
    }
}
