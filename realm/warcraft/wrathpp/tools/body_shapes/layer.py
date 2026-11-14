"""The body layer: a layer of its own over a converted character model's front, below the navel, drawn with each
character's own hair texture times a design picked by its display (body options' Style and Density).

  count(m2_or_vertices, skin_bytes, race)            -> how many triangles the layer takes (for refine's reserve)
  add(m2_bytes, skin_bytes, vertices, race, select)  -> (m2_bytes, skin_bytes, info)
  patch(base_m2, made_m2)                            -> the package's patch for a model: the header and what follows the base
  unpatch(base_m2, patch)                            -> made_m2 again (what the app does: WrathppBody.withPatch)

race: {"k": scale against the Human, "fold": the fold's height, "body": the skin's body section ids, "hair_block": the
patch of the race's hair textures (column, row of a 16 x 16 grid) where every colour's strands are} (races.json).

How the game draws it (the 3.3.5a client at the pinned decompilation, docs in README.md):
  - the layer is one skin section, geoset 1901: group 19, which the client's CCharacterComponent::GeosRenderPrep hides
    (0..2000) and nothing of the game's shows; Wrath++'s native mod shows it after GeosRenderPrep when the character
    wears nothing on the legs and its model has the design texture (the display's, below);
  - one batch, two textures: the character's hair (texture type 6, which the character component puts in from its hair
    style and colour), a small patch of its strands (a hair texture is a sheet: strands, braids, clasps, jewellery; the
    patch is where the race's colours differ most, which is the strands), times the design (type 11: the display's TextureVariation_1, which
    CCharacterComponent::ReplaceMonsterSkin puts in from the model's folder) over the layer's square; alpha blended
    (material blend 2) with the texture combiner list (model flag 0x8, header 0x130) [1, 0, 1, 1]: every other batch's
    combiner index 0 (MOD, OPAQUE: as the game sets them without the list), the layer's 2 (MOD, MOD: Combiners_Mod_Mod,
    vertex shader Diffuse_T1_T2: the hair by the first texture coordinates, the design by the second);
  - its vertices are the body's own under it (the same bones and weights) lifted 0.4 mm along the normal, after the
    model's vertices; texture coordinates: the hair patch's middle half over the whole layer, the design's square SPAN x k wide, its top
    TOP x k above the fold, left to right her right to her left as seen from the front.
"""
import struct

import numpy as np

from refine import VERT, read_skin, write_skin

GEOSET = 1901
SPAN, TOP = 0.21, 0.16
GRID = 16
LIFT = 0.0004
MIN_NX = 0.12
HAIR, DESIGN = 6, 11
COMBINERS = (1, 0, 1, 1)
LAYER_COMBINER = 2
FLAG_COMBINERS = 0x8
HEADER = 0x138
MAX_BONES = 64

# the header's arrays this changes (offset: what)
NAME, VERTICES, TEXTURES, REPLACEABLE, MATERIALS = 0x08, 0x3C, 0x50, 0x68, 0x70
BONE_COMBOS, TEX_COMBOS, COORD_COMBOS, WEIGHT_COMBOS, TRANSFORM_COMBOS, COMBINER_COMBOS = 0x78, 0x80, 0x88, 0x90, 0x98, 0x130


def array(m, off):
    return struct.unpack_from("<II", m, off)


def _records(vertices):
    n = len(vertices) // VERT
    rec = np.frombuffer(vertices, np.uint8).reshape(n, VERT)
    P = rec[:, 0:12].copy().view("<f4").reshape(n, 3).astype(np.float64)
    N = rec[:, 20:32].copy().view("<f4").reshape(n, 3).astype(np.float64)
    return rec, P, N


def frame(race):
    span = SPAN * race["k"]
    return span, race["fold"] + TOP * race["k"]


def triangles(P, skb, race):
    """The body's triangles under the layer's square that face the front: model vertex ids (n x 3), and the sections
    they came from."""
    verts, idx, _, secs, _, _, _ = read_skin(skb)
    span, ztop = frame(race)
    zbot = ztop - span
    out, owners = [], []
    for si, s in enumerate(secs):
        if s[0] not in race["body"]:
            continue
        st = s[4] + s[1] * 65536
        T = verts[idx[st:st + s[5]]].reshape(-1, 3)
        p = P[T]
        keep = (p[:, :, 2].max(1) >= zbot) & (p[:, :, 2].min(1) <= ztop) & (np.abs(p[:, :, 1]).min(1) <= span / 2)
        fn = np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0])
        fn /= np.linalg.norm(fn, axis=1, keepdims=True) + 1e-12
        keep &= (fn[:, 0] >= MIN_NX) & (p[:, :, 0].mean(1) >= 0)
        out.append(T[keep]); owners += [si] * int(keep.sum())
    return (np.concatenate(out) if out else np.zeros((0, 3), np.int64)), owners


def count(vertices, skb, race):
    _, P, _ = _records(vertices)
    return len(triangles(P, skb, race)[0])


def _put(blob, base_len, payload):
    """payload appended to the blob (16-byte aligned); its offset in the made file"""
    while (base_len + len(blob)) % 16:
        blob.append(0)
    at = base_len + len(blob)
    blob.extend(payload)
    return at


def add(m2b, skb, vertices, race, select=None):
    """[m2b] with [vertices] (48 bytes each: the model's own or a body shape's) and the layer's after them, its skin
    [skb] (the model's, with room for the layer's indices) with the layer's section and batch after its own. [select]:
    the vertices whose places choose the layer's triangles (default [vertices]): one shape's, so that every shape of a
    model has the same triangles and one skin."""
    if m2b[:4] != b"MD20":
        raise ValueError("not a 3.3.5 model")
    flags = struct.unpack_from("<I", m2b, 0x10)[0]
    if flags & FLAG_COMBINERS:
        raise ValueError("the model has a texture combiner list already")
    if array(m2b, NAME)[1] != 0x130:
        raise ValueError("the model's name isn't where the combiner list goes")
    rec, P, N = _records(vertices)
    nv = len(rec)
    verts, idx, props, secs, batches, bn, mx = read_skin(skb)
    Psel = _records(select)[1] if select is not None else P
    T, owners = triangles(Psel, skb, race)
    if not len(T):
        raise ValueError("no body under the layer")
    span, ztop = frame(race)
    used = np.unique(T.ravel())
    local = {int(g): j for j, g in enumerate(used)}
    # the layer's vertices: the body's own lifted, both texture coordinates its own
    L = rec[used].copy()
    p = P[used] + N[used] * LIFT
    y, z = p[:, 1], p[:, 2]
    uv1 = np.stack([(y + span / 2) / span, (ztop - z) / span], 1)
    bx, by = race["hair_block"]
    uv0 = (np.array([bx, by], np.float64) + 0.25 + 0.5 * np.clip(uv1, 0, 1)) / GRID
    L[:, 0:12] = p.astype("<f4").view(np.uint8).reshape(-1, 12)
    L[:, 32:40] = uv0.astype("<f4").view(np.uint8).reshape(-1, 8)
    L[:, 40:48] = uv1.astype("<f4").view(np.uint8).reshape(-1, 8)
    # one section: its own bone list (the bones the layer's vertices hang on)
    bones = sorted({int(b) for r in L for w, b in zip(r[12:16], r[16:20]) if w})
    if len(bones) > MAX_BONES:
        raise ValueError("the layer hangs on %d bones" % len(bones))
    slot = {b: i for i, b in enumerate(bones)}
    lprops = np.zeros((len(L), 4), np.uint8)
    infl = 1
    for i, r in enumerate(L):
        n = 0
        for j in range(4):
            if r[12 + j]:
                lprops[i, j] = slot[int(r[16 + j])]
                n += 1
        infl = max(infl, n)
    m = bytearray(m2b)
    base_len = (len(m2b) + 15) // 16 * 16
    blob = bytearray()
    # the arrays, old and new
    def old(off, fmt, size):
        n, o = array(m2b, off)
        return [struct.unpack_from(fmt, m2b, o + i * size) for i in range(n)]
    textures = old(TEXTURES, "<IIII", 16)
    tex_combos = [x[0] for x in old(TEX_COMBOS, "<H", 2)]
    coord_combos = [x[0] for x in old(COORD_COMBOS, "<H", 2)]
    weight_combos = [x[0] for x in old(WEIGHT_COMBOS, "<H", 2)]
    transform_combos = [x[0] for x in old(TRANSFORM_COMBOS, "<H", 2)]
    materials = old(MATERIALS, "<HH", 4)
    bone_combos = [x[0] for x in old(BONE_COMBOS, "<H", 2)]
    replaceable = [x[0] for x in old(REPLACEABLE, "<h", 2)]
    hair_tex, design_tex = len(textures), len(textures) + 1
    textures += [(HAIR, 0, 0, 0), (DESIGN, 0, 0, 0)]                 # both clamped
    while len(replaceable) <= DESIGN:
        replaceable.append(-1)
    if replaceable[DESIGN] < 0:
        replaceable[DESIGN] = design_tex
    tc = len(tex_combos); tex_combos += [hair_tex, design_tex]
    cc = len(coord_combos); coord_combos += [0, 1]
    wc = len(weight_combos); weight_combos += [weight_combos[0] if weight_combos else 0] * 2
    xc = len(transform_combos); transform_combos += [0xFFFF, 0xFFFF]
    mat = len(materials); materials.append((0, 2))
    bc = len(bone_combos); bone_combos += bones
    name_n, name_o = array(m2b, NAME)
    name = bytes(m2b[name_o:name_o + name_n])
    struct.pack_into("<II", m, NAME, name_n, _put(blob, base_len, name))
    struct.pack_into("<II", m, VERTICES, nv + len(L), _put(blob, base_len, bytes(rec.tobytes()) + bytes(L.tobytes())))
    struct.pack_into("<II", m, TEXTURES, len(textures), _put(blob, base_len, b"".join(struct.pack("<IIII", *t) for t in textures)))
    struct.pack_into("<II", m, REPLACEABLE, len(replaceable), _put(blob, base_len, struct.pack("<%dh" % len(replaceable), *replaceable)))
    struct.pack_into("<II", m, MATERIALS, len(materials), _put(blob, base_len, b"".join(struct.pack("<HH", *x) for x in materials)))
    for off, values in ((BONE_COMBOS, bone_combos), (TEX_COMBOS, tex_combos), (COORD_COMBOS, coord_combos),
                        (WEIGHT_COMBOS, weight_combos), (TRANSFORM_COMBOS, transform_combos), (COMBINER_COMBOS, list(COMBINERS))):
        struct.pack_into("<II", m, off, len(values), _put(blob, base_len, struct.pack("<%dH" % len(values), *values)))
    struct.pack_into("<I", m, 0x10, flags | FLAG_COMBINERS)
    # the skin: the layer's vertices, triangles, section and batch after the model's own; every other batch's combiner 0
    nsv = len(verts)
    verts2 = np.concatenate([verts, nv + np.arange(len(L))])
    props2 = np.concatenate([props, lprops])
    ist = len(idx)
    idx2 = np.concatenate([idx, np.array([nsv + local[int(g)] for g in T.ravel()], np.int64)])
    if ist > 0xFFFF:
        raise ValueError("the layer would start past the game's 65535 indices (%d)" % ist)
    if len(idx2) > 0xFFFF:
        raise ValueError("the skin has %d indices with the layer: refine with a larger reserve" % len(idx2))
    if len(verts2) > 0xFFFF:
        raise ValueError("too many skin vertices")
    centre = Psel[used].mean(0)                                    # (the selecting shape's: one skin for every shape)
    radius = float(np.linalg.norm(Psel[used] - centre, axis=1).max())
    # the bone the layer hangs on most
    weight = {}
    for r in L:
        for w, b in zip(r[12:16], r[16:20]):
            if w:
                weight[int(b)] = weight.get(int(b), 0) + int(w)
    centre_bone = max(weight, key=weight.get)
    sec = [GEOSET, 0, nsv, len(L), ist, len(T) * 3, len(bones), bc, infl, centre_bone] + list(centre) + list(centre) + [radius]
    secs2 = [list(s) for s in secs] + [sec]
    B = [list(struct.unpack_from("<BbHHHHHHHHHHH", batches, i * 24)) for i in range(bn)]
    source = next(b for b in B if secs[b[3]][0] == secs[owners[0]][0])
    for b in B:
        b[2] = 0
    layer = list(source)
    layer[1] = 0
    layer[2] = LAYER_COMBINER
    layer[3] = layer[4] = len(secs2) - 1
    layer[6] = mat
    layer[7] = 0
    layer[8] = 2
    layer[9], layer[10], layer[11], layer[12] = tc, cc, wc, xc
    B.append(layer)
    bbytes = b"".join(struct.pack("<BbHHHHHHHHHHH", *b) for b in B)
    skin = write_skin(verts2, idx2, props2, secs2, bbytes, len(B), max(mx, len(bones)))
    while len(m) < base_len:
        m.append(0)
    made = bytes(m) + bytes(blob)
    return made, skin, {"triangles": len(T), "vertices": len(L), "bones": len(bones), "indices": len(idx2), "skin_vertices": len(verts2)}


def patch(base, made):
    """What turns [base] into [made]: the header, and what [made] has after [base] (16-byte aligned)."""
    at = (len(base) + 15) // 16 * 16
    if made[HEADER:len(base)] != base[HEADER:]:
        raise ValueError("the made model changed the base past its header")
    return made[:HEADER] + made[at:]


def unpatch(base, p):
    at = (len(base) + 15) // 16 * 16
    return p[:HEADER] + base[HEADER:] + bytes(at - len(base)) + p[HEADER:]
