"""The body layer's designs (layer.py): one texture a style and density, made from the design maps (the user's own:
a shade and a coverage per pixel, at the source designs' frame; never in the repository), for the layer's square of a
race of scale 1 with its fold at 0 (the layer's texture coordinates are in the race's scale, so one texture serves
every race).

  texture(maps_dir, index, name, density) -> RGBA (SIZE x SIZE)

The game multiplies the character's hair texture by it (Combiners_Mod_Mod): its grey is how dark the hair is drawn
there (G0 at a strand's darkest, G0 + G1 x LIGHT_SHARE at its lightest: the hair colour's own dark and light, as
measured on the ten races' hair textures: dark 0.68 x the texture's mean, light 1.37 x), its alpha the coverage times
the density. Designs framing the cleft (LOW) sit 2 cm lower."""
import json
import os

import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates

import layer

SIZE = 256
WIDTH = 0.13                 # the full design's width on a race of scale 1, metres
ANCHOR, ANCHOR_LOW = 0.024, 0.004
LOW = {"full_natural", "wild"}
G0, G1, LIGHT_SHARE = 0.68, 0.69, 0.5
REFERENCE = (97.0, 125.0)    # the source frame's point that sits at the anchor, in its pixels
# the styles' order: the source's five, then the drawn ones; the last is the faction's own
STYLES = ["full_natural", "natural", "small_triangle", "heart", "strip", "wild", "moon", "star", "diamond", "flame",
          "bolt", "swords", "skull", "heart_large", "triangle_large"]
FACTION = {"alliance": "alliance", "horde": "horde"}
DENSITIES = (0.25, 0.5, 0.75, 1.0)


def load(maps_dir, name):
    a = np.asarray(Image.open(os.path.join(maps_dir, name + ".png")).convert("RGBA")).astype(np.float32)
    return a[..., 0] / 255.0, a[..., 3]


def reference_width(maps_dir, index):
    _, al = load(maps_dir, "full_natural")
    xs = np.where((al > 40).any(0))[0]
    return float(xs.max() - xs.min()) / index["scale"]["full_natural"]


def texture(maps_dir, index, name, density):
    shade, cover = load(maps_dir, name)
    sc = index["scale"][name]
    mm = WIDTH / reference_width(maps_dir, index) / sc          # metres per map pixel
    span, top = layer.SPAN, layer.TOP
    j, i = np.mgrid[0:SIZE, 0:SIZE].astype(np.float32) + 0.5
    y = i / SIZE * span - span / 2
    z = top - j / SIZE * span
    anchor = ANCHOR_LOW if name in LOW else ANCHOR
    dx = REFERENCE[0] * sc - y / mm                              # the design's left is her right, seen from the front
    dy = REFERENCE[1] * sc - (z - anchor) / mm
    A = map_coordinates(cover, [dy, dx], order=1, mode="constant") / 255.0 * density
    S = map_coordinates(shade, [dy, dx], order=1, mode="constant")
    g = np.clip(G0 + G1 * S * LIGHT_SHARE, 0, 1) * 255
    out = np.dstack([g, g, g, A * 255]).clip(0, 255).astype(np.uint8)
    out[0, :, 3] = out[-1, :, 3] = out[:, 0, 3] = out[:, -1, 3] = 0   # clamped: nothing past the square
    return out


def styles(faction):
    return STYLES + [FACTION[faction]]


def index_of(maps_dir):
    return json.load(open(os.path.join(maps_dir, "index.json")))
