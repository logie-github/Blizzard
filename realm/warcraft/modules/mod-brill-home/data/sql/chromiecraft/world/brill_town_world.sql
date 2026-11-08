-- Brill: A Place Among the Forsaken (mod-brill-home; ChromieCraft's world database alone: ctl.sh
-- realm_sql). Made by tools/build_town.py from tools/town/*.py; don't edit by hand. Written to be
-- applied again: its own rows go first.

CREATE TABLE IF NOT EXISTS `brill_town_phase` (`bit` INT UNSIGNED NOT NULL, `ord` INT UNSIGNED NOT NULL, `cond` VARCHAR(255) NOT NULL DEFAULT '', PRIMARY KEY (`bit`, `ord`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS `brill_town_gossip` (`npc` INT UNSIGNED NOT NULL, `ord` INT UNSIGNED NOT NULL, `kind` VARCHAR(8) NOT NULL, `cond` VARCHAR(255) NOT NULL DEFAULT '', `icon` TINYINT UNSIGNED NOT NULL DEFAULT 0, `text` TEXT, `text_id` INT UNSIGNED NOT NULL DEFAULT 0, `action` VARCHAR(16) NOT NULL DEFAULT '', `quest` INT UNSIGNED NOT NULL DEFAULT 0, `credit` INT UNSIGNED NOT NULL DEFAULT 0, `marker` INT UNSIGNED NOT NULL DEFAULT 0, `emote` INT UNSIGNED NOT NULL DEFAULT 0, `reply` TEXT, `arg` INT UNSIGNED NOT NULL DEFAULT 0, PRIMARY KEY (`npc`, `ord`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS `brill_town_stage` (`type` TINYINT UNSIGNED NOT NULL, `value` INT NOT NULL, `ord` INT UNSIGNED NOT NULL, `cond` VARCHAR(255) NOT NULL DEFAULT '', PRIMARY KEY (`type`, `value`, `ord`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS `brill_town_invis` (`kind` CHAR(1) NOT NULL, `guid` INT UNSIGNED NOT NULL, `type` TINYINT UNSIGNED NOT NULL, `value` INT NOT NULL, PRIMARY KEY (`kind`, `guid`, `type`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
DELETE FROM `brill_town_stage`;
DELETE FROM `brill_town_invis`;
DROP TABLE IF EXISTS `brill_town_use`;
CREATE TABLE `brill_town_use` (`go` INT UNSIGNED NOT NULL, `ord` INT UNSIGNED NOT NULL, `cond` VARCHAR(255) NOT NULL DEFAULT '', `quest` INT UNSIGNED NOT NULL DEFAULT 0, `credit` INT UNSIGNED NOT NULL DEFAULT 0, `text_id` INT UNSIGNED NOT NULL DEFAULT 0, `marker` INT UNSIGNED NOT NULL DEFAULT 0, `tele_map` INT NOT NULL DEFAULT -1, `tele_x` FLOAT NOT NULL DEFAULT 0, `tele_y` FLOAT NOT NULL DEFAULT 0, `tele_z` FLOAT NOT NULL DEFAULT 0, `tele_o` FLOAT NOT NULL DEFAULT 0, PRIMARY KEY (`go`, `ord`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
DELETE FROM `brill_town_phase`;
DELETE FROM `brill_town_gossip`;
DELETE FROM `brill_town_use`;
DELETE FROM `creature_template` WHERE `entry` BETWEEN 970200 AND 971699;
DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN 970200 AND 971699;
DELETE FROM `creature` WHERE `guid` BETWEEN 970200 AND 971699;
DELETE FROM `gameobject_template` WHERE `entry` BETWEEN 970200 AND 971699;
DELETE FROM `gameobject` WHERE `guid` BETWEEN 970200 AND 971699;
DELETE FROM `npc_text` WHERE `ID` BETWEEN 970200 AND 971699;
DELETE FROM `quest_template` WHERE `ID` BETWEEN 970200 AND 971699;
DELETE FROM `quest_template_addon` WHERE `ID` BETWEEN 970200 AND 971699;
DELETE FROM `quest_offer_reward` WHERE `ID` BETWEEN 970200 AND 971699;
DELETE FROM `quest_request_items` WHERE `ID` BETWEEN 970200 AND 971699;
DELETE FROM `creature_queststarter` WHERE `quest` BETWEEN 970200 AND 971699;
DELETE FROM `creature_questender` WHERE `quest` BETWEEN 970200 AND 971699;
DELETE FROM `smart_scripts` WHERE `entryorguid` BETWEEN 970200 AND 971699 AND `source_type` = 0;
DELETE FROM `gameobject_template_addon` WHERE `entry` BETWEEN 970200 AND 971699;
DELETE FROM `npc_vendor` WHERE `entry` BETWEEN 970200 AND 971699;
DELETE FROM `game_event_creature` WHERE `guid` BETWEEN 970200 AND 971699;
DELETE FROM `game_event_gameobject` WHERE `guid` BETWEEN 970200 AND 971699;
DELETE FROM `creature_default_trainer` WHERE `CreatureId` BETWEEN 970200 AND 971699;
DELETE FROM `creature_template_movement` WHERE `CreatureId` BETWEEN 970200 AND 971699;
DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 19 AND `SourceEntry` BETWEEN 970200 AND 971699;
DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 23 AND `SourceGroup` BETWEEN 970200 AND 971699;
DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 30 AND `SourceEntry` BETWEEN 970200 AND 971699;
DELETE FROM `game_event` WHERE `eventEntry` IN (230, 231, 232, 233);
DELETE FROM `gameobjectdisplayinfo_dbc` WHERE `ID` BETWEEN 9700 AND 9709;
INSERT INTO `gameobjectdisplayinfo_dbc` (`ID`, `ModelName`, `Sound_1`, `Sound_2`, `Sound_3`, `Sound_4`, `Sound_5`, `Sound_6`, `Sound_7`, `Sound_8`, `Sound_9`, `Sound_10`, `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`, `GeoBoxMaxX`, `GeoBoxMaxY`, `GeoBoxMaxZ`, `ObjectEffectPackageID`) VALUES
(9700, 'World\\wmo\\Azeroth\\Buildings\\Duskwood_Inn\\Duskwood_Inn.wmo', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -37.7, -13.5, -6.7, 21.9, 18.7, 23.2, 0),
(9701, 'World\\Expansion02\\Doodads\\Generic\\Human\\Northrend_HumanLadder\\Final\\HU_HumanLadder.mdx', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -0.04, -0.18, 0.0, 0.04, 0.37, 3.55, 0);
INSERT INTO `game_event` (`eventEntry`, `start_time`, `end_time`, `occurence`, `length`, `holiday`, `description`, `world_event`, `announce`) VALUES
(230, '2020-01-01 06:00:00', '2037-12-31 00:00:00', 1440, 240, 0, 'Brill: morning', 0, 0),
(231, '2020-01-01 10:00:00', '2037-12-31 00:00:00', 1440, 480, 0, 'Brill: day', 0, 0),
(232, '2020-01-01 18:00:00', '2037-12-31 00:00:00', 1440, 240, 0, 'Brill: evening', 0, 0),
(233, '2020-01-01 22:00:00', '2037-12-31 00:00:00', 1440, 480, 0, 'Brill: night', 0, 0);

-- The New House
INSERT INTO `creature_template` (`entry`, `name`, `subname`, `gossip_menu_id`, `minlevel`, `maxlevel`, `faction`, `npcflag`, `speed_walk`, `speed_run`, `unit_class`, `unit_flags`, `type`, `rank`, `HealthModifier`, `DamageModifier`, `mingold`, `maxgold`, `flags_extra`, `AIName`, `ScriptName`) VALUES
(970200, 'Oswin Thatcher', 'Carpenter', 0, 25, 25, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(970201, 'Cellar Rat', NULL, 0, 5, 6, 14, 0, 1, 1.14286, 1, 0, 1, 0, 0.7, 0.7, 0, 0, 0, '', ''),
(970202, 'Innkeeper Renee', NULL, 0, 20, 20, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(970203, 'Apothecary Johaan', NULL, 0, 20, 20, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(970204, 'Hamlin Atkins', NULL, 0, 20, 20, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(970205, 'Deathguard Dillinger', NULL, 0, 20, 20, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(970206, 'Broken furniture inspected', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970207, 'Rotten floorboards inspected', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970208, 'Leaking roof inspected', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970209, 'Cellar hatch inspected', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970210, 'Salvageable lumber', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970211, 'Bucket of nails', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970212, 'Cedric\'s letters read', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970213, 'The portrait found', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970214, 'The chest opened', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970215, 'The bricked-up wall examined', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970216, 'Candles and lamp oil', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970217, 'Linens', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970218, 'Clean straw', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970219, 'Furnishings chosen', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970220, 'Neighbors invited', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', '');
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`) VALUES
(970200, 0, 1638, 1, 1),
(970201, 0, 1141, 1.3, 1),
(970201, 1, 1418, 1.3, 1),
(970201, 2, 2176, 1.3, 1),
(970202, 0, 8190, 1, 1),
(970203, 0, 1565, 1, 1),
(970204, 0, 1635, 1, 1),
(970205, 0, 2855, 1, 1),
(970206, 0, 11686, 1, 1),
(970207, 0, 11686, 1, 1),
(970208, 0, 11686, 1, 1),
(970209, 0, 11686, 1, 1),
(970210, 0, 11686, 1, 1),
(970211, 0, 11686, 1, 1),
(970212, 0, 11686, 1, 1),
(970213, 0, 11686, 1, 1),
(970214, 0, 11686, 1, 1),
(970215, 0, 11686, 1, 1),
(970216, 0, 11686, 1, 1),
(970217, 0, 11686, 1, 1),
(970218, 0, 11686, 1, 1),
(970219, 0, 11686, 1, 1),
(970220, 0, 11686, 1, 1);
INSERT INTO `creature_template_movement` (`CreatureId`, `Ground`, `Swim`, `Flight`, `Rooted`, `Chase`, `Random`, `InteractionPauseTimer`) VALUES (970201, 1, 1, 2, 0, 0, 0, 0);
INSERT INTO `creature` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(970200, 970200, 0, 85, 0, 1, 1, 2264.577, 479.898, 33.810, 0.3491, 60, 0, 0, 'mod-brill-home town'),
(970201, 970201, 0, 85, 0, 1, 524288, 2274.913, 483.661, -2.720, 5.2360, 30, 0, 0, 'mod-brill-home town'),
(970202, 970201, 0, 85, 0, 1, 524288, 2280.552, 485.713, -2.720, 2.2690, 30, 0, 0, 'mod-brill-home town'),
(970203, 970201, 0, 85, 0, 1, 524288, 2281.324, 474.821, -2.720, 0.1746, 30, 0, 0, 'mod-brill-home town'),
(970204, 970201, 0, 85, 0, 1, 524288, 2272.867, 471.742, -2.720, 4.0143, 30, 0, 0, 'mod-brill-home town'),
(970205, 970201, 0, 85, 0, 1, 524288, 2274.656, 487.292, -2.720, 1.2218, 30, 0, 0, 'mod-brill-home town'),
(970206, 970201, 0, 85, 0, 1, 524288, 2268.979, 475.115, -2.720, 5.8469, 30, 0, 0, 'mod-brill-home town'),
(970207, 970202, 0, 85, 0, 1, 2097152, 2273.359, 481.499, 34.060, 5.4106, 60, 0, 0, 'mod-brill-home town'),
(970208, 970203, 0, 85, 0, 1, 2097152, 2275.402, 478.518, 34.060, 1.5708, 60, 0, 0, 'mod-brill-home town'),
(970209, 970204, 0, 85, 0, 1, 2097152, 2274.291, 479.816, 34.060, 4.0143, 60, 0, 0, 'mod-brill-home town'),
(970210, 970205, 0, 85, 0, 1, 2097152, 2270.130, 480.430, 34.060, 0.3491, 60, 0, 0, 'mod-brill-home town');
INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `Data0`, `Data1`, `ScriptName`) VALUES
(970200, 10, 6682, 'Broken Furniture', 1, 0, 970200, 'go_brill_town'),
(970201, 10, 6682, 'Rotten Floorboards', 0.5, 0, 970200, 'go_brill_town'),
(970202, 10, 239, 'Leaking Roof', 1, 0, 970200, 'go_brill_town'),
(970203, 2, 6481, 'Cellar Hatch', 1, 0, 0, 'go_brill_town'),
(970204, 33, 9700, 'Harrow Cellar', 1, 0, 0, ''),
(970205, 2, 9701, 'Cellar Ladder', 1.8, 0, 0, 'go_brill_town'),
(970206, 5, 461, 'Rats\' Nest', 0.35, 0, 0, ''),
(970207, 10, 6718, 'Bricked-Up Stair', 1.2, 0, 970203, 'go_brill_town'),
(970208, 10, 220, 'Bundle of Letters', 1, 0, 970202, 'go_brill_town'),
(970209, 10, 2850, 'Faded Portrait', 0.9, 0, 970202, 'go_brill_town'),
(970210, 10, 1, 'Rusted Chest', 1, 0, 970202, 'go_brill_town'),
(970211, 5, 6038, 'Lantern', 1, 0, 0, ''),
(970212, 5, 240, 'Candelabra', 1, 0, 0, ''),
(970213, 5, 5743, 'Storage Chest', 1, 0, 0, ''),
(970214, 5, 5911, 'Straw Dog Bed', 1, 0, 0, ''),
(970215, 10, 1108, 'Salvageable Lumber', 1, 0, 970201, 'go_brill_town'),
(970216, 10, 239, 'Bucket of Nails', 1, 0, 970201, 'go_brill_town');
INSERT INTO `gameobject_template_addon` (`entry`, `faction`, `flags`) VALUES (970204, 0, 32), (970200, 0, 4), (970201, 0, 4), (970202, 0, 4), (970207, 0, 4), (970208, 0, 4), (970209, 0, 4), (970210, 0, 4), (970215, 0, 4), (970216, 0, 4);
INSERT INTO `gameobject` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`, `animprogress`, `state`, `Comment`) VALUES
(970200, 970200, 0, 85, 0, 1, 262144, 2274.316, 480.624, 34.060, 5.0615, 0, 0, 0.573558, -0.819165, 0, 255, 1, 'mod-brill-home town'),
(970201, 970201, 0, 85, 0, 1, 262144, 2279.139, 480.677, 34.060, 5.0615, 0, 0, 0.573558, -0.819165, 0, 255, 1, 'mod-brill-home town'),
(970202, 970202, 0, 85, 0, 1, 262144, 2272.078, 480.926, 34.060, 5.0615, 0, 0, 0.573558, -0.819165, 0, 255, 1, 'mod-brill-home town'),
(970203, 970203, 0, 85, 0, 1, 1, 2275.185, 477.800, 34.060, 5.0615, 0, 0, 0.573558, -0.819165, 0, 255, 1, 'mod-brill-home town'),
(970204, 970204, 0, 85, 0, 1, 1, 2282.356, 454.445, 4.000, 5.0615, 0, 0, 0.573558, -0.819165, 0, 255, 1, 'mod-brill-home town'),
(970205, 970205, 0, 85, 0, 1, 1, 2268.060, 487.871, -2.720, 5.0615, 0, 0, 0.573558, -0.819165, 0, 255, 1, 'mod-brill-home town'),
(970206, 970206, 0, 85, 0, 1, 1, 2264.456, 484.324, -2.370, 5.0615, 0, 0, 0.573558, -0.819165, 0, 255, 1, 'mod-brill-home town'),
(970207, 970207, 0, 85, 0, 1, 1, 2264.824, 482.436, -1.770, 5.0615, 0, 0, 0.573558, -0.819165, 0, 255, 1, 'mod-brill-home town'),
(970208, 970208, 0, 85, 0, 1, 1, 2275.454, 476.036, 34.060, 5.0615, 0, 0, 0.573558, -0.819165, 0, 255, 1, 'mod-brill-home town'),
(970209, 970209, 0, 85, 0, 1, 1, 2280.173, 481.053, 37.360, 3.4907, 0, 0, 0.984804, -0.173670, 0, 255, 1, 'mod-brill-home town'),
(970210, 970210, 0, 85, 0, 1, 1, 2275.822, 475.319, 34.060, 1.9199, 0, 0, 0.819165, 0.573558, 0, 255, 1, 'mod-brill-home town'),
(970211, 970211, 0, 85, 0, 1, 1048576, 2269.130, 482.301, 38.160, 0.3491, 0, 0, 0.173670, 0.984804, 0, 255, 1, 'mod-brill-home town'),
(970212, 970211, 0, 85, 0, 1, 1048576, 2276.819, 482.226, 38.660, 5.0615, 0, 0, 0.573558, -0.819165, 0, 255, 1, 'mod-brill-home town'),
(970213, 970212, 0, 85, 0, 1, 1048576, 2275.998, 484.482, 35.360, 5.0615, 0, 0, 0.573558, -0.819165, 0, 255, 1, 'mod-brill-home town'),
(970214, 970213, 0, 85, 0, 1, 1048576, 2275.972, 486.015, 34.060, 5.0615, 0, 0, 0.573558, -0.819165, 0, 255, 1, 'mod-brill-home town'),
(970215, 970214, 0, 85, 0, 1, 1048576, 2278.904, 480.591, 34.060, 0.3491, 0, 0, 0.173670, 0.984804, 0, 255, 1, 'mod-brill-home town'),
(970216, 970215, 0, 85, 0, 1, 1, 2828.000, 1049.000, 110.900, 1.0000, 0, 0, 0.479426, 0.877583, 0, 255, 1, 'mod-brill-home town'),
(970217, 970215, 0, 85, 0, 1, 1, 2750.000, 780.000, 113.200, 2.0000, 0, 0, 0.841471, 0.540302, 0, 255, 1, 'mod-brill-home town'),
(970218, 970215, 0, 85, 0, 1, 1, 2258.000, 1308.000, 33.400, 0.5000, 0, 0, 0.247404, 0.968912, 0, 255, 1, 'mod-brill-home town'),
(970219, 970215, 0, 85, 0, 1, 1, 2446.000, 488.000, 44.300, 4.0000, 0, 0, 0.909297, -0.416147, 0, 255, 1, 'mod-brill-home town'),
(970220, 970215, 0, 85, 0, 1, 1, 2060.000, 560.000, 39.000, 3.0000, 0, 0, 0.997495, 0.070737, 0, 255, 1, 'mod-brill-home town'),
(970221, 970216, 0, 85, 0, 1, 1, 2268.000, 1306.000, 33.400, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town');
INSERT INTO `brill_town_use` (`go`, `ord`, `cond`, `quest`, `credit`, `text_id`, `marker`, `tele_map`, `tele_x`, `tele_y`, `tele_z`, `tele_o`) VALUES
(970200, 0, 'I970200', 970200, 970206, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970201, 0, 'I970200', 970200, 970207, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970202, 0, 'I970200', 970200, 970208, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970203, 0, 'I970200', 970200, 970209, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970203, 1, 'O', 0, 0, 0, 0, 0, 2268.436, 486.837, -2.420, 5.0615),
(970205, 0, '', 0, 0, 0, 0, 0, 2276.735, 478.365, 34.260, 3.4907),
(970207, 0, 'I970203', 970203, 970215, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970208, 0, 'I970202', 970202, 970212, 970200, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970209, 0, 'I970202', 970202, 970213, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970210, 0, 'I970202', 970202, 970214, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970215, 0, 'I970201', 970201, 970210, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970216, 0, 'I970201', 970201, 970211, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000);
INSERT INTO `brill_town_gossip` (`npc`, `ord`, `kind`, `cond`, `icon`, `text`, `text_id`, `action`, `quest`, `credit`, `marker`, `emote`, `reply`, `arg`) VALUES
(970200, 0, 'greet', '!O', 0, NULL, 970201, '', 0, 0, 0, 0, NULL, 0),
(970200, 1, 'greet', 'I970204 F80', 0, NULL, 970202, '', 0, 0, 0, 0, NULL, 0),
(970200, 2, 'greet', 'R970205 F80', 0, NULL, 970203, '', 0, 0, 0, 0, NULL, 0),
(970200, 3, 'greet', 'R970205', 0, NULL, 970204, '', 0, 0, 0, 0, NULL, 0),
(970200, 4, 'greet', 'R970203', 0, NULL, 970205, '', 0, 0, 0, 0, NULL, 0),
(970200, 5, 'greet', '', 0, NULL, 970206, '', 0, 0, 0, 0, NULL, 0),
(970200, 6, 'option', 'R970205 O', 1, 'I\'d like more furniture for the house.', 0, 'upgrades', 0, 0, 0, 0, NULL, 0),
(970200, 7, 'option', 'I970204 !U0', 0, 'A kitchen table and two chairs.', 0, 'furnish', 970204, 970219, 0, 0, 'A table. Good. Every house argues better over a table.', 0),
(970200, 8, 'option', 'I970204 !U1', 0, 'A wardrobe.', 0, 'furnish', 970204, 970219, 0, 0, 'A wardrobe. Cedar, so the moths stay out. The moths here are the size of bats.', 1),
(970200, 9, 'option', 'I970204 !U2', 0, 'A bookshelf.', 0, 'furnish', 970204, 970219, 0, 0, 'A bookshelf. A reader, then. Brill could use one.', 2),
(970200, 10, 'option', 'I970204 !U3', 0, 'A bearskin rug.', 0, 'furnish', 970204, 970219, 0, 0, 'A rug. I\'ll ask the trappers. The bear won\'t mind.', 3),
(970200, 11, 'option', 'I970204 !U4', 0, 'A pot-bellied stove.', 0, 'furnish', 970204, 970219, 0, 0, 'A stove. Proper heat. Your living guests will thank you, and your dead ones will pretend to.', 4),
(970200, 12, 'option', 'I970204', 0, 'It\'s furnished enough. Keep the wood for something else.', 0, 'credit', 970204, 970219, 0, 0, 'Suit yourself. I\'ll put it toward the shelves.', 0),
(2118, 13, 'option', 'I970204', 0, 'Oswin Thatcher sent me for candles and lamp oil.', 0, 'credit', 970204, 970216, 0, 0, 'For Cedric\'s old place? About time someone lit a lamp in it. Here. Tell Oswin they\'re on Jamie\'s account. She\'ll love that.', 0),
(2134, 14, 'option', 'I970204', 0, 'I need linens for my house. Not the gray ones.', 0, 'credit', 970204, 970217, 0, 0, 'Not the gray ones! Oswin\'s been talking. Fine. The cream, then. They were my mother\'s pattern. Don\'t bleed on them.', 0),
(10055, 15, 'option', 'I970204', 0, 'Could I have some clean straw? For my dog\'s bed.', 0, 'credit', 970204, 970218, 0, 0, 'Clean straw, for a living dog. Do you know how long it\'s been since anyone in Brill asked me for something for a living animal? Take two armfuls.', 0),
(5688, 16, 'option', 'I970205', 0, 'Come to a housewarming at my place.', 0, 'credit', 970205, 970220, 970206, 4, 'A party? In Brill? I\'ll bring the cider. Nobody can taste it, but everybody remembers the smell.', 0),
(1518, 17, 'option', 'I970205', 0, 'Would you come to a housewarming at my house, Apothecary?', 0, 'credit', 970205, 970220, 970207, 0, 'A social obligation. How quaint. ...Yes, very well. I\'ll bring something. Something non-lethal, I suppose.', 0),
(3547, 18, 'option', 'I970205', 0, 'You\'re invited to my housewarming, neighbor.', 0, 'credit', 970205, 970220, 970208, 4, 'Neighbor! Nobody\'s called me that in years. I\'ll bring mushrooms. The good ones. The ones that don\'t talk back.', 0),
(1496, 19, 'option', 'I970205', 0, 'There\'s a housewarming at my house. You should come.', 0, 'credit', 970205, 970220, 970209, 0, 'I\'m on watch. ...I\'ll watch from your doorway, then. Same thing, with walls.', 0),
(970202, 20, 'greet', 'F80', 0, NULL, 970207, '', 0, 0, 0, 0, NULL, 0),
(970202, 21, 'greet', '', 0, NULL, 970208, '', 0, 0, 0, 0, NULL, 0),
(970203, 22, 'greet', '', 0, NULL, 970209, '', 0, 0, 0, 0, NULL, 0),
(970204, 23, 'greet', 'F2', 0, NULL, 970210, '', 0, 0, 0, 0, NULL, 0),
(970204, 24, 'greet', '', 0, NULL, 970211, '', 0, 0, 0, 0, NULL, 0),
(970205, 25, 'greet', '', 0, NULL, 970212, '', 0, 0, 0, 0, NULL, 0);
UPDATE `creature_template` SET `npcflag` = `npcflag` | 1 WHERE `entry` IN (1496, 1518, 2118, 2134, 3547, 5688, 10055);
INSERT INTO `brill_town_phase` (`bit`, `ord`, `cond`) VALUES
(262144, 0, 'O !R970201'),
(524288, 0, 'A970203'),
(1048576, 0, 'R970204'),
(2097152, 0, 'C970205'),
(2097152, 1, 'R970205 D4');
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `Flags`, `RewardXPDifficulty`, `RewardMoney`, `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `AreaDescription`, `QuestCompletionLog`, `RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `ObjectiveText1`, `RequiredNpcOrGo2`, `RequiredNpcOrGoCount2`, `ObjectiveText2`, `RequiredNpcOrGo3`, `RequiredNpcOrGoCount3`, `ObjectiveText3`, `RequiredNpcOrGo4`, `RequiredNpcOrGoCount4`, `ObjectiveText4`, `RewardItem1`, `RewardAmount1`, `RewardItem2`, `RewardAmount2`, `RewardItem3`, `RewardAmount3`, `RewardItem4`, `RewardAmount4`) VALUES
(970200, 2, -1, 5, 159, 0, 2, 1500, 0, 'The Place Is Yours', 'Inspect the house with Oswin Thatcher: the broken furniture, the rotten floorboards, the leaking roof and the cellar hatch.', 'You\'ll be the new owner, then. Oswin Thatcher, carpenter, late of the Undercity\'s Rogues\' Quarter, and before that of a town that doesn\'t exist anymore. Jamie Nore sent for me. She said it was a favor. Jamie\'s favors are the kind you pay for twice.$B$BI\'ve had a look from the doorway. I\'ve seen worse. Mostly in the Plaguelands.$B$BCedric kept the roof on, I\'ll give him that, but the dead don\'t notice damp and they don\'t notice rot. Before I lift a hammer, I want you to see it with your own eyes: the broken furniture, the floorboards by the hearth, wherever the rain\'s getting in, and that hatch down to the cellar. A house is like a body, $n. You find out what\'s wrong with it before you start cutting.', '', 'Return to Oswin Thatcher outside your house in Brill.', 970206, 1, 'Broken furniture inspected', 970207, 1, 'Rotten floorboards inspected', 970208, 1, 'Leaking roof inspected', 970209, 1, 'Cellar hatch inspected', 0, 0, 0, 0, 0, 0, 0, 0),
(970201, 2, -1, 5, 159, 0, 4, 3500, 0, 'Timber for the Dead', 'Salvage 5 piles of usable lumber from abandoned farms around Tirisfal and a bucket of nails from Solliden Farmstead, then return to Oswin Thatcher.', 'I\'d buy new timber, but the nearest honest lumber is in Silverpine, and the worgen have opinions about who cuts it. Besides, Tirisfal is full of houses nobody needs anymore.$B$BThe farms out past Brill were built by people who knew their trade. Agamand Mills, the Solliden place, the old steadings east and west of town: there\'s oak in those walls older than either of us. Find the piles that haven\'t rotted through and bring back what you can carry. And nails. The Soliddens kept a bucket of them in the barn; nobody\'s had a use for them since.$B$BMind what still lives out there. Or doesn\'t live, but walks about anyway.', '', 'Return to Oswin Thatcher outside your house in Brill.', 970210, 5, 'Salvageable lumber', 970211, 1, 'Bucket of nails', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(970202, 2, -1, 5, 159, 0, 3, 2500, 0, 'Things Left Behind', 'Look through what Cedric Harrow left in the house: the bundle of letters, the portrait and the locked chest. Then speak with Oswin Thatcher.', 'Pulling up the floor turned up more than rot. Cedric left things behind: a bundle of letters under the loose board, a portrait over the mantel, and a chest with a lock rusted shut. I don\'t go through other people\'s things. It\'s bad luck, and I\'ve had enough of that.$B$BBut it\'s your house now. If there\'s anything in there worth keeping, or worth sending after him to Northrend, you\'re the one who ought to decide.', '', 'Return to Oswin Thatcher outside your house in Brill.', 970212, 1, 'Cedric\'s letters read', 970213, 1, 'The portrait found', 970214, 1, 'The chest opened', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(970203, 2, -1, 5, 159, 0, 4, 3000, 0, 'Beneath the Floorboards', 'Go down the hatch to your cellar, kill 6 Cellar Rats, then look at what\'s behind their nest.', 'Something\'s been chewing at the joists from below. I thought it was the house settling until it squeaked at me.$B$BRats. Big ones. Cellar rats in Tirisfal grow fat on whatever the plague left in the ground, and they\'ve been nesting under your floor since before Cedric came back. Down the hatch with you. Clear them out, and then have a proper look round the back of that cellar. I\'ve a feeling they came from somewhere further down than the cellar. Rats don\'t dig that deep without a reason.', '', 'Return to Oswin Thatcher outside your house in Brill.', 970201, 6, '', 970215, 1, 'The bricked-up wall examined', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(970204, 2, -1, 5, 159, 0, 4, 4000, 0, 'A Home Worth Keeping', 'Get candles and lamp oil from Abigail Shiel, linens from Mrs. Winters and clean straw from Morganus the stable master, then choose two furnishings with Oswin Thatcher.', 'Roof, door, floor, rats. That\'s the house done. A home is the rest of it.$B$BYou\'ll want light: Abigail Shiel sells candles and lamp oil by the market. Linens for the bed: Mrs. Winters, and don\'t let her talk you into the gray ones. And straw, clean straw, from Morganus at the stable, so that dog of yours has somewhere to sleep that isn\'t your bed.$B$BThen come and tell me how you want the place set out. I\'ll build you two pieces of whatever you like, on Jamie\'s account. She owes me more than she\'ll admit.', '', 'Return to Oswin Thatcher outside your house in Brill.', 970216, 1, 'Candles and lamp oil', 970217, 1, 'Linens', 970218, 1, 'Clean straw', 970219, 2, 'Furnishings chosen', 858, 3, 0, 0, 0, 0, 0, 0),
(970205, 2, -1, 5, 159, 0, 5, 5000, 0, 'A Housewarming for the Dead', 'Invite Innkeeper Renee, Apothecary Johaan, Hamlin Atkins and Deathguard Dillinger to your house, then speak with Oswin Thatcher there.', 'In Lordaeron, when a house was finished, you filled it with people the first night, so it would know what it was for. We did it in my town. We did it the night before the soldiers came to burn it.$B$BI\'d like to do it once more.$B$BInvite your neighbors. Renee at the inn, she\'ll bring something to drink whether anyone can taste it or not. Johaan, if he can be pried away from his vials. Hamlin, the mushroom farmer next door. And Dillinger, so the Deathguard know which house to watch.$B$BThey\'ll come. People in Brill don\'t get asked to things. It\'ll be the first invitation some of them have had since they died.', '', 'Speak with Oswin Thatcher outside your house in Brill.', 970220, 4, 'Neighbors invited', 0, 0, '', 0, 0, '', 0, 0, '', 929, 3, 0, 0, 0, 0, 0, 0),
(970206, 2, 1, 1, -1, 0, 0, 0, 0, '[invited_renee]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(970207, 2, 1, 1, -1, 0, 0, 0, 0, '[invited_johaan]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(970208, 2, 1, 1, -1, 0, 0, 0, 0, '[invited_hamlin]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(970209, 2, 1, 1, -1, 0, 0, 0, 0, '[invited_dillinger]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`, `SpecialFlags`) VALUES (970200, 970121, 0), (970201, 970200, 0), (970202, 970201, 0), (970203, 970202, 0), (970204, 970203, 0), (970205, 970204, 0);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`) VALUES
(970200, 1, 'So. A cellar that groans at night, a roof like a sieve, and furniture fit for kindling. I\'ve rebuilt houses for worse owners in worse towns.$B$BThe roof first, then the door, then the floor. Everything else can wait. Nothing in Tirisfal is in a hurry, least of all the people in it.'),
(970201, 1, 'Good oak. Dry, straight, and only a little bloodstained.$B$B(Over the next hours Oswin works without stopping. The broken furniture goes out the door as kindling, the rotten boards come up, the gap in the roof closes, and the door finally shuts the way a door should.)$B$BThere. It\'s a house again, $n. Not a home, not yet. But the rain stays outside, which is a start.'),
(970202, 1, 'Elinor, two boys, and a dog called Bramble. And the last letter dated the week the grain came in from Andorhal.$B$B(Oswin is quiet a while.)$B$BI\'ll send the ring to Vengeance Landing with the next ship. Cedric should have it. The toy soldiers... leave them on the shelf. Some things belong to a house more than to a person.'),
(970203, 1, 'A wall of brick at the back of the cellar, and a mark on it you don\'t like the look of. Show me.$B$B(Oswin studies your description for a long moment.)$B$BI\'ve seen that sign before. In Stratholme, on the doors of the houses the Cult of the Damned used. Somebody bricked that up before the plague came to Brill, or just after.$B$BI\'ll mortar over it again. Whatever\'s behind it has waited this long. If you want to know more, I\'d ask someone who keeps the dead\'s records. I\'d rather not know at all.'),
(970204, 1, '(Oswin hangs the last lantern and steps back to the doorway.)$B$BThere. Lamps that don\'t smoke, linen that doesn\'t smell of grave dirt, a bed of straw by the stove for the dog, and a chest for whatever you drag home from your travels.$B$BIt looks like somebody lives here, $n. That\'s all a house ever wants.'),
(970205, 1, '(The house is full: Renee pouring something brown into cups, Johaan explaining a recipe to Hamlin, who is explaining mushrooms back at him, Dillinger standing by the door out of habit.)$B$BListen to that. Six years I\'ve been building rooms for people to be lonely in.$B$BI\'ll stay on in Brill a while, I think. Jamie keeps finding me work. If you want anything else done to the place, you know where to find me. Right here, usually, admiring my own roof.');
INSERT INTO `quest_request_items` (`ID`, `EmoteOnComplete`, `EmoteOnIncomplete`, `CompletionText`) VALUES
(970200, 1, 1, 'Seen it all yet? Don\'t step on the boards by the hearth. Or do, and save me the trouble of pulling them up.'),
(970201, 1, 1, 'Timber? Nails? The roof isn\'t going to stop leaking because we\'ve been patient with it.'),
(970202, 1, 1, 'Found anything? You\'ve got the look of someone reading something they shouldn\'t.'),
(970203, 1, 1, 'Still squeaking. I can hear them from out here.'),
(970204, 1, 1, 'Light, linen, straw, and your say in the rest. I\'m not building it all on my own guesswork.'),
(970205, 1, 1, 'Have you asked them? Don\'t worry if they say no. They won\'t say no.');
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES (970200, 970200), (970200, 970201), (970200, 970202), (970200, 970203), (970200, 970204), (970200, 970205);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES (970200, 970200), (970200, 970201), (970200, 970202), (970200, 970203), (970200, 970204), (970200, 970205);

-- The Gravekeeper's Ledger
INSERT INTO `creature_template` (`entry`, `name`, `subname`, `gossip_menu_id`, `minlevel`, `maxlevel`, `faction`, `npcflag`, `speed_walk`, `speed_run`, `unit_class`, `unit_flags`, `type`, `rank`, `HealthModifier`, `DamageModifier`, `mingold`, `maxgold`, `flags_extra`, `AIName`, `ScriptName`) VALUES
(970300, 'Mortimer Weller', 'Gravekeeper', 0, 22, 22, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(970301, 'Mercy Hollin', NULL, 0, 12, 12, 68, 3, 1, 1.14286, 1, 512, 6, 0, 1, 1, 0, 0, 2, '', ''),
(970302, 'Gideon Hale', NULL, 0, 12, 12, 68, 1, 1, 1.14286, 1, 512, 6, 0, 1, 1, 0, 0, 2, '', ''),
(970303, 'Edith Fairweather', NULL, 0, 10, 10, 68, 1, 1, 1.14286, 1, 512, 6, 0, 1, 1, 0, 0, 2, '', ''),
(970304, 'Walter Shaw', NULL, 0, 13, 13, 68, 1, 1, 1.14286, 1, 512, 6, 0, 1, 1, 0, 0, 2, '', ''),
(970305, 'Mercy Hollin', NULL, 0, 12, 12, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(970306, 'Gideon Hale', 'Stonemason', 0, 12, 12, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(970307, 'Edith Fairweather', 'Weaver', 0, 10, 10, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(970308, 'Walter Shaw', NULL, 0, 13, 13, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(970309, 'Burial ledgers sorted', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970310, 'Neglected graves inspected', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970311, 'Disturbed graves searched', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970312, 'Trail of grave dirt followed', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970313, 'Whoever hides in the mausoleum spoken with', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970314, 'Belongings recovered', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970315, 'Brill\'s question settled', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970316, 'Names entered on Brill\'s rolls', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970317, 'The last bell rung', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', '');
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`) VALUES
(970300, 0, 2650, 1, 1),
(970301, 0, 2660, 1, 1),
(970302, 0, 2649, 1, 1),
(970303, 0, 2664, 1, 1),
(970304, 0, 2654, 1, 1),
(970305, 0, 2660, 1, 1),
(970306, 0, 2649, 1, 1),
(970307, 0, 2664, 1, 1),
(970308, 0, 2654, 1, 1),
(970309, 0, 11686, 1, 1),
(970310, 0, 11686, 1, 1),
(970311, 0, 11686, 1, 1),
(970312, 0, 11686, 1, 1),
(970313, 0, 11686, 1, 1),
(970314, 0, 11686, 1, 1),
(970315, 0, 11686, 1, 1),
(970316, 0, 11686, 1, 1),
(970317, 0, 11686, 1, 1);
INSERT INTO `creature` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(970300, 970300, 0, 85, 0, 1, 1, 2362.000, 342.000, 38.030, 3.0000, 60, 0, 0, 'mod-brill-home town'),
(970301, 970301, 0, 85, 0, 1, 1, 2486.000, 259.000, 47.280, 2.8000, 60, 0, 0, 'mod-brill-home town'),
(970302, 970302, 0, 85, 0, 1, 1, 2489.000, 265.000, 46.440, 3.4000, 60, 0, 0, 'mod-brill-home town'),
(970303, 970303, 0, 85, 0, 1, 1, 2484.000, 253.000, 45.920, 2.4000, 60, 0, 0, 'mod-brill-home town'),
(970304, 970304, 0, 85, 0, 1, 1, 2491.000, 251.000, 45.380, 2.2000, 60, 0, 0, 'mod-brill-home town'),
(970305, 970305, 0, 85, 0, 1, 4194304, 2352.000, 336.000, 38.080, 0.4000, 60, 0, 0, 'mod-brill-home town'),
(970306, 970306, 0, 85, 0, 1, 4194304, 2290.000, 318.000, 35.310, 1.6000, 60, 0, 0, 'mod-brill-home town'),
(970307, 970307, 0, 85, 0, 1, 4194304, 2262.000, 279.000, 34.790, 0.8000, 60, 0, 0, 'mod-brill-home town'),
(970308, 970308, 0, 85, 0, 1, 4194304, 2296.000, 393.000, 34.070, 0.2000, 60, 0, 0, 'mod-brill-home town');
INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `Data0`, `Data1`, `ScriptName`) VALUES
(970300, 10, 193, 'Neglected Grave', 1, 0, 970300, 'go_brill_town'),
(970301, 10, 499, 'Neglected Grave', 1, 0, 970300, 'go_brill_town'),
(970302, 10, 2452, 'Neglected Grave', 1, 0, 970300, 'go_brill_town'),
(970303, 10, 19, 'Neglected Grave', 1, 0, 970300, 'go_brill_town'),
(970304, 10, 399, 'Neglected Grave', 1, 0, 970300, 'go_brill_town'),
(970305, 10, 498, 'Disturbed Grave', 1, 0, 970301, 'go_brill_town'),
(970306, 10, 49, 'Disturbed Grave', 1, 0, 970301, 'go_brill_town'),
(970307, 10, 498, 'Disturbed Grave', 1, 0, 970301, 'go_brill_town'),
(970308, 10, 49, 'Trail of Grave Dirt', 0.5, 0, 970302, 'go_brill_town'),
(970309, 5, 1187, 'Lyle Family Mausoleum', 1, 0, 0, ''),
(970310, 10, 5511, 'Mason\'s Tool Roll', 0.6, 0, 970303, 'go_brill_town'),
(970311, 10, 7494, 'Sewing Basket', 1, 0, 970303, 'go_brill_town'),
(970312, 10, 1, 'Tin Letter Box', 0.5, 0, 970303, 'go_brill_town');
INSERT INTO `gameobject_template_addon` (`entry`, `faction`, `flags`) VALUES (970300, 0, 4), (970301, 0, 4), (970302, 0, 4), (970303, 0, 4), (970304, 0, 4), (970305, 0, 4), (970306, 0, 4), (970307, 0, 4), (970308, 0, 4), (970310, 0, 4), (970311, 0, 4), (970312, 0, 4);
INSERT INTO `gameobject` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`, `animprogress`, `state`, `Comment`) VALUES
(970300, 970300, 0, 85, 0, 1, 1, 2352.000, 322.000, 36.420, 1.2000, 0, 0, 0.564642, 0.825336, 0, 255, 1, 'mod-brill-home town'),
(970301, 970301, 0, 85, 0, 1, 1, 2348.000, 360.000, 36.720, 0.4000, 0, 0, 0.198669, 0.980067, 0, 255, 1, 'mod-brill-home town'),
(970302, 970302, 0, 85, 0, 1, 1, 2366.000, 368.000, 37.790, 4.9000, 0, 0, 0.637765, -0.770231, 0, 255, 1, 'mod-brill-home town'),
(970303, 970303, 0, 85, 0, 1, 1, 2396.000, 362.000, 37.010, 3.6000, 0, 0, 0.973848, -0.227202, 0, 255, 1, 'mod-brill-home town'),
(970304, 970304, 0, 85, 0, 1, 1, 2400.000, 325.000, 38.090, 3.1000, 0, 0, 0.999784, 0.020795, 0, 255, 1, 'mod-brill-home town'),
(970305, 970305, 0, 85, 0, 1, 1, 2372.000, 374.000, 37.340, 1.0000, 0, 0, 0.479426, 0.877583, 0, 255, 1, 'mod-brill-home town'),
(970306, 970306, 0, 85, 0, 1, 1, 2356.000, 376.000, 35.910, 2.2000, 0, 0, 0.891207, 0.453596, 0, 255, 1, 'mod-brill-home town'),
(970307, 970307, 0, 85, 0, 1, 1, 2340.000, 368.000, 34.650, 5.5000, 0, 0, 0.381661, -0.924302, 0, 255, 1, 'mod-brill-home town'),
(970308, 970308, 0, 85, 0, 1, 1, 2425.000, 300.000, 36.170, 5.8000, 0, 0, 0.239249, -0.970958, 0, 255, 1, 'mod-brill-home town'),
(970309, 970308, 0, 85, 0, 1, 1, 2458.000, 280.000, 31.440, 5.9000, 0, 0, 0.190423, -0.981702, 0, 255, 1, 'mod-brill-home town'),
(970310, 970308, 0, 85, 0, 1, 1, 2472.000, 268.000, 45.380, 5.9000, 0, 0, 0.190423, -0.981702, 0, 255, 1, 'mod-brill-home town'),
(970311, 970309, 0, 85, 0, 1, 1, 2497.000, 257.000, 46.090, 2.8000, 0, 0, 0.985450, 0.169967, 0, 255, 1, 'mod-brill-home town'),
(970312, 970310, 0, 85, 0, 1, 1, 2041.500, 153.000, 34.300, 1.4000, 0, 0, 0.644218, 0.764842, 0, 255, 1, 'mod-brill-home town'),
(970313, 970311, 0, 85, 0, 1, 1, 2483.500, 24.500, 26.900, 0.6000, 0, 0, 0.295520, 0.955336, 0, 255, 1, 'mod-brill-home town'),
(970314, 970312, 0, 85, 0, 1, 1, 2903.000, 387.000, 30.020, 4.0000, 0, 0, 0.909297, -0.416147, 0, 255, 1, 'mod-brill-home town');
INSERT INTO `brill_town_use` (`go`, `ord`, `cond`, `quest`, `credit`, `text_id`, `marker`, `tele_map`, `tele_x`, `tele_y`, `tele_z`, `tele_o`) VALUES
(970300, 0, 'I970300', 970300, 970310, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970301, 0, 'I970300', 970300, 970310, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970302, 0, 'I970300', 970300, 970310, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970303, 0, 'I970300', 970300, 970310, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970304, 0, 'I970300', 970300, 970310, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970305, 0, 'I970301', 970301, 970311, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970306, 0, 'I970301', 970301, 970311, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970307, 0, 'I970301', 970301, 970311, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970308, 0, 'I970302', 970302, 970312, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970310, 0, 'I970303', 970303, 970314, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970311, 0, 'I970303', 970303, 970314, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970312, 0, 'I970303', 970303, 970314, 970300, 0, -1, 0.000, 0.000, 0.000, 0.0000);
INSERT INTO `brill_town_gossip` (`npc`, `ord`, `kind`, `cond`, `icon`, `text`, `text_id`, `action`, `quest`, `credit`, `marker`, `emote`, `reply`, `arg`) VALUES
(970300, 1000, 'greet', 'R970904', 0, NULL, 970301, '', 0, 0, 0, 0, NULL, 0),
(970300, 1001, 'greet', 'C970904', 0, NULL, 970302, '', 0, 0, 0, 0, NULL, 0),
(970300, 1002, 'greet', 'T970900', 0, NULL, 970303, '', 0, 0, 0, 0, NULL, 0),
(970300, 1003, 'greet', 'R970304 R970305', 0, NULL, 970304, '', 0, 0, 0, 0, NULL, 0),
(970300, 1004, 'greet', 'R970304 R970306', 0, NULL, 970305, '', 0, 0, 0, 0, NULL, 0),
(970300, 1005, 'greet', 'R970203 !R970304', 0, NULL, 970306, '', 0, 0, 0, 0, NULL, 0),
(970300, 1006, 'greet', 'A970304', 0, NULL, 970307, '', 0, 0, 0, 0, NULL, 0),
(970300, 1007, 'greet', 'T970302 !R970304', 0, NULL, 970308, '', 0, 0, 0, 0, NULL, 0),
(970300, 1008, 'greet', 'A970301', 0, NULL, 970309, '', 0, 0, 0, 0, NULL, 0),
(970300, 1009, 'greet', 'A970300', 0, NULL, 970310, '', 0, 0, 0, 0, NULL, 0),
(970300, 1010, 'greet', '', 0, NULL, 970311, '', 0, 0, 0, 0, NULL, 0),
(970300, 1011, 'option', 'I970300', 0, '(Help Mortimer sort the burial ledgers.)', 0, 'credit', 970300, 970309, 0, 1, 'Plague year on the left, after on the right. Births in the green book, there were so few. Thank you, $n.$BHere\'s the odd thing: Hollin. Hale. Fairweather. Shaw. Written twice. Go and see their stones for me, along the wall, and the Lyle stone at the end.', 0),
(970300, 1012, 'option', 'I970304', 0, '(Ring the bell over the lychgate.)', 0, 'credit', 970304, 970317, 0, 2, '(The bell sounds once, flat and cracked, out over the town. On the cemetery wall, four figures stand very still until it fades.)', 0),
(970300, 1013, 'option', 'R970203', 0, 'Oswin Thatcher said to ask you about a mark in my cellar.', 0, 'say', 0, 0, 0, 0, 'A crowned eye, on brick? I know of it, though not from my books. Brill had a benefactor in the plague year, a Master Croft, who paid for many kindnesses and some walls. Ask the Deathstalker by the mausoleum. She\'s been waiting for someone to.', 0),
(970301, 1014, 'option', 'I970302', 0, 'I\'m not here to hurt you. Mortimer Weller sent me.', 0, 'credit', 970302, 970313, 0, 6, 'Weller. The clerk. ...Put your hands where I can see them, and come up slowly.', 0),
(970301, 1015, 'option', 'I970303', 0, 'Walk into Brill by daylight, under your own names. Let them see you.', 0, 'choice', 970303, 970315, 970305, 273, 'By daylight. Walter will hate it. ...Good. Let them look; we\'ll look back. I delivered half the Deathguard\'s grandmothers.', 0),
(970301, 1016, 'option', 'I970303', 0, 'Come in quietly, at night, with the gravekeeper\'s word ahead of you.', 0, 'choice', 970303, 970315, 970306, 273, 'Quietly, then. Edith will be glad. Not everyone wants to be a curiosity, $n. Some of us only want to be left to sew.', 0),
(1499, 1017, 'option', 'I970304', 0, 'Gravekeeper Weller asks that four names be entered on Brill\'s rolls.', 0, 'credit', 970304, 970316, 0, 1, 'Four more risen, and the Deathguard didn\'t find them first? Unusual. ...Hollin, Hale, Fairweather, Shaw. Entered, under the Dark Lady\'s protection. Tell them they owe tithe from the next harvest, the same as everyone. Freedom has its paperwork.', 0),
(970301, 1018, 'greet', 'R970304', 0, NULL, 970312, '', 0, 0, 0, 0, NULL, 0),
(970301, 1019, 'greet', 'T970302', 0, NULL, 970313, '', 0, 0, 0, 0, NULL, 0),
(970301, 1020, 'greet', '', 0, NULL, 970314, '', 0, 0, 0, 0, NULL, 0),
(970302, 1021, 'greet', 'R970304', 0, NULL, 970315, '', 0, 0, 0, 0, NULL, 0),
(970302, 1022, 'greet', '', 0, NULL, 970316, '', 0, 0, 0, 0, NULL, 0),
(970303, 1023, 'greet', 'R970304', 0, NULL, 970317, '', 0, 0, 0, 0, NULL, 0),
(970303, 1024, 'greet', '', 0, NULL, 970318, '', 0, 0, 0, 0, NULL, 0),
(970304, 1025, 'greet', 'R970304', 0, NULL, 970319, '', 0, 0, 0, 0, NULL, 0),
(970304, 1026, 'greet', '', 0, NULL, 970320, '', 0, 0, 0, 0, NULL, 0),
(970305, 1027, 'greet', 'R970305 D3', 0, NULL, 970321, '', 0, 0, 0, 0, NULL, 0),
(970305, 1028, 'greet', 'R970305', 0, NULL, 970322, '', 0, 0, 0, 0, NULL, 0),
(970305, 1029, 'greet', '', 0, NULL, 970323, '', 0, 0, 0, 0, NULL, 0),
(970306, 1030, 'greet', 'R970904', 0, NULL, 970324, '', 0, 0, 0, 0, NULL, 0),
(970306, 1031, 'greet', 'R970305', 0, NULL, 970325, '', 0, 0, 0, 0, NULL, 0),
(970306, 1032, 'greet', '', 0, NULL, 970326, '', 0, 0, 0, 0, NULL, 0),
(970307, 1033, 'greet', 'R970306', 0, NULL, 970327, '', 0, 0, 0, 0, NULL, 0),
(970307, 1034, 'greet', '', 0, NULL, 970328, '', 0, 0, 0, 0, NULL, 0),
(970308, 1035, 'greet', 'R970305', 0, NULL, 970329, '', 0, 0, 0, 0, NULL, 0),
(970308, 1036, 'greet', '', 0, NULL, 970330, '', 0, 0, 0, 0, NULL, 0);
UPDATE `creature_template` SET `npcflag` = `npcflag` | 1 WHERE `entry` IN (1499);
INSERT INTO `brill_town_phase` (`bit`, `ord`, `cond`) VALUES
(4194304, 0, 'R970304');
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `Flags`, `RewardXPDifficulty`, `RewardMoney`, `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `AreaDescription`, `QuestCompletionLog`, `RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `ObjectiveText1`, `RequiredNpcOrGo2`, `RequiredNpcOrGoCount2`, `ObjectiveText2`, `RequiredNpcOrGo3`, `RequiredNpcOrGoCount3`, `ObjectiveText3`, `RequiredNpcOrGo4`, `RequiredNpcOrGoCount4`, `ObjectiveText4`, `RewardItem1`, `RewardAmount1`, `RewardItem2`, `RewardAmount2`, `RewardItem3`, `RewardAmount3`, `RewardItem4`, `RewardAmount4`) VALUES
(970300, 2, -1, 5, 159, 0, 3, 2000, 0, 'Names Among the Stones', 'Help Mortimer Weller sort Brill\'s burial ledgers, then inspect five neglected graves in the cemetery.', 'You there. You\'ve the look of someone who reads. Forgive me: I don\'t get many visitors who still do.$B$BI was the parish clerk here, before. I wrote every burial of the plague year in this ledger, until my hand shook too hard to hold the pen, and then somebody wrote mine. The Dark Lady\'s people gave me the cemetery back when I rose. A clerk to the last, it seems.$B$BGraves are coming up empty, $n. Not torn open, the way the Scourge leave them. Just... empty. And when I went to the ledgers to see whose, I found names written twice. My own hand, and then another\'s.$B$BHelp me put the books in order, and then look at five of the oldest graves along the wall. Tell me what the stones say. I\'d go myself, but I\'d rather not be alone with this until I know what it is.', '', 'Return to Gravekeeper Mortimer Weller in Brill\'s cemetery.', 970309, 1, 'Burial ledgers sorted', 970310, 5, 'Neglected graves inspected', 0, 0, '', 0, 0, '', 118, 2, 0, 0, 0, 0, 0, 0),
(970301, 2, -1, 5, 159, 0, 3, 2500, 0, 'Fresh Earth', 'Search three recently disturbed graves in Brill\'s cemetery for evidence of who has been taking the dead.', 'The Deathguard tell me it\'s the Rot Hide gnolls. They dig for bones the way dogs do, and they\'ve done it before. Executor Zygand says to put a guard on the gate and stop fretting.$B$BBut I\'ve seen what gnolls leave behind, $n: half the coffin in splinters and the other half chewed. These graves were opened neatly. Somebody filled the holes back in after. Gnolls don\'t tidy.$B$BThree of the double-named graves were disturbed within the week, along the north side, by the old yew. Look them over properly. Whatever was left behind, I want to know about it before the Deathguard decide what it means for us.', '', 'Return to Gravekeeper Mortimer Weller in Brill\'s cemetery.', 970311, 3, 'Disturbed graves searched', 0, 0, '', 0, 0, '', 0, 0, '', 858, 2, 0, 0, 0, 0, 0, 0),
(970302, 2, -1, 5, 159, 0, 4, 2500, 0, 'Those Who Were Forgotten', 'Follow the trail of grave dirt east of Brill\'s cemetery to wherever it leads, and speak with whoever you find.', 'There\'s a furrow in the grass past the east wall, where something heavy was dragged, or someone who couldn\'t yet walk was helped along. It goes up toward the wooded hill, where the old Lyle family mausoleum stands. The Lyles all died in the first month of the plague. No one has opened that door since.$B$BI could tell the Deathguard. They\'d go up there with torches, and whoever is inside would be put down a second time, or a third.$B$BI\'d rather you went. You don\'t wear a tabard, and you\'ve the patience to talk before you swing. If they are what I think they are, they\'ll be more afraid of you than you need be of them. Mostly.', '', 'Speak with Mercy Hollin at the Lyle mausoleum east of Brill.', 970312, 3, 'Trail of grave dirt followed', 970313, 1, 'Whoever hides in the mausoleum spoken with', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(970303, 2, -1, 5, 159, 0, 4, 3000, 0, 'A Name of One\'s Own', 'Recover Gideon\'s tools from the old smithy west of Brill, Edith\'s basket from her cottage south of town and Walter\'s letters from the gnolls\' farmstead north-east of it, and help Mercy decide how they\'ll face Brill.', 'I woke in the dark with earth in my mouth, and I knew my own name. That was the strange part. For years I\'d only known his voice in my head, and then it was gone, and there I was. Mercy. Just Mercy.$B$BI dug myself out. Then I heard knocking from the next grave, so I took Mortimer\'s spade from his shed and dug again. Four times, so far. I\'ll keep listening.$B$BThe others want things back, before they\'ll believe they\'re people. Gideon wants his tools from the old smithy by the west road. Edith wants her sewing basket from her cottage south of town, the one by the duskbat woods. Walter\'s letters are at his farmstead north-east of here, where the Rot Hide gnolls have their camp now.$B$BAnd when you come back, help me talk sense into them about Brill. We can\'t live in a tomb forever. Though Walter would try.', '', 'Return to Mercy Hollin at the Lyle mausoleum east of Brill.', 970314, 3, 'Belongings recovered', 970315, 1, 'Brill\'s question settled', 0, 0, '', 0, 0, '', 858, 2, 0, 0, 0, 0, 0, 0),
(970304, 2, -1, 5, 159, 0, 5, 4000, 0, 'The Last Bell', 'Ask Magistrate Sevren in Brill\'s town hall to enter the four names on Brill\'s rolls, then ring the cemetery bell with Gravekeeper Mortimer Weller.', 'There\'s a custom in Brill. There was, anyway. When someone was laid in the ground, the clerk rang the bell over the lychgate, once, so the whole parish knew a life was finished. In the plague year it rang so often they stopped ringing it at all.$B$BMortimer told me, through you, that he\'d like to ring it once more for the four of us. The other way round. Not a life finished; a death.$B$BBut a bell\'s only a bell. The Magistrate keeps the rolls of who lives in Brill, and who the Deathguard are to leave alone. Our names need to be on them, $n, or we\'re only corpses with opinions. Go to Sevren in the town hall, and then to Mortimer. We\'ll be watching from the wall.', '', 'Return to Gravekeeper Mortimer Weller in Brill\'s cemetery.', 970316, 1, 'Names entered on Brill\'s rolls', 970317, 1, 'The last bell rung', 0, 0, '', 0, 0, '', 1930, 1, 0, 0, 0, 0, 0, 0),
(970305, 2, 1, 1, -1, 0, 0, 0, 0, '[openly]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(970306, 2, 1, 1, -1, 0, 0, 0, 0, '[quietly]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`, `SpecialFlags`) VALUES (970300, 0, 0), (970301, 970300, 0), (970302, 970301, 0), (970303, 970302, 0), (970304, 970303, 0);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`) VALUES
(970300, 1, 'Hollin, Hale, Fairweather, Shaw. Every one of them twice.$B$BThe first entry\'s mine: buried in the plague year. The second is in a Deathguard\'s square hand, two years on. \'Remains found walking. Put down. Returned to plot.\'$B$BSo they were Scourge, once, after they died. The Deathguard cut them down and gave them back to the earth. I\'d have called that the end of the matter. It seems the earth didn\'t agree.'),
(970301, 1, 'My own spade. I wondered where that went.$B$BAnd this lid: scored on the inside, as if someone woke and clawed at it. But the nails were drawn from the outside, one by one, by somebody who knew what they were doing.$B$BNo one is stealing the dead, $n. Someone is letting them out.'),
(970302, 1, '(The woman lowers the spade, but doesn\'t let go of it.)$B$BMortimer sent you? Mortimer Weller, the clerk? He wrote my name in that book of his. Twice, I expect.$B$BI\'m Mercy Hollin. I was the midwife here, when Brill had children. Behind me are Gideon, Edith and Walter. We\'re not Scourge, whatever you\'ve been told. We were, once. We remember it. That\'s why we\'re hiding.'),
(970303, 1, 'Look at Gideon, turning that chisel over like he\'d never seen one. And Edith hasn\'t let go of her basket since you put it in her hands.$B$BWalter read his letters twice and then went outside to stand in the rain. Leave him be. He\'ll come back.$B$BYou\'ve given them something I couldn\'t, $n: proof they were somebody before, and not only something.'),
(970304, 1, 'Hollin. Hale. Fairweather. Shaw. Written a third time, and in the right column at last.$B$B(Gideon Hale clears his throat behind you.)$B$B"Gravekeeper. There\'s something you should know, since we\'re being honest. In the plague year a gentleman named Croft paid me to brick up the old way down beneath this cemetery, and two others like it about the town. To keep the sickness out of the refuge, he said. The people sheltering below went quiet soon after. I\'ve wondered what I sealed in, ever since I could wonder again."$B$B(Mortimer looks at you for a long moment.)$B$BWrite that down somewhere, $n. Not in my ledger. I\'ve enough to keep in it.');
INSERT INTO `quest_request_items` (`ID`, `EmoteOnComplete`, `EmoteOnIncomplete`, `CompletionText`) VALUES
(970300, 1, 1, 'Have you seen to the ledgers? And the stones along the wall?'),
(970301, 1, 1, 'Anything? Even a footprint would be more than the Deathguard have found.'),
(970303, 1, 1, 'Walter keeps asking if you\'ve found his letters. He pretends he isn\'t asking.'),
(970304, 1, 1, 'Have the names been entered? Has it rung?');
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES (970300, 970300), (970300, 970301), (970300, 970302), (970301, 970303), (970301, 970304);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES (970300, 970300), (970300, 970301), (970301, 970302), (970301, 970303), (970300, 970304);

-- The Apothecary's Apprentice
INSERT INTO `creature_template` (`entry`, `name`, `subname`, `gossip_menu_id`, `minlevel`, `maxlevel`, `faction`, `npcflag`, `speed_walk`, `speed_run`, `unit_class`, `unit_flags`, `type`, `rank`, `HealthModifier`, `DamageModifier`, `mingold`, `maxgold`, `flags_extra`, `AIName`, `ScriptName`) VALUES
(970400, 'Wendell Crane', 'Apprentice Apothecary', 0, 15, 15, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(970401, 'Frenzied Specimen', NULL, 0, 10, 10, 14, 0, 1, 1.14286, 1, 0, 1, 0, 2.2, 1.3, 40, 40, 0, 'SmartAI', ''),
(970402, 'Storage shed investigated', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970403, 'Stolen reagents recovered', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970404, 'Suspicious delivery examined', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970405, 'Caged darkhounds examined', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970406, 'Judgment given', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', '');
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`) VALUES
(970400, 0, 4111, 1, 1),
(970401, 0, 9020, 1.25, 1),
(970402, 0, 11686, 1, 1),
(970403, 0, 11686, 1, 1),
(970404, 0, 11686, 1, 1),
(970405, 0, 11686, 1, 1),
(970406, 0, 11686, 1, 1);
INSERT INTO `creature` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(970400, 970400, 0, 85, 0, 1, 1, 2249.500, 343.500, 35.200, 3.1400, 60, 0, 0, 'mod-brill-home town'),
(970401, 970401, 0, 85, 0, 1, 1, 2606.000, 186.000, 33.300, 2.5000, 60, 4, 1, 'mod-brill-home town');
UPDATE `creature_template` SET `AIName` = 'SmartAI' WHERE `entry` IN (970401);
INSERT INTO `smart_scripts` (`entryorguid`, `source_type`, `id`, `link`, `event_type`, `event_phase_mask`, `event_chance`, `event_flags`, `event_param1`, `event_param2`, `event_param3`, `event_param4`, `event_param5`, `event_param6`, `action_type`, `action_param1`, `action_param2`, `action_param3`, `action_param4`, `action_param5`, `action_param6`, `target_type`, `target_param1`, `target_param2`, `target_param3`, `target_param4`, `target_x`, `target_y`, `target_z`, `target_o`, `comment`) VALUES
(970401, 0, 0, 0, 0, 0, 100, 0, 3000, 5000, 12000, 16000, 0, 0, 11, 3427, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 'Frenzied Specimen casts 3427');
INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `Data0`, `Data1`, `ScriptName`) VALUES
(970400, 10, 662, 'Locked Storage Shed', 1, 0, 970400, 'go_brill_town'),
(970401, 5, 7485, 'Washbasin', 1, 0, 0, ''),
(970402, 5, 4073, 'Dirty Glassware', 1, 0, 0, ''),
(970403, 10, 335, 'Pilfered Reagent Crate', 1, 0, 970401, 'go_brill_town'),
(970404, 10, 7524, 'Abandoned Handcart', 1, 0, 970401, 'go_brill_town'),
(970405, 10, 4151, 'Wendell\'s Cage', 0.7, 0, 970403, 'go_brill_town'),
(970406, 10, 4151, 'Wendell\'s Cage', 0.7, 0, 970403, 'go_brill_town'),
(970407, 10, 4151, 'Wendell\'s Cage', 0.7, 0, 970403, 'go_brill_town'),
(970408, 5, 4391, 'Crane\'s Apparatus', 1, 0, 0, ''),
(970409, 5, 7448, 'Bubbling Retort', 0.45, 0, 0, ''),
(970410, 5, 254, 'Johaan\'s Ledger', 1, 0, 0, ''),
(970411, 5, 4251, 'Charred Remains', 1, 0, 0, ''),
(970412, 5, 239, 'Scrubbing Bucket', 1, 0, 0, '');
INSERT INTO `gameobject_template_addon` (`entry`, `faction`, `flags`) VALUES (970400, 0, 4), (970403, 0, 4), (970404, 0, 4), (970405, 0, 4), (970406, 0, 4), (970407, 0, 4);
INSERT INTO `gameobject` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`, `animprogress`, `state`, `Comment`) VALUES
(970400, 970400, 0, 85, 0, 1, 1, 2250.500, 355.000, 35.200, 5.6200, 0, 0, 0.325549, -0.945525, 0, 255, 1, 'mod-brill-home town'),
(970401, 970401, 0, 85, 0, 1, 1, 2247.600, 344.600, 35.200, 1.6000, 0, 0, 0.717356, 0.696707, 0, 255, 1, 'mod-brill-home town'),
(970402, 970402, 0, 85, 0, 1, 1, 2247.400, 342.400, 35.200, 4.0000, 0, 0, 0.909297, -0.416147, 0, 255, 1, 'mod-brill-home town'),
(970403, 970403, 0, 85, 0, 1, 1, 2286.000, 1298.000, 32.200, 1.0000, 0, 0, 0.479426, 0.877583, 0, 255, 1, 'mod-brill-home town'),
(970404, 970403, 0, 85, 0, 1, 1, 2294.000, 1322.000, 31.500, 2.2000, 0, 0, 0.891207, 0.453596, 0, 255, 1, 'mod-brill-home town'),
(970405, 970403, 0, 85, 0, 1, 1, 2276.000, 1334.000, 33.500, 4.1000, 0, 0, 0.887362, -0.461073, 0, 255, 1, 'mod-brill-home town'),
(970406, 970403, 0, 85, 0, 1, 1, 2300.000, 1305.000, 31.400, 0.4000, 0, 0, 0.198669, 0.980067, 0, 255, 1, 'mod-brill-home town'),
(970407, 970404, 0, 85, 0, 1, 1, 2280.000, 1288.000, 31.500, 0.8000, 0, 0, 0.389418, 0.921061, 0, 255, 1, 'mod-brill-home town'),
(970408, 970405, 0, 85, 0, 1, 1, 2450.000, 200.000, 37.500, 1.0000, 0, 0, 0.479426, 0.877583, 0, 255, 1, 'mod-brill-home town'),
(970409, 970406, 0, 85, 0, 1, 1, 2522.000, 252.000, 47.000, 3.0000, 0, 0, 0.997495, 0.070737, 0, 255, 1, 'mod-brill-home town'),
(970410, 970407, 0, 85, 0, 1, 1, 2602.000, 182.000, 34.000, 5.0000, 0, 0, 0.598472, -0.801144, 0, 255, 1, 'mod-brill-home town'),
(970411, 970408, 0, 85, 0, 1, 8388608, 2246.600, 340.400, 35.200, 3.3000, 0, 0, 0.996865, -0.079121, 0, 255, 1, 'mod-brill-home town'),
(970412, 970409, 0, 85, 0, 1, 8388608, 2245.800, 346.000, 35.200, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(970413, 970410, 0, 85, 0, 1, 8388608, 2251.200, 341.000, 35.200, 2.0000, 0, 0, 0.841471, 0.540302, 0, 255, 1, 'mod-brill-home town'),
(970414, 970411, 0, 85, 0, 1, 16777216, 2252.600, 352.000, 35.200, 0.6000, 0, 0, 0.295520, 0.955336, 0, 255, 1, 'mod-brill-home town'),
(970415, 970412, 0, 85, 0, 1, 16777216, 2248.700, 345.000, 35.200, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town');
INSERT INTO `brill_town_use` (`go`, `ord`, `cond`, `quest`, `credit`, `text_id`, `marker`, `tele_map`, `tele_x`, `tele_y`, `tele_z`, `tele_o`) VALUES
(970400, 0, 'I970400', 970400, 970402, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970403, 0, 'I970401', 970401, 970403, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970404, 0, 'I970401', 970401, 970404, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970405, 0, 'I970403', 970403, 970405, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970406, 0, 'I970403', 970403, 970405, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970407, 0, 'I970403', 970403, 970405, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000);
INSERT INTO `brill_town_gossip` (`npc`, `ord`, `kind`, `cond`, `icon`, `text`, `text_id`, `action`, `quest`, `credit`, `marker`, `emote`, `reply`, `arg`) VALUES
(1518, 2000, 'option', 'I970404', 0, '(Hand him the notes.) It belongs to the Society. Take it.', 0, 'choice', 970404, 970406, 970405, 0, 'Sensible. Faranell will be delighted; he so rarely is. Crane will be credited, in a footnote, in a file no one reads. That is more than most of us are given.', 0),
(1518, 2001, 'option', 'I970404', 0, 'Let him go on with it, Apothecary. Under your eye.', 0, 'choice', 970404, 970406, 970406, 0, 'Under my eye. You do realize it is the only one I have left that still sits properly in its socket? ...Very well. A bench in the yard, my reagents, my ledger, my rules. If a single hound bites anyone, it is both of you I report.', 0),
(1518, 2002, 'option', 'I970404', 0, '(Burn the notes in the still behind the shed.) No one should have this.', 0, 'choice', 970404, 970406, 970407, 0, '(Johaan watches the smoke rise from behind the laboratory and says nothing for a long while.)$B$BPerhaps. I would have liked to read it first. That is the trouble with alchemists, $n. We always want to read everything first.', 0),
(1518, 2003, 'greet', 'R970405', 0, NULL, 970400, '', 0, 0, 0, 0, NULL, 0),
(1518, 2004, 'greet', 'R970406', 0, NULL, 970401, '', 0, 0, 0, 0, NULL, 0),
(1518, 2005, 'greet', 'R970407', 0, NULL, 970402, '', 0, 0, 0, 0, NULL, 0),
(1518, 2006, 'greet', 'I970401', 0, NULL, 970403, '', 0, 0, 0, 0, NULL, 0),
(970400, 2007, 'greet', 'R970405 R970804', 0, NULL, 970404, '', 0, 0, 0, 0, NULL, 0),
(970400, 2008, 'greet', 'R970406 R970804', 0, NULL, 970405, '', 0, 0, 0, 0, NULL, 0),
(970400, 2009, 'greet', 'R970405', 0, NULL, 970406, '', 0, 0, 0, 0, NULL, 0),
(970400, 2010, 'greet', 'R970406', 0, NULL, 970407, '', 0, 0, 0, 0, NULL, 0),
(970400, 2011, 'greet', 'R970407', 0, NULL, 970408, '', 0, 0, 0, 0, NULL, 0),
(970400, 2012, 'greet', 'A970404', 0, NULL, 970409, '', 0, 0, 0, 0, NULL, 0),
(970400, 2013, 'greet', 'R970402', 0, NULL, 970410, '', 0, 0, 0, 0, NULL, 0),
(970400, 2014, 'greet', 'A970400', 0, NULL, 970411, '', 0, 0, 0, 0, NULL, 0),
(970400, 2015, 'greet', '', 0, NULL, 970412, '', 0, 0, 0, 0, NULL, 0),
(2132, 2016, 'option', 'R970407', 0, '(Ask her about Wendell Crane.)', 0, 'say', 0, 0, 0, 0, 'You burned it. Good. Some things shouldn\'t be kept, $n. Only the things that matter. Only the things that are yours.', 0),
(2132, 2017, 'option', 'R970406', 0, '(Ask her about Wendell Crane.)', 0, 'say', 0, 0, 0, 0, 'Wendell brought me a jar of the Stay to look at. Fine work. Careful. I\'d never let anyone put it in me, of course. I\'d rather keep my rot. It\'s mine.', 0),
(2132, 2018, 'option', 'R970405', 0, '(Ask her about Wendell Crane.)', 0, 'say', 0, 0, 0, 0, 'The Society has his notes now. They\'ll make something of it, and none of us will be allowed to have it. That\'s what the Society is for.', 0),
(2132, 2019, 'option', 'R970402 !R970404', 0, '(Ask her about Wendell Crane.)', 0, 'say', 0, 0, 0, 0, 'So it\'s Wendell. Poor thing. He asked me once whether lavender oil could cover the smell of a bad hand. I told him nothing covers it. You just stop letting people close enough to notice.', 0),
(2132, 2020, 'option', 'A970400', 0, '(Ask her about Johaan\'s missing ingredients.)', 0, 'say', 0, 0, 0, 0, 'Johaan\'s been counting his jars twice a day. He thinks I don\'t notice him counting mine as well. I don\'t steal, $n. I\'ve never needed to.', 0),
(2132, 2021, 'option', 'A970401', 0, '(Ask her about Johaan\'s missing ingredients.)', 0, 'say', 0, 0, 0, 0, 'Johaan\'s been counting his jars twice a day. He thinks I don\'t notice him counting mine as well. I don\'t steal, $n. I\'ve never needed to.', 0);
UPDATE `creature_template` SET `npcflag` = `npcflag` | 1 WHERE `entry` IN (1518, 2132);
INSERT INTO `brill_town_phase` (`bit`, `ord`, `cond`) VALUES
(8388608, 0, 'R970406'),
(16777216, 0, 'R970407');
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `Flags`, `RewardXPDifficulty`, `RewardMoney`, `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `AreaDescription`, `QuestCompletionLog`, `RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `ObjectiveText1`, `RequiredNpcOrGo2`, `RequiredNpcOrGoCount2`, `ObjectiveText2`, `RequiredNpcOrGo3`, `RequiredNpcOrGoCount3`, `ObjectiveText3`, `RequiredNpcOrGo4`, `RequiredNpcOrGoCount4`, `ObjectiveText4`, `RewardItem1`, `RewardAmount1`, `RewardItem2`, `RewardAmount2`, `RewardItem3`, `RewardAmount3`, `RewardItem4`, `RewardAmount4`) VALUES
(970400, 2, -1, 5, 159, 0, 3, 1500, 0, 'An Unpleasant Odor', 'Investigate the locked storage shed behind Apothecary Johaan\'s laboratory in Brill, then return to Johaan.', 'You there. You have a nose, I trust? Most of Brill has stopped using theirs, which is a mercy, given the town\'s chief exports.$B$BThings have been going missing from my stores. Embalming salts. Grave moss. Three flasks of distilled bile I was saving for a particularly ungrateful Scarlet. I keep inventories, $n. I may be the only person left in Tirisfal who keeps inventories.$B$BAnd for a week now there has been a smell from the storage shed behind the laboratory. Not our usual smell. Something sweet beneath it, like lilies left too long on a coffin. I do not keep lilies.$B$BThe shed is locked, and I did not lock it. Go and look. Through the boards, if you must. Tell me what is in there before I am obliged to go and see for myself.', '', 'Return to Apothecary Johaan in Brill.', 970402, 1, 'Storage shed investigated', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(970401, 2, -1, 5, 159, 0, 4, 3000, 0, 'Missing Reagents', 'Recover 4 crates of stolen reagents and examine the suspicious delivery at Solliden Farmstead, north of Brill, then return to Apothecary Johaan.', 'Solliden Farmstead lies north of here, past the mills. Old Solliden still walks his fields, though he no longer remembers what they are for, and the hands who work them are less pleasant company than he is. A quiet place to leave a crate, if one did not wish to be asked about it.$B$BWhatever was carted out there is mine, and the Society\'s, which is to say the Dark Lady\'s. Bring it back. Every crate you can find.$B$BAnd look for the delivery itself: a cart, a sack, a bill of lading, anything with a hand on it. Thieves are seldom clever, $n, but they are always careless about paper. I want to know who has been signing for my salts.', '', 'Return to Apothecary Johaan in Brill.', 970403, 4, 'Stolen reagents recovered', 970404, 1, 'Suspicious delivery examined', 0, 0, '', 0, 0, '', 858, 2, 0, 0, 0, 0, 0, 0),
(970402, 2, -1, 5, 159, 0, 2, 1500, 0, 'The Apprentice\'s Secret', 'Speak with Wendell Crane in the yard behind Apothecary Johaan\'s laboratory in Brill.', 'You have returned my salts, and I am grateful, in my fashion. Now I need one thing more, and I need it from someone who is not me.$B$BWendell works in the yard behind the laboratory, washing whatever I dirty. Go and speak with him. Show him those slips. I want to know what he has been brewing in my shed, and for whom. If he is selling to the Scarlets, or the Cult, or, the Dark Lady forbid, to the trolls, I will deal with it myself.$B$BIf it is something else... then I want to know what it is before I decide what it is worth.$B$BHe will talk to you. He has not talked to me in three years, except to say \'yes, Apothecary.\'', '', 'Speak with Wendell Crane behind the laboratory in Brill.', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(970403, 2, -1, 5, 159, 0, 4, 3500, 0, 'A Question of Progress', 'Examine Wendell Crane\'s three caged darkhounds in the hills north-east of Brill and deal with whatever has become of the third, then return to Wendell.', 'Mostly. That\'s the word that keeps me up, and I don\'t even sleep.$B$BIn a jar the Stay is perfect: no rot, no softening, not in six weeks. But a jar isn\'t a body. I needed something living and rotting at once, and Tirisfal has no shortage of those.$B$BThe darkhounds north-east of town have the wasting sickness: fur coming out in handfuls, sores that never close. I baited three of them with dosed meat and caged them in the hills on the way to the lake. I haven\'t dared go back. Johaan watches the road, and I\'m a coward besides.$B$BLook at them for me. All three. Tell me what the Stay has done to them. Whatever it is.', '', 'Return to Wendell Crane behind the laboratory in Brill.', 970405, 3, 'Caged darkhounds examined', 970401, 1, '', 0, 0, '', 0, 0, '', 2455, 2, 858, 2, 0, 0, 0, 0),
(970404, 2, -1, 5, 159, 0, 5, 4500, 0, 'The Apothecary\'s Judgment', 'Take Wendell Crane\'s notes on the Stay to Apothecary Johaan and decide what becomes of them.', 'I\'ve written it all out. The recipe, the doses, the hounds. Every mistake.$B$B(He presses a bound sheaf of notes into your hands. The ink on the last page is still wet.)$B$BTake it to Johaan. I can\'t. If I stand in front of him I\'ll only say \'yes, Apothecary\' and let him decide, the way I always have.$B$BYou\'ve seen what it does, the good and the bad. You decide what he hears. Give it to him, and the Society will have it, and Faranell\'s people in the Undercity will do with it whatever they do. Ask him to let me go on, under his eye, slowly, properly. Or burn it, and I\'ll go back to washing glass, and we\'ll all rot at the usual rate.$B$BWhatever you choose, I\'ll abide by it. I\'m tired of being the only one who knows.', '', 'Return to Apothecary Johaan in Brill.', 970406, 1, 'Judgment given', 0, 0, '', 0, 0, '', 0, 0, '', 2458, 2, 2459, 1, 0, 0, 0, 0),
(970405, 2, 1, 1, -1, 0, 0, 0, 0, '[surrendered]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(970406, 2, 1, 1, -1, 0, 0, 0, 0, '[supervised]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(970407, 2, 1, 1, -1, 0, 0, 0, 0, '[destroyed]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`, `SpecialFlags`) VALUES (970400, 0, 0), (970401, 970400, 0), (970402, 970401, 0), (970403, 970402, 0), (970404, 970403, 0);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`) VALUES
(970400, 1, 'A still. In my shed. With my salts in it.$B$B(Johaan pinches the bridge of his nose. A flake of skin comes away; he flicks it aside.)$B$BAnd crates bound for Solliden Farmstead. Someone is carting my reagents out of Brill and brewing with whatever is left behind my back. One of my apprentices, then. I have two, and I trust neither of them, which is the proper relationship.$B$BWell. At least they label their crates.'),
(970401, 1, 'Crane.$B$B(Johaan is silent for a long moment.)$B$BWendell Crane has been my apprentice for three years. He scrubs my glassware. He sweeps my floor. He has never once spoken out of turn, which I took for respect and ought to have taken for concealment.$B$BI won\'t question him. If I question him, I shall have to report whatever he says to the Society, and the Society does not believe in second chances. Or, in my experience, in first ones.'),
(970402, 1, '(Wendell looks at the slips, then at his hands. Two fingers of the left are gone at the knuckle; the rest are bound in gauze.)$B$BSo he knows. Of course he knows. He counts everything.$B$BI\'m not selling it. I\'m not selling anything. I\'m trying to stop this.$B$B(He holds up the hand.)$B$BI washed the dead for burial in Andorhal, before the grain came. I know what happens to a body, $n. I know it to the day. We\'re no different; we\'re only slower. A finger a year. An ear. One morning you wake and your jaw won\'t close. The Society\'s salts keep the worst of it off. I\'m making something that keeps us whole.$B$BI call it the Stay. And it works. Mostly.'),
(970403, 1, 'One healed. One set like a tanned hide. And one... I heard it, you know. Last night, from the yard. I told myself it was the wind.$B$B(Wendell writes it all down, carefully, with his three good fingers.)$B$BThe flesh holds. That much is true. But the stiffening, the madness... If the Stay does that to a hound\'s mind, what would it do to ours? Our minds are all that keep us from being the Scourge, $n. Will, and nothing else.$B$BI don\'t know whether I\'ve made a cure or a cage.'),
(970404, 1, 'It is settled, then. Whatever we have done, we have done it with our eyes open, which is more than the Lich King ever allowed any of us.$B$B(Johaan opens his ledger and writes a single line. He blots it with great care.)$B$BCrane will hear it from me. You have earned a rest from my apprentices\' troubles, and I have earned a rest from my own. Take these. They were brewed properly, by someone who keeps inventories.');
INSERT INTO `quest_request_items` (`ID`, `EmoteOnComplete`, `EmoteOnIncomplete`, `CompletionText`) VALUES
(970400, 1, 1, 'Well? I can smell it from here. Which, I assure you, is saying something.'),
(970401, 1, 1, 'My salts, $n. And the name. I will settle for the salts if I must.'),
(970403, 1, 1, 'Did it work? Don\'t tell me it didn\'t work. Tell me, but gently.'),
(970404, 1, 1, 'You have something of Crane\'s. I can tell by the way you hold it. Like a dead bird.');
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES (1518, 970400), (1518, 970401), (1518, 970402), (970400, 970403), (970400, 970404);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES (1518, 970400), (1518, 970401), (970400, 970402), (970400, 970403), (1518, 970404);
UPDATE `creature_template` SET `npcflag` = `npcflag` | 3 WHERE `entry` IN (1518);

-- Whispers of the Scarlet
INSERT INTO `creature_template` (`entry`, `name`, `subname`, `gossip_menu_id`, `minlevel`, `maxlevel`, `faction`, `npcflag`, `speed_walk`, `speed_run`, `unit_class`, `unit_flags`, `type`, `rank`, `HealthModifier`, `DamageModifier`, `mingold`, `maxgold`, `flags_extra`, `AIName`, `ScriptName`) VALUES
(970500, 'Lowell Marsh', 'Lamplighter', 0, 10, 10, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(970501, 'Scarlet Courier', NULL, 0, 9, 10, 67, 0, 1, 1.14286, 1, 0, 7, 0, 1, 1, 40, 40, 0, '', ''),
(970502, 'Charred letter recovered', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970503, 'Innkeeper Renee questioned', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970504, 'Mrs. Winters questioned', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970505, 'Abigail Shiel questioned', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970506, 'Signs of the informant found', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970507, 'Street lamp searched', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970508, 'Captured Scarlet Zealot questioned', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970509, 'Lowell Marsh\'s fate decided', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', '');
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`) VALUES
(970500, 0, 2611, 1, 1),
(970501, 0, 2467, 1, 1),
(970501, 1, 2478, 1, 1),
(970502, 0, 11686, 1, 1),
(970503, 0, 11686, 1, 1),
(970504, 0, 11686, 1, 1),
(970505, 0, 11686, 1, 1),
(970506, 0, 11686, 1, 1),
(970507, 0, 11686, 1, 1),
(970508, 0, 11686, 1, 1),
(970509, 0, 11686, 1, 1);
INSERT INTO `creature` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(970500, 970500, 0, 85, 0, 1, 33554432, 2236.000, 286.000, 35.170, 0.3000, 60, 0, 0, 'mod-brill-home town'),
(970501, 970501, 0, 85, 0, 1, 1, 2480.000, 150.000, 29.020, 1.0000, 120, 4, 1, 'mod-brill-home town'),
(970502, 970501, 0, 85, 0, 1, 1, 2495.000, 165.000, 29.030, 3.5000, 120, 4, 1, 'mod-brill-home town'),
(970503, 970501, 0, 85, 0, 1, 1, 2505.000, 150.000, 28.210, 2.2000, 120, 4, 1, 'mod-brill-home town'),
(970504, 970501, 0, 85, 0, 1, 1, 2475.000, 170.000, 29.920, 5.0000, 120, 4, 1, 'mod-brill-home town');
INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `Data0`, `Data1`, `ScriptName`) VALUES
(970500, 10, 397, 'Smouldering Fire', 1, 0, 970500, 'go_brill_town'),
(970501, 10, 134, 'Loose Stones', 0.4, 0, 970501, 'go_brill_town'),
(970502, 10, 275, 'Chalk-Marked Crate', 0.8, 0, 970501, 'go_brill_town'),
(970503, 10, 220, 'Folded Note', 1, 0, 970502, 'go_brill_town');
INSERT INTO `gameobject_template_addon` (`entry`, `faction`, `flags`) VALUES (970500, 0, 4), (970501, 0, 4), (970502, 0, 4), (970503, 0, 4);
INSERT INTO `gameobject` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`, `animprogress`, `state`, `Comment`) VALUES
(970500, 970500, 0, 85, 0, 1, 1, 2485.000, 158.000, 29.070, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(970501, 970500, 0, 85, 0, 1, 1, 2500.000, 175.000, 30.110, 1.2000, 0, 0, 0.564642, 0.825336, 0, 255, 1, 'mod-brill-home town'),
(970502, 970500, 0, 85, 0, 1, 1, 2470.000, 162.000, 30.090, 2.4000, 0, 0, 0.932039, 0.362358, 0, 255, 1, 'mod-brill-home town'),
(970503, 970501, 0, 85, 0, 1, 1, 2292.300, 314.300, 35.450, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(970504, 970502, 0, 85, 0, 1, 1, 2281.000, 257.000, 34.470, 1.9000, 0, 0, 0.813416, 0.581683, 0, 255, 1, 'mod-brill-home town'),
(970505, 970503, 0, 85, 0, 1, 1, 2270.500, 327.300, 34.600, 0.5000, 0, 0, 0.247404, 0.968912, 0, 255, 1, 'mod-brill-home town'),
(970506, 970503, 0, 85, 0, 1, 1, 2225.400, 252.400, 33.710, 2.0000, 0, 0, 0.841471, 0.540302, 0, 255, 1, 'mod-brill-home town'),
(970507, 970503, 0, 85, 0, 1, 1, 2280.600, 434.300, 34.150, 4.0000, 0, 0, 0.909297, -0.416147, 0, 255, 1, 'mod-brill-home town');
INSERT INTO `brill_town_use` (`go`, `ord`, `cond`, `quest`, `credit`, `text_id`, `marker`, `tele_map`, `tele_x`, `tele_y`, `tele_z`, `tele_o`) VALUES
(970500, 0, 'I970500', 970500, 970502, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970501, 0, 'I970501', 970501, 970506, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970502, 0, 'I970501', 970501, 970506, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970503, 0, 'I970502', 970502, 970507, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000);
INSERT INTO `brill_town_gossip` (`npc`, `ord`, `kind`, `cond`, `icon`, `text`, `text_id`, `action`, `quest`, `credit`, `marker`, `emote`, `reply`, `arg`) VALUES
(970500, 3000, 'greet', 'R970506 D4', 0, NULL, 970500, '', 0, 0, 0, 0, NULL, 0),
(970500, 3001, 'greet', 'R970506', 0, NULL, 970501, '', 0, 0, 0, 0, NULL, 0),
(970500, 3002, 'greet', 'A970504', 0, NULL, 970502, '', 0, 0, 0, 0, NULL, 0),
(970500, 3003, 'greet', 'T970502', 0, NULL, 970503, '', 0, 0, 0, 0, NULL, 0),
(970500, 3004, 'greet', '', 0, NULL, 970504, '', 0, 0, 0, 0, NULL, 0),
(970500, 3005, 'option', 'I970504', 0, 'Magistrate Sevren will hear all of it. You\'ll answer to him.', 0, 'choice', 970504, 970509, 970505, 2, '(Lowell nods, as if he had expected nothing else.) Yes. That\'s fair. Will you walk with me to the town hall? I\'d rather not go with the Deathguard\'s hands on my arms. They were my friends, you see.$B$B(He sets his lamp-pole against the well, very carefully, as though someone else might need it.)', 0),
(970500, 3006, 'option', 'I970504', 0, 'Burn Anselm\'s letters and stay. Be what you are, and be it here.', 0, 'choice', 970504, 970509, 970506, 18, 'Stay. As this. (He looks at his hands for a long time.) Brother Anselm called me a lamb lost in the dark. You\'re the first to say the dark\'s a place a person can live in.$B$BI\'ll burn them. Tonight. All of them. And if he writes again, I\'ll burn that too. If you see me wavering, $n, you have my leave to tell Sevren everything.', 0),
(970500, 3007, 'option', 'I970504', 0, 'Take the west road tonight. Don\'t come back to Brill.', 0, 'choice', 970504, 970509, 970507, 2, 'You\'d... (His voice catches.) I won\'t go to Anselm. I swear it. I\'ll go somewhere the Crusade has never heard of and neither has the Dark Lady, if there\'s such a place left.$B$B(He takes nothing but his coat.) Light the north road lamp for me, would you? Someone ought to. Goodbye, $n.', 0),
(5688, 3008, 'option', 'I970501', 0, 'Who in Brill keeps odd hours, Renee?', 0, 'credit', 970501, 970503, 0, 0, 'Odd hours? Love, everyone here\'s dead; there are no other kind. (She lowers her voice.) But since you ask: the only one who comes in after the second bell is old Lowell, the lamplighter. Takes a seat by the back door, never drinks, leaves when the watch changes. I always thought he was lonely.', 0),
(2134, 3009, 'option', 'I970501', 0, 'Has anyone been asking about the Deathguard\'s rounds?', 0, 'credit', 970501, 970504, 0, 0, 'Asking? No one needs to ask. Every child in the old Brill could tell you when the watch changed by when the lamps were lit. (She frowns.) Strange thing, though. Lowell Marsh bought a whole quire of paper from me last month. Lamplighters don\'t write much.', 0),
(2118, 3010, 'option', 'I970501', 0, 'Seen anyone by the cistern after dark?', 0, 'credit', 970501, 970505, 0, 0, 'The well? Only the lamplighter, and he\'s always there; he fills his oil pot from the cistern beside it. (She pauses.) Though he did take an awfully long time over it last week. Down on his knees. I took it for prayer. You\'d be surprised how many of us still do.', 0),
(1931, 3011, 'option', 'I970502', 0, '(Show him the charred letters.)', 0, 'credit', 970502, 970508, 0, 0, '(The zealot glances at the letters and his cracked lips twitch into a smile.) Ah. Our little lamb\'s handwriting. He\'ll be made whole, you know, when the Light comes to cleanse this place. Brother Anselm promised him. (He catches himself, too late, and turns his face to the wall.)', 0),
(1931, 3012, 'greet', 'R970505', 0, NULL, 970505, '', 0, 0, 0, 0, NULL, 0),
(1499, 3013, 'greet', 'R970505', 0, NULL, 970506, '', 0, 0, 0, 0, NULL, 0),
(1499, 3014, 'greet', 'R970507', 0, NULL, 970507, '', 0, 0, 0, 0, NULL, 0),
(1499, 3015, 'greet', 'R970506', 0, NULL, 970508, '', 0, 0, 0, 0, NULL, 0),
(5688, 3016, 'greet', 'R970507 D3', 0, NULL, 970509, '', 0, 0, 0, 0, NULL, 0),
(1652, 3017, 'greet', 'R970505', 0, NULL, 970510, '', 0, 0, 0, 0, NULL, 0),
(1652, 3018, 'greet', 'R970507', 0, NULL, 970511, '', 0, 0, 0, 0, NULL, 0),
(1746, 3019, 'greet', 'R970506', 0, NULL, 970512, '', 0, 0, 0, 0, NULL, 0),
(1746, 3020, 'greet', 'R970505', 0, NULL, 970513, '', 0, 0, 0, 0, NULL, 0),
(1745, 3021, 'greet', 'R970507', 0, NULL, 970514, '', 0, 0, 0, 0, NULL, 0),
(1745, 3022, 'greet', 'R970504', 0, NULL, 970515, '', 0, 0, 0, 0, NULL, 0),
(2209, 3023, 'greet', 'R970505', 0, NULL, 970516, '', 0, 0, 0, 0, NULL, 0),
(2210, 3024, 'greet', 'R970504', 0, NULL, 970517, '', 0, 0, 0, 0, NULL, 0);
UPDATE `creature_template` SET `npcflag` = `npcflag` | 1 WHERE `entry` IN (1499, 1652, 1745, 1746, 1931, 2118, 2134, 2209, 2210, 5688);
INSERT INTO `brill_town_phase` (`bit`, `ord`, `cond`) VALUES
(33554432, 0, '!R970505 !R970507');
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `Flags`, `RewardXPDifficulty`, `RewardMoney`, `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `AreaDescription`, `QuestCompletionLog`, `RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `ObjectiveText1`, `RequiredNpcOrGo2`, `RequiredNpcOrGoCount2`, `ObjectiveText2`, `RequiredNpcOrGo3`, `RequiredNpcOrGoCount3`, `ObjectiveText3`, `RequiredNpcOrGo4`, `RequiredNpcOrGoCount4`, `ObjectiveText4`, `RewardItem1`, `RewardAmount1`, `RewardItem2`, `RewardAmount2`, `RewardItem3`, `RewardAmount3`, `RewardItem4`, `RewardAmount4`) VALUES
(970500, 2, -1, 5, 159, 0, 4, 1800, 0, 'Letters in the Ashes', 'Kill 4 Scarlet Couriers in the hollow northeast of Brill and recover 3 charred letters from their campfires, then return to Magistrate Sevren in Brill.', 'Three nights ago the Crusade ambushed a supply cart on the east road. They knew which road, they knew which hour, and they knew the escort would be two Deathguards short because of the changing of the watch. That is not luck, $n. Luck doesn\'t keep a schedule.$B$BSomeone is telling them. I don\'t yet know who, and I\'d rather not hang the wrong neck; the town has few enough left.$B$BMy scouts have seen Scarlet couriers in the hollow northeast of town, past the cemetery road. When they\'re cornered they throw their letters on the fire. Zealots: they\'d rather burn the evidence than trust Light to protect it. Kill them before they finish the job and pull what you can from the ashes. Half a letter is still a letter.', '', 'Return to Magistrate Sevren in Brill.', 970501, 4, '', 970502, 3, 'Charred letter recovered', 0, 0, '', 0, 0, '', 858, 2, 0, 0, 0, 0, 0, 0),
(970501, 2, -1, 5, 159, 0, 4, 2000, 0, 'Eyes Among Us', 'Question Innkeeper Renee, Mrs. Winters and Abigail Shiel, and look for signs of the informant by the cistern and behind the tavern. Then return to Magistrate Sevren.', 'If I start asking questions myself, the whole town will know by supper that the Magistrate is frightened. They\'d be right, but there\'s no reason to tell them.$B$BYou\'re new enough that people still talk to you. Go and listen. Innkeeper Renee hears everything said over a drink; Mrs. Winters and Abigail Shiel keep the market and see who comes and goes. Ask them who keeps odd hours, who has been asking after the watch.$B$BAnd look around while you\'re at it. Letters have to pass from hand to hand somewhere. The cistern and the back of the tavern are both quiet after dark, and both on a patrol\'s blind side. If I were selling my town, that is where I\'d do it.', '', 'Return to Magistrate Sevren in Brill.', 970503, 1, 'Innkeeper Renee questioned', 970504, 1, 'Mrs. Winters questioned', 970505, 1, 'Abigail Shiel questioned', 970506, 2, 'Signs of the informant found', 0, 0, 0, 0, 0, 0, 0, 0),
(970502, 2, -1, 5, 159, 0, 4, 2000, 0, 'The Scarlet Informant', 'Search the street lamps of Brill for anything left at their feet, and question the Captured Scarlet Zealot in the tavern\'s cellar. Then return to Magistrate Sevren.', 'Everything you found keeps time with the lamps. The letter names the hour the lamps are lit. The chalk and the cistern are on the lamplighter\'s round. Every word of it points at Lowell Marsh, and I\'ve known Lowell since before the Dark Lady gave us back our wills. He lit the lamps in this town when it had living people in it.$B$BSo I want proof, not a pattern. Look at the lamps along the street. A man who leaves word for someone leaves it where his hands already are.$B$BThen go down to the cellar under the Gallows\' End. We have a zealot down there who thinks his silence is a prayer. Show him the letters. Even a zealot\'s face says something.', '', 'Return to Magistrate Sevren in Brill.', 970507, 3, 'Street lamp searched', 970508, 1, 'Captured Scarlet Zealot questioned', 0, 0, '', 0, 0, '', 2455, 2, 0, 0, 0, 0, 0, 0),
(970503, 2, -1, 5, 159, 0, 2, 1000, 0, 'The Promise of Life', 'Confront Lowell Marsh, the lamplighter, by the cistern in Brill.', 'Go to him, $n. Not with guards; he\'d only lie to guards, and he\'d lie badly, and someone would lose patience. Go yourself. He\'s by the cistern most evenings, cleaning his glass.$B$BI want to know why. Forty years he served this town, and the Crusade burns people like him by the cartload. Whatever they offered him, it must have been worth more to him than his neighbors.$B$BFind out what it was. Then we\'ll decide what Brill does about it. Or what you do, if I can\'t bring myself to.', '', 'Speak with Lowell Marsh in Brill.', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(970504, 2, -1, 5, 159, 0, 5, 3500, 0, 'A Betrayer\'s Fate', 'Decide Lowell Marsh\'s fate: expose him to Magistrate Sevren, persuade him to abandon his arrangement, or help him escape Brill. Then return to Magistrate Sevren.', 'Two of our Deathguards died on that east road. I know their names. Morgan and Pell. I lit the lamp they walked under on the way out of town.$B$BI didn\'t think... no. I did think. I just thought about the sun more.$B$BBrother Anselm writes that it\'s nearly ready, the rite. A few more letters. I don\'t even know anymore if I believe him. A man who wants you to betray your town for a miracle would say the miracle was nearly ready, wouldn\'t he?$B$B(He laughs, a dry sound.)$B$BSevren sent you, so it\'s yours to say. Hand me to him, and I\'ll go quietly. Tell me to burn Anselm\'s letters, and I\'ll try, though I don\'t know if I can. Or look the other way while I take the west road tonight, and I\'ll never trouble Brill again. Whatever you choose, $n, I won\'t blame you for it. I\'ve used up all my blaming on myself.', '', 'Return to Magistrate Sevren in Brill.', 970509, 1, 'Lowell Marsh\'s fate decided', 0, 0, '', 0, 0, '', 0, 0, '', 4496, 1, 0, 0, 0, 0, 0, 0),
(970505, 2, 1, 1, -1, 0, 0, 0, 0, '[exposed]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(970506, 2, 1, 1, -1, 0, 0, 0, 0, '[spared]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(970507, 2, 1, 1, -1, 0, 0, 0, 0, '[escaped]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`, `SpecialFlags`) VALUES (970500, 0, 0), (970501, 970500, 0), (970502, 970501, 0), (970503, 970502, 0), (970504, 970503, 0);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`) VALUES
(970500, 1, '(Sevren lays the blackened pages on his desk and smooths them flat with a careful finger.)$B$B"...the eastern escort changes at the second bell, and the north road stands empty until the lamps are lit..." They know when the lamps are lit. Of course they do.$B$BThis wasn\'t written by a Crusader, $n. Look at the hand: it shakes. Whoever wrote this has been dead a long time and still remembers his letters. One of ours.'),
(970501, 1, 'A chalk mark behind the tavern and a hollow under the cistern\'s stones, and three good women who all mention, without being asked, the man who\'s always about when the patrols change.$B$B(Sevren closes his eyes.)$B$BNo. Don\'t say the name yet. I want to be certain before I let myself think it.'),
(970502, 1, 'Three folded notes, one at the foot of each lamp, each with nothing on it but an hour, and a zealot who laughed and called him "our lamb."$B$B(Sevren is quiet for a long moment.)$B$BLowell Marsh. A lamplighter. He walks every street with the night watch; they talk to him about their hours because he\'s harmless. He has been harmless for forty years.$B$BI could have the Deathguard drag him in tonight. I find I don\'t want to. Not yet.'),
(970503, 1, '(Lowell Marsh sets down his lamp-pole very slowly. For a moment he looks as if he means to run; then his shoulders drop.)$B$BSo the Magistrate knows. Good. I\'m tired of carrying it.$B$BHis name is Brother Anselm. He found me on the north road last spring, alone with my ladder, and he didn\'t burn me. He talked to me. He said the Light can call a soul back into living flesh, that it\'s been done, that the Scourge\'s curse is only a sickness and sicknesses are cured. He said he\'d pray over me himself. He said I\'d feel the sun again.$B$BAll I had to do was tell him when the lamps were lit.$B$B(He looks down at his grey hands.)$B$BDo you know what it is to remember warmth, $g sir:madam;? I\'d have told him anything.'),
(970504, 1, 'It\'s done, then.$B$B(Sevren doesn\'t ask for details, and seems careful not to look as if he wants them.)$B$BThe Crusade will find our patrols harder to read now, whatever became of the man who read them. I\'ll change the watch hours tonight regardless; I\'d be a fool not to.$B$BYou did a hard, quiet thing for this town, $n. Those are the ones nobody thanks you for, so let me be the one who does. Thank you.');
INSERT INTO `quest_request_items` (`ID`, `EmoteOnComplete`, `EmoteOnIncomplete`, `CompletionText`) VALUES
(970500, 1, 1, 'Anything from the hollow? Even a scrap with a date on it would do.'),
(970501, 1, 1, 'Well? I\'ve been staring at that letter so long I could forge it.'),
(970502, 1, 1, 'The lamps, $n, and the zealot. Then we\'ll know.'),
(970504, 1, 1, '(Lowell waits, turning his lamp-pole in his hands.)');
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES (1499, 970500), (1499, 970501), (1499, 970502), (1499, 970503), (970500, 970504);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES (1499, 970500), (1499, 970501), (1499, 970502), (970500, 970503), (1499, 970504);
UPDATE `creature_template` SET `npcflag` = `npcflag` | 3 WHERE `entry` IN (1499);

-- The Last Customer
INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`) VALUES (970600, 0, 755, 0, 0, 0), (970600, 1, 17027, 0, 0, 0), (970600, 2, 5042, 0, 0, 0), (970600, 3, 5048, 0, 0, 0), (970600, 4, 3419, 0, 0, 0), (970600, 5, 3420, 0, 0, 0), (970600, 6, 5363, 0, 0, 0), (970600, 7, 18233, 0, 0, 0), (970600, 8, 5374, 0, 0, 0), (970600, 9, 5115, 0, 0, 0), (970600, 10, 5376, 0, 0, 0), (970600, 11, 3300, 0, 0, 0), (970600, 12, 5373, 0, 0, 0), (970600, 13, 5433, 0, 0, 0), (970600, 14, 11940, 0, 0, 0), (970600, 15, 6297, 0, 0, 0);
INSERT INTO `creature_template` (`entry`, `name`, `subname`, `gossip_menu_id`, `minlevel`, `maxlevel`, `faction`, `npcflag`, `speed_walk`, `speed_run`, `unit_class`, `unit_flags`, `type`, `rank`, `HealthModifier`, `DamageModifier`, `mingold`, `maxgold`, `flags_extra`, `AIName`, `ScriptName`) VALUES
(970600, 'Ambrose Wicke', 'Candles and Sundries', 0, 22, 22, 68, 131, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(970601, 'Agnes Balnir', 'Laundress', 0, 18, 18, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(970602, 'Dusty corners cleaned', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970603, 'Order ledger found', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970604, 'The ledger\'s last entry read', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970605, 'The wrapped order found', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970606, 'Magistrate Sevren asked about the Balnirs', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970607, 'Signs of the Balnirs\' fate found', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970608, 'The candlesticks settled', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', '');
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`) VALUES
(970600, 0, 2622, 1, 1),
(970601, 0, 2671, 1, 1),
(970602, 0, 11686, 1, 1),
(970603, 0, 11686, 1, 1),
(970604, 0, 11686, 1, 1),
(970605, 0, 11686, 1, 1),
(970606, 0, 11686, 1, 1),
(970607, 0, 11686, 1, 1),
(970608, 0, 11686, 1, 1);
INSERT INTO `creature` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(970600, 970600, 0, 85, 0, 1, 1, 2345.300, 277.900, 34.750, 2.7000, 60, 0, 0, 'mod-brill-home town'),
(970601, 970601, 0, 85, 0, 1, 1, 547.000, 1588.000, 130.120, 0.9000, 60, 0, 0, 'mod-brill-home town');
INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `Data0`, `Data1`, `ScriptName`) VALUES
(970600, 5, 7872, 'Wicke\'s Stall', 1, 0, 0, ''),
(970601, 5, 7732, 'Shop Counter', 1, 0, 0, ''),
(970602, 10, 159, 'Moth-Eaten Rug', 1, 0, 970600, 'go_brill_town'),
(970603, 10, 113, 'Dust-Choked Crate', 1, 0, 970600, 'go_brill_town'),
(970604, 10, 187, 'Cobwebbed Shelf', 1, 0, 970600, 'go_brill_town'),
(970605, 10, 164, 'Green-Bound Ledger', 1, 0, 970600, 'go_brill_town'),
(970606, 10, 4191, 'Paper-Wrapped Parcel', 1, 0, 970601, 'go_brill_town'),
(970607, 10, 2491, 'Weathered Notice', 1, 0, 970602, 'go_brill_town'),
(970608, 10, 470, 'Scorched Family Book', 1, 0, 970602, 'go_brill_town'),
(970609, 10, 2452, 'Balnir Family Stone', 1, 0, 970602, 'go_brill_town'),
(970610, 5, 100, 'Wicke\'s Candles', 1, 0, 0, ''),
(970611, 5, 7494, 'Basket of Sundries', 1, 0, 0, ''),
(970612, 5, 6311, 'Black Roses', 1, 0, 0, ''),
(970613, 5, 107, 'Second-Hand Books', 1, 0, 0, '');
INSERT INTO `gameobject_template_addon` (`entry`, `faction`, `flags`) VALUES (970602, 0, 4), (970603, 0, 4), (970604, 0, 4), (970605, 0, 4), (970606, 0, 4), (970607, 0, 4), (970608, 0, 4), (970609, 0, 4);
INSERT INTO `gameobject` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`, `animprogress`, `state`, `Comment`) VALUES
(970600, 970600, 0, 85, 0, 1, 1, 2345.000, 278.000, 34.720, 2.7000, 0, 0, 0.975723, 0.219007, 0, 255, 1, 'mod-brill-home town'),
(970601, 970601, 0, 85, 0, 1, 1, 2343.900, 278.500, 34.600, 2.7000, 0, 0, 0.975723, 0.219007, 0, 255, 1, 'mod-brill-home town'),
(970602, 970602, 0, 85, 0, 1, 1, 2342.100, 279.400, 34.430, 2.7000, 0, 0, 0.975723, 0.219007, 0, 255, 1, 'mod-brill-home town'),
(970603, 970603, 0, 85, 0, 1, 1, 2345.800, 280.900, 34.610, 1.2000, 0, 0, 0.564642, 0.825336, 0, 255, 1, 'mod-brill-home town'),
(970604, 970604, 0, 85, 0, 1, 1, 2347.900, 279.500, 34.910, 2.7000, 0, 0, 0.975723, 0.219007, 0, 255, 1, 'mod-brill-home town'),
(970605, 970605, 0, 85, 0, 1, 1, 2343.100, 277.200, 34.570, 2.7000, 0, 0, 0.975723, 0.219007, 0, 255, 1, 'mod-brill-home town'),
(970606, 970606, 0, 85, 0, 1, 1, 2345.600, 275.100, 34.920, 2.7000, 0, 0, 0.975723, 0.219007, 0, 255, 1, 'mod-brill-home town'),
(970607, 970607, 0, 85, 0, 1, 1, 1998.000, -455.000, 34.530, 1.6000, 0, 0, 0.717356, 0.696707, 0, 255, 1, 'mod-brill-home town'),
(970608, 970608, 0, 85, 0, 1, 1, 1948.000, -442.000, 35.450, 0.3000, 0, 0, 0.149438, 0.988771, 0, 255, 1, 'mod-brill-home town'),
(970609, 970609, 0, 85, 0, 1, 1, 2041.000, -517.000, 43.660, 4.7000, 0, 0, 0.711473, -0.702713, 0, 255, 1, 'mod-brill-home town'),
(970610, 970610, 0, 85, 0, 1, 67108864, 2341.600, 276.500, 34.450, 2.7000, 0, 0, 0.975723, 0.219007, 0, 255, 1, 'mod-brill-home town'),
(970611, 970611, 0, 85, 0, 1, 67108864, 2343.500, 281.800, 34.440, 1.9000, 0, 0, 0.813416, 0.581683, 0, 255, 1, 'mod-brill-home town'),
(970612, 970612, 0, 85, 0, 1, 67108864, 2340.500, 278.300, 34.430, 2.7000, 0, 0, 0.975723, 0.219007, 0, 255, 1, 'mod-brill-home town'),
(970613, 970613, 0, 85, 0, 1, 67108864, 2347.400, 280.600, 34.770, 1.0000, 0, 0, 0.479426, 0.877583, 0, 255, 1, 'mod-brill-home town');
INSERT INTO `brill_town_use` (`go`, `ord`, `cond`, `quest`, `credit`, `text_id`, `marker`, `tele_map`, `tele_x`, `tele_y`, `tele_z`, `tele_o`) VALUES
(970602, 0, 'I970600', 970600, 970602, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970603, 0, 'I970600', 970600, 970602, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970604, 0, 'I970600', 970600, 970602, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970605, 0, 'I970600', 970600, 970603, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970606, 0, 'I970601', 970601, 970605, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970607, 0, 'I970602', 970602, 970607, 970600, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970608, 0, 'I970602', 970602, 970607, 970601, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970609, 0, 'I970602', 970602, 970607, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000);
INSERT INTO `brill_town_gossip` (`npc`, `ord`, `kind`, `cond`, `icon`, `text`, `text_id`, `action`, `quest`, `credit`, `marker`, `emote`, `reply`, `arg`) VALUES
(970600, 4000, 'greet', 'R970604 R970605', 0, NULL, 970602, '', 0, 0, 0, 0, NULL, 0),
(970600, 4001, 'greet', 'R970604 R970606', 0, NULL, 970603, '', 0, 0, 0, 0, NULL, 0),
(970600, 4002, 'greet', 'R970604', 0, NULL, 970604, '', 0, 0, 0, 0, NULL, 0),
(970600, 4003, 'greet', 'A970604', 0, NULL, 970605, '', 0, 0, 0, 0, NULL, 0),
(970600, 4004, 'greet', 'T970603', 0, NULL, 970606, '', 0, 0, 0, 0, NULL, 0),
(970600, 4005, 'greet', 'T970602', 0, NULL, 970607, '', 0, 0, 0, 0, NULL, 0),
(970600, 4006, 'greet', 'T970600', 0, NULL, 970608, '', 0, 0, 0, 0, NULL, 0),
(970600, 4007, 'greet', '', 0, NULL, 970609, '', 0, 0, 0, 0, NULL, 0),
(970600, 4008, 'option', 'I970601', 0, 'Read the ledger\'s last entry with him.', 0, 'credit', 970601, 970604, 0, 1, '"Balnir, T., of the Balnir Farmstead. One pair candlesticks, silvered, vine pattern, engraved. For his wedding. Paid in full, in coin and two seasons\' beeswax." And the date, $n. Read me the date. ...Eleven years? No. No, that\'s the ink. It runs.', 0),
(970600, 4009, 'option', 'I970604', 0, 'Light them, and keep them in your window. For the wedding.', 0, 'choice', 970604, 970608, 970605, 2, 'In the window. Yes. Yes, that\'s proper. Folk will ask who they\'re for, and I\'ll say: a customer. Paid in full. Not for sale.', 0),
(970600, 4010, 'option', 'I970604', 0, 'Sell them to the next couple who\'ll have them. Someone should be married by them.', 0, 'choice', 970604, 970608, 970606, 273, 'Sell them. To a wedding. Hah! In Brill! I may be waiting another eleven years, $n. But I\'ll wait with the shutters open, this time.', 0),
(970600, 4011, 'option', 'R970604', 1, 'Let me see what you\'re selling.', 0, 'vendor', 0, 0, 0, 0, NULL, 0),
(970600, 4012, 'option', 'R970604 O', 0, 'Anything for the house by the road?', 0, 'say', 0, 0, 0, 1, 'The old Harrow place? Candles, $n. A house is only a house until someone lights a candle in it. After that it\'s a home, and after that, in my experience, it\'s a fire risk. I sell buckets too.', 0),
(970600, 4013, 'option', 'R970604 R970205', 0, 'I had a housewarming, you know.', 0, 'say', 0, 0, 0, 6, 'And nobody told me? I\'d have brought a candle. Two! Well. Next time someone in Brill dies and gets up again, we\'ll call it a housewarming and I\'ll bring three.', 0),
(1499, 4014, 'option', 'I970601', 0, 'Do the town\'s books say what became of the Balnir family?', 0, 'credit', 970601, 970606, 0, 1, 'Balnir. The farm south-east, past the crossroads. The Crown quarantined it the first autumn of the plague: the grain. My predecessor\'s hand. No departures recorded, $n, and nobody living\'s been there since. If Wicke\'s sending you out there, tell him the Deathguard won\'t fetch you back.', 0),
(970601, 4015, 'greet', 'R970604', 0, NULL, 970610, '', 0, 0, 0, 0, NULL, 0),
(970601, 4016, 'greet', 'R970603', 0, NULL, 970611, '', 0, 0, 0, 0, NULL, 0),
(970601, 4017, 'greet', '', 0, NULL, 970612, '', 0, 0, 0, 0, NULL, 0),
(970601, 4018, 'option', 'R970603', 0, 'Tell me about the wedding that never happened.', 0, 'say', 0, 0, 0, 1, 'Harvest, the twelfth. Marian had a dress her mother wore, let out twice. Father had bought a pig. I was to come home from Silverpine the week before. I didn\'t: the roads were closed. I had a letter from Tobias saying the grain had come in plentiful, and they\'d have bread enough for half of Brill. That was the last letter. I\'ve read it so often I don\'t need it any more.', 0);
UPDATE `creature_template` SET `npcflag` = `npcflag` | 1 WHERE `entry` IN (1499);
INSERT INTO `brill_town_phase` (`bit`, `ord`, `cond`) VALUES
(67108864, 0, 'R970604');
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `Flags`, `RewardXPDifficulty`, `RewardMoney`, `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `AreaDescription`, `QuestCompletionLog`, `RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `ObjectiveText1`, `RequiredNpcOrGo2`, `RequiredNpcOrGoCount2`, `ObjectiveText2`, `RequiredNpcOrGo3`, `RequiredNpcOrGoCount3`, `ObjectiveText3`, `RequiredNpcOrGo4`, `RequiredNpcOrGoCount4`, `ObjectiveText4`, `RewardItem1`, `RewardAmount1`, `RewardItem2`, `RewardAmount2`, `RewardItem3`, `RewardAmount3`, `RewardItem4`, `RewardAmount4`) VALUES
(970600, 2, -1, 5, 159, 0, 2, 600, 0, 'Business as Usual', 'Clean the dust from Ambrose Wicke\'s stall behind Brill\'s town hall and find his old order ledger.', 'Closed. Can\'t you read the sign? Oh. The sign fell down. Years ago, I expect.$B$BAmbrose Wicke, candles, lamps and sundries, established in Brill before most of Brill was buried. I don\'t sell, $g lad:lass;. Not until an order is collected. A customer paid in full, and a shop that sells his goods out from under him is a shop that cheats. My father said that, and his father before him, and they were both a great deal warmer than I am now.$B$BBut the dust. The dust I will admit to. I woke behind this counter after the plague and I have been standing at it since, and the moths have had the run of the place. Shake out the rug, clear the crate and the shelf, and look under the counter for my order ledger. Green binding. It has his name in it. I\'d look myself, but I\'m keeping shop.', '', 'Return to Ambrose Wicke in Brill.', 970602, 3, 'Dusty corners cleaned', 970603, 1, 'Order ledger found', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(970601, 2, -1, 5, 159, 0, 3, 800, 0, 'An Outstanding Order', 'Read the ledger\'s last entry with Ambrose Wicke, find the order wrapped at the back of his stall, and ask Magistrate Sevren in Brill\'s town hall about the customer\'s family.', 'Now that you\'ve found it, you may as well read it. My eyes aren\'t what they were, chiefly because one of them isn\'t anywhere.$B$BThe last entry. Read it with me. He\'ll be here any day: he said so when he paid. Then look at the back of the stall, behind the shelf. His order is wrapped in brown paper and string, the way it\'s been waiting.$B$BAnd ask the Magistrate about the family. Sevren keeps the town\'s books now, such as they are. If the young man\'s moved house, the Magistrate will know where. People move. I did. Into the ground and out again, but it counts.', '', 'Return to Ambrose Wicke in Brill.', 970604, 1, 'The ledger\'s last entry read', 970605, 1, 'The wrapped order found', 970606, 1, 'Magistrate Sevren asked about the Balnirs', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(970602, 2, -1, 9, 159, 0, 4, 1500, 0, 'No Forwarding Address', 'Search the Balnir Farmstead, south-east of Brill, for what became of the Balnir family, then return to Ambrose Wicke.', 'The Balnir Farmstead. South and east of here, past the crossroads, where the road bends toward the old Crusade tower. A good farm, once: Tobias\'s father grew snapdragons for the market, of all things, and brought me the wax from his bees.$B$BGo and see. There will be something. A notice on the gate, a family book in the house, the stones in the family plot; farmers write things down, and they bury their people where they can see them from the kitchen.$B$BMind the farm. The Magistrate says nothing living goes there, and from his face I gather nothing dead goes there gladly either. Find out where Tobias went, $n. I don\'t ask you to bring him. Only to tell me where to send word.', '', 'Return to Ambrose Wicke in Brill.', 970607, 3, 'Signs of the Balnirs\' fate found', 0, 0, '', 0, 0, '', 0, 0, '', 858, 2, 0, 0, 0, 0, 0, 0),
(970603, 2, -1, 9, 159, 0, 3, 1000, 0, 'The Gift Never Given', 'Find Agnes Balnir at the Sepulcher in Silverpine Forest.', 'Silverpine. A great many of us who woke there went no further than the Sepulcher: the Dark Lady\'s people keep it, and it\'s the nearest thing to a town those woods have left. If Agnes Balnir is anywhere, she\'s there, or under it.$B$BGo and find her. Don\'t tell her about the candlesticks straight off. Tell her Ambrose Wicke of Brill is holding an order in her brother\'s name, paid in full, and wishes to know what she would like done with it. That\'s the proper form.$B$BAnd $n... if she doesn\'t remember him, don\'t press her. Some of us came back with the whole of our lives. Some came back with a name and a smell of smoke.', '', 'Return to Agnes Balnir at the Sepulcher.', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(970604, 2, -1, 9, 159, 0, 4, 2500, 0, 'Closing the Ledger', 'Take Agnes Balnir\'s letter to Ambrose Wicke in Brill and decide what becomes of the candlesticks.', 'I\'ve written to him. It\'s short. I was never one for letters; Tobias wrote them for both of us.$B$BI can\'t say what\'s to be done with them, $n. If I say keep them, I\'m keeping a wedding that never came. If I say sell them, I\'m selling my brother\'s last good idea. So I\'ve told old Wicke the order is yours to settle. You found the farm. You saw the grave. You choose.$B$BTell him one more thing for me, would you? Tell him Tobias isn\'t coming. Not because he doesn\'t care. Whatever climbed out of that grave wasn\'t my brother, and it didn\'t come to me, or to Marian, and it won\'t come to a candle shop. Tell him to open the shutters.', '', 'Return to Ambrose Wicke in Brill.', 970608, 1, 'The candlesticks settled', 0, 0, '', 0, 0, '', 0, 0, '', 7338, 1, 0, 0, 0, 0, 0, 0),
(970605, 2, 1, 1, -1, 0, 0, 0, 0, '[lit]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(970606, 2, 1, 1, -1, 0, 0, 0, 0, '[sold]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`, `SpecialFlags`) VALUES (970600, 0, 0), (970601, 970600, 0), (970602, 970601, 0), (970603, 970602, 0), (970604, 970603, 0);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`) VALUES
(970600, 1, 'There it is. The binding\'s gone grey, but then so have I.$B$BAnd the stall looks very nearly like a place someone might buy something. Not that they may. Take this for your trouble: it\'s payment, not a sale, and I\'ll thank you not to confuse the two.'),
(970601, 1, 'Quarantined. By the Crown.$B$BI remember the soldiers on the road. I remember thinking it was a great deal of fuss over grain.$B$BAnd the date. Eleven years. I\'d have sworn it was last spring. You lose the count, standing still; the days don\'t come in and buy anything, so you don\'t notice them. Still. A farm doesn\'t move, $n. Someone there will know where he went.'),
(970602, 1, 'Marian first, then Tobias, then the old man. And the grave open.$B$B...$B$BI sold Osric Balnir his wife\'s funeral candles, you know. Plain ones. He wouldn\'t take the good ones on credit, though I offered.$B$BBut the girl. Agnes. Her name isn\'t crossed out. In service in Silverpine, the book says. If she lived, or if she did what I did and didn\'t stay dead, she is the order\'s next of kin.'),
(970603, 1, 'Ambrose Wicke? Old Wicke, with the candles? He\'s still... well. Aren\'t we all, still.$B$BTobias\'s candlesticks. He showed me the drawing. Silver, with a vine going up them, and their names on the base and the date. Harvest, the twelfth. Four years they waited for the levies to come down so the wedding could be paid for, and when they finally set the day it was the week the grain came.$B$BI remember it. I remember all of it. That\'s the trouble with me.'),
(970604, 1, '"The order is settled. Signed, A. Balnir, next of kin."$B$BWell. That\'s that, then.$B$BEleven years I\'ve kept this stall shut for a young man who was in the ground before I was. And I\'d have kept it shut eleven more, $n, because while the order was open I was still a shopkeeper with a customer coming, and not just a dead man standing behind a counter.$B$BHelp me with the shutters. We\'re open. Take this from stock, on the house: it\'s been waiting for someone too.');
INSERT INTO `quest_request_items` (`ID`, `EmoteOnComplete`, `EmoteOnIncomplete`, `CompletionText`) VALUES
(970600, 1, 1, 'The ledger, $n. Green binding. Under the counter. I\'d know it by the smell if I still had one.'),
(970601, 1, 1, 'Has the Magistrate said where he\'s gone? People don\'t just stop coming for their orders.'),
(970602, 1, 1, 'Well? Is there a forwarding address? Even the dead leave forwarding addresses. I left one. It\'s here.'),
(970604, 1, 1, 'You\'ve given him the letter? What did he say?');
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES (970600, 970600), (970600, 970601), (970600, 970602), (970600, 970603), (970601, 970604);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES (970600, 970600), (970600, 970601), (970600, 970602), (970601, 970603), (970600, 970604);

-- A Deathguard's Duty
INSERT INTO `creature_template` (`entry`, `name`, `subname`, `gossip_menu_id`, `minlevel`, `maxlevel`, `faction`, `npcflag`, `speed_walk`, `speed_run`, `unit_class`, `unit_flags`, `type`, `rank`, `HealthModifier`, `DamageModifier`, `mingold`, `maxgold`, `flags_extra`, `AIName`, `ScriptName`) VALUES
(970700, 'Deathguard Harlan', NULL, 0, 12, 12, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(970701, 'Deathguard Harlan', NULL, 0, 12, 12, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(970702, 'Deathguard Harlan', NULL, 0, 12, 12, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(970703, 'Maren Ashby', NULL, 0, 5, 5, 35, 1, 1, 1.14286, 1, 0, 7, 0, 1, 1, 0, 0, 2, '', ''),
(970704, 'Lise Ashby', NULL, 0, 1, 1, 35, 1, 1, 1.14286, 1, 0, 7, 0, 1, 1, 0, 0, 2, '', ''),
(970705, 'Roadside Ghoul', NULL, 0, 9, 10, 21, 0, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 0, '', ''),
(970706, 'Gnawbone', NULL, 0, 11, 11, 21, 0, 1, 1.14286, 1, 0, 6, 0, 2.5, 1.3, 120, 120, 0, '', ''),
(970707, 'Supplies delivered to Deathguard Abraham', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970708, 'Supplies delivered to Deathguard Terrence', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970709, 'Supplies delivered to Deathguard Linnea', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970710, 'Patrol brazier stoked', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970711, 'Wrecked cart searched', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970712, 'Deathguard Lawrence asked about Harlan', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970713, 'Deathguard Bartholomew asked about Harlan', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970714, 'Harlan\'s tracks followed', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970715, 'Spoke with Maren Ashby', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970716, 'Spoke with Lise Ashby', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970717, 'Firewood at the gate found', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970718, 'Deathguard Harlan\'s choice made', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', '');
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`) VALUES
(970700, 0, 2862, 1, 1),
(970701, 0, 2862, 1, 1),
(970702, 0, 2862, 1, 1),
(970703, 0, 18618, 1, 1),
(970704, 0, 252, 1, 1),
(970705, 0, 829, 1, 1),
(970706, 0, 1202, 1.25, 1),
(970707, 0, 11686, 1, 1),
(970708, 0, 11686, 1, 1),
(970709, 0, 11686, 1, 1),
(970710, 0, 11686, 1, 1),
(970711, 0, 11686, 1, 1),
(970712, 0, 11686, 1, 1),
(970713, 0, 11686, 1, 1),
(970714, 0, 11686, 1, 1),
(970715, 0, 11686, 1, 1),
(970716, 0, 11686, 1, 1),
(970717, 0, 11686, 1, 1),
(970718, 0, 11686, 1, 1);
INSERT INTO `creature` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(970700, 970700, 0, 85, 0, 1, 1, 2285.000, 1235.000, 38.670, 1.8000, 60, 0, 0, 'mod-brill-home town'),
(970701, 970701, 0, 85, 0, 1, 134217728, 2262.000, 428.000, 35.390, 0.0000, 60, 0, 0, 'mod-brill-home town'),
(970702, 970702, 0, 85, 0, 1, 268435456, 2345.000, 385.000, 34.260, 4.7100, 60, 0, 0, 'mod-brill-home town'),
(970703, 970703, 0, 85, 0, 1, 1, 2262.000, 1292.000, 31.900, 4.6000, 60, 0, 0, 'mod-brill-home town'),
(970704, 970704, 0, 85, 0, 1, 1, 2266.000, 1288.000, 31.420, 3.0000, 60, 3, 1, 'mod-brill-home town'),
(970705, 970705, 0, 85, 0, 1, 1, 2252.500, 540.000, 34.800, 1.0000, 120, 5, 1, 'mod-brill-home town'),
(970706, 970705, 0, 85, 0, 1, 1, 2272.500, 552.000, 34.320, 3.0000, 120, 5, 1, 'mod-brill-home town'),
(970707, 970705, 0, 85, 0, 1, 1, 2244.200, 560.000, 33.890, 4.5000, 120, 5, 1, 'mod-brill-home town'),
(970708, 970705, 0, 85, 0, 1, 1, 2236.000, 590.000, 33.330, 0.5000, 120, 5, 1, 'mod-brill-home town'),
(970709, 970706, 0, 85, 0, 1, 1, 2270.300, 560.000, 35.370, 3.6000, 180, 0, 0, 'mod-brill-home town');
INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `Data0`, `Data1`, `ScriptName`) VALUES
(970700, 10, 7524, 'Wrecked Cart', 1, 0, 970701, 'go_brill_town'),
(970701, 10, 498, 'Bootprints', 0.5, 0, 970702, 'go_brill_town'),
(970702, 10, 1248, 'Bundle of Firewood', 0.6, 0, 970703, 'go_brill_town');
INSERT INTO `gameobject_template_addon` (`entry`, `faction`, `flags`) VALUES (970700, 0, 4), (970701, 0, 4), (970702, 0, 4);
INSERT INTO `gameobject` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`, `animprogress`, `state`, `Comment`) VALUES
(970700, 970700, 0, 85, 0, 1, 1, 2268.000, 545.000, 33.360, 2.3000, 0, 0, 0.912764, 0.408487, 0, 255, 1, 'mod-brill-home town'),
(970701, 970700, 0, 85, 0, 1, 1, 2248.800, 566.000, 33.440, 1.6000, 0, 0, 0.717356, 0.696707, 0, 255, 1, 'mod-brill-home town'),
(970702, 970700, 0, 85, 0, 1, 1, 2254.500, 586.000, 34.060, 2.4000, 0, 0, 0.932039, 0.362358, 0, 255, 1, 'mod-brill-home town'),
(970703, 970701, 0, 85, 0, 1, 1, 2208.000, 690.000, 34.900, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(970704, 970701, 0, 85, 0, 1, 1, 2230.000, 900.000, 48.000, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(970705, 970701, 0, 85, 0, 1, 1, 2250.000, 1150.000, 34.130, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(970706, 970702, 0, 85, 0, 1, 1, 2257.000, 1287.000, 32.110, 1.0000, 0, 0, 0.479426, 0.877583, 0, 255, 1, 'mod-brill-home town');
INSERT INTO `brill_town_use` (`go`, `ord`, `cond`, `quest`, `credit`, `text_id`, `marker`, `tele_map`, `tele_x`, `tele_y`, `tele_z`, `tele_o`) VALUES
(970700, 0, 'I970701', 970701, 970711, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970701, 0, 'I970702', 970702, 970714, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970702, 0, 'I970703', 970703, 970717, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000);
INSERT INTO `brill_town_gossip` (`npc`, `ord`, `kind`, `cond`, `icon`, `text`, `text_id`, `action`, `quest`, `credit`, `marker`, `emote`, `reply`, `arg`) VALUES
(1496, 5000, 'greet', 'R970704 R970705 D2', 0, NULL, 970700, '', 0, 0, 0, 0, NULL, 0),
(1496, 5001, 'greet', 'R970704 R970706 D2', 0, NULL, 970701, '', 0, 0, 0, 0, NULL, 0),
(1496, 5002, 'greet', 'R970704 D3', 0, NULL, 970702, '', 0, 0, 0, 0, NULL, 0),
(1496, 5003, 'greet', 'A970700 F2', 0, NULL, 970703, '', 0, 0, 0, 0, NULL, 0),
(1496, 5004, 'greet', 'T970702 !R970704', 0, NULL, 970704, '', 0, 0, 0, 0, NULL, 0),
(1496, 5005, 'greet', 'R970505 !T970700', 0, NULL, 970705, '', 0, 0, 0, 0, NULL, 0),
(1496, 5006, 'option', 'F2 A970701', 0, '(Let Corn sniff the cart\'s scent from your gloves.)', 0, 'say', 0, 0, 0, 0, 'Ha. He\'s got the stink of ghoul in his nose now; he\'ll growl before you see them. Keep him close on the north road.', 0),
(1735, 5007, 'option', 'I970700', 0, 'Dillinger sent supplies for your post.', 0, 'credit', 970700, 970707, 0, 0, 'Oil! And a whetstone. (Abraham turns them over in his hands.) Thank Dillinger for me. And tell him the north road\'s been bad at night. Whoever\'s meant to be patrolling between here and Brill, isn\'t.', 0),
(1738, 5008, 'option', 'I970700', 0, 'Supplies from Dillinger, Terrence.', 0, 'credit', 970700, 970708, 0, 0, '(Terrence takes the pack without breaking stride, checks it, and grunts.)', 0),
(1495, 5009, 'option', 'I970700', 0, 'Dillinger sends whetstones and oil.', 0, 'credit', 970700, 970709, 0, 0, 'Whetstones. I have been asking for whetstones since before the Dark Lady was a lady. (She tests one with a thumb.) Tell Dillinger he\'s forgiven. Mostly.', 0),
(1743, 5010, 'option', 'I970702', 0, 'What do you know about Harlan\'s absences?', 0, 'credit', 970702, 970712, 0, 0, 'Harlan? Steady as a gravestone. Never talks about before. (Lawrence hesitates.) Only once, the night the farmers at Solliden lit a harvest fire you could see from here. He stared at it until dawn. Said nothing. Next week, he started going missing.', 0),
(1742, 5011, 'option', 'I970702', 0, 'Where does Harlan go when he leaves his post?', 0, 'credit', 970702, 970713, 0, 0, 'West. Always west, over the river. (Bartholomew lowers his voice.) He takes firewood with him. Splits it himself behind the stables. What does a dead man want with firewood, I ask you?', 0),
(970700, 5012, 'greet', 'R970705', 0, NULL, 970706, '', 0, 0, 0, 0, NULL, 0),
(970700, 5013, 'greet', 'R970706', 0, NULL, 970707, '', 0, 0, 0, 0, NULL, 0),
(970700, 5014, 'greet', 'A970703 F2', 0, NULL, 970708, '', 0, 0, 0, 0, NULL, 0),
(970700, 5015, 'greet', 'T970702', 0, NULL, 970709, '', 0, 0, 0, 0, NULL, 0),
(970700, 5016, 'greet', '', 0, NULL, 970710, '', 0, 0, 0, 0, NULL, 0),
(970700, 5017, 'option', 'I970704', 0, 'Your post is waiting, Harlan. Brill needs you on that road.', 0, 'choice', 970704, 970718, 970705, 273, 'The road it is. (Harlan squares his shoulders.) It runs this way, at least. I\'ll keep it clean for them, and once a week I\'ll come and stand in the trees. Tell Dillinger I\'ll be at my post before the bell.', 0),
(970700, 5018, 'option', 'I970704', 0, 'Ask Dillinger for another post. Let them go, Harlan.', 0, 'choice', 970704, 970718, 970706, 2, 'Let them go. (He says it as if testing the weight of it.) They let me go seven years ago. It\'s only fair. (Harlan takes a last look at the window.) Tell Dillinger I\'ll take the cemetery. The dead don\'t need firewood.', 0),
(970703, 5019, 'greet', 'R970704 R970706', 0, NULL, 970711, '', 0, 0, 0, 0, NULL, 0),
(970703, 5020, 'greet', 'R970704 R970705', 0, NULL, 970712, '', 0, 0, 0, 0, NULL, 0),
(970703, 5021, 'greet', '', 0, NULL, 970713, '', 0, 0, 0, 0, NULL, 0),
(970703, 5022, 'option', 'I970703', 0, 'I\'m only passing. You keep a fine garden.', 0, 'credit', 970703, 970715, 0, 0, '(She studies you a long moment, then lets her hand fall.) It was my husband\'s garden. He died in the plague; everyone did, nearly. Lise and I stayed. People in Brill used to be people, you know. (Her voice softens.) Someone leaves wood at the gate. Every week. I never see who. Good evening.', 0),
(970704, 5023, 'greet', '', 0, NULL, 970714, '', 0, 0, 0, 0, NULL, 0),
(970704, 5024, 'option', 'I970703', 0, '(Ask the girl her name.)', 0, 'credit', 970703, 970716, 0, 0, 'Lise. Lise Ashby. (She tilts her head.) My papa was a farmhand here. I don\'t remember him much. He used to carry me on his shoulders to see the lamps in Brill. Mama says he\'d want me to be brave. Are you brave?', 0),
(970704, 5025, 'option', 'F2 A970703', 0, '(Let her pat Corn.)', 0, 'say', 0, 0, 0, 4, '(Lise squeals and throws her arms around Corn\'s neck. He snorts and licks her ear.) We had a dog! His name was Pudding! He was bigger than this one. Well. I was smaller.', 0),
(970701, 5026, 'greet', 'D3', 0, NULL, 970715, '', 0, 0, 0, 0, NULL, 0),
(970701, 5027, 'greet', '', 0, NULL, 970716, '', 0, 0, 0, 0, NULL, 0),
(970702, 5028, 'greet', 'D3', 0, NULL, 970717, '', 0, 0, 0, 0, NULL, 0),
(970702, 5029, 'greet', '', 0, NULL, 970718, '', 0, 0, 0, 0, NULL, 0);
UPDATE `creature_template` SET `npcflag` = `npcflag` | 1 WHERE `entry` IN (1495, 1496, 1735, 1738, 1742, 1743);
INSERT INTO `brill_town_phase` (`bit`, `ord`, `cond`) VALUES
(134217728, 0, 'R970705'),
(268435456, 0, 'R970706');
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `Flags`, `RewardXPDifficulty`, `RewardMoney`, `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `AreaDescription`, `QuestCompletionLog`, `RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `ObjectiveText1`, `RequiredNpcOrGo2`, `RequiredNpcOrGoCount2`, `ObjectiveText2`, `RequiredNpcOrGo3`, `RequiredNpcOrGoCount3`, `ObjectiveText3`, `RequiredNpcOrGo4`, `RequiredNpcOrGoCount4`, `ObjectiveText4`, `RewardItem1`, `RewardAmount1`, `RewardItem2`, `RewardAmount2`, `RewardItem3`, `RewardAmount3`, `RewardItem4`, `RewardAmount4`) VALUES
(970700, 2, -1, 5, 159, 0, 4, 1800, 0, 'The Night Watch', 'Deliver supplies to Deathguard Abraham on the north road, Deathguard Terrence on the Undercity road and Deathguard Linnea at the crossroads. Then return to Deathguard Dillinger.', 'You there. You\'ve got legs and you\'re not wearing a tabard, which makes you more use to me tonight than half the watch.$B$BBrill\'s Deathguard is stretched thinner than a ghoul\'s patience. The Executor sends the best of us to the Sepulcher and the Bulwark, the Crusade takes the unlucky ones, and the ones left are standing double watches. We don\'t tire, they say. Whoever says that hasn\'t stood eighteen hours on the same road.$B$BTake these packs to our posts outside town: Abraham at the river on the north road, Terrence on the Undercity road, Linnea at the crossroads. Oil, bandages, whetstones, a few letters.', '', 'Return to Deathguard Dillinger on Brill\'s north road.', 970707, 1, 'Supplies delivered to Deathguard Abraham', 970708, 1, 'Supplies delivered to Deathguard Terrence', 970709, 1, 'Supplies delivered to Deathguard Linnea', 0, 0, '', 858, 2, 0, 0, 0, 0, 0, 0),
(970701, 2, -1, 5, 159, 0, 4, 2500, 0, 'Trouble on the Road', 'Search the 3 wrecked carts on the north road between Brill and the river, and kill 4 Roadside Ghouls and Gnawbone. Then return to Deathguard Dillinger.', 'Abraham sent word back with you, did you notice? No, of course not; you were busy being thanked.$B$BTravelers on the north road have been set upon between here and the river. A tinker from Deathknell, two apothecaries\' runners, a cart of Agamand grain. Something drags them off the road at night and leaves the carts. Scourge stragglers, by the sound of it: ghouls, and one big enough that the survivors gave it a name.$B$BThat stretch is meant to be watched. It\'s Harlan\'s patrol. (Dillinger\'s jaw tightens.) It was Harlan\'s patrol. Go and look at the carts, find out what we\'re dealing with, and put it down.', '', 'Return to Deathguard Dillinger on Brill\'s north road.', 970711, 3, 'Wrecked cart searched', 970705, 4, '', 970706, 1, '', 0, 0, '', 2455, 2, 0, 0, 0, 0, 0, 0),
(970702, 2, -1, 5, 159, 0, 4, 2000, 0, 'An Empty Post', 'Ask Deathguard Lawrence and Deathguard Bartholomew about Harlan, follow his tracks west from the river, and find Deathguard Harlan.', 'Deserting a post is a hanging matter in the Deathguard. I don\'t want to hang Harlan. He\'s a good guard; he was a good farmhand before that, by all accounts, and he never once complained about either. But the Executor will notice soon, and when he does it won\'t be my decision anymore.$B$BLawrence and Bartholomew stood watch beside him longest. Ask them what they\'ve seen. Then go and find him before anyone else does. Last time he went missing someone saw tracks heading west from the river, toward the old farms.$B$BBring him back if you can. If you can\'t, at least tell me why.', '', 'Find Deathguard Harlan.', 970712, 1, 'Deathguard Lawrence asked about Harlan', 970713, 1, 'Deathguard Bartholomew asked about Harlan', 970714, 3, 'Harlan\'s tracks followed', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(970703, 2, -1, 5, 159, 0, 4, 1500, 0, 'The House Beyond the Trees', 'Go down to the cottage at Solliden Farmstead for Deathguard Harlan: speak with Maren and Lise Ashby, and see what he has been leaving at their gate. Then return to Harlan on the hill.', 'I come here every night I can steal. I stand in these trees and I watch the lamp in the window until it goes out. I tell myself it\'s to keep the ghouls away from them. Mostly it is.$B$BI can\'t go down there. Look at me. Maren would scream, and she\'d be right to; Lise would remember me like this instead of how I was. The farmers down there would put a pitchfork through me, and I\'d let them.$B$BBut you could go. You\'re a stranger. You could pass the gate and say good evening and look at them properly, which I haven\'t done in seven years. Tell me if Lise is well. Tell me if Maren still smiles at people. And see if... see if the wood\'s still there, by the gate. I\'d like to know if they use it.', '', 'Return to Deathguard Harlan on the hill above Solliden Farmstead.', 970715, 1, 'Spoke with Maren Ashby', 970716, 1, 'Spoke with Lise Ashby', 970717, 1, 'Firewood at the gate found', 0, 0, '', 858, 1, 0, 0, 0, 0, 0, 0),
(970704, 2, -1, 5, 159, 0, 5, 3500, 0, 'Duty and Memory', 'Help Deathguard Harlan decide: return to his post on the north road, or ask for a post away from his old home. Then return to Deathguard Dillinger.', 'There are two ways this goes. I\'ve had seven years to think them through, and I still can\'t pick one on my own.$B$BI go back to my post on the north road. I stand my watch, every hour of it. It\'s the road that runs toward this place; I\'d keep the ghouls off it and off them, and on my free days... I\'d come here, and stand in the trees, and go home again before the bell. Once a week. No more.$B$BOr I ask Dillinger for a post on the other side of Brill. The cemetery, say. Facing east, my back to all this. I\'d never see the lamp in that window again. Maybe that\'s what lets a man rest.$B$BYou\'ve seen them now. You\'ve seen me. Tell me which, $n. I\'ll do it.', '', 'Return to Deathguard Dillinger on Brill\'s north road.', 970718, 1, 'Deathguard Harlan\'s choice made', 0, 0, '', 0, 0, '', 0, 0, '', 858, 3, 0, 0, 0, 0, 0, 0),
(970705, 2, 1, 1, -1, 0, 0, 0, 0, '[returned]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(970706, 2, 1, 1, -1, 0, 0, 0, 0, '[reassigned]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`, `SpecialFlags`) VALUES (970700, 0, 0), (970701, 970700, 0), (970702, 970701, 0), (970703, 970702, 0), (970704, 970703, 0);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`) VALUES
(970700, 1, 'Abraham says thank you. Terrence says nothing, which for Terrence is thank you. Linnea says she\'s been asking for whetstones since the Third War.$B$BThat\'s one night covered. Brill has a lot of nights, $n.'),
(970701, 1, 'Gnawbone. Fitting. The survivors always have a way with names.$B$BThe north road\'s clear for now. Which brings me to the thing I didn\'t want to say: that road was only open to the ghouls because there was no one on it. Harlan\'s missed four patrols this month. He comes back before the bell, says nothing, stands his post like nothing happened. Then he\'s gone again.'),
(970702, 1, '(The Deathguard on the hill doesn\'t turn when you come up behind him. He\'s looking down at the farmstead below, at a cottage with smoke rising from its chimney.)$B$BI know who sent you. Dillinger\'s a decent sort; he\'d send someone quiet before he sent a noose. Tell him I\'m not deserting. I\'m only... standing a different watch.$B$B(He nods toward the cottage.)$B$BI was a farmhand at Solliden, before. That\'s my house. My wife\'s in it. My daughter. They lived, $n. The plague came through and they lived, and I didn\'t, and then I came back. Like this.'),
(970703, 1, 'She found the wood. She thinks it\'s a neighbor.$B$B(Harlan is quiet a long time.)$B$BLise has my mother\'s chin. She was four when I died; I didn\'t know what she\'d look like. Now I do. That\'s more than most of us get, $n. More than I had any right to.$B$B(He finally looks away from the cottage.)$B$BI can\'t keep doing this. Dillinger\'s covered for me as long as he can, and the road paid for it. Something has to change.'),
(970704, 1, 'Harlan told me himself. Walked up to me and reported, as if he\'d been gone an hour.$B$B(Dillinger shakes his head slowly.)$B$BSolliden. His wife and his girl, alive, an hour\'s walk from his post, and he never said a word. Seven years. I\'ve known men go to pieces over less, $n, living or dead. He\'ll do, now. You saw to that.$B$BThe Executor will hear he was on special duty for me. That\'s not even a lie, the way I count it. Thank you. Brill\'s watch is whole again.');
INSERT INTO `quest_request_items` (`ID`, `EmoteOnComplete`, `EmoteOnIncomplete`, `CompletionText`) VALUES
(970700, 1, 1, 'Packs delivered? The night won\'t wait for you, $n, and neither will the Scourge.'),
(970701, 1, 1, 'The road, $n. Every night it stays dangerous, someone in Brill goes without bread or oil or news.'),
(970702, 1, 1, '(Deathguard Harlan does not turn around.) I know Dillinger sent you. Give me a moment.'),
(970703, 1, 1, 'Did you see them? (He keeps his eyes on the cottage.) Tell me slowly.'),
(970704, 1, 1, '(Harlan waits, his eyes on the cottage\'s lamp.)');
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES (1496, 970700), (1496, 970701), (1496, 970702), (970700, 970703), (970700, 970704);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES (1496, 970700), (1496, 970701), (970700, 970702), (970700, 970703), (1496, 970704);
UPDATE `creature_template` SET `npcflag` = `npcflag` | 3 WHERE `entry` IN (1496);

-- Something in the Water
INSERT INTO `creature_template` (`entry`, `name`, `subname`, `gossip_menu_id`, `minlevel`, `maxlevel`, `faction`, `npcflag`, `speed_walk`, `speed_run`, `unit_class`, `unit_flags`, `type`, `rank`, `HealthModifier`, `DamageModifier`, `mingold`, `maxgold`, `flags_extra`, `AIName`, `ScriptName`) VALUES
(970800, 'Maudie Fenwick', 'Laundress', 0, 10, 10, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(970801, 'Culvert Broodmother', NULL, 0, 12, 12, 14, 0, 1, 1.14286, 1, 0, 1, 0, 3.0, 1.3, 300, 300, 0, 'SmartAI', ''),
(970802, 'Broodmother Larva', NULL, 0, 8, 9, 14, 0, 1, 1.14286, 1, 0, 1, 0, 0.6, 0.6, 0, 0, 0, '', ''),
(970803, 'Water samples drawn', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970804, 'Gray bloom examined', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970805, 'The culvert under the bridge found', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970806, 'Egg sacs burst', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970807, 'The nest searched', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970808, 'Brill\'s cistern cleansed', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', '');
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`) VALUES
(970800, 0, 4004, 1, 1),
(970801, 0, 12336, 0.8, 1),
(970802, 0, 15436, 1, 1),
(970803, 0, 11686, 1, 1),
(970804, 0, 11686, 1, 1),
(970805, 0, 11686, 1, 1),
(970806, 0, 11686, 1, 1),
(970807, 0, 11686, 1, 1),
(970808, 0, 11686, 1, 1);
INSERT INTO `creature` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(970800, 970800, 0, 85, 0, 1, 1, 2292.600, 314.600, 35.500, 3.9300, 60, 0, 0, 'mod-brill-home town'),
(970801, 970801, 0, 85, 0, 1, 1, 2212.000, 634.000, 24.800, 2.4000, 90, 0, 0, 'mod-brill-home town'),
(970802, 970802, 0, 85, 0, 1, 1, 2224.000, 636.000, 24.800, 3.0000, 60, 3, 1, 'mod-brill-home town'),
(970803, 970802, 0, 85, 0, 1, 1, 2212.000, 624.000, 24.800, 1.0000, 60, 3, 1, 'mod-brill-home town'),
(970804, 970802, 0, 85, 0, 1, 1, 2205.000, 636.000, 24.800, 5.0000, 60, 3, 1, 'mod-brill-home town');
UPDATE `creature_template` SET `AIName` = 'SmartAI' WHERE `entry` IN (970801);
INSERT INTO `smart_scripts` (`entryorguid`, `source_type`, `id`, `link`, `event_type`, `event_phase_mask`, `event_chance`, `event_flags`, `event_param1`, `event_param2`, `event_param3`, `event_param4`, `event_param5`, `event_param6`, `action_type`, `action_param1`, `action_param2`, `action_param3`, `action_param4`, `action_param5`, `action_param6`, `target_type`, `target_param1`, `target_param2`, `target_param3`, `target_param4`, `target_x`, `target_y`, `target_z`, `target_o`, `comment`) VALUES
(970801, 0, 0, 0, 0, 0, 100, 0, 3000, 5000, 10000, 14000, 0, 0, 11, 744, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 'Culvert Broodmother casts 744'),
(970801, 0, 1, 0, 0, 0, 100, 0, 6000, 8000, 15000, 18000, 0, 0, 11, 3427, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 'Culvert Broodmother casts 3427');
INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `Data0`, `Data1`, `ScriptName`) VALUES
(970800, 2, 6036, 'Brill Cistern', 1.4, 0, 0, 'go_brill_town'),
(970801, 10, 239, 'Maudie\'s Old Bucket', 1, 0, 970800, 'go_brill_town'),
(970802, 10, 389, 'Gray Bloom', 1, 0, 970802, 'go_brill_town'),
(970803, 10, 134, 'Collapsed Culvert', 0.6, 0, 970802, 'go_brill_town'),
(970804, 10, 364, 'Broodmother Egg Sac', 1, 0, 970803, 'go_brill_town'),
(970805, 10, 9, 'Split Cask', 1, 0, 970804, 'go_brill_town'),
(970806, 5, 7485, 'Maudie\'s Washtubs', 1, 0, 0, ''),
(970807, 5, 7484, 'Bucket of Clean Water', 1, 0, 0, ''),
(970808, 5, 7494, 'Laundry Basket', 1, 0, 0, '');
INSERT INTO `gameobject_template_addon` (`entry`, `faction`, `flags`) VALUES (970801, 0, 4), (970802, 0, 4), (970803, 0, 4), (970804, 0, 4), (970805, 0, 4);
INSERT INTO `gameobject` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`, `animprogress`, `state`, `Comment`) VALUES
(970800, 970800, 0, 85, 0, 1, 1, 2290.000, 312.000, 35.300, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(970801, 970801, 0, 85, 0, 1, 1, 2386.000, 95.000, 21.600, 1.0000, 0, 0, 0.479426, 0.877583, 0, 255, 1, 'mod-brill-home town'),
(970802, 970801, 0, 85, 0, 1, 1, 2418.000, 103.000, 21.500, 2.0000, 0, 0, 0.841471, 0.540302, 0, 255, 1, 'mod-brill-home town'),
(970803, 970801, 0, 85, 0, 1, 1, 2436.000, 106.000, 21.900, 4.0000, 0, 0, 0.909297, -0.416147, 0, 255, 1, 'mod-brill-home town'),
(970804, 970802, 0, 85, 0, 1, 1, 2262.000, 420.000, 35.000, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(970805, 970802, 0, 85, 0, 1, 1, 2255.000, 480.000, 33.900, 1.5000, 0, 0, 0.681639, 0.731689, 0, 255, 1, 'mod-brill-home town'),
(970806, 970802, 0, 85, 0, 1, 1, 2250.000, 560.000, 33.600, 3.0000, 0, 0, 0.997495, 0.070737, 0, 255, 1, 'mod-brill-home town'),
(970807, 970803, 0, 85, 0, 1, 1, 2228.000, 640.000, 24.750, 1.6000, 0, 0, 0.717356, 0.696707, 0, 255, 1, 'mod-brill-home town'),
(970808, 970804, 0, 85, 0, 1, 1, 2208.000, 630.000, 24.750, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(970809, 970804, 0, 85, 0, 1, 1, 2216.000, 641.000, 24.750, 1.0000, 0, 0, 0.479426, 0.877583, 0, 255, 1, 'mod-brill-home town'),
(970810, 970804, 0, 85, 0, 1, 1, 2203.000, 641.000, 24.800, 2.0000, 0, 0, 0.841471, 0.540302, 0, 255, 1, 'mod-brill-home town'),
(970811, 970804, 0, 85, 0, 1, 1, 2219.000, 631.000, 24.750, 3.0000, 0, 0, 0.997495, 0.070737, 0, 255, 1, 'mod-brill-home town'),
(970812, 970804, 0, 85, 0, 1, 1, 2210.000, 638.000, 24.750, 4.0000, 0, 0, 0.909297, -0.416147, 0, 255, 1, 'mod-brill-home town'),
(970813, 970805, 0, 85, 0, 1, 1, 2210.000, 644.000, 24.750, 0.7000, 0, 0, 0.342898, 0.939373, 0, 255, 1, 'mod-brill-home town'),
(970814, 970806, 0, 85, 0, 1, 536870912, 2294.200, 312.200, 35.500, 2.0000, 0, 0, 0.841471, 0.540302, 0, 255, 1, 'mod-brill-home town'),
(970815, 970807, 0, 85, 0, 1, 536870912, 2291.800, 309.600, 35.300, 0.5000, 0, 0, 0.247404, 0.968912, 0, 255, 1, 'mod-brill-home town'),
(970816, 970808, 0, 85, 0, 1, 536870912, 2295.000, 315.600, 35.800, 4.0000, 0, 0, 0.909297, -0.416147, 0, 255, 1, 'mod-brill-home town');
INSERT INTO `brill_town_use` (`go`, `ord`, `cond`, `quest`, `credit`, `text_id`, `marker`, `tele_map`, `tele_x`, `tele_y`, `tele_z`, `tele_o`) VALUES
(970800, 0, 'I970800', 970800, 970803, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970800, 1, 'I970804', 970804, 970808, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970801, 0, 'I970800', 970800, 970803, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970802, 0, 'I970802', 970802, 970804, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970803, 0, 'I970802', 970802, 970805, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970804, 0, 'I970803', 970803, 970806, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970805, 0, 'I970804', 970804, 970807, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000);
INSERT INTO `brill_town_gossip` (`npc`, `ord`, `kind`, `cond`, `icon`, `text`, `text_id`, `action`, `quest`, `credit`, `marker`, `emote`, `reply`, `arg`) VALUES
(970800, 6000, 'greet', 'R970804 R970406', 0, NULL, 970800, '', 0, 0, 0, 0, NULL, 0),
(970800, 6001, 'greet', 'R970804 R970407', 0, NULL, 970801, '', 0, 0, 0, 0, NULL, 0),
(970800, 6002, 'greet', 'R970804 R970405', 0, NULL, 970802, '', 0, 0, 0, 0, NULL, 0),
(970800, 6003, 'greet', 'R970804', 0, NULL, 970803, '', 0, 0, 0, 0, NULL, 0),
(970800, 6004, 'greet', 'A970804', 0, NULL, 970804, '', 0, 0, 0, 0, NULL, 0),
(970800, 6005, 'greet', 'T970801 !R970804', 0, NULL, 970805, '', 0, 0, 0, 0, NULL, 0),
(970800, 6006, 'greet', '', 0, NULL, 970806, '', 0, 0, 0, 0, NULL, 0),
(10665, 6007, 'option', 'A970804 T970402', 0, 'Could that cask have been Wendell Crane\'s?', 0, 'say', 0, 0, 0, 0, 'Crane\'s? No. Batch nine is older than his apprenticeship; the Society stopped numbering batches that way the year we took Brill back. I know what\'s been said about him. Whatever else he is, he\'s careful. More careful than whoever did this.', 0),
(10665, 6008, 'greet', 'R970804 T970402', 0, NULL, 970807, '', 0, 0, 0, 0, NULL, 0),
(10665, 6009, 'greet', 'R970804', 0, NULL, 970808, '', 0, 0, 0, 0, NULL, 0),
(10665, 6010, 'greet', 'A970803', 0, NULL, 970809, '', 0, 0, 0, 0, NULL, 0),
(2132, 6011, 'option', 'R970804', 0, '(Ask her about Maudie\'s well.)', 0, 'say', 0, 0, 0, 0, 'Maudie\'s cistern is clean again. I\'ve started washing my glassware in it. I can tell the difference. I\'m not sure I like that I can tell.', 0);
UPDATE `creature_template` SET `npcflag` = `npcflag` | 1 WHERE `entry` IN (2132, 10665);
INSERT INTO `brill_town_phase` (`bit`, `ord`, `cond`) VALUES
(536870912, 0, 'R970804');
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `Flags`, `RewardXPDifficulty`, `RewardMoney`, `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `AreaDescription`, `QuestCompletionLog`, `RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `ObjectiveText1`, `RequiredNpcOrGo2`, `RequiredNpcOrGoCount2`, `ObjectiveText2`, `RequiredNpcOrGo3`, `RequiredNpcOrGoCount3`, `ObjectiveText3`, `RequiredNpcOrGo4`, `RequiredNpcOrGoCount4`, `ObjectiveText4`, `RewardItem1`, `RewardAmount1`, `RewardItem2`, `RewardAmount2`, `RewardItem3`, `RewardAmount3`, `RewardItem4`, `RewardAmount4`) VALUES
(970800, 2, -1, 5, 159, 0, 3, 1500, 0, 'Water Unfit for the Dead', 'Draw a sample from Brill\'s cistern and three from the stream north-east of town, at Maudie Fenwick\'s old buckets, then return to Maudie in Brill.', 'You\'ll want to stand back from that cistern, dear. Further. Further than that.$B$BMaudie Fenwick. I do the washing for the inn: sheets, tabards, whatever the Deathguard bleed on, and the bedding of every orc and troll who stops in Brill on the way to somewhere better. The living sweat, you know. Terribly. Somebody has to wash it out.$B$BFor a fortnight the water\'s come up stinking. Not the honest stink of a town full of corpses; I\'m used to that, I am that. This is sour and green, and it clings to the cloth. Renee\'s had complaints.$B$BFill these jars for me. One from the cistern, and three from the stream north-east of town, where I drew water before the cistern was built. My old buckets are still on the bank. If the stream\'s gone bad as well, then it isn\'t just my cistern, is it?', '', 'Return to Maudie Fenwick by the cistern in Brill.', 970803, 4, 'Water samples drawn', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(970801, 2, -1, 5, 159, 0, 2, 1000, 0, 'A Peculiar Growth', 'Bring Maudie Fenwick\'s water samples to Junior Apothecary Holland in Brill.', 'I\'m a washerwoman, not an alchemist. I know when water\'s wrong; I couldn\'t tell you why.$B$BTake the jars to Junior Apothecary Holland, at the north end of town. Not Johaan. Johaan would want to keep them. Holland\'s young, by our reckoning, and still curious, and he doesn\'t charge for curiosity.$B$BTell him Maudie sent you. He\'ll pretend he doesn\'t know who I am. He sends me his robes every week and pretends they wash themselves.', '', 'Speak with Junior Apothecary Holland in Brill.', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(970802, 2, -1, 5, 159, 0, 4, 2500, 0, 'The Source of the Rot', 'Follow the fouled runoff west of Brill: examine 3 patches of gray bloom and find where the old drainage channel runs under the covered bridge, then return to Junior Apothecary Holland.', 'Water runs downhill, and so does everything in it. Brill\'s ground water drains west, under the hill, toward the channel the Lordaeron engineers cut to keep the fields from flooding. It\'s been dry since the plague. Nobody tends the sluices now.$B$BFollow the runoff. Where the larvae are thick, the ground will show it: a gray bloom, like mold on bread, wherever the water seeps out. Find three patches, then find where it all comes from. My guess is the channel itself, where it passes under the covered bridge on the Deathknell road.$B$BDon\'t touch the bloom with bare skin. Or with skin of any kind, really.', '', 'Return to Junior Apothecary Holland in Brill.', 970804, 3, 'Gray bloom examined', 970805, 1, 'The culvert under the bridge found', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(970803, 2, -1, 5, 159, 0, 5, 4000, 0, 'A Nest Below', 'Kill the Culvert Broodmother under the covered bridge west of Brill and burst 4 of its egg sacs, then return to Junior Apothecary Holland.', 'I\'d send for the Deathguard, but Executor Zygand would want it in writing, and then he\'d want to know why the Society didn\'t notice sooner, and then I\'d be writing for a month.$B$BYou go. Get under that bridge and kill whatever is laying those eggs. Burst the sacs too, every one you find. If even a few hatch, the whole thing starts over in a season.$B$BI\'ve no idea what it will be. A broodmother of some kind. Something the plague made, or something the plague made worse. Either way, it\'s grown fat on our water, and I would like it to stop.', '', 'Return to Junior Apothecary Holland in Brill.', 970801, 1, '', 970806, 4, 'Egg sacs burst', 0, 0, '', 0, 0, '', 858, 3, 0, 0, 0, 0, 0, 0),
(970804, 2, -1, 5, 159, 0, 5, 5000, 0, 'Clear Waters, Dark Memories', 'Search the broodmother\'s nest under the covered bridge, cleanse Brill\'s cistern with Holland\'s quicklime, then speak with Maudie Fenwick in Brill.', 'A broodmother that size doesn\'t grow on runoff alone, not in a few years. Something fed it. Something rich.$B$BGo back to the nest and search it, properly, now that nothing in it is trying to eat you. If anything was dumped there, a cask, a crate, anything with a label, I want to know what was in it.$B$BAnd take this.$B$B(He hands you a heavy sack of gray powder.)$B$BQuicklime and bitterroot ash. Tip it into Brill\'s cistern; it\'ll kill whatever larvae are left and won\'t harm anyone who\'s already dead. The living may want to boil their water for a week. Then tell Maudie she can have her cistern back.', '', 'Return to Maudie Fenwick by the cistern in Brill.', 970807, 1, 'The nest searched', 970808, 1, 'Brill\'s cistern cleansed', 0, 0, '', 0, 0, '', 2459, 1, 858, 2, 0, 0, 0, 0);
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`, `SpecialFlags`) VALUES (970800, 0, 0), (970801, 970800, 0), (970802, 970801, 0), (970803, 970802, 0), (970804, 970803, 0);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`) VALUES
(970800, 1, 'Look at that. Look at it moving.$B$BI\'ve washed blood, bile and the inside of a ghoul\'s mouth out of good linen and never once felt queasy. But that... that turns what\'s left of my stomach.$B$BIt\'s in the stream too. So it isn\'t my cistern. It\'s under all of us.'),
(970801, 1, 'Maudie sent you? I don\'t know any Maudie.$B$B(Holland uncorks the first jar, sniffs, and stops pretending.)$B$BOh, that\'s lovely. Look here, under the glass. These threads aren\'t weed. They\'re larvae: a parasite, a fluke of some kind, feeding on whatever\'s dissolved in the water. On us, in a manner of speaking. The runoff from a town of the dead is very rich.$B$BThey don\'t breed in open water. Something is laying them. Somewhere close, and dark, and wet.'),
(970802, 1, 'Under the bridge. Of course. Dark and damp, and nobody\'s walked that channel in years but the Rotting Dead, and they\'re not much for reporting things.$B$BWarm, you said. And the smell of eggs.$B$B(Holland goes rather pale, which takes some doing.)$B$BThat\'s a nest, $n. And whatever\'s laying in it will be considerably larger than a thread.'),
(970803, 1, 'Dead. And the sacs. Good. Good.$B$B(He sets down a jar he has been holding very tightly.)$B$BI\'ve watched the samples all afternoon. The threads have stopped moving. Not slowly: all at once, the moment it died, as if something had been pulling every one of their strings.$B$BThere\'s still what\'s left in the water. And something about how fast it grew is bothering me.'),
(970804, 1, 'It\'s clear. Look, $n, it\'s clear! I can see the bottom of the bucket!$B$B(She draws another, just to see it again.)$B$BAnd the cask, you say. Society work. Somebody up the road poured their mistake into the ground and let it seep under all of us, and never once came to ask why the water tasted wrong.$B$BWell. I won\'t say anything. Who would I say it to? But I\'ll be washing the Society\'s robes in this water from now on, and I\'ll know. Every time.');
INSERT INTO `quest_request_items` (`ID`, `EmoteOnComplete`, `EmoteOnIncomplete`, `CompletionText`) VALUES
(970800, 1, 1, 'Four jars. And don\'t drink from any of them, whatever you are.'),
(970802, 1, 1, 'Anything? The jars on my bench have started to cloud. That\'s new.'),
(970803, 1, 1, 'Is it dead? And the eggs? Both matter. The second rather more.'),
(970804, 1, 1, 'Is it done? Can I fill my tubs?');
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES (970800, 970800), (970800, 970801), (10665, 970802), (10665, 970803), (10665, 970804);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES (970800, 970800), (10665, 970801), (10665, 970802), (10665, 970803), (970800, 970804);
UPDATE `creature_template` SET `npcflag` = `npcflag` | 3 WHERE `entry` IN (10665);

-- Beneath the Gallows
INSERT INTO `creature_template` (`entry`, `name`, `subname`, `gossip_menu_id`, `minlevel`, `maxlevel`, `faction`, `npcflag`, `speed_walk`, `speed_run`, `unit_class`, `unit_flags`, `type`, `rank`, `HealthModifier`, `DamageModifier`, `mingold`, `maxgold`, `flags_extra`, `AIName`, `ScriptName`) VALUES
(970900, 'Isolde Ashcroft', 'Deathstalker', 0, 30, 30, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(970901, 'Isolde Ashcroft', 'Deathstalker', 0, 30, 30, 68, 3, 1, 1.14286, 1, 512, 6, 0, 1, 1, 0, 0, 2, '', ''),
(970902, 'Bound Sentinel', NULL, 0, 10, 11, 14, 0, 1, 1.14286, 1, 0, 6, 0, 1.0, 1.0, 0, 0, 0, 'SmartAI', ''),
(970903, 'Aldric Croft', 'Cult of the Damned', 0, 13, 13, 14, 0, 1, 1.14286, 8, 0, 6, 0, 3.0, 1.3, 200, 200, 0, 'SmartAI', ''),
(970904, 'The Cult\'s marks found', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970905, 'Refugees\' journals recovered', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970906, 'The warded door listened at', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970907, 'Croft\'s letters read', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(970908, 'Croft\'s Roll of the Raised', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', '');
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`) VALUES
(970900, 0, 1679, 1, 1),
(970901, 0, 1679, 1, 1),
(970902, 0, 200, 1, 1),
(970902, 1, 535, 1, 1),
(970903, 0, 10427, 1, 1),
(970904, 0, 11686, 1, 1),
(970905, 0, 11686, 1, 1),
(970906, 0, 11686, 1, 1),
(970907, 0, 11686, 1, 1),
(970908, 0, 11686, 1, 1);
INSERT INTO `creature` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(970900, 970900, 0, 85, 0, 1, 1073741824, 2378.000, 335.000, 38.510, 0.1000, 60, 0, 0, 'mod-brill-home town'),
(970901, 970901, 0, 85, 0, 1, 1, 2965.000, 645.000, 100.000, 0.2700, 60, 0, 0, 'mod-brill-home town'),
(970902, 970902, 0, 85, 0, 1, 1, 3040.000, 671.500, 81.200, 0.0000, 120, 0, 0, 'mod-brill-home town'),
(970903, 970902, 0, 85, 0, 1, 1, 3047.500, 671.000, 81.100, 3.1000, 120, 0, 0, 'mod-brill-home town'),
(970904, 970902, 0, 85, 0, 1, 1, 3030.000, 655.000, 75.400, 0.0000, 120, 0, 0, 'mod-brill-home town'),
(970905, 970902, 0, 85, 0, 1, 1, 3040.000, 655.000, 75.400, 3.1000, 120, 0, 0, 'mod-brill-home town'),
(970906, 970902, 0, 85, 0, 1, 1, 3052.000, 655.500, 75.400, 3.1000, 120, 0, 0, 'mod-brill-home town'),
(970907, 970902, 0, 85, 0, 1, 1, 3028.000, 688.500, 66.400, 0.0000, 120, 0, 0, 'mod-brill-home town'),
(970908, 970902, 0, 85, 0, 1, 1, 3040.000, 689.000, 66.600, 3.1000, 120, 0, 0, 'mod-brill-home town'),
(970909, 970903, 0, 85, 0, 1, 1, 3060.500, 694.000, 66.500, 3.6000, 300, 0, 0, 'mod-brill-home town');
UPDATE `creature_template` SET `AIName` = 'SmartAI' WHERE `entry` IN (970902, 970903);
INSERT INTO `smart_scripts` (`entryorguid`, `source_type`, `id`, `link`, `event_type`, `event_phase_mask`, `event_chance`, `event_flags`, `event_param1`, `event_param2`, `event_param3`, `event_param4`, `event_param5`, `event_param6`, `action_type`, `action_param1`, `action_param2`, `action_param3`, `action_param4`, `action_param5`, `action_param6`, `target_type`, `target_param1`, `target_param2`, `target_param3`, `target_param4`, `target_x`, `target_y`, `target_z`, `target_o`, `comment`) VALUES
(970902, 0, 0, 0, 0, 0, 100, 0, 3000, 5000, 8000, 11000, 0, 0, 11, 11976, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 'Bound Sentinel casts 11976'),
(970903, 0, 0, 0, 0, 0, 100, 0, 1000, 2000, 4000, 6000, 0, 0, 11, 20791, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 'Aldric Croft casts 20791'),
(970903, 0, 1, 0, 0, 0, 100, 0, 3000, 5000, 16000, 20000, 0, 0, 11, 980, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 'Aldric Croft casts 980'),
(970903, 0, 2, 0, 0, 0, 100, 0, 9000, 12000, 20000, 25000, 0, 0, 11, 689, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 'Aldric Croft casts 689');
INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `Data0`, `Data1`, `ScriptName`) VALUES
(970900, 10, 465, 'Crowned Eye Sigil', 0.6, 0, 970900, 'go_brill_town'),
(970901, 10, 302, 'Mausoleum Foundation Stone', 0.8, 0, 970900, 'go_brill_town'),
(970902, 10, 20, 'Sunken Earth', 0.8, 0, 970900, 'go_brill_town'),
(970903, 10, 105, 'Water-Stained Journal', 1, 0, 970901, 'go_brill_town'),
(970904, 10, 447, 'Baker\'s Daybook', 1, 0, 970901, 'go_brill_town'),
(970905, 10, 184, 'Child\'s Copybook', 0.8, 0, 970901, 'go_brill_town'),
(970906, 10, 6898, 'Bone-Warded Door', 1, 0, 970903, 'go_brill_town'),
(970907, 10, 164, 'Unsent Letters', 1, 0, 970903, 'go_brill_town'),
(970908, 10, 163, 'Roll of the Raised', 1, 0, 970904, 'go_brill_town'),
(970909, 5, 4152, 'Croft\'s Black Candle, Snuffed', 1, 0, 0, '');
INSERT INTO `gameobject_template_addon` (`entry`, `faction`, `flags`) VALUES (970900, 0, 4), (970901, 0, 4), (970902, 0, 4), (970903, 0, 4), (970904, 0, 4), (970905, 0, 4), (970906, 0, 4), (970907, 0, 4), (970908, 0, 4);
INSERT INTO `gameobject` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`, `animprogress`, `state`, `Comment`) VALUES
(970900, 970900, 0, 85, 0, 1, 1073741824, 2293.500, 240.000, 27.300, 1.6000, 0, 0, 0.717356, 0.696707, 0, 255, 1, 'mod-brill-home town'),
(970901, 970901, 0, 85, 0, 1, 1073741824, 2378.000, 326.000, 38.730, 1.6000, 0, 0, 0.717356, 0.696707, 0, 255, 1, 'mod-brill-home town'),
(970902, 970902, 0, 85, 0, 1, 1073741824, 2405.000, 318.000, 38.260, 1.6000, 0, 0, 0.717356, 0.696707, 0, 255, 1, 'mod-brill-home town'),
(970903, 970903, 0, 85, 0, 1, 1, 3045.000, 674.000, 81.200, 2.0000, 0, 0, 0.841471, 0.540302, 0, 255, 1, 'mod-brill-home town'),
(970904, 970904, 0, 85, 0, 1, 1, 3035.000, 657.000, 75.400, 4.0000, 0, 0, 0.909297, -0.416147, 0, 255, 1, 'mod-brill-home town'),
(970905, 970905, 0, 85, 0, 1, 1, 3021.500, 691.000, 66.500, 5.0000, 0, 0, 0.598472, -0.801144, 0, 255, 1, 'mod-brill-home town'),
(970906, 970906, 0, 85, 0, 1, 1, 3050.000, 690.000, 66.600, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(970907, 970907, 0, 85, 0, 1, 1, 3056.000, 693.000, 66.500, 3.0000, 0, 0, 0.997495, 0.070737, 0, 255, 1, 'mod-brill-home town'),
(970908, 970908, 0, 85, 0, 1, 1, 3062.500, 697.000, 66.500, 3.6000, 0, 0, 0.973848, -0.227202, 0, 255, 1, 'mod-brill-home town'),
(970909, 970909, 0, 85, 0, 1, 2147483648, 2280.457, 480.039, 36.180, 3.4907, 0, 0, 0.984804, -0.173670, 0, 255, 1, 'mod-brill-home town');
INSERT INTO `brill_town_use` (`go`, `ord`, `cond`, `quest`, `credit`, `text_id`, `marker`, `tele_map`, `tele_x`, `tele_y`, `tele_z`, `tele_o`) VALUES
(970900, 0, 'I970900', 970900, 970904, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970901, 0, 'I970900', 970900, 970904, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970902, 0, 'I970900', 970900, 970904, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970903, 0, 'I970901', 970901, 970905, 970900, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970904, 0, 'I970901', 970901, 970905, 970901, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970905, 0, 'I970901', 970901, 970905, 970902, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970906, 0, 'I970903', 970903, 970906, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970907, 0, 'I970903', 970903, 970907, 970903, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(970908, 0, 'I970904', 970904, 970908, 970904, 0, -1, 0.000, 0.000, 0.000, 0.0000);
INSERT INTO `brill_town_gossip` (`npc`, `ord`, `kind`, `cond`, `icon`, `text`, `text_id`, `action`, `quest`, `credit`, `marker`, `emote`, `reply`, `arg`) VALUES
(970900, 7000, 'greet', 'R970904', 0, NULL, 970905, '', 0, 0, 0, 0, NULL, 0),
(970900, 7001, 'greet', 'T970901', 0, NULL, 970906, '', 0, 0, 0, 0, NULL, 0),
(970900, 7002, 'greet', '', 0, NULL, 970907, '', 0, 0, 0, 0, NULL, 0),
(970901, 7003, 'greet', 'R970904', 0, NULL, 970908, '', 0, 0, 0, 0, NULL, 0),
(970901, 7004, 'greet', 'T970901', 0, NULL, 970909, '', 0, 0, 0, 0, NULL, 0),
(970901, 7005, 'greet', '', 0, NULL, 970910, '', 0, 0, 0, 0, NULL, 0),
(970306, 7006, 'option', 'T970900 !R970904', 0, 'Isolde Ashcroft found your mark on the mausoleum stone.', 0, 'say', 0, 0, 0, 0, 'T.C. Aye. I was proud of that wall, God help me. Croft paid in good silver and said the people below would thank me. Go carefully down there, $n. I laid those bricks to keep something in.', 0);
INSERT INTO `brill_town_phase` (`bit`, `ord`, `cond`) VALUES
(1073741824, 0, 'R970203'),
(1073741824, 1, 'R970304'),
(2147483648, 0, 'R970904 O');
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `Flags`, `RewardXPDifficulty`, `RewardMoney`, `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `AreaDescription`, `QuestCompletionLog`, `RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `ObjectiveText1`, `RequiredNpcOrGo2`, `RequiredNpcOrGoCount2`, `ObjectiveText2`, `RequiredNpcOrGo3`, `RequiredNpcOrGoCount3`, `ObjectiveText3`, `RequiredNpcOrGo4`, `RequiredNpcOrGoCount4`, `ObjectiveText4`, `RewardItem1`, `RewardAmount1`, `RewardItem2`, `RewardAmount2`, `RewardItem3`, `RewardAmount3`, `RewardItem4`, `RewardAmount4`) VALUES
(970900, 2, -1, 10, 159, 0, 4, 3000, 0, 'The Sealed Passage', 'Find the Cult\'s marks beneath Brill: in the cellar under the inn, on the mausoleum\'s foundation stone and where the ground has sunk at the cemetery\'s east edge.', 'Don\'t turn round. Admire the mausoleum. It\'s very fine.$B$BEither you\'ve seen a mark on a bricked-up wall you shouldn\'t have, or a dead mason has been talking where a gravekeeper could hear. Either way you\'ve found the edge of something I\'ve been following since Stratholme, and I\'d rather have you with me than blundering about alone.$B$BBefore the plague there were tunnels under this town: old cellars and a smugglers\' way that ran north under the hills. In the plague year someone walled every way into them and marked each wall. A crowned eye. The Cult of the Damned used it on the houses they meant to come back for.$B$BFind me the marks. There\'s one in the cellar under the inn, where the Deathguard keep their prisoners; one on this mausoleum\'s foundation stone; and one where the earth has fallen in past the east wall. Tell me which way they point.', '', 'Return to Deathstalker Isolde Ashcroft by the mausoleum in Brill\'s cemetery.', 970904, 3, 'The Cult\'s marks found', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(970901, 2, -1, 10, 159, 0, 4, 3500, 0, 'Echoes of Lordaeron', 'Recover three journals left by Brill\'s plague refugees in the Agamand Family Crypt, north of Brill, then find Deathstalker Isolde Ashcroft outside the crypt.', 'The Agamand Family Crypt is north of here, past the mills. The Agamands themselves don\'t rest easy, and they won\'t thank you for visiting. Go anyway.$B$BIf Croft\'s refuge opened into their vaults, the people who sheltered there will have left something. People write, when they\'re frightened and waiting. They write to whoever might find it.$B$BBring me what they wrote. I\'ll meet you outside the crypt. I have a few things to arrange first: there are people in the Undercity who\'d rather this stayed buried, and I\'d like them busy elsewhere.', '', 'Find Deathstalker Isolde Ashcroft outside the Agamand Family Crypt.', 970905, 3, 'Refugees\' journals recovered', 0, 0, '', 0, 0, '', 0, 0, '', 858, 2, 0, 0, 0, 0, 0, 0),
(970902, 2, -1, 10, 159, 0, 5, 4000, 0, 'The Unquiet Dead', 'Destroy 6 Bound Sentinels in the Agamand Family Crypt.', 'You\'ll have seen them down there: the ones in rags, standing their posts in the dark, who don\'t moan the way the Agamands do. They don\'t make any sound at all.$B$BThose are Croft\'s refugees. Hester Lyle and her children, the baker, the boy who wrote. He raised them and bound them to guard his door, and they\'ve stood there for years without a single thought of their own. Not like us. Nothing woke in them. Nothing is going to.$B$BI\'ve been free six years and I still don\'t know how to feel about doing this. Do it anyway. Put them down, $n, gently if you can. It\'s the only kindness left to give them.', '', 'Return to Deathstalker Isolde Ashcroft outside the Agamand Family Crypt.', 970902, 6, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(970903, 2, -1, 10, 159, 0, 5, 4000, 0, 'A Master Without a Kingdom', 'Find the warded door deep in the Agamand Family Crypt and hear out whoever is behind it, and read the letters left beside it.', 'He\'s still down there. Croft. Twenty years and a war later.$B$BI could take you straight to him and we could be done. But I want to know what we\'re dealing with: whether he\'s mad, or waiting for something, or someone. A Cult necromancer who\'s sat in the dark this long has either forgotten the world or is very sure it will come back to him.$B$BGo to the bottom of the crypt. There\'ll be a door he\'s warded. Talk to it. Listen. And look about you: a man like that keeps records. He can\'t help himself.', '', 'Return to Deathstalker Isolde Ashcroft outside the Agamand Family Crypt.', 970906, 1, 'The warded door listened at', 970907, 1, 'Croft\'s letters read', 0, 0, '', 0, 0, '', 2455, 2, 0, 0, 0, 0, 0, 0),
(970904, 2, -1, 10, 159, 0, 6, 6000, 0, 'No Masters but Ourselves', 'Slay Aldric Croft in the depths of the Agamand Family Crypt and take his Roll of the Raised to Gravekeeper Mortimer Weller in Brill.', 'His ward is weaker for the sentinels being gone. It\'ll break if you put your shoulder to it, and then it\'s you and him.$B$BHe\'s a necromancer of the old Cult: shadow, curses, the slow drain. He\'s had twenty years to prepare and no one to practise on, so he\'ll be sharp in his spells and soft everywhere else. Close quickly.$B$BWhen he\'s down, find his register. Every name he raised, he\'ll have written down: it\'s how they thought, the Cult, like stewards counting sheep. Those names belong to Brill. Take them to the gravekeeper. I\'ll stay and see the crypt sealed properly this time. My way.', '', 'Bring Croft\'s Roll of the Raised to Gravekeeper Mortimer Weller in Brill\'s cemetery.', 970903, 1, '', 970908, 1, 'Croft\'s Roll of the Raised', 0, 0, '', 0, 0, '', 929, 2, 14123, 1, 0, 0, 0, 0);
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`, `SpecialFlags`) VALUES (970900, 0, 0), (970901, 970900, 0), (970902, 970901, 0), (970903, 970902, 0), (970904, 970903, 0);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`) VALUES
(970900, 1, 'North. All three of them, north, toward Agamand Mills.$B$BThe Agamands had vaults under their family crypt, deep and dry. If the tunnels ran there, the people of Brill who went below to hide from the plague went there too. And the man who walled them in knew it.$B$BHis name was Aldric Croft. Brill remembers him fondly. He paid for the well, the bell rope, the orphans\' bread. He was also a necromancer of the Cult, and he was never found.'),
(970901, 1, '(Isolde reads by the last of the light, slowly, the way you\'d read a list of the dead. Which it is.)$B$B\'Master Croft says the air below is clean.\' \'Master Croft brought bread again.\' And then, near the end, in the boy\'s hand: \'Mother says the doors are bricked. Master Croft says it is for our own good. Mother has stopped answering.\'$B$BHe didn\'t hide them from the plague, $n. He kept them for it.'),
(970902, 1, 'Thank you. I mean that, though I won\'t say it again.$B$BWith his sentinels gone the crypt is quieter. Quiet enough that I could hear something further down, while you worked. A man\'s voice, reading aloud. Very patient. Very pleased with itself.'),
(970903, 1, 'Letters to the Lich King. Years of them, and not one answer.$B$BNo, he isn\'t mad. He\'s worse. He\'s loyal. He thinks the Master\'s silence is a test, and that our freedom is a fever that will pass. He\'d put every Forsaken in Brill back in the ground and call it tidying.$B$BWe are no one\'s servants now, $n. Not his, not his master\'s. I\'d like him to understand that before the end.'),
(970904, 1, 'A Roll of the Raised. In a fine hand. He even kept the dates.$B$BThirty-one names. Lyle, Hester, and four children. Pike, the baker. Merriweather. ...I wrote some of these into my ledger as \'remains not recovered.\' I suppose I can finish the entries now.$B$B(He sets the roll beside his ledger, carefully, as if it might wake.)$B$BIsolde sent word. She\'s had something carried to your house, if you keep one here: Croft\'s black candle, snuffed. She says every home ought to have one thing in it to remind you who isn\'t master there anymore. Thank you, $n. For Brill.');
INSERT INTO `quest_request_items` (`ID`, `EmoteOnComplete`, `EmoteOnIncomplete`, `CompletionText`) VALUES
(970900, 1, 1, 'Three marks. Don\'t touch them more than you must.'),
(970901, 1, 1, 'Did they write? They always write.'),
(970902, 1, 1, 'It doesn\'t get easier. It shouldn\'t.'),
(970903, 1, 1, 'Well? Is he mad?'),
(970904, 1, 1, '(Mortimer looks at your hands, and then at your face.) You\'ve been to the bottom of it, haven\'t you?');
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES (970900, 970900), (970900, 970901), (970901, 970902), (970901, 970903), (970901, 970904);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES (970900, 970900), (970901, 970901), (970901, 970902), (970901, 970903), (970300, 970904);

-- Brill Endures
INSERT INTO `creature_template` (`entry`, `name`, `subname`, `gossip_menu_id`, `minlevel`, `maxlevel`, `faction`, `npcflag`, `speed_walk`, `speed_run`, `unit_class`, `unit_flags`, `type`, `rank`, `HealthModifier`, `DamageModifier`, `mingold`, `maxgold`, `flags_extra`, `AIName`, `ScriptName`) VALUES
(971000, 'Rudd Carver', 'Builder\'s Yard Foreman', 0, 25, 25, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971001, 'Builder\'s Yard Laborer', NULL, 0, 15, 15, 68, 0, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971002, 'Executor Zygand told', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971003, 'Jamie Nore told', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971004, 'The town bell rung', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971005, 'Builders spoken with', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', '');
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`) VALUES
(971000, 0, 1631, 1, 1),
(971001, 0, 3516, 1, 1),
(971001, 1, 1638, 1, 1),
(971001, 2, 1604, 1, 1),
(971002, 0, 11686, 1, 1),
(971003, 0, 11686, 1, 1),
(971004, 0, 11686, 1, 1),
(971005, 0, 11686, 1, 1);
INSERT INTO `creature` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(971000, 971000, 0, 85, 0, 1, 1, 2297.000, 461.000, 33.900, 3.1000, 60, 0, 0, 'mod-brill-home town'),
(971001, 971001, 0, 85, 0, 1, 1, 2301.000, 467.000, 34.500, 2.0000, 60, 4, 1, 'mod-brill-home town'),
(971002, 971001, 0, 85, 0, 1, 1, 2293.000, 455.000, 34.400, 4.5000, 60, 4, 1, 'mod-brill-home town');
INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `Data0`, `Data1`, `ScriptName`) VALUES
(971000, 10, 7548, 'Bell Rope', 1, 0, 971000, 'go_brill_town'),
(971001, 5, 1248, 'Lumber Stack', 1, 0, 0, '');
INSERT INTO `gameobject_template_addon` (`entry`, `faction`, `flags`) VALUES (971000, 0, 4);
INSERT INTO `gameobject` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`, `animprogress`, `state`, `Comment`) VALUES
(971000, 971000, 0, 85, 0, 1, 1, 2299.000, 292.500, 35.200, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(971001, 971001, 0, 85, 0, 1, 1, 2303.000, 457.000, 34.000, 0.4000, 0, 0, 0.198669, 0.980067, 0, 255, 1, 'mod-brill-home town');
INSERT INTO `brill_town_use` (`go`, `ord`, `cond`, `quest`, `credit`, `text_id`, `marker`, `tele_map`, `tele_x`, `tele_y`, `tele_z`, `tele_o`) VALUES
(971000, 0, 'I971000', 971000, 971004, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000);
INSERT INTO `brill_town_gossip` (`npc`, `ord`, `kind`, `cond`, `icon`, `text`, `text_id`, `action`, `quest`, `credit`, `marker`, `emote`, `reply`, `arg`) VALUES
(1515, 8000, 'option', 'I971000', 0, 'The Magistrate is calling the town together. He asks the Deathguard to stand in the square.', 0, 'credit', 971000, 971002, 0, 0, 'Without blades. He said that, didn\'t he. ...Very well. We\'ll stand. Mostly so we can see who doesn\'t.', 0),
(2310, 8001, 'option', 'I971000', 0, 'Magistrate Sevren is calling the town together. Bring the ledgers.', 0, 'credit', 971000, 971003, 0, 0, 'The ledgers! All of them? ...Of course all of them. Give me an hour. Some of them have to be dusted. Some of them have to be found.', 0),
(1499, 8002, 'greet', 'R971001', 0, NULL, 971000, '', 0, 0, 0, 0, NULL, 0),
(1499, 8003, 'greet', 'R971000', 0, NULL, 971001, '', 0, 0, 0, 0, NULL, 0),
(971000, 8004, 'greet', 'R971001', 0, NULL, 971002, '', 0, 0, 0, 0, NULL, 0),
(971000, 8005, 'greet', '', 0, NULL, 971003, '', 0, 0, 0, 0, NULL, 0),
(971107, 8006, 'option', 'I971001', 0, 'Magistrate Sevren asked me to walk the town. How has it been?', 0, 'credit', 971001, 971005, 971002, 0, 'I came here expecting to bury people\'s faith. Instead they come and sit, and some of them pray, and some of them just remember. Halden rings the bell every evening. Nobody asks him to.', 0),
(971207, 8007, 'option', 'I971001', 0, 'Magistrate Sevren asked me to walk the town. How has it been?', 0, 'credit', 971001, 971005, 971003, 0, 'Do you know how many letters I\'ve returned to people who\'d forgotten they ever wrote them? Thirty-one. I wrote the number down. Of course I did.', 0),
(971300, 8008, 'option', 'I971001', 0, 'Magistrate Sevren asked me to walk the town. How has it been?', 0, 'credit', 971001, 971005, 971004, 0, 'The gravebloom came back this spring without anyone planting it. That\'s how you know a garden is real, dear. It stops needing you.', 0),
(971400, 8009, 'option', 'I971001', 0, 'Magistrate Sevren asked me to walk the town. How has it been?', 0, 'credit', 971001, 971005, 971005, 0, 'Agnes walked to the caravan yard yesterday. On her own. I didn\'t watch. I absolutely did not stand in the doorway and watch.', 0),
(971501, 8010, 'option', 'I971001', 0, 'Magistrate Sevren asked me to walk the town. How has it been?', 0, 'credit', 971001, 971005, 971006, 0, 'Forty-two shipments, three lost, one recovered, none unaccounted for. Brill is on the map, $n. I have the map. I drew it.', 0),
(971601, 8011, 'option', 'I971001', 0, 'Magistrate Sevren asked me to walk the town. How has it been?', 0, 'credit', 971001, 971005, 971007, 0, 'They come in the evening now. Not for the ale. Well. Some for the ale. Mostly they come to argue about it, which is the same thing.', 0);
UPDATE `creature_template` SET `npcflag` = `npcflag` | 1 WHERE `entry` IN (1499, 1515, 2310);
INSERT INTO `brill_town_stage` (`type`, `value`, `ord`, `cond`) VALUES
(1, 1, 0, 'R971000'),
(1, 2, 0, 'R971001');
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `Flags`, `RewardXPDifficulty`, `RewardMoney`, `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `AreaDescription`, `QuestCompletionLog`, `RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `ObjectiveText1`, `RequiredNpcOrGo2`, `RequiredNpcOrGoCount2`, `ObjectiveText2`, `RequiredNpcOrGo3`, `RequiredNpcOrGoCount3`, `ObjectiveText3`, `RequiredNpcOrGo4`, `RequiredNpcOrGoCount4`, `ObjectiveText4`, `RewardItem1`, `RewardAmount1`, `RewardItem2`, `RewardAmount2`, `RewardItem3`, `RewardAmount3`, `RewardItem4`, `RewardAmount4`) VALUES
(971000, 2, -1, 5, 159, 0, 5, 5000, 0, 'Brill Endures', 'Speak with Executor Zygand and Jamie Nore, ring the town bell in the square, then return to Magistrate Sevren.', 'Sit down, $n. No, not there; that chair belonged to the last magistrate, and he hasn\'t quite left it.$B$BI keep the town\'s accounts. Not just the coin: the people. Who arrived, who stayed, who walked into the Glades one night and didn\'t come back. For years the numbers only went one way.$B$BThey\'ve turned. A carpenter putting roofs back on. A gravekeeper who knows the names. Lamps lit on the right hours. A shop open again. You\'ve had a hand in more of that than I\'d like to admit to the Undercity, who\'d want to know why a magistrate needed a stranger to do his work.$B$BI mean to call the town together. Tell Executor Zygand his Deathguard will stand in the square without their blades out, for once. Tell Jamie Nore to bring the ledgers. Then ring the bell. Brill hasn\'t heard it rung for a gathering since before the plague.', '', 'Return to Magistrate Sevren in the Brill town hall.', 971002, 1, 'Executor Zygand told', 971003, 1, 'Jamie Nore told', 971004, 1, 'The town bell rung', 0, 0, '', 929, 3, 0, 0, 0, 0, 0, 0),
(971001, 2, -1, 5, 159, 0, 6, 10000, 0, 'The Town We Made', 'Walk through Brill and speak with Mirelle Vane, Edmund Rook, Edda Graves, Elspeth Rane, Irena Sable and Oren Blackbarrel, then return to Magistrate Sevren.', 'Six. A chapel, a library, a garden, a hall for the broken, an office for the road, and a brewery, Light help us. I\'ve stopped counting the people who\'ve moved here because of them; Jamie keeps losing her place.$B$BThere\'s nothing left on the board, $n. No more projects. No more requests. That\'s not why I called you in.$B$BWalk the town. Not to fix anything. Just walk it, and speak to the people who built it with you. Then come back and tell me what you saw. I\'d go myself, but they all stop being honest when the magistrate arrives.', '', 'Return to Magistrate Sevren in the Brill town hall.', 971005, 6, 'Builders spoken with', 0, 0, '', 0, 0, '', 0, 0, '', 929, 5, 0, 0, 0, 0, 0, 0),
(971002, 2, 1, 1, -1, 0, 0, 0, 0, '[walked_chapel]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971003, 2, 1, 1, -1, 0, 0, 0, 0, '[walked_library]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971004, 2, 1, 1, -1, 0, 0, 0, 0, '[walked_garden]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971005, 2, 1, 1, -1, 0, 0, 0, 0, '[walked_surgeon]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971006, 2, 1, 1, -1, 0, 0, 0, 0, '[walked_caravan]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971007, 2, 1, 1, -1, 0, 0, 0, 0, '[walked_brewery]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`, `SpecialFlags`) VALUES (971000, 0, 0), (971001, 971000, 0);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`) VALUES
(971000, 1, '(The square fills slowly: the Deathguard, the apothecaries, the innkeeper, the farmers, the ones who only come out after dark. Sevren reads the names of what\'s been mended, one by one.)$B$BBrill endures. It has always endured; that\'s the trouble with it. Endurance is what you do when you can\'t do anything else. I\'d like it to do something else now.$B$BI\'ve put a board up outside the hall: the Town Improvement Board. A chapel by the cemetery. A library. A garden. A surgeon\'s hall. A caravan office on the Undercity road. Somebody even wants the old brewery back. Each one has someone willing to see it through. None of them can do it alone.$B$BHelp whichever you like. Help none. The board will be there either way.'),
(971001, 1, '(Sevren listens without writing anything down, which is the first time you have ever seen him not write something down.)$B$BWhen I came here, Brill was a waystation. A place the dead passed through on their way to somewhere they could pretend they were alive. Now people come here to stay.$B$BYou didn\'t do it alone, and you won\'t let me pretend you did. But you did it, $n. Whatever you were before, you\'re a citizen of Brill now. The ledger says so. I wrote it myself.');
INSERT INTO `quest_request_items` (`ID`, `EmoteOnComplete`, `EmoteOnIncomplete`, `CompletionText`) VALUES
(971000, 1, 1, 'The bell, $n. Brill won\'t come for a magistrate. It might come for a bell.'),
(971001, 1, 1, 'Have you walked it all? The garden takes longest. Edda will want to show you every bed.');
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES (1499, 971000), (1499, 971001);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES (1499, 971000), (1499, 971001);
UPDATE `creature_template` SET `npcflag` = `npcflag` | 3 WHERE `entry` IN (1499);

-- The Forgotten Shadow Chapel
INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`) VALUES (971108, 0, 17028, 0, 0, 0), (971108, 1, 17029, 0, 0, 0), (971108, 2, 44615, 0, 0, 0), (971108, 3, 17027, 0, 0, 0), (971108, 4, 17056, 0, 0, 0), (971108, 5, 1399, 0, 0, 0), (971108, 6, 37201, 0, 0, 0), (971108, 7, 17020, 0, 0, 0);
INSERT INTO `creature_template` (`entry`, `name`, `subname`, `gossip_menu_id`, `minlevel`, `maxlevel`, `faction`, `npcflag`, `speed_walk`, `speed_run`, `unit_class`, `unit_flags`, `type`, `rank`, `HealthModifier`, `DamageModifier`, `mingold`, `maxgold`, `flags_extra`, `AIName`, `ScriptName`) VALUES
(971100, 'Dark Cleric Mirelle Vane', 'Forgotten Shadow', 0, 30, 30, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971101, 'Brother Halden Wick', 'Caretaker', 0, 22, 22, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971102, 'Acolyte Corven Dusk', NULL, 0, 12, 12, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971103, 'Acolyte Corven Dusk', NULL, 0, 12, 12, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971104, 'Elsbeth Vale', NULL, 0, 14, 14, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971105, 'Builder\'s Yard Laborer', NULL, 0, 15, 15, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971106, 'Oswin Thatcher', 'Carpenter', 0, 25, 25, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971107, 'Dark Cleric Mirelle Vane', 'Forgotten Shadow', 0, 30, 30, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971108, 'Acolyte Corven Dusk', 'Candles and Reagents', 0, 12, 12, 68, 131, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971109, 'Brother Halden Wick', 'Caretaker', 0, 22, 22, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971110, 'Elsbeth Vale', NULL, 0, 14, 14, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971111, 'Mercy Hollin', NULL, 0, 12, 12, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971112, 'Edith Fairweather', 'Weaver', 0, 10, 10, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971113, 'Dark Cleric Mirelle Vane', 'Forgotten Shadow', 0, 30, 30, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971114, 'The meeting house\'s walls read', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971115, 'Collapsed debris cleared', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971116, 'Altar, roof and prayer books examined', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971117, 'Mortimer Weller asked about the building', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971118, 'Usable stone blocks', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971119, 'Lengths of sound timber', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971120, 'Lantern frames and a cart from the builder\'s yard', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971121, 'The meeting house\'s doors rehung', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971122, 'Missing register pages recovered', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971123, 'The grave in the register found', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971124, 'Elsbeth Vale spoken with', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971125, 'The register restored at the lectern', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971126, 'Places of the teachings visited', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971127, 'The Agamand family\'s relic', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971128, 'Corven\'s question answered', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971129, 'The bell and its clapper recovered', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971130, 'The bell mended at Brill\'s smithy', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971131, 'The bell hung', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971132, 'The chapel\'s opening attended', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971133, 'Lost grave records recovered', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', '');
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`) VALUES
(971100, 0, 2668, 1, 1),
(971101, 0, 2640, 1, 1),
(971102, 0, 2618, 1, 1),
(971103, 0, 2618, 1, 1),
(971104, 0, 2662, 1, 1),
(971105, 0, 3516, 1, 1),
(971105, 1, 1638, 1, 1),
(971105, 2, 1604, 1, 1),
(971106, 0, 1638, 1, 1),
(971107, 0, 2668, 1, 1),
(971108, 0, 2618, 1, 1),
(971109, 0, 2640, 1, 1),
(971110, 0, 2662, 1, 1),
(971111, 0, 2660, 1, 1),
(971112, 0, 2664, 1, 1),
(971113, 0, 2668, 1, 1),
(971114, 0, 11686, 1, 1),
(971115, 0, 11686, 1, 1),
(971116, 0, 11686, 1, 1),
(971117, 0, 11686, 1, 1),
(971118, 0, 11686, 1, 1),
(971119, 0, 11686, 1, 1),
(971120, 0, 11686, 1, 1),
(971121, 0, 11686, 1, 1),
(971122, 0, 11686, 1, 1),
(971123, 0, 11686, 1, 1),
(971124, 0, 11686, 1, 1),
(971125, 0, 11686, 1, 1),
(971126, 0, 11686, 1, 1),
(971127, 0, 11686, 1, 1),
(971128, 0, 11686, 1, 1),
(971129, 0, 11686, 1, 1),
(971130, 0, 11686, 1, 1),
(971131, 0, 11686, 1, 1),
(971132, 0, 11686, 1, 1),
(971133, 0, 11686, 1, 1);
INSERT INTO `creature` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(971100, 971100, 0, 85, 0, 1, 2, 2386.130, 393.080, 35.360, 3.6652, 60, 0, 0, 'mod-brill-home town'),
(971101, 971101, 0, 85, 0, 1, 2, 2384.250, 398.350, 35.470, 3.6652, 60, 0, 0, 'mod-brill-home town'),
(971102, 971102, 0, 85, 0, 1, 2, 2389.470, 392.700, 34.500, 3.6652, 60, 0, 0, 'mod-brill-home town'),
(971103, 971103, 0, 85, 0, 1, 2, 2160.200, 360.000, 44.600, 2.4086, 60, 0, 0, 'mod-brill-home town'),
(971104, 971104, 0, 85, 0, 1, 1, 2364.400, 386.400, 36.600, 5.5851, 60, 0, 0, 'mod-brill-home town'),
(971105, 971105, 0, 85, 0, 1, 2, 2395.260, 390.270, 33.910, 3.6652, 60, 3, 1, 'mod-brill-home town'),
(971106, 971105, 0, 85, 0, 1, 2, 2395.290, 412.230, 34.160, 3.6652, 60, 3, 1, 'mod-brill-home town'),
(971107, 971106, 0, 85, 0, 1, 2, 2394.610, 388.400, 34.010, 2.6180, 60, 0, 0, 'mod-brill-home town'),
(971108, 971107, 0, 85, 0, 1, 1, 2402.490, 407.150, 37.200, 3.6652, 60, 0, 0, 'mod-brill-home town'),
(971109, 971108, 0, 85, 0, 1, 1, 2388.010, 402.830, 37.200, 5.2360, 60, 0, 0, 'mod-brill-home town'),
(971110, 971109, 0, 85, 0, 1, 1, 2396.440, 395.230, 37.200, 5.2360, 60, 0, 0, 'mod-brill-home town'),
(971111, 971110, 0, 85, 0, 1, 1, 2402.390, 401.320, 37.200, 0.5236, 60, 0, 0, 'mod-brill-home town'),
(971112, 971111, 0, 85, 0, 1, 4194304, 2396.110, 405.200, 37.200, 0.5236, 60, 0, 0, 'mod-brill-home town'),
(971113, 971112, 0, 85, 0, 1, 4194304, 2395.110, 406.930, 37.200, 0.5236, 60, 0, 0, 'mod-brill-home town'),
(971114, 971113, 0, 85, 0, 1, 1, 2322.020, 377.350, 34.390, 0.9721, 60, 0, 0, 'mod-brill-home town');
INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `Data0`, `Data1`, `ScriptName`) VALUES
(971100, 33, 7436, 'Abandoned Meeting House', 1, 0, 0, ''),
(971101, 10, 5992, 'Scratched Names', 3.0, 0, 971100, 'go_brill_town'),
(971102, 10, 134, 'Collapsed Debris', 1.3, 0, 971100, 'go_brill_town'),
(971103, 10, 227, 'Damaged Altar', 0.8, 0, 971100, 'go_brill_town'),
(971104, 10, 1109, 'Fallen Roof Beams', 1, 0, 971100, 'go_brill_town'),
(971105, 10, 107, 'Old Prayer Books', 1, 0, 971100, 'go_brill_town'),
(971106, 10, 13, 'Splintered Doors', 1, 0, 971101, 'go_brill_town'),
(971107, 5, 1109, 'Builder\'s Lumber', 1, 0, 0, ''),
(971108, 10, 7348, 'Reading Lectern', 1, 0, 971102, 'go_brill_town'),
(971109, 5, 682, 'Bench', 1, 0, 0, ''),
(971110, 5, 3171, 'Memorial Stone', 0.9, 0, 0, ''),
(971111, 5, 4152, 'Memorial Candle', 1.5, 0, 0, ''),
(971112, 10, 4571, 'Chapel Bell', 2.5, 0, 971104, 'go_brill_town'),
(971113, 5, 1109, 'Bell Hoist', 1, 0, 0, ''),
(971114, 10, 134, 'Stone Block', 1, 0, 971101, 'go_brill_town'),
(971115, 10, 1248, 'Sound Timber', 1, 0, 971101, 'go_brill_town'),
(971116, 10, 164, 'Torn Register Page', 1, 0, 971102, 'go_brill_town'),
(971117, 10, 2453, 'Grave of Willem Vale', 1, 0, 971102, 'go_brill_town'),
(971118, 10, 4152, 'Corven\'s Candle', 1, 0, 971103, 'go_brill_town'),
(971119, 10, 4152, 'Corven\'s Candle', 1, 0, 971103, 'go_brill_town'),
(971120, 10, 4152, 'Corven\'s Candle', 1, 0, 971103, 'go_brill_town'),
(971121, 5, 1527, 'Wayside Shrine', 1, 0, 0, ''),
(971122, 10, 8, 'Agamand Nursery Chest', 1, 0, 971103, 'go_brill_town'),
(971123, 10, 4571, 'Bell Under the Hay', 2.5, 0, 971104, 'go_brill_town'),
(971124, 10, 908, 'Bell Clapper', 1.5, 0, 971104, 'go_brill_town'),
(971125, 10, 220, 'Lost Grave Record', 1, 0, 971105, 'go_brill_town'),
(971126, 33, 7449, 'Forgotten Shadow Chapel', 1, 0, 0, ''),
(971127, 5, 227, 'Altar', 1, 0, 0, ''),
(971128, 5, 4152, 'Black Candle', 1.5, 0, 0, ''),
(971129, 5, 240, 'Candelabra', 1, 0, 0, ''),
(971130, 5, 7979, 'Forsaken Banner', 1, 0, 0, ''),
(971131, 5, 673, 'Pew', 1, 0, 0, ''),
(971132, 5, 7348, 'The Book of Names', 1, 0, 0, ''),
(971133, 5, 6645, 'Memorial Wall', 0.8, 0, 0, ''),
(971134, 5, 189, 'Chapel Bookshelf', 1, 0, 0, ''),
(971135, 5, 581, 'Reading Table', 1, 0, 0, ''),
(971136, 5, 184, 'On the Forgotten Shadow', 1, 0, 0, ''),
(971137, 5, 254, 'Sermons for the Risen', 1, 0, 0, ''),
(971138, 5, 1128, 'A Book of Reflections', 1, 0, 0, ''),
(971139, 5, 7548, 'Bell Rope', 0.06, 0, 0, ''),
(971140, 5, 581, 'Devotional Table', 0.6, 0, 0, ''),
(971141, 5, 4152, 'Memorial Candle', 1.3, 0, 0, ''),
(971142, 5, 254, 'Book of Reflections', 0.6, 0, 0, ''),
(971143, 5, 7979, 'Shadow Hanging', 0.4, 0, 0, '');
INSERT INTO `gameobject_template_addon` (`entry`, `faction`, `flags`) VALUES (971100, 0, 32), (971126, 0, 32), (971101, 0, 4), (971102, 0, 4), (971103, 0, 4), (971104, 0, 4), (971105, 0, 4), (971106, 0, 4), (971108, 0, 4), (971112, 0, 4), (971114, 0, 4), (971115, 0, 4), (971116, 0, 4), (971117, 0, 4), (971118, 0, 4), (971119, 0, 4), (971120, 0, 4), (971122, 0, 4), (971123, 0, 4), (971124, 0, 4), (971125, 0, 4);
INSERT INTO `gameobject` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`, `animprogress`, `state`, `Comment`) VALUES
(971100, 971100, 0, 85, 0, 1, 2, 2395.710, 401.500, 33.850, 2.0944, 0, 0, 0.866027, 0.499998, 0, 255, 1, 'mod-brill-home town'),
(971101, 971101, 0, 85, 0, 1, 2, 2397.170, 394.960, 34.800, 2.0944, 0, 0, 0.866027, 0.499998, 0, 255, 1, 'mod-brill-home town'),
(971102, 971102, 0, 85, 0, 1, 2, 2393.480, 393.750, 33.890, 2.6180, 0, 0, 0.965927, 0.258816, 0, 255, 1, 'mod-brill-home town'),
(971103, 971102, 0, 85, 0, 1, 2, 2387.910, 403.810, 34.360, 5.5851, 0, 0, 0.341998, -0.939701, 0, 255, 1, 'mod-brill-home town'),
(971104, 971102, 0, 85, 0, 1, 2, 2400.160, 397.380, 34.040, 3.6652, 0, 0, 0.965925, -0.258823, 0, 255, 1, 'mod-brill-home town'),
(971105, 971102, 0, 85, 0, 1, 2, 2394.910, 408.080, 33.930, 1.2217, 0, 0, 0.573564, 0.819161, 0, 255, 1, 'mod-brill-home town'),
(971106, 971102, 0, 85, 0, 1, 2, 2389.740, 399.440, 34.260, 4.7124, 0, 0, 0.707103, -0.707111, 0, 255, 1, 'mod-brill-home town'),
(971107, 971102, 0, 85, 0, 1, 2, 2402.090, 404.030, 34.770, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(971108, 971103, 0, 85, 0, 1, 2, 2403.420, 401.340, 34.780, 3.6652, 0, 0, 0.965925, -0.258823, 0, 255, 1, 'mod-brill-home town'),
(971109, 971104, 0, 85, 0, 1, 2, 2394.310, 396.310, 33.890, 2.4435, 0, 0, 0.939699, 0.342002, 0, 255, 1, 'mod-brill-home town'),
(971110, 971105, 0, 85, 0, 1, 2, 2391.570, 406.270, 33.900, 3.4907, 0, 0, 0.984804, -0.173669, 0, 255, 1, 'mod-brill-home town'),
(971111, 971106, 0, 85, 0, 1, 2, 2385.600, 401.210, 36.650, 2.0944, 0, 0, 0.866027, 0.499998, 0, 255, 1, 'mod-brill-home town'),
(971112, 971107, 0, 85, 0, 1, 2, 2386.470, 387.500, 35.420, 5.2360, 0, 0, 0.499995, -0.866028, 0, 255, 1, 'mod-brill-home town'),
(971113, 971108, 0, 85, 0, 1, 2, 2388.360, 401.420, 34.420, 5.2360, 0, 0, 0.499995, -0.866028, 0, 255, 1, 'mod-brill-home town'),
(971114, 971109, 0, 85, 0, 1, 2, 2396.840, 398.340, 33.930, 0.5236, 0, 0, 0.258820, 0.965926, 0, 255, 1, 'mod-brill-home town'),
(971115, 971109, 0, 85, 0, 1, 2, 2393.540, 404.060, 33.890, 0.5236, 0, 0, 0.258820, 0.965926, 0, 255, 1, 'mod-brill-home town'),
(971116, 971109, 0, 85, 0, 1, 2, 2399.610, 399.940, 34.140, 0.5236, 0, 0, 0.258820, 0.965926, 0, 255, 1, 'mod-brill-home town'),
(971117, 971109, 0, 85, 0, 1, 2, 2396.310, 405.660, 33.980, 0.5236, 0, 0, 0.258820, 0.965926, 0, 255, 1, 'mod-brill-home town'),
(971118, 971110, 0, 85, 0, 1, 2, 2399.870, 408.290, 34.650, 3.6652, 0, 0, 0.965925, -0.258823, 0, 255, 1, 'mod-brill-home town'),
(971119, 971111, 0, 85, 0, 1, 2, 2400.050, 406.780, 34.590, 2.0944, 0, 0, 0.866027, 0.499998, 0, 255, 1, 'mod-brill-home town'),
(971120, 971111, 0, 85, 0, 1, 2, 2403.720, 400.820, 35.720, 2.0944, 0, 0, 0.866027, 0.499998, 0, 255, 1, 'mod-brill-home town'),
(971121, 971111, 0, 85, 0, 1, 2, 2403.120, 401.860, 35.720, 2.0944, 0, 0, 0.866027, 0.499998, 0, 255, 1, 'mod-brill-home town'),
(971122, 971112, 0, 85, 0, 1, 2, 2383.800, 387.120, 35.200, 3.6652, 0, 0, 0.965925, -0.258823, 0, 255, 1, 'mod-brill-home town'),
(971123, 971113, 0, 85, 0, 1, 2, 2383.930, 384.890, 35.990, 5.2360, 0, 0, 0.499995, -0.866028, 0, 255, 1, 'mod-brill-home town'),
(971124, 971114, 0, 85, 0, 1, 1, 2140.000, 648.000, 33.920, 0.3491, 0, 0, 0.173665, 0.984805, 0, 255, 1, 'mod-brill-home town'),
(971125, 971114, 0, 85, 0, 1, 1, 2138.000, 662.000, 34.040, 1.3963, 0, 0, 0.642802, 0.766033, 0, 255, 1, 'mod-brill-home town'),
(971126, 971114, 0, 85, 0, 1, 1, 2144.000, 672.000, 34.700, 2.4435, 0, 0, 0.939699, 0.342002, 0, 255, 1, 'mod-brill-home town'),
(971127, 971114, 0, 85, 0, 1, 1, 2150.000, 680.000, 34.800, 3.4907, 0, 0, 0.984804, -0.173669, 0, 255, 1, 'mod-brill-home town'),
(971128, 971114, 0, 85, 0, 1, 1, 2170.000, 678.000, 33.360, 4.5379, 0, 0, 0.766030, -0.642804, 0, 255, 1, 'mod-brill-home town'),
(971129, 971114, 0, 85, 0, 1, 1, 2178.000, 670.000, 33.390, 5.5851, 0, 0, 0.341998, -0.939701, 0, 255, 1, 'mod-brill-home town'),
(971130, 971114, 0, 85, 0, 1, 1, 2182.000, 650.000, 33.610, 0.1745, 0, 0, 0.087139, 0.996196, 0, 255, 1, 'mod-brill-home town'),
(971131, 971114, 0, 85, 0, 1, 1, 2146.000, 640.000, 34.180, 1.7453, 0, 0, 0.766035, 0.642799, 0, 255, 1, 'mod-brill-home town'),
(971132, 971115, 0, 85, 0, 1, 1, 2131.000, 683.000, 37.450, 0.5236, 0, 0, 0.258820, 0.965926, 0, 255, 1, 'mod-brill-home town'),
(971133, 971115, 0, 85, 0, 1, 1, 2127.000, 690.000, 37.980, 1.9199, 0, 0, 0.819163, 0.573561, 0, 255, 1, 'mod-brill-home town'),
(971134, 971115, 0, 85, 0, 1, 1, 2136.000, 691.000, 37.430, 3.4907, 0, 0, 0.984804, -0.173669, 0, 255, 1, 'mod-brill-home town'),
(971135, 971115, 0, 85, 0, 1, 1, 2152.000, 650.000, 33.970, 5.2360, 0, 0, 0.499995, -0.866028, 0, 255, 1, 'mod-brill-home town'),
(971136, 971115, 0, 85, 0, 1, 1, 2175.000, 663.000, 33.680, 1.0472, 0, 0, 0.500001, 0.866025, 0, 255, 1, 'mod-brill-home town'),
(971137, 971115, 0, 85, 0, 1, 1, 2165.000, 640.000, 35.210, 2.6180, 0, 0, 0.965927, 0.258816, 0, 255, 1, 'mod-brill-home town'),
(971138, 971116, 0, 85, 0, 1, 1, 2910.030, 380.970, 31.550, 0.6981, 0, 0, 0.342005, 0.939698, 0, 255, 1, 'mod-brill-home town'),
(971139, 971116, 0, 85, 0, 1, 1, 2822.000, 813.500, 113.610, 2.0944, 0, 0, 0.866027, 0.499998, 0, 255, 1, 'mod-brill-home town'),
(971140, 971116, 0, 85, 0, 1, 1, 2263.520, 1313.270, 34.050, 4.5379, 0, 0, 0.766030, -0.642804, 0, 255, 1, 'mod-brill-home town'),
(971141, 971117, 0, 85, 0, 1, 1, 2366.000, 385.000, 36.750, 2.4435, 0, 0, 0.939699, 0.342002, 0, 255, 1, 'mod-brill-home town'),
(971142, 971118, 0, 85, 0, 1, 2, 2384.000, 347.000, 38.110, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(971143, 971119, 0, 85, 0, 1, 2, 2293.000, 407.000, 33.900, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(971144, 971120, 0, 85, 0, 1, 2, 2283.000, 298.500, 35.180, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(971145, 971121, 0, 85, 0, 1, 2, 2158.000, 362.000, 44.620, 0.3491, 0, 0, 0.173665, 0.984805, 0, 255, 1, 'mod-brill-home town'),
(971146, 971122, 0, 85, 0, 1, 1, 2751.500, 793.500, 119.220, 1.0472, 0, 0, 0.500001, 0.866025, 0, 255, 1, 'mod-brill-home town'),
(971147, 971123, 0, 85, 0, 1, 1, 2840.800, 413.400, 20.050, 0.5236, 0, 0, 0.258820, 0.965926, 0, 255, 1, 'mod-brill-home town'),
(971148, 971124, 0, 85, 0, 1, 1, 2910.370, 376.900, 31.750, 1.9199, 0, 0, 0.819163, 0.573561, 0, 255, 1, 'mod-brill-home town'),
(971149, 971125, 0, 85, 0, 1, 1, 2333.000, 521.500, 28.770, 1.5708, 0, 0, 0.707108, 0.707105, 0, 255, 1, 'mod-brill-home town'),
(971150, 971125, 0, 85, 0, 1, 1, 2150.000, 668.000, 33.840, 0.5236, 0, 0, 0.258820, 0.965926, 0, 255, 1, 'mod-brill-home town'),
(971151, 971125, 0, 85, 0, 1, 1, 2921.000, 371.000, 31.350, 3.4907, 0, 0, 0.984804, -0.173669, 0, 255, 1, 'mod-brill-home town'),
(971152, 971125, 0, 85, 0, 1, 1, 2812.000, 820.000, 112.840, 5.2360, 0, 0, 0.499995, -0.866028, 0, 255, 1, 'mod-brill-home town'),
(971153, 971126, 0, 85, 0, 1, 1, 2403.500, 406.000, 35.300, 3.6652, 0, 0, 0.965925, -0.258823, 0, 255, 1, 'mod-brill-home town'),
(971154, 971127, 0, 85, 0, 1, 1, 2408.000, 408.600, 37.900, 3.6652, 0, 0, 0.965925, -0.258823, 0, 255, 1, 'mod-brill-home town'),
(971155, 971128, 0, 85, 0, 1, 1, 2408.600, 407.560, 39.050, 3.6652, 0, 0, 0.965925, -0.258823, 0, 255, 1, 'mod-brill-home town'),
(971156, 971128, 0, 85, 0, 1, 1, 2407.400, 409.640, 39.050, 3.6652, 0, 0, 0.965925, -0.258823, 0, 255, 1, 'mod-brill-home town'),
(971157, 971129, 0, 85, 0, 1, 1, 2408.290, 405.300, 37.900, 3.6652, 0, 0, 0.965925, -0.258823, 0, 255, 1, 'mod-brill-home town'),
(971158, 971129, 0, 85, 0, 1, 1, 2405.290, 410.500, 37.900, 3.6652, 0, 0, 0.965925, -0.258823, 0, 255, 1, 'mod-brill-home town'),
(971159, 971129, 0, 85, 0, 1, 1, 2397.850, 394.190, 37.200, 2.0944, 0, 0, 0.866027, 0.499998, 0, 255, 1, 'mod-brill-home town'),
(971160, 971129, 0, 85, 0, 1, 1, 2394.900, 392.490, 37.200, 2.0944, 0, 0, 0.866027, 0.499998, 0, 255, 1, 'mod-brill-home town'),
(971161, 971130, 0, 85, 0, 1, 1, 2411.620, 405.140, 37.900, 3.6652, 0, 0, 0.965925, -0.258823, 0, 255, 1, 'mod-brill-home town'),
(971162, 971130, 0, 85, 0, 1, 1, 2406.820, 413.460, 37.900, 3.6652, 0, 0, 0.965925, -0.258823, 0, 255, 1, 'mod-brill-home town'),
(971163, 971131, 0, 85, 0, 1, 1, 2403.920, 401.280, 37.200, 3.6652, 0, 0, 0.965925, -0.258823, 0, 255, 1, 'mod-brill-home town'),
(971164, 971131, 0, 85, 0, 1, 1, 2399.620, 408.720, 37.200, 3.6652, 0, 0, 0.965925, -0.258823, 0, 255, 1, 'mod-brill-home town'),
(971165, 971131, 0, 85, 0, 1, 1, 2400.890, 399.530, 37.200, 3.6652, 0, 0, 0.965925, -0.258823, 0, 255, 1, 'mod-brill-home town'),
(971166, 971131, 0, 85, 0, 1, 1, 2396.590, 406.970, 37.200, 3.6652, 0, 0, 0.965925, -0.258823, 0, 255, 1, 'mod-brill-home town'),
(971167, 971131, 0, 85, 0, 1, 1, 2397.860, 397.780, 37.200, 3.6652, 0, 0, 0.965925, -0.258823, 0, 255, 1, 'mod-brill-home town'),
(971168, 971131, 0, 85, 0, 1, 1, 2393.560, 405.220, 37.200, 3.6652, 0, 0, 0.965925, -0.258823, 0, 255, 1, 'mod-brill-home town'),
(971169, 971132, 0, 85, 0, 1, 1, 2406.120, 403.470, 37.200, 0.5236, 0, 0, 0.258820, 0.965926, 0, 255, 1, 'mod-brill-home town'),
(971170, 971133, 0, 85, 0, 1, 1, 2396.470, 393.170, 37.200, 2.0944, 0, 0, 0.866027, 0.499998, 0, 255, 1, 'mod-brill-home town'),
(971171, 971134, 0, 85, 0, 1, 1, 2389.310, 406.580, 37.200, 3.6652, 0, 0, 0.965925, -0.258823, 0, 255, 1, 'mod-brill-home town'),
(971172, 971135, 0, 85, 0, 1, 1, 2392.540, 407.990, 37.200, 3.6652, 0, 0, 0.965925, -0.258823, 0, 255, 1, 'mod-brill-home town'),
(971173, 971136, 0, 85, 0, 1, 1, 2392.900, 407.960, 38.320, 4.0143, 0, 0, 0.906299, -0.422638, 0, 255, 1, 'mod-brill-home town'),
(971174, 971137, 0, 85, 0, 1, 1, 2392.180, 408.010, 38.320, 4.8869, 0, 0, 0.642796, -0.766037, 0, 255, 1, 'mod-brill-home town'),
(971175, 971138, 0, 85, 0, 1, 1, 2392.740, 407.640, 38.320, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(971176, 971139, 0, 85, 0, 1, 1, 2386.060, 394.200, 37.800, 3.6652, 0, 0, 0.965925, -0.258823, 0, 255, 1, 'mod-brill-home town'),
(971177, 971140, 0, 85, 0, 1, 1, 2274.832, 485.494, 34.060, 5.0615, 0, 0, 0.573558, -0.819165, 0, 255, 1, 'mod-brill-home town'),
(971178, 971141, 0, 85, 0, 1, 1, 2274.592, 485.566, 34.740, 5.0615, 0, 0, 0.573558, -0.819165, 0, 255, 1, 'mod-brill-home town'),
(971179, 971142, 0, 85, 0, 1, 1, 2275.071, 485.421, 34.740, 5.0615, 0, 0, 0.573558, -0.819165, 0, 255, 1, 'mod-brill-home town'),
(971180, 971143, 0, 85, 0, 1, 1, 2274.756, 485.700, 35.660, 5.0615, 0, 0, 0.573558, -0.819165, 0, 255, 1, 'mod-brill-home town');
INSERT INTO `brill_town_use` (`go`, `ord`, `cond`, `quest`, `credit`, `text_id`, `marker`, `tele_map`, `tele_x`, `tele_y`, `tele_z`, `tele_o`) VALUES
(971101, 0, 'I971100', 971100, 971114, 971100, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971102, 0, 'I971100', 971100, 971115, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971103, 0, 'I971100', 971100, 971116, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971104, 0, 'I971100', 971100, 971116, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971105, 0, 'I971100', 971100, 971116, 971101, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971106, 0, 'I971101', 971101, 971121, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971108, 0, 'I971102', 971102, 971125, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971112, 0, 'I971104', 971104, 971131, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971114, 0, 'I971101', 971101, 971118, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971115, 0, 'I971101', 971101, 971119, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971116, 0, 'I971102', 971102, 971122, 971102, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971117, 0, 'I971102', 971102, 971123, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971118, 0, 'I971103', 971103, 971126, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971119, 0, 'I971103', 971103, 971126, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971120, 0, 'I971103', 971103, 971126, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971122, 0, 'I971103', 971103, 971127, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971123, 0, 'I971104', 971104, 971129, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971124, 0, 'I971104', 971104, 971129, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971125, 0, 'I971105', 971105, 971133, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000);
INSERT INTO `brill_town_gossip` (`npc`, `ord`, `kind`, `cond`, `icon`, `text`, `text_id`, `action`, `quest`, `credit`, `marker`, `emote`, `reply`, `arg`) VALUES
(971100, 9000, 'greet', 'R971103', 0, NULL, 971103, '', 0, 0, 0, 0, NULL, 0),
(971100, 9001, 'greet', 'R971102', 0, NULL, 971104, '', 0, 0, 0, 0, NULL, 0),
(971100, 9002, 'greet', 'R971100', 0, NULL, 971105, '', 0, 0, 0, 0, NULL, 0),
(971100, 9003, 'greet', '', 0, NULL, 971106, '', 0, 0, 0, 0, NULL, 0),
(970300, 9004, 'option', 'I971100', 0, 'What was the meeting house past the cemetery wall?', 0, 'credit', 971100, 971117, 0, 1, 'The parish meeting house. Tithes, weddings, the harvest supper. In the plague year the sick were turned away from the inns, and the healthy daren\'t go home, so they all went there and barred the door. I wrote them into my book as they were carried out. I stopped when my own hand shook too hard. Nobody wrote after me.', 0),
(971101, 9005, 'greet', 'A971104', 0, NULL, 971107, '', 0, 0, 0, 0, NULL, 0),
(971101, 9006, 'greet', 'R971101', 0, NULL, 971108, '', 0, 0, 0, 0, NULL, 0),
(971101, 9007, 'greet', '', 0, NULL, 971109, '', 0, 0, 0, 0, NULL, 0),
(971000, 9008, 'option', 'I971101', 0, 'Halden Wick needs iron lantern frames for the chapel, and a cart for stone and timber.', 0, 'credit', 971101, 971120, 0, 1, 'Wick! Four frames, he\'ll want, and he\'ll say they\'re too fancy whatever I send. Take these: plain iron, my own forging. And the cart\'s yours for the day. Tell him if he wants it back in one piece he can come and sweet-talk the axle himself.', 0),
(971104, 9009, 'option', 'I971102', 0, 'Mirelle Vane is restoring the register of those who sheltered in the meeting house.', 0, 'say', 0, 0, 971106, 1, 'I know what\'s in it. Willem Vale, ferryman. He kept the door, the five days the dead came up the road. He prayed to the Light every hour of it, out loud, so the children wouldn\'t hear the scratching. The others cut their names in the wall while he stood there. He never had a hand free. So his name isn\'t on it.', 0),
(971104, 9010, 'option', 'I971102 R971106', 0, 'Then his name belongs on that wall, with the people he kept safe. Let Halden cut it.', 0, 'choice', 971102, 971124, 971107, 18, 'On the wall. With them. ...Yes. He\'d have argued, he\'d have said it\'s a Shadow chapel now. But he\'d have been standing in front of it, and that\'s where they\'ll see him. Tell the bellringer to cut it deep.', 0),
(971104, 9011, 'option', 'I971102 R971106', 0, 'The wall should stay exactly as they left it. He\'s in the book, in the Light\'s own words; that\'s his.', 0, 'choice', 971102, 971124, 971108, 2, 'Leave it as they cut it. Yes. He wouldn\'t want his name on a Shadow chapel, however kindly they meant it. He\'s in the book, praying. That\'s where I\'ll go to read him.', 0),
(971104, 9012, 'greet', 'R971107', 0, NULL, 971110, '', 0, 0, 0, 0, NULL, 0),
(971104, 9013, 'greet', 'R971108', 0, NULL, 971111, '', 0, 0, 0, 0, NULL, 0),
(971104, 9014, 'greet', '', 0, NULL, 971112, '', 0, 0, 0, 0, NULL, 0),
(971102, 9015, 'greet', 'R971103', 0, NULL, 971113, '', 0, 0, 0, 0, NULL, 0),
(971102, 9016, 'greet', 'A971103', 0, NULL, 971114, '', 0, 0, 0, 0, NULL, 0),
(971102, 9017, 'greet', '', 0, NULL, 971115, '', 0, 0, 0, 0, NULL, 0),
(971102, 9018, 'option', 'I971103', 0, 'You asked if power means anything without a reason. Power is only worth what you protect with it.', 0, 'choice', 971103, 971128, 971109, 273, 'What you protect with it. Like Willem Vale at the door. He hadn\'t any power at all, and he used every bit of it. ...Then the Shadow\'s power is only a door that holds. I can believe in a door.', 0),
(971102, 9019, 'option', 'I971103', 0, 'Power is the freedom to choose your own reasons. Nobody hands them to you any more.', 0, 'choice', 971103, 971128, 971110, 273, 'Choose my own reasons. The Lich King chose them for us, didn\'t he. Every one. ...Then the teaching isn\'t an answer at all. It\'s permission to ask. Oh. Oh, I like that very much.', 0),
(971102, 9020, 'option', 'I971103', 0, 'Having it is the reason. The dead who had no power are the ones who were used.', 0, 'choice', 971103, 971128, 971111, 274, 'So we hold on to it so no one takes it again. That\'s... true. It\'s also what the angry ones say, in the square. I\'ll think about it, $n. I\'ll think about it for a long time.', 0),
(971103, 9021, 'greet', 'R971103', 0, NULL, 971116, '', 0, 0, 0, 0, NULL, 0),
(971103, 9022, 'greet', '', 0, NULL, 971117, '', 0, 0, 0, 0, NULL, 0),
(2136, 9023, 'option', 'I971104', 0, 'Brother Halden Wick asks if you\'ll mend the old chapel bell. It\'s cracked, and the clapper\'s rusted.', 0, 'credit', 971104, 971130, 0, 1, 'A bell? I make swords, friend. ...Give it here. Crack\'s only in the lip; I can stitch that with a bronze bead and a lot of swearing. Clapper wants a new pin. Come back in an hour and don\'t let Halden near the forge, he\'ll tell me I\'m doing it wrong.', 0),
(971100, 9024, 'option', 'I971104', 0, 'The bell\'s hung. Brill\'s ready, Cleric.', 0, 'credit', 971104, 971132, 0, 2, 'Then we begin. (Mirelle turns to the gathered town.) This is not a house of the Light, and it is not a house of the Dark Lady. It is yours. Come here for strength, or for memory, or only for somewhere quiet to sit. No one in this room will tell you what you are. Halden: the bell.', 0),
(971107, 9025, 'greet', 'R971001', 0, NULL, 971118, '', 0, 0, 0, 0, NULL, 0),
(971107, 9026, 'greet', '', 0, NULL, 971119, '', 0, 0, 0, 0, NULL, 0),
(971107, 9027, 'option', 'R971104', 0, 'What does the Forgotten Shadow actually teach?', 0, 'say', 0, 0, 0, 1, 'Respect for ourselves and our dead, because no one else will give it. Tenacity, because we endured what should have ended us. Power, so no one decides for us again. It isn\'t a creed, $n. It\'s a description of what it takes to stay yourself. Anyone who tells you to obey it hasn\'t understood it.', 0),
(971107, 9028, 'option', 'R971104 R971404', 0, 'I hear you visit the Surgeon\'s Hall in the evenings.', 0, 'say', 0, 0, 0, 1, 'Some of Rane\'s patients ask for me. Not for prayers. They want someone to sit with them who isn\'t measuring anything. Elspeth pretends to disapprove. She saves me a chair.', 0),
(971113, 9029, 'greet', '', 0, NULL, 971120, '', 0, 0, 0, 0, NULL, 0),
(971108, 9030, 'greet', 'R971109', 0, NULL, 971121, '', 0, 0, 0, 0, NULL, 0),
(971108, 9031, 'greet', 'R971110', 0, NULL, 971122, '', 0, 0, 0, 0, NULL, 0),
(971108, 9032, 'greet', 'R971111', 0, NULL, 971123, '', 0, 0, 0, 0, NULL, 0),
(971108, 9033, 'greet', '', 0, NULL, 971124, '', 0, 0, 0, 0, NULL, 0),
(971108, 9034, 'option', 'R971104', 1, 'Let me see your candles and reagents.', 0, 'vendor', 0, 0, 0, 0, NULL, 0),
(971109, 9035, 'greet', '', 0, NULL, 971125, '', 0, 0, 0, 0, NULL, 0),
(971109, 9036, 'option', 'R971104', 1, 'Have you anything for a house? A candle, perhaps, and something for the wall.', 0, 'buy', 0, 0, 971112, 2, 'A memorial candle, a little Shadow hanging the Cleric\'s acolytes stitch, and a book of reflections, blank. Seventy-five silver, which goes to the roof. I\'ll have Corven carry them over. He\'ll want to know who the candle\'s for. Don\'t tell him; it\'s good for him.', 7500),
(971109, 9037, 'option', 'R971104 R970304', 0, 'Whose names are on the wall from the cemetery?', 0, 'say', 0, 0, 0, 1, 'Hollin, Hale, Fairweather and Shaw, the ones Weller wrote twice. They asked to be put on the wall living. Mercy said she\'d rather read her own name now than have strangers read it later. Hard to argue with.', 0),
(971109, 9038, 'option', 'R971104 R970904', 0, 'Have the thirty-one from under the hill been added?', 0, 'say', 0, 0, 0, 1, 'One a week. Gideon Hale cuts the stones and I cut the wall. Thirty-one weeks, $n. I\'ve never minded a job less.', 0),
(971109, 9039, 'option', 'R971104 R970604', 0, 'Are Tobias Balnir and Marian Hale on the wall?', 0, 'say', 0, 0, 0, 1, 'Side by side. Old Wicke came and stood in front of it for an hour and didn\'t buy a thing. I\'ve never seen him not sell something for an hour.', 0),
(971110, 9040, 'greet', '', 0, NULL, 971126, '', 0, 0, 0, 0, NULL, 0),
(971111, 9041, 'greet', '', 0, NULL, 971127, '', 0, 0, 0, 0, NULL, 0),
(971112, 9042, 'greet', '', 0, NULL, 971128, '', 0, 0, 0, 0, NULL, 0),
(971105, 9043, 'greet', '', 0, NULL, 971129, '', 0, 0, 0, 0, NULL, 0),
(971106, 9044, 'greet', '', 0, NULL, 971130, '', 0, 0, 0, 0, NULL, 0);
UPDATE `creature_template` SET `npcflag` = `npcflag` | 1 WHERE `entry` IN (2136);
INSERT INTO `brill_town_phase` (`bit`, `ord`, `cond`) VALUES
(2, 0, '!R971104');
INSERT INTO `brill_town_stage` (`type`, `value`, `ord`, `cond`) VALUES
(2, 1, 0, 'R971000'),
(2, 2, 0, 'R971100'),
(2, 3, 0, 'R971101'),
(2, 4, 0, 'R971102'),
(2, 5, 0, 'R971103'),
(2, 6, 0, 'R971104'),
(2, 7, 0, 'R971112');
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `Flags`, `RewardXPDifficulty`, `RewardMoney`, `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `AreaDescription`, `QuestCompletionLog`, `RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `ObjectiveText1`, `RequiredNpcOrGo2`, `RequiredNpcOrGoCount2`, `ObjectiveText2`, `RequiredNpcOrGo3`, `RequiredNpcOrGoCount3`, `ObjectiveText3`, `RequiredNpcOrGo4`, `RequiredNpcOrGoCount4`, `ObjectiveText4`, `RewardItem1`, `RewardAmount1`, `RewardItem2`, `RewardAmount2`, `RewardItem3`, `RewardAmount3`, `RewardItem4`, `RewardAmount4`) VALUES
(971100, 2, -1, 8, 159, 0, 3, 1500, 0, 'A Place for the Unforgotten', 'Inspect the abandoned meeting house north of Brill\'s cemetery, clear its collapsed debris, examine its altar, roof and prayer books, and ask the gravekeeper Mortimer Weller about the building\'s history.', 'You\'ll have come from the Magistrate\'s board. Good. I came because of a letter from the Undercity telling me Brill had no chapel, which I didn\'t believe until I\'d walked the length of the place twice.$B$BMirelle Vane. Dark Cleric, if titles matter to you. They matter less to me than they did when I wore white and said other prayers.$B$BThere\'s a meeting house past the cemetery wall. Nobody has used it since the plague. I want it for a chapel of the Forgotten Shadow: not a cathedral, not a pulpit for shouting at the faithless. A roof, some benches, a place to sit with what you\'ve lost and decide what to do about it.$B$BLook it over with me. Clear the worst of the rubble, see what\'s left of the altar, the roof and whatever books the damp has spared, and read the walls. Then ask the gravekeeper what the building was. Mortimer Weller keeps the cemetery\'s books; if anyone remembers, he will.', '', 'Return to Dark Cleric Mirelle Vane at the meeting house north of Brill\'s cemetery.', 971114, 1, 'The meeting house\'s walls read', 971115, 6, 'Collapsed debris cleared', 971116, 3, 'Altar, roof and prayer books examined', 971117, 1, 'Mortimer Weller asked about the building', 1181, 2, 0, 0, 0, 0, 0, 0),
(971101, 2, -1, 8, 159, 0, 4, 2000, 0, 'Stone, Timber, and Shadow', 'Bring 8 usable stone blocks and 6 lengths of timber from the ruined grounds of Cold Hearth Manor, see Rudd Carver at the builder\'s yard about lantern frames and a cart, and rehang the meeting house\'s doors.', 'Halden Wick. I rang the bells at the chapel in Lordaeron\'s east ward for thirty-one years, and I\'ll tell you what I told every bishop who came through: I don\'t hold with sermons. I hold with roofs.$B$BThe Cleric wants a chapel. Fine. But I\'ve seen what the faithful do with a building: next thing it\'s marble and gilt, and nobody dares sit down. This will be stone, timber and four honest walls.$B$BCold Hearth Manor, up the road past the crossroads. The Brisboises\' garden wall came down years back and their sheds with it; the family says anyone\'s welcome to the stone who\'ll mind the dead that wander the grounds. Eight good blocks, six lengths of sound timber. Then see Rudd Carver at the builder\'s yard about iron for the lantern frames and a cart for the lot.$B$BAnd those doors. They\'re hanging by one hinge and spite.', '', 'Return to Brother Halden Wick at the meeting house north of Brill\'s cemetery.', 971118, 8, 'Usable stone blocks', 971119, 6, 'Lengths of sound timber', 971120, 1, 'Lantern frames and a cart from the builder\'s yard', 971121, 1, 'The meeting house\'s doors rehung', 858, 3, 0, 0, 0, 0, 0, 0),
(971102, 2, -1, 8, 159, 0, 4, 2500, 0, 'The Book of Names', 'Recover the register\'s three missing pages from the abandoned houses at Garren\'s Haunt, Agamand Mills and Solliden Farmstead, find the grave its last entry names in Brill\'s cemetery, speak with Elsbeth Vale, and restore the register at the meeting house\'s lectern.', 'The laborers found this under the floor where the pulpit stood: a register, bound in sailcloth against the damp. Whoever kept it wrote down everyone who came in out of the sickness, the day they came and, too often, the day they were carried out.$B$BThree pages are gone. Torn, not rotted. People took them when they left, I think: a page with their family\'s names on it, carried home like a relic. The register mentions the Garrens, the mill houses at Agamand and the Sollidens. If the pages survived, they\'re in what\'s left of those houses.$B$BThe last entry is a burial, here in Brill\'s ground. And there\'s a woman, Elsbeth Vale, who has stood at that grave every evening since I came. I haven\'t spoken to her. I suspect she\'d rather I didn\'t. She might talk to you.$B$BWhen the book is whole, we\'ll restore it at the lectern, where it belongs.', '', 'Return to Dark Cleric Mirelle Vane at the meeting house north of Brill\'s cemetery.', 971122, 3, 'Missing register pages recovered', 971123, 1, 'The grave in the register found', 971124, 1, 'Elsbeth Vale spoken with', 971125, 1, 'The register restored at the lectern', 1180, 2, 0, 0, 0, 0, 0, 0),
(971103, 2, -1, 8, 159, 0, 5, 3000, 0, 'The Weight of Faith', 'Visit the three places Corven Dusk has marked with a candle in Brill, keep the darkhounds off him at the wayside shrine on the west road, recover the Agamand family\'s relic from their house at Agamand Mills, then answer Corven\'s question at the meeting house.', 'May I ask you something? Everyone else here is very busy being dead.$B$BThe Cleric teaches three things: respect, tenacity, power. Respect for ourselves and our dead. Tenacity, because we endure what should have ended us. Power, because no one will ever again decide for us what we are. I believe all of it. I think I do. But I walk through Brill and I see people who are only angry, and I wonder whether the teachings are a door, or just a nicer name for the wall.$B$BMirelle says I should walk, and think, and take someone who argues back. I\'ve left a candle burning at three places in town that I think belong to the teachings. Stand at each. Then the old wayside shrine on the west road: it was the Light\'s once, and the darkhounds den near it now. I\'d like to pray there anyway, if you\'ll keep them off me. And the Agamands left something upstairs in their house at the mills. I\'d like to see what they thought was worth keeping.', '', 'Return to Acolyte Corven Dusk at the meeting house north of Brill\'s cemetery.', 971126, 3, 'Places of the teachings visited', 1547, 6, 'Darkhounds driven from the wayside shrine', 971127, 1, 'The Agamand family\'s relic', 971128, 1, 'Corven\'s question answered', 929, 2, 0, 0, 0, 0, 0, 0),
(971104, 2, -1, 8, 159, 0, 5, 5000, 0, 'The Bell for the Forgotten', 'Find the chapel\'s hidden bell in the barn at Garren\'s Haunt and its clapper in the farmhouse there, have the bell mended at Brill\'s smithy, hang it at the meeting house, and attend the chapel\'s opening with Dark Cleric Mirelle Vane.', 'There was a bell. There\'s still a bell, if the gnolls haven\'t sold it.$B$BIt hung over this door when the meeting house was the parish\'s. In the plague we rang it for every death, and by the second week it never stopped. People couldn\'t sleep. People couldn\'t think. So one night Garren and I took it down and carted it to his barn and buried it in the hay, and I took the clapper out myself and hid it in his kitchen chimney, so nobody would ring it in grief at three in the morning.$B$BGarren\'s Haunt, east of here. The gnolls have the farm now. Bring me the bell and the clapper; take them to Oliver Dwor at the smithy, the bell\'s cracked and he\'s the only one in Brill with the patience. Then we hang it. And then, $n, the Cleric gets her opening, and I get to hear it once more.', '', 'Return to Brother Halden Wick at the meeting house north of Brill\'s cemetery.', 971129, 2, 'The bell and its clapper recovered', 971130, 1, 'The bell mended at Brill\'s smithy', 971131, 1, 'The bell hung', 971132, 1, 'The chapel\'s opening attended', 929, 3, 0, 0, 0, 0, 0, 0),
(971105, 2, -1, 8, 159, 4096, 2, 1500, 0, 'Names to Remember', 'Recover 3 lost grave records from the graves around Tirisfal: Brill\'s north graveyard, Cold Hearth Manor, Garren\'s Haunt and Agamand Mills.', 'Every parish kept a burial book. Most of them burned, or rotted, or were used to light Scourge fires. But the sextons wrote on whatever they had when the books ran out: boards, slates, the backs of tithe receipts, nailed to the grave markers or tucked into the gravedigger\'s sheds.$B$BHalden says they turn up all the time if you know where to look: the graveyard on the north road, the family plots at Cold Hearth, at Garren\'s and at the mills. Bring me three. Each one goes on the wall or in the book, whichever its people would have wanted.', '', 'Return to Dark Cleric Mirelle Vane in the Forgotten Shadow Chapel.', 971133, 3, 'Lost grave records recovered', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971106, 2, 1, 1, -1, 0, 0, 0, 0, '[heard]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971107, 2, 1, 1, -1, 0, 0, 0, 0, '[added]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971108, 2, 1, 1, -1, 0, 0, 0, 0, '[kept]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971109, 2, 1, 1, -1, 0, 0, 0, 0, '[protect]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971110, 2, 1, 1, -1, 0, 0, 0, 0, '[choose]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971111, 2, 1, 1, -1, 0, 0, 0, 0, '[strength]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971112, 2, 1, 1, -1, 0, 0, 0, 0, '[house_set]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`, `SpecialFlags`) VALUES (971100, 0, 0), (971101, 971100, 0), (971102, 971101, 0), (971103, 971102, 0), (971104, 971103, 0), (971105, 971104, 1);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`) VALUES
(971100, 1, 'Names. Dozens of them, cut into the plaster with knives and nails and, from the look of some, fingernails.$B$BWeller\'s right, then. They sheltered here when the sickness came through, and some of them knew they wouldn\'t leave.$B$BWe keep them. Every one. If the chapel has to be built around that wall instead of in front of it, so be it. The first thing this place will be is a memory. The second can be whatever Brill makes of it.'),
(971101, 1, 'Good stone. Old Brisboise didn\'t skimp, I\'ll say that for the living.$B$BRudd\'s lads will have the walls patched and half a roof on by week\'s end. The Cleric wants the old beams kept where they can be, and so do I, for different reasons. She says memory. I say they\'re oak.$B$BHere. For your back. Mine gave out in the plague year and never came back, which is a fine joke when you\'re dead.'),
(971102, 1, 'Whole. The binder\'s thread is new, but the hand is the old one.$B$B"Willem Vale, ferryman. Came in on the ninth day with his wife\'s sister and two children not his own. Kept the door. Carried out the fourteenth day."$B$BHe kept the door. Whatever came up the road those five days, it came to him first.$B$BElsbeth told me what was decided about the wall. I won\'t argue it. It wasn\'t mine to decide, and it wasn\'t the Shadow\'s. The benches go in tomorrow.'),
(971103, 1, '(Corven turns the little sunburst over in his fingers for a long time before he speaks.)$B$BThe Agamands kept this through everything. Then they kept being Agamands, after, in the worst way. I don\'t know which of those the relic was for.$B$BThank you for answering me. Most people tell me to stop asking. Mirelle says the asking is the teaching, and that if I ever stop, she\'ll know I\'ve started obeying somebody. I\'m going to light the candles at the door tonight. Someone should, and I\'d like it to be someone who\'s still thinking.'),
(971104, 1, '(Mirelle dedicates the chapel to those seeking strength, or memory, or only a quiet place to sit. Halden doesn\'t listen. He\'s standing under the bell with the rope in both hands, and when she\'s done he pulls, once, and the note rolls out over the cemetery and the town and the dark fields beyond.)$B$BThey\'ll never hear it, of course. But perhaps that\'s not why we ring it.$B$B...Go on in, $n. Sit down. Nobody here will mind.'),
(971105, 1, '(Mirelle reads each record twice, once to herself and once aloud, and hands them to Halden for the wall.)$B$BRemembered. That\'s all we can do for them, and it\'s more than anyone did for us.$B$BCome back tomorrow, if you like. The sextons were thorough, and the rain is patient. Between them there\'s always another name.');
INSERT INTO `quest_request_items` (`ID`, `EmoteOnComplete`, `EmoteOnIncomplete`, `CompletionText`) VALUES
(971100, 1, 1, 'The meeting house won\'t clear itself, $n. I know. I\'ve stood here a week waiting for it to.'),
(971101, 1, 1, 'Stone, timber, iron, and a door that shuts. That\'s a chapel. Everything else is opinion.'),
(971102, 1, 1, 'The pages, $n. A book of names with names missing is just a list of the people we managed to keep.'),
(971103, 1, 1, 'I\'ve written my question down, so I don\'t lose it. I keep reading it. It doesn\'t get any shorter.'),
(971104, 1, 1, 'Thirty-one years I rang bells. Then I spent the next ten making sure one never rang. Funny trade.'),
(971105, 1, 1, 'Three names, $n. Small work. The kind that\'s never finished.');
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES (971100, 971100), (971101, 971101), (971100, 971102), (971102, 971103), (971101, 971104), (971107, 971105);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES (971100, 971100), (971101, 971101), (971100, 971102), (971102, 971103), (971101, 971104), (971107, 971105);

-- The Reclamation Library
INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`) VALUES (971209, 0, 39354, 0, 0, 0), (971209, 1, 10648, 0, 0, 0), (971209, 2, 39501, 0, 0, 0), (971209, 3, 39505, 0, 0, 0), (971209, 4, 39489, 0, 0, 0), (971209, 5, 3766, 0, 0, 0), (971209, 6, 3767, 0, 0, 0);
INSERT INTO `creature_template` (`entry`, `name`, `subname`, `gossip_menu_id`, `minlevel`, `maxlevel`, `faction`, `npcflag`, `speed_walk`, `speed_run`, `unit_class`, `unit_flags`, `type`, `rank`, `HealthModifier`, `DamageModifier`, `mingold`, `maxgold`, `flags_extra`, `AIName`, `ScriptName`) VALUES
(971200, 'Edmund Rook', 'Librarian', 0, 20, 20, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971201, 'Tobias Wren', 'Bookbinder', 0, 18, 18, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971202, 'Maela Quill', 'Archivist', 0, 18, 18, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971203, 'Library Patron', NULL, 0, 10, 10, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971204, 'Builder\'s Yard Laborer', NULL, 0, 15, 15, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971205, 'Oswin Thatcher', 'Carpenter', 0, 25, 25, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971206, 'Scarlet Collector', NULL, 0, 10, 11, 67, 0, 1, 1.14286, 1, 0, 7, 0, 1, 1, 45, 45, 0, '', ''),
(971207, 'Edmund Rook', 'Head Librarian', 0, 20, 20, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971208, 'Maela Quill', 'Archivist', 0, 18, 18, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971209, 'Tobias Wren', 'Bookbinder', 0, 18, 18, 68, 129, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971210, 'Nora Bell', NULL, 0, 12, 12, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971211, 'Library Patron', NULL, 0, 10, 10, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971212, 'Edmund Rook', 'Head Librarian', 0, 20, 20, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971213, 'Edmund Rook', 'Head Librarian', 0, 20, 20, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971214, 'The office and its flooded cellar inspected', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971215, 'Surviving books recovered', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971216, 'The office\'s record chest', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971217, 'Magistrate Sevren\'s permission', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971218, 'Seasoned hardwood', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971219, 'Hinges and brackets from the builder\'s yard', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971220, 'Repairable parchment from Abigail Shiel', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971221, 'Shelves assembled and the cellar window mended', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971222, 'The Undercity\'s census records', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971223, 'The Agamand mill\'s ledger', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971224, 'Residents\' memories recorded', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971225, 'The Scarlet record store searched', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971226, 'The chronicle\'s missing pages', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971227, 'The chronicle reassembled and its last entry read', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971228, 'Invitations delivered', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971229, 'The last reading table finished', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971230, 'Books sorted into their collections', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971231, 'A recovered artifact donated', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971232, 'Lost documents recovered', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', '');
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`) VALUES
(971200, 0, 2651, 1, 1),
(971201, 0, 2634, 1, 1),
(971202, 0, 2667, 1, 1),
(971203, 0, 2669, 1, 1),
(971203, 1, 2633, 1, 1),
(971204, 0, 3516, 1, 1),
(971204, 1, 1638, 1, 1),
(971204, 2, 1604, 1, 1),
(971205, 0, 1638, 1, 1),
(971206, 0, 2466, 1, 1),
(971206, 1, 2477, 1, 1),
(971207, 0, 2651, 1, 1),
(971208, 0, 2667, 1, 1),
(971209, 0, 2634, 1, 1),
(971210, 0, 2665, 1, 1),
(971211, 0, 2669, 1, 1),
(971211, 1, 2633, 1, 1),
(971212, 0, 2651, 1, 1),
(971213, 0, 2651, 1, 1),
(971214, 0, 11686, 1, 1),
(971215, 0, 11686, 1, 1),
(971216, 0, 11686, 1, 1),
(971217, 0, 11686, 1, 1),
(971218, 0, 11686, 1, 1),
(971219, 0, 11686, 1, 1),
(971220, 0, 11686, 1, 1),
(971221, 0, 11686, 1, 1),
(971222, 0, 11686, 1, 1),
(971223, 0, 11686, 1, 1),
(971224, 0, 11686, 1, 1),
(971225, 0, 11686, 1, 1),
(971226, 0, 11686, 1, 1),
(971227, 0, 11686, 1, 1),
(971228, 0, 11686, 1, 1),
(971229, 0, 11686, 1, 1),
(971230, 0, 11686, 1, 1),
(971231, 0, 11686, 1, 1),
(971232, 0, 11686, 1, 1);
INSERT INTO `creature` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(971200, 971200, 0, 85, 0, 1, 4, 2234.390, 340.600, 35.200, 5.9341, 60, 0, 0, 'mod-brill-home town'),
(971201, 971201, 0, 85, 0, 1, 4, 2237.680, 348.450, 35.200, 5.9341, 60, 0, 0, 'mod-brill-home town'),
(971202, 971202, 0, 85, 0, 1, 4, 2223.270, 345.710, 35.120, 1.2217, 60, 0, 0, 'mod-brill-home town'),
(971203, 971203, 0, 85, 0, 1, 4, 2229.430, 350.920, 35.100, 1.2217, 60, 0, 0, 'mod-brill-home town'),
(971204, 971203, 0, 85, 0, 1, 4, 2226.900, 345.450, 35.150, 5.9341, 60, 0, 0, 'mod-brill-home town'),
(971205, 971204, 0, 85, 0, 1, 4, 2232.350, 356.030, 35.430, 4.3633, 60, 3, 1, 'mod-brill-home town'),
(971206, 971204, 0, 85, 0, 1, 4, 2213.920, 344.860, 35.590, 4.3633, 60, 3, 1, 'mod-brill-home town'),
(971207, 971205, 0, 85, 0, 1, 4, 2234.770, 355.360, 35.460, 4.7124, 60, 0, 0, 'mod-brill-home town'),
(971208, 971206, 0, 85, 0, 1, 1, 2343.000, 1310.000, 34.050, 0.0349, 120, 3, 1, 'mod-brill-home town'),
(971209, 971206, 0, 85, 0, 1, 1, 2326.000, 1318.000, 34.050, 0.0873, 120, 3, 1, 'mod-brill-home town'),
(971210, 971206, 0, 85, 0, 1, 1, 2338.000, 1320.000, 34.050, 0.0698, 120, 3, 1, 'mod-brill-home town'),
(971211, 971206, 0, 85, 0, 1, 1, 2358.000, 1314.000, 33.330, 0.0541, 120, 3, 1, 'mod-brill-home town'),
(971212, 971206, 0, 85, 0, 1, 1, 2334.000, 1332.000, 33.330, 0.0279, 120, 3, 1, 'mod-brill-home town'),
(971213, 971207, 0, 85, 0, 1, 1, 2230.610, 358.580, 36.500, 4.3633, 60, 0, 0, 'mod-brill-home town'),
(971214, 971208, 0, 85, 0, 1, 1, 2220.460, 358.440, 36.500, 5.9341, 60, 0, 0, 'mod-brill-home town'),
(971215, 971209, 0, 85, 0, 1, 1, 2223.660, 342.380, 36.500, 1.2217, 60, 0, 0, 'mod-brill-home town'),
(971216, 971210, 0, 85, 0, 1, 1, 2232.500, 353.530, 36.500, 2.7925, 60, 0, 0, 'mod-brill-home town'),
(971217, 971211, 0, 85, 0, 1, 1, 2223.960, 347.590, 36.500, 4.3633, 60, 0, 0, 'mod-brill-home town'),
(971218, 971211, 0, 85, 0, 1, 1, 2226.910, 357.160, 36.500, 5.9341, 60, 0, 0, 'mod-brill-home town'),
(971219, 971212, 0, 85, 0, 1, 1, 2398.390, 408.250, 37.200, 6.8068, 60, 0, 0, 'mod-brill-home town'),
(971220, 971213, 0, 85, 0, 1, 1, 2185.500, 285.000, 42.100, 0.6196, 60, 0, 0, 'mod-brill-home town');
INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `Data0`, `Data1`, `ScriptName`) VALUES
(971200, 33, 7464, 'Old Customs Office', 1, 0, 0, ''),
(971201, 10, 7732, 'Customs Counter', 1, 0, 971200, 'go_brill_town'),
(971202, 10, 6481, 'Flooded Cellar Hatch', 1, 0, 971200, 'go_brill_town'),
(971203, 10, 1, 'Water-Stained Record Chest', 1, 0, 971200, 'go_brill_town'),
(971204, 5, 581, 'Edmund\'s Desk', 1, 0, 0, ''),
(971205, 5, 107, 'Edmund\'s Notes', 1, 0, 0, ''),
(971206, 5, 335, 'Crate of Books', 1, 0, 0, ''),
(971207, 5, 43, 'Stack of Books', 1, 0, 0, ''),
(971208, 10, 1108, 'Unassembled Shelves', 1, 0, 971201, 'go_brill_town'),
(971209, 10, 6716, 'Broken Cellar Window', 1.5, 0, 971201, 'go_brill_town'),
(971210, 5, 188, 'Bookshelf', 1, 0, 0, ''),
(971211, 10, 234, 'Edmund\'s Worktable', 1, 0, 971203, 'go_brill_town'),
(971212, 7, 39, 'Chair', 1, 1, 1, ''),
(971213, 5, 335, 'Census Boxes', 1, 0, 0, ''),
(971214, 5, 4, 'Records Cabinet', 1, 0, 0, ''),
(971215, 5, 234, 'Locked Display Case', 1, 0, 0, ''),
(971216, 10, 581, 'Unfinished Reading Table', 1, 0, 971204, 'go_brill_town'),
(971217, 10, 107, 'Unsorted Books', 1, 0, 971204, 'go_brill_town'),
(971218, 10, 1128, 'Rain-Swollen Book', 1, 0, 971200, 'go_brill_town'),
(971219, 10, 1108, 'Seasoned Deadwood', 1, 0, 971201, 'go_brill_town'),
(971220, 10, 470, 'Agamand Mill Ledger', 1, 0, 971202, 'go_brill_town'),
(971221, 10, 234, 'Scarlet Sorting Table', 1, 0, 971203, 'go_brill_town'),
(971222, 10, 164, 'Chronicle Page', 1, 0, 971203, 'go_brill_town'),
(971223, 10, 220, 'Lost Document', 1, 0, 971205, 'go_brill_town'),
(971224, 33, 7463, 'Reclamation Library', 1, 0, 0, ''),
(971225, 5, 188, 'Bookshelf', 1, 0, 0, ''),
(971226, 5, 234, 'Reading Table', 1, 0, 0, ''),
(971227, 7, 39, 'Chair', 1, 1, 1, ''),
(971228, 5, 581, 'Librarian\'s Desk', 1, 0, 0, ''),
(971229, 5, 581, 'Bindery Bench', 1, 0, 0, ''),
(971230, 5, 4, 'Records Cabinet', 1, 0, 0, ''),
(971231, 5, 335, 'Census Boxes', 1, 0, 0, ''),
(971232, 5, 234, 'The Cinderford Chronicle', 1, 0, 0, ''),
(971233, 5, 184, 'Brill: A Parish History', 1, 0, 0, ''),
(971234, 5, 254, 'A Child\'s Primer', 1, 0, 0, ''),
(971235, 5, 470, 'The Brill Register', 1, 0, 0, ''),
(971236, 5, 43, 'Library Histories', 1, 0, 0, ''),
(971237, 5, 107, 'Bound Journals', 1, 0, 0, '');
INSERT INTO `gameobject_template_addon` (`entry`, `faction`, `flags`) VALUES (971200, 0, 32), (971224, 0, 32), (971201, 0, 4), (971202, 0, 4), (971203, 0, 4), (971208, 0, 4), (971209, 0, 4), (971211, 0, 4), (971216, 0, 4), (971217, 0, 4), (971218, 0, 4), (971219, 0, 4), (971220, 0, 4), (971221, 0, 4), (971222, 0, 4), (971223, 0, 4);
INSERT INTO `gameobject` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`, `animprogress`, `state`, `Comment`) VALUES
(971200, 971200, 0, 85, 0, 1, 4, 2226.520, 348.790, 34.950, 4.3633, 0, 0, 0.819159, -0.573567, 0, 255, 1, 'mod-brill-home town'),
(971201, 971201, 0, 85, 0, 1, 4, 2227.690, 341.760, 35.190, 4.3633, 0, 0, 0.819159, -0.573567, 0, 255, 1, 'mod-brill-home town'),
(971202, 971202, 0, 85, 0, 1, 4, 2224.300, 354.380, 34.950, 4.3633, 0, 0, 0.819159, -0.573567, 0, 255, 1, 'mod-brill-home town'),
(971203, 971203, 0, 85, 0, 1, 4, 2218.530, 345.840, 35.210, 4.8869, 0, 0, 0.642796, -0.766037, 0, 255, 1, 'mod-brill-home town'),
(971204, 971204, 0, 85, 0, 1, 4, 2235.710, 340.120, 35.200, 5.9341, 0, 0, 0.173658, -0.984806, 0, 255, 1, 'mod-brill-home town'),
(971205, 971205, 0, 85, 0, 1, 4, 2235.710, 340.120, 36.320, 5.5851, 0, 0, 0.341998, -0.939701, 0, 255, 1, 'mod-brill-home town'),
(971206, 971206, 0, 85, 0, 1, 4, 2233.650, 337.680, 35.200, 4.7124, 0, 0, 0.707103, -0.707111, 0, 255, 1, 'mod-brill-home town'),
(971207, 971206, 0, 85, 0, 1, 4, 2234.850, 336.600, 35.200, 5.5851, 0, 0, 0.341998, -0.939701, 0, 255, 1, 'mod-brill-home town'),
(971208, 971207, 0, 85, 0, 1, 4, 2233.650, 337.680, 36.230, 5.0615, 0, 0, 0.573558, -0.819165, 0, 255, 1, 'mod-brill-home town'),
(971209, 971207, 0, 85, 0, 1, 4, 2234.850, 336.600, 36.230, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(971210, 971208, 0, 85, 0, 1, 4, 2234.060, 351.360, 35.150, 5.5851, 0, 0, 0.341998, -0.939701, 0, 255, 1, 'mod-brill-home town'),
(971211, 971209, 0, 85, 0, 1, 4, 2224.420, 357.640, 35.100, 5.9341, 0, 0, 0.173658, -0.984806, 0, 255, 1, 'mod-brill-home town'),
(971212, 971210, 0, 85, 0, 1, 4, 2227.770, 355.140, 35.100, 4.3633, 0, 0, 0.819159, -0.573567, 0, 255, 1, 'mod-brill-home town'),
(971213, 971210, 0, 85, 0, 1, 4, 2231.060, 353.940, 35.140, 4.3633, 0, 0, 0.819159, -0.573567, 0, 255, 1, 'mod-brill-home town'),
(971214, 971211, 0, 85, 0, 1, 4, 2224.300, 348.530, 35.030, 4.3633, 0, 0, 0.819159, -0.573567, 0, 255, 1, 'mod-brill-home town'),
(971215, 971212, 0, 85, 0, 1, 4, 2224.950, 350.320, 35.030, 4.3633, 0, 0, 0.819159, -0.573567, 0, 255, 1, 'mod-brill-home town'),
(971216, 971213, 0, 85, 0, 1, 4, 2221.720, 344.360, 35.150, 4.3633, 0, 0, 0.819159, -0.573567, 0, 255, 1, 'mod-brill-home town'),
(971217, 971213, 0, 85, 0, 1, 4, 2223.130, 343.850, 35.150, 4.8869, 0, 0, 0.642796, -0.766037, 0, 255, 1, 'mod-brill-home town'),
(971218, 971214, 0, 85, 0, 1, 4, 2224.540, 342.480, 35.150, 1.2217, 0, 0, 0.573564, 0.819161, 0, 255, 1, 'mod-brill-home town'),
(971219, 971215, 0, 85, 0, 1, 4, 2221.910, 353.660, 34.990, 5.9341, 0, 0, 0.173658, -0.984806, 0, 255, 1, 'mod-brill-home town'),
(971220, 971216, 0, 85, 0, 1, 4, 2231.260, 348.660, 35.170, 4.8869, 0, 0, 0.642796, -0.766037, 0, 255, 1, 'mod-brill-home town'),
(971221, 971217, 0, 85, 0, 1, 4, 2226.050, 354.810, 35.010, 4.7124, 0, 0, 0.707103, -0.707111, 0, 255, 1, 'mod-brill-home town'),
(971222, 971217, 0, 85, 0, 1, 4, 2232.350, 352.520, 35.180, 5.7596, 0, 0, 0.258813, -0.965928, 0, 255, 1, 'mod-brill-home town'),
(971223, 971217, 0, 85, 0, 1, 4, 2220.450, 346.740, 35.110, 0.5236, 0, 0, 0.258820, 0.965926, 0, 255, 1, 'mod-brill-home town'),
(971224, 971217, 0, 85, 0, 1, 4, 2230.830, 344.560, 35.190, 1.5708, 0, 0, 0.707108, 0.707105, 0, 255, 1, 'mod-brill-home town'),
(971225, 971217, 0, 85, 0, 1, 4, 2221.100, 352.890, 35.010, 2.6180, 0, 0, 0.965927, 0.258816, 0, 255, 1, 'mod-brill-home town'),
(971226, 971217, 0, 85, 0, 1, 4, 2230.230, 340.840, 35.190, 3.6652, 0, 0, 0.965925, -0.258823, 0, 255, 1, 'mod-brill-home town'),
(971227, 971218, 0, 85, 0, 1, 1, 2915.250, 382.590, 31.550, 0.5236, 0, 0, 0.258820, 0.965926, 0, 255, 1, 'mod-brill-home town'),
(971228, 971218, 0, 85, 0, 1, 1, 2915.380, 376.730, 31.550, 2.6180, 0, 0, 0.965927, 0.258816, 0, 255, 1, 'mod-brill-home town'),
(971229, 971218, 0, 85, 0, 1, 1, 2841.600, 418.400, 20.850, 4.5379, 0, 0, 0.766030, -0.642804, 0, 255, 1, 'mod-brill-home town'),
(971230, 971218, 0, 85, 0, 1, 1, 2846.500, 413.200, 20.850, 1.3963, 0, 0, 0.642802, 0.766033, 0, 255, 1, 'mod-brill-home town'),
(971231, 971218, 0, 85, 0, 1, 1, 2906.500, 373.000, 30.630, 3.4907, 0, 0, 0.984804, -0.173669, 0, 255, 1, 'mod-brill-home town'),
(971232, 971219, 0, 85, 0, 1, 1, 2112.000, 352.000, 48.090, 0.5236, 0, 0, 0.258820, 0.965926, 0, 255, 1, 'mod-brill-home town'),
(971233, 971219, 0, 85, 0, 1, 1, 2104.000, 371.000, 45.030, 1.9199, 0, 0, 0.819163, 0.573561, 0, 255, 1, 'mod-brill-home town'),
(971234, 971219, 0, 85, 0, 1, 1, 2118.000, 389.000, 49.930, 3.4907, 0, 0, 0.984804, -0.173669, 0, 255, 1, 'mod-brill-home town'),
(971235, 971219, 0, 85, 0, 1, 1, 2098.000, 402.000, 54.590, 5.0615, 0, 0, 0.573558, -0.819165, 0, 255, 1, 'mod-brill-home town'),
(971236, 971219, 0, 85, 0, 1, 1, 2109.000, 418.000, 57.990, 0.3491, 0, 0, 0.173665, 0.984805, 0, 255, 1, 'mod-brill-home town'),
(971237, 971219, 0, 85, 0, 1, 1, 2124.000, 432.000, 64.930, 1.7453, 0, 0, 0.766035, 0.642799, 0, 255, 1, 'mod-brill-home town'),
(971238, 971219, 0, 85, 0, 1, 1, 2092.000, 380.000, 45.510, 3.3161, 0, 0, 0.996196, -0.087143, 0, 255, 1, 'mod-brill-home town'),
(971239, 971219, 0, 85, 0, 1, 1, 2130.000, 410.000, 60.730, 4.8869, 0, 0, 0.642796, -0.766037, 0, 255, 1, 'mod-brill-home town'),
(971240, 971220, 0, 85, 0, 1, 1, 2827.500, 810.500, 113.610, 2.4435, 0, 0, 0.939699, 0.342002, 0, 255, 1, 'mod-brill-home town'),
(971241, 971221, 0, 85, 0, 1, 1, 2336.000, 1312.000, 34.050, 3.1416, 0, 0, 1.000000, -0.000004, 0, 255, 1, 'mod-brill-home town'),
(971242, 971222, 0, 85, 0, 1, 1, 2331.500, 1311.000, 34.050, 0.6981, 0, 0, 0.342005, 0.939698, 0, 255, 1, 'mod-brill-home town'),
(971243, 971222, 0, 85, 0, 1, 1, 2338.500, 1316.500, 34.050, 2.2689, 0, 0, 0.906302, 0.422631, 0, 255, 1, 'mod-brill-home town'),
(971244, 971222, 0, 85, 0, 1, 1, 2333.000, 1318.500, 34.050, 4.5379, 0, 0, 0.766030, -0.642804, 0, 255, 1, 'mod-brill-home town'),
(971245, 971223, 0, 85, 0, 1, 1, 2846.000, 419.000, 20.850, 0.5236, 0, 0, 0.258820, 0.965926, 0, 255, 1, 'mod-brill-home town'),
(971246, 971223, 0, 85, 0, 1, 1, 2821.000, 809.500, 113.610, 2.0944, 0, 0, 0.866027, 0.499998, 0, 255, 1, 'mod-brill-home town'),
(971247, 971223, 0, 85, 0, 1, 1, 2262.970, 1319.080, 34.050, 3.6652, 0, 0, 0.965925, -0.258823, 0, 255, 1, 'mod-brill-home town'),
(971248, 971223, 0, 85, 0, 1, 1, 2131.500, 684.500, 37.670, 5.2360, 0, 0, 0.499995, -0.866028, 0, 255, 1, 'mod-brill-home town'),
(971249, 971224, 0, 85, 0, 1, 1, 2223.400, 344.600, 37.000, 1.2217, 0, 0, 0.573564, 0.819161, 0, 255, 1, 'mod-brill-home town'),
(971250, 971225, 0, 85, 0, 1, 1, 2226.610, 338.220, 36.500, 1.2217, 0, 0, 0.573564, 0.819161, 0, 255, 1, 'mod-brill-home town'),
(971251, 971225, 0, 85, 0, 1, 1, 2223.600, 339.310, 36.500, 1.2217, 0, 0, 0.573564, 0.819161, 0, 255, 1, 'mod-brill-home town'),
(971252, 971225, 0, 85, 0, 1, 1, 2220.600, 340.410, 36.500, 1.2217, 0, 0, 0.573564, 0.819161, 0, 255, 1, 'mod-brill-home town'),
(971253, 971225, 0, 85, 0, 1, 1, 2219.260, 343.760, 36.500, 5.9341, 0, 0, 0.173658, -0.984806, 0, 255, 1, 'mod-brill-home town'),
(971254, 971225, 0, 85, 0, 1, 1, 2220.360, 346.770, 36.500, 5.9341, 0, 0, 0.173658, -0.984806, 0, 255, 1, 'mod-brill-home town'),
(971255, 971225, 0, 85, 0, 1, 1, 2233.310, 358.660, 36.500, 4.3633, 0, 0, 0.819159, -0.573567, 0, 255, 1, 'mod-brill-home town'),
(971256, 971225, 0, 85, 0, 1, 1, 2227.290, 360.850, 36.500, 4.3633, 0, 0, 0.819159, -0.573567, 0, 255, 1, 'mod-brill-home town'),
(971257, 971225, 0, 85, 0, 1, 1, 2222.240, 357.790, 36.500, 2.7925, 0, 0, 0.984805, 0.173661, 0, 255, 1, 'mod-brill-home town'),
(971258, 971226, 0, 85, 0, 1, 1, 2229.770, 351.860, 36.500, 2.7925, 0, 0, 0.984805, 0.173661, 0, 255, 1, 'mod-brill-home town'),
(971259, 971226, 0, 85, 0, 1, 1, 2225.070, 353.570, 36.500, 2.7925, 0, 0, 0.984805, 0.173661, 0, 255, 1, 'mod-brill-home town'),
(971260, 971227, 0, 85, 0, 1, 1, 2231.400, 350.200, 36.500, 2.7925, 0, 0, 0.984805, 0.173661, 0, 255, 1, 'mod-brill-home town'),
(971261, 971227, 0, 85, 0, 1, 1, 2232.080, 352.080, 36.500, 2.7925, 0, 0, 0.984805, 0.173661, 0, 255, 1, 'mod-brill-home town'),
(971262, 971227, 0, 85, 0, 1, 1, 2227.050, 352.000, 36.500, 2.7925, 0, 0, 0.984805, 0.173661, 0, 255, 1, 'mod-brill-home town'),
(971263, 971227, 0, 85, 0, 1, 1, 2227.670, 353.690, 36.500, 2.7925, 0, 0, 0.984805, 0.173661, 0, 255, 1, 'mod-brill-home town'),
(971264, 971228, 0, 85, 0, 1, 1, 2230.240, 357.540, 36.500, 1.2217, 0, 0, 0.573564, 0.819161, 0, 255, 1, 'mod-brill-home town'),
(971265, 971229, 0, 85, 0, 1, 1, 2224.170, 343.790, 36.500, 1.2217, 0, 0, 0.573564, 0.819161, 0, 255, 1, 'mod-brill-home town'),
(971266, 971230, 0, 85, 0, 1, 1, 2219.390, 354.040, 36.500, 1.2217, 0, 0, 0.573564, 0.819161, 0, 255, 1, 'mod-brill-home town'),
(971267, 971231, 0, 85, 0, 1, 1, 2222.760, 361.860, 36.500, 1.2217, 0, 0, 0.573564, 0.819161, 0, 255, 1, 'mod-brill-home town'),
(971268, 971231, 0, 85, 0, 1, 1, 2221.170, 362.440, 36.500, 1.7453, 0, 0, 0.766035, 0.642799, 0, 255, 1, 'mod-brill-home town'),
(971269, 971232, 0, 85, 0, 1, 1, 2225.840, 358.610, 36.500, 4.3633, 0, 0, 0.819159, -0.573567, 0, 255, 1, 'mod-brill-home town'),
(971270, 971233, 0, 85, 0, 1, 1, 2229.350, 351.590, 37.840, 1.5708, 0, 0, 0.707108, 0.707105, 0, 255, 1, 'mod-brill-home town'),
(971271, 971234, 0, 85, 0, 1, 1, 2224.920, 354.050, 37.840, 4.0143, 0, 0, 0.906299, -0.422638, 0, 255, 1, 'mod-brill-home town'),
(971272, 971235, 0, 85, 0, 1, 1, 2230.240, 357.540, 37.620, 2.7925, 0, 0, 0.984805, 0.173661, 0, 255, 1, 'mod-brill-home town'),
(971273, 971236, 0, 85, 0, 1, 1, 2279.619, 482.341, 36.180, 3.4907, 0, 0, 0.984804, -0.173670, 0, 255, 1, 'mod-brill-home town'),
(971274, 971237, 0, 85, 0, 1, 1, 2279.927, 481.495, 36.180, 3.4907, 0, 0, 0.984804, -0.173670, 0, 255, 1, 'mod-brill-home town');
INSERT INTO `brill_town_use` (`go`, `ord`, `cond`, `quest`, `credit`, `text_id`, `marker`, `tele_map`, `tele_x`, `tele_y`, `tele_z`, `tele_o`) VALUES
(971201, 0, 'I971200', 971200, 971214, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971202, 0, 'I971200', 971200, 971214, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971203, 0, 'I971200', 971200, 971216, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971208, 0, 'I971201', 971201, 971221, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971209, 0, 'I971201', 971201, 971221, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971211, 0, 'I971203', 971203, 971227, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971216, 0, 'I971204', 971204, 971229, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971217, 0, 'I971204', 971204, 971230, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971218, 0, 'I971200', 971200, 971215, 971200, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971219, 0, 'I971201', 971201, 971218, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971220, 0, 'I971202', 971202, 971223, 971201, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971221, 0, 'I971203', 971203, 971225, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971222, 0, 'I971203', 971203, 971226, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971223, 0, 'I971205', 971205, 971232, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000);
INSERT INTO `brill_town_gossip` (`npc`, `ord`, `kind`, `cond`, `icon`, `text`, `text_id`, `action`, `quest`, `credit`, `marker`, `emote`, `reply`, `arg`) VALUES
(971200, 10000, 'greet', 'R971203', 0, NULL, 971202, '', 0, 0, 0, 0, NULL, 0),
(971200, 10001, 'greet', 'R971201', 0, NULL, 971203, '', 0, 0, 0, 0, NULL, 0),
(971200, 10002, 'greet', 'R971200', 0, NULL, 971204, '', 0, 0, 0, 0, NULL, 0),
(971200, 10003, 'greet', '', 0, NULL, 971205, '', 0, 0, 0, 0, NULL, 0),
(1499, 10004, 'option', 'I971200', 0, 'Edmund Rook asks the town\'s leave to make the old customs office on Stillhome Lane a library.', 0, 'credit', 971200, 971217, 0, 1, 'A library. In the customs office. The Crown taxed every sack of grain that came down that road, and the grain killed us. ...Yes. Let it hold books. Tell Rook the deed is his for a penny a year, and that I will expect a receipt. He\'ll enjoy that.', 0),
(971000, 10005, 'option', 'I971201', 0, 'Tobias Wren needs hinges and brackets for the library\'s shelves.', 0, 'credit', 971201, 971219, 0, 1, 'The quiet one? He came by and stood at the gate for ten minutes and then went away again. Should\'ve said. Here: brass hinges, iron brackets, and a bag of screws I counted myself. Tell him they\'re a loan. Tell him I\'d like to borrow a book. Something with ships.', 0),
(2118, 10006, 'option', 'I971201', 0, 'Tobias Wren the bookbinder needs parchment to mend torn pages.', 0, 'credit', 971201, 971220, 0, 1, 'For mending? Then you want the thin stuff, not the good stuff. ...Here, four bundles. The bottom one\'s a bit foxed. Tell Wren I want the first book he mends, to read, not to keep. I\'ll know if he\'s skipped the poems.', 0),
(971201, 10007, 'greet', 'R971202', 0, NULL, 971206, '', 0, 0, 0, 0, NULL, 0),
(971201, 10008, 'greet', '', 0, NULL, 971207, '', 0, 0, 0, 0, NULL, 0),
(971202, 10009, 'greet', 'R971202', 0, NULL, 971208, '', 0, 0, 0, 0, NULL, 0),
(971202, 10010, 'greet', '', 0, NULL, 971209, '', 0, 0, 0, 0, NULL, 0),
(10781, 10011, 'option', 'I971202', 0, 'Maela Quill of the Brill library asks for a copy of the eastern ward\'s census rolls.', 0, 'credit', 971202, 971222, 0, 1, 'The eastern ward. Quill. Of course it\'s Quill; she wrote half of them. ...The Dark Lady\'s census takes precedence, you understand, but a copy can be made. There. Tell her the Undercity\'s clerks would like their pen back. She knows which one.', 0),
(2309, 10012, 'option', 'I971202 !R971206', 0, 'Maela Quill is recording where Brill\'s people lived before. Do you remember your old street?', 0, 'credit', 971202, 971224, 971206, 1, 'Wheelwrights\' Row. Number nine. There was a girl next door who threw apples at our cat and then cried when it ran off. Freckles. A pinafore with blue birds on it. I can\'t for the life of me remember her name. Funny, the things that stay.', 0),
(2134, 10013, 'option', 'I971202 !R971207', 0, 'Maela Quill is recording where Brill\'s people lived before. Do you remember your old street?', 0, 'credit', 971202, 971224, 971207, 1, 'Before I was Winters? Tolley. Number eleven, Wheelwrights\' Row. Mother made me wear a pinafore with blue birds on it, Light knows why. There was a boy next door with a cat I hated. ...Why are you looking at me like that?', 0),
(2311, 10014, 'option', 'I971202 !R971208', 0, 'Maela Quill is recording where Brill\'s people lived before. Do you remember your old street?', 0, 'credit', 971202, 971224, 971208, 1, 'Wheelwrights\' Row, I think. Fourteen. Or forty. Mother kept bees on the roof, and the bakery was on the corner. ...It wasn\'t? Well, write it down how I said it. The bees are true.', 0),
(2309, 10015, 'greet', 'R971202', 0, NULL, 971210, '', 0, 0, 0, 0, NULL, 0),
(2134, 10016, 'greet', 'R971202', 0, NULL, 971211, '', 0, 0, 0, 0, NULL, 0),
(3547, 10017, 'option', 'I971204 !R971209', 0, 'Edmund Rook invites you to the opening of the Reclamation Library.', 0, 'credit', 971204, 971228, 971209, 3, 'A library! Have they anything on mushrooms? I\'ve got a few things to say about mushrooms, and nobody ever writes them down. I\'ll come. I\'ll bring a basket.', 0),
(5688, 10018, 'option', 'I971204 !R971210', 0, 'Edmund Rook invites you to the opening of the Reclamation Library.', 0, 'credit', 971204, 971228, 971210, 3, 'Edmund? The one who kept his books in my stable? The horses will miss him. I\'ll come, and I\'ll bring something for the table, and if he writes down what I wear I\'ll know.', 0),
(1515, 10019, 'option', 'I971204 !R971211', 0, 'Edmund Rook invites you to the opening of the Reclamation Library.', 0, 'credit', 971204, 971228, 971211, 3, 'A library. Hm. The Deathguard aren\'t much for reading. ...I\'ll come. Someone should make sure the books aren\'t Scarlet propaganda. I\'ll need to read a great many of them, to be sure.', 0),
(2114, 10020, 'option', 'I971204 !R971212', 0, 'Edmund Rook invites you to the opening of the Reclamation Library.', 0, 'credit', 971204, 971228, 971212, 3, 'Books are paper, and paper is pressed herbs, more or less. I\'ll come. Tell him to keep the herbals somewhere dry, or I\'ll take them home with me.', 0),
(971200, 10021, 'option', 'I971204', 0, 'For the case by the door: a child\'s slate from a Tirisfal schoolroom, the lesson still on it.', 0, 'choice', 971204, 971231, 971213, 2, 'A IS FOR APPLE. B IS FOR BREAD. ...Somebody\'s sleeve rubbed out the rest. That\'s what we lost, $n. Not kings. The lesson for Tuesday. It goes beside the chronicle.', 0),
(971200, 10022, 'option', 'I971204', 0, 'For the case by the door: a silver crown of Lordaeron, struck the year of the plague.', 0, 'choice', 971204, 971231, 971214, 2, 'Terenas, young. And the harvest wheat. They struck that the spring before. Everyone had them. Nobody spent the last ones. It goes beside the chronicle, $n, so people remember what the world cost.', 0),
(971200, 10023, 'option', 'I971204', 0, 'For the case by the door: the herald\'s broadsheet announcing the Andorhal grain.', 0, 'choice', 971204, 971231, 971215, 2, '"Good news for the northern parishes." ...I read this aloud in the square myself, I think. I was proud of the price. It goes beside the chronicle, $n. Next to Cinderford. They belong together.', 0),
(971207, 10024, 'greet', 'R971001', 0, NULL, 971212, '', 0, 0, 0, 0, NULL, 0),
(971207, 10025, 'greet', '', 0, NULL, 971213, '', 0, 0, 0, 0, NULL, 0),
(971207, 10026, 'option', 'R971204 R970202 !R971216', 0, 'I found Elinor Harrow\'s letters to Cedric in my house. Would the library like copies?', 0, 'say', 0, 0, 971216, 2, 'Copies. Yes. Keep the originals, $n; they\'re yours, and his, and hers. Tobias will copy them by hand. He says a letter copied by a machine is a letter that\'s been read by a stranger. Maela will want the date of every one.', 0),
(971208, 10027, 'greet', '', 0, NULL, 971214, '', 0, 0, 0, 0, NULL, 0),
(971208, 10028, 'option', 'R971204', 0, 'What\'s in the archive now?', 0, 'say', 0, 0, 0, 1, 'The census of the eastern ward, the Agamand flour ledger, the customs records, the Cinderford chronicle, and a drawer for everything people bring in that has no other drawer. That drawer is the largest. It is not a failure of filing. It\'s a fact about the world.', 0),
(971208, 10029, 'option', 'R971204 R971216', 0, 'Have the Harrow letters been filed?', 0, 'say', 0, 0, 0, 1, 'Copied, dated and filed under HARROW, CEDRIC AND ELINOR, CORRESPONDENCE. Tobias cried over the last one and had to start the page again. I\'ve noted it in the margin. He asked me not to. I\'ve noted that too.', 0),
(971208, 10030, 'option', 'R971204 R970304', 0, 'Have you a copy of the gravekeeper\'s ledger?', 0, 'say', 0, 0, 0, 1, 'Weller let me copy it. Every burial in the plague year, and the four entries written twice. Mercy Hollin came in and corrected her own date of death. She was right. It was the Thursday.', 0),
(971208, 10031, 'option', 'R971204 R970604', 0, 'Anything from Ambrose Wicke\'s shop?', 0, 'say', 0, 0, 0, 1, 'His order ledger, the green one, lent for copying with a great deal of instruction. The Balnir entry is in the family histories now: Tobias Balnir and Marian Hale, to be wed at harvest. I\'ve filed it under weddings. It\'s where it belongs.', 0),
(971208, 10032, 'option', 'R971204 R970504', 0, 'What do you keep on the Scarlet Crusade?', 0, 'say', 0, 0, 0, 1, 'Everything the Deathguard would let me copy about the courier and the leak in Brill, dated and indexed. Their collectors burn our books; we keep theirs. I find that the most satisfying shelf in the room.', 0),
(971208, 10033, 'option', 'R971204 R970704', 0, 'Anything from the Deathguard?', 0, 'say', 0, 0, 0, 1, 'Harlan\'s patrol logs, and a letter the Ashbys asked to have kept. I\'ve put it with the family histories, not the military records. Harlan said that was the right drawer. He\'s the first Deathguard who\'s ever agreed with me.', 0),
(971208, 10034, 'option', 'R971204 R970904', 0, 'Is there a record of what was under the hill?', 0, 'say', 0, 0, 0, 1, 'Thirty-one names, and Croft\'s own roll beside them, so nobody can say later that it didn\'t happen. I keep that drawer locked. Not to hide it. So that opening it is a decision.', 0),
(971208, 10035, 'option', 'R971204 R971104', 0, 'Have you a copy of the chapel\'s Book of Names?', 0, 'say', 0, 0, 0, 1, 'Every page, including the three you carried home. Mirelle Vane checked my copy against hers and found a comma. I have never been so pleased to be corrected.', 0),
(971208, 10036, 'option', 'R971204 R971304', 0, 'Anything from the Stillgarden?', 0, 'say', 0, 0, 0, 1, 'Edda Graves dictated the names of two hundred and twelve flowers. I checked them against an old herbal. She missed one. She says she didn\'t miss it; she\'s leaving it out on purpose. I\'ve noted both positions.', 0),
(971208, 10037, 'option', 'R971204 R971404', 0, 'Do you keep the Surgeon\'s Hall\'s records?', 0, 'say', 0, 0, 0, 1, 'Copies of the patient charter, and Agnes Morrow\'s case, with her permission, in Elspeth Rane\'s hand, which is the worst hand I have ever had to read. I\'ve made a fair copy. She says it\'s less accurate. It isn\'t.', 0),
(971208, 10038, 'option', 'R971204 R971504', 0, 'Does the caravan office send you anything?', 0, 'say', 0, 0, 0, 1, 'Every manifest, in duplicate. Irena Sable is the only person in Brill whose records I haven\'t had to correct. We don\'t like each other at all. It\'s wonderful.', 0),
(971208, 10039, 'option', 'R971204 R971604', 0, 'Anything from the brewery?', 0, 'say', 0, 0, 0, 1, 'Oren Blackbarrel\'s father\'s recipe book, lent for copying. Half the measurements are in thumbs. I\'ve filed it under history, not cookery, until somebody can tell me how large his father\'s thumbs were.', 0),
(971209, 10040, 'greet', '', 0, NULL, 971215, '', 0, 0, 0, 0, NULL, 0),
(971209, 10041, 'option', 'R971204', 1, 'Let me see your writing supplies.', 0, 'vendor', 0, 0, 0, 0, NULL, 0),
(971209, 10042, 'option', 'R971204', 1, 'Could the library spare a few books for my house? And something to write in.', 0, 'buy', 0, 0, 971217, 2, 'Histories, on long loan; Edmund has written down that you have them. And three journals I bound myself. Sixty silver, for the binding thread. I\'ll carry them over tonight and put them by the bed, where you\'ll read them.', 6000),
(971210, 10043, 'greet', '', 0, NULL, 971216, '', 0, 0, 0, 0, NULL, 0),
(971203, 10044, 'greet', '', 0, NULL, 971217, '', 0, 0, 0, 0, NULL, 0),
(971211, 10045, 'greet', '', 0, NULL, 971218, '', 0, 0, 0, 0, NULL, 0),
(971212, 10046, 'greet', '', 0, NULL, 971219, '', 0, 0, 0, 0, NULL, 0),
(971213, 10047, 'greet', '', 0, NULL, 971220, '', 0, 0, 0, 0, NULL, 0),
(971204, 10048, 'greet', '', 0, NULL, 971221, '', 0, 0, 0, 0, NULL, 0),
(971205, 10049, 'greet', '', 0, NULL, 971222, '', 0, 0, 0, 0, NULL, 0);
UPDATE `creature_template` SET `npcflag` = `npcflag` | 1 WHERE `entry` IN (1499, 1515, 2114, 2118, 2134, 2309, 2311, 3547, 5688, 10781);
INSERT INTO `brill_town_phase` (`bit`, `ord`, `cond`) VALUES
(4, 0, '!R971204');
INSERT INTO `brill_town_stage` (`type`, `value`, `ord`, `cond`) VALUES
(4, 1, 0, 'R971000'),
(4, 2, 0, 'R971200'),
(4, 3, 0, 'R971201'),
(4, 4, 0, 'R971202'),
(4, 5, 0, 'R971203'),
(4, 6, 0, 'R971204'),
(4, 7, 0, 'R971217');
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `Flags`, `RewardXPDifficulty`, `RewardMoney`, `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `AreaDescription`, `QuestCompletionLog`, `RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `ObjectiveText1`, `RequiredNpcOrGo2`, `RequiredNpcOrGoCount2`, `ObjectiveText2`, `RequiredNpcOrGo3`, `RequiredNpcOrGoCount3`, `ObjectiveText3`, `RequiredNpcOrGo4`, `RequiredNpcOrGoCount4`, `ObjectiveText4`, `RewardItem1`, `RewardAmount1`, `RewardItem2`, `RewardAmount2`, `RewardItem3`, `RewardAmount3`, `RewardItem4`, `RewardAmount4`) VALUES
(971200, 2, -1, 8, 159, 0, 3, 1500, 0, 'More Than Ashes', 'Inspect the old customs office on Stillhome Lane and its flooded cellar, recover 5 surviving books from the abandoned Garren farm at Garren\'s Haunt, retrieve the office\'s record chest, and obtain Magistrate Sevren\'s permission to convert the property.', 'You\'re $n. I know because I wrote it down when you passed the inn on Tuesday. I write everything down. It isn\'t a habit, it\'s a precaution.$B$BEdmund Rook. I was a tutor once, in a house with a library. I remember the smell of that room better than the faces of the children, and that frightens me more than anything the Scourge ever did.$B$BI have forty-one books in crates in the inn\'s stable, and the horses are eating the bindings. Brill needs a library. Not for me: for every one of us who woke up with half a life missing.$B$BThe old customs office on Stillhome Lane is empty. Look it over with me, cellar and all. The Garrens out at Garren\'s Haunt kept more books than any house in the parish; bring back whatever the gnolls haven\'t eaten. There\'s a record chest in the office somewhere. And the Magistrate must agree, or none of this is legal, and I would hate to be dead and a squatter.', '', 'Return to Edmund Rook at the old customs office on Stillhome Lane in Brill.', 971214, 2, 'The office and its flooded cellar inspected', 971215, 5, 'Surviving books recovered', 971216, 1, 'The office\'s record chest', 971217, 1, 'Magistrate Sevren\'s permission', 955, 2, 0, 0, 0, 0, 0, 0),
(971201, 2, -1, 8, 159, 0, 4, 2000, 0, 'Shelves for the Dead', 'Gather 8 pieces of hardwood from the dead oaks west of Brill, get hinges and brackets from Rudd Carver at the builder\'s yard and repairable parchment from Abigail Shiel, then help Tobias Wren assemble the first shelves and mend the cellar window.', '(The bookbinder speaks so quietly you have to lean in.)$B$BTobias Wren. I bind books. Bound, I should say; I haven\'t had a book to bind since the plague. Edmund has forty-one, and every one of them is coming apart.$B$BThey need shelves before they need me. Dry ones, off the floor, out of the light. The oaks the blight killed, west of town past the last houses: they\'ve stood dead so long they\'ve seasoned on the root. Eight good lengths. Rudd Carver has hinges and brackets, if you ask him nicely, and Abigail Shiel sells parchment I can use to mend the torn leaves.$B$BThen help me put the first shelves together. And the cellar window, before the next rain. Water is the only thing books are afraid of. Well. Water and the Scarlet Crusade.', '', 'Return to Tobias Wren at the old customs office on Stillhome Lane in Brill.', 971218, 8, 'Seasoned hardwood', 971219, 1, 'Hinges and brackets from the builder\'s yard', 971220, 1, 'Repairable parchment from Abigail Shiel', 971221, 2, 'Shelves assembled and the cellar window mended', 858, 3, 0, 0, 0, 0, 0, 0),
(971202, 2, -1, 8, 159, 0, 4, 2500, 0, 'The Names We Carried', 'Obtain the surviving census records from Royal Overseer Bauhaus in the Undercity, recover the Agamand mill\'s ledger from the barn at Agamand Mills, then record the memories of Thomas Arlento, Mrs. Winters and Doreen Beltis in Brill.', 'Maela Quill. I took the census of Lordaeron\'s eastern ward three times, and I can tell you the household of every door on Wheelwrights\' Row, and I would very much like people to stop telling me the bakery was on the corner. It was not on the corner.$B$BThree people in Brill gave me the same street when Edmund asked where they lived before. Wheelwrights\' Row. None of them knows the others. They walk past each other every day.$B$BI want the records. The Undercity kept what the Crown\'s clerks didn\'t burn: Royal Overseer Bauhaus has the census rolls, if you can make him part with a copy. The Agamand mill kept a ledger of every family in the eastern ward that bought their flour; it\'s in the barn at Agamand Mills, if the bones there haven\'t sat on it. Then talk to them: Thomas Arlento, Mrs. Winters at the general store, Doreen Beltis. Write down what they remember. Exactly what they remember, $n. Not what they\'d like to.', '', 'Return to Maela Quill at the old customs office on Stillhome Lane in Brill.', 971222, 1, 'The Undercity\'s census records', 971223, 1, 'The Agamand mill\'s ledger', 971224, 3, 'Residents\' memories recorded', 0, 0, '', 2455, 3, 0, 0, 0, 0, 0, 0),
(971203, 2, -1, 9, 159, 0, 5, 3000, 0, 'The Missing Chapter', 'Search the Scarlet Crusade\'s record store in the barn at Solliden Farmstead, deal with the Scarlet collectors there, recover the Cinderford chronicle\'s missing pages, and reassemble the chronicle at Edmund Rook\'s worktable in Brill.', 'Cinderford. A village a day\'s walk north of here, before. It burned in the second month of the plague, and everyone knows the story: the villagers barred the road against the sick, and the sick burned it down around them. They tell it in the Undercity as a lesson about the living.$B$BThe parish clerk kept a chronicle. I thought it was lost. It isn\'t. A trader swears he saw it in a crate at Solliden Farmstead last month, with the Scarlet Crusade\'s seal on the lid: they\'ve been collecting what they call plague-tainted writings from every ruin in Tirisfal, and carting them to the Solliden barn to sort and burn.$B$BI want that chronicle, $n. Whatever it says. Go to the barn, find their record store, and bring me every page you can. The collectors won\'t hand it over, and I don\'t suppose you\'ll ask them twice.', '', 'Return to Edmund Rook at the old customs office on Stillhome Lane in Brill.', 971225, 1, 'The Scarlet record store searched', 971206, 5, 'Scarlet Collectors', 971226, 3, 'The chronicle\'s missing pages', 971227, 1, 'The chronicle reassembled and its last entry read', 929, 2, 0, 0, 0, 0, 0, 0),
(971204, 2, -1, 9, 159, 0, 5, 5000, 0, 'An Open Book', 'Deliver Edmund Rook\'s invitations to Hamlin Atkins, Innkeeper Renee, Executor Zygand and Faruza, help Tobias Wren finish the reading table and sort 6 books into their collections, donate a recovered artifact, then attend the library\'s opening.', 'It\'s nearly ready. Shelves, tables, a case for the chronicle, Maela\'s archive, Tobias\'s poems in every margin he thinks I won\'t check.$B$BAnd nobody will come.$B$BNo, I\'ve thought about it. I\'ve written it down. The living had libraries because they had time. We have nothing but time, and we spend it standing in doorways. Who will walk in?$B$BTake these invitations. Hamlin Atkins, the innkeeper, the Executor, Faruza. If those four come, the rest of Brill will follow to see why. Help Tobias with the last table; there are books on every surface that need sorting into their collections. And bring something for the case by the door, $n. One thing you found out there that ought to be remembered. A library ought to begin with a gift.', '', 'Return to Edmund Rook at the old customs office on Stillhome Lane in Brill.', 971228, 4, 'Invitations delivered', 971229, 1, 'The last reading table finished', 971230, 6, 'Books sorted into their collections', 971231, 1, 'A recovered artifact donated', 3385, 3, 0, 0, 0, 0, 0, 0),
(971205, 2, -1, 8, 159, 4096, 2, 1500, 0, 'Lost Pages', 'Recover 3 lost documents from the abandoned places of Tirisfal: the barns at Garren\'s Haunt and Agamand Mills, the farmhouse at Solliden Farmstead and the sheds behind Cold Hearth Manor.', 'Every abandoned house in Tirisfal has paper in it. Letters behind the dresser, a diary under a mattress, deeds in a tin, a grocer\'s bill nobody will ever pay. The rain is getting to them faster than we are.$B$BMaela keeps a list of where people have seen them: the barns at Garren\'s and the mills, the Solliden farmhouse, the sheds behind Cold Hearth. Bring me three. I\'ll write down where you found them.$B$BIt isn\'t glamorous. Nobody will thank you for a grocer\'s bill. But one day someone will walk in here and ask whether anyone remembers a family called Brewer, and Maela will open a drawer.', '', 'Return to Edmund Rook in the Reclamation Library.', 971232, 3, 'Lost documents recovered', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971206, 2, 1, 1, -1, 0, 0, 0, 0, '[asked_thomas]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971207, 2, 1, 1, -1, 0, 0, 0, 0, '[asked_winters]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971208, 2, 1, 1, -1, 0, 0, 0, 0, '[asked_doreen]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971209, 2, 1, 1, -1, 0, 0, 0, 0, '[invited_hamlin]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971210, 2, 1, 1, -1, 0, 0, 0, 0, '[invited_renee]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971211, 2, 1, 1, -1, 0, 0, 0, 0, '[invited_zygand]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971212, 2, 1, 1, -1, 0, 0, 0, 0, '[invited_faruza]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971213, 2, 1, 1, -1, 0, 0, 0, 0, '[slate]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971214, 2, 1, 1, -1, 0, 0, 0, 0, '[crown]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971215, 2, 1, 1, -1, 0, 0, 0, 0, '[broadsheet]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971216, 2, 1, 1, -1, 0, 0, 0, 0, '[letters]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971217, 2, 1, 1, -1, 0, 0, 0, 0, '[house_set]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`, `SpecialFlags`) VALUES (971200, 0, 0), (971201, 971200, 0), (971202, 971201, 0), (971203, 971202, 0), (971204, 971203, 0), (971205, 971204, 1);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`) VALUES
(971200, 1, '(Edmund turns the pages of a small green primer, swollen with damp, and stops at the flyleaf.)$B$B"For my Davey, who will read it before I can. Mother."$B$BI don\'t know who Davey was. I don\'t know if he learned to read. I\'m going to find out.$B$B...Not today. Today this goes on a shelf, and it\'s the first book in the Reclamation Library, and I\'m going to write down that it was.'),
(971201, 1, '(Tobias runs a thumb along the first shelf and doesn\'t seem to notice he\'s smiling.)$B$BLevel. Even the dead can build level.$B$BI wrote something in the margin of Edmund\'s ledger while you were gone. Don\'t tell him. "Oak that died standing / holds the books of those who fell. / Neither minds the weight." It isn\'t very good. Margins are where you put the things that aren\'t very good.'),
(971202, 1, '(Maela reads your notes twice and then sets the census roll beside them, one line at a time.)$B$BArlento, number nine, Wheelwrights\' Row. Winters, then Tolley, number eleven. Next door. They shared a wall for fourteen years.$B$BHe\'s been buying lamp oil from her since the autumn. She\'s been overcharging him, I expect. ...No, don\'t tell them. I already sent a note. I\'m told he went straight to the store and stood there for a quarter of an hour and neither of them said a word, and then she gave him the oil for nothing.$B$BThis is what an archive is for. Not the past. The people still in it.'),
(971203, 1, '(Edmund reads the last entry with you, and then sits for a long while with his hand flat on the page.)$B$BThey didn\'t bar the road. They opened the church to everyone, sick and well, and sat them in the same pews, because nobody knew yet what the sickness was, and the clerk wrote that it would be a sin to choose. And then they died. Together. The Crown\'s men burned the village afterward, to be safe.$B$BIt\'s worse than the story. It\'s also true. It goes in a case by the door, and anyone in Brill can read it.'),
(971204, 1, '(They come: Hamlin with mushroom dirt still on his boots, the innkeeper with a basket, the Executor, who stands at the back with his arms folded and reads for an hour. And then the rest of Brill, to see why.)$B$B(Near closing, a woman at the far table makes a small sound. She\'s holding a letter from the bottom of one of Edmund\'s crates. She doesn\'t put it down when the lamps are dimmed, and nobody asks her to leave.)$B$BThat\'s Nora Bell. She\'s been looking for her family since the spring. I think, $n, she\'s found someone.$B$BI\'m going to write down that this happened. And then I\'m going to stop writing for a while and watch it.'),
(971205, 1, '(Edmund unfolds each one as if it might break, and copies it into the register before he reads it properly.)$B$BA recipe. A bill of sale for a goat. A love letter with the name scratched out. All of it, $n. All of it counts.');
INSERT INTO `quest_request_items` (`ID`, `EmoteOnComplete`, `EmoteOnIncomplete`, `CompletionText`) VALUES
(971200, 1, 1, 'Five books, $n. I\'d settle for four. I wouldn\'t settle for four. I\'d write down that I settled and then lie awake about it.'),
(971201, 1, 1, 'Dry wood, dry paper, dry cellar. It sounds simple. Most simple things are, until it rains.'),
(971202, 1, 1, 'Exactly, $n. If they say the bakery was on the corner, write that down, and write that they were wrong.'),
(971203, 1, 1, 'Every page. A chronicle with the end torn out isn\'t history. It\'s a rumour with a binding.'),
(971204, 1, 1, 'Did they say they\'d come? Did they say it as though they meant it? Write down how they said it.'),
(971205, 1, 1, 'Three, $n. Anything with writing on it. Anything at all.');
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES (971200, 971200), (971201, 971201), (971202, 971202), (971200, 971203), (971200, 971204), (971207, 971205);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES (971200, 971200), (971201, 971201), (971202, 971202), (971200, 971203), (971200, 971204), (971207, 971205);

-- The Stillgarden
INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`) VALUES (971302, 0, 2447, 0, 0, 0), (971302, 1, 765, 0, 0, 0), (971302, 2, 2449, 0, 0, 0), (971302, 3, 785, 0, 0, 0), (971302, 4, 2450, 0, 0, 0), (971302, 5, 3369, 0, 0, 0), (971302, 6, 4605, 0, 0, 0), (971302, 7, 4604, 0, 0, 0), (971302, 8, 22250, 0, 0, 0), (971302, 9, 3421, 0, 0, 0), (971302, 10, 3419, 0, 0, 0), (971302, 11, 3420, 0, 0, 0), (971302, 12, 2453, 0, 0, 0), (971302, 13, 2452, 0, 0, 0), (971302, 14, 2562, 0, 0, 0), (971302, 15, 3422, 0, 0, 0);
INSERT INTO `creature_template` (`entry`, `name`, `subname`, `gossip_menu_id`, `minlevel`, `maxlevel`, `faction`, `npcflag`, `speed_walk`, `speed_run`, `unit_class`, `unit_flags`, `type`, `rank`, `HealthModifier`, `DamageModifier`, `mingold`, `maxgold`, `flags_extra`, `AIName`, `ScriptName`) VALUES
(971300, 'Edda Graves', 'Gardener', 0, 20, 20, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971301, 'Pellen Moss', 'Herbalist', 0, 20, 20, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971302, 'Pellen Moss', 'Herbalist', 0, 20, 20, 68, 129, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971303, 'Willa Fen', 'Garden Attendant', 0, 15, 15, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971304, 'Willa Fen', 'Garden Attendant', 0, 15, 15, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971305, 'Willa Fen', 'Garden Attendant', 0, 15, 15, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971306, 'Odo', 'Garden Watchman', 0, 25, 25, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971307, 'Odo', 'Garden Watchman', 0, 25, 25, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971308, 'Odo', 'Garden Watchman', 0, 25, 25, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971309, 'Builder\'s Yard Laborer', NULL, 0, 15, 15, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971310, 'Oswin Thatcher', 'Carpenter', 0, 25, 25, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971311, 'Brill Resident', NULL, 0, 10, 10, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971312, 'Carolai Anise', 'Alchemy Trainer', 0, 20, 20, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971313, 'Bloated Drain Toad', NULL, 0, 9, 10, 14, 0, 1, 1.14286, 1, 0, 1, 0, 0.9, 0.9, 40, 40, 0, '', ''),
(971314, 'Blighted weeds pulled', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971315, 'Rubble shifted', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971316, 'Soil taken from the stakes', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971317, 'Pellen Moss\'s assessment', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971318, 'Gravebloom seedlings lifted', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971319, 'Pale spore cap', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971320, 'Brightwater silt and water', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971321, 'Beds planted and watered', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971322, 'Cracked drain inspected', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971323, 'Drain outlet cleared', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971324, 'Soil treatment mixed with Pellen', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971325, 'Townsfolk\'s flowers remembered', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971326, 'Seeds from Cold Hearth Manor', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971327, 'Moonpetal lily', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971328, 'Memorial bed planted', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971329, 'Ripe herbs cut', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971330, 'Pellen\'s stall set out', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971331, 'Bouquet laid and guests invited', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971332, 'Edda\'s question answered', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971333, 'Beds tended', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971334, 'Ripe herbs cut', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', '');
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`) VALUES
(971300, 0, 4123, 1, 1),
(971301, 0, 2646, 1, 1),
(971302, 0, 2646, 1, 1),
(971303, 0, 2672, 1, 1),
(971304, 0, 2672, 1, 1),
(971305, 0, 2672, 1, 1),
(971306, 0, 2625, 1, 1),
(971307, 0, 2625, 1, 1),
(971308, 0, 2625, 1, 1),
(971309, 0, 2632, 1, 1),
(971309, 1, 2642, 1, 1),
(971309, 2, 2647, 1, 1),
(971310, 0, 1638, 1, 1),
(971311, 0, 2657, 1, 1),
(971311, 1, 2628, 1, 1),
(971311, 2, 2630, 1, 1),
(971312, 0, 1601, 1, 1),
(971313, 0, 5379, 1.2, 1),
(971314, 0, 11686, 1, 1),
(971315, 0, 11686, 1, 1),
(971316, 0, 11686, 1, 1),
(971317, 0, 11686, 1, 1),
(971318, 0, 11686, 1, 1),
(971319, 0, 11686, 1, 1),
(971320, 0, 11686, 1, 1),
(971321, 0, 11686, 1, 1),
(971322, 0, 11686, 1, 1),
(971323, 0, 11686, 1, 1),
(971324, 0, 11686, 1, 1),
(971325, 0, 11686, 1, 1),
(971326, 0, 11686, 1, 1),
(971327, 0, 11686, 1, 1),
(971328, 0, 11686, 1, 1),
(971329, 0, 11686, 1, 1),
(971330, 0, 11686, 1, 1),
(971331, 0, 11686, 1, 1),
(971332, 0, 11686, 1, 1),
(971333, 0, 11686, 1, 1),
(971334, 0, 11686, 1, 1);
INSERT INTO `creature` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(971300, 971300, 0, 85, 0, 1, 1, 2347.000, 213.000, 38.160, 0.6800, 60, 0, 0, 'mod-brill-home town'),
(971301, 971301, 0, 85, 0, 1, 8, 2351.000, 211.000, 38.270, 4.7100, 60, 0, 0, 'mod-brill-home town'),
(971302, 971302, 0, 85, 0, 1, 1, 2362.500, 211.000, 36.910, 1.5700, 60, 0, 0, 'mod-brill-home town'),
(971303, 971303, 0, 85, 0, 1, 8, 2344.500, 211.800, 38.130, 5.2000, 60, 0, 0, 'mod-brill-home town'),
(971304, 971304, 0, 85, 0, 1, 1, 2354.000, 209.400, 38.240, 4.7100, 60, 0, 0, 'mod-brill-home town'),
(971305, 971305, 0, 85, 0, 1, 1, 2342.900, 210.800, 38.090, 2.2000, 60, 0, 0, 'mod-brill-home town'),
(971306, 971306, 0, 85, 0, 1, 8, 2364.600, 206.200, 36.720, 2.9000, 60, 0, 0, 'mod-brill-home town'),
(971307, 971307, 0, 85, 0, 1, 1, 2349.000, 209.400, 38.350, 4.6000, 60, 0, 0, 'mod-brill-home town'),
(971308, 971308, 0, 85, 0, 1, 1, 2357.600, 220.400, 36.610, 1.5700, 60, 0, 0, 'mod-brill-home town'),
(971309, 971309, 0, 85, 0, 1, 8, 2338.500, 210.500, 37.710, 0.0000, 60, 3, 1, 'mod-brill-home town'),
(971310, 971309, 0, 85, 0, 1, 8, 2358.500, 206.800, 38.030, 3.0000, 60, 3, 1, 'mod-brill-home town'),
(971311, 971310, 0, 85, 0, 1, 8, 2361.000, 209.000, 37.410, 2.6000, 60, 0, 0, 'mod-brill-home town'),
(971312, 971311, 0, 85, 0, 1, 1, 2336.000, 214.600, 36.970, 1.5700, 60, 0, 0, 'mod-brill-home town'),
(971313, 971311, 0, 85, 0, 1, 1, 2343.800, 214.600, 37.820, 1.5700, 60, 0, 0, 'mod-brill-home town'),
(971314, 971312, 0, 85, 0, 1, 1, 2355.000, 200.000, 38.390, 1.2000, 60, 0, 0, 'mod-brill-home town'),
(971315, 971313, 0, 85, 0, 1, 1, 2398.000, 120.000, 30.880, 0.0000, 60, 4, 1, 'mod-brill-home town'),
(971316, 971313, 0, 85, 0, 1, 1, 2405.000, 124.000, 31.620, 1.0000, 60, 4, 1, 'mod-brill-home town'),
(971317, 971313, 0, 85, 0, 1, 1, 2400.000, 116.000, 29.900, 2.0000, 60, 4, 1, 'mod-brill-home town'),
(971318, 971313, 0, 85, 0, 1, 1, 2395.000, 128.000, 31.980, 3.0000, 60, 4, 1, 'mod-brill-home town'),
(971319, 971313, 0, 85, 0, 1, 1, 2402.000, 131.000, 33.850, 4.0000, 60, 4, 1, 'mod-brill-home town'),
(971320, 971313, 0, 85, 0, 1, 1, 2409.000, 126.000, 30.530, 5.0000, 60, 4, 1, 'mod-brill-home town');
INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `Data0`, `Data1`, `ScriptName`) VALUES
(971300, 10, 4111, 'Blighted Weeds', 1.3, 0, 971300, 'go_brill_town'),
(971301, 10, 134, 'Fallen Wall', 1, 0, 971300, 'go_brill_town'),
(971302, 10, 5452, 'Edda\'s Marker Stake', 0.8, 0, 971300, 'go_brill_town'),
(971303, 5, 6151, 'Garden Fence', 1, 0, 0, ''),
(971304, 2, 20, 'Garden Bed', 1, 0, 0, 'go_brill_town'),
(971305, 5, 6479, 'Spade', 1, 0, 0, ''),
(971306, 5, 662, 'Tool Shed', 1, 0, 0, ''),
(971307, 5, 4632, 'Gravebloom', 1.2, 0, 0, ''),
(971308, 5, 7884, 'Nightshade', 0.8, 0, 0, ''),
(971309, 5, 6648, 'Asters', 1.2, 0, 0, ''),
(971310, 5, 755, 'New Sluice', 2.5, 0, 0, ''),
(971311, 5, 6036, 'Rain Barrel', 1, 0, 0, ''),
(971312, 5, 6313, 'Flower Bed', 0.8, 0, 0, ''),
(971313, 5, 385, 'Pale Fungus', 0.45, 0, 0, ''),
(971314, 2, 49, 'Memorial Bed', 1, 0, 0, 'go_brill_town'),
(971315, 7, 682, 'Garden Bench', 1, 1, 1, ''),
(971316, 5, 6647, 'Forget-Me-Nots', 1.2, 0, 0, ''),
(971317, 5, 253, 'Moonpetal Lily', 0.9, 0, 0, ''),
(971318, 2, 269, 'Ripe Peacebloom', 0.6, 0, 0, 'go_brill_town'),
(971319, 2, 270, 'Ripe Silverleaf', 0.4, 0, 0, 'go_brill_town'),
(971320, 2, 4632, 'Ripe Gravebloom', 1.8, 0, 0, 'go_brill_town'),
(971321, 10, 7443, 'Pellen\'s Stall', 1, 0, 971304, 'go_brill_town'),
(971322, 5, 6963, 'Herb Sacks', 1, 0, 0, ''),
(971323, 10, 4632, 'Gravebloom', 1, 0, 971301, 'go_brill_town'),
(971324, 10, 359, 'Pale Spore Cap', 0.7, 0, 971301, 'go_brill_town'),
(971325, 10, 20, 'Brightwater Silt', 0.5, 0, 971301, 'go_brill_town'),
(971326, 10, 7969, 'Cracked Drain', 2.5, 0, 971302, 'go_brill_town'),
(971327, 10, 134, 'Choked Drain Mouth', 1, 0, 971302, 'go_brill_town'),
(971328, 10, 6606, 'Rotted Seed Frame', 1, 0, 971303, 'go_brill_town'),
(971329, 10, 253, 'Moonpetal Lily', 1, 0, 971303, 'go_brill_town'),
(971330, 10, 498, 'Plague Graves', 1.6, 0, 971304, 'go_brill_town'),
(971331, 5, 6646, 'Edda\'s Wreath', 1, 0, 0, ''),
(971332, 5, 6647, 'Edda\'s Flowers', 1.3, 0, 0, ''),
(971333, 5, 7792, 'Fungal Terrarium', 1.2, 0, 0, '');
INSERT INTO `gameobject_template_addon` (`entry`, `faction`, `flags`) VALUES (971300, 0, 4), (971301, 0, 4), (971302, 0, 4), (971321, 0, 4), (971323, 0, 4), (971324, 0, 4), (971325, 0, 4), (971326, 0, 4), (971327, 0, 4), (971328, 0, 4), (971329, 0, 4), (971330, 0, 4);
INSERT INTO `gameobject` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`, `animprogress`, `state`, `Comment`) VALUES
(971300, 971300, 0, 85, 0, 1, 8, 2345.000, 203.200, 38.360, 0.3000, 0, 0, 0.149438, 0.988771, 0, 255, 1, 'mod-brill-home town'),
(971301, 971300, 0, 85, 0, 1, 8, 2350.000, 210.600, 38.220, 1.4000, 0, 0, 0.644218, 0.764842, 0, 255, 1, 'mod-brill-home town'),
(971302, 971300, 0, 85, 0, 1, 8, 2357.500, 203.200, 38.150, 2.5000, 0, 0, 0.948985, 0.315322, 0, 255, 1, 'mod-brill-home town'),
(971303, 971300, 0, 85, 0, 1, 8, 2360.500, 205.000, 37.630, 4.0000, 0, 0, 0.909297, -0.416147, 0, 255, 1, 'mod-brill-home town'),
(971304, 971300, 0, 85, 0, 1, 8, 2336.500, 208.000, 37.670, 5.1000, 0, 0, 0.557684, -0.830054, 0, 255, 1, 'mod-brill-home town'),
(971305, 971300, 0, 85, 0, 1, 8, 2352.000, 214.600, 37.930, 0.9000, 0, 0, 0.434966, 0.900447, 0, 255, 1, 'mod-brill-home town'),
(971306, 971301, 0, 85, 0, 1, 8, 2341.000, 204.600, 38.160, 0.4000, 0, 0, 0.198669, 0.980067, 0, 255, 1, 'mod-brill-home town'),
(971307, 971301, 0, 85, 0, 1, 8, 2353.500, 202.800, 38.300, 2.0000, 0, 0, 0.841471, 0.540302, 0, 255, 1, 'mod-brill-home town'),
(971308, 971301, 0, 85, 0, 1, 8, 2364.000, 203.000, 36.890, 3.5000, 0, 0, 0.983986, -0.178246, 0, 255, 1, 'mod-brill-home town'),
(971309, 971301, 0, 85, 0, 1, 8, 2365.000, 209.500, 36.280, 5.0000, 0, 0, 0.598472, -0.801144, 0, 255, 1, 'mod-brill-home town'),
(971310, 971302, 0, 85, 0, 1, 8, 2343.500, 209.400, 38.080, 1.5700, 0, 0, 0.706825, 0.707388, 0, 255, 1, 'mod-brill-home town'),
(971311, 971302, 0, 85, 0, 1, 8, 2348.500, 209.400, 38.240, 1.5700, 0, 0, 0.706825, 0.707388, 0, 255, 1, 'mod-brill-home town'),
(971312, 971302, 0, 85, 0, 1, 8, 2353.500, 209.400, 38.160, 1.5700, 0, 0, 0.706825, 0.707388, 0, 255, 1, 'mod-brill-home town'),
(971313, 971303, 0, 85, 0, 1, 1, 2342.200, 218.000, 36.620, 3.1416, 0, 0, 1.000000, -0.000004, 0, 255, 1, 'mod-brill-home town'),
(971314, 971303, 0, 85, 0, 1, 1, 2346.400, 218.000, 37.460, 3.1416, 0, 0, 1.000000, -0.000004, 0, 255, 1, 'mod-brill-home town'),
(971315, 971303, 0, 85, 0, 1, 1, 2350.600, 218.000, 37.620, 3.1416, 0, 0, 1.000000, -0.000004, 0, 255, 1, 'mod-brill-home town'),
(971316, 971303, 0, 85, 0, 1, 1, 2360.600, 218.000, 36.350, 3.1416, 0, 0, 1.000000, -0.000004, 0, 255, 1, 'mod-brill-home town'),
(971317, 971303, 0, 85, 0, 1, 1, 2366.800, 199.500, 36.250, 4.7100, 0, 0, 0.707951, -0.706262, 0, 255, 1, 'mod-brill-home town'),
(971318, 971303, 0, 85, 0, 1, 1, 2366.800, 203.700, 36.190, 4.7100, 0, 0, 0.707951, -0.706262, 0, 255, 1, 'mod-brill-home town'),
(971319, 971303, 0, 85, 0, 1, 1, 2366.800, 207.900, 35.950, 4.7100, 0, 0, 0.707951, -0.706262, 0, 255, 1, 'mod-brill-home town'),
(971320, 971303, 0, 85, 0, 1, 1, 2366.800, 212.100, 35.530, 4.7100, 0, 0, 0.707951, -0.706262, 0, 255, 1, 'mod-brill-home town'),
(971321, 971304, 0, 85, 0, 1, 1, 2343.500, 207.000, 38.170, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(971322, 971304, 0, 85, 0, 1, 1, 2348.500, 207.000, 38.300, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(971323, 971304, 0, 85, 0, 1, 1, 2353.500, 207.000, 38.230, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(971324, 971305, 0, 85, 0, 1, 8, 2345.600, 205.300, 38.300, 0.2000, 0, 0, 0.099833, 0.995004, 0, 255, 1, 'mod-brill-home town'),
(971325, 971305, 0, 85, 0, 1, 8, 2355.600, 205.400, 38.180, 1.0000, 0, 0, 0.479426, 0.877583, 0, 255, 1, 'mod-brill-home town'),
(971326, 971306, 0, 85, 0, 1, 1, 2339.800, 199.000, 38.490, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(971327, 971307, 0, 85, 0, 1, 1, 2342.600, 207.000, 38.580, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(971328, 971307, 0, 85, 0, 1, 1, 2347.600, 207.000, 38.740, 1.0000, 0, 0, 0.479426, 0.877583, 0, 255, 1, 'mod-brill-home town'),
(971329, 971307, 0, 85, 0, 1, 1, 2352.600, 207.000, 38.700, 2.0000, 0, 0, 0.841471, 0.540302, 0, 255, 1, 'mod-brill-home town'),
(971330, 971308, 0, 85, 0, 1, 1, 2344.400, 207.100, 38.610, 0.5000, 0, 0, 0.247404, 0.968912, 0, 255, 1, 'mod-brill-home town'),
(971331, 971308, 0, 85, 0, 1, 1, 2349.400, 206.900, 38.710, 1.5000, 0, 0, 0.681639, 0.731689, 0, 255, 1, 'mod-brill-home town'),
(971332, 971308, 0, 85, 0, 1, 1, 2354.400, 207.100, 38.590, 2.5000, 0, 0, 0.948985, 0.315322, 0, 255, 1, 'mod-brill-home town'),
(971333, 971309, 0, 85, 0, 1, 1, 2347.300, 216.600, 38.360, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(971334, 971309, 0, 85, 0, 1, 1, 2349.700, 216.600, 38.450, 1.0000, 0, 0, 0.479426, 0.877583, 0, 255, 1, 'mod-brill-home town'),
(971335, 971309, 0, 85, 0, 1, 1, 2352.800, 216.600, 38.310, 2.0000, 0, 0, 0.841471, 0.540302, 0, 255, 1, 'mod-brill-home town'),
(971336, 971309, 0, 85, 0, 1, 1, 2355.200, 216.600, 38.090, 3.0000, 0, 0, 0.997495, 0.070737, 0, 255, 1, 'mod-brill-home town'),
(971337, 971310, 0, 85, 0, 1, 1, 2365.000, 196.800, 36.670, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(971338, 971311, 0, 85, 0, 1, 1, 2362.600, 199.400, 37.280, 0.3000, 0, 0, 0.149438, 0.988771, 0, 255, 1, 'mod-brill-home town'),
(971339, 971312, 0, 85, 0, 1, 1, 2343.500, 206.200, 38.600, 0.7000, 0, 0, 0.342898, 0.939373, 0, 255, 1, 'mod-brill-home town'),
(971340, 971312, 0, 85, 0, 1, 1, 2348.500, 207.800, 38.690, 2.2000, 0, 0, 0.891207, 0.453596, 0, 255, 1, 'mod-brill-home town'),
(971341, 971312, 0, 85, 0, 1, 1, 2353.500, 206.200, 38.640, 4.0000, 0, 0, 0.909297, -0.416147, 0, 255, 1, 'mod-brill-home town'),
(971342, 971313, 0, 85, 0, 1, 1, 2346.600, 195.600, 38.960, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(971343, 971313, 0, 85, 0, 1, 1, 2358.600, 195.800, 38.020, 1.5000, 0, 0, 0.681639, 0.731689, 0, 255, 1, 'mod-brill-home town'),
(971344, 971314, 0, 85, 0, 1, 1, 2340.000, 212.600, 37.610, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(971345, 971315, 0, 85, 0, 1, 1, 2337.400, 216.000, 36.870, 1.5700, 0, 0, 0.706825, 0.707388, 0, 255, 1, 'mod-brill-home town'),
(971346, 971315, 0, 85, 0, 1, 1, 2341.900, 216.000, 37.340, 1.5700, 0, 0, 0.706825, 0.707388, 0, 255, 1, 'mod-brill-home town'),
(971347, 971316, 0, 85, 0, 1, 1, 2339.300, 211.800, 38.190, 0.3000, 0, 0, 0.149438, 0.988771, 0, 255, 1, 'mod-brill-home town'),
(971348, 971316, 0, 85, 0, 1, 1, 2340.800, 211.900, 38.360, 1.3000, 0, 0, 0.605186, 0.796084, 0, 255, 1, 'mod-brill-home town'),
(971349, 971316, 0, 85, 0, 1, 1, 2339.500, 213.500, 38.030, 2.3000, 0, 0, 0.912764, 0.408487, 0, 255, 1, 'mod-brill-home town'),
(971350, 971317, 0, 85, 0, 1, 1, 2340.100, 212.600, 38.370, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(971351, 971318, 0, 85, 0, 1, 1, 2348.000, 197.000, 38.770, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(971352, 971319, 0, 85, 0, 1, 1, 2352.500, 197.000, 38.540, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(971353, 971320, 0, 85, 0, 1, 1, 2357.000, 197.000, 38.190, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(971354, 971321, 0, 85, 0, 1, 1, 2362.500, 213.200, 36.550, 1.5700, 0, 0, 0.706825, 0.707388, 0, 255, 1, 'mod-brill-home town'),
(971355, 971322, 0, 85, 0, 1, 1, 2364.900, 213.000, 35.940, 1.2000, 0, 0, 0.564642, 0.825336, 0, 255, 1, 'mod-brill-home town'),
(971356, 971323, 0, 85, 0, 1, 1, 2334.000, 339.500, 35.390, 0.5000, 0, 0, 0.247404, 0.968912, 0, 255, 1, 'mod-brill-home town'),
(971357, 971323, 0, 85, 0, 1, 1, 2339.500, 350.000, 35.810, 1.5000, 0, 0, 0.681639, 0.731689, 0, 255, 1, 'mod-brill-home town'),
(971358, 971323, 0, 85, 0, 1, 1, 2398.000, 380.000, 34.120, 2.5000, 0, 0, 0.948985, 0.315322, 0, 255, 1, 'mod-brill-home town'),
(971359, 971323, 0, 85, 0, 1, 1, 2381.500, 368.500, 37.610, 3.5000, 0, 0, 0.983986, -0.178246, 0, 255, 1, 'mod-brill-home town'),
(971360, 971323, 0, 85, 0, 1, 1, 2420.500, 372.000, 34.550, 4.5000, 0, 0, 0.778073, -0.628174, 0, 255, 1, 'mod-brill-home town'),
(971361, 971323, 0, 85, 0, 1, 1, 2421.000, 392.000, 36.470, 5.5000, 0, 0, 0.381661, -0.924302, 0, 255, 1, 'mod-brill-home town'),
(971362, 971324, 0, 85, 0, 1, 1, 2388.000, 221.000, 34.730, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(971363, 971325, 0, 85, 0, 1, 1, 2895.000, 212.000, 8.010, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(971364, 971326, 0, 85, 0, 1, 1, 2368.500, 196.500, 36.120, 1.0000, 0, 0, 0.479426, 0.877583, 0, 255, 1, 'mod-brill-home town'),
(971365, 971326, 0, 85, 0, 1, 1, 2386.000, 160.000, 34.710, 1.2000, 0, 0, 0.564642, 0.825336, 0, 255, 1, 'mod-brill-home town'),
(971366, 971326, 0, 85, 0, 1, 1, 2398.000, 132.000, 33.460, 1.1000, 0, 0, 0.522687, 0.852525, 0, 255, 1, 'mod-brill-home town'),
(971367, 971327, 0, 85, 0, 1, 1, 2404.000, 113.000, 28.350, 1.3000, 0, 0, 0.605186, 0.796084, 0, 255, 1, 'mod-brill-home town'),
(971368, 971328, 0, 85, 0, 1, 1, 2181.000, 682.000, 33.390, 2.0000, 0, 0, 0.841471, 0.540302, 0, 255, 1, 'mod-brill-home town'),
(971369, 971329, 0, 85, 0, 1, 1, 2889.000, 196.000, 8.080, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(971370, 971330, 0, 85, 0, 1, 1, 2414.000, 386.000, 35.280, 1.0000, 0, 0, 0.479426, 0.877583, 0, 255, 1, 'mod-brill-home town'),
(971371, 971331, 0, 85, 0, 1, 1, 2414.000, 386.000, 35.380, 1.0000, 0, 0, 0.479426, 0.877583, 0, 255, 1, 'mod-brill-home town'),
(971372, 971332, 0, 85, 0, 1, 1, 2396.610, 393.940, 37.200, 2.0940, 0, 0, 0.865927, 0.500171, 0, 255, 1, 'mod-brill-home town'),
(971373, 971332, 0, 85, 0, 1, 1, 2395.740, 393.440, 37.200, 2.0940, 0, 0, 0.865927, 0.500171, 0, 255, 1, 'mod-brill-home town'),
(971374, 971333, 0, 85, 0, 1, 1, 2276.942, 486.421, 34.060, 5.0615, 0, 0, 0.573558, -0.819165, 0, 255, 1, 'mod-brill-home town');
INSERT INTO `brill_town_use` (`go`, `ord`, `cond`, `quest`, `credit`, `text_id`, `marker`, `tele_map`, `tele_x`, `tele_y`, `tele_z`, `tele_o`) VALUES
(971300, 0, 'I971300', 971300, 971314, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971301, 0, 'I971300', 971300, 971315, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971302, 0, 'I971300', 971300, 971316, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971304, 0, 'I971301', 971301, 971321, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971304, 1, 'I971305', 971305, 971333, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971314, 0, 'I971303', 971303, 971328, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971314, 1, 'I971305', 971305, 971333, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971318, 0, 'I971304', 971304, 971329, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971318, 1, 'I971305', 971305, 971334, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971319, 0, 'I971304', 971304, 971329, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971319, 1, 'I971305', 971305, 971334, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971320, 0, 'I971304', 971304, 971329, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971320, 1, 'I971305', 971305, 971334, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971321, 0, 'I971304', 971304, 971330, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971323, 0, 'I971301', 971301, 971318, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971324, 0, 'I971301', 971301, 971319, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971325, 0, 'I971301', 971301, 971320, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971326, 0, 'I971302', 971302, 971322, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971327, 0, 'I971302', 971302, 971323, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971328, 0, 'I971303', 971303, 971326, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971329, 0, 'I971303', 971303, 971327, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971330, 0, 'I971304', 971304, 971331, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000);
INSERT INTO `brill_town_gossip` (`npc`, `ord`, `kind`, `cond`, `icon`, `text`, `text_id`, `action`, `quest`, `credit`, `marker`, `emote`, `reply`, `arg`) VALUES
(971300, 11000, 'greet', 'R971304 R971306', 0, NULL, 971300, '', 0, 0, 0, 0, NULL, 0),
(971300, 11001, 'greet', 'R971304 R971307', 0, NULL, 971301, '', 0, 0, 0, 0, NULL, 0),
(971300, 11002, 'greet', 'R971303', 0, NULL, 971302, '', 0, 0, 0, 0, NULL, 0),
(971300, 11003, 'greet', 'R971302', 0, NULL, 971303, '', 0, 0, 0, 0, NULL, 0),
(971300, 11004, 'greet', 'R971301', 0, NULL, 971304, '', 0, 0, 0, 0, NULL, 0),
(971300, 11005, 'greet', 'R971300', 0, NULL, 971305, '', 0, 0, 0, 0, NULL, 0),
(971300, 11006, 'greet', '', 0, NULL, 971306, '', 0, 0, 0, 0, NULL, 0),
(971300, 11007, 'option', 'I971304', 0, 'The herbs. Brill needs medicine more than ornament.', 0, 'choice', 971304, 971332, 971306, 273, 'Practical. Pellen will be insufferable. ...You\'re right, of course. The herbs get the front and the light, and the flowers can have the corners. Flowers are good at corners. So were most of my relatives.', 0),
(971300, 11008, 'option', 'I971304', 0, 'The flowers. The town has enough that\'s merely useful.', 0, 'choice', 971304, 971332, 971307, 4, 'Flowers! Oh, I knew I liked you. The front beds for colour, then, and Pellen\'s herbs at the back where the light suits them, which is what I shall tell him the reason was.', 0),
(971300, 11009, 'option', 'R971304 O', 1, 'Have you anything green for my house?', 0, 'buy', 0, 0, 971314, 2, 'For the house by the road? Oh, yes. A pot of asters for beside the door, and one of Pellen\'s little glass jars with a fungus garden inside: no water, no light, no fuss. It will outlive us both. Well. It\'ll outlive you. Odo will carry them round.', 7500),
(971301, 11010, 'greet', 'R971302', 0, NULL, 971307, '', 0, 0, 0, 0, NULL, 0),
(971301, 11011, 'greet', 'R971301', 0, NULL, 971308, '', 0, 0, 0, 0, NULL, 0),
(971301, 11012, 'greet', 'R971300', 0, NULL, 971309, '', 0, 0, 0, 0, NULL, 0),
(971301, 11013, 'greet', '', 0, NULL, 971310, '', 0, 0, 0, 0, NULL, 0),
(971301, 11014, 'option', 'I971300', 0, 'I\'ve brought the soil from Edda\'s stakes.', 0, 'credit', 971300, 971317, 0, 1, '(Pellen tips each handful onto a slate, sniffs it, rubs it between finger and thumb, and writes for some time.) Acid. Heavy with bone meal, which is to say bone. Fungal threads throughout. Ordinary flowers would sulk and die here. Gravebloom, nightshade, the paler fungi... Tell Edda it will grow things. Unusual things. If properly treated. Underline \'properly\'.', 0),
(971301, 11015, 'option', 'I971302 R970804', 0, 'Edda sent me to help with the soil treatment.', 0, 'credit', 971302, 971324, 0, 1, 'Look here, under the glass. These pale threads: I\'ve seen them before, in a jar on Holland\'s bench. The parasite from Maudie\'s well. You burned it out of the west channel, I\'m told; these are what washed round by the stream before you did, and settled in Holt\'s drain. They\'re dying already. Holland\'s lime and bitterroot ash, then, cut with bone meal for the roots. Stir. Slowly. There.', 0),
(971301, 11016, 'option', 'I971302 !R970804', 0, 'Edda sent me to help with the soil treatment.', 0, 'credit', 971302, 971324, 0, 1, 'Look here, under the glass. Pale threads, thousands of them, feeding on the rot. Larvae of some kind. Something upstream is laying them, somewhere dark and wet; I\'ll send a jar to Junior Apothecary Holland, who collects this sort of thing. Today we sweeten the ground: lime, ash and bone meal, worked in by hand. Stir. Slowly. There.', 0),
(971302, 11017, 'greet', 'R971306', 0, NULL, 971311, '', 0, 0, 0, 0, NULL, 0),
(971302, 11018, 'greet', '', 0, NULL, 971312, '', 0, 0, 0, 0, NULL, 0),
(971303, 11019, 'greet', 'A971303', 0, NULL, 971313, '', 0, 0, 0, 0, NULL, 0),
(971303, 11020, 'greet', '', 0, NULL, 971314, '', 0, 0, 0, 0, NULL, 0),
(971304, 11021, 'greet', '', 0, NULL, 971315, '', 0, 0, 0, 0, NULL, 0),
(971305, 11022, 'greet', '', 0, NULL, 971316, '', 0, 0, 0, 0, NULL, 0),
(971306, 11023, 'greet', 'R971301', 0, NULL, 971317, '', 0, 0, 0, 0, NULL, 0),
(971306, 11024, 'greet', '', 0, NULL, 971318, '', 0, 0, 0, 0, NULL, 0),
(971307, 11025, 'greet', 'F2', 0, NULL, 971319, '', 0, 0, 0, 0, NULL, 0),
(971307, 11026, 'greet', '', 0, NULL, 971320, '', 0, 0, 0, 0, NULL, 0),
(971308, 11027, 'greet', '', 0, NULL, 971321, '', 0, 0, 0, 0, NULL, 0),
(971309, 11028, 'greet', '', 0, NULL, 971322, '', 0, 0, 0, 0, NULL, 0),
(971310, 11029, 'greet', '', 0, NULL, 971323, '', 0, 0, 0, 0, NULL, 0),
(971311, 11030, 'greet', '', 0, NULL, 971324, '', 0, 0, 0, 0, NULL, 0),
(971312, 11031, 'greet', 'F80', 0, NULL, 971325, '', 0, 0, 0, 0, NULL, 0),
(971312, 11032, 'greet', 'F16', 0, NULL, 971326, '', 0, 0, 0, 0, NULL, 0),
(971312, 11033, 'greet', 'F32', 0, NULL, 971327, '', 0, 0, 0, 0, NULL, 0),
(971312, 11034, 'greet', '', 0, NULL, 971328, '', 0, 0, 0, 0, NULL, 0),
(2132, 11035, 'option', 'R971303 F16', 0, '(Ask her about the lily in Edda\'s memorial bed.)', 0, 'say', 0, 0, 0, 1, 'Edda came to my shop and asked what a moonpetal lily meant. I told her. She went very quiet, and then she planted one for everyone in Brill who never got an answer. I already have mine, my love. It\'s in my locket, pressed flat, where nothing can take it. I check it every morning. I check on you every morning too, from the window. Don\'t tell Edda.', 0),
(2132, 11036, 'option', 'R971303 F32', 0, '(Ask her about the lily in Edda\'s memorial bed.)', 0, 'say', 0, 0, 0, 1, 'The lily in Edda\'s bed? I gave her the cutting. Don\'t look at me like that; friends give each other things. You gave me a lily once and told me what it meant, and I\'ve kept it, and the meaning, exactly as you said it. I keep everything exactly as it\'s said.', 0),
(2132, 11037, 'option', 'R971303 !F16 !F32', 0, '(Ask her about the lily in Edda\'s memorial bed.)', 0, 'say', 0, 0, 0, 1, 'Edda\'s put a moonpetal lily in her memorial bed. Before the plague, a girl in Tirisfal gave one to the one she meant to marry; if they kept it, that meant yes. Edda says hers is for everyone who never got to ask. I think she\'s wrong. I think it\'s for everyone who\'s still waiting for an answer.', 0),
(5688, 11038, 'option', 'I971303', 0, 'Do you remember any flowers from your life before?', 0, 'credit', 971303, 971325, 971308, 1, 'Flowers. Hm. ...White heather and orange blossom. My wedding, in the chapel at Tarren Mill. The heather made me sneeze all through the vows, and Garold laughed so hard the priest stopped. I don\'t remember Garold\'s face. I remember the sneezing.', 0),
(1496, 11039, 'option', 'I971303', 0, 'Do you remember any flowers from your life before?', 0, 'credit', 971303, 971325, 971309, 1, 'Marigolds. I put them on my brother\'s grave every autumn for nine years. He drowned in the Lordamere when we were boys. I used to think the marigolds were for him. There\'s nobody to put them on mine now, and I find I don\'t mind. I think they were for me all along.', 0),
(2134, 11040, 'option', 'I971303', 0, 'Do you remember any flowers from your life before?', 0, 'credit', 971303, 971325, 971310, 1, 'Sweet peas. My mother grew them up the back fence: pink and white, and a purple one she called the bishop. We had to pick them every morning, or they\'d stop flowering. You have to keep taking from them, she said. That was her whole philosophy of children, too.', 0),
(3547, 11041, 'option', 'I971304', 0, 'Edda Graves invites you to the Stillgarden\'s opening.', 0, 'credit', 971304, 971331, 971311, 4, 'A garden opening! On the rise? Will there be mushrooms? There ought to be mushrooms. I\'ll bring mushrooms. The quiet ones.', 0),
(2118, 11042, 'option', 'I971304', 0, 'Edda Graves invites you to the Stillgarden\'s opening.', 0, 'credit', 971304, 971331, 971312, 1, 'The garden? With the herbalist who labels everything twice? I\'ll come. Somebody has to sell him twine for all those bundles, and it may as well be me.', 0),
(10665, 11043, 'option', 'I971304', 0, 'Edda Graves invites you to the Stillgarden\'s opening.', 0, 'credit', 971304, 971331, 971313, 6, 'Me? To a... an opening? Nobody invites me to anything that isn\'t an autopsy. ...I\'ll come. May I look at the drain while I\'m there? I\'ve been curious about the drain.', 0);
UPDATE `creature_template` SET `npcflag` = `npcflag` | 1 WHERE `entry` IN (1496, 2118, 2132, 2134, 3547, 5688, 10665);
INSERT INTO `brill_town_phase` (`bit`, `ord`, `cond`) VALUES
(8, 0, '!R971304');
INSERT INTO `brill_town_stage` (`type`, `value`, `ord`, `cond`) VALUES
(5, 1, 0, 'R971000'),
(5, 2, 0, 'R971300'),
(5, 3, 0, 'R971301'),
(5, 4, 0, 'R971302'),
(5, 5, 0, 'R971303'),
(5, 6, 0, 'R971304'),
(5, 7, 0, 'R971314');
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `Flags`, `RewardXPDifficulty`, `RewardMoney`, `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `AreaDescription`, `QuestCompletionLog`, `RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `ObjectiveText1`, `RequiredNpcOrGo2`, `RequiredNpcOrGoCount2`, `ObjectiveText2`, `RequiredNpcOrGo3`, `RequiredNpcOrGoCount3`, `ObjectiveText3`, `RequiredNpcOrGo4`, `RequiredNpcOrGoCount4`, `ObjectiveText4`, `RewardItem1`, `RewardAmount1`, `RewardItem2`, `RewardAmount2`, `RewardItem3`, `RewardAmount3`, `RewardItem4`, `RewardAmount4`) VALUES
(971300, 2, -1, 8, 159, 0, 4, 2500, 0, 'A Patch of Earth', 'Pull 6 patches of blighted weeds and shift 4 piles of rubble on Holt\'s Rise, Brill\'s eastern edge, take soil from Edda\'s 3 marker stakes to Pellen Moss, then return to Edda Graves.', 'Mind your feet, dear. That\'s gloom weed you\'re standing in, and it bites through boots.$B$BEdda Graves. I sold flowers on the Lordamere road before the plague: roses for weddings, lilies for funerals, violets for apologies. I still know them all, every name. Strange, what stays. I couldn\'t tell you my sister\'s face, but I can tell you a white carnation means remembrance and a yellow one means you\'ve been a fool.$B$BBrill\'s filling up with carts and lumber and hammering, and nobody has anywhere to simply sit. So I asked the Magistrate for this rise. Old Holt kept an orchard up here, once. Now it\'s weeds and broken wall, and Odo, who came with it.$B$BPull the weeds and shift that rubble, would you? I\'ve set three stakes where the beds ought to go; take a handful of soil from each to Pellen Moss. He\'ll tell us whether anything decent will grow in it. He\'ll tell us at length.', '', 'Return to Edda Graves on Holt\'s Rise, at Brill\'s eastern edge.', 971314, 6, 'Blighted weeds pulled', 971315, 4, 'Rubble shifted', 971316, 3, 'Soil taken from the stakes', 971317, 1, 'Pellen Moss\'s assessment', 0, 0, 0, 0, 0, 0, 0, 0),
(971301, 2, -1, 8, 159, 0, 4, 3500, 0, 'What Takes Root', 'Lift 6 gravebloom seedlings from between the stones of Brill\'s cemetery, take a pale spore cap from the grove east of the garden and silt and water from the shore of Brightwater Lake, then plant and water Edda\'s 3 beds. Return to Pellen Moss.', 'Pellen Moss. I study the flora of the Glades: what it does, what it cures, what it kills, and in which order.$B$BYou\'ve seen the soil. Most things would die in it. So we plant what has already learned to live in death. Gravebloom grows in Brill\'s cemetery, between the stones, where nothing else will: a pale little flower that roots in what\'s left of us. Six seedlings, lifted gently, with their soil.$B$BWe\'ll want fungus to turn the ground. There\'s a shaded grove just east of here; look under the trees for a pale spore cap. And Brightwater Lake, north-east of town, has a grey silt along its shore that holds water like a sponge. A jar of the silt and a jar of the lake.$B$BThen plant Edda\'s beds and water them. Gently. Seedlings are like patients, $n. They mostly want to be left alone, but not too alone.', '', 'Return to Pellen Moss in the Stillgarden.', 971318, 6, 'Gravebloom seedlings lifted', 971319, 1, 'Pale spore cap', 971320, 1, 'Brightwater silt and water', 971321, 3, 'Beds planted and watered', 0, 0, 0, 0, 0, 0, 0, 0),
(971302, 2, -1, 9, 159, 0, 5, 4500, 0, 'The Garden\'s Hunger', 'Inspect 3 cracked sections of Holt\'s old drain running from the Stillgarden down to the stream, kill 6 Bloated Drain Toads nesting at its mouth, clear the outlet, and help Pellen Moss mix a treatment for the soil. Then return to Edda Graves.', 'Look at them, dear. Look at the gravebloom.$B$B(Along the beds the pale flowers have curled in on themselves. Their leaves are spotted brown, and the soil has a wet, sour sheen.)$B$BThree days ago they stood up like soldiers. Now they look the way I feel in the mornings. Pellen says it\'s the water. Holt laid a clay drain under this rise when it was an orchard, to carry the rain down to the stream north-east of here. If the drain\'s choked, the rain has nowhere to go but back up, into our beds, carrying whatever\'s been festering down there.$B$BFollow the old pipe down the slope; it\'s cracked open in places, and you can see in. Scrape up a little of the muck for Pellen while you\'re at it. Whatever\'s blocking the bottom, clear it. Then help him brew something to sweeten the ground. I\'m too old to lose a garden twice.', '', 'Return to Edda Graves in the Stillgarden.', 971322, 3, 'Cracked drain inspected', 971313, 6, '', 971323, 1, 'Drain outlet cleared', 971324, 1, 'Soil treatment mixed with Pellen', 858, 2, 0, 0, 0, 0, 0, 0),
(971303, 2, -1, 9, 159, 0, 5, 4000, 0, 'A Bloom for Every Memory', 'Ask three of Brill\'s townsfolk what flowers they remember, take seeds from the old kitchen garden behind Cold Hearth Manor and a moonpetal lily from the shore of Brightwater Lake, and help Willa Fen plant the memorial bed. Then speak with Edda Graves.', 'Can I tell you something? I can\'t smell any of it.$B$BNot the gravebloom, not the nightshade, not whatever Pellen boils in that pot. The apothecaries say it\'s common in the newly risen; the nose goes first. I woke in a pit outside Andorhal four months ago and I haven\'t smelled a thing since, except smoke, once, and I think I imagined that.$B$BSo I water the beds and I pull the weeds, and Edda talks about roses as if they were people she owes money to, and I don\'t see the point. Flowers are for the living. We aren\'t.$B$BShe heard me say it. She didn\'t argue. She said you\'d show me, and walked off. So... show me, I suppose. She says to ask people in town what flowers they remember, fetch seeds from the old garden at Cold Hearth Manor and a moonpetal lily from Brightwater\'s shore, and help me plant a bed for the people we can\'t remember. Her words.', '', 'Speak with Edda Graves in the Stillgarden.', 971325, 3, 'Townsfolk\'s flowers remembered', 971326, 1, 'Seeds from Cold Hearth Manor', 971327, 1, 'Moonpetal lily', 971328, 1, 'Memorial bed planted', 3421, 1, 0, 0, 0, 0, 0, 0),
(971304, 2, -1, 9, 159, 0, 5, 6000, 0, 'The First Harvest', 'Cut the 3 ripe herbs in the Stillgarden\'s glasshouse, set out Pellen Moss\'s stall, lay Edda\'s bouquet on the plague graves at the north end of the cemetery and invite Hamlin Atkins, Abigail Shiel and Junior Apothecary Holland, then answer Edda\'s question.', 'The frame\'s up, the drain runs clean, and this morning Pellen stood among the seedlings and said, I quote, \'adequate.\' I nearly fainted.$B$BIt\'s time, dear. The first harvest. Nothing grand: the peacebloom, the silverleaf and the first of the gravebloom, cut at the stem the way I showed you. Help Pellen set out his stall; he means to sell herbs to the town, and he has never sold anything in his life, or since.$B$BThen the invitations. The first flowers always went to the cemetery, in my day: the dead are a town\'s oldest residents, and we\'re hardly in a position to argue. Lay this bouquet on the plague graves at the north end. Then Hamlin Atkins, and Abigail Shiel, and young Holland, who\'s never been invited to anything without a corpse at it.$B$BAnd come and find me before the gathering. I have a question to put to you, and I\'ve been putting it off.', '', 'Return to Edda Graves in the Stillgarden.', 971329, 3, 'Ripe herbs cut', 971330, 1, 'Pellen\'s stall set out', 971331, 4, 'Bouquet laid and guests invited', 971332, 1, 'Edda\'s question answered', 22250, 1, 0, 0, 0, 0, 0, 0),
(971305, 2, -1, 9, 159, 4096, 2, 1200, 0, 'A Garden Is Kept', 'Tend 4 of the Stillgarden\'s beds and cut 3 ripe herbs in the glasshouse, then return to Edda Graves.', 'Morning, dear. Or evening. I\'ve stopped keeping track; the plants keep it for me.$B$BA garden isn\'t made, it\'s kept. Pull what\'s crept back into the beds, pinch the dead heads off the gravebloom, and see what\'s ripe under the glass. Not too much, mind. We take a little and leave the rest, or there\'s nothing next week. That\'s gardening, and good husbandry, and most of what I know about people as well.$B$BOdo will tell you which beds want you. He talks to them, and they answer him, he says. I don\'t argue with Odo before noon.', '', 'Return to Edda Graves in the Stillgarden.', 971333, 4, 'Beds tended', 971334, 3, 'Ripe herbs cut', 0, 0, '', 0, 0, '', 2447, 2, 765, 2, 0, 0, 0, 0),
(971306, 2, 1, 1, -1, 0, 0, 0, 0, '[practical]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971307, 2, 1, 1, -1, 0, 0, 0, 0, '[decorative]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971308, 2, 1, 1, -1, 0, 0, 0, 0, '[remembered_renee]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971309, 2, 1, 1, -1, 0, 0, 0, 0, '[remembered_dillinger]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971310, 2, 1, 1, -1, 0, 0, 0, 0, '[remembered_winters]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971311, 2, 1, 1, -1, 0, 0, 0, 0, '[invited_hamlin]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971312, 2, 1, 1, -1, 0, 0, 0, 0, '[invited_abigail]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971313, 2, 1, 1, -1, 0, 0, 0, 0, '[invited_holland]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971314, 2, 1, 1, -1, 0, 0, 0, 0, '[house_set]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`, `SpecialFlags`) VALUES (971300, 971000, 0), (971301, 971300, 0), (971302, 971301, 0), (971303, 971302, 0), (971304, 971303, 0), (971305, 971304, 1);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`) VALUES
(971300, 1, '(Edda reads Pellen\'s notes twice, her lips moving.)$B$BAcid. Grave-rich. Full of things that died and some that didn\'t quite finish. \'Capable of supporting unusual varieties, if properly treated.\' Oh, I could kiss him. I won\'t. Neither of us would enjoy it.$B$BDo you know what that means, dear? It means it\'s a garden. It always was. It was only waiting for somebody to stop walking past it.'),
(971301, 1, '(Pellen kneels by the beds and says nothing for a long while, which you gather is praise.)$B$BThey\'ve taken. You see the gravebloom leaning toward the light? It does that the first night. In a week it\'ll turn its back on the sun entirely, as is proper.$B$BI\'ll confess something. When Edda said \'a garden\', I thought she meant to plant a memory and watch it die. But this is botany. This, I can write down.'),
(971302, 1, '(Edda presses her hand flat on the treated soil and holds it there.)$B$BIt\'s warm. Is that daft? It feels warm.$B$BToads, you say. A whole nest of them squatting in Holt\'s pipe, and everything they left behind running back up into my beds. I\'ve had lodgers like that.$B$BPellen wants a frame over the seedlings now, to keep the worst of the rain off while the ground mends. Rudd Carver says he can spare the timber if somebody else finds the glass. Somebody else is usually me.'),
(971303, 1, '(Willa is still kneeling at the memorial bed. She has a hand cupped around the lily, as if to keep the wind off it.)$B$BShe\'s been there an hour. She won\'t say why. Renee\'s wedding flowers, perhaps, or Dillinger\'s marigolds, or Mrs. Winters\' mother\'s sweet peas. It doesn\'t matter which.$B$B\'You can\'t smell them either,\' she said to me. Not properly, not for years, I told her. That isn\'t what they\'re for any more, dear. They\'re for remembering on purpose, so you don\'t only remember by accident.$B$BShe didn\'t answer. But she asked me what the lily was called. Twice.'),
(971304, 1, '(The rise is full: Hamlin explaining mushrooms to anyone who stands still, Abigail Shiel pricing Pellen\'s stall, Holland on his knees by the drain. Selina Weston came up from the lane uninvited and pretended she was passing. Odo walks among them, telling the plants who everyone is.)$B$BLook at them, $n. Half of them can\'t smell a thing, and they came anyway.$B$B(Edda raises a cup of something that may once have been elderflower cordial.)$B$BThey may be dead, but that doesn\'t mean they should spend eternity somewhere ugly.'),
(971305, 1, 'Lovely. You\'ve a gardener\'s hands, $n, whatever else you\'ve done with them.$B$BTake a share of the harvest. It\'s yours; you grew it, in a manner of speaking. In a manner of speaking, I\'m still a florist. Pellen will want to weigh it first. Let him. It makes him happy, in his way.');
INSERT INTO `quest_request_items` (`ID`, `EmoteOnComplete`, `EmoteOnIncomplete`, `CompletionText`) VALUES
(971300, 1, 1, 'Weeds first, then stones, then soil. Gardening is mostly the same three things, in that order, forever.'),
(971301, 1, 1, 'Seedlings, spores, silt, water, then the beds. I\'ve written it down. I write everything down.'),
(971302, 1, 1, 'The beds are worse this morning. Pellen\'s taken to whispering at them. That\'s Odo\'s job.'),
(971303, 1, 1, 'Has anyone remembered a flower yet? I asked a Deathguard once. He said \'red\'.'),
(971304, 1, 1, 'At the stem, dear, not the root. We\'re harvesting, not burying. That\'s the other place.'),
(971305, 1, 1, 'Four beds, three herbs. The gravebloom will try to nip you. It\'s affectionate.');
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES (971300, 971300), (971301, 971301), (971300, 971302), (971303, 971303), (971300, 971304), (971300, 971305);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES (971300, 971300), (971301, 971301), (971300, 971302), (971300, 971303), (971300, 971304), (971300, 971305);

-- The Surgeon's Hall
INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`) VALUES (971409, 0, 1251, 0, 0, 0), (971409, 1, 2581, 0, 0, 0), (971409, 2, 3530, 0, 0, 0), (971409, 3, 6452, 0, 0, 0), (971409, 4, 2320, 0, 0, 0), (971409, 5, 2321, 0, 0, 0), (971409, 6, 3371, 0, 0, 0), (971409, 7, 118, 0, 0, 0), (971409, 8, 858, 0, 0, 0), (971409, 9, 2458, 0, 0, 0), (971409, 10, 5997, 0, 0, 0), (971409, 11, 3382, 0, 0, 0), (971409, 12, 2324, 0, 0, 0), (971409, 13, 4340, 0, 0, 0), (971409, 14, 3531, 0, 0, 0), (971409, 15, 2456, 0, 0, 0);
INSERT INTO `creature_template` (`entry`, `name`, `subname`, `gossip_menu_id`, `minlevel`, `maxlevel`, `faction`, `npcflag`, `speed_walk`, `speed_run`, `unit_class`, `unit_flags`, `type`, `rank`, `HealthModifier`, `DamageModifier`, `mingold`, `maxgold`, `flags_extra`, `AIName`, `ScriptName`) VALUES
(971400, 'Surgeon Elspeth Rane', 'Head Surgeon', 0, 30, 30, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971401, 'Timm Vetch', 'Apprentice Surgeon', 0, 18, 18, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971402, 'Fenwick Pike', 'Medical Orderly', 0, 22, 22, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971403, 'Jory Haskett', 'Carter', 0, 12, 12, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971404, 'Old Nan Thistle', 'Peddler', 0, 12, 12, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971405, 'Corwin Teague', 'Deathguard Recruit', 0, 10, 10, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971406, 'Agnes Morrow', 'Patient', 0, 14, 14, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971407, 'Agnes Morrow', NULL, 0, 14, 14, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971408, 'Agnes Morrow', NULL, 0, 14, 14, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971409, 'Fenwick Pike', 'Medical Orderly', 0, 22, 22, 68, 129, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971410, 'Timm Vetch', 'Apprentice Surgeon', 0, 18, 18, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971411, 'Timm Vetch', 'Apprentice Surgeon', 0, 18, 18, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971412, 'Patient', NULL, 0, 10, 10, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971413, 'Patient', NULL, 0, 10, 10, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971414, 'Apothecary Tobin Crell', 'Royal Apothecary Society', 0, 25, 25, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971415, 'Builder\'s Yard Laborer', NULL, 0, 15, 15, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971416, 'Oswin Thatcher', 'Carpenter', 0, 25, 25, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971417, 'Carolai Anise', 'Alchemy Trainer', 0, 20, 20, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971418, 'Injured travellers spoken with', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971419, 'Linen and splints', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971420, 'Surgical instruments recovered', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971421, 'Vacant farmhouse inspected', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971422, 'Oak tables recovered', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971423, 'Needles and thread', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971424, 'Glass and cleaning spirit', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971425, 'Medical cabinets put together', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971426, 'Articulated joints salvaged', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971427, 'Leather straps and gears', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971428, 'The clockmaker\'s hand', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971429, 'Prosthetic assembled and tested', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971430, 'Proposal and case records read', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971431, 'Patients consulted', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971432, 'Apothecary Johaan consulted', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971433, 'The patients\' charter written', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971434, 'Examination table prepared', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971435, 'Agnes\'s leg cleaned and splinted', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971436, 'Brace fitted with Timm', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971437, 'Instruments handed to Elspeth', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971438, 'Linen from Mrs. Winters', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971439, 'Thread from Abigail Shiel', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971440, 'Deathguard Dillinger\'s shoulder closed', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971441, 'Hamlin Atkins\'s hand stitched', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', '');
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`) VALUES
(971400, 0, 4108, 1, 1),
(971401, 0, 2653, 1, 1),
(971402, 0, 2637, 1, 1),
(971403, 0, 3880, 1, 1),
(971404, 0, 2663, 1, 1),
(971405, 0, 3863, 1, 1),
(971406, 0, 4041, 1, 1),
(971407, 0, 4041, 1, 1),
(971408, 0, 4041, 1, 1),
(971409, 0, 2637, 1, 1),
(971410, 0, 2653, 1, 1),
(971411, 0, 2653, 1, 1),
(971412, 0, 2644, 1, 1),
(971412, 1, 2658, 1, 1),
(971412, 2, 2661, 1, 1),
(971412, 3, 2673, 1, 1),
(971413, 0, 2644, 1, 1),
(971413, 1, 2658, 1, 1),
(971413, 2, 2661, 1, 1),
(971413, 3, 2673, 1, 1),
(971414, 0, 1965, 1, 1),
(971415, 0, 2655, 1, 1),
(971415, 1, 2641, 1, 1),
(971415, 2, 2645, 1, 1),
(971416, 0, 1638, 1, 1),
(971417, 0, 1601, 1, 1),
(971418, 0, 11686, 1, 1),
(971419, 0, 11686, 1, 1),
(971420, 0, 11686, 1, 1),
(971421, 0, 11686, 1, 1),
(971422, 0, 11686, 1, 1),
(971423, 0, 11686, 1, 1),
(971424, 0, 11686, 1, 1),
(971425, 0, 11686, 1, 1),
(971426, 0, 11686, 1, 1),
(971427, 0, 11686, 1, 1),
(971428, 0, 11686, 1, 1),
(971429, 0, 11686, 1, 1),
(971430, 0, 11686, 1, 1),
(971431, 0, 11686, 1, 1),
(971432, 0, 11686, 1, 1),
(971433, 0, 11686, 1, 1),
(971434, 0, 11686, 1, 1),
(971435, 0, 11686, 1, 1),
(971436, 0, 11686, 1, 1),
(971437, 0, 11686, 1, 1),
(971438, 0, 11686, 1, 1),
(971439, 0, 11686, 1, 1),
(971440, 0, 11686, 1, 1),
(971441, 0, 11686, 1, 1);
INSERT INTO `creature` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(971400, 971400, 0, 85, 0, 1, 1, 2313.900, 368.300, 33.970, 2.7200, 60, 0, 0, 'mod-brill-home town'),
(971401, 971401, 0, 85, 0, 1, 16, 2318.200, 364.800, 33.780, 3.7600, 60, 0, 0, 'mod-brill-home town'),
(971402, 971402, 0, 85, 0, 1, 16, 2321.100, 361.100, 33.660, 2.8900, 60, 0, 0, 'mod-brill-home town'),
(971403, 971403, 0, 85, 0, 1, 16, 2318.000, 356.500, 34.160, 0.4500, 60, 0, 0, 'mod-brill-home town'),
(971404, 971404, 0, 85, 0, 1, 16, 2323.200, 357.100, 33.780, 2.1900, 60, 0, 0, 'mod-brill-home town'),
(971405, 971405, 0, 85, 0, 1, 16, 2321.300, 352.500, 34.490, 1.5000, 60, 0, 0, 'mod-brill-home town'),
(971406, 971406, 0, 85, 0, 1, 16, 2332.500, 388.400, 33.980, 4.1100, 60, 0, 0, 'mod-brill-home town'),
(971407, 971407, 0, 85, 0, 1, 1, 2310.200, 369.100, 34.020, 4.6400, 60, 0, 0, 'mod-brill-home town'),
(971408, 971408, 0, 85, 0, 1, 1, 2295.500, 304.000, 35.280, 2.2000, 60, 0, 0, 'mod-brill-home town'),
(971409, 971409, 0, 85, 0, 1, 1, 2322.350, 372.520, 34.390, 4.1140, 60, 0, 0, 'mod-brill-home town'),
(971410, 971410, 0, 85, 0, 1, 1, 2324.670, 371.670, 34.390, 5.6840, 60, 0, 0, 'mod-brill-home town'),
(971411, 971411, 0, 85, 0, 1, 1, 2188.060, 280.380, 42.100, 1.3100, 60, 0, 0, 'mod-brill-home town'),
(971412, 971412, 0, 85, 0, 1, 1, 2324.030, 378.880, 34.390, 2.5430, 60, 0, 0, 'mod-brill-home town'),
(971413, 971413, 0, 85, 0, 1, 1, 2321.550, 375.250, 34.390, 2.5430, 60, 0, 0, 'mod-brill-home town'),
(971414, 971414, 0, 85, 0, 1, 1, 2308.700, 369.500, 34.040, 6.0300, 60, 0, 0, 'mod-brill-home town'),
(971415, 971415, 0, 85, 0, 1, 16, 2312.900, 382.400, 34.100, 5.6800, 60, 2, 1, 'mod-brill-home town'),
(971416, 971415, 0, 85, 0, 1, 16, 2327.600, 363.200, 33.580, 2.5400, 60, 2, 1, 'mod-brill-home town'),
(971417, 971416, 0, 85, 0, 1, 16, 2310.800, 377.100, 34.180, 6.2100, 60, 0, 0, 'mod-brill-home town'),
(971418, 971417, 0, 85, 0, 1, 1, 2320.400, 364.500, 33.700, 3.2400, 60, 0, 0, 'mod-brill-home town');
INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `Data0`, `Data1`, `ScriptName`) VALUES
(971400, 33, 8020, 'Vacant Farmhouse', 1, 0, 0, ''),
(971401, 33, 8010, 'Surgeon\'s Hall', 1, 0, 0, ''),
(971402, 10, 1248, 'Boarded Door', 1.3, 0, 971400, 'go_brill_town'),
(971403, 5, 6449, 'Surgeon\'s Crate', 0.8, 0, 0, ''),
(971404, 10, 7524, 'Overturned Wagon', 1, 0, 971400, 'go_brill_town'),
(971405, 5, 7873, 'Treatment Tent', 1, 0, 0, ''),
(971406, 5, 1109, 'Lumber', 1, 0, 0, ''),
(971407, 10, 1108, 'Cabinet Parts', 1, 0, 971401, 'go_brill_town'),
(971408, 10, 221, 'Heavy Oak Table', 1, 0, 971401, 'go_brill_town'),
(971409, 10, 8073, 'Examination Table', 0.85, 0, 971404, 'go_brill_town'),
(971410, 5, 151, 'Oak Table', 0.8, 0, 0, ''),
(971411, 5, 4, 'Medical Cabinet', 1, 0, 0, ''),
(971412, 5, 581, 'Side Table', 1, 0, 0, ''),
(971413, 5, 4072, 'Bottles', 1, 0, 0, ''),
(971414, 10, 1248, 'Practice Frame', 0.8, 0, 971402, 'go_brill_town'),
(971415, 10, 7000, 'Rusted Mill Gearing', 1, 0, 971402, 'go_brill_town'),
(971416, 10, 7731, 'Clockmaker\'s Hand', 0.5, 0, 971402, 'go_brill_town'),
(971417, 5, 234, 'Timm\'s Workbench', 1, 0, 0, ''),
(971418, 10, 7751, 'The Society\'s Proposal', 1.5, 0, 971403, 'go_brill_town'),
(971419, 10, 1, 'Case Records', 1.3, 0, 971403, 'go_brill_town'),
(971420, 10, 6508, 'Instrument Tray', 0.7, 0, 971404, 'go_brill_town'),
(971421, 5, 3471, 'Ward Bed', 0.75, 0, 0, ''),
(971422, 5, 8073, 'Examination Table', 0.8, 0, 0, ''),
(971423, 5, 234, 'Timm\'s Workbench', 1, 0, 0, ''),
(971424, 5, 4, 'Medical Cabinet', 1, 0, 0, ''),
(971425, 5, 187, 'Shelf', 1, 0, 0, ''),
(971426, 5, 4073, 'Bottles', 1, 0, 0, ''),
(971427, 5, 5112, 'Washbasin', 1, 0, 0, ''),
(971428, 5, 7979, 'Forsaken Banner', 1, 0, 0, ''),
(971429, 7, 682, 'Bench', 1, 1, 1, ''),
(971430, 5, 7494, 'Carolai\'s Basket', 1, 0, 0, ''),
(971431, 5, 6449, 'First-Aid Cabinet', 0.55, 0, 0, ''),
(971432, 5, 5112, 'Washbasin', 0.6, 0, 0, ''),
(971433, 5, 7233, 'Varden\'s Anatomy of the Risen', 0.35, 0, 0, '');
INSERT INTO `gameobject_template_addon` (`entry`, `faction`, `flags`) VALUES (971400, 0, 32), (971401, 0, 32), (971402, 0, 4), (971404, 0, 4), (971407, 0, 4), (971408, 0, 4), (971409, 0, 4), (971414, 0, 4), (971415, 0, 4), (971416, 0, 4), (971418, 0, 4), (971419, 0, 4), (971420, 0, 4);
INSERT INTO `gameobject` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`, `animprogress`, `state`, `Comment`) VALUES
(971400, 971400, 0, 85, 0, 1, 16, 2324.000, 376.000, 30.290, 5.6845, 0, 0, 0.294892, -0.955531, 0, 255, 1, 'mod-brill-home town'),
(971401, 971401, 0, 85, 0, 1, 1, 2324.000, 376.000, 30.290, 5.6845, 0, 0, 0.294892, -0.955531, 0, 255, 1, 'mod-brill-home town'),
(971402, 971402, 0, 85, 0, 1, 16, 2319.450, 371.110, 34.390, 5.6840, 0, 0, 0.295131, -0.955457, 0, 255, 1, 'mod-brill-home town'),
(971403, 971403, 0, 85, 0, 1, 16, 2316.700, 363.500, 33.690, 6.0300, 0, 0, 0.126255, -0.991998, 0, 255, 1, 'mod-brill-home town'),
(971404, 971404, 0, 85, 0, 1, 1, 2092.000, 146.000, 34.970, 2.6000, 0, 0, 0.963558, 0.267499, 0, 255, 1, 'mod-brill-home town'),
(971405, 971405, 0, 85, 0, 1, 16, 2320.600, 355.900, 33.950, 5.6800, 0, 0, 0.297041, -0.954865, 0, 255, 1, 'mod-brill-home town'),
(971406, 971406, 0, 85, 0, 1, 16, 2315.400, 386.100, 33.930, 0.9700, 0, 0, 0.466208, 0.884675, 0, 255, 1, 'mod-brill-home town'),
(971407, 971407, 0, 85, 0, 1, 16, 2325.500, 363.100, 33.440, 5.6800, 0, 0, 0.297041, -0.954865, 0, 255, 1, 'mod-brill-home town'),
(971408, 971408, 0, 85, 0, 1, 1, 2920.000, 400.000, 30.990, 0.6000, 0, 0, 0.295520, 0.955336, 0, 255, 1, 'mod-brill-home town'),
(971409, 971408, 0, 85, 0, 1, 1, 2926.000, 406.000, 31.030, 2.1000, 0, 0, 0.867423, 0.497571, 0, 255, 1, 'mod-brill-home town'),
(971410, 971409, 0, 85, 0, 1, 16, 2311.000, 365.800, 33.800, 0.9700, 0, 0, 0.466208, 0.884675, 0, 255, 1, 'mod-brill-home town'),
(971411, 971410, 0, 85, 0, 1, 16, 2308.100, 361.600, 33.860, 5.6800, 0, 0, 0.297041, -0.954865, 0, 255, 1, 'mod-brill-home town'),
(971412, 971411, 0, 85, 0, 1, 16, 2312.900, 371.200, 34.000, 4.1100, 0, 0, 0.885046, -0.465504, 0, 255, 1, 'mod-brill-home town'),
(971413, 971411, 0, 85, 0, 1, 16, 2322.400, 364.800, 33.540, 4.1100, 0, 0, 0.885046, -0.465504, 0, 255, 1, 'mod-brill-home town'),
(971414, 971412, 0, 85, 0, 1, 16, 2313.300, 363.900, 33.720, 5.6800, 0, 0, 0.297041, -0.954865, 0, 255, 1, 'mod-brill-home town'),
(971415, 971412, 0, 85, 0, 1, 16, 2308.800, 367.200, 33.870, 5.6800, 0, 0, 0.297041, -0.954865, 0, 255, 1, 'mod-brill-home town'),
(971416, 971413, 0, 85, 0, 1, 16, 2313.800, 364.300, 34.850, 0.9700, 0, 0, 0.466208, 0.884675, 0, 255, 1, 'mod-brill-home town'),
(971417, 971414, 0, 85, 0, 1, 16, 2334.000, 368.000, 33.770, 0.9700, 0, 0, 0.466208, 0.884675, 0, 255, 1, 'mod-brill-home town'),
(971418, 971415, 0, 85, 0, 1, 1, 2790.000, 805.000, 113.250, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(971419, 971415, 0, 85, 0, 1, 1, 2805.000, 825.000, 111.840, 1.3000, 0, 0, 0.605186, 0.796084, 0, 255, 1, 'mod-brill-home town'),
(971420, 971415, 0, 85, 0, 1, 1, 2780.000, 830.000, 111.840, 2.6000, 0, 0, 0.963558, 0.267499, 0, 255, 1, 'mod-brill-home town'),
(971421, 971416, 0, 85, 0, 1, 1, 2770.000, 806.000, 112.990, 4.0000, 0, 0, 0.909297, -0.416147, 0, 255, 1, 'mod-brill-home town'),
(971422, 971417, 0, 85, 0, 1, 16, 2331.300, 364.400, 33.690, 5.6800, 0, 0, 0.297041, -0.954865, 0, 255, 1, 'mod-brill-home town'),
(971423, 971418, 0, 85, 0, 1, 16, 2313.300, 363.900, 34.840, 0.9700, 0, 0, 0.466208, 0.884675, 0, 255, 1, 'mod-brill-home town'),
(971424, 971419, 0, 85, 0, 1, 16, 2335.100, 372.700, 33.650, 5.6800, 0, 0, 0.297041, -0.954865, 0, 255, 1, 'mod-brill-home town'),
(971425, 971420, 0, 85, 0, 1, 16, 2308.800, 367.200, 34.990, 0.9700, 0, 0, 0.466208, 0.884675, 0, 255, 1, 'mod-brill-home town'),
(971426, 971421, 0, 85, 0, 1, 1, 2322.210, 379.760, 34.390, 0.9720, 0, 0, 0.467093, 0.884208, 0, 255, 1, 'mod-brill-home town'),
(971427, 971421, 0, 85, 0, 1, 1, 2319.790, 376.210, 34.390, 0.9720, 0, 0, 0.467093, 0.884208, 0, 255, 1, 'mod-brill-home town'),
(971428, 971422, 0, 85, 0, 1, 1, 2325.940, 375.650, 34.390, 5.6840, 0, 0, 0.295131, -0.955457, 0, 255, 1, 'mod-brill-home town'),
(971429, 971423, 0, 85, 0, 1, 1, 2325.750, 370.930, 34.390, 5.6840, 0, 0, 0.295131, -0.955457, 0, 255, 1, 'mod-brill-home town'),
(971430, 971424, 0, 85, 0, 1, 1, 2329.950, 377.270, 34.390, 4.1140, 0, 0, 0.884113, -0.467273, 0, 255, 1, 'mod-brill-home town'),
(971431, 971425, 0, 85, 0, 1, 1, 2323.320, 369.680, 34.390, 0.9720, 0, 0, 0.467093, 0.884208, 0, 255, 1, 'mod-brill-home town'),
(971432, 971426, 0, 85, 0, 1, 1, 2323.440, 369.850, 36.170, 0.9720, 0, 0, 0.467093, 0.884208, 0, 255, 1, 'mod-brill-home town'),
(971433, 971427, 0, 85, 0, 1, 1, 2326.580, 378.360, 34.390, 5.6840, 0, 0, 0.295131, -0.955457, 0, 255, 1, 'mod-brill-home town'),
(971434, 971428, 0, 85, 0, 1, 1, 2319.900, 366.800, 33.680, 4.1100, 0, 0, 0.885046, -0.465504, 0, 255, 1, 'mod-brill-home town'),
(971435, 971429, 0, 85, 0, 1, 1, 2310.000, 368.000, 33.880, 0.9700, 0, 0, 0.466208, 0.884675, 0, 255, 1, 'mod-brill-home town'),
(971436, 971430, 0, 85, 0, 1, 1, 2321.300, 364.500, 33.570, 5.6800, 0, 0, 0.297041, -0.954865, 0, 255, 1, 'mod-brill-home town'),
(971437, 971431, 0, 85, 0, 1, 1, 2268.711, 482.574, 34.060, 5.0615, 0, 0, 0.573558, -0.819165, 0, 255, 1, 'mod-brill-home town'),
(971438, 971432, 0, 85, 0, 1, 1, 2270.212, 478.597, 34.060, 0.3491, 0, 0, 0.173670, 0.984804, 0, 255, 1, 'mod-brill-home town'),
(971439, 971433, 0, 85, 0, 1, 1, 2268.711, 482.574, 35.030, 5.2360, 0, 0, 0.499980, -0.866037, 0, 255, 1, 'mod-brill-home town');
INSERT INTO `brill_town_use` (`go`, `ord`, `cond`, `quest`, `credit`, `text_id`, `marker`, `tele_map`, `tele_x`, `tele_y`, `tele_z`, `tele_o`) VALUES
(971402, 0, 'I971400', 971400, 971421, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971404, 0, 'I971400', 971400, 971420, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971407, 0, 'I971401', 971401, 971425, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971408, 0, 'I971401', 971401, 971422, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971409, 0, 'I971404', 971404, 971434, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971414, 0, 'I971402', 971402, 971429, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971415, 0, 'I971402', 971402, 971426, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971416, 0, 'I971402', 971402, 971428, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971418, 0, 'I971403', 971403, 971430, 971400, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971419, 0, 'I971403', 971403, 971430, 971401, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971420, 0, 'I971404', 971404, 971437, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000);
INSERT INTO `brill_town_gossip` (`npc`, `ord`, `kind`, `cond`, `icon`, `text`, `text_id`, `action`, `quest`, `credit`, `marker`, `emote`, `reply`, `arg`) VALUES
(971400, 12000, 'greet', 'R971404 R970405 D2', 0, NULL, 971402, '', 0, 0, 0, 0, NULL, 0),
(971400, 12001, 'greet', 'R971404 R970406 D2', 0, NULL, 971403, '', 0, 0, 0, 0, NULL, 0),
(971400, 12002, 'greet', 'R971404 R970407 D2', 0, NULL, 971404, '', 0, 0, 0, 0, NULL, 0),
(971400, 12003, 'greet', 'R971404 R971406', 0, NULL, 971405, '', 0, 0, 0, 0, NULL, 0),
(971400, 12004, 'greet', 'R971404 R971407', 0, NULL, 971406, '', 0, 0, 0, 0, NULL, 0),
(971400, 12005, 'greet', 'A971404', 0, NULL, 971407, '', 0, 0, 0, 0, NULL, 0),
(971400, 12006, 'greet', 'R971403', 0, NULL, 971408, '', 0, 0, 0, 0, NULL, 0),
(971400, 12007, 'greet', 'R971402', 0, NULL, 971409, '', 0, 0, 0, 0, NULL, 0),
(971400, 12008, 'greet', 'R971401', 0, NULL, 971410, '', 0, 0, 0, 0, NULL, 0),
(971400, 12009, 'greet', 'R971400', 0, NULL, 971411, '', 0, 0, 0, 0, NULL, 0),
(971400, 12010, 'greet', '', 0, NULL, 971412, '', 0, 0, 0, 0, NULL, 0),
(971400, 12011, 'option', 'I971403', 0, 'No research at all. This hall heals; it doesn\'t experiment.', 0, 'choice', 971403, 971433, 971406, 273, 'Clinical, then. No trials, no tinctures, no \'promising remedies\'. The Society can find its volunteers somewhere else; I\'ll give them directions. The clause reads: \'No research shall be done within these walls.\' Short. I like short.', 0),
(971400, 12012, 'option', 'I971403', 0, 'Allow research, but only on those who freely agree, and under your eye.', 0, 'choice', 971403, 971433, 971407, 1, 'Voluntary, supervised, and stopped the moment anyone says stop. I\'ll stand at the foot of every bed, and their apothecary will sign the register in front of the patient, not behind a door. It\'s more than they\'d have offered and less than they wanted. That\'s usually where the right answer lives.', 0),
(971400, 12013, 'option', 'R971404 R971406', 0, '(Ask about the charter.)', 0, 'say', 0, 0, 0, 1, 'It\'s nailed to the door, at the height of an apothecary\'s eyes. \'No research shall be done within these walls.\' Faranell\'s office wrote back to ask whether that included observation. I wrote back: yes.', 0),
(971400, 12014, 'option', 'R971404 R971407', 0, '(Ask about the charter.)', 0, 'say', 0, 0, 0, 1, 'Nailed to the door. Consent freely given, freely withdrawn, the surgeon present. Crell comes of a morning, signs, asks, is refused, signs again. He\'s learning. Slowly. Like a dog that can read.', 0),
(971400, 12015, 'option', 'R971404 O', 1, 'Could the hall spare anything for my house?', 0, 'buy', 0, 0, 971416, 1, 'For your house. A first-aid cabinet, stocked; a washbasin, so you stop bleeding on your sheets; and Varden\'s Anatomy of the Risen, the only useful book the Society ever printed. Fenwick will carry them round. Read chapter four before you need it.', 12000),
(971401, 12016, 'greet', 'R971402', 0, NULL, 971413, '', 0, 0, 0, 0, NULL, 0),
(971401, 12017, 'greet', 'A971400', 0, NULL, 971414, '', 0, 0, 0, 0, NULL, 0),
(971401, 12018, 'greet', '', 0, NULL, 971415, '', 0, 0, 0, 0, NULL, 0),
(971401, 12019, 'option', '!R971402', 0, 'What happened to your arm?', 0, 'say', 0, 0, 0, 1, 'Eight months ago. After I died, mind; not before. A beam came down in the Apothecarium\'s cellars. By the time they dug me out it was grey to the shoulder. We don\'t heal, $n. People think that because we\'re dead, nothing more can happen to us. Everything can still happen to us. It just doesn\'t get better.', 0),
(971401, 12020, 'option', 'I971404', 0, 'Let\'s fit Agnes\'s brace.', 0, 'credit', 971404, 971436, 0, 1, 'Strap one above the knee. Strap two below. The hinge sits on the joint... not there, there. (The brace clicks into place. Timm checks every buckle twice, then a third time when Elspeth looks over.) It\'s not a hand. It\'s better than a hand. It doesn\'t twitch.', 0),
(971410, 12021, 'greet', '', 0, NULL, 971416, '', 0, 0, 0, 0, NULL, 0),
(971411, 12022, 'greet', '', 0, NULL, 971417, '', 0, 0, 0, 0, NULL, 0),
(971402, 12023, 'greet', '', 0, NULL, 971418, '', 0, 0, 0, 0, NULL, 0),
(971402, 12024, 'option', 'I971404', 0, 'I\'m ready to help with Agnes\'s leg.', 0, 'credit', 971404, 971435, 0, 1, 'Hold here. Both hands. Don\'t squeeze; steady. (Fenwick cuts the old wrappings away, washes the wound with something that smells like a forge, picks grit and splinters out with a long needle, and binds the leg straight between two boards, humming an old marching tune the whole time.) There. She\'ll hold. They mostly do, if you give them something to hold on to.', 0),
(971409, 12025, 'greet', 'R971407', 0, NULL, 971419, '', 0, 0, 0, 0, NULL, 0),
(971409, 12026, 'greet', '', 0, NULL, 971420, '', 0, 0, 0, 0, NULL, 0),
(971403, 12027, 'greet', '', 0, NULL, 971421, '', 0, 0, 0, 0, NULL, 0),
(971404, 12028, 'greet', '', 0, NULL, 971422, '', 0, 0, 0, 0, NULL, 0),
(971405, 12029, 'greet', '', 0, NULL, 971423, '', 0, 0, 0, 0, NULL, 0),
(971403, 12030, 'option', 'I971400', 0, 'How are you holding up?', 0, 'credit', 971400, 971418, 971408, 1, 'Holding up? Holding on, more like. Worgen, out of the Silverpine trees, three of them. Went for the horse first, then me. Took a good bite of this arm and spat it out. Apparently I don\'t taste right any more. First compliment I\'ve had in years.', 0),
(971404, 12031, 'option', 'I971400', 0, 'How are you holding up?', 0, 'credit', 971400, 971418, 971409, 1, 'Ribs. The cart went over on me when the horse bolted. I can hear them grinding when I breathe, which is a funny thing to hear when you don\'t need to breathe. The surgeon says I\'m lucky. I\'m a hundred and four, counting the dead years. I\'m owed some luck.', 0),
(971405, 12032, 'option', 'I971400', 0, 'How are you holding up?', 0, 'credit', 971400, 971418, 971410, 1, 'Three fingers. I can\'t feel them, which is right, I suppose, since they\'re gone. But I can\'t feel the others either. Is that normal? The surgeon says it\'s normal. She says it like she\'s said it before. A lot.', 0),
(971403, 12033, 'option', 'I971403', 0, 'The Society wants to try its remedies on patients here. What do you think?', 0, 'credit', 971403, 971431, 971411, 1, 'If they\'d pay me? I\'d let them try anything short of setting me alight. ...Actually, ask them about the alight. I\'ve been cold for nine years.', 0),
(971404, 12034, 'option', 'I971403', 0, 'The Society wants to try its remedies on patients here. What do you think?', 0, 'credit', 971403, 971431, 971412, 1, 'Try things on me? I\'ve been tried on, dear. By the plague, by the Scourge, by a cart. I\'d like something to be my decision, for once. Ask me first. That\'s all. Ask, and listen to the answer.', 0),
(971405, 12035, 'option', 'I971403', 0, 'The Society wants to try its remedies on patients here. What do you think?', 0, 'credit', 971403, 971431, 971413, 1, 'Would it hurt? Would it bring the fingers back? Would I be... I\'m sorry. I don\'t know. I don\'t think I\'d want to be something they write down in a book. Is that a stupid thing to want?', 0),
(971406, 12036, 'greet', '', 0, NULL, 971424, '', 0, 0, 0, 0, NULL, 0),
(971407, 12037, 'greet', '', 0, NULL, 971425, '', 0, 0, 0, 0, NULL, 0),
(971408, 12038, 'greet', '', 0, NULL, 971426, '', 0, 0, 0, 0, NULL, 0),
(971412, 12039, 'greet', '', 0, NULL, 971427, '', 0, 0, 0, 0, NULL, 0),
(971413, 12040, 'greet', '', 0, NULL, 971428, '', 0, 0, 0, 0, NULL, 0),
(971414, 12041, 'greet', 'R971407', 0, NULL, 971429, '', 0, 0, 0, 0, NULL, 0),
(971414, 12042, 'greet', '', 0, NULL, 971430, '', 0, 0, 0, 0, NULL, 0),
(971415, 12043, 'greet', '', 0, NULL, 971431, '', 0, 0, 0, 0, NULL, 0),
(971416, 12044, 'greet', '', 0, NULL, 971432, '', 0, 0, 0, 0, NULL, 0),
(971417, 12045, 'greet', 'F80', 0, NULL, 971433, '', 0, 0, 0, 0, NULL, 0),
(971417, 12046, 'greet', 'F16', 0, NULL, 971434, '', 0, 0, 0, 0, NULL, 0),
(971417, 12047, 'greet', 'F32', 0, NULL, 971435, '', 0, 0, 0, 0, NULL, 0),
(971417, 12048, 'greet', '', 0, NULL, 971436, '', 0, 0, 0, 0, NULL, 0),
(2132, 12049, 'option', 'R971404 F16', 0, '(Ask her about the Surgeon\'s Hall.)', 0, 'say', 0, 0, 0, 1, 'I take Elspeth a basket every evening. She holds every bottle up to the light before it goes near a patient. I like her, my love. She doesn\'t trust anyone either. If you\'re ever hurt, you come to me first. Not to her. To me.', 0),
(2132, 12050, 'option', 'R971404 F32', 0, '(Ask her about the Surgeon\'s Hall.)', 0, 'say', 0, 0, 0, 1, 'Elspeth Rane buys my willowbark by the sack now. She\'s the first person in Brill who ever read the label before asking me what\'s in it. If anything happens to you, friend, I want to hear it from you. Not from her ledger.', 0),
(2132, 12051, 'option', 'R971404 !F16 !F32', 0, '(Ask her about the Surgeon\'s Hall.)', 0, 'say', 0, 0, 0, 1, 'The surgeon by the cemetery sends for my willowbark every evening. She won\'t let Johaan near her patients. She lets me. I\'ve decided to take that as a compliment.', 0),
(2134, 12052, 'option', 'I971400', 0, 'Surgeon Rane needs linen for bandages. Eight rolls.', 0, 'credit', 971400, 971419, 971414, 1, 'Linen for the new surgeon? Eight rolls, clean, none of the grey. Tell her it\'s on credit, and tell her if she cuts it crooked I\'ll know.', 0),
(971000, 12053, 'option', 'I971400', 0, 'Surgeon Rane needs four splints.', 0, 'credit', 971400, 971419, 971415, 1, 'Splints. Straight ash, planed smooth; I\'ve lath ends that\'ll do. Tell her if she ever needs a roof, I do those too, but they don\'t fit in a sling.', 0),
(2118, 12054, 'option', 'I971401', 0, 'Surgeon Rane needs needles and stitching thread.', 0, 'credit', 971401, 971423, 0, 1, 'Needles and gut for the surgeon. I\'ll give her the sailmaker\'s ones; they go through anything. Don\'t tell me what anything is.', 0),
(10665, 12055, 'option', 'I971401', 0, 'Surgeon Rane needs clean glass and something to clean wounds with.', 0, 'credit', 971401, 971424, 0, 1, 'Bottles, yes, she\'s welcome to bottles, and carbolic, and spirit of wine. And would she like to try this? It\'s a tincture for the preservation of... no? No. Tell her I asked nicely.', 0),
(971000, 12056, 'option', 'I971402', 0, 'Timm Vetch needs leather straps and small gears for an arm.', 0, 'credit', 971402, 971427, 0, 1, 'An arm, is it? The lad with the sleeve. Here: harness leather, good and supple, and a tin of clock gears off a dead wagon. Don\'t ask whose. Tell him if it works, I want to see it wave.', 0),
(1518, 12057, 'option', 'I971403', 0, 'Surgeon Rane would like your view of the Society\'s proposal.', 0, 'credit', 971403, 971432, 0, 1, 'Rane. She came to my door once to tell me a tincture of mine was a crime against the liver. ...Tell her this, then. The Society does not ask. It never has. If she wants her patients asked, she must write it down and make the Society sign it. That is the only kind of conscience it recognises.', 0),
(2134, 12058, 'option', 'I971405', 0, 'Surgeon Rane needs clean linen again.', 0, 'credit', 971405, 971438, 0, 1, 'Again? She goes through linen like the Scourge went through Andorhal. Here. And take the heavy roll for Dillinger; he bleeds through the cheap stuff.', 0),
(2118, 12059, 'option', 'I971405', 0, 'Surgeon Rane needs more thread.', 0, 'credit', 971405, 971439, 0, 1, 'Gut, heavy and light. I\'ve started stocking it by the yard. It outsells candles now. I find that a very Brill sentence.', 0),
(1496, 12060, 'option', 'I971405', 0, 'Hold still. Surgeon\'s orders.', 0, 'credit', 971405, 971440, 0, 1, 'It\'s nothing. ...Fine. Fine. (He holds still while you close the old crossbow wound in his shoulder.) A Scarlet at the river, in the spring. My shoulder\'s still annoyed about it.', 0),
(3547, 12061, 'option', 'I971405', 0, 'Let me see that hand.', 0, 'credit', 971405, 971441, 0, 1, 'It\'s fine! It\'s mushroom paste. Very healing. ...It\'s gone blue. Is it meant to go blue? (You clean the paste out and stitch the cut while Hamlin explains which mushrooms are good for wounds. None of them, it turns out.)', 0);
UPDATE `creature_template` SET `npcflag` = `npcflag` | 1 WHERE `entry` IN (1496, 1518, 2118, 2132, 2134, 3547, 10665);
INSERT INTO `brill_town_phase` (`bit`, `ord`, `cond`) VALUES
(16, 0, '!R971404');
INSERT INTO `brill_town_stage` (`type`, `value`, `ord`, `cond`) VALUES
(7, 1, 0, 'R971000'),
(7, 2, 0, 'R971400'),
(7, 3, 0, 'R971401'),
(7, 4, 0, 'R971402'),
(7, 5, 0, 'R971403'),
(7, 6, 0, 'R971404'),
(7, 7, 0, 'R971416');
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `Flags`, `RewardXPDifficulty`, `RewardMoney`, `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `AreaDescription`, `QuestCompletionLog`, `RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `ObjectiveText1`, `RequiredNpcOrGo2`, `RequiredNpcOrGoCount2`, `ObjectiveText2`, `RequiredNpcOrGo3`, `RequiredNpcOrGoCount3`, `ObjectiveText3`, `RequiredNpcOrGo4`, `RequiredNpcOrGoCount4`, `ObjectiveText4`, `RewardItem1`, `RewardAmount1`, `RewardItem2`, `RewardAmount2`, `RewardItem3`, `RewardAmount3`, `RewardItem4`, `RewardAmount4`) VALUES
(971400, 2, -1, 8, 159, 0, 4, 2500, 0, 'Holding Together', 'Speak with the three injured travellers in Surgeon Elspeth Rane\'s care, get linen from Mrs. Winters and splints from Rudd Carver at the builder\'s yard, recover her instruments from the wagon she left on the Undercity road, and look into the vacant farmhouse by the cemetery gate. Then return to Elspeth.', 'You. Can you hold a man\'s leg still while I set it? No? Then fetch, carry, and keep out of my light.$B$BElspeth Rane. I was a physician in Lordaeron for twenty-two years and I have been a corpse for nine, and in neither condition have I seen a town this size without a single surgeon. Brill has an inn, a stable, a magistrate and two apothecaries who would sooner bottle my patients than mend them.$B$BI came up the Undercity road with three travellers who met something with teeth. Then my wagon lost a wheel, and the horse lost its nerve. Talk to them; they\'ll tell you more than they tell me. Bandages and splints, from whoever in this town sells cloth and wood. My instruments are still in the wagon, past the bend before the crossroads. And look over that boarded-up farmhouse. If it has four walls and a roof, it\'s a hospital.', '', 'Return to Surgeon Elspeth Rane by the cemetery gate in Brill.', 971418, 3, 'Injured travellers spoken with', 971419, 2, 'Linen and splints', 971420, 1, 'Surgical instruments recovered', 971421, 1, 'Vacant farmhouse inspected', 1251, 5, 0, 0, 0, 0, 0, 0),
(971401, 2, -1, 8, 159, 0, 4, 3500, 0, 'A Steady Hand', 'Recover 2 oak tables from the yard at Garren\'s Haunt, get needles and thread from Abigail Shiel and glass and cleaning spirit from Junior Apothecary Holland, and put together the cabinets by the farmhouse door. Then report to Surgeon Elspeth Rane.', 'Fenwick Pike. Orderly. I was with the surgeons of the Second Regiment on the Darrowmere line, and then I wasn\'t with anybody for a while, and now she\'s sent for me and here I am, still holding things together. It\'s mostly what I\'m for.$B$BShe wants a proper examination room, and she wants it yesterday. Two tables, for a start: the Garrens, up at Garren\'s Haunt north of here, laid their dead out on good oak tables, and the gnolls have dragged them into the yard. Needles and gut, which Abigail Shiel sells for mending sails and won\'t ask what we\'re mending. Glass and something to clean with; Junior Apothecary Holland is the only one up this road who\'ll give us bottles without asking for a patient in return.$B$BAnd Rudd\'s lads have left cabinet parts by the door. Thatcher\'s chalked every piece. Thatcher says they go together in an hour. Thatcher says a lot of things.', '', 'Return to Surgeon Elspeth Rane by the cemetery gate in Brill.', 971422, 2, 'Oak tables recovered', 971423, 1, 'Needles and thread', 971424, 1, 'Glass and cleaning spirit', 971425, 1, 'Medical cabinets put together', 2581, 3, 0, 0, 0, 0, 0, 0),
(971402, 2, -1, 9, 159, 0, 5, 4500, 0, 'A Spare Arm and a Leg', 'Salvage 3 articulated joints from the rusted mill gearing at Agamand Mills, get leather straps and gears from Rudd Carver at the builder\'s yard, find the hand in the burned clockmaker\'s shop at Agamand Mills, then help Timm Vetch put his prosthetic together and test it.', 'Don\'t stare at the sleeve. Everyone stares at the sleeve. ...Fine. Stare.$B$BI lost it eight months ago. Not in the plague, not when I died: after. A beam came down in the Apothecarium\'s cellars and pinned it, and by the time they dug me out it had gone grey to the shoulder, and Elspeth said it had to come off. It doesn\'t grow back, $n. We don\'t heal. We wear out slower than we used to, and then all at once.$B$BSo I\'ve been reading. A tinker\'s plans, gnomish, torn out of a notebook somebody sold in the Undercity: a hand that closes when you flex your shoulder. Joints, straps, gears, and the hand itself. The mill at Agamand Mills has gearing rusting in the yard, joints and all. Rudd Carver will spare straps and gears. And the plans say \'begin with a good hand.\' There was a clockmaker in the mill village; his shop\'s half burned. If anyone left a hand lying about, it\'d be him.', '', 'Return to Timm Vetch at the Surgeon\'s Hall in Brill.', 971426, 3, 'Articulated joints salvaged', 971427, 1, 'Leather straps and gears', 971428, 1, 'The clockmaker\'s hand', 971429, 1, 'Prosthetic assembled and tested', 0, 0, 0, 0, 0, 0, 0, 0),
(971403, 2, -1, 9, 159, 0, 5, 4500, 0, 'The Patient Comes First', 'Read the Royal Apothecary Society\'s proposal and Elspeth\'s case records, ask the three patients in the tent what they make of it, consult Apothecary Johaan, then help Surgeon Elspeth Rane write the hall\'s charter.', 'An apothecary came to see me this morning, with Master Apothecary Faranell\'s seal on his papers. He was very polite. They\'re always very polite.$B$BThe Royal Apothecary Society proposes, and I quote, \'to make use of the Surgeon\'s Hall\'s patients in the trial of promising remedies for the decay of the flesh.\' Make use of. As if a patient were a field to be ploughed.$B$BI won\'t have it. I also won\'t be told I\'m a sentimental old woman standing in the way of progress, so we will do this properly. Read the proposal; it\'s on the side table in the yard. Fetch my case records from the chest by the side wall; I want the facts. Ask the patients themselves. Ask Johaan, who has the Society\'s ear and, I\'m told, a conscience somewhere about him. Then come back, and we\'ll write down what this hall is for, so nobody has to ask again.', '', 'Return to Surgeon Elspeth Rane at the Surgeon\'s Hall in Brill.', 971430, 2, 'Proposal and case records read', 971431, 3, 'Patients consulted', 971432, 1, 'Apothecary Johaan consulted', 971433, 1, 'The patients\' charter written', 0, 0, 0, 0, 0, 0, 0, 0),
(971404, 2, -1, 9, 159, 0, 5, 6000, 0, 'The First Patient', 'Prepare the examination table, help Fenwick Pike clean and splint Agnes Morrow\'s leg, help Timm Vetch fit her brace and hand Surgeon Elspeth Rane her instruments through the operation. Then visit Agnes in the ward once she\'s recovered.', 'Her name is Agnes Morrow. She walked from Tarren Mill on that leg, which is either very brave or very stupid, and in my experience the two are cousins.$B$BBandits on the Hillsbrad road. A cudgel, then a fall, then nine days walking on it. The bone\'s split above the knee, the flesh round it has started to go, and if it goes much further she\'ll lose the leg, and with it the only thing she has, which is the road.$B$BThis will be the hall\'s first proper operation, and I mean it to be done properly. Lay out the table, scrubbed, the lamps lit. Fenwick will clean and splint the limb; you\'ll hold what he tells you to hold. Timm has made her a brace; help him fit it, and don\'t let him improvise. Then stand at my right hand and give me what I ask for, the moment I ask for it.$B$BAfter, she\'ll need rest. Then go and see her. Patients remember who came back.', '', 'Visit Agnes Morrow in the ward of the Surgeon\'s Hall.', 971434, 1, 'Examination table prepared', 971435, 1, 'Agnes\'s leg cleaned and splinted', 971436, 1, 'Brace fitted with Timm', 971437, 1, 'Instruments handed to Elspeth', 858, 3, 2458, 2, 0, 0, 0, 0),
(971405, 2, -1, 9, 159, 4096, 2, 1200, 0, 'Repairs Required', 'Get clean linen from Mrs. Winters and thread from Abigail Shiel, close Deathguard Dillinger\'s shoulder and stitch Hamlin Atkins\'s hand, then return to Surgeon Elspeth Rane.', 'Repairs, $n. Every day, repairs. A town of the dead is a town of things coming loose: stitches, joints, the odd ear. Most of them won\'t come to me until something falls off, so I go to them. Or rather, you do.$B$BLinen from Mrs. Winters, thread from Abigail Shiel. Dillinger\'s shoulder has opened again; he\'ll tell you it\'s nothing, so don\'t ask him, tell him. And Hamlin Atkins has cut his hand on a mushroom knife, again, and is trying to mend it with mushroom paste, again.', '', 'Return to Surgeon Elspeth Rane at the Surgeon\'s Hall in Brill.', 971438, 1, 'Linen from Mrs. Winters', 971439, 1, 'Thread from Abigail Shiel', 971440, 1, 'Deathguard Dillinger\'s shoulder closed', 971441, 1, 'Hamlin Atkins\'s hand stitched', 1251, 4, 2581, 2, 0, 0, 0, 0),
(971406, 2, 1, 1, -1, 0, 0, 0, 0, '[clinical]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971407, 2, 1, 1, -1, 0, 0, 0, 0, '[voluntary]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971408, 2, 1, 1, -1, 0, 0, 0, 0, '[spoke_jory]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971409, 2, 1, 1, -1, 0, 0, 0, 0, '[spoke_nan]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971410, 2, 1, 1, -1, 0, 0, 0, 0, '[spoke_corwin]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971411, 2, 1, 1, -1, 0, 0, 0, 0, '[asked_jory]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971412, 2, 1, 1, -1, 0, 0, 0, 0, '[asked_nan]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971413, 2, 1, 1, -1, 0, 0, 0, 0, '[asked_corwin]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971414, 2, 1, 1, -1, 0, 0, 0, 0, '[got_linen]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971415, 2, 1, 1, -1, 0, 0, 0, 0, '[got_splints]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971416, 2, 1, 1, -1, 0, 0, 0, 0, '[house_set]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`, `SpecialFlags`) VALUES (971400, 971000, 0), (971401, 971400, 0), (971402, 971401, 0), (971403, 971402, 0), (971404, 971403, 0), (971405, 971404, 1);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`) VALUES
(971400, 1, '(Under Elspeth\'s barked instructions the yard becomes a ward: canvas, cots, a fire for boiling, a table for cutting.)$B$BAdequate. Not good. Adequate. That word will have to carry a great deal of weight for a while.$B$BThe house is sound, you say. Then that\'s where we\'ll be, once the Magistrate stops pretending to read my petition. I\'ve sent to the Undercity for an orderly: Fenwick Pike, who held men together on the Darrowmere line while I stitched them. If he\'s still in one piece himself.'),
(971401, 1, '(Elspeth runs a finger along the tables, holds each needle to the light, and counts the bottles twice.)$B$BAdequate. ...No. Good. That\'s good work.$B$BHolland sent bottles. Clean ones. And a note offering me \'a promising preservative of the tissues, untested.\' Every apothecary in Tirisfal has something untested in a jar that they\'d like to try on someone who can\'t say no. I\'m thinking of papering the walls with their notes.$B$BSet the tables out under the canvas. Brill can be examined in the open air for now, like livestock.'),
(971402, 1, '(The arm lies on the bench: brass, leather and oak, the gnomish hand at the end of it curled loosely, like a sleeping thing.)$B$BIt works. It works! Did you see it grab the... well, it grabbed you. Sorry about that. The spring on the third finger was wound backwards. It only twitches when it\'s cold now.$B$BElspeth looked at it for a full minute. Then she said, \'Good. Practise on the frame for a month before you strap it to anyone.\' That\'s the nicest thing she has ever said to me. I\'m having it framed.'),
(971403, 1, '(Elspeth reads the charter aloud, slowly, the way a sentence is read in court.)$B$B\'No patient of this hall shall be made the subject of any trial, test or remedy without their knowledge. The surgeon\'s judgement in their care is final.\' And then your clause, $n. Good. It\'s written. Things that are written are harder to forget, even for us.$B$BI\'ll send a copy to the Undercity. Faranell won\'t read it. Someone in his office will, and they\'ll remember the name at the bottom, which is mine. Now out of my ward; people are trying to rest in it.'),
(971404, 1, '(Days later. Agnes Morrow is standing. The brace creaks, the cane trembles, and Fenwick hovers with his hands out like a man catching eggs. She waves him off.)$B$BLook at that. Nine days I walked on that leg thinking every step was the last it had in it.$B$BI meant to get patched up and move on. But Rane asked me every morning, \'Does it hurt? Good. That means it\'s still yours.\' I think I\'ll stay a while.$B$BI\'ve been dead for years. I\'d rather not spend the next hundred crawling.'),
(971405, 1, 'Good. Every stitch you put in today is one I don\'t have to put in tomorrow. That isn\'t gratitude, $n, it\'s arithmetic.$B$B...Fine. It\'s a little gratitude. Take the bandages, and use them on yourself before you come to me. I\'d like one person in Brill to arrive already mended.');
INSERT INTO `quest_request_items` (`ID`, `EmoteOnComplete`, `EmoteOnIncomplete`, `CompletionText`) VALUES
(971400, 1, 1, 'Bandages. Splints. Instruments. The house. I can count to four, $n, and so can you.'),
(971401, 1, 1, 'Tables, needles, glass, cabinets. She\'ll inspect every one. She inspects me twice a day.'),
(971402, 1, 1, 'Joints, straps, gears, a hand. Then we find out whether I\'ve been reading page nine upside down.'),
(971403, 1, 1, 'Proposal, records, patients, Johaan. Then the pen. I\'ve sharpened it. I\'ve sharpened several.'),
(971404, 1, 1, '(Agnes is propped on the cot, her leg splinted hip to ankle.) Is she done sharpening things? Tell her to get on with it. I\'ve a road waiting.'),
(971405, 1, 1, 'Linen, thread, a shoulder, a hand. In that order, if you can manage it.');
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES (971400, 971400), (971402, 971401), (971401, 971402), (971400, 971403), (971400, 971404), (971400, 971405);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES (971400, 971400), (971400, 971401), (971401, 971402), (971400, 971403), (971406, 971404), (971400, 971405);

-- The Caravan Office
INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`) VALUES (971501, 0, 4496, 0, 0, 0), (971501, 1, 5571, 0, 0, 0), (971501, 2, 5572, 0, 0, 0), (971501, 3, 4498, 0, 0, 0), (971501, 4, 856, 0, 0, 0), (971501, 5, 159, 0, 0, 0), (971501, 6, 4540, 0, 0, 0), (971501, 7, 117, 0, 0, 0), (971501, 8, 4471, 0, 0, 0), (971501, 9, 4470, 0, 0, 0), (971501, 10, 2320, 0, 0, 0), (971501, 11, 5042, 0, 0, 0), (971501, 12, 5048, 0, 0, 0);
INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`) VALUES (971503, 0, 6529, 0, 0, 0), (971503, 1, 6530, 0, 0, 0), (971503, 2, 6256, 0, 0, 0), (971503, 3, 7005, 0, 0, 0), (971503, 4, 2901, 0, 0, 0), (971503, 5, 5956, 0, 0, 0), (971503, 6, 2604, 0, 0, 0), (971503, 7, 6260, 0, 0, 0), (971503, 8, 2324, 0, 0, 0), (971503, 9, 3371, 0, 0, 0), (971503, 10, 2678, 0, 0, 0), (971503, 11, 6217, 0, 0, 0), (971503, 12, 2880, 0, 0, 0), (971503, 13, 4399, 0, 0, 0);
INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`) VALUES (971519, 0, 6529, 0, 0, 0), (971519, 1, 6530, 0, 0, 0), (971519, 2, 6256, 0, 0, 0), (971519, 3, 7005, 0, 0, 0), (971519, 4, 2901, 0, 0, 0), (971519, 5, 5956, 0, 0, 0), (971519, 6, 2604, 0, 0, 0), (971519, 7, 6260, 0, 0, 0), (971519, 8, 2324, 0, 0, 0), (971519, 9, 3371, 0, 0, 0), (971519, 10, 2678, 0, 0, 0), (971519, 11, 6217, 0, 0, 0), (971519, 12, 2880, 0, 0, 0), (971519, 13, 4399, 0, 0, 0);
INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`) VALUES (971521, 0, 4604, 0, 0, 0), (971521, 1, 4605, 0, 0, 0), (971521, 2, 4606, 0, 0, 0), (971521, 3, 2928, 0, 0, 0), (971521, 4, 2930, 0, 0, 0), (971521, 5, 5173, 0, 0, 0), (971521, 6, 3371, 0, 0, 0), (971521, 7, 2321, 0, 0, 0), (971521, 8, 4340, 0, 0, 0), (971521, 9, 2325, 0, 0, 0);
INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`) VALUES (971522, 0, 787, 0, 0, 0), (971522, 1, 4592, 0, 0, 0), (971522, 2, 6290, 0, 0, 0), (971522, 3, 6256, 0, 0, 0), (971522, 4, 6530, 0, 0, 0), (971522, 5, 4470, 0, 0, 0), (971522, 6, 4399, 0, 0, 0), (971522, 7, 2678, 0, 0, 0);
INSERT INTO `creature_template` (`entry`, `name`, `subname`, `gossip_menu_id`, `minlevel`, `maxlevel`, `faction`, `npcflag`, `speed_walk`, `speed_run`, `unit_class`, `unit_flags`, `type`, `rank`, `HealthModifier`, `DamageModifier`, `mingold`, `maxgold`, `flags_extra`, `AIName`, `ScriptName`) VALUES
(971500, 'Quartermaster Irena Sable', 'Caravan Administrator', 0, 30, 30, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971501, 'Quartermaster Irena Sable', 'Caravan Office', 0, 30, 30, 68, 131, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971502, 'Dren Hollow', 'Caravan Driver', 0, 20, 20, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971503, 'Selwyn Price', 'Travelling Merchant', 0, 15, 15, 68, 129, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971504, 'Garth Molt', 'Caravan Guard', 0, 25, 25, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971505, 'Bastian Coyle', 'Caravan Guard', 0, 18, 18, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971506, 'Ostin Marl', 'Carter', 0, 14, 14, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971507, 'Beatrix Fell', 'Carter', 0, 14, 14, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971508, 'Jory Thane', 'Carter', 0, 11, 11, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971509, 'Aldous Penhallow', 'Merchants\' Exchange', 0, 30, 30, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971510, 'Lucan Ashgrove', 'Factor of the Sepulcher', 0, 20, 20, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971511, 'Roadwarden Silas Hobb', NULL, 0, 25, 25, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971512, 'Bartle Kemp', 'The Road Toll', 0, 12, 12, 14, 0, 1, 1.14286, 1, 512, 7, 0, 2.5, 1.3, 300, 300, 0, 'SmartAI', ''),
(971513, 'Kemp\'s Cutthroat', NULL, 0, 10, 11, 14, 0, 1, 1.14286, 1, 512, 7, 0, 1, 1, 60, 60, 0, 'SmartAI', ''),
(971514, 'Hedge Ambusher', NULL, 0, 10, 11, 14, 0, 1, 1.14286, 1, 512, 7, 0, 1, 1, 50, 50, 0, 'SmartAI', ''),
(971515, 'Dren Hollow', 'Caravan Driver', 0, 20, 20, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971516, 'Dren Hollow', 'Caravan Driver', 0, 20, 20, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971517, 'Dren Hollow', 'Caravan Driver', 0, 20, 20, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971518, 'Dren Hollow', 'Caravan Driver', 0, 20, 20, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971519, 'Selwyn Price', 'Travelling Merchant', 0, 15, 15, 68, 129, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971520, 'Selwyn Price', 'Travelling Merchant', 0, 15, 15, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971521, 'Hugh Varley', 'Undercity Teamster', 0, 20, 20, 68, 129, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971522, 'Odile Brannock', 'Silverpine Peddler', 0, 18, 18, 68, 129, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971523, 'Caravan Porter', NULL, 0, 10, 10, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971524, 'Yard Hand', NULL, 0, 10, 10, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971525, 'Caravan Night Watch', NULL, 0, 20, 20, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971526, 'Weary Traveller', NULL, 0, 10, 10, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971527, 'Sleepless Traveller', NULL, 0, 10, 10, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971528, 'Wenna Dask', 'Seamstress', 0, 10, 10, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971529, 'Oswin Thatcher', 'Carpenter', 0, 25, 25, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971530, 'Builder\'s Yard Laborer', NULL, 0, 15, 15, 68, 0, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971531, 'Caravan drivers interviewed', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971532, 'Road and broken wagons inspected', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971533, 'Magistrate Sevren consulted', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971534, 'Caravan office site marked', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971535, 'Dumped shipping crates recovered', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971536, 'Loading winch from Rudd Carver', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971537, 'Timber and iron fittings gathered', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971538, 'Loading platform raised and crates stowed', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971539, 'Missing shipping records recovered', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971540, 'Brill\'s stolen cargo recovered', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971541, 'The altered manifest settled', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971542, 'The Merchants\' Exchange\'s agreement', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971543, 'The Sepulcher\'s agreement', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971544, 'Caravan guards recruited', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971545, 'The first caravan\'s road chosen', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971546, 'Wagon loaded and inspected', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971547, 'Garth and Bastian briefed', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971548, 'Delivery receipt signed at the crossroads', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971549, 'Parcel signed for by Innkeeper Renee', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971550, 'Parcel signed for by Apothecary Johaan', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971551, 'Parcel signed for by Hamlin Atkins', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971552, 'Magistrate Sevren asked', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971553, 'Hamlin Atkins asked', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', '');
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`) VALUES
(971500, 0, 2666, 1, 1),
(971501, 0, 2666, 1, 1),
(971502, 0, 3548, 1, 1),
(971503, 0, 3672, 1, 1),
(971504, 0, 3523, 1, 1),
(971505, 0, 2627, 1, 1),
(971506, 0, 2629, 1, 1),
(971507, 0, 2811, 1, 1),
(971508, 0, 2643, 1, 1),
(971509, 0, 2648, 1, 1),
(971510, 0, 2652, 1, 1),
(971511, 0, 1589, 1, 1),
(971512, 0, 2631, 1, 1),
(971513, 0, 2639, 1, 1),
(971513, 1, 2659, 1, 1),
(971513, 2, 2620, 1, 1),
(971514, 0, 2639, 1, 1),
(971514, 1, 2659, 1, 1),
(971515, 0, 3548, 1, 1),
(971516, 0, 3548, 1, 1),
(971517, 0, 3548, 1, 1),
(971518, 0, 3548, 1, 1),
(971519, 0, 3672, 1, 1),
(971520, 0, 3672, 1, 1),
(971521, 0, 2636, 1, 1),
(971522, 0, 2667, 1, 1),
(971523, 0, 1574, 1, 1),
(971523, 1, 1577, 1, 1),
(971524, 0, 3542, 1, 1),
(971524, 1, 2635, 1, 1),
(971525, 0, 1590, 1, 1),
(971526, 0, 2656, 1, 1),
(971526, 1, 2614, 1, 1),
(971526, 2, 2617, 1, 1),
(971527, 0, 2656, 1, 1),
(971527, 1, 2614, 1, 1),
(971527, 2, 2617, 1, 1),
(971528, 0, 2665, 1, 1),
(971529, 0, 1638, 1, 1),
(971530, 0, 3516, 1, 1),
(971530, 1, 1638, 1, 1),
(971530, 2, 1604, 1, 1),
(971531, 0, 11686, 1, 1),
(971532, 0, 11686, 1, 1),
(971533, 0, 11686, 1, 1),
(971534, 0, 11686, 1, 1),
(971535, 0, 11686, 1, 1),
(971536, 0, 11686, 1, 1),
(971537, 0, 11686, 1, 1),
(971538, 0, 11686, 1, 1),
(971539, 0, 11686, 1, 1),
(971540, 0, 11686, 1, 1),
(971541, 0, 11686, 1, 1),
(971542, 0, 11686, 1, 1),
(971543, 0, 11686, 1, 1),
(971544, 0, 11686, 1, 1),
(971545, 0, 11686, 1, 1),
(971546, 0, 11686, 1, 1),
(971547, 0, 11686, 1, 1),
(971548, 0, 11686, 1, 1),
(971549, 0, 11686, 1, 1),
(971550, 0, 11686, 1, 1),
(971551, 0, 11686, 1, 1),
(971552, 0, 11686, 1, 1),
(971553, 0, 11686, 1, 1);
INSERT INTO `creature` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(971500, 971500, 0, 85, 0, 1, 32, 2199.500, 261.000, 36.630, 5.3400, 60, 0, 0, 'mod-brill-home town'),
(971501, 971501, 0, 85, 0, 1, 1, 2189.750, 283.630, 42.100, 4.7300, 60, 0, 0, 'mod-brill-home town'),
(971502, 971502, 0, 85, 0, 1, 32, 2188.500, 253.000, 37.950, 0.6300, 60, 0, 0, 'mod-brill-home town'),
(971503, 971503, 0, 85, 0, 1, 32, 2203.800, 263.400, 36.190, 3.6500, 60, 0, 0, 'mod-brill-home town'),
(971504, 971504, 0, 85, 0, 1, 1, 2193.000, 248.000, 35.710, 5.4300, 60, 0, 0, 'mod-brill-home town'),
(971505, 971505, 0, 85, 0, 1, 1, 2184.500, 245.500, 36.600, 5.5000, 60, 0, 0, 'mod-brill-home town'),
(971506, 971506, 0, 85, 0, 1, 32, 2189.000, 226.500, 36.100, 1.3200, 60, 0, 0, 'mod-brill-home town'),
(971507, 971507, 0, 85, 0, 1, 32, 2197.500, 231.000, 34.490, 2.2400, 60, 0, 0, 'mod-brill-home town'),
(971508, 971508, 0, 85, 0, 1, 32, 2205.000, 235.500, 34.130, 1.7800, 60, 0, 0, 'mod-brill-home town'),
(971509, 971509, 0, 85, 0, 1, 1, 1639.700, 250.900, -43.020, 3.3900, 60, 0, 0, 'mod-brill-home town'),
(971510, 971510, 0, 85, 0, 1, 32, 2262.000, 251.000, 34.300, 3.9000, 60, 0, 0, 'mod-brill-home town'),
(971511, 971511, 0, 85, 0, 1, 1, 2049.500, 168.500, 34.640, 4.2000, 60, 0, 0, 'mod-brill-home town'),
(971512, 971512, 0, 85, 0, 1, 1, 2114.000, 229.000, 61.920, 5.5000, 120, 0, 0, 'mod-brill-home town'),
(971513, 971513, 0, 85, 0, 1, 1, 2118.500, 223.000, 60.310, 5.0000, 120, 3, 1, 'mod-brill-home town'),
(971514, 971513, 0, 85, 0, 1, 1, 2109.500, 234.500, 61.980, 0.2000, 120, 3, 1, 'mod-brill-home town'),
(971515, 971513, 0, 85, 0, 1, 1, 2120.000, 235.500, 60.800, 3.5000, 120, 3, 1, 'mod-brill-home town'),
(971516, 971513, 0, 85, 0, 1, 1, 2108.000, 226.000, 61.550, 1.0000, 120, 3, 1, 'mod-brill-home town'),
(971517, 971514, 0, 85, 0, 1, 1, 2093.000, 141.000, 35.040, 2.4000, 120, 2, 1, 'mod-brill-home town'),
(971518, 971514, 0, 85, 0, 1, 1, 2087.000, 139.000, 34.280, 1.8000, 120, 2, 1, 'mod-brill-home town'),
(971519, 971514, 0, 85, 0, 1, 1, 2084.000, 144.500, 34.410, 1.2000, 120, 2, 1, 'mod-brill-home town'),
(971520, 971514, 0, 85, 0, 1, 1, 2097.500, 137.500, 35.770, 2.9000, 120, 2, 1, 'mod-brill-home town'),
(971521, 971515, 0, 85, 0, 1, 1, 2188.000, 252.000, 37.750, 4.0400, 60, 0, 0, 'mod-brill-home town'),
(971522, 971516, 0, 85, 0, 1, 1, 2183.110, 250.090, 38.060, 2.2700, 60, 0, 0, 'mod-brill-home town'),
(971523, 971517, 0, 85, 0, 1, 1, 2199.420, 287.540, 36.380, 5.2400, 60, 0, 0, 'mod-brill-home town'),
(971524, 971518, 0, 85, 0, 1, 1, 2191.110, 252.230, 37.210, 2.6200, 60, 0, 0, 'mod-brill-home town'),
(971525, 971519, 0, 85, 0, 1, 1, 2202.000, 260.500, 36.000, 5.3400, 60, 0, 0, 'mod-brill-home town'),
(971526, 971520, 0, 85, 0, 1, 1, 2257.000, 249.500, 33.710, 0.4000, 60, 0, 0, 'mod-brill-home town'),
(971527, 971521, 0, 85, 0, 1, 1, 2181.660, 245.600, 37.180, 2.2700, 60, 0, 0, 'mod-brill-home town'),
(971528, 971522, 0, 85, 0, 1, 1, 2181.660, 245.600, 37.180, 2.2700, 60, 0, 0, 'mod-brill-home town'),
(971529, 971523, 0, 85, 0, 1, 1, 2177.810, 246.300, 38.170, 4.3600, 60, 0, 0, 'mod-brill-home town'),
(971530, 971523, 0, 85, 0, 1, 1, 2182.650, 252.970, 39.100, 0.1700, 60, 0, 0, 'mod-brill-home town'),
(971531, 971524, 0, 85, 0, 1, 1, 2184.510, 253.870, 39.020, 1.2200, 60, 0, 0, 'mod-brill-home town'),
(971532, 971524, 0, 85, 0, 1, 1, 2175.710, 242.580, 37.930, 3.4900, 60, 0, 0, 'mod-brill-home town'),
(971533, 971525, 0, 85, 0, 1, 1, 2190.480, 249.090, 36.440, 5.4100, 60, 0, 0, 'mod-brill-home town'),
(971534, 971526, 0, 85, 0, 1, 1, 2196.730, 295.800, 36.490, 2.0900, 60, 0, 0, 'mod-brill-home town'),
(971535, 971527, 0, 85, 0, 1, 1, 2195.800, 297.810, 36.490, 5.2400, 60, 0, 0, 'mod-brill-home town'),
(971536, 971528, 0, 85, 0, 1, 1, 2199.170, 302.980, 36.490, 3.6700, 60, 0, 0, 'mod-brill-home town'),
(971537, 971529, 0, 85, 0, 1, 32, 2196.000, 271.000, 40.090, 2.4500, 60, 0, 0, 'mod-brill-home town'),
(971538, 971530, 0, 85, 0, 1, 32, 2191.660, 270.690, 40.420, 2.3600, 60, 3, 1, 'mod-brill-home town'),
(971539, 971530, 0, 85, 0, 1, 32, 2168.990, 242.810, 40.600, 2.2700, 60, 3, 1, 'mod-brill-home town');
UPDATE `creature_template` SET `AIName` = 'SmartAI' WHERE `entry` IN (971512, 971513, 971514);
INSERT INTO `smart_scripts` (`entryorguid`, `source_type`, `id`, `link`, `event_type`, `event_phase_mask`, `event_chance`, `event_flags`, `event_param1`, `event_param2`, `event_param3`, `event_param4`, `event_param5`, `event_param6`, `action_type`, `action_param1`, `action_param2`, `action_param3`, `action_param4`, `action_param5`, `action_param6`, `target_type`, `target_param1`, `target_param2`, `target_param3`, `target_param4`, `target_x`, `target_y`, `target_z`, `target_o`, `comment`) VALUES
(971512, 0, 0, 0, 0, 0, 100, 0, 3000, 5000, 8000, 11000, 0, 0, 11, 11976, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 'Bartle Kemp casts 11976'),
(971512, 0, 1, 0, 0, 0, 100, 0, 6000, 8000, 12000, 15000, 0, 0, 11, 8646, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 'Bartle Kemp casts 8646'),
(971513, 0, 0, 0, 0, 0, 100, 0, 4000, 7000, 10000, 14000, 0, 0, 11, 8646, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 'Kemp\'s Cutthroat casts 8646'),
(971514, 0, 0, 0, 0, 0, 100, 0, 2000, 4000, 9000, 12000, 0, 0, 11, 11976, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 'Hedge Ambusher casts 11976');
INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `Data0`, `Data1`, `ScriptName`) VALUES
(971500, 33, 8011, 'Caravan Warehouse', 1, 0, 0, ''),
(971501, 33, 8010, 'Brill Caravan Office', 1, 0, 0, ''),
(971502, 33, 7465, 'Wayfarer\'s Rest', 1, 0, 0, ''),
(971503, 5, 8698, 'Quartermaster\'s Awning', 0.7, 0, 0, ''),
(971504, 5, 234, 'Field Desk', 1, 0, 0, ''),
(971505, 5, 8, 'Quartermaster\'s Strongbox', 1, 0, 0, ''),
(971506, 5, 3678, 'Stalled Supply Wagon', 1, 0, 0, ''),
(971507, 10, 20, 'Rutted Roadway', 1.6, 0, 971500, 'go_brill_town'),
(971508, 10, 7524, 'Broken Supply Wagon', 1, 0, 971500, 'go_brill_town'),
(971509, 10, 6134, 'Surveyor\'s Stakes', 1, 0, 971500, 'go_brill_town'),
(971510, 5, 3678, 'Dren\'s Wagon', 1, 0, 0, ''),
(971511, 5, 7195, 'Temporary Warehouse', 1, 0, 0, ''),
(971512, 10, 1108, 'Caravan Timber', 1, 0, 971501, 'go_brill_town'),
(971513, 10, 1248, 'Loading Platform Frame', 1, 0, 971501, 'go_brill_town'),
(971514, 10, 113, 'Recovered Crates', 1, 0, 971501, 'go_brill_town'),
(971515, 10, 18, 'Dumped Shipping Crate', 1, 0, 971501, 'go_brill_town'),
(971516, 5, 36, 'Loading Platform', 2.0, 0, 0, ''),
(971517, 5, 31, 'Stacked Freight', 1, 0, 0, ''),
(971518, 5, 3678, 'Freight Wagon', 1, 0, 0, ''),
(971519, 10, 7524, 'Abandoned Supply Wagon', 1, 0, 971502, 'go_brill_town'),
(971520, 10, 164, 'Dropped Shipping Record', 1, 0, 971502, 'go_brill_town'),
(971521, 5, 192, 'Campfire', 1, 0, 0, ''),
(971522, 5, 7873, 'Bandit\'s Tent', 1, 0, 0, ''),
(971523, 5, 113, 'Stolen Goods', 1, 0, 0, ''),
(971524, 10, 347, 'Brill\'s Cargo', 1, 0, 971502, 'go_brill_town'),
(971525, 5, 7732, 'Caravan Office Counter', 1, 0, 0, ''),
(971526, 5, 91, 'Chair', 1, 0, 0, ''),
(971527, 5, 234, 'Map Table', 1, 0, 0, ''),
(971528, 5, 222, 'Route Maps', 1, 0, 0, ''),
(971529, 5, 43, 'Caravan Ledgers', 1, 0, 0, ''),
(971530, 5, 8, 'Locked Records', 1, 0, 0, ''),
(971531, 10, 3678, 'Brill\'s First Wagon', 1, 0, 971504, 'go_brill_town'),
(971532, 10, 31, 'Chalk-Marked Crate', 1, 0, 971504, 'go_brill_town'),
(971533, 5, 3678, 'Undercity Caravan Wagon', 1, 0, 0, ''),
(971534, 5, 5392, 'Selwyn\'s Wagon', 0.75, 0, 0, ''),
(971535, 5, 221, 'Table', 1, 0, 0, ''),
(971536, 5, 603, 'Bench', 1, 0, 0, ''),
(971537, 5, 727, 'Wayfarer\'s Rest', 1, 0, 0, ''),
(971538, 5, 7872, 'Marta\'s Tent', 1, 0, 0, ''),
(971539, 5, 8, 'Sea Chest from the Sepulcher', 1, 0, 0, ''),
(971540, 5, 287, 'Delivery Parcels', 0.7, 0, 0, '');
INSERT INTO `gameobject_template_addon` (`entry`, `faction`, `flags`) VALUES (971500, 0, 32), (971501, 0, 32), (971502, 0, 32), (971507, 0, 4), (971508, 0, 4), (971509, 0, 4), (971512, 0, 4), (971513, 0, 4), (971514, 0, 4), (971515, 0, 4), (971519, 0, 4), (971520, 0, 4), (971524, 0, 4), (971531, 0, 4), (971532, 0, 4);
INSERT INTO `gameobject` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`, `animprogress`, `state`, `Comment`) VALUES
(971500, 971500, 0, 85, 0, 1, 1, 2172.000, 261.000, 40.850, 5.4110, 0, 0, 0.422401, -0.906409, 0, 255, 1, 'mod-brill-home town'),
(971501, 971501, 0, 85, 0, 1, 1, 2186.000, 282.000, 38.000, 0.7850, 0, 0, 0.382499, 0.923956, 0, 255, 1, 'mod-brill-home town'),
(971502, 971502, 0, 85, 0, 1, 1, 2198.000, 300.000, 32.390, 0.5240, 0, 0, 0.259013, 0.965874, 0, 255, 1, 'mod-brill-home town'),
(971503, 971503, 0, 85, 0, 1, 32, 2196.200, 264.600, 38.330, 5.3400, 0, 0, 0.454306, -0.890846, 0, 255, 1, 'mod-brill-home town'),
(971504, 971504, 0, 85, 0, 1, 32, 2201.300, 259.400, 35.900, 5.3400, 0, 0, 0.454306, -0.890846, 0, 255, 1, 'mod-brill-home town'),
(971505, 971505, 0, 85, 0, 1, 32, 2197.600, 258.600, 36.630, 5.3400, 0, 0, 0.454306, -0.890846, 0, 255, 1, 'mod-brill-home town'),
(971506, 971506, 0, 85, 0, 1, 32, 2186.000, 224.000, 37.100, 0.5000, 0, 0, 0.247404, 0.968912, 0, 255, 1, 'mod-brill-home town'),
(971507, 971507, 0, 85, 0, 1, 32, 2192.000, 238.000, 34.960, 0.5000, 0, 0, 0.247404, 0.968912, 0, 255, 1, 'mod-brill-home town'),
(971508, 971508, 0, 85, 0, 1, 32, 2178.000, 222.500, 38.460, 0.8000, 0, 0, 0.389418, 0.921061, 0, 255, 1, 'mod-brill-home town'),
(971509, 971508, 0, 85, 0, 1, 32, 2156.000, 222.000, 42.590, 1.9000, 0, 0, 0.813416, 0.581683, 0, 255, 1, 'mod-brill-home town'),
(971510, 971509, 0, 85, 0, 1, 32, 2193.000, 274.000, 40.860, 0.8000, 0, 0, 0.389418, 0.921061, 0, 255, 1, 'mod-brill-home town'),
(971511, 971510, 0, 85, 0, 1, 1, 2186.000, 249.500, 37.370, 0.5500, 0, 0, 0.271547, 0.962425, 0, 255, 1, 'mod-brill-home town'),
(971512, 971511, 0, 85, 0, 1, 32, 2164.890, 244.590, 42.590, 5.4100, 0, 0, 0.422854, -0.906198, 0, 255, 1, 'mod-brill-home town'),
(971513, 971512, 0, 85, 0, 1, 32, 2307.000, 468.000, 34.400, 1.0000, 0, 0, 0.479426, 0.877583, 0, 255, 1, 'mod-brill-home town'),
(971514, 971513, 0, 85, 0, 1, 32, 2179.340, 247.580, 38.150, 5.4100, 0, 0, 0.422854, -0.906198, 0, 255, 1, 'mod-brill-home town'),
(971515, 971514, 0, 85, 0, 1, 32, 2168.730, 243.900, 41.000, 5.4100, 0, 0, 0.422854, -0.906198, 0, 255, 1, 'mod-brill-home town'),
(971516, 971514, 0, 85, 0, 1, 32, 2166.860, 246.900, 42.290, 5.4100, 0, 0, 0.422854, -0.906198, 0, 255, 1, 'mod-brill-home town'),
(971517, 971514, 0, 85, 0, 1, 32, 2169.300, 246.330, 41.230, 5.4100, 0, 0, 0.422854, -0.906198, 0, 255, 1, 'mod-brill-home town'),
(971518, 971515, 0, 85, 0, 1, 1, 2158.000, 196.000, 42.660, 0.3000, 0, 0, 0.149438, 0.988771, 0, 255, 1, 'mod-brill-home town'),
(971519, 971515, 0, 85, 0, 1, 1, 2152.500, 181.000, 41.230, 1.2000, 0, 0, 0.564642, 0.825336, 0, 255, 1, 'mod-brill-home town'),
(971520, 971515, 0, 85, 0, 1, 1, 2140.000, 163.500, 38.050, 2.0000, 0, 0, 0.841471, 0.540302, 0, 255, 1, 'mod-brill-home town'),
(971521, 971515, 0, 85, 0, 1, 1, 2117.000, 165.500, 37.760, 0.4000, 0, 0, 0.198669, 0.980067, 0, 255, 1, 'mod-brill-home town'),
(971522, 971515, 0, 85, 0, 1, 1, 2104.000, 161.000, 36.460, 2.5000, 0, 0, 0.948985, 0.315322, 0, 255, 1, 'mod-brill-home town'),
(971523, 971515, 0, 85, 0, 1, 1, 2071.500, 160.500, 34.820, 1.1000, 0, 0, 0.522687, 0.852525, 0, 255, 1, 'mod-brill-home town'),
(971524, 971516, 0, 85, 0, 1, 1, 2180.680, 250.660, 38.730, 5.4100, 0, 0, 0.422854, -0.906198, 0, 255, 1, 'mod-brill-home town'),
(971525, 971517, 0, 85, 0, 1, 1, 2174.670, 246.920, 39.100, 5.7600, 0, 0, 0.258619, -0.965979, 0, 255, 1, 'mod-brill-home town'),
(971526, 971517, 0, 85, 0, 1, 1, 2186.360, 254.770, 38.900, 0.3500, 0, 0, 0.174108, 0.984727, 0, 255, 1, 'mod-brill-home town'),
(971527, 971517, 0, 85, 0, 1, 1, 2187.360, 262.140, 39.950, 5.4100, 0, 0, 0.422854, -0.906198, 0, 255, 1, 'mod-brill-home town'),
(971528, 971518, 0, 85, 0, 1, 1, 2157.420, 256.600, 42.930, 5.4100, 0, 0, 0.422854, -0.906198, 0, 255, 1, 'mod-brill-home town'),
(971529, 971519, 0, 85, 0, 1, 1, 2143.500, 174.000, 39.600, 0.6000, 0, 0, 0.295520, 0.955336, 0, 255, 1, 'mod-brill-home town'),
(971530, 971520, 0, 85, 0, 1, 1, 2133.000, 190.000, 49.350, 0.9000, 0, 0, 0.434966, 0.900447, 0, 255, 1, 'mod-brill-home town'),
(971531, 971520, 0, 85, 0, 1, 1, 2124.500, 206.500, 54.020, 2.0000, 0, 0, 0.841471, 0.540302, 0, 255, 1, 'mod-brill-home town'),
(971532, 971521, 0, 85, 0, 1, 1, 2115.000, 232.500, 61.840, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(971533, 971522, 0, 85, 0, 1, 1, 2108.500, 230.500, 61.990, 0.4000, 0, 0, 0.198669, 0.980067, 0, 255, 1, 'mod-brill-home town'),
(971534, 971523, 0, 85, 0, 1, 1, 2112.000, 236.500, 61.800, 1.4000, 0, 0, 0.644218, 0.764842, 0, 255, 1, 'mod-brill-home town'),
(971535, 971524, 0, 85, 0, 1, 1, 2111.500, 233.000, 62.030, 0.8000, 0, 0, 0.389418, 0.921061, 0, 255, 1, 'mod-brill-home town'),
(971536, 971525, 0, 85, 0, 1, 1, 2188.620, 282.490, 42.100, 4.7300, 0, 0, 0.700853, -0.713306, 0, 255, 1, 'mod-brill-home town'),
(971537, 971526, 0, 85, 0, 1, 1, 2190.880, 283.200, 42.100, 4.7300, 0, 0, 0.700853, -0.713306, 0, 255, 1, 'mod-brill-home town'),
(971538, 971527, 0, 85, 0, 1, 1, 2181.760, 281.290, 42.100, 0.7900, 0, 0, 0.384808, 0.922997, 0, 255, 1, 'mod-brill-home town'),
(971539, 971528, 0, 85, 0, 1, 1, 2181.760, 281.290, 43.050, 1.1300, 0, 0, 0.535416, 0.844589, 0, 255, 1, 'mod-brill-home town'),
(971540, 971529, 0, 85, 0, 1, 1, 2187.840, 286.670, 42.100, 0.7900, 0, 0, 0.384808, 0.922997, 0, 255, 1, 'mod-brill-home town'),
(971541, 971530, 0, 85, 0, 1, 1, 2179.210, 282.280, 42.100, 0.7900, 0, 0, 0.384808, 0.922997, 0, 255, 1, 'mod-brill-home town'),
(971542, 971531, 0, 85, 0, 1, 32, 2178.910, 242.650, 37.170, 5.4100, 0, 0, 0.422854, -0.906198, 0, 255, 1, 'mod-brill-home town'),
(971543, 971532, 0, 85, 0, 1, 32, 2174.690, 243.020, 38.300, 5.5800, 0, 0, 0.344393, -0.938825, 0, 255, 1, 'mod-brill-home town'),
(971544, 971532, 0, 85, 0, 1, 32, 2178.600, 239.130, 37.060, 6.1100, 0, 0, 0.086484, -0.996253, 0, 255, 1, 'mod-brill-home town'),
(971545, 971532, 0, 85, 0, 1, 32, 2183.140, 242.280, 36.370, 0.3500, 0, 0, 0.174108, 0.984727, 0, 255, 1, 'mod-brill-home town'),
(971546, 971533, 0, 85, 0, 1, 1, 2178.910, 242.650, 37.170, 5.4100, 0, 0, 0.422854, -0.906198, 0, 255, 1, 'mod-brill-home town'),
(971547, 971534, 0, 85, 0, 1, 1, 2199.000, 263.500, 37.350, 1.0000, 0, 0, 0.479426, 0.877583, 0, 255, 1, 'mod-brill-home town'),
(971548, 971535, 0, 85, 0, 1, 1, 2196.830, 297.020, 36.490, 0.5200, 0, 0, 0.257081, 0.966390, 0, 255, 1, 'mod-brill-home town'),
(971549, 971535, 0, 85, 0, 1, 1, 2202.530, 299.150, 36.490, 0.5200, 0, 0, 0.257081, 0.966390, 0, 255, 1, 'mod-brill-home town'),
(971550, 971536, 0, 85, 0, 1, 1, 2197.630, 295.630, 36.490, 0.5200, 0, 0, 0.257081, 0.966390, 0, 255, 1, 'mod-brill-home town'),
(971551, 971536, 0, 85, 0, 1, 1, 2196.030, 298.400, 36.490, 3.6700, 0, 0, 0.965301, -0.261141, 0, 255, 1, 'mod-brill-home town'),
(971552, 971537, 0, 85, 0, 1, 1, 2206.530, 292.220, 34.290, 5.2400, 0, 0, 0.498262, -0.867027, 0, 255, 1, 'mod-brill-home town'),
(971553, 971538, 0, 85, 0, 1, 32, 2198.930, 299.380, 34.290, 0.5200, 0, 0, 0.257081, 0.966390, 0, 255, 1, 'mod-brill-home town'),
(971554, 971539, 0, 85, 0, 1, 1, 2271.872, 479.095, 34.060, 5.0615, 0, 0, 0.573558, -0.819165, 0, 255, 1, 'mod-brill-home town'),
(971555, 971540, 0, 85, 0, 1, 1, 2278.647, 482.466, 34.060, 5.4106, 0, 0, 0.422598, -0.906317, 0, 255, 1, 'mod-brill-home town');
INSERT INTO `brill_town_use` (`go`, `ord`, `cond`, `quest`, `credit`, `text_id`, `marker`, `tele_map`, `tele_x`, `tele_y`, `tele_z`, `tele_o`) VALUES
(971507, 0, 'I971500', 971500, 971532, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971508, 0, 'I971500', 971500, 971532, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971509, 0, 'I971500', 971500, 971534, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971512, 0, 'I971501', 971501, 971537, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971513, 0, 'I971501', 971501, 971538, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971514, 0, 'I971501', 971501, 971538, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971515, 0, 'I971501', 971501, 971535, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971519, 0, 'I971502', 971502, 971539, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971520, 0, 'I971502', 971502, 971539, 971500, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971524, 0, 'I971502', 971502, 971540, 0, 971512, -1, 0.000, 0.000, 0.000, 0.0000),
(971531, 0, 'I971504', 971504, 971546, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971532, 0, 'I971504', 971504, 971546, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000);
INSERT INTO `brill_town_gossip` (`npc`, `ord`, `kind`, `cond`, `icon`, `text`, `text_id`, `action`, `quest`, `credit`, `marker`, `emote`, `reply`, `arg`) VALUES
(971500, 13000, 'greet', 'R971514', 0, NULL, 971501, '', 0, 0, 0, 0, NULL, 0),
(971500, 13001, 'greet', 'R971515', 0, NULL, 971502, '', 0, 0, 0, 0, NULL, 0),
(971500, 13002, 'greet', 'T971500', 0, NULL, 971503, '', 0, 0, 0, 0, NULL, 0),
(971500, 13003, 'greet', '', 0, NULL, 971504, '', 0, 0, 0, 0, NULL, 0),
(971501, 13004, 'greet', 'R971604 D3', 0, NULL, 971505, '', 0, 0, 0, 0, NULL, 0),
(971501, 13005, 'greet', 'R971514', 0, NULL, 971506, '', 0, 0, 0, 0, NULL, 0),
(971501, 13006, 'greet', 'R971515', 0, NULL, 971507, '', 0, 0, 0, 0, NULL, 0),
(971501, 13007, 'greet', '', 0, NULL, 971508, '', 0, 0, 0, 0, NULL, 0),
(971501, 13008, 'option', 'R971504', 1, 'Let me see your supplies.', 0, 'vendor', 0, 0, 0, 0, NULL, 0),
(971501, 13009, 'option', 'R971504 R970604', 0, 'Did anything come from the Sepulcher?', 0, 'say', 0, 0, 0, 1, 'A parcel, for you. From an A. Balnir, laundress. (She hands over a soft bundle in brown paper.) Two pillowcases, pressed, and a note: "For the house. They were my mother\'s. Tell old Wicke to open the shutters wider." I\'ve entered them as household linen, no duty. Don\'t tell the Exchange.', 0),
(971501, 13010, 'option', 'R971504 R970405', 0, 'Any post from the Undercity?', 0, 'say', 0, 0, 0, 1, 'One letter, from the Apothecarium, opened and resealed by the Society, which is legal and rude. (She reads the cover note.) "W. Crane, under supervision. Permitted one letter a month." He asks after Johaan\'s knees and whether the Stay ever did anyone any good. I\'d answer him myself, but he didn\'t ask me.', 0),
(971501, 13011, 'option', 'R971504', 1, 'I\'d like some furniture delivered to my house.', 0, 'buy', 0, 0, 971507, 1, 'For the house by the road. (She opens a catalogue, which of course she has.) A sea chest from the Sepulcher, oak, iron-bound, only slightly haunted. And a standing order: anything addressed to you comes up the road and onto your floor, parcels and all. I\'ll have Dren deliver them. He\'ll complain. Sign here.', 10000),
(971502, 13012, 'greet', 'R971503', 0, NULL, 971509, '', 0, 0, 0, 0, NULL, 0),
(971502, 13013, 'greet', 'R971501', 0, NULL, 971510, '', 0, 0, 0, 0, NULL, 0),
(971502, 13014, 'greet', '', 0, NULL, 971511, '', 0, 0, 0, 0, NULL, 0),
(971515, 13015, 'greet', '', 0, NULL, 971512, '', 0, 0, 0, 0, NULL, 0),
(971516, 13016, 'greet', '', 0, NULL, 971513, '', 0, 0, 0, 0, NULL, 0),
(971517, 13017, 'greet', '', 0, NULL, 971514, '', 0, 0, 0, 0, NULL, 0),
(971518, 13018, 'greet', '', 0, NULL, 971515, '', 0, 0, 0, 0, NULL, 0),
(971503, 13019, 'greet', 'R971514', 0, NULL, 971516, '', 0, 0, 0, 0, NULL, 0),
(971503, 13020, 'greet', 'R971515', 0, NULL, 971517, '', 0, 0, 0, 0, NULL, 0),
(971503, 13021, 'greet', 'A971502', 0, NULL, 971518, '', 0, 0, 0, 0, NULL, 0),
(971503, 13022, 'greet', '', 0, NULL, 971519, '', 0, 0, 0, 0, NULL, 0),
(971503, 13023, 'option', 'I971502 R971512', 0, 'Your name is on a bill of sale in a bandit camp, Selwyn.', 0, 'say', 0, 0, 971513, 18, '(For once, Selwyn has nothing cheerful to say.)$B$BI owe money, $n. To a lender at the Sepulcher who doesn\'t write things down, which is the worst kind. The Scourge burned my stock and the Crusade burned the next. I thought: one wagon. The Exchange insures it, nobody\'s hurt, Kemp gets his third, I sell Brill its own oil at a fair price and pay my debt.$B$B...The driver walked home in the dark. I didn\'t think about the driver.', 0),
(971503, 13024, 'option', '', 1, 'Let me see what you\'re selling.', 0, 'vendor', 0, 0, 0, 0, NULL, 0),
(971519, 13025, 'greet', 'R971514', 0, NULL, 971520, '', 0, 0, 0, 0, NULL, 0),
(971519, 13026, 'greet', 'R971515', 0, NULL, 971521, '', 0, 0, 0, 0, NULL, 0),
(971519, 13027, 'greet', '', 0, NULL, 971522, '', 0, 0, 0, 0, NULL, 0),
(971519, 13028, 'option', '', 1, 'Let me see what you\'re selling.', 0, 'vendor', 0, 0, 0, 0, NULL, 0),
(971520, 13029, 'greet', '', 0, NULL, 971523, '', 0, 0, 0, 0, NULL, 0),
(971506, 13030, 'greet', '', 0, NULL, 971524, '', 0, 0, 0, 0, NULL, 0),
(971506, 13031, 'option', 'I971500', 0, 'The quartermaster\'s asking what\'s gone wrong on the road to Brill.', 0, 'credit', 971500, 971531, 971508, 1, 'Wrong? Nothing\'s gone wrong. It\'s always been like this. I bring salt and lamp oil from the Undercity, I stop here, and nobody comes. So I wait. Yesterday I waited so long a Deathguard asked if I was a new statue. In the end somebody buys the lot off the back for half what it\'s worth, and I go home. Write that down, if she likes writing.', 0),
(971507, 13032, 'greet', '', 0, NULL, 971525, '', 0, 0, 0, 0, NULL, 0),
(971507, 13033, 'option', 'I971500', 0, 'Quartermaster Sable wants to know why you\'re stuck here.', 0, 'credit', 971500, 971531, 971509, 1, 'Three crates of nails for the builder\'s yard and a receipt book with no one to sign it. I\'m not leaving nails on the road for the first ghoul with a hammer. Two days I\'ve been here. If she wants a complaint, she can have it in writing. I\'ve already written it. Twice.', 0),
(971508, 13034, 'greet', '', 0, NULL, 971526, '', 0, 0, 0, 0, NULL, 0),
(971508, 13035, 'option', 'I971500', 0, 'The quartermaster is asking the drivers what\'s gone wrong.', 0, 'credit', 971500, 971531, 971510, 1, 'I lost a crate. Off the back, at the bend past the brazier, in the dark. By the time I\'d turned round it was gone, and so was the man who\'d been walking behind me all the way from the crossroads. Friendly fellow. Asked where I was bound and what I carried, and I told him. I tell everyone. ...I shouldn\'t, should I.', 0),
(1499, 13036, 'option', 'I971500', 0, 'Quartermaster Sable asks whether Brill will grant her ground for a caravan office.', 0, 'credit', 971500, 971533, 0, 1, 'Grant it? Take it. That ground by the Undercity road has grown nothing but turkeys since the plague. (He writes, blots, writes again.) Tell Quartermaster Sable she has the town\'s leave, and the town\'s sympathy. She\'ll need both.', 0),
(1499, 13037, 'option', 'I971506', 0, 'Wenna Dask, at the Wayfarer\'s Rest, would like to be entered on Brill\'s rolls.', 0, 'credit', 971506, 971552, 0, 1, 'A seamstress from Andorhal. (Sevren writes the name with great care, and blots it.) She\'ll be the first person this year to come to Brill on purpose. Give her this. It says she lives here. It doesn\'t say it\'s easy.', 0),
(971000, 13038, 'option', 'I971501', 0, 'Dren Hollow says you owe him a loading winch.', 0, 'credit', 971501, 971536, 0, 1, 'Owe him? I lent Dren Hollow a winch in the plague year and he brought it back with a dead man still hanging off the hook. ...Fine. Take the small one. Tell him the hook\'s been cleaned. Tell him I want it back.', 0),
(2135, 13039, 'option', 'I971501', 0, 'The caravan yard needs iron fittings for a loading platform.', 0, 'credit', 971501, 971537, 971511, 1, 'Fittings. Brackets, bolts, a hinge or six. (He sweeps a heap of black iron off his bench into a sack.) Undercity pattern, every one. Tell the driver to bring the sack back. Sacks don\'t grow on trees. Nothing grows on trees round here.', 0),
(971500, 13040, 'option', 'I971502 R971513', 0, 'Selwyn Price altered the manifest. He sold the route to the bandits.', 0, 'choice', 971502, 971541, 971514, 1, '(Irena\'s pen stops.) Price. Of course it\'s Price. He\'s asked me to waive his fees every day for a month, and I took it for his manner.$B$BI\'ll write to the Exchange tonight. He\'ll be fined, his license struck, and every coin he takes in Brill will pass through my ledger until the debt\'s paid. He can stay. Brill needs somebody who\'ll buy anything. But he\'ll do it where I can see him.', 0),
(971500, 13041, 'option', 'I971502 R971513', 0, 'It was Selwyn, to pay a debt. Let him repay every copper and keep trading, under your eye.', 0, 'choice', 971502, 971541, 971515, 1, '(Irena considers you for a long moment.) You\'re asking me not to report a theft.$B$B...No. You\'re asking me to collect on it. That I can do. He\'ll repay the Exchange, the driver and the price of your boots, in full, on my schedule, and he\'ll show me his books every week. If he misses one payment I\'ll report him myself, and tell him you vouched for him. I suspect that will worry him more.', 0),
(971509, 13042, 'greet', 'R971503', 0, NULL, 971527, '', 0, 0, 0, 0, NULL, 0),
(971509, 13043, 'greet', '', 0, NULL, 971528, '', 0, 0, 0, 0, NULL, 0),
(971509, 13044, 'option', 'I971503', 0, 'Quartermaster Sable of Brill asks the Exchange to agree terms for a regular caravan.', 0, 'credit', 971503, 971542, 0, 1, 'Brill. (He says it the way one names an ailment.) Sable\'s prospectus arrived this morning: forty pages, indexed. I have never been so thoroughly persuaded of anything in my unlife.$B$BVery well. The Exchange will send a wagon a week and take one back, at the standard tariff, less a plague discount I have just invented. Sign here. And here. And there.', 0),
(971510, 13045, 'greet', '', 0, NULL, 971529, '', 0, 0, 0, 0, NULL, 0),
(971510, 13046, 'option', 'I971503', 0, 'Brill\'s caravan office wants an agreement with the Sepulcher.', 0, 'credit', 971503, 971543, 0, 1, 'The Sepulcher sells fish, timber and bad news, and we\'re always looking for somebody to sell them to. Brill buys? Then Brill has a friend. (He signs with a flourish.) I\'ll say this for your quartermaster: she\'s the first soul this side of the Greymane Wall who ever asked me for terms in writing. I nearly wept. I would have, if I could.', 0),
(1515, 13047, 'option', 'I971503', 0, 'The caravan office needs a Deathguard to escort its wagons.', 0, 'credit', 971503, 971544, 971516, 1, 'Civilian escort duty. (Zygand looks at you as if you\'d asked him to knit.) ...Molt. Garth Molt. He\'s my best road man, and he\'s been asking for a change. He\'ll hate it. He\'ll be good at it. Tell Sable she has him until the Dark Lady says otherwise.', 0),
(971505, 13048, 'option', 'I971503', 0, 'Quartermaster Sable is hiring guards. Still interested?', 0, 'credit', 971503, 971544, 971517, 273, 'Interested? I\'ve been standing by this crate since dawn holding my own letter of recommendation. I wrote it myself. (It is very short.) Bastian Coyle, Lordaeron militia, the Glades company, until the company stopped being people. I know the roads, I can use a spear and I don\'t run. That last one\'s new. I\'m proud of it.', 0),
(971502, 13049, 'option', 'I971503', 0, 'Send the first wagon to the Undercity. The capital should see what Brill can do.', 0, 'choice', 971503, 971545, 971518, 273, 'The Undercity it is. Safe road, big market, more paperwork than cargo, and Penhallow will be insufferable about it. ...You\'re right, though. Let them see us coming up their road with our own seal on the boards.', 0),
(971502, 13050, 'option', 'I971503', 0, 'Send the first wagon toward Silverpine. The Sepulcher needs it more.', 0, 'choice', 971503, 971545, 971519, 273, 'Silverpine. Worse road, wolves, worgen, and a market that pays in fish. (Dren grins, which on him looks painful.) Good. The Sepulcher\'s lived on whatever the Undercity forgets to send. Let them be first at something.', 0),
(971504, 13051, 'option', 'I971504', 0, 'We roll at the bell. Dren wants the road ahead cleared.', 0, 'credit', 971504, 971547, 971520, 273, 'Heard. (Garth tests the edge of his axe with a grey thumb.) Twelve years on the north road, and they give me a cart of nails to mind. ...It\'s a good cart. Don\'t tell Dren I said so.', 0),
(971505, 13052, 'option', 'I971504', 0, 'We roll at the bell, Bastian.', 0, 'credit', 971504, 971547, 971521, 273, 'At the bell. (Bastian swallows, which he hasn\'t needed to do in years.) First real duty since the militia. I\'ll be at the tailboard. If anything comes over that hedge, $n, it\'ll find me standing.', 0),
(971511, 13053, 'greet', 'R971504', 0, NULL, 971530, '', 0, 0, 0, 0, NULL, 0),
(971511, 13054, 'greet', '', 0, NULL, 971531, '', 0, 0, 0, 0, NULL, 0),
(971511, 13055, 'option', 'I971504 R971518', 0, 'Brill\'s first caravan, for your signature.', 0, 'credit', 971504, 971548, 0, 1, 'Brill, outbound for the Undercity. (He reads the docket, checks the seal and signs with a stub of pencil.) Twenty years I\'ve watched carts come down from Brill. Never seen one go up with its own seal on. There. Signed. Tell your quartermaster the crossroads says welcome to the road.', 0),
(971511, 13056, 'option', 'I971504 R971519', 0, 'Brill\'s first caravan, for your signature.', 0, 'credit', 971504, 971548, 0, 1, 'Brill, outbound for the Sepulcher. Silverpine! (He laughs, a dry sound.) Brave or daft. Signed. The Sepulcher\'s own wagon passed an hour ago going the other way. I told them you\'d be along. They didn\'t believe me either.', 0),
(971504, 13057, 'greet', 'R970505', 0, NULL, 971532, '', 0, 0, 0, 0, NULL, 0),
(971504, 13058, 'greet', 'R970506', 0, NULL, 971533, '', 0, 0, 0, 0, NULL, 0),
(971504, 13059, 'greet', 'R970507', 0, NULL, 971534, '', 0, 0, 0, 0, NULL, 0),
(971504, 13060, 'greet', '', 0, NULL, 971535, '', 0, 0, 0, 0, NULL, 0),
(971505, 13061, 'greet', 'R970504', 0, NULL, 971536, '', 0, 0, 0, 0, NULL, 0),
(971505, 13062, 'greet', '', 0, NULL, 971537, '', 0, 0, 0, 0, NULL, 0),
(971521, 13063, 'greet', 'R971518', 0, NULL, 971538, '', 0, 0, 0, 0, NULL, 0),
(971521, 13064, 'greet', '', 0, NULL, 971539, '', 0, 0, 0, 0, NULL, 0),
(971521, 13065, 'option', '', 1, 'Let me see what the Undercity\'s sent.', 0, 'vendor', 0, 0, 0, 0, NULL, 0),
(971522, 13066, 'greet', 'R971519', 0, NULL, 971540, '', 0, 0, 0, 0, NULL, 0),
(971522, 13067, 'greet', '', 0, NULL, 971541, '', 0, 0, 0, 0, NULL, 0),
(971522, 13068, 'option', '', 1, 'Let me see what\'s come from Silverpine.', 0, 'vendor', 0, 0, 0, 0, NULL, 0),
(971523, 13069, 'greet', '', 0, NULL, 971542, '', 0, 0, 0, 0, NULL, 0),
(971524, 13070, 'greet', '', 0, NULL, 971543, '', 0, 0, 0, 0, NULL, 0),
(971525, 13071, 'greet', '', 0, NULL, 971544, '', 0, 0, 0, 0, NULL, 0),
(971526, 13072, 'greet', '', 0, NULL, 971545, '', 0, 0, 0, 0, NULL, 0),
(971527, 13073, 'greet', '', 0, NULL, 971546, '', 0, 0, 0, 0, NULL, 0),
(971528, 13074, 'greet', 'R971506', 0, NULL, 971547, '', 0, 0, 0, 0, NULL, 0),
(971528, 13075, 'greet', '', 0, NULL, 971548, '', 0, 0, 0, 0, NULL, 0),
(3547, 13076, 'option', 'I971506', 0, 'Could you use a hand in your beds? Her name\'s Wenna Dask.', 0, 'credit', 971506, 971553, 0, 273, 'Steady hands? I\'ve a hundred yards of beds and two hands, one of them loose. Send her round at dawn. Tell her to wear old clothes. Tell her everything\'s old clothes, out here.', 0),
(5688, 13077, 'option', 'I971505', 0, 'A parcel from the caravan office. Sign here?', 0, 'credit', 971505, 971549, 0, 1, 'Candles and a barrel tap! The old tap\'s been weeping since the Third War. (She signs with a flourish.) Thank Irena for me. Tell her she still owes me for that bottle of port.', 0),
(1518, 13078, 'option', 'I971505', 0, 'A crate of vials from the caravan office, for your signature.', 0, 'credit', 971505, 971550, 0, 1, '(Johaan counts the vials, all of them, aloud.) ...forty-seven, forty-eight. Forty-eight. The order was for forty-eight. Remarkable. Your quartermaster may be the only competent person in Tirisfal.', 0),
(3547, 13079, 'option', 'I971505', 0, 'A sack for your mushroom beds, from the caravan office.', 0, 'credit', 971505, 971551, 0, 4, 'Ah, that\'s the good stuff. Bat guano from the caves under the Sepulcher, aged a year. (He breathes it in deeply, though he can\'t smell a thing.) Lovely. The blues\'ll be up to my knees by summer.', 0),
(971529, 13080, 'greet', 'O', 0, NULL, 971549, '', 0, 0, 0, 0, NULL, 0),
(971529, 13081, 'greet', '', 0, NULL, 971550, '', 0, 0, 0, 0, NULL, 0);
UPDATE `creature_template` SET `npcflag` = `npcflag` | 1 WHERE `entry` IN (1499, 1515, 1518, 2135, 3547, 5688);
INSERT INTO `brill_town_phase` (`bit`, `ord`, `cond`) VALUES
(32, 0, '!R971504');
INSERT INTO `brill_town_stage` (`type`, `value`, `ord`, `cond`) VALUES
(8, 1, 0, 'R971000'),
(8, 2, 0, 'R971500'),
(8, 3, 0, 'R971501'),
(8, 4, 0, 'R971502'),
(8, 5, 0, 'R971503'),
(8, 6, 0, 'R971504'),
(8, 7, 0, 'R971507');
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `Flags`, `RewardXPDifficulty`, `RewardMoney`, `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `AreaDescription`, `QuestCompletionLog`, `RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `ObjectiveText1`, `RequiredNpcOrGo2`, `RequiredNpcOrGoCount2`, `ObjectiveText2`, `RequiredNpcOrGo3`, `RequiredNpcOrGoCount3`, `ObjectiveText3`, `RequiredNpcOrGo4`, `RequiredNpcOrGoCount4`, `ObjectiveText4`, `RewardItem1`, `RewardAmount1`, `RewardItem2`, `RewardAmount2`, `RewardItem3`, `RewardAmount3`, `RewardItem4`, `RewardAmount4`) VALUES
(971500, 2, -1, 10, 159, 0, 3, 1200, 0, 'The Road Isn\'t Empty', 'Interview three caravan drivers stranded on the Undercity road, inspect the road and two broken supply wagons, ask Magistrate Sevren about a caravan office, and mark a site for it beside the road. Then return to Quartermaster Irena Sable.', 'You\'ll be the one Sevren mentioned. Good. I have a form for you, but I\'ll spare you it.$B$BIrena Sable, quartermaster, late of the Undercity\'s supply office. The Merchants\' Exchange sent me because Brill has become a complaint. Drivers arrive with no one to receive them. Goods are unloaded into the mud. Three shipments this season were signed for by nobody at all, which is a remarkable trick in a town of the dead.$B$BI need to know how bad it is before I tell anyone what to build. Talk to the drivers stuck along the road. Look at the road itself, and at the two wagons that broke trying to use it. Then ask the Magistrate whether Brill will give me ground for an office, and if he says yes, drive a stake into it before he changes his mind.', '', 'Return to Quartermaster Irena Sable on the Undercity road in Brill.', 971531, 3, 'Caravan drivers interviewed', 971532, 3, 'Road and broken wagons inspected', 971533, 1, 'Magistrate Sevren consulted', 971534, 1, 'Caravan office site marked', 0, 0, 0, 0, 0, 0, 0, 0),
(971501, 2, -1, 10, 159, 0, 3, 1500, 0, 'A Place to Unload', 'Recover 6 dumped shipping crates along the Undercity road south of Brill, get a loading winch from Rudd Carver at the builder\'s yard, timber from the yard and iron fittings from Abe Winters by Brill\'s smithy, then help Dren Hollow raise the loading platform and stow the crates in the big tent.', 'So you\'re the one running the quartermaster\'s errands. Dren Hollow. I drive: the Undercity to Brill, Brill to the Sepulcher and back, for longer than I\'ve been dead.$B$BIrena\'s drawn a yard on paper. Paper doesn\'t hold freight. What holds freight is a platform a wagon can back up to, a winch to get the heavy loads off, and a roof over what you\'ve unloaded.$B$BStart with the crates. Every driver who couldn\'t find anyone to sign for his load dumped it in the ditch between here and the crossroads, and half of it\'s still lying there. Bring back what\'s sound. Rudd Carver at the builder\'s yard owes me a winch, though he\'ll tell you he doesn\'t. He\'s timber put by for us, too, and Abe Winters by the smithy can spare iron.$B$BThen we build.', '', 'Return to Dren Hollow at the caravan yard in Brill.', 971535, 6, 'Dumped shipping crates recovered', 971536, 1, 'Loading winch from Rudd Carver', 971537, 2, 'Timber and iron fittings gathered', 971538, 4, 'Loading platform raised and crates stowed', 4496, 1, 0, 0, 0, 0, 0, 0),
(971502, 2, -1, 10, 159, 0, 4, 2500, 0, 'The Missing Manifest', 'Search the abandoned wagon on the Undercity road south of Brill and recover 3 missing shipping records, follow the trail to the bandits\' camp on the hill west of the road, kill Bartle Kemp and recover Brill\'s cargo. Find out who altered the manifest, then settle it with Quartermaster Irena Sable.', 'A shipment bound for Brill has vanished on the Undercity road: lamp oil, nails, medicine, a crate of seed for Hamlin Atkins. The driver came in on foot and says he was set on by bandits.$B$BI believe in the bandits. I don\'t believe the manifest. Look at it. The cargo is in the clerk\'s hand, but the route and the hour have been scraped off and written in again by someone else. Someone with a better pen.$B$BThe wagon\'s still where he left it, where the road bends south of town. Search it. The records that should be with it are gone, and paper doesn\'t walk; it blows, or it\'s carried. Follow it. Bandits who rob the right wagon, on the right road, at the right hour, were told where to stand. Find out who told them, and bring me back my cargo.', '', 'Return to Quartermaster Irena Sable on the Undercity road in Brill.', 971539, 3, 'Missing shipping records recovered', 971512, 1, '', 971540, 1, 'Brill\'s stolen cargo recovered', 971541, 1, 'The altered manifest settled', 858, 3, 0, 0, 0, 0, 0, 0),
(971503, 2, -1, 10, 159, 0, 4, 2500, 0, 'Licenses and Liabilities', 'Secure a trading agreement from Aldous Penhallow of the Merchants\' Exchange in the Undercity\'s Trade Quarter and another from Lucan Ashgrove of the Sepulcher at the Gallows\' End, recruit two caravan guards (ask Executor Zygand for a Deathguard; Bastian Coyle waits at the yard), and choose with Dren Hollow which road takes Brill\'s first caravan. Then bring the route maps to Quartermaster Irena Sable.', 'The office has a counter and a lock. What it hasn\'t got is anyone to trade with.$B$BA caravan office is a promise: that a wagon leaving Brill will arrive somewhere, and that someone there will pay for what\'s in it. I can\'t make that promise on my own authority. I need it in writing, from the Merchants\' Exchange in the Undercity\'s Trade Quarter and from the Sepulcher\'s factor, who is lodging at the Gallows\' End and charging his room to someone else.$B$BWe\'ll want guards, too. I posted a notice and a man answered it; he\'s at the yard. And Executor Zygand owes this town a Deathguard for its roads. Ask him nicely. Then ask him again.$B$BDren has the route maps. He\'ll want to argue about which road gets our first wagon. Let him, then choose.', '', 'Return to Quartermaster Irena Sable on the Undercity road in Brill.', 971542, 1, 'The Merchants\' Exchange\'s agreement', 971543, 1, 'The Sepulcher\'s agreement', 971544, 2, 'Caravan guards recruited', 971545, 1, 'The first caravan\'s road chosen', 929, 2, 0, 0, 0, 0, 0, 0),
(971504, 2, -1, 10, 159, 0, 5, 4000, 0, 'The First Departure', 'Load Brill\'s first wagon with its 3 chalk-marked crates and check its harness and wheels, brief its guards Garth Molt and Bastian Coyle, kill 4 Hedge Ambushers on the Undercity road ahead of it, and have the delivery receipt signed by Roadwarden Silas Hobb at the crossroads. Then return to Quartermaster Irena Sable.', 'First wagon. Our wagon, out of our yard, with Brill\'s seal on the boards. Twenty years I\'ve waited to drive one of those without somebody else\'s name on it.$B$BHere\'s how it goes. The three crates with the chalk marks go on first; they\'re the ones on the manifest, and Irena will know if you load the wrong three. Check the harness and the wheels, because I will, and I\'d rather not find anything. Tell Garth and Bastian we roll at the bell.$B$BThen ride ahead of me down the Undercity road. Kemp\'s lads didn\'t all die on that hill, and they know what a new wagon looks like. Clear the hedges. At the crossroads the roadwarden signs for the load, and once that receipt\'s signed, Brill\'s a stop on the map.', '', 'Return to Quartermaster Irena Sable at the caravan yard in Brill.', 971546, 4, 'Wagon loaded and inspected', 971547, 2, 'Garth and Bastian briefed', 971514, 4, '', 971548, 1, 'Delivery receipt signed at the crossroads', 4498, 1, 0, 0, 0, 0, 0, 0),
(971505, 2, -1, 10, 159, 4096, 2, 1500, 0, 'Brill Deliveries', 'Deliver the caravan office\'s parcels to Innkeeper Renee at the Gallows\' End, Apothecary Johaan and Hamlin Atkins in Brill, then return to Quartermaster Irena Sable.', 'Three parcels, three signatures, one trip. The contract pays by the parcel and penalizes by the hour.$B$BInnkeeper Renee is expecting candles and a barrel tap. Apothecary Johaan\'s is a crate of empty vials, which he will count in front of you, so let him. Hamlin Atkins has a sack of something for his mushroom beds that I\'ve declined to examine; carry it at arm\'s length.$B$BSome days it\'s three parcels and some days it\'s thirty; today, mercifully, it\'s three. Bring back the signatures. Brill runs on trust, $n. The caravan office runs on receipts.', '', 'Return to Quartermaster Irena Sable at the Brill Caravan Office.', 971549, 1, 'Parcel signed for by Innkeeper Renee', 971550, 1, 'Parcel signed for by Apothecary Johaan', 971551, 1, 'Parcel signed for by Hamlin Atkins', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971506, 2, -1, 10, 159, 0, 2, 1000, 0, 'Somewhere to Stay', 'Ask Magistrate Sevren to enter Wenna Dask on Brill\'s rolls and ask Hamlin Atkins whether he could use a hand, then return to Wenna at the Wayfarer\'s Rest.', 'I was meant to go on to the Sepulcher with the next wagon. I\'ve been meant to for a week. (She turns her room key over and over in her fingers.) I keep finding reasons. The wagon\'s full. The road\'s wet. Marta needs help with the sheets.$B$BI was a seamstress in Andorhal. I don\'t know anyone in Silverpine. I don\'t know anyone here either, but here people say good morning, even the ones without much of a face to say it with.$B$BWould you ask for me? The Magistrate keeps the rolls; if he puts my name in them I\'ll have to stay, won\'t I. And Hamlin Atkins looked like a man who could use steady hands. Mine are, mostly. I\'d ask myself, but if they say no I\'d rather hear it from you.', '', 'Return to Wenna Dask at the Wayfarer\'s Rest in Brill.', 971552, 1, 'Magistrate Sevren asked', 971553, 1, 'Hamlin Atkins asked', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971507, 2, 1, 1, -1, 0, 0, 0, 0, '[house_set]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971508, 2, 1, 1, -1, 0, 0, 0, 0, '[asked_ostin]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971509, 2, 1, 1, -1, 0, 0, 0, 0, '[asked_beatrix]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971510, 2, 1, 1, -1, 0, 0, 0, 0, '[asked_jory]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971511, 2, 1, 1, -1, 0, 0, 0, 0, '[abe_fittings]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971512, 2, 1, 1, -1, 0, 0, 0, 0, '[cargo_seen]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971513, 2, 1, 1, -1, 0, 0, 0, 0, '[heard_selwyn]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971514, 2, 1, 1, -1, 0, 0, 0, 0, '[selwyn_exposed]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971515, 2, 1, 1, -1, 0, 0, 0, 0, '[selwyn_supervised]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971516, 2, 1, 1, -1, 0, 0, 0, 0, '[garth_assigned]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971517, 2, 1, 1, -1, 0, 0, 0, 0, '[bastian_hired]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971518, 2, 1, 1, -1, 0, 0, 0, 0, '[first_undercity]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971519, 2, 1, 1, -1, 0, 0, 0, 0, '[first_silverpine]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971520, 2, 1, 1, -1, 0, 0, 0, 0, '[garth_briefed]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971521, 2, 1, 1, -1, 0, 0, 0, 0, '[bastian_briefed]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`, `SpecialFlags`) VALUES (971500, 0, 0), (971501, 971500, 0), (971502, 971501, 0), (971503, 971502, 0), (971504, 971503, 0), (971505, 971504, 1), (971506, 971504, 0);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`) VALUES
(971500, 1, '(Irena writes as you talk, without once looking down at the page.)$B$BThree drivers with nowhere to unload. Ruts deep enough to lose a wheel in. Two wagons broken on the same stretch, both picked clean. And a magistrate who said yes before I\'d finished asking, which is the most alarming thing I\'ve heard all week.$B$BBrill doesn\'t need a clerk at a table by the road. It needs a loading yard, a warehouse and an office with a door that locks. I\'ll draw it up tonight. In triplicate. Someone has to.'),
(971501, 1, '(Dren stamps on the new platform twice, hard. It doesn\'t move.)$B$BThat\'ll take a loaded wagon. The winch will lift a cask of oil without taking anybody\'s arm off, which is more than the last one I used could say.$B$BTwenty years I\'ve driven into Brill and never once had somewhere to stop. I think I\'ll park here a while. Just to see what it feels like.'),
(971502, 1, '(Irena lays the recovered records beside the manifest and runs her finger down both, line by line.)$B$BEvery crate accounted for. One way or another.$B$BThe office will open with its books straight. That matters more than you\'d think. The dead have long memories and very little else, and they remember who cheated them.$B$BThe builders can have the inside of the office now. I\'ll keep my table by the road until it opens, thank you. Regulations.'),
(971503, 1, '(Irena spreads Dren\'s maps across her table and weighs the corners with an inkpot, an iron weight and a skull she apparently keeps for the purpose.)$B$BPenhallow\'s seal, Ashgrove\'s signature, and the Executor\'s mark on an escort order, which I intend to frame. Brill has trade routes. Two of them. On paper, which is where everything real begins.$B$BNow all we need is a wagon to go down one.'),
(971504, 1, '(The yard is full. The guards are back, dusty and pleased with themselves; Dren is telling three people at once about the ambush; strangers with packs are asking where a body might sleep. Irena reads the signed receipt twice. Then she stands, straightens her coat and says, loudly enough for the whole yard:)$B$BThe Brill Caravan Office is open.$B$B(Nobody cheers. The Forsaken rarely do. But nobody leaves, either.)$B$BBrill has an inn, a market, and people willing to buy things. The next logical step is paperwork. Lots of paperwork. I\'ll be in my office, $n. It has a door now. Do knock.'),
(971505, 1, 'Three signatures, in three inks, one of them possibly not ink. All valid. Here\'s your fee.$B$BIf Renee told you I owe her for a bottle of port, I don\'t. I have the receipt. I always have the receipt.$B$BSame time tomorrow? Brill will still be here. So, regrettably, will the paperwork.'),
(971506, 1, '(Wenna reads the slip Sevren wrote twice, then folds it very small and tucks it inside her collar.)$B$BResident of Brill. Wenna Dask, seamstress, of Andorhal and... here. (She laughs, and seems startled by it.)$B$BI\'ll tell Marta I\'m keeping the room. Then I\'ll tell Hamlin I can\'t tell one mushroom from another, and we\'ll see if he still wants me.');
INSERT INTO `quest_request_items` (`ID`, `EmoteOnComplete`, `EmoteOnIncomplete`, `CompletionText`) VALUES
(971500, 1, 1, 'Drivers, road, wagons, Magistrate, stake. Any order you like, so long as it ends with the stake.'),
(971501, 1, 1, 'Crates, winch, timber, iron. You can\'t unload a wagon onto good intentions.'),
(971502, 1, 1, 'Cargo, records and a name. I\'ll take the name last. I want to be sure of it.'),
(971503, 1, 1, 'Two agreements, two guards, one road. I\'m told the dead don\'t hurry. I\'m told a great many things.'),
(971504, 1, 1, 'Crates, harness, guards, road, receipt. Then we\'re a caravan office and not a man with a wagon.'),
(971505, 1, 1, 'Signatures, $n. A delivery without a signature is just a walk.'),
(971506, 1, 1, 'Did they say no? You can tell me. I\'ve been told no by better. Well. By worse.');
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES (971500, 971500), (971502, 971501), (971500, 971502), (971500, 971503), (971502, 971504), (971501, 971505), (971528, 971506);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES (971500, 971500), (971502, 971501), (971500, 971502), (971500, 971503), (971500, 971504), (971501, 971505), (971528, 971506);

-- The Old Brewery
INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`) VALUES (971601, 0, 159, 0, 0, 0), (971601, 1, 1179, 0, 0, 0), (971601, 2, 2723, 0, 0, 0), (971601, 3, 2593, 0, 0, 0), (971601, 4, 2594, 0, 0, 0), (971601, 5, 2894, 0, 0, 0), (971601, 6, 4600, 0, 0, 0), (971601, 7, 2596, 0, 0, 0), (971601, 8, 2686, 0, 0, 0), (971601, 9, 18287, 0, 0, 0);
INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`) VALUES (971606, 0, 4470, 0, 0, 0), (971606, 1, 4399, 0, 0, 0), (971606, 2, 4400, 0, 0, 0), (971606, 3, 2880, 0, 0, 0), (971606, 4, 3857, 0, 0, 0), (971606, 5, 5956, 0, 0, 0), (971606, 6, 6217, 0, 0, 0);
INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`) VALUES (971607, 0, 4470, 0, 0, 0), (971607, 1, 4399, 0, 0, 0), (971607, 2, 4400, 0, 0, 0), (971607, 3, 2880, 0, 0, 0), (971607, 4, 3857, 0, 0, 0), (971607, 5, 5956, 0, 0, 0), (971607, 6, 6217, 0, 0, 0);
INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`) VALUES (971609, 0, 2678, 0, 0, 0), (971609, 1, 2692, 0, 0, 0), (971609, 2, 3713, 0, 0, 0), (971609, 3, 2665, 0, 0, 0), (971609, 4, 30817, 0, 0, 0), (971609, 5, 4604, 0, 0, 0), (971609, 6, 4605, 0, 0, 0), (971609, 7, 4606, 0, 0, 0), (971609, 8, 4607, 0, 0, 0), (971609, 9, 159, 0, 0, 0);
INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`) VALUES (971610, 0, 2678, 0, 0, 0), (971610, 1, 2692, 0, 0, 0), (971610, 2, 3713, 0, 0, 0), (971610, 3, 2665, 0, 0, 0), (971610, 4, 30817, 0, 0, 0), (971610, 5, 4604, 0, 0, 0), (971610, 6, 4605, 0, 0, 0), (971610, 7, 4606, 0, 0, 0), (971610, 8, 4607, 0, 0, 0), (971610, 9, 159, 0, 0, 0);
INSERT INTO `creature_template` (`entry`, `name`, `subname`, `gossip_menu_id`, `minlevel`, `maxlevel`, `faction`, `npcflag`, `speed_walk`, `speed_run`, `unit_class`, `unit_flags`, `type`, `rank`, `HealthModifier`, `DamageModifier`, `mingold`, `maxgold`, `flags_extra`, `AIName`, `ScriptName`) VALUES
(971600, 'Brewmaster Oren Blackbarrel', NULL, 0, 25, 25, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971601, 'Brewmaster Oren Blackbarrel', 'The Old Brewery', 0, 25, 25, 68, 131, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971602, 'Bram Lusk', 'Cooper', 0, 20, 20, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971603, 'Calla Fenn', 'Apprentice Brewer', 0, 12, 12, 68, 3, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971604, 'Marta Greaves', 'Wayfarer\'s Rest', 0, 15, 15, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971605, 'Brewhouse Rat', NULL, 0, 8, 9, 14, 0, 1, 1.14286, 1, 512, 1, 0, 0.6, 0.6, 0, 0, 0, '', ''),
(971606, 'Bram Lusk', 'Cooper', 0, 20, 20, 68, 129, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971607, 'Bram Lusk', 'Cooper', 0, 20, 20, 68, 129, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971608, 'Bram Lusk', 'Cooper', 0, 20, 20, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971609, 'Calla Fenn', 'Brewing Ingredients', 0, 12, 12, 68, 129, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971610, 'Calla Fenn', 'Brewing Ingredients', 0, 12, 12, 68, 129, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971611, 'Calla Fenn', 'Apprentice Brewer', 0, 12, 12, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971612, 'Tasting Room Regular', NULL, 0, 10, 10, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971613, 'Brewmaster Oren Blackbarrel', 'The Old Brewery', 0, 25, 25, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971614, 'Brewmaster Oren Blackbarrel', 'The Old Brewery', 0, 25, 25, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971615, 'Oswin Thatcher', 'Carpenter', 0, 25, 25, 68, 1, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971616, 'Builder\'s Yard Laborer', NULL, 0, 15, 15, 68, 0, 1, 1.14286, 1, 0, 6, 0, 1, 1, 0, 0, 2, '', ''),
(971617, 'The old brewhouse looked into', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971618, 'Piles of spoiled stores cleared', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971619, 'Oren\'s brewing ledger found', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971620, 'Copper tubing salvaged', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971621, 'Sound oak staves', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971622, 'Iron hoops from Oliver Dwor', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971623, 'Vats repaired and casks assembled', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971624, 'Ingredients gathered', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971625, 'Experimental batches set going', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971626, 'Townspeople who tasted the batches', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971627, 'A recipe chosen for Oren', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971628, 'Spoiled barrels examined', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971629, 'Bram and Calla questioned', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971630, 'Cellar searched and growths cut out', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971631, 'Cellar vent repaired', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971632, 'Invitations delivered', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971633, 'Sample barrels tapped at the market', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971634, 'Tasting room set up', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971635, 'Signature drink named', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971636, 'Fresh bitterroot cut', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971637, 'Innkeeper Renee\'s verdict', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971638, 'Deathguard Burgess\'s verdict', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', ''),
(971639, 'Hamlin Atkins\'s verdict', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 1, 1, 0, 0, 130, '', '');
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`) VALUES
(971600, 0, 3652, 1, 1),
(971601, 0, 3652, 1, 1),
(971602, 0, 2615, 1, 1),
(971603, 0, 4528, 1, 1),
(971604, 0, 2670, 1, 1),
(971605, 0, 1141, 1.5, 1),
(971606, 0, 2615, 1, 1),
(971607, 0, 2615, 1, 1),
(971608, 0, 2615, 1, 1),
(971609, 0, 4528, 1, 1),
(971610, 0, 4528, 1, 1),
(971611, 0, 4528, 1, 1),
(971612, 0, 2632, 1, 1),
(971612, 1, 2634, 1, 1),
(971612, 2, 2657, 1, 1),
(971613, 0, 3652, 1, 1),
(971614, 0, 3652, 1, 1),
(971615, 0, 1638, 1, 1),
(971616, 0, 3516, 1, 1),
(971616, 1, 1638, 1, 1),
(971616, 2, 1604, 1, 1),
(971617, 0, 11686, 1, 1),
(971618, 0, 11686, 1, 1),
(971619, 0, 11686, 1, 1),
(971620, 0, 11686, 1, 1),
(971621, 0, 11686, 1, 1),
(971622, 0, 11686, 1, 1),
(971623, 0, 11686, 1, 1),
(971624, 0, 11686, 1, 1),
(971625, 0, 11686, 1, 1),
(971626, 0, 11686, 1, 1),
(971627, 0, 11686, 1, 1),
(971628, 0, 11686, 1, 1),
(971629, 0, 11686, 1, 1),
(971630, 0, 11686, 1, 1),
(971631, 0, 11686, 1, 1),
(971632, 0, 11686, 1, 1),
(971633, 0, 11686, 1, 1),
(971634, 0, 11686, 1, 1),
(971635, 0, 11686, 1, 1),
(971636, 0, 11686, 1, 1),
(971637, 0, 11686, 1, 1),
(971638, 0, 11686, 1, 1),
(971639, 0, 11686, 1, 1);
INSERT INTO `creature` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(971600, 971600, 0, 85, 0, 1, 64, 2220.120, 267.760, 34.770, 5.1500, 60, 0, 0, 'mod-brill-home town'),
(971601, 971601, 0, 85, 0, 1, 1, 2222.010, 279.790, 36.080, 3.5780, 60, 0, 0, 'mod-brill-home town'),
(971602, 971602, 0, 85, 0, 1, 64, 2210.860, 266.310, 35.500, 5.6700, 60, 0, 0, 'mod-brill-home town'),
(971603, 971603, 0, 85, 0, 1, 64, 2227.990, 270.990, 34.720, 5.1500, 60, 0, 0, 'mod-brill-home town'),
(971604, 971604, 0, 85, 0, 1, 1, 2202.450, 289.290, 35.160, 5.2400, 60, 0, 0, 'mod-brill-home town'),
(971605, 971605, 0, 85, 0, 1, 64, 2216.280, 292.560, 35.080, 0.4400, 90, 3, 1, 'mod-brill-home town'),
(971606, 971605, 0, 85, 0, 1, 64, 2218.550, 293.620, 35.160, 0.4400, 90, 3, 1, 'mod-brill-home town'),
(971607, 971605, 0, 85, 0, 1, 64, 2216.340, 294.790, 35.090, 0.4400, 90, 3, 1, 'mod-brill-home town'),
(971608, 971605, 0, 85, 0, 1, 64, 2220.960, 291.980, 35.190, 0.4400, 90, 3, 1, 'mod-brill-home town'),
(971609, 971605, 0, 85, 0, 1, 64, 2213.860, 294.190, 34.790, 0.4400, 90, 3, 1, 'mod-brill-home town'),
(971610, 971605, 0, 85, 0, 1, 64, 2219.720, 295.820, 35.170, 0.4400, 90, 3, 1, 'mod-brill-home town'),
(971611, 971606, 0, 85, 0, 1, 1, 2210.410, 266.100, 35.520, 5.6700, 60, 0, 0, 'mod-brill-home town'),
(971612, 971607, 0, 85, 0, 1, 1, 2206.060, 270.690, 37.020, 0.4400, 60, 0, 0, 'mod-brill-home town'),
(971613, 971608, 0, 85, 0, 1, 1, 2215.880, 274.500, 36.080, 5.1500, 60, 0, 0, 'mod-brill-home town'),
(971614, 971609, 0, 85, 0, 1, 1, 2214.370, 280.080, 36.080, 3.5780, 60, 0, 0, 'mod-brill-home town'),
(971615, 971610, 0, 85, 0, 1, 1, 2232.460, 270.870, 34.450, 5.1500, 60, 0, 0, 'mod-brill-home town'),
(971616, 971611, 0, 85, 0, 1, 1, 2215.340, 291.020, 34.970, 2.0100, 60, 0, 0, 'mod-brill-home town'),
(971617, 971612, 0, 85, 0, 1, 1, 2221.380, 274.530, 36.080, 2.0100, 60, 0, 0, 'mod-brill-home town'),
(971618, 971612, 0, 85, 0, 1, 1, 2229.660, 261.500, 34.110, 2.0100, 60, 0, 0, 'mod-brill-home town'),
(971619, 971612, 0, 85, 0, 1, 1, 2233.750, 265.730, 34.110, 5.1500, 60, 0, 0, 'mod-brill-home town'),
(971620, 971613, 0, 85, 0, 1, 1, 2264.000, 248.000, 33.710, 0.2000, 60, 0, 0, 'mod-brill-home town'),
(971621, 971614, 0, 85, 0, 1, 1, 2188.260, 278.890, 42.100, 1.5900, 60, 0, 0, 'mod-brill-home town'),
(971622, 971615, 0, 85, 0, 1, 64, 2217.870, 260.750, 34.410, 1.4500, 60, 0, 0, 'mod-brill-home town'),
(971623, 971616, 0, 85, 0, 1, 64, 2215.150, 267.760, 35.150, 0.9600, 60, 3, 1, 'mod-brill-home town'),
(971624, 971616, 0, 85, 0, 1, 64, 2220.050, 291.560, 35.180, 3.9300, 60, 3, 1, 'mod-brill-home town');
INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `Data0`, `Data1`, `ScriptName`) VALUES
(971600, 33, 8020, 'Old Brewhouse', 1, 0, 0, ''),
(971601, 33, 7432, 'The Old Brewery', 1, 0, 0, ''),
(971602, 10, 6513, 'Old Brewing Copper', 1, 0, 971600, 'go_brill_town'),
(971603, 10, 2129, 'Spoiled Brewing Stores', 0.6, 0, 971600, 'go_brill_town'),
(971604, 10, 184, 'Fallen Shelf', 1, 0, 971600, 'go_brill_town'),
(971605, 10, 1108, 'Cellar Hatch', 1, 0, 971603, 'go_brill_town'),
(971606, 5, 234, 'Cooper\'s Bench', 1, 0, 0, ''),
(971607, 5, 1108, 'Cask Staves', 1, 0, 0, ''),
(971608, 10, 32, 'Fermentation Vat', 1.6, 0, 971601, 'go_brill_town'),
(971609, 10, 32, 'Unhooped Cask', 1, 0, 971601, 'go_brill_town'),
(971610, 10, 8026, 'Rotten Cask', 0.8, 0, 971601, 'go_brill_town'),
(971611, 10, 6639, 'Junked Pump', 1, 0, 971601, 'go_brill_town'),
(971612, 5, 216, 'Brewing Kettle', 1, 0, 0, ''),
(971613, 5, 348, 'Brewhouse Furnace', 1, 0, 0, ''),
(971614, 5, 189, 'Brewing Shelves', 1, 0, 0, ''),
(971615, 5, 6036, 'New Cask', 1, 0, 0, ''),
(971616, 5, 95, 'Chimney Smoke', 1, 0, 0, ''),
(971617, 2, 301, 'Bitterroot', 0.8, 0, 0, 'go_brill_town'),
(971618, 10, 216, 'Experimental Mash Tub', 0.8, 0, 971602, 'go_brill_town'),
(971619, 10, 216, 'Experimental Mash Tub', 0.8, 0, 971602, 'go_brill_town'),
(971620, 10, 216, 'Experimental Mash Tub', 0.8, 0, 971602, 'go_brill_town'),
(971621, 10, 7470, 'Spoiled Barrel', 1, 0, 971603, 'go_brill_town'),
(971622, 10, 6432, 'Wall-Rot', 0.45, 0, 971603, 'go_brill_town'),
(971623, 10, 7969, 'Cellar Vent', 0.15, 0, 971603, 'go_brill_town'),
(971624, 5, 189, 'Cask Racks', 1, 0, 0, ''),
(971625, 10, 1727, 'Old Brewery Sample Barrel', 1, 0, 971604, 'go_brill_town'),
(971626, 10, 221, 'Tasting Room Trestle', 1, 0, 971604, 'go_brill_town'),
(971627, 5, 7732, 'Brewery Counter', 1, 0, 0, ''),
(971628, 5, 319, 'Ale Keg', 1, 0, 0, ''),
(971629, 5, 32, 'Fermentation Vat', 1.6, 0, 0, ''),
(971630, 5, 221, 'Table', 1, 0, 0, ''),
(971631, 5, 603, 'Bench', 1, 0, 0, ''),
(971632, 5, 4073, 'Bottle Shelf', 1, 0, 0, ''),
(971633, 5, 1727, 'Barrel Stand', 0.7, 0, 0, ''),
(971634, 5, 189, 'Drinks Cabinet', 0.45, 0, 0, '');
INSERT INTO `gameobject_template_addon` (`entry`, `faction`, `flags`) VALUES (971600, 0, 32), (971601, 0, 32), (971602, 0, 4), (971603, 0, 4), (971604, 0, 4), (971605, 0, 4), (971608, 0, 4), (971609, 0, 4), (971610, 0, 4), (971611, 0, 4), (971618, 0, 4), (971619, 0, 4), (971620, 0, 4), (971621, 0, 4), (971622, 0, 4), (971623, 0, 4), (971625, 0, 4), (971626, 0, 4);
INSERT INTO `gameobject` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`, `animprogress`, `state`, `Comment`) VALUES
(971600, 971600, 0, 85, 0, 1, 64, 2217.000, 278.000, 31.980, 0.4360, 0, 0, 0.216277, 0.976332, 0, 255, 1, 'mod-brill-home town'),
(971601, 971601, 0, 85, 0, 1, 1, 2217.000, 278.000, 31.980, 0.4360, 0, 0, 0.216277, 0.976332, 0, 255, 1, 'mod-brill-home town'),
(971602, 971602, 0, 85, 0, 1, 64, 2215.550, 265.740, 34.980, 2.0070, 0, 0, 0.843357, 0.537354, 0, 255, 1, 'mod-brill-home town'),
(971603, 971603, 0, 85, 0, 1, 64, 2219.320, 264.740, 34.600, 0.4360, 0, 0, 0.216277, 0.976332, 0, 255, 1, 'mod-brill-home town'),
(971604, 971603, 0, 85, 0, 1, 64, 2217.030, 262.560, 34.610, 1.1340, 0, 0, 0.537104, 0.843516, 0, 255, 1, 'mod-brill-home town'),
(971605, 971603, 0, 85, 0, 1, 64, 2224.000, 264.160, 34.310, 1.8330, 0, 0, 0.793476, 0.608601, 0, 255, 1, 'mod-brill-home town'),
(971606, 971603, 0, 85, 0, 1, 64, 2224.340, 268.180, 34.650, 2.5310, 0, 0, 0.953758, 0.300576, 0, 255, 1, 'mod-brill-home town'),
(971607, 971603, 0, 85, 0, 1, 64, 2224.580, 260.570, 34.120, 3.2290, 0, 0, 0.999045, -0.043690, 0, 255, 1, 'mod-brill-home town'),
(971608, 971603, 0, 85, 0, 1, 64, 2227.570, 263.620, 34.190, 3.9270, 0, 0, 0.923878, -0.382688, 0, 255, 1, 'mod-brill-home town'),
(971609, 971604, 0, 85, 0, 1, 64, 2222.290, 291.500, 35.190, 0.9600, 0, 0, 0.461779, 0.886995, 0, 255, 1, 'mod-brill-home town'),
(971610, 971605, 0, 85, 0, 1, 1, 2216.670, 290.540, 35.120, 0.4360, 0, 0, 0.216277, 0.976332, 0, 255, 1, 'mod-brill-home town'),
(971611, 971606, 0, 85, 0, 1, 1, 2208.420, 266.830, 35.840, 2.0100, 0, 0, 0.844162, 0.536088, 0, 255, 1, 'mod-brill-home town'),
(971612, 971607, 0, 85, 0, 1, 1, 2205.550, 268.250, 36.730, 0.9600, 0, 0, 0.461779, 0.886995, 0, 255, 1, 'mod-brill-home town'),
(971613, 971608, 0, 85, 0, 1, 1, 2207.210, 271.780, 36.760, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971614, 971608, 0, 85, 0, 1, 1, 2205.310, 275.860, 37.480, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971615, 971609, 0, 85, 0, 1, 64, 2209.660, 262.990, 35.150, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971616, 971609, 0, 85, 0, 1, 64, 2206.790, 264.410, 35.770, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971617, 971609, 0, 85, 0, 1, 64, 2209.140, 260.540, 34.850, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971618, 971610, 0, 85, 0, 1, 64, 2207.820, 285.860, 34.990, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971619, 971610, 0, 85, 0, 1, 64, 2204.920, 286.160, 35.560, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971620, 971610, 0, 85, 0, 1, 64, 2207.460, 289.000, 34.570, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971621, 971610, 0, 85, 0, 1, 64, 2203.950, 283.500, 36.690, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971622, 971610, 0, 85, 0, 1, 64, 2205.010, 289.510, 34.710, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971623, 971610, 0, 85, 0, 1, 64, 2202.020, 286.460, 36.130, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971624, 971611, 0, 85, 0, 1, 1, 2088.000, 262.000, 57.190, 1.5000, 0, 0, 0.681639, 0.731689, 0, 255, 1, 'mod-brill-home town'),
(971625, 971612, 0, 85, 0, 1, 1, 2203.650, 272.330, 37.880, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971626, 971613, 0, 85, 0, 1, 1, 2203.620, 279.480, 37.810, 2.0100, 0, 0, 0.844162, 0.536088, 0, 255, 1, 'mod-brill-home town'),
(971627, 971614, 0, 85, 0, 1, 1, 2201.320, 277.310, 38.820, 2.0100, 0, 0, 0.844162, 0.536088, 0, 255, 1, 'mod-brill-home town'),
(971628, 971615, 0, 85, 0, 1, 1, 2201.680, 274.170, 38.760, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971629, 971615, 0, 85, 0, 1, 1, 2204.460, 269.390, 37.210, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971630, 971616, 0, 85, 0, 1, 1, 2215.270, 285.250, 48.980, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971631, 971617, 0, 85, 0, 1, 1, 2150.000, 300.000, 46.950, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home town'),
(971632, 971617, 0, 85, 0, 1, 1, 2158.000, 312.000, 43.780, 1.6000, 0, 0, 0.717356, 0.696707, 0, 255, 1, 'mod-brill-home town'),
(971633, 971617, 0, 85, 0, 1, 1, 2145.000, 285.000, 49.690, 3.1000, 0, 0, 0.999784, 0.020795, 0, 255, 1, 'mod-brill-home town'),
(971634, 971617, 0, 85, 0, 1, 1, 2162.000, 325.000, 42.290, 4.4000, 0, 0, 0.808496, -0.588501, 0, 255, 1, 'mod-brill-home town'),
(971635, 971618, 0, 85, 0, 1, 64, 2228.140, 268.300, 34.510, 0.4360, 0, 0, 0.216277, 0.976332, 0, 255, 1, 'mod-brill-home town'),
(971636, 971619, 0, 85, 0, 1, 64, 2230.410, 269.360, 34.480, 0.4360, 0, 0, 0.216277, 0.976332, 0, 255, 1, 'mod-brill-home town'),
(971637, 971620, 0, 85, 0, 1, 64, 2231.170, 272.470, 34.660, 0.4360, 0, 0, 0.216277, 0.976332, 0, 255, 1, 'mod-brill-home town'),
(971638, 971621, 0, 85, 0, 1, 64, 2213.050, 288.850, 34.720, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971639, 971621, 0, 85, 0, 1, 64, 2210.630, 290.480, 34.530, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971640, 971621, 0, 85, 0, 1, 64, 2212.260, 292.890, 34.600, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971641, 971622, 0, 85, 0, 1, 64, 2215.210, 287.760, 34.960, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971642, 971622, 0, 85, 0, 1, 64, 2219.700, 289.960, 35.170, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971643, 971622, 0, 85, 0, 1, 64, 2217.060, 288.510, 35.120, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971644, 971623, 0, 85, 0, 1, 1, 2212.860, 286.880, 34.750, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971645, 971624, 0, 85, 0, 1, 1, 2210.620, 286.940, 34.690, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971646, 971625, 0, 85, 0, 1, 1, 2250.500, 267.500, 34.340, 2.6000, 0, 0, 0.963558, 0.267499, 0, 255, 1, 'mod-brill-home town'),
(971647, 971625, 0, 85, 0, 1, 1, 2257.500, 278.000, 34.270, 2.5000, 0, 0, 0.948985, 0.315322, 0, 255, 1, 'mod-brill-home town'),
(971648, 971625, 0, 85, 0, 1, 1, 2246.000, 274.000, 34.110, 2.6000, 0, 0, 0.963558, 0.267499, 0, 255, 1, 'mod-brill-home town'),
(971649, 971626, 0, 85, 0, 1, 64, 2228.960, 265.370, 34.280, 0.4360, 0, 0, 0.216277, 0.976332, 0, 255, 1, 'mod-brill-home town'),
(971650, 971627, 0, 85, 0, 1, 1, 2220.380, 279.030, 36.080, 0.4360, 0, 0, 0.216277, 0.976332, 0, 255, 1, 'mod-brill-home town'),
(971651, 971628, 0, 85, 0, 1, 1, 2224.100, 277.450, 36.960, 3.5780, 0, 0, 0.976288, -0.216476, 0, 255, 1, 'mod-brill-home town'),
(971652, 971628, 0, 85, 0, 1, 1, 2221.560, 282.890, 36.960, 3.5780, 0, 0, 0.976288, -0.216476, 0, 255, 1, 'mod-brill-home town'),
(971653, 971629, 0, 85, 0, 1, 1, 2211.290, 280.300, 36.080, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971654, 971630, 0, 85, 0, 1, 1, 2216.210, 273.770, 36.080, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971655, 971630, 0, 85, 0, 1, 1, 2220.960, 275.430, 36.080, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971656, 971631, 0, 85, 0, 1, 1, 2216.850, 272.410, 36.080, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971657, 971631, 0, 85, 0, 1, 1, 2215.580, 275.130, 36.080, 3.5800, 0, 0, 0.976071, -0.217452, 0, 255, 1, 'mod-brill-home town'),
(971658, 971631, 0, 85, 0, 1, 1, 2221.590, 274.070, 36.080, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971659, 971631, 0, 85, 0, 1, 1, 2220.320, 276.790, 36.080, 3.5800, 0, 0, 0.976071, -0.217452, 0, 255, 1, 'mod-brill-home town'),
(971660, 971632, 0, 85, 0, 1, 1, 2212.530, 274.810, 36.080, 0.4400, 0, 0, 0.218230, 0.975897, 0, 255, 1, 'mod-brill-home town'),
(971661, 971633, 0, 85, 0, 1, 1, 2276.843, 476.606, 34.060, 1.9199, 0, 0, 0.819165, 0.573558, 0, 255, 1, 'mod-brill-home town'),
(971662, 971634, 0, 85, 0, 1, 1, 2279.074, 484.218, 34.060, 5.0615, 0, 0, 0.573558, -0.819165, 0, 255, 1, 'mod-brill-home town');
INSERT INTO `brill_town_use` (`go`, `ord`, `cond`, `quest`, `credit`, `text_id`, `marker`, `tele_map`, `tele_x`, `tele_y`, `tele_z`, `tele_o`) VALUES
(971602, 0, 'I971600', 971600, 971617, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971603, 0, 'I971600', 971600, 971618, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971604, 0, 'I971600', 971600, 971619, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971605, 0, 'I971603', 971603, 971630, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971608, 0, 'I971601', 971601, 971623, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971609, 0, 'I971601', 971601, 971623, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971610, 0, 'I971601', 971601, 971621, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971611, 0, 'I971601', 971601, 971620, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971617, 0, 'I971602', 971602, 971624, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971617, 1, 'I971605', 971605, 971636, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971618, 0, 'I971602', 971602, 971625, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971619, 0, 'I971602', 971602, 971625, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971620, 0, 'I971602', 971602, 971625, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971621, 0, 'I971603', 971603, 971628, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971622, 0, 'I971603', 971603, 971630, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971623, 0, 'I971603', 971603, 971631, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971625, 0, 'I971604', 971604, 971633, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000),
(971626, 0, 'I971604', 971604, 971634, 0, 0, -1, 0.000, 0.000, 0.000, 0.0000);
INSERT INTO `brill_town_gossip` (`npc`, `ord`, `kind`, `cond`, `icon`, `text`, `text_id`, `action`, `quest`, `credit`, `marker`, `emote`, `reply`, `arg`) VALUES
(971600, 14000, 'greet', 'R971603', 0, NULL, 971600, '', 0, 0, 0, 0, NULL, 0),
(971600, 14001, 'greet', 'R971601', 0, NULL, 971601, '', 0, 0, 0, 0, NULL, 0),
(971600, 14002, 'greet', 'R971600', 0, NULL, 971602, '', 0, 0, 0, 0, NULL, 0),
(971600, 14003, 'greet', '', 0, NULL, 971603, '', 0, 0, 0, 0, NULL, 0),
(971600, 14004, 'option', 'I971604', 0, 'Call it Gravemalt Stout.', 0, 'choice', 971604, 971635, 971619, 273, 'Gravemalt Stout. Dark, bitter, and it\'ll stain your teeth, if you\'ve still got any. (Oren chalks it on the slate.) Brill will drink it out of spite. Good.', 0),
(971600, 14005, 'option', 'I971604', 0, 'Call it Lordaeron Reserve.', 0, 'choice', 971604, 971635, 971620, 273, 'Lordaeron Reserve. (Oren is quiet for a moment.) My father\'s ale, under the old kingdom\'s name. Folk will order it and think of something. That\'s all a name\'s for, really.', 0),
(971600, 14006, 'option', 'I971604', 0, 'Call it Blackroot Bitter.', 0, 'choice', 971604, 971635, 971621, 273, 'Blackroot Bitter. Herbal, harsh, brewed for the palates we\'ve got and not the ones we lost. Calla will be insufferable. (He chalks it anyway, large.)', 0),
(971601, 14007, 'greet', 'R971504 D3', 0, NULL, 971604, '', 0, 0, 0, 0, NULL, 0),
(971601, 14008, 'greet', 'R971619', 0, NULL, 971605, '', 0, 0, 0, 0, NULL, 0),
(971601, 14009, 'greet', 'R971620', 0, NULL, 971606, '', 0, 0, 0, 0, NULL, 0),
(971601, 14010, 'greet', 'R971621', 0, NULL, 971607, '', 0, 0, 0, 0, NULL, 0),
(971601, 14011, 'option', 'R971604', 1, 'What are you pouring?', 0, 'vendor', 0, 0, 0, 0, NULL, 0),
(971601, 14012, 'option', 'R971604', 1, 'Could you send something round to my house?', 0, 'buy', 0, 0, 971606, 1, 'For the house by the road? A barrel stand with a cask on it, mugs that don\'t leak, and a little cabinet Bram knocked together from the old vats\' staves. I\'ll have Bram cart it over. (He takes your coin.) And a sign for the cabinet. Everybody should have a brewery sign in the house. It reminds you where you\'d rather be.', 7500),
(971613, 14013, 'greet', '', 0, NULL, 971608, '', 0, 0, 0, 0, NULL, 0),
(971614, 14014, 'greet', '', 0, NULL, 971609, '', 0, 0, 0, 0, NULL, 0),
(971602, 14015, 'greet', 'R971601', 0, NULL, 971610, '', 0, 0, 0, 0, NULL, 0),
(971602, 14016, 'greet', '', 0, NULL, 971611, '', 0, 0, 0, 0, NULL, 0),
(971602, 14017, 'option', 'I971603', 0, 'Oren thinks someone spoiled the batch. What do you know?', 0, 'credit', 971603, 971629, 971615, 1, 'Someone. (Bram runs a thumb down a stave and shows you the green on it.) Look at the wood, not the people. That\'s growing out of the oak. My casks were sound when they left my bench. It got in after. It got in from somewhere with walls.', 0),
(971606, 14018, 'greet', '', 0, NULL, 971612, '', 0, 0, 0, 0, NULL, 0),
(971606, 14019, 'option', '', 1, 'Show me what a cooper sells.', 0, 'vendor', 0, 0, 0, 0, NULL, 0),
(971607, 14020, 'greet', '', 0, NULL, 971613, '', 0, 0, 0, 0, NULL, 0),
(971607, 14021, 'option', '', 1, 'Show me what a cooper sells.', 0, 'vendor', 0, 0, 0, 0, NULL, 0),
(971608, 14022, 'greet', '', 0, NULL, 971614, '', 0, 0, 0, 0, NULL, 0),
(971603, 14023, 'greet', 'R971603', 0, NULL, 971615, '', 0, 0, 0, 0, NULL, 0),
(971603, 14024, 'greet', 'R971602', 0, NULL, 971616, '', 0, 0, 0, 0, NULL, 0),
(971603, 14025, 'greet', '', 0, NULL, 971617, '', 0, 0, 0, 0, NULL, 0),
(971603, 14026, 'option', 'I971602 R971609 R971610 R971611', 0, 'Refine the dark batch, with Hamlin\'s culture.', 0, 'choice', 971602, 971627, 971612, 273, 'The dark one. Hamlin\'s "excellent". Good: it\'s got body, it\'s got a cellar in it. Oren will say it isn\'t ale. Oren will be right, and then he\'ll drink three.', 0),
(971603, 14027, 'option', 'I971602 R971609 R971610 R971611', 0, 'Refine the old family brown. Oren deserves his father\'s ale.', 0, 'choice', 971602, 971627, 971613, 273, 'The family brown. Dillinger\'s "mud". (Calla sighs.) Fine. Sentiment. I\'ll tell him, and I\'ll pretend I\'m not pleased, and you\'ll pretend you can\'t see me pretending.', 0),
(971603, 14028, 'option', 'I971602 R971609 R971610 R971611', 0, 'Refine the bitterroot batch.', 0, 'choice', 971602, 971627, 971614, 273, 'The bitterroot. Zygand\'s mystery. Yes. Yes! If it made the Executor feel something, it\'ll make anybody feel something. Possibly alarm. Alarm is a flavor.', 0),
(971603, 14029, 'option', 'I971603', 0, 'Oren thinks your cultures spoiled the batch.', 0, 'credit', 971603, 971629, 971616, 1, 'My cultures are in sealed jars in the yard, because I\'m not an idiot. (Calla\'s voice is very level.) Go and look at the cellar, $n. Smell the walls. I told him in the spring the walls smelled wrong. He told me walls don\'t smell. Walls absolutely smell.', 0),
(971609, 14030, 'greet', 'R971604', 0, NULL, 971618, '', 0, 0, 0, 0, NULL, 0),
(971609, 14031, 'option', '', 1, 'What have you got for brewing and cooking?', 0, 'vendor', 0, 0, 0, 0, NULL, 0),
(971610, 14032, 'greet', '', 0, NULL, 971619, '', 0, 0, 0, 0, NULL, 0),
(971610, 14033, 'option', '', 1, 'What have you got for brewing and cooking?', 0, 'vendor', 0, 0, 0, 0, NULL, 0),
(971611, 14034, 'greet', '', 0, NULL, 971620, '', 0, 0, 0, 0, NULL, 0),
(971612, 14035, 'greet', '', 0, NULL, 971621, '', 0, 0, 0, 0, NULL, 0),
(971604, 14036, 'greet', 'R971504 R971604', 0, NULL, 971622, '', 0, 0, 0, 0, NULL, 0),
(971604, 14037, 'greet', 'R971504', 0, NULL, 971623, '', 0, 0, 0, 0, NULL, 0),
(971604, 14038, 'greet', 'R971604', 0, NULL, 971624, '', 0, 0, 0, 0, NULL, 0),
(971604, 14039, 'greet', '', 0, NULL, 971625, '', 0, 0, 0, 0, NULL, 0),
(971604, 14040, 'option', 'I971604', 0, 'Oren invites you to the brewery\'s opening.', 0, 'credit', 971604, 971632, 971618, 11, 'Free drink, is it? Free drinks are the dearest kind; you pay in conversation. (Marta tucks the invitation into her apron.) I\'ll come. I\'ll want a word about his barrel price, too. Twelve silver a cask! For water with ideas!', 0),
(5688, 14041, 'option', 'I971604', 0, 'Brewmaster Blackbarrel invites you to the brewery\'s opening.', 0, 'credit', 971604, 971632, 971617, 1, 'An invitation! (Renee reads it twice.) Competition, a stone\'s throw from my door. Tell him I\'ll come, and I\'ll bring my own mug, and if his ale\'s better than mine I\'ll buy the recipe, and if it\'s worse I\'ll buy him a drink. Either way he loses.', 0),
(2136, 14042, 'option', 'I971601', 0, 'Bram Lusk the cooper needs iron hoops.', 0, 'credit', 971601, 971622, 0, 4, 'Bram\'s coopering again? (Oliver laughs, a rusty sound.) I made his hoops when we were both breathing. Here: twenty, all sizes, and a hoop-driver he\'ll pretend he doesn\'t need. Tell him the first barrel\'s mine.', 0),
(3547, 14043, 'option', 'I971602', 0, 'Calla Fenn would like a fungal culture. Your blue caps are the finest in Tirisfal.', 0, 'credit', 971602, 971624, 971607, 4, 'Finest in Tirisfal! Finest in Lordaeron, I\'d say, but nobody\'s measured. (He scoops a grey-blue crust into a jar.) The mother culture. Started from a cap my grandfather grew in his boot. Tell the girl to feed it barley and talk to it kindly.', 0),
(33996, 14044, 'option', 'I971602', 0, 'The old brewhouse needs a sack of brewing grain.', 0, 'credit', 971602, 971624, 971608, 4, 'Brewing grain! For a brewery! (William heaves a sack onto your shoulder before you can object.) Do you know how long it\'s been since anyone asked me for grain that wasn\'t for bats? On the house. No. Not on the house. Tell Oren it\'s on the house, and I\'ll charge him double later.', 0),
(3547, 14045, 'option', 'I971602', 0, 'Would you taste one of Calla\'s experimental batches?', 0, 'credit', 971602, 971626, 971609, 4, '(Hamlin takes a long pull of the dark batch, and his eyes go wide.) Oh, that\'s the blue in it. That\'s my blue! That\'s excellent, that is. Earthy. Like a good cellar. I\'ll have another, if it\'s going.', 0),
(1496, 14046, 'option', 'I971602', 0, 'Would you taste one of the brewery\'s experimental batches?', 0, 'credit', 971602, 971626, 971610, 274, '(Dillinger sniffs the old brown, sips, and sets it down with great care.) It tastes like mud, $g sir:madam;. I spent the Third War in a trench, so I\'m qualified to say. It tastes like that trench.', 0),
(1515, 14047, 'option', 'I971602', 0, 'Would you taste one of the brewery\'s experimental batches?', 0, 'credit', 971602, 971626, 971611, 1, '(Zygand drinks the bitterroot batch in one swallow and stands very still.) ...I tasted that. I haven\'t tasted anything since Andorhal. (A long pause.) I have no idea whether it was good. Don\'t ask me again until I\'ve decided.', 0),
(5688, 14048, 'option', 'I971605', 0, 'This week\'s Brewer\'s Special, for your verdict.', 0, 'credit', 971605, 971637, 0, 1, '(Renee sips.) Interesting. ...That\'s an innkeeper\'s word, love. It means I\'ll sell it, but I won\'t drink it.', 0),
(1652, 14049, 'option', 'I971605', 0, 'The Old Brewery\'s special. Your verdict?', 0, 'credit', 971605, 971638, 0, 6, '(Burgess drinks it like medicine.) Interesting. Is it meant to fizz in the nose? I haven\'t got a nose. It\'s fizzing anyway.', 0),
(3547, 14050, 'option', 'I971605', 0, 'Calla\'s latest. What do you make of it?', 0, 'credit', 971605, 971639, 0, 4, '(Hamlin drinks and blinks, slowly.) I can see sounds. Lovely. Is that the culture? Tell her to keep feeding it.', 0),
(2132, 14051, 'option', 'F80 R971604', 0, 'What do you make of Oren\'s brewing?', 0, 'say', 0, 0, 0, 1, 'His bitterroot\'s picked too late and his hops are three years old; he keeps them in a sack by the furnace, the poor things. I took him a jar of dried nightshade and a pinch of grave moss, ground fine. He held them as if I\'d handed him a live toad. (She smiles.) He\'ll use them. He\'ll say it was his idea. I\'ll let him.', 0),
(971615, 14052, 'greet', 'O', 0, NULL, 971626, '', 0, 0, 0, 0, NULL, 0),
(971615, 14053, 'greet', '', 0, NULL, 971627, '', 0, 0, 0, 0, NULL, 0);
UPDATE `creature_template` SET `npcflag` = `npcflag` | 1 WHERE `entry` IN (1496, 1515, 1652, 2132, 2136, 3547, 5688, 33996);
INSERT INTO `brill_town_phase` (`bit`, `ord`, `cond`) VALUES
(64, 0, '!R971604');
INSERT INTO `brill_town_stage` (`type`, `value`, `ord`, `cond`) VALUES
(9, 1, 0, 'R971000'),
(9, 2, 0, 'R971600'),
(9, 3, 0, 'R971601'),
(9, 4, 0, 'R971602'),
(9, 5, 0, 'R971603'),
(9, 6, 0, 'R971604'),
(9, 7, 0, 'R971606');
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `Flags`, `RewardXPDifficulty`, `RewardMoney`, `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `AreaDescription`, `QuestCompletionLog`, `RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `ObjectiveText1`, `RequiredNpcOrGo2`, `RequiredNpcOrGoCount2`, `ObjectiveText2`, `RequiredNpcOrGo3`, `RequiredNpcOrGoCount3`, `ObjectiveText3`, `RequiredNpcOrGo4`, `RequiredNpcOrGoCount4`, `ObjectiveText4`, `RewardItem1`, `RewardAmount1`, `RewardItem2`, `RewardAmount2`, `RewardItem3`, `RewardAmount3`, `RewardItem4`, `RewardAmount4`) VALUES
(971600, 2, -1, 10, 159, 0, 3, 1200, 0, 'The Kegs Are Empty', 'Look into the old brewhouse beside the Gallows\' End, clear 6 piles of spoiled brewing stores from its yard, kill 6 Brewhouse Rats nesting by the cellar hatch behind it and find Oren\'s old brewing ledger. Then bring it to Brewmaster Oren Blackbarrel.', 'Don\'t tell me. You\'ve come to ask what use a brewery is in a town where half the drinkers can\'t taste and the other half can\'t swallow.$B$BI\'ve heard it. From the Magistrate, from the Deathguard, from a bat. I\'ll tell you what I told the bat. A brewery isn\'t about the beer. It\'s the work: the malting, the mashing, the waiting, and at the end of it a room full of people arguing whether it was worth the wait. Brill has nowhere to argue.$B$BThis was my brewhouse, and my father\'s before me. It\'s still standing, more or less, but it\'s full of rot and rats. Look inside. Clear out what\'s spoiled, kill whatever\'s nesting by the cellar, and find my ledger. Green leather. If the rats have eaten it, I want to know which rat.', '', 'Return to Brewmaster Oren Blackbarrel at the old brewhouse in Brill.', 971617, 1, 'The old brewhouse looked into', 971618, 6, 'Piles of spoiled stores cleared', 971605, 6, '', 971619, 1, 'Oren\'s brewing ledger found', 0, 0, 0, 0, 0, 0, 0, 0),
(971601, 2, -1, 10, 159, 0, 3, 1500, 0, 'A Proper Fermentation', 'Salvage copper tubing from the goblins\' junked pump below the zeppelin tower west of Brill, 6 sound oak staves from the rotten casks behind the brewhouse and iron hoops from Oliver Dwor by Brill\'s smithy, then help Bram Lusk repair the 2 fermentation vats and assemble the 3 storage casks in the brewhouse yard.', 'Bram Lusk. Cooper. I made the barrels for this brewhouse, and for the Gallows\' End, and for every farm between here and Agamand Mills. Then the plague came, and nobody needed barrels for anything but the one thing, and those don\'t have to hold water.$B$BOren says the vats can be saved. Oren is half right. The wood\'s good. The copper\'s gone: the tubing from the cooler rotted through, and you can\'t brew without it. The goblins at the zeppelin tower junked a pump last spring; there\'ll be copper in that.$B$BThe old casks out back are rotten, but some staves will still be sound. Pick me six. Oliver Dwor at the smithy will have hoops if you ask him like you mean it.$B$BThen we\'ll see if my hands remember.', '', 'Return to Bram Lusk at the old brewhouse in Brill.', 971620, 1, 'Copper tubing salvaged', 971621, 6, 'Sound oak staves', 971622, 1, 'Iron hoops from Oliver Dwor', 971623, 5, 'Vats repaired and casks assembled', 858, 2, 0, 0, 0, 0, 0, 0),
(971602, 2, -1, 10, 159, 0, 4, 2500, 0, 'Taste of the Living', 'Gather 4 bitterroot on the hillside west of Brill, a fungal culture from Hamlin Atkins and brewing grain from William Saldean by the smithy; set Calla Fenn\'s 3 experimental batches going in the brewhouse yard, have Hamlin Atkins, Deathguard Dillinger and Executor Zygand taste them, and choose which recipe Oren should refine. Then return to Calla.', 'Calla Fenn. Apprentice. Allegedly.$B$BHere\'s the problem. Oren wants to brew his father\'s ale exactly as it was. He tasted his first batch yesterday, and do you know what it tasted of, to him? Nothing. Wet nothing. He threw the mug at the wall. It\'s still there; the mug, I mean. It went into the plaster.$B$BWe don\'t taste like the living, so we shouldn\'t brew like them. Bitter herbs carry. Some cultures turn grain into something you can feel at the back of your skull. I\'ve ideas. I need ingredients.$B$BBitterroot from the hillside west of town. A culture from Hamlin Atkins\'s beds; he\'ll give you the good one if you praise his blue caps. Grain from William Saldean. Then help me set three batches going, and find three brave volunteers.', '', 'Return to Calla Fenn at the old brewhouse in Brill.', 971624, 6, 'Ingredients gathered', 971625, 3, 'Experimental batches set going', 971626, 3, 'Townspeople who tasted the batches', 971627, 1, 'A recipe chosen for Oren', 2593, 3, 0, 0, 0, 0, 0, 0),
(971603, 2, -1, 10, 159, 0, 4, 2500, 0, 'A Bitter Batch', 'Examine the 3 spoiled barrels behind the brewhouse, question Bram Lusk and Calla Fenn, go down through the cellar hatch and cut out the 3 growths in the brewhouse\'s back wall, and repair the cellar\'s vent. Then report to Brewmaster Oren Blackbarrel.', 'Spoiled. All of it. Forty gallons of the best thing this brewhouse has made since my father died, gone to slime overnight. Green slime. With hairs.$B$BSomebody did this, $n. Somebody doesn\'t want a brewery in Brill: the Gallows\' End, maybe, or some apothecary who fancies my cellar for his jars, or someone closer than that. Calla\'s been in and out of the cellar with her cultures all week. I\'m not saying it\'s her. I\'m saying her cultures are green.$B$BLook at the barrels. Ask Bram and Calla what they know, and watch their faces while they answer. Then go down into the cellar, because whatever started this started there. And fix that vent while you\'re down; the air\'s so foul the rats have moved out.', '', 'Return to Brewmaster Oren Blackbarrel at the old brewhouse in Brill.', 971628, 3, 'Spoiled barrels examined', 971629, 2, 'Bram and Calla questioned', 971630, 4, 'Cellar searched and growths cut out', 971631, 1, 'Cellar vent repaired', 929, 2, 0, 0, 0, 0, 0, 0),
(971604, 2, -1, 10, 159, 0, 5, 4000, 0, 'To Absent Friends', 'Invite Innkeeper Renee of the Gallows\' End and Marta Greaves of the Wayfarer\'s Rest to the opening, tap the 3 sample barrels at Brill\'s market, help Calla set up the tasting room in the brewhouse yard, and name the brewery\'s signature drink with Brewmaster Oren Blackbarrel.', 'It\'s ready. I\'ve said that four times this week and taken it back three, so listen quickly.$B$BNot a grand opening. I hate grand. A few barrels, a few people, the doors open. Take an invitation to Renee at the Gallows\' End; she\'ll pretend she isn\'t worried about the competition. And one to Marta Greaves, who keeps the Wayfarer\'s Rest behind us and will try to haggle over the price of a free drink.$B$BBram\'s rolled three sample barrels down to the market. Tap them, so folk get a taste and an argument before tonight. Calla needs a hand with the tasting room.$B$BAnd the drink needs a name. I\'ve had forty. I hate all of them. You choose; then it\'s your fault.', '', 'Return to Brewmaster Oren Blackbarrel at the old brewhouse in Brill.', 971632, 2, 'Invitations delivered', 971633, 3, 'Sample barrels tapped at the market', 971634, 1, 'Tasting room set up', 971635, 1, 'Signature drink named', 2596, 5, 0, 0, 0, 0, 0, 0),
(971605, 2, -1, 10, 159, 32768, 2, 2500, 0, 'Brewer\'s Special', 'Cut 3 bitterroot on the hillside west of Brill, then pour this week\'s experimental brew for Innkeeper Renee, Deathguard Burgess and Hamlin Atkins and bring their verdicts to Brewmaster Oren Blackbarrel.', 'Calla\'s been at it again. Every week a new experiment: fermented in a skull, aged in a coffin, flavored with something she won\'t name in front of the Deathguard. Some weeks it\'s dreadful. Some weeks it\'s dreadful in an interesting way.$B$BThis week\'s wants bitterroot from the hillside west of town, fresh cut. Then take a jug round to our usual victims: Renee at the Gallows\' End, Deathguard Burgess in the square, and Hamlin Atkins, who will drink anything that ever touched a mushroom. Write down what they say. Calla says the notes are science. I say they\'re evidence.', '', 'Return to Brewmaster Oren Blackbarrel at the Old Brewery in Brill.', 971636, 3, 'Fresh bitterroot cut', 971637, 1, 'Innkeeper Renee\'s verdict', 971638, 1, 'Deathguard Burgess\'s verdict', 971639, 1, 'Hamlin Atkins\'s verdict', 0, 0, 0, 0, 0, 0, 0, 0),
(971606, 2, 1, 1, -1, 0, 0, 0, 0, '[house_set]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971607, 2, 1, 1, -1, 0, 0, 0, 0, '[got_culture]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971608, 2, 1, 1, -1, 0, 0, 0, 0, '[got_grain]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971609, 2, 1, 1, -1, 0, 0, 0, 0, '[tasted_hamlin]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971610, 2, 1, 1, -1, 0, 0, 0, 0, '[tasted_dillinger]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971611, 2, 1, 1, -1, 0, 0, 0, 0, '[tasted_zygand]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971612, 2, 1, 1, -1, 0, 0, 0, 0, '[recipe_dark]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971613, 2, 1, 1, -1, 0, 0, 0, 0, '[recipe_family]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971614, 2, 1, 1, -1, 0, 0, 0, 0, '[recipe_herbal]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971615, 2, 1, 1, -1, 0, 0, 0, 0, '[asked_bram]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971616, 2, 1, 1, -1, 0, 0, 0, 0, '[asked_calla]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971617, 2, 1, 1, -1, 0, 0, 0, 0, '[asked_renee]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971618, 2, 1, 1, -1, 0, 0, 0, 0, '[asked_marta]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971619, 2, 1, 1, -1, 0, 0, 0, 0, '[stout]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971620, 2, 1, 1, -1, 0, 0, 0, 0, '[reserve]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0),
(971621, 2, 1, 1, -1, 0, 0, 0, 0, '[bitter]', '', '', '', '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, '', 0, 0, 0, 0, 0, 0, 0, 0);
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`, `SpecialFlags`) VALUES (971600, 0, 0), (971601, 971600, 0), (971602, 971601, 0), (971603, 971602, 0), (971604, 971603, 0), (971605, 971604, 1);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`) VALUES
(971600, 1, '(Oren turns the pages with great care, as if they might crumble. Some do.)$B$BMash temperatures. Hop weights. The year the frost got into the barley... And here. My father\'s hand. "Blackbarrel Brown, for the harvest. Two measures of crystal malt, and don\'t let the boy near the hops."$B$B(For a long moment he says nothing at all.)$B$BHe brewed this every autumn. I\'d forgotten. I\'d forgotten I\'d forgotten.$B$B...Well. Don\'t stand there. There\'s a brewery to mend.'),
(971601, 1, '(Bram drives the last hoop home and rolls the cask across the yard. It runs true, straight and quiet, and comes to rest against the wall with a sound like a door closing.)$B$BHear that? That\'s a cask that\'ll hold. First one in eleven years.$B$B(He looks at his hands for a while.)$B$BThey remembered.'),
(971602, 1, '(Calla reads her notes aloud, with feeling.)$B$B"Excellent." "Mud." "The first thing I\'ve tasted in years, and I can\'t decide if that\'s a compliment." Three batches, three verdicts, no two alike. Science.$B$BOren pretended not to listen to any of it, which means he heard every word. He\'s out back now with your choice, muttering at it. That\'s how he shows love.$B$BWe\'re going to need somewhere for people to sit while they disagree.'),
(971603, 1, '(Oren holds a lump of the wall-rot up to the light and stares at it for a long time.)$B$BIn the walls. Since before the plague. Breathing out through that choked vent into every cask I filled. Nobody did it. It was just... here. Waiting, like everything in Brill.$B$B(He sets it down.)$B$BI\'ll have to say it to her, won\'t I. Calla! ...I said you\'d ruined the batch. I was wrong. You can stop smirking. No, you can\'t, I can see that from here. Fine.$B$BThe cellar\'s sound, $n. The brewery\'s sound. We open as soon as I can bear to.'),
(971604, 1, '(The brewhouse is full: Renee and Marta arguing at the counter, Bram explaining staves to a Deathguard who didn\'t ask, Calla pouring, Hamlin Atkins weeping a little into his mug. Oren climbs onto a cask and raises his own.)$B$BTo the people I worked beside, when we were alive. To old Tess, and the Brennan boys, and my father, who never once let me near the hops. They\'d hate this beer.$B$B(He drinks.)$B$BI can\'t remember the last time I tasted a good ale. Fortunately, I can remember how to make one.'),
(971605, 1, '(Oren reads the verdicts and grunts.)$B$B"Interesting." "Interesting." "I can see sounds." Calla will call that a triumph. I\'ll call it a week. She\'s already planning the next one; I saw her eyeing a coffin at the undertaker\'s.$B$BHere\'s your fee. Come back next week and we\'ll do it all again with something worse.');
INSERT INTO `quest_request_items` (`ID`, `EmoteOnComplete`, `EmoteOnIncomplete`, `CompletionText`) VALUES
(971600, 1, 1, 'The ledger, $n. Green leather, brass corners. Try not to read it. It\'s private. It\'s mostly about barley, but it\'s private.'),
(971601, 1, 1, 'Copper, staves, hoops. A barrel\'s only three things. That\'s why it\'s hard.'),
(971602, 1, 1, 'Bitterroot, culture, grain, three batches, three victims. I mean tasters.'),
(971603, 1, 1, 'Well? Who was it? Don\'t spare my feelings. I keep them in a jar.'),
(971604, 1, 1, 'Invitations, barrels, tables, a name. A brewery is mostly a list.'),
(971605, 1, 1, 'Bitterroot first, then the jug. Don\'t drink from it. Calla\'s counting.');
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES (971600, 971600), (971602, 971601), (971603, 971602), (971600, 971603), (971600, 971604), (971601, 971605);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES (971600, 971600), (971602, 971601), (971603, 971602), (971600, 971603), (971600, 971604), (971601, 971605);

-- Trainers: the training and the trainer flags of a creature of the game's own.
INSERT INTO `creature_default_trainer` (`CreatureId`, `TrainerId`) SELECT 971107, `TrainerId` FROM `creature_default_trainer` WHERE `CreatureId` = 2129;
UPDATE `creature_template` SET `npcflag` = `npcflag` | ((SELECT `npcflag` FROM (SELECT `npcflag` FROM `creature_template` WHERE `entry` = 2129) AS t) & 112) WHERE `entry` = 971107;
INSERT INTO `creature_default_trainer` (`CreatureId`, `TrainerId`) SELECT 971302, `TrainerId` FROM `creature_default_trainer` WHERE `CreatureId` = 2114;
UPDATE `creature_template` SET `npcflag` = `npcflag` | ((SELECT `npcflag` FROM (SELECT `npcflag` FROM `creature_template` WHERE `entry` = 2114) AS t) & 112) WHERE `entry` = 971302;
INSERT INTO `creature_default_trainer` (`CreatureId`, `TrainerId`) SELECT 971409, `TrainerId` FROM `creature_default_trainer` WHERE `CreatureId` = 5759;
UPDATE `creature_template` SET `npcflag` = `npcflag` | ((SELECT `npcflag` FROM (SELECT `npcflag` FROM `creature_template` WHERE `entry` = 5759) AS t) & 112) WHERE `entry` = 971409;
-- The projects' spawns that show from a stage.
INSERT INTO `brill_town_invis` (`kind`, `guid`, `type`, `value`) VALUES
('c', 971000, 1, 1),
('c', 971001, 1, 1),
('c', 971002, 1, 1),
('g', 971001, 1, 1),
('c', 971100, 2, 1),
('c', 971101, 2, 2),
('c', 971102, 2, 3),
('c', 971103, 2, 4),
('c', 971104, 2, 3),
('c', 971105, 2, 2),
('c', 971106, 2, 2),
('c', 971107, 2, 3),
('c', 971108, 2, 6),
('c', 971109, 2, 6),
('c', 971110, 2, 6),
('c', 971111, 2, 6),
('c', 971112, 2, 6),
('c', 971113, 2, 6),
('c', 971114, 7, 6),
('c', 971114, 2, 6),
('g', 971100, 2, 1),
('g', 971101, 2, 1),
('g', 971102, 2, 1),
('g', 971103, 2, 1),
('g', 971104, 2, 1),
('g', 971105, 2, 1),
('g', 971106, 2, 1),
('g', 971107, 2, 1),
('g', 971108, 2, 1),
('g', 971109, 2, 1),
('g', 971110, 2, 1),
('g', 971111, 2, 2),
('g', 971112, 2, 2),
('g', 971113, 2, 3),
('g', 971114, 2, 4),
('g', 971115, 2, 4),
('g', 971116, 2, 4),
('g', 971117, 2, 4),
('g', 971118, 2, 4),
('g', 971119, 2, 4),
('g', 971120, 2, 4),
('g', 971121, 2, 4),
('g', 971122, 2, 5),
('g', 971123, 2, 5),
('g', 971141, 2, 3),
('g', 971142, 2, 4),
('g', 971143, 2, 4),
('g', 971144, 2, 4),
('g', 971145, 2, 4),
('g', 971153, 2, 6),
('g', 971154, 2, 6),
('g', 971155, 2, 6),
('g', 971156, 2, 6),
('g', 971157, 2, 6),
('g', 971158, 2, 6),
('g', 971159, 2, 6),
('g', 971160, 2, 6),
('g', 971161, 2, 6),
('g', 971162, 2, 6),
('g', 971163, 2, 6),
('g', 971164, 2, 6),
('g', 971165, 2, 6),
('g', 971166, 2, 6),
('g', 971167, 2, 6),
('g', 971168, 2, 6),
('g', 971169, 2, 6),
('g', 971170, 2, 6),
('g', 971171, 2, 6),
('g', 971172, 2, 6),
('g', 971173, 2, 6),
('g', 971174, 2, 6),
('g', 971175, 2, 6),
('g', 971176, 2, 6),
('g', 971177, 2, 7),
('g', 971178, 2, 7),
('g', 971179, 2, 7),
('g', 971180, 2, 7),
('c', 971200, 4, 1),
('c', 971201, 4, 2),
('c', 971202, 4, 3),
('c', 971203, 4, 4),
('c', 971204, 4, 4),
('c', 971205, 4, 2),
('c', 971206, 4, 2),
('c', 971207, 4, 2),
('c', 971213, 4, 6),
('c', 971214, 4, 6),
('c', 971215, 4, 6),
('c', 971216, 4, 6),
('c', 971217, 4, 6),
('c', 971218, 4, 6),
('c', 971219, 2, 6),
('c', 971219, 4, 6),
('c', 971220, 8, 6),
('c', 971220, 4, 6),
('g', 971200, 4, 1),
('g', 971201, 4, 1),
('g', 971202, 4, 1),
('g', 971203, 4, 1),
('g', 971204, 4, 2),
('g', 971205, 4, 2),
('g', 971206, 4, 2),
('g', 971207, 4, 2),
('g', 971208, 4, 2),
('g', 971209, 4, 2),
('g', 971210, 4, 2),
('g', 971211, 4, 2),
('g', 971212, 4, 3),
('g', 971213, 4, 3),
('g', 971214, 4, 3),
('g', 971215, 4, 3),
('g', 971216, 4, 4),
('g', 971217, 4, 4),
('g', 971218, 4, 4),
('g', 971219, 4, 5),
('g', 971220, 4, 5),
('g', 971221, 4, 5),
('g', 971222, 4, 5),
('g', 971223, 4, 5),
('g', 971224, 4, 5),
('g', 971225, 4, 5),
('g', 971226, 4, 5),
('g', 971249, 4, 6),
('g', 971250, 4, 6),
('g', 971251, 4, 6),
('g', 971252, 4, 6),
('g', 971253, 4, 6),
('g', 971254, 4, 6),
('g', 971255, 4, 6),
('g', 971256, 4, 6),
('g', 971257, 4, 6),
('g', 971258, 4, 6),
('g', 971259, 4, 6),
('g', 971260, 4, 6),
('g', 971261, 4, 6),
('g', 971262, 4, 6),
('g', 971263, 4, 6),
('g', 971264, 4, 6),
('g', 971265, 4, 6),
('g', 971266, 4, 6),
('g', 971267, 4, 6),
('g', 971268, 4, 6),
('g', 971269, 4, 6),
('g', 971270, 4, 6),
('g', 971271, 4, 6),
('g', 971272, 4, 6),
('g', 971273, 4, 7),
('g', 971274, 4, 7),
('c', 971300, 5, 1),
('c', 971301, 5, 1),
('c', 971302, 5, 6),
('c', 971303, 5, 2),
('c', 971304, 5, 6),
('c', 971305, 5, 6),
('c', 971306, 5, 1),
('c', 971307, 5, 6),
('c', 971308, 5, 6),
('c', 971309, 5, 2),
('c', 971310, 5, 2),
('c', 971311, 5, 2),
('c', 971312, 5, 6),
('c', 971313, 5, 6),
('c', 971314, 5, 6),
('g', 971300, 5, 1),
('g', 971301, 5, 1),
('g', 971302, 5, 1),
('g', 971303, 5, 1),
('g', 971304, 5, 1),
('g', 971305, 5, 1),
('g', 971306, 5, 1),
('g', 971307, 5, 1),
('g', 971308, 5, 1),
('g', 971309, 5, 1),
('g', 971310, 5, 1),
('g', 971311, 5, 1),
('g', 971312, 5, 1),
('g', 971313, 5, 2),
('g', 971314, 5, 2),
('g', 971315, 5, 2),
('g', 971316, 5, 2),
('g', 971317, 5, 2),
('g', 971318, 5, 2),
('g', 971319, 5, 2),
('g', 971320, 5, 2),
('g', 971321, 5, 2),
('g', 971322, 5, 2),
('g', 971323, 5, 2),
('g', 971324, 5, 2),
('g', 971325, 5, 2),
('g', 971326, 5, 3),
('g', 971327, 5, 3),
('g', 971328, 5, 3),
('g', 971329, 5, 3),
('g', 971330, 5, 3),
('g', 971331, 5, 3),
('g', 971332, 5, 3),
('g', 971333, 5, 3),
('g', 971334, 5, 3),
('g', 971335, 5, 3),
('g', 971336, 5, 3),
('g', 971337, 5, 4),
('g', 971338, 5, 4),
('g', 971339, 5, 4),
('g', 971340, 5, 4),
('g', 971341, 5, 4),
('g', 971342, 5, 4),
('g', 971343, 5, 4),
('g', 971344, 5, 4),
('g', 971345, 5, 5),
('g', 971346, 5, 5),
('g', 971347, 5, 5),
('g', 971348, 5, 5),
('g', 971349, 5, 5),
('g', 971350, 5, 5),
('g', 971351, 5, 5),
('g', 971352, 5, 5),
('g', 971353, 5, 5),
('g', 971354, 5, 5),
('g', 971355, 5, 6),
('g', 971356, 5, 2),
('g', 971357, 5, 2),
('g', 971358, 5, 2),
('g', 971359, 5, 2),
('g', 971360, 5, 2),
('g', 971361, 5, 2),
('g', 971362, 5, 2),
('g', 971371, 5, 6),
('g', 971372, 2, 6),
('g', 971372, 5, 6),
('g', 971373, 2, 6),
('g', 971373, 5, 6),
('g', 971374, 5, 7),
('c', 971400, 7, 1),
('c', 971401, 7, 1),
('c', 971402, 7, 2),
('c', 971403, 7, 1),
('c', 971404, 7, 1),
('c', 971405, 7, 1),
('c', 971406, 7, 5),
('c', 971407, 7, 6),
('c', 971408, 7, 6),
('c', 971409, 7, 6),
('c', 971410, 7, 6),
('c', 971411, 8, 6),
('c', 971411, 7, 6),
('c', 971412, 7, 6),
('c', 971413, 7, 6),
('c', 971414, 7, 5),
('c', 971415, 7, 2),
('c', 971416, 7, 2),
('c', 971417, 7, 2),
('c', 971418, 7, 6),
('g', 971400, 7, 1),
('g', 971401, 7, 6),
('g', 971402, 7, 1),
('g', 971403, 7, 1),
('g', 971405, 7, 2),
('g', 971406, 7, 2),
('g', 971407, 7, 2),
('g', 971410, 7, 3),
('g', 971411, 7, 3),
('g', 971412, 7, 3),
('g', 971413, 7, 3),
('g', 971414, 7, 3),
('g', 971415, 7, 3),
('g', 971416, 7, 3),
('g', 971417, 7, 3),
('g', 971422, 7, 4),
('g', 971423, 7, 4),
('g', 971424, 7, 4),
('g', 971425, 7, 5),
('g', 971426, 7, 6),
('g', 971427, 7, 6),
('g', 971428, 7, 6),
('g', 971429, 7, 6),
('g', 971430, 7, 6),
('g', 971431, 7, 6),
('g', 971432, 7, 6),
('g', 971433, 7, 6),
('g', 971434, 7, 6),
('g', 971435, 7, 6),
('g', 971436, 7, 6),
('g', 971437, 7, 7),
('g', 971438, 7, 7),
('g', 971439, 7, 7),
('c', 971500, 8, 1),
('c', 971501, 8, 6),
('c', 971502, 8, 2),
('c', 971503, 8, 1),
('c', 971504, 8, 5),
('c', 971505, 8, 4),
('c', 971506, 8, 1),
('c', 971507, 8, 1),
('c', 971508, 8, 1),
('c', 971510, 8, 4),
('c', 971521, 8, 6),
('c', 971522, 8, 6),
('c', 971523, 8, 6),
('c', 971524, 8, 6),
('c', 971525, 8, 6),
('c', 971526, 8, 6),
('c', 971527, 8, 6),
('c', 971528, 8, 6),
('c', 971529, 8, 6),
('c', 971530, 8, 6),
('c', 971531, 8, 6),
('c', 971532, 8, 6),
('c', 971533, 8, 6),
('c', 971534, 8, 6),
('c', 971535, 8, 6),
('c', 971536, 8, 6),
('c', 971537, 8, 2),
('c', 971538, 8, 2),
('c', 971539, 8, 2),
('g', 971500, 8, 3),
('g', 971501, 8, 4),
('g', 971502, 8, 6),
('g', 971503, 8, 1),
('g', 971504, 8, 1),
('g', 971505, 8, 1),
('g', 971506, 8, 1),
('g', 971507, 8, 1),
('g', 971508, 8, 1),
('g', 971509, 8, 1),
('g', 971510, 8, 1),
('g', 971511, 8, 2),
('g', 971512, 8, 2),
('g', 971513, 8, 2),
('g', 971514, 8, 2),
('g', 971515, 8, 2),
('g', 971516, 8, 2),
('g', 971517, 8, 2),
('g', 971524, 8, 3),
('g', 971525, 8, 3),
('g', 971526, 8, 3),
('g', 971527, 8, 3),
('g', 971528, 8, 3),
('g', 971536, 8, 4),
('g', 971537, 8, 4),
('g', 971538, 8, 4),
('g', 971539, 8, 4),
('g', 971540, 8, 4),
('g', 971541, 8, 4),
('g', 971542, 8, 5),
('g', 971543, 8, 5),
('g', 971544, 8, 5),
('g', 971545, 8, 5),
('g', 971546, 8, 6),
('g', 971547, 8, 6),
('g', 971548, 8, 6),
('g', 971549, 8, 6),
('g', 971550, 8, 6),
('g', 971551, 8, 6),
('g', 971552, 8, 1),
('g', 971553, 8, 1),
('g', 971554, 8, 7),
('g', 971555, 8, 7),
('c', 971600, 9, 1),
('c', 971601, 9, 6),
('c', 971602, 9, 2),
('c', 971603, 9, 3),
('c', 971604, 9, 1),
('c', 971605, 9, 1),
('c', 971606, 9, 1),
('c', 971607, 9, 1),
('c', 971608, 9, 1),
('c', 971609, 9, 1),
('c', 971610, 9, 1),
('c', 971611, 9, 6),
('c', 971612, 9, 6),
('c', 971613, 9, 6),
('c', 971614, 9, 6),
('c', 971615, 9, 6),
('c', 971616, 9, 6),
('c', 971617, 9, 6),
('c', 971618, 9, 6),
('c', 971619, 9, 6),
('c', 971620, 9, 6),
('c', 971621, 8, 6),
('c', 971621, 9, 6),
('c', 971622, 9, 2),
('c', 971623, 9, 2),
('c', 971624, 9, 2),
('g', 971601, 9, 6),
('g', 971602, 9, 1),
('g', 971603, 9, 1),
('g', 971604, 9, 1),
('g', 971605, 9, 1),
('g', 971606, 9, 1),
('g', 971607, 9, 1),
('g', 971608, 9, 1),
('g', 971609, 9, 1),
('g', 971610, 9, 1),
('g', 971611, 9, 2),
('g', 971612, 9, 2),
('g', 971613, 9, 2),
('g', 971614, 9, 2),
('g', 971615, 9, 2),
('g', 971616, 9, 2),
('g', 971617, 9, 2),
('g', 971618, 9, 2),
('g', 971619, 9, 2),
('g', 971620, 9, 2),
('g', 971621, 9, 2),
('g', 971622, 9, 2),
('g', 971623, 9, 2),
('g', 971625, 9, 3),
('g', 971626, 9, 3),
('g', 971627, 9, 3),
('g', 971628, 9, 3),
('g', 971629, 9, 3),
('g', 971630, 9, 3),
('g', 971635, 9, 3),
('g', 971636, 9, 3),
('g', 971637, 9, 3),
('g', 971638, 9, 4),
('g', 971639, 9, 4),
('g', 971640, 9, 4),
('g', 971641, 9, 4),
('g', 971642, 9, 4),
('g', 971643, 9, 4),
('g', 971644, 9, 4),
('g', 971645, 9, 5),
('g', 971646, 9, 5),
('g', 971647, 9, 5),
('g', 971648, 9, 5),
('g', 971649, 9, 5),
('g', 971650, 9, 6),
('g', 971651, 9, 6),
('g', 971652, 9, 6),
('g', 971653, 9, 6),
('g', 971654, 9, 6),
('g', 971655, 9, 6),
('g', 971656, 9, 6),
('g', 971657, 9, 6),
('g', 971658, 9, 6),
('g', 971659, 9, 6),
('g', 971660, 9, 6),
('g', 971661, 9, 7),
('g', 971662, 9, 7);
INSERT INTO `game_event_creature` (`eventEntry`, `guid`) VALUES (231, 971001), (231, 971002), (231, 971105), (231, 971106), (231, 971107), (232, 971111), (232, 971112), (232, 971113), (232, 971114), (231, 971203), (231, 971204), (231, 971205), (231, 971206), (231, 971207), (231, 971217), (231, 971218), (232, 971219), (231, 971220), (231, 971304), (232, 971305), (231, 971307), (233, 971308), (231, 971309), (231, 971310), (231, 971311), (232, 971312), (232, 971313), (230, 971314), (231, 971407), (232, 971408), (231, 971411), (231, 971412), (233, 971413), (230, 971414), (231, 971415), (231, 971416), (231, 971417), (232, 971418), (230, 971521), (231, 971522), (232, 971523), (233, 971524), (231, 971525), (232, 971526), (231, 971527), (232, 971528), (231, 971529), (231, 971530), (230, 971531), (230, 971532), (233, 971533), (232, 971534), (233, 971535), (231, 971537), (231, 971538), (231, 971539), (230, 971611), (231, 971612), (232, 971613), (231, 971614), (232, 971615), (233, 971616), (232, 971617), (232, 971618), (232, 971619), (232, 971620), (231, 971621), (231, 971622), (231, 971623), (231, 971624);
INSERT INTO `game_event_gameobject` (`eventEntry`, `guid`) VALUES (232, 971436), (231, 971546), (231, 971547), (231, 971630);
INSERT INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`, `ConditionTypeOrReference`, `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`, `NegativeCondition`, `Comment`) VALUES
(30, 1, 970305, 0, 0, 9, 0, 970301, 0, 0, 0, 'mod-brill-home town: opened_spade while its quest is in the log'),
(30, 1, 970306, 0, 0, 9, 0, 970301, 0, 0, 0, 'mod-brill-home town: opened_lid while its quest is in the log'),
(30, 1, 970307, 0, 0, 9, 0, 970301, 0, 0, 0, 'mod-brill-home town: opened_shroud while its quest is in the log'),
(30, 1, 970308, 0, 0, 9, 0, 970302, 0, 0, 0, 'mod-brill-home town: trail while its quest is in the log'),
(30, 1, 970310, 0, 0, 9, 0, 970303, 0, 0, 0, 'mod-brill-home town: toolroll while its quest is in the log'),
(30, 1, 970311, 0, 0, 9, 0, 970303, 0, 0, 0, 'mod-brill-home town: basket while its quest is in the log'),
(30, 1, 970312, 0, 0, 9, 0, 970303, 0, 0, 0, 'mod-brill-home town: letters while its quest is in the log'),
(30, 1, 970403, 0, 0, 9, 0, 970401, 0, 0, 0, 'mod-brill-home town: crate while its quest is in the log'),
(30, 1, 970404, 0, 0, 9, 0, 970401, 0, 0, 0, 'mod-brill-home town: cart while its quest is in the log'),
(30, 1, 970500, 0, 0, 9, 0, 970500, 0, 0, 0, 'mod-brill-home town: embers while its quest is in the log'),
(30, 1, 970501, 0, 0, 9, 0, 970501, 0, 0, 0, 'mod-brill-home town: wellstone while its quest is in the log'),
(30, 1, 970502, 0, 0, 9, 0, 970501, 0, 0, 0, 'mod-brill-home town: chalkcrate while its quest is in the log'),
(30, 1, 970503, 0, 0, 9, 0, 970502, 0, 0, 0, 'mod-brill-home town: lamp while its quest is in the log'),
(30, 1, 970606, 0, 0, 9, 0, 970601, 0, 0, 0, 'mod-brill-home town: parcel while its quest is in the log'),
(30, 1, 970607, 0, 0, 9, 0, 970602, 0, 0, 0, 'mod-brill-home town: notice while its quest is in the log'),
(30, 1, 970608, 0, 0, 9, 0, 970602, 0, 0, 0, 'mod-brill-home town: bible while its quest is in the log'),
(30, 1, 970700, 0, 0, 9, 0, 970701, 0, 0, 0, 'mod-brill-home town: cart while its quest is in the log'),
(30, 1, 970701, 0, 0, 9, 0, 970702, 0, 0, 0, 'mod-brill-home town: tracks while its quest is in the log'),
(30, 1, 970702, 0, 0, 9, 0, 970703, 0, 0, 0, 'mod-brill-home town: firewood while its quest is in the log'),
(30, 1, 970801, 0, 0, 9, 0, 970800, 0, 0, 0, 'mod-brill-home town: bucket while its quest is in the log'),
(30, 1, 970802, 0, 0, 9, 0, 970802, 0, 0, 0, 'mod-brill-home town: bloom while its quest is in the log'),
(30, 1, 970803, 0, 0, 9, 0, 970802, 0, 0, 0, 'mod-brill-home town: culvert while its quest is in the log'),
(30, 1, 970804, 0, 0, 9, 0, 970803, 0, 0, 0, 'mod-brill-home town: sac while its quest is in the log'),
(30, 1, 970805, 0, 0, 9, 0, 970804, 0, 0, 0, 'mod-brill-home town: cask while its quest is in the log'),
(30, 1, 970900, 0, 0, 9, 0, 970900, 0, 0, 0, 'mod-brill-home town: mark_cellar while its quest is in the log'),
(30, 1, 970901, 0, 0, 9, 0, 970900, 0, 0, 0, 'mod-brill-home town: mark_stone while its quest is in the log'),
(30, 1, 970902, 0, 0, 9, 0, 970900, 0, 0, 0, 'mod-brill-home town: mark_sunken while its quest is in the log'),
(30, 1, 970903, 0, 0, 9, 0, 970901, 0, 0, 0, 'mod-brill-home town: journal_lyle while its quest is in the log'),
(30, 1, 970904, 0, 0, 9, 0, 970901, 0, 0, 0, 'mod-brill-home town: journal_pike while its quest is in the log'),
(30, 1, 970905, 0, 0, 9, 0, 970901, 0, 0, 0, 'mod-brill-home town: journal_boy while its quest is in the log'),
(30, 1, 970906, 0, 0, 9, 0, 970903, 0, 0, 0, 'mod-brill-home town: ward while its quest is in the log'),
(30, 1, 970907, 0, 0, 9, 0, 970903, 0, 0, 0, 'mod-brill-home town: croft_letters while its quest is in the log'),
(30, 1, 970908, 0, 0, 9, 0, 970904, 0, 0, 0, 'mod-brill-home town: roll while its quest is in the log'),
(30, 1, 971000, 0, 0, 9, 0, 971000, 0, 0, 0, 'mod-brill-home town: bell while its quest is in the log'),
(19, 0, 971000, 0, 0, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 0, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 0, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 1, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 1, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 1, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 2, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 2, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 2, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 3, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 3, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 3, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 4, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 4, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 4, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 5, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 5, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 5, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 6, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 6, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 6, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 7, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 7, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 7, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 8, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 8, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 8, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 9, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 9, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 9, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 10, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 10, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 10, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 11, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 11, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 11, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 12, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 12, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 12, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 13, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 13, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 13, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 14, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 14, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 14, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 15, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 15, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 15, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 16, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 16, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 16, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 17, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 17, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 17, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 18, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 18, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 18, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 19, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 19, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 19, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 20, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 20, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 20, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 21, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 21, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 21, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 22, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 22, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 22, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 23, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 23, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 23, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 24, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 24, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 24, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 25, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 25, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 25, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 26, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 26, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 26, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 27, 8, 0, 970205, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 27, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 27, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 28, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 28, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 28, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 29, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 29, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 29, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 30, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 30, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 30, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 31, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 31, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 31, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 32, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 32, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 32, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 33, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 33, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 33, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 34, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 34, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 34, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 35, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 35, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 35, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 36, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 36, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 36, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 37, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 37, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 37, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 38, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 38, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 38, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 39, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 39, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 39, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 40, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 40, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 40, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 41, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 41, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 41, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 42, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 42, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 42, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 43, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 43, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 43, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 44, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 44, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 44, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 45, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 45, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 45, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 46, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 46, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 46, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 47, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 47, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 47, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 48, 8, 0, 970128, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 48, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 48, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 49, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 49, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 49, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 50, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 50, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 50, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 51, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 51, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 51, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 52, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 52, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 52, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 53, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 53, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 53, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 54, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 54, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 54, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 55, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 55, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 55, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 56, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 56, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 56, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 57, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 57, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 57, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 58, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 58, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 58, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 59, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 59, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 59, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 60, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 60, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 60, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 61, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 61, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 61, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 62, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 62, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 62, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 63, 8, 0, 970304, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 63, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 63, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 64, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 64, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 64, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 65, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 65, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 65, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 66, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 66, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 66, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 67, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 67, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 67, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 68, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 68, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 68, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 69, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 69, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 69, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 70, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 70, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 70, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 71, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 71, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 71, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 72, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 72, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 72, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 73, 8, 0, 970404, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 73, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 73, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 74, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 74, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 74, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 75, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 75, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 75, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 76, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 76, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 76, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 77, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 77, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 77, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 78, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 78, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 78, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 79, 8, 0, 970504, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 79, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 79, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 80, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 80, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 80, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 81, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 81, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 81, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 82, 8, 0, 970604, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 82, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 82, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 83, 8, 0, 970704, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 83, 8, 0, 970804, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971000, 0, 83, 8, 0, 970904, 0, 0, 0, 'mod-brill-home town: endures'),
(19, 0, 971001, 0, 0, 8, 0, 971104, 0, 0, 0, 'mod-brill-home town: town'),
(19, 0, 971001, 0, 0, 8, 0, 971204, 0, 0, 0, 'mod-brill-home town: town'),
(19, 0, 971001, 0, 0, 8, 0, 971304, 0, 0, 0, 'mod-brill-home town: town'),
(19, 0, 971001, 0, 0, 8, 0, 971404, 0, 0, 0, 'mod-brill-home town: town'),
(19, 0, 971001, 0, 0, 8, 0, 971504, 0, 0, 0, 'mod-brill-home town: town'),
(19, 0, 971001, 0, 0, 8, 0, 971604, 0, 0, 0, 'mod-brill-home town: town'),
(30, 1, 971105, 0, 0, 9, 0, 971100, 0, 0, 0, 'mod-brill-home town: prayerbooks while its quest is in the log'),
(30, 1, 971114, 0, 0, 9, 0, 971101, 0, 0, 0, 'mod-brill-home town: stone_block while its quest is in the log'),
(30, 1, 971115, 0, 0, 9, 0, 971101, 0, 0, 0, 'mod-brill-home town: timber while its quest is in the log'),
(30, 1, 971116, 0, 0, 9, 0, 971102, 0, 0, 0, 'mod-brill-home town: page while its quest is in the log'),
(30, 1, 971118, 0, 0, 9, 0, 971103, 0, 0, 0, 'mod-brill-home town: sigil_respect while its quest is in the log'),
(30, 1, 971119, 0, 0, 9, 0, 971103, 0, 0, 0, 'mod-brill-home town: sigil_tenacity while its quest is in the log'),
(30, 1, 971120, 0, 0, 9, 0, 971103, 0, 0, 0, 'mod-brill-home town: sigil_power while its quest is in the log'),
(30, 1, 971122, 0, 0, 9, 0, 971103, 0, 0, 0, 'mod-brill-home town: relic while its quest is in the log'),
(30, 1, 971123, 0, 0, 9, 0, 971104, 0, 0, 0, 'mod-brill-home town: hidden_bell while its quest is in the log'),
(30, 1, 971124, 0, 0, 9, 0, 971104, 0, 0, 0, 'mod-brill-home town: clapper while its quest is in the log'),
(30, 1, 971125, 0, 0, 9, 0, 971105, 0, 0, 0, 'mod-brill-home town: record while its quest is in the log'),
(30, 1, 971203, 0, 0, 9, 0, 971200, 0, 0, 0, 'mod-brill-home town: office_chest while its quest is in the log'),
(30, 1, 971208, 0, 0, 9, 0, 971201, 0, 0, 0, 'mod-brill-home town: unbuilt while its quest is in the log'),
(30, 1, 971217, 0, 0, 9, 0, 971204, 0, 0, 0, 'mod-brill-home town: unsorted while its quest is in the log'),
(30, 1, 971218, 0, 0, 9, 0, 971200, 0, 0, 0, 'mod-brill-home town: garren_book while its quest is in the log'),
(30, 1, 971219, 0, 0, 9, 0, 971201, 0, 0, 0, 'mod-brill-home town: hardwood while its quest is in the log'),
(30, 1, 971220, 0, 0, 9, 0, 971202, 0, 0, 0, 'mod-brill-home town: mill_ledger while its quest is in the log'),
(30, 1, 971221, 0, 0, 9, 0, 971203, 0, 0, 0, 'mod-brill-home town: store while its quest is in the log'),
(30, 1, 971222, 0, 0, 9, 0, 971203, 0, 0, 0, 'mod-brill-home town: chronicle_page while its quest is in the log'),
(30, 1, 971223, 0, 0, 9, 0, 971205, 0, 0, 0, 'mod-brill-home town: lost_doc while its quest is in the log'),
(23, 971302, 2453, 0, 0, 8, 0, 971306, 0, 0, 0, 'mod-brill-home town: pellen_stall'),
(23, 971302, 2452, 0, 0, 8, 0, 971306, 0, 0, 0, 'mod-brill-home town: pellen_stall'),
(23, 971302, 2562, 0, 0, 8, 0, 971307, 0, 0, 0, 'mod-brill-home town: pellen_stall'),
(23, 971302, 3422, 0, 0, 8, 0, 971307, 0, 0, 0, 'mod-brill-home town: pellen_stall'),
(30, 1, 971302, 0, 0, 9, 0, 971300, 0, 0, 0, 'mod-brill-home town: markers while its quest is in the log'),
(30, 1, 971323, 0, 0, 9, 0, 971301, 0, 0, 0, 'mod-brill-home town: seedlings while its quest is in the log'),
(30, 1, 971324, 0, 0, 9, 0, 971301, 0, 0, 0, 'mod-brill-home town: spore while its quest is in the log'),
(30, 1, 971325, 0, 0, 9, 0, 971301, 0, 0, 0, 'mod-brill-home town: silt while its quest is in the log'),
(30, 1, 971326, 0, 0, 9, 0, 971302, 0, 0, 0, 'mod-brill-home town: pipes while its quest is in the log'),
(30, 1, 971327, 0, 0, 9, 0, 971302, 0, 0, 0, 'mod-brill-home town: outlet while its quest is in the log'),
(30, 1, 971328, 0, 0, 9, 0, 971303, 0, 0, 0, 'mod-brill-home town: frame while its quest is in the log'),
(30, 1, 971329, 0, 0, 9, 0, 971303, 0, 0, 0, 'mod-brill-home town: moonlily while its quest is in the log'),
(30, 1, 971330, 0, 0, 9, 0, 971304, 0, 0, 0, 'mod-brill-home town: graves while its quest is in the log'),
(23, 971409, 3531, 0, 0, 8, 0, 971406, 0, 0, 0, 'mod-brill-home town: fenwick_hall'),
(23, 971409, 2456, 0, 0, 8, 0, 971407, 0, 0, 0, 'mod-brill-home town: fenwick_hall'),
(30, 1, 971404, 0, 0, 9, 0, 971400, 0, 0, 0, 'mod-brill-home town: wagon while its quest is in the log'),
(30, 1, 971407, 0, 0, 9, 0, 971401, 0, 0, 0, 'mod-brill-home town: cabparts while its quest is in the log'),
(30, 1, 971414, 0, 0, 9, 0, 971402, 0, 0, 0, 'mod-brill-home town: mech while its quest is in the log'),
(30, 1, 971415, 0, 0, 9, 0, 971402, 0, 0, 0, 'mod-brill-home town: gearing while its quest is in the log'),
(30, 1, 971416, 0, 0, 9, 0, 971402, 0, 0, 0, 'mod-brill-home town: hand while its quest is in the log'),
(30, 1, 971418, 0, 0, 9, 0, 971403, 0, 0, 0, 'mod-brill-home town: proposal while its quest is in the log'),
(30, 1, 971419, 0, 0, 9, 0, 971403, 0, 0, 0, 'mod-brill-home town: records while its quest is in the log'),
(30, 1, 971507, 0, 0, 9, 0, 971500, 0, 0, 0, 'mod-brill-home town: ruts while its quest is in the log'),
(30, 1, 971508, 0, 0, 9, 0, 971500, 0, 0, 0, 'mod-brill-home town: broken_wagon while its quest is in the log'),
(30, 1, 971509, 0, 0, 9, 0, 971500, 0, 0, 0, 'mod-brill-home town: site_stakes while its quest is in the log'),
(30, 1, 971512, 0, 0, 9, 0, 971501, 0, 0, 0, 'mod-brill-home town: timber while its quest is in the log'),
(30, 1, 971513, 0, 0, 9, 0, 971501, 0, 0, 0, 'mod-brill-home town: platform_frame while its quest is in the log'),
(30, 1, 971514, 0, 0, 9, 0, 971501, 0, 0, 0, 'mod-brill-home town: stow_crates while its quest is in the log'),
(30, 1, 971515, 0, 0, 9, 0, 971501, 0, 0, 0, 'mod-brill-home town: dumped while its quest is in the log'),
(30, 1, 971519, 0, 0, 9, 0, 971502, 0, 0, 0, 'mod-brill-home town: q3_wagon while its quest is in the log'),
(30, 1, 971520, 0, 0, 9, 0, 971502, 0, 0, 0, 'mod-brill-home town: trail_records while its quest is in the log'),
(30, 1, 971532, 0, 0, 9, 0, 971504, 0, 0, 0, 'mod-brill-home town: marked_crates while its quest is in the log'),
(23, 971601, 2596, 0, 0, 8, 0, 971619, 0, 0, 0, 'mod-brill-home town: oren'),
(23, 971601, 2686, 0, 0, 8, 0, 971620, 0, 0, 0, 'mod-brill-home town: oren'),
(23, 971601, 18287, 0, 0, 8, 0, 971621, 0, 0, 0, 'mod-brill-home town: oren'),
(30, 1, 971603, 0, 0, 9, 0, 971600, 0, 0, 0, 'mod-brill-home town: spoiled while its quest is in the log'),
(30, 1, 971604, 0, 0, 9, 0, 971600, 0, 0, 0, 'mod-brill-home town: ledger while its quest is in the log'),
(30, 1, 971609, 0, 0, 9, 0, 971601, 0, 0, 0, 'mod-brill-home town: cask_frames while its quest is in the log'),
(30, 1, 971610, 0, 0, 9, 0, 971601, 0, 0, 0, 'mod-brill-home town: rotten_casks while its quest is in the log'),
(30, 1, 971611, 0, 0, 9, 0, 971601, 0, 0, 0, 'mod-brill-home town: pump while its quest is in the log'),
(30, 1, 971618, 0, 0, 9, 0, 971602, 0, 0, 0, 'mod-brill-home town: tub_dark while its quest is in the log'),
(30, 1, 971619, 0, 0, 9, 0, 971602, 0, 0, 0, 'mod-brill-home town: tub_family while its quest is in the log'),
(30, 1, 971620, 0, 0, 9, 0, 971602, 0, 0, 0, 'mod-brill-home town: tub_herbal while its quest is in the log'),
(30, 1, 971621, 0, 0, 9, 0, 971603, 0, 0, 0, 'mod-brill-home town: bad_barrels while its quest is in the log'),
(30, 1, 971622, 0, 0, 9, 0, 971603, 0, 0, 0, 'mod-brill-home town: growths while its quest is in the log'),
(30, 1, 971623, 0, 0, 9, 0, 971603, 0, 0, 0, 'mod-brill-home town: vent while its quest is in the log'),
(30, 1, 971625, 0, 0, 9, 0, 971604, 0, 0, 0, 'mod-brill-home town: samples while its quest is in the log');
-- The words.
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970200, '(Letters tied with twine, all to Cedric, all from Elinor. The early ones are about the harvest and the boys and a dog called Bramble. The last is short:$B$B\'They say the grain from Andorhal is bad. Owen is coughing. Come home quickly. I don\'t like how quiet the road is.\'$B$BShe never wrote again.)', '(Letters tied with twine, all to Cedric, all from Elinor. The early ones are about the harvest and the boys and a dog called Bramble. The last is short:$B$B\'They say the grain from Andorhal is bad. Owen is coughing. Come home quickly. I don\'t like how quiet the road is.\'$B$BShe never wrote again.)', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970201, 'Oswin Thatcher, carpenter. I\'ve been sent to fix a house for somebody who hasn\'t got it yet. Jamie Nore\'s idea of planning.', 'Oswin Thatcher, carpenter. I\'ve been sent to fix a house for somebody who hasn\'t got it yet. Jamie Nore\'s idea of planning.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970202, 'Two cups by the stove now, and somebody\'s alchemy things on the windowsill. Are some of these furnishings for her, then? I\'ll make the chair arms wider. She looks like the sort who sits and watches.', 'Two cups by the stove now, and somebody\'s alchemy things on the windowsill. Are some of these furnishings for her, then? I\'ll make the chair arms wider. She looks like the sort who sits and watches.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970203, 'The alchemist swept my sawdust out of the door this morning before I\'d finished making it. Tidy. Very tidy. She asked me which boards creak. I told her. I\'m still not sure I should have.', 'The alchemist swept my sawdust out of the door this morning before I\'d finished making it. Tidy. Very tidy. She asked me which boards creak. I told her. I\'m still not sure I should have.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (970204, 'Still standing. The roof, I mean. And me, more or less.', 'Still standing. The roof, I mean. And me, more or less.', 0.333, 'Jamie\'s got me fixing the town hall\'s shutters next. Then the inn\'s stairs. Brill was falling down for years and nobody noticed, because nobody here expects anything to stay up.', 'Jamie\'s got me fixing the town hall\'s shutters next. Then the inn\'s stairs. Brill was falling down for years and nobody noticed, because nobody here expects anything to stay up.', 0.333, 'If you want anything else built, $n, ask. I\'ve grown fond of your house. Don\'t tell it.', 'If you want anything else built, $n, ask. I\'ve grown fond of your house. Don\'t tell it.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970205, 'I mortared the gap twice. Some nights I\'d swear I hear it breathing through the brick. Probably the wind.', 'I mortared the gap twice. Some nights I\'d swear I hear it breathing through the brick. Probably the wind.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970206, 'Oswin Thatcher, carpenter. Mind the boards. Mind the roof. Mind everything, really; this house has been left to itself a long time.', 'Oswin Thatcher, carpenter. Mind the boards. Mind the roof. Mind everything, really; this house has been left to itself a long time.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970207, 'So the alchemist lives here now. She poured my cider back into the jug and gave me tea instead. I didn\'t argue. Nobody argues with Carolai.', 'So the alchemist lives here now. She poured my cider back into the jug and gave me tea instead. I didn\'t argue. Nobody argues with Carolai.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (970208, 'I brought cider. Can\'t taste it. Neither can half of us. We drink it anyway; it\'s the ceremony that counts.', 'I brought cider. Can\'t taste it. Neither can half of us. We drink it anyway; it\'s the ceremony that counts.', 0.333, 'My inn\'s never been this quiet, and your house has never been this loud. Seems fair.', 'My inn\'s never been this quiet, and your house has never been this loud. Seems fair.', 0.333, 'When I was alive I used to bake for every new house on the lane. I\'ve forgotten how. I remember the smell, though.', 'When I was alive I used to bake for every new house on the lane. I\'ve forgotten how. I remember the smell, though.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (970209, 'I\'ve brought you a tincture for the damp. Rub it on the walls, not yourself. Probably not yourself.', 'I\'ve brought you a tincture for the damp. Rub it on the walls, not yourself. Probably not yourself.', 0.333, 'A very reasonable house. Solid. Uncontaminated. I\'m almost disappointed.', 'A very reasonable house. Solid. Uncontaminated. I\'m almost disappointed.', 0.333, 'Your carpenter has opinions about rot. I have more. We\'ve been discussing it for an hour. It\'s been delightful.', 'Your carpenter has opinions about rot. I have more. We\'ve been discussing it for an hour. It\'s been delightful.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970210, 'That dog of yours keeps sniffing my mushrooms. Smart dog. He knows the good ones.', 'That dog of yours keeps sniffing my mushrooms. Smart dog. He knows the good ones.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (970211, 'Mushrooms! I brought mushrooms. A housewarming gift. Plant them in the cellar; they\'ll love it down there.', 'Mushrooms! I brought mushrooms. A housewarming gift. Plant them in the cellar; they\'ll love it down there.', 0.333, 'We\'re neighbors now. If you hear me singing to the crops at night, that\'s normal. It helps them grow.', 'We\'re neighbors now. If you hear me singing to the crops at night, that\'s normal. It helps them grow.', 0.333, 'Lovely house. Smells of fresh oak. Mine smells of mushrooms. Everything I own smells of mushrooms.', 'Lovely house. Smells of fresh oak. Mine smells of mushrooms. Everything I own smells of mushrooms.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (970212, 'I\'m not on duty. I\'m standing by the door because that\'s where I stand.', 'I\'m not on duty. I\'m standing by the door because that\'s where I stand.', 0.333, 'The Deathguard know which house this is now. Nothing comes up that road without us seeing it.', 'The Deathguard know which house this is now. Nothing comes up that road without us seeing it.', 0.333, 'It\'s good, this. People in a room together who aren\'t afraid of each other. Don\'t tell Zygand I said so.', 'It\'s good, this. People in a room together who aren\'t afraid of each other. Don\'t tell Zygand I said so.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970300, '(Letters tied with string, each beginning \'Dear Da\' in a careful round hand. The last is dated the week the plague came to Brill.)', '(Letters tied with string, each beginning \'Dear Da\' in a careful round hand. The last is dated the week the plague came to Brill.)', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970301, 'Thirty-one names, $n. Thirty-one people Croft kept in the dark and wrote down like stock. They\'re in my ledger now, in the right column. I ring the bell at dusk for one of them each night. It\'ll take a month. I find I don\'t mind the work.', 'Thirty-one names, $n. Thirty-one people Croft kept in the dark and wrote down like stock. They\'re in my ledger now, in the right column. I ring the bell at dusk for one of them each night. It\'ll take a month. I find I don\'t mind the work.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970302, 'Isolde\'s message said you\'d bring me something from under the hill. I\'ve cleared a page for it. I hope a page is enough.', 'Isolde\'s message said you\'d bring me something from under the hill. I\'ve cleared a page for it. I hope a page is enough.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970303, 'You\'ve been below. I can smell it on you: old candle-fat and older stone. Whatever\'s down there, $n, mind you come back up the same as you went. Some don\'t.', 'You\'ve been below. I can smell it on you: old candle-fat and older stone. Whatever\'s down there, $n, mind you come back up the same as you went. Some don\'t.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970304, 'Mercy walked through the market at noon yesterday and bought a loaf she can\'t eat, just to be seen paying for it. Half of Brill stared. The other half asked if she still delivers. She does, it seems: she\'s been at the Apothecary\'s door asking after foals and calves.$B$BThe ledger balances, $n. First time in years.', 'Mercy walked through the market at noon yesterday and bought a loaf she can\'t eat, just to be seen paying for it. Half of Brill stared. The other half asked if she still delivers. She does, it seems: she\'s been at the Apothecary\'s door asking after foals and calves.$B$BThe ledger balances, $n. First time in years.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970305, 'They came in by night, as we agreed, and the Deathguard had their orders. No torches. A week on, and the baker\'s boy still doesn\'t know Edith was ever under my lawn. That\'s how she wants it.$B$BThe ledger balances, $n. First time in years.', 'They came in by night, as we agreed, and the Deathguard had their orders. No torches. A week on, and the baker\'s boy still doesn\'t know Edith was ever under my lawn. That\'s how she wants it.$B$BThe ledger balances, $n. First time in years.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970306, 'A carpenter came by asking whether the parish books mention a mark like a crowned eye. They don\'t. But a Deathstalker asked me the very same thing a month ago, and she\'s been standing by the mausoleum ever since, pretending to admire it.', 'A carpenter came by asking whether the parish books mention a mark like a crowned eye. They don\'t. But a Deathstalker asked me the very same thing a month ago, and she\'s been standing by the mausoleum ever since, pretending to admire it.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970307, 'The bell\'s rope is new. I bought it myself. Have you been to the Magistrate?', 'The bell\'s rope is new. I bought it myself. Have you been to the Magistrate?', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970308, 'I\'ve kept the Deathguard away from the east hill. Told them it\'s adders. Don\'t make a liar of me.', 'I\'ve kept the Deathguard away from the east hill. Told them it\'s adders. Don\'t make a liar of me.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970309, 'North side, by the yew. Mind the soft ground; it isn\'t always empty.', 'North side, by the yew. Mind the soft ground; it isn\'t always empty.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970310, 'The ledgers are in a terrible state. I kept them dry for twenty years and then I died and nobody else did. Shall we?', 'The ledgers are in a terrible state. I kept them dry for twenty years and then I died and nobody else did. Shall we?', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (970311, 'Mind the newer stones. The ground hasn\'t settled. Neither, some days, have the residents.', 'Mind the newer stones. The ground hasn\'t settled. Neither, some days, have the residents.', 0.333, 'Every name in this ground was someone\'s. I keep them straight. It\'s the least I can do, and in this town the least is a great deal.', 'Every name in this ground was someone\'s. I keep them straight. It\'s the least I can do, and in this town the least is a great deal.', 0.333, 'You\'re welcome to walk here. Only don\'t stand on anyone. They notice, these days.', 'You\'re welcome to walk here. Only don\'t stand on anyone. They notice, these days.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970312, 'I come back up here some nights. It was the first place I was myself. Brill is louder than I remember.', 'I come back up here some nights. It was the first place I was myself. Brill is louder than I remember.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970313, 'Keep your voice low. Walter startles.', 'Keep your voice low. Walter startles.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970314, '(A grey-faced woman blocks the mausoleum door with a spade held like a pike.)$B$BThis is a tomb. There\'s nothing for you here. Go on.', '(A grey-faced woman blocks the mausoleum door with a spade held like a pike.)$B$BThis is a tomb. There\'s nothing for you here. Go on.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970315, 'Mercy\'s up here again, is she? I came to fix the hinge. Somebody should. It kept us.', 'Mercy\'s up here again, is she? I came to fix the hinge. Somebody should. It kept us.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970316, 'I cut half the stones down in that cemetery, you know. Mine too. Didn\'t expect to read it from the wrong side.', 'I cut half the stones down in that cemetery, you know. Mine too. Didn\'t expect to read it from the wrong side.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970317, 'It\'s quiet up here. I come to sew when the town gets to be too much.', 'It\'s quiet up here. I come to sew when the town gets to be too much.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970318, 'Please don\'t look at my face. I know what\'s left of it. I\'d... rather you looked at my hands. They still know how to work.', 'Please don\'t look at my face. I know what\'s left of it. I\'d... rather you looked at my hands. They still know how to work.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970319, 'Don\'t tell the others I come up here. I like the view. From up here Brill looks like it did.', 'Don\'t tell the others I come up here. I like the view. From up here Brill looks like it did.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970320, 'I remember the Deathguard\'s blade going in. I remember being grateful. Then I woke up again. Do you understand? I don\'t want to be grateful twice.', 'I remember the Deathguard\'s blade going in. I remember being grateful. Then I woke up again. Do you understand? I don\'t want to be grateful twice.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970321, 'Junior Apothecary Holland asked me to look at a sow that\'s farrowing. I said I\'ve never midwifed a pig. He said nor has anyone in Brill, these days. So I\'m going.', 'Junior Apothecary Holland asked me to look at a sow that\'s farrowing. I said I\'ve never midwifed a pig. He said nor has anyone in Brill, these days. So I\'m going.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970322, '$n! Come and be seen with me. The more people I\'m seen talking to, the fewer think I\'m here to eat them.', '$n! Come and be seen with me. The more people I\'m seen talking to, the fewer think I\'m here to eat them.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970323, 'I help Mortimer with the graves, nights. I listen for knocking. There hasn\'t been any since. I keep listening.', 'I help Mortimer with the graves, nights. I listen for knocking. There hasn\'t been any since. I keep listening.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970324, 'Isolde told me what was behind my wall. I\'ll be cutting thirty-one stones this winter, $n. I\'ll do them properly. It\'s what I owe.', 'Isolde told me what was behind my wall. I\'ll be cutting thirty-one stones this winter, $n. I\'ll do them properly. It\'s what I owe.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970325, 'Three commissions already. Forsaken want their names on something solid. I understand the feeling.', 'Three commissions already. Forsaken want their names on something solid. I understand the feeling.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970326, 'I mend what the Deathguard break. Steps, walls, the odd gravestone. Nobody asks where I learned. Suits me.', 'I mend what the Deathguard break. Steps, walls, the odd gravestone. Nobody asks where I learned. Suits me.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970327, 'Nobody knows. They think I came down from the Undercity for the quiet. I let them. I\'m making shrouds for Mortimer, good ones. Somebody ought to be buried properly.', 'Nobody knows. They think I came down from the Undercity for the quiet. I let them. I\'m making shrouds for Mortimer, good ones. Somebody ought to be buried properly.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970328, 'A girl from the inn stared at me for a whole afternoon, and then asked me to teach her to spin. I almost ran. I didn\'t.', 'A girl from the inn stared at me for a whole afternoon, and then asked me to teach her to spin. I almost ran. I didn\'t.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970329, 'Dillinger offered me a tabard. Me, in the Deathguard. After what they did. ...I\'m thinking about it. Somebody ought to remember what it\'s like on the other end.', 'Dillinger offered me a tabard. Me, in the Deathguard. After what they did. ...I\'m thinking about it. Somebody ought to remember what it\'s like on the other end.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970330, 'I stand the north road at night. Nobody asked me to. Old habit. Brill militia: he stood.', 'I stand the north road at night. Nobody asked me to. Old habit. Brill militia: he stood.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (970400, 'Faranell wrote back. Three pages of questions and no thanks, and Crane\'s name misspelled twice. Still, the Society has it now, and the Society forgets nothing it can use.', 'Faranell wrote back. Three pages of questions and no thanks, and Crane\'s name misspelled twice. Still, the Society has it now, and the Society forgets nothing it can use.', 0.333, 'Crane says \'yes, Apothecary\' again. I had grown used to the alternative. I find I do not care for the old way as much.', 'Crane says \'yes, Apothecary\' again. I had grown used to the alternative. I find I do not care for the old way as much.', 0.333, 'A courier from the Undercity asked whether I had any other apprentices with ideas. I told him no. It was very nearly true.', 'A courier from the Undercity asked whether I had any other apprentices with ideas. I told him no. It was very nearly true.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (970401, 'Crane is at his bench before I am at mine. I have caught him humming. It is deeply unsettling.', 'Crane is at his bench before I am at mine. I have caught him humming. It is deeply unsettling.', 0.333, 'I check his ledger every night. He checks mine. It is like having a conscience, only one that washes glassware.', 'I check his ledger every night. He checks mine. It is like having a conscience, only one that washes glassware.', 0.333, 'The healed hound is still alive. I have named it Exhibit A. Crane calls it something else, and I have chosen not to hear what.', 'The healed hound is still alive. I have named it Exhibit A. Crane calls it something else, and I have chosen not to hear what.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (970402, 'There is still a black patch behind the shed. I haven\'t had it raked. A reminder is cheaper than a sermon.', 'There is still a black patch behind the shed. I haven\'t had it raked. A reminder is cheaper than a sermon.', 0.333, 'Crane scrubs the floors now as well as the glass. I did not ask him to. I have not asked him to stop.', 'Crane scrubs the floors now as well as the glass. I did not ask him to. I have not asked him to stop.', 0.333, 'Some nights I think of what was in those notes. Then I think of the third hound. Then I go back to work.', 'Some nights I think of what was in those notes. Then I think of the third hound. Then I go back to work.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970403, 'Solliden, $n. My salts, and a name. My inventories do not lie. People do. Go and find out which of them.', 'Solliden, $n. My salts, and a name. My inventories do not lie. People do. Go and find out which of them.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970404, 'Holland says the cask under the bridge was Society work, from before my time. I checked the batch numbers anyway. Twice. I wanted to be sure it wasn\'t mine. I suppose nothing is mine now.', 'Holland says the cask under the bridge was Society work, from before my time. I checked the batch numbers anyway. Twice. I wanted to be sure it wasn\'t mine. I suppose nothing is mine now.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970405, 'Johaan has me boiling every drop I use, since the well. He says if we\'re going to keep bodies whole we\'ll start by not poisoning them. I\'ve written that on the wall.', 'Johaan has me boiling every drop I use, since the well. He says if we\'re going to keep bodies whole we\'ll start by not poisoning them. I\'ve written that on the wall.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (970406, 'The Society sent a courier for the notes. He read the first page on the doorstep and laughed. I don\'t know what that means. I\'ve decided not to find out.', 'The Society sent a courier for the notes. He read the first page on the doorstep and laughed. I don\'t know what that means. I\'ve decided not to find out.', 0.333, 'Yes, Apothecary. No, Apothecary. I\'ve had a great deal of practice.', 'Yes, Apothecary. No, Apothecary. I\'ve had a great deal of practice.', 0.333, 'Maybe they\'ll make something of it. Maybe in ten years some Deathguard will keep his fingers and never know my name. That would be all right. I think that would be all right.', 'Maybe they\'ll make something of it. Maybe in ten years some Deathguard will keep his fingers and never know my name. That would be all right. I think that would be all right.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (970407, 'Johaan checks every dose twice. He says it\'s to keep me honest. I think he\'s interested. Don\'t tell him I said so.', 'Johaan checks every dose twice. He says it\'s to keep me honest. I think he\'s interested. Don\'t tell him I said so.', 0.333, 'Small doses, slow work, everything written down. It\'ll take years. We have years. It\'s the one thing we have plenty of.', 'Small doses, slow work, everything written down. It\'ll take years. We have years. It\'s the one thing we have plenty of.', 0.333, 'The hound\'s flank is still closed. Six weeks now. I go out and look at it every morning, like it\'s the sunrise.', 'The hound\'s flank is still closed. Six weeks now. I go out and look at it every morning, like it\'s the sunrise.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (970408, 'I scrub the floors now as well as the glass. Johaan says it\'s so I\'ll know what\'s under my feet. I think it\'s so I won\'t have time to think.', 'I scrub the floors now as well as the glass. Johaan says it\'s so I\'ll know what\'s under my feet. I think it\'s so I won\'t have time to think.', 0.333, 'It was right to burn it. I tell myself so every morning, when I count my fingers.', 'It was right to burn it. I tell myself so every morning, when I count my fingers.', 0.333, 'The healed hound got out of its cage, they tell me. Somewhere in the hills there\'s one darkhound that won\'t rot. Good luck to it.', 'The healed hound got out of its cage, they tell me. Somewhere in the hills there\'s one darkhound that won\'t rot. Good luck to it.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970409, 'You have the notes. Don\'t read me what you\'ve decided. I\'ll find out from his face.', 'You have the notes. Don\'t read me what you\'ve decided. I\'ll find out from his face.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970410, 'You\'ve seen the hand. You might as well see the rest.', 'You\'ve seen the hand. You might as well see the rest.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970411, 'The shed? It\'s... storage. For storage things. I wouldn\'t go near it, the smell\'s awful. You\'ll want to stay upwind. Far upwind.', 'The shed? It\'s... storage. For storage things. I wouldn\'t go near it, the smell\'s awful. You\'ll want to stay upwind. Far upwind.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (970412, 'Apprentice Crane. If you\'re looking for the Apothecary, he\'s inside, being disappointed in something.', 'Apprentice Crane. If you\'re looking for the Apothecary, he\'s inside, being disappointed in something.', 0.333, 'Mind the basin; it\'s lye. It\'ll take the skin off. Not that I\'d notice for a day or two.', 'Mind the basin; it\'s lye. It\'ll take the skin off. Not that I\'d notice for a day or two.', 0.333, 'Three years I\'ve washed his glass. I could tell you every crack in every retort in Brill. Nobody asks.', 'Three years I\'ve washed his glass. I could tell you every crack in every retort in Brill. Nobody asks.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (970500, 'I went to Apothecary Johaan yesterday and asked him straight out: can it be undone? He laughed at me, then he stopped laughing and gave me a very long answer that meant no. It helped, oddly. A door shut properly is easier than one left ajar.', 'I went to Apothecary Johaan yesterday and asked him straight out: can it be undone? He laughed at me, then he stopped laughing and gave me a very long answer that meant no. It helped, oddly. A door shut properly is easier than one left ajar.', 0.333, 'Deathguard Cyrus asked after my knees today. My knees! I\'ve no feeling in them since the plague. But he asked. I think that\'s what Anselm was really selling me, $n. Someone who\'d ask.', 'Deathguard Cyrus asked after my knees today. My knees! I\'ve no feeling in them since the plague. But he asked. I think that\'s what Anselm was really selling me, $n. Someone who\'d ask.', 0.333, 'A letter came from Brother Anselm. I put it in the lamp by the inn and lit it with the rest. Best light that lamp\'s ever given.', 'A letter came from Brother Anselm. I put it in the lamp by the inn and lit it with the rest. Best light that lamp\'s ever given.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970501, 'Evening, $n. The lamps are lit on time and no one knows when but the watch. (He polishes a lamp-glass, and doesn\'t quite meet your eyes.) I\'m trying. That\'s all I can say. I\'m trying.', 'Evening, $n. The lamps are lit on time and no one knows when but the watch. (He polishes a lamp-glass, and doesn\'t quite meet your eyes.) I\'m trying. That\'s all I can say. I\'m trying.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970502, '(Lowell\'s hands are shaking around the lamp-pole.) Have you decided? I\'d rather know.', '(Lowell\'s hands are shaking around the lamp-pole.) Have you decided? I\'d rather know.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970503, 'Evening. (Lowell\'s eyes flick to you and away again.) The lamps won\'t light themselves, $g sir:madam;.', 'Evening. (Lowell\'s eyes flick to you and away again.) The lamps won\'t light themselves, $g sir:madam;.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (970504, 'Evening, $g sir:madam;. Mind the ladder. I\'ve a dozen lamps to light before the watch changes, and the north road ones are always last.', 'Evening, $g sir:madam;. Mind the ladder. I\'ve a dozen lamps to light before the watch changes, and the north road ones are always last.', 0.333, 'Forty years I\'ve lit these lamps. Kings, plague, and now the Dark Lady, and the lamps never cared which. There\'s a comfort in that, isn\'t there?', 'Forty years I\'ve lit these lamps. Kings, plague, and now the Dark Lady, and the lamps never cared which. There\'s a comfort in that, isn\'t there?', 0.333, 'The Deathguard like a bit of company on the night round. They tell me everything. Who\'s tired, who\'s sore, who\'s late. I just listen. Someone ought to.', 'The Deathguard like a bit of company on the night round. They tell me everything. Who\'s tired, who\'s sore, who\'s late. I just listen. Someone ought to.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970505, '(The zealot is praying under his breath. When he sees you, he stops.) Anselm will hear what you did to his lamb. The Light keeps an account, abomination.', '(The zealot is praying under his breath. When he sees you, he stops.) Anselm will hear what you did to his lamb. The Light keeps an account, abomination.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970506, 'The Royal Apothecary Society took Lowell Marsh to the Undercity this morning. I asked what would become of him and was told it was a matter for the Dark Lady\'s agents. I have decided to be satisfied with that answer. Brill\'s patrols are its own again, $n. That is what matters. That is what I keep telling myself.', 'The Royal Apothecary Society took Lowell Marsh to the Undercity this morning. I asked what would become of him and was told it was a matter for the Dark Lady\'s agents. I have decided to be satisfied with that answer. Brill\'s patrols are its own again, $n. That is what matters. That is what I keep telling myself.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970507, 'Lowell Marsh is gone. He left his ladder against the inn wall and walked off in the night, and the north road lamp was burning when the watch found it, though no one remembers lighting it. (Sevren studies you a moment.) I don\'t suppose you\'d know anything about that. No. Of course you wouldn\'t.', 'Lowell Marsh is gone. He left his ladder against the inn wall and walked off in the night, and the north road lamp was burning when the watch found it, though no one remembers lighting it. (Sevren studies you a moment.) I don\'t suppose you\'d know anything about that. No. Of course you wouldn\'t.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970508, 'The letters have stopped. Whoever it was lost his nerve, or his priest. (Sevren glances out of the window, toward the lamplighter working in the square.) I have decided not to wonder why the lamps have been lit so very carefully lately. A magistrate must choose what to wonder about.', 'The letters have stopped. Whoever it was lost his nerve, or his priest. (Sevren glances out of the window, toward the lamplighter working in the square.) I have decided not to wonder why the lamps have been lit so very carefully lately. A magistrate must choose what to wonder about.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (970509, 'A letter came for you, love. No name on the outside, just yours. (It reads:) "The ferry at the Sepulcher takes anyone who pays. I mend nets now on the Silverpine coast. The fishermen don\'t ask what I am; the fog makes us all the same color. I think of the north road lamp. W."', 'A letter came for you, love. No name on the outside, just yours. (It reads:) "The ferry at the Sepulcher takes anyone who pays. I mend nets now on the Silverpine coast. The fishermen don\'t ask what I am; the fog makes us all the same color. I think of the north road lamp. W."', 0.333, 'Another letter for you. (It reads:) "I\'ve heard nothing from Brother Anselm and I\'ve stopped listening for him. A worgen came down to the shore last night and we looked at each other a long while and then it went away. There\'s a lesson in that, I think. Not a comfortable one. W."', 'Another letter for you. (It reads:) "I\'ve heard nothing from Brother Anselm and I\'ve stopped listening for him. A worgen came down to the shore last night and we looked at each other a long while and then it went away. There\'s a lesson in that, I think. Not a comfortable one. W."', 0.333, 'One more of these came for you. Same shaky hand. (It reads:) "A Forsaken captain is taking volunteers for Northrend. They say no one there asks where you came from, only whether you\'ll stand. I\'m going to try standing. Light a lamp for me, if Brill\'s found anyone to light them. W."', 'One more of these came for you. Same shaky hand. (It reads:) "A Forsaken captain is taking volunteers for Northrend. They say no one there asks where you came from, only whether you\'ll stand. I\'m going to try standing. Light a lamp for me, if Brill\'s found anyone to light them. W."', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970510, 'You\'re the one who found the lamplighter out. (Burgess straightens.) Two of mine died on that east road. Pell was a friend. If you ever need a blade at your back in Brill, $n, you\'ll have mine.', 'You\'re the one who found the lamplighter out. (Burgess straightens.) Two of mine died on that east road. Pell was a friend. If you ever need a blade at your back in Brill, $n, you\'ll have mine.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970511, 'Lamplighter vanished the same night you were seen talking with him by the well. (Burgess\'s eyes narrow.) I\'m sure that\'s nothing, $g sir:madam;. Move along.', 'Lamplighter vanished the same night you were seen talking with him by the well. (Burgess\'s eyes narrow.) I\'m sure that\'s nothing, $g sir:madam;. Move along.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970512, 'Lowell\'s been walking the night round with me again. Asks after my knees. (Cyrus snorts.) My knees! But it\'s company. Odd: he never asks about the watch hours anymore. Used to be all he talked about.', 'Lowell\'s been walking the night round with me again. Asks after my knees. (Cyrus snorts.) My knees! But it\'s company. Odd: he never asks about the watch hours anymore. Used to be all he talked about.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970513, 'Lowell Marsh. I told him about my hours myself, every night for a year. (Cyrus stares at nothing.) I thought he was listening because he cared.', 'Lowell Marsh. I told him about my hours myself, every night for a year. (Cyrus stares at nothing.) I thought he was listening because he cared.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970514, 'Nobody\'s lit the lamps since Marsh left. The Executor says he\'ll find someone. Meanwhile we walk in the dark. Funny how you don\'t notice a man until he\'s gone.', 'Nobody\'s lit the lamps since Marsh left. The Executor says he\'ll find someone. Meanwhile we walk in the dark. Funny how you don\'t notice a man until he\'s gone.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970515, 'Patrol hours changed overnight on the Magistrate\'s word, and the Crusade hasn\'t touched a cart since. Someone did good work, $n. I hear it was you.', 'Patrol hours changed overnight on the Magistrate\'s word, and the Crusade hasn\'t touched a cart since. Someone did good work, $n. I hear it was you.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970516, 'We kept the lamplighter down here one night, before the apothecaries came for him. He sat by the zealots\' cell and didn\'t say a word to them. They prayed for him the whole night. Worst sound I ever heard.', 'We kept the lamplighter down here one night, before the apothecaries came for him. He sat by the zealots\' cell and didn\'t say a word to them. They prayed for him the whole night. Worst sound I ever heard.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970517, 'The zealot\'s stopped gloating since you came down here with those letters. Whatever you did up there, keep doing it.', 'The zealot\'s stopped gloating since you came down here with those letters. Whatever you did up there, keep doing it.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970600, '(BY ORDER OF THE CROWN OF LORDAERON. THIS HOLDING IS UNDER QUARANTINE. NO PERSON SHALL ENTER OR LEAVE. GRAIN FROM THIS HOLDING IS TO BE BURNED.$B$BBelow, in pencil: we did burn it. it didn\'t help.)', '(BY ORDER OF THE CROWN OF LORDAERON. THIS HOLDING IS UNDER QUARANTINE. NO PERSON SHALL ENTER OR LEAVE. GRAIN FROM THIS HOLDING IS TO BE BURNED.$B$BBelow, in pencil: we did burn it. it didn\'t help.)', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970601, '(The Balnirs: Osric and Ada; Tobias, to wed Marian Hale, the date scratched out and written again three times; Agnes.$B$BThen, in Osric\'s shaking hand, all one autumn: Marian. Tobias. Ada. In another hand: Osric.$B$BBeside Agnes: in service, Silverpine.)', '(The Balnirs: Osric and Ada; Tobias, to wed Marian Hale, the date scratched out and written again three times; Agnes.$B$BThen, in Osric\'s shaking hand, all one autumn: Marian. Tobias. Ada. In another hand: Osric.$B$BBeside Agnes: in service, Silverpine.)', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`, `text3_0`, `text3_1`, `Probability3`) VALUES (970602, 'Customer! A living one, or near enough. Mind the candlesticks in the window: they\'re not for sale. Everything else is, and most of it is older than you are.', 'Customer! A living one, or near enough. Mind the candlesticks in the window: they\'re not for sale. Everything else is, and most of it is older than you are.', 0.250, 'Welcome, welcome. Business is excellent. Nobody in Brill needs light to see by, so they buy candles for the smell. You\'d be amazed what people want to smell like, round here.', 'Welcome, welcome. Business is excellent. Nobody in Brill needs light to see by, so they buy candles for the smell. You\'d be amazed what people want to smell like, round here.', 0.250, 'Two candles in the window, burning for a wedding. Folk ask who they\'re for. I tell them a customer. The best kind: paid in full and never complains.', 'Two candles in the window, burning for a wedding. Folk ask who they\'re for. I tell them a customer. The best kind: paid in full and never complains.', 0.250, 'Ah, $n. Come in. I\'ve a pocket watch that stopped the hour its owner did. Very reasonable. It\'s right twice a day, which is more than most of my customers manage.', 'Ah, $n. Come in. I\'ve a pocket watch that stopped the hour its owner did. Very reasonable. It\'s right twice a day, which is more than most of my customers manage.', 0.250);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`, `text3_0`, `text3_1`, `Probability3`) VALUES (970603, 'Customer! The candlesticks are for sale, if you\'re marrying. Nobody\'s asked yet. Forsaken courtship is slow, I\'m told. Something about the hands coming off.', 'Customer! The candlesticks are for sale, if you\'re marrying. Nobody\'s asked yet. Forsaken courtship is slow, I\'m told. Something about the hands coming off.', 0.250, 'Welcome, welcome. Wrapping paper, $n? Red ribbon or blue. I\'ve a great deal of practice wrapping things that never get collected.', 'Welcome, welcome. Wrapping paper, $n? Red ribbon or blue. I\'ve a great deal of practice wrapping things that never get collected.', 0.250, 'Sold three candles to a Deathguard this morning. He didn\'t say what for. In Brill, you learn not to ask what the candles are for.', 'Sold three candles to a Deathguard this morning. He didn\'t say what for. In Brill, you learn not to ask what the candles are for.', 0.250, 'Ah, $n. I\'ve a mirror in stock. Broken, I\'m afraid. Most of my customers prefer it that way.', 'Ah, $n. I\'ve a mirror in stock. Broken, I\'m afraid. Most of my customers prefer it that way.', 0.250);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (970604, 'Open for business, $n. Candles, curios, and a very good price on handkerchiefs. Funerals and weddings both: I don\'t ask which.', 'Open for business, $n. Candles, curios, and a very good price on handkerchiefs. Funerals and weddings both: I don\'t ask which.', 0.500, 'Customer! Come in, come in, before you die. Though if you do, I\'ll still be here.', 'Customer! Come in, come in, before you die. Though if you do, I\'ll still be here.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970605, 'That\'s Agnes Balnir\'s hand on that letter. I\'d know it anywhere: she used to sign for her father\'s wax. Well? Give it here. No. Wait. Tell me first. Then give it here.', 'That\'s Agnes Balnir\'s hand on that letter. I\'d know it anywhere: she used to sign for her father\'s wax. Well? Give it here. No. Wait. Tell me first. Then give it here.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970606, 'Silverpine. I\'ve not been out of Brill since I woke up. I\'d lose the custom. Not that I\'ve any. Go on, $n: the Sepulcher. Tell her it\'s paid in full.', 'Silverpine. I\'ve not been out of Brill since I woke up. I\'d lose the custom. Not that I\'ve any. Go on, $n: the Sepulcher. Tell her it\'s paid in full.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970607, 'The Balnir Farmstead, $n. South and east. When you come back, try not to look at me like that. I can see your face from here. Well. With the one eye.', 'The Balnir Farmstead, $n. South and east. When you come back, try not to look at me like that. I can see your face from here. Well. With the one eye.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970608, 'Mind the counter. It\'s held up a good deal of business in its time, and lately it\'s been holding up me.', 'Mind the counter. It\'s held up a good deal of business in its time, and lately it\'s been holding up me.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970609, 'Closed. We\'re closed. There\'s an order outstanding, and until it\'s collected, nothing in this stall is for sale. No, not even that. Especially not that.', 'Closed. We\'re closed. There\'s an order outstanding, and until it\'s collected, nothing in this stall is for sale. No, not even that. Especially not that.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970610, 'Did he open the shutters? Good. Good. Tobias always said old Wicke would have sold candles to the sun if it stood still long enough.', 'Did he open the shutters? Good. Good. Tobias always said old Wicke would have sold candles to the sun if it stood still long enough.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970611, 'Shrouds don\'t wash themselves, $n. Well. Some of them try. Those I report to the Deathguard.', 'Shrouds don\'t wash themselves, $n. Well. Some of them try. Those I report to the Deathguard.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970612, 'Laundry? Leave it there, and careful what you hand me: half of what comes in here used to belong to someone, and they may want it back.', 'Laundry? Leave it there, and careful what you hand me: half of what comes in here used to belong to someone, and they may want it back.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (970700, 'Harlan stood his whole watch last night and the night before. Didn\'t miss a bell. (Dillinger almost smiles.) Brill owes you for that, $n. So do I.', 'Harlan stood his whole watch last night and the night before. Didn\'t miss a bell. (Dillinger almost smiles.) Brill owes you for that, $n. So do I.', 0.500, 'Quiet on the north road. Harlan sees to it. Took his rest day at Solliden, came back before the bell, same as he promised. You\'re welcome at my fire any night you like, $n.', 'Quiet on the north road. Harlan sees to it. Took his rest day at Solliden, came back before the bell, same as he promised. You\'re welcome at my fire any night you like, $n.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (970701, 'Harlan\'s taken to the cemetery watch like he was born to it. Well. Died to it. He doesn\'t look west anymore. Brill\'s in your debt, $n.', 'Harlan\'s taken to the cemetery watch like he was born to it. Well. Died to it. He doesn\'t look west anymore. Brill\'s in your debt, $n.', 0.500, 'New lad on the north road now; keen, careless. I miss Harlan\'s patience out there, but he\'s whole at the cemetery, and that\'s what counts. Good to see you, $n.', 'New lad on the north road now; keen, careless. I miss Harlan\'s patience out there, but he\'s whole at the cemetery, and that\'s what counts. Good to see you, $n.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970702, '$n. The watch knows your name now. Not many living or dead can say that in Brill.', '$n. The watch knows your name now. Not many living or dead can say that in Brill.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970703, 'That pug yours? Corn, is it. Small, but he\'s one of ours now, stitches and all. Take him on your rounds; ghouls don\'t like a dog that doesn\'t flinch, and that one\'s past flinching.', 'That pug yours? Corn, is it. Small, but he\'s one of ours now, stitches and all. Take him on your rounds; ghouls don\'t like a dog that doesn\'t flinch, and that one\'s past flinching.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970704, 'Any word of Harlan? (Dillinger glances toward the north road.) I\'ll stand his watch until you\'re back.', 'Any word of Harlan? (Dillinger glances toward the north road.) I\'ll stand his watch until you\'re back.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970705, 'You\'re the one who found Sevren\'s leak. Two of ours died on that east road. (Dillinger nods.) If you\'ve a mind to help the watch, I\'ve work.', 'You\'re the one who found Sevren\'s leak. Two of ours died on that east road. (Dillinger nods.) If you\'ve a mind to help the watch, I\'ve work.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970706, 'My rest day. (Harlan doesn\'t look away from the cottage.) I stand here till the lamp goes out, then I walk back and take the dawn watch. Once a week. It\'s enough. It has to be.', 'My rest day. (Harlan doesn\'t look away from the cottage.) I stand here till the lamp goes out, then I walk back and take the dawn watch. Once a week. It\'s enough. It has to be.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970707, 'Last time. I told myself that, coming up the hill. (Harlan turns away from the cottage.) I\'ll be at the cemetery tomorrow, facing east. Don\'t tell me if the lamp\'s still lit.', 'Last time. I told myself that, coming up the hill. (Harlan turns away from the cottage.) I\'ll be at the cemetery tomorrow, facing east. Don\'t tell me if the lamp\'s still lit.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970708, 'A pug. (Something in Harlan\'s face softens.) We had a dog. Lise named it Pudding. Leave yours here with me while you go down; the farmers will take him for a stray and loose the hounds.', 'A pug. (Something in Harlan\'s face softens.) We had a dog. Lise named it Pudding. Leave yours here with me while you go down; the farmers will take him for a stray and loose the hounds.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970709, '(Harlan watches the cottage below. Smoke rises from its chimney.)', '(Harlan watches the cottage below. Smoke rises from its chimney.)', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970710, 'Move along. I\'m on patrol. (The Deathguard keeps his eyes on the farmstead below, and doesn\'t seem to be patrolling anything.)', 'Move along. I\'m on patrol. (The Deathguard keeps his eyes on the farmstead below, and doesn\'t seem to be patrolling anything.)', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970711, 'No firewood at the gate this month. (Maren pulls her shawl tighter.) Silly. I\'d started thinking of it as a friend. Some kind neighbor I never saw.', 'No firewood at the gate this month. (Maren pulls her shawl tighter.) Silly. I\'d started thinking of it as a friend. Some kind neighbor I never saw.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970712, 'Wood at the gate again this morning. Every seventh day, now, regular as a bell. (She smiles, a little puzzled.) Whoever it is, I hope they\'re warm.', 'Wood at the gate again this morning. Every seventh day, now, regular as a bell. (She smiles, a little puzzled.) Whoever it is, I hope they\'re warm.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970713, '(The woman by the cottage stiffens when she sees you, one hand on the doorframe.) We\'ve nothing worth taking, stranger. The farmers are just across the yard.', '(The woman by the cottage stiffens when she sees you, one hand on the doorframe.) We\'ve nothing worth taking, stranger. The farmers are just across the yard.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970714, '(A girl of eleven or so peers at you from behind the fence.) Mama says not to talk to strangers from Brill.', '(A girl of eleven or so peers at you from behind the fence.) Mama says not to talk to strangers from Brill.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970715, 'Rest day tomorrow. (Harlan\'s eyes go west, just for a moment, then back to the road.) Quiet watch. Exactly how I like it.', 'Rest day tomorrow. (Harlan\'s eyes go west, just for a moment, then back to the road.) Quiet watch. Exactly how I like it.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970716, 'North road\'s clear, $n. Not a ghoul between here and the river. (He nods once.) Thanks to you, I\'m standing where I ought to be.', 'North road\'s clear, $n. Not a ghoul between here and the river. (He nods once.) Thanks to you, I\'m standing where I ought to be.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970717, 'The dead in this cemetery don\'t want anything from me. (Harlan leans on his halberd.) There\'s a peace in that. Most days.', 'The dead in this cemetery don\'t want anything from me. (Harlan leans on his halberd.) There\'s a peace in that. Most days.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970718, 'Cemetery watch, $n. Facing east, toward the Plaguelands and whatever comes out of them. (He doesn\'t look back over his shoulder. It seems to take some effort.)', 'Cemetery watch, $n. Facing east, toward the Plaguelands and whatever comes out of them. (He doesn\'t look back over his shoulder. It seems to take some effort.)', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970800, 'That Crane lad comes by every morning for a bucket now. Says the Apothecary insists on clean water for his work. Nice manners. Short a few fingers. Aren\'t we all.', 'That Crane lad comes by every morning for a bucket now. Says the Apothecary insists on clean water for his work. Nice manners. Short a few fingers. Aren\'t we all.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970801, 'Johaan\'s apprentice scrubs the laboratory floors with my water now. He asked me once whether I thought he\'d done right. I told him I wash other people\'s stains for a living, and I don\'t ask how they got there.', 'Johaan\'s apprentice scrubs the laboratory floors with my water now. He asked me once whether I thought he\'d done right. I told him I wash other people\'s stains for a living, and I don\'t ask how they got there.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970802, 'Society couriers through the square twice this week, carrying crates up from Johaan\'s. They didn\'t stop for water. I didn\'t offer.', 'Society couriers through the square twice this week, carrying crates up from Johaan\'s. They didn\'t stop for water. I didn\'t offer.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (970803, 'Clean water, clean linen, and Renee\'s paying me again. A body can\'t ask for more. Well, a living one could. I\'ve stopped asking.', 'Clean water, clean linen, and Renee\'s paying me again. A body can\'t ask for more. Well, a living one could. I\'ve stopped asking.', 0.333, 'Draw yourself a bucket, if you like. It\'s the best water in Tirisfal now. That isn\'t saying much, but I\'ll say it.', 'Draw yourself a bucket, if you like. It\'s the best water in Tirisfal now. That isn\'t saying much, but I\'ll say it.', 0.333, 'Hear that? The windlass. I used to hate the sound. Now I sing along. Badly. I was always bad.', 'Hear that? The windlass. I used to hate the sound. Now I sing along. Badly. I was always bad.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970804, 'Holland\'s powder? Go on, then. Tip it in. I\'ll hold my breath. Habit.', 'Holland\'s powder? Go on, then. Tip it in. I\'ll hold my breath. Habit.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970805, 'I\'ve been washing in rainwater from the barrels. Do you know how long it takes to fill a tub from a barrel? Neither did I. Now I know.', 'I\'ve been washing in rainwater from the barrels. Do you know how long it takes to fill a tub from a barrel? Neither did I. Now I know.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (970806, 'Don\'t drink from that well. Don\'t even look into it too long. It looks back.', 'Don\'t drink from that well. Don\'t even look into it too long. It looks back.', 0.500, 'Maudie Fenwick, laundress. If it\'s stained, I\'ve washed it. If it\'s cursed, I\'ve washed it twice.', 'Maudie Fenwick, laundress. If it\'s stained, I\'ve washed it. If it\'s cursed, I\'ve washed it twice.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970807, 'I asked about batch nine in the Undercity. Nobody remembered it. Everybody remembered to tell me not to ask again. Crane says that\'s how the Society says thank you.', 'I asked about batch nine in the Undercity. Nobody remembered it. Everybody remembered to tell me not to ask again. Crane says that\'s how the Society says thank you.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (970808, 'The samples from the cistern are clean. I\'ve kept one of the old ones in a sealed jar on my shelf. For science. And to remind me to look at the water now and then.', 'The samples from the cistern are clean. I\'ve kept one of the old ones in a sealed jar on my shelf. For science. And to remind me to look at the water now and then.', 0.500, 'Maudie says the robes come back whiter now. I\'ve told her robes aren\'t meant to be white. She ignored me.', 'Maudie says the robes come back whiter now. I\'ve told her robes aren\'t meant to be white. She ignored me.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970809, 'Under the covered bridge, west on the Deathknell road. Burst the sacs. All of them, if you can.', 'Under the covered bridge, west on the Deathknell road. Burst the sacs. All of them, if you can.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970900, '(HESTER LYLE, HER BOOK. \'Third day below. Master Croft says the air here is clean and the plague cannot follow. The children are frightened of the Agamand vaults but I tell them the dead are only sleeping. God forgive me, I believed it.\')', '(HESTER LYLE, HER BOOK. \'Third day below. Master Croft says the air here is clean and the plague cannot follow. The children are frightened of the Agamand vaults but I tell them the dead are only sleeping. God forgive me, I believed it.\')', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970901, '(Accounts in a baker\'s hand, flour and salt, and then: \'Croft brought bread again. Good white bread. Where does he get the flour, with the mills shut? Lyle\'s youngest has the cough. Croft says it is only the damp. Croft says a great deal.\')', '(Accounts in a baker\'s hand, flour and salt, and then: \'Croft brought bread again. Good white bread. Where does he get the flour, with the mills shut? Lyle\'s youngest has the cough. Croft says it is only the damp. Croft says a great deal.\')', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970902, '(Letters practised over and over in a careful round hand, and then, near the end: \'Mother says the doors are bricked. Master Croft says it is for our own good. Mother has stopped answering. I am going to be brave like Da.\')', '(Letters practised over and over in a careful round hand, and then, near the end: \'Mother says the doors are bricked. Master Croft says it is for our own good. Mother has stopped answering. I am going to be brave like Da.\')', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970903, '(A stack of letters, each addressed TO MY MASTER, IN NORTHREND. \'Brill is tended. The flock is counted.\' \'I await your instruction.\' \'The Banshee\'s rabble walk my town as if it were theirs.\' \'Master, I have been patient.\' The most recent is only one line, written many times: \'Answer me.\')', '(A stack of letters, each addressed TO MY MASTER, IN NORTHREND. \'Brill is tended. The flock is counted.\' \'I await your instruction.\' \'The Banshee\'s rabble walk my town as if it were theirs.\' \'Master, I have been patient.\' The most recent is only one line, written many times: \'Answer me.\')', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970904, '(Thirty-one names in a fine, careful hand, each with the date of its raising and its use. SENTINEL. SENTINEL. LABOURER. SENTINEL.)', '(Thirty-one names in a fine, careful hand, each with the date of its raising and its use. SENTINEL. SENTINEL. LABOURER. SENTINEL.)', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970905, 'The crypt\'s walled again, the right way this time: no marks, no gifts, no Croft. I\'ll be moving on soon. Before I go: well done. I don\'t say it often.', 'The crypt\'s walled again, the right way this time: no marks, no gifts, no Croft. I\'ll be moving on soon. Before I go: well done. I don\'t say it often.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970906, 'Why are you looking for me here? I said I\'d meet you at the crypt. North, past the mills.', 'Why are you looking for me here? I said I\'d meet you at the crypt. North, past the mills.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970907, '(A woman in a dark hood studies the mausoleum\'s stonework with great interest. She doesn\'t look at you.)$B$BKeep walking as if we\'re strangers. We are, for now.', '(A woman in a dark hood studies the mausoleum\'s stonework with great interest. She doesn\'t look at you.)$B$BKeep walking as if we\'re strangers. We are, for now.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970908, 'Sealed. My way. Go home, $n. Light a candle. Not his.', 'Sealed. My way. Go home, $n. Light a candle. Not his.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970909, 'Mind the Agamands on the stair. They\'re only angry; they don\'t know any better.', 'Mind the Agamands on the stair. They\'re only angry; they don\'t know any better.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (970910, 'This crypt belongs to the Agamands. I\'m only resting. You\'ll want to keep walking.', 'This crypt belongs to the Agamands. I\'m only resting. You\'ll want to keep walking.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971000, 'Citizen $n. I do enjoy writing that. Is there something the town can do for you, for a change?', 'Citizen $n. I do enjoy writing that. Is there something the town can do for you, for a change?', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971001, 'The board\'s still up, $n. Some days I stand at the window and watch people read it. Nobody read anything in Brill for years.', 'The board\'s still up, $n. Some days I stand at the window and watch people read it. Nobody read anything in Brill for years.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971002, 'Six jobs, six openings, and not one roof fell on anybody. I\'ve built for kings, $n. Kings were easier. Kings didn\'t argue about the color of a chapel door.', 'Six jobs, six openings, and not one roof fell on anybody. I\'ve built for kings, $n. Kings were easier. Kings didn\'t argue about the color of a chapel door.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (971003, 'Rudd Carver, builder\'s yard. You bring it, we build it. You don\'t bring it, we stand here looking at the road.', 'Rudd Carver, builder\'s yard. You bring it, we build it. You don\'t bring it, we stand here looking at the road.', 0.333, 'Oswin Thatcher keeps coming round to tell my lads they\'re doing it wrong. He\'s usually right. Don\'t tell him.', 'Oswin Thatcher keeps coming round to tell my lads they\'re doing it wrong. He\'s usually right. Don\'t tell him.', 0.333, 'Materials go on the left. Tools on the right. The pile in the middle is somebody\'s lunch from the plague year; nobody touch it.', 'Materials go on the left. Tools on the right. The pile in the middle is somebody\'s lunch from the plague year; nobody touch it.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971100, '(Names, cut into the plaster at every height a hand could reach. Low down, where a child would sit, a little house with smoke coming out of the chimney, and under it: WE ARE STILL HERE.)', '(Names, cut into the plaster at every height a hand could reach. Low down, where a child would sit, a little house with smoke coming out of the chimney, and under it: WE ARE STILL HERE.)', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971101, '(In the margins, in a dozen hands: names, the price of bread, a recipe for willow-bark tea, and again and again: Light keep the door.)', '(In the margins, in a dozen hands: names, the price of bread, a recipe for willow-bark tea, and again and again: Light keep the door.)', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971102, '(Names and dates in the meeting house\'s hand. Beside one name, in another hand, much later: we got home.)', '(Names and dates in the meeting house\'s hand. Beside one name, in another hand, much later: we got home.)', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971103, 'Corven lit the candles at the door last night without being asked. I didn\'t say anything. If I praise him he\'ll stop to wonder why, and then he\'ll stop lighting them.', 'Corven lit the candles at the door last night without being asked. I didn\'t say anything. If I praise him he\'ll stop to wonder why, and then he\'ll stop lighting them.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971104, 'Benches, $n. People have started coming in to sit on them. One of them asked me what the rules were. I told her there\'s only one: no one gets to tell you what you are. She asked if that included me. I said especially me.', 'Benches, $n. People have started coming in to sit on them. One of them asked me what the rules were. I told her there\'s only one: no one gets to tell you what you are. She asked if that included me. I said especially me.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971105, 'Halden objects to everything I say and then does it better than I asked. I\'ve decided to find this restful.', 'Halden objects to everything I say and then does it better than I asked. I\'ve decided to find this restful.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971106, '(A tall Forsaken in black and violet regards the burnt meeting house as though it owes her money.)$B$BI was a priestess of the Light once. I prayed in buildings very like this one. You learn a great deal about a faith from what\'s left standing when it\'s gone.', '(A tall Forsaken in black and violet regards the burnt meeting house as though it owes her money.)$B$BI was a priestess of the Light once. I prayed in buildings very like this one. You learn a great deal about a faith from what\'s left standing when it\'s gone.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971107, 'Garren\'s barn, $n, under the hay at the back. And the chimney. Mind the soot; it\'s older than you.', 'Garren\'s barn, $n, under the hay at the back. And the chimney. Mind the soot; it\'s older than you.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971108, 'Half a roof. You know what half a roof is? It\'s a promise. I work on it nights, when the Cleric isn\'t here to suggest stained glass.', 'Half a roof. You know what half a roof is? It\'s a promise. I work on it nights, when the Cleric isn\'t here to suggest stained glass.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971109, 'Brother Halden. I was never anybody\'s brother, mind; the bishop gave everyone titles so he\'d have something to take away. Hand me that maul if you\'re staying.', 'Brother Halden. I was never anybody\'s brother, mind; the bishop gave everyone titles so he\'d have something to take away. Hand me that maul if you\'re staying.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (971110, 'I went and looked at it. WILLEM VALE, WHO KEPT THE DOOR. The bellringer cut it deeper than the others. I didn\'t ask him to.', 'I went and looked at it. WILLEM VALE, WHO KEPT THE DOOR. The bellringer cut it deeper than the others. I didn\'t ask him to.', 0.500, 'I still pray to the Light, $n. Here, at his grave. The Cleric knows. She brought me a candle.', 'I still pray to the Light, $n. Here, at his grave. The Cleric knows. She brought me a candle.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (971111, 'I read him in the book most evenings. Willem Vale, ferryman. Kept the door. It\'s enough. It\'s what he was.', 'I read him in the book most evenings. Willem Vale, ferryman. Kept the door. It\'s enough. It\'s what he was.', 0.500, 'I still pray to the Light, $n. Here, at his grave. The Cleric knows. She brought me a candle.', 'I still pray to the Light, $n. Here, at his grave. The Cleric knows. She brought me a candle.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971112, '(A thin Forsaken woman in a mended grey shawl stands at a small stone, a Light\'s sunburst wound round her fingers.)$B$BI come every evening. I don\'t pray to the Shadow. Don\'t send anyone to ask me to.', '(A thin Forsaken woman in a mended grey shawl stands at a small stone, a Light\'s sunburst wound round her fingers.)$B$BI come every evening. I don\'t pray to the Shadow. Don\'t send anyone to ask me to.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971113, 'I light them at dusk now. The candles. Nobody told me to; that\'s rather the point, I think.', 'I light them at dusk now. The candles. Nobody told me to; that\'s rather the point, I think.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971114, 'Did you stand at all three? What did you think? No, wait, don\'t tell me yet. I want to have my own answer first, so I can tell whether yours changes it.', 'Did you stand at all three? What did you think? No, wait, don\'t tell me yet. I want to have my own answer first, so I can tell whether yours changes it.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971115, 'Acolyte Corven Dusk. I woke up four months ago in a field near Deathknell, and I\'ve been asking questions ever since. Mirelle says that\'s a good sign. Brother Halden says it\'s a symptom.', 'Acolyte Corven Dusk. I woke up four months ago in a field near Deathknell, and I\'ve been asking questions ever since. Mirelle says that\'s a good sign. Brother Halden says it\'s a symptom.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971116, 'I come back here sometimes. The darkhounds keep coming back too. We have that in common, the darkhounds and I.', 'I come back here sometimes. The darkhounds keep coming back too. We have that in common, the darkhounds and I.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971117, '(Corven kneels at the worn stone priest, not quite praying.)$B$BHe hasn\'t got a face any more. Neither have some of us. Keep the hounds off, would you? I\'d like to finish my thought.', '(Corven kneels at the worn stone priest, not quite praying.)$B$BHe hasn\'t got a face any more. Neither have some of us. Keep the hounds off, would you? I\'d like to finish my thought.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971118, 'The chapel\'s full most evenings, $n, and half of them don\'t believe a word I say. I\'ve never been so pleased with a congregation.', 'The chapel\'s full most evenings, $n, and half of them don\'t believe a word I say. I\'ve never been so pleased with a congregation.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (971119, 'Sit, if you like. You needn\'t believe anything. The benches don\'t check.', 'Sit, if you like. You needn\'t believe anything. The benches don\'t check.', 0.333, 'The Forgotten Shadow asks very little: that you belong to yourself. Most days, that\'s plenty to be going on with.', 'The Forgotten Shadow asks very little: that you belong to yourself. Most days, that\'s plenty to be going on with.', 0.333, 'Halden rang the bell at dusk again. Nobody asked him to. I\'ve stopped asking him not to.', 'Halden rang the bell at dusk again. Nobody asked him to. I\'ve stopped asking him not to.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971120, '(Mirelle sits beside a cot with her hands folded, saying nothing at all, which the patient seems to find a great comfort.)$B$BEvening, $n. I\'m not here as a priestess. I\'m here as company. It\'s much harder.', '(Mirelle sits beside a cot with her hands folded, saying nothing at all, which the patient seems to find a great comfort.)$B$BEvening, $n. I\'m not here as a priestess. I\'m here as company. It\'s much harder.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (971121, 'Candles, $n? The black ones are for remembering. The white ones are for light to read by. I sell both. I think of them as the same thing, most days.', 'Candles, $n? The black ones are for remembering. The white ones are for light to read by. I sell both. I think of them as the same thing, most days.', 0.500, 'I\'ve been thinking about doors. Willem Vale\'s door. Ours. What it means to hold one.', 'I\'ve been thinking about doors. Willem Vale\'s door. Ours. What it means to hold one.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (971122, 'Candles, $n? Choose your own; I\'ve stopped recommending. It turns out people like being asked.', 'Candles, $n? Choose your own; I\'ve stopped recommending. It turns out people like being asked.', 0.500, 'I gave a sermon last week. Mirelle let me. It was all questions. Three people walked out and eleven stayed to argue.', 'I gave a sermon last week. Mirelle let me. It was all questions. Three people walked out and eleven stayed to argue.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (971123, 'Candles, $n? ...I\'ve been sparring with the Deathguard in the mornings. Mirelle says it\'s healthy to be able to hold on to things. She also says it\'s healthy to be able to let go of them. I\'m working on the first one.', 'Candles, $n? ...I\'ve been sparring with the Deathguard in the mornings. Mirelle says it\'s healthy to be able to hold on to things. She also says it\'s healthy to be able to let go of them. I\'m working on the first one.', 0.500, 'Strength is the reason. I still think so. I\'m just less sure what it\'s the reason for.', 'Strength is the reason. I still think so. I\'m just less sure what it\'s the reason for.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971124, 'Candles and reagents, $n. And questions, free of charge.', 'Candles and reagents, $n. And questions, free of charge.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (971125, 'I keep the candles at the wall lit. Dawn and dusk. You\'d be surprised how many names one candle covers.', 'I keep the candles at the wall lit. Dawn and dusk. You\'d be surprised how many names one candle covers.', 0.333, 'Bell\'s in good voice. Better than mine ever was.', 'Bell\'s in good voice. Better than mine ever was.', 0.333, 'Don\'t let the Cleric make you sit through a sermon. There\'s no sermon. She just likes watching people expect one.', 'Don\'t let the Cleric make you sit through a sermon. There\'s no sermon. She just likes watching people expect one.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971126, 'I don\'t pray here. I just sit. The Cleric says that counts for something. I haven\'t decided what.', 'I don\'t pray here. I just sit. The Cleric says that counts for something. I haven\'t decided what.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971127, 'We come in the evenings, Edith and I. It\'s the one place in Brill nobody stares. Everyone here is busy being quiet.', 'We come in the evenings, Edith and I. It\'s the one place in Brill nobody stares. Everyone here is busy being quiet.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971128, 'I sewed the cushions for the front bench. Nobody knows. I like it that way.', 'I sewed the cushions for the front bench. Nobody knows. I like it that way.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (971129, 'Rudd says the chapel gets the good stone. The library gets the good stone too. Rudd says a lot of things.', 'Rudd says the chapel gets the good stone. The library gets the good stone too. Rudd says a lot of things.', 0.333, 'Mind the scaffold. It\'s mostly holding.', 'Mind the scaffold. It\'s mostly holding.', 0.333, 'That bellringer\'s been up since before the bats. Does he sleep? Do any of us?', 'That bellringer\'s been up since before the bats. Does he sleep? Do any of us?', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971130, 'Oswin Thatcher. Jamie Nore sent me to check the builders aren\'t robbing the town. They\'re not. They\'re just slow. Halden\'s tenons are better than mine, which I will deny to my grave. My second one.', 'Oswin Thatcher. Jamie Nore sent me to check the builders aren\'t robbing the town. They\'re not. They\'re just slow. Halden\'s tenons are better than mine, which I will deny to my grave. My second one.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971200, '(On the flyleaf: GARREN. ASK BEFORE YOU BORROW.)', '(On the flyleaf: GARREN. ASK BEFORE YOU BORROW.)', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971201, '(The mill\'s flour ledger, its pages stuck at the corners. Every household in the eastern ward that bought Agamand flour, in a miller\'s blunt hand. WHEELWRIGHTS\' ROW: no. 9, ARLENTO, 2 sacks; no. 11, TOLLEY, 1 sack, owes; no. 14, BELTIS, 2 sacks.)', '(The mill\'s flour ledger, its pages stuck at the corners. Every household in the eastern ward that bought Agamand flour, in a miller\'s blunt hand. WHEELWRIGHTS\' ROW: no. 9, ARLENTO, 2 sacks; no. 11, TOLLEY, 1 sack, owes; no. 14, BELTIS, 2 sacks.)', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971202, 'Everyone who comes past stops at the chronicle\'s case. Nobody says anything. I\'ve started writing down how long they stand there. The longest was forty minutes. It was the Executor.', 'Everyone who comes past stops at the chronicle\'s case. Nobody says anything. I\'ve started writing down how long they stand there. The longest was forty minutes. It was the Executor.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971203, 'Shelves! I\'ve arranged them three times. Maela has rearranged them four. We\'re both writing down who\'s winning.', 'Shelves! I\'ve arranged them three times. Maela has rearranged them four. We\'re both writing down who\'s winning.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971204, 'I\'ve a desk now. Well. A table. Under the sky. Tobias says the sky is temporary; I\'ve written down that he said so.', 'I\'ve a desk now. Well. A table. Under the sky. Tobias says the sky is temporary; I\'ve written down that he said so.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971205, '(A thin Forsaken in an ink-stained coat is writing in a notebook, and doesn\'t stop when he looks up.)$B$BOne moment. "Tuesday, the stranger by the old customs office, looks capable." There. Hello.', '(A thin Forsaken in an ink-stained coat is writing in a notebook, and doesn\'t stop when he looks up.)$B$BOne moment. "Tuesday, the stranger by the old customs office, looks capable." There. Hello.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971206, '(Tobias is sewing a spine and doesn\'t look up.)$B$BMaela\'s people come in to read the census. Some of them cry. I keep handkerchiefs in the drawer now. Linen. They\'re the only thing I\'ve bought for myself in ten years.', '(Tobias is sewing a spine and doesn\'t look up.)$B$BMaela\'s people come in to read the census. Some of them cry. I keep handkerchiefs in the drawer now. Linen. They\'re the only thing I\'ve bought for myself in ten years.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971207, '(He speaks so softly you have to lean in.)$B$BTobias. Bookbinder. Pleased. ...Sorry. I\'m not used to people yet. I\'m used to paper.', '(He speaks so softly you have to lean in.)$B$BTobias. Bookbinder. Pleased. ...Sorry. I\'m not used to people yet. I\'m used to paper.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971208, 'People come in now and ask me where they lived. I tell them, $n. Exactly. Some of them argue. I enjoy that very much.', 'People come in now and ask me where they lived. I tell them, $n. Exactly. Some of them argue. I enjoy that very much.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971209, 'Maela Quill. Before you ask: yes, I remember. I remember almost everything. The trouble is that nobody else does, and they will insist.', 'Maela Quill. Before you ask: yes, I remember. I remember almost everything. The trouble is that nobody else does, and they will insist.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (971210, 'Bess Tolley. Number eleven. She threw apples at my cat. Forty years, and she\'s been selling me lamp oil since the autumn. She still won\'t apologise about the cat.', 'Bess Tolley. Number eleven. She threw apples at my cat. Forty years, and she\'s been selling me lamp oil since the autumn. She still won\'t apologise about the cat.', 0.500, 'I take my supper to the general store most evenings. We don\'t eat, either of us. We sit on the step and argue about what the street looked like. She\'s usually right. I don\'t tell her.', 'I take my supper to the general store most evenings. We don\'t eat, either of us. We sit on the step and argue about what the street looked like. She\'s usually right. I don\'t tell her.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971211, 'Tommy Arlento comes by every evening and sits on my step. I don\'t charge him for the oil any more. Don\'t tell anyone; I\'ve a reputation.', 'Tommy Arlento comes by every evening and sits on my step. I don\'t charge him for the oil any more. Don\'t tell anyone; I\'ve a reputation.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971212, 'Thirty-one letters returned to people who\'d forgotten writing them. I wrote the number down. Of course I did.', 'Thirty-one letters returned to people who\'d forgotten writing them. I wrote the number down. Of course I did.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (971213, 'Welcome to the Reclamation Library. Please don\'t eat in the stacks. I know you don\'t eat. Someone tried.', 'Welcome to the Reclamation Library. Please don\'t eat in the stacks. I know you don\'t eat. Someone tried.', 0.333, 'I wrote down everything that happened today. Then I read it back and remembered some of it. That\'s a good day.', 'I wrote down everything that happened today. Then I read it back and remembered some of it. That\'s a good day.', 0.333, 'Nora\'s at the far table again. She comes at opening and stays past dark. I\'ve stopped dimming the lamps.', 'Nora\'s at the far table again. She comes at opening and stays past dark. I\'ve stopped dimming the lamps.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (971214, 'The archive, $n. Everything in it is correct. If you find something that isn\'t, tell me at once. Please. I\'ll be awake.', 'The archive, $n. Everything in it is correct. If you find something that isn\'t, tell me at once. Please. I\'ll be awake.', 0.500, 'Somebody asked me today what number they\'d lived at. I told them. They said they\'d thought it was seventeen. It was twelve. They thanked me. People are thanking me now. I don\'t know what to do with it.', 'Somebody asked me today what number they\'d lived at. I told them. They said they\'d thought it was seventeen. It was twelve. They thanked me. People are thanking me now. I don\'t know what to do with it.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (971215, 'Ink, parchment, a satchel for your papers. And journals, if you\'d like something to put in them.', 'Ink, parchment, a satchel for your papers. And journals, if you\'d like something to put in them.', 0.500, '(Tobias is writing very small in the margin of a ledger. He covers it with his hand when he sees you looking.)', '(Tobias is writing very small in the margin of a ledger. He covers it with his hand when he sees you looking.)', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (971216, '(Nora Bell has a letter open on the table in front of her. She doesn\'t look up.)$B$BIt\'s from my sister. She wrote it the week before. She says the plums are in. I\'d forgotten we had plums.', '(Nora Bell has a letter open on the table in front of her. She doesn\'t look up.)$B$BIt\'s from my sister. She wrote it the week before. She says the plums are in. I\'d forgotten we had plums.', 0.333, 'I thought death had taken everything. Apparently, I hadn\'t checked the library.', 'I thought death had taken everything. Apparently, I hadn\'t checked the library.', 0.333, 'Edmund says I can take the letter home. I don\'t want to. It\'s safer here. I\'m safer here, reading it.', 'Edmund says I can take the letter home. I don\'t want to. It\'s safer here. I\'m safer here, reading it.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (971217, 'Maela says I lived on Chandlers\' Lane. I don\'t remember Chandlers\' Lane. I remember a blue door. She\'s looking for the door.', 'Maela says I lived on Chandlers\' Lane. I don\'t remember Chandlers\' Lane. I remember a blue door. She\'s looking for the door.', 0.500, 'I came to ask where my mother was buried. They didn\'t know yet. They wrote my name down. That\'s something.', 'I came to ask where my mother was buried. They didn\'t know yet. They wrote my name down. That\'s something.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (971218, 'Shh. ...Sorry. Habit. I was a schoolmistress.', 'Shh. ...Sorry. Habit. I was a schoolmistress.', 0.333, 'I\'ve been reading about Brill\'s old fair. I think I went. I think I won a pig.', 'I\'ve been reading about Brill\'s old fair. I think I went. I think I won a pig.', 0.333, 'Maela found my house. It\'s a field now. I\'m going to go and stand in it.', 'Maela found my house. It\'s a field now. I\'m going to go and stand in it.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971219, 'I come to read where it\'s quiet. The library is never quiet now. I wrote that down too, with a little star beside it.', 'I come to read where it\'s quiet. The library is never quiet now. I wrote that down too, with a little star beside it.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971220, 'Every caravan brings something written. Bills, letters, a song somebody wrote on the back of a manifest. Irena lets me copy them before they\'re filed. I think she\'s pleased someone else reads them.', 'Every caravan brings something written. Bills, letters, a song somebody wrote on the back of a manifest. Irena lets me copy them before they\'re filed. I think she\'s pleased someone else reads them.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (971221, 'Books. We\'re building a house for books. In my day we built houses for people. Mind you, in my day we were people.', 'Books. We\'re building a house for books. In my day we built houses for people. Mind you, in my day we were people.', 0.333, 'The quiet one, Wren, brought us tea. None of us can drink it. We held it anyway. It was warm.', 'The quiet one, Wren, brought us tea. None of us can drink it. We held it anyway. It was warm.', 0.333, 'Don\'t stack the oak on the left, the archivist says the left is for archives. I don\'t know what that means.', 'Don\'t stack the oak on the left, the archivist says the left is for archives. I don\'t know what that means.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971222, 'Oswin Thatcher. Jamie Nore keeps sending me to look at other people\'s carpentry. This one\'s sound. The bookbinder checks every joint with a level older than both of us. I like him.', 'Oswin Thatcher. Jamie Nore keeps sending me to look at other people\'s carpentry. This one\'s sound. The bookbinder checks every joint with a level older than both of us. I like him.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (971300, 'Herbs at the front, as you said. Pellen\'s taken to standing among them with his hands behind his back like a general. The flowers sulk in the corners. Flowers are good at corners.', 'Herbs at the front, as you said. Pellen\'s taken to standing among them with his hands behind his back like a general. The flowers sulk in the corners. Flowers are good at corners.', 0.333, 'Johaan\'s sent his apprentice up twice this week for silverleaf. Twice! A garden that\'s useful. My mother would never have believed it.', 'Johaan\'s sent his apprentice up twice this week for silverleaf. Twice! A garden that\'s useful. My mother would never have believed it.', 0.333, 'Come and sit, dear. The herbs don\'t mind being looked at. They just don\'t care if you do.', 'Come and sit, dear. The herbs don\'t mind being looked at. They just don\'t care if you do.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (971301, 'Flowers at the front, as you said. People stop at the gate just to look. Some of them come in. One of them cried, last Tuesday. Don\'t tell her I told you.', 'Flowers at the front, as you said. People stop at the gate just to look. Some of them come in. One of them cried, last Tuesday. Don\'t tell her I told you.', 0.333, 'Pellen\'s herbs are at the back, where the light\'s better for them anyway, which is what I told him the reason was. Don\'t contradict me.', 'Pellen\'s herbs are at the back, where the light\'s better for them anyway, which is what I told him the reason was. Don\'t contradict me.', 0.333, 'Come and sit, dear. The asters are out. They mean patience. Or possibly afterthought. I forget which.', 'Come and sit, dear. The asters are out. They mean patience. Or possibly afterthought. I forget which.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971302, 'Willa planted three more forget-me-nots this morning without being asked. I didn\'t say a word. I went behind the frame and had a little sit-down.', 'Willa planted three more forget-me-nots this morning without being asked. I didn\'t say a word. I went behind the frame and had a little sit-down.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971303, 'Willa\'s been watering the beds twice a day and telling me it\'s pointless twice a day. I\'ve given her something to think about. Or rather, I\'ve given you something to give her.', 'Willa\'s been watering the beds twice a day and telling me it\'s pointless twice a day. I\'ve given her something to think about. Or rather, I\'ve given you something to give her.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971304, 'Gravebloom, dear. Pale as candles and twice as stubborn. If they make it through the week, we\'ll have a garden.', 'Gravebloom, dear. Pale as candles and twice as stubborn. If they make it through the week, we\'ll have a garden.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971305, 'Rudd Carver\'s lads have put the fence up. It leans. Everything in Brill leans. I\'ve decided it\'s a style.', 'Rudd Carver\'s lads have put the fence up. It leans. Everything in Brill leans. I\'ve decided it\'s a style.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971306, 'Edda Graves, dear. Florist, once. I\'m going to make a garden here, if the weeds and Odo will let me.', 'Edda Graves, dear. Florist, once. I\'m going to make a garden here, if the weeds and Odo will let me.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971307, 'Necrotic loam, treated with lime and bone. I\'ve written it up. Nobody will read it, but it\'s written.', 'Necrotic loam, treated with lime and bone. I\'ve written it up. Nobody will read it, but it\'s written.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971308, 'The gravebloom has turned its back on the sun. Entirely as predicted. I find that very restful.', 'The gravebloom has turned its back on the sun. Entirely as predicted. I find that very restful.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971309, 'Acid, grave-rich, and full of fungal thread. I\'ve seen worse soil. I\'ve been buried in worse soil.', 'Acid, grave-rich, and full of fungal thread. I\'ve seen worse soil. I\'ve been buried in worse soil.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971310, 'Pellen Moss. Don\'t touch that. Or that. That one you may touch, but you\'ll regret it.', 'Pellen Moss. Don\'t touch that. Or that. That one you may touch, but you\'ll regret it.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971311, 'Peacebloom, silverleaf, earthroot, mageroyal, and bruiseweed for those who know what to do with it. The herbs have the front beds now. I may have said \'adequate\' again. I meant it more.', 'Peacebloom, silverleaf, earthroot, mageroyal, and bruiseweed for those who know what to do with it. The herbs have the front beds now. I may have said \'adequate\' again. I meant it more.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971312, 'Herbs, and a few flowers, since Edda insists people want to buy things that do nothing. Apparently they do. I\'ve stopped arguing. I\'ve started charging.', 'Herbs, and a few flowers, since Edda insists people want to buy things that do nothing. Apparently they do. I\'ve stopped arguing. I\'ve started charging.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971313, 'Ask them what flowers they remember. Then come back and tell me. I\'ll pretend not to be interested.', 'Ask them what flowers they remember. Then come back and tell me. I\'ll pretend not to be interested.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971314, 'Willa Fen. I water things. They grow. I still don\'t see what for, but I\'m told that\'s the beginning of gardening.', 'Willa Fen. I water things. They grow. I still don\'t see what for, but I\'m told that\'s the beginning of gardening.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (971315, 'Forget-me-nots by the gate, now. I picked the spot. Don\'t tell Edda; she\'ll be smug about it.', 'Forget-me-nots by the gate, now. I picked the spot. Don\'t tell Edda; she\'ll be smug about it.', 0.333, 'I still can\'t smell them. I know which is which, though. I\'ve learned them all. Edda says that\'s better than smelling. She\'s lying, but it\'s kind of her.', 'I still can\'t smell them. I know which is which, though. I\'ve learned them all. Edda says that\'s better than smelling. She\'s lying, but it\'s kind of her.', 0.333, 'Water in the morning, never at noon. The leaves scald. I didn\'t know a dead woman could worry about leaves scalding.', 'Water in the morning, never at noon. The leaves scald. I didn\'t know a dead woman could worry about leaves scalding.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971316, 'I sit with the lily of an evening. I don\'t know why. It doesn\'t smell of anything, to me. But somebody planted a lily for every one of us that nobody\'s waiting for, and I like to keep it company.', 'I sit with the lily of an evening. I don\'t know why. It doesn\'t smell of anything, to me. But somebody planted a lily for every one of us that nobody\'s waiting for, and I like to keep it company.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971317, 'I\'ve told the gravebloom who everyone is. That one there doesn\'t like Pellen. I don\'t blame it.', 'I\'ve told the gravebloom who everyone is. That one there doesn\'t like Pellen. I don\'t blame it.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (971318, 'Odo. Groundskeeper. Holt hired me forty years ago and nobody\'s told me to stop. So I haven\'t.', 'Odo. Groundskeeper. Holt hired me forty years ago and nobody\'s told me to stop. So I haven\'t.', 0.500, 'Don\'t mind me. I\'m just telling the apple stumps it\'s going to be all right. It isn\'t, for them. But you say these things.', 'Don\'t mind me. I\'m just telling the apple stumps it\'s going to be all right. It isn\'t, for them. But you say these things.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971319, 'Your big dog slept under the east bench all yesterday afternoon. I told the asters he was a friend. They were very good about it.', 'Your big dog slept under the east bench all yesterday afternoon. I told the asters he was a friend. They were very good about it.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (971320, 'Shh. The silverleaf\'s asleep. ...No, I\'m joking. Mostly.', 'Shh. The silverleaf\'s asleep. ...No, I\'m joking. Mostly.', 0.333, 'Forty years I kept Holt\'s apples. Now it\'s gravebloom. Gravebloom listens better. Apples just want to fall on you.', 'Forty years I kept Holt\'s apples. Now it\'s gravebloom. Gravebloom listens better. Apples just want to fall on you.', 0.333, 'Edda says I\'m a watchman. I watch. Mostly I watch the plants. Somebody ought to.', 'Edda says I\'m a watchman. I watch. Mostly I watch the plants. Somebody ought to.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971321, 'Evening. Or morning, by your lot\'s reckoning. I keep the lantern lit so the plants know where the gate is. Some of them wander.', 'Evening. Or morning, by your lot\'s reckoning. I keep the lantern lit so the plants know where the gate is. Some of them wander.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (971322, 'Fence posts. A garden needs a fence, the old lady says, so the flowers know where they\'re allowed.', 'Fence posts. A garden needs a fence, the old lady says, so the flowers know where they\'re allowed.', 0.333, 'Rudd says plant it straight. The ground says otherwise. The ground usually wins round here.', 'Rudd says plant it straight. The ground says otherwise. The ground usually wins round here.', 0.333, 'That old watchman keeps telling the rubble our names. I don\'t like it knowing my name.', 'That old watchman keeps telling the rubble our names. I don\'t like it knowing my name.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971323, 'Oswin Thatcher. Jamie Nore lends me out like a ladder. Your house is holding up; I looked in on it on the way. This fence won\'t, if those lads keep setting posts in wet ground.', 'Oswin Thatcher. Jamie Nore lends me out like a ladder. Your house is holding up; I looked in on it on the way. This fence won\'t, if those lads keep setting posts in wet ground.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`, `text3_0`, `text3_1`, `Probability3`) VALUES (971324, 'I come up here after the inn closes its doors for the night. It\'s quiet. That\'s all. That\'s enough.', 'I come up here after the inn closes its doors for the night. It\'s quiet. That\'s all. That\'s enough.', 0.250, 'My wife grew lavender. I can\'t smell this lot, but I know it\'s lavender. That\'s something, isn\'t it?', 'My wife grew lavender. I can\'t smell this lot, but I know it\'s lavender. That\'s something, isn\'t it?', 0.250, 'The lady with the flowers asked me what I remembered. I said nothing. Then I sat here an hour and remembered a hedge.', 'The lady with the flowers asked me what I remembered. I said nothing. Then I sat here an hour and remembered a hedge.', 0.250, 'Don\'t sit on that end. Odo says the bench is haunted. It\'s not. It\'s just Odo, at night.', 'Don\'t sit on that end. Odo says the bench is haunted. It\'s not. It\'s just Odo, at night.', 0.250);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971325, 'You\'re up early. I didn\'t want to wake you. I only came for nightshade, and a little gravebloom, and I\'ll be home before the kettle\'s cold. I\'m always home before the kettle\'s cold.', 'You\'re up early. I didn\'t want to wake you. I only came for nightshade, and a little gravebloom, and I\'ll be home before the kettle\'s cold. I\'m always home before the kettle\'s cold.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971326, 'There you are. I knew you\'d come by; you always take the long way round on a market day. Hold the basket for me. No, closer.', 'There you are. I knew you\'d come by; you always take the long way round on a market day. Hold the basket for me. No, closer.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971327, 'Hello, friend. Edda lets me take what I need if I weed for it. I weed very thoroughly. Nothing grows here that I haven\'t approved of.', 'Hello, friend. Edda lets me take what I need if I weed for it. I weed very thoroughly. Nothing grows here that I haven\'t approved of.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971328, 'Carolai Anise. I have an arrangement with Edda: I weed, and she doesn\'t ask what the nightshade is for. It\'s for tonics. Mostly.', 'Carolai Anise. I have an arrangement with Edda: I weed, and she doesn\'t ask what the nightshade is for. It\'s for tonics. Mostly.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971400, '(\'PROPOSAL: the use of the Surgeon\'s Hall\'s patients, being already in a state of decay, in the trial of Formulae 12 through 31 for the arrest of necrotic progression. Patients shall be informed as necessary.\'$B$BUnder Master Apothecary Faranell\'s seal. AS NECESSARY is underlined in red ink, three times.)', '(\'PROPOSAL: the use of the Surgeon\'s Hall\'s patients, being already in a state of decay, in the trial of Formulae 12 through 31 for the arrest of necrotic progression. Patients shall be informed as necessary.\'$B$BUnder Master Apothecary Faranell\'s seal. AS NECESSARY is underlined in red ink, three times.)', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971401, '(Forty-one numbered folders. Under each: CONSENTED. Two say REFUSED, and under that, TREATED OTHERWISE. One says DIED (AGAIN). ATTENDED.)', '(Forty-one numbered folders. Under each: CONSENTED. Two say REFUSED, and under that, TREATED OTHERWISE. One says DIED (AGAIN). ATTENDED.)', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971402, 'The Society has young Crane\'s notes now, I hear. Johaan\'s apprentice. I read a copy. Half of it is genius and half of it is a crime, and the Society will keep the wrong half. Mind the step.', 'The Society has young Crane\'s notes now, I hear. Johaan\'s apprentice. I read a copy. Half of it is genius and half of it is a crime, and the Society will keep the wrong half. Mind the step.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971403, 'Johaan lets his apprentice go on brewing that \'Stay\' of his, under supervision. I\'ve asked to see the notes. I\'ve asked to see the subjects. So far I have seen neither. Supervision is a word, $n. I prefer a register.', 'Johaan lets his apprentice go on brewing that \'Stay\' of his, under supervision. I\'ve asked to see the notes. I\'ve asked to see the subjects. So far I have seen neither. Supervision is a word, $n. I prefer a register.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971404, 'Johaan burned his apprentice\'s work, I\'m told. A tincture to slow the rot. I don\'t know whether to thank him or weep. Probably neither. There\'s a patient waiting.', 'Johaan burned his apprentice\'s work, I\'m told. A tincture to slow the rot. I don\'t know whether to thank him or weep. Probably neither. There\'s a patient waiting.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (971405, 'The hall\'s open, the charter\'s on the door, and not one apothecary has set foot past it. I\'d call that a good week.', 'The hall\'s open, the charter\'s on the door, and not one apothecary has set foot past it. I\'d call that a good week.', 0.333, 'Agnes walked to the square and back this morning. Twice. I didn\'t watch. Fenwick watched. I watched Fenwick.', 'Agnes walked to the square and back this morning. Twice. I didn\'t watch. Fenwick watched. I watched Fenwick.', 0.333, 'If you\'re bleeding, come in. If you\'re selling something, the Society\'s office is in the Undercity.', 'If you\'re bleeding, come in. If you\'re selling something, the Society\'s office is in the Undercity.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (971406, 'The Society\'s man comes of a morning with his little bottles, and signs the register in front of the patient, and I stand at the foot of the bed. So far he has been very polite. They\'re always very polite.', 'The Society\'s man comes of a morning with his little bottles, and signs the register in front of the patient, and I stand at the foot of the bed. So far he has been very polite. They\'re always very polite.', 0.333, 'Two patients volunteered for the Society\'s trials. One withdrew on the second day, and the apothecary thanked him for his time. I made sure of the thanking.', 'Two patients volunteered for the Society\'s trials. One withdrew on the second day, and the apothecary thanked him for his time. I made sure of the thanking.', 0.333, 'Agnes walked to the square and back this morning. Twice. I didn\'t watch. Fenwick watched. I watched Fenwick.', 'Agnes walked to the square and back this morning. Twice. I didn\'t watch. Fenwick watched. I watched Fenwick.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971407, 'Table, Fenwick, Timm, me. In that order. Agnes is counting on all of us, and I\'m counting on you to keep up.', 'Table, Fenwick, Timm, me. In that order. Agnes is counting on all of us, and I\'m counting on you to keep up.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971408, 'The charter\'s on the door, and there\'s a woman coming up the Hillsbrad road on a leg that needs more than a charter. Are you ready, $n? Say yes. I haven\'t time for the other answer.', 'The charter\'s on the door, and there\'s a woman coming up the Hillsbrad road on a leg that needs more than a charter. Are you ready, $n? Say yes. I haven\'t time for the other answer.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971409, 'Timm\'s arm works. I told him so. I didn\'t tell him I came back to the yard at midnight to watch it pick up a teacup. Don\'t you tell him either.', 'Timm\'s arm works. I told him so. I didn\'t tell him I came back to the yard at midnight to watch it pick up a teacup. Don\'t you tell him either.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971410, 'Tables, cabinets, lamps. It\'s beginning to look like a place where a person might get better, instead of a place where a person waits to stop.', 'Tables, cabinets, lamps. It\'s beginning to look like a place where a person might get better, instead of a place where a person waits to stop.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971411, 'A tent and three cots. Lordaeron\'s finest physicians would weep. I did, a little, in the privacy of my own head.', 'A tent and three cots. Lordaeron\'s finest physicians would weep. I did, a little, in the privacy of my own head.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971412, 'If you\'re bleeding, wait your turn. If you\'re not, make yourself useful or make yourself scarce.', 'If you\'re bleeding, wait your turn. If you\'re not, make yourself useful or make yourself scarce.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971413, 'Gerald\'s on the bench. The arm. I\'ve named it Gerald. Don\'t laugh. It only twitches when it\'s cold, and it\'s always cold.', 'Gerald\'s on the bench. The arm. I\'ve named it Gerald. Don\'t laugh. It only twitches when it\'s cold, and it\'s always cold.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971414, 'Timm Vetch, apprentice. That\'s the sleeve everyone stares at. Go on, ask. Everyone asks.', 'Timm Vetch, apprentice. That\'s the sleeve everyone stares at. Go on, ask. Everyone asks.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971415, 'Timm Vetch. Apprentice surgeon. One day just surgeon. One day, Elspeth says, if I stop fidgeting.', 'Timm Vetch. Apprentice surgeon. One day just surgeon. One day, Elspeth says, if I stop fidgeting.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (971416, 'Design five. Springs in every finger, no more twitching. ...It twitched. Design six, then.', 'Design five. Springs in every finger, no more twitching. ...It twitched. Design six, then.', 0.333, 'A Deathguard came in yesterday wanting a hook. A hook! I made him a hand. He cried. I think he cried. Hard to tell with us.', 'A Deathguard came in yesterday wanting a hook. A hook! I made him a hand. He cried. I think he cried. Hard to tell with us.', 0.333, 'Elspeth lets me do the stitching now. Only the straight bits. I do very straight bits.', 'Elspeth lets me do the stitching now. Only the straight bits. I do very straight bits.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971417, 'Six brass springs, two dozen screws and a box of watch gears from Gilneas, which won\'t sell to us, so from whoever\'s buying from Gilneas. The Quartermaster wants it in triplicate. I\'ve only the one hand that writes.', 'Six brass springs, two dozen screws and a box of watch gears from Gilneas, which won\'t sell to us, so from whoever\'s buying from Gilneas. The Quartermaster wants it in triplicate. I\'ve only the one hand that writes.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971418, 'Fenwick Pike. Hold still, I\'m looking at your seams. ...You\'re fine. You\'d be amazed how many aren\'t.', 'Fenwick Pike. Hold still, I\'m looking at your seams. ...You\'re fine. You\'d be amazed how many aren\'t.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971419, 'Bandages, salves, a little something for the complexion. Gray dye sells best; nobody wants to look fresh. And the Society\'s tonics, for those who\'ve signed for them. Ask Elspeth first. Everyone asks Elspeth first.', 'Bandages, salves, a little something for the complexion. Gray dye sells best; nobody wants to look fresh. And the Society\'s tonics, for those who\'ve signed for them. Ask Elspeth first. Everyone asks Elspeth first.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971420, 'Bandages, salves, a little something for the complexion. Gray dye sells best; nobody round here wants to look fresh. And if you\'d like to learn to tie a proper bandage, I teach. Elspeth says I\'m patient. I\'ve had practice.', 'Bandages, salves, a little something for the complexion. Gray dye sells best; nobody round here wants to look fresh. And if you\'d like to learn to tie a proper bandage, I teach. Elspeth says I\'m patient. I\'ve had practice.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971421, 'Jory Haskett. Carter. Or I was, before the horse decided it had better things to do than be eaten.', 'Jory Haskett. Carter. Or I was, before the horse decided it had better things to do than be eaten.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971422, 'Don\'t mind me, dear. I\'m only lying here being brave. It\'s harder than it looks.', 'Don\'t mind me, dear. I\'m only lying here being brave. It\'s harder than it looks.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971423, 'I\'m... I\'m fine. I\'m a Deathguard. Recruit. We\'re supposed to be fine. Is it normal, that I can\'t feel the other fingers either?', 'I\'m... I\'m fine. I\'m a Deathguard. Recruit. We\'re supposed to be fine. Is it normal, that I can\'t feel the other fingers either?', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971424, 'Agnes Morrow. Traveller, until my leg had other ideas. If you\'re the help, help. If you\'re the surgeon, I\'m ready. If you\'re a priest, go away.', 'Agnes Morrow. Traveller, until my leg had other ideas. If you\'re the help, help. If you\'re the surgeon, I\'m ready. If you\'re a priest, go away.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (971425, 'Round the yard, twice. Rane says three times by the end of the week. I say four. We\'ll see who\'s dead first. Ha.', 'Round the yard, twice. Rane says three times by the end of the week. I say four. We\'ll see who\'s dead first. Ha.', 0.333, 'The brace creaks when I\'m going uphill. Timm says that\'s a feature. Timm says a lot of things are features.', 'The brace creaks when I\'m going uphill. Timm says that\'s a feature. Timm says a lot of things are features.', 0.333, 'I keep meaning to leave. The road\'s right there. But then someone new comes up it on a stretcher, and I sit with them till Rane\'s ready, because somebody sat with me.', 'I keep meaning to leave. The road\'s right there. But then someone new comes up it on a stretcher, and I sit with them till Rane\'s ready, because somebody sat with me.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971426, 'I walk to the square of an evening and read the Board. Then I walk back. That\'s all. Nine days I couldn\'t. I like to read the Board.', 'I walk to the square of an evening and read the Board. Then I walk back. That\'s all. Nine days I couldn\'t. I like to read the Board.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`, `text3_0`, `text3_1`, `Probability3`) VALUES (971427, 'The surgeon says I\'ll keep the hand. I didn\'t know that was in question. Nobody tells you anything.', 'The surgeon says I\'ll keep the hand. I didn\'t know that was in question. Nobody tells you anything.', 0.250, 'I came in for a stitch and she found three more things. She always finds three more things.', 'I came in for a stitch and she found three more things. She always finds three more things.', 0.250, 'Ghoul bite. From before. It\'s been bothering me for six years and I finally came in. Don\'t tell my wife.', 'Ghoul bite. From before. It\'s been bothering me for six years and I finally came in. Don\'t tell my wife.', 0.250, 'The orderly sings while he stitches. Badly. It helps, somehow.', 'The orderly sings while he stitches. Badly. It helps, somehow.', 0.250);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (971428, 'Can\'t sleep. Well. I never sleep. Can\'t lie still, I mean. Neither can the leg.', 'Can\'t sleep. Well. I never sleep. Can\'t lie still, I mean. Neither can the leg.', 0.333, 'The lad with the brass arm came by at midnight to check my splint. I think he doesn\'t sleep either.', 'The lad with the brass arm came by at midnight to check my splint. I think he doesn\'t sleep either.', 0.333, 'Quiet in here at night. The surgeon sits by the door with a lamp and a book. She doesn\'t turn the pages. She\'s listening.', 'Quiet in here at night. The surgeon sits by the door with a lamp and a book. She doesn\'t turn the pages. She\'s listening.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971429, 'Apothecary Crell, Royal Apothecary Society. I have three volunteers and a register that must be countersigned by the surgeon in triplicate. I\'ve grown rather fond of triplicate. It\'s the only thing here that\'s fond of me.', 'Apothecary Crell, Royal Apothecary Society. I have three volunteers and a register that must be countersigned by the surgeon in triplicate. I\'ve grown rather fond of triplicate. It\'s the only thing here that\'s fond of me.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971430, 'Apothecary Crell, Royal Apothecary Society. I\'m not here to conduct research. The charter forbids it. I\'m here to read the charter. Every morning. In case it\'s changed.', 'Apothecary Crell, Royal Apothecary Society. I\'m not here to conduct research. The charter forbids it. I\'m here to read the charter. Every morning. In case it\'s changed.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (971431, 'Roof\'s good. Floor\'s good. Walls are good. Surgeon still found eleven things wrong with it.', 'Roof\'s good. Floor\'s good. Walls are good. Surgeon still found eleven things wrong with it.', 0.333, 'Working next to a graveyard. Rudd says it\'s quiet. It\'s not quiet. It\'s just not loud yet.', 'Working next to a graveyard. Rudd says it\'s quiet. It\'s not quiet. It\'s just not loud yet.', 0.333, 'Don\'t go in the tent. The orderly sings.', 'Don\'t go in the tent. The orderly sings.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971432, 'Oswin Thatcher. Rudd borrowed me. The surgeon wants the doorway wide enough for a stretcher and a ghoul side by side. I asked her why a ghoul. She said \'experience.\'', 'Oswin Thatcher. Rudd borrowed me. The surgeon wants the doorway wide enough for a stretcher and a ghoul side by side. I asked her why a ghoul. She said \'experience.\'', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971433, 'Willowbark and comfrey for the surgeon. I\'ll be home in a moment; I only have to watch her check every bottle. She checks every bottle. I like that in a woman. Not too much.', 'Willowbark and comfrey for the surgeon. I\'ll be home in a moment; I only have to watch her check every bottle. She checks every bottle. I like that in a woman. Not too much.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971434, 'There you are. If you\'re hurt, my love, you come to me first. Not her. Me. I\'ll know what to do. I\'ve been practising.', 'There you are. If you\'re hurt, my love, you come to me first. Not her. Me. I\'ll know what to do. I\'ve been practising.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971435, 'Hello, friend. I bring the surgeon a basket every evening. She reads every label before she asks what\'s in it. Nobody in Brill has ever read my labels first.', 'Hello, friend. I bring the surgeon a basket every evening. She reads every label before she asks what\'s in it. Nobody in Brill has ever read my labels first.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971436, 'Carolai Anise. Herbal preparations for the surgeon: comfrey, willowbark, a sleeping draught. She won\'t let Johaan near her patients. She lets me. I\'ve decided not to find that suspicious.', 'Carolai Anise. Herbal preparations for the surgeon: comfrey, willowbark, a sleeping draught. She won\'t let Johaan near her patients. She lets me. I\'ve decided not to find that suspicious.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971500, '(A bill of lading for Hamlin Atkins\'s seed, torn off its pad.)', '(A bill of lading for Hamlin Atkins\'s seed, torn off its pad.)', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971501, 'The Exchange fined Price a year\'s profit and struck his license. He\'s working it off at a copper a crate, under my eye. He says good morning to me every morning. I say it back. Neither of us means it.', 'The Exchange fined Price a year\'s profit and struck his license. He\'s working it off at a copper a crate, under my eye. He says good morning to me every morning. I say it back. Neither of us means it.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971502, 'Price brought me his first payment this morning, on time, counted twice, in a little bag with a ribbon on it. I\'ve entered the payment. I\'ve also entered the ribbon. Everything goes in the book, $n.', 'Price brought me his first payment this morning, on time, counted twice, in a little bag with a ribbon on it. I\'ve entered the payment. I\'ve also entered the ribbon. Everything goes in the book, $n.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971503, 'Name, cargo, purpose. ...Oh, it\'s you. Good. You\'re the only person in Brill who doesn\'t make me fill in a form about them.', 'Name, cargo, purpose. ...Oh, it\'s you. Good. You\'re the only person in Brill who doesn\'t make me fill in a form about them.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971504, 'Name, cargo, destination. ...You\'re not a delivery. Pity. I was hoping for a delivery. I\'ve had none that arrived where they were going since I got here.', 'Name, cargo, destination. ...You\'re not a delivery. Pity. I was hoping for a delivery. I\'ve had none that arrived where they were going since I got here.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971505, 'Blackbarrel was in again about the carriage on his barley. I explained the tariff. He explained his father. We were both very thorough. He\'ll be back tomorrow; I\'ve already filled in his form.', 'Blackbarrel was in again about the carriage on his barley. I explained the tariff. He explained his father. We were both very thorough. He\'ll be back tomorrow; I\'ve already filled in his form.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (971506, 'Price paid his weekly fine in coppers, every one of them face up. I believe that\'s his idea of an insult. I\'ve counted them. It took a while. That\'s my idea of one.', 'Price paid his weekly fine in coppers, every one of them face up. I believe that\'s his idea of an insult. I\'ve counted them. It took a while. That\'s my idea of one.', 0.500, 'Forty-two shipments since the office opened, three lost, one stolen and recovered, none unaccounted for. The Exchange has asked me to write a report on how it\'s done. It will be very long.', 'Forty-two shipments since the office opened, three lost, one stolen and recovered, none unaccounted for. The Exchange has asked me to write a report on how it\'s done. It will be very long.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (971507, 'Price\'s books are clean this week. Too clean. I\'ll go through them again. He\'d be disappointed if I didn\'t.', 'Price\'s books are clean this week. Too clean. I\'ll go through them again. He\'d be disappointed if I didn\'t.', 0.500, 'Forty-two shipments since the office opened, three lost, one stolen and recovered, none unaccounted for. The Exchange has asked me to write a report on how it\'s done. It will be very long.', 'Forty-two shipments since the office opened, three lost, one stolen and recovered, none unaccounted for. The Exchange has asked me to write a report on how it\'s done. It will be very long.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971508, 'Brill Caravan Office. Arrivals, departures, losses, complaints. Mostly complaints. I find them very soothing.', 'Brill Caravan Office. Arrivals, departures, losses, complaints. Mostly complaints. I find them very soothing.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971509, 'First wagon\'s greased and waiting. I\'ve walked round it eleven times. Don\'t count. I\'m not counting.', 'First wagon\'s greased and waiting. I\'ve walked round it eleven times. Don\'t count. I\'m not counting.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971510, 'Platform\'s held three loads and a Deathguard who fell off the roof. Best thing I ever helped build. Don\'t tell Irena I said \'best\'. She\'ll want it in writing.', 'Platform\'s held three loads and a Deathguard who fell off the roof. Best thing I ever helped build. Don\'t tell Irena I said \'best\'. She\'ll want it in writing.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971511, 'Dren Hollow. Wagon\'s mine, horse is mine, the road belongs to whoever\'s got the biggest stick on it. Today that\'s nobody. Make the most of it.', 'Dren Hollow. Wagon\'s mine, horse is mine, the road belongs to whoever\'s got the biggest stick on it. Today that\'s nobody. Make the most of it.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (971512, 'Every morning: wheels, axles, harness, then the horse, then me. The horse complains less.', 'Every morning: wheels, axles, harness, then the horse, then me. The horse complains less.', 0.333, 'Grease, $n. Everyone thinks a road\'s about horses. It\'s about grease.', 'Grease, $n. Everyone thinks a road\'s about horses. It\'s about grease.', 0.333, 'Undercity wagon\'s due at the tenth bell. It\'s always late. I like that about it; it\'s reliable.', 'Undercity wagon\'s due at the tenth bell. It\'s always late. I like that about it; it\'s reliable.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (971513, 'Mind the winch. It\'s kinder than Rudd\'s, but it doesn\'t know you.', 'Mind the winch. It\'s kinder than Rudd\'s, but it doesn\'t know you.', 0.500, 'Sixty crates this week and not one in the ditch. I\'d say I\'d retire, but I\'d only go and drive somewhere.', 'Sixty crates this week and not one in the ditch. I\'d say I\'d retire, but I\'d only go and drive somewhere.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (971514, 'Marta lets me sit here if I don\'t drink at her. I don\'t drink. I sit. It\'s nice.', 'Marta lets me sit here if I don\'t drink at her. I don\'t drink. I sit. It\'s nice.', 0.500, 'Evening. Silverpine\'s come in. Fish, timber and worry. Same as ever.', 'Evening. Silverpine\'s come in. Fish, timber and worry. Same as ever.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (971515, 'Can\'t sleep. Never could, even before. I watch the wagons. The wagons watch the road.', 'Can\'t sleep. Never could, even before. I watch the wagons. The wagons watch the road.', 0.500, 'Night, $n. Garth\'s on the gate, I\'m on the brazier. Between us, nothing gets through but the fog.', 'Night, $n. Garth\'s on the gate, I\'m on the brazier. Between us, nothing gets through but the fog.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971516, 'Selwyn Price, licensed by nobody, fined by everybody. (He smiles, a little too widely.) I\'m still buying, $n. Irena takes her share first. I\'d do the same, in her place. I very nearly did, in mine.', 'Selwyn Price, licensed by nobody, fined by everybody. (He smiles, a little too widely.) I\'m still buying, $n. Irena takes her share first. I\'d do the same, in her place. I very nearly did, in mine.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971517, '(Selwyn drops his voice.) Two payments made. Eleven to go. I\'ve never paid anybody back before, $n. It\'s a very strange feeling. Rather like being sober.', '(Selwyn drops his voice.) Two payments made. Eleven to go. I\'ve never paid anybody back before, $n. It\'s a very strange feeling. Rather like being sober.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971518, 'Oh, it\'s you! Off to the hills? Terrible business. Terrible. Bandits. (He laughs, and stops.) Do mind yourself up there.', 'Oh, it\'s you! Off to the hills? Terrible business. Terrible. Bandits. (He laughs, and stops.) Do mind yourself up there.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (971519, 'Selwyn Price, buyer of anything, seller of everything else! Tell the quartermaster I\'ve waived her fee for listening to me. She might return the favor.', 'Selwyn Price, buyer of anything, seller of everything else! Tell the quartermaster I\'ve waived her fee for listening to me. She might return the favor.', 0.333, 'Buying! Bones, buttons, bits of armor, the occasional heirloom. Selling! Mostly the same, at a modest markup.', 'Buying! Bones, buttons, bits of armor, the occasional heirloom. Selling! Mostly the same, at a modest markup.', 0.333, 'Irena says there\'s a form for being a merchant. I\'ve asked for the form for not filling in forms. She says she\'s looking into it. I think we\'re becoming friends.', 'Irena says there\'s a form for being a merchant. I\'ve asked for the form for not filling in forms. She says she\'s looking into it. I think we\'re becoming friends.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971520, 'Buying! Selling! Being audited! Step up, $n, it\'s all very fair now. Painfully fair.', 'Buying! Selling! Being audited! Step up, $n, it\'s all very fair now. Painfully fair.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971521, 'Down to nine payments. Irena smiled at me yesterday. At least, her face moved. I\'m taking it as a smile.', 'Down to nine payments. Irena smiled at me yesterday. At least, her face moved. I\'m taking it as a smile.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971522, 'Selwyn Price, buyer of anything! The Undercity wagon\'s brought me a crate of mystery. I haven\'t opened it. Mystery sells better shut.', 'Selwyn Price, buyer of anything! The Undercity wagon\'s brought me a crate of mystery. I haven\'t opened it. Mystery sells better shut.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (971523, 'Evening, $n. I\'m not selling anything. I\'m sitting. Renee says it\'s restful. I\'m told I\'ll get the hang of it.', 'Evening, $n. I\'m not selling anything. I\'m sitting. Renee says it\'s restful. I\'m told I\'ll get the hang of it.', 0.500, '(Selwyn is turning a copper over his knuckles.) One more payment on the debt this week, and nobody had to hold a wagon up for it. Imagine that.', '(Selwyn is turning a copper over his knuckles.) One more payment on the debt this week, and nobody had to hold a wagon up for it. Imagine that.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971524, 'Waiting. Been waiting since the third bell. Before that, I was waiting since the second.', 'Waiting. Been waiting since the third bell. Before that, I was waiting since the second.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971525, 'If you\'re from the builder\'s yard, I\'ve your nails. If you\'re not, I\'ve still got your nails. Nobody wants nails until they need them.', 'If you\'re from the builder\'s yard, I\'ve your nails. If you\'re not, I\'ve still got your nails. Nobody wants nails until they need them.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971526, '(Jory is checking the ropes on his wagon, and then checking them again.) Hello. Sorry. Hello.', '(Jory is checking the ropes on his wagon, and then checking them again.) Hello. Sorry. Hello.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971527, 'Brill\'s wagon arrives on the day, at the hour, with the seal unbroken. I find it unsettling. Give Sable my regards. Tell her to stop writing to me.', 'Brill\'s wagon arrives on the day, at the hour, with the seal unbroken. I find it unsettling. Give Sable my regards. Tell her to stop writing to me.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971528, 'The Merchants\' Exchange. Tariffs, licenses, disputes and condolences. Mostly disputes. Condolences are extra.', 'The Merchants\' Exchange. Tariffs, licenses, disputes and condolences. Mostly disputes. Condolences are extra.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971529, 'Lucan Ashgrove, for the Sepulcher. Fish, timber and bad news, $g sir:madam;, all at very reasonable prices.', 'Lucan Ashgrove, for the Sepulcher. Fish, timber and bad news, $g sir:madam;, all at very reasonable prices.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971530, 'Brill\'s wagons go by twice a week now, crooked B on the tailboard. I sign them through. Best part of my day, and I\'ve a very long day.', 'Brill\'s wagons go by twice a week now, crooked B on the tailboard. I sign them through. Best part of my day, and I\'ve a very long day.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971531, 'Crossroads. Brill north, the Undercity south and west, Silverpine beyond. Sign in, move on, mind the wolves.', 'Crossroads. Brill north, the Undercity south and west, Silverpine beyond. Sign in, move on, mind the wolves.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971532, 'Heard you found the lamplighter out. Two of ours died on the east road and he lit the lamp they walked under. I change the hour of every wagon twice now, and I tell nobody. Not even Irena. Especially not Irena; she\'d write it down.', 'Heard you found the lamplighter out. Two of ours died on the east road and he lit the lamp they walked under. I change the hour of every wagon twice now, and I tell nobody. Not even Irena. Especially not Irena; she\'d write it down.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971533, 'Marsh still lights the lamps. Executor\'s orders: nobody tells him the caravan hours, and he doesn\'t ask. Suits me. A man who doesn\'t ask is a man who\'s learned something.', 'Marsh still lights the lamps. Executor\'s orders: nobody tells him the caravan hours, and he doesn\'t ask. Suits me. A man who doesn\'t ask is a man who\'s learned something.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971534, 'Lamplighter went west one night and nobody\'s lit the north road since. A wagon in the dark is a wagon nobody can count. I\'m not sorry. I\'m not glad. I\'m on duty.', 'Lamplighter went west one night and nobody\'s lit the north road since. A wagon in the dark is a wagon nobody can count. I\'m not sorry. I\'m not glad. I\'m on duty.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971535, 'Garth Molt. Caravan escort, by order of the Executor. I go where the wagon goes and I come back when it does. That\'s the whole of it.', 'Garth Molt. Caravan escort, by order of the Executor. I go where the wagon goes and I come back when it does. That\'s the whole of it.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971536, 'Before I signed on, I asked Irena one thing: who knows the caravan hours? She showed me the list. It\'s short. After that business with the lamplighter, short is how I like it.', 'Before I signed on, I asked Irena one thing: who knows the caravan hours? She showed me the list. It\'s short. After that business with the lamplighter, short is how I like it.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971537, 'Bastian Coyle, caravan guard. Still getting used to the \'guard\' part. The \'caravan\' part I\'m told I\'ll get used to when I\'ve walked behind one for a year.', 'Bastian Coyle, caravan guard. Still getting used to the \'guard\' part. The \'caravan\' part I\'m told I\'ll get used to when I\'ve walked behind one for a year.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971538, 'Brill sent its first wagon to us, I hear. The Exchange talked of nothing else for a week. Penhallow had it entered in the minutes. Now: mushrooms, dust and dye, what\'ll it be?', 'Brill sent its first wagon to us, I hear. The Exchange talked of nothing else for a week. Penhallow had it entered in the minutes. Now: mushrooms, dust and dye, what\'ll it be?', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971539, 'Undercity freight, by day, on the dot. Well. On a dot. Mushrooms, reagents, dyes. Mind the crates; they\'re heavier than they look and so am I.', 'Undercity freight, by day, on the dot. Well. On a dot. Mushrooms, reagents, dyes. Mind the crates; they\'re heavier than they look and so am I.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971540, 'Brill\'s first ever wagon came to the Sepulcher. To us! Half the town turned out to look at it. Nobody had seen a wagon arrive on purpose in years. Fish? I\'ve fish.', 'Brill\'s first ever wagon came to the Sepulcher. To us! Half the town turned out to look at it. Nobody had seen a wagon arrive on purpose in years. Fish? I\'ve fish.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971541, 'Silverpine, come in at dusk. Fish, bait, timber, and what news the worgen haven\'t eaten.', 'Silverpine, come in at dusk. Fish, bait, timber, and what news the worgen haven\'t eaten.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (971542, 'Mind your back. No, mine. Mine\'s the one that comes off.', 'Mind your back. No, mine. Mine\'s the one that comes off.', 0.500, 'Crates off, crates on. Same crates, some days. Nobody tells us.', 'Crates off, crates on. Same crates, some days. Nobody tells us.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (971543, 'Wheels greased, harness checked, horses fed. Dren says horses don\'t need feeding. Dren\'s horse disagrees.', 'Wheels greased, harness checked, horses fed. Dren says horses don\'t need feeding. Dren\'s horse disagrees.', 0.500, 'Early start, $g sir:madam;. The Undercity wagon waits for nobody, except when it\'s late.', 'Early start, $g sir:madam;. The Undercity wagon waits for nobody, except when it\'s late.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971544, 'Night watch on the yard. Nobody in, nobody out, unless they\'ve got a form. I\'ve been told about the forms.', 'Night watch on the yard. Nobody in, nobody out, unless they\'ve got a form. I\'ve been told about the forms.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (971545, 'Off the Undercity wagon. Is there a bed? There\'s a bed. Thank the Dark Lady, there\'s a bed.', 'Off the Undercity wagon. Is there a bed? There\'s a bed. Thank the Dark Lady, there\'s a bed.', 0.333, 'Bound for the Sepulcher in the morning. Or for here, if they\'ll have me. I haven\'t decided. I\'m told nobody does, at first.', 'Bound for the Sepulcher in the morning. Or for here, if they\'ll have me. I haven\'t decided. I\'m told nobody does, at first.', 0.333, 'They say Brill\'s got a brewery now. And a garden. I used to think Brill was where you went on the way to somewhere else.', 'They say Brill\'s got a brewery now. And a garden. I used to think Brill was where you went on the way to somewhere else.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (971546, 'Can\'t sleep. Never can, in a new bed. Never could in an old one, either, since.', 'Can\'t sleep. Never can, in a new bed. Never could in an old one, either, since.', 0.500, '(The traveller is sitting very still by the cold hearth.) It\'s quiet here. I\'d forgotten quiet.', '(The traveller is sitting very still by the cold hearth.) It\'s quiet here. I\'d forgotten quiet.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (971547, 'Morning, $n. Three shirts to mend for the Deathguard and Hamlin\'s apron, which I think used to be a sail.', 'Morning, $n. Three shirts to mend for the Deathguard and Hamlin\'s apron, which I think used to be a sail.', 0.500, 'I\'ve a door with my name on it. Well, on a card pinned to it. Marta says that counts.', 'I\'ve a door with my name on it. Well, on a card pinned to it. Marta says that counts.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971548, 'Is it raining? It\'s always about to rain here. That\'s a reason to wait, isn\'t it. One more day.', 'Is it raining? It\'s always about to rain here. That\'s a reason to wait, isn\'t it. One more day.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (971549, 'Your house is fine, before you ask. I\'m only here because Rudd\'s lads hold a level like it owes them money.', 'Your house is fine, before you ask. I\'m only here because Rudd\'s lads hold a level like it owes them money.', 0.500, 'A caravan office, $n. Next it\'ll be a bank. Then Brill will be a city, and I\'ll have to charge city rates.', 'A caravan office, $n. Next it\'ll be a bank. Then Brill will be a city, and I\'ll have to charge city rates.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971550, 'Oswin Thatcher. I build roofs. This one\'s an office, which means it\'ll leak on paper. I\'m doing my best.', 'Oswin Thatcher. I build roofs. This one\'s an office, which means it\'ll leak on paper. I\'m doing my best.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971600, 'The cellar breathes. The casks are full. I keep finding reasons not to open, $n. That\'s how you know it\'s nearly ready.', 'The cellar breathes. The casks are full. I keep finding reasons not to open, $n. That\'s how you know it\'s nearly ready.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971601, 'Smoke from my chimney. Do you see it? Eleven years. I keep stepping out to look at it, like a fool. Don\'t tell Calla.', 'Smoke from my chimney. Do you see it? Eleven years. I keep stepping out to look at it, like a fool. Don\'t tell Calla.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971602, 'My father\'s brown, in my father\'s hand. I\'ve read the page so often the ink\'s coming off on my thumb. Bram\'s about somewhere, saying the vats can be saved. He\'s an optimist. I find it exhausting.', 'My father\'s brown, in my father\'s hand. I\'ve read the page so often the ink\'s coming off on my thumb. Bram\'s about somewhere, saying the vats can be saved. He\'s an optimist. I find it exhausting.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971603, 'Oren Blackbarrel. Brewmaster. Yes, still. Being dead is no excuse for being out of work.', 'Oren Blackbarrel. Brewmaster. Yes, still. Being dead is no excuse for being out of work.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971604, 'Sable\'s charged me carriage on my own barley. Carriage! I carried casks up that road on my back when she was still... well, when we were all still. I\'m going round there tomorrow. I go round there every day.', 'Sable\'s charged me carriage on my own barley. Carriage! I carried casks up that road on my back when she was still... well, when we were all still. I\'m going round there tomorrow. I go round there every day.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (971605, 'Gravemalt Stout, $n. Deathguard Burgess has three a night and says it tastes of nothing. He keeps checking.', 'Gravemalt Stout, $n. Deathguard Burgess has three a night and says it tastes of nothing. He keeps checking.', 0.500, 'Pull up a bench. Mind the one on the end; it\'s Hamlin\'s, and he\'ll tell you about mushrooms.', 'Pull up a bench. Mind the one on the end; it\'s Hamlin\'s, and he\'ll tell you about mushrooms.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (971606, 'Lordaeron Reserve, $n. My father\'s brown. Folk order it and go quiet. I don\'t ask what they\'re thinking of. I know.', 'Lordaeron Reserve, $n. My father\'s brown. Folk order it and go quiet. I don\'t ask what they\'re thinking of. I know.', 0.500, 'Pull up a bench. Mind the one on the end; it\'s Hamlin\'s, and he\'ll tell you about mushrooms.', 'Pull up a bench. Mind the one on the end; it\'s Hamlin\'s, and he\'ll tell you about mushrooms.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (971607, 'Blackroot Bitter, $n. Calla tells everyone it was her idea. It was your idea. I tell everyone that.', 'Blackroot Bitter, $n. Calla tells everyone it was her idea. It was your idea. I tell everyone that.', 0.500, 'Pull up a bench. Mind the one on the end; it\'s Hamlin\'s, and he\'ll tell you about mushrooms.', 'Pull up a bench. Mind the one on the end; it\'s Hamlin\'s, and he\'ll tell you about mushrooms.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (971608, 'Delivering. Renee orders six casks a week and complains about all six. That\'s loyalty, that is.', 'Delivering. Renee orders six casks a week and complains about all six. That\'s loyalty, that is.', 0.500, 'Evening, $n. Don\'t tell Renee, but her tap pours better than mine. I\'ll fix that tomorrow. Mine, I mean.', 'Evening, $n. Don\'t tell Renee, but her tap pours better than mine. I\'ll fix that tomorrow. Mine, I mean.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (971609, '(Oren is jabbing a finger at a form.) "Contents of cask." Ale! What else would it be? ...Don\'t answer that.', '(Oren is jabbing a finger at a form.) "Contents of cask." Ale! What else would it be? ...Don\'t answer that.', 0.500, 'Sable and I have an arrangement. She charges me, and I argue, and then I pay. It\'s been working for weeks.', 'Sable and I have an arrangement. She charges me, and I argue, and then I pay. It\'s been working for weeks.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971610, 'Twelve casks this week. I sleep under the bench now. Not because I\'m tired. Because I want to be near them.', 'Twelve casks this week. I sleep under the bench now. Not because I\'m tired. Because I want to be near them.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971611, 'Bram Lusk. Cooper. (He turns a stave over in his hands, sighting along it.) Good oak doesn\'t care if you\'re dead. That\'s what I like about it.', 'Bram Lusk. Cooper. (He turns a stave over in his hands, sighting along it.) Good oak doesn\'t care if you\'re dead. That\'s what I like about it.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971612, 'Morning. Hoops first, then staves, then whatever Oren\'s broken overnight. He breaks something every night. I think it\'s how he sleeps.', 'Morning. Hoops first, then staves, then whatever Oren\'s broken overnight. He breaks something every night. I think it\'s how he sleeps.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971613, 'Caravan office wants forty casks for the Undercity run. Forty! (Bram looks very nearly happy.) I\'ll need more oak.', 'Caravan office wants forty casks for the Undercity run. Forty! (Bram looks very nearly happy.) I\'ll need more oak.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971614, 'One mug, then home. (He has said this every evening for a month. He means it every time.)', 'One mug, then home. (He has said this every evening for a month. He means it every time.)', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971615, 'He apologized. Out loud. In front of Bram. I\'ve written down the date. I may have it carved somewhere.', 'He apologized. Out loud. In front of Bram. I\'ve written down the date. I may have it carved somewhere.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971616, 'Your recipe\'s in the vat. Oren\'s pretending he chose it. Let him; it keeps him calm, and calm is when he brews best.', 'Your recipe\'s in the vat. Oren\'s pretending he chose it. Let him; it keeps him calm, and calm is when he brews best.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971617, 'Calla Fenn. Before you ask: yes, that\'s mold, yes, it\'s on purpose, and no, you can\'t have some.', 'Calla Fenn. Before you ask: yes, that\'s mold, yes, it\'s on purpose, and no, you can\'t have some.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`, `text3_0`, `text3_1`, `Probability3`) VALUES (971618, 'This week: barley, bitterroot and a culture I scraped off a grave in the old cemetery. With permission. Mostly.', 'This week: barley, bitterroot and a culture I scraped off a grave in the old cemetery. With permission. Mostly.', 0.250, 'This week\'s special is aged in a coffin. A clean one. I asked. Well, I knocked first.', 'This week\'s special is aged in a coffin. A clean one. I asked. Well, I knocked first.', 0.250, 'This week: rye, nightshade and a lullaby. Don\'t laugh; the yeast likes it.', 'This week: rye, nightshade and a lullaby. Don\'t laugh; the yeast likes it.', 0.250, 'This week\'s is so bitter Dillinger saluted it. I\'m calling that a review.', 'This week\'s is so bitter Dillinger saluted it. I\'m calling that a review.', 0.250);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971619, 'Tasting counter\'s open. Pick one. If you don\'t like it, pick another. If you don\'t like that, Oren will want to know why, at length.', 'Tasting counter\'s open. Pick one. If you don\'t like it, pick another. If you don\'t like that, Oren will want to know why, at length.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971620, 'Shh. The cultures are sleeping. Well, they\'re not. But they\'re quieter when I tell them they are.', 'Shh. The cultures are sleeping. Well, they\'re not. But they\'re quieter when I tell them they are.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (971621, 'I don\'t drink. Can\'t. I come for the arguing. Best arguing in Tirisfal.', 'I don\'t drink. Can\'t. I come for the arguing. Best arguing in Tirisfal.', 0.333, 'Oren says this one tastes of the old kingdom. I say it tastes of Oren. Neither of us can taste a thing.', 'Oren says this one tastes of the old kingdom. I say it tastes of Oren. Neither of us can taste a thing.', 0.333, 'Sit, sit. The bench by the door wobbles. Don\'t sit there. That\'s where the new ones sit, so we can watch.', 'Sit, sit. The bench by the door wobbles. Don\'t sit there. That\'s where the new ones sit, so we can watch.', 0.333);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`) VALUES (971622, 'A real roof, $n, and ale delivered to the door. If Blackbarrel would just come down two silver a cask I\'d die happy. Again.', 'A real roof, $n, and ale delivered to the door. If Blackbarrel would just come down two silver a cask I\'d die happy. Again.', 0.500, 'Full house tonight: two from the Undercity, one from the Sepulcher and a fellow who says he\'s from Stratholme and won\'t say more. I\'ve put him by the window.', 'Full house tonight: two from the Undercity, one from the Sepulcher and a fellow who says he\'s from Stratholme and won\'t say more. I\'ve put him by the window.', 0.500);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971623, 'The Wayfarer\'s Rest! Beds, board and no questions. Well, a few questions. I like to know who\'s under my roof.', 'The Wayfarer\'s Rest! Beds, board and no questions. Well, a few questions. I like to know who\'s under my roof.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971624, 'Blackbarrel\'s ale in a tent. It\'s very good ale. It\'s a very bad tent. When that caravan office gets round to building me a roof, I\'ll serve it properly.', 'Blackbarrel\'s ale in a tent. It\'s very good ale. It\'s a very bad tent. When that caravan office gets round to building me a roof, I\'ll serve it properly.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971625, 'Marta Greaves. Rooms, enquire within. Within the tent. It\'s a very good tent. The caravan office has promised me walls, when they\'ve finished their paperwork.', 'Marta Greaves. Rooms, enquire within. Within the tent. It\'s a very good tent. The caravan office has promised me walls, when they\'ve finished their paperwork.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971626, 'Your roof\'s fine, $n. I\'m here because Bram asked me to look at the rafters, and because Oren keeps telling me about his father, and I find I don\'t mind.', 'Your roof\'s fine, $n. I\'m here because Bram asked me to look at the rafters, and because Oren keeps telling me about his father, and I find I don\'t mind.', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES (971627, 'Oswin Thatcher. The roof wants new shingles and the floor wants a miracle. I can do one of those.', 'Oswin Thatcher. The roof wants new shingles and the floor wants a miracle. I can do one of those.', 1);
-- (20 of the town's 21 phases used)
