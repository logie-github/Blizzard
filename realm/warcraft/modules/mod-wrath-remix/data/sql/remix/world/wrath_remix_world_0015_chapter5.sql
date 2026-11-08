-- Chapter V, The Lifewarden's Warning (STORY.md): Sholazar Basin, and Moratari's chapter. Moratari's
-- transitions as the earlier chapters' are made (wrath_remix_world_0006_bridges.sql), and between
-- them Eternus's agents at the Maker's Overlook, siphoning the Makers' pillar to build something
-- that can hold an hour still; as that is undone, Eternus comes for Moratari herself (its scene in
-- wrath_remix_world_0014_scenes.sql).
--
--   WRM-501  after A Kingdom Gone (77421) or Welcome to Sholazar Basin (12489), Moratari by Hemet
--            Nesingwary: the hunt left alone; to Pilot Vic, whose Force of Nature (12803) leads to
--            the Avatar of Freya
--   WRM-502  after Powering the Waygate - The Maker's Perch (12559), Moratari at the Maker's
--            Overlook: six Infinite Siphoners and the Siphon of Hours; The Etymidian (12548) waits
--            for it
--   WRM-521  after Reclamation (12546), Moratari by the Avatar of Freya: to K3 in the Storm Peaks,
--            Chapter VI (Gretchen Fizzlespark's They Took Our Men!, 12843)
--
-- Spawns 7704240 to 7704259.

SET @MORATARI := 770001, @SIPHONER := 770046, @SIPHON := 770047;

DELETE FROM `quest_template` WHERE `ID` IN (77501, 77502, 77521);
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `RewardXPDifficulty`, `RewardMoney`, `Flags`,
  `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `QuestCompletionLog`,
  `RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `RequiredNpcOrGo2`, `RequiredNpcOrGoCount2`, `ObjectiveText1`, `ObjectiveText2`, `VerifiedBuild`) VALUES
-- V-A: Mr. Nesingwary's hunt.
(77501, 2, 54, 52, 3711, 5, 0, 0, 0,
 'A Brief Hunting Expedition',
 'Speak with Moratari again to travel to Pilot Vic.',
 'Mr. Nesingwary has an impressive catalog. Rhinos, crocolisks, a great many very large cats. He would like you to add to it, and he will be very cheerful about it, and it will take you the better part of a week.$B$BWe shall admire it from a safe temporal distance.$B$BSomething else is happening in this basin, $n. The titans built it to keep life safe, and something here has woken that still remembers how. A pilot named Vic has set down not far from it. Let us start with him.',
 'Speak with Moratari.', 0, 0, 0, 0, '', '', 0),
-- WRM-502: the Maker's Overlook.
(77502, 2, 57, 52, 3711, 5, 0, 0, 0,
 'Stolen Hours',
 'Slay 6 Infinite Siphoners and destroy the Siphon of Hours at the Maker''s Overlook, then speak with Moratari there.',
 'Stop. Before you touch that switch, look at the pillar.$B$BSee how the light bends around it, as if it were a little later there than here? That is a siphon of hours. Eternus''s agents are drinking the Makers'' power out of this place, one stolen hour at a time.$B$BI built the first of those, $n. A long time ago, for her, for something I believed in. I know what that much power is for, and I do not like it.$B$BKill them. Break it. Then we will talk about what she is building.',
 'Speak with Moratari at the Maker''s Overlook.', @SIPHONER, 6, @SIPHON, 1, 'Infinite Siphoner slain', 'Siphon of Hours destroyed', 0),
-- WRM-521: to the Storm Peaks.
(77521, 2, 60, 52, 3711, 5, 0, 0, 0,
 'The Makers'' Trail',
 'Speak with Moratari again to travel to K3, at the foot of the Storm Peaks.',
 'The waygate opens, the cult is gone, and the Avatar has her garden back. Freya herself is very far from here, and very much not herself, and I suspect her avatar knows it.$B$BThe titans left more than gardens in Northrend. North of here, in the Storm Peaks, they left a city: Ulduar. Giants walk those mountains, and some of them still remember the Makers. Some remember them wrong.$B$BAlleria asked me to tell her when you reach the mountains. I think she has felt something up there that she does not like. There is a goblin outpost called K3 at the foot of the peaks. Chapter VI begins there.',
 'Speak with Moratari.', 0, 0, 0, 0, '', '', 0);

DELETE FROM `quest_template_addon` WHERE `ID` IN (77501, 77502, 77521);
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`) VALUES (77501, 0), (77502, 12559), (77521, 12546);

DELETE FROM `quest_offer_reward` WHERE `ID` IN (77501, 77502, 77521);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`, `VerifiedBuild`) VALUES
(77501, 1, 'Hold on. Vic has had a very bad week, and he is about to tell you all about it.', 0),
(77502, 1, 'It''s done. The pillar is the Makers'' again.$B$BStay a moment, $n. I think someone is about to come and see me.', 0),
(77521, 1, 'Hold on. It is cold up there. Colder than anywhere you have been, and you have been to the Dragonblight.', 0);

DELETE FROM `creature_queststarter` WHERE `quest` IN (77501, 77502, 77521);
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES (@MORATARI, 77501), (@MORATARI, 77502), (@MORATARI, 77521);
DELETE FROM `creature_questender` WHERE `quest` IN (77501, 77502, 77521);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES (@MORATARI, 77501), (@MORATARI, 77502), (@MORATARI, 77521);

DELETE FROM `remix_bridge` WHERE `quest` IN (77501, 77502, 77521);
-- Before Pilot Vic and Gretchen Fizzlespark, facing them.
INSERT INTO `remix_bridge` (`quest`, `next_quest`, `chapter`, `map`, `x`, `y`, `z`, `o`, `skipped`)
SELECT b.quest, b.next_quest, b.chapter, c.`map`, c.`position_x` + 4 * COS(c.`orientation`), c.`position_y` + 4 * SIN(c.`orientation`),
  c.`position_z` + 0.5, MOD(c.`orientation` + PI(), 2 * PI()), b.skipped
FROM `creature` c JOIN (
  SELECT 77501 AS quest, 12803 AS next_quest, 5 AS chapter, 102602 AS facing, '12520 12526 12556 12549 12550 12558 12551 12560 12569 12595' AS skipped UNION ALL
  SELECT 77521, 12843, 6, 98958, ''
) b ON c.`guid` = b.facing;

-- WRM-501 follows either way into the basin; The Etymidian waits for WRM-502.
DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 19 AND `SourceEntry` IN (77501, 12548);
INSERT INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`, `ConditionTypeOrReference`,
  `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`, `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`) VALUES
(19, 0, 77501, 0, 0, 8, 0, 77421, 0, 0, 0, 0, 0, '', 'Wrath Remix: A Brief Hunting Expedition after A Kingdom Gone'),
(19, 0, 77501, 0, 1, 8, 0, 12489, 0, 0, 0, 0, 0, '', 'Wrath Remix: ... or after Welcome to Sholazar Basin'),
(19, 0, 12548, 0, 0, 8, 0, 77502, 0, 0, 0, 0, 0, '', 'Wrath Remix: The Etymidian after Stolen Hours');

-- Moratari by Hemet Nesingwary and by the Avatar of Freya (a step to their left), and on the Maker's
-- Overlook by its switch; the Siphoners about the pillar's platform, the Siphon by the switch.
DELETE FROM `creature` WHERE `guid` BETWEEN 7704240 AND 7704259;
INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `equipment_id`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`)
SELECT 7704240 + n, @MORATARI, c.`map`, 1, c.`phaseMask`, 1,
  c.`position_x` + 2.5 * COS(c.`orientation` + PI() / 2), c.`position_y` + 2.5 * SIN(c.`orientation` + PI() / 2),
  c.`position_z`, c.`orientation`, 60, 0, 0, CONCAT('Wrath Remix: Moratari, ', what)
FROM `creature` c JOIN (
  SELECT 0 AS n, 103256 AS beside, 'WRM-501, Nesingwary Base Camp (Hemet Nesingwary)' AS what UNION ALL
  SELECT 1, 110319, 'WRM-521, Rainspeaker Rapids (the Avatar of Freya)'
) b ON c.`guid` = b.beside;
INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `equipment_id`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(7704242, @MORATARI, 571, 1, 1, 1, 5739.0, 3046.0, 288.1, 0.20, 60, 0, 0, 'Wrath Remix: Moratari, WRM-502, the Maker''s Overlook'),
(7704243, @SIPHONER, 571, 1, 1, 0, 5745.0, 3060.0, 288.1, 4.70, 180, 0, 0, 'Wrath Remix: Infinite Siphoner, the Maker''s Overlook'),
(7704244, @SIPHONER, 571, 1, 1, 0, 5758.0, 3062.0, 288.1, 4.20, 180, 0, 0, 'Wrath Remix: Infinite Siphoner, the Maker''s Overlook'),
(7704245, @SIPHONER, 571, 1, 1, 0, 5768.0, 3054.0, 288.0, 2.40, 180, 0, 0, 'Wrath Remix: Infinite Siphoner, the Maker''s Overlook'),
(7704246, @SIPHONER, 571, 1, 1, 0, 5730.0, 3058.0, 288.1, 5.60, 180, 0, 0, 'Wrath Remix: Infinite Siphoner, the Maker''s Overlook'),
(7704247, @SIPHONER, 571, 1, 1, 0, 5772.0, 3058.0, 288.1, 3.60, 180, 0, 0, 'Wrath Remix: Infinite Siphoner, the Maker''s Overlook'),
(7704248, @SIPHONER, 571, 1, 1, 0, 5752.0, 3070.0, 288.1, 4.70, 180, 0, 0, 'Wrath Remix: Infinite Siphoner, the Maker''s Overlook'),
(7704249, @SIPHONER, 571, 1, 1, 0, 5735.0, 3050.0, 288.0, 1.40, 180, 0, 0, 'Wrath Remix: Infinite Siphoner, the Maker''s Overlook'),
(7704250, @SIPHON,   571, 1, 1, 0, 5756.0, 3049.0, 288.1, 0,    180, 0, 0, 'Wrath Remix: Siphon of Hours, the Maker''s Overlook');

DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 30 AND (`SourceId` BETWEEN 7704240 AND 7704259 OR `SourceEntry` IN (@SIPHONER, @SIPHON));
INSERT INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`, `ConditionTypeOrReference`,
  `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`, `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`) VALUES
(30, 0, @MORATARI, 7704242, 0, 8, 0, 12559, 0, 0, 0, 0, 0, '', 'Wrath Remix: Moratari at the Maker''s Overlook once the Perch is powered'),
(30, 0, @SIPHONER, 0, 0, 47, 0, 77502, 8, 0, 0, 0, 0, '', 'Wrath Remix: Eternus''s agents at the Overlook, for Stolen Hours'),
(30, 0, @SIPHON, 0, 0, 47, 0, 77502, 8, 0, 0, 0, 0, '', 'Wrath Remix: their siphon, for Stolen Hours');

DELETE FROM `remix_quest_reward` WHERE `quest` IN (77501, 77502, 77521);
INSERT INTO `remix_quest_reward` (`quest`, `bronze`) VALUES (77501, 1000), (77502, 4000), (77521, 2000);
