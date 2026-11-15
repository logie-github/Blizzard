#!/usr/bin/env python3
"""The registry's categories for the Shadowlands options a character keeps (the parts: sl_parts.py): one category for each
option of each race and sex that is drawn, so that the realm keeps a character's choice of it, sends it to the clients that
see her and the add-on gives it to the native mod.

    python3 tools/registry_parts.py LOOKS.json              rewrites registry/registry.json (the categories from 1190) and
                                                            registry/parts_ids.json when what is drawn changed

A category's id is the next free one from 1200 the first time an option is drawn and the same ever after (parts_ids.json:
"never reuse a category or option id for another look"); 1190 is the hair colour the character was made with (the pictures
that follow the hair, eyebrows, are chosen by it). A category's options are the choices' numbers ("1" to "N": no text of
the game's is in the repository), the first the default (today's "None" where an option has one); the creator shows the
choices by their names from the looks. The registry's version goes up by one when anything here changed."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import registry  # noqa: E402

REGISTRY = os.path.join(os.path.dirname(HERE), "registry", "registry.json")
IDS = os.path.join(os.path.dirname(HERE), "registry", "parts_ids.json")
HAIR_COLOUR = 1190
FIRST = 1200
RACES = (1, 2, 3, 4, 5, 6, 7, 8, 10, 11)
SEXES = {0: "male", 1: "female"}
ORIGIN = "Wrath++'s own: a Shadowlands option a character keeps (tools/registry_parts.py); the native mod draws it as a part"


def drawn(model):
    """The options of [model] (a looks.json model) that a part draws: [(name, number of choices)]."""
    return [(o["name"], len(o["choices"])) for o in model.get("overlays", [])]


def build(looks, doc, ids):
    kept = [c for c in doc["categories"] if c["id"] < HAIR_COLOUR]
    keys = ids.setdefault("keys", {})
    nxt = ids.get("next", FIRST)
    cats = []
    colours = 1
    for race_key, entry in sorted(looks["races"].items(), key=lambda kv: int(kv[0])):
        for sex_key, model in sorted(entry["models"].items()):
            colours = max(colours, len(model.get("hair_colors", [])))
            for name, n in drawn(model):
                key = "%d_%d:%s" % (entry["race"], int(sex_key), name)
                if key not in keys:
                    keys[key] = nxt
                    nxt += 1
                cats.append({"id": keys[key], "key": "PART_" + key.upper().replace(":", "_").replace(" ", "_"), "name": name[:48], "kind": "texture_layer",
                             "default": 1, "origin": ORIGIN,
                             "eligibility": [{"race": entry["race"], "sexes": [SEXES[int(sex_key)]], "classes": []}],
                             "options": [{"id": i + 1, "name": str(i + 1), "value": i} for i in range(n)]})
    ids["next"] = nxt
    cats.insert(0, {"id": HAIR_COLOUR, "key": "HAIR_COLOUR", "name": "Hair colour", "kind": "texture_layer", "default": 1, "origin": ORIGIN,
                    "eligibility": [{"race": r, "sexes": ["male", "female"], "classes": []} for r in RACES],
                    "options": [{"id": i + 1, "name": str(i + 1), "value": i} for i in range(colours)]})
    return kept + cats


def main(argv):
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    with open(argv[1]) as f:
        looks = json.load(f)
    with open(REGISTRY, encoding="utf-8") as f:
        doc = json.load(f)
    ids = json.load(open(IDS)) if os.path.exists(IDS) else {}
    cats = build(looks, doc, ids)
    if cats != doc["categories"]:
        doc["categories"] = cats
        doc["version"] = int(doc["version"]) + 1
        with open(REGISTRY, "w", encoding="utf-8", newline="\n") as f:
            json.dump(doc, f, indent=2, ensure_ascii=False)
            f.write("\n")
        with open(IDS, "w", encoding="utf-8", newline="\n") as f:
            json.dump(ids, f, indent=1, sort_keys=True)
            f.write("\n")
        print("registry version %d: %d categories" % (doc["version"], len(cats)))
    else:
        print("registry unchanged (version %d)" % doc["version"])
    version, normalized = registry.normalize(doc)
    blob = registry.encode(version, normalized)
    print("%d bytes, hash %08x" % (len(blob), registry.fnv1a(blob)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
