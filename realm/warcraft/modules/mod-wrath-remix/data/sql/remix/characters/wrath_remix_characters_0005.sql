-- The opening (src/RemixIntro.cpp): 1 once a Timerunner has been through it, so it plays once.
ALTER TABLE `remix_character` ADD COLUMN IF NOT EXISTS `intro` TINYINT UNSIGNED NOT NULL DEFAULT 0 AFTER `back_o`;
