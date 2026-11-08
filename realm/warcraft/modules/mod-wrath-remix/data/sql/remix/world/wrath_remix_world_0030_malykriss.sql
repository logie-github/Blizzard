-- Malykriss: The Vile Hold, the Infinite Bazaar's home (tools/malykriss.py writes this file: edit that and
-- run it again). The Scourge's garrison is not in Remix's world, nor the game's quests that need it; the
-- hall belongs to the Bazaar's allies, the Knights of the Ebon Blade and the last free nerubians of
-- Azjol-Nerub, and to the time-magic round the hourglass (src/RemixMalykriss.cpp). Never in
-- ChromieCraft's world: this file is Remix's world database's only.

-- The garrison: 36 kinds, every spawn of them in Malykriss.
DROP TEMPORARY TABLE IF EXISTS `remix_malykriss_gone`;
CREATE TEMPORARY TABLE `remix_malykriss_gone` (`guid` INT UNSIGNED NOT NULL PRIMARY KEY)
  SELECT `guid` FROM `creature` WHERE `map` = 571 AND `position_x` BETWEEN 5950 AND 6700
    AND `position_y` BETWEEN 1480 AND 2020 AND `id` IN (30894, 30920, 30921, 30922, 30953, 30954, 30956, 30957, 30958, 31012, 31042, 31049, 31064, 31065, 31066, 31068, 31075, 31159, 31160, 31161, 31163, 31221, 31223, 31224, 31225, 31226, 31255, 31320, 31321, 31322, 31323, 31324, 31325, 31326, 31327, 31747);
DELETE FROM `waypoint_data` WHERE `id` IN (SELECT `path_id` FROM `creature_addon` WHERE `path_id` <> 0 AND `guid` IN (SELECT `guid` FROM `remix_malykriss_gone`));
DELETE FROM `creature_addon` WHERE `guid` IN (SELECT `guid` FROM `remix_malykriss_gone`);
DELETE FROM `creature_formations` WHERE `leaderGUID` IN (SELECT `guid` FROM `remix_malykriss_gone`) OR `memberGUID` IN (SELECT `guid` FROM `remix_malykriss_gone`);
DELETE FROM `smart_scripts` WHERE `source_type` = 0 AND -`entryorguid` IN (SELECT `guid` FROM `remix_malykriss_gone`);
DELETE FROM `pool_creature` WHERE `guid` IN (SELECT `guid` FROM `remix_malykriss_gone`);
DELETE FROM `game_event_creature` WHERE `guid` IN (SELECT `guid` FROM `remix_malykriss_gone`);
DELETE FROM `linked_respawn` WHERE `guid` IN (SELECT `guid` FROM `remix_malykriss_gone`) OR `linkedGuid` IN (SELECT `guid` FROM `remix_malykriss_gone`);
DELETE FROM `creature_movement_override` WHERE `SpawnId` IN (SELECT `guid` FROM `remix_malykriss_gone`);
DELETE FROM `creature` WHERE `guid` IN (SELECT `guid` FROM `remix_malykriss_gone`);
DROP TEMPORARY TABLE `remix_malykriss_gone`;

-- The Scourge's furnaces, and the ore and herbs on the crater's floor (the camp stands on it).
DROP TEMPORARY TABLE IF EXISTS `remix_malykriss_gone`;
CREATE TEMPORARY TABLE `remix_malykriss_gone` (`guid` INT UNSIGNED NOT NULL PRIMARY KEY)
  SELECT `guid` FROM `gameobject` WHERE `map` = 571 AND `position_x` BETWEEN 5950 AND 6700
    AND `position_y` BETWEEN 1480 AND 2020
    AND (`id` = 193004 OR (`id` IN (189980, 189981, 191133, 190171, 190172) AND `position_z` < 545.0));
DELETE FROM `pool_gameobject` WHERE `guid` IN (SELECT `guid` FROM `remix_malykriss_gone`);
DELETE FROM `game_event_gameobject` WHERE `guid` IN (SELECT `guid` FROM `remix_malykriss_gone`);
DELETE FROM `gameobject` WHERE `guid` IN (SELECT `guid` FROM `remix_malykriss_gone`);
DROP TEMPORARY TABLE `remix_malykriss_gone`;

-- The game's quests that need the garrison, off (disables, quests).
DELETE FROM `disables` WHERE `sourceType` = 1 AND `entry` IN (13138, 13140, 13155, 13143, 13145, 13146, 13147, 13160, 13161, 13162, 13163, 13164);
INSERT INTO `disables` (`sourceType`, `entry`, `flags`, `params_0`, `params_1`, `comment`) VALUES
(1, 13138, 0, '', '', 'Wrath Remix: I''m Smelting... Smelting! (Malykriss is the Bazaar)'),
(1, 13140, 0, '', '', 'Wrath Remix: The Runesmiths of Malykriss (Malykriss is the Bazaar)'),
(1, 13155, 0, '', '', 'Wrath Remix: Vereth the Cunning (Malykriss is the Bazaar)'),
(1, 13143, 0, '', '', 'Wrath Remix: New Recruit (Malykriss is the Bazaar)'),
(1, 13145, 0, '', '', 'Wrath Remix: The Vile Hold (Malykriss is the Bazaar)'),
(1, 13146, 0, '', '', 'Wrath Remix: Generosity Abounds (Malykriss is the Bazaar)'),
(1, 13147, 0, '', '', 'Wrath Remix: Matchmaker (Malykriss is the Bazaar)'),
(1, 13160, 0, '', '', 'Wrath Remix: Stunning View (Malykriss is the Bazaar)'),
(1, 13161, 0, '', '', 'Wrath Remix: The Rider of the Unholy (Malykriss is the Bazaar)'),
(1, 13162, 0, '', '', 'Wrath Remix: The Rider of Frost (Malykriss is the Bazaar)'),
(1, 13163, 0, '', '', 'Wrath Remix: The Rider of Blood (Malykriss is the Bazaar)'),
(1, 13164, 0, '', '', 'Wrath Remix: The Fate of Bloodbane (Malykriss is the Bazaar)');

DELETE FROM `creature_template` WHERE `entry` BETWEEN 770400 AND 770479;
DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN 770400 AND 770479;
DELETE FROM `creature_template_addon` WHERE `entry` BETWEEN 770400 AND 770479;
DELETE FROM `creature_template_movement` WHERE `CreatureId` BETWEEN 770400 AND 770479;
DELETE FROM `creature_equip_template` WHERE `CreatureID` BETWEEN 770400 AND 770479;
INSERT INTO `creature_template` (`entry`, `name`, `subname`, `gossip_menu_id`, `minlevel`, `maxlevel`, `exp`, `faction`, `npcflag`,
  `speed_walk`, `speed_run`, `rank`, `unit_class`, `unit_flags`, `unit_flags2`, `type`, `flags_extra`,
  `HealthModifier`, `DamageModifier`, `BaseAttackTime`, `RegenHealth`, `ScriptName`) VALUES
(770400, 'Ebon Blade Gatewarden', 'Knights of the Ebon Blade', 0, 80, 80, 2, 2050, 0, 1, 1.14286, 0, 1, 770, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_bazaar_life'),
(770401, 'Ebon Blade Sentinel', 'Knights of the Ebon Blade', 0, 80, 80, 2, 2050, 0, 1, 1.14286, 0, 1, 770, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_bazaar_life'),
(770402, 'Ebon Blade Runesmith', 'Knights of the Ebon Blade', 0, 80, 80, 2, 2050, 0, 1, 1.14286, 0, 1, 770, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_bazaar_life'),
(770403, 'Ebon Blade Duelist', 'Knights of the Ebon Blade', 0, 80, 80, 2, 2050, 0, 1, 1.14286, 0, 1, 770, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_malykriss'),
(770404, 'Commander Aldren Hask', 'Knights of the Ebon Blade', 77101, 80, 80, 2, 2050, 1, 1, 1.14286, 0, 1, 770, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_bazaar_life'),
(770405, 'Deathcharger', NULL, 0, 80, 80, 2, 2050, 0, 1, 1.14286, 0, 1, 33555202, 2048, 1, 2, 10, 1, 2000, 1, ''),
(770406, 'Captured Atrocity', 'Held in a Moment', 0, 80, 80, 2, 35, 0, 1, 1.14286, 0, 1, 33555202, 2048, 6, 2, 10, 1, 2000, 1, ''),
(770410, 'Warlord Kaz''anub', 'Remnant of Azjol-Nerub', 77102, 80, 80, 2, 35, 1, 1, 1.14286, 0, 1, 770, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_bazaar_life'),
(770411, 'Elder Zek''thira', 'Remnant of Azjol-Nerub', 77103, 80, 80, 2, 35, 1, 1, 1.14286, 0, 1, 770, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_bazaar_life'),
(770412, 'Architect Thekk''ri', 'Remnant of Azjol-Nerub', 77104, 80, 80, 2, 35, 1, 1, 1.14286, 0, 1, 770, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_bazaar_life'),
(770413, 'Azjol Warden', 'Remnant of Azjol-Nerub', 0, 80, 80, 2, 35, 0, 1, 1.14286, 0, 1, 770, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_bazaar_life'),
(770414, 'Azjol Silkweaver', 'Remnant of Azjol-Nerub', 0, 80, 80, 2, 35, 0, 1, 1.14286, 0, 1, 770, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_bazaar_life'),
(770415, 'Azjol Skitterer', NULL, 0, 80, 80, 2, 35, 0, 1, 1.14286, 0, 1, 770, 2048, 8, 2, 10, 1, 2000, 1, ''),
(770416, 'Azjol Skyguard', 'Remnant of Azjol-Nerub', 0, 80, 80, 2, 35, 0, 1, 1.14286, 0, 1, 33555202, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_malykriss'),
(770417, 'Azjol Envoy', 'Remnant of Azjol-Nerub', 77105, 80, 80, 2, 35, 1, 1, 1.14286, 0, 1, 770, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_bazaar_life'),
(770420, 'Hourglass Sands', NULL, 0, 80, 80, 2, 35, 0, 1, 1.14286, 0, 1, 33555202, 2048, 10, 128, 10, 1, 2000, 1, 'npc_remix_malykriss'),
(770421, 'Bazaar Sandshaper', 'Keepers of Time', 0, 80, 80, 2, 35, 0, 1, 1.14286, 0, 1, 770, 2048, 2, 2, 10, 1, 2000, 1, 'npc_remix_malykriss'),
(770422, 'Hourglass''s Heart', NULL, 0, 80, 80, 2, 35, 0, 1, 1.14286, 0, 1, 33555202, 2048, 10, 128, 10, 1, 2000, 1, 'npc_remix_malykriss'),
(770423, 'Frost Sphere', NULL, 0, 80, 80, 2, 35, 0, 1, 1.14286, 0, 1, 33555202, 2048, 10, 2, 10, 1, 2000, 1, 'npc_remix_malykriss'),
(770424, 'Time Rift', NULL, 0, 80, 80, 2, 35, 0, 1, 1.14286, 0, 1, 33555202, 2048, 10, 2, 10, 1, 2000, 1, 'npc_remix_malykriss'),
(770425, 'Saronite Fog', NULL, 0, 80, 80, 2, 35, 0, 1, 1.14286, 0, 1, 33555202, 2048, 10, 128, 10, 1, 2000, 1, ''),
(770426, 'Burrow', NULL, 0, 80, 80, 2, 35, 0, 1, 1.14286, 0, 1, 33555202, 2048, 10, 128, 10, 1, 2000, 1, '');
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) VALUES
(770400, 0, 25998, 1, 1, 0),
(770400, 1, 25999, 1, 1, 0),
(770400, 2, 26000, 1, 1, 0),
(770400, 3, 26001, 1, 1, 0),
(770401, 0, 26834, 1, 1, 0),
(770401, 1, 26835, 1, 1, 0),
(770401, 2, 26836, 1, 1, 0),
(770401, 3, 26837, 1, 1, 0),
(770402, 0, 25580, 1, 1, 0),
(770402, 1, 25745, 1, 1, 0),
(770402, 2, 25746, 1, 1, 0),
(770402, 3, 25747, 1, 1, 0),
(770403, 0, 25998, 1, 1, 0),
(770403, 1, 25999, 1, 1, 0),
(770403, 2, 26000, 1, 1, 0),
(770403, 3, 26001, 1, 1, 0),
(770404, 0, 26834, 1, 1, 0),
(770405, 0, 25280, 1, 1, 0),
(770406, 0, 7858, 1, 1, 0),
(770410, 0, 23882, 0.6, 1, 0),
(770411, 0, 24130, 1, 1, 0),
(770412, 0, 23570, 1, 1, 0),
(770413, 0, 23942, 1, 1, 0),
(770413, 1, 23578, 1, 1, 0),
(770414, 0, 23569, 1, 1, 0),
(770414, 1, 23564, 1, 1, 0),
(770415, 0, 23819, 1, 1, 0),
(770415, 1, 23571, 1, 1, 0),
(770416, 0, 23913, 1, 1, 0),
(770416, 1, 23916, 1, 1, 0),
(770417, 0, 23569, 1, 1, 0),
(770420, 0, 11686, 1, 1, 0),
(770421, 0, 14887, 1, 1, 0),
(770422, 0, 11686, 1, 1, 0),
(770423, 0, 25144, 1, 1, 0),
(770424, 0, 25392, 1, 1, 0),
(770425, 0, 11686, 1, 1, 0),
(770426, 0, 11686, 1, 1, 0);
INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) VALUES
(770406, 0, 0, 0, 1, 0, 0, '34712 45776'),
(770414, 0, 0, 0, 1, 0, 0, '56726'),
(770420, 0, 0, 0, 1, 0, 0, '50057'),
(770423, 0, 0, 0, 1, 0, 0, '67539'),
(770425, 0, 0, 0, 1, 0, 0, '63096'),
(770426, 0, 0, 0, 1, 0, 0, '66969');
-- The flying ones hover where they are put.
INSERT INTO `creature_template_movement` (`CreatureId`, `Ground`, `Swim`, `Flight`, `Rooted`, `Chase`, `Random`, `InteractionPauseTimer`) VALUES
(770416, 0, 0, 1, 0, 0, 0, NULL),
(770422, 0, 0, 1, 0, 0, 0, NULL),
(770423, 0, 0, 1, 0, 0, 0, NULL),
(770424, 0, 0, 1, 0, 0, 0, NULL);
-- Weapons: the game's own Ebon Blade knights'.
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) SELECT 770400, 1, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = 29202 AND `ID` = 1;
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) SELECT 770401, 1, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = 30197 AND `ID` = 1;
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) SELECT 770402, 1, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = 28865 AND `ID` = 1;
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) SELECT 770403, 1, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = 29202 AND `ID` = 1;
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) SELECT 770404, 1, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = 30197 AND `ID` = 1;

DELETE FROM `npc_text` WHERE `ID` BETWEEN 7702100 AND 7702179;
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES
(7702101, 'Commander Aldren Hask, Knights of the Ebon Blade. The Highlord sent us to hold this hall while the dragons trade in it, and to make sure nothing the Lich King left behind gets up again.$B$BWe served him once. Most of the Scourge you will meet in Icecrown were raised by the same hand that raised me. Kill them cleanly, $c. They would thank you, if they could.', 'Commander Aldren Hask, Knights of the Ebon Blade. The Highlord sent us to hold this hall while the dragons trade in it, and to make sure nothing the Lich King left behind gets up again.$B$BWe served him once. Most of the Scourge you will meet in Icecrown were raised by the same hand that raised me. Kill them cleanly, $c. They would thank you, if they could.', 1),
(7702102, 'You smell of the surface, and of sand. The dragons vouch for you and the death knights tolerate you. That will do.$B$BWe are what is left of Azjol-Nerub that still breathes. The Scourge took our dead, our king and our craft: their ziggurats are our ziggurats, their necropolises our halls, built crooked by thieves. Malykriss is the first we have taken back.$B$BWhen your war reaches the Citadel, tell the Lich King the nerubians sent you.', 'You smell of the surface, and of sand. The dragons vouch for you and the death knights tolerate you. That will do.$B$BWe are what is left of Azjol-Nerub that still breathes. The Scourge took our dead, our king and our craft: their ziggurats are our ziggurats, their necropolises our halls, built crooked by thieves. Malykriss is the first we have taken back.$B$BWhen your war reaches the Citadel, tell the Lich King the nerubians sent you.', 1),
(7702103, 'Anub''arak was our king. Now he is the Lich King''s, somewhere under the ice, and he still answers to his name. One day someone will end that.$B$BI would like it to be one of us. I will settle for someone who remembers that he was ours.', 'Anub''arak was our king. Now he is the Lich King''s, somewhere under the ice, and he still answers to his name. One day someone will end that.$B$BI would like it to be one of us. I will settle for someone who remembers that he was ours.', 1),
(7702104, 'Look at the ribs above you. Unfinished, all of them. The Scourge build fast and badly; they learned from slaves who were afraid.$B$BWe are not afraid. Give me a hundred years and this will be a hall worth the name. The dragons tell me you will not be here in a hundred years. Pity.', 'Look at the ribs above you. Unfinished, all of them. The Scourge build fast and badly; they learned from slaves who were afraid.$B$BWe are not afraid. Give me a hundred years and this will be a hall worth the name. The dragons tell me you will not be here in a hundred years. Pity.', 1),
(7702105, 'I carry the Warlord''s words to the death knights, and theirs back to him. Most days that means carrying complaints about webs.$B$BThey are better company than they look. So are we.', 'I carry the Warlord''s words to the death knights, and theirs back to him. Most days that means carrying complaints about webs.$B$BThey are better company than they look. So are we.', 1);
DELETE FROM `gossip_menu` WHERE `MenuID` BETWEEN 77100 AND 77179;
INSERT INTO `gossip_menu` (`MenuID`, `TextID`) VALUES
(77101, 7702101),
(77102, 7702102),
(77103, 7702103),
(77104, 7702104),
(77105, 7702105);

DELETE FROM `creature_addon` WHERE `guid` BETWEEN 7706000 AND 7706999;
DELETE FROM `waypoint_data` WHERE `id` BETWEEN 7706000 AND 7706999;
DELETE FROM `creature` WHERE `guid` BETWEEN 7706000 AND 7706999;
INSERT INTO `creature` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `equipment_id`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(7706001, 770400, 571, 210, 4520, 1, 1, 1, 6352.00, 1936.00, 508.60, 1.5708, 60, 0.0, 0, 'Wrath Remix: Ebon Blade Gatewarden, Malykriss'),
(7706002, 770400, 571, 210, 4520, 1, 1, 1, 6338.00, 1936.00, 508.60, 1.5708, 60, 0.0, 0, 'Wrath Remix: Ebon Blade Gatewarden, Malykriss'),
(7706003, 770404, 571, 210, 4520, 1, 1, 1, 6402.00, 1772.00, 508.70, 1.6557, 60, 0.0, 0, 'Wrath Remix: Commander Aldren Hask, Malykriss'),
(7706004, 770417, 571, 210, 4520, 1, 1, 0, 6404.50, 1768.00, 508.70, 2.1294, 60, 0.0, 0, 'Wrath Remix: Azjol Envoy, Malykriss'),
(7706005, 770403, 571, 210, 4520, 1, 1, 1, 6415.00, 1755.00, 508.70, 1.5708, 60, 0.0, 0, 'Wrath Remix: Ebon Blade Duelist, Malykriss'),
(7706006, 770403, 571, 210, 4520, 1, 1, 1, 6415.00, 1758.50, 508.70, 4.7124, 60, 0.0, 0, 'Wrath Remix: Ebon Blade Duelist, Malykriss'),
(7706007, 770401, 571, 210, 4520, 1, 1, 1, 6386.00, 1789.00, 508.70, 1.4673, 60, 0.0, 0, 'Wrath Remix: Ebon Blade Sentinel, Malykriss'),
(7706008, 770401, 571, 210, 4520, 1, 1, 1, 6380.00, 1790.00, 508.70, 1.3886, 60, 0.0, 0, 'Wrath Remix: Ebon Blade Sentinel, Malykriss'),
(7706009, 770405, 571, 210, 4520, 1, 1, 0, 6428.00, 1782.00, 508.70, 1.5708, 60, 0.0, 0, 'Wrath Remix: Deathcharger, Malykriss'),
(7706010, 770405, 571, 210, 4520, 1, 1, 0, 6431.00, 1775.00, 508.70, 1.5708, 60, 0.0, 0, 'Wrath Remix: Deathcharger, Malykriss'),
(7706011, 770406, 571, 210, 4520, 1, 1, 0, 6430.00, 1760.00, 508.70, 3.3390, 60, 0.0, 0, 'Wrath Remix: Captured Atrocity, Malykriss'),
(7706012, 770402, 571, 210, 4520, 1, 1, 1, 6300.00, 1745.00, 525.30, 6.0382, 60, 0.0, 0, 'Wrath Remix: Ebon Blade Runesmith, Malykriss'),
(7706013, 770402, 571, 210, 4520, 1, 1, 1, 6316.00, 1733.00, 525.30, 1.9890, 60, 0.0, 0, 'Wrath Remix: Ebon Blade Runesmith, Malykriss'),
(7706014, 770402, 571, 210, 4520, 1, 1, 1, 6292.00, 1760.00, 525.30, 5.2023, 60, 0.0, 0, 'Wrath Remix: Ebon Blade Runesmith, Malykriss'),
(7706015, 770401, 571, 210, 4520, 1, 1, 1, 6552.00, 1645.00, 631.70, 2.0712, 60, 0.0, 0, 'Wrath Remix: Ebon Blade Sentinel, Malykriss'),
(7706016, 770413, 571, 210, 4520, 1, 1, 0, 6098.00, 1921.00, 632.70, 1.4902, 60, 0.0, 0, 'Wrath Remix: Azjol Warden, Malykriss'),
(7706020, 770410, 571, 210, 4520, 1, 1, 0, 6512.00, 1852.00, 514.00, 3.1416, 60, 0.0, 0, 'Wrath Remix: Warlord Kaz''anub, Malykriss'),
(7706021, 770411, 571, 210, 4520, 1, 1, 0, 6503.00, 1864.00, 512.90, 5.3559, 60, 0.0, 0, 'Wrath Remix: Elder Zek''thira, Malykriss'),
(7706022, 770412, 571, 210, 4520, 1, 1, 0, 6488.00, 1834.00, 509.90, 4.0451, 60, 0.0, 0, 'Wrath Remix: Architect Thekk''ri, Malykriss'),
(7706023, 770414, 571, 210, 4520, 1, 1, 0, 6478.00, 1866.00, 508.70, 5.3559, 60, 0.0, 0, 'Wrath Remix: Azjol Silkweaver, Malykriss'),
(7706024, 770414, 571, 210, 4520, 1, 1, 0, 6520.00, 1838.00, 515.00, 2.4669, 60, 0.0, 0, 'Wrath Remix: Azjol Silkweaver, Malykriss'),
(7706025, 770413, 571, 210, 4520, 1, 1, 0, 6466.00, 1850.00, 508.70, 3.1416, 60, 0.0, 0, 'Wrath Remix: Azjol Warden, Malykriss'),
(7706026, 770415, 571, 210, 4520, 1, 1, 0, 6495.00, 1848.00, 511.20, 0.0000, 60, 4.0, 1, 'Wrath Remix: Azjol Skitterer, Malykriss'),
(7706027, 770415, 571, 210, 4520, 1, 1, 0, 6500.00, 1842.00, 512.10, 0.0000, 60, 4.0, 1, 'Wrath Remix: Azjol Skitterer, Malykriss'),
(7706028, 770415, 571, 210, 4520, 1, 1, 0, 6490.00, 1856.00, 510.30, 0.0000, 60, 4.0, 1, 'Wrath Remix: Azjol Skitterer, Malykriss'),
(7706029, 770415, 571, 210, 4520, 1, 1, 0, 6505.00, 1850.00, 513.40, 0.0000, 60, 4.0, 1, 'Wrath Remix: Azjol Skitterer, Malykriss'),
(7706030, 770426, 571, 210, 4520, 1, 1, 0, 6485.00, 1872.00, 508.70, 0.0000, 60, 0.0, 0, 'Wrath Remix: Burrow, Malykriss'),
(7706031, 770426, 571, 210, 4520, 1, 1, 0, 6514.00, 1832.00, 514.00, 0.0000, 60, 0.0, 0, 'Wrath Remix: Burrow, Malykriss'),
(7706035, 770416, 571, 210, 4520, 1, 1, 0, 6492.00, 1805.00, 655.00, 1.5708, 60, 0.0, 0, 'Wrath Remix: Azjol Skyguard, Malykriss'),
(7706036, 770416, 571, 210, 4520, 1, 1, 0, 6262.00, 1805.00, 690.00, 4.7124, 60, 0.0, 0, 'Wrath Remix: Azjol Skyguard, Malykriss'),
(7706040, 770420, 571, 210, 4520, 1, 1, 0, 6394.00, 1898.00, 508.70, 0.0000, 60, 0.0, 0, 'Wrath Remix: Hourglass Sands, Malykriss'),
(7706041, 770422, 571, 210, 4520, 1, 1, 0, 6394.00, 1898.00, 512.60, 0.0000, 60, 0.0, 0, 'Wrath Remix: Hourglass''s Heart, Malykriss'),
(7706042, 770421, 571, 210, 4520, 1, 1, 0, 6394.00, 1891.00, 508.70, 1.5708, 60, 0.0, 0, 'Wrath Remix: Bazaar Sandshaper, Malykriss'),
(7706043, 770421, 571, 210, 4520, 1, 1, 0, 6394.00, 1905.00, 508.70, 4.7124, 60, 0.0, 0, 'Wrath Remix: Bazaar Sandshaper, Malykriss'),
(7706044, 770424, 571, 210, 4520, 1, 1, 0, 6394.00, 1898.00, 521.60, 0.0000, 60, 0.0, 0, 'Wrath Remix: Time Rift, Malykriss'),
(7706045, 770423, 571, 210, 4520, 1, 1, 0, 6403.00, 1898.00, 513.60, 0.0000, 60, 0.0, 0, 'Wrath Remix: Frost Sphere, Malykriss'),
(7706046, 770423, 571, 210, 4520, 1, 1, 0, 6385.00, 1898.00, 513.60, 0.0000, 60, 0.0, 0, 'Wrath Remix: Frost Sphere, Malykriss'),
(7706047, 770425, 571, 210, 4520, 1, 1, 0, 6345.00, 1950.00, 508.20, 0.0000, 60, 0.0, 0, 'Wrath Remix: Saronite Fog, Malykriss'),
(7706048, 770425, 571, 210, 4520, 1, 1, 0, 6308.00, 1872.00, 508.70, 0.0000, 60, 0.0, 0, 'Wrath Remix: Saronite Fog, Malykriss'),
(7706050, 770401, 571, 210, 4520, 1, 1, 1, 6345.00, 1926.00, 508.70, 0, 60, 0, 2, 'Wrath Remix: Ebon Blade Sentinel, Malykriss, on rounds'),
(7706051, 770413, 571, 210, 4520, 1, 1, 0, 6470.00, 1852.00, 508.70, 0, 60, 0, 2, 'Wrath Remix: Azjol Warden, Malykriss, on rounds'),
(7706052, 770401, 571, 210, 4520, 1, 1, 1, 6170.00, 1898.00, 632.70, 0, 60, 0, 2, 'Wrath Remix: Ebon Blade Sentinel, Malykriss, on rounds'),
(7706053, 770413, 571, 210, 4520, 1, 1, 0, 6547.00, 1810.00, 629.70, 0, 60, 0, 2, 'Wrath Remix: Azjol Warden, Malykriss, on rounds');
INSERT INTO `creature_addon` (`guid`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) VALUES
(7706001, 0, 25280, 0, 1, 0, 0, ''),
(7706002, 0, 25280, 0, 1, 0, 0, ''),
(7706005, 0, 0, 0, 1, 333, 0, ''),
(7706006, 0, 0, 0, 1, 333, 0, ''),
(7706012, 0, 0, 0, 1, 173, 0, ''),
(7706013, 0, 0, 0, 1, 173, 0, ''),
(7706023, 0, 0, 0, 1, 474, 0, ''),
(7706024, 0, 0, 0, 1, 474, 0, ''),
(7706050, 7706050, 25280, 0, 1, 0, 0, ''),
(7706051, 7706051, 0, 0, 1, 0, 0, ''),
(7706052, 7706052, 0, 0, 1, 0, 0, ''),
(7706053, 7706053, 0, 0, 1, 0, 0, '');
INSERT INTO `waypoint_data` (`id`, `point`, `position_x`, `position_y`, `position_z`, `orientation`, `delay`, `move_type`) VALUES
(7706050, 1, 6345.00, 1926.00, 508.70, NULL, 4000, 0),
(7706050, 2, 6318.00, 1884.00, 508.70, NULL, 0, 0),
(7706050, 3, 6318.00, 1832.00, 508.90, NULL, 0, 0),
(7706050, 4, 6345.00, 1806.00, 508.70, NULL, 0, 0),
(7706050, 5, 6392.00, 1790.00, 508.70, NULL, 0, 0),
(7706050, 6, 6425.00, 1768.00, 508.70, NULL, 3000, 0),
(7706050, 7, 6392.00, 1790.00, 508.70, NULL, 0, 0),
(7706050, 8, 6345.00, 1806.00, 508.70, NULL, 0, 0),
(7706050, 9, 6318.00, 1832.00, 508.90, NULL, 0, 0),
(7706050, 10, 6318.00, 1884.00, 508.70, NULL, 0, 0),
(7706051, 1, 6470.00, 1852.00, 508.70, NULL, 3000, 0),
(7706051, 2, 6450.00, 1828.00, 508.90, NULL, 0, 0),
(7706051, 3, 6448.00, 1790.00, 508.70, NULL, 0, 0),
(7706051, 4, 6470.00, 1760.00, 508.70, NULL, 0, 0),
(7706051, 5, 6500.00, 1730.00, 508.70, NULL, 4000, 0),
(7706051, 6, 6470.00, 1760.00, 508.70, NULL, 0, 0),
(7706051, 7, 6448.00, 1790.00, 508.70, NULL, 0, 0),
(7706051, 8, 6450.00, 1828.00, 508.90, NULL, 0, 0),
(7706052, 1, 6170.00, 1898.00, 632.70, NULL, 3000, 0),
(7706052, 2, 6260.00, 1939.00, 631.60, NULL, 0, 0),
(7706052, 3, 6350.00, 1952.00, 631.80, NULL, 0, 0),
(7706052, 4, 6440.00, 1964.00, 631.50, NULL, 5000, 0),
(7706052, 5, 6350.00, 1952.00, 631.80, NULL, 0, 0),
(7706052, 6, 6260.00, 1939.00, 631.60, NULL, 0, 0),
(7706053, 1, 6547.00, 1810.00, 629.70, NULL, 4000, 0),
(7706053, 2, 6547.00, 1720.00, 629.70, NULL, 0, 0),
(7706053, 3, 6552.00, 1650.00, 630.80, NULL, 0, 0),
(7706053, 4, 6555.00, 1600.00, 633.60, NULL, 4000, 0),
(7706053, 5, 6552.00, 1650.00, 630.80, NULL, 0, 0),
(7706053, 6, 6547.00, 1720.00, 629.70, NULL, 0, 0);

DELETE FROM `gameobject_template` WHERE `entry` BETWEEN 770220 AND 770259;
INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `IconName`, `castBarCaption`, `unk1`, `size`, `AIName`, `ScriptName`, `VerifiedBuild`) VALUES
(770220, 5, 8713, 'Ebon Blade Banner', '', '', '', 1.0, '', '', 0),
(770221, 5, 8175, 'Runeforge', '', '', '', 2.03, '', '', 0),
(770222, 5, 9195, 'Brazier', '', '', '', 1.0, '', '', 0),
(770223, 5, 8365, 'Blood Orb', '', '', '', 1.5, '', '', 0),
(770224, 5, 7803, 'Nerubian Egg', '', '', '', 1.2, '', '', 0),
(770225, 5, 7836, 'Chunk of Saronite', '', '', '', 0.5, '', '', 0),
(770226, 5, 7133, 'Hourglass', '', '', '', 0.012, '', '', 0);
DELETE FROM `gameobject` WHERE `guid` BETWEEN 7705400 AND 7705599;
INSERT INTO `gameobject` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`,
  `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`, `animprogress`, `state`, `ScriptName`, `VerifiedBuild`, `Comment`) VALUES
(7705400, 770220, 571, 210, 4520, 1, 1, 6356.00, 1939.00, 508.40, 1.5708, 0.000000, 0.000000, 0.707107, 0.707107, 300, 100, 1, '', 0, 'Wrath Remix: Ebon Blade Banner, the west gate'),
(7705401, 770220, 571, 210, 4520, 1, 1, 6334.00, 1939.00, 508.30, 1.5708, 0.000000, 0.000000, 0.707107, 0.707107, 300, 100, 1, '', 0, 'Wrath Remix: Ebon Blade Banner, the west gate'),
(7705402, 770223, 571, 210, 4520, 1, 1, 6358.00, 1930.00, 508.60, 0.0000, 0.000000, 0.000000, 0.000000, 1.000000, 300, 100, 1, '', 0, 'Wrath Remix: Blood Orb, the west gate'),
(7705403, 770223, 571, 210, 4520, 1, 1, 6332.00, 1930.00, 508.60, 0.0000, 0.000000, 0.000000, 0.000000, 1.000000, 300, 100, 1, '', 0, 'Wrath Remix: Blood Orb, the west gate'),
(7705404, 770220, 571, 210, 4520, 1, 1, 6408.00, 1792.00, 508.60, 1.7578, 0.000000, 0.000000, 0.770030, 0.638008, 300, 100, 1, '', 0, 'Wrath Remix: Ebon Blade Banner, the Ebon Blade''s quarter'),
(7705405, 770220, 571, 210, 4520, 1, 1, 6376.00, 1795.00, 508.60, 1.3225, 0.000000, 0.000000, 0.614106, 0.789223, 300, 100, 1, '', 0, 'Wrath Remix: Ebon Blade Banner, the Ebon Blade''s quarter'),
(7705406, 770221, 571, 210, 4520, 1, 1, 6416.00, 1740.00, 508.60, 1.5708, 0.000000, 0.000000, 0.707107, 0.707107, 300, 100, 1, '', 0, 'Wrath Remix: Runeforge, the Ebon Blade''s quarter'),
(7705407, 770222, 571, 210, 4520, 1, 1, 6390.00, 1742.00, 508.60, 0.0000, 0.000000, 0.000000, 0.000000, 1.000000, 300, 100, 1, '', 0, 'Wrath Remix: Brazier, the Ebon Blade''s quarter'),
(7705408, 770222, 571, 210, 4520, 1, 1, 6395.00, 1760.00, 508.60, 0.0000, 0.000000, 0.000000, 0.000000, 1.000000, 300, 100, 1, '', 0, 'Wrath Remix: Brazier, the Ebon Blade''s quarter'),
(7705409, 770222, 571, 210, 4520, 1, 1, 6412.00, 1778.00, 508.60, 0.0000, 0.000000, 0.000000, 0.000000, 1.000000, 300, 100, 1, '', 0, 'Wrath Remix: Brazier, the Ebon Blade''s quarter'),
(7705410, 770224, 571, 210, 4520, 1, 1, 6523.00, 1858.00, 514.90, 0.4000, 0.000000, 0.000000, 0.198669, 0.980067, 300, 100, 1, '', 0, 'Wrath Remix: Nerubian Egg, the nerubians'' hall'),
(7705411, 770224, 571, 210, 4520, 1, 1, 6519.00, 1846.00, 514.90, 1.9000, 0.000000, 0.000000, 0.813416, 0.581683, 300, 100, 1, '', 0, 'Wrath Remix: Nerubian Egg, the nerubians'' hall'),
(7705412, 770224, 571, 210, 4520, 1, 1, 6470.00, 1866.00, 508.60, 3.1000, 0.000000, 0.000000, 0.999784, 0.020795, 300, 100, 1, '', 0, 'Wrath Remix: Nerubian Egg, the nerubians'' hall'),
(7705413, 770224, 571, 210, 4520, 1, 1, 6476.00, 1834.00, 508.60, 5.0000, -0.000000, 0.000000, 0.598472, -0.801144, 300, 100, 1, '', 0, 'Wrath Remix: Nerubian Egg, the nerubians'' hall'),
(7705414, 770224, 571, 210, 4520, 1, 1, 6480.00, 1868.00, 508.60, 2.6000, 0.000000, 0.000000, 0.963558, 0.267499, 300, 100, 1, '', 0, 'Wrath Remix: Nerubian Egg, the nerubians'' hall'),
(7705415, 770225, 571, 210, 4520, 1, 1, 6486.00, 1830.00, 509.30, 0.7000, 0.000000, 0.000000, 0.342898, 0.939373, 300, 100, 1, '', 0, 'Wrath Remix: Chunk of Saronite, the nerubians'' hall, the architect''s'),
(7705416, 770225, 571, 210, 4520, 1, 1, 6491.00, 1829.00, 510.20, 2.2000, 0.000000, 0.000000, 0.891207, 0.453596, 300, 100, 1, '', 0, 'Wrath Remix: Chunk of Saronite, the nerubians'' hall, the architect''s'),
(7705417, 770226, 571, 210, 4520, 1, 1, 6378.00, 1893.00, 513.60, 0.3000, 0.172153, 0.026018, 0.147156, 0.973669, 300, 100, 1, '', 0, 'Wrath Remix: Hourglass, the market lane, held in time'),
(7705418, 770226, 571, 210, 4520, 1, 1, 6369.00, 1893.00, 514.40, 2.1000, -0.062035, -0.108146, 0.860655, 0.493689, 300, 100, 1, '', 0, 'Wrath Remix: Hourglass, the market lane, held in time'),
(7705419, 770226, 571, 210, 4520, 1, 1, 6360.00, 1893.00, 513.20, 4.0000, -0.092845, 0.202870, 0.886378, -0.405657, 300, 100, 1, '', 0, 'Wrath Remix: Hourglass, the market lane, held in time'),
(7705420, 770226, 571, 210, 4520, 1, 1, 6351.00, 1893.00, 514.00, 5.2000, 0.170238, -0.102414, 0.505226, -0.839808, 300, 100, 1, '', 0, 'Wrath Remix: Hourglass, the market lane, held in time'),
(7705421, 770226, 571, 210, 4520, 1, 1, 6342.00, 1893.00, 513.60, 1.0000, 0.087612, 0.047863, 0.477030, 0.873198, 300, 100, 1, '', 0, 'Wrath Remix: Hourglass, the market lane, held in time');

DELETE FROM `remix_bazaar_line` WHERE `guid` BETWEEN 7706000 AND 7706999;
INSERT INTO `remix_bazaar_line` (`guid`, `line`, `text`, `emote`, `reply_guid`, `reply`, `reply_emote`) VALUES
(7706001, 0, 'Nothing comes through this gate that the Ebon Blade has not seen first.', 0, 0, '', 0),
(7706001, 1, 'Quiet out there tonight.', 1, 7706002, 'It is always quiet before the Citadel sends something.', 0),
(7706002, 0, 'We served him once. Every one of us remembers the day we stopped.', 0, 0, '', 0),
(7706003, 0, 'Malykriss was to be his new Acherus. We took the old one from him. The dragons took this one from his calendar.', 1, 0, '', 0),
(7706003, 1, 'Your Warlord wants the east stair.', 1, 7706004, 'The Warlord wants everything. He will settle for the east stair.', 0),
(7706003, 2, 'If anything in this hall tries to kill you, it is not one of mine.', 0, 0, '', 0),
(7706004, 0, 'The death knights keep their gate and we keep our webs. Nobody has been eaten yet.', 1, 0, '', 0),
(7706007, 0, 'Keep to the floor, Timerunner. The edges are older than they look.', 0, 0, '', 0),
(7706008, 0, 'A sword that has been cursed twice still cuts. So does a knight.', 0, 0, '', 0),
(7706012, 0, 'A rune is a promise cut into steel. Ours we keep now.', 0, 0, '', 0),
(7706012, 1, 'The Scourge left these forges warm. It would be rude not to use them.', 11, 0, '', 0),
(7706013, 0, 'Bring your blade, if it is worth the trouble. Razorice, Fallen Crusader, Cinderglacier: the forge does not care which side you were on.', 1, 0, '', 0),
(7706015, 0, 'He built this place to watch over Icecrown. Now it watches him.', 0, 0, '', 0),
(7706015, 1, 'From up here you can count the Citadel''s lights. I stopped counting.', 0, 0, '', 0),
(7706016, 0, 'They sacrificed our dead on this altar. Now I stand on it, and I am not dead.', 0, 0, '', 0),
(7706020, 0, 'The Lich King broke Azjol-Nerub and made our king his hound. We have long memories, surface-walker. Longer than his reign.', 1, 0, '', 0),
(7706020, 1, 'Arthas walked through our dead city with Anub''arak at his heel. I watched from the dark. I am done watching.', 0, 0, '', 0),
(7706020, 2, 'The death knights walked through the webs again.', 1, 7706021, 'Then we weave them stronger. They were his once, as our dead are. Patience.', 0),
(7706021, 0, 'The dragons say this hour sits outside his reach. I have heard promises before. I am weaving anyway.', 0, 0, '', 0),
(7706022, 0, 'Saronite remembers every shape you give it. That is why we build slowly.', 0, 0, '', 0),
(7706022, 1, 'He wanted a fortress to replace Acherus. He will find it has new tenants.', 11, 0, '', 0),
(7706023, 0, 'Shh. The silk listens.', 0, 0, '', 0),
(7706025, 0, 'Mind the webs, surface-walker. They are older than your city.', 0, 0, '', 0),
(7706050, 0, 'Make way. Ebon Blade, on our rounds.', 0, 0, '', 0),
(7706051, 0, 'The halls are quiet. The quiet is ours now.', 0, 0, '', 0),
(7706052, 0, 'The wind off the Citadel smells of saronite and old blood. You get used to it. I hope you never do.', 0, 0, '', 0);
