#!/usr/bin/env python3
"""Packs undead skins for Wrath++'s living races into the file the app imports (World of Warcraft's box, held:
Undead skins (Wrath++); app/src/main/java/com/logie/blizz/wrathpp/WrathppUndead.kt). The skins are pictures of yours,
painted on today's (Shadowlands') textures: they are never in this repository, and neither is the file this makes.

    python3 tools/undead_pack.py LOOKS.json CACHE SKINS OUT.zip

LOOKS.json, CACHE: sl_looks.py's (races; the files fetched by id, where the models are). SKINS: a folder a model, named
as the looks name it (HumanFemale), holding a folder a skin, in the order they are offered, named NN_Name:

    SKINS/HumanFemale/1_Grave Blue/body.png   today's body texture (twice as wide as tall: the body in its left half)
                                   face.png   today's face texture (square: the head as today's model maps it)
    SKINS/HumanFemale/underwear.txt           "none" (the skins are drawn without underwear) or "race" (the race's own
                                              over them: the default)

Each skin becomes what Wrath++'s converted models draw (the allied races' textures.py does the same for the game's own):
the body's left half as a 512 x 512 palettized skin, and the head's used part of the face as a 256 x 128 FaceLower, cut
as that model's head was laid out when it was converted (m2.head_layout). They get names of their own beside the
race's (…SkinUndead00_NN.blp, …FaceLowerUndeadNN.blp), and manifest.json says which is which: the app adds them to the
game's character table as new skin colours after the race's own.
"""
import io
import json
import os
import struct
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sl_looks                                 # noqa: E402  (puts the allied races' tools on the path)
import numpy as np                              # noqa: E402
from PIL import Image                           # noqa: E402

KIND = "wrathpp-undead-skins"


def head_layout_of(read, model):
    """Where the model's head is in today's texture, as the converter decided when it made the model."""
    import m2
    data = read(model["model"])
    chunks = m2.chunks_of(data)
    child = m2.Skeleton(read(struct.unpack_from("<I", chunks["SKID"])[0])) if "SKID" in chunks else m2.OwnSkeleton(data)
    mdl = m2.Model(data, child)
    skin = m2.Skin(read(mdl.skin_ids[0]))
    skin.batches = [b for b in skin.batches if b[9] + max(b[8], 1) <= len(mdl.texture_lookup) and b[6] < len(mdl.materials)]
    types = [k for k, _ in mdl.textures]
    body = [s for s in range(len(skin.sections)) if any(b[3] == s and types[mdl.texture_lookup[b[9]]] == m2.BODY for b in skin.batches)]
    return m2.head_layout(mdl, skin, body)


def skin_folders(model_dir):
    out = []
    for name in sorted(os.listdir(model_dir)):
        full = os.path.join(model_dir, name)
        if os.path.isdir(full) and os.path.isfile(os.path.join(full, "body.png")) and os.path.isfile(os.path.join(full, "face.png")):
            label = name.split("_", 1)[1] if "_" in name and name.split("_", 1)[0].isdigit() else name
            out.append((label.replace("_", " ").strip(), full))
    return out


def swatch_of(skin_rgba):
    """The skin's colour for the creator's swatch: the middle of the chest (classic's layout: the torso, upper right)."""
    h, w = skin_rgba.shape[:2]
    patch = skin_rgba[int(h * 0.12):int(h * 0.36), int(w * 0.60):int(w * 0.90), :3].reshape(-1, 3)
    r, g, b = (int(v) for v in np.median(patch, axis=0))
    return (r << 16) | (g << 8) | b


def pack_model(model, head, model_dir):
    """A model's skins: (manifest entry, {game path: BLP bytes})."""
    import blp
    import textures
    files, skins = {}, []
    for k, (label, folder) in enumerate(skin_folders(model_dir)):
        body = np.array(Image.open(os.path.join(folder, "body.png")).convert("RGBA"))
        left = body[:, :body.shape[1] // 2] if body.shape[1] == 2 * body.shape[0] else body
        if (left.shape[1], left.shape[0]) != textures.SKIN:
            left = textures.resized(np.ascontiguousarray(left), textures.SKIN)
        left = np.ascontiguousarray(left); left[:, :, 3] = 255
        face = np.array(Image.open(os.path.join(folder, "face.png")).convert("RGBA"))
        face[:, :, 3] = 255
        skin_path = "%s\\%sSkinUndead00_%02d.blp" % (model["folder"], model["name"], k)
        face_path = "%s\\%sFaceLowerUndead%02d.blp" % (model["folder"], model["name"], k)
        files[skin_path] = blp.write_palette(left)
        files[face_path] = blp.write_palette(textures.head_cut(face, head))
        skins.append({"name": label, "swatch": swatch_of(left), "skin": skin_path, "face": face_path})
    underwear = "race"
    note = os.path.join(model_dir, "underwear.txt")
    if os.path.isfile(note):
        underwear = open(note).read().strip() or "race"
        if underwear not in ("none", "race"):
            raise ValueError("%s: underwear.txt says %r (none or race)" % (model["name"], underwear))
    return {"name": model["name"], "underwear": underwear, "skins": skins}, files


def pack(looks, read, skins_dir, out_path, log=print):
    manifest = {"format": 1, "kind": KIND, "build": looks.get("build", sl_looks.BUILD), "models": {}}
    files = {}
    for entry in looks["races"].values():
        for sex, model in sorted(entry["models"].items()):
            model_dir = os.path.join(skins_dir, model["name"])
            if not os.path.isdir(model_dir) or not skin_folders(model_dir):
                continue
            item, made = pack_model(model, head_layout_of(read, model), model_dir)
            item["race"], item["sex"] = entry["race"], int(sex)
            manifest["models"]["%d_%d" % (entry["race"], int(sex))] = item
            files.update(made)
            log("%s: %d skins (%s), underwear %s" % (model["name"], len(item["skins"]), ", ".join(s["name"] for s in item["skins"]), item["underwear"]))
    if not manifest["models"]:
        raise SystemExit("no skins found under %s for any model of the looks" % skins_dir)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        z.writestr("manifest.json", json.dumps(manifest, indent=1, sort_keys=True))
        for path in sorted(files):
            z.writestr("client/" + path.replace("\\", "/"), files[path])
    log("%s: %d models, %d textures, %d bytes" % (out_path, len(manifest["models"]), len(files), os.path.getsize(out_path)))
    return manifest


def main(argv):
    if len(argv) != 5:
        print(__doc__, file=sys.stderr)
        return 2
    import package as allied_package
    with open(argv[1]) as f:
        looks = json.load(f)
    pack(looks, allied_package.cached(argv[2], allied_package.wago), argv[3], argv[4])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
