"""A converted character model (3.3.5 .m2 and its 00.skin) with chosen triangles split, finer where the body options
reshape it, paid for by the worn gear's pieces cut down a little more, so the skin stays within 3.3.5's 65535 indices.

  refine(m2_bytes, skin_bytes, pick, levels) -> (m2_bytes, skin_bytes, info)

pick(positions, tris, section_ids) -> boolean per triangle: the ones to split (red-green: neighbours split along the
shared edge only, so nothing opens). New vertices: Phong tessellation's edge midpoint (the midpoint pulled onto the two
corners' tangent planes, so the surface stays round), normals and texture coordinates averaged, bone weights mixed
(the 4 heaviest, bytes summing to 255). Every split triangle stays in its own section, with its bones."""
import os, struct, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'modules', 'mod-allied-races', 'tools'))
import decimate, m2 as M2

VERT = 48
HAIR_FLOOR = 0.9            # the hair keeps at least this much of what the looks gave it


def read_skin(s):
    vn, vo, ixn, ixo, pn, po, sn, so, bn, bo, mx = struct.unpack_from("<11I", s, 4)
    verts = np.frombuffer(s, "<u2", vn, vo).astype(np.int64)
    idx = np.frombuffer(s, "<u2", ixn, ixo).astype(np.int64)
    props = np.frombuffer(s, np.uint8, pn * 4, po).reshape(pn, 4).copy()
    secs = [list(struct.unpack_from("<10H7f", s, so + i * 48)) for i in range(sn)]
    batches = s[bo:bo + bn * 24]
    return verts, idx, props, secs, batches, bn, mx


def write_skin(verts, idx, props, secs, batches, bn, mx):
    header = 48
    body = bytearray()
    def put(payload):
        while (header + len(body)) % 16: body.append(0)
        at = header + len(body); body.extend(payload); return at
    parts = [(len(verts), put(struct.pack("<%dH" % len(verts), *verts))),
             (len(idx), put(struct.pack("<%dH" % len(idx), *idx))),
             (len(props), put(bytes(np.asarray(props, np.uint8).tobytes()))),
             (len(secs), put(b"".join(struct.pack("<10H7f", *s) for s in secs))),
             (bn, put(batches))]
    head = bytearray(b"SKIN")
    for c, o in parts: head += struct.pack("<II", c, o)
    head += struct.pack("<I", mx)
    return bytes(head) + bytes(body)


def mix_bones(wa, ba, wb, bb):
    acc = {}
    for w, b in list(zip(wa, ba)) + list(zip(wb, bb)):
        if w: acc[int(b)] = acc.get(int(b), 0) + 0.5 * w
    top = sorted(acc.items(), key=lambda kv: -kv[1])[:4]
    tot = sum(w for _, w in top)
    raw = [w / tot * 255 for _, w in top]
    q = [int(np.floor(x)) for x in raw]
    for j in sorted(range(len(raw)), key=lambda j: -(raw[j] - q[j]))[:255 - sum(q)]: q[j] += 1
    bones = [b for b, _ in top]
    while len(q) < 4: q.append(0); bones.append(0)
    return q, bones


def refine(m2b, skb, pick, levels=1, log=print):
    d = bytearray(m2b)
    nv, ov = struct.unpack_from("<II", d, 60)
    V = [bytes(d[ov + i * VERT: ov + (i + 1) * VERT]) for i in range(nv)]
    verts, idx, props, secs, batches, bn, mx = read_skin(skb)
    # each section's triangles as model vertex ids, and each (section, vertex)'s bone slots
    tris, slots = [], []
    for si, s in enumerate(secs):
        st = s[4] + s[1] * 65536
        loc = idx[st:st + s[5]].reshape(-1, 3)
        tris.append(verts[loc].copy())
        sl = {}
        for k in range(s[2], s[2] + s[3]): sl[int(verts[k])] = bytes(props[k])
        slots.append(sl)
    lookup_ofs = struct.unpack_from("<II", d, 120)
    lookup = np.frombuffer(bytes(d), "<u2", lookup_ofs[0], lookup_ofs[1])
    pos = lambda i: np.array(struct.unpack_from("<3f", V[i], 0))
    nrm = lambda i: np.array(struct.unpack_from("<3f", V[i], 20))
    for level in range(levels):
        P = np.array([struct.unpack_from("<3f", v, 0) for v in V])
        key = [tuple(np.round(p, 5)) for p in P]
        allt = np.concatenate(tris); owner = np.concatenate([np.full(len(t), si) for si, t in enumerate(tris)])
        chosen = pick(P, allt, np.array([secs[o][0] for o in owner]), level)
        # red-green: edges marked by place; a triangle with two marked edges has its third marked too
        ek = lambda a, b: (min(key[a], key[b]), max(key[a], key[b]))
        marked = set()
        for t in allt[chosen]:
            for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])): marked.add(ek(a, b))
        mid = {}
        def midpoint(a, b, si):
            k = (min(a, b), max(a, b))
            if k in mid: return mid[k]
            pa, pb, na, nb = pos(a), pos(b), nrm(a), nrm(b)
            m = 0.5 * (pa + pb)
            pr = lambda p, n: m - np.dot(m - p, n) * n
            q = 0.5 * (pr(pa, na) + pr(pb, nb))
            n = na + nb; n /= np.linalg.norm(n) + 1e-12
            va, vb = V[a], V[b]
            wa, ba = va[12:16], va[16:20]; wb, bb = vb[12:16], vb[16:20]
            w, bo = mix_bones(wa, ba, wb, bb)
            uva = struct.unpack_from("<4f", va, 32); uvb = struct.unpack_from("<4f", vb, 32)
            rec = struct.pack("<3f", *q) + bytes(w) + bytes(bo) + struct.pack("<3f", *n) + struct.pack("<4f", *[(x + y) / 2 for x, y in zip(uva, uvb)])
            V.append(rec); mid[k] = len(V) - 1
            return mid[k]
        new_tris = []
        nsplit = 0
        for si, T in enumerate(tris):
            out = []
            s = secs[si]
            pal = list(lookup[s[7]:s[7] + s[6]])
            for t in T:
                a, b, c = (int(x) for x in t)
                m_ab, m_bc, m_ca = (ek(a, b) in marked), (ek(b, c) in marked), (ek(c, a) in marked)
                n = m_ab + m_bc + m_ca
                if n == 0: out.append((a, b, c)); continue
                nsplit += 1
                if n == 3:
                    x, y, z = midpoint(a, b, si), midpoint(b, c, si), midpoint(c, a, si)
                    out += [(a, x, z), (x, b, y), (z, y, c), (x, y, z)]
                elif n == 2:
                    # two edges split: the corner between them cut off, the rest in two (the shorter diagonal)
                    if not m_ab: a, b, c = c, a, b                 # turned (keeping the winding) so (b, c) is the edge not split
                    elif not m_ca: a, b, c = b, c, a
                    x, z = midpoint(a, b, si), midpoint(c, a, si)
                    out.append((a, x, z))
                    if np.linalg.norm(pos(x) - pos(c)) < np.linalg.norm(pos(z) - pos(b)): out += [(x, b, c), (x, c, z)]
                    else: out += [(x, b, z), (z, b, c)]
                else:
                    if m_ab: x = midpoint(a, b, si); out += [(a, x, c), (x, b, c)]
                    elif m_bc: y = midpoint(b, c, si); out += [(a, b, y), (a, y, c)]
                    else: z = midpoint(c, a, si); out += [(a, b, z), (z, b, c)]
                for v in out[-(4 if n == 3 else 3 if n == 2 else 2):]:
                    for g in v:
                        if g not in slots[si]:
                            rec = V[g]; w = rec[12:16]; bo = rec[16:20]
                            sl = [0, 0, 0, 0]
                            for j in range(4):
                                if w[j]:
                                    sl[j] = pal.index(bo[j])
                            slots[si][g] = bytes(sl)
            new_tris.append(np.array(out, np.int64).reshape(-1, 3))
        tris = new_tris
        log("level %d: %d triangles split, %d new vertices" % (level + 1, nsplit, len(mid)))
    # within 3.3.5's indices: the worn gear's pieces (not the bare variant 01) give way
    total = sum(len(t) * 3 for t in tris)
    P = np.array([struct.unpack_from("<3f", v, 0) for v in V])
    gear = [si for si, s in enumerate(secs) if M2.tier_of(s[0]) == "gear" and s[0] % 100 != 1 and len(tris[si]) > 4]
    budget = M2.INDEX_BUDGET - 40
    if total > budget:
        # where a piece meets what can be drawn with it (another group: the body, the bare pieces); a group's
        # variants are drawn one at a time and may part along their shared edges
        joins = {}
        for si in gear:
            others = {sj: tris[sj] for sj in range(len(tris)) if secs[sj][0] // 100 != secs[si][0] // 100}
            others[si] = tris[si]
            joins[si] = M2.shared_positions(P, others)[si]
        gsum = sum(len(tris[si]) * 3 for si in gear)
        for attempt in range(20):
            total = sum(len(t) * 3 for t in tris)
            if total <= budget: break
            gsum = sum(len(tris[si]) * 3 for si in gear)
            frac = max(0.45, (gsum - (total - budget) * 1.05) / gsum)
            for si in gear:
                tgt = max(1, int(len(tris[si]) * frac))
                tris[si] = decimate.decimate(P, tris[si], tgt, locked=joins.get(si, set()))
            log("gear cut to %.0f%%: %d indices" % (frac * 100, sum(len(t) * 3 for t in tris)))
    # then the hair (every style's own section, one drawn at a time), at most HAIR_FLOOR of what it had
    total = sum(len(t) * 3 for t in tris)
    hair = [si for si, s in enumerate(secs) if M2.tier_of(s[0]) == "hair" and len(tris[si]) > 4]
    if total > budget and hair:
        hjoins = {}
        for si in hair:
            others = {sj: tris[sj] for sj in range(len(tris)) if M2.tier_of(secs[sj][0]) != "hair"}
            others[si] = tris[si]
            hjoins[si] = M2.shared_positions(P, others)[si]
        h0 = sum(len(tris[si]) * 3 for si in hair)
        for attempt in range(10):
            total = sum(len(t) * 3 for t in tris)
            if total <= budget: break
            hs = sum(len(tris[si]) * 3 for si in hair)
            frac = max(HAIR_FLOOR * h0 / hs, (hs - (total - budget) * 1.05) / hs)
            if frac >= 0.999: break
            for si in hair:
                tris[si] = decimate.decimate(P, tris[si], max(1, int(len(tris[si]) * frac)), locked=hjoins[si])
            log("hair cut to %.0f%% of what it had: %d indices" % (100.0 * sum(len(tris[si]) * 3 for si in hair) / h0, sum(len(t) * 3 for t in tris)))
    total = sum(len(t) * 3 for t in tris)
    if total > M2.INDEX_BUDGET: raise ValueError("still %d indices" % total)
    # the skin again
    out_v, out_i, out_p = [], [], []
    for si, s in enumerate(secs):
        place = {}
        vs, ist = len(out_v), len(out_i)
        infl = 0
        for t in tris[si]:
            for g in t:
                g = int(g)
                if g not in place:
                    place[g] = len(out_v); out_v.append(g); out_p.append(slots[si][g])
                    infl = max(infl, sum(1 for x in V[g][12:16] if x))
                out_i.append(place[g])
        s[1] = 0; s[2] = vs; s[3] = len(place); s[4] = ist; s[5] = len(tris[si]) * 3; s[8] = max(1, infl)
    if len(out_v) > 65535: raise ValueError("too many skin vertices")
    skin = write_skin(out_v, out_i, np.frombuffer(b"".join(out_p), np.uint8).reshape(-1, 4), secs, batches, bn, mx)
    # the model's vertices: the new array at the end of the file
    while len(d) % 16: d.append(0)
    at = len(d); d += b"".join(V)
    struct.pack_into("<II", d, 60, len(V), at)
    return bytes(d), skin, {"vertices": len(V), "added": len(V) - nv, "indices": len(out_i), "skin_vertices": len(out_v)}
