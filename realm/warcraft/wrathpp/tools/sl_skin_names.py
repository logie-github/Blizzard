#!/usr/bin/env python3
"""Which of today's files each skin of Wrath++'s looks was made from, by name: what a set of replacement textures named as
today's game names them (Ralia's mod: humanfemaleskin00_03_hd.blp) is matched by. The app's Ralia import
(app/src/main/java/com/logie/blizz/wrathpp/WrathppRalia.kt) reads the list from the looks.

    python3 tools/sl_skin_names.py fetch LOOKS.json data/skin_names.json    the names, from wago.tools (slow; now and then)
    python3 tools/sl_skin_names.py list LOOKS.json data/skin_names.json OUT.json      the list (wrathpp-looks.yml: no network)

The looks know a skin by its file's id; the names are wago.tools' (its file search, a word a model, as mod-ralia's
build_data.py asks it), kept in data/skin_names.json (file id: name; names alone, as mod-ralia's retail_paths.json) so
that making the looks doesn't wait on that search. A skin with a body tattoo painted in is left out of the list (a
replacement body would lose the tattoo), and so is one whose file has no name.

    { "format": 1, "models": { "1_1": { "name": "HumanFemale", "race": 1, "sex": 1, "skins": [
        { "index": 0, "path": "Character\\Human\\Female\\HumanFemaleSkin00_00.blp", "retail": "humanfemaleskin00_00_hd.blp" } ] } } }
"""
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sl_looks                                 # noqa: E402  (puts the allied races' tools on the path)


def wago_search(word):
    request = urllib.request.Request("https://wago.tools/api/files?search=" + word, headers={"User-Agent": "wrathpp-looks/1.0"})
    with urllib.request.urlopen(request, timeout=300) as response:
        found = json.load(response)
    return found if isinstance(found, dict) else {}


def fetch(looks, known, search=wago_search, log=print, save=lambda: None):
    """Adds to [known] (file id: name) the names of the looks' skins' files it hasn't; a search that fails costs its model."""
    for entry in looks["races"].values():
        for sex, model in sorted(entry["models"].items()):
            wanted = {str(s["body"]) for s in model["skins"]}
            if wanted <= set(known):
                continue
            for word in ((model["name"] + "skin").lower(), model["name"].lower()):
                try:
                    found = search(word)
                except Exception as e:                      # the site not answering
                    log("%s: no answer for %s (%s)" % (model["name"], word, e))
                    continue
                for fid, name in found.items():
                    if fid in wanted:
                        known[fid] = os.path.basename(name.replace("\\", "/")).lower()
                if wanted & set(known):
                    break
            save()
            log("%s: %d of %d skins' files named" % (model["name"], len(wanted & set(known)), len(wanted)))
    return known


def build(looks, known, log=print):
    import names
    out = {"format": 1, "build": looks.get("build", sl_looks.BUILD), "models": {}}
    for entry in looks["races"].values():
        for sex, model in sorted(entry["models"].items()):
            skins = [{"index": s["index"], "path": names.skin(model, s["index"]), "retail": known[str(s["body"])]}
                     for s in model["skins"] if not s.get("tattoo") and str(s["body"]) in known]
            if skins:
                out["models"]["%d_%d" % (entry["race"], int(sex))] = {"name": model["name"], "race": entry["race"], "sex": int(sex), "skins": skins}
            log("%s: %d of %d skins named" % (model["name"], len(skins), sum(1 for s in model["skins"] if not s.get("tattoo"))))
    return out


def main(argv):
    if len(argv) == 4 and argv[1] == "fetch":
        with open(argv[2]) as f:
            looks = json.load(f)
        known = {}
        if os.path.isfile(argv[3]):
            with open(argv[3]) as f:
                known = json.load(f)

        def save():
            with open(argv[3], "w") as f:
                json.dump(known, f, indent=0, sort_keys=True)
        fetch(looks, known, save=save)
        save()
        return 0
    if len(argv) == 5 and argv[1] == "list":
        with open(argv[2]) as f:
            looks = json.load(f)
        with open(argv[3]) as f:
            known = json.load(f)
        data = build(looks, known)
        os.makedirs(os.path.dirname(os.path.abspath(argv[4])), exist_ok=True)
        with open(argv[4], "w") as f:
            json.dump(data, f, indent=1, sort_keys=True)
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
