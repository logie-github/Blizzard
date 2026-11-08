#!/usr/bin/env python3
"""A converted model drawn the way the 3.3.5 game draws it, to a PNG: the skin's sections through
their bone combos (a vertex's bone slots lead through the section's combo to the model's bones),
posed on an animation (Stand, by default) at a moment, with the character's composed texture (the
skin, the underwear, the face's lower and upper parts in the body texture's regions; the hair's own
texture), the hardcoded textures, and the model's own cameras (type 1: the character screen's full
figure; type 0: the portrait). Nothing here is the game: it is its reading of the files, which is
what the converter has to satisfy.

    python3 tools/render_m2.py MODEL.m2 FILES DBC_DIR OUT.png [--race 15 --sex 1 --skin 0 --face 0
                                                              --hair 0 --feature 0 --time 400
                                                              --camera 1 --size 480x720]

FILES: the package (tools/package.py's output: the textures by the paths the tables name);
DBC_DIR: the module's data/client/dbc (CharSections, CharHairGeosets, CharacterFacialHairStyles).
Needs numpy and Pillow.
"""
import argparse
import math
import os
import struct
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import blp  # noqa: E402


def arr(m, off):
    return struct.unpack_from("<II", m, off)


class Model:
    def __init__(self, path):
        self.path = path
        self.folder = os.path.dirname(path)
        self.name = os.path.splitext(os.path.basename(path))[0]
        m = self.m = open(path, "rb").read()
        if m[:4] != b"MD20":
            raise ValueError("not a 3.3.5 model: " + path)
        n, o = arr(m, 20)
        self.global_seqs = list(struct.unpack_from("<%dI" % n, m, o))
        n, o = arr(m, 28)
        self.seqs = [struct.unpack_from("<HHIfIhHIIIffffffffhH", m, o + i * 64) for i in range(n)]
        self.in_file = [bool(s[4] & 0x20) for s in self.seqs]
        n, o = arr(m, 44)
        self.bones = []
        for i in range(n):
            at = o + i * 88
            key, flags, parent = struct.unpack_from("<iIh", m, at)
            self.bones.append((parent, flags, at + 16, at + 36, at + 56, np.array(struct.unpack_from("<3f", m, at + 76))))
        n, o = arr(m, 60)
        self.vertices = np.frombuffer(m, dtype=np.uint8, count=n * 48, offset=o).reshape(n, 48)
        self.pos = np.frombuffer(self.vertices[:, 0:12].tobytes(), dtype="<f4").reshape(n, 3)
        self.weights = self.vertices[:, 12:16].astype(np.float32) / 255.0
        self.vbones = self.vertices[:, 16:20].astype(np.int32)
        self.normals = np.frombuffer(self.vertices[:, 20:32].tobytes(), dtype="<f4").reshape(n, 3)
        self.uv = np.frombuffer(self.vertices[:, 32:40].tobytes(), dtype="<f4").reshape(n, 2)
        n, o = arr(m, 80)
        self.textures = []
        for i in range(n):
            kind, flags, nn, no = struct.unpack_from("<IIII", m, o + i * 16)
            self.textures.append((kind, m[no:no + nn].split(b"\0")[0].decode("latin-1")))
        n, o = arr(m, 112)
        self.materials = [struct.unpack_from("<HH", m, o + i * 4) for i in range(n)]
        n, o = arr(m, 120)
        self.bone_lookup = list(struct.unpack_from("<%dH" % n, m, o))
        n, o = arr(m, 128)
        self.tex_lookup = list(struct.unpack_from("<%dh" % n, m, o))
        n, o = arr(m, 272)
        self.cameras = []
        for i in range(n):
            at = o + i * 100
            kind, fov, far, near = struct.unpack_from("<Ifff", m, at)
            self.cameras.append((kind, fov, near, far, at + 16, np.array(struct.unpack_from("<3f", m, at + 36)),
                                 at + 48, np.array(struct.unpack_from("<3f", m, at + 68))))
        self.anim_files = {}

    def anim_data(self, seq):
        """Where an external sequence's track data is."""
        if self.in_file[seq]:
            return self.m
        if seq not in self.anim_files:
            sid, var = self.seqs[seq][0], self.seqs[seq][1]
            path = os.path.join(self.folder, "%s%04d-%02d.anim" % (self.name, sid, var))
            self.anim_files[seq] = open(path, "rb").read() if os.path.exists(path) else b""
        return self.anim_files[seq]

    def track(self, at, seq, t, size, fmt, default):
        """A track's value for sequence seq at time t (ms): linear between keys."""
        m = self.m
        interp, gseq, tn, to, vn, vo = struct.unpack_from("<HhIIII", m, at)
        if gseq >= 0:
            use = 0
            length = self.global_seqs[gseq] if gseq < len(self.global_seqs) else 0
            t = t % length if length else 0
        else:
            use = seq
        if use >= tn or use >= vn:
            return default
        kn, ko = struct.unpack_from("<II", m, to + use * 8)
        dn, do = struct.unpack_from("<II", m, vo + use * 8)
        if kn == 0 or dn == 0:
            return default
        data = self.anim_data(use) if gseq < 0 else m
        if not data:
            return default
        times = np.frombuffer(data, dtype="<u4", count=kn, offset=ko)
        if fmt == "q":
            raw = np.frombuffer(data, dtype="<i2", count=dn * 4, offset=do).reshape(dn, 4).astype(np.float64)
            vals = np.where(raw < 0, raw + 32767, raw - 32767) / 32767.0
        else:
            vals = np.frombuffer(data, dtype="<f4", count=dn * 3, offset=do).reshape(dn, 3).astype(np.float64)
        i = int(np.searchsorted(times, t, side="right")) - 1
        if i < 0:
            return vals[0]
        if i >= len(vals) - 1 or interp == 0:
            return vals[min(i, len(vals) - 1)]
        t0, t1 = times[i], times[i + 1]
        f = 0.0 if t1 <= t0 else (t - t0) / float(t1 - t0)
        a, b = vals[i], vals[i + 1]
        if fmt == "q":
            if np.dot(a, b) < 0:
                b = -b
            v = a * (1 - f) + b * f
            n = np.linalg.norm(v)
            return v / n if n else a
        return a * (1 - f) + b * f

    def bone_matrices(self, seq, t):
        world = [None] * len(self.bones)
        for i, (parent, flags, ta, ra, sa, pivot) in enumerate(self.bones):
            tr = self.track(ta, seq, t, 12, "v", np.zeros(3))
            q = self.track(ra, seq, t, 8, "q", np.array([0.0, 0.0, 0.0, 1.0]))
            sc = self.track(sa, seq, t, 12, "v", np.ones(3))
            x, y, z, w = q
            r = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                          [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                          [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
            local = np.eye(4)
            local[:3, :3] = r * sc[None, :]
            local[:3, 3] = pivot + tr - local[:3, :3] @ pivot
            world[i] = local if parent < 0 else world[parent] @ local
        return np.array(world)

    def camera(self, kind, seq, t):
        for ckind, fov, near, far, pa, pbase, ta, tbase in self.cameras:
            if ckind == kind:
                pos = pbase + self.track(pa, seq, t, 36, "v", np.zeros(3))[:3]
                target = tbase + self.track(ta, seq, t, 36, "v", np.zeros(3))[:3]
                return fov, near, far, pos, target
        return None


class Skin:
    def __init__(self, path):
        s = open(path, "rb").read()
        vn, vo, ixn, ixo, pn, po, sn, so, bn, bo = struct.unpack_from("<10I", s, 4)
        self.vertices = np.frombuffer(s, dtype="<u2", count=vn, offset=vo).astype(np.int64)
        self.indices = np.frombuffer(s, dtype="<u2", count=ixn, offset=ixo).astype(np.int64)
        self.slots = np.frombuffer(s, dtype=np.uint8, count=pn * 4, offset=po).reshape(pn, 4).astype(np.int64)
        self.sections = [struct.unpack_from("<10H7f", s, so + i * 48) for i in range(sn)]
        self.batches = [struct.unpack_from("<BbHHHhHHHHHHH", s, bo + i * 24) for i in range(bn)]


def rows(path, kinds):
    """The 'put' rows of a tables' changes file, typed by its 'types' line."""
    out = []
    for line in open(path, encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        if f[0] == "put":
            out.append([int(v) if k == "i" else (float(v) if k == "f" else v.replace("\\\\", "\\")) for k, v in zip(kinds, f[1:])])
        elif f[0] == "appendraw":
            raw = bytes.fromhex(f[1])
            out.append(list(struct.unpack("<%di" % (len(raw) // 4), raw)))
    return out


def read_blp(files, path):
    if not path:
        return None
    full = os.path.join(files, *path.split("\\"))
    if not os.path.isfile(full):
        return None
    return blp.read(open(full, "rb").read())


def paste(dst, src, x0, y0, x1, y1):
    """src scaled into dst's region, blended by its alpha."""
    h, w = y1 - y0, x1 - x0
    img = Image.fromarray(src).resize((w, h), Image.BILINEAR)
    s = np.asarray(img).astype(np.float32)
    a = s[:, :, 3:4] / 255.0
    region = dst[y0:y1, x0:x1].astype(np.float32)
    region[:, :, :3] = region[:, :, :3] * (1 - a) + s[:, :, :3] * a
    dst[y0:y1, x0:x1] = region.astype(np.uint8)


def compose(files, dbc, race, sex, skin, face, hair):
    sections = rows(os.path.join(dbc, "CharSections.txt"), "iiiisssiii")
    mine = [r for r in sections if r[1] == race and r[2] == sex]
    def pick(kind, variation, color):
        for r in mine:
            if r[3] == kind and r[8] == variation and r[9] == color:
                return r
        return None
    body = None
    row = pick(0, skin, 0)
    if row:
        body = read_blp(files, row[4])
    if body is None:
        body = np.full((512, 512, 4), 128, dtype=np.uint8)
    body = np.array(body)
    if body.shape[0] != 512:
        body = np.asarray(Image.fromarray(body).resize((512, 512)))
    body = np.array(body)
    row = pick(4, skin, 0)
    if row:
        pelvis, torso = read_blp(files, row[4]), read_blp(files, row[5])
        if pelvis is not None:
            paste(body, pelvis, 256, 192, 512, 320)        # LegUpper
        if torso is not None:
            paste(body, torso, 256, 0, 512, 128)           # TorsoUpper
    row = pick(1, face, skin)
    if row:
        lower, upper = read_blp(files, row[4]), read_blp(files, row[5])
        if lower is not None:
            paste(body, lower, 0, 384, 256, 512)           # FaceLower
        if upper is not None:
            paste(body, upper, 0, 320, 256, 384)           # FaceUpper
    hair_tex = None
    row = pick(3, hair, 0)
    if row:
        hair_tex = read_blp(files, row[4])
    return body, hair_tex


def visible_geosets(dbc, race, sex, hair, feature, present):
    """What the 3.3.5 game shows of a character model with nothing worn: geoset 0 always (the
    body), the hair style's geoset, the feature's (groups 1, 2, 3, 16, 17 from the facial table),
    and of each other group it knows (up to 18) the first geoset (X01; the ears' 702). Groups the
    game doesn't know (19 and up) aren't shown: the converter folds the body parts today's models
    keep there into geoset 0."""
    shown = {0}
    for r in rows(os.path.join(dbc, "CharHairGeosets.txt"), "iiiiii"):
        if r[1] == race and r[2] == sex and r[3] == hair:
            shown.add(r[4])
            if r[5]:
                shown.add(0)
    for r in rows(os.path.join(dbc, "CharacterFacialHairStyles.txt"), "iiiiiiii"):
        if r[0] == race and r[1] == sex and r[2] == feature:
            for group, value in zip((1, 3, 2, 16, 17), r[3:8]):
                if value:
                    shown.add(group * 100 + value)
    groups = {g // 100 for g in present}
    for g in groups:
        if g in (0, 1, 2, 3, 16, 17) or g > 18:
            continue
        default = 702 if g == 7 else g * 100 + 1
        if default in present:
            shown.add(default)
    return shown


def look_at(eye, target, up=(0, 0, 1)):
    f = target - eye
    f /= np.linalg.norm(f)
    s = np.cross(f, np.array(up, dtype=float))
    s /= np.linalg.norm(s)
    u = np.cross(s, f)
    view = np.eye(4)
    view[0, :3], view[1, :3], view[2, :3] = s, u, -f
    view[:3, 3] = -view[:3, :3] @ eye
    return view


def render(model, skin, texture, hair_tex, files, shown, world, camera, size, light_dir):
    W, H = size
    fov, near, far, eye, target = camera
    view = look_at(eye, target)
    aspect = W / H
    f = 1.0 / math.tan(fov / 2)
    image = np.zeros((H, W, 3), dtype=np.float32)
    image[:] = (36, 30, 48)
    zbuf = np.full((H, W), np.inf)
    # every skin vertex posed through its section's combo
    N = len(skin.vertices)
    posed = np.zeros((N, 3))
    normals = np.zeros((N, 3))
    for sec in skin.sections:
        sid, level, vs, vc, is_, ic, bc, bci, binf, cb = sec[:10]
        ks = np.arange(vs, vs + vc)
        g = skin.vertices[ks]
        p = model.pos[g]
        n = model.normals[g]
        w = model.weights[g]
        slots = skin.slots[ks]
        acc = np.zeros((vc, 3))
        nacc = np.zeros((vc, 3))
        for j in range(4):
            wj = w[:, j]
            if not wj.any():
                continue
            bones = np.array([model.bone_lookup[bci + s] if s < bc and bci + s < len(model.bone_lookup) else 0 for s in slots[:, j]])
            M = world[bones]                                     # vc x 4 x 4
            tp = np.einsum("vij,vj->vi", M[:, :3, :3], p) + M[:, :3, 3]
            tn = np.einsum("vij,vj->vi", M[:, :3, :3], n)
            acc += tp * wj[:, None]
            nacc += tn * wj[:, None]
        posed[ks] = acc
        normals[ks] = nacc
    # to the screen
    hom = np.concatenate([posed, np.ones((N, 1))], axis=1) @ view.T
    z = -hom[:, 2]
    ok = z > 1e-3
    sx = np.where(ok, (hom[:, 0] * f / aspect) / np.maximum(z, 1e-3), 0) * 0.5 + 0.5
    sy = np.where(ok, (hom[:, 1] * f) / np.maximum(z, 1e-3), 0) * 0.5 + 0.5
    px = sx * W
    py = (1 - sy) * H
    nl = normals / np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-6)
    shade = 0.45 + 0.55 * np.clip(nl @ light_dir, 0, 1)
    uv = model.uv[skin.vertices]
    drawn = 0
    def blend_of(b):
        return model.materials[b[6]][1] if b[6] < len(model.materials) else 0
    for b in sorted(skin.batches, key=lambda b: (blend_of(b) >= 2, b[1])):
        sec = skin.sections[b[3]]
        sid, level, vs, vc, is_, ic = sec[:6]
        if sid not in shown:
            continue
        mflags, blend = model.materials[b[6]] if b[6] < len(model.materials) else (0, 0)
        unlit = bool(mflags & 0x1)
        tex = model.textures[model.tex_lookup[b[9]]] if b[9] < len(model.tex_lookup) else (1, "")
        kind, name = tex
        if kind == 1:
            tx = texture
        elif kind == 6:
            tx = hair_tex
        elif kind == 2:
            continue                                             # cape: none at creation
        elif kind == 0:
            tx = read_blp(files, name)
        else:
            tx = None
        if tx is None:
            tx = np.full((4, 4, 4), 255, dtype=np.uint8)
        tx = np.asarray(tx)
        th, tw = tx.shape[:2]
        # The game reads the 16-bit start alone: the modern format's high word (level) is lost on
        # it, so a section placed past the first 65535 indices draws from the wrong triangles.
        first = is_
        tris = skin.indices[first:first + ic].reshape(-1, 3)
        for tri in tris:
            if not ok[tri].all():
                continue
            xs, ys = px[tri], py[tri]
            x0, x1 = int(max(0, math.floor(xs.min()))), int(min(W - 1, math.ceil(xs.max())))
            y0, y1 = int(max(0, math.floor(ys.min()))), int(min(H - 1, math.ceil(ys.max())))
            if x1 < x0 or y1 < y0:
                continue
            if (x1 - x0) * (y1 - y0) > W * H // 2:
                continue                                         # a triangle across the whole screen: broken
            gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            d = (xs[1] - xs[0]) * (ys[2] - ys[0]) - (xs[2] - xs[0]) * (ys[1] - ys[0])
            if abs(d) < 1e-9:
                continue
            l1 = ((gx - xs[0]) * (ys[2] - ys[0]) - (xs[2] - xs[0]) * (gy - ys[0])) / d
            l2 = ((xs[1] - xs[0]) * (gy - ys[0]) - (gx - xs[0]) * (ys[1] - ys[0])) / d
            l0 = 1 - l1 - l2
            inside = (l0 >= 0) & (l1 >= 0) & (l2 >= 0)
            if not inside.any():
                continue
            zz = l0 * z[tri[0]] + l1 * z[tri[1]] + l2 * z[tri[2]]
            sub = zbuf[y0:y1 + 1, x0:x1 + 1]
            hit = inside & (zz <= sub + 1e-4)
            if not hit.any():
                continue
            u = l0 * uv[tri[0], 0] + l1 * uv[tri[1], 0] + l2 * uv[tri[2], 0]
            v = l0 * uv[tri[0], 1] + l1 * uv[tri[1], 1] + l2 * uv[tri[2], 1]
            ti = np.clip((v % 1.0) * th, 0, th - 1).astype(int)
            tj = np.clip((u % 1.0) * tw, 0, tw - 1).astype(int)
            texel = tx[ti, tj]
            alpha = texel[:, :, 3].astype(np.float32) / 255.0
            if blend == 1:                                       # alpha key: the game's test
                hit &= texel[:, :, 3] >= 224
                if not hit.any():
                    continue
            sh = 1.0 if unlit else (l0 * shade[tri[0]] + l1 * shade[tri[1]] + l2 * shade[tri[2]])[:, :, None]
            color = texel[:, :, :3].astype(np.float32) * sh
            region = image[y0:y1 + 1, x0:x1 + 1]
            if blend in (0, 1):
                region[hit] = color[hit]
                sub[hit] = zz[hit]
            elif blend == 2:                                     # alpha blend (no depth written)
                a = alpha[:, :, None]
                region[hit] = (region * (1 - a) + color * a)[hit]
            elif blend == 3:                                     # additive
                region[hit] = np.minimum(255, region + color)[hit]
            elif blend == 4:                                     # additive by alpha
                region[hit] = np.minimum(255, region + color * alpha[:, :, None])[hit]
            else:                                                # modulate
                region[hit] = (region * color / 255.0 * (2 if blend == 6 else 1))[hit]
            drawn += 1
    return np.clip(image, 0, 255).astype(np.uint8), drawn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("files")
    ap.add_argument("dbc")
    ap.add_argument("out")
    ap.add_argument("--race", type=int, default=15)
    ap.add_argument("--sex", type=int, default=1)
    ap.add_argument("--skin", type=int, default=0)
    ap.add_argument("--face", type=int, default=0)
    ap.add_argument("--hair", type=int, default=0)
    ap.add_argument("--feature", type=int, default=0)
    ap.add_argument("--time", type=int, default=400, help="ms into the sequence")
    ap.add_argument("--sequence", type=int, default=0, help="sequence id (0: Stand)")
    ap.add_argument("--camera", type=int, default=1, help="the model's camera type: 1 full figure, 0 portrait")
    ap.add_argument("--eye", help="x,y,z: a camera of your own instead")
    ap.add_argument("--target", default="0,0,1")
    ap.add_argument("--fov", type=float, default=0.9)
    ap.add_argument("--size", default="480x720")
    a = ap.parse_args()
    W, H = (int(x) for x in a.size.lower().split("x"))
    model = Model(a.model)
    skin = Skin(os.path.join(model.folder, model.name + "00.skin"))
    seq = next((i for i, s in enumerate(model.seqs) if s[0] == a.sequence and s[1] == 0), 0)
    length = model.seqs[seq][2]
    t = a.time % max(1, length)
    world = model.bone_matrices(seq, t)
    texture, hair_tex = compose(a.files, a.dbc, a.race, a.sex, a.skin, a.face, a.hair)
    present = {s[0] for s in skin.sections}
    shown = visible_geosets(a.dbc, a.race, a.sex, a.hair, a.feature, present)
    if a.eye:
        eye = np.array([float(x) for x in a.eye.split(",")])
        target = np.array([float(x) for x in a.target.split(",")])
        camera = (a.fov, 0.1, 100.0, eye, target)
    else:
        camera = model.camera(a.camera, seq, t)
        if camera is None:
            raise SystemExit("the model has no camera of type %d" % a.camera)
    light = np.array([1.0, 0.6, 1.2])
    light /= np.linalg.norm(light)
    image, drawn = render(model, skin, texture, hair_tex, a.files, shown, world, camera, (W, H), light)
    Image.fromarray(image).save(a.out)
    print("%s: sequence %d at %d ms, %d geosets shown, %d triangles drawn, camera at %s -> %s" % (
        a.out, model.seqs[seq][0], t, len(shown), drawn, np.round(camera[3], 2).tolist(), np.round(camera[4], 2).tolist()))


if __name__ == "__main__":
    main()
