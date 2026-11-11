package com.logie.blizz.porter.port

/** The realm's equipment slots (the core's EquipmentSlots), and the Armory's names for them. */
object PortSlots {
    const val HEAD = 0
    const val NECK = 1
    const val SHOULDERS = 2
    const val SHIRT = 3
    const val CHEST = 4
    const val WAIST = 5
    const val LEGS = 6
    const val FEET = 7
    const val WRISTS = 8
    const val HANDS = 9
    const val FINGER1 = 10
    const val FINGER2 = 11
    const val TRINKET1 = 12
    const val TRINKET2 = 13
    const val BACK = 14
    const val MAIN_HAND = 15
    const val OFF_HAND = 16
    const val RANGED = 17
    const val TABARD = 18
    const val EQUIPMENT_END = 19
    /** The four bag slots, and the backpack's sixteen. */
    const val BAG_FIRST = 19
    const val BACKPACK_FIRST = 23
    const val BACKPACK_LAST = 38

    private val NAMES = listOf("Head", "Neck", "Shoulders", "Shirt", "Chest", "Waist", "Legs", "Feet", "Wrists", "Hands", "Finger", "Finger", "Trinket", "Trinket", "Back", "Main hand", "Off hand", "Ranged", "Tabard")

    fun name(slot: Int): String = when (slot) {
        FINGER1, TRINKET1 -> NAMES[slot] + " 1"
        FINGER2, TRINKET2 -> NAMES[slot] + " 2"
        in 0 until EQUIPMENT_END -> NAMES[slot]
        in BAG_FIRST until BACKPACK_FIRST -> "Bag ${slot - BAG_FIRST + 1}"
        else -> "Backpack ${slot - BACKPACK_FIRST + 1}"
    }

    private val ARMORY = mapOf(
        "head" to HEAD, "neck" to NECK, "shoulder" to SHOULDERS, "shoulders" to SHOULDERS, "back" to BACK, "cloak" to BACK,
        "chest" to CHEST, "shirt" to SHIRT, "body" to SHIRT, "tabard" to TABARD, "wrist" to WRISTS, "wrists" to WRISTS,
        "hand" to HANDS, "hands" to HANDS, "waist" to WAIST, "leg" to LEGS, "legs" to LEGS, "foot" to FEET, "feet" to FEET,
        "leftfinger" to FINGER1, "finger1" to FINGER1, "rightfinger" to FINGER2, "finger2" to FINGER2,
        "lefttrinket" to TRINKET1, "trinket1" to TRINKET1, "righttrinket" to TRINKET2, "trinket2" to TRINKET2,
        "weapon" to MAIN_HAND, "mainhand" to MAIN_HAND, "offhand" to OFF_HAND, "secondaryhand" to OFF_HAND, "ranged" to RANGED,
    )

    /** The realm slot of an Armory slot name, whichever of its two spellings ("leftFinger", "FINGER_1"); null when unknown. */
    fun realmSlot(armory: String): Int? = ARMORY[armory.lowercase().replace("_", "").replace(" ", "")]
}

/** The core's InventoryType values, and the Armory's names for them. */
object InventoryTypes {
    const val HEAD = 1
    const val NECK = 2
    const val SHOULDERS = 3
    const val BODY = 4
    const val CHEST = 5
    const val WAIST = 6
    const val LEGS = 7
    const val FEET = 8
    const val WRISTS = 9
    const val HANDS = 10
    const val FINGER = 11
    const val TRINKET = 12
    const val WEAPON = 13
    const val SHIELD = 14
    const val RANGED = 15
    const val CLOAK = 16
    const val TWO_HAND = 17
    const val BAG = 18
    const val TABARD = 19
    const val ROBE = 20
    const val MAIN_HAND = 21
    const val OFF_HAND = 22
    const val HOLDABLE = 23
    const val AMMO = 24
    const val THROWN = 25
    const val RANGED_RIGHT = 26
    const val RELIC = 28

    private val ARMORY = mapOf(
        "HEAD" to HEAD, "NECK" to NECK, "SHOULDER" to SHOULDERS, "SHOULDERS" to SHOULDERS, "BODY" to BODY, "SHIRT" to BODY, "CHEST" to CHEST,
        "WAIST" to WAIST, "LEGS" to LEGS, "FEET" to FEET, "WRIST" to WRISTS, "WRISTS" to WRISTS, "HAND" to HANDS, "HANDS" to HANDS,
        "FINGER" to FINGER, "TRINKET" to TRINKET, "WEAPON" to WEAPON, "SHIELD" to SHIELD, "RANGED" to RANGED, "CLOAK" to CLOAK,
        "TWOHWEAPON" to TWO_HAND, "2HWEAPON" to TWO_HAND, "BAG" to BAG, "TABARD" to TABARD, "ROBE" to ROBE, "WEAPONMAINHAND" to MAIN_HAND,
        "WEAPONOFFHAND" to OFF_HAND, "HOLDABLE" to HOLDABLE, "AMMO" to AMMO, "THROWN" to THROWN, "RANGEDRIGHT" to RANGED_RIGHT, "RELIC" to RELIC,
    )

    fun of(armory: String): Int? = ARMORY[armory.uppercase().replace("_", "")]
}

/** How a character holds its weapons. */
enum class GearHands { TWO_HAND, ONE_HAND, DUAL_WIELD, ONE_HAND_SHIELD, ONE_HAND_HOLDABLE }

/** How the item of a slot was chosen. */
enum class GearHow {
    /** The very item the character wears in retail. */
    EXACT,
    /** The item whose look the character wears (its transmog), which this realm has. */
    TRANSMOG,
    /** An item of this realm in place of the retail one. */
    REPLACEMENT,
    /** Something retail has no slot for (the ranged or relic slot), or that a character needs. */
    ADDED,
    /** Nothing fitting was found. */
    NONE,
}

/** One slot's choice, and why. */
data class SlotChoice(val slot: Int, val retail: PortEquipment?, val item: ItemTemplate?, val how: GearHow, val why: String) {
    val slotName: String get() = PortSlots.name(slot)
}

/** The items the porter looks at: the realm's `item_template` (through the database on the phone, a list in tests). */
interface ItemSource {
    /** The items with these ids that the realm has. */
    fun items(ids: Collection<Int>): Map<Int, ItemTemplate>

    /**
     * Wearable items of these inventory types under [rules]' limits ([GearRules.sqlFilter] is the cheap part of the
     * filter; the gear planner checks everything again). [wide] drops the lower level bound and lets common items in,
     * for a slot that found nothing otherwise.
     */
    fun candidates(inventoryTypes: Set<Int>, rules: GearRules, wide: Boolean): List<ItemTemplate>

    /** Which of these items the game gives in some way: loot, a vendor, a quest, or a recipe ([crafted] are the realm's recipes' items). */
    fun obtainable(ids: Collection<Int>, crafted: Set<Int>): Set<Int>
}

/** The limits a character's gear is chosen under: who wears it, at which level, how good it may be. */
data class GearRules(val race: Int, val classId: Int, val level: Int, val side: PortFaction, val tier: GearTier) {
    /** The best quality and the highest item level allowed (null: only the required level limits it). */
    val maxQuality: Int get() = if (tier == GearTier.FRESH) QUALITY_RARE else QUALITY_EPIC

    /**
     * The highest item level allowed. At the expansions' caps, the tier's own (80: heroic dungeons' 200, Naxxramas'
     * 213, Icecrown's and the Ruby Sanctum's 284; 70: 115, 125, 164; 60: 63, 71, 92). Between them, what a character of
     * the level finds (an item's level runs a few above its required level before 60, and climbs faster through
     * Outland and Northrend), a few levels more for the Raid and Best tiers. It bounds even items that ask no level:
     * quest rewards whose quest asked it.
     */
    val maxItemLevel: Int get() {
        val fresh = when {
            level >= 80 -> 200
            level > 70 -> 115 + (level - 70) * 8
            level == 70 -> 115
            level > 60 -> 63 + (level - 60) * 5
            level == 60 -> 63
            else -> level + 8
        }
        return when (tier) {
            GearTier.FRESH -> fresh
            GearTier.RAID -> when (level) { 80 -> 213; 70 -> 125; 60 -> 71; else -> fresh + 8 }
            GearTier.BEST -> when (level) { 80 -> 284; 70 -> 164; 60 -> 92; else -> fresh + 12 }
        }
    }

    /** The lowest required level of a candidate: items of the last fifteen levels (a wider search drops it). */
    val minRequiredLevel: Int get() = (level - 15).coerceAtLeast(0)

    /** The item flag of the other side's items (FlagsExtra), which this character can never use. */
    val otherSideFlag: Long get() = when (side) {
        PortFaction.ALLIANCE -> ItemTemplate.EXTRA_HORDE_ONLY
        PortFaction.HORDE -> ItemTemplate.EXTRA_ALLIANCE_ONLY
        PortFaction.NEUTRAL -> 0L
    }

    /** The SQL condition for the realm's `item_template` (numbers only: every value here is an Int). */
    fun sqlFilter(inventoryTypes: Set<Int>, wide: Boolean): String {
        val quality = if (wide) "Quality BETWEEN $QUALITY_COMMON AND $maxQuality" else "Quality BETWEEN $QUALITY_UNCOMMON AND $maxQuality"
        val required = if (wide) "RequiredLevel <= $level" else "RequiredLevel BETWEEN $minRequiredLevel AND $level"
        return "class IN (2, 4) AND InventoryType IN (${Sql.list(inventoryTypes)}) AND $quality AND $required" +
            " AND ItemLevel <= $maxItemLevel" +
            " AND (AllowableClass & ${RealmData.classBit(classId)}) <> 0 AND (AllowableRace & ${RealmData.raceBit(race)}) <> 0" +
            " AND requiredhonorrank = 0 AND RequiredCityRank = 0 AND HolidayId = 0 AND Map = 0 AND area = 0 AND duration = 0" +
            " AND RandomProperty = 0 AND RandomSuffix = 0 AND ScalingStatDistribution = 0" +
            " AND (Flags & ${ItemTemplate.FLAG_CONJURED or ItemTemplate.FLAG_DEPRECATED}) = 0 AND (FlagsExtra & $otherSideFlag) = 0"
    }

    companion object {
        const val QUALITY_POOR = 0
        const val QUALITY_COMMON = 1
        const val QUALITY_UNCOMMON = 2
        const val QUALITY_RARE = 3
        const val QUALITY_EPIC = 4
        const val QUALITY_HEIRLOOM = 7
    }
}

/**
 * How much each stat is worth to a role (the core's ItemModType numbers), for choosing between items of a slot. The
 * numbers only need to order a slot's items sensibly: a stat the role lives on first, then what helps it, then the rest.
 */
class StatWeights(private val stats: Map<Int, Double>, val armor: Double, val meleeDps: Double, val rangedDps: Double, val blockValue: Double) {
    fun of(stat: Int): Double = stats[stat] ?: 0.0

    /** How good [item] is in [slot] for the role; [equip] are the stats its equip spells give ([RealmData.equipStats]). */
    fun score(item: ItemTemplate, slot: Int, equip: List<Pair<Int, Int>> = emptyList()): Double {
        var score = 0.0
        for ((type, value) in item.stats) score += of(type) * value
        for ((type, value) in equip) score += of(type) * value
        score += armor * item.armor + blockValue * item.block
        if (item.itemClass == ITEM_WEAPON) score += (if (slot == PortSlots.RANGED) rangedDps else meleeDps) * item.dps
        // (items without stats, the low levels' whites: the better made first)
        return score + item.itemLevel * 0.01 + item.quality * 0.001
    }

    companion object {
        const val ITEM_WEAPON = 2
        const val ITEM_ARMOR = 4
        private const val AGILITY = 3
        private const val STRENGTH = 4
        private const val INTELLECT = 5
        private const val SPIRIT = 6
        private const val STAMINA = 7
        private const val DEFENSE = 12
        private const val DODGE = 13
        private const val PARRY = 14
        private const val BLOCK = 15
        private const val HIT_MELEE = 16
        private const val HIT_RANGED = 17
        private const val HIT_SPELL = 18
        private const val CRIT_MELEE = 19
        private const val CRIT_RANGED = 20
        private const val CRIT_SPELL = 21
        private const val HASTE_MELEE = 28
        private const val HASTE_RANGED = 29
        private const val HASTE_SPELL = 30
        private const val HIT = 31
        private const val CRIT = 32
        private const val HASTE = 36
        private const val EXPERTISE = 37
        private const val ATTACK_POWER = 38
        private const val RANGED_ATTACK_POWER = 39
        private const val FERAL_ATTACK_POWER = 40
        private const val HEALING = 41
        private const val SPELL_DAMAGE = 42
        private const val MP5 = 43
        private const val ARMOR_PENETRATION = 44
        private const val SPELL_POWER = 45
        private const val BLOCK_VALUE = 48

        private fun physical(main: Int, other: Int, extra: Map<Int, Double> = emptyMap()) = mapOf(
            main to 1.0, other to 0.4, STAMINA to 0.05, ATTACK_POWER to 0.45, CRIT_MELEE to 0.55, CRIT to 0.55, HIT_MELEE to 0.6, HIT to 0.6,
            HASTE_MELEE to 0.45, HASTE to 0.45, EXPERTISE to 0.5, ARMOR_PENETRATION to 0.55,
        ) + extra

        private val CASTER = mapOf(
            SPELL_POWER to 1.0, SPELL_DAMAGE to 1.0, INTELLECT to 0.35, SPIRIT to 0.15, STAMINA to 0.05, HIT_SPELL to 0.7, HIT to 0.7,
            CRIT_SPELL to 0.5, CRIT to 0.5, HASTE_SPELL to 0.6, HASTE to 0.6, MP5 to 0.2,
        )

        private val HEALER = mapOf(
            SPELL_POWER to 1.0, HEALING to 1.0, INTELLECT to 0.7, SPIRIT to 0.45, MP5 to 0.6, CRIT_SPELL to 0.4, CRIT to 0.4,
            HASTE_SPELL to 0.5, HASTE to 0.5, STAMINA to 0.1,
        )

        private val PLATE_TANK = mapOf(
            STAMINA to 1.0, DEFENSE to 0.9, DODGE to 0.7, PARRY to 0.65, BLOCK to 0.4, BLOCK_VALUE to 0.25, STRENGTH to 0.45, AGILITY to 0.4,
            EXPERTISE to 0.4, HIT_MELEE to 0.35, HIT to 0.35, 1 to 0.1,
        )

        private val BEAR_TANK = mapOf(
            STAMINA to 1.0, AGILITY to 0.9, DODGE to 0.7, DEFENSE to 0.5, EXPERTISE to 0.4, HIT_MELEE to 0.35, HIT to 0.35, STRENGTH to 0.3,
            FERAL_ATTACK_POWER to 0.2, ATTACK_POWER to 0.2,
        )

        /** The weights for a class (the realm's id), the role it plays, and the stat its spec lives on when known. */
        fun of(classId: Int, role: PortRole, primary: PortStat?): StatWeights {
            val main = primary ?: when (classId) {
                PortTargets.WARRIOR, PortTargets.DEATH_KNIGHT -> PortStat.STRENGTH
                PortTargets.PALADIN -> if (role == PortRole.HEALER) PortStat.INTELLECT else PortStat.STRENGTH
                PortTargets.ROGUE, PortTargets.HUNTER -> PortStat.AGILITY
                PortTargets.DRUID -> if (role == PortRole.DAMAGE) PortStat.INTELLECT else if (role == PortRole.TANK) PortStat.AGILITY else PortStat.INTELLECT
                PortTargets.SHAMAN -> PortStat.INTELLECT
                else -> PortStat.INTELLECT
            }
            return when {
                role == PortRole.TANK && classId == PortTargets.DRUID -> StatWeights(BEAR_TANK, armor = 0.04, meleeDps = 0.5, rangedDps = 0.0, blockValue = 0.0)
                role == PortRole.TANK -> StatWeights(PLATE_TANK, armor = 0.02, meleeDps = 1.5, rangedDps = 0.2, blockValue = 0.25)
                role == PortRole.HEALER -> StatWeights(HEALER, armor = 0.003, meleeDps = 0.0, rangedDps = 0.0, blockValue = 0.0)
                classId == PortTargets.HUNTER -> StatWeights(
                    physical(AGILITY, INTELLECT, mapOf(RANGED_ATTACK_POWER to 0.45, CRIT_RANGED to 0.55, HIT_RANGED to 0.6, HASTE_RANGED to 0.4, INTELLECT to 0.25, STRENGTH to 0.05)),
                    armor = 0.003, meleeDps = 0.3, rangedDps = 3.5, blockValue = 0.0,
                )
                main == PortStat.STRENGTH -> StatWeights(physical(STRENGTH, AGILITY), armor = 0.003, meleeDps = 3.0, rangedDps = 0.3, blockValue = 0.0)
                main == PortStat.AGILITY -> StatWeights(
                    physical(AGILITY, STRENGTH, if (classId == PortTargets.DRUID) mapOf(FERAL_ATTACK_POWER to 0.45) else if (classId == PortTargets.SHAMAN) mapOf(INTELLECT to 0.3) else emptyMap()),
                    armor = 0.003, meleeDps = 3.0, rangedDps = 0.3, blockValue = 0.0,
                )
                else -> StatWeights(CASTER, armor = 0.003, meleeDps = 0.0, rangedDps = 0.0, blockValue = 0.0)
            }
        }
    }
}

/**
 * Chooses what a ported character wears, slot by slot: the retail item when the realm has the very item and the
 * character can use it; else the item whose look it wears (its transmog), when the realm has that and it is within the
 * limits; else the realm's best item for the slot and the role. The character's weapon configuration is kept where its
 * class can hold it (two-hander, one-hander and shield or off-hand, two weapons), and its class's ranged or relic slot
 * is filled, which retail no longer has.
 *
 * Checks every rule the core applies as it loads a character's equipment (Player::CanEquipItem, CanUseItem): the
 * class and race masks, the side, the required level, the weapon and armour skills ([skills]: what the character
 * will have), required skills, spells and reputations, and that unique items are worn once.
 */
class GearPlanner(
    private val source: ItemSource,
    private val rules: GearRules,
    private val weights: StatWeights,
    private val role: PortRole,
    /** The character's skills as planned: skill id to value. */
    private val skills: Map<Int, Int>,
    private val knownSpells: Set<Int>,
    /** The reputation rank the character will have with a faction (0 Hated ... 7 Exalted), or null when unknown. */
    private val reputationRank: (Int) -> Int?,
    /** The items the realm's recipes make (they are obtainable). */
    private val crafted: Set<Int>,
    /** The item stats an equip spell gives ([RealmData.equipStats]). */
    private val equipStats: (Int) -> List<Pair<Int, Int>> = { emptyList() },
) {
    private val equipCache = HashMap<Int, List<Pair<Int, Int>>>()

    private fun score(item: ItemTemplate, slot: Int) =
        weights.score(item, slot, item.equipSpells.flatMap { spell -> equipCache.getOrPut(spell) { equipStats(spell) } })

    private val classId get() = rules.classId

    /** What was chosen: the slots, and the reasons as lines. */
    data class Result(val choices: List<SlotChoice>, val hands: GearHands, val handsWhy: String)

    fun plan(equipment: List<PortEquipment>): Result {
        val bySlot = HashMap<Int, PortEquipment>()
        var retailRangedMain: PortEquipment? = null
        for (piece in equipment) {
            val slot = PortSlots.realmSlot(piece.slot) ?: continue
            if (slot == PortSlots.MAIN_HAND && isRangedWeapon(piece)) {
                retailRangedMain = piece
                continue
            }
            bySlot.putIfAbsent(slot, piece)
        }
        val known = source.items(equipment.flatMap { listOfNotNull(it.itemId, it.transmogItemId) }.filter { it > 0 })

        val (hands, handsWhy) = chooseHands(bySlot[PortSlots.MAIN_HAND], bySlot[PortSlots.OFF_HAND])

        // The slots to fill: those retail fills (but the weapons, by the configuration), and the class's ranged slot.
        val wanted = LinkedHashMap<Int, PortEquipment?>()
        for (slot in 0 until PortSlots.EQUIPMENT_END) {
            if (slot == PortSlots.MAIN_HAND || slot == PortSlots.OFF_HAND || slot == PortSlots.RANGED) continue
            bySlot[slot]?.let { wanted[slot] = it }
        }
        if (bySlot[PortSlots.MAIN_HAND] != null || retailRangedMain != null) {
            wanted[PortSlots.MAIN_HAND] = bySlot[PortSlots.MAIN_HAND]
            if (hands != GearHands.TWO_HAND && hands != GearHands.ONE_HAND) wanted[PortSlots.OFF_HAND] = bySlot[PortSlots.OFF_HAND]
        }
        val rangedKinds = rangedSlotKinds()
        if (rangedKinds.isNotEmpty() && (wanted.isNotEmpty() || retailRangedMain != null)) wanted[PortSlots.RANGED] = retailRangedMain

        // Every candidate the realm has for these slots, at once; a wider look for the slots that found nothing.
        val types = wanted.keys.flatMap { slotTypes(it, hands) }.toSet()
        val pool = ArrayList(source.candidates(types, rules, wide = false))
        val usable = HashMap<Int, List<ItemTemplate>>()
        fun fill(list: List<ItemTemplate>) {
            val ok = list.filter { problem(it) == null && !looksUnreal(it) }
            val obtainable = source.obtainable(ok.map { it.entry }, crafted)
            for (slot in wanted.keys) {
                usable[slot] = (usable[slot].orEmpty() + ok.filter { it.entry in obtainable && fitsSlot(it, slot, hands) }).distinctBy { it.entry }
            }
        }
        fill(pool)
        val empty = wanted.keys.filter { usable[it].isNullOrEmpty() }
        if (empty.isNotEmpty()) fill(source.candidates(empty.flatMap { slotTypes(it, hands) }.toSet(), rules, wide = true))

        val chosen = ArrayList<SlotChoice>()
        val taken = HashSet<Int>()
        val categories = HashSet<Int>()
        for ((slot, retail) in wanted) {
            val choice = choose(slot, retail, hands, known, usable[slot].orEmpty(), taken, categories)
            choice.item?.let { item ->
                taken.add(item.entry)
                if (item.itemLimitCategory != 0) categories.add(item.itemLimitCategory)
            }
            chosen.add(choice)
        }
        return Result(chosen.sortedBy { it.slot }, hands, handsWhy)
    }

    private fun choose(
        slot: Int,
        retail: PortEquipment?,
        hands: GearHands,
        known: Map<Int, ItemTemplate>,
        pool: List<ItemTemplate>,
        taken: Set<Int>,
        categories: Set<Int>,
    ): SlotChoice {
        fun free(item: ItemTemplate) = item.entry !in taken && (item.itemLimitCategory == 0 || item.itemLimitCategory !in categories)
        val notes = ArrayList<String>()
        if (retail != null) {
            // 1. The very item.
            val exact = known[retail.itemId]
            when {
                exact == null -> notes.add("this game has no item ${retail.itemId}")
                !sameName(exact.name, retail.name) -> notes.add("item ${retail.itemId} is another item here (${exact.name})")
                else -> {
                    val problem = problem(exact, exact = true) ?: if (!fitsSlot(exact, slot, hands, exact = true)) "it doesn't fit the ${PortSlots.name(slot).lowercase()} as this character holds its weapons" else if (!free(exact)) "it is unique and already worn" else null
                    if (problem == null) return SlotChoice(slot, retail, exact, GearHow.EXACT, "the same item")
                    notes.add("${exact.name}: $problem")
                }
            }
            // 2. Its look, when this game has that item and it is within the limits.
            retail.transmogItemId?.takeIf { it > 0 && it != retail.itemId }?.let { look ->
                val item = pool.firstOrNull { it.entry == look }
                if (item != null && free(item)) return SlotChoice(slot, retail, item, GearHow.TRANSMOG, "its look (transmog); " + notes.joinToString("; "))
                known[look]?.let { notes.add("its look, ${it.name}, is outside this character's limits") }
            }
        }
        // 3. The best item of the slot for the role, of the retail weapon's kind where the class can use it.
        val retailKind = retail?.takeIf { it.itemClass == StatWeights.ITEM_WEAPON }?.itemSubclass
        val ofKind = if (retailKind != null && retailKind >= 0) pool.filter { it.itemClass == StatWeights.ITEM_WEAPON && it.subclass == retailKind && free(it) } else emptyList()
        val candidates = ofKind.ifEmpty { pool.filter(::free) }
        // (a tabard says whose side one is on: none is given in place of another)
        if (slot == PortSlots.TABARD) return SlotChoice(slot, retail, null, GearHow.NONE, (notes + "no tabard is given in place of another").joinToString("; "))
        val best = candidates.maxWithOrNull(compareBy<ItemTemplate> { score(it, slot) }.thenBy { it.itemLevel }.thenBy { -it.entry })
        if (best == null) {
            return SlotChoice(slot, retail, null, GearHow.NONE, (notes + "nothing of this realm fits").joinToString("; "))
        }
        val how = if (retail == null) GearHow.ADDED else GearHow.REPLACEMENT
        val why = buildString {
            if (notes.isNotEmpty()) append(notes.joinToString("; ")).append("; ")
            append(if (retail == null) "the class's ${PortSlots.name(slot).lowercase()} slot" else "the best for a ${role.name.lowercase()} of its level")
            append(" (item level ${best.itemLevel}")
            if (ofKind.isNotEmpty()) append(", the same kind of weapon")
            append(")")
        }
        return SlotChoice(slot, retail, best, how, why)
    }

    // ---- what a character may wear

    /** Why the character can't wear [item] (the core's own checks), or null when it can. */
    fun problem(item: ItemTemplate, exact: Boolean = false): String? {
        if (!item.usableByClass(classId)) return "not for this class"
        if (!item.usableByRace(rules.race)) return "not for this race"
        if (item.flagsExtra and rules.otherSideFlag != 0L) return "the other side's"
        if (item.requiredLevel > rules.level) return "needs level ${item.requiredLevel}"
        // (the tier's limits: for anything but the very item the character wears)
        if (!exact && item.itemLevel > rules.maxItemLevel) return "above item level ${rules.maxItemLevel}"
        if (!exact && item.quality > rules.maxQuality) return "better than the tier allows"
        val skill = itemSkill(item)
        if (skill != 0 && (skills[skill] ?: 0) == 0) return "needs a skill this character doesn't have"
        if (item.requiredSkill != 0 && (skills[item.requiredSkill] ?: 0) < item.requiredSkillRank) return "needs a profession at ${item.requiredSkillRank}"
        if (item.requiredSpell != 0 && item.requiredSpell !in knownSpells) return "needs a specialization"
        if (item.requiredRepFaction != 0 && (reputationRank(item.requiredRepFaction) ?: -1) < item.requiredRepRank) return "needs a reputation this character won't have"
        if (item.requiredHonorRank != 0 || item.requiredCityRank != 0) return "a PvP rank's"
        if (item.holiday != 0) return "only during a holiday"
        if (item.map != 0 || item.area != 0) return "only usable in one place"
        if (item.duration != 0) return "it expires"
        if (item.flags and ItemTemplate.FLAG_CONJURED != 0L) return "conjured"
        if (item.randomProperty != 0 || item.randomSuffix != 0) return "its random enchantment can't be known"
        if (item.scalingStats != 0 && (!exact || rules.level > HEIRLOOM_MAX_LEVEL)) return "an heirloom"
        if (!exact && item.flags and ItemTemplate.FLAG_DEPRECATED != 0L) return "deprecated"
        return null
    }

    /** The weapon or armour skill an item needs (Item::GetSkill). */
    private fun itemSkill(item: ItemTemplate): Int = when (item.itemClass) {
        StatWeights.ITEM_WEAPON -> WEAPON_SKILLS[item.subclass] ?: 0
        StatWeights.ITEM_ARMOR -> ARMOR_SKILLS[item.subclass] ?: 0
        else -> 0
    }

    private fun can(skill: Int) = (skills[skill] ?: 0) > 0

    /** The armour subclass the character wears: the best its skills allow (plate, mail, leather, cloth). */
    private val armorSubclass: Int by lazy { listOf(4, 3, 2, 1).firstOrNull { can(ARMOR_SKILLS.getValue(it)) } ?: 1 }

    private fun canDualWield() = can(SKILL_DUAL_WIELD) || SPELL_DUAL_WIELD in knownSpells

    private fun twoHandKinds() = TWO_HAND_KINDS.filter { can(WEAPON_SKILLS.getValue(it)) }
    private fun oneHandKinds() = ONE_HAND_KINDS.filter { can(WEAPON_SKILLS.getValue(it)) }

    /** The kinds the class's ranged or relic slot takes (empty: none). */
    private fun rangedSlotKinds(): List<Int> = when (classId) {
        PortTargets.PALADIN -> listOf(RELIC_LIBRAM)
        PortTargets.DRUID -> listOf(RELIC_IDOL)
        PortTargets.SHAMAN -> listOf(RELIC_TOTEM)
        PortTargets.DEATH_KNIGHT -> listOf(RELIC_SIGIL)
        PortTargets.PRIEST, PortTargets.MAGE, PortTargets.WARLOCK -> listOf(WAND).filter { can(WEAPON_SKILLS.getValue(it)) }
        else -> RANGED_KINDS.filter { can(WEAPON_SKILLS.getValue(it)) }
    }

    /** The inventory types a slot takes, as the character holds its weapons. */
    private fun slotTypes(slot: Int, hands: GearHands): List<Int> = when (slot) {
        PortSlots.HEAD -> listOf(InventoryTypes.HEAD)
        PortSlots.NECK -> listOf(InventoryTypes.NECK)
        PortSlots.SHOULDERS -> listOf(InventoryTypes.SHOULDERS)
        PortSlots.SHIRT -> listOf(InventoryTypes.BODY)
        PortSlots.CHEST -> listOf(InventoryTypes.CHEST, InventoryTypes.ROBE)
        PortSlots.WAIST -> listOf(InventoryTypes.WAIST)
        PortSlots.LEGS -> listOf(InventoryTypes.LEGS)
        PortSlots.FEET -> listOf(InventoryTypes.FEET)
        PortSlots.WRISTS -> listOf(InventoryTypes.WRISTS)
        PortSlots.HANDS -> listOf(InventoryTypes.HANDS)
        PortSlots.FINGER1, PortSlots.FINGER2 -> listOf(InventoryTypes.FINGER)
        PortSlots.TRINKET1, PortSlots.TRINKET2 -> listOf(InventoryTypes.TRINKET)
        PortSlots.BACK -> listOf(InventoryTypes.CLOAK)
        PortSlots.TABARD -> listOf(InventoryTypes.TABARD)
        PortSlots.MAIN_HAND -> if (hands == GearHands.TWO_HAND) listOf(InventoryTypes.TWO_HAND) else listOf(InventoryTypes.WEAPON, InventoryTypes.MAIN_HAND)
        PortSlots.OFF_HAND -> when (hands) {
            GearHands.DUAL_WIELD -> listOf(InventoryTypes.WEAPON, InventoryTypes.OFF_HAND)
            GearHands.ONE_HAND_SHIELD -> listOf(InventoryTypes.SHIELD)
            GearHands.ONE_HAND_HOLDABLE -> listOf(InventoryTypes.HOLDABLE)
            else -> emptyList()
        }
        PortSlots.RANGED -> listOf(InventoryTypes.RANGED, InventoryTypes.RANGED_RIGHT, InventoryTypes.THROWN, InventoryTypes.RELIC)
        else -> emptyList()
    }

    /**
     * Whether [item] goes in [slot] for this character: its inventory type, and the kind of armour or weapon. Chosen
     * armour is the best kind the character wears; the retail item itself ([exact]) may be any kind it can wear.
     */
    private fun fitsSlot(item: ItemTemplate, slot: Int, hands: GearHands, exact: Boolean = false): Boolean {
        if (item.inventoryType !in slotTypes(slot, hands)) return false
        return when (slot) {
            PortSlots.HEAD, PortSlots.SHOULDERS, PortSlots.CHEST, PortSlots.WAIST, PortSlots.LEGS, PortSlots.FEET, PortSlots.WRISTS, PortSlots.HANDS ->
                item.itemClass == StatWeights.ITEM_ARMOR && (if (exact) item.subclass in 1..4 else item.subclass == armorSubclass)
            PortSlots.BACK -> item.itemClass == StatWeights.ITEM_ARMOR && item.subclass == 1
            PortSlots.NECK, PortSlots.FINGER1, PortSlots.FINGER2, PortSlots.TRINKET1, PortSlots.TRINKET2, PortSlots.SHIRT, PortSlots.TABARD ->
                item.itemClass == StatWeights.ITEM_ARMOR && item.subclass == 0
            PortSlots.MAIN_HAND -> item.itemClass == StatWeights.ITEM_WEAPON &&
                item.subclass in (if (hands == GearHands.TWO_HAND) twoHandKinds() else oneHandKinds())
            PortSlots.OFF_HAND -> when (hands) {
                GearHands.DUAL_WIELD -> item.itemClass == StatWeights.ITEM_WEAPON && item.subclass in oneHandKinds()
                GearHands.ONE_HAND_SHIELD -> item.itemClass == StatWeights.ITEM_ARMOR && item.subclass == 6
                GearHands.ONE_HAND_HOLDABLE -> item.itemClass == StatWeights.ITEM_ARMOR && item.subclass == 0
                else -> false
            }
            PortSlots.RANGED -> {
                val kinds = rangedSlotKinds()
                if (item.inventoryType == InventoryTypes.RELIC) item.itemClass == StatWeights.ITEM_ARMOR && item.subclass in kinds
                else item.itemClass == StatWeights.ITEM_WEAPON && item.subclass in kinds
            }
            else -> false
        }
    }

    private fun looksUnreal(item: ItemTemplate): Boolean = isUnreal(item.name)

    // ---- the weapon configuration

    private fun isRangedWeapon(piece: PortEquipment): Boolean {
        val type = InventoryTypes.of(piece.inventoryType)
        if (type == InventoryTypes.RANGED || type == InventoryTypes.RANGED_RIGHT || type == InventoryTypes.THROWN) return true
        return piece.itemClass == StatWeights.ITEM_WEAPON && piece.itemSubclass in setOf(BOW, GUN, CROSSBOW, WAND, THROWN)
    }

    private fun retailHands(main: PortEquipment?, off: PortEquipment?): GearHands? {
        if (main == null) return null
        val mainType = InventoryTypes.of(main.inventoryType)
        val twoHanded = mainType == InventoryTypes.TWO_HAND || (main.itemClass == StatWeights.ITEM_WEAPON && main.itemSubclass in TWO_HAND_KINDS)
        if (twoHanded) return GearHands.TWO_HAND
        val offType = off?.let { InventoryTypes.of(it.inventoryType) }
        return when {
            off == null -> GearHands.ONE_HAND
            offType == InventoryTypes.SHIELD || (off.itemClass == StatWeights.ITEM_ARMOR && off.itemSubclass == 6) -> GearHands.ONE_HAND_SHIELD
            offType == InventoryTypes.HOLDABLE -> GearHands.ONE_HAND_HOLDABLE
            else -> GearHands.DUAL_WIELD
        }
    }

    private fun feasible(hands: GearHands): Boolean = when (hands) {
        GearHands.TWO_HAND -> twoHandKinds().isNotEmpty()
        GearHands.ONE_HAND, GearHands.ONE_HAND_HOLDABLE -> oneHandKinds().isNotEmpty()
        GearHands.DUAL_WIELD -> oneHandKinds().isNotEmpty() && canDualWield()
        GearHands.ONE_HAND_SHIELD -> oneHandKinds().isNotEmpty() && can(SKILL_SHIELD)
    }

    /** How the class holds its weapons when retail's way isn't open to it. */
    private fun natural(): GearHands {
        val wanted = when (classId) {
            PortTargets.WARRIOR -> if (role == PortRole.TANK) GearHands.ONE_HAND_SHIELD else GearHands.TWO_HAND
            PortTargets.PALADIN -> if (role == PortRole.DAMAGE) GearHands.TWO_HAND else GearHands.ONE_HAND_SHIELD
            PortTargets.SHAMAN -> GearHands.ONE_HAND_SHIELD
            PortTargets.ROGUE -> GearHands.DUAL_WIELD
            PortTargets.DEATH_KNIGHT, PortTargets.HUNTER, PortTargets.DRUID -> GearHands.TWO_HAND
            else -> GearHands.TWO_HAND
        }
        return listOf(wanted, GearHands.TWO_HAND, GearHands.ONE_HAND_SHIELD, GearHands.ONE_HAND_HOLDABLE, GearHands.ONE_HAND).firstOrNull(::feasible) ?: GearHands.ONE_HAND
    }

    private fun chooseHands(main: PortEquipment?, off: PortEquipment?): Pair<GearHands, String> {
        val retail = retailHands(main, off)
        if (retail != null && feasible(retail)) return retail to "as in retail (${describe(retail)})"
        val natural = natural()
        val why = if (retail == null) "the class's own way (${describe(natural)})"
        else "retail's ${describe(retail)} isn't open to this class at this level: ${describe(natural)} instead"
        return natural to why
    }

    private fun describe(hands: GearHands) = when (hands) {
        GearHands.TWO_HAND -> "a two-handed weapon"
        GearHands.ONE_HAND -> "a one-handed weapon"
        GearHands.DUAL_WIELD -> "two weapons"
        GearHands.ONE_HAND_SHIELD -> "a weapon and a shield"
        GearHands.ONE_HAND_HOLDABLE -> "a weapon and an off-hand item"
    }

    companion object {
        /** Retail item names and this game's are compared without case and punctuation ("Tabard of the Argent Crusade"). */
        fun sameName(a: String, b: String): Boolean = norm(a) == norm(b)

        /** Names the game's data uses for items no player gets: tests, placeholders, deprecated and NPC-only ones. */
        fun isUnreal(name: String): Boolean = UNREAL.any { it.containsMatchIn(name) }
        private fun norm(s: String) = s.lowercase().filter { it.isLetterOrDigit() }

        const val SKILL_DUAL_WIELD = 118
        const val SKILL_SHIELD = 433
        const val SPELL_DUAL_WIELD = 674
        /** 3.3.5a's heirlooms scale to 80 (ScalingStatDistribution's MaxLevel; the core's DEFAULT_MAX_LEVEL). */
        const val HEIRLOOM_MAX_LEVEL = 80

        const val BOW = 2
        const val GUN = 3
        const val THROWN = 16
        const val CROSSBOW = 18
        const val WAND = 19
        const val RELIC_LIBRAM = 7
        const val RELIC_IDOL = 8
        const val RELIC_TOTEM = 9
        const val RELIC_SIGIL = 10

        /** Item::GetSkill's tables: a weapon's subclass to its skill (the core's item_weapon_skills), an armour's. */
        val WEAPON_SKILLS = mapOf(0 to 44, 1 to 172, 2 to 45, 3 to 46, 4 to 54, 5 to 160, 6 to 229, 7 to 43, 8 to 55, 10 to 136, 13 to 473, 15 to 173, 16 to 176, 18 to 226, 19 to 228)
        val ARMOR_SKILLS = mapOf(1 to 415, 2 to 414, 3 to 413, 4 to 293, 6 to 433)

        val TWO_HAND_KINDS = listOf(1, 5, 6, 8, 10)
        val ONE_HAND_KINDS = listOf(0, 4, 7, 13, 15)
        val RANGED_KINDS = listOf(BOW, GUN, CROSSBOW, THROWN)

        private val UNREAL = listOf(
            Regex("\\bTEST\\b"), Regex("^Test\\b"), Regex("\\bTest\\b"), Regex("\\[PH]"), Regex("\\bPH\\b"), Regex("(?i)deprecated"),
            Regex("\\(old\\)"), Regex("\\bOLD\\b"), Regex("^zz"), Regex("^Monster - "), Regex("\\bQA\\b"), Regex("\\bDEV\\b"), Regex("(?i)\\bunused\\b"),
            Regex("\\bDND\\b"), Regex("(?i)^NPC "), Regex("(?i)placeholder"),
        )
    }
}
