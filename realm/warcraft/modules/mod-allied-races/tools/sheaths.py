#!/usr/bin/env python3
"""The races' weapons on their backs as their kin wear them: a converted model's back sheath
attachments (3.3.5's 26 and 27, the main and off hand's sheathed weapon; 28, the shield; 30 and 31,
the large weapons) turned to the way the old races' face in Stand.

    python3 tools/sheaths.py MODEL.m2 [MODEL.m2...]     turns the models' sheaths, in place

Today's game turns a sheathed weapon by data of its own, which 3.3.5 hasn't: our models' sheath
points face forward, and a staff on a void elf's back went through her chest. data/sheaths.json has
each kin's sheath points' orientation in Stand's first moment (measured on the Alternative HD
Patch's models; ChromieCraft's HD patch has the same skeletons), as quaternions (x, y, z, w). Each
sheath point gets a bone of its own, a child of the bone it was on, turned by the rotation that
brings that bone's orientation to the kin's (a constant, on a global sequence), its pivot the
sheath point: the weapon sits as the kin's does in Stand and moves with the body as before.
"""
import json
import os
import struct
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_m2  # noqa: E402

MODULE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAMES = os.path.join(MODULE, "data", "sheaths.json")
SHEATHS = (26, 27, 28, 30, 31)
KIN = {"VoidElf": "BloodElf", "Nightborne": "NightElf", "LightforgedDraenei": "Draenei", "ZandalariTroll": "Troll"}
BONE = 88


def matrix(q):
    x, y, z, w = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def quaternion(m):
    t = np.trace(m)
    if t > 0:
        s = np.sqrt(t + 1) * 2
        q = [(m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s, (m[1, 0] - m[0, 1]) / s, s / 4]
    else:
        i = int(np.argmax(np.diag(m)))
        if i == 0:
            s = np.sqrt(1 + m[0, 0] - m[1, 1] - m[2, 2]) * 2
            q = [s / 4, (m[0, 1] + m[1, 0]) / s, (m[0, 2] + m[2, 0]) / s, (m[2, 1] - m[1, 2]) / s]
        elif i == 1:
            s = np.sqrt(1 + m[1, 1] - m[0, 0] - m[2, 2]) * 2
            q = [(m[0, 1] + m[1, 0]) / s, s / 4, (m[1, 2] + m[2, 1]) / s, (m[0, 2] - m[2, 0]) / s]
        else:
            s = np.sqrt(1 + m[2, 2] - m[0, 0] - m[1, 1]) * 2
            q = [(m[0, 2] + m[2, 0]) / s, (m[1, 2] + m[2, 1]) / s, s / 4, (m[1, 0] - m[0, 1]) / s]
    q = np.array(q)
    return q / np.linalg.norm(q)


def packed(q):
    """A quaternion as 3.3.5 keeps one: four shorts, render_m2.py's reading reversed."""
    out = []
    for f in q:
        f = max(-1.0, min(1.0, float(f)))
        # (render_m2.py reads a short below 0 as raw + 32767, else raw - 32767, over 32767)
        v = int(round(f * 32767 - 32767)) if f >= 0 else int(round(f * 32767 + 32767))
        out.append(max(-32768, min(32767, v)))
    return struct.pack("<4h", *out)


def frames_for(name):
    """The kin's sheath orientations for a model of ours (VoidElfMale...), or None."""
    with open(FRAMES) as f:
        frames = json.load(f)
    for race, kin in KIN.items():
        for sex in ("Male", "Female"):
            if name == race + sex:
                return {int(k): v for k, v in frames[kin][sex].items()}
    return None


def turn(path, log=print):
    """Gives the model at [path] its kin's sheaths. Returns how many it turned."""
    name = os.path.splitext(os.path.basename(path))[0]
    frames = frames_for(name)
    if not frames:
        return 0
    model = render_m2.Model(path)
    seq = next((i for i, s in enumerate(model.seqs) if s[0] == 0 and s[1] == 0), 0)
    world = model.bone_matrices(seq, 0)
    m = bytearray(model.m)

    def arr(at):
        return struct.unpack_from("<II", m, at)

    def append(payload, align=16):
        while len(m) % align:
            m.append(0)
        at = len(m)
        m.extend(payload)
        return at

    loops_n, loops_at = arr(20)
    loops = list(struct.unpack_from("<%dI" % loops_n, m, loops_at)) if loops_n else []
    gseq = len(loops)
    loops.append(1)                                   # a loop of a moment: the one key always
    bones_n, bones_at = arr(44)
    bones = bytearray(m[bones_at:bones_at + bones_n * BONE])
    att_n, att_at = arr(240)
    empty = struct.pack("<hhIIII", 0, -1, 0, 0, 0, 0)
    turned = 0
    for i in range(att_n):
        at = att_at + i * 40
        aid, bone = struct.unpack_from("<IH", m, at)
        if aid not in frames or bone >= bones_n:
            continue
        position = struct.unpack_from("<3f", m, at + 8)
        r = world[bone][:3, :3]
        r = r / np.cbrt(abs(np.linalg.det(r)))           # (a scaled bone's scale left out)
        local = r.T @ matrix(frames[aid])                 # from the bone's orientation to the kin's
        times = append(struct.pack("<I", 0), 4)
        values = append(packed(quaternion(local)), 4)
        ts = append(struct.pack("<II", 1, times), 4)
        vs = append(struct.pack("<II", 1, values), 4)
        rotation = struct.pack("<hhIIII", 1, gseq, 1, ts, 1, vs)
        bones += struct.pack("<iIhHI", -1, 0x200, bone, 0, 0) + empty + rotation + empty + struct.pack("<3f", *position)
        struct.pack_into("<H", m, at + 4, bones_n + turned)
        turned += 1
    if not turned:
        return 0
    struct.pack_into("<II", m, 44, bones_n + turned, append(bytes(bones)))
    struct.pack_into("<II", m, 20, len(loops), append(struct.pack("<%dI" % len(loops), *loops)))
    with open(path, "wb") as out:
        out.write(m)
    log("%s: %d sheaths turned as its kin's" % (name, turned))
    return turned


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    for p in sys.argv[1:]:
        turn(p)
