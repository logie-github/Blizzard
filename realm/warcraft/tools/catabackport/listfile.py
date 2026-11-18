"""The community listfile (`<fdid>;<path>`, the union of every build's names): loaded whole or only under some prefixes."""
import re

TILE = re.compile(r"^world/maps/([^/]+)/\1_(\d+)_(\d+)\.adt$")


def load(path, prefixes=None):
    """({fdid: path}, {path: fdid}), paths lower case; with prefixes only the paths that start with one of them."""
    by_id, by_path = {}, {}
    prefixes = tuple(prefixes) if prefixes else None
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            i, sep, p = line.rstrip("\r\n").partition(";")
            if not sep or not i.isdigit():
                continue
            p = p.lower()
            if prefixes and not p.startswith(prefixes):
                continue
            by_id[int(i)] = p
            by_path[p] = int(i)
    return by_id, by_path


def tiles_by_dir(by_path):
    """{directory: sorted [(x, y)]}: the root tiles the listfile names (an upper bound for any one build)."""
    out = {}
    for p in by_path:
        m = TILE.match(p)
        if m:
            out.setdefault(m.group(1), set()).add((int(m.group(2)), int(m.group(3))))
    return {d: sorted(t) for d, t in out.items()}
