#!/usr/bin/env python3
"""Makes the Infinite Bazaar's Bronze vendors' lists from a world database.

Legion Remix's Bazaar sells, for Bronze, what its expansion was known for, each of its vendors
one trade: its raids' and dungeons' sets and gear by difficulty, its PvP and world apparel, its
mounts, companions and toys, its consumables, gems and materials. This does the same for Wrath of
the Lich King, each Legion Remix vendor selling the Wrath version of their wares. The world
database says what dropped where (instance_encounters and the bosses' loot, references followed,
and the chests the game puts its loot in) and who sells what (the PvP vendors, by what their
prices ask for; the Northrend factions' quartermasters); tier sets come from their item sets;
relics, glyphs and gems from item_template (those the game gives somehow: a vendor, loot, a
quest, or a spell that makes them); mounts, companions, toys, consumables, cosmetics, emblems
and materials from the lists below. It writes
data/sql/remix/world/wrath_remix_world_0010_vendors.sql (the price ladder as ItemExtendedCost
rows, the lists as hidden vendor templates and npc_vendor rows, and remix_vendor_list, which says
which Bazaar vendor offers which list) and data/vendor_catalog.md (what's on each list).

    python3 tools/vendor_catalog.py --mysql "mariadb -uroot acore_world" \\
        --dbc <the server's data>/dbc

--mysql is the command that runs SQL on stdin against the (unchanged, ChromieCraft) world
database and prints tab-separated rows (mariadb's batch output; the app's
"sh <files>/server/ctl.sh sql acore_world" does too); --dbc the folder with the client's DBC files
(DungeonEncounter.dbc, ItemSet.dbc, ItemExtendedCost.dbc, GemProperties.dbc,
SpellItemEnchantment.dbc, Spell.dbc).
"""

import argparse
import math
import os
import shlex
import struct
import subprocess
from collections import OrderedDict, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
SQL = os.path.join(DATA, "sql", "remix", "world", "wrath_remix_world_0010_vendors.sql")
CATALOG = os.path.join(DATA, "vendor_catalog.md")

BRONZE = 77001          # the Bronze currency item (wrath_remix_world_0009_bronze.sql)
COST_BASE = 7700        # ItemExtendedCost ids: COST_BASE + the price's place on the ladder
LIST_BASE = 770300      # the lists' hidden vendor templates: LIST_BASE + 1, 2, ...
LIST_LAST = 770399
VISIBLE = 150           # what one vendor window can show a player (MAX_VENDOR_ITEMS)
STORED = 255            # what a list may hold (the core counts its items in a byte)
GOSSIP = 31             # lists one vendor may name (GOSSIP_MAX_MENU_ITEMS, 32, less the Bronze line)

# Every price a ware can have, in Bronze: one ItemExtendedCost row each.
LADDER = [25, 50, 75, 100, 150, 200, 250, 300, 400, 500, 600, 750, 1000, 1250, 1500, 2000,
          2500, 3000, 4000, 5000, 6000, 7500, 10000, 12500, 15000, 20000, 25000]

# The Bazaar's vendors (wrath_remix_world_0009_bronze.sql), after the guide's roster and Legion
# Remix's cast, each with their Legion Remix trade in its Wrath version.
ALURMI, HOROS, DOMELIUS, ARTUROS, AEONICUS, DURUS = 770005, 770201, 770202, 770203, 770204, 770205
PYTHAGORUS = 770206     # Mythic apparel: the raids' 25 player heroic
SACERDORMU = 770207     # Heroic apparel: the raids' 10 player heroic
AGOS = 770208           # Lost and Found apparel: the arena seasons' and Wintergrasp's
LARAH = 770209          # World apparel: Northrend's factions, the Argent Tournament, the Ashen Verdict
FREDDIE = 770210        # Discount cloaks: every cloak on the other lists, a step cheaper
JAKKUS = 770211         # Class wares: relics and glyphs
HEMET = 770212          # Mounts
NOSTWIN = 770213        # Snacks and stuff: food, drink, potions, elixirs, flasks, scrolls, bandages
UNICUS = 770214         # Exclusive ensembles: tabards, shirts and holiday costumes
LIDAMORRUTU = 770215    # Gems
LINDORMI = 770216       # Emblems (the dungeons are Sa'at's)
ERUS = 770217           # Crafting materials
NAMES = OrderedDict([
    (ALURMI, "Alurmi"), (HOROS, "Horos"), (DOMELIUS, "Domelius"), (ARTUROS, "Arturos"),
    (AEONICUS, "Aeonicus"), (DURUS, "Durus"), (SACERDORMU, "Sacerdormu"), (PYTHAGORUS, "Pythagorus"),
    (AGOS, "Agos the Silent"), (LARAH, "Larah Treebender"), (FREDDIE, "Freddie Threads"),
    (JAKKUS, "Grandmaster Jakkus"), (HEMET, "Hemet Nesingwary XVII"), (NOSTWIN, "Nostwin"),
    (UNICUS, "Unicus"), (LIDAMORRUTU, "Lidamorrutu"), (LINDORMI, "Lindormi"), (ERUS, "Erus"),
])

# Dungeons and raids: map -> name. A raid's modes are 10, 25, 10 heroic, 25 heroic; a dungeon's
# normal and heroic (the creature's difficulty entries, in that order).
DUNGEONS = OrderedDict([
    (574, "Utgarde Keep"), (576, "The Nexus"), (601, "Azjol-Nerub"), (619, "Ahn'kahet"),
    (600, "Drak'Tharon Keep"), (608, "The Violet Hold"), (604, "Gundrak"), (599, "Halls of Stone"),
    (602, "Halls of Lightning"), (578, "The Oculus"), (575, "Utgarde Pinnacle"),
    (595, "The Culling of Stratholme"), (650, "Trial of the Champion"), (632, "The Forge of Souls"),
    (658, "Pit of Saron"), (668, "Halls of Reflection"),
])
FROZEN_HALLS = {632, 658, 668}
RAIDS = OrderedDict([
    (533, "Naxxramas"), (615, "The Obsidian Sanctum"), (616, "The Eye of Eternity"),
    (624, "Vault of Archavon"), (603, "Ulduar"), (249, "Onyxia's Lair"),
    (649, "Trial of the Crusader"), (631, "Icecrown Citadel"), (724, "The Ruby Sanctum"),
])
HEROIC_RAIDS = {649, 631, 724}
# A raid's modes' vendors, as Legion Remix splits its raids' apparel: Raid Finder's (Aeonicus) the
# 10 player, Normal's (Durus) the 25 player, Heroic's (Sacerdormu) the 10 player heroic, Mythic's
# (Pythagorus) the 25 player heroic.
RAID_MODES = [(0, "10 player", AEONICUS), (1, "25 player", DURUS), (2, "10 player heroic", SACERDORMU),
              (3, "25 player heroic", PYTHAGORUS)]

# Tier sets: (vendor, label, item set ids, item level). The sets two modes share go to the one whose
# tokens they were: Tier 9 at 245 to the 25 player (the Trophy of the Crusade drops in 25 player
# Trial of the Crusader, not in 10 heroic), Tier 10 at 264 to the 10 player heroic (the Mark of
# Sanctification drops in both; the heroic vendor sells its look, as each of Legion Remix's does).
T7 = list(range(787, 806))
T8 = list(range(820, 839))
T9 = list(range(843, 881))
T10 = list(range(883, 902))
TIERS = [
    (AEONICUS, "Tier 7, Naxxramas (10 player)", T7, 200),
    (AEONICUS, "Tier 8, Ulduar (10 player)", T8, 219),
    (AEONICUS, "Tier 9, Trial of the Crusader (10 player)", T9, 232),
    (AEONICUS, "Tier 10, Icecrown Citadel (10 player)", T10, 251),
    (DURUS, "Tier 7, Naxxramas (25 player)", T7, 213),
    (DURUS, "Tier 8, Ulduar (25 player)", T8, 226),
    (DURUS, "Tier 9, Trial of the Crusader (25 player)", T9, 245),
    (PYTHAGORUS, "Tier 9, Trial of the Grand Crusader (25 heroic)", T9, 258),
    (SACERDORMU, "Tier 10, Icecrown Citadel (25 player and 10 heroic)", T10, 264),
    (PYTHAGORUS, "Tier 10, Icecrown Citadel (25 heroic)", T10, 277),
]

LEGENDARIES = [(46017, 20000, "Val'anyr, Hammer of Ancient Kings"), (49623, 25000, "Shadowmourne")]

# Mounts from Wrath (3.0 to 3.3): (item, price). Faction mounts are shown to their own side only.
MOUNTS = [
    # Drakes and proto-drakes: raids, dungeons, achievements, reputation, rares.
    (43955, 4000), (44178, 6000), (44707, 6000), (44177, 6000), (43952, 7500), (43953, 7500),
    (44151, 7500), (43951, 7500), (43986, 7500), (44160, 7500), (43954, 10000), (44168, 10000),
    (44164, 10000), (44175, 10000), (45802, 10000), (45801, 10000), (49636, 10000),
    (51954, 10000), (51955, 12500), (45693, 15000), (50818, 20000),
    # Mammoths, bears, the Argent Crusade's and the Kirin Tor's.
    (44230, 1500), (44231, 1500), (43956, 2500), (44077, 2500), (44225, 2500), (44226, 2500),
    (43958, 2500), (44080, 2500), (43961, 4000), (44086, 4000), (44234, 5000), (44235, 5000),
    (43962, 2500), (44223, 4000), (44224, 4000), (43959, 6000), (44083, 6000),
    (44413, 5000), (41508, 5000), (44689, 2500), (44690, 2500), (44842, 4000), (44843, 4000),
    (45725, 2500), (46813, 2500), (46814, 2500), (46815, 1500), (46816, 1500),
    (47179, 2500), (47180, 2500), (49044, 4000), (49046, 4000), (49096, 6000), (49098, 6000),
    # The capitals' mounts at the Argent Tournament, and the races' new ones.
    (45125, 1500), (45586, 1500), (45589, 1500), (45590, 1500), (45591, 1500), (45592, 1500),
    (45593, 1500), (45595, 1500), (45596, 1500), (45597, 1500),
    (46743, 1500), (46744, 1500), (46745, 1500), (46746, 1500), (46747, 1500), (46748, 1500),
    (46749, 1500), (46750, 1500), (46751, 1500), (46752, 1500), (46755, 1500), (46756, 1500),
    (46757, 1500), (46758, 1500), (46759, 1500), (46760, 1500), (46761, 1500), (46762, 1500),
    (46763, 1500), (46764, 1500),
    (46099, 1000), (46100, 1000), (46102, 1500), (46308, 1000), (47100, 1000), (47101, 1500),
    # Crafted, the Gladiators' frost wyrms, and the era's rewards and rarities.
    (44554, 2500), (44558, 5000), (54797, 5000), (40775, 4000), (46109, 4000), (52200, 10000),
    (46171, 10000), (46708, 10000), (47840, 10000), (50435, 12500),
    (50250, 7500), (54811, 7500), (54860, 7500), (54068, 6000), (54069, 6000), (46778, 6000),
    (43599, 6000), (49282, 6000),
]

# Companions from Wrath: (item, price).
PETS = [
    (39896, 250), (39898, 250), (39899, 250), (39973, 250), (43698, 250), (44721, 250),
    (44822, 250), (46398, 250), (40653, 250), (39148, 250), (44820, 250),
    (44965, 400), (44970, 400), (44971, 400), (44973, 400), (44974, 400), (44980, 400),
    (44982, 400), (44983, 400), (44984, 400), (45002, 400), (45606, 400), (44998, 600),
    (45022, 600), (46820, 600), (46821, 600), (44723, 500), (44738, 500), (44841, 500),
    (46544, 400), (46545, 400), (46707, 400), (46831, 400), (50446, 400), (54436, 400),
    (48112, 400), (48114, 400), (48116, 400), (48118, 400), (48120, 400), (48122, 400),
    (48124, 400), (48126, 400), (45942, 750), (49362, 750), (49912, 750), (54810, 1000),
    (39286, 1000), (39656, 1000), (41133, 1000), (44819, 1000), (45180, 1000), (46767, 1000),
    (46802, 1000), (49287, 1000), (49343, 1000), (49646, 1000), (49662, 1000), (49663, 1000),
    (49665, 1000), (49693, 1000), (54847, 1000), (56806, 1000), (48527, 1000), (43517, 500),
]

# Toys: Wrath's fun items that last (none that wants a profession to use).
TOYS = [
    (43499, 250), (44719, 250), (45984, 250), (46843, 250), (37710, 250), (54343, 250),
    (43824, 500), (44430, 500), (44606, 500), (45057, 500), (45063, 500), (46349, 500),
    (46709, 500), (46780, 500), (50471, 500), (54212, 500), (54651, 500), (54653, 500),
    (49703, 750), (49704, 750), (52201, 750), (52251, 750), (52253, 750), (54452, 1000),
]

# Heirlooms (every one the game has) and supplies, Alurmi's.
HEIRLOOMS = [
    (42949, 300), (42950, 300), (42951, 300), (42952, 300), (42984, 300), (42985, 300),
    (44099, 300), (44100, 300), (44101, 300), (44102, 300), (44103, 300), (44105, 300),
    (44107, 300), (48677, 500), (48683, 500), (48685, 500), (48687, 500), (48689, 500),
    (48691, 500), (42943, 500), (42944, 500), (42945, 500), (42946, 500), (42947, 500),
    (42948, 500), (44091, 500), (44092, 500), (44093, 500), (44094, 500), (44095, 500),
    (44096, 500), (48716, 500), (48718, 500), (42991, 400), (42992, 400), (50255, 400),
    (44097, 400), (44098, 400),
]
SUPPLIES = [(41599, 100)]

# Agos the Silent's: what the PvP vendors sell for honor, arena points or Wintergrasp's Marks of
# Honor, item level 187 and up, by the gladiators' season its item level is (the trinkets,
# medallions and battlemasters' too), and Wintergrasp's own.
WG_MARK = 43589         # Wintergrasp Mark of Honor
PVP_SEASONS = [(0, "Savage and Hateful Gladiator's"), (213, "Deadly Gladiator's"),
               (226, "Furious Gladiator's"), (245, "Relentless Gladiator's"), (264, "Wrathful Gladiator's")]
WINTERGRASP = "Wintergrasp's Titan-Forged"

# Larah Treebender's: the wearable wares of Northrend's factions' quartermasters (the Alliance
# Vanguard's and the Horde Expedition's for Valiance and Warsong, the Kalu'ak's, the Kirin Tor's
# and their ring vendor's, the Wyrmrest Accord's, the Ebon Blade's, Frenzyheart's, the Oracles',
# the Argent Crusade's, the Sons of Hodir's, the Ashen Verdict's, the Silver Covenant's and the
# Sunreavers'), the Argent Tournament's (the capitals' quartermasters there and the Crusader's), and
# the Ashen Verdict's rings (quest rewards).
FACTION_VENDORS = [32564, 32773, 32565, 32774, 31916, 32763, 32287, 32172, 32533, 32538, 31911,
                   31910, 30431, 32540, 37687, 34881, 34772]
TOURNAMENT_VENDORS = [33307, 33310, 33553, 33554, 33555, 33556, 33557, 33650, 33653, 33657, 34885]

# Grandmaster Jakkus's: each class's relics of Northrend, and its glyphs.
RELICS = OrderedDict([(7, "Librams"), (8, "Idols"), (9, "Totems"), (10, "Sigils")])
CLASSES = OrderedDict([(1, "Warrior"), (2, "Paladin"), (3, "Hunter"), (4, "Rogue"), (5, "Priest"),
                       (6, "Death knight"), (7, "Shaman"), (8, "Mage"), (9, "Warlock"), (11, "Druid")])
GLYPH_PRICE = 25

# Lidamorrutu's: Northrend's cut gems, rare and epic, its meta and prismatic gems (none whose bonus
# wants a profession: the Dragon's Eyes are a jewelcrafter's own).
GEM_PRICES = {3: 150, 4: 400}
META_PRICE = 500

# Nostwin's: Northrend's consumables, (item, price).
FOOD = [
    # The cooks' feasts and their food that leaves one well fed, the hunters' pets' treats.
    (34753, 50), (43015, 50), (43478, 50), (43480, 50),
    (34748, 25), (34749, 25), (34750, 25), (34751, 25), (34752, 25), (34754, 25), (34755, 25),
    (34756, 25), (34757, 25), (34758, 25), (34762, 25), (34763, 25), (34764, 25), (34765, 25),
    (34766, 25), (34767, 25), (34768, 25), (34769, 25), (42942, 25), (42993, 25), (42994, 25),
    (42995, 25), (42996, 25), (42997, 25), (42998, 25), (42999, 25), (43000, 25), (43001, 25),
    (43268, 25), (44953, 25), (34125, 25), (39691, 25), (42779, 25), (45932, 25), (43005, 25),
    # Drink.
    (33444, 25), (33445, 25), (35954, 25), (37253, 25), (40357, 25), (41731, 25), (42777, 25),
    (43236, 25), (43086, 25), (44941, 25), (44750, 25), (38698, 25),
]
POTIONS = [
    # Potions and injectors.
    (33447, 50), (33448, 50), (39671, 50), (40067, 50), (40077, 50), (40081, 50), (40087, 50),
    (40093, 50), (40211, 50), (40212, 50), (40213, 50), (40214, 50), (40215, 50), (40216, 50),
    (40217, 50), (41166, 50), (42545, 50),
    # Elixirs.
    (39666, 50), (40068, 50), (40070, 50), (40072, 50), (40073, 50), (40076, 50), (40078, 50),
    (40097, 50), (40109, 50), (44325, 50), (44327, 50), (44328, 50), (44329, 50), (44330, 50),
    (44331, 50), (44332, 50),
    # Flasks.
    (46376, 100), (46377, 100), (46378, 100), (46379, 100), (40079, 50), (44939, 50),
]
SCROLLS = [
    (37091, 25), (37093, 25), (37097, 25), (43463, 25), (43465, 25), (43467, 25), (37092, 25),
    (37094, 25), (37098, 25), (43464, 25), (43466, 25), (49632, 50),
    # Bandages (their First Aid taken off with the other requirements).
    (34721, 25), (34722, 25),
]

# Unicus's: Wrath's looks, (item, price).
TABARDS = [
    # Northrend's factions', the Argent Tournament's capitals', the Silver Covenant's and the
    # Sunreavers', Midsummer's.
    (43154, 250), (43155, 250), (43156, 250), (43157, 250), (45574, 250), (45577, 250),
    (45578, 250), (45579, 250), (45580, 250), (45581, 250), (45582, 250), (45583, 250),
    (45584, 250), (45585, 250), (46817, 250), (46818, 250), (35279, 250), (35280, 250),
    # The Argent Tournament's champions', the achievements', the gladiators'.
    (46874, 500), (40643, 500), (43300, 500), (43348, 500), (43349, 500), (49052, 500),
    (49054, 500), (52252, 500), (45983, 1000), (49086, 1000), (51534, 1000),
    # The era's trading card game's and its tournament's, never in the game itself.
    (38309, 750), (38310, 750), (38311, 750), (38312, 750), (38313, 750), (38314, 750), (36941, 750),
]
SHIRTS = [
    (42360, 100), (42361, 100), (42363, 100), (42365, 100), (42368, 100), (42369, 100),
    (42370, 100), (42371, 100), (42372, 100), (42373, 100), (42374, 100), (42375, 100),
    (42376, 100), (42377, 100), (42378, 100), (41248, 100), (41249, 100), (41250, 100),
    (41251, 100), (41252, 100), (41253, 100), (41254, 100), (41255, 100), (45664, 100),
    (45666, 100), (45667, 100), (45668, 100), (45669, 100), (45670, 100), (45671, 100),
    (45672, 100), (45673, 100), (45674, 100), (44693, 100), (44694, 100), (52019, 250),
]
HOLIDAYS = [
    # Midsummer, the Lunar Festival, Noblegarden, Brewfest, the Day of the Dead, Pilgrim's Bounty,
    # Hallow's End, the Feast of Winter Veil, Love is in the Air.
    (23323, 150), (23324, 150), (34683, 150), (34685, 150), (21157, 150), (21538, 150),
    (21539, 150), (21541, 150), (21543, 150), (21544, 150), (6833, 150), (6835, 150), (19028, 150),
    (44800, 150), (44803, 150), (45073, 150), (33047, 150), (34008, 150), (33862, 150),
    (33863, 150), (33864, 150), (33868, 150), (33966, 150), (33967, 150), (33968, 150),
    (33969, 150), (46860, 150), (46861, 150), (44785, 150), (44788, 150), (46723, 150),
    (46800, 150), (46824, 150), (33292, 150), (21524, 150), (21525, 150), (34085, 150),
    (34087, 150), (22276, 150), (22278, 150), (22279, 150), (22280, 150), (22277, 150),
    (22281, 150), (22282, 150),
]

# Lindormi's: the emblems (so the Dalaran emblem vendors open up) and the Badge of Justice. Dear
# enough that no gear is cheaper through them than on the Bronze vendors' lists (none dearer for
# the newer, which Dalaran trades down): Tier 7 for 30 to 45 Emblems of Heroism comes to 750 to
# 1,125 Bronze, against 250 from Aeonicus; the 226 pieces for 19 to 39 Emblems of Conquest to 475
# to 975, against 400 to 500 on Durus's Ulduar list; the 245 pieces for 25 to 75 Emblems of
# Triumph to 1,250 to 3,750, against 750 to 1,000; the 264 pieces for 30 to 95 Emblems of Frost
# to 1,500 to 4,750, against 1,250 to 2,000 from Sacerdormu.
EMBLEMS = [(29434, 25), (40752, 25), (40753, 25), (45624, 25), (47241, 50), (49426, 50)]

# Erus's: Northrend's crafting materials, (item, price).
MATERIALS = [
    # Herbs, pigments and inks.
    (36901, 25), (36903, 25), (36904, 25), (36905, 25), (36906, 25), (36907, 25), (37921, 25),
    (39970, 25), (36908, 50), (39343, 25), (43109, 50), (43126, 25), (43127, 50),
    # Ore and bars.
    (36909, 25), (36916, 25), (36912, 25), (36913, 25), (36910, 50), (41163, 50), (46849, 50),
    (37663, 100),
    # Cloth.
    (33470, 25), (41510, 25), (41511, 50), (41593, 100), (41594, 100), (41595, 100),
    # Leather, scales and fur.
    (33567, 25), (33568, 25), (38425, 50), (38557, 25), (38558, 25), (38561, 25), (44128, 100),
    # Enchanting.
    (34054, 25), (34056, 25), (34055, 50), (34053, 25), (34052, 75), (34057, 100),
    # Elements.
    (37700, 25), (37701, 25), (37702, 25), (37703, 25), (37704, 25), (37705, 25), (35622, 50),
    (35623, 50), (35624, 50), (35625, 50), (35627, 50), (36860, 50),
    # The orbs, and the rarest.
    (43102, 100), (45087, 250), (47556, 400), (49908, 750),
]

INVTYPE_2H, INVTYPE_RANGED, INVTYPE_RANGEDRIGHT, INVTYPE_TRINKET = 17, 15, 26, 12
INVTYPE_ONEHAND = {13, 21, 22}
INVTYPE_SHIRT, INVTYPE_CLOAK, INVTYPE_TABARD, INVTYPE_RELIC = 4, 16, 19, 28


def run_sql(mysql, sql):
    out = subprocess.run(shlex.split(mysql) + ["--batch", "--skip-column-names"], input=sql,
                         capture_output=True, text=True, check=True).stdout
    return [line.split("\t") for line in out.splitlines() if line]


def read_dbc(path):
    data = open(path, "rb").read()
    _, rows, fields, size, _ = struct.unpack("<4s4I", data[:20])
    strings = data[20 + rows * size:]
    records = [struct.unpack_from("<%di" % fields, data, 20 + i * size) for i in range(rows)]
    return records, strings


def dbc_string(strings, offset):
    return strings[offset:strings.index(b"\0", offset)].decode("utf-8", "replace")


def snap(price):
    """The ladder's nearest price (nearest by ratio)."""
    return min(LADDER, key=lambda p: abs(math.log(p / price)))


def gear_price(level, inventory_type):
    """Bronze for raid and dungeon gear: 200 at item level 200, 3% more a level, weapons and
    trinkets a little more."""
    price = 200 * 1.03 ** (level - 200)
    if inventory_type in (INVTYPE_2H, INVTYPE_RANGED, INVTYPE_RANGEDRIGHT):
        price *= 1.5
    elif inventory_type in INVTYPE_ONEHAND or inventory_type == INVTYPE_TRINKET:
        price *= 1.25
    return snap(max(price, 50))


class Catalog:
    def __init__(self, mysql, dbc):
        self.mysql = mysql
        self.dbc = dbc
        self.items = {}
        self.lists = []  # (vendor, label, side, [(item, price)])

    def item_info(self, ids):
        ids = sorted(set(ids) - set(self.items))
        for i in range(0, len(ids), 500):
            chunk = ",".join(str(x) for x in ids[i:i + 500])
            for row in run_sql(self.mysql, f"SELECT entry, name, class, subclass, Quality, ItemLevel, InventoryType, "
                               f"FlagsExtra & 3, AllowableClass, bonding, itemset FROM item_template WHERE entry IN ({chunk})"):
                e = int(row[0])
                self.items[e] = dict(name=row[1], cls=int(row[2]), sub=int(row[3]), quality=int(row[4]),
                                     level=int(row[5]), inv=int(row[6]), side=int(row[7]),
                                     classes=int(row[8]), bonding=int(row[9]), itemset=int(row[10]))

    def loot(self, table, ids):
        """Every item [ids]' loot can give, references followed."""
        found, refs, seen = set(), set(), set()
        todo = [(table, i) for i in ids if i]
        while todo:
            batch = defaultdict(list)
            for t, i in todo:
                if (t, i) not in seen:
                    seen.add((t, i))
                    batch[t].append(i)
            todo = []
            for t, entries in batch.items():
                rows = run_sql(self.mysql, f"SELECT Item, Reference FROM {t} WHERE Entry IN ({','.join(map(str, entries))})")
                for item, ref in rows:
                    if int(ref):
                        todo.append(("reference_loot_template", int(ref)))
                    else:
                        found.add(int(item))
        return found

    def encounters(self):
        """map -> the creature entries whose kill is a boss of it (instance_encounters)."""
        records, _ = read_dbc(os.path.join(self.dbc, "DungeonEncounter.dbc"))
        maps = {r[0]: r[1] for r in records}
        bosses = defaultdict(set)
        for entry, kind, credit in run_sql(self.mysql, "SELECT entry, creditType, creditEntry FROM instance_encounters"):
            m = maps.get(int(entry))
            if m in DUNGEONS or m in RAIDS:
                if int(kind) == 0:
                    bosses[m].add(int(credit))
        return bosses

    def modes(self, entries):
        """creature entry -> its loot ids by mode (the entry and its difficulty entries)."""
        if not entries:
            return {}
        rows = run_sql(self.mysql, "SELECT ct.entry, ct.lootid, d1.lootid, d2.lootid, d3.lootid FROM creature_template ct "
                       "LEFT JOIN creature_template d1 ON d1.entry = ct.difficulty_entry_1 "
                       "LEFT JOIN creature_template d2 ON d2.entry = ct.difficulty_entry_2 "
                       "LEFT JOIN creature_template d3 ON d3.entry = ct.difficulty_entry_3 "
                       f"WHERE ct.entry IN ({','.join(map(str, entries))})")
        return {int(r[0]): [int(x) if x not in ("", "NULL") else 0 for x in r[1:]] for r in rows}

    def chests(self, map_id):
        """The chests of an instance: loot id by mode (the spawn mask's bits)."""
        rows = run_sql(self.mysql, "SELECT g.spawnMask, t.Data1 FROM gameobject g JOIN gameobject_template t ON t.entry = g.id "
                       f"WHERE g.map = {map_id} AND t.type = 3 AND t.Data1 > 0")
        by_mode = defaultdict(set)
        for mask, loot in rows:
            for mode in range(4):
                if int(mask) & (1 << mode):
                    by_mode[mode].add(int(loot))
        return by_mode

    def gear(self, items, raid):
        """Of [items]: armor and weapons of the instance's quality, not tier tokens or sets (the tier
        vendors have those), recipes, mounts or junk."""
        self.item_info(items)
        keep = []
        for e in items:
            i = self.items.get(e)
            if not i or i["cls"] not in (2, 4) or i["level"] < 150:
                continue
            if i["quality"] < (4 if raid else 3) or i["quality"] > 4:
                continue
            if i["itemset"] and i["cls"] == 4 and i["level"] >= 200 and i["itemset"] in T7 + T8 + T9 + T10:
                continue
            keep.append(e)
        return keep

    def made(self):
        """The items a spell makes (Spell.dbc's create item effects): what the professions craft."""
        if not hasattr(self, "_made"):
            records, _ = read_dbc(os.path.join(self.dbc, "Spell.dbc"))
            # Effect[3] at 71 to 73, EffectItemType[3] at 107 to 109; 24 is SPELL_EFFECT_CREATE_ITEM
            self._made = {r[107 + k] for r in records for k in range(3) if r[71 + k] == 24 and r[107 + k]}
        return self._made

    def obtainable(self, ids):
        """Of [ids]: those the game gives somehow (a vendor, any loot, a quest, a spell that makes them)."""
        ids = sorted(set(ids))
        found = set(ids) & self.made()
        rewards = ["RewardItem%d" % n for n in range(1, 5)] + ["RewardChoiceItemID%d" % n for n in range(1, 7)]
        for i in range(0, len(ids), 500):
            chunk = ",".join(str(x) for x in ids[i:i + 500])
            queries = [f"SELECT item FROM npc_vendor WHERE item IN ({chunk})"]
            queries += [f"SELECT Item FROM {t} WHERE Item IN ({chunk}) AND Reference = 0" for t in (
                "creature_loot_template", "gameobject_loot_template", "item_loot_template",
                "reference_loot_template", "mail_loot_template", "disenchant_loot_template",
                "prospecting_loot_template", "milling_loot_template", "skinning_loot_template",
                "pickpocketing_loot_template", "fishing_loot_template")]
            queries += [f"SELECT {c} FROM quest_template WHERE {c} IN ({chunk})" for c in rewards]
            found |= {int(r[0]) for r in run_sql(self.mysql, " UNION ".join(queries))}
        return found

    def gear_wares(self, ids, low=0, high=4):
        """Of [ids]: what can be worn but a shirt or a tabard (Unicus's), of quality low to high."""
        self.item_info(ids)
        return sorted(e for e in set(ids) if e in self.items and self.items[e]["cls"] in (2, 4)
                      and self.items[e]["inv"] not in (0, INVTYPE_SHIRT, INVTYPE_TABARD)
                      and low <= self.items[e]["quality"] <= high)

    def priced(self, ids):
        return [(e, gear_price(self.items[e]["level"], self.items[e]["inv"])) for e in ids]

    def handpicked(self, vendor, label, wares):
        self.item_info([e for e, _ in wares])
        missing = [e for e, _ in wares if e not in self.items]
        if missing:
            raise SystemExit(f"{label}: no such items {missing}")
        twice = sorted({e for e, _ in wares if [w for w, _ in wares].count(e) > 1})
        if twice:
            raise SystemExit(f"{label}: items listed twice {twice}")
        self.add(vendor, label, wares)

    def add(self, vendor, label, wares, side=0, levels=False):
        """A list, split in parts no player sees more than a window of (each part named by its item
        levels with levels, else numbered)."""
        wares = sorted(set(wares), key=lambda w: (self.items.get(w[0], {}).get("inv", 0), self.items.get(w[0], {}).get("level", 0), w[0]))
        def shown(item, cls, side):
            # as the core's vendor window does: a side's items to that side only, and a
            # bind-on-pickup item to the classes that can use it
            i = self.items.get(item, {})
            if i.get("side", 0) not in (0, side):
                return False
            classes = i.get("classes", -1)
            return i.get("bonding") != 1 or classes == -1 or bool(classes & (1 << (cls - 1)))

        def visible(part):
            return max(sum(1 for w, _ in part if shown(w, c, s)) for c in (1, 2, 3, 4, 5, 6, 7, 8, 9, 11) for s in (1, 2))
        parts, current = [], []
        for w in wares:
            current.append(w)
            if len(current) >= STORED or visible(current) > VISIBLE:
                current.pop()
                parts.append(current)
                current = [w]
        if current:
            parts.append(current)
        for n, part in enumerate(parts):
            if levels:
                low, high = (f(self.items[w]["level"] for w, _ in part) for f in (min, max))
                name = f"{label}, item level {low}" + (f" to {high}" if high > low else "")
            else:
                name = label if len(parts) == 1 else f"{label}, part {n + 1}"
            self.lists.append((vendor, name, side, part))

    def build(self):
        bosses = self.encounters()
        boss_modes = self.modes(sorted(set().union(*bosses.values())))

        # Dungeons (Arturos): the Northrend dungeons normal and heroic, the Argent Tournament's,
        # the Frozen Halls normal and heroic.
        groups = defaultdict(set)
        for m in DUNGEONS:
            chests = self.chests(m)
            for mode in (0, 1):
                creature = {boss_modes[b][mode] for b in bosses.get(m, ()) if b in boss_modes and boss_modes[b][mode]}
                key = ("Trial of the Champion" if m == 650 else "The Frozen Halls" if m in FROZEN_HALLS
                       else "Northrend's dungeons") + (", heroic" if mode else "")
                items = self.loot("creature_loot_template", creature) | self.loot("gameobject_loot_template", chests[mode])
                groups[key] |= set(self.gear(items, False))
        for label in ("Northrend's dungeons", "Northrend's dungeons, heroic", "Trial of the Champion",
                      "Trial of the Champion, heroic", "The Frozen Halls", "The Frozen Halls, heroic"):
            self.add(ARTUROS, label, [(e, gear_price(self.items[e]["level"], self.items[e]["inv"])) for e in groups[label]])

        # Raids: 10 player (Aeonicus), 25 player (Durus), 10 player heroic (Sacerdormu), 25 player
        # heroic (Pythagorus).
        for m, name in RAIDS.items():
            modes = RAID_MODES if m in HEROIC_RAIDS else RAID_MODES[:2]
            chests = self.chests(m)
            for mode, size, vendor in modes:
                creature = {boss_modes[b][mode] for b in bosses.get(m, ()) if b in boss_modes and boss_modes[b][mode]}
                items = self.loot("creature_loot_template", creature) | self.loot("gameobject_loot_template", chests[mode])
                gear = self.gear(items, True)
                if gear:
                    self.add(vendor, f"{name} ({size})", [(e, gear_price(self.items[e]["level"], self.items[e]["inv"])) for e in gear])

        # Tier sets: every piece of every class's set at that item level (each sees its own).
        records, strings = read_dbc(os.path.join(self.dbc, "ItemSet.dbc"))
        self.set_names = {r[0]: dbc_string(strings, r[1]) for r in records}
        for vendor, label, sets, level in TIERS:
            rows = run_sql(self.mysql, f"SELECT entry FROM item_template WHERE itemset IN ({','.join(map(str, sets))}) "
                           f"AND ItemLevel = {level} AND class = 4 AND Quality = 4")
            items = [int(r[0]) for r in rows]
            self.item_info(items)
            price = snap(250 * 1.03 ** (level - 200))
            alliance = [(e, price) for e in items if self.items[e]["side"] != 1]
            horde = [(e, price) for e in items if self.items[e]["side"] != 2]
            if len(items) > STORED:
                self.add(vendor, label, alliance, side=1)
                self.add(vendor, label, horde, side=2)
            else:
                self.add(vendor, label, [(e, price) for e in items])

        self.item_info([e for e, _, _ in LEGENDARIES])
        self.add(DURUS, "Legendaries", [(e, p) for e, p, _ in LEGENDARIES])

        for vendor, label, wares in ((HEMET, "Mounts of Northrend", MOUNTS), (DOMELIUS, "Companions", PETS),
                                     (HOROS, "Toys and curiosities", TOYS), (ALURMI, "Heirlooms", HEIRLOOMS),
                                     (ALURMI, "Supplies", SUPPLIES)):
            self.handpicked(vendor, label, wares)

        self.pvp()
        self.factions()
        self.class_wares()
        for vendor, label, wares in ((NOSTWIN, "Food and drink", FOOD), (NOSTWIN, "Potions, elixirs and flasks", POTIONS),
                                     (NOSTWIN, "Scrolls and bandages", SCROLLS), (UNICUS, "Tabards", TABARDS),
                                     (UNICUS, "Shirts", SHIRTS), (UNICUS, "Holiday costumes", HOLIDAYS)):
            self.handpicked(vendor, label, wares)
        self.gems()
        for vendor, label, wares in ((LINDORMI, "Emblems", EMBLEMS), (ERUS, "Materials of Northrend", MATERIALS)):
            self.handpicked(vendor, label, wares)
        self.cloaks()

    def pvp(self):
        """Agos's: the PvP vendors' apparel by season, and Wintergrasp's."""
        records, _ = read_dbc(os.path.join(self.dbc, "ItemExtendedCost.dbc"))
        # ID, HonorPoints, ArenaPoints, ArenaBracket, ItemID[5], ItemCount[5], ...
        marks = {r[0] for r in records if WG_MARK in r[4:9]}
        costs = sorted({r[0] for r in records if r[1] or r[2]} | marks)
        rows = run_sql(self.mysql, f"SELECT DISTINCT item, ExtendedCost FROM npc_vendor WHERE ExtendedCost IN ({','.join(map(str, costs))})")
        wintergrasp = {int(e) for e, c in rows if int(c) in marks}
        groups = defaultdict(list)
        for e in self.gear_wares([int(e) for e, _ in rows], low=3):
            if self.items[e]["level"] < 187:
                continue
            season = [label for low, label in PVP_SEASONS if self.items[e]["level"] >= low][-1]
            groups[WINTERGRASP if e in wintergrasp else season].append(e)
        for label in [label for _, label in PVP_SEASONS] + [WINTERGRASP]:
            self.add(AGOS, label, self.priced(groups[label]))

    def factions(self):
        """Larah's: Northrend's factions' wearable wares, the Argent Tournament's, the Ashen Verdict's rings."""
        for label, vendors in (("Northrend's factions", FACTION_VENDORS), ("The Argent Tournament", TOURNAMENT_VENDORS)):
            rows = run_sql(self.mysql, f"SELECT DISTINCT item FROM npc_vendor WHERE entry IN ({','.join(map(str, vendors))})")
            self.add(LARAH, label, self.priced(self.gear_wares([int(r[0]) for r in rows], low=2)))
        rows = run_sql(self.mysql, "SELECT entry FROM item_template WHERE name LIKE 'Ashen Band of %'")
        self.add(LARAH, "The Ashen Verdict", self.priced(self.gear_wares([int(r[0]) for r in rows], low=4)))

    def class_wares(self):
        """Jakkus's: Northrend's relics, each kind its list, and each class's glyphs."""
        rows = run_sql(self.mysql, f"SELECT entry FROM item_template WHERE InventoryType = {INVTYPE_RELIC} AND entry >= 36000 "
                       "AND ItemLevel >= 130 AND Quality BETWEEN 2 AND 4")
        relics = self.obtainable(int(r[0]) for r in rows)
        self.item_info(relics)
        for sub, label in RELICS.items():
            self.add(JAKKUS, label, self.priced(e for e in relics if self.items[e]["sub"] == sub))
        rows = run_sql(self.mysql, "SELECT entry FROM item_template WHERE class = 16 AND Quality >= 1 AND name LIKE 'Glyph of %'")
        glyphs = {int(r[0]) for r in rows} & self.made()
        self.item_info(glyphs)
        for cls, name in CLASSES.items():
            self.add(JAKKUS, f"{name} glyphs", [(e, GLYPH_PRICE) for e in glyphs
                                                if self.items[e]["sub"] == cls and self.items[e]["classes"] == 1 << (cls - 1)])

    def gems(self):
        """Lidamorrutu's: Northrend's cut gems anyone may use (their bonus wanting no profession)."""
        properties, _ = read_dbc(os.path.join(self.dbc, "GemProperties.dbc"))
        enchants, _ = read_dbc(os.path.join(self.dbc, "SpellItemEnchantment.dbc"))
        enchant = {r[0]: r[1] for r in properties}          # ID, the gem's SpellItemEnchantment
        skill = {r[0]: r[35] for r in enchants}             # requiredSkill (35)
        rows = run_sql(self.mysql, "SELECT entry, GemProperties FROM item_template WHERE class = 3 AND entry >= 36000 "
                       "AND ItemLevel >= 80 AND Quality IN (3, 4) AND GemProperties > 0 AND RequiredSkill = 0")
        gems = self.obtainable(int(e) for e, g in rows if skill.get(enchant.get(int(g)), 1) == 0)
        self.item_info(gems)
        meta = [(e, META_PRICE if self.items[e]["sub"] == 6 else GEM_PRICES[self.items[e]["quality"]])
                for e in gems if self.items[e]["sub"] in (6, 8)]
        for quality, label in ((3, "Rare gems"), (4, "Epic gems")):
            self.add(LIDAMORRUTU, label, [(e, GEM_PRICES[quality]) for e in gems
                                          if self.items[e]["quality"] == quality and self.items[e]["sub"] not in (6, 8)])
        self.add(LIDAMORRUTU, "Meta and prismatic gems", meta)

    def cloaks(self):
        """Freddie's: every cloak on the other lists, a step down the ladder from its lowest price there."""
        lowest = {}
        for _, _, _, wares in self.lists:
            for e, p in wares:
                if self.items[e]["inv"] == INVTYPE_CLOAK and self.items[e]["quality"] <= 4:
                    lowest[e] = min(p, lowest.get(e, p))
        if any(p == LADDER[0] for p in lowest.values()):
            raise SystemExit("a cloak at the ladder's lowest price can't be had cheaper")
        self.add(FREDDIE, "Cloaks", [(e, LADDER[LADDER.index(p) - 1]) for e, p in lowest.items()], levels=True)

    def write(self):
        if len(self.lists) > LIST_LAST - LIST_BASE:
            raise SystemExit(f"{len(self.lists)} lists: more than the range holds")
        for vendor, name in NAMES.items():
            if sum(1 for v, _, _, _ in self.lists if v == vendor) > GOSSIP:
                raise SystemExit(f"{name}: more lists than a gossip menu holds")
        out = ["-- The Infinite Bazaar's Bronze vendors' lists. Made by tools/vendor_catalog.py from the world",
               "-- database (do not edit by hand; edit the tool and run it again). What's on them:",
               "-- data/vendor_catalog.md.", ""]
        out += ["-- The price ladder: one ItemExtendedCost per price (the client has the same rows: the module",
                "-- writes them into its patch).",
                f"DELETE FROM `itemextendedcost_dbc` WHERE `ID` BETWEEN {COST_BASE + 1} AND {COST_BASE + 99};",
                "INSERT INTO `itemextendedcost_dbc` (`ID`, `HonorPoints`, `ArenaPoints`, `ArenaBracket`, `ItemID_1`, `ItemID_2`, "
                "`ItemID_3`, `ItemID_4`, `ItemID_5`, `ItemCount_1`, `ItemCount_2`, `ItemCount_3`, `ItemCount_4`, `ItemCount_5`, "
                "`RequiredArenaRating`, `ItemPurchaseGroup`) VALUES"]
        out.append(",\n".join(f"({COST_BASE + n + 1}, 0, 0, 0, {BRONZE}, 0, 0, 0, 0, {p}, 0, 0, 0, 0, 0, 0)"
                              for n, p in enumerate(LADDER)) + ";")
        out += ["", "-- Each list is a vendor template of its own, never spawned: the Bazaar's vendors open it.",
                f"DELETE FROM `creature_template` WHERE `entry` BETWEEN {LIST_BASE + 1} AND {LIST_LAST};",
                "INSERT INTO `creature_template` (`entry`, `name`, `subname`, `minlevel`, `maxlevel`, `faction`, `npcflag`, "
                "`unit_class`, `flags_extra`) VALUES"]
        out.append(",\n".join(f"({LIST_BASE + n + 1}, 'Wrath Remix wares', '{sql(label)[:100]}', 80, 80, 35, 128, 1, 128)"
                              for n, (_, label, _, _) in enumerate(self.lists)) + ";")
        out += [f"DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN {LIST_BASE + 1} AND {LIST_LAST};",
                "INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`)",
                f"SELECT `entry`, 0, 19373, 1, 1, 0 FROM `creature_template` WHERE `entry` BETWEEN {LIST_BASE + 1} AND {LIST_LAST};",
                "", "DELETE FROM `remix_vendor_list`;",
                "INSERT INTO `remix_vendor_list` (`list`, `vendor`, `sort`, `side`, `label`) VALUES"]
        out.append(",\n".join(f"({LIST_BASE + n + 1}, {vendor}, {n + 1}, {side}, '{sql(label)}')"
                              for n, (vendor, label, side, _) in enumerate(self.lists)) + ";")
        out += ["", f"DELETE FROM `npc_vendor` WHERE `entry` BETWEEN {LIST_BASE + 1} AND {LIST_LAST};"]
        for n, (_, label, _, wares) in enumerate(self.lists):
            out.append(f"-- {label}")
            out.append("INSERT INTO `npc_vendor` (`entry`, `slot`, `item`, `maxcount`, `incrtime`, `ExtendedCost`) VALUES")
            out.append(",\n".join(f"({LIST_BASE + n + 1}, {slot}, {e}, 0, 0, {COST_BASE + LADDER.index(p) + 1})"
                                  for slot, (e, p) in enumerate(wares)) + ";")
        open(SQL, "w").write("\n".join(out) + "\n")

        md = ["# The Infinite Bazaar's Bronze vendors", "",
              "Made by `tools/vendor_catalog.py` (with `data/sql/remix/world/wrath_remix_world_0010_vendors.sql`).",
              "Prices in Bronze. A list shows each player only what their class and side can use.", ""]
        for vendor, name in NAMES.items():
            md.append(f"## {name}")
            md.append("")
            md.append("| List | Wares | Prices |")
            md.append("| --- | --- | --- |")
            for v, label, side, wares in self.lists:
                if v == vendor:
                    prices = sorted({p for _, p in wares})
                    who = {1: " (Alliance)", 2: " (Horde)"}.get(side, "")
                    md.append(f"| {label}{who} | {len(wares)} | {prices[0]:,} to {prices[-1]:,} |" if len(prices) > 1
                              else f"| {label}{who} | {len(wares)} | {prices[0]:,} |")
            md.append("")
        md.append("## The hand-picked lists")
        md.append("")
        for title, wares in (("Mounts", MOUNTS), ("Companions", PETS), ("Toys and curiosities", TOYS),
                             ("Food and drink", FOOD), ("Potions, elixirs and flasks", POTIONS),
                             ("Scrolls and bandages", SCROLLS), ("Tabards", TABARDS), ("Shirts", SHIRTS),
                             ("Holiday costumes", HOLIDAYS), ("Emblems", EMBLEMS), ("Materials of Northrend", MATERIALS)):
            md.append(f"**{title}:** " + ", ".join(f"{self.items[e]['name']} ({p:,})" for e, p in wares) + ".")
            md.append("")
        open(CATALOG, "w").write("\n".join(md))
        total = sum(len(w) for _, _, _, w in self.lists)
        print(f"{len(self.lists)} lists, {total} wares -> {os.path.relpath(SQL)}, {os.path.relpath(CATALOG)}")
        for vendor, label, side, wares in self.lists:
            print(f"  {NAMES[vendor]:21} {label}{' (A)' if side == 1 else ' (H)' if side == 2 else ''}: {len(wares)}")


def sql(text):
    return text.replace("\\", "\\\\").replace("'", "''")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--mysql", required=True, help="command running SQL on the world database")
    parser.add_argument("--dbc", required=True, help="folder with the client's DBC files")
    args = parser.parse_args()
    catalog = Catalog(args.mysql, args.dbc)
    catalog.build()
    catalog.write()


if __name__ == "__main__":
    main()
