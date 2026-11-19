"""A woman's soft body weighted where it shows: at the bottom of the curve (the user, 18 November 2026: "The jiggle needs
to be at the bottom of the curve on the butt or boob not the nipple").

The native mod's soft body (Native.cpp SoftWatch) moves a bone by a spring, and what is weighted to the bone moves with
it. Until now the bones were the retail skeleton's breast bones, found by a guess at their height (sl_parts.soft_body),
with Blizzard's own weights: the most at the tip. This gives every woman's converted model four bones of its own (the
chest's two under her chest bone, key 53; the seat's two under her pelvis, key 51; no key, no animation: each follows
the bone it hangs on until the spring moves it) and weights them by a map: the most on the lower curve of the chest and
of the seat, a third of it at the tip (the seat's fullest point), fading out above and at the fold.

  soft_weights.py map SHAPES.npz OUT.json     the map (soft_map.json, in the repository) made from the Human's shape field
                                              (body_shapes/shapes.py source): where her shapes differ is where the chest
                                              and seat are; the curve's bottom from her own surface
  soften(model_path)                          a converted model and its 00.skin rewritten; returns what parts.txt says
                                              of it (sl_parts.parts_table: the B and S lines)

The map is a grid over the body texture (the classic layout every converted race shares: m2.py), one for each side of
the body: a vertex takes the weight at its place on the texture, as body_shapes/shapes.py carries the shapes. A vertex
keeps its three heaviest bones beside the new one; a section's bone list takes the new bones (up to 3.3.5's 64)."""
import json
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "body_shapes"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "modules", "mod-allied-races", "tools"))
import refine  # noqa: E402

MAP = os.path.join(HERE, "soft_map.json")
GRID = 128
CHEST_KEY, PELVIS_KEY, HIP_KEYS, KNEE_KEYS = 53, 51, (55, 56), (57, 58)
MAX_BONES = 64
LEAST = 0.05                      # a weight under this is none
# the curve, from under the fold (h below 0) over its bottom (h about 0.45) to the tip or fullest point (h 1) and above
CURVE = [(-0.6, 0.0), (0.0, 0.45), (0.45, 1.0), (1.0, 0.35), (1.6, 0.08), (2.2, 0.0)]
BONES, VERTICES, BONE_COMBOS, TEXTURES, TEX_COMBOS = 0x2C, 0x3C, 0x78, 0x50, 0x80


def step(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def make_map(field_path, out):
    """The map from the Human's shape field: for each side, the chest's and the seat's weight over the body texture."""
    from scipy.spatial import cKDTree
    d = np.load(field_path)
    P, N, UV = d["P"], d["N"], d["uv"]
    s = np.linalg.norm(d["D_Voluptuous"] - d["D_Petite"], axis=1)          # where the shapes differ: the chest and the seat
    waist = 1.235 * P[:, 2].max() / 1.98                                     # (between them nothing differs: the field's own gap)
    hx, hy = np.interp(CURVE[0][0], [0, 1], [0, 1]), None
    doc = {"size": GRID, "curve": CURVE, "sides": []}
    for side in (1, -1):
        mine = P[:, 1] * side >= -1e-3
        entry = {}
        for name in ("chest", "seat"):
            part = mine & ((P[:, 2] > waist) if name == "chest" else (P[:, 2] < waist))
            if name == "seat":
                part &= P[:, 0] < -0.01                                      # the back of her
            reg = part & (s > 0.15 * s[part].max())
            away = P[reg][np.argmax(P[reg, 0] * (1 if name == "chest" else -1))]     # the tip; the seat's fullest point
            under = reg & (N[:, 2] < (-0.3 if name == "chest" else -0.15))           # the fold: where the surface turns down
            fold = float(np.percentile(P[under, 2], 10))
            h = (P[:, 2] - fold) / (away[2] - fold)
            w = np.interp(h, [c[0] for c in CURVE], [c[1] for c in CURVE]) * step(s / s[part].max(), 0.12, 0.5) * part
            if name == "seat":
                w *= step(-P[:, 0], 0.01, 0.05)
            # onto the grid: each cell from the Human's vertices near it on the texture (none near: nothing)
            tree = cKDTree(UV[mine])
            c = (np.stack(np.meshgrid(np.arange(GRID), np.arange(GRID)), -1).reshape(-1, 2) + 0.5) / GRID
            dist, j = tree.query(c, k=4)
            wt = 1.0 / (dist * dist + 1e-9)
            g = (w[mine][j] * wt).sum(1) / wt.sum(1) * np.clip(2 - dist[:, 0] / 0.012, 0, 1)
            cells = np.where(g > LEAST / 2)[0]
            entry[name] = {"fold": round(fold, 4), "away": [round(float(x), 4) for x in away],
                           "cells": [[int(i), int(round(g[i] * 255))] for i in cells]}
            print("%s %s: fold %.3f, tip %s, %d vertices weighted, %d cells" % ("left" if side > 0 else "right", name, fold, np.round(away, 3).tolist(), int((w > LEAST).sum()), len(cells)))
        doc["sides"].append(entry)
    with open(out, "w") as f:
        json.dump(doc, f, separators=(",", ":"))


class Map:
    def __init__(self, path=MAP):
        doc = json.load(open(path))
        self.size = doc["size"]
        self.grid = np.zeros((2, 2, self.size * self.size))
        for s, side in enumerate(doc["sides"]):
            for r, name in enumerate(("chest", "seat")):
                for i, v in side[name]["cells"]:
                    self.grid[s, r, i] = v / 255.0
        self.grid = self.grid.reshape(2, 2, self.size, self.size)

    def at(self, uv, y):
        """(n x 4) weights of vertices at [uv] on the texture and [y] (their side): chest left, right, seat left, right."""
        n = self.size
        x = np.clip(uv[:, 0] * n - 0.5, 0, n - 1.001)
        v = np.clip(uv[:, 1] * n - 0.5, 0, n - 1.001)
        x0, v0 = x.astype(int), v.astype(int)
        fx, fv = x - x0, v - v0
        out = np.zeros((len(uv), 4))
        for s, sel in enumerate((y >= 0, y < 0)):
            for r in range(2):
                g = self.grid[s, r]
                w = g[v0, x0] * (1 - fx) * (1 - fv) + g[v0, x0 + 1] * fx * (1 - fv) + g[v0 + 1, x0] * (1 - fx) * fv + g[v0 + 1, x0 + 1] * fx * fv
                out[:, r * 2 + s] = np.where(sel, w, 0.0)
        return out


def arr(m, off):
    return struct.unpack_from("<II", m, off)


def soften(model_path, soft_map=None, log=lambda *a: None):
    """[model_path] (a woman's converted .m2, its 00.skin beside it) given its soft bones and their weights. Returns
    {"count": bones, "parent": the chest bone, "bones": [[bone, pivot x, y, z, []], x2], "seat": {"parent": the pelvis,
    "bones": [...]}} (the chest's as sl_parts.soft_body returned the retail breast bones), or None for a model without a
    chest and pelvis key bone, or on which the map finds no chest."""
    soft_map = soft_map or Map()
    m = bytearray(open(model_path, "rb").read())
    skin_path = model_path[:-3] + "00.skin"
    skb = open(skin_path, "rb").read()
    nb, ob = arr(m, BONES)
    bones = [bytes(m[ob + i * 88: ob + (i + 1) * 88]) for i in range(nb)]
    key = [struct.unpack_from("<i", b, 0)[0] for b in bones]
    pivot = [struct.unpack_from("<3f", b, 76) for b in bones]
    if CHEST_KEY not in key or PELVIS_KEY not in key:
        return None
    chest, pelvis = key.index(CHEST_KEY), key.index(PELVIS_KEY)
    knee = min((pivot[key.index(k)][2] for k in KNEE_KEYS if k in key), default=0.0)
    nv, ov = arr(m, VERTICES)
    rec = np.frombuffer(bytes(m[ov:ov + nv * 48]), np.uint8).reshape(nv, 48).copy()
    P = rec[:, 0:12].copy().view("<f4").reshape(nv, 3).astype(np.float64)
    UV = rec[:, 32:40].copy().view("<f4").reshape(nv, 2).astype(np.float64)
    verts, idx, props, secs, batches, bn, mx = refine.read_skin(skb)
    # the vertices the body's texture draws (the body, and what is worn over it with its texture)
    nt, ot = arr(m, TEXTURES)
    types = [struct.unpack_from("<I", m, ot + i * 16)[0] for i in range(nt)]
    nc, oc = arr(m, TEX_COMBOS)
    combos = struct.unpack_from("<%dH" % nc, m, oc)
    drawn = np.zeros(nv, bool)
    for i in range(bn):
        b = struct.unpack_from("<BbHHHHHHHHHHH", batches, i * 24)
        if b[9] < nc and combos[b[9]] < nt and types[combos[b[9]]] == 1:
            s = secs[b[3]]
            drawn[verts[s[2]:s[2] + s[3]]] = True
    W = soft_map.at(UV, P[:, 1]) * drawn[:, None]
    W[:, :2] *= (P[:, 2] > pivot[pelvis][2])[:, None]                       # the chest is above her pelvis,
    W[:, 2:] *= ((P[:, 2] < pivot[chest][2]) & (P[:, 2] > knee))[:, None]   # the seat between her knees and her chest
    # and behind her hip joints (the texture's seam at the leg's crease lets a little of the map onto her front)
    hips = [pivot[key.index(k)] for k in HIP_KEYS if k in key]
    if hips:
        hx = sum(h[0] for h in hips) / len(hips)
        leg = max(0.05, sum(h[2] for h in hips) / len(hips) - knee)
        W[:, 2:] *= step((hx - P[:, 0]) / leg, -0.04, 0.10)[:, None]
    W[W < LEAST] = 0
    region = W.argmax(1)
    w = W.max(1)
    kept = [r for r in range(4) if (region[w > 0] == r).sum() >= 6 and w[(region == r)].max() >= 0.3]
    if 0 not in kept or 1 not in kept:
        return None
    w[~np.isin(region, kept)] = 0
    new_bone = {r: nb + i for i, r in enumerate(kept)}
    # a section whose bone list has no room for a vertex's new bone: that vertex stays as it was
    need = {}
    for si, s in enumerate(secs):
        ks = np.arange(s[2], s[2] + s[3])
        mine = ks[w[verts[ks]] > 0]
        need[si] = sorted({new_bone[int(region[verts[k]])] for k in mine})
        if s[6] + len(need[si]) > MAX_BONES:
            log("section %d (geoset %d) has %d bones: its vertices stay as they are" % (si, s[0], s[6]))
            w[verts[mine]] = 0
            need[si] = []
    centre = {}
    for r in kept:
        sel = (region == r) & (w > 0)
        if not sel.any():
            return None
        centre[r] = (P[sel] * w[sel, None]).sum(0) / w[sel].sum()
    # the vertices: the new bone's weight, the three heaviest of before sharing the rest
    for v in np.where(w > 0)[0]:
        ws = int(round(255 * w[v]))
        old = sorted(((int(rec[v, 12 + j]), int(rec[v, 16 + j])) for j in range(4) if rec[v, 12 + j]), reverse=True)[:3]
        rest = 255 - ws
        total = sum(x for x, _ in old)
        if not old or total == 0 or rest <= 0:
            share = []
            ws = 255
        else:
            raw = [x * rest / total for x, _ in old]
            share = [int(x) for x in raw]
            for j in sorted(range(len(raw)), key=lambda j: raw[j] - share[j], reverse=True)[:rest - sum(share)]:
                share[j] += 1
        out = [(x, b) for x, (_, b) in zip(share, old) if x] + [(ws, new_bone[int(region[v])])]
        out += [(0, 0)] * (4 - len(out))
        rec[v, 12:16] = [x for x, _ in out]
        rec[v, 16:20] = [b for _, b in out]
    # the bones: after the model's own, each hung on the chest or the pelvis, still (a bone's tracks with no keys)
    def keys_of(b, at):
        _, _, tc, to, _, _ = struct.unpack_from("<hhIIII", b, at)
        return sum(struct.unpack_from("<I", m, to + i * 8)[0] for i in range(tc)) if to + tc * 8 <= len(m) else 1
    still = next((b[16:76] for b in bones if all(keys_of(b, 16 + 20 * t) == 0 for t in range(3))), None)
    if still is None:
        still = struct.pack("<hhIIII", 0, -1, 0, 0, 0, 0) * 3
    for r in kept:
        bones.append(struct.pack("<iIhHI", -1, 0, chest if r < 2 else pelvis, 0, 0) + still + struct.pack("<3f", *centre[r]))
    # the skin: each section's bone list with its new bones (a list of its own after the model's), its vertices' slots
    ncb, ocb = arr(m, BONE_COMBOS)
    bone_combos = list(struct.unpack_from("<%dH" % ncb, m, ocb))
    props = props.copy()
    for si, s in enumerate(secs):
        if not need[si]:
            continue
        palette = bone_combos[s[7]:s[7] + s[6]] + need[si]
        s[7], s[6] = len(bone_combos), len(palette)
        bone_combos += palette
        for k in range(s[2], s[2] + s[3]):
            v = verts[k]
            if w[v] > 0:
                props[k] = [palette.index(int(rec[v, 16 + j])) if rec[v, 12 + j] else 0 for j in range(4)]
                s[8] = max(s[8], int((rec[v, 12:16] > 0).sum()))
    while len(m) % 16:
        m.append(0)
    struct.pack_into("<II", m, BONES, len(bones), len(m))
    m += b"".join(bones)
    while len(m) % 16:
        m.append(0)
    struct.pack_into("<II", m, BONE_COMBOS, len(bone_combos), len(m))
    m += struct.pack("<%dH" % len(bone_combos), *bone_combos)
    m[ov:ov + nv * 48] = rec.tobytes()
    with open(model_path, "wb") as f:
        f.write(bytes(m))
    with open(skin_path, "wb") as f:
        f.write(refine.write_skin(verts, idx, props, secs, batches, bn, max(mx, max(s[6] for s in secs))))
    side = lambda r: [new_bone[r]] + [round(float(x), 5) for x in centre[r]] + [[]]
    out = {"count": len(bones), "parent": chest, "bones": [side(0), side(1)]}
    if 2 in kept and 3 in kept:
        out["seat"] = {"parent": pelvis, "bones": [side(2), side(3)]}
    log("%s: soft bones %s; %d vertices weighted (chest %d, seat %d)" % (os.path.basename(model_path), [new_bone[r] for r in kept], int((w > 0).sum()),
        int(((w > 0) & (region < 2)).sum()), int(((w > 0) & (region >= 2)).sum())))
    return out


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "map":
        make_map(sys.argv[2], sys.argv[3])
    else:
        raise SystemExit(__doc__)
