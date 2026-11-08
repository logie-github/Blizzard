-- Wrath Remix: the module's own tables in the Remix world database (acore_world_remix only: the
-- app's ctl.sh lists this folder in that database's updates_include, never in the main realm's).
-- Data only, made again whenever this file changes.

-- Northrend's creatures and quests at the chapters' levels. A creature in the zone (map and zone,
-- or the whole map when zone is 0) whose level is within 5 of original_min or above is put at the
-- matching level of band_min to band_max (straight-line, at most 3 above band_max); quests whose
-- QuestSortID is quest_sort get their levels the same way (wrath_remix_world_0005_levels.sql).
DROP TABLE IF EXISTS `remix_level_band`;
CREATE TABLE `remix_level_band` (
  `map` SMALLINT UNSIGNED NOT NULL,
  `zone` INT UNSIGNED NOT NULL DEFAULT 0,
  `quest_sort` SMALLINT NOT NULL DEFAULT 0,
  `original_min` SMALLINT NOT NULL,
  `original_max` SMALLINT NOT NULL,
  `band_min` SMALLINT NOT NULL,
  `band_max` SMALLINT NOT NULL,
  `chapter` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `name` VARCHAR(64) NOT NULL DEFAULT '',
  PRIMARY KEY (`map`, `zone`),
  UNIQUE KEY `quest_sort` (`quest_sort`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Moratari's transitions: a new quest (`quest`) that takes the place of a block of the original
-- chain. Its own prerequisite is the original quest before the block (quest_template_addon); the
-- original quest after the block (`next_quest`) opens with either this or the block's own end
-- (conditions). Turning it in takes the Timerunner to (map, x, y, z, o) when map isn't 65535, and
-- moves their chapter on to `chapter`.
DROP TABLE IF EXISTS `remix_bridge`;
CREATE TABLE `remix_bridge` (
  `quest` INT UNSIGNED NOT NULL,
  `next_quest` INT UNSIGNED NOT NULL DEFAULT 0,
  `chapter` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `map` SMALLINT UNSIGNED NOT NULL DEFAULT 65535,
  `x` FLOAT NOT NULL DEFAULT 0,
  `y` FLOAT NOT NULL DEFAULT 0,
  `z` FLOAT NOT NULL DEFAULT 0,
  `o` FLOAT NOT NULL DEFAULT 0,
  `skipped` VARCHAR(255) NOT NULL DEFAULT '' COMMENT 'the original quests it stands for, for the log',
  PRIMARY KEY (`quest`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- The chapters: their levels, and where a Timerunner of each side starts them.
DROP TABLE IF EXISTS `remix_chapter`;
CREATE TABLE `remix_chapter` (
  `chapter` TINYINT UNSIGNED NOT NULL,
  `name` VARCHAR(64) NOT NULL,
  `level_min` TINYINT UNSIGNED NOT NULL,
  `level_max` TINYINT UNSIGNED NOT NULL,
  `alliance_map` SMALLINT UNSIGNED NOT NULL,
  `alliance_x` FLOAT NOT NULL,
  `alliance_y` FLOAT NOT NULL,
  `alliance_z` FLOAT NOT NULL,
  `horde_map` SMALLINT UNSIGNED NOT NULL,
  `horde_x` FLOAT NOT NULL,
  `horde_y` FLOAT NOT NULL,
  `horde_z` FLOAT NOT NULL,
  `summary` VARCHAR(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`chapter`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Zephyr's destinations. side: 0 both, 1 Alliance, 2 Horde. Shown from min_level on.
DROP TABLE IF EXISTS `remix_travel`;
CREATE TABLE `remix_travel` (
  `id` SMALLINT UNSIGNED NOT NULL,
  `name` VARCHAR(64) NOT NULL,
  `side` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `min_level` TINYINT UNSIGNED NOT NULL DEFAULT 1,
  `map` SMALLINT UNSIGNED NOT NULL,
  `x` FLOAT NOT NULL,
  `y` FLOAT NOT NULL,
  `z` FLOAT NOT NULL,
  `o` FLOAT NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Alurmi's wares for Bronze. side: 0 both, 1 Alliance, 2 Horde.
DROP TABLE IF EXISTS `remix_shop`;
CREATE TABLE `remix_shop` (
  `id` SMALLINT UNSIGNED NOT NULL,
  `category` TINYINT UNSIGNED NOT NULL,
  `item` INT UNSIGNED NOT NULL,
  `count` SMALLINT UNSIGNED NOT NULL DEFAULT 1,
  `price` INT UNSIGNED NOT NULL,
  `side` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Bronze for a quest, in place of the usual WrathRemix.Bronze.Quest (Remix's own quests).
DROP TABLE IF EXISTS `remix_quest_reward`;
CREATE TABLE `remix_quest_reward` (
  `quest` INT UNSIGNED NOT NULL,
  `bronze` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`quest`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
