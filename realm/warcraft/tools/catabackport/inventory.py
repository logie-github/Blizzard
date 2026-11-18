"""Stage `inventory`: the maps of the pinned Cataclysm build, as a manifest with one entry per map.

Reads Map (and AreaTable for the id plan) from the source, each map's WDT for its tiles (the listfile's names when the WDT
cannot be had), decides group, terrain-swap base, new ids and the weight the shard plan uses. Writes manifest.json and
inventory-report.txt. Everything here is from the tables and pinned configuration (data/overrides.json): nobody chooses.
"""
import csv
import io
import json
import os
import re
import struct

from . import ids, listfile, source as src, util

CONTINENTS = {"azeroth", "kalimdor", "expansion01", "northrend"}
GROUPS = {0: "world", 1: "dungeon", 2: "raid", 3: "battleground", 4: "arena"}


def rows(text):
    return list(csv.DictReader(io.StringIO(text)))


def num(v, default=0):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return default


def wdt_tiles(data):
    """The tiles a WDT says have an ADT: its MAIN chunk, 64 x 64 entries of 8 bytes (flag 1 = has one)."""
    i = 0
    while i + 8 <= len(data):
        magic = data[i:i + 4]
        size = struct.unpack_from("<I", data, i + 4)[0]
        if magic[::-1] == b"MAIN" or magic == b"MAIN":
            body = data[i + 8:i + 8 + size]
            return sorted((n % 64, n // 64) for n in range(min(4096, len(body) // 8))
                          if struct.unpack_from("<I", body, n * 8)[0] & 1)
        i += 8 + size
    return None


def swap_base(directory, all_dirs):
    """The generic rule for a terrain swap: `<other>phase...`, `<other>_phase...` where <other> is another map's directory."""
    d = directory.lower()
    m = re.match(r"^(.*?)_?phase[a-z0-9_]*$", d)
    if m and m.group(1) and m.group(1) in all_dirs and m.group(1) != d:
        return m.group(1)
    return None


def classify(row, directory, is_swap):
    if is_swap:
        return "swap"
    if directory.lower() in CONTINENTS:
        return "continent"
    return GROUPS.get(num(row.get("InstanceType")), "other")


def build(source, pins, listfile_path=None, overrides=None, report=None):
    """Returns the manifest dict. `report` is a list that gets one line for everything not taken and why."""
    report = report if report is not None else []
    overrides = overrides or util.load_json(os.path.join(util.HERE, "data", "overrides.json"), {})
    table = rows(source.table("Map"))
    by_path, tiles_listed = {}, {}
    if listfile_path:
        _, by_path = listfile.load(listfile_path, prefixes=("world/maps/",))
        tiles_listed = listfile.tiles_by_dir(by_path)
    st = ids.stock()
    all_dirs = {r["Directory"].lower() for r in table if r.get("Directory")}
    taken_dirs = set(st["map_dirs"])
    maps = []
    for r in sorted(table, key=lambda r: num(r["ID"])):
        mid, directory = num(r["ID"]), overrides.get("directory", {}).get(r["ID"], r.get("Directory", ""))
        if not directory:
            report.append(f"map {mid}: no directory (not a world map), not taken")
            continue
        if mid in overrides.get("exclude", []) or re.match(overrides.get("exclude_dir_regex", "(?!x)x"), directory, re.I):
            report.append(f"map {mid} {directory}: excluded by data/overrides.json")
            continue
        if num(r.get("ExpansionID")) > pins["max_expansion"]:
            report.append(f"map {mid} {directory}: expansion {r.get('ExpansionID')} is past Cataclysm, not taken")
            continue
        base = overrides.get("swap_of", {}).get(str(mid))
        base_dir = None
        if base is None:
            base_dir = swap_base(directory, all_dirs)
            if base_dir:
                base = next(num(x["ID"]) for x in table if x.get("Directory", "").lower() == base_dir)
        entry = {"id": mid, "dir": directory, "name": r.get("MapName_lang", ""), "instance_type": num(r.get("InstanceType")),
                 "parent": num(r.get("ParentMapID")), "expansion": num(r.get("ExpansionID")),
                 "swap_of": base, "group": classify(r, directory, base is not None)}
        # The tiles: the WDT's MAIN chunk; the listfile's names where the WDT can't be had.
        wdt_id = num(r.get("WdtFileDataID")) or by_path.get(f"world/maps/{directory.lower()}/{directory.lower()}.wdt", 0)
        entry["wdt_fdid"] = wdt_id
        tiles, how = None, ""
        if wdt_id:
            try:
                tiles = wdt_tiles(source.file(wdt_id))
                how = "wdt"
            except src.Missing:
                report.append(f"map {mid} {directory}: WDT {wdt_id} is not in the build")
            except src.SourceDown as e:
                report.append(f"map {mid} {directory}: WDT not fetched, source down ({e}); tiles from the listfile")
        if tiles is None and directory.lower() in tiles_listed:
            tiles, how = tiles_listed[directory.lower()], "listfile"
        if tiles is None and not wdt_id:
            report.append(f"map {mid} {directory}: no WDT and no tiles named: not taken")
            continue
        entry["tiles"] = [list(t) for t in (tiles or [])]
        entry["tiles_from"] = how or "unknown"
        entry["n_tiles"] = len(entry["tiles"])
        entry["weight"] = max(1, entry["n_tiles"])
        # What it is next to 3.3.5a: a map the game has not (new), one it has that Cataclysm made over (revamped: the pinned list),
        # or one it has as it is (stock: the same as Wrath's, not redone unless named by id).
        entry["origin"] = "revamped" if mid in overrides.get("revamped", []) else ("stock" if mid in st["map_ids"] else "new")
        entry["status"] = ("done_elsewhere" if mid in overrides.get("done_elsewhere", []) else
                           "planned" if entry["origin"] != "stock" else "same_as_stock")
        maps.append(entry)
    # (ids for the maps that are made; a "revamped" map is always renumbered: it lives beside 3.3.5a's own, CATA_BACKPORT.md 5.1)
    made = [m for m in maps if m["status"] in ("planned", "done_elsewhere")]
    new = ids.alloc_map_ids([m["id"] for m in made if m["origin"] != "revamped"], st["map_ids"], taken_dirs,
                            {m["id"]: m["dir"] for m in made})
    revamped = ids.alloc_map_ids([m["id"] for m in made if m["origin"] == "revamped"], set(st["map_ids"]) | set(new.values()),
                                 set(), {}, force_move=True)
    new.update(revamped)
    for m in maps:
        m["new_id"] = new.get(m["id"], m["id"])
        m["new_dir"] = ids.new_dir(m["dir"], m["id"], m["new_id"], taken_dirs)
        m["input_hash"] = util.input_hash(pins["build"], pins["converter"]["commit"], m["id"], m["dir"], m["tiles"])
    manifest = {"version": 1, "build": pins["build"], "pins": pins, "maps": maps}
    return manifest


def id_plan(source, manifest):
    """ids.json: Cataclysm's area ids and explore bits over *every* area of the manifest's maps, decided once for the whole
    expansion (so that a shard's ids do not depend on which maps ran with it)."""
    st = ids.stock()
    maps = {m["id"] for m in manifest["maps"] if m["status"] in ("planned", "done_elsewhere")}
    areas = [r for r in rows(source.table("AreaTable")) if num(r.get("ContinentID")) in maps]
    area_ids = ids.alloc_area_ids([num(r["ID"]) for r in areas], st["area_ids"])
    bits, none = ids.alloc_explore_bits({num(r["ID"]): num(r.get("AreaBit", r.get("ExploreFlag", 0))) for r in areas}, st["area_bits"],
                                        st.get("area_bit_by_id"))
    return {"maps": {str(m["id"]): m["new_id"] for m in manifest["maps"]}, "areas": {str(k): v for k, v in area_ids.items()},
            "explore_bits": {str(k): v for k, v in bits.items()}, "no_explore_bit": none}


def pick_proof(manifest):
    """The smallest dungeon with tiles (ties by id): the map a first run proves the pipeline on."""
    c = [m for m in manifest["maps"] if m["group"] == "dungeon" and m["n_tiles"] and m["status"] == "planned"]
    c.sort(key=lambda m: (m["n_tiles"], m["id"]))
    return c[0]["id"] if c else None


def report_text(manifest, report):
    by = {}
    for m in manifest["maps"]:
        g = by.setdefault(m["group"], [0, 0])
        g[0] += 1
        g[1] += m["n_tiles"]
    lines = [f"build {manifest['build']}: {len(manifest['maps'])} maps taken"]
    lines += [f"  {g}: {n} maps, {t} tiles" for g, (n, t) in sorted(by.items())]
    lines.append(f"proof map: {pick_proof(manifest)}")
    lines += ["not taken / notes:"] + ["  " + r for r in report]
    return "\n".join(lines) + "\n"


def run(source, pins, work, listfile_path=None, builds_note=True):
    report = []
    manifest = build(source, pins, listfile_path, report=report)
    try:
        manifest["id_plan"] = id_plan(source, manifest)
    except src.Missing:
        report.append("AreaTable is not in the build: no area id plan")
    except src.SourceDown as e:
        report.append(f"AreaTable not fetched, source down ({e}): no area id plan")
    manifest["proof"] = pick_proof(manifest)
    util.dump_json(os.path.join(work, "manifest.json"), manifest)
    util.write_atomic(os.path.join(work, "inventory-report.txt"), report_text(manifest, report))
    return manifest
