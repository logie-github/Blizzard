#!/usr/bin/env python3
"""What the two races are made of, read from Blizzard's own tables of today (wago.tools' CSVs of
ChrRaces, ChrModel, ChrCustomization*, TextureFileData, SoundKitEntry, VocalUISounds,
EmotesTextSound, NameGen) and written as data/retail/races.json: for each race and sex, the
model's files, which geosets stay and under which ids (the policy tools/m2.py converts by), the
skins, faces, eyes, hair styles and colours and facial features with the files each takes, the
voices and the name generator's names. The other tools work from that file alone, so the tables
needn't be fetched again; run this when a table changed.

    python3 tools/races.py CSV_DIR        the CSVs, named <Table>.csv (wago.tools/db2/<Table>/csv)

How today's options become 3.3.5's five sliders (skin, face, hair style, hair colour, feature):
  * Skin colour: every skin colour a player may pick; for nightborne, each with every body
    tattoo (seven, "None" first).
  * Face: every face, each with every eye colour (face 1 eye 1, face 1 eye 2...). Void elves' eye
    colours are the nine a player picks without a demon hunter's blindfold (3.3.5 has room for
    255 faces: 28 faces x 9). A face today has textures for the skins of its kind (the void
    faces for the void skins, the high elf faces for the high elf skins); the other skins take
    the nearest face of their own kind, so every face number draws on every skin.
  * Hair style: every style. The void elves' tentacles (today's switch beside the hair style)
    are on the feature slider, a variant a shape.
  * Hair colour: every colour a player may pick.
  * Feature: void elf men their facial hair, void elf women their earrings; nightborne men
    every chin decoration x mustache x jaw jewellery, nightborne women every jaw jewellery x
    earrings x necklace (3.3.5's feature table holds geosets of groups 1, 3 and 2, so the
    earrings (group 35 today) go to group 3 and the necklaces (36) to group 2).
  Left at their first choice (3.3.5 has no slider for them): ears, eyebrows, eye style, eyesight,
  face tattoos, face jewellery, headdresses, hair decorations, luminous hands; horns, blindfolds
  and demon hunter tattoos aren't theirs.
"""
import collections
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODULE = os.path.dirname(HERE)
OUT = os.path.join(MODULE, "data", "retail", "races.json")

RACES = {
    "voidelf": {"race": 29, "name": "VoidElf", "models": {0: 57, 1: 58}, "parent_models": {0: 1100087, 1: 1100258},
                "eye_colours": 9},
    "nightborne": {"race": 27, "name": "Nightborne", "models": {0: 53, 1: 54}, "parent_models": {0: 974343, 1: 921844},
                   "eye_colours": 0},
    "lightforged": {"race": 30, "name": "LightforgedDraenei", "models": {0: 59, 1: 60}, "parent_models": {0: 1005887, 1: 1022598},
                    "eye_colours": 0},
    "zandalari": {"race": 31, "name": "ZandalariTroll", "models": {0: 61, 1: 62}, "parent_models": {0: 0, 1: 0},
                  "eye_colours": 0},
}
# The feature slider: which of today's options go on it (the first changes slowest), and which of
# today's geoset groups stand in for 3.3.5's feature groups 1, 3 and 2 (16 is 3.3.5's own too).
FEATURES = {
    ("voidelf", 0): (["Facial Hair"], {}),
    ("voidelf", 1): (["Earrings"], {35: 3}),
    ("nightborne", 0): (["Chin Decoration", "Mustache", "Jaw Jewelry"], {35: 3, 36: 2}),
    ("nightborne", 1): (["Jaw Jewelry", "Earrings", "Necklace"], {35: 3, 36: 2}),
    ("lightforged", 0): (["Facial Hair", "Tendrils"], {}),
    ("lightforged", 1): (["Horns", "Tendrils"], {24: 3}),
    ("zandalari", 0): (["Tusks", "Piercings"], {40: 3, 35: 1}),
    ("zandalari", 1): (["Tusks", "Earrings", "Piercings", "Necklace"], {40: 3, 35: 1, 36: 2}),
}
# Choices always shown (folded into geoset 0, which the game always draws), where 3.3.5 has no slider
# left for them: the Lightforged's forehead rune, the light on their brow (its first choice is none,
# which took the rune out altogether).
ALWAYS = {"lightforged": {"Rune": "Righteous"}}
# Group 0 geosets that are the head itself, not a hair style, kept always (into geoset 0): the
# Lightforged men's geoset 1 is the skin of the forehead and crown and the bony crest over it (their
# "horns", drawn with the hair's texture as the Draenei men's are). Taken for an unchosen hair style,
# it was left out, and their foreheads were missing (the user's screenshots).
HEAD = {("lightforged", 0): [1]}
EARS_OPTIONS = ("Ears", "Ear Gauge")
AVAILABLE = "3"                 # ChrCustomizationReq.ReqType of a choice any player picks
TARGET_BODY, TARGET_FACE, TARGET_HAIR, TARGET_TENTACLES, TARGET_PELVIS, TARGET_TORSO, TARGET_TATTOO, TARGET_EYES, TARGET_EYE_FACE, TARGET_JEWELRY = \
    "1", "5", "10", "11", "13", "14", "16", "25", "36", "38"
BODY_TATTOOS = ("Body Tattoo", "Tattoo")    # a skin overlay with colours of its own (nightborne; lightforged and zandalari)
# Today's geoset groups the 3.3.5 game picks from its tables, so every variant stays:
TABLE_GROUPS = {0, 1, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13, 15, 18}
GLOW_GROUP, EARS_GROUP = 17, 7


def rows(csv_dir, table):
    with open(os.path.join(csv_dir, table + ".csv"), newline="") as f:
        return list(csv.DictReader(f))


class Tables:
    def __init__(self, csv_dir):
        r = lambda t: rows(csv_dir, t)
        self.options = {o["ID"]: o for o in r("ChrCustomizationOption")}
        self.choices = collections.defaultdict(list)
        for c in r("ChrCustomizationChoice"):
            self.choices[c["ChrCustomizationOptionID"]].append(c)
        for cs in self.choices.values():
            cs.sort(key=lambda c: int(c["OrderIndex"]))
        self.choice_by_id = {c["ID"]: c for cs in self.choices.values() for c in cs}
        self.elements = collections.defaultdict(list)
        for e in r("ChrCustomizationElement"):
            self.elements[e["ChrCustomizationChoiceID"]].append(e)
        self.materials = {m["ID"]: m for m in r("ChrCustomizationMaterial")}
        self.geosets = {g["ID"]: g for g in r("ChrCustomizationGeoset")}
        self.skinned = {g["ID"]: g for g in r("ChrCustomizationSkinnedModel")}
        self.reqs = {q["ID"]: q for q in r("ChrCustomizationReq")}
        self.textures = collections.defaultdict(list)
        for t in r("TextureFileData"):
            self.textures[t["MaterialResourcesID"]].append(int(t["FileDataID"]))
        self.model_data = {m["ID"]: m for m in r("CreatureModelData")}
        self.chr_models = {m["ID"]: m for m in r("ChrModel")}
        self.displays = {}
        display_path = os.path.join(csv_dir, "CreatureDisplayInfo.csv")
        if os.path.exists(display_path):
            for d in rows(csv_dir, "CreatureDisplayInfo"):
                self.displays[d["ID"]] = d
        self.vocal = [v for v in r("VocalUISounds")]
        self.emotes = [e for e in r("EmotesTextSound")]
        self.kits = collections.defaultdict(list)
        for k in r("SoundKitEntry"):
            self.kits[k["SoundKitID"]].append(int(k["FileDataID"]))
        self.names = [n for n in r("NameGen")]

    def available(self, choice):
        req = self.reqs.get(choice["ChrCustomizationReqID"])
        return req is None or req["ReqType"] == AVAILABLE

    def option(self, model_id, name):
        for o in self.options.values():
            if o["ChrModelID"] == str(model_id) and o["Name_lang"] == name:
                return o
        return None

    def option_choices(self, model_id, name, only_available=True):
        o = self.option(model_id, name)
        if not o:
            return []
        return [c for c in self.choices[o["ID"]] if not only_available or self.available(c)]

    def material_files(self, element):
        m = self.materials[element["ChrCustomizationMaterialID"]]
        return m["ChrModelTextureTargetID"], self.textures.get(m["MaterialResourcesID"], [])

    def geoset_of(self, element):
        g = self.geosets[element["ChrCustomizationGeosetID"]]
        return int(g["GeosetType"]) * 100 + int(g["GeosetID"])

    def choice_geosets(self, choice):
        """The choice's geosets (a geoset ending in 00 shows nothing: left out)."""
        return [g for g in (self.geoset_of(e) for e in self.elements[choice["ID"]] if e["ChrCustomizationGeosetID"] != "0") if g % 100]

    def choice_groups(self, choice):
        """The geoset groups the choice touches, its models of its own (horns, blindfolds) included."""
        groups = {self.geoset_of(e) // 100 for e in self.elements[choice["ID"]] if e["ChrCustomizationGeosetID"] != "0"}
        for e in self.elements[choice["ID"]]:
            if e["ChrCustomizationSkinnedModelID"] != "0":
                groups.add(int(self.skinned[e["ChrCustomizationSkinnedModelID"]]["GeosetType"]))
        return groups

    def choice_materials(self, choice, target=None):
        out = []
        for e in self.elements[choice["ID"]]:
            if e["ChrCustomizationMaterialID"] == "0":
                continue
            t, files = self.material_files(e)
            if target is None or t == target:
                out.append((e["RelatedChrCustomizationChoiceID"], files))
        return out


def model_file(tables, chr_model_id):
    chr_model = tables.chr_models[str(chr_model_id)]
    display = tables.displays.get(chr_model["DisplayID"])
    if display:
        model = tables.model_data[display["ModelID"]]
        return int(model["FileDataID"])
    return 0


def build_model(tables, race_key, race, sex, model_id, model_file_id):
    name = race["name"] + ("Female" if sex else "Male")
    folder = "Character\\%s\\%s" % (race["name"], "Female" if sex else "Male")
    out = {"name": name, "folder": folder, "model": model_file_id, "parent_model": race["parent_models"][sex], "sex": sex}

    # Hair styles: variation -> geoset; void tentacles as styles of their own.
    styles = tables.option_choices(model_id, "Hair Style", only_available=False)
    hair = []
    geoset_policy = collections.defaultdict(list)         # old geoset -> new ids
    for i, c in enumerate(styles):
        gs = [g for g in tables.choice_geosets(c) if g < 100]
        geoset = gs[0] if gs else 0
        hair.append({"variation": i, "geoset": geoset, "name": c["Name_lang"], "choice": c["ID"]})
        if geoset:
            geoset_policy[geoset].append(geoset)
    # Void tentacles: today a switch beside the hair style, each style with its own shape (a
    # group 2 geoset). They go on the feature slider (below), one variant a shape, named for the
    # style the shape was made for: a copy of every style with its tentacles on would double the
    # hair's triangles, and 3.3.5 can address 65535 indices in a model (m2.py).
    tentacles = tables.option_choices(model_id, "Tentacles", only_available=False)
    hardcoded = {}
    hardcoded_files = {}
    tentacle_variants = []
    if len(tentacles) > 1:
        on = tentacles[1]
        style_of_choice = {h["choice"]: h for h in hair}
        for e in tables.elements[on["ID"]]:
            if e["ChrCustomizationGeosetID"] != "0" and e["RelatedChrCustomizationChoiceID"] in style_of_choice:
                tentacle = tables.geoset_of(e)
                style = style_of_choice[e["RelatedChrCustomizationChoiceID"]]
                if tentacle // 100 == 2 and tentacle % 100:
                    tentacle_variants.append({"name": "Tentacles (%s)" % style["name"], "geosets": [(2, tentacle % 100)]})
                    geoset_policy[tentacle].append(tentacle)
        for _, files in tables.choice_materials(on, TARGET_TENTACLES):
            if files:
                path = "%s\\%sHairVoid.blp" % (folder, name)
                hardcoded["7"] = path
                hardcoded_files[path] = files[0]
    # Jewellery (texture type 20): the first jewellery colour's texture.
    jewel = tables.option_choices(model_id, "Jewelry Color", only_available=False)
    if jewel:
        for _, files in tables.choice_materials(jewel[0], TARGET_JEWELRY):
            if files:
                path = "%s\\%sJewelry.blp" % (folder, name)
                hardcoded["20"] = path
                hardcoded_files[path] = files[0]

    # Hair colours.
    hair_colors = []
    for i, c in enumerate(tables.option_choices(model_id, "Hair Color")):
        files = [f for _, fs in tables.choice_materials(c, TARGET_HAIR) for f in fs]
        if files:
            hair_colors.append({"index": len(hair_colors), "file": files[0]})

    # Skins: body, underwear; nightborne with each body tattoo.
    # A skin without underwear of its own (the Lightforged's) takes the first jewelry colour's
    # pelvis and torso pieces, which today's models wear in its place.
    jewelry_first = tables.option_choices(model_id, "Jewelry Color", only_available=False)
    jewelry_pelvis = jewelry_torso = 0
    if jewelry_first:
        fs = [f for _, files in tables.choice_materials(jewelry_first[0], TARGET_PELVIS) for f in files]
        jewelry_pelvis = fs[0] if fs else 0
        fs = [f for _, files in tables.choice_materials(jewelry_first[0], TARGET_TORSO) for f in files]
        jewelry_torso = fs[0] if fs else 0
    skin_choices = tables.option_choices(model_id, "Skin Color")
    tattoos = []
    for oname in BODY_TATTOOS:
        tattoos = tables.option_choices(model_id, oname, only_available=False)
        if tattoos:
            break
    tattoo_files = [[]]
    tattoo_names = ["None"]
    for t in tattoos[1:]:
        files = [f for _, fs in tables.choice_materials(t, TARGET_TATTOO) for f in fs]
        if files:
            tattoo_files.append(files)
            tattoo_names.append(t["Name_lang"])
    skins = []
    base_skins = []
    for i, c in enumerate(skin_choices):
        body = [f for _, fs in tables.choice_materials(c, TARGET_BODY) for f in fs]
        pelvis = [f for _, fs in tables.choice_materials(c, TARGET_PELVIS) for f in fs]
        torso = [f for _, fs in tables.choice_materials(c, TARGET_TORSO) for f in fs]
        if not body:
            continue
        base_skins.append({"choice": c["ID"], "order": int(c["OrderIndex"]), "body": body[0], "pelvis": pelvis[0] if pelvis else jewelry_pelvis, "torso": torso[0] if torso else jewelry_torso})
    for t, (files, tname) in enumerate(zip(tattoo_files, tattoo_names)):
        for b in base_skins:
            skins.append(dict(b, index=len(skins), base=base_skins.index(b), tattoo=files, tattoo_name=tname))

    # Faces: each with its texture a skin (of the skins it has one for).
    face_choices = tables.option_choices(model_id, "Face")
    skin_index_of_choice = {b["choice"]: i for i, b in enumerate(base_skins)}
    faces = []
    for c in face_choices:
        textures = {}
        for related, files in tables.choice_materials(c, TARGET_FACE):
            if related in skin_index_of_choice and files:
                textures[skin_index_of_choice[related]] = files[0]
        faces.append({"choice": c["ID"], "name": c["Name_lang"], "textures": textures})
    # the skins a face is for: its kind; a face with none is for every skin
    kinds = {}
    for f in faces:
        kinds[f["choice"]] = frozenset(f["textures"]) or frozenset(range(len(base_skins)))
    for f in faces:
        own = kinds[f["choice"]]
        f["skins"] = sorted(own)
    # every face on every base skin: a skin outside a face's kind takes that kind's nearest face
    # of the same rank; a skin of the kind without the texture takes the nearest skin's
    for s in range(len(base_skins)):
        for i, f in enumerate(faces):
            if s in f["textures"]:
                continue
            kind_faces = [g for g in faces if s in kinds[g["choice"]]]
            if s in kinds[f["choice"]] or not kind_faces:
                pool = [g for g in faces if g is f]
            else:
                # the same rank within its kind
                rank = [g for g in faces if kinds[g["choice"]] == kinds[f["choice"]]].index(f)
                pool = [kind_faces[rank % len(kind_faces)]]
            source = pool[0]
            nearest = min(source["textures"], key=lambda k: abs(k - s), default=None)
            f["textures"][s] = source["textures"][nearest] if nearest is not None else 0
    for f in faces:
        f["textures"] = {str(k): v for k, v in sorted(f["textures"].items())}

    # Eye colours: the player's, without the demon hunter's (related to blindfolds), the first
    # [eye_colours] when 3.3.5's 255 faces can't hold them all.
    eyes = []
    blindfold_related = set()
    for c in tables.option_choices(model_id, "Blindfold", only_available=False):
        for e in tables.elements[c["ID"]]:
            if e["RelatedChrCustomizationChoiceID"] != "0":
                blindfold_related.add(e["RelatedChrCustomizationChoiceID"])
    eyesight = tables.option_choices(model_id, "Eyesight", only_available=False)
    overlays = {}
    if eyesight:
        for related, files in tables.choice_materials(eyesight[0], TARGET_EYE_FACE):
            if files:
                overlays[related] = files[0]
    glow_geosets = {}
    for c in tables.option_choices(model_id, "Eye Color"):
        if c["ID"] in blindfold_related or c["Flags"] != "0":
            continue
        files = [f for _, fs in tables.choice_materials(c, TARGET_EYES) for f in fs]
        if not files:
            continue
        eye = {"index": len(eyes), "file": files[0], "swatch": int(c["SwatchColor_0"]), "choice": c["ID"]}
        if c["ID"] in overlays:
            eye["overlay"] = overlays[c["ID"]]
        glows = [g for g in tables.choice_geosets(c) if g // 100 == GLOW_GROUP]
        if glows:
            glow_geosets[c["ID"]] = glows[0]
        eyes.append(eye)
    limit = race["eye_colours"] or len(eyes)
    if len(faces) * len(eyes) > 255:
        limit = min(limit, 255 // max(1, len(faces)))
    eyes = eyes[:limit]

    # The feature slider: which options, in what order (the first option changes slowest), and
    # today's group -> 3.3.5's feature group for groups 3.3.5 hasn't (FEATURES).
    feature_options, regroup = FEATURES[(race_key, sex)]
    per_option = []
    for oname in feature_options:
        cs = tables.option_choices(model_id, oname, only_available=False)
        variants = []
        for c in cs:
            gs = tables.choice_geosets(c)
            kept = []
            sources = set()
            for g in gs:
                group, variant = g // 100, g % 100
                sources.add(group)
                if group in regroup:
                    group = regroup[group]
                if group in (1, 2, 3, 16) and variant:
                    kept.append((group, variant))
                    geoset_policy[g].append(group * 100 + variant)
            variants.append({"name": c["Name_lang"], "geosets": kept, "sources": sorted(sources)})
        per_option.append(variants)
    if tentacle_variants:
        per_option.append([{"name": "", "geosets": []}] + tentacle_variants)
    features = []

    def combos(level, chosen):
        if level == len(per_option):
            geo = {1: 0, 2: 0, 3: 0, 16: 0}
            names = []
            for v in chosen:
                for group, variant in v["geosets"]:
                    geo[group] = variant
                names.append(v["name"])
            features.append({"variation": len(features), "geosets": [geo[1], geo[3], geo[2], geo[16], 2], "name": ", ".join(n for n in names if n)})
            return
        for v in per_option[level]:
            combos(level + 1, chosen + [v])
    combos(0, [])

    # The rest of the geosets: the tables' groups whole, the others at their first choice (m2.py
    # completes the policy from the skin's geosets); an option whose first choice shows nothing
    # (earrings "None"...) takes its group out, unless the feature slider uses it.
    drop_groups = set()
    feature_groups = set()
    for variants in per_option:
        for v in variants:
            feature_groups.update(group for group, _ in v["geosets"])
            feature_groups.update(v.get("sources", ()))
    for o in tables.options.values():
        if o["ChrModelID"] != str(model_id) or o["Name_lang"] in feature_options:
            continue
        cs = tables.choices[o["ID"]]
        groups = set()
        for c in cs:
            groups |= tables.choice_groups(c)
        if cs and groups and not tables.choice_geosets(cs[0]):
            drop_groups.update(g for g in groups if g not in TABLE_GROUPS and g not in feature_groups)
    for oname in EARS_OPTIONS:
        ears = tables.option_choices(model_id, oname, only_available=False)
        if ears:
            for g in tables.choice_geosets(ears[0]):
                if g // 100 == EARS_GROUP:
                    geoset_policy[g].append(702)
            break
    glow = glow_geosets.get(eyes[0]["choice"]) if eyes else None
    geoset_policy[glow or GLOW_GROUP * 100 + 1].extend([1702, 1703])
    # The body parts today's models keep in groups 3.3.5 doesn't know (the head and mouth in 32,
    # the eyeballs in 33, the eyebrows in 34; the toes, torso and forearms in 20, 22 and 23, which
    # m2.complete_policy folds) become geoset 0, which the game always draws (the HD look's models
    # keep their whole body there).
    geoset_policy[3301].append(0)                          # the eyeballs (drawn from the face region)
    for oname, cname in ALWAYS.get(race_key, {}).items():
        for c in tables.option_choices(model_id, oname, only_available=False):
            if c["Name_lang"] == cname:
                for g in tables.choice_geosets(c):
                    geoset_policy[g].append(0)
    geoset_policy[3201].append(0)                          # the mouth, beside the head the Eyes choice picks
    for g in HEAD.get((race_key, sex), []):
        geoset_policy[g].append(0)
    geoset_policy[0].append(0)                             # the scalp
    for oname in ("Eyes", "Eyebrows"):
        for c in tables.option_choices(model_id, oname, only_available=False)[:1]:
            for g in tables.choice_geosets(c):
                geoset_policy[g].append(0)
    if not tables.option_choices(model_id, "Eyes", only_available=False):
        geoset_policy[3202].append(0)                      # the head (an Eyes choice picks one otherwise)
    out.update({"hardcoded": hardcoded, "hardcoded_files": hardcoded_files, "eye_geosets": [3301],
                "hair": hair, "hair_colors": hair_colors, "skins": skins, "base_skins": len(base_skins), "faces": faces, "eyes": eyes,
                "features": features, "feature_options": feature_options, "geoset_policy": {str(k): sorted(set(v)) for k, v in geoset_policy.items()},
                "drop_groups": sorted(drop_groups),
                "tattoos": tattoo_names})
    return out


def voices(tables, race_id):
    out = {"vocal": [], "emotes": []}
    for v in tables.vocal:
        if v["RaceID"] != str(race_id):
            continue
        kits = [v["NormalSoundID_0"], v["NormalSoundID_1"]]
        out["vocal"].append({"enum": int(v["VocalUIEnum"]), "kits": [{"id": int(k), "files": tables.kits.get(k, [])} for k in kits]})
    for e in tables.emotes:
        if e["RaceID"] != str(race_id):
            continue
        out["emotes"].append({"emote": int(e["EmotesTextID"]), "sex": int(e["SexID"]), "kit": {"id": int(e["SoundID"]), "files": tables.kits.get(e["SoundID"], [])}})
    return out


def main(csv_dir):
    tables = Tables(csv_dir)
    out = {}
    for key, race in RACES.items():
        entry = {"race": race["race"], "name": race["name"], "models": {}}
        for sex, model_id in race["models"].items():
            file_id = model_file(tables, model_id)
            if not file_id:
                raise SystemExit("no model file for ChrModel %d: CreatureDisplayInfo.csv (the rows of its displays) is needed" % model_id)
            entry["models"][str(sex)] = build_model(tables, key, race, sex, model_id, file_id)
        entry["voices"] = voices(tables, race["race"])
        entry["names"] = [{"name": n["Name"], "sex": int(n["Sex"])} for n in tables.names if n["RaceID"] == str(race["race"])]
        out[key] = entry
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    for key, entry in out.items():
        for sex, m in entry["models"].items():
            print("%s %s: %d skins (%d base), %d faces x %d eyes, %d hair styles, %d hair colours, %d features" % (
                key, m["name"], len(m["skins"]), m["base_skins"], len(m["faces"]), len(m["eyes"]), len(m["hair"]), len(m["hair_colors"]), len(m["features"])))
        print("%s: %d vocal, %d emotes, %d names" % (key, len(entry["voices"]["vocal"]), len(entry["voices"]["emotes"]), len(entry["names"])))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1])
