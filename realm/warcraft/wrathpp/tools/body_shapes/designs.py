"""The body layer's design maps drawn by code, for the package CI makes (`.github/workflows/wrathpp-body.yml`): usage

  designs.py OUT_DIR

One map a style (masks.py reads them: RGB a shade, 0 the hair colour's dark to 255 its light; A the coverage), every one
on the same 200 x 200 frame: the middle of the body at column 97, the top of the cleft at row 125, about 1.7 mm a pixel
(`full_natural` is the width masks.py takes as 13 cm). Nothing here is anyone's art: a shape, filled with short strands
from a seeded generator, a few reaching past its edge as hair does; the two factions' styles are plain stand-ins (a
shield with a cross, a spiked banner), not the game's crests. A package made by hand may be given maps of your own in
their place (pack2.py's MAPS_DIR; the first packages' came from the user's own files and were never in the repository).
The same seed gives the same maps."""
import json
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

N, F = 200, 4                       # the frame, and how much larger it is drawn before it is made small
CX, CY = 97, 125


def px(x, y):
    """x across from the middle, y up from the top of the cleft, in the frame's pixels: where that is on the large canvas."""
    return ((CX + x) * F, (CY - y) * F)


def poly(points):
    return lambda d: d.polygon([px(x, y) for x, y in points], fill=255)


def disc(x, y, r, fill=255):
    return lambda d: d.ellipse([px(x - r, y + r), px(x + r, y - r)], fill=fill)


def star(cx, cy, R, r, n=5):
    pts = []
    for k in range(2 * n):
        a = math.pi / 2 + k * math.pi / n
        rr = R if k % 2 == 0 else r
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return poly(pts)


def heart(cx, top, w):
    r = w / 4.0
    return [disc(cx - r, top - r, r), disc(cx + r, top - r, r), poly([(cx - 2 * r + 0.3, top - r - 0.6 * r), (cx + 2 * r - 0.3, top - r - 0.6 * r), (cx, top - 2.2 * w / 2)])]


def bar(x0, y0, x1, y1, w):
    return lambda d: d.line([px(x0, y0), px(x1, y1)], fill=255, width=int(w * F))


# each style: what is drawn (in order; a fill of 0 cuts out)
SHAPES = {
    "full_natural": [poly([(-38, 50), (38, 50), (30, 30), (9, 0), (0, -8), (-9, 0), (-30, 30)])],
    "natural": [poly([(-30, 44), (30, 44), (0, -2)])],
    "small_triangle": [poly([(-17, 32), (17, 32), (0, 3)])],
    "heart": heart(0, 36, 30),
    "strip": [poly([(-5, 42), (5, 42), (5, 3), (-5, 3)])],
    "wild": [poly([(-44, 58), (44, 58), (40, 22), (12, -6), (0, -12), (-12, -6), (-40, 22)])],
    "moon": [disc(0, 26, 20), disc(9, 30, 17, fill=0)],
    "star": [star(0, 26, 23, 9.5)],
    "diamond": [poly([(0, 50), (18, 26), (0, 3), (-18, 26)])],
    "flame": [poly([(0, 56), (9, 40), (17, 26), (15, 12), (7, 4), (0, 2), (-7, 4), (-15, 12), (-17, 26), (-8, 34), (-6, 46)])],
    "bolt": [poly([(6, 54), (-14, 26), (-2, 26), (-8, 2), (14, 32), (2, 32)])],
    "swords": [bar(-16, 46, 14, 6, 4), bar(16, 46, -14, 6, 4), bar(-21, 37, -9, 46, 3), bar(21, 37, 9, 46, 3)],
    "skull": [disc(0, 32, 17), poly([(-10, 22), (10, 22), (8, 6), (-8, 6)]), disc(-7, 31, 4.5, fill=0), disc(7, 31, 4.5, fill=0),
              poly([(-1.5, 22), (1.5, 22), (0, 27)]), ],
    "heart_large": heart(0, 52, 48),
    "triangle_large": [poly([(-34, 46), (34, 46), (0, -2)])],
    "alliance": [poly([(-19, 52), (19, 52), (19, 26), (0, 3), (-19, 26)]), lambda d: d.line([px(0, 46), px(0, 14)], fill=0, width=5 * F),
                 lambda d: d.line([px(-12, 36), px(12, 36)], fill=0, width=5 * F)],
    "horde": [poly([(0, 56), (8, 40), (24, 50), (16, 28), (8, 20), (0, 3), (-8, 20), (-16, 28), (-24, 50), (-8, 40)]), disc(0, 30, 5, fill=0)],
}
SHORT = {"skull", "swords", "horde", "alliance", "star", "bolt", "moon"}        # fine shapes: shorter strands past the edge


def design(name, seed):
    rng = np.random.default_rng(seed)
    big = Image.new("L", (N * F, N * F), 0)
    d = ImageDraw.Draw(big)
    for draw in SHAPES[name]:
        draw(d)
    mask = np.asarray(big.filter(ImageFilter.GaussianBlur(0.6 * F))).astype(np.float32) / 255
    # the strands' shade: short strokes, dark and light, all over; then those rooted at the edge, which add coverage
    shade = Image.new("L", (N * F, N * F), 110)
    edge = Image.new("L", (N * F, N * F), 0)
    ds, de = ImageDraw.Draw(shade), ImageDraw.Draw(edge)

    def stroke(x, y, length, into, value, width):
        ang = rng.uniform(0, 2 * math.pi)
        curl = rng.choice([-1, 1]) * rng.uniform(0.2, 0.6)
        pts = []
        for _ in range(7):
            pts.append((x, y))
            x += math.cos(ang) * length / 6
            y += math.sin(ang) * length / 6
            ang += curl + rng.normal(0, 0.15)
        into.line(pts, fill=int(value), width=width)

    ys, xs = np.where(mask > 0.5)
    if len(xs) == 0:
        raise SystemExit("%s: nothing drawn" % name)
    for j in rng.integers(0, len(xs), max(400, len(xs) // 14)):
        stroke(xs[j], ys[j], rng.uniform(4, 9) * F, ds, 255 * min(1.0, rng.beta(1.6, 2.2)), int(rng.integers(1, 4)))
    rim = (mask > 0.35) & (mask < 0.8)
    ys, xs = np.where(rim)
    reach = (1.4, 2.6) if name in SHORT else ((4.0, 8.0) if name == "wild" else (2.2, 4.5))
    for j in rng.integers(0, max(1, len(xs)), len(xs) // (10 if name == "wild" else 22)):
        stroke(xs[j], ys[j], rng.uniform(*reach) * F, de, rng.uniform(140, 235), int(rng.integers(1, 3)))
    grain = np.asarray(Image.fromarray((rng.random((N // 2, N // 2)) * 255).astype(np.uint8)).resize((N * F, N * F), Image.BICUBIC)).astype(np.float32) / 255
    alpha = np.maximum(mask * (0.86 + 0.14 * grain) * 255, np.asarray(edge).astype(np.float32))
    small = lambda a: np.asarray(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((N, N), Image.LANCZOS))
    s = small(np.asarray(shade.filter(ImageFilter.GaussianBlur(0.25 * F))).astype(np.float32))
    return np.dstack([s, s, s, small(alpha)])


def main(out):
    os.makedirs(out, exist_ok=True)
    for i, name in enumerate(SHAPES):
        Image.fromarray(design(name, 20261119 + i)).save(os.path.join(out, name + ".png"))
    with open(os.path.join(out, "index.json"), "w") as f:
        json.dump({"drawn": list(SHAPES), "scale": {n: 1 for n in SHAPES}}, f)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])
