-- Wrath Remix's records of its Timerunners, in the Remix characters database only.

-- A Timerunner: Bronze in hand and earned in all, and the chapter they've reached.
CREATE TABLE IF NOT EXISTS `remix_character` (
  `guid` INT UNSIGNED NOT NULL,
  `bronze` INT UNSIGNED NOT NULL DEFAULT 0,
  `bronze_earned` INT UNSIGNED NOT NULL DEFAULT 0,
  `chapter` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `created` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Every purchase from Alurmi, and every transition of Moratari's taken.
CREATE TABLE IF NOT EXISTS `remix_log` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `guid` INT UNSIGNED NOT NULL,
  `what` VARCHAR(16) NOT NULL,
  `entry` INT UNSIGNED NOT NULL DEFAULT 0,
  `amount` INT NOT NULL DEFAULT 0,
  `time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `guid` (`guid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
