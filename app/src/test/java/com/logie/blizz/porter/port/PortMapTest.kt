package com.logie.blizz.porter.port

import com.logie.blizz.porter.port.PortTestData.table
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class PortMapTest {
    private fun bit(field: List<Int>, index: Int) = field[index / 32] and (1 shl (index % 32)) != 0

    private val data = RealmData.of(mapOf(
        "WorldMapArea" to table("WorldMapArea",
            mapOf(0 to 1, 1 to 0, 2 to 12, 4 to 0, 5 to 0, 6 to 0, 7 to 0, 8 to -1),
            mapOf(0 to 2, 1 to 530, 2 to 3430, 4 to 0, 5 to 0, 6 to 0, 7 to 0, 8 to 0),
            mapOf(0 to 3, 1 to 530, 2 to 3483, 4 to 0, 5 to 0, 6 to 0, 7 to 0, 8 to -1),
            mapOf(0 to 4, 1 to 571, 2 to 495, 4 to 0, 5 to 0, 6 to 0, 7 to 0, 8 to -1),
        ),
        "AreaTable" to table("AreaTable",
            mapOf(0 to 12, 1 to 0, 2 to 0, 3 to 5, 10 to 0, 11 to "Elwynn Forest"),
            mapOf(0 to 87, 1 to 0, 2 to 12, 3 to 40, 10 to 0, 11 to "Goldshire"),
            mapOf(0 to 3430, 1 to 530, 2 to 0, 3 to 100, 10 to 0, 11 to "Eversong Woods"),
            mapOf(0 to 3483, 1 to 530, 2 to 0, 3 to 200, 10 to 0, 11 to "Hellfire Peninsula"),
            mapOf(0 to 495, 1 to 571, 2 to 0, 3 to 300, 10 to 0, 11 to "Howling Fjord"),
            mapOf(0 to 876, 1 to 1, 2 to 0, 3 to 400, 10 to 0, 11 to "GM Island"),
        ),
        "TaxiNodes" to table("TaxiNodes",
            mapOf(0 to 2, 1 to 0, 2 to 0, 3 to 0, 22 to 0, 23 to 541),
            mapOf(0 to 23, 1 to 1, 2 to 0, 3 to 0, 22 to 2224, 23 to 0),
            mapOf(0 to 82, 1 to 530, 2 to 0, 3 to 0, 22 to 19917, 23 to 0),
            mapOf(0 to 99, 1 to 530, 2 to 0, 3 to 0, 22 to 2224, 23 to 0),
            mapOf(0 to 100, 1 to 530, 2 to 0, 3 to 0, 22 to 0, 23 to 541),
            mapOf(0 to 315, 1 to 0, 2 to 0, 3 to 0, 22 to 32981, 23 to 0),
            mapOf(0 to 5, 1 to 0, 2 to 0, 3 to 0, 22 to 0, 23 to 541),
        ),
        "TaxiPath" to table("TaxiPath", mapOf(0 to 1, 1 to 5, 2 to 2, 3 to 0), mapOf(0 to 2, 1 to 2, 2 to 6, 3 to 10)),
        "Spell" to table("Spell", PortTestData.spell(31606, "Flight Path", effects = listOf(SpellEffect(123, 0, 1, 0, 0, 0)))),
    ))

    @Test fun aCharacterHasExploredTheContinentsItsLevelOpens() {
        assertEquals(emptySet<PortMap.Continent>(), PortMap.continents(9))
        assertEquals(setOf(PortMap.Continent.OLD_WORLD), PortMap.continents(19))
        assertEquals(setOf(PortMap.Continent.OLD_WORLD, PortMap.Continent.OUTLAND), PortMap.continents(60))
        assertEquals(PortMap.Continent.entries.toSet(), PortMap.continents(80))

        val old = PortMap.exploredZones(data, PortMap.continents(19))
        assertEquals(PortMap.EXPLORED_SIZE, old.size)
        // Elwynn, Goldshire in it, and Eversong (Outland's map, shown on the Eastern Kingdoms').
        assertTrue(bit(old, 5) && bit(old, 40) && bit(old, 100))
        assertTrue(!bit(old, 200) && !bit(old, 300))
        assertTrue("GM Island is on no map", !bit(old, 400))
        val all = PortMap.exploredZones(data, PortMap.continents(80))
        assertTrue(bit(all, 200) && bit(all, 300))
        assertTrue(PortMap.exploredZones(data, emptySet()).all { it == 0 })
    }

    @Test fun itKnowsItsSidesFlightPathsThere() {
        val alliance = PortMap.taxiMask(data, PortFaction.ALLIANCE, PortMap.continents(19))
        assertEquals(PortMap.TAXI_SIZE, alliance.size)
        assertTrue(bit(alliance, 2 - 1))
        assertTrue("the Horde's", !bit(alliance, 23 - 1))
        assertTrue("Outland's", !bit(alliance, 100 - 1))
        assertTrue("only a spell's path leaves it", !bit(alliance, 5 - 1))
        val horde = PortMap.taxiMask(data, PortFaction.HORDE, PortMap.continents(80))
        assertTrue(bit(horde, 23 - 1) && bit(horde, 82 - 1) && bit(horde, 99 - 1))
        assertTrue("the death knights' own", !bit(horde, 315 - 1))
        assertTrue(!bit(horde, 2 - 1))
    }
}
