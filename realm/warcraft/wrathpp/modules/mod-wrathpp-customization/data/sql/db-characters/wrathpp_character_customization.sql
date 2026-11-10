-- Wrath++: each character's extended appearance, one row a category (docs/wrathpp/PROTOCOL.md).
-- Only in the Wrath++ characters database: this module is built into the Wrath++ server alone, and
-- refuses to run on a database whose name doesn't end in _wrathpp. The stock five fields
-- (skin, face, hair style, hair colour, facial hair) stay in `characters`, untouched.
CREATE TABLE IF NOT EXISTS `wrathpp_character_customization` (
  `guid` INT UNSIGNED NOT NULL COMMENT 'characters.guid',
  `category_id` SMALLINT UNSIGNED NOT NULL COMMENT 'registry category id (stable)',
  `option_id` SMALLINT UNSIGNED NOT NULL COMMENT 'registry option id (stable)',
  `registry_version` SMALLINT UNSIGNED NOT NULL COMMENT 'registry version the choice was validated against',
  `updated` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`guid`, `category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Wrath++ extended appearance';
