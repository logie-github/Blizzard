"""Small shared helpers: atomic files, hashes, JSON, deterministic archives, the pins."""
import hashlib
import io
import json
import os
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))


def pins(path=None):
    return json.load(open(path or os.path.join(HERE, "pins.json"), encoding="utf-8"))


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_atomic(path, data):
    """Write bytes or text so that a reader (or a rerun) never sees half a file."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".part"
    with open(tmp, "wb") as f:
        f.write(data if isinstance(data, bytes) else data.encode("utf-8"))
    os.replace(tmp, path)


def dump_json(path, obj):
    write_atomic(path, json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False) + "\n")


def load_json(path, default=None):
    try:
        return json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return default


def input_hash(*parts):
    """A stable hash of JSON-able parts: what a map's pack was made from (skip_done compares it)."""
    return sha256_bytes(json.dumps(parts, sort_keys=True, separators=(",", ":")).encode())[:16]


def det_tar(src_dir, dest, epoch, mode="xz"):
    """A tar of src_dir's files, byte for byte the same for the same content: sorted names, fixed owner, mode and time."""
    names = []
    for root, _, files in os.walk(src_dir):
        for f in files:
            names.append(os.path.relpath(os.path.join(root, f), src_dir))
    names.sort()
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        for rel in names:
            full = os.path.join(src_dir, rel)
            info = tarfile.TarInfo(rel.replace(os.sep, "/"))
            info.size = os.path.getsize(full)
            info.mtime = epoch
            info.mode = 0o644
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            with open(full, "rb") as f:
                tar.addfile(info, f)
    raw = buf.getvalue()
    if mode == "xz":
        import lzma
        raw = lzma.compress(raw, preset=6, check=lzma.CHECK_CRC64)
    write_atomic(dest, raw)
    return len(names)
