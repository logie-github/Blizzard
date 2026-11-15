package com.logie.blizz.porter.port

import java.util.Locale

/**
 * The SQL a port runs. The characters database's part is one transaction: two checks that stop it before anything is
 * written (the name is free, the account has room), the character's guid and its items' guids taken from the tables'
 * highest at that moment (locked till the end), every row inserted, and the guids printed as the last row
 * (`porter <guid> <last item guid before ours>`). A failed statement ends the client before COMMIT, so the database
 * drops the whole transaction.
 *
 * Every value is a number (Kotlin Ints and Longs) or a name that passed [PortNames] and is quoted by [Sql.text].
 */
object PortSql {
    /** item_instance's enchantments column of an item without any: 12 enchantment slots of 3 numbers. */
    private val NO_ENCHANTMENTS = "0 ".repeat(36)

    fun characterScript(plan: PortPlan, charactersPerRealm: Int, now: Long): String {
        val guid = "@porter_guid"
        val name = Sql.text(plan.name)
        val out = StringBuilder()
        out.append("-- The Character Porter: ${plan.name} for account ${plan.accountId}, one transaction.\n")
        out.append("START TRANSACTION;\n")
        out.append("DELIMITER //\n")
        out.append("BEGIN NOT ATOMIC\n")
        out.append("  IF EXISTS (SELECT 1 FROM characters WHERE name = $name) THEN\n")
        out.append("    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Porter: a character of this realm already has that name';\n")
        out.append("  END IF;\n")
        out.append("  IF (SELECT COUNT(*) FROM characters WHERE account = ${plan.accountId}) >= $charactersPerRealm THEN\n")
        out.append("    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Porter: the account has as many characters on this realm as its list holds';\n")
        out.append("  END IF;\n")
        out.append("END//\n")
        out.append("DELIMITER ;\n")
        out.append("SELECT COALESCE(MAX(guid), 0) + 1 INTO $guid FROM characters FOR UPDATE;\n")
        out.append("SELECT COALESCE(MAX(guid), 0) INTO @porter_item FROM item_instance FOR UPDATE;\n")

        val equipment = LongArray(PortSlots.BACKPACK_FIRST)
        for (item in plan.items) if (item.slot < PortSlots.BACKPACK_FIRST) equipment[item.slot] = item.entry.toLong()
        val cache = buildString { for (slot in 0 until PortSlots.BACKPACK_FIRST) append(equipment[slot]).append(" 0 ") }
        val p = plan.position
        out.append("INSERT INTO characters (guid, account, name, race, class, gender, level, xp, money, skin, face, hairStyle, hairColor, facialStyle, ")
            .append("bankSlots, restState, playerFlags, position_x, position_y, position_z, map, instance_id, instance_mode_mask, orientation, taximask, online, ")
            .append("cinematic, totaltime, leveltime, logout_time, is_logout_resting, rest_bonus, resettalents_cost, resettalents_time, trans_x, trans_y, trans_z, ")
            .append("trans_o, transguid, extra_flags, stable_slots, at_login, zone, death_expire_time, taxi_path, arenaPoints, totalHonorPoints, todayHonorPoints, ")
            .append("yesterdayHonorPoints, totalKills, todayKills, yesterdayKills, chosenTitle, knownCurrencies, watchedFaction, drunk, health, power1, power2, ")
            .append("power3, power4, power5, power6, power7, latency, talentGroupsCount, activeTalentGroup, exploredZones, equipmentCache, ammoId, knownTitles, ")
            .append("actionBars, grantableLevels, innTriggerId, extraBonusTalentCount) VALUES (")
            .append(listOf(
                guid, plan.accountId, name, plan.race, plan.classId, plan.gender, plan.level, 0, plan.money,
                plan.appearance.skin, plan.appearance.face, plan.appearance.hairStyle, plan.appearance.hairColor, plan.appearance.facialHair,
                0, REST_STATE_NORMAL, unsigned(plan.playerFlags), float(p.x), float(p.y), float(p.z), p.map, 0, 0, float(p.o), Sql.text(numbers(plan.taxiMask)), 0,
                // cinematic 1: the race's intro isn't played to a character that has seen the world
                1, 0, 0, now, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, plan.atLogin, p.zone, 0, Sql.text(""), 0, 0, 0,
                0, 0, 0, 0, plan.chosenTitle, 0, NO_WATCHED_FACTION, 0, FULL, FULL, 0,
                // health and the powers past their maximum: the core cuts them to it (full); rage and runic power start empty
                FULL, FULL, 0, 0, 0, 0, 1, 0, Sql.text(numbers(plan.exploredZones)), Sql.text(cache), plan.ammoId, Sql.text(numbers(plan.knownTitles)),
                0, 0, 0, 0,
            ).joinToString(", ")).append(");\n")
        out.append("INSERT INTO character_homebind (guid, mapId, zoneId, posX, posY, posZ) VALUES ($guid, ${p.map}, ${p.zone}, ${float(p.x)}, ${float(p.y)}, ${float(p.z)});\n")

        if (plan.items.isNotEmpty()) {
            out.append("INSERT INTO item_instance (guid, itemEntry, owner_guid, creatorGuid, giftCreatorGuid, count, duration, charges, flags, enchantments, randomPropertyId, durability, playedTime, text) VALUES\n")
            out.append(plan.items.withIndex().joinToString(",\n") { (i, item) ->
                // flags 1: bound, as an item a character has worn is
                "(@porter_item + ${i + 1}, ${item.entry}, $guid, 0, 0, ${item.count}, 0, ${Sql.text(item.charges)}, $ITEM_SOULBOUND, ${Sql.text(NO_ENCHANTMENTS)}, 0, ${item.durability}, 0, '')"
            }).append(";\n")
            out.append("INSERT INTO character_inventory (guid, bag, slot, item) VALUES\n")
            out.append(plan.items.withIndex().joinToString(",\n") { (i, item) -> "($guid, 0, ${item.slot}, @porter_item + ${i + 1})" }).append(";\n")
        }
        values(out, "character_spell (guid, spell, specMask)", plan.spells.map { "($guid, $it, $SPEC_MASK_ALL)" })
        values(out, "character_skills (guid, skill, value, max)", plan.skills.map { "($guid, ${it.skill}, ${it.value}, ${it.max})" })
        values(out, "character_reputation (guid, faction, standing, flags)", plan.reputations.map { "($guid, ${it.faction}, ${it.standing}, ${it.flags})" })
        values(out, "character_queststatus_rewarded (guid, quest, active)", plan.quests.map { "($guid, $it, 1)" })
        values(out, "character_achievement (guid, achievement, date)", plan.achievements.map { "($guid, ${it.first}, ${it.second})" })
        values(out, "character_action (guid, spec, button, action, type)", plan.actions.map { "($guid, 0, ${it.button}, ${it.action}, ${it.type})" })
        out.append("COMMIT;\n")
        out.append("SELECT 'porter', $guid, @porter_item;\n")
        return out.toString()
    }

    /** The login database's count of the account's characters on the realm, as the core keeps it (realmcharacters). */
    fun realmCharactersScript(realm: PortRealm, accountId: Int): String =
        "REPLACE INTO realmcharacters (realmid, acctid, numchars) SELECT ${realm.realm.id}, $accountId, COUNT(*) " +
            "FROM ${Sql.name(realm.charactersDb)}.characters WHERE account = $accountId;\n"

    private fun values(out: StringBuilder, table: String, rows: List<String>) {
        for (chunk in rows.chunked(500)) out.append("INSERT INTO $table VALUES\n").append(chunk.joinToString(",\n")).append(";\n")
    }

    /** Numbers as the core writes its number lists: each followed by a space, unsigned. */
    private fun numbers(values: List<Int>) = buildString { for (v in values) append(unsigned(v)).append(' ') }

    private fun unsigned(value: Int): Long = value.toLong() and 0xFFFFFFFFL

    private fun float(value: Float) = String.format(Locale.ROOT, "%.4f", value)

    private const val REST_STATE_NORMAL = 2
    private const val ITEM_SOULBOUND = 1
    private const val SPEC_MASK_ALL = 255
    private const val FULL = 999999
    private const val NO_WATCHED_FACTION = 4294967295L
}
