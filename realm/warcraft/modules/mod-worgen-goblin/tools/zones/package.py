#!/usr/bin/env python3
"""The starting areas' package (cata-zones.tar.xz, a release of its own the app downloads): the game's
files for them, made for 3.3.5a, and the world server's data for their maps.

    python3 tools/zones/package.py CACHE CONVERTER TOOLS SERVER_DBC OUT

CACHE: where the game's files are kept between runs (fetched from wago.tools at common.BUILD, by the
ids data/zones/files.tsv lists); CONVERTER: wotlkconv (github.com/Bar3b0n3s/Converter, the commit
warcraft/server-version.env pins) as a command; TOOLS: a folder with AzerothCore's map_extractor,
vmap4_extractor, vmap4_assembler and mmaps_generator (built from the realm's core, for this machine)
and its mmaps-config.yaml; SERVER_DBC: the server data's dbc folder (3.3.5a's tables); OUT: the
package's folder, made empty first:

  client/files/...      the game's files at their paths in the game (lower case), made for 3.3.5a:
                        the maps (Cataclysm's split tiles made whole, and the terrain swaps made into
                        whole maps), the models, buildings and textures they place, the minimap
                        pictures, the world maps' pictures, the loading screens, the music and sounds
  client/files.txt      their paths in the game (backslashes), a line each
  client/same.txt       paths in the game whose file is another's (a terrain swap's tiles that are its
                        base map's): "path<TAB>the other's path"; the patch keeps such a file once
  client/minimap.txt    the lines for the game's minimap index (textures\\minimap\\md5translate.trs)
  server/maps|vmaps|mmaps/...   the world server's data for the seven maps
  server/cameras/...    the race intros' camera flights (their models), which the world server follows
                        to send the game what each passes (ctl.sh puts them in its data's cameras/)
  server/same.txt       the same, for the server's files (a terrain swap's tiles that are its base's)
  VERSION               what it was made from

Nothing in it replaces a file of 3.3.5a's: the patch the realm makes of it adds the files the game
hasn't (src/WorgenGoblinPatch.cpp), and the server's files are new maps' (ctl.sh zones).
"""
import concurrent.futures
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODULE = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(MODULE), "mod-skyborne", "tools"))
import common  # noqa: E402

ZONES = os.path.join(MODULE, "data", "zones")
# 3.3.5a's liquid types (LiquidType.dbc): a Cataclysm one it hasn't is made the 3.3.5a one of its kind
# (by Cataclysm's own: its sound bank, 0 water, 1 ocean, 2 magma, 3 slime).
LIQUIDS_335 = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 19, 20, 21, 41, 61, 81, 100, 121, 141, 181}
LIQUID_KIND = {0: 1, 1: 2, 2: 3, 3: 4}
# Textures of the world (terrain, models, buildings) at most this big: 3.3.5a is a 32-bit game, and a
# phone's; the interface's (world maps, loading screens) as they are.
WORLD_TEXTURES = 512


def read_aliases():
    """aliases.tsv: {file id: the other paths the game loads it by}."""
    path, aliases = os.path.join(ZONES, "aliases.tsv"), {}
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            if line.startswith("#") or not line.strip():
                continue
            fdid, alias = line.rstrip("\n").split("\t")
            aliases.setdefault(int(fdid), []).append(alias)
    return aliases


def put_aliases(conv, files, aliases):
    """Each converted file again at the other paths the game loads it by (an item's model, textures
    and icon where 3.3.5a's ItemDisplayInfo looks: aliases.tsv); a model's skins and animations go
    with it. Their data is shared in the patch (dedupe)."""
    made = 0
    for fdid, paths in sorted(aliases.items()):
        if fdid not in files:
            continue
        src = os.path.join(conv, files[fdid][0])
        if not os.path.exists(src):
            continue
        pairs = [(src, os.path.join(conv, a)) for a in paths]
        if src.endswith(".m2"):
            folder, stem = os.path.dirname(src), os.path.basename(src)[:-3]
            for name in os.listdir(folder):
                if name.startswith(stem) and name.endswith((".skin", ".anim")) and name[len(stem):len(stem) + 1].isdigit():
                    for a in paths:
                        pairs.append((os.path.join(folder, name), os.path.join(conv, a[:-3] + name[len(stem):])))
        for a, b in pairs:
            if os.path.exists(b):
                continue
            os.makedirs(os.path.dirname(b), exist_ok=True)
            shutil.copyfile(a, b)
            made += 1
    print(f"{made} files put where 3.3.5a also loads them")


def run(*args, **kw):
    print("+", " ".join(str(a) for a in args), flush=True)
    subprocess.run([str(a) for a in args], check=True, **kw)


def read_files():
    files = {}
    for line in open(os.path.join(ZONES, "files.tsv"), encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        fdid, path, kind = line.rstrip("\n").split("\t")
        files[int(fdid)] = (path, kind)
    return files


def fetch(cache, files, stage):
    """Every file into stage/<its path> (Cataclysm Classic's, as it is)."""
    def one(item):
        fdid, (path, _) = item
        data = common.file_bytes(cache, fdid)
        if not data:
            return path
        dest = os.path.join(stage, path)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(data)
        return None
    with concurrent.futures.ThreadPoolExecutor(8) as pool:
        missing = [p for p in pool.map(one, sorted(files.items())) if p]
    print(f"fetched {len(files) - len(missing)} files; {len(missing)} not in the build")
    return missing


def convert(converter, stage, conv, listfile):
    """wotlkconv over every folder of the game's (the world's: maps, models, terrain textures, with
    textures at most WORLD_TEXTURES; the interface's as they are), but the sounds (3.3.5a's as they are)."""
    report = {}
    parts = sorted(p for p in os.listdir(stage) if p != "sound" and os.path.isdir(os.path.join(stage, p)))
    for part in parts:
        size = 4096 if part == "interface" else WORLD_TEXTURES
        src = os.path.join(stage, part)
        out = os.path.join(conv, part)
        rep = os.path.join(conv, f"report-{part}.json")
        run(*converter, "convert", src, "-o", out, "--listfile", listfile, "--max-texture-size", size,
            "-j", os.cpu_count() or 4, "-q", "--report", rep)
        report[part] = json.load(open(rep))["accounting"]
        os.remove(rep)
    print(json.dumps(report))
    return report


def skin_batches(data):
    """A skin's batches: (offset of each 24-byte M2Batch)."""
    if data[:4] != b"SKIN":
        return []
    count, at = struct.unpack_from("<II", data, 36)
    return [at + 24 * k for k in range(count)] if at + 24 * count <= len(data) else []


def single_textures(stage, conv):
    """A batch whose Cataclysm shader 3.3.5a hasn't (an 0x8000 shader id: its colour texture with an
    environment reflection, say) the converter resets to 3.3.5a's default with its two or three
    textures kept, which 3.3.5a draws black (seen on a phone: Kezan's pipes): drawn with its first
    texture alone, its colour."""
    fixed = 0
    for root, _, names in os.walk(conv):
        for name in names:
            if not name.endswith(".skin"):
                continue
            out_path = os.path.join(root, name)
            src_path = os.path.join(stage, os.path.relpath(out_path, conv))
            if not os.path.exists(src_path):
                continue
            src, out = open(src_path, "rb").read(), bytearray(open(out_path, "rb").read())
            a, b = skin_batches(src), skin_batches(out)
            if not a or len(a) != len(b):
                continue
            changed = False
            for sa, ob in zip(a, b):
                shader = struct.unpack_from("<H", src, sa + 2)[0]
                if shader & 0x8000 and struct.unpack_from("<H", out, ob + 2)[0] == 0 and struct.unpack_from("<H", out, ob + 14)[0] > 1:
                    struct.pack_into("<H", out, ob + 14, 1)
                    changed = True
                    fixed += 1
            if changed:
                with open(out_path, "wb") as f:
                    f.write(out)
    print(f"{fixed} batches drawn with their colour texture alone")


def m2_tracks(m):
    """The animation tracks of a 3.3.5a model (M2Track: interpolation, global sequence, timestamps,
    values), by where each starts: the bones', colours', texture weights' and transforms',
    attachments' and cameras' (each [(offset, has values)])."""
    def arr(at):
        return struct.unpack_from("<II", m, at)
    out = []
    count, at = arr(44)
    out += [(at + b * 88 + off, True) for b in range(count) for off in (16, 36, 56)]
    count, at = arr(72)
    out += [(at + c * 40 + off, True) for c in range(count) for off in (0, 20)]
    count, at = arr(88)
    out += [(at + w * 20, True) for w in range(count)]
    count, at = arr(96)
    out += [(at + t * 60 + off, True) for t in range(count) for off in (0, 20, 40)]
    count, at = arr(240)
    out += [(at + a * 40 + 20, True) for a in range(count)]
    count, at = arr(272)
    out += [(at + c * 100 + off, True) for c in range(count) for off in (16, 48, 80)]
    return out


def fix_models(conv):
    """Each converted model made as 3.3.5a's own are (seen on a phone: Gilneas's carts, barrels and
    stalls coming and going and swapping at the least turn of the camera, the game's own models
    beside them steady; tools/check_m2.py of mod-allied-races finds each of these):
      - its internal name, its file's (as 3.3.5a's own: Pumpkin01.m2's is "Pumpkin01"): the
        converter leaves it empty, as retail's newer files have it, and 3.3.5a takes a model by it;
      - its animation lookup, by which the game finds a sequence by its animation id (from id % size
        to an empty slot): empty or partial in retail's newer files, made whole;
      - a track that has one set of keys for every sequence (retail's newer way) given one set a
        sequence, as 3.3.5a reads it (the game takes the set of the sequence playing: a doodad's
        stand isn't always its first, and past the one set it read whatever followed);
      - a texture transform its lookup names that the model hasn't: none."""
    named = looked = tracks = lookups = 0

    def append(data, block):
        while len(data) % 16:
            data.append(0)
        at = len(data)
        data += block
        return at

    for root, _, names in os.walk(conv):
        for name in names:
            if not name.lower().endswith(".m2"):
                continue
            path = os.path.join(root, name)
            data = bytearray(open(path, "rb").read())
            if data[:4] != b"MD20":
                continue
            original = bytes(data)
            length, _ = struct.unpack_from("<II", data, 8)
            if length <= 1:
                stem = name[:-3].encode("latin-1") + b"\0"
                struct.pack_into("<II", data, 8, len(stem), append(data, stem))
                named += 1
            sequences, seq_at = struct.unpack_from("<II", data, 28)
            ids = [struct.unpack_from("<H", data, seq_at + 64 * k)[0] for k in range(sequences)]
            in_file = [bool(struct.unpack_from("<I", data, seq_at + 64 * k + 16)[0] & 0x20) for k in range(sequences)]
            if sequences:
                table = [-1] * (max(ids) + 2)
                for k, anim in enumerate(ids):
                    if table[anim] < 0:
                        table[anim] = k
                count, at = struct.unpack_from("<II", data, 36)
                if count != len(table) or list(struct.unpack_from(f"<{count}h", data, at)) != table:
                    struct.pack_into("<II", data, 36, len(table), append(data, struct.pack(f"<{len(table)}h", *table)))
                    looked += 1
            for at, has_values in m2_tracks(data):
                gseq, count, offset = struct.unpack_from("<hII", data, at + 2)
                if gseq >= 0 or count != 1 or sequences < 2:
                    continue
                stamps = struct.unpack_from("<II", data, offset)
                vcount, voffset = struct.unpack_from("<II", data, at + 12)
                values = struct.unpack_from("<II", data, voffset) if vcount == 1 else (0, 0)
                # (a sequence kept in its own file (.anim) reads its keys there: none for it)
                tstamps = b"".join(struct.pack("<II", *(stamps if in_file[k] or k == 0 else (0, 0))) for k in range(sequences))
                tvalues = b"".join(struct.pack("<II", *(values if in_file[k] or k == 0 else (0, 0))) for k in range(sequences))
                struct.pack_into("<II", data, at + 4, sequences, append(data, tstamps))
                if has_values and vcount == 1:
                    struct.pack_into("<II", data, at + 12, sequences, append(data, tvalues))
                tracks += 1
            transforms = struct.unpack_from("<I", data, 96)[0]
            count, at = struct.unpack_from("<II", data, 152)
            for k in range(count):
                if struct.unpack_from("<h", data, at + 2 * k)[0] >= transforms:
                    struct.pack_into("<h", data, at + 2 * k, -1)
                    lookups += 1
            if bytes(data) != original:
                with open(path, "wb") as f:
                    f.write(data)
    print(f"{named} models given their names, {looked} their animation lookup, {tracks} tracks a set of keys "
          f"a sequence, {lookups} texture transform lookups that named none")


def plain_textures(conv):
    """A terrain texture whose plain diffuse file the build hasn't (the tiles name the plain one:
    files.plain_twins) has its specular variant (<name>_s.blp, the same diffuse) under that name."""
    made = 0
    for root, _, names in os.walk(os.path.join(conv, "tileset")):
        for name in names:
            if name.endswith("_s.blp"):
                plain = os.path.join(root, name[:-len("_s.blp")] + ".blp")
                if not os.path.exists(plain):
                    shutil.copyfile(os.path.join(root, name), plain)
                    made += 1
    print(f"{made} terrain textures put under their plain name")


def cameras(conv, out):
    """The camera flights' models for the world server (CinematicCamera's Model: cameras\\<name>.mdx,
    read as <data>/cameras/<name>.m2), as 3.3.5a's map_extractor gives it the game's own."""
    src, dest = os.path.join(conv, "cameras"), os.path.join(out, "cameras")
    os.makedirs(dest, exist_ok=True)
    names = sorted(n for n in os.listdir(src) if n.endswith(".m2")) if os.path.isdir(src) else []
    for name in names:
        shutil.copyfile(os.path.join(src, name), os.path.join(dest, name))
    assert names, "no camera flights converted"
    print(f"server cameras: {names}")


def fix_wdt(path):
    """3.3.5a takes any flag in a WDT's tile list for a tile: Cataclysm's empty tiles keep one
    (0x2); only "has a tile" (0x1) is kept."""
    data = bytearray(open(path, "rb").read())
    at = data.find(b"NIAM")
    assert at >= 0, path
    at += 8
    for k in range(4096):
        flags = struct.unpack_from("<I", data, at + k * 8)[0]
        struct.pack_into("<I", data, at + k * 8, flags & 1)
    with open(path, "wb") as f:
        f.write(data)


def wdt_tiles(path):
    data = open(path, "rb").read()
    at = data.find(b"NIAM") + 8
    return {(k % 64, k // 64) for k in range(4096) if struct.unpack_from("<I", data, at + k * 8)[0] & 1}


def set_wdt_tiles(path, tiles):
    data = bytearray(open(path, "rb").read())
    at = data.find(b"NIAM") + 8
    for k in range(4096):
        struct.pack_into("<I", data, at + k * 8, 1 if (k % 64, k // 64) in tiles else 0)
    with open(path, "wb") as f:
        f.write(data)


def fix_liquids(path, remap):
    """A tile's liquids of a type 3.3.5a hasn't made its kind's 3.3.5a type."""
    data = bytearray(open(path, "rb").read())
    i, changed = 0, 0
    while i + 8 <= len(data):
        magic = data[i:i + 4]
        size = struct.unpack_from("<I", data, i + 4)[0]
        if magic == b"O2HM":
            base = i + 8
            for k in range(256):
                offset, layers, _ = struct.unpack_from("<III", data, base + k * 12)
                for layer in range(layers):
                    at = base + offset + layer * 24
                    kind = struct.unpack_from("<H", data, at)[0]
                    if kind not in LIQUIDS_335:
                        struct.pack_into("<H", data, at, remap.get(kind, 1))
                        changed += 1
        i += 8 + size
    if changed:
        with open(path, "wb") as f:
            f.write(data)
    return changed


def maps(conv, cache):
    """The maps made for 3.3.5a: their WDTs' tiles, their liquids; then each terrain swap made a
    whole map (its base's tiles where it has none of its own). Returns {map dir: {(x, y): path}}."""
    liquids = {}
    for r in common.table(cache, "LiquidType"):
        kind = int(r["SoundBank"])
        liquids[int(r["ID"])] = LIQUID_KIND.get(kind, 1)
    root = os.path.join(conv, "world", "maps")
    tiles = {}
    for directory in common.MAPS.values():
        folder = os.path.join(root, directory.lower())
        wdt = os.path.join(folder, directory.lower() + ".wdt")
        fix_wdt(wdt)
        tiles[directory] = {}
        for name in os.listdir(folder):
            m = re.match(r".*_(\d+)_(\d+)\.adt$", name)
            if m:
                fix_liquids(os.path.join(folder, name), liquids)
                tiles[directory][(int(m.group(1)), int(m.group(2)))] = os.path.join(folder, name)
        assert set(tiles[directory]) == wdt_tiles(wdt), directory
    same = {}
    for map_id, base_id in common.OVERLAYS.items():
        directory, base = common.MAPS[map_id], common.MAPS[base_id]
        folder = os.path.join(root, directory.lower())
        for xy, path in tiles[base].items():
            if xy in tiles[directory]:
                continue
            dest = os.path.join(folder, f"{directory.lower()}_{xy[0]}_{xy[1]}.adt")
            shutil.copyfile(path, dest)
            tiles[directory][xy] = dest
            same[dest] = path
        set_wdt_tiles(os.path.join(folder, directory.lower() + ".wdt"), set(tiles[directory]))
        wdl = os.path.join(folder, directory.lower() + ".wdl")
        if not os.path.exists(wdl):
            shutil.copyfile(os.path.join(root, base.lower(), base.lower() + ".wdl"), wdl)
    return tiles, same


def minimaps(conv, files_dir, tiles):
    """The minimap pictures under textures\\minimap, and the index's lines naming them by map and tile."""
    lines = []
    root = os.path.join(conv, "world", "minimaps")
    for map_id, directory in common.MAPS.items():
        base = common.MAPS.get(common.OVERLAYS.get(map_id, map_id))
        lines.append(f"dir: {directory}")
        for (x, y) in sorted(tiles[directory]):
            own = os.path.join(root, directory.lower(), f"map{x:02d}_{y:02d}.blp")
            src, of = (own, directory) if os.path.exists(own) else (os.path.join(root, base.lower(), f"map{x:02d}_{y:02d}.blp"), base)
            if not os.path.exists(src):
                continue
            name = f"cataclysm_{of.lower()}_map{x:02d}_{y:02d}.blp"
            dest = os.path.join(files_dir, "textures", "minimap", name)
            if not os.path.exists(dest):
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copyfile(src, dest)
            lines.append(f"{directory}\\map{x:02d}_{y:02d}.blp\t{name}")
    shutil.rmtree(root)
    return lines


def dbc(path, rows, types):
    """A 3.3.5a table file of [rows] (values in the order of [types])."""
    strings = bytearray(b"\0")
    offsets = {"": 0}
    records = bytearray()
    for row in rows:
        for v, t in zip(row, types):
            if t == "s":
                if v not in offsets:
                    offsets[v] = len(strings)
                    strings += v.encode("utf-8") + b"\0"
                records += struct.pack("<I", offsets[v])
            elif t == "f":
                records += struct.pack("<f", float(v))
            else:
                records += struct.pack("<I", int(v) & 0xFFFFFFFF)
    with open(path, "wb") as f:
        f.write(b"WDBC" + struct.pack("<4I", len(rows), len(types), 4 * len(types), len(strings)) + records + strings)


def our_rows(table):
    """data/zones/client/dbc/<table>.txt's rows, as values."""
    types, rows = None, []
    for line in open(os.path.join(ZONES, "client", "dbc", table + ".txt"), encoding="utf-8"):
        parts = line.rstrip("\n").split("\t")
        if parts[0] == "types":
            types = parts[1]
        elif parts[0] == "put":
            rows.append([p.replace("\\\\", "\\") for p in parts[1:]])
    return types, rows


def server_data(tools, conv, server_dbc, work, out):
    """The world server's data for the maps: AzerothCore's own tools over a stand-in game that has
    the maps (and their models) and a Map table of them alone."""
    game = os.path.join(work, "game", "Data")
    os.makedirs(os.path.join(game, "enUS"), exist_ok=True)
    loose = os.path.join(work, "loose")
    os.makedirs(os.path.join(loose, "DBFilesClient"), exist_ok=True)
    with open(os.path.join(loose, "component.wow-enUS.txt"), "w") as f:
        f.write('<?xml version="1.0"?><componentinfo><component name="WoW" version="12340"/></componentinfo>')
    types, rows = our_rows("Map")
    dbc(os.path.join(loose, "DBFilesClient", "Map.dbc"), rows, types)
    shutil.copyfile(find(server_dbc, "LiquidType.dbc"), os.path.join(loose, "DBFilesClient", "LiquidType.dbc"))
    stock_go = common.Dbc(find(server_dbc, "GameObjectDisplayInfo.dbc"))
    dbc(os.path.join(loose, "DBFilesClient", "GameObjectDisplayInfo.dbc"), [], "i" * stock_go.nfields)
    mpq(os.path.join(game, "enUS", "locale-enUS.MPQ"), loose,
        ["component.wow-enUS.txt", "DBFilesClient\\Map.dbc", "DBFilesClient\\LiquidType.dbc", "DBFilesClient\\GameObjectDisplayInfo.dbc"])
    world = [os.path.relpath(os.path.join(r, n), conv).replace("/", "\\") for r, _, ns in os.walk(conv)
             for n in ns if n.endswith((".adt", ".wdt", ".wdl", ".m2", ".skin", ".wmo"))]
    mpq(os.path.join(game, "common.MPQ"), conv, world)
    data = os.path.join(work, "data")
    os.makedirs(data, exist_ok=True)
    run(os.path.join(tools, "map_extractor"), "-i", os.path.join(work, "game"), "-o", data, "-e", "1", cwd=data,
        stdout=subprocess.DEVNULL)
    run(os.path.join(tools, "vmap4_extractor"), "-d", game + "/", cwd=data, stdout=subprocess.DEVNULL)
    os.makedirs(os.path.join(data, "vmaps"), exist_ok=True)
    run(os.path.join(tools, "vmap4_assembler"), "Buildings", "vmaps", cwd=data, stdout=subprocess.DEVNULL)
    os.makedirs(os.path.join(data, "mmaps"), exist_ok=True)
    shutil.copyfile(os.path.join(tools, "mmaps-config.yaml"), os.path.join(data, "mmaps-config.yaml"))
    for map_id in sorted(common.MAPS):
        run(os.path.join(tools, "mmaps_generator"), map_id, "--config", "mmaps-config.yaml", "--threads", os.cpu_count() or 4,
            "--silent", cwd=data, stdout=subprocess.DEVNULL)
    for part in ("maps", "vmaps", "mmaps"):
        dest = os.path.join(out, part)
        os.makedirs(dest, exist_ok=True)
        for name in sorted(os.listdir(os.path.join(data, part))):
            if name == "temp_gameobject_models":
                continue           # (the game's objects' models: none of these maps' yet)
            shutil.copyfile(os.path.join(data, part, name), os.path.join(dest, name))
    counts = {p: len(os.listdir(os.path.join(out, p))) for p in ("maps", "vmaps", "mmaps")}
    assert counts["maps"] >= sum(1 for _ in common.MAPS), counts
    for map_id in common.MAPS:
        assert os.path.exists(os.path.join(out, "mmaps", f"{map_id:03d}.mmap")), map_id
    print(f"server data: {counts}")


def find(folder, name):
    for f in os.listdir(folder):
        if f.lower() == name.lower():
            return os.path.join(folder, f)
    raise FileNotFoundError(name)


def mpq(path, root, names):
    """An MPQ of [names] (paths in the game) from root/<path>, with mod-skyborne's MPQ writer."""
    listing = path + ".names"
    with open(listing, "w") as f:
        f.write("\n".join(names) + "\n")
    run(MKMPQ, path, root, listing)
    os.remove(listing)


def dedupe(folder):
    """Files with the same bytes: one kept, the others named in same.txt (path, kept path)."""
    seen, same = {}, []
    for root, _, names in os.walk(folder):
        for name in sorted(names):
            path = os.path.join(root, name)
            digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
            rel = os.path.relpath(path, folder)
            if digest in seen:
                same.append((rel, seen[digest]))
                os.remove(path)
            else:
                seen[digest] = rel
    return same


MKMPQ = None


def main():
    global MKMPQ
    if len(sys.argv) != 6:
        sys.exit(__doc__)
    cache, converter, tools, server_dbc, out = sys.argv[1:]
    converter = converter.split()
    MKMPQ = os.path.join(tools, "zones_mkmpq")
    work = os.path.join(cache, "work")
    shutil.rmtree(work, ignore_errors=True)
    shutil.rmtree(out, ignore_errors=True)
    files = read_files()
    stage, conv = os.path.join(work, "stage"), os.path.join(work, "conv")
    missing = fetch(cache, files, stage)
    listfile = os.path.join(work, "listfile.csv")
    with open(listfile, "w", newline="\n") as f:
        f.write("".join(f"{fdid};{path}\n" for fdid, (path, _) in sorted(files.items())))
    report = convert(converter, stage, conv, listfile)
    single_textures(stage, conv)
    fix_models(conv)
    # Sounds aren't the converter's: they're 3.3.5a's as they are (Ogg Vorbis).
    for fdid, (path, kind) in files.items():
        src = os.path.join(stage, path)
        if kind == "sound" and os.path.exists(src):
            dest = os.path.join(conv, path)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copyfile(src, dest)
    put_aliases(conv, files, read_aliases())
    plain_textures(conv)
    tiles, _ = maps(conv, cache)
    client = os.path.join(out, "client", "files")
    minimap = minimaps(conv, client, tiles)
    server_data(tools, conv, server_dbc, work, os.path.join(out, "server"))
    cameras(conv, os.path.join(out, "server"))
    # The game's files: everything converted (the server's stand-in game made from them, gone).
    for root, _, names in os.walk(conv):
        for name in names:
            src = os.path.join(root, name)
            rel = os.path.relpath(src, conv).lower()
            if rel.startswith("report-"):
                continue
            dest = os.path.join(client, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.move(src, dest)
    with open(os.path.join(out, "client", "minimap.txt"), "w", newline="\n") as f:
        f.write("\n".join(minimap) + "\n")
    for part, folder in (("client", client), ("server", os.path.join(out, "server"))):
        same = dedupe(folder)
        with open(os.path.join(out, part, "same.txt"), "w", newline="\n") as f:
            f.write("".join(f"{a.replace(os.sep, chr(92)) if part == 'client' else a}\t"
                            f"{b.replace(os.sep, chr(92)) if part == 'client' else b}\n" for a, b in same))
    listed = []
    for root, _, names in os.walk(client):
        for name in names:
            listed.append(os.path.relpath(os.path.join(root, name), client).replace(os.sep, "\\"))
    listed += [l.split("\t")[0] for l in open(os.path.join(out, "client", "same.txt")) if l.strip()]
    with open(os.path.join(out, "client", "files.txt"), "w", newline="\n") as f:
        f.write("\n".join(sorted(listed)) + "\n")
    with open(os.path.join(out, "VERSION"), "w") as f:
        json.dump({"build": common.BUILD, "files": len(files), "not_in_build": len(missing), "converted": report}, f)
        f.write("\n")
    shutil.rmtree(work)
    print(f"package: {len(listed)} game files, in {out}")


if __name__ == "__main__":
    main()
