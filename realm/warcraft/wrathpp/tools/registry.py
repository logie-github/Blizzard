#!/usr/bin/env python3
"""Wrath++ customization registry: checks registry/registry.json and writes the canonical binary the
world server loads and sends to clients (SMSG_WRATHPP_REGISTRY), byte for byte what
protocol/wrathpp_appearance.h's WriteRegistry writes, and its FNV-1a hash.

    python3 tools/registry.py check  [REGISTRY_JSON]
    python3 tools/registry.py build  REGISTRY_JSON OUT_BIN      (prints version and hash)
    python3 tools/registry.py dump   REGISTRY_BIN               (decodes a binary, as JSON)

Rules (the same as CheckRegistry): category and option ids unique and > 0 for categories, the
default an option of the category, every category with options and eligibility, geoset values 0..99,
names at most 48 bytes, kinds geoset / texture_layer / attachment.
"""
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(os.path.dirname(HERE), "registry", "registry.json")
KINDS = {"geoset": 1, "texture_layer": 2, "attachment": 3}
SEXES = {"male": 1, "female": 2}
MAX_NAME = 48


class RegistryError(Exception):
    pass


def class_mask(names_or_ids, classes):
    mask = 0
    for c in names_or_ids:
        cid = classes[c] if isinstance(c, str) else int(c)
        if not 1 <= cid <= 32:
            raise RegistryError(f"class {c!r} out of range")
        mask |= 1 << (cid - 1)
    return mask


def normalize(doc):
    """The registry as the binary holds it: categories and options sorted by id."""
    if doc.get("schema") != 1:
        raise RegistryError("schema must be 1")
    version = int(doc["version"])
    if not 1 <= version <= 0xFFFF:
        raise RegistryError("version out of range")
    classes = doc.get("classes", {})
    cats = []
    seen = set()
    for c in doc["categories"]:
        cid = int(c["id"])
        if not 1 <= cid <= 0xFFFF or cid in seen:
            raise RegistryError(f"category id {cid} zero, out of range or repeated")
        seen.add(cid)
        if c["kind"] not in KINDS:
            raise RegistryError(f"category {cid}: kind {c['kind']!r}")
        name = c["name"].encode("utf-8")
        if len(name) > MAX_NAME:
            raise RegistryError(f"category {cid}: name over {MAX_NAME} bytes")
        elig = []
        for e in c["eligibility"]:
            sexmask = 0
            for s in e["sexes"]:
                sexmask |= SEXES[s]
            race = int(e["race"])
            if not 1 <= race <= 255 or not sexmask:
                raise RegistryError(f"category {cid}: eligibility {e}")
            elig.append((race, sexmask, class_mask(e.get("classes", []), classes)))
        if not elig:
            raise RegistryError(f"category {cid}: no eligibility")
        opts = []
        oseen = set()
        for o in c["options"]:
            oid = int(o["id"])
            if not 0 <= oid <= 0xFFFF or oid in oseen:
                raise RegistryError(f"category {cid}: option id {oid} repeated or out of range")
            oseen.add(oid)
            value = int(o["value"])
            if c["kind"] == "geoset" and not 0 <= value <= 99:
                raise RegistryError(f"category {cid} option {oid}: geoset value {value} not 0..99")
            oname = o["name"].encode("utf-8")
            if len(oname) > MAX_NAME:
                raise RegistryError(f"category {cid} option {oid}: name over {MAX_NAME} bytes")
            opts.append((oid, value, class_mask(o.get("classes", []), classes), oname))
        if not opts:
            raise RegistryError(f"category {cid}: no options")
        if int(c["default"]) not in oseen:
            raise RegistryError(f"category {cid}: default {c['default']} isn't one of its options")
        group = int(c.get("geoset_group", 0))
        if c["kind"] == "geoset" and not 1 <= group <= 99:
            raise RegistryError(f"category {cid}: geoset_group {group}")
        cats.append((cid, KINDS[c["kind"]], group, int(c["default"]), name, elig, sorted(opts)))
    return version, sorted(cats, key=lambda c: c[0])


def encode(version, cats):
    out = bytearray(struct.pack("<HH", version, len(cats)))
    for cid, kind, group, default, name, elig, opts in cats:
        out += struct.pack("<HBHH", cid, kind, group, default)
        out += bytes([len(name)]) + name
        out += struct.pack("<H", len(elig))
        for race, sexmask, cmask in elig:
            out += struct.pack("<BBI", race, sexmask, cmask)
        out += struct.pack("<H", len(opts))
        for oid, value, cmask, oname in opts:
            out += struct.pack("<HHI", oid, value, cmask) + bytes([len(oname)]) + oname
    return bytes(out)


def fnv1a(data):
    h = 2166136261
    for b in data:
        h = ((h ^ b) * 16777619) & 0xFFFFFFFF
    return h


def decode(data):
    pos = 0

    def take(fmt):
        nonlocal pos
        vals = struct.unpack_from(fmt, data, pos)
        pos += struct.calcsize(fmt)
        return vals

    def text():
        nonlocal pos
        n = data[pos]
        s = data[pos + 1:pos + 1 + n]
        pos += 1 + n
        return s.decode("utf-8")

    version, nc = take("<HH")
    cats = []
    for _ in range(nc):
        cid, kind, group, default = take("<HBHH")
        name = text()
        (ne,) = take("<H")
        elig = [dict(zip(("race", "sexmask", "classmask"), take("<BBI"))) for _ in range(ne)]
        (no,) = take("<H")
        opts = []
        for _ in range(no):
            oid, value, cmask = take("<HHI")
            opts.append({"id": oid, "value": value, "classmask": cmask, "name": text()})
        cats.append({"id": cid, "kind": kind, "geoset_group": group, "default": default, "name": name,
                     "eligibility": elig, "options": opts})
    if pos != len(data):
        raise RegistryError("trailing bytes")
    return {"version": version, "categories": cats}


def build(path):
    with open(path, encoding="utf-8") as f:
        version, cats = normalize(json.load(f))
    blob = encode(version, cats)
    return version, blob, fnv1a(blob)


def main(argv):
    if len(argv) < 2 or argv[1] not in ("check", "build", "dump"):
        print(__doc__, file=sys.stderr)
        return 2
    try:
        if argv[1] == "dump":
            with open(argv[2], "rb") as f:
                print(json.dumps(decode(f.read()), indent=2))
            return 0
        path = argv[2] if len(argv) > 2 else DEFAULT
        version, blob, digest = build(path)
        if argv[1] == "build":
            out = argv[3]
            with open(out + ".new", "wb") as f:
                f.write(blob)
            os.replace(out + ".new", out)
        print(f"registry version {version} hash 0x{digest:08x} ({len(blob)} bytes)")
        return 0
    except (RegistryError, KeyError, ValueError) as e:
        print(f"registry: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
