#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""The murlocs' character models (tools/murloc_model.py's output) drawn as the game would draw them at
character creation: each hair style, feature, skin colour and eye colour, in a contact sheet, with
mod-allied-races' renderer (tools/render_m2.py: its reading of the files, not the game).

    python3 tools/render_murloc.py FILES OUT.png

FILES: tools/murloc_model.py's output folder. Needs numpy and Pillow.
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "mod-allied-races", "tools"))
import murloc_looks as L  # noqa: E402
import render_m2 as R  # noqa: E402
import blp  # noqa: E402

COMPOSED = 512


def texture(files, name):
    return np.asarray(blp.read(open(os.path.join(files, *name.split("/")), "rb").read()))


def composed(files, eyes, skin):
    """The composed texture: the base, then the face row's FaceUpper and FaceLower in their regions."""
    out = np.array(Image.fromarray(texture(files, "Character/Murloc/MurlocBase.blp")).convert("RGBA").resize((L.COMPOSED, L.COMPOSED)))
    for name, (x0, y0, x1, y1) in ((L.face_lower(skin), L.FACE_LOWER), (L.face_upper(eyes, skin), L.FACE_UPPER)):
        out[y0:y1, x0:x1] = np.asarray(Image.fromarray(texture(files, name.replace("\\", "/"))).convert("RGBA"))
    return out


def draw(files, sex, skin, eyes, fins, feature, fin_colour=0, size=(220, 300), yaw=0.0):
    path = os.path.join(files, "Character", "Murloc", sex, "Murloc%s.m2" % sex)
    model = R.Model(path)
    skin_file = R.Skin(os.path.join(os.path.dirname(path), "Murloc%s00.skin" % sex))
    seq = next((i for i, s in enumerate(model.seqs) if s[0] == 0), 0)
    world = model.bone_matrices(seq, 400)
    shown = {0, L.fin_geoset(fins), 100 + L.feature_geoset(feature)}
    cam = model.camera(1, seq, 400) or model.camera(0, seq, 400)
    if yaw:
        import math
        fov, near, far, eye, target = cam
        e = np.array(eye) - np.array(target)
        c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
        e = np.array([e[0] * c - e[1] * s, e[0] * s + e[1] * c, e[2]])
        cam = (fov, near, far, tuple(np.array(target) + e), target)
    light = np.array([1.0, 0.6, 1.2])
    light /= np.linalg.norm(light)
    hair = texture(files, L.fin_texture(fins, fin_colour).replace("\\", "/"))
    image, drawn = R.render(model, skin_file, composed(files, eyes, skin), hair, files, shown, world, cam, size, light)
    return image


def main():
    files, out = sys.argv[1], sys.argv[2]
    small = (150, 200)
    rows = []
    # each fin style, front and side; each feature (a woman's)
    rows.append(np.concatenate([draw(files, "Male", 1, 1, s, 0, 0, yaw=y) for s in range(len(L.FIN_STYLES)) for y in (0, 70)], axis=1))
    for sex in ("Male", "Female"):
        rows.append(np.concatenate([draw(files, sex, 2, 4, 0, f, 1, size=small) for f in range(len(L.FEATURES[sex]))], axis=1))
    rows.append(np.concatenate([draw(files, "Male", s, 1, 0, 0, 0, size=small) for s in range(len(L.SKINS))], axis=1))
    rows.append(np.concatenate([draw(files, "Female", 3, 0, 4, 0, c, size=small, yaw=40) for c in range(len(L.FIN_COLOURS))], axis=1))
    rows.append(np.concatenate([draw(files, "Male", 1, e, 0, 0, 0, size=(110, 150))[:75] for e in range(len(L.EYE_COLOURS))], axis=1))
    width = max(r.shape[1] for r in rows)
    sheet = np.concatenate([np.pad(r, ((0, 0), (0, width - r.shape[1]), (0, 0))) for r in rows], axis=0)
    Image.fromarray(sheet).save(out)
    print(out, sheet.shape)


if __name__ == "__main__":
    main()
