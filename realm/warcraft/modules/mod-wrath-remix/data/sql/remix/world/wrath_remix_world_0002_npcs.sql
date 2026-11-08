-- Wrath Remix's people (STORY.md): Eternus of the Infinite Dragonflight, who brings Timerunners to
-- Northrend to change the Lich King's war, her lieutenant Moratari, the Keepers of Time, the
-- prologue's echoes of the war's dead and its anomalies, the Bazaar's instructors, and from
-- Chapter II Sylvanas and Alleria Windrunner and Eternus's loyalists. New entries
-- in Remix's own range (770001+), on models the 3.3.5a client has: Moratari is a blood elf woman in
-- dark plate with glowing runes (Lady Alistra's look), Eternus the Infinite Dragonflight's
-- Chrono-Lord Epoch, the Keepers their own Caverns of Time selves, the echoes the people they were.
-- Moratari has no title over her head: she meets the Timerunner beside quest givers all over
-- Northrend, and there she is one more traveler in a war full of them.
-- Her own spawns (where she waits at her posts) are out of creatures' fights (unit_flags 512,
-- immune to NPCs): Eternus's loyalists stand by some of them, and their faction (2111) counts hers
-- an enemy. As the companion she fights beside the Timerunner (src/RemixMoratari.cpp clears it).

SET @MORATARI := 770001, @ETERNUS := 770002, @ANDORMU := 770003, @NOZARI := 770004,
    @ALURMI := 770005, @ZEPHYR := 770006, @SAAT := 770007, @CHRONOLOGIST := 770008,
    @MOMENTUS := 770009, @ECHO_FOOTMAN := 770021, @ECHO_SAURFANG := 770022,
    @ECHO_BOLVAR := 770023, @ANOMALY := 770031, @ANOMALY_CREDIT := 770032, @INSTRUCTOR_CREDIT := 770033,
    @SYLVANAS := 770011, @ALLERIA := 770012, @MORATARI_SCENE := 770013, @TURN_CREDIT := 770034,
    @INTERLOPER := 770041, @SYLVANAS_ABROAD := 770014, @ALLERIA_ABROAD := 770015,
    @LESSON_1 := 770067, @LESSON_2 := 770068, @LESSON_3 := 770069,
    @PLAN_WHAT := 770049, @PLAN_HOW := 770050, @PLAN_WHY := 770058;

-- Until build 56 Remix's creatures were 7700001 and up, which made the core keep a table of
-- creature templates 7.7 million long (its fast lookups are indexed by entry): gone.
DELETE FROM `creature_template` WHERE `entry` BETWEEN 7700001 AND 7700199;
DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN 7700001 AND 7700199;
DELETE FROM `creature_template_addon` WHERE `entry` BETWEEN 7700001 AND 7700199;
DELETE FROM `creature_equip_template` WHERE `CreatureID` BETWEEN 7700001 AND 7700199;
DELETE FROM `creature_default_trainer` WHERE `CreatureId` BETWEEN 7700001 AND 7700199;

-- (the Bazaar's camp, 770070 to 770099, is wrath_remix_world_0023_bazaar.sql's, and the opening's,
-- 770120 to 770149, wrath_remix_world_0024_intro.sql's: left to them, so this file can change alone)
DELETE FROM `creature_template` WHERE `entry` BETWEEN 770001 AND 770199 AND `entry` NOT BETWEEN 770070 AND 770099 AND `entry` NOT BETWEEN 770120 AND 770149;
INSERT INTO `creature_template` (`entry`, `name`, `subname`, `minlevel`, `maxlevel`, `exp`, `faction`, `npcflag`,
  `speed_walk`, `speed_run`, `rank`, `unit_class`, `unit_flags`, `unit_flags2`, `type`, `flags_extra`,
  `HealthModifier`, `DamageModifier`, `BaseAttackTime`, `RegenHealth`, `ScriptName`) VALUES
(@MORATARI,       'Moratari',       NULL,                      80, 80, 2, 35, 3, 1, 1.14286, 0, 1, 512, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_moratari'),
(@ETERNUS,        'Eternus',        'Infinite Dragonflight',   83, 83, 2, 35, 3, 1, 1.14286, 3, 2, 0, 2048, 2, 2, 25, 1, 2000, 1, 'npc_remix_eternus'),
(@ANDORMU,        'Andormu',        'Keepers of Time',         80, 80, 2, 35, 3, 1, 1.14286, 0, 1, 0, 2048, 2, 2, 10, 1, 2000, 1, 'npc_remix_keeper'),
(@NOZARI,         'Nozari',         'Keepers of Time',         80, 80, 2, 35, 3, 1, 1.14286, 0, 1, 0, 2048, 2, 2, 10, 1, 2000, 1, 'npc_remix_keeper'),
(@ALURMI,         'Alurmi',         'Bronze Quartermaster',    80, 80, 2, 35, 131, 1, 1.14286, 0, 1, 0, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_alurmi'),
(@ZEPHYR,         'Zephyr',         'Keeper of the Ways',      80, 80, 2, 35, 1, 1, 1.14286, 0, 1, 0, 2048, 2, 2, 10, 1, 2000, 1, 'npc_remix_zephyr'),
(@SAAT,           'Sa''at',         'Timeline Safety',         80, 80, 2, 35, 1, 1, 1.14286, 0, 1, 0, 2048, 2, 2, 10, 1, 2000, 1, 'npc_remix_saat'),
(@CHRONOLOGIST,   'Chronologist',   'Wrath Remix',             80, 80, 2, 35, 1, 1, 1.14286, 0, 1, 0, 2048, 2, 2, 10, 1, 2000, 1, 'npc_remix_chronologist'),
(@MOMENTUS,       'Momentus',       'Weaponmaster',            80, 80, 2, 35, 1, 1, 1.14286, 0, 2, 0, 2048, 2, 2, 10, 1, 2000, 1, 'npc_remix_momentus'),
-- The war's dead as Eternus shows them, frozen at the moment they fell.
(@ECHO_FOOTMAN,   'Echo of a Fallen Footman', 'Valiance Keep, the first day', 80, 80, 2, 35, 1, 1, 1.14286, 0, 1, 0, 2048, 7, 2, 1, 1, 2000, 1, 'npc_remix_echo'),
(@ECHO_SAURFANG,  'Echo of Dranosh Saurfang', 'Angrathar, the Wrathgate',     80, 80, 2, 35, 1, 1, 1.14286, 0, 1, 0, 2048, 7, 2, 1, 1, 2000, 1, 'npc_remix_echo'),
(@ECHO_BOLVAR,    'Echo of Bolvar Fordragon', 'Angrathar, the Wrathgate',     80, 80, 2, 35, 1, 1, 1.14286, 0, 1, 0, 2048, 7, 2, 1, 1, 2000, 1, 'npc_remix_echo'),
(@ANOMALY,        'Temporal Anomaly', NULL,                    10, 10, 0, 14, 0, 1, 1.14286, 0, 1, 0, 2048, 2, 0, 0.8, 0.5, 2000, 1, 'npc_remix_anomaly'),
-- WRM-013's credit (never spawned): each anomaly's death gives it to the Timerunner it came for,
-- whoever struck the blow (a passing bot, Moratari's company).
(@ANOMALY_CREDIT, 'Temporal Anomaly', NULL,                    10, 10, 0, 14, 0, 1, 1.14286, 0, 1, 0, 2048, 2, 128, 1, 1, 2000, 1, ''),
-- WRM-012's (never spawned): given by any of the Bazaar's instructors as they're spoken to.
(@INSTRUCTOR_CREDIT, 'Your class''s instructor', NULL,          80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
-- WRM-011's (never spawned): each of the three things the Timerunner asks Eternus.
(@PLAN_WHAT,      'What Eternus wants', NULL,                  80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(@PLAN_HOW,       'How it is done', NULL,                      80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(@PLAN_WHY,       'Why you', NULL,                             80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
-- The class lessons' (wrath_remix_world_0025_lessons.sql; never spawned): each of a lesson's three
-- abilities used as the instructor asks (src/RemixLessons.cpp).
(@LESSON_1,       'A lesson''s first ability', NULL,           80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(@LESSON_2,       'A lesson''s second ability', NULL,          80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(@LESSON_3,       'A lesson''s third ability', NULL,           80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
-- Chapter II (wrath_remix_world_0011_chapter2.sql): Sylvanas and Alleria Windrunner, brought back
-- from the future by the bronze; Moratari as WRM-207's scene has her (seen by one Timerunner, no
-- quests); its credit (never spawned).
(@SYLVANAS,       'Sylvanas Windrunner', NULL,                 83, 83, 2, 35, 3, 1, 1.14286, 3, 2, 0, 2048, 7, 2, 25, 1, 2000, 1, 'npc_remix_windrunner'),
(@ALLERIA,        'Alleria Windrunner',  NULL,                 83, 83, 2, 35, 3, 1, 1.14286, 3, 1, 0, 2048, 7, 2, 25, 1, 2000, 1, 'npc_remix_windrunner'),
-- The same two anywhere but the Bazaar: hooded, and passing for two more adventurers in a war
-- full of them. This year's Sylvanas must never hear of the other one, and no one else may
-- learn who they are.
(@SYLVANAS_ABROAD, 'Hooded Ranger',  'Adventurer',             80, 80, 2, 35, 3, 1, 1.14286, 0, 2, 0, 2048, 7, 2, 25, 1, 2000, 1, 'npc_remix_windrunner'),
(@ALLERIA_ABROAD,  'Cloaked Ranger', 'Adventurer',             80, 80, 2, 35, 3, 1, 1.14286, 0, 1, 0, 2048, 7, 2, 25, 1, 2000, 1, 'npc_remix_windrunner'),
(@MORATARI_SCENE, 'Moratari',       'Infinite Dragonflight',   80, 80, 2, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 2, 10, 1, 2000, 1, ''),
(@TURN_CREDIT,    'What Sylvanas came to say', NULL,           80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, '');

-- Eternus's loyalists on the Wrathgate's cliffs (WRM-208): the Infinite Assailants of Chromie's
-- hourglass under another name, at the Dragonblight's levels like them.
DROP TEMPORARY TABLE IF EXISTS `remix_interloper`;
CREATE TEMPORARY TABLE `remix_interloper` SELECT * FROM `creature_template` WHERE `entry` = 27896;
UPDATE `remix_interloper` SET `entry` = @INTERLOPER, `name` = 'Infinite Interloper', `subname` = 'Eternus''s Loyalist',
  `ScriptName` = 'npc_remix_story_foe', `AIName` = '', `KillCredit1` = 0, `KillCredit2` = 0;
INSERT INTO `creature_template` SELECT * FROM `remix_interloper`;
DROP TEMPORARY TABLE `remix_interloper`;

-- After the turn (STORY.md, "After the turn" and "The end"): the people the scenes stage (seen by
-- one Timerunner, no quests, no gossip: RemixScenes.cpp), Eternus's agents in each chapter (their
-- deaths count for every Timerunner nearby who needs them), Eternus at the last hour with her
-- loyalists, the three who fight beside the Timerunner there, and the credits the story gives.
-- The agents' levels are their zone's own (each chapter's band makes them the chapter's).
SET @ACT_SYLVANAS := 770051, @ACT_ALLERIA := 770052, @ACT_ETERNUS := 770053, @ACT_THORIM := 770054,
    @ACT_SIF := 770055, @ACT_ANDORMU := 770056, @ACT_NOZARI := 770057,
    @ANCHOR := 770042, @REWINDER := 770043, @TIMESNATCHER := 770044, @RIFT := 770045,
    @SIPHONER := 770046, @SIPHON := 770047, @WEAVER := 770048,
    @LAST_ETERNUS := 770061, @LAST_CHRONOMANCER := 770062, @LAST_EXECUTIONER := 770063,
    @ALLY_MORATARI := 770064, @ALLY_SYLVANAS := 770065, @ALLY_ALLERIA := 770066,
    @LAST_HOUR_CREDIT := 770036, @BYE_SYLVANAS := 770037, @BYE_ALLERIA := 770038, @BYE_ANDORMU := 770039,
    @BYE_NOZARI := 770040, @ROAD_CREDIT := 770035;
INSERT INTO `creature_template` (`entry`, `name`, `subname`, `minlevel`, `maxlevel`, `exp`, `faction`, `npcflag`,
  `speed_walk`, `speed_run`, `rank`, `unit_class`, `unit_flags`, `unit_flags2`, `type`, `flags_extra`,
  `HealthModifier`, `DamageModifier`, `BaseAttackTime`, `RegenHealth`, `ScriptName`) VALUES
-- The scenes' people (unit flags: not attackable, nor attacking). Sylvanas and Alleria are only
-- ever in scenes out in the world, so in their disguises.
(@ACT_SYLVANAS,  'Hooded Ranger',  'Adventurer',             80, 80, 2, 35, 0, 1, 1.14286, 0, 2, 770, 2048, 7, 2, 25, 1, 2000, 1, ''),
(@ACT_ALLERIA,   'Cloaked Ranger', 'Adventurer',             80, 80, 2, 35, 0, 1, 1.14286, 0, 1, 770, 2048, 7, 2, 25, 1, 2000, 1, ''),
(@ACT_ETERNUS,   'Eternus',        'Infinite Dragonflight',  83, 83, 2, 35, 0, 1, 1.14286, 3, 2, 770, 2048, 2, 2, 25, 1, 2000, 1, ''),
(@ACT_THORIM,    'Thorim',         NULL,                     82, 82, 2, 35, 0, 1, 1.14286, 3, 1, 770, 2048, 7, 2, 25, 1, 2000, 1, ''),
(@ACT_SIF,       'Echo of Sif',    NULL,                     80, 80, 2, 35, 0, 1, 1.14286, 0, 1, 770, 2048, 7, 2, 1, 1, 2000, 1, ''),
(@ACT_ANDORMU,   'Andormu',        'Keepers of Time',        80, 80, 2, 35, 0, 1, 1.14286, 0, 1, 770, 2048, 2, 2, 10, 1, 2000, 1, ''),
(@ACT_NOZARI,    'Nozari',         'Keepers of Time',        80, 80, 2, 35, 0, 1, 1.14286, 0, 1, 770, 2048, 2, 2, 10, 1, 2000, 1, ''),
-- Chapter III: the Temporal Anchors at Ursoc's Den, and their Infinite Rewinders.
(@ANCHOR,        'Temporal Anchor', 'Eternus''s Working',     74, 74, 2, 2111, 0, 1, 1.14286, 0, 1, 4, 2048, 10, 0, 2.5, 0.2, 2000, 1, 'npc_remix_story_foe'),
(@REWINDER,      'Infinite Rewinder', 'Eternus''s Loyalist',  74, 74, 2, 2111, 0, 1, 1.14286, 0, 8, 0, 2048, 2, 0, 1.2, 1, 2000, 1, 'npc_remix_story_foe'),
-- Chapter IV: beneath Voltarus.
(@TIMESNATCHER,  'Infinite Timesnatcher', 'Eternus''s Loyalist', 76, 76, 2, 2111, 0, 1, 1.14286, 0, 1, 0, 2048, 2, 0, 1.2, 1.1, 2000, 1, 'npc_remix_story_foe'),
(@RIFT,          'Unstable Rift',  'Eternus''s Working',      76, 76, 2, 2111, 0, 1, 1.14286, 0, 1, 4, 2048, 10, 0, 4, 0.2, 2000, 1, 'npc_remix_story_foe'),
-- Chapter V: the Maker's Overlook.
(@SIPHONER,      'Infinite Siphoner', 'Eternus''s Loyalist',  77, 77, 2, 2111, 0, 1, 1.14286, 0, 8, 0, 2048, 2, 0, 1.2, 1, 2000, 1, 'npc_remix_story_foe'),
(@SIPHON,        'Siphon of Hours', 'Eternus''s Working',     77, 77, 2, 2111, 0, 1, 1.14286, 0, 1, 4, 2048, 10, 0, 4, 0.2, 2000, 1, 'npc_remix_story_foe'),
-- Chapter VI: the Terrace of the Makers.
(@WEAVER,        'Infinite Weaver', 'Eternus''s Loyalist',    79, 79, 2, 2111, 0, 1, 1.14286, 0, 8, 0, 2048, 2, 0, 1.5, 1.1, 2000, 1, 'npc_remix_story_foe'),
-- Chapter VII: the last hour, at the doors of Icecrown Citadel.
(@LAST_ETERNUS,  'Eternus',        'The Last Hour',          80, 80, 2, 2111, 0, 1, 1.14286, 3, 2, 0, 2048, 2, 0, 40, 2.5, 2000, 1, 'npc_remix_eternus_last_hour'),
(@LAST_CHRONOMANCER, 'Infinite Chronomancer', 'Eternus''s Loyalist', 80, 80, 2, 2111, 0, 1, 1.14286, 0, 8, 0, 2048, 2, 0, 1.5, 1, 2000, 1, 'npc_remix_story_foe'),
(@LAST_EXECUTIONER,  'Infinite Executioner',  'Eternus''s Loyalist', 80, 80, 2, 2111, 0, 1, 1.14286, 0, 1, 0, 2048, 2, 0, 2, 1.2, 2000, 1, 'npc_remix_story_foe'),
(@ALLY_MORATARI, 'Moratari',       NULL,                     80, 80, 2, 35, 0, 1, 1.14286, 1, 8, 0, 2048, 7, 0, 60, 1.5, 2000, 1, 'npc_remix_last_hour_ally'),
(@ALLY_SYLVANAS, 'Hooded Ranger',  'Adventurer',           80, 80, 2, 35, 0, 1, 1.14286, 1, 1, 0, 2048, 7, 0, 60, 2, 2000, 1, 'npc_remix_last_hour_ally'),
(@ALLY_ALLERIA,  'Cloaked Ranger', 'Adventurer',           80, 80, 2, 35, 0, 1, 1.14286, 1, 1, 0, 2048, 7, 0, 60, 2, 2000, 1, 'npc_remix_last_hour_ally'),
-- Credits (never spawned).
(@ROAD_CREDIT,       'What was said, heard', NULL,            80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(@LAST_HOUR_CREDIT,  'Eternus driven off', NULL,             80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(@BYE_SYLVANAS,      'Goodbye said to Sylvanas', NULL,       80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(@BYE_ALLERIA,       'Goodbye said to Alleria', NULL,        80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(@BYE_ANDORMU,       'Goodbye said to Andormu', NULL,        80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, ''),
(@BYE_NOZARI,        'Goodbye said to Nozari', NULL,         80, 80, 0, 35, 0, 1, 1.14286, 0, 1, 0, 2048, 7, 128, 1, 1, 2000, 1, '');

DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN 770001 AND 770199 AND `CreatureID` NOT BETWEEN 770070 AND 770099 AND `CreatureID` NOT BETWEEN 770120 AND 770149;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) VALUES
(@MORATARI, 0, 25458, 1, 1, 0),
(@ETERNUS, 0, 26580, 1, 1, 0),
(@ANDORMU, 0, 19267, 1, 1, 0),
(@NOZARI, 0, 19268, 1, 1, 0),
(@ALURMI, 0, 20384, 1, 1, 0),
(@ZEPHYR, 0, 19282, 1, 1, 0),
(@SAAT, 0, 19411, 1, 1, 0),
(@CHRONOLOGIST, 0, 27756, 1, 1, 0),   -- a bronze dragon as a woman of Lordaeron (Zidormi's look)
(@MOMENTUS, 0, 19062, 1, 1, 0),      -- an armoured infinite dragonspawn (an Infinite Executioner's), as Legion Remix's weaponmaster
(@ECHO_FOOTMAN, 0, 23031, 1, 1, 0),    -- a Valiance Keep Footman
(@ECHO_SAURFANG, 0, 23034, 1, 1, 0),   -- Saurfang the Younger
(@ECHO_BOLVAR, 0, 24879, 1, 1, 0),     -- Highlord Bolvar Fordragon at the Wrathgate
(@ANOMALY, 0, 20515, 1, 1, 0),
(@ANOMALY_CREDIT, 0, 20515, 1, 1, 0),
(@INSTRUCTOR_CREDIT, 0, 19373, 1, 1, 0),
(@PLAN_WHAT, 0, 26580, 1, 1, 0),
(@PLAN_HOW, 0, 26580, 1, 1, 0),
(@PLAN_WHY, 0, 26580, 1, 1, 0),
(@LESSON_1, 0, 19373, 1, 1, 0),
(@LESSON_2, 0, 19373, 1, 1, 0),
(@LESSON_3, 0, 19373, 1, 1, 0),
(@SYLVANAS, 0, 28213, 1, 1, 0),       -- the Banshee Queen as Wrath has her
(@ALLERIA, 0, 21741, 1, 1, 0),        -- a living high elf ranger-general: the 3.3.5 game has no Alleria
(@SYLVANAS_ABROAD, 0, 21746, 1, 1, 0), -- an elf woman in a black hood and cloak, as rangers go about
(@ALLERIA_ABROAD, 0, 21741, 1, 1, 0),  -- her own hood and cloak, the blue ones
(@MORATARI_SCENE, 0, 25458, 1, 1, 0),
(@TURN_CREDIT, 0, 28213, 1, 1, 0),
(@INTERLOPER, 0, 19059, 1, 1, 0),
(@INTERLOPER, 1, 19062, 1, 1, 0),
(@ACT_SYLVANAS, 0, 21746, 1, 1, 0),
(@ACT_ALLERIA, 0, 21741, 1, 1, 0),
(@ACT_ETERNUS, 0, 26580, 1, 1, 0),
(@ACT_THORIM, 0, 28977, 1, 1, 0),
(@ACT_SIF, 0, 28488, 1, 1, 0),
(@ACT_ANDORMU, 0, 19267, 1, 1, 0),
(@ACT_NOZARI, 0, 19268, 1, 1, 0),
(@ANCHOR, 0, 25392, 0.6, 1, 0),        -- a small rift in time
(@REWINDER, 0, 19061, 1, 1, 0),
(@REWINDER, 1, 19063, 1, 1, 0),
(@TIMESNATCHER, 0, 19059, 1, 1, 0),
(@TIMESNATCHER, 1, 19062, 1, 1, 0),
(@RIFT, 0, 25392, 1, 1, 0),
(@SIPHONER, 0, 19061, 1, 1, 0),
(@SIPHONER, 1, 19063, 1, 1, 0),
(@SIPHON, 0, 25392, 0.8, 1, 0),
(@WEAVER, 0, 19060, 1, 1, 0),
(@WEAVER, 1, 19135, 1, 1, 0),
(@LAST_ETERNUS, 0, 26580, 1.2, 1, 0),
(@LAST_CHRONOMANCER, 0, 19061, 1, 1, 0),
(@LAST_EXECUTIONER, 0, 19062, 1, 1, 0),
(@ALLY_MORATARI, 0, 25458, 1, 1, 0),
(@ALLY_SYLVANAS, 0, 21746, 1, 1, 0),
(@ALLY_ALLERIA, 0, 21741, 1, 1, 0),
(@ROAD_CREDIT, 0, 25458, 1, 1, 0),
(@LAST_HOUR_CREDIT, 0, 26580, 1, 1, 0),
(@BYE_SYLVANAS, 0, 28213, 1, 1, 0),
(@BYE_ALLERIA, 0, 21741, 1, 1, 0),
(@BYE_ANDORMU, 0, 19267, 1, 1, 0),
(@BYE_NOZARI, 0, 19268, 1, 1, 0);

DELETE FROM `creature_template_addon` WHERE `entry` BETWEEN 770001 AND 770199 AND `entry` NOT BETWEEN 770070 AND 770099 AND `entry` NOT BETWEEN 770120 AND 770149;
INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) VALUES
-- The echoes: half seen, with motes of time about them.
(@ECHO_FOOTMAN, 0, 0, 0, 1, 0, 0, '44816 37119'),
(@ECHO_SAURFANG, 0, 0, 0, 1, 0, 0, '44816 37119'),
(@ECHO_BOLVAR, 0, 0, 0, 1, 0, 0, '44816 37119'),
-- Sif as Eternus weaves her out of the hours before she died: half there.
(@ACT_SIF, 0, 0, 0, 1, 0, 0, '44816 37119');

DELETE FROM `creature_equip_template` WHERE `CreatureID` BETWEEN 770001 AND 770199 AND `CreatureID` NOT BETWEEN 770070 AND 770099 AND `CreatureID` NOT BETWEEN 770120 AND 770149;
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) VALUES
(@MORATARI, 1, 39287, 0, 0, 0),
(@MORATARI_SCENE, 1, 39287, 0, 0, 0),
(@ETERNUS, 1, 38609, 0, 0, 0),
(@ZEPHYR, 1, 13861, 0, 0, 0),
(@MOMENTUS, 1, 12950, 0, 0, 0),     -- a warhammer
(@ACT_ETERNUS, 1, 38609, 0, 0, 0),
(@LAST_ETERNUS, 1, 38609, 0, 0, 0),
(@ALLY_MORATARI, 1, 39287, 0, 0, 0);

-- What Eternus's agents cast at whoever they fight (npc_remix_story_foe: one every few seconds).
DELETE FROM `creature_template_spell` WHERE `CreatureID` BETWEEN 770041 AND 770066;
INSERT INTO `creature_template_spell` (`CreatureID`, `Index`, `Spell`, `VerifiedBuild`) VALUES
(@REWINDER, 0, 9613, 0),              -- Shadow Bolt
(@REWINDER, 1, 51020, 0),             -- Time Lapse
(@TIMESNATCHER, 0, 15580, 0),         -- Strike
(@TIMESNATCHER, 1, 52772, 0),         -- Curse of Exertion
(@SIPHONER, 0, 15124, 0),             -- Arcane Bolt
(@SIPHONER, 1, 52657, 0),             -- Temporal Vortex
(@WEAVER, 0, 38085, 0),               -- Shadow Blast
(@WEAVER, 1, 51020, 0),               -- Time Lapse
(@LAST_CHRONOMANCER, 0, 15124, 0),    -- Arcane Bolt
(@LAST_CHRONOMANCER, 1, 52657, 0),    -- Temporal Vortex
(@LAST_EXECUTIONER, 0, 15580, 0),     -- Strike
(@LAST_EXECUTIONER, 1, 52771, 0);     -- Wounding Strike

-- What each of them says when spoken to (the module picks the text).
DELETE FROM `npc_text` WHERE `ID` BETWEEN 7702001 AND 7702099;
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES
-- Moratari: before the first quest is done, as you wake; after; on where you are in history.
(7702001, 'Steady. That passes. Time is hard on a body the first time it is pulled through.$B$BYour friends are still at that table, in your own hour, mid-toast; no one there has missed you, and no one will. Here, it is the year the war began, and none of what I showed you has happened yet.$B$BI am Moratari. Eternus sent me for you, and she will tell you why herself: she is just there.',
          'Steady. That passes. Time is hard on a body the first time it is pulled through.$B$BYour friends are still at that table, in your own hour, mid-toast; no one there has missed you, and no one will. Here, it is the year the war began, and none of what I showed you has happened yet.$B$BI am Moratari. Eternus sent me for you, and she will tell you why herself: she is just there.', 1),
(7702002, 'Hello again, Timerunner. The war is still where we left it. That is either reassuring or the problem, depending on whom you ask.',
          'Hello again, Timerunner. The war is still where we left it. That is either reassuring or the problem, depending on whom you ask.', 1),
(7702003, 'Every Timerunner I have sent into this war, I can find again. If you lose your way, I will return you to the start of the chapter you are in.',
          'Every Timerunner I have sent into this war, I can find again. If you lose your way, I will return you to the start of the chapter you are in.', 1),
-- Eternus.
(7702010, 'I have watched this war more times than I can count, champion. Every time, the same graves. I did not bring you here to watch it with me.',
          'I have watched this war more times than I can count, champion. Every time, the same graves. I did not bring you here to watch it with me.', 1),
(7702011, 'The bronze will tell you history is sacred. The bronze let Stratholme burn, and called it duty. I would rather save someone.',
          'The bronze will tell you history is sacred. The bronze let Stratholme burn, and called it duty. I would rather save someone.', 1),
(7702012, 'Fewer graves. That is all.$B$BI cannot stop the Lich King''s war: it is too large, and history pushes back against anyone who leans on it too hard. But a war is made of a thousand small moments. A scout who comes back. A tunnel found a day early. A supply cart that arrives. Change enough of the small ones, and the large ones begin to change on their own.$B$BWith you, this war can be won sooner, and cheaper, than you won it the first time.',
          'Fewer graves. That is all.$B$BI cannot stop the Lich King''s war: it is too large, and history pushes back against anyone who leans on it too hard. But a war is made of a thousand small moments. A scout who comes back. A tunnel found a day early. A supply cart that arrives. Change enough of the small ones, and the large ones begin to change on their own.$B$BWith you, this war can be won sooner, and cheaper, than you won it the first time.', 1),
(7702013, 'Quietly. You will fight this war again from its first day, beside the same people, and wherever you know a little more than you should, you will use it.$B$BBut no one of this year may ever learn what you are. Not a general, not a friend, not a king. If they knew, they would act on what they knew, and the war would come apart in ways neither of us could follow. A good hunch, a lucky patrol, a careful look at the right map: that is all they may ever see. Some of them will not believe you anyway. Let them doubt; then let them find it for themselves.$B$BAnd it cannot last. Time will let us lean on it for a while, never for good: one day this experiment ends, and you go home. Be wise with the days it gives you.$B$BMoratari will be with you. She knows this war as well as I do, and she whispers better.',
          'Quietly. You will fight this war again from its first day, beside the same people, and wherever you know a little more than you should, you will use it.$B$BBut no one of this year may ever learn what you are. Not a general, not a friend, not a king. If they knew, they would act on what they knew, and the war would come apart in ways neither of us could follow. A good hunch, a lucky patrol, a careful look at the right map: that is all they may ever see. Some of them will not believe you anyway. Let them doubt; then let them find it for themselves.$B$BAnd it cannot last. Time will let us lean on it for a while, never for good: one day this experiment ends, and you go home. Be wise with the days it gives you.$B$BMoratari will be with you. She knows this war as well as I do, and she whispers better.', 1),
(7702014, 'Because you were there. You know where this war bleeds, because you bled there too.$B$BAnd because you lost someone in it. Everyone I choose has. It makes them careful in a way my kin have forgotten how to be.',
          'Because you were there. You know where this war bleeds, because you bled there too.$B$BAnd because you lost someone in it. Everyone I choose has. It makes them careful in a way my kin have forgotten how to be.', 1),
-- The Keepers of Time (with Sylvanas and Alleria, after the turn).
(7702020, 'The Infinite were always going to try this. We were always going to need someone who remembers how it ends.',
          'The Infinite were always going to try this. We were always going to need someone who remembers how it ends.', 1),
(7702021, 'I keep the record of every change the Infinite have tried, and every one you have stopped. It is a long record. Yours is a good part of it.',
          'I keep the record of every change the Infinite have tried, and every one you have stopped. It is a long record. Yours is a good part of it.', 1),
-- The Bazaar's services.
(7702030, 'Bronze, Timerunner. Time leaves it everywhere you go: every errand finished, every foe felled. I trade in it, and I do not ask whose side you are on.',
          'Bronze, Timerunner. Time leaves it everywhere you go: every errand finished, every foe felled. I trade in it, and I do not ask whose side you are on.', 1),
(7702040, 'Every road in Northrend runs through this camp, if you know how to fold it. Where to?',
          'Every road in Northrend runs through this camp, if you know how to fold it. Where to?', 1),
(7702050, 'The dungeons of Northrend keep their own hours. Here they keep yours: each is waiting at the level of the chapter it belongs to.',
          'The dungeons of Northrend keep their own hours. Here they keep yours: each is waiting at the level of the chapter it belongs to.', 1),
(7702060, 'Seven chapters, ten levels to eighty, and the Lich King at the end of them. Here is where you stand.',
          'Seven chapters, ten levels to eighty, and the Lich King at the end of them. Here is where you stand.', 1),
(7702070, 'There are few problems that a little heat and a hammer cannot solve.$B$BEvery weapon your hands were made for, $c: I will teach you all of them, today, as if you had trained with each for years. No Bronze for this. We forge our own futures.',
          'There are few problems that a little heat and a hammer cannot solve.$B$BEvery weapon your hands were made for, $c: I will teach you all of them, today, as if you had trained with each for years. No Bronze for this. We forge our own futures.', 1),
-- The echoes (WRM-011): the dead Eternus means to save.
(7702080, 'The boats came in under the arrows and the cold. I made it off the beach. I did not make it off the second day. When I stood up again, I was fighting for them.',
          'The boats came in under the arrows and the cold. I made it off the beach. I did not make it off the second day. When I stood up again, I was fighting for them.', 1),
(7702081, 'For the Horde... The gate opened, and he came down to meet us himself. I reached him first. Tell my father I did not run.',
          'For the Horde... The gate opened, and he came down to meet us himself. I reached him first. Tell my father I did not run.', 1),
(7702082, 'The plague, then the fire. Then the cold, and a voice telling me that someone has to hold it. It is so very cold.',
          'The plague, then the fire. Then the cold, and a voice telling me that someone has to hold it. It is so very cold.', 1),
-- Sylvanas and Alleria (Chapter II): atop Wyrmrest Temple, at the Bazaar after the turn, and
-- Alleria on the Wrathgate's cliffs; then Alleria at the Bazaar from Chapter V, from Chapter VII
-- and once the war is over (keeping the Timerunner at arm's length less and less: STORY.md), and
-- in the Grizzly Hills (npc_remix_windrunner, RemixNpcs.cpp).
(7702090, 'The bronze brought us back to this year. I would not have chosen it.$B$BStand on my left. You always do. <She catches herself.> You will. It is a habit you have not given me yet.$B$BGo and ask your mistress what she means to do at the Wrathgate, Timerunner. Ask her who she thinks will wear the Helm when Arthas is gone.',
          'The bronze brought us back to this year. I would not have chosen it.$B$BStand on my left. You always do. <She catches herself.> You will. It is a habit you have not given me yet.$B$BGo and ask your mistress what she means to do at the Wrathgate, Timerunner. Ask her who she thinks will wear the Helm when Arthas is gone.', 1),
(7702091, 'Eternus will not stop, and neither will we. Every change her loyalists make, we unmake.$B$BI am not asking you to love the war as it was. Only to let it happen.$B$B<For a moment, she almost smiles.> You argued with me just like that, once. You will, I mean. Do not ask me when.',
          'Eternus will not stop, and neither will we. Every change her loyalists make, we unmake.$B$BI am not asking you to love the war as it was. Only to let it happen.$B$B<For a moment, she almost smiles.> You argued with me just like that, once. You will, I mean. Do not ask me when.', 1),
(7702092, '<The cloaked ranger looks at you a moment longer than a stranger would. Then she draws back her hood, only for you, and only for a moment.>$B$BAlleria Windrunner. You know the name, I think. Every history of the Second War ends with it: the ranger who followed Turalyon through the Dark Portal and never came home.$B$BIn your year, they still tell it that way. In mine, I came home. It took me a thousand years.$B$B<Her eyes move over you: your gear, your hands, the shadows under your eyes.>$B$BYou have not been sleeping.$B$B<She lifts the hood again, a little too quickly.>$B$BIt is nothing. A ranger notices things. I am here because my sister asked me to come, and she does not ask. I can feel when the shape of the world is wrong, Timerunner, and this year feels wrong, and it is getting worse. That is the whole of my interest in you.',
          '<The cloaked ranger looks at you a moment longer than a stranger would. Then she draws back her hood, only for you, and only for a moment.>$B$BAlleria Windrunner. You know the name, I think. Every history of the Second War ends with it: the ranger who followed Turalyon through the Dark Portal and never came home.$B$BIn your year, they still tell it that way. In mine, I came home. It took me a thousand years.$B$B<Her eyes move over you: your gear, your hands, the shadows under your eyes.>$B$BYou have not been sleeping.$B$B<She lifts the hood again, a little too quickly.>$B$BIt is nothing. A ranger notices things. I am here because my sister asked me to come, and she does not ask. I can feel when the shape of the world is wrong, Timerunner, and this year feels wrong, and it is getting worse. That is the whole of my interest in you.', 1),
(7702093, 'Moratari keeps the Bazaar now. She is a better host than Eternus was, and a worse liar.$B$BWhen Eternus moves again, I will feel it, and you will be the first to know. You are the one doing the work. That is the only reason.$B$B<She glances at you, and away.>$B$BHave you eaten? There is bread by the hourglass that the bronze pretend they did not bake. Do not look at me like that. A soldier who fights hungry fights badly, and I will not have Eternus win because you were too stubborn to sit down.',
          'Moratari keeps the Bazaar now. She is a better host than Eternus was, and a worse liar.$B$BWhen Eternus moves again, I will feel it, and you will be the first to know. You are the one doing the work. That is the only reason.$B$B<She glances at you, and away.>$B$BHave you eaten? There is bread by the hourglass that the bronze pretend they did not bake. Do not look at me like that. A soldier who fights hungry fights badly, and I will not have Eternus win because you were too stubborn to sit down.', 1),
(7702094, 'Below us, the gate. Somewhere behind us, the Forsaken who will betray everyone at it. And on these cliffs, Eternus''s loyalists, here to change it.$B$BWe let it happen, Timerunner. I have never had to stand still for anything harder.$B$B<She does not look at you.>$B$BStay where I can see you. For my sister''s sake. If you fall on these cliffs, she will never let me hear the end of it.',
          'Below us, the gate. Somewhere behind us, the Forsaken who will betray everyone at it. And on these cliffs, Eternus''s loyalists, here to change it.$B$BWe let it happen, Timerunner. I have never had to stand still for anything harder.$B$B<She does not look at you.>$B$BStay where I can see you. For my sister''s sake. If you fall on these cliffs, she will never let me hear the end of it.', 1),
(7702095, 'You are back. Good. Moratari was asking.$B$B<She is restringing a bow that does not need it.>$B$BYou go into every fight half a step ahead of everyone else, $n. You always have. You think it is courage. It is a habit, and one day it will be the wrong habit, and I will not always be there to pull you back by the collar.$B$B<Her hands stop.>$B$BHere, I mean. I will not always be here. Go on. History is waiting, and it is even less patient than I am.',
          'You are back. Good. Moratari was asking.$B$B<She is restringing a bow that does not need it.>$B$BYou go into every fight half a step ahead of everyone else, $n. You always have. You think it is courage. It is a habit, and one day it will be the wrong habit, and I will not always be there to pull you back by the collar.$B$B<Her hands stop.>$B$BHere, I mean. I will not always be here. Go on. History is waiting, and it is even less patient than I am.', 1),
(7702096, 'The Citadel. I can feel it from here: a cold that goes all the way down.$B$B<She steps closer than she usually allows, and straightens something on your shoulder that was already straight.>$B$BListen to me. When you go up there, you will want to stand between him and everyone else. You will. I know you will. Let us stand there with you, for once.$B$BThere is something I would tell you, $n, if things were otherwise. They are not. Ask me after.$B$B<She steps back to where she always stands.>$B$BAnd do not make that face. It is not as if I would miss you.',
          'The Citadel. I can feel it from here: a cold that goes all the way down.$B$B<She steps closer than she usually allows, and straightens something on your shoulder that was already straight.>$B$BListen to me. When you go up there, you will want to stand between him and everyone else. You will. I know you will. Let us stand there with you, for once.$B$BThere is something I would tell you, $n, if things were otherwise. They are not. Ask me after.$B$B<She steps back to where she always stands.>$B$BAnd do not make that face. It is not as if I would miss you.', 1),
(7702097, 'It is done. Arthas is dead, Bolvar holds the cold, and the world has its ending back.$B$BAsk what you want to ask, Timerunner. I will answer what I can, while either of us still remembers it.$B$B<She adds, without looking at you:>$B$BAnd you will say goodbye before you go. Properly. I will not be left standing here wondering whether you meant to.',
          'It is done. Arthas is dead, Bolvar holds the cold, and the world has its ending back.$B$BAsk what you want to ask, Timerunner. I will answer what I can, while either of us still remembers it.$B$B<She adds, without looking at you:>$B$BAnd you will say goodbye before you go. Properly. I will not be left standing here wondering whether you meant to.', 1),
(7702098, 'The people here walk these woods as though nothing under them could hurt anyone. I envy them that.$B$B<She looks you over, quickly, the way a ranger reads a trail.>$B$BYou came up through the hills on your own again. You always do that.$B$B<A pause.>$B$BYou look like someone who would, I mean. Keep your back to something solid, Timerunner. I would rather not explain to my sister how I lost you to a bear.',
          'The people here walk these woods as though nothing under them could hurt anyone. I envy them that.$B$B<She looks you over, quickly, the way a ranger reads a trail.>$B$BYou came up through the hills on your own again. You always do that.$B$B<A pause.>$B$BYou look like someone who would, I mean. Keep your back to something solid, Timerunner. I would rather not explain to my sister how I lost you to a bear.', 1);

-- The Bazaar's instructors: one for each class, every rank of every spell up to your level, as a
-- capital's trainer teaches them (their trainer lists are the capitals' own), and the class's lesson
-- (wrath_remix_world_0025_lessons.sql). Paladins have two, for the Alliance's and the Horde's seals.
DELETE FROM `creature_template` WHERE `entry` BETWEEN 770101 AND 770112;
INSERT INTO `creature_template` (`entry`, `name`, `subname`, `minlevel`, `maxlevel`, `exp`, `faction`, `npcflag`,
  `speed_walk`, `speed_run`, `rank`, `unit_class`, `unit_flags`, `unit_flags2`, `type`, `flags_extra`,
  `HealthModifier`, `DamageModifier`, `BaseAttackTime`, `RegenHealth`, `ScriptName`) VALUES
(770101, 'Timeworn Instructor', 'Warrior Trainer',          80, 80, 2, 35, 51, 1, 1.14286, 0, 1, 0, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_instructor'),
(770102, 'Timeworn Instructor', 'Paladin Trainer',          80, 80, 2, 35, 51, 1, 1.14286, 0, 2, 0, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_instructor'),
(770103, 'Timeworn Instructor', 'Paladin Trainer (Horde)',  80, 80, 2, 35, 51, 1, 1.14286, 0, 2, 0, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_instructor'),
(770104, 'Timeworn Instructor', 'Hunter Trainer',           80, 80, 2, 35, 51, 1, 1.14286, 0, 1, 0, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_instructor'),
(770105, 'Timeworn Instructor', 'Rogue Trainer',            80, 80, 2, 35, 51, 1, 1.14286, 0, 1, 0, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_instructor'),
(770106, 'Timeworn Instructor', 'Priest Trainer',           80, 80, 2, 35, 51, 1, 1.14286, 0, 2, 0, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_instructor'),
(770107, 'Timeworn Instructor', 'Death Knight Trainer',     80, 80, 2, 35, 51, 1, 1.14286, 0, 1, 0, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_instructor'),
(770108, 'Timeworn Instructor', 'Shaman Trainer',           80, 80, 2, 35, 51, 1, 1.14286, 0, 2, 0, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_instructor'),
(770109, 'Timeworn Instructor', 'Mage Trainer',             80, 80, 2, 35, 51, 1, 1.14286, 0, 8, 0, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_instructor'),
(770110, 'Timeworn Instructor', 'Warlock Trainer',          80, 80, 2, 35, 51, 1, 1.14286, 0, 8, 0, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_instructor'),
(770111, 'Timeworn Instructor', 'Druid Trainer',            80, 80, 2, 35, 51, 1, 1.14286, 0, 2, 0, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_instructor');

-- Each one a teacher out of another year and another people, as they would stand in a capital:
-- an orc's warrior, a human's and a blood elf's paladins, a tauren hunter, a night elf rogue, a
-- human priestess, a death knight, an orc shaman, a gnome mage, an orc warlock, a night elf druid.
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) VALUES
(770101, 0, 4556, 1, 1, 0),     -- Malosh's look
(770102, 0, 1499, 1, 1, 0),     -- Lord Grayson Shadowbreaker's
(770103, 0, 15521, 1, 1, 0),    -- Jesthenis Sunstriker's
(770104, 0, 2112, 1, 1, 0),     -- Kary Thunderhorn's
(770105, 0, 1725, 1, 1, 0),     -- Frahun Shadewhisper's
(770106, 0, 1495, 1, 1, 0),     -- High Priestess Laurena's
(770107, 0, 25468, 1, 1, 0),    -- Amal'thazad's
(770108, 0, 1360, 1, 1, 0),     -- Kardris Dreamseeker's
(770109, 0, 3108, 1, 1, 0),     -- Bink's
(770110, 0, 1326, 1, 1, 0),     -- Zevrost's
(770111, 0, 2261, 1, 1, 0);     -- Mathrengyl Bearwalker's

DELETE FROM `creature_default_trainer` WHERE `CreatureId` BETWEEN 770101 AND 770112;
INSERT INTO `creature_default_trainer` (`CreatureId`, `TrainerId`) VALUES
(770101, 1), (770102, 3), (770103, 4), (770104, 7), (770105, 9), (770106, 11),
(770107, 13), (770108, 14), (770109, 16), (770110, 31), (770111, 33);
