"""Stage `convert`: one unit's staged Cataclysm files made for 3.3.5a.

`wotlkconv` (the Converter, at the pinned commit) over each top-level folder of the stage as the zones package does
(zones/package.py `convert`: world files at most 512 pixels, the interface's as they are), sounds copied as they are; then the
zones' own fixes, called read-only from package.py (`single_textures`, `fix_models`, `plain_textures`, `fix_wdt`, `fix_liquids`);
then what is generic here: the WDT's tile set checked against the tiles written, terrain swaps made whole from their base, the
minimap pictures and their index. Output: <work>/<unit>/conv/ (the game's files) and <work>/<unit>/out/client/ (the pack's half).
"""
import json
import os
import re
import shutil
import struct
import subprocess
import sys

from . import util, zones_adapter

WORLD_TEXTURES = 512


def converter_command(converter_src=None, command=None):
    """(argv prefix, env): `--converter "cmd ..."` as given, or `python3 -m wotlkconv` over the Converter's src folder."""
    env = dict(os.environ)
    if command:
        return command.split(), env
    if converter_src:
        env["PYTHONPATH"] = converter_src + os.pathsep + env.get("PYTHONPATH", "")
    return [sys.executable, "-m", "wotlkconv"], env


def run_converter(cmd, env, src, out, listfile, size, jobs, report, log):
    argv = cmd + ["convert", src, "-o", out, "--listfile", listfile, "--max-texture-size", str(size), "-j", str(jobs), "-q",
                  "--report", report]
    log("+ " + " ".join(argv))
    p = subprocess.run(argv, env=env, capture_output=True, text=True)
    acc = {}
    try:
        acc = json.load(open(report))["accounting"]
    except (OSError, ValueError, KeyError):
        pass
    return p.returncode, acc, (p.stdout + p.stderr)[-2000:]


def tile_files(conv, d):
    """{(x, y): path} of a map directory's converted tiles."""
    folder = os.path.join(conv, "world", "maps", d.lower())
    out = {}
    if os.path.isdir(folder):
        for name in os.listdir(folder):
            m = re.match(r".*_(\d+)_(\d+)\.adt$", name)
            if m:
                out[(int(m.group(1)), int(m.group(2)))] = os.path.join(folder, name)
    return out


def remap_adt_areas(path, mapping):
    """The area id of each of a tile's 256 chunks (MCNK header, offset 52) through `mapping` {old: new}: the tile's chunks name
    AreaTable rows, and the rows of a map made over beside 3.3.5a's own have new ids (ids.alloc_area_ids). Returns how many
    chunks changed."""
    data = bytearray(open(path, "rb").read())
    i, changed = 0, 0
    while i + 8 <= len(data):
        magic = bytes(data[i:i + 4])
        size = struct.unpack_from("<I", data, i + 4)[0]
        if magic == b"KNCM" and size >= 56:
            old = struct.unpack_from("<I", data, i + 8 + 52)[0]
            new = mapping.get(old, old)
            if new != old:
                struct.pack_into("<I", data, i + 8 + 52, new)
                changed += 1
        i += 8 + size
    if changed:
        with open(path, "wb") as f:
            f.write(data)
    return changed


def finish_map(conv, m, liquids, base_conv=None, base_dir=None, areas=None):
    """The unit's map made right: liquids 3.3.5a has, the WDT's flags, its tile set equal to the tiles written (a mismatch is
    returned as a problem, not asserted), and a terrain swap made whole from its base's tiles. Returns (tiles, problems)."""
    pkg = zones_adapter.load("package")
    d = m["dir"].lower()
    problems = []
    folder = os.path.join(conv, "world", "maps", d)
    wdt = os.path.join(folder, d + ".wdt")
    tiles = tile_files(conv, d)
    for path in tiles.values():
        pkg.fix_liquids(path, liquids)
        if areas:
            remap_adt_areas(path, areas)
    if os.path.exists(wdt):
        pkg.fix_wdt(wdt)
    else:
        problems.append("no WDT was converted")
    if base_conv:                                         # a terrain swap: its base's tiles where it has none of its own
        base = tile_files(base_conv, base_dir)
        for xy, path in sorted(base.items()):
            if xy not in tiles:
                dest = os.path.join(folder, f"{d}_{xy[0]}_{xy[1]}.adt")
                os.makedirs(folder, exist_ok=True)
                shutil.copyfile(path, dest)
                tiles[xy] = dest
        if os.path.exists(wdt):
            pkg.set_wdt_tiles(wdt, set(tiles))
        wdl = os.path.join(folder, d + ".wdl")
        base_wdl = os.path.join(base_conv, "world", "maps", base_dir.lower(), base_dir.lower() + ".wdl")
        if not os.path.exists(wdl) and os.path.exists(base_wdl):
            shutil.copyfile(base_wdl, wdl)
    elif os.path.exists(wdt):
        in_wdt = pkg.wdt_tiles(wdt)
        wanted = set(tiles)
        if wanted != in_wdt:
            problems.append(f"WDT lists {len(in_wdt)} tiles, {len(wanted)} written: {len(in_wdt - wanted)} tiles missing, "
                            f"{len(wanted - in_wdt)} extra")
    return tiles, problems


def minimaps(conv, files_dir, tiles, new_dir, dir_for):
    """The minimap pictures under textures\\minimap and the index's lines (as zones/package.py `minimaps`); `dir_for` is the
    directory whose pictures a tile uses (the swap's own, or its base's)."""
    lines = [f"dir: {new_dir}"]
    root = os.path.join(conv, "world", "minimaps")
    for (x, y) in sorted(tiles):
        for of in dir_for:
            src = os.path.join(root, of.lower(), f"map{x:02d}_{y:02d}.blp")
            if os.path.exists(src):
                name = f"cataclysm_{of.lower()}_map{x:02d}_{y:02d}.blp"
                dest = os.path.join(files_dir, "textures", "minimap", name)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                if not os.path.exists(dest):
                    shutil.copyfile(src, dest)
                lines.append(f"{new_dir}\\map{x:02d}_{y:02d}.blp\t{name}")
                break
    shutil.rmtree(root, ignore_errors=True)
    return lines


def run(m, unit, work, listfile, cmd, env, liquids, jobs=4, base_unit=None, base_map=None, log=print, areas=None):
    """Converts one unit. Returns {"status": ok|partial|failed, "problems": [...], "accounting": {...}}."""
    pkg = zones_adapter.load("package")
    base = os.path.join(work, unit["unit"])
    stage, conv = os.path.join(base, "stage"), os.path.join(base, "conv")
    out_client = os.path.join(base, "out", "client", "files")
    shutil.rmtree(conv, ignore_errors=True)
    shutil.rmtree(os.path.join(base, "out"), ignore_errors=True)
    os.makedirs(conv)
    problems, accounting = [], {}
    parts = sorted(p for p in os.listdir(stage) if p != "sound" and os.path.isdir(os.path.join(stage, p)))
    for part in parts:
        size = 4096 if part == "interface" else WORLD_TEXTURES
        rep = os.path.join(conv, f"report-{part}.json")
        code, acc, tail = run_converter(cmd, env, os.path.join(stage, part), os.path.join(conv, part), listfile, size, jobs, rep, log)
        accounting[part] = acc
        if code:
            problems.append(f"the Converter failed on {part} (exit {code}): {tail[-300:]}")
        if os.path.exists(rep):
            os.remove(rep)
    sounds = os.path.join(stage, "sound")
    if os.path.isdir(sounds):
        shutil.copytree(sounds, os.path.join(conv, "sound"), dirs_exist_ok=True)
    pkg.single_textures(stage, conv)
    pkg.fix_models(conv)
    pkg.plain_textures(conv)
    base_conv = os.path.join(work, base_unit, "conv") if base_unit else None
    tiles, tp = finish_map(conv, m, liquids, base_conv, base_map["dir"] if base_map else None, areas)
    problems += tp
    dir_for = [m["dir"]] + ([base_map["dir"]] if base_map else [])
    mm_lines = minimaps(conv, out_client, tiles, m["new_dir"], dir_for)
    os.makedirs(os.path.join(base, "out", "client"), exist_ok=True)
    util.write_atomic(os.path.join(base, "out", "client", "minimap.txt"), "\n".join(mm_lines) + "\n")
    for root, _, names in os.walk(conv):
        for name in names:
            src = os.path.join(root, name)
            rel = os.path.relpath(src, conv).lower()
            if rel.startswith("report-"):
                continue
            dest = os.path.join(out_client, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copyfile(src, dest)        # (conv stays: a terrain swap of this map and the extractors read it)
    status = "ok" if not problems else ("failed" if not tiles else "partial")
    return {"status": status, "problems": problems, "accounting": accounting, "tiles": len(tiles)}
