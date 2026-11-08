#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""The naga's headdresses and outfits: Blizzard's own, made for the naga's body (Battle for Azeroth's
Nazjatar naga wear them: the files end _na_m and _na_f), as parts the world server adds to the
client's naga model as it makes the game's patch (src/MurlocNagaPatch.cpp, MergeParts).

    python3 tools/naga_parts.py fetch DIR          fetches the game's files from wago.tools by their ids
                                                    and writes the parts and their textures into DIR
    python3 tools/naga_parts.py convert SRC DIR    the same from files already fetched (named by id)

The files are the game's, so they are never in this repository: the server package makes them
(scripts/package-azerothcore.sh) into the module's data/files, with the murlocs'. Their list,
naga.files, is written last.

The character creation screen's choices (tools/build_data.py writes the tables):
  - Headdress (the hair style, ChrRaces' token NAGA): none, and for men the myrmidon's crown and the
    warlord's helm, for women the sea witch's headdress (helm_*_na_m/_na_f: placed at the naga's
    head, its attachment 11, which the 3.3.5 naga hasn't, on the head's bone);
  - Headdress color (the hair colour): the headdress's colours (its item displays' textures), drawn
    with the character's hair texture (type 6);
  - Features: none, and each outfit in each of its colours (collections_*_na_m/_na_f: skinned to the
    naga's bones, which the 3.3.5 naga has at the same places).

Character/Naga_/<Sex>/Naga<Sex>Parts.dat: the parts' geometries, each drawn by one or more uses (a
geoset and a texture: an outfit's colours share its triangles, as the game's 16-bit section starts
leave room for no more):
  "NPRT", version 2, geometry count (u32); a geometry: blend (u16), vertices (u32), triangles (u32),
  uses (u16), each: geoset (u16), texture type (u16: 6 the hair's, 0 its own), texture name (u16
  length, bytes); vertices of 84 bytes: position (3f), normal (3f), coordinates (2f), four bones'
  places (12f: the client's naga's bones are found by them), four weights (4 bytes, 255 in all);
  triangles (3 x u16).
"""
import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import murloc_model as M  # noqa: E402
from naga_looks import HEADDRESSES, OUTFITS, colours, features  # noqa: E402,F401

MANIFEST = "naga.files"
NAGA = {"Male": 120294, "Female": 120263}          # character/naga_/<sex>/naga_<sex>.m2 (their skeletons)
HEAD_ATTACHMENT = 11
def attachment(src, ident):
    m = src.m
    count, at = struct.unpack_from("<II", m, 0xF0)
    for i in range(count):
        if struct.unpack_from("<I", m, at + 40 * i)[0] == ident:
            bone = struct.unpack_from("<H", m, at + 40 * i + 4)[0]
            return bone, np.array(struct.unpack_from("<3f", m, at + 40 * i + 8))
    raise ValueError("no attachment %d" % ident)


def part_bytes(src, uses, rigid_on=None):
    """[src]'s first skin's batches, each a geometry (its own blend) drawn by every one of [uses]
    ((geoset, texture type, texture name): a colour of it, its own geoset). [rigid_on]: (bone place,
    offset) for an item held at an attachment (all its vertices on that bone, moved by the offset)."""
    out = []
    for i in range(len(src.batches)):
        triangles, batch = src.batch_triangles(i)
        blend = struct.unpack_from("<H", src.materials[batch[6]], 2)[0] if batch[6] < len(src.materials) else 0
        used = np.unique(triangles)
        at = {int(v): k for k, v in enumerate(used)}
        part = bytearray(struct.pack("<HIIH", blend, len(used), len(triangles), len(uses)))
        for geoset, texture_type, texture_name in uses:
            name = texture_name.encode()
            part += struct.pack("<HHH", geoset, texture_type, len(name)) + name
        for v in used:
            raw = src.raw[v]
            pos = raw[0:12].copy().view("<f4")
            normal = raw[20:32].copy().view("<f4")
            uv = raw[32:40].copy().view("<f4")
            weights = [int(w) for w in raw[12:16]]
            if rigid_on is not None:
                place, offset = rigid_on
                pos = pos + offset
                places = [place] * 4
                weights = [255, 0, 0, 0]
            else:
                places = [src.pivot[src.bones[v, j]] if weights[j] else src.pivot[src.bones[v, 0]] for j in range(4)]
            part += struct.pack("<3f3f2f", *pos, *normal, *uv)
            for place in places:
                part += struct.pack("<3f", *place)
            part += bytes(weights)
        for t in triangles:
            part += struct.pack("<3H", *(at[int(v)] for v in t))
        out.append(bytes(part))
    return out


def convert(read, folder):
    files = {}
    for sex, naga_id in NAGA.items():
        naga = M.Source(read, naga_id)
        bone, offset = attachment(naga, HEAD_ATTACHMENT)
        head_place = naga.pivot[bone]
        parts = []
        for style, (model, textures, _) in enumerate(HEADDRESSES[sex], start=1):
            src = M.Source(read, model)
            # (an item held at an attachment: its own vertices about the attachment's place)
            parts += part_bytes(src, [(style + 1, 6, "")], rigid_on=(head_place, offset))
        feature = 1
        for outfit, (model, textures, name) in enumerate(OUTFITS[sex]):
            src = M.Source(read, model)
            uses = []
            for colour in range(len(textures)):
                feature += 1
                uses.append((100 + feature, 0, "Character\\Naga_\\%s\\Naga%s%s%d.blp" % (sex, sex, name, colour)))
                files["Character/Naga_/%s/Naga%s%s%d.blp" % (sex, sex, name, colour)] = read(textures[colour])
            parts += part_bytes(src, uses)
        files["Character/Naga_/%s/Naga%sParts.dat" % (sex, sex)] = b"NPRT" + struct.pack("<II", 2, len(parts)) + b"".join(parts)
        # the headdresses' colours: the hair texture of each style and colour (a style with fewer
        # colours repeats its first)
        for style, (_, textures, name) in enumerate(HEADDRESSES[sex], start=1):
            for c in range(colours(sex)):
                files["Character/Naga_/%s/Naga%s%s%d.blp" % (sex, sex, name, c)] = read(textures[c] if c < len(textures) else textures[0])
    for name, data in files.items():
        if name.endswith(".blp") and data[:4] != b"BLP2":
            raise ValueError("%s isn't a BLP2 texture" % name)
        path = os.path.join(folder, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as out:
            out.write(data)
    with open(os.path.join(folder, MANIFEST), "w") as out:
        out.write("".join(name + "\n" for name in sorted(files)))
    print("naga: %d files in %s" % (len(files), folder))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "fetch":
        convert(M.cached(os.environ.get("MURLOC_CACHE"), M.wago), sys.argv[2])
    elif len(sys.argv) == 4 and sys.argv[1] == "convert":
        convert(M.cached(sys.argv[2], None), sys.argv[3])
    else:
        print(__doc__)
        sys.exit(2)
