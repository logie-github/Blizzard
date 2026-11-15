#!/usr/bin/env python3
"""The rig's screen painted with Shadowlands' own art: paint.py SHOT.json ART_DIR OUT.png [SCALE]
ART_DIR: the art package's client folder (Interface\\Wrathpp\\Creator\\*.blp are read from it). What the creator draws
is drawn as the game would: each piece's part of its file, stretched to its place, tinted, in its layer and strata. A
picture of 3.3.5's own (not on this machine) is a faint box; text is in a stand-in font at its size. Not the game:
no 3D scene, no font of the game's; what it shows is what is where, how large, and over what."""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "modules", "mod-allied-races", "tools")))
import blp
shot = json.load(open(sys.argv[1])); art = sys.argv[2]; out = sys.argv[3]
K = float(sys.argv[4]) if len(sys.argv) > 4 else 1.625          # the phone: 1828 x 1248 pixels for 1125 x 768 units
W, H = shot["w"], shot["h"]
im = Image.new("RGBA", (int(W * K), int(H * K)), (46, 52, 66, 255))
# where the game's scene would be: a figure's outline, so that what is over it is seen to be
d0 = ImageDraw.Draw(im)
cx = W * K / 2
d0.ellipse((cx - 40 * K, 150 * K, cx + 40 * K, 230 * K), fill=(70, 78, 96, 255))
d0.rounded_rectangle((cx - 75 * K, 235 * K, cx + 75 * K, 640 * K), radius=40 * K, fill=(70, 78, 96, 255))
cache = {}
def load(name):
    key = name.lower().replace("/", "\\")
    if key not in cache:
        path = os.path.join(art, *key.split("\\")) + ".blp"
        found = None
        folder = os.path.dirname(path)
        if os.path.isdir(folder):
            for f in os.listdir(folder):
                if f.lower() == os.path.basename(path).lower():
                    found = os.path.join(folder, f)
        else:
            # the art's folders as the tool wrote them (their own letters)
            parts = key.split("\\")
            cur = art
            for part in parts[:-1]:
                nxt = [f for f in os.listdir(cur) if f.lower() == part] if os.path.isdir(cur) else []
                if not nxt: cur = None; break
                cur = os.path.join(cur, nxt[0])
            if cur:
                for f in os.listdir(cur):
                    if f.lower() == parts[-1] + ".blp": found = os.path.join(cur, f)
        cache[key] = Image.fromarray(blp.read(open(found, "rb").read()), "RGBA") if found else None
    return cache[key]
STRATA = {"BACKGROUND": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "DIALOG": 4, "FULLSCREEN": 5, "FULLSCREEN_DIALOG": 6, "TOOLTIP": 7}
LAYER = {"BACKGROUND": 0, "BORDER": 1, "ARTWORK": 2, "OVERLAY": 3, "HIGHLIGHT": 9, "": 2}
def font(size):
    try: return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", max(6, int(round(size))))
    except Exception: return ImageFont.load_default()
frames = shot["frames"]
order = sorted(range(len(frames)), key=lambda i: (STRATA.get(frames[i]["strata"], 2), i))
# a frame's regions are drawn in their layers over the frame; frames in the order they were made within a strata
def box(f): return (f["l"] * K, (H - f["b"] - f["h"]) * K, (f["l"] + f["w"]) * K, (H - f["b"]) * K)
missing = set()
for layer_pass in (0, 1, 2, 3):
    pass
drawn = 0
by_strata = {}
for i in order: by_strata.setdefault(STRATA.get(frames[i]["strata"], 2), []).append(i)
for strata in sorted(by_strata):
    idx = by_strata[strata]
    # textures and texts by layer within the strata (a simplification: the game orders by frame level first)
    for lay in (0, 1, 2, 3):
        for i in idx:
            f = frames[i]
            if f["kind"] not in ("Texture", "FontString") or LAYER.get(f["layer"], 2) != lay: continue
            x0, y0, x1, y1 = box(f)
            if f["kind"] == "Texture":
                # (whole pixels by the edges, so that two pieces that meet share their edge)
                x0, y0, x1, y1 = round(x0), round(y0), round(x1), round(y1)
            w, h = int(round(x1 - x0)), int(round(y1 - y0))
            if f["kind"] == "Texture":
                if w < 1 or h < 1 or f["alpha"] <= 0: continue
                if f["colour"]:
                    c = f["colour"]; v = f["vertex"] or [1, 1, 1, 1]
                    a = c[3] * f["alpha"]
                    if a <= 0: continue
                    tile = Image.new("RGBA", (w, h), (int(c[0] * 255), int(c[1] * 255), int(c[2] * 255), int(a * 255)))
                elif f["file"]:
                    src = load(f["file"])
                    if src is None:
                        if f["mine"] and f["file"] not in missing: missing.add(f["file"])
                        if f["mine"]:
                            tile = Image.new("RGBA", (w, h), (0, 0, 0, 0)); ImageDraw.Draw(tile).rectangle((0, 0, w - 1, h - 1), outline=(120, 200, 120, 200), fill=(60, 110, 60, 70))
                        else: continue
                    else:
                        c = f["coords"] or [0, 1, 0, 1]
                        if len(c) == 8: c = [c[0], c[4], c[1], c[3]]
                        l, r, t, b = c
                        sw, sh = src.size
                        crop = src.transform((w, h), Image.Transform.EXTENT, (l * sw, t * sh, r * sw, b * sh), Image.Resampling.BILINEAR)
                        arr = np.asarray(crop).astype(np.float32)
                        v = f["vertex"] or [1, 1, 1, 1]
                        if f["grey"]:
                            g = arr[:, :, :3].mean(axis=2, keepdims=True); arr[:, :, :3] = g
                        arr[:, :, 0] *= v[0]; arr[:, :, 1] *= v[1]; arr[:, :, 2] *= v[2]
                        arr[:, :, 3] *= f["alpha"] * (v[3] if len(v) > 3 else 1)
                        tile = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
                else: continue
                layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
                layer.paste(tile, (int(round(x0)), int(round(y0))))
                if f.get("clip"):
                    cl, cb, cw, ch = f["clip"]
                    keep = Image.new("L", im.size, 0)
                    ImageDraw.Draw(keep).rectangle((cl * K, (H - cb - ch) * K, (cl + cw) * K, (H - cb) * K), fill=255)
                    layer.putalpha(Image.composite(layer.getchannel("A"), Image.new("L", im.size, 0), keep))
                if f["blend"] == "ADD":
                    a = np.asarray(layer).astype(np.float32); base = np.asarray(im).astype(np.float32)
                    base[:, :, :3] = np.clip(base[:, :, :3] + a[:, :, :3] * (a[:, :, 3:4] / 255.0), 0, 255)
                    im = Image.fromarray(base.astype(np.uint8), "RGBA")
                else:
                    im = Image.alpha_composite(im, layer)
                drawn += 1
            elif f["text"]:
                size = (f["font"] or 12) * K
                fnt = font(size)
                c = f["colour"] or [1, 1, 1, 1]
                if f.get("clip"):
                    cl, cb, cw, ch = f["clip"]
                    if y1 < (H - cb - ch) * K or y0 > (H - cb) * K: continue
                d = ImageDraw.Draw(im)
                # on as many lines as its width takes, where it was given a width and a height for more than one
                lines = [f["text"]]
                if (x1 - x0) > 4 and d.textlength(f["text"], font=fnt) > (x1 - x0) and (y1 - y0) > size * 2 and " " in f["text"]:
                    lines, cur = [], ""
                    for word in f["text"].split(" "):
                        if cur and d.textlength(cur + " " + word, font=fnt) > (x1 - x0): lines.append(cur); cur = word
                        else: cur = (cur + " " + word).strip()
                    lines.append(cur)
                a = int(255 * f["alpha"])
                for n, line in enumerate(lines):
                    tw = d.textlength(line, font=fnt)
                    x = x0
                    if f["justify"] == "RIGHT": x = x1 - tw
                    elif f["justify"] in ("CENTER", ""): x = (x0 + x1) / 2 - tw / 2
                    y = (y0 + y1) / 2 - size * 0.6 + (n - (len(lines) - 1) / 2.0) * size * 1.15
                    d.text((x + K, y + K), line, fill=(0, 0, 0, a), font=fnt)
                    d.text((x, y), line, fill=(int(c[0] * 255), int(c[1] * 255), int(c[2] * 255), a), font=fnt)
im.convert("RGB").save(out)
print("painted", out, im.size, drawn, "pieces;", len(missing), "of 3.3.5's own pictures shown as boxes")
