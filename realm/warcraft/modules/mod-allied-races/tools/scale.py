#!/usr/bin/env python3
"""The races' models at their kin's size: a converted model (3.3.5's format, tools/m2.py's output)
measured as the game poses it, and made larger or smaller all through to a height.

    python3 tools/scale.py MODEL.m2 [MODEL.m2...]           the models' heights
    python3 tools/scale.py MODEL.m2 --to HEIGHT              the model scaled to HEIGHT

The height is the head's: where its bone (key bone 6) is in the Stand animation's first moment,
the feet at 0, posed as render_m2.py poses a model. Ears, hair, horns and crests don't move it
(the nightborne's ears are in their body's mesh, the night elves' aren't), nor how the body
stoops above it. The old races measure the same in both HD patches the app offers (the
Alternative HD Patch's patch-A and ChromieCraft's Patch-H), KIN_HEIGHTS below.

Scaling makes the model larger about its origin (the point between the feet): the vertices, the
bones' pivots and every translation of their animations (the model's own and those in the .anim
files), the attachments, events and cameras, the bounds, the collision mesh and the skin's section
centres. Rotations and the bones' own scales stay as they are, so every pose is the old pose
scaled.
"""
import os
import struct
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_m2  # noqa: E402

# The old races' heights (male, female) as both HD patches draw them, measured as below: what the
# allied races are scaled to. Void elves are blood elves' size, the nightborne night elves', the
# Lightforged the Draenei's, the Zandalari the trolls' (the user: "Trolls to trolls. Draenei to
# draenei. Elves to elves.").
KIN_HEIGHTS = {
    "BloodElf": (1.868, 1.717),
    "NightElf": (2.212, 2.017),
    "Draenei": (2.251, 2.108),
    "Troll": (2.072, 2.136),
}
KIN = {"VoidElf": "BloodElf", "Nightborne": "NightElf", "LightforgedDraenei": "Draenei", "ZandalariTroll": "Troll"}
CLOSE_ENOUGH = 0.002            # within this (a fifth of a percent) a model is left as it is

HEAD = 6                        # the key bone that is the head


def height(path):
    """Where the head's bone is in Stand at 0 ms (the feet at 0)."""
    model = render_m2.Model(path)
    n, o = struct.unpack_from("<II", model.m, 52)
    keys = struct.unpack_from("<%dh" % n, model.m, o) if n else ()
    if len(keys) <= HEAD or keys[HEAD] < 0:
        raise ValueError("%s: no head bone" % path)
    bone = keys[HEAD]
    seq = next((i for i, s in enumerate(model.seqs) if s[0] == 0 and s[1] == 0), 0)
    world = model.bone_matrices(seq, 0)[bone]
    return float((world[:3, :3] @ model.bones[bone][5] + world[:3, 3])[2])


def target_height(name):
    """The height a model of ours (VoidElfMale...) is made, None for another model."""
    for race, kin in KIN.items():
        for sex, suffix in enumerate(("Male", "Female")):
            if name == race + suffix:
                return KIN_HEIGHTS[kin][sex]
    return None


def scale_floats(data, at, count, factor):
    if count:
        values = np.frombuffer(bytes(data[at:at + count * 4]), dtype="<f4") * np.float32(factor)
        data[at:at + count * 4] = values.astype("<f4").tobytes()


def scale(path, factor, log=print):
    """Scales the model at [path] (its .skin and .anim files beside it) by [factor], in place.
    Returns the files changed."""
    folder = os.path.dirname(path)
    name = os.path.splitext(os.path.basename(path))[0]
    m = bytearray(open(path, "rb").read())
    if m[:4] != b"MD20":
        raise ValueError("not a 3.3.5 model: " + path)

    def arr(at):
        return struct.unpack_from("<II", m, at)

    n, o = arr(28)
    seqs = [struct.unpack_from("<HHIfI", m, o + i * 64) for i in range(n)]
    anims = {}                                  # sequence index -> bytearray of its .anim file

    def anim(i):
        if i not in anims:
            p = os.path.join(folder, "%s%04d-%02d.anim" % (name, seqs[i][0], seqs[i][1]))
            anims[i] = (p, bytearray(open(p, "rb").read())) if os.path.exists(p) else (p, None)
        return anims[i][1]

    done = set()                                # (file, offset): data scaled once, however many tracks share it

    def track(at, floats):
        """A track's values, [floats] floats each."""
        interp, gseq, tn, to, vn, vo = struct.unpack_from("<hhIIII", m, at)
        for i in range(vn):
            count, offset = struct.unpack_from("<II", m, vo + i * 8)
            if not count:
                continue
            external = gseq < 0 and i < len(seqs) and not seqs[i][4] & 0x20
            data = anim(i) if external else m
            if data is None:
                continue
            key = (anims[i][0] if external else None, offset)
            if key in done:
                continue
            done.add(key)
            scale_floats(data, offset, count * floats, factor)

    # vertices: their positions
    n, o = arr(60)
    for i in range(n):
        scale_floats(m, o + i * 48, 3, factor)
    # bones: the translations and the pivot
    n, o = arr(44)
    for i in range(n):
        at = o + i * 88
        track(at + 16, 3)
        scale_floats(m, at + 76, 3, factor)
    # bounds (the box and radius, the collision box and radius) and the collision mesh
    scale_floats(m, 160, 14, factor)
    n, o = arr(224)
    scale_floats(m, o, n * 3, factor)
    # attachments and events: where they are on their bones
    n, o = arr(240)
    for i in range(n):
        scale_floats(m, o + i * 40 + 8, 3, factor)
    n, o = arr(256)
    for i in range(n):
        scale_floats(m, o + i * 36 + 12, 3, factor)
    # cameras: where they are and look, with their tracks (a value and two tangents a key)
    n, o = arr(272)
    for i in range(n):
        at = o + i * 100
        track(at + 16, 9)
        scale_floats(m, at + 36, 3, factor)
        track(at + 48, 9)
        scale_floats(m, at + 68, 3, factor)

    changed = [path]
    with open(path, "wb") as out:
        out.write(m)
    for p, data in anims.values():
        if data is not None:
            with open(p, "wb") as out:
                out.write(data)
            changed.append(p)
    # the skin: each section's centre and sort centre and radius
    skin_path = os.path.join(folder, name + "00.skin")
    s = bytearray(open(skin_path, "rb").read())
    sn, so = struct.unpack_from("<II", s, 28)
    for i in range(sn):
        scale_floats(s, so + i * 48 + 20, 7, factor)
    with open(skin_path, "wb") as out:
        out.write(s)
    changed.append(skin_path)
    log("%s: scaled by %.4f (%d animation files)" % (name, factor, len(changed) - 2))
    return changed


def to_kin(path, log=print):
    """The model of ours at [path] made its kin's height (tools/package.py calls this as it makes
    the models). Returns the factor (1 when it was close enough already, or isn't ours)."""
    name = os.path.splitext(os.path.basename(path))[0]
    want = target_height(name)
    if want is None:
        return 1.0
    have = height(path)
    factor = want / have
    if abs(factor - 1.0) <= CLOSE_ENOUGH:
        log("%s: %.3f tall, as its kin (%.3f)" % (name, have, want))
        return 1.0
    scale(path, factor, log)
    log("%s: %.3f tall, now %.3f (its kin's %.3f)" % (name, have, height(path), want))
    return factor


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    if "--to" in args:
        i = args.index("--to")
        want = float(args[i + 1])
        for path in args[:i]:
            scale(path, want / height(path))
            print("%s: %.3f" % (path, height(path)))
    else:
        for path in args:
            print("%s: %.3f" % (path, height(path)))
