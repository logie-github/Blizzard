"""Stage `plan`: which maps, cut into units a runner can hold, spread over shards.

A unit is a map, or a block of a big map's tile rows (a continent's pack must stay under a release asset's 2 GB and its work
under a runner's disk). Shards are balanced by weight (tiles). The matrix is what the workflow's `fromJSON` takes: at most
256 jobs. Pure functions of the manifest and the options, so a rerun gives the same plan.
"""
import math
import os

from . import util

MAX_JOBS = 256
MAX_TILES_PER_UNIT = 450        # about 1.4 GB packed, 3.2 GB unpacked at the zones package's 3 MB / 7 MB per tile (CATA_BACKPORT.md 2.3)


def select(manifest, spec):
    """spec: `all`, `proof`, or a comma list of map ids, directories (case free) and `group:<name>`. `done_elsewhere` maps
    are only taken when named by id."""
    maps = manifest["maps"]
    spec = (spec or "all").strip()
    if spec == "all":
        return [m for m in maps if m["status"] == "planned"]
    out = []
    for part in [p.strip() for p in spec.split(",") if p.strip()]:
        if part == "proof":
            chosen = [m for m in maps if m["id"] == manifest.get("proof")]
        elif part.startswith("group:"):
            chosen = [m for m in maps if m["group"] == part[6:] and m["status"] == "planned"]
        elif part.isdigit():
            chosen = [m for m in maps if m["id"] == int(part)]
        else:
            chosen = [m for m in maps if m["dir"].lower() == part.lower() or m["new_dir"].lower() == part.lower()]
        if not chosen:
            raise SystemExit(f"plan: nothing matches {part!r}")
        out += chosen
    seen, uniq = set(), []
    for m in out:
        if m["id"] not in seen:
            seen.add(m["id"])
            uniq.append(m)
    return uniq


def units_of(m, max_tiles=MAX_TILES_PER_UNIT):
    """A map as one unit, or several blocks of whole tile rows (the first carries the map's own files: WDT, tables)."""
    tiles = sorted(m["tiles"], key=lambda t: (t[1], t[0]))
    if len(tiles) <= max_tiles:
        return [{"unit": m["new_dir"].lower(), "map": m["id"], "part": 0, "parts": 1, "tiles": None, "weight": m["weight"]}]
    rows = {}
    for x, y in tiles:
        rows.setdefault(y, []).append([x, y])
    blocks, cur = [], []
    for y in sorted(rows):
        if cur and len(cur) + len(rows[y]) > max_tiles:
            blocks.append(cur)
            cur = []
        cur += rows[y]
    if cur:
        blocks.append(cur)
    return [{"unit": f"{m['new_dir'].lower()}-r{k}", "map": m["id"], "part": k, "parts": len(blocks), "tiles": b, "weight": len(b)}
            for k, b in enumerate(blocks)]


def shard_units(units, n):
    """Longest-processing-time first: heaviest unit to the lightest shard; ties by name."""
    load = [0] * n
    for u in sorted(units, key=lambda u: (-u["weight"], u["unit"])):
        i = min(range(n), key=lambda k: (load[k], k))
        u["shard"] = i
        load[i] += u["weight"]
    return load


def make(manifest, maps_spec="all", shards=None, budget_tiles=600, done_hashes=None, max_tiles=MAX_TILES_PER_UNIT):
    """Returns plan {"units": [...], "shards": n, "skipped": [...]}. `done_hashes` {unit: input_hash} of packs already in the
    release: a unit with the same hash is skipped (skip_done)."""
    chosen = select(manifest, maps_spec)
    units, skipped = [], []
    for m in chosen:
        for u in units_of(m, max_tiles):
            u["input_hash"] = util.input_hash(m["input_hash"], u["part"], u["tiles"])
            if done_hashes and done_hashes.get(u["unit"]) == u["input_hash"]:
                skipped.append(u["unit"])
                continue
            units.append(u)
    # A terrain swap is made whole from its base's converted tiles: it runs in its base's shard, after it, and only when the
    # base is one unit (a split continent's swap is not made whole: reported).
    by_map = {m["id"]: m for m in manifest["maps"]}
    names = {u["map"]: u["unit"] for u in units if u["parts"] == 1}
    for u in list(units):
        base = by_map[u["map"]].get("swap_of")
        u["base"] = None
        if base is not None:
            if base in names:
                u["base"] = names[base]
            else:
                skipped.append(f"{u['unit']}: its base map {base} is not in this plan as one unit (split, not selected or done)")
                units.remove(u)
    total = sum(u["weight"] for u in units)
    n = (shards or max(1, min(MAX_JOBS, math.ceil(total / budget_tiles)))) if units else 1
    n = max(1, min(MAX_JOBS, n, len(units) or 1))
    movable = [u for u in units if not u["base"]]
    load = shard_units(movable, n)
    shard_of = {u["unit"]: u["shard"] for u in movable}
    for u in units:
        if u["base"]:
            u["shard"] = shard_of[u["base"]]
            load[u["shard"]] += u["weight"]
    order = lambda u: (u["shard"], 1 if u["base"] else 0, u["unit"])
    return {"units": sorted(units, key=order), "shards": n, "load": load, "skipped": sorted(skipped)}


def matrix(plan):
    inc = []
    for i in range(plan["shards"]):
        mine = [u for u in plan["units"] if u["shard"] == i]
        if mine:
            inc.append({"shard": i, "of": plan["shards"], "units": ",".join(u["unit"] for u in mine),
                        "weight": sum(u["weight"] for u in mine)})
    return {"include": inc}


def for_shard(plan, spec):
    """`i/n` (the units of shard i when the plan has n shards) or `all`."""
    if spec in (None, "", "all"):
        return plan["units"]
    i, n = (int(x) for x in spec.split("/"))
    if n != plan["shards"]:
        raise SystemExit(f"plan has {plan['shards']} shards, not {n}")
    return [u for u in plan["units"] if u["shard"] == i]
