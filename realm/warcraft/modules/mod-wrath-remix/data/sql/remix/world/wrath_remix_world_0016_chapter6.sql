-- Chapter VI, The Secrets of Ulduar (STORY.md): the Storm Peaks, and Eternus's grief. Moratari's
-- transitions as the earlier chapters' are made (wrath_remix_world_0006_bridges.sql), and on the
-- Terrace of the Makers Eternus's agents weaving an echo of Sif out of the hours before she died,
-- to give a grieving god his wife back; as that is undone, Eternus stands before Thorim herself
-- (its scene in wrath_remix_world_0014_scenes.sql).
--
--   WRM-601  after Taking on All Challengers (12971), Moratari by Lok'lira the Crone: the bear, the
--            harness, the last proto-drake and the pit, annotated; Lok'lira's Parting Gift (13062)
--   WRM-602  after The Terrace of the Makers (13057), Moratari by Thorim on the Terrace: four
--            Infinite Weavers; Loken's Lackeys (13035) and The Earthen Oath (13005) wait for it
--   WRM-621  after The Reckoning (13047), Moratari by King Jokkum: to the Argent Vanguard in
--            Icecrown, Chapter VII (Highlord Tirion Fordring's Honor Above All Else, 13036)
--
-- Spawns 7704260 to 7704279.

SET @MORATARI := 770001, @WEAVER := 770048;

DELETE FROM `quest_template` WHERE `ID` IN (77601, 77602, 77621);
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `RewardXPDifficulty`, `RewardMoney`, `Flags`,
  `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `QuestCompletionLog`,
  `RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `ObjectiveText1`, `VerifiedBuild`) VALUES
-- VI-A: the Sons of Hodir's tests.
(77601, 2, 64, 60, 67, 5, 0, 0, 0,
 'The Very Long Road to Thorim',
 'Speak with Moratari again to be ready for Lok''lira''s Parting Gift.',
 'Lok''lira has more for you. A bear to befriend, a harness to make, the last proto-drake of her kind to ride, and a pit full of very large people who would like to hit you, one at a time, until the Sons of Hodir are impressed.$B$BIf we count every sparring victory, we will be here for several centuries. I have annotated the results.$B$BThe crone is ready to give you what you came for. After that, the Drakkensryd, and a storm giant who has been waiting a very long time for someone to climb up to him.',
 'Speak with Moratari.', 0, 0, '', 0),
-- WRM-602: the Terrace of the Makers.
(77602, 2, 68, 60, 67, 5, 0, 0, 0,
 'A Gift of Grief',
 'Slay 4 Infinite Weavers on the Terrace of the Makers, then speak with Moratari.',
 'Do you see them, at the edge of the terrace? Weavers. Eternus has sent them to make something delicate, and I have just understood what it is.$B$BThey are weaving an echo of Sif out of the hours before she died. Thorim''s wife. Eternus means to stand her in front of her husband and give her back to him.$B$BIt is the kindest thing she has ever tried, and it would ruin him. A storm giant who gets his wife back from a stranger does not go to war with his brother. He does not go anywhere at all. And everything Loken has done in these mountains goes on being done.$B$BStop the weaving, $n.',
 'Speak with Moratari on the Terrace of the Makers.', @WEAVER, 4, 'Infinite Weaver slain', 0),
-- WRM-621: to Icecrown.
(77621, 2, 70, 60, 67, 5, 0, 0, 0,
 'Storm''s End',
 'Speak with Moratari again to travel to the Argent Vanguard in Icecrown.',
 'Loken''s hold on these mountains is broken, and Thorim remembers who he is. Loken himself waits in the Halls of Lightning, deep in the mountain; Sa''at can send you there, when you are ready to finish what Thorim started.$B$BAnd beyond these peaks, the last of it. Icecrown. The Argent Crusade has carved a foothold out of the ice, and Highlord Tirion Fordring is gathering everyone who will come to stand at the Lich King''s door.$B$BEternus will be there. She has nowhere else left to be. Chapter VII begins at the Argent Vanguard.',
 'Speak with Moratari.', 0, 0, '', 0);

DELETE FROM `quest_template_addon` WHERE `ID` IN (77601, 77602, 77621);
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`) VALUES (77601, 12971), (77602, 13057), (77621, 13047);

DELETE FROM `quest_offer_reward` WHERE `ID` IN (77601, 77602, 77621);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`, `VerifiedBuild`) VALUES
(77601, 1, 'There. You were magnificent in the pit. I have it in writing.', 0),
(77602, 1, 'That''s the last of them. The echo is still there, half-made; I can''t unweave it in time.$B$BShe is coming. Stand with Thorim, $n. Whatever happens, let him answer.', 0),
(77621, 1, 'Hold on. This is the last road. Let''s not be late for it.', 0);

DELETE FROM `creature_queststarter` WHERE `quest` IN (77601, 77602, 77621);
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES (@MORATARI, 77601), (@MORATARI, 77602), (@MORATARI, 77621);
DELETE FROM `creature_questender` WHERE `quest` IN (77601, 77602, 77621);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES (@MORATARI, 77601), (@MORATARI, 77602), (@MORATARI, 77621);

DELETE FROM `remix_bridge` WHERE `quest` IN (77601, 77602, 77621);
INSERT INTO `remix_bridge` (`quest`, `next_quest`, `chapter`, `map`, `x`, `y`, `z`, `o`, `skipped`) VALUES
-- At Lok'lira, who gives what follows: nowhere to go.
(77601, 13062, 6, 65535, 0, 0, 0, 0, '12972 12851 12856 13063 12900 12983 12996 12997 13061');
-- Before Highlord Tirion Fordring at the Argent Vanguard, facing him.
INSERT INTO `remix_bridge` (`quest`, `next_quest`, `chapter`, `map`, `x`, `y`, `z`, `o`, `skipped`)
SELECT 77621, 13036, 7, c.`map`, c.`position_x` + 4 * COS(c.`orientation`), c.`position_y` + 4 * SIN(c.`orientation`),
  c.`position_z` + 0.5, MOD(c.`orientation` + PI(), 2 * PI()), ''
FROM `creature` c WHERE c.`guid` = 207222;

-- Lok'lira's Parting Gift opens with VI-A or the pit's end (Prepare for Glory: its PrevQuestID, now
-- a condition); Loken's Lackeys and The Earthen Oath wait for WRM-602.
UPDATE `quest_template_addon` SET `PrevQuestID` = 0 WHERE `ID` = 13062;
DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 19 AND `SourceEntry` IN (13062, 13035, 13005);
INSERT INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`, `ConditionTypeOrReference`,
  `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`, `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`) VALUES
(19, 0, 13062, 0, 0, 8, 0, 77601, 0, 0, 0, 0, 0, '', 'Wrath Remix: Lok''lira''s Parting Gift after The Very Long Road to Thorim'),
(19, 0, 13062, 0, 1, 8, 0, 13061, 0, 0, 0, 0, 0, '', 'Wrath Remix: ... or after Prepare for Glory'),
(19, 0, 13035, 0, 0, 8, 0, 77602, 0, 0, 0, 0, 0, '', 'Wrath Remix: Loken''s Lackeys after A Gift of Grief'),
(19, 0, 13005, 0, 0, 8, 0, 77602, 0, 0, 0, 0, 0, '', 'Wrath Remix: The Earthen Oath after A Gift of Grief');

-- Moratari by Lok'lira, by Thorim on the Terrace and by King Jokkum (a step to their left); the
-- Weavers about the Terrace's edge around Thorim.
DELETE FROM `creature` WHERE `guid` BETWEEN 7704260 AND 7704279;
INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `equipment_id`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`)
SELECT 7704260 + n, @MORATARI, c.`map`, 1, c.`phaseMask`, 1,
  c.`position_x` + 2.5 * COS(c.`orientation` + PI() / 2), c.`position_y` + 2.5 * SIN(c.`orientation` + PI() / 2),
  c.`position_z`, c.`orientation`, 60, 0, 0, CONCAT('Wrath Remix: Moratari, ', what)
FROM `creature` c JOIN (
  SELECT 0 AS n, 2593 AS beside, 'WRM-601, the Hyldsmeet (Lok''lira the Crone)' AS what UNION ALL
  SELECT 1, 1955077, 'WRM-602, the Terrace of the Makers (Thorim)' UNION ALL
  SELECT 2, 207220, 'WRM-621, Dun Niffelem (King Jokkum)'
) b ON c.`guid` = b.beside;
INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `equipment_id`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`)
SELECT 7704263 + n, @WEAVER, c.`map`, 1, 1, 0, c.`position_x` + dx, c.`position_y` + dy, c.`position_z`, o, 180, 0, 0,
  'Wrath Remix: Infinite Weaver, the Terrace of the Makers'
FROM `creature` c JOIN (
  SELECT 0 AS n, 14.0 AS dx, 10.0 AS dy, 3.80 AS o UNION ALL
  SELECT 1, 10.0, 4.0, 3.50 UNION ALL
  SELECT 2, -10.0, -2.0, 0.20 UNION ALL
  SELECT 3, -9.0, 15.0, 5.20 UNION ALL
  SELECT 4, 18.0, -3.0, 3.10
) w ON c.`guid` = 1955077;

DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 30 AND (`SourceId` BETWEEN 7704260 AND 7704279 OR `SourceEntry` = @WEAVER);
INSERT INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`, `ConditionTypeOrReference`,
  `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`, `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`) VALUES
(30, 0, @WEAVER, 0, 0, 47, 0, 77602, 8, 0, 0, 0, 0, '', 'Wrath Remix: Eternus''s Weavers on the Terrace, for A Gift of Grief');

DELETE FROM `remix_quest_reward` WHERE `quest` IN (77601, 77602, 77621);
INSERT INTO `remix_quest_reward` (`quest`, `bronze`) VALUES (77601, 1500), (77602, 5000), (77621, 2500);
