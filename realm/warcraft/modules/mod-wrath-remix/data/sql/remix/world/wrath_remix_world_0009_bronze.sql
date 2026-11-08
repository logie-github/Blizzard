-- Bronze as a currency, and the Infinite Bazaar's people after Legion Remix's: its Bronze vendors
-- (Horos's toys and curiosities, Domelius's companions, Arturos's dungeons, Aeonicus's and Durus's
-- raids, Sacerdormu's and Pythagorus's heroic raids, Agos's arena wares, Larah's faction wares, Freddie's
-- cloaks, Grandmaster Jakkus's glyphs, relics and class mounts, Hemet Nesingwary's mounts, Nostwin's
-- snacks and stuff, Unicus's ensembles, Lidamorrutu's gems, Lindormi's emblems, Erus's materials;
-- Alurmi keeps the heirlooms), Pageturner Metros who knows where they all are, and Nedward by his
-- barber's chair. The wares are lists of their own, priced in Bronze
-- (wrath_remix_world_0010_vendors.sql, made by tools/vendor_catalog.py).
--
-- Bronze is an item, 77001, in the currency tab like the emblems (a currency token: CurrencyTypes
-- row 342, under Wrath of the Lich King), and every price is an ItemExtendedCost of n Bronze. The
-- client has to know those rows to show them: the module writes them into a patch for the game
-- (Data/patch-Y.MPQ) as the realm starts. The server's side of them is here, in the *_dbc tables
-- the core reads over its DBC files (the Remix world database only).

SET @BRONZE := 77001;

-- The item: Emblem of Frost's, renamed, with the bronze dragonflight's head for an icon.
DELETE FROM `item_template` WHERE `entry` = @BRONZE;
DROP TEMPORARY TABLE IF EXISTS `remix_bronze_item`;
CREATE TEMPORARY TABLE `remix_bronze_item` SELECT * FROM `item_template` WHERE `entry` = 49426;
UPDATE `remix_bronze_item` SET `entry` = @BRONZE, `name` = 'Bronze', `displayid` = 43636, `Quality` = 6, `ItemLevel` = 1,
  `description` = 'Time, minted. Earned for every quest and foe in Wrath Remix, spent at the Infinite Bazaar.';
INSERT INTO `item_template` SELECT * FROM `remix_bronze_item`;
DROP TEMPORARY TABLE `remix_bronze_item`;

DELETE FROM `item_dbc` WHERE `ID` = @BRONZE;
INSERT INTO `item_dbc` (`ID`, `ClassID`, `SubclassID`, `Sound_Override_Subclassid`, `Material`, `DisplayInfoID`, `InventoryType`, `SheatheType`) VALUES
(@BRONZE, 10, 0, -1, -1, 43636, 0, 0);

DELETE FROM `currencytypes_dbc` WHERE `ID` = 342 OR `ItemID` = @BRONZE;
INSERT INTO `currencytypes_dbc` (`ID`, `ItemID`, `CategoryID`, `BitIndex`) VALUES
(342, @BRONZE, 21, 30);

-- Which vendor offers which list (wrath_remix_world_0010_vendors.sql fills it). side: 0 both,
-- 1 Alliance, 2 Horde.
CREATE TABLE IF NOT EXISTS `remix_vendor_list` (
  `list` INT UNSIGNED NOT NULL,
  `vendor` INT UNSIGNED NOT NULL,
  `sort` SMALLINT UNSIGNED NOT NULL DEFAULT 0,
  `side` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `label` VARCHAR(128) NOT NULL,
  PRIMARY KEY (`list`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- The vendors and the rest of the cast, as Legion Remix has them: the infinite dragonflight, as
-- dragonspawn, drakonid and a whelp or in mortal guise (3.3.5 has the Black Morass's and Culling of
-- Stratholme's infinite), but for Nedward and Lindormi (bronze) and Freddie, Larah and Hemet
-- (mortals). Gossip texts 7702201 + n, as the module picks them (RemixNpcs.cpp, RemixCast.cpp).
-- (770201 and up: wrath_remix_world_0002_npcs.sql clears 770001 to 770199 when it runs again.)
SET @HOROS := 770201, @DOMELIUS := 770202, @ARTUROS := 770203, @AEONICUS := 770204, @DURUS := 770205,
    @PYTHAGORUS := 770206, @SACERDORMU := 770207, @AGOS := 770208, @LARAH := 770209, @FREDDIE := 770210,
    @JAKKUS := 770211, @HEMET := 770212, @NOSTWIN := 770213, @UNICUS := 770214, @LIDAMORRUTU := 770215,
    @LINDORMI := 770216, @ERUS := 770217, @METROS := 770218, @NEDWARD := 770219;
DELETE FROM `creature_template` WHERE `entry` BETWEEN 770201 AND 770299;
INSERT INTO `creature_template` (`entry`, `name`, `subname`, `minlevel`, `maxlevel`, `exp`, `faction`, `npcflag`,
  `speed_walk`, `speed_run`, `rank`, `unit_class`, `unit_flags`, `unit_flags2`, `type`, `flags_extra`,
  `HealthModifier`, `DamageModifier`, `BaseAttackTime`, `RegenHealth`, `ScriptName`) VALUES
(@HOROS,       'Horos',                 'Rare Collections',             80, 80, 2, 35, 129, 1, 1.14286, 0, 1, 0, 2048, 2, 2, 10, 1, 2000, 1, 'npc_remix_bronze_vendor'),
(@DOMELIUS,    'Domelius',              'Companions',                   80, 80, 2, 35, 129, 1, 1.14286, 0, 1, 0, 2048, 2, 2, 10, 1, 2000, 1, 'npc_remix_bronze_vendor'),
(@ARTUROS,     'Arturos',               'Dungeon Wares',                80, 80, 2, 35, 129, 1, 1.14286, 0, 1, 0, 2048, 2, 2, 10, 1, 2000, 1, 'npc_remix_bronze_vendor'),
(@AEONICUS,    'Aeonicus',              'Raid Wares (10 Player)',       80, 80, 2, 35, 129, 1, 1.14286, 0, 1, 0, 2048, 2, 2, 10, 1, 2000, 1, 'npc_remix_bronze_vendor'),
(@DURUS,       'Durus',                 'Raid Wares (25 Player)',       80, 80, 2, 35, 129, 1, 1.14286, 0, 1, 0, 2048, 2, 2, 10, 1, 2000, 1, 'npc_remix_bronze_vendor'),
(@PYTHAGORUS,  'Pythagorus',            'Heroic Raid Wares (25 Player)', 80, 80, 2, 35, 129, 1, 1.14286, 0, 1, 0, 2048, 2, 2, 10, 1, 2000, 1, 'npc_remix_bronze_vendor'),
(@SACERDORMU,  'Sacerdormu',            'Heroic Raid Wares (10 Player)', 80, 80, 2, 35, 129, 1, 1.14286, 0, 1, 0, 2048, 2, 2, 10, 1, 2000, 1, 'npc_remix_bronze_vendor'),
(@AGOS,        'Agos the Silent',       'Arena and Wintergrasp Wares',  80, 80, 2, 35, 129, 1, 1.14286, 0, 1, 0, 2048, 2, 2, 10, 1, 2000, 1, 'npc_remix_bronze_vendor'),
(@LARAH,       'Larah Treebender',      'Faction Wares',                80, 80, 2, 35, 129, 1, 1.14286, 0, 1, 0, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_bronze_vendor'),
(@FREDDIE,     'Freddie Threads',       'Discount Cloak Dealer',        80, 80, 2, 35, 129, 1, 1.14286, 0, 1, 0, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_bronze_vendor'),
(@JAKKUS,      'Grandmaster Jakkus',    'Class Mounts and Glyphs',      80, 80, 2, 35, 129, 1, 1.14286, 0, 1, 0, 2048, 2, 2, 10, 1, 2000, 1, 'npc_remix_bronze_vendor'),
(@HEMET,       'Hemet Nesingwary XVII', 'Beastmaster',                  80, 80, 2, 35, 129, 1, 1.14286, 0, 1, 0, 2048, 7, 2, 10, 1, 2000, 1, 'npc_remix_bronze_vendor'),
(@NOSTWIN,     'Nostwin',               'Snacks and Stuff',             80, 80, 2, 35, 129, 1, 1.14286, 0, 1, 0, 2048, 2, 2, 10, 1, 2000, 1, 'npc_remix_bronze_vendor'),
(@UNICUS,      'Unicus',                'Exclusive Ensembles',          80, 80, 2, 35, 129, 1, 1.14286, 0, 1, 0, 2048, 2, 2, 10, 1, 2000, 1, 'npc_remix_bronze_vendor'),
(@LIDAMORRUTU, 'Lidamorrutu',           'Limitless Lapidary',           80, 80, 2, 35, 129, 1, 1.14286, 0, 1, 0, 2048, 2, 2, 10, 1, 2000, 1, 'npc_remix_bronze_vendor'),
(@LINDORMI,    'Lindormi',              'Emblems',                      80, 80, 2, 35, 129, 1, 1.14286, 0, 1, 0, 2048, 2, 2, 10, 1, 2000, 1, 'npc_remix_bronze_vendor'),
(@ERUS,        'Erus',                  'Scrap Master',                 80, 80, 2, 35, 129, 1, 1.14286, 0, 1, 0, 2048, 2, 2, 10, 1, 2000, 1, 'npc_remix_bronze_vendor'),
(@METROS,      'Pageturner Metros',     'Administrative Assistant',     80, 80, 2, 35, 1,   1, 1.14286, 0, 1, 0, 2048, 2, 2, 10, 1, 2000, 1, 'npc_remix_metros'),
(@NEDWARD,     'Nedward',               'Barber',                       80, 80, 2, 35, 1,   1, 1.14286, 0, 1, 0, 2048, 2, 2, 10, 1, 2000, 1, 'npc_remix_nedward');

DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN 770201 AND 770299;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) VALUES
-- (the looks 3.3.5 has nearest Legion Remix's; where the game's own model is small or large, scaled)
(@HOROS, 0, 24911, 1, 1, 0),        -- an infinite drakonid, horned (an Infinite Destroyer's)
(@DOMELIUS, 0, 11801, 1, 1, 0),     -- an infinite dragon as a grey old orc in black and teal (Sayoc's)
(@ARTUROS, 0, 20512, 1, 1, 0),      -- an infinite drakonid (an Infinite Destroyer's)
(@AEONICUS, 0, 19061, 1, 1, 0),     -- an infinite dragonspawn, robed (an Infinite Chronomancer's)
(@DURUS, 0, 19059, 1, 1, 0),        -- an infinite dragonspawn, armoured (an Infinite Saboteur's)
(@PYTHAGORUS, 0, 20513, 0.7, 1, 0), -- a large infinite drakonid (Chrono Lord Deja's)
(@SACERDORMU, 0, 27647, 1, 1, 0),   -- an infinite dragonspawn caster (an Infinite Agent's)
(@AGOS, 0, 19058, 1, 1, 0),         -- a lean infinite dragonspawn (an Infinite Assassin's)
(@LARAH, 0, 15472, 1, 1, 0),        -- a tauren woman in green (Herbalist Proudfeather's)
(@FREDDIE, 0, 26075, 1, 1, 0),      -- a man in a purple suit and wide hat (Timothy Jones's)
(@JAKKUS, 0, 30414, 2.5, 1, 0),     -- an infinite dragon as a pandaren (the Pandaren Monk's, man-sized)
(@HEMET, 0, 27303, 1, 1, 0),        -- a dwarf hunter (a Nesingwary Game Warden's)
(@NOSTWIN, 0, 10095, 1, 1, 0),      -- a purple whelp (a Chromatic Whelp's)
(@UNICUS, 0, 19063, 1, 1, 0),       -- an infinite dragonspawn caster (an Infinite Vanquisher's)
(@LIDAMORRUTU, 0, 4487, 1, 1, 0),   -- an infinite dragon as a night elf in black leather (Alanndarian Nightsong's)
(@LINDORMI, 0, 20222, 1, 1, 0),     -- a bronze dragon as an elf in gold (Soridormi's)
(@ERUS, 0, 20512, 0.8, 1, 0),       -- a small infinite drakonid (an Infinite Destroyer's)
(@METROS, 0, 23204, 1, 1, 0),       -- an infinite dragon as a gnome in black and blue leather (Beryl Reclaimer's)
(@NEDWARD, 0, 26766, 1, 1, 0);      -- a bronze dragon as a man in an open gold vest (Adamman the Trader's)

-- What they hold (their spawns' equipment 1).
DELETE FROM `creature_equip_template` WHERE `CreatureID` BETWEEN 770201 AND 770299;
INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`) VALUES
(@ARTUROS, 1, 0, 0, 5258, 0),          -- a bow
(@AEONICUS, 1, 14837, 0, 0, 0),        -- a staff
(@DURUS, 1, 39287, 39288, 0, 0),       -- a sword and his shield
(@PYTHAGORUS, 1, 11321, 0, 0, 0),      -- a sword. Of course he can lift it.
(@SACERDORMU, 1, 39289, 0, 0, 0),      -- a staff
(@AGOS, 1, 19924, 0, 0, 0),            -- a dagger
(@LARAH, 1, 21123, 0, 0, 0),           -- a white flower
(@HEMET, 1, 19015, 0, 25280, 0),       -- an axe and a game hunter's musket
(@UNICUS, 1, 28739, 0, 0, 0),          -- a staff
(@LINDORMI, 1, 30441, 0, 0, 0),        -- a staff
(@ERUS, 1, 31824, 0, 0, 0),            -- a work wrench
(@METROS, 1, 12742, 0, 0, 0);          -- a book

-- What each says (the module picks it; 7702201 and up, outside 0002's texts).
DELETE FROM `npc_text` WHERE `ID` BETWEEN 7702201 AND 7702299;
INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES
(7702201, 'We will have everything in time, Timerunner.$B$BToys, trinkets, a music box that plays a song nobody has written yet: every curiosity Northrend ever lost, and I found. Bronze, please. Time is not free, but it is negotiable.',
          'We will have everything in time, Timerunner.$B$BToys, trinkets, a music box that plays a song nobody has written yet: every curiosity Northrend ever lost, and I found. Bronze, please. Time is not free, but it is negotiable.', 1),
(7702202, 'I am late. So very, very late. Perhaps I should get a clock.$B$BCompanions, then. History remembers the battles; I remember the little things people carried into them.',
          'I am late. So very, very late. Perhaps I should get a clock.$B$BCompanions, then. History remembers the battles; I remember the little things people carried into them.', 1),
(7702203, 'Good to see you, champion! How fare your hunts?$B$BWhat the heroes of Northrend took from its dungeons, without the dungeons. Choose a hall, and I will show you what it gave.',
          'Good to see you, champion! How fare your hunts?$B$BWhat the heroes of Northrend took from its dungeons, without the dungeons. Choose a hall, and I will show you what it gave.', 1),
(7702204, 'Oh, a Timerunner! I bet you''ve got stories to tell.$B$BTen champions against the Scourge, again and again. Their spoils are here: the sets the record remembers, and every blade and bauble.',
          'Oh, a Timerunner! I bet you''ve got stories to tell.$B$BTen champions against the Scourge, again and again. Their spoils are here: the sets the record remembers, and every blade and bauble.', 1),
(7702205, 'Keep your shield up, and patience will see you through any battle.$B$BTwenty-five champions against the Scourge, and what they carried home: the sets, the blades, and two weapons the war handed out only once.',
          'Keep your shield up, and patience will see you through any battle.$B$BTwenty-five champions against the Scourge, and what they carried home: the sets, the blades, and two weapons the war handed out only once.', 1),
(7702206, 'What do you need, puny $r?$B$BThe heroic hours, twenty-five strong: what the Crusaders'' Coliseum, Icecrown Citadel and the Ruby Sanctum gave the few who lived through them. Offers? My wares are full price!',
          'What do you need, puny $r?$B$BThe heroic hours, twenty-five strong: what the Crusaders'' Coliseum, Icecrown Citadel and the Ruby Sanctum gave the few who lived through them. Offers? My wares are full price!', 1),
(7702207, 'Why choose between substance and style when you can have both?$B$BThe heroic hours for ten, and the Lich King''s own regalia besides. Pythagorus sells the same for twenty-five. Louder.',
          'Why choose between substance and style when you can have both?$B$BThe heroic hours for ten, and the Lich King''s own regalia besides. Pythagorus sells the same for twenty-five. Louder.', 1),
(7702208, '<Agos gives you a knowing nod, and gestures at the gladiators'' armor behind him, and at the Titan-forged pieces Wintergrasp''s keepers hand out.>',
          '<Agos gives you a knowing nod, and gestures at the gladiators'' armor behind him, and at the Titan-forged pieces Wintergrasp''s keepers hand out.>', 1),
(7702209, 'Oh honey, you need a new look.$B$BEvery faction in Northrend has something it gives its friends: the Argent Crusade, the Kirin Tor, the Ashen Verdict, the Kalu''ak and the rest. You haven''t time to make that many friends. That''s what I''m for.',
          'Oh honey, you need a new look.$B$BEvery faction in Northrend has something it gives its friends: the Argent Crusade, the Kirin Tor, the Ashen Verdict, the Kalu''ak and the rest. You haven''t time to make that many friends. That''s what I''m for.', 1),
(7702210, 'Hey there, kitty-cat, you look like you could use some threads.$B$BCloaks. Every cloak this war ever handed out, at a price you''ll tell your friends about. Everybody who''s anybody knows somebody who knows Freddie Threads.',
          'Hey there, kitty-cat, you look like you could use some threads.$B$BCloaks. Every cloak this war ever handed out, at a price you''ll tell your friends about. Everybody who''s anybody knows somebody who knows Freddie Threads.', 1),
(7702211, 'Ah, welcome young $c! I remember my $c training like it was yesterday.$B$BGlyphs and relics for every calling. And for those whose order rides to war on a steed of its own, that steed.',
          'Ah, welcome young $c! I remember my $c training like it was yesterday.$B$BGlyphs and relics for every calling. And for those whose order rides to war on a steed of its own, that steed.', 1),
(7702212, 'The name''s Hemet Nesingwary, tha seventeenth. Surely you''ve ''eard of my esteemed and grand familial lineage.$B$BMounts, then: every beast that ever carried a hero across Northrend, and a few nobody''s caught yet. Me great-great-great-somethin''-grandpappy''s out in Sholazar this very year. Best not tell ''im I''m ''ere.',
          'The name''s Hemet Nesingwary, tha seventeenth. Surely you''ve ''eard of my esteemed and grand familial lineage.$B$BMounts, then: every beast that ever carried a hero across Northrend, and a few nobody''s caught yet. Me great-great-great-somethin''-grandpappy''s out in Sholazar this very year. Best not tell ''im I''m ''ere.', 1),
(7702213, '<Nostwin munches on something delicious.>$B$BHi! Can I interest you in a fancy paper or this jar of bees I found? No? Snacks, then. And potions. And scrolls. And stuff.',
          '<Nostwin munches on something delicious.>$B$BHi! Can I interest you in a fancy paper or this jar of bees I found? No? Snacks, then. And potions. And scrolls. And stuff.', 1),
(7702214, 'Styles change all the time, but nothing stays out of style forever.$B$BTabards, shirts, the costumes of a dozen festivals. Wear them to war. No one in this year knows what is in fashion yet.',
          'Styles change all the time, but nothing stays out of style forever.$B$BTabards, shirts, the costumes of a dozen festivals. Wear them to war. No one in this year knows what is in fashion yet.', 1),
(7702215, 'Hmph.$B$BIf you''re in a rush, I can pluck a gem you''ve yet to find from a different timeline. It just takes a little Bronze.',
          'Hmph.$B$BIf you''re in a rush, I can pluck a gem you''ve yet to find from a different timeline. It just takes a little Bronze.', 1),
(7702216, 'Tales of adventure are the best! Dark dungeons, terrifying monsters, shiny treasures... I want to hear all about them!$B$BEmblems, for every hero who earned them the long way and lost them somewhere in time. Bronze, please. And a story, if you have one.',
          'Tales of adventure are the best! Dark dungeons, terrifying monsters, shiny treasures... I want to hear all about them!$B$BEmblems, for every hero who earned them the long way and lost them somewhere in time. Bronze, please. And a story, if you have one.', 1),
(7702217, 'Erus scrap junk for you. Everything has its time; junk''s time is now.$B$BOre, cloth, leather, herbs, the dust of things unmade. All of Northrend, in pieces.',
          'Erus scrap junk for you. Everything has its time; junk''s time is now.$B$BOre, cloth, leather, herbs, the dust of things unmade. All of Northrend, in pieces.', 1),
(7702218, 'Need something? I''ve got theories to sort through.$B$BI know where everyone in this camp is, what they sell, and when they last took a break. Ask after anyone, $n, and I''ll put a flag on your map.',
          'Need something? I''ve got theories to sort through.$B$BI know where everyone in this camp is, what they sell, and when they last took a break. Ask after anyone, $n, and I''ll put a flag on your map.', 1),
(7702219, 'Sit, sit! A little off the top, a little out of the timeline.$B$BThe chair''s right there. Gold, mind, not Bronze: some things never change.',
          'Sit, sit! A little off the top, a little out of the timeline.$B$BThe chair''s right there. Gold, mind, not Bronze: some things never change.', 1);

-- Where they stand (tools/bazaar.py keeps these spots, gives each a stall or a prop of its own and
-- what they say, in wrath_remix_world_0023_bazaar.sql): the market lane along the Bazaar's west side
-- (Horos, Domelius, Arturos, Aeonicus, Durus after Alurmi), each behind the counter of a stall
-- facing the lane; the north row along its north edge, facing the heart (Pythagorus, Sacerdormu,
-- Agos, Unicus, Larah, Freddie, Nedward by his chair); Hemet by the waystation with his mounts;
-- Grandmaster Jakkus at the training yard's east edge, beside Momentus; Nostwin and Erus at the
-- campfire; Pageturner Metros at her desk by the heart; Lidamorrutu and Lindormi in the chronicle
-- corner. Spawns 7704201 + n, to 7704219 (only those: the chapters' files have the rest of 7704200
-- to 7704399): wrath_remix_world_0004_spawns.sql has 7704001 to 7704199. Heights are the floor's
-- (data/bazaar_ground.tsv, 508.6 throughout), and a tenth over it.
DELETE FROM `creature` WHERE `guid` BETWEEN 7704201 AND 7704219;
INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `equipment_id`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(7704201, @HOROS,       571, 1, 1, 0, 6371.0, 1900.5, 508.7, 4.71, 60, 0, 0, 'Wrath Remix: Horos, Bazaar'),
(7704202, @DOMELIUS,    571, 1, 1, 0, 6362.0, 1900.5, 508.7, 4.71, 60, 0, 0, 'Wrath Remix: Domelius, Bazaar'),
(7704203, @ARTUROS,     571, 1, 1, 1, 6353.0, 1900.0, 508.7, 4.71, 60, 0, 0, 'Wrath Remix: Arturos, Bazaar'),
(7704204, @AEONICUS,    571, 1, 1, 1, 6344.0, 1900.5, 508.7, 4.71, 60, 0, 0, 'Wrath Remix: Aeonicus, Bazaar'),
(7704205, @DURUS,       571, 1, 1, 1, 6335.5, 1900.5, 508.7, 4.71, 60, 0, 0, 'Wrath Remix: Durus, Bazaar'),
(7704206, @PYTHAGORUS,  571, 1, 1, 1, 6429.5, 1888.0, 508.7, 3.14, 60, 0, 0, 'Wrath Remix: Pythagorus, Bazaar'),
(7704207, @SACERDORMU,  571, 1, 1, 1, 6429.5, 1879.0, 508.7, 3.14, 60, 0, 0, 'Wrath Remix: Sacerdormu, Bazaar'),
(7704208, @AGOS,        571, 1, 1, 1, 6429.5, 1870.0, 508.7, 3.14, 60, 0, 0, 'Wrath Remix: Agos the Silent, Bazaar'),
(7704209, @LARAH,       571, 1, 1, 1, 6429.5, 1852.0, 508.7, 3.14, 60, 0, 0, 'Wrath Remix: Larah Treebender, Bazaar'),
(7704210, @FREDDIE,     571, 1, 1, 0, 6429.5, 1843.0, 508.7, 3.14, 60, 0, 0, 'Wrath Remix: Freddie Threads, Bazaar'),
(7704211, @JAKKUS,      571, 1, 1, 0, 6370.0, 1808.5, 508.7, 1.57, 60, 0, 0, 'Wrath Remix: Grandmaster Jakkus, Bazaar'),
(7704212, @HEMET,       571, 1, 1, 1, 6415.0, 1818.5, 508.7, 1.99, 60, 0, 0, 'Wrath Remix: Hemet Nesingwary XVII, Bazaar'),
(7704213, @NOSTWIN,     571, 1, 1, 0, 6350.0, 1879.5, 508.7, 4.64, 60, 0, 0, 'Wrath Remix: Nostwin, Bazaar'),
(7704214, @UNICUS,      571, 1, 1, 1, 6429.5, 1861.0, 508.7, 3.14, 60, 0, 0, 'Wrath Remix: Unicus, Bazaar'),
(7704215, @LIDAMORRUTU, 571, 1, 1, 0, 6422.0, 1903.0, 508.7, 4.07, 60, 0, 0, 'Wrath Remix: Lidamorrutu, Bazaar'),
(7704216, @LINDORMI,    571, 1, 1, 1, 6409.5, 1903.0, 508.7, 4.32, 60, 0, 0, 'Wrath Remix: Lindormi, Bazaar'),
(7704217, @ERUS,        571, 1, 1, 1, 6328.0, 1866.0, 508.7, 0.00, 60, 0, 0, 'Wrath Remix: Erus, Bazaar'),
(7704218, @METROS,      571, 1, 1, 1, 6405.0, 1866.0, 508.7, 3.14, 60, 0, 0, 'Wrath Remix: Pageturner Metros, Bazaar'),
(7704219, @NEDWARD,     571, 1, 1, 0, 6430.5, 1834.5, 508.7, 3.84, 60, 0, 0, 'Wrath Remix: Nedward, Bazaar');
