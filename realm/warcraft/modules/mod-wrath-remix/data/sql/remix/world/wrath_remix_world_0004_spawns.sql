-- Where Wrath Remix's people stand: the Infinite Bazaar in Malykriss: The Vile Hold, the Lich King's
-- unfinished necropolis in Icecrown (wrath_remix_world_0030_malykriss.sql), where every new
-- Timerunner wakes and the prologue is played, and Moratari at each landing and at each of her
-- transitions. Spawn guids in
-- Remix's range (7704000+). Moratari beside an original quest giver is placed from that NPC's own
-- spawn, a step to its side, so she stands where it stands. CI's server test checks the floor under
-- every one of them.

SET @MORATARI := 770001, @ETERNUS := 770002, @ANDORMU := 770003, @NOZARI := 770004,
    @ALURMI := 770005, @ZEPHYR := 770006, @SAAT := 770007, @CHRONOLOGIST := 770008,
    @MOMENTUS := 770009, @ECHO_FOOTMAN := 770021, @ECHO_SAURFANG := 770022, @ECHO_BOLVAR := 770023,
    @SYLVANAS := 770011, @ALLERIA := 770012, @INTERLOPER := 770041,
    @SYLVANAS_ABROAD := 770014, @ALLERIA_ABROAD := 770015;

DELETE FROM `creature` WHERE `guid` BETWEEN 7704001 AND 7704199;

-- The Infinite Bazaar, on Malykriss's level floor under the necropolis's ribs. A new Timerunner wakes in the
-- middle of it (playercreateinfo, wrath_remix_world_0003_prologue.sql), facing Eternus and
-- Moratari, with the echoes of the war's dead beyond them. The Keepers of Time come later, with
-- the bronze (Chapter II). The camp around them (its districts, props and people) is
-- wrath_remix_world_0023_bazaar.sql (tools/bazaar.py, which keeps these spots too): Alurmi at the
-- head of the market lane, Zephyr at the waystation's door, Sa'at at his map table, the
-- Chronologist in the chronicle corner, the instructors at work in the training yard and Momentus,
-- the weaponmaster, at its edge.
SET @HX := 6394, @HY := 1869, @HZ := 508.7;
INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `equipment_id`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(7704011, @ETERNUS,      571, 1, 1, 1, @HX,      @HY + 8,  @HZ, 4.71, 60, 0, 0, 'Wrath Remix: Eternus, Bazaar'),
(7704012, @MORATARI,     571, 1, 1, 1, @HX - 9,  @HY + 2,  @HZ, 5.78, 60, 0, 0, 'Wrath Remix: Moratari, Bazaar'),
(7704015, @ALURMI,       571, 1, 1, 0, 6380.0, 1900.5, 508.7, 4.71, 60, 0, 0, 'Wrath Remix: Alurmi, Bazaar'),
(7704016, @ZEPHYR,       571, 1, 1, 1, 6402.5, 1838.0, 508.7, 1.87, 60, 0, 0, 'Wrath Remix: Zephyr, Bazaar'),
(7704017, @SAAT,         571, 1, 1, 0, 6389.5, 1822.5, 508.7, 3.28, 60, 0, 0, 'Wrath Remix: Sa''at, Bazaar'),
(7704018, @CHRONOLOGIST, 571, 1, 1, 0, 6410.0, 1895.0, 508.7, 0.00, 60, 0, 0, 'Wrath Remix: Chronologist, Bazaar'),
(7704019, @MOMENTUS,     571, 1, 1, 1, 6383.0, 1808.5, 508.7, 1.57, 60, 0, 0, 'Wrath Remix: Momentus, Bazaar'),
-- After the turn (WRM-207), for those who saw it: where its scene leaves them (RemixNpcs.cpp).
(7704013, @SYLVANAS,     571, 1, 1, 0, @HX + 4,   @HY + 6,   @HZ, 3.60, 60, 0, 0, 'Wrath Remix: Sylvanas Windrunner, Bazaar'),
(7704014, @ALLERIA,      571, 1, 1, 0, @HX + 6.5, @HY + 3.5, @HZ, 3.40, 60, 0, 0, 'Wrath Remix: Alleria Windrunner, Bazaar');

-- Chapter II (wrath_remix_world_0011_chapter2.sql): Sylvanas and Alleria atop Wyrmrest Temple, on
-- either side of Chromie (WRM-204, WRM-205); Alleria on the cliffs above the Wrathgate, where the
-- Forsaken's catapults stand on the day, with Eternus's loyalists around her (WRM-208). Each is
-- seen only by those the story has there (the chapter's visibility conditions), and away from the
-- Bazaar both are in their disguises (two rangers, adventurers like any other).
INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `equipment_id`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`)
SELECT 7704033, @SYLVANAS_ABROAD, c.`map`, 1, 1, 0, c.`position_x` + 3.5 * COS(c.`orientation` + PI() / 2), c.`position_y` + 3.5 * SIN(c.`orientation` + PI() / 2),
  c.`position_z`, c.`orientation`, 60, 0, 0, 'Wrath Remix: Sylvanas Windrunner, Wyrmrest Temple (beside Chromie)'
FROM `creature` c WHERE c.`guid` = 131083
UNION ALL
SELECT 7704034, @ALLERIA_ABROAD, c.`map`, 1, 1, 0, c.`position_x` + 3.5 * COS(c.`orientation` - PI() / 2), c.`position_y` + 3.5 * SIN(c.`orientation` - PI() / 2),
  c.`position_z`, c.`orientation`, 60, 0, 0, 'Wrath Remix: Alleria Windrunner, Wyrmrest Temple (beside Chromie)'
FROM `creature` c WHERE c.`guid` = 131083;
INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `equipment_id`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(7704035, @ALLERIA_ABROAD, 571, 1, 1, 0, 4974.5, 1383.5, 283.2, 0.30, 60, 0, 0, 'Wrath Remix: Alleria Windrunner, the Wrathgate''s cliffs'),
(7704040, @INTERLOPER, 571, 1, 1, 0, 4984.9, 1394.4, 284.4, 3.60, 30, 0, 0, 'Wrath Remix: Infinite Interloper, the Wrathgate''s cliffs'),
(7704041, @INTERLOPER, 571, 1, 1, 0, 4991.0, 1400.3, 284.4, 3.80, 30, 0, 0, 'Wrath Remix: Infinite Interloper, the Wrathgate''s cliffs'),
(7704042, @INTERLOPER, 571, 1, 1, 0, 5000.5, 1401.6, 284.4, 3.90, 30, 0, 0, 'Wrath Remix: Infinite Interloper, the Wrathgate''s cliffs'),
(7704043, @INTERLOPER, 571, 1, 1, 0, 4990.0, 1388.0, 284.4, 3.40, 30, 0, 0, 'Wrath Remix: Infinite Interloper, the Wrathgate''s cliffs'),
(7704044, @INTERLOPER, 571, 1, 1, 0, 4998.0, 1391.0, 284.4, 3.50, 30, 0, 0, 'Wrath Remix: Infinite Interloper, the Wrathgate''s cliffs'),
(7704045, @INTERLOPER, 571, 1, 1, 0, 4978.7, 1391.8, 284.4, 3.70, 30, 0, 0, 'Wrath Remix: Infinite Interloper, the Wrathgate''s cliffs'),
(7704046, @INTERLOPER, 571, 1, 1, 0, 5006.0, 1396.0, 284.4, 3.60, 30, 0, 0, 'Wrath Remix: Infinite Interloper, the Wrathgate''s cliffs');

-- The instructors, at work in the Bazaar's training yard (tools/bazaar.py; what each is doing there,
-- sparring, kneeling, at the targets, is wrath_remix_world_0023_bazaar.sql's creature_addon).
INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `equipment_id`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`)
SELECT 7704020 + (t.`entry` - 770100), t.`entry`, 571, 1, 1, 0, p.x, p.y, p.z, p.o, 60, 0, 0,
  CONCAT('Wrath Remix: ', t.`subname`, ', Bazaar')
FROM `creature_template` t JOIN (
  SELECT 770101 AS entry, 6371.5 AS x, 1838.5 AS y, 508.7 AS z, 3.76 AS o UNION ALL
  SELECT 770102 AS entry, 6378.0 AS x, 1830.0 AS y, 508.7 AS z, 4.71 AS o UNION ALL
  SELECT 770103 AS entry, 6378.0 AS x, 1825.0 AS y, 508.7 AS z, 1.57 AS o UNION ALL
  SELECT 770104 AS entry, 6355.0 AS x, 1829.0 AS y, 508.7 AS z, 3.14 AS o UNION ALL
  SELECT 770105 AS entry, 6374.5 AS x, 1843.5 AS y, 508.7 AS z, 4.17 AS o UNION ALL
  SELECT 770106 AS entry, 6376.0 AS x, 1850.5 AS y, 508.7 AS z, 0.00 AS o UNION ALL
  SELECT 770107 AS entry, 6365.0 AS x, 1819.8 AS y, 508.7 AS z, 4.71 AS o UNION ALL
  SELECT 770108 AS entry, 6348.0 AS x, 1848.0 AS y, 508.7 AS z, 1.57 AS o UNION ALL
  SELECT 770109 AS entry, 6360.0 AS x, 1840.5 AS y, 508.7 AS z, 4.71 AS o UNION ALL
  SELECT 770110 AS entry, 6352.0 AS x, 1840.5 AS y, 508.7 AS z, 4.71 AS o UNION ALL
  SELECT 770111 AS entry, 6343.5 AS x, 1846.0 AS y, 508.7 AS z, 0.42 AS o
) p ON p.entry = t.`entry`;

-- Moratari beside original quest givers: at each landing (where WRM-005 ends), at her
-- transitions (wrath_remix_world_0006_bridges.sql, and the later chapters') and at each coast's
-- last quest (WRM-121). A step to the giver's left, facing the same way, in the giver's phases
-- (or those given: Thrall's after the Battle for the Undercity is in its phase, 64, and the
-- Timerunner is back in the world's, 1, once it's turned in).
INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `equipment_id`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`)
SELECT 7704050 + n, @MORATARI, c.`map`, 1, IF(b.phase, b.phase, c.`phaseMask`), 1,
  c.`position_x` + 2.5 * COS(c.`orientation` + PI() / 2), c.`position_y` + 2.5 * SIN(c.`orientation` + PI() / 2),
  c.`position_z`, c.`orientation`, 60, 0, 0, CONCAT('Wrath Remix: Moratari, ', what)
FROM `creature` c JOIN (
  SELECT 1 AS n, 116919 AS beside, 'Valiance Keep landing (Recruitment Officer Blythe)' AS what, 0 AS phase UNION ALL
  SELECT 2, 125539, 'Warsong Hold landing (Warsong Recruitment Officer)', 0 UNION ALL
  SELECT 3, 133903, 'Valgarde landing (Macalroy)', 0 UNION ALL
  SELECT 4, 101906, 'Vengeance Landing (Apothecary Lysander)', 0 UNION ALL
  SELECT 5, 99763,  'WRM-006, Alliance Borean Tundra (William Allerton)', 0 UNION ALL
  SELECT 6, 107800, 'WRM-016, Horde Borean Tundra (Mobu)', 0 UNION ALL
  SELECT 7, 203320, 'WRM-026 and WRM-121, Westguard Keep (Captain Adams)', 0 UNION ALL
  SELECT 8, 101136, 'WRM-121, Alliance Borean Tundra (Thassarian)', 0 UNION ALL
  SELECT 9, 125447, 'WRM-121, Horde Borean Tundra (Garrosh Hellscream)', 0 UNION ALL
  SELECT 10, 113677, 'WRM-121, Horde Howling Fjord ("Hacksaw" Jenny)', 0 UNION ALL
  -- Chapter II (wrath_remix_world_0011_chapter2.sql)
  SELECT 11, 133653, 'WRM-203 and WRM-201, Alliance Dragonblight (Cavalier Durkon)', 0 UNION ALL
  SELECT 12, 108123, 'WRM-213 and WRM-211, Horde Dragonblight (Doctor Sintar Malefious)', 0 UNION ALL
  SELECT 27, 133759, 'WRM-206, Fordragon Hold (Highlord Bolvar Fordragon)', 0 UNION ALL
  SELECT 28, 111852, 'WRM-216, the Kor''kron Vanguard (Saurfang the Younger)', 0 UNION ALL
  SELECT 13, 132193, 'WRM-202 and WRM-212, the Wrathgate (Alexstrasza)', 0 UNION ALL
  SELECT 14, 10495,  'WRM-221, Stormwind Keep (King Varian Wrynn)', 0 UNION ALL
  SELECT 15, 3109785, 'WRM-222, the throne room of Lordaeron (Thrall)', 65 UNION ALL
  -- Chapter III (wrath_remix_world_0012_chapter3.sql)
  SELECT 16, 110818, 'WRM-301, Amberpine Lodge (Hierophant Thayreen)', 0 UNION ALL
  SELECT 17, 107481, 'WRM-311, Conquest Hold (Windseer Grayhorn)', 0 UNION ALL
  -- Chapter IV (wrath_remix_world_0013_chapter4.sql)
  SELECT 19, 105125, 'WRM-401 and WRM-402, the Ebon Watch (Stefan Vadu)', 0 UNION ALL
  SELECT 20, 110645, 'WRM-403, Zul''Drak (Hexxer Ubungo)', 0 UNION ALL
  SELECT 21, 101938, 'WRM-404, Zim''Torga (Witch Doctor Khufu)', 0 UNION ALL
  SELECT 22, 115292, 'WRM-421, Gundrak (Tol''mar)', 0 UNION ALL
  -- Eternus's first kindness, in Chapter I (wrath_remix_world_0006_bridges.sql)
  SELECT 25, 116619, 'WRM-017, Valiance Keep (Sergeant Hammerhill)', 0 UNION ALL
  SELECT 26, 125571, 'WRM-018, Warsong Hold (Overlord Razgor)', 0
) b ON c.`guid` = b.beside;

-- WRM-302 and WRM-321 (wrath_remix_world_0012_chapter3.sql): at Drak'Tharon Keep's door in the
-- Grizzly Hills, where nobody of the game's stands to be beside. On the landing before it, a few
-- yards from where the keep puts those who leave it (4774.5, -2028.0, 229.4), facing the way up
-- from the road; its floor's height from the navigation mesh (230.1 there, the landing 229.4 to
-- 230.1).
INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `equipment_id`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES
(7704068, @MORATARI, 571, 1, 1, 1, 4778.0, -2034.0, 229.9, 4.00, 60, 0, 0, 'Wrath Remix: Moratari, WRM-302 and WRM-321, Drak''Tharon Keep''s door');

-- The Azure Dragonflight's raiders at the Violet Stand killed new Timerunners on arrival when the
-- Bazaar was below it (until build 117): not in Remix's world.
DELETE FROM `creature` WHERE `id` = 31402 AND `guid` IN (72221, 13424, 13423);
