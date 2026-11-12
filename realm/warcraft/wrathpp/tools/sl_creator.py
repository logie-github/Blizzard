#!/usr/bin/env python3
"""What Wrath++'s character creator shows (app/src/main/assets/wrathpp/WrathppCreate.lua): Shadowlands' own list of
customization options for each race and sex, in its categories and its order, each option's choices in the order
and with the names and colour swatches the game gives them, and how a choice reaches the 3.3.5 game.

3.3.5 keeps five numbers a character (skin, face, hair style, hair colour, feature). tools/sl_looks.py packs
Shadowlands' options into them: a face number is a face and an eye colour, a feature number one choice of each of
several options, a skin number a skin colour and (where the race has them) a body tattoo. The creator shows the
options apart again, as Shadowlands does; this file is the key between the two:

    WrathppLooks.models["<race>_<sex>"] = {
        fields = { skin = {19}, face = {36, 7}, hair = {26}, haircolor = {42}, feature = {8, 7, 3} },
              a number is its parts, the first changing slowest: face = facePart * 7 + eyePart
        categories = { { id, name, order, zoom }, ... }          Shadowlands' (Face, Hair, Accessories, Body, Markings)
        options = { { name, category, type (0 a list, 1 a switch), field, part (1-based), choices = { {v, n, s, s2, c} } } }
              v: the part's number for that choice; n: its name (empty: a number alone); s, s2: swatch colours
              (0xRRGGBB); c: "dk" a death knight's alone, "nodk" every other class's.
              An option with no field is one nothing draws yet (the native mod's work): listed, and not chosen from.
    }

    python3 tools/sl_creator.py data CSV_DIR LOOKS.json OUT.lua

CSV_DIR and LOOKS.json: sl_looks.py's (fetch, races). Made by wrathpp-looks.yml into the looks package
(client/Interface/GlueXML/WrathppLooks.lua); the app puts it in the creator's patch beside the script.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sl_looks                                 # noqa: E402
from sl_looks import allied                     # noqa: E402

DK, DH = 1 << 5, 1 << 11
FIELDS = ("skin", "face", "hair", "haircolor", "feature")


def class_rule(tables, choice):
    """Which of 3.3.5's classes may pick a choice: "dk", "nodk" or None (all). A demon hunter's alone is everyone's
    (Wrath++ has no demon hunters: docs/wrathpp/SHADOWLANDS_OPTIONS.md)."""
    req = tables.reqs.get(choice["ChrCustomizationReqID"])
    if req is None:
        return None
    mask = int(req["ClassMask"])
    if mask in (0, -1):
        return None
    mask &= 0xFFF
    if mask & ~DH == 0:
        return None
    if mask & ~DH == DK:
        return "dk"
    if not mask & DK:
        return "nodk"
    return None


def swatch(value):
    value = int(value or 0)
    return value & 0xFFFFFF if value else None


def entry(tables, choice, digit):
    e = {"v": digit, "n": choice["Name_lang"] or ""}
    for key, column in (("s", "SwatchColor_0"), ("s2", "SwatchColor_1")):
        colour = swatch(choice.get(column))
        if colour is not None:
            e[key] = colour
    rule = class_rule(tables, choice)
    if rule:
        e["c"] = rule
    return e


def ui_order(choice):
    return int(choice.get("UiOrderIndex") or 0), int(choice["OrderIndex"])


def digits_of(tables, model, chr_model):
    """For each of today's options the looks carry: (field, part index, {choice id: the part's number}), by option name."""
    out = {}
    aliases = {tables.aliases.get((str(chr_model), asked), asked): asked for asked in ("Hair Style", "Hair Color")}
    skin_parts = []
    if len(model["tattoos"]) > 1:
        for oname in allied.BODY_TATTOOS:
            tattoos = tables.option_choices(chr_model, oname, only_available=False)
            if tattoos:
                digits = {tattoos[0]["ID"]: 0}
                for t in tattoos[1:]:
                    if [f for _, fs in tables.choice_materials(t, allied.TARGET_TATTOO) for f in fs]:
                        digits[t["ID"]] = len(digits)
                if len(digits) != len(model["tattoos"]):
                    raise ValueError("%s: %d tattoos here, %d in the looks" % (model["name"], len(digits), len(model["tattoos"])))
                out[oname] = ("skin", 0, digits)
                skin_parts.append(len(digits))
                break
    base = model["base_skins"]
    out["Skin Color"] = ("skin", len(skin_parts), {s["choice"]: s["base"] for s in model["skins"][:base]})
    skin_parts.append(base)
    out["Face"] = ("face", 0, {f["choice"]: i for i, f in enumerate(model["faces"])})
    out["Eye Color"] = ("face", 1, {e["choice"]: e["index"] for e in model["eyes"]})
    hair_name = next(today for today, asked in aliases.items() if asked == "Hair Style")
    out[hair_name] = ("hair", 0, {h["choice"]: h["variation"] for h in model["hair"]})
    colours = {}
    for c in tables.option_choices(chr_model, "Hair Color"):
        if [f for _, fs in tables.choice_materials(c, allied.TARGET_HAIR) for f in fs]:
            colours[c["ID"]] = len(colours)
    if len(colours) != len(model["hair_colors"]):
        raise ValueError("%s: %d hair colours here, %d in the looks" % (model["name"], len(colours), len(model["hair_colors"])))
    colour_name = next(today for today, asked in aliases.items() if asked == "Hair Color")
    out[colour_name] = ("haircolor", 0, colours)
    feature_parts = []
    for k, oname in enumerate(model["feature_options"]):
        cs = tables.option_choices(chr_model, oname, only_available=False)
        out[oname] = ("feature", k, {c["ID"]: i for i, c in enumerate(cs)})
        feature_parts.append(len(cs))
    fields = {"skin": skin_parts, "face": [len(model["faces"]), len(model["eyes"])], "hair": [len(model["hair"])],
              "haircolor": [len(model["hair_colors"])], "feature": feature_parts}
    counts = {"skin": len(model["skins"]), "face": len(model["faces"]) * len(model["eyes"]), "hair": len(model["hair"]),
              "haircolor": len(model["hair_colors"]), "feature": len(model["features"])}
    for field, parts in fields.items():
        n = 1
        for p in parts:
            n *= p
        if n != counts[field]:
            raise ValueError("%s: the %s parts %s make %d, the looks have %d" % (model["name"], field, parts, n, counts[field]))
    return out, fields


def build_model(tables, categories, race_id, sex, model):
    chr_model = model["chr_model"]
    for asked, today in sl_looks.ALIASES.get(race_id, {}).items():
        tables.aliases[(str(chr_model), asked)] = today
    tables.only_available[str(chr_model)] = sl_looks.AVAILABLE_ONLY.get((race_id, sex), set())
    tables.unlock(chr_model, sl_looks.UNLOCKED_ACHIEVEMENTS.get(race_id, set()))
    drawn, fields = digits_of(tables, model, chr_model)
    options, used = [], {}
    mine = sorted((o for o in tables.options.values() if o["ChrModelID"] == str(chr_model)), key=lambda o: int(o["OrderIndex"]))
    for o in mine:
        category = categories.get(o["ChrCustomizationCategoryID"])
        if category is None or int(category.get("SpellShapeshiftFormID") or 0):
            continue                                    # a druid's forms: 3.3.5's are fixed models
        choices = sorted(tables.choices[o["ID"]], key=ui_order)
        option = {"name": o["Name_lang"], "category": int(category["ID"]), "type": int(o["OptionType"] or 0)}
        if o["Name_lang"] in drawn:
            field, part, digits = drawn[o["Name_lang"]]
            option["field"], option["part"] = field, part + 1
            option["choices"] = [entry(tables, c, digits[c["ID"]]) for c in choices if c["ID"] in digits]
        else:
            option["choices"] = [entry(tables, c, i) for i, c in enumerate(c for c in choices if tables.available(c))]
        if len(option["choices"]) < 2:
            continue
        options.append(option)
        used[category["ID"]] = category
    cats = [{"id": int(c["ID"]), "name": c["CategoryName_lang"].split(" (")[0], "order": int(c["OrderIndex"]),
             "zoom": int(c.get("CameraZoomLevel") or 0)} for c in used.values()]
    cats.sort(key=lambda c: (c["order"], c["id"]))
    return {"race": race_id, "sex": sex, "name": model["name"], "fields": fields, "categories": cats, "options": options}


def build(csv_dir, looks):
    tables = sl_looks.Tables(csv_dir)
    categories = {c["ID"]: c for c in allied.rows(csv_dir, "ChrCustomizationCategory")}
    models = {}
    for race in looks["races"].values():
        for sex, model in sorted(race["models"].items()):
            models["%d_%d" % (race["race"], int(sex))] = build_model(tables, categories, race["race"], int(sex), model)
    return {"build": looks.get("build", sl_looks.BUILD), "models": models}


# --- Lua ---------------------------------------------------------------------------------------------------------

def lua_value(v, indent=0):
    pad = "\t" * indent
    if v is None:
        return "nil"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        return '"%s"' % v.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    if isinstance(v, (list, tuple)):
        if all(not isinstance(x, (dict, list, tuple)) for x in v) or all(isinstance(x, dict) and set(x) <= {"v", "n", "s", "s2", "c"} for x in v):
            return "{ " + ", ".join(lua_value(x) for x in v) + (" }" if v else "}")
        return "{\n" + "".join("%s\t%s,\n" % (pad, lua_value(x, indent + 1)) for x in v) + pad + "}"
    if isinstance(v, dict):
        keys = sorted(v, key=lambda k: (k not in ("name", "race", "sex"), str(k)))
        key = lambda k: k if isinstance(k, str) and k.isidentifier() else '["%s"]' % k
        if set(v) <= {"v", "n", "s", "s2", "c"}:
            return "{ " + ", ".join("%s = %s" % (k, lua_value(v[k])) for k in ("v", "n", "s", "s2", "c") if k in v) + " }"
        return "{\n" + "".join("%s\t%s = %s,\n" % (pad, key(k), lua_value(v[k], indent + 1)) for k in keys) + pad + "}"
    raise TypeError(type(v))


def lua(data):
    return ("-- Wrath++'s creator: Shadowlands' options a race and sex (%s), made by realm/warcraft/wrathpp/tools/sl_creator.py.\n"
            "WrathppLooks = %s\n" % (data["build"], lua_value(data)))


def main(argv):
    if len(argv) == 5 and argv[1] == "data":
        with open(argv[3]) as f:
            looks = json.load(f)
        data = build(argv[2], looks)
        os.makedirs(os.path.dirname(os.path.abspath(argv[4])), exist_ok=True)
        with open(argv[4], "w", encoding="utf-8", newline="\n") as f:
            f.write(lua(data))
        for key, m in sorted(data["models"].items()):
            drawn = [o["name"] for o in m["options"] if "field" in o]
            rest = [o["name"] for o in m["options"] if "field" not in o]
            print("%s: %d options drawn (%s); not drawn yet: %s" % (m["name"], len(drawn), ", ".join(drawn), ", ".join(rest) or "none"))
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
