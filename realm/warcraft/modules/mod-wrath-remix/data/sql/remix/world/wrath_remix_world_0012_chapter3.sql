-- Moratari's transitions in Chapter III, The Curse of Grizzly Hills (the guide's bridges III-A and
-- III-B, and WRM-321), as Chapter I's and II's are made (wrath_remix_world_0006_bridges.sql): a new
-- quest from Moratari by the ender of the original quest it follows
-- (wrath_remix_world_0004_spawns.sql). Never Drak'Tharon Keep or what Drakuru says there: III-B
-- only comes before it, and WRM-321 after it.
--
--   WRM-301  Alliance  after Ursoc, the Bear God (12249)          opens Filling the Cages (11984)
--   WRM-311  Horde     after Ursoc, the Bear God (12236)          opens Filling the Cages (11984)
--   WRM-302  both      after Voices From the Dust (12068)         at Drak'Tharon's door, before Cleansing Drak'Tharon
--   WRM-321  both      after Cleansing Drak'Tharon (12238): to Light's Breach in Zul'Drak, Chapter IV
--
-- Voices From the Dust is turned in to the Image of Drakuru at Drakil'jin Ruins, Cleansing
-- Drak'Tharon to the one the dungeon summons at its top, where nobody can stand beside it: WRM-302's
-- and WRM-321's Moratari stands at the keep's door in the Grizzly Hills instead
-- (wrath_remix_world_0004_spawns.sql), where the Timerunner goes in and the keep puts them out again.

SET @MORATARI := 770001;

DELETE FROM `quest_template` WHERE `ID` IN (77301, 77302, 77311, 77321);
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `RewardXPDifficulty`, `RewardMoney`, `Flags`,
  `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `QuestCompletionLog`, `VerifiedBuild`) VALUES
-- III-A: Ursoc at rest, and the hills' other wars (lumber camps, the Iron Thane, goblins and
-- shredders, the Conquest Pit) left to whoever wants them. Drakuru's breadcrumbs are Troll Season!
-- and Good Troll Hunting.
(77301, 2, 38, 32, 394, 5, 0, 0, 1101,
 'A Shorter Path Through the Woods',
 'Speak with Moratari again to travel to Samir, by Drakuru''s cages.',
 'Ursoc rests, and the forest is a little less sick than it was. Amberpine Lodge has a great deal more for you: lumber camps at war with each other, a dwarf with an iron anvil and a worse temper, goblins, shredders, wolves.$B$BThere are a dozen paths through these woods. Only one ends with a very interesting troll. His name is Drakuru. He would like to be your friend, and he has cages that need filling.$B$BIf you would rather walk every one of those paths yourself, the woods will keep them for you.',
 'Speak with Moratari.', 0),
(77311, 2, 38, 32, 394, 5, 0, 0, 690,
 'A Shorter Path Through the Woods',
 'Speak with Moratari again to travel to Samir, by Drakuru''s cages.',
 'Ursoc rests, and the forest is a little less sick than it was. Conquest Hold has a great deal more for you: a pit to fight in, lumber camps at war, an iron dwarf to bring down, goblins with opinions about all of it.$B$BThere are a dozen paths through these woods. Only one ends with a very interesting troll. His name is Drakuru. He would like to be your friend, and he has cages that need filling.$B$BIf you would rather walk every one of those paths yourself, the woods will keep them for you.',
 'Speak with Moratari.', 0),
-- III-B: no skip. The dungeon and what is said at its top stay as they are.
(77302, 2, 39, 32, 394, 5, 0, 0, 0,
 'A Friend of Questionable Judgment',
 'Speak with Moratari at the door of Drak''Tharon Keep.',
 'Drakuru wants you to climb Drak''Tharon and cleanse it. He has been very helpful. Elixirs, visions, a great deal of encouragement, and never once has he asked for anything in return.$B$BI have a theory about your new friend. I sincerely hope the theory is wrong.$B$BGo in. Do what he asks; history needs you to. Only remember, when you reach the top, that a troll who speaks to you through smoke is still a troll you cannot see.',
 'Speak with Moratari.', 0),
-- WRM-321: the travel to Zul'Drak.
(77321, 2, 40, 32, 394, 5, 0, 0, 0,
 'The Truth About Drakuru',
 'Speak with Moratari again to travel to Light''s Breach in Zul''Drak.',
 'The Prophet Tharon''ja is dead, Drak''Tharon is clean, and Drakuru has thanked you very warmly through a cloud of smoke. He would like you to visit him in Zul''Drak. In person, this time.$B$BThe Drakkari empire is eating itself, $n. Its trolls kill their own gods for their power, and the Scourge is glad to help. The Argent Crusade holds Light''s Breach at its edge, and Crusader Lord Lantinga wants answers about what the Scourge is doing there. I suspect he will find a familiar name in them.$B$BChapter IV begins at Light''s Breach. The road there is long and uneventful; let us not take it.',
 'Speak with Moratari.', 0);

DELETE FROM `quest_template_addon` WHERE `ID` IN (77301, 77302, 77311, 77321);
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`) VALUES
(77301, 12249), (77311, 12236), (77302, 12068), (77321, 12238);

DELETE FROM `quest_offer_reward` WHERE `ID` IN (77301, 77302, 77311, 77321);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`, `VerifiedBuild`) VALUES
(77301, 1, 'Hold on. Samir will be delighted. Samir is always delighted.', 0),
(77311, 1, 'Hold on. Samir will be delighted. Samir is always delighted.', 0),
(77302, 1, 'Mind the stairs. And the trolls. And the troll.', 0),
(77321, 1, 'Hold on. Zul''Drak is warmer than the Grizzly Hills, and much less pleasant.', 0);

DELETE FROM `creature_queststarter` WHERE `quest` IN (77301, 77302, 77311, 77321);
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES
(@MORATARI, 77301), (@MORATARI, 77302), (@MORATARI, 77311), (@MORATARI, 77321);
DELETE FROM `creature_questender` WHERE `quest` IN (77301, 77302, 77311, 77321);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES
(@MORATARI, 77301), (@MORATARI, 77302), (@MORATARI, 77311), (@MORATARI, 77321);

DELETE FROM `remix_bridge` WHERE `quest` IN (77301, 77302, 77311, 77321);
INSERT INTO `remix_bridge` (`quest`, `next_quest`, `chapter`, `map`, `x`, `y`, `z`, `o`, `skipped`) VALUES
-- Before Samir, facing him.
(77301, 11984, 3, 571, 3849.4, -1958.8, 208.5, 5.29, '12210'),
(77311, 11984, 3, 571, 3849.4, -1958.8, 208.5, 5.29, '12208'),
-- At the door: nothing skipped, nowhere to go.
(77302, 12238, 3, 65535, 0, 0, 0, 0, ''),
-- Before Crusader Lord Lantinga, facing him (In Search Of Answers, both sides).
(77321, 12902, 4, 571, 5149.1, -2206.5, 236.6, 2.57, '');

-- Filling the Cages opens with III-A or Drakuru's breadcrumbs, Troll Season! (Alliance) and Good
-- Troll Hunting (Horde): their NextQuestID made those its only ways in; the conditions say it now.
UPDATE `quest_template_addon` SET `NextQuestID` = 0 WHERE `ID` IN (12208, 12210);
DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 19 AND `SourceEntry` = 11984;
INSERT INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`, `ConditionTypeOrReference`,
  `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`, `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`) VALUES
(19, 0, 11984, 0, 0, 8, 0, 77301, 0, 0, 0, 0, 0, '', 'Wrath Remix: Filling the Cages after A Shorter Path Through the Woods (Alliance)'),
(19, 0, 11984, 0, 1, 8, 0, 77311, 0, 0, 0, 0, 0, '', 'Wrath Remix: ... or the Horde''s'),
(19, 0, 11984, 0, 2, 8, 0, 12210, 0, 0, 0, 0, 0, '', 'Wrath Remix: ... or after Troll Season!'),
(19, 0, 11984, 0, 3, 8, 0, 12208, 0, 0, 0, 0, 0, '', 'Wrath Remix: ... or after Good Troll Hunting');

DELETE FROM `remix_quest_reward` WHERE `quest` IN (77301, 77302, 77311, 77321);
INSERT INTO `remix_quest_reward` (`quest`, `bronze`) VALUES
(77301, 800), (77311, 800), (77302, 500), (77321, 1500);

-- After the turn (STORY.md, Chapter III): Alleria's chapter. Eternus's agents have set Temporal
-- Anchors around Ursoc's Den, to wind the Bear God back to before Vordrassil's roots reached what
-- lies beneath; she has heard that voice's cousins, and knows it will only find another ear.
--
--   WRM-303  Alliance  Alleria, beside Hierophant Thayreen once Vordrassil's Sapling (12248) is
--                      done: break three Temporal Anchors, then Alleria at Ursoc's Den.
--   WRM-313  Horde     the same, beside Windseer Grayhorn once The Bear God's Offspring (12231) is.
--   Ursoc, the Bear God (12249, 12236) waits for it.
--
-- Its scenes (wrath_remix_world_0014_scenes.sql): Alleria as it's taken, and again beside the
-- Bear God's quest giver as Ursoc's quest is turned in. Spawns 7704310 to 7704329.

SET @ALLERIA_ABROAD := 770015, @ANCHOR := 770042, @REWINDER := 770043;

DELETE FROM `quest_template` WHERE `ID` IN (77303, 77313);
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `RewardXPDifficulty`, `RewardMoney`, `Flags`,
  `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `QuestCompletionLog`,
  `RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `ObjectiveText1`, `VerifiedBuild`) VALUES
(77303, 2, 40, 32, 394, 5, 0, 0, 1101,
 'The Hollow Crown',
 'Break 3 Temporal Anchors around Ursoc''s Den, then speak with Alleria Windrunner there.',
 'You felt it too, didn''t you? No. You wouldn''t have. Not yet.$B$BEternus''s agents have set Temporal Anchors around Ursoc''s Den. Stand with me a moment, $n, and I will tell you why that frightens me.$B$BFor the world''s sake. Do not flatter yourself.',
 'Speak with Alleria Windrunner at Ursoc''s Den.', @ANCHOR, 3, 'Temporal Anchor broken', 0),
(77313, 2, 40, 32, 394, 5, 0, 0, 690,
 'The Hollow Crown',
 'Break 3 Temporal Anchors around Ursoc''s Den, then speak with Alleria Windrunner there.',
 'You felt it too, didn''t you? No. You wouldn''t have. Not yet.$B$BEternus''s agents have set Temporal Anchors around Ursoc''s Den. Stand with me a moment, $n, and I will tell you why that frightens me.$B$BFor the world''s sake. Do not flatter yourself.',
 'Speak with Alleria Windrunner at Ursoc''s Den.', @ANCHOR, 3, 'Temporal Anchor broken', 0);

DELETE FROM `quest_template_addon` WHERE `ID` IN (77303, 77313);
-- (The Alliance's opens with Vordrassil's Sapling turned in, as a condition below: as its
-- PrevQuestID, the core would ask for all of the Sapling's exclusive group, -12248, too.)
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`) VALUES (77303, 0), (77313, 12231);

DELETE FROM `quest_offer_reward` WHERE `ID` IN (77303, 77313);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`, `VerifiedBuild`) VALUES
(77303, 1, 'That''s the last of them. Feel that? No, of course you don''t. The hills just went quiet again, the way a room goes quiet when something in it stops pretending to sleep.$B$B<She looks you over for wounds, finds none worth mentioning, and mentions one anyway.>$B$BClean that before it festers. I am not asking.$B$BHierophant Thayreen is waiting for you. Do what you came here to do, and do it kindly. Ursoc did not choose what happened to him.', 0),
(77313, 1, 'That''s the last of them. Feel that? No, of course you don''t. The hills just went quiet again, the way a room goes quiet when something in it stops pretending to sleep.$B$B<She looks you over for wounds, finds none worth mentioning, and mentions one anyway.>$B$BClean that before it festers. I am not asking.$B$BWindseer Grayhorn is waiting for you. Do what you came here to do, and do it kindly. Ursoc did not choose what happened to him.', 0);

DELETE FROM `creature_queststarter` WHERE `quest` IN (77303, 77313);
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES (@ALLERIA_ABROAD, 77303), (@ALLERIA_ABROAD, 77313);
DELETE FROM `creature_questender` WHERE `quest` IN (77303, 77313);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES (@ALLERIA_ABROAD, 77303), (@ALLERIA_ABROAD, 77313);

-- Ursoc, the Bear God waits for The Hollow Crown, which waits for Vordrassil's Sapling.
DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 19 AND `SourceEntry` IN (12249, 12236, 77303);
INSERT INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`, `ConditionTypeOrReference`,
  `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`, `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`) VALUES
(19, 0, 12249, 0, 0, 8, 0, 77303, 0, 0, 0, 0, 0, '', 'Wrath Remix: Ursoc, the Bear God after The Hollow Crown'),
(19, 0, 12236, 0, 0, 8, 0, 77313, 0, 0, 0, 0, 0, '', 'Wrath Remix: Ursoc, the Bear God after The Hollow Crown'),
(19, 0, 77303, 0, 0, 8, 0, 12248, 0, 0, 0, 0, 0, '', 'Wrath Remix: The Hollow Crown after Vordrassil''s Sapling');

-- Alleria beside Thayreen and Grayhorn (a step to their right), and at Ursoc's Den beside Tur
-- Ragepaw; the anchors around the den's mouth, where the maulers wander, each with a Rewinder.
DELETE FROM `creature` WHERE `guid` BETWEEN 7704310 AND 7704329;
INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `equipment_id`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`)
SELECT 7704310 + n, @ALLERIA_ABROAD, c.`map`, 1, c.`phaseMask`, 0,
  c.`position_x` + 2.5 * COS(c.`orientation` - PI() / 2), c.`position_y` + 2.5 * SIN(c.`orientation` - PI() / 2),
  c.`position_z`, c.`orientation`, 60, 0, 0, CONCAT('Wrath Remix: Alleria Windrunner, ', what)
FROM `creature` c JOIN (
  SELECT 0 AS n, 110818 AS beside, 'WRM-303, Amberpine Lodge (Hierophant Thayreen)' AS what UNION ALL
  SELECT 1, 107481, 'WRM-313, Conquest Hold (Windseer Grayhorn)' UNION ALL
  SELECT 2, 114077, 'WRM-303 and WRM-313, Ursoc''s Den (Tur Ragepaw)'
) b ON c.`guid` = b.beside;
INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `equipment_id`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(7704315, @ANCHOR,   571, 1, 1, 0, 4681.5, -3853.0, 327.4, 0, 180, 0, 0, 'Wrath Remix: Temporal Anchor, Ursoc''s Den'),
(7704316, @ANCHOR,   571, 1, 1, 0, 4694.0, -3866.5, 327.4, 0, 180, 0, 0, 'Wrath Remix: Temporal Anchor, Ursoc''s Den'),
(7704317, @ANCHOR,   571, 1, 1, 0, 4700.0, -3845.0, 327.4, 0, 180, 0, 0, 'Wrath Remix: Temporal Anchor, Ursoc''s Den'),
(7704318, @REWINDER, 571, 1, 1, 0, 4684.5, -3857.0, 327.4, 2.40, 180, 0, 0, 'Wrath Remix: Infinite Rewinder, Ursoc''s Den'),
(7704319, @REWINDER, 571, 1, 1, 0, 4690.0, -3870.0, 327.4, 1.20, 180, 0, 0, 'Wrath Remix: Infinite Rewinder, Ursoc''s Den'),
(7704320, @REWINDER, 571, 1, 1, 0, 4697.0, -3849.0, 327.4, 3.90, 180, 0, 0, 'Wrath Remix: Infinite Rewinder, Ursoc''s Den');

-- Who is seen where: Alleria at the lodges from the chain's last quest until The Hollow Crown is
-- turned in, at the den while it's being done; the anchors and their Rewinders while it is.
DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 30 AND (`SourceId` BETWEEN 7704310 AND 7704329 OR `SourceEntry` IN (@ANCHOR, @REWINDER));
INSERT INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`, `ConditionTypeOrReference`,
  `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`, `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`) VALUES
(30, 0, @ALLERIA_ABROAD, 7704310, 0, 8, 0, 12248, 0, 0, 0, 0, 0, '', 'Wrath Remix: Alleria at Amberpine Lodge after Vordrassil''s Sapling'),
(30, 0, @ALLERIA_ABROAD, 7704310, 0, 8, 0, 77303, 0, 0, 1, 0, 0, '', 'Wrath Remix: ... until The Hollow Crown'),
(30, 0, @ALLERIA_ABROAD, 7704311, 0, 8, 0, 12231, 0, 0, 0, 0, 0, '', 'Wrath Remix: Alleria at Conquest Hold after The Bear God''s Offspring'),
(30, 0, @ALLERIA_ABROAD, 7704311, 0, 8, 0, 77313, 0, 0, 1, 0, 0, '', 'Wrath Remix: ... until The Hollow Crown'),
(30, 0, @ALLERIA_ABROAD, 7704312, 0, 47, 0, 77303, 10, 0, 0, 0, 0, '', 'Wrath Remix: Alleria at Ursoc''s Den during The Hollow Crown'),
(30, 0, @ALLERIA_ABROAD, 7704312, 1, 47, 0, 77313, 10, 0, 0, 0, 0, '', 'Wrath Remix: ... the Horde''s'),
(30, 0, @ANCHOR, 0, 0, 47, 0, 77303, 8, 0, 0, 0, 0, '', 'Wrath Remix: the Temporal Anchors, for The Hollow Crown'),
(30, 0, @ANCHOR, 0, 1, 47, 0, 77313, 8, 0, 0, 0, 0, '', 'Wrath Remix: ... the Horde''s'),
(30, 0, @REWINDER, 0, 0, 47, 0, 77303, 8, 0, 0, 0, 0, '', 'Wrath Remix: the Rewinders, for The Hollow Crown'),
(30, 0, @REWINDER, 0, 1, 47, 0, 77313, 8, 0, 0, 0, 0, '', 'Wrath Remix: ... the Horde''s');

DELETE FROM `remix_quest_reward` WHERE `quest` IN (77303, 77313);
INSERT INTO `remix_quest_reward` (`quest`, `bronze`) VALUES (77303, 2500), (77313, 2500);
