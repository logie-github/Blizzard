"""A format 1 body shapes zip (pack.py) made again for looks that changed only in where some vertices are (the hair
lifted out of the head by decimate.sink_lifts): usage

  rebase.py SHAPES_V1.zip OLD_LOOKS_CLIENT_DIR NEW_LOOKS_CLIENT_DIR OUT.zip

Each shape's vertex block is the looks' vertex array with the shape's changes (the chest and seat, and what moves with
them) and the vertices the refinement added at its end. A vertex the shape left as the old looks had it takes the new
looks' record where that differs; one the shape changed is left as it is. The looks' model and skin have to be the same
in everything but those records (the vertex counts and the skin's bytes are checked), and the manifest's looks_sha256
becomes the new looks' model's, which is what pack2.py and the app check."""
import hashlib
import json
import os
import struct
import sys
import zipfile


def sha(b):
    return hashlib.sha256(b).hexdigest()


def struct_sha(m2b):
    n, o = struct.unpack_from("<II", m2b, 60)
    if n == 0 or o < 68 or o + n * 48 > len(m2b):
        return sha(m2b)
    b = bytearray(m2b)
    for i in range(n):
        b[o + i * 48:o + i * 48 + 12] = bytes(12)
    return sha(bytes(b))


def vertices(m2b):
    n, o = struct.unpack_from("<II", m2b, 60)
    return [m2b[o + i * 48:o + (i + 1) * 48] for i in range(n)]


def rebase(v1, old_dir, new_dir, out):
    src = zipfile.ZipFile(v1)
    man = json.loads(src.read("wrathpp-body.json"))
    done = {}
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for entry in man["models"]:
            rel = entry["model"]
            old = open(os.path.join(old_dir, rel), "rb").read()
            new = open(os.path.join(new_dir, rel), "rb").read()
            if sha(old) != entry["looks_sha256"] and struct_sha(old) != entry.get("looks_struct_sha256"):
                raise SystemExit("%s: the shapes were not made for the old looks given" % rel)
            skin_rel = entry["skin"]
            if open(os.path.join(old_dir, skin_rel), "rb").read() != open(os.path.join(new_dir, skin_rel), "rb").read():
                raise SystemExit("%s: the skin differs between the looks: not a change of positions" % skin_rel)
            ov, nv = vertices(old), vertices(new)
            if len(ov) != len(nv):
                raise SystemExit("%s: %d vertices before, %d after" % (rel, len(ov), len(nv)))
            moved = {i for i in range(len(ov)) if ov[i] != nv[i]}
            if any(ov[i][12:] != nv[i][12:] for i in moved):
                raise SystemExit("%s: more than positions changed" % rel)
            entry["looks_sha256"] = sha(new)
            entry["looks_struct_sha256"] = struct_sha(new)
            for preset, block in entry["blocks"].items():
                data = bytearray(src.read(block["file"]))
                taken = 0
                for i in moved:
                    if bytes(data[i * 48:(i + 1) * 48]) == ov[i]:
                        data[i * 48:(i + 1) * 48] = nv[i]
                        taken += 1
                block["sha256"] = sha(bytes(data))
                block["size"] = len(data)
                done[block["file"]] = bytes(data)
                print("%s %s: %d of %d moved vertices taken (%d left as the shape has them)" % (rel, preset, taken, len(moved), len(moved) - taken))
        for info in src.infolist():
            if info.filename == "wrathpp-body.json":
                continue
            z.writestr(info.filename, done.get(info.filename, src.read(info.filename)))
        z.writestr("wrathpp-body.json", json.dumps(man, indent=1))


if __name__ == "__main__":
    rebase(*sys.argv[1:5])
