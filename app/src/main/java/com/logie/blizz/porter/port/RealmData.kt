package com.logie.blizz.porter.port

import java.io.File
import java.io.IOException

/** A spell's row of a skill (SkillLineAbility): which races and classes have it, and how it comes with the skill. */
data class SkillAbility(val skill: Int, val spell: Int, val raceMask: Int, val classMask: Int, val minRank: Int, val supercededBy: Int, val acquire: Int, val trivialHigh: Int)

/** A skill as one race and class has it (SkillRaceClassInfo). */
data class SkillInfo(val skill: Int, val raceMask: Int, val classMask: Int, val flags: Int, val minLevel: Int, val tier: Int)

/** How the core keeps a skill's value (ObjectMgr's GetSkillRangeType). */
enum class SkillRange { LANGUAGE, LEVEL, MONO, RANK, NONE }

/**
 * The realm's client data the porter needs, as its world server has it: the files of `data/dbc` with the world
 * database's `*_dbc` rows over them ([DbcTable]). Read once for a plan; nothing here writes.
 *
 * The functions mirror the core's own rules (named in each), so that what the porter writes is what the world server
 * accepts when it loads the character.
 */
class RealmData private constructor(private val tables: Map<String, DbcTable>, private val facialHair: List<IntArray>, reserved: Set<String>, profane: Set<String>) {
    val spells = tables.getValue("Spell")
    val factions = tables.getValue("Faction")
    val achievements = tables.getValue("Achievement")
    val titles = tables.getValue("CharTitles")
    val races = tables.getValue("ChrRaces")
    val classes = tables.getValue("ChrClasses")
    val taxiNodes = tables.getValue("TaxiNodes")
    val areas = tables.getValue("AreaTable")
    val worldMapAreas = tables.getValue("WorldMapArea")
    val charSections = tables.getValue("CharSections")
    val taxiPaths = tables.getValue("TaxiPath")
    private val skillLines = tables.getValue("SkillLine")
    private val skillTiers = tables.getValue("SkillTiers")

    /** Names no character may have (NamesReserved.dbc as the core cleans it, lower case) and words none may be (NamesProfanity.dbc). */
    val reservedNames: Set<String> = reserved
    val profaneNames: Set<String> = profane

    val abilities: List<SkillAbility> = tables.getValue("SkillLineAbility").rows().map {
        SkillAbility(it.int(1), it.int(2), it.int(3), it.int(4), it.int(7), it.int(8), it.int(9), it.int(10))
    }.toList()
    private val abilitiesBySpell: Map<Int, List<SkillAbility>> = abilities.groupBy { it.spell }
    private val abilitiesBySkill: Map<Int, List<SkillAbility>> = abilities.groupBy { it.skill }

    private val skillInfos: Map<Int, List<SkillInfo>> = tables.getValue("SkillRaceClassInfo").rows().map {
        SkillInfo(it.int(1), it.int(2), it.int(3), it.int(4), it.int(5), it.int(6))
    }.toList().groupBy { it.skill }

    // ---- races and classes

    fun raceName(race: Int): String = races[race]?.string(RACE_NAME).orEmpty().ifEmpty { "race $race" }

    fun className(classId: Int): String = classes[classId]?.string(CLASS_NAME).orEmpty().ifEmpty { "class $classId" }

    /** The side a race is on, as the core reads it (Player::TeamIdForRace: ChrRaces' team field, 7 Alliance, 1 Horde). */
    fun faction(race: Int): PortFaction = when (races[race]?.int(RACE_TEAM)) {
        7 -> PortFaction.ALLIANCE
        1 -> PortFaction.HORDE
        else -> PortFaction.NEUTRAL
    }

    // ---- spells

    fun spellExists(spell: Int): Boolean = spell > 0 && spells[spell] != null

    fun spellName(spell: Int): String {
        val row = spells[spell] ?: return "spell $spell"
        val rank = row.string(SPELL_RANK)
        return row.string(SPELL_NAME) + if (rank.isEmpty()) "" else " ($rank)"
    }

    /** The spell's three effects: effect, aura, misc value, the spell it triggers or teaches, base points. */
    fun effects(spell: Int): List<SpellEffect> {
        val row = spells[spell] ?: return emptyList()
        return (0..2).map { SpellEffect(row.int(SPELL_EFFECT + it), row.int(SPELL_AURA + it), row.int(SPELL_MISC + it), row.int(SPELL_TRIGGER + it), row.int(SPELL_BASE + it), row.int(SPELL_ITEM + it)) }
            .filter { it.effect != 0 }
    }

    /** What a character knows after a trainer "teaches" [spell]: the spells it teaches when it is a lesson (Trainer::Spell::IsCastable), else itself. */
    fun taught(spell: Int): List<Int> {
        val lessons = effects(spell).filter { it.effect == EFFECT_LEARN_SPELL && it.trigger > 0 }.map { it.trigger }
        return lessons.ifEmpty { listOf(spell) }
    }

    fun isLesson(spell: Int): Boolean = effects(spell).any { it.effect == EFFECT_LEARN_SPELL }

    fun isMount(spell: Int): Boolean = effects(spell).any { it.effect == EFFECT_APPLY_AURA && it.aura == AURA_MOUNTED }

    /**
     * A mount that flies: one with a flying speed of its own, one marked as flying (its AttributesEx4's 0x04000000, the
     * scaling ones' too), or a scaling mount ([isScalingMount]).
     */
    fun isFlyingMount(spell: Int): Boolean {
        if (!isMount(spell)) return false
        if (effects(spell).any { it.effect == EFFECT_APPLY_AURA && it.aura == AURA_FLIGHT_SPEED }) return true
        if ((spells[spell]?.int(SPELL_ATTRIBUTES_EX4) ?: 0) and ATTR4_FLYING_MOUNT != 0) return true
        return isScalingMount(spell)
    }

    /**
     * A mount that can be ridden on the ground everywhere: one with a ground speed of its own that isn't kept to flying
     * areas (3.3.5a's flying mounts are, by that AttributesEx4 mark: none can be used in Azeroth), or a scaling one.
     */
    fun isGroundMount(spell: Int): Boolean {
        if (!isMount(spell)) return false
        if (isScalingMount(spell)) return true
        val flyingOnly = (spells[spell]?.int(SPELL_ATTRIBUTES_EX4) ?: 0) and ATTR4_FLYING_MOUNT != 0
        return !flyingOnly && effects(spell).any { it.effect == EFFECT_APPLY_AURA && it.aura == AURA_MOUNTED_SPEED }
    }

    /** A mount whose speed a script picks by the rider's riding (Invincible, the Celestial Steed): no speed of its own, a script effect. */
    fun isScalingMount(spell: Int): Boolean {
        val effects = effects(spell)
        return isMount(spell) && effects.any { it.effect == EFFECT_SCRIPT } &&
            effects.none { it.effect == EFFECT_APPLY_AURA && (it.aura == AURA_MOUNTED_SPEED || it.aura == AURA_FLIGHT_SPEED) }
    }

    /**
     * What an item's equip spell gives, as the item stats it stands for (ItemModType numbers): the old items' spell
     * power, attack power, mana regeneration, block value and ratings are such spells, not stats, in 3.3.5a's data.
     * Percentages (the oldest items' "+1% hit") are given as about the rating they were turned into.
     */
    fun equipStats(spell: Int): List<Pair<Int, Int>> {
        val out = ArrayList<Pair<Int, Int>>()
        for (e in effects(spell)) {
            if (e.effect != EFFECT_APPLY_AURA) continue
            val value = e.base + 1
            when (e.aura) {
                13 -> if (e.misc and 0x7E != 0) out.add(45 to value)
                135 -> out.add(41 to value)
                99 -> out.add(38 to value)
                124 -> out.add(39 to value)
                85 -> if (e.misc == 0) out.add(43 to value)
                158 -> out.add(48 to value)
                123 -> out.add(47 to value)
                54 -> out.add(31 to value * 10)
                55 -> out.add(18 to value * 8)
                52 -> out.add(32 to value * 14)
                57 -> out.add(21 to value * 14)
                49 -> out.add(13 to value * 12)
                47 -> out.add(14 to value * 15)
                51 -> out.add(15 to value * 5)
                30 -> if (e.misc == 95) out.add(12 to value * 2)
                189 -> out.addAll(ratingStats(e.misc, value))
            }
        }
        return out
    }

    /** SPELL_AURA_MOD_RATING's mask of combat ratings as item stats. */
    private fun ratingStats(mask: Int, value: Int): List<Pair<Int, Int>> {
        fun all(vararg bits: Int) = bits.all { mask and (1 shl it) != 0 }
        val out = ArrayList<Pair<Int, Int>>()
        if (all(5, 6, 7)) out.add(31 to value) else for ((bit, stat) in listOf(5 to 16, 6 to 17, 7 to 18)) if (all(bit)) out.add(stat to value)
        if (all(8, 9, 10)) out.add(32 to value) else for ((bit, stat) in listOf(8 to 19, 9 to 20, 10 to 21)) if (all(bit)) out.add(stat to value)
        if (all(17, 18, 19)) out.add(36 to value) else for ((bit, stat) in listOf(17 to 28, 18 to 29, 19 to 30)) if (all(bit)) out.add(stat to value)
        for ((bit, stat) in listOf(1 to 12, 2 to 13, 3 to 14, 4 to 15, 23 to 37, 24 to 44)) if (all(bit)) out.add(stat to value)
        if (all(14) || all(15) || all(16)) out.add(35 to value)
        return out
    }

    /** The skill a spell sets as it is learned, and the step (SpellMgr::LoadSpellLearnSkills: the SKILL effect). */
    fun skillStep(spell: Int): Pair<Int, Int>? =
        effects(spell).firstOrNull { it.effect == EFFECT_SKILL }?.let { it.misc to it.base + 1 }

    /** The items the spell makes (a recipe's). */
    fun createdItems(spell: Int): List<Int> = effects(spell).filter { it.effect == EFFECT_CREATE_ITEM && it.item > 0 }.map { it.item }

    fun abilitiesOf(spell: Int): List<SkillAbility> = abilitiesBySpell[spell].orEmpty()

    fun abilitiesIn(skill: Int): List<SkillAbility> = abilitiesBySkill[skill].orEmpty()

    /** Player::IsSpellFitByClassAndRace: a spell with no skill fits anyone; else one of its skills must be the race's and class's. */
    fun spellFits(spell: Int, race: Int, classId: Int): Boolean {
        val rows = abilitiesOf(spell)
        if (rows.isEmpty()) return true
        val raceBit = raceBit(race)
        val classBit = classBit(classId)
        return rows.any { (it.raceMask == 0 || it.raceMask and raceBit != 0) && (it.classMask == 0 || it.classMask and classBit != 0) && skillInfo(it.skill, race, classId) != null }
    }

    /** Player::CheckSkillLearnedBySpell: a saved spell of a skill none of which the race and class may have is deleted at login. */
    fun spellKeptAtLogin(spell: Int, race: Int, classId: Int): Boolean {
        val rows = abilitiesOf(spell).filter { skillLines[it.skill] != null }
        return rows.isEmpty() || rows.any { skillInfo(it.skill, race, classId) != null }
    }

    // ---- skills

    fun skillName(skill: Int): String = skillLines[skill]?.string(SKILL_NAME).orEmpty().ifEmpty { "skill $skill" }

    fun skillCategory(skill: Int): Int = skillLines[skill]?.int(SKILL_CATEGORY) ?: -1

    fun skillsOfCategory(category: Int): List<Int> = skillLines.rows().filter { it.int(SKILL_CATEGORY) == category }.map { it.id }.toList().sorted()

    /** DBCStores' GetSkillRaceClassInfo: the skill's row for this race and class, or null when they can't have it. */
    fun skillInfo(skill: Int, race: Int, classId: Int): SkillInfo? {
        val raceBit = raceBit(race)
        val classBit = classBit(classId)
        return skillInfos[skill]?.firstOrNull { (it.raceMask == 0 || it.raceMask and raceBit != 0) && (it.classMask == 0 || it.classMask and classBit != 0) }
    }

    /** The highest value of a rank-kept skill at [rank] (1-based: SkillTiers' Value[rank - 1]); 0 when there is no such rank. */
    fun tierValue(tier: Int, rank: Int): Int {
        if (rank < 1 || rank > 16) return 0
        return skillTiers[tier]?.int(TIER_VALUE + rank - 1) ?: 0
    }

    fun skillRange(info: SkillInfo): SkillRange {
        if (skillLines[info.skill] == null) return SkillRange.NONE
        if (skillTiers[info.tier] != null) return SkillRange.RANK
        if (info.skill == SKILL_RUNEFORGING) return SkillRange.MONO
        return when (skillCategory(info.skill)) {
            CATEGORY_ARMOR -> SkillRange.MONO
            CATEGORY_LANGUAGES -> SkillRange.LANGUAGE
            else -> SkillRange.LEVEL
        }
    }

    /**
     * The spells a character has by its skills alone, never saved (Player::learnSkillRewardedSpells): those a skill
     * gives when it is learned, and those it gives at a value the character has reached.
     */
    fun spellsOfSkills(skills: Map<Int, Int>, race: Int, classId: Int): Set<Int> {
        val raceBit = raceBit(race)
        val classBit = classBit(classId)
        val known = HashSet<Int>()
        for ((skill, value) in skills) {
            for (a in abilitiesIn(skill)) {
                if (a.acquire != ACQUIRE_ON_VALUE && a.acquire != ACQUIRE_ON_LEARN) continue
                if (a.raceMask != 0 && a.raceMask and raceBit == 0) continue
                if (a.classMask != 0 && a.classMask and classBit == 0) continue
                if (a.acquire == ACQUIRE_ON_VALUE && value < a.minRank) continue
                if (spellExists(a.spell)) known.add(a.spell)
            }
        }
        return known
    }

    // ---- looks

    /** The facial hair styles a race and gender has (CharacterFacialHairStyles). */
    fun facialHairStyles(race: Int, gender: Int): Set<Int> = facialHair.filter { it[0] == race && it[1] == gender }.map { it[2] }.toSet()

    /** A race and gender's rows of CharSections of one kind that a player may pick: (variation, colour) pairs. */
    fun looks(race: Int, gender: Int, kind: Int, deathKnight: Boolean): List<Pair<Int, Int>> = charSections.rows()
        .filter { it.int(SECTION_RACE) == race && it.int(SECTION_GENDER) == gender && it.int(SECTION_KIND) == kind }
        .filter { it.int(SECTION_FLAGS) and SECTION_PLAYER != 0 && (deathKnight || it.int(SECTION_FLAGS) and SECTION_DEATH_KNIGHT == 0) }
        .map { it.int(SECTION_VARIATION) to it.int(SECTION_COLOR) }.toList()

    companion object {
        const val EFFECT_APPLY_AURA = 6
        const val EFFECT_CREATE_ITEM = 24
        const val EFFECT_LEARN_SPELL = 36
        const val EFFECT_DUAL_WIELD = 40
        const val EFFECT_SKILL_STEP = 44
        const val EFFECT_TRADE_SKILL = 47
        const val EFFECT_SKILL = 118
        const val EFFECT_SCRIPT = 77
        private const val SPELL_ATTRIBUTES_EX4 = 8
        private const val ATTR4_FLYING_MOUNT = 0x04000000
        const val AURA_MOUNTED = 78
        const val AURA_FLIGHT_SPEED = 207
        const val AURA_MOUNTED_SPEED = 32
        const val ACQUIRE_ON_VALUE = 1
        const val ACQUIRE_ON_LEARN = 2
        const val CATEGORY_WEAPON = 6
        const val CATEGORY_CLASS = 7
        const val CATEGORY_ARMOR = 8
        const val CATEGORY_SECONDARY = 9
        const val CATEGORY_LANGUAGES = 10
        const val CATEGORY_PROFESSION = 11
        const val SKILL_RUNEFORGING = 776
        const val SKILL_FLAG_ALWAYS_MAX = 0x10

        // The fields read of each file (the core's DBCStructure.h).
        private const val SPELL_ATTRIBUTES = 4
        private const val SPELL_EFFECT = 71
        private const val SPELL_BASE = 80
        private const val SPELL_AURA = 95
        private const val SPELL_ITEM = 107
        private const val SPELL_MISC = 110
        private const val SPELL_TRIGGER = 116
        private const val SPELL_NAME = 136
        private const val SPELL_RANK = 153
        private const val SKILL_CATEGORY = 1
        private const val SKILL_NAME = 3
        const val FACTION_LIST = 1
        const val FACTION_RACE_MASK = 2
        const val FACTION_CLASS_MASK = 6
        const val FACTION_BASE = 10
        const val FACTION_FLAGS = 14
        const val FACTION_NAME = 23
        const val ACHIEVEMENT_FACTION = 1
        const val ACHIEVEMENT_NAME = 4
        const val ACHIEVEMENT_FLAGS = 41
        const val TITLE_NAME = 2
        const val TITLE_BIT = 36
        private const val RACE_TEAM = 7
        private const val RACE_NAME = 14
        private const val CLASS_NAME = 4
        const val TAXI_MAP = 1
        const val TAXI_X = 2
        const val TAXI_Y = 3
        const val TAXI_MOUNT_HORDE = 22
        const val TAXI_MOUNT_ALLIANCE = 23
        const val AREA_MAP = 1
        const val AREA_ZONE = 2
        const val AREA_EXPLORE_FLAG = 3
        const val AREA_LEVEL = 10
        const val AREA_NAME = 11
        const val MAP_AREA_MAP = 1
        const val MAP_AREA_AREA = 2
        const val MAP_AREA_Y1 = 4
        const val MAP_AREA_Y2 = 5
        const val MAP_AREA_X1 = 6
        const val MAP_AREA_X2 = 7
        const val MAP_AREA_VIRTUAL = 8
        private const val TIER_VALUE = 17
        const val EFFECT_SEND_TAXI = 123
        private const val SECTION_RACE = 1
        private const val SECTION_GENDER = 2
        private const val SECTION_KIND = 3
        private const val SECTION_FLAGS = 7
        private const val SECTION_VARIATION = 8
        private const val SECTION_COLOR = 9
        const val SECTION_SKIN = 0
        const val SECTION_FACE = 1
        const val SECTION_HAIR = 3
        private const val SECTION_PLAYER = 0x1
        private const val SECTION_DEATH_KNIGHT = 0x4

        fun raceBit(race: Int): Int = if (race in 1..32) 1 shl (race - 1) else 0
        fun classBit(classId: Int): Int = if (classId in 1..32) 1 shl (classId - 1) else 0

        /** A table to read: the file, the fields of it the porter uses, and which field is its id. */
        private class Source(val key: String, val fields: List<Int>, val idField: Int = 0) {
            val file = "$key.dbc"
            val sqlTable = key.lowercase() + "_dbc"
        }

        private val SOURCES = listOf(
            Source("Spell", listOf(0, SPELL_ATTRIBUTES, SPELL_ATTRIBUTES_EX4) + (0..2).flatMap { listOf(SPELL_EFFECT + it, SPELL_BASE + it, SPELL_AURA + it, SPELL_ITEM + it, SPELL_MISC + it, SPELL_TRIGGER + it) } + listOf(SPELL_NAME, SPELL_RANK)),
            Source("SkillLineAbility", listOf(0, 1, 2, 3, 4, 7, 8, 9, 10)),
            Source("SkillRaceClassInfo", listOf(0, 1, 2, 3, 4, 5, 6)),
            Source("SkillLine", listOf(0, SKILL_CATEGORY, SKILL_NAME)),
            Source("SkillTiers", listOf(0) + (TIER_VALUE until TIER_VALUE + 16)),
            Source("Faction", listOf(0, FACTION_LIST) + (2..18) + listOf(FACTION_NAME)),
            Source("Achievement", listOf(0, ACHIEVEMENT_FACTION, ACHIEVEMENT_NAME, ACHIEVEMENT_FLAGS)),
            Source("CharTitles", listOf(0, TITLE_NAME, TITLE_BIT)),
            Source("ChrRaces", listOf(0, 1, RACE_TEAM, RACE_NAME)),
            Source("ChrClasses", listOf(0, CLASS_NAME)),
            Source("TaxiNodes", listOf(0, TAXI_MAP, TAXI_X, TAXI_Y, TAXI_MOUNT_HORDE, TAXI_MOUNT_ALLIANCE)),
            Source("AreaTable", listOf(0, AREA_MAP, AREA_ZONE, AREA_EXPLORE_FLAG, AREA_LEVEL, AREA_NAME)),
            Source("WorldMapArea", listOf(0, MAP_AREA_MAP, MAP_AREA_AREA, MAP_AREA_Y1, MAP_AREA_Y2, MAP_AREA_X1, MAP_AREA_X2, MAP_AREA_VIRTUAL)),
            Source("TaxiPath", listOf(0, 1, 2, 3)),
            Source("CharSections", listOf(0, SECTION_RACE, SECTION_GENDER, SECTION_KIND, SECTION_FLAGS, SECTION_VARIATION, SECTION_COLOR)),
        )

        /**
         * Reads the realm's data: the files in [dbcDir] (the `dbc` folder of the world server's DataDir) and the world
         * database's rows over them. Two round trips to the database: the `*_dbc` tables' columns, then their rows.
         * Throws IOException when a file the porter needs isn't there.
         */
        fun load(dbcDir: File, db: RealmDb, worldDb: String): RealmData {
            if (!dbcDir.isDirectory) throw IOException("The realm's data folder isn't there: ${dbcDir.path}")
            val files = SOURCES.associate { source ->
                val file = DbcFile.find(dbcDir, source.file) ?: throw IOException("The realm's data has no ${source.file} (${dbcDir.path})")
                source.key to DbcFile.open(file)
            }
            // The database's tables of the same data: their columns are the file's fields in order, so a field is
            // read by the column at its place.
            val extra = listOf("characterfacialhairstyles_dbc", "namesreserved_dbc", "namesprofanity_dbc")
            val names = (SOURCES.map { it.sqlTable } + extra).joinToString(",") { Sql.text(it) }
            val columns = HashMap<String, MutableMap<Int, String>>()
            for (row in db.query(worldDb, "SELECT TABLE_NAME, ORDINAL_POSITION, COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = ${Sql.text(worldDb)} AND TABLE_NAME IN ($names)")) {
                val table = row.getOrNull(0)?.lowercase() ?: continue
                val place = row.getOrNull(1)?.toIntOrNull() ?: continue
                columns.getOrPut(table) { HashMap() }[place - 1] = row.getOrNull(2) ?: continue
            }
            val wanted = ArrayList<Pair<String, List<Int>>>()
            for (source in SOURCES) {
                val known = columns[source.sqlTable] ?: continue
                if (source.fields.all { known.containsKey(it) }) wanted.add(source.sqlTable to source.fields)
            }
            for (table in extra) {
                val known = columns[table] ?: continue
                val fields = if (table == "characterfacialhairstyles_dbc") listOf(0, 1, 2) else listOf(1)
                if (fields.all { known.containsKey(it) }) wanted.add(table to fields)
            }
            val rows = db.queryAll(worldDb, wanted.map { (table, fields) ->
                "SELECT " + fields.joinToString(", ") { Sql.name(columns.getValue(table).getValue(it)) } + " FROM " + Sql.name(table)
            })
            val overlays = HashMap<String, List<Map<Int, String?>>>()
            wanted.forEachIndexed { index, (table, fields) ->
                overlays[table] = rows[index].map { row -> fields.withIndex().associate { (i, field) -> field to row.getOrNull(i) } }
            }
            val tables = SOURCES.associate { source ->
                source.key to DbcTable(source.key, files.getValue(source.key), source.idField, overlays[source.sqlTable].orEmpty())
            }
            // Facial hair styles have no id: the file's rows and the database's are all there are.
            val facial = ArrayList<IntArray>()
            DbcFile.find(dbcDir, "CharacterFacialHairStyles.dbc")?.let { DbcFile.open(it) }?.let { file ->
                for (record in 0 until file.recordCount) facial.add(intArrayOf(file.int(record, 0), file.int(record, 1), file.int(record, 2)))
            }
            for (row in overlays["characterfacialhairstyles_dbc"].orEmpty()) {
                facial.add(intArrayOf(row[0]?.toIntOrNull() ?: continue, row[1]?.toIntOrNull() ?: continue, row[2]?.toIntOrNull() ?: continue))
            }
            return RealmData(tables, facial, patterns(dbcDir, "NamesReserved.dbc", overlays["namesreserved_dbc"]), patterns(dbcDir, "NamesProfanity.dbc", overlays["namesprofanity_dbc"]))
        }

        /** A names file's patterns as the core keeps them (ObjectMgr::LoadReservedPlayerNamesDBC: the `\<` and `\>` marks taken off), in lower case. */
        private fun patterns(dbcDir: File, name: String, overlay: List<Map<Int, String?>>?): Set<String> {
            val out = HashSet<String>()
            DbcFile.find(dbcDir, name)?.let { DbcFile.open(it) }?.let { file ->
                for (record in 0 until file.recordCount) out.add(clean(file.string(record, 1)))
            }
            for (row in overlay.orEmpty()) row[1]?.let { out.add(clean(it)) }
            out.remove("")
            return out
        }

        private fun clean(pattern: String): String = pattern.replace("\\<", "").replace("\\>", "").lowercase()

        /** For tests: the data from tables made by hand. */
        internal fun of(tables: Map<String, DbcTable>, facialHair: List<IntArray> = emptyList(), reserved: Set<String> = emptySet(), profane: Set<String> = emptySet()): RealmData {
            val all = SOURCES.associate { it.key to (tables[it.key] ?: DbcTable(it.key, null, 0, emptyList())) }
            return RealmData(all, facialHair, reserved, profane)
        }
    }
}

/** One effect of a spell. */
data class SpellEffect(val effect: Int, val aura: Int, val misc: Int, val trigger: Int, val base: Int, val item: Int)
