"""The races' character textures for 3.3.5, from the game's of today (tools/package.py runs
this; tools/races.json says which files; the model's layout.json, written by tools/m2.py, says
where the head went).

3.3.5 composes a character's texture itself (a square: the body as classic's, the face region
in its lower left quarter) from palettized textures in CharSections: the skin (512 x 512 here, as
the HD looks' are), the face (FaceLower 256 x 128 and FaceUpper 256 x 64, drawn over the face
region), the underwear (256 x 128 each) and the hair (drawn by the model as it is, DXT).

Today's body texture is 1024 x 512: the body in its left half (classic's layout exactly, so that
half is the 3.3.5 skin as it is) and the head in its right, drawn over by the face texture
(512 x 512, opaque) and, for nightborne, the eye colour's glow on the face (an additive overlay);
the eyes are a texture of their own (256 x 128) on the eyeball mesh. Here the face becomes
FaceLower (the head's used part, turned if that fits better, as the model's coordinates were
remapped) and the eyes FaceUpper (the strip the eyeball mesh's coordinates were remapped to).
Nightborne body tattoos are painted into the skin (a skin colour of their own each)."""
import os

import numpy as np
from PIL import Image

import blp
import names

SKIN, FACE_LOWER, FACE_UPPER, UNDERWEAR = (512, 512), (256, 128), (256, 64), (256, 128)


def image(rgba):
    return Image.fromarray(rgba, "RGBA")


def over(base, layer):
    """[layer] (RGBA) alpha-blended over [base] (RGBA), both the same size."""
    a = layer[:, :, 3:4].astype(np.float32) / 255.0
    out = base.astype(np.float32)
    out[:, :, :3] = layer[:, :, :3] * a + out[:, :, :3] * (1 - a)
    return np.clip(out, 0, 255).astype(np.uint8)


def add(base, layer):
    """[layer] added to [base] (an additive glow), weighted by its alpha."""
    a = layer[:, :, 3:4].astype(np.float32) / 255.0
    out = base.astype(np.float32)
    out[:, :, :3] = out[:, :, :3] + layer[:, :, :3] * a
    return np.clip(out, 0, 255).astype(np.uint8)


def resized(rgba, size):
    return np.array(image(rgba).resize(size, Image.Resampling.LANCZOS))


def head_cut(face_rgba, layout):
    """The head's used part of a 512 x 512 face texture, turned and sized as FaceLower."""
    u0, v0, u1, v1 = layout["box"]
    h, w = face_rgba.shape[:2]
    x0, x1 = int(round((u0 - 0.5) * 2 * w)), int(round((u1 - 0.5) * 2 * w))
    y0, y1 = int(round(v0 * h)), int(round(v1 * h))
    x1, y1 = max(x1, x0 + 1), max(y1, y0 + 1)
    cut = face_rgba[y0:y1, x0:x1]
    if layout["rotate"]:
        # the model's coordinates were turned: (fu, fv) -> (fv, 1 - fu), so the picture turns the same way
        cut = np.rot90(cut, k=1)
    return resized(np.ascontiguousarray(cut), FACE_LOWER)


class Writer:
    def __init__(self, out_dir, log):
        self.out_dir, self.log, self.written = out_dir, log, []

    def write(self, path, data):
        full = os.path.join(self.out_dir, path.replace("\\", "/"))
        if not os.path.exists(full):
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full + ".part", "wb") as f:
                f.write(data)
            os.replace(full + ".part", full)
        self.written.append(path)

    def exists(self, path):
        return os.path.exists(os.path.join(self.out_dir, path.replace("\\", "/")))


def build(read, model, layout, out_dir, log=print):
    """Writes the model's textures into [out_dir]; returns their paths."""
    w = Writer(out_dir, log)
    n = {"skin": lambda c: names.skin(model, c), "pelvis": lambda c: names.pelvis(model, c), "torso": lambda c: names.torso(model, c),
         "hair": lambda c: names.hair(model, c)}
    head = layout["head"]
    eyes = model["eyes"]
    faces = model["faces"]
    base_count = model["base_skins"]
    cache = {}

    def texture(fid):
        if fid not in cache:
            cache[fid] = blp.read(read(fid))
        return cache[fid]

    # Skins: the body's left half; a tattoo painted over it.
    for s in model["skins"]:
        path = n["skin"](s["index"])
        if not w.exists(path):
            body = texture(s["body"])
            left = body[:, :body.shape[1] // 2]
            if left.shape[0] != SKIN[1] or left.shape[1] != SKIN[0]:
                left = resized(np.ascontiguousarray(left), SKIN)
            for fid in s["tattoo"][:1]:
                tattoo = texture(fid)
                half = tattoo[:, :tattoo.shape[1] // 2] if tattoo.shape[1] == 2 * tattoo.shape[0] else tattoo
                left = over(left, resized(np.ascontiguousarray(half), SKIN))
            w.write(path, blp.write_palette(np.ascontiguousarray(left)))
        else:
            w.write(path, b"")
        for kind in ("pelvis", "torso"):
            if s[kind]:
                path = n[kind](s["index"])
                if not w.exists(path):
                    w.write(path, blp.write_palette(resized(texture(s[kind]), UNDERWEAR), alpha=True))
                else:
                    w.write(path, b"")

    # Faces: FaceLower from the head, one a face texture (and a nightborne eye glow), FaceUpper
    # one an eye colour; the tables name them for every face number on every skin.
    for e in eyes:
        path = names.face_upper(model, e)
        if not w.exists(path):
            upper = np.array(resized(texture(e["file"]), FACE_UPPER))
            upper[:, :, 3] = 255
            w.write(path, blp.write_palette(upper))
        else:
            w.write(path, b"")
    face_files = sorted(set(v for f in faces for v in f["textures"].values() if v))
    for fid in face_files:
        for e in (eyes if any(e.get("overlay") for e in eyes) else [None]):
            path = names.face_lower(model, fid, e)
            if w.exists(path):
                w.write(path, b"")
                continue
            face = texture(fid)
            if e is not None and e.get("overlay"):
                face = add(face, resized(texture(e["overlay"]), (face.shape[1], face.shape[0])))
            w.write(path, blp.write_palette(head_cut(face, head)))

    # Hair: the colours' textures as they are (DXT, the model's own).
    for h in model["hair_colors"]:
        path = n["hair"](h["index"])
        if not w.exists(path):
            w.write(path, read(h["file"]))
        else:
            w.write(path, b"")
    log("%s: %d textures" % (model["name"], len(set(w.written))))
    return sorted(set(w.written))
