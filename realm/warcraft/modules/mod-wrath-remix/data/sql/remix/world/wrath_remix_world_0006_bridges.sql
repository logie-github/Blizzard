-- Chapter I, The Northrend Invasion (STORY.md): the Borean Tundra for both sides, Howling Fjord for
-- whoever goes there. Until the turn in Chapter II, Moratari's transitions are Eternus's: she has
-- read the war, and folds the road to where she means to change it. Each is a new quest from
-- Moratari standing by the giver of the original quest it follows (wrath_remix_world_0004_spawns.sql),
-- standing for a block of original quests: the next original quest opens with either the
-- transition or the block's own last quest, so nothing is ever marked done that wasn't, and a
-- Timerunner who'd rather do the block still can. Ids from the world database
-- (data/campaign_manifest.csv, tools/quest_audit.py).
--
-- Eternus's first kindness, on each side (WRM-017, WRM-018): a squad history lost, saved. Each opens
-- the chain's next quest. The Alliance's then goes on to Mark Hanes (WRM-019), whose Word on the
-- Street the game leaves to be found.
--
-- Since build 91, Moratari's interventions (wrath_remix_world_0027_moratari.sql) sit in these chains:
-- WRM-006 follows William Allerton's testimony (he is alive) and leads to Unit S's rescue (WRM-045)
-- before Thassarian; Mobu's two parts quests are back on the Horde's road (WRM-016 is gone: the
-- Timerunner knows where the parts are).
--
-- (Until build 90, wrath_remix_world_0003_prologue.sql's deletes of the first prologue's quests,
-- 77001 to 77009, took the Alliance's transition, 77006, out whenever that file changed and this
-- one didn't: this note makes this file change too, so it comes back.)

SET @MORATARI := 770001, @MARK_HANES := 26155;

DELETE FROM `quest_template` WHERE `ID` IN (77006, 77016, 77026, 77121, 77122, 77123, 77124);
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `RewardXPDifficulty`, `RewardMoney`, `Flags`,
  `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `QuestCompletionLog`, `VerifiedBuild`) VALUES
-- Alliance, Borean Tundra: Leryssa's search for her brother, from William Allerton's house to the
-- siege where Thassarian is found.
(77006, 2, 15, 10, 3537, 5, 0, 0, 1101,
 'A Useful Omission',
 'Speak with Moratari again to go where Thassarian''s trail ends.',
 'Thassarian is alive, and William has told you where they sent him. The rest of the road is a borrowed ledger, a barrel of wine, a deserter, a coward or two, and a tuskarr with a grudge, and every step of it ends where William''s story already did: at Death''s Stand.$B$BCorporal Venn is holding out there, and Thassarian is just beyond. Let me fold the road.$B$BIf you would rather walk every step yourself, the road is still there.',
 'Speak with Moratari.', 0),
-- Alliance, Howling Fjord: Scout Knowles' missions and the drunken plan that ends at Mission:
-- Plague This!, before Operation: Skornful Wrath.
(77026, 2, 16, 10, 495, 5, 0, 0, 1101,
 'A Useful Omission',
 'Speak with Moratari again to be ready for Operation: Skornful Wrath.',
 'Westguard Keep has a great many missions for a newcomer: eternal flames, retrieved packages, Forsaken papers, and a goblin''s plan that only works if everyone involved is very drunk. They all end in the same place: Captain Adams ready to take Skorn.$B$BEternus has read them. The captain is ready now.',
 'Speak with Moratari.', 0),
-- Into the Dragonblight: the end of each coast's chapter, where Eternus wants the Timerunner next.
(77121, 2, 20, 18, 3537, 5, 0, 0, 1101,
 'Into the Dragonblight',
 'Speak with Moratari again to travel to Wintergarde Keep.',
 'The landing holds. Eternus is pleased with you, and so, I find, am I.$B$BShe wants you inland, where the war turns: Wintergarde Keep, in the Dragonblight. Naxxramas floats over it, and High Commander Wyrmbane is about to learn exactly what that means. There is a great deal there Eternus would like to change. Let us not keep her waiting.',
 'Speak with Moratari.', 0),
(77122, 2, 20, 18, 3537, 5, 0, 0, 690,
 'Into the Dragonblight',
 'Speak with Moratari again to travel to Agmar''s Hammer.',
 'The landing holds. Eternus is pleased with you, and so, I find, am I.$B$BShe wants you inland, where the war turns: Agmar''s Hammer, in the Dragonblight. The Horde is pushing toward the gate of Icecrown, and Overlord Agmar believes victory is near. Eternus believes she can make it so. Let us not keep her waiting.',
 'Speak with Moratari.', 0),
(77123, 2, 20, 18, 495, 5, 0, 0, 1101,
 'Into the Dragonblight',
 'Speak with Moratari again to travel to Wintergarde Keep.',
 'Skorn is taken. The fjord is not where the war will be decided, though, and Eternus wants you where it is.$B$BWintergarde Keep, in the Dragonblight. Naxxramas floats over it, and High Commander Wyrmbane is about to learn exactly what that means. Let us not keep her waiting.',
 'Speak with Moratari.', 0),
(77124, 2, 20, 18, 495, 5, 0, 0, 690,
 'Into the Dragonblight',
 'Speak with Moratari again to travel to Agmar''s Hammer.',
 'The apothecaries'' work here is finished, and I would rather not think about what it is for. Eternus, I suspect, thinks about little else.$B$BAgmar''s Hammer, in the Dragonblight. The Horde is pushing toward the gate of Icecrown, and Eternus wants you there. Let us not keep her waiting.',
 'Speak with Moratari.', 0);

DELETE FROM `quest_template_addon` WHERE `ID` IN (77006, 77016, 77026, 77121, 77122, 77123, 77124);
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`) VALUES
(77006, 11599), (77026, 11291),
(77121, 12019), (77122, 11652), (77123, 11250), (77124, 11310);

DELETE FROM `quest_offer_reward` WHERE `ID` IN (77006, 77016, 77026, 77121, 77122, 77123, 77124);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`, `VerifiedBuild`) VALUES
(77006, 1, 'I think our records can survive without another afternoon of interviews. Hold on to something.', 0),
(77026, 1, 'The captain is ready. So, I suspect, are you.', 0),
(77121, 1, 'Hold on. The Dragonblight is cold even for Northrend.', 0),
(77122, 1, 'Hold on. The Dragonblight is cold even for Northrend.', 0),
(77123, 1, 'Hold on. The Dragonblight is cold even for Northrend.', 0),
(77124, 1, 'Hold on. The Dragonblight is cold even for Northrend.', 0);

DELETE FROM `creature_queststarter` WHERE `quest` IN (77006, 77016, 77026, 77121, 77122, 77123, 77124);
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES
(@MORATARI, 77006), (@MORATARI, 77026),
(@MORATARI, 77121), (@MORATARI, 77122), (@MORATARI, 77123), (@MORATARI, 77124);
DELETE FROM `creature_questender` WHERE `quest` IN (77006, 77016, 77026, 77121, 77122, 77123, 77124);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES
(@MORATARI, 77006), (@MORATARI, 77026),
(@MORATARI, 77121), (@MORATARI, 77122), (@MORATARI, 77123), (@MORATARI, 77124);

-- (its own rows: the later chapters' files have theirs)
DELETE FROM `remix_bridge` WHERE `quest` IN (77006, 77016, 77026, 77121, 77122, 77123, 77124);
INSERT INTO `remix_bridge` (`quest`, `next_quest`, `chapter`, `map`, `x`, `y`, `z`, `o`, `skipped`) VALUES
-- Before Corporal Venn (Unit S's rescue, then Thassarian, the Death Knight).
(77006, 77045, 1, 571, 3116.4, 3841.8, 23.3, 2.60, '11600 11601 11603 11604 11932 12086 11944'),
(77026, 11248, 1, 65535, 0, 0, 0, 0, '11199 11202 11327 11328 11330 11331 11332'),
-- Before High Commander Halford Wyrmbane, and Overlord Agmar.
(77121, 12235, 2, 571, 3764.6, -772.4, 196.1, 5.54, ''),
(77122, 12034, 2, 571, 3842.4, 1489.6, 92.1, 4.71, ''),
(77123, 12235, 2, 571, 3764.6, -772.4, 196.1, 5.54, ''),
(77124, 12034, 2, 571, 3842.4, 1489.6, 92.1, 4.71, '');

-- The next original quest opens with either the transition or the block's own end. (Mobu's two parts
-- quests open Tanks a lot... again as the game has them: both, NextQuestID 11651 with
-- ExclusiveGroup -11643.)
UPDATE `quest_template_addon` SET `PrevQuestID` = 0 WHERE `ID` IN (12088, 11248);
UPDATE `quest_template_addon` SET `NextQuestID` = 11651 WHERE `ID` IN (11643, 11644);
DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 19 AND `SourceEntry` IN (12088, 11651, 11248);
INSERT INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`, `ConditionTypeOrReference`,
  `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`, `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`) VALUES
(19, 0, 12088, 0, 0, 8, 0, 77045, 0, 0, 0, 0, 0, '', 'Wrath Remix: Thassarian, the Death Knight after No One Left Behind (Unit S''s rescue)'),
(19, 0, 12088, 0, 1, 8, 0, 11944, 0, 0, 0, 0, 0, '', 'Wrath Remix: ... or after Surrounded!'),
(19, 0, 11248, 0, 0, 8, 0, 77026, 0, 0, 0, 0, 0, '', 'Wrath Remix: Operation: Skornful Wrath after A Useful Omission'),
(19, 0, 11248, 0, 1, 8, 0, 11332, 0, 0, 0, 0, 0, '', 'Wrath Remix: ... or after Mission: Plague This!');

-- Eternus's first kindness: a squad history lost, saved before it is lost. Moratari by the giver of
-- the last quest it follows (Sergeant Hammerhill, Overlord Razgor); the chain's next quest opens
-- after it. The Alliance's Word on the Street is Mark Hanes's, a little way off, which the game
-- leaves to be found: Moratari sends the Timerunner to him (WRM-019).
DELETE FROM `quest_template` WHERE `ID` IN (77017, 77018, 77019);
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `RewardXPDifficulty`, `RewardMoney`, `Flags`,
  `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `QuestCompletionLog`,
  `RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `ObjectiveText1`, `VerifiedBuild`) VALUES
(77017, 2, 16, 10, 3537, 5, 0, 0, 1101,
 'A Kindness Out of Time',
 'Slay 8 Crypt Crawlers on the beach below Valiance Keep, then return to Moratari.',
 'Eternus has her first kindness for you, $n.$B$BThe beach below the keep is quieter now, thanks to you. It does not stay quiet. Tonight a squad of the keep''s footmen goes down to the shore to clear the last of the crypt crawlers, and in the record I have, none of them come back up. Within the week they are wearing Scourge colors.$B$BClear the crawlers before the squad goes down, and they will not need to. It is a small change. Eternus believes small changes are where history is kindest.',
 'Return to Moratari.',
 25227, 8, '', 0),
(77018, 2, 16, 10, 3537, 5, 0, 0, 690,
 'A Kindness Out of Time',
 'Slay 8 Nerub''ar at Mightstone Quarry, then return to Moratari.',
 'Eternus has her first kindness for you, $n.$B$BMightstone Quarry is the Horde''s again, but the nerubians beneath it are not finished. Tomorrow a Warsong patrol goes into the tunnels after them, and in the record I have, the patrol''s names end up on the walls of Warsong Hold with a line through them. Some of them come back. Not as orcs.$B$BThin the Nerub''ar before the patrol goes in, and the patrol comes home. It is a small change. Eternus believes small changes are where history is kindest.',
 'Return to Moratari.',
 25382, 8, 'Nerub''ar slain', 0),
(77019, 2, 16, 10, 3537, 3, 0, 0, 1101,
 'Word at the Gate',
 'Speak with Mark Hanes at Valiance Keep.',
 'Valiance Keep has been asking after you, it seems. Mark Hanes, just inside the gate, has word of someone you will want to meet: a woman searching for her brother.$B$BHer brother is a death knight. History cares about him a great deal, and so, I promise you, will you. Go and hear Mark out.',
 'Speak with Mark Hanes.',
 0, 0, '', 0);

DELETE FROM `quest_template_addon` WHERE `ID` IN (77017, 77018, 77019);
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`) VALUES
(77017, 11897), (77018, 11602), (77019, 77017);

DELETE FROM `quest_request_items` WHERE `ID` IN (77017, 77018);
INSERT INTO `quest_request_items` (`ID`, `EmoteOnComplete`, `EmoteOnIncomplete`, `CompletionText`, `VerifiedBuild`) VALUES
(77017, 1, 1, 'Is the beach clear?', 0),
(77018, 1, 1, 'Is it done?', 0);

DELETE FROM `quest_offer_reward` WHERE `ID` IN (77017, 77018, 77019);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`, `VerifiedBuild`) VALUES
(77017, 1, 'Then tonight the squad comes back up. Somewhere in the record a page has changed, and nobody but us will ever know it was different.$B$BI will admit it feels good. Eternus says it is supposed to.', 0),
(77018, 1, 'Then the patrol comes home. Somewhere in the record a page has changed, and nobody but us will ever know it was different.$B$BI will admit it feels good. Eternus says it is supposed to.$B$BOverlord Razgor has your next orders.', 0),
(77019, 1, 'Moratari''s friend? Good. I''ve a woman down at the docks who won''t stop asking every soldier off every boat the same question, and I think you might be the one to answer it.', 0);

DELETE FROM `creature_queststarter` WHERE `quest` IN (77017, 77018, 77019);
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES
(@MORATARI, 77017), (@MORATARI, 77018), (@MORATARI, 77019);
DELETE FROM `creature_questender` WHERE `quest` IN (77017, 77018, 77019);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES
(@MORATARI, 77017), (@MORATARI, 77018), (@MARK_HANES, 77019);

-- The chain goes on after the kindness: Word on the Street (Mark Hanes), Wind Master To'bor
-- (Overlord Razgor). As well as the quests before them, as the world has it.
DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 19 AND `SourceEntry` IN (11927, 11634);
INSERT INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`, `ConditionTypeOrReference`,
  `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`, `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`) VALUES
(19, 0, 11927, 0, 0, 8, 0, 77017, 0, 0, 0, 0, 0, '', 'Wrath Remix: Word on the Street after A Kindness Out of Time'),
(19, 0, 11634, 0, 0, 8, 0, 77018, 0, 0, 0, 0, 0, '', 'Wrath Remix: Wind Master To''bor after A Kindness Out of Time');

DELETE FROM `remix_quest_reward` WHERE `quest` IN (77017, 77018, 77019);
INSERT INTO `remix_quest_reward` (`quest`, `bronze`) VALUES
(77017, 800), (77018, 800), (77019, 200);

DELETE FROM `remix_quest_reward` WHERE `quest` IN (77006, 77016, 77026, 77121, 77122, 77123, 77124);
INSERT INTO `remix_quest_reward` (`quest`, `bronze`) VALUES
(77006, 800), (77026, 800), (77121, 1500), (77122, 1500), (77123, 1500), (77124, 1500);
