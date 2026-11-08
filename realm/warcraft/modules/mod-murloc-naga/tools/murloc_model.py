#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""The murlocs' character model and textures (tools/murloc_looks.py says what they are): Blizzard's
newer murloc made a model the 3.3.5 game draws as a character's: its body in each skin colour, its eyes
in each eye colour, its fins in each style and colour, its kin's parts as features.

    python3 tools/murloc_model.py fetch DIR          fetches the game's files from wago.tools by their
                                                      ids and writes the murlocs' files into DIR
    python3 tools/murloc_model.py convert SRC DIR    the same from files already fetched (named by id)

The files are the game's, so they are never in this repository: the server package makes them
(scripts/package-azerothcore.sh) into the module's data/files, where the world server finds them
(src/MurlocNagaPatch.cpp puts them in the game's patch-<locale>-T with the module's tables). The list
of them, murloc.files, is written last.

What's made:
  - Character/Murloc/<Sex>/Murloc<Sex>.m2, its 00.skin and .anim files: murloc2 as Wrath Remix's
    converter makes the newer format 3.3.5's (mod-wrath-remix/tools/models.py), then
      - its body and eyes drawn with the character's composed texture (type 1), their texture
        coordinates moved into its face region (murloc_looks.BODY_BLOCK and EYE_BLOCK), which the
        face rows fill: the only part of it no armour is drawn into;
      - its fins (the triangles of its body whose texture, in the blue skin, is the fins' gold) cut
        from the body and drawn with the character's hair texture (type 6), a geoset a fin style:
        its own spines as they are, shorter, longer, swept back, and other models' (the classic
        murloc's crest, the deep sea murloc's sail);
      - what's on its eyes' own bones put on the head's (their animations draw the eyes into the
        head as it stands);
      - the parts its kin lend (their vertices, bones taken to murloc2's at the same places: a bone
        it hasn't, to its nearest parent it has), geosets of group 1: the features;
  - Character/Murloc/MurlocBase.blp: the composed texture's base (512 x 512, palettized, as the
    game composes only those): one colour, under the face region;
  - Character/Murloc/MurlocBody<NN>.blp: FaceLower (256 x 128, palettized): a skin's body;
  - Character/Murloc/MurlocEyes<EE>_<NN>.blp: FaceUpper (256 x 64, palettized): an eye colour's eyes
    beside a skin's body;
  - Character/Murloc/MurlocFins[<Style>]<NN>.blp: the fins' textures, a fin colour's (murloc2's own
    fins one each; another model's fins one each of theirs);
  - Character/Murloc/Murloc<Part>.blp: the parts' textures (the game's).
"""
import os
import struct
import sys
import time
import urllib.request

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "mod-wrath-remix", "tools"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "mod-allied-races", "tools"))
import murloc_anims  # noqa: E402
import murloc_looks as L  # noqa: E402
import models  # noqa: E402
import blp  # noqa: E402
import importlib.util  # noqa: E402

# The starting areas' list of a 3.3.5 model's animation tracks (mod-worgen-goblin/tools/zones/package.py).
_ZONES = os.path.join(HERE, "..", "..", "mod-worgen-goblin", "tools", "zones")
sys.path.insert(0, _ZONES)
_spec = importlib.util.spec_from_file_location("zones_package", os.path.join(_ZONES, "package.py"))
zones_package = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(zones_package)


def one_set_a_sequence(data):
    """A track with one set of keys for every sequence (the newer format's way) given one set a
    sequence, as 3.3.5 reads it (the set of the sequence playing): the one set for the first sequence
    and every other kept in the model, none for a sequence kept in its own .anim file (its flag 0x20,
    at its record's byte 12, says it's in the model). Returns how many tracks changed."""
    sequences, seq_at = struct.unpack_from("<II", data, 28)
    in_model = [bool(struct.unpack_from("<I", data, seq_at + 64 * k + 12)[0] & 0x20) for k in range(sequences)]
    changed = 0

    def append(block):
        while len(data) % 16:
            data.append(0)
        at = len(data)
        data.extend(block)
        return at
    for at, has_values in zones_package.m2_tracks(bytes(data)):
        gseq, count, offset = struct.unpack_from("<hII", data, at + 2)
        if gseq >= 0 or count != 1 or sequences < 2:
            continue
        stamps = struct.unpack_from("<II", data, offset)
        vcount, voffset = struct.unpack_from("<II", data, at + 12)
        values = struct.unpack_from("<II", data, voffset) if vcount == 1 else (0, 0)
        keep = [in_model[k] or k == 0 for k in range(sequences)]
        struct.pack_into("<II", data, at + 4, sequences, append(b"".join(struct.pack("<II", *(stamps if keep[k] else (0, 0))) for k in range(sequences))))
        if has_values and vcount == 1:
            struct.pack_into("<II", data, at + 12, sequences, append(b"".join(struct.pack("<II", *(values if keep[k] else (0, 0))) for k in range(sequences))))
        changed += 1
    return changed

USER_AGENT = "YeaBwoi-build/1.0 (+https://github.com/logie-github/YeaBwoi)"
MANIFEST = "murloc.files"
FOLDER = "Character/Murloc"
MAX_BONES = 64
# the 3.3.5 header's arrays
H_VERTS, H_TEXTURES, H_TEX_REPLACE, H_RENDER_FLAGS, H_BONE_LOOKUP, H_TEX_LOOKUP = 0x3C, 0x50, 0x68, 0x70, 0x78, 0x80
H_TEX_UNIT_LOOKUP, H_TRANSP_LOOKUP, H_UV_LOOKUP, H_BOUNDS, H_BONES = 0x88, 0x90, 0x98, 0xA0, 0x2C
TYPE_HARDCODED, TYPE_SKIN, TYPE_HAIR, TYPE_CREATURE = 0, 1, 6, 11
CREATURE_FOLDER = "Creature/MurlocTribe"


def wago(file_id):
    for attempt in range(4):
        try:
            request = urllib.request.Request("https://wago.tools/api/casc/%d?download" % file_id, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.read()
        except Exception as error:  # a network hiccup: once more, a little later
            print("murloc: file %d: %s" % (file_id, error), file=sys.stderr)
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("file %d couldn't be fetched" % file_id)


def cached(folder, fetch):
    def read(file_id):
        path = os.path.join(folder, str(file_id)) if folder else None
        if path and os.path.exists(path) and os.path.getsize(path):
            with open(path, "rb") as f:
                return f.read()
        if fetch is None:
            raise FileNotFoundError(file_id)
        data = fetch(file_id)
        if path:
            os.makedirs(folder, exist_ok=True)
            with open(path + ".part", "wb") as f:
                f.write(data)
            os.replace(path + ".part", path)
        return data
    return read


# The newer format, read --------------------------------------------------------------------------

class Source:
    """A model of the newer format: its vertices, bones and first skin, as numbers."""

    def __init__(self, read, file_id):
        data = read(file_id)
        self.chunks = models.chunks_of(data)
        self.m = self.chunks["MD21"]
        m = self.m
        nv, ov = struct.unpack_from("<II", m, H_VERTS)
        self.raw = np.frombuffer(m[ov:ov + 48 * nv], dtype=np.uint8).reshape(nv, 48).copy()
        self.pos = self.raw[:, 0:12].copy().view("<f4").reshape(nv, 3)
        nb, ob = struct.unpack_from("<II", m, H_BONES)
        self.parent = [struct.unpack_from("<h", m, ob + 88 * i + 8)[0] for i in range(nb)]
        self.key = [struct.unpack_from("<i", m, ob + 88 * i)[0] for i in range(nb)]
        self.pivot = np.array([struct.unpack_from("<3f", m, ob + 88 * i + 76) for i in range(nb)])
        sfid = struct.unpack("<%dI" % (len(self.chunks["SFID"]) // 4), self.chunks["SFID"])
        self.skin = read(sfid[0])
        s = self.skin
        sv_n, sv_o = struct.unpack_from("<II", s, 4)
        ix_n, ix_o = struct.unpack_from("<II", s, 12)
        pr_n, pr_o = struct.unpack_from("<II", s, 20)
        se_n, se_o = struct.unpack_from("<II", s, 28)
        ba_n, ba_o = struct.unpack_from("<II", s, 36)
        self.skin_vertices = np.array(struct.unpack_from("<%dH" % sv_n, s, sv_o))
        self.indices = np.array(struct.unpack_from("<%dH" % ix_n, s, ix_o))
        self.props = np.frombuffer(s[pr_o:pr_o + 4 * pr_n], dtype=np.uint8).reshape(pr_n, 4)
        self.sections = [struct.unpack_from("<10H7f", s, se_o + 48 * i) for i in range(se_n)]
        self.batches = [struct.unpack_from("<BbHHHhHHHHHHH", s, ba_o + 24 * i) for i in range(ba_n)]
        lc, lo = struct.unpack_from("<II", m, H_BONE_LOOKUP)
        self.lookup = struct.unpack_from("<%dH" % lc, m, lo)
        rc, ro = struct.unpack_from("<II", m, H_RENDER_FLAGS)
        self.materials = [m[ro + 4 * i:ro + 4 * i + 4] for i in range(rc)]
        # each model vertex's bones (global) through the skin's sections, with its weights
        self.bones = np.zeros((nv, 4), dtype=np.int32)
        for sec in self.sections:
            vs, vc, combo = sec[2] + 65536 * sec[1], sec[3], sec[7]
            for k in range(vs, vs + vc):
                g = self.skin_vertices[k]
                for j in range(4):
                    self.bones[g, j] = self.lookup[combo + self.props[k, j]] if self.raw[g, 12 + j] else 0

    def batch_triangles(self, index):
        b = self.batches[index]
        sec = self.sections[b[3]]
        first = sec[4] + 65536 * sec[1]
        return self.skin_vertices[self.indices[first:first + sec[5]]].reshape(-1, 3), b

    def under(self, bone, root):
        while bone >= 0:
            if bone == root:
                return True
            bone = self.parent[bone]
        return False


def pieces(src, triangles):
    """The batch's connected pieces (vertices at one place joined), each a list of triangle rows."""
    weld = {}
    ids = np.zeros(len(src.pos), dtype=np.int64)
    for v in np.unique(triangles):
        ids[v] = weld.setdefault(tuple(np.round(src.pos[v], 4)), len(weld))
    parent = list(range(len(weld)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for t in triangles:
        a = find(ids[t[0]])
        for v in t[1:]:
            b = find(ids[v])
            if b != a:
                parent[b] = a
    groups = {}
    for i, t in enumerate(triangles):
        groups.setdefault(find(ids[t[0]]), []).append(i)
    return [np.array(g) for g in groups.values()]


def part_triangles(src, base, spec):
    """The triangles (source vertex indices) of a part (murloc_looks.PARTS)."""
    triangles, batch = src.batch_triangles(spec["batch"])
    take = spec["take"]
    kind = take[0]
    if kind in ("top", "below", "centre"):
        keep = []
        for group in pieces(src, triangles):
            vs = np.unique(triangles[group])
            if kind == "top" and src.pos[vs, 2].max() > take[1]:
                keep.extend(group)
            elif kind == "below" and src.pos[vs, 2].max() <= take[1]:
                keep.extend(group)
            elif kind == "centre":
                c = src.pos[vs].mean(axis=0)
                x0, x1, y0, y1, z0, z1 = take[1:]
                if x0 <= c[0] <= x1 and y0 <= c[1] <= y1 and z0 <= c[2] <= z1 and len(group) < 1000:
                    keep.extend(group)
        return triangles[sorted(keep)], batch
    dominant = src.bones[np.arange(len(src.pos)), src.raw[:, 12:16].argmax(axis=1)]
    if kind in ("head", "body"):
        head = src.key.index(6)
        on_head = np.array([all(src.under(dominant[v], head) for v in t) for t in triangles])
        return triangles[on_head if kind == "head" else ~on_head], batch
    if kind == "added":
        extra = set(int(b) for b in np.where(np.linalg.norm(src.pivot[:, None] - base.pivot[None], axis=2).min(axis=1) > 0.01)[0])
        x0, x1, y0, y1, z0, z1 = take[1:]
        keep = []
        for i, t in enumerate(triangles):
            c = src.pos[t].mean(axis=0)
            if all(int(dominant[v]) in extra for v in t) and x0 <= c[0] <= x1 and y0 <= c[1] <= y1 and z0 <= c[2] <= z1:
                keep.append(i)
        return triangles[keep], batch
    raise ValueError("a part taken by %r" % (kind,))


def bone_map(src, base):
    """Each of [src]'s bones as murloc2's: the one at its place, else its nearest parent's that is,
    else (none of its parents at one) the murloc2 bone nearest it."""
    out = []
    for b in range(len(src.pivot)):
        a = b
        while True:
            d = np.linalg.norm(base.pivot - src.pivot[a], axis=1)
            if d.min() < 0.01:
                out.append(int(d.argmin()))
                break
            a = src.parent[a]
            if a < 0:
                out.append(int(np.linalg.norm(base.pivot - src.pivot[b], axis=1).argmin()))
                break
    return out


# The model, made ---------------------------------------------------------------------------------

def build_skin(blob, raw, vbones, parts):
    """3.3.5's skin for [parts] (geoset, triangles of model vertices, texture lookup index, material
    index, priority): sections of at most MAX_BONES bones, their batches; the model's bone lookup."""
    out_vertices, out_props, out_indices, out_sections, out_batches, out_lookup = [], [], [], [], [], []
    for geoset, triangles, texture, material, priority in parts:
        groups = []
        for tri in triangles:
            used = {int(vbones[v, j]) for v in tri for j in range(4) if raw[v, 12 + j]}
            if not groups or len(set(groups[-1][0]) | used) > MAX_BONES:
                groups.append([[], []])
            palette = groups[-1][0]
            for b in sorted(used):
                if b not in palette:
                    palette.append(b)
            groups[-1][1].append(tri)
        for palette, tris in groups:
            place = {}
            vertex_start, index_start = len(out_vertices), len(out_indices)
            influences = 0
            centre = raw[np.unique(np.array(tris)), 0:12].copy().view("<f4").reshape(-1, 3).mean(axis=0)
            for tri in tris:
                for v in tri:
                    if v not in place:
                        place[v] = len(out_vertices)
                        out_vertices.append(int(v))
                        slot = [0, 0, 0, 0]
                        n = 0
                        for j in range(4):
                            if raw[v, 12 + j]:
                                slot[j] = palette.index(int(vbones[v, j]))
                                n += 1
                        influences = max(influences, n)
                        out_props.append(bytes(slot))
                    out_indices.append(place[v])
            combo = len(out_lookup)
            out_lookup.extend(palette)
            radius = float(np.linalg.norm(raw[np.unique(np.array(tris)), 0:12].copy().view("<f4").reshape(-1, 3) - centre, axis=1).max())
            out_sections.append(struct.pack("<10H7f", geoset, index_start >> 16, vertex_start & 0xFFFF, len(place),
                                            index_start & 0xFFFF, len(tris) * 3, len(palette), combo, max(1, influences),
                                            palette[0] if palette else 0, *centre, *centre, radius))
            # flags 16 (as 3.3.5's own), shader 0, one texture, no texture transform, first transparency
            out_batches.append(struct.pack("<BbHHHhHHHHHHH", 16, priority, 0, len(out_sections) - 1, len(out_sections) - 1,
                                           -1, material, 0, 1, texture, 0, 0, 0))
    if len(out_vertices) > 65535:
        raise ValueError("too many vertices for one skin")
    header = 48
    body = bytearray()

    def place(payload):
        while (header + len(body)) % 16:
            body.append(0)
        at = header + len(body)
        body.extend(payload)
        return at
    arrays = [
        (len(out_vertices), place(struct.pack("<%dH" % len(out_vertices), *out_vertices))),
        (len(out_indices), place(struct.pack("<%dH" % len(out_indices), *out_indices))),
        (len(out_props), place(b"".join(out_props))),
        (len(out_sections), place(b"".join(out_sections))),
        (len(out_batches), place(b"".join(out_batches))),
    ]
    head = bytearray(b"SKIN")
    for count, offset in arrays:
        head += struct.pack("<II", count, offset)
    head += struct.pack("<I", MAX_BONES)
    blob.set_array(H_BONE_LOOKUP, len(out_lookup), blob.append(struct.pack("<%dH" % len(out_lookup), *out_lookup)))
    return bytes(head) + bytes(body)


def fin_triangles(base, triangles, skin):
    """Which of the body's [triangles] are its fins: those whose texture, in the skin [skin] (RGBA,
    murloc_looks.FIN_SKIN's), is the fins' colour at three of four places (its centre, and toward
    each corner)."""
    h, w = skin.shape[:2]
    hue, light, sat = hls(skin)
    mask = (hue > L.FIN_HUE[0]) & (hue < L.FIN_HUE[1]) & (sat > L.FIN_SATURATION) & (light > L.FIN_LIGHTNESS)
    uv = base.raw[:, 32:40].copy().view("<f4").reshape(-1, 2)
    out = np.zeros(len(triangles), dtype=bool)
    for i, t in enumerate(triangles):
        centre = uv[t].mean(axis=0)
        places = [centre] + [uv[v] * 0.6 + centre * 0.4 for v in t]
        out[i] = sum(bool(mask[int(np.clip(p[1] * h, 0, h - 1)), int(np.clip(p[0] * w, 0, w - 1))]) for p in places) >= 3
    return out


def fin_roots(base, fin_tris, body_vertices):
    """For each fin vertex, its root: the nearest vertex of its spine at a place the body has too (where
    the spine joins the body); a spine that doesn't join it, its own vertex nearest the body."""
    pos = base.pos
    on_body = {tuple(np.round(pos[v], 4)) for v in body_vertices}
    body_pos = pos[np.array(sorted(body_vertices))]
    out = {}
    for group in pieces(base, fin_tris):
        vs = np.unique(fin_tris[group])
        roots = [v for v in vs if tuple(np.round(pos[v], 4)) in on_body]
        if not roots:
            roots = [vs[np.array([np.linalg.norm(body_pos - pos[v], axis=1).min() for v in vs]).argmin()]]
        places = pos[np.array(roots)]
        for v in vs:
            out[int(v)] = places[np.linalg.norm(places - pos[v], axis=1).argmin()]
    return out


def reshaped(pos, roots, scale, sweep):
    """Fin vertices' places, each spine [scale] times as long from its root and swept [sweep] degrees
    back (about the side-to-side axis: x is forward, z up)."""
    a = np.radians(sweep)
    c, s = np.cos(a), np.sin(a)
    out = pos.copy()
    for i, root in enumerate(roots):
        d = pos[i] - root
        d = np.array([d[0] * c - d[2] * s, d[1], d[0] * s + d[2] * c])
        out[i] = root + d * scale
    return out


def make_model(read, sex, creature=False):
    """The murloc's model for [sex] (its skin, .anim files and the parts' texture ids by name); or, with
    [creature], the tribe's people's: murloc2 whole, drawn with a creature's skin (its look's texture:
    every skin of the game's, as it is), with the same eyes and emotes."""
    name = "MurlocTribe" if creature else "Murloc" + sex
    folder = CREATURE_FOLDER if creature else "%s/%s" % (FOLDER, sex)
    models.NAME, models.FOLDER = name, folder
    base = Source(read, L.BASE_MODEL)
    models.SHOWN_GEOSETS = {s[0] for s in base.sections}
    m2 = read(L.BASE_MODEL)
    model, _, needed, anims = models.convert_model(m2, base.skin)
    blob = models.Blob(model)

    # The base's own triangles: the eyes (the smaller batch) and the body, its fins cut from it.
    own = sorted((base.batch_triangles(i) for i in range(len(base.batches))), key=lambda tb: len(tb[0]))
    eyes, body = own[0], own[-1]
    fin = fin_triangles(base, body[0], rgba(read, L.SKINS[L.FIN_SKIN][0])) if not creature else np.zeros(len(body[0]), dtype=bool)
    body_triangles, fin_tris = body[0][~fin], body[0][fin]

    # The eyes' own bones (the eyeballs' and the lids'): their animations draw the eyes back into the
    # head (the eyeballs, the eye colour, hidden as the murloc stands), so what's on them is on the
    # head's bone, the eyes where the model has them, moving with the head.
    head = base.key.index(6)
    eye_vertices = np.unique(eyes[0])
    eye_bones = {int(b) for v in eye_vertices for j, b in enumerate(base.bones[v]) if base.raw[v, 12 + j]} - {head}

    raw = base.raw.copy()
    vbones = base.bones.copy()
    uv = raw[:, 32:40].copy().view("<f4").reshape(-1, 2)

    def add(rows, bones):
        nonlocal raw, vbones
        first = len(raw)
        raw = np.concatenate([raw, rows])
        vbones = np.concatenate([vbones, bones])
        return first

    def set_uv(rows, coordinates):
        rows[:, 32:40] = np.asarray(coordinates, dtype="<f4").view(np.uint8).reshape(-1, 8)

    # The body reads the composed texture's body block (its texture coordinates, 0 to 1 of the skin,
    # into the block, a texel in from its edges).
    x0, y0, x1, y1 = L.BODY_BLOCK
    body_vertices = np.unique(body_triangles)
    if creature:
        return creature_model(blob, base, raw, vbones, eye_bones, head, body, eyes, read, needed, anims)
    block = np.empty((len(body_vertices), 2))
    block[:, 0] = (x0 + 0.5 + np.clip(uv[body_vertices, 0], 0, 1) * (x1 - x0 - 1)) / L.COMPOSED
    block[:, 1] = (y0 + 0.5 + np.clip(uv[body_vertices, 1], 0, 1) * (y1 - y0 - 1)) / L.COMPOSED
    rows = raw[body_vertices]
    set_uv(rows, block)
    raw[body_vertices] = rows

    # The eyes read the eye block (their own vertices: from the skin's eye region to it).
    u0, v0, u1, v1 = L.EYES
    x0, y0, x1, y1 = L.EYE_BLOCK
    rows = base.raw[eye_vertices].copy()
    coordinates = np.empty((len(eye_vertices), 2))
    coordinates[:, 0] = (x0 + 0.5 + np.clip((uv[eye_vertices, 0] - u0) / (u1 - u0), 0, 1) * (x1 - x0 - 1)) / L.COMPOSED
    coordinates[:, 1] = (y0 + 0.5 + np.clip((uv[eye_vertices, 1] - v0) / (v1 - v0), 0, 1) * (y1 - y0 - 1)) / L.COMPOSED
    set_uv(rows, coordinates)
    first = add(rows, base.bones[eye_vertices])
    at = {int(v): first + i for i, v in enumerate(eye_vertices)}
    eye_triangles = np.vectorize(lambda v: at[int(v)])(eyes[0])

    # textures: the composed texture, the hair (the fins' colour), then each part's own
    textures = [(TYPE_SKIN, ""), (TYPE_HAIR, "")]
    part_textures = {}
    parts = [(0, body_triangles, 0, body[1][6], 0), (0, eye_triangles, 0, eyes[1][6], 0)]
    materials = list(base.materials)
    sources = {}

    def source(file_id):
        if file_id not in sources:
            sources[file_id] = Source(read, file_id)
        return sources[file_id]

    def transplant(src, tris):
        """[src]'s triangles' vertices added on murloc2's bones; the triangles, renumbered."""
        mapping = bone_map(src, base)
        vs = np.unique(tris)
        rows = src.raw[vs].copy()
        bones = np.array([[mapping[int(src.bones[v, j])] for j in range(4)] for v in vs], dtype=np.int32)
        for i in range(len(vs)):                       # (the vertex's own bone indices, the model's)
            if bones.max() < 256:
                rows[i, 16:20] = np.array([b if rows[i, 12 + j] else 0 for j, b in enumerate(bones[i])], dtype=np.uint8)
        first = add(rows, bones)
        at = {int(v): first + i for i, v in enumerate(vs)}
        return np.vectorize(lambda v: at[int(v)])(tris)

    def material(src, batch):
        mat = src.materials[batch[6]] if batch[6] < len(src.materials) else b"\0\0\0\0"
        if mat not in materials:
            materials.append(mat)
        return materials.index(mat)

    # The fins, a geoset a style, drawn with the hair texture.
    fin_vertices = np.unique(fin_tris)
    roots = fin_roots(base, fin_tris, body_vertices)
    for style, (_, how) in enumerate(L.FIN_STYLES):
        geoset = L.fin_geoset(style)
        if how.get("own"):
            rows = base.raw[fin_vertices].copy()
            places = reshaped(base.pos[fin_vertices], [roots[int(v)] for v in fin_vertices], how["scale"], how["sweep"])
            rows[:, 0:12] = places.astype("<f4").view(np.uint8).reshape(-1, 12)
            first = add(rows, base.bones[fin_vertices])
            at = {int(v): first + i for i, v in enumerate(fin_vertices)}
            parts.append((geoset, np.vectorize(lambda v: at[int(v)])(fin_tris), 1, body[1][6], 0))
        else:
            src = source(how["model"])
            tris, batch = part_triangles(src, base, {"batch": how["batch"], "take": ("top", how["z"])})
            if not len(tris):
                raise ValueError("%s: no fins taken" % how["name"])
            parts.append((geoset, transplant(src, tris), 1, material(src, batch), 0))

    # The features, a geoset each (none, the first, has none).
    for feature, (_, names) in enumerate(L.FEATURES[sex]):
        geoset = 100 + L.feature_geoset(feature)
        for part in names:
            spec = L.PARTS[part]
            src = source(spec["model"])
            tris, batch = part_triangles(src, base, spec)
            if not len(tris):
                raise ValueError("%s: no triangles taken" % part)
            key = spec["texture"]
            if key not in part_textures:
                part_textures[key] = len(textures)
                textures.append((TYPE_HARDCODED, "%s\\Murloc%s.blp" % (FOLDER.replace("/", "\\"), L.TEXTURE_NAMES[key])))
            parts.append((geoset, transplant(src, tris), part_textures[key], material(src, batch), 0))

    # (the eyes' bones, the head's; each vertex's bone indices, the model's)
    vbones[np.isin(vbones, sorted(eye_bones))] = head
    if vbones.max() < 256:
        raw[:, 16:20] = np.where(raw[:, 12:16] > 0, vbones, 0).astype(np.uint8)

    # the arrays the header names, made again
    blob.set_array(H_VERTS, len(raw), blob.append(raw.tobytes()))
    tex_bytes, names = bytearray(), {"": blob.append(b"\0")}
    for kind, path in textures:
        if path not in names:
            names[path] = blob.append(path.encode() + b"\0")
    for kind, path in textures:
        tex_bytes += struct.pack("<IIII", kind, 0, len(path) + 1, names[path])
    blob.set_array(H_TEXTURES, len(textures), blob.append(bytes(tex_bytes)))
    blob.set_array(H_TEX_LOOKUP, len(textures), blob.append(struct.pack("<%dh" % len(textures), *range(len(textures)))))
    replace = [-1] * (max(k for k, _ in textures) + 1)
    for i, (kind, _) in enumerate(textures):
        if kind and replace[kind] < 0:
            replace[kind] = i
    blob.set_array(H_TEX_REPLACE, len(replace), blob.append(struct.pack("<%dh" % len(replace), *replace)))
    blob.set_array(H_RENDER_FLAGS, len(materials), blob.append(b"".join(materials)))
    count, _ = blob.array(H_TRANSP_LOOKUP)
    if count == 0:
        blob.set_array(H_TRANSP_LOOKUP, 1, blob.append(struct.pack("<h", 0)))
    blob.set_array(H_UV_LOOKUP, 1, blob.append(struct.pack("<h", -1)))
    skin = build_skin(blob, raw, vbones, parts)
    pos = raw[:, 0:12].copy().view("<f4").reshape(-1, 3)
    lo, hi = pos.min(axis=0), pos.max(axis=0)
    struct.pack_into("<6ff", blob.data, H_BOUNDS, *lo, *hi, float(np.linalg.norm(hi - lo) / 2))
    one_set_a_sequence(blob.data)
    add_emotes(blob.data, read)
    return bytes(blob.data), skin, anims, needed, part_textures


def add_emotes(data, read):
    """The costume's emotes on murloc2 (tools/murloc_anims.py), their moves at murloc2's height."""
    costume = models.chunks_of(read(L.COSTUME_MODEL))["MD21"]
    nb, ob = struct.unpack_from("<II", costume, H_BONES)
    tall = max(struct.unpack_from("<f", costume, ob + 88 * i + 84)[0] for i in range(nb))
    nb, ob = struct.unpack_from("<II", data, H_BONES)
    ours = max(struct.unpack_from("<f", data, ob + 88 * i + 84)[0] for i in range(nb))
    added, sets = murloc_anims.add_emotes(data, costume, scale=ours / tall)
    if len(added) < 20 or sets < 200:
        raise ValueError(f"the costume's emotes didn't take ({len(added)} sequences, {sets} sets)")


def creature_model(blob, base, raw, vbones, eye_bones, head, body, eyes, read, needed, anims):
    """The tribe's people's murloc: the body and eyes with the creature's skin (its own coordinates)."""
    parts = [(0, body[0], 0, body[1][6], 0), (0, eyes[0], 0, eyes[1][6], 0)]
    vbones[np.isin(vbones, sorted(eye_bones))] = head
    if vbones.max() < 256:
        raw[:, 16:20] = np.where(raw[:, 12:16] > 0, vbones, 0).astype(np.uint8)
    blob.set_array(H_VERTS, len(raw), blob.append(raw.tobytes()))
    names = {"": blob.append(b"\0")}
    blob.set_array(H_TEXTURES, 1, blob.append(struct.pack("<IIII", TYPE_CREATURE, 0, 1, names[""])))
    blob.set_array(H_TEX_LOOKUP, 1, blob.append(struct.pack("<h", 0)))
    replace = [-1] * (TYPE_CREATURE + 1)
    replace[TYPE_CREATURE] = 0
    blob.set_array(H_TEX_REPLACE, len(replace), blob.append(struct.pack("<%dh" % len(replace), *replace)))
    blob.set_array(H_RENDER_FLAGS, len(base.materials), blob.append(b"".join(base.materials)))
    count, _ = blob.array(H_TRANSP_LOOKUP)
    if count == 0:
        blob.set_array(H_TRANSP_LOOKUP, 1, blob.append(struct.pack("<h", 0)))
    blob.set_array(H_UV_LOOKUP, 1, blob.append(struct.pack("<h", -1)))
    skin = build_skin(blob, raw, vbones, parts)
    one_set_a_sequence(blob.data)
    add_emotes(blob.data, read)
    return bytes(blob.data), skin, anims, needed, {}


# The textures ------------------------------------------------------------------------------------

def rgba(read, file_id):
    return np.asarray(blp.read(read(file_id)), dtype=np.uint8)


def hls(image):
    """Hue, lightness and saturation (0 to 1) of each pixel of an RGBA image."""
    np.seterr(divide="ignore", invalid="ignore")
    rgb = image[:, :, :3].astype(np.float64) / 255.0
    hi, lo = rgb.max(axis=2), rgb.min(axis=2)
    light = (hi + lo) / 2
    span = hi - lo
    sat = np.where(span == 0, 0, span / np.where(light < 0.5, hi + lo, 2 - hi - lo + 1e-12))
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    safe = np.where(span == 0, 1, span)
    hue = np.where(hi == r, ((g - b) / safe) % 6, np.where(hi == g, (b - r) / safe + 2, (r - g) / safe + 4)) / 6
    return np.where(span == 0, 0, hue), light, sat


def from_hls(hue, light, sat):
    """hls's inverse: an RGB image (uint8)."""
    q = np.where(light < 0.5, light * (1 + sat), light + sat - light * sat)
    p = 2 * light - q

    def channel(t):
        t = t % 1.0
        return np.where(t < 1 / 6, p + (q - p) * 6 * t, np.where(t < 0.5, q, np.where(t < 2 / 3, p + (q - p) * (2 / 3 - t) * 6, p)))
    rgb = np.stack([channel(hue + 1 / 3), channel(hue), channel(hue - 1 / 3)], axis=2)
    return np.clip(np.round(rgb * 255), 0, 255).astype(np.uint8)


def hls_recolour(image, hue, saturation, lightness):
    """[image] (RGBA) with every pixel's hue made [hue] (below 0, kept), its saturation and lightness
    multiplied."""
    h, l, s = hls(image)
    out = image.copy()
    out[:, :, :3] = from_hls(h if hue < 0 else np.full_like(h, hue), np.clip(l * lightness, 0, 1), np.clip(s * saturation, 0, 1))
    return out


def recipe(image, hue, saturation, lightness):
    return image if hue < 0 and saturation == 1 and lightness == 1 else hls_recolour(image, hue, saturation, lightness)


def resized(image, width, height):
    return np.asarray(Image.fromarray(image).resize((width, height), Image.Resampling.LANCZOS)).copy()


def uv_mask(src, triangles, width, height):
    """The texels [triangles] of [src] read (a mask, [height] x [width])."""
    from PIL import ImageDraw
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    uv = src.raw[:, 32:40].copy().view("<f4").reshape(-1, 2)
    for t in triangles:
        draw.polygon([(float(uv[v, 0] * width), float(uv[v, 1] * height)) for v in t], fill=255)
    return np.asarray(mask) > 0


def median_hls(image, mask):
    h, l, s = hls(image)
    return float(np.median(h[mask])), float(np.median(l[mask])), float(np.median(s[mask]))


def face_textures(read):
    """The composed texture's face region's textures: FaceLower a skin colour's (its body's lower
    part), FaceUpper an eye colour's and a skin colour's (the eyes, beside the body's upper part)."""
    files = {}
    x0, y0, x1, y1 = L.BODY_BLOCK
    fx0, fy0, fx1, fy1 = L.FACE_UPPER
    lx0, ly0, lx1, ly1 = L.FACE_LOWER
    ex0, ey0, ex1, ey1 = L.EYE_BLOCK
    eyes = []
    for _, skin, hue, saturation, lightness in L.EYE_COLOURS:
        image = rgba(read, L.SKINS[skin][0])
        h, w = image.shape[:2]
        u0, v0, u1, v1 = L.EYES
        crop = image[int(round(v0 * h)):int(round(v1 * h)), int(round(u0 * w)):int(round(u1 * w))]
        eyes.append(recipe(resized(crop, ex1 - ex0, ey1 - ey0), hue, saturation, lightness))
    for c, (file_id, _) in enumerate(L.SKINS):
        block = resized(rgba(read, file_id), x1 - x0, y1 - y0)
        region = np.zeros((ly1 - fy0, lx1 - lx0, 4), dtype=np.uint8)       # the face region, 256 x 192
        region[:, x0 - lx0:x1 - lx0] = block
        region[:, :x0 - lx0] = block[:, :1]                                 # (beside the body: its edge, drawn on)
        region[:, :, 3] = 255
        files[L.face_lower(c)] = blp.write_palette(region[ly0 - fy0:], alpha=False)
        for f, eye in enumerate(eyes):
            upper = region[:fy1 - fy0].copy()
            upper[ey0 - fy0:ey1 - fy0, ex0 - fx0:ex1 - fx0] = eye
            upper[:, :, 3] = 255
            files[L.face_upper(f, c)] = blp.write_palette(upper, alpha=False)
    return files


def fin_textures(read):
    """The fins' textures, a style's in each fin colour (the hair rows'): murloc2's own fins the skin
    whose fins they are; another model's, its texture recoloured to the fins' colour."""
    files = {}
    base = Source(read, L.BASE_MODEL)
    own = sorted((base.batch_triangles(i) for i in range(len(base.batches))), key=lambda tb: len(tb[0]))
    body = own[-1][0]
    fin_skin = rgba(read, L.SKINS[L.FIN_SKIN][0])
    fins = body[fin_triangles(base, body, fin_skin)]
    colours = []
    for _, skin, hue, saturation, lightness in L.FIN_COLOURS:
        image = recipe(rgba(read, L.SKINS[skin][0]), hue, saturation, lightness)
        image[:, :, 3] = 255
        mask = uv_mask(base, fins, image.shape[1], image.shape[0])
        colours.append((image, median_hls(image, mask)))
    for style, (_, how) in enumerate(L.FIN_STYLES):
        if how.get("own"):
            for h, (image, _) in enumerate(colours):
                files.setdefault(L.fin_texture(style, h).replace("\\", "/"), blp.write_palette(resized(image, L.FIN_SIZE, L.FIN_SIZE), alpha=False))
            continue
        src = Source(read, how["model"])
        tris, _ = part_triangles(src, base, {"batch": how["batch"], "take": ("top", how["z"])})
        texture = rgba(read, how["texture"])
        mask = uv_mask(src, tris, texture.shape[1], texture.shape[0])
        hue, light, sat = median_hls(texture, mask)
        h0, l0, s0 = hls(texture)
        for h, (_, (to_hue, to_light, to_sat)) in enumerate(colours):
            image = texture.copy()
            image[:, :, :3] = from_hls(np.full_like(h0, to_hue), np.clip(l0 * to_light / max(light, 1e-3), 0, 1),
                                       np.clip(s0 * to_sat / max(sat, 1e-3), 0, 1))
            files[L.fin_texture(style, h).replace("\\", "/")] = blp.write_palette(resized(image, L.FIN_SIZE, L.FIN_SIZE), alpha=True)
    return files


def convert(read, folder):
    files = {}
    for sex in ("Male", "Female"):
        model, skin, anims, needed, part_textures = make_model(read, sex)
        files["%s/%s/Murloc%s.m2" % (FOLDER, sex, sex)] = model
        files["%s/%s/Murloc%s00.skin" % (FOLDER, sex, sex)] = skin
        for file_id, name in anims.items():
            files[name] = models.anim_payload(read(file_id))
    # the tribe's people's murloc (a creature's model: its looks' textures the game's skins)
    model, skin, anims, _, _ = make_model(read, "Male", creature=True)
    files["%s/MurlocTribe.m2" % CREATURE_FOLDER] = model
    files["%s/MurlocTribe00.skin" % CREATURE_FOLDER] = skin
    for file_id, name in anims.items():
        files[name] = models.anim_payload(read(file_id))
    for i, (file_id, _) in enumerate(L.SKINS):
        files["%s/MurlocTribeSkin%02d.blp" % (CREATURE_FOLDER, i)] = read(file_id)
    for file_id, name in L.TEXTURE_NAMES.items():
        files["%s/Murloc%s.blp" % (FOLDER, name)] = read(file_id)
    for name, data in list(face_textures(read).items()) + list(fin_textures(read).items()):
        files[name.replace("\\", "/")] = data
    # the composed texture's base (what the game composes is palettized; a skin row's): one colour
    base = np.zeros((L.COMPOSED, L.COMPOSED, 4), dtype=np.uint8)
    base[:, :] = (96, 96, 96, 255)
    files["%s/MurlocBase.blp" % FOLDER] = blp.write_palette(base, alpha=False)
    for name, data in files.items():
        if name.endswith(".blp") and data[:4] != b"BLP2":
            raise ValueError("%s isn't a BLP2 texture" % name)
    for name, data in files.items():
        path = os.path.join(folder, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as out:
            out.write(data)
    with open(os.path.join(folder, MANIFEST), "w") as out:
        out.write("".join(name + "\n" for name in sorted(files)))
    print("murloc: %d files in %s" % (len(files), folder))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "fetch":
        convert(cached(os.environ.get("MURLOC_CACHE"), wago), sys.argv[2])
    elif len(sys.argv) == 4 and sys.argv[1] == "convert":
        convert(cached(sys.argv[2], None), sys.argv[3])
    else:
        print(__doc__)
        sys.exit(2)
