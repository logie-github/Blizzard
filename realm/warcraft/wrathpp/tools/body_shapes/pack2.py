"""The body options package (format 2): for each race, the looks' own model with the body layer (layer.py), the body
shapes' models where a race has them (from a format 1 zip: its refined skin and shape vertex blocks), and the layer's
design textures (masks.py). usage:

  pack2.py OUT.zip LOOKS_CLIENT_DIR RACES.json MAPS_DIR [SHAPES_V1.zip]

RACES.json: per race (Human, Orc, ...): {"race": id, "k", "fold", "body", "hair_block"} (layer.py). A model is a
patch of the looks' own (the header and what follows the base: layer.patch), checked by the SHA-256 of the looks' model
it was made from and of the model it makes. The app (WrathppBody) puts the race's own model's back in place of the
looks' model and each shape's beside it, with the textures in each race's folder and the display rows that pick them
(README: "Body options on Wrath++")."""
import hashlib
import io
import json
import os
import struct
import sys
import zipfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "modules", "mod-allied-races", "tools"))
import blp  # noqa: E402
import layer  # noqa: E402
import masks  # noqa: E402
import refine  # noqa: E402

SHAPES = ["As drawn", "Petite", "Curvy", "Voluptuous"]
ALLIANCE = {1, 3, 4, 7, 11}
SELECT = "Curvy"             # the shape whose places choose the layer's triangles for every shape of a model


def sha(b):
    return hashlib.sha256(b).hexdigest()


def vertices_of(m2b):
    nv, ov = struct.unpack_from("<II", m2b, 60)
    return m2b[ov:ov + nv * 48]


def main(out, looks, races_json, maps, v1=None):
    races = json.load(open(races_json))
    index = masks.index_of(maps)
    shapes_zip = zipfile.ZipFile(v1) if v1 else None
    v1_list = json.loads(shapes_zip.read("wrathpp-body.json")) if shapes_zip else {"models": []}
    man = {"format": 2, "kind": "wrathpp-body", "shapes": SHAPES, "densities": [25, 50, 75, 100],
           "styles": {f: masks.styles(f) for f in ("alliance", "horde")}, "races": [], "models": [], "textures": []}
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        def put(name, data):
            z.writestr(name, data)
            return {"file": name, "sha256": sha(data), "size": len(data)}
        for race, R in races.items():
            rel = "Character/%s/Female/%sFemale" % (race, race)
            base = open("%s/%s.m2" % (looks, rel), "rb").read()
            skin = open("%s/%s00.skin" % (looks, rel), "rb").read()
            man["races"].append({"race": race, "race_id": R["race"], "folder": "Character/%s/Female" % race,
                                 "faction": "alliance" if R["race"] in ALLIANCE else "horde"})
            V = vertices_of(base)
            n = layer.count(V, skin, R)
            _, s0, info0 = refine.refine(base, skin, lambda *a: None, levels=0, reserve=3 * n + 30, log=lambda *a: None)
            made, s1, li = layer.add(base, s0, V, R)
            entry = {"race": race, "shape": 0, "model": rel + ".m2", "skin": rel + "00.skin", "looks_sha256": sha(base),
                     "made_sha256": sha(made), "patch": put("%s/0.patch" % race, layer.patch(base, made)),
                     "skin_file": put("%s/0.skin" % race, s1)}
            man["models"].append(entry)
            print(race, "as drawn:", li, flush=True)
            # the body shapes (format 1's refined skin and shape vertices)
            old = next((m for m in v1_list["models"] if m["race"] == race), None)
            if old is None:
                continue
            if old["looks_sha256"] != sha(base):
                raise SystemExit("%s: the shapes were made for other looks" % race)
            blocks = {p: shapes_zip.read(b["file"]) for p, b in old["blocks"].items()}
            vskin = shapes_zip.read(old["skin_file"])
            sel = blocks[SELECT]
            refined = bytearray(base)
            while len(refined) % 16:
                refined.append(0)
            at = len(refined)
            refined += sel
            struct.pack_into("<II", refined, 60, len(sel) // 48, at)
            n = layer.count(sel, vskin, R)
            _, rs, _ = refine.refine(bytes(refined), vskin, lambda *a: None, levels=0, reserve=3 * n + 30, log=lambda *a: None)
            shared = None
            for k, shape in enumerate(SHAPES[1:], 1):
                made, sk, li = layer.add(base, rs, blocks[shape], R, select=sel)
                if shared is None:
                    shared = put("%s/shapes.skin" % race, sk)
                elif sha(sk) != shared["sha256"]:
                    raise SystemExit("%s: the shapes' skins differ" % race)
                man["models"].append({"race": race, "shape": k, "model": "%sWpp%d.m2" % (rel, k), "skin": "%sWpp%d00.skin" % (rel, k),
                                      "anims_of": rel, "looks_sha256": sha(base), "made_sha256": sha(made),
                                      "patch": put("%s/%d.patch" % (race, k), layer.patch(base, made)), "skin_file": shared})
                print(race, shape, li, flush=True)
        # the designs, a texture each style and density, and the empty one
        names = sorted(set(masks.styles("alliance") + masks.styles("horde")))
        for name in names:
            for d, density in enumerate(masks.DENSITIES, 1):
                rgba = masks.texture(maps, index, name, density)
                man["textures"].append(dict(put("designs/%s_%d.blp" % (name, d), blp.write_palette(rgba, alpha=True)), design=name, density=d))
        empty = np.zeros((8, 8, 4), np.uint8)
        man["textures"].append(dict(put("designs/none.blp", blp.write_palette(empty, alpha=True)), design="", density=0))
        z.writestr("wrathpp-body.json", json.dumps(man, indent=1))
    print(os.path.getsize(out) // 1024, "KB")


if __name__ == "__main__":
    main(*sys.argv[1:])
