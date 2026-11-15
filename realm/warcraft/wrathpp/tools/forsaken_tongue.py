#!/usr/bin/env python3
"""The Forsaken woman's hanging-tongue jaw (the user: "make the forsaken use the drop down tongue mouth ... the tongue one
that the males have ... just remodel the jaw of the woman ... the tongue needs to sway like in the original head and keep
it forsaken exclusive"; made and shown in the viewer on 12 November 2026, carried into Wrath++'s looks on 13 November).

Today's Forsaken man has a jaw choice whose piece (geoset 104, his "Slobber" and "Drooler") hangs open with the tongue
out; the woman has none. Made here from today's two models, whatever their version (their heads are the same as the
prototype's, vertex for vertex):

  * his piece is fitted to her head by the bones they share (a similarity: scale, turn, move), its seam loop snapped
    onto the seam of her own jaw piece (202), the snap eased into the rest;
  * its skin is laid onto the surface her jaw had, so none of it stands off her face; the torn flesh and the mouth
    follow it; flesh that stands through the skin is sunk under it; stretched and needle-thin triangles go;
  * gaps along the join are closed with small triangles; skin laid over itself (where his shape and hers differ) is
    thinned to one layer; her own jaw skin is kept a hair under the piece wherever it shows through;
  * her skin (laid, on the join) takes her own weights and her own face texture where it lies on her face, so it
    follows every skin colour and face she has; the flesh, mouth and tongue keep his texture and, on his jaw's chain,
    his bones (his jaw and the tongue's), carried over and hung from her head with his keyframes (m2.py's graft).

build(...) returns the piece; sl_looks.py puts it in the model description (policy["graft"]) and m2.convert draws it as
the woman's jaw choice "Hanging Tongue" (geoset 205, in place of her own jaw piece).
"""
import os
import struct
import sys
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "modules", "mod-allied-races", "tools"))
import m2  # noqa: E402

HIS_PIECE = 104          # the man's hanging jaw (Slobber, Drooler)
HER_JAW = 202            # the woman's own jaw piece, the one the hanging jaw takes the place of
NEW_GEOSET = 205         # group 2's first free variant on her model: her jaw choices are 202 to 204
HER_HEAD_PARTS = (0, 2201)


class Mesh:
    """A model of today's (its own bones) and its first skin, as the graft reads them."""

    def __init__(self, model_data, skin_data):
        self.model = m2.Model(model_data)
        self.skin = m2.Skin(skin_data)
        v = np.frombuffer(b"".join(self.model.vertices), np.uint8).reshape(-1, 48)
        self.pos = v[:, 0:12].copy().view(np.float32).reshape(-1, 3)
        self.bw = v[:, 12:16].copy()
        self.bi = v[:, 16:20].copy()
        self.nrm = v[:, 20:32].copy().view(np.float32).reshape(-1, 3)
        self.uv = v[:, 32:40].copy().view(np.float32).reshape(-1, 2)
        self.tex_types = [k for k, _ in self.model.textures]
        self.tex_lookup = self.model.texture_lookup
        self.vidx = np.array(self.skin.vertices, np.int64)
        self.idx = np.array(self.skin.indices, np.int64)
        self.subs = [{"id": s[0], "start": s[4] + s[1] * 65536, "count": s[5]} for s in self.skin.sections]
        self.batches = [{"sub": b[3], "tex_combo": b[9]} for b in self.skin.batches]


def tris_of(m, s, gid, ttype=1):
    """[m]'s triangles (its vertex numbers) of geoset [gid] drawn with a texture of type [ttype]."""
    out = []
    for b in s.batches:
        sub = s.subs[b["sub"]]
        if sub["id"] == gid and m.tex_types[m.tex_lookup[b["tex_combo"]]] == ttype:
            out.append(s.vidx[s.idx[sub["start"]:sub["start"] + sub["count"]]].reshape(-1, 3))
    return np.concatenate(out) if out else np.zeros((0, 3), int)


class Bones:
    """A model's own bones: their names' hashes, parents, pivots and key bone numbers."""

    def __init__(self, model_data):
        sk = m2.OwnSkeleton(model_data)
        heads = [struct.unpack_from("<iIhHI", h) for h, _, _ in sk.bones]
        self.skeleton = sk
        self.keyid = [h[0] for h in heads]
        self.flags = [h[1] for h in heads]
        self.parent = np.array([h[2] for h in heads])
        self.crc = np.array([h[4] for h in heads], np.int64)
        self.pivot = np.array([struct.unpack("<3f", p) for _, _, p in sk.bones], np.float64)


def descendants(par, b):
    out = {b}
    grew = True
    while grew:
        grew = False
        for i, p in enumerate(par):
            if p in out and i not in out:
                out.add(i)
                grew = True
    return out


def umeyama(A, B):
    """The similarity (scale, rotation, move) taking the points [A] nearest onto [B]."""
    ma, mb = A.mean(0), B.mean(0)
    a, b = A - ma, B - mb
    U, S, Vt = np.linalg.svd(b.T @ a / len(A))
    d = np.sign(np.linalg.det(U @ Vt))
    D = np.diag([1, 1, d])
    R = U @ D @ Vt
    s = np.trace(np.diag(S) @ D) / (a ** 2).sum() * len(A)
    return s, R, mb - s * R @ ma


def main_loop(pos, tr):
    """the piece's outer seam: its longest closed border, as ordered positions."""
    key = lambda v: tuple(np.round(pos[v], 4))
    c = Counter()
    for t in tr:
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            ka, kb = key(a), key(b)
            c[(ka, kb) if ka < kb else (kb, ka)] += 1
    adj = defaultdict(list)
    for (a, b), n in c.items():
        if n == 1:
            adj[a].append(b); adj[b].append(a)
    best, seen = [], set()
    for start in adj:
        if start in seen:
            continue
        loop, cur = [start], start
        seen.add(start)
        while True:
            nx = [n for n in adj[cur] if n not in seen]
            if not nx:
                break
            cur = nx[0]; seen.add(cur); loop.append(cur)
        if len(loop) > len(best):
            best = loop
    return np.array(best)


def param(loop):
    """start at the top-centre point, run toward +y; returns the reordered loop and each point's 0..1 position."""
    i0 = int(np.argmin(np.abs(loop[:, 1]) * 4 - loop[:, 2]))
    loop = np.roll(loop, -i0, axis=0)
    if loop[1][1] < loop[-1][1]:
        loop = np.concatenate([loop[:1], loop[1:][::-1]])
    seg = np.linalg.norm(np.diff(np.concatenate([loop, loop[:1]]), axis=0), axis=1)
    return loop, np.concatenate([[0], np.cumsum(seg)[:-1]]) / seg.sum(), seg.sum()


def build(her_model, her_skin, his_model, his_skin, his_comp, log=print):
    """The piece: [her_model]/[her_skin] and [his_model]/[his_skin] today's two models' bytes; [his_comp] his composed
    texture (body left, face right with the Slobber jaw's paint; H x W x 3, floats) by which his skin is told from his
    flesh. Returns its vertices (Q, N, his texture's UV, her face texture's HUV), triangles (tr), bones (BI: hers, or
    1000 + his for the ones carried over; BW), which vertices are her skin (hers), the fit, and her own skin kept
    under it (back)."""
    f, fs = Mesh(her_model, her_skin), None
    fs = f
    mm = ms = Mesh(his_model, his_skin)
    t_sk, s_sk = Bones(her_model), Bones(his_model)
    t_crc, t_par, t_piv = t_sk.crc, t_sk.parent, t_sk.pivot
    s_crc, s_par, s_piv = s_sk.crc, s_sk.parent, s_sk.pivot
    tof = {int(c): i for i, c in enumerate(t_crc)}
    her_tex = np.zeros((512, 1024, 1), np.float32)          # the plane her face texture's coordinates are counted over
    # ---- fit the male piece to her head by the head bones
    tr = tris_of(mm, ms, 104, 1); pv = np.unique(tr)
    dom = mm.bi[pv][np.arange(len(pv)), mm.bw[pv].argmax(1)]
    bone = int(np.bincount(dom).argmax())
    while True:
        sub = [i for i in descendants(s_par, bone) if s_crc[i] in tof]
        if len(sub) >= 6 or s_par[bone] < 0:
            break
        bone = int(s_par[bone])
    sc, R, tt = umeyama(s_piv[sub], t_piv[[tof[s_crc[i]] for i in sub]])
    Q = sc * (R @ mm.pos[pv].T).T + tt
    Nn = (R @ mm.nrm[pv].T).T
    idx_of = {g: i for i, g in enumerate(pv)}
    ltr = np.vectorize(idx_of.get)(tr)

    # ---- snap its seam onto hers
    her_loop, her_t, her_len = param(main_loop(f.pos, tris_of(f, fs, 202, 1)))
    his_loop, his_t, his_len = param(main_loop(Q, ltr))
    hx = np.concatenate([her_loop, her_loop[:1]]); ht = np.concatenate([her_t, [1.0]])
    dt = np.abs(his_t[:, None] - her_t[None, :]); dt = np.minimum(dt, 1 - dt)
    snap_j = dt.argmin(1)                                            # each of his seam points takes one of her seam vertices
    for i in range(1, len(snap_j)):                                  # kept in order round the loop
        if (snap_j[i] - snap_j[i - 1]) % len(her_loop) > len(her_loop) // 2:
            snap_j[i] = snap_j[i - 1]
    target = her_loop[snap_j]
    disp_loop = target - his_loop
    log("seam: his %d points, hers %d; mean snap %.4f, max %.4f" % (len(his_loop), len(her_loop),
          np.linalg.norm(disp_loop, axis=1).mean(), np.linalg.norm(disp_loop, axis=1).max()))
    # ease the snap into the piece: each vertex follows the seam points near it, fading with distance from the seam
    d = np.linalg.norm(Q[:, None, :] - his_loop[None, :, :], axis=2)
    w = 1.0 / (d ** 2 + 1e-8)
    move = (w @ disp_loop) / w.sum(1, keepdims=True)
    fade = np.exp(-(d.min(1) / 0.022) ** 2)[:, None]
    Q2 = Q + move * fade
    on_seam = d.min(1) < 1e-4
    Q2[on_seam] = Q[on_seam] + move[on_seam]                         # exactly on her seam
    # ---- the piece's skin is laid onto the surface her own jaw piece had, everywhere (not only by the seam), so
    # none of it stands off her face or passes through her neck; the torn flesh and mouth follow their skin
    hj_all = tris_of(f, fs, 202, 1)
    def _inner(v):
        fu, fv = (f.uv[v][0] - 0.5) * 2, f.uv[v][1]
        return (0.64 < fu < 0.725 and 0.13 < fv < 0.36) or (fu > 0.90 and 0.18 < fv < 0.47) or (fu < 0.20 and fv > 0.90)
    HT = np.array([t for t in hj_all if not any(_inner(v) for v in t)])           # her jaw's outer skin triangles
    A_, B_, C_ = f.pos[HT[:, 0]].astype(np.float64), f.pos[HT[:, 1]].astype(np.float64), f.pos[HT[:, 2]].astype(np.float64)
    def closest(p):
        """closest point on her jaw skin to p: (point, triangle index, barycentric weights)."""
        ab, ac, ap = B_ - A_, C_ - A_, p - A_
        d1, d2 = (ab * ap).sum(1), (ac * ap).sum(1)
        bp = p - B_; d3, d4 = (ab * bp).sum(1), (ac * bp).sum(1)
        cp = p - C_; d5, d6 = (ab * cp).sum(1), (ac * cp).sum(1)
        va, vb, vc = d3 * d6 - d5 * d4, d5 * d2 - d1 * d6, d1 * d4 - d3 * d2
        den = va + vb + vc; den = np.where(np.abs(den) < 1e-18, 1e-18, den)
        v = vb / den; w = vc / den
        bary = np.stack([1 - v - w, v, w], 1)
        # outside the face: clamp to the triangle (project the weights back in)
        bary = np.clip(bary, 0, None); bary /= bary.sum(1, keepdims=True)
        pts = bary[:, :1] * A_ + bary[:, 1:2] * B_ + bary[:, 2:] * C_
        # a clamped weight is not always the true closest point; refine on the edges
        best = np.linalg.norm(pts - p, axis=1)
        for P0, P1, i0, i1 in ((A_, B_, 0, 1), (B_, C_, 1, 2), (C_, A_, 2, 0)):
            e = P1 - P0; t = np.clip(((p - P0) * e).sum(1) / np.maximum((e * e).sum(1), 1e-18), 0, 1)
            q = P0 + e * t[:, None]; dq = np.linalg.norm(q - p, axis=1)
            inside = (va >= 0) & (vb >= 0) & (vc >= 0)
            use = (dq < best) & ~inside
            pts[use] = q[use]; best[use] = dq[use]
            nb = np.zeros_like(bary); nb[:, i0] = 1 - t; nb[:, i1] = t
            bary[use] = nb[use]
        k = int(best.argmin())
        return pts[k], k, bary[k], best[k]
    _t = his_comp
    _uv = mm.uv[pv]
    _c = _t[(_uv[:, 1] * _t.shape[0]).astype(int).clip(0, _t.shape[0] - 1), (_uv[:, 0] * _t.shape[1]).astype(int).clip(0, _t.shape[1] - 1)]
    _rim = np.median(_c[d.min(1) < 0.012], axis=0)
    is_skin = np.linalg.norm(_c - _rim, axis=1) < 45                    # the piece's skin, not its tongue or mouth
    _tong = (_uv[:, 0] > 0.733) & (_uv[:, 0] < 0.859) & (_uv[:, 1] > 0.84)
    _lum = _c.mean(1); _sat = _c.max(1) - _c.min(1)
    is_skin |= (d.min(1) < 0.022) & ~_tong & (_sat < 60) & (_lum > 60)   # and its grimy skin in the strip beside the join
    is_skin |= (_uv[:, 0] > 0.765) & (_uv[:, 0] < 0.806) & (_uv[:, 1] > 0.680) & (_uv[:, 1] < 0.706)   # and the underside of his nose (his nostrils): hers is above the join, so here it is plain skin
    # ... and his upper lip's own skin, which is lighter than the skin at the piece's rim the first test goes by (left out,
    # that strip was neither laid on her face nor moved by her bones, and tore from the skin round it in every pose)
    is_skin |= (_uv[:, 0] > 0.74) & (_uv[:, 0] < 0.86) & (_uv[:, 1] > 0.69) & (_uv[:, 1] < 0.745) & (_sat < 60) & (_lum > 100) & ~_tong
    her_uv_at = np.zeros((len(Q2), 2)); her_n = Nn.copy(); laid = np.zeros(len(Q2), bool)
    moved = np.zeros_like(Q2)
    for i in np.nonzero(is_skin)[0]:
        cp_, k_, bc_, dist_ = closest(Q2[i])
        if dist_ > 0.035:
            continue
        moved[i] = cp_ - Q2[i]; laid[i] = True
        her_uv_at[i] = bc_ @ f.uv[HT[k_]]
        n_ = bc_ @ f.nrm[HT[k_]]; her_n[i] = n_ / (np.linalg.norm(n_) + 1e-9)
    # the rest (torn flesh, mouth, tongue) follows the skin near it, fading with distance
    sk = np.nonzero(laid)[0]
    dsk = np.linalg.norm(Q2[:, None, :] - Q2[sk][None, :, :], axis=2)
    ks = np.argsort(dsk, axis=1)[:, :6]
    ws = 1.0 / (np.take_along_axis(dsk, ks, 1) ** 2 + 1e-8)
    follow = (moved[sk][ks] * ws[..., None]).sum(1) / ws.sum(1, keepdims=True)
    follow *= np.exp(-(dsk.min(1) / 0.018) ** 2)[:, None]
    Q2 = Q2 + np.where(laid[:, None], moved, follow)
    # nothing but the tongue may stand outside the surface her jaw had: whatever does is drawn back just under it
    HNt = np.cross(B_ - A_, C_ - A_); HNt /= np.linalg.norm(HNt, axis=1, keepdims=True) + 1e-12
    _c0 = (A_ + B_ + C_) / 3
    if ((HNt * (_c0 - _c0.mean(0))).sum(1) < 0).mean() > 0.5:
        HNt = -HNt                                                    # outward
    tongue_v = (UVp_src := mm.uv[pv])[:, 0] > 0.733
    tongue_v &= (UVp_src[:, 0] < 0.859) & (UVp_src[:, 1] > 0.84)
    pulled = 0
    for i in np.nonzero(~laid & ~tongue_v)[0]:
        cp_, k_, bc_, dist_ = closest(Q2[i])
        sd_ = float((Q2[i] - cp_) @ HNt[k_])
        if sd_ > -0.0008 and dist_ < 0.05:
            Q2[i] = cp_ - HNt[k_] * 0.0012; pulled += 1
    log("vertices drawn back under her jaw surface:", pulled)
    # and under the piece's own laid skin: its triangles are chords of her rounder face, so flesh a hair under her
    # surface could still stand through them (the dark shards under the nose and along the upper lip)
    _DEPTH = 0.0035
    _skinv = laid | on_seam
    _sk_t = ltr[_skinv[ltr].all(1)]
    sunk = 0
    # ... and under her own head's skin beside the join (what stood behind her upper lip showed through it as dark flecks)
    _ht = tris_of(f, fs, 0).reshape(-1, 3)
    _hc = f.pos[_ht].mean(1)
    _ht = _ht[((_hc > Q2.min(0) - 0.015) & (_hc < Q2.max(0) + 0.015)).all(1)]
    for _pass in range(2):
        _a, _b, _c = Q2[_sk_t[:, 0]], Q2[_sk_t[:, 1]], Q2[_sk_t[:, 2]]
        _n = np.cross(_b - _a, _c - _a); _n /= np.linalg.norm(_n, axis=1, keepdims=True) + 1e-12
        _out = (her_n[_sk_t].sum(1) * _n).sum(1) < 0
        _n[_out] = -_n[_out]                                           # outward, as her normals are
        _ha, _hb, _hcn = f.pos[_ht[:, 0]].astype(np.float64), f.pos[_ht[:, 1]].astype(np.float64), f.pos[_ht[:, 2]].astype(np.float64)
        _hn = np.cross(_hb - _ha, _hcn - _ha); _hn /= np.linalg.norm(_hn, axis=1, keepdims=True) + 1e-12
        _hout = (f.nrm[_ht].sum(1) * _hn).sum(1) < 0
        _hn[_hout] = -_hn[_hout]
        _a, _b, _c, _n = np.concatenate([_a, _ha]), np.concatenate([_b, _hb]), np.concatenate([_c, _hcn]), np.concatenate([_n, _hn])
        for i in np.nonzero(~_skinv & ~tongue_v)[0]:
            sd = ((Q2[i] - _a) * _n).sum(1)
            pr = Q2[i] - sd[:, None] * _n
            v0, v1, v2 = _b - _a, _c - _a, pr - _a
            d00, d01, d11 = (v0 * v0).sum(1), (v0 * v1).sum(1), (v1 * v1).sum(1)
            d20, d21 = (v2 * v0).sum(1), (v2 * v1).sum(1)
            dn = d00 * d11 - d01 * d01 + 1e-18
            bv, bw = (d11 * d20 - d01 * d21) / dn, (d00 * d21 - d01 * d20) / dn
            hit = (bv > 0.0) & (bw > 0.0) & (bv + bw < 1.0) & (np.abs(sd) < 0.012) & (sd > -_DEPTH)
            if hit.any():
                k = np.nonzero(hit)[0][np.abs(sd[hit]).argmin()]
                Q2[i] = pr[k] - _n[k] * _DEPTH; sunk += 1
    log("flesh sunk under the piece's own skin:", sunk)
    # triangles the moves stretched into long slivers are dropped
    def _edges(P, T):
        return np.stack([np.linalg.norm(P[T[:, i]] - P[T[:, (i + 1) % 3]], axis=1) for i in range(3)], 1)
    e0, e1 = _edges(Q, ltr), _edges(Q2, ltr)
    bad = ((e1 / np.maximum(e0, 1e-6) > 1.6) & (e1 > 0.010)).any(1) & ~laid[ltr].all(1) & ~on_seam[ltr].any(1)
    _ar = np.linalg.norm(np.cross(Q2[ltr[:, 1]] - Q2[ltr[:, 0]], Q2[ltr[:, 2]] - Q2[ltr[:, 0]]), axis=1)
    bad |= (_ar / np.maximum(e1.max(1) ** 2, 1e-12) < 0.05) & (e1.max(1) > 0.010) & ~on_seam[ltr].any(1)   # needle-thin ones too
    bad |= (_ar / np.maximum(e1.max(1) ** 2, 1e-12) < 0.025) & (e1.max(1) > 0.008)                           # and hair-thin ones even on the seam
    bad &= ~laid[ltr].any(1)                                        # never a triangle of the skin itself: that would leave a hole
    log("stretched triangles dropped:", int(bad.sum()))
    ltr = ltr[~bad]
    Nn = np.where(laid[:, None], her_n, Nn)
    log("skin vertices laid on her face: %d of %d skin; largest move %.4f" % (laid.sum(), is_skin.sum(), np.linalg.norm(moved, axis=1).max()))
    # her skin the piece meets: the head, and the neck piece under the chin (geoset 2201), whose vertices the lower part of
    # the join sits on (their normals and bones are the join's there: the head's nearest vertex is round the corner)
    def _geoset(gid):
        out = [fs.vidx[fs.idx[s_["start"]:s_["start"] + s_["count"]]] for s_ in fs.subs if s_["id"] == gid]
        return np.concatenate(out) if out else np.zeros(0, int)
    hv0 = np.unique(np.concatenate([tris_of(f, fs, 0).reshape(-1), _geoset(2201)]))
    def head_normal(p):
        return f.nrm[hv0[np.linalg.norm(f.pos[hv0] - p, axis=1).argmin()]]
    UVp = mm.uv[pv].astype(np.float64).copy()
    # how much of her own face texture each vertex takes: all of it on laid skin, easing off beside the torn flesh
    nonskin = np.nonzero(~is_skin)[0]
    d_ns = np.linalg.norm(Q2[:, None, :] - Q2[nonskin][None, :, :], axis=2).min(1) if len(nonskin) else np.full(len(Q2), 1.0)
    seam_w = laid * np.clip(d_ns / 0.003, 1.0, 1)
    for i in np.nonzero(on_seam)[0]:
        Nn[i] = head_normal(Q2[i]); seam_w[i] = 1.0
        cp_, k_, bc_, dist_ = closest(Q2[i]); her_uv_at[i] = bc_ @ f.uv[HT[k_]]
    # every seam vertex of the piece sits exactly on its vertex of her seam
    for i in np.nonzero(on_seam)[0]:
        li = int(np.linalg.norm(his_loop - Q[i], axis=1).argmin())
        Q2[i] = her_loop[snap_j[li]]
    # ... and takes her texture where it now is (it was read above where his loop's point lay, up to centimetres away:
    # the laid skin beside the join was then measured, and painted, as if it reached somewhere else)
    for i in np.nonzero(on_seam)[0]:
        cp_, k_, bc_, dist_ = closest(Q2[i]); her_uv_at[i] = bc_ @ f.uv[HT[k_]]
    # where her seam has a vertex between two of his, a small triangle closes the gap
    loop_vi = [int(np.linalg.norm(Q - p_, axis=1).argmin()) for p_ in his_loop]
    extraP, extraN, extraUV, extraT, extraW, extraH = [], [], [], [], [], []
    nH = len(her_loop)
    for i in range(len(his_loop)):
        a_, b_ = loop_vi[i], loop_vi[(i + 1) % len(his_loop)]
        ja, jb = int(snap_j[i]), int(snap_j[(i + 1) % len(his_loop)])
        gap = (jb - ja) % nH
        if 2 <= gap <= 6:
            for q in range(1, gap):
                k = (ja + q) % nH
                extraP.append(her_loop[k]); extraN.append(head_normal(her_loop[k]))
                extraUV.append(UVp[a_] + (UVp[b_] - UVp[a_]) * q / gap); extraW.append(1.0)
                cp_, k_, bc_, dist_ = closest(her_loop[k]); extraH.append(bc_ @ f.uv[HT[k_]])
                prev = a_ if q == 1 else len(Q2) + len(extraP) - 2
                extraT.append([prev, len(Q2) + len(extraP) - 1, b_])
    log("filler triangles", len(extraT))
    if extraP:
        Q2 = np.concatenate([Q2, np.array(extraP)]); Nn = np.concatenate([Nn, np.array(extraN)])
        UVp = np.concatenate([UVp, np.array(extraUV)]); seam_w = np.concatenate([seam_w, np.array(extraW)])
        her_uv_at = np.concatenate([her_uv_at, np.array(extraH)])
        ltr = np.concatenate([ltr, np.array(extraT)])

    # every vertex takes the place on her face nearest it (a triangle with a corner off her skin takes her texture at its
    # skin end; the piece's own triangles take his)
    for i in range(len(Q2)):
        cp_, k_, bc_, dist_ = closest(Q2[i])
        if (her_uv_at[i] == 0).all():
            her_uv_at[i] = bc_ @ f.uv[HT[k_]]
    # ---- bone weights, so the piece moves with her: the join and the laid skin take her own weights; the rest keep
    # the male's, on her bones of the same name; his jaw and everything under it (the tongue's chain) stay his
    # bones, carried over (1000 + his bone number) and hung from her head
    skf, skm = t_sk, s_sk
    f_of = {c: i for i, c in enumerate(skf.crc)}
    jaw_m = skm.keyid.index(7)
    kids = defaultdict(list)
    for i_, p_ in enumerate(skm.parent):
        if p_ >= 0:
            kids[p_].append(i_)
    jawsub, stack = set(), [jaw_m]
    while stack:
        b_ = stack.pop(); jawsub.add(b_); stack += kids[b_]
    def map_bone(b_):
        return 1000 + b_ if (b_ in jawsub or skm.crc[b_] not in f_of) else f_of[skm.crc[b_]]
    n_orig = len(pv)
    BI = np.zeros((len(Q2), 4), np.int32); BW = np.zeros((len(Q2), 4), np.uint8)
    # flesh that shares a triangle with the laid skin moves with it (her weights); the flesh deeper in keeps his bones'
    _lz = np.zeros(len(Q2), bool); _lz[:len(laid)] = laid | on_seam
    _near_skin = np.zeros(len(Q2), bool)
    for t3 in ltr:
        if _lz[t3].any():
            _near_skin[t3] = True
    for i_ in range(len(Q2)):
        if i_ >= n_orig or on_seam[i_]:
            j_ = hv0[np.linalg.norm(f.pos[hv0] - Q2[i_], axis=1).argmin()]
            BI[i_], BW[i_] = f.bi[j_].astype(int), f.bw[j_]
        elif laid[i_] or (_near_skin[i_] and not any(mm.bw[pv[i_]][q_] and (int(mm.bi[pv[i_]][q_]) in jawsub) for q_ in range(4))):
            # her skin's own weights where the vertex lies on or by it: the laid skin, and all the rest of the piece that
            # none of his jaw's bones (the tongue's chain) moves. Left on his bones of the same names, the flesh beside
            # the laid skin moved a little differently from it in every pose, and gaps opened between them.
            cp_, k_, bc_, dist_ = closest(Q2[i_])
            acc_ = {}
            for wv_, vtx_ in zip(bc_, HT[k_]):
                for b_, w_ in zip(f.bi[vtx_], f.bw[vtx_]):
                    if w_:
                        acc_[int(b_)] = acc_.get(int(b_), 0.0) + float(wv_) * float(w_)
            top_ = sorted(acc_.items(), key=lambda kv: -kv[1])[:4]
            tot_ = sum(w_ for _, w_ in top_)
            ws_ = [int(round(w_ / tot_ * 255)) for _, w_ in top_]; ws_[0] += 255 - sum(ws_)
            for q_, ((b_, _), w_) in enumerate(zip(top_, ws_)):
                BI[i_, q_], BW[i_, q_] = b_, w_
        else:
            for q_ in range(4):
                if mm.bw[pv[i_]][q_]:
                    BI[i_, q_], BW[i_, q_] = map_bone(int(mm.bi[pv[i_]][q_])), mm.bw[pv[i_]][q_]
    log("weights: her bones on %d vertices, carried-over male bones: %s" % (int((BI < 1000).all(1).sum()), sorted(set((BI[BI >= 1000] - 1000).tolist()))))
    # The skin laid on her face folds over itself where his shape and hers differ (the underside of his nose, the edge
    # under the chin): layers of thin triangles one on another, which show as fine lines and creases. A laid triangle
    # goes when the others still cover all of it (counted over her own texture's plane, where the laid skin lies flat).
    _skinv2 = np.zeros(len(Q2), bool); _skinv2[:len(laid)] = laid | on_seam
    _onj = np.zeros(len(Q2), bool); _onj[:len(on_seam)] = on_seam; _onj[n_orig:] = True
    _cand = np.nonzero(_skinv2[ltr].all(1))[0]
    _keep_edge = set(np.nonzero(_onj[ltr].sum(1) >= 2)[0].tolist())       # a triangle with an edge on the join stays: it closes it
    _RES = 6
    def _foot(t3):
        return _foot_uv(her_uv_at[t3])
    def _foot_uv(uv3):
        px = np.asarray(uv3, np.float64) * [her_tex.shape[1] * _RES, her_tex.shape[0] * _RES]
        if np.ptp(px[:, 0]) > 0.16 * her_tex.shape[1] * _RES or np.ptp(px[:, 1]) > 0.28 * her_tex.shape[0] * _RES:
            return None                                                  # corners on separate parts of her texture: left alone
        x0, x1 = int(np.floor(px[:, 0].min())), int(np.ceil(px[:, 0].max())); y0, y1 = int(np.floor(px[:, 1].min())), int(np.ceil(px[:, 1].max()))
        den = (px[1, 1] - px[2, 1]) * (px[0, 0] - px[2, 0]) + (px[2, 0] - px[1, 0]) * (px[0, 1] - px[2, 1])
        if abs(den) < 1e-9 or x1 <= x0 or y1 <= y0:
            return (y0, x0, np.zeros((max(y1 - y0, 0) + 1, max(x1 - x0, 0) + 1), bool), den)
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        b0 = ((px[1, 1] - px[2, 1]) * (gx - px[2, 0]) + (px[2, 0] - px[1, 0]) * (gy - px[2, 1])) / den
        b1 = ((px[2, 1] - px[0, 1]) * (gx - px[2, 0]) + (px[0, 0] - px[2, 0]) * (gy - px[2, 1])) / den
        return (y0, x0, (b0 >= 0) & (b1 >= 0) & (b0 + b1 <= 1), den)
    _count = np.zeros((her_tex.shape[0] * _RES + 2, her_tex.shape[1] * _RES + 2), np.int16)
    _feet = {}
    for k in _cand:
        f_ = _foot(ltr[k])
        if f_ is not None:
            _feet[k] = f_; y0, x0, m_, _ = f_
            _count[y0:y0 + m_.shape[0], x0:x0 + m_.shape[1]] += m_
    # which way most of the laid skin winds over her texture: a triangle winding the other way is folded back
    _sign = np.sign(np.median([f_[3] for f_ in _feet.values()])) if _feet else 1
    _area = lambda k: abs(_feet[k][3])
    _gone = []
    for folded_first in (True, False):
        for k in sorted(_feet, key=_area):
            if k in _gone or k in _keep_edge or (np.sign(_feet[k][3]) != _sign) != folded_first:
                continue
            y0, x0, m_, _ = _feet[k]
            reg = _count[y0:y0 + m_.shape[0], x0:x0 + m_.shape[1]]
            if not m_.any() or (reg[m_] >= 2).all():
                reg -= m_; _gone.append(k)
    log("laid triangles under others taken out: %d of %d (folded back: %d)" % (len(_gone), len(_cand), sum(1 for k in _gone if np.sign(_feet[k][3]) != _sign)))
    ltr = np.delete(ltr, _gone, axis=0)
    # A triangle that closes the piece between her own edge and its flesh (under the chin, at the mouth's corners) shared
    # its flesh corners' normals and texture: lit as the inside of the mouth and coloured as his, it showed as a bright
    # crease on her skin. Those corners get copies for such a triangle alone: her skin's normal there, and the colour
    # her skin has at the triangle's corner on her edge.
    _sv = np.zeros(len(Q2), bool); _sv[:len(on_seam)] = on_seam; _sv[n_orig:] = True
    _lv = np.zeros(len(Q2), bool); _lv[:len(laid)] = laid
    _free = ~(_sv | _lv)
    _aQ, _aN, _aUV, _aBI, _aBW, _closed = [], [], [], [], [], 0
    _aH = []
    for k in range(len(ltr)):
        t3 = ltr[k].copy()
        if not (_sv[t3].any() and _free[t3].any()):
            continue
        edge = t3[_sv[t3]][0]
        for j in range(3):
            v = t3[j]
            if _free[v]:
                _aQ.append(Q2[v]); _aN.append(Nn[edge]); _aUV.append(UVp[edge]); _aBI.append(BI[v]); _aBW.append(BW[v]); _aH.append(her_uv_at[edge])
                ltr[k, j] = len(Q2) + len(_aQ) - 1
        _closed += 1
    if _aQ:
        Q2 = np.concatenate([Q2, np.array(_aQ)]); Nn = np.concatenate([Nn, np.array(_aN)]); UVp = np.concatenate([UVp, np.array(_aUV)])
        BI = np.concatenate([BI, np.array(_aBI)]); BW = np.concatenate([BW, np.array(_aBW)])
        her_uv_at = np.concatenate([her_uv_at, np.array(_aH)])
    log("closing triangles given her skin's normal and colour:", _closed)
    # every triangle wound to agree with its vertices' normals (a viewer that lights both sides turns the normal of a
    # triangle it takes for a back face, which drew the laid skin darker than her face beside it)
    _fn = np.cross(Q2[ltr[:, 1]] - Q2[ltr[:, 0]], Q2[ltr[:, 2]] - Q2[ltr[:, 0]])
    _flip = (_fn * Nn[ltr].sum(1)).sum(1) < 0
    ltr[_flip] = ltr[_flip][:, [0, 2, 1]]
    log("triangles rewound to their normals: %d of %d (laid skin: %d)" % (_flip.sum(), len(ltr), (_flip & np.pad(laid, (0, len(Q2) - len(laid)))[ltr].all(1)).sum()))
    _pad = lambda a_: np.concatenate([a_, np.zeros((len(Q2) - len(a_),) + a_.shape[1:], a_.dtype)]) if len(a_) < len(Q2) else a_

    # Her own skin from the nose down to her lips, a hair under the laid skin: the laid skin has his nostrils' openings
    # in it (and any pinhole of the fit), and what showed through them was the dark inside of his nose. Now it is her skin.
    import scipy.ndimage as _ndi
    _ys, _xs = np.nonzero(_count > 0)
    _box = (slice(_ys.min(), _ys.max() + 1), slice(_xs.min(), _xs.max() + 1))
    _lab, _nlab = _ndi.label(_count[_box] == 0)
    _sizes = np.bincount(_lab.reshape(-1))
    _edge = set(np.unique(np.concatenate([_lab[0], _lab[-1], _lab[:, 0], _lab[:, -1]])).tolist())
    _small = [i for i in range(1, _nlab + 1) if i not in _edge and _sizes[i] < 20000]      # holes in the laid skin: not the mouth, not the outside
    _pin = np.zeros(_count.shape, bool); _pin[_box] = np.isin(_lab, _small)
    _pin = _ndi.binary_dilation(_pin, iterations=3)
    log("holes in the laid skin: %d (cells: %s)" % (len(_small), [int(_sizes[i]) for i in _small][:12]))
    _bt = []
    for t3 in HT:                                                       # her jaw's skin under a hole of the laid skin, or wholly under the laid skin
        f_ = _foot_uv(f.uv[t3])
        if f_ is None:
            continue
        y0, x0, m_, _ = f_
        if not m_.sum():
            continue
        if _pin[y0:y0 + m_.shape[0], x0:x0 + m_.shape[1]][m_].any() or (_count[y0:y0 + m_.shape[0], x0:x0 + m_.shape[1]][m_] >= 1).mean() >= 0.9:
            _bt.append(t3)
    # Her jaw's skin has her mouth in it: a slit between her lips, which the laid skin (lying on her skin) leaves open at
    # its corners. The slit's rim is her jaw skin's open edges that are not the join; each rim is closed with triangles
    # from its middle.
    _wkey = lambda v: tuple(np.round(f.pos[v], 4))
    _ecount = Counter()
    for t3 in HT:
        for a_, b_ in ((t3[0], t3[1]), (t3[1], t3[2]), (t3[2], t3[0])):
            _ecount[tuple(sorted((_wkey(a_), _wkey(b_))))] += 1
    _onloop = lambda v: np.linalg.norm(her_loop - f.pos[v], axis=1).min() < 1e-4
    _rim = []
    for t3 in HT:
        for a_, b_ in ((t3[0], t3[1]), (t3[1], t3[2]), (t3[2], t3[0])):
            if _ecount[tuple(sorted((_wkey(a_), _wkey(b_))))] == 1 and not (_onloop(a_) and _onloop(b_)):
                _rim.append((a_, b_))
    _radj = defaultdict(list)
    for a_, b_ in _rim:
        _radj[_wkey(a_)].append((a_, b_)); _radj[_wkey(b_)].append((a_, b_))
    _seen, _slits = set(), []
    for start in list(_radj):
        if start in _seen:
            continue
        stack, edges = [start], []
        while stack:
            k_ = stack.pop()
            if k_ in _seen:
                continue
            _seen.add(k_)
            for a_, b_ in _radj[k_]:
                edges.append((a_, b_)); stack += [_wkey(a_), _wkey(b_)]
        _slits.append(list({(a_, b_) for a_, b_ in edges}))
    _bv = list(np.unique(np.array(_bt).reshape(-1))) if _bt else []
    _bQl = [f.pos[v].astype(np.float64) for v in _bv]; _bNl = [f.nrm[v].astype(np.float64) for v in _bv]
    _bUVl = [f.uv[v] for v in _bv]; _bBIl = [f.bi[v] for v in _bv]; _bBWl = [f.bw[v] for v in _bv]
    _bloc = {v: i for i, v in enumerate(_bv)}
    def _bidx(v):
        if v not in _bloc:
            _bloc[v] = len(_bQl)
            _bQl.append(f.pos[v].astype(np.float64)); _bNl.append(f.nrm[v].astype(np.float64)); _bUVl.append(f.uv[v]); _bBIl.append(f.bi[v]); _bBWl.append(f.bw[v])
        return _bloc[v]
    _btris = [[_bidx(v) for v in t3] for t3 in _bt]
    _bQ = np.array(_bQl) if _bQl else np.zeros((0, 3)); _bN = np.array(_bNl) if _bNl else np.zeros((0, 3))
    _bon = np.array([np.linalg.norm(her_loop - p_, axis=1).min() < 1e-4 for p_ in _bQ]) if len(_bQ) else np.zeros(0, bool)
    _bQ[~_bon] -= _bN[~_bon] * 0.0007                                   # the join's own vertices stay on the join
    _bTr = np.array(_btris) if _btris else np.zeros((0, 3), int)
    _bv = np.arange(len(_bQ))
    log("her own skin under the laid skin: %d triangles, %d of its %d vertices on the join" % (len(_bTr), int(_bon.sum()), len(_bv)))

    # which of the piece's vertices are her skin (drawn with her own face texture) and which its flesh (his)
    hers = np.zeros(len(Q2), bool)
    hers[:len(laid)] = laid | on_seam
    hers[n_orig:n_orig + len(extraP)] = True
    hers[len(Q2) - len(_aQ):] = True
    return {"Q": Q2, "N": Nn, "UV": UVp, "HUV": her_uv_at, "tr": ltr, "BI": BI, "BW": BW, "hers": hers,
            "fit": (float(sc), R, tt), "carried": sorted(set((BI[BI >= 1000] - 1000).tolist())), "his_jaw": jaw_m,
            "back": {"Q": _bQ, "N": _bN, "UV": np.array(_bUVl).reshape(-1, 2), "tr": _bTr, "BI": np.array(_bBIl).reshape(-1, 4), "BW": np.array(_bBWl).reshape(-1, 4)}}

