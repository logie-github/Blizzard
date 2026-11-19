"""Mesh simplification for the converter (m2.py): fewer triangles for a mesh section, by quadric
error metrics with half-edge collapses (a vertex slides onto a neighbour; no new vertices, so
every vertex keeps its texture coordinates, normal and bones). Boundaries and texture seams are
kept: a vertex on an open edge, or sharing its position with another vertex (the two sides of a
seam), stays where it is.

A stock 3.3.5 reads a mesh section's triangle start as a 16-bit number, so a model's sections have to fit in
65535 indices; today's character models have twice that. m2.convert cuts a model's own skin (<Model>00.skin) to that,
and writes the whole one beside it (<Model>00w.skin, m2.WIDE_SKINS), which Wrath++'s native mod makes the stock client
draw: there only what would pass the skin's vertex limit (65535) or m2.WIDE_INDEX_BUDGET is the cut skin's.
"""
import heapq

import numpy as np


UV_SCALE = 0.25                # a texture unit counts as this fraction of the mesh's diagonal in the error
BOUNDARY_WEIGHT = 10.0          # how hard an open outline is held (the plane of the edge, without texture coordinates)
BOUNDARY_WEIGHT_HAIR = 20.0     # (with them, and for hair: the cards' silhouettes)
SLIVER = 0.08                   # a triangle's quality (1 for an equilateral one) below which a collapse may not leave it


def decimate(positions, triangles, target, locked=(), uvs=None, kind=None):
    """[positions]: N x 3 of the vertices the triangles name (any ids: only the ones used matter);
    [triangles]: M x 3 vertex ids; [target]: the triangle count to come down to; [uvs]: N x 2 texture coordinates, when
    given they are part of the error (below); [kind]: the model's tier of the section ("hair": see below). Returns the
    triangles kept (K x 3, K <= M, with K >= target unless the mesh runs out of collapses).

    With [uvs] the error is the quadric of the five-dimensional points (x, y, z, s*u, s*v), s scaling a texture unit to the
    mesh's own size (Garland and Heckbert's attribute quadrics): a collapse that moves a vertex over the texture
    (stretching a hair card's alpha picture over a sliver) costs as much as one that moves it in space. A collapse may
    not turn a triangle over in the texture either. The open outline of a mesh (a hair card's silhouette) is held to its
    own line in both spaces, [kind] "hair" much harder, and a triangle may not become a sliver."""
    tris = [tuple(int(v) for v in t) for t in np.asarray(triangles).reshape(-1, 3)]
    tris = [t for t in tris if len(set(t)) == 3]
    if len(tris) <= target:
        return np.array(tris, dtype=np.int64).reshape(-1, 3)
    pos = np.asarray(positions, dtype=np.float64)
    used = sorted(set(v for t in tris for v in t))
    if uvs is not None:
        uv = np.asarray(uvs, dtype=np.float64)
        diag = float(np.linalg.norm(pos[used].max(0) - pos[used].min(0))) or 1.0
        feat = np.zeros((len(pos), 5))
        feat[:, :3] = pos
        feat[:, 3:] = uv * (UV_SCALE * diag)
    else:
        uv = None
        feat = pos
    dim = feat.shape[1]
    boundary_weight = BOUNDARY_WEIGHT_HAIR if kind == "hair" else BOUNDARY_WEIGHT
    locked = set(int(v) for v in locked)
    # the same position twice: the two sides of a texture seam. They move together (a collapse
    # of one onto a neighbour takes the other onto that neighbour's twin), so the seam stays
    # closed; a position shared by more than two vertices stays where it is.
    at = {}
    for t in tris:
        for v in t:
            at.setdefault(tuple(np.round(pos[v], 5)), set()).add(v)
    twin = {}
    for vs in at.values():
        if len(vs) == 2:
            a, b = tuple(vs)
            twin[a], twin[b] = b, a
        elif len(vs) > 2:
            locked.update(vs)
    alive = [True] * len(tris)
    faces_of = {}
    for i, t in enumerate(tris):
        for v in t:
            faces_of.setdefault(v, set()).add(i)

    def plane(t):
        a, b, c = pos[t[0]], pos[t[1]], pos[t[2]]
        n = np.cross(b - a, c - a)
        area = np.linalg.norm(n)
        if area < 1e-12:
            return None, 0.0
        n /= area
        return np.append(n, -np.dot(n, a)), area * 0.5

    def quadric_of_flat(points, area):
        """The squared distance to the flat through [points] (two directions in dim dimensions), times [area], as a
        (dim+1)-square matrix over (x, 1)."""
        p = points[0]
        e1 = points[1] - p
        n1 = np.linalg.norm(e1)
        if n1 < 1e-12:
            return None
        e1 = e1 / n1
        e2 = points[2] - p
        e2 = e2 - np.dot(e2, e1) * e1
        n2 = np.linalg.norm(e2)
        if n2 < 1e-12:
            return None
        e2 = e2 / n2
        A = np.eye(dim) - np.outer(e1, e1) - np.outer(e2, e2)
        b = np.dot(p, e1) * e1 + np.dot(p, e2) * e2 - p
        c = np.dot(p, p) - np.dot(p, e1) ** 2 - np.dot(p, e2) ** 2
        M = np.zeros((dim + 1, dim + 1))
        M[:dim, :dim] = A
        M[:dim, dim] = b
        M[dim, :dim] = b
        M[dim, dim] = c
        return M * area

    Q = {}
    for i, t in enumerate(tris):
        p, area = plane(t)
        if p is None:
            continue
        if uv is None:
            q = np.outer(p, p) * area
        else:
            q = quadric_of_flat(feat[list(t)], area)
            if q is None:
                continue
        for v in t:
            Q[v] = Q.get(v, 0) + q
    # open edges: a vertex on one may only slide along it (onto a neighbour on the same open
    # edge), and the edge's own plane weighs in so the outline keeps its shape
    edge_count = {}

    def edges(t):
        return (frozenset((t[0], t[1])), frozenset((t[1], t[2])), frozenset((t[2], t[0])))

    for t in tris:
        for e in edges(t):
            edge_count[e] = edge_count.get(e, 0) + 1
    for i, t in enumerate(tris):
        p, area = plane(t)
        if p is None:
            continue
        for e in edges(t):
            if edge_count[e] == 1:
                a, b = tuple(e)
                if uv is None:
                    d = pos[b] - pos[a]
                    n = np.cross(d, p[:3])
                    ln = np.linalg.norm(n)
                    if ln < 1e-12:
                        continue
                    n /= ln
                    bp = np.append(n, -np.dot(n, pos[a]))
                    q = np.outer(bp, bp) * (np.linalg.norm(d) ** 2 * boundary_weight)
                else:
                    # the outline's own line in space and texture together: a vertex off it costs, along it does not
                    d = feat[b] - feat[a]
                    ln = np.linalg.norm(d)
                    if ln < 1e-12:
                        continue
                    e1 = d / ln
                    A = np.eye(dim) - np.outer(e1, e1)
                    bv = np.dot(feat[a], e1) * e1 - feat[a]
                    c = np.dot(feat[a], feat[a]) - np.dot(feat[a], e1) ** 2
                    q = np.zeros((dim + 1, dim + 1))
                    q[:dim, :dim] = A
                    q[:dim, dim] = bv
                    q[dim, :dim] = bv
                    q[dim, dim] = c
                    q *= ln * ln * boundary_weight
                Q[a] = Q.get(a, 0) + q
                Q[b] = Q.get(b, 0) + q

    def on_boundary(v):
        return any(edge_count.get(e, 0) == 1 for i in faces_of.get(v, ()) for e in edges(tris[i]) if v in e)

    version = {}
    ZERO = np.zeros((dim + 1, dim + 1))

    def cost(a, b):
        p = np.append(feat[b], 1.0)
        # (a vertex of degenerate triangles alone has no quadric: nothing says what collapsing it costs, so it goes last)
        if a not in Q or b not in Q:
            return 1e30
        return float(p @ (Q[a] + Q[b]) @ p)

    def allowed(a, b):
        if a in locked or a not in faces_of or b not in faces_of:
            return False
        if not any(b in tris[i] for i in faces_of[a]):
            return False
        if on_boundary(a) and edge_count.get(frozenset((a, b)), 0) != 1:
            return False
        return True

    def push(a, b, heap):
        if not allowed(a, b):
            return
        version[a] = version.get(a, 0)
        heapq.heappush(heap, (cost(a, b), a, b, version[a], version.get(b, 0)))

    def uv_area(t):
        u = uv[list(t)]
        return (u[1, 0] - u[0, 0]) * (u[2, 1] - u[0, 1]) - (u[2, 0] - u[0, 0]) * (u[1, 1] - u[0, 1])

    def quality(t):
        a, b, c = pos[t[0]], pos[t[1]], pos[t[2]]
        area = np.linalg.norm(np.cross(b - a, c - a)) * 0.5
        sq = np.dot(b - a, b - a) + np.dot(c - b, c - b) + np.dot(a - c, a - c)
        return 4.0 * 1.7320508 * area / sq if sq > 1e-18 else 0.0

    def flips(a, b):
        """The triangles around a that b replaces a in, or None if one would turn over (in space, or in the texture), or
        become a sliver."""
        changed = []
        for i in faces_of[a]:
            t = tris[i]
            if b in t:
                continue
            before, _ = plane(t)
            after_t = tuple(b if v == a else v for v in t)
            after, _ = plane(after_t)
            if before is None or after is None or np.dot(before[:3], after[:3]) < 0.1:
                return None
            if uv is not None:
                ub, ua = uv_area(t), uv_area(after_t)
                if ub * ua < 0 or (abs(ub) > 1e-12 and abs(ua) < 0.05 * abs(ub)):
                    return None
                qb, qa = quality(t), quality(after_t)
                if qa < SLIVER and qa < 0.5 * qb:
                    return None
            changed.append((i, after_t))
        return changed

    def collapse(a, b, changed):
        nonlocal count
        for i in list(faces_of[a]):
            t = tris[i]
            if b in t:
                alive[i] = False
                count -= 1
                for e in edges(t):
                    edge_count[e] -= 1
                for v in t:
                    faces_of[v].discard(i)
                    if not faces_of[v]:
                        del faces_of[v]
        for i, after_t in changed:
            for e in edges(tris[i]):
                edge_count[e] -= 1
            tris[i] = after_t
            for e in edges(after_t):
                edge_count[e] = edge_count.get(e, 0) + 1
            faces_of.setdefault(b, set()).add(i)
        faces_of.pop(a, None)
        if a in Q or b in Q:
            Q[b] = Q.get(a, ZERO) + Q.get(b, ZERO)
        version[a] = version.get(a, 0) + 1
        version[b] = version.get(b, 0) + 1
        around = set()
        for i in faces_of.get(b, ()):
            around.update(tris[i])
        around.discard(b)
        for v in around:
            push(v, b, heap)
            push(b, v, heap)

    heap = []
    for e in edge_count:
        a, b = tuple(e)
        push(a, b, heap)
        push(b, a, heap)
    count = len(tris)
    while count > target and heap:
        c, a, b, va, vb = heapq.heappop(heap)
        if version.get(a, 0) != va or version.get(b, 0) != vb or not allowed(a, b):
            continue
        changed = flips(a, b)
        if changed is None:
            continue
        a2, b2 = twin.get(a), twin.get(b)
        if a2 is not None and a2 in faces_of:
            # the seam's other side goes along, onto b's twin (or b itself where the seam ends)
            target2 = b2 if (b2 is not None and allowed(a2, b2)) else (b if allowed(a2, b) else None)
            if target2 is None:
                continue
            changed2 = flips(a2, target2)
            if changed2 is None:
                continue
            collapse(a, b, changed)
            if a2 in faces_of and target2 in faces_of:
                collapse(a2, target2, changed2)
        else:
            collapse(a, b, changed)
    out = [t for i, t in enumerate(tris) if alive[i]]
    return np.array(out, dtype=np.int64).reshape(-1, 3)


def plan(sizes, budget, floors):
    """How much of each tier to keep: [sizes]: tier -> index count; [budget]: indices allowed in
    all; [floors]: tiers in the order they give way, each with the fraction it never goes below.
    Returns tier -> fraction (1.0 where nothing is taken), taking from the first tiers first."""
    keep = {t: 1.0 for t in sizes}
    total = sum(sizes.values())
    for tier, floor in floors:
        if total <= budget:
            break
        if tier not in sizes or not sizes[tier]:
            continue
        need = total - budget
        can = sizes[tier] * (keep[tier] - floor)
        take = min(need, can)
        keep[tier] -= take / sizes[tier]
        total -= take
    if total > budget:
        # still over: everything the same bit more
        f = budget / total
        for t in keep:
            keep[t] *= f
    return keep


def _closest_on_triangles(p, a, b, c):
    """The closest point to [p] on each of the triangles (a, b, c: K x 3), Ericson's method, all at once."""
    ab, ac, ap = b - a, c - a, p - a
    d1, d2 = (ab * ap).sum(1), (ac * ap).sum(1)
    bp = p - b
    d3, d4 = (ab * bp).sum(1), (ac * bp).sum(1)
    cp = p - c
    d5, d6 = (ab * cp).sum(1), (ac * cp).sum(1)
    vc, vb, va = d1 * d4 - d3 * d2, d5 * d2 - d1 * d6, d3 * d6 - d5 * d4
    out = np.empty_like(a)
    for k in range(len(a)):
        if d1[k] <= 0 and d2[k] <= 0:
            out[k] = a[k]
        elif d3[k] >= 0 and d4[k] <= d3[k]:
            out[k] = b[k]
        elif vc[k] <= 0 and d1[k] >= 0 and d3[k] <= 0:
            out[k] = a[k] + ab[k] * (d1[k] / (d1[k] - d3[k]) if d1[k] != d3[k] else 0.0)
        elif d6[k] >= 0 and d5[k] <= d6[k]:
            out[k] = c[k]
        elif vb[k] <= 0 and d2[k] >= 0 and d6[k] <= 0:
            out[k] = a[k] + ac[k] * (d2[k] / (d2[k] - d6[k]) if d2[k] != d6[k] else 0.0)
        elif va[k] <= 0 and (d4[k] - d3[k]) >= 0 and (d5[k] - d6[k]) >= 0:
            w = (d4[k] - d3[k]) / ((d4[k] - d3[k]) + (d5[k] - d6[k])) if ((d4[k] - d3[k]) + (d5[k] - d6[k])) != 0 else 0.0
            out[k] = b[k] + (c[k] - b[k]) * w
        else:
            total = va[k] + vb[k] + vc[k]
            den = 1.0 / total if total != 0 else 0.0
            out[k] = a[k] + ab[k] * (vb[k] * den) + ac[k] * (vc[k] * den)
    return out


def sink_lifts(positions, normals, before, after, locked=(), cap=0.025):
    """What cutting a mesh section down takes from a shell that lies over something (hair over the scalp, worn gear over
    the body): a triangle spanning what were several is a chord, inside the surface the removed vertices lay on, and the
    skin shows through it. Returns {vertex: distance} to move each kept vertex out along its normal so that every removed
    vertex is under the new surface again: each removed vertex that lies out along its normal from the nearest kept
    triangle asks that triangle's three vertices for that height (the most asked wins, at most [cap]).
    [positions], [normals]: N x 3 of the model's vertices; [before], [after]: the section's triangles (M x 3) before and
    after the cut; [locked]: vertices that stay where they are (a seam with another section)."""
    before, after = np.asarray(before).reshape(-1, 3), np.asarray(after).reshape(-1, 3)
    if len(after) == 0 or len(before) <= len(after):
        return {}
    kept = set(int(v) for v in after.ravel())
    removed = np.array(sorted(set(int(v) for v in before.ravel()) - kept), dtype=np.int64)
    if not len(removed):
        return {}
    locked = set(int(v) for v in locked)
    A, B, C = positions[after[:, 0]], positions[after[:, 1]], positions[after[:, 2]]
    centre = (A + B + C) / 3.0
    lifts = {}
    for r in removed:
        p = positions[r]
        # (the nearest sixteen by a stable order, taken in the mesh's own order: two triangles that share the closest point
        # are the same far, and which one wins must not depend on the machine's sort: the lifts have to come out the same
        # on every build, or the looks' models differ from one build to the next and the body options package, which names
        # the model it was made for, stops matching)
        near = np.sort(np.argsort(((centre - p) ** 2).sum(1), kind="stable")[:16])
        hits = _closest_on_triangles(p, A[near], B[near], C[near])
        k = int(np.argmin(np.round(((hits - p) ** 2).sum(1), 12)))
        n = normals[r]
        ln = np.linalg.norm(n)
        if ln < 1e-9:
            continue
        height = round(float(np.dot(p - hits[k], n / ln)), 5)       # (to a hundredth of a millimetre: no last-bit drift)
        if not np.isfinite(height) or height <= 1e-5:
            continue
        for v in after[near[k]]:
            v = int(v)
            if v not in locked:
                lifts[v] = min(cap, max(lifts.get(v, 0.0), height))
    return lifts


def plan_stages(sizes, budget, stages, current=None, skip=()):
    """Like plan, in stages: [stages]: lists of (tier, floor), floors fractions of the tier's size in [sizes] (the source's).
    A stage takes from its tiers in order, each down to its floor; the next stage opens only when the total is still over
    the budget after it. [current]: tier -> the size the tier has now (default: [sizes]); [skip]: tiers that gave all they
    could (not taken from again). Returns tier -> fraction of [sizes] to come down to. Over budget after the last stage:
    everything the same bit more."""
    now = dict(sizes) if current is None else {t: current.get(t, 0) for t in sizes}
    keep = {t: (now[t] / sizes[t] if sizes[t] else 1.0) for t in sizes}
    total = sum(now.values())
    for stage in stages:
        for tier, floor in stage:
            if total <= budget:
                break
            if tier not in sizes or not sizes[tier] or tier in skip:
                continue
            can = sizes[tier] * max(0.0, keep[tier] - floor)
            take = min(total - budget, can)
            keep[tier] -= take / sizes[tier]
            total -= take
    if total > budget:
        f = budget / total
        for t in keep:
            keep[t] *= f
    return keep
