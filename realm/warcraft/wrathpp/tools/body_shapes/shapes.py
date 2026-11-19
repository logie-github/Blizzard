"""The Human woman's body shapes carried onto every other race's woman, without the viewer: usage

  shapes.py source HUMAN_V1.zip LOOKS_DIR REFINED_HUMAN_DIR OUT.npz
  shapes.py carry SOURCE.npz HUMAN_V1.zip LOOKS_DIR RACES.json OUT_V1.zip [Race ...]

source: the shapes as a field over the Human's body: for every vertex of her refined model that the body's texture
draws, where it is on the texture (the classic layout every converted race shares: m2.py), where it is on her, and
what each shape (Petite, Curvy, Voluptuous) does to it: the move, and the change of its texture coordinates.
HUMAN_V1.zip: the format 1 zip (pack.py) of her shapes, made for the looks given (rebase.py); REFINED_HUMAN_DIR: her
refined model before the shapes (refine.py's, Character/Human/Female/HumanFemale.m2), whose vertices the zip's
blocks are in the order of. The field is yours as the zip is: never in the repository.

carry: for each race of RACES.json (or those named; the Human's own entry is copied from HUMAN_V1.zip), a format 1
entry in OUT_V1.zip, which pack2.py takes as it takes the Human's:
  - by region: a vertex of her body takes the field of the Human's body at the same place of the body texture (the 4
    nearest of the Human's vertices there, on the same side of the body; nothing where the Human has no vertex near);
  - by proportion: the move is turned and scaled as her body is against the Human's around that place (the similarity
    that best lays the Human's vertices within about 7 cm on hers: a chest that leans or is broader takes the shape
    leaning and broader);
  - her model is refined first where the shapes move it most (refine.py: the chest and seat finer, the worn gear's
    pieces giving way: as many triangles as the skin has room for), and once more where a shape bends the surface
    sharply; the field is taken again on the refined
    model, smoothed a little over her own mesh, and written as pack.py's vertex blocks (other pieces at the same places
    moved with the body, normals turned by how the surface turned, as presets.py does).
Each race is to be looked at (render.py) before its package goes anywhere: the field is the Human's sculpted shapes
(MakeHuman's CC0 targets, carried onto her by the viewer of 14 November 2026); what this adds is only where they land."""
import hashlib
import json
import os
import struct
import sys
import zipfile

import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "modules", "mod-allied-races", "tools"))
import m2 as M2  # noqa: E402
import refine  # noqa: E402

PRESETS = ["Petite", "Curvy", "Voluptuous"]
NEAR_UV = 0.02          # a Human vertex this near on the texture, or the field fades (gone at twice this)
SIGMA = 0.07            # the neighbourhood the proportion is taken over, metres on the Human
PICK = 0.004            # refine where a shape moves a vertex 4 mm (x her scale), or more where the skin has less room
SHARP = 20.0            # degrees between two triangles a shape may bend them to before they are split


def sha(b):
    return hashlib.sha256(b).hexdigest()


def struct_sha(m2b):
    n, o = struct.unpack_from("<II", m2b, 60)
    a = np.frombuffer(bytearray(m2b), np.uint8)
    a[o:o + n * 48].reshape(n, 48)[:, :12] = 0
    return sha(a.tobytes())


def records(m2b):
    n, o = struct.unpack_from("<II", m2b, 60)
    return np.frombuffer(m2b, np.uint8, n * 48, o).reshape(n, 48).copy()


def f32(rec, a, b):
    return rec[:, a:b].copy().view("<f4").reshape(len(rec), (b - a) // 4).astype(np.float64)


def body_of(skb, ids):
    """(the body's vertices, its triangles, every triangle of the skin) as model vertex ids"""
    verts, idx, _, secs, _, _, _ = refine.read_skin(skb)
    tri = lambda s: verts[idx[refine.section_slice(idx, s)]].reshape(-1, 3)
    body = np.concatenate([tri(s) for s in secs if s[0] in ids])
    return np.unique(body), body, np.concatenate([tri(s) for s in secs])


def make_source(v1, looks, refined_dir, out):
    z = zipfile.ZipFile(v1)
    entry = next(m for m in json.loads(z.read("wrathpp-body.json"))["models"] if m["race"] == "Human")
    rel = os.path.join(refined_dir, "Character", "Human", "Female", "HumanFemale")
    base = records(open(rel + ".m2", "rb").read())
    skin = z.read(entry["skin_file"])
    races = json.load(open(os.path.join(HERE, "races.json")))
    mv, _, _ = body_of(skin, set(races["Human"]["body"]))
    P0, N0, UV0 = f32(base, 0, 12), f32(base, 20, 32), f32(base, 32, 40)
    data = {"uv": UV0[mv], "P": P0[mv], "N": N0[mv]}
    for p in PRESETS:
        blk = np.frombuffer(z.read(entry["blocks"][p]["file"]), np.uint8).reshape(-1, 48)
        if len(blk) != len(base):
            raise SystemExit("the refined model has %d vertices, the zip's %s block %d" % (len(base), p, len(blk)))
        data["D_" + p] = f32(blk, 0, 12)[mv] - P0[mv]
        data["dUV_" + p] = f32(blk, 32, 40)[mv] - UV0[mv]
        print(p, "moves %d of %d body vertices, the most %.1f cm; %d texture coordinates" % (
            (np.linalg.norm(data["D_" + p], axis=1) > 1e-5).sum(), len(mv), np.linalg.norm(data["D_" + p], axis=1).max() * 100,
            (np.abs(data["dUV_" + p]).max(1) > 1e-6).sum()))
    np.savez_compressed(out, **data)


class Field:
    """The Human's shapes, asked by a place on the body texture and a side of the body."""

    def __init__(self, path):
        d = np.load(path)
        self.P, self.uv = d["P"], d["uv"]
        self.D = np.stack([d["D_" + p] for p in PRESETS], 1)                    # n x 3 presets x 3
        self.dUV = np.stack([d["dUV_" + p] for p in PRESETS], 1)
        self.side = [np.where(self.P[:, 1] >= -1e-3)[0], np.where(self.P[:, 1] <= 1e-3)[0]]     # her left, her right
        self.tree = [cKDTree(self.uv[s]) for s in self.side]

    def at(self, uv, y):
        """For places [uv] on the texture of vertices at [y] (their side): (the Human's place there, the moves, the
        texture coordinates' changes, how near the Human's nearest vertex is on the texture)."""
        n = len(uv)
        H, D, dUV, near = np.zeros((n, 3)), np.zeros((n, 3, 3)), np.zeros((n, 3, 2)), np.full(n, 9.0)
        for k, sel in enumerate((y >= 0, y < 0)):
            if not sel.any():
                continue
            d, j = self.tree[k].query(uv[sel], k=4)
            w = 1.0 / (d * d + 1e-10)
            w /= w.sum(1, keepdims=True)
            src = self.side[k][j]
            H[sel] = (self.P[src] * w[..., None]).sum(1)
            D[sel] = (self.D[src] * w[..., None, None]).sum(1)
            dUV[sel] = (self.dUV[src] * w[..., None, None]).sum(1)
            near[sel] = d[:, 0]
        return H, D, dUV, near


def similarities(H, P, at, sigma):
    """For each of the Human's places [at], the rotation and scale that best lay the pairs Human [H] -> her [P] near it."""
    R, S = np.zeros((len(at), 3, 3)), np.zeros(len(at))
    for a in range(0, len(at), 256):
        q = at[a:a + 256]
        w = np.exp(-((q[:, None, :] - H[None, :, :]) ** 2).sum(2) / (2 * sigma * sigma))
        w /= w.sum(1, keepdims=True)
        mh, mp = w @ H, w @ P
        dh, dp = H[None] - mh[:, None], P[None] - mp[:, None]
        C = np.einsum("qn,qni,qnj->qij", w, dp, dh)
        U, sv, Vt = np.linalg.svd(C)
        det = np.sign(np.linalg.det(U @ Vt))
        fix = np.stack([np.ones_like(det), np.ones_like(det), det], 1)
        R[a:a + 256] = np.einsum("qij,qj,qjk->qik", U, fix, Vt)
        S[a:a + 256] = (sv * fix).sum(1) / np.einsum("qn,qni,qni->q", w, dh, dh)
    return R, S


def carried(field, rec, mv, tris, k):
    """What each shape does to her body's vertices [mv]: (moves n x 3 presets x 3, texture changes, weights)."""
    P, UV = f32(rec, 0, 12), f32(rec, 32, 40)
    H, D, dUV, near = field.at(UV[mv], P[mv, 1])
    fade = np.clip(2 - near / NEAR_UV, 0, 1)
    ok = near < NEAR_UV
    # pairs that agree with her whole body laid on the Human's (a place of the texture that is another part on her: out)
    R0, S0 = similarities(H[ok], P[mv][ok], H[ok].mean(0)[None], 10.0)
    mh, mp = H[ok].mean(0), P[mv][ok].mean(0)
    res = np.linalg.norm((H - mh) @ R0[0].T * S0[0] + mp - P[mv], axis=1)
    good = ok & (res < 0.12 * max(k, 0.5) + 2.5 * np.median(res[ok]))
    fade = fade * (res < 0.2 * max(k, 0.5) + 4 * np.median(res[ok]))
    moved = (np.abs(D).max((1, 2)) > 1e-6) & (fade > 0)
    out, outuv = np.zeros((len(mv), 3, 3)), np.zeros((len(mv), 3, 2))
    if moved.any():
        R, S = similarities(H[good], P[mv][good], H[moved], SIGMA)
        out[moved] = np.einsum("n,nij,npj->npi", S, R, D[moved]) * fade[moved, None, None]
        outuv[moved] = dUV[moved] * fade[moved, None, None]
    # smoothed a little over her own mesh (welded by place), so the field has no step where her vertices lie otherwise
    local = {int(g): i for i, g in enumerate(mv)}
    T = np.array([[local[int(v)] for v in t] for t in tris])
    key = np.round(P[mv], 5)
    _, weld = np.unique(key, axis=0, return_inverse=True)
    weld = weld.ravel()
    e = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]], T[:, [1, 0]], T[:, [2, 1]], T[:, [0, 2]]])
    ea, eb = weld[e[:, 0]], weld[e[:, 1]]
    nw = weld.max() + 1
    cnt = np.bincount(ea, minlength=nw).astype(float)
    flat = out.reshape(len(mv), 9)
    for _ in range(2):
        g = np.zeros((nw, 9))
        np.add.at(g, weld, flat)
        g /= np.maximum(np.bincount(weld, minlength=nw), 1)[:, None]
        s = np.zeros((nw, 9))
        np.add.at(s, ea, g[eb])
        g = np.where(cnt[:, None] > 0, 0.5 * g + 0.5 * s / np.maximum(cnt, 1)[:, None], g)
        flat = g[weld]
    return flat.reshape(len(mv), 3, 3), outuv, {"near": int(ok.sum()), "agree": int(good.sum()), "moved": int(moved.sum()), "scale": float(S0[0])}


def vnormals(P, tris, weld):
    fn = np.cross(P[tris[:, 1]] - P[tris[:, 0]], P[tris[:, 2]] - P[tris[:, 0]])
    acc = np.zeros((weld.max() + 1, 3))
    for j in range(3):
        np.add.at(acc, weld[tris[:, j]], fn)
    n = acc[weld]
    return n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)


def blocks_of(rec, mv, all_tris, D, dUV):
    """Each shape's vertex block (presets.py's rules), and what it did."""
    nv = len(rec)
    P0, N0, UV0 = f32(rec, 0, 12), f32(rec, 20, 32), f32(rec, 32, 40)
    _, weld = np.unique(np.round(P0, 5), axis=0, return_inverse=True)
    weld = weld.ravel()
    G0 = vnormals(P0, all_tris, weld)
    drawn = np.zeros(nv, bool)
    drawn[mv] = True
    others = np.where(~drawn)[0]
    dist, j = cKDTree(P0[mv]).query(P0[others])
    near = (dist < 0.003) & (np.einsum("ij,ij->i", N0[others], N0[mv[j]]) > 0.3)
    out, info = {}, {}
    for p, name in enumerate(PRESETS):
        P = P0.copy()
        P[mv] += D[:, p]
        P[others[near]] += D[j[near], p]
        UV = UV0.copy()
        UV[mv] += dUV[:, p]
        G = vnormals(P, all_tris, weld)
        moved = np.linalg.norm(P - P0, axis=1) > 1e-6
        N = N0.copy()
        N[moved] = N0[moved] + G[moved] - G0[moved]
        N[moved] /= np.linalg.norm(N[moved], axis=1, keepdims=True) + 1e-12
        r = rec.copy()
        r[:, 0:12] = P.astype("<f4").view(np.uint8).reshape(nv, 12)
        r[:, 20:32] = N.astype("<f4").view(np.uint8).reshape(nv, 12)
        r[:, 32:40] = UV.astype("<f4").view(np.uint8).reshape(nv, 8)
        out[name] = r.tobytes()
        info[name] = {"moved": int(moved.sum()), "max_mm": round(float(np.linalg.norm(P - P0, axis=1).max() * 1000), 1)}
    return out, info


def sharp(rec, mv, tris, D):
    """The body's triangles (as sorted model vertex ids) a shape bends more than SHARP against a neighbour, and by how much."""
    P0 = f32(rec, 0, 12)
    _, weld = np.unique(np.round(P0, 5), axis=0, return_inverse=True)
    weld = weld.ravel()
    local = {int(g): i for i, g in enumerate(mv)}
    edges = {}
    for ti, t in enumerate(tris):
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            edges.setdefault((min(weld[a], weld[b]), max(weld[a], weld[b])), []).append(ti)
    pairs = np.array([ts for ts in edges.values() if len(ts) == 2])
    unit = lambda X: (lambda fn: fn / (np.linalg.norm(fn, axis=1, keepdims=True) + 1e-12))(np.cross(X[tris[:, 1]] - X[tris[:, 0]], X[tris[:, 2]] - X[tris[:, 0]]))
    ang = lambda fn: np.degrees(np.arccos(np.clip(np.einsum("ij,ij->i", fn[pairs[:, 0]], fn[pairs[:, 1]]), -1, 1)))
    a0 = ang(unit(P0))
    bad = {}
    for p in range(len(PRESETS)):
        X = P0.copy()
        X[mv] += D[:, p]
        a = ang(unit(X))
        for q in np.where((a > SHARP) & (a - a0 > 0.5 * SHARP))[0]:
            for ti in pairs[q]:
                key = tuple(sorted(int(v) for v in tris[ti]))
                bad[key] = max(bad.get(key, 0.0), float(a[q]))
    return bad


def carry_race(field, base, skin, R, log):
    k = R["k"]
    ids = set(R["body"])
    mv, tris, _ = body_of(skin, ids)
    rec = records(base)
    D, _, info = carried(field, rec, mv, tris, k)
    log("on her own mesh: %s" % info)
    reach = dict(zip(mv.tolist(), np.linalg.norm(D, axis=2).max(1).tolist()))
    # what the skin can give: the worn gear's pieces down to about half, a little of the hair, what is free; a split
    # triangle costs about 10 indices (its own three more, its neighbours' halves)
    verts, idx, _, secs, _, _, _ = refine.read_skin(skin)
    tier = lambda s: M2.tier_of(s[0])
    room = min(M2.index_budget() - len(idx), 6 * (M2.SKIN_VERTEX_LIMIT - len(verts))) + 0.5 * sum(s[5] for s in secs if tier(s) == "gear" and s[0] % 100 != 1) + 0.08 * sum(s[5] for s in secs if tier(s) == "hair")
    every = np.concatenate([verts[idx[refine.section_slice(idx, s)]].reshape(-1, 3) for s in secs])
    of_tri = np.sort(np.array([max(reach.get(int(v), 0.0) for v in t) for t in every]))[::-1]
    most = max(1, int(0.4 * room / 10))
    th = max(PICK * k, float(of_tri[min(most, len(of_tri) - 1)]))
    for attempt in range(5):
        try:
            m2b, skb, ri = refine.refine(base, skin, lambda P, T, sid, level: np.array([max(reach.get(int(v), 0.0) for v in t) > th for t in T]), 1, log=lambda *a: None)
            break
        except ValueError as err:
            log("splitting where a shape moves more than %.1f mm: %s; less" % (th * 1000, err))
            th *= 1.4
    else:
        raise ValueError("no room in the skin to refine")
    log("refined where a shape moves more than %.1f mm: %s" % (th * 1000, ri))
    # once more where a shape bends the surface sharply
    mv, tris, _ = body_of(skb, ids)
    rec = records(m2b)
    D, _, _ = carried(field, rec, mv, tris, k)
    bad = sharp(rec, mv, tris, D)
    worst = sorted(bad, key=bad.get, reverse=True)
    while len(worst) >= 12:
        chosen = set(worst)
        try:
            m2b, skb, ri = refine.refine(m2b, skb, lambda P, T, sid, level: np.array([tuple(sorted(int(v) for v in t)) in chosen for t in T]), 1, log=lambda *a: None)
            log("the %d sharpest of %d bent triangles split: %s" % (len(worst), len(bad), ri))
            break
        except ValueError:
            worst = worst[:len(worst) // 2]
    mv, tris, all_tris = body_of(skb, ids)
    rec = records(m2b)
    D, dUV, info = carried(field, rec, mv, tris, k)
    left = len(sharp(rec, mv, tris, D))
    blocks, binfo = blocks_of(rec, mv, all_tris, D, dUV)
    log("%s; scale %.3f; still bent sharply: %d triangles" % (binfo, info["scale"], left))
    return blocks, skb, dict(info, shapes=binfo, sharp=left, vertices=len(rec))


def carry(source, human_v1, looks, races_json, out, only=()):
    field = Field(source)
    races = json.load(open(races_json))
    hz = zipfile.ZipFile(human_v1)
    hman = json.loads(hz.read("wrathpp-body.json"))
    man = {"format": 1, "kind": "wrathpp-body", "presets": PRESETS, "default": "Curvy", "models": []}
    report = {}
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for race, R in races.items():
            if "files" in R or (only and race not in only):
                continue
            rel = "Character/%s/Female/%sFemale" % (race, race)
            base = open(os.path.join(looks, "client", rel + ".m2"), "rb").read()
            if race == "Human":
                e = next(m for m in hman["models"] if m["race"] == "Human")
                if e["looks_sha256"] != sha(base) and e.get("looks_struct_sha256") != struct_sha(base):
                    raise SystemExit("the Human's shapes were made for other looks: rebase.py first")
                for b in e["blocks"].values():
                    z.writestr(b["file"], hz.read(b["file"]))
                z.writestr(e["skin_file"], hz.read(e["skin_file"]))
                man["models"].append(e)
                continue
            skin = open(os.path.join(looks, "client", rel + "00.skin"), "rb").read()
            try:
                blocks, skb, info = carry_race(field, base, skin, R, lambda s: print(race + ":", s, flush=True))
            except ValueError as err:
                print(race + ": NOT MADE:", err, flush=True)
                report[race] = {"error": str(err)}
                continue
            e = {"race": race, "model": rel + ".m2", "skin": rel + "00.skin", "looks_sha256": sha(base), "looks_struct_sha256": struct_sha(base),
                 "looks_vertices": struct.unpack_from("<I", base, 60)[0], "blocks": {}}
            for p in PRESETS:
                name = "%s/%s.vtx" % (race, p)
                z.writestr(name, blocks[p])
                e["blocks"][p] = {"file": name, "vertices": len(blocks[p]) // 48, "sha256": sha(blocks[p])}
            e["skin_file"] = "%s/%sFemale00.skin" % (race, race)
            e["skin_sha256"] = sha(skb)
            z.writestr(e["skin_file"], skb)
            man["models"].append(e)
            report[race] = info
        z.writestr("wrathpp-body.json", json.dumps(man, indent=1))
    json.dump(report, open(out + ".report.json", "w"), indent=1)


if __name__ == "__main__":
    if sys.argv[1] == "source":
        make_source(*sys.argv[2:6])
    elif sys.argv[1] == "carry":
        carry(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], set(sys.argv[7:]))
    else:
        raise SystemExit(__doc__)
