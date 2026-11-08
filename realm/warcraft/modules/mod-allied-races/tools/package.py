#!/usr/bin/env python3
"""Fetches the two races' files from Blizzard's game (wago.tools, by their file ids: the models,
skeletons, animations, textures and voices data/retail/races.json names) and makes from them what
the 3.3.5 game draws and plays: the models (tools/m2.py, at their kin's height: tools/scale.py), the textures (tools/textures.py) and the
voices as MP3 files, into a folder laid out as the game's patch (the world server puts it in the
game as the realm starts: src/AlliedRacesPatch.cpp). The files are the game's, so they are never in
this repository: the server package runs this (scripts/package-azerothcore.sh).

    python3 tools/package.py fetch CACHE DIR      fetches into CACHE (files named by id; what's
                                                  there already isn't fetched again) and writes DIR
    python3 tools/package.py build CACHE DIR      the same from a CACHE already fetched
    python3 tools/package.py list                 the file ids needed, one a line
"""
import json
import os
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import check_m2                                # noqa: E402
import m2                                      # noqa: E402
import scale                                   # noqa: E402
import sheaths                                 # noqa: E402
import textures                                # noqa: E402

MODULE = os.path.dirname(HERE)
RACES = os.path.join(MODULE, "data", "retail", "races.json")
USER_AGENT = "YeaBwoi-build/1.0 (+https://github.com/logie-github/YeaBwoi)"   # (wago.tools turns away Python's own)
MANIFEST = "alliedraces.files"


def wago(file_id):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request("https://wago.tools/api/casc/%d?download" % file_id,
                                        headers={"User-Agent": USER_AGENT}), timeout=120) as response:
                return response.read()
        except Exception as error:  # a network hiccup: once more, a little later
            print("package: file %d: %s" % (file_id, error), file=sys.stderr)
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("file %d couldn't be fetched" % file_id)


def cached(cache, fetch):
    os.makedirs(cache, exist_ok=True)

    def read(file_id):
        path = os.path.join(cache, str(file_id))
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            if fetch is None:
                raise FileNotFoundError(file_id)
            data = fetch(file_id)
            with open(path + ".part", "wb") as out:
                out.write(data)
            os.replace(path + ".part", path)
        with open(path, "rb") as f:
            return f.read()
    return read


def needed_files(races):
    """Every file id the races need (the models' skeletons and animations are found as the
    models are read, so they aren't here)."""
    ids = set()
    for race in races.values():
        for model in race["models"].values():
            ids.add(model["model"])
            if model["parent_model"]:
                ids.add(model["parent_model"])
            ids.update(model["hardcoded_files"].values())
            for h in model["hair_colors"]:
                ids.add(h["file"])
            for s in model["skins"]:
                ids.update(f for f in (s["body"], s["pelvis"], s["torso"]) if f)
                ids.update(s["tattoo"])
            for f in model["faces"]:
                ids.update(v for v in f["textures"].values() if v)
            for e in model["eyes"]:
                ids.add(e["file"])
                if e.get("overlay"):
                    ids.add(e["overlay"])
        for v in race["voices"]["vocal"]:
            for k in v["kits"]:
                ids.update(k["files"])
        for e in race["voices"]["emotes"]:
            ids.update(e["kit"]["files"])
    ids.discard(0)
    return sorted(ids)


def voice_files(race, read, out_dir, log):
    """The race's voices as MP3s (as the game's narrations are; a tenth of the WAVs' size), named by
    their sound kits: Sound\\Character\\<Race>\\<Race>_<kit>_<n>.mp3."""
    written = []
    kits = {}
    for v in race["voices"]["vocal"]:
        for k in v["kits"]:
            kits[k["id"]] = k["files"]
    for e in race["voices"]["emotes"]:
        kits[e["kit"]["id"]] = e["kit"]["files"]
    folder = os.path.join(out_dir, "Sound", "Character", race["name"])
    os.makedirs(folder, exist_ok=True)
    for kit, files in sorted(kits.items()):
        for n, fid in enumerate(files):
            name = "%s_%d_%d.mp3" % (race["name"], kit, n + 1)
            path = os.path.join(folder, name)
            # Made again from the game's file (cached by its id) each time: an MP3 already there
            # may be one an earlier run left cut short, which still decodes in part.
            src, part = path + ".src", path + ".part"
            try:
                with open(src, "wb") as f:
                    f.write(read(fid))
                # Encoded as the game's own MP3s are: MPEG-1 (44.1 kHz), constant bitrate, no ID3
                # tag and no VBR (Xing) header, which the 2008 client's decoder may not take.
                result = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-xerror", "-y", "-i", src, "-map", "0:a:0",
                                         "-ac", "1", "-ar", "44100", "-codec:a", "libmp3lame", "-b:a", "64k", "-write_xing", "0",
                                         "-id3v2_version", "0", "-write_id3v1", "0", "-f", "mp3", part], capture_output=True)
                if result.returncode or not os.path.exists(part) or not os.path.getsize(part):
                    # (a voice missing would be silence where the tables name it: the package isn't made)
                    raise RuntimeError("voice %d (kit %d) couldn't be converted: %s" %
                                       (fid, kit, result.stderr.decode(errors="replace").strip()))
                os.replace(part, path)
            finally:
                for temporary in (src, part):
                    if os.path.exists(temporary):
                        os.remove(temporary)
            written.append("Sound\\Character\\%s\\%s" % (race["name"], name))
    return written


def build(read, out_dir, log=print):
    # The list of files goes first and comes back last: a run that stops on the way leaves none, so
    # the world server never takes an earlier run's list for this one's files.
    os.makedirs(out_dir, exist_ok=True)
    manifest = os.path.join(out_dir, MANIFEST)
    if os.path.exists(manifest):
        os.remove(manifest)
    with open(RACES) as f:
        races = json.load(f)
    written = []
    for key, race in races.items():
        for sex, model in race["models"].items():
            policy = dict(model, geosets=None)
            written += m2.convert(read, policy, out_dir, log)
            # at its kin's height (tools/scale.py): blood elves', night elves', Draenei's, trolls'
            model_path = os.path.join(out_dir, model["folder"].replace("\\", "/"), model["name"] + ".m2")
            scale.to_kin(model_path, log)
            # its weapons on its back as its kin wear them (tools/sheaths.py)
            sheaths.turn(model_path, log)
            # checked the way the game would trip over it (tools/check_m2.py: the sequences' own files too)
            problems = check_m2.check(model_path)
            if problems:
                raise ValueError("%s: %s" % (model["name"], "; ".join(problems[:20])))
            layout_path = os.path.join(out_dir, model["folder"].replace("\\", "/"), model["name"] + ".layout.json")
            with open(layout_path) as f:
                layout = json.load(f)
            written += textures.build(read, model, layout, out_dir, log)
            for path, fid in model["hardcoded_files"].items():
                full = os.path.join(out_dir, path.replace("\\", "/"))
                if not os.path.exists(full):
                    os.makedirs(os.path.dirname(full), exist_ok=True)
                    with open(full, "wb") as out:
                        out.write(read(fid))
                written.append(path)
        written += voice_files(race, read, out_dir, log)
    # the list of files, written last: the world server takes the races into the game only when
    # it's there and every file it names is
    with open(manifest, "w") as out:
        out.write("".join(name + "\n" for name in sorted(set(written))))
    log("package: %d files in %s" % (len(set(written)), out_dir))


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "list":
        with open(RACES) as f:
            print("\n".join(str(i) for i in needed_files(json.load(f))))
    elif len(sys.argv) == 4 and sys.argv[1] in ("fetch", "build"):
        build(cached(sys.argv[2], wago if sys.argv[1] == "fetch" else None), sys.argv[3])
    else:
        print(__doc__)
        sys.exit(2)
