package com.logie.blizz.porter.port

import com.logie.blizz.wow.Realm
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

class PortRulesTest {
    @get:Rule val temp = TemporaryFolder()

    @Test fun theRetailLevelIsTheSameShareOfTheRealmsCap() {
        assertEquals(80, PortLevels.scaled(90, 80))
        assertEquals(19, PortLevels.scaled(90, 19))
        assertEquals(19, PortLevels.scaled(95, 19))
        assertEquals(4, PortLevels.scaled(20, 19))
        assertEquals(1, PortLevels.scaled(1, 19))
        assertEquals(1, PortLevels.scaled(2, 19))
        assertEquals(40, PortLevels.scaled(45, 80))
        assertEquals(71, PortLevels.scaled(80, 80))
        assertEquals(1, PortLevels.scaled(0, 80))
    }

    @Test fun theArmorysSlotsAndInventoryTypesInEitherSpelling() {
        for ((armory, slot) in listOf("head" to 0, "HEAD" to 0, "shoulder" to 2, "SHOULDER" to 2, "shirt" to 3, "SHIRT" to 3, "leg" to 6, "LEGS" to 6,
            "foot" to 7, "FEET" to 7, "hand" to 9, "HANDS" to 9, "leftFinger" to 10, "FINGER_1" to 10, "rightFinger" to 11, "FINGER_2" to 11,
            "leftTrinket" to 12, "TRINKET_1" to 12, "rightTrinket" to 13, "TRINKET_2" to 13, "back" to 14, "BACK" to 14, "weapon" to 15,
            "MAIN_HAND" to 15, "offhand" to 16, "OFF_HAND" to 16, "tabard" to 18, "TABARD" to 18)) {
            assertEquals(armory, slot, PortSlots.realmSlot(armory))
        }
        assertNull(PortSlots.realmSlot("profession_tool"))
        assertEquals(InventoryTypes.TWO_HAND, InventoryTypes.of("TWOHWEAPON"))
        assertEquals(InventoryTypes.RANGED_RIGHT, InventoryTypes.of("RANGEDRIGHT"))
        assertEquals(InventoryTypes.HOLDABLE, InventoryTypes.of("HOLDABLE"))
        assertEquals(InventoryTypes.ROBE, InventoryTypes.of("ROBE"))
        assertEquals(InventoryTypes.OFF_HAND, InventoryTypes.of("WEAPONOFFHAND"))
        assertNull(InventoryTypes.of("PROFESSION_TOOL"))
    }

    @Test fun namesFollowTheRealmsRules() {
        assertEquals("Brannoc", PortNames.normalize("bRANNOC"))
        assertNull(PortNames.problem("Brannoc"))
        assertNull(PortNames.problem("Zoë"))
        assertNull(PortNames.problem("Аркадий"))
        assertNotNull(PortNames.problem("B"))
        assertNotNull(PortNames.problem("Thirteenchars"))
        assertNotNull(PortNames.problem("Xal'veth"))
        assertNotNull(PortNames.problem("Ann a"))
        assertNotNull(PortNames.problem("Zoëд"))
        assertNotNull(PortNames.problem("Baaad"))
        assertNotNull(PortNames.problem("Thegm"))
        assertNotNull(PortNames.problem("Robert'); DROP"))
        assertNotNull(PortNames.problem("Zoë", strict = 1))
    }

    private val combos = listOf(
        RaceClass(1, 1), RaceClass(1, 4), RaceClass(4, 4), RaceClass(4, 11), RaceClass(6, 11), RaceClass(6, 1), RaceClass(3, 3), RaceClass(1, 6),
        RaceClass(15, 1), RaceClass(15, 4), RaceClass(15, 6), RaceClass(16, 6), RaceClass(2, 1), RaceClass(2, 3), RaceClass(10, 8),
    )
    private val sides = mapOf(1 to PortFaction.ALLIANCE, 3 to PortFaction.ALLIANCE, 4 to PortFaction.ALLIANCE, 15 to PortFaction.ALLIANCE,
        2 to PortFaction.HORDE, 6 to PortFaction.HORDE, 10 to PortFaction.HORDE, 16 to PortFaction.HORDE)

    private fun character(race: Int, classId: Int, faction: PortFaction, role: PortRole = PortRole.DAMAGE) =
        PortCharacter("Test", race, classId, 0, faction, 90, spec = PortSpec("x", role))

    private fun suggest(c: PortCharacter, level: Int = 80) = PortTargets.suggest(c, combos, { sides[it] ?: PortFaction.NEUTRAL }, level)!!

    @Test fun aRaceAndClassTheRealmHasStayAsTheyAre() {
        val s = suggest(character(1, 1, PortFaction.ALLIANCE))
        assertEquals(1 to 1, s.race to s.classId)
        assertFalse(s.needsChoice)
    }

    @Test fun alliedRacesGoToTheRealmsOwnRaceThenToTheirKin() {
        assertEquals(15, suggest(character(29, 4, PortFaction.ALLIANCE)).race)
        val noVoidElves = PortTargets.suggest(character(29, 4, PortFaction.ALLIANCE), combos.filter { it.race != 15 }, { sides[it] ?: PortFaction.NEUTRAL }, 80)!!
        assertEquals(4 to 4, noVoidElves.race to noVoidElves.classId)
        assertEquals(16, suggest(character(27, 6, PortFaction.HORDE)).race)
        assertEquals(6, suggest(character(28, 1, PortFaction.HORDE)).race)
        assertEquals(3, suggest(character(34, 3, PortFaction.ALLIANCE)).race)
        assertEquals(2, suggest(character(36, 1, PortFaction.HORDE)).race)
    }

    @Test fun aClassWrathHasntIsProposedByItsRoleAndMarkedForTheirChoice() {
        val dh = suggest(character(29, PortTargets.DEMON_HUNTER, PortFaction.ALLIANCE))
        assertEquals(15 to PortTargets.ROGUE, dh.race to dh.classId)
        assertTrue(dh.needsChoice)
        val tank = suggest(character(4, PortTargets.DEMON_HUNTER, PortFaction.ALLIANCE, PortRole.TANK))
        assertEquals(4 to PortTargets.DRUID, tank.race to tank.classId)
        assertTrue(tank.needsChoice)
        val monk = suggest(character(6, PortTargets.MONK, PortFaction.HORDE, PortRole.HEALER))
        assertEquals(6 to PortTargets.DRUID, monk.race to monk.classId)
    }

    @Test fun aRaceWithoutKinIsTheirChoiceOnItsSide() {
        val pandaren = suggest(character(26, PortTargets.WARRIOR, PortFaction.HORDE))
        assertEquals(PortFaction.HORDE, sides[pandaren.race])
        assertEquals(PortTargets.WARRIOR, pandaren.classId)
        assertTrue(pandaren.needsChoice)
    }

    @Test fun aDeathKnightUnderTheRealmsStartIsAnotherClass() {
        val dk = suggest(character(1, PortTargets.DEATH_KNIGHT, PortFaction.ALLIANCE), level = 19)
        assertTrue(dk.classId != PortTargets.DEATH_KNIGHT)
        assertTrue(dk.needsChoice)
        assertEquals(PortTargets.DEATH_KNIGHT, suggest(character(1, PortTargets.DEATH_KNIGHT, PortFaction.ALLIANCE), level = 80).classId)
    }

    @Test fun theRealmsCapIsItsMaxLevelOrChromieCraftsProgressionCap() {
        val root = temp.newFolder("files")
        File(root, "etc/modules").mkdirs()
        File(root, "etc/worldserver.conf").writeText("# a comment\nMaxPlayerLevel = 80\nDataDir = \"${root.path}/data-modules\"\nCharactersPerRealm = 10\n")
        File(root, "etc/modules/chromie-xp.conf").writeText("[worldserver]\nChromie.Stable.MaxPlayerLevel = 19\n")
        File(root, "data/dbc").mkdirs()
        val files = RealmFiles(root, PortRealm.of(Realm.CHROMIE)!!)
        assertEquals(LevelCap(80, 19, 55), files.levelCap())
        assertEquals(19, files.levelCap().effective)
        // DataDir names a folder that isn't there: the realm's data.
        assertEquals(File(root, "data/dbc"), files.dbcDir())
        File(root, "data-modules/dbc").mkdirs()
        assertEquals(File(root, "data-modules/dbc"), RealmFiles(root, PortRealm.of(Realm.CHROMIE)!!).dbcDir())
        val remix = RealmFiles(root, PortRealm.of(Realm.REMIX)!!)
        assertEquals(80, remix.levelCap().max)
        assertNull(PortRealm.of(Realm.OCTO))
        assertEquals("acore_characters_wrathpp", PortRealm.of(Realm.WRATHPP)!!.charactersDb)
    }
}
