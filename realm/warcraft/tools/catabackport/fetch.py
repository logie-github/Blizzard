"""Stage `fetch`: one unit's game files, by file id, into `<work>/<unit>/stage/<path in the game>`.

The unit's own files are everything the listfile names under world/maps/<dir>/ (not the files 3.3.5a never reads) and its
minimap pictures; then the closure of what those name (models, buildings, textures, skins, animations), read from the files
themselves with the zones' own parsers (zones/files.py: adt_refs, model_refs, plain_twins). Resumable: a file already in the
stage with the size recorded is not fetched again; a missing id (the build lacks it) is recorded, never an error; a source that
stays down raises SourceDown after the files fetched so far are kept (the unit is `deferred`).
"""
import concurrent.futures
import os
import re

from . import source as src, util, zones_adapter

SKIP_MAP_FILES = re.compile(r"(\.pm4|\.h2o|_tex1\.adt|_lod\.adt|_obj1\.adt)$")
MODEL_EXT = (".m2", ".wmo", ".skin", ".anim", ".skel", ".bone", ".phys")
TILE_NAME = re.compile(r"_(\d+)_(\d+)(?:_obj0|_tex0)?\.adt$")


def start_files(m, unit, by_id):
    """{fdid: (path, kind)}: the unit's map files (all tiles, or only the unit's block of rows) and minimaps."""
    d = m["dir"].lower()
    want = {tuple(t) for t in unit["tiles"]} if unit.get("tiles") else None
    out = {}
    for fdid, path in by_id.items():
        if path.startswith(f"world/maps/{d}/"):
            if SKIP_MAP_FILES.search(path):
                continue
            mt = TILE_NAME.search(path)
            if want is not None and mt and (int(mt.group(1)), int(mt.group(2))) not in want:
                continue
            if want is not None and not mt and unit["part"] != 0:
                continue                       # (the WDT and WDL go with the first block)
            out[fdid] = (path, "map")
        elif path.startswith(f"world/minimaps/{d}/"):
            mm = re.match(r"map(\d+)_(\d+)\.blp$", path[len(f"world/minimaps/{d}/"):])
            if mm and (want is None or (int(mm.group(1)), int(mm.group(2))) in want):
                out[fdid] = (path, "minimap")
    return out


def run(source, m, unit, by_id, by_path, work, jobs=8, log=print):
    """Fetches one unit. Returns its state dict (also written to <work>/<unit>/state.json under "fetch")."""
    zf = zones_adapter.load("files")
    base = os.path.join(work, unit["unit"])
    stage = os.path.join(base, "stage")
    sp = os.path.join(base, "state.json")
    state = util.load_json(sp, {})
    prev = state.get("fetch", {})
    if prev.get("done") and prev.get("input_hash") == unit["input_hash"] and all(
            os.path.exists(os.path.join(stage, p)) for p in prev.get("paths", [])):
        log(f"{unit['unit']}: fetch already done ({len(prev['paths'])} files)")
        return prev
    files = start_files(m, unit, by_id)
    seen = set(files)
    todo = list(files)
    missing, sizes = [], {}

    def one(fdid):
        path, _ = files[fdid]
        dest = os.path.join(stage, path)
        if os.path.exists(dest):
            return fdid, open(dest, "rb").read()          # resume: kept from an earlier try
        try:
            data = source.file(fdid)
        except src.Missing:
            return fdid, b""
        util.write_atomic(dest, data)
        return fdid, data

    try:
        with concurrent.futures.ThreadPoolExecutor(jobs) as pool:
            while todo:
                batch, todo = todo, []
                for fdid, data in pool.map(one, batch):
                    path, _ = files[fdid]
                    if not data:
                        missing.append(path)
                        continue
                    sizes[path] = len(data)
                    if path.endswith(".adt"):
                        refs = zf.adt_refs(data, by_path)
                        refs |= zf.plain_twins(refs, by_id, by_path)
                    elif path.endswith((".m2", ".wmo")):
                        refs = zf.model_refs(path, data, by_path)
                    else:
                        refs = set()
                    for r in refs:
                        if r in seen or r not in by_id:
                            continue
                        seen.add(r)
                        files[r] = (by_id[r], "model" if by_id[r].endswith(MODEL_EXT) else "texture")
                        todo.append(r)
    except src.SourceDown as e:
        state["fetch"] = {"done": False, "error": str(e), "fetched": len(sizes), "input_hash": unit["input_hash"]}
        util.dump_json(sp, state)
        raise
    res = {"done": True, "input_hash": unit["input_hash"], "files": len(sizes), "bytes": sum(sizes.values()),
           "missing": sorted(missing), "paths": sorted(sizes), "ids": {p: f for f, (p, _) in files.items() if p in sizes}}
    state["fetch"] = res
    util.dump_json(sp, state)
    log(f"{unit['unit']}: fetched {res['files']} files, {res['bytes'] >> 20} MB, {len(missing)} not in the build")
    return res
