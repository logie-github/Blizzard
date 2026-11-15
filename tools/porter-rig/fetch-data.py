#!/usr/bin/env python3
"""Fetches only the parts of the world server's data zip the porter rig needs.

The server data (realm/warcraft/server-data.env) is one 1.2 GB zip of dbc, Cameras, maps, vmaps and
mmaps. The rig's world server runs with vmaps and mmaps off, so only the first three are wanted:
this reads the zip's directory with HTTP range requests, downloads the byte ranges those members
occupy (members of one folder sit together, so that is a few large requests), and unpacks them.

    fetch-data.py URL DEST [FOLDER ...]      (folders default to: dbc Cameras maps)

Nothing but the standard library. The download goes through HTTPS_PROXY if the machine has one.
"""
import os
import struct
import sys
import urllib.request
import zlib

CHUNK = 8 << 20


def fetch(url, start, end):
    """Bytes [start, end) of the file at [url]."""
    for attempt in range(5):
        try:
            request = urllib.request.Request(url, headers={"Range": f"bytes={start}-{end - 1}", "User-Agent": "porter-rig"})
            with urllib.request.urlopen(request, timeout=120) as response:
                if response.status != 206:
                    raise RuntimeError(f"the server ignored the range request (status {response.status})")
                data = response.read()
            if len(data) != end - start:
                raise RuntimeError(f"short read: {len(data)} of {end - start}")
            return data
        except Exception as error:  # noqa: BLE001 (any network fault is retried)
            if attempt == 4:
                raise
            print(f"  retrying {start}-{end}: {error}", file=sys.stderr)


def size_of(url):
    request = urllib.request.Request(url, headers={"Range": "bytes=0-0", "User-Agent": "porter-rig"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return int(response.headers["Content-Range"].rsplit("/", 1)[1])


def directory(url, total):
    """The zip's members: (name, method, compressed size, size, crc, local header offset)."""
    tail_size = min(total, 1 << 16)
    tail = fetch(url, total - tail_size, total)
    at = tail.rfind(b"PK\x05\x06")
    if at < 0:
        raise RuntimeError("no zip end record")
    count, cd_size, cd_offset = struct.unpack_from("<HII", tail, at + 10)
    if cd_offset == 0xFFFFFFFF or count == 0xFFFF:
        locator = tail.rfind(b"PK\x06\x07")
        end64 = struct.unpack_from("<Q", tail, locator + 8)[0]
        record = fetch(url, end64, end64 + 56)
        count, cd_size, cd_offset = struct.unpack_from("<Q", record, 32)[0], *struct.unpack_from("<QQ", record, 40)
    cd = fetch(url, cd_offset, cd_offset + cd_size)
    members, pos = [], 0
    for _ in range(count):
        if cd[pos:pos + 4] != b"PK\x01\x02":
            raise RuntimeError("bad directory entry")
        method, = struct.unpack_from("<H", cd, pos + 10)
        crc, csize, usize, name_len, extra_len, comment_len = struct.unpack_from("<IIIHHH", cd, pos + 16)
        offset, = struct.unpack_from("<I", cd, pos + 42)
        name = cd[pos + 46:pos + 46 + name_len].decode("utf-8", "replace")
        extra = cd[pos + 46 + name_len:pos + 46 + name_len + extra_len]
        # Zip64 sizes and offsets, when the 32-bit fields are full.
        e = 0
        while e + 4 <= len(extra):
            tag, length = struct.unpack_from("<HH", extra, e)
            if tag == 1:
                values = extra[e + 4:e + 4 + length]
                v = 0
                if usize == 0xFFFFFFFF:
                    usize, = struct.unpack_from("<Q", values, v); v += 8
                if csize == 0xFFFFFFFF:
                    csize, = struct.unpack_from("<Q", values, v); v += 8
                if offset == 0xFFFFFFFF:
                    offset, = struct.unpack_from("<Q", values, v); v += 8
            e += 4 + length
        members.append((name, method, csize, usize, crc, offset))
        pos += 46 + name_len + extra_len + comment_len
    return members


def main():
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    url, dest = sys.argv[1], sys.argv[2]
    folders = sys.argv[3:] or ["dbc", "Cameras", "maps"]
    total = size_of(url)
    members = directory(url, total)
    print(f"{len(members)} members in a zip of {total} bytes")
    for folder in folders:
        wanted = [m for m in members if m[0].startswith(folder + "/") and not m[0].endswith("/")]
        if not wanted:
            print(f"{folder}: nothing in the zip", file=sys.stderr)
            continue
        if os.path.isfile(os.path.join(dest, folder, ".complete")):
            print(f"{folder}: already here")
            continue
        # Each member is a local header (30 bytes + name + extra, at most a few hundred) and its data.
        start = min(m[5] for m in wanted)
        end = min(total, max(m[5] + 30 + 1024 + m[2] for m in wanted))
        print(f"{folder}: {len(wanted)} files, bytes {start}-{end} ({(end - start) >> 20} MB)")
        blob = bytearray()
        at = start
        while at < end:
            piece = fetch(url, at, min(end, at + CHUNK))
            blob += piece
            at += len(piece)
            print(f"  {(at - start) >> 20} MB", end="\r", flush=True)
        print()
        for name, method, csize, usize, crc, offset in wanted:
            local = offset - start
            if blob[local:local + 4] != b"PK\x03\x04":
                raise RuntimeError(f"{name}: no local header")
            name_len, extra_len = struct.unpack_from("<HH", blob, local + 26)
            data = bytes(blob[local + 30 + name_len + extra_len:local + 30 + name_len + extra_len + csize])
            if method == 8:
                data = zlib.decompress(data, -15)
            elif method != 0:
                raise RuntimeError(f"{name}: compression method {method}")
            if len(data) != usize or (zlib.crc32(data) & 0xFFFFFFFF) != crc:
                raise RuntimeError(f"{name}: damaged")
            # (a member's name is used as a path only below the destination)
            path = os.path.normpath(os.path.join(dest, name))
            if not path.startswith(os.path.normpath(dest) + os.sep):
                raise RuntimeError(f"{name}: outside the destination")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as out:
                out.write(data)
        open(os.path.join(dest, folder, ".complete"), "w").close()
        del blob
    print("done")


if __name__ == "__main__":
    main()
