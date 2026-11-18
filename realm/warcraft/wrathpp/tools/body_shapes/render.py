"""The package's models as the app makes them, drawn (render_m2.py) for looking at: usage

  render.py PACKAGE.zip LOOKS_DIR OUT_DIR [--design NAME_DENSITY] [--views close,front,side,rear,run] [Race ...]

LOOKS_DIR: the looks package unpacked (client/ and dbc/). For each race of the package (or those named) one picture
OUT_DIR/<Race>.png: a row per shape the package has for her (As drawn first), a column per view: close (the layer with
a design, default natural at 100%), front, side and rear standing, and run (the Run animation, from the side-rear).
The models are made from the looks' own by the package's patches, checked by its SHA-256s, into OUT_DIR/game."""
import hashlib
import json
import os
import sys
import tempfile
import zipfile

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "modules", "mod-allied-races", "tools"))
import blp  # noqa: E402
import layer  # noqa: E402
import measure  # noqa: E402
import render_m2 as r  # noqa: E402

SIZE = 300
STAND, RUN = 0, 5


def unpack(z, man, looks, out, only=None):
    """Each model the package makes, written under [out] with the looks' animation files linked under its name."""
    made = {}
    for m in man["models"]:
        if only and m["race"] not in only:
            continue
        rel = m["model"] if m["shape"] == 0 else m["anims_of"] + ".m2"
        base = open(os.path.join(looks, "client", rel), "rb").read()
        model = layer.unpatch(base, z.read(m["patch"]["file"]))
        if hashlib.sha256(model).hexdigest() != m["made_sha256"]:
            raise SystemExit("%s shape %d: the looks given are not the package's (rebase it)" % (m["race"], m["shape"]))
        path = os.path.join(out, m["model"])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "wb").write(model)
        open(os.path.join(out, m["skin"]), "wb").write(z.read(m["skin_file"]["file"]))
        src = os.path.dirname(os.path.join(looks, "client", rel))
        prefix, own = os.path.basename(rel)[:-3], os.path.basename(m["model"])[:-3]
        for f in os.listdir(src):
            if f.startswith(prefix) and f.endswith(".anim") and f[len(prefix):len(prefix) + 4].isdigit():
                dst = os.path.join(os.path.dirname(path), own + f[len(prefix):])
                if not os.path.lexists(dst):
                    os.symlink(os.path.realpath(os.path.join(src, f)), dst)
        made.setdefault(m["race"], {})[m["shape"]] = path
    return made


def views(k, fold, height, hips, chest):
    """[hips], [chest]: where her hips' middle and her chest bone are in the pose drawn (x, y, z)."""
    x, y, hz, rest = hips
    z = fold + 0.024 * k + (hz - rest)
    mid = 0.52 * height
    d = 1.75 * height
    cx, cy, cz = chest[0] + 0.06 * k, chest[1], chest[2] + 0.03 * k
    return {"close": ((x + 0.9 * k, y, z + 0.05 * k), (x + 0.04 * k, y, z + 0.01 * k), 0.38),
            "front": ((d, 0.35 * d, mid + 0.1 * height), (0, 0, mid), 0.62),
            "side": ((0.0, d, mid), (0, 0, mid), 0.62),
            "rear": ((-d, 0.45 * d, mid), (0, 0, mid), 0.62),
            "run": ((-0.8 * d, 0.8 * d, mid), (0, 0, mid), 0.62),
            "chest": ((cx + 1.1 * k, cy + 0.8 * k, cz + 0.05 * k), (cx + 0.05 * k, cy, cz), 0.6),
            "chestside": ((cx + 0.05 * k, cy + 1.3 * k, cz), (cx + 0.05 * k, cy, cz), 0.55),
            "seat": ((x - 1.2 * k, y + 0.75 * k, z + 0.12 * k), (x - 0.05 * k, y, z + 0.06 * k), 0.6),
            "seatside": ((x, y + 1.4 * k, z + 0.06 * k), (x, y, z + 0.06 * k), 0.55)}


def posed(world, bone, pivot):
    return (world[bone] @ np.append(pivot, 1.0))[:3]


def bare(dbc):
    """The tables without the women's underwear (Wrath++ draws none: WrathppBare)."""
    p = os.path.join(dbc, "CharSections.txt")
    lines = [ln for ln in open(p, encoding="utf-8") if not (ln.startswith("put\t") and ln.split("\t")[3:5] == ["1", "4"])]
    open(p, "w", encoding="utf-8").writelines(lines)
    return dbc


def sheet(race, entry, paths, looks, dbc, design, which, shapes, hair=0):
    files = os.path.join(looks, "client")
    L = entry["layer"]
    tex, hair_tex = r.compose(files, dbc, entry["race_id"], 1, 0, 0, hair)
    light = np.array([1.0, 0.6, 1.2])
    light /= np.linalg.norm(light)
    rows = []
    for shape in sorted(paths):
        m = r.Model(paths[shape])
        sk = r.Skin(paths[shape][:-3] + "00.skin")
        shown = r.visible_geosets(dbc, entry["race_id"], 1, hair, 0, {s[0] for s in sk.sections}) | {layer.GEOSET}
        key = [__import__("struct").unpack_from("<i", m.m, b[2] - 16)[0] for b in m.bones]
        seq = {i: next((j for j, s in enumerate(m.seqs) if s[0] == i and s[1] == 0), None) for i in (STAND, RUN)}
        ims = []
        for v in which:
            s = seq[RUN] if v == "run" and seq[RUN] is not None else seq[STAND]
            world = m.bone_matrices(s, 300 if v == "run" else 400)
            hl, hr = (posed(world, key.index(q), m.bones[key.index(q)][5]) for q in (56, 55))
            rest = (m.bones[key.index(56)][5][2] + m.bones[key.index(55)][5][2]) / 2
            cb = key.index(53) if 53 in key else key.index(56)
            hips = tuple((hl + hr) / 2 + [0.03 * L["k"], 0, 0]) + (rest,)
            eye, target, fov = views(L["k"], L["fold"], float(m.pos[:, 2].max()), hips, posed(world, cb, m.bones[cb][5]))[v]
            img, _ = r.render(m, sk, tex, hair_tex, files, shown, world, (fov, 0.1, 100.0, np.array(eye, float), np.array(target, float)),
                              (SIZE, int(SIZE * 1.25)), light, design_tex=design)
            ims.append(Image.fromarray(img))
        row = Image.new("RGB", (SIZE * len(ims), ims[0].height))
        for i, im in enumerate(ims):
            row.paste(im, (i * SIZE, 0))
        ImageDraw.Draw(row).text((4, 4), "%s: %s" % (race, shapes[shape]), fill=(255, 230, 150))
        rows.append(row)
    out = Image.new("RGB", (rows[0].width, sum(x.height for x in rows)))
    y = 0
    for x in rows:
        out.paste(x, (0, y))
        y += x.height
    return out


def main(argv):
    opts = {"--design": "natural_4", "--views": "close,front,side,rear,run"}
    args = []
    i = 0
    while i < len(argv):
        if argv[i] in opts:
            opts[argv[i]] = argv[i + 1]
            i += 2
        else:
            args.append(argv[i])
            i += 1
    package, looks, out = args[:3]
    only = set(args[3:])
    z = zipfile.ZipFile(package)
    man = json.loads(z.read("wrathpp-body.json"))
    design = blp.read(z.read("designs/%s.blp" % opts["--design"])) if opts["--design"] != "none" else None
    made = unpack(z, man, looks, os.path.join(out, "game"), only)
    with tempfile.TemporaryDirectory() as tmp:
        dbc = bare(measure.tables(os.path.join(looks, "dbc"), tmp))
        for entry in man["races"]:
            race = entry.get("files", entry["race"])
            if race not in made or (only and entry["race"] not in only and race not in only) or "layer" not in entry:
                continue
            img = sheet(entry["race"], entry, made[race], looks, dbc, design, opts["--views"].split(","), man["shapes"])
            img.save(os.path.join(out, entry["race"] + ".png"))
            print(entry["race"], img.size, flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
