package com.logie.blizz.porter.port

/** Where a race and class start (playercreateinfo): which pairs the realm has, and where they are made. */
data class CreateInfo(val race: Int, val classId: Int, val map: Int, val zone: Int, val x: Float, val y: Float, val z: Float, val o: Float)

/** A skill every character of the races and classes in the masks has (playercreateinfo_skills; a mask of 0 is everyone). */
data class CreateSkill(val raceMask: Int, val classMask: Int, val skill: Int, val rank: Int)

/** A spell given at every login (playercreateinfo_spell_custom: the realm's custom races' racials). */
data class CreateSpell(val raceMask: Int, val classMask: Int, val spell: Int)

/** A button of a new character's action bar (playercreateinfo_action): 0 a spell, 128 an item, 64 a macro. */
data class CreateAction(val button: Int, val action: Int, val type: Int)

/** A spell a trainer teaches (trainer and trainer_spell): its kind (0 class, 1 riding, 2 profession and weapons, 3 pets) and what it asks. */
data class TrainerSpell(
    val trainer: Int,
    val type: Int,
    val requirement: Int,
    val spell: Int,
    val reqSkill: Int,
    val reqSkillRank: Int,
    val reqAbilities: List<Int>,
    val reqLevel: Int,
)

/** A place by name (game_tele). */
data class Place(val name: String, val map: Int, val x: Float, val y: Float, val z: Float, val o: Float)

/** A quest of the realm: its title, and the races that may take it (0: all). */
data class RealmQuest(val id: Int, val title: String, val allowableRaces: Long)

/**
 * What the porter reads of the realm's world database: never written. One batch of SELECTs ([load]), because on the
 * phone every call starts the database client anew.
 */
class RealmWorld(
    val createInfos: List<CreateInfo>,
    val createSkills: List<CreateSkill>,
    val createSpells: List<CreateSpell>,
    val trainerSpells: List<TrainerSpell>,
    /** spell_ranks: each spell's chain (its first rank) and its rank in it. */
    private val ranks: Map<Int, Pair<Int, Int>>,
    /** spell_required: the spells a spell needs before a trainer teaches it. */
    val required: Map<Int, List<Int>>,
    val places: Map<String, Place>,
) {
    private val chains: Map<Int, List<Int>> = ranks.entries.groupBy({ it.value.first }, { it.key to it.value.second })
        .mapValues { (_, spells) -> spells.sortedBy { it.second }.map { it.first } }

    /** The race and class pairs a character can be made as on this realm. */
    val combos: List<RaceClass> get() = createInfos.map { RaceClass(it.race, it.classId) }.distinct().sortedWith(compareBy({ it.race }, { it.classId }))

    fun createInfo(race: Int, classId: Int): CreateInfo? = createInfos.firstOrNull { it.race == race && it.classId == classId }

    /** The rank before [spell] in its chain (SpellMgr::GetPrevSpellInChain), or 0. */
    fun previousRank(spell: Int): Int {
        val (first, rank) = ranks[spell] ?: return 0
        if (rank <= 1) return 0
        return chains[first]?.getOrNull(rank - 2) ?: 0
    }

    /** Every rank of [spell]'s chain, lowest first (just [spell] when it has none). */
    fun chainOf(spell: Int): List<Int> = ranks[spell]?.let { chains[it.first] } ?: listOf(spell)

    companion object {
        fun load(db: RealmDb, worldDb: String, classId: Int?): RealmWorld {
            val trainerFilter = if (classId == null) "t.Type IN (0, 1, 2)" else "(t.Type = 0 AND t.Requirement = $classId) OR t.Type IN (1, 2)"
            val results = db.queryAll(worldDb, listOf(
                "SELECT race, class, map, zone, position_x, position_y, position_z, orientation FROM playercreateinfo",
                "SELECT raceMask, classMask, skill, `rank` FROM playercreateinfo_skills",
                "SELECT racemask, classmask, Spell FROM playercreateinfo_spell_custom",
                "SELECT t.Id, t.Type, t.Requirement, s.SpellId, s.ReqSkillLine, s.ReqSkillRank, s.ReqAbility1, s.ReqAbility2, s.ReqAbility3, s.ReqLevel " +
                    "FROM trainer_spell s JOIN trainer t ON t.Id = s.TrainerId WHERE $trainerFilter",
                "SELECT first_spell_id, spell_id, `rank` FROM spell_ranks",
                "SELECT spell_id, req_spell FROM spell_required",
                "SELECT name, map, position_x, position_y, position_z, orientation FROM game_tele WHERE name IN ('Stormwind', 'Orgrimmar')",
            ))
            fun num(s: String?): Int = s?.toLongOrNull()?.toInt() ?: s?.toDoubleOrNull()?.toInt() ?: 0
            fun dec(s: String?): Float = s?.toFloatOrNull() ?: 0f
            val infos = results[0].map { CreateInfo(num(it[0]), num(it[1]), num(it[2]), num(it[3]), dec(it[4]), dec(it[5]), dec(it[6]), dec(it[7])) }
            val skills = results[1].map { CreateSkill(num(it[0]), num(it[1]), num(it[2]), num(it[3])) }
            val spells = results[2].map { CreateSpell(num(it[0]), num(it[1]), num(it[2])) }
            val trainers = results[3].map {
                TrainerSpell(num(it[0]), num(it[1]), num(it[2]), num(it[3]), num(it[4]), num(it[5]), listOf(num(it[6]), num(it[7]), num(it[8])).filter { a -> a > 0 }, num(it[9]))
            }
            val ranks = results[4].associate { num(it[1]) to (num(it[0]) to num(it[2])) }
            val required = results[5].groupBy({ num(it[0]) }, { num(it[1]) })
            val places = results[6].associate { (it[0] ?: "") to Place(it[0] ?: "", num(it[1]), dec(it[2]), dec(it[3]), dec(it[4]), dec(it[5])) }
            return RealmWorld(infos, skills, spells, trainers, ranks, required, places)
        }
    }
}

/**
 * An item of the realm's `item_template`, with what the porter needs to judge it: where it goes, who may use it, what
 * it asks, and what it gives.
 */
data class ItemTemplate(
    val entry: Int,
    val name: String,
    val itemClass: Int,
    val subclass: Int,
    val inventoryType: Int,
    val quality: Int,
    val itemLevel: Int,
    val requiredLevel: Int,
    val allowableClass: Long,
    val allowableRace: Long,
    val flags: Long,
    val flagsExtra: Long,
    val requiredSkill: Int,
    val requiredSkillRank: Int,
    val requiredSpell: Int,
    val requiredHonorRank: Int,
    val requiredCityRank: Int,
    val requiredRepFaction: Int,
    val requiredRepRank: Int,
    val maxCount: Int,
    val stackable: Int,
    val containerSlots: Int,
    val stats: List<Pair<Int, Int>>,
    val armor: Int,
    val damageMin: Float,
    val damageMax: Float,
    val delay: Int,
    val block: Int,
    val maxDurability: Int,
    val charges: List<Int>,
    val randomProperty: Int,
    val randomSuffix: Int,
    val scalingStats: Int,
    val holiday: Int,
    val map: Int,
    val area: Int,
    val duration: Int,
    val itemLimitCategory: Int,
    val bonding: Int,
    /** Its spells and when each acts (1: while worn). */
    val spells: List<Pair<Int, Int>> = emptyList(),
) {
    /** The spells that act while it is worn. */
    val equipSpells: List<Int> get() = spells.filter { it.second == TRIGGER_ON_EQUIP && it.first > 0 }.map { it.first }

    /** Damage per second of a weapon (0 for anything else). */
    val dps: Double get() = if (delay > 0 && damageMax > 0) (damageMin + damageMax) / 2.0 / (delay / 1000.0) else 0.0

    /** Player::CanUseItem's masks: -1 is everyone, 0 no one. */
    fun usableByClass(classId: Int): Boolean = allowableClass and RealmData.classBit(classId).toLong() != 0L
    fun usableByRace(race: Int): Boolean = allowableRace and RealmData.raceBit(race).toLong() != 0L

    companion object {
        const val FLAG_CONJURED = 0x2L
        const val FLAG_DEPRECATED = 0x10L
        const val FLAG_UNIQUE_EQUIPPABLE = 0x80000L
        const val EXTRA_HORDE_ONLY = 0x1L
        const val EXTRA_ALLIANCE_ONLY = 0x2L
        const val TRIGGER_ON_EQUIP = 1

        /** The columns read, in the order [parse] reads them. */
        val COLUMNS = listOf(
            "entry", "name", "class", "subclass", "InventoryType", "Quality", "ItemLevel", "RequiredLevel", "AllowableClass", "AllowableRace",
            "Flags", "FlagsExtra", "RequiredSkill", "RequiredSkillRank", "requiredspell", "requiredhonorrank", "RequiredCityRank",
            "RequiredReputationFaction", "RequiredReputationRank", "maxcount", "stackable", "ContainerSlots",
        ) + (1..10).flatMap { listOf("stat_type$it", "stat_value$it") } + listOf(
            "armor", "dmg_min1", "dmg_max1", "delay", "block", "MaxDurability",
        ) + (1..5).map { "spellcharges_$it" } + listOf(
            "RandomProperty", "RandomSuffix", "ScalingStatDistribution", "HolidayId", "Map", "area", "duration", "ItemLimitCategory", "bonding",
        ) + (1..5).flatMap { listOf("spellid_$it", "spelltrigger_$it") }

        val SELECT: String = "SELECT " + COLUMNS.joinToString(", ") { Sql.name(it) } + " FROM item_template"

        fun parse(row: List<String?>): ItemTemplate {
            var i = 0
            fun text() = row.getOrNull(i++) ?: ""
            fun int() = text().let { it.toLongOrNull()?.toInt() ?: it.toDoubleOrNull()?.toInt() ?: 0 }
            fun long() = text().let { it.toLongOrNull() ?: it.toDoubleOrNull()?.toLong() ?: 0L }
            fun float() = text().toFloatOrNull() ?: 0f
            val entry = int()
            val name = text()
            val item = ItemTemplate(
                entry = entry, name = name, itemClass = int(), subclass = int(), inventoryType = int(), quality = int(), itemLevel = int(),
                requiredLevel = int(), allowableClass = long(), allowableRace = long(), flags = long(), flagsExtra = long(), requiredSkill = int(),
                requiredSkillRank = int(), requiredSpell = int(), requiredHonorRank = int(), requiredCityRank = int(), requiredRepFaction = int(),
                requiredRepRank = int(), maxCount = int(), stackable = int(), containerSlots = int(),
                stats = (1..10).map { int() to int() }.filter { it.first != 0 || it.second != 0 }.filter { it.second != 0 },
                armor = int(), damageMin = float(), damageMax = float(), delay = int(), block = int(), maxDurability = int(),
                charges = (1..5).map { int() },
                randomProperty = int(), randomSuffix = int(), scalingStats = int(), holiday = int(), map = int(), area = int(), duration = int(),
                itemLimitCategory = int(), bonding = int(),
                spells = (1..5).map { int() to int() }.filter { it.first != 0 },
            )
            return item
        }
    }
}
