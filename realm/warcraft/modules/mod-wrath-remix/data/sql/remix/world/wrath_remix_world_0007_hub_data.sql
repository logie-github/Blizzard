-- The Bazaar's records: the seven chapters and Zephyr's roads.

DELETE FROM `remix_chapter`;
INSERT INTO `remix_chapter` (`chapter`, `name`, `level_min`, `level_max`, `alliance_map`, `alliance_x`, `alliance_y`, `alliance_z`,
  `horde_map`, `horde_x`, `horde_y`, `horde_z`, `summary`) VALUES
(1, 'The Northrend Invasion', 10, 20, 571, 2269.5, 5173.7, 11.1, 571, 2759.3, 6094.6, 77.9,
 'The fleets land on two shores: Borean Tundra and Howling Fjord.'),
(2, 'The Wrathgate', 20, 32, 571, 3712.4, -694.9, 215.6, 571, 3865.9, 1525.6, 90.0,
 'The Dragonblight, Wyrmrest, and the gate of Icecrown.'),
(3, 'The Curse of Grizzly Hills', 32, 42, 571, 3446.4, -2754.1, 199.4, 571, 3258.9, -2263.1, 114.4,
 'Worgen, the bear god Ursoc, and a troll named Drakuru.'),
(4, 'The Fallen Empire', 42, 52, 571, 5521.6, -2672.3, 304.0, 571, 5521.6, -2672.3, 304.0,
 'Zul''Drak: the Drakkari empire devours its own gods.'),
(5, 'The Lifewarden''s Warning', 52, 60, 571, 5596.1, 5824.4, -67.7, 571, 5596.1, 5824.4, -67.7,
 'Sholazar Basin, Freya''s garden, and the titans'' waygate.'),
(6, 'The Secrets of Ulduar', 60, 70, 571, 6186.8, -1052.9, 410.2, 571, 6186.8, -1052.9, 410.2,
 'The Storm Peaks: Thorim, Loken, and the halls beneath the mountain.'),
(7, 'Icecrown: The Last Necessary Battle', 70, 80, 571, 6164.5, -61.3, 388.2, 571, 6164.5, -61.3, 388.2,
 'The Argent Crusade, the Ebon Blade, the Frozen Halls and the Lich King.');

DELETE FROM `remix_travel`;
INSERT INTO `remix_travel` (`id`, `name`, `side`, `min_level`, `map`, `x`, `y`, `z`, `o`) VALUES
(1, 'The Infinite Bazaar', 0, 1, 571, 6394.0, 1861.0, 508.7, 1.57),
(2, 'Dalaran', 0, 1, 571, 5813.9, 449.1, 658.8, 1.6),
(10, 'Valiance Keep, Borean Tundra', 1, 10, 571, 2269.5, 5173.7, 11.1, 0.5),
(11, 'Warsong Hold, Borean Tundra', 2, 10, 571, 2759.3, 6094.6, 77.9, 3.5),
(12, 'Valgarde, Howling Fjord', 1, 10, 571, 567.4, -5011.0, 11.5, 4.5),
(13, 'Vengeance Landing, Howling Fjord', 2, 10, 571, 1918.6, -6175.9, 24.4, 2.9),
(20, 'Wintergarde Keep, Dragonblight', 1, 18, 571, 3712.4, -694.9, 215.6, 3.1),
(21, 'Agmar''s Hammer, Dragonblight', 2, 18, 571, 3865.9, 1525.6, 90.0, 3.1),
(22, 'Wyrmrest Temple, Dragonblight', 0, 18, 571, 3653.2, 247.6, 52.3, 1.6),
(30, 'Amberpine Lodge, Grizzly Hills', 1, 30, 571, 3446.4, -2754.1, 199.4, 1.6),
(31, 'Conquest Hold, Grizzly Hills', 2, 30, 571, 3258.9, -2263.1, 114.4, 1.6),
(40, 'The Argent Stand, Zul''Drak', 0, 40, 571, 5521.6, -2672.3, 304.0, 1.6),
(50, 'Nesingwary Base Camp, Sholazar Basin', 0, 50, 571, 5596.1, 5824.4, -67.7, 1.6),
(60, 'K3, The Storm Peaks', 0, 58, 571, 6186.8, -1052.9, 410.2, 1.6),
(70, 'The Argent Vanguard, Icecrown', 0, 68, 571, 6164.5, -61.3, 388.2, 1.6);

-- Alurmi's wares were a gossip shop here; they're vendor lists priced in Bronze now, with the other
-- Bronze vendors' (wrath_remix_world_0010_vendors.sql).
DELETE FROM `remix_shop`;
