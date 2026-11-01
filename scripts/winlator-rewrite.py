#!/usr/bin/env python3
"""Rewrites the install path compiled into Winlator's runtime, for the World of Warcraft app.

    winlator-rewrite.py OLD NEW FILE.tzst...

Each zstd-compressed tar (Winlator's rootfs and the components it unpacks: Box64, graphics
drivers, DXVK, PulseAudio...) is rewritten in place: every OLD in its files' contents and in its
links' targets becomes NEW. OLD and NEW must be the same length, so programs keep their layout
(strings, ELF headers). Prints how many places changed in each.
"""
import io
import sys
import tarfile

import zstandard


def rewrite(path, old, new):
    with open(path, "rb") as f:
        raw = zstandard.ZstdDecompressor().stream_reader(f).read()
    src = tarfile.open(fileobj=io.BytesIO(raw), mode="r:")
    out = io.BytesIO()
    dst = tarfile.open(fileobj=out, mode="w:", format=tarfile.GNU_FORMAT)
    changed = 0
    for member in src.getmembers():
        data = None
        if member.isfile():
            data = src.extractfile(member).read()
            count = data.count(old)
            if count:
                data = data.replace(old, new)
                changed += count
        if member.issym() or member.islnk():
            target = member.linkname.encode()
            if old in target:
                member.linkname = target.replace(old, new).decode()
                changed += 1
        dst.addfile(member, io.BytesIO(data) if data is not None else None)
    dst.close()
    compressed = zstandard.ZstdCompressor(level=19, threads=-1).compress(out.getvalue())
    with open(path, "wb") as f:
        f.write(compressed)
    return changed


def main():
    if len(sys.argv) < 4:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    old, new = sys.argv[1].encode(), sys.argv[2].encode()
    if len(old) != len(new):
        sys.exit(f"{sys.argv[1]} and {sys.argv[2]} aren't the same length")
    total = 0
    for path in sys.argv[3:]:
        changed = rewrite(path, old, new)
        total += changed
        print(f"{changed:6d}  {path}")
    print(f"{total:6d}  in all")


if __name__ == "__main__":
    main()
