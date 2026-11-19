#!/usr/bin/env python3
"""Checks wrathpp-repack.py on a small package made here: which pack each path goes to, that every file is in exactly one
pack with the hash the manifest says, that the packs unpack to the original, and that the manifest keeps format 1's fields."""
import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("repack", os.path.join(HERE, "wrathpp-repack.py"))
repack = importlib.util.module_from_spec(spec)
spec.loader.exec_module(repack)

FILES = {
    "ctl.sh": b"#!/bin/sh\n", "VERSION": b"v1", "bin/worldserver": b"W" * 100, "bin/authserver": b"A" * 10,
    "bin/mariadbd": b"M" * 50, "bin/mariadb": b"m", "lib/libc.musl-aarch64.so.1": b"L" * 40, "share/mariadb/x": b"s",
    "mariadb-seed/ibdata1": b"I" * 30, "etc/worldserver.conf.dist": b"c", "lua_scripts/a.lua": b"l",
    "src/data/sql/base/db_world/a.sql": b"INSERT 1;", "src/data/sql/updates/b.sql": b"INSERT 2;",
    "src/modules/mod-playerbots/data/sql/playerbots/p.sql": b"p", "src/modules/mod-x/data/sql/db-world/w.sql": b"w",
    "src/modules/mod-x/src/Bracket_a/sql/z.sql": b"z", "src/modules/mod-x/data/zones/server/maps/m": b"m",
    "src/modules/mod-x/data/files/Character/big.m2": b"B" * 500, "src/modules/mod-y/data/files/Sound/s.ogg": b"S" * 20,
    "src/modules/mod-wrathpp-customization/data/registry.bin": b"R", "src/modules/mod-wrathpp-customization/data/sql/db-world/c.sql": b"c",
}
EXPECT = {
    "ctl.sh": "core", "VERSION": "core", "bin/worldserver": "core", "bin/authserver": "core", "bin/mariadbd": "runtime", "bin/mariadb": "runtime",
    "lib/libc.musl-aarch64.so.1": "runtime", "share/mariadb/x": "runtime", "mariadb-seed/ibdata1": "runtime", "etc/worldserver.conf.dist": "core",
    "lua_scripts/a.lua": "core", "src/data/sql/base/db_world/a.sql": "sql", "src/data/sql/updates/b.sql": "sql",
    "src/modules/mod-playerbots/data/sql/playerbots/p.sql": "modules-sql", "src/modules/mod-x/data/sql/db-world/w.sql": "modules-sql",
    "src/modules/mod-x/src/Bracket_a/sql/z.sql": "modules-sql", "src/modules/mod-x/data/zones/server/maps/m": "modules-data",
    "src/modules/mod-x/data/files/Character/big.m2": "payload-mod-x", "src/modules/mod-y/data/files/Sound/s.ogg": "payload-mod-y",
    "src/modules/mod-wrathpp-customization/data/registry.bin": "core", "src/modules/mod-wrathpp-customization/data/sql/db-world/c.sql": "core",
}


def sha(b):
    return hashlib.sha256(b).hexdigest()


class RepackTest(unittest.TestCase):
    def test_rules(self):
        for path, pack in EXPECT.items():
            self.assertEqual(pack, repack.pack_of(path), path)

    def test_repack(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = os.path.join(tmp, "wrathpp-server.tar.xz")
            with tarfile.open(source, "w:xz") as t:
                for d in ("server", "server/src/data/sql/custom", "server/bin"):
                    info = tarfile.TarInfo(d); info.type = tarfile.DIRTYPE; info.mode = 0o755; t.addfile(info)
                for path, data in FILES.items():
                    info = tarfile.TarInfo("server/" + path); info.size = len(data); info.mode = 0o755 if path.startswith("bin/") else 0o644
                    t.addfile(info, io.BytesIO(data))
            out = os.path.join(tmp, "out")
            manifest = repack.repack(source, out, 1, "abc", 1)
            # format 1's fields describe the whole package, so an app that only knows format 1 still installs
            self.assertEqual(os.path.getsize(source), manifest["size"])
            self.assertEqual(sha(open(source, "rb").read()), manifest["sha256"])
            self.assertEqual(2, manifest["format"])
            self.assertEqual(json.load(open(os.path.join(out, "wrathpp-server.json")))["sha256"], manifest["sha256"])
            by_name = {p["name"]: p for p in manifest["packs"]}
            self.assertEqual({"core", "runtime", "sql", "modules-sql", "modules-data", "payload-mod-x", "payload-mod-y"}, set(by_name))
            self.assertTrue(by_name["payload-mod-x"]["optional"] and not by_name["core"]["optional"])
            self.assertEqual("mod-x", by_name["payload-mod-x"]["module"])
            self.assertTrue(by_name["sql"]["shareable"] and by_name["sql"]["immutable"])
            self.assertTrue(by_name["runtime"]["shareable"] and not by_name["runtime"]["immutable"])
            self.assertNotIn("files", by_name["core"])
            self.assertIn("src/data/sql/custom", by_name["sql"]["dirs"])
            # each pack's own hash and size are right; every file is in exactly one pack, with its hash
            seen = {}
            for name, p in by_name.items():
                path = os.path.join(out, p["file"])
                self.assertEqual(os.path.getsize(path), p["size"])
                self.assertEqual(sha(open(path, "rb").read()), p["sha256"])
                with tarfile.open(path, "r:xz") as t:
                    for m in t:
                        if m.isfile():
                            data = t.extractfile(m).read()
                            rel = m.name[len("server/"):]
                            self.assertNotIn(rel, seen, "in two packs: " + rel)
                            seen[rel] = (name, sha(data))
                            self.assertEqual(EXPECT[rel], name)
                for f in p.get("files", []):
                    self.assertEqual(sha(FILES[f["path"]]), f["sha256"])
                    self.assertEqual(len(FILES[f["path"]]), f["size"])
            self.assertEqual(set(FILES), set(seen))
            for rel, (name, digest) in seen.items():
                self.assertEqual(sha(FILES[rel]), digest)

    def test_a_link_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = os.path.join(tmp, "x.tar.xz")
            with tarfile.open(source, "w:xz") as t:
                info = tarfile.TarInfo("server/lib/l"); info.type = tarfile.SYMTYPE; info.linkname = "m"; t.addfile(info)
            with self.assertRaises(SystemExit):
                repack.repack(source, os.path.join(tmp, "o"), 1, "", 1)


if __name__ == "__main__":
    unittest.main()
