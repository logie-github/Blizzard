#!/usr/bin/env python3
"""What mod-worgoblin changes in the game's tables, made to go on top of whatever the client and the
realm already have (the HD looks', the allied races', the Skyborne's), instead of in place of them.

mod-worgoblin (github.com/heyitsbench/mod-worgoblin) ships 30 whole tables of the game (its
data/patch/DBFilesClient), for both the server's data folder and the game: the game's own tables
with its Worgen and Goblins in them. Put in as they are, they'd take the place of every other patch's
rows in those tables (an HD look's characters, the allied races and the Skyborne), and they also carry
an editor's damage of the game's own text (quotes doubled, line breaks dropped: 2000 spell tooltips).
So this compares each table with the game's own (the server's dbc folder, the 3.3.5a enUS client's)
and keeps what mod-worgoblin really changes:

  - the rows it adds (renumbered where the game's tables or an HD look may have rows of their own:
    the looks, the starting outfits, the names, the voices, the barber's styles);
  - the numbers it changes in the game's own rows (the races' bits in the reputations, skills,
    abilities and talent trees, OR'd in; a few spells' fields, the helmets' hidden hair), not their text;
  - for the character tables, only its Worgen's (race 12) and Goblins' (race 9) rows: its tables have
    rows of other races' too (another project's), which aren't its races and aren't put in;
  - the game's own creatures of those two races (the goblins of Azeroth's ports and the fel orcs of
    Outland: race 9's and 12's looks, hair and voices) moved out of the way first, to races 28 and 29,
    the way the allied races and the Skyborne move theirs, so the creatures look as they always have;
  - ChrRaces 9 and 12 as mod-worgoblin has them (the two races made playable).

It writes:
  - data/client/dbc/<Table>.txt: the changes, in the Skyborne's format (mod-skyborne's
    SkyborneFiles.cpp, ApplyChanges), made into the game's patch as the realm starts
    (src/WorgenGoblinPatch.cpp);
  - data/server/worgen_goblin_dbc.sql: the same for the tables the world server reads (their *_dbc
    tables in the world database, which it reads over its DBC files), as statements that merge into
    what's there (the race bits OR'd), run at every start of ChromieCraft's world server, after the
    modules' SQL (src/WorgenGoblin.cpp): the allied races' and the Skyborne's SQL put whole rows of the
    same tables (the reputations, the skills), which in either order would otherwise drop one's bits.

    python3 tools/build_data.py STOCK_DBC_DIR WORGOBLIN_DIR CORE_DIR

STOCK_DBC_DIR: the server's dbc folder (AzerothCore's data, github.com/wowgaming/client-data);
WORGOBLIN_DIR: mod-worgoblin at the commit warcraft/server-version.env pins; CORE_DIR: the core's
source (its data/sql/base/db_world names the *_dbc tables' columns). Run again when the pin moves.
"""
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODULE = os.path.dirname(HERE)
TYPES = json.load(open(os.path.join(HERE, "dbc_types.json")))

GOBLIN, WORGEN = 9, 12
RACES = (GOBLIN, WORGEN)
MOVED = {GOBLIN: 28, WORGEN: 29}       # the game's own goblin and fel orc creatures' race, out of the way

# Where the race is in the character tables (an int field's index, or a byte's offset for the raw
# ones): only these races' new rows are put in.
RACE_FIELD = {
    "CharSections": 1, "CharHairGeosets": 1, "CharHairTextures": 1, "CharacterFacialHairStyles": 0,
    "BarberShopStyle": 37, "NameGen": 2, "EmotesTextSound": 2, "VocalUISounds": 2,
}
RACE_BYTE = {"CharStartOutfit": 4, "CharBaseInfo": 0}
# The game's own rows of the two races (its creatures') moved to MOVED first, by this field.
MOVE_FIELD = {
    "CharSections": 1, "CharHairGeosets": 1, "CharHairTextures": 1, "CharacterFacialHairStyles": 0,
    "CreatureDisplayInfoExtra": 1, "VocalUISounds": 2, "EmotesTextSound": 2, "NameGen": 2,
}
# New rows numbered from here (ids an HD look or the other modules' rows don't use: the allied
# races' are 920000+ looks, 9100+ outfits and hair, 9200+ voices, 91000+ names and emotes; the
# Skyborne's 9000 to 9107 voices). The rest keep mod-worgoblin's ids, which other rows name (its
# sounds, displays, models, spells, items).
RENUMBER = {
    "CharSections": 880000, "CharHairGeosets": 8800, "CharStartOutfit": 8800, "NameGen": 80000,
    "EmotesTextSound": 88000, "VocalUISounds": 8800, "BarberShopStyle": 8800,
}
# Race masks: mod-worgoblin's bits OR'd into the row (whatever the other modules put in it).
MASKS = {
    "Faction": (2, 3, 4, 5), "SkillLineAbility": (3,), "SkillRaceClassInfo": (2,), "TalentTab": (19,),
}
# Tables whose rows of the game's own mod-worgoblin doesn't change on purpose: its copies differ only
# where its editor damaged them (text) or where they're another project's (other races' rows).
CHARACTER_TABLES = set(RACE_FIELD) | set(RACE_BYTE)
# The tables the world server reads (with a *_dbc table of the world database over each).
SERVER = {
    "Achievement": "achievement_dbc", "Achievement_Criteria": "achievement_criteria_dbc",
    "BarberShopStyle": "barbershopstyle_dbc", "CharSections": "charsections_dbc",
    "CharStartOutfit": "charstartoutfit_dbc", "ChrRaces": "chrraces_dbc",
    "CreatureDisplayInfo": "creaturedisplayinfo_dbc", "CreatureDisplayInfoExtra": "creaturedisplayinfoextra_dbc",
    "CreatureModelData": "creaturemodeldata_dbc", "EmotesTextSound": "emotestextsound_dbc",
    "Faction": "faction_dbc", "Item": "item_dbc", "ItemDisplayInfo": "itemdisplayinfo_dbc",
    "SkillLine": "skillline_dbc", "SkillLineAbility": "skilllineability_dbc",
    "SkillRaceClassInfo": "skillraceclassinfo_dbc", "SoundEntries": "soundentries_dbc", "Spell": "spell_dbc",
    "SummonProperties": "summonproperties_dbc", "TalentTab": "talenttab_dbc",
}


# mod-worgoblin's Worgen leave numbers out: their features are 1 to 23 without 0 and 16, and the
# women's hair styles start at 1. The character creation screen counts a slider's rows and then asks
# for the numbers from 0 up (a missing one is the look-up that crashed the screen: crash report #34),
# so the gaps get rows the way the game's own tables have them: a feature of none (no geosets), a
# hair style of none (no hair, the scalp shown, as a bald human's). Fields: (race, sex, variation).
GAPS = {"CharacterFacialHairStyles": (0, 1, 2), "CharHairGeosets": (1, 2, 3)}

# mod-worgoblin's rows changed for the module's code: Two Forms (68996), which mod-worgoblin has as a
# lasting transformation into a creature (and leaves ungiven), made Cataclysm's: an instant spell of
# the player's own, a 1.5 second cooldown, its effect a dummy src/WorgenGoblinForms.cpp answers (the
# human form). Fields by index (3.3.5a's Spell): Attributes 4, AttributesExC 7, RecoveryTime 29,
# DurationIndex 40, Effect 71, EffectAuraPeriod 98 to 100, EffectApplyAuraName 95, EffectMiscValue 110.
ROW_EDITS = {"Spell": {68996: {4: 0, 7: 0, 29: 1500, 40: 0, 71: 3, 95: 0, 100: 0, 110: 0}}}
# The module's scripts for those (the world database's spell_script_names), put in at every start.
SCRIPTS_SQL = ("DELETE FROM `spell_script_names` WHERE `spell_id` = 68996;\n"
               "INSERT INTO `spell_script_names` (`spell_id`, `ScriptName`) VALUES (68996, 'spell_worgen_goblin_two_forms');")


def fill_gaps(name, rows, report):
    race_at, sex_at, var_at = GAPS[name]
    added = []
    groups = {}
    for v in rows:
        groups.setdefault((v[race_at], v[sex_at]), set()).add(v[var_at])
    for (race, sex), variations in sorted(groups.items()):
        for missing in sorted(set(range(max(variations) + 1)) - variations):
            if name == "CharacterFacialHairStyles":
                row = [race, sex, missing, 0, 0, 0, 0, 0]
            else:
                row = [0, race, sex, missing, 0, 1]      # (its id is given as the rows are numbered)
            added.append(row)
            report.append(f"{name}: race {race} sex {sex}: variation {missing} added (none)")
    return added


class Dbc:
    def __init__(self, path):
        data = open(path, "rb").read()
        magic, self.count, self.fields, self.size, strings = struct.unpack("<4s4I", data[:20])
        assert magic == b"WDBC", path
        self.raw = [data[20 + i * self.size:20 + (i + 1) * self.size] for i in range(self.count)]
        self.text = data[20 + self.count * self.size:]

    def s(self, offset):
        end = self.text.index(b"\0", offset)
        return self.text[offset:end].decode("utf-8")

    def values(self, raw, types):
        """A row as values: text as text (mod-worgoblin's doubled quotes made single), floats as floats."""
        ints = struct.unpack(f"<{len(types)}I", raw)
        out = []
        for v, t in zip(ints, types):
            if t == "s":
                out.append(self.s(v).replace('""', '"'))
            elif t == "f":
                out.append(struct.unpack("<f", struct.pack("<I", v))[0])
            else:
                out.append(v)
        return out


def find(folder, name):
    for f in os.listdir(folder):
        if f.lower() == name.lower() + ".dbc":
            return os.path.join(folder, f)
    raise FileNotFoundError(name)


def is_locale_flags(types, i):
    """The field after a localized text's 16 languages (its flags)."""
    return i >= 16 and types[i - 16:i] == "s" * 16 and (i + 1 >= len(types) or types[i] == "i")


def esc(text):
    return str(text).replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "")


def client_value(v, t):
    if t == "s":
        return esc(v)
    if t == "f":
        return repr(float(v))
    return str(int(v) & 0xFFFFFFFF)


def i32(v):
    return struct.unpack("<i", struct.pack("<I", int(v) & 0xFFFFFFFF))[0]


def sql_value(v, t, unsigned=False):
    if t == "s":
        return "'" + str(v).replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "") + "'"
    if t == "f":
        return repr(float(v))
    return str(int(v) & 0xFFFFFFFF) if unsigned else str(i32(v))


def or_into(column, unsigned):
    """SQL for a race mask column with the new row's bits OR'd in: MariaDB ORs as 64-bit unsigned
    numbers (a -1, every race, becomes 2^64 - 1, which an INT column can't take), so the result is
    taken back to the column's 32 bits."""
    bits = f"((`{column}` | VALUES(`{column}`)) & 0xFFFFFFFF)"
    if unsigned:
        return f"`{column}` = {bits}"
    return f"`{column}` = IF({bits} >= 0x80000000, CAST({bits} AS SIGNED) - 4294967296, {bits})"


def columns(core, table):
    """A *_dbc table's columns, in the order of its DBC file's fields."""
    start = re.compile(r"CREATE TABLE (?:IF NOT EXISTS )?`%s`" % table)
    for folder in ("base", "updates"):
        root = os.path.join(core, "data", "sql", folder, "db_world")
        for name in sorted(os.listdir(root)):
            text = open(os.path.join(root, name), encoding="utf-8", errors="replace").read()
            m = start.search(text)
            if m:
                body = text[m.start():]
                body = body[:body.index("ENGINE")]
                return [(name, "unsigned" in kind) for name, kind in re.findall(r"^\s*`(\w+)`\s+([^,\n]*)", body, re.M)]
    raise FileNotFoundError(table)


def raw_outfit(raw):
    """A CharStartOutfit record (296 bytes) as its 77 values: id, race, class, sex, outfit, 72 ints."""
    return list(struct.unpack("<I4B72I", raw))


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    stock_dir, worgoblin, core = sys.argv[1:]
    theirs_dir = os.path.join(worgoblin, "data", "patch", "DBFilesClient")
    client, server, report = {}, [], []

    def line(name, text):
        client.setdefault(name, []).append(text)

    for name in sorted(TYPES):
        types = TYPES[name]
        stock = Dbc(find(stock_dir, name))
        theirs = Dbc(find(theirs_dir, name))
        assert (stock.fields, stock.size) == (theirs.fields, theirs.size), name
        raw = types == "raw"
        if not raw:
            assert len(types) == stock.fields and stock.size == stock.fields * 4, name

        # The game's own creatures of the two races, moved out of their places first.
        if name == "ChrRaces":
            for race, to in MOVED.items():
                line(name, f"copyrow\t{race}\t{to}")
        if name in MOVE_FIELD:
            for race, to in MOVED.items():
                line(name, f"remapfield\t{MOVE_FIELD[name]}\t{race}\t{to}")

        if raw:
            # CharStartOutfit (an id, then bytes) and CharBaseInfo (two bytes): their two races' rows.
            at = RACE_BYTE[name]
            mine = [r for r in theirs.raw if r[at] in RACES]
            stock_keys = {r[at:at + 3] if name == "CharStartOutfit" else r for r in stock.raw}
            new = [r for r in mine if (r[at:at + 3] if name == "CharStartOutfit" else r) not in stock_keys]
            if name == "CharStartOutfit":
                rows = []
                for n, r in enumerate(sorted(new, key=lambda r: r[4:8])):
                    r = struct.pack("<I", RENUMBER[name] + n) + r[4:]
                    line(name, "putraw\t" + r.hex())
                    rows.append(raw_outfit(r))
                server.append((name, "new", rows, None))
            else:
                for r in new:
                    line(name, "appendraw\t" + r.hex())
            report.append(f"{name}: {len(new)} rows of theirs")
            continue

        stock_rows = {struct.unpack_from("<I", r)[0]: r for r in stock.raw}
        keyed = name not in ("CharacterFacialHairStyles",)    # (no id: race, sex and variation)
        new_rows, changed = [], []
        for r in theirs.raw:
            values = theirs.values(r, types)
            if name in RACE_FIELD and values[RACE_FIELD[name]] not in RACES:
                continue
            if not keyed:
                key = tuple(values[:3])
                if key in {tuple(stock.values(s, types)[:3]) for s in stock.raw}:
                    continue
                new_rows.append(values)
                continue
            rid = values[0]
            if rid not in stock_rows:
                new_rows.append(values)
                continue
            if name == "ChrRaces":
                if rid in RACES:
                    new_rows.append(values)       # the race's row as mod-worgoblin has it, whole
                continue
            if name in CHARACTER_TABLES:
                continue
            old = stock.values(stock_rows[rid], types)
            # (its editor wrote some floats back rounded: 9999999 as 10000000; those aren't changes)
            fields = [i for i, (a, b, t) in enumerate(zip(old, values, types))
                      if t != "s" and not is_locale_flags(types, i) and a != b
                      and not (t == "f" and abs(a - b) <= 1e-6 * max(1.0, abs(a)))]
            if fields:
                changed.append((rid, old, values, fields))

        if name in GAPS:
            new_rows += fill_gaps(name, new_rows, report)
        for v in new_rows:
            for i, value in ROW_EDITS.get(name, {}).get(v[0], {}).items():
                v[i] = value
        if name in RENUMBER:
            new_rows.sort(key=lambda v: v[0])
            for n, v in enumerate(new_rows):
                v[0] = RENUMBER[name] + n
        if keyed and new_rows:
            line(name, "types\t" + types)
        for v in new_rows:
            if keyed:
                line(name, "put\t" + "\t".join(client_value(x, t) for x, t in zip(v, types)))
            else:
                line(name, "appendraw\t" + struct.pack(f"<{len(v)}I", *v).hex())
        masks = MASKS.get(name, ())
        for rid, old, values, fields in changed:
            for i in fields:
                if i in masks:
                    line(name, f"or\t{rid}\t{i}\t{values[i] & ~old[i] & 0xFFFFFFFF}")
                else:
                    bits = struct.unpack("<I", struct.pack("<f", values[i]))[0] if types[i] == "f" else values[i]
                    line(name, f"set\t{rid}\t{i}\t{bits & 0xFFFFFFFF}")
        if name in SERVER:
            server.append((name, "new", new_rows, None))
            server.append((name, "changed", changed, masks))
        report.append(f"{name}: {len(new_rows)} new rows, {len(changed)} rows changed")

    # The game's tables.
    folder = os.path.join(MODULE, "data", "client", "dbc")
    os.makedirs(folder, exist_ok=True)
    for old in os.listdir(folder):
        if old.endswith(".txt"):
            os.remove(os.path.join(folder, old))
    for name, lines in sorted(client.items()):
        # (a "types" line first, as the changes are read in order; written once)
        body = [l for l in lines if not l.startswith("types\t")]
        head = [l for l in lines if l.startswith("types\t")][:1]
        moves = [l for l in body if l.startswith(("copyrow", "remapfield"))]
        rest = [l for l in body if not l.startswith(("copyrow", "remapfield"))]
        with open(os.path.join(folder, name + ".txt"), "w", newline="\n") as f:
            f.write(f"# {name}: mod-worgoblin's Worgen and Goblins (tools/build_data.py)\n")
            f.write("\n".join(head + moves + rest) + "\n")

    # The world server's tables.
    sql = ["-- mod-worgoblin's Worgen and Goblins in the world server's tables (tools/build_data.py): run by",
           "-- src/WorgenGoblin.cpp at every start of ChromieCraft's world server, after the modules' SQL.",
           "-- New rows put in (or put back); mod-worgoblin's race bits OR'd into the game's rows, whatever",
           "-- other modules put in them; its other changed numbers set."]
    for name, kind, rows, masks in server:
        if not rows:
            continue
        table = SERVER[name]
        cols = columns(core, table)
        unsigned = [u for _, u in cols]
        cols = [c for c, _ in cols]
        types = "iiiii" + "i" * 72 if name == "CharStartOutfit" else TYPES[name]
        assert len(cols) == len(types), (table, len(cols), len(types))
        names = ", ".join(f"`{c}`" for c in cols)
        if kind == "new":
            update = ", ".join(f"`{c}` = VALUES(`{c}`)" for c in cols[1:])
            for i in range(0, len(rows), 200):
                values = ",\n".join("(" + ", ".join(sql_value(v, t, u) for v, t, u in zip(r, types, unsigned)) + ")" for r in rows[i:i + 200])
                sql.append(f"INSERT INTO `{table}` ({names}) VALUES\n{values}\nON DUPLICATE KEY UPDATE {update};")
            continue
        # Changed rows: the game's row with mod-worgoblin's numbers, merged into the one there.
        groups = {}
        for rid, old, values, fields in rows:
            full = list(old)
            for i in fields:
                full[i] = (old[i] | values[i]) if i in masks else values[i]
            groups.setdefault(tuple(fields), []).append(full)
        for fields, fulls in sorted(groups.items()):
            update = ", ".join(or_into(cols[i], unsigned[i]) if i in masks
                               else f"`{cols[i]}` = VALUES(`{cols[i]}`)" for i in fields)
            for i in range(0, len(fulls), 200):
                values = ",\n".join("(" + ", ".join(sql_value(v, t, u) for v, t, u in zip(r, types, unsigned)) + ")" for r in fulls[i:i + 200])
                sql.append(f"INSERT INTO `{table}` ({names}) VALUES\n{values}\nON DUPLICATE KEY UPDATE {update};")
    os.makedirs(os.path.join(MODULE, "data", "server"), exist_ok=True)
    with open(os.path.join(MODULE, "data", "server", "worgen_goblin_dbc.sql"), "w", newline="\n") as f:
        f.write("\n".join(sql + ["-- The module's scripts for them (src/WorgenGoblinForms.cpp).", SCRIPTS_SQL]) + "\n")
    print("\n".join(report))


if __name__ == "__main__":
    main()
