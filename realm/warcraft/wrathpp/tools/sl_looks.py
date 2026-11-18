#!/usr/bin/env python3
"""Shadowlands' looks (9.2.7.45745) for the ten races of 3.3.5, made what the 3.3.5 game draws, for Wrath++ alone:
the models of today's ten races (wago.tools, by file id), converted by the allied races' converter
(realm/warcraft/modules/mod-allied-races/tools: m2.py, textures.py), their skins, faces, hair styles and colours
and facial features as Shadowlands has them, and the game's three character tables (CharSections, CharHairGeosets,
CharacterFacialHairStyles) with the ten races' rows made from them. The files are Blizzard's, so they are never in
this repository: CI makes them (.github/workflows/wrathpp-looks.yml) and the app puts them in Wrath++'s copy of the game
and its server's data.

    python3 tools/sl_looks.py fetch CSV_DIR                    the tables (wago.tools' CSVs at 9.2.7.45745)
    python3 tools/sl_looks.py races CSV_DIR LOOKS.json         what each race and sex is made of (from the tables)
    python3 tools/sl_looks.py data CSV_DIR RACES.json          the allied races' data (the High Elf too)
    python3 tools/sl_looks.py allied CSV_DIR LOOKS.json        the same as races, for the allied races
    python3 tools/sl_looks.py verify LOOKS.json OUT            the files the tables name are all in OUT
    python3 tools/sl_looks.py package LOOKS.json CACHE DBC OUT fetches into CACHE (files by id) and writes OUT:
                                                               OUT/client   the game's patch (game paths)
                                                               OUT/changes  the ten races' rows as change files
                                                               DBC: the server's dbc folder (server-data.env's data.zip)
    python3 tools/sl_looks.py assemble STOCK_DBC OUT CHANGES...  OUT/changes: the change files merged; OUT/dbc: the
                                                               server's tables with them applied

CSV_DIR: wago.tools' CSVs at 9.2.7.45745 (sl_inventory.py fetch, and the TABLES_MORE here).

How Shadowlands' options go on 3.3.5's five sliders for now (docs/wrathpp/SHADOWLANDS_OPTIONS.md, "The way there"):
skin colour (every one), face (every face, each with every eye colour while 3.3.5's 255 faces hold them), hair style,
hair colour, and the feature slider: the options FEATURES names, every combination (3.3.5's facial table holds geoset
groups 1, 3, 2 and 16: today's other groups are moved onto those where FEATURES says). The rest stay at their first
choice until the native mod draws them as categories of their own.
"""
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ALLIED_TOOLS = os.path.abspath(os.path.join(HERE, "..", "..", "modules", "mod-allied-races", "tools"))
sys.path.insert(0, ALLIED_TOOLS)
import races as allied                         # noqa: E402

BUILD = "9.2.7.45745"
TABLES_MORE = ("TextureFileData", "CreatureModelData", "CreatureDisplayInfo", "VocalUISounds", "EmotesTextSound",
               "SoundKitEntry", "NameGen", "ChrModelTextureLayer", "CharComponentTextureSections", "ChrCustomizationCondModel")
# race id: (folder name, ChrModel ids by sex)
RACES = {1: ("Human", {0: 1, 1: 2}), 2: ("Orc", {0: 3, 1: 4}), 3: ("Dwarf", {0: 5, 1: 6}), 4: ("NightElf", {0: 7, 1: 8}),
         5: ("Scourge", {0: 9, 1: 10}), 6: ("Tauren", {0: 11, 1: 12}), 7: ("Gnome", {0: 13, 1: 14}),
         8: ("Troll", {0: 15, 1: 16}), 10: ("BloodElf", {0: 19, 1: 20}), 11: ("Draenei", {0: 21, 1: 22}),
         # the Goblins and Worgen (Wrath++'s race ids 9 and 12, mod-worgen-goblin's; Shadowlands' Goblin ChrModels 17/18, its Worgen's
         # 43/44, the wolf form): made as the ten are, their rows replacing the module's own (the looks' change files go last for them)
         9: ("Goblin", {0: 17, 1: 18}), 12: ("Worgen", {0: 43, 1: 44})}
# The allied races and the Pandaren (Shadowlands' own race ids), which 3.3.5 hasn't: made the same way, for the races
# module that gives them a race id of 3.3.5's (docs/wrathpp/ALLIED_RACES.md). race id: (folder name, ChrModel ids by sex)
ALLIED = {27: ("Nightborne", {0: 53, 1: 54}), 28: ("Highmountain", {0: 55, 1: 56}), 29: ("VoidElf", {0: 57, 1: 58}),
          30: ("Lightforged", {0: 59, 1: 60}), 31: ("Zandalari", {0: 61, 1: 62}),
          34: ("DarkIron", {0: 67, 1: 68}), 35: ("Vulpera", {0: 69, 1: 70}), 36: ("Maghar", {0: 71, 1: 72}),
          37: ("Mechagnome", {0: 73, 1: 74})}
# The four the allied races module already makes (its own policy: parent skeletons, the eye colours that fit, the
# Lightforged runes): their key there.
LEGACY = {27: "nightborne", 29: "voidelf", 30: "lightforged", 31: "zandalari"}
# The feature slider, a race and sex: today's options (every combination, the first changing slowest; at most 255) and
# today's geoset groups moved onto 3.3.5's facial groups (1, 3, 2, 16).
FEATURES = {
    (1, 0): (["Beard", "Mustache", "Sideburns"], {}),                                   # 8 x 7 x 3
    (1, 1): (["Piercings", "Necklace"], {35: 3, 36: 2}),                                # 15 x 9
    (2, 0): (["Beard", "Sideburns"], {}),                                               # 14 x 9
    (2, 1): (["Earrings", "Nose Ring", "Necklace"], {35: 3, 36: 2}),                    # 14 x 3 x 3
    (3, 0): (["Beard", "Mustache"], {}),                                                # 11 x 10
    (3, 1): (["Earrings", "Piercings"], {35: 3}),                                       # 8 x 6
    (4, 0): (["Beard", "Mustache", "Sideburns"], {}),                                   # 8 x 5 x 5
    (4, 1): (["Earrings", "Nose Ring", "Necklace"], {35: 3, 36: 2}),                    # 4 x 4 x 4
    (5, 0): (["Jaw Features", "Face Features"], {}),                                    # 11 x 5
    (5, 1): (["Face Features", "Jaw Features"], {}),                                    # 4 x 5
    (6, 0): (["Horn Style", "Facial Hair"], {24: 3}),                                   # 17 x 13 (the horns players pick)
    (6, 1): (["Horn Style", "Earrings"], {24: 3, 35: 1}),                               # 20 x 5
    (7, 0): (["Beard", "Mustache"], {}),                                                # 9 x 11
    (7, 1): (["Earrings"], {35: 3}),                                                    # 15
    (8, 0): (["Tusks", "Earrings", "Piercing"], {40: 3, 35: 1}),                        # 10 x 6 x 3
    (8, 1): (["Tusks", "Earrings", "Piercing"], {40: 3, 35: 1}),                        # 6 x 8 x 3
    (10, 0): (["Facial Hair"], {}),                                                     # 13
    (10, 1): (["Earrings", "Necklace"], {35: 3, 36: 2}),                                # 14 x 4
    (11, 0): (["Facial Hair", "Tendrils", "Circlet"], {37: 3}),                         # 11 x 8 x 2
    (11, 1): (["Horns", "Tendrils", "Tail"], {24: 3, 38: 16}),                          # 12 x 2 x 6
    (9, 0): (["Earrings", "Nose Ring"], {35: 3}),                                        # the Goblins' (Wrath++'s 9)
    (9, 1): (["Earrings", "Nose Ring"], {35: 3}),
    # The Worgen's (Wrath++'s 12). Their ears are geosets of group 2, which 3.3.5's facial table shows itself, and they draw from
    # the head's half of the skin (the face's place of the composed texture): on the slider the game draws them, on every
    # character and creature. As a piece hung by the native mod (until 18 November 2026) they took the plain skin file, whose
    # face's place holds no face: dark shapes behind an earless head (the phone's "bear-like head and a crescent behind it").
    # Ears first (slowest), so a character made before keeps its facial hair's number.
    (12, 0): (["Ears", "Facial Hair"], {}),                                             # 12 x 12
    (12, 1): (["Ears"], {}),                                                            # 12
}
FEATURES.update({
    (28, 0): (["Horn Style", "Beard"], {24: 3}), (28, 1): (["Horn Style", "Earrings"], {24: 3, 35: 1}),
    (32, 0): (["Mustache", "Beard"], {}), (32, 1): (["Earrings", "Necklace"], {35: 3, 36: 2}),
    (34, 0): (["Facial Hair", "Piercings"], {35: 3, 16: 16}), (34, 1): (["Piercings"], {35: 3, 16: 16}),
    (35, 0): (["Ears", "Snout"], {41: 3}), (35, 1): (["Ears", "Snout"], {41: 3}),
    (36, 0): (["Beard", "Sideburns"], {}), (36, 1): (["Earrings", "Nose Ring"], {35: 3}),
    (37, 0): (["Facial Hair"], {}), (37, 1): ([], {}),
})
# Options of a feature whose choices a player picks only (ChrCustomizationReq), where every choice wouldn't fit.
AVAILABLE_ONLY = {(6, 0): {"Horn Style"}}
# Today's names for an option the allied races' reading asks for by another (the Tauren's mane is their hair style,
# their horns' colour their hair colour: the hair texture).
ALIASES = {6: {"Hair Style": "Foremane", "Hair Color": "Horn Color"}, 28: {"Hair Style": "Foremane", "Hair Color": "Horn Color"},
           35: {"Skin Color": "Fur Color"}, 12: {"Skin Color": "Fur Color"}}
# Looks today's game opens by an achievement, open to everyone on Wrath++ from the start: the Blood Elves' Dark Ranger
# skin and red eyes (achievement 15579; the user: "unlock the dark ranger skin by default for blood elves"). The skin
# was among the skins already (a choice any class may pick once it is unlocked); the eye colour is marked as one the
# creator hides (Flags) and was left out with the demon hunters' blind eyes. With it the women's twelve eye colours
# (3.3.5 holds 255 faces: 20 faces x 12) no longer have room for the death knights' own, which is the last and goes:
# 3.3.5 lights a death knight's eyes by itself.
UNLOCKED_ACHIEVEMENTS = {10: {"15579"}}
SEXES = ("Male", "Female")
# Models that don't convert yet: the game's own (Alternative HD) look stays for them, rows and all. The Blood Elf man's
# arms and legs come out shredded (his skeleton file's 252 bones; the other nineteen models are right): open.
SKIP = set()           # (the Blood Elf man was here until his files were fetched of one build: m2.MixedBuilds)


# The head's geosets (today's group 32) are numbered one higher in the models than in 9.2.7's tables: the models are fetched as
# their newest copies, which keep the inside of the mouth as 3201 and the heads from 3202, and today's ChrCustomizationGeoset
# has its three head rows (ids 2083 to 2085) one up ((32, 2) to (32, 4)); at 9.2.7 they are (32, 1) to (32, 3). Read as they
# stand, the Nightborne's Eyes (two heads) named the mouth as its first choice, so the head was left out of the model (the
# phone's race screen, 18 November 2026: eyeballs, teeth and hair around nothing), and the Human's Face Shape gave its second
# shape for the third choice and the first again, without its mouth, for the second.
HEAD_GROUP = 32
HEAD_SHIFT = 1 if BUILD == "9.2.7.45745" else 0


class Tables(allied.Tables):
    """The allied races' reading of the tables, with the ten races' own names for an option."""

    def __init__(self, csv_dir):
        super().__init__(csv_dir)
        self.aliases = {}
        self.only_available = {}
        self.unlocked = set()

    def geoset_of(self, element):
        """A choice's geoset as the models number it: a head's (HEAD_SHIFT) one up from this build's row."""
        geoset = super().geoset_of(element)
        return geoset + HEAD_SHIFT if geoset // 100 == HEAD_GROUP and geoset % 100 else geoset

    def unlock(self, model_id, achievements):
        """The choices of a model's options that only an achievement of [achievements] closes: never left out for being hidden."""
        for o in self.options.values():
            if o["ChrModelID"] != str(model_id):
                continue
            for c in self.choices[o["ID"]]:
                req = self.reqs.get(c["ChrCustomizationReqID"])
                if req is not None and req.get("ReqAchievementID") in achievements:
                    self.unlocked.add(c["ID"])

    def option_choices(self, model_id, name, only_available=True):
        name = self.aliases.get((str(model_id), name), name)
        if name in self.only_available.get(str(model_id), ()):
            only_available = True
        return super().option_choices(model_id, name, only_available)


# Today's options that are a picture laid over the head or the body (the layers of its skin after the face: eyebrows, makeup,
# scars, paints, tattoos), apart from what the five sliders and the feature slider carry.
# Feature-slider options whose colour is a picker the 3.3.5 model can't take (the Gnome woman's Earrings: their Earring Color): drawn
# again as a piece over the model's own, lifted, in the colour chosen (parts_of, sl_parts.geoset_part)
FEATURE_PARTS = {"GnomeFemale": ("Earrings",)}

# BASE ONLY (the user, 18 November 2026: "Limit the options to base options for now which means ralias mods and undead mods and
# shadowlands"): the creator, the package and the game carry only what 3.3.5's five numbers carry (skin colour, face with its eye
# colour, hair style, hair colour, the feature slider), plus Ralia's skins and the undead ones. Everything else is OFF: model pieces
# (ears, horns, tails, vines, the Gnome woman's Earrings: FEATURE_PARTS...), overlay pictures (eyebrows, makeup, scars, tattoos,
# paints), model variants (the Orc's Upright...), colour pickers; no "Not drawn yet" rows either. One switch, read by build_races, by
# the package step (load_looks) and by the creator's data (sl_creator.py): False brings today's pieces back exactly as they were.
# (WRATHPP_BASE_ONLY=0 in the environment turns it off for a run; the saved-choice registry is never touched by it.)
BASE_ONLY = os.environ.get("WRATHPP_BASE_ONLY", "1") != "0"
EXTRAS = ("overlays", "variants", "parts", "pickers")


def base_only():
    return BASE_ONLY


def strip_extras(looks):
    """[looks] (looks.json, or the allied races' keyed by name) with the extended options taken out of every model while BASE_ONLY
    is on: the lists of overlays, variants, parts and pickers empty, no part_types. In place; returns [looks]."""
    if not BASE_ONLY:
        return looks
    races = looks["races"] if isinstance(looks.get("races"), dict) and "build" in looks else looks
    for entry in races.values():
        for model in entry.get("models", {}).values():
            for k in EXTRAS:
                model[k] = []
            model.pop("part_types", None)
    return looks


SLIDERS = ("Skin Color", "Face", "Hair Style", "Hair Color", "Eye Color")
HEAD_MASKS = (512, 1024, 2048, -1)           # the layers that reach the head in today's layouts: its sections (9, 10, 11) or the whole skin (-1)
BODY_MASKS = (4096, -1)                      # and the body: its section (12) or the whole skin


def ui_order(choice):
    return int(choice.get("UiOrderIndex") or 0), int(choice.get("OrderIndex") or 0)


def overlays_of(tables, chr_model, model):
    """The options of [chr_model] that are pictures over the head, in the order the creator lists the choices (the available
    ones by their UI order: a choice's number is its place here, from 1):

        [{"name", "target", "choices": [{"name", "id", "files"}], "depends": [options], "style": bool}]

    A choice's files: {"*": file id} for any, {a hair colour's index: file id} where the picture follows the hair (eyebrows),
    {"r<id>": file id} where it follows another option's choice (a paint's colour follows the paint's style: the file is the
    colour's own for the style whose choice id that is). A choice with no picture (None) has no files. An option whose
    pictures hang on another's choices names them in "depends"; each of those (the styles: no picture of their own) is
    listed with "style": true so that the character keeps its choice of it. The pictures are the head's sections (masks 512,
    1024, 2048: 512 x 512) or the whole skin (-1: 1024 x 512, the head its right half); a picture on the body only is left to
    the body's parts."""
    layout = tables.chr_models[str(chr_model)]["CharComponentTextureLayoutID"]
    masks = {}
    for row in tables.layers:
        if row["CharComponentTextureLayoutsID"] == layout and row["TextureType"] == "1":     # the skin's (type 1), not the hair's, horns' or jewellery's
            masks[row["ChrModelTextureTargetID_0"]] = int(row["TextureSectionTypeBitMask"])
    colour_of = {c["choice"]: c["index"] for c in model["hair_colors"] if "choice" in c}
    option_of = {c["ID"]: o for o in tables.options.values() for c in tables.choices[o["ID"]]}
    out = []
    skip = set(SLIDERS) | set(model.get("feature_options", []))
    skip |= {today for (cm, asked), today in getattr(tables, "aliases", {}).items() if cm == str(chr_model)}    # (the Worgen's Fur Color is its skin's slider)
    for o in sorted((o for o in tables.options.values() if o["ChrModelID"] == str(chr_model)), key=lambda o: int(o["OrderIndex"])):
        if o["Name_lang"] in skip or (len(model.get("tattoos", [])) > 1 and o["Name_lang"] in allied.BODY_TATTOOS):
            continue                                # (the skin's own tattoos are painted into the skins already)
        choices, targets, depends = [], set(), []
        for c in sorted((c for c in tables.option_choices(chr_model, o["Name_lang"], only_available=False) if tables.available(c)), key=ui_order):
            files, body = {}, {}
            for e in tables.elements[c["ID"]]:
                if e["ChrCustomizationMaterialID"] == "0":
                    continue
                target, fids = tables.material_files(e)
                mask = masks.get(target)
                if not fids or (mask not in HEAD_MASKS and mask not in BODY_MASKS):
                    continue
                targets.add(target)
                related = e["RelatedChrCustomizationChoiceID"]
                if related == "0":
                    key = "*"
                elif related in colour_of:
                    key = str(colour_of[related])
                elif related in option_of and option_of[related]["ID"] != o["ID"]:
                    key = "r" + related
                    if option_of[related]["Name_lang"] not in depends:
                        depends.append(option_of[related]["Name_lang"])
                else:
                    continue
                if mask in HEAD_MASKS:
                    files[key] = fids[0]
                if mask in BODY_MASKS:
                    body[key] = fids[0]
            entry = {"name": c["Name_lang"], "id": c["ID"], "files": files}
            if body:
                entry["body"] = body
            choices.append(entry)
        if targets and any(c["files"] or c.get("body") for c in choices):
            entry = {"name": o["Name_lang"], "target": sorted(targets)[0], "choices": choices}
            if depends:
                entry["depends"] = depends
            out.append(entry)
    for entry in list(out):
        for name in entry.get("depends", []):
            if not any(x["name"] == name for x in out):
                chs = [{"name": c["Name_lang"], "id": c["ID"], "files": {}} for c in
                       sorted((c for c in tables.option_choices(chr_model, name, only_available=False) if tables.available(c)), key=ui_order)]
                out.append({"name": name, "target": entry["target"], "choices": chs, "style": True})
    return out


# (Eyes: the Nightborne's, two heads of the model itself, today's 3202 and 3203. As a piece laid over the model it was the head
# drawn a second time with the bare skin for its texture, on a model that had none.)
GEOSET_VARIANTS = ("Face Shape", "Skin Type", "Eyes")


def variants_of(tables, chr_model, model):
    """The options of [chr_model] that change the character's model (the Orc man's Upright: another model of the game's, a conditional
    model): [{"name", "choices": [{"name", "id", "file": the model's file id, or 0 for the model itself}]}]. A choice's number is its
    place here (the available ones by their UI order, from 1), as the creator lists them."""
    out = []
    for o in sorted((o for o in tables.options.values() if o["ChrModelID"] == str(chr_model)), key=lambda o: int(o["OrderIndex"])):
        chs = sorted((c for c in tables.option_choices(chr_model, o["Name_lang"], only_available=False) if tables.available(c)), key=ui_order)
        choices = []
        for c in chs:
            file = 0
            for e in tables.elements[c["ID"]]:
                cond = tables.cond_models.get(e.get("ChrCustomizationCondModelID", "0"))
                if cond:
                    data = tables.model_data.get(cond["CreatureModelDataID"])
                    if data and int(data["FileDataID"]) != model["model"]:
                        file = int(data["FileDataID"])
            choices.append({"name": c["Name_lang"], "id": c["ID"], "file": file})
        if len(choices) > 1 and any(c["file"] for c in choices):
            out.append({"name": o["Name_lang"], "choices": choices})
        elif len(choices) > 1 and o["Name_lang"] in GEOSET_VARIANTS:
            # the head's shape, the Forsaken's skin type: geosets of the model itself, which a model piece laid over it would double:
            # a model of its own for each choice, with that choice's geosets and none of the others'
            for choice, c in zip(choices, chs):
                choice["geosets"] = tables.choice_geosets(c)
            if any(c["geosets"] for c in choices):
                out.append({"name": o["Name_lang"], "choices": choices, "geoset": True})
    return out


def parts_of(tables, chr_model, model):
    """The options of [chr_model] that are model pieces (ears, headdresses, vines, tails, hair of the Tauren...: geosets today's 3.3.5
    skin has no room for) and the texture pickers beside them (a jewellery's, a vine's colour: a layer of a texture type other than the
    skin's):

        parts:   [{"name", "choices": [{"name", "id", "geosets": [today's geoset ids]}]}]
        pickers: [{"name", "type": today's texture type, "choices": [{"name", "id", "file": file id or 0}]}]

    A choice's number is its place here (the available ones by their UI order, from 1), as the creator lists them. What the sliders,
    the feature slider and the pictures over the head carry is not listed again."""
    layout = tables.chr_models[str(chr_model)]["CharComponentTextureLayoutID"]
    kinds = {}
    for row in tables.layers:
        if row["CharComponentTextureLayoutsID"] == layout:
            kinds[row["ChrModelTextureTargetID_0"]] = row["TextureType"]
    skip = set(SLIDERS) | set(model.get("feature_options", [])) | {o["name"] for o in model.get("overlays", [])}
    skip |= {today for (cm, asked), today in tables.aliases.items() if cm == str(chr_model)}      # (the Tauren's Foremane and Horn Color are the hair's sliders)
    skip |= {v["name"] for v in model.get("variants", [])}
    skip |= set(GEOSET_VARIANTS)                # (they replace the head or the body of the model itself: a piece laid over it would double it)
    feature_parts = FEATURE_PARTS.get(model.get("name"), ())
    skip -= set(feature_parts)
    parts, pickers = [], []
    for o in sorted((o for o in tables.options.values() if o["ChrModelID"] == str(chr_model)), key=lambda o: int(o["OrderIndex"])):
        if o["Name_lang"] in skip or (len(model.get("tattoos", [])) > 1 and o["Name_lang"] in allied.BODY_TATTOOS):
            continue
        chs = sorted((c for c in tables.option_choices(chr_model, o["Name_lang"], only_available=False) if tables.available(c)), key=ui_order)
        if o["Name_lang"] in feature_parts:
            # a feature slider's option the model draws in one colour only: a piece over it takes the colour (its choices are the slider's digits)
            every = tables.option_choices(chr_model, o["Name_lang"], only_available=False)
            geo = [{"name": c["Name_lang"], "id": c["ID"], "geosets": tables.choice_geosets(c)} for c in every]
            if any(g["geosets"] for g in geo):
                parts.append({"name": o["Name_lang"], "choices": geo, "feature": True})
            continue
        geo = [{"name": c["Name_lang"], "id": c["ID"], "geosets": tables.choice_geosets(c)} for c in chs]
        if any(g["geosets"] for g in geo) and len(chs) > 1:
            parts.append({"name": o["Name_lang"], "choices": geo})
            continue
        # A piece that is a model of its own (horns, blindfolds): a collection's model, a geoset of it for each choice
        files, skin_geo = set(), []
        for c in chs:
            ids = []
            for e in tables.elements[c["ID"]]:
                if e["ChrCustomizationSkinnedModelID"] != "0":
                    sm = tables.skinned[e["ChrCustomizationSkinnedModelID"]]
                    files.add(int(sm["CollectionsFileDataID"]))
                    ids.append(int(sm["GeosetType"]) * 100 + int(sm["GeosetID"]))
            skin_geo.append({"name": c["Name_lang"], "id": c["ID"], "geosets": ids})
        if len(files) == 1 and any(g["geosets"] for g in skin_geo) and len(chs) > 1:
            parts.append({"name": o["Name_lang"], "choices": skin_geo, "skinned": next(iter(files))})
            continue
        types = set()
        picks = []
        for c in chs:
            file = 0
            for e in tables.elements[c["ID"]]:
                if e["ChrCustomizationMaterialID"] == "0":
                    continue
                target, fids = tables.material_files(e)
                if kinds.get(target) not in (None, "1") and fids and e["RelatedChrCustomizationChoiceID"] == "0":
                    types.add(int(kinds[target]))
                    file = fids[0]
            picks.append({"name": c["Name_lang"], "id": c["ID"], "file": file})
        if len(types) == 1 and len(chs) > 1 and any(p["file"] for p in picks):
            pickers.append({"name": o["Name_lang"], "type": next(iter(types)), "choices": picks})
    return parts, pickers


# Options whose first choice is a part of the character itself, whatever the creator offers: the Mechagnome's Arm Upgrade and Leg
# Upgrade (the first choices: the 'Standard' arm, geoset 29 id 1; the leg, types 31 and 30 id 1). The model of the game the base
# model has none of its limbs in is a collection's (ChrCustomizationSkinnedModel), made on the character's skeleton: m2.convert's
# "merge" puts the choice's geosets into the character's own model as always-drawn body, with the one fixed picture the plates take
# (the first choice of the option that fills the skin extra's replaceable type 8: the Paint's, the plates' atlas in the collection's
# own coordinates), so that the Mechagnome has its arms and legs in the creator, the world and the preview, whatever skin is picked.
# (Before: a piece hung on the character, its texture the player's skin file, which these coordinates are not made for: bright
# green, the user's phone pictures of 18 November; and no piece at all while the options are off.)
ALWAYS_ON = {"Mechagnome": ("Arm Upgrade", "Leg Upgrade")}


def always_on_of(tables, chr_model, model):
    """[{"model": a collection's file id, "sections": [its geoset ids], "texture": a file id}] for [model]'s ALWAYS_ON options
    (m2.convert's "merge"), or [] for a model with none. Raises when an option has no model of its own or no picture to draw it with."""
    names = next((v for k, v in ALWAYS_ON.items() if model["name"].startswith(k)), ())
    if not names:
        return []
    layout = tables.chr_models[str(chr_model)]["CharComponentTextureLayoutID"]
    kinds = {row["ChrModelTextureTargetID_0"]: row["TextureType"] for row in tables.layers if row["CharComponentTextureLayoutsID"] == layout}
    options = sorted((o for o in tables.options.values() if o["ChrModelID"] == str(chr_model)), key=lambda o: int(o["OrderIndex"]))

    def first(option):
        chs = sorted((c for c in tables.option_choices(chr_model, option["Name_lang"], only_available=False) if tables.available(c)), key=ui_order)
        return chs[0] if chs else None

    texture = 0
    for o in options:
        c = first(o)
        for e in tables.elements[c["ID"]] if c else ():
            if e["ChrCustomizationMaterialID"] != "0":
                target, fids = tables.material_files(e)
                if kinds.get(target) == "8" and fids:
                    texture = texture or fids[0]
    out = []
    for name in names:
        option = next((o for o in options if o["Name_lang"] == name), None)
        c = first(option) if option else None
        found = {}
        for e in tables.elements[c["ID"]] if c else ():
            if e["ChrCustomizationSkinnedModelID"] != "0":
                sm = tables.skinned[e["ChrCustomizationSkinnedModelID"]]
                found.setdefault(int(sm["CollectionsFileDataID"]), []).append(int(sm["GeosetType"]) * 100 + int(sm["GeosetID"]))
        if not found:
            raise SystemExit("%s: its %s has no model of the game's to draw" % (model["name"], name))
        for fid, geosets in found.items():
            have = next((x for x in out if x["model"] == fid), None)
            if have:
                have["sections"] += geosets
                have["options"].append(name)
            else:
                out.append({"options": [name], "model": fid, "sections": geosets, "texture": texture})
    if not texture:
        raise SystemExit("%s: no picture of replaceable type 8 for %s" % (model["name"], ", ".join(names)))
    return out


def build_races(csv_dir, races=None):
    """What each race and sex is made of. [races]: RACES (the ten of 3.3.5's, the default) or ALLIED."""
    tables = Tables(csv_dir)
    out = {"build": BUILD, "races": {}}
    for race_id, (name, models) in (races or RACES).items():
        entry = {"race": race_id, "name": name, "models": {}}
        for sex, chr_model in models.items():
            if (race_id, sex) in SKIP:
                continue
            for asked, today in ALIASES.get(race_id, {}).items():
                tables.aliases[(str(chr_model), asked)] = today
            tables.only_available[str(chr_model)] = AVAILABLE_ONLY.get((race_id, sex), set())
            tables.unlock(chr_model, UNLOCKED_ACHIEVEMENTS.get(race_id, set()))
            file_id = allied.model_file(tables, chr_model)
            if not file_id:
                raise SystemExit("no model file for ChrModel %d (CreatureDisplayInfo.csv is needed)" % chr_model)
            if race_id in LEGACY:
                key = LEGACY[race_id]
                race = dict(allied.RACES[key], name=name)
            else:
                key = "wpp%d_%d" % (race_id, sex)
                allied.FEATURES[(key, sex)] = FEATURES[(race_id, sex)]
                race = {"race": race_id, "name": name, "parent_models": {sex: 0}, "eye_colours": 0}
            model = allied.build_model(tables, key, race, sex, chr_model, file_id)
            if len(model["features"]) > 255:
                raise SystemExit("%s: %d features, past 3.3.5's 255" % (model["name"], len(model["features"])))
            model["chr_model"] = chr_model
            # (the feature slider's digits, the first changing slowest: how many choices each of its options has; npc_numbers)
            model["feature_sizes"] = [len(tables.option_choices(chr_model, o, only_available=False)) for o in model["feature_options"]]
            if BASE_ONLY:
                model["merge"] = always_on_of(tables, chr_model, model)          # (the pieces themselves bring these back when it is off)
                model["overlays"], model["variants"], model["parts"], model["pickers"] = [], [], [], []
            else:
                model["merge"] = []
                model["overlays"] = overlays_of(tables, chr_model, model)
                model["variants"] = variants_of(tables, chr_model, model)
                model["parts"], model["pickers"] = parts_of(tables, chr_model, model)
            entry["models"][str(sex)] = model
        entry["replace_rows"] = races is None             # the ten of 3.3.5: their rows in the tables are replaced
        out["races"][str(race_id)] = entry
    return out


# --- the game's tables: change files (tools/apply_client.py) ----------------------------------------------------------------

TABLE_KINDS = {"CharSections": "iiiisssiii", "CharHairGeosets": "iiiiii", "CharacterFacialHairStyles": "iiiiiiii"}
ID_LOOKS = 3000000      # the ten races' new rows' ids in CharSections and CharHairGeosets: clear of every table the client has


def table_rows(looks):
    """The ten races' rows of the three tables, as the allied races' build_data.py makes theirs (names.py's paths)."""
    import names
    sections, hair, facial = [], [], []
    for entry in looks["races"].values():
        race = entry["race"]
        for sex, m in sorted(entry["models"].items()):
            sex = int(sex)
            for s in m["skins"]:
                c = s["index"]
                # (the second texture is the skin extra, which the game puts on the model's texture type 8: a model with fur has
                # one a skin, textures.py; the Forsaken's is the whole texture of today, m2.py's bony pieces)
                sections.append([race, sex, 0, names.skin(m, c), names.skin_extra(m, c) if m.get("skin_extra") or s.get("extra") else "", "", 17, 0, c])
                if s["pelvis"]:
                    sections.append([race, sex, 4, names.pelvis(m, c), names.torso(m, c) if s["torso"] else "", "", 17, 0, c])
            for fi, face in enumerate(m["faces"]):
                for s in m["skins"]:
                    fid = names.face_file(m, face, s)
                    for eye in m["eyes"]:
                        # 17 (0x11): a face of every class's, a death knight's too. 3.3.5's own faces are 1 (every class
                        # but a death knight) with a death knight's own faces beside them (5); today's game has no faces
                        # of a death knight's own, and with 1 the game counted NO face for a death knight of these races
                        # (CCharacterComponent::GetNumFacesForSkin: a death knight's rows need 0x4 or 0x10), so its face
                        # and skin could not be changed, and Wrath++'s creator stopped on the count (12 November 2026).
                        sections.append([race, sex, 1, names.face_lower(m, fid, eye), names.face_upper(m, eye), "", 17,
                                         names.face_variation(m, fi, eye["index"]), s["index"]])
            for h in m["hair"]:
                for hc in m["hair_colors"]:
                    # Texture2 is the scalp (ScalpLower, laid over the face's place): the hair's colour on the skin where
                    # the style is cut short
                    scalp = h.get("scalp", {}).get(str(hc["index"])) or h.get("scalp", {}).get("*")
                    sections.append([race, sex, 3, names.hair(m, hc["index"]), names.scalp(m, scalp) if scalp else "", "", 17,
                                     h["variation"], hc["index"]])
                if not m["hair_colors"]:
                    # A race without hair colours (the Worgen: the mane is the fur's colour, the skin extra) still needs a hair
                    # row a style: the game takes a style only if the table has it with the character's hair colour
                    # (CCharacterComponent::SetHairStyle, ComponentValidateBase), and the realm checks the same row. Colour 0,
                    # no texture of its own (ReplaceHairTexture leaves an empty name alone).
                    sections.append([race, sex, 3, "", "", "", 17, h["variation"], 0])
                hair.append([race, sex, h["variation"], h["geoset"], 0])
            for f in m["features"]:
                facial.append([race, sex, f["variation"]] + list(f["geosets"]))
    return sections, hair, facial


def looks_changes(looks, stock_dbc_dir):
    """The ten races' rows of the three tables as change files (tools/apply_client.py): every row of their race and sex
    dropped, theirs put. Applied to the client's own tables (an HD look's included) by the app, and to the server's by
    assemble. The facial table's glow column (geoset group 17: the night elves' eye glow) is the race's own, from
    [stock_dbc_dir]'s table."""
    import apply_client
    mine = sorted((entry["race"], int(sex)) for entry in looks["races"].values() if entry.get("replace_rows") for sex in entry["models"])
    if not mine:
        return {}
    only = {"races": {k: v for k, v in looks["races"].items() if v.get("replace_rows")}}
    sections, hair, facial = table_rows(only)
    with open(os.path.join(stock_dbc_dir, "CharacterFacialHairStyles.dbc"), "rb") as f:
        t = apply_client.Table(f.read())
    glow = {}
    for i in range(len(t.records)):
        glow.setdefault((t.get(i, 0), t.get(i, 1)), t.get(i, 7))

    def esc(v):
        return str(v).replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n")

    out = {}
    lines = ["types\t" + TABLE_KINDS["CharSections"]]
    lines += ["drop\t1\t%d\t2\t%d" % rs for rs in mine]
    lines += ["put\t" + "\t".join(esc(v) for v in [ID_LOOKS + i] + r) for i, r in enumerate(sections)]
    out["CharSections"] = "\n".join(lines) + "\n"
    lines = ["types\t" + TABLE_KINDS["CharHairGeosets"]]
    lines += ["drop\t1\t%d\t2\t%d" % rs for rs in mine]
    lines += ["put\t" + "\t".join(esc(v) for v in [ID_LOOKS + i] + r) for i, r in enumerate(hair)]
    out["CharHairGeosets"] = "\n".join(lines) + "\n"
    lines = ["types\t" + TABLE_KINDS["CharacterFacialHairStyles"]]
    lines += ["drop\t0\t%d\t1\t%d" % rs for rs in mine]
    lines += ["appendraw\t" + struct.pack("<8I", *(r[:7] + [glow.get((r[0], r[1]), 0)])).hex() for r in facial]
    out["CharacterFacialHairStyles"] = "\n".join(lines) + "\n"
    npc = npc_changes(only, stock_dbc_dir)
    if npc:
        out["CreatureDisplayInfoExtra"] = npc
    return out


# --- the creatures' looks (CreatureDisplayInfoExtra) -----------------------------------------------------------------------------
# A creature drawn with a race's model has a row there: its race, sex and 3.3.5's five numbers (skin, face, hair style, hair colour,
# facial hair), its items, and the name of a texture baked from all of it for the model 3.3.5 had. On the looks' models the baked
# face lies in the wrong place (m2.py: the head's layout is the converter's own), so Wrath++'s native mod has the game compose such
# a creature's skin as it does a player's (Native.cpp, "the creatures' skins"; Wrathpp\npc.txt says which races and sexes), from the
# row's five numbers. Those are 3.3.5's, and the looks' tables count otherwise (a face is a face and an eye colour, the feature
# slider several options at once, the Tauren's horns no longer their hair): the rule below turns them into the looks' own, in
# whatever rows the table has (the game's, an HD look's, Cataclysm's starting areas'), by race and sex.
EXTRA_KINDS = "iiiiiiiiiiiiiiiiiiiis"
EXTRA_RACE, EXTRA_SEX, EXTRA_SKIN, EXTRA_FACE, EXTRA_HAIR, EXTRA_COLOUR, EXTRA_FACIAL = 1, 2, 3, 4, 5, 6, 7
NPC_LISTED = 64         # the numbers written out one by one (3.3.5's own go to 24): any other takes what 0 takes
# 3.3.5's hair style slider where today's Hair Style is something else: the option of today's feature slider it became (the
# Tauren's horns: their hair is today's Foremane).
CLASSIC_HAIR = {(6, 0): "Horn Style", (6, 1): "Horn Style"}
# 3.3.5's feature slider where it is one option of today's feature slider, its choices in 3.3.5's order ("": nothing of today's
# slider: the Night Elf women's markings and the Tauren women's hair are not on it). Any other race and sex: today's features are
# matched by their geosets (3.3.5's beards, moustaches and sideburns kept their numbers).
CLASSIC_FEATURE = {(1, 1): "Piercings", (2, 1): "Earrings", (3, 1): "Earrings", (4, 1): "", (6, 0): "Facial Hair", (6, 1): "",
                   (7, 1): "Earrings", (8, 0): "Tusks", (8, 1): "Tusks", (10, 0): "Facial Hair", (10, 1): "Earrings", (11, 1): "Horns"}


def classic_tables(stock_dbc_dir):
    """3.3.5's own numbers, from the stock tables: {(race, sex): {"skins", "faces", "hair", "colours": how many, "facial": {variation:
    its geosets (groups 1, 3, 2)}}}."""
    import apply_client
    out = {}

    def entry(race, sex):
        return out.setdefault((race, sex), {"skins": 0, "faces": 0, "hair": 0, "colours": 0, "facial": {}})

    path = os.path.join(stock_dbc_dir, "CharSections.dbc")
    t = apply_client.Table(struct.pack("<4s4I", b"WDBC", 0, 10, 40, 1) + b"\0")     # (no table: no race of 3.3.5's is known)
    if os.path.exists(path):
        with open(path, "rb") as f:
            t = apply_client.Table(f.read())
    for i in range(len(t.records)):
        race, sex, section, variation, colour = t.get(i, 1), t.get(i, 2), t.get(i, 3), t.get(i, 8), t.get(i, 9)
        e = entry(race, sex)
        if section == 0:
            e["skins"] = max(e["skins"], colour + 1)
        elif section == 1:
            e["faces"] = max(e["faces"], variation + 1)
        elif section == 3:
            e["hair"], e["colours"] = max(e["hair"], variation + 1), max(e["colours"], colour + 1)
    with open(os.path.join(stock_dbc_dir, "CharacterFacialHairStyles.dbc"), "rb") as f:
        t = apply_client.Table(f.read())
    for i in range(len(t.records)):
        entry(t.get(i, 0), t.get(i, 1))["facial"].setdefault(t.get(i, 2), (t.get(i, 3), t.get(i, 4), t.get(i, 5)))
    return out


def npc_numbers(m, race, sex, classic):
    """3.3.5's five numbers of a creature of [m]'s race and sex as the looks' tables count them:

        {"skin", "face", "colour", "hair": {3.3.5's number: the looks'}, "facial": {(3.3.5's hair style, facial hair): the looks'}}

    for every number to NPC_LISTED (and 3.3.5's own, [classic]: classic_tables' entry, or None for a race 3.3.5 hasn't). How: Shadowlands
    made 3.3.5's variations its choices one after the other (their ids in a row from the first: a race's 15 skins are choices
    N to N+14, the creatures' own and the death knights' among them), so 3.3.5's number n is the choice n after the first, and the
    looks' number is that choice's place in the looks. A choice the looks leave out (the creatures' own skins: a player can't pick
    them) and a number 3.3.5 hasn't take the place of the number as many back as the looks' first run is long (a death knight's
    face its face, a creature's skin one of the players'). A face is the face with the first eye colour. The feature slider:
    CLASSIC_FEATURE and CLASSIC_HAIR, else the looks' feature whose geosets are 3.3.5's (3.3.5's "none" is geoset 1, today's 0)."""
    def places(entries, number):
        ids = {}
        for i, e in enumerate(entries):
            if "choice" in e:
                ids.setdefault(int(e["choice"]), number(e, i))
        if not ids:
            return lambda n: 0
        first = min(ids)
        run = 0
        while first + run in ids:
            run += 1
        return lambda n: ids[first + n] if first + n in ids and n < (limit[0] or n + 1) else ids[first + n % run]

    limit = [0]
    listed = range(NPC_LISTED)
    out = {}
    for field, entries, number, count in (("skin", m["skins"], lambda e, i: e.get("index", i), "skins"),
                                          ("face", m["faces"], lambda e, i: i * max(1, len(m["eyes"])), "faces"),
                                          ("hair", m["hair"], lambda e, i: e.get("variation", i), "hair"),
                                          ("colour", m["hair_colors"], lambda e, i: e.get("index", i), "colours")):
        limit[0] = classic[count] if classic and classic["faces"] else 0     # (a race 3.3.5 hasn't: every choice in the run counts)
        place = places(entries, number)
        out[field] = {n: place(n) for n in listed}
    # the feature slider: its digits (the first option changing slowest)
    options, sizes = list(m.get("feature_options", [])), list(m.get("feature_sizes", []))
    total = 1
    for size in sizes:
        total *= size
    if len(sizes) != len(options) or total != len(m["features"]) or not total:
        options, sizes = [], []                            # (no digits known: every creature takes the first feature)

    def feature(digits):
        n = 0
        for k, size in enumerate(sizes):
            n = n * size + (digits.get(k, 0) % size)
        return n

    def by_geosets(wanted):
        best, score = 0, -1
        for f in m["features"]:
            got = sum(1 for a, b in zip(f["geosets"][:3], wanted) if a == b) * 4 - sum(1 for g in f["geosets"][:3] if g)
            if got > score:
                best, score = f["variation"], got
        return best

    hair_option = CLASSIC_HAIR.get((race, sex))
    own = CLASSIC_FEATURE.get((race, sex))
    facial_rows = (classic or {}).get("facial", {})
    facial = {}
    hairs = range(NPC_LISTED // 2) if hair_option in options else (0,)     # (two numbers a key: half as far each)
    for h in hairs:
        for n in (range(NPC_LISTED // 2) if hair_option in options else listed):
            digits = {}
            if hair_option in options:
                digits[options.index(hair_option)] = h
            if own is None and not hair_option:
                if n in facial_rows and m["features"]:
                    facial[(h, n)] = by_geosets([0 if g == 1 else g for g in facial_rows[n]])
                else:
                    facial[(h, n)] = 0
                continue
            if own and own in options:
                digits[options.index(own)] = n
            facial[(h, n)] = feature(digits) if sizes else 0
    out["facial"] = facial
    out["hair_in_features"] = hair_option in options
    if out["hair_in_features"]:
        out["hair"] = {n: 0 for n in listed}                # (3.3.5's hair style went to the feature slider: today's first hair)
    return out


def npc_changes(looks, stock_dbc_dir):
    """The rule for CreatureDisplayInfoExtra (a change file's text, apply_client.py's `map`), for the races and sexes whose rows the
    looks replace; "" where there are none."""
    classic = classic_tables(stock_dbc_dir)
    lines = []
    for entry in sorted((e for e in looks["races"].values() if e.get("replace_rows")), key=lambda e: e["race"]):
        for sex, m in sorted(entry["models"].items()):
            race, sex = entry["race"], int(sex)
            n = npc_numbers(m, race, sex, classic.get((race, sex)))
            where = "%d=%d,%d=%d" % (EXTRA_RACE, race, EXTRA_SEX, sex)

            def line(source, to, pairs, default):
                keys = sorted(pairs)
                return "\t".join(["map", where, source, str(to), str(default)] + [
                    "%s=%d" % (",".join(str(k) for k in key) if isinstance(key, tuple) else key, pairs[key]) for key in keys if pairs[key] != default])

            # (the feature first: it reads 3.3.5's hair style, which the hair's line then replaces)
            if n["hair_in_features"]:
                lines.append(line("%d,%d" % (EXTRA_HAIR, EXTRA_FACIAL), EXTRA_FACIAL, n["facial"], n["facial"][(0, 0)]))
            else:
                lines.append(line(str(EXTRA_FACIAL), EXTRA_FACIAL, {k[1]: v for k, v in n["facial"].items()}, n["facial"][(0, 0)]))
            lines.append(line(str(EXTRA_SKIN), EXTRA_SKIN, n["skin"], n["skin"][0]))
            lines.append(line(str(EXTRA_FACE), EXTRA_FACE, n["face"], n["face"][0]))
            lines.append(line(str(EXTRA_HAIR), EXTRA_HAIR, n["hair"], n["hair"][0]))
            lines.append(line(str(EXTRA_COLOUR), EXTRA_COLOUR, n["colour"], n["colour"][0]))
    if not lines:
        return ""
    return "\n".join(["# CreatureDisplayInfoExtra: the creatures of the looks' races, 3.3.5's five numbers made the looks' (sl_looks.py npc_changes)",
                      "types\t" + EXTRA_KINDS] + lines) + "\n"


def write_npc_list(looks, client):
    """Wrathpp/npc.txt in [client] (the game's patch): the races and sexes whose model is the looks' ("race<TAB>sex" a line), for the
    native mod: a creature of one of them has its skin composed, not its baked texture put on. The ten races' run and the allied
    races' write the same file: the lines of races this one doesn't have are kept."""
    mine = {}
    for entry in looks["races"].values():
        for sex in entry["models"]:
            mine[(int(entry["race"]), int(sex))] = True
    path = os.path.join(client, "Wrathpp", "npc.txt")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for l in f:
                parts = l.split()
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    mine.setdefault((int(parts[0]), int(parts[1])), True)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("# Wrath++ (sl_looks.py): race, sex of the looks' models; their creatures' skins are composed (Native.cpp)\n")
        f.write("".join("%d\t%d\n" % key for key in sorted(mine)))
    return path


# The character tables whose rows the looks replace race by race (drop, then put): the first dir's (the looks' own) go last, after
# every other dir's, so that a module that makes a race the looks redo (mod-worgen-goblin's Worgen and Goblins: Cataclysm's models
# and textures) has its rows of that race dropped and the looks' put instead; its other races' rows stay.
# CreatureDisplayInfoExtra's too: the looks' rule (npc_changes) is for every creature of a race, the ones the other dirs put (Cataclysm's
# starting areas, the Worgen and Goblins) among them, and after the creatures' own races have moved off the ids the looks' races take.
LOOKS_LAST = ("CharSections.txt", "CharHairGeosets.txt", "CharacterFacialHairStyles.txt", "CreatureDisplayInfoExtra.txt")


def merge_changes(out_dir, *dirs):
    """The change files of [dirs] (a table's, in the order of the dirs; LOOKS_LAST's of the first dir after the others') one file a
    table in [out_dir]."""
    os.makedirs(out_dir, exist_ok=True)
    merged, last = {}, {}
    for at, d in enumerate(dirs):
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if name.endswith(".txt"):
                with open(os.path.join(d, name), encoding="utf-8") as f:
                    text = f.read().rstrip("\n")
                if at == 0 and name in LOOKS_LAST:
                    last[name] = text
                else:
                    merged.setdefault(name, []).append(text)
    for name, text in last.items():
        merged.setdefault(name, []).append(text)
    for name, parts in merged.items():
        with open(os.path.join(out_dir, name), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(parts) + "\n")
    return sorted(merged)


NARRATIONS = {"voidelf": ("voidelf_intro.mp3", "VoidElfNarration.mp3"), "nightborne": ("nightborne_intro.mp3", "NightborneNarration.mp3"),
              "lightforged": ("lightforged_intro.mp3", "LightforgedDraeneiNarration.mp3"),
              "zandalari": ("zandalari_intro.mp3", "ZandalariTrollNarration.mp3")}
# wago.tools' music of the Highmountain's flythrough (file id), for the race that has no narration of the user's.
NARRATION_FILES = {"highmountain": (1862320, "HighmountainTaurenNarration.mp3")}
# The Dark Troll's: a narration made for it (an AI voice made like the Zandalari intro's, the user's: realm/warcraft/wrathpp/data/darktroll_intro.mp3).
OWN_NARRATIONS = {"darktroll": (os.path.join(os.path.dirname(HERE), "data", "darktroll_intro.mp3"), "DarkTrollNarration.mp3")}


def narrations(keys, read, client, log=print):
    """The intros' narrations into OUT/client/Sound/CinematicVoices: the allied races module's own MP3s (the user's) where it has
    them, else wago.tools' file by its id made the game's MP3 format (44.1 kHz, no tags)."""
    import subprocess
    folder = os.path.join(client, "Sound", "CinematicVoices")
    os.makedirs(folder, exist_ok=True)
    written = []
    for key in keys:
        if key in OWN_NARRATIONS:
            with open(OWN_NARRATIONS[key][0], "rb") as f, open(os.path.join(folder, OWN_NARRATIONS[key][1]), "wb") as out:
                out.write(f.read())
            written.append("Sound\\CinematicVoices\\" + OWN_NARRATIONS[key][1])
        elif key in NARRATIONS:
            src = os.path.join(os.path.dirname(ALLIED_TOOLS), "data", "client", NARRATIONS[key][0])
            with open(src, "rb") as f, open(os.path.join(folder, NARRATIONS[key][1]), "wb") as out:
                out.write(f.read())
            written.append("Sound\\CinematicVoices\\" + NARRATIONS[key][1])
        elif key in NARRATION_FILES:
            fid, name = NARRATION_FILES[key]
            raw, part = os.path.join(folder, "%d.src" % fid), os.path.join(folder, name + ".part")
            with open(raw, "wb") as out:
                out.write(read(fid))
            try:
                r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-ar", "44100", "-ac", "2", "-b:a", "128k",
                                    "-id3v2_version", "0", "-write_id3v1", "0", "-f", "mp3", part], capture_output=True)
                if r.returncode or not os.path.getsize(part):
                    raise RuntimeError("%s couldn't be converted: %s" % (name, r.stderr.decode(errors="replace").strip()))
                os.replace(part, os.path.join(folder, name))
            finally:
                for tmp in (raw, part):
                    if os.path.exists(tmp):
                        os.remove(tmp)
            written.append("Sound\\CinematicVoices\\" + name)
    return written


# wago.tools' race icons (the allied races' achievement icons), the creation screen's pictures of the new races (tokens as
# app/src/main/assets/wrathpp/WrathppAlliedRaces.lua has them): file id.
RACE_ICONS = {"VOIDELF": 1786422, "LIGHTFORGEDDRAENEI": 1786420, "DARKIRONDWARF": 1851464, "MECHAGNOME": 3208032, "HIGHELF": 131152,
              "NIGHTBORNE": 1786421, "ZANDALARITROLL": 1851465, "DARKTROLL": 1851465, "HIGHMOUNTAINTAUREN": 1786419, "VULPERA": 3208033, "MAGHARORC": 1989713}


# The High Elf wears the Blood Elf man's portrait, the creator's own (the Shadowlands atlas, file 131152, its cell at ICON_CROPS:
# left, top, right, bottom), with the fel green taken out: the irises (saturated green, hue 75 degrees and up) become blue, brighter
# and stronger so they read at 64 x 64, and the green-olive cast around the eyes, on the nose, mouth and chin (hue 36 to 75 degrees
# in the darker pixels; the blond hair is brighter, and the browner olive of the face's lower middle) goes back to the skin's orange (hue 20).
ICON_CROPS = {"HIGHELF": (1027, 256, 1284, 509)}
BLUE_EYES = ("HIGHELF",)


def blue_eyes(rgba):
    """A copy of the 64 x 64 RGBA icon with the green irises turned blue and the green cast on the skin turned to skin."""
    import numpy as np
    from PIL import Image
    hsv = np.asarray(Image.fromarray(rgba[..., :3]).convert("HSV")).astype(float)
    hue = hsv[..., 0] * 360 / 255
    sat = hsv[..., 1] / 255
    val = hsv[..., 2] / 255
    iris = (hue >= 75) & (hue <= 175) & (sat > 0.25)
    cast = (hue >= 36) & (hue < 75) & (val < 0.8) & (sat > 0.25)
    # the olive of the nose, mouth and chin is a brown a few degrees from the skin's: inside that part of the face only
    face = np.zeros(hue.shape, dtype=bool)
    face[30:61, 20:47] = True
    cast |= face & (hue >= 26) & (val < 0.88) & (sat > 0.3)
    hsv[..., 0][iris] = 212 * 255 / 360
    hsv[..., 1][iris] = np.minimum(255, hsv[..., 1][iris] * 1.15)
    hsv[..., 2][iris] = np.minimum(255, hsv[..., 2][iris] * 1.1)
    hsv[..., 0][cast] = 18 * 255 / 360
    out = rgba.copy()
    rgb = np.asarray(Image.fromarray(np.rint(hsv).astype(np.uint8), "HSV").convert("RGB"))
    changed = iris | cast
    out[..., :3][changed] = rgb[changed]
    return out


def race_icons(read, client, log=print):
    """The race icons as 64 x 64 3.3.5 textures: Interface/Glues/CharacterCreate/WrathppRaces/<TOKEN>.blp."""
    import blp
    import numpy as np
    from PIL import Image
    folder = os.path.join(client, "Interface", "Glues", "CharacterCreate", "WrathppRaces")
    os.makedirs(folder, exist_ok=True)
    written = []
    for token, fid in sorted(RACE_ICONS.items()):
        rgba = blp.read(read(fid))
        if token in ICON_CROPS:
            left, top, right, bottom = ICON_CROPS[token]
            rgba = np.ascontiguousarray(rgba[top:bottom, left:right])
        img = Image.fromarray(rgba).convert("RGBA").resize((64, 64), Image.LANCZOS)
        if token in BLUE_EYES:
            img = Image.fromarray(blue_eyes(np.asarray(img)))
        with open(os.path.join(folder, token + ".blp"), "wb") as f:
            f.write(blp.write_palette(np.ascontiguousarray(np.asarray(img)), alpha=True))
        written.append("Interface\\Glues\\CharacterCreate\\WrathppRaces\\%s.blp" % token)
    return written


def allied_game_ids():
    """The allied races' race ids in the game, by key (tools/races_profile.py's KEY: the ids below 22 the client can hold). That file is
    run by the allied races' build_data with names it gives it; its ids and keys are read from its source."""
    lines = open(os.path.join(HERE, "races_profile.py"), encoding="utf-8").read().splitlines()
    import re
    # (the race-id lines: "NAME = 9" or "A, B, ... = range(12, 21)", each before KEY)
    wanted = [l.split("#")[0] for l in lines[:next(n for n, l in enumerate(lines) if l.startswith("KEY ="))]
              if re.match(r"^[A-Z][A-Z_, ]* = (\d+|range\(\d+, \d+\))\s*(#.*)?$", l)]
    i = next(n for n, l in enumerate(lines) if l.startswith("KEY ="))
    wanted.append(lines[i])
    while not lines[i].rstrip().endswith("}"):
        i += 1
        wanted.append(lines[i])
    ns = {}
    exec("\n".join(wanted), {}, ns)
    return {key: race for race, key in ns["KEY"].items()}


def drawn_looks(looks):
    """The races whose parts the add-on draws, as write_parts_table and registry_parts take them: the ten as they are (their own race
    id), the allied races by the race id the game gives them. The High Elf's models are the Void Elf's ("alias_of")."""
    game = allied_game_ids()
    out = {}
    for key, entry in looks["races"].items():
        if entry.get("replace_rows"):
            out[key] = entry
        elif key in game:
            out[str(game[key])] = dict(entry, race=game[key])
    return {"races": out}


def load_looks(path):
    """A looks file: sl_looks.py races' ({"races": ...}) or the allied races' data (sl_looks.py data: the races by key)."""
    with open(path) as f:
        looks = json.load(f)
    looks = looks if "races" in looks and isinstance(looks["races"], dict) and "build" in looks else {"races": looks}
    return strip_extras(looks)           # (an older looks file with pieces: BASE_ONLY writes none of them)


def alias_target(looks, looks_path, entry):
    """The entry [entry] ("alias_of") has its files of: in [looks], else in the ten races' looks.json beside [looks_path] (the Dark Troll's
    "8" is the Troll's), else None."""
    key = entry.get("alias_of")
    if not key:
        return None
    if key in looks["races"]:
        return looks["races"][key]
    ten = os.path.join(os.path.dirname(os.path.abspath(looks_path)), "looks.json")
    if os.path.abspath(ten) != os.path.abspath(looks_path) and os.path.isfile(ten):
        return load_looks(ten)["races"].get(key)
    return None


def package(looks_path, cache, dbc_dir, out_dir, log=print):
    """The models, textures, voices and narrations of [looks_path]'s races into OUT/client (the game's paths), and the ten
    races' rows as change files into OUT/changes. A race with "alias_of" (the High Elf) has the other's files."""
    import check_m2
    import m2
    import package as allied_package
    import textures
    looks = load_looks(looks_path)
    read = allied_package.cached(cache, allied_package.wago)
    specs = {}
    for entry in looks["races"].values():
        for model in entry["models"].values():
            specs.update(model.get("synth", {}))
    if specs:                                            # (the Dark Troll's tinted colours: made-up file ids, made when asked for)
        import dark_troll
        read = dark_troll.Resolver(read, specs)
    client = os.path.join(out_dir, "client")
    written = []
    fallbacks = {}                                       # model name -> the (id, variation) of its sequences drawn as another animation
    for key, entry in looks["races"].items():
        if entry.get("alias_of"):
            continue
        for sex, model in sorted(entry["models"].items()):
            # the model's own files (its .m2, .skin, skeleton, animations): the newest copies, or one retail build's where the newest
            # don't fit together (m2.MixedBuilds: the Blood Elf man's), for the model and every piece made from it
            mread = read
            try:
                written += m2.convert(mread, dict(model, geosets=None, retry_on_fallback=True), client, log)
            except m2.MixedBuilds as mixed:
                # (also a model whose animation files fit none of its skeletons, m2.FallbackAnimations: 385 sequences of 17 models played
                # as another animation, the emotes, sitting and sleeping among them, until their files were fetched of one build)
                log("%s; its files fetched at %s" % (mixed, allied_package.PINNED_BUILD))
                mread = allied_package.cached(os.path.join(cache, allied_package.PINNED_BUILD), allied_package.wago_at(allied_package.PINNED_BUILD))
                written += m2.convert(mread, dict(model, geosets=None), client, log)
            fallbacks[model["name"]] = list(m2.last_fallbacks)
            model_path = os.path.join(client, model["folder"].replace("\\", "/"), model["name"] + ".m2")
            problems = check_m2.check(model_path)
            if problems:
                raise ValueError("%s: %s" % (model["name"], "; ".join(problems[:20])))
            layout_path = model_path[:-3] + ".layout.json"
            with open(layout_path) as f:
                layout = json.load(f)
            os.remove(layout_path)
            model["skin_extra"] = bool(layout.get("extra"))       # its skin rows name their extra (table_rows)
            if int(sex) == 1:
                # a woman's soft body: four bones of the model's own, weighted at the bottom of the chest's and the seat's curve
                # (soft_weights.py; until 18 November 2026 the retail breast bones found by their height, sl_parts.soft_body, which
                # on eleven races were bones of the face)
                import soft_weights
                # (a fault in this step must not stop the whole package: the model as it was is put back and the woman has no soft
                # body of her own this release)
                with open(model_path, "rb") as f:
                    before_soft = f.read()
                try:
                    soft = soft_weights.soften(model_path, log=log)
                    if soft:
                        problems = check_m2.check(model_path)
                        if problems:
                            raise ValueError("%s with its soft body: %s" % (model["name"], "; ".join(problems[:20])))
                        model["soft"] = soft
                except Exception as error:     # noqa: BLE001
                    log("%s: no soft body this release (%s)" % (model["name"], error))
                    with open(model_path, "wb") as f:
                        f.write(before_soft)
                    model.pop("soft", None)
            written += textures.build(read, model, layout, client, log)
            if model.get("overlays"):
                import sl_parts
                written += sl_parts.head_shell(mread, model, client, log)
                if any(c.get("body") for o in model["overlays"] for c in o["choices"]):
                    written += sl_parts.body_shell(mread, model, client, log)
            for variant in model.get("variants", []):
                import sl_parts
                for k, choice in enumerate(variant["choices"], 1):
                    if (choice["file"] or choice.get("geosets")) and not (k == 1 and variant.get("geoset")):     # (the first choice of a geoset variant is the model as it is)
                        files = sl_parts.variant_model(mread, model, variant, k, choice, client, log)
                        written += files
                        if model.get("soft"):                         # her variants' models have her soft body: the same bones at the same places
                            import soft_weights
                            for path in files:
                                if path.lower().endswith(".m2"):
                                    full = path if os.path.isabs(path) else os.path.join(client, path.replace("\\", "/"))
                                    if os.path.isfile(full):
                                        try:
                                            got = soft_weights.soften(full, log=log)
                                        except Exception as error:     # noqa: BLE001
                                            got = None
                                            log("%s: its soft body failed (%s)" % (os.path.basename(full), error))
                                        if not got or [b[0] for b in got["bones"]] != [b[0] for b in model["soft"]["bones"]]:
                                            log("%s: its soft bones are not %s's (%s)" % (os.path.basename(full), model["name"], got and [b[0] for b in got["bones"]]))
            if model.get("parts"):
                import sl_parts
                model["part_types"] = {}
                for part in model["parts"]:
                    files, types = sl_parts.geoset_part(mread, model, part, client, log)
                    written += files
                    model["part_types"][part["name"]] = sorted(types)
                written += sl_parts.write_pickers(read, model, client, log)
            if model.get("overlays"):
                # the pictures laid over the head and body (eyebrows, makeup, scars...): every model with overlays, pieces or none (inside
                # the pieces' step they were written only for a model that has pieces: the Human, Orc and Dwarf women's, the Trolls',
                # the Dark Iron man's were not in the package, and the game drew them bright green)
                import sl_parts
                written += sl_parts.write_overlays(mread, model, layout, client, log)
            for path, fid in model["hardcoded_files"].items():
                full = os.path.join(client, path.replace("\\", "/"))
                os.makedirs(os.path.dirname(full), exist_ok=True)
                with open(full, "wb") as out:
                    out.write(read(fid))
                written.append(path)
        if entry.get("voices"):
            written += allied_package.voice_files(entry, read, client, log)
    written += narrations([e for e in looks["races"] if e in NARRATIONS or e in NARRATION_FILES or e in OWN_NARRATIONS], read, client, log)
    if any(e.get("alias_of") or k in KEYS.values() for k, e in looks["races"].items()):
        written += race_icons(read, client, log)
    changes = looks_changes(looks, dbc_dir)
    os.makedirs(os.path.join(out_dir, "changes"), exist_ok=True)
    for name, text in changes.items():
        with open(os.path.join(out_dir, "changes", name + ".txt"), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    ten = drawn_looks(looks)
    # (the High Elf is the Void Elf's files: the textures its pieces take are the Void Elf's)
    # (and the Dark Troll's the Troll's, one of the ten: in looks.json beside this file, whose package step ran first and saved its pieces' types)
    for entry in looks["races"].values():
        other_race = alias_target(looks, looks_path, entry)
        if other_race:
            for sex, m in entry["models"].items():
                other = other_race["models"].get(sex, {})
                if other.get("part_types"):
                    m["part_types"] = other["part_types"]
    if ten["races"]:
        import sl_parts
        ids_path = os.path.join(os.path.dirname(HERE), "registry", "parts_ids.json")
        ids = json.load(open(ids_path)).get("keys", {}) if os.path.exists(ids_path) else {}
        sl_parts.write_parts_table(ten, client, ids)
        written.append("Wrathpp\\parts.txt")
        write_npc_list(ten, client)
        written.append("Wrathpp\\npc.txt")
        # (the textures the model pieces take, which the creator's options step needs: put in the looks file)
        if any(m.get("part_types") or m.get("soft") for e in ten["races"].values() for m in e["models"].values()):
            with open(looks_path) as f:
                saved = json.load(f)
            races = saved["races"] if "races" in saved and "build" in saved else saved
            for key, e in looks["races"].items():
                for sex, m in e["models"].items():
                    if m.get("part_types") and key in races:
                        races[key]["models"][sex]["part_types"] = m["part_types"]
            with open(looks_path, "w") as f:
                json.dump(saved, f, indent=1, sort_keys=True)
    check_fallbacks(fallbacks, dbc_dir, out_dir, log)
    missing = verify(looks, out_dir)
    if missing:
        raise ValueError("%d files the tables name are not in the package, e.g. %s" % (len(missing), ", ".join(missing[:5])))
    listing = os.path.join(out_dir, "looks.files")
    if os.path.exists(listing):                      # (the ten's and the allied races' runs share an OUT)
        with open(listing) as f:
            written += [line.rstrip("\n") for line in f if line.strip()]
    with open(listing, "w") as out:
        out.write("".join(p + "\n" for p in sorted(set(written))))
    log("looks: %d files" % len(set(written)))


ANIM_BASELINE = os.path.join(os.path.dirname(HERE), "data", "anim_fallbacks.json")


def game_animations(dbc_dir):
    """The animation ids 3.3.5 knows (its AnimationData): the ones a player's model can be asked to play, all of them for a character."""
    path = os.path.join(dbc_dir, "AnimationData.dbc")
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        data = f.read()
    count, _fields, size = struct.unpack_from("<3I", data, 4)
    return {struct.unpack_from("<I", data, 20 + i * size)[0] for i in range(count)}


def fallback_counts(fallbacks, known):
    """Per model, how many of its sequences play as another animation that a player meets (an id 3.3.5 knows: the animation ids
    of the sequences m2.convert drew as another because their files fit none of the model's skeletons)."""
    return {name: sum(1 for anim, _var in keys if known is None or anim in known) for name, keys in sorted(fallbacks.items())}


def check_fallbacks(fallbacks, dbc_dir, out_dir, log=print, baseline_path=None):
    """The CI guard on animations: the count per model of gameplay-relevant sequences that fall back may not rise above the
    baseline (data/anim_fallbacks.json: model name -> count, a model not in it 0). Writes the run's counts to OUT/anim_fallbacks.json
    (copy it over the baseline to lower it)."""
    counts = fallback_counts(fallbacks, game_animations(dbc_dir))
    with open(os.path.join(out_dir, "anim_fallbacks.json"), "w") as f:
        json.dump(counts, f, indent=1, sort_keys=True)
    path = baseline_path or ANIM_BASELINE
    baseline = json.load(open(path)) if os.path.exists(path) else {}
    log("animations drawn as another (gameplay ids): %d in %d models" % (sum(counts.values()), sum(1 for n in counts.values() if n)))
    worse = ["%s: %d (baseline %d; e.g. %s)" % (name, n, baseline.get(name, 0), ", ".join("%d-%d" % k for k in fallbacks[name][:4]))
             for name, n in counts.items() if n > baseline.get(name, 0)]
    if worse:
        raise ValueError("animation fallbacks rose (a skeleton and its .anim files of two builds?): " + "; ".join(worse))
    return counts


def verify(looks, out_dir):
    """The files the ten races' new rows and every race's models name that the package lacks (a table row naming no file is
    a white character)."""
    client = os.path.join(out_dir, "client")
    have = set()
    for root, _, files in os.walk(client):
        for f in files:
            have.add(os.path.relpath(os.path.join(root, f), client).replace("/", "\\").lower())
    named = set()
    ten = {"races": {k: v for k, v in looks["races"].items() if v.get("replace_rows")}}
    if ten["races"]:
        sections, hair, facial = table_rows(ten)
        named |= {r[3] for r in sections} | {r[4] for r in sections} | {r[5] for r in sections}
        named.discard("")
    for entry in looks["races"].values():
        for m in entry["models"].values():
            named.add(m["folder"] + "\\" + m["name"] + ".m2")
    # every file the add-on's parts table names (the pieces' models, the pictures over the head and body, skins, colours): a picture
    # missing from the package is drawn bright green
    parts = os.path.join(client, "Wrathpp", "parts.txt")
    if os.path.exists(parts):
        with open(parts, encoding="utf-8") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                for field in line.rstrip("\n").split("\t")[1:]:
                    if "\\" in field and field.lower().endswith((".blp", ".m2")) and "%" not in field:
                        named.add(field)
    # every animation a model keeps in a file of its own (3.3.5: <Model>NNNN-VV.anim): one the package lacks is read from the HD pack's
    # files of that name, made for another skeleton, and the character is drawn torn
    import re
    import struct
    for entry in looks["races"].values():
        for m in entry["models"].values():
            folder = os.path.join(client, m["folder"].replace("\\", "/"))
            if not os.path.isdir(folder):
                continue
            # the model and its variants (<Model>V2.m2: the Orc man's Upright, a woman's variants)
            for f in sorted(os.listdir(folder)):
                stem = f[:-3]
                if not f.lower().endswith(".m2") or not re.fullmatch(re.escape(m["name"]) + r"(V\d+)?", stem, re.I):
                    continue
                with open(os.path.join(folder, f), "rb") as fh:
                    data = fh.read()
                if data[:4] != b"MD20":
                    continue
                count, at = struct.unpack_from("<II", data, 28)
                for i in range(count):
                    sid, var = struct.unpack_from("<HH", data, at + i * 64)
                    if not struct.unpack_from("<I", data, at + i * 64 + 12)[0] & 0x20:
                        named.add("%s\\%s%04d-%02d.anim" % (m["folder"], stem, sid, var))
    return sorted(n for n in named if n.lower() not in have)


def assemble(stock_dbc_dir, out_dir, change_dirs):
    """OUT/changes: the change files of [change_dirs] merged a table (the ten races' looks, the allied races'); OUT/dbc: the
    server's tables, the stock ones with all of them applied. (The client's are made by the app from its own.)"""
    import apply_client
    names = merge_changes(os.path.join(out_dir, "changes"), *change_dirs)
    os.makedirs(os.path.join(out_dir, "dbc"), exist_ok=True)
    for name in names:
        table_name = name[:-4]
        path = os.path.join(stock_dbc_dir, table_name + ".dbc")
        if not os.path.exists(path):
            continue                                       # (a table the server doesn't read)
        with open(path, "rb") as f:
            table = apply_client.Table(f.read())
        with open(os.path.join(out_dir, "changes", name), encoding="utf-8") as f:
            apply_client.apply(table, f.read())
        if table_name == "CharSections":
            apply_client.sort_char_sections(table)
        with open(os.path.join(out_dir, "dbc", table_name + ".dbc"), "wb") as f:
            f.write(table.write())
    print("assembled %d tables" % len(names))
    return 0


def fetch(csv_dir):
    import sl_inventory
    saved = sl_inventory.TABLES
    try:
        sl_inventory.TABLES = tuple(saved) + TABLES_MORE
        sl_inventory.fetch(csv_dir)
    finally:
        sl_inventory.TABLES = saved


# The allied races' keys in the races data (the allied races module's own for its four).
KEYS = {27: "nightborne", 28: "highmountain", 29: "voidelf", 30: "lightforged", 31: "zandalari",
        34: "darkiron", 35: "vulpera", 36: "maghar", 37: "mechagnome"}


def high_elf(void):
    """The High Elf (the Alliance's, built on the Void Elf's body): the Void Elf's models with only the skins and faces of the
    high elf kind (today's Void Elf tables carry both), the skins numbered from 0 (their files keep the Void Elf's numbers:
    names.py's "file_index"). Its files are the Void Elf's: nothing of its own to convert ("alias_of")."""
    import copy
    out = copy.deepcopy(void)
    out["alias_of"] = "voidelf"
    for sex, m in out["models"].items():
        void_skins = {s["index"] for s in m["skins"] if s["index"] < 6}
        keep = [s for s in m["skins"] if s["index"] not in void_skins]
        faces = [f for f in m["faces"] if f["skins"] and not set(f["skins"]) <= void_skins]
        m["file_index"] = {str(j): s["index"] for j, s in enumerate(keep)}
        m["skins"] = [dict(s, index=j) for j, s in enumerate(keep)]
        m["base_skins"] = len(keep)
        m["faces"] = faces
        m["model_path"] = m["folder"] + "\\" + m["name"] + ".mdx"
    return out


def dark_troll_entry(troll, night_elf, choice_rows=None):
    """The Dark Troll (the Alliance's: the Night Elves' ancestors' kin, warcraft.wiki.gg/wiki/Dark_troll): the Troll's body built under its own
    folder ([troll]: build_races of ChrModels 15 and 16 named "DarkTroll": its own model and texture files, the Troll's by their content), with the
    Night Elf's skin and hair colours and the dark trolls' own skins added (dark_troll.py: made-up file ids and their specs, the creator's extra
    choices). [choice_rows]: today's choices by id, for the swatches of the borrowed colours."""
    import copy
    import dark_troll
    out = copy.deepcopy(troll)
    out["name"] = "DarkTroll"
    out["replace_rows"] = False
    for sex, m in out["models"].items():
        # (each sex its own range of made-up ids: package() merges the sexes' specs by id, and both counted up from SYNTH, so the man's
        # skin 13 on was made from the woman's spec of the same id, a face picture for a body: the phone's white torso, black arms)
        specs, extra = dark_troll.extend(m, night_elf["models"][sex], first_id=dark_troll.SYNTH + int(sex) * 1000000)
        for row in extra["Skin Color"] + extra["Hair Color"]:
            if choice_rows and row["ID"] in choice_rows:
                row["SwatchColor_0"] = choice_rows[row["ID"]].get("SwatchColor_0", "0")
                row["SwatchColor_1"] = choice_rows[row["ID"]].get("SwatchColor_1", "0")
        for row, (_, rgb) in zip(extra["Skin Color"][-len(dark_troll.OWN_SKINS):], dark_troll.OWN_SKINS):
            row["SwatchColor_0"] = str(rgb[0] << 16 | rgb[1] << 8 | rgb[2])
        m["synth"] = specs
        m["extra_choices"] = extra
    return out


def races_data(csv_dir, out_path):
    """The races data (the format of the allied races module's data/retail/races.json: models, voices, names) for the ten
    allied races and the High Elf: what Wrath++'s race wiring (tools/races_profile.py, the allied races' build_data.py) reads."""
    looks = build_races(csv_dir, ALLIED)
    tables = Tables(csv_dir)
    data = {}
    for race_id, entry in looks["races"].items():
        race_id = int(race_id)
        key = KEYS[race_id]
        data[key] = {"race": race_id, "name": entry["name"], "models": entry["models"],
                     "voices": allied.voices(tables, race_id),
                     "names": [{"name": n["Name"], "sex": int(n["Sex"])} for n in tables.names if n["RaceID"] == str(race_id)]}
    he = high_elf(data["voidelf"])
    he["name"] = "HighElf"
    he["race"] = 10                                      # its voices and names are the Blood Elves'
    he["voices"] = allied.voices(tables, 10)
    he["names"] = [{"name": n["Name"], "sex": int(n["Sex"])} for n in tables.names if n["RaceID"] == "10"]
    data["highelf"] = he
    troll = build_races(csv_dir, {8: ("DarkTroll", RACES[8][1])})["races"]["8"]
    night = build_races(csv_dir, {4: RACES[4]})["races"]["4"]
    rows = {c["ID"]: c for cs in tables.choices.values() for c in cs}
    dt = dark_troll_entry(troll, night, rows)
    dt["race"] = 8                                       # its names are the Trolls'
    dt["voices"] = {"vocal": [], "emotes": []}
    dt["names"] = [{"name": n["Name"], "sex": int(n["Sex"])} for n in tables.names if n["RaceID"] == "8"]
    data["darktroll"] = dt
    with open(out_path, "w") as f:
        json.dump(data, f, indent=1, sort_keys=True)
    return data


def main(argv):
    if len(argv) == 4 and argv[1] == "data":
        for k, e in races_data(argv[2], argv[3]).items():
            print("%s: %s, %d vocal, %d emotes, %d names" % (k, "+".join("%s %d skins %d faces" % (m["name"], len(m["skins"]), len(m["faces"])) for m in e["models"].values()),
                                                           len(e["voices"]["vocal"]), len(e["voices"]["emotes"]), len(e["names"])))
        return 0
    if len(argv) == 3 and argv[1] == "fetch":
        fetch(argv[2])
        return 0
    if len(argv) == 4 and argv[1] in ("races", "allied"):
        looks = build_races(argv[2], ALLIED if argv[1] == "allied" else None)
        with open(argv[3], "w") as f:
            json.dump(looks, f, indent=1, sort_keys=True)
        for entry in looks["races"].values():
            for sex, m in sorted(entry["models"].items()):
                print("%s: %d skins, %d faces x %d eyes, %d hair styles x %d colours, %d features (%s)" % (
                    m["name"], len(m["skins"]), len(m["faces"]), len(m["eyes"]), len(m["hair"]), len(m["hair_colors"]),
                    len(m["features"]), ", ".join(m["feature_options"])))
        return 0
    if len(argv) >= 5 and argv[1] == "assemble":
        return assemble(argv[2], argv[3], argv[4:])
    if len(argv) == 4 and argv[1] == "verify":
        missing = verify(load_looks(argv[2]), argv[3])
        print("%d missing" % len(missing), *missing[:20], sep="\n")
        return 1 if missing else 0
    if len(argv) == 6 and argv[1] == "package":
        package(argv[2], argv[3], argv[4], argv[5])
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
