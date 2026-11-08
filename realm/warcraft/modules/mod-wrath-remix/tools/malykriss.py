#!/usr/bin/env python3
"""Writes Malykriss: The Vile Hold, the Infinite Bazaar's home: data/sql/remix/world/wrath_remix_world_0030_malykriss.sql.

    python3 tools/malykriss.py

Malykriss is the necropolis the Lich King began in Icecrown to replace Acherus and never finished: a
crater of saronite under the ribs of a necropolis with no skin, its walkways a hundred and twenty
yards up. The Bazaar stands on the crater's level floor (tools/bazaar.py). In Remix's world the
Scourge's garrison is gone (the Bazaar's dragons took care of it when they started cleaning up the
timeline, as Moratari tells a Timerunner who wakes there) (its spawns and the game's quests that need them: the Shadow Vault's
Malykriss quests), and the hall belongs to the Bazaar's allies:

  - the Knights of the Ebon Blade: their quarter in the east field (their commander, duelists,
    deathchargers, a runeforge), wardens at the west gate, runesmiths at the Scourge's Runeworks, a
    patrol on the floor and sentinels on the walkways and at the Icy Lookout;
  - the last free nerubians of Azjol-Nerub, who were building in saronite before the Scourge stole
    the craft from them: their hall in the north-west lobe by the Blood Forge (their warlord, an
    elder, an architect, silkweavers, eggs, burrows, spiderlings), a warden walking the floor, one
    on the north walkway, one at the Altar of Sacrifice, and skyguards circling the necropolis;
  - and the time-magic at the heart: the hourglass's sands heard and glowing, two sandshapers
    channelling bronze into it, a time rift above it pouring gold, frost spheres circling it
    (src/RemixMalykriss.cpp moves and casts them).

Those with something to say say it as the Bazaar's people do (remix_bazaar_line, src/RemixBazaar.cpp;
this file's spawns are 7706000 and up). Heights are the floor's: data/bazaar_ground.tsv (the camp)
and data/malykriss_ground.tsv (everywhere else here, both levels), `.remix ground` on the realm.
Positions are the world's (x north, y west).
"""
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "sql", "remix", "world", "wrath_remix_world_0030_malykriss.sql")
GROUNDS = [os.path.join(HERE, "..", "data", name) for name in ("bazaar_ground.tsv", "malykriss_ground.tsv")]

MAP, ZONE, AREA = 571, 210, 4520
EAST, NORTH, WEST, SOUTH = 3 * math.pi / 2, 0.0, math.pi / 2, math.pi
TALK, BOW, EXCLAIM, QUESTION, LAUGH, POINT, SALUTE, YES, NO = 1, 2, 5, 6, 11, 25, 66, 273, 274
STATE_WORK, STATE_READY1H, STATE_SPELL = 173, 333, 474
KNEEL = 8
HOURGLASS = (6394.0, 1898.0)                 # tools/bazaar.py's
NECROPOLIS = (6377.0, 1805.0)                # the frame's middle
CITADEL = (6137.0, 2404.0)                   # Icecrown Citadel


def load_ground():
    ground = {}
    for path in GROUNDS:
        for line in open(path):
            if line.startswith("#") or not line.strip():
                continue
            x, y, z = line.split()
            ground.setdefault((int(x), int(y)), []).append(float(z))
    return ground


GROUND_Z = load_ground()


def z_at(x, y, near=508.6):
    """The floor under (x, y) nearest the height `near` (Malykriss has two levels): the closest
    reading within two yards."""
    best, best_d = None, 99.0
    for gx in range(int(x) - 2, int(x) + 3):
        for gy in range(int(y) - 2, int(y) + 3):
            for z in GROUND_Z.get((gx, gy), ()):
                if abs(z - near) > 12:
                    continue
                d = math.hypot(gx - x, gy - y) + abs(z - near) * 0.01
                if d < best_d:
                    best, best_d = z, d
    if best is None:
        raise SystemExit(f"no floor reading near {x} {y} at {near}: survey there first (data/malykriss_ground.tsv)")
    return best


def facing(x, y, tx, ty):
    return math.atan2(ty - y, tx - x) % (2 * math.pi)


def sql_text(text):
    return "'" + text.replace("\\", "\\\\").replace("'", "''") + "'"


# ---- The Scourge's garrison, gone from Remix's world ---------------------------------------------
# Everyone of these in Malykriss (all of them in area 4520; the box is the area's). The Arctic Cloud
# (24879) stays: it is weather.
GARRISON = {
    30894: "Lithe Stalker", 31323: "Lithe Stalker", 30920: "Lumbering Atrocity", 31226: "Lumbering Atrocity",
    30921: "Skeletal Runesmith", 31321: "Skeletal Runesmith", 30922: "Umbral Brute", 31320: "Umbral Brute",
    30957: "Death Knight Initiate", 30958: "Death Knight Initiate", 31326: "Death Knight Initiate",
    31327: "Death Knight Initiate", 31042: "Death Knight Adept", 31325: "Death Knight Adept",
    31012: "Iceskin Sentry", 31324: "Iceskin Sentry", 31075: "Scourge Bomb", 31255: "Saronite Shaper",
    31322: "Saronite Shaper", 30953: "Baelok", 31159: "Baelok", 30954: "Rokir", 31160: "Rokir",
    30956: "Sapph", 31161: "Sapph", 31163: "Icefury", 31224: "Icefury", 31221: "Bloodsunder",
    31223: "Bloodsunder", 31225: "Plaguehoof", 31747: "Necrotic Webspinner", 31049: "Geist Return Bunny",
    31064: "Malykriss Icy Lookout Bunny", 31065: "Malykriss Altar of Sacrifice Bunny",
    31066: "Malykriss Runeworks Bunny", 31068: "Malykriss Blood Forge Bunny",
}
BOX = (5950, 6700, 1480, 2020)               # x, x, y, y
# The Scourge's furnaces (a quest's spell focus), and the ore and herbs on the crater's floor.
FURNACE = 193004
NODES = (189980, 189981, 191133, 190171, 190172)
FLOOR_TOP = 545.0
# The game's quests that need the garrison: the Shadow Vault's Malykriss quests (Crusader Olakin
# Sainrith's, Keritose Bloodblade's first, Vereth the Cunning's), off in Remix's world.
QUESTS_OFF = {
    13138: "I'm Smelting... Smelting!", 13140: "The Runesmiths of Malykriss", 13155: "Vereth the Cunning",
    13143: "New Recruit", 13145: "The Vile Hold", 13146: "Generosity Abounds", 13147: "Matchmaker",
    13160: "Stunning View", 13161: "The Rider of the Unholy", 13162: "The Rider of Frost",
    13163: "The Rider of Blood", 13164: "The Fate of Bloodbane",
}

# ---- Who lives here -------------------------------------------------------------------------------
EBON_BLADE, FRIENDLY = 2050, 35              # FactionTemplate: the Knights of the Ebon Blade's; friendly to all
PASSIVE, NOT_SELECTABLE = 770, 0x02000000    # unit flags: not attackable nor attacking; not selectable
CIVILIAN, TRIGGER = 2, 128                   # flags_extra
LIFE, MAGIC = "npc_remix_bazaar_life", "npc_remix_malykriss"
NERUB = "Remnant of Azjol-Nerub"
DEATHCHARGER = 25280                         # the Acherus Deathcharger's look, as a mount
INVISIBLE = [11686]

# entry: (name, subname, displays, scale, type, faction, unit flags, flags_extra, script, gossip text,
#         equipment from, flies)
PEOPLE = {
    770400: ("Ebon Blade Gatewarden", "Knights of the Ebon Blade", [25998, 25999, 26000, 26001], 1, 7, EBON_BLADE, PASSIVE, CIVILIAN, LIFE, 0, 29202, False),
    770401: ("Ebon Blade Sentinel", "Knights of the Ebon Blade", [26834, 26835, 26836, 26837], 1, 7, EBON_BLADE, PASSIVE, CIVILIAN, LIFE, 0, 30197, False),
    770402: ("Ebon Blade Runesmith", "Knights of the Ebon Blade", [25580, 25745, 25746, 25747], 1, 7, EBON_BLADE, PASSIVE, CIVILIAN, LIFE, 0, 28865, False),
    770403: ("Ebon Blade Duelist", "Knights of the Ebon Blade", [25998, 25999, 26000, 26001], 1, 7, EBON_BLADE, PASSIVE, CIVILIAN, MAGIC, 0, 29202, False),
    770404: ("Commander Aldren Hask", "Knights of the Ebon Blade", [26834], 1, 7, EBON_BLADE, PASSIVE, CIVILIAN, LIFE, 7702101, 30197, False),
    770405: ("Deathcharger", None, [DEATHCHARGER], 1, 1, EBON_BLADE, PASSIVE | NOT_SELECTABLE, CIVILIAN, "", 0, 0, False),
    770406: ("Captured Atrocity", "Held in a Moment", [7858], 1, 6, FRIENDLY, PASSIVE | NOT_SELECTABLE, CIVILIAN, "", 0, 0, False),
    770410: ("Warlord Kaz'anub", NERUB, [23882], 0.6, 7, FRIENDLY, PASSIVE, CIVILIAN, LIFE, 7702102, 0, False),
    770411: ("Elder Zek'thira", NERUB, [24130], 1, 7, FRIENDLY, PASSIVE, CIVILIAN, LIFE, 7702103, 0, False),
    770412: ("Architect Thekk'ri", NERUB, [23570], 1, 7, FRIENDLY, PASSIVE, CIVILIAN, LIFE, 7702104, 0, False),
    770413: ("Azjol Warden", NERUB, [23942, 23578], 1, 7, FRIENDLY, PASSIVE, CIVILIAN, LIFE, 0, 0, False),
    770414: ("Azjol Silkweaver", NERUB, [23569, 23564], 1, 7, FRIENDLY, PASSIVE, CIVILIAN, LIFE, 0, 0, False),
    770415: ("Azjol Skitterer", None, [23819, 23571], 1, 8, FRIENDLY, PASSIVE, CIVILIAN, "", 0, 0, False),
    770416: ("Azjol Skyguard", NERUB, [23913, 23916], 1, 7, FRIENDLY, PASSIVE | NOT_SELECTABLE, CIVILIAN, MAGIC, 0, 0, True),
    770417: ("Azjol Envoy", NERUB, [23569], 1, 7, FRIENDLY, PASSIVE, CIVILIAN, LIFE, 7702105, 0, False),
    # The time-magic's hosts.
    770420: ("Hourglass Sands", None, INVISIBLE, 1, 10, FRIENDLY, PASSIVE | NOT_SELECTABLE, TRIGGER, MAGIC, 0, 0, False),
    770421: ("Bazaar Sandshaper", "Keepers of Time", [14887], 1, 2, FRIENDLY, PASSIVE, CIVILIAN, MAGIC, 0, 0, False),
    770422: ("Hourglass's Heart", None, INVISIBLE, 1, 10, FRIENDLY, PASSIVE | NOT_SELECTABLE, TRIGGER, MAGIC, 0, 0, True),
    770423: ("Frost Sphere", None, [25144], 1, 10, FRIENDLY, PASSIVE | NOT_SELECTABLE, CIVILIAN, MAGIC, 0, 0, True),
    770424: ("Time Rift", None, [25392], 1, 10, FRIENDLY, PASSIVE | NOT_SELECTABLE, CIVILIAN, MAGIC, 0, 0, True),
    770425: ("Saronite Fog", None, INVISIBLE, 1, 10, FRIENDLY, PASSIVE | NOT_SELECTABLE, TRIGGER, "", 0, 0, False),
    770426: ("Burrow", None, INVISIBLE, 1, 10, FRIENDLY, PASSIVE | NOT_SELECTABLE, TRIGGER, "", 0, 0, False),
}
# Auras each always has (creature_template_addon): the magic's visuals.
AURAS = {
    770406: "34712 45776",     # Time Stop, Ice Block: a moment held
    770414: "56726",           # Nerubian Webs: spinning
    770420: "50057",           # the Hourglass of Eternity's glow and sound of running sand
    770423: "67539",           # Frost Sphere
    770425: "63096",           # Saronite Fog Visual
    770426: "66969",           # Churning Ground Visual: a burrow, with its sound
}

# Spawns, 7706000 and up: (guid, entry, x, y, near z, orientation, stand state, emote state, mount,
#                          wander, height above the floor)
EB_COMMANDER = (6402.0, 1772.0)
SPAWNS = [
    # The west gate: two wardens, mounted, facing out.
    (7706001, 770400, 6352.0, 1936.0, 508.6, WEST, 0, 0, DEATHCHARGER, 0, 0),
    (7706002, 770400, 6338.0, 1936.0, 508.6, WEST, 0, 0, DEATHCHARGER, 0, 0),
    # The Ebon Blade's quarter, the east field: the commander and the nerubians' envoy, duelists,
    # knights at its mouth, deathchargers, a captured atrocity held in a moment.
    (7706003, 770404, *EB_COMMANDER, 508.6, facing(*EB_COMMANDER, 6394.0, 1866.0), 0, 0, 0, 0, 0),
    (7706004, 770417, 6404.5, 1768.0, 508.6, facing(6404.5, 1768.0, *EB_COMMANDER), 0, 0, 0, 0, 0),
    (7706005, 770403, 6415.0, 1755.0, 508.6, facing(6415.0, 1755.0, 6415.0, 1758.5), 0, STATE_READY1H, 0, 0, 0),
    (7706006, 770403, 6415.0, 1758.5, 508.6, facing(6415.0, 1758.5, 6415.0, 1755.0), 0, STATE_READY1H, 0, 0, 0),
    (7706007, 770401, 6386.0, 1789.0, 508.6, facing(6386.0, 1789.0, 6394.0, 1866.0), 0, 0, 0, 0, 0),
    (7706008, 770401, 6380.0, 1790.0, 508.6, facing(6380.0, 1790.0, 6394.0, 1866.0), 0, 0, 0, 0, 0),
    (7706009, 770405, 6428.0, 1782.0, 508.6, WEST, 0, 0, 0, 0, 0),
    (7706010, 770405, 6431.0, 1775.0, 508.6, WEST, 0, 0, 0, 0, 0),
    (7706011, 770406, 6430.0, 1760.0, 508.6, facing(6430.0, 1760.0, 6415.0, 1757.0), 0, 0, 0, 0, 0),
    # The Runeworks: runesmiths at the Scourge's forges.
    (7706012, 770402, 6300.0, 1745.0, 525.2, facing(6300.0, 1745.0, 6312.0, 1742.0), 0, STATE_WORK, 0, 0, 0),
    (7706013, 770402, 6316.0, 1733.0, 525.2, facing(6316.0, 1733.0, 6312.0, 1742.0), 0, STATE_WORK, 0, 0, 0),
    (7706014, 770402, 6292.0, 1760.0, 525.2, facing(6292.0, 1760.0, 6300.0, 1745.0), 0, 0, 0, 0, 0),
    # The walkways: a sentinel at the Icy Lookout, a nerubian warden at the Altar of Sacrifice, both
    # watching the Citadel.
    (7706015, 770401, 6552.0, 1645.0, 631.6, facing(6552.0, 1645.0, *CITADEL), 0, 0, 0, 0, 0),
    (7706016, 770413, 6098.0, 1921.0, 632.6, facing(6098.0, 1921.0, *CITADEL), 0, 0, 0, 0, 0),
    # The nerubians' hall, the north-west lobe by the Blood Forge.
    (7706020, 770410, 6512.0, 1852.0, 514.0, SOUTH, 0, 0, 0, 0, 0),
    (7706021, 770411, 6503.0, 1864.0, 513.0, facing(6503.0, 1864.0, 6512.0, 1852.0), 0, 0, 0, 0, 0),
    (7706022, 770412, 6488.0, 1834.0, 510.0, facing(6488.0, 1834.0, 6462.0, 1801.0), 0, 0, 0, 0, 0),
    (7706023, 770414, 6478.0, 1866.0, 510.0, facing(6478.0, 1866.0, 6490.0, 1850.0), 0, STATE_SPELL, 0, 0, 0),
    (7706024, 770414, 6520.0, 1838.0, 515.0, facing(6520.0, 1838.0, 6505.0, 1850.0), 0, STATE_SPELL, 0, 0, 0),
    (7706025, 770413, 6466.0, 1850.0, 510.0, SOUTH, 0, 0, 0, 0, 0),
    (7706026, 770415, 6495.0, 1848.0, 510.0, 0.0, 0, 0, 0, 4.0, 0),
    (7706027, 770415, 6500.0, 1842.0, 510.0, 0.0, 0, 0, 0, 4.0, 0),
    (7706028, 770415, 6490.0, 1856.0, 510.0, 0.0, 0, 0, 0, 4.0, 0),
    (7706029, 770415, 6505.0, 1850.0, 513.0, 0.0, 0, 0, 0, 4.0, 0),
    (7706030, 770426, 6485.0, 1872.0, 510.0, 0.0, 0, 0, 0, 0, 0),
    (7706031, 770426, 6514.0, 1832.0, 514.0, 0.0, 0, 0, 0, 0, 0),
    # Skyguards circling the necropolis, outside its ribs (src/RemixMalykriss.cpp flies them).
    (7706035, 770416, NECROPOLIS[0] + 115.0, NECROPOLIS[1], None, WEST, 0, 0, 0, 0, 655.0),
    (7706036, 770416, NECROPOLIS[0] - 115.0, NECROPOLIS[1], None, EAST, 0, 0, 0, 0, 690.0),
    # The heart's magic: the sands, the sandshapers and the rift pouring into the hourglass's heart,
    # frost spheres circling it.
    (7706040, 770420, *HOURGLASS, 508.6, 0.0, 0, 0, 0, 0, 0.1),
    (7706041, 770422, *HOURGLASS, 508.6, 0.0, 0, 0, 0, 0, 4.0),
    (7706042, 770421, HOURGLASS[0], HOURGLASS[1] - 7.0, 508.6, WEST, 0, 0, 0, 0, 0),
    (7706043, 770421, HOURGLASS[0], HOURGLASS[1] + 7.0, 508.6, EAST, 0, 0, 0, 0, 0),
    (7706044, 770424, *HOURGLASS, 508.6, 0.0, 0, 0, 0, 0, 13.0),
    (7706045, 770423, HOURGLASS[0] + 9.0, HOURGLASS[1], 508.6, 0.0, 0, 0, 0, 0, 5.0),
    (7706046, 770423, HOURGLASS[0] - 9.0, HOURGLASS[1], 508.6, 0.0, 0, 0, 0, 0, 5.0),
    # Saronite fog seeping in at the gate and the south edge.
    (7706047, 770425, 6345.0, 1950.0, 508.6, 0.0, 0, 0, 0, 0, 0.3),
    (7706048, 770425, 6308.0, 1872.0, 508.6, 0.0, 0, 0, 0, 0, 0.3),
]

# Walkers on a loop (waypoint_data, path id = guid): (guid, entry, near z, mount, [(x, y, pause ms)])
WALKERS = [
    # An Ebon Blade patrol, mounted, from the gate round the camp to their quarter.
    (7706050, 770401, 508.6, DEATHCHARGER, [(6345.0, 1926.0, 4000), (6318.0, 1884.0, 0), (6318.0, 1832.0, 0), (6345.0, 1806.0, 0),
                                            (6392.0, 1790.0, 0), (6425.0, 1768.0, 3000), (6392.0, 1790.0, 0), (6345.0, 1806.0, 0),
                                            (6318.0, 1832.0, 0), (6318.0, 1884.0, 0)]),
    # A nerubian warden, from the hall to the north-east lobe and back.
    (7706051, 770413, 509.0, 0, [(6470.0, 1852.0, 3000), (6450.0, 1828.0, 0), (6448.0, 1790.0, 0), (6470.0, 1760.0, 0),
                                 (6500.0, 1730.0, 4000), (6470.0, 1760.0, 0), (6448.0, 1790.0, 0), (6450.0, 1828.0, 0)]),
    # A sentinel on the west rampart.
    (7706052, 770401, 632.0, 0, [(6170.0, 1898.0, 3000), (6260.0, 1939.0, 0), (6350.0, 1952.0, 0), (6440.0, 1964.0, 5000),
                                 (6350.0, 1952.0, 0), (6260.0, 1939.0, 0)]),
    # A nerubian warden on the north walkway.
    (7706053, 770413, 630.0, 0, [(6547.0, 1810.0, 4000), (6547.0, 1720.0, 0), (6552.0, 1650.0, 0), (6555.0, 1600.0, 4000),
                                 (6552.0, 1650.0, 0), (6547.0, 1720.0, 0)]),
]

# What stands here (game object templates 770220 and up, spawns 7705400 and up): key: (display, size, name)
PROPS = {
    "eb_banner":   (8713, 1.0, "Ebon Blade Banner"),
    "eb_runeforge": (8175, 2.03, "Runeforge"),
    "eb_brazier":  (9195, 1.0, "Brazier"),
    "blood_orb":   (8365, 1.5, "Blood Orb"),
    "egg":         (7803, 1.2, "Nerubian Egg"),
    "saronite":    (7836, 0.5, "Chunk of Saronite"),
    "small_glass": (7133, 0.012, "Hourglass"),                 # the great hourglass's, a hand high
}
PROP_ENTRY = {key: 770220 + i for i, key in enumerate(PROPS)}
# (prop, x, y, near z, orientation, what it's for[, height above the floor, tilt])
PLACED = [
    ("eb_banner", 6356.0, 1939.0, 508.6, WEST, "the west gate"),
    ("eb_banner", 6334.0, 1939.0, 508.6, WEST, "the west gate"),
    ("blood_orb", 6358.0, 1930.0, 508.6, 0.0, "the west gate"),
    ("blood_orb", 6332.0, 1930.0, 508.6, 0.0, "the west gate"),
    ("eb_banner", 6408.0, 1792.0, 508.6, facing(6408.0, 1792.0, 6394.0, 1866.0), "the Ebon Blade's quarter"),
    ("eb_banner", 6376.0, 1795.0, 508.6, facing(6376.0, 1795.0, 6394.0, 1866.0), "the Ebon Blade's quarter"),
    ("eb_runeforge", 6416.0, 1740.0, 508.6, WEST, "the Ebon Blade's quarter"),
    ("eb_brazier", 6390.0, 1742.0, 508.6, 0.0, "the Ebon Blade's quarter"),
    ("eb_brazier", 6395.0, 1760.0, 508.6, 0.0, "the Ebon Blade's quarter"),
    ("eb_brazier", 6412.0, 1778.0, 508.6, 0.0, "the Ebon Blade's quarter"),
    ("egg", 6523.0, 1858.0, 515.0, 0.4, "the nerubians' hall"),
    ("egg", 6519.0, 1846.0, 515.0, 1.9, "the nerubians' hall"),
    ("egg", 6470.0, 1866.0, 509.0, 3.1, "the nerubians' hall"),
    ("egg", 6476.0, 1834.0, 509.0, 5.0, "the nerubians' hall"),
    ("egg", 6480.0, 1868.0, 509.0, 2.6, "the nerubians' hall"),
    ("saronite", 6486.0, 1830.0, 510.0, 0.7, "the nerubians' hall, the architect's"),
    ("saronite", 6491.0, 1829.0, 510.0, 2.2, "the nerubians' hall, the architect's"),
    # Over the market lane, hourglasses held in time, each stopped at its own tilt.
    *[("small_glass", x, 1893.0, 508.6, o, "the market lane, held in time", up, tilt) for x, o, up, tilt in (
        (6378.0, 0.3, 5.0, 0.35), (6369.0, 2.1, 5.8, -0.25), (6360.0, 4.0, 4.6, 0.45), (6351.0, 5.2, 5.4, -0.4), (6342.0, 1.0, 5.0, 0.2))],
]

# ---- What they say ------------------------------------------------------------------------------
# guid: [(text, emote, reply guid, reply, reply emote)]
LINES = {
    7706001: [("Nothing comes through this gate that the Ebon Blade has not seen first.", 0, 0, "", 0),
              ("Quiet out there tonight.", TALK, 7706002, "It is always quiet before the Citadel sends something.", 0)],
    7706002: [("We served him once. Every one of us remembers the day we stopped.", 0, 0, "", 0)],
    7706003: [("Malykriss was to be his new Acherus. We took the old one from him. The dragons took this one from his calendar.", TALK, 0, "", 0),
              ("Your Warlord wants the east stair.", TALK, 7706004, "The Warlord wants everything. He will settle for the east stair.", 0),
              ("If anything in this hall tries to kill you, it is not one of mine.", 0, 0, "", 0)],
    7706004: [("The death knights keep their gate and we keep our webs. Nobody has been eaten yet.", TALK, 0, "", 0)],
    7706007: [("Keep to the floor, Timerunner. The edges are older than they look.", 0, 0, "", 0)],
    7706008: [("A sword that has been cursed twice still cuts. So does a knight.", 0, 0, "", 0)],
    7706012: [("A rune is a promise cut into steel. Ours we keep now.", 0, 0, "", 0),
              ("The Scourge left these forges warm. It would be rude not to use them.", LAUGH, 0, "", 0)],
    7706013: [("Bring your blade, if it is worth the trouble. Razorice, Fallen Crusader, Cinderglacier: the forge does not care which side you were on.", TALK, 0, "", 0)],
    7706015: [("He built this place to watch over Icecrown. Now it watches him.", 0, 0, "", 0),
              ("From up here you can count the Citadel's lights. I stopped counting.", 0, 0, "", 0)],
    7706016: [("They sacrificed our dead on this altar. Now I stand on it, and I am not dead.", 0, 0, "", 0)],
    7706020: [("The Lich King broke Azjol-Nerub and made our king his hound. We have long memories, surface-walker. Longer than his reign.", TALK, 0, "", 0),
              ("Arthas walked through our dead city with Anub'arak at his heel. I watched from the dark. I am done watching.", 0, 0, "", 0),
              ("The death knights walked through the webs again.", TALK, 7706021, "Then we weave them stronger. They were his once, as our dead are. Patience.", 0)],
    7706021: [("The dragons say this hour sits outside his reach. I have heard promises before. I am weaving anyway.", 0, 0, "", 0)],
    7706022: [("Saronite remembers every shape you give it. That is why we build slowly.", 0, 0, "", 0),
              ("He wanted a fortress to replace Acherus. He will find it has new tenants.", LAUGH, 0, "", 0)],
    7706023: [("Shh. The silk listens.", 0, 0, "", 0)],
    7706025: [("Mind the webs, surface-walker. They are older than your city.", 0, 0, "", 0)],
    7706050: [("Make way. Ebon Blade, on our rounds.", 0, 0, "", 0)],
    7706051: [("The halls are quiet. The quiet is ours now.", 0, 0, "", 0)],
    7706052: [("The wind off the Citadel smells of saronite and old blood. You get used to it. I hope you never do.", 0, 0, "", 0)],
}

# What the named say when spoken to (npc_text, gossip_menu 77100 + n).
GOSSIP = {
    7702101: "Commander Aldren Hask, Knights of the Ebon Blade. The Highlord sent us to hold this hall while the dragons trade in it, and to make sure nothing the Lich King left behind gets up again.$B$BWe served him once. Most of the Scourge you will meet in Icecrown were raised by the same hand that raised me. Kill them cleanly, $c. They would thank you, if they could.",
    7702102: "You smell of the surface, and of sand. The dragons vouch for you and the death knights tolerate you. That will do.$B$BWe are what is left of Azjol-Nerub that still breathes. The Scourge took our dead, our king and our craft: their ziggurats are our ziggurats, their necropolises our halls, built crooked by thieves. Malykriss is the first we have taken back.$B$BWhen your war reaches the Citadel, tell the Lich King the nerubians sent you.",
    7702103: "Anub'arak was our king. Now he is the Lich King's, somewhere under the ice, and he still answers to his name. One day someone will end that.$B$BI would like it to be one of us. I will settle for someone who remembers that he was ours.",
    7702104: "Look at the ribs above you. Unfinished, all of them. The Scourge build fast and badly; they learned from slaves who were afraid.$B$BWe are not afraid. Give me a hundred years and this will be a hall worth the name. The dragons tell me you will not be here in a hundred years. Pity.",
    7702105: "I carry the Warlord's words to the death knights, and theirs back to him. Most days that means carrying complaints about webs.$B$BThey are better company than they look. So are we.",
}


def main():
    out = []
    w = out.append
    lo, hi = BOX[0], BOX[1]
    w("""-- Malykriss: The Vile Hold, the Infinite Bazaar's home (tools/malykriss.py writes this file: edit that and
-- run it again). The Scourge's garrison is not in Remix's world, nor the game's quests that need it; the
-- hall belongs to the Bazaar's allies, the Knights of the Ebon Blade and the last free nerubians of
-- Azjol-Nerub, and to the time-magic round the hourglass (src/RemixMalykriss.cpp). Never in
-- ChromieCraft's world: this file is Remix's world database's only.
""")
    # The garrison, and everything that names its spawns.
    entries = ", ".join(str(e) for e in sorted(GARRISON))
    w(f"""-- The garrison: {len(GARRISON)} kinds, every spawn of them in Malykriss.
DROP TEMPORARY TABLE IF EXISTS `remix_malykriss_gone`;
CREATE TEMPORARY TABLE `remix_malykriss_gone` (`guid` INT UNSIGNED NOT NULL PRIMARY KEY)
  SELECT `guid` FROM `creature` WHERE `map` = {MAP} AND `position_x` BETWEEN {lo} AND {hi}
    AND `position_y` BETWEEN {BOX[2]} AND {BOX[3]} AND `id` IN ({entries});
DELETE FROM `waypoint_data` WHERE `id` IN (SELECT `path_id` FROM `creature_addon` WHERE `path_id` <> 0 AND `guid` IN (SELECT `guid` FROM `remix_malykriss_gone`));
DELETE FROM `creature_addon` WHERE `guid` IN (SELECT `guid` FROM `remix_malykriss_gone`);
DELETE FROM `creature_formations` WHERE `leaderGUID` IN (SELECT `guid` FROM `remix_malykriss_gone`) OR `memberGUID` IN (SELECT `guid` FROM `remix_malykriss_gone`);
DELETE FROM `smart_scripts` WHERE `source_type` = 0 AND -`entryorguid` IN (SELECT `guid` FROM `remix_malykriss_gone`);
DELETE FROM `pool_creature` WHERE `guid` IN (SELECT `guid` FROM `remix_malykriss_gone`);
DELETE FROM `game_event_creature` WHERE `guid` IN (SELECT `guid` FROM `remix_malykriss_gone`);
DELETE FROM `linked_respawn` WHERE `guid` IN (SELECT `guid` FROM `remix_malykriss_gone`) OR `linkedGuid` IN (SELECT `guid` FROM `remix_malykriss_gone`);
DELETE FROM `creature_movement_override` WHERE `SpawnId` IN (SELECT `guid` FROM `remix_malykriss_gone`);
DELETE FROM `creature` WHERE `guid` IN (SELECT `guid` FROM `remix_malykriss_gone`);
DROP TEMPORARY TABLE `remix_malykriss_gone`;

-- The Scourge's furnaces, and the ore and herbs on the crater's floor (the camp stands on it).
DROP TEMPORARY TABLE IF EXISTS `remix_malykriss_gone`;
CREATE TEMPORARY TABLE `remix_malykriss_gone` (`guid` INT UNSIGNED NOT NULL PRIMARY KEY)
  SELECT `guid` FROM `gameobject` WHERE `map` = {MAP} AND `position_x` BETWEEN {lo} AND {hi}
    AND `position_y` BETWEEN {BOX[2]} AND {BOX[3]}
    AND (`id` = {FURNACE} OR (`id` IN ({", ".join(str(n) for n in NODES)}) AND `position_z` < {FLOOR_TOP}));
DELETE FROM `pool_gameobject` WHERE `guid` IN (SELECT `guid` FROM `remix_malykriss_gone`);
DELETE FROM `game_event_gameobject` WHERE `guid` IN (SELECT `guid` FROM `remix_malykriss_gone`);
DELETE FROM `gameobject` WHERE `guid` IN (SELECT `guid` FROM `remix_malykriss_gone`);
DROP TEMPORARY TABLE `remix_malykriss_gone`;

-- The game's quests that need the garrison, off (disables, quests).""")
    w("DELETE FROM `disables` WHERE `sourceType` = 1 AND `entry` IN (" + ", ".join(str(q) for q in QUESTS_OFF) + ");")
    w("INSERT INTO `disables` (`sourceType`, `entry`, `flags`, `params_0`, `params_1`, `comment`) VALUES")
    w(",\n".join(f"(1, {q}, 0, '', '', {sql_text('Wrath Remix: ' + t + ' (Malykriss is the Bazaar)')})" for q, t in QUESTS_OFF.items()) + ";")
    w("")

    # The people.
    w("DELETE FROM `creature_template` WHERE `entry` BETWEEN 770400 AND 770479;")
    w("DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN 770400 AND 770479;")
    w("DELETE FROM `creature_template_addon` WHERE `entry` BETWEEN 770400 AND 770479;")
    w("DELETE FROM `creature_template_movement` WHERE `CreatureId` BETWEEN 770400 AND 770479;")
    w("DELETE FROM `creature_equip_template` WHERE `CreatureID` BETWEEN 770400 AND 770479;")
    w("INSERT INTO `creature_template` (`entry`, `name`, `subname`, `gossip_menu_id`, `minlevel`, `maxlevel`, `exp`, `faction`, `npcflag`,")
    w("  `speed_walk`, `speed_run`, `rank`, `unit_class`, `unit_flags`, `unit_flags2`, `type`, `flags_extra`,")
    w("  `HealthModifier`, `DamageModifier`, `BaseAttackTime`, `RegenHealth`, `ScriptName`) VALUES")
    rows = []
    for entry, (name, sub, displays, scale, ctype, faction, flags, extra, script, text, equip, flies) in PEOPLE.items():
        menu = text - 7702100 + 77100 if text else 0
        rows.append(f"({entry}, {sql_text(name)}, {sql_text(sub) if sub else 'NULL'}, {menu}, 80, 80, 2, {faction}, {1 if text else 0}, "
                    f"1, 1.14286, 0, 1, {flags}, 2048, {ctype}, {extra}, 10, 1, 2000, 1, {sql_text(script)})")
    w(",\n".join(rows) + ";")
    w("INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) VALUES")
    rows = []
    for entry, (name, sub, displays, scale, *_rest) in PEOPLE.items():
        for i, d in enumerate(displays):
            rows.append(f"({entry}, {i}, {d}, {scale}, 1, 0)")
    w(",\n".join(rows) + ";")
    w("INSERT INTO `creature_template_addon` (`entry`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) VALUES")
    w(",\n".join(f"({e}, 0, 0, 0, 1, 0, 0, {sql_text(a)})" for e, a in AURAS.items()) + ";")
    w("-- The flying ones hover where they are put.")
    w("INSERT INTO `creature_template_movement` (`CreatureId`, `Ground`, `Swim`, `Flight`, `Rooted`, `Chase`, `Random`, `InteractionPauseTimer`) VALUES")
    w(",\n".join(f"({e}, 0, 0, 1, 0, 0, 0, NULL)" for e, p in PEOPLE.items() if p[11]) + ";")
    w("-- Weapons: the game's own Ebon Blade knights'.")
    for entry, p in PEOPLE.items():
        if p[10]:
            w(f"INSERT INTO `creature_equip_template` (`CreatureID`, `ID`, `ItemID1`, `ItemID2`, `ItemID3`, `VerifiedBuild`)"
              f" SELECT {entry}, 1, `ItemID1`, `ItemID2`, `ItemID3`, 0 FROM `creature_equip_template` WHERE `CreatureID` = {p[10]} AND `ID` = 1;")
    w("")
    w("DELETE FROM `npc_text` WHERE `ID` BETWEEN 7702100 AND 7702179;")
    w("INSERT INTO `npc_text` (`ID`, `text0_0`, `text0_1`, `Probability0`) VALUES")
    w(",\n".join(f"({i}, {sql_text(t)}, {sql_text(t)}, 1)" for i, t in GOSSIP.items()) + ";")
    w("DELETE FROM `gossip_menu` WHERE `MenuID` BETWEEN 77100 AND 77179;")
    w("INSERT INTO `gossip_menu` (`MenuID`, `TextID`) VALUES")
    w(",\n".join(f"({i - 7702100 + 77100}, {i})" for i in GOSSIP) + ";")
    w("")

    # Where they are.
    w("DELETE FROM `creature_addon` WHERE `guid` BETWEEN 7706000 AND 7706999;")
    w("DELETE FROM `waypoint_data` WHERE `id` BETWEEN 7706000 AND 7706999;")
    w("DELETE FROM `creature` WHERE `guid` BETWEEN 7706000 AND 7706999;")
    w("INSERT INTO `creature` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `equipment_id`, `position_x`, `position_y`, `position_z`, `orientation`, `spawntimesecs`, `wander_distance`, `MovementType`, `Comment`) VALUES")
    rows, addons = [], []
    for guid, entry, x, y, near, o, stand, emote, mount, wander, up in SPAWNS:
        z = (z_at(x, y, near) if near is not None else 0.0) + (up or 0.1)
        equip = 1 if PEOPLE[entry][10] else 0
        rows.append(f"({guid}, {entry}, {MAP}, {ZONE}, {AREA}, 1, 1, {equip}, {x:.2f}, {y:.2f}, {z:.2f}, {o:.4f}, 60, {wander:.1f}, {1 if wander else 0}, "
                    f"{sql_text('Wrath Remix: ' + PEOPLE[entry][0] + ', Malykriss')})")
        if stand or emote or mount:
            addons.append(f"({guid}, 0, {mount}, {stand}, 1, {emote}, 0, '')")
    for guid, entry, near, mount, points in WALKERS:
        x, y, _ = points[0]
        rows.append(f"({guid}, {entry}, {MAP}, {ZONE}, {AREA}, 1, 1, {1 if PEOPLE[entry][10] else 0}, {x:.2f}, {y:.2f}, {z_at(x, y, near) + 0.1:.2f}, 0, 60, 0, 2, "
                    f"{sql_text('Wrath Remix: ' + PEOPLE[entry][0] + ', Malykriss, on rounds')})")
        addons.append(f"({guid}, {guid}, {mount}, 0, 1, 0, 0, '')")
    w(",\n".join(rows) + ";")
    w("INSERT INTO `creature_addon` (`guid`, `path_id`, `mount`, `bytes1`, `bytes2`, `emote`, `visibilityDistanceType`, `auras`) VALUES")
    w(",\n".join(addons) + ";")
    w("INSERT INTO `waypoint_data` (`id`, `point`, `position_x`, `position_y`, `position_z`, `orientation`, `delay`, `move_type`) VALUES")
    rows = []
    for guid, entry, near, mount, points in WALKERS:
        for n, (x, y, pause) in enumerate(points, start=1):
            rows.append(f"({guid}, {n}, {x:.2f}, {y:.2f}, {z_at(x, y, near) + 0.1:.2f}, NULL, {pause}, 0)")
    w(",\n".join(rows) + ";")
    w("")

    # What stands here.
    w("DELETE FROM `gameobject_template` WHERE `entry` BETWEEN 770220 AND 770259;")
    w("INSERT INTO `gameobject_template` (`entry`, `type`, `displayId`, `name`, `IconName`, `castBarCaption`, `unk1`, `size`, `AIName`, `ScriptName`, `VerifiedBuild`) VALUES")
    w(",\n".join(f"({PROP_ENTRY[k]}, 5, {d}, {sql_text(n)}, '', '', '', {s}, '', '', 0)" for k, (d, s, n) in PROPS.items()) + ";")
    w("DELETE FROM `gameobject` WHERE `guid` BETWEEN 7705400 AND 7705599;")
    w("INSERT INTO `gameobject` (`guid`, `id`, `map`, `zoneId`, `areaId`, `spawnMask`, `phaseMask`, `position_x`, `position_y`, `position_z`, `orientation`,")
    w("  `rotation0`, `rotation1`, `rotation2`, `rotation3`, `spawntimesecs`, `animprogress`, `state`, `ScriptName`, `VerifiedBuild`, `Comment`) VALUES")
    rows = []
    for i, (key, x, y, near, o, what, *more) in enumerate(PLACED):
        up, tilt = (more + [0.0, 0.0])[:2]
        # turned by o about the up axis, then tipped by tilt about its own long one
        rot = (math.cos(o / 2) * math.sin(tilt / 2), math.sin(o / 2) * math.sin(tilt / 2), math.sin(o / 2) * math.cos(tilt / 2),
               math.cos(o / 2) * math.cos(tilt / 2))
        rows.append(f"({7705400 + i}, {PROP_ENTRY[key]}, {MAP}, {ZONE}, {AREA}, 1, 1, {x:.2f}, {y:.2f}, {z_at(x, y, near) + up:.2f}, {o:.4f}, "
                    f"{rot[0]:.6f}, {rot[1]:.6f}, {rot[2]:.6f}, {rot[3]:.6f}, 300, 100, 1, '', 0, {sql_text('Wrath Remix: ' + PROPS[key][2] + ', ' + what)})")
    w(",\n".join(rows) + ";")
    w("")

    # The lines (remix_bazaar_line is 0023_bazaar's; this file's are its spawns').
    w("DELETE FROM `remix_bazaar_line` WHERE `guid` BETWEEN 7706000 AND 7706999;")
    w("INSERT INTO `remix_bazaar_line` (`guid`, `line`, `text`, `emote`, `reply_guid`, `reply`, `reply_emote`) VALUES")
    rows = []
    for guid, lines in LINES.items():
        for n, (text, emote, reply_guid, reply, reply_emote) in enumerate(lines):
            rows.append(f"({guid}, {n}, {sql_text(text)}, {emote}, {reply_guid}, {sql_text(reply)}, {reply_emote})")
    w(",\n".join(rows) + ";")

    with open(OUT, "w") as f:
        f.write("\n".join(out) + "\n")
    print(f"{len(GARRISON)} kinds of the garrison gone, {len(QUESTS_OFF)} quests off, {len(SPAWNS) + len(WALKERS)} spawns, "
          f"{len(PLACED)} things placed, {sum(len(v) for v in LINES.values())} lines")


if __name__ == "__main__":
    main()
