package com.logie.blizz.porter.port

import com.logie.blizz.porter.port.PortTestData.item
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class PortGearTest {
    private val PLATE = 4
    private val ARMOR = 4
    private val WEAPON = 2
    private val stamina = 7
    private val strength = 4
    private val agility = 3
    private val intellect = 5

    /** A human warrior's skills at 80 (plate, mail, shields, swords both kinds, dual wield, guns) or what [extra] says. */
    private fun warriorSkills(extra: Map<Int, Int> = emptyMap()) = mapOf(293 to 1, 413 to 1, 414 to 1, 415 to 1, 433 to 1, 43 to 400, 55 to 400, 118 to 400, 46 to 400, 176 to 400) + extra

    private fun planner(items: List<ItemTemplate>, role: PortRole = PortRole.TANK, classId: Int = 1, level: Int = 80, tier: GearTier = GearTier.FRESH,
                        skills: Map<Int, Int> = warriorSkills(), side: PortFaction = PortFaction.ALLIANCE, unobtainable: Set<Int> = setOf(109),
                        equipStats: (Int) -> List<Pair<Int, Int>> = { emptyList() }) =
        GearPlanner(PortTestData.ListItemSource(items, unobtainable), GearRules(1, classId, level, side, tier), StatWeights.of(classId, role, null), role,
            skills, emptySet(), { null }, emptySet(), equipStats)

    private fun retail(slot: String, id: Int, name: String, type: String, itemClass: Int = ARMOR, subclass: Int = PLATE, transmog: Int? = null) =
        PortEquipment(slot, id, name, "EPIC", 690, type, itemClass, subclass, transmog)

    private val helms = listOf(
        item(100, "Strong Helm", ARMOR, PLATE, InventoryTypes.HEAD, itemLevel = 200, requiredLevel = 80, stats = listOf(stamina to 50)),
        item(101, "Stout Helm", ARMOR, PLATE, InventoryTypes.HEAD, itemLevel = 187, requiredLevel = 80, stats = listOf(stamina to 60)),
        item(102, "Mail Helm", ARMOR, 3, InventoryTypes.HEAD, itemLevel = 200, requiredLevel = 80, stats = listOf(stamina to 90)),
        item(103, "Old Helm", ARMOR, PLATE, InventoryTypes.HEAD, itemLevel = 66, requiredLevel = 60, stats = listOf(stamina to 20)),
        item(104, "Horde Helm", ARMOR, PLATE, InventoryTypes.HEAD, itemLevel = 200, requiredLevel = 80, stats = listOf(stamina to 99), flagsExtra = ItemTemplate.EXTRA_HORDE_ONLY),
        item(105, "Priest Helm", ARMOR, PLATE, InventoryTypes.HEAD, itemLevel = 200, requiredLevel = 80, stats = listOf(stamina to 99), allowableClass = 16),
        item(106, "Lucky Helm", ARMOR, PLATE, InventoryTypes.HEAD, itemLevel = 200, requiredLevel = 80, stats = listOf(stamina to 99), randomProperty = 5),
        item(107, "Raid Helm", ARMOR, PLATE, InventoryTypes.HEAD, quality = 4, itemLevel = 264, requiredLevel = 80, stats = listOf(stamina to 150)),
        item(108, "Test Helm TEST", ARMOR, PLATE, InventoryTypes.HEAD, itemLevel = 200, requiredLevel = 80, stats = listOf(stamina to 99)),
        item(109, "Lost Helm", ARMOR, PLATE, InventoryTypes.HEAD, itemLevel = 200, requiredLevel = 80, stats = listOf(stamina to 99)),
    )

    @Test fun theBestOfTheSlotForTheRoleOfTheBestArmourItWears() {
        val result = planner(helms).plan(listOf(retail("head", 230000, "Helm of Midnight", "HEAD")))
        val head = result.choices.single { it.slot == PortSlots.HEAD }
        // Not the mail one (plate is what it wears), not the other side's, another class's, a random enchantment's, a test's, nor one nobody gets.
        assertEquals(101, head.item!!.entry)
        assertEquals(GearHow.REPLACEMENT, head.how)
        assertTrue(head.why, head.why.contains("this game has no item 230000"))
    }

    @Test fun theRetailItemItselfWhenTheRealmHasItAndItCanBeWorn() {
        val head = planner(helms).plan(listOf(retail("head", 103, "Old Helm", "HEAD"))).choices.single { it.slot == PortSlots.HEAD }
        assertEquals(103, head.item!!.entry)
        assertEquals(GearHow.EXACT, head.how)
        // The same id as another item of this realm isn't the same item.
        val other = planner(helms).plan(listOf(retail("head", 103, "Helm of Something Else", "HEAD"))).choices.single { it.slot == PortSlots.HEAD }
        assertEquals(101, other.item!!.entry)
        assertTrue(other.why, other.why.contains("is another item here"))
    }

    @Test fun itsLookWhenTheRealmHasThatItemWithinTheLimits() {
        val look = planner(helms).plan(listOf(retail("head", 230000, "Helm of Midnight", "HEAD", transmog = 100))).choices.single { it.slot == PortSlots.HEAD }
        assertEquals(100, look.item!!.entry)
        assertEquals(GearHow.TRANSMOG, look.how)
        // A look beyond the tier: the best within it instead, and why.
        val raid = planner(helms).plan(listOf(retail("head", 230000, "Helm of Midnight", "HEAD", transmog = 107))).choices.single { it.slot == PortSlots.HEAD }
        assertEquals(101, raid.item!!.entry)
        assertTrue(raid.why, raid.why.contains("its look, Raid Helm, is outside"))
        val best = planner(helms, tier = GearTier.BEST).plan(listOf(retail("head", 230000, "Helm of Midnight", "HEAD", transmog = 107))).choices.single { it.slot == PortSlots.HEAD }
        assertEquals(107, best.item!!.entry)
    }

    @Test fun ringsAndTrinketsAreNotWornTwice() {
        val rings = listOf(
            item(200, "Band of Might", ARMOR, 0, InventoryTypes.FINGER, itemLevel = 200, requiredLevel = 80, stats = listOf(stamina to 60), maxCount = 1),
            item(201, "Band of Lesser Might", ARMOR, 0, InventoryTypes.FINGER, itemLevel = 200, requiredLevel = 80, stats = listOf(stamina to 40)),
        )
        val choices = planner(rings).plan(listOf(retail("leftFinger", 230001, "A", "FINGER", subclass = 0), retail("rightFinger", 230002, "B", "FINGER", subclass = 0))).choices
        assertEquals(listOf(200, 201), choices.filter { it.slot == PortSlots.FINGER1 || it.slot == PortSlots.FINGER2 }.map { it.item!!.entry })
    }

    private val weapons = listOf(
        item(300, "Great Sword", WEAPON, 8, InventoryTypes.TWO_HAND, itemLevel = 200, requiredLevel = 80, stats = listOf(strength to 80), damage = 500f to 700f, delay = 3600),
        item(301, "Long Sword", WEAPON, 7, InventoryTypes.WEAPON, itemLevel = 200, requiredLevel = 80, stats = listOf(strength to 40), damage = 300f to 400f, delay = 2600),
        item(302, "Short Sword", WEAPON, 7, InventoryTypes.WEAPON, itemLevel = 190, requiredLevel = 80, stats = listOf(strength to 30), damage = 250f to 350f, delay = 2600),
        item(303, "Tower Shield", ARMOR, 6, InventoryTypes.SHIELD, itemLevel = 200, requiredLevel = 80, stats = listOf(stamina to 50), armor = 6000),
        item(304, "Orb", ARMOR, 0, InventoryTypes.HOLDABLE, itemLevel = 200, requiredLevel = 80, stats = listOf(intellect to 30)),
        item(305, "Rifle", WEAPON, 3, InventoryTypes.RANGED_RIGHT, itemLevel = 200, requiredLevel = 80, stats = listOf(agility to 30), damage = 300f to 500f, delay = 2800),
        item(306, "Throwing Axe", WEAPON, 16, InventoryTypes.THROWN, itemLevel = 190, requiredLevel = 80, stats = listOf(stamina to 20), damage = 100f to 150f, delay = 1900),
        item(307, "Great Axe", WEAPON, 1, InventoryTypes.TWO_HAND, itemLevel = 200, requiredLevel = 80, stats = listOf(agility to 70), damage = 500f to 700f, delay = 3600),
        item(308, "Argent Tabard", ARMOR, 0, InventoryTypes.TABARD, quality = 1, itemLevel = 1, requiredLevel = 0, requiredRep = 1106 to 5),
        item(309, "Guild Tabard", ARMOR, 0, InventoryTypes.TABARD, quality = 1, itemLevel = 1, requiredLevel = 0),
    )

    @Test fun theRetailWeaponConfigurationIsKeptWhereTheClassCanHoldIt() {
        val twoHanded = planner(weapons, role = PortRole.DAMAGE).plan(listOf(retail("weapon", 230010, "Voidglass Executioner", "TWOHWEAPON", WEAPON, 8)))
        assertEquals(GearHands.TWO_HAND, twoHanded.hands)
        assertEquals(300, twoHanded.choices.single { it.slot == PortSlots.MAIN_HAND }.item!!.entry)
        assertTrue(twoHanded.choices.none { it.slot == PortSlots.OFF_HAND })

        val shield = planner(weapons).plan(listOf(retail("weapon", 230011, "Kris", "WEAPON", WEAPON, 7), retail("offhand", 230012, "Bulwark", "SHIELD", ARMOR, 6)))
        assertEquals(GearHands.ONE_HAND_SHIELD, shield.hands)
        assertEquals(301, shield.choices.single { it.slot == PortSlots.MAIN_HAND }.item!!.entry)
        assertEquals(303, shield.choices.single { it.slot == PortSlots.OFF_HAND }.item!!.entry)

        val dual = planner(weapons, role = PortRole.DAMAGE).plan(listOf(retail("weapon", 230013, "A", "WEAPONMAINHAND", WEAPON, 9), retail("offhand", 230014, "B", "WEAPONOFFHAND", WEAPON, 9)))
        assertEquals(GearHands.DUAL_WIELD, dual.hands)
        val hands = dual.choices.filter { it.slot == PortSlots.MAIN_HAND || it.slot == PortSlots.OFF_HAND }.map { it.item!!.entry }
        assertEquals(listOf(301, 302), hands)
    }

    @Test fun aConfigurationTheClassCantHoldBecomesItsOwn() {
        // Two weapons without Dual Wield (a shaman's comes from a talent the porter doesn't spend): a weapon and a shield.
        val noDualWield = planner(weapons, skills = warriorSkills() - 118, role = PortRole.DAMAGE)
            .plan(listOf(retail("weapon", 230013, "A", "WEAPON", WEAPON, 7), retail("offhand", 230014, "B", "WEAPON", WEAPON, 7)))
        assertNotEquals(GearHands.DUAL_WIELD, noDualWield.hands)
        assertTrue(noDualWield.handsWhy, noDualWield.handsWhy.contains("isn't open to this class"))
        // A shield without the shield skill: the class's own way.
        val noShield = planner(weapons, skills = warriorSkills() - 433).plan(listOf(retail("weapon", 230011, "Kris", "WEAPON", WEAPON, 7), retail("offhand", 230012, "Bulwark", "SHIELD", ARMOR, 6)))
        assertNotEquals(GearHands.ONE_HAND_SHIELD, noShield.hands)
    }

    @Test fun aHuntersRetailBowOrGunIsItsRangedSlotWithAMeleeWeaponBeside() {
        val hunterSkills = mapOf(413 to 1, 414 to 1, 415 to 1, 46 to 300, 45 to 300, 172 to 300, 43 to 300, 118 to 300)
        val result = planner(weapons, role = PortRole.DAMAGE, classId = 3, skills = hunterSkills).plan(listOf(retail("weapon", 230020, "Voidglass Hand Cannon", "RANGEDRIGHT", WEAPON, 3)))
        assertEquals(305, result.choices.single { it.slot == PortSlots.RANGED }.item!!.entry)
        assertEquals(GearHow.REPLACEMENT, result.choices.single { it.slot == PortSlots.RANGED }.how)
        assertEquals(307, result.choices.single { it.slot == PortSlots.MAIN_HAND }.item!!.entry)
        assertEquals(GearHands.TWO_HAND, result.hands)
    }

    @Test fun theClassesRangedOrRelicSlotIsFilledThoughRetailHasNone() {
        val result = planner(weapons, role = PortRole.DAMAGE).plan(listOf(retail("weapon", 230010, "Executioner", "TWOHWEAPON", WEAPON, 8)))
        val ranged = result.choices.single { it.slot == PortSlots.RANGED }
        assertEquals(GearHow.ADDED, ranged.how)
        assertTrue(ranged.item!!.entry in setOf(305, 306))
    }

    @Test fun aTabardIsTheVeryOneOrNone() {
        val kept = planner(weapons).plan(listOf(retail("tabard", 309, "Guild Tabard", "TABARD", subclass = 0))).choices.single { it.slot == PortSlots.TABARD }
        assertEquals(GearHow.EXACT, kept.how)
        val asked = planner(weapons).plan(listOf(retail("tabard", 308, "Argent Tabard", "TABARD", subclass = 0))).choices.single { it.slot == PortSlots.TABARD }
        assertNull(asked.item)
        assertTrue(asked.why, asked.why.contains("needs a reputation"))
    }

    @Test fun anItemsEquipSpellsCountForItsRole() {
        val trinkets = listOf(
            item(400, "Fighter's Charm", ARMOR, 0, InventoryTypes.TRINKET, itemLevel = 200, requiredLevel = 80, stats = listOf(31 to 30)),
            item(401, "Mage's Charm", ARMOR, 0, InventoryTypes.TRINKET, itemLevel = 200, requiredLevel = 80, equipSpells = listOf(9001)),
        )
        val data = PortTestData.realmData()
        val caster = planner(trinkets, role = PortRole.DAMAGE, classId = 8, skills = mapOf(415 to 1), equipStats = data::equipStats)
        // (a mage: weights are a caster's; StatWeights.of reads the class)
        val chosen = GearPlanner(PortTestData.ListItemSource(trinkets), GearRules(1, 8, 80, PortFaction.ALLIANCE, GearTier.FRESH), StatWeights.of(8, PortRole.DAMAGE, PortStat.INTELLECT),
            PortRole.DAMAGE, mapOf(415 to 1), emptySet(), { null }, emptySet(), data::equipStats).plan(listOf(retail("leftTrinket", 230030, "Voidcore", "TRINKET", subclass = 0)))
        assertEquals(401, chosen.choices.single { it.slot == PortSlots.TRINKET1 }.item!!.entry)
        // Without reading its spell, the hit rating looked better.
        val blind = GearPlanner(PortTestData.ListItemSource(trinkets), GearRules(1, 8, 80, PortFaction.ALLIANCE, GearTier.FRESH), StatWeights.of(8, PortRole.DAMAGE, PortStat.INTELLECT),
            PortRole.DAMAGE, mapOf(415 to 1), emptySet(), { null }, emptySet()).plan(listOf(retail("leftTrinket", 230030, "Voidcore", "TRINKET", subclass = 0)))
        assertEquals(400, blind.choices.single { it.slot == PortSlots.TRINKET1 }.item!!.entry)
        assertTrue(caster.problem(trinkets[0]) == null)
    }

    @Test fun itemLevelsAreBoundedAtEveryLevelEvenForItemsThatAskNone() {
        assertEquals(12, GearRules(1, 1, 4, PortFaction.ALLIANCE, GearTier.FRESH).maxItemLevel)
        assertEquals(200, GearRules(1, 1, 80, PortFaction.ALLIANCE, GearTier.FRESH).maxItemLevel)
        assertEquals(284, GearRules(1, 1, 80, PortFaction.ALLIANCE, GearTier.BEST).maxItemLevel)
        assertEquals(125, GearRules(1, 1, 70, PortFaction.ALLIANCE, GearTier.RAID).maxItemLevel)
        assertEquals(63, GearRules(1, 1, 60, PortFaction.ALLIANCE, GearTier.FRESH).maxItemLevel)
        assertEquals(155, GearRules(1, 1, 75, PortFaction.ALLIANCE, GearTier.FRESH).maxItemLevel)
        val quest = item(500, "Quest Reward Helm", ARMOR, PLATE, InventoryTypes.HEAD, itemLevel = 187, requiredLevel = 0, stats = listOf(stamina to 99))
        val low = item(501, "Small Helm", ARMOR, 3, InventoryTypes.HEAD, quality = 2, itemLevel = 10, requiredLevel = 2, stats = listOf(stamina to 3))
        val choice = planner(listOf(quest, low), level = 4, skills = mapOf(413 to 1, 414 to 1, 415 to 1)).plan(listOf(retail("head", 230000, "Helm", "HEAD", subclass = 3)))
        assertEquals(501, choice.choices.single { it.slot == PortSlots.HEAD }.item!!.entry)
        val sql = GearRules(1, 1, 4, PortFaction.ALLIANCE, GearTier.FRESH).sqlFilter(setOf(1), wide = false)
        assertTrue(sql, sql.contains("ItemLevel <= 12") && sql.contains("(FlagsExtra & 1) = 0") && sql.contains("(AllowableRace & 1) <> 0"))
    }
}
