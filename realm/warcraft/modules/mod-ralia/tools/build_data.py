#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""The allied races' sources for Ralia's mod (data/client/sources.txt): which of today's files each of
their skin and underwear colours takes.

The allied races' colours (mod-allied-races, data/retail/races.json) are numbered as this game's tables
have them, not as today's files are, so their textures' names (VoidElfFemaleSkin00_07.blp...) aren't
those of Ralia's files: each takes the file its colour was made from (its body's, pelvis's and torso's
file ids, named by today's game's file list: data/retail_paths.json). A tattooed colour takes the change
of its plain colour (the same body, no tattoo: "=" and that colour's texture), so its tattoo stays; one
with no plain colour takes the nearest colour's ("=" alone).

  build_data.py            writes data/client/sources.txt from data/retail_paths.json
  build_data.py --fetch    fetches the file names from wago.tools first (data/retail_paths.json)
"""
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
MODULE = os.path.dirname(HERE)
ALLIED = os.path.join(MODULE, "..", "mod-allied-races")
sys.path.insert(0, os.path.join(ALLIED, "tools"))
import names  # noqa: E402

RACES = os.path.join(ALLIED, "data", "retail", "races.json")
PATHS = os.path.join(MODULE, "data", "retail_paths.json")
OUT = os.path.join(MODULE, "data", "client", "sources.txt")


def models():
    with open(RACES) as f:
        races = json.load(f)
    for key in sorted(races):
        for sex in sorted(races[key]["models"]):
            yield key, races[key]["models"][sex]


def file_ids():
    ids = set()
    for _, model in models():
        for s in model["skins"]:
            for kind in ("body", "pelvis", "torso"):
                if s.get(kind):
                    ids.add(s[kind])
    return ids


def fetch():
    """The file names of today's game for the races' file ids, from wago.tools' file search (a search a
    race's folder, the blood elves' too: the void elves wear some of theirs)."""
    wanted = file_ids()
    found = {}
    for word in ("voidelf", "nightborne", "lightforgeddraenei", "zandalaritroll", "bloodelffemale", "bloodelfmale"):
        url = "https://wago.tools/api/files?search=" + word
        request = urllib.request.Request(url, headers={"User-Agent": "YeaBwoi-build/1.0 (+https://github.com/logie-github/YeaBwoi)"})
        with urllib.request.urlopen(request, timeout=300) as response:
            for fid, path in json.load(response).items():
                if int(fid) in wanted:
                    found[int(fid)] = path
    missing = sorted(wanted - set(found))
    if missing:
        sys.exit("no names for file ids %s" % missing)
    with open(PATHS, "w") as f:
        json.dump({str(k): found[k] for k in sorted(found)}, f, indent=0, sort_keys=True)
        f.write("\n")


def build():
    with open(PATHS) as f:
        paths = {int(k): v for k, v in json.load(f).items()}
    lines = ["# Ralia's mod: which of today's files each of the allied races' colours takes (tools/build_data.py).",
             "# target<TAB>source: a file of today's game by its path (Ralia's file of that name), or \"=\" and the",
             "# colour whose change it takes (a tattooed colour's plain one; \"=\" alone: the nearest colour's)."]
    for key, model in models():
        plain = {}
        for s in model["skins"]:
            if not s["tattoo"]:
                plain.setdefault(s["body"], s["index"])
        for s in model["skins"]:
            c = s["index"]
            if s["tattoo"]:
                base = plain.get(s["body"])
                lines.append("%s\t=%s" % (names.skin(model, c), names.skin(model, base) if base is not None else ""))
            else:
                lines.append("%s\t%s" % (names.skin(model, c), paths[s["body"]]))
            for kind, name in (("pelvis", names.pelvis), ("torso", names.torso)):
                if s.get(kind):
                    lines.append("%s\t%s" % (name(model, c), paths[s[kind]]))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("%s: %d lines" % (os.path.relpath(OUT, MODULE), len(lines) - 3))


if __name__ == "__main__":
    if "--fetch" in sys.argv[1:]:
        fetch()
    build()
