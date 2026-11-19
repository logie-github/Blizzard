#!/usr/bin/env python3
"""Extra skins: a picture of today's game (a wago file id) made one more skin colour of a race and sex, the creator offering it whatever
the Ralia import supplies (`keep`). One line of [EXTRA_SKINS] a skin:

    {"race": 1, "sex": 1, "name": "Ash", "file": 201749, "swatch": (26, 26, 24), "build": None}

race, sex: the model (the ten races of 3.3.5: looks.json); name: the creator's name for it; file: the wago file id of a texture in the CLASSIC body
layout (one picture of the whole body, 3.3.5's skin: the face and underwear painted in); swatch: the colour the creator draws its swatch in
(the picture's mean, kept here so that making the looks needs no download); build: a retail build to fetch the file at, or None for the newest.

[extend] adds the skin to the looks (sl_looks.py races): a base skin after the model's own (the next colour number), a made-up file id
(EXTRA_BASE and up) naming its picture ([Reader] makes the file when the package step asks for it), "bare": True (its rows name no face, eye or
underwear texture: the picture has them painted in, so the rows exist, with empty names, and no look-up hits a missing row), the creator's choice
row (`extra_choices`, `keep`). The model's body is taken as the left half of the file's picture (textures.py), so [Reader] gives the picture twice
side by side. A skin of a model with tattoo blocks is refused (its skins are numbered by block)."""
import numpy as np

EXTRA_BASE = 2100000000
EXTRA_SKINS = [
    {"race": 1, "sex": 1, "name": "Ash", "file": 201749, "swatch": (26, 26, 24), "build": None},
]


def extend(looks, extra=None):
    """[looks] (looks.json: {"races": ...}) with the extra skins added to the models they are for; in place, returns [looks]. Done once a skin."""
    for n, spec in enumerate(EXTRA_SKINS if extra is None else extra):
        entry = looks["races"].get(str(spec["race"]))
        model = entry["models"].get(str(spec["sex"])) if entry else None
        if model is None:
            continue
        choice = "extra:" + spec["name"].lower().replace(" ", "-")
        if any(s["choice"] == choice for s in model["skins"]):
            continue
        if len(model["tattoos"]) > 1 or len(model["skins"]) != model["base_skins"]:
            raise ValueError("%s: an extra skin on a model with tattoo blocks isn't made" % model["name"])
        fid = EXTRA_BASE + n
        place = model["base_skins"]
        model["skins"].append({"base": place, "body": fid, "choice": choice, "index": place, "order": 2000 + n, "pelvis": 0, "torso": 0,
                               "tattoo": [], "tattoo_name": model["skins"][0]["tattoo_name"], "bare": True, "added": spec["name"]})
        model["base_skins"] = place + 1
        for face in model["faces"]:
            face["skins"] = sorted(set(face["skins"]) | {place})
        r, g, b = spec["swatch"]
        model.setdefault("extra_choices", {}).setdefault("Skin Color", []).append(
            {"ID": choice, "Name_lang": spec["name"], "ChrCustomizationReqID": "0", "SwatchColor_0": str(r << 16 | g << 8 | b), "SwatchColor_1": "0", "keep": True})
        model.setdefault("extra_files", {})[str(fid)] = {"file": spec["file"], "build": spec.get("build")}
    return looks


class Reader:
    """A reader that makes an extra skin's made-up file id's texture (the picture twice side by side, DXT: textures.py takes the left half
    of a body and sizes it to 3.3.5's skin) and passes every other file id to [read]. [files]: {made-up id: {"file", "build"}};
    [read_at]: build -> a reader of that build's copies (a pinned file)."""

    def __init__(self, read, files, read_at):
        import blp
        self.blp, self.read, self.read_at = blp, read, read_at
        self.files = {int(k): v for k, v in files.items()}

    def __call__(self, fid):
        spec = self.files.get(fid) if isinstance(fid, int) else None
        if spec is None:
            return self.read(fid)
        data = (self.read_at(spec["build"]) if spec.get("build") else self.read)(spec["file"])
        picture = np.ascontiguousarray(self.blp.read(data))
        return self.blp.write_dxt(np.ascontiguousarray(np.hstack([picture, picture])), alpha=False)
