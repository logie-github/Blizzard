package com.logie.blizz.porter.port

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class PortSpellsTest {
    private val data = PortTestData.realmData()
    private val world = PortTestData.realmWorld()

    private fun book(level: Int, race: Int = 1, classId: Int = 1) = SpellBook(data, world, race, classId, level).also { it.learnClass() }

    @Test fun aWarriorLearnsItsTrainersQuestsWeaponsAndRidingUpToItsLevel() {
        val book = book(80)
        for (spell in listOf(71, 355, 7386, 284, 750, 674, 202, 33388, 33391)) assertTrue("knows $spell", book.knows(spell))
        assertEquals(SpellSource.QUEST, book.learned[71])
        assertEquals(SpellSource.CLASS_TRAINER, book.learned[284])
        assertEquals(SpellSource.WEAPON_MASTER, book.learned[202])
        assertEquals(SpellSource.RIDING, book.learned[33391])
        // Plate (750 gives skill 293), Dual Wield (674: 118), Two-Handed Swords (202: 55), riding 150.
        assertEquals(SkillValue(1, 1), book.skills[293])
        assertEquals(SkillValue(400, 400), book.skills[118])
        assertEquals(SkillValue(400, 400), book.skills[55])
        assertEquals(SkillValue(150, 150), book.skills[762])
        assertEquals(SkillValue(300, 300), book.skills[98])
        assertNull("an orc's language isn't a human's", book.skills[109])
    }

    @Test fun whatTheSkillsGiveIsKnownButNotWritten() {
        val written = book(80).written()
        assertTrue(written.containsAll(listOf(71, 355, 7386, 284, 33388, 33391)))
        // Heroic Strike's first rank and Battle Stance come with Arms, Plate Mail with its skill: the core gives them at every login.
        for (given in listOf(78, 2457, 750, 674, 202, 6603)) assertFalse("$given is the skills'", given in written)
    }

    @Test fun nothingAboveTheLevelIsTaught() {
        val young = book(30, race = 2)
        assertTrue(young.knows(674))
        assertFalse(young.knows(750))
        assertNull(young.skills[293])
        assertEquals(SkillValue(75, 75), young.skills[762])
        assertFalse(young.knows(33391))
        val child = book(5)
        assertFalse(child.knows(674))
        assertFalse(child.knows(33388))
        assertNull(child.skills[762])
        assertFalse("Taunt is a level 10 quest's", child.knows(355))
        assertEquals(SkillValue(25, 25), child.skills[43])
    }

    @Test fun aNextRankIsTaughtOnlyAfterTheOneBefore() {
        val book = SpellBook(data, world, 1, 1, 80)
        // (no Arms yet: Heroic Strike's first rank isn't known, so its second can't be taught)
        assertFalse(book.canTeach(world.trainerSpells.first { it.spell == 284 }))
        book.learnDefaults()
        assertTrue(book.canTeach(world.trainerSpells.first { it.spell == 284 }))
    }

    @Test fun aProfessionIsItsOldPartsCutToTheRankItsLevelAllows() {
        val book = book(80)
        val smithing = PortProfession(164, "Blacksmithing", true, listOf(PortProfessionTier("Classic Blacksmithing", 300, 300), PortProfessionTier("Outland Blacksmithing", 75, 75),
            PortProfessionTier("Northrend Blacksmithing", 40, 75), PortProfessionTier("Khaz Algar Blacksmithing", 100, 100)))
        assertEquals(415, SpellBook.professionPoints(smithing))
        val outcome = book.learnProfession(smithing, 0)
        assertNull(outcome.problem)
        // The test realm's trainers teach two ranks: Journeyman's 150 is as far as it goes.
        assertEquals(150, outcome.value)
        assertEquals(150, outcome.max)
        assertEquals(1, outcome.recipes)
        assertTrue(book.knows(2018) && book.knows(3100) && book.knows(2660))
        assertEquals(SkillValue(150, 150), book.skills[164])

        val low = book(8)
        val lowOutcome = low.learnProfession(smithing, 0)
        assertEquals(75, lowOutcome.value)
        assertFalse(low.knows(3100))
        assertNotNull(book(3).learnProfession(smithing, 0).problem)
    }

    @Test fun professionsTheGameHasntOrBeyondTwoAreRefused() {
        val book = book(80)
        assertEquals("this game has no such profession", book.learnProfession(PortProfession(794, "Archaeology", false, listOf(PortProfessionTier("Archaeology", 900))), 0).problem)
        val smithing = PortProfession(164, "Blacksmithing", true, listOf(PortProfessionTier("Classic Blacksmithing", 100)))
        assertNotNull(book.learnProfession(smithing, 2).problem)
        assertNotNull(book.learnProfession(PortProfession(164, "Blacksmithing", true, listOf(PortProfessionTier("Dragon Isles Blacksmithing", 100))), 0).problem)
    }

    @Test fun mountsGoByTheirSpellOrNameAndTheRaceIsGivenWhatItLacks() {
        val book = book(80)
        val outcomes = book.learnMounts(listOf(PortMount(6, "Brown Horse"), PortMount(1792, "Algarian Stormrider"), PortMount(363, "Invincible", spellId = 72286)), PortFaction.ALLIANCE)
        assertEquals(458, outcomes[0].spell)
        assertNull(outcomes[1].spell)
        assertEquals(72286, outcomes[2].spell)
        // Invincible flies and runs: nothing more is given.
        assertEquals(3, outcomes.size)

        val walker = book(60)
        val given = walker.learnMounts(listOf(PortMount(6, "Brown Horse")), PortFaction.ALLIANCE)
        assertEquals(listOf(458, 32235), given.map { it.spell })
        assertNull(given[1].mount)

        val nothing = book(60).learnMounts(emptyList(), PortFaction.ALLIANCE)
        assertEquals(listOf(458, 23229, 32235), nothing.map { it.spell })
        assertTrue(book(15).learnMounts(emptyList(), PortFaction.ALLIANCE).isEmpty())
    }

    @Test fun flyingAndGroundMountsAreToldApart() {
        assertTrue(data.isGroundMount(458))
        assertFalse(data.isFlyingMount(458))
        assertTrue(data.isFlyingMount(32235))
        assertFalse("a flying mount can't be ridden in Azeroth", data.isGroundMount(32235))
        assertTrue(data.isScalingMount(72286))
        assertTrue(data.isFlyingMount(72286) && data.isGroundMount(72286))
    }

    @Test fun equipSpellsCountAsTheStatsTheyGive() {
        assertEquals(listOf(45 to 30), data.equipStats(9001))
        assertTrue(data.equipStats(458).isEmpty())
    }
}
