"""A race's entry of races.json (layer.py) measured on the looks' own woman: usage

  measure.py LOOKS_DIR RACES.json Name=id [Name=id ...] [--all]

LOOKS_DIR: the looks package unpacked (client/ and dbc/). Each Name (the model's folder: Goblin, VoidElf ...) not yet in
RACES.json is measured and added (--all: every one again); a race drawn with another's files is written by hand
({"race": 22, "files": "VoidElf"}: pack2.py).

  k     her scale against the Human: the root of (thigh length x hip joints' spacing) over the Human's, from the key
        bones 55 to 58 (the hip joints and the knees); the ten races' entries of 14 November 2026 were this within 0.5%;
  fold  the height the designs hang on: the middle of the lowest front-facing and the highest down-facing point of
        the body on her middle line between the legs, less 2.5 cm x k (the Human's 0.996); an estimate, to be looked
        at in a render (render.py) and corrected by hand where a design sits high or low;
  x     where her front begins (her hip joints, when they stand more than 3 cm behind the model's middle);
  body  the sections drawn with the body's texture on a bare character (the tables' first hair and feature);
  hair_block  the patch of the race's hair textures (16 x 16 grid) where the colours differ most and each is even
        (the strands; a sheet's flat unused parts left out); a race without hair textures (the Worgen, the Vulpera) gets "texture": 1: the layer is drawn
        with her body's own texture under it (her fur), darkened by the design."""
import json
import os
import struct
import sys
import tempfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "modules", "mod-allied-races", "tools"))
import render_m2 as r  # noqa: E402

TABLES = {"CharSections": "iiiisssiii", "CharHairGeosets": "iiiiii", "CharacterFacialHairStyles": "iiiiiiii"}
GRID = 16


def tables(dbc_dir, out_dir):
    """The looks' character tables as the text files render_m2.py reads (its rows())."""
    os.makedirs(out_dir, exist_ok=True)
    for name, kinds in TABLES.items():
        b = open(os.path.join(dbc_dir, name + ".dbc"), "rb").read()
        n, _, size, _ = struct.unpack_from("<4I", b, 4)
        strings = b[20 + n * size:]
        with open(os.path.join(out_dir, name + ".txt"), "w", encoding="utf-8") as f:
            f.write("types\t%s\n" % kinds)
            for i in range(n):
                row = struct.unpack_from("<%di" % len(kinds), b, 20 + i * size)
                vals = [strings[v:strings.index(b"\0", v)].decode("latin1").replace("\\", "\\\\") if k == "s" else str(v) for k, v in zip(kinds, row)]
                f.write("put\t" + "\t".join(vals) + "\n")
    return out_dir


def woman(looks, name):
    m = r.Model("%s/client/Character/%s/Female/%sFemale.m2" % (looks, name, name))
    return m, r.Skin(os.path.join(m.folder, m.name + "00.skin"))


def joints(m):
    """The hip joints and the knees (2 x 3 each, her left first): the key bones 56, 55 and 58, 57."""
    key = [struct.unpack_from("<i", m.m, b[2] - 16)[0] for b in m.bones]
    piv = [b[5] for b in m.bones]
    need = [k for k in (55, 56, 57, 58) if k not in key]
    if need:
        raise ValueError("%s: no key bone %s" % (m.name, need))
    return np.array([piv[key.index(56)], piv[key.index(55)]], np.float64), np.array([piv[key.index(58)], piv[key.index(57)]], np.float64)


def legs(m):
    hip, knee = joints(m)
    return float(np.linalg.norm(hip - knee, axis=1).mean()), float(abs(hip[0, 1] - hip[1, 1])), float(hip[:, 2].mean())


def body_sections(m, sk, dbc, race):
    shown = r.visible_geosets(dbc, race, 1, 0, 0, {s[0] for s in sk.sections})
    return sorted({int(sk.sections[b[3]][0]) for b in sk.batches
                   if sk.sections[b[3]][0] in shown and b[9] < len(m.tex_lookup) and m.textures[m.tex_lookup[b[9]]][0] == 1})


def fold_of(m, sk, body, k, thigh, w, hz):
    bv = np.unique(np.concatenate([sk.vertices[sk.indices[s[4] + s[1] * 65536: s[4] + s[1] * 65536 + s[5]]] for s in sk.sections if s[0] in body]))
    P, N = m.pos[bv], m.normals[bv]
    mid = (np.abs(P[:, 1]) < 0.12 * w) & (P[:, 2] > hz - 0.6 * thigh) & (P[:, 2] < hz + 0.25 * thigh)
    down = mid & (N[:, 2] < -0.5)
    front = mid & (N[:, 0] > 0.5) & (P[:, 0] > P[mid, 0].mean() if mid.any() else False)
    if not down.any():
        raise ValueError("%s: nothing faces down between the legs" % m.name)
    cz = float(P[down, 2].max())
    zf = float(P[front, 2].min()) if front.any() else cz
    return (cz + min(zf, cz + 0.06 * k)) / 2 - 0.025 * k


def hair_block(looks, dbc, race):
    """(column, row) of the hair textures' patch with every colour's strands, or None where the race has no hair textures."""
    rows = r.rows(os.path.join(dbc, "CharSections.txt"), "iiiisssiii")
    A = []
    q = 256 // GRID
    for t in sorted({x[4] for x in rows if x[1] == race and x[2] == 1 and x[3] == 3 and x[4]}):
        a = r.read_blp(os.path.join(looks, "client"), t)
        if a is not None:
            A.append(np.asarray(Image.fromarray(np.asarray(a)).resize((256, 256), Image.BOX)).astype(float)[..., :3])
    if len(A) < 2:
        return None
    L = np.array(A) @ [0.299, 0.587, 0.114]
    blocks = L.reshape(len(A), GRID, q, GRID, q)
    within = blocks.std((2, 4)).mean(0) / (blocks.mean((2, 4)).mean(0) + 1)
    cross = L.std(0).reshape(GRID, q, GRID, q)
    score = cross.min(axis=(1, 3)) - 40 * within
    score[40 * within < 1.5] = -1e9                             # (a sheet's unused parts are flat: strands are not)
    by, bx = np.unravel_index(score.argmax(), score.shape)
    return [int(bx), int(by)]


def measure(looks, dbc, name, race, human=None):
    m, sk = woman(looks, name)
    human = human or legs(woman(looks, "Human")[0])
    thigh, w, hz = legs(m)
    k = float(np.sqrt(thigh / human[0] * w / human[1]))
    body = body_sections(m, sk, dbc, race)
    out = {"race": race, "k": round(k, 5), "fold": round(fold_of(m, sk, body, k, thigh, w, hz), 5), "body": body}
    hx = float(joints(m)[0][:, 0].mean())
    if hx < -0.03:
        out["x"] = round(hx, 5)                                 # (her hips stand behind the model's middle: her front begins there)
    block = hair_block(looks, dbc, race)
    if block is None:
        out["texture"] = 1
        out["hair_block"] = [0, 0]
    else:
        out["hair_block"] = block
    return out


def main(argv):
    every = "--all" in argv
    argv = [a for a in argv if a != "--all"]
    looks, path = argv[:2]
    races = json.load(open(path)) if os.path.isfile(path) else {}
    with tempfile.TemporaryDirectory() as tmp:
        dbc = tables(os.path.join(looks, "dbc"), tmp)
        human = legs(woman(looks, "Human")[0])
        for spec in argv[2:]:
            name, rid = spec.split("=")
            if name in races and not every:
                continue
            new = measure(looks, dbc, name, int(rid), human)
            old = races.get(name)
            if old and old.get("fold_by_hand"):
                new["fold"], new["fold_by_hand"] = old["fold"], True
            races[name] = new
            print(name, json.dumps(new), flush=True)
    json.dump(races, open(path, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
