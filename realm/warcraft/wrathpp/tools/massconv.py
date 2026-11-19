#!/usr/bin/env python3
"""Wrath++'s mass check of what the converters made: every race and every zone of a manifest, one run, one report.

The races (Shadowlands' models by sl_looks.py, Cataclysm's by mod-worgen-goblin) and the Cataclysm zones are each converted by
their own tool; what was missing or wrong in one of them used to be found on the phone (the Worgen woman's head floating over a human
body, the Goblins' ears and chin 'not drawn yet', a model named by a table and not in the package). This reads the finished package
and says, for each entry of the manifest, what is missing or broken:

  races   the ChrRaces row; both sexes' display rows, their model rows and the model files and skins named; the model's own
          structure (check_m2); each sex's skin, face, hair and facial hair rows in CharSections, CharBaseInfo's class combinations and
          CharStartOutfit rows for every class; the character textures (check_textures); and, from the creator's report, every
          option still 'not drawn yet' for the race.
  zones   each map's WDT, every tile it lists and every model and world object those tiles name.

    python3 tools/massconv.py audit LOOKS_DIR MANIFEST.json [--report looks-report.txt] [--zones ZONES_DIR]

LOOKS_DIR: the package folder (dbc/*.dbc, client/...). MANIFEST: tools/massconv.json. Prints one line per problem and a summary per entry;
exit status 1 when anything is wrong (--warn-only: always 0).
"""
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "modules", "mod-allied-races", "tools"))

SEXES = ("Male", "Female")
SKIN, FACE, FACIAL_HAIR, HAIR, UNDERWEAR = 0, 1, 2, 3, 4


def dbc_rows(path):
    """A DBC's records as tuples of 32-bit words, and its string block."""
    with open(path, "rb") as f:
        d = f.read()
    if d[:4] != b"WDBC":
        raise ValueError("not a DBC: " + path)
    n, fields, size, strings = struct.unpack_from("<4I", d, 4)
    if size == fields * 4:
        rows = [struct.unpack_from("<%dI" % fields, d, 20 + i * size) for i in range(n)]
    else:                                                    # byte fields (CharBaseInfo: race, class)
        rows = [tuple(d[20 + i * size:20 + (i + 1) * size]) for i in range(n)]
    return rows, d[20 + n * size:20 + n * size + strings]


def string_at(block, offset):
    if offset >= len(block):
        return ""
    end = block.index(b"\0", offset)
    return block[offset:end].decode("utf-8", "replace")


def find(root, rel):
    """The file [rel] under [root], any case, .mdx for .m2, or None."""
    cur = root
    for part in rel.replace("\\", "/").split("/"):
        if not os.path.isdir(cur):
            return None
        names = {n.lower(): n for n in os.listdir(cur)}
        low = part.lower()
        if low not in names and low.endswith(".mdx"):
            low = low[:-4] + ".m2"
        if low not in names and low.endswith(".mdl"):
            low = low[:-4] + ".m2"
        if low not in names:
            return None
        cur = os.path.join(cur, names[low])
    return cur if os.path.isfile(cur) else None


def model_files(client, model_path):
    """The model file and its first skin (3.3.5 keeps a model's vertices' draw lists in Name00.skin), or (None, None)."""
    m2 = find(client, model_path)
    if m2 is None:
        return None, None
    skin = find(client, os.path.splitext(model_path)[0] + "00.skin")
    return m2, skin


def audit_race(looks, race, tables, report_lines, problems):
    """Every check of one manifest race: [race] is {id, name, models: {Male: path, Female: path}, classes: [...]}. Problems are
    appended to [problems] as (race name, text)."""
    rid, name = race["id"], race["name"]
    client = os.path.join(looks, "client")

    def bad(text):
        problems.append((name, text))

    row = tables["ChrRaces"].get(rid)
    if row is None:
        bad("no ChrRaces row for race %d" % rid)
        return
    displays = {"Male": row[4], "Female": row[5]}
    base = tables["CharBaseInfo.keys"]
    allowed = sorted(c for r, c in base if r == rid) if base is not None else []     # the classes the race may be made as
    if base is not None and not allowed:
        bad("CharBaseInfo allows no class for race %d" % rid)
    for sex in SEXES:
        did = displays[sex]
        d = tables["CreatureDisplayInfo"].get(did)
        if d is None:
            bad("%s: ChrRaces names display %d and CreatureDisplayInfo has no such row" % (sex, did))
            continue
        m = tables["CreatureModelData"].get(d[1])
        if m is None:
            bad("%s: display %d names model row %d and CreatureModelData has no such row" % (sex, did, d[1]))
            continue
        path = tables["CreatureModelData.path"][d[1]]
        m2, skin = model_files(client, path)
        if m2 is None:
            bad("%s: model %s (row %d) is not in the package" % (sex, path, d[1]))
        else:
            try:
                import check_m2
                for p in check_m2.check(m2):
                    bad("%s: %s: %s" % (sex, os.path.basename(m2), p))
            except ImportError:
                pass
            if skin is None:
                bad("%s: %s has no 00.skin" % (sex, os.path.basename(m2)))
        want = race.get("models", {}).get(sex)
        if want and path.replace("/", "\\").lower().replace(".mdx", ".m2") != want.replace("/", "\\").lower().replace(".mdx", ".m2"):
            bad("%s: the table names %s, the manifest %s" % (sex, path, want))
        sexid = SEXES.index(sex)
        sections = [r for r in tables["CharSections.rows"] if r[1] == rid and r[2] == sexid]
        kinds = {r[3] for r in sections}
        for kind, label in ((SKIN, "skin"), (FACE, "face"), (HAIR, "hair")):
            if kind not in kinds and race.get("needs", {}).get(label, True):
                bad("%s: no %s rows in CharSections" % (sex, label))
        # every skin colour has a face of every kind, as the screen counts them
        skins = {r[9] for r in sections if r[3] == SKIN and r[8] == 0}
        if not skins and SKIN in kinds:
            bad("%s: skin rows but no colour 0 of variation 0" % sex)
        for cls in allowed:
            if tables["CharStartOutfit.keys"] is not None and (rid, sexid, cls) not in tables["CharStartOutfit.keys"] and race.get("outfits", True):
                bad("%s: CharBaseInfo allows class %d and CharStartOutfit has no row for it" % (sex, cls))
    for cls in race.get("classes", []):
        if base is not None and cls not in allowed:
            bad("CharBaseInfo does not allow race %d with class %d" % (rid, cls))
    # the creator's report: what is still 'not drawn yet' for the race
    for line in report_lines:
        m = re.match(r"^(\w+?)(Male|Female): .*not drawn yet: (.*)$", line)
        if m and m.group(1).lower() == race.get("token", name).lower().replace(" ", ""):
            bad("%s: options not drawn yet: %s" % (m.group(2), m.group(3)))


def load_tables(looks):
    d = os.path.join(looks, "dbc")
    t = {}
    rows, _ = dbc_rows(os.path.join(d, "ChrRaces.dbc"))
    t["ChrRaces"] = {r[0]: r for r in rows}
    rows, _ = dbc_rows(os.path.join(d, "CreatureDisplayInfo.dbc"))
    t["CreatureDisplayInfo"] = {r[0]: r for r in rows}
    rows, block = dbc_rows(os.path.join(d, "CreatureModelData.dbc"))
    t["CreatureModelData"] = {r[0]: r for r in rows}
    t["CreatureModelData.path"] = {r[0]: string_at(block, r[2]) for r in rows}
    rows, _ = dbc_rows(os.path.join(d, "CharSections.dbc"))
    t["CharSections.rows"] = rows
    try:
        rows, _ = dbc_rows(os.path.join(d, "CharBaseInfo.dbc"))
        t["CharBaseInfo.keys"] = {(r[0], r[1]) for r in rows}
    except (OSError, ValueError):
        t["CharBaseInfo.keys"] = None                        # not in this package: its checks are left out
    try:
        rows, _ = dbc_rows(os.path.join(d, "CharStartOutfit.dbc"))
        t["CharStartOutfit.keys"] = {(r[1] & 0xFF, (r[1] >> 16) & 0xFF, (r[1] >> 8) & 0xFF) for r in rows}
    except (OSError, ValueError):
        t["CharStartOutfit.keys"] = None
    return t


def audit_zone(zones, zone, problems):
    """One manifest zone: {name, map}: its WDT, every tile the WDT lists, and every name its tiles' model and object lists hold."""
    name, folder = zone["name"], zone["map"]
    base = os.path.join(zones, "World", "Maps", folder)

    def bad(text):
        problems.append((name, text))

    wdt = find(zones, "World/Maps/%s/%s.wdt" % (folder, folder))
    if wdt is None:
        bad("no %s.wdt" % folder)
        return
    data = open(wdt, "rb").read()
    tiles = []
    i = 0
    while i + 8 <= len(data):
        tag, size = data[i:i + 4], struct.unpack_from("<I", data, i + 4)[0]
        if tag == b"NIAM":                                   # MAIN, stored reversed
            for n in range(64 * 64):
                flags = struct.unpack_from("<I", data, i + 8 + n * 8)[0]
                if flags & 1:
                    tiles.append((n % 64, n // 64))
        i += 8 + size
    if not tiles:
        bad("the WDT lists no tiles")
    for x, y in tiles:
        adt = find(zones, "World/Maps/%s/%s_%d_%d.adt" % (folder, folder, x, y))
        if adt is None:
            bad("tile %d_%d is listed and not in the package" % (x, y))
            continue
        blob = open(adt, "rb").read()
        j = 0
        while j + 8 <= len(blob):
            tag, size = blob[j:j + 4], struct.unpack_from("<I", blob, j + 4)[0]
            if tag in (b"XDMM", b"OMWM"):                    # MMDX models, MWMO world objects: zero-separated names
                for nm in blob[j + 8:j + 8 + size].split(b"\0"):
                    if nm and find(zones, nm.decode("utf-8", "replace")) is None:
                        bad("tile %d_%d names %s and it is not in the package" % (x, y, nm.decode("utf-8", "replace")))
            j += 8 + size


def main(argv):
    if len(argv) < 4 or argv[1] != "audit":
        print(__doc__)
        return 2
    looks, manifest = argv[2], argv[3]
    warn_only = "--warn-only" in argv
    report = []
    if "--report" in argv:
        report = open(argv[argv.index("--report") + 1], encoding="utf-8", errors="replace").read().splitlines()
    zones = argv[argv.index("--zones") + 1] if "--zones" in argv else None
    spec = json.load(open(manifest, encoding="utf-8"))
    problems = []
    tables = load_tables(looks)
    for race in spec.get("races", []):
        audit_race(looks, race, tables, report, problems)
    if zones:
        for zone in spec.get("zones", []):
            audit_zone(zones, zone, problems)
    names = [r["name"] for r in spec.get("races", [])] + [z["name"] for z in spec.get("zones", []) if zones]
    for name in names:
        mine = [t for n, t in problems if n == name]
        print("%-22s %s" % (name, "ok" if not mine else "%d problem(s)" % len(mine)))
        for t in mine:
            print("    " + t)
    print("%d problem(s) in %d entries" % (len(problems), len(names)))
    return 0 if warn_only or not problems else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
