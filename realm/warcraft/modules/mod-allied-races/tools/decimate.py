"""Mesh simplification for the converter (m2.py): fewer triangles for a mesh section, by quadric
error metrics with half-edge collapses (a vertex slides onto a neighbour; no new vertices, so
every vertex keeps its texture coordinates, normal and bones). Boundaries and texture seams are
kept: a vertex on an open edge, or sharing its position with another vertex (the two sides of a
seam), stays where it is.

3.3.5 reads a mesh section's triangle start as a 16-bit number (the modern format's high word is
lost on it), so a model's sections have to fit in 65535 indices; today's character models have
twice that, and the HD look's models were cut down the same way.
"""
import heapq

import numpy as np


def decimate(positions, triangles, target, locked=()):
    """[positions]: N x 3 of the vertices the triangles name (any ids: only the ones used matter);
    [triangles]: M x 3 vertex ids; [target]: the triangle count to come down to. Returns the
    triangles kept (K x 3, K <= M, with K >= target unless the mesh runs out of collapses)."""
    tris = [tuple(int(v) for v in t) for t in np.asarray(triangles).reshape(-1, 3)]
    tris = [t for t in tris if len(set(t)) == 3]
    if len(tris) <= target:
        return np.array(tris, dtype=np.int64).reshape(-1, 3)
    pos = np.asarray(positions, dtype=np.float64)
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

    Q = {}
    for i, t in enumerate(tris):
        p, area = plane(t)
        if p is None:
            continue
        q = np.outer(p, p) * area
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
                d = pos[b] - pos[a]
                n = np.cross(d, p[:3])
                ln = np.linalg.norm(n)
                if ln < 1e-12:
                    continue
                n /= ln
                bp = np.append(n, -np.dot(n, pos[a]))
                q = np.outer(bp, bp) * (np.linalg.norm(d) ** 2 * 10.0)
                Q[a] = Q.get(a, 0) + q
                Q[b] = Q.get(b, 0) + q

    def on_boundary(v):
        return any(edge_count.get(e, 0) == 1 for i in faces_of.get(v, ()) for e in edges(tris[i]) if v in e)

    version = {}
    ZERO = np.zeros((4, 4))

    def cost(a, b):
        p = np.append(pos[b], 1.0)
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

    def flips(a, b):
        """The triangles around a that b replaces a in, or None if one would turn over."""
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
            out[k] = a[k] + ab[k] * (d1[k] / (d1[k] - d3[k]))
        elif d6[k] >= 0 and d5[k] <= d6[k]:
            out[k] = c[k]
        elif vb[k] <= 0 and d2[k] >= 0 and d6[k] <= 0:
            out[k] = a[k] + ac[k] * (d2[k] / (d2[k] - d6[k]))
        elif va[k] <= 0 and (d4[k] - d3[k]) >= 0 and (d5[k] - d6[k]) >= 0:
            w = (d4[k] - d3[k]) / ((d4[k] - d3[k]) + (d5[k] - d6[k]))
            out[k] = b[k] + (c[k] - b[k]) * w
        else:
            den = 1.0 / (va[k] + vb[k] + vc[k])
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
        near = np.argsort(((centre - p) ** 2).sum(1))[:16]
        hits = _closest_on_triangles(p, A[near], B[near], C[near])
        k = int(np.argmin(((hits - p) ** 2).sum(1)))
        n = normals[r]
        ln = np.linalg.norm(n)
        if ln < 1e-9:
            continue
        height = float(np.dot(p - hits[k], n / ln))
        if height <= 1e-5:
            continue
        for v in after[near[k]]:
            v = int(v)
            if v not in locked:
                lifts[v] = min(cap, max(lifts.get(v, 0.0), height))
    return lifts
