#!/usr/bin/env python3
"""Shadowlands' character customization for the ten races 3.3.5 has (and Wrath++'s realm plays), read from the game's own
tables at Shadowlands' last build (9.2.7.45745, wago.tools' CSVs of them): every option each race and sex has, in the
game's order, with its choices, and what each choice changes, so that Wrath++ can carry them faithfully as categories of
their own (docs/wrathpp/LEGION_OPTIONS_735.md, now Shadowlands').

    python3 tools/sl_inventory.py fetch CSV_DIR          the tables into CSV_DIR (wago.tools, build 9.2.7.45745)
    python3 tools/sl_inventory.py build CSV_DIR OUT.json the inventory, and a summary on stdout
    python3 tools/sl_inventory.py markdown OUT.json      the inventory as docs/wrathpp/SHADOWLANDS_OPTIONS.md's tables

What a choice changes, as the 3.3.5 renderer would have to do it:
  geoset    model pieces shown (hair, earrings, horns, beards...): group*100+id, as 3.3.5's geosets
  material  a texture painted into a section of the character's skin (tattoos, eye colour, skin, face...)
  model     a model of its own drawn with the character (a skinned model: some horns, hair pieces)
Requirements: a choice restricted to a class (death knights' eyes, demon hunters' horns and tattoos) or by an
achievement or item is marked; the inventory keeps them so the restriction can be kept or opened by decision.
"""
import collections
import csv
import json
import os
import sys
import urllib.request

BUILD = "9.2.7.45745"
TABLES = ("ChrCustomizationOption", "ChrCustomizationChoice", "ChrCustomizationElement", "ChrCustomizationGeoset",
          "ChrCustomizationMaterial", "ChrCustomizationSkinnedModel", "ChrCustomizationReq", "ChrModel",
          "ChrRaceXChrModel", "ChrCustomizationCategory")
USER_AGENT = "YeaBwoi-build/1.0 (+https://github.com/logie-github/YeaBwoi)"
# 3.3.5's playable races (ChrRaces ids, the same today).
RACES = {1: "Human", 2: "Orc", 3: "Dwarf", 4: "NightElf", 5: "Scourge", 6: "Tauren", 7: "Gnome", 8: "Troll",
         10: "BloodElf", 11: "Draenei"}
CLASSES = {1: "Warrior", 2: "Paladin", 3: "Hunter", 4: "Rogue", 5: "Priest", 6: "DeathKnight", 7: "Shaman", 8: "Mage",
           9: "Warlock", 10: "Monk", 11: "Druid", 12: "DemonHunter", 13: "Evoker"}


def fetch(csv_dir):
    os.makedirs(csv_dir, exist_ok=True)
    for t in TABLES:
        url = "https://wago.tools/db2/%s/csv?build=%s" % (t, BUILD)
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": USER_AGENT}), timeout=120) as r:
            data = r.read()
        with open(os.path.join(csv_dir, t + ".csv"), "wb") as f:
            f.write(data)
        print("%s: %d bytes" % (t, len(data)))


def rows(csv_dir, table):
    with open(os.path.join(csv_dir, table + ".csv"), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


WOTLK = {"Warrior", "Paladin", "Hunter", "Rogue", "Priest", "DeathKnight", "Shaman", "Mage", "Warlock", "Druid"}


def restriction(req):
    """What limits a choice for Wrath++'s classes: None (anyone), "unlock N" (ChrCustomizationReq.ReqType other than 3,
    a choice the game opens by something other than class: its meaning per type isn't read here), or the 3.3.5 classes
    allowed ("DeathKnight", "Druid"), "none of 3.3.5's" for a demon hunter's or evoker's alone."""
    if not req:
        return None
    if req["type"] != 3:
        return "unlock %d" % req["type"]
    if not req["classes"]:
        return None
    allowed = WOTLK.intersection(req["classes"])
    if allowed == WOTLK:
        return None
    return "+".join(sorted(allowed)) if allowed else "none of 3.3.5's"


def classes_of(mask):
    return [name for bit, name in CLASSES.items() if mask & (1 << (bit - 1))]


def build(csv_dir):
    options = rows(csv_dir, "ChrCustomizationOption")
    choices = collections.defaultdict(list)
    for c in rows(csv_dir, "ChrCustomizationChoice"):
        choices[c["ChrCustomizationOptionID"]].append(c)
    elements = collections.defaultdict(list)
    for e in rows(csv_dir, "ChrCustomizationElement"):
        elements[e["ChrCustomizationChoiceID"]].append(e)
    geosets = {g["ID"]: g for g in rows(csv_dir, "ChrCustomizationGeoset")}
    materials = {m["ID"]: m for m in rows(csv_dir, "ChrCustomizationMaterial")}
    skinned = {m["ID"]: m for m in rows(csv_dir, "ChrCustomizationSkinnedModel")}
    reqs = {r["ID"]: r for r in rows(csv_dir, "ChrCustomizationReq")}
    models = {m["ID"]: m for m in rows(csv_dir, "ChrModel")}
    categories = {c["ID"]: c["CategoryName_lang"] for c in rows(csv_dir, "ChrCustomizationCategory")}
    race_models = collections.defaultdict(list)
    for r in rows(csv_dir, "ChrRaceXChrModel"):
        race_models[int(r["ChrRacesID"])].append(r["ChrModelID"])

    out = {"build": BUILD, "races": []}
    for race_id, race_name in RACES.items():
        for model_id in sorted(race_models[race_id], key=int):
            model = models[model_id]
            sex = int(model["Sex"])
            entry = {"race": race_id, "race_name": race_name, "sex": "female" if sex else "male", "chr_model": int(model_id), "options": []}
            for o in sorted((o for o in options if o["ChrModelID"] == model_id), key=lambda o: int(o["OrderIndex"])):
                opt = {"id": int(o["ID"]), "name": o["Name_lang"], "category": categories.get(o["ChrCustomizationCategoryID"], ""),
                       "kinds": set(), "choices": []}
                for c in sorted(choices[o["ID"]], key=lambda c: int(c["OrderIndex"])):
                    req = reqs.get(c["ChrCustomizationReqID"])
                    ch = {"id": int(c["ID"]), "name": c["Name_lang"], "geosets": [], "materials": [], "models": [], "requires": None}
                    if req:
                        mask = int(req["ClassMask"] or 0)
                        ch["requires"] = {"type": int(req["ReqType"]), "classes": classes_of(mask) if mask else [],
                                          "achievement": int(req["ReqAchievementID"] or 0)}
                    for e in elements[c["ID"]]:
                        related = int(e["RelatedChrCustomizationChoiceID"] or 0)
                        if e["ChrCustomizationGeosetID"] != "0" and e["ChrCustomizationGeosetID"] in geosets:
                            g = geosets[e["ChrCustomizationGeosetID"]]
                            ch["geosets"].append({"geoset": int(g["GeosetType"]) * 100 + int(g["GeosetID"]), "with": related})
                        if e["ChrCustomizationMaterialID"] != "0" and e["ChrCustomizationMaterialID"] in materials:
                            m = materials[e["ChrCustomizationMaterialID"]]
                            ch["materials"].append({"target": int(m["ChrModelTextureTargetID"]), "resources": int(m["MaterialResourcesID"]), "with": related})
                        if e["ChrCustomizationSkinnedModelID"] != "0" and e["ChrCustomizationSkinnedModelID"] in skinned:
                            s = skinned[e["ChrCustomizationSkinnedModelID"]]
                            ch["models"].append({"file": int(s["CollectionsFileDataID"]), "geoset": int(s["GeosetType"]) * 100 + int(s["GeosetID"]), "with": related})
                    for kind in ("geosets", "materials", "models"):
                        if ch[kind]:
                            opt["kinds"].add(kind[:-1])
                    opt["choices"].append(ch)
                opt["kinds"] = sorted(opt["kinds"])
                entry["options"].append(opt)
            out["races"].append(entry)
    return out


def summary(inv):
    lines = []
    for r in inv["races"]:
        parts = []
        for o in r["options"]:
            restricted = sum(1 for c in o["choices"] if restriction(c["requires"]))
            parts.append("%s %d%s [%s]" % (o["name"], len(o["choices"]), (" (%d restricted)" % restricted) if restricted else "", "+".join(o["kinds"])))
        lines.append("%s %s: %s" % (r["race_name"], r["sex"], "; ".join(parts)))
    return "\n".join(lines)


STOCK = {"Skin Color": "skin", "Face": "face", "Hair Style": "hair style", "Hair Color": "hair colour"}


def markdown(inv):
    """A table a race and sex: each option in the game's order, its choices, what draws it and who may pick it."""
    out = []
    for r in inv["races"]:
        out.append("### %s %s (ChrModel %d)\n" % (r["race_name"], r["sex"], r["chr_model"]))
        out.append("| # | Option | Choices | Drawn by | Restricted choices | 3.3.5 slider |")
        out.append("|---|---|---|---|---|---|")
        for i, o in enumerate(r["options"], 1):
            restricted = collections.Counter(restriction(c["requires"]) for c in o["choices"] if restriction(c["requires"]))
            out.append("| %d | %s | %d | %s | %s | %s |" % (
                i, o["name"], len(o["choices"]), ", ".join(o["kinds"]) or "form (druid)",
                ", ".join("%d %s" % (n, k) for k, n in sorted(restricted.items())) or "",
                STOCK.get(o["name"], "")))
        out.append("")
    return "\n".join(out)


def main(argv):
    if len(argv) >= 3 and argv[1] == "fetch":
        fetch(argv[2])
        return 0
    if len(argv) == 4 and argv[1] == "build":
        inv = build(argv[2])
        with open(argv[3], "w", encoding="utf-8") as f:
            json.dump(inv, f, indent=1, sort_keys=False)
        print(summary(inv))
        return 0
    if len(argv) == 3 and argv[1] == "markdown":
        with open(argv[2], encoding="utf-8") as f:
            print(markdown(json.load(f)))
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
