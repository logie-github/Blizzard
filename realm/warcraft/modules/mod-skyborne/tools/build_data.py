#!/usr/bin/env python3
"""Builds the Skyborne's data from the game's own tables: the world database's SQL
(data/sql/db-world/skyborne_world.sql) and the changes the module makes to the game's tables and
textures as the realm starts (data/client/dbc/*.txt, data/client/textures.txt; SkyborneClient.cpp
reads them). Run it again when something here changes; its output is committed.

  build_data.py DBC_DIR WORLD_SQL_DIR

DBC_DIR: the server's dbc folder (the data.zip in warcraft/server-data.env); WORLD_SQL_DIR: the
core's data/sql/base/db_world at the realm's commit (warcraft/server-version.env).

The Skyborne (WoW: Forever's elves of the wind) are two races here, one for each side, both on the
blood elf's body:
  13  Skyborne of the High Order, Alliance: Humans' start in Northshire, their quests and standing
  14  Skyborne Windshapers, Horde: the Tauren's start at Camp Narache, their quests and standing
Races 13 and 14 were the game's Naga and Broken, which only creatures use: they move to 22 and 23
in the game's tables (their looks, their creatures' looks), out of the way. The blood elves get a
Dark Ranger skin.
"""

import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODULE = os.path.dirname(HERE)
COLUMNS = json.load(open(os.path.join(HERE, "dbc_columns.json")))
TYPES = json.load(open(os.path.join(HERE, "dbc_types.json")))

HUMAN, ORC, DWARF, NIGHTELF, UNDEAD, TAUREN, GNOME, TROLL, BLOODELF, DRAENEI = 1, 2, 3, 4, 5, 6, 7, 8, 10, 11
ALLIANCE, HORDE = 13, 14                       # the two Skyborne races
MOVED = {13: 22, 14: 23}                       # Naga, Broken: the creatures' races, moved
BIT = {ALLIANCE: 1 << 12, HORDE: 1 << 13}
ALLIANCE_MASK = sum(1 << (r - 1) for r in (HUMAN, DWARF, NIGHTELF, GNOME, DRAENEI))
HORDE_MASK = sum(1 << (r - 1) for r in (ORC, UNDEAD, TAUREN, TROLL, BLOODELF))
WARRIOR, PALADIN, HUNTER, ROGUE, PRIEST, DK, SHAMAN, MAGE, WARLOCK, DRUID = 1, 2, 3, 4, 5, 6, 7, 8, 9, 11
CLASSES = {ALLIANCE: (WARRIOR, HUNTER, ROGUE, MAGE, DRUID), HORDE: (WARRIOR, HUNTER, ROGUE, SHAMAN, DRUID)}
# Whose start each class takes (gear, action bars, place): the side's own race where it has the
# class, the nearest one where it doesn't.
TEMPLATE = {
    ALLIANCE: {WARRIOR: HUMAN, HUNTER: NIGHTELF, ROGUE: HUMAN, MAGE: HUMAN, DRUID: NIGHTELF},
    HORDE: {WARRIOR: TAUREN, HUNTER: TAUREN, ROGUE: BLOODELF, SHAMAN: TAUREN, DRUID: TAUREN},
}
START = {ALLIANCE: HUMAN, HORDE: TAUREN}
RACE_STATS = (-1, 1, -1, 1, 0)               # Strength, Agility, Stamina, Intellect, Spirit       # where they begin, whose quests and standing they share
FILESTRING = {ALLIANCE: "SkyborneA", HORDE: "SkyborneH"}

# Skin colours: the blood elf's ten, then the Skyborne's blues (colour index: name, hue, saturation,
# lightness), made from the blood elf's fairest skin (colour 0).
BLUES = {
    19: ("Sky", 0.54, 0.45, 1.15),
    20: ("Azure", 0.555, 0.50, 1.06),
    21: ("Cerulean", 0.565, 0.50, 0.97),
    22: ("Ocean", 0.57, 0.48, 0.87),
    23: ("Glacier", 0.58, 0.36, 0.95),
    24: ("Frost", 0.53, 0.25, 1.20),
}
DARK_RANGER = (19, ("Dark Ranger", 0.10, 0.85))   # the blood elf's new skin: its colours' saturation x0.10, lightness x0.85; red eyes
DARK_RANGER_EYES = (0.0, 1.0, 1.0)
# Eyes: each face twice, blue (faces 0-9) and yellow (10-19); never the blood elf's green.
EYES = [("blue", (0.56, 0.80, 1.15)), ("yellow", (0.13, 0.85, 1.20))]
# Hair colours: the blood elf's thirteen, then these, from its silver (colour 1).
HAIRS = {
    13: ("Snow", 0.60, 0.00, 1.25),
    14: ("Sky", 0.56, 0.45, 1.05),
    15: ("Azure", 0.59, 0.55, 0.85),
    16: ("Storm", 0.62, 0.45, 0.60),
    17: ("Teal", 0.50, 0.40, 0.90),
    18: ("Twilight", 0.70, 0.30, 0.85),
    19: ("Pink", 0.93, 0.55, 1.15),
    20: ("Rose", 0.95, 0.65, 1.00),
    21: ("Blossom", 0.91, 0.45, 1.25),
}
HAIR_SOURCE = 1
FACES = 10                                     # the blood elf's faces for everyone (0-9)

# New rows' ids, high enough to stay clear of the game's and other modules' (mod-worgoblin's...).
ID_SECTIONS = 900000
ID_OUTFIT = 9000
ID_HAIRGEO = 9000
ID_NAMEGEN = 90000
ID_VOCAL = 9000
ID_EMOTESOUND = 90000
ID_SEQUENCE = {ALLIANCE: 9001, HORDE: 9002}
ID_CAMERA = {ALLIANCE: 9001, HORDE: 9002}
ID_SOUND = 900001
SPELLS = {"walk": 98701, "skysight": 98702, "leyline": 98703, "wind": 98704, "insight": 98705,
          "blessing": 98706, "energized": 98707}


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


# Output ----------------------------------------------------------------------------------------

class Client:
    """The changes to the game's tables, a file for each (SkyborneClient.cpp applies them)."""

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
            os.remove(os.path.join(folder, old))
        for name, lines in sorted(self.files.items()):
            with open(os.path.join(folder, name + ".txt"), "w", newline="\n") as f:
                f.write(f"# {name}: the Skyborne's changes (tools/build_data.py)\n")
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
            values = ",\n".join("(" + ", ".join(sql_value(v, t) for v, t in zip(r, types)) + ")" for r in chunk)
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


# The game's tables --------------------------------------------------------------------------------

def dbc_row_values(dbc, row, types):
    """A row as values: strings resolved, floats as floats, the rest as numbers."""
    out = []
    for v, t in zip(row, types):
        out.append(dbc.s(v) if t == "s" else f32(v) if t == "f" else v)
    return out


def sql_rows(path, table):
    text = open(path).read()
    if "INSERT INTO" not in text:
        return []
    body = text.split("INSERT INTO", 1)[1]
    rows = []
    for m in re.finditer(r"\((.*?)\)[,;]\s*$", body, re.M):
        rows.append([v.strip() for v in re.findall(r"'(?:[^'\\]|\\.)*'|[^,]+", m.group(1))])
    return rows


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    dbc_dir, world = sys.argv[1], sys.argv[2]
    D = lambda name: Dbc(os.path.join(dbc_dir, name + ".dbc"))
    client, sql = Client(), Sql()
    # The creatures' races moved out of the Skyborne's places in the client's own rows (an HD look's
    # too, whatever their ids): their race, their looks, hair shapes, beards and voice rows.
    for old, new in MOVED.items():
        client.copyrow("ChrRaces", old, new)
        for table, field in (("CharSections", 1), ("CharHairGeosets", 1), ("CreatureDisplayInfoExtra", 1),
                             ("CharacterFacialHairStyles", 0), ("VocalUISounds", 2)):
            client.remapfield(table, field, old, new)
    textures = []
    sql.raw("-- The Skyborne (mod-skyborne): generated by tools/build_data.py from the game's own tables;\n"
            "-- edit that, not this. Safe to run again: every row is replaced, every mask OR'd.")

    # Races ----------------------------------------------------------------------------------------
    races = D("ChrRaces")
    rt = TYPES["chrraces_dbc"]
    rows = {r[0]: r for r in races.rows}
    sql.comment("The two races, on the blood elf's body.")
    server_races = []
    for race in (ALLIANCE, HORDE):
        v = dbc_row_values(races, rows[BLOODELF], rt)
        start = rows[START[race]]
        v[0] = race
        v[1] = rows[BLOODELF][1]                       # flags: playable, can mount
        v[2] = start[2]                                 # faction template: the start race's
        v[7] = start[7]                                 # language: Common or Orcish (the side)
        v[11] = FILESTRING[race]
        v[12] = ID_SEQUENCE[race]
        v[13] = start[13]                               # the side
        for i in range(14, 14 + 16):
            v[i] = "Skyborne" if i == 14 else ""
        for i in range(31, 31 + 16):
            v[i] = "Skyborne" if i == 31 else ""
        for i in range(48, 48 + 16):
            v[i] = "Skyborne" if i == 48 else ""
        v[68] = 0                                       # any expansion
        client.put("ChrRaces", rt, v)
        server_races.append(v)
    sql.replace("chrraces_dbc", COLUMNS["chrraces_dbc"], rt, server_races)

    # Looks ----------------------------------------------------------------------------------------
    sections = D("CharSections")
    st = TYPES["charsections_dbc"]
    new_sections, moved_sections = [], []
    next_id = [ID_SECTIONS]

    def section(race, sex, base, tex, flags, variation, color):
        v = [next_id[0], race, sex, base, tex[0], tex[1], tex[2], flags, variation, color]
        next_id[0] += 1
        client.put("CharSections", st, v)
        new_sections.append(v)

    def texture(op, params, src, dst):
        if src and dst:
            textures.append("\t".join([op, ",".join(f"{p:g}" for p in params), src, dst]))

    def skyborne_path(path, color=None, variation=None):
        """Blood elf texture path -> its Skyborne copy (another colour or face)."""
        d, n = path.rsplit("\\", 1)
        d = re.sub(r"(?i)\\bloodelf\b", r"\\Skyborne", "\\" + d)[1:]
        n = re.sub(r"(?i)^bloodelf", "Skyborne", n)
        m = re.match(r"(.*?)(\d\d)_(\d\d)\.blp$", n, re.I)
        if m:
            var = int(m.group(2)) if variation is None else variation
            col = int(m.group(3)) if color is None else color
            n = f"{m.group(1)}{var:02d}_{col:02d}.blp"
        return d + "\\" + n

    def dark_ranger_path(path):
        d, n = path.rsplit("\\", 1)
        m = re.match(r"(.*?)(\d\d)_(\d\d)\.blp$", n, re.I)
        return d + "\\" + f"{m.group(1)}{m.group(2)}_{DARK_RANGER[0]:02d}.blp"

    be = [r for r in sections.rows if r[1] == BLOODELF]
    tex = lambda r: [sections.s(r[4]), sections.s(r[5]), sections.s(r[6])]
    selectable = lambda r: (r[7] & 1) and not (r[7] & 4)    # a player's, not only a death knight's

    for sex in (0, 1):
        skins = {r[9]: r for r in be if r[2] == sex and r[3] == 0 and selectable(r)}
        overlay = {r[9]: r for r in be if r[2] == sex and r[3] == 4 and selectable(r)}
        faces = {(r[8], r[9]): r for r in be if r[2] == sex and r[3] == 1 and selectable(r)}
        hairs = [r for r in be if r[2] == sex and r[3] == 3 and selectable(r)]
        beards = [r for r in be if r[2] == sex and r[3] == 2 and selectable(r)]
        base_skin, base_overlay = skins[0], overlay.get(0)

        # The blood elf's Dark Ranger skin.
        dr, (name, s, l) = DARK_RANGER
        t = tex(base_skin)
        section(BLOODELF, sex, 0, [dark_ranger_path(t[0]), "", ""], base_skin[7], 0, dr)
        texture("grey", (s, l) + DARK_RANGER_EYES, t[0], dark_ranger_path(t[0]))
        # Section 4: no textures (the patch empties every race's: SkybornePatch.cpp, EmptyOverlayRows).
        if base_overlay:
            section(BLOODELF, sex, 4, ["", "", ""], base_overlay[7], 0, dr)
        # (every face of the first skin, the death knights' too: a death knight's are the skin's all, and
        # a skin with fewer than the others crashed the character creation screen, releases up to 1.0.245)
        for f in sorted((r for r in be if r[2] == sex and r[3] == 1 and r[9] == 0 and r[7] & 1), key=lambda r: r[8]):
            v = f[8]
            t = tex(f)
            section(BLOODELF, sex, 1, [dark_ranger_path(x) if x else "" for x in t], f[7], v, dr)
            for x in t:
                texture("grey", (s, l) + DARK_RANGER_EYES, x, dark_ranger_path(x) if x else "")

        for race in (ALLIANCE, HORDE):
            # Skins (the blood elf's own, and the blues) and section 4 rows without textures.
            for color, r in sorted(skins.items()):
                section(race, sex, 0, tex(r), r[7], 0, color)
            for color, r in sorted(overlay.items()):
                section(race, sex, 4, ["", "", ""], r[7], 0, color)
            for color, (name, h, s, l) in BLUES.items():
                t = tex(base_skin)
                section(race, sex, 0, [skyborne_path(t[0], color), "", ""], base_skin[7], 0, color)
                if race == ALLIANCE:
                    texture("skin", (h, s, l) + EYES[0][1], t[0], skyborne_path(t[0], color))
                if base_overlay:
                    section(race, sex, 4, ["", "", ""], base_overlay[7], 0, color)
            # Faces: blue eyes (0-9), yellow (10-19), on every skin.
            for e, (eye, eyes) in enumerate(EYES):
                for v in range(FACES):
                    for color in sorted(skins) + sorted(BLUES):
                        src = faces.get((v, color if color in skins else 0))
                        if not src:
                            continue
                        t = tex(src)
                        nv = v + e * FACES
                        dst = [skyborne_path(x, color, nv) if x else "" for x in t]
                        section(race, sex, 1, dst, src[7], nv, color)
                        if race == ALLIANCE:
                            for x, y in zip(t, dst):
                                if color in BLUES:
                                    _, h, s, l = BLUES[color]
                                    texture("skin", (h, s, l) + eyes, x, y)
                                else:
                                    texture("eyes", eyes, x, y)
            # Hair and beards: the blood elf's colours, and the new ones from its silver.
            for r in hairs + beards:
                section(race, sex, r[3], tex(r), r[7], r[8], r[9])
            for color, (name, h, s, l) in HAIRS.items():
                for r in hairs + beards:
                    if r[9] != HAIR_SOURCE:
                        continue
                    t = tex(r)
                    dst = [skyborne_path(x, color) if x else "" for x in t]
                    section(race, sex, r[3], dst, r[7], r[8], color)
                    if race == ALLIANCE:
                        for x, y in zip(t, dst):
                            texture("hair", (h, s, l), x, y)

    # The moved races' looks.
    for r in sections.rows:
        if r[1] in MOVED:
            v = dbc_row_values(sections, r, st)
            v[1] = MOVED[r[1]]
            moved_sections.append(v)
    sql.comment("Their looks (and the blood elf's Dark Ranger skin); the creatures' races 13 and 14 moved to 22 and 23.")
    # Their rows' ids follow each other: a build with fewer looks leaves none of the last one's.
    sql.raw(f"DELETE FROM `charsections_dbc` WHERE `ID` BETWEEN {ID_SECTIONS} AND {ID_SECTIONS + 9999};\n")
    sql.replace("charsections_dbc", COLUMNS["charsections_dbc"], st, new_sections + moved_sections)

    # Hair shapes, beards, names, voices (the game's tables only, but for the emotes' sounds).
    geo = D("CharHairGeosets")
    gid = ID_HAIRGEO
    for r in geo.rows:
        if r[1] == BLOODELF:
            for race in (ALLIANCE, HORDE):
                client.put("CharHairGeosets", "iiiiii", [gid, race] + r[2:])
                gid += 1
    beards = D("CharacterFacialHairStyles")
    for raw in beards.raw:
        race, sex = struct.unpack_from("<II", raw)
        if race == BLOODELF:
            for new in (ALLIANCE, HORDE):
                client.append_raw("CharacterFacialHairStyles", struct.pack("<I", new) + raw[4:])
    names = D("NameGen")
    nid = ID_NAMEGEN
    for r in names.rows:
        if r[2] == BLOODELF:
            for race in (ALLIANCE, HORDE):
                client.put("NameGen", "isii", [nid, names.s(r[1]), race, r[3]])
                nid += 1
    vocal = D("VocalUISounds")
    vid = ID_VOCAL
    for r in vocal.rows:
        if r[2] == BLOODELF:
            for race in (ALLIANCE, HORDE):
                v = list(r)
                v[0], v[2] = vid, race
                client.put("VocalUISounds", "i" * vocal.fields, v)
                vid += 1
    emotes = D("EmotesTextSound")
    eid, emote_rows = ID_EMOTESOUND, []
    for r in emotes.rows:
        if r[2] == BLOODELF:
            for race in (ALLIANCE, HORDE):
                v = [eid, r[1], race, r[3], r[4]]
                client.put("EmotesTextSound", "iiiii", v)
                emote_rows.append(v)
                eid += 1
    sql.comment("Their voices for the emotes.")
    sql.replace("emotestextsound_dbc", COLUMNS["emotestextsound_dbc"], "iiiii", emote_rows)

    # Classes and starting gear.
    for race in (ALLIANCE, HORDE):
        for cls in CLASSES[race]:
            client.append_raw("CharBaseInfo", bytes([race, cls]))
    outfits = D("CharStartOutfit")
    oid, outfit_rows = ID_OUTFIT, []
    for raw in outfits.raw:
        race, cls, sex, outfit = raw[4], raw[5], raw[6], raw[7]
        for new in (ALLIANCE, HORDE):
            if cls in CLASSES[new] and TEMPLATE[new][cls] == race:
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
        if r[1] == 9 and "racial" in name.lower():       # the races' own lines ("Racial - Human"...)
            racial_lines.add(r[0])
        if r[1] == 10:                                   # SKILL_CATEGORY_LANGUAGES
            languages[r[0]] = name
    COMMON, ORCISH = 98, 109

    def faction_bits(mask, line):
        add = 0
        if line in languages:
            # Only the side's own rows: the Horde's Common row (and the Alliance's Orcish one) is a
            # tiered one for learning it, and a race in it may be given that row (rank 0: nothing)
            # in place of its own.
            if line == COMMON and mask & ALLIANCE_MASK:
                add |= BIT[ALLIANCE]
            if line == ORCISH and mask & HORDE_MASK:
                add |= BIT[HORDE]
            return add
        if line in racial_lines:
            return 0
        if mask & ALLIANCE_MASK:
            add |= BIT[ALLIANCE]
        if mask & HORDE_MASK:
            add |= BIT[HORDE]
        return add

    def ors(table, dbc, types, field_mask, field_line, sql_table):
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
            sql.raw(f"UPDATE `{sql_table}` SET `RaceMask` = `RaceMask` & ~{BIT[ALLIANCE] | BIT[HORDE]} "
                    f"WHERE `ID` IN ({', '.join(str(i) for i in wrong)}) AND `RaceMask` > 0;")

    sql.comment("Skills and abilities open to either side's races are open to theirs (the racials and languages aside).")
    ors("SkillRaceClassInfo", D("SkillRaceClassInfo"), TYPES["skillraceclassinfo_dbc"], 2, 1, "skillraceclassinfo_dbc")
    ors("SkillLineAbility", D("SkillLineAbility"), TYPES["skilllineability_dbc"], 3, 1, "skilllineability_dbc")

    sql.comment("Standing: the start race's (Stormwind's for the High Order, Thunder Bluff's for the Windshapers).")
    factions = D("Faction")
    ft = TYPES["faction_dbc"]
    faction_rows = []
    for r in factions.rows:
        v = list(r)
        for slot in range(4):
            mask = r[2 + slot]
            if mask & 0x7FFFFFFF == 0x7FFFFFFF:
                continue
            for race in (ALLIANCE, HORDE):
                if mask & (1 << (START[race] - 1)):
                    v[2 + slot] |= BIT[race]
        if v != list(r):
            for slot in range(4):
                if v[2 + slot] != r[2 + slot]:
                    client.orfield("Faction", r[0], 2 + slot, v[2 + slot] & ~r[2 + slot])
            faction_rows.append(dbc_row_values(factions, v, ft))
    # (merged, not replaced: the allied races' SQL changes the same rows, and until 1.0.328 whichever was put in
    # last took the other's races' bits out of the reputations' rows)
    sql.merge_masks("faction_dbc", COLUMNS["faction_dbc"], ft, faction_rows,
                    [f"ReputationRaceMask_{n}" for n in range(1, 5)])

    # The intro: the start race's flight, Skyborne narration -----------------------------------------
    seqs, cams, sounds = D("CinematicSequences"), D("CinematicCamera"), D("SoundEntries")
    seq_rows = {r[0]: r for r in seqs.rows}
    cam_rows = {r[0]: r for r in cams.rows}
    snd_rows = {r[0]: r for r in sounds.rows}
    sound = dbc_row_values(sounds, snd_rows[3840], TYPES["soundentries_dbc"])  # HumanFlyByNarration
    sound[0], sound[2], sound[3] = ID_SOUND, "SkyborneFlyByNarration", "SkyborneNarration.mp3"
    client.put("SoundEntries", TYPES["soundentries_dbc"], sound)
    sql.comment("The intro: the start race's flight over its home, with the Skyborne's own narration.")
    sql.replace("soundentries_dbc", COLUMNS["soundentries_dbc"], TYPES["soundentries_dbc"], [sound])
    cam_sql, seq_sql = [], []
    for race in (ALLIANCE, HORDE):
        seq = seq_rows[races.rows[[r[0] for r in races.rows].index(START[race])][12]]
        cam = dbc_row_values(cams, cam_rows[seq[2]], TYPES["cinematiccamera_dbc"])
        cam[0], cam[2] = ID_CAMERA[race], ID_SOUND
        client.put("CinematicCamera", TYPES["cinematiccamera_dbc"], cam)
        cam_sql.append(cam)
        s = [ID_SEQUENCE[race], seq[1], ID_CAMERA[race]] + [0] * 7
        client.put("CinematicSequences", "i" * 10, s)
        seq_sql.append(s)
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

    # As WoW: Forever has them since its beta build of 15 October 2026 (Walk on Air's cooldown 90
    # seconds, Wind Blessed 3% haste, Skysight and Read Ley Line cast while moving). Their buffs last
    # 15 minutes, as they do there beside an elemental convergence or a ley line, everywhere (the
    # user's choice: Northrend's world has neither).
    no_cost = dict(Reagent_1=0, ReagentCount_1=0, ManaCostPct=0, SpellClassSet=0, SpellClassMask_1=0,
                   SpellClassMask_2=0, SpellClassMask_3=0, BaseLevel=1, SpellLevel=1, RangeIndex=1,
                   ImplicitTargetA_1=1, CastingTimeIndex=1, StartRecoveryCategory=133, StartRecoveryTime=1500,
                   SchoolMask=8, Attributes=0x10, AttributesEx=0, AttributesEx6=0, InterruptFlags=0, DispelType=0)
    trigger = lambda spell_id: dict(Effect_1=64, EffectAura_1=0, EffectBasePoints_1=0, EffectDieSides_1=0,
                                    EffectTriggerSpell_1=spell_id, SpellVisualID_1=0)
    aura = dict(no_cost, Attributes=0, StartRecoveryCategory=0, StartRecoveryTime=0, DurationIndex=347)   # 15 min
    spell_rows = [
        spell(130, SPELLS["walk"], "Walk on Air", "Racial",
              "Glide downward through the air for $d.", "Gliding.",
              DurationIndex=1, RecoveryTime=90000, SpellIconID=220, **dict(no_cost, DispelType=1)),
        spell(130, SPELLS["skysight"], "Skysight", "Racial",
              "Grants an Elemental Blessing that increases run and mounted speed by 10% for 15 min. "
              "Does not stack with other movement speed increases.", "",
              RecoveryTime=120000, SpellIconID=1530, **dict(no_cost, CastingTimeIndex=3), **trigger(SPELLS["blessing"])),
        spell(130, SPELLS["blessing"], "Elemental Blessing", "",
              "Run and mounted speed increased by $s1%.", "Run and mounted speed increased by $s1%.",
              SpellIconID=1530, EffectAura_1=171, EffectBasePoints_1=9, EffectDieSides_1=1, SpellVisualID_1=0,
              Effect_2=6, EffectAura_2=172, EffectBasePoints_2=9, EffectDieSides_2=1, ImplicitTargetA_2=1, **aura),
        spell(130, SPELLS["leyline"], "Read Ley Line", "Racial",
              "Activate a ley line to gain Energized, increasing your Health and Mana regeneration by 100% for 15 min.", "",
              RecoveryTime=120000, SpellIconID=2158, **dict(no_cost, CastingTimeIndex=5, SchoolMask=64), **trigger(SPELLS["energized"])),
        spell(130, SPELLS["energized"], "Energized", "",
              "Health and Mana regeneration increased by $s1%.", "Health and Mana regeneration increased by $s1%.",
              SpellIconID=2158, EffectAura_1=88, EffectBasePoints_1=99, EffectDieSides_1=1, SpellVisualID_1=0,
              Effect_2=6, EffectAura_2=110, EffectBasePoints_2=99, EffectDieSides_2=1, ImplicitTargetA_2=1,
              EffectMiscValue_2=0, **dict(aura, SchoolMask=64)),
        spell(20550, SPELLS["wind"], "Wind Blessed", "Racial Passive",
              "Increases melee, ranged and spellcasting haste by 3%.", "",
              SpellIconID=1397, EffectAura_1=138, EffectBasePoints_1=2, EffectDieSides_1=1,
              Effect_2=6, EffectAura_2=140, EffectBasePoints_2=2, EffectDieSides_2=1, ImplicitTargetA_2=1,
              Effect_3=6, EffectAura_3=65, EffectBasePoints_3=2, EffectDieSides_3=1, ImplicitTargetA_3=1),
        spell(20557, SPELLS["insight"], "Elemental Insight", "Racial Passive",
              "Damage dealt to Elementals increased by 5%.", "",
              SpellIconID=2017, EffectMiscValue_1=1 << (4 - 1)),
    ]
    sql.comment("Their racials: Walk on Air, Skysight (Windshapers, with Elemental Blessing), Read Ley Line (High Order,\n"
                "with Energized), Wind Blessed, Elemental Insight.")
    sql.replace("spell_dbc", COLUMNS["spell_dbc"], spt, spell_rows)

    # The world database: starts, skills, stats, forms, quests, standing --------------------------------
    sql.comment("Where they start (their start race's place), for every class.")
    pci = sql_rows(os.path.join(world, "playercreateinfo.sql"), "playercreateinfo")
    place = {}
    for r in pci:
        place.setdefault(int(r[0]), r)                    # the race's first class: its start
    out = []
    for race in (ALLIANCE, HORDE):
        p = place[START[race]]
        for cls in CLASSES[race]:
            out.append([race, cls] + p[2:])
    sql.raw("REPLACE INTO `playercreateinfo` (`race`, `class`, `map`, `zone`, `position_x`, `position_y`, `position_z`, `orientation`) VALUES\n"
            + ",\n".join("(" + ", ".join(str(x) for x in r) + ")" for r in out) + ";")

    racial_spells = set()
    for r in D("SkillLineAbility").rows:
        if r[1] in racial_lines:
            racial_spells.add(r[2])
    sql.comment("Their action bars: the class's start race's, without that race's racials.")
    acts = sql_rows(os.path.join(world, "playercreateinfo_action.sql"), "playercreateinfo_action")
    out = []
    for race in (ALLIANCE, HORDE):
        for cls in CLASSES[race]:
            for r in acts:
                if int(r[0]) == TEMPLATE[race][cls] and int(r[1]) == cls and not (int(r[4]) == 0 and int(r[3]) in racial_spells):
                    out.append([race, cls] + r[2:])
    sql.raw(f"DELETE FROM `playercreateinfo_action` WHERE `race` IN ({ALLIANCE}, {HORDE});")
    sql.raw("INSERT INTO `playercreateinfo_action` (`race`, `class`, `button`, `action`, `type`) VALUES\n"
            + ",\n".join("(" + ", ".join(str(x) for x in r) + ")" for r in out) + ";")

    sql.comment("Their skills: their side's weapons and armour; Common or Orcish; no other race's racials.")
    for r in sql_rows(os.path.join(world, "playercreateinfo_skills.sql"), "playercreateinfo_skills"):
        mask, skill = int(r[0]), int(r[2])
        if mask == 0:
            continue
        add = faction_bits(mask, skill)
        if add:
            sql.raw(f"UPDATE `playercreateinfo_skills` SET `raceMask` = `raceMask` | {add} WHERE (`raceMask` & 2047) = {mask & 2047} AND `classMask` = {r[1]} AND `skill` = {skill};")

    sql.comment("Their racials, learned at creation.")
    sql.raw(f"DELETE FROM `playercreateinfo_spell_custom` WHERE `Spell` BETWEEN {min(SPELLS.values())} AND {max(SPELLS.values())};")
    both = BIT[ALLIANCE] | BIT[HORDE]
    custom = [(both, SPELLS["walk"], "Skyborne - Walk on Air"), (BIT[HORDE], SPELLS["skysight"], "Skyborne - Skysight"),
              (BIT[ALLIANCE], SPELLS["leyline"], "Skyborne - Read Ley Line"), (both, SPELLS["wind"], "Skyborne - Wind Blessed"),
              (both, SPELLS["insight"], "Skyborne - Elemental Insight")]
    sql.raw("INSERT INTO `playercreateinfo_spell_custom` (`racemask`, `classmask`, `Spell`, `Note`) VALUES\n"
            + ",\n".join(f"({m}, 0, {s}, '{n}')" for m, s, n in custom) + ";")

    sql.comment("Their stats: WoW: Forever's starting stats for every class are the class's base with Strength -1,\n"
                "Agility +1, Stamina -1, Intellect +1, Spirit 0. Druid forms: the night elf's. Totems: the tauren's.")
    sql.raw("REPLACE INTO `player_race_stats` (`Race`, `Strength`, `Agility`, `Stamina`, `Intellect`, `Spirit`) VALUES\n"
            + ",\n".join(f"({race}, " + ", ".join(str(x) for x in RACE_STATS) + ")" for race in (ALLIANCE, HORDE)) + ";")
    forms = [r for r in sql_rows(os.path.join(world, "player_shapeshift_model.sql"), "player_shapeshift_model") if int(r[1]) == NIGHTELF]
    sql.raw(f"DELETE FROM `player_shapeshift_model` WHERE `RaceID` IN ({ALLIANCE}, {HORDE});")
    sql.raw("INSERT INTO `player_shapeshift_model` (`ShapeshiftID`, `RaceID`, `CustomizationID`, `GenderID`, `ModelID`) VALUES\n"
            + ",\n".join(f"({r[0]}, {race}, {r[2]}, {r[3]}, {r[4]})" for race in (ALLIANCE, HORDE) for r in forms) + ";")
    totems = [r for r in sql_rows(os.path.join(world, "player_totem_model.sql"), "player_totem_model") if int(r[1]) == TAUREN]
    sql.raw(f"DELETE FROM `player_totem_model` WHERE `RaceID` IN ({ALLIANCE}, {HORDE});")
    sql.raw("INSERT INTO `player_totem_model` (`TotemID`, `RaceID`, `ModelID`) VALUES\n"
            + ",\n".join(f"({r[0]}, {race}, {r[2]})" for race in (ALLIANCE, HORDE) for r in totems) + ";")

    sql.comment("Quests, items and conditions for their start race are theirs too: the Humans' for the High Order,\n"
                "the Tauren's for the Windshapers; and those of the race their classes' starts come from where the\n"
                "start race hasn't the class (the Night Elves' hunters' and druids', the Blood Elves' rogues').")
    for race in (ALLIANCE, HORDE):
        b = BIT[race]
        s = 0
        for r in {START[race]} | set(TEMPLATE[race].values()):
            s |= 1 << (r - 1)
        sql.raw(f"UPDATE `quest_template` SET `AllowableRaces` = `AllowableRaces` | {b} WHERE `AllowableRaces` & {s} AND `AllowableRaces` & 0x7FFFFFFF <> 0x7FFFFFFF;")
        sql.raw(f"UPDATE `item_template` SET `AllowableRace` = `AllowableRace` | {b} WHERE `AllowableRace` <> -1 AND `AllowableRace` & {s} AND `AllowableRace` & 0x7FFFFFFF <> 0x7FFFFFFF;")
        sql.raw(f"UPDATE `conditions` SET `ConditionValue1` = `ConditionValue1` | {b} WHERE `ConditionTypeOrReference` = 16 AND `ConditionValue1` & {s};")

    # Write -----------------------------------------------------------------------------------------
    with open(os.path.join(MODULE, "data", "sql", "db-world", "skyborne_world.sql"), "w", newline="\n") as f:
        f.write("\n".join(sql.parts) + "\n")
    client.write(os.path.join(MODULE, "data", "client", "dbc"))
    seen, unique = set(), []
    for t in textures:
        dst = t.split("\t")[3].lower()
        if dst not in seen:
            seen.add(dst)
            unique.append(t)
    with open(os.path.join(MODULE, "data", "client", "textures.txt"), "w", newline="\n") as f:
        f.write("# The Skyborne's textures, made from the game's own as the realm starts (tools/build_data.py).\n"
                "# op<TAB>params<TAB>source<TAB>destination. skin: hue,saturation,lightness[,eye hue,eye saturation,eye lightness]\n"
                "# (eye hue -1: eyes as they are); grey: saturation kept,lightness,eye hue,eye saturation,eye lightness;\n"
                "# eyes: hue,saturation,lightness; hair: hue,saturation,lightness.\n")
        f.write("\n".join(unique) + "\n")
    print(f"{len(new_sections)} looks, {len(unique)} textures, {len(client.files)} tables, {len(spell_rows)} spells")


if __name__ == "__main__":
    main()
