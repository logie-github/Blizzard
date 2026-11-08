"""The ground's and the water's height at a point of a map, read from the server's map files
(the data.zip in warcraft/server-data.env, its maps/ folder) as the core's GridTerrainData reads
them: tools/build_data.py places the races' homes, their people and their things on the ground
with it, and keeps the intros' cameras above it.

    terrain.MAPS = "<the server data's maps folder>"
    terrain.height(x, y)      the ground's height (None where the map has no tile)
    terrain.liquid(x, y)      the water's level (None where there's none)
    terrain.area(x, y)        the AreaTable id of the place (a zone's or one of its areas'; None off the map)

The buildings and docks (WMOs) aren't in these files: on them, a place's height is taken from
someone standing there (a creature of the game's)."""
import functools
import os
import struct

import numpy as np

MAPS = os.environ.get("WOW_SERVER_MAPS", "")
SIZE = 533.3333333           # a tile's width, in yards
RES = 128                    # its cells a side


@functools.lru_cache(maxsize=None)
def tile(mapid, gx, gy):
    path = os.path.join(MAPS, "%03d%02d%02d.map" % (mapid, gx, gy))
    if not os.path.exists(path):
        return None
    d = open(path, "rb").read()
    _, _, _, aoff, _, hoff, _, loff, _, _, _ = struct.unpack_from("<4sII8I", d, 0)
    t = {}
    if aoff:
        _, flags, grid_area = struct.unpack_from("<4sHH", d, aoff)
        t["area"] = grid_area if flags & 1 else np.frombuffer(d, "<u2", 16 * 16, aoff + 8)
    if hoff:
        _, flags, low, high = struct.unpack_from("<4sIff", d, hoff)
        at = hoff + 16
        if flags & 1:
            t["flat"] = low
        elif flags & 2:
            step = (high - low) / 65535
            t["v9"] = np.frombuffer(d, "<u2", 129 * 129, at) * step + low
            at += 129 * 129 * 2
            t["v8"] = np.frombuffer(d, "<u2", 128 * 128, at) * step + low
        elif flags & 4:
            step = (high - low) / 255
            t["v9"] = np.frombuffer(d, "u1", 129 * 129, at) * step + low
            at += 129 * 129
            t["v8"] = np.frombuffer(d, "u1", 128 * 128, at) * step + low
        else:
            t["v9"] = np.frombuffer(d, "<f4", 129 * 129, at).astype(np.float64)
            at += 129 * 129 * 4
            t["v8"] = np.frombuffer(d, "<f4", 128 * 128, at).astype(np.float64)
    if loff:
        _, flags, _, _, ox, oy, w, h, level = struct.unpack_from("<4sBBHBBBBf", d, loff)
        at = loff + 16
        water = dict(level=level, ox=ox, oy=oy, w=w, h=h)
        if not flags & 1:
            at += 512
            water["flags"] = np.frombuffer(d, "u1", 256, at)
            at += 256
        if not flags & 2:
            water["map"] = np.frombuffer(d, "<f4", w * h, at)
        t["liquid"] = water
    return t


def _cell(x, y):
    fx, fy = RES * (32 - x / SIZE), RES * (32 - y / SIZE)
    return int(32 - x / SIZE), int(32 - y / SIZE), fx, fy


def height(x, y, mapid=1):
    gx, gy, fx, fy = _cell(x, y)
    t = tile(mapid, gx, gy)
    if t is None or ("v9" not in t and "flat" not in t):
        return None
    if "flat" in t:
        return float(t["flat"])
    xi, yi = int(fx), int(fy)
    dx, dy = fx - xi, fy - yi
    xi &= RES - 1
    yi &= RES - 1
    v9, v8 = t["v9"], t["v8"]
    h5 = 2 * v8[xi * 128 + yi]
    # (the cell's four corners and its middle make four triangles, as the core reads them)
    if dx + dy < 1:
        if dx > dy:
            h1, h2 = v9[xi * 129 + yi], v9[(xi + 1) * 129 + yi]
            a, b, c = h2 - h1, h5 - h1 - h2, h1
        else:
            h1, h3 = v9[xi * 129 + yi], v9[xi * 129 + yi + 1]
            a, b, c = h5 - h1 - h3, h3 - h1, h1
    else:
        if dx > dy:
            h2, h4 = v9[(xi + 1) * 129 + yi], v9[(xi + 1) * 129 + yi + 1]
            a, b, c = h2 + h4 - h5, h4 - h2, h5 - h4
        else:
            h3, h4 = v9[xi * 129 + yi + 1], v9[(xi + 1) * 129 + yi + 1]
            a, b, c = h4 - h3, h3 + h4 - h5, h5 - h4
    return float(a * dx + b * dy + c)


def area(x, y, mapid=1):
    """The AreaTable id there, as the core's GridTerrainData::getArea reads it."""
    gx, gy, _, _ = _cell(x, y)
    t = tile(mapid, gx, gy)
    if t is None or "area" not in t:
        return None
    a = t["area"]
    if isinstance(a, int):
        return a
    lx, ly = int(16 * (32 - x / SIZE)) & 15, int(16 * (32 - y / SIZE)) & 15
    return int(a[lx * 16 + ly])


def liquid(x, y, mapid=1):
    gx, gy, fx, fy = _cell(x, y)
    t = tile(mapid, gx, gy)
    if t is None or "liquid" not in t:
        return None
    w = t["liquid"]
    xi, yi = int(fx) & (RES - 1), int(fy) & (RES - 1)
    if "flags" in w and not w["flags"][(xi // 8) * 16 + yi // 8]:
        return None
    if "map" not in w:
        return float(w["level"])
    cx, cy = xi - w["oy"], yi - w["ox"]
    if cx < 0 or cx >= w["h"] or cy < 0 or cy >= w["w"]:
        return None
    return float(w["map"][cx * w["w"] + cy])


def surface(x, y, mapid=1):
    """The ground, or the water's top where the water is deeper than the ground (a swimmer's place)."""
    g = height(x, y, mapid)
    w = liquid(x, y, mapid)
    if g is None:
        return w
    return max(g, w) if w is not None else g
