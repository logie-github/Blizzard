-- The old races' new classes (mod-allied-races) train at another class's trainers: the core gives them their
-- own class's trainer there (patches/azerothcore/0011), and this gives them that class's trainers' words and
-- options. Undead paladins and dwarf shamans train at the priest trainers, human hunters at the warrior
-- trainers, gnome priests and troll warlocks at the mage trainers, orc mages at the warlock trainers.
-- A class's trainers offer training, unlearning talents and dual specialization to their own class alone
-- (conditions: the class), and greet everyone else with "I can't train you". Each such condition gets a
-- second way through for each pair (an ElseGroup of its own): the pair's race and class, with the rest of the
-- first way's conditions; and the "not of this class" greetings leave the pair out. Written to be applied
-- again: its own rows (and the undead paladins' alone of releases 1.0.335 to 1.0.337) are taken out first.

SET @COMMENT := 'mod-allied-races: new classes at their host class''s trainers';
SET @CLASS := 15, @RACE := 16;        -- condition types

DELETE FROM `conditions` WHERE `Comment` IN (@COMMENT, 'mod-allied-races: undead paladins at the priest trainers');

-- The pairs: race mask, class mask, the host class (and its mask), the ElseGroup of their way through.
DROP TEMPORARY TABLE IF EXISTS `app_pairs`;
CREATE TEMPORARY TABLE `app_pairs` (`Race` INT UNSIGNED, `Guest` INT UNSIGNED, `Host` INT UNSIGNED, `HostMask` INT UNSIGNED, `OrGroup` INT UNSIGNED);
INSERT INTO `app_pairs` VALUES
(16, 2, 5, 16, 7),          -- undead paladins: priest trainers
(1, 4, 1, 1, 8),            -- human hunters: warrior trainers
(4, 64, 5, 16, 9),          -- dwarf shamans: priest trainers
(64, 16, 8, 128, 10),       -- gnome priests: mage trainers
(2, 128, 9, 256, 11),       -- orc mages: warlock trainers
(128, 256, 8, 128, 12);     -- troll warlocks: mage trainers

-- The host classes' class trainers' gossip menus.
DROP TEMPORARY TABLE IF EXISTS `app_menus`;
CREATE TEMPORARY TABLE `app_menus`
SELECT DISTINCT ct.`gossip_menu_id` AS `MenuID`, t.`Requirement` AS `Host`
FROM `creature_template` ct
JOIN `creature_default_trainer` cdt ON cdt.`CreatureId` = ct.`entry`
JOIN `trainer` t ON t.`Id` = cdt.`TrainerId`
WHERE t.`Type` = 0 AND t.`Requirement` IN (1, 5, 8, 9) AND ct.`gossip_menu_id` <> 0;

-- Their greetings (14) and options (15) that need the host class, or any class but it (the pair's among
-- them, or "not the host class": a negative condition, as the portal trainers' greetings have), with that
-- class mask, for each pair at that host.
DROP TEMPORARY TABLE IF EXISTS `app_sources`;
CREATE TEMPORARY TABLE `app_sources`
SELECT DISTINCT c.`SourceTypeOrReferenceId` AS `Type`, c.`SourceGroup` AS `Grp`, c.`SourceEntry` AS `Entry`, c.`SourceId` AS `Id`,
    c.`ConditionValue1` AS `Classes`, c.`NegativeCondition` = 0 AND (c.`ConditionValue1` & p.`HostMask`) <> 0 AS `ForHost`,
    c.`NegativeCondition` AS `Negative`,
    p.`Race`, p.`Guest`, p.`OrGroup`
FROM `conditions` c
JOIN `app_menus` m ON m.`MenuID` = c.`SourceGroup`
JOIN `app_pairs` p ON p.`Host` = m.`Host`
WHERE c.`SourceTypeOrReferenceId` IN (14, 15) AND c.`ElseGroup` = 0 AND c.`ConditionTypeOrReference` = @CLASS
    AND c.`ConditionTarget` = 0
    AND ((c.`NegativeCondition` = 0 AND ((c.`ConditionValue1` & p.`HostMask`) <> 0) <> ((c.`ConditionValue1` & p.`Guest`) <> 0))
        OR (c.`NegativeCondition` = 1 AND (c.`ConditionValue1` & p.`HostMask`) <> 0 AND (c.`ConditionValue1` & p.`Guest`) = 0));

-- The "not of this class" ones: no longer for the pair's race (its other classes come back through the
-- second way, below).
INSERT IGNORE INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`,
    `ConditionTypeOrReference`, `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`,
    `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`)
SELECT `Type`, `Grp`, `Entry`, `Id`, 0, @RACE, 0, `Race`, 0, 0, 1, 0, 0, '', @COMMENT
FROM `app_sources` WHERE NOT `ForHost`;

-- The second way: the first way's other conditions,
DROP TEMPORARY TABLE IF EXISTS `app_rest`;
CREATE TEMPORARY TABLE `app_rest`
SELECT c.`SourceTypeOrReferenceId`, c.`SourceGroup`, c.`SourceEntry`, c.`SourceId`, s.`OrGroup`, c.`ConditionTypeOrReference`,
    c.`ConditionTarget`, c.`ConditionValue1`, c.`ConditionValue2`, c.`ConditionValue3`, c.`NegativeCondition`, c.`ErrorType`,
    c.`ErrorTextId`, c.`ScriptName`
FROM `conditions` c
JOIN `app_sources` s ON s.`Type` = c.`SourceTypeOrReferenceId` AND s.`Grp` = c.`SourceGroup`
    AND s.`Entry` = c.`SourceEntry` AND s.`Id` = c.`SourceId`
WHERE c.`ElseGroup` = 0 AND c.`ConditionTypeOrReference` <> @CLASS AND c.`Comment` <> @COMMENT;

INSERT IGNORE INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`,
    `ConditionTypeOrReference`, `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`,
    `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`)
SELECT `SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `OrGroup`,
    `ConditionTypeOrReference`, `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`,
    `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, @COMMENT
FROM `app_rest`;

-- the pair's race,
INSERT IGNORE INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`,
    `ConditionTypeOrReference`, `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`,
    `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`)
SELECT `Type`, `Grp`, `Entry`, `Id`, `OrGroup`, @RACE, 0, `Race`, 0, 0, 0, 0, 0, '', @COMMENT
FROM `app_sources`;

-- and the pair's class (for the host's greetings and options), or any of the "not of this class" classes but
-- the pair's (none of the negative condition's classes, nor the pair's).
INSERT IGNORE INTO `conditions` (`SourceTypeOrReferenceId`, `SourceGroup`, `SourceEntry`, `SourceId`, `ElseGroup`,
    `ConditionTypeOrReference`, `ConditionTarget`, `ConditionValue1`, `ConditionValue2`, `ConditionValue3`,
    `NegativeCondition`, `ErrorType`, `ErrorTextId`, `ScriptName`, `Comment`)
SELECT `Type`, `Grp`, `Entry`, `Id`, `OrGroup`, @CLASS, 0, IF(`ForHost`, `Guest`, IF(`Negative`, `Classes` | `Guest`, `Classes` & ~`Guest`)),
    0, 0, `Negative`, 0, 0, '', @COMMENT
FROM `app_sources`;

DROP TEMPORARY TABLE IF EXISTS `app_pairs`;
DROP TEMPORARY TABLE IF EXISTS `app_menus`;
DROP TEMPORARY TABLE IF EXISTS `app_sources`;
DROP TEMPORARY TABLE IF EXISTS `app_rest`;
