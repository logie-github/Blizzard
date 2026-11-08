-- Northrend at Wrath Remix's chapter levels: Timerunners start at 10, so Borean Tundra and Howling
-- Fjord are 10 to 20, Dragonblight 20 to 32, and so on to Icecrown at 70 to 80, with the dungeons at
-- their chapter's levels (normal difficulty; heroic stays at 80). The module sets each creature's
-- level as it appears (and scales its spells to match): near a Timerunner, theirs, as Legion
-- Remix has it (WrathRemix.LevelBands.FollowPlayer), and otherwise from this table, which also
-- says where Remix's levels are at all. Here the quests get the chapters' levels, their rewards'
-- level and stats follow, and the dungeons open at the new levels.
--
-- Made again whenever this file changes: the original values are kept once, in remix_original_*,
-- and every change is worked out from them.

DELETE FROM `remix_level_band`;
INSERT INTO `remix_level_band` (`map`, `zone`, `quest_sort`, `original_min`, `original_max`, `band_min`, `band_max`, `chapter`, `name`) VALUES
-- The chapters' zones.
(571, 3537, 3537, 68, 72, 10, 20, 1, 'Borean Tundra'),
(571, 4024, 4024, 68, 72, 10, 20, 1, 'Coldarra (quests; its creatures are Borean Tundra''s)'),
(571, 495, 495, 68, 72, 10, 20, 1, 'Howling Fjord'),
(571, 65, 65, 71, 75, 20, 32, 2, 'Dragonblight'),
(571, 394, 394, 73, 75, 32, 42, 3, 'Grizzly Hills'),
(571, 66, 66, 74, 77, 42, 52, 4, 'Zul''Drak'),
(571, 3711, 3711, 76, 78, 52, 60, 5, 'Sholazar Basin'),
(571, 67, 67, 77, 80, 60, 70, 6, 'The Storm Peaks'),
(571, 210, 210, 77, 80, 70, 80, 7, 'Icecrown'),
(571, 2817, 2817, 74, 76, 60, 70, 0, 'Crystalsong Forest'),
-- The sea between them (the North Fleet off the Howling Fjord's coast, the Kvaldir; and where a
-- ship's crew is made before it's put aboard), Hrothgar's Landing, and Wintergrasp (outside its
-- battle: the module leaves it to the game while the battle is on). Their quests stay the game's
-- (a quest_sort no quest has: the zone's, negative).
(571, 3979, -3979, 68, 72, 10, 20, 1, 'The Frozen Sea'),
(571, 4742, -4742, 77, 80, 70, 80, 7, 'Hrothgar''s Landing'),
(571, 4197, -4197, 77, 80, 70, 80, 7, 'Wintergrasp (outside its battle)'),
-- The Battle for the Undercity (Chapter II's end).
(0, 1497, 1497, 70, 80, 28, 34, 2, 'Undercity'),
-- The dungeons, normal difficulty.
(574, 0, 206, 69, 72, 15, 20, 1, 'Utgarde Keep'),
(576, 0, 4265, 71, 73, 15, 20, 1, 'The Nexus'),
(601, 0, 4277, 72, 74, 24, 28, 2, 'Azjol-Nerub'),
(619, 0, 4494, 73, 75, 28, 32, 2, 'Ahn''kahet: The Old Kingdom'),
(600, 0, 4196, 74, 76, 36, 42, 3, 'Drak''Tharon Keep'),
(608, 0, 4415, 75, 77, 40, 46, 4, 'The Violet Hold'),
(604, 0, 4416, 76, 78, 48, 52, 4, 'Gundrak'),  -- its quests' sort: the instance's zone (4375 is the area outside)
(599, 0, 4264, 77, 79, 62, 66, 6, 'Halls of Stone'),
(602, 0, 4272, 79, 81, 66, 70, 6, 'Halls of Lightning'),
(578, 0, 4228, 79, 81, 74, 78, 7, 'The Oculus'),
(575, 0, 1196, 79, 81, 74, 78, 7, 'Utgarde Pinnacle'),
(595, 0, 4100, 79, 81, 74, 78, 7, 'The Culling of Stratholme'),
(650, 0, 4723, 80, 82, 76, 80, 7, 'Trial of the Champion'),
(632, 0, 4809, 80, 82, 76, 80, 7, 'The Forge of Souls'),
(658, 0, 4813, 80, 82, 76, 80, 7, 'Pit of Saron'),
(668, 0, 4820, 80, 82, 78, 80, 7, 'Halls of Reflection');

-- The quests: their original levels, once. Those of the Battle for the Undercity's chain, which
-- happen outside Northrend, count as Dragonblight's.
CREATE TABLE IF NOT EXISTS `remix_original_quest` (
  `ID` INT UNSIGNED NOT NULL,
  `QuestLevel` SMALLINT NOT NULL,
  `MinLevel` SMALLINT NOT NULL,
  `RewardMoney` INT NOT NULL,
  `quest_sort` SMALLINT NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT IGNORE INTO `remix_original_quest` (`ID`, `QuestLevel`, `MinLevel`, `RewardMoney`, `quest_sort`)
SELECT q.`ID`, q.`QuestLevel`, q.`MinLevel`, q.`RewardMoney`, q.`QuestSortID`
FROM `quest_template` q JOIN `remix_level_band` b ON b.`quest_sort` = q.`QuestSortID`
WHERE q.`ID` NOT BETWEEN 77000 AND 77999;
INSERT IGNORE INTO `remix_original_quest` (`ID`, `QuestLevel`, `MinLevel`, `RewardMoney`, `quest_sort`)
SELECT `ID`, `QuestLevel`, `MinLevel`, `RewardMoney`, 65 FROM `quest_template`
WHERE `ID` IN (13347, 13369, 13370, 13371, 13377, 13242, 13257, 13266, 13267);

-- A quest's level in a band: unchanged far below the zone's levels (a city's own quests: the
-- Undercity's), else on the straight line from the original range to the chapter's, at most 3
-- above the chapter's top. (A creature's, in the module, is unchanged only at or below the band.)
-- (Written out in each statement: MariaDB has no inline functions in plain SQL files.)
UPDATE `quest_template` q
JOIN `remix_original_quest` o ON o.`ID` = q.`ID`
JOIN `remix_level_band` b ON b.`quest_sort` = o.`quest_sort`
SET q.`QuestLevel` = IF(o.`QuestLevel` <= 0 OR o.`QuestLevel` < b.`original_min` - 5, o.`QuestLevel`,
      LEAST(b.`band_max` + 3, GREATEST(1, ROUND(b.`band_min` + (o.`QuestLevel` - b.`original_min`) * (b.`band_max` - b.`band_min`) / GREATEST(1, b.`original_max` - b.`original_min`))))),
    q.`MinLevel` = IF(o.`MinLevel` < b.`original_min` - 5, o.`MinLevel`,
      LEAST(b.`band_max`, GREATEST(1, ROUND(b.`band_min` + (o.`MinLevel` - b.`original_min`) * (b.`band_max` - b.`band_min`) / GREATEST(1, b.`original_max` - b.`original_min`))))),
    q.`RewardMoney` = IF(o.`RewardMoney` <= 0 OR o.`QuestLevel` <= 0 OR o.`QuestLevel` < b.`original_min` - 5, o.`RewardMoney`,
      ROUND(o.`RewardMoney` * POW(LEAST(1, LEAST(b.`band_max` + 3, GREATEST(1, ROUND(b.`band_min` + (o.`QuestLevel` - b.`original_min`) * (b.`band_max` - b.`band_min`) / GREATEST(1, b.`original_max` - b.`original_min`)))) / o.`QuestLevel`), 1.5)));

-- And as Legion Remix has them, the quests show the Timerunner's own level (as the game's holiday
-- quests do: -1), so their experience is a level's worth whenever they're done. Their chapter's
-- level is kept in remix_quest_level for the guide (src/RemixGuide.cpp), which leaves out the ones
-- a Timerunner has outgrown.
CREATE TABLE IF NOT EXISTS `remix_quest_level` (
  `ID` INT UNSIGNED NOT NULL,
  `QuestLevel` SMALLINT NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
DELETE FROM `remix_quest_level`;
INSERT IGNORE INTO `remix_quest_level` (`ID`, `QuestLevel`)
SELECT q.`ID`, q.`QuestLevel` FROM `quest_template` q
JOIN `remix_original_quest` o ON o.`ID` = q.`ID`
JOIN `remix_level_band` b ON b.`quest_sort` = o.`quest_sort`
WHERE o.`QuestLevel` > 0 AND o.`QuestLevel` >= b.`original_min` - 5 AND q.`QuestLevel` > 0;
UPDATE `quest_template` q JOIN `remix_quest_level` l ON l.`ID` = q.`ID` SET q.`QuestLevel` = -1;

-- The quests' armour and weapons: most of Northrend's ask for no level at all (the quests did),
-- so they would arrive at 15 as they are at 70. Their item level, stats, armour, damage and price
-- (and level, where they have one) shrink with the quest's level, by the same ratio: a reward of a
-- level 71 quest that is now level 18 keeps a quarter. The lowest ratio if several quests give it.
-- Consumables keep theirs.
CREATE TABLE IF NOT EXISTS `remix_original_item` (
  `entry` INT UNSIGNED NOT NULL,
  `RequiredLevel` SMALLINT NOT NULL,
  `ItemLevel` SMALLINT NOT NULL,
  `armor` INT NOT NULL,
  `block` INT NOT NULL,
  `dmg_min1` FLOAT NOT NULL, `dmg_max1` FLOAT NOT NULL, `dmg_min2` FLOAT NOT NULL, `dmg_max2` FLOAT NOT NULL,
  `stat_value1` INT NOT NULL, `stat_value2` INT NOT NULL, `stat_value3` INT NOT NULL, `stat_value4` INT NOT NULL,
  `stat_value5` INT NOT NULL, `stat_value6` INT NOT NULL, `stat_value7` INT NOT NULL, `stat_value8` INT NOT NULL,
  `stat_value9` INT NOT NULL, `stat_value10` INT NOT NULL,
  `BuyPrice` BIGINT NOT NULL, `SellPrice` BIGINT NOT NULL,
  `ratio` FLOAT NOT NULL DEFAULT 1,
  PRIMARY KEY (`entry`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `remix_reward_item`;
CREATE TABLE `remix_reward_item` (`item` INT UNSIGNED NOT NULL, `quest` INT UNSIGNED NOT NULL, KEY (`item`)) ENGINE=InnoDB;
INSERT INTO `remix_reward_item` (`item`, `quest`)
SELECT `RewardItem1`, `ID` FROM `quest_template` WHERE `RewardItem1` > 0 UNION ALL
SELECT `RewardItem2`, `ID` FROM `quest_template` WHERE `RewardItem2` > 0 UNION ALL
SELECT `RewardItem3`, `ID` FROM `quest_template` WHERE `RewardItem3` > 0 UNION ALL
SELECT `RewardItem4`, `ID` FROM `quest_template` WHERE `RewardItem4` > 0 UNION ALL
SELECT `RewardChoiceItemID1`, `ID` FROM `quest_template` WHERE `RewardChoiceItemID1` > 0 UNION ALL
SELECT `RewardChoiceItemID2`, `ID` FROM `quest_template` WHERE `RewardChoiceItemID2` > 0 UNION ALL
SELECT `RewardChoiceItemID3`, `ID` FROM `quest_template` WHERE `RewardChoiceItemID3` > 0 UNION ALL
SELECT `RewardChoiceItemID4`, `ID` FROM `quest_template` WHERE `RewardChoiceItemID4` > 0 UNION ALL
SELECT `RewardChoiceItemID5`, `ID` FROM `quest_template` WHERE `RewardChoiceItemID5` > 0 UNION ALL
SELECT `RewardChoiceItemID6`, `ID` FROM `quest_template` WHERE `RewardChoiceItemID6` > 0;
DELETE r FROM `remix_reward_item` r LEFT JOIN `remix_original_quest` o ON o.`ID` = r.`quest` WHERE o.`ID` IS NULL;

INSERT IGNORE INTO `remix_original_item` (`entry`, `RequiredLevel`, `ItemLevel`, `armor`, `block`,
  `dmg_min1`, `dmg_max1`, `dmg_min2`, `dmg_max2`, `stat_value1`, `stat_value2`, `stat_value3`, `stat_value4`,
  `stat_value5`, `stat_value6`, `stat_value7`, `stat_value8`, `stat_value9`, `stat_value10`, `BuyPrice`, `SellPrice`)
SELECT i.`entry`, i.`RequiredLevel`, i.`ItemLevel`, i.`armor`, i.`block`,
  i.`dmg_min1`, i.`dmg_max1`, i.`dmg_min2`, i.`dmg_max2`, i.`stat_value1`, i.`stat_value2`, i.`stat_value3`, i.`stat_value4`,
  i.`stat_value5`, i.`stat_value6`, i.`stat_value7`, i.`stat_value8`, i.`stat_value9`, i.`stat_value10`, i.`BuyPrice`, i.`SellPrice`
FROM `item_template` i WHERE i.`class` IN (2, 4) AND i.`ItemLevel` >= 100 AND i.`entry` IN (SELECT `item` FROM `remix_reward_item`);

-- Each quest's ratio: its level now over its level before.
UPDATE `remix_original_item` o SET o.`ratio` = COALESCE((
  SELECT MIN(LEAST(1, IF(q.`QuestLevel` <= 0, 1,
    LEAST(b.`band_max` + 3, GREATEST(1, ROUND(b.`band_min` + (q.`QuestLevel` - b.`original_min`) * (b.`band_max` - b.`band_min`) / GREATEST(1, b.`original_max` - b.`original_min`)))) / q.`QuestLevel`)))
  FROM `remix_reward_item` r
  JOIN `remix_original_quest` q ON q.`ID` = r.`quest`
  JOIN `remix_level_band` b ON b.`quest_sort` = q.`quest_sort`
  WHERE r.`item` = o.`entry` AND q.`QuestLevel` >= b.`original_min` - 5), 1);
DROP TABLE IF EXISTS `remix_reward_item`;

UPDATE `item_template` i JOIN `remix_original_item` o ON o.`entry` = i.`entry`
SET i.`RequiredLevel` = IF(o.`RequiredLevel` = 0, 0, GREATEST(1, ROUND(o.`RequiredLevel` * o.`ratio`))),
    i.`ItemLevel` = GREATEST(1, ROUND(o.`ItemLevel` * o.`ratio`)),
    i.`armor` = ROUND(o.`armor` * o.`ratio`),
    i.`block` = ROUND(o.`block` * o.`ratio`),
    i.`dmg_min1` = ROUND(o.`dmg_min1` * o.`ratio`, 1),
    i.`dmg_max1` = ROUND(o.`dmg_max1` * o.`ratio`, 1),
    i.`dmg_min2` = ROUND(o.`dmg_min2` * o.`ratio`, 1),
    i.`dmg_max2` = ROUND(o.`dmg_max2` * o.`ratio`, 1),
    i.`stat_value1` = IF(o.`stat_value1` > 0, GREATEST(1, ROUND(o.`stat_value1` * o.`ratio`)), ROUND(o.`stat_value1` * o.`ratio`)),
    i.`stat_value2` = IF(o.`stat_value2` > 0, GREATEST(1, ROUND(o.`stat_value2` * o.`ratio`)), ROUND(o.`stat_value2` * o.`ratio`)),
    i.`stat_value3` = IF(o.`stat_value3` > 0, GREATEST(1, ROUND(o.`stat_value3` * o.`ratio`)), ROUND(o.`stat_value3` * o.`ratio`)),
    i.`stat_value4` = IF(o.`stat_value4` > 0, GREATEST(1, ROUND(o.`stat_value4` * o.`ratio`)), ROUND(o.`stat_value4` * o.`ratio`)),
    i.`stat_value5` = IF(o.`stat_value5` > 0, GREATEST(1, ROUND(o.`stat_value5` * o.`ratio`)), ROUND(o.`stat_value5` * o.`ratio`)),
    i.`stat_value6` = IF(o.`stat_value6` > 0, GREATEST(1, ROUND(o.`stat_value6` * o.`ratio`)), ROUND(o.`stat_value6` * o.`ratio`)),
    i.`stat_value7` = IF(o.`stat_value7` > 0, GREATEST(1, ROUND(o.`stat_value7` * o.`ratio`)), ROUND(o.`stat_value7` * o.`ratio`)),
    i.`stat_value8` = IF(o.`stat_value8` > 0, GREATEST(1, ROUND(o.`stat_value8` * o.`ratio`)), ROUND(o.`stat_value8` * o.`ratio`)),
    i.`stat_value9` = IF(o.`stat_value9` > 0, GREATEST(1, ROUND(o.`stat_value9` * o.`ratio`)), ROUND(o.`stat_value9` * o.`ratio`)),
    i.`stat_value10` = IF(o.`stat_value10` > 0, GREATEST(1, ROUND(o.`stat_value10` * o.`ratio`)), ROUND(o.`stat_value10` * o.`ratio`)),
    i.`BuyPrice` = ROUND(o.`BuyPrice` * o.`ratio`),
    i.`SellPrice` = ROUND(o.`SellPrice` * o.`ratio`);

-- The dungeons open at their chapter's levels (normal difficulty).
UPDATE `dungeon_access_template` t JOIN `remix_level_band` b ON b.`map` = t.`map_id` AND b.`zone` = 0
SET t.`min_level` = GREATEST(1, b.`band_min` - 2)
WHERE t.`difficulty` = 0;
