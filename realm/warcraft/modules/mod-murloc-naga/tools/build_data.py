#!/usr/bin/env python3
"""Builds the Murlocs' and the Naga's data from the game's own tables, the core's world SQL and
the server's maps, and tools/content.py (their people, things and quests):

  - data/sql/chromiecraft/world/murloc_naga_world.sql: the world database (the races' `*_dbc`
    rows, starts, skills, standing, racials, their stories' spells, the quests of their kin opened
    to them, and what the retired starts left, taken out);
  - data/sql/chromiecraft/world/murloc_story.sql and naga_story.sql: the two stories, compiled
    (tools/murloc/compile.py), with the server test's steps for each (warcraft/server/);
  - data/client/dbc/*.txt: the rows to change in the game's tables (the Skyborne's format, applied
    by src/MurlocNagaPatch.cpp as the world server starts);
  - data/client/looks.txt: the textures the patch makes (the murlocs' skins from the game's own,
    the naga's new skin colours) and the murloc model it makes from the game's;
  - data/client/narration.txt: the intros' narrations, put together from the game's own sounds;
  - data/client/Cameras/: the intros' cameras (tools/cameras.py).

Its output is committed; run it again after changing it.

  build_data.py DBC_DIR WORLD_SQL_DIR MAPS_DIR

DBC_DIR, MAPS_DIR: the server's dbc and maps folders (the data.zip in warcraft/server-data.env);
WORLD_SQL_DIR: the core's data/sql/base/db_world at the realm's commit (warcraft/server-version.env).

The races (the user: "Murloc to alliance and naga to horde"), level 10, each with its own story to 55:
  19  Murloc, Alliance: from the Wrathtail's pens at the Zoram Strand (tools/murloc/: murloc_story.sql)
  20  Naga, Horde: from Rethress Sanctum in Azshara (tools/naga/: naga_story.sql), compiled after the
      murlocs' and clear of their phases
(their first starts, the murlocs' village and the naga's camp off Auberdine, are retired: tools/content.py)
Races 19 and 20 were the game's Taunka and Northrend Skeleton, which only creatures use: they move
to 30 and 31 in the game's tables (their looks, their creatures' looks), as the other modules move
theirs (22 to 29)."""

import json
import math
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODULE = os.path.dirname(HERE)
MODULES = os.path.dirname(MODULE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(MODULES, "mod-allied-races", "tools"))
import cameras  # noqa: E402
import content as C  # noqa: E402
import murloc_looks as ML  # noqa: E402
import naga_looks as NL  # noqa: E402
import sqlrows  # noqa: E402
import terrain  # noqa: E402

COLUMNS = json.load(open(os.path.join(MODULES, "mod-allied-races", "tools", "dbc_columns.json")))
TYPES = json.load(open(os.path.join(MODULES, "mod-allied-races", "tools", "dbc_types.json")))

HUMAN, ORC, DWARF, NIGHTELF, UNDEAD, TAUREN, GNOME, TROLL, BLOODELF, DRAENEI = 1, 2, 3, 4, 5, 6, 7, 8, 10, 11
MURLOC, NAGA = C.MURLOC, C.NAGA
RACE_IDS = (MURLOC, NAGA)
MOVED = {19: 30, 20: 31}                       # Taunka, Northrend Skeleton: the creatures' races, moved
BIT = {MURLOC: 1 << (MURLOC - 1), NAGA: 1 << (NAGA - 1)}
ALLIANCE_MASK = sum(1 << (r - 1) for r in (HUMAN, DWARF, NIGHTELF, GNOME, DRAENEI))
HORDE_MASK = sum(1 << (r - 1) for r in (ORC, UNDEAD, TAUREN, TROLL, BLOODELF))
KIN = {MURLOC: NIGHTELF, NAGA: TROLL}           # whose standing, stats, quests and items they share
WARRIOR, PALADIN, HUNTER, ROGUE, PRIEST, DK, SHAMAN, MAGE, WARLOCK, DRUID = 1, 2, 3, 4, 5, 6, 7, 8, 9, 11
CLASSES_OF = {MURLOC: (WARRIOR, HUNTER, ROGUE, PRIEST, SHAMAN, MAGE),
              NAGA: (WARRIOR, HUNTER, ROGUE, PRIEST, SHAMAN, MAGE, WARLOCK)}
# Whose start each class takes (gear, action bar): the kin's where it has the class, the nearest
# race of the side's where it hasn't.
TEMPLATE = {
    MURLOC: {WARRIOR: NIGHTELF, HUNTER: NIGHTELF, ROGUE: NIGHTELF, PRIEST: NIGHTELF, SHAMAN: DRAENEI, MAGE: HUMAN},
    NAGA: {WARRIOR: TROLL, HUNTER: TROLL, ROGUE: TROLL, PRIEST: TROLL, SHAMAN: TROLL, MAGE: TROLL, WARLOCK: ORC},
}
NAME = {MURLOC: "Murloc", NAGA: "Naga"}
PREFIX = {MURLOC: "Mu", NAGA: "Na"}
FILESTRING = {MURLOC: "Murloc", NAGA: "Naga_"}  # Character\<this>\<Male|Female>\<this><Male|Female>.m2
FEATURE_LABELS = {MURLOC: ("FEATURES", "FEATURES", "MURLOC"), NAGA: ("FEATURES", "FEATURES", "NAGA")}

# Ids clear of the game's (an HD look's too) and the other modules'.
ID_SECTIONS = 860000
ID_SECTIONS_END = 869999
ID_OUTFIT, ID_HAIRGEO, ID_NAMEGEN = 9300, 9300, 93000
ID_DISPLAY = {MURLOC: (33101, 33102)}           # the naga wear the game's own (17402, 17403)
ID_MODEL = {MURLOC: (3701, 3702)}
PLAYER_MODEL = 0x4                               # CreatureModelData: a player's model (drawn as a character)
LOOT_COMMENT = "mod-murloc-naga: camp"                  # creature_loot_template rows of the naga's camp
ID_TRIBE_MODEL, ID_TRIBE_DISPLAY = 3703, 33103   # the tribe's people's murloc, a look a skin (33103-33115)
ID_SEQUENCE = {MURLOC: 9021, NAGA: 9022}
ID_CAMERA = {MURLOC: 9021, NAGA: 9022}
ID_NARRATION = {MURLOC: 975001, NAGA: 975002}
ID_GO_DISPLAY = 9750                            # the game's end at 9624
ID_VOCAL = 9500                                 # (the Skyborne's 9000 to 9107, the allied races' 9200 on)
# Their voices: (men's, women's) words, and when pressed: the game's creature murlocs' (fidgets, aggro)
# and naga's (the naga's and the sirens': their pre-aggro hiss, their aggro).
VOICES = {MURLOC: ((414, 415), (416, 1109)), NAGA: ((3437, 4024), (3438, 4025))}
# The people's voices (the game's creature sounds): as they're spoken to, as a quest is handed in.
MURLOC_HELLO, MURLOC_CHEER = (414, 415, 1109), (416, 417)
VOICED = {"elder": (MURLOC_HELLO, MURLOC_CHEER), "chief": ((416, 417, 414), MURLOC_CHEER), "cook": (MURLOC_HELLO, MURLOC_CHEER),
          "snatcher": ((1109, 415), MURLOC_CHEER), "oracle": ((415, 414), MURLOC_CHEER), "fishmonger": (MURLOC_HELLO, ()),
          "sloshy": ((8475,), (8475,)), "szaria": ((4024,), ()), "vyssa": ((4024,), ()), "ssaveth": ((3437,), ())}
# The retired naga camp's people who are the naga's story's (tools/murloc/profiles.py NAGA.KEPT_ENTRIES).
KEPT_ENTRIES = {"szaria": 975017, "ssaveth": 975018, "vyssa": 975019}
SPELLS = {"phase_murloc": 98880, "phase_naga": 98881, "amphibious": 98882, "mrrgglll": 98883, "slippery": 98884,
          "serpent": 98885, "tail_sweep": 98886, "scales": 98887, "low_profile": 98888, "phase_murloc_alone": 98889}
# Where a murloc keeps a low profile (Low Profile: creatures notice it at a few yards, their minimum):
# every town and city (AreaTable's town flag), and the outposts its story goes into.
TOWN_FLAG = 0x200
LOW_PROFILE_OUTPOSTS = [2897]                   # Zoram'gar Outpost

# The naga's new skin colours, after the game's five: (name, the colour they're made from, its hue (0 to 1
# around the colour wheel, -1 to keep each colour's own), saturation x, lightness x), as the game's
# creature naga are coloured (the naga lords' crimson, the sirens' gold and violet) and a grey.
NAGA_COLOURS = {
    0: [("Crimson", 0, 0.99, 1.4, 1.1), ("Gold", 0, 0.11, 1.5, 1.25), ("Violet", 0, 0.77, 1.3, 1.1), ("Ashen", 1, -1, 0.1, 1.3)],
    1: [("Crimson", 3, 0.99, 1.3, 1.1), ("Silver", 3, -1, 0.1, 1.4), ("Violet", 3, 0.78, 1.2, 1.0), ("Gold", 1, 0.12, 1.2, 1.1)],
}
NAGA_STOCK_COLOURS = 5
# Their names on the creation screen's random button.
NAMES = {
    (MURLOC, 0): ["Mrglgrl", "Grrlgl", "Blrrgl", "Mrrlmrl", "Glubglub", "Gurglug", "Murglor", "Slrrp", "Flrrbl", "Mrkglk",
                  "Grglmr", "Blubbr", "Mrrrgal", "Gloomfin", "Splashgill", "Wigglefin", "Snorkl", "Grublub", "Rrrglm", "Bloopglub"],
    (MURLOC, 1): ["Mrrglia", "Glubbeth", "Blurgla", "Mrrlia", "Sloshi", "Gurgla", "Murla", "Flrrba", "Bubbla", "Glimmerfin",
                  "Mrgala", "Plopla", "Shellia", "Splishi", "Rrrgla", "Blippa", "Glurra", "Mrrmie", "Kelpie", "Wavelia"],
    (NAGA, 0): ["Ssarith", "Vashtan", "Zsorroth", "Nazrael", "Ssethis", "Thalassor", "Iszar", "Varzhoth", "Kezzik", "Ssalak",
                "Zulreth", "Hasshar", "Naziros", "Thessk", "Morrsath", "Szaruun", "Velrash", "Ithyss", "Zhessar", "Krasith"],
    (NAGA, 1): ["Szaria", "Ssylvara", "Neshara", "Vashira", "Zalyssa", "Ithessa", "Lyssandra", "Nazjara", "Seshiri", "Thyssa",
                "Vysseth", "Zsara", "Ilthana", "Sseraphe", "Nalyss", "Kezra", "Isshara", "Velsza", "Hisseth", "Mazira"],
}
STATS_FROM = KIN
# The towns' factions a murloc starts Hostile with (at war: their guards attack, and can be attacked),
# set by the module (src/MurlocNaga.cpp) as one is made: the Alliance's and the Horde's, and the
# goblins' (the Steamwheedle Cartel's). Standing above Hostile ends the war (the core's own rule).
MURLOC_HOSTILE_FACTIONS = [469, 72, 47, 69, 54, 930, 67, 76, 81, 68, 530, 911, 169, 21, 369, 470, 577]


class Dbc:
    def __init__(self, path):
        data = open(path, "rb").read()
        magic, self.count, self.fields, self.size, _ = struct.unpack("<4s4I", data[:20])
        assert magic == b"WDBC", path
        self.raw = [data[20 + i * self.size:20 + (i + 1) * self.size] for i in range(self.count)]
        self.text = data[20 + self.count * self.size:]
        self.rows = [list(struct.unpack(f"<{self.fields}I", r)) for r in self.raw] if self.size == self.fields * 4 else None

    def s(self, offset):
        end = self.text.index(b"\0", offset)
        return self.text[offset:end].decode("utf-8")


def f32(v):
    return struct.unpack("<f", struct.pack("<I", v))[0]


def i32(v):
    return struct.unpack("<i", struct.pack("<I", v & 0xFFFFFFFF))[0]


def values_of(dbc, row, types):
    return [dbc.s(v) if t == "s" else f32(v) if t == "f" else v for v, t in zip(row, types)]


def esc(text):
    return str(text).replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n")


class Client:
    """The changes to the game's tables, a file for each (MurlocNagaPatch.cpp applies them with the
    Skyborne's ApplyChanges)."""

    def __init__(self):
        self.files, self.types = {}, {}

    def line(self, name, text):
        self.files.setdefault(name, []).append(text)

    def put(self, name, types, values):
        assert len(types) == len(values), (name, len(types), len(values))
        assert self.types.setdefault(name, types) == types, name
        self.line(name, "put\t" + "\t".join(esc(v) if t == "s" else repr(float(v)) if t == "f" else str(int(v) & 0xFFFFFFFF)
                                             for t, v in zip(types, values)))

    def put_raw(self, name, data):
        self.line(name, "putraw\t" + data.hex())

    def append_raw(self, name, data):
        self.line(name, "appendraw\t" + data.hex())

    def orfield(self, name, row_id, field, value):
        self.line(name, f"or\t{row_id}\t{field}\t{value & 0xFFFFFFFF}")

    def setfield(self, name, row_id, field, value):
        self.line(name, f"set\t{row_id}\t{field}\t{value & 0xFFFFFFFF}")

    def copyrow(self, name, row_id, new_id):
        self.line(name, f"copyrow\t{row_id}\t{new_id}")

    def remapfield(self, name, field, old, new):
        self.line(name, f"remapfield\t{field}\t{old}\t{new}")

    def write(self, folder):
        os.makedirs(folder, exist_ok=True)
        for old in os.listdir(folder):
            if old.endswith(".txt"):
                os.remove(os.path.join(folder, old))
        for name, lines in sorted(self.files.items()):
            with open(os.path.join(folder, name + ".txt"), "w", newline="\n") as f:
                f.write(f"# {name}: the Murlocs' and the Naga's changes (tools/build_data.py)\n")
                if name in self.types:
                    f.write(f"types\t{self.types[name]}\n")
                f.write("\n".join(lines) + "\n")


def q(v):
    return sqlrows.quote(v)


def sql_value(v, t):
    if t == "s":
        return q(str(v))
    if t == "f":
        return repr(float(v))
    return str(i32(int(v)))


def or_into(column):
    """A race mask column (a signed INT) with the new row's bits OR'd in (mod-allied-races' or_into)."""
    bits = f"((`{column}` | VALUES(`{column}`)) & 0xFFFFFFFF)"
    return f"`{column}` = IF({bits} >= 0x80000000, CAST({bits} AS SIGNED) - 4294967296, {bits})"


class Sql:
    def __init__(self):
        self.parts = []

    def comment(self, text):
        self.parts.append("\n-- " + text.replace("\n", "\n-- "))

    def raw(self, text):
        self.parts.append(text)

    def insert(self, table, columns, rows, verb="INSERT"):
        if not rows:
            return
        cols = ", ".join(f"`{c}`" for c in columns)
        for i in range(0, len(rows), 200):
            body = ",\n".join("(" + ", ".join(fmt(v) for v in r) + ")" for r in rows[i:i + 200])
            self.parts.append(f"{verb} INTO `{table}` ({cols}) VALUES\n{body};")

    def replace_dbc(self, table, types, rows):
        if not rows:
            return
        cols = ", ".join(f"`{c}`" for c in COLUMNS[table])
        for i in range(0, len(rows), 200):
            body = ",\n".join("(" + ", ".join(sql_value(v, t) for v, t in zip(r, types)) + ")" for r in rows[i:i + 200])
            self.parts.append(f"REPLACE INTO `{table}` ({cols}) VALUES\n{body};")


def fmt(v):
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return repr(round(v, 4))
    return q(v)


# Places -------------------------------------------------------------------------------------------

def ground(xy):
    """(x, y, z): z the ground's (or the one given, for a building's floor or a dock)."""
    if len(xy) == 3:
        return tuple(float(v) for v in xy)
    x, y = xy
    z = terrain.height(x, y)
    assert z is not None, xy
    return (float(x), float(y), round(z + 0.05, 2))


def sea_floor_ring(centre, radius_min, radius_max, depth_min, depth_max, count, seed):
    """[count] points of the sea floor around [centre], the water above them [depth_min] to
    [depth_max] yards deep, spread around it: every such point on a polar grid, then picked in
    turn around the circle (from the angle [seed]), each at least 6 yards from the others."""
    found = []
    for step in range(0, 360, 4):
        a = math.radians(step)
        for r in range(int(radius_min), int(radius_max) + 1, 3):
            x, y = centre[0] + r * math.cos(a), centre[1] + r * math.sin(a)
            g, w = terrain.height(x, y), terrain.liquid(x, y)
            if g is not None and w is not None and depth_min <= w - g <= depth_max:
                found.append(((step - math.degrees(seed)) % 360, round(x, 1), round(y, 1), round(g + 0.1, 2)))
    found.sort()
    out = []
    spacing = 360.0 / count
    for n in range(count):
        want = n * spacing
        best = None
        for angle, x, y, z in found:
            if all(math.hypot(x - p[0], y - p[1]) > 6 for p in out):
                d = min(abs(angle - want), 360 - abs(angle - want))
                if best is None or d < best[0]:
                    best = (d, (x, y, z))
        if best:
            out.append(best[1])
    assert len(out) == count, (centre, len(out))
    return out


def summit(centre, radius):
    best = None
    for dx in range(-radius, radius + 1, 2):
        for dy in range(-radius, radius + 1, 2):
            g = terrain.height(centre[0] + dx, centre[1] + dy)
            if g is not None and (best is None or g > best[2]):
                best = (centre[0] + dx, centre[1] + dy, g)
    return (float(best[0]), float(best[1]), round(best[2] + 0.1, 2))


def rotation(o):
    return (0.0, 0.0, round(math.sin(o / 2), 6), round(math.cos(o / 2), 6))


def top(x, y):
    """The ground, or the water over it."""
    g, w = terrain.height(x, y), terrain.liquid(x, y)
    return max(g if g is not None else -1e9, w if w is not None else -1e9)


def camera_keys(path):
    """[(ms, (x, y) or (x, y, z), height above the ground or water when z isn't given, target)]:
    the camera kept at least 4 yards above the ground and the water along the way."""
    keys = []
    for ms, at, rise, target in path:
        if len(at) == 2:
            at = (at[0], at[1], top(*at) + rise)
        if len(target) == 2:
            target = (target[0], target[1], top(*target) + 1.5)
        keys.append((ms, at, target))
    for (t0, a, _), (t1, b, _) in zip(keys, keys[1:]):
        for i in range(1, 10):
            f = i / 10
            x, y, z = (a[k] + (b[k] - a[k]) * f for k in range(3))
            assert z > top(x, y) + 2.5, ("the camera goes under", t0, (x, y, z), top(x, y))
    return keys


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    dbc_dir, world, maps = sys.argv[1:4]
    terrain.MAPS = maps
    D = lambda name: Dbc(os.path.join(dbc_dir, name + ".dbc"))
    W = lambda name: sqlrows.table(os.path.join(world, name + ".sql"))[1]
    client, sql = Client(), Sql()
    sql.raw("-- The Murlocs and the Naga (mod-murloc-naga): generated by tools/build_data.py from the game's own tables,\n"
            "-- the core's world SQL, the server's maps and tools/content.py; edit those, not this. Safe to run again:\n"
            "-- every row is replaced, every mask OR'd, every id the module's own.")

    # The creatures' races moved out of the new races' places in the client's own rows -----------
    for old, new in MOVED.items():
        client.copyrow("ChrRaces", old, new)
        for table, field in (("CharSections", 1), ("CharHairGeosets", 1), ("CreatureDisplayInfoExtra", 1),
                             ("CharacterFacialHairStyles", 0), ("VocalUISounds", 2)):
            client.remapfield(table, field, old, new)

    races = D("ChrRaces")
    rt = TYPES["chrraces_dbc"]
    race_rows = {r[0]: r for r in races.rows}

    # The murlocs' model and looks: a CreatureModelData row and a CreatureDisplayInfo row a sex, from
    # the game's murloc's (its size, collision, footsteps) with the character model the patch makes.
    displays, model_data = D("CreatureDisplayInfo"), D("CreatureModelData")
    display_rows = {r[0]: r for r in displays.rows}
    model_rows = {r[0]: r for r in model_data.rows}
    dt = "iiiifissssiiiiii"
    mt = "iisifiiffffiiifff" + "ffffff" + "fffff"
    murloc_model = next(r for r in model_data.rows if model_data.s(r[2]).lower() == "creature\\murloc\\murloc.mdx")
    naga_display = display_rows[race_rows[13][4]]
    # The game draws a player as a character (the composed skin, the face, the chosen hair and features'
    # geosets) only on a model flagged a player's (CreatureModelData's 0x4, "is player model"). Without it
    # a player is drawn as a creature is: every geoset at once, the character's textures white. The
    # murlocs' models take a playable race's flags (the human's, 0x804); the game's naga male hasn't the
    # flag (its female has), so the naga's two models get it.
    player_flags = model_rows[display_rows[race_rows[1][4]][1]][1]
    assert player_flags & PLAYER_MODEL, hex(player_flags)
    for display in (race_rows[13][4], race_rows[13][5]):
        client.orfield("CreatureModelData", display_rows[display][1], 1, PLAYER_MODEL)
    model_sql, display_sql = [], []
    for sex in (0, 1):
        m = values_of(model_data, murloc_model, mt)
        m[0] = ID_MODEL[MURLOC][sex]
        m[1] = player_flags
        m[2] = "Character\\Murloc\\%s\\Murloc%s.mdx" % (("Male", "Female")[sex], ("Male", "Female")[sex])
        client.put("CreatureModelData", mt, m)
        model_sql.append(m)
        d = values_of(displays, naga_display, dt)
        d[0], d[1], d[2], d[3], d[4] = ID_DISPLAY[MURLOC][sex], ID_MODEL[MURLOC][sex], 0, 0, 1.0
        d[12] = 0
        client.put("CreatureDisplayInfo", dt, d)
        display_sql.append(d)
    # The tribe's people (tools/murloc/): murloc2 as a creature's model, with the costume's emotes
    # (tools/murloc_model.py), a look for each of its skins.
    m = values_of(model_data, murloc_model, mt)
    m[0], m[2] = ID_TRIBE_MODEL, "Creature\\MurlocTribe\\MurlocTribe.mdx"
    client.put("CreatureModelData", mt, m)
    model_sql.append(m)
    murloc_look = display_rows[next(r[0] for r in displays.rows if r[1] == murloc_model[0])]
    for n in range(len(ML.SKINS)):
        d = values_of(displays, murloc_look, dt)
        d[0], d[1], d[2], d[3], d[4] = ID_TRIBE_DISPLAY + n, ID_TRIBE_MODEL, d[2], 0, 1.0
        d[6], d[7], d[8], d[9] = f"MurlocTribeSkin{n:02d}", "", "", ""     # (the murloc's sounds, kept)
        client.put("CreatureDisplayInfo", dt, d)
        display_sql.append(d)
    sql.comment("The murlocs' models (CreatureModelData) and looks (CreatureDisplayInfo): the race's, and its tribe's people's\n"
                "(murloc2 in each of its skins, with emotes); the naga wear the game's own.")
    sql.raw("REPLACE INTO `creaturemodeldata_dbc` (`ID`, `Flags`, `ModelName`, `SizeClass`, `ModelScale`, `BloodID`, `FootprintTextureID`, "
            "`FootprintTextureLength`, `FootprintTextureWidth`, `FootprintParticleScale`, `FoleyMaterialID`, `FootstepShakeSize`, "
            "`DeathThudShakeSize`, `SoundID`, `CollisionWidth`, `CollisionHeight`, `MountHeight`, `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`, "
            "`GeoBoxMaxX`, `GeoBoxMaxY`, `GeoBoxMaxZ`, `WorldEffectScale`, `AttachedEffectScale`, `MissileCollisionRadius`, "
            "`MissileCollisionPush`, `MissileCollisionRaise`) VALUES\n"
            + ",\n".join("(" + ", ".join(sql_value(v, t) for v, t in zip(r, mt)) + ")" for r in model_sql) + ";")
    sql.raw(f"REPLACE INTO `creature_model_info` (`DisplayID`, `BoundingRadius`, `CombatReach`, `Gender`, `DisplayID_Other_Gender`) "
            f"SELECT n.`id`, i.`BoundingRadius`, i.`CombatReach`, 2, 0 FROM `creature_model_info` i JOIN (SELECT "
            + " UNION SELECT ".join(str(ID_TRIBE_DISPLAY + n) + (" AS `id`" if n == 0 else "") for n in range(len(ML.SKINS)))
            + ") n WHERE i.`DisplayID` = 478;")                       # (a murloc of the game's: its size)
    sql.raw("REPLACE INTO `creaturedisplayinfo_dbc` (`ID`, `ModelID`, `SoundID`, `ExtendedDisplayInfoID`, `CreatureModelScale`, "
            "`CreatureModelAlpha`, `TextureVariation_1`, `TextureVariation_2`, `TextureVariation_3`, `PortraitTextureName`, `BloodLevel`, "
            "`BloodID`, `NPCSoundID`, `ParticleColorID`, `CreatureGeosetData`, `ObjectEffectPackageID`) VALUES\n"
            + ",\n".join("(" + ", ".join(sql_value(v, t) for v, t in zip(r, dt)) + ")" for r in display_sql) + ";")

    # Races ----------------------------------------------------------------------------------------
    sql.comment("The races: Murloc (19, the Alliance's, the night elves' standing) and Naga (20, the Horde's, the trolls'); the\n"
                "game's Taunka and Northrend Skeleton, which only creatures are, moved to 30 and 31.")
    server_races = []
    for race in RACE_IDS:
        kin = race_rows[KIN[race]]
        v = values_of(races, kin, rt)
        v[0] = race
        v[1] = race_rows[BLOODELF][1]                   # flags: playable, can mount
        v[4], v[5] = ID_DISPLAY[race] if race in ID_DISPLAY else (race_rows[13][4], race_rows[13][5])
        v[6] = PREFIX[race]
        v[11] = FILESTRING[race]
        v[12] = ID_SEQUENCE[race]
        for base in (14, 31, 48):
            for i in range(base, base + 16):
                v[i] = NAME[race] if i == base else ""
        v[65], v[66], v[67] = FEATURE_LABELS[race]
        v[68] = 0
        client.put("ChrRaces", rt, v)
        server_races.append(v)
    for old, new in MOVED.items():
        v = values_of(races, race_rows[old], rt)
        v[0] = new
        server_races.append(v)
    sql.replace_dbc("chrraces_dbc", rt, server_races)

    # Looks ----------------------------------------------------------------------------------------
    st = TYPES["charsections_dbc"]
    sections = D("CharSections")
    new_sections = []
    next_id = [ID_SECTIONS]

    def section(race, sex, kind, tex, flags, variation, colour):
        v = [next_id[0], race, sex, kind, tex[0], tex[1], tex[2], flags, variation, colour]
        next_id[0] += 1
        client.put("CharSections", st, v)
        new_sections.append(v)

    # The murlocs (tools/murloc_looks.py; their model and textures made by tools/murloc_model.py as the
    # server is packaged). The body and eyes are drawn with the composed texture's face region, which
    # the face rows fill: a face is an eye colour, each in every skin colour (FaceLower the skin's body,
    # FaceUpper the eyes beside it); the skin rows' base (one colour) is under it. A hair style is a fin
    # style, its colour the fins' (the hair row's texture); a facial hair style a feature (geosets
    # only). Every run the game sizes its choices by is whole: a face a skin colour, a feature and a
    # fin style a fin colour.
    looks = ["# The textures the patch makes from the game's own (tools/build_data.py): the naga's new colours.",
             "# naga_colour\t<sex>\t<new colour>\t<the colour it's made from>\t<hue (-1: kept)>\t<saturation x>\t<lightness x>"]
    for sex, sexname in ((0, "Male"), (1, "Female")):
        for c in range(len(ML.SKINS)):
            section(MURLOC, sex, 0, ["Character\\Murloc\\MurlocBase.blp", "", ""], 1, 0, c)
        for face in range(len(ML.EYE_COLOURS)):
            for c in range(len(ML.SKINS)):
                section(MURLOC, sex, 1, [ML.face_lower(c), ML.face_upper(face, c), ""], 1, face, c)
        for feature in range(len(ML.FEATURES[sexname])):
            for h in range(len(ML.FIN_COLOURS)):
                section(MURLOC, sex, 2, ["", "", ""], 1, feature, h)
        for style in range(len(ML.FIN_STYLES)):
            for h in range(len(ML.FIN_COLOURS)):
                section(MURLOC, sex, 3, [ML.fin_texture(style, h), "", ""], 1, style, h)
        for c in range(len(ML.SKINS)):
            section(MURLOC, sex, 4, ["", "", ""], 1, 0, c)

    # The naga: the game's own looks of its naga (race 13's rows, an HD look's textures by the same
    # names), and their new colours, made by the patch from the game's.
    # Their skins, faces and underwear are the game's; their hair and facial hair rows (which name
    # textures the game hasn't) are the headdresses' and the features' (tools/naga_looks.py): a hair
    # row a headdress style and colour (its texture the headdress's in that colour), a facial hair row
    # a feature and colour (none: the outfits are their own textures).
    naga_rows = [values_of(sections, r, st) for r in sections.rows if r[1] == 13 and r[3] in (0, 1, 4)]
    assert naga_rows, "the game's naga looks"
    for r in naga_rows:
        section(NAGA, r[2], r[3], [r[4], r[5], r[6]], r[7], r[8], r[9])
    for sex, sexname in ((0, "Male"), (1, "Female")):
        for style in range(len(NL.HEADDRESSES[sexname]) + 1):
            for c in range(NL.colours(sexname)):
                section(NAGA, sex, 3, [NL.headdress_texture(sexname, style, c), "", ""], 1, style, c)
        for feature in range(len(NL.features(sexname)) + 1):
            for c in range(NL.colours(sexname)):
                section(NAGA, sex, 2, ["", "", ""], 1, feature, c)
    for sex, sexname in ((0, "Male"), (1, "Female")):
        p = f"Character\\Naga_\\{sexname}\\Naga_{sexname}"
        for n, (name, source, hue, sat, light) in enumerate(NAGA_COLOURS[sex]):
            c = NAGA_STOCK_COLOURS + n
            looks.append(f"naga_colour\t{sex}\t{c}\t{source}\t{hue}\t{sat}\t{light}")
            section(NAGA, sex, 0, [f"{p}Skin00_{c:02d}.blp", f"{p}Skin00_{c:02d}_Extra.blp", ""], 1, 0, c)
            section(NAGA, sex, 1, [f"{p}FaceLower00_{c:02d}.blp", f"{p}FaceUpper00_{c:02d}.blp", ""], 1, 0, c)
            section(NAGA, sex, 4, [f"{p}NakedPelvisSkin00_{c:02d}.blp", f"{p}NakedTorsoSkin00_{c:02d}.blp", ""], 1, 0, c)
    for r in sections.rows:
        if r[1] in MOVED:
            v = values_of(sections, r, st)
            v[1] = MOVED[r[1]]
            new_sections.append(v)
    assert next_id[0] <= ID_SECTIONS_END
    sql.comment("Their looks; the creatures' races 19 and 20 moved to 30 and 31.")
    sql.raw(f"DELETE FROM `charsections_dbc` WHERE `ID` BETWEEN {ID_SECTIONS} AND {ID_SECTIONS_END};")
    sql.replace_dbc("charsections_dbc", st, new_sections)

    # Hair shapes and features (the game's tables only).
    geo = D("CharHairGeosets")
    gid = ID_HAIRGEO
    for sex, sexname in ((0, "Male"), (1, "Female")):
        for style in range(len(NL.HEADDRESSES[sexname]) + 1):
            client.put("CharHairGeosets", "iiiiii", [gid, NAGA, sex, style, NL.hair_geoset(style), 0])
            gid += 1
    for sex, sexname in ((0, "Male"), (1, "Female")):
        for style in range(len(ML.FIN_STYLES)):
            client.put("CharHairGeosets", "iiiiii", [gid, MURLOC, sex, style, ML.fin_geoset(style), 0])
            gid += 1
    facial = D("CharacterFacialHairStyles")
    for sex, sexname in ((0, "Male"), (1, "Female")):
        for feature in range(len(NL.features(sexname)) + 1):
            geosets = [NL.feature_geoset(feature)] + [0] * (facial.fields - 4)
            client.append_raw("CharacterFacialHairStyles", struct.pack(f"<{facial.fields}I", NAGA, sex, feature, *geosets))
    for sex, sexname in ((0, "Male"), (1, "Female")):
        for feature in range(len(ML.FEATURES[sexname])):
            # (the first geoset: group 1, the model's mesh 100 + it)
            geosets = [ML.feature_geoset(feature)] + [0] * (facial.fields - 4)
            client.append_raw("CharacterFacialHairStyles", struct.pack(f"<{facial.fields}I", MURLOC, sex, feature, *geosets))
    # Their voices at the UI's moments ("not enough mana", "can't do that yet"): the game's own creature
    # sounds, a row each moment the game's humans have (VocalUISounds: moment, race, the men's and
    # women's words, then when pressed): the murlocs' fidgets and aggro, the naga's and the sirens'.
    vocal = D("VocalUISounds")
    vid = ID_VOCAL
    for r in vocal.rows:
        if r[2] == HUMAN:
            for race, (normal, pissed) in VOICES.items():
                client.put("VocalUISounds", "iiiiiii", [vid, r[1], race, normal[0], normal[1], pissed[0], pissed[1]])
                vid += 1
    assert vid < ID_VOCAL + 400
    nid = ID_NAMEGEN
    for (race, sex), names in NAMES.items():
        for name in names:
            client.put("NameGen", "isii", [nid, name, race, sex])
            nid += 1
    open(os.path.join(MODULE, "data", "client", "looks.txt"), "w", newline="\n").write("\n".join(looks) + "\n")

    # Classes and starting gear --------------------------------------------------------------------
    for race in RACE_IDS:
        for cls in CLASSES_OF[race]:
            client.append_raw("CharBaseInfo", bytes([race, cls]))
    outfits = D("CharStartOutfit")
    oid, outfit_rows = ID_OUTFIT, []
    for raw in outfits.raw:
        orace, cls, sex, outfit = raw[4], raw[5], raw[6], raw[7]
        for new in RACE_IDS:
            if TEMPLATE[new].get(cls) == orace:
                client.put_raw("CharStartOutfit", struct.pack("<I", oid) + bytes([new, cls, sex, outfit]) + raw[8:])
                ints = struct.unpack(f"<{len(raw[8:]) // 4}I", raw[8:])
                outfit_rows.append([oid, new, cls, sex, outfit] + list(ints))
                oid += 1
    sql.comment("Their classes' starting gear: their kin's for the class (or the nearest race's).")
    sql.replace_dbc("charstartoutfit_dbc", TYPES["charstartoutfit_dbc"], outfit_rows)

    # Skills and abilities by race, standing ---------------------------------------------------------
    lines = D("SkillLine")
    racial_lines, languages = set(), {}
    for r in lines.rows:
        if r[1] == 9 and "racial" in lines.s(r[3]).lower():
            racial_lines.add(r[0])
        if r[1] == 10:
            languages[r[0]] = lines.s(r[3])
    COMMON, ORCISH, TITAN = 98, 109, 140

    def side_bits(mask, line):
        add = 0
        if line in languages:
            # (the murlocs speak Nerglish alone: the game's Titan, renamed, which no player race speaks)
            if line == TITAN:
                add |= BIT[MURLOC]
            if line == ORCISH and mask & HORDE_MASK:
                add |= BIT[NAGA]
            return add
        if line in racial_lines:
            return 0
        if mask & ALLIANCE_MASK:
            add |= BIT[MURLOC]
        if mask & HORDE_MASK:
            add |= BIT[NAGA]
        return add

    def ors(table, dbc, field_mask, field_line, sql_table):
        rows = []
        for r in dbc.rows:
            mask = r[field_mask]
            if mask == 0 or mask & 0x7FFFFFFF == 0x7FFFFFFF:
                continue
            add = side_bits(mask, r[field_line])
            if add and (mask | add) != mask:
                client.orfield(table, r[0], field_mask, add)
                v = list(r)
                v[field_mask] = mask | add
                rows.append(v)
        if rows:
            cols = COLUMNS[sql_table]
            body = ",\n".join("(" + ", ".join(str(i32(x)) for x in v) + ")" for v in rows)
            sql.raw(f"INSERT INTO `{sql_table}` ({', '.join(f'`{c}`' for c in cols)}) VALUES\n{body}\n"
                    f"ON DUPLICATE KEY UPDATE {or_into('RaceMask')};")

    sql.comment("Skills and abilities open to either side's races are open to theirs (the racials and languages aside).")
    ors("SkillRaceClassInfo", D("SkillRaceClassInfo"), 2, 1, "skillraceclassinfo_dbc")
    ors("SkillLineAbility", D("SkillLineAbility"), 3, 1, "skilllineability_dbc")

    sql.comment("Standing: their kin's (the night elves' for the murlocs, the trolls' for the naga). The naga are neutral to the\n"
                "night elves of Darnassus, the Explorers' League (Ironforge) and the Gnomeregan Exiles, whose people they meet in\n"
                "Darkshore, where the Horde's other races are hated: the core and the game take a reputation faction's people's\n"
                "reaction from the character's own standing with it, so those people talk to the naga alone of the Horde, and\n"
                "their guards leave them be. The first of a faction's four slots that names the race gives its standing; the\n"
                "naga's are put in the last, free slot of those three factions (and in no other slot of theirs).")
    factions = D("Faction")
    ft = TYPES["faction_dbc"]
    faction_rows = []
    for r in factions.rows:
        v = list(r)
        for slot in range(4):
            mask = r[2 + slot]
            if mask & 0x7FFFFFFF == 0x7FFFFFFF:
                continue
            for race in RACE_IDS:
                if race == NAGA and r[0] in C.NAGA_NEUTRAL_FACTIONS:
                    continue
                if race == MURLOC and r[0] in MURLOC_HOSTILE_FACTIONS:
                    continue
                if mask & (1 << (KIN[race] - 1)):
                    v[2 + slot] |= BIT[race]
        if r[0] in C.NAGA_NEUTRAL_FACTIONS:
            assert r[5] == 0, (r[0], "its last slot isn't free")
            v[5], v[13], v[17] = BIT[NAGA], 0, 1      # neutral, shown, not at war
        if v != list(r):
            for slot in range(4):
                if v[2 + slot] != r[2 + slot]:
                    client.orfield("Faction", r[0], 2 + slot, v[2 + slot] & ~r[2 + slot])
            if r[0] in C.NAGA_NEUTRAL_FACTIONS:
                client.setfield("Faction", r[0], 13, 0)
                client.setfield("Faction", r[0], 17, 1)
            faction_rows.append(values_of(factions, v, ft))
    cols = ", ".join(f"`{c}`" for c in COLUMNS["faction_dbc"])
    update = ", ".join(or_into(f"ReputationRaceMask_{n}") for n in range(1, 5))
    for i in range(0, len(faction_rows), 200):
        body = ",\n".join("(" + ", ".join(sql_value(x, t) for x, t in zip(r, ft)) + ")" for r in faction_rows[i:i + 200])
        sql.raw(f"INSERT INTO `faction_dbc` ({cols}) VALUES\n{body}\nON DUPLICATE KEY UPDATE {update};")
    sql.raw(f"UPDATE `faction_dbc` SET `ReputationBase_4` = 0, `ReputationFlags_4` = 1 WHERE `ID` IN "
            f"({', '.join(str(f) for f in C.NAGA_NEUTRAL_FACTIONS)});")
    sql.comment("The murlocs are no kin of the towns' (their standing with them: Hostile, set by the module as one is made;\n"
                "earlier releases put them in the night elves' slots).")
    sql.raw("UPDATE `faction_dbc` SET " + ", ".join(f"`ReputationRaceMask_{n}` = `ReputationRaceMask_{n}` & ~{BIT[MURLOC]}" for n in range(1, 5))
            + f" WHERE `ID` IN ({', '.join(str(f) for f in MURLOC_HOSTILE_FACTIONS)});")

    # The racials and the phases ---------------------------------------------------------------------
    spells = D("Spell")
    spt = TYPES["spell_dbc"]
    by_id = {r[0]: r for r in spells.rows}
    SC = {n: i for i, n in enumerate(COLUMNS["spell_dbc"])}

    def spell(template, sid, name, rank, description, aura_text, **fields):
        v = values_of(spells, by_id[template], spt)
        v[0] = sid
        for k in ("Name", "NameSubtext", "Description", "AuraDescription"):
            for i in range(16):
                v[SC[f"{k}_Lang_enUS"] + i] = ""
        v[SC["Name_Lang_enUS"]] = name
        v[SC["NameSubtext_Lang_enUS"]] = rank
        v[SC["Description_Lang_enUS"]] = description
        v[SC["AuraDescription_Lang_enUS"]] = aura_text
        for k, value in fields.items():
            v[SC[k]] = value
        client.put("Spell", spt, v)
        return v

    # The murlocs' questline (tools/murloc/) and the naga's (tools/naga/): compiled here, the murlocs' first (the
    # naga's phases keep clear of theirs where both stories are: Azshara), their phases' spells made below.
    story = murloc_story(D, W)
    naga = naga_story(D, W, story)

    PASSIVE, HIDDEN = 0x40, 0x80
    no_cost = dict(Reagent_1=0, ReagentCount_1=0, ManaCost=0, ManaCostPct=0, SpellClassSet=0, SpellClassMask_1=0,
                   SpellClassMask_2=0, SpellClassMask_3=0, BaseLevel=1, SpellLevel=1)
    spell_rows = [
        # Their phases in Darkshore and Ashenvale (spell_area): the world's and their own.
        spell(20550, SPELLS["phase_murloc"], "Murloc Kinship", "", "", "", Attributes=PASSIVE | HIDDEN | 0x100,
              Effect_1=6, EffectAura_1=261, EffectMiscValue_1=1 | C.PHASE[MURLOC], EffectBasePoints_1=0, EffectDieSides_1=1,
              Effect_2=0, EffectAura_2=0, Effect_3=0, EffectAura_3=0, **no_cost),
        spell(20550, SPELLS["phase_naga"], "Renegade's Path", "", "", "", Attributes=PASSIVE | HIDDEN | 0x100,
              Effect_1=6, EffectAura_1=261, EffectMiscValue_1=1 | C.PHASE[NAGA], EffectBasePoints_1=0, EffectDieSides_1=1,
              Effect_2=0, EffectAura_2=0, Effect_3=0, EffectAura_3=0, **no_cost),
        # The murlocs'.
        spell(20550, SPELLS["amphibious"], "Amphibious", "Racial Passive",
              "You breathe water as easily as air, and swim 50% faster.", "",
              Effect_1=6, EffectAura_1=82, EffectBasePoints_1=0, EffectDieSides_1=1,
              Effect_2=6, EffectAura_2=58, EffectBasePoints_2=49, EffectDieSides_2=1, ImplicitTargetA_2=1,
              Effect_3=0, EffectAura_3=0, SpellIconID=by_id[5227][SC["SpellIconID"]], **no_cost),
        spell(20549, SPELLS["mrrgglll"], "Mrrgglll!", "Racial",
              "Let out a terrible murloc war-gurgle, stunning enemies within 8 yards for 2 sec.", "",
              RecoveryTime=120000, CastingTimeIndex=1, **no_cost),
        spell(20550, SPELLS["slippery"], "Slippery", "Racial Passive",
              "Your wet scales make you harder to hit, increasing your chance to dodge by 1%.", "",
              Effect_1=6, EffectAura_1=49, EffectBasePoints_1=0, EffectDieSides_1=1, Effect_2=0, EffectAura_2=0,
              Effect_3=0, EffectAura_3=0, **no_cost),
        # The murlocs' in towns: noticed at a few yards (detected range -40: the game's minimum, 5 yards).
        spell(20550, SPELLS["low_profile"], "Low Profile", "", "", "", Attributes=PASSIVE | HIDDEN | 0x100,
              Effect_1=6, EffectAura_1=152, EffectBasePoints_1=-41, EffectDieSides_1=1, ImplicitTargetA_1=1,
              Effect_2=0, EffectAura_2=0, Effect_3=0, EffectAura_3=0, **no_cost),
        # The naga's.
        spell(20550, SPELLS["serpent"], "Serpent's Grace", "Racial Passive",
              "You breathe water as easily as air, and swim 50% faster.", "",
              Effect_1=6, EffectAura_1=82, EffectBasePoints_1=0, EffectDieSides_1=1,
              Effect_2=6, EffectAura_2=58, EffectBasePoints_2=49, EffectDieSides_2=1, ImplicitTargetA_2=1,
              Effect_3=0, EffectAura_3=0, SpellIconID=by_id[5227][SC["SpellIconID"]], **no_cost),
        spell(20549, SPELLS["tail_sweep"], "Tail Sweep", "Racial",
              "Sweep your tail through the enemies around you, stunning those within 8 yards for 2 sec.", "",
              RecoveryTime=120000, CastingTimeIndex=1, **no_cost),
        spell(20550, SPELLS["scales"], "Scales of the Deep", "Racial Passive",
              "Your hardened scales increase the armor you get from items by 5%.", "",
              Effect_1=6, EffectAura_1=142, EffectBasePoints_1=4, EffectDieSides_1=1, EffectMiscValue_1=1,
              Effect_2=0, EffectAura_2=0, Effect_3=0, EffectAura_3=0, **no_cost),
    ]
    durations = [r for r in D("SpellDuration").rows if r[2] == 0 and r[1] == r[3] and 0 < r[1] < 4294967295]

    def duration(seconds):
        if not seconds:
            return 21                                           # (until taken off)
        return min(durations, key=lambda r: (abs(r[1] - seconds * 1000), r[0]))[0]

    def story_spells(st, phase_name):
        """A story's phases (hidden, passive: each its bit) and auras (tools/murloc/ and tools/naga/: AURAS, the naga's
        memories, the marker and the fade): a mark on the bar, a disguise, a slow, a stun, a screen effect..."""
        for sid, bit in st.phase_spells:
            spell_rows.append(spell(20550, sid, phase_name, "", "", "", Attributes=PASSIVE | HIDDEN | 0x100,
                                    Effect_1=6, EffectAura_1=261, EffectMiscValue_1=bit, EffectBasePoints_1=0, EffectDieSides_1=1,
                                    Effect_2=0, EffectAura_2=0, Effect_3=0, EffectAura_3=0, **no_cost))
        if st is story:
            # The story's chapters that show the murlocs' phase alone (no world: the pens): its own phase, no other.
            spell_rows.append(spell(20550, SPELLS["phase_murloc_alone"], "Murloc Kinship", "", "", "", Attributes=PASSIVE | HIDDEN | 0x100,
                                    Effect_1=6, EffectAura_1=261, EffectMiscValue_1=C.PHASE[MURLOC], EffectBasePoints_1=0, EffectDieSides_1=1,
                                    Effect_2=0, EffectAura_2=0, Effect_3=0, EffectAura_3=0, **no_cost))
        for a in st.spells:
            icon = by_id[a["icon"]][SC["SpellIconID"]] if a["icon"] in by_id else by_id[20550][SC["SpellIconID"]]
            effects = a.get("effects") or [(a["aura"], a["misc"], a["amount"])]
            fields = {}
            for n in (1, 2, 3):
                if n <= len(effects):
                    aura, misc, amount = effects[n - 1]
                    fields.update({f"Effect_{n}": 6, f"EffectAura_{n}": aura, f"EffectMiscValue_{n}": misc,
                                   f"EffectBasePoints_{n}": amount - 1 if amount else 0, f"EffectDieSides_{n}": 1, f"ImplicitTargetA_{n}": 1,
                                   f"ImplicitTargetB_{n}": 0})
                else:
                    fields.update({f"Effect_{n}": 0, f"EffectAura_{n}": 0})
            spell_rows.append(spell(20550, a["id"], a["name"], "", a["text"], a["text"],
                                    Attributes=(HIDDEN | 0x100) if a.get("hidden") else 0, AttributesEx=0,
                                    # (a mark, a memory, the marker: kept through death)
                                    AttributesEx3=0x100000 if a["kind"] == "mark" or a.get("keep") else 0,
                                    DurationIndex=duration(a["seconds"]), RangeIndex=1, SpellIconID=icon,
                                    SpellVisualID_1=a["visual"], **fields, **no_cost))
    if story:
        story_spells(story, "Murloc Tidings")
    if naga:
        story_spells(naga, naga.P.phase_spell_name)
    # (the language spell's name: Nerglish, as its skill)
    titan = values_of(spells, by_id[816], spt)
    titan[SC["Name_Lang_enUS"]] = "Language Nerglish"
    client.put("Spell", spt, titan)
    sql.comment("Their racials, their phases (seen in Darkshore and Ashenvale: spell_area) and the murlocs' story's.")
    sql.replace_dbc("spell_dbc", spt, spell_rows)

    # The intros -------------------------------------------------------------------------------------
    sounds = D("SoundEntries")
    snt = TYPES["soundentries_dbc"]
    snd_rows = {r[0]: r for r in sounds.rows}
    cams_dbc = D("CinematicCamera")
    narration_rows, cam_sql, seq_sql = [], [], []
    flights = intro_flights(story, naga)
    for race in RACE_IDS:
        sound = values_of(sounds, snd_rows[3840], snt)      # HumanFlyByNarration
        sound[0], sound[2] = ID_NARRATION[race], f"{NAME[race]}FlyByNarration"
        sound[3:13] = [f"{NAME[race]}Narration.wav"] + [""] * 9
        sound[13:23] = [1] + [0] * 9
        sound[23] = "Sound\\CinematicVoices"
        client.put("SoundEntries", snt, sound)
        narration_rows.append(sound)
        origin, keys = flights[race]
        m2, skin = cameras.write(f"Flyby{NAME[race]}", camera_keys(keys), origin)
        folder = os.path.join(MODULE, "data", "client", "Cameras")
        os.makedirs(folder, exist_ok=True)
        open(os.path.join(folder, f"Flyby{NAME[race]}.m2"), "wb").write(m2)
        open(os.path.join(folder, f"Flyby{NAME[race]}00.skin"), "wb").write(skin)
        cam = [ID_CAMERA[race], f"Cameras\\Flyby{NAME[race]}.mdx", ID_NARRATION[race], origin[0], origin[1], origin[2], 0.0]
        client.put("CinematicCamera", TYPES["cinematiccamera_dbc"], cam)
        cam_sql.append(cam)
        s = [ID_SEQUENCE[race], 0, ID_CAMERA[race]] + [0] * 7
        client.put("CinematicSequences", "i" * 10, s)
        seq_sql.append(s)
    assert cams_dbc.rows
    sql.comment("The intros: a flight over each race's home, with its own narration (put together by the patch from the game's\n"
                "sounds: data/client/narration.txt).")
    sql.replace_dbc("soundentries_dbc", snt, narration_rows)
    sql.replace_dbc("cinematiccamera_dbc", TYPES["cinematiccamera_dbc"], cam_sql)
    sql.replace_dbc("cinematicsequences_dbc", TYPES["cinematicsequences_dbc"], seq_sql)
    write_narration()

    # Homes, people, quests ------------------------------------------------------------------------
    homes(client, sql, W)
    __import__("naga_assets").add_naga_assets(client, sql, D)   # the naga's story's voices and looks (tools/naga_assets.py)

    # The world database: starts, skills, stats, standing ------------------------------------------
    sql.comment("Where they start: each race at its story's start (the murlocs in the Wrathtail's pens at the Zoram Strand, the naga\n"
                "at Rethress Sanctum in Azshara), every class.")
    elder = ground(next(p for p in C.MURLOC_PEOPLE if p[0] == "elder")[4])
    szaria = ground(next(p for p in C.NAGA_PEOPLE if p[0] == "szaria")[4])
    start = {MURLOC: (C.MAP, C.DARKSHORE, elder[0] + 4.0, elder[1], None, 4.71), NAGA: (C.MAP, C.DARKSHORE, szaria[0] - 5.0, szaria[1], None, 0.0)}
    for race, st in ((MURLOC, story), (NAGA, naga)):      # (each story's first chapter's)
        if st and st.tables.get("_start"):
            s_ = st.tables["_start"]
            start[race] = (s_["map"], s_["zone"], s_["x"], s_["y"], s_["z"], s_["o"])
    out = []
    for race in RACE_IDS:
        m, zone, x, y, z, o = start[race]
        z = terrain.height(x, y, m) + 0.5 if z is None else z
        for cls in CLASSES_OF[race]:
            out.append(f"({race}, {cls}, {m}, {zone}, {x:.2f}, {y:.2f}, {z:.2f}, {o})")
    sql.raw(f"DELETE FROM `playercreateinfo` WHERE `race` IN ({MURLOC}, {NAGA});")
    sql.raw("INSERT INTO `playercreateinfo` (`race`, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`) VALUES\n"
            + ",\n".join(out) + ";")

    racial_spells = {r[2] for r in D("SkillLineAbility").rows if r[1] in racial_lines}
    sql.comment("Their action bars: their class's template race's, without that race's racials; their own on the bar.")
    acts = W("playercreateinfo_action")
    out = []
    active = {MURLOC: SPELLS["mrrgglll"], NAGA: SPELLS["tail_sweep"]}
    for race in RACE_IDS:
        for cls in CLASSES_OF[race]:
            used = set()
            for r in acts:
                if int(r["race"]) == TEMPLATE[race][cls] and int(r["class"]) == cls and not (int(r["type"]) == 0 and int(r["action"]) in racial_spells):
                    out.append(f"({race}, {cls}, {r['button']}, {r['action']}, {r['type']})")
                    used.add(int(r["button"]))
            button = next(b for b in range(2, 12) if b not in used)
            out.append(f"({race}, {cls}, {button}, {active[race]}, 0)")
    sql.raw(f"DELETE FROM `playercreateinfo_action` WHERE `race` IN ({MURLOC}, {NAGA});")
    sql.raw("INSERT INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`) VALUES\n" + ",\n".join(out) + ";")

    sql.comment("Their skills: their side's weapons and armour; Common or Orcish; no other race's racials (rows found by their\n"
                "stock races, the low eleven bits, as the other race modules find them).")
    for r in W("playercreateinfo_skills"):
        mask, skill = int(r["raceMask"]), int(r["skill"])
        if mask == 0:
            continue
        add = side_bits(mask, skill)
        if add:
            sql.raw(f"UPDATE `playercreateinfo_skills` SET `raceMask` = `raceMask` | {add} WHERE (`raceMask` & 2047) = {mask & 2047} "
                    f"AND `classMask` = {r['classMask']} AND `skill` = {skill};")
    nerglish_language(client, sql, D, COMMON, TITAN)

    sql.comment("Their racials, learned at creation.")
    sql.raw(f"DELETE FROM `playercreateinfo_spell_custom` WHERE `Spell` BETWEEN {min(SPELLS.values())} AND {max(SPELLS.values())};")
    custom = [(BIT[MURLOC], SPELLS["amphibious"], "Murloc - Amphibious"), (BIT[MURLOC], SPELLS["mrrgglll"], "Murloc - Mrrgglll!"),
              (BIT[MURLOC], SPELLS["slippery"], "Murloc - Slippery"),
              (BIT[NAGA], SPELLS["serpent"], "Naga - Serpent's Grace"), (BIT[NAGA], SPELLS["tail_sweep"], "Naga - Tail Sweep"),
              (BIT[NAGA], SPELLS["scales"], "Naga - Scales of the Deep")]
    sql.raw("INSERT INTO `playercreateinfo_spell_custom` (`racemask`, `classmask`, `Spell`, `Note`) VALUES\n"
            + ",\n".join(f"({m}, 0, {s}, {q(n)})" for m, s, n in custom) + ";")
    # (this file's rows only: the murlocs' story's SQL puts their phase in its other zones, the naga's story's SQL the naga's
    # own; the naga's Darkshore phase is retired with their camp)
    sql.raw(f"DELETE FROM `spell_area` WHERE (`spell` = {SPELLS['phase_murloc']} AND `area` IN ({C.DARKSHORE}, {C.ASHENVALE})) "
            f"OR `spell` IN ({SPELLS['phase_naga']}, {SPELLS['phase_murloc_alone']});")
    # (a zone of the murlocs' story that shows their phase alone until a quest's done: the world's and theirs after)
    alone = {zone: quest for zones, quest in (story.tables.get("_alone", []) if story else []) for zone in zones}
    phase_rows = [f"({SPELLS['phase_' + k]}, {area}, {alone.get(area, 0) if race == MURLOC else 0}, 0, 0, {BIT[race]}, 2, 1, 64, 11)"
                  for k, race in (("murloc", MURLOC), ("naga", NAGA)) for area in (C.DARKSHORE, C.ASHENVALE)
                  if race == MURLOC or C.NAGA_CAMP]
    # (the end quest's status: the spell is given while it's one of these: not yet rewarded)
    phase_rows += [f"({SPELLS['phase_murloc_alone']}, {area}, 0, {quest}, 0, {BIT[MURLOC]}, 2, 1, 64, 63)" for area, quest in sorted(alone.items())]
    sql.raw("INSERT INTO `spell_area` (`spell`, `area`, `quest_start`, `quest_end`, `aura_spell`, `racemask`, `gender`, `autocast`, "
            "`quest_start_status`, `quest_end_status`) VALUES\n" + ",\n".join(phase_rows) + ";")
    towns = sorted({r[0] for r in D("AreaTable").rows if r[4] & TOWN_FLAG} | set(LOW_PROFILE_OUTPOSTS))
    sql.comment(f"A murloc keeps a low profile in the {len(towns)} towns and cities (Low Profile): their guards notice it at a few yards.")
    sql.raw(f"DELETE FROM `spell_area` WHERE `spell` = {SPELLS['low_profile']};")
    sql.raw("INSERT INTO `spell_area` (`spell`, `area`, `quest_start`, `quest_end`, `aura_spell`, `racemask`, `gender`, `autocast`, "
            "`quest_start_status`, `quest_end_status`) VALUES\n"
            + ",\n".join(f"({SPELLS['low_profile']}, {area}, 0, 0, 0, {BIT[MURLOC]}, 2, 1, 64, 11)" for area in towns) + ";")

    sql.comment("Their stats: their kin's.")
    stats = {int(r["Race"]): r for r in W("player_race_stats")}
    sql.raw("REPLACE INTO `player_race_stats` (`Race`, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`) VALUES\n"
            + ",\n".join(f"({race}, " + ", ".join(stats[STATS_FROM[race]][k] for k in ("Strength", "Agility", "Stamina", "Intellect", "Spirit")) + ")"
                         for race in RACE_IDS) + ";")

    sql.comment("Quests, items and conditions of their kin are theirs too: the night elves' for the murlocs, the trolls' (the\n"
                "Horde's) for the naga (each story's gate, src/MurlocNaga.cpp, closes them until its last quest is done).")
    for race in RACE_IDS:
        b, s = BIT[race], 1 << (KIN[race] - 1)
        sql.raw(f"UPDATE `quest_template` SET `AllowableRaces` = `AllowableRaces` | {b} WHERE `AllowableRaces` & {s} AND `AllowableRaces` & 0x7FFFFFFF <> 0x7FFFFFFF AND `ID` NOT BETWEEN {C.QUEST_BASE} AND {C.QUEST_BASE + 99};")
        sql.raw(f"UPDATE `item_template` SET `AllowableRace` = `AllowableRace` | {b} WHERE `AllowableRace` <> -1 AND `AllowableRace` & {s} AND `AllowableRace` & 0x7FFFFFFF <> 0x7FFFFFFF;")
        sql.raw(f"UPDATE `conditions` SET `ConditionValue1` = `ConditionValue1` | {b} WHERE `ConditionTypeOrReference` = 16 AND `ConditionValue1` & {s};")
    sql.comment("The naga's retired Darkshore start, undone where a realm had it: the Alliance's own Darkshore quests it opened to\n"
                "them, and the conditions that closed the way out of Darkshore to them.")
    sql.raw(f"UPDATE `quest_template` SET `AllowableRaces` = `AllowableRaces` & ~{BIT[NAGA]} WHERE `ID` IN "
            f"({', '.join(str(x) for x in C.RETIRED_DARKSHORE_ALLIANCE_ONLY)}) AND (`AllowableRaces` & {1 << (KIN[NAGA] - 1)}) = 0;")
    sql.raw(f"DELETE FROM `conditions` WHERE `SourceTypeOrReferenceId` = 19 AND `ConditionTypeOrReference` = 16 AND `ConditionValue1` = {BIT[NAGA]} "
            f"AND `NegativeCondition` = 1 AND `SourceEntry` IN ({', '.join(str(x) for x in C.RETIRED_NAGA_CLOSED)}) "
            "AND `Comment` = 'mod-murloc-naga: not for the naga (it leads out of Darkshore to the Alliance)';")

    # Write ------------------------------------------------------------------------------------------
    with open(os.path.join(MODULE, "data", "sql", "chromiecraft", "world", "murloc_naga_world.sql"), "w", newline="\n") as f:
        f.write("\n".join(sql.parts) + "\n")
    for st, profile in ((story, "MURLOC"), (naga, "NAGA")):
        write_story(st, getattr(story_compiler(), profile), client)
    client.write(os.path.join(MODULE, "data", "client", "dbc"))
    print(f"{len(new_sections)} looks, {len(client.files)} tables, {len(spell_rows)} spells"
          + (f", the murlocs' story: {len(story.tables.get('quest_template', []))} quests" if story else "")
          + (f", the naga's story: {len(naga.tables.get('quest_template', []))} quests" if naga else ""))


def write_story(st, P, client):
    """A story's SQL (data/sql/chromiecraft/world/<its file>), its rows of the game's tables (the patch's: its items,
    object looks and new looks) and the server test's steps for it (warcraft/server/<its steps file>, from its
    test.steps written with the story's names)."""
    S = story_compiler()
    path = os.path.join(MODULE, "data", "sql", "chromiecraft", "world", P.sql_file)
    if not st:
        if os.path.exists(path):
            os.remove(path)
        return
    for row in st.client.get("Item", []):
        client.put("Item", "iiiiiiii", row)
    gdt = "isiiiiiiiiiiffffffi"
    for row in st.client.get("GameObjectDisplayInfo", []):
        client.put("GameObjectDisplayInfo", gdt, row)
    for row in st.client.get("CreatureDisplayInfo", []):
        client.put("CreatureDisplayInfo", "iiiifissssiiiiii", row)
    for row in st.client.get("CreatureDisplayInfoExtra", []):
        client.put("CreatureDisplayInfoExtra", "i" * 20 + "s", row)
    displays = st.client.get("GameObjectDisplayInfo", [])
    extra = ""
    if displays:
        extra = ("INSERT INTO `gameobjectdisplayinfo_dbc` (`ID`, `ModelName`, `Sound_1`, `Sound_2`, `Sound_3`, `Sound_4`, `Sound_5`, "
                 "`Sound_6`, `Sound_7`, `Sound_8`, `Sound_9`, `Sound_10`, `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`, `GeoBoxMaxX`, "
                 "`GeoBoxMaxY`, `GeoBoxMaxZ`, `ObjectEffectPackageID`) VALUES\n"
                 + ",\n".join(f"({r[0]}, {q(r[1])}, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, 0, 1, 1, 3, 0)" for r in displays) + ";")
    head = f"DELETE FROM `gameobjectdisplayinfo_dbc` WHERE `ID` BETWEEN {P.GO_DISPLAY_BASE} AND {P.GO_DISPLAY_END};\n"
    with open(path, "w", newline="\n") as f:
        f.write(S.sql(st.tables, head + extra, P))
    template = os.path.join(P.folder, "test.steps")
    if os.path.exists(template):
        with open(os.path.join(MODULE, "..", "..", "server", P.steps_file), "w", newline="\n") as f:
            f.write(st.resolve(open(template).read()))


def nerglish_language(client, sql, D, common, titan):
    """The murlocs' own language: the game's Titan (no player race speaks it), named Nerglish, its
    words murloc words (Blizzard's translator's, from Titan's own), the murlocs' alone; and no Common
    (earlier releases gave them Common: the Alliance's words, which a murloc doesn't know)."""
    sql.comment("Their language: Nerglish (the game's Titan, renamed in the patch), not Common.")
    sql.raw(f"UPDATE `playercreateinfo_skills` SET `raceMask` = `raceMask` & ~{BIT[MURLOC]} WHERE `skill` = {common};")
    sql.raw(f"REPLACE INTO `playercreateinfo_skills` (`raceMask`, `classMask`, `skill`, `rank`, `comment`) VALUES "
            f"({BIT[MURLOC]}, 0, {titan}, 0, 'Murloc - Language: Nerglish');")
    import nerglish
    langs = D("Languages")
    row = next(r for r in langs.rows if r[0] == C.NERGLISH_LANGUAGE)
    client.put("Languages", "i" + "s" * 16 + "i", [row[0], "Nerglish"] + [""] * 15 + [row[17]])
    words = D("LanguageWords")
    for r in words.rows:
        if r[1] == C.NERGLISH_LANGUAGE:
            client.put("LanguageWords", "iis", [r[0], r[1], nerglish.word(words.s(r[2])).lower()])
    lines = D("SkillLine")
    row = next(r for r in lines.rows if r[0] == titan)
    types = "iii" + "s" * 16 + "i" + "s" * 16 + "i" + "i" + "s" * 16 + "i" + "i"
    v = values_of(lines, row, types)
    v[3], v[20] = "Language: Nerglish", "The murlocs' tongue."
    client.put("SkillLine", types, v)


WORLD_CACHE = {}


def story_compiler():
    sys.path.insert(0, os.path.join(HERE, "murloc"))
    import compile as story_compile
    return story_compile


def cached_world(W):
    def world(name):
        if name not in WORLD_CACHE:
            WORLD_CACHE[name] = W(name)
        return WORLD_CACHE[name]
    return world


def murloc_story(D, W):
    """The murlocs' questline (tools/murloc/ch*.py) compiled (tools/murloc/compile.py), or None while it
    has no chapters."""
    S = story_compiler()
    chapters = S.load(upto=C.MURLOC_CHAPTERS)
    if not chapters:
        return None
    story = S.Story(chapters, cached_world(W), D, lambda m, x, y: terrain.height(x, y, m),
                    race_phase_spell=SPELLS["phase_murloc"], area=lambda m, x, y: terrain.area(x, y, m), profile=S.MURLOC)
    story.tables, story.client = story.build()
    return story


def naga_story(D, W, murlocs):
    """The naga's questline (tools/naga/ch*.py), compiled after the murlocs' and clear of their phases (the bits their
    people carry in each zone, Azshara above all), then both checked: neither race sees the other's people. None while
    it has no chapters."""
    S = story_compiler()
    chapters = S.load(S.NAGA.folder, upto=C.NAGA_CHAPTERS, prefix="naga")
    if not chapters:
        return None
    story = S.Story(chapters, cached_world(W), D, lambda m, x, y: terrain.height(x, y, m),
                    area=lambda m, x, y: terrain.area(x, y, m), profile=S.NAGA,
                    reserved=S.bits_by_zone(murlocs) if murlocs else None, water=lambda m, x, y: terrain.liquid(x, y, m))
    story.tables, story.client = story.build()
    problems = S.check_apart([murlocs, story]) if murlocs else []
    if problems:
        sys.exit("the murlocs' and the naga's phases cross:\n  " + "\n  ".join(problems[:40]))
    warnings = S.lint(story)
    print(f"the naga's story: {len(warnings)} lint warnings" + "".join(f"\n  {w}: {what}" for w, what in warnings[:60]))
    return story


# The intros ---------------------------------------------------------------------------------------

def intro_flights(story=None, naga=None):
    """Each race's flight: (origin, [(ms, place, height, target)]): the murlocs' from the open sea
    over the pens (their story's start: the old village's elder before it) to where they stand (about
    42 s); the naga's (61 s, Lady Vashj's words, then the sea and the crèche's horn: bible 18.1) over
    the Bay of Storms, south along Southridge Beach, up past the Ravencrest Monument on its cliffs and
    down over the sea to Rethress Sanctum, where a new naga stands (their story's start; the retired
    camp's island north of Auberdine before it)."""
    vx, vy = C.VILLAGE
    elder = ground(next(p for p in C.MURLOC_PEOPLE if p[0] == "elder")[4])
    pens = story and story.tables.get("_start") and story.tables["_start"]["map"] == C.MAP
    if pens:
        s_ = story.tables["_start"]
        vx, vy = s_["x"], s_["y"]
        elder = (s_["x"], s_["y"], s_["z"])
        # the pens: in from the sea to the west, high over the stockade, round it, down into the line of slaves
        murloc = [
            (0, (vx - 30, vy + 260), 34.0, (vx, vy)),
            (6000, (vx - 10, vy + 160), 24.0, (vx, vy)),
            (12000, (vx + 5, vy + 70), 16.0, (vx, vy)),
            (17000, (vx + 40, vy + 35), 16.0, (vx - 5, vy + 10)),
            (22000, (vx + 55, vy - 10), 18.0, (vx, vy + 5)),
            (27000, (vx + 30, vy - 50), 30.0, (vx - 5, vy + 10)),
            (31000, (vx - 25, vy - 45), 30.0, (vx, vy + 10)),
            (35000, (vx - 50, vy), 14.0, (vx, vy + 5)),
            (39000, (elder[0] - 12, elder[1] + 6), 5.0, (elder[0], elder[1], elder[2] + 1.0)),
            (42000, (elder[0] - 7, elder[1] + 3), 3.5, (elder[0], elder[1], elder[2] + 1.0)),
        ]
    else:
        murloc = None
    murloc = murloc or [
        (0, (vx - 30, vy + 260), 32.0, (vx, vy)),
        (6000, (vx - 10, vy + 160), 20.0, (vx, vy)),
        (12000, (vx + 5, vy + 70), 8.0, (vx, vy)),
        (17000, (vx + 40, vy + 35), 9.0, (vx - 5, vy + 10)),
        (22000, (vx + 55, vy - 10), 12.0, (vx, vy + 5)),
        (27000, (vx + 30, vy - 50), 30.0, (vx - 5, vy + 10)),
        (31000, (vx - 25, vy - 45), 30.0, (vx, vy + 10)),
        (35000, (vx - 50, vy), 9.0, (vx, vy + 5)),
        (39000, (elder[0] - 12, elder[1] + 6), 4.0, (elder[0], elder[1], elder[2] + 1.0)),
        (42000, (elder[0] - 7, elder[1] + 3), 3.0, (elder[0], elder[1], elder[2] + 1.0)),
    ]
    cx, cy = C.CAMP
    szaria = ground(next(p for p in C.NAGA_PEOPLE if p[0] == "szaria")[4])
    ix, iy = C.INFILTRATORS[0]
    if naga and naga.tables.get("_start") and naga.tables["_start"]["map"] == C.MAP:
        s_ = naga.tables["_start"]
        nx, ny, nz = s_["x"], s_["y"], s_["z"]
        monument = (2425.0, -6831.0, 116.0)            # the Ravencrest Monument (the broken colossus on the cliffs)
        flight = [                                  # (heights over the cliffs given as they are: the camera stays above them)
            (0, (3180, -6960, 60.0), 0.0, (2800, -6800)),
            (8000, (2930, -6900, 80.0), 0.0, (2600, -6820)),
            (16000, (2700, -6880, 170.0), 0.0, monument),
            (23000, (2520, -6800, 175.0), 0.0, monument),
            (29000, (2400, -6720, 170.0), 0.0, monument),
            (35000, (2230, -6720, 150.0), 0.0, (2120, -6560)),
            (41000, (2100, -6660, 60.0), 0.0, (nx, ny)),
            (47000, (2110, -6560, 22.0), 0.0, (nx, ny)),
            (53000, (2150, -6495), 10.0, (nx, ny, nz + 1.5)),
            (58000, (nx - 18, ny - 14), 5.0, (nx, ny, nz + 1.5)),
            (61000, (nx - 9, ny - 7), 3.0, (nx, ny, nz + 1.5)),
        ]
        return {MURLOC: ((float(vx), float(vy), 0.0), murloc), NAGA: ((float(nx), float(ny), 0.0), flight)}
    naga = [
        (0, (7350, 1150), 40.0, (7100, 900)),
        (10000, (7150, 1000), 30.0, (ix, iy)),
        (19000, (ix + 20, iy + 40), 45.0, (ix, iy)),
        (27000, (6950, 760), 40.0, (cx, cy)),
        (35000, (6840, 720), 26.0, (6450, 500)),
        (43000, (6780, 860), 28.0, (cx, cy)),
        (50000, (cx + 30, cy + 35), 14.0, (cx, cy)),
        (56000, (szaria[0] + 14, szaria[1] + 6), 5.0, (szaria[0], szaria[1], szaria[2] + 2.0)),
        (61000, (szaria[0] + 8, szaria[1] + 2), 3.5, (szaria[0], szaria[1], szaria[2] + 2.0)),
    ]
    return {MURLOC: ((float(vx), float(vy), 0.0), murloc), NAGA: ((float(cx), float(cy), 0.0), naga)}


# Lady Vashj's words, as the naga's narration (bible 18.1, re-cut: no spoiler of her death, which is their
# story's end): the game's own lines (Serpentshrine Cavern's), who the naga were and what they wanted (Intro01)
# and their war against the surface (Phase01, Aggro04, Phase02, BowShot02, Aggro02); then the present, where the
# story starts: the sea off Rethress Sanctum, the crèche's horn, and far off in the deep a siren's hiss.
# (ms from the intro's start, the game's file.)
VASHJ = "Sound\\Creature\\LadyVashj\\COIL_LadyVashj_"
NARRATION = {
    "Naga": [(500, VASHJ + "Intro01.wav"), (20500, VASHJ + "Phase01.wav"), (30000, VASHJ + "Aggro04.wav"),
             (33500, VASHJ + "Phase02.wav"), (38500, VASHJ + "BowShot02.wav"), (42500, VASHJ + "Aggro02.wav"),
             (46500, "Sound\\Ambience\\Water\\OceanA.wav"), (51500, "Sound\\Doodad\\HornGoober.wav"),
             (57000, "Sound\\Creature\\NagaFemale\\NagaFemalePreAggro.wav")],
    # The pens at the Zoram Strand (the murlocs' story's start): the sea, chains, the count gong, a whip and
    # a slave's yelp, a fry, the sea witch's hiss, the gong again; and at the very end, far off, one murloc's
    # war-gurgle (the cry the naga lash singers for).
    "Murloc": [(300, "Sound\\Ambience\\Water\\OceanA.wav"), (3500, "Sound\\Item\\FoleySounds\\ChainFoley01.wav"),
               (7000, "Sound\\Doodad\\G_GongTroll01.wav"), (11000, "Sound\\Item\\Weapons\\Whip\\BullWhipHit1.wav"),
               (11600, "Sound\\Creature\\Murloc\\mMurlocWoundA.wav"),
               (15500, "Sound\\Creature\\BabyMurloc\\BabyMurlocA.wav"), (19000, "Sound\\Item\\FoleySounds\\ChainFoley01.wav"),
               (22500, "Sound\\Creature\\NagaFemale\\NagaFemalePreAggro.wav"), (26500, "Sound\\Item\\Weapons\\Whip\\BullWhipHit1.wav"),
               (27200, "Sound\\Creature\\Murloc\\mMurlocWoundB.wav"), (24000, "Sound\\Ambience\\Water\\OceanA.wav"),
               (31500, "Sound\\Creature\\BabyMurloc\\BabyMurlocC.wav"), (34000, "Sound\\Doodad\\G_GongTroll01.wav"),
               (38500, "Sound\\Creature\\Murloc\\mMurlocAggroOld.wav")],
}


def write_narration():
    lines = ["# The intros' narrations: the game's own sounds, each at its moment (ms), mixed into one file by the patch",
             "# (Sound\\CinematicVoices\\<Race>Narration.wav). <race>\t<ms>\t<the game's file>"]
    for race, parts in NARRATION.items():
        for ms, path in parts:
            lines.append(f"{race}\t{ms}\t{path}")
    open(os.path.join(MODULE, "data", "client", "narration.txt"), "w", newline="\n").write("\n".join(lines) + "\n")


# Homes, people, things, quests ----------------------------------------------------------------

def homes(client, sql, W):
    templates = {r["entry"]: r for r in W("creature_template")}
    npc_ids, go_ids, item_ids = {}, {}, {}
    creatures, models, spawns, texts, menus, vendor = [], [], [], [], [], []
    gos, go_spawns, go_loot, cr_loot, go_displays = [], [], [], [], []
    spawn = [C.SPAWN_BASE]
    go_spawn = [C.GO_SPAWN_BASE]
    next_npc = [C.NPC_BASE]
    next_go = [C.GO_BASE]
    next_text = [C.TEXT_BASE]

    def text(words):
        tid = next_text[0]
        next_text[0] += 1
        texts.append((tid, words, words, 1))
        return tid

    def npc(key, name, subname, look, level, faction, npcflag=0, unit_class=1, rank=0, health=1.0, ai="", flags_extra=0,
            unit_flags=0, scale=1.0, gossip=None, loot=False, damage=1.0, speed_run=1.14286):
        entry = next_npc[0]
        next_npc[0] += 1
        npc_ids[key] = entry
        menu = 0
        if gossip:
            menu = entry
            menus.append((menu, text(gossip)))
        lo, hi = level if isinstance(level, tuple) else (level, level)
        creatures.append((entry, name, subname or "", menu, lo, hi, faction, npcflag, 1.0, speed_run, 1.0, unit_class, unit_flags,
                          7, flags_extra, rank, health, 1.0, 1.0, damage, 2000, 2000, entry if loot else 0, 1, ai, ""))
        models.append((entry, 0, C.LOOK.get(look, look), scale, 1))
        return entry

    def place(entry, where, o, phase, wander=0.0, respawn=300, comment=""):
        x, y, z = ground(where)
        spawns.append((spawn[0], entry, C.MAP, 0, 0, 1, phase, round(x, 2), round(y, 2), round(z, 2), o, respawn, wander,
                       1 if wander else 0, comment))
        spawn[0] += 1

    def go_display(path):
        did = ID_GO_DISPLAY + len(go_displays)
        go_displays.append((did, path))
        return did

    def go_template(key, kind, display, name, size=1.0, data=None):
        entry = next_go[0]
        next_go[0] += 1
        go_ids[key] = entry
        d = (data or []) + [0] * (24 - len(data or []))
        gos.append((entry, kind, display, name, size) + tuple(d))
        return entry

    def go_place(entry, where, o, phase, respawn=120, comment=""):
        x, y, z = ground(where)
        r = rotation(o)
        go_spawns.append((go_spawn[0], entry, C.MAP, 0, 0, 1, phase, round(x, 2), round(y, 2), round(z, 2), o,
                          r[0], r[1], r[2], r[3], respawn, 100, 1, comment))
        go_spawn[0] += 1

    # Quest items and rewards (the client learns them from the patch's Item table too).
    items = []
    for n, (key, name, look, stack) in enumerate(C.ITEMS):
        iid = C.ITEM_BASE + n
        item_ids[key] = iid
        items.append(dict(entry=iid, cls=12, sub=0, name=name, display=look, quality=1, bonding=4, stack=stack, maxcount=stack,
                          inv=0, level=1, req=0, stats=[], armor=0, material=-1))
    for n, (key, name, look, inv, cls, sub, quality, level, stats, armor) in enumerate(C.REWARDS):
        iid = C.ITEM_BASE + 50 + n
        item_ids[key] = iid
        items.append(dict(entry=iid, cls=cls, sub=sub, name=name, display=look, quality=quality, bonding=1, stack=1, maxcount=0,
                          inv=inv, level=level, req=level - 5, stats=stats, armor=armor, material=7 if inv == 16 else 1 if cls == 2 else 4))
    item_ids[C.THRESHER_EYE] = C.THRESHER_EYE

    def item_of(key):
        return item_ids[key] if not isinstance(key, int) else key

    MP, NP = C.PHASE[C.MURLOC], C.PHASE[C.NAGA]
    # The murlocs' village.
    gossip = {
        "elder": "Mrrgl. Mrgl mrgl mrrrrgl.$B$B(The elder leans on his staff and watches the elves' lights across the water.)",
        "chief": "(Grrmlgrrl doesn't look up from his spear. He grunts.)",
        "cook": "(Murlorga offers you a ladle of something grey. It moves.)$B$BMrgl?",
        "snatcher": "(Blrrgl hides something behind his back, very fast.)$B$Bmrgl...",
        "oracle": "Mmmmrrrrgllll...$B$B(Oracle Glubbub stares straight through you, at something far out at sea.)",
        "fishmonger": "(Mrrlglr slaps a fish on the counter and points at it, then at your coin pouch.)$B$BMrgl!",
        "sloshy": "(Sloshy hiccups.)",
    }
    roles = {"quest": 2, "vendor": 128 | 1, "ambient": 0, "fry": 0}
    # The retired village (MURLOC_VILLAGE False) is still made, then its rows are taken out: its ids
    # stay taken, so the naga's people and things after it keep the ids they've always had.
    village_lists = (creatures, models, spawns, menus, vendor, gos, go_spawns, go_loot, cr_loot)
    village_at = [len(lst) for lst in village_lists]

    def retire_village():
        if not C.MURLOC_VILLAGE:
            for lst, n in zip(village_lists, village_at):
                del lst[n:]
    if True:
        for key, name, sub, look, where, o, role in C.MURLOC_PEOPLE + [C.SLOSHY]:
            flag = roles[role] | (1 if key in gossip else 0)
            e = npc(key, name, sub, look, (1, 1) if role == "fry" else (12, 13), 35, flag, unit_class=2 if key in ("elder", "oracle", "cook") else 1,
                    gossip=gossip.get(key), scale=0.5 if role == "fry" else 1.0, ai="SmartAI" if key in VOICED else "")
            place(e, where, o, MP, wander=4.0 if role in ("ambient", "fry") else 0.0, comment=f"mod-murloc-naga: {name}")
        vendor += [(npc_ids["fishmonger"], i, item) for i, item in enumerate((787, 4592, 4593, 4594, 159, 1179))]
        raider = npc("raider", "Stormscale Raider", None, "naga_male", (11, 12), 74, unit_class=1)
        models.append((raider, 1, C.LOOK["siren"], 1.0, 1))
        for i, where in enumerate(C.RAIDERS):
            place(raider, where, (i * 1.3) % 6.28, MP, wander=4.0, comment="mod-murloc-naga: the murlocs' enemies")
        sssilith = npc("sssilith", "Tidecaller Sssilith", None, "naga_lord", 13, 74, unit_class=2, health=3.0, damage=1.5, loot=True)
        place(sssilith, C.SSSILITH, 3.0, MP, comment="mod-murloc-naga: the raiders' leader")
        cr_loot.append((sssilith, item_ids["trident"], 100))
        for where in C.CRAWLERS:
            place(C.PYGMY_TIDE_CRAWLER, where, 0.0, MP, wander=5.0, respawn=90, comment="mod-murloc-naga: the village's crawlers")
        trigger = npc("summit", "Island Summit", None, 11686, 1, 35, ai="SmartAI", flags_extra=128, unit_flags=0x02000000 | 0x200)
        vx, vy = C.VILLAGE
        peak = summit((6265, 925), 20)
        place(trigger, peak, 0.0, MP, comment="mod-murloc-naga: the oracle's vision")
        for path, name, where, o, scale in C.MURLOC_THINGS:
            go_place(go_template(name + str(len(gos)), 5, go_display(path), name, scale), ground(where), o, MP, respawn=0,
                     comment=f"mod-murloc-naga: {name}")
        altar_path, altar_name, altar_where, altar_o, altar_scale = C.ALTAR
        altar = go_template("altar", 2, go_display(altar_path), altar_name, altar_scale, [0, 0, 0, 0, 0, 0])
        go_place(altar, ground(altar_where), altar_o, MP, respawn=0, comment="mod-murloc-naga: the Murloc Altar")
    retire_village()

    def chest(key, name, display, item, quest, places, phase, size=1.0):
        entry = go_template(key, 3, display, name, size, [259, 0, 0, 1, 0, 0, 0, 0, quest])
        gos[-1] = gos[-1][:6] + (entry,) + gos[-1][7:]         # its loot is its own entry
        go_loot.append((entry, item, 100))
        for where in places:
            go_place(entry, where, 0.0, phase, comment=f"mod-murloc-naga: {name}")
        return entry

    murloc_quest_id = {qd["n"]: C.QUEST_BASE + qd["n"] for qd in C.MURLOC_QUESTS}
    naga_quest_id = {qd["n"]: C.QUEST_BASE + qd["n"] for qd in C.NAGA_QUESTS}
    village_at = [len(lst) for lst in village_lists]
    if True:
        shore = sea_floor_ring(C.VILLAGE, 16, 48, 0.4, 6.0, 12, 0.3)
        deep = sea_floor_ring(C.VILLAGE, 25, 85, 4.0, 16.0, 18, 1.1)
        chest("mussels", "Mussel Cluster", 261, item_ids["mussel"], murloc_quest_id[2], shore, MP, 0.6)
        chest("kelp", "Fresh Kelp", 267, item_ids["kelp"], murloc_quest_id[7], deep[:9], MP)
        chest("coral", "Glowing Coral", 887, item_ids["coral"], murloc_quest_id[10], deep[9:], MP, 0.5)
        clam = sea_floor_ring((vx - 10, vy + 30), 70, 130, 12, 30, 1, 2.0)
        chest("clam", "Giant Clam", 261, item_ids["pearl"], murloc_quest_id[13], clam, MP, 2.0)
        chest("crates", "Unattended Crate", 2, item_ids["trinket"], murloc_quest_id[3], C.TRINKET_CRATES, MP, 0.8)
        chest("bread", "Basket of Sweet Rolls", 10, item_ids["roll"], murloc_quest_id[4], C.BREAD_BASKETS, MP, 0.6)
        chest("lures", "Box of Shiny Lures", 2, item_ids["lures"], murloc_quest_id[12], [C.LURE_BOX], MP, 0.5)
    retire_village()
        # (Darkshore's threshers drop the Thresher Eye already, for those whose quests need it: Buzzbox 411's)

    # The naga's camp: retired as the village was (made, then its rows taken out: its ids stay taken). Lady Szaria,
    # Myrmidon Ssaveth and Vyssa the Coral-Keeper keep their entries: the naga's story's people (tools/naga/ch0_*.py,
    # naga_story.sql), whose rows this file leaves alone.
    camp_at = [len(lst) for lst in village_lists]
    camp_keys = set(npc_ids)
    village_keys = set(npc_ids) if not C.MURLOC_VILLAGE else set()
    gossip.update({
        "szaria": "We were the Stormscale's, once, and before that Queen Azshara's. Now we are no one's but our own.$B$BThe night elves across the water have no reason to trust us. Give them one. And when they have taught you all they will, go south to the Grove of the Ancients: the old one there, Onu, hears what the sea says. He will know where your path goes next.",
        "ssaveth": "I watch the north. They will come from the north.",
        "vyssa": "Coral, kelp, fresh water from the island's spring. It is not the palaces of Zin-Azshari. It will do.",
        "scout": "Keep your head down, mon. Dem Wrathtail got eyes all over dis beach.",
    })
    for key, name, sub, look, where, o, role in C.NAGA_PEOPLE:
        flag = roles[role] | (1 if key in gossip else 0)
        e = npc(key, name, sub, look, (14, 15) if role == "quest" else (12, 13), 35, flag, unit_class=2 if look in ("siren", "sorceress", "sea_witch") else 1,
                gossip=gossip.get(key), ai="SmartAI" if key in VOICED else "")
        place(e, where, o, NP, comment=f"mod-murloc-naga: {name}")
    vendor += [(npc_ids["vyssa"], i, item) for i, item in enumerate((159, 1179, 787, 4592, 4593, 4540))]
    infiltrator = npc("infiltrator", "Stormscale Infiltrator", None, "naga_male", (10, 11), 74, unit_class=1, loot=True)
    models.append((infiltrator, 1, C.LOOK["siren"], 1.0, 1))
    for i, where in enumerate(C.INFILTRATORS):
        place(infiltrator, where, (i * 1.7) % 6.28, NP, wander=4.0, comment="mod-murloc-naga: the naga's hunters")
    cr_loot.append((infiltrator, item_ids["orders"], 65))
    for path, name, where, o, scale in C.NAGA_THINGS:
        go_place(go_template(name + str(len(gos)), 5, go_display(path), name, scale), ground(where), o, NP, respawn=0,
                 comment=f"mod-murloc-naga: {name}")
    key, name, sub, look, where, o, role = C.SCOUT
    scout = npc(key, name, sub, look, 30, 126, 2 | 1, gossip=gossip["scout"])
    place(scout, where, o, NP, comment="mod-murloc-naga: the Darkspear scout at the Zoram Strand")
    retired = set()
    if not C.NAGA_CAMP:
        for lst, n in zip(village_lists, camp_at):
            del lst[n:]
        retired = set(npc_ids) - camp_keys
    retired |= village_keys                                 # (their voices go with them)
    kept = sorted(KEPT_ENTRIES.values())
    assert all(npc_ids[k] == e for k, e in KEPT_ENTRIES.items()), "the camp's people kept their entries"

    # The quests.
    quests, addons, offers, requests, starters, enders, go_enders, conditions = [], [], [], [], [], [], [], []
    smart = []

    def who(key):
        if isinstance(key, int):
            return key
        kind, k = key.split(":")
        return npc_ids[k] if kind == "npc" else go_ids[k]

    for race, qlist, ids in ((C.MURLOC, C.MURLOC_QUESTS if C.MURLOC_VILLAGE else [], murloc_quest_id),
                             (C.NAGA, C.NAGA_QUESTS if C.NAGA_CAMP else [], naga_quest_id)):
        for qd in qlist:
            qid = ids[qd["n"]]
            zone = C.ASHENVALE if qd["n"] in (32, 33, 34) else C.DARKSHORE
            req_npc = [(who(k) if not isinstance(k, int) else k, n) for k, n in qd.get("kill", [])]
            req_items = [(item_of(k), n) for k, n in qd.get("items", [])]
            text_body = qd.get("onu_text") if qd.get("onu_text") else qd["text"]
            choices = [item_ids[k] for k in qd.get("rewards_choice", [])] + [item_ids[k] for k in qd.get("rewards", [])]
            standing = qd.get("standing", [])
            rep_index = {10: 1, 25: 2, 75: 3, 150: 4, 250: 5, 350: 6, 500: 7, 1000: 8}
            money = 0 if qd["n"] == 0 else 150 * qd["level"]
            quests.append(dict(ID=qid, QuestType=2, QuestLevel=qd["level"], MinLevel=qd["min"], QuestSortID=zone, Flags=8,
                               RewardXPDifficulty=qd["xp"], RewardMoney=money, AllowableRaces=BIT[race],
                               LogTitle=qd["title"], LogDescription=qd["log"], QuestDescription=text_body, AreaDescription="",
                               QuestCompletionLog="", StartItem=item_of(qd["source_item"]) if qd.get("source_item") else 0,
                               req_npc=req_npc, req_items=req_items, choices=choices, standing=[(f, rep_index[v]) for f, v in standing]))
            prev = ids[qd["prev"]] if "prev" in qd else 0
            special = 2 if qd.get("explore") else 0
            addons.append((qid, prev, special, 1 if qd.get("source_item") else 0))
            offers.append((qid, 1, qd["reward"]))
            if qd.get("progress"):
                requests.append((qid, 6, 6, qd["progress"]))
            starters.append((who(qd["giver"]), qid))
            for extra in qd.get("also", []):
                starters.append((extra, qid))
            end = qd["ender"]
            if isinstance(end, str) and end.startswith("go:"):
                go_enders.append((who(end), qid))
            else:
                enders.append((who(end), qid))
            if qd.get("explore"):
                smart.append((trigger, qid))

    # The Onu's quest (The Tide Turns) is offered by Onu at the Grove of the Ancients; Lady Szaria
    # says where to find him.
    sql.comment("Their homes: the murlocs' village, the naga's camp, their enemies, the things they steal, in their own phases.")
    keep = f" AND {{}} NOT IN ({', '.join(map(str, kept))})" if kept else ""
    sql.raw(f"DELETE FROM `creature_template` WHERE `entry` BETWEEN {C.NPC_BASE} AND {C.NPC_BASE + 99}{keep.format('`entry`')};")
    sql.raw(f"DELETE FROM `creature_template_model` WHERE `CreatureID` BETWEEN {C.NPC_BASE} AND {C.NPC_BASE + 99}{keep.format('`CreatureID`')};")
    sql.insert("creature_template", ["entry", "name", "subname", "gossip_menu_id", "minlevel", "maxlevel", "faction", "npcflag",
                                     "speed_walk", "speed_run", "speed_swim", "unit_class", "unit_flags", "type", "flags_extra", "rank",
                                     "HealthModifier", "ManaModifier", "ArmorModifier", "DamageModifier", "BaseAttackTime",
                                     "RangeAttackTime", "lootid", "RegenHealth", "AIName", "ScriptName"], creatures)
    sql.insert("creature_template_model", ["CreatureID", "Idx", "CreatureDisplayID", "DisplayScale", "Probability"], models)
    sql.raw(f"DELETE FROM `creature` WHERE `guid` BETWEEN {C.SPAWN_BASE} AND {C.SPAWN_BASE + 999};")
    sql.insert("creature", ["guid", "id", "map", "zoneId", "areaId", "spawnMask", "phaseMask", "position_x", "position_y", "position_z",
                            "orientation", "spawntimesecs", "wander_distance", "MovementType", "Comment"], spawns)
    sql.raw(f"DELETE FROM `npc_text` WHERE `ID` BETWEEN {C.TEXT_BASE} AND {C.TEXT_BASE + 99};")
    sql.insert("npc_text", ["ID", "text0_0", "text0_1", "Probability0"], texts)
    sql.raw(f"DELETE FROM `gossip_menu` WHERE `MenuID` BETWEEN {C.NPC_BASE} AND {C.NPC_BASE + 99}{keep.format('`MenuID`')};")
    sql.insert("gossip_menu", ["MenuID", "TextID"], menus)
    sql.raw(f"DELETE FROM `npc_vendor` WHERE `entry` BETWEEN {C.NPC_BASE} AND {C.NPC_BASE + 99}{keep.format('`entry`')};")
    sql.insert("npc_vendor", ["entry", "slot", "item"], vendor)

    sql.raw(f"DELETE FROM `gameobject_template` WHERE `entry` BETWEEN {C.GO_BASE} AND {C.GO_BASE + 99};")
    sql.insert("gameobject_template", ["entry", "type", "displayId", "name", "size"] + [f"Data{i}" for i in range(24)], gos)
    sql.raw(f"DELETE FROM `gameobject` WHERE `guid` BETWEEN {C.GO_SPAWN_BASE} AND {C.GO_SPAWN_BASE + 999};")
    sql.insert("gameobject", ["guid", "id", "map", "zoneId", "areaId", "spawnMask", "phaseMask", "position_x", "position_y", "position_z",
                              "orientation", "rotation0", "rotation1", "rotation2", "rotation3", "spawntimesecs", "animprogress",
                              "state", "Comment"], go_spawns)
    sql.raw(f"DELETE FROM `gameobject_loot_template` WHERE `Entry` BETWEEN {C.GO_BASE} AND {C.GO_BASE + 99};")
    sql.insert("gameobject_loot_template", ["Entry", "Item", "Reference", "Chance", "QuestRequired", "LootMode", "GroupId",
                                            "MinCount", "MaxCount", "Comment"],
               [(e, i, 0, c, 1, 1, 0, 1, 1, "mod-murloc-naga") for e, i, c in go_loot])
    # (the story's loot, tools/murloc/, is "mod-murloc-naga: story" and its own to take out: each file takes out its own only,
    # whichever of them the server applies again; "mod-murloc-naga" alone was both's)
    sql.raw(f"DELETE FROM `creature_loot_template` WHERE `Comment` = '{LOOT_COMMENT}' OR (`Comment` = 'mod-murloc-naga' "
            f"AND `Entry` BETWEEN {C.NPC_BASE} AND {C.NPC_BASE + 99});")
    sql.insert("creature_loot_template", ["Entry", "Item", "Reference", "Chance", "QuestRequired", "LootMode", "GroupId",
                                          "MinCount", "MaxCount", "Comment"],
               [(e, i, 0, c, 1, 1, 0, 1, 1, LOOT_COMMENT) for e, i, c in cr_loot])

    # Their things' looks: the game's models as objects (GameObjectDisplayInfo, the game's and the server's).
    gdt = "isiiiiiiiiiiffffffi"
    for did, path in go_displays:
        client.put("GameObjectDisplayInfo", gdt, [did, path] + [0] * 10 + [-1.0, -1.0, 0.0, 1.0, 1.0, 3.0, 0])
    sql.raw(f"DELETE FROM `gameobjectdisplayinfo_dbc` WHERE `ID` BETWEEN {ID_GO_DISPLAY} AND {ID_GO_DISPLAY + 49};")
    sql.raw("INSERT INTO `gameobjectdisplayinfo_dbc` (`ID`, `ModelName`, `Sound_1`, `Sound_2`, `Sound_3`, `Sound_4`, `Sound_5`, `Sound_6`, "
            "`Sound_7`, `Sound_8`, `Sound_9`, `Sound_10`, `GeoBoxMinX`, `GeoBoxMinY`, `GeoBoxMinZ`, `GeoBoxMaxX`, `GeoBoxMaxY`, `GeoBoxMaxZ`, "
            "`ObjectEffectPackageID`) VALUES\n"
            + ",\n".join(f"({did}, {q(path)}, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, 0, 1, 1, 3, 0)" for did, path in go_displays) + ";")

    sql.comment("Their quest items and rewards.")
    sql.raw(f"DELETE FROM `item_template` WHERE `entry` BETWEEN {C.ITEM_BASE} AND {C.ITEM_BASE + 99};")
    item_cols = ["entry", "class", "subclass", "SoundOverrideSubclass", "name", "displayid", "Quality", "Flags", "BuyPrice", "SellPrice",
                 "InventoryType", "AllowableClass", "AllowableRace", "ItemLevel", "RequiredLevel", "maxcount", "stackable",
                 "stat_type1", "stat_value1", "stat_type2", "stat_value2", "armor", "bonding", "Material", "sheath",
                 "dmg_min1", "dmg_max1", "delay", "description"]
    rows = []
    for it in items:
        s = it["stats"] + [(0, 0)] * (2 - len(it["stats"]))
        weapon = it["cls"] == 2
        rows.append((it["entry"], it["cls"], it["sub"], -1, it["name"], it["display"], it["quality"], 0,
                     it["level"] * 40 if it["quality"] > 1 else 0, it["level"] * 10 if it["quality"] > 1 else 0, it["inv"], -1, -1,
                     it["level"], max(0, it["req"]), it["maxcount"], it["stack"], s[0][0], s[0][1], s[1][0], s[1][1], it["armor"],
                     it["bonding"], it["material"], 2 if weapon else 0, 24.0 if weapon else 0.0, 37.0 if weapon else 0.0,
                     3200 if weapon else 0, ""))
        client.put("Item", "iiiiiiii", [it["entry"], it["cls"], it["sub"], -1, it["material"], it["display"], it["inv"], 2 if weapon else 0])
    sql.insert("item_template", item_cols, rows)

    sql.comment("Their quests: the murlocs' (all theirs: murloc words, every giver a murloc) and the naga's (their start, and the way\n"
                "to the Horde after Darkshore: Onu at the Grove of the Ancients, a Darkspear scout at the Zoram Strand, Marukai at\n"
                "Zoram'gar, whose Naga at the Zoram Strand (6442) is the Horde's own).")
    sql.raw(f"DELETE FROM `quest_template` WHERE `ID` BETWEEN {C.QUEST_BASE} AND {C.QUEST_BASE + 99};")
    qcols = ["ID", "QuestType", "QuestLevel", "MinLevel", "QuestSortID", "Flags", "RewardXPDifficulty", "RewardMoney", "AllowableRaces",
             "LogTitle", "LogDescription", "QuestDescription", "AreaDescription", "QuestCompletionLog", "StartItem"]
    qcols += [f"RequiredNpcOrGo{i}" for i in range(1, 5)] + [f"RequiredNpcOrGoCount{i}" for i in range(1, 5)]
    qcols += [f"RequiredItemId{i}" for i in range(1, 7)] + [f"RequiredItemCount{i}" for i in range(1, 7)]
    qcols += [f"RewardChoiceItemID{i}" for i in range(1, 7)] + [f"RewardChoiceItemQuantity{i}" for i in range(1, 7)]
    qcols += [f"RewardFactionID{i}" for i in range(1, 3)] + [f"RewardFactionValue{i}" for i in range(1, 3)]
    rows = []
    for qd in quests:
        rn = (qd["req_npc"] + [(0, 0)] * 4)[:4]
        ri = (qd["req_items"] + [(0, 0)] * 6)[:6]
        ch = (qd["choices"] + [0] * 6)[:6]
        st = (qd["standing"] + [(0, 0)] * 2)[:2]
        rows.append(tuple(qd[c] for c in qcols[:15]) + tuple(n for n, _ in rn) + tuple(c for _, c in rn)
                    + tuple(i for i, _ in ri) + tuple(c for _, c in ri) + tuple(ch) + tuple(1 if c else 0 for c in ch)
                    + tuple(f for f, _ in st) + tuple(v for _, v in st))
    sql.insert("quest_template", qcols, rows)
    sql.raw(f"DELETE FROM `quest_template_addon` WHERE `ID` BETWEEN {C.QUEST_BASE} AND {C.QUEST_BASE + 99};")
    sql.insert("quest_template_addon", ["ID", "PrevQuestID", "SpecialFlags", "ProvidedItemCount"], addons)
    sql.raw(f"DELETE FROM `quest_offer_reward` WHERE `ID` BETWEEN {C.QUEST_BASE} AND {C.QUEST_BASE + 99};")
    sql.insert("quest_offer_reward", ["ID", "Emote1", "RewardText"], offers)
    sql.raw(f"DELETE FROM `quest_request_items` WHERE `ID` BETWEEN {C.QUEST_BASE} AND {C.QUEST_BASE + 99};")
    sql.insert("quest_request_items", ["ID", "EmoteOnComplete", "EmoteOnIncomplete", "CompletionText"], requests)
    for table, rows_ in (("creature_queststarter", starters), ("creature_questender", enders), ("gameobject_questender", go_enders)):
        sql.raw(f"DELETE FROM `{table}` WHERE `quest` BETWEEN {C.QUEST_BASE} AND {C.QUEST_BASE + 99};")
        sql.insert(table, ["id", "quest"], rows_)
    # Their voices as they're spoken to (the game's creature sounds, a random one of those given) and as
    # a quest is handed in to them: the murlocs' gurgles and cheer, Sloshy's baby burbles, the naga's
    # and the sirens' hiss.
    smart_rows = [(t, 0, i, 0, 10, 0, 100, 0, 2, 12, 1000, 1000, 1, 0, 15, qid, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0,
                   "mod-murloc-naga: the island's summit, for the oracle's vision") for i, (t, qid) in enumerate(smart)]
    for key, (hello, reward) in VOICED.items():
        if key not in npc_ids or key in retired:
            continue
        entry = npc_ids[key]
        for i, (event, sounds) in enumerate(((64, hello), (20, reward))):
            if not sounds:
                continue
            sounds = (list(sounds) + [0, 0, 0, 0])[:4]
            smart_rows.append((entry, 0, i, 0, event, 0, 100, 0, 0, 0, 0, 0, 0, 0, 115, sounds[0], sounds[1], sounds[2], sounds[3], 0, 0,
                               1, 0, 0, 0, 0, 0, 0, 0, 0, f"mod-murloc-naga: {key}'s voice"))
    sql.raw(f"DELETE FROM `smart_scripts` WHERE `entryorguid` BETWEEN {C.NPC_BASE} AND {C.NPC_BASE + 99} AND `source_type` = 0"
            f"{keep.format('`entryorguid`')};")
    sql.insert("smart_scripts", ["entryorguid", "source_type", "id", "link", "event_type", "event_phase_mask", "event_chance",
                                 "event_flags", "event_param1", "event_param2", "event_param3", "event_param4", "event_param5",
                                 "event_param6", "action_type", "action_param1", "action_param2", "action_param3", "action_param4",
                                 "action_param5", "action_param6", "target_type", "target_param1", "target_param2", "target_param3",
                                 "target_param4", "target_x", "target_y", "target_z", "target_o", "comment"],
               smart_rows)


if __name__ == "__main__":
    main()
