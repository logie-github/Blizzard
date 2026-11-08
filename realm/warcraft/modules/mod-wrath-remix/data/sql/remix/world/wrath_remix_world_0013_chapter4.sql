-- Moratari's transitions in Chapter IV, The Fallen Empire (the guide's bridges IV-A and IV-B, and
-- WRM-421), as the earlier chapters' are made (wrath_remix_world_0006_bridges.sql): a new quest from
-- Moratari by the ender of the original quest it follows (wrath_remix_world_0004_spawns.sql). The
-- guide keeps Infiltrating Voltarus, Disclosure and Betrayal, and the main beats of the loa's
-- story; the bridges stand for what lies between.
--
--   WRM-401  after The Ebon Watch (12884)              opens Infiltrating Voltarus (12661)  IV-A, the way in
--   WRM-402  after Infiltrating Voltarus (12661)       opens Sabotage (12676)               IV-A, the way to the end
--   WRM-403  after Precious Elemental Fluids (12510)   opens Preparations for the Underworld (12666)
--   WRM-404  after You Reap What You Sow (12685) and Betrayal (12713): opens The Gods Have Spoken (12729)  IV-B
--   WRM-421  after Gal'darah Must Pay (13096) and Betrayal: to Nesingwary Base Camp in Sholazar
--            Basin, Chapter V (Hemet Nesingwary himself, past the breadcrumbs that lead to him)
--
-- Every quest here is both sides'. WRM-401 skips the chokers' quests too (An Invitation, of
-- Sorts... and Darkness Calling: a Withered Troll's drop, item-started), and their way to
-- Voltarus; Reunited, the Voltarus quest of Darkness Calling's way, opens after it.

SET @MORATARI := 770001;

DELETE FROM `quest_template` WHERE `ID` IN (77401, 77402, 77403, 77404, 77421);
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `RewardXPDifficulty`, `RewardMoney`, `Flags`,
  `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `QuestCompletionLog`, `VerifiedBuild`) VALUES
(77401, 2, 45, 42, 66, 5, 0, 0, 0,
 'The Things the Scourge Remembers',
 'Speak with Moratari again to be ready to infiltrate Voltarus.',
 'The Ebon Blade wants a spy aboard Voltarus, and Drakuru wants a friend. Stefan Vadu has a plan for giving both of them you: a dead troll''s necklace, a meeting or two, a few errands for your new friend, a disguise stitched from things best not described.$B$BThe Scourge remembers everything, $n. Every order, every requisition, every corpse it has ever counted. What matters is not in its ledgers. It is aboard Voltarus, and the Ebon Blade is ready to send you there now.$B$BIf you would rather run every errand first, Drakuru will be glad of the help. He always is.',
 'Speak with Moratari.', 0),
(77402, 2, 46, 42, 66, 5, 0, 0, 0,
 'The Paperwork of Betrayal',
 'Speak with Moratari again to be ready to sabotage Voltarus.',
 'You are inside. Drakuru believes you are his, the Ebon Blade believes you are theirs, and both are about to ask a great deal of you: plague barrels, propaganda, quotas of the dead to fill.$B$BThe paperwork of betrayal is astonishingly thorough. Its consequences are far more interesting. Stefan Vadu is ready to bring Voltarus down around Drakuru''s ears. Let us skip to the sabotage.',
 'Speak with Moratari.', 0),
-- The loa: Har'koa's rescue (the mushrooms, Jin'Alai, Rhunok and his prophet, the way back to her).
(77403, 2, 47, 42, 66, 5, 0, 0, 0,
 'A Pilgrim''s Shortcut',
 'Speak with Moratari again to travel to Har''koa at Zim''Torga.',
 'The trolls of Zul''Drak are killing their own gods and drinking their blood. The gods still alive are hiding, wounded or furious, and every one of them would like a hero''s help: mushrooms, mixtures, a witch doctor, a temple to break into, a goddess''s children to save.$B$BI have read the whole pilgrimage. It ends with Har''koa alive and asking you for something far more dangerous than mushrooms. Let us begin there.$B$BIf you would rather walk the pilgrim''s road yourself, the altars are not going anywhere. That is rather the problem with altars.',
 'Speak with Moratari.', 0),
-- IV-B: the rest of the shrines (Warlord Zol'Maz's key, Mam'toth's rampage).
(77404, 2, 50, 42, 66, 5, 0, 0, 0,
 'The Gods Are Still Silent',
 'Speak with Moratari again to hear what the gods have to say.',
 'Drakuru is dead, and the Lich King came to Voltarus himself to see to it. The Drakkari''s gods are dying or dead, and their prophets are drinking what is left. There are more altars, of course: a warlord''s key, a mammoth god in a temper.$B$BWe have enough evidence to understand what became of the Drakkari. No need to disturb every altar to prove it. Khufu knows where the last of their prophets will gather; that is where this ends.',
 'Speak with Moratari.', 0),
(77421, 2, 52, 42, 66, 5, 0, 0, 0,
 'A Kingdom Gone',
 'Speak with Moratari again to travel to Nesingwary Base Camp in Sholazar Basin.',
 'Gal''darah is dead: the last of the Drakkari''s great prophets, and the last of their empire''s great mistakes. Gundrak is quiet.$B$BI have seen this kingdom at its height, $n. It was cruel, and proud, and magnificent, and it ate its own gods rather than kneel to the Lich King. I am not sure whether that makes it brave or only hungry. Either way, it is gone.$B$BSomething else is stirring in the west: a basin the titans tended, an old guardian''s warning, and a famous hunter Dalaran believes is lost in it. He is not lost. He is hunting. Chapter V begins at his camp.',
 'Speak with Moratari.', 0);

DELETE FROM `quest_template_addon` WHERE `ID` IN (77401, 77402, 77403, 77404, 77421);
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`) VALUES
(77401, 12884), (77402, 12661), (77403, 12510), (77404, 12685), (77421, 13096);

DELETE FROM `quest_offer_reward` WHERE `ID` IN (77401, 77402, 77403, 77404, 77421);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`, `VerifiedBuild`) VALUES
(77401, 1, 'Do try to look undead. It is mostly a matter of posture.', 0),
(77402, 1, 'Quietly, now. A necropolis is a terrible place to sneeze.', 0),
(77403, 1, 'Hold on. Har''koa is a cat: a very large, very divine cat. Mind your manners.', 0),
(77404, 1, 'Listen to the gods while they still have voices.', 0),
(77421, 1, 'Hold on. Sholazar is warm, green and full of things that want to eat you. You will love it.', 0);

DELETE FROM `creature_queststarter` WHERE `quest` IN (77401, 77402, 77403, 77404, 77421);
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES
(@MORATARI, 77401), (@MORATARI, 77402), (@MORATARI, 77403), (@MORATARI, 77404), (@MORATARI, 77421);
DELETE FROM `creature_questender` WHERE `quest` IN (77401, 77402, 77403, 77404, 77421);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES
(@MORATARI, 77401), (@MORATARI, 77402), (@MORATARI, 77403), (@MORATARI, 77404), (@MORATARI, 77421);

DELETE FROM `remix_bridge` WHERE `quest` IN (77401, 77402, 77403, 77404, 77421);
INSERT INTO `remix_bridge` (`quest`, `next_quest`, `chapter`, `map`, `x`, `y`, `z`, `o`, `skipped`) VALUES
-- At Stefan Vadu, who gives what follows: nowhere to go.
(77401, 12661, 4, 65535, 0, 0, 0, 0, '12631 12633 12637 12638 12629 12643 12648 12649'),
(77402, 12676, 4, 65535, 0, 0, 0, 0, '12669 12673 12677 12686'),
-- Before Har'koa at Zim'Torga, facing her.
(77403, 12666, 4, 571, 5746.8, -3606.8, 387.2, 4.54, '12514 12516 12623 12627 12628 12632 12642 12646 12647 12653 12665'),
-- At Witch Doctor Khufu, who gives what follows.
(77404, 12729, 4, 65535, 0, 0, 0, 0, '12712 12721'),
-- Before Hemet Nesingwary at his camp, facing him (the breadcrumbs that lead to him: Where in the
-- World is Hemet Nesingwary?, Welcome to Sholazar Basin, whose Monte Muzzleshot waits by a rare
-- that would greet a Timerunner landing there).
(77421, 0, 5, 571, 5582.5, 5748.6, -71.9, 0.11, '12521 12489');

-- IV-B and WRM-421 follow Drakuru's end as well (the guide: after the final Drakuru encounter).
DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 19 AND `SourceEntry` IN (77404, 77421, 12661, 12663, 12676, 12666, 12729);
-- Infiltrating Voltarus: IV-A or the disguise quests' ends (their NextQuestID, now conditions).
UPDATE `quest_template_addon` SET `NextQuestID` = 0 WHERE `ID` IN (12648, 12649);
-- Reunited (Darkness Calling's way's Voltarus quest) after Suit Up! or WRM-401; Dark Horizon
-- (the other way's) as it was. Both while Infiltrating Voltarus is in the log, as the world has it.
-- The others open with either the transition or the quest before them.
UPDATE `quest_template_addon` SET `PrevQuestID` = 0 WHERE `ID` IN (12663, 12676, 12666, 12729);
INSERT INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`, `ConditionTypeOrReference`,
  `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`, `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`) VALUES
(19, 0, 77404, 0, 0, 8, 0, 12713, 0, 0, 0, 0, 0, '', 'Wrath Remix: The Gods Are Still Silent after Betrayal'),
(19, 0, 77421, 0, 0, 8, 0, 12713, 0, 0, 0, 0, 0, '', 'Wrath Remix: A Kingdom Gone after Betrayal'),
(19, 0, 12661, 0, 0, 8, 0, 77401, 0, 0, 0, 0, 0, '', 'Wrath Remix: Infiltrating Voltarus after The Things the Scourge Remembers'),
(19, 0, 12661, 0, 1, 8, 0, 12648, 0, 0, 0, 0, 0, '', 'Wrath Remix: ... or after Dressing Down'),
(19, 0, 12661, 0, 2, 8, 0, 12649, 0, 0, 0, 0, 0, '', 'Wrath Remix: ... or after Suit Up!'),
(19, 0, 12663, 0, 0, 9, 0, 12661, 0, 0, 0, 0, 0, '', 'Quest acceptable only if player has taken quest Infiltrating Voltarus'),
(19, 0, 12663, 0, 0, 8, 0, 12649, 0, 0, 0, 0, 0, '', 'Wrath Remix: Reunited after Suit Up!'),
(19, 0, 12663, 0, 1, 9, 0, 12661, 0, 0, 0, 0, 0, '', 'Wrath Remix: ... or, Infiltrating Voltarus taken'),
(19, 0, 12663, 0, 1, 8, 0, 77401, 0, 0, 0, 0, 0, '', 'Wrath Remix: ... after The Things the Scourge Remembers'),
(19, 0, 12676, 0, 0, 8, 0, 77402, 0, 0, 0, 0, 0, '', 'Wrath Remix: Sabotage after The Paperwork of Betrayal'),
(19, 0, 12676, 0, 1, 8, 0, 12677, 0, 0, 0, 0, 0, '', 'Wrath Remix: ... or after Hazardous Materials'),
(19, 0, 12666, 0, 0, 8, 0, 77403, 0, 0, 0, 0, 0, '', 'Wrath Remix: Preparations for the Underworld after A Pilgrim''s Shortcut'),
(19, 0, 12666, 0, 1, 8, 0, 12665, 0, 0, 0, 0, 0, '', 'Wrath Remix: ... or after I Sense a Disturbance'),
(19, 0, 12729, 0, 0, 8, 0, 77404, 0, 0, 0, 0, 0, '', 'Wrath Remix: The Gods Have Spoken after The Gods Are Still Silent'),
(19, 0, 12729, 0, 1, 8, 0, 12721, 0, 0, 0, 0, 0, '', 'Wrath Remix: ... or after Rampage');

DELETE FROM `remix_quest_reward` WHERE `quest` IN (77401, 77402, 77403, 77404, 77421);
INSERT INTO `remix_quest_reward` (`quest`, `bronze`) VALUES
(77401, 600), (77402, 800), (77403, 800), (77404, 800), (77421, 1500);

-- After the turn (STORY.md, Chapter IV): Sylvanas's chapter. Eternus's agents are beneath Voltarus,
-- opening a rift to carry Drakuru out of history before the Lich King comes for him: and if the
-- Lich King never comes to Voltarus, he never sees the Timerunner, never decides they are worth
-- keeping for the end.
--
--   WRM-405  Sylvanas, beside Stefan Vadu at the Ebon Watch once Sabotage (12676) is done (taking it
--            goes beneath Voltarus, where she waits): six Infinite Timesnatchers and their Unstable
--            Rift; turned in to her there, and back to Stefan Vadu, whose Betrayal (12713) waits for
--            it. Spawns 7704220 to 7704239.

SET @SYLVANAS_ABROAD := 770014, @TIMESNATCHER := 770044, @RIFT := 770045;

DELETE FROM `quest_template` WHERE `ID` = 77405;
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `RewardXPDifficulty`, `RewardMoney`, `Flags`,
  `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `QuestCompletionLog`,
  `RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `RequiredNpcOrGo2`, `RequiredNpcOrGoCount2`, `ObjectiveText1`, `ObjectiveText2`, `VerifiedBuild`) VALUES
(77405, 2, 49, 42, 66, 5, 0, 0, 0,
 'One Life Too Many',
 'Slay 6 Infinite Timesnatchers and close the Unstable Rift beneath Voltarus, then speak with Sylvanas Windrunner there.',
 'Eternus has found another life to save. You will not like whose.$B$BListen, and then I will meet you beneath Voltarus. Do not keep me waiting; I have waited on trolls before.',
 'Speak with Sylvanas Windrunner beneath Voltarus.', @TIMESNATCHER, 6, @RIFT, 1, 'Infinite Timesnatcher slain', 'Unstable Rift closed', 0);

DELETE FROM `quest_template_addon` WHERE `ID` = 77405;
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`) VALUES (77405, 12676);

DELETE FROM `quest_offer_reward` WHERE `ID` = 77405;
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`, `VerifiedBuild`) VALUES
(77405, 1, 'Good. Now go and betray him. He has earned that much.$B$BWhen the Lich King comes for him, he will look at you. Look back. Remember his face. You will see it again, at the top of his citadel.$B$B<She hesitates.>$B$BBe careful on that necropolis, $n. I have grown used to you coming back. ...I will grow used to it. Do not ask.$B$BStefan Vadu is waiting. I will send you to him.', 0);

DELETE FROM `creature_queststarter` WHERE `quest` = 77405;
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES (@SYLVANAS_ABROAD, 77405);
DELETE FROM `creature_questender` WHERE `quest` = 77405;
INSERT INTO `creature_questender` (`id`, `quest`) VALUES (@SYLVANAS_ABROAD, 77405);

-- Taking it goes beneath Voltarus, before Sylvanas; turning it in goes back to Stefan Vadu.
CREATE TABLE IF NOT EXISTS `remix_departure` (
  `quest` INT UNSIGNED NOT NULL,
  `map` SMALLINT UNSIGNED NOT NULL,
  `x` FLOAT NOT NULL,
  `y` FLOAT NOT NULL,
  `z` FLOAT NOT NULL,
  `o` FLOAT NOT NULL,
  PRIMARY KEY (`quest`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
DELETE FROM `remix_departure` WHERE `quest` = 77405;
INSERT INTO `remix_departure` (`quest`, `map`, `x`, `y`, `z`, `o`) VALUES (77405, 571, 6099.0, -1930.0, 235.6, 2.40);
DELETE FROM `remix_bridge` WHERE `quest` = 77405;
INSERT INTO `remix_bridge` (`quest`, `next_quest`, `chapter`, `map`, `x`, `y`, `z`, `o`, `skipped`)
SELECT 77405, 12713, 4, c.`map`, c.`position_x` + 4 * COS(c.`orientation`), c.`position_y` + 4 * SIN(c.`orientation`),
  c.`position_z` + 0.5, MOD(c.`orientation` + PI(), 2 * PI()), ''
FROM `creature` c WHERE c.`guid` = 105125;

-- Betrayal waits for it.
DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 19 AND `SourceEntry` = 12713;
INSERT INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`, `ConditionTypeOrReference`,
  `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`, `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`) VALUES
(19, 0, 12713, 0, 0, 8, 0, 77405, 0, 0, 0, 0, 0, '', 'Wrath Remix: Betrayal after One Life Too Many');

-- Sylvanas at the Ebon Watch (a step to Stefan Vadu's right) and beneath Voltarus; the agents and
-- their rift on the ground below the necropolis, where its geists and vargul walk.
DELETE FROM `creature` WHERE `guid` BETWEEN 7704220 AND 7704239;
INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `equipment_id`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`)
SELECT 7704220, @SYLVANAS_ABROAD, c.`map`, 1, c.`phaseMask`, 0,
  c.`position_x` + 2.5 * COS(c.`orientation` - PI() / 2), c.`position_y` + 2.5 * SIN(c.`orientation` - PI() / 2),
  c.`position_z`, c.`orientation`, 60, 0, 0, 'Wrath Remix: Sylvanas Windrunner, WRM-405, the Ebon Watch (Stefan Vadu)'
FROM `creature` c WHERE c.`guid` = 105125;
INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `equipment_id`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(7704221, @SYLVANAS_ABROAD,     571, 1, 1, 0, 6095.3, -1926.8, 235.4, 5.60, 60, 0, 0, 'Wrath Remix: Sylvanas Windrunner, WRM-405, beneath Voltarus'),
(7704222, @TIMESNATCHER, 571, 1, 1, 0, 6121.4, -1936.6, 234.7, 3.50, 180, 0, 0, 'Wrath Remix: Infinite Timesnatcher, beneath Voltarus'),
(7704223, @TIMESNATCHER, 571, 1, 1, 0, 6123.2, -1974.4, 234.2, 2.80, 180, 0, 0, 'Wrath Remix: Infinite Timesnatcher, beneath Voltarus'),
(7704224, @TIMESNATCHER, 571, 1, 1, 0, 6090.2, -1983.8, 233.5, 1.20, 180, 0, 0, 'Wrath Remix: Infinite Timesnatcher, beneath Voltarus'),
(7704225, @TIMESNATCHER, 571, 1, 1, 0, 6124.1, -2007.8, 232.3, 1.90, 180, 0, 0, 'Wrath Remix: Infinite Timesnatcher, beneath Voltarus'),
(7704226, @TIMESNATCHER, 571, 1, 1, 0, 6166.3, -1965.4, 233.3, 3.60, 180, 0, 0, 'Wrath Remix: Infinite Timesnatcher, beneath Voltarus'),
(7704227, @TIMESNATCHER, 571, 1, 1, 0, 6176.5, -1970.2, 232.3, 3.40, 180, 0, 0, 'Wrath Remix: Infinite Timesnatcher, beneath Voltarus'),
(7704228, @TIMESNATCHER, 571, 1, 1, 0, 6145.1, -1986.2, 231.9, 2.60, 180, 0, 0, 'Wrath Remix: Infinite Timesnatcher, beneath Voltarus'),
(7704229, @RIFT,         571, 1, 1, 0, 6139.3, -1993.9, 231.9, 0,    180, 0, 0, 'Wrath Remix: Unstable Rift, beneath Voltarus');

DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 30 AND (`SourceId` BETWEEN 7704220 AND 7704239 OR `SourceEntry` IN (@TIMESNATCHER, @RIFT));
INSERT INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`, `ConditionTypeOrReference`,
  `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`, `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`) VALUES
(30, 0, @SYLVANAS_ABROAD, 7704220, 0, 8, 0, 12676, 0, 0, 0, 0, 0, '', 'Wrath Remix: Sylvanas at the Ebon Watch after Sabotage'),
(30, 0, @SYLVANAS_ABROAD, 7704220, 0, 47, 0, 77405, 1, 0, 0, 0, 0, '', 'Wrath Remix: ... until One Life Too Many is taken'),
(30, 0, @SYLVANAS_ABROAD, 7704221, 0, 47, 0, 77405, 10, 0, 0, 0, 0, '', 'Wrath Remix: Sylvanas beneath Voltarus during One Life Too Many'),
(30, 0, @TIMESNATCHER, 0, 0, 47, 0, 77405, 8, 0, 0, 0, 0, '', 'Wrath Remix: Eternus''s agents beneath Voltarus, for One Life Too Many'),
(30, 0, @RIFT, 0, 0, 47, 0, 77405, 8, 0, 0, 0, 0, '', 'Wrath Remix: their rift, for One Life Too Many');

DELETE FROM `remix_quest_reward` WHERE `quest` = 77405;
INSERT INTO `remix_quest_reward` (`quest`, `bronze`) VALUES (77405, 3500);
