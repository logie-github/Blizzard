"""The game's files the starting areas need, by Cataclysm Classic's file ids: their maps' own (the
terrain, its minimap pictures), and everything the maps place (models, buildings) with everything those
use (skins, animations, textures, a building's parts and the models inside it), read from the files
themselves (fetched at common.BUILD).
"""
import concurrent.futures
import re
import struct

import common


def chunks(data, start=0):
    i = start
    while i + 8 <= len(data):
        magic = data[i:i + 4]
        size = struct.unpack_from("<I", data, i + 4)[0]
        yield magic, data[i + 8:i + 8 + size]
        i += 8 + size


def ints(body):
    return list(struct.unpack(f"<{len(body) // 4}I", body[:len(body) // 4 * 4]))


def names(body):
    return [n.decode("latin-1").replace("\\", "/").lower() for n in body.split(b"\0") if n]


def plain_twins(ids, by_id, by_path):
    """The plain diffuse texture beside each terrain texture named by its specular variant
    (<name>_s.blp, the diffuse with a specular mask in its alpha, which Cataclysm's tiles name):
    3.3.5a's tiles name the plain one (the converter names it when it's there), and a tile naming
    the _s file draws its ground flat green."""
    out = set()
    for i in ids:
        path = by_id.get(i, "")
        if path.startswith("tileset/") and path.endswith("_s.blp"):
            twin = by_path.get(path[:-len("_s.blp")] + ".blp")
            if twin:
                out.add(twin)
    return out


def adt_refs(data, by_path):
    """The file ids an ADT (root, _obj or _tex) names: its models, buildings and textures."""
    found = set()
    mmdx = mwmo = []
    mddf = modf = b""
    for magic, body in chunks(data):
        m = magic[::-1]
        if m == b"MMDX":
            mmdx = names(body)
        elif m == b"MWMO":
            mwmo = names(body)
        elif m == b"MTEX":
            found.update(by_path[n] for n in names(body) if n in by_path)
        elif m in (b"MDID", b"MHID"):
            found.update(i for i in ints(body) if i)
        elif m == b"MDDF":
            mddf = body
        elif m == b"MODF":
            modf = body
    for k in range(0, len(mddf) - 35, 36):
        name_id, _, _, _, _, _, _, _, _, flags = struct.unpack_from("<II3f3fHH", mddf, k)
        if flags & 0x40:
            found.add(name_id)
        elif name_id < len(mmdx) and mmdx[name_id] in by_path:
            found.add(by_path[mmdx[name_id]])
    for k in range(0, len(modf) - 63, 64):
        name_id = struct.unpack_from("<I", modf, k)[0]
        flags = struct.unpack_from("<H", modf, k + 56)[0]
        if flags & 0x8:
            found.add(name_id)
        elif name_id < len(mwmo) and mwmo[name_id] in by_path:
            found.add(by_path[mwmo[name_id]])
    return found


def model_refs(path, data, by_path):
    """What a model or a building uses (by file id)."""
    found = set()
    if path.endswith(".m2") and data[:4] == b"MD21":
        for magic, body in chunks(data):
            if magic in (b"SFID", b"TXID", b"BFID", b"SKID", b"PFID"):
                found.update(ints(body))
            elif magic == b"AFID":
                found.update(struct.unpack_from("<I", body, k + 4)[0] for k in range(0, len(body) - 7, 8))
    elif path.endswith(".wmo") and data[:4] == b"REVM":
        for magic, body in chunks(data):
            m = magic[::-1]
            if m == b"GFID":
                found.update(ints(body))
            elif m == b"MODI":
                found.update(ints(body))
            elif m == b"MOMT":
                for k in range(0, len(body) - 63, 64):
                    found.update(struct.unpack_from("<I", body, k + o)[0] for o in (12, 24, 36))
            elif m == b"MOTX":
                found.update(by_path[n] for n in names(body) if n in by_path)
            elif m == b"MODN":
                found.update(by_path[re.sub(r"\.(mdx|mdl)$", ".m2", n)] for n in names(body)
                             if re.sub(r"\.(mdx|mdl)$", ".m2", n) in by_path)
    return {i for i in found if i}


def wmo_id(data):
    """A building's WMO id (its MOHD's), which WMOAreaTable names its areas by."""
    for magic, body in chunks(data):
        if magic[::-1] == b"MOHD":
            return struct.unpack_from("<I", body, 32)[0]
    return None


def map_files(by_id):
    """The maps' own files: everything in their folders, and their minimap pictures."""
    out = {}
    for directory in common.MAPS.values():
        prefix = f"world/maps/{directory.lower()}/"
        minimap = f"world/minimaps/{directory.lower()}/"
        for fdid, path in by_id.items():
            if path.startswith(prefix):
                # (not the server-side and later-game files 3.3.5a never reads: navigation meshes,
                # Legion's second texture tiles and level-of-detail tiles, the liquids' sidecars)
                if not re.search(r"(\.pm4|\.h2o|_tex1\.adt|_lod\.adt|_obj1\.adt)$", path):
                    out[fdid] = (path, "map")
            elif path.startswith(minimap) and re.match(r"map\d+_\d+\.blp$", path[len(minimap):]):
                out[fdid] = (path, "minimap")
    return out


def closure(cache, by_id, by_path, start, jobs=8):
    """[start] (file id: (path, kind)) with every file they use, fetched; and the buildings' WMO ids
    (each its file's id)."""
    files = dict(start)
    wmo_ids = {}
    todo = list(files)
    seen = set(todo)
    missing = []
    with concurrent.futures.ThreadPoolExecutor(jobs) as pool:
        while todo:
            batch, todo = todo, []
            for fdid, data in zip(batch, pool.map(lambda f: common.file_bytes(cache, f), batch)):
                path, kind = files[fdid]
                if not data:
                    missing.append(path)
                    continue
                if path.endswith(".adt"):
                    refs = adt_refs(data, by_path)
                    refs |= plain_twins(refs, by_id, by_path)
                elif path.endswith((".m2", ".wmo")):
                    refs = model_refs(path, data, by_path)
                    if path.endswith(".wmo") and not re.search(r"_\d{3}\.wmo$", path):
                        w = wmo_id(data)
                        if w:
                            wmo_ids[w] = fdid
                else:
                    refs = set()
                for r in refs:
                    if r in seen or r not in by_id:
                        continue
                    seen.add(r)
                    files[r] = (by_id[r], "model" if by_id[r].endswith((".m2", ".wmo", ".skin", ".anim", ".skel", ".bone", ".phys"))
                                else "texture")
                    todo.append(r)
    return files, wmo_ids, missing
