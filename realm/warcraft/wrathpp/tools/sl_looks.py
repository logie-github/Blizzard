#!/usr/bin/env python3
"""Shadowlands' looks (9.2.7.45745) for the ten races of 3.3.5, made what the 3.3.5 game draws, for Wrath++ alone:
the models of today's ten races (wago.tools, by file id), converted by the allied races' converter
(realm/warcraft/modules/mod-allied-races/tools: m2.py, textures.py), their skins, faces, hair styles and colours
and facial features as Shadowlands has them, and the game's three character tables (CharSections, CharHairGeosets,
CharacterFacialHairStyles) with the ten races' rows made from them. The files are Blizzard's, so they are never in
this repository: CI makes them (.github/workflows/wrathpp-looks.yml) and the app puts them in Wrath++'s copy of the game
and its server's data.

    python3 tools/sl_looks.py fetch CSV_DIR                    the tables (wago.tools' CSVs at 9.2.7.45745)
    python3 tools/sl_looks.py races CSV_DIR LOOKS.json         what each race and sex is made of (from the tables)
    python3 tools/sl_looks.py verify LOOKS.json DBC OUT        the files the tables name are all in OUT
    python3 tools/sl_looks.py package LOOKS.json CACHE DBC OUT  fetches into CACHE (files by id) and writes OUT:
                                                               OUT/client  the game's patch (game paths), the tables
                                                                           in DBFilesClient
                                                               OUT/dbc     the same tables for the world server
                                                               DBC: the server's dbc folder (server-data.env's data.zip),
                                                               the rows of everything but the ten races

CSV_DIR: wago.tools' CSVs at 9.2.7.45745 (sl_inventory.py fetch, and the TABLES_MORE here).

How Shadowlands' options go on 3.3.5's five sliders for now (docs/wrathpp/SHADOWLANDS_OPTIONS.md, "The way there"):
skin colour (every one), face (every face, each with every eye colour while 3.3.5's 255 faces hold them), hair style,
hair colour, and the feature slider: the options FEATURES names, every combination (3.3.5's facial table holds geoset
groups 1, 3, 2 and 16: today's other groups are moved onto those where FEATURES says). The rest stay at their first
choice until the native mod draws them as categories of their own.
"""
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ALLIED = os.path.join(HERE, "..", "..", "modules", "mod-allied-races", "tools")
sys.path.insert(0, os.path.abspath(ALLIED))
import races as allied                         # noqa: E402

BUILD = "9.2.7.45745"
TABLES_MORE = ("TextureFileData", "CreatureModelData", "CreatureDisplayInfo", "VocalUISounds", "EmotesTextSound",
               "SoundKitEntry", "NameGen")
# race id: (folder name, ChrModel ids by sex)
RACES = {1: ("Human", {0: 1, 1: 2}), 2: ("Orc", {0: 3, 1: 4}), 3: ("Dwarf", {0: 5, 1: 6}), 4: ("NightElf", {0: 7, 1: 8}),
         5: ("Scourge", {0: 9, 1: 10}), 6: ("Tauren", {0: 11, 1: 12}), 7: ("Gnome", {0: 13, 1: 14}),
         8: ("Troll", {0: 15, 1: 16}), 10: ("BloodElf", {0: 19, 1: 20}), 11: ("Draenei", {0: 21, 1: 22})}
# The feature slider, a race and sex: today's options (every combination, the first changing slowest; at most 255) and
# today's geoset groups moved onto 3.3.5's facial groups (1, 3, 2, 16).
FEATURES = {
    (1, 0): (["Beard", "Mustache", "Sideburns"], {}),                                   # 8 x 7 x 3
    (1, 1): (["Piercings", "Necklace"], {35: 3, 36: 2}),                                # 15 x 9
    (2, 0): (["Beard", "Sideburns"], {}),                                               # 14 x 9
    (2, 1): (["Earrings", "Nose Ring", "Necklace"], {35: 3, 36: 2}),                    # 14 x 3 x 3
    (3, 0): (["Beard", "Mustache"], {}),                                                # 11 x 10
    (3, 1): (["Earrings", "Piercings"], {35: 3}),                                       # 8 x 6
    (4, 0): (["Beard", "Mustache", "Sideburns"], {}),                                   # 8 x 5 x 5
    (4, 1): (["Earrings", "Nose Ring", "Necklace"], {35: 3, 36: 2}),                    # 4 x 4 x 4
    (5, 0): (["Jaw Features", "Face Features"], {}),                                    # 11 x 5
    (5, 1): (["Face Features", "Jaw Features"], {}),                                    # 4 x 5
    (6, 0): (["Horn Style", "Facial Hair"], {24: 3}),                                   # 17 x 13 (the horns players pick)
    (6, 1): (["Horn Style", "Earrings"], {24: 3, 35: 1}),                               # 20 x 5
    (7, 0): (["Beard", "Mustache"], {}),                                                # 9 x 11
    (7, 1): (["Earrings"], {35: 3}),                                                    # 15
    (8, 0): (["Tusks", "Earrings", "Piercing"], {40: 3, 35: 1}),                        # 10 x 6 x 3
    (8, 1): (["Tusks", "Earrings", "Piercing"], {40: 3, 35: 1}),                        # 6 x 8 x 3
    (10, 0): (["Facial Hair"], {}),                                                     # 13
    (10, 1): (["Earrings", "Necklace"], {35: 3, 36: 2}),                                # 14 x 4
    (11, 0): (["Facial Hair", "Tendrils", "Circlet"], {37: 3}),                         # 11 x 8 x 2
    (11, 1): (["Horns", "Tendrils", "Tail"], {24: 3, 38: 16}),                          # 12 x 2 x 6
}
# Options of a feature whose choices a player picks only (ChrCustomizationReq), where every choice wouldn't fit.
AVAILABLE_ONLY = {(6, 0): {"Horn Style"}}
# Today's names for an option the allied races' reading asks for by another (the Tauren's mane is their hair style,
# their horns' colour their hair colour: the hair texture).
ALIASES = {6: {"Hair Style": "Foremane", "Hair Color": "Horn Color"}}
# Looks today's game opens by an achievement, open to everyone on Wrath++ from the start: the Blood Elves' Dark Ranger
# skin and red eyes (achievement 15579; the user: "unlock the dark ranger skin by default for blood elves"). The skin
# was among the skins already (a choice any class may pick once it is unlocked); the eye colour is marked as one the
# creator hides (Flags) and was left out with the demon hunters' blind eyes. With it the women's twelve eye colours
# (3.3.5 holds 255 faces: 20 faces x 12) no longer have room for the death knights' own, which is the last and goes:
# 3.3.5 lights a death knight's eyes by itself.
UNLOCKED_ACHIEVEMENTS = {10: {"15579"}}
SEXES = ("Male", "Female")
# Models that don't convert yet: the game's own (Alternative HD) look stays for them, rows and all. The Blood Elf man's
# arms and legs come out shredded (his skeleton file's 252 bones; the other nineteen models are right): open.
SKIP = {(10, 0)}


class Tables(allied.Tables):
    """The allied races' reading of the tables, with the ten races' own names for an option."""

    def __init__(self, csv_dir):
        super().__init__(csv_dir)
        self.aliases = {}
        self.only_available = {}
        self.unlocked = set()

    def unlock(self, model_id, achievements):
        """The choices of a model's options that only an achievement of [achievements] closes: never left out for being hidden."""
        for o in self.options.values():
            if o["ChrModelID"] != str(model_id):
                continue
            for c in self.choices[o["ID"]]:
                req = self.reqs.get(c["ChrCustomizationReqID"])
                if req is not None and req.get("ReqAchievementID") in achievements:
                    self.unlocked.add(c["ID"])

    def option_choices(self, model_id, name, only_available=True):
        name = self.aliases.get((str(model_id), name), name)
        if name in self.only_available.get(str(model_id), ()):
            only_available = True
        return super().option_choices(model_id, name, only_available)


def build_races(csv_dir):
    tables = Tables(csv_dir)
    out = {"build": BUILD, "races": {}}
    for race_id, (name, models) in RACES.items():
        entry = {"race": race_id, "name": name, "models": {}}
        for sex, chr_model in models.items():
            if (race_id, sex) in SKIP:
                continue
            for asked, today in ALIASES.get(race_id, {}).items():
                tables.aliases[(str(chr_model), asked)] = today
            tables.only_available[str(chr_model)] = AVAILABLE_ONLY.get((race_id, sex), set())
            tables.unlock(chr_model, UNLOCKED_ACHIEVEMENTS.get(race_id, set()))
            key = "wpp%d_%d" % (race_id, sex)
            allied.FEATURES[(key, sex)] = FEATURES[(race_id, sex)]
            file_id = allied.model_file(tables, chr_model)
            if not file_id:
                raise SystemExit("no model file for ChrModel %d (CreatureDisplayInfo.csv is needed)" % chr_model)
            race = {"race": race_id, "name": name, "parent_models": {sex: 0}, "eye_colours": 0}
            model = allied.build_model(tables, key, race, sex, chr_model, file_id)
            if len(model["features"]) > 255:
                raise SystemExit("%s: %d features, past 3.3.5's 255" % (model["name"], len(model["features"])))
            model["chr_model"] = chr_model
            entry["models"][str(sex)] = model
        out["races"][str(race_id)] = entry
    return out


# --- the game's tables (WDBC) ---------------------------------------------------------------------------------------

class Dbc:
    def __init__(self, data, kinds):
        magic, count, fields, size, text_size = struct.unpack_from("<4s4I", data)
        if magic != b"WDBC" or fields != len(kinds) or size != fields * 4:
            raise ValueError("not the table expected (%d fields)" % fields)
        text = data[20 + count * size:]
        self.kinds = kinds
        self.rows = []
        for i in range(count):
            raw = struct.unpack_from("<%dI" % fields, data, 20 + i * size)
            self.rows.append([text[v:text.index(b"\0", v)].decode("utf-8") if k == "s" else v for k, v in zip(kinds, raw)])

    def write(self):
        strings = bytearray(b"\0")
        where = {"": 0}
        body = bytearray()
        for row in self.rows:
            for k, v in zip(self.kinds, row):
                if k == "s":
                    if v not in where:
                        where[v] = len(strings)
                        strings += v.encode("utf-8") + b"\0"
                    body += struct.pack("<I", where[v])
                else:
                    body += struct.pack("<I", v & 0xFFFFFFFF)
        n = len(self.kinds)
        return struct.pack("<4s4I", b"WDBC", len(self.rows), n, n * 4, len(strings)) + bytes(body) + bytes(strings)


TABLE_KINDS = {"CharSections": "iiiisssiii", "CharHairGeosets": "iiiiii", "CharacterFacialHairStyles": "iiiiiiii"}


def table_rows(looks):
    """The ten races' rows of the three tables, as the allied races' build_data.py makes theirs (names.py's paths)."""
    import names
    sections, hair, facial = [], [], []
    for entry in looks["races"].values():
        race = entry["race"]
        for sex, m in sorted(entry["models"].items()):
            sex = int(sex)
            for s in m["skins"]:
                c = s["index"]
                sections.append([race, sex, 0, names.skin(m, c), "", "", 17, 0, c])
                if s["pelvis"]:
                    sections.append([race, sex, 4, names.pelvis(m, c), names.torso(m, c) if s["torso"] else "", "", 17, 0, c])
            for fi, face in enumerate(m["faces"]):
                for s in m["skins"]:
                    fid = names.face_file(m, face, s)
                    for eye in m["eyes"]:
                        sections.append([race, sex, 1, names.face_lower(m, fid, eye), names.face_upper(m, eye), "", 1,
                                         names.face_variation(m, fi, eye["index"]), s["index"]])
            for h in m["hair"]:
                for hc in m["hair_colors"]:
                    sections.append([race, sex, 3, names.hair(m, hc["index"]), "", "", 17, h["variation"], hc["index"]])
                hair.append([race, sex, h["variation"], h["geoset"], 0])
            for f in m["features"]:
                facial.append([race, sex, f["variation"]] + list(f["geosets"]))
    return sections, hair, facial


def tables_for(looks, dbc_dir):
    """The three tables: the server's own with every row of the ten races replaced by theirs. The glow column of the
    facial table (geoset group 17: night elves' eyes) as the race had it."""
    mine = {(entry["race"], int(sex)) for entry in looks["races"].values() for sex in entry["models"]}
    out = {}
    read = lambda name: Dbc(open(os.path.join(dbc_dir, name + ".dbc"), "rb").read(), TABLE_KINDS[name])
    sections, hair, facial = table_rows(looks)
    t = read("CharSections")
    kept = [r for r in t.rows if (r[1], r[2]) not in mine]
    next_id = max([r[0] for r in t.rows] + [0]) + 1
    t.rows = kept + [[next_id + i] + r for i, r in enumerate(sections)]
    out["CharSections"] = t
    t = read("CharHairGeosets")
    kept = [r for r in t.rows if (r[1], r[2]) not in mine]
    next_id = max([r[0] for r in t.rows] + [0]) + 1
    t.rows = kept + [[next_id + i] + r for i, r in enumerate(hair)]
    out["CharHairGeosets"] = t
    t = read("CharacterFacialHairStyles")
    glow = {}
    for r in t.rows:
        glow.setdefault((r[0], r[1]), r[7])
    kept = [r for r in t.rows if (r[0], r[1]) not in mine]
    t.rows = kept + [r[:7] + [glow.get((r[0], r[1]), 0)] for r in facial]
    out["CharacterFacialHairStyles"] = t
    return out


def package(looks_path, cache, dbc_dir, out_dir, log=print):
    import check_m2
    import m2
    import package as allied_package
    import textures
    with open(looks_path) as f:
        looks = json.load(f)
    read = allied_package.cached(cache, allied_package.wago)
    client = os.path.join(out_dir, "client")
    written = []
    for entry in looks["races"].values():
        for sex, model in sorted(entry["models"].items()):
            written += m2.convert(read, dict(model, geosets=None), client, log)
            model_path = os.path.join(client, model["folder"].replace("\\", "/"), model["name"] + ".m2")
            problems = check_m2.check(model_path)
            if problems:
                raise ValueError("%s: %s" % (model["name"], "; ".join(problems[:20])))
            layout_path = model_path[:-3] + ".layout.json"
            with open(layout_path) as f:
                layout = json.load(f)
            os.remove(layout_path)
            written += textures.build(read, model, layout, client, log)
            for path, fid in model["hardcoded_files"].items():
                full = os.path.join(client, path.replace("\\", "/"))
                os.makedirs(os.path.dirname(full), exist_ok=True)
                with open(full, "wb") as out:
                    out.write(read(fid))
                written.append(path)
    written += write_tables(looks, dbc_dir, out_dir)
    missing = verify(looks, dbc_dir, out_dir)
    if missing:
        raise ValueError("%d files the tables name are not in the package, e.g. %s" % (len(missing), ", ".join(missing[:5])))
    with open(os.path.join(out_dir, "looks.files"), "w") as out:
        out.write("".join(p + "\n" for p in sorted(set(written))))
    log("looks: %d files" % len(set(written)))


def verify(looks, dbc_dir, out_dir):
    """The files the ten races' new rows name that the package lacks (a table row naming no file is a white character)."""
    client = os.path.join(out_dir, "client")
    have = set()
    for root, _, files in os.walk(client):
        for f in files:
            have.add(os.path.relpath(os.path.join(root, f), client).replace("/", "\\").lower())
    sections, hair, facial = table_rows(looks)
    named = {r[3] for r in sections} | {r[4] for r in sections} | {r[5] for r in sections}
    named.discard("")
    for entry in looks["races"].values():
        for m in entry["models"].values():
            named.add(m["folder"] + "\\" + m["name"] + ".m2")
    return sorted(n for n in named if n.lower() not in have)


def write_tables(looks, dbc_dir, out_dir):
    """The three tables into OUT/client/DBFilesClient and OUT/dbc; their game paths."""
    client = os.path.join(out_dir, "client")
    os.makedirs(os.path.join(client, "DBFilesClient"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "dbc"), exist_ok=True)
    written = []
    for name, t in tables_for(looks, dbc_dir).items():
        blob = t.write()
        for path in (os.path.join(client, "DBFilesClient", name + ".dbc"), os.path.join(out_dir, "dbc", name + ".dbc")):
            with open(path, "wb") as out:
                out.write(blob)
        written.append("DBFilesClient\\%s.dbc" % name)
    return written


def fetch(csv_dir):
    import sl_inventory
    saved = sl_inventory.TABLES
    try:
        sl_inventory.TABLES = tuple(saved) + TABLES_MORE
        sl_inventory.fetch(csv_dir)
    finally:
        sl_inventory.TABLES = saved


def main(argv):
    if len(argv) == 3 and argv[1] == "fetch":
        fetch(argv[2])
        return 0
    if len(argv) == 4 and argv[1] == "races":
        looks = build_races(argv[2])
        with open(argv[3], "w") as f:
            json.dump(looks, f, indent=1, sort_keys=True)
        for entry in looks["races"].values():
            for sex, m in sorted(entry["models"].items()):
                print("%s: %d skins, %d faces x %d eyes, %d hair styles x %d colours, %d features (%s)" % (
                    m["name"], len(m["skins"]), len(m["faces"]), len(m["eyes"]), len(m["hair"]), len(m["hair_colors"]),
                    len(m["features"]), ", ".join(m["feature_options"])))
        return 0
    if len(argv) == 5 and argv[1] == "verify":
        with open(argv[2]) as f:
            missing = verify(json.load(f), argv[3], argv[4])
        print("%d missing" % len(missing), *missing[:20], sep="\n")
        return 1 if missing else 0
    if len(argv) == 6 and argv[1] == "package":
        package(argv[2], argv[3], argv[4], argv[5])
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
