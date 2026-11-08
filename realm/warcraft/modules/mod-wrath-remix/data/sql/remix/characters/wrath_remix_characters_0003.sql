-- Build 65: the journal behind Report Time Anomaly (src/RemixReport.cpp). remix_log keeps each
-- Timerunner's way through the story (quests taken, finished, turned in and dropped, who they spoke
-- to, the zones they entered, levels and deaths) beside the purchases and transitions it kept
-- already, each with the area it happened in.
ALTER TABLE `remix_log` ADD COLUMN IF NOT EXISTS `area` SMALLINT UNSIGNED NOT NULL DEFAULT 0 AFTER `amount`;
