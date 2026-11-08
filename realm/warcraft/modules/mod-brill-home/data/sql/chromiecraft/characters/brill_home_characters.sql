-- mod-brill-home (ChromieCraft's characters database alone: ctl.sh realm_sql): a character's house in
-- Brill, the furniture bought for it (its phase bits: src/BrillHome.cpp) and when its bed last gave
-- rested experience (Unix time), and its flags (1: slept in it; 2: the dog's quest done; 4: the
-- dog, Corn, is its pet).
CREATE TABLE IF NOT EXISTS `brill_home` (
    `guid` INT UNSIGNED NOT NULL,
    `upgrades` INT UNSIGNED NOT NULL DEFAULT 0,
    `last_rested` INT UNSIGNED NOT NULL DEFAULT 0,
    `flags` INT UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (`guid`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- An adopted dog keeps its saved looks in character_pet, even in the stable: the mastiff's and a display of
-- Corn's own (39700 to 39703) made the game's pug's (31174), which wears Corn's coat in the module's patch;
-- and his name where it kept the mastiff's. Applied again, it changes nothing.
UPDATE `character_pet` SET `modelid` = 31174 WHERE `entry` = 970115 AND `modelid` BETWEEN 39700 AND 39703;
UPDATE `character_pet` SET `name` = 'Corn' WHERE `entry` = 970115 AND `name` = 'Mastiff';
