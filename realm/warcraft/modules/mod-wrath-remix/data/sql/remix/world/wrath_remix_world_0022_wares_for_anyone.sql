-- Everything the Bronze vendors sell is for anyone, at any level: no level, no riding or other
-- skill, no spell, no honor or city rank, no reputation to buy it, wear it, ride it or use it. A
-- level 10 Timerunner can buy a raid's gear or a drake and use it at once (with every riding skill
-- taught from the first login: WrathRemix.FreeRiding). The wares are the Bronze vendors' lists
-- (npc_vendor 770301 to 770499, wrath_remix_world_0010_vendors.sql). What each had is kept in
-- remix_original_ware_requirement; this file comes after the level bands' (0005), which scale some
-- of the same items' levels first. The files are applied each on its own, as it changes (0005 or
-- 0010 again without this one would put requirements back), so the module also takes them off
-- the wares in memory as the realm starts (FreeWares, src/WrathRemix.cpp).

CREATE TABLE IF NOT EXISTS `remix_original_ware_requirement` (
  `entry` INT UNSIGNED NOT NULL,
  `RequiredLevel` SMALLINT NOT NULL,
  `RequiredSkill` SMALLINT NOT NULL,
  `RequiredSkillRank` SMALLINT NOT NULL,
  `requiredspell` INT NOT NULL,
  `requiredhonorrank` INT NOT NULL,
  `RequiredCityRank` INT NOT NULL,
  `RequiredReputationFaction` SMALLINT NOT NULL,
  `RequiredReputationRank` SMALLINT NOT NULL,
  PRIMARY KEY (`entry`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO `remix_original_ware_requirement` (`entry`, `RequiredLevel`, `RequiredSkill`, `RequiredSkillRank`,
  `requiredspell`, `requiredhonorrank`, `RequiredCityRank`, `RequiredReputationFaction`, `RequiredReputationRank`)
SELECT i.`entry`, i.`RequiredLevel`, i.`RequiredSkill`, i.`RequiredSkillRank`, i.`requiredspell`, i.`requiredhonorrank`,
  i.`RequiredCityRank`, i.`RequiredReputationFaction`, i.`RequiredReputationRank`
FROM `item_template` i WHERE i.`entry` IN (SELECT `item` FROM `npc_vendor` WHERE `entry` BETWEEN 770301 AND 770499);

UPDATE `item_template` SET `RequiredLevel` = 0, `RequiredSkill` = 0, `RequiredSkillRank` = 0, `requiredspell` = 0,
  `requiredhonorrank` = 0, `RequiredCityRank` = 0, `RequiredReputationFaction` = 0, `RequiredReputationRank` = 0
WHERE `entry` IN (SELECT `entry` FROM `remix_original_ware_requirement`);
