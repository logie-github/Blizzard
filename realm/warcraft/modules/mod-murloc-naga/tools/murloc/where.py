#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""What's at a spot of the world, for writing a chapter (tools/murloc/SCHEMA.md): the ground's height,
the water's (and so whether someone there stands on land, wades or swims), and the game's creatures
and objects nearest it (their names, levels and places: a place on the ground beside them is a safe
one to put someone).

    WOW_SERVER_MAPS=<maps> WOW_WORLD_SQL=<db_world> python3 tools/murloc/where.py MAP X Y [RADIUS]
    ... python3 tools/murloc/where.py find NAME [MAP]     the game's creatures by name: their places

MAPS: the server data's maps folder; WOW_WORLD_SQL: the core's data/sql/base/db_world."""
import math
import os
import pickle
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "mod-allied-races", "tools"))
import sqlrows  # noqa: E402
import terrain  # noqa: E402

WORLD = os.environ.get("WOW_WORLD_SQL", "")
CACHE = os.path.join(os.environ.get("TMPDIR", "/tmp"), "murloc_where.pickle")


def world():
    if os.path.exists(CACHE):
        with open(CACHE, "rb") as f:
            return pickle.load(f)
    names = {int(r["entry"]): (r["name"], r["subname"] or "", int(r["minlevel"]), int(r["maxlevel"]), int(r["faction"]))
             for r in sqlrows.table(os.path.join(WORLD, "creature_template.sql"))[1]}
    spawns = [(int(r["id1"]), int(r["map"]), float(r["position_x"]), float(r["position_y"]), float(r["position_z"]))
              for r in sqlrows.table(os.path.join(WORLD, "creature.sql"))[1]]
    gonames = {int(r["entry"]): r["name"] for r in sqlrows.table(os.path.join(WORLD, "gameobject_template.sql"))[1]}
    gos = [(int(r["id"]), int(r["map"]), float(r["position_x"]), float(r["position_y"]), float(r["position_z"]))
           for r in sqlrows.table(os.path.join(WORLD, "gameobject.sql"))[1]]
    data = (names, spawns, gonames, gos)
    with open(CACHE, "wb") as f:
        pickle.dump(data, f)
    return data


def main():
    terrain.MAPS = os.environ.get("WOW_SERVER_MAPS", terrain.MAPS)
    names, spawns, gonames, gos = world()
    if sys.argv[1] == "find":
        want = sys.argv[2].lower()
        m = int(sys.argv[3]) if len(sys.argv) > 3 else None
        for entry, (name, sub, lo, hi, fac) in names.items():
            if want in name.lower():
                pts = [s for s in spawns if s[0] == entry and (m is None or s[1] == m)]
                if pts:
                    cx = sum(p[2] for p in pts) / len(pts)
                    cy = sum(p[3] for p in pts) / len(pts)
                    print(f"{entry} {name} <{sub}> level {lo}-{hi} faction {fac}: {len(pts)} on map {pts[0][1]}, "
                          f"around ({cx:.0f}, {cy:.0f}); e.g. " + ", ".join(f"({p[2]:.1f}, {p[3]:.1f}, {p[4]:.1f})" for p in pts[:4]))
        return
    m, x, y = int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])
    r = float(sys.argv[4]) if len(sys.argv) > 4 else 40.0
    g = terrain.height(x, y, m)
    w = terrain.liquid(x, y, m)
    if g is None:
        print("no map tile here")
    else:
        kind = "land" if w is None or w < g else ("shallows (wading)" if w - g < 1.6 else f"water {w - g:.1f} yd deep")
        print(f"ground {g:.2f}" + (f", water at {w:.2f}" if w is not None else "") + f": {kind}")
    near = sorted(((math.hypot(s[2] - x, s[3] - y), s) for s in spawns if s[1] == m and abs(s[2] - x) < r and abs(s[3] - y) < r),
                  key=lambda t: t[0])[:15]
    for d, s in near:
        name, sub, lo, hi, fac = names.get(s[0], ("?", "", 0, 0, 0))
        print(f"  {d:5.1f} yd  {s[0]} {name}" + (f" <{sub}>" if sub else "") + f" (level {lo}-{hi}, faction {fac}) at ({s[2]:.1f}, {s[3]:.1f}, {s[4]:.1f})")
    near = sorted(((math.hypot(o[2] - x, o[3] - y), o) for o in gos if o[1] == m and abs(o[2] - x) < r and abs(o[3] - y) < r),
                  key=lambda t: t[0])[:8]
    for d, o in near:
        print(f"  {d:5.1f} yd  object {o[0]} {gonames.get(o[0], '?')} at ({o[2]:.1f}, {o[3]:.1f}, {o[4]:.1f})")


if __name__ == "__main__":
    main()
