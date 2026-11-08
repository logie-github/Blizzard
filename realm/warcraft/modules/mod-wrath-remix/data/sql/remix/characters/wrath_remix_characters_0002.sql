-- Build 56: the starter kit, and Remix's quests renumbered.

-- Whether a Timerunner has had the starter kit (wrath_remix_world_0008_starter.sql): its version.
ALTER TABLE `remix_character` ADD COLUMN IF NOT EXISTS `kit` TINYINT UNSIGNED NOT NULL DEFAULT 0 AFTER `chapter`;

-- Remix's quests were 7701nnn; they're 77nnn now (77000 + the guide's WRM number). Timerunners keep
-- what they've done and what they're on.
UPDATE IGNORE `character_queststatus` SET `quest` = `quest` - 7624000 WHERE `quest` BETWEEN 7701000 AND 7701999;
UPDATE IGNORE `character_queststatus_rewarded` SET `quest` = `quest` - 7624000 WHERE `quest` BETWEEN 7701000 AND 7701999;
DELETE FROM `character_queststatus` WHERE `quest` BETWEEN 7701000 AND 7701999;
DELETE FROM `character_queststatus_rewarded` WHERE `quest` BETWEEN 7701000 AND 7701999;
UPDATE `remix_log` SET `entry` = `entry` - 7624000 WHERE `what` = 'bridge' AND `entry` BETWEEN 7701000 AND 7701999;
