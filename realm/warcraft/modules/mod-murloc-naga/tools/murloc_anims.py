# SPDX-License-Identifier: GPL-3.0-or-later
"""Emotes for the murlocs: the game's murloc models (the classic one, and Blizzard's newer murloc2 the
race wears) have no emote animations (talk, point, cheer, bow, cry, kneel...: an emote plays nothing on
them), and show-not-tell needs them. The murloc costume (creature/murloccostume, BlizzCon 2007's, made
to be worn by players) has every one, on a skeleton built like murloc2's: the same root, spine, chest,
head and jaw, arms that hang the same way from the shoulders to the fingers, legs in the same order.
Its emotes are added to a converted murloc2 (tools/murloc_model.py) as sequences of their own, each bone
murloc2 has turned as the costume's is (a bone's rotation is about its own pivot, from the pose the
model is made in: the same on both), its moves scaled to murloc2's height; a bone the costume hasn't, and
everything else that animates (colours, attachments), as it is when murloc2 stands.

    add_emotes(model, costume, bones, scale)   model: a 3.3.5 murloc2 (bytearray, changed in place);
                                               costume: the newer format's murloccostume (its MD21);
                                               bones: {costume bone: murloc2 bone}; returns the ids added
"""
import struct

import numpy as np

SEQUENCE = 64
H_SEQUENCES, H_LOOKUP, H_BONES, H_COLOURS, H_WEIGHTS, H_UV, H_ATTACH, H_CAMERAS = 0x1C, 0x24, 0x2C, 0x48, 0x58, 0x60, 0xF0, 0x110
H_EVENTS, H_LIGHTS, H_RIBBONS, H_PARTICLES = 0x100, 0x108, 0x120, 0x128
NO_VALUES = 0                    # (an event's track: times alone)
IN_MODEL = 0x20

# The costume's bones as murloc2's (both skeletons' indices; tools/murloc_looks.py names the models).
COSTUME_BONES = {
    1: 1, 2: 2, 4: 5, 8: 9, 20: 15,                                   # root, spine, chest, head, jaw
    9: 8, 22: 13, 27: 22, 32: 24, 33: 25, 67: 62, 69: 65,             # left arm: shoulder, elbow, hand, fingers
    10: 10, 23: 19, 28: 23, 34: 26, 35: 27, 68: 61, 70: 66,           # right arm
    6: 3, 17: 6, 24: 11, 29: 20,                                      # left leg: hip, knee, ankle, toes
    7: 4, 18: 7, 25: 12, 30: 21,                                      # right leg
    64: 58, 65: 59, 66: 57, 63: 56, 61: 54, 62: 55,                   # breath, head's attachments
}


def _arr(m, at):
    return struct.unpack_from("<II", m, at)


def tracks(m):
    """[(offset of an M2Track, value size, bone index or None, which: 0 translation, 1 rotation, 2 scale)]"""
    out = []
    n, at = _arr(m, H_BONES)
    for b in range(n):
        out += [(at + b * 88 + 16, 12, b, 0), (at + b * 88 + 36, 8, b, 1), (at + b * 88 + 56, 12, b, 2)]
    n, at = _arr(m, H_COLOURS)
    out += [(at + c * 40 + off, size, None, None) for c in range(n) for off, size in ((0, 12), (20, 2))]
    n, at = _arr(m, H_WEIGHTS)
    out += [(at + w * 20, 2, None, None) for w in range(n)]
    n, at = _arr(m, H_UV)
    out += [(at + t * 60 + off, size, None, None) for t in range(n) for off, size in ((0, 12), (20, 16), (40, 12))]
    n, at = _arr(m, H_ATTACH)
    out += [(at + a * 40 + 20, 1, None, None) for a in range(n)]
    n, at = _arr(m, H_CAMERAS)
    out += [(at + c * 100 + off, size, None, None) for c in range(n) for off, size in ((16, 36), (48, 36), (80, 12))]
    n, at = _arr(m, H_EVENTS)
    out += [(at + e * 36 + 24, NO_VALUES, None, None) for e in range(n)]
    for header in (H_LIGHTS, H_RIBBONS, H_PARTICLES):
        if _arr(m, header)[0]:
            raise ValueError("a model with lights, ribbons or particles: their tracks aren't known here")
    return out


def _append(data, block):
    while len(data) % 16:
        data.append(0)
    at = len(data)
    data += block
    return at


def _keys(md21, track_at, seq, size):
    """The costume's keys of a track for a sequence: (times, raw values) or None."""
    interp, gseq = struct.unpack_from("<Hh", md21, track_at)
    tn, to = _arr(md21, track_at + 4)
    vn, vo = _arr(md21, track_at + 12)
    if gseq >= 0 or seq >= tn or seq >= vn:
        return None
    n, at = _arr(md21, to + 8 * seq)
    vcount, vat = _arr(md21, vo + 8 * seq)
    if n == 0 or vcount != n:
        return None
    return interp, md21[at:at + 4 * n], md21[vat:vat + size * n], n


def add_emotes(model, costume, bones=COSTUME_BONES, scale=1.0, skip=()):
    m = model
    seq_n, seq_at = _arr(m, H_SEQUENCES)
    ids = [struct.unpack_from("<H", m, seq_at + SEQUENCE * k)[0] for k in range(seq_n)]
    stand = next(k for k in range(seq_n) if ids[k] == 0)
    c_n, c_at = _arr(costume, H_SEQUENCES)
    have = set(ids) | set(skip)
    new = []                                    # (costume sequence, its record)
    for k in range(c_n):
        rec = bytearray(costume[c_at + SEQUENCE * k:c_at + SEQUENCE * (k + 1)])
        anim, variation = struct.unpack_from("<HH", rec, 0)
        if anim in have or variation != 0:
            continue
        new.append((k, rec))
    if not new:
        return []
    # the sequences: the model's, then the costume's emotes (kept in the model, their bounds murloc2's)
    stand_rec = m[seq_at + SEQUENCE * stand:seq_at + SEQUENCE * (stand + 1)]
    records = bytearray(m[seq_at:seq_at + SEQUENCE * seq_n])
    for n, (k, rec) in enumerate(new):
        flags = struct.unpack_from("<I", rec, 12)[0]
        struct.pack_into("<I", rec, 12, flags | IN_MODEL)
        rec[32:60] = stand_rec[32:60]                                  # (murloc2's bounds)
        struct.pack_into("<hH", rec, 60, -1, seq_n + n)                 # no variation after it; itself
        records += rec
    struct.pack_into("<II", m, H_SEQUENCES, seq_n + len(new), _append(m, records))
    total = seq_n + len(new)
    ids += [struct.unpack_from("<H", rec, 0)[0] for _, rec in new]
    # the lookup by animation id: each id its own slot
    size = max(ids) + 1
    lookup = [-1] * size
    for k, a in enumerate(ids):
        if lookup[a] < 0:
            lookup[a] = k
    struct.pack_into("<II", m, H_LOOKUP, size, _append(m, struct.pack(f"<{size}h", *lookup)))
    # every track: its sets for the new sequences (a mapped bone's, the costume's keys; anything else,
    # its stand's)
    c_bones = {v: k for k, v in bones.items()}
    c_bone_at = _arr(costume, H_BONES)[1]
    added = 0
    for at, size, bone, which in tracks(bytes(m)):
        interp, gseq = struct.unpack_from("<Hh", m, at)
        if gseq >= 0:
            continue
        tn, to = _arr(m, at + 4)
        vn, vo = _arr(m, at + 12) if size else (tn, 0)
        source = None
        if bone is not None and bone in c_bones:
            source = c_bone_at + c_bones[bone] * 88 + 16 + 20 * which
        sets = []
        for k, _ in new:
            keys = _keys(costume, source, k, size) if source is not None else None
            if keys is not None:
                c_interp, times, values, n = keys
                if which == 0 and scale != 1.0:
                    values = (np.frombuffer(values, "<f4") * np.float32(scale)).astype("<f4").tobytes()
                sets.append((n, times, values))
                added += 1
            else:
                sets.append(None)
        if tn == 0 and all(s is None for s in sets):
            continue                                                   # (never animated: as it is)
        if tn not in (0, seq_n) or vn != tn:
            raise ValueError(f"a track with {tn} sets for {seq_n} sequences")
        old_t = m[to:to + 8 * tn] if tn else b"\0" * (8 * seq_n)
        old_v = (m[vo:vo + 8 * vn] if vn else b"\0" * (8 * seq_n)) if size else b"\0" * (8 * max(tn, seq_n))
        stand_t = old_t[8 * stand:8 * stand + 8]
        stand_v = old_v[8 * stand:8 * stand + 8]
        new_t, new_v = bytearray(old_t), bytearray(old_v)
        for s in sets:
            if s is None:
                new_t += stand_t
                new_v += stand_v
            else:
                n, times, values = s
                new_t += struct.pack("<II", n, _append(m, times))
                new_v += struct.pack("<II", n, _append(m, values))
        struct.pack_into("<II", m, at + 4, total, _append(m, new_t))
        if size:
            struct.pack_into("<II", m, at + 12, total, _append(m, new_v))
        if tn == 0 and interp == 0:
            struct.pack_into("<H", m, at, 1)                           # (keys of its own now: linear)
    # an animated bone: flagged so (the game skips the matrices of bones that never move)
    n, bat = _arr(m, H_BONES)
    for b in set(bones.values()):
        if b < n:
            flags = struct.unpack_from("<I", m, bat + b * 88 + 4)[0]
            struct.pack_into("<I", m, bat + b * 88 + 4, flags | 0x200)
    return [struct.unpack_from("<H", rec, 0)[0] for _, rec in new], added
