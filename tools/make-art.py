#!/usr/bin/env python3
"""Makes the app's pictures and icons from the user's art in branding/ (run from the repository root)."""
from pathlib import Path
from PIL import Image, ImageDraw

B = Path("branding")
RES = Path("app/src/main/res")
NODPI = RES / "drawable-nodpi"
NODPI.mkdir(parents=True, exist_ok=True)

# Box art: 600x800 (3:4), cut from the 2:3 art. How much of the cut comes off the top: the rest
# comes off the bottom, so each game's logo stays whole.
TOP_SHARE = {"diablo": 0.5, "diablo2": 0.5, "warcraft3_tft": 0.6}
for f in sorted((B / "covers").iterdir()):
    im = Image.open(f).convert("RGB").resize((600, 900), Image.LANCZOS)
    cut = 100
    top = round(cut * TOP_SHARE.get(f.stem, 1.0))
    im = im.crop((0, top, 600, top + 800))
    im.save(NODPI / f"cover_{f.stem}.webp", quality=90)

# Wide art for the tile layout (branding/wide/<game>.*), 2:1 or wider, kept whole (1200 wide at most).
if (B / "wide").is_dir():
    for f in sorted((B / "wide").iterdir()):
        im = Image.open(f).convert("RGB")
        im.thumbnail((1200, 1200), Image.LANCZOS)
        im.save(NODPI / f"wide_{f.stem}.webp", quality=90)

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

# The icon: the compass with its B, on blue. Adaptive: the compass (its star, frame and B, cut out
# of branding/icon.png) over a blue of its own; legacy squares and the themed (one-colour) icon
# are made from the same two.
import random
from PIL import ImageFilter, ImageChops

icon = Image.open(B / "icon.png").convert("RGB")
S = icon.width
white = Image.new("L", icon.size, 0)
wp, ip = white.load(), icon.load()
for y in range(S):
    for x in range(S):
        wp[x, y] = 255 if min(ip[x, y]) > 200 else 0
outside = white.copy()
for seed in [(0, 0), (S - 1, 0), (0, S - 1), (S - 1, S - 1)]:
    ImageDraw.floodfill(outside, seed, 128)
mask = outside.point(lambda v: 0 if v == 128 else 255)
emblem = icon.convert("RGBA"); emblem.putalpha(mask); emblem = emblem.crop(mask.getbbox())
# The B and the star are the white parts of the emblem: the themed icon's shape.
shape = white.crop(mask.getbbox())

def blue(size):
    """Blizzard blue: bright at the lower right, deep at the upper left, with the soft diagonal streaks of the art."""
    n = 256
    grad = Image.new("RGB", (n, n))
    gp = grad.load()
    top, bottom = (8, 70, 160), (36, 150, 245)
    for y in range(n):
        for x in range(n):
            t = (x + y) / (2 * n - 2)
            gp[x, y] = tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    streaks = Image.new("L", (n, n), 0)
    d = ImageDraw.Draw(streaks)
    rnd = random.Random(5)
    for _ in range(26):
        x0, y0 = rnd.randint(-40, n), rnd.randint(0, n)
        length = rnd.randint(40, 120)
        d.line([(x0, y0), (x0 + length, y0 - length // 3)], fill=rnd.randint(30, 90), width=rnd.randint(1, 3))
    streaks = streaks.filter(ImageFilter.GaussianBlur(2.2))
    light = Image.new("RGB", (n, n), (150, 215, 255))
    out = Image.composite(light, grad, streaks)
    return out.resize((size, size), Image.LANCZOS)

# Legacy squares: the compass over the blue, the star's tips cut off by nothing (the square holds them).
square = blue(432)
side = 372
e = emblem.resize((side, round(side * emblem.height / emblem.width)), Image.LANCZOS)
square.paste(e, ((432 - e.width) // 2, (432 - e.height) // 2), e)
for name, size in {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}.items():
    d = RES / f"mipmap-{name}"; d.mkdir(exist_ok=True)
    square.resize((size, size), Image.LANCZOS).save(d / "ic_blizz.png")

# Adaptive: 108dp layers, of which a circle of 66dp always shows. The compass fills that circle.
fg = Image.new("RGBA", (432, 432), (0, 0, 0, 0))
side = 228
e = emblem.resize((side, round(side * emblem.height / emblem.width)), Image.LANCZOS)
fg.paste(e, ((432 - e.width) // 2, (432 - e.height) // 2), e)
fg.save(NODPI / "ic_blizz_foreground.png")
blue(432).save(NODPI / "ic_blizz_background.png")
mono = Image.new("RGBA", (432, 432), (0, 0, 0, 0))
m = shape.resize((side, round(side * shape.height / shape.width)), Image.LANCZOS)
mono.paste(Image.new("RGBA", m.size, (255, 255, 255, 255)), ((432 - m.width) // 2, (432 - m.height) // 2), m)
mono.save(NODPI / "ic_blizz_monochrome.png")

# Games' own loading screens (branding/splash/<game>.png, and <game>-logo.png over it).
for f in sorted(p for p in (B / "splash").iterdir() if p.suffix in (".png", ".jpg")):
    im = Image.open(f)
    if f.stem.endswith("-logo"):
        im.convert("RGBA").save(NODPI / f"splash_logo_{f.stem[:-5]}.webp", quality=92)
    else:
        im = im.convert("RGB")
        im.thumbnail((1920, 1920), Image.LANCZOS)
        im.save(NODPI / f"splash_{f.stem}.webp", quality=86)
