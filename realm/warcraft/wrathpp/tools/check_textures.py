#!/usr/bin/env python3
"""The character textures the looks package puts in CharSections, checked the way 3.3.5's component code reads them
(WoW/Common/ComponentCore/CharacterComponent.cpp: Paste, PasteOpaque, PasteTransparent*): it pastes only PALETTIZED
textures (BLP2 colour encoding 1; any other draws as flat green) of the section kinds 0 (skin), 1 (face lower and upper), 2
(facial hair), 4 (underwear), and for each source mip level from the one it starts at to the source's last it writes a mip
of the component's own texture: a source with more mips than the component's chain, or with sizes that aren't powers of two,
writes past it (a heap corruption that shows at the next allocation: issue 294). So each such texture that the package has:
palettized, power-of-two sides of at most 512, a whole mip chain (mips down to 1 x 1), its section's sides
(skin 256 or 512 square, face lower 256 x 128, face upper 256 x 64, facial hair 128 x 64 or 256 x 128, underwear 256 x 128;
the game's own HD textures use these), and no mip sizes that don't halve.

    python3 tools/check_textures.py LOOKS_DIR          (the package folder: changes/CharSections.txt, client/...)

Prints each problem and a count; exit status 1 when there is any problem.
"""
import os
import struct
import sys

SECTIONS = {0: "skin", 1: "face", 2: "facial hair", 4: "underwear"}
SIDES = {0: {(256, 256), (512, 512)}, 1: {(256, 128), (256, 64), (128, 64), (128, 32), (64, 32), (256, 256)},
         2: {(128, 64), (256, 128), (64, 32)}, 4: {(256, 128), (128, 64)}}


def header(path):
    with open(path, "rb") as f:
        d = f.read(1172)
    if len(d) < 148 or d[:4] != b"BLP2":
        return None
    kind, enc, alpha, aenc, mips, w, h = struct.unpack_from("<IBBBBII", d, 4)
    offsets = struct.unpack_from("<16I", d, 20)
    sizes = struct.unpack_from("<16I", d, 84)
    return {"kind": kind, "enc": enc, "alpha": alpha, "hasmips": mips, "w": w, "h": h,
            "levels": [(o, s) for o, s in zip(offsets, sizes) if o and s]}


def textures(changes_text):
    types, out = "", []
    for line in changes_text.split("\n"):
        f = line.rstrip("\r").split("\t")
        if f[0] == "types":
            types = f[1]
        elif f[0] == "put" and len(f) == len(types) + 1 and len(types) == 10:
            v = f[1:]
            section = int(v[3])
            for i in (4, 5, 6):
                if v[i]:
                    out.append((int(v[1]), int(v[2]), section, v[i].replace("\\\\", "\\")))
    return out


def find(client, rel):
    cur = client
    for part in rel.replace("\\", "/").split("/"):
        names = {n.lower(): n for n in os.listdir(cur)} if os.path.isdir(cur) else {}
        if part.lower() not in names:
            return None
        cur = os.path.join(cur, names[part.lower()])
    return cur if os.path.isfile(cur) else None


def main(folder):
    with open(os.path.join(folder, "changes", "CharSections.txt"), encoding="utf-8") as f:
        rows = textures(f.read())
    client = os.path.join(folder, "client")
    problems, seen, missing = [], set(), 0
    for race, sex, section, name in rows:
        if section not in SECTIONS or name in seen:
            continue
        seen.add(name)
        path = find(client, name)
        if not path:
            missing += 1                                    # (the game's own, not in the package)
            continue
        h = header(path)
        what = "%s (race %d, %s)" % (name, race, SECTIONS[section])
        if not h:
            problems.append("%s: not a BLP2" % what); continue
        if h["enc"] != 1:
            problems.append("%s: not palettized (encoding %d): the component code draws it as flat green" % (what, h["enc"])); continue
        w, ht = h["w"], h["h"]
        if w & (w - 1) or ht & (ht - 1) or max(w, ht) > 512:
            problems.append("%s: sides %d x %d (powers of two, at most 512)" % (what, w, ht))
        if (w, ht) not in SIDES[section]:
            problems.append("%s: %d x %d isn't a size the game's %s textures have" % (what, w, ht, SECTIONS[section]))
        want = max(w, ht).bit_length()
        if len(h["levels"]) != want:
            problems.append("%s: %d mip levels, a %d x %d texture has %d" % (what, len(h["levels"]), w, ht, want))
        for i, (o, s) in enumerate(h["levels"]):
            mw, mh = max(1, w >> i), max(1, ht >> i)
            if s != mw * mh + (mw * mh * max(h["alpha"], 0) + 7) // 8:
                problems.append("%s: mip %d is %d bytes, %d x %d needs %d" % (what, i, s, mw, mh, mw * mh + (mw * mh * h["alpha"] + 7) // 8))
                break
    for p in problems:
        print("PROBLEM", p)
    print("%d character textures checked (%d of the game's own not in the package), %d problems" % (len(seen) - missing, missing, len(problems)))
    return 1 if problems else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1]))
