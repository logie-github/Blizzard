-- Wrath Remix's prologue (STORY.md, "Prologue"): a new Timerunner, a veteran of the war against
-- the Lich King pulled out of a tavern in their own hour by Moratari, shown the war's end and its
-- cost (src/RemixIntro.cpp), arrives at the Infinite Bazaar in Malykriss: The Vile Hold,
-- Icecrown's unfinished necropolis, in the year the war began. Eternus tells them plainly what she wants and how it is done;
-- then, one thing at a time, Bronze and Alurmi, their class's instructor and lesson, the Bazaar's
-- keepers, the hourglass and the hearthstone, the anomalies; and the war's first day, in the
-- Borean Tundra. Each quest is given where the last one ended. WRM-nnn is quest 77nnn.

SET @MORATARI := 770001, @ETERNUS := 770002, @ALURMI := 770005,
    @ECHO_FOOTMAN := 770021, @ECHO_SAURFANG := 770022, @ECHO_BOLVAR := 770023,
    @ANOMALY_CREDIT := 770032, @INSTRUCTOR_CREDIT := 770033;

-- Every new character but a death knight wakes at the Bazaar, before Eternus and Moratari (death
-- knights keep Acherus and their own story; the module brings them to the Bazaar after it). The
-- world server sets it again in its own copy as it starts (src/RemixIntro.cpp): mod-skyborne's SQL,
-- applied again whenever it changes, puts its races' start back where theirs was.
UPDATE `playercreateinfo` SET `map` = 571, `zone` = 4520, `position_x` = 6394.0, `position_y` = 1866.0,
  `position_z` = 508.7, `orientation` = 1.57 WHERE `class` <> 6;

-- Until build 56 Remix's quests were 7701nnn, which made the core keep a table of quests 7.7
-- million long (its fast lookups are indexed by id): gone, with everything that named them.
DELETE FROM `quest_template` WHERE `ID` BETWEEN 7701000 AND 7701999;
DELETE FROM `quest_template_addon` WHERE `ID` BETWEEN 7701000 AND 7701999;
DELETE FROM `quest_request_items` WHERE `ID` BETWEEN 7701000 AND 7701999;
DELETE FROM `quest_offer_reward` WHERE `ID` BETWEEN 7701000 AND 7701999;
DELETE FROM `creature_queststarter` WHERE `quest` BETWEEN 7701000 AND 7701999;
DELETE FROM `creature_questender` WHERE `quest` BETWEEN 7701000 AND 7701999;
DELETE FROM `remix_quest_reward` WHERE `quest` BETWEEN 7701000 AND 7701999;

-- The first prologue (WRM-001 to 007, in the Caverns of Time, until build 64): gone too. Not 77006,
-- which is Chapter I's Alliance transition now (wrath_remix_world_0006_bridges.sql): this file can
-- change on its own, and its deletes must not take that one out.
DELETE FROM `quest_template` WHERE `ID` BETWEEN 77001 AND 77009 AND `ID` <> 77006;
DELETE FROM `quest_template_addon` WHERE `ID` BETWEEN 77001 AND 77009 AND `ID` <> 77006;
DELETE FROM `quest_request_items` WHERE `ID` BETWEEN 77001 AND 77009 AND `ID` <> 77006;
DELETE FROM `quest_offer_reward` WHERE `ID` BETWEEN 77001 AND 77009 AND `ID` <> 77006;
DELETE FROM `creature_queststarter` WHERE `quest` BETWEEN 77001 AND 77009 AND `quest` <> 77006;
DELETE FROM `creature_questender` WHERE `quest` BETWEEN 77001 AND 77009 AND `quest` <> 77006;
DELETE FROM `remix_quest_reward` WHERE `quest` BETWEEN 77001 AND 77009 AND `quest` <> 77006;

-- The prologue, one thing at a time: Moratari sends the Timerunner to Eternus (WRM-010), who
-- answers what she wants, how it is done and why them (WRM-011); Time's Toll and Bronze, at Alurmi's
-- stall (WRM-012); their class's instructor (WRM-020) and lesson (WRM-030 to 039,
-- wrath_remix_world_0025_lessons.sql); the Bazaar's keepers, the hourglass and the hearthstone
-- (WRM-021); the anomalies (WRM-013); and the front (WRM-014 / 015).
SET @PLAN_WHAT := 770049, @PLAN_HOW := 770050, @PLAN_WHY := 770058,
    @ZEPHYR := 770006, @SAAT := 770007, @CHRONOLOGIST := 770008;

DELETE FROM `quest_template` WHERE `ID` BETWEEN 77010 AND 77015 OR `ID` IN (77020, 77021);
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `RewardXPDifficulty`, `RewardMoney`, `Flags`,
  `AllowableRaces`, `RewardItem1`, `RewardAmount1`, `LogTitle`, `LogDescription`, `QuestDescription`, `QuestCompletionLog`,
  `RequiredNpcOrGo1`, `RequiredNpcOrGo2`, `RequiredNpcOrGo3`, `RequiredNpcOrGoCount1`, `RequiredNpcOrGoCount2`, `RequiredNpcOrGoCount3`,
  `ObjectiveText1`, `ObjectiveText2`, `ObjectiveText3`, `VerifiedBuild`) VALUES
(77010, 2, 10, 1, 210, 3, 0, 8, 0, 0, 0,
 'Out of Time',
 'Speak with Eternus at the heart of the Infinite Bazaar.',
 'This is the Infinite Bazaar, $n: Malykriss, the necropolis the Lich King began here in Icecrown and never finished. You may remember this place. You may remember creeping through it for the Ebon Blade, the riders, Orbaz Bloodbane. That never happens now. When we started cleaning up the timeline, the Scourge infestation here was one of the first things we took care of, and Malykriss is entirely ours: my flight''s, the Knights of the Ebon Blade who keep its gates, and the last free nerubians of Azjol-Nerub, who were building in saronite long before the Scourge stole the craft from them.$B$BOut there, the Alliance''s ships and the Horde''s zeppelins are only now reaching Northrend. The soldiers aboard them have no idea what is waiting for them. You do.$B$BGo and speak with Eternus. She has been looking forward to this.',
 'Speak with Eternus.',
 0, 0, 0, 0, 0, 0, '', '', '', 0),
(77011, 2, 10, 1, 210, 4, 0, 8, 0, 0, 0,
 'The Plan',
 'Ask Eternus what she wants of you, how it is to be done, and why she chose you.',
 'You have questions. Good. I would not trust anyone who came this far and had none.$B$BAsk me what I want, how it is to be done, and why it is you. I will answer each of them plainly. Then we begin.',
 'Speak with Eternus.',
 @PLAN_WHAT, @PLAN_HOW, @PLAN_WHY, 1, 1, 1,
 'Asked what she wants', 'Asked how it is done', 'Asked why you', 0),
(77012, 2, 10, 1, 210, 3, 0, 8, 0, 0, 0,
 'Time''s Toll',
 'Speak with Alurmi, at the head of the market lane on the camp''s west side.',
 'Time takes its toll on those who travel through it. You will feel weaker than the hero who sat in that tavern, because you are: most of what you could do has stayed behind, in your own hour. It comes back. Every day of this war, you will be stronger than the last.$B$BBronze will help. You will gather it as you go, and Alurmi trades it for gear that grows as you do. Hers is the first stall of the market, on the camp''s west side.',
 'Speak with Alurmi.',
 0, 0, 0, 0, 0, 0, '', '', '', 0),
(77020, 2, 10, 1, 210, 3, 0, 8, 0, 0, 0,
 'Old Habits',
 'Find your class''s Timeworn Instructor in the training yard, on the south-east side of the camp.',
 'Before you spend it, find your instructor, across the camp in the training yard to the south-east. There is one there for every kind of fighter, and the finest heirloom in my stall is wasted on someone who has forgotten what to do with it.$B$BWhen your instructor is done with you, Moratari will want you back.',
 'Speak with your class''s instructor.',
 0, 0, 0, 0, 0, 0, '', '', '', 0),
(77021, 2, 10, 1, 210, 3, 0, 8, 0, 0, 0,
 'The Bazaar''s Keepers',
 'Speak with Zephyr, Sa''at and the Chronologist, then return to Moratari.',
 'Your instructor tells me you will do.$B$BNow, the Bazaar. Zephyr keeps its roads, at the waystation to the north-east: she can send you to Dalaran, to the landings, and to the camp of any chapter your strength allows. Sa''at has his map table there too. He keeps watch over the dungeons and the raids, and will tell you when each is ready for you. The Chronologist, in the chronicle corner to the north-west, keeps the record of where you are in the war, and can take you back to the start of a chapter. Speak with all three.$B$BAnd the hourglass in your bag is mine. Turn it anywhere, and it brings you here. Turn it here, and it takes you back to wherever you were. Not in the middle of a fight, though: time is fussy about that.',
 'Return to Moratari.',
 @ZEPHYR, @SAAT, @CHRONOLOGIST, 1, 1, 1, 'Zephyr spoken to', 'Sa''at spoken to', 'The Chronologist spoken to', 0),
(77013, 2, 10, 1, 210, 4, 0, 8, 0, 41599, 2,
 'A Small Demonstration',
 'Defeat 3 Temporal Anomalies, then return to Moratari.',
 'Eternus wants to know you can survive the war before she sends you into it. So do I.$B$BTime does not like being changed. Where it is pulled on, it frays, and things come through the seams: anomalies. They are drawn to Timerunners, which is unfortunate for you and convenient for me.$B$BTell me when you are ready, and I will let three of them through. Not all at once; I would like you alive at the end of this.',
 'Return to Moratari.',
 @ANOMALY_CREDIT, 0, 0, 3, 0, 0, 'Temporal Anomaly defeated', '', '', 0),
(77014, 2, 10, 1, 210, 4, 0, 8, 1101, 0, 0,
 'To the Front',
 'Speak with Eternus to be sent to Valiance Keep in the Borean Tundra.',
 'The war begins on the shore, $n, and so do you.$B$BThe Alliance''s fleet has put in at Valiance Keep, in the Borean Tundra, and the Scourge was there to meet it. Eternus will fold the road for you. When you arrive, enlist: Recruitment Officer Blythe is signing up every sword that comes off the boats.$B$BI will be there before you. I usually am.',
 'Speak with Eternus.',
 0, 0, 0, 0, 0, 0, '', '', '', 0),
(77015, 2, 10, 1, 210, 4, 0, 8, 690, 0, 0,
 'To the Front',
 'Speak with Eternus to be sent to Warsong Hold in the Borean Tundra.',
 'The war begins at Warsong Hold, $n, and so do you.$B$BThe zeppelins from Orgrimmar are coming in over the Borean Tundra, and the Scourge is already at the Hold''s walls. Garrosh Hellscream would much rather be marching than holding them. Eternus will fold the road for you. When you arrive, report to the Warsong Recruitment Officer at the zeppelin landing.$B$BI will be there before you. I usually am.',
 'Speak with Eternus.',
 0, 0, 0, 0, 0, 0, '', '', '', 0);

-- One after another; none for death knights, who arrive later and by their own road. After Old
-- Habits, the class's lesson; whichever lesson it was opens the Bazaar's Keepers (each lesson's
-- NextQuestID, in wrath_remix_world_0025_lessons.sql).
DELETE FROM `quest_template_addon` WHERE `ID` BETWEEN 77010 AND 77015 OR `ID` IN (77020, 77021);
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`, `AllowableClasses`) VALUES
(77010, 0, 1503), (77011, 77010, 1503), (77012, 77011, 1503), (77020, 77012, 1503), (77021, 0, 1503),
(77013, 77021, 1503), (77014, 77013, 1503), (77015, 77013, 1503);

DELETE FROM `quest_request_items` WHERE `ID` BETWEEN 77010 AND 77015 OR `ID` IN (77020, 77021);
INSERT INTO `quest_request_items` (`ID`, `EmoteOnComplete`, `EmoteOnIncomplete`, `CompletionText`, `VerifiedBuild`) VALUES
(77011, 1, 1, 'Ask whatever you need. Here, at least, there is time.', 0),
(77021, 1, 1, 'Met them all? They are odd, but they are ours.', 0),
(77013, 1, 1, 'Is that all of them? Look behind you before you answer.', 0);

DELETE FROM `quest_offer_reward` WHERE `ID` BETWEEN 77010 AND 77015 OR `ID` IN (77020, 77021);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`, `VerifiedBuild`) VALUES
(77010, 1, 'So Moratari has found you. Welcome, $n.$B$BYou have seen what this war costs, and you paid your share of it. You won anyway. Most would call that enough.$B$BI am Eternus, of the Infinite Dragonflight. My kind are said to want time broken. I want it mended. Ask me what you will.', 0),
(77011, 1, 'Now you know what I know, or as much of it as will help you.$B$BThere is a price for coming here, and you should hear it from me.', 0),
(77012, 1, 'Eternus sent you? Then you will want an heirloom. Buy it once, and it keeps pace with you all the way to Icecrown.$B$BHere is some Bronze to start. My lists will be here when you are ready to choose.', 0),
(77020, 1, 'There you are. Every Timerunner finds this yard sooner or later, looking for the fighter they were. Let us see how much of yours came through.', 0),
(77021, 1, 'Now you know your way around. Your hearthstone remembers the Bazaar, too: it is your home between battles now.$B$BBefore I let you anywhere near the war, though, I want to see you fight.', 0),
(77013, 4, 'There. You are stronger than you were an hour ago, which is the whole point of you.$B$BTake these bags: you will carry a great deal of the war home with you. And the Bronze: Alurmi will be glad to see it. When you are ready, Eternus will send you to the front.', 0),
(77014, 1, 'The first day of the war. You have stood on that beach once already, $n; this time, you know what is coming.$B$BKeep it to yourself. When something can be done better, find a reason anyone would believe, and do it.$B$BGo well. Every one you save is one I will not have to mourn again.', 0),
(77015, 1, 'The first day of the war. You have stood on those walls once already, $n; this time, you know what is coming.$B$BKeep it to yourself. When something can be done better, find a reason anyone would believe, and do it.$B$BGo well. Every one you save is one I will not have to mourn again.', 0);

DELETE FROM `creature_queststarter` WHERE `quest` BETWEEN 77010 AND 77015 OR `quest` IN (77020, 77021);
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES
(@MORATARI, 77010), (@ETERNUS, 77011), (@ETERNUS, 77012), (@ALURMI, 77020), (@MORATARI, 77021), (@MORATARI, 77013),
(@MORATARI, 77014), (@MORATARI, 77015);

-- Old Habits ends at the Timerunner's own class's instructor (the others don't take it: their
-- script hides it, src/RemixNpcs.cpp).
DELETE FROM `creature_questender` WHERE `quest` BETWEEN 77010 AND 77015 OR `quest` IN (77020, 77021);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES
(@ETERNUS, 77010), (@ETERNUS, 77011), (@ALURMI, 77012), (@MORATARI, 77021), (@MORATARI, 77013), (@ETERNUS, 77014), (@ETERNUS, 77015),
(770101, 77020), (770102, 77020), (770103, 77020), (770104, 77020), (770105, 77020), (770106, 77020), (770107, 77020),
(770108, 77020), (770109, 77020), (770110, 77020), (770111, 77020);

-- To the front: before the officer who enlists the landing, facing them (wrath_remix_world_0006's
-- transitions table; the module takes the Timerunner there as Eternus is answered).
DELETE FROM `remix_bridge` WHERE `quest` IN (77014, 77015);
INSERT INTO `remix_bridge` (`quest`, `next_quest`, `chapter`, `map`, `x`, `y`, `z`, `o`, `skipped`) VALUES
(77014, 11672, 1, 571, 2297.7, 5236.9, 11.4, 5.92, ''),
(77015, 11585, 1, 571, 2757.5, 6090.8, 77.9, 0.42, '');

-- Bronze for the prologue: enough at Alurmi's stall for a first heirloom.
DELETE FROM `remix_quest_reward` WHERE `quest` BETWEEN 77010 AND 77015 OR `quest` IN (77020, 77021);
INSERT INTO `remix_quest_reward` (`quest`, `bronze`) VALUES
(77010, 500), (77011, 1000), (77012, 1500), (77020, 500), (77021, 500), (77013, 6000), (77014, 2000), (77015, 2000);
