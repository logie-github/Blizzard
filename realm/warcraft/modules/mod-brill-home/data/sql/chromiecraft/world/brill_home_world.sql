-- mod-brill-home (ChromieCraft's world database alone: ctl.sh realm_sql). Made by tools/build_sql.py;
-- don't edit by hand. Written to be applied again: its own rows go first.

DELETE FROM `gameobject_template` WHERE `entry` BETWEEN 970100 AND 970119;
DELETE FROM `gameobject` WHERE `guid` BETWEEN 970100 AND 970149;
DELETE FROM `creature_template` WHERE `entry` BETWEEN 970110 AND 970119;
DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN 970110 AND 970119;
DELETE FROM `creature` WHERE `guid` BETWEEN 970100 AND 970149;
DELETE FROM `quest_template` WHERE `ID` BETWEEN 970120 AND 970129;
DELETE FROM `quest_template_addon` WHERE `ID` BETWEEN 970120 AND 970129;
DELETE FROM `quest_offer_reward` WHERE `ID` BETWEEN 970120 AND 970129;
DELETE FROM `quest_request_items` WHERE `ID` BETWEEN 970120 AND 970129;
DELETE FROM `creature_queststarter` WHERE `quest` BETWEEN 970120 AND 970129;
DELETE FROM `creature_questender` WHERE `quest` BETWEEN 970120 AND 970129;
DELETE FROM `creature_template` WHERE `entry` BETWEEN 970150 AND 970159;
DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN 970150 AND 970159;
DELETE FROM `npc_text` WHERE `ID` BETWEEN 970140 AND 970159;

-- The house (the farmhouse Brill's own are), its furniture (each in its phase).
INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `Data0`, `Data1`, `Data3`, `ScriptName`) VALUES
(970100, 33, 7432, 'Harrow Farmhouse', 1, 0, 0, 0, ''),
(970101, 2, 3471, 'Starter Bed', 1.0, 0, 0, 0, 'go_brill_home_bed'),
(970102, 5, 234, 'Kitchen Table', 1.0, 0, 0, 0, ''),
(970103, 7, 39, 'Chair', 1.0, 1, 1, 0, ''),
(970104, 5, 4, 'Wardrobe', 1.0, 0, 0, 0, ''),
(970105, 5, 188, 'Bookshelf', 1.0, 0, 0, 0, ''),
(970106, 5, 9405, 'Bearskin Rug', 0.65, 0, 0, 0, ''),
(970107, 5, 348, 'Pot-Bellied Stove', 1.0, 0, 0, 0, '');
DELETE FROM `gameobject_template_addon` WHERE `entry` = 970100;
INSERT INTO `gameobject_template_addon` (`entry`, `faction`, `flags`) VALUES (970100, 0, 32);

INSERT INTO `gameobject` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`, `animprogress`, `state`, `Comment`) VALUES
(970100, 970100, 0, 85, 159, 1, 1, 2275.000, 480.500, 29.960, 5.0615, 0, 0, 0.573558, -0.819165, 0, 255, 1, 'mod-brill-home'),
(970101, 970101, 0, 85, 159, 1, 512, 2272.806, 476.530, 34.060, 5.0615, 0, 0, 0.573558, -0.819165, 0, 255, 1, 'mod-brill-home'),
(970102, 970102, 0, 85, 159, 1, 2048, 2276.443, 483.260, 34.060, 0.3491, 0, 0, 0.173670, 0.984804, 0, 255, 1, 'mod-brill-home'),
(970103, 970103, 0, 85, 159, 1, 2048, 2275.080, 482.764, 34.060, 0.3491, 0, 0, 0.173670, 0.984804, 0, 255, 1, 'mod-brill-home'),
(970104, 970103, 0, 85, 159, 1, 2048, 2277.213, 481.146, 34.060, 1.9199, 0, 0, 0.819165, 0.573558, 0, 255, 1, 'mod-brill-home'),
(970105, 970104, 0, 85, 159, 1, 4096, 2269.931, 483.901, 34.060, 5.0615, 0, 0, 0.573558, -0.819165, 0, 255, 1, 'mod-brill-home'),
(970106, 970105, 0, 85, 159, 1, 8192, 2279.386, 476.637, 34.060, 1.9199, 0, 0, 0.819165, 0.573558, 0, 255, 1, 'mod-brill-home'),
(970107, 970106, 0, 85, 159, 1, 16384, 2277.999, 479.570, 34.060, 0.3491, 0, 0, 0.173670, 0.984804, 0, 255, 1, 'mod-brill-home'),
(970108, 970107, 0, 85, 159, 1, 32768, 2280.515, 478.272, 34.060, 3.4907, 0, 0, 0.984804, -0.173670, 0, 255, 1, 'mod-brill-home');

-- Cedric Harrow (who leaves the house to the player), and the bed's credit (sleeping in it).
INSERT INTO `creature_template` (`entry`, `name`, `subname`, `gossip_menu_id`, `minlevel`, `maxlevel`, `faction`, `npcflag`, `speed_walk`, `speed_run`, `unit_class`, `unit_flags`, `type`, `flags_extra`, `ScriptName`) VALUES
(970110, 'Cedric Harrow', NULL, 0, 20, 20, 68, 2, 1, 1.14286, 1, 0, 6, 2, ''),
(970111, 'Slept in your new bed', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 130, '');
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`) VALUES
(970110, 0, 3533, 1, 1),
(970111, 0, 11686, 1, 1);
INSERT INTO `creature` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(970100, 970110, 0, 85, 159, 1, 256, 2271.557, 480.311, 34.060, 3.2725, 120, 0, 0, 'mod-brill-home');

-- Jamie Nore (Brill's town hall) gives the quests and the house's upgrades (src/BrillHome.cpp).
UPDATE `creature_template` SET `npcflag` = `npcflag` | 3, `gossip_menu_id` = 970130, `ScriptName` = 'npc_brill_home_jamie' WHERE `entry` = 2310;

-- Their words.
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES
(970140, 'Brill\'s records are in order, the dead stay in their proper plots, and the living pay their taxes. Mostly.$B$BWhat can I do for you, $n?', 'Brill\'s records are in order, the dead stay in their proper plots, and the living pay their taxes. Mostly.$B$BWhat can I do for you, $n?', 1),
(970141, 'What would you like for the house? I\'ll have it carried over today.', 'What would you like for the house? I\'ll have it carried over today.', 1),
(970142, 'A wooden bed with a straw mattress and a quilt that\'s only been mended twice.', 'A wooden bed with a straw mattress and a quilt that\'s only been mended twice.', 1),
(970143, 'Mind the third board by the door. I never did get it to sit right.', 'Mind the third board by the door. I never did get it to sit right.', 1);

-- The quests: Cedric's house to Jamie; her welcome (done as it's taken); her bed.
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `Flags`, `RewardXPDifficulty`, `RewardMoney`, `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `AreaDescription`, `QuestCompletionLog`, `RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `ObjectiveText1`) VALUES
(970120, 2, -1, 5, 159, 8, 2, 0, 0, 'The House by the Road', 'Speak with Jamie Nore in the Brill town hall.', 'You\'ve the look of someone who keeps their word, $n. Brill could use more of those.$B$BI built this house before the plague, for Elinor and our two boys. When I rose again my feet carried me back here before my mind knew where it was going. I put the roof back on board by board. Thought it would help me remember who I was.$B$BIt didn\'t. It only reminds me who isn\'t here.$B$BThere\'s a ship leaving the Undercity for Vengeance Landing at the next dark of the moon, and I mean to be on it. Whatever the Lich King took from me, I\'ll take some of it back in Northrend.$B$BBrill took me in when the living would have burned me. I\'d like to leave it something better than an empty house. Let it go to someone the town can count on.$B$BJamie Nore at the town hall keeps the deeds. Tell her Cedric Harrow sent you, and that the house is yours.', '', 'Return to Jamie Nore in Brill.', 0, 0, ''),
(970121, 2, -1, 5, 159, 65544, 1, 0, 0, 'Welcome Home', 'Sign the deed to your house with Jamie Nore.', 'Then let\'s make it official. Sign here... and here. There.$B$BBrill isn\'t much, $n, and Tirisfal isn\'t kind. But a door that shuts and a roof that keeps the rain out are worth more than gold out here. Look after it, and it\'ll look after you.', '', '', 0, 0, ''),
(970122, 2, -1, 5, 159, 8, 2, 0, 0, 'Not on the Floor', 'Sleep in the bed in your new house, then return to Jamie Nore in Brill.', 'We can\'t have someone living in this town sleeping on the floor now, can we?$B$BThe innkeeper owed me a favor, and the inn had a spare bed taking up room in its cellar. I\'ve had it carried over to your house. Nothing grand: a wooden frame, a straw mattress, and a quilt that\'s only been mended twice.$B$BGo and try it out. Lie down, get a proper night\'s sleep, and then come back and tell me I was right.', '', 'Return to Jamie Nore in Brill.', 970111, 1, 'Slept in your new bed');
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`) VALUES
(970120, 0), (970121, 970120), (970122, 970121);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`) VALUES
(970120, 1, 'Cedric\'s house? He\'s giving it to you?$B$BHe stood in that doorway every night for three years, watching the road as if someone was coming home. I suppose someone finally is.$B$BWell. The deed\'s in order. Cedric always did keep his papers tidy, even dead.'), (970121, 2, 'Welcome home, neighbor.$B$BI walked past it this morning, mind you. Cedric took nearly everything with him; there isn\'t so much as a stool left. We\'ll fix that.'), (970122, 1, 'You look rested. Don\'t argue; you do.$B$BWhenever you\'d like to make the place more of a home, come and see me. I know a carpenter in the Undercity who owes me even more than the innkeeper did.');
INSERT INTO `quest_request_items` (`ID`, `EmoteOnComplete`, `EmoteOnIncomplete`, `CompletionText`) VALUES
(970122, 1, 1, 'Well? Have you tried it yet?');
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES
(970110, 970120), (2310, 970121), (2310, 970122);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES
(2310, 970120), (2310, 970121), (2310, 970122);

-- Corn, the dog: beside the bed once the player has slept in it (its phase), his quest, and the
-- template his pet is made from; the quest's two credits. The game's pug in the user's Forsaken coat.
INSERT INTO `creature_template` (`entry`, `name`, `subname`, `gossip_menu_id`, `minlevel`, `maxlevel`, `faction`, `npcflag`, `speed_walk`, `speed_run`, `unit_class`, `unit_flags`, `type`, `type_flags`, `family`, `flags_extra`, `ScriptName`) VALUES
(970112, 'Corn', NULL, 0, 1, 1, 35, 3, 1, 1.14286, 1, 0, 1, 0, 1, 2, 'npc_brill_home_mastiff'),
(970115, 'Corn', NULL, 0, 1, 1, 35, 0, 1, 1.14286, 1, 0, 1, 1, 1, 0, ''),
(970116, 'Corn', NULL, 0, 1, 1, 35, 0, 1, 1.14286, 1, 0, 1, 0, 1, 0, 'npc_brill_home_companion'),
(970117, 'Stabled Companion', NULL, 0, 1, 1, 35, 0, 1, 1.14286, 1, 0, 1, 0, 1, 0, 'npc_brill_home_companion'),
(970113, 'Played fetch with Corn', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 0, 130, ''),
(970114, 'Scratched Corn behind the ears', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 0, 0, 130, '');
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`) VALUES
(970112, 0, 31174, 1, 1),
(970115, 0, 31174, 1, 1),
(970116, 0, 31174, 1, 1),
(970117, 0, 31174, 1, 1),
(970113, 0, 11686, 1, 1),
(970114, 0, 11686, 1, 1);
INSERT INTO `creature` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(970101, 970112, 0, 85, 159, 1, 1024, 2273.180, 479.944, 34.060, 4.4506, 60, 0, 0, 'mod-brill-home');
DELETE FROM `creature_model_info` WHERE `DisplayID` BETWEEN 39700 AND 39703;
DELETE FROM `creaturemodeldata_dbc` WHERE `ID` = 3970;
DELETE FROM `creaturedisplayinfo_dbc` WHERE `ID` BETWEEN 39700 AND 39703;
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES
(970144, '(The dog looks happy to see you.)', '(The dog looks happy to see you.)', 1),
(970145, '(Corn sits by the door, watching you. He seems to be waiting until you have room for him.)', '(Corn sits by the door, watching you. He seems to be waiting until you have room for him.)', 1);
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `Flags`, `RewardXPDifficulty`, `RewardMoney`, `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `AreaDescription`, `QuestCompletionLog`, `RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `ObjectiveText1`, `RequiredNpcOrGo2`, `RequiredNpcOrGoCount2`, `ObjectiveText2`) VALUES
(970123, 2, -1, 5, 159, 8, 1, 0, 0, 'A Visitor in the Night', 'Throw the stick for Corn three times, then give him a good scratch behind the ears.', '(A small pug is sitting beside your bed, as if it has been waiting a while for you to wake up. It is not entirely alive: its coat is gray-green and stitched in places, and its eyes glow a soft yellow. A muddy stick lies between its front paws. The tag on its spiked collar reads CORN.)$B$B(It noses the stick toward you. It looks at the door. It looks back at you.)', '', 'Return to Corn.', 970113, 3, 'Played fetch', 970114, 1, 'Scratched behind the ears');
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`) VALUES (970123, 0);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`) VALUES (970123, 0, '(Corn turns three circles on the floor beside your bed and flops down with a long, wheezing, contented sigh.)$B$B(When you step toward the door, he gets up and follows.)');
INSERT INTO `quest_request_items` (`ID`, `EmoteOnComplete`, `EmoteOnIncomplete`, `CompletionText`) VALUES (970123, 0, 0, '(Corn drops the stick at your feet again and waits, tail curled, ears up.)');
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES (970112, 970123);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES (970112, 970123);

-- Carolai Anise: her quests (once Corn is the player's), her visit to the house, her living
-- there; the keepsakes she sends the player for, and the credits. Her menu is src/BrillHome.cpp's.
UPDATE `creature_template` SET `npcflag` = `npcflag` | 3, `ScriptName` = 'npc_brill_home_carolai' WHERE `entry` = 2132;
INSERT INTO `creature_template` (`entry`, `name`, `subname`, `gossip_menu_id`, `minlevel`, `maxlevel`, `faction`, `npcflag`, `speed_walk`, `speed_run`, `unit_class`, `unit_flags`, `type`, `flags_extra`, `ScriptName`) VALUES
(970118, 'Carolai Anise', NULL, 0, 20, 20, 68, 3, 1, 1.14286, 1, 0, 6, 2, 'npc_brill_home_carolai_visit'),
(970119, 'Carolai Anise', NULL, 0, 20, 20, 68, 1, 1, 1.14286, 1, 0, 6, 2, 'npc_brill_home_carolai_home'),
(970150, 'Shared tea with Carolai', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 130, ''),
(970151, 'Carolai\'s locket', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 130, ''),
(970152, 'Moonpetal lily', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 130, ''),
(970153, 'Gave Carolai your answer', NULL, 0, 1, 1, 35, 0, 1, 1, 1, 33554432, 10, 130, '');
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`) VALUES
(970118, 0, 1601, 1, 1),
(970119, 0, 1601, 1, 1),
(970150, 0, 11686, 1, 1),
(970151, 0, 11686, 1, 1),
(970152, 0, 11686, 1, 1),
(970153, 0, 11686, 1, 1);
INSERT INTO `creature` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(970102, 970118, 0, 85, 159, 1, 65536, 2271.557, 480.311, 34.060, 3.2725, 60, 0, 0, 'mod-brill-home'),
(970103, 970119, 0, 85, 159, 1, 131072, 2272.932, 483.259, 34.060, 1.9199, 60, 0, 0, 'mod-brill-home');
INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `size`, `Data0`, `Data1`, `Data3`, `ScriptName`) VALUES
(970108, 2, 8, 'Old Footlocker', 1, 0, 0, 0, 'go_brill_home_keepsake'),
(970109, 2, 3232, 'Moonpetal Lily', 1.6, 0, 0, 0, 'go_brill_home_keepsake'),
(970110, 5, 4391, 'Carolai\'s Alchemy Table', 0.8, 0, 0, 0, '');
INSERT INTO `gameobject` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`, `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`, `animprogress`, `state`, `Comment`) VALUES
(970120, 970108, 0, 85, 0, 1, 1, 2266.600, 1316.400, 34.100, 1.2000, 0, 0, 0.564642, 0.825336, 0, 255, 1, 'mod-brill-home'),
(970121, 970109, 0, 85, 0, 1, 1, 2496.000, 102.000, 21.410, 0.0000, 0, 0, 0.000000, 1.000000, 0, 255, 1, 'mod-brill-home'),
(970122, 970110, 0, 85, 159, 1, 131072, 2272.531, 484.358, 34.060, 5.0615, 0, 0, 0.573558, -0.819165, 0, 255, 1, 'mod-brill-home');
DELETE FROM `quest_poi` WHERE `QuestID` IN (970125, 970128);
DELETE FROM `quest_poi_points` WHERE `QuestID` IN (970125, 970128);
INSERT INTO `quest_poi` (`QuestID`, `id`, `ObjectiveIndex`, `MapID`, `WorldMapAreaId`, `Floor`, `Priority`, `Flags`, `VerifiedBuild`) VALUES
(970125, 0, 0, 0, 20, 0, 0, 1, 0), (970128, 0, 0, 0, 20, 0, 0, 1, 0);
INSERT INTO `quest_poi_points` (`QuestID`, `Idx1`, `Idx2`, `X`, `Y`, `VerifiedBuild`) VALUES
(970125, 0, 0, 2267, 1316, 0), (970128, 0, 0, 2496, 102, 0);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES
(970146, '(Carolai has swept your floor, folded your things and made tea. She\'s waiting for you to sit.)', '(Carolai has swept your floor, folded your things and made tea. She\'s waiting for you to sit.)', 1),
(970148, '(Carolai looks at the lily in your hand, then at you, and waits.)', '(Carolai looks at the lily in your hand, then at you, and waits.)', 1),
(970149, 'There you are. You always come back to me, $n.$B$BI\'d know your footsteps anywhere. I listen for them.', 'There you are. You always come back to me, $n.$B$BI\'d know your footsteps anywhere. I listen for them.', 1),
(970150, 'Hello, friend.$B$BYou didn\'t sleep well last night. No, don\'t tell me. I know you didn\'t.', 'Hello, friend.$B$BYou didn\'t sleep well last night. No, don\'t tell me. I know you didn\'t.', 1),
(970151, '(Under a moth-eaten quilt in the footlocker lies a small tin locket, its chain knotted. Inside is a faded painting of a young woman with Carolai\'s eyes.)$B$B(You take it.)', '(Under a moth-eaten quilt in the footlocker lies a small tin locket, its chain knotted. Inside is a faded painting of a young woman with Carolai\'s eyes.)$B$B(You take it.)', 1),
(970152, '(A single pale lily grows where the water laps at the reeds. Its petals are cold, and faintly bright, like the moon on Lordamere.)$B$B(You pick it.)', '(A single pale lily grows where the water laps at the reeds. Its petals are cold, and faintly bright, like the moon on Lordamere.)$B$B(You pick it.)', 1);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`, `text3_0`, `text3_1`, `Probability3`, `text4_0`, `text4_1`, `Probability4`, `text5_0`, `text5_1`, `Probability5`, `text6_0`, `text6_1`, `Probability6`) VALUES (970147, 'Welcome home, my love. I\'ve warmed the kettle. I warm it every time I hear you on the road.', 'Welcome home, my love. I\'ve warmed the kettle. I warm it every time I hear you on the road.', 0.14, 'The dog likes me now. He sleeps across the doorway, so nothing gets in. Or out. Good boy.', 'The dog likes me now. He sleeps across the doorway, so nothing gets in. Or out. Good boy.', 0.14, 'I moved your things around a little. You\'ll get used to it. I got used to everything about you.', 'I moved your things around a little. You\'ll get used to it. I got used to everything about you.', 0.14, 'Jamie waved at you in the square today. I saw. It\'s all right. I\'m not angry. I\'m never angry with you.', 'Jamie waved at you in the square today. I saw. It\'s all right. I\'m not angry. I\'m never angry with you.', 0.14, 'I\'ve set up my bench by the window. The light\'s better here. And I can see the road, so I know when you\'re coming.', 'I\'ve set up my bench by the window. The light\'s better here. And I can see the road, so I know when you\'re coming.', 0.14, 'I read to the dog while you were out. He likes the sad parts. So do I.', 'I read to the dog while you were out. He likes the sad parts. So do I.', 0.14, 'Tea? I made it the way you like it. I\'ve been watching how you like it.', 'Tea? I made it the way you like it. I\'ve been watching how you like it.', 0.14);
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`, `text1_0`, `text1_1`, `Probability1`, `text2_0`, `text2_1`, `Probability2`) VALUES (970153, 'I let myself in. You don\'t mind. Friends don\'t mind. I brought you a tonic for the cough you had on Tuesday.', 'I let myself in. You don\'t mind. Friends don\'t mind. I brought you a tonic for the cough you had on Tuesday.', 0.33, 'I was passing. I\'m always passing. Your dog was lonely, so I sat with him. We had a long talk about you.', 'I was passing. I\'m always passing. Your dog was lonely, so I sat with him. We had a long talk about you.', 0.33, 'Jamie says I shouldn\'t come in when you\'re out. Jamie says a great many things.', 'Jamie says I shouldn\'t come in when you\'re out. Jamie says a great many things.', 0.33);
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `Flags`, `RewardXPDifficulty`, `RewardMoney`, `AllowableRaces`, `LogTitle`, `LogDescription`, `QuestDescription`, `AreaDescription`, `QuestCompletionLog`, `RequiredNpcOrGo1`, `RequiredNpcOrGoCount1`, `ObjectiveText1`, `RequiredNpcOrGo2`, `RequiredNpcOrGoCount2`, `ObjectiveText2`, `RewardItem1`, `RewardAmount1`, `RewardItem2`, `RewardAmount2`) VALUES
(970124, 2, -1, 5, 159, 0, 4, 2500, 0, 'A Tonic for Corn', 'Kill 8 Cursed Darkhounds in the hills north of Brill, then return to Carolai Anise.', 'You\'re the one who took Cedric\'s house. With the little dog. Corn, isn\'t it?$B$BDon\'t look so surprised. Brill is small, and I have a window. I see you leave at first light and I see you come home, and I see that dog of yours sitting in your doorway, scratching at its ears.$B$BIt\'s blightmange. The darkhounds carry it out of the woods and leave it in the grass for every dog in Tirisfal to roll in, living or otherwise; it eats what the plague left of them, too. First the fur comes out in clumps, then the skin goes, and then... well. You\'ve seen the darkhounds.$B$BI can brew something for it. But it\'s no use treating him while the hills are crawling with the things that gave it to him. Thin out the Cursed Darkhounds north of Brill, and the tonic will be ready when you come back.$B$BI\'ll be right here. I\'m always right here.', '', 'Return to Carolai Anise in Brill.', 1548, 8, '', 0, 0, '', 0, 0, 0, 0),
(970125, 2, -1, 5, 159, 0, 4, 2500, 0, 'What Solliden Kept', 'Recover Carolai\'s locket from the footlocker in the farmhouse at Solliden Farmstead, then return to Carolai Anise in Brill.', 'The tonic took. He barely scratched at all today. I watched.$B$BMay I ask you something? Not as an alchemist.$B$BBefore the plague I lived at Solliden Farmstead, north of here. My mother gave me a locket the day I was sent to Lordaeron to apprentice. When I rose, it was gone. I\'ve never gone back for it. Old Solliden still walks his fields, and he doesn\'t remember me. He doesn\'t remember anything.$B$BI could ask anyone in Brill. I\'m asking you. It was in the farmhouse, in the footlocker under the window. Will you bring it back to me?', '', 'Return to Carolai Anise in Brill.', 970151, 1, 'Carolai\'s locket', 0, 0, '', 0, 0, 0, 0),
(970126, 2, -1, 5, 159, 0, 2, 2500, 0, 'A Gift for Jamie Nore', 'Take Carolai\'s perfume to Jamie Nore in the Brill town hall.', 'I\'ve been thinking about Jamie Nore.$B$BShe found you that house. She found you the bed. She\'s always so helpful, isn\'t she? Always there, with her ledgers and her deeds and her warm, living hands.$B$BI should thank her properly, for looking after you before I could. Take her this: a perfume, a very old recipe. Tell her it\'s from me. Tell her I said she\'s been more than kind, and that she needn\'t trouble herself over you any longer.$B$BAnd $n? Don\'t open it. It isn\'t for you.', '', 'Speak with Jamie Nore in Brill.', 0, 0, '', 0, 0, '', 0, 0, 0, 0),
(970127, 2, -1, 5, 159, 0, 3, 2500, 0, 'An Unlocked Door', 'Sit and drink tea with Carolai in your house, then speak with her at her shop in Brill.', 'Oh! You\'re home. You\'re early. You\'re never home this early.$B$BYour door was open. It was. I thought something might have happened to you, so I came in to wait, and then I couldn\'t just sit, could I? So I swept. And I washed the cups. And I folded your things. You fold your shirts in thirds; I\'ve put them in halves. It\'s better for the linen.$B$BJamie didn\'t like her present, did she? I could tell by the way she looked at me in the square. It doesn\'t matter.$B$BSit with me. Please. I made tea. I can\'t taste it anymore, but I remember how it ought to be made, and I made it for you.', '', 'Return to Carolai Anise in Brill.', 970150, 1, 'Shared tea with Carolai', 0, 0, '', 0, 0, 0, 0),
(970128, 2, -1, 5, 159, 0, 5, 10000, 0, 'What the Heart Keeps', 'Pick a moonpetal lily on the west shore of Brightwater Lake, east of Brill, then give it to Carolai Anise in Brill and tell her what it means.', 'There\'s a flower that grows on the shore of Brightwater Lake, east of here: the moonpetal lily. Before the plague, a girl in Tirisfal gave one to the one she meant to marry. If they kept it, that was yes.$B$BI won\'t ask you a question you aren\'t ready for. So I\'ll ask you this instead. Go to the lake and bring me one. Then, when you give it to me, tell me what it means.$B$BWhatever you say, I\'ll... I\'ll understand.$B$BI\'ll be here. Waiting. As I always am.', '', 'Return to Carolai Anise in Brill.', 970152, 1, 'Moonpetal lily', 970153, 1, 'Gave Carolai your answer', 929, 5, 3385, 3);
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`) VALUES
(970124, 970123), (970125, 970124), (970126, 970125), (970127, 970126), (970128, 970127);
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`) VALUES
(970124, 1, 'Eight. I counted the howls from here. I thought it might be nine.$B$BHere. Rub it into his ears, morning and night. He\'ll fuss; they always fuss.$B$BDon\'t thank me, $n. It was nothing. I like having a reason to see you.'), (970125, 0, 'You found it.$B$B(She turns the locket over in her fingers for a long time.)$B$BI\'d forgotten her face. I\'d started to think I had made her up.$B$BThank you, $n. I\'ll keep it close. I keep everything that matters close.'), (970126, 0, 'From Carolai? How... thoughtful.$B$B(Jamie unstoppers the vial, sniffs once, and goes very still.)$B$BThat\'s bitterroot, $n. The Apothecaries put it in rat poison. A drop of this on the skin and I\'d only be sick for a week. Probably.$B$BI\'m sure it\'s a mistake. She does work with a great many bottles.$B$B(She corks it and drops it into the waste bin all the same.)$B$BShe\'s been asking about you, you know. Since the day you signed the deed. Which road you take, when you come home, whether you have... company. Last week she asked me which key opens your door.$B$BI didn\'t give it to her. Just lock up tonight, would you?'), (970127, 1, 'You came. I wasn\'t sure you would.$B$BI\'ve stood at this bench for six years mixing tinctures for travelers who never look up. Then you looked up.$B$BI know what I am, $n. I know what the living say about us, and I know what Jamie says about me. I know I don\'t go about this the way other people do. But I have never wanted anything the way I want to be near you.$B$BThere. It\'s said. Now I need to know what you\'ll say back, and I want to hear it properly.'), (970128, 0, '(Carolai threads the lily\'s stem through the locket\'s chain and lets it rest against her heart, where it will dry, and keep.)$B$BWhatever we are to each other, $n, you\'ve given me a reason to keep my shutters open in the morning.$B$BTake these. I brewed them for you before you ever walked into my shop. I brew a great many things for you.');
INSERT INTO `quest_request_items` (`ID`, `EmoteOnComplete`, `EmoteOnIncomplete`, `CompletionText`) VALUES
(970124, 1, 1, 'Has he stopped scratching? He hadn\'t this morning. Five times before you\'d even opened your shutters.'), (970125, 1, 1, 'The farmhouse is north, past the mills. Mind Solliden. He was kind, once.'), (970127, 0, 0, 'You came. I wasn\'t sure you would.'), (970128, 0, 0, '(Carolai looks at your hands first, to see if there\'s a lily in them.)');
INSERT INTO `creature_queststarter` (`id`, `quest`) VALUES
(2132, 970124), (2132, 970125), (2132, 970126), (970118, 970127), (2132, 970128);
INSERT INTO `creature_questender` (`id`, `quest`) VALUES
(2132, 970124), (2132, 970125), (2310, 970126), (2132, 970127), (2132, 970128);
