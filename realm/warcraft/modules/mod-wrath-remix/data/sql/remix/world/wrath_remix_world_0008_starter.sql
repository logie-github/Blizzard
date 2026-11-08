-- What a Timerunner starts with, since they start at 10 without having lived levels 1 to 9: gear
-- for their class, and the abilities their class quests would have taught them. Death knights
-- have their own (Acherus gives both). The module hands out the kit once, at a Timerunner's first
-- login (or next login, for one made before it existed): each piece is put on in place of the
-- starting clothes, or goes in the bags when something better is on. Every rank a class trainer
-- teaches up to their level comes with it, free, at every level (WrathRemix.AutoLearn).

-- The kit: heirlooms (they grow with the Timerunner to 80: shoulders, chest, weapons, a trinket
-- and a ring) and the best fixed greens for levels 1 to 10 for the slots heirlooms don't have.
DROP TABLE IF EXISTS `remix_starter_kit`;
CREATE TABLE `remix_starter_kit` (
  `class` TINYINT UNSIGNED NOT NULL,
  `item` INT UNSIGNED NOT NULL,
  `count` TINYINT UNSIGNED NOT NULL DEFAULT 1,
  `comment` VARCHAR(64) NOT NULL DEFAULT '',
  PRIMARY KEY (`class`, `item`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Abilities the game teaches through class quests rather than trainers, from the level the
-- quest is done at.
DROP TABLE IF EXISTS `remix_class_spell`;
CREATE TABLE `remix_class_spell` (
  `class` TINYINT UNSIGNED NOT NULL,
  `spell` INT UNSIGNED NOT NULL,
  `level` TINYINT UNSIGNED NOT NULL,
  `comment` VARCHAR(64) NOT NULL DEFAULT '',
  PRIMARY KEY (`class`, `spell`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Classes: 1 warrior, 2 paladin, 3 hunter, 4 rogue, 5 priest, 7 shaman, 8 mage, 9 warlock, 11 druid.
INSERT INTO `remix_starter_kit` (`class`, `item`, `count`, `comment`) VALUES
-- Warrior and paladin: strength, mail below 40 (the heirloom plate is wearable before then).
(1, 42949, 1, 'Polished Spaulders of Valor'), (1, 48685, 1, 'Polished Breastplate of Valor'),
(1, 42943, 1, 'Bloodied Arcanite Reaper'), (1, 42991, 1, 'Swift Hand of Justice'),
(1, 50255, 1, 'Dread Pirate Ring'), (1, 8350, 1, 'The 1 Ring'),
(1, 2978, 1, 'Veteran Leggings'), (1, 2980, 1, 'Veteran Gloves'), (1, 3302, 1, 'Brackwater Boots'),
(1, 832, 1, 'Silver Defias Belt'), (1, 2284, 1, 'Rat Cloth Cloak'),
(2, 42949, 1, 'Polished Spaulders of Valor'), (2, 48685, 1, 'Polished Breastplate of Valor'),
(2, 42943, 1, 'Bloodied Arcanite Reaper'), (2, 42991, 1, 'Swift Hand of Justice'),
(2, 50255, 1, 'Dread Pirate Ring'), (2, 8350, 1, 'The 1 Ring'),
(2, 2978, 1, 'Veteran Leggings'), (2, 2980, 1, 'Veteran Gloves'), (2, 3302, 1, 'Brackwater Boots'),
(2, 832, 1, 'Silver Defias Belt'), (2, 2284, 1, 'Rat Cloth Cloak'),
-- Hunter: agility, a bow, leather below 40 (the heirloom mail is wearable before then).
(3, 42950, 1, 'Champion Herod''s Shoulder'), (3, 48677, 1, 'Champion''s Deathdealer Breastplate'),
(3, 42946, 1, 'Charmed Ancient Bone Bow'), (3, 42945, 1, 'Venerable Dal''Rend''s Sacred Charge'),
(3, 42991, 1, 'Swift Hand of Justice'), (3, 50255, 1, 'Dread Pirate Ring'), (3, 8350, 1, 'The 1 Ring'),
(3, 38513, 1, 'Boarhide Leggings'), (3, 2976, 1, 'Hunting Gloves'), (3, 2309, 1, 'Embossed Leather Boots'),
(3, 1355, 1, 'Buckskin Cape'),
-- Rogue: agility, two daggers.
(4, 42952, 1, 'Stained Shadowcraft Spaulders'), (4, 48689, 1, 'Stained Shadowcraft Tunic'),
(4, 42944, 2, 'Balanced Heartseeker'), (4, 42991, 1, 'Swift Hand of Justice'),
(4, 50255, 1, 'Dread Pirate Ring'), (4, 8350, 1, 'The 1 Ring'),
(4, 38513, 1, 'Boarhide Leggings'), (4, 2976, 1, 'Hunting Gloves'), (4, 2309, 1, 'Embossed Leather Boots'),
(4, 1355, 1, 'Buckskin Cape'),
-- Priest, mage, warlock: intellect, a staff.
(5, 42985, 1, 'Tattered Dreadmist Mantle'), (5, 48691, 1, 'Tattered Dreadmist Robe'),
(5, 42947, 1, 'Dignified Headmaster''s Charge'), (5, 42992, 1, 'Discerning Eye of the Beast'),
(5, 50255, 1, 'Dread Pirate Ring'), (5, 8350, 1, 'The 1 Ring'),
(5, 3291, 1, 'Ancestral Woollies'), (5, 4768, 1, 'Adept''s Gloves'), (5, 3307, 1, 'Barbaric Cloth Boots'),
(5, 2283, 1, 'Rat Cloth Belt'), (5, 4771, 1, 'Harvest Cloak'),
(8, 42985, 1, 'Tattered Dreadmist Mantle'), (8, 48691, 1, 'Tattered Dreadmist Robe'),
(8, 42947, 1, 'Dignified Headmaster''s Charge'), (8, 42992, 1, 'Discerning Eye of the Beast'),
(8, 50255, 1, 'Dread Pirate Ring'), (8, 8350, 1, 'The 1 Ring'),
(8, 3291, 1, 'Ancestral Woollies'), (8, 4768, 1, 'Adept''s Gloves'), (8, 3307, 1, 'Barbaric Cloth Boots'),
(8, 2283, 1, 'Rat Cloth Belt'), (8, 4771, 1, 'Harvest Cloak'),
(9, 42985, 1, 'Tattered Dreadmist Mantle'), (9, 48691, 1, 'Tattered Dreadmist Robe'),
(9, 42947, 1, 'Dignified Headmaster''s Charge'), (9, 42992, 1, 'Discerning Eye of the Beast'),
(9, 50255, 1, 'Dread Pirate Ring'), (9, 8350, 1, 'The 1 Ring'),
(9, 3291, 1, 'Ancestral Woollies'), (9, 4768, 1, 'Adept''s Gloves'), (9, 3307, 1, 'Barbaric Cloth Boots'),
(9, 2283, 1, 'Rat Cloth Belt'), (9, 4771, 1, 'Harvest Cloak'),
-- Shaman: intellect, a mace (the shield stays), and the four totems every totem spell needs.
(7, 42951, 1, 'Mystical Pauldrons of Elements'), (7, 48683, 1, 'Mystical Vest of Elements'),
(7, 42948, 1, 'Devout Aurastone Hammer'), (7, 42992, 1, 'Discerning Eye of the Beast'),
(7, 50255, 1, 'Dread Pirate Ring'), (7, 8350, 1, 'The 1 Ring'),
(7, 3291, 1, 'Ancestral Woollies'), (7, 4768, 1, 'Adept''s Gloves'), (7, 3307, 1, 'Barbaric Cloth Boots'),
(7, 2283, 1, 'Rat Cloth Belt'), (7, 4771, 1, 'Harvest Cloak'),
(7, 5175, 1, 'Earth Totem'), (7, 5176, 1, 'Fire Totem'), (7, 5177, 1, 'Water Totem'), (7, 5178, 1, 'Air Totem'),
-- Druid: intellect, a staff.
(11, 42984, 1, 'Preened Ironfeather Shoulders'), (11, 48687, 1, 'Preened Ironfeather Breastplate'),
(11, 42947, 1, 'Dignified Headmaster''s Charge'), (11, 42992, 1, 'Discerning Eye of the Beast'),
(11, 50255, 1, 'Dread Pirate Ring'), (11, 8350, 1, 'The 1 Ring'),
(11, 3291, 1, 'Ancestral Woollies'), (11, 4768, 1, 'Adept''s Gloves'), (11, 3307, 1, 'Barbaric Cloth Boots'),
(11, 2283, 1, 'Rat Cloth Belt'), (11, 4771, 1, 'Harvest Cloak');

INSERT INTO `remix_class_spell` (`class`, `spell`, `level`, `comment`) VALUES
(1, 71, 10, 'Defensive Stance'), (1, 355, 10, 'Taunt'), (1, 7386, 10, 'Sunder Armor'),
(1, 2458, 30, 'Berserker Stance'),
(2, 7328, 12, 'Redemption'),
(3, 1515, 10, 'Tame Beast'), (3, 883, 10, 'Call Pet'), (3, 2641, 10, 'Dismiss Pet'),
(3, 6991, 10, 'Feed Pet'), (3, 982, 10, 'Revive Pet'),
(4, 2842, 20, 'Poisons'),
(9, 697, 10, 'Summon Voidwalker'), (9, 712, 20, 'Summon Succubus'), (9, 691, 30, 'Summon Felhunter'),
(9, 1122, 50, 'Inferno'), (9, 18540, 60, 'Ritual of Doom'),
(11, 5487, 10, 'Bear Form'), (11, 6795, 10, 'Growl'), (11, 6807, 10, 'Maul'),
(11, 18960, 10, 'Teleport: Moonglade');
