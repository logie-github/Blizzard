package com.logie.blizz.porter.port

import java.io.ByteArrayOutputStream
import java.nio.ByteBuffer
import java.nio.ByteOrder

/** Hand-made realm data for the porter's unit tests: DBC files' bytes, tables, a database and an item source. */
object PortTestData {
    /** A WDBC file of four-byte fields: [rows] of [fields] numbers each, and the texts they point at (by [text]). */
    class DbcWriter(private val fields: Int) {
        private val strings = ByteArrayOutputStream().apply { write(0) }
        private val offsets = HashMap<String, Int>()
        private val rows = ArrayList<IntArray>()

        fun text(value: String): Int = offsets.getOrPut(value) {
            val at = strings.size()
            strings.write(value.toByteArray(Charsets.UTF_8))
            strings.write(0)
            at
        }

        fun row(vararg cells: Pair<Int, Int>): DbcWriter {
            val row = IntArray(fields)
            for ((field, value) in cells) row[field] = value
            rows.add(row)
            return this
        }

        fun bytes(): ByteArray {
            val stringBlock = strings.toByteArray()
            val buffer = ByteBuffer.allocate(20 + rows.size * fields * 4 + stringBlock.size).order(ByteOrder.LITTLE_ENDIAN)
            buffer.putInt(0x43424457).putInt(rows.size).putInt(fields).putInt(fields * 4).putInt(stringBlock.size)
            for (row in rows) for (cell in row) buffer.putInt(cell)
            buffer.put(stringBlock)
            return buffer.array()
        }
    }

    /** A client data table from database-style rows only (field number to text): what tests need of a file. */
    fun table(name: String, vararg rows: Map<Int, Any>): DbcTable =
        DbcTable(name, null, 0, rows.map { row -> row.mapValues { it.value.toString() } })

    fun spell(id: Int, name: String, rank: String = "", effects: List<SpellEffect> = emptyList(), attributesEx4: Int = 0): Map<Int, Any> {
        val row = HashMap<Int, Any>()
        row[0] = id
        row[4] = 0
        row[8] = attributesEx4
        for (i in 0..2) {
            val e = effects.getOrNull(i)
            row[71 + i] = e?.effect ?: 0
            row[80 + i] = e?.base ?: 0
            row[95 + i] = e?.aura ?: 0
            row[107 + i] = e?.item ?: 0
            row[110 + i] = e?.misc ?: 0
            row[116 + i] = e?.trigger ?: 0
        }
        row[136] = name
        row[153] = rank
        return row
    }

    fun ability(id: Int, skill: Int, spell: Int, raceMask: Int = 0, classMask: Int = 0, minRank: Int = 1, supercededBy: Int = 0, acquire: Int = 0): Map<Int, Any> =
        mapOf(0 to id, 1 to skill, 2 to spell, 3 to raceMask, 4 to classMask, 7 to minRank, 8 to supercededBy, 9 to acquire, 10 to 0)

    fun skillInfo(id: Int, skill: Int, raceMask: Int, classMask: Int, flags: Int = 0, tier: Int = 0): Map<Int, Any> =
        mapOf(0 to id, 1 to skill, 2 to raceMask, 3 to classMask, 4 to flags, 5 to 0, 6 to tier)

    fun skillLine(id: Int, category: Int, name: String): Map<Int, Any> = mapOf(0 to id, 1 to category, 3 to name)

    fun tiers(id: Int, vararg values: Int): Map<Int, Any> = (mapOf<Int, Any>(0 to id) + (17 until 33).associateWith { values.getOrElse(it - 17) { 0 } })

    fun race(id: Int, team: Int, name: String): Map<Int, Any> = mapOf(0 to id, 1 to 0, 7 to team, 14 to name)

    fun charClass(id: Int, name: String): Map<Int, Any> = mapOf(0 to id, 4 to name)

    fun faction(id: Int, name: String, list: Int, raceMasks: List<Int> = listOf(0, 0, 0, 0), classMasks: List<Int> = listOf(0, 0, 0, 0), bases: List<Int> = listOf(0, 0, 0, 0), flags: List<Int> = listOf(0, 0, 0, 0)): Map<Int, Any> {
        val row = HashMap<Int, Any>()
        row[0] = id
        row[1] = list
        for (i in 0..3) {
            row[2 + i] = raceMasks[i]
            row[6 + i] = classMasks[i]
            row[10 + i] = bases[i]
            row[14 + i] = flags[i]
        }
        row[18] = 0
        row[23] = name
        return row
    }

    val HUMAN = race(1, 7, "Human")
    val ORC = race(2, 1, "Orc")
    val WARRIOR = charClass(1, "Warrior")
    val HUNTER = charClass(3, "Hunter")

    /** Skills and spells enough for a human or orc warrior and a hunter: weapons, armour, riding, a profession. */
    fun realmData(extraSpells: List<Map<Int, Any>> = emptyList(), extraAbilities: List<Map<Int, Any>> = emptyList(), factions: List<Map<Int, Any>> = emptyList(),
                  extraTables: Map<String, DbcTable> = emptyMap(), facialHair: List<IntArray> = emptyList()): RealmData {
        val learn = 36
        val skillEffect = 118
        val aura = 6
        val spells = listOf(
            spell(78, "Heroic Strike", "Rank 1"), spell(284, "Heroic Strike", "Rank 2"),
            spell(2457, "Battle Stance"), spell(71, "Defensive Stance"), spell(355, "Taunt"), spell(7386, "Sunder Armor"),
            spell(750, "Plate Mail"), spell(674, "Dual Wield"), spell(201, "One-Handed Swords"), spell(202, "Two-Handed Swords"), spell(264, "Bows"),
            spell(33388, "Apprentice Riding", effects = listOf(SpellEffect(skillEffect, 0, 762, 0, 0, 0))),
            spell(33391, "Journeyman Riding", effects = listOf(SpellEffect(skillEffect, 0, 762, 0, 1, 0))),
            spell(2018, "Blacksmithing", "Apprentice", effects = listOf(SpellEffect(skillEffect, 0, 164, 0, 0, 0))),
            spell(2020, "Apprentice Blacksmith", effects = listOf(SpellEffect(learn, 0, 0, 2018, 0, 0), SpellEffect(44, 0, 164, 0, 0, 0))),
            spell(3100, "Blacksmithing", "Journeyman", effects = listOf(SpellEffect(skillEffect, 0, 164, 0, 1, 0))),
            spell(2660, "Rough Sharpening Stone", effects = listOf(SpellEffect(24, 0, 0, 0, 0, 2862))),
            spell(458, "Brown Horse", effects = listOf(SpellEffect(aura, 78, 284, 0, 0, 0), SpellEffect(aura, 32, 0, 0, 59, 0))),
            spell(23229, "Swift Brown Steed", effects = listOf(SpellEffect(aura, 78, 284, 0, 0, 0), SpellEffect(aura, 32, 0, 0, 99, 0))),
            spell(32235, "Golden Gryphon", effects = listOf(SpellEffect(aura, 78, 1, 0, 0, 0), SpellEffect(aura, 207, 0, 0, 149, 0), SpellEffect(aura, 32, 0, 0, 59, 0)), attributesEx4 = 0x04000000),
            spell(72286, "Invincible", effects = listOf(SpellEffect(aura, 78, 1, 0, 0, 0), SpellEffect(aura, 4, 0, 0, -1, 0), SpellEffect(77, 0, 0, 0, 0, 0))),
            spell(6603, "Auto Attack"), spell(266, "Guns"),
            spell(9001, "Increase Spell Dam 30", effects = listOf(SpellEffect(aura, 13, 126, 0, 29, 0))),
        ) + extraSpells
        val abilities = listOf(
            ability(1, 26, 78, acquire = 2), ability(2, 26, 284, classMask = 1), ability(3, 26, 2457, acquire = 2), ability(4, 257, 71, classMask = 1),
            ability(5, 257, 355, classMask = 1), ability(6, 257, 7386, classMask = 1),
            ability(7, 293, 750, classMask = 3, acquire = 2), ability(8, 118, 674, classMask = 13, acquire = 2),
            ability(9, 43, 201, classMask = 7, acquire = 2), ability(10, 55, 202, classMask = 3, acquire = 2), ability(11, 45, 264, classMask = 4, acquire = 2),
            ability(12, 762, 33388), ability(13, 762, 33391), ability(14, 164, 2018), ability(15, 164, 3100), ability(16, 164, 2660),
            ability(17, 777, 458), ability(18, 777, 23229), ability(19, 777, 32235), ability(20, 777, 72286), ability(21, 183, 6603, acquire = 2),
            ability(22, 46, 266, classMask = 7, acquire = 2),
        ) + extraAbilities
        val all = 0x7FFFFFFF
        val infos = listOf(
            skillInfo(1, 26, all, 1, flags = 0x10), skillInfo(2, 257, all, 1, flags = 0x10), skillInfo(3, 293, all, 3), skillInfo(4, 413, all, 7),
            skillInfo(5, 414, all, 0x7FF), skillInfo(6, 415, all, 0x7FF), skillInfo(7, 118, all, 13), skillInfo(8, 43, all, 7), skillInfo(9, 55, all, 3),
            skillInfo(10, 45, all, 4), skillInfo(11, 762, all, all, flags = 0x90, tier = 223), skillInfo(12, 164, all, all, tier = 41),
            skillInfo(13, 777, all, all), skillInfo(14, 183, all, all), skillInfo(15, 98, 1, all), skillInfo(16, 109, 2, all), skillInfo(17, 95, all, all),
            skillInfo(18, 433, all, 3), skillInfo(19, 46, all, 7),
        )
        val lines = listOf(
            skillLine(26, 7, "Arms"), skillLine(257, 7, "Protection"), skillLine(293, 8, "Plate Mail"), skillLine(413, 8, "Mail"), skillLine(414, 8, "Leather"),
            skillLine(415, 8, "Cloth"), skillLine(433, 8, "Shield"), skillLine(118, 6, "Dual Wield"), skillLine(43, 6, "Swords"), skillLine(55, 6, "Two-Handed Swords"),
            skillLine(45, 6, "Bows"), skillLine(762, 9, "Riding"), skillLine(164, 11, "Blacksmithing"), skillLine(777, 7, "Mounts"), skillLine(183, 12, "GENERIC"),
            skillLine(98, 10, "Language: Common"), skillLine(109, 10, "Language: Orcish"), skillLine(95, 6, "Defense"), skillLine(46, 6, "Guns"),
        )
        return RealmData.of(mapOf(
            "Spell" to table("Spell", *spells.toTypedArray()),
            "SkillLineAbility" to table("SkillLineAbility", *abilities.toTypedArray()),
            "SkillRaceClassInfo" to table("SkillRaceClassInfo", *infos.toTypedArray()),
            "SkillLine" to table("SkillLine", *lines.toTypedArray()),
            "SkillTiers" to table("SkillTiers", tiers(41, 75, 150, 225, 300, 375, 450), tiers(223, 75, 150, 225, 300)),
            "ChrRaces" to table("ChrRaces", HUMAN, ORC),
            "ChrClasses" to table("ChrClasses", WARRIOR, HUNTER),
            "Faction" to table("Faction", *factions.toTypedArray()),
        ) + extraTables, facialHair)
    }

    /** CharSections' row: a race and gender's look of one kind (0 skin, 1 face, 3 hair), a player's to pick. */
    fun section(id: Int, race: Int, gender: Int, kind: Int, variation: Int, color: Int, flags: Int = 1): Map<Int, Any> =
        mapOf(0 to id, 1 to race, 2 to gender, 3 to kind, 7 to flags, 8 to variation, 9 to color)

    /** The world database's part: a human and an orc warrior and a human hunter, their trainers. */
    fun realmWorld(): RealmWorld = RealmWorld(
        createInfos = listOf(
            CreateInfo(1, 1, 0, 12, -8949.95f, -132.49f, 83.53f, 0f), CreateInfo(2, 1, 1, 14, -618.5f, -4251.7f, 38.7f, 0f), CreateInfo(1, 3, 0, 12, -8949.95f, -132.49f, 83.53f, 0f),
        ),
        createSkills = listOf(
            CreateSkill(0, 1, 26, 0), CreateSkill(0, 1, 257, 0), CreateSkill(0, 1, 43, 0), CreateSkill(0, 0, 415, 0), CreateSkill(0, 0x7FF, 414, 0),
            CreateSkill(0, 1, 413, 0), CreateSkill(0, 1, 433, 0), CreateSkill(1, 0, 98, 0), CreateSkill(2, 0, 109, 0), CreateSkill(0, 0, 183, 0),
            CreateSkill(0, 0, 777, 0), CreateSkill(0, 0, 95, 0), CreateSkill(0, 4, 45, 0),
        ),
        createSpells = emptyList(),
        trainerSpells = listOf(
            TrainerSpell(1, 0, 1, 284, 0, 0, listOf(78), 6),
            TrainerSpell(1, 0, 1, 750, 0, 0, emptyList(), 40),
            TrainerSpell(1, 0, 1, 674, 0, 0, emptyList(), 10),
            TrainerSpell(35, 1, 0, 33388, 762, 0, emptyList(), 20),
            TrainerSpell(35, 1, 0, 33391, 762, 75, emptyList(), 40),
            TrainerSpell(47, 2, 0, 202, 0, 0, emptyList(), 0),
            TrainerSpell(47, 2, 0, 266, 0, 0, emptyList(), 0),
            TrainerSpell(60, 2, 0, 2020, 0, 0, emptyList(), 5),
            TrainerSpell(60, 2, 0, 3100, 164, 50, emptyList(), 10),
            TrainerSpell(60, 2, 0, 2660, 164, 1, emptyList(), 0),
        ),
        ranks = mapOf(78 to (78 to 1), 284 to (78 to 2), 33388 to (33388 to 1), 33391 to (33388 to 2), 2018 to (2018 to 1), 3100 to (2018 to 2)),
        required = emptyMap(),
        places = mapOf("Stormwind" to Place("Stormwind", 0, -8833.38f, 628.628f, 94.0066f, 1.06535f)),
    )

    /** An item as `item_template` would give it, in [ItemTemplate.COLUMNS]' order. */
    fun item(
        entry: Int, name: String, itemClass: Int, subclass: Int, inventoryType: Int, quality: Int = 3, itemLevel: Int = 60, requiredLevel: Int = 55,
        stats: List<Pair<Int, Int>> = emptyList(), armor: Int = 0, damage: Pair<Float, Float> = 0f to 0f, delay: Int = 0, allowableClass: Long = -1,
        allowableRace: Long = -1, flags: Long = 0, flagsExtra: Long = 0, maxCount: Int = 0, requiredSkill: Int = 0, requiredSkillRank: Int = 0,
        requiredRep: Pair<Int, Int> = 0 to 0, randomProperty: Int = 0, scaling: Int = 0, holiday: Int = 0, containerSlots: Int = 0, stackable: Int = 1,
        equipSpells: List<Int> = emptyList(), limitCategory: Int = 0,
    ) = ItemTemplate(
        entry, name, itemClass, subclass, inventoryType, quality, itemLevel, requiredLevel, allowableClass, allowableRace, flags, flagsExtra,
        requiredSkill, requiredSkillRank, 0, 0, 0, requiredRep.first, requiredRep.second, maxCount, stackable, containerSlots, stats, armor,
        damage.first, damage.second, delay, 0, 100, listOf(0, 0, 0, 0, 0), randomProperty, 0, scaling, holiday, 0, 0, 0, limitCategory, 1,
        equipSpells.map { it to 1 },
    )

    /** [item] as the database's text row ([ItemTemplate.parse]'s input). */
    fun row(item: ItemTemplate): List<String?> {
        val stats = (0 until 10).flatMap { listOf((item.stats.getOrNull(it)?.first ?: 0).toString(), (item.stats.getOrNull(it)?.second ?: 0).toString()) }
        val spells = (0 until 5).flatMap { listOf((item.spells.getOrNull(it)?.first ?: 0).toString(), (item.spells.getOrNull(it)?.second ?: 0).toString()) }
        return listOf(
            item.entry, item.name, item.itemClass, item.subclass, item.inventoryType, item.quality, item.itemLevel, item.requiredLevel, item.allowableClass,
            item.allowableRace, item.flags, item.flagsExtra, item.requiredSkill, item.requiredSkillRank, item.requiredSpell, item.requiredHonorRank,
            item.requiredCityRank, item.requiredRepFaction, item.requiredRepRank, item.maxCount, item.stackable, item.containerSlots,
        ).map { it.toString() } + stats + listOf(item.armor, item.damageMin, item.damageMax, item.delay, item.block, item.maxDurability).map { it.toString() } +
            item.charges.map { it.toString() } +
            listOf(item.randomProperty, item.randomSuffix, item.scalingStats, item.holiday, item.map, item.area, item.duration, item.itemLimitCategory, item.bonding).map { it.toString() } +
            spells
    }

    /** An item source over a list: every item it has is obtainable unless named in [unobtainable]. */
    class ListItemSource(private val all: List<ItemTemplate>, private val unobtainable: Set<Int> = emptySet()) : ItemSource {
        override fun items(ids: Collection<Int>) = all.filter { it.entry in ids }.associateBy { it.entry }
        override fun candidates(inventoryTypes: Set<Int>, rules: GearRules, wide: Boolean) = all.filter {
            it.inventoryType in inventoryTypes && it.itemLevel <= rules.maxItemLevel && it.requiredLevel <= rules.level && it.quality <= rules.maxQuality &&
                (wide || (it.quality >= GearRules.QUALITY_UNCOMMON && it.requiredLevel >= rules.minRequiredLevel))
        }
        override fun obtainable(ids: Collection<Int>, crafted: Set<Int>) = ids.filter { it !in unobtainable }.toSet()
    }

    /**
     * A database that answers SELECTs by the first rule whose text the statement contains, answers scripts it is told to
     * run by their own rules ([onExecute]), and records both.
     */
    class FakeRealmDb : RealmDb {
        val rules = ArrayList<Pair<String, (String) -> List<List<String?>>>>()
        private val executeRules = ArrayList<Pair<String, List<List<String?>>>>()
        val executed = ArrayList<Pair<String, String>>()
        val queries = ArrayList<String>()

        fun on(contains: String, rows: List<List<Any?>>) = apply { rules.add(contains to { _ -> rows.map { r -> r.map { it?.toString() } } }) }
        fun on(contains: String, answer: (String) -> List<List<String?>>) = apply { rules.add(contains to answer) }
        fun onExecute(contains: String, rows: List<List<Any?>>) = apply { executeRules.add(contains to rows.map { r -> r.map { it?.toString() } }) }

        override fun query(database: String, sql: String): List<List<String?>> {
            queries.add(sql)
            return rules.firstOrNull { sql.contains(it.first) }?.second?.invoke(sql) ?: emptyList()
        }

        override fun execute(database: String, sql: String): List<List<String?>> {
            executed.add(database to sql)
            return executeRules.firstOrNull { sql.contains(it.first) }?.second ?: emptyList()
        }
    }
}
