-- The opening (src/RemixIntro.cpp): a new Timerunner, a veteran of the war against the Lich King,
-- is drinking with friends in their faction's tavern when Moratari pulls them out of their hour:
-- back into the war's last battle at the Broken Front in Icecrown, then through what his reign
-- cost (the Wrathgate, Wintergarde, Icecrown's fields of the dead), and on to the Bazaar. Its
-- people are the game's own, under entries of their own (770120 to 770149) so nothing of theirs
-- (their scripts, their loot, their vehicles) comes with them: the Scourge (ghouls, an
-- abomination, crypt fiends, a deathbringer, a frost wyrm, the val'kyr) and the Lich King with
-- Frostmourne; Highlord Tirion Fordring with the Ashbringer, the Argent Crusade, the Skybreaker's
-- marines and the Kor'kron; the unseen ones the effects and the voices come from; the tavern's
-- innkeepers and the Timerunner's three friends (each side's own), with their tankards; the
-- fallen of the Wrathgate; Wintergarde's villagers and its risen. All of them are summoned for the
-- one Timerunner, in a phase of their own; the script sets their sides, levels and health.

DROP TEMPORARY TABLE IF EXISTS `remix_intro_cast`;
CREATE TEMPORARY TABLE `remix_intro_cast` (
  `entry` INT UNSIGNED NOT NULL,
  `source` INT UNSIGNED NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  `subname` VARCHAR(100) NULL,
  `unit_flags` INT UNSIGNED NOT NULL,
  `flags_extra` INT UNSIGNED NOT NULL,
  `faction` SMALLINT UNSIGNED NOT NULL,
  `display` INT UNSIGNED NOT NULL DEFAULT 0,      -- its one look (0: the source's own looks)
  `held` INT NOT NULL DEFAULT 0,                  -- in its hand (0: the source's arms, -1: nothing)
  PRIMARY KEY (`entry`)
);
-- unit_flags: 0x100 the player can't attack them, 0x200 nor creatures, 0x2 nobody (the Lich King,
-- who is not there to be fought; the unseen ones). flags_extra 0x80: unseen (a trigger). Sides:
-- the Scourge 2068, and against it 250, which every player, Alliance or Horde, sees as a friend.
INSERT INTO `remix_intro_cast` (`entry`, `source`, `name`, `subname`, `unit_flags`, `flags_extra`, `faction`, `display`, `held`) VALUES
(770120, 26125, 'Risen Ghoul', NULL, 0, 0, 2068, 0, 0),
(770121, 30597, 'Spiked Ghoul', NULL, 0, 0, 2068, 0, 0),
(770122, 28843, 'Bloated Abomination', NULL, 0, 0, 2068, 0, 0),
(770123, 27734, 'Crypt Fiend', NULL, 0, 0, 2068, 0, 0),
(770124, 36892, 'Ymirjar Deathbringer', NULL, 0, 0, 2068, 0, 0),
(770125, 28670, 'Frostbrood Vanquisher', NULL, 770, 0, 2068, 0, 0),
(770126, 28534, 'Val''kyr Battle-maiden', NULL, 770, 0, 2068, 0, 0),
(770127, 36597, 'The Lich King', NULL, 770, 0, 2068, 0, 0),
(770128, 38995, 'Highlord Tirion Fordring', 'The Argent Crusade', 256, 0, 250, 0, 0),
(770129, 38493, 'Argent Crusader', NULL, 256, 0, 250, 0, 0),
(770130, 28029, 'Argent Crusader', NULL, 256, 0, 250, 0, 0),
(770131, 30352, 'Skybreaker Marine', NULL, 256, 0, 250, 0, 0),
(770132, 30755, 'Kor''kron Reaver', NULL, 256, 0, 250, 0, 0),
(770133, 21252, 'The Argent Crusade', NULL, 770, 128, 250, 0, 0),
(770134, 21252, 'The Scourge', NULL, 770, 128, 2068, 0, 0),
(770135, 21252, 'Eternus', NULL, 770, 128, 35, 0, 0),
(770136, 21252, 'The Lich King', NULL, 770, 128, 35, 0, 0),
-- The tavern: its innkeeper, and the Timerunner's three friends, each with a tankard (2703).
(770137, 33480, 'Brannoc Ironvale', NULL, 770, 0, 35, 29088, 2703),
(770138, 33563, 'Sylenna Moonfall', NULL, 770, 0, 35, 28710, 2703),
(770139, 33477, 'Tobias Harlan', NULL, 770, 0, 35, 29092, 2703),
(770140, 33459, 'Grakka Bloodfist', NULL, 770, 0, 35, 29090, 2703),
(770141, 33471, 'Tahono Swiftwind', NULL, 770, 0, 35, 28597, 2703),
(770142, 33382, 'Veylan Dawnspire', NULL, 770, 0, 35, 28853, 2703),
(770143, 6740, 'Innkeeper Allison', 'Innkeeper', 770, 0, 35, 0, 0),
(770144, 6929, 'Innkeeper Gryshka', 'Innkeeper', 770, 0, 35, 0, 0),
-- The fallen of the Wrathgate, the Alliance's and the Horde's.
(770145, 27160, 'Fallen Soldier', NULL, 770, 0, 35, 24361, -1),
(770146, 27553, 'Fallen Soldier', NULL, 770, 0, 35, 23864, -1),
-- Wintergarde: its people, and what the Scourge made of them.
(770147, 27336, 'Wintergarde Villager', NULL, 770, 0, 35, 24560, -1),
(770148, 27283, 'Risen Villager', NULL, 770, 0, 2068, 0, 0),
(770149, 27315, 'Wintergarde Villager', NULL, 770, 0, 35, 24533, -1);

DELETE FROM `creature_template` WHERE `entry` BETWEEN 770120 AND 770149;
DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN 770120 AND 770149;
DELETE FROM `creature_equip_template` WHERE `CreatureID` BETWEEN 770120 AND 770149;

DROP TEMPORARY TABLE IF EXISTS `remix_intro_template`;
CREATE TEMPORARY TABLE `remix_intro_template` SELECT c.`entry` AS `cast_entry`, t.* FROM `remix_intro_cast` c JOIN `creature_template` t ON t.`entry` = c.`source`;
UPDATE `remix_intro_template` r JOIN `remix_intro_cast` c ON c.`entry` = r.`cast_entry`
SET r.`entry` = c.`entry`, r.`name` = c.`name`, r.`subname` = c.`subname`, r.`unit_flags` = c.`unit_flags`,
    r.`flags_extra` = c.`flags_extra`, r.`faction` = c.`faction`, r.`difficulty_entry_1` = 0, r.`difficulty_entry_2` = 0, r.`difficulty_entry_3` = 0,
    r.`KillCredit1` = 0, r.`KillCredit2` = 0, r.`gossip_menu_id` = 0, r.`minlevel` = 10, r.`maxlevel` = 10, r.`npcflag` = 0,
    r.`lootid` = 0, r.`pickpocketloot` = 0, r.`skinloot` = 0, r.`mingold` = 0, r.`maxgold` = 0, r.`VehicleId` = 0,
    r.`MovementType` = 0, r.`AIName` = '', r.`ScriptName` = 'npc_remix_intro', r.`CreatureImmunitiesId` = 0,
    r.`HealthModifier` = 1, r.`DamageModifier` = 1, r.`RegenHealth` = 1, r.`exp` = 2;
ALTER TABLE `remix_intro_template` DROP COLUMN `cast_entry`;
INSERT INTO `creature_template` SELECT * FROM `remix_intro_template`;
DROP TEMPORARY TABLE `remix_intro_template`;

INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`)
SELECT c.`entry`, m.`Idx`, m.`CreatureDisplayID`, m.`DisplayScale`, m.`Probability`, 0
FROM `remix_intro_cast` c JOIN `creature_template_model` m ON m.`CreatureID` = c.`source` WHERE c.`display` = 0;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`)
SELECT c.`entry`, 0, c.`display`, 1, 1, 0 FROM `remix_intro_cast` c WHERE c.`display` <> 0;

-- Their arms: the Ashbringer, Frostmourne, the crusaders', the marines' and the Kor'kron's; the
-- friends' tankards.
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`)
SELECT c.`entry`, e.`ID`, e.`ItemID1`, e.`ItemID2`, e.`ItemID3`, 0
FROM `remix_intro_cast` c JOIN `creature_equip_template` e ON e.`CreatureID` = c.`source` AND e.`ID` = 1 WHERE c.`held` = 0;
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`)
SELECT c.`entry`, 1, c.`held`, 0, 0, 0 FROM `remix_intro_cast` c WHERE c.`held` > 0;

DROP TEMPORARY TABLE `remix_intro_cast`;
