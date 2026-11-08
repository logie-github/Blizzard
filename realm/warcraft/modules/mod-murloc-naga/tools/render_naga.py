#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""The naga's story's models drawn to contact sheets, with mod-allied-races' renderer (tools/render_m2.py:
its reading of the files, not the game), to check them by eye:

    python3 tools/render_naga.py creatures FILES OUT.png
        tools/naga_models.py's models (FILES: its output folder): each at its stand and in its emotes;
    python3 tools/render_naga.py emotes MODEL.m2 SEX TEXTURES OUT.png [--side]
        a naga model with tools/naga_emotes.py's emotes merged in (the patch's: tools/test_patch.cpp
        --dump writes it), each new animation at its start, middle and end; SEX 0 or 1; TEXTURES: the
        client's files (its naga skins, by the paths the module's CharSections rows name).

Needs numpy and Pillow.
"""
import math
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "mod-allied-races", "tools"))
import blp  # noqa: E402
import naga_emotes as NE  # noqa: E402
import render_m2 as R  # noqa: E402
from naga import looks as LK  # noqa: E402

DBC = os.path.join(HERE, "..", "data", "client", "dbc")
CREATURE_ANIMS = [0, 60, 66, 67, 68, 70, 75, 84, 113, 97, 91, 100, 55, 125, 109]


def frame(model, skin, anim, t, size, yaw, height, texture=None, hair=None, files="", skins=None):
    seq = next((i for i, s in enumerate(model.seqs) if s[0] == anim and s[1] == 0), None)
    if seq is None:
        return None
    if model.seqs[seq][4] & NE.ALIAS:                         # (an alias: its sequence's index, at its record's byte 62)
        seq = int.from_bytes(model.m[R.arr(model.m, 28)[1] + 64 * seq + 62:][:2], "little")
    world = model.bone_matrices(seq, t)
    present = {s[0] for s in skin.sections}
    shown = present if skins is not None else {g for g in present if g == 0 or g % 100 == 1 or g == 702}
    target = np.array([0.0, 0.0, height * 0.5])
    c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    e = np.array([height * 2.3 * c, height * 2.3 * s, height * 0.25])
    light = np.array([1.0, 0.6, 1.2])
    light /= np.linalg.norm(light)
    saved, original = list(model.textures), R.read_blp
    if skins is not None:                     # (a creature's skins, put in as files the renderer reads)
        for i, (kind, _) in enumerate(saved):
            if kind in (11, 12, 13) and skins[kind - 11] is not None:
                model.textures[i] = (0, "\0skin%d" % (kind - 11))
        R.read_blp = lambda f, p: skins[int(p[5:])] if p.startswith("\0skin") else original(f, p)
    try:
        image, _ = R.render(model, skin, texture, hair, files, shown, world, (0.75, 0.1, 100.0, target + e, target), size, light)
    finally:
        R.read_blp = original
        model.textures[:] = saved
    return image


def sheet(rows, out):
    rows = [r for r in rows if r]
    width = max(sum(i.shape[1] for i in r) for r in rows)
    lines = [np.pad(np.concatenate(r, axis=1), ((0, 0), (0, width - sum(i.shape[1] for i in r)), (0, 0))) for r in rows]
    Image.fromarray(np.concatenate(lines, axis=0)).save(out)
    print(out, len(rows), "rows")


def creatures(files, out):
    rows = []
    for c in LK.CREATURES:
        path = os.path.join(files, *c["folder"].split("/"), c["name"] + ".m2")
        model, skin = R.Model(path), R.Skin(path[:-3] + "00.skin")
        names = next(s for d, (m, _, _, s) in sorted(LK.CREATURE_LOOKS.items()) if m == c["model_data"])
        skins = [np.asarray(blp.read(open(os.path.join(os.path.dirname(path), n + ".blp"), "rb").read())) if n else None for n in names]
        height = max(1.0, float(model.pos[:, 2].max()))
        row = []
        for anim in CREATURE_ANIMS:
            seq = next((s for s in model.seqs if s[0] == anim and s[1] == 0), None)
            if seq is None:
                continue
            image = frame(model, skin, anim, min(900, seq[2] // 2), (170, 220), 20.0, height, files=files, skins=skins)
            if image is not None:
                row.append(image)
        rows.append(row)
    sheet(rows, out)


def emotes(path, sex, textures, out, side=False):
    model, skin = R.Model(path), R.Skin(path[:-3] + "00.skin")
    texture, hair = R.compose(textures, DBC, 20, sex, 0, 0, 0)
    rows = []
    for anim, _ in NE.EMOTES:
        seq = next((s for s in model.seqs if s[0] == anim and s[1] == 0), None)
        if seq is None or seq[4] & NE.ALIAS:
            continue
        length = seq[2]
        row = [frame(model, skin, anim, t, (150, 190), 70.0 if side else 15.0, 2.4, texture, hair, textures)
               for t in (0, length // 2, length)]
        rows.append([i for i in row if i is not None])
    sheet(rows, out)


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "creatures":
        creatures(sys.argv[2], sys.argv[3])
    elif len(sys.argv) in (6, 7) and sys.argv[1] == "emotes":
        emotes(sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5], side="--side" in sys.argv[6:])
    else:
        print(__doc__)
        sys.exit(2)
