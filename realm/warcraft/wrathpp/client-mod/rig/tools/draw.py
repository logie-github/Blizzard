#!/usr/bin/env python3
"""The rig's screen as a picture: draw.py SHOT.json OUT.png. The game's own pieces grey (red where they take taps), the
creator's gold; text where it is. Not the game's art: the places and sizes of things."""
import json, sys
from PIL import Image, ImageDraw, ImageFont
shot = json.load(open(sys.argv[1]))
W, H = int(shot["w"]), int(shot["h"])
S = 1
im = Image.new("RGB", (W * S, H * S), (30, 34, 46)); d = ImageDraw.Draw(im)
try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
except Exception: font = ImageFont.load_default()
def box(f): return (f["l"], H - f["b"] - f["h"], f["l"] + f["w"], H - f["b"])
frames = shot["frames"]
for f in frames:
    mine = f["name"].startswith("Wrathpp") or f["parent"].startswith("Wrathpp")
    x0, y0, x1, y1 = box(f)
    if f["kind"] == "Texture":
        if f["w"] >= W - 2 and f["h"] >= H - 2: continue
        d.rectangle((x0, y0, x1, y1), outline=(70, 74, 60) if not mine else (110, 100, 60))
    elif f["kind"] == "FontString": pass
    else:
        tappable = f["kind"] in ("Button", "CheckButton", "EditBox", "Slider")
        colour = (230, 190, 70) if mine else ((220, 80, 80) if tappable else (120, 130, 150))
        d.rectangle((x0, y0, x1, y1), outline=colour, width=2 if tappable else 1)
for f in frames:
    x0, y0, x1, y1 = box(f)
    if f["kind"] == "FontString" and f["text"]:
        d.text((x0, y0), f["text"][:40], fill=(240, 225, 160), font=font)
    elif f["kind"] in ("Button", "CheckButton", "EditBox") and f["name"]:
        label = f["text"] or f["name"].replace("Wrathpp", "").replace("CharacterCreate", "").replace("CharCreate", "")
        d.text((x0 + 2, y0 + 1), label[:18], fill=(170, 180, 200), font=font)
im.save(sys.argv[2]); print("drawn", sys.argv[2], W, "x", H)
