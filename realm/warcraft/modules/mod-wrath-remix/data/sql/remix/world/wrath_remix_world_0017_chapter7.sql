-- Chapter VII, Icecrown (STORY.md): the Argent Crusade's war, Crusader Bridenbrad and the one
-- Eternus could not save, Sylvanas before the Frozen Halls, the Frozen Halls themselves, Eternus's
-- last hour at the doors of Icecrown Citadel, and the Lich King. Its scenes are in
-- wrath_remix_world_0014_scenes.sql; the last hour's fight in RemixLastHour.cpp.
--
--   WRM-702  after Light Within the Darkness (13083), Moratari by Tirion at Crusaders' Pinnacle:
--            Eternus, who went to Bridenbrad before the naaru did
--   WRM-701  Alliance  after The Crusaders' Pinnacle (13157), Moratari by Tirion: to Sylvanas at the
--                      Bazaar (taking it goes there); to Dalaran, before Apprentice Nelphi and
--                      Inside the Frozen Citadel (24510)
--   WRM-711  Horde     the same; before Dark Ranger Vorel and Inside the Frozen Citadel (24506)
--   WRM-721  after Wrath of the Lich King (24500, 24802), Moratari outside the Frozen Halls (taking
--            it goes to the doors of Icecrown Citadel): Eternus's last hour
--   WRM-800  after The Last Hour, Moratari at the Citadel's doors: the Lich King; turned in to
--            Moratari at the Bazaar, where the Timerunner is brought once the ending cinematic is
--            over, or at their next login if they were gone before it (RemixEnding.cpp)
--
-- Spawns 7704280 to 7704299.
--
-- WRM-702 and WRM-701/711, both from the same Moratari, can be in the log together: each scene's
-- credit, the scenes' one, goes to its own quest alone (RemixScenes.cpp).

SET @MORATARI := 770001, @SYLVANAS := 770011, @SCENE_CREDIT := 770035, @LAST_HOUR_CREDIT := 770036, @LICH_KING := 36597;

DELETE FROM `quest_template` WHERE `ID` IN (77701, 77702, 77711, 77721, 77800);
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `RewardXPDifficulty`, `RewardMoney`, `Flags`,
  `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `QuestCompletionLog`,
  `RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `ObjectiveText1`, `VerifiedBuild`) VALUES
-- WRM-702: after Bridenbrad.
(77702, 2, 78, 70, 210, 5, 0, 0, 0,
 'What He Was Offered',
 'Hear Eternus out at Crusaders'' Pinnacle, then speak with Moratari.',
 'Bridenbrad is at peace. The naaru came for him, and he went with them.$B$BSomeone else came for him first, $n. I can feel where Eternus stood in the snow beside him. She is still close. I think she wants to talk to you.$B$BStay with me a moment.',
 'Speak with Moratari at Crusaders'' Pinnacle.', @SCENE_CREDIT, 1, 'Eternus heard out', 0),
-- WRM-701 / 711 (VII-A): the rest of Icecrown's war, and Sylvanas before the Frozen Halls.
(77701, 2, 78, 70, 210, 5, 0, 0, 1101,
 'The Armies Are in Place',
 'Speak with Sylvanas Windrunner at the Infinite Bazaar.',
 'The Crusade holds the Pinnacle, the Ebon Blade holds the Shadow Vault, and the war in Icecrown has more work in it than any one hero could finish in a lifetime. You have done enough quartermaster work to supply all of history.$B$BThe Frozen Halls are next: the Lich King''s forge, his pit and his hall of mirrors. Before you go in, Sylvanas has asked to see you. I think it costs her something to ask.$B$BI will take you to the Bazaar.',
 'Speak with Sylvanas Windrunner at the Infinite Bazaar.', @SCENE_CREDIT, 1, 'Sylvanas heard out', 0),
(77711, 2, 78, 70, 210, 5, 0, 0, 690,
 'The Armies Are in Place',
 'Speak with Sylvanas Windrunner at the Infinite Bazaar.',
 'The Crusade holds the Pinnacle, the Ebon Blade holds the Shadow Vault, and the war in Icecrown has more work in it than any one hero could finish in a lifetime. You have done enough quartermaster work to supply all of history.$B$BThe Frozen Halls are next: the Lich King''s forge, his pit and his hall of mirrors. Before you go in, Sylvanas has asked to see you. I think it costs her something to ask.$B$BI will take you to the Bazaar.',
 'Speak with Sylvanas Windrunner at the Infinite Bazaar.', @SCENE_CREDIT, 1, 'Sylvanas heard out', 0),
-- WRM-721: the last hour.
(77721, 2, 80, 70, 210, 5, 0, 0, 0,
 'The Last Hour',
 'Face Eternus at the doors of Icecrown Citadel, then speak with Moratari there.',
 'You came out. The record is whole.$B$BWe have reached the end of the road, $n. The Citadel. Bolvar''s last hour, and Arthas''s.$B$BAnd Eternus is at its doors. Every Infinite still loyal to her is with her. She means to hold the last hour open, and I do not think she will let anyone talk her out of it this time.$B$BSylvanas and Alleria are already there, and I will be beside you. Come.',
 'Speak with Moratari at the doors of Icecrown Citadel.', @LAST_HOUR_CREDIT, 1, 'Eternus driven off', 0),
-- WRM-800: the Lich King (a raid's quest: its credit counts in a raid group).
(77800, 2, 80, 70, 210, 5, 0, 64, 0,
 'The Last Necessary Battle',
 'Defeat the Lich King atop Icecrown Citadel, then return to Moratari at the Infinite Bazaar.',
 'This is the part of history we came here to understand. The rest of it is yours.$B$BGo up through the Citadel, through everything he has left between you and the top. Tirion Fordring will be with you at the end. So will a great many people who will not live to see the morning.$B$BWhen the Lich King falls, someone has to take up his crown. You know who. Let him.$B$BThis last battle is yours to fight. I will be waiting for you at the Bazaar.',
 'Return to Moratari at the Infinite Bazaar.', @LICH_KING, 1, 'The Lich King defeated', 0);

DELETE FROM `quest_template_addon` WHERE `ID` IN (77701, 77702, 77711, 77721, 77800);
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`) VALUES (77702, 13083), (77701, 13157), (77711, 13157), (77721, 0), (77800, 77721);

DELETE FROM `quest_offer_reward` WHERE `ID` IN (77701, 77702, 77711, 77721, 77800);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`, `VerifiedBuild`) VALUES
(77702, 1, 'She never asked any of them. I think she is only now realizing it.$B$BIt may be the most important thing that has happened to her in this whole war, and no one but you and I will ever know.', 0),
(77701, 1, 'Go. Apprentice Nelphi is waiting for you in Dalaran; she knows the way into the Frozen Halls. I will not be going with you.', 0),
(77711, 1, 'Go. Dark Ranger Vorel is waiting for you in Dalaran. She serves me, in this year. Be kind to her.', 0),
(77721, 1, 'Catch your breath, $n. She will not be back tonight.$B$BEverything we came here for is behind those doors.', 0),
(77800, 1, 'You are back.$B$BSit down a moment. You have earned that, at least.', 0);

DELETE FROM `creature_queststarter` WHERE `quest` IN (77701, 77702, 77711, 77721, 77800);
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES
(@MORATARI, 77702), (@MORATARI, 77701), (@MORATARI, 77711), (@MORATARI, 77721), (@MORATARI, 77800);
DELETE FROM `creature_questender` WHERE `quest` IN (77701, 77702, 77711, 77721, 77800);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES
(@MORATARI, 77702), (@SYLVANAS, 77701), (@SYLVANAS, 77711), (@MORATARI, 77721), (@MORATARI, 77800);

-- Where taking a quest goes: to the Bazaar, before Sylvanas (who stands at its east side, facing
-- west); to the doors of Icecrown Citadel, where its raid lets people out.
DELETE FROM `remix_departure` WHERE `quest` IN (77701, 77711, 77721);
INSERT INTO `remix_departure` (`quest`, `map`, `x`, `y`, `z`, `o`) VALUES
(77701, 571, 6394.4, 1873.2, 508.7, 0.46),
(77711, 571, 6394.4, 1873.2, 508.7, 0.46),
(77721, 571, 5790.0, 2071.5, 636.1, 0.40);

-- Turning in VII-A goes to Dalaran, before the Frozen Halls' first quest giver of each side.
DELETE FROM `remix_bridge` WHERE `quest` IN (77701, 77702, 77711, 77721, 77800);
INSERT INTO `remix_bridge` (`quest`, `next_quest`, `chapter`, `map`, `x`, `y`, `z`, `o`, `skipped`)
SELECT b.quest, b.next_quest, 7, c.`map`, c.`position_x` + 4 * COS(c.`orientation`), c.`position_y` + 4 * SIN(c.`orientation`),
  c.`position_z` + 0.5, MOD(c.`orientation` + PI(), 2 * PI()), b.skipped
FROM `creature` c JOIN (
  SELECT 77701 AS quest, 24510 AS next_quest, 101236 AS facing, '' AS skipped UNION ALL
  SELECT 77711, 24506, 133649, ''
) b ON c.`guid` = b.facing;

-- The Last Hour after either side's escape from the Halls of Reflection.
DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 19 AND `SourceEntry` = 77721;
INSERT INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`, `ConditionTypeOrReference`,
  `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`, `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`) VALUES
(19, 0, 77721, 0, 0, 8, 0, 24500, 0, 0, 0, 0, 0, '', 'Wrath Remix: The Last Hour after Wrath of the Lich King (Alliance)'),
(19, 0, 77721, 0, 1, 8, 0, 24802, 0, 0, 0, 0, 0, '', 'Wrath Remix: ... or the Horde''s');

-- Moratari by Tirion at Crusaders' Pinnacle (a step to his left), outside the Frozen Halls, where
-- their dungeons let people out, and at the doors of the Citadel.
DELETE FROM `creature` WHERE `guid` BETWEEN 7704280 AND 7704299;
INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `equipment_id`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`)
SELECT 7704280, @MORATARI, c.`map`, 1, c.`phaseMask`, 1,
  c.`position_x` + 2.5 * COS(c.`orientation` + PI() / 2), c.`position_y` + 2.5 * SIN(c.`orientation` + PI() / 2),
  c.`position_z`, c.`orientation`, 60, 0, 0, 'Wrath Remix: Moratari, WRM-701/711 and WRM-702, Crusaders'' Pinnacle (Highlord Tirion Fordring)'
FROM `creature` c WHERE c.`guid` = 121845;
INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `equipment_id`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(7704281, @MORATARI, 571, 1, 1, 1, 5627.0, 1993.0, 798.1, 0.80, 60, 0, 0, 'Wrath Remix: Moratari, WRM-721, outside the Frozen Halls'),
(7704282, @MORATARI, 571, 1, 1, 1, 5786.0, 2066.0, 636.1, 0.40, 60, 0, 0, 'Wrath Remix: Moratari, WRM-721 and WRM-800, the doors of Icecrown Citadel');

DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 30 AND `SourceId` BETWEEN 7704280 AND 7704299;
INSERT INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`, `ConditionTypeOrReference`,
  `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`, `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`) VALUES
(30, 0, @MORATARI, 7704281, 0, 8, 0, 24500, 0, 0, 0, 0, 0, '', 'Wrath Remix: Moratari outside the Frozen Halls after the escape (Alliance)'),
(30, 0, @MORATARI, 7704281, 1, 8, 0, 24802, 0, 0, 0, 0, 0, '', 'Wrath Remix: ... or the Horde''s'),
-- (not while the last hour's fight is on: her other self fights beside the Timerunner then)
(30, 0, @MORATARI, 7704282, 0, 47, 0, 77721, 66, 0, 0, 0, 0, '', 'Wrath Remix: Moratari at the Citadel''s doors once Eternus is driven off');

DELETE FROM `remix_quest_reward` WHERE `quest` IN (77701, 77702, 77711, 77721, 77800);
INSERT INTO `remix_quest_reward` (`quest`, `bronze`) VALUES
(77702, 5000), (77701, 2500), (77711, 2500), (77721, 25000), (77800, 50000);
