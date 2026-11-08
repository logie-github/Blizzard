#!/usr/bin/env python3
"""Builds the two races' data from the game's own tables and data/retail/races.json (tools/
races.py): the world database's SQL (data/sql/chromiecraft/world/allied_races_world.sql) and the changes
the module makes to the game's tables as the realm starts (data/client/dbc/*.txt;
AlliedRacesPatch.cpp applies them, the way mod-skyborne's are). Run it again when something here
or in races.json changes; its output is committed.

  build_data.py DBC_DIR WORLD_SQL_DIR

DBC_DIR: the server's dbc folder (the data.zip in warcraft/server-data.env); WORLD_SQL_DIR: the
core's data/sql/base/db_world at the realm's commit (warcraft/server-version.env).

The races:
  15  Void Elf, Alliance: the Draenei's start in Ammen Vale, their quests and standing (the Exodar)
  16  Nightborne, Horde: the Forsaken's start in Deathknell, their quests and standing (Undercity)
Races 15 and 16 were the game's Skeleton and Vrykul, which only creatures use: they move to 24
and 25 in the game's tables (their looks, their creatures' looks), out of the way (the Skyborne
moved 13 and 14 to 22 and 23 the same way).
"""
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import names                                   # noqa: E402
import sqlrows                                 # noqa: E402

MODULE = os.path.dirname(HERE)
COLUMNS = json.load(open(os.path.join(HERE, "dbc_columns.json")))
TYPES = json.load(open(os.path.join(HERE, "dbc_types.json")))
RACES = json.load(open(os.path.join(MODULE, "data", "retail", "races.json")))

HUMAN, ORC, DWARF, NIGHTELF, UNDEAD, TAUREN, GNOME, TROLL, BLOODELF, DRAENEI = 1, 2, 3, 4, 5, 6, 7, 8, 10, 11
VOIDELF, NIGHTBORNE, LIGHTFORGED, ZANDALARI = 15, 16, 17, 18
RACE_IDS = (VOIDELF, NIGHTBORNE, LIGHTFORGED, ZANDALARI)
ALLIANCE_RACES, HORDE_RACES = (VOIDELF, LIGHTFORGED), (NIGHTBORNE, ZANDALARI)
MOVED = {15: 24, 16: 25, 17: 26, 18: 27}       # Skeleton, Vrykul, Tuskarr, Forest Troll: the creatures' races, moved
KEY = {VOIDELF: "voidelf", NIGHTBORNE: "nightborne", LIGHTFORGED: "lightforged", ZANDALARI: "zandalari"}
BIT = {r: 1 << (r - 1) for r in RACE_IDS}
ALLIANCE_MASK = sum(1 << (r - 1) for r in (HUMAN, DWARF, NIGHTELF, GNOME, DRAENEI))
HORDE_MASK = sum(1 << (r - 1) for r in (ORC, UNDEAD, TAUREN, TROLL, BLOODELF))
ALLIANCE_BITS = sum(BIT[r] for r in ALLIANCE_RACES)
HORDE_BITS = sum(BIT[r] for r in HORDE_RACES)
WARRIOR, PALADIN, HUNTER, ROGUE, PRIEST, DK, SHAMAN, MAGE, WARLOCK, DRUID = 1, 2, 3, 4, 5, 6, 7, 8, 9, 11
# Each race's classes of today that 3.3.5 has.
CLASSES_OF = {
    VOIDELF: (WARRIOR, HUNTER, ROGUE, PRIEST, DK, MAGE, WARLOCK),
    NIGHTBORNE: (WARRIOR, HUNTER, ROGUE, PRIEST, DK, MAGE, WARLOCK),
    LIGHTFORGED: (WARRIOR, PALADIN, HUNTER, PRIEST, DK, MAGE),
    ZANDALARI: (WARRIOR, PALADIN, HUNTER, ROGUE, PRIEST, DK, SHAMAN, MAGE, DRUID),
}
START = {VOIDELF: DRAENEI, NIGHTBORNE: UNDEAD, LIGHTFORGED: DRAENEI, ZANDALARI: TAUREN}   # where they begin, whose quests and standing they share
# Whose start each class takes (gear, action bars): the start race's where it has the class, the
# nearest of its side where it doesn't.
TEMPLATE = {
    VOIDELF: {WARRIOR: DRAENEI, HUNTER: DRAENEI, ROGUE: HUMAN, PRIEST: DRAENEI, DK: DRAENEI, MAGE: DRAENEI, WARLOCK: HUMAN},
    NIGHTBORNE: {WARRIOR: UNDEAD, HUNTER: BLOODELF, ROGUE: UNDEAD, PRIEST: UNDEAD, DK: UNDEAD, MAGE: UNDEAD, WARLOCK: UNDEAD},
    LIGHTFORGED: {WARRIOR: DRAENEI, PALADIN: DRAENEI, HUNTER: DRAENEI, PRIEST: DRAENEI, DK: DRAENEI, MAGE: DRAENEI},
    ZANDALARI: {WARRIOR: TAUREN, PALADIN: BLOODELF, HUNTER: TAUREN, ROGUE: TROLL, PRIEST: TROLL, DK: TAUREN, SHAMAN: TAUREN, MAGE: TROLL, DRUID: TAUREN},
}
# Classes the old races are given, each with the race whose start gear, action bar, class skills and
# class quests it takes; they begin where the race's warriors do. The user: "Also let undead be
# paladins"; then WoW: Forever's new pairs ("Add these race class combos"): human hunters, dwarf
# shamans, gnome priests, orc mages and troll warlocks.
EXTRA_CLASSES = {
    UNDEAD: {PALADIN: BLOODELF},
    HUMAN: {HUNTER: DWARF},
    DWARF: {SHAMAN: DRAENEI},
    GNOME: {PRIEST: HUMAN},
    ORC: {MAGE: TROLL},
    TROLL: {WARLOCK: ORC},
}
STATS_FROM = {VOIDELF: BLOODELF, NIGHTBORNE: NIGHTELF, LIGHTFORGED: DRAENEI, ZANDALARI: TROLL}   # their kin's starting stats
MODEL_FROM = {VOIDELF: BLOODELF, NIGHTBORNE: NIGHTELF, LIGHTFORGED: DRAENEI, ZANDALARI: TROLL}   # whose model rows theirs are copied from
PREFIX = {VOIDELF: "Ve", NIGHTBORNE: "Nb", LIGHTFORGED: "Ld", ZANDALARI: "Za"}
NAME = {VOIDELF: "Void Elf", NIGHTBORNE: "Nightborne", LIGHTFORGED: "Lightforged Draenei", ZANDALARI: "Zandalari Troll"}
NARRATION = {VOIDELF: "VoidElfNarration.mp3", NIGHTBORNE: "NightborneNarration.mp3",
             LIGHTFORGED: "LightforgedDraeneiNarration.mp3", ZANDALARI: "ZandalariTrollNarration.mp3"}
FEATURE_LABELS = {VOIDELF: ("FEATURES", "FEATURES", "NORMAL"), NIGHTBORNE: ("FEATURES", "FEATURES", "NORMAL"),
                  LIGHTFORGED: ("FEATURES", "HORNS", "NORMAL"), ZANDALARI: ("TUSKS", "TUSKS", "NORMAL")}
# The quests of the start race alone that are cloned for the new race (tools/quests.py): those
# keep their race, the clone is the new race's; every other quest of the start race opens to it.
CLONED = json.load(open(os.path.join(MODULE, "data", "retail", "cloned_quests.json"))) if os.path.exists(
    os.path.join(MODULE, "data", "retail", "cloned_quests.json")) else {}

# New rows' ids, clear of the game's, the Skyborne's (900000s, 9000s) and Wrath Remix's.
ID_SECTIONS = 920000
ID_SECTIONS_END = 999999
ID_OUTFIT = 9100
ID_HAIRGEO = 9100
ID_NAMEGEN = 91000
ID_VOCAL = 9200                   # (the Skyborne's are 9000 to 9107: the game's table carries both patches' rows)
ID_EMOTESOUND = 91000
ID_SEQUENCE = {VOIDELF: 9011, NIGHTBORNE: 9012, LIGHTFORGED: 9013, ZANDALARI: 9014}
ID_CAMERA = {VOIDELF: 9011, NIGHTBORNE: 9012, LIGHTFORGED: 9013, ZANDALARI: 9014}
ID_NARRATION = {VOIDELF: 910001, NIGHTBORNE: 910002, LIGHTFORGED: 910003, ZANDALARI: 910004}
ID_VOICE = 910100
# The UI's moments 3.3.5 has twice that today's tables list once (the game's own blood elves and
# Draenei have the same sounds at both): "can't drink any more" (6, as 47) and "invalid target" (66,
# as 11).
VOCAL_TWINS = {6: 47, 66: 11}
ID_DISPLAY = {VOIDELF: (33001, 33002), NIGHTBORNE: (33003, 33004), LIGHTFORGED: (33005, 33006), ZANDALARI: (33007, 33008)}  # male, female looks
ID_MODEL = {VOIDELF: (3601, 3602), NIGHTBORNE: (3603, 3604), LIGHTFORGED: (3605, 3606), ZANDALARI: (3607, 3608)}
SPELLS = {"rift": 98711, "rift_open": 98712, "entropic": 98713, "entropic_buff": 98714, "chill": 98715, "calm": 98716,
          "cantrips": 98717, "pulse": 98718, "pulse_slow": 98719, "arcane_res": 98720, "affinity": 98721, "history": 98722,
          "judgment": 98723, "judgment_strike": 98724, "forge": 98725, "reckoning": 98726, "reckoning_burst": 98727,
          "holy_res": 98728, "demonbane": 98729, "regeneratin": 98730, "paku": 98731, "paku_buff": 98732, "swoop": 98733,
          "city_of_gold": 98734}
# WoW: Forever's racials for the eight races of 1.x (the user: "Add the new or updated racials to each race"):
# forever.warcraftdb.com's spells (Forever 1.60.1). Its new spells' ids are a million and more, past what
# 3.3.5's tables take; theirs here are these. The racials 3.3.5 has and Forever keeps (some changed) keep
# their own ids.
FOREVER = {"will_to_survive": 98800, "ruthless": 98801, "blood_fury": 98802, "blood_fury_sp": 98803, "savage": 98804,
           "shatter_curse": 98806, "earth_fury": 98807, "big_game_hunter": 98808, "elunes_light": 98809,
           "quickness": 98810, "grave_melee": 98811, "grave_caster": 98812, "grave_drain": 98813,
           "cultivation": 98814, "plainsrunning": 98815, "plainsrunning_speed": 98816,
           "mind_mana": 98817, "mind_rage": 98818, "mind_energy": 98819, "mind_runic": 98820,
           "eureka_priest": 98821, "eureka_mage": 98822, "eureka_warlock": 98823, "eureka_warrior": 98824,
           "eureka_rogue": 98825, "confounding_flash": 98826, "rapid_regeneration": 98842}
# The gnome priest's own two (Forever's priest racials), taught by the module as the level comes
# (AlliedRacesForever.cpp): Contingency Plan's ward a rank, its shield a rank and its healing a rank.
CONTINGENCY_WARD = (98827, 98828, 98829, 98830, 98831)
CONTINGENCY_SHIELD = (98832, 98833, 98834, 98835, 98836)
CONTINGENCY_HEAL = (98837, 98838, 98839, 98840, 98841)
CONTINGENCY_LEVEL = (20, 30, 40, 50, 60)
CONTINGENCY_ABSORB = (155, 290, 467, 596, 926)
CONTINGENCY_TICK = (25, 40, 56, 102, 134)                # healing every 3 sec for 15 sec
ID_FOREVER_ABILITY = 23500                     # new SkillLineAbility rows (the game's end at 21980)
# Each race's racial skill line and its racials in Forever: (spell, class mask: 0 for every class).
RACIAL_LINE = {HUMAN: 754, ORC: 125, DWARF: 101, NIGHTELF: 126, UNDEAD: 220, TAUREN: 124, GNOME: 753, TROLL: 733}
CLS = {c: 1 << (c - 1) for c in (WARRIOR, PALADIN, HUNTER, ROGUE, PRIEST, DK, SHAMAN, MAGE, WARLOCK, DRUID)}
FOREVER_KIT = {
    HUMAN: [(FOREVER["will_to_survive"], 0), (20600, 0), (FOREVER["ruthless"], 0), (20598, 0)],
    ORC: [(FOREVER["blood_fury"], 0), (20573, 0), (FOREVER["savage"], 0), (FOREVER["shatter_curse"], 0)],
    DWARF: [(20594, 0), (2481, 0), (FOREVER["earth_fury"], 0), (FOREVER["big_game_hunter"], 0)],
    NIGHTELF: [(FOREVER["elunes_light"], 0), (FOREVER["quickness"], 0), (58984, 0), (20585, 0)],
    # (Touch of the Grave's 20% is Forever's warriors', paladins' and rogues'; death knights, which
    # Forever hasn't, have it too)
    UNDEAD: [(20577, 0), (FOREVER["grave_melee"], CLS[WARRIOR] | CLS[PALADIN] | CLS[ROGUE] | CLS[DK]),
             (FOREVER["grave_caster"], CLS[PRIEST] | CLS[MAGE] | CLS[WARLOCK]), (5227, 0), (7744, 0)],
    TAUREN: [(20549, 0), (20550, 0), (FOREVER["cultivation"], 0), (FOREVER["plainsrunning"], 0)],
    # (Expansive Mind's runic power: the gnome death knight's, which Forever hasn't)
    GNOME: [(20593, 0), (20589, 0), (FOREVER["mind_mana"], CLS[PRIEST] | CLS[MAGE] | CLS[WARLOCK]),
            (FOREVER["mind_rage"], CLS[WARRIOR]), (FOREVER["mind_energy"], CLS[ROGUE]), (FOREVER["mind_runic"], CLS[DK]),
            (FOREVER["eureka_priest"], CLS[PRIEST]), (FOREVER["eureka_mage"], CLS[MAGE]),
            (FOREVER["eureka_warlock"], CLS[WARLOCK]), (FOREVER["eureka_warrior"], CLS[WARRIOR]),
            (FOREVER["eureka_rogue"], CLS[ROGUE])],
    TROLL: [(26297, 0), (20555, 0), (FOREVER["rapid_regeneration"], 0), (20557, 0)],
}
NPC_RIFT = 900101
NPC_JUDGMENT, NPC_RECKONING = 900102, 900103   # earlier releases' stalkers for Light's Judgment and Reckoning (deleted)
DISPLAY_RIFT = 9510                            # Creature\Spells\Creature_SpellPortal


class Dbc:
    def __init__(self, path):
        data = open(path, "rb").read()
        magic, self.count, self.fields, self.size, strings = struct.unpack("<4s4I", data[:20])
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


class Client:
    """The changes to the game's tables, a file for each (AlliedRacesPatch.cpp applies them)."""

    def __init__(self):
        self.files = {}
        self.types = {}

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
                f.write(f"# {name}: the void elves' and the nightborne's changes (tools/build_data.py)\n")
                if name in self.types:
                    f.write(f"types\t{self.types[name]}\n")
                f.write("\n".join(lines) + "\n")


def esc(text):
    return str(text).replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n")


def sql_value(v, t):
    if t == "s":
        return "'" + str(v).replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n") + "'"
    if t == "f":
        return repr(float(v))
    return str(i32(int(v)))


def or_into(column):
    """SQL for a race mask column (a signed INT) with the new row's bits OR'd in: MariaDB ORs as
    64-bit unsigned numbers (a -1, every race, becomes 2^64 - 1, which the column can't take, and
    the statement fails), so the result is taken back to the column's 32 bits."""
    bits = f"((`{column}` | VALUES(`{column}`)) & 0xFFFFFFFF)"
    return f"`{column}` = IF({bits} >= 0x80000000, CAST({bits} AS SIGNED) - 4294967296, {bits})"


class Sql:
    def __init__(self):
        self.parts = []

    def comment(self, text):
        self.parts.append("\n-- " + text.replace("\n", "\n-- "))

    def raw(self, text):
        self.parts.append(text)

    def replace(self, table, columns, types, rows):
        if not rows:
            return
        cols = ", ".join(f"`{c}`" for c in columns)
        for i in range(0, len(rows), 200):
            chunk = rows[i:i + 200]
            # (the core's spell class masks are unsigned columns, where every bit is 4294967295)
            values = ",\n".join("(" + ", ".join(str(int(v) & 0xFFFFFFFF) if "SpellClassMask" in c and t == "i" else sql_value(v, t)
                                                 for v, t, c in zip(r, types, columns)) + ")" for r in chunk)
            self.parts.append(f"REPLACE INTO `{table}` ({cols}) VALUES\n{values};")

    def merge_masks(self, table, columns, types, rows, masks):
        """Rows put in, or, where the table has the row already, their bits OR'd into its [masks]:
        another module's rows of the same table (the reputations: the allied races', the Skyborne's,
        mod-worgen-goblin's) keep their races' bits whichever is applied last."""
        if not rows:
            return
        cols = ", ".join(f"`{c}`" for c in columns)
        update = ", ".join(or_into(m) for m in masks)
        for i in range(0, len(rows), 200):
            chunk = rows[i:i + 200]
            values = ",\n".join("(" + ", ".join(sql_value(v, t) for v, t in zip(r, types)) + ")" for r in chunk)
            self.parts.append(f"INSERT INTO `{table}` ({cols}) VALUES\n{values}\nON DUPLICATE KEY UPDATE {update};")


def dbc_row_values(dbc, row, types):
    out = []
    for v, t in zip(row, types):
        out.append(dbc.s(v) if t == "s" else f32(v) if t == "f" else v)
    return out


def narration_sound(template, race):
    """A race's narration's SoundEntries row from the game's own ([template]): its file alone, the
    nine other files' places empty and unweighted (as the Death Knights' narration has them), so
    the game never picks an empty alternative."""
    sound = list(template)
    sound[0], sound[2] = ID_NARRATION[race], f"{RACES[KEY[race]]['name']}FlyByNarration"
    sound[3:13] = [NARRATION[race]] + [""] * 9
    sound[13:23] = [1] + [0] * 9
    sound[23] = "Sound\\CinematicVoices"
    return sound


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    dbc_dir, world = sys.argv[1], sys.argv[2]
    D = lambda name: Dbc(os.path.join(dbc_dir, name + ".dbc"))
    client, sql = Client(), Sql()
    # The creatures' races moved out of the new races' places in the client's own rows (an HD look's
    # too, whatever their ids): their race, their looks, hair shapes, features and voice rows.
    for old, new in MOVED.items():
        client.copyrow("ChrRaces", old, new)
        for table, field in (("CharSections", 1), ("CharHairGeosets", 1), ("CreatureDisplayInfoExtra", 1),
                             ("CharacterFacialHairStyles", 0), ("VocalUISounds", 2)):
            client.remapfield(table, field, old, new)
    sql.raw("-- The void elves and the nightborne (mod-allied-races): generated by tools/build_data.py from the\n"
            "-- game's own tables and data/retail/races.json; edit those, not this. Safe to run again: every row is\n"
            "-- replaced, every mask OR'd.")
    models = {race: {int(sex): m for sex, m in RACES[KEY[race]]["models"].items()} for race in RACE_IDS}

    # Models and looks: a CreatureModelData row and a CreatureDisplayInfo row a model, copied from
    # the kin's (the blood elves' for the void elves, the night elves' for the nightborne).
    races = D("ChrRaces")
    rt = TYPES["chrraces_dbc"]
    race_rows = {r[0]: r for r in races.rows}
    displays, model_data = D("CreatureDisplayInfo"), D("CreatureModelData")
    display_rows = {r[0]: r for r in displays.rows}
    model_rows = {r[0]: r for r in model_data.rows}
    dt = "iiiifissssiiiiii"
    mt = "iisifiiffffiiifff" + "ffffff" + "fffff"
    sql.comment("Their models (CreatureModelData) and looks (CreatureDisplayInfo), from their kin's rows.")
    display_sql, model_sql = [], []
    for race in RACE_IDS:
        kin = race_rows[MODEL_FROM[race]]
        for sex in (0, 1):
            kin_display = display_rows[kin[4 + sex]]
            kin_model = model_rows[kin_display[1]]
            m = dbc_row_values(model_data, kin_model, mt)
            m[0] = ID_MODEL[race][sex]
            m[2] = models[race][sex]["folder"] + "\\" + models[race][sex]["name"] + ".mdx"
            client.put("CreatureModelData", mt, m)
            model_sql.append(m)
            d = dbc_row_values(displays, kin_display, dt)
            d[0] = ID_DISPLAY[race][sex]
            d[1] = ID_MODEL[race][sex]
            d[2] = 0                                        # no creature sound set
            d[3] = 0                                        # no extra: a player's look
            d[4] = 1.0
            d[12] = 0
            client.put("CreatureDisplayInfo", dt, d)
            display_sql.append(d)
    sql.replace("creaturemodeldata_dbc", [c for c in ["ID", "Flags", "ModelName", "SizeClass", "ModelScale", "BloodID", "FootprintTextureID",
                "FootprintTextureLength", "FootprintTextureWidth", "FootprintParticleScale", "FoleyMaterialID", "FootstepShakeSize",
                "DeathThudShakeSize", "SoundID", "CollisionWidth", "CollisionHeight", "MountHeight", "GeoBoxMinX", "GeoBoxMinY", "GeoBoxMinZ",
                "GeoBoxMaxX", "GeoBoxMaxY", "GeoBoxMaxZ", "WorldEffectScale", "AttachedEffectScale", "MissileCollisionRadius",
                "MissileCollisionPush", "MissileCollisionRaise"]], mt, model_sql)
    sql.replace("creaturedisplayinfo_dbc", ["ID", "ModelID", "SoundID", "ExtendedDisplayInfoID", "CreatureModelScale", "CreatureModelAlpha",
                "TextureVariation_1", "TextureVariation_2", "TextureVariation_3", "PortraitTextureName", "BloodLevel", "BloodID",
                "NPCSoundID", "ParticleColorID", "CreatureGeosetData", "ObjectEffectPackageID"], dt, display_sql)

    # Races ----------------------------------------------------------------------------------------
    sql.comment("The races: the start race's faction, language and side; their own models, names and intros.")
    server_races = []
    for race in RACE_IDS:
        start = race_rows[START[race]]
        v = dbc_row_values(races, start, rt)
        v[0] = race
        v[1] = race_rows[BLOODELF][1]                   # flags: playable, can mount
        v[4], v[5] = ID_DISPLAY[race]
        v[6] = PREFIX[race]
        v[11] = models[race][0]["folder"].split("\\")[1]    # ClientFileString: Character\<this>\...
        v[12] = ID_SEQUENCE[race]
        for base in (14, 31, 48):
            for i in range(base, base + 16):
                v[i] = NAME[race] if i == base else ""
        v[65], v[66], v[67] = FEATURE_LABELS[race]      # the sliders' names: men's feature, women's, hair
        v[68] = 0                                       # any expansion
        client.put("ChrRaces", rt, v)
        server_races.append(v)
    sql.replace("chrraces_dbc", COLUMNS["chrraces_dbc"], rt, server_races)

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

    SKIN_FLAGS, FACE_FLAGS = 17, 1
    for race in RACE_IDS:
        for sex in (0, 1):
            m = models[race][sex]
            for s in m["skins"]:
                c = s["index"]
                section(race, sex, 0, [names.skin(m, c), "", ""], SKIN_FLAGS, 0, c)
                if s["pelvis"]:
                    section(race, sex, 4, [names.pelvis(m, c), names.torso(m, c) if s["torso"] else "", ""], SKIN_FLAGS, 0, c)
            for fi, face in enumerate(m["faces"]):
                for s in m["skins"]:
                    fid = names.face_file(m, face, s)
                    for eye in m["eyes"]:
                        v = names.face_variation(m, fi, eye["index"])
                        section(race, sex, 1, [names.face_lower(m, fid, eye), names.face_upper(m, eye), ""], FACE_FLAGS, v, s["index"])
            for h in m["hair"]:
                for hc in m["hair_colors"]:
                    section(race, sex, 3, [names.hair(m, hc["index"]), "", ""], SKIN_FLAGS, h["variation"], hc["index"])
    for r in sections.rows:
        if r[1] in MOVED:
            v = dbc_row_values(sections, r, st)
            v[1] = MOVED[r[1]]
            new_sections.append(v)
    sql.comment("Their looks: skins, faces (a face an eye colour), hair, underwear; the creatures' races 15 to 18 moved to 24 to 27.")
    sql.raw(f"DELETE FROM `charsections_dbc` WHERE `ID` BETWEEN {ID_SECTIONS} AND {ID_SECTIONS_END};\n")
    assert next_id[0] <= ID_SECTIONS_END, next_id[0]
    sql.replace("charsections_dbc", COLUMNS["charsections_dbc"], st, new_sections)

    # Hair shapes, features, names, voices (the game's tables only, but for the emotes' sounds).
    geo = D("CharHairGeosets")
    gid = ID_HAIRGEO
    for race in RACE_IDS:
        for sex in (0, 1):
            for h in models[race][sex]["hair"]:
                client.put("CharHairGeosets", "iiiiii", [gid, race, sex, h["variation"], h["geoset"], 0])
                gid += 1
    for race in RACE_IDS:
        for sex in (0, 1):
            for f in models[race][sex]["features"]:
                client.append_raw("CharacterFacialHairStyles", struct.pack("<8I", race, sex, f["variation"], *f["geosets"]))
    nid = ID_NAMEGEN
    for race in RACE_IDS:
        for n in RACES[KEY[race]]["names"]:
            client.put("NameGen", "isii", [nid, n["name"], race, n["sex"]])
            nid += 1

    # Voices: a SoundEntries row a sound kit (its WAVs, tools/package.py), named by VocalUISounds
    # (the race's words at the UI's moments) and EmotesTextSound (its emotes).
    sounds = D("SoundEntries")
    snt = TYPES["soundentries_dbc"]
    snd_rows = {r[0]: r for r in sounds.rows}
    emote_ids = set(r[0] for r in D("EmotesText").rows)
    sound_sql, emote_rows = [], []
    vid, eid, sid = ID_VOCAL, ID_EMOTESOUND, ID_VOICE
    vocal_template = dbc_row_values(sounds, snd_rows[9549], snt)      # BloodElfMale_InventoryFull
    emote_template = dbc_row_values(sounds, snd_rows[10025], snt)     # TextEmote BeF Bored
    for race in RACE_IDS:
        name = RACES[KEY[race]]["name"]
        kit_sound = {}

        def sound_for(kit, template, label):
            nonlocal sid
            if not kit["files"]:
                return 0
            if kit["id"] in kit_sound:
                return kit_sound[kit["id"]]
            row = list(template)
            row[0] = sid
            row[2] = f"{name} {label} {kit['id']}"
            files = [f"{name}_{kit['id']}_{n + 1}.mp3" for n in range(min(10, len(kit["files"])))]
            for i in range(10):
                row[3 + i] = files[i] if i < len(files) else ""
                row[13 + i] = 1 if i < len(files) else 0
            row[23] = f"Sound\\Character\\{name}"
            client.put("SoundEntries", snt, row)
            sound_sql.append(row)
            kit_sound[kit["id"]] = sid
            sid += 1
            return kit_sound[kit["id"]]

        vocal = list(RACES[KEY[race]]["voices"]["vocal"])
        by_enum = {v["enum"]: v for v in vocal}
        vocal += [dict(by_enum[twin], enum=enum) for enum, twin in VOCAL_TWINS.items() if enum not in by_enum and twin in by_enum]
        for v in vocal:
            ids = [sound_for(k, vocal_template, "Vocal") for k in v["kits"]]
            client.put("VocalUISounds", "iiiiiii", [vid, v["enum"], race, ids[0], ids[1], 0, 0])
            vid += 1
        for e in RACES[KEY[race]]["voices"]["emotes"]:
            if e["emote"] not in emote_ids:
                continue
            s = sound_for(e["kit"], emote_template, "Emote")
            if not s:
                continue
            row = [eid, e["emote"], race, e["sex"], s]
            client.put("EmotesTextSound", "iiiii", row)
            emote_rows.append(row)
            eid += 1
    sql.comment("Their voices (the game's sound kits of today, as MP3s in the patch) and their emotes.")
    sql.replace("soundentries_dbc", COLUMNS["soundentries_dbc"], snt, sound_sql)
    sql.replace("emotestextsound_dbc", COLUMNS["emotestextsound_dbc"], "iiiii", emote_rows)

    # Classes and starting gear.
    for race in RACE_IDS:
        for cls in CLASSES_OF[race]:
            client.append_raw("CharBaseInfo", bytes([race, cls]))
    for race, classes in EXTRA_CLASSES.items():
        for cls in classes:
            client.append_raw("CharBaseInfo", bytes([race, cls]))
    outfits = D("CharStartOutfit")
    oid, outfit_rows = ID_OUTFIT, []
    for raw in outfits.raw:
        orace, cls, sex, outfit = raw[4], raw[5], raw[6], raw[7]
        for new in RACE_IDS:
            if cls in TEMPLATE[new] and TEMPLATE[new][cls] == orace:
                data = struct.pack("<I", oid) + bytes([new, cls, sex, outfit]) + raw[8:]
                client.put_raw("CharStartOutfit", data)
                ints = struct.unpack(f"<{len(raw[8:]) // 4}I", raw[8:])
                outfit_rows.append([oid, new, cls, sex, outfit] + list(ints))
                oid += 1
        for new, classes in EXTRA_CLASSES.items():
            if classes.get(cls) == orace:
                data = struct.pack("<I", oid) + bytes([new, cls, sex, outfit]) + raw[8:]
                client.put_raw("CharStartOutfit", data)
                ints = struct.unpack(f"<{len(raw[8:]) // 4}I", raw[8:])
                outfit_rows.append([oid, new, cls, sex, outfit] + list(ints))
                oid += 1
    sql.comment("Their classes' starting gear: the start race's for the class (or the nearest race's).")
    sql.replace("charstartoutfit_dbc", COLUMNS["charstartoutfit_dbc"], TYPES["charstartoutfit_dbc"], outfit_rows)

    # Skills and abilities by race, standing --------------------------------------------------------
    lines = D("SkillLine")
    racial_lines, languages = set(), {}
    for r in lines.rows:
        name = lines.s(r[3])
        if r[1] == 9 and "racial" in name.lower():
            racial_lines.add(r[0])
        if r[1] == 10:
            languages[r[0]] = name
    COMMON, ORCISH = 98, 109

    def faction_bits(mask, line):
        add = 0
        if line in languages:
            # Only the side's own rows: the Horde's Common row (and the Alliance's Orcish one) is a
            # tiered one for learning it, and a race in it may be given that row (rank 0: nothing)
            # in place of its own.
            if line == COMMON and mask & ALLIANCE_MASK:
                add |= ALLIANCE_BITS
            if line == ORCISH and mask & HORDE_MASK:
                add |= HORDE_BITS
            return add
        if line in racial_lines:
            return 0
        if mask & ALLIANCE_MASK:
            add |= ALLIANCE_BITS
        if mask & HORDE_MASK:
            add |= HORDE_BITS
        return add

    def ors(table, dbc, field_mask, field_line, sql_table):
        rows, wrong = [], []
        for r in dbc.rows:
            mask = r[field_mask]
            if mask == 0 or mask & 0x7FFFFFFF == 0x7FFFFFFF:
                continue
            if r[field_line] in (COMMON, ORCISH) and not faction_bits(mask, r[field_line]):
                wrong.append(r[0])
            add = faction_bits(mask, r[field_line])
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
        if wrong:
            # (releases up to 1.0.236 put these races in the other side's language rows too)
            sql.raw(f"UPDATE `{sql_table}` SET `RaceMask` = `RaceMask` & ~{ALLIANCE_BITS | HORDE_BITS} "
                    f"WHERE `ID` IN ({', '.join(str(i) for i in wrong)}) AND `RaceMask` > 0;")

    sql.comment("Skills and abilities open to either side's races are open to theirs (the racials and languages aside).")
    ors("SkillRaceClassInfo", D("SkillRaceClassInfo"), 2, 1, "skillraceclassinfo_dbc")
    ors("SkillLineAbility", D("SkillLineAbility"), 3, 1, "skilllineability_dbc")

    # Each class's own skill lines (its specs' lines, as SkillRaceClassInfo has them for that class alone),
    # whose abilities of no class (class mask 0) are the class's too.
    line_category = {r[0]: r[1] for r in lines.rows}
    class_lines = {}
    for r in D("SkillRaceClassInfo").rows:
        if line_category.get(r[1]) == 7 and r[3] and r[3] & (r[3] - 1) == 0 and not lines.s(
                next(x for x in lines.rows if x[0] == r[1])[3]).startswith("Pet"):
            class_lines.setdefault(r[3].bit_length(), set()).add(r[1])

    sql.comment("The old races' new classes (undead paladins; human hunters, dwarf shamans, gnome priests, orc mages, troll\n"
                "warlocks): the class's skills and abilities that the race their start comes from has, theirs too.")
    for table, dbc, f_mask, f_class, f_line, sql_table in (
            ("SkillRaceClassInfo", D("SkillRaceClassInfo"), 2, 3, 1, "skillraceclassinfo_dbc"),
            ("SkillLineAbility", D("SkillLineAbility"), 3, 4, 1, "skilllineability_dbc")):
        rows = []
        for race, classes in EXTRA_CLASSES.items():
            for cls, like in classes.items():
                bit, like_bit = 1 << (race - 1), 1 << (like - 1)
                for r in dbc.rows:
                    mask, cmask = r[f_mask], r[f_class]
                    ours = (cmask & (1 << (cls - 1))) or (cmask == 0 and r[f_line] in class_lines.get(cls, ()))
                    if not ours or not mask & like_bit or mask & bit or r[f_line] in racial_lines:
                        continue
                    client.orfield(table, r[0], f_mask, bit)
                    v = list(r)
                    v[f_mask] = mask | bit
                    rows.append(v)
        if rows:
            cols = COLUMNS[sql_table]
            body = ",\n".join("(" + ", ".join(str(i32(x)) for x in v) + ")" for v in rows)
            sql.raw(f"INSERT INTO `{sql_table}` ({', '.join(f'`{c}`' for c in cols)}) VALUES\n{body}\n"
                    f"ON DUPLICATE KEY UPDATE {or_into('RaceMask')};")

    sql.comment("Standing: the start race's (the Exodar's for the void elves, Undercity's for the nightborne).")
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
                if mask & (1 << (START[race] - 1)):
                    v[2 + slot] |= BIT[race]
        if v != list(r):
            for slot in range(4):
                if v[2 + slot] != r[2 + slot]:
                    client.orfield("Faction", r[0], 2 + slot, v[2 + slot] & ~r[2 + slot])
            faction_rows.append(dbc_row_values(factions, v, ft))
    # (merged, not replaced: the Skyborne's SQL changes the same rows, and until 1.0.328 whichever was put in
    # last took the other's races' bits out of the reputations' rows)
    sql.merge_masks("faction_dbc", COLUMNS["faction_dbc"], ft, faction_rows,
                    [f"ReputationRaceMask_{n}" for n in range(1, 5)])

    # The intros: the start race's flight, their own narration (the user's MP3s) -----------------
    seqs, cams = D("CinematicSequences"), D("CinematicCamera")
    seq_rows = {r[0]: r for r in seqs.rows}
    cam_rows = {r[0]: r for r in cams.rows}
    narration_rows, cam_sql, seq_sql = [], [], []
    for race in RACE_IDS:
        sound = narration_sound(dbc_row_values(sounds, snd_rows[3840], snt), race)  # HumanFlyByNarration
        client.put("SoundEntries", snt, sound)
        narration_rows.append(sound)
        seq = seq_rows[race_rows[START[race]][12]]
        cam = dbc_row_values(cams, cam_rows[seq[2]], TYPES["cinematiccamera_dbc"])
        cam[0], cam[2] = ID_CAMERA[race], ID_NARRATION[race]
        client.put("CinematicCamera", TYPES["cinematiccamera_dbc"], cam)
        cam_sql.append(cam)
        s = [ID_SEQUENCE[race], seq[1], ID_CAMERA[race]] + [0] * 7
        client.put("CinematicSequences", "i" * 10, s)
        seq_sql.append(s)
    sql.comment("The intros: the start race's flight over its home, with each race's own narration.")
    sql.replace("soundentries_dbc", COLUMNS["soundentries_dbc"], snt, narration_rows)
    sql.replace("cinematiccamera_dbc", COLUMNS["cinematiccamera_dbc"], TYPES["cinematiccamera_dbc"], cam_sql)
    sql.replace("cinematicsequences_dbc", COLUMNS["cinematicsequences_dbc"], TYPES["cinematicsequences_dbc"], seq_sql)

    # The racials -----------------------------------------------------------------------------------
    spells = D("Spell")
    spt = TYPES["spell_dbc"]
    by_id = {r[0]: r for r in spells.rows}
    C = {n: i for i, n in enumerate(COLUMNS["spell_dbc"])}

    def spell(template, sid, name, rank, description, aura_text, **fields):
        v = dbc_row_values(spells, by_id[template], spt)
        v[0] = sid
        for k in ("Name", "NameSubtext", "Description", "AuraDescription"):
            for i in range(16):
                v[C[f"{k}_Lang_enUS"] + i] = ""
        v[C["Name_Lang_enUS"]] = name
        v[C["NameSubtext_Lang_enUS"]] = rank
        v[C["Description_Lang_enUS"]] = description
        v[C["AuraDescription_Lang_enUS"]] = aura_text
        for k, value in fields.items():
            v[C[k]] = value
        client.put("Spell", spt, v)
        return v

    # Templates: 130 (Slow Fall: an instant self spell), 20550 (Endurance) and 20557 (Beast
    # Slaying), the Tauren's and Trolls' passives; 54710 (MOLL-E, the portable mailbox); 20549
    # (War Stomp, around the caster).
    no_cost = dict(Reagent_1=0, ReagentCount_1=0, ManaCostPct=0, SpellClassSet=0, SpellClassMask_1=0,
                   SpellClassMask_2=0, SpellClassMask_3=0, BaseLevel=1, SpellLevel=1, RangeIndex=1,
                   ImplicitTargetA_1=1, CastingTimeIndex=1, StartRecoveryCategory=133, StartRecoveryTime=1500,
                   SchoolMask=32, Attributes=0x10, AttributesEx=0, AttributesEx6=0, InterruptFlags=0, DispelType=0)
    ALL_SCHOOLS, MAGIC_SCHOOLS, SHADOW, ARCANE, HOLY = 127, 126, 32, 64, 2
    spell_rows = [
        spell(130, SPELLS["rift"], "Spatial Rift", "Racial",
              "Tear a rift in space up to 15 yards ahead. Use this ability again within 6 sec to teleport through the rift. 3 min cooldown once the rift closes.", "",
              SpellIconID=87, Effect_1=3, EffectAura_1=0, EffectBasePoints_1=0, EffectDieSides_1=0, SpellVisualID_1=0, DurationIndex=0,
              RecoveryTime=0, **no_cost),
        spell(130, SPELLS["rift_open"], "Spatial Rift", "",
              "A rift stands open. Use Spatial Rift again to teleport through it.", "A rift stands open. Use Spatial Rift again to teleport through it.",
              SpellIconID=87, Effect_1=6, EffectAura_1=4, EffectBasePoints_1=0, EffectDieSides_1=0, SpellVisualID_1=0, DurationIndex=32,
              **dict(no_cost, Attributes=0, StartRecoveryCategory=0, StartRecoveryTime=0)),
        spell(20550, SPELLS["entropic"], "Entropic Embrace", "Racial Passive",
              "Your abilities have a chance to empower you with the essence of the Void, increasing your damage and healing by 5% for 12 sec.", "",
              SpellIconID=164, EffectAura_1=42, EffectBasePoints_1=0, EffectDieSides_1=0, EffectTriggerSpell_1=SPELLS["entropic_buff"],
              ProcTypeMask=0x55554, ProcChance=10, SchoolMask=SHADOW),
        spell(20550, SPELLS["entropic_buff"], "Entropic Embrace", "",
              "Damage and healing done increased by 5%.", "Damage and healing done increased by 5%.",
              SpellIconID=164, EffectAura_1=79, EffectBasePoints_1=4, EffectDieSides_1=1, EffectMiscValue_1=ALL_SCHOOLS,
              Effect_2=6, EffectAura_2=136, EffectBasePoints_2=4, EffectDieSides_2=1, ImplicitTargetA_2=1,
              DurationIndex=29, Attributes=0, SchoolMask=SHADOW),
        spell(20557, SPELLS["chill"], "Chill of Night", "Racial Passive",
              "Reduces Shadow damage taken by 1%.", "",
              SpellIconID=207, EffectAura_1=87, EffectBasePoints_1=-2, EffectDieSides_1=1, EffectMiscValue_1=SHADOW),
        spell(20557, SPELLS["calm"], "Preternatural Calm", "Racial Passive",
              "Your spell casts are not delayed by taking damage.", "",
              SpellIconID=2014, EffectAura_1=149, EffectBasePoints_1=99, EffectDieSides_1=1, EffectMiscValue_1=0),
        spell(54710, SPELLS["cantrips"], "Cantrips", "Racial",
              "Conjure up an Eldritch Grimoire, allowing you mail access for 10 min.", "",
              SpellIconID=2030, RecoveryTime=600000, CastingTimeIndex=5, ManaCost=0, ManaCostPct=0, Reagent_1=0, ReagentCount_1=0,
              Attributes=0x10, SchoolMask=SHADOW, BaseLevel=1, SpellLevel=1),
        spell(20549, SPELLS["pulse"], "Arcane Pulse", "Racial",
              "Deals Arcane damage to nearby enemies within 8 yards and reduces their movement speed by 50% for 12 sec.", "",
              SpellIconID=2294, Effect_1=2, EffectAura_1=0, EffectBasePoints_1=19, EffectDieSides_1=1, EffectRealPointsPerLevel_1=2.0,
              ImplicitTargetA_1=22, ImplicitTargetB_1=15, EffectRadiusIndex_1=14, EffectMechanic_1=0, Mechanic=0,
              Effect_2=64, EffectAura_2=0, EffectBasePoints_2=0, EffectDieSides_2=0, EffectTriggerSpell_2=SPELLS["pulse_slow"],
              ImplicitTargetA_2=1, ImplicitTargetB_2=0, RecoveryTime=180000, DurationIndex=0, SchoolMask=ARCANE, DispelType=0,
              CastingTimeIndex=1, StartRecoveryCategory=133, StartRecoveryTime=1500, Attributes=0x10),
        spell(20549, SPELLS["pulse_slow"], "Arcane Pulse", "",
              "Movement speed reduced by 50%.", "Movement speed reduced by 50%.",
              SpellIconID=2294, Effect_1=6, EffectAura_1=33, EffectBasePoints_1=-51, EffectDieSides_1=1, EffectMiscValue_1=0,
              ImplicitTargetA_1=22, ImplicitTargetB_1=15, EffectRadiusIndex_1=14, EffectMechanic_1=11, Mechanic=11,
              RecoveryTime=0, DurationIndex=29, SchoolMask=ARCANE, DispelType=1, Attributes=0, StartRecoveryCategory=0, StartRecoveryTime=0),
        spell(20557, SPELLS["arcane_res"], "Arcane Resistance", "Racial Passive",
              "Reduces Arcane damage taken by 1%.", "",
              SpellIconID=1918, EffectAura_1=87, EffectBasePoints_1=-2, EffectDieSides_1=1, EffectMiscValue_1=ARCANE),
        spell(20557, SPELLS["affinity"], "Magical Affinity", "Racial Passive",
              "Increases magical damage dealt by 1%.", "",
              SpellIconID=2120, EffectAura_1=79, EffectBasePoints_1=0, EffectDieSides_1=1, EffectMiscValue_1=MAGIC_SCHOOLS),
        spell(20557, SPELLS["history"], "Ancient History", "Racial Passive",
              "Inscription skill increased by 15.", "",
              SpellIconID=3267, EffectAura_1=98, EffectBasePoints_1=14, EffectDieSides_1=1, EffectMiscValue_1=773),
        # Lightforged Draenei
        spell(130, SPELLS["judgment"], "Light's Judgment", "Racial",
              "Call down a strike of Holy energy where you stand (on your target, if you have one), dealing Holy damage to enemies within 5 yards after 3 sec. 3 min cooldown.", "",
              SpellIconID=156, Effect_1=3, EffectAura_1=0, EffectBasePoints_1=0, EffectDieSides_1=0, SpellVisualID_1=0, DurationIndex=0,
              RecoveryTime=180000, **dict(no_cost, SchoolMask=HOLY)),
        spell(20549, SPELLS["judgment_strike"], "Light's Judgment", "",
              "Holy damage to enemies within 5 yards.", "",
              SpellIconID=156, Effect_1=2, EffectAura_1=0, EffectBasePoints_1=39, EffectDieSides_1=1, EffectRealPointsPerLevel_1=6.0,
              ImplicitTargetA_1=87, ImplicitTargetB_1=16, EffectRadiusIndex_1=8, EffectMechanic_1=0, Mechanic=0, RangeIndex=13,
              Effect_2=0, EffectAura_2=0, EffectBasePoints_2=0, EffectDieSides_2=0, EffectTriggerSpell_2=0, ImplicitTargetA_2=0,
              RecoveryTime=0, DurationIndex=0, SchoolMask=HOLY, DispelType=0, CastingTimeIndex=1, StartRecoveryCategory=0,
              StartRecoveryTime=0, Attributes=0x10),
        spell(20557, SPELLS["forge"], "Forge of Light", "Racial Passive",
              "Blacksmithing skill increased by 10.", "",
              SpellIconID=335, EffectAura_1=98, EffectBasePoints_1=9, EffectDieSides_1=1, EffectMiscValue_1=164),
        spell(20557, SPELLS["reckoning"], "Light's Reckoning", "Racial Passive",
              "When you die, Holy energy bursts from you, dealing Holy damage to enemies and healing allies within 8 yards.", "",
              SpellIconID=121, EffectAura_1=4, EffectBasePoints_1=0, EffectDieSides_1=1, EffectMiscValue_1=0),
        spell(20549, SPELLS["reckoning_burst"], "Light's Reckoning", "",
              "Holy damage to enemies, healing to allies, within 8 yards.", "",
              SpellIconID=121, Effect_1=2, EffectAura_1=0, EffectBasePoints_1=59, EffectDieSides_1=1, EffectRealPointsPerLevel_1=8.0,
              ImplicitTargetA_1=22, ImplicitTargetB_1=15, EffectRadiusIndex_1=14, EffectMechanic_1=0, Mechanic=0,
              Effect_2=10, EffectAura_2=0, EffectBasePoints_2=59, EffectDieSides_2=1, EffectRealPointsPerLevel_2=8.0, EffectTriggerSpell_2=0,
              ImplicitTargetA_2=22, ImplicitTargetB_2=30, EffectRadiusIndex_2=14,
              RecoveryTime=0, DurationIndex=0, SchoolMask=HOLY, DispelType=0, CastingTimeIndex=1, StartRecoveryCategory=0,
              StartRecoveryTime=0, Attributes=0x10),
        spell(20557, SPELLS["holy_res"], "Holy Resistance", "Racial Passive",
              "Reduces Holy damage taken by 1%.", "",
              SpellIconID=329, EffectAura_1=87, EffectBasePoints_1=-2, EffectDieSides_1=1, EffectMiscValue_1=HOLY),
        spell(20557, SPELLS["demonbane"], "Demonbane", "Racial Passive",
              "Experience gained from killing Demons increased by 20%.", "",
              SpellIconID=545, EffectAura_1=4, EffectBasePoints_1=0, EffectDieSides_1=1, EffectMiscValue_1=0),
        # Zandalari Trolls
        spell(20550, SPELLS["regeneratin"], "Regeneratin'", "Racial",
              "Regenerate 100% of your maximum health over 6 sec. Taking damage interrupts it. 2.5 min cooldown.", "Regeneratin' health.",
              SpellIconID=123, Effect_1=6, EffectAura_1=20, EffectBasePoints_1=16, EffectDieSides_1=1, EffectAuraPeriod_1=1000,
              ImplicitTargetA_1=1, ImplicitTargetB_1=0, DurationIndex=32, RecoveryTime=150000, Attributes=0x10,
              InterruptFlags=0, AuraInterruptFlags=0x2, SchoolMask=1, CastingTimeIndex=1, StartRecoveryCategory=133, StartRecoveryTime=1500,
              BaseLevel=1, SpellLevel=1, RangeIndex=1),
        spell(20550, SPELLS["paku"], "Embrace of Pa'ku", "Racial Passive",
              "Your attacks and abilities have a chance to grant you 4% critical strike for 12 sec.", "",
              SpellIconID=1661, EffectAura_1=42, EffectBasePoints_1=0, EffectDieSides_1=0, EffectTriggerSpell_1=SPELLS["paku_buff"],
              ProcTypeMask=0x55554, ProcChance=10, SchoolMask=1),
        spell(20550, SPELLS["paku_buff"], "Embrace of Pa'ku", "",
              "Critical strike chance increased by 4%.", "Critical strike chance increased by 4%.",
              SpellIconID=1661, EffectAura_1=57, EffectBasePoints_1=3, EffectDieSides_1=1, EffectMiscValue_1=0,
              Effect_2=6, EffectAura_2=52, EffectBasePoints_2=3, EffectDieSides_2=1, ImplicitTargetA_2=1,
              DurationIndex=29, Attributes=0, SchoolMask=1),
        spell(130, SPELLS["swoop"], "Pterrordax Swoop", "Racial",
              "Reduces your falling speed for 2 min. 15 min cooldown.", "Falling slowly.",
              SpellIconID=505, DurationIndex=4, RecoveryTime=900000, **dict(no_cost, SchoolMask=1, Attributes=0x10)),
        spell(20557, SPELLS["city_of_gold"], "City of Gold", "Racial Passive",
              "Gold looted from creatures increased by 2%.", "",
              SpellIconID=2801, EffectAura_1=4, EffectBasePoints_1=0, EffectDieSides_1=1, EffectMiscValue_1=0),
    ]
    sql.comment("Their racials: Spatial Rift (with its open-rift mark), Entropic Embrace (with its buff), Chill of Night,\n"
                "Preternatural Calm, Cantrips; Arcane Pulse (with its slow), Arcane Resistance, Magical Affinity, Ancient History;\n"
                "Light's Judgment (with its strike), Forge of Light, Light's Reckoning (with its burst), Holy Resistance, Demonbane;\n"
                "Regeneratin', Embrace of Pa'ku (with its buff), Pterrordax Swoop, City of Gold.")
    sql.replace("spell_dbc", COLUMNS["spell_dbc"], spt, spell_rows)
    sql.raw(f"DELETE FROM `spell_proc` WHERE `SpellId` IN ({SPELLS['entropic']}, {SPELLS['paku']});\n"
            f"INSERT INTO `spell_proc` (`SpellId`, `SchoolMask`, `SpellFamilyName`, `SpellFamilyMask0`, `SpellFamilyMask1`, `SpellFamilyMask2`, "
            f"`ProcFlags`, `SpellTypeMask`, `SpellPhaseMask`, `HitMask`, `AttributesMask`, `DisableEffectsMask`, `ProcsPerMinute`, `Chance`, `Cooldown`, `Charges`) VALUES\n"
            f"({SPELLS['entropic']}, 0, 0, 0, 0, 0, 0x55554, 0, 2, 0, 0, 0, 0, 10, 30000, 0),\n"
            f"({SPELLS['paku']}, 0, 0, 0, 0, 0, 0x55554, 0, 2, 0, 0, 0, 0, 10, 30000, 0);")
    sql.raw(f"DELETE FROM `spell_script_names` WHERE `spell_id` IN ({SPELLS['rift']}, {SPELLS['rift_open']}, {SPELLS['judgment']});\n"
            f"INSERT INTO `spell_script_names` (`spell_id`, `ScriptName`) VALUES ({SPELLS['rift']}, 'spell_allied_spatial_rift'), "
            f"({SPELLS['rift_open']}, 'spell_allied_spatial_rift_open'), ({SPELLS['judgment']}, 'spell_allied_lights_judgment');")
    sql.comment("Spatial Rift's rift: a creature that stands where the rift is torn (AlliedRacesSpells.cpp). Light's Judgment's\n"
                "strike and Light's Reckoning's burst are the player's own casts; the unseen creatures earlier releases cast them\n"
                "with are deleted.")
    sql.raw(f"DELETE FROM `creature_template` WHERE `entry` IN ({NPC_RIFT}, {NPC_JUDGMENT}, {NPC_RECKONING});\n"
            f"INSERT INTO `creature_template` (`entry`, `name`, `subname`, `minlevel`, `maxlevel`, `faction`, `npcflag`, `unit_flags`, `type`, `type_flags`, "
            f"`MovementType`, `flags_extra`, `AIName`, `ScriptName`, `VerifiedBuild`) VALUES\n"
            f"({NPC_RIFT}, 'Spatial Rift', '', 1, 1, 35, 0, 33554434, 10, 0, 0, 130, '', '', 12340);\n"
            f"DELETE FROM `creature_template_model` WHERE `CreatureID` IN ({NPC_RIFT}, {NPC_JUDGMENT}, {NPC_RECKONING});\n"
            f"INSERT INTO `creature_template_model` (`CreatureID`, `Idx`, `CreatureDisplayID`, `DisplayScale`, `Probability`, `VerifiedBuild`) VALUES\n"
            f"({NPC_RIFT}, 0, {DISPLAY_RIFT}, 1, 1, 12340);")

    # WoW: Forever's racials for the eight races of 1.x --------------------------------------------
    def effects(*specs, **extra):
        """Effects 1 to 3 (the rest cleared): each (effect, aura, amount, misc, more fields), the amount as
        the tooltip has it (base points one less, one die side)."""
        f = {}
        for n in range(1, 4):
            spec = specs[n - 1] if n <= len(specs) else None
            effect, aura, amount, misc, more = (spec + (0, 0, 0, 0, {})[len(spec):]) if spec else (0, 0, 0, 0, {})
            f.update({f"Effect_{n}": effect, f"EffectAura_{n}": aura, f"EffectBasePoints_{n}": amount - 1 if effect else 0,
                      f"EffectDieSides_{n}": 1 if effect else 0, f"EffectMiscValue_{n}": misc, f"EffectMiscValueB_{n}": 0,
                      f"ImplicitTargetA_{n}": 1 if effect else 0, f"ImplicitTargetB_{n}": 0, f"EffectRadiusIndex_{n}": 0,
                      f"EffectTriggerSpell_{n}": 0, f"EffectAuraPeriod_{n}": 0, f"EffectRealPointsPerLevel_{n}": 0.0,
                      f"EffectMechanic_{n}": 0, f"EffectSpellClassMaskA_{n}": 0, f"EffectSpellClassMaskB_{n}": 0,
                      f"EffectSpellClassMaskC_{n}": 0, f"EffectChainTargets_{n}": 0, f"EffectItemType_{n}": 0})
            f.update(more)
        f.update(extra)
        return f

    AURA, TRIGGER, DISPEL, DISPEL_MECHANIC, DUMMY, LEECH = 6, 64, 38, 108, 3, 9
    PHYSICAL, ALL = 1, 127
    passive = dict(DurationIndex=21, RecoveryTime=0, CategoryRecoveryTime=0, Category=0, ProcTypeMask=0, ProcChance=101,
                   SpellVisualID_1=0)
    active = dict(Attributes=0x10, AttributesEx=0, AttributesEx2=0, CastingTimeIndex=1, RangeIndex=1, Category=0,
                  CategoryRecoveryTime=0, StartRecoveryCategory=133, StartRecoveryTime=1500, PowerType=0, ManaCost=0,
                  ManaCostPct=0, BaseLevel=1, SpellLevel=1, ProcTypeMask=0, ProcChance=101, PreventionType=2)
    D_INF, D_2, D_3, D_6, D_8, D_10, D_15, D_30 = 21, 39, 27, 32, 31, 1, 8, 9
    icon = lambda sid: by_id[sid][C["SpellIconID"]]
    every_spell = (0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF)
    family = {PRIEST: 6, MAGE: 3, WARLOCK: 5, WARRIOR: 4, ROGUE: 8}

    def class_mod(n, op, amount):
        """Effect n: Add Pct Modifier on every spell of the class (SpellClassSet)."""
        return (AURA, 108, amount, op, {f"EffectSpellClassMaskA_{n}": every_spell[0], f"EffectSpellClassMaskB_{n}": every_spell[1],
                                         f"EffectSpellClassMaskC_{n}": every_spell[2]})

    F = FOREVER
    forever_rows = [
        # Human
        spell(59752, F["will_to_survive"], "Will to Survive", "Racial", "Instantly removes all Stun effects.", "",
              **effects((DISPEL_MECHANIC, 0, 1, 12)), **dict(active, AttributesEx=163840, AttributesEx5=393224, RecoveryTime=180000,
                                                              DurationIndex=0, SpellVisualID_1=86, SpellIconID=icon(59752))),
        spell(20598, F["ruthless"], "Ruthless", "Racial Passive", "Increases your critical strike chance with all spells and attacks by 2%.", "",
              **effects((AURA, 290, 2)), **passive, SpellIconID=icon(20597)),
        spell(20598, 20598, "The Human Spirit", "Racial Passive", "Spirit increased by $s1%.", "", **effects((AURA, 137, 5, 4))),
        # Orc
        spell(20572, F["blood_fury"], "Blood Fury", "Racial", "Increases Attack Power and Spell Power by 10% for $d.",
              "Attack Power and Spell Power increased by 10%.",
              **effects((AURA, 166, 10), (AURA, 167, 10), (TRIGGER, 0, 0, 0, {"EffectTriggerSpell_3": F["blood_fury_sp"]})),
              **dict(active, RecoveryTime=180000, DurationIndex=D_15, AttributesEx=32, AttributesEx2=147456, SpellIconID=icon(20572),
                     SpellVisualID_1=47)),
        spell(20572, F["blood_fury_sp"], "Blood Fury", "", "Spell Power increased by 10%.", "Spell Power increased by 10%.",
              **effects((AURA, 13, 0, 126), (AURA, 135, 0, 127)),
              **dict(active, Attributes=0x80, RecoveryTime=0, DurationIndex=D_15, StartRecoveryCategory=0, StartRecoveryTime=0,
                     SpellIconID=icon(20572), SpellVisualID_1=0)),
        spell(20573, 20573, "Hardiness", "Racial Passive", "Duration of Stun effects on you reduced by 20%.", "",
              **effects((AURA, 232, -20, 12))),
        spell(20598, F["savage"], "Savage", "Racial Passive", "Increases your critical strike chance with all spells and abilities by 1%.", "",
              **effects((AURA, 290, 1)), **passive, SpellIconID=icon(20574)),
        spell(26297, F["shatter_curse"], "Shatter Curse", "Racial",
              "Instantly removes all Curses, and reduces all Magical damage taken by 5% for $d.", "Reduces Magical damage taken by 5%.",
              **effects((AURA, 87, -5, 126), (DISPEL, 0, 99, 2)),
              **dict(active, RecoveryTime=180000, DurationIndex=D_8, SpellIconID=icon(475), SpellVisualID_1=0)),
        # Dwarf: Stoneform's immunities last 8 sec now, and its second part (65116) reduces Physical damage
        # taken instead of raising armour
        spell(20594, 20594, "Stoneform", "Racial",
              "Instantly removes and grants immunity to all Bleed, Poison, and Disease effects, and reduces all Physical damage taken by 10% for $d.",
              "Immune to Bleed, Poison, and Disease effects. Reduces Physical damage taken by 10%.",
              RecoveryTime=180000, DurationIndex=D_8),
        spell(65116, 65116, "Stoneform", "", "Reduces Physical damage taken by 10%.", "Reduces Physical damage taken by 10%.",
              **effects((AURA, 87, -10, PHYSICAL))),
        spell(20598, F["earth_fury"], "Earth Fury", "Racial Passive", "Increases your critical strike bonus to damage and healing by 2%.", "",
              **effects((AURA, 163, 2, ALL), (AURA, 50, 2)), **passive, SpellIconID=icon(59224)),
        spell(20557, F["big_game_hunter"], "Big Game Hunter", "Racial Passive", "Damage dealt versus Beasts increased by $s1%.", "",
              SpellIconID=icon(20595)),
        # Night Elf
        spell(26297, F["elunes_light"], "Elune's Light", "Racial", "Increases your critical strike chance with all spells and attacks by 10% for $d.",
              "Critical strike chance with all spells and attacks increased by 10%.",
              **effects((AURA, 290, 10)), **dict(active, RecoveryTime=180000, DurationIndex=D_15, SpellIconID=icon(8921), SpellVisualID_1=0)),
        spell(20598, F["quickness"], "Quickness", "Racial Passive",
              "Dodge chance increased by 1% and movement speed increased by 2%. Night Elf Rogues and Druids are harder to detect in Stealth as if they were 1 level higher.", "",
              **effects((AURA, 49, 1), (AURA, 129, 2), (AURA, 154, 5)), **passive, SpellIconID=icon(20582)),
        # (in combat its cooldown is 2 min: AlliedRacesForever.cpp)
        spell(58984, 58984, "Shadowmeld", "Racial",
              "Activate to slip into the shadows, reducing the chance for enemies to detect your presence. Lasts until cancelled or upon moving. Using this ability in combat discourages enemies from attacking you, but increases the cooldown to 2 min.",
              "Shadowmelded.", RecoveryTime=10000),
        # Undead
        spell(20598, F["grave_melee"], "Touch of the Grave", "Racial Passive",
              "Your spells and attacks have a 20% chance to drain Health from the target, up to 5% of your maximum Health.", "",
              **effects((AURA, 4, 5)), **dict(passive, ProcTypeMask=0x55554, ProcChance=20), SpellIconID=icon(20579)),
        spell(20598, F["grave_caster"], "Touch of the Grave", "Racial Passive",
              "Your spells and attacks have a 30% chance to drain Health from the target, up to 5% of your maximum Health.", "",
              **effects((AURA, 4, 5)), **dict(passive, ProcTypeMask=0x55554, ProcChance=30), SpellIconID=icon(20579)),
        spell(20549, F["grave_drain"], "Touch of the Grave", "", "Drains Health from the target.", "",
              **effects((LEECH, 0, 1, 0, {"ImplicitTargetA_1": 6, "EffectMultipleValue_1": 1.0})),
              **dict(active, Attributes=0x10, AttributesEx=0, AttributesEx4=0, Mechanic=0, ShapeshiftMask=0, MaxTargets=0, RecoveryTime=0,
                     DurationIndex=0, CastingTimeIndex=1, RangeIndex=13, InterruptFlags=0, StartRecoveryCategory=0, StartRecoveryTime=0,
                     SchoolMask=32, SpellIconID=icon(20579), SpellVisualID_1=0, DefenseType=0, AttributesEx3=0x10000)),
        spell(5227, 5227, "Underwater Breathing", "Racial Passive", "Underwater breath lasts $s1% longer than normal.", "",
              **effects((AURA, 155, 300))),
        # Tauren
        spell(20549, 20549, "War Stomp", "Racial", "Stuns up to $i enemies within $a1 yds for $d.", "Stunned.", RecoveryTime=90000),
        spell(20550, 20550, "Endurance", "Racial Passive", "Total Health increased by 5% and critical strike bonus to damage and healing increased by 2%.", "",
              **effects((AURA, 282, 5), (AURA, 163, 2, ALL), (AURA, 50, 2))),
        spell(20577, F["cultivation"], "Cultivation", "Racial",
              "Cultivate a nearby herb, growing a duplicate you can harvest without requiring Herbalism skill. Each herb may only be cultivated once.", "",
              **effects((DUMMY, 0, 15)), **dict(active, AttributesEx=0, AttributesEx2=0, ShapeshiftMask=0, TargetCreatureType=0,
                                                CastingTimeIndex=14, RecoveryTime=900000, RangeIndex=7, SpellIconID=icon(20552),
                                                SpellVisualID_1=0, InterruptFlags=15)),
        spell(20598, F["plainsrunning"], "Plainsrunning", "Racial Passive",
              "Gain 1% increased movement speed every 5 sec spent moving, up to a maximum of 30% increase. Taking damage or standing still will reduce this effect. In addition, you move 3% faster while mounted.", "",
              **effects((AURA, 226, 1, 0, {"EffectAuraPeriod_1": 1000}), (AURA, 4, 5), (AURA, 130, 3)),
              **dict(passive, ProcTypeMask=0x100000, ProcChance=100), SpellIconID=icon(2983)),
        spell(2983, F["plainsrunning_speed"], "Plainsrunning", "", "Movement speed increased by 1%.", "Movement speed increased by $s1%.",
              **effects((AURA, 31, 1)), **dict(active, Attributes=0, RecoveryTime=0, DurationIndex=D_INF, StartRecoveryCategory=0,
                                               StartRecoveryTime=0, CumulativeAura=30, SpellIconID=icon(2983), SpellVisualID_1=0)),
        # Gnome
        spell(20593, 20593, "Engineering Specialization", "Racial Passive",
              "Your gnomish ingenuity reduces the rate of engineering devices failing or backfiring when you use them by 20%.", "",
              **effects((AURA, 4, 20))),
        spell(20589, 20589, "Escape Artist", "Racial",
              "Instantly escape the effects of any movement impairing effect and gain immunity to those effects for $d.",
              "Immune to movement impairing effects.",
              **effects((77, 0, 0), (AURA, 77, 1, 7), (AURA, 77, 1, 11)), RecoveryTime=120000, DurationIndex=D_3),
        spell(20598, F["mind_mana"], "Expansive Mind", "Racial Passive", "Maximum Mana increased by 5%.", "",
              **effects((AURA, 132, 5, 0)), **passive, SpellIconID=icon(20591)),
        spell(20598, F["mind_rage"], "Expansive Mind", "Racial Passive", "Maximum Rage increased by 5%.", "",
              **effects((AURA, 132, 5, 1)), **passive, SpellIconID=icon(20591)),
        spell(20598, F["mind_energy"], "Expansive Mind", "Racial Passive", "Maximum Energy increased by 5%.", "",
              **effects((AURA, 132, 5, 3)), **passive, SpellIconID=icon(20591)),
        spell(20598, F["mind_runic"], "Expansive Mind", "Racial Passive", "Maximum Runic Power increased by 5%.", "",
              **effects((AURA, 132, 5, 6)), **passive, SpellIconID=icon(20591)),
    ]
    eureka = {PRIEST: ("eureka_priest", "Mana", "non-periodic damaging or healing abilities", "deal 10% more damage or healing"),
              MAGE: ("eureka_mage", "Mana", "damaging abilities", "deal 10% more damage"),
              WARLOCK: ("eureka_warlock", "Mana", "non-periodic damaging abilities", "deal 10% more damage"),
              WARRIOR: ("eureka_warrior", "Rage", "non-periodic damaging abilities", "deal 10% more damage"),
              ROGUE: ("eureka_rogue", "Energy", "non-periodic damaging abilities", "deal 10% more damage")}
    for cls, (key, power, what, more) in eureka.items():
        mods = [class_mod(1, 14, -10), class_mod(2, 0, 10)]
        if cls == MAGE:
            mods.append(class_mod(3, 22, 10))            # (the mage's periodic damage too)
        forever_rows.append(spell(26297, F[key], "Eureka!", "Racial",
                                  f"Your {what} have their {power} cost reduced by 10% and {more} for $d.",
                                  f"{what[0].upper() + what[1:]} cost 10% less {power} and {more}.",
                                  **effects(*mods), **dict(active, RecoveryTime=120000, DurationIndex=D_8, SpellClassSet=family[cls],
                                                           SchoolMask=8, DispelType=1, SpellIconID=icon(20593), SpellVisualID_1=0)))
    # The gnome priest's own: Confounding Flash (level 10) and Contingency Plan (level 20 on, five ranks)
    forever_rows.append(spell(20549, F["confounding_flash"], "Confounding Flash", "Racial",
                              "Confuses up to $i enemies within $a1 yds for $d. Any damage taken will break the effect.", "Confused.",
                              **effects((AURA, 5, 0, 0, {"ImplicitTargetA_1": 18, "ImplicitTargetB_1": 16, "EffectRadiusIndex_1": 14})),
                              **dict(Mechanic=2, CastingTimeIndex=3, RecoveryTime=120000, DurationIndex=D_3, ManaCostPct=3, PowerType=0,
                                     BaseLevel=10, SpellLevel=10, AuraInterruptFlags=0x2, SchoolMask=2, MaxTargets=5, ShapeshiftMask=0,
                                     SpellIconID=icon(8122), SpellVisualID_1=0)))
    for rank, (ward, shield, heal, level, absorb, tick) in enumerate(zip(CONTINGENCY_WARD, CONTINGENCY_SHIELD, CONTINGENCY_HEAL, CONTINGENCY_LEVEL,
                                                                          CONTINGENCY_ABSORB, CONTINGENCY_TICK), 1):
        forever_rows.append(spell(17, ward, "Contingency Plan", f"Rank {rank}",
                                  f"Place a Holy ward on an ally for $d. The next time this ally takes damage dropping their Health below 35%, they will gain a shield absorbing {absorb} damage and begin healing for {tick * 5} Health over 15 sec. A target may be affected by only one Contingency Plan.",
                                  "Warded against damage taking Health below 35%.",
                                  **effects((AURA, 4, 35, 0, {"ImplicitTargetA_1": 21})),
                                  **dict(active, Attributes=0x10, RecoveryTime=600000, DurationIndex=D_30, RangeIndex=4, BaseLevel=level,
                                         ProcTypeMask=0x100000, ProcChance=100,
                                         SpellLevel=level, SchoolMask=2, DispelType=1, SpellClassSet=0, SpellClassMask_1=0, SpellClassMask_2=0,
                                         SpellClassMask_3=0, ManaCostPct=0, SpellIconID=icon(47788), SpellVisualID_1=0)))
        forever_rows.append(spell(17, shield, "Contingency Plan", f"Rank {rank}", f"Absorbing {absorb} damage.", f"Absorbing {absorb} damage.",
                                  **effects((AURA, 69, absorb, ALL)),
                                  **dict(active, Attributes=0x80, RecoveryTime=0, DurationIndex=D_15, RangeIndex=13, BaseLevel=level, SpellLevel=level,
                                         SchoolMask=2, DispelType=1, SpellClassSet=0, SpellClassMask_1=0, SpellClassMask_2=0, SpellClassMask_3=0,
                                         StartRecoveryCategory=0, StartRecoveryTime=0, SpellIconID=icon(47788), SpellVisualID_1=0)))
        forever_rows.append(spell(17, heal, "Contingency Plan", f"Rank {rank}", f"Healing {tick} damage every 3 sec.", f"Healing {tick} damage every 3 sec.",
                                  **effects((AURA, 8, tick, 0, {"EffectAuraPeriod_1": 3000})),
                                  **dict(active, Attributes=0x80, RecoveryTime=0, DurationIndex=D_15, RangeIndex=13, BaseLevel=level, SpellLevel=level,
                                         SchoolMask=2, DispelType=1, SpellClassSet=0, SpellClassMask_1=0, SpellClassMask_2=0, SpellClassMask_3=0,
                                         StartRecoveryCategory=0, StartRecoveryTime=0, SpellIconID=icon(47788), SpellVisualID_1=0)))
    forever_rows += [
        # Troll
        spell(26297, 26297, "Berserking", "Racial", "Increases your spellcasting and attack speed by $s1% for $d.",
              "Spellcasting and attack speed increased by $s1%.", **effects((AURA, 193, 10))),
        spell(20555, 20555, "Regeneration", "Racial Passive",
              "Health regeneration rate increased by $s1%. In addition, $s2% of total Health regeneration will continue during combat.", "",
              **effects((AURA, 88, 20), (AURA, 116, 20))),
        spell(20578, F["rapid_regeneration"], "Rapid Regeneration", "Racial",
              "Regenerate 50% of your maximum Health over $d. Any movement, action, or damage taken will cancel the effect.",
              "Regenerating 50% of maximum Health over $d.",
              **effects((AURA, 20, 10, 0, {"EffectAuraPeriod_1": 1200})),
              **dict(active, Attributes=0x10, AttributesEx=536870976, RecoveryTime=180000, DurationIndex=D_6, ChannelInterruptFlags=15374,
                     SpellIconID=icon(20555), SpellVisualID_1=by_id[20578][C["SpellVisualID_1"]])),
    ]
    sql.comment("WoW: Forever's racials for the eight races of 1.x (Forever 1.60.1, forever.warcraftdb.com): its new ones, and\n"
                "the changes to those 3.3.5 has (War Stomp's cooldown, Stoneform's immunities and Physical damage, Berserking's 10%...).")
    sql.replace("spell_dbc", COLUMNS["spell_dbc"], spt, forever_rows)
    sql.raw(f"DELETE FROM `spell_proc` WHERE `SpellId` IN ({F['grave_melee']}, {F['grave_caster']}, {F['plainsrunning']}, "
            f"{', '.join(str(w) for w in CONTINGENCY_WARD)});\n"
            f"INSERT INTO `spell_proc` (`SpellId`, `SchoolMask`, `SpellFamilyName`, `SpellFamilyMask0`, `SpellFamilyMask1`, `SpellFamilyMask2`, "
            f"`ProcFlags`, `SpellTypeMask`, `SpellPhaseMask`, `HitMask`, `AttributesMask`, `DisableEffectsMask`, `ProcsPerMinute`, `Chance`, `Cooldown`, `Charges`) VALUES\n"
            f"({F['grave_melee']}, 0, 0, 0, 0, 0, 0x55554, 1, 2, 0, 0, 0, 0, 20, 0, 0),\n"
            f"({F['grave_caster']}, 0, 0, 0, 0, 0, 0x55554, 1, 2, 0, 0, 0, 0, 30, 0, 0),\n"
            + ",\n".join(f"({sid}, 0, 0, 0, 0, 0, 0x100000, 0, 0, 0, 0, 0, 0, 100, 0, 0)" for sid in (F["plainsrunning"],) + CONTINGENCY_WARD) + ";")
    scripted = [(F["blood_fury_sp"], "spell_forever_blood_fury"), (58984, "spell_forever_shadowmeld"),
                (F["grave_melee"], "spell_forever_touch_of_the_grave"), (F["grave_caster"], "spell_forever_touch_of_the_grave"),
                (F["cultivation"], "spell_forever_cultivation"), (F["plainsrunning"], "spell_forever_plainsrunning")]
    scripted += [(ward, "spell_forever_contingency_plan") for ward in CONTINGENCY_WARD]
    sql.raw(f"DELETE FROM `spell_script_names` WHERE `ScriptName` LIKE 'spell\\_forever\\_%';\n"
            "INSERT INTO `spell_script_names` (`spell_id`, `ScriptName`) VALUES\n"
            + ",\n".join(f"({sid}, '{name}')" for sid, name in scripted) + ";")

    # Each race's racial line: its old abilities' rows given Forever's racials (the rest no longer taught: a
    # skill's spells are taught at each login, not kept, so a character loses the old ones at its next).
    sla = D("SkillLineAbility")
    slt = TYPES["skilllineability_dbc"]
    ability_rows, next_ability = [], ID_FOREVER_ABILITY
    for race, kit in FOREVER_KIT.items():
        line = RACIAL_LINE[race]
        old = [r for r in sla.rows if r[1] == line]
        for i, (sid, cmask) in enumerate(kit):
            if i < len(old):
                v = dbc_row_values(sla, old[i], slt)
            else:
                v = dbc_row_values(sla, old[0], slt)
                v[0] = next_ability
                next_ability += 1
            v[2], v[3], v[4], v[9] = sid, 1 << (race - 1), cmask, 1     # spell, race, class, taught with the skill
            client.put("SkillLineAbility", slt, v)
            ability_rows.append(v)
        for r in old[len(kit):]:
            v = dbc_row_values(sla, r, slt)
            v[9] = 0                                         # no longer taught
            client.put("SkillLineAbility", slt, v)
            ability_rows.append(v)
    sql.comment("Each race's racial skill line teaches Forever's racials (its rows, and new ones from 23500); the old ones no longer.")
    sql.replace("skilllineability_dbc", COLUMNS["skilllineability_dbc"], slt, ability_rows)
    sql.comment("New characters' action bars: Forever's racial where 3.3.5's stood (Will to Survive for Every Man for Himself,\n"
                "one Blood Fury for the orcs' three).")
    for race, olds, new in ((HUMAN, (59752,), F["will_to_survive"]), (ORC, (20572, 33697, 33702), F["blood_fury"])):
        sql.raw(f"UPDATE `playercreateinfo_action` SET `action` = {new} WHERE `race` = {race} AND `type` = 0 "
                f"AND `action` IN ({', '.join(str(o) for o in olds)});")

    # The world database: starts, skills, stats, quests, standing ----------------------------------
    sql.comment("Where they start (their start race's place), for every class (the death knights' at Ebon Hold).")
    cols, pci = sqlrows.table(os.path.join(world, "playercreateinfo.sql"))
    place = {(int(r["race"]), int(r["class"])): r for r in pci}
    out = []
    for race in RACE_IDS:
        for cls in CLASSES_OF[race]:
            p = place.get((START[race], cls)) or place[(START[race], WARRIOR)]
            out.append([race, cls, p["map"], p["zone"], p["position_x"], p["position_y"], p["position_z"], p["orientation"]])
    for race, classes in EXTRA_CLASSES.items():
        for cls in classes:
            p = place[(race, WARRIOR)]
            out.append([race, cls, p["map"], p["zone"], p["position_x"], p["position_y"], p["position_z"], p["orientation"]])
    sql.raw("REPLACE INTO `playercreateinfo` (`race`, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`) VALUES\n"
            + ",\n".join("(" + ", ".join(str(x) for x in r) + ")" for r in out) + ";")

    racial_spells = set()
    for r in D("SkillLineAbility").rows:
        if r[1] in racial_lines:
            racial_spells.add(r[2])
    sql.comment("Their action bars: the class's start race's, without that race's racials.")
    cols, acts = sqlrows.table(os.path.join(world, "playercreateinfo_action.sql"))
    out = []
    for race in RACE_IDS:
        for cls in CLASSES_OF[race]:
            for r in acts:
                if int(r["race"]) == TEMPLATE[race][cls] and int(r["class"]) == cls and not (int(r["type"]) == 0 and int(r["action"]) in racial_spells):
                    out.append([race, cls, r["button"], r["action"], r["type"]])
    like_racials = {r[2] for r in D("SkillLineAbility").rows if r[1] in racial_lines}
    for race, classes in EXTRA_CLASSES.items():
        for cls, like in classes.items():
            for r in acts:
                if int(r["race"]) == like and int(r["class"]) == cls and not (int(r["type"]) == 0 and int(r["action"]) in like_racials):
                    out.append([race, cls, r["button"], r["action"], r["type"]])
            sql.raw(f"DELETE FROM `playercreateinfo_action` WHERE `race` = {race} AND `class` = {cls};")
    sql.raw(f"DELETE FROM `playercreateinfo_action` WHERE `race` IN ({', '.join(str(r) for r in RACE_IDS)});")
    sql.raw("INSERT INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`) VALUES\n"
            + ",\n".join("(" + ", ".join(str(x) for x in r) + ")" for r in out) + ";")

    sql.comment("Their skills: their side's weapons and armour; Common or Orcish; no other race's racials. The rows are\n"
                "found by their stock races (the low eleven bits), as the Skyborne's SQL finds them: each adds its races'\n"
                "bits to the same rows, and an exact match finds nothing once the other has run (the Skyborne had no\n"
                "language, Swords or Two-Handed Swords up to 1.0.236 for that).")
    cols, skills = sqlrows.table(os.path.join(world, "playercreateinfo_skills.sql"))
    for r in skills:
        mask, skill = int(r["raceMask"]), int(r["skill"])
        if mask == 0:
            continue
        add = faction_bits(mask, skill)
        if add:
            sql.raw(f"UPDATE `playercreateinfo_skills` SET `raceMask` = `raceMask` | {add} WHERE (`raceMask` & 2047) = {mask & 2047} AND `classMask` = {r['classMask']} AND `skill` = {skill};")

    sql.comment("The old races' new classes: the class's own starting skills the race their start comes from has (a human\n"
                "hunter's Guns, as a dwarf hunter's).")
    for r in skills:
        mask, cmask, skill = int(r["raceMask"]), int(r["classMask"]), int(r["skill"])
        for race, classes in EXTRA_CLASSES.items():
            for cls, like in classes.items():
                bit, like_bit = 1 << (race - 1), 1 << (like - 1)
                if mask and cmask == 1 << (cls - 1) and mask & like_bit and not mask & bit:
                    sql.raw(f"UPDATE `playercreateinfo_skills` SET `raceMask` = `raceMask` | {bit} WHERE (`raceMask` & 2047) = {mask & 2047} "
                            f"AND `classMask` = {cmask} AND `skill` = {skill};")

    sql.comment("Their racials, learned at creation.")
    sql.raw(f"DELETE FROM `playercreateinfo_spell_custom` WHERE `Spell` BETWEEN {min(SPELLS.values())} AND {max(SPELLS.values())};")
    custom = [(BIT[VOIDELF], SPELLS["rift"], "Void Elf - Spatial Rift"), (BIT[VOIDELF], SPELLS["entropic"], "Void Elf - Entropic Embrace"),
              (BIT[VOIDELF], SPELLS["chill"], "Void Elf - Chill of Night"), (BIT[VOIDELF], SPELLS["calm"], "Void Elf - Preternatural Calm"),
              (BIT[VOIDELF], SPELLS["cantrips"], "Void Elf - Cantrips"),
              (BIT[NIGHTBORNE], SPELLS["pulse"], "Nightborne - Arcane Pulse"), (BIT[NIGHTBORNE], SPELLS["arcane_res"], "Nightborne - Arcane Resistance"),
              (BIT[NIGHTBORNE], SPELLS["affinity"], "Nightborne - Magical Affinity"), (BIT[NIGHTBORNE], SPELLS["history"], "Nightborne - Ancient History"),
              (BIT[LIGHTFORGED], SPELLS["judgment"], "Lightforged Draenei - Light's Judgment"), (BIT[LIGHTFORGED], SPELLS["forge"], "Lightforged Draenei - Forge of Light"),
              (BIT[LIGHTFORGED], SPELLS["reckoning"], "Lightforged Draenei - Light's Reckoning"), (BIT[LIGHTFORGED], SPELLS["holy_res"], "Lightforged Draenei - Holy Resistance"),
              (BIT[LIGHTFORGED], SPELLS["demonbane"], "Lightforged Draenei - Demonbane"),
              (BIT[ZANDALARI], SPELLS["regeneratin"], "Zandalari Troll - Regeneratin"), (BIT[ZANDALARI], SPELLS["paku"], "Zandalari Troll - Embrace of Paku"),
              (BIT[ZANDALARI], SPELLS["swoop"], "Zandalari Troll - Pterrordax Swoop"), (BIT[ZANDALARI], SPELLS["city_of_gold"], "Zandalari Troll - City of Gold")]
    sql.raw("INSERT INTO `playercreateinfo_spell_custom` (`racemask`, `classmask`, `Spell`, `Note`) VALUES\n"
            + ",\n".join(f"({m}, 0, {s}, {sqlrows.quote(n)})" for m, s, n in custom) + ";")

    sql.comment("Their stats: their kin's (the blood elves' for the void elves, the night elves' for the nightborne).")
    cols, stats = sqlrows.table(os.path.join(world, "player_race_stats.sql"))
    by_race = {int(r["Race"]): r for r in stats}
    sql.raw("REPLACE INTO `player_race_stats` (`Race`, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`) VALUES\n"
            + ",\n".join(f"({race}, " + ", ".join(by_race[STATS_FROM[race]][k] for k in ("Strength", "Agility", "Stamina", "Intellect", "Spirit")) + ")"
                         for race in RACE_IDS) + ";")

    sql.comment("Quests, items and conditions for their start race are theirs too (the Draenei's for the void elves, the\n"
                "Forsaken's for the nightborne), but for the start quests cloned for them (tools/quests.py), which stay the\n"
                "start race's alone; and those of the race their classes' starts come from where the start race hasn't the\n"
                "class (the Humans' rogues' and warlocks', the Blood Elves' hunters').")
    for race in RACE_IDS:
        b = BIT[race]
        s = 0
        for r in {START[race]} | set(TEMPLATE[race].values()):
            s |= 1 << (r - 1)
        cloned = CLONED.get(KEY[race], [])
        keep = f" AND `ID` NOT IN ({', '.join(str(q) for q in cloned)})" if cloned else ""
        sql.raw(f"UPDATE `quest_template` SET `AllowableRaces` = `AllowableRaces` | {b} WHERE `AllowableRaces` & {s} AND `AllowableRaces` & 0x7FFFFFFF <> 0x7FFFFFFF{keep};")
        sql.raw(f"UPDATE `item_template` SET `AllowableRace` = `AllowableRace` | {b} WHERE `AllowableRace` <> -1 AND `AllowableRace` & {s} AND `AllowableRace` & 0x7FFFFFFF <> 0x7FFFFFFF;")
        sql.raw(f"UPDATE `conditions` SET `ConditionValue1` = `ConditionValue1` | {b} WHERE `ConditionTypeOrReference` = 16 AND `ConditionValue1` & {s};")

    sql.comment("The old races' new classes: the class's own quests (one class's alone) of the race their start comes from are\n"
                "theirs too: a human hunter's taming lessons are a dwarf hunter's, a dwarf shaman's totems a Draenei shaman's.")
    for race, classes in EXTRA_CLASSES.items():
        for cls, like in classes.items():
            bit, like_bit = 1 << (race - 1), 1 << (like - 1)
            sql.raw(f"UPDATE `quest_template` q JOIN `quest_template_addon` a ON a.`ID` = q.`ID` SET q.`AllowableRaces` = q.`AllowableRaces` | {bit} "
                    f"WHERE a.`AllowableClasses` = {1 << (cls - 1)} AND q.`AllowableRaces` & {like_bit} AND q.`AllowableRaces` & 0x7FFFFFFF <> 0x7FFFFFFF;")

    # Write -----------------------------------------------------------------------------------------
    with open(os.path.join(MODULE, "data", "sql", "chromiecraft", "world", "allied_races_world.sql"), "w", newline="\n") as f:
        f.write("\n".join(sql.parts) + "\n")
    client.write(os.path.join(MODULE, "data", "client", "dbc"))
    print(f"{len(new_sections)} looks, {len(client.files)} tables, {len(spell_rows)} spells, {len(sound_sql)} voice sounds, {len(emote_rows)} emotes")


if __name__ == "__main__":
    main()
