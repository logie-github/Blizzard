#!/usr/bin/env python3
"""Makes the app's pictures and icons from the user's art in branding/ (run from the repository root)."""
from pathlib import Path
from PIL import Image, ImageDraw

B = Path("branding")
RES = Path("app/src/main/res")
NODPI = RES / "drawable-nodpi"
NODPI.mkdir(parents=True, exist_ok=True)

# Box art: 600x900 (2:3), the shelf's shape.
for f in sorted((B / "covers").iterdir()):
    im = Image.open(f).convert("RGB")
    w, h = im.size
    if abs(w / h - 2 / 3) > 0.01:  # crop to 2:3, keeping the top (the art) and the bottom (the logo) centred
        if w / h > 2 / 3:
            nw = round(h * 2 / 3); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
        else:
            nh = round(w * 3 / 2); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    im = im.resize((600, 900), Image.LANCZOS)
    im.save(NODPI / f"cover_{f.stem}.webp", quality=90)

# The header: the ice field.
im = Image.open(B / "header.png").convert("RGB")
im.save(NODPI / "blizz_header.webp", quality=88)

# The logo: the word in its blue, ENTERTAINMENT (black in the file) in the same blue for the dark screen.
logo = Image.open(B / "logo.png").convert("RGBA")
px = logo.load()
for y in range(logo.height):
    for x in range(logo.width):
        r, g, b, a = px[x, y]
        if a > 0 and r < 90 and g < 90 and b < 90:
            px[x, y] = (0x00, 0xB4, 0xFF, a)
logo.thumbnail((1200, 1200), Image.LANCZOS)
logo.save(NODPI / "blizz_logo.webp", quality=92)

# The icon. Legacy squares, and an adaptive icon: the emblem (everything inside the white star)
# over the streaked blue.
icon = Image.open(B / "icon.png").convert("RGB")
for name, size in {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}.items():
    d = RES / f"mipmap-{name}"; d.mkdir(exist_ok=True)
    icon.resize((size, size), Image.LANCZOS).save(d / "ic_launcher.png")

S = icon.width
white = Image.new("L", icon.size, 0)
wp, ip = white.load(), icon.load()
for y in range(S):
    for x in range(S):
        r, g, b = ip[x, y]
        wp[x, y] = 255 if min(r, g, b) > 200 else 0
outside = white.copy()
for seed in [(0, 0), (S - 1, 0), (0, S - 1), (S - 1, S - 1)]:
    ImageDraw.floodfill(outside, seed, 128)
mask = outside.point(lambda v: 0 if v == 128 else 255)
box = mask.getbbox()
emblem = icon.convert("RGBA"); emblem.putalpha(mask); emblem = emblem.crop(box)
# The foreground is 108dp; its safe circle is 66dp across, and the star's points may reach a little past it.
fg = Image.new("RGBA", (432, 432), (0, 0, 0, 0))
side = 300
e = emblem.resize((side, round(side * emblem.height / emblem.width)), Image.LANCZOS)
fg.paste(e, ((432 - e.width) // 2, (432 - e.height) // 2), e)
fg.save(NODPI / "ic_launcher_foreground.png")
bg = icon.resize((432, 432), Image.LANCZOS)
bg.save(NODPI / "ic_launcher_background.png")
