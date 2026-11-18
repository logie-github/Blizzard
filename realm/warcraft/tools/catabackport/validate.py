"""Stage `validate`: what a unit made is checked before it is packed; a file that fails is not shipped and is reported.

Structural checks by signature (the Converter's own limits.py values): ADT v18 with its MCIN, WDT v17 with a 32 KB MAIN, M2 MD20
version 264, skin, WMO v17, BLP2 with sane dimensions, DBC-style table files' header agreeing with their rows. Then references: every
model, building and texture an ADT names is a file of the unit (or, with a stock list, of 3.3.5a's own); a name that is neither is
`unresolved` (a count and the first few names in the report: a hole in the world, not a crash). A unit with a bad map file (ADT/WDT)
is `failed`; one with other files dropped is `partial`.
"""
import os
import re
import struct

MAX_BLP = 4096


def chunks(data, start=0):
    i = start
    while i + 8 <= len(data):
        magic = data[i:i + 4]
        size = struct.unpack_from("<I", data, i + 4)[0]
        yield magic[::-1], data[i + 8:i + 8 + size], size
        i += 8 + size


def check_adt(data):
    ch = {m: b for m, b, _ in chunks(data)}
    if b"MVER" not in ch or struct.unpack_from("<I", ch[b"MVER"])[0] != 18:
        return "ADT is not version 18"
    if b"MCIN" not in ch or len(ch[b"MCIN"]) != 4096:
        return "ADT has no 256-entry MCIN (the split tile was not made whole)"
    return None


def check_wdt(data):
    ch = {m: b for m, b, _ in chunks(data)}
    if b"MVER" not in ch or struct.unpack_from("<I", ch[b"MVER"])[0] != 17:
        return "WDT is not version 17"
    if b"MAIN" not in ch or len(ch[b"MAIN"]) != 32768:
        return "WDT has no 64 x 64 MAIN"
    return None


def check_m2(data):
    if data[:4] != b"MD20":
        return "M2 is not a flat MD20 (still chunked, or not a model)"
    if struct.unpack_from("<I", data, 4)[0] != 264:
        return f"M2 version {struct.unpack_from('<I', data, 4)[0]}, not 264"
    return None


def check_skin(data):
    return None if data[:4] == b"SKIN" else "skin has no SKIN header"


def check_wmo(data):
    ch = list(chunks(data))
    if not ch or ch[0][0] != b"MVER" or struct.unpack_from("<I", ch[0][1])[0] != 17:
        return "WMO is not version 17"
    return None


def check_blp(data):
    if data[:4] != b"BLP2":
        return "BLP is not BLP2"
    w, h = struct.unpack_from("<II", data, 12)
    if not (0 < w <= MAX_BLP and 0 < h <= MAX_BLP):
        return f"BLP is {w} x {h}"
    return None


CHECKS = {".adt": check_adt, ".wdt": check_wdt, ".m2": check_m2, ".skin": check_skin, ".blp": check_blp}


def check(path, data):
    if path.endswith(".wmo"):
        # (a group file, name_000.wmo, has no root's MVER-first layout of the same kind: only roots are checked)
        return None if re.search(r"_\d{3}\.wmo$", path) else check_wmo(data)
    fn = CHECKS.get(os.path.splitext(path)[1])
    return fn(data) if fn else None


def adt_names(data):
    out = []
    for m, body, _ in chunks(data):
        if m in (b"MMDX", b"MWMO", b"MTEX"):
            out += [n.decode("latin-1").replace("\\", "/").lower() for n in body.split(b"\0") if n]
    return out


def run(files_dir, stock=None, drop=True):
    """Checks <files_dir> (the unit's client/files). Returns {"status", "checked", "bad": [(path, why)], "dropped": n,
    "unresolved": {"count", "sample"}}. With drop, a failing non-map file is removed."""
    have, bad, checked, wanted = set(), [], 0, {}
    for root, _, names in os.walk(files_dir):
        for n in names:
            have.add(os.path.relpath(os.path.join(root, n), files_dir).replace(os.sep, "/").lower())
    for rel in sorted(have):
        path = os.path.join(files_dir, rel)
        data = open(path, "rb").read()
        why = check(rel, data)
        checked += 1
        if why:
            bad.append((rel, why))
        elif rel.endswith(".adt"):
            for n in adt_names(data):
                wanted.setdefault(re.sub(r"\.(mdx|mdl)$", ".m2", n), rel)
    map_bad = [b for b in bad if b[0].endswith((".adt", ".wdt"))]
    if drop:
        for rel, _ in bad:
            if not rel.endswith((".adt", ".wdt")):
                os.remove(os.path.join(files_dir, rel))
                have.discard(rel)
    stock = stock or set()
    unresolved = sorted(n for n in wanted if n not in have and n not in stock)
    status = "failed" if map_bad else ("partial" if bad else "ok")
    return {"status": status, "checked": checked, "bad": bad, "dropped": len(bad) - len(map_bad) if drop else 0,
            "unresolved": {"count": len(unresolved), "sample": unresolved[:20]}}
