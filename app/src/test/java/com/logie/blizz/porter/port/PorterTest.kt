package com.logie.blizz.porter.port

import com.logie.blizz.porter.port.PortTestData.DbcWriter
import com.logie.blizz.porter.port.PortTestData.item
import com.logie.blizz.wow.Realm
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder
import java.io.File

/**
 * The porter's plan and its SQL against a hand-made realm: the database's answers canned ([PortTestData.FakeRealmDb]),
 * its client data made in memory. What it reads, what it decides, what it refuses, and the script it runs.
 */
class PorterTest {
    @get:Rule val temp = TemporaryFolder()

    private val ARMOR = 4
    private val items = listOf(
        item(6948, "Hearthstone", 15, 0, 0, quality = 1, itemLevel = 1, requiredLevel = 0),
        item(103, "Old Helm", ARMOR, 4, InventoryTypes.HEAD, itemLevel = 66, requiredLevel = 60, stats = listOf(7 to 20)),
        item(101, "Stout Helm", ARMOR, 4, InventoryTypes.HEAD, itemLevel = 187, requiredLevel = 80, stats = listOf(7 to 60)),
        item(301, "Long Sword", 2, 7, InventoryTypes.WEAPON, itemLevel = 200, requiredLevel = 80, stats = listOf(4 to 40), damage = 300f to 400f, delay = 2600),
        item(303, "Tower Shield", ARMOR, 6, InventoryTypes.SHIELD, itemLevel = 200, requiredLevel = 80, stats = listOf(7 to 50), armor = 6000),
        item(305, "Rifle", 2, 3, InventoryTypes.RANGED_RIGHT, itemLevel = 200, requiredLevel = 80, stats = listOf(3 to 30), damage = 300f to 500f, delay = 2800),
        item(46874, "Argent Crusader's Tabard", ARMOR, 0, InventoryTypes.TABARD, quality = 3, itemLevel = 1, requiredLevel = 0),
        item(4500, "Traveler's Backpack", 1, 0, InventoryTypes.BAG, quality = 2, itemLevel = 65, requiredLevel = 0, containerSlots = 16),
        item(28060, "Impact Shot", 6, 3, InventoryTypes.AMMO, quality = 2, itemLevel = 85, requiredLevel = 62, stackable = 1000),
    )

    private fun ids(sql: String): Set<Int> = Regex("IN \\(([0-9, ]+)\\)").findAll(sql).flatMap { it.groupValues[1].split(",") }.mapNotNull { it.trim().toIntOrNull() }.toSet()

    private fun world() = PortTestData.realmWorld()

    private fun db(takenNames: Set<String> = emptySet()) = PortTestData.FakeRealmDb().apply {
        val w = world()
        on("information_schema.SCHEMATA", listOf(listOf("acore_auth"), listOf("acore_world"), listOf("acore_characters")))
        on("FROM playercreateinfo_skills", w.createSkills.map { listOf(it.raceMask, it.classMask, it.skill, it.rank) })
        on("FROM playercreateinfo_spell_custom", emptyList())
        on("FROM playercreateinfo_action", listOf(listOf(72, 6603, 0), listOf(73, 78, 0), listOf(74, 9999, 0), listOf(83, 6948, 128)))
        on("FROM playercreateinfo", w.createInfos.map { listOf(it.race, it.classId, it.map, it.zone, it.x, it.y, it.z, it.o) })
        on("FROM trainer_spell", w.trainerSpells.map { listOf(it.trainer, it.type, it.requirement, it.spell, it.reqSkill, it.reqSkillRank, it.reqAbilities.getOrElse(0) { 0 }, 0, 0, it.reqLevel) })
        on("FROM spell_ranks", listOf(listOf(78, 78, 1), listOf(78, 284, 2), listOf(33388, 33388, 1), listOf(33388, 33391, 2)))
        on("FROM spell_required", emptyList())
        on("FROM game_tele", listOf(listOf("Stormwind", 0, -8833.38, 628.628, 94.0066, 1.06535)))
        on("FROM account WHERE username") { sql -> if (sql.contains("'PORTER'")) listOf(listOf("5")) else emptyList() }
        on("COUNT(*) FROM characters WHERE account", listOf(listOf(2)))
        on("MAX(guid), 0) FROM characters", listOf(listOf(500)))
        on("FROM characters WHERE name") { sql -> if (takenNames.any { sql.contains("'$it'") }) listOf(listOf("1")) else emptyList() }
        on("FROM reserved_name", emptyList())
        on("FROM profanity_name", emptyList())
        on("FROM quest_template WHERE ID IN", listOf(listOf(783, "A Threat Within", 351309), listOf(86574, "Stonetalon Supply Run", 351309), listOf(788, "Cutting Teeth", 690)))
        for (source in listOf("creature_loot_template", "reference_loot_template", "gameobject_loot_template", "item_loot_template", "npc_vendor", "RewardItem", "RewardChoiceItemID")) {
            on(source) { sql -> ids(sql).map { listOf(it.toString()) } }
        }
        on("FROM item_template WHERE entry IN") { sql -> items.filter { it.entry in ids(sql) }.map(PortTestData::row) }
        on("FROM item_template WHERE class IN (2, 4)") { _ -> items.filter { it.itemClass == 2 || it.itemClass == 4 }.map(PortTestData::row) }
        on("FROM item_template WHERE class = 1") { _ -> items.filter { it.itemClass == 1 }.map(PortTestData::row) }
        on("FROM item_template WHERE class = 6") { _ -> items.filter { it.itemClass == 6 }.map(PortTestData::row) }
        onExecute("START TRANSACTION", listOf(listOf("porter", "501", "8000")))
    }

    /** Achievements and titles from a client file (they must be the game's own, not a module's). */
    private fun clientTables(): Map<String, DbcTable> {
        val achievements = DbcWriter(42)
        achievements.row(0 to 6, 1 to -1, 4 to achievements.text("Level 10"), 41 to 0x4)
        achievements.row(0 to 457, 1 to -1, 4 to achievements.text("Realm First! Level 80"), 41 to 0x100)
        achievements.row(0 to 614, 1 to 1, 4 to achievements.text("For The Alliance!"), 41 to 0)
        achievements.row(0 to 619, 1 to 0, 4 to achievements.text("For The Horde!"), 41 to 0)
        val titles = DbcWriter(37)
        titles.row(0 to 131, 2 to titles.text("%s the Argent Champion"), 36 to 99)
        return mapOf(
            "Achievement" to DbcTable("Achievement", DbcFile.parse(achievements.bytes()), 0, emptyList()),
            "CharTitles" to DbcTable("CharTitles", DbcFile.parse(titles.bytes()), 0, emptyList()),
        )
    }

    private fun porter(db: RealmDb, realm: Realm = Realm.CHROMIE): Porter {
        val root = temp.root
        File(root, "etc/modules").mkdirs()
        File(root, "etc/worldserver.conf").writeText("MaxPlayerLevel = 80\nCharactersPerRealm = 10\n")
        File(root, "etc/modules/chromie-xp.conf").writeText("Chromie.Stable.MaxPlayerLevel = 19\n")
        val data = PortTestData.realmData(
            factions = listOf(
                PortTestData.faction(72, "Stormwind", 19, raceMasks = listOf(1100, 690, 1, 0), bases = listOf(3100, -42000, 4000, 0), flags = listOf(273, 6, 17, 0)),
                PortTestData.faction(76, "Orgrimmar", 14, raceMasks = listOf(160, 1101, 2, 528), bases = listOf(3100, -42000, 4000, 500), flags = listOf(273, 6, 17, 17)),
                PortTestData.faction(1106, "Argent Crusade", 94, raceMasks = listOf(32767, 0, 0, 0), flags = listOf(16, 0, 0, 0)),
            ),
            extraTables = clientTables(),
        )
        return Porter(db, RealmFiles(root, PortRealm.of(realm)!!), now = { 1_800_000_000L }, data = data)
    }

    private val character = PortCharacter(
        name = "Brannoc", raceId = 1, classId = 1, gender = 0, faction = PortFaction.ALLIANCE, level = 90,
        spec = PortSpec("Protection", PortRole.TANK, PortStat.STRENGTH),
        equipment = listOf(
            PortEquipment("head", 103, "Old Helm", "EPIC", 66, "HEAD", 4, 4),
            PortEquipment("weapon", 237728, "Voidglass Kris", "EPIC", 690, "WEAPON", 2, 7),
            PortEquipment("offhand", 237723, "Bulwark", "EPIC", 690, "SHIELD", 4, 6),
            PortEquipment("tabard", 46874, "Argent Crusader's Tabard", "RARE", 1, "TABARD", 4, 0),
        ),
        professions = listOf(PortProfession(164, "Blacksmithing", true, listOf(PortProfessionTier("Classic Blacksmithing", 300)))),
        mounts = listOf(PortMount(6, "Brown Horse"), PortMount(1, "Nothing Of This Game")),
        reputations = listOf(PortReputation("Stormwind", "Exalted", 999), PortReputation("Orgrimmar", "Hated"), PortReputation("Council of Dornogal", "Renown 25"),
            PortReputation("argent crusade", "Renown 3")),
        completedQuests = listOf(PortQuest(783, "A Threat Within"), PortQuest(86574, "The Weight of the World"), PortQuest(86575), PortQuest(788)),
        achievements = listOf(PortAchievement(6, 1_700_000_000L), PortAchievement(457), PortAchievement(614), PortAchievement(619), PortAchievement(40953)),
        titleIds = listOf(131, 448), activeTitleId = 131,
        appearance = PortAppearance(4, 7, 9, 3, 4),
    )

    private val options = PortOptions(Realm.CHROMIE, "porter", "brannoc", race = 1, classId = 1, gender = 0, level = 80, money = 5_000_000_000L, gearTier = GearTier.FRESH)

    @Test fun aPlanHasEverythingTheCharacterNeedsAndWhy() {
        val plan = porter(db()).plan(character, options)
        assertTrue(plan.refusals.toString(), plan.ready)
        assertEquals("Brannoc", plan.name)
        assertEquals(5, plan.accountId)
        assertEquals(80, plan.level)
        assertEquals(Porter.MAX_MONEY, plan.money)
        assertEquals(501, plan.estimatedGuid)
        assertEquals(Porter.AT_LOGIN_FIRST, plan.atLogin)
        assertEquals(PlannedPosition("Stormwind", 0, 1519, -8833.38f, 628.628f, 94.0066f, 1.06535f), plan.position)

        val bySlot = plan.items.associate { it.slot to it.entry }
        assertEquals(103, bySlot[PortSlots.HEAD])
        assertEquals(301, bySlot[PortSlots.MAIN_HAND])
        assertEquals(303, bySlot[PortSlots.OFF_HAND])
        assertEquals(305, bySlot[PortSlots.RANGED])
        assertEquals(46874, bySlot[PortSlots.TABARD])
        assertEquals(listOf(4500, 4500, 4500, 4500), (19..22).map { bySlot[it] })
        assertEquals(6948, bySlot[PortSlots.BACKPACK_FIRST])
        assertEquals(28060, plan.ammoId)
        assertEquals(1000, plan.items.first { it.entry == 28060 }.count)
        assertEquals(GearHow.EXACT, plan.report.equipment.single { it.slot == PortSlots.HEAD }.how)

        assertTrue(plan.spells.containsAll(listOf(71, 355, 7386, 284, 33388, 33391, 458, 2018, 2660)))
        assertTrue(PlannedSkill(762, 150, 150) in plan.skills)
        assertTrue(PlannedSkill(164, 150, 150) in plan.skills)

        // Stormwind: Exalted (42999) less a human's base (4000); Orgrimmar hidden from humans; no Renown here.
        assertEquals(listOf(PlannedReputation(72, 38999, 17)), plan.reputations)
        assertEquals(listOf(783), plan.quests)
        assertEquals(listOf(6 to 1_700_000_000L, 614 to 1_800_000_000L), plan.achievements)
        assertEquals(99, plan.chosenTitle)
        assertTrue(plan.knownTitles[99 / 32] and (1 shl (99 % 32)) != 0)
        // The action bar's Heroic Strike at the rank it knows, the unknown spell left off, the hearthstone kept.
        assertEquals(listOf(PlannedAction(72, 6603, 0), PlannedAction(73, 284, 0), PlannedAction(83, 6948, 128)), plan.actions)

        val text = plan.report.lines().joinToString("\n")
        for (expected in listOf("Orgrimmar: dropped", "Council of Dornogal: dropped", "Nothing Of This Game: dropped", "another quest here", "the other side's", "statistics, hidden or realm-first")) {
            assertTrue("\"$expected\" in\n$text", text.contains(expected))
        }
    }

    @Test fun aPlanIsRefusedWithTheReason() {
        assertFalse(porter(db(takenNames = setOf("Brannoc"))).plan(character, options).ready)
        assertTrue(porter(db()).plan(character, options.copy(account = "nobody")).refusals.any { it.contains("no account") })
        assertTrue(porter(db()).plan(character, options.copy(race = 4, classId = 4)).refusals.any { it.contains("has no") })
        assertTrue(porter(db()).plan(character, options.copy(level = 81)).refusals.any { it.contains("outside") })
        assertTrue(porter(db()).plan(character, options.copy(name = "Xal'veth")).refusals.isNotEmpty())
        val scaled = porter(db()).plan(character, options.copy(level = null))
        assertEquals(19, scaled.level)
        assertEquals(Porter.PLAYER_FLAGS_NO_XP_GAIN, scaled.playerFlags)
        try {
            porter(db(takenNames = setOf("Brannoc"))).apply(porter(db(takenNames = setOf("Brannoc"))).plan(character, options))
            fail()
        } catch (e: IllegalStateException) { }
    }

    @Test fun remixAndTheOtherGamesRealmsTakeNone() {
        val remix = porter(db(), Realm.REMIX).support()
        assertFalse(remix.supported)
        assertTrue(remix.reason!!.contains("Timerunner"))
        assertFalse(Porter(db(), RealmFiles(temp.root, PortRealm(Realm.OCTO, "a", "b", "c", "etc"))).support().supported)
        assertTrue(porter(db()).support().supported)
        val missing = PortTestData.FakeRealmDb().on("information_schema.SCHEMATA", listOf(listOf("acore_auth")))
        assertFalse(porter(missing).support().supported)
    }

    @Test fun applyWritesOneTransactionThenTheAccountsCount() {
        val db = db()
        val porter = porter(db)
        val plan = porter.plan(character, options)
        val result = porter.apply(plan)
        assertEquals(PortResult(501, 8001, 8000 + plan.items.size, "Brannoc"), result)
        assertEquals(listOf("acore_characters", "acore_auth"), db.executed.map { it.first })
        assertEquals("REPLACE INTO realmcharacters (realmid, acctid, numchars) SELECT 1, 5, COUNT(*) FROM `acore_characters`.characters WHERE account = 5;\n", db.executed[1].second)
    }

    @Test fun theScriptChecksFirstThenWritesEveryRowInOneTransaction() {
        val plan = porter(db()).plan(character, options)
        val sql = PortSql.characterScript(plan, 10, 1_800_000_000L)
        val lines = sql.lines()
        assertEquals("START TRANSACTION;", lines[1])
        assertTrue(sql.contains("IF EXISTS (SELECT 1 FROM characters WHERE name = 'Brannoc') THEN\n    SIGNAL SQLSTATE '45000'"))
        assertTrue(sql.contains("IF (SELECT COUNT(*) FROM characters WHERE account = 5) >= 10 THEN"))
        assertTrue(sql.indexOf("SIGNAL") < sql.indexOf("INSERT INTO characters"))
        assertTrue(sql.contains("SELECT COALESCE(MAX(guid), 0) + 1 INTO @porter_guid FROM characters FOR UPDATE;"))
        assertTrue(sql.contains("SELECT COALESCE(MAX(guid), 0) INTO @porter_item FROM item_instance FOR UPDATE;"))
        assertEquals("SELECT 'porter', @porter_guid, @porter_item;", lines.last { it.isNotEmpty() })
        assertEquals("COMMIT;", lines.filter { it.isNotEmpty() }.dropLast(1).last())

        val insert = lines.single { it.startsWith("INSERT INTO characters (") }
        val columns = insert.substringAfter("(").substringBefore(")").split(",").map { it.trim() }
        val values = insert.substringAfter("VALUES (").removeSuffix(");").split(",").map { it.trim() }
        assertEquals(75, columns.size)
        assertEquals(columns.size, values.size)
        val value = columns.zip(values).toMap()
        assertEquals("@porter_guid", value["guid"])
        assertEquals("'Brannoc'", value["name"])
        assertEquals("80", value["level"])
        assertEquals("1", value["cinematic"])
        assertEquals("32", value["at_login"])
        assertEquals("1519", value["zone"])
        assertEquals("99", value["chosenTitle"])
        assertEquals("4294967295", value["watchedFaction"])
        assertEquals(46, value.getValue("equipmentCache").trim('\'').trim().split(" ").size)
        assertEquals(128, value.getValue("exploredZones").trim('\'').trim().split(" ").size)
        assertEquals(14, value.getValue("taximask").trim('\'').trim().split(" ").size)
        assertEquals(6, value.getValue("knownTitles").trim('\'').trim().split(" ").size)
        assertTrue(value.getValue("equipmentCache"), value.getValue("equipmentCache").startsWith("'103 0 " + "0 0 ".repeat(14) + "301 0 303 0 305 0 46874 0 4500 0 4500 0 4500 0 4500 0 '"))

        assertTrue(sql.contains("(@porter_item + 1, ${plan.items[0].entry}, @porter_guid, 0, 0, 1, 0, '0 0 0 0 0 ', 1, '${"0 ".repeat(36)}', 0, 100, 0, '')"))
        assertEquals(plan.items.size, Regex("\\(@porter_guid, 0, \\d+, @porter_item \\+ \\d+\\)").findAll(sql).count())
        assertTrue(sql.contains("INSERT INTO character_reputation (guid, faction, standing, flags) VALUES\n(@porter_guid, 72, 38999, 17);"))
        assertTrue(sql.contains("INSERT INTO character_queststatus_rewarded (guid, quest, active) VALUES\n(@porter_guid, 783, 1);"))
        assertNotNull(Regex("INSERT INTO character_spell \\(guid, spell, specMask\\) VALUES\n\\(@porter_guid, \\d+, 255\\)").find(sql))
        assertTrue(sql.contains("INSERT INTO character_homebind (guid, mapId, zoneId, posX, posY, posZ) VALUES (@porter_guid, 0, 1519, -8833.3799, 628.6280, 94.0066);"))
    }
}
