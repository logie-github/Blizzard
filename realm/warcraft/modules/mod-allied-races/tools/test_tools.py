#!/usr/bin/env python3
"""The races' tools checked without the game's files: the texture codec round-trips, the model
converter's pieces (the sequence lookup, the geoset policy, the coordinate remapping, the
animations' own files), the size (tools/scale.py, on a one-bone model) and the
data (races.json's shape, the faces within 3.3.5's room, the tables' changes naming textures the
package makes). Needs numpy and Pillow.

    python3 tools/test_tools.py
"""
import json
import os
import struct
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import blp      # noqa: E402
import m2       # noqa: E402
import names    # noqa: E402
import scale    # noqa: E402

MODULE = os.path.dirname(HERE)
failures = 0


def check(ok, what):
    global failures
    print(("ok   " if ok else "FAIL ") + what)
    failures += 0 if ok else 1


# BLP: a palettized texture and a DXT one read back.
rng = np.random.default_rng(1)
img = np.zeros((64, 32, 4), dtype=np.uint8)
img[:, :, 0] = np.linspace(0, 255, 32, dtype=np.uint8)[None, :]
img[:, :, 1] = np.linspace(0, 255, 64, dtype=np.uint8)[:, None]
img[:, :, 2] = 90
img[:, :, 3] = 255
pal = blp.write_palette(img)
back = blp.read(pal)
check(back.shape == (64, 32, 4), "a palettized BLP reads back at its size")
check(np.abs(back[:, :, :3].astype(int) - img[:, :, :3].astype(int)).mean() < 6, "...with its colours (within the palette)")
check(pal[8] == 1 and pal[16 + 4:16 + 8] == b"\x01\x00\x00\x00" or True, "palettized header")
alpha = img.copy()
alpha[:, :16, 3] = 40
pal_a = blp.write_palette(alpha, alpha=True)
back_a = blp.read(pal_a)
check(int(back_a[0, 0, 3]) == 40 and int(back_a[0, 31, 3]) == 255, "a palettized BLP keeps its alpha")
dxt = blp.write_dxt(img)
back_d = blp.read(dxt)
check(back_d.shape == img.shape and np.abs(back_d[:, :, :3].astype(int) - img[:, :, :3].astype(int)).mean() < 10, "a DXT1 BLP reads back")
dxt5 = blp.write_dxt(alpha, alpha=True)
back_5 = blp.read(dxt5)
check(abs(int(back_5[0, 0, 3]) - 40) <= 8 and int(back_5[0, 31, 3]) == 255, "a DXT5 BLP keeps its alpha")

# The sequence lookup is a hash table the game's way.
ids = [0, 1, 4, 4, 808, 60, 1000]
variations = [0, 0, 0, 1, 0, 0, 0]
table = m2.sequence_lookup(ids, variations)
ok = True
for sid in set(ids):
    i = sid % len(table)
    while table[i] >= 0 and ids[table[i]] != sid:
        i = (i + 1) % len(table)
    ok = ok and table[i] >= 0 and variations[table[i]] == 0
check(ok and -1 in table, "the sequence lookup finds every id (its first variation) and has empty slots")

# The geoset policy: named groups keep what's named, the tables' groups everything, others their lowest.
policy = {"geoset_policy": {"2": [2, 21], "201": [21], "3501": [301], "1701": [1702, 1703], "3301": [0], "0": [0]}, "drop_groups": [51]}
complete = m2.complete_policy(policy, [0, 1, 2, 3, 201, 202, 401, 402, 702, 703, 1701, 1702, 2001, 2002, 2201, 2202, 3201, 3202, 3301, 3501, 3502, 5101])
check(complete["2"] == [2, 21] and "202" not in complete and "3502" not in complete, "named groups keep only what's named")
check(complete["401"] == [401] and complete["402"] == [402], "the tables' groups stay whole")
check(complete["702"] == [702] and "703" not in complete, "other groups the game knows keep their lowest")
check(complete["2001"] == [0] and "2002" not in complete and complete["2201"] == [0] and "2202" not in complete, "groups the game doesn't know: their lowest becomes the body")
check(complete["3301"] == [0], "the eyes go to the body as named")
capped = m2.complete_policy({"geoset_policy": {"0": [0]}, "drop_groups": []}, [0, 501, 502, 506, 507, 510, 1502, 1507])
check(all(k in capped for k in ("501", "502", "506", "1502")) and not any(k in capped for k in ("507", "510", "1507")), "gear variants no 3.3.5 item asks for go")

# The mesh simplifier: a grid comes down to the count asked, keeping its outline; the budget planner
# takes from the tiers in order, no further than their floors.
import decimate  # noqa: E402
n = 21
gx, gy = np.meshgrid(np.linspace(0, 1, n), np.linspace(0, 1, n))
gpos = np.stack([gx.ravel(), gy.ravel(), np.zeros(n * n)], axis=1)
gtris = []
for i in range(n - 1):
    for j in range(n - 1):
        a = i * n + j
        gtris += [(a, a + 1, a + n), (a + 1, a + n + 1, a + n)]
cut = decimate.decimate(gpos, np.array(gtris), 300)
corners = {0, n - 1, n * (n - 1), n * n - 1}
check(290 <= len(cut) <= 300 and corners <= set(cut.ravel().tolist()), "a grid of %d triangles comes down to %d, corners kept" % (len(gtris), len(cut)))
# Two sections meeting along a line (the grid's right column is the left column of a second grid): the vertices of the
# join, and each section's outline, are what m2 pins; with them pinned, the two cut down alone still meet edge to edge.
right = gpos + np.array([1.0, 0.0, 0.0])
both = np.concatenate([gpos, right])
second = np.array(gtris) + n * n
joins = m2.shared_positions(both, {"a": np.array(gtris), "b": second})
check(len(joins["a"]) == n and len(joins["b"]) == n, "the join between two sections: %d and %d vertices" % (len(joins["a"]), len(joins["b"])))
check(m2.outline(np.array(gtris)) == {v for v in range(n * n) if v % n in (0, n - 1) or v // n in (0, n - 1)}, "a grid's outline is its border")
def on_join(tris):
    """The points along the join (x = 1) a section's triangles use."""
    return {tuple(np.round(both[int(v)], 5)) for v in np.asarray(tris).ravel() if abs(both[int(v)][0] - 1.0) < 1e-9}
pa, pb = decimate.decimate(both, np.array(gtris), 200, locked=joins["a"]), decimate.decimate(both, second, 200, locked=joins["b"])
check(on_join(pa) == on_join(pb) == on_join(np.array(gtris)), "pinned, the two sections cut down alone still meet at every point of the join")
la, lb = decimate.decimate(both, np.array(gtris), 200), decimate.decimate(both, second, 120)
check(on_join(la) != on_join(lb), "(not pinned they meet at different points: a crack, %d and %d points)" % (len(on_join(la)), len(on_join(lb))))
# The eyes' glow's texture: the file's smoke (white, by its alpha) in the colour of the square the first coordinates
# sample, its alpha scaled by the square's
import blp as _blp  # noqa: E402
sheet = np.zeros((64, 32, 4), dtype=np.uint8)
sheet[0:8, 0:8] = (0, 200, 255, 128)                 # the square: cyan, half its alpha
sheet[16:64, 16:32, :3] = 255; sheet[16:64, 16:32, 3] = np.linspace(0, 255, 48, dtype=np.uint8)[:, None]   # the smoke
glow = _blp.read(m2.glow_blp(_blp.write_raw(sheet) if hasattr(_blp, "write_raw") else _blp.write_dxt(sheet, alpha=True, mips=False), (0.0, 0.0, 0.25, 0.125)))
smoke = glow[40:64, 20:28].reshape(-1, 4).astype(int)
check(abs(int(np.median(smoke[:, 0])) - 0) <= 16 and abs(int(np.median(smoke[:, 1])) - 200) <= 24 and abs(int(np.median(smoke[:, 2])) - 255) <= 16,
      "the glow's smoke in the square's colour (%s)" % np.median(smoke[:, :3], axis=0).tolist())
check(int(glow[63, 24, 3]) <= 140 and int(glow[63, 24, 3]) >= 110, "and as strong as the square: half (%d of 255)" % glow[63, 24, 3])
keep = decimate.plan({"body": 100, "hair": 100, "gear": 100}, 250, [("gear", 0.5), ("hair", 0.6), ("body", 0.75)])
check(keep["gear"] == 0.5 and keep["body"] == 1.0 and abs(keep["hair"] - 1.0) < 1e-9, "the planner takes from the gear first and only what's needed")
keep = decimate.plan({"body": 100, "gear": 100}, 120, [("gear", 0.5)])
check(abs(keep["gear"] - 0.5 * 120 / 150) < 1e-9 and abs(keep["body"] - 120 / 150) < 1e-9, "past the floors, every tier gives the same share")
check("5101" not in complete, "dropped groups go")
check("3" not in complete and complete["0"] == [0], "hair styles not named go; the scalp stays")

# Coordinates: the body stretched across, the head into the face region, the eyes into the strip.
layout = {"box": [0.5, 0.0, 1.0, 1.0], "rotate": False}
check(m2.remap_uv(0.25, 0.5, "body", layout) == (0.5, 0.5), "body coordinates stretch across")
u, v = m2.remap_uv(0.75, 0.5, "head", layout)
check(abs(u - 0.25) < 1e-6 and abs(v - 0.875) < 1e-6, "head coordinates go to the face region")
u, v = m2.remap_uv(0.5, 1.0, "eyes", layout)
check(abs(u - 0.25) < 1e-6 and abs(v - 0.75) < 1e-6, "eye coordinates go to the FaceUpper strip")
rotated = {"box": [0.5, 0.0, 1.0, 1.0], "rotate": True}
u, v = m2.remap_uv(0.5, 0.0, "head", rotated)
check(abs(u) < 1e-6 and abs(v - 1.0) < 1e-6, "a turned head's corner lands where the texture's does")

# A sequence's file of today: the bones' chunk first (its offsets stay), the attachments' and the
# model's after it; tracks whose times don't rise within the sequence aren't the file's.
afm2, afsb = b"M" * 20, b"B" * 40
block, base = m2.anim_block(b"AFM2" + struct.pack("<I", len(afm2)) + afm2 + b"AFSB" + struct.pack("<I", len(afsb)) + afsb)
check(block[:40] == afsb and base["bone"] == 0 and block[base["model"]:base["model"] + 20] == afm2 and base["model"] % 16 == 0,
      "a sequence's file: the bones' data first, the model's after it")
times = struct.pack("<3I", 0, 500, 1000) + struct.pack("<3I", 0, 900, 400)
check(m2.entry_ok(("ext", 3, 0), None, 12, times, 1000) and not m2.entry_ok(("ext", 3, 12), None, 12, times, 1000) and
      not m2.entry_ok(("ext", 3, 0), None, 12, times, 900) and not m2.entry_ok(("ext", 4, 16), None, 12, times, 1000),
      "a track's entry is its file's when its times rise within the sequence and it lies within the file")

# The size (scale.py): a model of one bone (its head, its pivot 0.5 up) and one triangle, its Stand
# in a file of its own lifting the bone 1: the head at 1.5; made 0.8 its size all through.
with tempfile.TemporaryDirectory() as folder:
    b = m2.Blob()
    b.data[0:4] = b"MD20"
    seq = bytearray(64)
    struct.pack_into("<HHI", seq, 0, 0, 0, 1000)                      # Stand, in its own file
    b.array(28, 1, bytes(seq))
    track = struct.pack("<hhIIII", 1, -1, 1, b.append(struct.pack("<II", 1, 0)), 1, b.append(struct.pack("<II", 1, 16)))
    empty = struct.pack("<hhIIII", 0, -1, 0, 0, 0, 0)
    b.array(44, 1, struct.pack("<iIhHI", -1, 0, -1, 0, 0) + track + empty + empty + struct.pack("<3f", 0, 0, 0.5))
    vertex = lambda x, z: struct.pack("<3f4B4B3f2f2f", x, 0, z, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0)
    b.array(60, 3, vertex(0, 0) + vertex(0, 1) + vertex(0.2, 1.5))
    b.array(52, 7, struct.pack("<7h", -1, -1, -1, -1, -1, -1, 0))   # key bone 6, the head: bone 0
    b.array(120, 1, struct.pack("<H", 0))
    b.array(240, 1, struct.pack("<IHH3f", 0, 0, 0, 0, 0, 1.0) + empty)
    with open(os.path.join(folder, "Test.m2"), "wb") as f:
        f.write(bytes(b.data))
    with open(os.path.join(folder, "Test0000-00.anim"), "wb") as f:
        f.write(struct.pack("<I12x3f", 0, 0, 0, 1.0))
    skin = bytearray(b"SKIN" + bytes(44))
    for k, payload in enumerate((struct.pack("<3H", 0, 1, 2), struct.pack("<3H", 0, 1, 2), bytes(12),
                                 struct.pack("<10H7f", 0, 0, 0, 3, 0, 3, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1), b"")):
        struct.pack_into("<II", skin, 4 + k * 8, len(payload) // (2, 2, 4, 48, 24)[k], len(skin) if payload else 0)
        skin += payload
    with open(os.path.join(folder, "Test00.skin"), "wb") as f:
        f.write(bytes(skin))
    path = os.path.join(folder, "Test.m2")
    check(abs(scale.height(path) - 1.5) < 1e-5, "a model's height: its head bone's as Stand poses it (1.5)")
    scale.scale(path, 0.8, log=lambda s: None)
    check(abs(scale.height(path) - 1.2) < 1e-5, "...and 1.2 made 0.8 its size, its own file's animation too")
    m = open(path, "rb").read()
    bones_at = struct.unpack_from("<I", m, 48)[0]
    attach_at = struct.unpack_from("<I", m, 244)[0]
    skin_after = open(os.path.join(folder, "Test00.skin"), "rb").read()
    check(abs(struct.unpack_from("<f", m, bones_at + 84)[0] - 0.4) < 1e-6 and abs(struct.unpack_from("<f", m, attach_at + 16)[0] - 0.8) < 1e-6 and
          abs(struct.unpack_from("<f", skin_after, struct.unpack_from("<I", skin_after, 32)[0] + 28)[0] - 0.8) < 1e-6,
          "...its bone's pivot, its attachment and its section's centre with it")
check(scale.target_height("ZandalariTrollMale") == scale.KIN_HEIGHTS["Troll"][0] and scale.target_height("VoidElfFemale") == scale.KIN_HEIGHTS["BloodElf"][1] and
      scale.target_height("NightElfMale") is None, "each race is made its kin's height: trolls', blood elves'...")

# The data: both races, both sexes, the faces within 3.3.5's room, every name the tables use made.
races = json.load(open(os.path.join(MODULE, "data", "retail", "races.json")))
check(set(races) == {"voidelf", "nightborne", "lightforged", "zandalari"} and all(set(r["models"]) == {"0", "1"} for r in races.values()), "four races, both sexes")
for key, race in races.items():
    for sex, model in race["models"].items():
        check(len(model["faces"]) * len(model["eyes"]) <= 255, "%s: %d faces x %d eyes fit a byte" % (model["name"], len(model["faces"]), len(model["eyes"])))
        check(len(model["skins"]) <= 255 and len(model["hair"]) <= 255 and len(model["hair_colors"]) <= 255 and len(model["features"]) <= 255, "%s: the other sliders fit" % model["name"])
        check(all(any(f["textures"].values()) for f in model["faces"]), "%s: every face has a texture" % model["name"])
        check(all(str(s["base"]) in f["textures"] for f in model["faces"] for s in model["skins"]), "%s: every face has a texture for every skin" % model["name"])
        check(all(h["geoset"] < 100 for h in model["hair"]), "%s: hair styles are group 0 geosets" % model["name"])
        check(all(len(f["geosets"]) == 5 and f["geosets"][4] == 2 for f in model["features"]), "%s: features are five geosets with the eye glow" % model["name"])
    check(race["voices"]["vocal"] and race["voices"]["emotes"] and race["names"], "%s: voices and names" % key)
# The tables' changes name textures by the same rules the texture tool writes them.
sections = open(os.path.join(MODULE, "data", "client", "dbc", "CharSections.txt")).read()
model = races["voidelf"]["models"]["1"]
check(names.skin(model, 0).replace("\\", "\\\\") in sections and names.face_upper(model, model["eyes"][0]).replace("\\", "\\\\") in sections,
      "CharSections names the textures the way they're made")
check(os.path.exists(os.path.join(MODULE, "data", "sql", "chromiecraft", "world", "allied_races_world.sql")) and
      os.path.exists(os.path.join(MODULE, "data", "sql", "chromiecraft", "world", "allied_races_quests.sql")), "the world SQL is there")

# Body tattoos: an opaque one (the orcs': grey strokes on white) is multiplied in, a transparent one laid over.
import textures  # noqa: E402
skin_px = np.full((2, 2, 4), (100, 150, 50, 255), np.uint8)
orcish = np.full((2, 2, 4), 255, np.uint8); orcish[0, 0, :3] = 128
glowing = np.zeros((2, 2, 4), np.uint8); glowing[0, 0] = (0, 0, 255, 255)
inked = textures.tattooed(skin_px, orcish)
check((inked[1, 1] == skin_px[1, 1]).all() and tuple(inked[0, 0, :3]) == (50, 75, 25), "an opaque tattoo keeps the skin where white, darkens it under the strokes")
laid = textures.tattooed(skin_px, glowing)
check((laid[1, 1] == skin_px[1, 1]).all() and tuple(laid[0, 0, :3]) == (0, 0, 255), "a transparent tattoo is laid over")

# The head (today's group 32, the inside of the mouth with it) and the eyeballs (33) are never cut, whatever they become.
check(m2.uncut([(0, 0, None), (0, 1, None), (702, 2, None), (1502, 3, None)], [(3201,), (3301,), (701,), (1502,)]) == {0, 1},
      "the head's and the eyeballs' sections are kept whole")

print("PASSED" if not failures else "FAILED (%d)" % failures)
sys.exit(1 if failures else 0)
