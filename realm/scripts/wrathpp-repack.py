#!/usr/bin/env python3
"""Splits Wrath++'s server package into packs the app installs in parallel (docs/wrathpp, format 2).

Input: the package as the realm scripts make it (wrathpp-server.tar.xz: one tar.xz, every entry under server/).
Output (in --out): one wrathpp-server-<pack>.tar.xz per pack (entries named exactly as in the input, so any pack
unpacks on its own into the same server/ folder) and wrathpp-server.json: the format-1 fields (size, sha256, unpacked:
the whole package, which apps that only know format 1 still download) plus "packs".

Packs, by what a path is:
  core         the programs of this realm alone (world and login server, the extractors, ctl.sh, configs, Lua, the
               Wrath++ module): what no other realm's server package has
  runtime      MariaDB's programs, the libraries it and the servers run on, its seed database (shareable)
  sql          AzerothCore's base and update SQL, the biggest text in the package (shareable, immutable)
  modules-sql  the modules' SQL (playerbots', the others') (shareable, immutable)
  modules-data the modules' other server data (shareable, immutable)
  payload-<m>  a module's client files (data/files): the models, textures and sounds its patch for the game is made
               of. Optional: only a game that puts the module's patch in its Data needs them, and Wrath++'s does not
               (its package has no share/client), so an install without them plays the same.

Shareable packs list every file with its size and SHA-256: an install that finds the same files in the Wrath+ server
folder takes them from there instead of downloading. Nothing here compiles anything; run it on a finished package.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tarfile

MODULE = re.compile(r"^src/modules/([^/]+)/(.*)$")
CORE_MODULES = {"mod-wrathpp-customization"}
SHAREABLE = {"runtime", "sql", "modules-sql", "modules-data"}
IMMUTABLE = {"sql", "modules-sql", "modules-data"}


def pack_of(rel):
    """The pack a path (relative to server/, no trailing slash) belongs to."""
    m = MODULE.match(rel)
    if m:
        module, inner = m.group(1), m.group(2)
        if module in CORE_MODULES:
            return "core"
        if inner == "data/files" or inner.startswith("data/files/"):
            return "payload-" + module
        if "sql" in inner.split("/"):
            return "modules-sql"
        return "modules-data"
    if rel == "src/data/sql" or rel.startswith("src/data/sql/"):
        return "sql"
    if rel.startswith(("lib/", "share/", "mariadb-seed")) or rel in ("lib", "share"):
        return "runtime"
    if rel.startswith("bin/mariadb"):
        return "runtime"
    return "core"


class Hashing:
    """A file object that hashes what is read from it."""

    def __init__(self, f):
        self.f, self.digest = f, hashlib.sha256()

    def read(self, n=-1):
        data = self.f.read(n)
        self.digest.update(data)
        return data


class Pack:
    def __init__(self, name, out, level):
        self.name = name
        self.path = os.path.join(out, "wrathpp-server-%s.tar.xz" % name)
        self.file = open(self.path, "wb")
        self.xz = subprocess.Popen(["xz", "-T0", "-%d" % level, "-c"], stdin=subprocess.PIPE, stdout=self.file)
        self.tar = tarfile.open(fileobj=self.xz.stdin, mode="w|", format=tarfile.PAX_FORMAT)
        self.files = []
        self.dirs = []
        self.unpacked = 0

    def close(self):
        self.tar.close()
        self.xz.stdin.close()
        if self.xz.wait() != 0:
            raise SystemExit("xz failed for pack " + self.name)
        self.file.close()


def sha256_file(path):
    d = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            d.update(block)
    return d.hexdigest()


def repack(source, out, level, commit, protocol):
    os.makedirs(out, exist_ok=True)
    packs = {}
    with tarfile.open(source, "r|xz") as tar:
        for member in tar:
            name = member.name[2:] if member.name.startswith("./") else member.name
            if not name.startswith("server/") and name != "server":
                raise SystemExit("entry outside server/: " + name)
            if member.issym() or member.islnk():
                raise SystemExit("links are not handled (none in the package): " + name)
            rel = name[len("server/"):].rstrip("/") if name != "server" else ""
            pack_name = "core" if rel == "" else pack_of(rel)
            pack = packs.get(pack_name)
            if pack is None:
                pack = packs[pack_name] = Pack(pack_name, out, level)
            if member.isdir():
                pack.tar.addfile(member)
                if rel:
                    pack.dirs.append(rel)
                continue
            if not member.isfile():
                raise SystemExit("unexpected entry type: " + name)
            hashed = Hashing(tar.extractfile(member))
            pack.tar.addfile(member, hashed)
            pack.unpacked += member.size
            pack.files.append({"path": rel, "size": member.size, "sha256": hashed.digest.hexdigest(), "mode": member.mode & 0o777})
    for pack in packs.values():
        pack.close()
    entries = []
    for pack in sorted(packs.values(), key=lambda p: p.name):
        entry = {
            "name": pack.name,
            "file": os.path.basename(pack.path),
            "size": os.path.getsize(pack.path),
            "sha256": sha256_file(pack.path),
            "unpacked": pack.unpacked,
            "optional": pack.name.startswith("payload-"),
        }
        if pack.name.startswith("payload-"):
            entry["module"] = pack.name[len("payload-"):]
        if pack.name in SHAREABLE:
            entry["shareable"] = True
            entry["immutable"] = pack.name in IMMUTABLE
            entry["files"] = sorted(pack.files, key=lambda f: f["path"])
            entry["dirs"] = sorted(pack.dirs)
        entries.append(entry)
    whole = {"size": os.path.getsize(source), "sha256": sha256_file(source)}
    manifest = {
        "size": whole["size"], "sha256": whole["sha256"],
        "unpacked": sum(p.unpacked for p in packs.values()),
        "format": 2, "protocol": protocol, "commit": commit, "packs": entries,
    }
    with open(os.path.join(out, "wrathpp-server.json"), "w") as f:
        json.dump(manifest, f, separators=(",", ":"))
    return manifest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--out", required=True)
    ap.add_argument("--level", type=int, default=6)
    ap.add_argument("--commit", default="")
    ap.add_argument("--protocol", type=int, default=1)
    args = ap.parse_args()
    manifest = repack(args.source, args.out, args.level, args.commit, args.protocol)
    for p in manifest["packs"]:
        print("%-28s %8.1f MB packed %8.1f MB unpacked%s" % (
            p["name"], p["size"] / 1e6, p["unpacked"] / 1e6, "  (optional)" if p["optional"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
