#!/usr/bin/env python3
"""Writes the Infinite Bazaar's camp: data/sql/remix/world/wrath_remix_world_0023_bazaar.sql.

    python3 tools/bazaar.py

The Bazaar is a camp in Malykriss: The Vile Hold, the necropolis the Lich King began in Icecrown and never
finished (until build 117 it stood in Crystalsong Forest; every spot moved by the same step, x + 694 and
y + 854, onto the level floor under the necropolis's ribs). It is a camp, not a ring of people. Around the story's own people at its heart (Eternus,
Moratari, the echoes; wrath_remix_world_0004_spawns.sql and the others place them, and the turn's
scene walks between them), it has districts a Timerunner can read at a glance:

  - the heart, under a great hourglass, where every Timerunner wakes; Pageturner Metros's desk;
  - the market lane along the west edge: a stall for each Bronze trader, Alurmi's first;
  - the north row along the north edge, facing the heart: the heroic raids' pavilions (Pythagorus,
    Sacerdormu), the apparel stalls (Agos, Unicus, Larah, Freddie), Nedward's barber's chair;
  - the training yard to the south-east: the instructors at work, dummies and targets to try;
    Grandmaster Jakkus's stall and Momentus the weaponmaster at its east edge;
  - the waystation to the north-east: Zephyr, her drake and a door in time; Sa'at's map table;
    Hemet Nesingwary's mounts and proto-drake;
  - the chronicle corner to the north-west: the Chronologist's shelves, an orb; Lidamorrutu's gems,
    Lindormi's emblems;
  - the campfire to the south: other Timerunners, veterans of this war from their own hours after it,
    a cook; Nostwin's snacks, Erus's scrap;
  - and between them porters on their rounds, wardens walking the edge, whelps underfoot.

Legion Remix's Bazaar cast (the Bronze vendors, Metros, Nedward) are wrath_remix_world_0009_bronze.sql's
creatures, placed there (STORY_SPOTS keeps their spots); their stalls and lines are here.

Everyone with something to say says it now and then while a Timerunner is about, to the air or to
someone near them (src/RemixBazaar.cpp). Positions are the world's (x north, y west); heights are
the floor's, from data/bazaar_ground.tsv (`.remix ground` on the realm, a reading every two
yards), so nothing floats or sinks.
"""
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "sql", "remix", "world", "wrath_remix_world_0023_bazaar.sql")
GROUND = os.path.join(HERE, "..", "data", "bazaar_ground.tsv")

MAP, ZONE, AREA = 571, 210, 4520                                     # Icecrown; Malykriss: The Vile Hold

# Emotes (SharedDefines.h): one-shot gestures for lines, looping states for what people do.
TALK, BOW, WAVE, CHEER, EXCLAIM, QUESTION, EAT, LAUGH, POINT, SALUTE, YES, NO = 1, 2, 3, 4, 5, 6, 7, 11, 25, 66, 273, 274
STATE_WORK, STATE_TALK, STATE_EAT, STATE_READY1H, STATE_BOW, STATE_SPELL = 173, 378, 418, 333, 376, 474
SIT, SLEEP, KNEEL = 1, 3, 8                                          # stand states (creature_addon.bytes1)

EAST, NORTH, WEST, SOUTH = 3 * math.pi / 2, 0.0, math.pi / 2, math.pi


def load_ground():
    ground = {}
    if os.path.exists(GROUND):
        for line in open(GROUND):
            if line.startswith("#") or not line.strip():
                continue
            x, y, z = line.split()
            ground[(int(x), int(y))] = float(z)
    return ground


GROUND_Z = load_ground()


def z_at(x, y):
    """The floor under (x, y): the nearest reading within two yards (the plaza is level)."""
    best, best_d = None, 99.0
    for gx in range(int(x) - 3, int(x) + 4):
        for gy in range(int(y) - 3, int(y) + 4):
            if (gx, gy) in GROUND_Z:
                d = math.hypot(gx - x, gy - y)
                if d < best_d:
                    best, best_d = GROUND_Z[(gx, gy)], d
    if best is None:
        raise SystemExit(f"no floor reading near {x} {y}: survey there first (data/bazaar_ground.tsv)")
    return best


def facing(x, y, tx, ty):
    """The orientation from (x, y) towards (tx, ty)."""
    return math.atan2(ty - y, tx - x) % (2 * math.pi)


def sql_text(text):
    return "'" + text.replace("\\", "\\\\").replace("'", "''") + "'"


# ---- What stands in the camp (gameobject templates of their own, 770001 and up) ----------------
# (key: display, size, name). Displays are the game's own (GameObjectDisplayInfo.dbc).
PROPS = {
    "hourglass":   (7133, 0.065, "The Great Hourglass"),        # the Caverns of Time's, small
    "rug_green":   (6767, 1.4, "Rug"),
    "rug_red":     (6360, 1.6, "Rug"),
    "brazier":     (6660, 1.0, "Brazier"),                       # gold flame, the sands' colour
    "brazier_sm":  (7842, 1.0, "Brazier"),                       # the Scourge's own, from Malykriss's builders
    "lamp":        (9195, 1.0, "Brazier"),                       # a Scourge brazier burning orange (Dalaran's lampposts until build 117)
    "stall":       (7498, 0.75, "Stall"),                        # an open canopy
    "pavilion":    (7683, 0.6, "Pavilion"),
    "wagon":       (5392, 0.9, "Wagon"),
    "crate":       (31, 1.0, "Crate"),
    "crate_be":    (6792, 1.2, "Crate"),
    "crate_open":  (6791, 1.2, "Crate"),
    "barrel":      (6670, 1.0, "Barrel"),
    "table":       (6916, 1.1, "Table"),
    "table_big":   (6608, 1.0, "Table"),
    "bench":       (6979, 1.0, "Bench"),
    "weapon_rack": (130, 1.0, "Weapon Rack"),
    "weapon_crate": (6708, 1.0, "Weapon Crate"),
    "target":      (232, 0.8, "Archery Target"),
    "banner":      (8713, 1.0, "Ebon Blade Banner"),             # the Knights of the Ebon Blade keep the gates
    "campfire":    (6744, 1.6, "Campfire"),
    "cookpot":     (6888, 1.0, "Cooking Pot"),
    "bookshelf":   (137, 1.0, "Bookshelf"),
    "bookshelf_low": (187, 1.0, "Bookshelf"),
    "book":        (6475, 1.0, "Book"),
    "scroll_map":  (222, 1.0, "Map"),
    "map_table":   (6605, 0.5, "Map Table"),
    "orb":         (8124, 0.15, "Death's Gaze Orb"),            # an Eye of Acherus, its gaze turned on time
    "portal":      (4713, 0.12, "Door in Time"),
    # (new kinds go last: the others keep their entries)
    "rune_circle": (6679, 0.6, "Rune Circle"),                   # a Scourge rune circle, its crystals holding time instead
    "lightshaft":  (7317, 0.35, "Light"),
    "runeforge":   (8176, 2.03, "Runeforge"),                    # a death knight's runeforge that works (spell focus 1552)
    # (the Legion Remix cast's: Nedward's chair, and what each trader keeps by them)
    "barber_chair": (7896, 1.0, "Barbershop Chair"),             # a barbershop's chair that works (PROP_CHAIR)
    "anvil":       (166, 1.0, "Anvil"),
    "weapon_rack_sc": (7949, 0.8, "Weapon Rack"),                # the Scourge's own
    "gear_chest":  (8686, 1.0, "Scrap"),                         # a crate of Ulduar's gears
    "junk":        (7114, 1.2, "Scrap"),
    "platter":     (566, 0.6, "Roast Boar"),
    "hay":         (6145, 0.8, "Hay"),
    "trough":      (6148, 0.9, "Water Trough"),
    "gem_grinder": (7733, 1.0, "Gem Grinder"),
    "gems":        (7456, 0.6, "Uncut Gems"),
    "treasure":    (259, 0.9, "Coffer"),
    "armor_stand": (7738, 1.2, "Armor Stand"),
    "armor_stand_mail": (7827, 1.2, "Armor Stand"),
    "wardrobe":    (4031, 1.0, "Wardrobe"),
    "argent_banner": (7933, 1.0, "Argent Crusade Banner"),
}
PROP_ENTRY = {key: 770001 + i for i, key in enumerate(PROPS)}
# Props that do something when clicked: (game object type, script). The campfire calls Moratari over
# (RemixCampfire.cpp); a goober (10) is clickable.
PROP_USE = {"campfire": (10, "go_remix_campfire")}
# Spell focuses: (focus, distance), as the Shadow Vault's runeforge (191757) has them.
PROP_FOCUS = {"runeforge": (1552, 15)}
# Barber chairs (type 32): the chair's height, as the game's (190683) has it. A click sits the
# Timerunner in it and opens the barbershop, anywhere (GameObject::Use; the haircut is paid in gold).
PROP_CHAIR = {"barber_chair": 2}

# Where each thing stands: (prop, x, y, orientation, what it's for[, height above the floor: on a table])
PLACED = [
    # The heart: the great hourglass behind the echoes, a rug under Eternus and Moratari, braziers.
    ("hourglass", 6394.0, 1898.0, 0.0, "the heart"),
    ("rune_circle", 6394.0, 1898.0, 0.0, "the heart, under the hourglass"),
    ("lightshaft", 6394.0, 1898.0, 0.0, "the heart, on the hourglass"),
    ("rug_green", 6392.0, 1876.0, 0.0, "the heart, under Eternus and Moratari"),
    ("brazier", 6387.5, 1881.5, 0.0, "the heart"),
    ("brazier", 6400.5, 1881.5, 0.0, "the heart"),
    ("lamp", 6386.5, 1857.0, 0.0, "the heart, south"),
    ("lamp", 6405.0, 1888.0, 0.0, "the heart, north"),
    # The market lane, down the west edge: a stall for each trader, facing the lane.
    *[(kind, x, 1902.5, EAST, f"the market, {who}'s stall") for kind, x, who in (
        ("stall", 6380.0, "Alurmi"), ("stall", 6371.0, "Horos"), ("stall", 6362.0, "Domelius"),
        ("stall", 6353.0, "Arturos"), ("pavilion", 6344.0, "Aeonicus"), ("pavilion", 6335.5, "Durus"))],
    ("table", 6380.0, 1898.0, EAST, "Alurmi's counter"),
    ("weapon_crate", 6382.5, 1900.0, EAST, "Alurmi's heirlooms"),
    ("weapon_rack", 6377.0, 1901.5, EAST, "Alurmi's heirlooms"),
    ("crate_be", 6369.0, 1900.0, 0.4, "Horos's stall"),
    ("table", 6362.0, 1898.0, EAST, "Domelius's counter"),
    ("crate_open", 6359.5, 1900.0, 0.0, "Domelius's stall"),
    ("weapon_rack", 6355.5, 1901.5, EAST, "Arturos's stall"),
    ("weapon_rack", 6350.5, 1901.5, EAST, "Arturos's stall"),
    ("table_big", 6344.0, 1897.8, EAST, "Aeonicus's counter"),
    ("table_big", 6335.5, 1897.8, EAST, "Durus's counter"),
    ("banner", 6384.5, 1897.0, EAST, "the market's mouth"),
    ("lamp", 6357.5, 1896.0, 0.0, "the market lane"),
    # Across the lane: a trader's wagon, what the porters carry.
    ("wagon", 6362.0, 1883.0, NORTH, "the market lane"),
    ("crate", 6372.0, 1887.0, 0.3, "the market lane"),
    ("crate", 6372.5, 1885.6, 1.1, "the market lane"),
    ("barrel", 6371.0, 1886.2, 0.0, "the market lane"),
    ("barrel", 6349.0, 1887.0, 0.0, "the market lane"),
    ("crate_be", 6350.0, 1885.5, 0.7, "the market lane"),
    # The training yard, south-east: targets, racks, banners at its corners.
    ("target", 6343.0, 1826.0, NORTH, "the training yard"),
    ("target", 6343.0, 1832.0, NORTH, "the training yard"),
    ("weapon_rack", 6363.0, 1818.0, WEST, "the training yard"),
    ("weapon_rack", 6367.0, 1818.0, WEST, "the training yard"),
    ("banner", 6380.0, 1818.0, WEST, "the training yard"),
    ("banner", 6380.0, 1853.0, EAST, "the training yard"),
    ("banner", 6340.0, 1853.0, EAST, "the training yard"),
    ("brazier", 6348.0, 1850.5, 0.0, "the training yard, the shaman's fire"),
    ("brazier_sm", 6350.0, 1840.5, 0.0, "the training yard, the warlock's"),
    ("rug_red", 6376.0, 1850.5, 0.0, "the training yard, the priestess's"),
    ("runeforge", 6374.0, 1815.5, NORTH, "the training yard, the death knight's"),
    # The waystation, north-east: a door in time, Sa'at's map table.
    ("portal", 6407.5, 1835.0, facing(6407.5, 1835.0, 6394.0, 1866.0), "the waystation"),
    ("map_table", 6386.0, 1822.0, 0.0, "the waystation, Sa'at's"),
    ("lamp", 6394.0, 1820.0, 0.0, "the waystation"),
    # The chronicle corner, north-west (on the level ground; the rise beyond is the hill's): shelves,
    # books, an orb.
    ("bookshelf", 6417.0, 1893.0, SOUTH, "the chronicle corner"),
    ("bookshelf", 6417.0, 1896.5, SOUTH, "the chronicle corner"),
    ("bookshelf_low", 6417.0, 1899.5, SOUTH, "the chronicle corner"),
    ("table", 6412.5, 1895.0, 0.0, "the chronicle corner"),
    ("book", 6412.5, 1895.0, 0.5, "the chronicle corner"),
    ("scroll_map", 6412.8, 1894.6, 1.2, "the chronicle corner"),
    ("orb", 6413.0, 1903.5, 0.0, "the chronicle corner"),
    ("brazier_sm", 6408.0, 1891.0, 0.0, "the chronicle corner"),
    # The campfire, south: benches round a fire, the cook's pot, lanterns.
    ("campfire", 6349.0, 1866.0, 0.0, "the campfire"),
    ("bench", 6344.5, 1866.0, NORTH, "the campfire"),
    ("bench", 6353.5, 1866.0, NORTH, "the campfire"),
    ("cookpot", 6339.5, 1860.0, 0.0, "the campfire, the cook's"),
    ("barrel", 6337.5, 1858.0, 0.0, "the campfire"),
    ("crate", 6336.5, 1863.0, 0.6, "the campfire"),
    ("brazier_sm", 6357.0, 1873.0, 0.0, "the campfire"),
    ("brazier_sm", 6342.0, 1874.5, 0.0, "the campfire"),
    # (new things go last: the others keep their spawns)
    # The north row, along the north edge facing the heart: the heroic raids' pavilions, the
    # apparel stalls (Agos's arena wares, Unicus's ensembles, Larah's factions, Freddie's cloaks),
    # Nedward's barber's chair at its end.
    ("pavilion", 6431.5, 1888.0, SOUTH, "the north row, Pythagorus's"),
    ("table_big", 6426.8, 1888.0, SOUTH, "Pythagorus's counter"),
    ("pavilion", 6431.5, 1879.0, SOUTH, "the north row, Sacerdormu's"),
    ("table_big", 6426.8, 1879.0, SOUTH, "Sacerdormu's counter"),
    ("stall", 6431.5, 1870.0, SOUTH, "the north row, Agos's stall"),
    ("weapon_rack", 6433.0, 1867.5, SOUTH, "Agos's stall"),
    ("armor_stand_mail", 6433.0, 1872.5, SOUTH, "Agos's stall"),
    ("stall", 6431.5, 1861.0, SOUTH, "the north row, Unicus's stall"),
    ("armor_stand", 6433.0, 1858.5, SOUTH, "Unicus's ensembles"),
    ("armor_stand", 6433.0, 1863.5, SOUTH, "Unicus's ensembles"),
    ("stall", 6431.5, 1852.0, SOUTH, "the north row, Larah's stall"),
    ("argent_banner", 6433.0, 1854.5, SOUTH, "Larah's stall"),
    ("crate_open", 6433.0, 1849.5, 0.5, "Larah's stall"),
    ("stall", 6431.5, 1843.0, SOUTH, "the north row, Freddie's stall"),
    ("wardrobe", 6433.5, 1843.0, SOUTH, "Freddie's cloaks"),
    ("barber_chair", 6427.5, 1832.0, SOUTH, "the north row, Nedward's"),
    # The waystation's north-east corner: Hemet's mounts, by his proto-drake.
    ("hay", 6420.5, 1823.0, facing(6420.5, 1823.0, 6394.0, 1866.0), "the waystation, Hemet's"),
    ("trough", 6426.0, 1818.5, WEST, "the waystation, Hemet's"),
    # The training yard's east edge, facing into it: Jakkus's stall and glyphs, Momentus's weapons.
    ("stall", 6370.0, 1806.5, WEST, "the training yard, Jakkus's stall"),
    ("table", 6373.0, 1809.0, WEST, "Jakkus's glyphs"),
    ("book", 6373.0, 1809.0, 0.4, "Jakkus's glyphs", 1.0),
    ("weapon_rack_sc", 6383.0, 1805.0, WEST, "the training yard, Momentus's"),
    ("anvil", 6386.0, 1810.0, WEST, "the training yard, Momentus's"),
    # The campfire: Nostwin's snacks on the market side, Erus's scrap on the far side.
    ("table", 6353.0, 1880.0, 0.0, "the campfire, Nostwin's snacks"),
    ("platter", 6353.0, 1880.0, 0.3, "Nostwin's snacks", 1.0),
    ("crate_open", 6347.0, 1881.0, 0.6, "Nostwin's stuff"),
    ("gear_chest", 6325.5, 1863.0, facing(6325.5, 1863.0, 6349.0, 1866.0), "the campfire, Erus's scrap"),
    ("junk", 6325.0, 1868.5, 0.8, "Erus's scrap"),
    ("crate", 6323.5, 1866.0, 0.3, "Erus's scrap"),
    # The heart: Metros's desk, where a newcomer asks the way.
    ("table", 6402.5, 1866.0, NORTH, "the heart, Metros's desk"),
    ("book", 6402.5, 1866.3, 1.2, "Metros's desk", 1.0),
    ("scroll_map", 6402.4, 1865.6, 0.5, "Metros's desk", 1.0),
    # The chronicle corner: Lidamorrutu's gems, Lindormi's coffer of emblems.
    ("table", 6420.5, 1901.0, 0.0, "the chronicle corner, Lidamorrutu's"),
    ("gems", 6420.5, 1901.0, 0.5, "Lidamorrutu's", 1.0),
    ("gem_grinder", 6424.0, 1906.0, facing(6424.0, 1906.0, 6394.0, 1866.0), "Lidamorrutu's"),
    ("treasure", 6408.5, 1906.5, facing(6408.5, 1906.5, 6394.0, 1866.0), "the chronicle corner, Lindormi's"),
]

# ---- Who is in the camp -----------------------------------------------------------------------
# New people (770070 and up): entry: (name, subname, displays, type, flags, script, gossip text)
NOT_SELECTABLE = 0x02000000
PASSIVE = 770                                                         # not attackable, nor attacking
PEOPLE = {
    770070: ("Brannigan Holt", "Timerunner", [3343], 7, 0, "npc_remix_bazaar_life", 7702401),
    770071: ("Vaela Sunbrook", "Timerunner", [21271], 7, 0, "npc_remix_bazaar_life", 7702402),
    770072: ("Grukk Ironjaw", "Timerunner", [4560], 7, 0, "npc_remix_bazaar_life", 7702403),
    770073: ("Thaddeus Quill", "Timerunner", [21272], 7, 0, "npc_remix_bazaar_life", 7702404),
    770074: ("Tessaly Dawnwhisper", "Timerunner", [16685], 7, 0, "npc_remix_bazaar_life", 7702405),
    770075: ("Morrigan Ashe", "Timerunner", [1592], 7, 0, "npc_remix_bazaar_life", 7702406),
    770076: ("Zhar'ka", "Timerunner", [4068], 7, 0, "npc_remix_bazaar_life", 7702407),
    770077: ("Korvan Steelhide", "Timerunner", [21273], 7, 0, "npc_remix_bazaar_life", 7702408),
    770078: ("Marta Sandsworth", "Camp Cook", [27952], 7, 0, "npc_remix_bazaar_life", 7702409),
    770079: ("Sand Gnome Porter", None, [21027, 21028, 21029, 21030], 7, 0, "npc_remix_bazaar_life", 0),
    770080: ("Bazaar Warden", "Keepers of Time", [14887], 2, 0, "npc_remix_bazaar_life", 7702410),
    770081: ("Bronze Whelpling", None, [6292], 2, 0, "", 0),
    770082: ("Zephyr's Drake", None, [25852], 2, NOT_SELECTABLE, "", 0),
    770083: ("Time-Lost Proto-Drake", "Hemet's Collection", [28045], 2, NOT_SELECTABLE, "", 0),
    770084: ("Hyacinth Macaw", "Domelius's Companions", [6192], 1, 0, "", 0),
    770085: ("Mana Wyrmling", "Domelius's Companions", [19600], 10, 0, "", 0),
    770086: ("Orange Tabby Cat", "Domelius's Companions", [5554], 1, 0, "", 0),
}
TRAINING_DUMMY = 770087                                               # the game's dummy, renamed

# Where the story's own Bazaar people stand now (written into 0004/0009, kept here for the lines
# and the checks): guid: (who, x, y, orientation)
STORY_SPOTS = {
    7704011: ("Eternus", 6394.0, 1877.0, 4.71),
    7704012: ("Moratari", 6385.0, 1871.0, 5.78),
    7704013: ("Sylvanas", 6398.0, 1875.0, 3.60),
    7704014: ("Alleria", 6400.5, 1872.5, 3.40),
    7704015: ("Alurmi", 6380.0, 1900.5, EAST),
    7704016: ("Zephyr", 6402.5, 1838.0, facing(6402.5, 1838.0, 6394.0, 1866.0)),
    7704017: ("Sa'at", 6389.5, 1822.5, facing(6389.5, 1822.5, 6386.0, 1822.0)),
    7704018: ("the Chronologist", 6410.0, 1895.0, facing(6410.0, 1895.0, 6412.5, 1895.0)),
    7704019: ("Momentus", 6383.0, 1808.5, WEST),                       # the training yard's weaponmaster (in the chronicle corner before Malykriss)
    7704201: ("Horos", 6371.0, 1900.5, EAST),
    7704202: ("Domelius", 6362.0, 1900.5, EAST),
    7704203: ("Arturos", 6353.0, 1900.0, EAST),
    7704204: ("Aeonicus", 6344.0, 1900.5, EAST),
    7704205: ("Durus", 6335.5, 1900.5, EAST),
    # The rest of Legion Remix's cast (0009, 7704201 + their entry's n): the north row, ...
    7704206: ("Pythagorus", 6429.5, 1888.0, SOUTH),
    7704207: ("Sacerdormu", 6429.5, 1879.0, SOUTH),
    7704208: ("Agos the Silent", 6429.5, 1870.0, SOUTH),
    7704214: ("Unicus", 6429.5, 1861.0, SOUTH),
    7704209: ("Larah Treebender", 6429.5, 1852.0, SOUTH),
    7704210: ("Freddie Threads", 6429.5, 1843.0, SOUTH),
    7704219: ("Nedward", 6430.5, 1834.5, facing(6430.5, 1834.5, 6427.5, 1832.0)),
    # ... Hemet by the waystation, Jakkus at the training yard, Nostwin and Erus at the campfire,
    # Metros at the heart, Lidamorrutu and Lindormi in the chronicle corner
    7704212: ("Hemet Nesingwary XVII", 6415.0, 1818.5, facing(6415.0, 1818.5, 6394.0, 1866.0)),
    7704211: ("Grandmaster Jakkus", 6370.0, 1808.5, WEST),
    7704213: ("Nostwin", 6350.0, 1879.5, facing(6350.0, 1879.5, 6349.0, 1866.0)),
    7704217: ("Erus", 6328.0, 1866.0, NORTH),
    7704218: ("Pageturner Metros", 6405.0, 1866.0, facing(6405.0, 1866.0, 6394.0, 1866.0)),
    7704215: ("Lidamorrutu", 6422.0, 1903.0, facing(6422.0, 1903.0, 6394.0, 1866.0)),
    7704216: ("Lindormi", 6409.5, 1903.0, facing(6409.5, 1903.0, 6394.0, 1866.0)),
    7704300: ("Andormu", 6395.5, 1878.0, 4.71),
    7704301: ("Nozari", 6392.5, 1878.0, 4.71),
}
# The instructors (770101 to 770111, guid 7704020 + n): (x, y, orientation, stand state, emote state)
DUMMIES = [(6368.0, 1836.0), (6360.0, 1836.0), (6352.0, 1836.0)]
INSTRUCTORS = {
    770101: (6371.5, 1838.5, facing(6371.5, 1838.5, 6368.0, 1836.0), 0, STATE_READY1H),      # warrior, at a dummy
    770102: (6378.0, 1830.0, facing(6378.0, 1830.0, 6378.0, 1825.0), 0, 0),                  # the paladins, talking
    770103: (6378.0, 1825.0, facing(6378.0, 1825.0, 6378.0, 1830.0), 0, 0),
    770104: (6355.0, 1829.0, facing(6355.0, 1829.0, 6343.0, 1829.0), 0, STATE_BOW),          # hunter, at the targets
    770105: (6374.5, 1843.5, facing(6374.5, 1843.5, 6371.5, 1838.5), 0, 0),                  # rogue, watching the warrior
    770106: (6376.0, 1850.5, NORTH, KNEEL, 0),                                              # priestess, kneeling
    770107: (6365.0, 1819.8, WEST + math.pi, 0, STATE_WORK),                                # death knight, at the racks
    770108: (6348.0, 1848.0, facing(6348.0, 1848.0, 6348.0, 1850.5), 0, 0),                  # shaman, at her fire
    770109: (6360.0, 1840.5, facing(6360.0, 1840.5, 6360.0, 1836.0), 0, STATE_SPELL),        # mage, at a dummy
    770110: (6352.0, 1840.5, facing(6352.0, 1840.5, 6352.0, 1836.0), 0, 0),                  # warlock, at a dummy
    770111: (6343.5, 1846.0, facing(6343.5, 1846.0, 6348.0, 1848.0), SIT, 0),                # druid, sitting
}

# New spawns, 7704500 and up: (guid, entry, x, y, orientation, stand state, emote state, wander)
SPAWNS = [
    # The campfire.
    (7704501, 770070, 6349.0, 1862.3, facing(6349.0, 1862.3, 6349.0, 1866.0), SIT, 0, 0),
    (7704502, 770071, 6348.0, 1869.7, facing(6348.0, 1869.7, 6349.0, 1866.0), SIT, 0, 0),
    (7704503, 770072, 6354.5, 1861.8, facing(6354.5, 1861.8, 6349.0, 1866.0), 0, 0, 0),
    (7704504, 770073, 6351.2, 1869.3, facing(6351.2, 1869.3, 6349.0, 1866.0), SIT, 0, 0),
    (7704505, 770074, 6356.5, 1875.5, facing(6356.5, 1875.5, 6394.0, 1898.0), 0, 0, 0),
    (7704506, 770075, 6341.0, 1872.0, facing(6341.0, 1872.0, 6339.5, 1875.5), 0, STATE_TALK, 0),
    (7704507, 770076, 6339.5, 1875.5, facing(6339.5, 1875.5, 6341.0, 1872.0), 0, 0, 0),
    (7704508, 770077, 6342.5, 1859.0, facing(6342.5, 1859.0, 6339.5, 1860.0), 0, STATE_EAT, 0),
    (7704509, 770078, 6338.0, 1861.0, facing(6338.0, 1861.0, 6339.5, 1860.0), 0, STATE_WORK, 0),
    # The market lane's critters, Domelius's companions.
    (7704510, 770084, 6361.0, 1896.0, 0.0, 0, 0, 3.0),
    (7704511, 770085, 6363.5, 1895.0, 0.0, 0, 0, 3.0),
    (7704512, 770086, 6360.0, 1894.0, 0.0, 0, 0, 3.0),
    # Hemet's proto-drake, beside him (Horos's, behind his stall, before Malykriss); Zephyr's drake, resting.
    (7704513, 770083, 6421.0, 1813.0, facing(6421.0, 1813.0, 6394.0, 1866.0), 0, 0, 0),
    (7704514, 770082, 6403.5, 1823.0, facing(6403.5, 1823.0, 6398.0, 1831.0), 0, 0, 0),
    # Whelplings underfoot.
    (7704515, 770081, 6387.0, 1894.0, 0.0, 0, 0, 5.0),
    (7704516, 770081, 6375.0, 1890.0, 0.0, 0, 0, 5.0),
    (7704517, 770081, 6358.0, 1858.0, 0.0, 0, 0, 5.0),
    # The training yard's dummies.
    *[(7704520 + i, TRAINING_DUMMY, x, y, NORTH, 0, 0, 0) for i, (x, y) in enumerate(DUMMIES)],
]

# Walkers: (guid, entry, [(x, y, pause ms), ...]) on a loop (waypoint_data, path id = guid).
WALKERS = [
    (7704530, 770079, [(6382.0, 1894.0, 4000), (6366.0, 1893.0, 0), (6340.0, 1893.0, 5000), (6340.0, 1888.0, 0),
                       (6366.0, 1889.0, 3000), (6382.0, 1890.0, 0)]),
    (7704531, 770079, [(6359.0, 1855.0, 3000), (6366.0, 1850.0, 0), (6378.0, 1857.0, 0), (6384.0, 1862.0, 4000),
                       (6370.0, 1866.0, 0), (6361.0, 1870.0, 0)]),
    (7704532, 770079, [(6392.0, 1836.0, 5000), (6383.5, 1850.0, 0), (6380.0, 1884.0, 4000), (6383.5, 1850.0, 0)]),
    # (the wardens are dragonspawn, two yards round: clear of the training yard's archery targets, and
    # of its racks, banner and lamp along y 964)
    (7704533, 770080, [(6339.0, 1818.0, 2000), (6338.0, 1850.0, 0), (6332.0, 1857.0, 0), (6332.0, 1878.0, 0), (6340.0, 1886.0, 0),
                       (6340.0, 1894.0, 3000), (6340.0, 1886.0, 0), (6332.0, 1878.0, 0), (6332.0, 1857.0, 0), (6338.0, 1850.0, 0)]),
    (7704534, 770080, [(6344.0, 1814.5, 2000), (6370.0, 1814.5, 0), (6402.0, 1814.5, 2000), (6370.0, 1814.5, 0)]),
]

# ---- What they say ------------------------------------------------------------------------------
# guid: [(text, emote, reply guid, reply, reply emote)]
LINES = {
    # The story's people.
    7704011: [("Every stall in this camp holds something history threw away. I only kept it.", TALK, 0, "", 0),
              ("Do not let the sands hurry you, champion. Here, at least, there is time.", TALK, 0, "", 0)],
    7704012: [("Mind the hourglass. It runs in every direction at once, and it hates being bumped.", POINT, 0, "", 0),
              ("If this hall looks familiar, it should. We cleared the Scourge out of it when we started tidying the timeline. It is ours now, every rib of it.", TALK, 0, "", 0),
              ("Every Timerunner who wakes here asks me the same thing first. The answer is no: you cannot go back yet.", TALK, 0, "", 0)],
    7704015: [("Heirlooms! Gear that grows with you, for Timerunners with no time to shop twice.", EXCLAIM, 0, "", 0),
              ("Bronze only. Gold has no sense of history.", TALK, 0, "", 0),
              ("Moratari! Someone tried to pay me in Stratholme coin again.", TALK, 7704012, "Did you take it?", QUESTION)],
    7704016: [("Roads fold best when nobody watches them do it.", TALK, 0, "", 0),
              ("Easy, girl. They are only Timerunners. They are always in a hurry.", TALK, 0, "", 0)],
    7704017: [("Every dungeon in Northrend, waiting at the hour you are ready for it. Ask, and I will tell you which.", TALK, 0, "", 0)],
    7704018: [("Valiance Keep, the first day... no, this page is smudged. Someone keeps changing things.", QUESTION, 0, "", 0),
              ("Every record says the same war. That is the comforting part. It is also the frightening part.", TALK, 0, "", 0)],
    7704019: [("There are few problems that a little heat and a hammer cannot solve.", TALK, 0, "", 0),
              ("We forge our own futures.", 0, 0, "", 0),
              ("Grandmaster, that rib up there was not so low yesterday.", POINT, 7704211, "Nonsense. The sky is barely even falling.", TALK)],
    7704013: [("Stop watching the hourglass, sister. It will not run out.", TALK, 7704014,
               "It already has, in a hundred places. You just cannot hear it.", TALK),
              ("This year smells of plague and ice. I had forgotten. I had made myself forget.", 0, 0, "", 0)],
    7704014: [("When the bronze came for me, the Void was at the gates of Quel'Thalas. I hope they are still holding.", TALK,
               7704013, "They will hold. Our people always hold, until the moment they do not.", 0),
              ("If the Timerunner asks, I was watching the hourglass. Not the door.", TALK, 7704013, "Of course you were, sister.", 0)],
    7704300: [("The record is quieter today.", TALK, 7704301, "Quieter is not the same as whole, Andormu.", TALK)],
    # The traders, Legion Remix's Bazaar cast (their own words where the game has them; a line that
    # begins with %s is an emote).
    7704201: [("We will have everything in time.", TALK, 0, "", 0),
              ("Toys, trinkets, a music box that plays a song nobody has written yet. Every curiosity Northrend ever lost, I found.", EXCLAIM, 0, "", 0)],
    7704202: [("I am late. So very, very late.", QUESTION, 0, "", 0),
              ("Perhaps I should get a clock.", TALK, 0, "", 0),
              ("Careful, that whelp bites. No, the other one.", POINT, 0, "", 0)],
    7704203: [("Good to see you, champion! How fare your hunts?", WAVE, 0, "", 0),
              ("Every blade on this rack came out of a dungeon in a braver hand than mine. It can go back in with yours.", TALK, 0, "", 0)],
    7704204: [("Oh, a Timerunner! I bet you've got stories to tell.", EXCLAIM, 0, "", 0),
              ("Ten champions against the Scourge, again and again. Their spoils look better on you than in a tomb.", TALK, 0, "", 0),
              ("Durus! Which is heavier, do you think: a shield, or a promise?", QUESTION, 7704205,
               "Patience wins wars. But if you ask one more question, I will swallow my shield.", 0)],
    7704205: [("Keep your shield up, and patience will see you through any battle.", TALK, 0, "", 0),
              ("Twenty-five against the Lich King's halls. This is what they carried home. The ones who came home.", TALK, 0, "", 0)],
    7704206: [("Offers? My wares are full price!", NO, 0, "", 0),
              ("Of course I can lift it. It's a sword.", LAUGH, 0, "", 0)],
    7704207: [("Why choose between substance and style when you can have both?", TALK, 0, "", 0),
              ("%s glances over at Pythagorus and sighs.", 0, 0, "", 0)],
    7704208: [("%s gives a passerby a knowing nod.", YES, 0, "", 0),
              ("%s nods silently, closing their eyes to show their sincerity.", YES, 0, "", 0)],
    7704214: [("Styles change all the time, but nothing stays out of style forever.", TALK, 0, "", 0)],
    7704209: [("Oh honey, you need a new look.", TALK, 0, "", 0),
              ("Ooh! I've always wanted to dress up like a baddie.", EXCLAIM, 7704214, "Curious.", 0)],
    7704210: [("Hey there, kitty-cat, you look like you could use some threads.", WAVE, 0, "", 0),
              ("Everybody who's anybody knows somebody who knows Freddie Threads.", TALK, 0, "", 0)],
    7704219: [("Sit, sit! A little off the top, a little out of the timeline.", TALK, 0, "", 0),
              ("Hold still. The last fellow fidgeted and left with next Tuesday's beard.", LAUGH, 0, "", 0)],
    7704212: [("The name's Hemet Nesingwary, tha seventeenth.", TALK, 0, "", 0),
              ("Surely you've 'eard of my esteemed and grand familial lineage.", TALK, 0, "", 0),
              ("Them death knights keep a fine 'orse. Bit bony.", LAUGH, 0, "", 0)],
    7704211: [("I remember my training like it was yesterday. For a dragon, it very nearly was.", LAUGH, 0, "", 0)],
    7704213: [("%s munches on something delicious.", EAT, 0, "", 0),
              ("Hi! Can I interest you in a fancy paper or this jar of bees I found?", TALK, 0, "", 0),
              ("Erus! Can this go in the scrap pile? I already ate the good part.", QUESTION, 7704217,
               "Snacks are for snacking, just as scraps are for scrapping. No exceptions.", NO)],
    7704217: [("Erus scrap junk for you.", TALK, 0, "", 0),
              ("Everything has its time.", 0, 0, "", 0)],
    7704218: [("Need something? I've got theories to sort through.", TALK, 0, "", 0),
              ("Day in, day out, count count count.", 0, 0, "", 0)],
    7704215: [("If you're in a rush, I can pluck a gem you've yet to find from a different timeline. It just takes a little Bronze.", TALK, 0, "", 0)],
    7704216: [("Tales of adventure are the best! Dark dungeons, terrifying monsters, shiny treasures... I want to hear all about them!", EXCLAIM, 0, "", 0),
              ("Oh wow, you're not dead! That's so cool!", CHEER, 0, "", 0),
              ("Lidamorrutu! Tell me a story. A dark one, with treasure in it!", EXCLAIM, 7704215, "Hmph.", 0)],
    # The instructors.
    7704021: [("Again. Shield up. No, the other shield.", TALK, 0, "", 0)],
    7704025: [("You telegraph every swing, orc.", TALK, 7704021, "And you hide behind every tent. We all have our gifts.", LAUGH)],
    7704022: [("The Light sounds the same in every year.", TALK, 7704023, "Says a man who has never heard it sung in Silvermoon.", TALK)],
    7704024: [("Patience. The beast comes to the one who waits.", 0, 0, "", 0)],
    7704026: [("Breathe. The Light will wait for you. It always has.", 0, 0, "", 0)],
    7704027: [("I remember dying. It gets easier to talk about. Not much easier.", TALK, 0, "", 0)],
    7704028: [("The winds here blow from tomorrow. Listen, and you will hear rain that has not fallen yet.", TALK, 0, "", 0)],
    7704029: [("If you can see the fireball coming, you cast it too slowly.", TALK, 0, "", 0)],
    7704030: [("Do not feed the imp. Whatever it tells you.", NO, 0, "", 0)],
    7704031: [("Even on stone, things grow. Slowly. Sideways, sometimes.", 0, 0, "", 0)],
    # The other Timerunners, veterans of this war, each from their own hour after it.
    7704501: [("Last thing I remember, I was buying a round in Ironforge to toast the Lich King's fall.",
               TALK, 7704502, "Then we had better be home before it goes flat.", 0)],
    7704502: [("Third time through the Borean Tundra this week. The penguins are starting to recognize me.", LAUGH,
               7704501, "Those are not penguins taking notes, Vaela. Those are bronze dragons.", TALK)],
    7704503: [("Gnome. Why is my bag lighter than when I came?", QUESTION, 7704504, "Time dilation! Or I borrowed your rations. One of the two.", TALK),
              ("I fought my way into Ulduar. Next to what was under it, the Scourge is almost polite.", TALK, 7704504, "Almost. They still bite.", 0)],
    7704505: [("The Sunwell burns again in this year. In mine too, and still half of Silvermoon lies in ruins. Some wounds take longer than a war.", 0, 0, "", 0)],
    7704506: [("They keep asking if I am from this year. I am barely from this century.", TALK, 7704507,
               "Ya worry too much, mon. Time be a river. We just be fishin'.", LAUGH)],
    7704507: [("Vol'jin be chieftain of de Darkspear in dis year, and in mine. Some tings time don't touch.", TALK, 7704506,
               "Do not say that too loud. The dragons get twitchy.", 0)],
    7704508: [("Best stew in any century. Do not tell the cook I said so.", EAT, 7704509, "I heard that, Steelhide. Second bowl is still Bronze.", LAUGH)],
    7704509: [("Stew's on! Sholazar mushrooms, and something the gnome swears is a vegetable.", EXCLAIM, 0, "", 0),
              ("Eat while you can. The Scourge does not stop for supper.", TALK, 0, "", 0)],
    # Those on their rounds.
    7704530: [("Mind your feet! Crates of yesterday coming through!", EXCLAIM, 0, "", 0)],
    7704531: [("Who orders forty hourglasses? Again?", QUESTION, 0, "", 0)],
    7704532: [("If this crate is from tomorrow, why is it already late?", TALK, 0, "", 0)],
    7704533: [("The Bazaar keeps its own peace, in every year.", 0, 0, "", 0)],
    7704534: [("No fighting, no thieving, and no meeting your own past self. Those are the rules.", 0, 0, "", 0)],
}

# What the Timerunners and the camp's people say when spoken to (npc_text, gossip_menu).
GOSSIP = {
    7702401: "Brannigan Holt, Stormwind. Or I was, a few years from now.$B$BYou look like you woke up the same way I did. Get your strength back, then get out there. The war is not going to wait for us twice.",
    7702402: "Shh. Listen to that fire. In my time I cannot sit by one without thinking of the Wrathgate.$B$BI know. I know what Eternus wants. I have not decided what I think about it yet. Have you?",
    7702403: "Grukk Ironjaw, of the Frostwolves. I have killed centaur and quilboar and once, by accident, a very large goat.$B$BThe Scourge I know: I followed it all the way to the Frozen Throne. It is good to fight something I already understand.",
    7702404: "Thaddeus Quill, engineer, Timerunner, and the only gnome in this camp who read the warning label on the hourglass.$B$BIt says do not shake. I shook it. That is how I got here, I think.",
    7702405: "The Sunwell is burning again. I can feel it from here, even in this year. It was dark for so long.$B$BWhatever Eternus offers you, $c, ask her what it costs. It always costs something.",
    7702406: "Morrigan Ashe. Forsaken, priestess, and very tired of being asked if I am from around here.$B$BI died in the Third War. I would rather not watch this one do it to anyone else. That is why I listened to Eternus. I am still listening.",
    7702407: "Zhar'ka of the Darkspear. De spirits be very confused in dis place, mon. Dey keep askin' me what year it be.$B$BI tell dem: all of dem.",
    7702408: "Korvan Steelhide, Ironforge. If you are looking for the stew, it is behind me, and it is mine.$B$B...Fine. There is enough for two.",
    7702409: "Sit, eat, Timerunner. Whatever year you came from, you came hungry. They all do.",
    7702410: "The Keepers set wardens on the Bazaar while Timerunners come and go. Keep the peace, and the peace will keep you.",
}


def main():
    out = []
    w = out.append
    w("""-- The Infinite Bazaar's camp (tools/bazaar.py writes this file: edit that and run it again). Around
-- the story's people at its heart, districts a Timerunner can read at a glance: the market lane along
-- the west edge (a stall for each Bronze trader), the north row along the north edge (the heroic
-- raids' pavilions, the apparel stalls, Nedward's barber's chair), the training yard to the
-- south-east (the instructors at work, dummies and targets; Jakkus and Momentus at its edge), the
-- waystation to the north-east (Zephyr, her drake, a door in time, Sa'at's map table, Hemet's
-- mounts), the chronicle corner to the north-west (Lidamorrutu's gems, Lindormi's emblems), the
-- campfire to the south (other Timerunners, veterans of this war from their own hours after it, a
-- cook, Nostwin's snacks, Erus's scrap), and porters, wardens and whelps on their rounds. Who says
-- what while a Timerunner is about is remix_bazaar_line (src/RemixBazaar.cpp). Heights are the
-- floor's (data/bazaar_ground.tsv). The story's own people and the Bazaar's cast stand where
-- wrath_remix_world_0004_spawns.sql, 0009 and 0018 place them.
""")
    # Props.
    lo, hi = 770001, 770001 + len(PROPS) - 1
    w(f"DELETE FROM `gameobject_template` WHERE `entry` BETWEEN 770001 AND 770099;")
    w("INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `IconName`, `castBarCaption`, `unk1`, `size`, `Data0`, `Data1`, `AIName`, `ScriptName`, `VerifiedBuild`) VALUES")
    def kind(k):
        """(type, Data0, Data1) of a prop's template."""
        if k in PROP_CHAIR:
            return 32, PROP_CHAIR[k], 0
        if k in PROP_FOCUS:
            return (8,) + PROP_FOCUS[k]
        return PROP_USE.get(k, (5, ''))[0], 0, 0
    w(",\n".join(f"({PROP_ENTRY[k]}, {kind(k)[0]}, {d}, {sql_text(n)}, '', '', '', {s}, "
                 f"{kind(k)[1]}, {kind(k)[2]}, '', "
                 f"{sql_text(PROP_USE.get(k, (5, ''))[1])}, 0)" for k, (d, s, n) in PROPS.items()) + ";")
    w("")
    w("DELETE FROM `gameobject` WHERE `guid` BETWEEN 7705001 AND 7705299;")
    w("INSERT INTO `gameobject` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`,")
    w("  `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`, `animprogress`, `state`, `ScriptName`, `VerifiedBuild`, `Comment`) VALUES")
    rows = []
    assert len(PLACED) <= 299, "the camp's things are spawns 7705001 to 7705299"
    for i, (key, x, y, o, what, *up) in enumerate(PLACED):
        z = z_at(x, y) + (up[0] if up else 0.0)
        rows.append(f"({7705001 + i}, {PROP_ENTRY[key]}, {MAP}, {ZONE}, {AREA}, 1, 1, {x:.2f}, {y:.2f}, {z:.2f}, {o:.4f}, "
                    f"0, 0, {math.sin(o / 2):.6f}, {math.cos(o / 2):.6f}, 300, 100, 1, '', 0, {sql_text('Wrath Remix: ' + PROPS[key][2] + ', ' + what)})")
    w(",\n".join(rows) + ";")
    w("")

    # People.
    w("DELETE FROM `creature_template` WHERE `entry` BETWEEN 770070 AND 770099;")
    w("DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN 770070 AND 770099;")
    w("INSERT INTO `creature_template` (`entry`, `name`, `subname`, `gossip_menu_id`, `minlevel`, `maxlevel`, `exp`, `faction`, `npcflag`,")
    w("  `speed_walk`, `speed_run`, `rank`, `unit_class`, `unit_flags`, `unit_flags2`, `type`, `flags_extra`,")
    w("  `HealthModifier`, `DamageModifier`, `BaseAttackTime`, `RegenHealth`, `ScriptName`) VALUES")
    rows = []
    for entry, (name, sub, displays, ctype, flags, script, text) in PEOPLE.items():
        menu = text - 7702400 + 77040 if text else 0
        rows.append(f"({entry}, {sql_text(name)}, {sql_text(sub) if sub else 'NULL'}, {menu}, 80, 80, 2, 35, {1 if text else 0}, "
                    f"1, 1.14286, 0, 1, {PASSIVE | flags}, 2048, {ctype}, 2, 10, 1, 2000, 1, {sql_text(script)})")
    w(",\n".join(rows) + ";")
    w("INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) VALUES")
    rows = []
    for entry, (name, sub, displays, *_rest) in PEOPLE.items():
        for i, d in enumerate(displays):
            rows.append(f"({entry}, {i}, {d}, 1, 1, 0)")
    w(",\n".join(rows) + ";")
    w("""
-- The training yard's dummies: the game's own, under a plain name, at a Timerunner's first level,
-- and the class lessons' (npc_remix_dummy, src/RemixLessons.cpp).
DROP TEMPORARY TABLE IF EXISTS `remix_dummy`;
CREATE TEMPORARY TABLE `remix_dummy` SELECT * FROM `creature_template` WHERE `entry` = 31146;
UPDATE `remix_dummy` SET `entry` = 770087, `name` = 'Training Dummy', `subname` = NULL, `minlevel` = 10, `maxlevel` = 10, `rank` = 0, `ScriptName` = 'npc_remix_dummy';
INSERT INTO `creature_template` SELECT * FROM `remix_dummy`;
DROP TEMPORARY TABLE `remix_dummy`;
INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`)
SELECT 770087, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, 0 FROM `creature_template_model` WHERE `CreatureID` = 31146;
""")

    # What they say when spoken to.
    w("DELETE FROM `npc_text` WHERE `ID` BETWEEN 7702401 AND 7702499;")
    w("INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES")
    w(",\n".join(f"({i}, {sql_text(t)}, {sql_text(t)}, 1)" for i, t in GOSSIP.items()) + ";")
    w("DELETE FROM `gossip_menu` WHERE `MenuID` BETWEEN 77040 AND 77099;")
    w("INSERT INTO `gossip_menu` (`MenuID`, `TextID`) VALUES")
    w(",\n".join(f"({i - 7702400 + 77040}, {i})" for i in GOSSIP) + ";")
    w("")

    # Where they stand, and what they do.
    w("DELETE FROM `creature` WHERE `guid` BETWEEN 7704500 AND 7704599;")
    w("INSERT INTO `creature` (`guid`, `id`, `map`, `spawnMask`, `phaseMask`, `equipment_id`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES")
    rows = []
    for guid, entry, x, y, o, stand, emote, wander in SPAWNS:
        name = PEOPLE[entry][0] if entry in PEOPLE else "Training Dummy"
        rows.append(f"({guid}, {entry}, {MAP}, 1, 1, 0, {x:.2f}, {y:.2f}, {z_at(x, y) + 0.1:.2f}, {o:.4f}, 60, {wander:.1f}, {1 if wander else 0}, "
                    f"{sql_text('Wrath Remix: ' + name + ', Bazaar')})")
    for guid, entry, points in WALKERS:
        x, y, _ = points[0]
        rows.append(f"({guid}, {entry}, {MAP}, 1, 1, 0, {x:.2f}, {y:.2f}, {z_at(x, y) + 0.1:.2f}, 0, 60, 0, 2, "
                    f"{sql_text('Wrath Remix: ' + PEOPLE[entry][0] + ', Bazaar, on rounds')})")
    w(",\n".join(rows) + ";")
    w("DELETE FROM `creature_addon` WHERE `guid` BETWEEN 7704500 AND 7704599 OR `guid` BETWEEN 7704021 AND 7704031;")
    w("INSERT INTO `creature_addon` (`guid`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) VALUES")
    rows = []
    for guid, entry, x, y, o, stand, emote, wander in SPAWNS:
        if stand or emote:
            rows.append(f"({guid}, 0, 0, {stand}, 1, {emote}, 0, '')")
    for guid, entry, points in WALKERS:
        rows.append(f"({guid}, {guid}, 0, 0, 1, 0, 0, '')")
    for entry, (x, y, o, stand, emote) in INSTRUCTORS.items():
        if stand or emote:
            rows.append(f"({7704020 + entry - 770100}, 0, 0, {stand}, 1, {emote}, 0, '')")
    w(",\n".join(rows) + ";")
    w("DELETE FROM `waypoint_data` WHERE `id` BETWEEN 7704500 AND 7704599;")
    w("INSERT INTO `waypoint_data` (`id`, `point`, `position_x`, `position_y`, `position_z`, `orientation`, `delay`, `move_type`) VALUES")
    rows = []
    for guid, entry, points in WALKERS:
        for n, (x, y, pause) in enumerate(points, start=1):
            rows.append(f"({guid}, {n}, {x:.2f}, {y:.2f}, {z_at(x, y) + 0.1:.2f}, NULL, {pause}, 0)")
    w(",\n".join(rows) + ";")
    w("")

    # The lines.
    w("""CREATE TABLE IF NOT EXISTS `remix_bazaar_line` (
  `guid` INT UNSIGNED NOT NULL,
  `line` TINYINT UNSIGNED NOT NULL DEFAULT 0,
  `text` VARCHAR(512) NOT NULL,
  `emote` INT UNSIGNED NOT NULL DEFAULT 0,
  `reply_guid` INT UNSIGNED NOT NULL DEFAULT 0,
  `reply` VARCHAR(512) NOT NULL DEFAULT '',
  `reply_emote` INT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`guid`, `line`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
DELETE FROM `remix_bazaar_line` WHERE `guid` < 7706000;  -- (Malykriss's own, 7706000 and up, are wrath_remix_world_0030_malykriss.sql's)""")
    w("INSERT INTO `remix_bazaar_line` (`guid`, `line`, `text`, `emote`, `reply_guid`, `reply`, `reply_emote`) VALUES")
    rows = []
    for guid, lines in LINES.items():
        for n, (text, emote, reply_guid, reply, reply_emote) in enumerate(lines):
            rows.append(f"({guid}, {n}, {sql_text(text)}, {emote}, {reply_guid}, {sql_text(reply)}, {reply_emote})")
    w(",\n".join(rows) + ";")

    with open(OUT, "w") as f:
        f.write("\n".join(out) + "\n")
    print(f"{len(PLACED)} things placed, {len(SPAWNS) + len(WALKERS)} people, {sum(len(v) for v in LINES.values())} lines")


if __name__ == "__main__":
    main()
