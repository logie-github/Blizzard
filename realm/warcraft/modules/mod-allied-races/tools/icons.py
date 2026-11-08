#!/usr/bin/env python3
"""The races' portraits for the character creation screen's race icons: Wowhead's race icons
(data/client/icons/*.jpg, 56 x 56) made 128 x 128 DXT textures (data/client/icons/*.blp) the
patch paints into the game's icon sheets (AlliedRacesPatch.cpp). Their output is committed; run
it again after changing a picture.

    python3 tools/icons.py
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import blp  # noqa: E402

ICONS = os.path.join(os.path.dirname(HERE), "data", "client", "icons")
SIZE = 128

for name in sorted(os.listdir(ICONS)):
    if not name.endswith(".jpg"):
        continue
    image = Image.open(os.path.join(ICONS, name)).convert("RGBA").resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    rgba = np.array(image)
    rgba[:, :, 3] = 255
    out = os.path.join(ICONS, name[:-4] + ".blp")
    with open(out, "wb") as f:
        f.write(blp.write_dxt(rgba, alpha=False, mips=False))
    print(out, rgba.shape)
