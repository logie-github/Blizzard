#!/usr/bin/env python3
"""Blizzard's player models of today (format 274: a chunked .m2 whose bones, sequences and
attachments are in a .skel file with a parent .skel, and animations in .anim files) made models
the 3.3.5 game draws (format 264, everything in the .m2 but the external animations).

    python3 tools/m2.py SRC POLICY.json DIR    converts the model POLICY describes from files in
                                               SRC (named by their file ids) into DIR

What changes:
  * The skeleton: the child's bones with the parent's sequences (the child's own over them where
    they share an id and variation, the rest added), every bone, attachment and event track with
    one entry a sequence; the sequence lookup a table by id for the ids 3.3.5 knows; sequences
    kept in their own files stay so (3.3.5 reads <Name>NNNN-VV.anim files too: one block, where
    today's has the bones', the attachments' and the model's data in chunks of their own, so the
    three go one after the other and the tracks point into theirs); the blend times and flags
    written 3.3.5's way.
  * The body texture layout: today's body texture is twice as wide as tall (the body in its left
    half, the head in its right); 3.3.5 composes a square one (the body as classic's, the face in
    the lower left quarter from the FaceLower and FaceUpper textures). The body's coordinates are
    stretched across, the head's go to the face region (cropped to what the head uses, turned if
    that fits better) and the eyes' (a texture of their own today) to the FaceUpper strip. The
    texture tool (textures.py) bakes the textures the same way, from the layout this writes.
  * The geosets: those 3.3.5 chooses by its tables (hair, facial features, armour) are kept
    under the ids the policy gives; of the groups 3.3.5 doesn't know (shown always), only the
    chosen variant stays. Hair styles get copies with the void tentacles where the policy says.
  * The textures: body, cape and hair keep their types; the eye texture becomes part of the body
    composite; today's tentacle and jewellery textures become fixed textures of the model; guild
    tabard and demon hunter textures go with their batches. Every batch draws one texture.
  * Mesh sections are split so none uses more than 64 bones (3.3.5's limit); vertices not drawn
    are left out; cameras take 3.3.5's layout; particles, ribbons and lights are left out.
"""
import json
import math
import os
import struct
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decimate  # noqa: E402

MAX_BONES = 64
INDEX_BUDGET = 65535            # the game reads a section's triangle start as 16 bits: every section within this
# What gives way when a model has more than that (decimate.py), and how far: the gear first, then
# the features and the hair, the body (the face among it) last.
TIER_FLOORS = [("gear", 0.45), ("features", 0.6), ("hair", 0.6), ("body", 0.75)]
TIER_FLOORS_MORE = [("gear", 0.3), ("features", 0.4), ("hair", 0.4), ("body", 0.6)]
GEAR_GROUPS = {4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 18, 19, 20}
GEAR_MAX_VARIANT = 6            # 3.3.5's items ask for a group's variants 1 to 6 (ItemDisplayInfo's geoset groups 0 to 5)


def tier_of(geoset):
    """Which part of the model a (new) geoset id is, for the index budget."""
    if geoset == 0 or geoset == 702:
        return "body"
    if geoset < 100:
        return "hair"
    if geoset // 100 in (1, 2, 3, 16, 17):
        return "features"
    return "gear"
LAST_ANIMATION = 505                 # 3.3.5's AnimationData ends here
KEY_BONES = 27                       # 3.3.5 knows key bones 0 to 26
M2_FLAGS = 0x2080                    # what the known HD conversions keep of the newer flags
HEADER = 304
BONE, SEQ, ATTACH, EVENT, CAMERA_IN, CAMERA_OUT, VERTEX, SECTION, BATCH = 88, 64, 40, 36, 116, 100, 48, 48, 24
TRACK, TRACK_BASE = 20, 12
BODY, CAPE, HAIR, EYES = 1, 2, 6, 19
KEPT_TYPES = {0, BODY, CAPE, HAIR}


def chunks_of(data):
    out = {}
    at = 0
    while at + 8 <= len(data):
        cid = data[at:at + 4].decode("latin1")
        size = struct.unpack_from("<I", data, at + 4)[0]
        out[cid] = data[at + 8:at + 8 + size]
        at += 8 + size
    return out


def arr(blob, at):
    return struct.unpack_from("<II", blob, at)


class Track:
    """An M2Track: interpolation, global sequence, and per sequence (count, offset) pairs for
    timestamps and values, with the bytes behind them for sequences kept in the file."""

    def __init__(self, interp, gseq, timestamps, values):
        self.interp, self.gseq, self.timestamps, self.values = interp, gseq, timestamps, values

    @staticmethod
    def read(blob, at, value_size, in_file):
        """[in_file(i)] says whether sequence i's data is in [blob] (else in its .anim file). A
        track of a global sequence has its data in [blob] whatever the sequences' files: it's
        never in a sequence's own file."""
        interp, gseq, tc, to, vc, vo = struct.unpack_from("<hhIIII", blob, at)
        ts, vs = [], []
        for i in range(max(tc, vc)):
            t = struct.unpack_from("<II", blob, to + i * 8) if i < tc else (0, 0)
            v = struct.unpack_from("<II", blob, vo + i * 8) if i < vc else (0, 0)
            if gseq >= 0 or in_file(i):
                ts.append(blob[t[1]:t[1] + t[0] * 4] if t[0] else b"")
                vs.append(blob[v[1]:v[1] + v[0] * value_size] if v[0] else b"")
            else:
                ts.append(("ext",) + tuple(t))
                vs.append(("ext",) + tuple(v))
        return Track(interp, gseq, ts, vs)

    @staticmethod
    def read_base(blob, at, in_file):
        interp, gseq, tc, to = struct.unpack_from("<hhII", blob, at)
        ts = []
        for i in range(tc):
            t = struct.unpack_from("<II", blob, to + i * 8)
            ts.append(blob[t[1]:t[1] + t[0] * 4] if gseq >= 0 or in_file(i) else ("ext",) + tuple(t))
        return Track(interp, gseq, ts, None)

    def has_data(self):
        return any(entry_count(t) for t in self.timestamps)


def entry_count(entry):
    if isinstance(entry, tuple):
        return entry[1]
    return len(entry) // 4 if entry else 0


class Skeleton:
    def __init__(self, data):
        c = chunks_of(data)
        self.parent = struct.unpack_from("<I", c["SKPD"], 8)[0] if "SKPD" in c else 0
        sks = c["SKS1"]
        gl, glo, sc, so, lc, lo = struct.unpack_from("<6I", sks)
        self.loops = list(struct.unpack_from("<%dI" % gl, sks, glo))
        self.seqs = [bytearray(sks[so + i * SEQ:so + (i + 1) * SEQ]) for i in range(sc)]
        self.in_file = [bool(struct.unpack_from("<I", s, 12)[0] & 0x20) for s in self.seqs]
        skb = c["SKB1"]
        bc, bo, kc, ko = struct.unpack_from("<4I", skb)
        self.key_bones = list(struct.unpack_from("<%dh" % kc, skb, ko))
        self.bones = []
        for i in range(bc):
            at = bo + i * BONE
            head = skb[at:at + 16]
            tracks = [Track.read(skb, at + 16 + k * TRACK, size, lambda s: self.in_file[s] if s < len(self.in_file) else True)
                      for k, size in enumerate((12, 8, 12))]
            self.bones.append((head, tracks, skb[at + 76:at + 88]))
        ska = c["SKA1"]
        ac, ao, alc, alo = struct.unpack_from("<4I", ska)
        self.attachments = []
        for i in range(ac):
            at = ao + i * ATTACH
            self.attachments.append((ska[at:at + 20], Track.read(ska, at + 20, 1, lambda s: self.in_file[s] if s < len(self.in_file) else True)))
        self.attachment_lookup = list(struct.unpack_from("<%dh" % alc, ska, alo))
        self.anim_files = {}
        if "AFID" in c:
            raw = c["AFID"]
            for i in range(0, len(raw), 8):
                anim, var, fid = struct.unpack_from("<HHI", raw, i)
                if fid:
                    self.anim_files[(anim, var)] = fid

    def key(self, i):
        return struct.unpack_from("<HH", self.seqs[i], 0)


class Model:
    """The .m2's own part (format 274, chunked)."""

    def __init__(self, data, skeleton=None):
        c = chunks_of(data)
        self.chunks = c
        m = c["MD21"]
        self.m = m
        if m[:4] != b"MD20":
            raise ValueError("not a model")
        # Its sequences (a model with its skeleton inside), else its skeleton's: which are in the file.
        sc, so = arr(m, 28)
        if sc:
            self.keys = [struct.unpack_from("<HH", m, so + i * SEQ) for i in range(sc)]
            self.in_file = [bool(struct.unpack_from("<I", m, so + i * SEQ + 12)[0] & 0x20) for i in range(sc)]
        else:
            self.keys = [skeleton.key(i) for i in range(len(skeleton.seqs))]
            self.in_file = list(skeleton.in_file)
        in_file = lambda s: self.in_file[s] if s < len(self.in_file) else True
        vc, vo = arr(m, 60)
        self.vertices = [m[vo + i * VERTEX:vo + (i + 1) * VERTEX] for i in range(vc)]
        tc, to = arr(m, 80)
        self.textures = [struct.unpack_from("<II", m, to + i * 16) for i in range(tc)]
        self.texture_ids = list(struct.unpack_from("<%dI" % (len(c["TXID"]) // 4), c["TXID"])) if "TXID" in c else []
        lc, lo = arr(m, 128)
        self.texture_lookup = list(struct.unpack_from("<%dh" % lc, m, lo))
        mc, mo = arr(m, 112)
        self.materials = [struct.unpack_from("<HH", m, mo + i * 4) for i in range(mc)]
        rc, ro = arr(m, 104)
        self.replaceable = list(struct.unpack_from("<%dh" % rc, m, ro))
        wc, wo = arr(m, 88)
        self.weights = [Track.read(m, wo + i * TRACK, 2, in_file) for i in range(wc)]
        trc, tro = arr(m, 144)
        self.transparency_lookup = list(struct.unpack_from("<%dh" % trc, m, tro))
        ttc, tto = arr(m, 96)
        self.transforms = [[Track.read(m, tto + i * 60 + k * TRACK, size, in_file) for k, size in enumerate((12, 16, 12))] for i in range(ttc)]
        tlc, tlo = arr(m, 152)
        self.transform_lookup = list(struct.unpack_from("<%dh" % tlc, m, tlo))
        ec, eo = arr(m, 256)
        self.events = []
        for i in range(ec):
            at = eo + i * EVENT
            self.events.append((m[at:at + 24], Track.read_base(m, at + 24, in_file)))
        cc, co = arr(m, 272)
        self.cameras = []
        for i in range(cc):
            at = co + i * CAMERA_IN
            kind, far, near = struct.unpack_from("<Iff", m, at)
            pos = Track.read(m, at + 12, 36, in_file)
            pos_base = m[at + 32:at + 44]
            target = Track.read(m, at + 44, 36, in_file)
            target_base = m[at + 64:at + 76]
            roll = Track.read(m, at + 76, 12, in_file)
            fov = Track.read(m, at + 96, 12, in_file)
            self.cameras.append((kind, far, near, pos, pos_base, target, target_base, roll, fov))
        clc, clo = arr(m, 280)
        self.camera_lookup = list(struct.unpack_from("<%dh" % clc, m, clo))
        self.bounds = m[160:216]
        ctc, cto = arr(m, 216)
        self.coll_tris = m[cto:cto + ctc * 2]
        cvc, cvo = arr(m, 224)
        self.coll_verts = m[cvo:cvo + cvc * 12]
        cnc, cno = arr(m, 232)
        self.coll_normals = m[cno:cno + cnc * 12]
        self.skin_ids = list(struct.unpack_from("<%dI" % (len(c["SFID"]) // 4), c["SFID"])) if "SFID" in c else []
        self.skeleton_id = struct.unpack_from("<I", c["SKID"])[0] if "SKID" in c else 0
        self.index_of = {}
        for i, k in enumerate(self.keys):
            self.index_of.setdefault(k, i)


class Skin:
    def __init__(self, data):
        if data[:4] != b"SKIN":
            raise ValueError("not a skin")
        vn, vo, ixn, ixo, pn, po, sn, so, bn, bo = struct.unpack_from("<10I", data, 4)
        self.vertices = struct.unpack_from("<%dH" % vn, data, vo)
        self.indices = struct.unpack_from("<%dH" % ixn, data, ixo)
        self.properties = [data[po + i * 4:po + i * 4 + 4] for i in range(pn)]
        self.sections = [struct.unpack_from("<10H7f", data, so + i * SECTION) for i in range(sn)]
        self.batches = [struct.unpack_from("<BbHHHhHHHHHHH", data, bo + i * BATCH) for i in range(bn)]


# The merged skeleton ------------------------------------------------------------------------------

class Merged:
    """The parent's sequences with the child's over and after them: for each merged sequence,
    where it comes from (skeleton, index)."""

    def __init__(self, child, parent):
        self.child, self.parent = child, parent
        self.sources = []                 # (which, index): which 0 = parent, 1 = child
        self.child_index = {}             # child sequence index -> merged index
        self.parent_index = {}
        if parent:
            by_key = {}
            for i in range(len(parent.seqs)):
                self.sources.append((0, i))
                self.parent_index[i] = i
                by_key.setdefault(parent.key(i), i)
        else:
            by_key = {}
        for i in range(len(child.seqs)):
            k = child.key(i)
            if k in by_key and parent:
                j = by_key[k]
                self.sources[j] = (1, i)
                self.child_index[i] = j
            else:
                self.child_index[i] = len(self.sources)
                self.sources.append((1, i))
        # global sequences: the child's list where the parent's is its start, else both
        if parent and child.loops[:len(parent.loops)] == parent.loops:
            self.loops = list(child.loops)
            self.child_loop = lambda g: g
        elif parent:
            self.loops = list(parent.loops) + list(child.loops)
            self.child_loop = lambda g: g + len(parent.loops)
        else:
            self.loops = list(child.loops)
            self.child_loop = lambda g: g
        self.n = len(self.sources)

    def skeleton(self, which):
        return self.child if which else self.parent

    def in_file(self, j):
        which, i = self.sources[j]
        return self.skeleton(which).in_file[i]

    def seq(self, j):
        which, i = self.sources[j]
        return self.skeleton(which).seqs[i]

    def anim_file(self, j):
        """The file id of a sequence kept in its own file (the child's own, else the parent's)."""
        which, i = self.sources[j]
        skel = self.skeleton(which)
        key = skel.key(i)
        if key in skel.anim_files:
            return skel.anim_files[key]
        if which and self.parent and key in self.parent.anim_files:
            return self.parent.anim_files[key]
        return 0

    def remap_index(self, which, index):
        if index == 0xFFFF:
            return 0xFFFF
        table = self.child_index if which else self.parent_index
        return table.get(index, 0xFFFF)

    def merge_tracks(self, child_track, parent_track, parent_map=None):
        """One track with an entry a merged sequence: the child's for its sequences, the parent's
        for the parent's. [parent_track] None: the parent's sequences get no data. [parent_map]:
        the parent skeleton's sequence index -> the index into [parent_track]'s entries (when
        the track is another file's, with its own sequence order)."""
        interp = 0
        for t in (parent_track, child_track):
            if t and t.has_data():
                interp = t.interp if not interp else interp
        if not interp:
            interp = child_track.interp if child_track else (parent_track.interp if parent_track else 0)
        gseq = -1
        if child_track and child_track.gseq >= 0:
            gseq = self.child_loop(child_track.gseq)
        elif parent_track and parent_track.gseq >= 0:
            gseq = parent_track.gseq
        if gseq >= 0:
            # a global sequence's data is in its first entry alone, the entry of the track whose
            # loop it is (not the first merged sequence's, which may be the other skeleton's)
            t = child_track if child_track and child_track.gseq >= 0 else parent_track
            first = next((k for k in range(len(t.timestamps)) if entry_count(t.timestamps[k])), 0)
            ts = t.timestamps[first:first + 1] or [b""]
            vs = (t.values[first:first + 1] or [b""]) if t.values is not None else None
            return Track(interp, gseq, ts, vs)
        ts, vs = [], []
        has_values = (child_track and child_track.values is not None) or (parent_track and parent_track.values is not None)
        for j in range(self.n):
            which, i = self.sources[j]
            t = child_track if which else parent_track
            if not which and parent_map is not None:
                i = parent_map.get(i, -1)
            if t is None or i < 0 or i >= len(t.timestamps):
                ts.append(b"")
                vs.append(b"")
                continue
            if j in getattr(self, "no_file", ()):
                ts.append(b"")
                vs.append(b"")
                continue
            ts.append(t.timestamps[i])
            vs.append(t.values[i] if t.values is not None else b"")
        return Track(interp, gseq, ts, vs if has_values else None)


TABLE_GROUPS = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13, 15, 18}   # 3.3.5 picks from these by its tables


LAST_KNOWN_GROUP = 18   # 3.3.5 shows the first geoset of each group up to the belt's; later groups it doesn't draw


def complete_policy(policy, geosets):
    """The geosets kept, old id (as text) -> new ids: the policy's own (tools/races.py: hair,
    features, ears, the eye glow, the head...); of the groups it doesn't name, the groups 3.3.5's
    tables choose from whole, the groups the policy drops none, and the rest their lowest (the one
    shown without an item): kept as it is in a group 3.3.5 knows, folded into geoset 0 (always
    drawn) in a group it doesn't (today's toes, torso and forearms in groups 20, 22 and 23)."""
    out = {k: list(v) for k, v in policy["geoset_policy"].items()}
    named = {int(k) // 100 for k in out}
    drop = set(policy.get("drop_groups", []))
    by_group = {}
    for g in geosets:
        by_group.setdefault(g // 100, []).append(g)
    for group, members in sorted(by_group.items()):
        members.sort()
        for g in members:
            if str(g) in out:
                continue
            if group in named or group in drop:
                continue
            if group in TABLE_GROUPS:
                if group in GEAR_GROUPS and g % 100 > GEAR_MAX_VARIANT:
                    continue                       # a variant no 3.3.5 item asks for
                out[str(g)] = [g]
            elif g == members[0]:
                out[str(g)] = [g] if group <= LAST_KNOWN_GROUP else [0]
    return out


def sequence_lookup(ids, variations):
    """The sequence lookup as the game reads it: a hash table (an id's first slot is id % size,
    the next ones after it until an empty slot), each id's first variation in it, with room so
    every probe ends at an empty slot."""
    first = {}
    for j, (sid, var) in enumerate(zip(ids, variations)):
        if sid not in first or (var == 0 and variations[first[sid]] != 0):
            first[sid] = j
    size = max(64, 2 * len(first))
    table = [-1] * size
    for sid, j in sorted(first.items()):
        i = sid % size
        while table[i] >= 0:
            i = (i + 1) % size
        table[i] = j
    return table


# The output ---------------------------------------------------------------------------------------

class Blob:
    def __init__(self):
        self.data = bytearray(HEADER)

    def append(self, payload, align=16):
        while len(self.data) % align:
            self.data.append(0)
        at = len(self.data)
        self.data.extend(payload)
        return at

    def array(self, at, count, payload):
        offset = self.append(payload) if count else 0
        struct.pack_into("<II", self.data, at, count, offset)
        return offset

    def set_array(self, at, count, offset):
        struct.pack_into("<II", self.data, at, count, offset)


def write_track(blob, track, external_ok=True):
    """A track's bytes (20, or 12 for a timestamps-only one) with its arrays written out."""
    n = len(track.timestamps)
    ts_entries, vs_entries = [], []
    for i in range(n):
        for entries, data in ((ts_entries, track.timestamps[i]), (vs_entries, track.values[i] if track.values is not None else None)):
            if data is None:
                continue
            if isinstance(data, tuple):
                entries.append((data[1], data[2]))        # kept in the sequence's own file
            elif data:
                entries.append((entry_count_bytes(data, entries is ts_entries, track), blob.append(data, 4)))
            else:
                entries.append((0, 0))
    out = struct.pack("<hh", track.interp, track.gseq)
    ts_at = blob.append(b"".join(struct.pack("<II", *e) for e in ts_entries), 4) if ts_entries else 0
    out += struct.pack("<II", len(ts_entries), ts_at)
    if track.values is not None:
        vs_at = blob.append(b"".join(struct.pack("<II", *e) for e in vs_entries), 4) if vs_entries else 0
        out += struct.pack("<II", len(vs_entries), vs_at)
    return out


def entry_count_bytes(data, is_timestamps, track):
    if is_timestamps:
        return len(data) // 4
    return len(data) // track.value_size


def with_value_size(track, size):
    track.value_size = size
    return track


# Geometry -----------------------------------------------------------------------------------------

def head_layout(model, skin, body_sections):
    """Where the head's texture coordinates go: the box they use in the right half of today's
    texture, and whether it's turned to fit the face region (256 x 128 of 512) better."""
    us, vs = [], []
    for s in body_sections:
        sec = skin.sections[s]
        level, vstart, vcount = sec[1], sec[2], sec[3]
        for k in range(vstart, vstart + vcount):
            u, v = struct.unpack_from("<ff", model.vertices[skin.vertices[k]], 32)
            if u >= 0.5:
                us.append(u)
                vs.append(v)
    if not us:
        return None
    us.sort()
    vs.sort()
    cut = max(1, len(us) // 500)                  # the stray 0.2% at each end (a seam's vertices)
    u0, u1 = max(0.5, us[cut]), min(1.0, us[-1 - cut])
    v0, v1 = max(0.0, vs[cut]), min(1.0, vs[-1 - cut])
    # a little room, snapped to the texture's 512ths
    u0, v0 = math.floor((u0 - 0.5) * 512) / 512 + 0.5, math.floor(v0 * 512) / 512
    u1, v1 = math.ceil((u1 - 0.5) * 512) / 512 + 0.5, math.ceil(v1 * 512) / 512
    width, height = (u1 - u0) * 2, v1 - v0        # of the right half, as fractions of it
    # the region is twice as wide as tall: turn the head when it's taller than wide
    rotate = height > width
    return {"box": [u0, v0, u1, v1], "rotate": rotate}


def remap_uv(u, v, kind, layout):
    if kind == "body":
        return u * 2.0, v
    if kind == "head":
        u0, v0, u1, v1 = layout["box"]
        fu = min(1.0, max(0.0, (u - u0) / (u1 - u0))) if u1 > u0 else 0.0
        fv = min(1.0, max(0.0, (v - v0) / (v1 - v0))) if v1 > v0 else 0.0
        if layout["rotate"]:
            fu, fv = fv, 1.0 - fu
        return fu * 0.5, 0.75 + fv * 0.25
    if kind == "eyes":
        return u * 0.5, 0.625 + v * 0.125
    return u, v


ANIM_CHUNKS = (b"AFM2", b"AFSA", b"AFSB")


def anim_block(data):
    """A sequence's file of today as 3.3.5's, and where its parts start in it. Today's .anim has the
    skeleton's bone data (AFSB), its attachments' (AFSA) and the model's own (AFM2) in chunks, each
    track's offsets into its own chunk; 3.3.5's is one block. The three go one after the other, the
    bones' first (their offsets stay); the attachments' and the model's tracks move by where theirs
    start. An older file is one block already."""
    if data[:4] not in ANIM_CHUNKS:
        return bytes(data), {"bone": 0, "attach": 0, "model": 0}
    c = chunks_of(data)
    out = bytearray(c.get("AFSB", b""))
    base = {"bone": 0}
    for kind, cid in (("attach", "AFSA"), ("model", "AFM2")):
        while len(out) % 16:
            out.append(0)
        base[kind] = len(out)
        out += c.get(cid, b"")
    return bytes(out), base


def entry_ok(t, v, size, data, duration):
    """Whether a track's entry for a sequence kept in its own file ([data]) is that file's: within
    it, its times rising and within the sequence ([duration] ms)."""
    if not (isinstance(t, tuple) and t[1]):
        return True
    if t[2] + t[1] * 4 > len(data) or (isinstance(v, tuple) and v[1] and v[2] + v[1] * size > len(data)):
        return False
    times = np.frombuffer(data, dtype="<u4", count=t[1], offset=t[2]).astype(np.int64)
    return bool((np.diff(times) >= 0).all() and times[-1] <= duration + 1)


def bones_match(skeleton, i, data, duration):
    """Whether the skeleton's sequence i's bone data is in [data]: all but a fiftieth of its
    tracks' entries are that file's (a few of today's skeletons list files whose data is laid out
    for another skeleton: the nightborne's and the void elf women's parents' list their older
    models' files)."""
    good = bad = 0
    for head, tracks, pivot in skeleton.bones:
        for track, size in zip(tracks, (12, 8, 12)):
            if track.gseq >= 0 or i >= len(track.timestamps):
                continue
            t, v = track.timestamps[i], track.values[i]
            if isinstance(t, tuple) and t[1]:
                if entry_ok(t, v, size, data, duration):
                    good += 1
                else:
                    bad += 1
    return bad <= (good + bad) / 50


class OwnSkeleton:
    """An older model's own bones, sequences and files (a model without a .skel), read as a
    Skeleton is: where the files a newer skeleton lists were made for it."""

    def __init__(self, data):
        c = chunks_of(data)
        m = c["MD21"]
        sc, so = arr(m, 28)
        self.seqs = [bytearray(m[so + i * SEQ:so + (i + 1) * SEQ]) for i in range(sc)]
        self.in_file = [bool(struct.unpack_from("<I", s, 12)[0] & 0x20) for s in self.seqs]
        in_file = lambda s: self.in_file[s] if s < len(self.in_file) else True
        bc, bo = arr(m, 44)
        self.bones = []
        for i in range(bc):
            at = bo + i * BONE
            self.bones.append((m[at:at + 16], [Track.read(m, at + 16 + k * TRACK, size, in_file)
                                                for k, size in enumerate((12, 8, 12))], m[at + 76:at + 88]))
        self.anim_files = {}
        raw = c.get("AFID", b"")
        for i in range(0, len(raw), 8):
            anim, var, fid = struct.unpack_from("<HHI", raw, i)
            if fid:
                self.anim_files[(anim, var)] = fid

    def key(self, i):
        return struct.unpack_from("<HH", self.seqs[i], 0)


def bone_sources(files, policy, child, parent):
    """The other skeletons whose files a sequence's data may be in: the parent model's own bones
    (an older model) or its skeleton, where that isn't the one the child's names."""
    out = []
    if policy.get("parent_model"):
        data = files(policy["parent_model"])
        c = chunks_of(data)
        if "SKID" in c:
            sid = struct.unpack_from("<I", c["SKID"])[0]
            if sid != child.parent:
                out.append(Skeleton(files(sid)))
        elif "MD21" in c and arr(c["MD21"], 44)[0]:
            out.append(OwnSkeleton(data))
    return out


def convert(files, policy, out_dir, log=print):
    """[files]: file id -> bytes (a function). [policy]: the model's description (see the module's
    tools/races.py for how one is made). Writes the model into [out_dir] and returns the list of
    files written (the game's paths)."""
    name, folder = policy["name"], policy["folder"]
    m2_data = files(policy["model"])
    chunks = chunks_of(m2_data)
    child = Skeleton(files(struct.unpack_from("<I", chunks["SKID"])[0]))
    parent = Skeleton(files(child.parent)) if child.parent else None
    merged = Merged(child, parent)
    model = Model(m2_data, child)
    parent_model = Model(files(policy["parent_model"]), parent) if parent and policy.get("parent_model") else None
    parent_map = {i: parent_model.index_of.get(parent.key(i), -1) for i in range(len(parent.seqs))} if parent_model else None
    skin = Skin(files(model.skin_ids[0]))
    blob = Blob()
    d = blob.data
    d[0:4] = b"MD20"
    struct.pack_into("<I", d, 4, 264)
    struct.pack_into("<I", d, 16, M2_FLAGS)
    blob.array(8, len(name) + 1, name.encode() + b"\0")

    # Global sequences and sequences.
    blob.array(20, len(merged.loops), struct.pack("<%dI" % len(merged.loops), *merged.loops))
    seqs = bytearray()
    ids = []
    external = []                                     # (merged index, (id, var), file id)
    no_file = set()                                   # external sequences with no file: empty
    merged.no_file = no_file
    anim_out, anim_base = {}, {}                      # an external sequence's file as 3.3.5's, where each part starts
    durations = {}                                    # an external sequence's length, as its file has it
    bones_from = {}                                   # an external sequence whose bone data is another skeleton's: (it, its index)
    unusable = set()
    others = None
    for j in range(merged.n):
        which, i = merged.sources[j]
        fid = merged.anim_file(j) if not merged.in_file(j) else 0
        if not fid:
            continue
        skel = merged.skeleton(which)
        key, duration = skel.key(i), struct.unpack_from("<I", skel.seqs[i], 4)[0]
        block = anim_block(files(fid))
        if not bones_match(skel, i, block[0], duration):
            # the file is laid out for another skeleton: the one it fits gives this sequence's bones
            if others is None:
                others = bone_sources(files, policy, child, parent)
            for other in others:
                if key not in other.anim_files:
                    continue
                k = next(n for n in range(len(other.seqs)) if other.key(n) == key)
                other_duration = struct.unpack_from("<I", other.seqs[k], 4)[0]
                other_block = anim_block(files(other.anim_files[key]))
                if bones_match(other, k, other_block[0], max(duration, other_duration)):
                    bones_from[j] = (other, k)
                    block, duration = other_block, max(duration, other_duration)
                    break
            else:
                unusable.add(j)
                continue
        anim_out[j], anim_base[j] = block
        durations[j] = duration
    keys = [struct.unpack_from("<HH", merged.seq(j), 0) for j in range(merged.n)]
    stand = keys.index((0, 0)) if (0, 0) in keys else 0
    for j in range(merged.n):
        which, i = merged.sources[j]
        s = bytearray(merged.seq(j))
        sid, var, dur = struct.unpack_from("<HHI", s, 0)
        flags = struct.unpack_from("<I", s, 12)[0] & 0xFF
        blend_in, blend_out = struct.unpack_from("<HH", s, 28)
        struct.pack_into("<I", s, 12, flags)
        struct.pack_into("<I", s, 28, max(blend_in, blend_out))
        vnext, anext = struct.unpack_from("<HH", s, 60)
        struct.pack_into("<HH", s, 60, merged.remap_index(which, vnext), merged.remap_index(which, anext))
        if j in unusable:
            # drawn as another: the animation's first variation, else Stand (an alias, its own tracks empty)
            first = keys.index((sid, 0)) if (sid, 0) in keys else stand
            target = first if first != j and first not in unusable else stand
            log("%s: sequence %d-%d's file fits none of its skeletons: drawn as %d-%d" % (name, sid, var, *keys[target]))
            struct.pack_into("<I", s, 12, flags | 0x20 | 0x40)
            struct.pack_into("<H", s, 62, target)
            no_file.add(j)
        elif not merged.in_file(j):
            fid = merged.anim_file(j)
            if j in bones_from:
                other, k = bones_from[j]
                fid = other.anim_files[other.key(k)]
                log("%s: sequence %d-%d's bones from the skeleton its file is laid out for" % (name, sid, var))
            if fid:
                external.append((j, (sid, var), fid))
            else:
                # no file of its own: the sequence has no data (its tracks are empty), kept as in the file
                struct.pack_into("<I", s, 12, flags | 0x20)
                no_file.add(j)
        seqs += s
        ids.append(sid)
    blob.array(28, merged.n, bytes(seqs))

    def rebased(track, kind, size=None):
        """[track] with its entries in the sequences' own files moved to where their chunk now is
        ([size]: a value's bytes); an entry that isn't its file's (past its end, or times that
        don't rise within the sequence) is left empty, so the game never reads what isn't it."""
        if track.gseq >= 0:
            return track
        size = size or getattr(track, "value_size", None)
        for j in range(len(track.timestamps)):
            t = track.timestamps[j]
            v = track.values[j] if track.values is not None else None
            if not isinstance(t, tuple) or j not in anim_base:
                continue
            at = anim_base[j][kind]
            t = (t[0], t[1], t[2] + at) if t[1] else t
            if isinstance(v, tuple):
                v = (v[0], v[1], v[2] + at) if v[1] else v
            if not entry_ok(t, v, size or 0, anim_out[j], durations[j]):
                t, v = b"", b"" if v is not None else None
            track.timestamps[j] = t
            if track.values is not None:
                track.values[j] = v
        return track

    def real_floats(track, size):
        """[track] (translations or scales, three floats a value) without the entries whose values
        aren't (a file laid out for another skeleton), which the game would read as positions
        thousands of yards off and throw their vertices across the screen."""
        for j in range(len(track.values)):
            v = track.values[j]
            if isinstance(v, tuple):
                if not v[1] or j not in anim_out:
                    continue
                raw = anim_out[j][v[2]:v[2] + v[1] * size]
            else:
                raw = v
            if not raw:
                continue
            x = np.frombuffer(raw, dtype="<f4", count=len(raw) // 4)
            if not np.isfinite(x).all() or np.abs(x).max() > 100.0:
                track.timestamps[j], track.values[j] = b"", b""
        return track

    table = sequence_lookup(ids, [struct.unpack_from("<H", merged.seq(j), 2)[0] for j in range(merged.n)])
    blob.array(36, len(table), struct.pack("<%dh" % len(table), *table))

    by_crc = {}

    def other_bone(other, crc):
        """The other skeleton's bone of the same name (its name's hash)."""
        if id(other) not in by_crc:
            by_crc[id(other)] = {struct.unpack_from("<I", h, 12)[0]: (h, t, p) for h, t, p in other.bones}
        return by_crc[id(other)].get(crc)

    # Bones: the child's, their tracks merged.
    bones = bytearray()
    for b, (head, tracks, pivot) in enumerate(child.bones):
        key_bone, flags, parent_bone, submesh, crc = struct.unpack_from("<iIhHI", head)
        if parent and b < len(parent.bones):
            flags |= struct.unpack_from("<I", parent.bones[b][0], 4)[0] & 0x200
        bones += struct.pack("<iIhHI", key_bone, flags, parent_bone, submesh, crc)
        for k, size in enumerate((12, 8, 12)):
            ptrack = parent.bones[b][1][k] if parent and b < len(parent.bones) else None
            track = merged.merge_tracks(tracks[k], ptrack)
            if track.gseq < 0:
                for j, (other, n) in bones_from.items():
                    o = other_bone(other, crc)
                    ot = o[1][k] if o else None
                    if ot and ot.gseq < 0 and n < len(ot.timestamps):
                        track.timestamps[j], track.values[j] = ot.timestamps[n], ot.values[n]
                        track.interp = track.interp or ot.interp
                    else:
                        track.timestamps[j], track.values[j] = b"", b""
            track = rebased(track, "bone", size)
            if k != 1 and track.gseq < 0:
                track = real_floats(track, size)
            bones += write_track(blob, with_value_size(track, size))
        bones += pivot
    blob.array(44, len(child.bones), bytes(bones))
    key_bones = (child.key_bones + [-1] * KEY_BONES)[:KEY_BONES]
    blob.array(52, len(key_bones), struct.pack("<%dh" % len(key_bones), *key_bones))

    # Textures: the ones kept, with names for the fixed ones; the lookup is one entry a texture.
    textures, texture_names, texture_index = [], {}, {}
    hard = policy.get("hardcoded", {})                  # texture type (as text) -> game path
    for i, (kind, flags) in enumerate(model.textures):
        fid = model.texture_ids[i] if i < len(model.texture_ids) else 0
        if kind == 0 and fid:
            path = "%s\\%s_%d.blp" % (folder, name, fid)
            texture_names[fid] = path
            texture_index[i] = len(textures)
            textures.append((0, flags, path))
        elif kind in (BODY, CAPE, HAIR):
            texture_index[i] = len(textures)
            textures.append((kind, flags, ""))
        elif kind == EYES:
            texture_index[i] = len(textures)            # drawn from the body composite
            textures.append((BODY, flags, ""))
        elif str(kind) in hard:
            texture_index[i] = len(textures)
            textures.append((0, flags, hard[str(kind)]))
    tex_blob = bytearray()
    paths = []
    for kind, flags, path in textures:
        paths.append(path.encode() + b"\0" if path else b"\0")
        tex_blob += struct.pack("<IIII", kind, flags, 0, 0)
    tex_at = blob.array(80, len(textures), bytes(tex_blob))
    for i, p in enumerate(paths):
        at = blob.append(p, 1)
        struct.pack_into("<II", d, tex_at + i * 16 + 8, len(p), at)
    blob.array(128, len(textures), struct.pack("<%dh" % len(textures), *range(len(textures))))
    blob.array(136, 1, struct.pack("<hh", 0, 0))

    # Texture weights and transforms (as the model has them: static, or on a global sequence).
    weights = b"".join(write_track(blob, with_value_size(rebased(merged.merge_tracks(t, None), "model", 2), 2)) for t in model.weights)
    blob.array(88, len(model.weights), weights)
    blob.array(144, len(model.transparency_lookup), struct.pack("<%dh" % len(model.transparency_lookup), *model.transparency_lookup))
    transforms = b""
    for tracks in model.transforms:
        for k, size in enumerate((12, 16, 12)):
            transforms += write_track(blob, with_value_size(rebased(merged.merge_tracks(tracks[k], None), "model", size), size))
    blob.array(96, len(model.transforms), transforms)
    lookup = [t if 0 <= t < len(model.transforms) else -1 for t in model.transform_lookup]
    blob.array(152, len(lookup), struct.pack("<%dh" % len(lookup), *lookup))
    blob.array(104, len(model.replaceable), struct.pack("<%dh" % len(model.replaceable), *model.replaceable))
    materials = b"".join(struct.pack("<HH", flags & 0x1F, min(blend, 6) if blend != 7 else 4) for flags, blend in model.materials)
    blob.array(112, len(model.materials), materials)

    # Bounds and collision.
    d[160:216] = model.bounds
    blob.array(216, len(model.coll_tris) // 2, model.coll_tris)
    blob.array(224, len(model.coll_verts) // 12, model.coll_verts)
    blob.array(232, len(model.coll_normals) // 12, model.coll_normals)

    # Attachments: the child's.
    attachments = b""
    for head, track in child.attachments:
        attachments += head + write_track(blob, with_value_size(rebased(merged.merge_tracks(track, None), "attach", 1), 1))
    blob.array(240, len(child.attachments), attachments)
    blob.array(248, len(child.attachment_lookup), struct.pack("<%dh" % len(child.attachment_lookup), *child.attachment_lookup))

    # Events: the child model's, with the parent model's timings for the parent's sequences.
    parent_events = {}
    if parent_model:
        for head, track in parent_model.events:
            parent_events[head[:4]] = track
    events = b""
    for head, track in model.events:
        events += head + write_track(blob, rebased(merged.merge_tracks(track, parent_events.get(head[:4]), parent_map), "model"))
    blob.array(256, len(model.events), events)
    blob.array(264, 0, b"")

    # Cameras in 3.3.5's layout: the field of view a number (the newer track's first key).
    cameras = b""
    for kind, far, near, pos, pos_base, target, target_base, roll, fov in model.cameras:
        value = 0.7853981634
        for entry in fov.values or []:
            if isinstance(entry, bytes) and len(entry) >= 4:
                v = struct.unpack_from("<f", entry)[0]
                if 0.1 < v < 3.0:
                    value = v
                break
        cameras += struct.pack("<Ifff", kind, value, far, near)
        cameras += write_track(blob, with_value_size(rebased(merged.merge_tracks(pos, None), "model", 36), 36)) + pos_base
        cameras += write_track(blob, with_value_size(rebased(merged.merge_tracks(target, None), "model", 36), 36)) + target_base
        cameras += write_track(blob, with_value_size(rebased(merged.merge_tracks(roll, None), "model", 12), 12))
    blob.array(272, len(model.cameras), cameras)
    blob.array(280, len(model.camera_lookup), struct.pack("<%dh" % len(model.camera_lookup), *model.camera_lookup))
    blob.array(288, 0, b"")
    blob.array(296, 0, b"")

    # The mesh: sections kept, renumbered, copied; their textures; the bone palettes.
    geosets = policy.get("geosets") or complete_policy(policy, sorted(set(sec[0] for sec in skin.sections)))
    eye_geosets = set(policy.get("eye_geosets", []))
    texture_types = [k for k, _ in model.textures]
    body_sections = [s for s in range(len(skin.sections)) if any(
        b[3] == s and texture_types[model.texture_lookup[b[9]]] == BODY for b in skin.batches)]
    layout = head_layout(model, skin, body_sections)
    out_vertices, out_props, out_indices, out_sections, out_batches, out_lookup = [], [], [], [], [], []
    new_vertex = {}

    def vertex(index, kind):
        key = (index, kind)
        if key not in new_vertex:
            v = bytearray(model.vertices[index])
            if kind == "second":                  # (a card drawn by its shape's coordinates: glyph_card)
                struct.pack_into("<ff", v, 32, *struct.unpack_from("<ff", v, 40))
                new_vertex[key] = (len(new_vertex), bytes(v))
                return new_vertex[key][0]
            u, vv = struct.unpack_from("<ff", v, 32)
            if kind == "body" and u >= 0.5:
                kind = "head"
            struct.pack_into("<ff", v, 32, *remap_uv(u, vv, kind, layout))
            new_vertex[key] = (len(new_vertex), bytes(v))
        return new_vertex[key][0]

    def glyph_card(b):
        """A card today's shader 0x4011 draws from two textures of one file, additively: the
        Lightforged's runes, a scrolling band of light (its first coordinates, along the atlas's top)
        times the glyph (its second). 3.3.5 draws a batch's one texture by the first coordinates, which
        showed the band as a solid bar; the card takes its second, the glyph, which glows on its own.
        (Shader 0x4014, the eye glow's, has its colour in the first coordinates: it stays.)"""
        if b[2] != 0x4011 or b[8] != 2 or b[9] + 1 >= len(model.texture_lookup) or model.materials[b[6]][1] not in (3, 4, 7):
            return False
        first, second = model.texture_lookup[b[9]], model.texture_lookup[b[9] + 1]
        ids = model.texture_ids
        return first == second or (max(first, second) < len(ids) and ids[first] == ids[second] != 0)

    sections_by_id = {}
    for s, sec in enumerate(skin.sections):
        sections_by_id.setdefault(sec[0], []).append(s)
    batches_of = {}
    for b in skin.batches:
        batches_of.setdefault(b[3], []).append(b)
    plan = []                                           # (new geoset id, section index, batch)
    for old, news in geosets.items():
        for s in sections_by_id.get(int(old), []):
            for b in batches_of.get(s, []):
                kind = texture_types[model.texture_lookup[b[9]]]
                if kind not in KEPT_TYPES and kind != EYES and str(kind) not in hard:
                    continue
                for new in news:
                    plan.append((new, s, b))

    # The triangles of each section (as the model's vertex ids), cut down to what 3.3.5 can
    # address: it reads a section's triangle start as 16 bits, so every section has to begin
    # within the first 65535 indices. Today's models have twice that; the gear gives way first,
    # then the features and the hair, the body last (decimate.py).
    positions = np.array([struct.unpack_from("<3f", v) for v in model.vertices])
    source_tris = {}
    for new_id, s, b in plan:
        if s in source_tris:
            continue
        sec = skin.sections[s]
        first = sec[4] + sec[1] * 65536
        ks = np.array(skin.indices[first:first + sec[5]], dtype=np.int64)
        source_tris[s] = np.array(skin.vertices, dtype=np.int64)[ks].reshape(-1, 3)
    sizes = {}
    for new_id, s, b in plan:
        t = tier_of(new_id)
        sizes[t] = sizes.get(t, 0) + len(source_tris[s]) * 3
    cut = dict(source_tris)
    tier_of_section = {s: tier_of(new_id) for new_id, s, b in plan}
    # A pass takes what the floors allow; a mesh may not give all that was asked of it (its
    # outline and seams stay), so further passes ask for the rest, more from every tier.
    copies = {}
    for n, s, b in plan:
        copies[s] = copies.get(s, 0) + 1
    for step in range(12):
        now = {}
        for s, t in tier_of_section.items():
            now[t] = now.get(t, 0) + len(cut[s]) * 3 * copies[s]
        total = sum(now.values())
        if total <= INDEX_BUDGET:
            break
        floors = TIER_FLOORS if step == 0 else TIER_FLOORS_MORE if step == 1 else []
        keep = decimate.plan(now, INDEX_BUDGET - 300, floors)
        before = total
        for s, t in tier_of_section.items():
            fraction = keep[t]
            if fraction < 0.999 and len(cut[s]) > 2:
                cut[s] = decimate.decimate(positions, cut[s], max(1, int(round(len(cut[s]) * fraction))))
        total = sum(len(cut[s]) * 3 * copies[s] for s in tier_of_section)
        if total >= before:
            raise ValueError("%s: the meshes can't be cut to %d indices (%d)" % (name, INDEX_BUDGET, total))
    for t in sorted(sizes):
        kept = sum(len(cut[s]) * 3 for n, s, b in plan if tier_of(n) == t)
        log("%s: %s %.0f%% (%d of %d indices)" % (name, t, 100.0 * kept / max(1, sizes[t]), kept, sizes[t]))

    vertices_bytes = []
    for new_id, s, b in sorted(plan, key=lambda p: (tier_of(p[0]) == "body", p[0], p[1])):
        sec = skin.sections[s]
        kind = texture_types[model.texture_lookup[b[9]]]
        uv_kind = "eyes" if kind == EYES or sec[0] in eye_geosets else ("body" if kind == BODY else "same")
        if glyph_card(b):
            uv_kind = "second"
        # Each vertex's bones: the model's bone indices the vertex itself carries (the game,
        # drawing with a section's combo, puts a vertex on the bone its slot names there: the
        # combos made here must name these).
        bones_of = {}
        for g in set(int(v) for v in cut[s].ravel()):
            w = model.vertices[g][12:16]
            vb = model.vertices[g][16:20]
            bones_of[g] = [(vb[j], w[j]) for j in range(4) if w[j]]
        groups = []
        for tri in cut[s]:
            tri = tuple(int(v) for v in tri)
            used = {bone for g in tri for bone, _ in bones_of[g]}
            if not groups or len(set(groups[-1][0]) | used) > MAX_BONES:
                groups.append([[], []])
            palette = groups[-1][0]
            for bone in sorted(used):
                if bone not in palette:
                    palette.append(bone)
            groups[-1][1].append(tri)
        for palette, triangles in groups:
            place = {}
            vertex_start, index_start = len(out_vertices), len(out_indices)
            influences = 0
            for tri in triangles:
                for g in tri:
                    if g not in place:
                        place[g] = len(out_vertices)
                        out_vertices.append(vertex(g, uv_kind))
                        w = model.vertices[g][12:16]
                        slot = [0, 0, 0, 0]
                        n = 0
                        for j in range(4):
                            if w[j]:
                                slot[j] = palette.index(bones_of[g][n][0])
                                n += 1
                        influences = max(influences, n)
                        out_props.append(bytes(slot))
                    out_indices.append(place[g])
            combo_index = len(out_lookup)
            out_lookup.extend(palette)
            out_sections.append(struct.pack("<10H7f", new_id, 0, vertex_start, len(place),
                                            index_start, len(triangles) * 3, len(palette), combo_index,
                                            max(1, influences), sec[9], *sec[10:17]))
            texture = texture_index[model.texture_lookup[b[9]]]
            shader = 0x10 if textures[texture][0] in (CAPE, 0) and kind != EYES else 0
            flags = b[0] & 0x1F
            # (a glyph card's texture moves as its glyph's stage does, the second: the band's scroll,
            # the first, slid the atlas's glyphs across the card)
            transform = b[12] + 1 if uv_kind == "second" and b[12] + 1 < len(model.transform_lookup) else b[12]
            out_batches.append(struct.pack("<BbHHHhHHHHHHH", flags, b[1], shader, len(out_sections) - 1, len(out_sections) - 1,
                                           -1, b[6], 0, 1, texture, 0, b[11] if b[11] < len(model.transparency_lookup) else 0, transform))
    if len(out_vertices) > 65535:
        raise ValueError("%s: too many vertices for one skin (%d)" % (name, len(out_vertices)))
    if len(out_indices) > 65535:
        raise ValueError("%s: too many indices for one skin (%d): the game reads 16-bit starts" % (name, len(out_indices)))
    # vertices in the model: the ones drawn, in the skin's order, with their bones as the model's
    vertices = bytearray()
    for (index, kind), (new, data) in sorted(new_vertex.items(), key=lambda kv: kv[1][0]):
        vertices += data
    blob.array(60, len(new_vertex), bytes(vertices))
    struct.pack_into("<I", d, 68, 1)
    blob.array(120, len(out_lookup), struct.pack("<%dH" % len(out_lookup), *out_lookup))

    # The skin file.
    header = 48
    body = bytearray()

    def put(payload):
        while (header + len(body)) % 16:
            body.append(0)
        at = header + len(body)
        body.extend(payload)
        return at

    parts = [
        (len(out_vertices), put(struct.pack("<%dH" % len(out_vertices), *out_vertices))),
        (len(out_indices), put(struct.pack("<%dH" % len(out_indices), *out_indices))),
        (len(out_props), put(b"".join(out_props))),
        (len(out_sections), put(b"".join(out_sections))),
        (len(out_batches), put(b"".join(out_batches))),
    ]
    head = bytearray(b"SKIN")
    for count, offset in parts:
        head += struct.pack("<II", count, offset)
    head += struct.pack("<I", MAX_BONES)
    skin_out = bytes(head) + bytes(body)

    # Files.
    written = {}
    written["%s\\%s.m2" % (folder, name)] = bytes(blob.data)
    written["%s\\%s00.skin" % (folder, name)] = skin_out
    for j, (sid, var), fid in external:
        path = "%s\\%s%04d-%02d.anim" % (folder, name, sid, var)
        if path not in written:
            written[path] = anim_out[j]
    for fid, path in texture_names.items():
        written[path] = files(fid)
    for path, data in written.items():
        full = os.path.join(out_dir, path.replace("\\", "/"))
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "wb") as out:
            out.write(data)
    with open(os.path.join(out_dir, folder.replace("\\", "/"), name + ".layout.json"), "w") as out:
        json.dump({"head": layout, "eyes": [0.0, 0.625, 0.5, 0.75], "sequences": merged.n, "vertices": len(out_vertices),
                   "sections": len(out_sections), "textures": [(k, p) for k, _, p in textures]}, out, indent=1)
    log("%s: %d sequences (%d in their own files), %d bones, %d vertices, %d sections, %d textures" % (
        name, merged.n, len(external), len(child.bones), len(out_vertices), len(out_sections), len(textures)))
    return sorted(written)


def local(source):
    def read(file_id):
        for candidate in (str(file_id), "%d.m2" % file_id, os.path.join("anim", str(file_id)), os.path.join("tex", str(file_id))):
            path = os.path.join(source, candidate)
            if os.path.exists(path):
                with open(path, "rb") as f:
                    return f.read()
        raise FileNotFoundError(file_id)
    return read


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(2)
    with open(sys.argv[2]) as f:
        convert(local(sys.argv[1]), json.load(f), sys.argv[3])
