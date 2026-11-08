-- Moratari's Hourglass (src/RemixHourglass.cpp): where each Timerunner last came to the Bazaar from,
-- for it to take them back to (back_map -1: nowhere yet).
ALTER TABLE `remix_character` ADD COLUMN IF NOT EXISTS `back_map` INT NOT NULL DEFAULT -1 AFTER `kit`;
ALTER TABLE `remix_character` ADD COLUMN IF NOT EXISTS `back_x` FLOAT NOT NULL DEFAULT 0 AFTER `back_map`;
ALTER TABLE `remix_character` ADD COLUMN IF NOT EXISTS `back_y` FLOAT NOT NULL DEFAULT 0 AFTER `back_x`;
ALTER TABLE `remix_character` ADD COLUMN IF NOT EXISTS `back_z` FLOAT NOT NULL DEFAULT 0 AFTER `back_y`;
ALTER TABLE `remix_character` ADD COLUMN IF NOT EXISTS `back_o` FLOAT NOT NULL DEFAULT 0 AFTER `back_z`;
