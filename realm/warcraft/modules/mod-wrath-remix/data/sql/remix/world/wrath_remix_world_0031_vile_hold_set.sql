-- The Unrisen's plate: a death knight's set nobody mentions, in a Scourge coffer left by the supply
-- wagons on Malykriss's south terrace (up the spiked ramp from the crater floor's south edge, about
-- 170 yards on foot from the Great Hourglass), a spiked skull helm set on its lid. A click on the
-- coffer starts WRM-061 to 063 (src/RemixVileHoldSet.cpp): break the three binding runes around it,
-- have the Great Hourglass write the Timerunner's name on the runesmith's tally, kneel at the
-- coffer. The last gives the plate, in one container (one bag slot at the turn-in; what doesn't fit
-- stays in it until it's taken).
--
-- The plate is an heirloom any class can wear: armour subclass Miscellaneous (no proficiency; the
-- core's CanUseItem checks a skill only for cloth to shield), bind to account, level 1 and up,
-- scaled by ScalingStatDistribution (which stats) and ScalingStatValue (which of
-- ScalingStatValues.dbc's columns: the budget and the armour for the wearer's level, to 80). Only
-- rows and bits the game's own DBCs have, so the client's tooltips agree. 3.3.5's heirlooms cover
-- shoulders, chests, rings and weapons; the other slots borrow the nearest column (see README):
--   head    primary budget, plate shoulder armour     wrists  ring budget, mail shoulder armour
--   chest   primary budget, plate chest armour        hands   shoulder budget, mail chest armour
--   legs    primary budget, plate chest armour        waist   shoulder budget, mail chest armour
--   shoulders, feet: shoulder budget, plate shoulder armour; back: ring budget, cloak armour.
-- Stats every class uses: critical strike, hit and stamina (ScalingStatDistribution 371, the Dread
-- Pirate Ring's), haste on wrists, hands and feet (251, Swift Hand of Justice's).
-- The looks are the Acherus Knight's, a death knight's first plate (the only death knight set with
-- all eight armour slots and an icon for each).
--
-- Ids: items 77010 to 77020, game objects 770200 to 770206 (spawns 7705800 to 7705804), quests 77061
-- to 77063, npc_text 7702180. No creatures (the credits are game objects).

-- The plate, the container that holds it, and the tally.
DELETE FROM `item_template` WHERE `entry` BETWEEN 77010 AND 77029;
INSERT INTO `item_template` (`entry`, `class`, `subclass`, `SoundOverrideSubclass`, `name`, `displayid`, `Quality`, `Flags`, `BuyCount`,
  `BuyPrice`, `SellPrice`, `InventoryType`, `AllowableClass`, `AllowableRace`, `ItemLevel`, `RequiredLevel`, `maxcount`, `stackable`,
  `ScalingStatDistribution`, `ScalingStatValue`, `armor`, `holy_res`, `fire_res`, `nature_res`, `frost_res`, `shadow_res`, `arcane_res`,
  `spellid_1`, `spelltrigger_1`, `bonding`, `description`, `Material`, `sheath`, `MaxDurability`, `ScriptName`, `VerifiedBuild`) VALUES
(77010, 4, 0, -1, 'Hood of the Unrisen',        51495, 7, 134217728, 1, 0, 0,  1, -1, -1, 1, 1, 0, 1, 371,     264, 64, 0, 0, 0, 0, 0, 0, 0, 0, 1,
 'Forged in Malykriss for a knight who never rose.', 6, 0, 0, '', 0),
(77011, 4, 0, -1, 'Pauldrons of the Unrisen',   51501, 7, 134217728, 1, 0, 0,  3, -1, -1, 1, 1, 0, 1, 371,     257, 64, 0, 0, 0, 0, 0, 0, 0, 0, 1,
 'Forged in Malykriss for a knight who never rose.', 6, 0, 0, '', 0),
(77012, 4, 0, -1, 'Battleplate of the Unrisen', 51494, 7, 134217728, 1, 0, 0,  5, -1, -1, 1, 1, 0, 1, 371, 8388616, 85, 0, 0, 0, 0, 0, 0, 0, 0, 1,
 'Forged in Malykriss for a knight who never rose.', 6, 0, 0, '', 0),
(77013, 4, 0, -1, 'Wristguards of the Unrisen', 51500, 7, 134217728, 1, 0, 0,  9, -1, -1, 1, 1, 0, 1, 251,  262272, 32, 0, 0, 0, 0, 0, 0, 0, 0, 1,
 'Forged in Malykriss for a knight who never rose.', 6, 0, 0, '', 0),
(77014, 4, 0, -1, 'Gauntlets of the Unrisen',   51498, 7, 134217728, 1, 0, 0, 10, -1, -1, 1, 1, 0, 1, 251, 4194305, 43, 0, 0, 0, 0, 0, 0, 0, 0, 1,
 'Forged in Malykriss for a knight who never rose.', 6, 0, 0, '', 0),
(77015, 4, 0, -1, 'Girdle of the Unrisen',      51497, 7, 134217728, 1, 0, 0,  6, -1, -1, 1, 1, 0, 1, 371, 4194305, 43, 0, 0, 0, 0, 0, 0, 0, 0, 1,
 'Forged in Malykriss for a knight who never rose.', 6, 0, 0, '', 0),
(77016, 4, 0, -1, 'Legplates of the Unrisen',   51499, 7, 134217728, 1, 0, 0,  7, -1, -1, 1, 1, 0, 1, 371, 8388616, 85, 0, 0, 0, 0, 0, 0, 0, 0, 1,
 'Forged in Malykriss for a knight who never rose.', 6, 0, 0, '', 0),
(77017, 4, 0, -1, 'Greaves of the Unrisen',     51496, 7, 134217728, 1, 0, 0,  8, -1, -1, 1, 1, 0, 1, 251,     257, 64, 0, 0, 0, 0, 0, 0, 0, 0, 1,
 'Forged in Malykriss for a knight who never rose.', 6, 0, 0, '', 0),
(77018, 4, 1, -1, 'Shroud of the Unrisen',      49738, 7, 134217728, 1, 0, 0, 16, -1, -1, 1, 1, 0, 1, 371,  786432,  7, 0, 0, 0, 0, 0, 0, 0, 0, 1,
 'Forged in Malykriss for a knight who never rose.', 7, 0, 0, '', 0),
-- (opened for its loot: ITEM_FLAG_HAS_LOOT with the account's binding)
(77019, 15, 0, -1, 'Plate of the Unrisen',      12644, 7, 134217732, 1, 0, 0,  0, -1, -1, 1, 0, 0, 1,   0,       0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
 'The fortieth knight of Malykriss''s plate, folded in black cloth. Yours.', -1, 0, 0, '', 0),
-- (a quest item; its use is the module's, the spell is never cast)
(77020, 12, 0, -1, 'Runesmith''s Tally',        1143, 1, 0,         1, 0, 0,  0, -1, -1, 1, 0, 1, 1,   0,       0,  0, 0, 0, 0, 0, 0, 0, 52096, 0, 4,
 'Forty lines, forty numbers, no names. Use it at the Great Hourglass.', -1, 0, 0, 'item_remix_unrisen_tally', 0);

-- What the game itself needs to know of them (written into the game's patch as the realm starts).
DELETE FROM `item_dbc` WHERE `ID` BETWEEN 77010 AND 77029;
INSERT INTO `item_dbc` (`ID`, `ClassID`, `SubclassID`, `Sound_Override_Subclassid`, `Material`, `DisplayInfoID`, `InventoryType`, `SheatheType`) VALUES
(77010, 4, 0, -1, 6, 51495, 1, 0),
(77011, 4, 0, -1, 6, 51501, 3, 0),
(77012, 4, 0, -1, 6, 51494, 5, 0),
(77013, 4, 0, -1, 6, 51500, 9, 0),
(77014, 4, 0, -1, 6, 51498, 10, 0),
(77015, 4, 0, -1, 6, 51497, 6, 0),
(77016, 4, 0, -1, 6, 51499, 7, 0),
(77017, 4, 0, -1, 6, 51496, 8, 0),
(77018, 4, 1, -1, 7, 49738, 16, 0),
(77019, 15, 0, -1, -1, 12644, 0, 0),
(77020, 12, 0, -1, -1, 1143, 0, 0);

DELETE FROM `item_loot_template` WHERE `Entry` BETWEEN 77010 AND 77029;
INSERT INTO `item_loot_template` (`Entry`, `Item`, `Reference`, `Chance`, `QuestRequired`, `LootMode`, `GroupId`, `MinCount`, `MaxCount`, `Comment`) VALUES
(77019, 77010, 0, 100, 0, 1, 0, 1, 1, 'Plate of the Unrisen: hood'),
(77019, 77011, 0, 100, 0, 1, 0, 1, 1, 'Plate of the Unrisen: pauldrons'),
(77019, 77012, 0, 100, 0, 1, 0, 1, 1, 'Plate of the Unrisen: battleplate'),
(77019, 77013, 0, 100, 0, 1, 0, 1, 1, 'Plate of the Unrisen: wristguards'),
(77019, 77014, 0, 100, 0, 1, 0, 1, 1, 'Plate of the Unrisen: gauntlets'),
(77019, 77015, 0, 100, 0, 1, 0, 1, 1, 'Plate of the Unrisen: girdle'),
(77019, 77016, 0, 100, 0, 1, 0, 1, 1, 'Plate of the Unrisen: legplates'),
(77019, 77017, 0, 100, 0, 1, 0, 1, 1, 'Plate of the Unrisen: greaves'),
(77019, 77018, 0, 100, 0, 1, 0, 1, 1, 'Plate of the Unrisen: shroud');

-- The coffer (a quest giver: the Scourge's chest), the helm on its lid (not clickable), the three
-- binding runestones (Naxxramas's, each a quest object of WRM-061's, clickable only while it's in
-- the log), and the two credits no one sees (never spawned: the Hourglass's writing, the kneel).
DELETE FROM `gameobject_template` WHERE `entry` BETWEEN 770200 AND 770219;
INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `IconName`, `castBarCaption`, `unk1`, `size`,
  `Data0`, `Data1`, `Data2`, `Data3`, `Data4`, `Data5`, `Data6`, `Data7`, `Data8`, `Data9`, `Data10`, `Data11`, `Data12`, `Data13`,
  `Data14`, `Data15`, `Data16`, `Data17`, `AIName`, `ScriptName`, `VerifiedBuild`) VALUES
(770200, 2, 8508, 'Unclaimed Coffer', '', '', '', 0.75,  0, 0,     0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, '', 'go_remix_unrisen_coffer', 0),
(770201, 5, 8501, 'Unclaimed Helm', '', '', '', 1.5,     0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '', '', 0),
(770202, 10, 6714, 'Rune of Binding', '', '', '', 1.0,   0, 77061, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, '', '', 0),
(770203, 10, 6714, 'Rune of Obedience', '', '', '', 1.0, 0, 77061, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, '', '', 0),
(770204, 10, 6714, 'Rune of Silence', '', '', '', 1.0,   0, 77061, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, '', '', 0),
(770205, 5, 7133, 'A Name Written', '', '', '', 1.0,     0, 0,     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '', '', 0),
(770206, 5, 8508, 'Knelt at the Coffer', '', '', '', 1.0, 0, 0,    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '', '', 0);

DELETE FROM `gameobject_template_addon` WHERE `entry` BETWEEN 770200 AND 770219;
INSERT INTO `gameobject_template_addon` (`entry`, `faction`, `flags`, `mingold`, `maxgold`) VALUES
(770201, 0, 16, 0, 0);      -- GO_FLAG_NOT_SELECTABLE: the coffer under it takes the click

-- On the south terrace (z 525, the server's own collision and navmesh: the floor survey stops at the
-- crater floor), in the corner between a Scourge wagon and its plague bombs, facing the top of the
-- ramp (6278, 1842) the Timerunner comes up by: the coffer's padlock and skull toward it, the helm's
-- face, each runestone's rune. Rotations are the orientation's (sin and cos of half of it).
DELETE FROM `gameobject` WHERE `guid` BETWEEN 7705800 AND 7705849;
INSERT INTO `gameobject` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`,
  `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`, `animprogress`, `state`, `ScriptName`, `VerifiedBuild`, `Comment`) VALUES
(7705800, 770200, 571, 210, 4520, 1, 1, 6262.00, 1840.00, 525.17, 4.8367, 0, 0, 0.661803, -0.749678, 300, 100, 1, '', 0, 'Wrath Remix: the Unclaimed Coffer, Malykriss''s south terrace'),
(7705801, 770201, 571, 210, 4520, 1, 1, 6262.00, 1840.00, 526.14, 0.1244, 0, 0, 0.062137, 0.998068, 300, 100, 1, '', 0, 'Wrath Remix: the Unclaimed Helm, on the coffer''s lid'),
(7705802, 770202, 571, 210, 4520, 1, 1, 6267.00, 1840.00, 525.04, 0.1799, 0, 0, 0.089806, 0.995959, 300, 100, 1, '', 0, 'Wrath Remix: Rune of Binding, by the coffer'),
(7705803, 770203, 571, 210, 4520, 1, 1, 6259.50, 1844.30, 525.18, 6.1595, 0, 0, 0.061805, -0.998088, 300, 100, 1, '', 0, 'Wrath Remix: Rune of Obedience, by the coffer'),
(7705804, 770204, 571, 210, 4520, 1, 1, 6259.50, 1835.70, 525.18, 0.3282, 0, 0, 0.163376, 0.986564, 300, 100, 1, '', 0, 'Wrath Remix: Rune of Silence, by the coffer');

-- The quests. The coffer gives and takes back all three, one after another; at the Timerunner's
-- own level, from 10 (a death knight from 55).
DELETE FROM `quest_template` WHERE `ID` BETWEEN 77061 AND 77063;
INSERT INTO `quest_template` (`ID`, `QuestType`, `QuestLevel`, `MinLevel`, `QuestSortID`, `RewardXPDifficulty`, `RewardMoney`, `Flags`,
  `AllowableRaces`, `StartItem`, `RewardItem1`, `RewardAmount1`, `LogTitle`, `LogDescription`, `QuestDescription`, `QuestCompletionLog`,
  `RequiredNpcOrGo1`, `RequiredNpcOrGo2`, `RequiredNpcOrGo3`, `RequiredNpcOrGoCount1`, `RequiredNpcOrGoCount2`, `RequiredNpcOrGoCount3`,
  `ObjectiveText1`, `ObjectiveText2`, `ObjectiveText3`, `VerifiedBuild`) VALUES
(77061, 2, -1, 10, 210, 3, 0, 0, 0, 0, 0, 0,
 'Plate Without a Knight',
 'Break the three binding runes around the Unclaimed Coffer in Malykriss.',
 'The coffer is Scourge work: banded in saronite, a skull for a lock, and a helm set on its lid like a crown on a grave. It is not locked.$B$BInside, folded in black cloth, lies a full suit of runed plate. Hood, pauldrons, battleplate, gauntlets, greaves, a shroud: every piece of it, and none of it ever worn. The straps have never been buckled. There is no blood on it, and no frost from a rider''s breath.$B$BThe Lich King''s runesmiths made plate like this for the knights he meant to raise here, in the necropolis he never finished. Three runestones stand around the coffer, cut with runes of binding. While they hold, the plate will answer no one but a knight of the Scourge.$B$BBreak them.',
 'Return to the Unclaimed Coffer.',
 -770202, -770203, -770204, 1, 1, 1,
 'Rune of Binding broken', 'Rune of Obedience broken', 'Rune of Silence broken', 0),
(77062, 2, -1, 10, 210, 3, 0, 0, 0, 77020, 0, 0,
 'A Name Never Written',
 'Use the Runesmith''s Tally at the Great Hourglass in the heart of the Infinite Bazaar, then return to the Unclaimed Coffer.',
 'The tally''s line for this suit reads: The fortieth knight of Malykriss. To be raised in the new necropolis. Fitted to the one who rises.$B$BNo one rose to wear it. The Bazaar''s dragons swept the Lich King''s builders out of Malykriss when they began putting the timeline in order, before they ever finished it, and the knight this plate was waiting for was never raised. The line beside the number stayed blank.$B$BThe infinite dragonflight deals in blank lines, $n. In this hour, your own name is not written anywhere either.$B$BTake the tally to the Great Hourglass at the heart of the Bazaar and hold it up to the sands. Then bring it back here.',
 'Return to the Unclaimed Coffer.',
 -770205, 0, 0, 1, 0, 0,
 'Name written at the Great Hourglass', '', '', 0),
(77063, 2, -1, 10, 210, 3, 0, 0, 0, 0, 77019, 1,
 'The Knight Who Never Rose',
 'Kneel at the Unclaimed Coffer, then take up the plate.',
 'One instruction remains, in the runesmith''s hand at the foot of the tally: Each knight shall kneel at the coffer and receive the plate from the hand of his king.$B$BThere is no king in Malykriss to give it to you. The Lich King sits on his throne at the top of the Citadel, and in this hour he has never heard your name.$B$BKneel anyway. Not to him: to the knight who was meant to wear this, and never did. Then take up the plate.',
 'Take up the plate from the Unclaimed Coffer.',
 -770206, 0, 0, 1, 0, 0,
 'Knelt at the Unclaimed Coffer (/kneel)', '', '', 0);

DELETE FROM `quest_template_addon` WHERE `ID` BETWEEN 77061 AND 77063;
INSERT INTO `quest_template_addon` (`ID`, `PrevQuestID`, `NextQuestID`, `ProvidedItemCount`) VALUES
(77061, 0, 0, 0),
(77062, 77061, 0, 1),
(77063, 77062, 0, 0);

DELETE FROM `quest_request_items` WHERE `ID` BETWEEN 77061 AND 77063;
INSERT INTO `quest_request_items` (`ID`, `EmoteOnComplete`, `EmoteOnIncomplete`, `CompletionText`, `VerifiedBuild`) VALUES
(77061, 0, 0, 'The runestones still glow around the coffer. The plate lies cold in its cloth.', 0),
(77062, 0, 0, 'The tally''s line is still blank.', 0),
(77063, 0, 0, 'The plate waits in its cloth.', 0);

DELETE FROM `quest_offer_reward` WHERE `ID` BETWEEN 77061 AND 77063;
INSERT INTO `quest_offer_reward` (`ID`, `Emote1`, `RewardText`, `VerifiedBuild`) VALUES
(77061, 0, 'The last rune gutters out. Frost runs off the coffer''s lid like sweat.$B$BUnder the plate, where the runes kept it hidden, lies a runesmith''s tally: a list of the knights this armory was forged for, one line to each suit. Every line is numbered.$B$BNot one of them has a name.', 0),
(77062, 0, 'The sand has written on the tally in a hand that is neither yours nor the runesmith''s. The fortieth knight of Malykriss has a name now, and it is yours.$B$BThe plate has changed with it. The runes along its edges have dulled from Scourge blue to bronze, and the hood, held up against you, is your size.', 0),
(77063, 0, 'No voice answers. No king''s hand comes down. The coffer''s lid only gives a little under yours, as if it had been waiting.$B$BThe plate is yours: the Lich King''s own pattern, made for a knight he never raised and fitted now to one he never will. It will grow with you, whatever you are, and whatever you become.', 0);

DELETE FROM `gameobject_queststarter` WHERE `quest` BETWEEN 77061 AND 77063;
INSERT INTO `gameobject_queststarter` (`id`, `quest`) VALUES (770200, 77061), (770200, 77062), (770200, 77063);
DELETE FROM `gameobject_questender` WHERE `quest` BETWEEN 77061 AND 77063;
INSERT INTO `gameobject_questender` (`id`, `quest`) VALUES (770200, 77061), (770200, 77062), (770200, 77063);

-- Where the map shows them (Icecrown's map, 492), once a quest is in the log: the coffer for
-- each turn-in (objective -1), the runestones, the Great Hourglass, the coffer to kneel at. (The
-- guide, src/RemixGuide.cpp, flags these too; nothing points to the coffer before it's found.)
DELETE FROM `quest_poi` WHERE `QuestID` BETWEEN 77061 AND 77063;
INSERT INTO `quest_poi` (`QuestID`, `id`, `ObjectiveIndex`, `MapID`, `WorldMapAreaId`, `Floor`, `Priority`, `Flags`, `VerifiedBuild`) VALUES
(77061, 0, -1, 571, 492, 0, 0, 1, 0),
(77061, 1, 0, 571, 492, 0, 0, 3, 0),
(77061, 2, 1, 571, 492, 0, 0, 3, 0),
(77061, 3, 2, 571, 492, 0, 0, 3, 0),
(77062, 0, -1, 571, 492, 0, 0, 1, 0),
(77062, 1, 0, 571, 492, 0, 0, 3, 0),
(77063, 0, -1, 571, 492, 0, 0, 1, 0),
(77063, 1, 0, 571, 492, 0, 0, 3, 0);
DELETE FROM `quest_poi_points` WHERE `QuestID` BETWEEN 77061 AND 77063;
INSERT INTO `quest_poi_points` (`QuestID`, `Idx1`, `Idx2`, `X`, `Y`, `VerifiedBuild`) VALUES
(77061, 0, 0, 6262, 1840, 0),
(77061, 1, 0, 6267, 1840, 0),
(77061, 2, 0, 6260, 1844, 0),
(77061, 3, 0, 6260, 1836, 0),
(77062, 0, 0, 6262, 1840, 0),
(77062, 1, 0, 6394, 1898, 0),
(77063, 0, 0, 6262, 1840, 0),
(77063, 1, 0, 6262, 1840, 0);

-- The coffer once its plate is taken (src/RemixVileHoldSet.cpp: a piece lost is in the cloth again).
DELETE FROM `npc_text` WHERE `ID` BETWEEN 7702180 AND 7702199;
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES
(7702180, 'The coffer is empty but for its black cloth, still folded to the shape of the plate it held. The runestones around it are dark.$B$BThe cloth remembers what was in it.',
          'The coffer is empty but for its black cloth, still folded to the shape of the plate it held. The runestones around it are dark.$B$BThe cloth remembers what was in it.', 1);
